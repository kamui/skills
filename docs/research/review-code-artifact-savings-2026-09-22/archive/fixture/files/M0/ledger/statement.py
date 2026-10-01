"""Plain-text account statements."""
from __future__ import annotations

from ledger.accounts import Account


def format_cents(cents: int) -> str:
    """Render cents as a signed decimal amount such as -12.50. Raises nothing."""
    sign = "-" if cents < 0 else ""
    whole, part = divmod(abs(cents), 100)
    return f"{sign}{whole}.{part:02d}"


def statement_rows(account: Account) -> list[tuple[str, str, str, str]]:
    """Return (date, description, amount, running balance) rows in posting order. Raises nothing."""
    rows = []
    running = 0
    for entry in account.entries:
        running += entry.amount
        rows.append((entry.day.isoformat(), entry.description, format_cents(entry.amount), format_cents(running)))
    return rows


def render_statement(account: Account) -> str:
    """Render a fixed-width statement ending with the closing balance. Raises nothing."""
    lines = [f"Statement for {account.number} ({account.owner})"]
    for day, description, amount, running in statement_rows(account):
        lines.append(f"{day}  {description:<30.30}  {amount:>12}  {running:>12}")
    lines.append(f"Closing balance: {format_cents(account.balance())}")
    return "\n".join(lines) + "\n"
