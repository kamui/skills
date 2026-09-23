"""Accounts and entries. Amounts are integer cents."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


class LedgerError(ValueError):
    """Raised when an operation would break a ledger rule."""


@dataclass(frozen=True)
class Entry:
    day: date
    description: str
    amount: int  # cents; credits positive, debits negative


@dataclass
class Account:
    number: str
    owner: str
    entries: list[Entry] = field(default_factory=list)
    delegates: set[str] = field(default_factory=set)

    def balance(self) -> int:
        """Return the balance in cents. Raises nothing."""
        return sum(entry.amount for entry in self.entries)


class Ledger:
    """Accounts keyed by number."""

    def __init__(self) -> None:
        self.accounts: dict[str, Account] = {}

    def open(self, number: str, owner: str) -> Account:
        """Open an account. Raises LedgerError when the number is taken."""
        if number in self.accounts:
            raise LedgerError(f"account {number} already exists")
        account = Account(number, owner)
        self.accounts[number] = account
        return account

    def get(self, number: str) -> Account:
        """Return an account. Raises LedgerError when it does not exist."""
        try:
            return self.accounts[number]
        except KeyError:
            raise LedgerError(f"no account {number}") from None

    def grant(self, number: str, user: str, delegate: str) -> None:
        """Let delegate read the account's statement. Raises LedgerError unless user owns the account."""
        account = self.get(number)
        if account.owner != user:
            raise LedgerError(f"{user} does not own {number}")
        account.delegates.add(delegate)

    def revoke(self, number: str, user: str, delegate: str) -> None:
        """Withdraw a delegate's access. Raises LedgerError unless user owns the account."""
        account = self.get(number)
        if account.owner != user:
            raise LedgerError(f"{user} does not own {number}")
        account.delegates.discard(delegate)

    def post(self, number: str, day: date, description: str, amount: int) -> Entry:
        """Post one entry. Raises LedgerError for a zero amount, an overdraft, or an unknown account."""
        if not isinstance(amount, int) or amount == 0:
            raise LedgerError("amount must be a nonzero integer number of cents")
        account = self.get(number)
        if account.balance() + amount < 0:
            raise LedgerError(f"posting would overdraw {number}")
        entry = Entry(day, description, amount)
        account.entries.append(entry)
        return entry

    def transfer(self, source: str, target: str, day: date, amount: int) -> None:
        """Move a positive amount between two accounts atomically.

        Raises LedgerError for a non-positive amount, the same account on both
        sides, an unknown account, or an overdraft of the source.
        """
        if not isinstance(amount, int) or amount <= 0:
            raise LedgerError("transfer amount must be a positive integer number of cents")
        if source == target:
            raise LedgerError("cannot transfer to the same account")
        debit = self.get(source)
        credit = self.get(target)
        if debit.balance() < amount:
            raise LedgerError(f"transfer would overdraw {source}")
        debit.entries.append(Entry(day, f"transfer to {target}", -amount))
        credit.entries.append(Entry(day, f"transfer from {source}", amount))
