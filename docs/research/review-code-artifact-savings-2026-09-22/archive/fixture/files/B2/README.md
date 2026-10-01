# Ledger

A small single-currency ledger. Accounts hold dated entries in integer cents.

```sh
python3 -m ledger.cli statement ledger.json 1001
python3 -m ledger.cli statement ledger.json 1001 --since 2026-09-01 --until 2026-09-30
```

The JSON file lists accounts as `{"number", "owner", "entries": [[day, description, cents], ...]}`.

`--since` and `--until` are inclusive and optional. With `--since`, the statement opens with the balance of every earlier entry; the closing balance covers every entry through `--until`.
