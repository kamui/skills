#!/usr/bin/env python3
"""Drive scoreboard.py through subprocess on synthetic runs and on the real registry.

Usage::

    python3 bench/tools/test_scoreboard.py

Exit codes: 0 every test passed; 1 a test failed.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parent
SCRIPT = TOOLS / "scoreboard.py"
BUG1, BUG2, CLEAN = "t-bug1", "t-bug2", "t-clean"
TARGETS = (BUG1, BUG2, CLEAN)
START = datetime(2026, 1, 1, tzinfo=timezone.utc)


def spec(recall, times, cost, ff=0, noise=0, approved=0, zero=0, fixes=(0, 0, 0)) -> dict:
    return {"recall": recall, "times": times, "cost": cost, "ff": ff, "noise": noise,
            "approved": approved, "zero": zero, "fixes": fixes}


REF_ROWS = {BUG1: spec(1.0, [60, 120], 0.5, noise=2, fixes=(1, 0, 0)),
            BUG2: spec(0.5, [30, 30], 0.5, ff=1, approved=1, zero=1, fixes=(0, 1, 0)),
            CLEAN: spec(None, [90, 90], 1.0, ff=2, noise=2)}
OTHER_ROWS = {BUG1: spec(0.5, [20, 40], 0.2, fixes=(1, 0, 0)),
              CLEAN: spec(None, [10, 10], 0.2, noise=2)}
REF_OWN = "| Ref (reference) | v-ref | 3 of 3 | 6/6 | 75% | 1/4 | 1/4 | 3 (0.50 per review) | 0.7 | 1/2 | $0.33 | 1m 15s |"
OTHER_OWN = "| Other | v-other | 2 of 3 | 4/4 | 50% | 0/2 | 0/2 | 0 (0.00 per review) | 0.5 | 1/1 | $0.10 | 15s |"
OTHER_PAIR = ("| Other | v-other | 2 | 4/4 / 4/4 | 50% / 100% | 0/2 / 0/2 | 0/2 / 0/2 | "
              "0 (0.00 per review) / 2 (0.50 per review) | 0.5 / 1.0 | 1/1 / 1/1 | $0.10 / $0.38 | 15s / 1m 30s |")


def target_row(arm: str, target: str, s: dict) -> dict:
    n, buggy = len(s["times"]), s["recall"] is not None
    return {"key": {"arm": arm, "target": target}, "attempts_included": n,
            "valid_reviews": {"count": n, "buggy_count": n if buggy else 0, "false_findings_raw": s["ff"],
                              "approved_on_buggy": s["approved"], "zero_recovery": s["zero"], "noise_items": s["noise"]},
            "recall_attempt_level": s["recall"], "false_findings_raw": s["ff"],
            "fix_sufficient": dict(zip(("sufficient", "partial", "absent"), s["fixes"])),
            "cost_contemporaneous_usd": s["cost"], "elapsed_to_completion_s": statistics.median(s["times"])}


def arm_row(arm: str, rows: dict) -> dict:
    parts = [target_row(arm, t, s) for t, s in rows.items()]
    recalls = [s["recall"] for s in rows.values() if s["recall"] is not None]
    return {"key": {"arm": arm}, "attempts_included": sum(p["attempts_included"] for p in parts),
            "valid_reviews": {k: sum(p["valid_reviews"][k] for p in parts) for k in parts[0]["valid_reviews"]},
            "recall_attempt_level": round(sum(recalls) / len(recalls), 6) if recalls else None,
            "false_findings_raw": sum(p["false_findings_raw"] for p in parts),
            "fix_sufficient": {k: sum(p["fix_sufficient"][k] for p in parts) for k in ("sufficient", "partial", "absent")},
            "cost_contemporaneous_usd": (None if any(s["cost"] is None for s in rows.values())
                                         else round(sum(s["cost"] for s in rows.values()), 6)),
            "elapsed_to_completion_s": statistics.median([t for s in rows.values() for t in s["times"]])}


class ScoreboardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.registry = self.root / "scoreboard.json"
        self.out = self.root / "SCOREBOARD.md"
        self.write_cohort_run("suite", {BUG1: 2, BUG2: 1, CLEAN: 1}, ["pend"])
        self.write_run("r1", {"ref": REF_ROWS, "other": OTHER_ROWS}, manifest_registers={BUG1: 1},
                       graded={BUG1: 2, BUG2: 1, CLEAN: 1})
        self.suite = {"id": "s", "title": "Suite S", "summary": "Two arms.", "reference": "ref",
                      "cohort_run": "runs/suite", "entries": [self.entry("ref", "Ref", "runs/r1", "ref"),
                                                             self.entry("other", "Other", "runs/r1", "other")]}

    def tearDown(self) -> None:
        self.tmp.cleanup()

    @staticmethod
    def entry(entry_id: str, label: str, run: str, arm: str, results="results.v1.json") -> dict:
        return {"id": entry_id, "label": label, "version": f"v-{entry_id}",
                "sources": [{"run": run, "results": results, "arm": arm}]}

    def write_json(self, path: Path, value) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def manifest(self, targets, registers: dict, arms, planned=(), rubric=1, packets=None) -> dict:
        return {"rubric_version": rubric, "arms": [{"id": a} for a in arms],
                "cohort": [{"target": t, "register_version": registers.get(t, 1),
                            "packet_sha256": (packets or {}).get(t, f"packet-{t}"), "diff_manifest_sha256": f"diff-{t}"}
                           for t in targets],
                "planned_cells": list(planned)}

    def write_cohort_run(self, name: str, registers: dict, arms, packets=None) -> None:
        self.write_json(self.root / "runs" / name / "manifest.json",
                        self.manifest(list(registers), registers, arms, packets=packets))

    def write_run(self, name: str, arms: dict, manifest_registers=None, graded=None, rubric=1, by_arm_patch=None) -> None:
        run = self.root / "runs" / name
        targets = [t for t in TARGETS if any(t in rows for rows in arms.values())]
        cells, planned = [], []
        for arm, rows in arms.items():
            for target, s in rows.items():
                for replicate, seconds in enumerate(s["times"], 1):
                    attempt = f"{arm}-{target}-{replicate}"
                    cells.append({"target": target, "arm": arm, "replicate": replicate,
                                  "status": "valid completed", "attempts": [attempt]})
                    planned.append({"target": target, "arm": arm, "replicate": replicate})
                    self.write_json(run / "attempts" / attempt / "attempt.json", {
                        "timing": {"dispatched_at": START.isoformat(),
                                   "completed_at": (START + timedelta(seconds=seconds)).isoformat()},
                        "usage": {"billing": "api-dollars"}})
        by_arm = [arm_row(arm, rows) for arm, rows in arms.items()]
        if by_arm_patch:
            by_arm_patch(by_arm)
        self.write_json(run / "manifest.json", self.manifest(targets, manifest_registers or {}, arms, planned, rubric))
        self.write_json(run / "results.v1.json", {
            "rubric_version": rubric, "cells": cells, "by_arm": by_arm,
            "inputs": [{"target": t, "register_version": (graded or {}).get(t, 1)} for t in targets],
            "by_target_arm": [target_row(arm, t, s) for arm, rows in arms.items() for t, s in rows.items()]})

    def run_tool(self, *extra: str) -> subprocess.CompletedProcess:
        self.write_json(self.registry, {"schema_version": 1, "description": "test", "suites": [self.suite]})
        return subprocess.run([sys.executable, "-B", str(SCRIPT), "--registry", str(self.registry),
                               "--out", str(self.out), *extra],
                              capture_output=True, text=True, encoding="utf-8", check=False)

    def page(self) -> list:
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return self.out.read_text(encoding="utf-8").splitlines()

    def assert_refused(self, *expected: str) -> None:
        self.out.unlink(missing_ok=True)
        result = self.run_tool()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for fragment in expected:
            self.assertIn(fragment, result.stdout)
        self.assertFalse(self.out.exists())

    def test_own_target_rows_and_graded_register_comparability(self) -> None:
        page = self.page()
        self.assertIn(REF_OWN, page)
        self.assertIn(OTHER_OWN, page)
        self.assertIn(f"| `{BUG1}` |  | 100% · 0 FF | 50% · 0 FF |", page)
        self.assertIn(f"| `{CLEAN}` |  | clean · 2 FF | clean · 0 FF |", page)
        self.assertIn("| Version |  | v-ref | v-other |", page)
        self.assertIn("- [`r1`](runs/r1), `results.v1.json`, for `ref`, `other`", page)

    def test_own_target_row_equals_by_arm_when_every_target_ran(self) -> None:
        by_arm = arm_row("ref", REF_ROWS)
        self.assertEqual((by_arm["recall_attempt_level"], by_arm["elapsed_to_completion_s"],
                          by_arm["cost_contemporaneous_usd"] / by_arm["attempts_included"]), (0.75, 75, 2.0 / 6))
        self.assertIn(REF_OWN, self.page())
        self.write_run("r1", {"ref": REF_ROWS, "other": OTHER_ROWS}, graded={BUG1: 2},
                       by_arm_patch=lambda rows: rows[0]["valid_reviews"].update(noise_items=5))
        self.assert_refused("s/ref: runs/r1 by_target_arm rows do not reproduce its by_arm row on "
                            "valid_reviews.noise_items")

    def test_not_run_and_not_comparable_targets(self) -> None:
        page = self.page()
        self.assertIn(f"| `{BUG2}` |  | 50% · 1 FF | *not run* |", page)
        self.assertIn(f"- **Other** at v-other did not run `{BUG2}`.", page)
        self.write_cohort_run("suite", {BUG1: 2, BUG2: 3, CLEAN: 1}, ["pend"], packets={CLEAN: "moved"})
        page = self.page()
        self.assertIn(f"| `{BUG2}` |  | *not comparable (register v1, suite v3)* | *not run* |", page)
        self.assertIn(f"| `{CLEAN}` |  | *not comparable (packet differs)* | *not comparable (packet differs)* |", page)
        self.assertIn(f"- **Ref** at v-ref is not comparable on `{BUG2}` (register v1, suite v3), "
                      f"`{CLEAN}` (packet differs).", page)
        self.assertTrue(any(line.startswith("| Ref (reference) | v-ref | 1 of 3 |") for line in page))

    def test_pairwise_table_compares_each_row_with_the_reference_on_shared_targets(self) -> None:
        self.assertIn(OTHER_PAIR, self.page())

    def test_pending_entries_and_pending_reference(self) -> None:
        self.suite["entries"].append(self.entry("pend", "Pend", "runs/suite", "pend", results=None))
        page = self.page()
        self.assertIn("| Pend | v-pend | pending |" + " pending |" * 9, page)
        self.assertIn(f"| `{BUG1}` |  | 100% · 0 FF | 50% · 0 FF | *pending* |", page)
        self.assertIn(OTHER_PAIR, page)
        self.suite["reference"] = "pend"
        page = self.page()
        self.assertIn("| Other | v-other | pending |" + " pending |" * 9, page)
        self.assertIn(OTHER_OWN, page)

    def test_multi_source_entry_aggregates_across_runs(self) -> None:
        self.write_run("r2", {"x": {BUG1: spec(1.0, [100, 100], 0.3, ff=1, fixes=(1, 0, 0))}})
        self.write_run("r3", {"x": {BUG2: spec(0.0, [200, 200], 0.3, noise=2, approved=2, zero=2),
                                    CLEAN: spec(None, [50, 50], 0.3)}}, graded={})
        multi = self.entry("multi", "Multi", "runs/r2", "x")
        multi["sources"].append({"run": "runs/r3", "results": "results.v1.json", "arm": "x"})
        self.suite["entries"].append(multi)
        self.write_cohort_run("suite", {BUG1: 1, BUG2: 1, CLEAN: 1}, ["pend"])
        page = self.page()
        self.assertIn("| Multi | v-multi | 3 of 3 | 6/6 | 50% | 2/4 | 2/4 | 1 (0.17 per review) | 0.3 | 1/1 | $0.15 | 1m 40s |",
                      page)
        self.assertIn(f"| `{BUG2}` |  | 50% · 1 FF | *not run* | 0% · 0 FF |", page)
        self.write_run("r3", {"x": {BUG1: spec(0.0, [5], 0.1), CLEAN: spec(None, [50, 50], 0.3)}})
        self.assert_refused(f"s/multi: runs/r2 and runs/r3 both have attempts on {BUG1}")

    def test_check_passes_on_fresh_output_and_fails_after_an_edit(self) -> None:
        result = self.run_tool("--check")
        self.assertEqual((result.returncode, result.stdout.count("\n")), (1, 1), "a missing page is stale")
        self.page()
        self.assertEqual(self.run_tool("--check").returncode, 0)
        self.out.write_text(self.out.read_text(encoding="utf-8").replace("75%", "76%"), encoding="utf-8")
        result = self.run_tool("--check")
        self.assertEqual((result.returncode, result.stdout.count("\n")), (1, 1))
        self.assertIn("stale", result.stdout)

    def chart(self, *targets: str) -> None:
        self.suite["chart"] = {"targets": list(targets)}
        for entry, method in zip(self.suite["entries"], ("claude-builtin", "review-code")):
            entry.update(method=method, short=f"short-{entry['id']}")

    def test_chart_plots_every_row_that_ran_the_chart_targets_with_a_table_twin(self) -> None:
        self.chart(BUG1, CLEAN)
        page = self.page()
        self.assertIn("| Ref | v-ref | 100% | 0.50 | 1.0 | $0.38 | 4 of 4 |", page)
        self.assertIn("| Other | v-other | 50% | 0.00 | 0.5 | $0.10 | 4 of 4 |", page)
        for chart in ("cost", "false-findings"):
            for theme in ("light", "dark"):
                svg = (self.root / "scoreboard" / f"s-{chart}-{theme}.svg").read_text(encoding="utf-8")
                self.assertIn(">short-ref</text>", svg)
                self.assertIn("<title>Other at v-other: 50% of registered defects found", svg)
        self.assertFalse(any(line.startswith("Not plotted") for line in page))
        self.assertTrue(any(line.endswith("Recall averages every attempt, so a review that stopped or was filed "
                                          "harness-invalid counts as finding nothing.") for line in page))
        self.chart(BUG1, BUG2)
        self.assertIn("Not plotted, because they did not run every one of these targets: Other at v-other.", self.page())

    def test_chart_leaves_out_an_unavailable_figure_and_places_a_sub_cent_cost(self) -> None:
        self.write_run("r1", {"ref": REF_ROWS, "other": {BUG1: spec(0.5, [20, 40], None), CLEAN: spec(None, [10, 10], 0.004)}},
                       manifest_registers={BUG1: 1}, graded={BUG1: 2, BUG2: 1, CLEAN: 1})
        self.chart(BUG1, CLEAN)
        page = self.page()
        self.assertIn("Not plotted, because a plotted figure is unavailable for them: Other at v-other.", page)
        self.assertFalse(any(line.startswith("| Other | v-other | 50% |") for line in page))
        self.write_run("r1", {"ref": REF_ROWS, "other": {BUG1: spec(0.5, [20, 40], 0.004), CLEAN: spec(None, [10, 10], 0.004)}},
                       manifest_registers={BUG1: 1}, graded={BUG1: 2, BUG2: 1, CLEAN: 1})
        self.assertIn("| Other | v-other | 50% | 0.00 | 0.0 | $0.00 | 4 of 4 |", self.page())
        self.assertIn(">$0.001</text>", (self.root / "scoreboard" / "s-cost-light.svg").read_text(encoding="utf-8"))

    def test_chart_with_nothing_plotted_names_every_left_out_row(self) -> None:
        self.write_run("r1", {"ref": {**REF_ROWS, BUG2: spec(0.5, [30, 30], None)}, "other": OTHER_ROWS},
                       manifest_registers={BUG1: 1}, graded={BUG1: 2, BUG2: 1, CLEAN: 1})
        self.chart(BUG1, BUG2)
        page = self.page()
        self.assertIn(f"No reviewer is plotted on `{BUG1}`, `{BUG2}`.", page)
        self.assertIn("Not plotted, because they did not run every one of these targets: Other at v-other.", page)
        self.assertIn("Not plotted, because a plotted figure is unavailable for them: Ref at v-ref.", page)
        self.assertFalse((self.root / "scoreboard").exists())

    def test_check_fails_when_a_chart_is_stale(self) -> None:
        self.chart(BUG1, CLEAN)
        self.page()
        chart = self.root / "scoreboard" / "s-cost-dark.svg"
        chart.write_text(chart.read_text(encoding="utf-8").replace("short-ref", "edited"), encoding="utf-8")
        result = self.run_tool("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("s-cost-dark.svg is stale", result.stdout)

    def test_a_charted_suite_needs_methods_and_cohort_targets(self) -> None:
        self.chart(BUG1, "t-elsewhere")
        del self.suite["entries"][1]["method"]
        self.assert_refused("s: chart targets must be a non-empty subset of the cohort; not in it: t-elsewhere",
                            "s/other: a charted suite needs each entry's method")

    def test_rubric_mismatch_is_refused(self) -> None:
        self.write_run("r1", {"ref": REF_ROWS, "other": OTHER_ROWS}, graded={BUG1: 2}, rubric=2)
        self.assert_refused("s/ref: runs/r1 uses rubric v2, the cohort run v1")

    def test_missing_arm_row_is_refused(self) -> None:
        self.suite["entries"][1]["sources"][0]["arm"] = "pend"
        manifest = json.loads((self.root / "runs" / "r1" / "manifest.json").read_text(encoding="utf-8"))
        manifest["arms"].append({"id": "pend"})
        self.write_json(self.root / "runs" / "r1" / "manifest.json", manifest)
        self.assert_refused("s/other: runs/r1/results.v1.json has no by_arm row for arm pend")

    def test_unknown_reference_and_duplicate_ids_are_refused(self) -> None:
        self.suite["reference"] = "nobody"
        self.suite["entries"][1]["id"] = "ref"
        self.assert_refused("s: reference nobody names no entry", "s: duplicate entry id ref")

    def test_missing_results_is_refused_and_unreadable_results_is_an_input_error(self) -> None:
        self.suite["entries"][1]["sources"][0]["results"] = "results.v9.json"
        self.assert_refused("s/other: runs/r1/results.v9.json is missing")
        (self.root / "runs" / "r1" / "results.v9.json").write_text("{", encoding="utf-8")
        result = self.run_tool()
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot read", result.stderr)

    def test_real_registry_page_is_current(self) -> None:
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--check"],
                                capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
