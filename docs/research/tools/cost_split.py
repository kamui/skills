#!/usr/bin/env python3
"""Split a research run's harness-reported tokens into the review payload,
the research report, and the rest, and print the production-shaped figure.

A production review emits the review payload and nothing else. A research
run also writes a research report (verifier prompts, verbatim reports, the
full ledger, specific answers), and the harness-reported total includes the
output tokens spent on it. This script subtracts the report so cost
comparisons between arms use production-shaped figures. It does mechanical
arithmetic only; which file is the payload and which is the report is the run
author's call, made when the run writes them.

Usage::

    python3 docs/research/tools/cost_split.py \\
        --harness-total 281400 \\
        --payload <target>/<arm>-seed<n>-payload.md \\
        --report <target>/<arm>-seed<n>-run.md \\
        [--instruction-load N] [--repository-reads N] [--private-records N] \\
        [--payload-tokens N] [--report-tokens N] [--bytes-per-token 4] \\
        [--harness-note "primary not metered"] [--row "<label>"]

    python3 docs/research/tools/cost_split.py --header
    python3 docs/research/tools/cost_split.py --self-test

By default the payload and report are converted from their byte sizes at
``--bytes-per-token`` (4, the stated approximation). Pass ``--payload-tokens``
and ``--report-tokens`` when the harness exposes the real output-token counts;
the printout then labels those cells ``metered`` instead of ``est.``. The
other three parts of the split (instruction load, repository reads, private
records) are self-reported and optional; an omitted part prints as ``not
reported`` and is excluded from the arithmetic. Everything not attributed to
a reported part prints as ``unattributed``.

Output: a labelled block for the run document, or with ``--row`` one
Markdown table row in the column order of the holdout ``comparison-data.md``
cost table. ``--header`` prints that table's header from the same column
list, so the header and the rows cannot diverge. ``--harness-note`` appends a
qualifier to the harness-total cell in both forms; use it to mark a run whose
primary the harness did not meter, so the row reads as a lower bound without
hand-editing the pasted line.

Exit codes: ``0`` success; ``1`` the figures are inconsistent (the research
report, or the sum of the reported parts, exceeds the harness total), one
line per violation on stdout; ``2`` a file cannot be read or an argument is
not a valid number, with the reason on stderr.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from typing import Optional

COLUMNS = (
    "Run",
    "Harness total",
    "Instruction load",
    "Repository reads",
    "Private records",
    "Review payload",
    "Research report",
    "Production-shaped",
)


def positive_float(text: str) -> float:
    try:
        value = float(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"not a number: {text!r}") from exc
    if value <= 0:
        raise argparse.ArgumentTypeError(f"must be greater than zero: {text!r}")
    return value


def non_negative_int(text: str) -> int:
    try:
        value = int(text.replace(",", "").replace("_", ""))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"not a whole number: {text!r}") from exc
    if value < 0:
        raise argparse.ArgumentTypeError(f"must not be negative: {text!r}")
    return value


def fmt(value: int) -> str:
    return f"{value:,}"


def harness_cell(total: int, note: Optional[str]) -> str:
    return fmt(total) if not note else f"{fmt(total)} ({note})"


def table_row(cells) -> str:
    return "| " + " | ".join(cells) + " |"


def header_lines() -> list[str]:
    return [table_row(COLUMNS), table_row("---" for _ in COLUMNS)]


def file_bytes(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError as exc:
        raise SystemExit(f"cost_split: cannot read {path}: {exc.strerror}")


class Part:
    """One measured file: its byte size and its token count, metered or estimated."""

    def __init__(self, size: int, tokens: Optional[int], bytes_per_token: float) -> None:
        self.size = size
        self.metered = tokens is not None
        self.tokens = tokens if tokens is not None else round(size / bytes_per_token)
        self.bytes_per_token = bytes_per_token

    def describe(self) -> str:
        if self.metered:
            return f"{fmt(self.size)} bytes, metered"
        rate = f"{self.bytes_per_token:g}"
        return f"{fmt(self.size)} bytes at {rate} bytes/token, est."


def compute(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    """Return (output lines, violation lines)."""
    payload = Part(file_bytes(args.payload), args.payload_tokens, args.bytes_per_token)
    report = Part(file_bytes(args.report), args.report_tokens, args.bytes_per_token)
    total: int = args.harness_total

    optional = (
        ("instruction load", args.instruction_load),
        ("repository reads", args.repository_reads),
        ("private records", args.private_records),
    )
    reported_sum = payload.tokens + report.tokens + sum(v for _, v in optional if v is not None)
    production = total - report.tokens
    unattributed = total - reported_sum

    violations: list[str] = []
    if report.tokens > total:
        violations.append(
            f"research report ({fmt(report.tokens)} tokens) exceeds the harness total "
            f"({fmt(total)}); check which file is the report and whether the total is the whole run"
        )
    if reported_sum > total:
        violations.append(
            f"reported parts sum to {fmt(reported_sum)} tokens, more than the harness total "
            f"({fmt(total)}); the self-reported split double-counts something"
        )
    if violations:
        return [], violations

    share = (production / total * 100) if total else 0.0

    if args.row is not None:
        def cell(value: Optional[int]) -> str:
            return "—" if value is None else fmt(value)

        def part_cell(part: Part) -> str:
            kind = "metered" if part.metered else "est."
            return f"{fmt(part.tokens)} ({fmt(part.size)} B, {kind})"

        by_column = {
            "Run": args.row,
            "Harness total": harness_cell(total, args.harness_note),
            "Instruction load": cell(args.instruction_load),
            "Repository reads": cell(args.repository_reads),
            "Private records": cell(args.private_records),
            "Review payload": part_cell(payload),
            "Research report": part_cell(report),
            "Production-shaped": f"**{fmt(production)}**",
        }
        assert tuple(by_column) == COLUMNS, "row cells and COLUMNS disagree"
        return [table_row(by_column[name] for name in COLUMNS)], []

    width = 18
    source = "harness-reported" + (f"; {args.harness_note}" if args.harness_note else "")
    lines = [f"{'harness total':<{width}} {fmt(total):>10} tokens ({source})"]
    for label, value in optional:
        if value is None:
            lines.append(f"{label:<{width}} {'':>10} not reported")
        else:
            lines.append(f"{label:<{width}} {fmt(value):>10} tokens (self-reported)")
    lines.append(f"{'review payload':<{width}} {fmt(payload.tokens):>10} tokens ({payload.describe()})")
    lines.append(f"{'research report':<{width}} {fmt(report.tokens):>10} tokens ({report.describe()})")
    lines.append(
        f"{'unattributed':<{width}} {fmt(unattributed):>10} tokens (harness total minus every reported part)"
    )
    lines.append(
        f"{'production-shaped':<{width}} {fmt(production):>10} tokens "
        f"(harness total minus research report; {share:.1f}% of harness total)"
    )
    return lines, []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cost_split.py",
        description="Split a run's harness tokens into payload, report, and rest; print the production-shaped figure.",
    )
    parser.add_argument("--self-test", action="store_true", help="run the built-in checks and exit")
    parser.add_argument("--header", action="store_true", help="print the comparison-data.md cost table header and exit")
    parser.add_argument("--harness-total", type=non_negative_int, help="harness-reported tokens for the whole run")
    parser.add_argument("--payload", help="path to the review payload file")
    parser.add_argument("--report", help="path to the research report file")
    parser.add_argument("--instruction-load", type=non_negative_int, help="self-reported tokens spent reading skill files")
    parser.add_argument("--repository-reads", type=non_negative_int, help="self-reported tokens spent reading the repository")
    parser.add_argument("--private-records", type=non_negative_int, help="self-reported tokens spent on private records (ledger, notes)")
    parser.add_argument("--payload-tokens", type=non_negative_int, help="metered output tokens for the payload, if the harness exposes them")
    parser.add_argument("--report-tokens", type=non_negative_int, help="metered output tokens for the report, if the harness exposes them")
    parser.add_argument("--bytes-per-token", type=positive_float, default=4.0, help="conversion rate for the byte estimate (default 4)")
    parser.add_argument("--harness-note", metavar="TEXT", help="qualifier appended to the harness-total cell, e.g. 'primary not metered'")
    parser.add_argument("--row", metavar="LABEL", help="print one comparison-data.md table row labelled LABEL instead of the block")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.header:
        for line in header_lines():
            print(line)
        return 0
    missing = [name for name in ("harness_total", "payload", "report") if getattr(args, name) is None]
    if missing:
        parser.error("required: " + ", ".join("--" + m.replace("_", "-") for m in missing))
    try:
        lines, violations = compute(args)
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 2
    if violations:
        for line in violations:
            print(line)
        return 1
    for line in lines:
        print(line)
    return 0


# --- self-test -------------------------------------------------------------


def self_test() -> int:
    failures: list[str] = []
    script = os.path.abspath(__file__)

    def run(*extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, script, *extra], capture_output=True, text=True, encoding="utf-8"
        )

    def check(case: str, ok: bool, detail: str = "") -> None:
        if not ok:
            failures.append(f"{case}: {detail}".rstrip(": "))

    with tempfile.TemporaryDirectory() as tmp:
        payload = os.path.join(tmp, "payload.md")
        report = os.path.join(tmp, "report.md")
        with open(payload, "w", encoding="utf-8") as fh:
            fh.write("p" * 8_000)  # 2,000 tokens at 4 bytes/token
        with open(report, "w", encoding="utf-8") as fh:
            fh.write("r" * 60_000)  # 15,000 tokens at 4 bytes/token

        base = ["--harness-total", "280000", "--payload", payload, "--report", report]

        r = run(*base)
        check("estimate exits 0", r.returncode == 0, r.stderr)
        check("estimate payload", "review payload          2,000 tokens (8,000 bytes at 4 bytes/token, est.)" in r.stdout, r.stdout)
        check("estimate report", "research report        15,000 tokens (60,000 bytes at 4 bytes/token, est.)" in r.stdout, r.stdout)
        check("estimate production", "production-shaped     265,000 tokens (harness total minus research report; 94.6% of harness total)" in r.stdout, r.stdout)
        check("estimate unattributed", "unattributed          263,000 tokens" in r.stdout, r.stdout)
        check("estimate not reported", r.stdout.count("not reported") == 3, r.stdout)

        r = run(*base, "--instruction-load", "40,000", "--repository-reads", "150000", "--private-records", "30000")
        check("split exits 0", r.returncode == 0, r.stderr)
        check("split instruction load", "instruction load       40,000 tokens (self-reported)" in r.stdout, r.stdout)
        check("split unattributed", "unattributed           43,000 tokens" in r.stdout, r.stdout)
        check("split production unchanged", "production-shaped     265,000 tokens" in r.stdout, r.stdout)

        r = run(*base, "--payload-tokens", "2500", "--report-tokens", "18000")
        check("metered exits 0", r.returncode == 0, r.stderr)
        check("metered report", "research report        18,000 tokens (60,000 bytes, metered)" in r.stdout, r.stdout)
        check("metered production", "production-shaped     262,000 tokens" in r.stdout, r.stdout)

        r = run(*base, "--bytes-per-token", "3.5")
        check("rate exits 0", r.returncode == 0, r.stderr)
        check("rate report", "17,143 tokens (60,000 bytes at 3.5 bytes/token, est.)" in r.stdout, r.stdout)

        r = run(*base, "--row", "v5b seed 1", "--instruction-load", "40000")
        check("row exits 0", r.returncode == 0, r.stderr)
        expected = "| v5b seed 1 | 280,000 | 40,000 | — | — | 2,000 (8,000 B, est.) | 15,000 (60,000 B, est.) | **265,000** |"
        check("row content", r.stdout.strip() == expected, r.stdout)

        r = run(*base, "--harness-note", "primary not metered")
        check("note exits 0", r.returncode == 0, r.stderr)
        check("note in block", "harness total         280,000 tokens (harness-reported; primary not metered)" in r.stdout, r.stdout)

        r = run(*base, "--row", "v5b seed 2", "--harness-note", "primary not metered")
        check("note row exits 0", r.returncode == 0, r.stderr)
        check("note in row", r.stdout.startswith("| v5b seed 2 | 280,000 (primary not metered) | — |"), r.stdout)

        r = run("--header")
        check("header exits 0", r.returncode == 0, r.stderr)
        header = "| Run | Harness total | Instruction load | Repository reads | Private records | Review payload | Research report | Production-shaped |"
        check("header row", r.stdout.splitlines()[0] == header, r.stdout)
        check("header separator", r.stdout.splitlines()[1] == "| --- | --- | --- | --- | --- | --- | --- | --- |", r.stdout)
        check("header cell count matches row", header.count("|") == expected.count("|"), f"{header} vs {expected}")

        r = run("--harness-total", "10000", "--payload", payload, "--report", report)
        check("report exceeds total exits 1", r.returncode == 1, f"rc={r.returncode} {r.stderr}")
        check("report exceeds total message", "exceeds the harness total" in r.stdout, r.stdout)

        r = run(*base, "--instruction-load", "200000", "--repository-reads", "100000")
        check("sum exceeds total exits 1", r.returncode == 1, f"rc={r.returncode} {r.stderr}")
        check("sum exceeds total message", "double-counts" in r.stdout, r.stdout)

        r = run("--harness-total", "280000", "--payload", os.path.join(tmp, "absent.md"), "--report", report)
        check("missing file exits 2", r.returncode == 2, f"rc={r.returncode}")
        check("missing file names it", "absent.md" in r.stderr, r.stderr)

        r = run("--harness-total", "lots", "--payload", payload, "--report", report)
        check("bad total exits 2", r.returncode == 2, f"rc={r.returncode}")

        r = run(*base, "--bytes-per-token", "0")
        check("zero rate exits 2", r.returncode == 2, f"rc={r.returncode}")

        r = run("--payload", payload)
        check("missing required exits 2", r.returncode == 2, f"rc={r.returncode}")

    for line in failures:
        print(line)
    if not failures:
        print("cost_split.py self-test: all cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
