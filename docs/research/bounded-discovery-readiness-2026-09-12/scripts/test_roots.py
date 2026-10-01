#!/usr/bin/env python3
"""Test root recording and completed absence probes through the CLI.

Usage: python3 scripts/test_roots.py
Input: temporary directories only. Exit: 0 pass, 1 test failures.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import roots


class RootTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "arbitrary-real-cell-root"
        self.root.mkdir()
        self.record = self.base / "roots.json"

    def call(self, *args, expected=0):
        result = subprocess.run([sys.executable, str(Path(roots.__file__)), *map(str, args)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_record_is_exclusive_and_absence_uses_actual_root(self):
        self.call("record", "--out", self.record, "--root", self.root)
        before = self.record.read_bytes()
        self.call("record", "--out", self.record, "--root", self.root, expected=2)
        self.assertEqual(self.record.read_bytes(), before)
        self.call("check", "--record", self.record, expected=1)
        self.root.rmdir()
        result = self.call("check", "--record", self.record)
        self.assertTrue(json.loads(result.stdout)["probe_completed"])
        self.root.symlink_to(self.base / "missing")
        self.call("check", "--record", self.record, expected=1)

    def test_record_must_survive_root_removal(self):
        self.call("record", "--out", self.root / "roots.json", "--root", self.root, expected=1)

    def test_incomplete_probe_establishes_nothing(self):
        self.call("record", "--out", self.record, "--root", self.root)
        with patch.object(roots.os, "scandir", side_effect=PermissionError("permission denied")):
            with self.assertRaises(PermissionError):
                roots.check(self.record)
        self.record.write_text(json.dumps({"recorded_at": "test", "roots": [str(self.base / "missing-parent" / "cells")]}), encoding="utf-8")
        self.call("check", "--record", self.record, expected=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
