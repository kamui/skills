#!/usr/bin/env python3
"""Exercise adapter, fake tool and budget boundaries through their CLIs.

Usage: python3 scripts/test_adapter.py
Input: disposable synthetic fixtures; no provider requests or repository writes.
Exit: 0 all checks pass, 1 assertions fail.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from fixtures import CASES
from adapter import HERE, artifact
from budget import attempt_event


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def cli(script, *args):
    return subprocess.run([sys.executable, str(HERE / script), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8", timeout=90)


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.serial = 0

    def fixture(self, case="empty", arm="C"):
        self.serial += 1
        root = self.root / str(self.serial)
        result = cli("fixtures.py", "--out", root, "--case", case, "--arm", arm)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return root

    def run_cell(self, root, rc=0, runtime="fake", output="run"):
        result = cli("adapter.py", "--config", root / "config.json", "--scenario", root / "scenario.json",
                     "--out", root / output, "--runtime", runtime)
        self.assertEqual(result.returncode, rc, result.stdout + result.stderr)
        return read(root / output / "attempt.json"), read(root / output / "handoff.json")

    def test_transition_table(self):
        for case in CASES:
            with self.subTest(case=case):
                root = self.fixture(case)
                stopped = case in ("missing-finder", "malformed", "timeout")
                attempt, handoff = self.run_cell(root, 1 if stopped else 0)
                self.assertEqual(len(handoff["unattempted_cells"]), 23)
                self.assertFalse(handoff["dispatch_authorized"])
                self.assertLessEqual(len(attempt["batches"]), 2)
                if stopped:
                    self.assertIsNone(attempt["final_payload"])
                    self.assertTrue((root / "run/stop.json").exists())
                    self.assertIsNone(read(root / "run/timing.json")["completed_at"])
                else:
                    self.assertIsNotNone(attempt["final_payload"])
                    self.assertTrue(read(root / "run/timing.json")["completed_at"])
                if case == "missing-dispatch":
                    self.assertEqual(attempt["gaps"][0]["kind"], "missing-required-dispatch")
                if case == "missing-ruling":
                    self.assertEqual(attempt["gaps"][0]["kind"], "missing-required-ruling")
                if case in ("finder", "primary", "duplicate", "outside"):
                    self.assertEqual(len(attempt["batches"]), 1)
                    self.assertEqual(attempt["batches"][0]["decision"]["candidate_ids"], ["C1"])
                if case == "outside":
                    self.assertEqual(attempt["batches"][0]["packet"]["candidates"][0]["anchor"], "queue.rs:3")
                if case in ("refuted", "unresolved"):
                    self.assertEqual(attempt["batches"][1]["decision"]["mode"], "clean-verdict")
                    self.assertIn("R-C1", attempt["batches"][1]["decision"]["row_ids"])
                if case == "late-row":
                    self.assertEqual(attempt["batches"][1]["decision"]["candidate_ids"], [])
                    self.assertEqual(attempt["batches"][1]["decision"]["row_ids"], ["Q1"])
                if case == "spent-follow-up":
                    self.assertEqual(attempt["gaps"][0]["kind"], "required-unavailable-at-cap")

    def test_barrier_freshness_compact_packets_and_actual_tool_reads(self):
        root = self.fixture("duplicate")
        attempt, _ = self.run_cell(root)
        events = attempt["events"]
        release = next(i for i, e in enumerate(events) if e["kind"] == "cross-feed")
        freezes = [i for i, e in enumerate(events) if e["kind"] == "freeze" and e["phase"] == "discovery"]
        self.assertEqual(len(freezes), 2)
        self.assertTrue(all(i < release for i in freezes))
        verifier = next(i for i, e in enumerate(events) if e["kind"] == "worker-start" and e["context_id"] == "toy-initial-verifier")
        self.assertGreater(verifier, release)
        packet = read(root / "run/toy-initial-verifier/verification-input.json")
        for prohibited in ("support", "origin", "sources", "dedup_decision", "PRIVATE SUPPORT"):
            self.assertNotIn(prohibited, json.dumps({"candidates": packet["candidates"], "rows": packet["rows"]}))
        self.assertNotIn("PRIVATE SUPPORT", json.dumps(packet))
        transcript = root / "run/toy-finder/toy-finder-discovery-0.jsonl"
        records = [json.loads(line) for line in transcript.read_text(encoding="utf-8").splitlines()]
        results = [r["result"] for r in records if r["type"] == "tool-result"]
        self.assertEqual(results[0]["status"], "read")
        self.assertEqual([r["status"] for r in results[1:]], ["denied"] * 6)
        self.assertNotIn("SECRET CANARY", transcript.read_text(encoding="utf-8"))
        # Verifier read tools can inspect outside the finder frontier.
        direct = dict(packet={}, response=dict(tools=[dict(name="read", path=str(root / "inputs/clone/queue.rs"), start=3, end=3)],
                      report=dict(complete=True)), read_roots=[str(root / "inputs/clone")], ranges=None,
                      requested=dict(model="fixture", effort="high"), request_id="outside")
        result = subprocess.run([sys.executable, str(HERE / "fake_worker.py")], input=json.dumps(direct),
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0)
        self.assertIn("fn outside()", result.stdout)

    def test_pinned_omission_and_evidence_states_across_arms(self):
        for arm in "ABC":
            for case in ("hygiene", "generic", "concrete", "unavailable", "unknown", "not-inspected"):
                with self.subTest(arm=arm, case=case):
                    root = self.fixture(case, arm)
                    attempt, _ = self.run_cell(root)
                    self.assertEqual(attempt["batches"], [])
                    self.assertEqual(attempt["gaps"], [])
                    if arm != "C":
                        self.assertNotIn("finder", attempt["workers"])
                        self.assertFalse(any(e["kind"] == "cross-feed" for e in attempt["events"]))
                    initial = next(e for e in attempt["events"] if e["kind"] == "no-batch")
                    self.assertEqual(initial["decision"]["reason"], "policy-permitted-omission")
                    if case != "hygiene":
                        t = read(root / "run/final-stages.json")["claims"][1]
                        self.assertEqual(t["admission"]["disposition"], "rejected")
                        self.assertEqual(t["verification"]["disposition"], "not-required-policy")
                        self.assertEqual(t["inspected_evidence"][0]["availability"],
                                         case if case in ("unavailable", "unknown", "not-inspected") else "inspected")
                        self.assertTrue(t["safety_premise"])
                    outcome = read(root / "run/outcome-join.json")
                    self.assertIsNone(outcome["recovered"])
                    self.assertEqual(outcome["sufficient_outcome"], "unknown")

    def test_config_boundaries_and_no_cell_stops(self):
        mutations = [
            lambda c: c.update(arm="D"),
            lambda c: c.update(skill_tree="0" * 40),
            lambda c: c["source"].update(sha256="0" * 64),
            lambda c: c["contexts"].update({"initial-verifier": c["contexts"]["finder"]}),
            lambda c: c["workers"]["C"].update(effort="medium"),
            lambda c: c["limits"].update(wall_seconds=None),
            lambda c: c["limits"].update(commands=-1),
            lambda c: c.update(clone_root="/"),
            lambda c: c.update(isolation="prompt-only"),
            lambda c: c.update(completion_mode="publication"),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutations.index(mutate)):
                root = self.fixture()
                config = read(root / "config.json")
                mutate(config)
                save(root / "config.json", config)
                attempt, handoff = self.run_cell(root, 1)
                self.assertIsNone(attempt["attempt_id"])
                self.assertEqual(len(handoff["unattempted_cells"]), 24)
        root = self.fixture()
        attempt, handoff = self.run_cell(root, 1, "claude")
        self.assertEqual(handoff["disposition"], "stopped-runtime")
        self.assertIsNone(attempt["attempt_id"])
        self.assertEqual(handoff["actual_usd"], "0.00")

    def test_streams_settings_usage_and_continuations(self):
        for field in ("model", "effort"):
            for value in ("wrong", None):
                root = self.fixture()
                scenario = read(root / "scenario.json")
                observed = dict(model="fixture-primary", effort="high")
                observed[field] = value
                scenario["primary"]["discovery"]["observed"] = observed
                save(root / "scenario.json", scenario)
                attempt, _ = self.run_cell(root, 1)
                settings = [e for e in attempt["events"] if e["kind"] == "observed-settings" and e["context_id"] == "toy-primary"]
                self.assertEqual(settings[0]["state"], "unavailable" if value is None else "mismatched")
        root = self.fixture("primary")
        scenario = read(root / "scenario.json")
        response = scenario["primary"]["reconcile"]
        scenario["primary"]["reconcile"] = dict(requests=[deepcopy(response), response])
        save(root / "scenario.json", scenario)
        attempt, _ = self.run_cell(root)
        requests = attempt["workers"]["primary"]["requests"]
        self.assertEqual(len(requests), 5)
        self.assertTrue(all("meter" in r for r in requests))
        root = self.fixture("malformed")
        _, handoff = self.run_cell(root, 1)
        self.assertGreater(float(handoff["reserved_usd"]), 0)

    def test_payload_changes_missing_rulings_and_immutable_output(self):
        root = self.fixture("primary")
        scenario = read(root / "scenario.json")
        scenario["primary"]["final"]["report"]["claims"][0]["change"] = "A different unverified change"
        save(root / "scenario.json", scenario)
        self.run_cell(root, 1)
        root = self.fixture("primary")
        self.run_cell(root)
        manifest = read(root / "run/manifest.json")
        for name, sha in manifest.items():
            self.assertEqual(hashlib.sha256((root / "run" / name).read_bytes()).hexdigest(), sha)
        result = cli("adapter.py", "--config", root / "config.json", "--scenario", root / "scenario.json", "--out", root / "run")
        self.assertEqual(result.returncode, 2)
        for name, sha in manifest.items():
            self.assertEqual(hashlib.sha256((root / "run" / name).read_bytes()).hexdigest(), sha)

    def test_atomic_budget_reservations_and_settlements(self):
        root = self.fixture()
        ledger = root / "ledger.json"
        data = read(ledger)
        data.update(frozen_total_cap_usd="2", grading_closeout_reserve_usd="1")
        save(ledger, data)
        def reserve(rid, amount="0.7", phase="review", extra=()):
            return cli("budget.py", ledger, "reserve", "--id", rid, "--amount", amount,
                       "--phase", phase, "--evidence", "synthetic-request-bound", *extra)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(reserve, ("one", "two")))
        self.assertEqual(sorted(r.returncode for r in results), [0, 1])
        successful = json.loads(next(r.stdout for r in results if r.returncode == 0))["reservation_id"]
        result = cli("budget.py", ledger, "settle", "--id", successful, "--amount", "0.2", "--uncertainty", "0.1", "--evidence", "retained-usage")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(float(read(ledger)["uncertainty_usd"]), 0.1)
        self.assertEqual(reserve("too-large", "0.8").returncode, 1)
        self.assertEqual(reserve("close", "1", "closeout").returncode, 0)
        self.assertEqual(reserve("close-again", "0.1", "closeout").returncode, 1)
        self.assertEqual(cli("budget.py", ledger, "settle", "--id", successful, "--amount", "0", "--evidence", "duplicate").returncode, 1)

    def test_phase_attempt_caps_corruption_and_attempt_identity(self):
        root = self.fixture()
        ledger = root / "ledger.json"
        args = ("--phase", "pre-freeze", "--evidence", "probe")
        self.assertEqual(cli("budget.py", ledger, "reserve", "--id", "first", "--amount", "10", *args).returncode, 0)
        self.assertEqual(cli("budget.py", ledger, "reserve", "--id", "second", "--amount", "6", *args).returncode, 1)
        self.assertEqual(cli("budget.py", ledger, "reserve", "--id", "worker", "--amount", "2",
                             "--attempt", "a", "--attempt-cap", "1", "--evidence", "bound").returncode, 1)
        data = read(ledger)
        data["actual_usd"] = "1"
        save(ledger, data)
        self.assertEqual(cli("budget.py", ledger, "reserve", "--id", "corrupt", "--amount", "1", *args).returncode, 1)
        root = self.fixture()
        self.run_cell(root)
        attempt, handoff = self.run_cell(root, 1, output="second-run")
        self.assertIsNone(attempt["attempt_id"])
        self.assertIn("already used", handoff["reason"])

    def test_numeric_limits_and_forbidden_worker_restarts(self):
        for key, value in (("requests", 1), ("commands", 1), ("tokens", 1000), ("finder_tokens", 1), ("attempt_usd", "0.1")):
            root = self.fixture()
            config = read(root / "config.json")
            config["limits"][key] = value
            save(root / "config.json", config)
            _, handoff = self.run_cell(root, 1)
            self.assertEqual(handoff["disposition"], "stopped-budget", handoff["reason"])
        for role, phase in (("finder", "verification"), ("third-verifier", "verification")):
            root = self.fixture()
            scenario = read(root / "scenario.json")
            scenario.setdefault(role, {})[phase] = dict(report=dict(complete=True))
            save(root / "scenario.json", scenario)
            attempt, _ = self.run_cell(root, 1)
            self.assertIsNone(attempt["attempt_id"])

    def test_attempt_replacement_and_concurrency_caps(self):
        root = self.fixture()
        config = read(root / "config.json")
        ledger = root / "ledger.json"
        # Seed prior operational history mechanically; dispatch remains through the CLI.
        for index in range(27):
            previous = deepcopy(config)
            previous.update(attempt_id="prior-" + str(index), cell_id="prior-cell-" + str(index))
            previous["contexts"] = {r: c + "-" + str(index) for r, c in previous["contexts"].items()}
            attempt_event(ledger, previous)
            attempt_event(ledger, previous, "stopped-invalid")
        _, handoff = self.run_cell(root, 1)
        self.assertIn("attempt or simultaneous cell cap", handoff["reason"])
        root = self.fixture()
        config = read(root / "config.json")
        ledger = root / "ledger.json"
        for index in range(2):
            previous = deepcopy(config)
            previous.update(attempt_id="active-" + str(index), cell_id="active-cell-" + str(index))
            previous["contexts"] = {r: c + "-" + str(index) for r, c in previous["contexts"].items()}
            attempt_event(ledger, previous)
        _, handoff = self.run_cell(root, 1)
        self.assertIn("attempt or simultaneous cell cap", handoff["reason"])
        root = self.fixture()
        config = read(root / "config.json")
        ledger = root / "ledger.json"
        for index in range(4):
            previous = deepcopy(config)
            previous.update(attempt_id="replace-" + str(index), replacement_ordinal=index,
                            predecessor="replace-" + str(index - 1) if index else None,
                            replacement_evidence="Synthetic protocol failure")
            previous["contexts"] = {r: c + "-" + str(index) for r, c in previous["contexts"].items()}
            attempt_event(ledger, previous)
            attempt_event(ledger, previous, "stopped-invalid")
        config.update(predecessor="replace-3", replacement_ordinal=4, replacement_evidence="Synthetic invalidity")
        save(root / "config.json", config)
        _, handoff = self.run_cell(root, 1)
        self.assertIn("replacement cap", handoff["reason"])

    def test_scope_target_and_pinned_helper_integrity(self):
        for name, mutate in (
                ("target", lambda d: d.update(head_oid="0" * 40)),
                ("source", lambda d: d.pop("merged")),
                ("scope", lambda d: d.update(max_hops=3)),
                ("scope", lambda d: d["roots"][0].update(path="../../hidden-truth/canary.txt"))):
            root = self.fixture()
            config = read(root / "config.json")
            path = Path(config[name]["uri"])
            data = read(path)
            mutate(data)
            save(path, data)
            config[name] = artifact(path, config[name]["access"])
            save(root / "config.json", config)
            attempt, _ = self.run_cell(root, 1)
            self.assertIsNone(attempt["attempt_id"])
        root = self.fixture()
        config = read(root / "config.json")
        path = Path(config["helpers"]["validate_review"]["uri"])
        path.write_text("print('not the validator')\n", encoding="utf-8")
        config["helpers"]["validate_review"] = artifact(path)
        save(root / "config.json", config)
        _, handoff = self.run_cell(root, 1)
        self.assertIn("not the pinned policy helper", handoff["reason"])


if __name__ == "__main__":
    unittest.main()
