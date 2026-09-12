#!/usr/bin/env python3
"""Build a verifier prompt from machine-readable finder report blocks.

Purpose: render the fresh-context verifier's prompt from the two finder
reports and optional test-suite result summaries, carrying every candidate
field except `support` and only those acquitted ledger rows that relate to a
candidate, so the verifier never sees the finder's own demonstrations. With
`--packet` it also writes the accounting packet: every candidate id the
verifier owes a verdict and every acquittal row id it owes a ruling, which
`account_verifier_return.py` checks the return against.

Usage:
    python3 scripts/build_verifier_prompt.py --brief <absolute path>
        --repo <path> --base-sha <sha> --head-sha <sha> --merge-base <sha>
        --code <report> --requirements <report> [--suite-results <path>]
        [--prior <report>] [--packet <path>]

The prompt is written to stdout; violations are written to stdout too, one per
line, and the reason for an unreadable input to stderr.

Exit codes:
    0  the prompt was written (and the packet, when --packet was given)
    1  a report violates the finding format (one violation per line on stdout)
    2  the brief, a finder report, or the packet path could not be read or
       written

Input schema: each finder report carries a fenced ```candidates block of
`### Candidate` sections whose fields are `id`, `axis`, `kind`, `anchor`,
`fix`, `title`, `claim`, `support`, `trigger`, `impact`, `change`,
`priority`, `action`, once each in that order, every field line at column
zero, and a fenced ```ledger block of
`id | kind | claim | probe | evidence | disposition` rows. A line quoted
inside a field that begins with one of those labels is indented. `anchor`,
`fix`, and a row's evidence are whole `path:line` coordinates or file paths,
which may contain spaces. A candidate id starts with its axis (`code/` or
`requirements/`) and is unique across both reports; a ledger row id is the
axis name, a dash, and a positive integer (`code-3`, `requirements-1`),
unique within its report. `kind` is one of bug, concurrency, invariant,
security, performance, maintainability, requirement; a Requirements
candidate or row uses `requirement` and a Code one uses the other six.
When supplied, suite-results is a UTF-8 file containing one result-summary
line per suite. On a re-review, `--prior` names a report holding one
```candidates block of the prior findings whose fate turns on the code, in
the same section grammar with `support` left empty; they render under their
own heading and join the packet as candidates.
The packet is JSON: {"candidates": [{"id", "axis"}...],
"acquittals": [{"id", "axis", "evidence"}...]}.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

CANDIDATE_FIELDS = (
    "id",
    "axis",
    "kind",
    "anchor",
    "fix",
    "title",
    "claim",
    "support",
    "trigger",
    "impact",
    "change",
    "priority",
    "action",
)
VERIFIER_FIELDS = tuple(field for field in CANDIDATE_FIELDS if field != "support")
KINDS = (
    "bug",
    "concurrency",
    "invariant",
    "security",
    "performance",
    "maintainability",
    "requirement",
)
LEDGER_FIELD_COUNT = 6
AXES = ("Code", "Requirements")
KINDS_BY_AXIS = {"Code": KINDS[:-1], "Requirements": ("requirement",)}
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
COORDINATE_RE = re.compile(r"^(?P<path>.+?):\d+(?:-\d+)?$")
BARE_PATH_RE = re.compile(r"^(?P<path>[^\s`|()]*(?:/|\.(?=[^\s`|()]))[^\s`|()]*)$")
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
IDENTIFIER_RE = re.compile(
    r"\b[A-Za-z_][A-Za-z0-9_]*(?:(?:::|\.)[A-Za-z_][A-Za-z0-9_]*)*(?:\(\))?\b"
)
ROW_ID_RE = re.compile(r"^(?P<axis>code|requirements)-[1-9][0-9]*$")
CANDIDATE_ID_RE = re.compile(r"^(?P<axis>code|requirements)/\S+$")


class InputError(OSError):
    """An argument named an input the script could not read or write."""


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
    id: str
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

    A column-zero line naming a candidate field is always a field line, and the
    fields appear once each in `CANDIDATE_FIELDS` order, so the one it names
    must be the next field still expected; a column-zero label out of that
    order is refused rather than guessed at, because the parser cannot tell a
    quoted `support: enabled` from the candidate's own routing. Every other
    line continues the field above it verbatim, so a `claim` quotes a line that
    begins with a field label by indenting it.
    """
    fields: dict[str, str] = {}
    current: str | None = None
    expected = list(CANDIDATE_FIELDS)
    for line in lines:
        match = FIELD_RE.match(line)
        if match:
            field, value = match.groups()
            if expected and field == expected[0]:
                fields[field] = value
                current = field
                expected.pop(0)
                continue
            if field in fields:
                raise ReportError(
                    f"{label} has a second column-zero {field} line inside {current}; "
                    "indent it to quote it"
                )
            raise ReportError(
                f"{label} is missing {expected[0]} before {field}, or quotes a column-zero "
                f"{field} line inside {current} that should be indented"
            )
        if current is None:
            if not line.strip():
                continue
            if FIELD_LIKE_RE.match(line):
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
    axis = fields["axis"].strip()
    if axis not in AXES:
        raise ReportError(f"{label} has axis {axis!r}; expected Code or Requirements")
    kind = fields["kind"].strip()
    if kind not in KINDS:
        raise ReportError(f"{label} has kind {kind!r}; expected one of {', '.join(KINDS)}")
    if kind not in KINDS_BY_AXIS[axis]:
        raise ReportError(
            f"{label} has kind {kind!r}; a {axis} candidate uses "
            + ", ".join(KINDS_BY_AXIS[axis])
        )
    candidate_id = fields["id"].strip()
    id_match = CANDIDATE_ID_RE.match(candidate_id)
    if not id_match or id_match.group("axis") != axis.lower():
        raise ReportError(
            f"{label} has id {candidate_id!r}; a {axis} candidate id starts with {axis.lower()}/"
        )
    return Candidate(label=label, fields=fields)


def parse_candidates(report: str, axis_label: str) -> list[Candidate]:
    """Every candidate in the report's single candidates block, in order.

    `axis_label` names the report for messages; a `Prior` report may carry
    candidates of either axis, and the axis check is per section.
    """
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
    if axis_label in AXES:
        for candidate in candidates:
            if candidate.fields["axis"].strip() != axis_label:
                raise ReportError(
                    f"{candidate.label} carries axis {candidate.fields['axis'].strip()!r} "
                    f"inside the {axis_label} report"
                )
    seen: dict[str, str] = {}
    for candidate in candidates:
        candidate_id = candidate.fields["id"].strip()
        if candidate_id in seen:
            raise ReportError(
                f"{candidate.label} repeats id {candidate_id!r} already used by {seen[candidate_id]}"
            )
        seen[candidate_id] = candidate.label
    return candidates


def parse_ledger(report: str, axis_label: str) -> list[LedgerRow]:
    """Every acquitted ledger row, with its per-run id checked for shape and uniqueness.

    A row has six fields. The four-field grammar that preceded ids and kinds
    is refused by count, naming the old grammar, so an old row cannot parse
    as a new one with its claim read as an id.
    """
    blocks = fenced_blocks(report, "ledger")
    if not blocks:
        return []
    if len(blocks) != 1:
        raise ReportError(
            f"{axis_label} report must contain at most one ledger block; found {len(blocks)}"
        )
    rows: list[LedgerRow] = []
    seen_ids: set[str] = set()
    for row_number, line in enumerate(blocks[0].splitlines(), start=1):
        if not line.strip():
            continue
        fields = [field.strip() for field in line.split("|")]
        if len(fields) != LEDGER_FIELD_COUNT:
            hint = " (the four-field row grammar has no id or kind)" if len(fields) == 4 else ""
            raise ReportError(
                f"{axis_label} ledger row {row_number} has {len(fields)} fields, expected "
                f"{LEDGER_FIELD_COUNT} (id | kind | claim | route | evidence | disposition){hint}"
            )
        row_id, kind, claim, _, evidence, disposition = fields
        id_match = ROW_ID_RE.match(row_id)
        if not id_match or id_match.group("axis") != axis_label.lower():
            raise ReportError(
                f"{axis_label} ledger row {row_number} has id {row_id!r}; expected "
                f"{axis_label.lower()}-<n>"
            )
        if row_id in seen_ids:
            raise ReportError(f"{axis_label} ledger row {row_number} repeats id {row_id!r}")
        seen_ids.add(row_id)
        if kind not in KINDS:
            raise ReportError(
                f"{axis_label} ledger row {row_number} has kind {kind!r}; expected one of "
                + ", ".join(KINDS)
            )
        if kind not in KINDS_BY_AXIS[axis_label]:
            raise ReportError(
                f"{axis_label} ledger row {row_number} has kind {kind!r}; a {axis_label} row uses "
                + ", ".join(KINDS_BY_AXIS[axis_label])
            )
        if disposition == "acquitted":
            rows.append(
                LedgerRow(
                    axis=axis_label,
                    line=line,
                    id=row_id,
                    claim=claim,
                    evidence=evidence,
                )
            )
    return rows


def coordinate_path(text: str) -> str | None:
    """The file a whole `path:line` coordinate or bare file path names, or None.

    The text is the complete field or code span, so the path runs from its
    first character to the final `:line`, spaces included: `src/My File.py:14`
    names `src/My File.py`, never `File.py`. A bare path counts when it has no
    whitespace and carries a `/` or a `.`, which is what lets a `fix` name the
    file a missing requirement belongs in.
    """
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] == "`":
        text = text[1:-1].strip()
    match = COORDINATE_RE.match(text) or BARE_PATH_RE.match(text)
    if not match:
        return None
    return PurePosixPath(match.group("path")).as_posix()


def paths(text: str) -> set[str]:
    """Every repository-relative file identity a field cites.

    The field is read as one coordinate first, and failing that each of its
    code spans is; a coordinate is never picked out of running prose, because
    prose gives no boundary for a path containing spaces. Paths are normalized
    to their repository-relative form — a `./` prefix, a redundant `.` segment,
    or a doubled slash compares equal to the plain path — and then compared as
    whole file identities, never by suffix: a repository holding both `foo.py`
    and `src/foo.py` has two files, and treating a row about one as evidence
    about the other is exactly the unrelated work the related-only filter
    exists to keep out of the verifier.
    """
    whole = coordinate_path(text)
    if whole is not None:
        return {whole}
    found = {coordinate_path(span) for span in CODE_SPAN_RE.findall(text)}
    found.discard(None)
    return found


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
        if "/" not in span and coordinate_path(span) is None:
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
        candidate_paths = paths(candidate.fields["anchor"]) | paths(candidate.fields["fix"])
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


def read_input(path: str, description: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as error:
        raise InputError(f"cannot read {description} {path}: {error}") from error


def build(args: argparse.Namespace) -> tuple[str, dict]:
    brief = read_input(args.brief, "verifier brief")

    reports: list[tuple[str, str]] = []
    for axis_label, path in (("Code", args.code), ("Requirements", args.requirements)):
        reports.append((axis_label, read_input(path, f"{axis_label} report")))

    suite_results = None
    if args.suite_results:
        suite_results = read_input(args.suite_results, "suite results")

    prior_report = None
    if args.prior:
        prior_report = read_input(args.prior, "prior findings report")

    candidates: list[Candidate] = []
    ledger_rows: list[LedgerRow] = []
    for axis_label, report in reports:
        candidates.extend(parse_candidates(report, axis_label))
        ledger_rows.extend(parse_ledger(report, axis_label))

    prior: list[Candidate] = []
    if prior_report is not None:
        prior = parse_candidates(prior_report, "Prior")

    seen: dict[str, str] = {}
    for candidate in candidates + prior:
        candidate_id = candidate.fields["id"].strip()
        if candidate_id in seen:
            raise ReportError(
                f"{candidate.label} repeats id {candidate_id!r} already used by {seen[candidate_id]}"
            )
        seen[candidate_id] = candidate.label

    sections = [
        f"Verifier brief: `{args.brief}`\n\nRepository: `{args.repo}`",
        "## Pinned run identity\n\n"
        f"- base SHA: `{args.base_sha}`\n"
        f"- head SHA: `{args.head_sha}`\n"
        f"- merge-base: `{args.merge_base}`",
    ]
    if suite_results is not None:
        sections.append("## Test suite results\n\n" + suite_results.rstrip())
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
    if prior:
        sections.append(
            "## Prior findings\n\n"
            "Each is a claim about the current code at its recorded fix site.\n\n"
            + "\n\n".join(
                render_candidate(index, candidate)
                for index, candidate in enumerate(prior, start=len(candidates) + 1)
            )
        )

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

    packet = {
        "candidates": [
            {"id": candidate.fields["id"].strip(), "axis": candidate.fields["axis"].strip()}
            for candidate in candidates + prior
        ],
        "acquittals": [
            {"id": row.id, "axis": row.axis, "evidence": row.evidence} for row in related
        ],
    }
    return output, packet


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
    parser.add_argument(
        "--suite-results",
        help="UTF-8 file containing one result-summary line per test suite",
    )
    parser.add_argument(
        "--prior",
        help="re-review only: a report whose candidates block holds the prior findings to re-verify",
    )
    parser.add_argument(
        "--packet",
        help="write the accounting packet (expected candidate and acquittal ids) to this JSON file",
    )
    args = parser.parse_args()

    if not Path(args.brief).is_absolute():
        parser.error("--brief must be an absolute path")

    try:
        output, packet = build(args)
        if args.packet:
            try:
                Path(args.packet).write_text(
                    json.dumps(packet, indent=2) + "\n", encoding="utf-8"
                )
            except OSError as error:
                raise InputError(f"cannot write packet {args.packet}: {error}") from error
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
