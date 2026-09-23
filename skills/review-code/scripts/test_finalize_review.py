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
import hashlib
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


def run(args, cwd=SKILL, stdin=None, env=None):
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, input=stdin, capture_output=True, text=True, encoding="utf-8",
                          env=env)


def packet(threads):
    """A normalized packet pinning the fixture pull request, with the named threads."""
    return {"schema": "forge-packet/1", "repository_url": fixtures.REPO,
            "pr": {"title": "Retry charges", "body": "Closes #123.\n", "state": "OPEN", "merged": False, "base_ref": "main",
                   "base_sha": fixtures.BASE, "head_sha": HEAD, "repository_url": fixtures.REPO},
            "threads": [{"id": node, "is_resolved": False, "comments": [{"id": str(c), "body": "..."} for c in comments]}
                        for node, comments in threads.items()],
            "fingerprint": {"pr": {"title": "Retry charges", "body": "Closes #123.\n"},
                            "issues": [{"coordinate": "acme/payments#123", "title": "Retries", "body": "Reuse one key.",
                                        "comments": []}]}}


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
        derived = copy.deepcopy(composition)
        derived["run"]["target_kind"] = "pull-request"  # the packet's, filled into the retained composition
        report, finalization = self.succeeded(private, store, "--packet", private / "packet.json", composition=derived)
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
                                        ("repository", "requirements", "files", "check_evidence", "verification", "routed")]
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
            ("record-paths", lambda r: r["paths"].update(evidence_packet="evidence.md")),
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

    def test_non_utf8_stdio_keeps_the_bytes(self):
        """The derived composition reaches the composer intact whatever encoding its stdin uses."""
        outputs = []
        for encoding in ("utf-8", "latin-1"):
            private = self.directory("stdio")
            store = self.store(private)
            composition = self.composition(private, store)
            self.assertIn("—", composition["summary"]["issue_fit"], "the fixture carries non-ASCII prose")
            self.write(private, composition)
            result = run([FINALIZER, "--store", store, private], env=dict(os.environ, PYTHONIOENCODING=encoding))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            outputs.append({name: (private / name).read_bytes().replace(str(private).encode("utf-8"), b"<private>")
                            for name in (*PUBLIC, "report.md")})
            self.assertIn("Partial — retry", json.loads(outputs[-1]["payload.json"])["summary"]["body"])
        self.assertEqual(outputs[0], outputs[1])

    def test_malformed_inputs(self):
        private = self.directory("malformed")
        store = self.store(private)
        (private / "composition.json").write_text("{not json", encoding="utf-8")
        result = self.finalize(private, store)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("derive failed with exit 2", result.stdout)
        (private / "composition.json").write_text("[]", encoding="utf-8")
        result = self.finalize(private, store)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("input: schema:", result.stdout)
        self.write(private, self.composition(private, store))
        result = self.finalize(private, private / "absent-store.json")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("derive failed with exit 2", result.stdout)
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

        # A record naming an addenda directory elsewhere, as one written by hand could, guards that chain too; the
        # finalizer itself refuses to name any directory but its own.
        elsewhere = self.directory("moved")
        named = self.root / "named-addenda"
        named.mkdir()
        moved = self.composition(elsewhere, store, "implementation-gate", "range")
        self.write(elsewhere, moved)
        self.succeeded(elsewhere, store, profile="implementation-gate", composition=moved)
        moved["record"]["paths"]["addenda"] = str(named)
        self.write(elsewhere, moved)
        refused = self.finalize(elsewhere, store, profile="implementation-gate")
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn(f"record.paths: derived-field: `addenda={json.dumps(str(named))}` conflicts", refused.stdout)
        record = json.loads((elsewhere / "record.json").read_text(encoding="utf-8")) if (elsewhere / "record.json").exists() else None
        self.assertIsNone(record, "a refused run leaves no consumable record")
        self.write(elsewhere, self.composition(elsewhere, store, "implementation-gate", "range"))
        self.succeeded(elsewhere, store, profile="implementation-gate", composition=self.composition(elsewhere, store, "implementation-gate", "range"))
        record = json.loads((elsewhere / "record.json").read_text(encoding="utf-8"))
        record["record"]["paths"]["addenda"] = str(named)
        (elsewhere / "record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
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



# --- mechanical fields derived from the saved inputs ------------------------------

ISSUE = {"coordinate": "acme/payments#123", "title": "Retries must reuse one idempotency key",
         "body": "Acceptance criterion 2: one key per logical charge.\n",
         "comments": [{"id": 1001, "author": "octocat", "created_at": "2026-09-01T12:00:00Z",
                       "updated_at": "2026-09-01T12:00:00Z", "body": "Confirmed on the payments service."}]}
MESSAGE = "Keep the key\n\nReuse one idempotency key per logical charge.\n\n"
SPEC = {"identity": "spec/retries", "text": "Retries reuse one idempotency key per logical charge.\n"}


class Derive(unittest.TestCase):
    """Omitted mechanical fields come from the store, packet, fingerprint input and bundles; explicit copies are checked."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.count = 0
        self.stores: dict[str, Path] = {}
        for directory in ("src", "docs"):
            (self.repo / directory).mkdir(parents=True)
        self.git("init", "-q")
        self.write_files({"AGENTS.md": "Root rules.\n", "src/AGENTS.md": "Source rules.\n", "docs/notes.md": "notes\n"})
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD")
        self.git("checkout", "-qb", "retries")
        self.write_files({"docs/notes.md": "notes, changed\n"}, changed=42)
        self.git("add", ".")
        self.git("commit", "-q", "--cleanup=verbatim", "-m", MESSAGE)
        self.head = self.git("rev-parse", "HEAD")

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", *args], cwd=self.repo,
                              capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    def write_files(self, extra, changed=None):
        for name, count in (("src/payments.ts", 60), ("src/retry-policy.ts", 30), ("src/queue.ts", 10)):
            lines = [f"changed {i}" if changed and i in (changed, 18, 5) else f"line {i}" for i in range(1, count + 1)]
            (self.repo / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
        for name, text in extra.items():
            (self.repo / name).write_text(text, encoding="utf-8")

    # --- fixtures -------------------------------------------------------------

    def store(self, kind):
        """One store per target kind, shared by the directories that compare against each other."""
        if kind not in self.stores:
            path = self.root / f"store-{kind}.json"
            if kind == "worktree":
                (self.repo / "src" / "queue.ts").write_text("uncommitted\n", encoding="utf-8")
                args = ["--worktree", "--merge-base", self.base]
            else:
                args = ["--merge-base", self.base, "--head", self.head]
            built = run([SCRIPTS / "review_context.py", *args, "--store", path], cwd=self.repo)
            self.assertEqual(built.returncode, 0, built.stderr)
            self.stores[kind] = path
        return self.stores[kind]

    def context(self, kind):
        return json.loads(self.store(kind).read_text(encoding="utf-8"))["context"]

    def directory(self):
        self.count += 1
        private = self.root / f"private-{self.count}"
        private.mkdir()
        return private

    def bundle(self, private, tasks, name="initial", phase="initial"):
        """A verifier bundle manifest and the accounting report reconciled against it, as the helpers write them."""
        directory = private / name
        directory.mkdir()
        manifest = json.dumps({"format": "verifier-manifest/2", "batch": {"id": name, "phase": phase},
                               "candidate_ids": [t["id"] for t in tasks], "premise_ids": []}, indent=2).encode("utf-8")
        (directory / "manifest.json").write_bytes(manifest)
        (directory / "raw-return.json").write_text("{}\n", encoding="utf-8")
        accounting = directory / "accounting.json"
        fixtures.write_accounting(str(accounting), tasks)
        report = json.loads(accounting.read_text(encoding="utf-8"))
        report.update(manifest_sha256=hashlib.sha256(manifest).hexdigest(), raw_return=str(directory / "raw-return.json"))
        accounting.write_text(json.dumps(report), encoding="utf-8")
        return {"bundle": str(directory), "accounting": str(accounting), "operation": "Agent run_in_background=false"}

    def authored(self, private, kind, profile="publishable"):
        """What the reviewer writes: judgments, prose, and only the mechanical fields no saved input owns."""
        value = fixtures.gate_composition()
        value["run"] = {"coverage": "complete"}
        if kind != "pull-request":
            value["run"].update(base_ref="main", base_sha=self.base)
        if kind == "range":
            value["run"]["target_kind"] = "range"
        record = value["record"]
        record["repository"] = str(self.repo)
        if profile == "implementation-gate":
            record["paths"] = {"evidence_packet": str(self.root / "evidence.md")}
        else:
            del record["paths"]
        head = self.context(kind)["head"]
        for row in record["check_evidence"]:
            if row["head"] == fixtures.HEAD:
                row["head"] = head
        task = fixtures.candidate_task()
        record["verification"] = {"tasks": [task], "batches": [self.bundle(private, [task])],
                                  "allowance": {"initial_spent": True, "follow_up_spent": False, "carried_from": None},
                                  "outstanding": []}
        return value

    def explicit(self, private, kind, digest, profile="publishable"):
        """The same review with every mechanical field transcribed, as compositions were written before derivation."""
        value = self.authored(private, kind, profile)
        context = self.context(kind)
        value["run"].update(head=context["head"], merge_base=context["merge_base"], base_ref="main", base_sha=self.base,
                            context=digest, issues=["acme/payments#123"], merged=False, target_kind=kind)
        if kind == "pull-request":
            value["run"]["repository_url"] = fixtures.REPO
        else:
            value["run"].update(change_description=MESSAGE, specs=["spec/retries"])
        if kind == "range":
            value["run"]["target"] = "main...HEAD"
        if kind == "worktree":
            value["run"]["tree"] = context["snapshot"]["tree"]
        paths = value["record"].setdefault("paths", {})
        paths.update(private_dir=str(private), store=str(self.store(kind)), composition=str(private / "composition.json"),
                     skill_root=str(SKILL))
        if profile == "implementation-gate":
            paths["addenda"] = str(private / "addenda")
        for batch in value["record"]["verification"]["batches"]:
            batch.update(name="initial", phase="initial", raw_return=str(Path(batch["bundle"]) / "raw-return.json"))
        return value

    def fingerprint(self, private, kind, **change):
        if kind == "pull-request":
            value = {"specs": []}
        else:
            title = "main...HEAD" if kind == "range" else f"worktree tree={self.context(kind)['snapshot']['tree']}"
            value = {"pr": {"title": title, "body": MESSAGE}, "issues": [copy.deepcopy(ISSUE)], "specs": [dict(SPEC)]}
        value.update(change)
        path = private / "fingerprint.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def forge_packet(self, private, **pr):
        value = packet({})
        value["pr"].update({"base_sha": self.base, "head_sha": self.head, **pr})
        value["fingerprint"]["issues"] = [copy.deepcopy(ISSUE)]
        path = private / "packet.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def args(self, private, kind):
        """--packet on a pull request, and the saved fingerprint input on every target."""
        extra = ["--packet", self.forge_packet(private)] if kind == "pull-request" else []
        return [*extra, "--fingerprint-input", self.fingerprint(private, kind)]

    def finalize(self, private, kind, *extra, profile="publishable", composition=None):
        if composition is not None:
            (private / "composition.json").write_text(json.dumps(composition), encoding="utf-8")
        args = [FINALIZER, "--store", self.store(kind), *extra, private]
        if profile == "implementation-gate":
            args[1:1] = ["--profile", profile]
        return run(args, cwd=self.repo)

    def digest(self, fingerprint, packet_path=None, kind="range"):
        """The digest context_fingerprint.py prints for the same saved inputs."""
        extra = ["--packet", packet_path] if packet_path else []
        result = run([SCRIPTS / "context_fingerprint.py", *extra, "--guidance-base", self.base, "--store", self.store(kind),
                      fingerprint], cwd=self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def refused(self, result, stage, needle, private):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(f"{stage} failed with exit 1; later stages did not run:", result.stdout)
        self.assertIn(needle, result.stdout)
        self.assertEqual(sorted(n for n in (*PUBLIC, "record.json", "report.md") if (private / n).exists()), [])

    # --- targets ----------------------------------------------------------------

    def test_targets_derive_identity_paths_batches_and_digest(self):
        for profile, kind in (("publishable", "pull-request"), ("implementation-gate", "range"), ("publishable", "worktree")):
            with self.subTest(profile=profile, kind=kind):
                private = self.directory()
                extra = self.args(private, kind)
                result = self.finalize(private, kind, *extra, profile=profile, composition=self.authored(private, kind, profile))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                digest = self.digest(extra[-1], extra[1] if kind == "pull-request" else None, kind)
                if profile == "implementation-gate":
                    record = json.loads((private / "record.json").read_text(encoding="utf-8"))
                    finalization, derived_run, paths = record["finalization"], record["run"], record["record"]["paths"]
                    self.assertEqual((derived_run["target"], derived_run["specs"], derived_run["issues"]),
                                     ("main...HEAD", ["spec/retries"], ["acme/payments#123"]))
                    batch = record["record"]["verification"]["batches"][0]
                else:
                    retained = json.loads((private / "composition.json").read_text(encoding="utf-8"))
                    finalization, derived_run, paths = retained["finalization"], retained["run"], retained["record"]["paths"]
                    batch = retained["record"]["verification"]["batches"][0]
                context = self.context(kind)
                self.assertEqual((derived_run["head"], derived_run["merge_base"], derived_run["base_sha"], derived_run["context"]),
                                 (context["head"], context["merge_base"], self.base, digest))
                if kind == "pull-request":
                    self.assertEqual((derived_run["target_kind"], derived_run["repository_url"], derived_run["merged"], derived_run["issues"]),
                                     ("pull-request", fixtures.REPO, False, ["acme/payments#123"]))
                if kind == "worktree":
                    self.assertEqual((derived_run["target_kind"], derived_run["tree"], derived_run["change_description"]),
                                     ("worktree", context["snapshot"]["tree"], MESSAGE))
                expected = {"private_dir": str(private), "store": str(self.store(kind)), "composition": str(private / "composition.json"),
                            "skill_root": str(SKILL)}
                if profile == "implementation-gate":
                    expected.update(addenda=str(private / "addenda"), evidence_packet=str(self.root / "evidence.md"))
                self.assertEqual(paths, expected)
                self.assertEqual((batch["name"], batch["phase"], batch["raw_return"]),
                                 ("initial", "initial", str(private / "initial" / "raw-return.json")))
                self.assertEqual(finalization["inputs"], {"store": str(self.store(kind)), "fingerprint_input": str(extra[-1]),
                                                          "packet": str(extra[1]) if kind == "pull-request" else None})
                report = (private / "report.md").read_text(encoding="utf-8")
                self.assertIn(f"- fingerprint_input: `{extra[-1]}`", report)

                # Parity: the transcribed composition of the same review, with or without the saved inputs, renders the same bytes.
                for supplied in (True, False):
                    twin = self.directory()
                    twin_extra = self.args(twin, kind) if supplied else (["--packet", self.forge_packet(twin)] if kind == "pull-request" else [])
                    same = self.finalize(twin, kind, *twin_extra, profile=profile, composition=self.explicit(twin, kind, digest, profile))
                    self.assertEqual(same.returncode, 0, same.stdout + same.stderr)
                    for name in ARTIFACTS_OF[profile]:
                        mine, theirs = ((d / name).read_text(encoding="utf-8") for d in (private, twin))
                        if name == "record.json":
                            mine, theirs = (json.dumps({k: v for k, v in json.loads(t).items() if k not in ("record", "finalization")})
                                            for t in (mine, theirs))
                        self.assertEqual(mine, theirs, (name, supplied))

    def test_exact_bytes_and_unavailable_comments(self):
        body = "Keep the key\n\n\n"
        private = self.directory()
        fingerprint = self.fingerprint(private, "range", pr={"title": "main...HEAD", "body": body})
        result = self.finalize(private, "range", "--fingerprint-input", fingerprint, composition=self.authored(private, "range"))
        self.assertEqual(result.returncode, 0, result.stdout)
        retained = json.loads((private / "composition.json").read_text(encoding="utf-8"))
        self.assertEqual((retained["run"]["change_description"], retained["run"]["context"]), (body, self.digest(fingerprint)))
        private = self.directory()
        composition = self.authored(private, "range")
        composition["run"]["change_description"] = body.rstrip("\n")
        fingerprint = self.fingerprint(private, "range", pr={"title": "main...HEAD", "body": body})
        result = self.finalize(private, "range", "--fingerprint-input", fingerprint, composition=composition)
        self.refused(result, "derive", '`change_description="Keep the key"` conflicts with "Keep the key\\n\\n\\n"', private)

        digests = {}
        for name, issue in (("unavailable", {"comments": [], "comments_available": False}), ("empty", {"comments": []}),
                            ("listed", {})):
            private = self.directory()
            fingerprint = self.fingerprint(private, "range", issues=[dict(ISSUE, **issue)])
            result = self.finalize(private, "range", "--fingerprint-input", fingerprint, profile="implementation-gate",
                                   composition=self.authored(private, "range", "implementation-gate"))
            self.assertEqual(result.returncode, 0, result.stdout)
            digests[name] = json.loads((private / "record.json").read_text(encoding="utf-8"))["run"]["context"]
            self.assertEqual(digests[name], self.digest(fingerprint), name)
        self.assertEqual(len(set(digests.values())), 3, "unavailable, empty and listed comments are distinct inputs")

    def test_explicit_conflicts_are_refused(self):
        other = "f" * 40
        cases = [  # (target, change to the composition, packet change, needle)
            ("pull-request", {"run": {"head": other}}, {}, f"`head=\"{other}\"` conflicts"),
            ("pull-request", {"run": {"merge_base": other}}, {}, f"`merge_base=\"{other}\"` conflicts"),
            ("pull-request", {"run": {"base_sha": other}}, {}, f"`base_sha=\"{other}\"` conflicts"),
            ("pull-request", {"run": {"base_ref": "release"}}, {}, "`base_ref=\"release\"` conflicts"),
            ("pull-request", {"run": {"repository_url": "https://github.com/acme/other"}}, {}, "`repository_url=\"https://github.com/acme/other\"` conflicts"),
            ("pull-request", {"run": {"issues": []}}, {}, "`issues=[]` conflicts"),
            ("pull-request", {"run": {"merged": True}}, {}, "`merged=true` conflicts"),
            ("pull-request", {"run": {"target_kind": "range"}}, {}, "`target_kind=\"range\"` conflicts"),
            ("pull-request", {}, {"head_sha": other}, f"the packet pins head `{other}`"),
            ("range", {"run": {"target": "main..HEAD"}}, {}, "`target=\"main..HEAD\"` conflicts"),
            ("range", {"run": {"specs": ["spec/other"]}}, {}, "`specs=[\"spec/other\"]` conflicts"),
            ("range", {"run": {"merged": True}}, {}, "`merged=true` conflicts with false from a local target"),
            ("range", {"record": {"paths": {"skill_root": "/elsewhere/review-code"}}}, {}, "`skill_root=\"/elsewhere/review-code\"` conflicts"),
            ("range", {"record": {"paths": {"private_dir": "/tmp/another"}}}, {}, "`private_dir=\"/tmp/another\"` conflicts"),
            ("range", {"record": {"paths": {"store": "/tmp/another.json"}}}, {}, "`store=\"/tmp/another.json\"` conflicts"),
            ("range", {"batch": {"name": "follow-up"}}, {}, "`name=\"follow-up\"` conflicts"),
            ("range", {"batch": {"phase": "follow-up"}}, {}, "`phase=\"follow-up\"` conflicts"),
            ("range", {"batch": {"raw_return": "/tmp/repaired.json"}}, {}, "`raw_return=\"/tmp/repaired.json\"` conflicts"),
            ("worktree", {"run": {"tree": other}}, {}, f"`tree=\"{other}\"` conflicts"),
            ("worktree", {"run": {"target_kind": "range"}}, {}, "`target_kind=\"range\"` conflicts"),
        ]
        for kind, change, pr, needle in cases:
            with self.subTest(needle):
                private = self.directory()
                profile = "implementation-gate" if kind == "range" else "publishable"
                composition = self.authored(private, kind, profile)
                composition["run"].update(change.get("run", {}))
                composition["record"].setdefault("paths", {}).update(change.get("record", {}).get("paths", {}))
                composition["record"]["verification"]["batches"][0].update(change.get("batch", {}))
                extra = self.args(private, kind)
                if pr:
                    self.forge_packet(private, **pr)
                result = self.finalize(private, kind, *extra, profile=profile, composition=composition)
                self.refused(result, "derive", needle, private)

        # Explicit copies that agree are accepted, and so is a raw path spelled through a symlinked directory.
        private = self.directory()
        (self.root / "alias").symlink_to(private)
        composition = self.authored(private, "range", "implementation-gate")
        composition["run"].update(target="main...HEAD", merged=False, issues=["acme/payments#123"])
        composition["record"]["paths"]["private_dir"] = str(self.root / "alias")
        result = self.finalize(private, "range", *self.args(private, "range"), profile="implementation-gate", composition=composition)
        self.assertEqual(result.returncode, 0, result.stdout)

        # A bundle and an accounting report for different manifests do not pair.
        private = self.directory()
        composition = self.authored(private, "range", "implementation-gate")
        (private / "initial" / "manifest.json").write_text(json.dumps({"batch": {"id": "initial", "phase": "initial"}}), encoding="utf-8")
        result = self.finalize(private, "range", *self.args(private, "range"), profile="implementation-gate", composition=composition)
        self.refused(result, "derive", "accounts a return to another manifest", private)

    def test_stale_early_digest_is_refused(self):
        """A digest computed before the saved inputs changed, as the duplicate-review shortcut does, is never rebound."""
        private = self.directory()
        extra = self.args(private, "pull-request")
        stale = self.digest(extra[-1], extra[1], "pull-request")
        edited = json.loads(Path(extra[1]).read_text(encoding="utf-8"))
        edited["fingerprint"]["issues"][0]["comments"][0]["body"] = "Edited after the early digest."
        Path(extra[1]).write_text(json.dumps(edited), encoding="utf-8")
        composition = self.authored(private, "pull-request")
        composition["run"]["context"] = stale
        result = self.finalize(private, "pull-request", *extra, composition=composition)
        self.refused(result, "derive", f"`context={stale}` is not the digest of the saved inputs", private)
        composition["run"]["context"] = self.digest(extra[-1], extra[1], "pull-request")
        result = self.finalize(private, "pull-request", *extra, composition=composition)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_missing_authoritative_fields_and_inputs(self):
        cases = [
            ("merged unknown", "pull-request", {"merged": None}, None, "`merged` is omitted and the packet does not establish it"),
            ("no base", "pull-request", {"base_sha": ""}, None, "`base_sha` is omitted and the packet does not establish it"),
            ("no digest input", "range", {}, "no-fingerprint", "`context` is omitted; pass --fingerprint-input"),
            ("no pr", "range", {}, {"specs": []}, "`pr` is required unless --packet supplies it"),
            ("empty title", "range", {}, {"pr": {"title": "", "body": ""}}, "`target` is omitted and the fingerprint input's `pr.title` does not establish it"),
            ("guidance", "range", {}, {"pr": {"title": "t", "body": ""}, "guidance": []}, "the finalizer derives `guidance`"),
            ("pr beside packet", "pull-request", {}, {"pr": {"title": "t", "body": ""}}, "must not carry pr when --packet supplies it"),
            ("worktree title", "worktree", {}, {"pr": {"title": "worktree tree=" + "0" * 40, "body": ""}}, "a working tree's `pr.title` is `worktree tree="),
            ("no snapshot", "range", {}, "worktree-without-snapshot", "`tree` is omitted and"),
        ]
        for name, kind, pr, fingerprint, needle in cases:
            with self.subTest(name):
                private = self.directory()
                profile = "implementation-gate" if kind == "range" else "publishable"
                composition = self.authored(private, kind, profile)
                extra = self.args(private, kind)
                if kind == "pull-request" and pr:
                    self.forge_packet(private, **pr)
                if fingerprint == "no-fingerprint":
                    extra = []
                elif fingerprint == "worktree-without-snapshot":
                    composition["run"]["target_kind"] = "worktree"
                    profile = "publishable"
                elif fingerprint is not None:
                    (private / "fingerprint.json").write_text(json.dumps(fingerprint), encoding="utf-8")
                result = self.finalize(private, kind, *extra, profile=profile, composition=composition)
                self.refused(result, "derive", needle, private)
        private = self.directory()
        result = self.finalize(private, "range", "--fingerprint-input", private / "absent.json", profile="implementation-gate",
                               composition=self.authored(private, "range", "implementation-gate"))
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("derive failed with exit 2", result.stdout)

    def test_examples_finalize(self):
        """Each profile's --example, with only its placeholders pointed at this run, finalizes as written."""
        for profile, kind in (("publishable", "pull-request"), ("implementation-gate", "range")):
            with self.subTest(profile=profile):
                private = self.directory()
                shown = run([SCRIPTS / "compose_review.py", "--example", "--profile", profile])
                text = shown.stdout.replace("/tmp/review-code-XXXXXX", str(private))
                text = text.replace(fixtures.HEAD, self.head).replace(fixtures.BASE, self.base)
                example = json.loads(text)
                self.bundle(private, example["record"]["verification"]["tasks"])
                extra = self.args(private, kind)
                if kind == "pull-request":
                    threads = packet({"PRRT_kwDOABCD12": [1001]})["threads"]
                    value = json.loads(Path(extra[1]).read_text(encoding="utf-8"))
                    Path(extra[1]).write_text(json.dumps(dict(value, threads=threads)), encoding="utf-8")
                result = self.finalize(private, kind, *extra, profile=profile, composition=example)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue((private / "report.md").is_file())

    def test_omitted_judgments_are_never_approval(self):
        """Derivation fills no judgment: an omitted one stays an error, and no report or record says Approved."""
        cases = [
            ("coverage", lambda c: c["run"].pop("coverage"), "compose", "run.coverage: trailer-grammar"),
            ("status", lambda c: c["summary"].pop("status"), "compose", "summary.status: status-consistency"),
            ("files", lambda c: c["record"].pop("files"), "accounting", "`files` is required"),
            ("file state", lambda c: c["record"]["files"][0].pop("state"), "compose", "record.files[0]: schema: `state` is required"),
            ("ruling", lambda c: c["record"]["verification"]["tasks"][0].pop("ruling"), "compose", "`ruling` is required"),
            ("dispositions", lambda c: c["record"]["requirements"][0].pop("disposition"), "compose", "`disposition` is required"),
            ("allowance", lambda c: c["record"]["verification"].pop("allowance"), "accounting", "`allowance` is required"),
        ]
        for name, change, stage, needle in cases:
            with self.subTest(name):
                private = self.directory()
                composition = self.authored(private, "pull-request")
                change(composition)
                result = self.finalize(private, "pull-request", *self.args(private, "pull-request"), composition=composition)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(f"{stage} failed with exit 1", result.stdout)
                self.assertIn(needle, result.stdout)
                self.assertEqual(sorted(n for n in (*PUBLIC, "record.json", "report.md") if (private / n).exists()), [])


ARTIFACTS_OF = {"publishable": PUBLIC, "implementation-gate": ("record.json",)}


if __name__ == "__main__":
    unittest.main()
