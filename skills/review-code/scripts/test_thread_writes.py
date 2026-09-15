#!/usr/bin/env python3
"""Run the documented thread write loop against a stub `gh`.

Usage: python3 scripts/test_thread_writes.py [-v]
Inputs: the thread write loop block in review-code-publish's
`references/publication.md` and resolve-review's
`references/addressing-protocol.md`, and a stub `gh` on PATH that keeps a fake
thread state; no forge access and no live writes.
Exit 0: checks pass; 1: assertion failure; 2: a subprocess cannot run.

Both references must carry the same helper and loop. The loop must refuse an
invalid `writes.jsonl` before any write, preserve reply bodies exactly, post
each reply before its thread action, continue after a failure, record every
attempt, and reconcile an ambiguous write before its single retry, never
posting a confirmed reply again.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parent
SKILLS = SCRIPTS.parent.parent
PUBLICATION = SKILLS / "review-code-publish" / "references" / "publication.md"
ADDRESSING = SKILLS / "resolve-review" / "references" / "addressing-protocol.md"
SHELLS = [shell for shell in ("sh", "bash", "zsh", "dash") if shutil.which(shell)]
NASTY = "Line \"one\"\n\tback\\slash $(touch pwned) `touch pwned2` $HOME 'q' — ünïcödé 🚀 sep\n\n"

FAKE_GH = r"""#!/usr/bin/env python3
import json, os, re, sys
args = sys.argv[1:]
path = os.environ["GH_STATE"]
with open(path, encoding="utf-8") as f:
    state = json.load(f)
request = None
if "--input" in args:
    with open(args[args.index("--input") + 1], encoding="utf-8") as f:
        request = json.load(f)
if "graphql" in args:
    query, target = request["query"], request["variables"]["id"]
    kind = "reopen" if "unresolveReviewThread" in query else "resolve" if "resolveReviewThread" in query else "read"
else:
    kind, target = "reply", re.search(r"comments/(\d+)/replies", " ".join(args)).group(1)
plan = state["plan"].get("%s:%s" % (kind, target), [])
mode = plan.pop(0) if plan else "ok"
state["log"].append({"kind": kind, "target": target, "args": args, "input": request, "mode": mode})
out, err, rc = "", "", 0
if kind == "reply":
    if mode in ("ok", "landed", "short"):
        state["next_id"] += 1
        new = state["next_id"]
        state["comments"].setdefault(state["threads"][target], []).append(
            {"fullDatabaseId": str(new), "url": "https://github.test/c/%d" % new, "body": request["body"],
             "author": {"login": state["viewer"]}, "replyTo": {"fullDatabaseId": target}})
    if mode == "ok":
        out = json.dumps({"id": new, "html_url": "https://github.test/c/%d" % new, "in_reply_to_id": int(target),
                          "body": request["body"]})
    elif mode == "short":
        out = json.dumps({"id": new})
    elif mode == "refuse":
        err, rc = "gh: Validation Failed (HTTP 422)\n", 1
    else:
        err, rc = ("gh: timeout awaiting response\n" if mode == "landed" else "gh: HTTP 502 Bad Gateway\n"), 1
elif kind in ("resolve", "reopen"):
    if mode in ("ok", "landed"):
        state["resolved"][target] = kind == "resolve"
    name = "unresolveReviewThread" if kind == "reopen" else "resolveReviewThread"
    if mode == "ok":
        out = json.dumps({"data": {name: {"thread": {"isResolved": kind == "resolve"}}}})
    elif mode == "stuck":
        out = json.dumps({"data": {name: {"thread": {"isResolved": kind != "resolve"}}}})
    elif mode == "refuse":
        out = json.dumps({"errors": [{"message": "Resource not accessible by integration"}]})
        err, rc = "gh: Resource not accessible by integration (HTTP 403)\n", 1
    else:
        err, rc = ("gh: timeout awaiting response\n" if mode == "landed" else "gh: HTTP 502 Bad Gateway\n"), 1
else:
    if mode == "ok" or mode == "window":
        nodes = [] if mode == "window" else [{"fullDatabaseId": "1", "url": "u", "body": "finding",
                                             "author": {"login": "reviewer"}, "replyTo": None}] + state["comments"].get(target, [])
        out = json.dumps({"data": {"viewer": {"login": state["viewer"]}, "node": {
            "isResolved": state["resolved"].get(target, False),
            "comments": {"pageInfo": {"hasPreviousPage": mode == "window"}, "nodes": nodes}}}})
    else:
        err, rc = "gh: HTTP 502 Bad Gateway\n", 1
with open(path, "w", encoding="utf-8") as f:
    json.dump(state, f)
sys.stdout.write(out)
sys.stderr.write(err)
sys.exit(rc)
"""


def loop_block(path: Path) -> str:
    found = [b for b in re.findall(r"```sh\n(.*?)```", path.read_text(encoding="utf-8"), re.S) if "write-loop.sh" in b]
    assert len(found) == 1, (path, len(found))
    return found[0]


def shared(block: str) -> str:
    return block[:block.index("\nSH\n") + 4]


def row(item, cid=None, tid=None, body=None, action="none", **extra):
    return dict(id=item, comment_id=cid, thread_id=tid, body=body, action=action, **extra)


class Loop(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.binary = self.root / "bin"
        self.binary.mkdir()
        (self.binary / "gh").write_text(FAKE_GH, encoding="utf-8")
        (self.binary / "gh").chmod(0o755)
        self.count = 0

    def tearDown(self):
        self.temp.cleanup()

    def fresh(self, rows, plan=None, threads=None, raw=None):
        self.count += 1
        private = self.root / f"private {self.count}"  # a space checks quoting
        private.mkdir()
        text = raw if raw is not None else "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
        (private / "writes.jsonl").write_text(text, encoding="utf-8")
        state = {"plan": plan or {}, "log": [], "comments": {}, "resolved": {}, "next_id": 9000,
                 "viewer": "addresser", "threads": threads or {str(r["comment_id"]): r["thread_id"]
                                                               for r in rows if r.get("comment_id")}}
        (private / "state.json").write_text(json.dumps(state), encoding="utf-8")
        return private

    def run_loop(self, private, shell="sh", source=PUBLICATION, wrapped=False):
        script = shlex.quote(str(SCRIPTS / "run_events.py")) if wrapped else "''"
        text = (loop_block(source).replace("<private-dir>", shlex.quote(str(private))).replace("<pr>", "7")
                .replace("<recorded-absolute-run_events.py-path>", script))
        env = dict(os.environ, PATH=f"{self.binary}{os.pathsep}{os.environ['PATH']}",
                   GH_STATE=str(private / "state.json"))
        result = subprocess.run([shell, "-c", text], cwd=private, env=env, capture_output=True, text=True,
                                encoding="utf-8", timeout=120)
        state = json.loads((private / "state.json").read_text(encoding="utf-8"))
        results_path = private / "write-results.jsonl"
        results = ([json.loads(line) for line in results_path.read_text(encoding="utf-8").split("\n") if line]
                   if results_path.exists() else [])
        return result, state, results

    @staticmethod
    def calls(state, kind=None):
        return [(c["kind"], c["target"]) for c in state["log"] if kind is None or c["kind"] == kind]

    def test_both_references_carry_the_same_loop(self):
        publication, addressing = loop_block(PUBLICATION), loop_block(ADDRESSING)
        self.assertEqual(shared(publication), shared(addressing))
        self.assertNotIn("run_events", addressing)
        self.assertEqual(publication.count("wrap --private-dir"), 1)
        self.assertIn("--event forge-written --data role=replies -- sh", publication)
        self.assertNotIn("role=resolutions", publication)
        self.assertTrue(addressing.rstrip().endswith('sh "$d/write-loop.sh" "$d" "$pr"'))
        text = PUBLICATION.read_text(encoding="utf-8")
        rules = text[text.index(publication) + len(publication) + 4:].strip().split("\n\n")
        self.assertEqual(len(rules), 3)
        for paragraph in rules:
            self.assertIn(paragraph, ADDRESSING.read_text(encoding="utf-8"))

    def test_mappings_and_shared_wording(self):
        publication = PUBLICATION.read_text(encoding="utf-8")
        addressing = ADDRESSING.read_text(encoding="utf-8")
        protocol = (SKILLS / "code-review-publish" / "references" / "review-protocol.md").read_text(encoding="utf-8")
        self.assertIn("`action`: `resolve` for `fixed`, `accepted`, and `obsolete`; `none` for `still-open`, "
                      "`not-verifiable`, disputed items", publication)
        self.assertIn("`action`: `resolve` for `implemented`, `already-addressed`, and `answered` items", addressing)
        self.assertIn("`reopen` for a thread resolved too early", addressing)
        self.assertIn("`none` for `declined`, `needs-info`, and `blocked`", addressing)
        self.assertNotIn("rather than batching resolutions at the end", addressing + protocol)
        for text in (addressing, protocol):
            self.assertIn("never as a detached sweep of resolutions after the replies", text)

    def test_validation_refuses_before_any_write(self):
        good = row("a", 101, "T1", "ok", "resolve")
        cases = {
            "not a JSON object": "[1]\n",
            "missing action": json.dumps({k: v for k, v in good.items() if k != "action"}) + "\n",
            "unknown field extra": json.dumps(dict(good, extra=1)) + "\n",
            "action is not resolve": json.dumps(dict(good, action="close")) + "\n",
            "a reply needs comment_id and thread_id": json.dumps(row("a", None, "T1", "x")) + "\n",
            "resolve needs thread_id": json.dumps(row("a", None, None, None, "resolve")) + "\n",
            "body is not a non-empty string": json.dumps(dict(good, body="")) + "\n",
            "is_resolved is not a boolean": json.dumps(dict(good, is_resolved=0)) + "\n",
            "duplicate id a": json.dumps(good) + "\n" + json.dumps(row("a", 102, "T2", "y")) + "\n",
            "second thread action on T1": json.dumps(good) + "\n" + json.dumps(row("b", None, "T1", None, "resolve")) + "\n",
            "duplicate reply to comment 101": json.dumps(good) + "\n" + json.dumps(row("b", 101, "T1", "ok")) + "\n",
        }
        for reason, raw in cases.items():
            with self.subTest(reason=reason):
                # the valid first row would be written if validation ran lazily
                private = self.fresh([], raw=json.dumps(row("z", 100, "T0", "first")) + "\n" + raw,
                                     threads={"100": "T0", "101": "T1", "102": "T2"})
                result, state, results = self.run_loop(private)
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertIn(reason, result.stdout)
                self.assertIn("writes.jsonl refused; nothing was written", result.stdout)
                self.assertEqual((state["log"], results), ([], []))

    def test_exact_bodies_in_reply_then_action_order(self):
        rows = [row("a", 101, "T1", NASTY, "resolve"), row("b", None, "T2", None, "resolve", is_resolved=False),
                row("c", 103, "T3", "declined: reason", "none"), row("d", None, "T4", None, "resolve", is_resolved=True),
                row("e"), row("f", 106, "T6", "reopened: regressed", "reopen", is_resolved=True)]
        for source in (PUBLICATION, ADDRESSING):
            for shell in SHELLS:
                for wrapped in ((False, True) if source == PUBLICATION else (False,)):
                    with self.subTest(source=source.name, shell=shell, wrapped=wrapped):
                        private = self.fresh(rows)
                        result, state, results = self.run_loop(private, shell, source, wrapped)
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertEqual(self.calls(state), [("reply", "101"), ("resolve", "T1"), ("resolve", "T2"),
                                                             ("reply", "103"), ("reply", "106"), ("reopen", "T6")])
                        self.assertEqual(state["log"][0]["input"], {"body": NASTY})
                        self.assertEqual(state["comments"]["T1"][0]["body"], NASTY)
                        self.assertFalse((private / "pwned").exists() or (private / "pwned2").exists())
                        self.assertIn("writes: 6 confirmed, 6 not required, 0 unresolved", result.stdout)
                        skipped = {(r["item"], r["reason"]) for r in results if r["kind"] == "skip"}
                        self.assertIn(("d", "thread already in that state"), skipped)
                        self.assertIn(("e", "no thread action"), skipped)
                        replies = [r for r in results if r["step"] == "reply" and r["kind"] == "write"]
                        self.assertTrue(all(r["outcome"] == "confirmed" and r["created_id"] for r in replies))
                        self.assertNotIn(NASTY, (private / "write-results.jsonl").read_text(encoding="utf-8"))
                        events = private / "run-events.jsonl"
                        if wrapped:
                            recorded = [json.loads(line) for line in events.read_text(encoding="utf-8").splitlines()]
                            self.assertEqual([(e["event"], e["data"]["role"], e["data"]["argv0"], e["exit"])
                                              for e in recorded], [("forge-written", "replies", "sh", 0)])
                        else:
                            self.assertFalse(events.exists())
                        again, state, _ = self.run_loop(private, shell, source, wrapped)
                        self.assertEqual(again.returncode, 0, again.stdout)
                        self.assertEqual(len(state["log"]), 6, "a confirmed write ran again")

    def test_failed_reply_blocks_its_action_and_later_items_continue(self):
        rows = [row("a", 101, "T1", "fixed", "resolve"), row("b", 102, "T2", "fixed too", "resolve")]
        private = self.fresh(rows, plan={"reply:101": ["refuse"]})
        result, state, results = self.run_loop(private)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(self.calls(state), [("reply", "101"), ("reply", "102"), ("resolve", "T2")])
        self.assertIn("unresolved a reply: failed (refused: HTTP 422)", result.stdout)
        self.assertIn("unresolved a resolve: blocked (reply not confirmed)", result.stdout)
        self.assertIn("writes: 2 confirmed, 0 not required, 2 unresolved", result.stdout)
        self.assertTrue(Path(next(r for r in results if r["outcome"] == "failed")["stderr"]).read_text(encoding="utf-8"))
        again, state, _ = self.run_loop(private)
        self.assertEqual(again.returncode, 1)
        self.assertEqual(len(state["log"]), 3, "a refused write was retried")

    def test_ambiguous_reply_that_landed_is_reconciled_without_reposting(self):
        for mode in ("landed", "short"):
            with self.subTest(mode=mode):
                private = self.fresh([row("a", 101, "T1", NASTY, "resolve")], plan={"reply:101": [mode]})
                result, state, _ = self.run_loop(private)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertEqual(self.calls(state), [("reply", "101")])
                self.assertIn("unresolved a reply: ambiguous", result.stdout)
                again, state, results = self.run_loop(private)
                self.assertEqual(again.returncode, 0, again.stdout)
                self.assertEqual(self.calls(state), [("reply", "101"), ("read", "T1"), ("resolve", "T1")])
                read = next(r for r in results if r["kind"] == "read")
                self.assertEqual((read["outcome"], read["created_id"]), ("confirmed", 9001))

    def test_ambiguous_reply_that_was_lost_retries_once(self):
        private = self.fresh([row("a", 101, "T1", "fixed", "resolve")], plan={"reply:101": ["lost", "lost"]})
        self.assertEqual(self.run_loop(private)[0].returncode, 1)
        second, state, _ = self.run_loop(private)
        self.assertEqual(second.returncode, 1, second.stdout)
        self.assertEqual(self.calls(state), [("reply", "101"), ("read", "T1"), ("reply", "101")])
        third, state, _ = self.run_loop(private)
        self.assertEqual(third.returncode, 1)
        self.assertEqual(self.calls(state, "reply"), [("reply", "101")] * 2, "more than one retry")
        self.assertIn("unresolved a reply: blocked (retry budget spent)", third.stdout)
        success = self.fresh([row("a", 101, "T1", "fixed", "resolve")], plan={"reply:101": ["lost"]})
        self.run_loop(success)
        retried, state, _ = self.run_loop(success)
        self.assertEqual(retried.returncode, 0, retried.stdout)
        self.assertEqual(self.calls(state), [("reply", "101"), ("read", "T1"), ("reply", "101"), ("resolve", "T1")])

    def test_unsettled_reconciliation_never_retries(self):
        for read_mode in ("lost", "window"):
            with self.subTest(read=read_mode):
                private = self.fresh([row("a", 101, "T1", "fixed", "none")],
                                     plan={"reply:101": ["lost"], "read:T1": [read_mode]})
                self.run_loop(private)
                result, state, _ = self.run_loop(private)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(self.calls(state), [("reply", "101"), ("read", "T1")])
                self.assertIn("unresolved a reply: blocked (reconciliation unsettled; not retried)", result.stdout)

    def test_failed_resolution_after_confirmed_reply_never_reposts(self):
        private = self.fresh([row("a", 101, "T1", "fixed", "resolve")], plan={"resolve:T1": ["refuse"]})
        result, state, _ = self.run_loop(private)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unresolved a resolve: failed (refused: HTTP 403)", result.stdout)
        again, state, _ = self.run_loop(private)
        self.assertEqual((again.returncode, self.calls(state)), (1, [("reply", "101"), ("resolve", "T1")]))
        private = self.fresh([row("a", 101, "T1", "fixed", "resolve")], plan={"resolve:T1": ["lost"]})
        self.assertEqual(self.run_loop(private)[0].returncode, 1)
        again, state, _ = self.run_loop(private)
        self.assertEqual(again.returncode, 0, again.stdout)
        self.assertEqual(self.calls(state), [("reply", "101"), ("resolve", "T1"), ("read", "T1"), ("resolve", "T1")])

    def test_unexpected_returned_state_is_a_failure(self):
        private = self.fresh([row("a", None, "T1", None, "resolve")], plan={"resolve:T1": ["stuck"]})
        result, _, results = self.run_loop(private)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unresolved a resolve: failed (returned isResolved false)", result.stdout)
        self.assertEqual(results[-1]["is_resolved"], False)

    def test_all_skipped_round_succeeds(self):
        private = self.fresh([row("d", None, "T4", None, "resolve", is_resolved=True), row("e"),
                              row("g", None, "T7", None, "reopen", is_resolved=False)])
        result, state, results = self.run_loop(private)
        self.assertEqual((result.returncode, state["log"]), (0, []), result.stdout)
        self.assertIn("writes: 0 confirmed, 6 not required, 0 unresolved", result.stdout)
        self.assertEqual({r["outcome"] for r in results}, {"skipped"})
        empty = self.fresh([])
        self.assertEqual(self.run_loop(empty)[0].returncode, 0)

    def test_changed_body_is_not_covered_by_an_earlier_confirmation(self):
        private = self.fresh([row("a", 101, "T1", "first draft", "none")])
        self.assertEqual(self.run_loop(private)[0].returncode, 0)
        (private / "writes.jsonl").write_text(json.dumps(row("a", 101, "T1", "corrected draft", "none")) + "\n",
                                              encoding="utf-8")
        result, state, _ = self.run_loop(private)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual([c["input"]["body"] for c in state["log"]], ["first draft", "corrected draft"])


if __name__ == "__main__":
    try:
        unittest.main()
    except OSError as error:
        print(f"test_thread_writes: cannot run a subprocess: {error}", file=sys.stderr)
        raise SystemExit(2)
