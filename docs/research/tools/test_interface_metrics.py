#!/usr/bin/env python3
"""Drive interface_metrics.py through its command line on synthetic transcripts and artifacts.

Usage: python3 docs/research/tools/test_interface_metrics.py [-v]
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "interface_metrics.py"
SKILL = "/opt/skills/review-code"


def assistant(request: str, at: str, tools: list = (), text: str = None) -> dict:
    content = [{"type": "tool_use", "id": tool_id, "name": name, "input": data} for tool_id, name, data in tools]
    if text:
        content.append({"type": "text", "text": text})
    return {"type": "assistant", "requestId": request, "timestamp": at, "effort": "high",
            "message": {"model": "claude-sonnet-5", "content": content,
                        "usage": {"input_tokens": 10, "cache_creation_input_tokens": 100,
                                  "cache_read_input_tokens": 1000, "output_tokens": 50,
                                  "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 100}}}}


def result(tool_id: str, at: str, text: str, error: bool = False) -> dict:
    return {"type": "user", "timestamp": at, "message": {"content": [
        {"type": "tool_result", "tool_use_id": tool_id, "content": text, "is_error": error}]}}


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, encoding="utf-8")


class Metrics(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="metrics-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.task = self.tmp / "task"
        (self.task / "work").mkdir(parents=True)
        (self.task / "review/addenda").mkdir(parents=True)

    def write(self, name: str, lines: list) -> Path:
        path = self.tmp / name
        path.write_text("".join(json.dumps(line) + "\n" for line in lines), encoding="utf-8")
        return path

    def composition(self) -> Path:
        path = self.task / "work/composition.json"
        path.write_text(json.dumps({
            "run": {"head": "a" * 40, "context": "c" * 64, "issues": ["x/y#1"], "coverage": "complete"},
            "summary": {"status": "Approved", "intent": "Add one two three."},
            "findings": [], "record": {"paths": {"store": "/s"}, "files": [{"path": "a.py", "state": "reviewed"}]}}),
            encoding="utf-8")
        return path

    def root_transcript(self, composition: Path) -> Path:
        t = "2026-09-22T10:00:{:02d}Z".format
        return self.write("root.jsonl", [
            assistant("r1", t(0), [("t1", "Read", {"file_path": f"{SKILL}/SKILL.md"})]),
            result("t1", t(1), "1\t# Review code\n2\tsix words in this entry point"),
            assistant("r2", t(2), [("t2", "Bash", {"command": f"S={SKILL}\npython3 \"$S/scripts/compose_review.py\" --example | head"})]),
            result("t2", t(3), "{\"run\": {}}"),
            assistant("r3", t(4), [("t3", "Bash", {"command": f"cd {SKILL}\nsed -n 1,40p scripts/compose_review.py"}),
                                   ("t4", "Bash", {"command": f"cat {SKILL}/references/rendering.md"})]),
            result("t3", t(5), "def main(): pass"),
            result("t4", t(5), "# Render and validate\nalpha beta"),
            assistant("r4", t(6), [("t5", "Write", {"file_path": str(composition), "content": "x" * 120})]),
            result("t5", t(7), "File created"),
            assistant("r5", t(8), [("t6", "Bash", {"command": f"python3 {SKILL}/scripts/finalize_review.py --store s p; echo \"exit=$?\""})]),
            result("t6", t(9), "compose failed with exit 1; later stages did not run:\nfindings[0]: x\nexit=1"),
            assistant("r6", t(10), [("t7", "Bash", {"command": f"python3 {SKILL}/scripts/finalize_review.py --store s p"})]),
            result("t7", t(12), "summary ok"),
            assistant("r7", t(20), [("t8", "Write", {"file_path": str(self.task / "work/report.md"), "content": "y" * 40})]),
            result("t8", t(21), "File created"),
            assistant("r8", t(30), [], text="Done."),
        ])

    def test_cell_measures_usage_validation_repairs_loads_and_fields(self):
        composition = self.composition()
        root = self.root_transcript(composition)
        (self.task / "work/fingerprint-input.json").write_text(json.dumps(
            {"pr": {"title": "main...x", "body": "msg"}, "specs": [{"identity": "s", "text": "t"}]}))
        bundle = self.task / "work/initial"
        bundle.mkdir()
        (bundle / "input.json").write_text(json.dumps({"run": {}, "batch": {}, "candidates": []}))
        (bundle / "manifest.json").write_text("{}")
        worker = self.write("agent-1.jsonl", [
            {"type": "user", "timestamp": "2026-09-22T10:00:13Z", "message": {"content": "Read the brief at /b/brief.md now."}},
            assistant("w1", "2026-09-22T10:00:14Z", [("u1", "Read", {"file_path": "/b/brief.md"})]),
            result("u1", "2026-09-22T10:00:15Z", "brief text here"),
            assistant("w2", "2026-09-22T10:00:16Z", [("u2", "Write", {"file_path": "/b/raw-return.json", "content": "{}"})]),
        ])
        (self.tmp / "stdout.json").write_text(json.dumps({"num_turns": 9, "duration_ms": 31000, "total_cost_usd": 0.5,
                                                          "subagent_stats": {"spawned": 1}, "permission_denials": []}))
        out = run("cell", "--transcript", str(root), "--worker", str(worker), "--skill-root", SKILL,
                  "--task-root", str(self.task), "--result", str(self.tmp / "stdout.json"))
        self.assertEqual(out.returncode, 0, out.stderr)
        report = json.loads(out.stdout)
        root_usage = report["usage"]["root"]["total"]
        self.assertEqual((root_usage["turns"], root_usage["tool_calls"], root_usage["cache_read"]), (8, 8, 8000))
        self.assertEqual(report["usage"]["all"]["turns"], 10)
        self.assertEqual(report["usage"]["root"]["transcripts"][0]["settings"]["efforts"], {"high": 8})
        self.assertEqual(report["harness"]["subagents_spawned"], 1)
        finalizer = report["finalizer"]
        self.assertEqual((finalizer["invocations"], finalizer["failed"], finalizer["repair_loops"]), (2, 1, 1))
        self.assertEqual(finalizer["validation"]["turns_after"], 2)
        self.assertEqual(finalizer["validation"]["tool_calls_after"], 1)
        self.assertEqual(finalizer["validation"]["seconds_after"], 18.0)
        totals = report["loads"]["totals"]
        self.assertEqual(totals["entrypoint"]["count"], 1)
        self.assertEqual(totals["helper-example"]["count"], 1)
        self.assertEqual(totals["script-source"]["count"], 1)
        self.assertEqual(totals["reference"], {"count": 1, "bytes": 32, "words": 6})
        self.assertNotIn("helper-help", totals)
        worker_loads = report["worker_loads"][0]
        self.assertEqual(worker_loads["totals"]["bundle"]["count"], 1)
        self.assertEqual(worker_loads["dispatch_prompt"]["words"], 6)
        by_class = report["authored"]["by_class"]
        self.assertEqual(by_class["composition"], {"writes": 1, "chars": 120})
        self.assertEqual(by_class["report"]["chars"], 40)
        self.assertEqual(by_class["raw-return"]["writes"], 1)
        fields = report["authored"]["fields"][0]
        self.assertEqual(fields["shape"], "composition")
        self.assertEqual(fields["mechanical"]["fields"], 5)
        self.assertEqual(fields["judgment"]["fields"], 5)
        self.assertEqual(fields["written_by"], "tool")
        unobserved = report["authored"]["fields"][1]
        self.assertEqual((unobserved["shape"], unobserved["written_by"]), ("fingerprint-input", "unobserved"))
        self.assertEqual((unobserved["mechanical"]["fields"], unobserved["judgment"]["fields"]), (4, 0))
        self.assertEqual(len(report["authored"]["fields"]), 2)
        self.assertEqual(report["after_last_addendum"]["status"], "unavailable")

    def test_continuation_without_finalizer_reports_the_addendum_tail(self):
        addendum = self.task / "review/addenda/addendum-x.json"
        addendum.write_text(json.dumps({"format": "implementation-gate-addendum/2", "workflow": "v5b-24",
                                        "reviewed_head": "a" * 40, "status": "Approved", "delta": [{"path": "a", "state": "reviewed"}]}))
        root = self.write("root.jsonl", [
            assistant("r1", "2026-09-22T10:00:00Z", [("t1", "Write", {"file_path": str(addendum), "content": "{}"})]),
            result("t1", "2026-09-22T10:00:01Z", "File created"),
            assistant("r2", "2026-09-22T10:00:05Z", [], text="Done."),
        ])
        out = run("cell", "--transcript", str(root), "--skill-root", SKILL, "--task-root", str(self.task))
        self.assertEqual(out.returncode, 0, out.stderr)
        report = json.loads(out.stdout)
        self.assertEqual(report["finalizer"]["validation"]["status"], "unavailable")
        self.assertEqual(report["after_last_addendum"]["turns_after"], 1)
        self.assertEqual(report["after_last_addendum"]["seconds_after"], 4.0)
        fields = report["authored"]["fields"][0]
        self.assertEqual(fields["shape"], "addendum")
        self.assertEqual((fields["mechanical"]["fields"], fields["judgment"]["fields"]), (4, 2))
        self.assertIsNone(report["usage"]["workers"])

    def test_fields_classifies_a_raw_return(self):
        path = self.tmp / "raw-return.json"
        path.write_text(json.dumps({"manifest_sha256": "f" * 64, "candidates": [
            {"id": "a", "verdict": "confirmed", "basis": "four words right here", "evidence": []}],
            "premises": [], "duplicate_groups": [], "observation": None}))
        out = run("fields", str(path))
        self.assertEqual(out.returncode, 0, out.stderr)
        inventory = json.loads(out.stdout)[0]
        self.assertEqual(inventory["shape"], "raw-return")
        self.assertEqual(inventory["mechanical"], {"fields": 1, "words": 1})
        self.assertEqual(inventory["judgment"]["words"], 6)

    def test_static_measures_instructions_helpers_and_sources(self):
        skill = self.tmp / "skill"
        (skill / "references").mkdir(parents=True)
        (skill / "scripts").mkdir()
        (skill / "SKILL.md").write_text("one two three\n", encoding="utf-8")
        (skill / "references/a.md").write_text("four five\n", encoding="utf-8")
        (skill / "references/b.md").write_text("six\n", encoding="utf-8")
        helper = "import sys\nprint('flags', *sys.argv[1:])\n"
        for name in ("review_context", "context_fingerprint", "compose_review", "build_verifier_prompt",
                     "account_verifier_return", "finalize_review", "forge_packet", "run_events"):
            (skill / f"scripts/{name}.py").write_text(helper, encoding="utf-8")
        (skill / "scripts/test_skip.py").write_text("ignored\n", encoding="utf-8")
        out = run("static", "--skill-root", str(skill))
        self.assertEqual(out.returncode, 0, out.stderr)
        report = json.loads(out.stdout)
        self.assertEqual(report["entrypoint"], {"bytes": 14, "words": 3})
        self.assertEqual(report["references"], {"count": 2, "bytes": 14, "words": 3})
        self.assertEqual(report["helper_output"]["compose_review.py --example --profile implementation-gate"]["words"], 4)
        self.assertNotIn("scripts/test_skip.py", report["script_sources"])
        (skill / "scripts/run_events.py").write_text("raise SystemExit(3)\n", encoding="utf-8")
        failed = run("static", "--skill-root", str(skill))
        self.assertEqual(failed.returncode, 2)
        self.assertIn("run_events.py --help exited 3", failed.stderr)

    def test_unreadable_input_exits_2(self):
        out = run("fields", str(self.tmp / "missing.json"))
        self.assertEqual(out.returncode, 2)
        self.assertIn("interface_metrics:", out.stderr)


if __name__ == "__main__":
    unittest.main()
