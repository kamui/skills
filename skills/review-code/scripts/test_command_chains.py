#!/usr/bin/env python3
"""Run the documented one-invocation command chains against local fixtures.

Usage: python3 scripts/test_command_chains.py
Inputs: SKILL.md step 5's `finalize_review.py` commands, the pull-request target's root
fetch and guarded early-build block, the publisher's freshness and
review-submission block, its dismissal command, the app-token acquisition
blocks in `audit-code-publish` and `code-review-publish`, a disposable Git
repository, and a stub `gh` on PATH; no forge access and no live writes.
Exit 0: checks pass; 1: assertion failure; 2: a subprocess cannot run.

The finalize command must produce the same payload, batch, and fragment bytes
as the three commands run separately, and stop visibly at the first failing
stage. The submission block must never POST after a failed, empty, malformed,
or mismatched head, must exit 3 only on that preflight route, and must keep a
POST failure's own status under a distinct attempted-write stage. Every token
acquisition must publish its write under a proved token and write nothing when
the token is missing or refused; the dismissal, whose single write is its own
proof, must write nothing when the token is missing. Neither the token nor the
dismissal message may reach `argv` or the inner shell's expansions.
The root block must build the first-review store once, byte-identical to the
direct build, with the diff persisted rather than printed, and must omit the
build whenever first-review status is unproven, while a failed root query or
build stays visible and stops.
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

import forge_packet
import test_compose_review as fixtures

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
TARGET = SKILL / "references" / "pull-request-target.md"
PUBLICATION = SKILL.parent / "review-code-publish" / "references" / "publication.md"
TOKEN_BLOCKS = {"audit": SKILL.parent / "audit-code-publish" / "references" / "publishing.md",
                "legacy": SKILL.parent / "code-review-publish" / "references" / "review-protocol.md"}
SHELLS = [shell for shell in ("sh", "bash", "zsh", "dash") if shutil.which(shell)]

FAKE_GH = r"""#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
with open(os.environ["GH_LOG"], "a", encoding="utf-8") as log:
    log.write(json.dumps(args) + "\n")
if os.environ.get("GH_TOKEN_LOG"):
    with open(os.environ["GH_TOKEN_LOG"], "a", encoding="utf-8") as tokens:
        tokens.write(json.dumps({"args": args, "token": os.environ.get("GH_TOKEN")}) + "\n")
if "graphql" in args and os.environ.get("GH_ROOT_FILE"):  # the root query
    rc = int(os.environ.get("GH_ROOT_RC", "0"))
    if rc:
        sys.stderr.write("gh: HTTP 502: Bad Gateway\n")
        sys.exit(rc)
    sys.stdout.write(open(os.environ["GH_ROOT_FILE"], encoding="utf-8").read())
    sys.exit(0)
if "--silent" in args:  # the preflight's token check
    sys.exit(int(os.environ.get("GH_SILENT_RC", "0")))
if "--method" in args and "PUT" in args:  # a dismissal
    print(json.dumps({"id": 992, "state": "DISMISSED"}))
    sys.exit(0)
if "--method" in args and "POST" in args:
    rc = int(os.environ.get("GH_POST_RC", "0"))
    if rc == 0:
        print(json.dumps({"id": 991, "state": "COMMENTED"}))
    else:
        sys.stderr.write("gh: HTTP 502 or timeout; outcome unknown\n")
    sys.exit(rc)
mode = os.environ.get("GH_HEAD_MODE", "match")
if mode == "fail":
    sys.stderr.write("gh: HTTP 404: Not Found\n")
    sys.exit(1)
if mode == "empty":
    sys.exit(0)
print({"match": os.environ["GH_HEAD"], "mismatch": "c" * 40, "malformed": "not-a-sha",
       "short": os.environ["GH_HEAD"][:7], "two-lines": os.environ["GH_HEAD"] + "\n" + os.environ["GH_HEAD"]}[mode])
"""

EMIT_FAILS = r"""#!/bin/sh
case "$1" in */validate_review.py)
  if [ "$2" = --emit-batch ]; then echo "summary.body: injected-batch-violation: emission refused"; exit 1; fi ;;
esac
case " $* " in *" --render "*) echo render >> "$CHAIN_LOG" ;; esac
exec "$REAL_PYTHON" "$@"
"""


def command(text: str, gate: bool) -> str:
    found = [c for c in re.findall(r"`(python3 scripts/finalize_review\.py [^`]*)`", text)
             if ("--profile implementation-gate" in c) == gate]
    assert len(found) == 1, (gate, found)
    return found[0]


def block(text: str, marker: str) -> str:
    found = [b for b in re.findall(r"```sh\n(.*?)```", text, re.S) if marker in b]
    assert len(found) == 1, (marker, len(found))
    return found[0]


class Chains(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def sh(self, shell, text, env=None, cwd=None):
        return subprocess.run([shell, "-c", text], cwd=cwd, env=env, capture_output=True, text=True,
                              encoding="utf-8", timeout=120)

    def repository(self):
        repo = self.root / "repo"
        (repo / "src").mkdir(parents=True)

        def git(*args):
            return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8",
                                  check=True).stdout.strip()

        def write(name, count, changed=None):
            lines = [f"line {i}" if i != changed else f"changed {i}" for i in range(1, count + 1)]
            (repo / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
        git("init", "-q")
        git("config", "user.name", "Test")
        git("config", "user.email", "test@example.invalid")
        write("src/payments.ts", 60)
        write("src/retry-policy.ts", 30)
        write("src/queue.ts", 10)
        git("add", ".")
        git("commit", "-qm", "base")
        base = git("rev-parse", "HEAD")
        write("src/payments.ts", 60, 42)
        write("src/retry-policy.ts", 30, 18)
        write("src/queue.ts", 10, 5)
        git("commit", "-qam", "change")
        return repo, base, git("rev-parse", "HEAD")

    def compositions(self, base, head):
        full = fixtures.base_composition()
        full["run"].update(head=head, base_sha=base, merge_base=base, target_kind="range", target="main..HEAD",
                           change_description="change")
        full["run"].pop("repository_url")
        linked = fixtures.base_composition()
        linked["run"].update(head=head, base_sha=base, merge_base=base)
        return {"range fixture": full, "pull-request fixture": linked}

    def private(self, repo, base, head, name):
        private = self.root / name
        private.mkdir()
        store = private / f"review-context-{head}.json"
        subprocess.run([sys.executable, str(SCRIPTS / "review_context.py"), "--merge-base", base, "--head", head,
                        "--store", str(store)], cwd=repo, capture_output=True, check=True)
        return private, store

    def composition_block(self, private, store):
        text = command((SKILL / "SKILL.md").read_text(encoding="utf-8"), gate=False)
        return text.replace("<private-dir>", shlex.quote(str(private))).replace("<store>", shlex.quote(str(store)))

    def direct(self, store, composition):
        def run(args, stdin=None):
            result = subprocess.run([sys.executable, *args], cwd=SKILL, input=stdin, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return result.stdout
        payload = run(["scripts/compose_review.py", "--store", str(store), str(composition)])
        return payload, run(["scripts/validate_review.py", "--emit-batch"], payload), \
            run(["scripts/validate_review.py", "--render"], payload)

    def test_composition_chain_is_byte_identical(self):
        repo, base, head = self.repository()
        for name, composition in self.compositions(base, head).items():
            for shell in SHELLS:
                with self.subTest(fixture=name, shell=shell):
                    private, store = self.private(repo, base, head, f"{name}-{shell}".replace(" ", "-"))
                    path = private / "composition.json"
                    path.write_text(json.dumps(composition), encoding="utf-8")
                    payload, batch, fragments = self.direct(store, path)
                    self.assertTrue(fragments.strip())
                    result = self.sh(shell, self.composition_block(private, store), cwd=SKILL)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual((private / "payload.json").read_bytes(), payload)
                    self.assertEqual((private / "batch.json").read_bytes(), batch)
                    self.assertEqual((private / "fragments.md").read_bytes(), fragments)
                    self.assertEqual(result.stdout, fragments.decode("utf-8"))
                    self.assertEqual(sorted(p.name for p in private.glob("*.part")), [])

    def test_composition_failure_is_visible_and_stops(self):
        repo, base, head = self.repository()
        composition = self.compositions(base, head)["range fixture"]
        composition["findings"][0].update(priority="P0", action="consider")
        for shell in SHELLS:
            with self.subTest(shell=shell):
                private, store = self.private(repo, base, head, f"refused-{shell}")
                (private / "composition.json").write_text(json.dumps(composition), encoding="utf-8")
                for stale in ("payload.json", "batch.json", "fragments.md"):
                    (private / stale).write_text("stale success\n", encoding="utf-8")
                result = self.sh(shell, self.composition_block(private, store), cwd=SKILL)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("compose failed with exit 1; later stages did not run:", result.stdout)
                self.assertRegex(result.stdout, r"findings\[0\]")
                for artifact in ("payload.json", "batch.json", "fragments.md", "payload.json.part"):
                    self.assertFalse((private / artifact).exists(), artifact)
        private, store = self.private(repo, base, head, "unreadable")
        result = self.sh("sh", self.composition_block(private, store), cwd=SKILL)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("compose failed with exit 2", result.stdout)
        self.assertIn("compose_review", result.stdout)

    def test_batch_validation_failure_is_visible_and_stops(self):
        repo, base, head = self.repository()
        composition = self.compositions(base, head)["range fixture"]
        binary = self.root / "bin"
        binary.mkdir()
        (binary / "python3").write_text(EMIT_FAILS, encoding="utf-8")
        (binary / "python3").chmod(0o755)
        log = self.root / "chain.log"
        env = dict(os.environ, PATH=f"{binary}{os.pathsep}{os.environ['PATH']}", REAL_PYTHON=sys.executable,
                   CHAIN_LOG=str(log))
        for shell in SHELLS:
            with self.subTest(shell=shell):
                private, store = self.private(repo, base, head, f"emit-{shell}")
                (private / "composition.json").write_text(json.dumps(composition), encoding="utf-8")
                (private / "batch.json").write_text("stale success\n", encoding="utf-8")
                result = self.sh(shell, self.composition_block(private, store), env=env, cwd=SKILL)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("emit-batch failed with exit 1; later stages did not run:", result.stdout)
                self.assertIn("injected-batch-violation", result.stdout)
                self.assertTrue((private / "payload.json").exists())
                self.assertFalse((private / "batch.json").exists())
                self.assertFalse((private / "fragments.md").exists())
                self.assertFalse(log.exists(), "render ran after a failed emission")

    # --- implementation-gate profile ---------------------------------------

    def gate_block(self, private, store):
        text = command((SKILL / "SKILL.md").read_text(encoding="utf-8"), gate=True)
        return text.replace("<private-dir>", shlex.quote(str(private))).replace("<store>", shlex.quote(str(store)))

    def gate_composition(self, base, head, store):
        value = fixtures.gate_composition()
        value["run"].update(head=head, base_sha=base, merge_base=base)
        value["record"]["paths"]["store"] = str(store)
        value["record"]["files"] = [{"path": p, "state": "reviewed"} for p in ("src/payments.ts", "src/retry-policy.ts", "src/queue.ts")]
        for item in value["record"]["check_evidence"]:
            if item["outcome"] != "historical":
                item["head"] = head
        return value

    def test_implementation_gate_chain_is_byte_identical(self):
        repo, base, head = self.repository()
        for shell in SHELLS:
            with self.subTest(shell=shell):
                private, store = self.private(repo, base, head, f"gate-{shell}")
                path = private / "composition.json"
                path.write_text(json.dumps(self.gate_composition(base, head, store)), encoding="utf-8")
                direct = subprocess.run([sys.executable, "scripts/compose_review.py", "--profile", "implementation-gate",
                                         "--store", str(store), str(path)], cwd=SKILL, capture_output=True)
                self.assertEqual(direct.returncode, 0, direct.stdout + direct.stderr)
                result = self.sh(shell, self.gate_block(private, store), cwd=SKILL)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual((private / "record.json").read_bytes(), direct.stdout)
                self.assertEqual(result.stdout, f"record {private}/record.json\n")
                self.assertTrue((private / "addenda").is_dir(), "the block creates the addenda directory a continuation appends to")
                for absent in ("payload.json", "batch.json", "fragments.md"):
                    self.assertFalse((private / absent).exists(), absent)
                self.assertEqual(sorted(p.name for p in private.glob("*.part")), [])

    def test_implementation_gate_failure_is_visible_and_stops(self):
        repo, base, head = self.repository()
        for shell in SHELLS:
            with self.subTest(shell=shell):
                private, store = self.private(repo, base, head, f"gate-refused-{shell}")
                composition = self.gate_composition(base, head, store)
                composition["record"]["verification"]["follow_up_spent"] = True
                (private / "composition.json").write_text(json.dumps(composition), encoding="utf-8")
                (private / "record.json").write_text("stale success\n", encoding="utf-8")
                result = self.sh(shell, self.gate_block(private, store), cwd=SKILL)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("record failed with exit 1; later stages did not run:", result.stdout)
                self.assertIn("follow_up_spent", result.stdout)
                for artifact in ("record.json", "record.json.part"):
                    self.assertFalse((private / artifact).exists(), artifact)

    # --- root fetch and guarded early build ---------------------------------

    def root_page(self, base, head, reviews=(), threads=(), comments=(), edit=None):
        page = forge_packet.sample_root()
        pr = page["data"]["repository"]["pullRequest"]
        pr.update(baseRefOid=base, headRefOid=head)
        pr["reviews"] = forge_packet.connection(list(reviews), len(reviews), False, None)
        pr["reviewThreads"] = forge_packet.connection(list(threads), len(threads), False, None)
        pr["comments"] = forge_packet.connection(list(comments), len(comments), False, None)
        if edit:
            edit(pr)
        return page

    @staticmethod
    def thread(*comments, has_next=False, total=None):
        nodes = [{"fullDatabaseId": str(5000 + i), "author": {"login": login}, "body": "prose", "createdAt": "2026-09-01T09:00:00Z",
                  "updatedAt": "2026-09-01T09:00:00Z", "lastEditedAt": None, "replyTo": None, "pullRequestReview": None, "url": "u"}
                 for i, login in enumerate(comments)]
        return {"id": "PRRT_1", "isResolved": False, "isOutdated": False, "path": "src/queue.ts", "line": 5, "originalLine": 5,
                "diffSide": "RIGHT", "comments": forge_packet.connection(nodes, len(nodes) if total is None else total, has_next)}

    @staticmethod
    def review(login):
        return {"fullDatabaseId": "900", "author": {"login": login}, "state": "COMMENTED", "body": "b", "submittedAt": "2026-09-01T09:00:00Z",
                "updatedAt": "2026-09-01T09:00:00Z", "lastEditedAt": None, "commit": {"oid": "a" * 40}, "url": "u"}

    def root_block(self, shell, repo, page, reviewer="reviewer", root_rc=0, prepare=None):
        private = Path(tempfile.mkdtemp(dir=self.root))
        root = private / "page.json"
        root.write_text(json.dumps(page), encoding="utf-8")
        if prepare:
            prepare(private)
        env = dict(os.environ, PATH=f"{self.gh_binary()}{os.pathsep}{os.environ['PATH']}", GH_LOG=str(private / "gh.log"),
                   GH_ROOT_FILE=str(root), GH_ROOT_RC=str(root_rc))
        text = (block(TARGET.read_text(encoding="utf-8"), "early-build.txt")
                .replace("<private-dir>", shlex.quote(str(private))).replace("<reviewer-login>", shlex.quote(reviewer))
                .replace("<run-events-script>", shlex.quote(str(SCRIPTS / "run_events.py")))
                .replace("<forge-packet-script>", shlex.quote(str(SCRIPTS / "forge_packet.py")))
                .replace("<review-context-script>", shlex.quote(str(SCRIPTS / "review_context.py"))).replace("<pr>", "7"))
        self.assertNotRegex(text.split("\n", 1)[0], r"<[a-z][^>]*>")
        result = self.sh(shell, text, env=env, cwd=repo)
        events = []
        if (private / "run-events.jsonl").exists():
            events = [json.loads(line) for line in (private / "run-events.jsonl").read_text(encoding="utf-8").splitlines()]
        return result, private, events

    def assert_deferred(self, result, private, reason):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, f"deferred: {reason}\n")
        self.assertEqual((private / "early-build.txt").read_text(encoding="utf-8"), result.stdout)
        self.assertTrue((private / "forge-1.json").exists(), "the root page is saved whatever the guard decides")
        self.assertEqual(sorted(p.name for p in private.glob("review-context-*.json")), [], "no early build")
        self.assertFalse((private / "context-build.out").exists())

    def test_root_block_builds_a_proven_first_review_once_and_privately(self):
        repo, base, head = self.repository()
        store_name = f"review-context-{head}.json"
        for shell in SHELLS:
            with self.subTest(shell=shell):
                direct = Path(tempfile.mkdtemp(dir=self.root))
                build = subprocess.run([sys.executable, str(SCRIPTS / "review_context.py"), "--merge-base", base, "--head", head,
                                        "--store", str(direct / store_name)], cwd=repo, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(build.returncode, 0, build.stderr)
                result, private, events = self.root_block(shell, repo, self.root_page(base, head))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stdout, f"eligible {base} {head}\n")
                self.assertEqual((private / "forge-1.json").read_text(encoding="utf-8"), json.dumps(self.root_page(base, head)))
                self.assertEqual((private / store_name).read_bytes(), (direct / store_name).read_bytes(),
                                 "the early store is the store step 2 would build")
                self.assertEqual((private / "context-build.out").read_text(encoding="utf-8"), build.stdout,
                                 "the build's stdout is persisted, not printed")
                self.assertIn("## diff", build.stdout)
                self.assertNotIn("## diff", result.stdout)
                self.assertEqual((private / "context-build.err").read_text(encoding="utf-8"), "")
                self.assertEqual([(e["event"], e.get("data", {}).get("role")) for e in events],
                                 [("forge-fetched", "root"), ("context-built", None)])

    def test_root_block_defers_when_first_review_status_is_unproven(self):
        repo, base, head = self.repository()
        me = "reviewer"

        def no_page_info(pr):
            del pr["comments"]["pageInfo"]

        def top_level_continuation(pr):
            pr["reviews"]["pageInfo"]["hasNextPage"] = True
            pr["reviews"]["totalCount"] = 2

        def merged(pr):
            pr.update(state="MERGED", merged=True)

        cases = [
            ("prior review", dict(reviews=[self.review(me)]), "prior state from the posting identity"),
            ("prior app review, suffix ignored", dict(reviews=[self.review("Reviewer[bot]")]), "prior state from the posting identity"),
            ("prior thread reply", dict(threads=[self.thread("author", me)]), "prior state from the posting identity"),
            ("prior pull-request comment", dict(comments=[{"fullDatabaseId": "77", "author": {"login": me}, "body": "<!-- x -->",
                                                          "createdAt": "2026-09-01T09:00:00Z", "updatedAt": "2026-09-01T09:00:00Z",
                                                          "lastEditedAt": None, "url": "u"}]), "prior state from the posting identity"),
            ("top-level continuation", dict(edit=top_level_continuation), "a review-state connection is not proven complete"),
            ("nested thread continuation hiding a later reply", dict(threads=[self.thread("author", has_next=True, total=2)]),
             "a thread's comments are not proven complete"),
            ("missing pagination metadata", dict(edit=no_page_info), "a review-state connection is not proven complete"),
            ("merged target", dict(edit=merged), "target state MERGED merged=true"),
        ]
        for name, kwargs, reason in cases:
            with self.subTest(case=name):
                result, private, _ = self.root_block("sh", repo, self.root_page(base, head, **kwargs))
                self.assert_deferred(result, private, reason)
        for shell in SHELLS:
            with self.subTest(case="prior review", shell=shell):
                result, private, _ = self.root_block(shell, repo, self.root_page(base, head, reviews=[self.review(me)]))
                self.assert_deferred(result, private, "prior state from the posting identity")
        with self.subTest(case="posting identity unknown"):
            result, private, _ = self.root_block("sh", repo, self.root_page(base, head), reviewer="")
            self.assert_deferred(result, private, "posting identity unknown")
        with self.subTest(case="invalid head field"):
            result, private, _ = self.root_block("sh", repo, self.root_page(base, head[:7]))
            self.assert_deferred(result, private, "required root fields missing or invalid")
        with self.subTest(case="guard exits without a verdict"):
            # `data` is a truthy non-object, so the guard raises before its own isinstance checks.
            result, private, _ = self.root_block("sh", repo, {"data": "x"})
            self.assert_deferred(result, private, "eligibility guard failed with exit 1")
            self.assertIn("AttributeError", result.stderr, "the guard's own failure stays visible")

    def test_root_block_defers_missing_commits_and_an_unresolved_merge_base(self):
        repo, base, head = self.repository()
        with self.subTest(case="missing head object"):
            result, private, _ = self.root_block("sh", repo, self.root_page(base, "a" * 40))
            self.assert_deferred(result, private, f"head commit {'a' * 40} not present locally")
        with self.subTest(case="missing base object"):
            result, private, _ = self.root_block("sh", repo, self.root_page("b" * 40, head))
            self.assert_deferred(result, private, f"base commit {'b' * 40} not present locally")
        orphan = subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit-tree",
                                 "-m", "orphan", "4b825dc642cb6eb9a060e54bf8d69288fbee4904"], cwd=repo, capture_output=True,
                                text=True, encoding="utf-8", check=True).stdout.strip()
        with self.subTest(case="unresolved merge-base"):
            result, private, _ = self.root_block("sh", repo, self.root_page(orphan, head))
            self.assert_deferred(result, private, "merge-base unresolved")

    def test_root_block_keeps_query_and_build_failures_visible(self):
        repo, base, head = self.repository()
        for shell in SHELLS:
            with self.subTest(case="root query failure", shell=shell):
                result, private, events = self.root_block(shell, repo, self.root_page(base, head), root_rc=1)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("root query failed with exit 1; no early build:", result.stdout)
                self.assertIn("HTTP 502", result.stderr)
                self.assertFalse((private / "early-build.txt").exists())
                self.assertEqual(sorted(p.name for p in private.glob("review-context-*.json")), [])
                self.assertEqual([(e["event"], e["exit"]) for e in events], [("forge-fetched", 1)])

        def occupy_store(private):
            (private / f"review-context-{head}.json").mkdir()

        for shell in SHELLS:
            with self.subTest(case="build failure", shell=shell):
                result, private, _ = self.root_block(shell, repo, self.root_page(base, head), prepare=occupy_store)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("early context build failed with exit 2:", result.stdout)
                self.assertIn("review_context", result.stdout)
                self.assertEqual((private / "early-build.txt").read_text(encoding="utf-8"), f"eligible {base} {head}\n")

    # --- publisher freshness and submission ---------------------------------

    def gh_binary(self):
        binary = self.root / "gh-bin"
        if not binary.exists():
            binary.mkdir()
            (binary / "gh").write_text(FAKE_GH, encoding="utf-8")
            (binary / "gh").chmod(0o755)
        return binary

    def submission(self, shell, head_mode="match", post_rc=0, wrapped=True, batch_head=fixtures.HEAD, tok="",
                   silent_rc=0):
        private = Path(tempfile.mkdtemp(dir=self.root))
        (private / "batch.json").write_text(json.dumps({"commit_id": batch_head, "event": "COMMENT", "body": "b",
                                                        "comments": []}), encoding="utf-8")
        binary = self.gh_binary()
        log = private / "gh.log"
        env = dict(os.environ, PATH=f"{binary}{os.pathsep}{os.environ['PATH']}", GH_LOG=str(log),
                   GH_HEAD=fixtures.HEAD, GH_HEAD_MODE=head_mode, GH_POST_RC=str(post_rc),
                   GH_TOKEN_LOG=str(private / "token.log"), GH_SILENT_RC=str(silent_rc))
        env.pop("GH_TOKEN", None)  # only the block's own acquisition may supply one
        script = shlex.quote(str(SCRIPTS / "run_events.py")) if wrapped else "''"
        text = (block(PUBLICATION.read_text(encoding="utf-8"), "preflight failed")
                .replace("<private-dir>", shlex.quote(str(private)))
                .replace("<skill-root>/scripts/run_events.py", script)
                .replace("<pr>", "7").replace("<reviewed head>", fixtures.HEAD))
        if tok:  # the block assigns `tok=` empty; a reviewing app fills it in
            marker = "tok=  #"
            self.assertIn(marker, text)
            text = text.replace(marker, "tok=%s  #" % shlex.quote(tok), 1)
        self.assertNotRegex(text.split("\n", 1)[0], r"<[a-z][^>]*>")
        result = self.sh(shell, text, env=env, cwd=self.root)
        calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
        events = []
        if (private / "run-events.jsonl").exists():
            events = [json.loads(line) for line in (private / "run-events.jsonl").read_text(encoding="utf-8").splitlines()]
        return result, calls, events, private

    @staticmethod
    def posts(calls):
        return [call for call in calls if "POST" in call]

    @staticmethod
    def tokens(private):
        path = private / "token.log"
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []

    def test_app_token_is_acquired_in_preflight_and_reused_by_the_post(self):
        # The command is several words. Expanded bare in command position it would be one
        # command name under zsh, which is the failure this block runs through `sh -c` to avoid.
        for shell in SHELLS:
            with self.subTest(shell=shell):
                result, calls, events, private = self.submission(shell, tok="printf %s app-token-xyz")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("preflight passed", result.stdout)
                self.assertEqual(len(self.posts(calls)), 1, calls)
                seen = self.tokens(private)
                checks = [r for r in seen if "--silent" in r["args"]]
                self.assertEqual(len(checks), 1, "the preflight checks the token exactly once")
                self.assertEqual(checks[0]["token"], "app-token-xyz")
                posted = [r for r in seen if "POST" in r["args"]]
                self.assertEqual([r["token"] for r in posted], ["app-token-xyz"],
                                 "the POST reuses the token the preflight acquired")
                self.assertNotIn("app-token-xyz", json.dumps(calls), "a token never reaches argv")

    def test_unusable_app_token_is_a_preflight_failure_that_writes_nothing(self):
        # A token the forge refuses is non-empty, so emptiness alone does not settle it: minted
        # against the wrong repository, or an installation suspended since it was issued.
        cases = (("printf %s ", 0, "prints nothing"), ("false unused-argument", 0, "exits non-zero"),
                 ("printf %s stale-token", 22, "the forge refuses the token"))
        for shell in SHELLS:
            for tok, silent_rc, reason in cases:
                with self.subTest(shell=shell, tok=reason):
                    result, calls, events, private = self.submission(shell, tok=tok, silent_rc=silent_rc)
                    self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                    self.assertIn("preflight failed: the review-token command", result.stdout)
                    self.assertIn("nothing was written", result.stdout)
                    self.assertNotIn("write attempted", result.stdout)
                    self.assertEqual(self.posts(calls), [])
                    self.assertFalse((private / "review-response.json").exists())

    # --- the app token in the other publishers and in the dismissal ---------

    def token_run(self, shell, source, tok, silent_rc=0):
        private = Path(tempfile.mkdtemp(dir=self.root))
        log, tokens = private / "gh.log", private / "token.log"
        env = dict(os.environ, PATH=f"{self.gh_binary()}{os.pathsep}{os.environ['PATH']}", GH_LOG=str(log),
                   GH_TOKEN_LOG=str(tokens), GH_SILENT_RC=str(silent_rc), GH_TOKEN="authenticated-user-token")
        text = (block(source.read_text(encoding="utf-8"), "review-token command")
                .replace("<review-token command>", tok)
                .replace("<the review write this invocation makes>",
                         'gh api --method POST "repos/{owner}/{repo}/pulls/7/reviews" --input /dev/null'))
        result = self.sh(shell, text, env=env, cwd=self.root)
        calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
        seen = [json.loads(line) for line in tokens.read_text(encoding="utf-8").splitlines()] if tokens.exists() else []
        return result, calls, seen

    def test_the_other_publishers_write_under_a_proved_app_token(self):
        # The acquisition and the write share one invocation: an exported variable does not
        # survive to the next one, and a write in a shell of its own goes out as the user.
        for name, source in TOKEN_BLOCKS.items():
            raw = block(source.read_text(encoding="utf-8"), "review-token command")
            self.assertIn("<the review write this invocation makes>", raw, name)
            for shell in SHELLS:
                with self.subTest(source=name, shell=shell):
                    result, calls, seen = self.token_run(shell, source, "printf %s app-token-xyz")
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    checks = [r for r in seen if "--silent" in r["args"]]
                    self.assertEqual([r["token"] for r in checks], ["app-token-xyz"],
                                     "the token is proved exactly once, under the app")
                    posted = [r for r in seen if "POST" in r["args"]]
                    self.assertEqual([r["token"] for r in posted], ["app-token-xyz"],
                                     "the write runs under the token the acquisition proved")
                    self.assertNotIn("app-token-xyz", json.dumps(calls), "a token never reaches argv")

    def test_the_other_publishers_write_nothing_without_a_usable_token(self):
        cases = (("printf %s ", 0, "prints nothing"), ("false unused-argument", 0, "exits non-zero"),
                 ("printf %s stale-token", 22, "the forge refuses the token"))
        for name, source in TOKEN_BLOCKS.items():
            for shell in SHELLS:
                for tok, silent_rc, reason in cases:
                    with self.subTest(source=name, shell=shell, tok=reason):
                        result, calls, seen = self.token_run(shell, source, tok, silent_rc)
                        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                        self.assertIn("no usable token", result.stdout)
                        self.assertIn("nothing was written", result.stdout)
                        self.assertEqual([call for call in calls if "POST" in call], [])
                        self.assertTrue(all(r["token"] != "authenticated-user-token" for r in seen),
                                        "the probe runs under the app token, never the user's")

    def dismissal(self, shell, tok="printf %s dismissal-token", why="superseded"):
        private = Path(tempfile.mkdtemp(dir=self.root))
        log = private / "gh.log"
        env = dict(os.environ, PATH=f"{self.gh_binary()}{os.pathsep}{os.environ['PATH']}", GH_LOG=str(log),
                   GH_TOKEN_LOG=str(private / "token.log"))
        env.pop("GH_TOKEN", None)
        text = (block(PUBLICATION.read_text(encoding="utf-8"), "dismissals")
                .replace("<review-token command>", tok)
                .replace("<pr>", "7").replace("<review id>", "2").replace("<why>", why))
        wrapped = "%s %s wrap --private-dir %s --event forge-written --data role=review -- %s" % (
            shlex.quote(sys.executable), shlex.quote(str(SCRIPTS / "run_events.py")),
            shlex.quote(str(private)), text.strip())
        result = self.sh(shell, wrapped, env=env, cwd=self.root)
        calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
        return result, calls, private

    def test_a_dismissal_without_a_token_writes_nothing_and_says_why(self):
        # `gh` reads an empty GH_TOKEN as no token at all, so falling through would dismiss
        # the app's review as the authenticated user. Each guard names its own route, so a
        # runner that failed is distinguishable from one that printed an empty token.
        cases = (("printf %s ", "prints nothing", "the review-token command printed no token"),
                 ("false unused-argument", "exits non-zero", "the review-token command failed"))
        for shell in SHELLS:
            for tok, reason, expected in cases:
                with self.subTest(shell=shell, tok=reason):
                    result, calls, _ = self.dismissal(shell, tok=tok)
                    self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                    self.assertEqual(calls, [])
                    self.assertIn(expected, result.stdout)
                    self.assertIn("nothing was dismissed", result.stdout)

    def test_the_dismissal_runs_wrapped_and_keeps_its_message_literal(self):
        why = 'superseded by the `id -un` review at $HOME, a \\ and a "quote" \u2014 done'
        for shell in SHELLS:
            with self.subTest(shell=shell):
                result, calls, private = self.dismissal(shell, why=why)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(len(calls), 1, calls)
                self.assertIn("message=" + why, calls[0], "the message reaches the forge unexpanded")
                self.assertNotIn("dismissal-token", json.dumps(calls), "a token never reaches argv")
                seen = [json.loads(line) for line in (private / "token.log").read_text(encoding="utf-8").splitlines()]
                self.assertEqual([r["token"] for r in seen], ["dismissal-token"])
                events = [json.loads(line) for line in
                          (private / "run-events.jsonl").read_text(encoding="utf-8").splitlines()]
                self.assertEqual([(e["event"], e["data"]["role"], e["data"]["argv0"], e["exit"]) for e in events],
                                 [("forge-written", "review", "sh", 0)])
                self.assertNotIn("dismissal-token", json.dumps(events))

    def test_preflight_failures_never_post(self):
        cases = [("fail", fixtures.HEAD, "head fetch exited 1"),
                 ("empty", fixtures.HEAD, "empty or malformed head"),
                 ("malformed", fixtures.HEAD, "empty or malformed head"),
                 ("short", fixtures.HEAD, "empty or malformed head"),
                 ("two-lines", fixtures.HEAD, "empty or malformed head"),
                 ("mismatch", fixtures.HEAD, "is not the reviewed head " + fixtures.HEAD),
                 ("match", "d" * 40, "batch.json commit_id is not the reviewed head")]
        for shell in SHELLS:
            for wrapped in (True, False):
                for mode, batch_head, reason in cases:
                    with self.subTest(shell=shell, wrapped=wrapped, mode=mode, batch=batch_head[:1]):
                        result, calls, events, private = self.submission(shell, mode, wrapped=wrapped,
                                                                         batch_head=batch_head)
                        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                        self.assertTrue(result.stdout.startswith("preflight failed: "), result.stdout)
                        self.assertIn(reason, result.stdout)
                        self.assertIn("nothing was written", result.stdout)
                        self.assertNotIn("write attempted", result.stdout)
                        self.assertEqual(self.posts(calls), [])
                        self.assertEqual(len(calls), 1)
                        self.assertFalse((private / "head.txt").exists())
                        self.assertFalse((private / "review-response.json").exists())
                        if mode == "fail":
                            self.assertIn("HTTP 404", result.stdout)
                        self.assertEqual([e["event"] for e in events], ["forge-fetched"] if wrapped else [])

    def test_matching_head_posts_once(self):
        for shell in SHELLS:
            for wrapped in (True, False):
                with self.subTest(shell=shell, wrapped=wrapped):
                    result, calls, events, private = self.submission(shell, wrapped=wrapped)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn(f"preflight passed: live head {fixtures.HEAD}", result.stdout)
                    self.assertIn('"id": 991', result.stdout)
                    self.assertEqual(calls[0], ["api", "repos/{owner}/{repo}/pulls/7", "--jq", ".head.sha"])
                    self.assertEqual(self.posts(calls), [["api", "--method", "POST", "repos/{owner}/{repo}/pulls/7/reviews",
                                                          "--input", str(private / "batch.json")]])
                    self.assertEqual((private / "head.txt").read_text(encoding="utf-8").strip(), fixtures.HEAD)
                    self.assertEqual(json.loads((private / "batch.json").read_text(encoding="utf-8"))["commit_id"],
                                     fixtures.HEAD)
                    if wrapped:
                        self.assertEqual([(e["event"], e["data"]["role"], e["exit"]) for e in events],
                                         [("forge-fetched", "root", 0), ("forge-written", "review", 0)])
                        self.assertEqual(events[0]["data"]["connection"], "root")
                    else:
                        self.assertEqual(events, [])

    def test_post_failures_keep_their_status_and_stage(self):
        for shell in SHELLS:
            for post_rc in (1, 3, 4):
                with self.subTest(shell=shell, post_rc=post_rc):
                    result, calls, events, private = self.submission(shell, post_rc=post_rc)
                    self.assertEqual(result.returncode, post_rc, result.stdout + result.stderr)
                    self.assertIn("preflight passed", result.stdout)
                    self.assertNotIn("preflight failed", result.stdout)
                    self.assertIn(f"write attempted: review POST exited {post_rc}", result.stdout)
                    self.assertIn("outcome unknown", result.stdout)
                    self.assertEqual(len(self.posts(calls)), 1, "an ambiguous write must not retry inside the block")
                    self.assertEqual([(e["event"], e["exit"]) for e in events],
                                     [("forge-fetched", 0), ("forge-written", post_rc)])

    def test_ambiguous_post_reconciliation_rereads_before_one_retry(self):
        # The block stops after an ambiguous POST; reconciliation reads before a single retry, and the retry
        # goes through the same block, so its fresh preflight runs before the second and final POST.
        result, calls, _, private = self.submission("sh", post_rc=1)
        self.assertEqual((result.returncode, len(self.posts(calls))), (1, 1))
        self.assertIn("re-read the pull request's reviews before one retry", result.stdout)
        self.assertTrue((private / "review-response.stderr").read_text(encoding="utf-8"))
        retry, calls, _, _ = self.submission("sh", post_rc=0)
        self.assertEqual(retry.returncode, 0, retry.stdout)
        self.assertEqual([("POST" in call) for call in calls], [False, True])
        stale, calls, _, _ = self.submission("sh", head_mode="mismatch")
        self.assertEqual((stale.returncode, self.posts(calls)), (3, []))


if __name__ == "__main__":
    try:
        unittest.main()
    except OSError as error:
        print(f"test_command_chains: cannot run a subprocess: {error}", file=sys.stderr)
        raise SystemExit(2)
