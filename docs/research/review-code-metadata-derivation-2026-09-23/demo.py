#!/usr/bin/env python3
"""Replay the #343 finalizer on the #341 baseline cells, with and without their transcribed metadata, offline.

Usage: python3 docs/research/review-code-metadata-derivation-2026-09-23/demo.py [--output demo.json]

Materializes the #341 archive into a temporary root with savings_archive.py, then copies each
baseline cell's private directory into its task. Only two prefixes are rewritten: the realization
root and the baseline's installed skill root, in composition.json and in each accounting report's
raw_return. The bundle manifests stay byte for byte, so each report's manifest_sha256 still pairs.
Each cell is finalized twice with this checkout's finalizer, in the cell's repository, with the
cell's packet (pull requests) and saved fingerprint input (`{"specs": []}` on a pull request, whose
baseline review supplied no spec):

- transcribed: the composition as the baseline model wrote it. Derivation must accept every
  explicit field, so each copy equals the value its saved input owns, the context digest included.
- derived: the same composition with every field the finalizer derives removed.

It records the exits, the removed leaves, the derived digest against the baseline's, and whether
the public outputs (payload, batch, fragments; the gate record less finalization, at the baseline's
paths) match the committed baseline bytes and each other. No model runs.

Exit 0 when every cell behaves as README.md states; 1 otherwise; 2 when an input cannot be read or
the archive cannot be materialized.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
SAVINGS = ROOT / "docs/research/review-code-artifact-savings-2026-09-22"
SKILL = ROOT / "skills/review-code"
FINALIZER = SKILL / "scripts/finalize_review.py"
REALIZED, BASELINE_SKILL = "/tmp/rcs-savings/baseline", "/tmp/rcs-savings/skills/d8c2dd9/skills/review-code"
CELLS = {  # cell: (private directory, profile, committed public outputs, saved fingerprint input or None for {"specs": []})
    "publishable": ("private", "publishable", ("payload.json", "batch.json", "fragments.md"), None),
    "required-verification": ("private", "publishable", ("payload.json", "batch.json", "fragments.md"), None),
    "implementation-gate": ("private.4XwGSs", "implementation-gate", ("record.json",), "fingerprint-input.json"),
}
RUN_DERIVED = {"pull-request": ("head", "merge_base", "base_ref", "base_sha", "merged", "repository_url", "issues", "target_kind", "context"),
               "range": ("head", "merge_base", "merged", "issues", "context", "target", "change_description", "specs")}
PATHS_DERIVED = {"publishable": ("private_dir", "store", "composition", "skill_root"),
                 "implementation-gate": ("private_dir", "store", "composition", "addenda", "skill_root")}
BATCH_DERIVED = ("name", "phase", "raw_return")


def leaves(value) -> int:
    """Leaf count as #341's inventory counts it: a scalar or an empty list is one leaf, a list its elements."""
    if isinstance(value, dict):
        return sum(leaves(v) for v in value.values())
    if isinstance(value, list):
        return sum(leaves(v) for v in value) if value else 1
    return 1


def strip(composition: dict, profile: str) -> tuple[dict, int]:
    """The composition less every field the finalizer derives, and how many leaves that removes."""
    value, removed = copy.deepcopy(composition), 0
    run = value["run"]
    for key in RUN_DERIVED[run.get("target_kind", "pull-request")]:
        if key in run:
            removed += leaves(run.pop(key))
    record = value.get("record", {})
    paths = record.get("paths", {})
    for key in PATHS_DERIVED[profile]:
        if key in paths:
            removed += leaves(paths.pop(key))
    if "paths" in record and not paths:
        del record["paths"]
    for batch in record.get("verification", {}).get("batches", []):
        for key in BATCH_DERIVED:
            if key in batch:
                removed += leaves(batch.pop(key))
    return value, removed


def relocate(text: str, root: Path) -> str:
    return text.replace(BASELINE_SKILL, str(SKILL)).replace(REALIZED, str(root))


def restore(text: str, root: Path) -> str:
    return text.replace(str(SKILL), BASELINE_SKILL).replace(str(root), REALIZED)


def finalize(root: Path, cell: str, arm: str, composition: dict) -> tuple[subprocess.CompletedProcess, Path]:
    private_name, profile, _public, fingerprint = CELLS[cell]
    source = SAVINGS / "baseline" / cell / "work" / private_name
    private = root / cell / "work" / f"{private_name}-{arm}"
    shutil.copytree(source, private, ignore=shutil.ignore_patterns(*CELLS[cell][2], "report.md", "addenda"))
    for accounting in private.rglob("accounting.json"):
        report = json.loads(accounting.read_text(encoding="utf-8"))
        report["raw_return"] = relocate(report["raw_return"], root).replace(f"/{private_name}/", f"/{private.name}/")
        accounting.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    text = relocate(json.dumps(composition, indent=2, ensure_ascii=False), root).replace(f"/{private_name}/", f"/{private.name}/")
    text = text.replace(f'/{private_name}"', f'/{private.name}"')
    (private / "composition.json").write_text(text + "\n", encoding="utf-8")
    store = next(p for p in private.iterdir() if p.name.startswith(("review-context", "store")) and p.suffix == ".json")
    args = [sys.executable, str(FINALIZER), "--profile", profile, "--store", str(store), "--compact"]
    if profile == "publishable":
        args += ["--packet", str(root / cell / "inputs" / "packet.json")]
        (private / "fingerprint.json").write_text('{"specs": []}\n', encoding="utf-8")
        fingerprint = "fingerprint.json"
    args += ["--fingerprint-input", str(private / fingerprint), str(private)]
    return subprocess.run(args, cwd=root / cell / "repo", capture_output=True, text=True, encoding="utf-8"), private


def public_bytes(cell: str, private: Path, root: Path) -> dict[str, bytes]:
    out = {}
    for name in CELLS[cell][2]:
        text = (private / name).read_text(encoding="utf-8")
        if name == "record.json":
            record = json.loads(text)
            record.pop("finalization")
            text = json.dumps(record, indent=2) + "\n"
        text = restore(text, root).replace(f"/{private.name}", f"/{CELLS[cell][0]}")
        out[name] = text.encode("utf-8")
    return out


def replay(root: Path, cell: str) -> dict:
    private_name, profile, public, _fingerprint = CELLS[cell]
    baseline = json.loads((SAVINGS / "baseline" / cell / "work" / private_name / "composition.json").read_text(encoding="utf-8"))
    derived, removed = strip(baseline, profile)
    row = {"cell": cell, "profile": profile, "mechanical_leaves_removed": removed,
           "baseline_composition_leaves": leaves(baseline), "derived_composition_leaves": leaves(derived)}
    outputs = {}
    for arm, composition in (("transcribed", baseline), ("derived", derived)):
        result, private = finalize(root, cell, arm, composition)
        first = next((line for line in result.stdout.splitlines() if " failed with exit " in line), None)
        row[arm] = {"exit": result.returncode, "failed_stage": first.split(" failed", 1)[0] if first else None}
        if result.returncode != 0:
            row[arm]["output"] = restore(result.stdout, root)
            continue
        outputs[arm] = public_bytes(cell, private, root)
        row[arm]["public_bytes_match_baseline"] = {name: outputs[arm][name] == (SAVINGS / "baseline" / cell / "work" / private_name / name).read_bytes()
                                                   for name in public}
        retained = json.loads((private / ("record.json" if profile == "implementation-gate" else "composition.json")).read_text(encoding="utf-8"))
        row[arm]["context_matches_baseline"] = retained["run"]["context"] == baseline["run"]["context"]
    if len(outputs) == 2:
        row["arms_identical"] = outputs["transcribed"] == outputs["derived"]
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", help="write the rows as JSON here")
    args = parser.parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix="rcs343-") as scratch:
            root = Path(scratch) / "root"
            built = subprocess.run([sys.executable, str(ROOT / "docs/research/tools/savings_archive.py"), "materialize",
                                    str(SAVINGS / "archive"), "--root", str(root), "--skill-root", str(SKILL)],
                                   capture_output=True, text=True, encoding="utf-8")
            if built.returncode != 0:
                print(f"demo: cannot materialize the archive: {built.stdout}{built.stderr}", file=sys.stderr)
                return 2
            rows = [replay(root, cell) for cell in CELLS]
    except (OSError, ValueError, StopIteration) as error:
        print(f"demo: cannot read a baseline input: {error}", file=sys.stderr)
        return 2
    text = json.dumps(rows, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    ok = {row["cell"]: row for row in rows}
    refused = ok["required-verification"]
    expected = (all(refused[arm]["failed_stage"] == "accounting" for arm in ("transcribed", "derived"))
                and all(ok[c][arm]["exit"] == 0 and all(ok[c][arm]["public_bytes_match_baseline"].values())
                        and ok[c][arm]["context_matches_baseline"] and ok[c]["arms_identical"]
                        for c in ("publishable", "implementation-gate") for arm in ("transcribed", "derived")))
    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
