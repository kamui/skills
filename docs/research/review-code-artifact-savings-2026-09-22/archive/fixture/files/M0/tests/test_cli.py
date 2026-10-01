import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from ledger.cli import main

DATA = {"accounts": [{"number": "1001", "owner": "ada",
                      "entries": [["2026-09-01", "deposit", 10000], ["2026-09-02", "coffee", -450]]}]}


class CliTest(unittest.TestCase):
    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(handle, "w", encoding="utf-8") as out:
            json.dump(DATA, out)

    def tearDown(self):
        os.unlink(self.path)

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = main(list(argv))
        return status, out.getvalue(), err.getvalue()

    def test_statement(self):
        status, out, _ = self.run_cli("statement", self.path, "1001")
        self.assertEqual(status, 0)
        self.assertIn("Closing balance: 95.50", out)

    def test_unknown_account_exits_2(self):
        status, _, err = self.run_cli("statement", self.path, "9999")
        self.assertEqual(status, 2)
        self.assertIn("no account 9999", err)


if __name__ == "__main__":
    unittest.main()
