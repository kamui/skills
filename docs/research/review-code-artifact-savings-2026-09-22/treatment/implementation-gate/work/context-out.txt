## manifest

```
M README.md +3 -0 new=no lines=12
M ledger/cli.py +16 -3 new=no lines=61
M ledger/statement.py +30 -6 new=no lines=54
A tests/test_filter.py +46 -0 new=yes lines=46
```

## diff

````diff
diff --git a/README.md b/README.md
index 3c8203a..c57fb92 100644
--- a/README.md
+++ b/README.md
@@ -4,6 +4,9 @@ A small single-currency ledger. Accounts hold dated entries in integer cents.
 
 ```sh
 python3 -m ledger.cli statement ledger.json 1001
+python3 -m ledger.cli statement ledger.json 1001 --since 2026-09-01 --until 2026-09-30
 ```
 
 The JSON file lists accounts as `{"number", "owner", "entries": [[day, description, cents], ...]}`.
+
+`--since` and `--until` are inclusive and optional. With `--since`, the statement opens with the balance of every earlier entry; the closing balance covers every entry through `--until`.
diff --git a/ledger/cli.py b/ledger/cli.py
index ac80393..055b0a0 100644
--- a/ledger/cli.py
+++ b/ledger/cli.py
@@ -1,4 +1,4 @@
-"""Command line: python3 -m ledger.cli statement FILE ACCOUNT."""
+"""Command line: python3 -m ledger.cli statement FILE ACCOUNT [--since DAY] [--until DAY]."""
 from __future__ import annotations
 
 import argparse
@@ -22,23 +22,36 @@ def load(path: str) -> Ledger:
     return ledger
 
 
+def iso_day(text: str) -> date:
+    """Parse YYYY-MM-DD. Raises argparse.ArgumentTypeError for anything else."""
+    try:
+        return date.fromisoformat(text)
+    except ValueError:
+        raise argparse.ArgumentTypeError(f"not a YYYY-MM-DD date: {text!r}") from None
+
+
 def build_parser() -> argparse.ArgumentParser:
     """Return the argument parser. Raises nothing."""
     parser = argparse.ArgumentParser(prog="ledger")
     commands = parser.add_subparsers(dest="command", required=True)
     statement = commands.add_parser("statement", help="print an account statement")
     statement.add_argument("file")
     statement.add_argument("account")
+    statement.add_argument("--since", type=iso_day, help="first day to include, YYYY-MM-DD")
+    statement.add_argument("--until", type=iso_day, help="last day to include, YYYY-MM-DD")
     return parser
 
 
 def main(argv: list[str] | None = None) -> int:
-    """Run the command line. Returns 2 on unreadable input or an unknown account."""
+    """Run the command line. Returns 2 on unreadable input, an unknown account, or an empty date range."""
     args = build_parser().parse_args(argv)
+    if args.since is not None and args.until is not None and args.since > args.until:
+        print("ledger: --since is after --until", file=sys.stderr)
+        return 2
     try:
         ledger = load(args.file)
-        sys.stdout.write(render_statement(ledger.get(args.account)))
+        sys.stdout.write(render_statement(ledger.get(args.account), args.since, args.until))
     except (OSError, ValueError, KeyError) as error:
         print(f"ledger: {error}", file=sys.stderr)
         return 2
     return 0
diff --git a/ledger/statement.py b/ledger/statement.py
index 9093565..c75e637 100644
--- a/ledger/statement.py
+++ b/ledger/statement.py
@@ -1,6 +1,9 @@
 """Plain-text account statements."""
 from __future__ import annotations
 
+from datetime import date
+from typing import Optional
+
 from ledger.accounts import Account
 
 
@@ -11,20 +14,41 @@ def format_cents(cents: int) -> str:
     return f"{sign}{whole}.{part:02d}"
 
 
-def statement_rows(account: Account) -> list[tuple[str, str, str, str]]:
-    """Return (date, description, amount, running balance) rows in posting order. Raises nothing."""
+def balance_before(account: Account, day: date) -> int:
+    """Return the balance of every entry dated before day. Raises nothing."""
+    return sum(entry.amount for entry in account.entries if entry.day < day)
+
+
+def balance_through(account: Account, day: date) -> int:
+    """Return the balance of every entry dated on or before day. Raises nothing."""
+    return sum(entry.amount for entry in account.entries if entry.day <= day)
+
+
+def statement_rows(account: Account, since: Optional[date] = None,
+                   until: Optional[date] = None) -> list[tuple[str, str, str, str]]:
+    """Return (date, description, amount, running balance) rows dated since..until inclusive.
+
+    Rows keep posting order. Raises nothing.
+    """
     rows = []
     running = 0
     for entry in account.entries:
         running += entry.amount
+        if since is not None and entry.day < since:
+            continue
+        if until is not None and entry.day > until:
+            continue
         rows.append((entry.day.isoformat(), entry.description, format_cents(entry.amount), format_cents(running)))
     return rows
 
 
-def render_statement(account: Account) -> str:
-    """Render a fixed-width statement ending with the closing balance. Raises nothing."""
+def render_statement(account: Account, since: Optional[date] = None, until: Optional[date] = None) -> str:
+    """Render a fixed-width statement for since..until inclusive. Raises nothing."""
     lines = [f"Statement for {account.number} ({account.owner})"]
-    for day, description, amount, running in statement_rows(account):
+    if since is not None:
+        lines.append(f"Opening balance: {format_cents(balance_before(account, since))}")
+    for day, description, amount, running in statement_rows(account, since, until):
         lines.append(f"{day}  {description:<30.30}  {amount:>12}  {running:>12}")
-    lines.append(f"Closing balance: {format_cents(account.balance())}")
+    closing = account.balance() if until is None else balance_through(account, until)
+    lines.append(f"Closing balance: {format_cents(closing)}")
     return "\n".join(lines) + "\n"
diff --git a/tests/test_filter.py b/tests/test_filter.py
new file mode 100644
index 0000000..a9a811e
--- /dev/null
+++ b/tests/test_filter.py
@@ -0,0 +1,46 @@
+import io
+import json
+import os
+import tempfile
+import unittest
+from contextlib import redirect_stderr, redirect_stdout
+from datetime import date
+
+from ledger.accounts import Ledger
+from ledger.cli import main
+from ledger.statement import render_statement, statement_rows
+
+ENTRIES = [["2026-08-30", "deposit", 10000], ["2026-09-01", "rent", -4000], ["2026-09-03", "coffee", -450]]
+
+
+class FilterTest(unittest.TestCase):
+    def setUp(self):
+        self.ledger = Ledger()
+        self.account = self.ledger.open("1001", "ada")
+        for day, description, cents in ENTRIES:
+            self.ledger.post("1001", date.fromisoformat(day), description, cents)
+
+    def test_rows_are_inclusive(self):
+        rows = statement_rows(self.account, date(2026, 9, 1), date(2026, 9, 3))
+        self.assertEqual([row[1] for row in rows], ["rent", "coffee"])
+
+    def test_opening_and_closing_balances(self):
+        text = render_statement(self.account, date(2026, 9, 1), date(2026, 9, 1))
+        self.assertIn("Opening balance: 100.00\n", text)
+        self.assertIn("  60.00\n", text)
+        self.assertTrue(text.endswith("Closing balance: 60.00\n"))
+
+    def test_cli_refuses_reversed_range(self):
+        handle, path = tempfile.mkstemp(suffix=".json")
+        with os.fdopen(handle, "w", encoding="utf-8") as out:
+            json.dump({"accounts": [{"number": "1001", "owner": "ada", "entries": ENTRIES}]}, out)
+        self.addCleanup(os.unlink, path)
+        err = io.StringIO()
+        with redirect_stdout(io.StringIO()), redirect_stderr(err):
+            status = main(["statement", path, "1001", "--since", "2026-09-03", "--until", "2026-09-01"])
+        self.assertEqual(status, 2)
+        self.assertIn("--since is after --until", err.getvalue())
+
+
+if __name__ == "__main__":
+    unittest.main()
````

## ranges

```
README.md:4-12 @head
README.md:4-9 @merge-base
ledger/cli.py:1-4 @head
ledger/cli.py:1-4 @merge-base
ledger/cli.py:22-57 @head
ledger/cli.py:22-44 @merge-base
ledger/statement.py:1-9 @head
ledger/statement.py:1-6 @merge-base
ledger/statement.py:14-54 @head
ledger/statement.py:11-30 @merge-base
tests/test_filter.py:1-46 @head
```

## history

```
README.md: 2301c83 2026-09-01 Start the ledger fixture
ledger/cli.py: 2301c83 2026-09-01 Start the ledger fixture
ledger/statement.py: 2301c83 2026-09-01 Start the ledger fixture
```

## chunks

```
diff README.md#1/1 lines=1-14 bytes=636 consumed
diff ledger/cli.py#1/1 lines=1-49 bytes=2103 consumed
diff ledger/statement.py#1/1 lines=1-62 bytes=2757 consumed
diff tests/test_filter.py#1/1 lines=1-52 bytes=2007 consumed
diff coverage: complete (4/4 chunks consumed)
```
