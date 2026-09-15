#!/usr/bin/env python3
"""Run the documented check-runs read against offline fixtures and a stub `gh`.

Usage: python3 scripts/test_check_runs.py [-v]
Inputs: the Reading check runs block in resolve-review's
`references/addressing-protocol.md`, code-review-publish's peer copy of the
shared reply vocabulary, and a stub `gh` on PATH that returns fixture pages;
no forge access.
Exit 0: checks pass; 1: assertion failure; 2: a subprocess cannot run.

The block must read every page for one full head SHA, retain each run's
identity, head, status, conclusion, and evidence URL, and write its result
only for a complete read. A failed page, a short or shifting read, malformed
output, or an abbreviated SHA must never leave a result file behind.
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
RESOLVE = SKILLS / "resolve-review"
ADDRESSING = RESOLVE / "references" / "addressing-protocol.md"
PEER = SKILLS / "code-review-publish" / "references" / "review-protocol.md"
SHELLS = [shell for shell in ("sh", "bash", "zsh", "dash") if shutil.which(shell)]
SHA = "a" * 40
OTHER = "b" * 40

FAKE_GH = r"""#!/usr/bin/env python3
import json, os, sys
with open(os.environ["GH_LOG"], "a", encoding="utf-8") as log:
    log.write(json.dumps(sys.argv[1:]) + "\n")
with open(os.environ["GH_FIXTURE"], encoding="utf-8") as f:
    fixture = json.load(f)
sys.stdout.write(fixture["stdout"])
sys.stderr.write(fixture.get("stderr", ""))
sys.exit(fixture.get("rc", 0))
"""


def block() -> str:
    found = [b for b in re.findall(r"```sh\n(.*?)```", ADDRESSING.read_text(encoding="utf-8"), re.S)
             if "check_runs.py" in b]
    assert len(found) == 1, len(found)
    return found[0]


def run(ident, name, conclusion="success", status="completed", head=SHA, app="github-actions", workflow=77):
    details = f"https://github.test/o/r/actions/runs/{workflow}/job/{ident}" if workflow else "https://ci.test/x"
    return {"id": ident, "name": name, "head_sha": head, "status": status, "conclusion": conclusion,
            "app": {"slug": app}, "check_suite": {"id": 500}, "details_url": details,
            "html_url": f"https://github.test/o/r/runs/{ident}"}


def pages(*chunks, total=None):
    count = sum(len(c) for c in chunks) if total is None else total
    return json.dumps([{"total_count": count, "check_runs": list(c)} for c in chunks])


class CheckRuns(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "bin").mkdir()
        (self.root / "bin" / "gh").write_text(FAKE_GH, encoding="utf-8")
        (self.root / "bin" / "gh").chmod(0o755)
        self.count = 0

    def tearDown(self):
        self.temp.cleanup()

    def read(self, stdout, rc=0, stderr="", sha=SHA, shell="sh", private=None):
        if private is None:
            self.count += 1
            private = self.root / f"private {self.count}"  # a space checks quoting
            private.mkdir()
        fixture = self.root / f"fixture-{self.count}.json"
        fixture.write_text(json.dumps({"stdout": stdout, "rc": rc, "stderr": stderr}), encoding="utf-8")
        log = private / "gh.log"
        text = block().replace("<private-dir>", shlex.quote(str(private))).replace("<sha>", shlex.quote(sha))
        env = dict(os.environ, PATH=f"{self.root / 'bin'}{os.pathsep}{os.environ['PATH']}",
                   GH_FIXTURE=str(fixture), GH_LOG=str(log))
        result = subprocess.run([shell, "-c", text], cwd=private, env=env, capture_output=True, text=True,
                                encoding="utf-8", timeout=60)
        calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
        out = private / f"check-runs.{sha}.json"
        return result, calls, (json.loads(out.read_text(encoding="utf-8")) if out.exists() else None), private

    def test_complete_paginated_read_retains_identity(self):
        fixture = pages([run(1, "unit (py3.9)"), run(2, "lint", workflow=None, app="other-ci")],
                        [run(3, "unit (py3.12)", conclusion=None, status="in_progress"),
                         run(4, "docs", conclusion="skipped")])
        for shell in SHELLS:
            with self.subTest(shell=shell):
                result, calls, doc, private = self.read(fixture, shell=shell)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(len(calls), 1)
                args = calls[0]
                for token in ("--paginate", "--slurp", f"repos/{{owner}}/{{repo}}/commits/{SHA}/check-runs",
                              "per_page=100", "filter=latest"):
                    self.assertIn(token, args)
                self.assertEqual((doc["requested_sha"], doc["total_count"]), (SHA, 4))
                self.assertEqual([r["id"] for r in doc["check_runs"]], [1, 2, 3, 4])
                first, lint, live, skipped = doc["check_runs"]
                self.assertEqual(first, dict(id=1, name="unit (py3.9)", head_sha=SHA, at_requested_head=True,
                                             app="github-actions", check_suite_id=500, workflow_run_id=77,
                                             status="completed", conclusion="success",
                                             url="https://github.test/o/r/runs/1"))
                self.assertEqual((lint["app"], lint["workflow_run_id"]), ("other-ci", None))
                self.assertEqual((live["status"], live["conclusion"]), ("in_progress", None))
                self.assertEqual(skipped["conclusion"], "skipped")
                lines = result.stdout.strip().splitlines()
                self.assertEqual(lines[0], 'success "unit (py3.9)" id=1 app=github-actions workflow_run=77 '
                                           "https://github.test/o/r/runs/1")
                self.assertTrue(lines[2].startswith('in_progress "unit (py3.12)" id=3'))
                self.assertEqual(lines[-1], f"complete {private}/check-runs.{SHA}.json")
                self.assertEqual((private / f"check-runs.{SHA}.status").read_text(encoding="utf-8").strip(), "0")

    def test_other_head_run_is_flagged(self):
        result, _, doc, _ = self.read(pages([run(1, "unit"), run(2, "unit", head=OTHER)]))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual([r["at_requested_head"] for r in doc["check_runs"]], [True, False])
        self.assertIn('other-head success "unit" id=2', result.stdout)

    def test_empty_head_is_complete_with_no_runs(self):
        result, _, doc, _ = self.read(json.dumps([{"total_count": 0, "check_runs": []}]))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual((doc["total_count"], doc["check_runs"]), (0, []))

    def test_incomplete_reads_leave_no_result(self):
        cases = {
            "gh exited 1": dict(stdout=pages([run(1, "unit")]), rc=1, stderr="gh: HTTP 502 Bad Gateway\n"),
            "2 of 3 check runs read": dict(stdout=pages([run(1, "unit")], [run(2, "lint")], total=3)),
            "total_count changed during the read": dict(stdout=json.dumps(
                [{"total_count": 2, "check_runs": [run(1, "unit")]}, {"total_count": 3, "check_runs": [run(2, "l")]}])),
            "check run 1 changed during the read": dict(stdout=pages([run(1, "unit", status="in_progress",
                                                                          conclusion=None)], [run(1, "unit")])),
            "malformed JSON": dict(stdout="[{\"total_count\": 1,"),
            "expected a non-empty array of pages": dict(stdout="[]"),
            "page without total_count and check_runs": dict(stdout=json.dumps([{"message": "Not Found"}])),
            "check run without an integer id": dict(stdout=json.dumps([{"total_count": 1, "check_runs": [{}]}])),
        }
        for reason, case in cases.items():
            for shell in SHELLS:
                with self.subTest(reason=reason, shell=shell):
                    result, _, doc, _ = self.read(shell=shell, **case)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn(f"incomplete check-runs {SHA}: {reason}", result.stdout)
                    self.assertNotIn("complete /", result.stdout)
                    self.assertIsNone(doc)

    def test_identical_repeat_collapses_but_short_count_stays_incomplete(self):
        result, _, doc, _ = self.read(pages([run(1, "unit")], [run(1, "unit")], total=2))
        self.assertEqual(result.returncode, 1)
        self.assertIn("1 of 2 check runs read", result.stdout)
        self.assertIsNone(doc)

    def test_incomplete_rerun_removes_an_earlier_result(self):
        _, _, doc, private = self.read(pages([run(1, "unit")]))
        self.assertIsNotNone(doc)
        result, _, doc, _ = self.read("", rc=1, private=private)
        self.assertEqual(result.returncode, 1)
        self.assertIsNone(doc)

    def test_abbreviated_or_invalid_sha_is_refused_before_gh(self):
        for sha in ("a" * 7, "A" * 40, "g" * 40, "a" * 41, ""):
            for shell in SHELLS:
                with self.subTest(sha=sha, shell=shell):
                    result, calls, doc, _ = self.read(pages([run(1, "unit")]), sha=sha, shell=shell)
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertIn("check runs need a full 40-hex head SHA", result.stdout)
                    self.assertEqual((calls, doc), ([], None))

    def test_skill_steps_use_the_evidence_rules(self):
        skill = (RESOLVE / "SKILL.md").read_text(encoding="utf-8")
        protocol = ADDRESSING.read_text(encoding="utf-8")
        for heading in ("**Selecting.**", "**Reusing.**", "**Invalidating.**", "**CI.**", "**Reporting.**",
                        "### Reading check runs"):
            self.assertEqual(protocol.count(heading), 1, heading)
        self.assertIn("under the protocol's Check evidence section", skill)
        self.assertIn("the protocol's Invalidating rule", skill)
        self.assertIn("each check with the head and input state it establishes", skill)
        for stale in ("run the relevant checks", "rerun affected checks", "and the checks run.", "`pnpm test` green."):
            self.assertNotIn(stale, skill + protocol + PEER.read_text(encoding="utf-8"))

    def test_shared_reply_vocabulary_lands_in_both_protocol_copies(self):
        protocol = ADDRESSING.read_text(encoding="utf-8")
        peer = PEER.read_text(encoding="utf-8")
        for shared in ("**Implemented** in `9f1e0aa` — extracted `assertOrderShape`; both call sites use it. "
                       "`pnpm test` green at `9f1e0aa`.",
                       "| `implemented` | change made | what changed, the check and the head it passed at, the commit |",
                       "`pnpm test` green at `5844a3c`. Every other thread resolved."):
            for name, text in (("addressing-protocol.md", protocol), ("review-protocol.md", peer)):
                self.assertIn(shared, text, name)
        self.assertIn("- each check with the head and input state it establishes, any failure that decides the "
                      "outcome, and any remaining verification gap;", peer)
        self.assertNotIn("Check evidence", peer)


if __name__ == "__main__":
    unittest.main(verbosity=2 if "-v" in sys.argv else 1, argv=[sys.argv[0]])
