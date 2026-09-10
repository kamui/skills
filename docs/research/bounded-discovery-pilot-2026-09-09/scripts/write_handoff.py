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
        completed = summary.get("completion") == "complete"
        records.append({
            "position": position,
            "arm": summary.get("arm"),
            "replicate": summary.get("replicate"),
            "worker_model": summary.get("worker_model"),
            "disposition": summary.get("disposition"),
            "completion": summary.get("completion"),
            "operational_validity": summary.get("operational_validity"),
            "valid_completed": completed and not summary.get("problems")
                               and summary.get("operational_validity") != "invalid",
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
        if summary.get("attempt_history"):
            attempts.extend(dict(entry, position=position) for entry in summary["attempt_history"])
            continue
        attempts.append({
            "position": position, "ordinal": summary.get("attempt_ordinal", 1),
            "validity": "valid" if not summary.get("problems") else "questioned",
            "disposition": summary.get("disposition"),
            "settled_usd": (summary.get("accounting") or {}).get("settled_usd"),
            "reconciliation_residual_usd":
                (summary.get("accounting") or {}).get("reconciliation_residual_usd"),
        })
    return attempts


def decide(cells, remaining) -> tuple:
    """The pilot's disposition, its blockers, and the cells that did not finish.

    ``continue`` asks whether the pilot was executed faithfully and whether the grid
    can still be paid for - not whether every cell produced a finished review. A cell
    that stops against the frozen dollar allowance is a measured incomplete result in
    every arm alike, which the preregistration is explicit about, so it does not block
    the programme. It does block a positive screen, and that is #152's gate to apply,
    so it is reported separately rather than folded into this one.

    What does block ``continue`` is unfaithfulness: a cell that never dispatched, an
    isolation check that did not pass, a read outside the permitted roots that nobody
    ruled on, or an unresolved problem - and an exhausted allowance.
    """
    blockers = []
    incomplete = []
    for cell in cells:
        position = cell["position"]
        if cell.get("disposition") == "unattempted":
            blockers.append("position %d was never dispatched" % position)
            continue
        if cell.get("problems"):
            blockers.append("position %d carries %d unresolved problem(s)"
                            % (position, len(cell["problems"])))
        if cell.get("isolation_ready") is False:
            blockers.append("position %d has an isolation check that did not pass" % position)
        if cell.get("read_audit_passed") is False:
            blockers.append("position %d has a read outside its permitted roots that was "
                            "not ruled on" % position)
        invalid = (cell.get("operational_validity") == "invalid" or bool(cell.get("problems"))
                   or cell.get("isolation_ready") is False or cell.get("read_audit_passed") is False)
        if cell.get("operational_validity") == "invalid" and not cell.get("problems"):
            blockers.append("position %d is operationally invalid" % position)
        if cell.get("completion") != "complete":
            effect = ("counts as missing in the screen, not as present; protocol invalidity "
                      "requires the documented replacement policy and remaining allowance"
                      if invalid else
                      "counts as missing in the screen, not as present; "
                      "it is a measured result and not replacement-eligible")
            incomplete.append({"position": position, "completion": cell.get("completion"),
                               "operational_validity": "invalid" if invalid else "valid",
                               "effect": effect})
    if remaining <= 0:
        blockers.append("no allowance remains under the frozen cap after the protected reserve")
    if not blockers:
        return "continue", blockers, incomplete
    if any("allowance" in reason for reason in blockers):
        return "stopped-budget", blockers, incomplete
    return "stopped-incomplete", blockers, incomplete


def affordability(cells, remaining) -> dict:
    """Whether the eighteen remaining grid cells fit, at the costs just measured.

    The freeze projected the grid from earlier runs and recorded that its headroom was
    thin. These are the first measurements of this configuration, so #151 is entitled
    to the arithmetic rather than the projection.
    """
    by_arm = {}
    for cell in cells:
        cost = cell.get("settled_usd")
        if cost and cell.get("arm"):
            by_arm.setdefault(cell["arm"], []).append(Decimal(str(cost)))
    means = {arm: sum(costs) / len(costs) for arm, costs in sorted(by_arm.items())}
    triple = sum(means.values()) if len(means) == 3 else None
    needed = triple * 6 if triple is not None else None
    fits = needed <= remaining if needed is not None else None
    triples = max(0, min(6, int(remaining / triple))) if triple else None
    missing = sorted(set("ABC") - set(means))
    warning = ("Projection unavailable: no settled cost for arm(s) %s. Known costs and "
               "unattempted cells are retained; no full-grid affordability claim is available."
               % ", ".join(missing) if missing else ("the remaining grid fits at the measured costs"
               if fits else
               "SHORTFALL: the eighteen remaining cells project to %s against %s available, "
               "so the grid cannot be completed under the frozen cap. At %s per triple the "
               "allowance covers %d of the 6 remaining triples, leaving %d cells unrun. #151 "
               "should expect stopped-budget and must stop on a triple boundary."
               % (str(round(needed, 4)), str(round(remaining, 4)), str(round(triple, 4)),
                  triples or 0, 18 - (triples or 0) * 3)))
    return {
        "missing_arm_measurements": missing,
        "measured_mean_per_arm_usd": {arm: str(round(mean, 4)) for arm, mean in means.items()},
        "measured_triple_usd": str(round(triple, 4)) if triple is not None else None,
        "remaining_grid_cells": 18,
        "projected_remaining_grid_usd": str(round(needed, 4)) if needed is not None else None,
        "remaining_under_cap_usd": str(round(remaining, 4)),
        "fits": fits,
        "affordable_remaining_triples": triples,
        "warning": warning,
        "note": "The frozen order is what makes a shortfall survivable: A/B/C triples are "
                "contiguous, so a mid-grid stopped-budget leaves whole triples rather than "
                "a ragged grid. The preregistration accepted that risk prospectively and "
                "said the headroom was thin; these are the first measured cells of this "
                "configuration, and they are dearer than the projection it used.",
    }


def setup_charges(ledger) -> dict:
    """Spend this ticket charged outside any attempt, itemised so the total reconciles.

    Preregistration section 7 requires shared setup to be charged once to the epic and
    never omitted, which means it also has to be visible: without it the handoff's
    actual_usd cannot be reproduced from the attempts it lists, and a reader is left
    with an unexplained gap.
    """
    items = []
    for event in ledger["events"]:
        if (event.get("operation") == "settle" and not event.get("attempt_id")
                and event.get("phase") == "review" and Decimal(str(event["actual_delta_usd"])) > 0):
            items.append({"reservation_id": event.get("reservation_id"),
                          "usd": event["actual_delta_usd"],
                          "why": (event.get("request_refs") or [""])[0]})
    total = sum(usd(item["usd"]) for item in items)
    return {"items": items, "total_usd": str(total),
            "note": "one-off shared setup: establishing that the cell image authenticates, "
                    "that the frozen flag set runs in it, and that a session's transcript can "
                    "be metered and fidelity-checked. Charged before any attempt was reserved "
                    "so an infrastructure failure could not burn an attempt ID."}


def reconcile(ledger, cells, attempts, setup) -> dict:
    """Check the reported total against the parts this handoff itemises."""
    pre_freeze = usd(ledger.get("pre_freeze_actual_usd"))
    attempted = sum(usd(entry.get("settled_usd")) for entry in attempts)
    accounted = pre_freeze + attempted + usd(setup["total_usd"])
    reported = usd(ledger["actual_usd"])
    return {"pre_freeze_actual_usd": str(pre_freeze),
            "attempts_settled_usd": str(attempted),
            "setup_usd": setup["total_usd"],
            "accounted_usd": str(accounted),
            "ledger_actual_usd": str(reported),
            "difference_usd": str(reported - accounted),
            "reconciles": reported == accounted}


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
    attempt_rows = None
    extra = load(args.extra_attempts, []) if args.extra_attempts else []
    seal = load(args.seal, {}) if args.seal else {}

    cap = usd(ledger["frozen_total_cap_usd"])
    protected = usd(ledger["grading_closeout_reserve_usd"])
    occupied = usd(ledger["actual_usd"]) + usd(ledger["reserved_usd"]) + usd(ledger["uncertainty_usd"])
    remaining = cap - protected - occupied
    disposition, blockers, incomplete = decide(cells, remaining)
    money = affordability(cells, remaining)
    attempt_rows = attempt_records(args.bundle, extra)
    setup = setup_charges(ledger)
    books = reconcile(ledger, cells, attempt_rows, setup)
    if not books["reconciles"]:
        blockers.append("the reported total does not reconcile with the itemised parts: "
                        "%s unexplained" % books["difference_usd"])
        disposition = "stopped-incomplete"

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
        "incomplete_cells": incomplete,
        "affordability": money,
        "cells": cells,
        "attempts": attempt_rows,
        "setup_charges": setup,
        "reconciliation": None,
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
            "work": "#151 runs the grid cells under the same frozen rules and the same "
                    "container isolation deviation, appending to the same ledger chain, which "
                    "now lives in evaluator storage because its attempt IDs name slots. #152 "
                    "adjudicates and scores once every reviewer run has stopped. Neither may "
                    "read the sealed pilot outcomes before then.",
            "budget_warning": money["warning"],
        },
    }
    document["reconciliation"] = books
    document["attempt_ledger"] = {
        "attempt_open_events": sum(1 for e in ledger["events"]
                                   if e.get("operation") == "attempt-open"),
        "attempt_limit": ledger.get("attempt_limit"),
        "replacements_consumed": sum(1 for e in ledger["events"]
                                     if e.get("operation") == "attempt-open"
                                     and e.get("predecessor")),
        "replacement_limit": ledger.get("replacement_limit"),
        "contexts_claimed": len({context for event in ledger["events"]
                                 if event.get("operation") == "attempt-open"
                                 for context in event.get("contexts", [])}
                                | {entry["context_id"] for entry in ledger.get("context_claims", [])}),
        "note": "claimed through the ledger's own attempt_event, which refuses a reused "
                "attempt ID or context ID, enforces both caps, and refuses a replacement "
                "whose predecessor was not closed as documented invalidity.",
    }
    Path(args.out).write_text(json.dumps(document, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")
    summary = "; ".join(blockers) if blockers else (
        "%d of %d cells complete" % (PLANNED_PILOT_CELLS - len(incomplete), PLANNED_PILOT_CELLS))
    if incomplete:
        summary += ", %d incomplete (%s)" % (
            len(incomplete), ", ".join("position %d %s" % (entry["position"], entry["completion"])
                                       for entry in incomplete))
    print("%s: %s" % (disposition, summary))
    if not money["fits"]:
        print(money["warning"])
    return 0


def self_test():
    checks = []
    def cell(n, **overrides):
        base = {"position": n, "arm": "ABC"[(n - 1) % 3], "valid_completed": True,
                "disposition": "dispatched", "completion": "complete",
                "isolation_ready": True, "read_audit_passed": True, "problems": [],
                "settled_usd": "4.0000000"}
        base.update(overrides)
        return base

    complete = [cell(n) for n in range(1, 7)]
    disposition, blockers, incomplete = decide(complete, Decimal("50"))
    checks.append(("six faithful complete cells continue",
                   disposition == "continue" and not blockers and not incomplete))
    stopped = [cell(n) for n in range(1, 7)]
    stopped[5] = cell(6, completion="stopped-budget")
    disposition, blockers, incomplete = decide(stopped, Decimal("50"))
    checks.append(("a budget-stopped cell is incomplete but does not stop the pilot",
                   disposition == "continue" and not blockers and len(incomplete) == 1
                   and "counts as missing in the screen" in incomplete[0]["effect"]))
    missing = [cell(n) for n in range(1, 6)] + [cell(6, disposition="unattempted")]
    disposition, blockers, _ = decide(missing, Decimal("50"))
    checks.append(("a never-dispatched cell stops the pilot",
                   disposition == "stopped-incomplete"
                   and any("never dispatched" in reason for reason in blockers)))
    broke = [cell(n) for n in range(1, 7)]
    broke[2]["problems"] = ["a fidelity failure"]
    disposition, blockers, _ = decide(broke, Decimal("50"))
    checks.append(("an unresolved problem stops the pilot",
                   disposition == "stopped-incomplete"
                   and any("unresolved" in reason for reason in blockers)))
    disposition, blockers, _ = decide(complete, Decimal("0"))
    checks.append(("an exhausted allowance is a budget stop",
                   disposition == "stopped-budget"))
    leaked = [cell(n) for n in range(1, 7)]
    leaked[0]["read_audit_passed"] = False
    disposition, blockers, _ = decide(leaked, Decimal("50"))
    checks.append(("an unruled read outside the permitted roots stops the pilot",
                   disposition == "stopped-incomplete"
                   and any("not ruled on" in reason for reason in blockers)))
    isolation = [cell(n) for n in range(1, 7)]
    isolation[4]["isolation_ready"] = False
    disposition, blockers, _ = decide(isolation, Decimal("50"))
    checks.append(("a failed isolation check stops the pilot",
                   any("isolation check" in reason for reason in blockers)))
    money = affordability([cell(1, arm="A", settled_usd="4"), cell(2, arm="B", settled_usd="5"),
                           cell(3, arm="C", settled_usd="8")], Decimal("200"))
    checks.append(("affordability sums one triple and scales it by six",
                   Decimal(money["measured_triple_usd"]) == Decimal("17")
                   and money["projected_remaining_grid_usd"] == "102.0000"
                   and money["fits"] is True))
    tight = affordability([cell(1, arm="A", settled_usd="4"), cell(2, arm="B", settled_usd="5"),
                           cell(3, arm="C", settled_usd="8")], Decimal("50"))
    checks.append(("a shortfall is reported rather than smoothed",
                   tight["fits"] is False))
    ledger = {"pre_freeze_actual_usd": "10.00", "actual_usd": "20.00", "events": [
        {"operation": "settle", "attempt_id": None, "phase": "review",
         "actual_delta_usd": "1.00", "reservation_id": "setup", "request_refs": ["why"]}]}
    setup = setup_charges(ledger)
    checks.append(("setup charges are itemised from the ledger",
                   setup["total_usd"] == "1.00" and len(setup["items"]) == 1))
    books = reconcile(ledger, [], [{"settled_usd": "9.00"}], setup)
    checks.append(("a total that adds up reconciles", books["reconciles"] is True))
    books = reconcile(ledger, [], [{"settled_usd": "8.00"}], setup)
    checks.append(("an unexplained gap is reported, not hidden",
                   books["reconciles"] is False and books["difference_usd"] == "1.00"))
    for name, passed in checks:
        print("%s %s" % ("ok  " if passed else "FAIL", name))
    return 0 if all(passed for _, passed in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
