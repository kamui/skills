#!/usr/bin/env python3
"""Exercise run timing through the transcript_usage.py CLI.

Usage: python3 docs/research/tools/test_transcript_usage.py
Inputs: temporary synthetic JSONL transcripts and JSON timing sidecars.
Exit codes: 0 all checks pass; 1 a test fails.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("transcript_usage.py")


class TimingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.root = self.transcript("root", "12:00:05", "12:01:35")
        self.sidecar = self.directory / "timing.json"
        self.events = {
            "completion_mode": "publication",
            "root_dispatched_at": "2026-09-05T12:00:00Z",
            "payload_validated_at": "2026-09-05T12:01:40Z",
            "completed_at": "2026-09-05T12:02:00Z",
        }

    def transcript(self, name: str, first, last) -> Path:
        path = self.directory / f"{name}.jsonl"
        records = [{
            "type": "assistant",
            "timestamp": f"2026-09-05T{stamp}Z" if stamp else None,
            "message": {"model": "test-model", "content": [], "usage": {
                "input_tokens": 10, "output_tokens": 20,
                "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
            }},
        } for stamp in (first, last)]
        path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
        return path

    def run_cli(self, *options, paths=None, events=None) -> subprocess.CompletedProcess:
        args = [sys.executable, str(SCRIPT), *map(str, paths or [self.root]), "--prices", "2,10"]
        if events is not None:
            self.sidecar.write_text(json.dumps(events), encoding="utf-8")
            args.extend(["--timing", str(self.sidecar)])
        return subprocess.run([*args, *options], capture_output=True, text=True, encoding="utf-8")

    def read_json(self, **kwargs) -> dict:
        result = self.run_cli("--json", **kwargs)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_overlapping_and_sequential_children(self) -> None:
        overlapping = [self.transcript("overlap-a", "12:00:10", "12:01:10"),
                       self.transcript("overlap-b", "12:00:20", "12:01:20")]
        sequential = [self.transcript("seq-a", "12:00:10", "12:00:40"),
                      self.transcript("seq-b", "12:00:50", "12:01:20")]
        for children, span_sum in ((overlapping, 210), (sequential, 150)):
            with self.subTest(span_sum=span_sum):
                paths = [self.root, *children]
                legacy = self.read_json(paths=paths)
                measured = self.read_json(paths=paths, events=self.events)
                self.assertEqual(measured["total"]["wall_seconds"], span_sum)
                self.assertEqual(measured["total"]["agent_span_sum_seconds"], span_sum)
                self.assertEqual(measured["timing"]["elapsed_to_payload_seconds"], 100)
                self.assertEqual(measured["timing"]["elapsed_to_completion_seconds"], 120)
                self.assertEqual(measured["total"], legacy["total"])
                self.assertEqual(measured["transcripts"], legacy["transcripts"])

    def test_timezone_offsets_and_fractional_seconds(self) -> None:
        self.events.update(root_dispatched_at="2026-09-05T08:00:00.250-04:00",
                           payload_validated_at="2026-09-05T14:01:40.500+02:00")
        timing = self.read_json(events=self.events)["timing"]
        self.assertEqual(timing["root_dispatched_at"], "2026-09-05T12:00:00.250000+00:00")
        self.assertEqual(timing["elapsed_to_payload_seconds"], 100.25)
        self.assertEqual(timing["elapsed_to_completion_seconds"], 119.75)

    def test_completion_modes_without_publication(self) -> None:
        for mode in ("render-only", "result"):
            with self.subTest(mode=mode):
                self.events["completion_mode"] = mode
                timing = self.read_json(events=self.events)["timing"]
                self.assertEqual(timing["completion_mode"], mode)
                self.assertEqual(timing["elapsed_to_completion_seconds"], 120)
                del self.events["completed_at"]
                self.assertIsNone(self.read_json(events=self.events)["timing"]["elapsed_to_completion_seconds"])
                self.events["completed_at"] = "2026-09-05T12:02:00Z"

    def test_missing_events_are_not_inferred(self) -> None:
        self.assertTrue(all(value is None for value in self.read_json()["timing"].values()))
        for missing in ("root_dispatched_at", "payload_validated_at", "completed_at"):
            for explicit_null in (False, True):
                with self.subTest(missing=missing, explicit_null=explicit_null):
                    events = dict(self.events)
                    if explicit_null:
                        events[missing] = None
                    else:
                        del events[missing]
                    timing = self.read_json(events=events)["timing"]
                    self.assertIsNone(timing[missing])
                    self.assertEqual(timing["elapsed_to_payload_seconds"],
                                     None if missing != "completed_at" else 100)
                    self.assertEqual(timing["elapsed_to_completion_seconds"],
                                     None if missing != "payload_validated_at" else 120)
        no_stamps = self.transcript("no-stamps", None, None)
        self.assertIsNone(self.read_json(paths=[no_stamps])["timing"]["elapsed_to_completion_seconds"])
        self.assertEqual(self.read_json(paths=[no_stamps], events=self.events)["timing"]["elapsed_to_completion_seconds"], 120)

    def test_invalid_ordering_even_with_missing_events(self) -> None:
        cases = [dict(self.events, payload_validated_at="2026-09-05T11:59:59Z"),
                 dict(self.events, completed_at="2026-09-05T12:00:30Z"),
                 dict(self.events, payload_validated_at=None, completed_at="2026-09-05T11:59:59Z"),
                 dict(self.events, root_dispatched_at=None, completed_at="2026-09-05T12:00:30Z")]
        for events in cases:
            with self.subTest(events=events):
                result = self.run_cli("--json", events=events)
                self.assertEqual(result.returncode, 2)
                self.assertIn(str(self.sidecar), result.stderr)
                self.assertIn("precedes", result.stderr)
                self.assertEqual(result.stdout, "")
        self.events.update(payload_validated_at=self.events["root_dispatched_at"],
                           completed_at=self.events["root_dispatched_at"])
        self.assertEqual(self.read_json(events=self.events)["timing"]["elapsed_to_completion_seconds"], 0)

    def test_invalid_schema_and_unreadable_sidecar(self) -> None:
        invalid = [[], {}, dict(self.events, completion_mode="unknown"),
                   dict(self.events, completed_at="2026-09-05T12:02:00"),
                   dict(self.events, completed_at="2026-09-31T12:02:00Z"),
                   dict(self.events, completed_at="2026-09-05T12:02:00+00:60"),
                   dict(self.events, completed_at=123), dict(self.events, typo="event")]
        for events in invalid:
            with self.subTest(events=events):
                result = self.run_cli("--json", events=events)
                self.assertEqual(result.returncode, 2)
                self.assertIn(str(self.sidecar), result.stderr)
                self.assertEqual(result.stdout, "")
        for raw in ("{broken", "\xff"):
            self.sidecar.write_bytes(raw.encode("latin-1"))
            result = self.run_cli("--timing", str(self.sidecar))
            self.assertEqual(result.returncode, 2)
            self.assertIn(str(self.sidecar), result.stderr)
        self.sidecar.unlink()
        result = self.run_cli("--timing", str(self.sidecar))
        self.assertEqual(result.returncode, 2)
        self.assertIn(str(self.sidecar), result.stderr)

    def test_report_blocks_and_legacy_rows(self) -> None:
        report = self.directory / "report.md"
        report.write_text("research report", encoding="utf-8")
        for options in (("--row", "run"), ("--report", str(report), "--row", "run"), ("--header",)):
            legacy = self.run_cli(*options)
            measured = self.run_cli(*options, events=self.events)
            self.assertEqual(measured.returncode, 0, measured.stderr)
            self.assertEqual(measured.stdout, legacy.stdout)
        result = self.run_cli("--report", str(report), events=self.events)
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in ("agent span sum", "not elapsed", "completion mode: publication",
                         "elapsed to payload seconds: 100.0", "elapsed to completion seconds: 120.0"):
            self.assertIn(expected, result.stdout)
        result = self.run_cli()
        self.assertIn("elapsed to completion seconds: unavailable", result.stdout)


if __name__ == "__main__":
    unittest.main()
