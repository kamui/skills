import csv
import io
import unittest
from datetime import date

from ledger.accounts import Ledger
from ledger.export import statement_csv


class ExportTest(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()
        self.account = self.ledger.open("1001", "ada")
        self.ledger.post("1001", date(2026, 9, 1), "deposit", 10_000)
        self.ledger.post("1001", date(2026, 9, 2), 'coffee, "large"', -450)

    def test_header_and_rows(self):
        lines = statement_csv(self.account).splitlines()
        self.assertEqual(lines[0], "date,description,amount,balance")
        self.assertEqual(lines[1], "2026-09-01,deposit,100.00,100.00")

    def test_descriptions_round_trip(self):
        rows = list(csv.reader(io.StringIO(statement_csv(self.account))))
        self.assertEqual(rows[2], ["2026-09-02", 'coffee, "large"', "-4.50", "95.50"])


if __name__ == "__main__":
    unittest.main()
