import unittest

from ledger.accounts import Ledger, LedgerError
from ledger.auth import can_post, can_view


class DelegatesTest(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()
        self.ada = self.ledger.open("1001", "ada")
        self.bob = self.ledger.open("1002", "bob")

    def test_grant_lets_delegate_view_that_account_only(self):
        self.ledger.grant("1001", "ada", "eve")
        self.assertTrue(can_view("eve", "delegate", self.ada))
        self.assertFalse(can_view("eve", "delegate", self.bob))

    def test_delegate_never_posts(self):
        self.ledger.grant("1001", "ada", "eve")
        self.assertFalse(can_post("eve", "delegate", self.ada))

    def test_only_owner_grants_and_revokes(self):
        with self.assertRaises(LedgerError):
            self.ledger.grant("1001", "bob", "eve")
        self.ledger.grant("1001", "ada", "eve")
        with self.assertRaises(LedgerError):
            self.ledger.revoke("1001", "bob", "eve")
        self.ledger.revoke("1001", "ada", "eve")
        self.assertFalse(can_view("eve", "delegate", self.ada))


if __name__ == "__main__":
    unittest.main()
