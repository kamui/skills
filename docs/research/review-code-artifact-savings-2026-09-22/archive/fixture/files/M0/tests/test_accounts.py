import unittest
from datetime import date

from ledger.accounts import Ledger, LedgerError

DAY = date(2026, 9, 1)


class AccountsTest(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()
        self.ledger.open("1001", "ada")
        self.ledger.open("1002", "bob")
        self.ledger.post("1001", DAY, "deposit", 10_000)

    def test_post_updates_balance(self):
        self.ledger.post("1001", DAY, "fee", -250)
        self.assertEqual(self.ledger.get("1001").balance(), 9_750)

    def test_post_refuses_zero_and_overdraft(self):
        with self.assertRaises(LedgerError):
            self.ledger.post("1001", DAY, "nothing", 0)
        with self.assertRaises(LedgerError):
            self.ledger.post("1002", DAY, "fee", -1)
        self.assertEqual(self.ledger.get("1002").entries, [])

    def test_open_refuses_duplicate(self):
        with self.assertRaises(LedgerError):
            self.ledger.open("1001", "eve")

    def test_transfer_moves_money(self):
        self.ledger.transfer("1001", "1002", DAY, 2_500)
        self.assertEqual(self.ledger.get("1001").balance(), 7_500)
        self.assertEqual(self.ledger.get("1002").balance(), 2_500)

    def test_refused_transfer_changes_nothing(self):
        with self.assertRaises(LedgerError):
            self.ledger.transfer("1002", "1001", DAY, 1)
        with self.assertRaises(LedgerError):
            self.ledger.transfer("1001", "1001", DAY, 1)
        self.assertEqual(len(self.ledger.get("1001").entries), 1)
        self.assertEqual(self.ledger.get("1002").entries, [])


if __name__ == "__main__":
    unittest.main()
