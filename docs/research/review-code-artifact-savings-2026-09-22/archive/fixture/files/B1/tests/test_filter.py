import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date

from ledger.accounts import Ledger
from ledger.cli import main
from ledger.statement import render_statement, statement_rows

ENTRIES = [["2026-08-30", "deposit", 10000], ["2026-09-01", "rent", -4000], ["2026-09-03", "coffee", -450]]


class FilterTest(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()
        self.account = self.ledger.open("1001", "ada")
        for day, description, cents in ENTRIES:
            self.ledger.post("1001", date.fromisoformat(day), description, cents)

    def test_rows_are_inclusive(self):
        rows = statement_rows(self.account, date(2026, 9, 1), date(2026, 9, 3))
        self.assertEqual([row[1] for row in rows], ["rent", "coffee"])

    def test_opening_and_closing_balances(self):
        text = render_statement(self.account, date(2026, 9, 1), date(2026, 9, 1))
        self.assertIn("Opening balance: 100.00\n", text)
        self.assertIn("  60.00\n", text)
        self.assertTrue(text.endswith("Closing balance: 60.00\n"))

    def test_cli_refuses_reversed_range(self):
        handle, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(handle, "w", encoding="utf-8") as out:
            json.dump({"accounts": [{"number": "1001", "owner": "ada", "entries": ENTRIES}]}, out)
        self.addCleanup(os.unlink, path)
        err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(err):
            status = main(["statement", path, "1001", "--since", "2026-09-03", "--until", "2026-09-01"])
        self.assertEqual(status, 2)
        self.assertIn("--since is after --until", err.getvalue())


if __name__ == "__main__":
    unittest.main()
