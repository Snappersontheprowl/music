#!/usr/bin/env python3
"""Run the unmodified converter and preserve inspectable evaluation artifacts."""

import argparse
from dataclasses import asdict
import hashlib
from importlib import metadata
import io
import json
from pathlib import Path
import sys
import time
import traceback

import guitarpro
import pdf_to_gp5
from pdf_to_gp5 import converter, i18n


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--tempo", type=int)
    parser.add_argument("--meter", help="Explicit metadata for a separate assisted run, e.g. 3/4")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output directory already exists; preserve the previous run")
    numerator, denominator = map(int, args.meter.split("/")) if args.meter else (None, None)
    options = converter.ConversionOptions(tempo=args.tempo, numerator=numerator, denominator=denominator)
    data = args.input.read_bytes()
    args.output.mkdir(parents=True)
    manifest = {
        "tool": "PDF-to-GP5", "version": pdf_to_gp5.__version__,
        "upstream_commit": "4754a207ff4a08be8dfb4b5097c4a4c3775004d4",
        "converter_sha256": hashlib.sha256(Path(converter.__file__).read_bytes()).hexdigest(),
        "source": str(args.input.resolve()), "source_sha256": hashlib.sha256(data).hexdigest(),
        "python": sys.version, "options": asdict(options),
        "packages": {dist.metadata["Name"]: dist.version for dist in metadata.distributions()},
    }
    save_json(args.output / "manifest.json", manifest)
    i18n.use("en")
    started = time.monotonic()
    try:
        result = converter.convert(data, options)
    except Exception as error:
        save_json(args.output / "failure.json", {
            "status": "failed", "exception": f"{type(error).__name__}: {error}",
            "conversion_seconds": round(time.monotonic() - started, 3),
            "gp5_generated": False, "traceback": traceback.format_exc(),
        })
        raise
    manifest["conversion_seconds"] = round(time.monotonic() - started, 3)
    save_json(args.output / "manifest.json", manifest)
    (args.output / "recognized.gp5").write_bytes(result.gp5)
    save_json(args.output / "conversion.json", result.report)
    (args.output / "preview.txt").write_text(
        "\n\n".join(track["preview"] for track in result.report["tracks"]) + "\n", encoding="utf-8")
    song = guitarpro.parse(io.BytesIO(result.gp5))
    tracks = []
    for track in song.tracks:
        measures = []
        for measure in track.measures:
            measures.append({
                "number": measure.header.number,
                "meter": f"{measure.header.timeSignature.numerator}/{measure.header.timeSignature.denominator.value}",
                "voices": [[{
                    "start_tick": beat.start, "duration_ticks": beat.duration.time,
                    "duration_value": beat.duration.value, "dotted": beat.duration.isDotted,
                    "status": beat.status.name,
                    "notes": [{"string": note.string, "fret": note.value, "type": note.type.name}
                              for note in beat.notes],
                } for beat in voice.beats] for voice in measure.voices],
            })
        tracks.append({"name": track.name, "capo": track.offset,
                       "strings": [{"number": string.number, "midi": string.value} for string in track.strings],
                       "measures": measures})
    save_json(args.output / "events.json", {"title": song.title, "tempo": song.tempo, "tracks": tracks})
    print(json.dumps({key: result.report[key] for key in ("tempo", "time_signature", "measures", "notes", "auto")}, indent=2))
    print(f"Artifacts: {args.output}")


if __name__ == "__main__":
    main()
