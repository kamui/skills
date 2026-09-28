#!/usr/bin/env python3
"""Apply this run's Stage 2 pass rules to its filed attempts and latest mappings.

Usage: python3 -B stage2.py [--json]

Read-only. Every valid attempt must appear in its target's latest mapping, or the script exits 2.
A review is one valid attempt. A stopped or harness-invalid attempt counts only toward the
invalid-attempt rule. Exit 0 when every rule holds, 1 when any rule rejects, 2 on missing input.
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
                out[attempt["attempt_id"]] = (mapping["target"], mapping["mapping_version"], attempt)
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
            print(f"stage2.py: {attempt['attempt_id']} has no mapping; grade its target first", file=sys.stderr)
            sys.exit(2)
        directory = os.path.dirname(path)
        composition = load(os.path.join(directory, "composition.json"))
        normalized = load(os.path.join(directory, "normalized.json"))
        target, version, graded = mappings[attempt["attempt_id"]]
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
        valid.append({"id": attempt["attempt_id"], "arm": arm, "target": target, "mapping": version,
                      "replicate": attempt["cell"]["replicate"], "cost": attempt["usage"]["priced_total_usd"],
                      "elapsed": elapsed(attempt), "defects": dict(defects),
                      "false": any(i["assignment"] == "false-finding" for i in items),
                      "stray": any(i["jurisdiction"] and i["assignment"] in ("false-finding", "non-material") for i in items),
                      "status": composition["summary"]["status"]})
    return valid, invalid


def decide(valid, invalid):
    arm = lambda name: [r for r in valid if r["arm"] == name]
    control, variant = arm("control"), arm("variant")
    count = lambda rows, key: sum(1 for r in rows if r[key])
    recovered = lambda rows: sum(len(r["defects"]) for r in rows)
    flag = lambda rows, key: sum(1 for r in rows for d in r["defects"].values() if d[key])
    targets = sorted({r["target"] for r in valid})
    wiped = []
    for target in targets:
        c = [r for r in control if r["target"] == target]
        v = [r for r in variant if r["target"] == target]
        for defect in sorted({d for r in c for d in r["defects"]}):
            if all(defect in r["defects"] for r in c) and len(c) == 3 and not any(defect in r["defects"] for r in v):
                wiped.append(f"{target} {defect}")

    def ratio(key):
        values = {}
        for target in targets:
            c = [r[key] for r in control if r["target"] == target and r[key] is not None]
            v = [r[key] for r in variant if r["target"] == target and r[key] is not None]
            values[target] = round(statistics.median(v) / statistics.median(c), 3)
        return values, round(statistics.median(values.values()), 3)

    cost_by_target, cost = ratio("cost")
    time_by_target, time = ratio("elapsed")
    rows = [
        ("Reviews carrying an in-jurisdiction false or non-material finding", count(control, "stray"), count(variant, "stray"),
         "variant minus control at most 1", count(variant, "stray") - count(control, "stray") <= 1),
        ("Reviews carrying any false finding", count(control, "false"), count(variant, "false"),
         "variant minus control at most 2", count(variant, "false") - count(control, "false") <= 2),
        ("Registered defects recovered", recovered(control), recovered(variant),
         "variant at least control minus 3, and no defect the control recovers 3 of 3 is recovered 0 of 3",
         recovered(variant) >= recovered(control) - 3 and not wiped),
        ("`must-fix` on recovered defects", flag(control, "must_fix"), flag(variant, "must_fix"),
         "variant at least control minus 3", flag(variant, "must_fix") >= flag(control, "must_fix") - 3),
        ("Sufficient remedies on recovered defects", flag(control, "sufficient"), flag(variant, "sufficient"),
         "variant at least control minus 3", flag(variant, "sufficient") >= flag(control, "sufficient") - 3),
        ("Invalid or stopped attempts", invalid["control"], invalid["variant"],
         "variant at most control plus 1", invalid["variant"] <= invalid["control"] + 1),
        ("Cost, median over targets of the variant-to-control ratio of per-target median cost", 1.0, cost,
         "at most 0.90", cost <= 0.90),
        ("Elapsed to payload, the same ratio", 1.0, time, "at most 0.90", time <= 0.90),
    ]
    return {"reviews": {"control": len(control), "variant": len(variant)}, "wiped_defects": wiped,
            "cost_ratio_by_target": cost_by_target, "elapsed_ratio_by_target": time_by_target,
            "approvals_of_buggy_change": {"control": sum(1 for r in control if r["status"] == "Approved" and r["target"] not in ("m-grpc-go-7390",)),
                                          "variant": sum(1 for r in variant if r["status"] == "Approved" and r["target"] not in ("m-grpc-go-7390",))},
            "cost_usd": {"control": round(sum(r["cost"] for r in control), 6), "variant": round(sum(r["cost"] for r in variant), 6)},
            "rules": [{"measure": m, "control": c, "variant": v, "passes_when": w, "holds": h} for m, c, v, w, h in rows],
            "passes": all(h for *_, h in rows)}


def main():
    valid, invalid = reviews()
    result = decide(valid, invalid)
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print(f"reviews: {result['reviews']}; invalid or stopped: {dict(invalid)}")
        for rule in result["rules"]:
            print(f"{'holds  ' if rule['holds'] else 'REJECTS'} | {rule['measure']} | control {rule['control']} | "
                  f"variant {rule['variant']} | {rule['passes_when']}")
        print("cost ratio by target:", result["cost_ratio_by_target"])
        print("elapsed ratio by target:", result["elapsed_ratio_by_target"])
        print("defects the control recovers 3 of 3 and the variant 0 of 3:", result["wiped_defects"] or "none")
        print("approvals of a buggy change:", result["approvals_of_buggy_change"], "| review cost:", result["cost_usd"])
        print("PASS" if result["passes"] else "REJECT")
    return 0 if result["passes"] else 1


if __name__ == "__main__":
    sys.exit(main())
