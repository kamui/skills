#!/usr/bin/env python3
"""Score the frozen #138 grid and apply its prospective screen, mechanically.

This is the scoring the preregistration freezes before any reviewer runs. It
consumes explicit adjudicated fields only — the target's status and defect IDs,
and each attempt's validity, completion, published status, clean claim, recovered
and sufficiently-fixed defect IDs, false-finding counts and billed cost — and it
never infers materiality, recovery or a clean verdict from prose. Every judgment
stays with #152's independent adjudication; this script does the arithmetic and
applies the frozen thresholds to it.

The definitions are the committed method's (``docs/research/code-review-one-shot-method.md``
section 4). Two of them are worth restating because they decide the screen:

* **False clean** is a property of the published status alone. An attempt on an
  adjudicated buggy target that explicitly returns Approved / clean / no material
  defects is false clean even when it also recovered the defect, reported it as a
  ``consider``, or declared operational incompleteness. Recovery credit never
  cancels it — the fixture set carries exactly that case.
* **Macro material recall** is the equal-weight mean over buggy targets of the
  arm's mean per-attempt recall on that target. It is computed twice: over every
  dispatched attempt, and over valid completed attempts only. A buggy target with
  no attempts in a view leaves that macro unavailable rather than counting zero.

Usage::

    python3 scripts/score_attempts.py --input grid.json [--json] [--out FILE]
    python3 scripts/score_attempts.py --self-test

Input schema (UTF-8 JSON)::

    {"experiment_id": str, "truth_version": str, "control_arm": "A",
     "candidate_arms": ["B", "C"],
     "thresholds": {"relative_recall_gain": 0.20, "zero_baseline_absolute_gain": 0.10,
                    "matched_cost_ratio": 1.25},
     "targets": {"<slot>": {"status": "buggy"|"clean", "defect_ids": [str, ...],
                            "truth_version": str}},
     "attempts": [{"attempt_id": str, "cell_id": str, "target_slot": str, "arm": str,
                   "replicate": int, "valid": bool, "completed": bool, "status": str,
                   "clean_claim": bool, "recovered_defect_ids": [str, ...],
                   "sufficient_fix_defect_ids": [str, ...], "raw_false_finding_items": int,
                   "unique_false_claims": int, "action_errors": int, "priority_errors": int,
                   "unresolved_adjudications": int, "billed_cost_usd": str}],
     "planned_cells": [str, ...]}

Output: a scorecard as Markdown blocks, or JSON with ``--json``. The screen for
each candidate arm reports ``pass``, ``fail`` or ``inconclusive`` with the reason
for every criterion; unresolved truth, a missing planned cell or a changed
clean/buggy mix forces ``inconclusive`` however the numbers fall.

Exit: 0 when the input scores, 1 on a content violation (unknown defect ID,
unknown arm, attempt on an unknown target, duplicate attempt ID) with one line
per violation on stdout, 2 when the input cannot be read or parsed.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from decimal import Decimal
from pathlib import Path

DEFAULT_THRESHOLDS = {"relative_recall_gain": 0.20, "zero_baseline_absolute_gain": 0.10,
                      "matched_cost_ratio": 1.25}


class Violation(ValueError):
    pass


def validate(document):
    violations = []
    targets = document["targets"]
    seen = set()
    for attempt in document["attempts"]:
        aid = attempt["attempt_id"]
        if aid in seen:
            violations.append("duplicate attempt_id " + aid)
        seen.add(aid)
        slot = attempt["target_slot"]
        if slot not in targets:
            violations.append("attempt %s names unknown target %s" % (aid, slot))
            continue
        known = set(targets[slot]["defect_ids"])
        for field in ("recovered_defect_ids", "sufficient_fix_defect_ids"):
            unknown = sorted(set(attempt.get(field, [])) - known)
            for defect in unknown:
                violations.append("attempt %s claims %s not in %s's register: %s" % (aid, field, slot, defect))
        extra = sorted(set(attempt.get("sufficient_fix_defect_ids", [])) -
                       set(attempt.get("recovered_defect_ids", [])))
        for defect in extra:
            violations.append("attempt %s credits a sufficient fix for unrecovered %s" % (aid, defect))
        if attempt["arm"] not in [document["control_arm"]] + list(document["candidate_arms"]):
            violations.append("attempt %s names unknown arm %s" % (aid, attempt["arm"]))
    for slot, target in targets.items():
        if target["status"] not in ("buggy", "clean"):
            violations.append("target %s has status %r" % (slot, target["status"]))
        if (target["status"] == "clean") != (not target["defect_ids"]):
            violations.append("target %s's status and defect register disagree" % slot)
    if violations:
        raise Violation("\n".join(violations))


def recall(attempt, targets):
    """Per-attempt recall; None on a clean target, where recall is not defined."""
    defects = targets[attempt["target_slot"]]["defect_ids"]
    if not defects:
        return None
    return len(set(attempt["recovered_defect_ids"]) & set(defects)) / len(defects)


def macro(attempts, targets, buggy_slots):
    """Equal-weight mean over buggy targets of the mean per-attempt recall."""
    per_target = {}
    for slot in buggy_slots:
        values = [recall(a, targets) for a in attempts if a["target_slot"] == slot]
        per_target[slot] = statistics.mean(values) if values else None
    if not per_target or any(value is None for value in per_target.values()):
        return None, per_target
    return statistics.mean(per_target.values()), per_target


def arm_scorecard(document, arm):
    targets = document["targets"]
    buggy = sorted(slot for slot, t in targets.items() if t["status"] == "buggy")
    attempts = [a for a in document["attempts"] if a["arm"] == arm]
    completed = [a for a in attempts if a["valid"] and a["completed"]]
    on_buggy = [a for a in attempts if targets[a["target_slot"]]["status"] == "buggy"]
    on_buggy_completed = [a for a in completed if targets[a["target_slot"]]["status"] == "buggy"]
    macro_all, per_target_all = macro(attempts, targets, buggy)
    macro_done, per_target_done = macro(completed, targets, buggy)
    false_clean = [a for a in on_buggy if a["clean_claim"]]
    false_clean_done = [a for a in on_buggy_completed if a["clean_claim"]]
    recovered = sum(len(set(a["recovered_defect_ids"])) for a in attempts)
    sufficient = sum(len(set(a["sufficient_fix_defect_ids"])) for a in attempts)
    denominator = sum(len(targets[a["target_slot"]]["defect_ids"]) for a in on_buggy)
    cells = {}
    for attempt in attempts:
        cells.setdefault(attempt["cell_id"], Decimal(0))
        cells[attempt["cell_id"]] += Decimal(str(attempt["billed_cost_usd"]))
    return {
        "arm": arm,
        "attempts": len(attempts),
        "valid_completed": len(completed),
        "completion_rate": (len(completed) / len(attempts)) if attempts else None,
        "macro_material_recall_all_attempts": macro_all,
        "macro_material_recall_completed_only": macro_done,
        "per_target_recall_all_attempts": per_target_all,
        "per_target_recall_completed_only": per_target_done,
        "false_clean_count": len(false_clean),
        "false_clean_rate": (len(false_clean) / len(on_buggy)) if on_buggy else None,
        "false_clean_count_completed_only": len(false_clean_done),
        "false_clean_rate_completed_only": (len(false_clean_done) / len(on_buggy_completed))
                                           if on_buggy_completed else None,
        "false_clean_attempt_ids": [a["attempt_id"] for a in false_clean],
        "zero_recovery_not_claiming_clean": len([a for a in on_buggy
                                                 if not a["recovered_defect_ids"] and not a["clean_claim"]]),
        "raw_false_finding_items": sum(a["raw_false_finding_items"] for a in attempts),
        "raw_false_finding_items_invalid_subtotal": sum(a["raw_false_finding_items"] for a in attempts
                                                        if not (a["valid"] and a["completed"])),
        "unique_false_claims": sum(a["unique_false_claims"] for a in attempts),
        "action_errors": sum(a.get("action_errors", 0) for a in attempts),
        "priority_errors": sum(a.get("priority_errors", 0) for a in attempts),
        "unresolved_adjudications": sum(a.get("unresolved_adjudications", 0) for a in attempts),
        "recovered_total": recovered,
        "sufficient_total": sufficient,
        "aggregate_fix_sufficiency": (sufficient / recovered) if recovered else None,
        "sufficient_outcome_recall": (sufficient / denominator) if denominator else None,
        "billed_cost_by_cell": {cell: str(cost) for cell, cost in sorted(cells.items())},
        "billed_cost_total": str(sum(cells.values(), Decimal(0))),
    }


def matched_cost_ratio(document, candidate, control):
    """Median of candidate/control billed cost over cells matched by target and replicate."""
    def by_pair(arm):
        pairs = {}
        for attempt in document["attempts"]:
            if attempt["arm"] != arm:
                continue
            key = (attempt["target_slot"], attempt["replicate"])
            pairs[key] = pairs.get(key, Decimal(0)) + Decimal(str(attempt["billed_cost_usd"]))
        return pairs
    left, right = by_pair(candidate), by_pair(control)
    ratios, unavailable = [], []
    for key in sorted(set(left) & set(right)):
        if right[key] == 0:
            unavailable.append("%s replicate %d: the control cell is zero-cost" % key)
            continue
        ratios.append(float(left[key] / right[key]))
    for key in sorted(set(left) ^ set(right)):
        unavailable.append("%s replicate %d: unmatched" % key)
    return (statistics.median(ratios) if ratios else None), len(ratios), unavailable


def screen(document, candidate, control, cards):
    thresholds = dict(DEFAULT_THRESHOLDS, **document.get("thresholds", {}))
    a, b = cards[control], cards[candidate]
    criteria, blockers = [], []
    def add(name, verdict, detail):
        criteria.append({"criterion": name, "verdict": verdict, "detail": detail})

    add("zero candidate-arm false findings", "pass" if b["raw_false_finding_items"] == 0 else "fail",
        "%d raw false finding items (%d of them in invalid or incomplete attempts)"
        % (b["raw_false_finding_items"], b["raw_false_finding_items_invalid_subtotal"]))

    worse_count = b["false_clean_count"] > a["false_clean_count"]
    worse_rate = (b["false_clean_rate"] is not None and a["false_clean_rate"] is not None
                  and b["false_clean_rate"] > a["false_clean_rate"])
    add("no worse false-clean count or rate", "fail" if worse_count or worse_rate else "pass",
        "%s: %d (%s) against %s: %d (%s)" % (candidate, b["false_clean_count"], b["false_clean_rate"],
                                             control, a["false_clean_count"], a["false_clean_rate"]))

    worse_completion = (b["completion_rate"] is not None and a["completion_rate"] is not None
                        and b["completion_rate"] < a["completion_rate"])
    add("no worse completion", "fail" if worse_completion else "pass",
        "%s: %s against %s: %s" % (candidate, b["completion_rate"], control, a["completion_rate"]))

    for view, key in (("all attempts", "macro_material_recall_all_attempts"),
                      ("completed only", "macro_material_recall_completed_only")):
        base, cand = a[key], b[key]
        if base is None or cand is None:
            add("macro material recall gain (%s)" % view, "inconclusive",
                "a buggy target has no attempts in this view, so the macro is unavailable")
            blockers.append("macro material recall is unavailable in the %s view" % view)
            continue
        if base == 0:
            ok = cand - base >= thresholds["zero_baseline_absolute_gain"]
            detail = ("control recall is zero, so the gate is +%.0f percentage points: %.3f against %.3f"
                      % (100 * thresholds["zero_baseline_absolute_gain"], cand, base))
        else:
            ok = (cand > base) and ((cand - base) / base >= thresholds["relative_recall_gain"])
            detail = ("%.3f against %.3f: %+.1f%% relative, %+.3f absolute (gate %+.0f%% relative and "
                      "positive absolute)" % (cand, base, 100 * (cand - base) / base, cand - base,
                                              100 * thresholds["relative_recall_gain"]))
        add("macro material recall gain (%s)" % view, "pass" if ok else "fail", detail)

    ratio, pairs, unavailable = matched_cost_ratio(document, candidate, control)
    if ratio is None:
        add("matched billed cell-cost ratio", "inconclusive", "no complete matched pair")
        blockers.append("no complete matched cost pair for " + candidate)
    else:
        add("matched billed cell-cost ratio", "pass" if ratio <= thresholds["matched_cost_ratio"] else "fail",
            "median %.3f over %d matched pairs (gate <= %.2f)%s"
            % (ratio, pairs, thresholds["matched_cost_ratio"],
               "; unavailable: " + "; ".join(unavailable) if unavailable else ""))

    if b["unresolved_adjudications"] or a["unresolved_adjudications"]:
        blockers.append("unresolved material truth remains in %d control and %d candidate attempts"
                        % (a["unresolved_adjudications"], b["unresolved_adjudications"]))
    planned = set(document.get("planned_cells", []))
    attempted = {attempt["cell_id"] for attempt in document["attempts"]}
    missing = sorted(planned - attempted)
    if missing:
        blockers.append("planned cells with no attempt: " + ", ".join(missing))
    expected_clean = document.get("expected_clean_targets")
    actual_clean = sorted(slot for slot, t in document["targets"].items() if t["status"] == "clean")
    if expected_clean is not None and sorted(expected_clean) != actual_clean:
        blockers.append("the clean/buggy target mix changed: frozen %s, now %s"
                        % (sorted(expected_clean), actual_clean))

    verdicts = [criterion["verdict"] for criterion in criteria]
    if blockers or "inconclusive" in verdicts:
        overall = "inconclusive"
    elif "fail" in verdicts:
        overall = "fail"
    else:
        overall = "pass"
    return {"candidate_arm": candidate, "control_arm": control, "verdict": overall,
            "criteria": criteria, "blockers": blockers,
            "note": "A positive screen recommends a fresh confirmation study against the "
                    "then-current integrated policy. It is not a promotion and not an "
                    "equivalence claim: four targets and two replicates cannot support one."}


def score(document):
    validate(document)
    control = document["control_arm"]
    arms = [control] + list(document["candidate_arms"])
    cards = {arm: arm_scorecard(document, arm) for arm in arms}
    screens = [screen(document, candidate, control, cards) for candidate in document["candidate_arms"]]
    return {"experiment_id": document.get("experiment_id"),
            "truth_version": document.get("truth_version"),
            "arms": cards, "screens": screens}


def render(report):
    lines = ["# Scorecard: %s (truth %s)" % (report["experiment_id"], report["truth_version"]), ""]
    lines.append("| Arm | Attempts | Valid completed | Completion | Macro recall (all) | "
                 "Macro recall (completed) | False clean | Raw false findings | Action errors | "
                 "Sufficient-outcome recall | Billed |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    def show(value, digits=3):
        return "n/a" if value is None else ("%.*f" % (digits, value) if isinstance(value, float) else str(value))
    for arm, card in report["arms"].items():
        lines.append("| %s | %d | %d | %s | %s | %s | %d (%s) | %d | %d | %s | $%s |" % (
            arm, card["attempts"], card["valid_completed"], show(card["completion_rate"]),
            show(card["macro_material_recall_all_attempts"]),
            show(card["macro_material_recall_completed_only"]),
            card["false_clean_count"], show(card["false_clean_rate"]),
            card["raw_false_finding_items"], card["action_errors"],
            show(card["sufficient_outcome_recall"]), card["billed_cost_total"]))
    for result in report["screens"]:
        lines += ["", "## Screen: %s against %s — **%s**" % (result["candidate_arm"],
                                                             result["control_arm"], result["verdict"]), ""]
        for criterion in result["criteria"]:
            lines.append("- **%s** — %s: %s" % (criterion["criterion"], criterion["verdict"], criterion["detail"]))
        for blocker in result["blockers"]:
            lines.append("- **blocked** — %s" % blocker)
        lines += ["", result["note"]]
    return "\n".join(lines) + "\n"


def self_test():
    """Drive the frozen fixtures, including the recovered-but-Approved false clean."""
    path = Path(__file__).with_name("scoring-fixtures.json")
    try:
        fixtures = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 2
    checks = []
    for fixture in fixtures["cases"]:
        name, expected = fixture["name"], fixture["expect"]
        try:
            report = score(fixture["input"])
        except Violation as exc:
            got = {"violation": str(exc).splitlines()[0]}
            checks.append((name, expected.get("violation") in got["violation"] if
                           expected.get("violation") else False))
            continue
        ok = True
        for arm, wanted in expected.get("arms", {}).items():
            card = report["arms"][arm]
            for key, value in wanted.items():
                actual = card[key]
                if isinstance(value, float) and isinstance(actual, float):
                    ok = ok and abs(actual - value) < 1e-9
                else:
                    ok = ok and actual == value
        for wanted in expected.get("screens", []):
            found = [s for s in report["screens"] if s["candidate_arm"] == wanted["candidate_arm"]]
            ok = ok and found and found[0]["verdict"] == wanted["verdict"]
            if found and wanted.get("blocker_contains"):
                ok = ok and any(wanted["blocker_contains"] in blocker for blocker in found[0]["blockers"])
        checks.append((name, bool(ok)))
    for name, ok in checks:
        print(("ok   " if ok else "FAIL ") + name)
    return 0 if all(ok for _, ok in checks) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input")
    parser.add_argument("--out")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.input:
        parser.error("--input is required")
    try:
        document = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 2
    try:
        report = score(document)
    except Violation as exc:
        print(str(exc))
        return 1
    except KeyError as exc:
        print("missing required field " + str(exc), file=sys.stderr)
        return 2
    text = (json.dumps(report, indent=2, sort_keys=True) + "\n") if args.json else render(report)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
