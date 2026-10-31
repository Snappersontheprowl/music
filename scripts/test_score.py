"""Checks for data preservation and edition boundaries; no external apps needed."""

import argparse
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
import score


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.root_patch = patch.object(score, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.args = argparse.Namespace(work="bach-prelude-bwv846", edition="piano-solo")
        score.initialize(self.args)
        self.paths = score.locations(self.args)

    def test_reinitialization_preserves_existing_files(self):
        readme = self.paths["source"] / "README.md"
        readme.write_text("用户来源记录")
        with self.assertRaises(ValueError):
            score.initialize(self.args)
        self.assertEqual(readme.read_text(), "用户来源记录")

    def test_add_edition_preserves_work_metadata(self):
        readme = self.root / "score" / self.args.work / "README.md"
        readme.write_text("用户作品信息")
        self.args.edition = "publisher-score"
        score.initialize(self.args)
        self.assertEqual(readme.read_text(), "用户作品信息")

    def test_reject_traversal_and_symlink_escape(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            score.slug("../outside")
        (self.root / "score" / "escaped").symlink_to(self.root, target_is_directory=True)
        self.args.work = "escaped"
        with self.assertRaises(ValueError):
            score.locations(self.args)

    def test_reject_missing_or_duplicate_pages_before_running(self):
        for names in (("page-002.png",), ("page-001.png", "page-001.jpg")):
            for name in names:
                Image.new("RGB", (16, 16)).save(self.paths["source"] / name)
            with patch.object(score, "run") as run:
                with self.assertRaises(ValueError):
                    score.recognize(self.args)
                run.assert_not_called()
            for name in names:
                (self.paths["source"] / name).unlink()
        self.assertEqual(list(self.paths["audiveris"].iterdir()), [])

    def test_images_keep_order_and_original_bytes(self):
        # Create in reverse directory order; TIFF must still follow page numbers.
        for name, color in (("page-002.png", "blue"), ("page-001.png", "red")):
            Image.new("RGB", (16, 16), color).save(self.paths["source"] / name)
        before = {p.name: p.read_bytes() for p in self.paths["source"].iterdir()}

        def fake_recognition(*_args, **_kwargs):
            (self.paths["audiveris"] / "input.omr").write_bytes(b"fixture")
            (self.paths["audiveris"] / "input.mxl").write_bytes(b"fixture")

        with patch.object(score, "run", side_effect=fake_recognition), \
                patch.object(score, "MAX_IMAGE_PIXELS", 100):
            score.recognize(self.args)
        with Image.open(self.paths["audiveris"] / "input.tiff") as image:
            self.assertEqual(image.n_frames, 2)
            self.assertLessEqual(image.width * image.height, 100)
            self.assertEqual(image.getpixel((0, 0)), (255, 0, 0))
            image.seek(1)
            self.assertEqual(image.getpixel((0, 0)), (0, 0, 255))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.paths["source"].iterdir()})

    def test_import_cannot_read_another_edition(self):
        source = self.root / "outside.mxl"
        source.write_bytes(b"fixture")
        self.args.input = str(source)
        with patch.object(score, "run") as run:
            with self.assertRaises(ValueError):
                score.import_score(self.args)
            run.assert_not_called()

    def test_failed_second_export_publishes_nothing(self):
        (self.paths["notation"] / f"{self.args.edition}.mscz").write_bytes(b"fixture")

        def fake_convert(_source, destination):
            if destination.suffix == ".musicxml":
                raise subprocess.CalledProcessError(1, "MuseScore")
            destination.write_bytes(b"%PDF-fixture")

        with patch.object(score, "convert", side_effect=fake_convert):
            with self.assertRaises(subprocess.CalledProcessError):
                score.publish(self.args)
        self.assertEqual(list(self.paths["export"].iterdir()), [])

    def test_publish_refuses_existing_deliverable(self):
        (self.paths["notation"] / f"{self.args.edition}.mscz").write_bytes(b"fixture")
        destination = self.paths["export"] / f"{self.args.edition}.pdf"
        destination.write_bytes(b"user-pdf")
        with patch.object(score, "run") as run:
            with self.assertRaises(ValueError):
                score.publish(self.args)
            run.assert_not_called()
        self.assertEqual(destination.read_bytes(), b"user-pdf")


if __name__ == "__main__":
    unittest.main()
