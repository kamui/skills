"""Command line: python3 -m ledger.cli statement FILE ACCOUNT [--since DAY] [--until DAY]."""
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


def iso_day(text: str) -> date:
    """Parse YYYY-MM-DD. Raises argparse.ArgumentTypeError for anything else."""
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a YYYY-MM-DD date: {text!r}") from None


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser. Raises nothing."""
    parser = argparse.ArgumentParser(prog="ledger")
    commands = parser.add_subparsers(dest="command", required=True)
    statement = commands.add_parser("statement", help="print an account statement")
    statement.add_argument("file")
    statement.add_argument("account")
    statement.add_argument("--since", type=iso_day, help="first day to include, YYYY-MM-DD")
    statement.add_argument("--until", type=iso_day, help="last day to include, YYYY-MM-DD")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command line. Returns 2 on unreadable input, an unknown account, or an empty date range."""
    args = build_parser().parse_args(argv)
    if args.since is not None and args.until is not None and args.since > args.until:
        print("ledger: --since is after --until", file=sys.stderr)
        return 2
    try:
        ledger = load(args.file)
        sys.stdout.write(render_statement(ledger.get(args.account), args.since, args.until))
    except (OSError, ValueError, KeyError) as error:
        print(f"ledger: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
