#!/usr/bin/env python3
"""Reproduce only the supplied four-measure excerpt into a new local score directory."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="New directory inside the local score/ collection")
    args = parser.parse_args()
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        parser.error("Run with the project .venv/bin/python")
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(ROOT / "score") or output == ROOT / "score":
        parser.error("Outputs must remain in the local score/ collection")
    if output.exists():
        parser.error("Output directory already exists; preserve the previous run")
    source = json.loads((HERE / "source.json").read_text(encoding="utf-8"))
    if hashlib.sha256((HERE / "input.png").read_bytes()).hexdigest() != source["input_sha256"]:
        parser.error("The supplied input does not match the reviewed excerpt")
    plan = json.loads((HERE / "plan.json").read_text(encoding="utf-8"))
    if len(plan["systems"]) != 1 or plan["systems"][0]["measures"] != 4:
        parser.error("This example is limited to one system and four measures")
    with tempfile.TemporaryDirectory(prefix="excerpt-input-", dir=ROOT / "score") as directory:
        directory = Path(directory)
        shutil.copy2(HERE / "input.png", directory / "input.png")
        plan["systems"][0]["source"] = str((directory / "input.png").relative_to(ROOT))
        plan_path = directory / "plan.json"
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        subprocess.run([sys.executable, str(ROOT / "tools/PDF-to-GP5/export.py"),
                        str(plan_path), str(output)], cwd=ROOT, check=True)
    xml = ET.parse(output / "opening.musicxml").getroot()
    assert len(xml.findall(".//measure")) == 4
    print(f"Four-measure reproduction completed: {output}")


if __name__ == "__main__":
    main()
