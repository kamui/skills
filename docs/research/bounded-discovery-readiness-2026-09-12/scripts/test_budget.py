#!/usr/bin/env python3
"""Exercise prospective stop semantics and inherited budget gates through CLIs.

Usage: python3 scripts/test_budget.py
Input: disposable synthetic ledgers only. Exit: 0 pass, 1 test failures.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import budget

HERE = Path(__file__).resolve().parent
OLD = HERE.parents[1] / "bounded-discovery-prototype" / "scripts"
sys.path.insert(0, str(OLD))
spec = importlib.util.spec_from_file_location("original_tests", OLD / "test_adapter.py")
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
original_cli = original.cli


def cli(script, *args):
    if script == "budget.py":
        return subprocess.run([sys.executable, str(HERE / script), *map(str, args)],
                              capture_output=True, text=True, encoding="utf-8", timeout=30)
    return original_cli(script, *args)


original.cli = cli
original.attempt_event = budget.attempt_event


class StopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ledger.json"
        raw = json.loads((OLD.parent / "ledger.json").read_text(encoding="utf-8"))
        raw = original.opening_state(raw)
        raw.update(frozen_total_cap_usd="100", grading_closeout_reserve_usd="10")
        self.path.write_text(json.dumps(raw), encoding="utf-8")

    def call(self, *args, expected=0):
        result = cli("budget.py", self.path, *args)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def stop(self):
        return self.call("stop", "--reason", "toy runtime unavailable", "--ticket", "199",
                         "--evidence", "synthetic-handoff.json")

    def read(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def test_stop_retains_money_and_history_then_settles(self):
        self.call("reserve", "--id", "running", "--amount", "5", "--evidence", "launch")
        before = self.read()
        event = json.loads(self.stop().stdout)
        after = self.read()
        self.assertEqual(after["events"][:-1], before["events"])
        self.assertEqual(after["reserved_usd"], before["reserved_usd"])
        self.assertEqual(event["ticket"], 199)
        self.assertEqual(event["previous_event_id"], before["events"][-1]["event_id"])
        self.call("settle", "--id", "running", "--amount", "2", "--uncertainty", "1",
                  "--evidence", "usage")
        self.assertEqual(self.read()["actual_usd"], "2.00")
        self.assertEqual(self.read()["uncertainty_usd"], "1.00")
        self.assertEqual(self.read()["events"][-2], event)

    def test_stop_refuses_restart_but_allows_protected_closeout(self):
        attempt = dict(attempt_id="a", cell_id="cell", contexts={"primary": "ctx"},
                       predecessor=None, replacement_ordinal=0)
        budget.attempt_event(self.path, attempt)
        self.stop()
        before = self.path.read_bytes()
        for phase in ("pre-freeze", "review"):
            self.call("reserve", "--id", "new", "--amount", "1", "--phase", phase,
                      "--evidence", "launch", expected=1)
        self.call("stop", "--reason", "replace", "--evidence", "new", "--ticket", "199", expected=1)
        self.call("cap-freeze", "--amount", "99", "--reserve", "10", "--evidence", "freeze", expected=1)
        with self.assertRaises(budget.Violation):
            budget.attempt_event(self.path, dict(attempt, attempt_id="b", cell_id="other"))
        self.assertEqual(self.path.read_bytes(), before)
        budget.attempt_event(self.path, attempt, close="stopped-runtime")
        self.call("reserve", "--id", "grade", "--amount", "2", "--phase", "grading", "--evidence", "grade")
        self.call("settle", "--id", "grade", "--amount", "1", "--evidence", "usage")

    def test_missing_evidence_and_unreadable_input_exit_codes(self):
        self.call("stop", "--reason", "x", expected=2)
        self.call("stop", "--reason", " ", "--evidence", "x", "--ticket", "199", expected=1)
        self.path.unlink()
        self.call("stop", "--reason", "x", "--evidence", "x", "--ticket", "199", expected=2)

    def test_stop_before_freeze_does_not_release_pre_freeze_reservation(self):
        raw = self.read()
        raw.update(frozen_total_cap_usd=None, grading_closeout_reserve_usd=None)
        self.path.write_text(json.dumps(raw), encoding="utf-8")
        self.call("reserve", "--id", "probe", "--amount", "2", "--phase", "pre-freeze", "--evidence", "probe")
        self.stop()
        self.call("cap-freeze", "--amount", "100", "--reserve", "10", "--evidence", "freeze", expected=1)
        self.call("settle", "--id", "probe", "--amount", "1", "--evidence", "usage")
        self.assertEqual(self.read()["reserved_usd"], "0.00")

    def test_concurrent_stops_append_exactly_once(self):
        def stop_once(_):
            return cli("budget.py", self.path, "stop", "--reason", "done", "--evidence", "handoff", "--ticket", "199")
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(stop_once, range(2)))
        self.assertEqual(sorted(result.returncode for result in results), [0, 1])
        self.assertEqual(sum(e["operation"] == "stop" for e in self.read()["events"]), 1)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(StopTests)
    for name in ("test_atomic_budget_reservations_and_settlements",
                 "test_phase_attempt_caps_corruption_and_attempt_identity",
                 "test_pre_freeze_unfrozen_ledger", "test_malformed_reservation_delta_closes_out",
                 "test_attempt_replacement_and_concurrency_caps"):
        suite.addTest(original.AdapterTests(name))
    sys.exit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
