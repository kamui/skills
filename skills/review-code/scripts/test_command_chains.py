#!/usr/bin/env python3
"""Run the documented one-invocation command chains against local fixtures.

Usage: python3 scripts/test_command_chains.py
Inputs: output.md's `render_review.py` command, implement-publish's prior-record
continuation, record check and approval gate, the pull-request target's fetch
command, the publisher's freshness and review-submission block, its dismissal command,
a disposable Git repository, and a stub `gh` on PATH; no forge access and no live writes.
Exit 0: checks pass; 1: assertion failure; 2: a subprocess cannot run.

The finalize command, run in the reviewed repository, must write the record, the
payload and batch the composer produces for the derived composition, fill only
the record's own paths and the other derived fields the fixtures omit, and stop
visibly at a refused composition with nothing promoted. implement-publish's
continuation must finalize from its prior record and pass its documented record
check, which refuses another head and a sibling that forked from an earlier
record; its gate must withhold publication from a checked `Needs Information`
record and permit it only for an `Approved` one. The submission
block must never POST after a failed, empty, malformed,
or mismatched head, must exit 3 only on that preflight route, and must keep a
POST failure's own status under a distinct attempted-write stage. Every token
acquisition must publish its write under a proved token and write nothing when
the token is missing or refused; the dismissal, whose single write is its own
proof, must write nothing when the token is missing. Neither the token nor the
dismissal message may reach `argv` or the inner shell's expansions.
The fetch command must save the response and the packet and build no context;
a failed root query must stop it, and a failed continuation must stay visible
as a gap in an incomplete packet.
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
import render_review
import test_render_composition as fixtures

SCRIPTS = Path(__file__).resolve().parent
SKILL = SCRIPTS.parent
TARGET = SKILL / "references" / "targets.md"
PUBLICATION = SKILL.parent / "review-code-publish" / "references" / "publication.md"
SHELLS = [shell for shell in ("sh", "bash", "zsh", "dash") if shutil.which(shell)]

FAKE_GH = r"""#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
with open(os.environ["GH_LOG"], "a", encoding="utf-8") as log:
    log.write(json.dumps(args) + "\n")
if os.environ.get("GH_TOKEN_LOG"):
    with open(os.environ["GH_TOKEN_LOG"], "a", encoding="utf-8") as tokens:
        tokens.write(json.dumps({"args": args, "token": os.environ.get("GH_TOKEN")}) + "\n")
if "graphql" in args and any(arg.startswith("after=") for arg in args):  # a continuation query
    sys.stderr.write("gh: HTTP 502: Bad Gateway\n")
    sys.exit(1)
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

IMPLEMENT = SKILL.parent / "implement-publish" / "SKILL.md"
GATE = ["status Approved", "coverage complete"]


def command(text: str) -> str:
    found = re.findall(r"^(python3 scripts/render_review\.py .+)$", text, re.MULTILINE)
    assert len(found) == 1, found
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
        self.repo = repo
        return repo, base, git("rev-parse", "HEAD")

    def record(self, head):
        return {"repository": str(self.repo), "requirements": [],
                "files": [{"path": p, "state": "reviewed"} for p in ("src/payments.ts", "src/retry-policy.ts", "src/queue.ts")],
                "check_evidence": [], "verification": {"tasks": [], "batches": [], "outstanding": []},
                "routed": {"unresolved": ["queue/retry-order"], "disputed": [], "unrecoverable_inputs": []}}

    def compositions(self, base, head):
        """A range and a pull-request composition, each with the private accounting finalization requires; the run
        identity the store owns and the record's own paths are left for the finalizer to derive."""
        full = fixtures.base_composition()
        full["run"].update(base_sha=base, target_kind="range", target="main..HEAD", change_description="change")
        for key in ("repository_url", "packet_context", "head", "merge_base"):
            full["run"].pop(key)
        linked = fixtures.base_composition()
        linked["run"].update(base_sha=base)
        for key in ("head", "merge_base"):
            linked["run"].pop(key)
        for value in (full, linked):
            value["findings"] = []
            value["summary"]["status"] = "Needs Information"
            value["record"] = self.record(head)
        return {"range fixture": full, "pull-request fixture": linked}

    def private(self, repo, base, head, name):
        private = self.root / name
        private.mkdir()
        store = private / f"review-context-{head}.json"
        subprocess.run([sys.executable, str(SCRIPTS / "review_context.py"), "--merge-base", base, "--head", head,
                        "--store", str(store)], cwd=repo, capture_output=True, check=True)
        return private, store

    def documented(self, private, store, extra=""):
        """The single documented finalize line, run in the reviewed repository with this skill's absolute script path."""
        text = command((SKILL / "references" / "output.md").read_text(encoding="utf-8"))
        text = (text.replace("scripts/render_review.py", shlex.quote(str(SCRIPTS / "render_review.py")))
                .replace("<private-dir>", shlex.quote(str(private))).replace("<store>", shlex.quote(str(store))))
        return text.replace(" --store ", f" {extra} --store ", 1) if extra else text

    def test_composition_chain_matches_the_composer(self):
        repo, base, head = self.repository()
        for name, composition in self.compositions(base, head).items():
            for shell in SHELLS:
                with self.subTest(fixture=name, shell=shell):
                    private, store = self.private(repo, base, head, f"{name}-{shell}".replace(" ", "-"))
                    path = private / "composition.json"
                    path.write_text(json.dumps(composition), encoding="utf-8")
                    result = self.sh(shell, self.documented(private, store), cwd=repo)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(json.loads(path.read_text(encoding="utf-8")), composition, "the composition stays as written")
                    record = json.loads((private / "record.json").read_text(encoding="utf-8"))
                    self.assertEqual(record["finalization"]["report"], str(private / "report.md"))
                    self.assertEqual(record["record"]["paths"], {"private_dir": str(private), "store": str(store),
                                                                 "composition": str(private / "composition.json"),
                                                                 "skill_root": str(SKILL)})
                    derived = json.loads(json.dumps(composition))
                    derived["run"].update(head=head, merge_base=base, supplied_inputs="no")
                    if derived["run"].get("target_kind") == "range":
                        derived["run"]["merged"] = False
                    derived["record"]["paths"] = record["record"]["paths"]
                    derived["record"]["verification"]["allowance"] = {"initial_spent": False, "follow_up_spent": False}
                    store_doc = json.loads(store.read_text(encoding="utf-8"))
                    payload, violations = render_review.compose(derived, store_doc)
                    self.assertEqual(violations, [])
                    self.assertEqual(json.loads((private / "payload.json").read_text(encoding="utf-8")), payload)
                    self.assertEqual(json.loads((private / "batch.json").read_text(encoding="utf-8")), render_review.emit_batch(payload))
                    checked = subprocess.run([sys.executable, str(SCRIPTS / "render_review.py"), "--check", str(private)],
                                             capture_output=True, text=True, encoding="utf-8")
                    self.assertEqual((checked.returncode, checked.stdout), (0, result.stdout))
                    self.assertTrue(result.stdout.endswith(f"report {private}/report.md\n"), result.stdout)
                    self.assertEqual(sorted(p.name for p in private.glob("*.part")), [])

    def test_composition_failure_is_visible_and_stops(self):
        repo, base, head = self.repository()
        composition = self.compositions(base, head)["range fixture"]
        composition["findings"] = [fixtures.finding(priority="P0", action="consider")]
        for shell in SHELLS:
            with self.subTest(shell=shell):
                private, store = self.private(repo, base, head, f"refused-{shell}")
                (private / "composition.json").write_text(json.dumps(composition), encoding="utf-8")
                for stale in ("record.json", "payload.json", "batch.json", "fragments.md", "report.md"):
                    (private / stale).write_text("stale success\n", encoding="utf-8")
                result = self.sh(shell, self.documented(private, store), cwd=repo)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("compose failed with exit 1; later stages did not run:", result.stdout)
                self.assertRegex(result.stdout, r"findings\[0\]")
                for artifact in ("record.json", "payload.json", "batch.json", "fragments.md", "report.md", "payload.json.part"):
                    self.assertFalse((private / artifact).exists(), artifact)
        private, store = self.private(repo, base, head, "unreadable")
        result = self.sh("sh", self.documented(private, store), cwd=repo)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("derive failed with exit 2", result.stdout)
        self.assertIn("cannot read composition", result.stdout)

    # --- implement-publish: continuation, record check and approval gate ------

    def test_implement_publish_publishes_only_an_approved_record_of_its_chain(self):
        repo, base, first = self.repository()

        def commit(prefix):
            (repo / "src" / "queue.ts").write_text("\n".join(f"{prefix} {i}" for i in range(1, 11)) + "\n", encoding="utf-8")
            subprocess.run(["git", "commit", "-qam", prefix], cwd=repo, check=True, capture_output=True)
            return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()

        second = commit("fixed")
        skill = IMPLEMENT.read_text(encoding="utf-8")
        self.assertIn("Supply the latest accepted record as `prior_record`", skill)
        for line in GATE:
            self.assertIn(f"`{line}`", skill)
        self.assertIn("`Needs Information`, `Changes Requested`, and `Incomplete` all withhold publication", skill)
        check = block(skill, "render_review.py --check").strip()
        composition = self.compositions(base, first)["range fixture"]
        composition["record"]["routed"]["unresolved"] = []
        still_open = {"id": "queue/retry-order", "classification": "still-open", "action": "question",
                      "note": "Still unanswered at the final head."}
        answered = {"id": "queue/retry-order", "classification": "obsolete", "action": "question",
                    "note": "The maintainer confirmed that retry order is outside the contract."}
        records = {}
        # R3 continues R2 at an unchanged head: an answer, with no code change, is what settles the question.
        for name, head, prior, item in (("r1", first, None, None), ("r2", second, "r1", still_open),
                                        ("sibling", second, "r1", answered), ("r3", second, "r2", answered)):
            private, store = self.private(repo, base, head, name)
            value = json.loads(json.dumps(composition))
            if item is not None:
                value["prior_items"] = [item]
            if item is answered:
                value["questions"] = []
                value["summary"]["status"] = "Approved"
            (private / "composition.json").write_text(json.dumps(value), encoding="utf-8")
            extra = f"--prior-record {shlex.quote(str(records[prior]))}" if prior else ""
            result = self.sh("sh", self.documented(private, store, extra), cwd=repo)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            records[name] = private / "record.json"

        def run_check(head, record, *accepted):
            text = (check.replace("<skill root>", shlex.quote(str(SKILL))).replace("<committed head>", head)
                    .replace("--lineage <each accepted record>", " ".join(f"--lineage {shlex.quote(str(r))}" for r in accepted))
                    .replace("<candidate record>", shlex.quote(str(record))).replace("<private-dir>", shlex.quote(str(record.parent))))
            self.assertNotRegex(text, r"<[a-z][^>]*>")
            return self.sh("sh", text, cwd=repo)

        def publishable(result):
            return result.returncode == 0 and result.stdout.splitlines()[:2] == GATE

        opened = run_check(first, records["r1"])
        self.assertEqual((opened.returncode, opened.stdout.splitlines()[0]), (0, "status Needs Information"), opened.stdout)
        self.assertFalse(publishable(opened), "an unanswered question is not approval")
        moved = run_check(second, records["r1"])
        self.assertEqual(moved.returncode, 1, moved.stdout)
        self.assertIn(f"reviews head `{first}`, not `{second}`", moved.stdout)

        continued = run_check(second, records["r2"], records["r1"])
        self.assertEqual((continued.returncode, continued.stdout.splitlines()[0]), (0, "status Needs Information"), continued.stdout)
        self.assertEqual(json.loads(records["r2"].read_text(encoding="utf-8"))["lineage"], [str(records["r1"])])
        self.assertFalse(publishable(continued), "a usable record at the final head is still not approval")

        # Once R2 is accepted, a sibling that continued R1 again does not descend from it, whatever its status.
        self.assertTrue(publishable(run_check(second, records["sibling"], records["r1"])), "the sibling approves on R1 alone")
        forked = run_check(second, records["sibling"], records["r1"], records["r2"])
        self.assertEqual(forked.returncode, 1, forked.stdout)
        self.assertIn(f"does not descend from `{records['r2']}`", forked.stdout)

        approved = run_check(second, records["r3"], records["r1"], records["r2"])
        self.assertEqual(approved.stdout.splitlines()[:2], GATE, approved.stdout)
        self.assertTrue(publishable(approved))
        later = run_check(commit("later"), records["r3"], records["r1"], records["r2"])
        self.assertEqual(later.returncode, 1, "an approval never carries to a later commit: " + later.stdout)

    # --- pull-request fetch -------------------------------------------------

    def fetch(self, shell, page, root_rc=0):
        private = Path(tempfile.mkdtemp(dir=self.root))
        root = private.parent / f"{private.name}-page.json"
        root.write_text(json.dumps(page), encoding="utf-8")
        env = dict(os.environ, PATH=f"{self.gh_binary()}{os.pathsep}{os.environ['PATH']}", GH_LOG=str(private.parent / f"{private.name}-gh.log"),
                   GH_ROOT_FILE=str(root), GH_ROOT_RC=str(root_rc))
        found = re.findall(r"^python3 scripts/forge_packet\.py fetch .+$", block(TARGET.read_text(encoding="utf-8"), "forge_packet.py fetch"),
                           re.MULTILINE)
        self.assertEqual(len(found), 1, found)
        text = (found[0].replace(" [--issue <reference> ...]", "")
                .replace("scripts/forge_packet.py", shlex.quote(str(SCRIPTS / "forge_packet.py")))
                .replace("<owner>/<repo>", "acme/payments").replace("<pr>", "7")
                .replace("<private-dir>", shlex.quote(str(private))))
        self.assertNotRegex(text, r"<[a-z][^>]*>")
        result = self.sh(shell, text, env=env, cwd=self.root)
        return result, private

    @staticmethod
    def packet(private):
        return json.loads((private / "packet.json").read_text(encoding="utf-8"))

    def test_fetch_saves_the_response_and_packet_and_builds_no_context(self):
        page = forge_packet.sample_root()
        for shell in SHELLS:
            with self.subTest(shell=shell):
                result, private = self.fetch(shell, page)
                self.assertEqual((result.returncode, result.stdout, result.stderr),
                                 (0, f"packet {private}/packet.json: complete, 1 responses\n", ""))
                self.assertEqual((private / "forge-1.json").read_text(encoding="utf-8"), json.dumps(page))
                self.assertEqual(sorted(p.name for p in private.iterdir()), ["fetch.json", "forge-1.json", "packet.json"],
                                 "step 2 is the one build point")
                self.assertTrue(self.packet(private)["complete"])

    def test_fetch_keeps_failures_and_gaps_visible(self):
        for shell in SHELLS:
            with self.subTest(case="root query failure", shell=shell):
                result, private = self.fetch(shell, forge_packet.sample_root(), root_rc=1)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("HTTP 502", result.stderr)
                self.assertIn("no root page", result.stderr)
                self.assertTrue((private / "forge-1.json").exists(), "a failed call is saved too")
                self.assertFalse((private / "packet.json").exists())
        page = forge_packet.sample_root()
        pr = page["data"]["repository"]["pullRequest"]
        pr["reviews"] = forge_packet.connection(pr["reviews"]["nodes"], len(pr["reviews"]["nodes"]) + 1, True)
        with self.subTest(case="failed continuation"):
            result, private = self.fetch("sh", page)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(": incomplete, 2 responses\n", result.stdout)
            self.assertIn("continuation reviews", result.stderr)
            packet = self.packet(private)
            self.assertFalse(packet["complete"])
            self.assertTrue(any(gap.startswith("reviews: ") for gap in packet["gaps"]), packet["gaps"])
            self.assertTrue(all(f"gap {gap}" in result.stdout.splitlines() for gap in packet["gaps"]))

    # --- publisher freshness and submission ---------------------------------

    def gh_binary(self):
        binary = self.root / "gh-bin"
        if not binary.exists():
            binary.mkdir()
            (binary / "gh").write_text(FAKE_GH, encoding="utf-8")
            (binary / "gh").chmod(0o755)
        return binary

    def submission(self, shell, head_mode="match", post_rc=0, batch_head=fixtures.HEAD, tok="", silent_rc=0):
        private = Path(tempfile.mkdtemp(dir=self.root))
        (private / "batch.json").write_text(json.dumps({"commit_id": batch_head, "event": "COMMENT", "body": "b",
                                                        "comments": []}), encoding="utf-8")
        binary = self.gh_binary()
        log = private / "gh.log"
        env = dict(os.environ, PATH=f"{binary}{os.pathsep}{os.environ['PATH']}", GH_LOG=str(log),
                   GH_HEAD=fixtures.HEAD, GH_HEAD_MODE=head_mode, GH_POST_RC=str(post_rc),
                   GH_TOKEN_LOG=str(private / "token.log"), GH_SILENT_RC=str(silent_rc))
        env.pop("GH_TOKEN", None)  # only the block's own acquisition may supply one
        text = (block(PUBLICATION.read_text(encoding="utf-8"), "preflight failed")
                .replace("<private-dir>", shlex.quote(str(private)))
                .replace("<pr>", "7").replace("<reviewed head>", fixtures.HEAD))
        if tok:  # the block assigns `tok=` empty; a reviewing app fills it in
            marker = "tok=  #"
            self.assertIn(marker, text)
            text = text.replace(marker, "tok=%s  #" % shlex.quote(tok), 1)
        self.assertNotRegex(text.split("\n", 1)[0], r"<[a-z][^>]*>")
        result = self.sh(shell, text, env=env, cwd=self.root)
        calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
        return result, calls, private

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
                result, calls, private = self.submission(shell, tok="printf %s app-token-xyz")
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
                    result, calls, private = self.submission(shell, tok=tok, silent_rc=silent_rc)
                    self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                    self.assertIn("preflight failed: the review-token command", result.stdout)
                    self.assertIn("nothing was written", result.stdout)
                    self.assertNotIn("write attempted", result.stdout)
                    self.assertEqual(self.posts(calls), [])
                    self.assertFalse((private / "review-response.json").exists())

    def dismissal(self, shell, tok="printf %s dismissal-token", why="superseded"):
        private = Path(tempfile.mkdtemp(dir=self.root))
        log = private / "gh.log"
        env = dict(os.environ, PATH=f"{self.gh_binary()}{os.pathsep}{os.environ['PATH']}", GH_LOG=str(log),
                   GH_TOKEN_LOG=str(private / "token.log"))
        env.pop("GH_TOKEN", None)
        text = (block(PUBLICATION.read_text(encoding="utf-8"), "dismissals")
                .replace("<review-token command>", tok)
                .replace("<pr>", "7").replace("<review id>", "2").replace("<why>", why))
        result = self.sh(shell, text.strip(), env=env, cwd=self.root)
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

    def test_the_dismissal_keeps_its_message_literal(self):
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

    def test_preflight_failures_never_post(self):
        cases = [("fail", fixtures.HEAD, "head fetch exited 1"),
                 ("empty", fixtures.HEAD, "empty or malformed head"),
                 ("malformed", fixtures.HEAD, "empty or malformed head"),
                 ("short", fixtures.HEAD, "empty or malformed head"),
                 ("two-lines", fixtures.HEAD, "empty or malformed head"),
                 ("mismatch", fixtures.HEAD, "is not the reviewed head " + fixtures.HEAD),
                 ("match", "d" * 40, "batch.json commit_id is not the reviewed head")]
        for shell in SHELLS:
            for mode, batch_head, reason in cases:
                with self.subTest(shell=shell, mode=mode, batch=batch_head[:1]):
                    result, calls, private = self.submission(shell, mode, batch_head=batch_head)
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

    def test_matching_head_posts_once(self):
        for shell in SHELLS:
            with self.subTest(shell=shell):
                result, calls, private = self.submission(shell)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(f"preflight passed: live head {fixtures.HEAD}", result.stdout)
                self.assertIn('"id": 991', result.stdout)
                self.assertEqual(calls[0], ["api", "repos/{owner}/{repo}/pulls/7", "--jq", ".head.sha"])
                self.assertEqual(self.posts(calls), [["api", "--method", "POST", "repos/{owner}/{repo}/pulls/7/reviews",
                                                      "--input", str(private / "batch.json")]])
                self.assertEqual((private / "head.txt").read_text(encoding="utf-8").strip(), fixtures.HEAD)
                self.assertEqual(json.loads((private / "batch.json").read_text(encoding="utf-8"))["commit_id"],
                                 fixtures.HEAD)

    def test_post_failures_keep_their_status_and_stage(self):
        for shell in SHELLS:
            for post_rc in (1, 3, 4):
                with self.subTest(shell=shell, post_rc=post_rc):
                    result, calls, private = self.submission(shell, post_rc=post_rc)
                    self.assertEqual(result.returncode, post_rc, result.stdout + result.stderr)
                    self.assertIn("preflight passed", result.stdout)
                    self.assertNotIn("preflight failed", result.stdout)
                    self.assertIn(f"write attempted: review POST exited {post_rc}", result.stdout)
                    self.assertIn("outcome unknown", result.stdout)
                    self.assertEqual(len(self.posts(calls)), 1, "an ambiguous write must not retry inside the block")

    def test_ambiguous_post_reconciliation_rereads_before_one_retry(self):
        # The block stops after an ambiguous POST; reconciliation reads before a single retry, and the retry
        # goes through the same block, so its fresh preflight runs before the second and final POST.
        result, calls, private = self.submission("sh", post_rc=1)
        self.assertEqual((result.returncode, len(self.posts(calls))), (1, 1))
        self.assertIn("re-read the pull request's reviews before one retry", result.stdout)
        self.assertTrue((private / "review-response.stderr").read_text(encoding="utf-8"))
        retry, calls, _ = self.submission("sh", post_rc=0)
        self.assertEqual(retry.returncode, 0, retry.stdout)
        self.assertEqual([("POST" in call) for call in calls], [False, True])
        stale, calls, _ = self.submission("sh", head_mode="mismatch")
        self.assertEqual((stale.returncode, self.posts(calls)), (3, []))


if __name__ == "__main__":
    try:
        unittest.main()
    except OSError as error:
        print(f"test_command_chains: cannot run a subprocess: {error}", file=sys.stderr)
        raise SystemExit(2)
