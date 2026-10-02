#!/usr/bin/env python3
"""Exercise render_review.py through its CLI: records, reports, derivation, staging, --check and prior records.

Usage: python3 scripts/test_render_review.py
Inputs: synthetic stores and packets, disposable Git repositories, the composition fixtures,
and an injected failure or interruption for each write step; no forge access.
Exit 0: all checks pass; 1: a check fails; 2: a subprocess cannot run.

Every successful fixture must write a record carrying the payload it validated, a batch
equal to that payload's projection, and a report carrying the summary body, each line
comment's full body, every ledger row, the routed state, and each drafted reply exactly
once. Every failure must leave no report and no consumable output, and a retry must
restore the clean run's bytes. The prior-record fixtures cover each refusal of the
one-hop check, a two-hop lineage with a carried confirmation, allowance carry, an
exhausted allowance after a fixed ordinary must-fix, and a sibling fork that only the
caller's lineage check can reject.
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

import forge_packet
import render_review as rr
import review_context as rc
import test_render_composition as fixtures

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
RENDER = SCRIPTS / "render_review.py"
HEAD, MERGE_BASE = fixtures.HEAD, fixtures.MERGE_BASE
TREE = "e" * 40
DELETED = "src/legacy-queue.ts"
MANIFEST = [{"path": "src/payments.ts", "status": "M"}, {"path": "src/retry-policy.ts", "status": "M"},
            {"path": "src/queue.ts", "status": "M"}, {"path": "docs/notes.md", "status": "M"}]
OUTPUTS = ("record.json", "payload.json", "batch.json")

# A subprocess that runs the finalizer with one injected fault: `write` fails staging the report, `promote` fails
# promoting it, `interrupt` raises KeyboardInterrupt there, and `kill` exits without cleanup there.
INJECT = r"""
import os, pathlib, sys
sys.path.insert(0, sys.argv[1])
import render_review
fault, sys.argv = sys.argv[2], ["render_review.py", *sys.argv[3:]]
real_replace, real_write = os.replace, pathlib.Path.write_bytes
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
os.replace, pathlib.Path.write_bytes = replace, write_bytes
sys.exit(render_review.main())
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


def bundle(private, tasks, name="initial", phase="initial"):
    """A verifier bundle manifest and the accounting report reconciled against it, as the helpers write them."""
    directory = Path(private) / name
    directory.mkdir()
    manifest = json.dumps({"format": "verifier-manifest/3", "bundle_id": f"bundle-{name}", "batch": {"id": name, "phase": phase},
                           "candidate_ids": [t["id"] for t in tasks], "premise_ids": []}, indent=2).encode("utf-8")
    (directory / "manifest.json").write_bytes(manifest)
    (directory / "raw-return.json").write_text("{}\n", encoding="utf-8")
    accounting = directory / "accounting.json"
    fixtures.write_accounting(str(accounting), tasks)
    report = json.loads(accounting.read_text(encoding="utf-8"))
    report.update(bundle_id=f"bundle-{name}", manifest_sha256=hashlib.sha256(manifest).hexdigest(),
                  raw_return=str(directory / "raw-return.json"))
    accounting.write_text(json.dumps(report), encoding="utf-8")
    return {"bundle": str(directory), "accounting": str(accounting), "operation": "Agent run_in_background=false"}


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

    def composition(self, private, store, kind="pull-request"):
        value = fixtures.gate_composition()
        if kind == "pull-request":
            value["run"] = fixtures.base_composition()["run"]
        elif kind == "worktree":
            value["run"].update(target_kind="worktree", tree=TREE)
            value["run"].pop("target")
        value["record"]["paths"] = {"private_dir": str(private), "store": str(store), "composition": str(private / "composition.json"),
                                    "skill_root": str(SKILL)}
        return value

    def write(self, private, composition):
        (private / "composition.json").write_text(json.dumps(composition), encoding="utf-8")

    def finalize(self, private, store, *extra):
        return run([RENDER, "--store", store, *extra, private])

    def check(self, private, *extra):
        return run([RENDER, "--check", *extra, private])

    def consumables(self, private):
        return sorted(name for name in (*OUTPUTS, "report.md") if (private / name).exists())

    def succeeded(self, private, store, *extra, composition=None):
        """Finalize, then assert the record, payload, batch and report agree and --check reads the same lines."""
        result = self.finalize(private, store, *extra)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = (private / "report.md").read_text(encoding="utf-8")
        record = json.loads((private / "record.json").read_text(encoding="utf-8"))
        payload = json.loads((private / "payload.json").read_text(encoding="utf-8"))
        batch = json.loads((private / "batch.json").read_text(encoding="utf-8"))
        self.assertEqual(rr.validate(payload), [])
        self.assertEqual(batch, rr.emit_batch(payload))
        self.assertEqual((record["summary"], record["items"]), (payload["summary"], payload["items"]))
        self.assertEqual((record["schema"], record["workflow"]), (rr.RECORD_SCHEMA, rr.WORKFLOW))
        finalization = record["finalization"]
        self.assertEqual((finalization["protocol"], finalization["report"]), (rr.FINALIZATION_PROTOCOL, str(private / "report.md")))
        self.assertEqual(json.loads((private / "composition.json").read_text(encoding="utf-8")), composition,
                         "the reviewer's composition is never rewritten")
        self.assert_complete(report, payload, record, finalization["replies"])
        self.assertEqual(sorted(p.name for p in private.glob("*.part")), [])
        checked = self.check(private)
        self.assertEqual((checked.returncode, checked.stdout), (0, result.stdout))
        self.assertEqual(result.stdout.splitlines()[0], f"status {record['status']}")
        self.assertTrue(result.stdout.endswith(f"report {private / 'report.md'}\n"), result.stdout)
        return report, record

    def assert_complete(self, report, payload, record, replies):
        body = payload["summary"]["body"]
        self.assertEqual(report.count(body.rstrip("\n")), 1, "the summary body appears once")
        for item in payload["items"]:
            self.assertEqual(report.count(item["markdown"]), 1, item.get("id", item["markdown"]))
            if item["type"] != "observation":
                self.assertEqual(report.count(item["trailer"]), 1, item["id"])
                if item["anchor"]["type"] == "line":
                    self.assertIn(f"### `{item['id']}`\n\n{item['markdown']}\n\n{item['trailer']}", report)
        accounting = record["record"]
        self.assertIn(f"- Repository: `{accounting['repository']}`", report.split("## Run", 1)[1])
        for row in accounting["requirements"]:
            self.assertIn(f"- `{row['source']}` ({row['class']}): {row['disposition']}. {row['evidence']}", report)
        for row in accounting["files"]:
            self.assertIn(f"- `{row['path']}`: {row['state']}", report)
        for row in accounting["check_evidence"]:
            self.assertIn(f"- `{row['check']}` at `{row['head']}`: {row['outcome']}", report)
        verification = accounting["verification"]
        for task in verification["tasks"]:
            self.assertIn(f"`{task['id']}`", report.split("## Verification", 1)[1])
        for batch in verification["batches"]:
            self.assertIn(f"accounting `{batch['accounting']}`", report)
        for entry in verification["outstanding"]:
            self.assertIn(f"- Outstanding: {entry}", report)
        for entry in accounting["routed"]["unrecoverable_inputs"]:
            self.assertIn(f"- Unrecoverable input: {entry}", report)
        for key in ("unresolved", "disputed"):
            for identity in accounting["routed"][key]:
                self.assertIn(f"`{identity}`", report.split("## Routed", 1)[1])
        for reply in replies:
            if reply["body"] is not None:
                self.assertEqual(report.count(reply["body"]), 1, reply["id"])
        for key, value in accounting["paths"].items():
            self.assertIn(f"`{value}`", report.split("## Artifacts", 1)[1], key)

    # --- targets and report contents --------------------------------------------

    def test_every_target_writes_the_one_record_shape(self):
        for kind in ("pull-request", "range", "worktree"):
            with self.subTest(kind=kind):
                private = self.directory(kind)
                store = self.store(private, snapshot=kind == "worktree")
                composition = self.composition(private, store, kind)
                self.write(private, composition)
                _report, record = self.succeeded(private, store, composition=composition)
                self.assertEqual((record["lineage"], record["prior_record"]), ([], None))
                self.assertEqual(record["run"]["target_kind"], kind)
                self.assertEqual(record["run"]["packet_context"], fixtures.CONTEXT if kind == "pull-request" else "none")
                self.assertEqual(record["run"]["supplied_inputs"], "no" if kind == "pull-request" else "yes")
                self.assertNotIn("profile", record)
                self.assertFalse((private / "fragments.md").exists() or (private / "addenda").exists())

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
        composition["run"].pop("packet_context")  # the packet's
        self.write(private, composition)
        report, record = self.succeeded(private, store, "--packet", private / "packet.json", composition=composition)
        self.assertEqual(record["run"]["packet_context"], forge_packet.packet_context(threads))
        trailer = "<!-- prior-item id={} classification={} head=" + HEAD + " -->"
        self.assertEqual([(r["id"], r["thread_id"], r["comment_id"], r["body"]) for r in record["finalization"]["replies"]], [
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
        public = "".join((private / name).read_text(encoding="utf-8") for name in ("payload.json", "batch.json"))
        for field in ("Fixed: the key is reused.", "PRRT_fixed", "prior-item id="):
            self.assertNotIn(field, public, "reply fields stay private")

    def test_missing_accounting_is_refused(self):
        removals = [("record",)] + [("record", key) for key in
                                    ("repository", "requirements", "files", "check_evidence", "verification", "routed")]
        removals += [("record", "verification", key) for key in ("tasks", "batches", "outstanding")]
        removals += [("record", "routed", key) for key in ("unresolved", "disputed", "unrecoverable_inputs")]
        for path in removals:
            with self.subTest(missing=".".join(path)):
                private = self.directory("accounting")
                store = self.store(private)
                composition = self.composition(private, store)
                target = composition
                for key in path[:-1]:
                    target = target[key]
                del target[path[-1]]
                self.write(private, composition)
                (private / "report.md").write_text("stale success\n", encoding="utf-8")
                result = self.finalize(private, store)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("accounting failed with exit 1; later stages did not run:", result.stdout)
                self.assertIn(": accounting: ", result.stdout)
                self.assertEqual(self.consumables(private), [])

    def test_accounting_contradictions_are_refused(self):
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
                private = self.directory("contradiction")
                store = self.store(private)
                composition = self.composition(private, store)
                change(composition["record"])
                self.write(private, composition)
                result = self.finalize(private, store)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn("compose failed with exit 1", result.stdout)
                self.assertIn(f": {rule}: ", result.stdout)
                self.assertEqual(self.consumables(private), [])
        private = self.directory("allowance")
        store = self.store(private)
        composition = self.composition(private, store)
        composition["record"]["verification"]["allowance"]["initial_spent"] = False
        self.write(private, composition)
        result = self.finalize(private, store)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("derive failed with exit 1", result.stdout)
        self.assertIn("`allowance={\"initial_spent\": false, \"follow_up_spent\": false}` conflicts", result.stdout)

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
                if name != "no packet":
                    composition["run"].pop("packet_context")
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
        outputs = []
        for encoding in ("utf-8", "latin-1"):
            private = self.directory("stdio")
            store = self.store(private)
            composition = self.composition(private, store)
            self.assertIn("—", composition["summary"]["issue_fit"], "the fixture carries non-ASCII prose")
            self.write(private, composition)
            result = run([RENDER, "--store", store, private], env=dict(os.environ, PYTHONIOENCODING=encoding))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            outputs.append({name: (private / name).read_bytes().replace(str(private).encode("utf-8"), b"<private>")
                            for name in (*OUTPUTS, "report.md")})
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
        missing = run([RENDER, private])
        self.assertEqual(missing.returncode, 2, missing.stderr)
        self.assertIn("--store is required", missing.stderr)
        stray = run([RENDER, "--store", store, "--head", HEAD, private])
        self.assertEqual(stray.returncode, 2, stray.stderr)
        self.assertEqual(self.consumables(private), [])

    # --- staging, failures, retries ------------------------------------------

    def clean_run(self):
        private = self.directory("clean-run")
        store = self.store(private)
        composition = self.composition(private, store)
        self.write(private, composition)
        self.succeeded(private, store, composition=composition)
        outputs = {name: (private / name).read_bytes() for name in (*OUTPUTS, "report.md", "composition.json")}
        return private, store, composition, outputs

    def assert_restored(self, private, store, composition, outputs):
        self.write(private, composition)
        retry = self.finalize(private, store)
        self.assertEqual(retry.returncode, 0, retry.stdout + retry.stderr)
        self.assertEqual({name: (private / name).read_bytes() for name in outputs}, outputs, "a retry restores the clean run")

    def test_compose_refusal_leaves_nothing_consumable_and_a_retry_restores(self):
        private, store, composition, outputs = self.clean_run()
        broken = copy.deepcopy(composition)
        broken["summary"]["status"] = "Approved"
        self.write(private, broken)
        result = self.finalize(private, store)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("compose failed with exit 1; later stages did not run:", result.stdout)
        self.assertEqual(self.consumables(private), [])
        self.assertNotEqual(self.check(private).returncode, 0)
        self.assert_restored(private, store, composition, outputs)

    def test_write_promotion_and_interruption_failures(self):
        private, store, composition, outputs = self.clean_run()
        # An uncaught KeyboardInterrupt ends Python by SIGINT once its cleanup ran.
        for fault, status in (("write", 2), ("promote", 2), ("interrupt", -2), ("kill", 137)):
            with self.subTest(fault=fault):
                result = run(["-c", INJECT, SCRIPTS, fault, "--store", store, private])
                self.assertEqual(result.returncode, status, result.stdout + result.stderr)
                self.assertFalse((private / "report.md").exists(), "no report without a complete run")
                if fault != "kill":
                    self.assertEqual(self.consumables(private), [], "cleanup removes what this run promoted")
                    self.assertEqual(sorted(p.name for p in private.glob("*.part")), [])
                if fault in ("write", "promote"):
                    self.assertIn("cannot write output", result.stderr)
                checked = self.check(private)
                self.assertEqual(checked.returncode, 1, checked.stdout)
                self.assertIn("unconsumable:", checked.stdout)
                self.assert_restored(private, store, composition, outputs)
        # A hard kill between promotions leaves earlier outputs without the report; they never read as success.
        run(["-c", INJECT, SCRIPTS, "kill", "--store", store, private])
        self.assertTrue(self.consumables(private))
        self.assertIn("does not exist, so its finalization did not complete", self.check(private).stdout)

    def test_stale_outputs_are_removed_first(self):
        private = self.directory("stale")
        store = self.store(private)
        composition = self.composition(private, store)
        self.write(private, composition)
        for name in (*OUTPUTS, "report.md", "payload.json.part", "fragments.md"):
            (private / name).write_text("stale success\n", encoding="utf-8")
        self.succeeded(private, store, composition=composition)
        self.assertFalse((private / "fragments.md").exists(), "a retired profile's output never reads as this run's")
        blocked = self.directory("blocked")
        (blocked / "report.md").mkdir()
        self.write(blocked, self.composition(blocked, store))
        result = self.finalize(blocked, store)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("cannot remove stale output", result.stderr)

    # --- consumers ----------------------------------------------------------------

    def test_check_refuses_unknown_incomplete_and_retired_records(self):
        private, _store, _composition, _outputs = self.clean_run()
        record = json.loads((private / "record.json").read_text(encoding="utf-8"))
        cases = (
            ("retired gate record", dict(record, schema="implementation-gate-record/2"), "not `review-code-record/1`"),
            ("unknown protocol", dict(record, finalization={"protocol": "review-code-finalization/1", "report": str(private / "report.md")}),
             "not `review-code-finalization/2`"),
            ("no finalization", {k: v for k, v in record.items() if k != "finalization"}, "carries no finalization marker"),
            ("missing report", dict(record, finalization=dict(record["finalization"], report=str(private / "absent.md"))), "does not exist"),
            ("another directory's report", dict(record, finalization=dict(record["finalization"], report=str(self.root / "report.md"))),
             None),
        )
        (self.root / "report.md").write_text("elsewhere\n", encoding="utf-8")
        for name, doc, needle in cases:
            with self.subTest(name):
                (private / "record.json").write_text(json.dumps(doc), encoding="utf-8")
                result = self.check(private)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(needle or "not this directory's", result.stdout)
        (private / "record.json").write_text(json.dumps(record), encoding="utf-8")
        (private / "batch.json").unlink()
        self.assertIn("batch.json is missing", self.check(private).stdout)
        self.assertEqual(self.check(self.directory("empty")).returncode, 1)


# --- mechanical fields derived from the store and packet ----------------------------------------------------------

MESSAGE = "Keep the key\n\nReuse one idempotency key per logical charge.\n\n"


class Derive(unittest.TestCase):
    """Omitted mechanical fields come from the store, packet, specs and bundles; explicit copies are checked."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.count = 0
        self.stores: dict[str, Path] = {}
        for directory in ("src", "docs"):
            (self.repo / directory).mkdir(parents=True)
        self.git("init", "-q")
        self.write_files({"AGENTS.md": "Root rules.\n", "docs/notes.md": "notes\n"})
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

    def store(self, kind):
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

    def authored(self, private, kind):
        """What the reviewer writes: judgments, prose, and only the mechanical fields no saved input owns."""
        value = fixtures.gate_composition()
        value["run"] = {"coverage": "complete", "specs": []}
        if kind != "pull-request":
            value["run"].update(base_ref="main", base_sha=self.base, issues=["acme/payments#123"], change_description=MESSAGE,
                                specs=["spec/retries"])
        if kind == "range":
            value["run"].update(target_kind="range", target="main...HEAD")
        record = value["record"]
        record["repository"] = str(self.repo)
        del record["paths"]
        head = self.context(kind)["head"]
        for row in record["check_evidence"]:
            if row["head"] == fixtures.HEAD:
                row["head"] = head
        task = fixtures.candidate_task()
        record["verification"] = {"tasks": [task], "batches": [bundle(private, [task])], "outstanding": []}
        return value

    def explicit(self, private, kind, packet_path=None):
        """The same review with every mechanical field transcribed."""
        value = self.authored(private, kind)
        context = self.context(kind)
        value["run"].update(head=context["head"], merge_base=context["merge_base"], base_ref="main", base_sha=self.base,
                            issues=["acme/payments#123"], merged=False, target_kind=kind,
                            supplied_inputs="yes" if value["run"]["specs"] else "no")
        if kind == "pull-request":
            value["run"]["repository_url"] = fixtures.REPO
            value["run"]["packet_context"] = forge_packet.packet_context(json.loads(Path(packet_path).read_text(encoding="utf-8")))
        if kind == "worktree":
            value["run"]["tree"] = context["snapshot"]["tree"]
        value["record"]["paths"] = {"private_dir": str(private), "store": str(self.store(kind)),
                                    "composition": str(private / "composition.json"), "skill_root": str(SKILL)}
        value["record"]["lineage"] = []
        verification = value["record"]["verification"]
        verification["allowance"] = {"initial_spent": True, "follow_up_spent": False}
        for batch in verification["batches"]:
            batch.update(name="initial", phase="initial", raw_return=str(Path(batch["bundle"]) / "raw-return.json"))
        return value

    def forge_packet(self, private, **pr):
        value = packet({})
        value["pr"].update({"base_sha": self.base, "head_sha": self.head, **pr})
        path = private / "packet.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def args(self, private, kind):
        return ["--packet", self.forge_packet(private)] if kind == "pull-request" else []

    def finalize(self, private, kind, *extra, composition=None):
        if composition is not None:
            (private / "composition.json").write_text(json.dumps(composition), encoding="utf-8")
        return run([RENDER, "--store", self.store(kind), *extra, private], cwd=self.repo)

    def refused(self, result, stage, needle, private):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(f"{stage} failed with exit 1; later stages did not run:", result.stdout)
        self.assertIn(needle, result.stdout)
        self.assertEqual(sorted(n for n in (*OUTPUTS, "report.md") if (private / n).exists()), [])

    def test_targets_derive_identity_paths_batches_and_packet_identity(self):
        for kind in ("pull-request", "range", "worktree"):
            with self.subTest(kind=kind):
                private = self.directory()
                extra = self.args(private, kind)
                result = self.finalize(private, kind, *extra, composition=self.authored(private, kind))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                record = json.loads((private / "record.json").read_text(encoding="utf-8"))
                derived_run, paths = record["run"], record["record"]["paths"]
                batch = record["record"]["verification"]["batches"][0]
                context = self.context(kind)
                self.assertEqual((derived_run["head"], derived_run["merge_base"], derived_run["base_sha"]),
                                 (context["head"], context["merge_base"], self.base))
                if kind == "pull-request":
                    self.assertEqual((derived_run["target_kind"], derived_run["repository_url"], derived_run["merged"],
                                      derived_run["issues"], derived_run["supplied_inputs"]),
                                     ("pull-request", fixtures.REPO, False, ["acme/payments#123"], "no"))
                    digest = forge_packet.packet_context(json.loads(Path(extra[1]).read_text(encoding="utf-8")))
                    self.assertEqual(derived_run["packet_context"], digest)
                    self.assertIn(f"packet_context={digest} supplied_inputs=no ", record["summary"]["trailer"])
                else:
                    self.assertEqual((derived_run["packet_context"], derived_run["supplied_inputs"], derived_run["specs"]),
                                     ("none", "yes", ["spec/retries"]))
                if kind == "worktree":
                    self.assertEqual((derived_run["target_kind"], derived_run["tree"]), ("worktree", context["snapshot"]["tree"]))
                self.assertEqual(paths, {"private_dir": str(private), "store": str(self.store(kind)),
                                         "composition": str(private / "composition.json"), "skill_root": str(SKILL)})
                self.assertEqual((batch["name"], batch["phase"], batch["raw_return"]),
                                 ("initial", "initial", str(private / "initial" / "raw-return.json")))
                self.assertEqual(record["record"]["verification"]["allowance"], {"initial_spent": True, "follow_up_spent": False})
                self.assertEqual(record["finalization"]["inputs"], {"store": str(self.store(kind)), "prior_record": None,
                                                                    "packet": str(extra[1]) if kind == "pull-request" else None})

                # Parity: the transcribed composition of the same review renders the same bytes.
                twin = self.directory()
                twin_extra = self.args(twin, kind)
                same = self.finalize(twin, kind, *twin_extra,
                                     composition=self.explicit(twin, kind, twin_extra[1] if twin_extra else None))
                self.assertEqual(same.returncode, 0, same.stdout + same.stderr)
                for name in ("payload.json", "batch.json"):
                    self.assertEqual((private / name).read_text(encoding="utf-8"), (twin / name).read_text(encoding="utf-8"), name)

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
            ("pull-request", {"run": {"packet_context": "0" * 64}}, {}, f"`packet_context=\"{'0' * 64}\"` conflicts"),
            ("pull-request", {"run": {"supplied_inputs": "yes"}}, {}, "`supplied_inputs=\"yes\"` conflicts with \"no\" from `run.specs`"),
            ("pull-request", {}, {"head_sha": other}, f"the packet pins head `{other}`"),
            ("range", {"run": {"merged": True}}, {}, "`merged=true` conflicts with false from a local target"),
            ("range", {"record": {"paths": {"skill_root": "/elsewhere/review-code"}}}, {}, "`skill_root=\"/elsewhere/review-code\"` conflicts"),
            ("range", {"record": {"paths": {"private_dir": "/tmp/another"}}}, {}, "`private_dir=\"/tmp/another\"` conflicts"),
            ("range", {"record": {"paths": {"store": "/tmp/another.json"}}}, {}, "`store=\"/tmp/another.json\"` conflicts"),
            ("range", {"record": {"lineage": ["/tmp/elsewhere/record.json"]}}, {}, "`lineage=[\"/tmp/elsewhere/record.json\"]` conflicts"),
            ("range", {"batch": {"name": "follow-up"}}, {}, "`name=\"follow-up\"` conflicts"),
            ("range", {"batch": {"phase": "follow-up"}}, {}, "`phase=\"follow-up\"` conflicts"),
            ("range", {"batch": {"raw_return": "/tmp/repaired.json"}}, {}, "`raw_return=\"/tmp/repaired.json\"` conflicts"),
            ("range", {"allowance": {"initial_spent": True, "follow_up_spent": True}}, {}, "`allowance="),
            ("worktree", {"run": {"tree": other}}, {}, f"`tree=\"{other}\"` conflicts"),
            ("worktree", {"run": {"target_kind": "range"}}, {}, "`target_kind=\"range\"` conflicts"),
        ]
        for kind, change, pr, needle in cases:
            with self.subTest(needle):
                private = self.directory()
                composition = self.authored(private, kind)
                composition["run"].update(change.get("run", {}))
                record = change.get("record", {})
                if "paths" in record:
                    composition["record"]["paths"] = dict(record["paths"])
                if "lineage" in record:
                    composition["record"]["lineage"] = record["lineage"]
                if "allowance" in change:
                    composition["record"]["verification"]["allowance"] = change["allowance"]
                composition["record"]["verification"]["batches"][0].update(change.get("batch", {}))
                extra = self.args(private, kind)
                if pr:
                    self.forge_packet(private, **pr)
                result = self.finalize(private, kind, *extra, composition=composition)
                self.refused(result, "derive", needle, private)

        # Explicit copies that agree are accepted, and so is a raw path spelled through a symlinked directory.
        private = self.directory()
        (self.root / "alias").symlink_to(private)
        composition = self.authored(private, "range")
        composition["run"].update(merged=False, supplied_inputs="yes")
        composition["record"]["paths"] = {"private_dir": str(self.root / "alias")}
        result = self.finalize(private, "range", composition=composition)
        self.assertEqual(result.returncode, 0, result.stdout)

        # A bundle and an accounting report for different manifests do not pair: another bundle ID, or an edited
        # manifest under the same ID.
        for change in ({"bundle_id": "bundle-rebuilt"}, {"candidate_ids": []}):
            private = self.directory()
            composition = self.authored(private, "range")
            manifest = private / "initial" / "manifest.json"
            manifest.write_text(json.dumps({**json.loads(manifest.read_text(encoding="utf-8")), **change}), encoding="utf-8")
            result = self.finalize(private, "range", composition=composition)
            self.refused(result, "derive", "accounts a return to another manifest", private)

        # A batch built or accounted by the retired helpers is refused rather than read.
        for name, change in (("manifest.json", {"format": "verifier-manifest/2"}),
                             ("accounting.json", {"format": "verifier-accounting/2"})):
            private = self.directory()
            composition = self.authored(private, "range")
            path = private / "initial" / name
            path.write_text(json.dumps({**json.loads(path.read_text(encoding="utf-8")), **change}), encoding="utf-8")
            result = self.finalize(private, "range", composition=composition)
            self.refused(result, "derive", "rebuild and reaccount the batch", private)

    def test_packet_context_follows_the_saved_packet(self):
        """An edited packet changes the digest the finalizer derives; a copy computed before the edit is refused."""
        private = self.directory()
        path = self.forge_packet(private)
        early = forge_packet.packet_context(json.loads(path.read_text(encoding="utf-8")))
        edited = json.loads(path.read_text(encoding="utf-8"))
        edited["fingerprint"]["issues"][0]["comments"] = [{"id": "7", "author": "octocat", "created_at": "2026-09-01T12:00:00Z",
                                                           "updated_at": "2026-09-01T12:00:00Z", "body": "Added later."}]
        path.write_text(json.dumps(edited), encoding="utf-8")
        composition = self.authored(private, "pull-request")
        composition["run"]["packet_context"] = early
        result = self.finalize(private, "pull-request", "--packet", path, composition=composition)
        self.refused(result, "derive", f"`packet_context=\"{early}\"` conflicts", private)
        del composition["run"]["packet_context"]
        result = self.finalize(private, "pull-request", "--packet", path, composition=composition)
        self.assertEqual(result.returncode, 0, result.stdout)
        record = json.loads((private / "record.json").read_text(encoding="utf-8"))
        self.assertEqual(record["run"]["packet_context"], forge_packet.packet_context(edited))
        self.assertNotEqual(record["run"]["packet_context"], early)

    def test_missing_authoritative_fields_and_inputs(self):
        cases = [
            ("merged unknown", "pull-request", {"merged": None}, "`merged` is omitted and the packet does not establish it"),
            ("no base", "pull-request", {"base_sha": ""}, "`base_sha` is omitted and the packet does not establish it"),
            ("no packet", "pull-request", "no-packet", "`packet_context` must be the 64-character"),
            ("no snapshot", "range", "worktree-without-snapshot", "`tree` is omitted and"),
        ]
        for name, kind, change, needle in cases:
            with self.subTest(name):
                private = self.directory()
                composition = self.authored(private, kind)
                extra = self.args(private, kind)
                stage = "derive"
                if change == "no-packet":
                    extra, stage = [], "compose"
                elif change == "worktree-without-snapshot":
                    composition["run"]["target_kind"] = "worktree"
                    composition["run"].pop("target")
                elif isinstance(change, dict):
                    self.forge_packet(private, **change)
                result = self.finalize(private, kind, *extra, composition=composition)
                self.refused(result, stage, needle, private)

    def test_example_finalizes(self):
        """--example, with only its placeholders pointed at this run, finalizes as written."""
        private = self.directory()
        shown = run([RENDER, "--example"])
        text = shown.stdout.replace("/tmp/review-code-XXXXXX", str(private))
        text = text.replace(fixtures.HEAD, self.head).replace(fixtures.BASE, self.base)
        example = json.loads(text)
        bundle(private, example["record"]["verification"]["tasks"])
        path = self.forge_packet(private)
        value = json.loads(path.read_text(encoding="utf-8"))
        path.write_text(json.dumps(dict(value, threads=packet({"PRRT_kwDOABCD12": [1001]})["threads"])), encoding="utf-8")
        result = self.finalize(private, "pull-request", "--packet", path, composition=example)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((private / "report.md").is_file())

    def test_omitted_judgments_are_never_approval(self):
        cases = [
            ("coverage", lambda c: c["run"].pop("coverage"), "compose", "run.coverage: trailer-grammar"),
            ("status", lambda c: c["summary"].pop("status"), "compose", "summary.status: status-consistency"),
            ("files", lambda c: c["record"].pop("files"), "accounting", "`files` is required"),
            ("file state", lambda c: c["record"]["files"][0].pop("state"), "compose", "record.files[0]: schema: `state` is required"),
            ("ruling", lambda c: c["record"]["verification"]["tasks"][0].pop("ruling"), "compose", "`ruling` is required"),
            ("dispositions", lambda c: c["record"]["requirements"][0].pop("disposition"), "compose", "`disposition` is required"),
            ("outstanding", lambda c: c["record"]["verification"].pop("outstanding"), "accounting", "`outstanding` is required"),
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
                self.assertEqual(sorted(n for n in (*OUTPUTS, "report.md") if (private / n).exists()), [])


# --- prior records ---------------------------------------------------------------------------------------------------

FINDING_ID = "ledger/frozen-transfer"
CONSIDER_ID = "ledger/post-docstring"


class PriorRecord(unittest.TestCase):
    """A local re-review after fixes continues a finalized record one hop back, and the caller checks the lineage."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        (self.repo / "src").mkdir(parents=True)
        self.git("init", "-q")
        self.write_ledger(0)
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD")
        self.git("checkout", "-qb", "freeze")
        self.heads = []
        for step in (1, 2, 3, 4):
            self.write_ledger(step)
            self.git("commit", "-qam", f"Freeze accounts, step {step}")
            self.heads.append(self.git("rev-parse", "HEAD"))
        self.count = 0

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", *args], cwd=self.repo,
                              capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    def write_ledger(self, step):
        lines = [f"line {i}" for i in range(1, 21)]
        for i in range(step):
            lines[i] = f"step {i + 1}"
        (self.repo / "src" / "ledger.py").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def store(self, head_index):
        path = self.root / f"store-{head_index}.json"
        if not path.exists():
            built = run([SCRIPTS / "review_context.py", "--merge-base", self.base, "--head", self.heads[head_index], "--store", path],
                        cwd=self.repo)
            self.assertEqual(built.returncode, 0, built.stderr)
        return path

    def directory(self):
        self.count += 1
        private = self.root / f"private-{self.count}"
        private.mkdir()
        return private

    def must_fix(self, **overrides):
        value = {"id": FINDING_ID, "title": "Refuse transfers into frozen accounts", "priority": "P1", "action": "must-fix",
                 "kind": "requirement", "trigger": "A transfer targets a frozen account.",
                 "impact": "Money reaches an account the specification freezes.",
                 "change": "Check the destination's `frozen` flag in `transfer`.",
                 "anchor": {"type": "line", "path": "src/ledger.py", "start_line": 1, "end_line": 1, "side": "RIGHT"}}
        value.update(overrides)
        return value

    def consider(self):
        return {"id": CONSIDER_ID, "title": "Document the frozen error", "priority": "P3", "action": "consider",
                "kind": "maintainability", "trigger": "A caller reads `post`'s docstring.",
                "impact": "The new error is undocumented.", "change": "Name the frozen error in the docstring.",
                "anchor": {"type": "line", "path": "src/ledger.py", "start_line": 2, "end_line": 2, "side": "RIGHT"}}

    def composition(self, status="Changes Requested", findings=None, tasks=None, batches=None, prior_items=None,
                    outstanding=None, routed=None, coverage="complete", gaps=None):
        summary = {"status": status, "intent": "Freeze accounts.", "issue_fit": "The spec's freeze rule, checked row by row.",
                   "coverage": "Complete merge-base diff reviewed."}
        if gaps:
            summary["coverage_gaps"] = gaps
        return {
            "run": {"target_kind": "range", "target": "main...HEAD", "base_ref": "main", "base_sha": self.base, "issues": [],
                    "specs": ["spec/freeze"], "change_description": "Freeze accounts", "coverage": coverage},
            "summary": summary,
            "findings": findings if findings is not None else [], "questions": [], "observations": [],
            "prior_items": prior_items or [],
            "record": {"repository": str(self.repo), "requirements": [], "files": [{"path": "src/ledger.py", "state": "reviewed"}],
                       "check_evidence": [],
                       "verification": {"tasks": tasks or [], "batches": batches or [], "outstanding": outstanding or []},
                       "routed": routed or {"unresolved": [], "disputed": [], "unrecoverable_inputs": []}},
        }

    def finalize(self, private, head_index, composition, prior=None, extra=()):
        (private / "composition.json").write_text(json.dumps(composition), encoding="utf-8")
        args = [RENDER, "--store", self.store(head_index), *extra]
        if prior is not None:
            args += ["--prior-record", prior]
        return run([*args, private], cwd=self.repo)

    def accepted(self, private, head_index, composition, prior=None):
        result = self.finalize(private, head_index, composition, prior)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return private / "record.json"

    def refused(self, result, needle, stage="compose"):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(f"{stage} failed with exit 1", result.stdout)
        self.assertIn(needle, result.stdout)

    def first(self, findings=None, follow_up=False):
        """R1 at the first head: a confirmed must-fix and a consider, with the initial batch (and the follow-up) spent."""
        private = self.directory()
        task = fixtures.candidate_task(FINDING_ID)
        batches = [bundle(private, [task])]
        if follow_up:
            batches.append(bundle(private, [], "follow-up", "follow-up"))
        composition = self.composition(findings=findings or [self.must_fix(), self.consider()], tasks=[task], batches=batches)
        return self.accepted(private, 0, composition)

    def carried(self, source, trigger="must-fix", batch="initial"):
        return {"id": FINDING_ID, "type": "candidate", "trigger": trigger, "batch": batch, "ruling": "confirmed",
                "confirmed_in": str(source)}

    def open_items(self, finding="still-open", consider="fixed"):
        return [{"id": FINDING_ID, "classification": finding, "action": "must-fix", "note": "Only the source is checked."},
                {"id": CONSIDER_ID, "classification": consider, "action": "consider", "note": "Documented."}]

    # --- success paths ----------------------------------------------------------------

    def test_two_hop_lineage_carries_a_confirmation_and_the_allowance(self):
        r1 = self.first()
        # R2 keeps the blocker open, carries its confirmation from R1 and spends the follow-up on a new premise.
        private = self.directory()
        premise = fixtures.premise_task(batch="follow-up")
        follow = bundle(private, [premise], "follow-up", "follow-up")
        r2 = self.accepted(private, 1, self.composition(findings=[self.must_fix()], tasks=[self.carried(r1), premise], batches=[follow],
                                                        prior_items=self.open_items()), r1)
        record = json.loads(r2.read_text(encoding="utf-8"))
        self.assertEqual((record["lineage"], record["prior_record"]), ([str(r1)], str(r1)))
        self.assertEqual(record["record"]["verification"]["allowance"], {"initial_spent": True, "follow_up_spent": True})
        report = (r2.parent / "report.md").read_text(encoding="utf-8")
        self.assertIn(f"batch `initial` of `{r1}`: confirmed.", report)
        self.assertIn(f"counting what the prior record `{r1}` spent.", report)
        # R3 carries the same provenance through R2, not R2 itself, and has nothing left to spend.
        private = self.directory()
        r3 = self.accepted(private, 2, self.composition(findings=[self.must_fix()], tasks=[self.carried(r1)],
                                                        prior_items=self.open_items()[:1]), r2)
        record = json.loads(r3.read_text(encoding="utf-8"))
        self.assertEqual(record["lineage"], [str(r1), str(r2)])
        self.assertEqual(record["record"]["verification"]["allowance"], {"initial_spent": True, "follow_up_spent": True})
        checked = run([RENDER, "--check", "--head", self.heads[2], "--lineage", r1, "--lineage", r2, "--lineage", r3, r3.parent])
        self.assertEqual(checked.returncode, 0, checked.stdout)
        # Through R2 the provenance is still R1's batch: naming R2, or a batch R1 never confirmed it in, is refused.
        for source, batch, needle in ((r2, "initial", "carry that provenance unchanged"),
                                      (r1, "follow-up", "carry that provenance unchanged"),
                                      (self.root / "elsewhere.json", "initial", "neither the prior record nor in its lineage")):
            with self.subTest(source=str(source), batch=batch):
                result = self.finalize(self.directory(), 2, self.composition(findings=[self.must_fix()],
                                                                             tasks=[self.carried(source, batch=batch)],
                                                                             prior_items=self.open_items()[:1]), r2)
                self.refused(result, needle)
        result = self.finalize(self.directory(), 2, self.composition(findings=[self.must_fix()],
                                                                     tasks=[self.carried(r1, trigger="security")],
                                                                     prior_items=self.open_items()[:1]), r2)
        self.refused(result, "confirmed it under `must-fix`")

    def test_fixed_must_fix_completes_with_both_batches_spent(self):
        r1 = self.first(follow_up=True)
        private = self.directory()
        r2 = self.accepted(private, 1, self.composition(status="Approved", prior_items=self.open_items("fixed")), r1)
        record = json.loads(r2.read_text(encoding="utf-8"))
        self.assertEqual((record["status"], record["run"]["coverage"]), ("Approved", "complete"))
        self.assertEqual(record["record"]["verification"]["allowance"], {"initial_spent": True, "follow_up_spent": True})
        self.assertEqual([p["classification"] for p in record["prior_items"]], ["fixed", "fixed"])
        # A new must-fix after both batches are spent cannot be confirmed: it stays outstanding and the run incomplete.
        new = self.must_fix(id="ledger/negative-balance", title="Refuse negative balances",
                            anchor={"type": "line", "path": "src/ledger.py", "start_line": 2, "end_line": 2, "side": "RIGHT"})
        pending = fixtures.candidate_task("ledger/negative-balance", batch=None, ruling="pending")
        result = self.finalize(self.directory(), 1, self.composition(status="Changes Requested", findings=[new], tasks=[pending],
                                                                     prior_items=self.open_items("fixed")), r1)
        self.refused(result, "requires a candidate task with its id")
        spent = bundle(self.directory(), [fixtures.candidate_task("ledger/negative-balance", batch="follow-up")], "follow-up", "follow-up")
        result = self.finalize(self.directory(), 1, self.composition(
            status="Changes Requested", findings=[new], tasks=[fixtures.candidate_task("ledger/negative-balance", batch="follow-up")],
            batches=[spent], prior_items=self.open_items("fixed")), r1)
        self.refused(result, "the prior record already spent its follow-up batch")
        private = self.directory()
        self.accepted(private, 1, self.composition(
            status="Incomplete", tasks=[pending], prior_items=self.open_items("fixed"), coverage="incomplete",
            outstanding=["ledger/negative-balance: must-fix candidate arrived after the follow-up was spent"],
            gaps=["`ledger/negative-balance` needs confirmation the spent allowance cannot give"]), r1)

    def test_required_unresolved_verification_leaves_it_incomplete(self):
        private = self.directory()
        task = fixtures.candidate_task(FINDING_ID)
        pending = fixtures.premise_task(batch=None, ruling="pending")
        r1 = self.accepted(private, 0, self.composition(
            findings=[self.must_fix()], tasks=[task, pending], batches=[bundle(private, [task])], coverage="incomplete",
            outstanding=["premise-1: no awaited route"], gaps=["premise-1 unverified"]))
        # The fix settles the finding, but the outstanding premise survives: complete coverage is refused.
        result = self.finalize(self.directory(), 1, self.composition(status="Approved", prior_items=self.open_items("fixed")[:1]), r1)
        self.refused(result, "drops `premise-1: no awaited route`")
        self.accepted(self.directory(), 1, self.composition(
            status="Incomplete", prior_items=self.open_items("fixed")[:1], coverage="incomplete", outstanding=["premise-1: no awaited route"],
            gaps=["premise-1 unverified"]), r1)
        # A task here that settles it lets it go.
        private = self.directory()
        holds = fixtures.premise_task(batch="follow-up")
        self.accepted(private, 1, self.composition(status="Approved", tasks=[holds],
                                                   batches=[bundle(private, [holds], "follow-up", "follow-up")],
                                                   prior_items=self.open_items("fixed")[:1]), r1)

    def test_a_settled_routed_item_releases_its_entry(self):
        settled = self.open_items()[1:]
        for key in ("unresolved", "disputed"):
            routed = {"unresolved": [], "disputed": [], "unrecoverable_inputs": [], key: [CONSIDER_ID]}
            r1 = self.accepted(self.directory(), 0, self.composition(status="Approved", findings=[self.consider()], routed=routed))
            for name, kept in (("the settling run drops it", None), ("the settling run keeps it and the next drops it", routed)):
                with self.subTest(key=key, case=name):
                    r2 = self.accepted(self.directory(), 1, self.composition(status="Approved", prior_items=settled, routed=kept), r1)
                    r3 = self.accepted(self.directory(), 2, self.composition(status="Approved"), r2)
                    checked = run([RENDER, "--check", "--head", self.heads[2], "--lineage", r1, "--lineage", r2, "--lineage", r3, r3.parent])
                    self.assertEqual((checked.returncode, checked.stdout.splitlines()[:2]), (0, ["status Approved", "coverage complete"]))
        # An entry is its item's whole id: an open item whose id holds a `:` is not mistaken for a settled prefix,
        # and of the tasks this run ruled on only one named by that whole id releases it.
        colon = "ledger:post-docstring"
        routed = {"unresolved": [colon], "disputed": [], "unrecoverable_inputs": []}
        finding = dict(self.consider(), id=colon)
        r1 = self.accepted(self.directory(), 0, self.composition(status="Approved", findings=[finding], routed=routed))
        still_open = [{"id": colon, "classification": "still-open", "action": "consider", "note": "Still undocumented."}]
        result = self.finalize(self.directory(), 1, self.composition(status="Approved", findings=[finding], prior_items=still_open), r1)
        self.refused(result, f"drops `{colon}`")
        for task, releases in ((fixtures.premise_task("ledger"), False), (fixtures.candidate_task(colon), True)):
            with self.subTest(task=task["id"]):
                private = self.directory()
                result = self.finalize(private, 1, self.composition(status="Approved", findings=[finding], prior_items=still_open,
                                                                    tasks=[task], batches=[bundle(private, [task])]), r1)
                if releases:
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                else:
                    self.refused(result, f"drops `{colon}`")
        # An unrecoverable input names no item, so settling every item releases nothing.
        missing = dict(status="Incomplete", coverage="incomplete", gaps=["the benchmark artifact was not supplied"])
        r1 = self.accepted(self.directory(), 0, self.composition(
            findings=[self.consider()], routed={"unresolved": [], "disputed": [], "unrecoverable_inputs": ["the benchmark artifact"]}, **missing))
        result = self.finalize(self.directory(), 1, self.composition(status="Approved", prior_items=settled), r1)
        self.refused(result, "drops `the benchmark artifact`; an unrecoverable input survives until a task in this run settles it")

    def test_sibling_fork_is_rejected_by_the_callers_lineage_check(self):
        r1 = self.first()
        r2 = self.accepted(self.directory(), 1, self.composition(findings=[self.must_fix()], tasks=[self.carried(r1)],
                                                                  prior_items=self.open_items()), r1)
        # A sibling that continues R1 again passes the one-hop check and reuses R1's unspent follow-up ...
        private = self.directory()
        premise = fixtures.premise_task(batch="follow-up")
        sibling = self.accepted(private, 2, self.composition(
            findings=[self.must_fix()], tasks=[self.carried(r1), premise], batches=[bundle(private, [premise], "follow-up", "follow-up")],
            prior_items=self.open_items()), r1)
        # ... so the caller, whose latest accepted record is R2, requires R2 and everything it dispatched in the lineage.
        refused = run([RENDER, "--check", "--head", self.heads[2], "--lineage", r2, "--lineage", sibling, sibling.parent])
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn(f"does not descend from `{r2}`", refused.stdout)
        head = run([RENDER, "--check", "--head", self.heads[3], sibling.parent])
        self.assertEqual(head.returncode, 1, head.stdout)
        self.assertIn(f"reviews head `{self.heads[2]}`, not `{self.heads[3]}`", head.stdout)
        accepted = run([RENDER, "--check", "--head", self.heads[1], "--lineage", r1, "--lineage", r2, r2.parent])
        self.assertEqual(accepted.returncode, 0, accepted.stdout)

    # --- refusals -------------------------------------------------------------------------

    def test_prior_record_refusals(self):
        r1 = self.first()
        good = dict(findings=[self.must_fix()], tasks=[self.carried(r1)], prior_items=self.open_items())

        def attempt(prior=r1, head_index=1, extra=(), **change):
            value = self.composition(**{**good, **change})
            return self.finalize(self.directory(), head_index, value, prior, extra)

        record = json.loads(r1.read_text(encoding="utf-8"))
        broken = self.root / "broken"
        broken.mkdir()
        for name, doc, needle in (
            ("no finalization", {k: v for k, v in record.items() if k != "finalization"}, "carries no finalization marker"),
            ("missing report", dict(record, finalization=dict(record["finalization"], report=str(broken / "absent.md"))), "does not exist"),
            ("retired gate record", dict(record, schema="implementation-gate-record/2"), "review an earlier record's head in full"),
            ("pull-request record", dict(record, run=dict(record["run"], target_kind="pull-request")), "a prior record continues a local target"),
            ("no lineage", {k: v for k, v in record.items() if k != "lineage"}, "lacks the record's run"),
        ):
            with self.subTest(name):
                path = broken / f"{name.replace(' ', '-')}.json"
                path.write_text(json.dumps(doc), encoding="utf-8")
                self.refused(attempt(prior=path), needle, "prior-record")
        self.refused(attempt(prior=self.root / "absent.json"), "cannot be read", "prior-record")

        cases = [
            ("unclassified open item", dict(prior_items=self.open_items()[:1]), f"open item `{CONSIDER_ID}` is unclassified"),
            ("unknown prior id", dict(prior_items=self.open_items() + [{"id": "ledger/other", "classification": "fixed",
                                                                        "action": "consider", "note": "n"}]),
             "`ledger/other` is not an open item of the prior record"),
            ("action changed", dict(prior_items=[dict(self.open_items()[0]), dict(self.open_items()[1], action="must-fix")]),
             "was `consider` in the prior record"),
            ("still-open not rendered", dict(findings=[], tasks=[], status="Changes Requested"), "renders it again under its id"),
            ("must-fix downgraded", dict(findings=[self.must_fix(action="consider", priority="P3")], tasks=[]),
             "stays `must-fix` until a classification settles it"),
            ("settled item rendered again", dict(prior_items=self.open_items("still-open", "fixed"), findings=[self.must_fix(), self.consider()]),
             "is fixed, so it is settled and not rendered again"),
            ("unconfirmed carried blocker", dict(tasks=[]), "requires a candidate task with its id"),
            ("routed dropped", None, "drops `ledger/frozen-transfer`"),
            ("prior head", None, "starts at its head"),
            ("delta review over incomplete prior coverage", None, "reviews the full diff, not the delta"),
            ("base changed", None, "a re-review after fixes keeps its base"),
            ("repository changed", None, "but the prior record reviewed"),
            ("lineage rewritten", None, "`lineage=[]` conflicts"),
            ("allowance below the prior", None, "`allowance={\"initial_spent\": false, \"follow_up_spent\": false}` conflicts"),
            ("initial batch again", None, "the prior record already spent its initial batch"),
            ("prior inside this directory", None, "finalize refused"),
        ]
        for name, change, needle in cases:
            with self.subTest(name):
                if change is not None:
                    self.refused(attempt(**change), needle)
                    continue
                value = self.composition(**good)
                private, stage = self.directory(), "compose"
                if name == "routed dropped":
                    # R1b routes its blocker as unresolved; the next run drops it.
                    routed = {"unresolved": [FINDING_ID], "disputed": [], "unrecoverable_inputs": []}
                    base = self.directory()
                    task = fixtures.candidate_task(FINDING_ID)
                    prior = self.accepted(base, 0, self.composition(findings=[self.must_fix()], tasks=[task],
                                                                    batches=[bundle(base, [task])], routed=routed))
                    value["prior_items"] = self.open_items()[:1]
                    value["record"]["verification"]["tasks"] = [self.carried(prior)]
                    self.refused(self.finalize(private, 1, value, prior), needle)
                    continue
                if name == "prior head":
                    value["run"]["prior_head"] = self.heads[2]
                elif name == "delta review over incomplete prior coverage":
                    base = self.directory()
                    task, pending = fixtures.candidate_task(FINDING_ID), fixtures.premise_task(batch=None, ruling="pending")
                    prior = self.accepted(base, 0, self.composition(
                        findings=[self.must_fix()], tasks=[task, pending], batches=[bundle(base, [task])], coverage="incomplete",
                        outstanding=["premise-1: no awaited route"], gaps=["premise-1 unverified"]))
                    value.update(prior_items=self.open_items()[:1], summary=dict(value["summary"], coverage_gaps=["premise-1 unverified"]))
                    value["run"].update(prior_head=self.heads[0], coverage="incomplete")
                    value["record"]["verification"].update(tasks=[self.carried(prior)], outstanding=["premise-1: no awaited route"])
                    self.refused(self.finalize(private, 1, value, prior), needle)
                    continue
                elif name == "base changed":
                    value["run"]["base_sha"] = self.heads[0]
                elif name == "repository changed":
                    value["record"]["repository"] = "/elsewhere/repo"
                elif name == "lineage rewritten":
                    value["record"]["lineage"], stage = [], "derive"
                elif name == "allowance below the prior":
                    value["record"]["verification"]["allowance"], stage = {"initial_spent": False, "follow_up_spent": False}, "derive"
                elif name == "initial batch again":
                    task = fixtures.candidate_task(FINDING_ID)
                    value["record"]["verification"]["tasks"] = [task]
                    value["record"]["verification"]["batches"] = [bundle(private, [task])]
                elif name == "prior inside this directory":
                    result = self.finalize(r1.parent, 1, value, r1)
                    self.assertEqual(result.returncode, 1, result.stdout)
                    self.assertIn(needle, result.stdout)
                    self.assertTrue((r1.parent / "report.md").is_file(), "a refused run leaves the prior intact")
                    continue
                self.refused(self.finalize(private, 1, value, r1), needle, stage)

        # Without a prior record a local target has no prior items or carried confirmations.
        self.refused(self.finalize(self.directory(), 1, self.composition(**good)), "a local target carries prior state only from a prior record")


if __name__ == "__main__":
    unittest.main()
