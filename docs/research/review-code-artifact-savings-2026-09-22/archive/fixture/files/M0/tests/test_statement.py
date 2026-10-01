import unittest
from datetime import date

from ledger.accounts import Ledger
from ledger.statement import format_cents, render_statement, statement_rows


class StatementTest(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()
        self.account = self.ledger.open("1001", "ada")
        self.ledger.post("1001", date(2026, 9, 1), "deposit", 10_000)
        self.ledger.post("1001", date(2026, 9, 2), "coffee", -450)

    def test_format_cents(self):
        self.assertEqual(format_cents(0), "0.00")
        self.assertEqual(format_cents(-1_250), "-12.50")
        self.assertEqual(format_cents(7), "0.07")

    def test_rows_carry_running_balance(self):
        self.assertEqual(statement_rows(self.account), [
            ("2026-09-01", "deposit", "100.00", "100.00"),
            ("2026-09-02", "coffee", "-4.50", "95.50"),
        ])

    def test_render_ends_with_closing_balance(self):
        text = render_statement(self.account)
        self.assertTrue(text.startswith("Statement for 1001 (ada)\n"))
        self.assertTrue(text.endswith("Closing balance: 95.50\n"))


if __name__ == "__main__":
    unittest.main()
