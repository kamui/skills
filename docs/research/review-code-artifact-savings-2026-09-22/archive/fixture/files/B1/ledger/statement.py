"""Plain-text account statements."""
from __future__ import annotations

from datetime import date
from typing import Optional

from ledger.accounts import Account


def format_cents(cents: int) -> str:
    """Render cents as a signed decimal amount such as -12.50. Raises nothing."""
    sign = "-" if cents < 0 else ""
    whole, part = divmod(abs(cents), 100)
    return f"{sign}{whole}.{part:02d}"


def balance_before(account: Account, day: date) -> int:
    """Return the balance of every entry dated before day. Raises nothing."""
    return sum(entry.amount for entry in account.entries if entry.day < day)


def balance_through(account: Account, day: date) -> int:
    """Return the balance of every entry dated on or before day. Raises nothing."""
    return sum(entry.amount for entry in account.entries if entry.day <= day)


def statement_rows(account: Account, since: Optional[date] = None,
                   until: Optional[date] = None) -> list[tuple[str, str, str, str]]:
    """Return (date, description, amount, running balance) rows dated since..until inclusive.

    Rows keep posting order. Raises nothing.
    """
    rows = []
    running = 0
    for entry in account.entries:
        running += entry.amount
        if since is not None and entry.day < since:
            continue
        if until is not None and entry.day > until:
            continue
        rows.append((entry.day.isoformat(), entry.description, format_cents(entry.amount), format_cents(running)))
    return rows


def render_statement(account: Account, since: Optional[date] = None, until: Optional[date] = None) -> str:
    """Render a fixed-width statement for since..until inclusive. Raises nothing."""
    lines = [f"Statement for {account.number} ({account.owner})"]
    if since is not None:
        lines.append(f"Opening balance: {format_cents(balance_before(account, since))}")
    for day, description, amount, running in statement_rows(account, since, until):
        lines.append(f"{day}  {description:<30.30}  {amount:>12}  {running:>12}")
    closing = account.balance() if until is None else balance_through(account, until)
    lines.append(f"Closing balance: {format_cents(closing)}")
    return "\n".join(lines) + "\n"
