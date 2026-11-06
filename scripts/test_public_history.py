"""Exercise the publication guard against real Git trees, history and push hooks."""

from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

import check_public_history as guard


class PublicHistoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.repo = self.root / "repository"
        self.repo.mkdir()
        self.run_git("init", "-q", "-b", "main")
        self.run_git("config", "user.name", "Fixture Author")
        self.run_git("config", "user.email", "fixture@example.invalid")
        self.commit_file("score/README.md", "Local collection guide")
        self.clean = self.run_git("rev-parse", "HEAD").stdout.strip()

    def run_git(self, *args, check=True):
        return subprocess.run(["git", "-C", str(self.repo), *args], text=True,
                              capture_output=True, check=check)

    def commit_file(self, name, content):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        self.run_git("add", "--", name)
        self.run_git("commit", "-qm", "Fixture change")

    def test_only_directory_guide_is_allowed(self):
        self.assertEqual(guard.violations(self.repo, ["HEAD"])[0], [])
        self.commit_file("score/example/source/page-001.png", "Synthetic placeholder")
        self.assertTrue(guard.violations(self.repo, ["HEAD"])[0])

    def test_deleted_material_still_blocks_history(self):
        name = "score/example/notation/source/score.musicxml"
        self.commit_file(name, "Synthetic placeholder")
        self.run_git("rm", "--", name)
        self.run_git("commit", "-qm", "Remove fixture from latest tree")
        self.assertEqual(self.run_git("ls-tree", "-r", "--name-only", "HEAD", "score").stdout.strip(), "score/README.md")
        self.assertTrue(guard.violations(self.repo, ["HEAD"])[0])

    def test_material_copied_outside_score_is_blocked(self):
        self.commit_file("doc/example.MusicXML", "Synthetic placeholder")
        self.assertTrue(guard.violations(self.repo, ["HEAD"])[0])

    def test_tags_and_multiple_reference_updates_are_checked(self):
        self.commit_file("results/events.json", "[]")
        self.run_git("tag", "-a", "score-tag", "-m", "Synthetic tag")
        bad = self.run_git("rev-parse", "score-tag").stdout.strip()
        lines = [f"refs/heads/clean {self.clean} refs/heads/clean {'0' * 40}\n",
                 f"refs/tags/score-tag {bad} refs/tags/score-tag {'0' * 40}\n"]
        self.assertTrue(guard.violations(self.repo, guard.pushed_refs(lines))[0])
        self.assertEqual(guard.pushed_refs([f"(delete) {'0' * 40} refs/heads/old {bad}\n"]), [])

    def test_non_commit_objects_fail_closed(self):
        blob = self.run_git("rev-parse", "HEAD:score/README.md").stdout.strip()
        with self.assertRaises(subprocess.CalledProcessError):
            guard.violations(self.repo, [blob])

    def approve_example(self):
        name = "examples/tablature-recognition/original-study/input.png"
        content = "Synthetic excerpt placeholder"
        file = self.repo / name
        file.parent.mkdir(parents=True)
        file.write_text(content)
        manifest = self.repo / guard.EXAMPLE_MANIFEST
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({"files": {name: hashlib.sha256(file.read_bytes()).hexdigest()}}))
        self.run_git("add", ".")
        self.run_git("commit", "-qm", "Review exact synthetic example")
        return name

    def test_exact_reviewed_example_is_allowed(self):
        self.approve_example()
        self.assertEqual(guard.violations(self.repo, ["HEAD"])[0], [])

    def test_replacing_reviewed_excerpt_is_blocked(self):
        name = self.approve_example()
        self.commit_file(name, "A different or larger input")
        self.assertTrue(guard.violations(self.repo, ["HEAD"])[0])

    def test_unreviewed_example_sibling_is_blocked(self):
        self.approve_example()
        self.commit_file("examples/tablature-recognition/original-study/whole-song.musicxml", "Synthetic placeholder")
        self.assertTrue(guard.violations(self.repo, ["HEAD"])[0])

    def test_manifest_cannot_approve_private_score_collection(self):
        name = "score/example/input.png"
        file = self.repo / name
        file.parent.mkdir(parents=True)
        file.write_text("Synthetic placeholder")
        manifest = self.repo / guard.EXAMPLE_MANIFEST
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({"files": {name: hashlib.sha256(file.read_bytes()).hexdigest()}}))
        self.run_git("add", ".")
        self.run_git("commit", "-qm", "Invalid private-path exception")
        with self.assertRaises(ValueError):
            guard.violations(self.repo, ["HEAD"])

    def test_later_manifest_does_not_approve_earlier_unreviewed_history(self):
        name = "examples/tablature-recognition/original-study/input.png"
        self.commit_file(name, "Synthetic placeholder")
        manifest = self.repo / guard.EXAMPLE_MANIFEST
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({"files": {name: hashlib.sha256((self.repo / name).read_bytes()).hexdigest()}}))
        self.run_git("add", ".")
        self.run_git("commit", "-qm", "Review after earlier publication")
        self.assertTrue(guard.violations(self.repo, ["HEAD"])[0])

    def test_actual_hook_blocks_tainted_push_and_allows_clean_branch(self):
        project = Path(__file__).resolve().parents[1]
        for name in (".githooks/pre-push", "scripts/check_public_history.py"):
            destination = self.repo / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(project / name, destination)
        hook = self.repo / ".githooks/pre-push"
        hook.chmod(0o755)
        interpreter = self.repo / ".venv/bin/python"
        interpreter.parent.mkdir(parents=True)
        interpreter.symlink_to(sys.executable)
        self.run_git("config", "core.hooksPath", ".githooks")
        remote = self.root / "remote.git"
        subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
        self.run_git("remote", "add", "origin", str(remote))
        self.commit_file("score/example/recognized.gp5", "Synthetic placeholder")
        blocked = self.run_git("push", "origin", "main", check=False)
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("Push blocked", blocked.stderr)
        self.assertEqual(self.run_git("ls-remote", "origin").stdout, "")
        self.run_git("branch", "clean", self.clean)
        allowed = self.run_git("push", "origin", "clean", check=False)
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertIn("refs/heads/clean", self.run_git("ls-remote", "origin").stdout)


if __name__ == "__main__":
    unittest.main()
