# Statement date filters

Statements always cover an account's whole history. Let a reader ask for a date range.

1. `ledger statement FILE ACCOUNT` accepts optional `--since YYYY-MM-DD` and `--until YYYY-MM-DD`; both bounds are inclusive.
2. With `--since`, the line after the heading is `Opening balance: <amount>`, the balance of every entry dated before `--since`.
3. Only entries dated within the range are listed, and each row's running balance continues from the opening balance.
4. `Closing balance` is the balance of every entry dated on or before `--until`, or of every entry when `--until` is absent.
5. An invalid date, or a `--since` later than `--until`, exits with status 2 and a message on stderr.
6. The README documents both options.
