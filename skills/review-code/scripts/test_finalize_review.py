#!/usr/bin/env python3
"""Exercise finalize_review.py through its CLI: accounting, reports, replies, staging, reruns, and --check.

Usage: python3 scripts/test_finalize_review.py
Inputs: synthetic stores and packets, the composer's fixture compositions, and an
injected failure or interruption for each write step; no forge access.
Exit 0: all checks pass; 1: a check fails; 2: a subprocess cannot run.

Every successful fixture must produce payload, batch, and fragment bytes (or the
gate record less its finalization) identical to the composer and validator run
directly, and a report carrying the summary body, each line comment's full body,
every ledger row, the routed state, and each drafted reply exactly once. Every
failure must leave no report and no consumable output, and a retry must restore
the clean run's bytes.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import compose_review as cr
import review_context as rc
import test_compose_review as fixtures

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
FINALIZER = SCRIPTS / "finalize_review.py"
HEAD, MERGE_BASE = fixtures.HEAD, fixtures.MERGE_BASE
TREE = "e" * 40
DELETED = "src/legacy-queue.ts"
MANIFEST = [{"path": "src/payments.ts", "status": "M"}, {"path": "src/retry-policy.ts", "status": "M"},
            {"path": "src/queue.ts", "status": "M"}, {"path": "docs/notes.md", "status": "M"}]
PUBLIC = ("payload.json", "batch.json", "fragments.md")

# A subprocess that runs the finalizer with one injected fault: `write` fails staging the report, `promote` fails
# promoting it, `interrupt` raises KeyboardInterrupt there, `kill` exits without cleanup there, and `stage-kill`
# exits without cleanup while the last stage (render, or the gate's record) runs.
INJECT = r"""
import os, pathlib, subprocess, sys
sys.path.insert(0, sys.argv[1])
import finalize_review
fault, sys.argv = sys.argv[2], ["finalize_review.py", *sys.argv[3:]]
real_replace, real_write, real_run = os.replace, pathlib.Path.write_bytes, subprocess.run
def replace(src, dst):
    if str(dst).endswith("report.md"):
        if fault == "promote":
            raise PermissionError(13, "injected promotion failure", str(dst))
        if fault == "interrupt":
            raise KeyboardInterrupt
        if fault == "kill":
            os._exit(137)
    return real_replace(src, dst)
def write_bytes(self, data):
    if fault == "write" and self.name == "report.md.part":
        raise OSError(28, "injected write failure", str(self))
    return real_write(self, data)
def run(command, *args, **kwargs):
    if fault == "stage-kill" and ("--render" in command or "implementation-gate" in command):
        os._exit(137)
    return real_run(command, *args, **kwargs)
os.replace, pathlib.Path.write_bytes, subprocess.run = replace, write_bytes, run
sys.exit(finalize_review.main())
"""


def run(args, cwd=SKILL, stdin=None):
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, input=stdin, capture_output=True, text=True, encoding="utf-8")


def packet(threads):
    return {"schema": "forge-packet/1", "threads": [
        {"id": node, "is_resolved": False, "comments": [{"id": str(c), "body": "..."} for c in comments]}
        for node, comments in threads.items()]}


class Finalize(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.count = 0

    def tearDown(self):
        self.temp.cleanup()

    # --- fixtures -------------------------------------------------------------

    def directory(self, name="run"):
        self.count += 1
        private = self.root / f"{name}-{self.count}"
        private.mkdir()
        return private

    def store(self, private, manifest=None, snapshot=False):
        context = {"head": HEAD, "merge_base": MERGE_BASE, "manifest": copy.deepcopy(manifest or MANIFEST)}
        if snapshot:
            context["snapshot"] = {"head": HEAD, "tree": TREE}
        path = private / f"review-context-{HEAD}.json"
        path.write_text(json.dumps({"format": rc.STORE_FORMAT, "context": context}), encoding="utf-8")
        return path

    def composition(self, private, store, profile="publishable", kind="pull-request"):
        value = fixtures.gate_composition()
        if kind == "pull-request":
            value["run"] = fixtures.base_composition()["run"]
        elif kind == "worktree":
            value["run"].update(target_kind="worktree", tree=TREE)
        paths = {"private_dir": str(private), "store": str(store), "composition": str(private / "composition.json"),
                 "skill_root": str(SKILL)}
        if profile == "implementation-gate":
            paths["addenda"] = str(private / "addenda")
        value["record"]["paths"] = paths
        return value

    def write(self, private, composition):
        (private / "composition.json").write_text(json.dumps(composition), encoding="utf-8")

    def finalize(self, private, store, *extra, profile="publishable"):
        args = [FINALIZER, "--store", store, *extra, private]
        if profile == "implementation-gate":
            args[1:1] = ["--profile", profile]
        return run(args)

    def check(self, private, profile="publishable"):
        return run([FINALIZER, "--check", "--profile", profile, private])

    def direct(self, private, store, profile="publishable"):
        """The public bytes the composer and validator print for the composition, or the gate record."""
        args = ["scripts/compose_review.py", "--store", store, private / "composition.json"]
        if profile == "implementation-gate":
            args[1:1] = ["--profile", profile]
        composed = subprocess.run([sys.executable, *map(str, args)], cwd=SKILL, capture_output=True)
        self.assertEqual(composed.returncode, 0, composed.stdout)
        if profile == "implementation-gate":
            return {"record.json": composed.stdout}
        out = {"payload.json": composed.stdout}
        for name, flag in (("batch.json", "--emit-batch"), ("fragments.md", "--render")):
            out[name] = subprocess.run([sys.executable, "scripts/validate_review.py", flag], cwd=SKILL, input=composed.stdout,
                                       capture_output=True, check=True).stdout
        return out

    def consumables(self, private):
        return sorted(name for name in (*PUBLIC, "record.json", "report.md") if (private / name).exists())

    def succeeded(self, private, store, *extra, profile="publishable", composition=None):
        """Finalize, then assert public-byte compatibility, a complete report, and a consumable --check."""
        expected = self.direct(private, store, profile)
        result = self.finalize(private, store, *extra, profile=profile)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = (private / "report.md").read_text(encoding="utf-8")
        if profile == "implementation-gate":
            self.assertEqual(result.stdout, f"record {private / 'record.json'}\n")
            record = json.loads((private / "record.json").read_text(encoding="utf-8"))
            finalization = record.pop("finalization")
            self.assertEqual((json.dumps(record, indent=2) + "\n").encode("utf-8"), expected["record.json"])
            self.assertTrue((private / "addenda").is_dir())
            payload = record
        else:
            self.assertEqual(result.stdout.encode("utf-8"), expected["fragments.md"])
            for name in PUBLIC:
                self.assertEqual((private / name).read_bytes(), expected[name], name)
            retained = json.loads((private / "composition.json").read_text(encoding="utf-8"))
            finalization = retained.pop("finalization")
            self.assertEqual(retained, composition, "the retained composition gains only its finalization")
            payload = json.loads(expected["payload.json"])
        self.assertEqual(finalization["protocol"], cr.FINALIZATION_PROTOCOL)
        self.assertEqual((finalization["profile"], finalization["report"]), (profile, str(private / "report.md")))
        self.assert_complete(report, payload, composition, finalization["replies"])
        self.assertEqual(sorted(p.name for p in private.glob("*.part")), [])
        checked = self.check(private, profile)
        self.assertEqual(checked.returncode, 0, checked.stdout)
        self.assertTrue(checked.stdout.endswith(f"report {private / 'report.md'}\n"), checked.stdout)
        compact = self.finalize(private, store, *extra, "--compact", profile=profile)
        self.assertEqual((compact.returncode, compact.stdout), (0, checked.stdout))
        return report, finalization

    def assert_complete(self, report, payload, composition, replies):
        body = payload["summary"]["body"]
        self.assertEqual(report.count(body.rstrip("\n")), 1, "the summary body appears once")
        for item in payload["items"]:
            self.assertEqual(report.count(item["markdown"]), 1, item.get("id", item["markdown"]))
            if item["type"] != "observation":
                self.assertEqual(report.count(item["trailer"]), 1, item["id"])
                if item["anchor"]["type"] == "line":
                    self.assertIn(f"### `{item['id']}`\n\n{item['markdown']}\n\n{item['trailer']}", report)
        record = composition["record"]
        self.assertIn(f"- Repository: `{record['repository']}`", report.split("## Run", 1)[1])
        for row in record["requirements"]:
            self.assertIn(f"- `{row['source']}` ({row['class']}): {row['disposition']}. {row['evidence']}", report)
        for row in record["files"]:
            self.assertIn(f"- `{row['path']}`: {row['state']}", report)
        for row in record["check_evidence"]:
            self.assertIn(f"- `{row['check']}` at `{row['head']}`: {row['outcome']}", report)
        verification = record["verification"]
        for task in verification["tasks"]:
            self.assertIn(f"`{task['id']}`", report.split("## Verification", 1)[1])
        for batch in verification["batches"]:
            self.assertIn(f"accounting `{batch['accounting']}`", report)
        for entry in verification["outstanding"]:
            self.assertIn(f"- Outstanding: {entry}", report)
        for entry in record["routed"]["unrecoverable_inputs"]:
            self.assertIn(f"- Unrecoverable input: {entry}", report)
        for key in ("unresolved", "disputed"):
            for identity in record["routed"][key]:
                self.assertIn(f"`{identity}`", report.split("## Routed", 1)[1])
        for reply in replies:
            if reply["body"] is not None:
                self.assertEqual(report.count(reply["body"]), 1, reply["id"])
        for key, value in record["paths"].items():
            self.assertIn(f"`{value}`", report.split("## Artifacts", 1)[1], key)

    # --- profiles, targets, and report contents --------------------------------

    def test_legal_profiles_and_targets(self):
        for profile, kind in (("publishable", "pull-request"), ("publishable", "range"), ("publishable", "worktree"),
                              ("implementation-gate", "range")):
            with self.subTest(profile=profile, kind=kind):
                private = self.directory(kind)
                store = self.store(private, snapshot=kind == "worktree")
                composition = self.composition(private, store, profile, kind)
                self.write(private, composition)
                self.succeeded(private, store, profile=profile, composition=composition)
        for kind in ("pull-request", "worktree"):
            with self.subTest(illegal=kind):
                private = self.directory(kind)
                store = self.store(private, snapshot=kind == "worktree")
                self.write(private, self.composition(private, store, "implementation-gate", kind))
                result = self.finalize(private, store, profile="implementation-gate")
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("record failed with exit 1", result.stdout)
                self.assertIn("run.target_kind: profile:", result.stdout)
                self.assertEqual(self.consumables(private), [])

    def test_clean_finding_question_observation_and_incomplete_reports(self):
        private = self.directory("clean")
        store = self.store(private)
        clean = self.composition(private, store)
        clean.update(findings=[], questions=[], observations=[])
        clean["summary"]["status"] = "Approved"
        clean["record"]["verification"] = fixtures.verification([], [])
        self.write(private, clean)
        report, _ = self.succeeded(private, store, composition=clean)
        self.assertNotIn("## Line comments", report)
        self.assertIn("- Allowance: initial batch unspent, follow-up unspent.", report)

        private = self.directory("items")
        store = self.store(private)
        items = self.composition(private, store)
        items["questions"][0]["anchor"] = {"type": "line", "path": "src/queue.ts", "start_line": 5, "end_line": 5, "side": "RIGHT"}
        self.write(private, items)
        report, _ = self.succeeded(private, store, composition=items)
        section = report.split("## Line comments", 1)[1].split("\n## ", 1)[0]
        self.assertIn("### `payments/retry-idempotency`", section)
        self.assertIn("### `queue/retry-order`", section)

        private = self.directory("incomplete")
        store = self.store(private)
        incomplete = self.composition(private, store)
        incomplete.update(findings=[], observations=[])
        incomplete["run"]["coverage"] = "incomplete"
        incomplete["summary"].update(status="Incomplete", coverage_gaps=["`src/queue.ts` unreviewed: diff chunk missing"])
        incomplete["record"]["files"][2]["state"] = "unreviewed"
        incomplete["record"]["verification"] = fixtures.verification(
            [fixtures.premise_task(batch=None, ruling="pending")], [], outstanding=["premise-1: no awaited route"])
        incomplete["record"]["routed"]["unrecoverable_inputs"] = ["the spec's benchmark artifact"]
        self.write(private, incomplete)
        report, _ = self.succeeded(private, store, composition=incomplete)
        self.assertIn("- `src/queue.ts`: unreviewed", report)

    def test_every_anchor_form_carries_each_body_once(self):
        private = self.directory("anchors")
        store = self.store(private, MANIFEST + [{"path": DELETED, "status": "D"}])
        composition = self.composition(private, store)
        line = fixtures.finding()
        span = fixtures.consider(id="payments/retry-span", anchor={"type": "line", "path": "src/payments.ts", "start_line": 40,
                                                                    "end_line": 44, "side": "LEFT"})
        span.pop("fix", None)
        whole = fixtures.consider(id="docs/notes-scope", title="Scope the notes to the release", anchor={"type": "file", "path": "docs/notes.md"},
                                  change="Scope `docs/notes.md` to this release.")
        whole.pop("fix", None)
        deleted = fixtures.consider(id="queue/legacy-callers", title="Keep the legacy queue callers working",
                                    anchor={"type": "file", "path": DELETED}, change=f"Restore `{DELETED}` or move its callers.")
        deleted.pop("fix", None)
        unknown = fixtures.consider(id="queue/unknown-origin", title="Name the queue's origin", anchor={"type": "file", "path": "src/queue.ts", "side": "UNKNOWN"},
                                    change="Name where `src/queue.ts` is generated from.")
        unknown.pop("fix", None)
        line_question = copy.deepcopy(composition["questions"][0])
        line_question.update(id="queue/retry-line", title="Must line five retry?",
                             anchor={"type": "line", "path": "src/queue.ts", "start_line": 5, "end_line": 5, "side": "RIGHT"})
        composition["findings"] = [line, span, whole, deleted, unknown]
        composition["questions"].append(line_question)
        composition["record"]["files"].append({"path": DELETED, "state": "reviewed"})
        self.write(private, composition)
        report, _ = self.succeeded(private, store, composition=composition)
        section = report.split("## Line comments", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(section.count("### "), 3, section)
        for body_carried in ("docs/notes-scope", "queue/legacy-callers", "queue/unknown-origin", "queue/retry-order"):
            self.assertNotIn(f"### `{body_carried}`", report)

    def test_prior_items_persist_replies_with_trailers_privately(self):
        private = self.directory("prior")
        store = self.store(private)
        composition = self.composition(private, store)
        composition["run"]["prior_head"] = fixtures.PRIOR
        composition["prior_items"] = [
            {"id": "queue/old-fixed", "classification": "fixed", "action": "must-fix", "note": "Fixed at the head.",
             "reply": "Fixed: the key is reused.\n", "thread_id": "PRRT_fixed", "comment_id": 101},
            {"id": "queue/old-open", "classification": "still-open", "action": "consider", "note": "Still open.",
             "reply": "Still open: see `src/queue.ts:5`, and ``` fences ```.", "thread_id": "PRRT_open", "comment_id": 201},
            {"id": "docs/old-unverifiable", "classification": "not-verifiable", "action": "question", "note": "Needs the owner.",
             "reply": "Cannot verify without the benchmark.", "thread_id": "PRRT_nv", "comment_id": 301},
            {"id": "api/old-disputed", "classification": "disputed", "action": "consider", "note": "Author declined twice.",
             "reply": None, "thread_id": "PRRT_disputed", "comment_id": 401},
            {"id": "cli/old-accepted", "classification": "accepted", "action": "consider", "note": "Risk accepted by the owner.",
             "thread_id": "PRRT_accepted", "comment_id": 501},
            {"id": "log/old-obsolete", "classification": "obsolete", "action": "consider", "note": "The code is gone.",
             "thread_id": None, "comment_id": None},
        ]
        composition["record"]["routed"]["disputed"] = ["api/old-disputed"]
        threads = packet({"PRRT_fixed": [101, 102], "PRRT_open": [201], "PRRT_nv": [301], "PRRT_disputed": [401],
                          "PRRT_accepted": [501], "PRRT_other": [601]})
        (private / "packet.json").write_text(json.dumps(threads), encoding="utf-8")
        self.write(private, composition)
        report, finalization = self.succeeded(private, store, "--packet", private / "packet.json", composition=composition)
        trailer = "<!-- prior-item id={} classification={} head=" + HEAD + " -->"
        self.assertEqual([(r["id"], r["thread_id"], r["comment_id"], r["body"]) for r in finalization["replies"]], [
            ("queue/old-fixed", "PRRT_fixed", 101, "Fixed: the key is reused.\n\n" + trailer.format("queue/old-fixed", "fixed")),
            ("queue/old-open", "PRRT_open", 201,
             "Still open: see `src/queue.ts:5`, and ``` fences ```.\n\n" + trailer.format("queue/old-open", "still-open")),
            ("docs/old-unverifiable", "PRRT_nv", 301, "Cannot verify without the benchmark."),
            ("api/old-disputed", "PRRT_disputed", 401, None),
            ("cli/old-accepted", "PRRT_accepted", 501, None),
            ("log/old-obsolete", None, None, None),
        ])
        self.assertIn("````markdown\nStill open:", report, "a fence longer than any backtick run in the reply")
        self.assertIn("### `log/old-obsolete`: obsolete\n\nNo forge thread. No drafted reply.", report)
        public = "".join((private / name).read_text(encoding="utf-8") for name in PUBLIC)
        for field in ("Fixed: the key is reused.", "PRRT_fixed", "prior-item id="):
            self.assertNotIn(field, public, "reply fields stay private")
        bare = copy.deepcopy(composition)
        for prior in bare["prior_items"]:
            for key in ("reply", "thread_id", "comment_id"):
                prior.pop(key, None)
        plain = self.directory("prior-plain")
        bare["record"]["paths"]["store"] = str(store)
        self.write(plain, bare)
        self.assertEqual(self.direct(plain, store)["payload.json"], (private / "payload.json").read_bytes())

    def test_missing_accounting_is_refused_for_either_profile(self):
        for profile, kind in (("publishable", "pull-request"), ("implementation-gate", "range")):
            removals = [("record",)] + [("record", key) for key in
                                        ("repository", "paths", "requirements", "files", "check_evidence", "verification", "routed")]
            removals += [("record", "verification", key) for key in ("tasks", "batches", "allowance", "outstanding")]
            removals += [("record", "routed", key) for key in ("unresolved", "disputed", "unrecoverable_inputs")]
            for path in removals:
                with self.subTest(profile=profile, missing=".".join(path)):
                    private = self.directory("accounting")
                    store = self.store(private)
                    composition = self.composition(private, store, profile, kind)
                    target = composition
                    for key in path[:-1]:
                        target = target[key]
                    del target[path[-1]]
                    self.write(private, composition)
                    (private / "report.md").write_text("stale success\n", encoding="utf-8")
                    result = self.finalize(private, store, profile=profile)
                    self.assertEqual(result.returncode, 1, result.stdout)
                    self.assertIn("accounting failed with exit 1; later stages did not run:", result.stdout)
                    self.assertIn(": accounting: ", result.stdout)
                    self.assertEqual(self.consumables(private), [])

    def test_publishable_accounting_contradictions_are_refused(self):
        def bad(change):
            private = self.directory("contradiction")
            store = self.store(private)
            composition = self.composition(private, store)
            change(composition["record"])
            self.write(private, composition)
            return private, store

        cases = [
            ("file-accounting", lambda r: r["files"].pop()),
            ("check-evidence", lambda r: r["check_evidence"][0].update(head=fixtures.PRIOR)),
            ("stable-id", lambda r: r["routed"]["unresolved"].append("payments/unknown")),
            ("verification", lambda r: r["verification"].update(tasks=[])),
            ("requirements", lambda r: r["requirements"][0].update({"class": "wish"})),
            ("record-paths", lambda r: r["paths"].pop("skill_root")),
            ("coverage-gaps", lambda r: r["routed"]["unrecoverable_inputs"].append("the benchmark")),
        ]
        for rule, change in cases:
            with self.subTest(rule=rule):
                private, store = bad(change)
                result = self.finalize(private, store)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("compose failed with exit 1", result.stdout)
                self.assertIn(f": {rule}: ", result.stdout)
                self.assertEqual(self.consumables(private), [])

    def test_invalid_reply_ids_and_packets(self):
        good = {"id": "queue/old-open", "classification": "still-open", "action": "consider", "note": "Still open.",
                "reply": "Still open.", "thread_id": "PRRT_open", "comment_id": 201}
        cases = [
            ("unknown thread", {"thread_id": "PRRT_missing"}, "names no thread in the packet"),
            ("not the first comment", {"comment_id": 202}, "is not the first comment"),
            ("reply without thread", {"thread_id": None, "comment_id": None}, "needs the packet's `thread_id`"),
            ("half the ids", {"comment_id": None}, "both set, or both null"),
            ("string comment id", {"comment_id": "201"}, "both set, or both null"),
            ("disputed reply", {"classification": "disputed"}, "drafts no `reply`"),
            ("authored trailer", {"reply": f"Open.\n\n<!-- prior-item id=queue/old-open classification=still-open head={HEAD} -->"},
             "carries a prior-item trailer"),
            ("empty reply", {"reply": " "}, "drafted reply prose, or null"),
            ("no packet", {}, "pass `--packet`"),
        ]
        threads = packet({"PRRT_open": [201, 202]})
        for name, change, needle in cases:
            with self.subTest(name):
                private = self.directory("reply")
                store = self.store(private)
                composition = self.composition(private, store)
                composition["run"]["prior_head"] = fixtures.PRIOR
                composition["prior_items"] = [dict(good, **change)]
                self.write(private, composition)
                (private / "packet.json").write_text(json.dumps(threads), encoding="utf-8")
                extra = [] if name == "no packet" else ["--packet", private / "packet.json"]
                result = self.finalize(private, store, *extra)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("accounting failed with exit 1", result.stdout)
                self.assertIn("prior_items[0]: prior-reply: ", result.stdout)
                self.assertIn(needle, result.stdout)
                self.assertEqual(self.consumables(private), [])
        private = self.directory("packet")
        store = self.store(private)
        composition = self.composition(private, store)
        composition["prior_items"] = [good]
        self.write(private, composition)
        (private / "packet.json").write_text(json.dumps({"schema": "forge-packet/0"}), encoding="utf-8")
        result = self.finalize(private, store, "--packet", private / "packet.json")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("packet: schema:", result.stdout)
        result = self.finalize(private, store, "--packet", private / "absent.json")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("cannot read packet", result.stdout)

    def test_malformed_inputs(self):
        private = self.directory("malformed")
        store = self.store(private)
        (private / "composition.json").write_text("{not json", encoding="utf-8")
        result = self.finalize(private, store)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("accounting failed with exit 2", result.stdout)
        (private / "composition.json").write_text("[]", encoding="utf-8")
        result = self.finalize(private, store)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("input: schema:", result.stdout)
        self.write(private, self.composition(private, store))
        result = self.finalize(private, private / "absent-store.json")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("compose failed with exit 2", result.stdout)
        store.write_text(json.dumps({"format": "other"}), encoding="utf-8")
        result = self.finalize(private, store)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("store: schema:", result.stdout)
        missing = run([FINALIZER, private])
        self.assertEqual(missing.returncode, 2, missing.stderr)
        self.assertIn("--store is required", missing.stderr)
        self.assertEqual(self.consumables(private), [])

    # --- staging, failures, retries ------------------------------------------

    def stub(self, stage):
        """A python3 on PATH whose named stage fails; every other command runs normally."""
        binary = self.root / f"bin-{stage}"
        binary.mkdir()
        flag = {"compose": "compose_review.py", "record": "compose_review.py", "emit-batch": "--emit-batch", "render": "--render"}[stage]
        (binary / "python3").write_text(
            f'#!/bin/sh\ncase " $* " in *"{flag}"*) echo "injected: {stage} refused"; exit 1;; esac\n'
            f'exec "{sys.executable}" "$@"\n', encoding="utf-8")
        (binary / "python3").chmod(0o755)
        return dict(os.environ, PATH=f"{binary}{os.pathsep}{os.environ['PATH']}")

    def clean_run(self, profile="publishable"):
        private = self.directory(profile)
        store = self.store(private)
        composition = self.composition(private, store, profile, "pull-request" if profile == "publishable" else "range")
        self.write(private, composition)
        self.succeeded(private, store, profile=profile, composition=composition)
        outputs = {name: (private / name).read_bytes() for name in (*PUBLIC, "record.json", "report.md", "composition.json")
                   if (private / name).exists()}
        return private, store, composition, outputs

    def assert_restored(self, private, store, composition, outputs, profile):
        self.write(private, composition)
        retry = self.finalize(private, store, profile=profile)
        self.assertEqual(retry.returncode, 0, retry.stdout + retry.stderr)
        self.assertEqual({name: (private / name).read_bytes() for name in outputs}, outputs, "a retry restores the clean run")

    def test_each_stage_failure_leaves_nothing_consumable_and_a_retry_restores(self):
        for profile, stages in (("publishable", ("compose", "emit-batch", "render")), ("implementation-gate", ("record",))):
            private, store, composition, outputs = self.clean_run(profile)
            for stage in stages:
                with self.subTest(profile=profile, stage=stage):
                    args = [FINALIZER, "--profile", profile, "--store", store, private]
                    result = subprocess.run([sys.executable, *map(str, args)], cwd=SKILL, capture_output=True, text=True,
                                            encoding="utf-8", env=self.stub(stage))
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn(f"{stage} failed with exit 1; later stages did not run:\ninjected: {stage} refused", result.stdout)
                    self.assertEqual(self.consumables(private), [])
                    self.assertEqual(sorted(p.name for p in private.glob("*.part")), [])
                    self.assertNotEqual(self.check(private, profile).returncode, 0)
                    self.assert_restored(private, store, composition, outputs, profile)

    def test_write_promotion_and_interruption_failures(self):
        for profile in ("publishable", "implementation-gate"):
            private, store, composition, outputs = self.clean_run(profile)
            # An uncaught KeyboardInterrupt ends Python by SIGINT once its cleanup ran.
            for fault, status in (("write", 2), ("promote", 2), ("interrupt", -2), ("kill", 137), ("stage-kill", 137)):
                with self.subTest(profile=profile, fault=fault):
                    result = run(["-c", INJECT, SCRIPTS, fault, "--profile", profile, "--store", store, private])
                    self.assertEqual(result.returncode, status, result.stdout + result.stderr)
                    self.assertFalse((private / "report.md").exists(), "no report without a complete run")
                    if fault in ("write", "promote", "interrupt"):
                        self.assertEqual(self.consumables(private), [], "cleanup removes what this run promoted")
                        self.assertEqual(sorted(p.name for p in private.glob("*.part")), [])
                    if fault in ("write", "promote"):
                        self.assertIn("cannot write output", result.stderr)
                    checked = self.check(private, profile)
                    self.assertEqual(checked.returncode, 1, checked.stdout)
                    self.assertIn("unconsumable:", checked.stdout)
                    self.assert_restored(private, store, composition, outputs, profile)
            # A hard kill between promotions leaves earlier outputs without the report; they never read as success.
            run(["-c", INJECT, SCRIPTS, "kill", "--profile", profile, "--store", store, private])
            self.assertTrue(self.consumables(private))
            self.assertIn("does not exist, so its finalization did not complete", self.check(private, profile).stdout)

    def test_stale_outputs_of_either_profile_are_removed_first(self):
        private = self.directory("stale")
        store = self.store(private)
        composition = self.composition(private, store)
        self.write(private, composition)
        for name in (*PUBLIC, "report.md", "payload.json.part", "composition.json.part"):
            (private / name).write_text("stale success\n", encoding="utf-8")
        (private / "record.json").write_text(json.dumps({"record": {"paths": {"addenda": str(private / "addenda")}}}), encoding="utf-8")
        self.succeeded(private, store, composition=composition)
        self.assertFalse((private / "record.json").exists(), "a publishable run never keeps or fabricates a gate record")
        blocked = self.directory("blocked")
        (blocked / "report.md").mkdir()
        self.write(blocked, self.composition(blocked, store))
        result = self.finalize(blocked, store)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("cannot remove stale output", result.stderr)

    # --- reruns, profile reuse, active chains -------------------------------------

    def snapshot_unreadable(self, private):
        """Paths and, where readable, bytes: a mode-000 file is compared by presence and mode."""
        out = {}
        for path in sorted(private.rglob("*")):
            try:
                out[str(path.relative_to(private))] = path.read_bytes() if path.is_file() else None
            except PermissionError:
                out[str(path.relative_to(private))] = oct(path.stat().st_mode)
        return out

    def snapshot(self, private):
        return {str(p.relative_to(private)): (p.read_bytes() if p.is_file() else None) for p in sorted(private.rglob("*"))}

    def test_profile_reuse_and_active_chains(self):
        private = self.directory("reuse")
        store = self.store(private)
        gate = self.composition(private, store, "implementation-gate", "range")
        publishable = self.composition(private, store, "publishable", "range")
        self.write(private, publishable)
        self.succeeded(private, store, composition=publishable)
        self.write(private, gate)
        self.succeeded(private, store, profile="implementation-gate", composition=gate)
        self.assertEqual([name for name in PUBLIC if (private / name).exists()], [], "a profile switch removes the other profile's outputs")
        self.assertEqual(self.check(private, "publishable").returncode, 1)
        self.assertTrue((private / "addenda").is_dir())
        self.write(private, publishable)
        self.succeeded(private, store, composition=publishable)  # an empty addenda directory is not an active chain
        self.assertFalse((private / "record.json").exists())

        self.write(private, gate)
        self.succeeded(private, store, profile="implementation-gate", composition=gate)
        (private / "addenda" / f"addendum-{HEAD}.json").write_text("{}", encoding="utf-8")
        before = self.snapshot(private)
        for profile, value in (("implementation-gate", gate), ("publishable", publishable)):
            with self.subTest(active=profile):
                self.write(private, value)
                before["composition.json"] = (private / "composition.json").read_bytes()
                result = self.finalize(private, store, profile=profile)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("finalize refused:", result.stdout)
                self.assertIn(f"addendum-{HEAD}.json", result.stdout)
                self.assertEqual(self.snapshot(private), before, "a refused rerun modifies nothing")

        # A record naming an addenda directory elsewhere guards that chain too.
        elsewhere = self.directory("moved")
        named = self.root / "named-addenda"
        named.mkdir()
        moved = self.composition(elsewhere, store, "implementation-gate", "range")
        moved["record"]["paths"]["addenda"] = str(named)
        self.write(elsewhere, moved)
        self.succeeded(elsewhere, store, profile="implementation-gate", composition=moved)
        (named / "addendum-1.json").write_text("{}", encoding="utf-8")
        result = self.finalize(elsewhere, store, profile="implementation-gate")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(str(named), result.stdout)

        # A record that cannot name its addenda directory is refused too: it may head a chain kept elsewhere.
        intact = (elsewhere / "record.json").read_bytes()
        for name, damage in (("truncated", lambda path: path.write_bytes(intact[:200])),
                             ("no addenda path", lambda path: path.write_text(json.dumps({"record": {"paths": {}}}), encoding="utf-8")),
                             ("unreadable", lambda path: path.chmod(0))):
            if name == "unreadable" and hasattr(os, "geteuid") and os.geteuid() == 0:
                continue  # root reads a mode-000 file
            with self.subTest(record=name):
                (elsewhere / "record.json").write_bytes(intact)
                damage(elsewhere / "record.json")
                before = self.snapshot_unreadable(elsewhere)
                for profile in ("implementation-gate", "publishable"):
                    result = self.finalize(elsewhere, store, profile=profile)
                    self.assertEqual(result.returncode, 1, result.stdout)
                    self.assertIn("cannot establish which addenda directory", result.stdout)
                    self.assertEqual(self.snapshot_unreadable(elsewhere), before, "a refused rerun modifies nothing")
                (elsewhere / "record.json").chmod(0o644)

    # --- consumers ----------------------------------------------------------------

    def test_check_reads_legacy_outputs_and_refuses_unknown_or_incomplete(self):
        private = self.directory("legacy-gate")
        store = self.store(private)
        gate = self.composition(private, store, "implementation-gate", "range")
        self.write(private, gate)
        (private / "record.json").write_bytes(self.direct(private, store, "implementation-gate")["record.json"])
        result = self.check(private, "implementation-gate")
        self.assertEqual((result.returncode, result.stdout), (0, f"legacy {private / 'record.json'}\n"))

        record = json.loads((private / "record.json").read_text(encoding="utf-8"))
        for name, doc, needle in (
            ("version-1 record", dict(record, schema="implementation-gate-record/1"), "not a valid implementation-gate-record/2"),
            ("invalid payload", dict(record, summary={}), "not a valid implementation-gate-record/2"),
            ("unknown protocol", dict(record, finalization={"protocol": "review-code-finalization/2", "report": str(private / "report.md")}),
             "unknown finalization protocol"),
            ("missing report", dict(record, finalization={"protocol": cr.FINALIZATION_PROTOCOL, "profile": "implementation-gate",
                                                          "report": str(private / "report.md")}), "does not exist"),
            ("other profile", dict(record, finalization={"protocol": cr.FINALIZATION_PROTOCOL, "profile": "publishable",
                                                         "report": str(private / "composition.json")}), "not `implementation-gate`"),
        ):
            with self.subTest(name):
                (private / "record.json").write_text(json.dumps(doc), encoding="utf-8")
                result = self.check(private, "implementation-gate")
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(needle, result.stdout)

        private = self.directory("legacy-publishable")
        store = self.store(private)
        self.write(private, self.composition(private, store))
        for name, data in self.direct(private, store).items():
            (private / name).write_bytes(data)
        result = self.check(private)
        self.assertEqual((result.returncode, result.stdout), (0, f"legacy {private / 'payload.json'}\n"))
        (private / "batch.json").unlink()
        self.assertEqual(self.check(private).returncode, 1)
        self.assertEqual(self.check(self.directory("empty")).returncode, 1)


if __name__ == "__main__":
    unittest.main()
