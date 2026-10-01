"""CSV statement export."""
from __future__ import annotations

import csv
import io

from ledger.accounts import Account
from ledger.statement import statement_rows

HEADER = ("date", "description", "amount", "balance")


def statement_csv(account: Account) -> str:
    """Return the account's statement as CSV with a header row. Raises nothing."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(HEADER)
    writer.writerows(statement_rows(account))
    return out.getvalue()
