#!/usr/bin/env python3
"""Answer the run's preregistered questions (README §8) from a results file, the attempt records and the mappings.

Usage::

    python3 docs/research/builtin-review-benchmark-2026-09-24/answers.py [--results results.v3.json]

Prints Markdown tables. Recall, false findings and the review-level counts come from the results file. The two ratios
are computed here, per matched cell (same target and replicate as arm A's): a cell's cost is the sum of every attempt
it took, replacements included (method §4); its elapsed-to-payload is its final attempt's. Each ratio is the median of
the per-cell ratios to A. The unrecovered defects are the register defects no admissible item in the named mappings
recovers. Exit codes: 0 printed; 1 an input cannot be read or lacks valid-review counts.
"""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "bench" / "runs" / "2026-09-24-builtin-baseline"
A = "review-code-sonnet-high"
ORDER = [A, "claude-builtin-sonnet-high", "claude-builtin-opus-high", "codex-default"]
LABEL = {A: "A review-code", "claude-builtin-sonnet-high": "B built-in Sonnet 5", "claude-builtin-opus-high": "C built-in Opus 5.5",
         "codex-default": "D codex review"}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def seconds(start, end):
    if not start or not end:
        return None
    parse = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
    return (parse(end) - parse(start)).total_seconds()


def register(target, version):
    plain = ROOT / "bench" / "targets" / target / f"register.v{version}.json"
    opened = Path.home() / ".t3" / "bench-runs" / RUN.name / "opened" / target / f"register.v{version}.json"
    return read(plain if plain.is_file() else opened)


def review_table(results):
    print("| Arm | Attempts | Valid reviews | Recall, completed-only (attempt-level) | False findings raw / unique per valid review | "
          "Approved on valid buggy | Zero recovery on valid buggy | False clean on valid buggy | Noise per valid review |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for arm in ORDER:
        row = next(r for r in results["by_arm"] if r["key"]["arm"] == arm)
        valid = row["valid_reviews"]
        n, on_buggy = valid["count"], valid["buggy_count"]
        print(f"| {LABEL[arm]} | {row['attempts_included']} | {n} | "
              f"{row['recall_completed_only']:.3f} ({row['recall_attempt_level']:.3f}) | "
              f"{valid['false_findings_raw'] / n:.2f} / {valid['false_findings_unique'] / n:.2f} "
              f"({valid['false_findings_raw']} / {valid['false_findings_unique']}) | "
              f"{valid['approved_on_buggy']}/{on_buggy} | {valid['zero_recovery']}/{on_buggy} | "
              f"{valid['false_clean']}/{on_buggy} | {valid['noise_items'] / n:.1f} ({valid['noise_items']} items) |")

    print()
    print("All-attempt counts include invalid and incomplete attempts; valid-review counts above exclude them.")
    print()
    print("| Arm | Attempts | False findings raw / unique per attempt | Approved on buggy | Zero recovery | False clean | "
          "All-attempt noise | Noise excluded from valid reviews |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for arm in ORDER:
        row = next(r for r in results["by_arm"] if r["key"]["arm"] == arm)
        n = row["attempts_included"]
        print(f"| {LABEL[arm]} | {n} | {row['false_findings_raw'] / n:.2f} / {row['false_findings_unique'] / n:.2f} "
              f"({row['false_findings_raw']} / {row['false_findings_unique']}) | {row['approved_on_buggy']} | "
              f"{row['zero_recovery']} | {row['false_clean']} | {row['noise_items']} | "
              f"{row['noise_items'] - row['valid_reviews']['noise_items']} |")


def cost_table(results, attempts):
    cost, elapsed = {}, {}
    for cell in results["cells"]:
        key = (cell["target"], cell["replicate"])
        records = [attempts[a] for a in cell["attempts"]]
        cost.setdefault(cell["arm"], {})[key] = sum(r["usage"]["priced_total_usd"] or 0 for r in records)
        last = records[-1]["timing"]
        elapsed.setdefault(cell["arm"], {})[key] = seconds(last.get("dispatched_at"), last.get("payload_validated_at"))
    print()
    print("| Arm | Cost pairs | Timing pairs | Median cost ratio to A | Arm total cost ($) | Median elapsed-to-payload ratio to A | "
          "Median elapsed to payload (s) |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for arm in ORDER:
        keys = sorted(set(cost[arm]) & set(cost[A]))
        cost_ratios = [cost[arm][k] / cost[A][k] for k in keys if cost[A][k]]
        time_ratios = [elapsed[arm][k] / elapsed[A][k] for k in keys if elapsed[arm][k] and elapsed[A][k]]
        print(f"| {LABEL[arm]} | {len(cost_ratios)} | {len(time_ratios)} | {statistics.median(cost_ratios):.2f} | {sum(cost[arm].values()):.2f} | "
              f"{statistics.median(time_ratios):.2f} | {statistics.median(v for v in elapsed[arm].values() if v):.0f} |")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default=str(RUN / "results.v3.json"))
    results = read(parser.parse_args().results)
    attempts = {p.parent.name: read(p) for p in sorted((RUN / "attempts").glob("att-*/attempt.json"))}
    review_table(results)

    print()
    print("Per target: attempt-level recall (`-` on a clean target), then valid-review raw false findings and zero-recovery counts.")
    print()
    print("| Target | " + " | ".join(LABEL[a] for a in ORDER) + " |")
    print("| --- |" + " --- |" * len(ORDER))
    for entry in results["inputs"]:
        cells = []
        for arm in ORDER:
            row = next(r for r in results["by_target_arm"] if r["key"] == {"arm": arm, "target": entry["target"]})
            recall = "-" if row["recall_attempt_level"] is None else f"{row['recall_attempt_level']:.2f}"
            cells.append(f"{recall}; ff {row['valid_reviews']['false_findings_raw']}; zr {row['valid_reviews']['zero_recovery']}")
        print(f"| {entry['target']} | " + " | ".join(cells) + " |")

    cost_table(results, attempts)

    print()
    print("| Target | Register | Defect | Recovered by |")
    print("| --- | --- | --- | --- |")
    for entry in results["inputs"]:
        target, version = entry["target"], entry["mapping_version"]
        mapping = read(RUN / "scoring" / target / f"mapping.v{version}.json")
        defects = [d["id"] for d in register(target, entry["register_version"])["defects"]]
        by = {d: set() for d in defects}
        for scored in mapping["attempts"]:
            record = attempts[scored["attempt_id"]]
            if record["disposition"].startswith("harness-invalid"):
                continue
            for item in scored["items"]:
                if item["assignment"].startswith("defect:"):
                    by[item["assignment"][7:]].add(record["cell"]["arm"])
        for defect in defects:
            arms = ", ".join(LABEL[a].split()[0] for a in ORDER if a in by[defect]) or "**none**"
            print(f"| {target} | v{entry['register_version']} | {defect} | {arms} |")


if __name__ == "__main__":
    main()
