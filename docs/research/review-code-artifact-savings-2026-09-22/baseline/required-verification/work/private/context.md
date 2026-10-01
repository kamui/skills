## manifest

```
M ledger/accounts.py +15 -0 new=no lines=92
M ledger/auth.py +3 -1 new=no lines=22
A tests/test_delegates.py +33 -0 new=yes lines=33
```

## diff

```diff
diff --git a/ledger/accounts.py b/ledger/accounts.py
index 4f23cd3..d9428a7 100644
--- a/ledger/accounts.py
+++ b/ledger/accounts.py
@@ -19,9 +19,10 @@ class Entry:
 @dataclass
 class Account:
     number: str
     owner: str
     entries: list[Entry] = field(default_factory=list)
+    delegates: set[str] = field(default_factory=set)
 
     def balance(self) -> int:
         """Return the balance in cents. Raises nothing."""
         return sum(entry.amount for entry in self.entries)
@@ -30,48 +31,62 @@ class Account:
 class Ledger:
     """Accounts keyed by number."""
 
     def __init__(self) -> None:
         self.accounts: dict[str, Account] = {}
 
     def open(self, number: str, owner: str) -> Account:
         """Open an account. Raises LedgerError when the number is taken."""
         if number in self.accounts:
             raise LedgerError(f"account {number} already exists")
         account = Account(number, owner)
         self.accounts[number] = account
         return account
 
     def get(self, number: str) -> Account:
         """Return an account. Raises LedgerError when it does not exist."""
         try:
             return self.accounts[number]
         except KeyError:
             raise LedgerError(f"no account {number}") from None
 
+    def grant(self, number: str, user: str, delegate: str) -> None:
+        """Let delegate read the account's statement. Raises LedgerError unless user owns the account."""
+        account = self.get(number)
+        if account.owner != user:
+            raise LedgerError(f"{user} does not own {number}")
+        account.delegates.add(delegate)
+
+    def revoke(self, number: str, user: str, delegate: str) -> None:
+        """Withdraw a delegate's access. Raises LedgerError unless user owns the account."""
+        account = self.get(number)
+        if account.owner != user:
+            raise LedgerError(f"{user} does not own {number}")
+        account.delegates.discard(delegate)
+
     def post(self, number: str, day: date, description: str, amount: int) -> Entry:
         """Post one entry. Raises LedgerError for a zero amount, an overdraft, or an unknown account."""
         if not isinstance(amount, int) or amount == 0:
             raise LedgerError("amount must be a nonzero integer number of cents")
         account = self.get(number)
         if account.balance() + amount < 0:
             raise LedgerError(f"posting would overdraw {number}")
         entry = Entry(day, description, amount)
         account.entries.append(entry)
         return entry
 
     def transfer(self, source: str, target: str, day: date, amount: int) -> None:
         """Move a positive amount between two accounts atomically.
 
         Raises LedgerError for a non-positive amount, the same account on both
         sides, an unknown account, or an overdraft of the source.
         """
         if not isinstance(amount, int) or amount <= 0:
             raise LedgerError("transfer amount must be a positive integer number of cents")
         if source == target:
             raise LedgerError("cannot transfer to the same account")
         debit = self.get(source)
         credit = self.get(target)
         if debit.balance() < amount:
             raise LedgerError(f"transfer would overdraw {source}")
         debit.entries.append(Entry(day, f"transfer to {target}", -amount))
         credit.entries.append(Entry(day, f"transfer from {source}", amount))
diff --git a/ledger/auth.py b/ledger/auth.py
index 83de7fe..f8b67be 100644
--- a/ledger/auth.py
+++ b/ledger/auth.py
@@ -3,15 +3,17 @@ from __future__ import annotations
 
 from ledger.accounts import Account
 
-ROLES = ("owner", "auditor", "teller")
+ROLES = ("owner", "delegate", "auditor", "teller")
 
 
 def can_view(user: str, role: str, account: Account) -> bool:
     """Return whether the user may read the account's statement. Raises nothing."""
     if role not in ROLES:
         return False
     if role in ("auditor", "teller"):
         return True
+    if role == "delegate":
+        return user in account.delegates
     return account.owner == user
 
 
diff --git a/tests/test_delegates.py b/tests/test_delegates.py
new file mode 100644
index 0000000..2c842ab
--- /dev/null
+++ b/tests/test_delegates.py
@@ -0,0 +1,33 @@
+import unittest
+
+from ledger.accounts import Ledger, LedgerError
+from ledger.auth import can_post, can_view
+
+
+class DelegatesTest(unittest.TestCase):
+    def setUp(self):
+        self.ledger = Ledger()
+        self.ada = self.ledger.open("1001", "ada")
+        self.bob = self.ledger.open("1002", "bob")
+
+    def test_grant_lets_delegate_view_that_account_only(self):
+        self.ledger.grant("1001", "ada", "eve")
+        self.assertTrue(can_view("eve", "delegate", self.ada))
+        self.assertFalse(can_view("eve", "delegate", self.bob))
+
+    def test_delegate_never_posts(self):
+        self.ledger.grant("1001", "ada", "eve")
+        self.assertFalse(can_post("eve", "delegate", self.ada))
+
+    def test_only_owner_grants_and_revokes(self):
+        with self.assertRaises(LedgerError):
+            self.ledger.grant("1001", "bob", "eve")
+        self.ledger.grant("1001", "ada", "eve")
+        with self.assertRaises(LedgerError):
+            self.ledger.revoke("1001", "bob", "eve")
+        self.ledger.revoke("1001", "ada", "eve")
+        self.assertFalse(can_view("eve", "delegate", self.ada))
+
+
+if __name__ == "__main__":
+    unittest.main()
```

## ranges

```
ledger/accounts.py:19-28 @head
ledger/accounts.py:19-27 @merge-base
ledger/accounts.py:31-92 @head
ledger/accounts.py:30-77 @merge-base
ledger/auth.py:3-19 @head
ledger/auth.py:3-17 @merge-base
tests/test_delegates.py:1-33 @head
```

## history

```
ledger/accounts.py: 2301c83 2026-09-01 Start the ledger fixture
ledger/auth.py: 2301c83 2026-09-01 Start the ledger fixture
```

## chunks

```
diff ledger/accounts.py#1/1 lines=1-78 bytes=3458 consumed
diff ledger/auth.py#1/1 lines=1-23 bytes=672 consumed
diff tests/test_delegates.py#1/1 lines=1-39 bytes=1354 consumed
diff coverage: complete (3/3 chunks consumed)
```
