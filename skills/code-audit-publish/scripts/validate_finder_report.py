#!/usr/bin/env python3
"""Validate the shape of a finder report's ledger, manifest, and counts blocks.

Purpose: refuse a finder report whose disposition ledger, returned manifest,
or requirement counts are missing or malformed, so the orchestrator can send
the finder back for a conforming shape instead of fabricating rows or
carrying an unauditable axis forward. The script checks shape only: it never
reads the repository, runs git, or judges what a row says.

Usage:
    python3 scripts/validate_finder_report.py --axis code|requirements
        --manifest <file> < <finder report>
    python3 scripts/validate_finder_report.py --self-test

The report is read from stdin as markdown. `--manifest` names the
orchestrator's changed-file manifest, one repository-relative path per line;
a `git diff --name-status` line is accepted too, and its last tab-separated
field is taken as the path, so a rename or copy lists under its new path.

Exit codes:
    0  the report conforms
    1  the report violates the shape (one line per violation on stdout, as
       `<block>:<row>: <rule>: <detail>`; row 0 is the block as a whole)
    2  the report or the manifest file could not be read, or a self-test
       subprocess failed, named on stderr

Input schema: the report carries one fenced ```candidates block in the
grammar `build_verifier_prompt.py` documents (thirteen ordered fields per
`### Candidate` section, or `None.`), and ends with, in this order, one
fenced ```ledger block, one fenced ```manifest block, and, on the
Requirements axis only, one fenced ```counts block. No other fenced block
may follow them.

    ```ledger
    <id> | <kind> | <one-line claim> | <falsification route> | <evidence> | <disposition>
    ```
    ```manifest
    <path> | <reviewed|ignored> | <reason>
    ```
    ```counts
    met=<n> not-met=<n> unverifiable=<n>
    ```

Rows are one per line, pipe-separated, no header row, no blank rows. A row
id is the axis name, a dash, and a positive integer (`code-3`,
`requirements-1`), unique within the block; it is a per-run handle, never a
published finding id. A kind is one of bug, concurrency, invariant,
security, performance, maintainability, requirement; a Requirements row
uses `requirement` and a Code row one of the other six. A disposition is
`candidate`, `acquitted`, `observation`, or, on the Requirements axis only,
`question`. Evidence is one whole `path:line`, `path:start-end`, or
quoted-rule location `` `path` § heading ``, optionally in backticks. The
four-field row grammar that preceded ids and kinds is refused by field
count, naming the old grammar. At least one ledger row is a `candidate`
unless the report says "no candidates" or its candidates block reads
`None.`. Every manifest path appears exactly once in the manifest block,
with `reviewed` or `ignored` as its status and a non-empty reason when
ignored.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_verifier_prompt import (  # noqa: E402  (sibling script in this skill)
    KINDS,
    KINDS_BY_AXIS,
    LEDGER_FIELD_COUNT,
    ROW_ID_RE,
    ReportError,
    parse_candidates,
)

AXES = ("code", "requirements")
DISPOSITIONS = ("candidate", "acquitted", "observation", "question")
STATUSES = ("reviewed", "ignored")
COUNT_KEYS = ("met", "not-met", "unverifiable")
FENCE_RE = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})(?P<info>[^`\s]*)[ \t]*$")
COORDINATE_RE = re.compile(r"^(?P<tick>`?)(?P<path>[^`]+?):\d+(?:-\d+)?(?P=tick)$")
QUOTED_RULE_RE = re.compile(r"^`?(?P<path>[^`§]+?)`?[ \t]*§[ \t]*\S.*$")
SEPARATOR_RE = re.compile(r"^[-:\s]+$")
NAME_STATUS_RE = re.compile(r"^[ACDMRTUXB]\d*$")
COUNT_TOKEN_RE = re.compile(r"^(?P<key>[A-Za-z-]+)=(?P<value>.*)$")
NO_CANDIDATES_RE = re.compile(r"\bno candidates\b", re.IGNORECASE)


class InputError(OSError):
    """The report or the manifest file could not be read."""


@dataclass
class Block:
    info: str
    lines: list[str]


@dataclass
class Violation:
    block: str
    row: int
    rule: str
    detail: str

    def render(self) -> str:
        return f"{self.block}:{self.row}: {self.rule}: {self.detail}"


def fenced_blocks(markdown: str) -> list[Block]:
    """Every top-level fenced block in document order.

    A block closes at the first line carrying a fence of the same character at
    least as long as the one that opened it, so a four-backtick block encloses
    a three-backtick fence as content rather than as a nested block.
    """
    lines = markdown.splitlines()
    blocks: list[Block] = []
    index = 0
    while index < len(lines):
        match = FENCE_RE.match(lines[index])
        if not match:
            index += 1
            continue
        fence = match.group("fence")
        closing = re.compile(rf"^[ \t]{{0,3}}{re.escape(fence[0])}{{{len(fence)},}}[ \t]*$")
        start = index + 1
        index = start
        while index < len(lines) and not closing.match(lines[index]):
            index += 1
        blocks.append(Block(info=match.group("info"), lines=lines[start:index]))
        index += 1
    return blocks


def strip_span(text: str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] == "`":
        text = text[1:-1].strip()
    return text


def normalize_path(text: str) -> str:
    text = strip_span(text)
    while text.startswith("./"):
        text = text[2:]
    return text


def read_manifest(path: str) -> list[str]:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as error:
        raise InputError(f"cannot read manifest {path}: {error}") from error
    entries: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        fields = line.rstrip("\n").split("\t")
        if len(fields) > 1 and NAME_STATUS_RE.match(fields[0].strip()):
            line = fields[-1]
        entries.append(normalize_path(line))
    return entries


def locate_blocks(blocks: list[Block], axis: str) -> tuple[dict[str, Block], list[Violation]]:
    """Find the ledger, manifest, and counts blocks and check they close the report."""
    violations: list[Violation] = []
    found: dict[str, Block] = {}
    expected = ["ledger", "manifest"] + (["counts"] if axis == "requirements" else [])

    for name in ("ledger", "manifest", "counts"):
        matching = [block for block in blocks if block.info == name]
        if name == "counts" and axis == "code":
            if matching:
                violations.append(
                    Violation("counts", 0, "counts block forbidden", "the Code axis returns no counts block")
                )
            continue
        if not matching:
            violations.append(
                Violation(name, 0, f"missing {name} block", f"the report has no fenced {name} block")
            )
        elif len(matching) > 1:
            violations.append(
                Violation(
                    name,
                    0,
                    f"duplicate {name} block",
                    f"the report has {len(matching)} fenced {name} blocks; exactly one is allowed",
                )
            )
        else:
            found[name] = matching[0]

    if len(found) == len(expected):
        tail = [block.info for block in blocks[-len(expected):]]
        if tail != expected:
            violations.append(
                Violation(
                    "report",
                    0,
                    "block order",
                    "the report must end with the blocks "
                    + ", ".join(expected)
                    + " in that order; found "
                    + ", ".join(info or "(no info string)" for info in tail),
                )
            )
    return found, violations


def is_separator_row(fields: list[str]) -> bool:
    return all(SEPARATOR_RE.match(field) for field in fields if field.strip()) and any(
        "-" in field for field in fields
    )


def is_header_row(fields: list[str], first: set[str], last: set[str]) -> bool:
    """A markdown table header or its separator row, which the blocks do not carry."""
    lowered = [field.strip().lower() for field in fields]
    return is_separator_row(fields) or (lowered[0] in first and lowered[-1] in last)


def check_candidates(report: str, axis: str) -> list[Violation]:
    """Refuse a candidates block the verifier-prompt builder would refuse.

    The builder's parser is the grammar; running it here gives a candidate
    shape violation the same one-shot re-dispatch a ledger violation gets,
    instead of surfacing at step 3 where no repair path exists.
    """
    try:
        parse_candidates(report, axis.capitalize())
    except ReportError as error:
        return [Violation("candidates", 0, "candidate shape", str(error))]
    return []


def check_ledger(block: Block, axis: str, report: str, blocks: list[Block]) -> list[Violation]:
    violations: list[Violation] = []
    rows = 0
    has_candidate = False
    seen_ids: dict[str, int] = {}
    for number, line in enumerate(block.lines, start=1):
        if not line.strip():
            violations.append(Violation("ledger", number, "blank row", "ledger rows may not be blank"))
            continue
        fields = [field.strip() for field in line.split("|")]
        if is_header_row(fields, {"id"}, {"disposition"}):
            violations.append(
                Violation("ledger", number, "header row", "the ledger has no header or separator row")
            )
            continue
        rows += 1
        if len(fields) != LEDGER_FIELD_COUNT:
            hint = "; the four-field grammar has no id or kind" if len(fields) == 4 else ""
            violations.append(
                Violation(
                    "ledger",
                    number,
                    "field count",
                    "expected six pipe-separated fields (id | kind | claim | route | evidence | "
                    f"disposition); found {len(fields)}{hint}",
                )
            )
            continue
        row_id, kind, claim, route, evidence, disposition = fields
        id_match = ROW_ID_RE.match(row_id)
        if not id_match or id_match.group("axis") != axis:
            violations.append(
                Violation("ledger", number, "row id", f"{row_id!r} is not {axis}-<n>")
            )
        elif row_id in seen_ids:
            violations.append(
                Violation(
                    "ledger",
                    number,
                    "duplicate row id",
                    f"{row_id} was already used on row {seen_ids[row_id]}",
                )
            )
        else:
            seen_ids[row_id] = number
        if kind not in KINDS:
            violations.append(
                Violation("ledger", number, "kind", f"{kind!r} is not one of {', '.join(KINDS)}")
            )
        elif kind not in KINDS_BY_AXIS[axis.capitalize()]:
            violations.append(
                Violation(
                    "ledger",
                    number,
                    "kind",
                    f"{kind!r} is not a {axis} kind; this axis uses "
                    + ", ".join(KINDS_BY_AXIS[axis.capitalize()]),
                )
            )
        for name, value in (("claim", claim), ("route", route)):
            if not value:
                violations.append(Violation("ledger", number, "empty field", f"the {name} field is empty"))
        if not (COORDINATE_RE.match(evidence) or QUOTED_RULE_RE.match(evidence)):
            violations.append(
                Violation(
                    "ledger",
                    number,
                    "evidence",
                    f"{evidence!r} is not one path:line, path:start-end, or `path` § heading location",
                )
            )
        if disposition not in DISPOSITIONS:
            violations.append(
                Violation(
                    "ledger",
                    number,
                    "disposition",
                    f"{disposition!r} is not one of {', '.join(DISPOSITIONS)}",
                )
            )
        elif disposition == "question" and axis == "code":
            violations.append(
                Violation(
                    "ledger", number, "disposition", "question is allowed only on the Requirements axis"
                )
            )
        elif disposition == "candidate":
            has_candidate = True
    if rows == 0:
        violations.append(Violation("ledger", 0, "empty ledger", "the ledger block has no rows"))
    elif not has_candidate and not declares_no_candidates(report, blocks):
        violations.append(
            Violation(
                "ledger",
                0,
                "no candidate row",
                "no ledger row has disposition candidate and the report does not say \"no candidates\"",
            )
        )
    return violations


def declares_no_candidates(report: str, blocks: list[Block]) -> bool:
    if NO_CANDIDATES_RE.search(report):
        return True
    for block in blocks:
        if block.info == "candidates":
            content = "\n".join(block.lines).strip().casefold()
            if content in {"none", "none."}:
                return True
    return False


def check_manifest(block: Block, manifest: list[str]) -> list[Violation]:
    violations: list[Violation] = []
    seen: dict[str, list[int]] = {}
    for number, line in enumerate(block.lines, start=1):
        if not line.strip():
            violations.append(Violation("manifest", number, "blank row", "manifest rows may not be blank"))
            continue
        fields = [field.strip() for field in line.split("|")]
        if is_header_row(fields, {"path", "file"}, {"reason", "status", "disposition"}):
            violations.append(
                Violation("manifest", number, "header row", "the manifest has no header or separator row")
            )
            continue
        if len(fields) != 3:
            violations.append(
                Violation(
                    "manifest",
                    number,
                    "field count",
                    f"expected three pipe-separated fields (path | status | reason); found {len(fields)}",
                )
            )
            continue
        path, status, reason = fields
        path = normalize_path(path)
        seen.setdefault(path, []).append(number)
        if status not in STATUSES:
            violations.append(
                Violation("manifest", number, "status", f"{status!r} is not one of {', '.join(STATUSES)}")
            )
        elif status == "ignored" and not reason:
            violations.append(
                Violation("manifest", number, "ignored reason", f"{path} is ignored without a reason")
            )
        if path not in manifest:
            violations.append(
                Violation("manifest", number, "unlisted path", f"{path} is not in the changed-file manifest")
            )
    for path in manifest:
        rows = seen.get(path, [])
        if not rows:
            violations.append(Violation("manifest", 0, "missing path", f"{path} has no manifest row"))
        elif len(rows) > 1:
            violations.append(
                Violation(
                    "manifest",
                    rows[1],
                    "duplicate path",
                    f"{path} appears {len(rows)} times (rows {', '.join(map(str, rows))}); exactly once is allowed",
                )
            )
    return violations


def check_counts(block: Block) -> list[Violation]:
    violations: list[Violation] = []
    values: dict[str, list[int]] = {}
    for number, line in enumerate(block.lines, start=1):
        for token in line.split():
            match = COUNT_TOKEN_RE.match(token)
            if not match:
                violations.append(
                    Violation("counts", number, "count token", f"{token!r} is not <key>=<integer>")
                )
                continue
            key, value = match.group("key"), match.group("value")
            if key not in COUNT_KEYS:
                violations.append(
                    Violation("counts", number, "count key", f"{key!r} is not one of {', '.join(COUNT_KEYS)}")
                )
                continue
            if not value.isdigit():
                violations.append(
                    Violation("counts", number, "count value", f"{key}={value!r} is not a non-negative integer")
                )
                continue
            values.setdefault(key, []).append(number)
    for key in COUNT_KEYS:
        rows = values.get(key, [])
        if not rows:
            violations.append(Violation("counts", 0, "missing count", f"{key}=<n> is absent"))
        elif len(rows) > 1:
            violations.append(Violation("counts", rows[1], "duplicate count", f"{key} is given more than once"))
    return violations


def validate(report: str, axis: str, manifest: list[str]) -> list[Violation]:
    blocks = fenced_blocks(report)
    found, violations = locate_blocks(blocks, axis)
    violations.extend(check_candidates(report, axis))
    if "ledger" in found:
        violations.extend(check_ledger(found["ledger"], axis, report, blocks))
    if "manifest" in found:
        violations.extend(check_manifest(found["manifest"], manifest))
    if "counts" in found:
        violations.extend(check_counts(found["counts"]))
    return violations


# --- self-test -------------------------------------------------------------

MANIFEST_PATHS = ("src/app.py", "docs/guide.md", "package-lock.json")

CODE_REPORT = """## Candidates

### Candidate 1

- id: code/app/retry-drops-last-error

````candidates
### Candidate
id: code/app/retry-drops-last-error
axis: Code
kind: bug
anchor: src/app.py:42
fix: (same as anchor)
title: retry loop drops the last error
claim: `retry()` at `src/app.py:42` returns None after the final failure instead of raising.
support: Read the loop; ran the focused test.
trigger: Every attempt fails.
impact: The caller proceeds with None where an exception was promised.
change: Re-raise the last error after the final attempt at `src/app.py:42`.
priority: P1
action: must-fix
````

## Observations

- The guide still shows the old flag name — `docs/guide.md:10`.

```ledger
code-1 | bug | retry() drops the last error | read the loop exit | src/app.py:42 | candidate
code-2 | bug | retry() double-counts attempts | trace the counter | src/app.py:30-38 | acquitted
code-3 | maintainability | guide shows the old flag name | compare to the CLI | docs/guide.md:10 | observation
code-4 | maintainability | lockfile drifts from package.json | diff the two | `package-lock.json:1` | acquitted
code-5 | maintainability | naming rule is violated | quote the rule | `CONTRIBUTING.md` § Naming | acquitted
```
```manifest
src/app.py | reviewed | read in full with its callers
docs/guide.md | reviewed | nothing stood out beyond the observation
package-lock.json | ignored | generated lockfile with no logic
```
"""

REQUIREMENTS_REPORT = """## Restated requirements

1. The retry helper raises after the last attempt.
2. The guide documents the new flag.

## Candidates

No candidates.

```candidates
None.
```

```ledger
requirements-1 | requirement | guide documents the new flag | search the guide | docs/guide.md:10 | acquitted
requirements-2 | requirement | retry raises after the last attempt | read the loop exit | src/app.py:42 | acquitted
requirements-3 | requirement | timeout default is tuned for production | needs a measurement | src/app.py:12 | question
```
```manifest
src/app.py | reviewed | implements requirement 1
docs/guide.md | reviewed | implements requirement 2
package-lock.json | ignored | generated lockfile, no requirement touches it
```
```counts
met=2 not-met=0 unverifiable=1
```
"""


def _replace(text: str, old: str, new: str) -> str:
    if old not in text:
        raise AssertionError(f"self-test fixture does not contain {old!r}")
    return text.replace(old, new, 1)


def self_test_cases() -> list[tuple[str, str, str, int, str]]:
    """(name, axis, report, expected exit code, expected substring of stdout)."""
    code, req = CODE_REPORT, REQUIREMENTS_REPORT
    manifest_head = "```manifest\n"
    return [
        ("code passes", "code", code, 0, ""),
        ("requirements passes", "requirements", req, 0, ""),
        ("missing ledger block", "requirements",
         req.replace("```ledger", "```record"), 1, "ledger:0: missing ledger block"),
        ("info string after whitespace is not a ledger block", "code",
         code.replace("```ledger", "``` ledger"), 1, "ledger:0: missing ledger block"),
        ("missing manifest block", "code",
         code.replace("```manifest", "```files"), 1, "manifest:0: missing manifest block"),
        ("missing counts block", "requirements",
         req.replace("```counts", "```tally"), 1, "counts:0: missing counts block"),
        ("counts forbidden on code", "code",
         code + "```counts\nmet=1 not-met=0 unverifiable=0\n```\n", 1, "counts:0: counts block forbidden"),
        ("duplicate ledger block", "code",
         code + "```ledger\nextra | route | src/app.py:1 | acquitted\n```\n", 1, "ledger:0: duplicate ledger block"),
        ("blocks not last", "code",
         code + "```text\ntrailing\n```\n", 1, "report:0: block order"),
        ("blocks out of order", "requirements",
         _replace(req, "```counts\nmet=2 not-met=0 unverifiable=1\n```\n", "")
         .replace("```ledger", "```counts\nmet=2 not-met=0 unverifiable=1\n```\n```ledger"),
         1, "report:0: block order"),
        ("ledger field count", "code",
         _replace(code, "| trace the counter | src/app.py:30-38 |", "| src/app.py:30-38 |"),
         1, "ledger:2: field count"),
        ("old four-field row refused by count", "code",
         _replace(code, "code-2 | bug | retry() double-counts attempts", "retry() double-counts attempts"),
         1, "ledger:2: field count: expected six pipe-separated fields (id | kind | claim | route | evidence | disposition); found 4; the four-field grammar has no id or kind"),
        ("ledger row id shape", "code",
         _replace(code, "code-2 | bug |", "row-2 | bug |"), 1, "ledger:2: row id: 'row-2' is not code-<n>"),
        ("ledger row id wrong axis", "code",
         _replace(code, "code-2 | bug |", "requirements-2 | bug |"), 1, "ledger:2: row id"),
        ("ledger row id duplicate", "code",
         _replace(code, "code-2 | bug |", "code-1 | bug |"), 1, "ledger:2: duplicate row id: code-1 was already used on row 1"),
        ("ledger kind", "code",
         _replace(code, "code-2 | bug |", "code-2 | race |"), 1, "ledger:2: kind: 'race' is not one of"),
        ("ledger kind wrong axis on code", "code",
         _replace(code, "code-2 | bug |", "code-2 | requirement |"),
         1, "ledger:2: kind: 'requirement' is not a code kind; this axis uses bug, concurrency"),
        ("ledger kind wrong axis on requirements", "requirements",
         _replace(req, "requirements-2 | requirement |", "requirements-2 | bug |"),
         1, "ledger:2: kind: 'bug' is not a requirements kind; this axis uses requirement"),
        ("ledger header row", "code",
         _replace(code, "```ledger\n", "```ledger\nid | kind | claim | route | evidence | disposition\n"),
         1, "ledger:1: header row"),
        ("ledger separator row", "code",
         _replace(code, "```ledger\n", "```ledger\n--- | --- | --- | --- | --- | ---\n"),
         1, "ledger:1: header row"),
        ("ledger blank row", "code",
         _replace(code, "| candidate\n", "| candidate\n\n"), 1, "ledger:2: blank row"),
        ("ledger disposition", "code",
         _replace(code, "| src/app.py:30-38 | acquitted", "| src/app.py:30-38 | dismissed"),
         1, "ledger:2: disposition"),
        ("question forbidden on code", "code",
         _replace(code, "| src/app.py:30-38 | acquitted", "| src/app.py:30-38 | question"),
         1, "ledger:2: disposition: question is allowed only"),
        ("ledger evidence prose", "code",
         _replace(code, "| src/app.py:30-38 |", "| src/app.py:30-38 and the counter |"),
         1, "ledger:2: evidence"),
        ("ledger evidence bare path", "code",
         _replace(code, "| src/app.py:30-38 |", "| src/app.py |"), 1, "ledger:2: evidence"),
        ("candidate missing kind", "code",
         _replace(code, "kind: bug\n", ""), 1, "candidates:0: candidate shape: Code Candidate is missing kind before anchor"),
        ("candidate old ten-field shape", "code",
         _replace(_replace(_replace(code, "kind: bug\n", ""),
                           "impact: The caller proceeds with None where an exception was promised.\n", ""),
                  "change: Re-raise the last error after the final attempt at `src/app.py:42`.\n", ""),
         1, "candidates:0: candidate shape: Code Candidate is missing kind before anchor"),
        ("candidate kind vocabulary", "code",
         _replace(code, "kind: bug\n", "kind: race\n"), 1, "candidates:0: candidate shape: Code Candidate has kind 'race'"),
        ("candidate kind wrong axis", "code",
         _replace(code, "kind: bug\n", "kind: requirement\n"),
         1, "candidates:0: candidate shape: Code Candidate has kind 'requirement'; a Code candidate uses bug, concurrency"),
        ("candidate id axis prefix", "code",
         _replace(code, "id: code/app/retry-drops-last-error\naxis: Code\n",
                  "id: requirements/app/retry-drops-last-error\naxis: Code\n"),
         1, "candidates:0: candidate shape: Code Candidate has id 'requirements/app/retry-drops-last-error'"),
        ("candidate empty change", "code",
         _replace(code, "change: Re-raise the last error after the final attempt at `src/app.py:42`.\n", "change:\n"),
         1, "candidates:0: candidate shape: Code Candidate has an empty change"),
        ("candidate duplicate id", "code",
         _replace(code, "````candidates\n", "````candidates\n### Candidate\nid: code/app/retry-drops-last-error\naxis: Code\nkind: bug\nanchor: src/app.py:42\nfix: (same as anchor)\ntitle: twin\nclaim: twin claim\nsupport: none\ntrigger: twin\nimpact: twin\nchange: twin\npriority: P2\naction: consider\n"),
         1, "candidates:0: candidate shape: Code Candidate repeats id 'code/app/retry-drops-last-error'"),
        ("candidates block missing", "code",
         code.replace("````candidates", "````proposals"), 1, "candidates:0: candidate shape: Code report must contain exactly one candidates block; found 0"),
        ("no candidate row", "code",
         _replace(code, "| src/app.py:42 | candidate", "| src/app.py:42 | acquitted"),
         1, "ledger:0: no candidate row"),
        ("no candidates phrase accepted", "code",
         _replace(code, "| src/app.py:42 | candidate", "| src/app.py:42 | acquitted")
         .replace("## Candidates\n", "## Candidates\n\nNo candidates.\n"), 0, ""),
        ("empty ledger", "code",
         re.sub(r"```ledger\n.*?```", "```ledger\n```", code, count=1, flags=re.DOTALL),
         1, "ledger:0: empty ledger"),
        ("manifest missing path", "code",
         _replace(code, "docs/guide.md | reviewed | nothing stood out beyond the observation\n", ""),
         1, "manifest:0: missing path: docs/guide.md"),
        ("manifest duplicate path", "code",
         _replace(code, manifest_head, manifest_head + "src/app.py | reviewed | read twice\n"),
         1, "manifest:2: duplicate path: src/app.py"),
        ("manifest unlisted path", "code",
         _replace(code, manifest_head, manifest_head + "src/other.py | reviewed | not in the diff\n"),
         1, "manifest:1: unlisted path: src/other.py"),
        ("manifest status", "code",
         _replace(code, "src/app.py | reviewed |", "src/app.py | read |"), 1, "manifest:1: status"),
        ("manifest ignored reason", "code",
         _replace(code, "package-lock.json | ignored | generated lockfile with no logic",
                  "package-lock.json | ignored |"), 1, "manifest:3: ignored reason"),
        ("manifest field count", "code",
         _replace(code, "src/app.py | reviewed | read in full with its callers", "src/app.py | reviewed"),
         1, "manifest:1: field count"),
        ("manifest header row", "code",
         _replace(code, manifest_head, manifest_head + "path | status | reason\n"),
         1, "manifest:1: header row"),
        ("counts missing key", "requirements",
         _replace(req, "met=2 not-met=0 unverifiable=1", "met=2 not-met=0"),
         1, "counts:0: missing count: unverifiable"),
        ("counts non-integer", "requirements",
         _replace(req, "met=2 not-met=0 unverifiable=1", "met=two not-met=0 unverifiable=1"),
         1, "counts:1: count value"),
        ("counts unknown key", "requirements",
         _replace(req, "unverifiable=1", "unverifiable=1 questions=1"), 1, "counts:1: count key"),
        ("counts stray token", "requirements",
         _replace(req, "unverifiable=1", "unverifiable=1 (one question)"), 1, "counts:1: count token"),
        ("name-status manifest accepted", "code", code, 0, ""),
    ]


def run_self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as directory:
        plain = Path(directory) / "manifest.txt"
        plain.write_text("\n".join(MANIFEST_PATHS) + "\n", encoding="utf-8")
        name_status = Path(directory) / "manifest.tsv"
        name_status.write_text(
            "".join(f"M\t{path}\n" for path in MANIFEST_PATHS), encoding="utf-8"
        )
        for name, axis, report, expected_code, expected_text in self_test_cases():
            manifest = name_status if name.startswith("name-status") else plain
            result = subprocess.run(
                [sys.executable, __file__, "--axis", axis, "--manifest", str(manifest)],
                input=report,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if result.returncode == 2:
                print(f"validate_finder_report --self-test: {name}: {result.stderr.strip()}", file=sys.stderr)
                return 2
            if result.returncode != expected_code or expected_text not in result.stdout:
                failures.append(
                    f"{name}: expected exit {expected_code} containing {expected_text!r}; "
                    f"got exit {result.returncode} with output {result.stdout.strip()!r}"
                )
        missing = Path(directory) / "absent.txt"
        result = subprocess.run(
            [sys.executable, __file__, "--axis", "code", "--manifest", str(missing)],
            input=CODE_REPORT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 2 or "cannot read manifest" not in result.stderr:
            failures.append(
                f"unreadable manifest: expected exit 2 naming the manifest; got exit "
                f"{result.returncode} with stderr {result.stderr.strip()!r}"
            )
    for failure in failures:
        print(failure)
    if failures:
        return 1
    print(f"validate_finder_report --self-test: {len(self_test_cases()) + 1} cases passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the ledger, manifest, and counts blocks of a finder report read from stdin."
    )
    parser.add_argument("--axis", choices=AXES, help="which finder wrote the report")
    parser.add_argument("--manifest", help="changed-file manifest, one path per line")
    parser.add_argument("--self-test", action="store_true", help="run the embedded fixtures and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.axis or not args.manifest:
        parser.error("--axis and --manifest are required unless --self-test is given")

    try:
        manifest = read_manifest(args.manifest)
        report = sys.stdin.buffer.read().decode("utf-8")
    except InputError as error:
        print(f"validate_finder_report: {error}", file=sys.stderr)
        return 2
    except (OSError, UnicodeDecodeError) as error:
        print(f"validate_finder_report: cannot read the report from stdin: {error}", file=sys.stderr)
        return 2

    violations = validate(report, args.axis, manifest)
    for violation in violations:
        print(violation.render())
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
