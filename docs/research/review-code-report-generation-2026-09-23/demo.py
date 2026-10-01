#!/usr/bin/env python3
"""Replay the #342 finalizer on the #341 baseline cells' saved compositions, offline.

Usage: python3 docs/research/review-code-report-generation-2026-09-23/demo.py [--output demo.json]

Copies each baseline cell's private directory from
docs/research/review-code-artifact-savings-2026-09-22/baseline into a temporary
directory, relocates only the private-directory prefix inside composition.json,
and runs this checkout's skills/review-code/scripts/finalize_review.py with
--compact. For each cell it records the exit, the public outputs' byte equality
with the committed baseline outputs, whether each item body appears once in the
generated report, and the model-authored report size at the baseline against
the generated report. No model runs, and no composition field is added.

Exit 0 when every cell behaves as README.md states; 1 otherwise; 2 when an
input cannot be read.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / "docs/research/review-code-artifact-savings-2026-09-22/baseline"
FINALIZER = ROOT / "skills/review-code/scripts/finalize_review.py"
CELLS = {  # cell: (private directory, profile, committed public outputs)
    "publishable": ("private", "publishable", ("payload.json", "batch.json", "fragments.md")),
    "required-verification": ("private", "publishable", ("payload.json", "batch.json", "fragments.md")),
    "implementation-gate": ("private.4XwGSs", "implementation-gate", ("record.json",)),
}
REALIZED = "/tmp/rcs-savings/baseline/{cell}/work/{private}"


def replay(cell: str, scratch: Path) -> dict:
    private_name, profile, public = CELLS[cell]
    source = BASELINE / cell / "work" / private_name
    private = scratch / cell
    shutil.copytree(source, private)
    realized = REALIZED.format(cell=cell, private=private_name)
    composition = (private / "composition.json").read_text(encoding="utf-8").replace(realized, str(private))
    (private / "composition.json").write_text(composition, encoding="utf-8")
    value = json.loads(composition)
    store = value.get("record", {}).get("paths", {}).get("store") or str(next(private.glob("store.json")))
    args = [sys.executable, str(FINALIZER), "--profile", profile, "--store", store, "--compact", str(private)]
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    authored = (BASELINE / cell / "work" / "report.md").read_text(encoding="utf-8")
    row = {"cell": cell, "profile": profile, "exit": result.returncode, "stdout": result.stdout.replace(str(private), "<private>"),
           "baseline_authored_report_chars": len(authored), "composition_has_record": "record" in value}
    if result.returncode != 0:
        return row
    same = {}
    for name in public:
        produced = (private / name).read_text(encoding="utf-8")
        if name == "record.json":  # compare the composer's record, less its finalization, at the realized paths
            record = json.loads(produced)
            record.pop("finalization")
            produced = json.dumps(record, indent=2) + "\n"
        same[name] = produced.replace(str(private), realized).encode("utf-8") == (source / name).read_bytes()
    report = (private / "report.md").read_text(encoding="utf-8")
    payload = json.loads((private / public[0]).read_text(encoding="utf-8"))
    row.update(public_bytes_unchanged=same, generated_report_chars=len(report),
               model_output_chars_under_artifacts=len(result.stdout),
               every_item_body_once=all(report.count(item["markdown"]) == 1 for item in payload["items"]),
               summary_body_once=report.count(payload["summary"]["body"].rstrip("\n")) == 1)
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", help="write the rows as JSON here")
    args = parser.parse_args()
    try:
        with tempfile.TemporaryDirectory() as scratch:
            rows = [replay(cell, Path(scratch)) for cell in CELLS]
    except (OSError, ValueError, StopIteration) as error:
        print(f"demo: cannot read a baseline input: {error}", file=sys.stderr)
        return 2
    text = json.dumps(rows, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    ok = {row["cell"]: row for row in rows}
    expected = (ok["required-verification"]["exit"] == 1
                and all(ok[c]["exit"] == 0 and all(ok[c]["public_bytes_unchanged"].values()) and ok[c]["every_item_body_once"]
                        and ok[c]["summary_body_once"] for c in ("publishable", "implementation-gate")))
    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
