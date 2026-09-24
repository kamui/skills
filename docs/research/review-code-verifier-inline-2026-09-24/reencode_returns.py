#!/usr/bin/env python3
"""Re-encode the four archived #341 verifier returns for the inline-only bundle identity of #358.

Usage:
    python3 reencode_returns.py write [--skill-root SKILL]
    python3 reencode_returns.py check [--skill-root SKILL]

The #341 archive and baseline cells hold four verifier bundles, each with a raw return that echoes
its manifest's SHA-256 (``verifier-manifest/2``, ``verifier-accounting/2``). ``write`` rebuilds each
bundle from its archived projected ``input.json`` with SKILL's ``build_verifier_prompt.py`` into
``fixtures/<name>/bundle``, which gives it a fresh ``bundle_id``, and writes
``fixtures/<name>/raw-return.json``: the archived return with ``manifest_sha256`` replaced, in place,
by that ID. Nothing else in the return changes, and the originals stay where they are. The archived
continuation seed is a template; its ``@TASK_ROOT@`` is realized as ``/tmp/rcs-savings/baseline/
continuation``, the root the #341 baseline cell used. ``write`` refuses to replace existing fixtures.

``check`` accounts each re-encoded return with SKILL's ``account_verifier_return.py`` into a scratch
directory and compares the report with the archived ``accounting.json``: the same structural result,
violations, accounted and withheld IDs, and the same returned records once the identity key is set
aside. It also requires the rebuilt bundle's projected input to equal the archived one, and SKILL's
helper to refuse each archived old-format bundle with exit 1 and no report, so this conversion
authorizes no live old-format return. One JSON line per fixture goes to stdout.

SKILL defaults to this repository's ``skills/review-code``.

Exit codes: 0 success; 1 a comparison failed, one line per failure on stderr; 2 an input cannot be
read, a helper cannot run, or ``write`` would replace a fixture.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
SAVINGS = HERE.parent / "review-code-artifact-savings-2026-09-22"
TASK_ROOT = "/tmp/rcs-savings/baseline/continuation"
# Each archived #341 bundle directory holds input.json, brief.md, manifest.json, raw-return.json and accounting.json.
SOURCES = {
    "archive-continuation-initial": SAVINGS / "archive/tasks/continuation/review/initial",
    "baseline-publishable-initial": SAVINGS / "baseline/publishable/work/private/verify-initial",
    "baseline-required-verification-initial": SAVINGS / "baseline/required-verification/work/private/bundle-initial",
    "baseline-continuation-follow-up": SAVINGS / "baseline/continuation/work/followup",
}
FIXTURES = HERE / "fixtures"


class Failure(Exception):
    """An input that cannot be read or a helper that cannot run: exit 2."""


def read_json(path: Path, realize: bool = False):
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise Failure(f"cannot read {path}: {error}") from error
    if realize:
        text = text.replace("@TASK_ROOT@", TASK_ROOT)
    return json.loads(text)


def run(command: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    except OSError as error:
        raise Failure(f"cannot run `{' '.join(command)}`: {error}") from error


def without(value: dict, key: str) -> dict:
    return {k: v for k, v in value.items() if k != key}


def write(skill: Path) -> int:
    for name, source in SOURCES.items():
        target = FIXTURES / name
        if target.exists():
            raise Failure(f"fixture already exists: {target}")
        # Build in scratch, so the builder's timing event lands there, and copy only the bundle.
        with tempfile.TemporaryDirectory() as scratch:
            projected = Path(scratch) / "input.json"
            projected.write_text(json.dumps(read_json(source / "input.json", realize=True), ensure_ascii=False), encoding="utf-8")
            result = run(["python3", str(skill / "scripts" / "build_verifier_prompt.py"), str(projected),
                          "--output", str(Path(scratch) / "bundle")])
            if result.returncode != 0:
                raise Failure(f"{name}: build exited {result.returncode}: {result.stdout}{result.stderr}")
            target.mkdir(parents=True)
            shutil.copytree(Path(scratch) / "bundle", target / "bundle")
        bundle_id = read_json(target / "bundle" / "manifest.json")["bundle_id"]
        original = read_json(source / "raw-return.json")
        reencoded = {("bundle_id" if key == "manifest_sha256" else key): (bundle_id if key == "manifest_sha256" else value)
                     for key, value in original.items()}
        (target / "raw-return.json").write_text(json.dumps(reencoded, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"fixture": name, "source": str(source.relative_to(REPO)), "bundle_id": bundle_id}))
    return 0


def check(skill: Path) -> int:
    failures = []
    helper = str(skill / "scripts" / "account_verifier_return.py")
    with tempfile.TemporaryDirectory() as scratch:
        for name, source in SOURCES.items():
            fixture = FIXTURES / name
            archived = read_json(source / "accounting.json")
            original = read_json(source / "raw-return.json")
            reencoded = read_json(fixture / "raw-return.json")
            manifest = read_json(fixture / "bundle" / "manifest.json")
            # Account scratch copies: the helper's timing event lands beside the bundle it reads.
            work = Path(scratch) / name
            shutil.copytree(fixture / "bundle", work / "fixture" / "bundle")
            shutil.copytree(source, work / "archived" / "bundle")
            report_path = work / "accounting.json"
            result = run(["python3", helper, "--bundle", str(work / "fixture" / "bundle"), "--output", str(report_path),
                          str(fixture / "raw-return.json")])
            if result.returncode not in (0, 1) or not report_path.exists():
                raise Failure(f"{name}: accounting exited {result.returncode}: {result.stdout}{result.stderr}")
            report = read_json(report_path)
            problems = []
            if read_json(fixture / "bundle" / "input.json") != read_json(source / "input.json", realize=True):
                problems.append("the rebuilt bundle's projected input differs from the archived input")
            if list(reencoded) != [("bundle_id" if key == "manifest_sha256" else key) for key in original]:
                problems.append("the re-encoded return's keys are not the archived keys with the identity key replaced")
            if reencoded.get("bundle_id") != manifest.get("bundle_id") or report.get("bundle_id") != manifest.get("bundle_id"):
                problems.append("the re-encoded return does not carry its bundle's ID")
            if without(reencoded, "bundle_id") != without(original, "manifest_sha256"):
                problems.append("the re-encoded return's records differ from the archived return")
            for key in ("structurally_complete", "violations", "accounted", "withheld"):
                if report.get(key) != archived.get(key):
                    problems.append(f"`{key}` is {json.dumps(report.get(key))}, archived {json.dumps(archived.get(key))}")
            if without(report.get("return", {}), "bundle_id") != without(archived.get("return", {}), "manifest_sha256"):
                problems.append("the accounted return's judgments or evidence differ from the archived accounting")
            refused_path = work / "archived-accounting.json"
            refused = run(["python3", helper, "--bundle", str(work / "archived" / "bundle"), "--output", str(refused_path),
                           str(source / "raw-return.json")])
            if refused.returncode != 1 or refused_path.exists() or "verifier-manifest/3" not in refused.stdout:
                problems.append(f"the archived old-format bundle was not refused: exit {refused.returncode}, {refused.stdout.strip()}")
            failures += [f"{name}: {problem}" for problem in problems]
            print(json.dumps({"fixture": name, "bundle_id": manifest.get("bundle_id"), "format": report.get("format"),
                              "structurally_complete": report.get("structurally_complete"),
                              "accounted": report.get("accounted"), "withheld": report.get("withheld"),
                              "matches_archived_accounting": not problems, "old_format_refused": refused.returncode == 1}))
    for failure in failures:
        print(failure, file=sys.stderr)
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("write", "check"))
    parser.add_argument("--skill-root", default=str(REPO / "skills" / "review-code"))
    args = parser.parse_args()
    try:
        return (write if args.command == "write" else check)(Path(args.skill_root).resolve())
    except (Failure, ValueError) as error:
        print(f"reencode_returns: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
