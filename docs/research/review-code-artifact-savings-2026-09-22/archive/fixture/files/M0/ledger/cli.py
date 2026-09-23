"""Command line: python3 -m ledger.cli statement FILE ACCOUNT."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from ledger.accounts import Ledger
from ledger.statement import render_statement


def load(path: str) -> Ledger:
    """Load a ledger from JSON. Raises OSError, ValueError, KeyError, or LedgerError on bad input."""
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    ledger = Ledger()
    for item in data["accounts"]:
        ledger.open(item["number"], item["owner"])
        for day, description, cents in item.get("entries", []):
            ledger.post(item["number"], date.fromisoformat(day), description, cents)
    return ledger


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser. Raises nothing."""
    parser = argparse.ArgumentParser(prog="ledger")
    commands = parser.add_subparsers(dest="command", required=True)
    statement = commands.add_parser("statement", help="print an account statement")
    statement.add_argument("file")
    statement.add_argument("account")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command line. Returns 2 on unreadable input or an unknown account."""
    args = build_parser().parse_args(argv)
    try:
        ledger = load(args.file)
        sys.stdout.write(render_statement(ledger.get(args.account)))
    except (OSError, ValueError, KeyError) as error:
        print(f"ledger: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
