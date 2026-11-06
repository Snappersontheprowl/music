#!/usr/bin/env python3
"""Reject score material anywhere in the history of refs intended for publication."""

import argparse
from pathlib import Path, PurePosixPath
import subprocess
import sys


SCORE_SUFFIXES = {
    ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".pdf", ".musicxml", ".mxl",
    ".gp", ".gp3", ".gp4", ".gp5", ".gpx", ".mscz", ".mscx", ".omr",
    ".mid", ".midi", ".bundle", ".zip", ".tar", ".gz", ".pack",
}
TRANSCRIPTION_NAMES = {
    "events.json", "reference.json", "parsed.json", "conversion.json", "preview.txt",
}


def git(repository, *args):
    return subprocess.check_output(["git", "-C", str(repository), *args], stderr=subprocess.PIPE)


def forbidden(path):
    if path == "score/README.md":
        return False
    file = PurePosixPath(path)
    return (file.parts[0].casefold() == "score" or
            file.suffix.casefold() in SCORE_SUFFIXES or
            file.name.casefold() in TRANSCRIPTION_NAMES)


def pushed_refs(lines):
    refs = []
    for line in lines:
        fields = line.split()
        if len(fields) != 4:
            raise ValueError("Malformed pre-push reference update")
        _local_ref, local_oid, _remote_ref, _remote_oid = fields
        if set(local_oid) == {"0"}:  # Deleting a remote ref sends no local history.
            continue
        refs.append(local_oid)
    return refs


def violations(repository, refs):
    commits = set()
    for ref in refs:
        # Annotated tags are allowed only when they ultimately refer to a commit.
        commit = git(repository, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}").strip().decode()
        commits.update(git(repository, "rev-list", commit).splitlines())
    bad = []
    for commit in sorted(commits):
        paths = git(repository, "ls-tree", "-rz", "--name-only", commit.decode()).split(b"\0")
        for raw in paths:
            if raw:
                path = raw.decode("utf-8", errors="surrogateescape")
                if forbidden(path):
                    bad.append((commit.decode(), path))
    return bad, len(commits)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pre-push", action="store_true", help="Read Git's reference updates from stdin")
    parser.add_argument("refs", nargs="*", help="Refs to inspect; default HEAD (hook remote arguments are ignored)")
    args = parser.parse_args()
    try:
        repository = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").decode().strip())
        refs = pushed_refs(sys.stdin) if args.pre_push else (args.refs or ["HEAD"])
        bad, count = violations(repository, refs)
    except (ValueError, subprocess.CalledProcessError, OSError) as error:
        print(f"Public-history check failed; push blocked: {error}", file=sys.stderr)
        return 1
    if bad:
        print("Push blocked: score material or private archives exist in the proposed history.", file=sys.stderr)
        for commit, path in bad[:12]:
            print(f"  {commit[:12]} {path}", file=sys.stderr)
        if len(bad) > 12:
            print(f"  ... {len(bad) - 12} more entries", file=sys.stderr)
        print("Keep scores local and remove them from all proposed commits, not only the latest tree.", file=sys.stderr)
        return 1
    print(f"Public-history check passed ({count} reachable commits).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
