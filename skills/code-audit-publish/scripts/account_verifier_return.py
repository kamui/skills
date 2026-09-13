#!/usr/bin/env python3
"""Account for every verdict and ruling in a verifier return.

Purpose: check the verifier's return against the accounting packet
`build_verifier_prompt.py --packet` wrote, so that every candidate the
verifier was given has exactly one verdict and every acquittal row it was
given has exactly one ruling. A missing, duplicate, unexpected, or malformed
record is a violation the orchestrator sends back once for the same
verdicts in conforming shape; it is never filled in, and a return with zero
records for a non-empty packet is a failure, not a clean review. The script
checks shape and accounting only: it never reads the repository, runs git,
or judges whether a verdict is right.

Usage:
    python3 scripts/account_verifier_return.py --packet <file> < <verifier return>
    python3 scripts/account_verifier_return.py --self-test

Exit codes:
    0  every expected id has exactly one conforming record; the normalized
       records are printed, one per line, as
       `candidate <id> | <verdict> | <basis>` then
       `acquittal <id> | <ruling> | <evidence>`
    1  the return violates the accounting (one line per violation on stdout,
       as `<block>:<row>: <rule>: <detail>`, each naming the record id where
       the row carries one; row 0 is the block as a whole), followed by one
       `accounted: <id>, ...` line listing every expected id with exactly one
       conforming record and one `withheld: <id>, ...` line listing every
       other expected id — missing, duplicated, or malformed. The two lines
       partition the packet, so the orchestrator withholds exactly what the
       `withheld:` line names and never infers it from the violations.
    2  the packet or the return could not be read, the packet is not the
       builder's JSON, or the packet is empty — an intentionally empty input
       takes the explicit clean-review path and dispatches no verifier — or a
       self-test subprocess failed, named on stderr

Input schema: the return ends with, in this order, one fenced ```verdicts
block and one fenced ```rulings block. No other fenced block may follow them.

    ```verdicts
    <candidate id> | <confirmed|plausible|refuted> | <basis>
    ```
    ```rulings
    <row id> | <holds|re-open> | <evidence>
    ```

Rows are one per line, pipe-separated, no header row, no blank rows. A
verdict's basis is, for `refuted`, one of the five evidence bases
(contradiction, prevention, established-intent, pre-existing,
no-consequence); for `confirmed`, the `path:line` of the quoted defect
line; for `plausible`, `trigger` or `impact`, whichever is unsettled. A
ruling's evidence is one whole `path:line`, `path:start-end`, or
quoted-rule location `` `path` § heading ``, optionally in backticks, and a
`holds` ruling cites a location the ledger row did not. Each block reads
`None.` (or is empty) only when the packet supplied no records of its kind.
The packet is the builder's JSON: {"candidates": [{"id", "axis"}...],
"acquittals": [{"id", "axis", "evidence"}...]}.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

VERDICTS = ("confirmed", "plausible", "refuted")
RULINGS = ("holds", "re-open")
REFUTATION_BASES = (
    "contradiction",
    "prevention",
    "established-intent",
    "pre-existing",
    "no-consequence",
)
PLAUSIBLE_BASES = ("trigger", "impact")
FENCE_RE = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})(?P<info>[^`\s]*)[ \t]*$")
COORDINATE_RE = re.compile(r"^(?P<tick>`?)(?P<path>[^`]+?):\d+(?:-\d+)?(?P=tick)$")
QUOTED_RULE_RE = re.compile(r"^`?(?P<path>[^`§]+?)`?[ \t]*§[ \t]*\S.*$")
SEPARATOR_RE = re.compile(r"^[-:\s]+$")
NONE_RE = re.compile(r"^(?:none\.?|no (?:verdicts|rulings)\.?)$", re.IGNORECASE)


class InputError(OSError):
    """The packet or the return could not be read, or the packet is unusable."""


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


@dataclass
class Packet:
    candidates: list[str]
    acquittals: dict[str, str]


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


def normalize_location(text: str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] == "`":
        text = text[1:-1].strip()
    while text.startswith("./"):
        text = text[2:]
    return text


def is_location(text: str) -> bool:
    return bool(COORDINATE_RE.match(text) or QUOTED_RULE_RE.match(text))


def read_packet(path: str) -> Packet:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as error:
        raise InputError(f"cannot read packet {path}: {error}") from error
    try:
        data = json.loads(text)
    except ValueError as error:
        raise InputError(f"packet {path} is not JSON: {error}") from error
    if not isinstance(data, dict) or not isinstance(data.get("candidates"), list) or not isinstance(
        data.get("acquittals"), list
    ):
        raise InputError(f"packet {path} is not the builder's shape (candidates and acquittals lists)")
    candidates: list[str] = []
    for entry in data["candidates"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not entry["id"]:
            raise InputError(f"packet {path} has a candidate entry without an id")
        if entry["id"] in candidates:
            raise InputError(f"packet {path} lists candidate {entry['id']} twice")
        candidates.append(entry["id"])
    acquittals: dict[str, str] = {}
    for entry in data["acquittals"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not entry["id"]:
            raise InputError(f"packet {path} has an acquittal entry without an id")
        if entry["id"] in acquittals:
            raise InputError(f"packet {path} lists acquittal {entry['id']} twice")
        acquittals[entry["id"]] = normalize_location(str(entry.get("evidence", "")))
    if not candidates and not acquittals:
        raise InputError(
            f"packet {path} is empty: an intentionally empty input takes the clean-review path "
            "and dispatches no verifier, so there is no return to account for"
        )
    return Packet(candidates=candidates, acquittals=acquittals)


def is_separator_row(fields: list[str]) -> bool:
    return all(SEPARATOR_RE.match(field) for field in fields if field.strip()) and any(
        "-" in field for field in fields
    )


def is_header_row(fields: list[str], first: set[str], second: set[str]) -> bool:
    lowered = [field.strip().lower() for field in fields]
    return is_separator_row(fields) or (
        len(lowered) >= 2 and lowered[0] in first and lowered[1] in second
    )


def locate_blocks(blocks: list[Block]) -> tuple[dict[str, Block], list[Violation]]:
    violations: list[Violation] = []
    found: dict[str, Block] = {}
    expected = ["verdicts", "rulings"]
    for name in expected:
        matching = [block for block in blocks if block.info == name]
        if not matching:
            violations.append(
                Violation(name, 0, f"missing {name} block", f"the return has no fenced {name} block")
            )
        elif len(matching) > 1:
            violations.append(
                Violation(
                    name,
                    0,
                    f"duplicate {name} block",
                    f"the return has {len(matching)} fenced {name} blocks; exactly one is allowed",
                )
            )
        else:
            found[name] = matching[0]
    if len(found) == len(expected):
        tail = [block.info for block in blocks[-len(expected):]]
        if tail != expected:
            violations.append(
                Violation(
                    "return",
                    0,
                    "block order",
                    "the return must end with the blocks verdicts, rulings in that order; found "
                    + ", ".join(info or "(no info string)" for info in tail),
                )
            )
    return found, violations


def block_is_none(block: Block) -> bool:
    content = [line.strip() for line in block.lines if line.strip()]
    return not content or (len(content) == 1 and bool(NONE_RE.match(content[0])))


def check_records(
    block: Block,
    name: str,
    expected: list[str],
    kind_label: str,
    vocabulary: tuple[str, ...],
    check_third: Callable[[str, str, str], str | None],
) -> tuple[dict[str, tuple[str, str]], list[Violation]]:
    """Parse one block's rows and account them against the expected ids.

    Returns the conforming records keyed by id (only ids with exactly one
    well-formed row) and the violations. `check_third` receives (id, word,
    third field) and returns a violation detail or None.
    """
    violations: list[Violation] = []
    rows_by_id: dict[str, list[int]] = {}
    records: dict[str, tuple[str, str]] = {}
    malformed: set[str] = set()
    if block_is_none(block):
        if expected:
            violations.append(
                Violation(
                    name,
                    0,
                    "empty block",
                    f"zero records for a packet of {len(expected)} {kind_label}(s); "
                    "absence is not a verdict",
                )
            )
    else:
        for number, line in enumerate(block.lines, start=1):
            if not line.strip():
                violations.append(Violation(name, number, "blank row", f"{name} rows may not be blank"))
                continue
            fields = [field.strip() for field in line.split("|")]
            if is_header_row(fields, {"id", "candidate", "row", "candidate id", "row id"}, {"verdict", "ruling"}):
                violations.append(
                    Violation(name, number, "header row", f"the {name} block has no header or separator row")
                )
                continue
            if len(fields) != 3:
                if fields[0] in expected:
                    rows_by_id.setdefault(fields[0], []).append(number)
                    malformed.add(fields[0])
                violations.append(
                    Violation(
                        name,
                        number,
                        "field count",
                        f"{fields[0] + ': ' if fields[0] in expected else ''}expected three "
                        f"pipe-separated fields (id | {kind_label} word | "
                        f"{'basis' if name == 'verdicts' else 'evidence'}); found {len(fields)}",
                    )
                )
                continue
            record_id, word, third = fields
            if record_id not in expected:
                violations.append(
                    Violation(
                        name,
                        number,
                        "unexpected id",
                        f"{record_id!r} is not a {kind_label} the verifier was given; a record it "
                        "invents is never a finding",
                    )
                )
                continue
            rows_by_id.setdefault(record_id, []).append(number)
            well_formed = True
            if word not in vocabulary:
                violations.append(
                    Violation(
                        name,
                        number,
                        kind_label,
                        f"{record_id}: {word!r} is not one of {', '.join(vocabulary)}",
                    )
                )
                well_formed = False
            else:
                detail = check_third(record_id, word, third)
                if detail is not None:
                    violations.append(
                        Violation(
                            name,
                            number,
                            "basis" if name == "verdicts" else "evidence",
                            f"{record_id}: {detail}",
                        )
                    )
                    well_formed = False
            if well_formed:
                records[record_id] = (word, third)
            else:
                malformed.add(record_id)
    for record_id in expected:
        rows = rows_by_id.get(record_id, [])
        if not rows:
            violations.append(
                Violation(name, 0, f"missing {kind_label}", f"{record_id} has no record")
            )
        elif len(rows) > 1:
            violations.append(
                Violation(
                    name,
                    rows[1],
                    f"duplicate {kind_label}",
                    f"{record_id} appears {len(rows)} times (rows {', '.join(map(str, rows))}); "
                    "exactly once is allowed",
                )
            )
            records.pop(record_id, None)
    for record_id in malformed:
        records.pop(record_id, None)
    return records, violations


def account(return_text: str, packet: Packet) -> tuple[list[str], list[Violation], list[str], list[str]]:
    """The normalized records, the violations, and the accounted / withheld id partition.

    Every expected id lands in exactly one of the two id lists: accounted when
    it has exactly one conforming record, withheld otherwise — missing,
    duplicated, malformed, or in a block the return lacks.
    """
    blocks = fenced_blocks(return_text)
    found, violations = locate_blocks(blocks)
    normalized: list[str] = []
    accounted: list[str] = []

    def verdict_basis(_: str, word: str, basis: str) -> str | None:
        if not basis:
            return "the basis field is empty"
        if word == "refuted" and basis not in REFUTATION_BASES:
            return (
                f"{basis!r} is not one of the five refutation bases "
                f"({', '.join(REFUTATION_BASES)}); a refutation without its basis is plausible"
            )
        if word == "plausible" and basis not in PLAUSIBLE_BASES:
            return f"{basis!r} is not trigger or impact, the thing a plausible verdict leaves unsettled"
        if word == "confirmed" and not is_location(basis):
            return f"{basis!r} is not the path:line of the quoted defect line"
        return None

    def ruling_evidence(row_id: str, word: str, evidence: str) -> str | None:
        if not is_location(evidence):
            return f"{evidence!r} is not one path:line, path:start-end, or `path` § heading location"
        if word == "holds" and normalize_location(evidence) == packet.acquittals[row_id]:
            return (
                f"a holds ruling cites {evidence}, the row's own evidence; it must cite a line "
                "the ledger row did not"
            )
        return None

    if "verdicts" in found:
        verdicts, more = check_records(
            found["verdicts"], "verdicts", packet.candidates, "verdict", VERDICTS, verdict_basis
        )
        violations.extend(more)
        for candidate_id in packet.candidates:
            if candidate_id in verdicts:
                word, basis = verdicts[candidate_id]
                normalized.append(f"candidate {candidate_id} | {word} | {basis}")
                accounted.append(candidate_id)
    else:
        for candidate_id in packet.candidates:
            violations.append(Violation("verdicts", 0, "missing verdict", f"{candidate_id} has no record"))
    if "rulings" in found:
        rulings, more = check_records(
            found["rulings"], "rulings", list(packet.acquittals), "ruling", RULINGS, ruling_evidence
        )
        violations.extend(more)
        for row_id in packet.acquittals:
            if row_id in rulings:
                word, evidence = rulings[row_id]
                normalized.append(f"acquittal {row_id} | {word} | {evidence}")
                accounted.append(row_id)
    else:
        for row_id in packet.acquittals:
            violations.append(Violation("rulings", 0, "missing ruling", f"{row_id} has no record"))
    withheld = [
        record_id
        for record_id in packet.candidates + list(packet.acquittals)
        if record_id not in accounted
    ]
    return normalized, violations, accounted, withheld


# --- self-test -------------------------------------------------------------

PACKET = {
    "candidates": [
        {"id": "code/browser-context/remove-cookies-race", "axis": "Code"},
        {"id": "requirements/release-notes/missing-flag", "axis": "Requirements"},
    ],
    "acquittals": [
        {"id": "code-2", "axis": "Code", "evidence": "packages/browserContext.ts:540-544"},
    ],
}

RETURN = """## Candidate 1

Confirmed: the clear at `packages/browserContext.ts:291` runs before the restore.

## Candidate 2

Refuted on contradiction: the notes name the flag at `docs/Release Notes.md:12`.

## Related rows

code-2 holds: the reset branch takes the same lock at `packages/browserContext.ts:538`.

Merge list: none. Counts: confirmed=1 plausible=0 refuted=1.

```verdicts
code/browser-context/remove-cookies-race | confirmed | packages/browserContext.ts:291
requirements/release-notes/missing-flag | refuted | contradiction
```
```rulings
code-2 | holds | packages/browserContext.ts:538
```
"""

VERDICTS_HEAD = "```verdicts\n"
RULINGS_HEAD = "```rulings\n"


def _replace(text: str, old: str, new: str) -> str:
    if old not in text:
        raise AssertionError(f"self-test fixture does not contain {old!r}")
    return text.replace(old, new, 1)


def self_test_cases() -> list[tuple[str, dict, str, int, str]]:
    """(name, packet, return, expected exit code, expected substring of stdout)."""
    full = RETURN
    no_rows = {"candidates": PACKET["candidates"], "acquittals": []}
    return [
        ("all records present", PACKET, full, 0,
         "candidate requirements/release-notes/missing-flag | refuted | contradiction\n"
         "acquittal code-2 | holds | packages/browserContext.ts:538"),
        ("empty response", PACKET, "The verifier returned nothing.\n", 1,
         "verdicts:0: missing verdicts block"),
        ("empty response names every id", PACKET, "", 1,
         "verdicts:0: missing verdict: code/browser-context/remove-cookies-race"),
        ("zero-record blocks are a failure", PACKET,
         "```verdicts\nNone.\n```\n```rulings\nNone.\n```\n", 1,
         "verdicts:0: empty block: zero records for a packet of 2 verdict(s); absence is not a verdict"),
        ("zero-record rulings are a failure", PACKET,
         _replace(full, "code-2 | holds | packages/browserContext.ts:538\n", ""), 1,
         "rulings:0: empty block: zero records for a packet of 1 ruling(s)"),
        ("missing last id", PACKET,
         _replace(full, "requirements/release-notes/missing-flag | refuted | contradiction\n", ""), 1,
         "verdicts:0: missing verdict: requirements/release-notes/missing-flag has no record"),
        ("duplicate id", PACKET,
         _replace(full, VERDICTS_HEAD,
                  VERDICTS_HEAD + "code/browser-context/remove-cookies-race | refuted | prevention\n"), 1,
         "verdicts:2: duplicate verdict: code/browser-context/remove-cookies-race appears 2 times"),
        ("unknown id", PACKET,
         _replace(full, VERDICTS_HEAD, VERDICTS_HEAD + "code/invented/finding | confirmed | src/x.py:1\n"), 1,
         "verdicts:1: unexpected id: 'code/invented/finding' is not a verdict the verifier was given"),
        ("malformed verdict", PACKET,
         _replace(full, "| confirmed | packages/browserContext.ts:291", "| probably | packages/browserContext.ts:291"), 1,
         "verdicts:1: verdict: code/browser-context/remove-cookies-race: 'probably' is not one of confirmed, plausible, refuted"),
        ("malformed verdict is withheld by name", PACKET,
         _replace(full, "| confirmed | packages/browserContext.ts:291", "| probably | packages/browserContext.ts:291"), 1,
         "accounted: requirements/release-notes/missing-flag, code-2\nwithheld: code/browser-context/remove-cookies-race"),
        ("refuted without a basis token", PACKET,
         _replace(full, "| refuted | contradiction", "| refuted | seems speculative"), 1,
         "verdicts:2: basis: requirements/release-notes/missing-flag: 'seems speculative' is not one of the five refutation bases"),
        ("malformed confirmed basis is withheld by name", PACKET,
         _replace(full, "| confirmed | packages/browserContext.ts:291", "| confirmed | prose without citation"), 1,
         "verdicts:1: basis: code/browser-context/remove-cookies-race: 'prose without citation' is not the path:line"),
        ("malformed confirmed basis lands in withheld", PACKET,
         _replace(full, "| confirmed | packages/browserContext.ts:291", "| confirmed | prose without citation"), 1,
         "withheld: code/browser-context/remove-cookies-race"),
        ("malformed duplicate beside a valid row is withheld", PACKET,
         _replace(full, VERDICTS_HEAD,
                  VERDICTS_HEAD + "code/browser-context/remove-cookies-race | refuted | seems speculative\n"), 1,
         "withheld: code/browser-context/remove-cookies-race"),
        ("short row naming an expected id is withheld", PACKET,
         _replace(full, "| confirmed | packages/browserContext.ts:291", "| confirmed"), 1,
         "verdicts:1: field count: code/browser-context/remove-cookies-race: expected three"),
        ("short row naming an expected id lands in withheld", PACKET,
         _replace(full, "| confirmed | packages/browserContext.ts:291", "| confirmed"), 1,
         "withheld: code/browser-context/remove-cookies-race"),
        ("malformed ruling is withheld by name", PACKET,
         _replace(full, "code-2 | holds |", "code-2 | stands |"), 1,
         "accounted: code/browser-context/remove-cookies-race, requirements/release-notes/missing-flag\nwithheld: code-2"),
        ("plausible names what is unsettled", PACKET,
         _replace(full, "| refuted | contradiction", "| plausible | impact"), 0,
         "candidate requirements/release-notes/missing-flag | plausible | impact"),
        ("plausible with a stray basis", PACKET,
         _replace(full, "| refuted | contradiction", "| plausible | needs an operator"), 1,
         "verdicts:2: basis: requirements/release-notes/missing-flag: 'needs an operator' is not trigger or impact"),
        ("confirmed without a quoted line", PACKET,
         _replace(full, "| confirmed | packages/browserContext.ts:291", "| confirmed | it clearly races"), 1,
         "verdicts:1: basis: code/browser-context/remove-cookies-race: 'it clearly races' is not the path:line of the quoted defect line"),
        ("empty basis", PACKET,
         _replace(full, "| confirmed | packages/browserContext.ts:291", "| confirmed |"), 1,
         "verdicts:1: basis: code/browser-context/remove-cookies-race: the basis field is empty"),
        ("field count", PACKET,
         _replace(full, "| confirmed | packages/browserContext.ts:291", "| confirmed"), 1,
         "verdicts:1: field count"),
        ("header row", PACKET,
         _replace(full, VERDICTS_HEAD, VERDICTS_HEAD + "id | verdict | basis\n"), 1,
         "verdicts:1: header row"),
        ("missing ruling", PACKET,
         _replace(full, "code-2 | holds | packages/browserContext.ts:538\n", "code-9 | holds | packages/browserContext.ts:538\n"), 1,
         "rulings:0: missing ruling: code-2 has no record"),
        ("duplicate ruling", PACKET,
         _replace(full, RULINGS_HEAD, RULINGS_HEAD + "code-2 | re-open | packages/browserContext.ts:600\n"), 1,
         "rulings:2: duplicate ruling: code-2 appears 2 times"),
        ("unexpected row id", PACKET,
         _replace(full, RULINGS_HEAD, RULINGS_HEAD + "code-9 | holds | packages/browserContext.ts:600\n"), 1,
         "rulings:1: unexpected id: 'code-9' is not a ruling the verifier was given"),
        ("malformed ruling", PACKET,
         _replace(full, "code-2 | holds |", "code-2 | stands |"), 1,
         "rulings:1: ruling: code-2: 'stands' is not one of holds, re-open"),
        ("holds citing the row's own evidence", PACKET,
         _replace(full, "code-2 | holds | packages/browserContext.ts:538",
                  "code-2 | holds | `packages/browserContext.ts:540-544`"), 1,
         "rulings:1: evidence: code-2: a holds ruling cites `packages/browserContext.ts:540-544`, the row's own evidence"),
        ("re-open may cite the row's evidence", PACKET,
         _replace(full, "code-2 | holds | packages/browserContext.ts:538",
                  "code-2 | re-open | packages/browserContext.ts:540-544"), 0,
         "acquittal code-2 | re-open | packages/browserContext.ts:540-544"),
        ("ruling evidence prose", PACKET,
         _replace(full, "code-2 | holds | packages/browserContext.ts:538",
                  "code-2 | holds | the reset branch takes the lock"), 1,
         "rulings:1: evidence: code-2: 'the reset branch takes the lock' is not one path:line"),
        ("blocks out of order", PACKET,
         _replace(_replace(full, "```rulings\ncode-2 | holds | packages/browserContext.ts:538\n```\n", ""),
                  VERDICTS_HEAD, "```rulings\ncode-2 | holds | packages/browserContext.ts:538\n```\n" + VERDICTS_HEAD), 1,
         "return:0: block order"),
        ("trailing block", PACKET, full + "```text\ntrailing\n```\n", 1, "return:0: block order"),
        ("no acquittals supplied, rulings None", no_rows,
         _replace(full, "code-2 | holds | packages/browserContext.ts:538\n", "None.\n"), 0,
         "candidate code/browser-context/remove-cookies-race | confirmed | packages/browserContext.ts:291"),
        ("no acquittals supplied, rulings empty", no_rows,
         _replace(full, "code-2 | holds | packages/browserContext.ts:538\n", ""), 0, "candidate "),
        ("no acquittals supplied, ruling invented", no_rows, full, 1,
         "rulings:1: unexpected id: 'code-2' is not a ruling the verifier was given"),
        ("violations leave the other ids accounted", PACKET,
         _replace(full, "requirements/release-notes/missing-flag | refuted | contradiction\n", ""), 1,
         "accounted: code/browser-context/remove-cookies-race, code-2\nwithheld: requirements/release-notes/missing-flag"),
        ("empty response withholds everything", PACKET, "", 1,
         "accounted: (none)\nwithheld: code/browser-context/remove-cookies-race, requirements/release-notes/missing-flag, code-2"),
    ]


def run_self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)

        def invoke(packet_path: Path, text: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, __file__, "--packet", str(packet_path)],
                input=text,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

        for name, packet, text, expected_code, expected_text in self_test_cases():
            packet_path = root / "packet.json"
            packet_path.write_text(json.dumps(packet), encoding="utf-8")
            result = invoke(packet_path, text)
            if result.returncode == 2:
                print(f"account_verifier_return --self-test: {name}: {result.stderr.strip()}", file=sys.stderr)
                return 2
            if result.returncode != expected_code or expected_text not in result.stdout:
                failures.append(
                    f"{name}: expected exit {expected_code} containing {expected_text!r}; "
                    f"got exit {result.returncode} with output {result.stdout.strip()!r}"
                )
        # The accounted and withheld lines partition the packet on every exit-1 run.
        packet_path = root / "packet.json"
        packet_path.write_text(json.dumps(PACKET), encoding="utf-8")
        result = invoke(
            packet_path,
            _replace(RETURN, "requirements/release-notes/missing-flag | refuted | contradiction\n", ""),
        )
        lines = result.stdout.splitlines()
        if not (len(lines) >= 2 and lines[-2].startswith("accounted: ") and lines[-1].startswith("withheld: ")):
            failures.append(f"exit-1 output does not end with the accounted and withheld lines: {lines!r}")
        else:
            listed = [x for x in (lines[-2][len("accounted: "):] + ", " + lines[-1][len("withheld: "):]).split(", ") if x != "(none)"]
            expected_ids = [c["id"] for c in PACKET["candidates"]] + [a["id"] for a in PACKET["acquittals"]]
            if sorted(listed) != sorted(expected_ids):
                failures.append(f"accounted and withheld do not partition the packet: {listed!r}")
        if "accounted:" in "".join(l for l in lines if l.startswith("verdicts:")):
            failures.append("a violation line carried the accounting summary")

        empty = root / "empty.json"
        empty.write_text(json.dumps({"candidates": [], "acquittals": []}), encoding="utf-8")
        result = invoke(empty, RETURN)
        if result.returncode != 2 or "clean-review path" not in result.stderr:
            failures.append(
                f"empty packet: expected exit 2 naming the clean-review path; got exit "
                f"{result.returncode} with stderr {result.stderr.strip()!r}"
            )
        result = invoke(root / "absent.json", RETURN)
        if result.returncode != 2 or "cannot read packet" not in result.stderr:
            failures.append(
                f"unreadable packet: expected exit 2 naming the packet; got exit "
                f"{result.returncode} with stderr {result.stderr.strip()!r}"
            )
        broken = root / "broken.json"
        broken.write_text("{not json", encoding="utf-8")
        result = invoke(broken, RETURN)
        if result.returncode != 2 or "is not JSON" not in result.stderr:
            failures.append(
                f"malformed packet: expected exit 2 naming JSON; got exit "
                f"{result.returncode} with stderr {result.stderr.strip()!r}"
            )
    for failure in failures:
        print(failure)
    if failures:
        return 1
    print(f"account_verifier_return --self-test: {len(self_test_cases()) + 4} cases passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Account a verifier return, read from stdin, against the builder's packet."
    )
    parser.add_argument("--packet", help="the JSON packet build_verifier_prompt.py --packet wrote")
    parser.add_argument("--self-test", action="store_true", help="run the embedded fixtures and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.packet:
        parser.error("--packet is required unless --self-test is given")

    try:
        packet = read_packet(args.packet)
        return_text = sys.stdin.buffer.read().decode("utf-8")
    except InputError as error:
        print(f"account_verifier_return: {error}", file=sys.stderr)
        return 2
    except (OSError, UnicodeDecodeError) as error:
        print(f"account_verifier_return: cannot read the return from stdin: {error}", file=sys.stderr)
        return 2

    normalized, violations, accounted, withheld = account(return_text, packet)
    if violations:
        for violation in violations:
            print(violation.render())
        print("accounted: " + (", ".join(accounted) or "(none)"))
        print("withheld: " + (", ".join(withheld) or "(none)"))
        return 1
    for line in normalized:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
