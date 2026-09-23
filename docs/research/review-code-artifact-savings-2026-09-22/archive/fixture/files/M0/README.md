# Ledger

A small single-currency ledger. Accounts hold dated entries in integer cents.

```sh
python3 -m ledger.cli statement ledger.json 1001
```

The JSON file lists accounts as `{"number", "owner", "entries": [[day, description, cents], ...]}`.
