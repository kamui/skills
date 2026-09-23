#!/usr/bin/env python3
"""Replay #341's continuation cell through the #345 continuation helper, with and without its mechanical fields, offline.

Usage: python3 docs/research/review-code-continuation-composer-2026-09-23/demo.py [--output demo.json]

For each arm, materializes the #341 archive's continuation task into its own temporary root with
savings_archive.py, copies the baseline cell's follow-up verifier bundle into the task's work directory
(rewriting only the realization-root prefix of its accounting report's raw_return, so the bundle
manifest and its hash stay byte for byte), builds the continuation store with review_context.py
--prior-head, and runs this checkout's continue_review.py compose on an input taken from the addendum
the baseline model wrote by hand:

- transcribed: the addendum exactly as written. Composition must accept every explicit field, so each
  copy equals the value the chain, store, bundle or accounting report owns.
- derived: the same addendum with every field the helper derives removed.

It records each arm's exit, the leaves removed, whether the saved addendum (less `finalization`, at the
baseline's realization root) is byte-identical to the baseline's, whether the arms agree, the chain
state afterwards, and the bytes a continuation reads to establish current state: the record and
earlier addenda by hand at the baseline, or `state --json` now. No model runs.

Exit 0 when every arm behaves as README.md states; 1 otherwise; 2 when an input cannot be read or the
archive cannot be materialized.
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
HELPER = SKILL / "scripts/continue_review.py"
REALIZED = "/tmp/rcs-savings/baseline"
BASE, REVIEWED, FINAL = ("2301c83ee0b2ba0248fe3d2d1f6cd481963545ab", "03ce7cd85d34afda4ae47f06d7958ea906b3fcc1",
                         "b96a362e99ce4f5b6b1fe26ad02fda66e8343723")
BASELINE = SAVINGS / "baseline/continuation/addenda" / f"addendum-{FINAL}.json"
DERIVED_TOP = ("format", "workflow", "record", "record_format", "reviewed_head", "final_head", "replaced_by_full_review", "routed")
DERIVED_VERIFICATION = ("allowance", "outstanding")
DERIVED_BATCH = ("name", "phase", "raw_return")


def leaves(value) -> int:
    """Leaf count as #341's inventory counts it: a scalar or an empty list is one leaf, a list its elements."""
    if isinstance(value, dict):
        return sum(leaves(v) for v in value.values())
    if isinstance(value, list):
        return sum(leaves(v) for v in value) if value else 1
    return 1


def strip(addendum: dict) -> tuple[dict, int]:
    """The addendum less every field the helper derives, and how many leaves that removes."""
    value, removed = copy.deepcopy(addendum), 0
    for key in DERIVED_TOP:
        removed += leaves(value.pop(key))
    for key in DERIVED_VERIFICATION:
        removed += leaves(value["verification"].pop(key))
    for batch in value["verification"]["batches"]:
        for key in DERIVED_BATCH:
            removed += leaves(batch.pop(key))
    return value, removed


def inventory(scratch: Path, value: dict) -> dict:
    """Mechanical and judgment leaves under #341's addendum inventory (interface_metrics.py fields).

    A derived input carries no `format`, which the inventory keys the shape on, so it is classified with
    that one mechanical leaf added and then subtracted.
    """
    added = "format" not in value
    path = scratch / "inventory.json"
    path.write_text(json.dumps({"format": "implementation-gate-addendum/2", **value}), encoding="utf-8")
    fields = subprocess.run([sys.executable, str(ROOT / "docs/research/tools/interface_metrics.py"), "fields", str(path)],
                            capture_output=True, text=True, encoding="utf-8", check=True)
    row = json.loads(fields.stdout)[0]
    return {"mechanical": row["mechanical"]["fields"] - int(added), "judgment": row["judgment"]["fields"]}


def materialize(scratch: Path, arm: str) -> Path:
    root = scratch / arm
    built = subprocess.run([sys.executable, str(ROOT / "docs/research/tools/savings_archive.py"), "materialize", str(SAVINGS / "archive"),
                            "--root", str(root), "--skill-root", str(SKILL), "--task", "continuation"],
                           capture_output=True, text=True, encoding="utf-8")
    if built.returncode != 0:
        raise OSError(f"cannot materialize the archive: {built.stdout}{built.stderr}")
    task = root / "continuation"
    followup = task / "work" / "followup"
    shutil.copytree(SAVINGS / "baseline/continuation/work/followup", followup)
    accounting = followup / "accounting.json"
    report = json.loads(accounting.read_text(encoding="utf-8"))
    report["raw_return"] = report["raw_return"].replace(REALIZED, str(root))
    accounting.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    store = task / "work" / "store.json"
    context = subprocess.run([sys.executable, str(SKILL / "scripts/review_context.py"), "--merge-base", BASE, "--head", FINAL,
                              "--prior-head", REVIEWED, "--base-ref", "main", "--store", str(store)],
                             cwd=task / "repo", capture_output=True, text=True, encoding="utf-8")
    if context.returncode != 0:
        raise OSError(f"cannot build the continuation store: {context.stdout}{context.stderr}")
    return root


def arm(scratch: Path, name: str, value: dict) -> tuple[dict, bytes | None]:
    root = materialize(scratch, name)
    task = root / "continuation"
    record = task / "review" / "record.json"
    at_baseline = lambda text: len(text.replace(str(root), REALIZED).encode("utf-8"))  # noqa: E731 (sizes at the baseline root)
    before = sum(at_baseline(p.read_text(encoding="utf-8")) for p in (record, *sorted((task / "review/addenda").glob("*.json"))))
    state_before = subprocess.run([sys.executable, str(HELPER), "state", "--json", str(record)], capture_output=True, text=True, encoding="utf-8")
    source = task / "work" / "continuation.json"
    source.write_text(json.dumps(json.loads(json.dumps(value).replace(REALIZED, str(root))), indent=2) + "\n", encoding="utf-8")
    result = subprocess.run([sys.executable, str(HELPER), "compose", "--record", str(record), "--store", str(task / "work/store.json"), str(source)],
                            capture_output=True, text=True, encoding="utf-8")
    row = {"exit": result.returncode, "authored_leaves": leaves(value), "inventory_341": inventory(Path(scratch), value),
           "state_read_bytes": {"baseline_record_and_addenda": before, "state_json": at_baseline(state_before.stdout)}}
    if result.returncode != 0:
        row["output"] = result.stdout.replace(str(root), REALIZED)
        return row, None
    saved = json.loads((task / "review/addenda" / f"addendum-{FINAL}.json").read_text(encoding="utf-8"))
    finalization = saved.pop("finalization")
    public = (json.dumps(saved, indent=2) + "\n").replace(str(root), REALIZED).encode("utf-8")
    report = Path(finalization["report"])
    after = subprocess.run([sys.executable, str(HELPER), "state", str(record)], capture_output=True, text=True, encoding="utf-8")
    row.update(addendum_matches_baseline=public == BASELINE.read_bytes(), report_bytes=at_baseline(report.read_text(encoding="utf-8")),
               report_distinct_from_record_report=report != task / "review" / "report.md",
               state_after={"exit": after.returncode, "lines": after.stdout.replace(str(root), REALIZED).splitlines()[:3]})
    return row, public


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", help="write the rows as JSON here")
    args = parser.parse_args()
    try:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        derived, removed = strip(baseline)
        with tempfile.TemporaryDirectory(prefix="rcs345-") as scratch:
            rows = {"baseline_addendum_leaves": leaves(baseline), "mechanical_leaves_removed": removed, "arms": {}}
            outputs = {}
            for name, value in (("transcribed", baseline), ("derived", derived)):
                rows["arms"][name], outputs[name] = arm(Path(scratch), name, value)
            rows["arms_identical"] = outputs["transcribed"] is not None and outputs["transcribed"] == outputs["derived"]
            example = subprocess.run([sys.executable, str(HELPER), "--example"], capture_output=True, check=True).stdout
            rows["instruction_bytes"] = {"continuation-addendum.md": (SKILL / "references/continuation-addendum.md").stat().st_size,
                                         "implement-publish continuation.md":
                                             (ROOT / "skills/implement-publish/references/continuation.md").stat().st_size,
                                         "continue_review.py --example": len(example)}
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"demo: {error}", file=sys.stderr)
        return 2
    text = json.dumps(rows, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    arms = rows["arms"].values()
    expected = rows["arms_identical"] and all(a["exit"] == 0 and a["addendum_matches_baseline"] and a["state_after"]["exit"] == 0
                                              and a["report_distinct_from_record_report"] for a in arms)
    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
