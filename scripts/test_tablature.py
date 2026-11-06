"""Check data preservation when combining synthetic guitar tracks."""

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import guitarpro


spec = importlib.util.spec_from_file_location("tablature_export", Path(__file__).resolve().parents[1] / "tools/PDF-to-GP5/export.py")
tablature = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tablature)


def synthetic_song():
    song = guitarpro.models.Song()
    voice = song.tracks[0].measures[0].voices[0]
    for index, fret in enumerate((0, 2, 4, 5)):
        beat = guitarpro.models.Beat(voice, start=960 + index * 960,
                                    status=guitarpro.models.BeatStatus.normal)
        beat.notes = [guitarpro.models.Note(beat, string=1, value=fret, type=guitarpro.models.NoteType.normal)]
        voice.beats.append(beat)
    return song


class TablatureTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "input.gp5"
        guitarpro.write(synthetic_song(), self.source, version=(5, 1, 0))
        self.plan = {"name": "guitar-study", "title": "Synthetic guitar study", "tempo": 80,
                     "meter": "4/4", "tuning": [64, 59, 55, 50, 45, 40], "capo": 0}

    def test_merge_preserves_frets_order_and_absolute_time(self):
        original = self.source.read_bytes()
        merged = tablature.merge_songs([self.source, self.source], self.plan)
        measures = merged.tracks[0].measures
        self.assertEqual([m.header.start for m in measures], [960, 4800])
        self.assertEqual([m.header.number for m in measures], [1, 2])
        for measure in measures:
            self.assertEqual([b.start - measure.header.start for b in measure.voices[0].beats], [0, 960, 1920, 2880])
            self.assertEqual([b.notes[0].value for b in measure.voices[0].beats], [0, 2, 4, 5])
        self.assertEqual(self.source.read_bytes(), original)

    def test_meter_mismatch_is_rejected(self):
        self.plan["meter"] = "3/4"
        with self.assertRaises(ValueError):
            tablature.merge_songs([self.source], self.plan)

    def test_existing_export_is_never_overwritten(self):
        existing = self.root / "guitar-study.musicxml"
        existing.write_text("User edits")
        with self.assertRaises(ValueError):
            tablature.export_score(synthetic_song(), self.plan, self.root)
        self.assertEqual(existing.read_text(), "User edits")

    def test_private_paths_reject_escape_and_escaping_symlinks(self):
        with patch.object(tablature, "ROOT", self.root):
            (self.root / "score").mkdir()
            (self.root / "score/escape").symlink_to(self.root, target_is_directory=True)
            for path in ("../outside", "score/../output", "score/escape/output"):
                with self.assertRaises(ValueError):
                    tablature.local_score_path(path)


if __name__ == "__main__":
    unittest.main()
