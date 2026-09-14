#!/usr/bin/env python3
"""CLI regressions for run timing events and their summary.

Usage: python3 scripts/test_run_events.py
Inputs: a disposable Git repository, the verifier-handoff fixtures, and
synthetic event files; no forge, worker, or transcript access.
Exit 0: checks pass; 1: assertion failure; 2: a subprocess cannot run.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

import test_verifier_handoff as handoff

SCRIPTS = Path(__file__).resolve().parent
DOMAIN = {"host": "h", "boot": "b", "boot_source": "linux:boot_id", "implementation": "mono"}
HEAD = "a" * 40
S = 1_000_000_000


def event(name, start, end, exit=0, clock=None, **data):
    return {"format": "review-run-event/1", "event": name, "exit": exit,
            "origin": {"script": "x.py", "pid": 1, "harness": {"name": None, "source": None, "session": None}},
            "clock": dict(DOMAIN) if clock is None else clock, "started_ns": start * S, "ended_ns": end * S,
            "ended_at": f"2026-09-14T12:00:{end % 60:02d}.000000Z", "policy": None, "data": data}


def context(end=2, **kw):
    return event("context-built", end - 1, end, head=HEAD, target="commit-range", **kw)


def brief(batch, end, mode="candidate-only", candidates=1, ledger_rows=0):
    return event("verifier-brief-built", end, end, batch_id=batch, phase="initial", mode=mode,
                 candidates=candidates, ledger_rows=ledger_rows)


def accounted(batch, end, exit=0, **counts):
    returned = {"confirmed": 1, "refuted": 0, "holds": 0, "re_open": 0}
    returned.update(counts)
    return event("verifier-return-accounted", end, end, exit=exit, batch_id=batch, returned=returned,
                 withheld={"candidates": 0, "ledger_rows": 0}, structurally_complete=exit == 0)


def payload(end, exit=0):
    return event("payload-composed", end - 1, end, exit=exit, head=HEAD, target_kind="range")


class RunEventTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.count = 0

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, script, *args, code=0, cwd=None, stdin=None):
        result = subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)], cwd=cwd, input=stdin,
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result

    def summarize(self, events, *args, code=0, raw=None):
        self.count += 1
        path = self.root / f"{self.count}-events.jsonl"
        path.write_text(raw if raw is not None else "".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
        output = self.root / f"{self.count}-summary.json"
        result = self.cli("run_events.py", "summarize", path, "--output", output, *args, code=code)
        return json.loads(output.read_text(encoding="utf-8")), result

    def repository(self):
        repo = self.root / "repo"
        repo.mkdir()

        def git(*args):
            return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                                  encoding="utf-8", check=True).stdout.strip()
        git("init", "-q")
        git("config", "user.name", "Test")
        git("config", "user.email", "test@example.invalid")
        (repo / "a.py").write_text("x = 1\n", encoding="utf-8")
        git("add", ".")
        git("commit", "-qm", "base")
        base = git("rev-parse", "HEAD")
        (repo / "a.py").write_text("x = 2\n", encoding="utf-8")
        git("commit", "-qam", "change")
        return repo, base, git("rev-parse", "HEAD")

    def composition(self, base, head, status="Approved"):
        return {"run": {"head": head, "base_sha": base, "merge_base": base, "base_ref": "main",
                        "target_kind": "range", "target": "main..HEAD", "context": "9" * 64, "issues": [],
                        "coverage": "complete", "merged": False, "change_description": "change"},
                "summary": {"status": status, "intent": "Change x.", "issue_fit": "No issue; commit message only.",
                            "coverage": "Complete range diff inspected."}}

    def test_ordinary_run_records_each_seam(self):
        repo, base, head = self.repository()
        private = self.root / "private"
        private.mkdir()
        store = private / f"review-context-{head}.json"
        self.cli("review_context.py", "--merge-base", base, "--head", head, "--store", store, cwd=repo)
        cases = handoff.HandoffTests("test_batch_modes_initial_and_followup")
        cases.root, cases.count = self.root, 100
        cases.run_cli = lambda script, *args, code=0, scripts=SCRIPTS: self.cli(script, *args, code=code)
        cases.path = lambda suffix: private / f"{suffix}" if suffix == "bundle" else self.root / f"{id(object())}-{suffix}"
        bundle = cases.build()
        cases.account(bundle, cases.returned(bundle))
        composition = self.root / "composition.json"
        composition.write_text(json.dumps(self.composition(base, head, "Changes Requested")), encoding="utf-8")
        refused = self.cli("compose_review.py", "--store", store, composition, code=1)
        self.assertNotIn('"summary"', refused.stdout)
        composition.write_text(json.dumps(self.composition(base, head)), encoding="utf-8")
        composed = self.cli("compose_review.py", "--store", store, composition)
        self.assertEqual(composed.stderr, "")
        json.loads(composed.stdout)  # stdout is still exactly the payload

        events_path = private / "run-events.jsonl"
        self.assertEqual(stat.S_IMODE(events_path.stat().st_mode), 0o600)
        events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([e["event"] for e in events], ["context-built", "verifier-brief-built",
                                                         "verifier-return-accounted", "payload-composed",
                                                         "payload-composed"])
        self.assertEqual([e["exit"] for e in events], [0, 0, 0, 1, 0])
        self.assertEqual(events[0]["data"]["head"], head)
        self.assertEqual(events[0]["policy"]["workflow"], "v5b-17")
        self.assertEqual(events[2]["data"]["returned"], {"confirmed": 1, "refuted": 0, "holds": 0, "re_open": 0})
        self.assertEqual(events[4]["data"]["target_kind"], "range")

        summary_path, sidecar = self.root / "summary.json", self.root / "timing.json"
        self.cli("run_events.py", "summarize", events_path, "--output", summary_path,
                 "--completion-mode", "result", "--timing-sidecar", sidecar)
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertTrue(summary["complete"], summary["gaps"] + summary["violations"])
        self.assertEqual(summary["identity"]["reviewed_head"]["value"], head)
        self.assertEqual(summary["verification"]["batches"][0]["returned"]["confirmed"], 1)
        self.assertEqual(summary["script_failures"][0]["exit"], 1)
        timing = json.loads(sidecar.read_text(encoding="utf-8"))
        self.assertEqual(set(timing), {"completion_mode", "root_dispatched_at", "payload_validated_at", "completed_at"})
        self.assertIsNone(timing["root_dispatched_at"])
        self.assertEqual(timing["completed_at"], events[4]["ended_at"])

    def test_recording_failure_never_changes_a_result(self):
        repo, base, head = self.repository()
        outputs = []
        for broken in (False, True):
            private = self.root / f"private-{broken}"
            private.mkdir()
            if broken:
                (private / "run-events.jsonl").mkdir()  # the append cannot open a file
            store = private / "context.json"
            built = self.cli("review_context.py", "--merge-base", base, "--head", head, "--store", store, cwd=repo)
            composition = self.root / f"composition-{broken}.json"
            composition.write_text(json.dumps(self.composition(base, head)), encoding="utf-8")
            composed = self.cli("compose_review.py", "--store", store, composition)
            outputs.append((built.stdout.replace(str(store), "STORE"), composed.stdout, composed.stderr))
        self.assertEqual(outputs[0], outputs[1])
        # A composer that exits from inside main still records its failure.
        private = self.root / "private-True"
        (private / "run-events.jsonl").rmdir()
        corrupt = private / "corrupt.json"
        corrupt.write_text("{", encoding="utf-8")
        self.cli("compose_review.py", "--store", corrupt, self.root / "composition-True.json", code=2)
        self.cli("compose_review.py", "--store", store, self.root / "missing.json", code=2)
        failures = [json.loads(line) for line in (private / "run-events.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([(e["event"], e["exit"]) for e in failures], [("payload-composed", 2)] * 2)
        # Without --store there is no private directory and nothing is written.
        composition = self.root / "composition-False.json"
        self.cli("compose_review.py", composition)
        self.assertFalse((self.root / "run-events.jsonl").exists())

    def test_overlapping_batches_are_counted_once(self):
        summary, _ = self.summarize([context(), brief("one", 10), brief("two", 20), accounted("one", 40),
                                     accounted("two", 50), payload(60)], "--completion-mode", "result")
        verification = summary["verification"]
        self.assertEqual(verification["bracket_sum_seconds"]["seconds"], 60.0)
        self.assertEqual(verification["bracket_union_seconds"]["seconds"], 40.0)
        self.assertEqual(summary["durations"]["context_to_validated_payload"]["seconds"], 58.0)
        self.assertTrue(summary["complete"])

    def test_dispatch_to_join_is_a_bracket_not_a_wait(self):
        summary, _ = self.summarize([context(), brief("one", 10), accounted("one", 30), payload(35)],
                                    "--completion-mode", "result")
        bracket = summary["verification"]["batches"][0]["brief_to_accounting"]
        self.assertEqual((bracket["seconds"], bracket["status"]), (20.0, "proxy"))
        self.assertIn("not primary waiting time", bracket["basis"])
        self.assertIn("primary_idle_wait", summary["not_observed"])
        self.assertNotIn("primary_idle_wait", summary["durations"])
        self.assertEqual(summary["durations"]["last_accounting_to_validated_payload"]["status"], "proxy")

    def test_missing_boundaries_stay_unavailable(self):
        summary, _ = self.summarize([brief("one", 10)], "--completion-mode", "result")
        self.assertFalse(summary["complete"])
        self.assertIsNone(summary["boundaries"]["validated_payload_at"])
        self.assertIsNone(summary["durations"]["context_to_validated_payload"]["seconds"])
        self.assertIsNone(summary["verification"]["bracket_union_seconds"]["seconds"])
        self.assertTrue(any("no recorded accounting" in gap for gap in summary["gaps"]))
        self.assertTrue(any("no successful context build" in gap for gap in summary["gaps"]))
        empty, _ = self.summarize([], "--completion-mode", "result")
        self.assertEqual((empty["event_count"], empty["complete"]), (0, False))

    def test_invalid_and_out_of_order_boundaries(self):
        lines = "\n".join([json.dumps(context()), "{not json", json.dumps({"format": "other"}),
                           json.dumps(event("payload-composed", 9, 8))]) + "\n"
        summary, result = self.summarize(None, raw=lines, code=1)
        self.assertEqual([item["line"] for item in summary["invalid_lines"]], [2, 3, 4])
        self.assertEqual(len(result.stdout.splitlines()), 3)
        self.assertFalse(summary["complete"])

        summary, result = self.summarize([context(20), payload(10)], code=1)
        self.assertIn("ended_ns precedes", result.stdout)
        self.assertEqual(summary["clock"]["status"], "out-of-order")
        self.assertTrue(all(d["seconds"] is None for d in summary["durations"].values()))

        summary, result = self.summarize([context(), accounted("one", 5), brief("one", 30)], code=1)
        self.assertIn("accounted before its brief was built", result.stdout)
        self.assertIsNone(summary["verification"]["batches"][0]["brief_to_accounting"]["seconds"])

        summary, _ = self.summarize([context(), accounted("orphan", 5), payload(9)], "--completion-mode", "result")
        self.assertTrue(any("without a recorded brief" in gap for gap in summary["gaps"]))
        self.assertFalse(summary["complete"])

        # Accountings that failed before reading a manifest are never merged into one batch.
        summary, _ = self.summarize([context(), brief("one", 3), accounted("one", 4), accounted(None, 5, exit=1),
                                     accounted(None, 6, exit=1), payload(9)], "--completion-mode", "result")
        self.assertEqual(summary["verification"]["batches_recorded"], 1)
        self.assertEqual(sum("no batch identity" in gap for gap in summary["gaps"]), 2)
        self.assertEqual(len(summary["script_failures"]), 2)

    def test_clock_domains_are_never_mixed(self):
        other = dict(DOMAIN, boot="rebooted")
        summary, _ = self.summarize([context(), event("payload-composed", 3, 4, clock=other, head=HEAD)],
                                    "--completion-mode", "result")
        self.assertEqual(summary["clock"]["status"], "mixed")
        self.assertIsNone(summary["durations"]["context_to_validated_payload"]["seconds"])
        self.assertIsNotNone(summary["boundaries"]["validated_payload_at"])
        unknown = dict(DOMAIN, boot=None)
        summary, _ = self.summarize([event("context-built", 1, 2, clock=unknown, head=HEAD)])
        self.assertEqual(summary["clock"]["status"], "unknown")
        self.assertIsNone(summary["durations"]["context_build"]["seconds"])

    def test_failure_and_cancellation(self):
        summary, _ = self.summarize([context(), brief("one", 10), payload(20, exit=1)], "--completion-mode", "result")
        self.assertIsNone(summary["boundaries"]["validated_payload_at"])
        self.assertEqual(summary["boundaries"]["final_result"]["status"], "unavailable")
        self.assertEqual([f["exit"] for f in summary["script_failures"]], [1])
        self.assertFalse(summary["complete"])
        summary, _ = self.summarize([context(), brief("one", 10), accounted("one", 20, exit=1), payload(30)],
                                    "--completion-mode", "result")
        self.assertTrue(summary["complete"], summary["gaps"])  # a structurally incomplete return is still joined
        self.assertFalse(summary["verification"]["batches"][0]["structurally_complete"])

    def test_completion_modes(self):
        events = [context(), payload(12)]
        for mode, completed in (("render-only", True), ("result", True), ("publication", False)):
            with self.subTest(mode=mode):
                self.count += 1
                sidecar = self.root / f"{self.count}-timing.json"
                summary, _ = self.summarize(events, "--completion-mode", mode, "--timing-sidecar", sidecar)
                timing = json.loads(sidecar.read_text(encoding="utf-8"))
                self.assertEqual(timing["payload_validated_at"], events[1]["ended_at"])
                self.assertEqual(timing["completed_at"], events[1]["ended_at"] if completed else None)
                self.assertEqual(summary["complete"], completed)
        summary, _ = self.summarize(events)
        self.assertIn("completion mode not supplied", summary["gaps"])
        self.cli("run_events.py", "summarize", self.root / "1-events.jsonl", "--output", self.root / "x.json",
                 "--timing-sidecar", self.root / "y.json", code=2)
        self.cli("run_events.py", "summarize", self.root / "1-events.jsonl", "--output", self.root / "1-summary.json",
                 code=2)
        self.cli("run_events.py", "summarize", self.root / "missing.jsonl", "--output", self.root / "z.json", code=2)

    def test_absent_billing_is_null_not_zero(self):
        summary, _ = self.summarize([context(), payload(4)], "--completion-mode", "result")
        usage = summary["usage"]
        self.assertEqual(usage["status"], "unavailable")
        self.assertTrue(all(usage[key] is None for key in ("input_tokens", "cache_write_tokens",
                                                            "cache_read_tokens", "output_tokens", "cost")))

    def test_empty_ledger_is_an_explicit_zero(self):
        unknown = brief("three", 30, mode="related-acquittal")
        unknown["data"]["ledger_rows"] = None
        summary, _ = self.summarize([context(), brief("one", 10, "complete-ledger", 0, 0), accounted("one", 11),
                                     brief("two", 20, "complete-ledger", 0, 4), accounted("two", 21),
                                     unknown, accounted("three", 31), payload(40)], "--completion-mode", "result")
        verification = summary["verification"]
        self.assertEqual(verification["complete_ledger_zero_rows"], 1)
        self.assertEqual(verification["complete_ledger_nonzero_rows"], 1)
        self.assertEqual(verification["ledger_rows_unknown"], 1)
        self.assertEqual(verification["batches"][0]["ledger_rows"], 0)

    def test_mixed_heads_are_a_violation(self):
        other = payload(10)
        other["data"]["head"] = "b" * 40
        summary, result = self.summarize([context(), other], code=1)
        self.assertIn("more than one reviewed head", result.stdout)
        self.assertIsNone(summary["identity"]["reviewed_head"]["value"])


if __name__ == "__main__":
    os.chdir(SCRIPTS)
    unittest.main()
