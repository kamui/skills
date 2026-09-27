#!/usr/bin/env python3
"""Measure review-code's instruction sets with removal candidates applied to a copy.

Usage: measure.py [--commit SHA] [--tests] [--keep] ID [ID ...]

Extracts SHA's tree into a temporary directory, removes each named span from the
copy's `skills/review-code` text, and runs the copy's `test_instruction_budget.py`.
`--tests` also runs every other `test_*.py` beside it. `--keep` leaves the copy in
place and prints its path. The checkout is never written.

Span ids are the ones README.md uses. A line span is inclusive and takes the blank
line after its paragraph; a byte span is 1-indexed and inclusive within one line,
as `cut -b` counts. Each span carries its measured size at the pinned commit, and a
different size is refused.

Exit 0 when every run passed, 1 when a span's size differs or a test failed, 2 when
git, tar or a script could not run.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PINNED = "05e336791ffd7f42abb74421df47032405fe0b52"
SKILL = Path("skills/review-code")
LINES = {  # id: (file, first line, last line, bytes)
    "R1": ("references/output.md", 15, 16, 598),
    "R2": ("references/output.md", 19, 20, 118),
    "R3": ("references/prior-state.md", 3, 4, 369),
    "R4": ("references/prior-state.md", 34, 35, 255),
    "R7": ("references/verification.md", 3, 4, 241),
    "R8": ("references/targets.md", 59, 60, 329),
    "R9": ("references/targets.md", 3, 4, 79),
    "O2": ("references/rubric.md", 66, 67, 394),
    "O3": ("references/output.md", 11, 12, 253),
    "O4": ("references/verifier-concurrency.md", 5, 6, 275),
    "N1": ("references/verification.md", 19, 20, 251),
    "N2": ("SKILL.md", 51, 52, 165),
    "N3": ("references/verifier.md", 38, 45, 1322),
    "N4": ("references/verifier.md", 54, 78, 656),
    "N5": ("references/prior-state.md", 23, 24, 229),
}
BYTES = {  # id: (file, line, ((first byte, last byte), ...))
    "R5": ("SKILL.md", 34, ((309, 467),)),
    "R6": ("references/output.md", 21, ((1, 297),)),
    "R10": ("references/output.md", 25, ((456, 697),)),
    "R11": ("references/output.md", 33, ((1, 169),)),
    "R12": ("references/output.md", 35, ((1, 88), (357, 460))),
    "O1": ("references/rubric.md", 72, ((259, 382),)),
}


def run(command: list[str], cwd: Path, **kwargs) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(command, cwd=cwd, **kwargs)
    except OSError as error:
        print(f"{' '.join(command)}: {error}", file=sys.stderr)
        raise SystemExit(2)


def extract(commit: str, root: Path, tree: Path) -> None:
    archive = run(["git", "archive", commit], root, capture_output=True)
    if archive.returncode != 0:
        print(f"git archive {commit}: {archive.stderr.decode('utf-8', 'replace').strip()}", file=sys.stderr)
        raise SystemExit(2)
    if run(["tar", "-x", "-C", str(tree)], root, input=archive.stdout).returncode != 0:
        print("tar -x failed", file=sys.stderr)
        raise SystemExit(2)


def apply(tree: Path, ids: list[str]) -> list[str]:
    """Remove the spans from the copy, last span first within a file; return size mismatches."""
    edits: dict[str, list[tuple[int, str]]] = {}
    for name in ids:
        file, line = (LINES[name][0], LINES[name][1]) if name in LINES else BYTES[name][:2]
        edits.setdefault(file, []).append((line, name))
    mismatches = []
    for file, spans in edits.items():
        path = tree / SKILL / file
        lines = path.read_bytes().split(b"\n")
        for _line, name in sorted(spans, reverse=True):
            if name in LINES:
                _file, first, last, expected = LINES[name]
                measured = sum(len(text) + 1 for text in lines[first - 1:last])
                del lines[first - 1:last]
            else:
                _file, line, ranges = BYTES[name]
                text, measured, expected = lines[line - 1], 0, sum(b - a + 1 for a, b in ranges)
                for first, last in sorted(ranges, reverse=True):
                    measured += len(text[first - 1:last])
                    text = text[:first - 1] + text[last:]
                lines[line - 1] = text
            print(f"{name}: {file}, {measured} bytes", flush=True)
            if measured != expected:
                mismatches.append(f"{name}: measured {measured} bytes, expected {expected}")
        path.write_bytes(b"\n".join(lines))
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ids", nargs="*", metavar="ID", help="span ids to remove; none measures the commit as it is")
    parser.add_argument("--commit", default=PINNED, help="commit to extract (default: the pinned commit)")
    parser.add_argument("--tests", action="store_true", help="also run every other test_*.py")
    parser.add_argument("--keep", action="store_true", help="keep the trimmed copy and print its path")
    args = parser.parse_args()
    unknown = [name for name in args.ids if name not in LINES and name not in BYTES]
    if unknown:
        parser.error(f"unknown span id: {', '.join(unknown)}")

    root = Path(run(["git", "rev-parse", "--show-toplevel"], Path.cwd(), capture_output=True, text=True,
                    encoding="utf-8").stdout.strip())
    tree = Path(tempfile.mkdtemp(prefix="rc394-"))
    try:
        extract(args.commit, root, tree)
        failures = apply(tree, args.ids)
        scripts = tree / SKILL / "scripts"
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        tests = sorted(scripts.glob("test_*.py")) if args.tests else [scripts / "test_instruction_budget.py"]
        for test in tests:
            budget = test.name == "test_instruction_budget.py"
            done = run([sys.executable, "-B", str(test)], tree, capture_output=not budget, text=True,
                       encoding="utf-8", env=environment)
            if not budget:
                print(f"{test.name}: {'pass' if done.returncode == 0 else 'FAIL'}")
            if done.returncode != 0:
                failures.append(f"{test.name}: exit {done.returncode}")
        for failure in failures:
            print(failure)
        if args.keep:
            print(f"copy: {tree}")
        return 1 if failures else 0
    finally:
        if not args.keep:
            shutil.rmtree(tree, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
