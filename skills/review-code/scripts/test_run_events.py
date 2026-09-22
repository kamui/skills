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
import re
import shlex
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest

import test_verifier_handoff as handoff

SCRIPTS = Path(__file__).resolve().parent
DOMAIN = {"host": "h", "boot": "b", "boot_source": "linux:boot_id", "implementation": "mono"}
HEAD = "a" * 40
S = 1_000_000_000

ECHO_CHILD = r"""
import os, sys
data = sys.stdin.buffer.read()
sys.stdout.buffer.write(b"out:" + data + b"\xff\x00no-newline")
sys.stderr.buffer.write(b"err:\xfe" + os.environ.get("RUN_EVENTS_PROBE", "").encode("utf-8"))
sys.exit(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
"""

WAITING_CHILD = r"""
import os, signal, sys, time
mode = sys.argv[2]
if mode == "exit-zero":
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
elif mode == "ignore":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
with open(sys.argv[1] + ".tmp", "w") as handle:
    handle.write(str(os.getpid()))
os.rename(sys.argv[1] + ".tmp", sys.argv[1])
time.sleep(60)
"""

FAKE_GH = "#!/usr/bin/env python3\nimport json, sys\nprint(json.dumps(sys.argv[1:]))\n"


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


def wrapped(name, start, end, exit=0, clock=None, argv0="gh", **data):
    item = event(name, start, end, exit=exit, clock=clock, argv0=argv0, signal=None, cancelled=None, **data)
    item["origin"]["script"] = "run_events.py"
    return item


def fetched(start, end, role="root", connection="root", **kw):
    return wrapped("forge-fetched", start, end, role=role, connection=connection, **kw)


def tested(start, end, **kw):
    kw.setdefault("head", HEAD)
    kw.setdefault("command", "python3 -m unittest test_a")
    return wrapped("focused-test-ran", start, end, argv0="python3", **kw)


def written(start, end, role="review", **kw):
    return wrapped("forge-written", start, end, role=role, **kw)


class RunEventTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.count = 0

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, script, *args, code=0, cwd=None, stdin=None):
        result = subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)], cwd=cwd, input=stdin,
                                capture_output=True, text=True, encoding="utf-8", timeout=120)
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
        self.assertEqual(events[0]["policy"]["workflow"], "v5b-22")
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

    def test_special_event_path_never_blocks(self):
        repo, base, head = self.repository()
        outputs = []
        for fifo in (False, True):
            private = self.root / f"special-{fifo}"
            private.mkdir()
            if fifo:
                os.mkfifo(private / "run-events.jsonl")  # no reader: a blocking open would hang
            store = private / "context.json"
            started = time.monotonic()
            built = subprocess.run([sys.executable, str(SCRIPTS / "review_context.py"), "--merge-base", base,
                                    "--head", head, "--store", str(store)], cwd=repo, capture_output=True,
                                   text=True, encoding="utf-8", timeout=20)
            composition = self.root / f"special-{fifo}.json"
            composition.write_text(json.dumps(self.composition(base, head)), encoding="utf-8")
            composed = subprocess.run([sys.executable, str(SCRIPTS / "compose_review.py"), "--store", str(store),
                                       str(composition)], capture_output=True, text=True, encoding="utf-8", timeout=20)
            self.assertLess(time.monotonic() - started, 20)
            outputs.append((built.returncode, built.stdout.replace(str(store), "STORE"), built.stderr,
                            composed.returncode, composed.stdout, composed.stderr))
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual((outputs[1][0], outputs[1][3]), (0, 0))
        self.assertTrue(stat.S_ISFIFO((self.root / "special-True" / "run-events.jsonl").stat().st_mode))

    def test_latest_accounting_follows_event_order(self):
        summary, _ = self.summarize([context(), brief("one", 10), brief("two", 20), accounted("two", 30),
                                     accounted("one", 50), payload(59)], "--completion-mode", "result")
        interval = summary["durations"]["last_accounting_to_validated_payload"]
        self.assertEqual((interval["seconds"], interval["status"]), (9.0, "proxy"))

    def test_malformed_fields_are_violations_not_crashes(self):
        cases = []
        bad = context()
        bad["clock"]["boot"] = {"nested": True}
        cases.append(("clock", bad))
        bad = payload(4)
        bad["ended_at"] = "not-a-timestamp"
        cases.append(("ended_at", bad))
        bad = payload(4)
        bad["ended_at"] = "2026-02-30T12:00:00Z"
        cases.append(("ended_at", bad))
        bad = context()
        bad["data"]["head"] = ["a"]
        cases.append(("identity fields", bad))
        bad = brief("one", 3)
        bad["data"]["batch_id"] = {"id": 1}
        cases.append(("identity fields", bad))
        bad = brief("one", 3)
        bad["data"]["candidates"] = "1"
        cases.append(("counts", bad))
        bad = accounted("one", 3)
        bad["data"]["returned"]["confirmed"] = -1
        cases.append(("data.returned", bad))
        bad = context()
        bad["origin"] = ["x"]
        cases.append(("origin", bad))
        bad = context()
        bad["policy"] = {"workflow": 17}
        cases.append(("policy", bad))
        for needle, line in cases:
            with self.subTest(needle=needle, line=line):
                self.count += 1
                sidecar = self.root / f"{self.count}-malformed-timing.json"
                summary, result = self.summarize([line], "--completion-mode", "result",
                                                 "--timing-sidecar", sidecar, code=1)
                self.assertIn(needle, result.stdout)
                self.assertEqual((summary["event_count"], summary["complete"]), (0, False))
                self.assertIsNone(json.loads(sidecar.read_text(encoding="utf-8"))["payload_validated_at"])
        # A rejected payload never exports a timestamp or reads as complete.
        bad = payload(4)
        bad["ended_at"] = "not-a-timestamp"
        sidecar = self.root / "rejected-timing.json"
        summary, _ = self.summarize([context(), bad], "--completion-mode", "result", "--timing-sidecar", sidecar, code=1)
        self.assertFalse(summary["complete"])
        self.assertIsNone(json.loads(sidecar.read_text(encoding="utf-8"))["completed_at"])

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

    # --- wrap ---------------------------------------------------------------

    def wrap(self, *args, stdin=None, env=None):
        return subprocess.run([sys.executable, str(SCRIPTS / "run_events.py"), "wrap", *map(str, args)],
                              input=stdin, capture_output=True, env=env, timeout=60)

    def events_in(self, private):
        path = Path(private) / "run-events.jsonl"
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def assert_one_wrapper_line(self, result):
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, b"")
        lines = result.stderr.decode("utf-8").splitlines()
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith("run_events:"), lines)

    def test_wrap_preserves_streams_environment_and_status(self):
        child = self.root / "echo.py"
        child.write_text(ECHO_CHILD, encoding="utf-8")
        private = self.root / "private"
        private.mkdir()
        env = dict(os.environ, RUN_EVENTS_PROBE="probe-é")
        stdin = b"in\x00\xffbytes\r\nno-final-newline"
        for code in (0, 1, 2, 42):
            with self.subTest(code=code):
                direct = subprocess.run([sys.executable, str(child), str(code)], input=stdin, capture_output=True,
                                        env=env, timeout=60)
                result = self.wrap("--private-dir", private, "--event", "forge-fetched", "--data", "role=root",
                                   "--data", "connection=root", "--", sys.executable, child, code, stdin=stdin, env=env)
                self.assertEqual(direct.returncode, code)
                self.assertEqual((result.returncode, result.stdout, result.stderr),
                                 (code, direct.stdout, direct.stderr))
        dump = [sys.executable, "-c", "import json, os, sys; sys.stdout.write(json.dumps(dict(os.environ), sort_keys=True))"]
        direct = subprocess.run(dump, capture_output=True, env=env, timeout=60)
        result = self.wrap("--private-dir", private, "--event", "focused-test-ran", "--data", f"head={HEAD}",
                           "--", *dump, env=env)
        self.assertEqual((result.returncode, result.stdout), (0, direct.stdout))
        self.assertEqual(json.loads(result.stdout)["RUN_EVENTS_PROBE"], "probe-é")

        events = self.events_in(private)
        self.assertEqual([e["exit"] for e in events], [0, 1, 2, 42, 0])
        self.assertEqual({e["origin"]["script"] for e in events}, {"run_events.py"})
        self.assertEqual(stat.S_IMODE((private / "run-events.jsonl").stat().st_mode), 0o600)
        self.assertEqual((events[0]["data"]["role"], events[0]["data"]["argv0"]), ("root", sys.executable))
        self.assertEqual(events[4]["data"]["command"], " ".join(dump))
        self.assertIsNone(events[4]["policy"])
        summary, _ = self.summarize(events, "--completion-mode", "result")
        self.assertEqual(summary["violations"], [])
        fetches = summary["commands"]["forge_fetches"]
        self.assertEqual((fetches["event_count"], fetches["failed_attempts"]), (4, 3))
        self.assertEqual([a["exit"] for a in fetches["attempts"]], [0, 1, 2, 42])
        self.assertEqual(summary["commands"]["focused_tests"]["attempts"][0]["head"], HEAD)

    def test_wrap_argument_errors_never_run_the_child(self):
        marker = self.root / "ran"
        touch = [sys.executable, "-c", f"open({str(marker)!r}, 'w').close()"]
        private = self.root / "private"
        private.mkdir()
        fetch = ["--event", "forge-fetched", "--data", "role=root", "--data", "connection=root"]
        cases = {
            "missing private dir": [*fetch, "--", *touch],
            "missing event": ["--private-dir", private, "--data", "role=root", "--", *touch],
            "missing separator": ["--private-dir", private, *fetch, *touch],
            "missing command": ["--private-dir", private, *fetch, "--"],
            "unknown event": ["--private-dir", private, "--event", "forge-read", "--", *touch],
            "unknown fetch role": ["--private-dir", private, "--event", "forge-fetched", "--data", "role=other",
                                   "--data", "connection=root", "--", *touch],
            "root with a connection": ["--private-dir", private, "--event", "forge-fetched", "--data", "role=root",
                                       "--data", "connection=reviews", "--", *touch],
            "continuation named root": ["--private-dir", private, "--event", "forge-fetched", "--data",
                                        "role=continuation", "--data", "connection=root", "--", *touch],
            "missing role": ["--private-dir", private, "--event", "forge-fetched", "--data", "connection=root",
                             "--", *touch],
            "short head": ["--private-dir", private, "--event", "focused-test-ran", "--data", "head=abc123",
                           "--", *touch],
            "derived command": ["--private-dir", private, "--event", "focused-test-ran", "--data", f"head={HEAD}",
                                "--data", "command=rm", "--", *touch],
            "duplicate role": ["--private-dir", private, "--event", "forge-written", "--data", "role=review",
                               "--data", "role=replies", "--", *touch],
            "malformed data": ["--private-dir", private, "--event", "forge-written", "--data", "rolereview",
                               "--", *touch],
            "unknown write role": ["--private-dir", private, "--event", "forge-written", "--data", "role=publish",
                                   "--", *touch],
        }
        for name, args in cases.items():
            with self.subTest(name=name):
                self.assert_one_wrapper_line(self.wrap(*args))
                self.assertFalse(marker.exists())
        self.assertFalse((private / "run-events.jsonl").exists())

    def test_wrap_unexecutable_child(self):
        private = self.root / "private"
        private.mkdir()
        not_executable = self.root / "not-executable.sh"
        not_executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        not_executable.chmod(0o644)
        for command in (self.root / "missing-program", not_executable):
            with self.subTest(command=command.name):
                self.assert_one_wrapper_line(self.wrap("--private-dir", private, "--event", "forge-written",
                                                       "--data", "role=review", "--", command))
        events = self.events_in(private)
        self.assertEqual([(e["event"], e["exit"]) for e in events], [("forge-written", 2)] * 2)

    def test_unusable_private_dir_changes_nothing(self):
        child = self.root / "echo.py"
        child.write_text(ECHO_CHILD, encoding="utf-8")
        blocked = self.root / "blocked"
        (blocked / "run-events.jsonl").mkdir(parents=True)
        readonly = self.root / "readonly"
        readonly.mkdir()
        readonly.chmod(0o500)
        try:
            direct = subprocess.run([sys.executable, str(child), "42"], input=b"x", capture_output=True, timeout=60)
            for directory in (self.root / "missing", blocked, readonly):
                with self.subTest(directory=directory.name):
                    result = self.wrap("--private-dir", directory, "--event", "forge-written", "--data",
                                       "role=replies", "--", sys.executable, child, "42", stdin=b"x")
                    self.assertEqual((result.returncode, result.stdout, result.stderr),
                                     (42, direct.stdout, direct.stderr))
            self.assertFalse((self.root / "missing").exists())
            if os.geteuid() != 0:
                self.assertFalse((readonly / "run-events.jsonl").exists())
        finally:
            readonly.chmod(0o700)

    def test_child_killed_by_a_signal_is_not_success(self):
        private = self.root / "private"
        private.mkdir()
        result = self.wrap("--private-dir", private, "--event", "forge-fetched", "--data", "role=ci", "--data",
                           "connection=ci", "--", sys.executable, "-c",
                           "import os, signal; os.kill(os.getpid(), signal.SIGTERM)")
        self.assertEqual((result.returncode, result.stderr), (128 + signal.SIGTERM, b""))
        recorded = self.events_in(private)[0]
        self.assertEqual((recorded["exit"], recorded["data"]["signal"], recorded["data"]["cancelled"]),
                         (128 + signal.SIGTERM, "SIGTERM", None))

    def test_caller_cancellation_stops_the_child_and_is_not_success(self):
        child = self.root / "waiting.py"
        child.write_text(WAITING_CHILD, encoding="utf-8")
        cases = (("default", 1, 128 + signal.SIGTERM, "SIGTERM"),
                 ("exit-zero", 1, 128 + signal.SIGTERM, None),
                 ("ignore", 2, 128 + signal.SIGKILL, "SIGKILL"))
        for mode, deliveries, expected, child_signal in cases:
            with self.subTest(mode=mode):
                private = self.root / f"cancel-{mode}"
                private.mkdir()
                ready = self.root / f"ready-{mode}"
                wrapper = subprocess.Popen([sys.executable, str(SCRIPTS / "run_events.py"), "wrap", "--private-dir",
                                            str(private), "--event", "focused-test-ran", "--data", f"head={HEAD}",
                                            "--", sys.executable, str(child), str(ready), mode])
                try:
                    deadline = time.monotonic() + 20
                    while not ready.exists() and time.monotonic() < deadline:
                        time.sleep(0.05)
                    pid = int(ready.read_text(encoding="utf-8"))
                    for _ in range(deliveries):
                        wrapper.send_signal(signal.SIGTERM)
                        time.sleep(0.5)
                    self.assertEqual(wrapper.wait(timeout=20), expected)
                finally:
                    if wrapper.poll() is None:
                        wrapper.kill()
                with self.assertRaises(ProcessLookupError):
                    os.kill(pid, 0)
                recorded = self.events_in(private)[0]
                self.assertEqual((recorded["exit"], recorded["data"]["cancelled"], recorded["data"]["signal"]),
                                 (expected, "SIGTERM", child_signal))

    def test_documented_wrapped_commands_run(self):
        sources = [SCRIPTS.parent / "references" / "pull-request-target.md",
                   SCRIPTS.parent.parent / "review-code-publish" / "references" / "publication.md"]
        binary = self.root / "bin"
        binary.mkdir()
        (binary / "gh").write_text(FAKE_GH, encoding="utf-8")
        (binary / "gh").chmod(0o755)
        env = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ.get("PATH", ""))
        script = shlex.quote(str(SCRIPTS / "run_events.py"))
        blocks = []
        for source in sources:
            if source.exists():
                documented = re.findall(r"```sh\n(.*?)```", source.read_text(encoding="utf-8"), re.S)
                self.assertTrue([block for block in documented if "run_events" in block or "run-events" in block],
                                f"{source.name} documents no wrapped command")
                # test_command_chains.py runs the freshness chain; test_thread_writes.py runs the write loop
                blocks.extend(block for block in documented
                              if ("run_events" in block or "run-events" in block)
                              and "preflight failed" not in block and "write-loop.sh" not in block)
        for number, block in enumerate(blocks):
            with self.subTest(block=number):
                private = self.root / f"documented-{number}"
                private.mkdir()
                text = (block.replace("<run-events-script>", script)
                        .replace("<forge-packet-script>", shlex.quote(str(SCRIPTS / "forge_packet.py")))
                        .replace("<skill-root>/scripts/run_events.py", script)
                        .replace("<private-dir>", shlex.quote(str(private))))
                text = re.sub(r"<[A-Za-z][A-Za-z0-9_.-]*>", "7", text)
                result = subprocess.run(["sh", "-c", text], cwd=self.root, env=env, capture_output=True,
                                        text=True, encoding="utf-8", timeout=60)
                self.assertEqual((result.returncode, result.stderr), (0, ""), text)
                events = self.events_in(private)
                self.assertEqual([e["data"]["argv0"] for e in events], ["gh"])
                self.summarize(events)
                saved = sorted(private.glob("forge-*.json"))
                for path in saved:
                    argv = json.loads(path.read_text(encoding="utf-8"))
                    self.assertIn("-F", argv)
                    self.assertIn("owner={owner}", argv)

    # --- wrapped-event summary ----------------------------------------------

    def test_wrapped_events_validate(self):
        events = [fetched(0, 1), context(), fetched(2, 3, "continuation", "reviewThreads"),
                  fetched(3, 4, "issue", "issue"), fetched(3, 5, "ci", "ci"), tested(4, 6), payload(8),
                  written(9, 10), written(10, 11, "replies"), written(11, 12, "resolutions"),
                  written(12, 13, "summary")]
        summary, _ = self.summarize(events, "--completion-mode", "result")
        self.assertEqual((summary["event_count"], summary["violations"], summary["complete"]), (11, [], True))
        self.assertEqual(summary["commands"]["publication_writes"]["by_role"],
                         {"review": 1, "replies": 1, "resolutions": 1, "summary": 1})
        cases = [("role must be one of", fetched(1, 2, role="other")),
                 ("requires connection=root", fetched(1, 2, connection="reviews")),
                 ("must name the requested connection", fetched(1, 2, "continuation", "ci")),
                 ("connection must name", fetched(1, 2, "continuation", "bad name")),
                 ("full lowercase commit SHA", tested(1, 2, head="abc")),
                 ("data.command", tested(1, 2, command=None)),
                 ("role must be one of", written(1, 2, role="publish")),
                 ("argv0", fetched(1, 2, argv0="")),
                 ("identity fields", fetched(1, 2, role=["root"]))]
        for needle, line in cases:
            with self.subTest(needle=needle):
                summary, result = self.summarize([line], code=1)
                self.assertIn(needle, result.stdout)
                self.assertEqual(summary["event_count"], 0)

    def test_overlapping_commands_are_counted_once(self):
        events = [fetched(0, 10), context(), fetched(5, 15, "continuation", "reviews", exit=1),
                  fetched(20, 25, "issue", "issue"), tested(3, 8), tested(6, 9, exit=1), payload(30),
                  written(31, 40), written(35, 45, "replies", exit=1)]
        summary, _ = self.summarize(events, "--completion-mode", "result")
        commands = summary["commands"]
        for group, count, failed, union in (("forge_fetches", 3, 1, 20.0), ("focused_tests", 2, 1, 6.0),
                                            ("publication_writes", 2, 1, 14.0)):
            with self.subTest(group=group):
                self.assertEqual((commands[group]["event_count"], commands[group]["failed_attempts"]), (count, failed))
                self.assertEqual((commands[group]["union_seconds"]["seconds"],
                                  commands[group]["union_seconds"]["status"]), (union, "captured"))
        self.assertEqual([a["exit"] for a in commands["forge_fetches"]["attempts"]], [0, 1, 0])
        for group in ("forge_fetches", "focused_tests", "publication_writes"):
            self.assertFalse([key for key in commands[group] if "sum" in key], commands[group])
        span = summary["durations"]["observed_span"]
        self.assertEqual(span["seconds"], 45.0)
        self.assertIn("not root elapsed", span["basis"])
        self.assertEqual(len(summary["script_failures"]), 3)
        self.assertTrue(summary["complete"])

    def test_independent_wrapped_events_may_append_out_of_order(self):
        events = [context(), fetched(0, 1), fetched(20, 40, "ci", "ci"),
                  fetched(10, 30, "continuation", "reviews"), tested(5, 12), payload(50)]
        summary, _ = self.summarize(events, "--completion-mode", "result")
        self.assertEqual((summary["clock"]["status"], summary["violations"]), ("single-domain", []))
        self.assertEqual(summary["commands"]["forge_fetches"]["union_seconds"]["seconds"], 31.0)
        self.assertEqual(summary["durations"]["context_to_validated_payload"]["seconds"], 48.0)
        self.assertTrue(summary["complete"])

        summary, result = self.summarize([context(20), fetched(1, 2), payload(10)], code=1)
        self.assertIn("ended_ns precedes", result.stdout)
        self.assertEqual(summary["clock"]["status"], "out-of-order")

        other = dict(DOMAIN, boot="rebooted")
        summary, _ = self.summarize([context(), fetched(3, 4, clock=other), payload(9)], "--completion-mode", "result")
        self.assertEqual(summary["clock"]["status"], "mixed")
        self.assertIsNone(summary["commands"]["forge_fetches"]["union_seconds"]["seconds"])

        for name, lines in (("started before", [context(), payload(20), written(10, 25)]),
                            ("appended before", [context(), written(21, 25), payload(20)])):
            with self.subTest(name=name):
                summary, result = self.summarize(lines, "--completion-mode", "result", code=1)
                self.assertIn("forge write precedes the validated payload", result.stdout)
                self.assertFalse(summary["complete"])

    def test_writes_never_complete_publication(self):
        scenarios = {
            "review written": [context(), payload(10), fetched(11, 12), written(12, 14)],
            "partial reply loop": [context(), payload(10), written(11, 13), written(13, 20, "replies", exit=1)],
            "no writes": [context(), payload(10)],
            "later failure": [context(), payload(10), written(11, 13), written(14, 15, "resolutions"),
                              fetched(16, 17), written(18, 19, "summary", exit=1)],
        }
        for name, events in scenarios.items():
            with self.subTest(name=name):
                self.count += 1
                sidecar = self.root / f"{self.count}-publication-timing.json"
                summary, _ = self.summarize(events, "--completion-mode", "publication", "--timing-sidecar", sidecar)
                self.assertEqual(summary["boundaries"]["final_result"]["status"], "unavailable")
                self.assertIn("caller or runtime evidence", summary["boundaries"]["final_result"]["reason"])
                self.assertIsNone(json.loads(sidecar.read_text(encoding="utf-8"))["completed_at"])
                self.assertFalse(summary["complete"])
                writes = summary["commands"]["publication_writes"]
                expected = [e["exit"] for e in events if e["event"] == "forge-written"]
                self.assertEqual([a["exit"] for a in writes["attempts"]], expected)
                if not expected:
                    self.assertEqual(writes["union_seconds"]["status"], "unavailable")
                    self.assertIn("unknown, not zero", writes["union_seconds"]["reason"])

    def test_mixed_heads_are_a_violation(self):
        other = payload(10)
        other["data"]["head"] = "b" * 40
        summary, result = self.summarize([context(), other], code=1)
        self.assertIn("more than one reviewed head", result.stdout)
        self.assertIsNone(summary["identity"]["reviewed_head"]["value"])


if __name__ == "__main__":
    os.chdir(SCRIPTS)
    unittest.main()
