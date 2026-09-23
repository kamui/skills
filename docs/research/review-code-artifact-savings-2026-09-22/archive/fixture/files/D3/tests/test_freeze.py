import unittest
from datetime import date

from ledger.accounts import Ledger, LedgerError

DAY = date(2026, 9, 1)


class FreezeTest(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()
        self.ledger.open("1001", "ada")
        self.ledger.post("1001", DAY, "deposit", 10_000)

    def test_frozen_account_refuses_postings(self):
        self.ledger.freeze("1001")
        with self.assertRaises(LedgerError):
            self.ledger.post("1001", DAY, "fee", -100)
        with self.assertRaises(LedgerError):
            self.ledger.post("1001", DAY, "deposit", 100)
        self.assertEqual(self.ledger.get("1001").balance(), 10_000)

    def test_frozen_account_refuses_transfers_both_ways(self):
        self.ledger.open("1002", "bob")
        self.ledger.freeze("1001")
        with self.assertRaises(LedgerError):
            self.ledger.transfer("1001", "1002", DAY, 100)
        self.ledger.unfreeze("1001")
        self.ledger.transfer("1001", "1002", DAY, 500)
        self.ledger.freeze("1001")
        with self.assertRaises(LedgerError):
            self.ledger.transfer("1002", "1001", DAY, 100)
        self.assertEqual(self.ledger.get("1001").balance(), 9_500)
        self.assertEqual(self.ledger.get("1002").balance(), 500)

    def test_unfreeze_restores_postings(self):
        self.ledger.freeze("1001")
        self.ledger.unfreeze("1001")
        self.ledger.post("1001", DAY, "fee", -100)
        self.assertEqual(self.ledger.get("1001").balance(), 9_900)

    def test_frozen_account_stays_readable(self):
        self.ledger.freeze("1001")
        self.assertEqual(self.ledger.get("1001").balance(), 10_000)


if __name__ == "__main__":
    unittest.main()
