## manifest

```
M ledger/cli.py +6 -2 new=no lines=52
A ledger/export.py +19 -0 new=yes lines=19
A tests/test_export.py +28 -0 new=yes lines=28
```

## diff

```diff
diff --git a/ledger/cli.py b/ledger/cli.py
index ac80393..59e9d6f 100644
--- a/ledger/cli.py
+++ b/ledger/cli.py
@@ -1,4 +1,4 @@
-"""Command line: python3 -m ledger.cli statement FILE ACCOUNT."""
+"""Command line: python3 -m ledger.cli statement FILE ACCOUNT [--format text|csv]."""
 from __future__ import annotations
 
 import argparse
@@ -7,8 +7,11 @@ import sys
 from datetime import date
 
 from ledger.accounts import Ledger
+from ledger.export import statement_csv
 from ledger.statement import render_statement
 
+FORMATS = {"text": render_statement, "csv": statement_csv}
+
 
 def load(path: str) -> Ledger:
     """Load a ledger from JSON. Raises OSError, ValueError, KeyError, or LedgerError on bad input."""
@@ -25,20 +28,21 @@ def load(path: str) -> Ledger:
 def build_parser() -> argparse.ArgumentParser:
     """Return the argument parser. Raises nothing."""
     parser = argparse.ArgumentParser(prog="ledger")
     commands = parser.add_subparsers(dest="command", required=True)
     statement = commands.add_parser("statement", help="print an account statement")
     statement.add_argument("file")
     statement.add_argument("account")
+    statement.add_argument("--format", choices=sorted(FORMATS), default="text")
     return parser
 
 
 def main(argv: list[str] | None = None) -> int:
     """Run the command line. Returns 2 on unreadable input or an unknown account."""
     args = build_parser().parse_args(argv)
     try:
         ledger = load(args.file)
-        sys.stdout.write(render_statement(ledger.get(args.account)))
+        sys.stdout.write(FORMATS[args.format](ledger.get(args.account)))
     except (OSError, ValueError, KeyError) as error:
         print(f"ledger: {error}", file=sys.stderr)
         return 2
     return 0
diff --git a/ledger/export.py b/ledger/export.py
new file mode 100644
index 0000000..b60fa2e
--- /dev/null
+++ b/ledger/export.py
@@ -0,0 +1,19 @@
+"""CSV statement export."""
+from __future__ import annotations
+
+import csv
+import io
+
+from ledger.accounts import Account
+from ledger.statement import statement_rows
+
+HEADER = ("date", "description", "amount", "balance")
+
+
+def statement_csv(account: Account) -> str:
+    """Return the account's statement as CSV with a header row. Raises nothing."""
+    out = io.StringIO()
+    writer = csv.writer(out, lineterminator="\n")
+    writer.writerow(HEADER)
+    writer.writerows(statement_rows(account))
+    return out.getvalue()
diff --git a/tests/test_export.py b/tests/test_export.py
new file mode 100644
index 0000000..07c358a
--- /dev/null
+++ b/tests/test_export.py
@@ -0,0 +1,28 @@
+import csv
+import io
+import unittest
+from datetime import date
+
+from ledger.accounts import Ledger
+from ledger.export import statement_csv
+
+
+class ExportTest(unittest.TestCase):
+    def setUp(self):
+        self.ledger = Ledger()
+        self.account = self.ledger.open("1001", "ada")
+        self.ledger.post("1001", date(2026, 9, 1), "deposit", 10_000)
+        self.ledger.post("1001", date(2026, 9, 2), 'coffee, "large"', -450)
+
+    def test_header_and_rows(self):
+        lines = statement_csv(self.account).splitlines()
+        self.assertEqual(lines[0], "date,description,amount,balance")
+        self.assertEqual(lines[1], "2026-09-01,deposit,100.00,100.00")
+
+    def test_descriptions_round_trip(self):
+        rows = list(csv.reader(io.StringIO(statement_csv(self.account))))
+        self.assertEqual(rows[2], ["2026-09-02", 'coffee, "large"', "-4.50", "95.50"])
+
+
+if __name__ == "__main__":
+    unittest.main()
```

## ranges

```
ledger/cli.py:1-4 @head
ledger/cli.py:1-4 @merge-base
ledger/cli.py:7-17 @head
ledger/cli.py:7-14 @merge-base
ledger/cli.py:28-48 @head
ledger/cli.py:25-44 @merge-base
ledger/export.py:1-19 @head
tests/test_export.py:1-28 @head
```

## history

```
ledger/cli.py: 2301c83 2026-09-01 Start the ledger fixture
```

## chunks

```
diff ledger/cli.py#1/1 lines=1-45 bytes=1765 consumed
diff ledger/export.py#1/1 lines=1-25 bytes=690 consumed
diff tests/test_export.py#1/1 lines=1-34 bytes=1108 consumed
diff coverage: complete (3/3 chunks consumed)
```
