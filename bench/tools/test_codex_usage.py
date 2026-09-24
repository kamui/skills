#!/usr/bin/env python3
"""Exercise codex_usage.py through its CLI.

Usage: python3 bench/tools/test_codex_usage.py
Inputs: temporary synthetic Codex rollout JSONL files.
Exit codes: 0 all checks pass; 1 a test fails.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("codex_usage.py")


def usage_line(response, inp, cached, write, out, reasoning=0, stamp="2026-09-24T00:00:04Z"):
    return {"timestamp": stamp, "type": "token_usage_record", "payload": {
        "response_id": response, "turn_id": "t1", "usage": {
            "input_tokens": inp, "cached_input_tokens": cached, "cache_write_input_tokens": write,
            "output_tokens": out, "reasoning_output_tokens": reasoning}}}


class CodexUsageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.sessions = Path(self.temp.name) / "sessions" / "2026" / "09" / "24"
        self.sessions.mkdir(parents=True)
        self.write("rollout-2026-09-24T00-00-00-root.jsonl", [
            {"timestamp": "2026-09-24T00:00:00Z", "type": "session_meta", "payload": {"id": "root"}}])
        self.child = self.write("rollout-2026-09-24T00-00-01-child.jsonl", [
            {"timestamp": "2026-09-24T00:00:01Z", "type": "session_meta",
             "payload": {"id": "child", "parent_thread_id": "root"}},
            {"timestamp": "2026-09-24T00:00:02Z", "type": "turn_context", "payload": {"model": "m"}},
            {"timestamp": "2026-09-24T00:00:03Z", "type": "response_item", "payload": {"type": "custom_tool_call"}},
            usage_line("r1", 1000, 400, 100, 50, 10),
            usage_line("r2", 2000, 1500, 0, 30, stamp="2026-09-24T00:01:04Z"),
        ])

    def write(self, name, records) -> Path:
        path = self.sessions / name
        path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        return path

    def run_cli(self, *args) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True, encoding="utf-8")

    def test_session_gather_prices_partitioned_input(self) -> None:
        result = self.run_cli("--sessions-dir", self.sessions.parent.parent.parent, "--session", "root",
                              "--prices", "10,50", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        total = json.loads(result.stdout)["total"]
        self.assertEqual((total["turns"], total["tool_calls"], total["text_only_turns"]), (2, 1, 1))
        self.assertEqual((total["input"], total["cache_read"], total["cache_write"]), (1000, 1900, 100))
        self.assertAlmostEqual(total["cost"], (1000 * 10 + 1900 * 1 + 100 * 12.5 + 80 * 50) / 1e6)

    def test_row_matches_header_columns(self) -> None:
        header = self.run_cli("--header").stdout.splitlines()[0]
        row = self.run_cli(self.child, "--prices", "10,50", "--row", "x").stdout.strip()
        self.assertEqual(header.count("|"), row.count("|"))

    def test_malformed_line_exits_2_with_coordinates(self) -> None:
        broken = self.sessions / "rollout-2026-09-24T00-00-02-broken.jsonl"
        broken.write_text(self.child.read_text(encoding="utf-8") + "{not json\n", encoding="utf-8")
        result = self.run_cli(broken, "--prices", "10,50")
        self.assertEqual(result.returncode, 2)
        self.assertIn(f"{broken}:6:", result.stderr)

    def test_non_object_line_exits_2(self) -> None:
        path = self.write("rollout-2026-09-24T00-00-05-list.jsonl", [[]])
        result = self.run_cli(path, "--prices", "10,50")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not an object", result.stderr)

    def test_inconsistent_usage_exits_2(self) -> None:
        path = self.write("rollout-2026-09-24T00-00-06-bad.jsonl", [usage_line("r", 10, 8, 8, 1)])
        result = self.run_cli(path, "--prices", "10,50")
        self.assertEqual(result.returncode, 2)
        self.assertIn("above input_tokens", result.stderr)

    def test_no_usage_exits_1(self) -> None:
        result = self.run_cli(self.sessions / "rollout-2026-09-24T00-00-00-root.jsonl", "--prices", "10,50")
        self.assertEqual(result.returncode, 1)

    def test_missing_root_exits_2(self) -> None:
        result = self.run_cli("--sessions-dir", self.sessions, "--session", "nope", "--prices", "10,50")
        self.assertEqual(result.returncode, 2)

    def test_negative_price_rejected(self) -> None:
        self.assertEqual(self.run_cli(self.child, "--prices", "-1,50").returncode, 2)
        self.assertEqual(self.run_cli(self.child, "--prices", "1,50", "--cached-mult", "-0.1").returncode, 2)

    def test_report_subtraction_clamped_to_output(self) -> None:
        report = Path(self.temp.name) / "run.md"
        report.write_text("x" * 100000, encoding="utf-8")
        row = self.run_cli(self.child, "--prices", "10,50", "--report", report, "--row", "x").stdout
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        self.assertEqual(cells[-2], "80")
        self.assertGreaterEqual(float(cells[-1].strip("*")), 0.0)


if __name__ == "__main__":
    unittest.main()
