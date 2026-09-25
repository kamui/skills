#!/usr/bin/env python3
"""Drive grade.py through subprocess on synthetic runs, a stub provisioner and a stub ``claude``.

Usage::

    python3 bench/tools/test_grade.py

Exit codes: 0 every test passed; 1 a test failed.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parent
SCRIPT = TOOLS / "grade.py"
TEMPLATE = TOOLS.parents[1] / "docs" / "research" / "builtin-review-benchmark-2026-09-24" / "prompts" / "grader-template.md"
sys.path.insert(0, str(TOOLS))
import check_manifest  # noqa: E402

RUN_ID, TARGET = "2026-01-01-grade-test", "t-grade-1"
A, B, C, D = "review-code-sonnet-high", "claude-builtin-sonnet-high", "claude-builtin-opus-high", "codex-default"
MODEL = "claude-sonnet-5"

PROVISION_STUB = """\
import argparse, os
parser = argparse.ArgumentParser()
parser.add_argument("command"); parser.add_argument("--target"); parser.add_argument("--out"); parser.add_argument("--cache-root")
args = parser.parse_args()
os.makedirs(args.out)
open(os.path.join(args.out, "main.go"), "w").write("package main\\n")
os.makedirs(args.out + "-cache")
"""

CLAUDE_STUB = """\
import json, os, pathlib, sys
argv = sys.argv[1:]
if argv == ["--version"]:
    print("9.9.9 (Claude Code)")
    sys.exit(0)
prompt = sys.stdin.read()
home, cwd = pathlib.Path(os.environ["HOME"]), pathlib.Path.cwd()
session, model = argv[argv.index("--session-id") + 1], os.environ.get("STUB_MODEL", argv[argv.index("--model") + 1])
pathlib.Path(os.environ["TMPDIR"], "stub.json").write_text(json.dumps({
    "credentials_seen": (home / ".claude" / ".credentials.json").is_file(), "argv": argv, "prompt": prompt,
    "wait_ceiling": os.environ.get("CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS")}))
usage = {"input_tokens": 10, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 1000, "output_tokens": 50,
         "cache_creation": {"ephemeral_5m_input_tokens": 100, "ephemeral_1h_input_tokens": 0}}
read = {"type": "tool_use", "id": "t1", "name": "Read", "input": {"file_path": os.environ.get("STUB_READ", str(cwd / "register.json"))}}
lines = [{"type": "user", "cwd": str(cwd), "message": {"role": "user", "content": prompt}},
         {"type": "assistant", "cwd": str(cwd), "requestId": "r1", "timestamp": "2026-01-01T00:00:01Z",
          "message": {"model": model, "usage": usage, "content": [read]}}]
project = home / ".claude" / "projects" / "-work"
project.mkdir(parents=True)
(project / (session + ".jsonl")).write_text("".join(json.dumps(line) + "\\n" for line in lines))
(cwd / "verdicts.json").write_text("{}")
"""


def item(claim, priority=None, action=None, kind="finding"):
    return {"file": "main.go", "line_start": 3, "line_end": 3, "claim": claim, "consequence": "It breaks.",
            "proposed_fix": None, "native_priority": priority, "native_action": action, "native_confidence": None,
            "kind": kind}


def review(verdict, items, status=None):
    return {"arm": "x", "parse_status": status or ("parsed" if items else "empty"), "native_verdict": verdict,
            "verdict_source": "x", "items": items, "parse_notes": []}


# attempt id: (arm, replicate, disposition, arm_reported_complete, normalized review,
#              [(assignment, fix_sufficiency, duplicate_group, candidate)] per item,
#              expected priority_error per item, expected (approved_on_buggy, zero_recovery, false_clean, completion))
BUGGY = {
    "att-001": (A, 1, "valid completed", True,
                review("Changes Requested", [item("Races on close", "P2", "consider"), item("Rename x", "P3", "must-fix"),
                                             item("Lock order is new", kind="observation")]),
                [("defect:GT-t1", "partial", None, None), ("non-material", "n/a", None, None),
                 ("unresolved", "n/a", None, "NC-1")],
                [True, True, "n/a"], (False, False, False, "completed")),
    "att-002": (A, 2, "stopped: timeout", None, review(None, [item("raw text")], "unresolved"),
                [("false-finding", "n/a", None, None)], ["n/a"], (False, True, False, "incomplete")),
    "att-003": (B, 1, "valid completed", None,
                review("findings", [item("Leaks the conn"), item("Nil map write"), item("Nil map write again")]),
                [("defect:GT-t2", "sufficient", None, None), ("false-finding", "n/a", "g1", None),
                 ("false-finding", "n/a", "g1", None)],
                ["n/a", "n/a", "n/a"], (False, False, False, "completed")),
    "att-004": (B, 2, "valid completed", None, review("empty-array", []), [], [], (True, True, True, "completed")),
    "att-005": (C, 1, "valid completed", None, review("findings", [item("Typo in log"), item("Races on close")]),
                [("non-material", "n/a", None, None), ("defect:GT-t1", "absent", None, None)],
                [False, True], (False, False, False, "completed")),
    "att-006": (C, 2, "harness-invalid: read audit: 1 violation(s)", None, review("findings", [item("Wrong")]),
                [("false-finding", "n/a", None, None)], ["n/a"], (False, True, False, "completed")),
    "att-007": (D, 1, "valid completed", None, review("Summary.", [item("Races on close", "P1"), item("Style", "P2")]),
                [("defect:GT-t1", "sufficient", None, None), ("non-material", "n/a", None, None)],
                [False, False], (False, False, False, "completed")),
    "att-008": (D, 2, "valid completed", None, review("Summary.", [item("Leaks the conn", "P2"), item("Style", "P1")]),
                [("defect:GT-t2", "sufficient", None, None), ("non-material", "n/a", None, None)],
                [True, False], (False, False, False, "completed")),
    "att-009": (D, 3, "valid completed", None, review("patch is correct", []), [], [], (True, True, True, "completed")),
    "att-010": (A, 3, "valid completed", False, review("Approved", []), [], [], (True, True, True, "incomplete")),
}
CLEAN = {
    "att-001": (A, 1, "valid completed", True, review("Approved", [item("Style", "P3", "consider")]),
                [("non-material", "n/a", None, None)], [False], ("n/a", "n/a", "n/a", "completed")),
    "att-002": (D, 1, "valid completed", None, review("patch is correct", []), [], [], ("n/a", "n/a", "n/a", "completed")),
}


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def build_run(root: Path, defects: list, attempts: dict) -> Path:
    run = root / "runs" / RUN_ID
    packet = b"# Packet\n\nThe pull request.\n"
    (run / "fixture").mkdir(parents=True)
    (run / "fixture" / "packet.md").write_bytes(packet)
    write_json(run / "fixture" / "target.json", {"id": TARGET, "shape": "buggy" if defects else "clean"})
    write_json(run / "fixture" / "register.v1.json", {"schema_version": 1, "target": TARGET, "version": 1,
                                                      "defects": [{"id": d} for d in defects], "non_defects": []})
    cells = []
    for attempt_id, (arm, replicate, disposition, complete, doc, *_rest) in attempts.items():
        cell = {"target": TARGET, "arm": arm, "replicate": replicate}
        cells.append(cell)
        write_json(run / "attempts" / attempt_id / "attempt.json", {
            "attempt_id": attempt_id, "cell": cell, "disposition": disposition, "arm_reported_complete": complete,
            "usage": {"priced_total_usd": 0.5},
            "timing": {"dispatched_at": "2026-01-01T00:00:00Z", "payload_validated_at": "2026-01-01T00:01:00Z",
                       "completed_at": "2026-01-01T00:01:00Z" if disposition == "valid completed" else None}})
        write_json(run / "attempts" / attempt_id / "normalized.json", doc)
    write_json(run / "manifest.json", {
        "run_id": RUN_ID, "rubric_version": 1, "rates": [], "planned_cells": cells,
        "cohort": [{"target": TARGET, "register_version": 1, "cohort_group": "regression",
                    "packet_sha256": hashlib.sha256(packet).hexdigest()}]})
    return run


def grade(*argv, env=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *argv], capture_output=True, text=True, encoding="utf-8",
                          env=env)


class Grade(unittest.TestCase):
    attempts = BUGGY
    defects = ["GT-t1", "GT-t2"]

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(os.path.realpath(self.temp.name))
        self.run_dir = build_run(self.root, self.defects, self.attempts)
        self.stub = self.root / "provision_stub.py"
        self.stub.write_text(PROVISION_STUB, encoding="utf-8")
        self.work, self.key = self.root / "work", self.root / "keys" / "key.json"
        self.key.parent.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def prepare(self, work=None, key=None) -> subprocess.CompletedProcess:
        return grade("prepare", "--run", str(self.run_dir), "--target", TARGET, "--work", str(work or self.work),
                     "--key", str(key or self.key), "--template", str(TEMPLATE), "--provision", str(self.stub))

    def prepared(self) -> dict:
        done = self.prepare()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        return json.loads(self.key.read_text(encoding="utf-8"))


class Prepare(Grade):
    def test_reviews_are_blind_and_every_attempt_is_keyed(self):
        key = self.prepared()
        self.assertEqual(stat.S_IMODE(self.key.stat().st_mode), 0o600)
        self.assertEqual([r["attempt_id"] for r in key["reviews"]], sorted(BUGGY))
        tokens = [r["token"] for r in key["reviews"]]
        self.assertEqual(len(set(tokens)), len(BUGGY))
        self.assertTrue(all(len(t) == 12 and t.startswith("blind-") and int(t[6:], 16) >= 0 for t in tokens), tokens)
        self.assertEqual(sorted(p.stem for p in (self.work / "reviews").iterdir()), sorted(tokens))
        self.assertEqual({r["attempt_id"]: r["items"] for r in key["reviews"]},
                         {a: len(spec[4]["items"]) for a, spec in BUGGY.items()})
        texts = {p.name: p.read_text(encoding="utf-8") for p in (self.work / "reviews").iterdir()}
        texts["prompt.md"] = (self.work / "prompt.md").read_text(encoding="utf-8")
        forbidden = [*BUGGY, A, B, C, D, RUN_ID, str(self.run_dir), str(self.root)]
        for name, text in texts.items():
            for needle in forbidden:
                self.assertNotIn(needle, text, name)
        by_attempt = {r["attempt_id"]: texts[r["token"] + ".md"] for r in key["reviews"]}
        self.assertEqual(by_attempt["att-004"].splitlines()[-1], "(no items)")
        self.assertIn("Claim: Wrong", by_attempt["att-006"])
        self.assertNotIn("P2", by_attempt["att-008"])
        prompt = texts["prompt.md"]
        self.assertIn("Registered defects: GT-t1, GT-t2.", prompt)
        listed = [line for line in prompt.splitlines() if line.startswith("- `reviews/blind-")]
        self.assertEqual(listed, [f"- `reviews/{t}.md`: {n} item{'' if n == 1 else 's'}" for t, n in
                                  sorted((r["token"], r["items"]) for r in key["reviews"])])
        self.assertEqual(key["prompt_sha256"], hashlib.sha256(prompt.encode("utf-8")).hexdigest())
        register = (self.run_dir / "fixture" / "register.v1.json").read_bytes()
        self.assertEqual((self.work / "register.json").read_bytes(), register)
        self.assertEqual(key["register"], {"version": 1, "sha256": hashlib.sha256(register).hexdigest()})
        self.assertTrue((self.work / "clone" / "main.go").is_file() and (self.work / "clone-cache").is_dir())
        self.assertTrue((self.work / "rubric.md").read_text(encoding="utf-8").startswith("# Scoring rubric, version 1"))

    def test_refusals(self):
        self.work.mkdir()
        (self.work / "x").write_text("", encoding="utf-8")
        done = self.prepare()
        self.assertEqual(done.returncode, 1)
        self.assertIn("not an empty directory", done.stdout)
        done = self.prepare(work=self.root / "fresh", key=self.root / "fresh" / "key.json")
        self.assertEqual(done.returncode, 1)
        self.assertIn("is inside", done.stdout)
        leaky = copy.deepcopy(BUGGY["att-003"][4])
        leaky["items"][0]["claim"] = "see att-003 output"
        write_json(self.run_dir / "attempts" / "att-003" / "normalized.json", leaky)
        done = self.prepare(work=self.root / "fresh")
        self.assertEqual(done.returncode, 1)
        self.assertRegex(done.stdout, r"reviews/blind-[0-9a-f]{6}\.md names 'att-003'")
        self.assertFalse((self.root / "fresh").exists() or self.key.exists())


class Map(Grade):
    def setUp(self):
        super().setUp()
        self.key_doc = self.prepared()
        self.token = {r["attempt_id"]: r["token"] for r in self.key_doc["reviews"]}
        self.dispatch = {"session_id": "0123abcd-0000-4000-8000-000000000000", "cli_version": "9.9.9", "model": MODEL,
                         "effort": "high", "prompt_sha256": self.key_doc["prompt_sha256"],
                         "dispatched_at": "2026-01-02T00:00:00Z", "completed_at": "2026-01-02T00:10:00Z", "exit_code": 0,
                         "models_observed": [MODEL], "subagents": 0, "audit_violations": [],
                         "usage": {"priced_total_usd": 1.0, "low": 1.0, "high": 1.0}, "verdicts_present": True}
        write_json(self.work / "dispatch.json", self.dispatch)

    def verdicts(self) -> dict:
        reviews, candidates = {}, {}
        for attempt_id, spec in self.attempts.items():
            items = {}
            for n, (assignment, fix, group, candidate) in enumerate(spec[5], 1):
                items[str(n)] = {"assignment": assignment, "duplicate_group": group, "fix_sufficiency": fix,
                                 "candidate": candidate, "notes": f"Quoted item {n}; reasoning."}
                if candidate:
                    candidates.setdefault(candidate, []).append({"review": self.token[attempt_id], "item": n})
            reviews[self.token[attempt_id]] = {"items": items}
        return {"reviews": reviews,
                "new_candidates": [{"id": c, "claim": "Close can deadlock.", "evidence": "Read main.go.",
                                    "confidence": "medium", "would_settle": "A race test.", "items": items}
                                   for c, items in candidates.items()]}

    def map(self, verdicts, version="1") -> subprocess.CompletedProcess:
        write_json(self.work / "verdicts.json", verdicts)
        return grade("map", "--run", str(self.run_dir), "--target", TARGET, "--work", str(self.work),
                     "--key", str(self.key), "--version", version)

    def mapping_path(self, version=1) -> Path:
        return self.run_dir / "scoring" / TARGET / f"mapping.v{version}.json"

    def test_valid_verdicts_unblind_to_a_scorable_mapping(self):
        done = self.map(self.verdicts())
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        mapping = json.loads(self.mapping_path().read_text(encoding="utf-8"))
        schema = json.loads((TOOLS.parent / "schema" / "mapping.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(check_manifest.validate(schema, mapping), [])
        self.assertEqual([a["attempt_id"] for a in mapping["attempts"]], sorted(self.attempts))
        for attempt in mapping["attempts"]:
            spec = self.attempts[attempt["attempt_id"]]
            self.assertEqual(attempt["blind_token"], self.token[attempt["attempt_id"]])
            self.assertEqual([i["item_id"] for i in attempt["items"]], [f"item-{n}" for n in range(len(spec[5]))])
            self.assertEqual([i["assignment"] for i in attempt["items"]], [v[0] for v in spec[5]])
            self.assertEqual([i["priority_error"] for i in attempt["items"]], spec[6], attempt["attempt_id"])
            level = attempt["review_level"]
            self.assertEqual((level["approved_on_buggy"], level["zero_recovery"], level["false_clean"], level["completion"]),
                             spec[7], attempt["attempt_id"])
            self.assertEqual(level["native_verdict"], spec[4]["native_verdict"])
        self.assertEqual(mapping["scored_at"], "2026-01-02T00:10:00Z")
        self.assertTrue(mapping["scored_by"]["blind"])
        self.assertIn(f"prompt sha256 {self.key_doc['prompt_sha256']}", mapping["scored_by"]["adjudicator"])
        self.assertIn(f"session {self.dispatch['session_id']}", mapping["scored_by"]["adjudicator"])
        self.check_extras(mapping)
        card = (self.run_dir / "scoring" / TARGET / "scorecard.v1.md").read_text(encoding="utf-8")
        self.assertEqual([line for line in card.splitlines() if line.startswith("## att-")],
                         [f"## {a} ({self.attempts[a][0]}), {self.token[a]}" for a in sorted(self.attempts)])
        results = self.root / "results.json"
        done = subprocess.run([sys.executable, str(TOOLS / "score.py"), "--run", str(self.run_dir), "--out", str(results),
                               "--metric-code-revision", "test"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.check_results(json.loads(results.read_text(encoding="utf-8")))
        done = self.map(self.verdicts())
        self.assertEqual(done.returncode, 1)
        self.assertIn("never overwritten", done.stdout)

    def check_extras(self, mapping):
        by_id = {a["attempt_id"]: a for a in mapping["attempts"]}
        groups = [i["duplicate_group"] for i in by_id["att-003"]["items"]]
        self.assertEqual(groups, [None, f"{self.token['att-003']}:g1", f"{self.token['att-003']}:g1"])
        self.assertEqual(by_id["att-001"]["items"][2]["notes"], "NC-1: Quoted item 3; reasoning.")
        card = (self.run_dir / "scoring" / TARGET / "scorecard.v1.md").read_text(encoding="utf-8")
        self.assertIn(f"- Items: att-001 item-2 ({self.token['att-001']} item 3)", card)

    def check_results(self, results):
        codex = next(r for r in results["by_arm"] if r["key"] == {"arm": D})
        self.assertEqual((codex["priority_errors"], codex["approved_on_buggy"], codex["recall_attempt_level"]),
                         (1, 1, round((0.5 + 0.5 + 0) / 3, 6)))

    def test_invalid_verdicts_are_refused(self):
        t1, t4 = self.token["att-001"], self.token["att-004"]

        def item_of(v, token, n="1"):
            return v["reviews"][token]["items"][n]

        cases = [
            ("a missing review", lambda v: v["reviews"].pop(t1), f"{t1}: no verdicts for this review"),
            ("an unknown review", lambda v: v["reviews"].update({"blind-000000": {"items": {}}}),
             "blind-000000: not a review the grader was given"),
            ("a missing item", lambda v: v["reviews"][t1]["items"].pop("2"), f'{t1}: item keys'),
            ("a zero-based item", lambda v: v["reviews"][t1]["items"].update({"0": item_of(v, t1)}), f"{t1}: item keys"),
            ("items on an empty review", lambda v: v["reviews"][t4]["items"].update({"1": item_of(v, t1)}),
             f"{t4}: item keys"),
            ("an unregistered defect", lambda v: item_of(v, t1).update(assignment="defect:GT-t9"),
             f"{t1} item 1: defect:GT-t9 is not a defect in the register"),
            ("an unknown assignment", lambda v: item_of(v, t1, "2").update(assignment="maybe"),
             f"{t1} item 2: assignment 'maybe'"),
            ("an ungraded recovery", lambda v: item_of(v, t1).update(fix_sufficiency="n/a"),
             f"{t1} item 1: fix_sufficiency 'n/a' on a recovery"),
            ("a graded non-recovery", lambda v: item_of(v, t1, "2").update(fix_sufficiency="partial"),
             f"{t1} item 2: fix_sufficiency 'partial' on a non-recovery"),
            ("a candidate on a false finding", lambda v: (item_of(v, t1, "3").update(assignment="false-finding")),
             f"{t1} item 3: candidate 'NC-1' on a 'false-finding' item"),
            ("a candidate that does not exist", lambda v: item_of(v, t1, "3").update(candidate="NC-9"),
             f"{t1} item 3: candidate 'NC-9' is not in new_candidates"),
            ("a candidate listing an item that does not name it",
             lambda v: v["new_candidates"][0]["items"].append({"review": t1, "item": 2}),
             f"NC-1: lists items [('{t1}', 2), ('{t1}', 3)], but the items naming it are [('{t1}', 3)]"),
            ("an item naming a candidate that does not list it", lambda v: v["new_candidates"][0].update(
                items=[{"review": self.token["att-002"], "item": 1}]), "NC-1: lists items"),
            ("empty notes", lambda v: item_of(v, t1).update(notes=" "), f"{t1} item 1: notes are empty"),
            ("a missing field", lambda v: item_of(v, t1).pop("candidate"), f"{t1} item 1: needs exactly"),
        ]
        for name, mutate, expected in cases:
            with self.subTest(name):
                verdicts = self.verdicts()
                mutate(verdicts)
                done = self.map(verdicts)
                self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
                self.assertIn(expected, done.stdout)
                self.assertFalse(self.mapping_path().exists())

    def test_dispatch_record_gates_the_mapping(self):
        cases = [
            ("no dispatch", None, "the grader has not been dispatched"),
            ("a violation", dict(self.dispatch, audit_violations=["file tool read outside allowed roots: /x"]),
             "dispatch read audit: file tool read outside allowed roots: /x"),
            ("another prompt", dict(self.dispatch, prompt_sha256="0" * 64), "dispatch ran prompt 000000000000"),
            ("a subagent", dict(self.dispatch, subagents=1), "1 subagent(s)"),
        ]
        for name, record, expected in cases:
            with self.subTest(name):
                (self.work / "dispatch.json").unlink(missing_ok=True)
                if record is not None:
                    write_json(self.work / "dispatch.json", record)
                done = self.map(self.verdicts())
                self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
                self.assertIn(expected, done.stdout)
                self.assertFalse(self.mapping_path().exists())

    def test_an_arm_without_a_rule_is_refused(self):
        path = self.run_dir / "attempts" / "att-004" / "attempt.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        record["cell"]["arm"] = "mystery-arm"
        write_json(path, record)
        done = self.map(self.verdicts())
        self.assertEqual(done.returncode, 1)
        self.assertIn("att-004: arm 'mystery-arm' has no rule", done.stdout)


class MapClean(Map):
    attempts = CLEAN
    defects = []

    def check_extras(self, mapping):
        self.assertIn("none: the register records this target as clean",
                      (self.work / "prompt.md").read_text(encoding="utf-8"))

    def check_results(self, results):
        self.assertEqual({r["key"]["arm"]: r["recall_attempt_level"] for r in results["by_arm"]}, {A: None, D: None})

    test_invalid_verdicts_are_refused = None
    test_an_arm_without_a_rule_is_refused = None


class Dispatch(Grade):
    def setUp(self):
        super().setUp()
        self.prepared()
        bin_dir, self.home = self.root / "bin", self.root / "userhome"
        bin_dir.mkdir()
        (bin_dir / "claude").write_text(f"#!{sys.executable}\n" + CLAUDE_STUB, encoding="utf-8")
        (bin_dir / "claude").chmod(0o755)
        write_json(self.home / ".claude" / ".credentials.json", {"token": "secret"})
        write_json(self.home / ".claude.json", {"oauthAccount": {"id": 1}, "projects": {"/elsewhere": {}}})
        (self.run_dir / "charges.jsonl").write_text(json.dumps({"at": "2026-01-01T00:00:00Z", "step": "earlier", "usd": 1.0})
                                                    + "\n", encoding="utf-8")
        self.env = dict(os.environ, HOME=str(self.home), PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}")

    def dispatch(self, model=MODEL, **extra) -> subprocess.CompletedProcess:
        return grade("dispatch", "--work", str(self.work), "--model", model, "--effort", "high", "--max-budget-usd", "5",
                     "--run", str(self.run_dir), "--step", "grading t-grade-1", env=dict(self.env, **extra))

    def seen(self) -> dict:
        return json.loads((self.work / "tmp" / "stub.json").read_text(encoding="utf-8"))

    def test_clean_session_records_and_charges(self):
        done = self.dispatch()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertTrue(self.seen()["credentials_seen"])
        self.assertFalse((self.work / "home" / ".claude" / ".credentials.json").exists())
        self.assertEqual(json.loads((self.work / "home" / ".claude.json").read_text(encoding="utf-8")),
                         {"oauthAccount": {"id": 1}, "hasCompletedOnboarding": True})
        argv = self.seen()["argv"]
        self.assertEqual(argv, ["-p", "--safe-mode", "--model", MODEL, "--effort", "high", "--session-id", argv[7],
                                "--disallowedTools", "Agent", "--allowedTools", "Read", "Glob", "Grep", "Write", "Bash",
                                "--max-budget-usd", "5.0"])
        self.assertEqual(self.seen()["prompt"], (self.work / "prompt.md").read_text(encoding="utf-8"))
        self.assertEqual(self.seen()["wait_ceiling"], "0")
        record = json.loads((self.work / "dispatch.json").read_text(encoding="utf-8"))
        self.assertEqual(record["session_id"], argv[7])
        self.assertEqual((record["cli_version"], record["model"], record["models_observed"], record["subagents"]),
                         ("9.9.9", MODEL, [MODEL], 0))
        self.assertEqual((record["exit_code"], record["audit_violations"], record["verdicts_present"]), (0, [], True))
        self.assertEqual(record["prompt_sha256"], hashlib.sha256((self.work / "prompt.md").read_bytes()).hexdigest())
        expected = (10 * 2 + 100 * 2.5 + 1000 * 0.2 + 50 * 10) / 1e6
        self.assertAlmostEqual(record["usage"]["priced_total_usd"], expected, places=9)
        timing = json.loads((self.work / "timing.json").read_text(encoding="utf-8"))
        self.assertEqual(timing["root_dispatched_at"], record["dispatched_at"])
        charges = (self.run_dir / "charges.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(charges), 2)
        self.assertEqual(json.loads(charges[1]), {"at": record["completed_at"], "step": "grading t-grade-1",
                                                  "usd": record["usage"]["priced_total_usd"], "model": MODEL,
                                                  "billing": "api-dollars", "session": argv[7][:8]})

    def test_a_read_outside_work_fails_the_dispatch(self):
        outside = self.root / "keys" / "key.json"
        done = self.dispatch(STUB_READ=str(outside))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(f"read audit: file tool read outside allowed roots: {outside}", done.stdout.splitlines())
        self.assertFalse((self.work / "home" / ".claude" / ".credentials.json").exists())
        record = json.loads((self.work / "dispatch.json").read_text(encoding="utf-8"))
        self.assertEqual(record["audit_violations"], [f"file tool read outside allowed roots: {outside}"])

    def test_another_model_fails_the_dispatch(self):
        done = self.dispatch(STUB_MODEL="claude-opus-5-5")
        self.assertEqual(done.returncode, 1)
        self.assertIn(f"models observed claude-opus-5-5, expected {MODEL}", done.stdout)

    def test_a_model_without_rates_is_not_priced(self):
        done = self.dispatch(model="claude-unpriced-1")
        self.assertEqual(done.returncode, 1)
        self.assertIn("no rates.json entry for claude-unpriced-1: usage not priced, no charge recorded", done.stdout)
        self.assertEqual(len((self.run_dir / "charges.jsonl").read_text(encoding="utf-8").splitlines()), 1)
        self.assertFalse((self.work / "home" / ".claude" / ".credentials.json").exists())

    def test_a_second_dispatch_is_refused(self):
        self.assertEqual(self.dispatch().returncode, 0)
        done = self.dispatch()
        self.assertEqual(done.returncode, 1)
        self.assertIn("already dispatched", done.stdout)


if __name__ == "__main__":
    unittest.main()
