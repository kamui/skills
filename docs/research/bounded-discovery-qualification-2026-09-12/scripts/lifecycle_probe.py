#!/usr/bin/env python3
"""Drive the pinned ledger's attempt lifecycle and assert that a refusal starts no worker.

#199 gap 3: in the pilot all sixteen attempt-open and attempt-close events were written in
one 27 ms window half an hour after the last settlement, so the 27-attempt cap and the
replacement rule gated nothing. The synthetic tests already show ``budget.py`` refusing
each violation. What they cannot show is the thing the gap is about: that the refusal
happens **before** a worker exists.

So this driver does what a coordinator does. For every claim it attempts, it calls the
pinned ``budget.py`` ``attempt_event`` first and only launches a worker if the claim
returned. The "worker" is a real subprocess that writes a marker file, so the absence of a
started worker is asserted from the filesystem rather than from the driver's own control
flow. Every claim, its outcome and the marker's presence are written to the report.

Usage::

    python3 scripts/lifecycle_probe.py --ledger FILE --markers DIR --out FILE
        [--budget-script FILE]
    python3 scripts/lifecycle_probe.py --self-test

Input: a DESIGN.md ``BudgetEvent`` ledger opened for this probe, with ``attempt_limit`` 5
and ``replacement_limit`` 2 so every cap and every eligibility rule is reachable.

Exit: 0 when every expected refusal was refused and no refused claim started a worker,
1 when any claim came out other than expected with one line per violation on stdout,
2 when an input cannot be read.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_BUDGET = (Path(__file__).resolve().parents[2] /
                  "bounded-discovery-readiness-2026-09-12" / "scripts" / "budget.py")


def load_budget(path: Path):
    spec = importlib.util.spec_from_file_location("pinned_budget", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def claim(budget, ledger, markers, report, label, config, close=None, expect="refused"):
    """Claim, then launch a worker only if the claim returned. Record both facts."""
    marker = markers / (label + ".marker")
    outcome, reason = "admitted", None
    try:
        budget.attempt_event(str(ledger), config, close=close)
    except budget.Violation as violation:
        outcome, reason = "refused", str(violation)
    except (KeyError, ValueError) as error:
        # A malformed ledger is an unreadable input, not a refusal; calling it one would
        # record a rule as having fired when nothing did.
        raise OSError("the ledger could not be claimed against: " + str(error)) from error
    if outcome == "admitted":
        subprocess.run([sys.executable, "-c",
                        "import sys, pathlib; pathlib.Path(sys.argv[1]).write_text('started', "
                        "encoding='utf-8')", str(marker)],
                       text=True, encoding="utf-8", check=True)
    report.append({
        "claim": label,
        "attempt_id": config["attempt_id"],
        "expected": expect,
        "outcome": outcome,
        "refusal": reason,
        "worker_started": marker.exists(),
        "observed_at": datetime.now(timezone.utc).isoformat(),
    })
    return outcome


def run(ledger: Path, markers: Path, out: Path, budget_script: Path):
    budget = load_budget(budget_script)
    markers.mkdir(parents=True, exist_ok=True)
    report: list = []

    def config(attempt, cell, contexts, predecessor=None, ordinal=0, evidence=None):
        body = {"attempt_id": attempt, "cell_id": cell, "contexts": dict(contexts),
                "predecessor": predecessor, "replacement_ordinal": ordinal}
        if evidence:
            body["replacement_evidence"] = evidence
        return body

    def attempt(label, expect, *args, **kwargs):
        close = kwargs.pop("close", None)
        claim(budget, ledger, markers, report, label, config(*args, **kwargs),
              close=close, expect=expect)

    attempt("01-first-open", "admitted", "A", "cell-1", {"primary": "ctx-A1"})
    attempt("02-duplicate-attempt-id", "refused", "A", "cell-9", {"primary": "ctx-X"})
    attempt("03-reused-context", "refused", "B", "cell-2", {"primary": "ctx-A1"})
    attempt("04-second-open", "admitted", "B", "cell-2", {"primary": "ctx-B1"})
    attempt("05-third-open-while-two-live", "refused", "C", "cell-3", {"primary": "ctx-C1"})
    attempt("06-close-A-stopped-invalid", "admitted", "A", "cell-1", {"primary": "ctx-A1"},
            close="stopped-invalid")
    attempt("07-replacement-without-evidence", "refused", "D", "cell-1", {"primary": "ctx-D1"},
            predecessor="A", ordinal=1)
    attempt("08-replacement-wrong-ordinal", "refused", "D", "cell-1", {"primary": "ctx-D1"},
            predecessor="A", ordinal=2, evidence="probes/P19-lifecycle-enforcement")
    attempt("09-replacement-admitted", "admitted", "D", "cell-1", {"primary": "ctx-D1"},
            predecessor="A", ordinal=1, evidence="probes/P19-lifecycle-enforcement")
    attempt("10-close-B-complete", "admitted", "B", "cell-2", {"primary": "ctx-B1"},
            close="complete")
    attempt("11-replacement-of-a-valid-attempt", "refused", "E", "cell-2", {"primary": "ctx-E1"},
            predecessor="B", ordinal=1, evidence="probes/P19-lifecycle-enforcement")
    attempt("12-close-D-stopped-invalid", "admitted", "D", "cell-1", {"primary": "ctx-D1"},
            close="stopped-invalid")
    attempt("13-second-replacement-admitted", "admitted", "F", "cell-1", {"primary": "ctx-F1"},
            predecessor="D", ordinal=2, evidence="probes/P19-lifecycle-enforcement")
    attempt("14-close-F-stopped-invalid", "admitted", "F", "cell-1", {"primary": "ctx-F1"},
            close="stopped-invalid")
    attempt("15-replacement-cap", "refused", "G", "cell-1", {"primary": "ctx-G1"},
            predecessor="F", ordinal=3, evidence="probes/P19-lifecycle-enforcement")
    attempt("16-fifth-attempt", "admitted", "H", "cell-4", {"primary": "ctx-H1"})
    attempt("17-attempt-cap", "refused", "I", "cell-5", {"primary": "ctx-I1"})

    violations = []
    for row in report:
        if row["outcome"] != row["expected"]:
            violations.append(row["claim"] + " expected " + row["expected"] +
                              " but was " + row["outcome"])
        if row["outcome"] == "refused" and row["worker_started"]:
            violations.append(row["claim"] + " was refused and a worker started anyway")
    data = json.loads(ledger.read_text(encoding="utf-8"))
    lifecycle = [e for e in data["events"]
                 if e["operation"] in ("attempt-open", "attempt-close")]
    body = {
        "probe": "P19",
        "rule": ("every claim goes through the ledger before a worker exists; a refusal is "
                 "enforcement only if no worker started, which is asserted from the marker "
                 "files rather than from this driver's control flow."),
        "budget_script": str(budget_script),
        "ledger": str(ledger),
        "claims": report,
        "lifecycle_events_written": len(lifecycle),
        "lifecycle_event_timestamps": [e["observed_at"] for e in lifecycle],
        "workers_started": sorted(p.name for p in markers.iterdir()),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    out.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    for violation in violations:
        print(violation)
    if not violations:
        print("lifecycle: " + str(len(report)) + " claims, " +
              str(sum(r["outcome"] == "refused" for r in report)) + " refused before any worker, " +
              str(len(lifecycle)) + " events written when they happened")
    return 1 if violations else 0


def new_ledger(path: Path):
    path.write_text(json.dumps({
        "schema_version": "bounded-discovery-v1", "experiment_id": "issue-207-P19-lifecycle",
        "owner": "kamui", "currency": "USD", "total_ceiling_usd": "1.00",
        "pre_freeze_ceiling_usd": "1.00", "frozen_total_cap_usd": None,
        "grading_closeout_reserve_usd": None, "actual_usd": "0", "reserved_usd": "0",
        "uncertainty_usd": "0", "pre_freeze_actual_usd": "0", "pre_freeze_reserved_usd": "0",
        "planned_cells": 5, "attempts_dispatched": 0, "replacement_limit": 2,
        "attempt_limit": 5,
        "events": [{
            "event_id": "P19-0001", "previous_event_id": None,
            "observed_at": datetime.now(timezone.utc).isoformat(), "ticket": 207,
            "actor": "kamui", "phase": "pre-freeze", "operation": "open", "attempt_id": None,
            "helper_id": None, "request_refs": [], "reservation_id": None,
            "actual_delta_usd": "0", "reservation_delta_usd": "0", "uncertainty_usd": "0",
            "rate_usage_evidence": [],
            "reason": ("A probe ledger for P19 only, with attempt_limit 5 and replacement_limit 2 "
                       "so every cap and every eligibility rule is reachable in one battery. "
                       "It carries no study money and is never settled against."),
        }],
    }, indent=2) + "\n", encoding="utf-8")


def self_test():
    import tempfile
    failures = []
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        ledger = base / "ledger.json"
        new_ledger(ledger)
        code = run(ledger, base / "markers", base / "report.json", DEFAULT_BUDGET)
        if code != 0:
            failures.append("the lifecycle battery did not come out as expected")
        report = json.loads((base / "report.json").read_text(encoding="utf-8"))
        refused = [r for r in report["claims"] if r["outcome"] == "refused"]
        if len(refused) != 8:
            failures.append("expected eight refusals, got " + str(len(refused)))
        if any(r["worker_started"] for r in refused):
            failures.append("a refused claim started a worker")
        if report["lifecycle_events_written"] != 9:
            failures.append("expected nine lifecycle events, got " +
                            str(report["lifecycle_events_written"]))
    for failure in failures:
        print("FAIL", failure)
    print(("FAILED " + str(len(failures))) if failures else "ok: 4 checks")
    return 1 if failures else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--markers", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--budget-script", type=Path, default=DEFAULT_BUDGET)
    parser.add_argument("--create-ledger", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        if not args.ledger or not args.markers or not args.out:
            print("--ledger, --markers and --out are required")
            return 1
        if args.create_ledger:
            new_ledger(args.ledger)
        return run(args.ledger, args.markers, args.out, args.budget_script)
    except OSError as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
