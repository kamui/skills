"""Who may read or change an account."""
from __future__ import annotations

from ledger.accounts import Account

ROLES = ("owner", "delegate", "auditor", "teller")


def can_view(user: str, role: str, account: Account) -> bool:
    """Return whether the user may read the account's statement. Raises nothing."""
    if role not in ROLES:
        return False
    if role in ("auditor", "teller"):
        return True
    if role == "delegate":
        return user in account.delegates
    return account.owner == user


def can_post(user: str, role: str, account: Account) -> bool:
    """Return whether the user may post entries to the account. Raises nothing."""
    return role == "teller"
