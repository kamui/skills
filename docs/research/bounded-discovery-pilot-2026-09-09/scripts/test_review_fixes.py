#!/usr/bin/env python3
"""Exercise PR 197 failure paths with synthetic cells and no provider calls.

Usage: python3 scripts/test_review_fixes.py [--docker-image IMAGE]
Input: optional local image containing python3, for real mount-boundary checks.
Exit: 0 when checks pass, 1 on test failures, 2 on invalid CLI input.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

SCRIPTS = Path(__file__).resolve().parent
READINESS = SCRIPTS.parents[1] / "bounded-discovery-readiness-2026-09-12" / "scripts"


def module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


runner = module("run_cell")
archive = module("archive_pilot")
handoff = module("write_handoff")
DOCKER_IMAGE = None


def result(stdout="", code=0):
    return subprocess.CompletedProcess([], code, stdout, "")


class ReviewFixes(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.evidence = tempfile.TemporaryDirectory()
        self.addCleanup(self.evidence.cleanup)
        self.root = self.base / "position-99"
        for name in ("artifacts", "runner", "logs", "work", "clone", "finder-clone",
                     "finder-store", "packet", "snapshot"):
            (self.root / name).mkdir(parents=True)
        self.row = {"position": 99, "attempt_id": "example-C-attempt-1",
                    "cell_id": "example-C", "arm": "C", "target_slot": "slot-9"}
        self.config = {"cells_root": str(self.base), "targets": str(self.base / "targets"),
                       "auth_env_file": str(self.base / "auth"), "proxy_port": 19876,
                       "image": DOCKER_IMAGE or "test", "ledger": str(self.base / "ledger.json")}
        self.config["roots_record"] = str(Path(self.evidence.name) / "roots.json")
        self.config["payload_contract"] = str(READINESS / "payload.py")
        runner.write(self.config["roots_record"], {"recorded_at": "synthetic",
                                                  "roots": [str(self.base.resolve())]})
        (self.base / "auth").write_text("# synthetic configuration\n", encoding="utf-8")
        (self.base / "targets" / "slot-9").mkdir(parents=True)
        runner.write(self.base / "targets" / "slot-9" / "manifest.json", {})
        runner.write(self.root / "artifacts" / "prepare.json",
                     {"attempt_id": self.row["attempt_id"], "problems": [], "packet_sha256": "packet"})
        runner.write(self.root / "artifacts" / "attestation.json", {"ready": True})
        for name in ("dispatch.md", "finder-prompt.md", "agents.json", "admission.md"):
            (self.root / "runner" / name).write_text("{FINDER_CLAIMS}" if name == "admission.md" else "test",
                                                      encoding="utf-8")
        shutil.copyfile(SCRIPTS / "mark_event.py", self.root / "runner" / "mark_event.py")
        shutil.copyfile(self.config["payload_contract"], self.root / "runner" / "payload.py")

    def fake_finder(self, malformed=False):
        claims = {"context_id": "finder", "packet_sha256": "packet", "scope_id": "scope",
                  "claims": [], "inspected": [], "frontier_expansions": [], "unavailable": []}
        output = json.dumps({"type": "result", "subtype": "success", "total_cost_usd": 2,
                             "result": "```json\n%s\n```" % json.dumps([] if malformed else claims)})
        process = Mock(returncode=0)
        process.communicate.return_value = (output, None)
        return process

    def dispatch(self, phases, malformed=False):
        finder = self.fake_finder(malformed)
        proxy = Mock()
        launches = []
        real_run = runner.run

        def phase(config, root, slot, row, label, argv):
            launches.append(argv)
            value = phases[len(launches) - 1]
            if isinstance(value, Exception):
                raise value
            runner.write(root / "work" / "freeze.json", {"ledger": []})
            (root / "work" / "review-payload.md").write_text("validated payload", encoding="utf-8")
            (root / "work" / "research-report.md").write_text("report", encoding="utf-8")
            real_run(sys.executable, root / "runner" / "mark_event.py",
                     root / "work" / "timing.json", "payload_validated_at")
            return dict(value, label=label)

        with patch.object(runner, "schedule_row", return_value=self.row), \
             patch.object(runner, "specs", return_value=({}, {"permitted_roots": []})), \
             patch.object(runner, "proxy_start", return_value=(proxy, None)), \
             patch.object(runner, "record_mounts"), \
             patch.object(runner, "isolation_phase", return_value=result()) as isolation, \
             patch.object(runner, "claim_attempt"), \
             patch.object(runner, "register_contexts"), \
             patch.object(runner, "reserve", return_value=result("reserved")) as reserve, \
             patch.object(runner.subprocess, "Popen", side_effect=lambda *args, **kw:
                          finder if args[0][0] == "docker" else self.real_popen(*args, **kw)), \
             patch.object(runner, "run_phase", side_effect=phase):
            runner.dispatch(self.config, 99)
        return runner.load(self.root / "artifacts" / "dispatch.json"), finder, launches, reserve, isolation

    @property
    def real_popen(self):
        return REAL_POPEN

    def phase(self, cost=1, subtype="success", envelope=True, code=0):
        return {"cost_usd": cost, "subtype": subtype, "envelope": envelope,
                "exit_code": code, "is_error": subtype != "success", "stderr_tail": ""}

    def test_finder_shapes(self):
        for value in ([], None, 1, "text", {"claims": [1]}, {"claims": [None]}):
            with self.subTest(value=value):
                claims, problems = runner.finder_claims("```json\n%s\n```" % json.dumps(value))
                self.assertIsNone(claims)
                self.assertTrue(problems)

    def test_shared_allowance_before_launch_and_after_barrier(self):
        record, _, launches, reserve, _ = self.dispatch([self.phase(cost=3), self.phase(cost=1)])
        allowances = [Decimal(argv[argv.index("--max-budget-usd") + 1]) for argv in launches]
        self.assertEqual(allowances, [Decimal(7), Decimal(4)])
        self.assertEqual(allowances[0] + Decimal(runner.FINDER_CEILING), Decimal(9))
        self.assertEqual(reserve.call_args.args[2], "11.00")
        self.assertEqual(record["completion"], "complete")
        self.assertIsNotNone(runner.load(self.root / "work" / "timing.json")["completed_at"])

    def test_malformed_finder_cost_cannot_interrupt_cleanup(self):
        for cost in ("not-a-number", None, -1, True, float("nan")):
            with self.subTest(cost=cost):
                for path in (self.root / "artifacts" / "dispatch.json", self.root / "work" / "timing.json",
                             self.root / "artifacts" / "finder-launch.json"):
                    path.unlink(missing_ok=True)
                process = self.fake_finder()
                envelope = json.loads(process.communicate.return_value[0])
                envelope["total_cost_usd"] = cost
                process.communicate.return_value = (json.dumps(envelope), None)
                with patch.object(self, "fake_finder", return_value=process):
                    record, _, _, _, isolation = self.dispatch([self.phase()])
                self.assertEqual(record["completion"], "stopped-finder")
                self.assertFalse(record["finder"]["reported_cost_valid"])
                self.assertEqual(isolation.call_count, 2)
                self.assertTrue((self.root / "artifacts" / "finder-result.json").is_file())

    def test_missing_primary_envelope_retains_finder_and_post_check(self):
        record, finder, _, _, isolation = self.dispatch([self.phase(envelope=False, code=1)])
        self.assertEqual(record["completion"], "stopped-runtime")
        self.assertEqual(record["finder"]["cost_usd"], 2)
        self.assertTrue((self.root / "artifacts" / "finder-result.json").is_file())
        finder.communicate.assert_called_once()
        self.assertEqual(isolation.call_count, 2)
        self.assertIn("stopped_at", record)
        self.assertIsNone(runner.load(self.root / "work" / "timing.json")["completed_at"])

    def test_finder_budget_envelope_does_not_require_claims(self):
        process = self.fake_finder()
        envelope = {"type": "result", "subtype": "error_max_budget_usd", "is_error": True,
                    "total_cost_usd": 2.01, "result": "unfinished"}
        process.communicate.return_value = (json.dumps(envelope), None)
        with patch.object(self, "fake_finder", return_value=process):
            record, _, launches, _, _ = self.dispatch([self.phase()])
        self.assertEqual(record["completion"], "stopped-budget")
        self.assertEqual(len(launches), 1)
        self.assertFalse(record["problems"])
        self.assertFalse(record["finder"]["problems"])
        self.assertIn("exhausted", record["stop_reason"])

    def test_refused_reservation_closes_budget_without_worker_usage(self):
        self.fresh_ledger()
        self.row["arm"] = "A"
        # Exhaust the spendable allowance with another reservation.
        budget = runner.budget_module(self.config)
        budget.transact(self.config["ledger"], "reserve", "occupied", "140", evidence="test")
        # dispatch needs this synthetic slot's manifest; the frozen budget module
        # location is supplied separately while using the real claim and reserve.
        self.config["targets"] = str(self.base / "targets")
        real_run = runner.run
        def run(*command, **kwargs):
            if len(command) > 1 and Path(command[1]).name == "budget.py":
                command = (command[0], str(SCRIPTS.parents[1] / "bounded-discovery-prototype" / "scripts" / "budget.py"), *command[2:])
            return real_run(*command, **kwargs)
        with patch.object(runner, "schedule_row", return_value=self.row), \
             patch.object(runner, "budget_module", return_value=budget), \
             patch.object(runner, "run", side_effect=run), \
             patch.object(runner, "specs", return_value=({}, {"permitted_roots": []})), \
             patch.object(runner, "proxy_start", return_value=(Mock(), None)), \
             patch.object(runner, "record_mounts", return_value=True), \
             patch.object(runner, "isolation_phase", return_value=result()), \
             patch.object(runner, "run_phase") as phase:
            self.assertEqual(runner.dispatch(self.config, 99), 0)
            record = runner.load(self.root / "artifacts" / "dispatch.json")
            self.assertTrue(record["reservation_refused"])
            self.assertFalse(record["problems"])
            phase.assert_not_called()
            self.assertEqual(runner.settle(self.config, 99), 0)
        closed = runner.load(self.config["ledger"])["events"][-1]
        self.assertEqual(closed["operation"], "attempt-close")
        self.assertEqual(closed["disposition"], "stopped-budget")
        saved = runner.load(self.root / "artifacts" / "settle.json")
        self.assertEqual(saved["operational_validity"], "valid")
        self.assertEqual(saved["settled_usd"], "0.0000000")
        self.assertEqual(saved["dispatch_stop_reason"], record["stop_reason"])
        runner.write(self.root / "artifacts" / "prepare.json",
                     dict(self.row, replicate=1, block="pilot", problems=[]))
        public = archive.summarize(self.root, [], b"synthetic-salt")
        self.assertEqual(public["stop_reason"], record["stop_reason"])
        target = self.base / "public" / "cells" / "position-01"
        target.mkdir(parents=True)
        runner.write(target / "summary.json", public)
        self.assertEqual(handoff.cell_records(self.base / "public")[0]["stop_reason"], record["stop_reason"])

    def test_primary_error_envelope_stops_before_resume(self):
        record, finder, launches, _, isolation = self.dispatch([
            self.phase(subtype="error_during_execution", code=1), self.phase()])
        self.assertEqual(record["completion"], "stopped-runtime")
        self.assertEqual(len(launches), 1)
        finder.communicate.assert_called_once()
        self.assertEqual(isolation.call_count, 2)
        self.assertIsNone(runner.load(self.root / "work" / "timing.json")["completed_at"])

    def test_primary_launch_exception_retains_finder(self):
        record, finder, _, _, _ = self.dispatch([runner.Failed("synthetic launch failure")])
        self.assertEqual(record["completion"], "stopped-runtime")
        self.assertEqual(record["finder"]["cost_usd"], 2)
        finder.communicate.assert_called_once()

    def test_malformed_finder_keeps_terminal_outcome(self):
        record, _, launches, _, _ = self.dispatch([self.phase()], malformed=True)
        self.assertEqual(record["completion"], "stopped-finder")
        self.assertEqual(len(launches), 1)
        self.assertEqual(runner.attempt_completion(record), "stopped-finder")
        self.assertIsNone(runner.load(self.root / "work" / "timing.json")["completed_at"])

    def test_exhausted_allowance_and_phase_two_stop_never_complete(self):
        for phases in ([self.phase(cost=7)], [self.phase(), self.phase(subtype="error_max_budget_usd")]):
            with self.subTest(phases=phases):
                for path in (self.root / "artifacts" / "dispatch.json", self.root / "work" / "timing.json",
                             self.root / "artifacts" / "finder-launch.json"):
                    path.unlink(missing_ok=True)
                record, _, _, _, _ = self.dispatch(phases)
                self.assertEqual(record["completion"], "stopped-budget")
                self.assertIn("stopped_at", record)
                self.assertIsNone(runner.load(self.root / "work" / "timing.json")["completed_at"])

    def test_finder_is_stopped_and_reaped_on_timeout(self):
        process = self.fake_finder()
        output = process.communicate.return_value
        process.communicate.side_effect = [subprocess.TimeoutExpired("finder", 0), output]
        record = {}
        with patch.object(runner, "run", return_value=result()) as command:
            runner.collect_finder(self.root, process, record)
        self.assertEqual(command.call_args.args[:2], ("docker", "stop"))
        self.assertEqual(process.communicate.call_count, 2)
        self.assertEqual(record["finder"]["cost_usd"], 2)

    def test_large_raw_evidence_is_retained(self):
        source = self.base / "raw"
        (source / "target").mkdir(parents=True)
        for name in ("session.jsonl", "raw.log", "result.json", "target/review.md"):
            (source / name).write_bytes(b"x" * (4 * 1024 * 1024 + 1))
        destination = self.base / "saved"
        archive.copy_evidence(source, destination, ())
        for name in ("session.jsonl", "raw.log", "result.json", "target/review.md"):
            self.assertEqual(runner.digest(source / name), runner.digest(destination / name))

    def test_empty_and_partial_handoff_cli(self):
        ledger = {"events": [], "frozen_total_cap_usd": "150", "grading_closeout_reserve_usd": "10",
                  "actual_usd": "0", "reserved_usd": "0", "uncertainty_usd": "0"}
        runner.write(self.base / "ledger.json", ledger)
        runner.write(self.base / "config.json", self.config)
        command = [sys.executable, str(SCRIPTS / "write_handoff.py"), "--config", str(self.base / "config.json"),
                   "--bundle", str(self.base / "public"), "--out", str(self.base / "handoff.json")]
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        document = runner.load(self.base / "handoff.json")
        self.assertEqual(document["disposition"], "stopped-incomplete")
        self.assertEqual(len(document["cells"]), 6)
        self.assertIsNone(document["affordability"]["fits"])
        money = handoff.affordability([{"arm": "A", "settled_usd": "3"}], Decimal("100"))
        self.assertEqual(money["missing_arm_measurements"], ["B", "C"])

    def test_direct_socket_evidence_requires_a_recorded_judgment(self):
        transcript = self.base / "socket.jsonl"
        command = "python3 -c 'import socket; socket.create_connection((\"192.0.2.1\",443))'"
        runner.write(transcript, {})
        transcript.write_text(json.dumps({"message": {"content": [{"type": "tool_use", "name": "Bash",
                                             "input": {"command": command}}]}}) + "\n", encoding="utf-8")
        self.assertFalse(runner.audit_network([str(transcript)], [])["passed"])
        self.assertFalse(runner.audit_network([str(transcript)], [{"host": "api.anthropic.com"}])["passed"])
        decision = {"command_sha256": hashlib.sha256(command.encode()).hexdigest(),
                    "reason": "synthetic test acceptance", "egress_event_indices": [0], "egress_sha256": "wrong"}
        self.assertFalse(runner.audit_network([str(transcript)], [], [decision])["passed"])

    def test_indirect_network_and_ordinary_shell_both_require_review(self):
        transcript = self.base / "indirect.jsonl"
        for command in ("python3 -c 'import asyncio; asyncio.run(asyncio.open_connection(\"192.0.2.1\",443))'",
                        "python3 opaque_script.py", "git status --short"):
            transcript.write_text(json.dumps({"message": {"content": [{"type": "tool_use", "name": "Bash",
                                                 "input": {"command": command}}]}}) + "\n", encoding="utf-8")
            audit = runner.audit_network([str(transcript)], [])
            self.assertFalse(audit["passed"])
            self.assertEqual(len(audit["candidates"]), 1)
        decision = {"command_sha256": hashlib.sha256(command.encode()).hexdigest(),
                    "no_network_occurred": True, "reason": "retained command and output show only local status"}
        self.assertTrue(runner.audit_network([str(transcript)], [], [decision])["passed"])

    def test_replacement_preserves_predecessor_and_uses_only_own_transcripts(self):
        runner.write(self.root / "artifacts" / "settle.json", {"completion": "stopped-invalid"})
        old = runner.session_home(self.root, "primary") / ".claude" / "projects" / "old.jsonl"
        old.parent.mkdir(parents=True)
        old.write_text("old evidence\n", encoding="utf-8")
        runner.retain_predecessor(self.config, 99, 2)
        saved = self.base / "retained-attempts" / "position-99-attempt-01.tar.gz"
        with tarfile.open(saved) as evidence:
            self.assertIn("attempt/session-homes/primary/.claude/projects/old.jsonl", evidence.getnames())
        retry = runner.cell_root(self.config, 99, 2)
        fresh = runner.session_home(retry, "primary") / ".claude" / "projects" / "new.jsonl"
        fresh.parent.mkdir(parents=True)
        fresh.write_text("new evidence\n", encoding="utf-8")
        self.assertEqual(runner.transcripts_for(retry), [str(fresh)])
        self.assertEqual(runner.transcripts_for(self.root), [str(old)])
        self.assertFalse((retry / "work" / "timing.json").exists())
        runner.write(self.root / "work" / "timing.json", {})
        with patch.object(runner, "schedule_row", return_value=self.row):
            with self.assertRaises(runner.Failed):
                runner.prepare(self.config, 99, force=True)
        self.assertTrue(old.is_file())

    def test_replacement_summary_uses_latest_and_retains_both_costs(self):
        retry = self.root / "attempt-02"
        (retry / "artifacts").mkdir(parents=True)
        runner.write(retry / "artifacts" / "prepare.json", {})
        def summary(path, secrets, salt):
            second = path == retry
            return {"attempt_ordinal": 2 if second else 1,
                    "disposition": "dispatched" if second else "stopped-invalid",
                    "problems": [] if second else ["old failure"],
                    "accounting": {"settled_usd": "3" if second else "2",
                                   "reconciliation_residual_usd": "0"}}
        with patch.object(archive, "summarize", side_effect=summary), \
             patch.object(archive, "stage_sealed", return_value=[]) as stage:
            public, _ = archive.stage_position(self.root, self.base / "staging", [], b"salt")
        self.assertEqual(public["disposition"], "dispatched")
        self.assertEqual(stage.call_count, 2)
        self.assertNotEqual(stage.call_args_list[0].args[2], stage.call_args_list[1].args[2])
        target = self.base / "public" / "cells" / "position-01"
        target.mkdir(parents=True)
        runner.write(target / "summary.json", public)
        attempts = handoff.attempt_records(self.base / "public", [])
        self.assertEqual([entry["ordinal"] for entry in attempts], [1, 2])
        self.assertEqual(sum(Decimal(entry["settled_usd"]) for entry in attempts), Decimal(5))

    def fresh_ledger(self):
        self.config["targets"] = str(SCRIPTS.parents[1] / "bounded-discovery-prototype" / "targets")
        runner.write(self.base / "ledger.json", {
            "owner": "test", "frozen_total_cap_usd": "150", "total_ceiling_usd": "150",
            "grading_closeout_reserve_usd": "10", "pre_freeze_ceiling_usd": "15",
            "actual_usd": "0", "reserved_usd": "0", "uncertainty_usd": "0",
            "pre_freeze_actual_usd": "0", "pre_freeze_reserved_usd": "0",
            "attempt_limit": 27, "replacement_limit": 3,
            "events": [{"event_id": "initial", "previous_event_id": None, "operation": "open",
                        "phase": "pre-freeze", "attempt_id": None, "actual_delta_usd": "0", "reservation_delta_usd": "0",
                        "uncertainty_usd": "0"}]})

    def usage_fixture(self, role, requests=(100000, 200000)):
        name = ("agent-verifier" if role == "worker" else
                runner.session_id(self.row["attempt_id"], "finder" if role == "finder" else "primary"))
        path = runner.session_home(self.root, "finder" if role == "finder" else "primary") / ".claude" / "projects" / (name + ".jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for index, tokens in enumerate(requests):
            entry = {"type": "assistant", "requestId": "request-%d" % index,
                     "message": {"model": "claude-sonnet-5", "usage": {"input_tokens": tokens}, "content": []}}
            # Repeated streamed lines must count once, including in the bound.
            lines.extend([json.dumps(entry), json.dumps(entry)])
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def settle_usage(self, phases, finder=None, roles=()):
        self.fresh_ledger()
        self.config.update(bundle=str(SCRIPTS.parents[1] / "bounded-discovery-runs-2026-09-08"),
                           tools=str(SCRIPTS.parents[1] / "tools"))
        for role in roles:
            self.usage_fixture(role)
        runner.claim_attempt(self.config, self.row, runner.cell_contexts(self.root, self.row))
        self.assertEqual(runner.reserve(self.config, self.row, "11.00" if self.row["arm"] == "C" else "10.00", "test").returncode, 0)
        runner.write(self.root / "artifacts" / "dispatch.json", {
            "attempt_id": self.row["attempt_id"], "arm": self.row["arm"], "disposition": "stopped-runtime",
            "phases": phases, "finder": finder, "problems": []})
        runner.write(self.root / "artifacts" / "cell-env-dispatch.json", {"permitted_roots": []})
        with patch.object(runner, "schedule_row", return_value=self.row), \
             patch.object(runner, "verify_models", return_value=({}, [])), \
             patch.object(runner, "audit_reads", return_value={"passed": True}):
            runner.settle(self.config, 99)
        return runner.load(self.root / "artifacts" / "settle.json"), runner.load(self.config["ledger"])

    def test_missing_primary_without_transcript_keeps_entire_reservation(self):
        self.row["arm"] = "A"
        record, ledger = self.settle_usage([self.phase(cost=0, envelope=False)])
        self.assertEqual(Decimal(ledger["reserved_usd"]), 10)
        self.assertEqual(Decimal(ledger["actual_usd"]), 0)
        self.assertIsNone(record["settled_usd"])
        self.assertTrue(record["reservation_retained"])
        self.assertFalse(any(e["operation"] == "settle" for e in ledger["events"]))

    def test_settlement_retains_roles_including_filtered_provider_error(self):
        original_fixture = self.usage_fixture

        def with_provider_error(role):
            path = original_fixture(role)
            with open(path, "a", encoding="utf-8") as stream:
                stream.write(json.dumps({"type": "assistant", "message": {
                    "model": "<synthetic>", "content": [], "usage": {}}}) + "\n")
            return path

        with patch.object(self, "usage_fixture", side_effect=with_provider_error):
            record, _ = self.settle_usage([self.phase(cost=0, envelope=False)],
                                          finder={"cost_usd": None},
                                          roles=("primary", "finder", "worker"))
        self.assertEqual(set(record["usage_per_role"]), {"primary", "finder", "worker"})
        self.assertTrue(all(Decimal(value["cost_usd"]) == Decimal("0.6")
                            for value in record["usage_per_role"].values()))
        sources = runner.load(self.root / "artifacts" / "filtered-transcripts" / "sources.json")
        self.assertEqual(len(sources), 3)
        for source in sources:
            self.assertEqual(source["source_sha256"], runner.digest(source["source"]))
            self.assertEqual(source["copy_sha256"], runner.digest(source["copy"]))

    def test_failed_launch_keeps_exact_argv_before_subprocess(self):
        command = ["example", "--model", "test", "--effort", "high", "--restricted",
                   "--max-budget-usd", "7", "--allowedTools", "Read", "Bash(git:*)"]
        path = self.root / "artifacts" / "primary-phase-1-launch.json"

        def failed_run(*args, **kwargs):
            self.assertEqual(runner.load(path)["argv"], list(args))
            raise runner.Failed("synthetic launch failure")

        with patch.object(runner, "docker_argv", return_value=command), \
             patch.object(runner, "run", side_effect=failed_run):
            with self.assertRaises(runner.Failed):
                runner.run_phase(self.config, self.root, "slot-9", self.row,
                                 "primary-phase-1", [])
        before = path.read_bytes()
        with self.assertRaises(FileExistsError):
            runner.retain_launch(self.root, self.row, "primary-phase-1", ["different"])
        self.assertEqual(path.read_bytes(), before)

    def test_finder_launch_retains_requested_controls(self):
        self.dispatch([self.phase(), self.phase()])
        command = runner.load(self.root / "artifacts" / "finder-launch.json")["argv"]
        self.assertEqual(command[command.index("--model") + 1], "claude-opus-5")
        self.assertEqual(command[command.index("--max-budget-usd") + 1], runner.FINDER_CEILING)
        self.assertIn("--restricted", command)

    def test_sandbox_acceptance_and_prefix_or_traversal_cannot_pass(self):
        permitted = ["/cells/example/clone"]
        path = self.root / "outside.jsonl"
        for value in ("/elsewhere/tidy.txt", "/cells/example/clone-sibling/secret",
                      "/cells/example/clone/../secret", "/cell-home-sibling/secret"):
            with self.subTest(path=value):
                path.write_text(json.dumps({"message": {"content": [{"type": "tool_use",
                    "name": "Read", "input": {"file_path": value}}]}}), encoding="utf-8")
                audit = runner.audit_reads(self.root, [str(path)], permitted,
                                            [{"path": value, "reason": "tidiness"}])
                self.assertFalse(audit["passed"])

    def test_unknown_metering_role_is_refused(self):
        with self.assertRaises(runner.Failed):
            runner.meter_roles(["unknown.jsonl"], self.row)

    def test_dispatch_requires_the_actual_unsealed_root(self):
        self.assertTrue(runner.dispatch_roots(self.config)["sha256"])
        for value in ({}, {"roots_record": self.config["roots_record"],
                           "cells_root": str(self.base / "wrong-root")}):
            with self.assertRaises(runner.Failed):
                runner.dispatch_roots(value)

    def test_missing_reports_retain_one_extra_request_per_worker(self):
        record, ledger = self.settle_usage([self.phase(cost=0, envelope=False)],
                                           finder={"cost_usd": None}, roles=("primary", "finder", "worker"))
        # Each worker has $0.60 observed and a largest $0.40 request at frozen $2/M.
        self.assertEqual(Decimal(ledger["actual_usd"]), Decimal("1.8"))
        self.assertEqual(Decimal(ledger["uncertainty_usd"]), Decimal("1.2"))
        self.assertEqual(Decimal(ledger["reserved_usd"]), 0)
        self.assertFalse(record["reservation_retained"])
        with patch.object(runner, "schedule_row", return_value=self.row), \
             patch.object(runner, "verify_models", return_value=({}, [])), \
             patch.object(runner, "audit_reads", return_value={"passed": True}):
            runner.settle(self.config, 99)
        self.assertEqual(runner.load(self.config["ledger"]), ledger)
        self.assertFalse(any("existing settlement" in p for p in runner.load(self.root / "artifacts" / "settle.json")["problems"]))

    def test_missing_finder_cost_cannot_be_offset_by_primary_report(self):
        record, ledger = self.settle_usage([self.phase(cost=2)],
                                           finder={"cost_usd": None}, roles=("primary", "finder"))
        self.assertEqual(Decimal(ledger["actual_usd"]), Decimal("2.6"))
        self.assertEqual(Decimal(ledger["uncertainty_usd"]), Decimal("0.4"))
        self.assertFalse(record["reservation_retained"])

    def test_missing_report_with_worker_launch_keeps_reservation(self):
        original_fixture = self.usage_fixture
        def fixture(role):
            path = original_fixture(role)
            if role == "primary":
                lines = path.read_text(encoding="utf-8").splitlines()
                entry = json.loads(lines[0])
                # A launch record can itself lack usage while other requests survive.
                entry["message"].pop("usage")
                entry["message"]["content"] = [{"type": "tool_use", "name": "Agent",
                                                "id": "launched-verifier", "input": {}}]
                lines[0] = json.dumps(entry)
                path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return path
        with patch.object(self, "usage_fixture", side_effect=fixture):
            record, ledger = self.settle_usage([self.phase(cost=0, envelope=False)],
                                               finder={"cost_usd": 2}, roles=("primary", "finder"))
        self.assertEqual(Decimal(ledger["reserved_usd"]), 11)
        self.assertIsNone(record["settled_usd"])
        self.assertTrue(record["reservation_retained"])

    def test_missing_resume_usage_keeps_reservation_until_phases_reconcile(self):
        record, ledger = self.settle_usage([self.phase(), self.phase(cost=0, envelope=False)],
                                           finder={"cost_usd": 2}, roles=("primary", "finder"))
        self.assertEqual(Decimal(ledger["reserved_usd"]), 11)
        self.assertTrue(record["reservation_retained"])

    def test_valid_zero_report_releases_reservation(self):
        self.row["arm"] = "A"
        record, ledger = self.settle_usage([self.phase(cost=0)])
        self.assertEqual(Decimal(ledger["reserved_usd"]), 0)
        self.assertEqual(Decimal(ledger["uncertainty_usd"]), 0)
        self.assertFalse(record["reservation_retained"])

    def test_primary_envelope_missing_cost_is_unknown(self):
        for cost in (None, "bad", -1, float("nan"), float("inf"), True):
            with self.subTest(cost=cost), patch.object(runner, "docker_argv", return_value=["synthetic"]), \
                 patch.object(runner, "run", return_value=result(json.dumps({"type": "result", "total_cost_usd": cost}))):
                (self.root / "artifacts" / "primary-launch.json").unlink(missing_ok=True)
                record = runner.run_phase(self.config, self.root, "slot-9", self.row, "primary", [])
                self.assertIsNone(record["cost_usd"])
                self.assertFalse(record["reported_cost_valid"])

    def test_regenerated_public_handoff_preserves_fidelity_hold(self):
        source = SCRIPTS.parent
        preserved = runner.load(source / "handoff.json")
        public = self.base / "public"
        shutil.copytree(source / "cells", public / "cells")
        shutil.copyfile(source / "fidelity-review.json", public / "fidelity-review.json")
        extra = [entry for entry in preserved["attempts"] if entry.get("ordinal") == 1
                 and entry.get("position") in (1, 3)]
        self.assertEqual(len(extra), 2)
        runner.write(self.base / "extra.json", extra)
        setup = preserved["setup_charges"]["items"]
        ledger = dict(preserved["accounting"], pre_freeze_actual_usd=preserved["reconciliation"]["pre_freeze_actual_usd"],
                      events=[{"operation": "settle", "phase": "review", "attempt_id": None,
                               "actual_delta_usd": item["usd"], "reservation_id": item["reservation_id"],
                               "request_refs": [item["why"]]} for item in setup])
        runner.write(self.base / "ledger.json", ledger)
        runner.write(self.base / "config.json", self.config)
        command = [sys.executable, str(SCRIPTS / "write_handoff.py"), "--config", str(self.base / "config.json"),
                   "--bundle", str(public), "--extra-attempts", str(self.base / "extra.json"),
                   "--out", str(self.base / "handoff.json")]
        for judgment in (preserved["fidelity_review"], None, {"status": "cleared"},
                         {"status": "cleared", "evidence": ["synthetic://operational-extract"],
                          "rationale": "Synthetic test judgment only; this does not clear the preserved pilot."}):
            with self.subTest(judgment=judgment):
                state = public / "fidelity-review.json"
                if judgment is None:
                    state.unlink()
                else:
                    runner.write(state, judgment)
                completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(completed.returncode, 0, completed.stderr)
                document = runner.load(self.base / "handoff.json")
                self.assertTrue(document["reconciliation"]["reconciles"], document["reconciliation"])
                cleared = judgment and judgment.get("evidence")
                self.assertEqual(document["disposition"], "continue" if cleared else "stopped-incomplete")
                self.assertEqual(bool(document["blockers"]), not bool(cleared))
                self.assertIn("fidelity_review", document)

    def test_actual_worker_registration_is_append_only_and_rejects_reuse(self):
        self.fresh_ledger()
        contexts = {"primary": "primary-id", "finder": "finder-id"}
        runner.claim_attempt(self.config, self.row, contexts)
        prefix = runner.load(self.config["ledger"])["events"]
        contexts["verifier:agent-new"] = "agent-new"
        runner.register_contexts(self.config, self.row, contexts)
        saved = runner.load(self.config["ledger"])
        self.assertEqual(saved["events"], prefix)
        self.assertEqual(len(saved["context_claims"]), 3)
        runner.register_contexts(self.config, self.row, contexts)
        self.assertEqual(runner.load(self.config["ledger"]), saved)
        with self.assertRaises(runner.Failed):
            runner.register_contexts(self.config, self.row, {"verifier": "finder-id"})
        runner.close_attempt(self.config, self.row, "complete")
        other = dict(self.row, attempt_id="other", cell_id="other")
        with self.assertRaises(runner.Failed):
            runner.claim_attempt(self.config, other, {"primary": "agent-new"})
        runner.claim_attempt(self.config, other, {"primary": "fresh"})
        with self.assertRaises(runner.Failed):
            runner.register_contexts(self.config, other, {"verifier": "agent-new"})

    def test_settlement_keeps_stop_reason_and_closes_invalid_attempt(self):
        self.fresh_ledger()
        self.config["bundle"] = str(self.base)
        runner.claim_attempt(self.config, self.row, runner.cell_contexts(self.root, self.row))
        self.assertEqual(runner.reserve(self.config, self.row, "11.00", "test").returncode, 0)
        runner.write(self.root / "artifacts" / "dispatch.json", {
            "attempt_id": self.row["attempt_id"], "arm": "C", "disposition": "stopped-finder",
            "phases": [self.phase()], "finder": {"cost_usd": 2}, "problems": ["malformed finder"],
            "stopped_at": "2026-01-01T00:00:00+00:00"})
        runner.write(self.root / "artifacts" / "cell-env-dispatch.json", {"permitted_roots": []})
        with patch.object(runner, "schedule_row", return_value=self.row):
            self.assertEqual(runner.settle(self.config, 99), 1)
        saved = runner.load(self.root / "artifacts" / "settle.json")
        self.assertEqual(saved["completion"], "stopped-finder")
        self.assertIn("malformed finder", saved["problems"])
        self.assertEqual(saved["stopped_at"], "2026-01-01T00:00:00+00:00")
        events = runner.load(self.config["ledger"])["events"]
        self.assertEqual(events[-1]["operation"], "attempt-close")
        self.assertEqual(events[-1]["disposition"], "stopped-invalid")
        self.assertEqual(saved["settled_usd"], "3.0000000")

    def test_settlement_invalidates_completed_timing_with_censored_stop(self):
        self.fresh_ledger()
        self.config["bundle"] = str(self.base)
        self.row["arm"] = "A"
        runner.claim_attempt(self.config, self.row, runner.cell_contexts(self.root, self.row))
        self.assertEqual(runner.reserve(self.config, self.row, "10.00", "test").returncode, 0)
        runner.write(self.root / "artifacts" / "dispatch.json", {
            "attempt_id": self.row["attempt_id"], "arm": "A", "disposition": "dispatched",
            "phases": [self.phase()], "problems": [], "ended_at": "2026-01-01T00:01:00+00:00"})
        runner.write(self.root / "artifacts" / "cell-env-dispatch.json", {"permitted_roots": []})
        sidecar = self.root / "work" / "timing.json"
        runner.write(sidecar, {"root_dispatched_at": "2026-01-01T00:00:00+00:00",
                               "completed_at": "2026-01-01T00:01:00+00:00"})
        with patch.object(runner, "schedule_row", return_value=self.row):
            runner.settle(self.config, 99)
        record = runner.load(self.root / "artifacts" / "settle.json")
        self.assertEqual(record["completion"], "stopped-invalid")
        self.assertEqual(record["stopped_at"], "2026-01-01T00:01:00+00:00")
        self.assertEqual(record["elapsed_seconds"], 60)
        self.assertTrue(record["duration_censored"])
        self.assertIsNone(runner.load(sidecar)["completed_at"])
        self.assertIsNotNone(runner.load(self.root / "artifacts" / "timing-before-settlement.json")["completed_at"])

    def test_budget_completion_does_not_override_operational_invalidity(self):
        for failure in (None, "model", "read"):
            with self.subTest(failure=failure):
                self.fresh_ledger()
                self.config.update(bundle=str(self.base), tools=str(self.base))
                self.row["arm"] = "A"
                transcript = runner.session_home(self.root, "primary") / ".claude" / "projects" / (runner.session_id(self.row["attempt_id"]) + ".jsonl")
                transcript.parent.mkdir(parents=True, exist_ok=True)
                transcript.write_text("{}\n", encoding="utf-8")
                runner.claim_attempt(self.config, self.row, runner.cell_contexts(self.root, self.row))
                self.assertEqual(runner.reserve(self.config, self.row, "10.00", "test").returncode, 0)
                runner.write(self.root / "artifacts" / "dispatch.json", {
                    "attempt_id": self.row["attempt_id"], "arm": "A", "disposition": "stopped-budget",
                    "phases": [self.phase(subtype="error_max_budget_usd")], "problems": [],
                    "stopped_at": "2026-01-01T00:01:00+00:00"})
                runner.write(self.root / "artifacts" / "cell-env-dispatch.json", {"permitted_roots": []})
                real_run = runner.run
                def run(*command, **kwargs):
                    if len(command) > 1 and Path(command[1]).name == "agent_effort.py":
                        return result()
                    if len(command) > 1 and Path(command[1]).name == "meter_split.py":
                        runner.write(self.root / "artifacts" / "usage-split.json", {
                            "total_cost_usd": "1", "per_model": {}, "within_tolerance": True})
                        return result()
                    return real_run(*command, **kwargs)
                with patch.object(runner, "schedule_row", return_value=self.row), \
                     patch.object(runner, "run", side_effect=run), \
                     patch.object(runner, "verify_models", return_value=(
                         {"primary": {"verified": failure != "model"}},
                         ["model mismatch"] if failure == "model" else [])), \
                     patch.object(runner, "audit_reads", return_value={"passed": failure != "read"}):
                    runner.settle(self.config, 99)
                record = runner.load(self.root / "artifacts" / "settle.json")
                self.assertEqual(record["completion"], "stopped-budget")
                self.assertEqual(record["stopped_at"], "2026-01-01T00:01:00+00:00")
                self.assertEqual(record["operational_validity"], "invalid" if failure else "valid")
                self.assertEqual(runner.load(self.config["ledger"])["events"][-1]["disposition"],
                                 "stopped-invalid" if failure else "stopped-budget")
                _, blockers, incomplete = handoff.decide([
                    dict(record, disposition="stopped-budget", isolation_ready=True,
                         read_audit_passed=failure != "read")], Decimal("100"))
                self.assertEqual(bool(blockers), bool(failure))
                self.assertEqual("not replacement-eligible" in incomplete[0]["effect"], failure is None)

    def test_final_payload_change_requires_revalidation(self):
        script = SCRIPTS / "mark_event.py"
        sidecar = self.root / "work" / "timing.json"
        runner.run(sys.executable, script, sidecar, "root_dispatched_at", "--create")
        self.assertEqual(runner.run(sys.executable, script, sidecar, "completed_at", check=False).returncode, 1)
        for name in ("review-payload.md", "research-report.md"):
            (sidecar.parent / name).write_text("first", encoding="utf-8")
        runner.run(sys.executable, script, sidecar, "payload_validated_at")
        (sidecar.parent / "review-payload.md").write_text("changed", encoding="utf-8")
        self.assertEqual(runner.run(sys.executable, script, sidecar, "completed_at", check=False).returncode, 1)
        self.assertIsNone(runner.load(sidecar)["completed_at"])


    # -- the uniform payload contract (#199 gap 6) -------------------------

    def contract_payload(self, arm="C", items=None, stop=None, outcome="findings"):
        """One arm's contract payload, in the shape every arm must produce."""
        if items is None:
            items = [{"type": "finding", "markdown": "The retry loop never resets.",
                      "trailer": "<!-- finding id=code/retry head=abc -->",
                      "anchor": {"type": "line", "path": "src/a.ts", "start_line": 1,
                                 "end_line": 2, "side": "RIGHT"},
                      "priority": "P1", "action": "must-fix", "blocking": True,
                      "kind": "bug"}]
        runner.write(self.root / "work" / "review-payload.json",
                     {"schema_version": "bounded-discovery-payload-v1",
                      "attempt_id": self.row["attempt_id"], "arm": arm, "outcome": outcome,
                      "summary": {"body": "## Review\n\nMode: retrospective."},
                      "items": items, "stop": stop})

    def settle_payload(self, disposition="stopped-runtime", contract=True, **extra):
        self.fresh_ledger()
        self.config.update(bundle=str(SCRIPTS.parents[1] / "bounded-discovery-runs-2026-09-08"),
                           tools=str(SCRIPTS.parents[1] / "tools"))
        runner.claim_attempt(self.config, self.row,
                             runner.cell_contexts(self.root, self.row))
        runner.reserve(self.config, self.row, "11.00", "test")
        record = {"attempt_id": self.row["attempt_id"], "arm": self.row["arm"],
                  "disposition": disposition, "phases": [], "finder": None, "problems": []}
        if contract:
            script = Path(self.config["payload_contract"])
            record["payload_contract"] = {"path": str(script), "sha256": runner.digest(script)}
        record.update(extra)
        runner.write(self.root / "artifacts" / "dispatch.json", record)
        runner.write(self.root / "artifacts" / "cell-env-dispatch.json", {"permitted_roots": []})
        with patch.object(runner, "schedule_row", return_value=self.row), \
             patch.object(runner, "verify_models", return_value=({}, [])), \
             patch.object(runner, "audit_reads", return_value={"passed": True}):
            runner.settle(self.config, 99)
        return runner.load(self.root / "artifacts" / "settle.json")

    def test_dispatch_requires_a_pinned_payload_contract(self):
        self.assertTrue(runner.payload_contract(self.config)["sha256"])
        for value in ({}, {"payload_contract": str(self.base / "absent.py")}):
            with self.assertRaises(runner.Failed):
                runner.payload_contract(value)

    def test_dispatch_requires_the_prepared_contract_to_match_the_pin(self):
        prepared = self.root / "runner" / "payload.py"
        contract = runner.payload_contract(self.config, self.root)
        self.assertEqual(contract["prepared_path"], str(prepared))
        self.assertEqual(runner.digest(prepared), contract["sha256"])
        # A copy that drifted from the configured file, and a cell prepared
        # before one was configured, both refuse before any worker starts.
        prepared.write_text("# a different validator\n", encoding="utf-8")
        with self.assertRaises(runner.Failed):
            runner.payload_contract(self.config, self.root)
        with patch.object(runner, "schedule_row", return_value=self.row):
            with self.assertRaises(runner.Failed):
                runner.dispatch(self.config, 99)
        prepared.unlink()
        with self.assertRaises(runner.Failed):
            runner.payload_contract(self.config, self.root)
        self.assertFalse((self.root / "artifacts" / "dispatch.json").exists())

    def test_every_arm_is_settled_under_one_contract_and_keeps_its_findings(self):
        self.contract_payload(stop={"reason": "runtime-error", "detail": "provider 502"})
        record = self.settle_payload()
        self.assertTrue(record["payload_contract_enforced"])
        self.assertTrue(record["payload_accepted"])
        self.assertEqual(record["payload_outcome"], "findings")
        self.assertEqual(record["payload_item_count"], 1)
        self.assertEqual(record["payload_produced_by"], "arm")
        receipt = runner.load(self.root / "artifacts" / "payload-receipt.json")
        self.assertEqual(receipt["arm"], "C")
        self.assertTrue(receipt["items_present"])

    def test_a_stopped_attempt_gets_a_stopped_payload_and_no_invented_items(self):
        record = self.settle_payload(stop_reason="arm C had no allowance left to resume")
        self.assertEqual(record["payload_outcome"], "unavailable")
        self.assertEqual(record["payload_item_count"], 0)
        self.assertEqual(record["payload_produced_by"], "coordinator")
        written = runner.load(self.root / "work" / "review-payload.json")
        self.assertEqual(written["items"], [])
        self.assertEqual(written["summary"]["body"], "")
        self.assertIn("no allowance left", written["stop"]["detail"])

    def test_a_markdown_only_payload_is_refused_rather_than_masked(self):
        (self.root / "work" / "review-payload.md").write_text(
            "## Review\n\nA real finding lives here.", encoding="utf-8")
        record = self.settle_payload()
        self.assertFalse(record["payload_accepted"])
        self.assertEqual(record["operational_validity"], "invalid")
        self.assertTrue(any("second payload form" in problem
                            for problem in record["problems"]))
        self.assertFalse((self.root / "work" / "review-payload.json").exists())
        self.assertIn("A real finding lives here",
                      (self.root / "work" / "review-payload.md").read_text(encoding="utf-8"))

    def test_an_arm_specific_structure_invalidates_the_attempt(self):
        self.contract_payload(stop={"reason": "runtime-error", "detail": "d"})
        document = runner.load(self.root / "work" / "review-payload.json")
        document["finder_claims"] = ["arm C only"]
        runner.write(self.root / "work" / "review-payload.json", document)
        record = self.settle_payload()
        self.assertFalse(record["payload_accepted"])
        self.assertTrue(any("finder_claims" in problem for problem in record["problems"]))

    def test_a_contract_that_changed_since_dispatch_accepts_nothing(self):
        self.contract_payload(stop={"reason": "runtime-error", "detail": "d"})
        record = self.settle_payload(payload_contract={
            "path": self.config["payload_contract"], "sha256": "0" * 64})
        self.assertFalse(record["payload_contract_enforced"])
        self.assertFalse(record["payload_accepted"])
        self.assertTrue(any("has changed" in problem for problem in record["problems"]))

    def test_a_historical_dispatch_record_settles_without_the_contract(self):
        record = self.settle_payload(contract=False)
        self.assertFalse(record["payload_contract_enforced"])
        self.assertNotIn("payload_accepted", record)
        self.assertFalse((self.root / "work" / "review-payload.json").exists())

    def test_container_roles_cannot_read_each_others_stores(self):
        if not DOCKER_IMAGE:
            self.skipTest("pass --docker-image for the local container check")
        for role in ("primary", "finder"):
            home = runner.session_home(self.root, role)
            home.mkdir(parents=True)
            (home / "canary").write_text(role, encoding="utf-8")
        (self.root / "work" / "secret").write_text("primary", encoding="utf-8")
        (self.root / "finder-store" / "secret").write_text("finder", encoding="utf-8")
        (self.root / "logs" / "finder.log").write_text("finder", encoding="utf-8")
        self.assertTrue(runner.record_mounts(self.config, self.root, "slot-9",
                                             self.root / "artifacts" / "mounts.json", "C"))
        for role, hidden in (("primary", ["finder-store/secret", "logs/finder.log", "session-homes/finder/canary"]),
                             ("finder", ["work/secret", "runner/dispatch.md", "session-homes/primary/canary"])):
            probe = "from pathlib import Path; import json; print(json.dumps([Path(p).exists() for p in %r]))" % [str(self.root / p) for p in hidden]
            argv = runner.docker_argv(self.config, self.root, "slot-9", "pr197-test-" + role,
                                      ["python3", "-c", probe], self.root / ("work" if role == "primary" else "finder-store"), role=role)
            observed = runner.run(*argv)
            self.assertEqual(json.loads(observed.stdout), [False] * len(hidden))


REAL_POPEN = subprocess.Popen

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--docker-image")
    args = parser.parse_args()
    DOCKER_IMAGE = args.docker_image
    unittest.main(argv=[sys.argv[0]], verbosity=2)
