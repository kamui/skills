#!/usr/bin/env python3
"""Apply this run's preregistered decision rule to its filed attempts and latest mappings.

Usage: python3 -B decide.py [--json]

Read-only. A review is one valid attempt, and every valid attempt must appear in its target's latest
mapping. Exit 0 pass, 1 reject, 2 missing input (including a target not yet run when the clean
target alone does not decide), 3 inconclusive.
"""
from __future__ import annotations

import glob
import json
import os
import re
import statistics
import sys
from collections import defaultdict
from datetime import datetime

RUN = os.path.dirname(os.path.abspath(__file__))
CONTROL = "review-code-sonnet-high-enforced-x394-control"
VARIANT = "review-code-sonnet-high-enforced-verification-off"
ARMS = {CONTROL: "control", VARIANT: "variant"}
CLEAN, BUGGY = "t-rclone-9699", "s-seaweedfs-10735"
REPLICATES = 3
RECALL_MARGIN = 2
FALSE_MARGIN = 2
MIN_CONTROL_BATCHES = 2
JURISDICTION_KINDS = ("security", "compatibility")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def latest_mappings():
    out = {}
    for directory in glob.glob(os.path.join(RUN, "scoring", "*")):
        versions = sorted(glob.glob(os.path.join(directory, "mapping.v*.json")),
                          key=lambda p: int(re.search(r"mapping\.v(\d+)", p).group(1)))
        if versions:
            mapping = load(versions[-1])
            for attempt in mapping["attempts"]:
                out[attempt["attempt_id"]] = attempt
    return out


def elapsed(attempt):
    timing = attempt["timing"]
    if not timing.get("payload_validated_at"):
        return None
    parse = lambda value: datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    return (parse(timing["payload_validated_at"]) - parse(timing["dispatched_at"])).total_seconds()


def reviews():
    mappings = latest_mappings()
    valid, invalid = [], defaultdict(int)
    for path in sorted(glob.glob(os.path.join(RUN, "attempts", "att-*", "attempt.json"))):
        attempt = load(path)
        arm = ARMS[attempt["cell"]["arm"]]
        if attempt["disposition"] != "valid completed":
            invalid[arm] += 1
            continue
        if attempt["attempt_id"] not in mappings:
            print(f"decide.py: {attempt['attempt_id']} has no mapping; grade its target first", file=sys.stderr)
            sys.exit(2)
        directory = os.path.dirname(path)
        composition = load(os.path.join(directory, "composition.json"))
        normalized = load(os.path.join(directory, "normalized.json"))
        graded = mappings[attempt["attempt_id"]]
        items = []
        for index, (grade, native) in enumerate(zip(graded["items"], normalized["items"])):
            finding = composition["findings"][index] if native["kind"] == "finding" else None
            items.append({"assignment": grade["assignment"], "fix": grade["fix_sufficiency"],
                          "must_fix": bool(finding and finding["action"] == "must-fix"),
                          "jurisdiction": bool(finding and (finding["action"] == "must-fix"
                                                            or finding["kind"] in JURISDICTION_KINDS))})
        defects = defaultdict(lambda: {"must_fix": False, "sufficient": False})
        for item in items:
            if item["assignment"].startswith("defect:"):
                entry = defects[item["assignment"][len("defect:"):]]
                entry["must_fix"] |= item["must_fix"]
                entry["sufficient"] |= item["fix"] == "sufficient"
        verification = composition.get("record", {}).get("verification") or {}
        valid.append({"id": attempt["attempt_id"], "arm": arm, "target": attempt["cell"]["target"],
                      "cell": (attempt["cell"]["target"], arm, attempt["cell"]["replicate"]),
                      "cost": attempt["usage"]["priced_total_usd"], "elapsed": elapsed(attempt),
                      "defects": dict(defects),
                      "false": any(i["assignment"] == "false-finding" for i in items),
                      "stray": any(i["jurisdiction"] and i["assignment"] in ("false-finding", "non-material") for i in items),
                      "batches": len(verification.get("batches") or []),
                      "status": composition["summary"]["status"]})
    return valid, invalid


def decide(valid, invalid):
    pick = lambda arm, target: [r for r in valid if r["arm"] == arm and r["target"] == target]
    count = lambda rows, key: sum(1 for r in rows if r[key])
    recovered = lambda rows: sum(len(r["defects"]) for r in rows)
    flag = lambda rows, key: sum(1 for r in rows for d in r["defects"].values() if d[key])
    clean = {arm: pick(arm, CLEAN) for arm in ("control", "variant")}
    buggy = {arm: pick(arm, BUGGY) for arm in ("control", "variant")}
    complete = lambda rows: len({r["cell"] for r in rows}) == REPLICATES

    false_rule = count(clean["variant"], "false") - count(clean["control"], "false") >= FALSE_MARGIN
    recall_rule = recovered(buggy["control"]) - recovered(buggy["variant"]) >= RECALL_MARGIN
    clean_done = all(complete(rows) for rows in clean.values())
    buggy_done = all(complete(rows) for rows in buggy.values())
    batches = count(clean["control"] + buggy["control"], "batches")

    if clean_done and false_rule:
        verdict = "reject"
    elif not (clean_done and buggy_done):
        verdict = "missing"
    elif recall_rule:
        verdict = "reject"
    elif batches < MIN_CONTROL_BATCHES:
        verdict = "inconclusive"
    else:
        verdict = "pass"

    def median_ratio(key):
        out = {}
        for target in (CLEAN, BUGGY):
            c = [r[key] for r in pick("control", target) if r[key] is not None]
            v = [r[key] for r in pick("variant", target) if r[key] is not None]
            if c and v:
                out[target] = round(statistics.median(v) / statistics.median(c), 3)
        return out

    per_arm = lambda f: {arm: f(arm) for arm in ("control", "variant")}
    return {
        "verdict": verdict,
        "rules": [
            {"rule": "clean target: variant reviews with a false finding minus control's is at least 2",
             "control": count(clean["control"], "false"), "variant": count(clean["variant"], "false"), "rejects": false_rule},
            {"rule": "buggy target: control recoveries minus variant recoveries is at least 2",
             "control": recovered(buggy["control"]), "variant": recovered(buggy["variant"]), "rejects": recall_rule},
            {"rule": "control dispatches a verifier batch in at least 2 of its reviews",
             "control": batches, "variant": None, "rejects": False},
        ],
        "literal_380": {"recall_not_below_control": recovered(buggy["variant"]) >= recovered(buggy["control"]),
                        "zero_false_findings_on_clean": count(clean["variant"], "false") == 0},
        "reviews": per_arm(lambda a: len(clean[a]) + len(buggy[a])),
        "invalid_or_stopped": dict(invalid),
        "buggy_false_findings": per_arm(lambda a: count(buggy[a], "false")),
        "in_jurisdiction_false_or_non_material": per_arm(lambda a: count(clean[a] + buggy[a], "stray")),
        "must_fix_on_recovered": per_arm(lambda a: flag(buggy[a], "must_fix")),
        "sufficient_on_recovered": per_arm(lambda a: flag(buggy[a], "sufficient")),
        "verdicts": {f"{t}/{a}": [r["status"] for r in pick(a, t)] for t in (CLEAN, BUGGY) for a in ("control", "variant")},
        "verifier_batches": {f"{t}/{a}": [r["batches"] for r in pick(a, t)] for t in (CLEAN, BUGGY) for a in ("control", "variant")},
        "cost_usd": per_arm(lambda a: round(sum(r["cost"] for r in clean[a] + buggy[a]), 6)),
        "cost_ratio_by_target": median_ratio("cost"),
        "elapsed_ratio_by_target": median_ratio("elapsed"),
    }


def main():
    result = decide(*reviews())
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        for rule in result["rules"]:
            print(f"{'REJECTS' if rule['rejects'] else 'holds  '} | {rule['rule']} | control {rule['control']} | variant {rule['variant']}")
        for key in ("literal_380", "reviews", "invalid_or_stopped", "buggy_false_findings", "in_jurisdiction_false_or_non_material",
                    "must_fix_on_recovered", "sufficient_on_recovered", "verdicts", "verifier_batches", "cost_usd",
                    "cost_ratio_by_target", "elapsed_ratio_by_target"):
            print(f"{key}: {result[key]}")
        print(result["verdict"].upper())
    return {"pass": 0, "reject": 1, "missing": 2, "inconclusive": 3}[result["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
