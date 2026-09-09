#!/usr/bin/env python3
"""Assemble #150's stage record from the cell summaries and the reconciled ledger.

The pilot's handoff is the artifact #151 and #152 read, so it has to say three
things without hedging: what happened to each of the six planned cells, what every
attempt cost including the ones that were not measured, and whether the pilot was
faithful and affordable enough for the grid to continue under unchanged rules.

``continue`` is returned only when every planned cell reached a valid completed
dispatch with no unresolved fidelity problem and the remaining allowance still
covers the rest of the grid. Anything else is a ``stopped-*`` disposition naming
the reason, because a partial pilot reported as a success would authorise eighteen
more cells on evidence that does not support them.

Like every other public artifact here, cells are named by schedule position and
never by slot: the selection rule is public, so naming the pilot's slots would
disclose which slot holds the clean control.

Usage::

    python3 write_handoff.py --config pilot-config.json --bundle BUNDLE \\
        [--seal BUNDLE/sealed/seal.json] --out BUNDLE/handoff.json
    python3 write_handoff.py --self-test

Exit: 0 on success, 1 on a content violation with one line per violation on
stdout, 2 when an input cannot be read.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

PLANNED_PILOT_CELLS = 6


def load(path, default=None):
    try:
        return json.loads(Path(os.path.expanduser(str(path))).read_text(encoding="utf-8"))
    except FileNotFoundError:
        if default is not None:
            return default
        sys.stderr.write("missing %s\n" % path)
        raise SystemExit(2)
    except (OSError, ValueError) as exc:
        sys.stderr.write("cannot read %s: %s\n" % (path, exc))
        raise SystemExit(2)


def usd(value) -> Decimal:
    return Decimal(str(value or "0"))


def cell_records(bundle) -> list:
    """One record per planned pilot cell, by position, with its disposition."""
    records = []
    for position in range(1, PLANNED_PILOT_CELLS + 1):
        summary_path = Path(bundle) / "cells" / ("position-%02d" % position) / "summary.json"
        if not summary_path.is_file():
            records.append({"position": position, "disposition": "unattempted",
                            "reason": "no summary was produced for this position"})
            continue
        summary = load(summary_path)
        phases = summary.get("phases") or []
        completed = bool(phases) and all(phase.get("exit_code") == 0
                                         and phase.get("is_error") is False
                                         for phase in phases)
        records.append({
            "position": position,
            "arm": summary.get("arm"),
            "replicate": summary.get("replicate"),
            "worker_model": summary.get("worker_model"),
            "disposition": summary.get("disposition"),
            "valid_completed": completed and not summary.get("problems"),
            "elapsed_seconds": summary.get("elapsed_seconds"),
            "settled_usd": (summary.get("accounting") or {}).get("settled_usd"),
            "isolation_ready": bool((summary.get("isolation") or {}).get("pre_dispatch_ready")
                                    and (summary.get("isolation") or {}).get("post_dispatch_ready")),
            "read_audit_passed": summary.get("read_audit_passed"),
            "problems": summary.get("problems") or [],
        })
    return records


def attempt_records(bundle, extra) -> list:
    """Every attempt, measured or not, by position and ordinal rather than by ID."""
    attempts = list(extra)
    for position in range(1, PLANNED_PILOT_CELLS + 1):
        summary_path = Path(bundle) / "cells" / ("position-%02d" % position) / "summary.json"
        if not summary_path.is_file():
            continue
        summary = load(summary_path)
        attempts.append({
            "position": position, "ordinal": summary.get("attempt_ordinal", 1),
            "validity": "valid" if not summary.get("problems") else "questioned",
            "disposition": summary.get("disposition"),
            "settled_usd": (summary.get("accounting") or {}).get("settled_usd"),
            "reconciliation_residual_usd":
                (summary.get("accounting") or {}).get("reconciliation_residual_usd"),
        })
    return attempts


def decide(cells, ledger, remaining) -> tuple:
    """The pilot's disposition, and every reason it is not ``continue``."""
    blockers = []
    valid = [cell for cell in cells if cell.get("valid_completed")]
    if len(valid) < PLANNED_PILOT_CELLS:
        blockers.append("%d of %d planned pilot cells reached a valid completed dispatch"
                        % (len(valid), PLANNED_PILOT_CELLS))
    for cell in cells:
        if cell.get("problems"):
            blockers.append("position %d carries %d unresolved problem(s)"
                            % (cell["position"], len(cell["problems"])))
        if cell.get("disposition") not in (None, "dispatched", "unattempted"):
            blockers.append("position %d stopped as %s" % (cell["position"], cell["disposition"]))
        if cell.get("isolation_ready") is False:
            blockers.append("position %d has an isolation check that did not pass" % cell["position"])
        if cell.get("read_audit_passed") is False:
            blockers.append("position %d has a read outside its permitted roots" % cell["position"])
    if remaining <= 0:
        blockers.append("no allowance remains under the frozen cap after the protected reserve")
    if not blockers:
        return "continue", blockers
    if any("allowance" in reason for reason in blockers):
        return "stopped-budget", blockers
    return "stopped-incomplete", blockers


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config")
    parser.add_argument("--bundle")
    parser.add_argument("--seal")
    parser.add_argument("--out")
    parser.add_argument("--extra-attempts",
                        help="JSON list of attempts with no summary, such as an aborted launch")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.config or not args.bundle or not args.out:
        parser.error("--config, --bundle and --out are required")

    config = load(args.config)
    ledger = load(config["ledger"])
    cells = cell_records(args.bundle)
    extra = load(args.extra_attempts, []) if args.extra_attempts else []
    seal = load(args.seal, {}) if args.seal else {}

    cap = usd(ledger["frozen_total_cap_usd"])
    protected = usd(ledger["grading_closeout_reserve_usd"])
    occupied = usd(ledger["actual_usd"]) + usd(ledger["reserved_usd"]) + usd(ledger["uncertainty_usd"])
    remaining = cap - protected - occupied
    disposition, blockers = decide(cells, ledger, remaining)

    document = {
        "schema_version": "bounded-discovery-v1",
        "artifact_id": "issue-150-pilot-handoff",
        "stage": "pilot",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "disposition": disposition,
        "blockers": blockers,
        "available_claims": [],
        "claims_note": "No quality, recall or cost comparison is reported here. The pilot's "
                       "outcomes stay sealed until every reviewer run has stopped, and no arm "
                       "may be described as better or worse on this evidence.",
        "planned_pilot_cells": PLANNED_PILOT_CELLS,
        "cells": cells,
        "attempts": attempt_records(args.bundle, extra),
        "accounting": {
            "frozen_total_cap_usd": str(cap),
            "grading_closeout_reserve_usd": str(protected),
            "actual_usd": ledger["actual_usd"],
            "reserved_usd": ledger["reserved_usd"],
            "uncertainty_usd": ledger["uncertainty_usd"],
            "remaining_under_cap_usd": str(remaining),
        },
        "sealed_evidence": seal,
        "next_stage": {
            "tickets": [151, 152],
            "work": "#151 runs the eighteen grid cells under the same frozen rules and the same "
                    "container isolation deviation, appending to the same ledger chain, which "
                    "now lives in evaluator storage because its attempt IDs name slots. #152 "
                    "adjudicates and scores once every reviewer run has stopped. Neither may "
                    "read the sealed pilot outcomes before then.",
        },
    }
    Path(args.out).write_text(json.dumps(document, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")
    print("%s: %s" % (disposition, "; ".join(blockers) if blockers else "six valid completed cells"))
    return 0


def self_test():
    checks = []
    complete = [{"position": n, "valid_completed": True, "disposition": "dispatched",
                 "isolation_ready": True, "read_audit_passed": True, "problems": []}
                for n in range(1, 7)]
    disposition, blockers = decide(complete, {}, Decimal("50"))
    checks.append(("six valid completed cells continue",
                   disposition == "continue" and not blockers))
    short = complete[:5]
    disposition, blockers = decide(short, {}, Decimal("50"))
    checks.append(("a missing cell stops the pilot", disposition == "stopped-incomplete"))
    broke = [dict(cell) for cell in complete]
    broke[2]["problems"] = ["a fidelity failure"]
    broke[2]["valid_completed"] = False
    disposition, blockers = decide(broke, {}, Decimal("50"))
    checks.append(("an unresolved problem stops the pilot",
                   disposition == "stopped-incomplete"
                   and any("unresolved" in reason for reason in blockers)))
    disposition, blockers = decide(complete, {}, Decimal("0"))
    checks.append(("an exhausted allowance is a budget stop",
                   disposition == "stopped-budget"))
    leaked = [dict(cell) for cell in complete]
    leaked[0]["read_audit_passed"] = False
    leaked[0]["valid_completed"] = False
    disposition, blockers = decide(leaked, {}, Decimal("50"))
    checks.append(("a read outside the permitted roots stops the pilot",
                   disposition == "stopped-incomplete"
                   and any("outside its permitted roots" in reason for reason in blockers)))
    isolation = [dict(cell) for cell in complete]
    isolation[4]["isolation_ready"] = False
    isolation[4]["valid_completed"] = False
    disposition, blockers = decide(isolation, {}, Decimal("50"))
    checks.append(("a failed isolation check stops the pilot",
                   any("isolation check" in reason for reason in blockers)))
    for name, passed in checks:
        print("%s %s" % ("ok  " if passed else "FAIL", name))
    return 0 if all(passed for _, passed in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
