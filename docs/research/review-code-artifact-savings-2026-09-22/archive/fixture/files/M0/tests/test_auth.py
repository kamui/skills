import unittest

from ledger.accounts import Account
from ledger.auth import can_post, can_view


class AuthTest(unittest.TestCase):
    def setUp(self):
        self.account = Account("1001", "ada")

    def test_owner_views_only_own_account(self):
        self.assertTrue(can_view("ada", "owner", self.account))
        self.assertFalse(can_view("bob", "owner", self.account))

    def test_staff_view_every_account(self):
        self.assertTrue(can_view("carol", "auditor", self.account))
        self.assertTrue(can_view("dan", "teller", self.account))

    def test_unknown_role_sees_nothing(self):
        self.assertFalse(can_view("ada", "admin", self.account))

    def test_only_tellers_post(self):
        self.assertTrue(can_post("dan", "teller", self.account))
        self.assertFalse(can_post("ada", "owner", self.account))
        self.assertFalse(can_post("carol", "auditor", self.account))


if __name__ == "__main__":
    unittest.main()
