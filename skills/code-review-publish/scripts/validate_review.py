#!/usr/bin/env python3
"""Validate a would-be code-review-publish review against the mechanical
rules of ``references/output-contract.md`` and ``references/review-rubric.md``.

The reviewer keeps every semantic judgment (is the evidence real, is the fix
location real, is a candidate a duplicate, is a question or observation
eligible, is coverage complete, is the status right). This script only checks
the rules that are decidable from the rendered payload itself.

Usage::

    python3 scripts/validate_review.py < payload.json
    python3 scripts/validate_review.py --self-test

Exit codes: ``0`` valid, ``1`` one or more violations (one line each, in the
form ``<location>: <rule>: <detail>``), ``2`` the payload could not be read.

Input schema (JSON object on stdin)::

    {
      "summary": {
        "body": "<complete summary markdown, run trailer included>",
        "trailer": "<!-- review-run ... -->",      # optional; else read from body
        "anchors": ["src/payments.ts:42"]          # optional; else read from body
      },
      "items": [
        {
          "type": "finding",
          "markdown": "<complete visible comment prose, trailer excluded>",
          "trailer": "<!-- finding id=... head=... priority=... action=...\n
                       blocking=... kind=... fix=... -->",
          "priority": "P1",            # findings only
          "action": "must-fix",        # must-fix | consider | question
          "blocking": true,            # findings only
          "kind": "bug",               # findings only
          "anchor": {"type": "line", "path": "src/payments.ts",
                     "start_line": 42, "end_line": 44, "side": "RIGHT"},
          "fix": "src/retry-policy.ts:18"          # optional
        },
        {
          "type": "question",
          "markdown": "...", "trailer": "<!-- question id=... head=... action=question -->",
          "anchor": {"type": "file", "path": "src/queue.ts"}
        },
        {"type": "observation", "markdown": "One sentence. Evidence: `redis.conf:1903`."}
      ]
    }

A file anchor carries exactly ``type`` and ``path``; a line anchor also carries
``start_line``, ``end_line``, and ``side``. ``summary.anchors`` holds the
durable summary coordinates in their rendered form (``path:line``,
``path:start-end``, or ``path (file)``).

Where a check could disagree with the reference text, the reference text wins
and this script is the thing that must be fixed. Three deliberate reading notes:
the observation evidence check requires an ``Evidence:`` pointer rather than
exactly one coordinate, because the output contract's own example pairs two
coordinates for a single drift pointer; ``context`` is a SHA-256 digest
rather than a commit SHA, so the 40-hex commit rule does not apply to it; and
the one-sentence observation check masks the abbreviations ``e.g.``, ``i.e.``,
``etc.``, ``vs.``, ``cf.``, and ``et al.`` so they do not count as sentence
breaks.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

WORKFLOW = "v5a-1"
PRIORITIES = ("P0", "P1", "P2", "P3")
ACTIONS = ("must-fix", "consider")
KINDS = (
    "bug",
    "concurrency",
    "invariant",
    "security",
    "performance",
    "maintainability",
    "requirement",
)
COVERAGE = ("complete", "incomplete")
SIDES = ("LEFT", "RIGHT")
MAX_OBSERVATIONS = 3
PERMISSION_SENTENCE = "Closing this without action is a correct response."
QUESTION_FRAMING = "Change no code for this"

COMMIT_SHA_KEYS = ("head", "base-sha", "merge-base")
RUN_REQUIRED = (
    "head",
    "base-ref",
    "base-sha",
    "merge-base",
    "workflow",
    "context",
    "issues",
    "coverage",
)
FINDING_REQUIRED = ("id", "head", "priority", "action", "blocking", "kind")
FINDING_OPTIONAL = ("fix",)
QUESTION_REQUIRED = ("id", "head", "action")
QUESTION_OPTIONAL = ()

COMMIT_SHA_RE = re.compile(r"\A[0-9a-f]{40}\Z")
DIGEST_RE = re.compile(r"\A[0-9a-f]{64}\Z")
TOKEN_RE = re.compile(r"\A[!-~]+\Z")
BAD_PERCENT_RE = re.compile(r"%(?![0-9A-Fa-f]{2})")
ISSUE_RE = re.compile(r"\A[^/\s#]+/[^/\s#]+#[0-9]+\Z")
LINE_COORD_RE = re.compile(r"\A(?P<path>[^\s:]+):(?P<start>[0-9]+)(?:-(?P<end>[0-9]+))?\Z")
FILE_COORD_RE = re.compile(r"\A(?P<path>\S+) \(file\)\Z")
TRAILER_RE = re.compile(r"\A<!--\s+(?P<kind>\S+)(?P<fields>(?:\s+\S+)*)\s+-->\Z")
RUN_TRAILER_RE = re.compile(r"<!--\s+review-run\b[^>]*-->")
FINDING_TITLE_RE = re.compile(r"\A\*\*\[(?P<priority>[^\]]+)\]\s+\[(?P<action>[^\]]+)\]")
QUESTION_TITLE_RE = re.compile(r"\A\*\*\[(?P<tag>[^\]]+)\]")
SUMMARY_ANCHOR_RE = re.compile(r"anchor `(?P<coordinate>[^`]+)`")
SUMMARY_FIX_RE = re.compile(r"fix `(?P<coordinate>[^`]+)`")
WORD_SHOULD_MUST_RE = re.compile(r"\b(should|must)\b", re.IGNORECASE)
ABBREVIATION_RE = re.compile(r"\b(?:e\.g|i\.e|etc|vs|cf|et al)\.(?=\s)", re.IGNORECASE)


class Report:
    """Collects violations as ``<location>: <rule>: <detail>`` lines."""

    def __init__(self) -> None:
        self.lines: list[str] = []

    def add(self, location: str, rule: str, detail: str) -> None:
        self.lines.append(f"{location}: {rule}: {detail}")

    def rules(self) -> set[str]:
        return {line.split(": ", 2)[1] for line in self.lines}


def parse_trailer(raw: str) -> tuple[str, list[tuple[str, str]]] | None:
    match = TRAILER_RE.match(raw.strip())
    if match is None:
        return None
    pairs: list[tuple[str, str]] = []
    for token in match.group("fields").split():
        key, separator, value = token.partition("=")
        if not separator or not key:
            return None
        pairs.append((key, value))
    return match.group("kind"), pairs


def check_trailer(
    report: Report,
    location: str,
    raw: Any,
    expected_kind: str,
    required: tuple[str, ...],
    optional: tuple[str, ...],
) -> dict[str, str]:
    if not isinstance(raw, str):
        report.add(location, "schema", "trailer must be a string")
        return {}
    parsed = parse_trailer(raw)
    if parsed is None:
        report.add(
            location,
            "trailer-grammar",
            "trailer must be `<!-- <type> key=value ... -->` with space-separated key=value tokens",
        )
        return {}
    kind, pairs = parsed
    if kind != expected_kind:
        report.add(location, "trailer-grammar", f"trailer type is `{kind}`, expected `{expected_kind}`")
    fields: dict[str, str] = {}
    for key, value in pairs:
        if key in fields:
            report.add(location, "trailer-grammar", f"duplicate trailer key `{key}`")
        fields[key] = value
    for key in required:
        if key not in fields:
            report.add(location, "trailer-grammar", f"missing required trailer key `{key}`")
    allowed = set(required) | set(optional)
    for key in fields:
        if key not in allowed:
            report.add(location, "trailer-grammar", f"unknown trailer key `{key}`")
    for key, value in fields.items():
        if not value:
            report.add(location, "trailer-grammar", f"trailer key `{key}` has an empty value")
            continue
        if not TOKEN_RE.match(value):
            report.add(
                location,
                "trailer-grammar",
                f"trailer value for `{key}` must be a single printable ASCII token",
            )
        if BAD_PERCENT_RE.search(value):
            report.add(
                location,
                "trailer-grammar",
                f"trailer value for `{key}` has a `%` that is not percent-encoded",
            )
    for key in COMMIT_SHA_KEYS:
        value = fields.get(key)
        if value is not None and not COMMIT_SHA_RE.match(value):
            report.add(
                location,
                "trailer-sha",
                f"`{key}={value}` must be exactly 40 lowercase hexadecimal characters",
            )
    return fields


def check_coordinate(report: Report, location: str, rule: str, coordinate: Any, allow_file: bool) -> None:
    if not isinstance(coordinate, str) or not coordinate:
        report.add(location, "schema", "coordinate must be a non-empty string")
        return
    if FILE_COORD_RE.match(coordinate):
        if not allow_file:
            report.add(location, rule, f"`{coordinate}` must be `path:line` or `path:start-end`")
        return
    match = LINE_COORD_RE.match(coordinate)
    if match is None:
        forms = "`path:line`, `path:start-end`, or `path (file)`" if allow_file else "`path:line` or `path:start-end`"
        report.add(location, rule, f"`{coordinate}` is not one of {forms}")
        return
    end = match.group("end")
    if end is not None and int(end) <= int(match.group("start")):
        report.add(
            location,
            rule,
            f"`{coordinate}` is a range, so start must be less than end; a single line uses `path:line`",
        )


def check_run_trailer(report: Report, location: str, raw: Any) -> None:
    fields = check_trailer(report, location, raw, "review-run", RUN_REQUIRED, ())
    workflow = fields.get("workflow")
    if workflow is not None and workflow != WORKFLOW:
        report.add(location, "trailer-grammar", f"`workflow={workflow}` must be `{WORKFLOW}`")
    context = fields.get("context")
    if context is not None and not DIGEST_RE.match(context):
        report.add(location, "trailer-grammar", "`context` must be a 64-character lowercase SHA-256 digest")
    coverage = fields.get("coverage")
    if coverage is not None and coverage not in COVERAGE:
        report.add(location, "trailer-grammar", f"`coverage={coverage}` must be one of {list(COVERAGE)}")
    issues = fields.get("issues")
    if issues is not None and issues != "none":
        coordinates = issues.split(",")
        for coordinate in coordinates:
            if not ISSUE_RE.match(coordinate):
                report.add(
                    location,
                    "trailer-grammar",
                    f"issue coordinate `{coordinate}` must be `owner/repo#number` or the whole value `none`",
                )
        if coordinates != sorted(coordinates):
            report.add(location, "trailer-grammar", "issue coordinates must be sorted")


def check_summary(report: Report, summary: Any) -> None:
    if not isinstance(summary, dict):
        report.add("summary", "schema", "summary must be an object")
        return
    body = summary.get("body")
    if not isinstance(body, str) or not body.strip():
        report.add("summary", "schema", "summary.body must be a non-empty string")
        body = ""
    raw_trailer = summary.get("trailer")
    if raw_trailer is None:
        match = RUN_TRAILER_RE.search(body)
        if match is None:
            report.add("summary", "trailer-grammar", "summary carries no `review-run` trailer")
        else:
            check_run_trailer(report, "summary.trailer", match.group(0))
    else:
        check_run_trailer(report, "summary.trailer", raw_trailer)
        if isinstance(raw_trailer, str) and raw_trailer.strip() and raw_trailer.strip() not in body:
            report.add("summary", "trailer-grammar", "summary.trailer does not appear in summary.body")

    anchors = summary.get("anchors")
    if anchors is None:
        anchors = [match.group("coordinate") for match in SUMMARY_ANCHOR_RE.finditer(body)]
        fixes = [match.group("coordinate") for match in SUMMARY_FIX_RE.finditer(body)]
    elif not isinstance(anchors, list):
        report.add("summary.anchors", "schema", "summary.anchors must be an array")
        return
    else:
        fixes = []
    for index, coordinate in enumerate(anchors):
        check_coordinate(report, f"summary.anchors[{index}]", "summary-anchor", coordinate, allow_file=True)
    for index, coordinate in enumerate(fixes):
        check_coordinate(report, f"summary.fix[{index}]", "fix-coordinate", coordinate, allow_file=False)


def check_anchor(report: Report, location: str, anchor: Any) -> None:
    if not isinstance(anchor, dict):
        report.add(location, "schema", "anchor must be an object")
        return
    anchor_type = anchor.get("type")
    path = anchor.get("path")
    if not isinstance(path, str) or not path:
        report.add(location, "anchor-shape", "anchor needs a non-empty `path`")
    if anchor_type == "file":
        extra = sorted(set(anchor) - {"type", "path"})
        if extra:
            report.add(location, "anchor-shape", f"a file anchor carries only `type` and `path`; found {extra}")
        return
    if anchor_type != "line":
        report.add(location, "anchor-shape", f"anchor `type` must be `line` or `file`, not `{anchor_type!r}`")
        return
    start = anchor.get("start_line")
    end = anchor.get("end_line")
    side = anchor.get("side")
    if not isinstance(start, int) or isinstance(start, bool) or start < 1:
        report.add(location, "anchor-shape", "a line anchor needs an integer `start_line` of at least 1")
    if not isinstance(end, int) or isinstance(end, bool) or end < 1:
        report.add(location, "anchor-shape", "a line anchor needs an integer `end_line` of at least 1")
    if isinstance(start, int) and isinstance(end, int) and not isinstance(start, bool) and not isinstance(end, bool):
        if end < start:
            report.add(location, "anchor-shape", "a line anchor range must have `end_line` at or after `start_line`")
    if side not in SIDES:
        report.add(location, "anchor-shape", f"a line anchor needs `side` in {list(SIDES)}, not `{side!r}`")


def check_finding(report: Report, location: str, item: dict[str, Any]) -> None:
    markdown = item.get("markdown")
    if not isinstance(markdown, str) or not markdown.strip():
        report.add(location, "schema", "finding needs non-empty `markdown`")
        markdown = ""
    priority = item.get("priority")
    action = item.get("action")
    blocking = item.get("blocking")
    kind = item.get("kind")

    if priority not in PRIORITIES:
        report.add(location, "priority-action", f"priority `{priority!r}` must be one of {list(PRIORITIES)}")
    if action not in ACTIONS:
        report.add(location, "priority-action", f"action `{action!r}` must be one of {list(ACTIONS)}")
    if not isinstance(blocking, bool):
        report.add(location, "priority-action", "blocking must be a boolean")
    if kind not in KINDS:
        report.add(location, "trailer-agreement", f"kind `{kind!r}` must be one of {list(KINDS)}")

    if priority == "P0" and action != "must-fix":
        report.add(location, "priority-action", "P0 is inherently `must-fix`")
    if action == "must-fix" and blocking is not True:
        report.add(location, "priority-action", "`must-fix` requires `blocking=true`")
    if action == "consider" and blocking is not False:
        report.add(location, "priority-action", "`consider` requires `blocking=false`")

    change_at = markdown.find("**Change:**")
    source_at = markdown.find("**Source:**")
    if change_at < 0:
        report.add(location, "field-order", "a finding states `Change`")
    if source_at >= 0 and change_at >= 0 and source_at < change_at:
        report.add(location, "field-order", "optional `Source` follows `Change`")
    trailing = markdown.rstrip()
    if action == "consider":
        if not trailing.endswith(PERMISSION_SENTENCE):
            report.add(
                location,
                "field-order",
                f"a `consider` finding ends with `{PERMISSION_SENTENCE}` as the last text before the trailer",
            )
    elif PERMISSION_SENTENCE in markdown:
        report.add(location, "field-order", "the close-without-action sentence belongs to `consider` findings only")

    title = FINDING_TITLE_RE.match(markdown.lstrip())
    if title is None:
        report.add(location, "trailer-agreement", "a finding title opens with `**[<priority>] [<action>] ...**`")
    else:
        if priority in PRIORITIES and title.group("priority") != priority:
            report.add(
                location,
                "trailer-agreement",
                f"visible priority `{title.group('priority')}` disagrees with `{priority}`",
            )
        if action in ACTIONS and title.group("action") != action:
            report.add(
                location,
                "trailer-agreement",
                f"visible action `{title.group('action')}` disagrees with `{action}`",
            )

    check_anchor(report, f"{location}.anchor", item.get("anchor"))
    fix = item.get("fix")
    if fix is not None:
        check_coordinate(report, f"{location}.fix", "fix-coordinate", fix, allow_file=False)

    fields = check_trailer(report, f"{location}.trailer", item.get("trailer"), "finding", FINDING_REQUIRED, FINDING_OPTIONAL)
    for key, value in (("priority", priority), ("action", action), ("kind", kind)):
        rendered = fields.get(key)
        if rendered is not None and value is not None and rendered != value:
            report.add(f"{location}.trailer", "trailer-agreement", f"`{key}={rendered}` disagrees with `{value}`")
    rendered_blocking = fields.get("blocking")
    if rendered_blocking is not None and isinstance(blocking, bool):
        if rendered_blocking != ("true" if blocking else "false"):
            report.add(
                f"{location}.trailer",
                "trailer-agreement",
                f"`blocking={rendered_blocking}` disagrees with `{blocking}`",
            )
    rendered_fix = fields.get("fix")
    if rendered_fix is not None:
        check_coordinate(report, f"{location}.trailer", "fix-coordinate", rendered_fix, allow_file=False)
    if rendered_fix is not None and isinstance(fix, str) and rendered_fix != fix:
        report.add(f"{location}.trailer", "trailer-agreement", f"`fix={rendered_fix}` disagrees with `{fix}`")
    if rendered_fix is None and isinstance(fix, str):
        report.add(f"{location}.trailer", "trailer-agreement", f"`fix` is set to `{fix}` but missing from the trailer")


def check_question(report: Report, location: str, item: dict[str, Any]) -> None:
    markdown = item.get("markdown")
    if not isinstance(markdown, str) or not markdown.strip():
        report.add(location, "schema", "question needs non-empty `markdown`")
        markdown = ""
    if item.get("priority") is not None:
        report.add(location, "question-form", "a question has no priority")
    if item.get("blocking") is not None:
        report.add(location, "question-form", "a question has no blocking flag")
    action = item.get("action")
    if action is not None and action != "question":
        report.add(location, "question-form", f"a question's action is `question`, not `{action}`")
    if "**Change:**" in markdown:
        report.add(location, "question-form", "a question requests no code change, so it states no `Change` field")
    if QUESTION_FRAMING not in markdown:
        report.add(location, "question-form", f"a question carries the `{QUESTION_FRAMING}` framing")
    title = QUESTION_TITLE_RE.match(markdown.lstrip())
    if title is None or title.group("tag") != "Question":
        report.add(location, "question-form", "a question title opens with `**[Question] ...**`")

    check_anchor(report, f"{location}.anchor", item.get("anchor"))
    fields = check_trailer(
        report, f"{location}.trailer", item.get("trailer"), "question", QUESTION_REQUIRED, QUESTION_OPTIONAL
    )
    rendered_action = fields.get("action")
    if rendered_action is not None and rendered_action != "question":
        report.add(f"{location}.trailer", "question-form", f"`action={rendered_action}` must be `question`")


def check_observation(report: Report, location: str, item: dict[str, Any]) -> None:
    markdown = item.get("markdown")
    if not isinstance(markdown, str) or not markdown.strip():
        report.add(location, "schema", "observation needs non-empty `markdown`")
        return
    for key in ("priority", "action", "blocking", "kind", "anchor", "trailer", "id", "fix"):
        if item.get(key) is not None:
            report.add(location, "observation-form", f"an observation carries no `{key}`")
    text = markdown.strip().lstrip("-").strip()
    if WORD_SHOULD_MUST_RE.search(text):
        report.add(location, "observation-form", "an observation uses descriptive language without `should` or `must`")
    claim, separator, evidence = text.partition("Evidence:")
    if not separator or not evidence.strip():
        report.add(location, "observation-form", "an observation ends with one `Evidence:` pointer")
        claim = text
    masked = ABBREVIATION_RE.sub(lambda m: m.group(0).replace(".", "\x00"), claim.strip())
    sentences = [part for part in masked.split(". ") if part.strip()]
    if len(sentences) != 1 or not claim.strip().endswith("."):
        report.add(location, "observation-form", "an observation is exactly one sentence before its evidence pointer")


def check_items(report: Report, items: Any) -> None:
    if not isinstance(items, list):
        report.add("items", "schema", "items must be an array")
        return
    observations = 0
    seen_ids: dict[str, int] = {}
    for index, item in enumerate(items):
        location = f"items[{index}]"
        if not isinstance(item, dict):
            report.add(location, "schema", "item must be an object")
            continue
        item_type = item.get("type")
        identity = item.get("id")
        if isinstance(identity, str) and item_type in ("finding", "question"):
            if identity in seen_ids:
                report.add(location, "trailer-agreement", f"stable id `{identity}` is already used by items[{seen_ids[identity]}]")
            seen_ids[identity] = index
            trailer = item.get("trailer")
            if isinstance(trailer, str):
                parsed = parse_trailer(trailer)
                if parsed is not None:
                    fields = dict(parsed[1])
                    if fields.get("id") not in (None, identity):
                        report.add(f"{location}.trailer", "trailer-agreement", f"`id={fields.get('id')}` disagrees with `{identity}`")
        if item_type == "finding":
            check_finding(report, location, item)
        elif item_type == "question":
            check_question(report, location, item)
        elif item_type == "observation":
            observations += 1
            check_observation(report, location, item)
        else:
            report.add(location, "schema", f"item `type` must be finding, question, or observation, not `{item_type!r}`")
    if observations > MAX_OBSERVATIONS:
        report.add("items", "observation-cap", f"at most {MAX_OBSERVATIONS} observations may publish; found {observations}")


def validate(payload: Any) -> list[str]:
    report = Report()
    if not isinstance(payload, dict):
        report.add("input", "schema", "payload must be a JSON object")
        return report.lines
    check_summary(report, payload.get("summary"))
    check_items(report, payload.get("items", []))
    return report.lines


HEAD = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
BASE_SHA = "b2c3d4e5f60718293a4b5c6d7e8f90123456789a"
MERGE_BASE = "d4e5f60718293a4b5c6d7e8f90123456789abcde"
CONTEXT = "91d34a2f4c869867167f0b31da7c207f4528e12e3d1ef4f107a5eabb4c18718e"

RUN_TRAILER = (
    f"<!-- review-run head={HEAD} base-ref=main base-sha={BASE_SHA} "
    f"merge-base={MERGE_BASE} workflow={WORKFLOW} context={CONTEXT} "
    "issues=acme/payments#123 coverage=complete -->"
)

SUMMARY_BODY = f"""**Changes Requested (advisory)** — 1 must-fix finding.

**Intent:** Add retries for charge submission without changing payment semantics.

**Issue fit:** Partial — retry availability is implemented, but acceptance criterion 2's idempotency guarantee remains open.

**Coverage:** Complete merge-base diff reviewed; payment callers and focused tests inspected.

**Reviewed:** `a1b2c3d` against merge-base `d4e5f6a`.

## Findings

- [P1] [must-fix] Preserve the idempotency key across retries — anchor `src/payments.ts:42`; fix `src/retry-policy.ts:18`

{RUN_TRAILER}
"""

FINDING_MARKDOWN = """**[P1] [must-fix] Preserve the idempotency key across retries**

**Triggers when:** The server commits a charge but its response times out and the
client retries.

**Impact:** The retry uses a new idempotency key and can submit a second charge.

**Change:** In `src/retry-policy.ts`, reuse one idempotency key across every attempt
for the same logical charge.

**Source:** Issue #123, acceptance criterion 2."""

QUESTION_MARKDOWN = """**[Question] Must retries preserve request order?**

**Evidence:** The new queue retries at the tail, while existing callers consume it
as FIFO. The issue, tests, and history do not establish whether reordering is allowed.

**Why it matters:** The answer determines whether this is a merge-blocking regression.

**Change no code for this.** Confirm whether retry order is part of the contract;
the maintainer answer settles whether the candidate should re-open as a finding."""

OBSERVATION_MARKDOWN = (
    "The first configuration sentence covers same-shard re-points more broadly than "
    "the implementation does. Evidence: `redis.conf:1903`, `src/replication.c:2701`."
)


def valid_payload() -> dict[str, Any]:
    """The output contract's own example review, in payload form."""
    return {
        "summary": {"body": SUMMARY_BODY, "trailer": RUN_TRAILER},
        "items": [
            {
                "type": "finding",
                "id": "payments/retry-idempotency",
                "markdown": FINDING_MARKDOWN,
                "trailer": (
                    f"<!-- finding id=payments/retry-idempotency head={HEAD} priority=P1 "
                    "action=must-fix blocking=true kind=requirement fix=src/retry-policy.ts:18 -->"
                ),
                "priority": "P1",
                "action": "must-fix",
                "blocking": True,
                "kind": "requirement",
                "anchor": {
                    "type": "line",
                    "path": "src/payments.ts",
                    "start_line": 42,
                    "end_line": 42,
                    "side": "RIGHT",
                },
                "fix": "src/retry-policy.ts:18",
            },
            {
                "type": "question",
                "id": "queue/retry-order",
                "markdown": QUESTION_MARKDOWN,
                "trailer": f"<!-- question id=queue/retry-order head={HEAD} action=question -->",
                "anchor": {"type": "file", "path": "src/queue.ts"},
            },
            {"type": "observation", "markdown": OBSERVATION_MARKDOWN},
        ],
    }


def consider_payload() -> dict[str, Any]:
    """A `consider` finding with a `Source`, exercising the F1.5 field order."""
    payload = valid_payload()
    finding = payload["items"][0]
    finding["priority"] = "P3"
    finding["action"] = "consider"
    finding["blocking"] = False
    finding["kind"] = "maintainability"
    finding["markdown"] = (
        FINDING_MARKDOWN.replace("[P1] [must-fix]", "[P3] [consider]")
        + f"\n\n{PERMISSION_SENTENCE}"
    )
    finding["trailer"] = (
        f"<!-- finding id=payments/retry-idempotency head={HEAD} priority=P3 "
        "action=consider blocking=false kind=maintainability fix=src/retry-policy.ts:18 -->"
    )
    payload["summary"]["body"] = SUMMARY_BODY.replace("[P1] [must-fix]", "[P3] [consider]")
    return payload


def abbreviation_payload() -> dict[str, Any]:
    """An observation whose abbreviation must not read as a sentence break."""
    payload = valid_payload()
    payload["items"][2]["markdown"] = (
        "The first configuration sentence covers more re-point shapes (e.g. same-shard "
        "moves) than the implementation does. Evidence: `redis.conf:1903`."
    )
    return payload


def _mutate(mutation) -> dict[str, Any]:
    payload = valid_payload()
    mutation(payload)
    return payload


def _set_summary_anchor(payload: dict[str, Any], coordinate: str) -> None:
    payload["summary"]["anchors"] = [coordinate]


def failing_cases() -> list[tuple[str, dict[str, Any], str]]:
    """(name, payload, rule expected in the violation output)."""

    def abbreviate_head(payload):
        payload["items"][0]["trailer"] = payload["items"][0]["trailer"].replace(HEAD, "a1b2c3d")

    def abbreviate_run_head(payload):
        payload["summary"]["trailer"] = payload["summary"]["trailer"].replace(f"head={HEAD}", "head=a1b2c3d")

    def uppercase_merge_base(payload):
        payload["summary"]["trailer"] = payload["summary"]["trailer"].replace(
            MERGE_BASE, MERGE_BASE.upper()
        )

    def source_before_change(payload):
        finding = payload["items"][0]
        finding["markdown"] = (
            "**[P1] [must-fix] Preserve the idempotency key across retries**\n\n"
            "**Source:** Issue #123, acceptance criterion 2.\n\n"
            "**Change:** Reuse one idempotency key across every attempt."
        )

    def consider_without_permission(payload):
        finding = payload["items"][0]
        finding["priority"] = "P3"
        finding["action"] = "consider"
        finding["blocking"] = False
        finding["markdown"] = FINDING_MARKDOWN.replace("[P1] [must-fix]", "[P3] [consider]")
        finding["trailer"] = (
            f"<!-- finding id=payments/retry-idempotency head={HEAD} priority=P3 "
            "action=consider blocking=false kind=requirement fix=src/retry-policy.ts:18 -->"
        )

    def consider_permission_not_last(payload):
        payload_finding = consider_payload()["items"][0]
        payload_finding["markdown"] = (
            payload_finding["markdown"].replace(f"\n\n{PERMISSION_SENTENCE}", "")
            + f"\n\n{PERMISSION_SENTENCE}\n\n**Impact:** trailing text after the permission sentence."
        )
        payload["items"][0] = payload_finding
        payload["summary"]["body"] = SUMMARY_BODY.replace("[P1] [must-fix]", "[P3] [consider]")

    def p0_consider(payload):
        finding = payload["items"][0]
        finding["priority"] = "P0"
        finding["action"] = "consider"
        finding["blocking"] = False
        finding["markdown"] = FINDING_MARKDOWN.replace("[P1] [must-fix]", "[P0] [consider]") + f"\n\n{PERMISSION_SENTENCE}"
        finding["trailer"] = (
            f"<!-- finding id=payments/retry-idempotency head={HEAD} priority=P0 "
            "action=consider blocking=false kind=requirement fix=src/retry-policy.ts:18 -->"
        )

    def must_fix_not_blocking(payload):
        payload["items"][0]["blocking"] = False
        payload["items"][0]["trailer"] = payload["items"][0]["trailer"].replace("blocking=true", "blocking=false")

    def consider_blocking(payload):
        finding = consider_payload()["items"][0]
        finding["blocking"] = True
        finding["trailer"] = finding["trailer"].replace("blocking=false", "blocking=true")
        payload["items"][0] = finding
        payload["summary"]["body"] = SUMMARY_BODY.replace("[P1] [must-fix]", "[P3] [consider]")

    def question_with_priority(payload):
        payload["items"][1]["priority"] = "P2"

    def question_requests_code(payload):
        payload["items"][1]["markdown"] = QUESTION_MARKDOWN + "\n\n**Change:** Reorder the queue."

    def question_without_framing(payload):
        payload["items"][1]["markdown"] = QUESTION_MARKDOWN.replace(
            "**Change no code for this.** ", ""
        )

    def four_observations(payload):
        payload["items"].extend(
            {"type": "observation", "markdown": OBSERVATION_MARKDOWN} for _ in range(3)
        )

    def observation_with_should(payload):
        payload["items"][2]["markdown"] = (
            "The configuration should cover same-shard re-points. Evidence: `redis.conf:1903`."
        )

    def observation_two_sentences(payload):
        payload["items"][2]["markdown"] = (
            "The configuration covers same-shard re-points. The implementation narrows it. "
            "Evidence: `redis.conf:1903`."
        )

    def observation_without_evidence(payload):
        payload["items"][2]["markdown"] = "The configuration covers same-shard re-points."

    def unknown_trailer_key(payload):
        payload["items"][0]["trailer"] = payload["items"][0]["trailer"].replace(
            "kind=requirement", "kind=requirement confidence=high"
        )

    def missing_trailer_key(payload):
        payload["items"][0]["trailer"] = payload["items"][0]["trailer"].replace("kind=requirement ", "")

    def wrong_workflow(payload):
        payload["summary"]["trailer"] = payload["summary"]["trailer"].replace(
            f"workflow={WORKFLOW}", "workflow=v5-1"
        )

    def malformed_trailer(payload):
        payload["items"][0]["trailer"] = "<!-- finding id payments/retry-idempotency -->"

    def line_anchor_without_side(payload):
        del payload["items"][0]["anchor"]["side"]

    def file_anchor_with_side(payload):
        payload["items"][1]["anchor"] = {"type": "file", "path": "src/queue.ts", "side": "RIGHT"}

    def trailer_disagreement(payload):
        payload["items"][0]["trailer"] = payload["items"][0]["trailer"].replace("priority=P1", "priority=P2")

    return [
        ("abbreviated finding head", _mutate(abbreviate_head), "trailer-sha"),
        ("abbreviated run head", _mutate(abbreviate_run_head), "trailer-sha"),
        ("uppercase merge-base", _mutate(uppercase_merge_base), "trailer-sha"),
        ("summary anchor with reversed range", _mutate(lambda p: _set_summary_anchor(p, "src/a.ts:44-42")), "summary-anchor"),
        ("summary anchor with equal range", _mutate(lambda p: _set_summary_anchor(p, "src/a.ts:42-42")), "summary-anchor"),
        ("summary anchor without coordinate", _mutate(lambda p: _set_summary_anchor(p, "src/a.ts")), "summary-anchor"),
        ("Source before Change", _mutate(source_before_change), "field-order"),
        ("consider without permission sentence", _mutate(consider_without_permission), "field-order"),
        ("permission sentence not last", _mutate(consider_permission_not_last), "field-order"),
        ("P0 marked consider", _mutate(p0_consider), "priority-action"),
        ("must-fix not blocking", _mutate(must_fix_not_blocking), "priority-action"),
        ("consider blocking", _mutate(consider_blocking), "priority-action"),
        ("question with priority", _mutate(question_with_priority), "question-form"),
        ("question requesting code", _mutate(question_requests_code), "question-form"),
        ("question without framing", _mutate(question_without_framing), "question-form"),
        ("four observations", _mutate(four_observations), "observation-cap"),
        ("observation using should", _mutate(observation_with_should), "observation-form"),
        ("observation with two sentences", _mutate(observation_two_sentences), "observation-form"),
        ("observation without evidence", _mutate(observation_without_evidence), "observation-form"),
        ("unknown trailer key", _mutate(unknown_trailer_key), "trailer-grammar"),
        ("missing trailer key", _mutate(missing_trailer_key), "trailer-grammar"),
        ("wrong workflow", _mutate(wrong_workflow), "trailer-grammar"),
        ("malformed trailer", _mutate(malformed_trailer), "trailer-grammar"),
        ("line anchor without side", _mutate(line_anchor_without_side), "anchor-shape"),
        ("file anchor with extra field", _mutate(file_anchor_with_side), "anchor-shape"),
        ("trailer priority disagreement", _mutate(trailer_disagreement), "trailer-agreement"),
        ("payload is not an object", [], "schema"),
    ]


def self_test() -> int:
    failures: list[str] = []
    passing = (
        ("contract example review", valid_payload()),
        ("consider finding", consider_payload()),
        ("observation with abbreviation", abbreviation_payload()),
    )
    for name, payload in passing:
        lines = validate(payload)
        if lines:
            failures.append(f"{name}: expected no violations, got: {'; '.join(lines)}")
    for name, payload, rule in failing_cases():
        lines = validate(payload)
        if not lines:
            failures.append(f"{name}: expected a `{rule}` violation, got none")
        elif rule not in {line.split(": ", 2)[1] for line in lines}:
            failures.append(f"{name}: expected a `{rule}` violation, got: {'; '.join(lines)}")
    for failure in failures:
        print(failure)
    if failures:
        print(f"validate_review: {len(failures)} self-test case(s) failed")
        return 1
    print(f"validate_review: self-test passed ({len(passing) + len(failing_cases())} cases)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a would-be v5a review payload against the mechanical output-contract rules."
    )
    parser.add_argument("input", nargs="?", default="-", help="JSON file, or - for stdin")
    parser.add_argument("--self-test", action="store_true", help="run the embedded fixtures and exit")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    try:
        if args.input == "-":
            payload = json.load(sys.stdin)
        else:
            with open(args.input, encoding="utf-8") as input_file:
                payload = json.load(input_file)
    except (OSError, ValueError) as error:
        print(f"validate_review: {error}", file=sys.stderr)
        return 2

    violations = validate(payload)
    for line in violations:
        print(line)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
