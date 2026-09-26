#!/usr/bin/env python3
"""Check offline answer-table populations and cost/timing samples.

Usage: python3 -B bench/tools/test_answers.py
Inputs: synthetic attempts and scores; no network or model calls.
Exit codes: 0 every test passed; 1 a test failed.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import unittest

import score

SCRIPT = Path(__file__).resolve().parents[2] / "docs/research/builtin-review-benchmark-2026-09-24/answers.py"
SPEC = importlib.util.spec_from_file_location("answers", SCRIPT)
answers = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(answers)


def rendered(function, *args):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        function(*args)
    return output.getvalue()


class Accounting(unittest.TestCase):
    def test_invalid_attempt_counts_stay_out_of_valid_review_rates(self):
        record = {"attempt_id": "valid", "disposition": "valid completed",
                  "usage": {"priced_total_usd": 1}, "timing": {}}
        level = {"completion": "completed", "approved_on_buggy": True,
                 "zero_recovery": True, "false_clean": True}
        entry = {"items": [{"assignment": "non-material", "priority_error": "n/a"}], "review_level": level}
        register = {"defects": [{"id": "GT-1"}]}
        valid = score.score_attempt(record, entry, register, 1)
        invalid = score.score_attempt(dict(record, disposition="harness-invalid: audit"),
                                      dict(entry, items=entry["items"] * 6), register, 1)
        rows = [score.row({"arm": arm}, [("t", valid), ("t", invalid)],
                          [{"target": "t", "status": "valid completed", "attempts": ["bad", "valid"]}],
                          {"t": {"buggy": True}}) for arm in answers.ORDER]
        table = rendered(answers.review_table, {"by_arm": rows})
        self.assertIn("| Attempts | Valid reviews |", table)
        self.assertIn("| A review-code | 2 | 1 | 0.000 (0.000) | 0.00 / 0.00 (0 / 0) | 1/1 | 1/1 | 1/1 | 1.0 (1 items) |", table)
        self.assertIn("| A review-code | 2 | 0.00 / 0.00 (0 / 0) | 2 | 2 | 2 | 7 | 6 |", table)

    def test_null_timestamps_reduce_timing_pairs_without_dropping_retry_cost(self):
        cells, attempts = [], {}
        for arm in answers.ORDER:
            for replicate in (1, 2):
                attempt_id = f"{arm}-{replicate}"
                attempts[attempt_id] = {
                    "usage": {"priced_total_usd": 2 if arm == answers.A else 1},
                    "timing": {"dispatched_at": "2026-01-01T00:00:00Z",
                               "payload_validated_at": None if arm == "codex-default" and replicate == 1
                               else "2026-01-01T00:01:00Z"},
                }
                cells.append({"target": "t", "arm": arm, "replicate": replicate, "attempts": [attempt_id]})
        attempts["retry"] = {"usage": {"priced_total_usd": 2}, "timing": {"payload_validated_at": None}}
        cells[0]["attempts"].insert(0, "retry")
        table = rendered(answers.cost_table, {"cells": cells}, attempts)
        self.assertIn("| Cost pairs | Timing pairs |", table)
        self.assertIn("| A review-code | 2 | 2 | 1.00 | 6.00 | 1.00 | 60 |", table)
        self.assertIn("| D codex review | 2 | 1 | 0.38 | 2.00 | 1.00 | 60 |", table)


if __name__ == "__main__":
    unittest.main()
