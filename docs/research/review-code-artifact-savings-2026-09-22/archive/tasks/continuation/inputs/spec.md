# Account freezing

Operations staff need to stop all activity on an account while a dispute is investigated.

1. `Ledger.freeze(number)` and `Ledger.unfreeze(number)` switch an account's frozen state; an unknown account raises `LedgerError`.
2. A frozen account accepts no new entries of any kind: postings, transfers out of it, and transfers into it each raise `LedgerError`.
3. A refused operation changes no account.
4. Unfreezing restores normal behavior.
5. A frozen account's balance and statement stay readable.
