#!/usr/bin/env python3
"""Recognize explicitly cropped guitar systems from a local plan and export TAB drafts."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import traceback
import xml.etree.ElementTree as ET

import guitarpro
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def local_score_path(path):
    path = (ROOT / path).resolve()
    if not path.is_relative_to((ROOT / "score").resolve()) or path == ROOT / "score":
        raise ValueError("Plans, source images and outputs must stay inside the local score collection")
    return path


def load_plan(path):
    plan = json.loads(path.read_text(encoding="utf-8"))
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", plan["name"]):
        raise ValueError("Plan name must use lowercase ASCII letters, digits and hyphens")
    if not isinstance(plan["title"], str) or not plan["title"].strip():
        raise ValueError("A display title is required")
    if not isinstance(plan["tempo"], int) or not 0 < plan["tempo"] <= 400:
        raise ValueError("Tempo must be a positive integer no greater than 400")
    numerator, denominator = map(int, plan["meter"].split("/"))
    if numerator <= 0 or denominator not in (1, 2, 4, 8, 16, 32, 64):
        raise ValueError("Invalid meter")
    if len(plan["tuning"]) != 6 or any(not isinstance(n, int) or not 0 <= n <= 127 for n in plan["tuning"]):
        raise ValueError("Tuning must specify six MIDI pitches, strings 1 through 6")
    if not isinstance(plan["capo"], int) or not 0 <= plan["capo"] <= 24:
        raise ValueError("Invalid capo fret")
    if not plan["systems"]:
        raise ValueError("At least one system is required")
    for system in plan["systems"]:
        source = local_score_path(system["source"])
        box = system["box"]
        if len(box) != 4 or any(not isinstance(n, int) for n in box):
            raise ValueError("Crop boxes need four integer pixel coordinates")
        with Image.open(source) as image:
            left, top, right, bottom = box
            if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
                raise ValueError(f"Crop box exceeds image: {source}")
        if not isinstance(system["measures"], int) or system["measures"] <= 0:
            raise ValueError("Each system requires a positive expected measure count")
    return plan


def recognize_systems(plan, output):
    rows = []
    for number, system in enumerate(plan["systems"], 1):
        source = local_score_path(system["source"])
        name = f"system-{number:03}"
        crop, result = output / f"{name}.png", output / name
        with Image.open(source) as image:
            image.crop(system["box"]).save(crop)
        with (output / f"{name}.log").open("w", encoding="utf-8") as log:
            subprocess.run([
                sys.executable, str(ROOT / "tools/PDF-to-GP5/evaluate.py"), str(crop), str(result),
                "--tempo", str(plan["tempo"]), "--meter", plan["meter"],
            ], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        song = guitarpro.parse(result / "recognized.gp5")
        if len(song.tracks) != 1 or len(song.tracks[0].strings) != 6:
            raise ValueError(f"Expected a single six-string guitar track in {name}")
        count = len(song.tracks[0].measures)
        if count != system["measures"]:
            raise ValueError(f"{name}: expected {system['measures']} measures, recognized {count}")
        rows.append({
            **system, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "result": name, "recognized_measures": count,
        })
        save_json(output / "coverage.json", {"status": "recognizing", "systems": rows})
        print(f"{name}: {count} measures", flush=True)
    return rows


def merge_songs(inputs, plan):
    """Merge printed order; normalize ties without importing a preceding crop's tuning."""
    merged = guitarpro.parse(inputs[0])
    track = merged.tracks[0]
    merged.title, merged.subtitle = plan["name"], "Uncorrected tablature"
    merged.artist = merged.music = merged.words = merged.copyright = ""
    merged.lyrics = guitarpro.models.Lyrics()
    merged.tempo = plan["tempo"]
    merged.measureHeaders, track.measures = [], []
    track.name, track.offset = "Guitar TAB", 0
    track.strings = [guitarpro.models.GuitarString(i, midi) for i, midi in enumerate(plan["tuning"], 1)]
    start = guitarpro.models.Duration.quarterTime
    previous_frets = [{}, {}]
    for source in inputs:
        song = guitarpro.parse(source)
        if len(song.tracks) != 1 or len(song.tracks[0].strings) != 6:
            raise ValueError(f"Expected a single six-string guitar track: {source}")
        for measure in song.tracks[0].measures:
            header = measure.header
            meter = f"{header.timeSignature.numerator}/{header.timeSignature.denominator.value}"
            if meter != plan["meter"]:
                raise ValueError(f"Unexpected meter {meter}: {source}")
            delta = start - header.start
            header.number, header.start = len(track.measures) + 1, start
            header.isRepeatOpen, header.repeatClose, header.repeatAlternative = False, -1, 0
            measure.track = track
            for voice_index, voice in enumerate(measure.voices):
                for beat in voice.beats:
                    beat.start += delta
                    beat.effect = guitarpro.models.BeatEffect()
                    for note in beat.notes:
                        note.effect = guitarpro.models.NoteEffect()
                        if note.type == guitarpro.models.NoteType.tie:
                            if note.string not in previous_frets[voice_index]:
                                raise ValueError(f"Unresolved tie in merged measure {header.number}")
                            note.value = previous_frets[voice_index][note.string]
                        if note.type != guitarpro.models.NoteType.dead:
                            previous_frets[voice_index][note.string] = note.value
                        else:
                            previous_frets[voice_index].pop(note.string, None)
            merged.measureHeaders.append(header)
            track.measures.append(measure)
            start += header.length
    return merged


def musescore(output, *args):
    command = ["flatpak", "run", "--user", f"--filesystem={ROOT}",
               "--env=QT_QPA_PLATFORM=offscreen", "--env=MU_QT_QPA_PLATFORM=offscreen",
               "org.musescore.MuseScore", *map(str, args)]
    with (output / "musescore.log").open("a", encoding="utf-8") as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)


def export_score(song, plan, output):
    files = [output / f"{plan['name']}.{ext}" for ext in ("gp5", "musicxml", "mscz", "pdf")]
    if any(p.exists() for p in files):
        raise ValueError("Output already exists; preserve the previous draft")
    guitarpro.write(song, files[0], version=(5, 1, 0))
    with tempfile.TemporaryDirectory(prefix="musescore-", dir=output) as temporary:
        temporary = Path(temporary)
        mscx = temporary / "score.mscx"
        musescore(output, "-o", mscx, files[0])
        tree = ET.parse(mscx)
        score = tree.getroot().find("Score")
        staff = score.find("Part/Staff")
        staff_type = staff.find("StaffType")
        staff_type.clear()
        staff_type.set("group", "tablature")
        for name, value in {
            "name": "tab6StrSimple", "lines": "6", "lineDistance": "1.5", "genClef": "1",
            "showBarlines": "1", "slashStyle": "0", "genTimesig": "1", "genKeysig": "0",
            "showRests": "1", "stemsDown": "1", "stemsThrough": "0", "upsideDown": "0", "useNumbers": "1",
        }.items():
            ET.SubElement(staff_type, name).text = value
        staff.find("defaultClef").text = "TAB"
        first_voice = score.find("Staff/Measure/voice")
        clef = first_voice.find("Clef")
        if clef is not None:
            first_voice.remove(clef)
        text = ET.Element("StaffText")
        ET.SubElement(text, "text").text = f"Capo {plan['capo']}; playback without capo transposition"
        first_voice.insert(0, text)
        for text in score.findall("Staff/VBox/Text"):
            if text.findtext("style") == "title":
                text.find("text").text = plan["title"]
        for meta in score.findall("metaTag"):
            if meta.get("name") == "workTitle":
                meta.text = plan["title"]
        tree.write(mscx, encoding="utf-8", xml_declaration=True)
        jobs = temporary / "jobs.json"
        save_json(jobs, [{"in": str(mscx), "out": [str(p) for p in files[1:]]}])
        musescore(output, "-j", jobs)
    xml = ET.parse(files[1]).getroot()
    measures = xml.findall(".//measure")
    if xml.findtext(".//clef/sign") != "TAB" or len(measures) != len(song.tracks[0].measures):
        raise ValueError("Export changed staff type or measure count")
    for original, exported in zip(song.tracks[0].measures, measures, strict=True):
        expected = Counter((n.string, n.value) for v in original.voices for b in v.beats for n in b.notes)
        actual = Counter((int(n.findtext("notations/technical/string")), int(n.findtext("notations/technical/fret")))
                         for n in exported.findall("note[pitch]"))
        if actual != expected:
            raise ValueError(f"String/fret changed in measure {original.header.number}")
    if any(not p.is_file() or not p.stat().st_size for p in files):
        raise ValueError("Incomplete export")
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="Private JSON plan inside score/")
    parser.add_argument("output", type=Path, help="New private output directory inside score/")
    args = parser.parse_args()
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        parser.error("Use the project .venv/bin/python")
    plan_path, output = local_score_path(args.plan), local_score_path(args.output)
    plan = load_plan(plan_path)
    if output.exists():
        parser.error("Output directory already exists; preserve previous results")
    output.mkdir(parents=True)
    save_json(output / "plan.json", plan)
    try:
        rows = recognize_systems(plan, output)
        song = merge_songs([output / row["result"] / "recognized.gp5" for row in rows], plan)
        hashes = export_score(song, plan, output)
        save_json(output / "coverage.json", {
            "status": "uncorrected", "systems": rows, "total_measures": len(song.measureHeaders),
            "outputs": hashes, "playback_capo": 0, "source_capo": plan["capo"],
            "techniques": "beat/note effects and repeats omitted; dead-note types retained",
        })
    except Exception:
        save_json(output / "failure.json", {"status": "failed", "traceback": traceback.format_exc()})
        raise
    print(f"Exported {len(song.measureHeaders)} measures to {output}")


if __name__ == "__main__":
    main()
