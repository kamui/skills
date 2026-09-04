#!/usr/bin/env python3
"""Build a verifier prompt from machine-readable finder report blocks.

Purpose: render the fresh-context verifier's prompt from the two finder
reports, carrying every candidate field except `support` and only those
acquitted ledger rows that relate to a candidate, so the verifier never sees
the finder's own demonstrations.

Usage:
    python3 scripts/build_verifier_prompt.py --brief <absolute path>
        --repo <path> --base-sha <sha> --head-sha <sha> --merge-base <sha>
        --code <report> --requirements <report>

The prompt is written to stdout; violations are written to stdout too, one per
line, and the reason for an unreadable input to stderr.

Exit codes:
    0  the prompt was written
    1  a report violates the finding format (one violation per line on stdout)
    2  the brief or a finder report could not be read

Input schema: each finder report carries a fenced ```candidates block of
`### Candidate` sections whose fields are `id`, `axis`, `anchor`, `fix`,
`title`, `claim`, `support`, `trigger`, `priority`, `action`, and a fenced
```ledger block of `claim | probe | evidence | disposition` rows.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

CANDIDATE_FIELDS = (
    "id",
    "axis",
    "anchor",
    "fix",
    "title",
    "claim",
    "support",
    "trigger",
    "priority",
    "action",
)
VERIFIER_FIELDS = tuple(field for field in CANDIDATE_FIELDS if field != "support")
FIELD_RE = re.compile(
    r"^(?:-\s+)?(?:\*\*)?("
    + "|".join(CANDIDATE_FIELDS)
    + r")(?:\*\*)?:[ \t]?(.*)$"
)
SUPPORT_LABEL_RE = re.compile(
    r"^[ \t]*(?:-\s+)?(?:\*\*)?support(?:\*\*)?:",
    re.IGNORECASE | re.MULTILINE,
)
FIELD_LIKE_RE = re.compile(r"^(?:-\s+)?(?:\*\*)?[A-Za-z][A-Za-z0-9_-]*(?:\*\*)?:")
HEADING_RE = re.compile(r"^### Candidate(?:\s+.*)?$")
LOCATION_RE = re.compile(r"(?P<path>[A-Za-z0-9_.@+-]+(?:/[A-Za-z0-9_.@+-]+)*):\d+(?:-\d+)?")
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
IDENTIFIER_RE = re.compile(
    r"\b[A-Za-z_][A-Za-z0-9_]*(?:(?:::|\.)[A-Za-z_][A-Za-z0-9_]*)*(?:\(\))?\b"
)


class InputError(OSError):
    """An argument named an input the script could not read."""


class ReportError(ValueError):
    """A finder report is not in the machine-readable shape."""


@dataclass
class Candidate:
    label: str
    fields: dict[str, str]


@dataclass
class LedgerRow:
    axis: str
    line: str
    claim: str
    evidence: str


def fenced_blocks(markdown: str, info: str) -> list[str]:
    lines = markdown.splitlines()
    blocks: list[str] = []
    index = 0
    opening = re.compile(rf"^[ \t]{{0,3}}(?P<fence>`{{3,}}|~{{3,}}){re.escape(info)}[ \t]*$")
    while index < len(lines):
        match = opening.match(lines[index])
        if not match:
            index += 1
            continue
        fence = match.group("fence")
        closing = re.compile(
            rf"^[ \t]{{0,3}}{re.escape(fence[0])}{{{len(fence)},}}[ \t]*$"
        )
        start = index + 1
        index = start
        while index < len(lines) and not closing.match(lines[index]):
            index += 1
        if index == len(lines):
            raise ReportError(f"unterminated {info} block")
        blocks.append("\n".join(lines[start:index]))
        index += 1
    return blocks


def parse_candidate_section(label: str, lines: list[str]) -> Candidate:
    """Split a candidate section into its fields, keeping continuation text verbatim.

    The fields appear once each, in `CANDIDATE_FIELDS` order, so a line opens a
    field only when it names the next one still expected. Any other line belongs
    to the field above it, including a line that looks like `name: value` — a
    `claim` quoting configuration or code is entitled to a column-zero
    `priority: high` without it being read as the candidate's own routing.
    """
    fields: dict[str, str] = {}
    current: str | None = None
    expected = list(CANDIDATE_FIELDS)
    for line in lines:
        match = FIELD_RE.match(line)
        if match and expected and match.group(1) == expected[0]:
            field, value = match.groups()
            fields[field] = value
            current = field
            expected.pop(0)
            continue
        if current is None:
            if not line.strip():
                continue
            if match or FIELD_LIKE_RE.match(line):
                raise ReportError(
                    f"{label} opens with {line.split(':', 1)[0].strip()}, expected {expected[0]}"
                )
            raise ReportError(f"{label} has text before its first field")
        fields[current] += "\n" + line

    fields = {name: value.rstrip() for name, value in fields.items()}
    for field in CANDIDATE_FIELDS:
        if field not in fields:
            raise ReportError(f"{label} is missing {field}")
    for field in VERIFIER_FIELDS:
        if not fields[field].strip():
            raise ReportError(f"{label} has an empty {field}")
    return Candidate(label=label, fields=fields)


def parse_candidates(report: str, axis_label: str) -> list[Candidate]:
    blocks = fenced_blocks(report, "candidates")
    if len(blocks) != 1:
        raise ReportError(
            f"{axis_label} report must contain exactly one candidates block; found {len(blocks)}"
        )
    block = blocks[0]
    if not block.strip() or block.strip().casefold() in {
        "none",
        "none.",
        "no candidates",
        "no candidates.",
    }:
        return []

    candidates: list[Candidate] = []
    heading: str | None = None
    section: list[str] = []
    for line in block.splitlines():
        if HEADING_RE.match(line):
            if heading is not None:
                candidates.append(parse_candidate_section(heading, section))
            heading = f"{axis_label} {line[4:].strip()}"
            section = []
        elif heading is None:
            if line.strip():
                raise ReportError(
                    f"{axis_label} candidates block has text before its first Candidate heading"
                )
        else:
            section.append(line)
    if heading is None:
        raise ReportError(f"{axis_label} candidates block has no Candidate heading")
    candidates.append(parse_candidate_section(heading, section))
    return candidates


def parse_ledger(report: str, axis_label: str) -> list[LedgerRow]:
    blocks = fenced_blocks(report, "ledger")
    if not blocks:
        return []
    if len(blocks) != 1:
        raise ReportError(
            f"{axis_label} report must contain at most one ledger block; found {len(blocks)}"
        )
    rows: list[LedgerRow] = []
    for row_number, line in enumerate(blocks[0].splitlines(), start=1):
        if not line.strip():
            continue
        fields = [field.strip() for field in line.split("|")]
        if len(fields) != 4:
            raise ReportError(f"{axis_label} ledger row {row_number} does not have four fields")
        claim, _, evidence, disposition = fields
        if disposition == "acquitted":
            rows.append(
                LedgerRow(
                    axis=axis_label,
                    line=line,
                    claim=claim,
                    evidence=evidence,
                )
            )
    return rows


def paths(text: str) -> set[str]:
    """Every repository-relative file path cited as a `path:line` coordinate.

    Paths are normalized to their repository-relative form, so a `./` prefix or
    a redundant `.` segment compares equal to the plain path. They are compared
    as whole file identities and never by suffix: a repository holding both
    `foo.py` and `src/foo.py` has two files,
    and treating a row about one as evidence about the other is exactly the
    unrelated work the related-only filter exists to keep out of the verifier.
    """
    return {
        PurePosixPath(match.group("path")).as_posix()
        for match in LOCATION_RE.finditer(text)
    }


def is_type_name(name: str) -> bool:
    """A PascalCase token with no member access reads as a class or type name.

    Relatedness keys on a shared function, branch, state field, or lock; two
    claims that share only a type name are not related.
    """
    return (
        name[0].isupper()
        and not name.isupper()
        and "_" not in name
        and "." not in name
        and "::" not in name
    )


def symbolic_names(text: str) -> set[str]:
    names: set[str] = set()
    for span in CODE_SPAN_RE.findall(text):
        if "/" not in span and not LOCATION_RE.search(span):
            names.add(span.removesuffix("()"))
    for token in IDENTIFIER_RE.findall(text):
        normalized = token.removesuffix("()")
        if (
            "_" in normalized
            or "::" in normalized
            or "." in normalized
            or any(character.isupper() for character in normalized[1:])
        ):
            names.add(normalized)
            if "." in normalized:
                names.add(normalized.rsplit(".", 1)[-1])
            if "::" in normalized:
                names.add(normalized.rsplit("::", 1)[-1])
    return {name for name in names if len(name) >= 4 and not is_type_name(name)}


def is_related(row: LedgerRow, candidates: list[Candidate]) -> bool:
    row_paths = paths(row.evidence)
    row_names = symbolic_names(row.claim)
    for candidate in candidates:
        candidate_paths = paths(
            candidate.fields["anchor"] + "\n" + candidate.fields["fix"]
        )
        if row_paths & candidate_paths:
            return True
        if row_names & symbolic_names(candidate.fields["claim"]):
            return True
    return False


def render_candidate(index: int, candidate: Candidate) -> str:
    lines = [f"### Candidate {index}"]
    for field in VERIFIER_FIELDS:
        value_lines = candidate.fields[field].splitlines() or [""]
        lines.append(f"{field}: {value_lines[0]}")
        lines.extend(value_lines[1:])
    return "\n".join(lines)


def build(args: argparse.Namespace) -> str:
    try:
        brief = Path(args.brief).read_text(encoding="utf-8")
    except OSError as error:
        raise InputError(f"cannot read verifier brief {args.brief}: {error}") from error

    reports: list[tuple[str, str]] = []
    for axis_label, path in (("Code", args.code), ("Requirements", args.requirements)):
        try:
            reports.append((axis_label, Path(path).read_text(encoding="utf-8")))
        except OSError as error:
            raise InputError(f"cannot read {axis_label} report {path}: {error}") from error

    candidates: list[Candidate] = []
    ledger_rows: list[LedgerRow] = []
    for axis_label, report in reports:
        candidates.extend(parse_candidates(report, axis_label))
        ledger_rows.extend(parse_ledger(report, axis_label))

    sections = [
        f"Verifier brief: `{args.brief}`\n\nRepository: `{args.repo}`",
        "## Pinned run identity\n\n"
        f"- base SHA: `{args.base_sha}`\n"
        f"- head SHA: `{args.head_sha}`\n"
        f"- merge-base: `{args.merge_base}`",
    ]
    if candidates:
        sections.append(
            "## Candidates\n\n"
            + "\n\n".join(
                render_candidate(index, candidate)
                for index, candidate in enumerate(candidates, start=1)
            )
        )
    else:
        sections.append("## Candidates\n\nNone.")

    related = []
    if re.search(r"^## Related acquittals[ \t]*$", brief, re.MULTILINE):
        related = [row for row in ledger_rows if is_related(row, candidates)]
    if related:
        rows_by_axis: dict[str, list[str]] = {}
        for row in related:
            rows_by_axis.setdefault(row.axis, []).append(row.line)
        related_sections = ["## Related acquitted ledger rows"]
        for axis_label, rows in rows_by_axis.items():
            related_sections.append(f"### {axis_label}\n\n" + "\n".join(rows))
        sections.append("\n\n".join(related_sections))

    output = "\n\n".join(sections) + "\n"
    if SUPPORT_LABEL_RE.search(output):
        raise ReportError("private field text survived into the verifier prompt")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write a fresh-context verifier prompt from two finder reports."
    )
    parser.add_argument("--brief", required=True, help="absolute path to references/verify.md")
    parser.add_argument("--repo", required=True, help="path to the repository under review")
    parser.add_argument("--base-sha", required=True, help="pinned base branch commit")
    parser.add_argument("--head-sha", required=True, help="pinned pull-request head commit")
    parser.add_argument("--merge-base", required=True, help="pinned comparison merge-base")
    parser.add_argument("--code", required=True, help="Code finder report")
    parser.add_argument("--requirements", required=True, help="Requirements finder report")
    args = parser.parse_args()

    if not Path(args.brief).is_absolute():
        parser.error("--brief must be an absolute path")

    try:
        output = build(args)
    except InputError as error:
        print(f"build_verifier_prompt: {error}", file=sys.stderr)
        return 2
    except ReportError as error:
        print(f"build_verifier_prompt: {error}")
        return 1
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
