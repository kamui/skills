#!/usr/bin/env python3
"""Drive the complete shutdown gate through its CLI, clearing and refusing.

Usage: python3 scripts/test_shutdown.py
Input: synthetic ledgers, synthetic probe captures and temporary directories
only; no study, provider session or container is launched, and no historical
seal is opened. Exit: 0 pass, 1 test failures.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import shutdown

SCRIPT = str(Path(shutdown.__file__).resolve())
HERE = Path(__file__).resolve().parent
PROTOTYPE = HERE.parents[1] / "bounded-discovery-prototype"
sys.path.insert(0, str(PROTOTYPE / "scripts"))
from fixtures import opening_state  # noqa: E402  (loaded from the pinned prototype)


def stamp(offset_seconds=0) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=offset_seconds)).isoformat()


def probe(stdout="", exit_code=0, ran=True, timed_out=False, stderr="", command=("ps",)):
    return {"command": list(command), "exit_code": exit_code, "stdout": stdout,
            "stderr": stderr, "ran": ran, "timed_out": timed_out}


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.cells = self.base / "cells"
        self.cells.mkdir()
        self.seal = self.base / "sealed"
        self.seal.mkdir()
        self.record = self.base / "roots.json"
        self.gate = self.base / "gate.json"
        self.probes_file = self.base / "probes.json"
        self.ledger = self.base / "ledger.json"
        self.build_ledger()
        self.roots_record()

    # -- fixtures ---------------------------------------------------------

    def budget(self, *args, expected=0):
        result = subprocess.run([sys.executable, str(HERE / "budget.py"), str(self.ledger),
                                 *map(str, args)], capture_output=True, text=True,
                                encoding="utf-8", timeout=60)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def build_ledger(self):
        """A synthetic study ledger, built through the prospective budget CLI."""
        import importlib.util

        raw = opening_state(json.loads((PROTOTYPE / "ledger.json").read_text(encoding="utf-8")))
        raw.update(frozen_total_cap_usd="100", grading_closeout_reserve_usd="10")
        self.ledger.write_text(json.dumps(raw), encoding="utf-8")
        spec = importlib.util.spec_from_file_location("bd_budget", HERE / "budget.py")
        budget = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(budget)
        attempt = dict(attempt_id="attempt-1", cell_id="cell-1",
                       contexts={"primary": "ctx-primary"}, predecessor=None,
                       replacement_ordinal=0)
        budget.attempt_event(self.ledger, attempt)
        self.budget("reserve", "--id", "attempt-1-reservation", "--amount", "9",
                    "--attempt", "attempt-1", "--attempt-cap", "9", "--evidence", "launch")
        self.budget("settle", "--id", "attempt-1-reservation", "--amount", "4",
                    "--evidence", "usage")
        budget.attempt_event(self.ledger, attempt, close="complete")
        self.budget("stop", "--reason", "the grid finished", "--ticket", "199",
                    "--evidence", "synthetic-handoff.json")

    def roots_record(self):
        result = subprocess.run([sys.executable, str(HERE / "roots.py"), "record", "--out",
                                 str(self.record), "--root", str(self.cells)],
                                capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.pinned = hashlib.sha256(self.record.read_bytes()).hexdigest()

    def write_probes(self, processes=None, containers=None, captured_at=None):
        document = {"captured_at": captured_at or stamp(),
                    "self_pid": os.getpid(),
                    "processes": processes if processes is not None else probe(),
                    "containers": containers if containers is not None
                    else probe(command=("docker", "ps"))}
        self.probes_file.write_text(json.dumps(document), encoding="utf-8")
        return self.probes_file

    def check(self, *extra, expected=0, roots_sha256=None, remove_root=True):
        if remove_root and self.cells.exists():
            self.cells.rmdir()
        if not self.probes_file.exists():
            self.write_probes()
        args = ["check", "--ledger", self.ledger, "--roots-record", self.record,
                "--roots-sha256", roots_sha256 or self.pinned, "--seal", self.seal,
                "--out", self.gate, "--probes-from", self.probes_file, *extra]
        result = subprocess.run([sys.executable, SCRIPT, *map(str, args)],
                                capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(result.returncode, expected,
                         "argv=%s\n%s%s" % (args, result.stdout, result.stderr))
        return result

    def recorded_root(self):
        return json.loads(self.record.read_text(encoding="utf-8"))["roots"][0]

    def gate_record(self):
        return json.loads(self.gate.read_text(encoding="utf-8"))

    def assert_blocked(self, result, check_name, fragment):
        record = self.gate_record()
        self.assertFalse(record["seal_may_be_opened"])
        self.assertIn(check_name, record["blocking"])
        entry = next(c for c in record["checks"] if c["check"] == check_name)
        self.assertIn(fragment, entry["detail"])
        self.assertIn(check_name, result.stdout)
        return entry

    # -- the clearing case ------------------------------------------------

    def test_a_complete_gate_clears_and_authorizes_the_seal(self):
        self.check()
        record = self.gate_record()
        self.assertTrue(record["seal_may_be_opened"])
        self.assertEqual(record["blocking"], [])
        self.assertEqual(sorted(c["check"] for c in record["checks"]),
                         sorted(shutdown.CHECKS))
        self.assertTrue(all(c["class"] == "required" for c in record["checks"]))
        self.assertTrue(all(c["established"] for c in record["checks"]))
        self.assertNotIn(self.recorded_root(),
                         json.dumps([c["detail"] for c in record["checks"]]))
        self.authorize(expected=0)
        self.authorize("--max-age-seconds", "3600", expected=0)

    def authorize(self, *extra, expected=0, gate=None):
        args = ["authorize", "--gate", gate or self.gate, *extra]
        result = subprocess.run([sys.executable, SCRIPT, *map(str, args)],
                                capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    # -- the recorded root ------------------------------------------------

    def test_a_record_that_is_not_the_pinned_one_blocks(self):
        result = self.check(roots_sha256="f" * 64, expected=1)
        self.assert_blocked(result, shutdown.CHECKS[0], "not the pinned")

    def test_a_record_inside_the_seal_establishes_nothing(self):
        inside = self.seal / "roots.json"
        inside.write_bytes(self.record.read_bytes())
        self.record = inside
        self.pinned = hashlib.sha256(inside.read_bytes()).hexdigest()
        result = self.check(expected=1)
        self.assert_blocked(result, shutdown.CHECKS[1], "inside the seal")

    def test_a_surviving_root_blocks_even_as_a_dangling_symlink(self):
        result = self.check(expected=1, remove_root=False)
        self.assert_blocked(result, shutdown.CHECKS[2], "1 recorded cell root(s) survive")
        self.cells.rmdir()
        self.cells.symlink_to(self.base / "gone")
        result = self.check(expected=1, remove_root=False)
        self.assert_blocked(result, shutdown.CHECKS[2], "survive")

    def test_an_unreadable_parent_is_an_incomplete_probe(self):
        document = json.loads(self.record.read_text(encoding="utf-8"))
        document["roots"] = [str(self.base / "vanished" / "cells")]
        self.record.write_text(json.dumps(document), encoding="utf-8")
        self.pinned = hashlib.sha256(self.record.read_bytes()).hexdigest()
        result = self.check(expected=1)
        entry = self.assert_blocked(result, shutdown.CHECKS[2], "could not be enumerated")
        self.assertFalse(entry["probe_completed"])

    def test_an_unreadable_record_blocks_every_root_check(self):
        self.record.unlink()
        result = self.check(expected=1)
        for name in shutdown.CHECKS[:3]:
            self.assertIn(name, self.gate_record()["blocking"])
        self.assertIn("could not be read", result.stdout)

    # -- the process probe ------------------------------------------------

    def test_a_live_reviewer_process_blocks_and_this_gate_does_not_match_itself(self):
        self.write_probes(processes=probe(
            stdout="4321 1 docker run --name bd-position-01-primary-phase-1 anthropic/cell\n"))
        result = self.check(expected=1)
        entry = self.assert_blocked(result, shutdown.CHECKS[3], "still name a reviewer run")
        self.assertEqual(entry["match_count"], 1)
        self.write_probes(processes=probe(
            stdout="%d 1 sh -c python3 shutdown.py check --roots-record %s # %s\n"
                   % (os.getpid(), self.record, self.recorded_root())))
        self.check()
        entry = next(c for c in self.gate_record()["checks"] if c["check"] == shutdown.CHECKS[3])
        self.assertEqual(entry["match_count"], 0)
        self.assertEqual(entry["own_ancestry_match_count"], 1)

    def test_a_missing_timed_out_or_failed_process_probe_establishes_nothing(self):
        for capture, fragment in (
                (probe(ran=False, exit_code=None, stderr="command not found"),
                 "did not run (command not found)"),
                (probe(ran=False, exit_code=None, timed_out=True), "timed out"),
                (probe(exit_code=1, stderr="ps: permission denied"), "exited 1")):
            self.write_probes(processes=capture)
            result = self.check(expected=1, remove_root=False)
            entry = self.assert_blocked(result, shutdown.CHECKS[3], fragment)
            self.assertFalse(entry["probe_completed"])

    # -- the container probe ----------------------------------------------

    def test_an_unreachable_runtime_is_not_a_clearance(self):
        self.write_probes(containers=probe(
            exit_code=1, stderr="Cannot connect to the Docker daemon at unix:///var/run/docker.sock",
            command=("docker", "ps")))
        result = self.check(expected=1)
        entry = self.assert_blocked(result, shutdown.CHECKS[4],
                                    "An unreachable runtime establishes nothing")
        self.assertFalse(entry["probe_completed"])

    def test_a_surviving_container_and_a_missing_runtime_both_block(self):
        self.write_probes(containers=probe(
            stdout="bd-position-01-primary-phase-1\tUp 3 minutes\n", command=("docker", "ps")))
        result = self.check(expected=1)
        self.assert_blocked(result, shutdown.CHECKS[4], "1 cell container(s) are still present")
        self.write_probes(containers=probe(ran=False, exit_code=None,
                                           stderr="command not found", command=("docker", "ps")))
        result = self.check(expected=1, remove_root=False)
        self.assert_blocked(result, shutdown.CHECKS[4], "command not found")

    def test_the_container_prefix_selects_what_counts(self):
        self.write_probes(containers=probe(stdout="unrelated-build\tExited (0)\n",
                                           command=("docker", "ps")))
        self.check()
        self.write_probes(containers=probe(stdout="study7-cell-1\tUp 2 seconds\n",
                                           command=("docker", "ps")))
        result = self.check("--container-prefix", "study7", expected=1,
                            remove_root=False)
        self.assert_blocked(result, shutdown.CHECKS[4], "1 cell container(s)")

    # -- the ledger -------------------------------------------------------

    def test_an_outstanding_reservation_blocks(self):
        self.budget("reserve", "--id", "closeout-reservation", "--amount", "2",
                    "--phase", "closeout", "--evidence", "closeout")
        result = self.check(expected=1)
        self.assert_blocked(result, shutdown.CHECKS[6], "reservation deltas sum to 2")

    def test_a_ledger_without_a_terminal_stop_blocks(self):
        document = json.loads(self.ledger.read_text(encoding="utf-8"))
        document["events"] = [e for e in document["events"] if e["operation"] != "stop"]
        self.ledger.write_text(json.dumps(document), encoding="utf-8")
        result = self.check(expected=1)
        self.assert_blocked(result, shutdown.CHECKS[8], "carries 0 stop events")

    def test_an_unclosed_attempt_and_a_broken_chain_block(self):
        document = json.loads(self.ledger.read_text(encoding="utf-8"))
        document["events"] = [e for e in document["events"]
                              if e["operation"] != "attempt-close"]
        self.ledger.write_text(json.dumps(document), encoding="utf-8")
        result = self.check(expected=1)
        self.assert_blocked(result, shutdown.CHECKS[5], "1 unclosed")
        document["events"][2]["previous_event_id"] = "not-the-previous-event"
        self.ledger.write_text(json.dumps(document), encoding="utf-8")
        result = self.check(expected=1, remove_root=False)
        self.assert_blocked(result, shutdown.CHECKS[7], "the chain breaks at event index 2")

    def test_a_ledger_event_after_the_probe_blocks(self):
        self.write_probes(captured_at=stamp(-3600))
        result = self.check(expected=1)
        self.assert_blocked(result, shutdown.CHECKS[9], "does not precede the probe")

    def test_an_unreadable_ledger_blocks_every_ledger_check(self):
        self.ledger.write_text("{not json", encoding="utf-8")
        result = self.check(expected=2)
        record = self.gate_record()
        for name in shutdown.CHECKS[5:]:
            self.assertIn(name, record["blocking"])
        self.assertIn("the ledger could not be read", result.stdout)

    # -- live probing and authorization -----------------------------------

    def test_live_probing_with_no_tools_on_the_path_blocks(self):
        self.cells.rmdir()
        empty = self.base / "empty-bin"
        empty.mkdir()
        args = ["check", "--ledger", self.ledger, "--roots-record", self.record,
                "--roots-sha256", self.pinned, "--seal", self.seal, "--out", self.gate,
                "--raw-out", self.base / "raw.json", "--timeout", "30"]
        result = subprocess.run([sys.executable, SCRIPT, *map(str, args)],
                                capture_output=True, text=True, encoding="utf-8", timeout=120,
                                env={"PATH": str(empty), "HOME": str(self.base)})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        record = self.gate_record()
        self.assertIn(shutdown.CHECKS[3], record["blocking"])
        self.assertIn(shutdown.CHECKS[4], record["blocking"])
        raw = json.loads((self.base / "raw.json").read_text(encoding="utf-8"))
        self.assertFalse(raw["processes"]["ran"])
        self.authorize(expected=1)

    def test_authorize_refuses_a_stale_incomplete_or_forged_gate(self):
        self.check()
        self.authorize("--max-age-seconds", "3600")
        record = self.gate_record()
        stale = dict(record, observed_at=stamp(-7200))
        path = self.base / "stale.json"
        path.write_text(json.dumps(stale), encoding="utf-8")
        self.assertIn("re-probe before opening the seal",
                      self.authorize("--max-age-seconds", "60", gate=path, expected=1).stdout)

        trimmed = dict(record, checks=record["checks"][:2])
        path = self.base / "trimmed.json"
        path.write_text(json.dumps(trimmed), encoding="utf-8")
        self.assertIn("missing the required check",
                      self.authorize(gate=path, expected=1).stdout)

        forged = dict(record, all_reviewers_stopped=True)
        forged["checks"] = [dict(check, established=False, detail="probe never ran")
                            if check["check"] == shutdown.CHECKS[4] else check
                            for check in record["checks"]]
        path = self.base / "forged.json"
        path.write_text(json.dumps(forged), encoding="utf-8")
        self.assertIn("did not establish its condition",
                      self.authorize(gate=path, expected=1).stdout)

        path = self.base / "other.json"
        path.write_text(json.dumps({"artifact_id": "something-else"}), encoding="utf-8")
        self.assertIn("is not a shutdown gate record",
                      self.authorize(gate=path, expected=1).stdout)
        self.authorize(gate=self.base / "absent.json", expected=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
