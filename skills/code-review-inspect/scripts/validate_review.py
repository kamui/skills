#!/usr/bin/env python3
"""Validate a would-be code-review-inspect record against the mechanical
rules of ``references/review-record.md``, ``references/rendering.md``, and
``references/review-rubric.md``.

The reviewer keeps every semantic judgment (is the evidence real, is the fix
location real, is a candidate a duplicate, is a question or observation
eligible, is coverage complete, is the status right). This script only checks
the rules that are decidable from the rendered payload itself.

Usage::

    python3 scripts/validate_review.py < payload.json
    python3 scripts/validate_review.py --render < payload.json
    python3 scripts/validate_review.py --emit-batch < payload.json > batch.json
    python3 scripts/validate_review.py --self-test

``--render`` prints the exact summary reference fragment for each finding and
question item, one per line in item order, so the reviewer pastes generated
text into the summary body instead of composing a link by hand. The validator
then requires each fragment to appear in ``summary.body`` exactly once.

``--emit-batch`` validates the payload and, when it has zero violations,
prints the forge-native one-call review body as JSON: ``commit_id`` (the run
trailer's ``head``), ``event`` (``COMMENT``, ``REQUEST_CHANGES``, or ``APPROVE``),
``body`` (``summary.body``, unchanged for ``COMMENT``), and ``comments`` — one entry per finding or question with a line
anchor, in item order, carrying ``path``, ``line``/``side`` (the anchor's end
line and side), ``start_line``/``start_side`` when the anchor spans more than
one line, and ``body`` (the item's markdown, a blank line, then its trailer).
File-anchored items and observations produce no comment: the summary body
already carries their prose. A payload with any violation prints the
violations and emits nothing. On the gating path only, enforce the first-line
status grammar and event compatibility, remove the advisory suffix, and
re-validate that edited body before emission. The batch is what validated
after the one scripted edit; COMMENT keeps its existing acceptance rules.
The script never posts; the forge call belongs to code-review-publish.

Exit codes: ``0`` valid (or every fragment rendered, or the batch emitted),
``1`` one or more violations (one line each, in the form
``<location>: <rule>: <detail>``), ``2`` the payload could not be read.

Input schema (JSON object on stdin)::

    {
      "summary": {
        "body": "<complete summary markdown, run trailer included>",
        "trailer": "<!-- review-run ... -->",      # optional; else read from body
        "repository_url": "https://github.com/acme/payments"  # optional
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
        {
          "type": "finding", ...,
          "anchor": {"type": "file", "path": "src/legacy.ts", "side": "LEFT"}
        },
        {"type": "observation", "markdown": "One sentence. Evidence: `redis.conf:1903`."}
      ]
    }

A file anchor carries ``type`` and ``path`` plus an optional ``side``: ``LEFT``
for a file the change deletes, which exists only at the merge-base; ``RIGHT``,
the default, for a file present at the head; ``UNKNOWN`` when the pinned
manifest/diff cannot establish the pre-image path or revision (an unlinked
file coordinate). Side provenance comes from the full merge-base manifest,
not a delta manifest or a guessed filename. A line anchor carries
``start_line``, ``end_line``, and a required ``side``. ``summary.repository_url``
is the base repository's canonical web URL; when present, ``RIGHT`` line
anchors, ``RIGHT`` file anchors, and fix sites render as commit-pinned blob
links at the run trailer's head, a ``LEFT`` file anchor renders as a blob link
at the run trailer's merge-base (a deleted file's forge path is its merge-base
path), and a ``LEFT`` line anchor stays a code span (a renamed file's forge
path is not its merge-base path, so no revision is guessed for it). When
absent, every coordinate renders as a code span. There is no payload override
for the summary's coordinates: the summary is checked by string equality
against the fragments ``--render`` produces, under the one rule
``summary-reference``.

Where a check could disagree with the reference text, the reference text wins
and this script is the thing that must be fixed. Four deliberate reading notes:
the observation evidence check requires an ``Evidence:`` pointer rather than
exactly one coordinate, because the rendering reference's own example pairs two
coordinates for a single drift pointer; ``context`` is a SHA-256 digest
rather than a commit SHA, so the 40-hex commit rule does not apply to it; and
the one-sentence observation check masks the abbreviations ``e.g.``, ``i.e.``,
``etc.``, ``vs.``, ``cf.``, and ``et al.`` so they do not count as sentence
breaks; and finding field labels are read with fenced code blocks and
inline code spans blanked out, so a ``**Impact:**`` quoted inside a suggestion
block or a code span is example text rather than a second field, while the
text between two labels — a suggestion block included — is what the field says,
so a ``Change`` made of one suggestion block is non-empty. Whether a field's
text is sufficient, whether its consequence matters, and whether the requested
remedy is the right one remain reviewer judgments.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
import urllib.parse
from typing import Any

WORKFLOW = "v5b-16"
PRIORITIES = ("P0", "P1", "P2", "P3")
ACTIONS = ("must-fix", "consider")
KINDS = (
    "bug",
    "compatibility",
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
# An ordinary finding's prose fields, in the order the review record states them;
# the first three are required and `Source` is optional.
FIELD_LABELS = ("Triggers when", "Impact", "Change", "Source")
FIELD_REQUIRED = ("Triggers when", "Impact", "Change")

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
# An entry is the word followed by a coordinate — a code span or a link — so
# prose may say "the file anchor is lost" without counting as one.
SUMMARY_ANCHOR_ENTRY_RE = re.compile(r"(?<![\w-])anchor (?=\[?`)")
SUMMARY_FIX_ENTRY_RE = re.compile(r"; fix (?=\[?`)")
BLOB_LINK_RE = re.compile(r"https?://[^\s()<>]+?/blob/(?P<revision>[^/\s()]+)/")
REPOSITORY_URL_RE = re.compile(r"\Ahttps?://[^\s/]+(?:/[^\s]*)?\Z")
SUMMARY_REFERENCE = "summary-reference"
WORD_SHOULD_MUST_RE = re.compile(r"\b(should|must)\b", re.IGNORECASE)
FIELD_LABEL_RE = re.compile(r"\*\*(?P<label>Triggers when|Impact|Change|Source):\*\*")
# A code span opens with a backtick run and closes with a run of the same length;
# it never crosses a blank line.
INLINE_CODE_RE = re.compile(r"(?<!`)(`+)(?!`)(?:(?!\n\n)[\s\S])+?(?<!`)\1(?!`)")
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


def check_run_trailer(report: Report, location: str, raw: Any) -> dict[str, str]:
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
    return fields


def blob_url(repository_url: str, head: str, path: str, start: int | None = None, end: int | None = None) -> str:
    """Build the commit-pinned blob URL for one coordinate.

    The path is percent-decoded once and then encoded once with
    ``urllib.parse.quote(path, safe="/")``, which neutralises spaces,
    parentheses, brackets, ``#``, ``?``, ``%``, and backticks inside the link
    target. Every line or range link carries ``?plain=1`` before its fragment
    so a rendered file (Markdown and the like) opens as source; a file link
    carries neither.
    """
    quoted = urllib.parse.quote(urllib.parse.unquote(path), safe="/")
    url = f"{repository_url.rstrip('/')}/blob/{head}/{quoted}"
    if start is None:
        return url
    if end is None or end == start:
        return f"{url}?plain=1#L{start}"
    return f"{url}?plain=1#L{start}-L{end}"


def _render_coordinate(
    run: dict[str, Any],
    coordinate: str,
    path: str,
    start: int | None,
    end: int | None,
    linked: bool,
    revision: str = "head",
) -> str:
    repository_url = run.get("repository_url")
    if not linked or not isinstance(repository_url, str):
        return f"`{coordinate}`"
    return f"[`{coordinate}`]({blob_url(repository_url, run[revision], path, start, end)})"


def render_reference(item: dict[str, Any], run: dict[str, Any]) -> str | None:
    """Return the exact summary fragment for a finding or question item.

    ``run`` carries ``head`` (the run trailer's full head SHA), ``merge_base``
    (the trailer's full merge-base SHA, or ``None``), and an optional
    ``repository_url``. The fragment is ``anchor <coordinate>`` followed by
    ``; fix <coordinate>`` when ``item.fix`` is set. ``RIGHT`` line anchors,
    ``RIGHT`` file anchors, and fix sites link at ``head`` when
    ``repository_url`` is present; a ``LEFT`` file anchor — a file the change
    deletes — links at ``merge_base``, the revision the file exists at;
    an ``UNKNOWN`` file side retains an unlinked coordinate; a
    ``LEFT`` line anchor renders as a code span with its fix still linked;
    without ``repository_url`` everything is a code span. Returns ``None`` when
    the anchor or fix is malformed, which the anchor-shape and fix-coordinate
    rules report separately, or when a ``LEFT`` file anchor needs a merge-base
    the run trailer does not supply, which the trailer rules report.
    """
    anchor = item.get("anchor")
    if not isinstance(anchor, dict) or not isinstance(anchor.get("path"), str) or not anchor["path"]:
        return None
    path = anchor["path"]
    if anchor.get("type") == "file":
        shape = Report()
        check_anchor(shape, "anchor", anchor)
        if shape.lines:
            return None
        side = anchor.get("side", "RIGHT")
        if side == "UNKNOWN":
            fragment = f"anchor `{path}` (file)"
        elif isinstance(run.get("repository_url"), str):
            revision = "merge_base" if side == "LEFT" else "head"
            if run.get(revision) is None:
                return None
            fragment = f"anchor {_render_coordinate(run, path, path, None, None, linked=True, revision=revision)} (file)"
        else:
            fragment = f"anchor `{path} (file)`"
    elif anchor.get("type") == "line":
        start, end, side = anchor.get("start_line"), anchor.get("end_line"), anchor.get("side")
        for value in (start, end):
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                return None
        if end < start or side not in SIDES:
            return None
        coordinate = f"{path}:{start}" if start == end else f"{path}:{start}-{end}"
        fragment = "anchor " + _render_coordinate(
            run, coordinate, path, start, None if start == end else end, linked=side == "RIGHT"
        )
    else:
        return None
    fix = item.get("fix")
    if fix is not None:
        if not isinstance(fix, str):
            return None
        match = LINE_COORD_RE.match(fix)
        if match is None:
            return None
        fix_start = int(match.group("start"))
        fix_end = int(match.group("end")) if match.group("end") is not None else None
        if fix_end is not None and fix_end <= fix_start:
            return None
        fragment += "; fix " + _render_coordinate(run, fix, match.group("path"), fix_start, fix_end, linked=True)
    return fragment


def referenced_items(items: Any) -> list[tuple[int, dict[str, Any]]]:
    if not isinstance(items, list):
        return []
    return [
        (index, item)
        for index, item in enumerate(items)
        if isinstance(item, dict) and item.get("type") in ("finding", "question")
    ]


def run_identity(summary: dict[str, Any], run_fields: dict[str, str]) -> dict[str, Any] | None:
    """The head, merge-base, and repository URL fragments render against, or None when links cannot be built.

    ``merge_base`` is ``None`` when the trailer lacks a full 40-hex merge-base;
    only a ``LEFT`` file anchor needs it, and the trailer rules report the gap.
    """
    repository_url = summary.get("repository_url")
    head = run_fields.get("head")
    merge_base = run_fields.get("merge-base")
    if not isinstance(merge_base, str) or not COMMIT_SHA_RE.match(merge_base):
        merge_base = None
    if repository_url is None:
        return {"head": head, "merge_base": merge_base, "repository_url": None}
    if not isinstance(head, str) or not COMMIT_SHA_RE.match(head):
        return None
    return {"head": head, "merge_base": merge_base, "repository_url": repository_url.rstrip("/")}


def check_summary_references(report: Report, body: str, summary: dict[str, Any], run_fields: dict[str, str], items: Any) -> None:
    """The one rule that ties the rendered summary to the structured items.

    Every finding and question item's rendered fragment appears exactly once;
    the body renders exactly one ``anchor `` entry per such item and one
    ``; fix `` per item with a fix, where an entry is the word followed by a
    coordinate in backticks or a link (prose may use the word freely); and
    when ``repository_url`` is present, every blob link in the body outside
    those generated fragments points at the run head — the fragments are the
    only place a merge-base link (a ``LEFT`` file anchor) may appear.
    """
    run = run_identity(summary, run_fields)
    if run is None:
        return  # the trailer rules already reported the unusable head
    referenced = referenced_items(items)
    expected_fixes = 0
    remainder = body
    for index, item in referenced:
        location = f"summary.body[items[{index}]]"
        fragment = render_reference(item, run)
        if fragment is None:
            continue  # anchor-shape, fix-coordinate, or the trailer rules report the malformed input
        count = body.count(fragment)
        if count == 0:
            detail = f"expected the rendered fragment `{fragment}` exactly once; not found"
            if run["repository_url"] is not None:
                plain = render_reference(item, {"head": run["head"], "merge_base": run["merge_base"], "repository_url": None})
                if plain is not None and plain in body:
                    detail += "; the body carries its bare code-span form, so render the fragment with --render"
            report.add(location, SUMMARY_REFERENCE, detail)
        elif count > 1:
            report.add(location, SUMMARY_REFERENCE, f"the rendered fragment `{fragment}` appears {count} times; expected once")
        else:
            remainder = remainder.replace(fragment, "", 1)
            if item.get("fix") is None:
                after = body[body.index(fragment) + len(fragment):]
                if after.startswith("; fix "):
                    report.add(location, SUMMARY_REFERENCE, "the summary renders a fix but the item has none")
        if item.get("fix") is not None:
            expected_fixes += 1
    anchors = len(SUMMARY_ANCHOR_ENTRY_RE.findall(body))
    if anchors != len(referenced):
        report.add(
            "summary.body",
            SUMMARY_REFERENCE,
            f"the body renders {anchors} `anchor ` entries for {len(referenced)} finding and question items",
        )
    fixes = len(SUMMARY_FIX_ENTRY_RE.findall(body))
    if fixes != expected_fixes:
        report.add(
            "summary.body",
            SUMMARY_REFERENCE,
            f"the body renders {fixes} `; fix ` entries for {expected_fixes} items with a fix",
        )
    if run["repository_url"] is not None:
        for match in BLOB_LINK_RE.finditer(remainder):
            revision = match.group("revision")
            if revision != run["head"]:
                report.add(
                    "summary.body",
                    SUMMARY_REFERENCE,
                    f"blob link revision `{revision}` is not the run head `{run['head']}`; "
                    "outside a rendered fragment, never link a branch or another commit",
                )


def check_summary(report: Report, summary: Any, items: Any = None) -> None:
    if not isinstance(summary, dict):
        report.add("summary", "schema", "summary must be an object")
        return
    body = summary.get("body")
    if not isinstance(body, str) or not body.strip():
        report.add("summary", "schema", "summary.body must be a non-empty string")
        body = ""
    raw_trailer = summary.get("trailer")
    run_fields: dict[str, str] = {}
    if raw_trailer is None:
        match = RUN_TRAILER_RE.search(body)
        if match is None:
            report.add("summary", "trailer-grammar", "summary carries no `review-run` trailer")
        else:
            run_fields = check_run_trailer(report, "summary.trailer", match.group(0))
    else:
        run_fields = check_run_trailer(report, "summary.trailer", raw_trailer)
        if isinstance(raw_trailer, str) and raw_trailer.strip() and raw_trailer.strip() not in body:
            report.add("summary", "trailer-grammar", "summary.trailer does not appear in summary.body")

    if "anchors" in summary:
        report.add(
            "summary.anchors",
            "schema",
            "`summary.anchors` is no longer part of the payload; the body is checked against the fragments `--render` produces",
        )
    repository_url = summary.get("repository_url")
    if repository_url is not None and (not isinstance(repository_url, str) or not REPOSITORY_URL_RE.match(repository_url)):
        report.add(
            "summary.repository_url",
            "schema",
            "summary.repository_url must be the base repository's canonical http(s) web URL",
        )
        summary = {key: value for key, value in summary.items() if key != "repository_url"}
    check_summary_references(report, body, summary, run_fields, items)


def check_anchor(report: Report, location: str, anchor: Any) -> None:
    if not isinstance(anchor, dict):
        report.add(location, "schema", "anchor must be an object")
        return
    anchor_type = anchor.get("type")
    path = anchor.get("path")
    if not isinstance(path, str) or not path:
        report.add(location, "anchor-shape", "anchor needs a non-empty `path`")
    if anchor_type == "file":
        extra = sorted(set(anchor) - {"type", "path", "side"})
        if extra:
            report.add(location, "anchor-shape", f"a file anchor carries only `type`, `path`, and an optional `side`; found {extra}")
        side = anchor.get("side", "RIGHT")
        if side not in (*SIDES, "UNKNOWN"):
            report.add(
                location,
                "anchor-shape",
                f"a file anchor's optional `side` is `LEFT` for a file the change deletes or `RIGHT` (the default), or `UNKNOWN` for an unestablished pre-image, not `{side!r}`",
            )
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


def mask_code(markdown: str) -> str:
    """Return ``markdown`` with fenced code blocks and inline code spans blanked to spaces.

    The result has the same length as the input, so an offset found in the
    masked text addresses the same character in the original. A fenced block
    opens on a line whose first non-space character (indented at most three
    spaces) starts a run of at least three backticks or tildes and closes on a
    line carrying only a run of that character at least as long; an unclosed
    block runs to the end. The fence lines are blanked with the block.
    """
    lines = markdown.split("\n")
    fence: tuple[str, int] | None = None
    for index, line in enumerate(lines):
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if fence is None:
            if indent <= 3 and (stripped.startswith("```") or stripped.startswith("~~~")):
                char = stripped[0]
                run = len(stripped) - len(stripped.lstrip(char))
                if char == "`" and "`" in stripped[run:]:
                    continue  # a backtick fence's info string may not contain a backtick
                fence = (char, run)
                lines[index] = " " * len(line)
        else:
            char, run = fence
            lines[index] = " " * len(line)
            if indent <= 3 and stripped.startswith(char * run) and not stripped.rstrip().strip(char):
                fence = None
    masked = "\n".join(lines)
    return INLINE_CODE_RE.sub(lambda match: " " * len(match.group(0)), masked)


def finding_fields(markdown: str) -> list[tuple[str, str]]:
    """The finding's labelled prose fields as ``(label, text)`` pairs in document order.

    Labels are located in the code-masked text, so a label quoted inside a code
    block or code span is not a field; each field's text is the original text
    from its label to the next label or the end, with a trailing permission
    sentence removed from the last field, so a suggestion block inside ``Change``
    is that field's text.
    """
    masked = mask_code(markdown)
    labels = [(match.group("label"), match.start(), match.end()) for match in FIELD_LABEL_RE.finditer(masked)]
    fields: list[tuple[str, str]] = []
    for index, (label, _start, end) in enumerate(labels):
        next_start = labels[index + 1][1] if index + 1 < len(labels) else len(markdown)
        text = markdown[end:next_start]
        if index + 1 == len(labels):
            trailing = text.rstrip()
            if trailing.endswith(PERMISSION_SENTENCE):
                text = trailing[: -len(PERMISSION_SENTENCE)]
        fields.append((label, text))
    return fields


def check_finding_fields(report: Report, location: str, markdown: str) -> None:
    """Exactly one non-empty ``Triggers when``, ``Impact``, and ``Change``, in that order, then optional ``Source``."""
    fields = finding_fields(markdown)
    counts = {label: sum(1 for name, _text in fields if name == label) for label in FIELD_LABELS}
    for label in FIELD_REQUIRED:
        if counts[label] == 0:
            report.add(
                location,
                "finding-fields",
                f"a finding states `**{label}:**` once; it is missing "
                "(a label inside a code block or code span is example text and does not count)",
            )
    for label in FIELD_LABELS:
        if counts[label] > 1:
            report.add(location, "finding-fields", f"`**{label}:**` appears {counts[label]} times; a finding states it once")
    for label, text in fields:
        if not text.strip():
            report.add(location, "finding-fields", f"`**{label}:**` is empty; a field carries its text after the label")
    first_seen: list[str] = []
    for label, _text in fields:
        if label not in first_seen:
            first_seen.append(label)
    expected = [label for label in FIELD_LABELS if label in first_seen]
    if first_seen != expected:
        actual = ", ".join(f"`{label}`" for label in first_seen)
        report.add(
            location,
            "field-order",
            f"fields appear as {actual}; the order is `Triggers when`, `Impact`, `Change`, then optional `Source`",
        )


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

    check_finding_fields(report, location, markdown)
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
    check_summary(report, payload.get("summary"), payload.get("items", []))
    check_items(report, payload.get("items", []))
    return report.lines


def run_trailer_fields(summary: dict[str, Any]) -> dict[str, str]:
    """The run trailer's fields, from ``summary.trailer`` or the trailer embedded in the body."""
    raw_trailer = summary.get("trailer")
    if raw_trailer is None:
        match = RUN_TRAILER_RE.search(summary.get("body") or "")
        raw_trailer = match.group(0) if match else None
    if raw_trailer is None:
        return {}
    return check_run_trailer(Report(), "summary.trailer", raw_trailer)


def render(payload: Any) -> tuple[list[str], list[str]]:
    """Return (fragments in item order, violations) for ``--render``."""
    if not isinstance(payload, dict) or not isinstance(payload.get("summary"), dict):
        return [], ["input: schema: payload must be a JSON object with a `summary` object"]
    summary = payload["summary"]
    run = run_identity(summary, run_trailer_fields(summary))
    if run is None:
        return [], ["summary.trailer: trailer-sha: `--render` needs a run trailer whose `head` is a full 40-hex SHA when `repository_url` is present"]
    fragments: list[str] = []
    violations: list[str] = []
    for index, item in referenced_items(payload.get("items", [])):
        fragment = render_reference(item, run)
        if fragment is not None:
            fragments.append(fragment)
        elif _needs_missing_merge_base(item, run):
            violations.append(
                f"items[{index}]: trailer-sha: a `LEFT` file anchor links at the run trailer's `merge-base`, "
                "which is missing or not a full 40-hex SHA"
            )
        else:
            violations.append(f"items[{index}]: anchor-shape: cannot render a fragment from a malformed anchor or fix")
    return fragments, violations


def _needs_missing_merge_base(item: dict[str, Any], run: dict[str, Any]) -> bool:
    anchor = item.get("anchor")
    return (
        isinstance(anchor, dict)
        and anchor.get("type") == "file"
        and anchor.get("side") == "LEFT"
        and run.get("repository_url") is not None
        and run.get("merge_base") is None
    )


def emit_batch(payload: dict[str, Any], event: str = "COMMENT") -> dict[str, Any]:
    """Project a zero-violation payload into GitHub's one-call review body.

    Call ``validate`` first. COMMENT preserves the body. Gating events check
    the advisory status line, remove its suffix, and re-validate a copy before
    projection; ValueError carries content violations. Anchors and item prose
    never change, and the input record remains immutable.
    """
    if event != "COMMENT":
        expected = {"APPROVE": "Approved", "REQUEST_CHANGES": "Changes Requested"}.get(event)
        if expected is None:
            raise ValueError("summary: event-status: unsupported review event")
        body = payload["summary"]["body"]
        first_line = body.split("\n", 1)[0]
        match = re.fullmatch(
            r"\*\*(Changes Requested|Incomplete|Needs Information|Approved)( \(advisory\))?\*\* — \S.*",
            first_line,
        )
        if match is None or bool(match.group(2)) != (match.group(1) in {"Changes Requested", "Approved"}):
            raise ValueError("summary: status-line: expected an advisory COMMENT status line before gating emission")
        if match.group(1) != expected:
            raise ValueError(f"summary: event-status: {event} requires {expected}")
        payload = copy.deepcopy(payload)
        payload["summary"]["body"] = body.replace(f"**{expected} (advisory)**", f"**{expected}**", 1)
        violations = validate(payload)
        if violations:
            raise ValueError("\n".join(violations))
    summary = payload["summary"]
    comments: list[dict[str, Any]] = []
    for _index, item in referenced_items(payload.get("items", [])):
        anchor = item.get("anchor") or {}
        if anchor.get("type") != "line":
            continue
        comment: dict[str, Any] = {
            "path": anchor["path"],
            "line": anchor["end_line"],
            "side": anchor["side"],
        }
        if anchor["start_line"] != anchor["end_line"]:
            comment["start_line"] = anchor["start_line"]
            comment["start_side"] = anchor["side"]
        comment["body"] = f"{item['markdown']}\n\n{item['trailer']}"
        comments.append(comment)
    return {
        "commit_id": run_trailer_fields(summary).get("head"),
        "event": event,
        "body": summary["body"],
        "comments": comments,
    }


HEAD = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
BASE_SHA = "b2c3d4e5f60718293a4b5c6d7e8f90123456789a"
MERGE_BASE = "d4e5f60718293a4b5c6d7e8f90123456789abcde"
OTHER_SHA = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
CONTEXT = "91d34a2f4c869867167f0b31da7c207f4528e12e3d1ef4f107a5eabb4c18718e"
REPOSITORY_URL = "https://github.com/acme/payments"
BLOB = f"{REPOSITORY_URL}/blob/{HEAD}"
MERGE_BASE_BLOB = f"{REPOSITORY_URL}/blob/{MERGE_BASE}"

RUN_TRAILER = (
    f"<!-- review-run head={HEAD} base-ref=main base-sha={BASE_SHA} "
    f"merge-base={MERGE_BASE} workflow={WORKFLOW} context={CONTEXT} "
    "issues=acme/payments#123 coverage=complete -->"
)

# The contract's summary example carries these two fragments byte-for-byte;
# `--render` on the contract payload must reproduce them.
FINDING_FRAGMENT = (
    f"anchor [`src/payments.ts:42`]({BLOB}/src/payments.ts?plain=1#L42); "
    f"fix [`src/retry-policy.ts:18`]({BLOB}/src/retry-policy.ts?plain=1#L18)"
)
QUESTION_FRAGMENT = f"anchor [`src/queue.ts`]({BLOB}/src/queue.ts) (file)"
PLAIN_FINDING_FRAGMENT = "anchor `src/payments.ts:42`; fix `src/retry-policy.ts:18`"
PLAIN_QUESTION_FRAGMENT = "anchor `src/queue.ts (file)`"
# A file the change deletes exists only at the merge-base, so its anchor links there (issue #84).
DELETED_PATH = "src/legacy-queue.ts"
DELETED_ANCHOR = {"type": "file", "path": DELETED_PATH, "side": "LEFT"}
DELETED_FRAGMENT = f"anchor [`{DELETED_PATH}`]({MERGE_BASE_BLOB}/{DELETED_PATH}) (file)"
DELETED_AT_HEAD_FRAGMENT = f"anchor [`{DELETED_PATH}`]({BLOB}/{DELETED_PATH}) (file)"
QUESTION_ENTRY = f"## Open questions\n\n- [Question] Must retries preserve request order? — {QUESTION_FRAGMENT}\n\n"

SUMMARY_BODY = f"""**Changes Requested (advisory)** — 1 must-fix finding, 1 open question.

**Intent:** Add retries for charge submission without changing payment semantics.

**Issue fit:** Partial — retry availability is implemented, but acceptance criterion 2's idempotency guarantee remains open.

**Coverage:** Complete merge-base diff reviewed; payment callers inspected; focused `retry-policy` test run once at the head: pass.

**Reviewed:** `a1b2c3d` against merge-base `d4e5f6a`.

## Findings

- [P1] [must-fix] Preserve the idempotency key across retries — {FINDING_FRAGMENT}

{QUESTION_ENTRY}{RUN_TRAILER}
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
    """The rendering reference's own example review, in payload form."""
    return {
        "summary": {"body": SUMMARY_BODY, "trailer": RUN_TRAILER, "repository_url": REPOSITORY_URL},
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


def plain_payload() -> dict[str, Any]:
    """The same review without `repository_url`: every coordinate is a code span."""
    payload = valid_payload()
    del payload["summary"]["repository_url"]
    payload["summary"]["body"] = SUMMARY_BODY.replace(FINDING_FRAGMENT, PLAIN_FINDING_FRAGMENT).replace(
        QUESTION_FRAGMENT, PLAIN_QUESTION_FRAGMENT
    )
    return payload


def deleted_file_payload() -> dict[str, Any]:
    """The contract example with its question re-anchored on a file the change deletes.

    The question's file anchor carries ``side: LEFT`` and links at the merge-base,
    the only revision the file exists at; the finding's ordinary ``RIGHT`` anchor
    and fix links are unchanged beside it.
    """
    payload = valid_payload()
    payload["items"][1]["anchor"] = dict(DELETED_ANCHOR)
    payload["summary"]["body"] = SUMMARY_BODY.replace(QUESTION_FRAGMENT, DELETED_FRAGMENT)
    return payload


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


UNANCHORED_FRAGMENT = f"anchor [`scripts/__pycache__/validate_review.cpython-314.pyc`]({BLOB}/scripts/__pycache__/validate_review.cpython-314.pyc) (file)"

UNANCHORED_FINDING_MARKDOWN = """**[P2] [must-fix] Remove the committed bytecode cache**

**Triggers when:** The change is merged: the diff adds a CPython bytecode cache
as a tracked file, and nothing ignores it. The file anchor is lost on GitHub's
batch endpoint, so this finding lives in the body.

**Impact:** Every self-test run rewrites the file and dirties the working tree.

**Change:** Delete the file and ignore `__pycache__/`."""


def unanchored_payload() -> dict[str, Any]:
    """A file-anchored finding placed in `Unanchored findings` instead of `Findings`.

    GitHub's review batch cannot carry a file subject, so this is the layout
    every file-anchored finding produces there. Its complete prose uses the
    word ``anchor``, which must not count as a rendered entry.
    """
    payload = valid_payload()
    finding = payload["items"][0]
    finding["id"] = "scripts/committed-pycache"
    finding["markdown"] = UNANCHORED_FINDING_MARKDOWN
    finding["trailer"] = (
        f"<!-- finding id=scripts/committed-pycache head={HEAD} priority=P2 "
        "action=must-fix blocking=true kind=maintainability -->"
    )
    finding["priority"] = "P2"
    finding["kind"] = "maintainability"
    finding["anchor"] = {"type": "file", "path": "scripts/__pycache__/validate_review.cpython-314.pyc"}
    del finding["fix"]
    del payload["items"][1]
    payload["summary"]["body"] = f"""**Changes Requested (advisory)** — 1 must-fix finding.

**Intent:** Render summary coordinates as commit-pinned links.

**Issue fit:** Met; the one blocker is a committed bytecode cache, not the feature.

**Coverage:** Complete merge-base diff reviewed, the committed cache included.

**Reviewed:** `a1b2c3d` against merge-base `d4e5f6a`.

## Unanchored findings

GitHub's review batch cannot carry a file subject, so this finding's complete prose is here.

- [P2] [must-fix] Remove the committed bytecode cache — {UNANCHORED_FRAGMENT}

{UNANCHORED_FINDING_MARKDOWN}

{RUN_TRAILER}
"""
    return payload


def abbreviation_payload() -> dict[str, Any]:
    """An observation whose abbreviation must not read as a sentence break."""
    payload = valid_payload()
    payload["items"][2]["markdown"] = (
        "The first configuration sentence covers more re-point shapes (e.g. same-shard "
        "moves) than the implementation does. Evidence: `redis.conf:1903`."
    )
    return payload


def reproduced_payload() -> dict[str, Any]:
    """Issue #134's reproduction: the contract finding with its `Triggers when` and `Impact` labels removed."""
    payload = valid_payload()
    payload["items"][0]["markdown"] = FINDING_MARKDOWN.replace("**Triggers when:** ", "").replace("**Impact:** ", "")
    return payload


def _paragraphs(markdown: str) -> list[str]:
    return markdown.split("\n\n")


def _field_paragraph(markdown: str, label: str) -> int:
    return next(index for index, paragraph in enumerate(_paragraphs(markdown)) if paragraph.startswith(f"**{label}:**"))


def without_field(markdown: str, label: str) -> str:
    """The finding prose with the labelled paragraph removed."""
    paragraphs = _paragraphs(markdown)
    del paragraphs[_field_paragraph(markdown, label)]
    return "\n\n".join(paragraphs)


def with_empty_field(markdown: str, label: str) -> str:
    """The finding prose with the labelled paragraph reduced to its bare label."""
    paragraphs = _paragraphs(markdown)
    paragraphs[_field_paragraph(markdown, label)] = f"**{label}:**"
    return "\n\n".join(paragraphs)


def with_swapped_fields(markdown: str, first: str, second: str) -> str:
    """The finding prose with two labelled paragraphs exchanged."""
    paragraphs = _paragraphs(markdown)
    one, two = _field_paragraph(markdown, first), _field_paragraph(markdown, second)
    paragraphs[one], paragraphs[two] = paragraphs[two], paragraphs[one]
    return "\n\n".join(paragraphs)


def with_duplicated_field(markdown: str, label: str) -> str:
    """The finding prose with the labelled paragraph stated twice in a row."""
    paragraphs = _paragraphs(markdown)
    index = _field_paragraph(markdown, label)
    paragraphs.insert(index, paragraphs[index])
    return "\n\n".join(paragraphs)


SUGGESTION_BLOCK = """```suggestion
const key = attempt.idempotencyKey; // **Impact:** and **Change:** here are code, not fields
```"""

# The contract finding whose `Change` carries a suggestion block quoting field labels.
SUGGESTION_MARKDOWN = without_field(FINDING_MARKDOWN, "Source").replace(
    "for the same logical charge.", f"for the same logical charge.\n\n{SUGGESTION_BLOCK}"
)


def finding_payload(markdown: str) -> dict[str, Any]:
    """The contract review with its finding's prose replaced; the anchor, trailer, and summary are unchanged."""
    payload = valid_payload()
    payload["items"][0]["markdown"] = markdown
    return payload


def consider_finding_payload(markdown: str) -> dict[str, Any]:
    """The `consider` review with its finding's prose replaced; the title is retagged and the permission sentence appended."""
    payload = consider_payload()
    payload["items"][0]["markdown"] = f"{markdown.replace('[P1] [must-fix]', '[P3] [consider]')}\n\n{PERMISSION_SENTENCE}"
    return payload


def unanchored_finding_payload(markdown: str) -> dict[str, Any]:
    """The `Unanchored findings` review with its body-rendered finding's prose replaced in both places."""
    payload = unanchored_payload()
    payload["items"][0]["markdown"] = markdown
    payload["summary"]["body"] = payload["summary"]["body"].replace(UNANCHORED_FINDING_MARKDOWN, markdown)
    return payload


def reference_payload(
    anchor: dict[str, Any],
    fix: str | None,
    fragment: str,
    repository_url: str | None = REPOSITORY_URL,
) -> dict[str, Any]:
    """A one-finding review whose summary renders `fragment` for an item with `anchor` and `fix`."""
    payload = valid_payload()
    finding = payload["items"][0]
    finding["anchor"] = anchor
    if fix is None:
        del finding["fix"]
        finding["trailer"] = finding["trailer"].replace(" fix=src/retry-policy.ts:18", "")
    else:
        finding["fix"] = fix
        finding["trailer"] = finding["trailer"].replace("fix=src/retry-policy.ts:18", f"fix={fix}")
    del payload["items"][1]
    payload["summary"]["body"] = SUMMARY_BODY.replace(FINDING_FRAGMENT, fragment).replace(QUESTION_ENTRY, "")
    if repository_url is None:
        del payload["summary"]["repository_url"]
    else:
        payload["summary"]["repository_url"] = repository_url
    return payload


def line_anchor(path: str, start: int, end: int | None = None, side: str = "RIGHT") -> dict[str, Any]:
    return {"type": "line", "path": path, "start_line": start, "end_line": start if end is None else end, "side": side}


def render_cases() -> list[tuple[str, dict[str, Any], str | None, str]]:
    """(name, anchor, fix, exact fragment) — every URL-construction rule the contract states."""
    fix = "src/retry-policy.ts:18"
    fix_fragment = f"fix [`src/retry-policy.ts:18`]({BLOB}/src/retry-policy.ts?plain=1#L18)"
    return [
        ("code file, single line, RIGHT, distinct fix", line_anchor("src/payments.ts", 42), fix, FINDING_FRAGMENT),
        (
            "Markdown file line carries ?plain=1",
            line_anchor("README.md", 14),
            None,
            f"anchor [`README.md:14`]({BLOB}/README.md?plain=1#L14)",
        ),
        (
            "range uses L<start>-L<end>",
            line_anchor("src/order.ts", 47, 52),
            None,
            f"anchor [`src/order.ts:47-52`]({BLOB}/src/order.ts?plain=1#L47-L52)",
        ),
        (
            "LEFT anchor stays a code span with a linked fix",
            line_anchor("src/old.ts", 9, side="LEFT"),
            fix,
            f"anchor `src/old.ts:9`; {fix_fragment}",
        ),
        (
            "file anchor links the file and keeps the (file) marker",
            {"type": "file", "path": "src/queue.ts"},
            None,
            QUESTION_FRAGMENT,
        ),
        (
            "file anchor with an explicit RIGHT side links at the head",
            {"type": "file", "path": "src/queue.ts", "side": "RIGHT"},
            None,
            QUESTION_FRAGMENT,
        ),
        (
            "deleted file anchor (LEFT) links at the merge-base",
            dict(DELETED_ANCHOR),
            None,
            DELETED_FRAGMENT,
        ),
        (
            "deleted file anchor keeps its fix linked at the head",
            dict(DELETED_ANCHOR),
            fix,
            f"{DELETED_FRAGMENT}; {fix_fragment}",
        ),
        (
            "range fix uses L<start>-L<end>",
            line_anchor("src/payments.ts", 42),
            "src/retry-policy.ts:18-20",
            f"anchor [`src/payments.ts:42`]({BLOB}/src/payments.ts?plain=1#L42); "
            f"fix [`src/retry-policy.ts:18-20`]({BLOB}/src/retry-policy.ts?plain=1#L18-L20)",
        ),
        (
            "spaces are percent-encoded once",
            line_anchor("docs/my file.md", 3),
            None,
            f"anchor [`docs/my file.md:3`]({BLOB}/docs/my%20file.md?plain=1#L3)",
        ),
        (
            "literal percent is encoded once",
            line_anchor("docs/100%.md", 7),
            None,
            f"anchor [`docs/100%.md:7`]({BLOB}/docs/100%25.md?plain=1#L7)",
        ),
        (
            "parentheses and brackets are encoded",
            line_anchor("src/a(1)[2].ts", 5),
            None,
            f"anchor [`src/a(1)[2].ts:5`]({BLOB}/src/a%281%29%5B2%5D.ts?plain=1#L5)",
        ),
        (
            "path-borne query and fragment are encoded",
            line_anchor("src/a#b?c.ts", 4),
            None,
            f"anchor [`src/a#b?c.ts:4`]({BLOB}/src/a%23b%3Fc.ts?plain=1#L4)",
        ),
    ]


def _mutate(mutation) -> dict[str, Any]:
    payload = valid_payload()
    mutation(payload)
    return payload


def compatibility_payload() -> dict[str, Any]:
    """A compatibility finding uses the same fields and publication path."""
    payload = valid_payload()
    finding = payload["items"][0]
    finding["kind"] = "compatibility"
    finding["trailer"] = finding["trailer"].replace("kind=requirement", "kind=compatibility")
    return payload


def _rewrite_fragment(payload: dict[str, Any], replacement: str) -> None:
    payload["summary"]["body"] = payload["summary"]["body"].replace(FINDING_FRAGMENT, replacement)


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

    # The five validator bypasses issue #82 reproduced against the code-span rule.
    def drop_reference_suffix(payload):
        _rewrite_fragment(payload, "")
        payload["summary"]["body"] = payload["summary"]["body"].replace("retries — \n", "retries\n")

    def malformed_links(payload):
        _rewrite_fragment(
            payload,
            f"anchor [src/payments.ts:42]({BLOB}/src/payments.ts); fix [src/retry-policy.ts:18]({BLOB}/src/retry-policy.ts)",
        )

    def disagreeing_anchor(payload):
        _rewrite_fragment(payload, FINDING_FRAGMENT.replace("payments.ts:42", "payments.ts:41").replace("#L42", "#L41"))

    def anchors_override_with_malformed_fix(payload):
        payload["summary"]["anchors"] = ["src/payments.ts:42"]
        _rewrite_fragment(payload, FINDING_FRAGMENT.split("; fix ")[0] + "; fix `src/retry-policy.ts`")

    def wrong_repository(payload):
        _rewrite_fragment(payload, FINDING_FRAGMENT.replace(f"{REPOSITORY_URL}/blob", "https://github.com/other/repo/blob", 1))

    def wrong_revision(payload):
        _rewrite_fragment(payload, FINDING_FRAGMENT.replace(HEAD, OTHER_SHA, 1))

    def wrong_path(payload):
        _rewrite_fragment(payload, FINDING_FRAGMENT.replace("/src/payments.ts?plain", "/src/other.ts?plain"))

    def wrong_line_fragment(payload):
        _rewrite_fragment(payload, FINDING_FRAGMENT.replace("#L42)", "#L43)"))

    def missing_plain(payload):
        _rewrite_fragment(payload, FINDING_FRAGMENT.replace("payments.ts?plain=1#L42", "payments.ts#L42"))

    def branch_in_revision_slot(payload):
        _rewrite_fragment(payload, FINDING_FRAGMENT.replace(f"/blob/{HEAD}/src/payments", "/blob/main/src/payments"))

    def merge_base_in_revision_slot(payload):
        _rewrite_fragment(payload, FINDING_FRAGMENT.replace(f"/blob/{HEAD}/src/payments", f"/blob/{MERGE_BASE}/src/payments"))

    def extra_rendered_entry(payload):
        payload["summary"]["body"] = payload["summary"]["body"].replace(
            "\n## Open questions",
            f"- [P2] [consider] An entry with no item — anchor [`src/extra.ts:1`]({BLOB}/src/extra.ts?plain=1#L1)\n\n## Open questions",
        )

    def coordinate_shaped_anchor_in_prose(payload):
        payload["summary"]["body"] = payload["summary"]["body"].replace(
            "\n## Open questions",
            "The old anchor `src/legacy.ts:7` no longer exists.\n\n## Open questions",
        )

    def bare_code_span_with_repository_url(payload):
        _rewrite_fragment(payload, PLAIN_FINDING_FRAGMENT)

    def linked_left_anchor(payload):
        payload["items"][0]["anchor"]["side"] = "LEFT"

    def fix_rendered_without_item_fix(payload):
        del payload["items"][0]["fix"]
        payload["items"][0]["trailer"] = payload["items"][0]["trailer"].replace(" fix=src/retry-policy.ts:18", "")

    def fix_missing_for_item_with_fix(payload):
        _rewrite_fragment(payload, FINDING_FRAGMENT.split("; fix ")[0])

    def duplicate_fragment(payload):
        payload["summary"]["body"] = payload["summary"]["body"].replace(
            f"— {FINDING_FRAGMENT}", f"— {FINDING_FRAGMENT} ({FINDING_FRAGMENT})"
        )

    def stray_branch_link(payload):
        payload["summary"]["body"] = payload["summary"]["body"].replace(
            "**Coverage:**", f"**Coverage:** See [`AGENTS.md`]({REPOSITORY_URL}/blob/main/AGENTS.md).", 1
        )

    def stray_merge_base_link(payload):
        payload["summary"]["body"] = payload["summary"]["body"].replace(
            "**Coverage:**", f"**Coverage:** See [`AGENTS.md`]({MERGE_BASE_BLOB}/AGENTS.md).", 1
        )

    def deleted_file_linked_at_head(payload):
        payload["items"][1]["anchor"] = dict(DELETED_ANCHOR)
        payload["summary"]["body"] = SUMMARY_BODY.replace(QUESTION_FRAGMENT, DELETED_AT_HEAD_FRAGMENT)

    def deleted_file_as_code_span(payload):
        payload["items"][1]["anchor"] = dict(DELETED_ANCHOR)
        payload["summary"]["body"] = SUMMARY_BODY.replace(QUESTION_FRAGMENT, f"anchor `{DELETED_PATH} (file)`")

    def file_anchor_with_unknown_side(payload):
        payload["items"][1]["anchor"] = {"type": "file", "path": "src/queue.ts", "side": "BOTH"}

    def bad_repository_url(payload):
        payload["summary"]["repository_url"] = "github.com/acme/payments"

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
            f"workflow={WORKFLOW}", "workflow=v5b-15"
        )

    def malformed_trailer(payload):
        payload["items"][0]["trailer"] = "<!-- finding id payments/retry-idempotency -->"

    def line_anchor_without_side(payload):
        del payload["items"][0]["anchor"]["side"]

    def reversed_anchor_range(payload):
        payload["items"][0]["anchor"]["start_line"] = 44

    def file_anchor_with_extra_field(payload):
        payload["items"][1]["anchor"] = {"type": "file", "path": "src/queue.ts", "start_line": 1}

    def equal_fix_range(payload):
        payload["items"][0]["fix"] = "src/retry-policy.ts:18-18"
        payload["items"][0]["trailer"] = payload["items"][0]["trailer"].replace(
            "fix=src/retry-policy.ts:18", "fix=src/retry-policy.ts:18-18"
        )

    def trailer_disagreement(payload):
        payload["items"][0]["trailer"] = payload["items"][0]["trailer"].replace("priority=P1", "priority=P2")

    # Issue #134: every finding carries exactly one non-empty `Triggers when`, `Impact`, and `Change`, in order.
    field_cases: list[tuple[str, dict[str, Any], str]] = [
        ("issue #134 reproduction: Triggers when and Impact labels removed", reproduced_payload(), "finding-fields"),
    ]
    for label in FIELD_REQUIRED:
        field_cases.append((f"missing {label}", finding_payload(without_field(FINDING_MARKDOWN, label)), "finding-fields"))
    for label in FIELD_LABELS:
        field_cases.append((f"empty {label}", finding_payload(with_empty_field(FINDING_MARKDOWN, label)), "finding-fields"))
    field_cases.extend(
        [
            ("Impact before Triggers when", finding_payload(with_swapped_fields(FINDING_MARKDOWN, "Triggers when", "Impact")), "field-order"),
            ("Change before Impact", finding_payload(with_swapped_fields(FINDING_MARKDOWN, "Impact", "Change")), "field-order"),
            ("Impact stated twice", finding_payload(with_duplicated_field(FINDING_MARKDOWN, "Impact")), "finding-fields"),
            ("Change stated twice", finding_payload(with_duplicated_field(FINDING_MARKDOWN, "Change")), "finding-fields"),
            (
                "Impact only inside a suggestion block",
                finding_payload(without_field(SUGGESTION_MARKDOWN, "Impact")),
                "finding-fields",
            ),
            (
                "Impact only inside a code span",
                finding_payload(without_field(FINDING_MARKDOWN, "Impact").replace("**Change:** In", "**Change:** See `**Impact:**` above. In")),
                "finding-fields",
            ),
            (
                "consider finding whose Change is only the permission sentence",
                consider_finding_payload(with_empty_field(without_field(FINDING_MARKDOWN, "Source"), "Change")),
                "finding-fields",
            ),
            (
                "unanchored finding without Impact",
                unanchored_finding_payload(without_field(UNANCHORED_FINDING_MARKDOWN, "Impact")),
                "finding-fields",
            ),
            (
                "unanchored finding with Change before Triggers when",
                unanchored_finding_payload(with_swapped_fields(UNANCHORED_FINDING_MARKDOWN, "Triggers when", "Change")),
                "field-order",
            ),
        ]
    )

    percent_anchor = line_anchor("docs/100%.md", 7)
    injection_path = "src/a](https://evil.example)b.ts"

    return [
        ("abbreviated finding head", _mutate(abbreviate_head), "trailer-sha"),
        ("abbreviated run head", _mutate(abbreviate_run_head), "trailer-sha"),
        ("uppercase merge-base", _mutate(uppercase_merge_base), "trailer-sha"),
        ("bypass 1: summary drops the anchor and fix suffix", _mutate(drop_reference_suffix), SUMMARY_REFERENCE),
        ("bypass 2: summary renders malformed links", _mutate(malformed_links), SUMMARY_REFERENCE),
        ("bypass 3: summary anchor disagrees with the item", _mutate(disagreeing_anchor), SUMMARY_REFERENCE),
        ("bypass 4: summary.anchors override hides a malformed fix", _mutate(anchors_override_with_malformed_fix), SUMMARY_REFERENCE),
        ("bypass 4: summary.anchors is no longer accepted", _mutate(anchors_override_with_malformed_fix), "schema"),
        ("bypass 5: wrong repository", _mutate(wrong_repository), SUMMARY_REFERENCE),
        ("bypass 5: wrong revision", _mutate(wrong_revision), SUMMARY_REFERENCE),
        ("bypass 5: wrong path", _mutate(wrong_path), SUMMARY_REFERENCE),
        ("bypass 5: wrong line fragment", _mutate(wrong_line_fragment), SUMMARY_REFERENCE),
        ("missing ?plain=1", _mutate(missing_plain), SUMMARY_REFERENCE),
        ("branch name in the revision slot", _mutate(branch_in_revision_slot), SUMMARY_REFERENCE),
        ("merge-base SHA in the revision slot", _mutate(merge_base_in_revision_slot), SUMMARY_REFERENCE),
        (
            "double encoding",
            reference_payload(percent_anchor, None, f"anchor [`docs/100%.md:7`]({BLOB}/docs/100%2525.md?plain=1#L7)"),
            SUMMARY_REFERENCE,
        ),
        (
            "Markdown-link injection through a path",
            reference_payload(
                line_anchor(injection_path, 5),
                None,
                f"anchor [`{injection_path}:5`]({BLOB}/{injection_path}?plain=1#L5)",
            ),
            SUMMARY_REFERENCE,
        ),
        ("extra rendered entry with no item", _mutate(extra_rendered_entry), SUMMARY_REFERENCE),
        ("coordinate-shaped anchor reference in prose", _mutate(coordinate_shaped_anchor_in_prose), SUMMARY_REFERENCE),
        ("bare code span for a RIGHT anchor with repository_url", _mutate(bare_code_span_with_repository_url), SUMMARY_REFERENCE),
        ("linked LEFT anchor", _mutate(linked_left_anchor), SUMMARY_REFERENCE),
        ("fix rendered for an item without one", _mutate(fix_rendered_without_item_fix), SUMMARY_REFERENCE),
        ("fix missing for an item with one", _mutate(fix_missing_for_item_with_fix), SUMMARY_REFERENCE),
        ("fragment rendered twice", _mutate(duplicate_fragment), SUMMARY_REFERENCE),
        ("stray branch link elsewhere in the body", _mutate(stray_branch_link), SUMMARY_REFERENCE),
        ("stray merge-base link elsewhere in the body", _mutate(stray_merge_base_link), SUMMARY_REFERENCE),
        ("deleted file anchor linked at the head", _mutate(deleted_file_linked_at_head), SUMMARY_REFERENCE),
        ("deleted file anchor as a bare code span with repository_url", _mutate(deleted_file_as_code_span), SUMMARY_REFERENCE),
        ("repository_url is not a web URL", _mutate(bad_repository_url), "schema"),
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
        ("reversed anchor range", _mutate(reversed_anchor_range), "anchor-shape"),
        ("file anchor with extra field", _mutate(file_anchor_with_extra_field), "anchor-shape"),
        ("file anchor with a side outside LEFT/RIGHT", _mutate(file_anchor_with_unknown_side), "anchor-shape"),
        ("equal fix range", _mutate(equal_fix_range), "fix-coordinate"),
        ("trailer priority disagreement", _mutate(trailer_disagreement), "trailer-agreement"),
        ("payload is not an object", [], "schema"),
        *field_cases,
    ]


EMIT_BATCH_CASES = 15


def emit_batch_cases() -> list[str]:
    """Failures from the ``--emit-batch`` cases: the projection, the CLI on a valid payload, the CLI on an invalid
    one, a compatibility finding, and the CLI on issue #134's reproduction, whose two missing fields are refused before any batch prints."""
    failures: list[str] = []
    payload = valid_payload()
    finding, question = payload["items"][0], payload["items"][1]
    batch = emit_batch(payload)
    want = {
        "commit_id": HEAD,
        "event": "COMMENT",
        "body": SUMMARY_BODY,
        "comments": [
            {
                "path": "src/payments.ts",
                "line": 42,
                "side": "RIGHT",
                "body": f"{FINDING_MARKDOWN}\n\n{finding['trailer']}",
            }
        ],
    }
    if batch != want:
        failures.append(f"emit-batch on the contract example: got {batch!r}, want {want!r}")
    if question["anchor"]["type"] != "file" or any(c["path"] == question["anchor"]["path"] for c in batch["comments"]):
        failures.append("emit-batch: the file-anchored question must produce no comment")
    if validate(payload):
        failures.append("emit-batch: the contract example must still validate after projection")
    finding["anchor"] = line_anchor("src/payments.ts", 40, 42)
    del finding["fix"]
    finding["trailer"] = finding["trailer"].replace(" fix=src/retry-policy.ts:18", "")
    ranged = emit_batch(payload)["comments"]
    want_ranged = {
        "path": "src/payments.ts",
        "line": 42,
        "side": "RIGHT",
        "start_line": 40,
        "start_side": "RIGHT",
        "body": f"{FINDING_MARKDOWN}\n\n{finding['trailer']}",
    }
    if ranged != [want_ranged]:
        failures.append(f"emit-batch multi-line anchor: got {ranged!r}, want {[want_ranged]!r}")

    command = [sys.executable, __file__, "--emit-batch"]
    valid = subprocess.run(command, input=json.dumps(valid_payload()), capture_output=True, text=True, encoding="utf-8")
    try:
        printed = json.loads(valid.stdout)
    except ValueError:
        printed = None
    if valid.returncode != 0 or printed != want or valid.stderr:
        failures.append(f"--emit-batch on the contract example: exit {valid.returncode}, stdout {valid.stdout!r}, stderr {valid.stderr!r}")

    compatibility = compatibility_payload()
    emitted = subprocess.run(command, input=json.dumps(compatibility), capture_output=True, text=True, encoding="utf-8")
    try:
        printed = json.loads(emitted.stdout)
    except ValueError:
        printed = None
    expected = dict(want)
    expected["comments"] = [dict(want["comments"][0])]
    expected["comments"][0]["body"] = f"{FINDING_MARKDOWN}\n\n{compatibility['items'][0]['trailer']}"
    if emitted.returncode != 0 or printed != expected or emitted.stderr:
        failures.append(f"--emit-batch on a compatibility finding: exit {emitted.returncode}, stdout {emitted.stdout!r}, stderr {emitted.stderr!r}")

    invalid_payload = _mutate(lambda p: p["items"][2].__setitem__("markdown", OBSERVATION_MARKDOWN.replace("covers", "should cover", 1)))
    violations = validate(invalid_payload)
    if len(violations) != 1:
        failures.append(f"--emit-batch fixture: expected exactly one violation, got: {'; '.join(violations)}")
    invalid = subprocess.run(command, input=json.dumps(invalid_payload), capture_output=True, text=True, encoding="utf-8")
    if invalid.returncode != 1 or invalid.stdout != "".join(f"{line}\n" for line in violations):
        failures.append(f"--emit-batch on one violation: exit {invalid.returncode}, stdout {invalid.stdout!r}")
    reproduced = reproduced_payload()
    violations = validate(reproduced)
    missing = [line for line in violations if ": finding-fields: " in line and "is missing" in line]
    if len(violations) != 2 or len(missing) != 2 or "Triggers when" not in missing[0] or "Impact" not in missing[1]:
        failures.append(f"issue #134 reproduction: expected two field-specific `finding-fields` violations, got: {'; '.join(violations)}")
    refused = subprocess.run(command, input=json.dumps(reproduced), capture_output=True, text=True, encoding="utf-8")
    if refused.returncode != 1 or refused.stdout != "".join(f"{line}\n" for line in violations) or "commit_id" in refused.stdout:
        failures.append(f"--emit-batch on the issue #134 reproduction: exit {refused.returncode}, stdout {refused.stdout!r}")
    # The status is a model judgment; these cases exercise only transport grammar.
    for status, event, expected_rule in [
        ("Changes Requested (advisory)", "REQUEST_CHANGES", None),
        ("Approved (advisory)", "APPROVE", None),
        ("Changes Requested (advisory)", "APPROVE", "event-status"),
        ("Approved (advisory)", "REQUEST_CHANGES", "event-status"),
        ("Incomplete", "APPROVE", "event-status"),
        ("Needs Information", "REQUEST_CHANGES", "event-status"),
        ("Approved", "APPROVE", "status-line"),
        ("Incomplete (advisory)", "APPROVE", "status-line"),
        ("Unknown", "APPROVE", "status-line"),
        ("Unknown", "COMMENT", None),
    ]:
        sample = valid_payload()
        sample["summary"]["body"] = sample["summary"]["body"].replace(
            "Changes Requested (advisory)", status, 1
        )
        before = copy.deepcopy(sample)
        result = subprocess.run(
            command + ["--event", event], input=json.dumps(sample),
            capture_output=True, text=True, encoding="utf-8",
        )
        if expected_rule:
            if result.returncode != 1 or f": {expected_rule}: " not in result.stdout or '"commit_id"' in result.stdout:
                failures.append(f"gating {status}/{event}: expected {expected_rule}, got {result.returncode}: {result.stdout!r}")
            continue
        expected = dict(want)
        expected["event"] = event
        expected["body"] = sample["summary"]["body"]
        if event != "COMMENT":
            expected["body"] = expected["body"].replace(" (advisory)**", "**", 1)
        try:
            printed = json.loads(result.stdout)
        except ValueError:
            printed = None
        if result.returncode != 0 or printed != expected or result.stderr:
            failures.append(f"gating {status}/{event}: unexpected batch {result.returncode}: {result.stdout!r}")
        direct = emit_batch(sample, event)
        if sample != before or direct != expected:
            failures.append(f"gating {status}/{event}: input changed or projection disagrees")
        edited = copy.deepcopy(sample)
        edited["summary"]["body"] = direct["body"]
        if validate(edited):
            failures.append(f"gating {status}/{event}: emitted body does not validate")
    return failures


# Checks ``self_test`` runs outside the ``passing``, ``failing_cases``, and emit-batch lists: the two
# code-span renders without ``repository_url``, ``--render`` on the contract example and on the
# deleted-file review, ``--render`` and ``validate`` with an abbreviated merge-base, and the bare
# code-span hint.
AD_HOC_CASES = 7


def self_test() -> int:
    failures: list[str] = []
    run = {"head": HEAD, "merge_base": MERGE_BASE, "repository_url": REPOSITORY_URL}
    plain_run = {"head": HEAD, "merge_base": MERGE_BASE, "repository_url": None}
    passing: list[tuple[str, dict[str, Any]]] = [
        ("contract example review", valid_payload()),
        ("compatibility finding", compatibility_payload()),
        ("code-span fallback without repository_url", plain_payload()),
        ("consider finding", consider_payload()),
        ("observation with abbreviation", abbreviation_payload()),
        ("file-anchored finding laid out in Unanchored findings", unanchored_payload()),
        ("deleted file anchor at the merge-base beside an ordinary RIGHT link", deleted_file_payload()),
        ("finding without the optional Source", finding_payload(without_field(FINDING_MARKDOWN, "Source"))),
        ("Change carrying a suggestion block that quotes field labels", finding_payload(SUGGESTION_MARKDOWN)),
        (
            "Change that is one suggestion block",
            finding_payload(with_empty_field(without_field(FINDING_MARKDOWN, "Source"), "Change") + f"\n\n{SUGGESTION_BLOCK}"),
        ),
        (
            "Change quoting a field label in a code span",
            finding_payload(FINDING_MARKDOWN.replace("**Change:** In", "**Change:** Keep the `**Impact:**` label. In")),
        ),
        ("consider finding with a suggestion block before the permission sentence", consider_finding_payload(SUGGESTION_MARKDOWN)),
    ]
    for name, anchor, fix, fragment in render_cases():
        item: dict[str, Any] = {"type": "finding", "anchor": anchor}
        if fix is not None:
            item["fix"] = fix
        rendered = render_reference(item, run)
        if rendered != fragment:
            failures.append(f"render {name}: got {rendered!r}, want {fragment!r}")
        passing.append((f"render {name}", reference_payload(anchor, fix, fragment)))
    plain_left = render_reference({"type": "finding", "anchor": line_anchor("src/old.ts", 9, side="LEFT")}, plain_run)
    if plain_left != "anchor `src/old.ts:9`":
        failures.append(f"render without repository_url: got {plain_left!r}")
    plain_deleted = render_reference({"type": "finding", "anchor": dict(DELETED_ANCHOR)}, plain_run)
    if plain_deleted != f"anchor `{DELETED_PATH} (file)`":
        failures.append(f"render deleted file anchor without repository_url: got {plain_deleted!r}")
    fragments, violations = render(valid_payload())
    if violations or fragments != [FINDING_FRAGMENT, QUESTION_FRAGMENT]:
        failures.append(f"--render on the contract example: got {fragments!r}, violations {violations!r}")
    fragments, violations = render(deleted_file_payload())
    if violations or fragments != [FINDING_FRAGMENT, DELETED_FRAGMENT]:
        failures.append(f"--render on the deleted-file review: got {fragments!r}, violations {violations!r}")
    no_merge_base = deleted_file_payload()
    no_merge_base["summary"]["trailer"] = no_merge_base["summary"]["trailer"].replace(MERGE_BASE, "d4e5f60")
    no_merge_base["summary"]["body"] = no_merge_base["summary"]["body"].replace(MERGE_BASE, "d4e5f60")
    fragments, violations = render(no_merge_base)
    if fragments != [FINDING_FRAGMENT] or len(violations) != 1 or "trailer-sha" not in violations[0]:
        failures.append(f"--render with an abbreviated merge-base: got {fragments!r}, violations {violations!r}")
    if "trailer-sha" not in {line.split(": ", 2)[1] for line in validate(no_merge_base)}:
        failures.append("validate with an abbreviated merge-base: expected a `trailer-sha` violation")
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
    bare = validate(_mutate(lambda p: _rewrite_fragment(p, PLAIN_FINDING_FRAGMENT)))
    if not any("bare code-span form" in line for line in bare):
        failures.append(f"bare code span: expected the --render hint, got: {'; '.join(bare)}")
    failures.extend(emit_batch_cases())
    for failure in failures:
        print(failure)
    if failures:
        print(f"validate_review: {len(failures)} self-test case(s) failed")
        return 1
    print(f"validate_review: self-test passed ({len(passing) + len(failing_cases()) + AD_HOC_CASES + EMIT_BATCH_CASES} cases, emit-batch included)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a would-be v5b review payload against the mechanical review-record and rendering rules."
    )
    parser.add_argument("input", nargs="?", default="-", help="JSON file, or - for stdin")
    parser.add_argument("--self-test", action="store_true", help="run the embedded fixtures and exit")
    parser.add_argument(
        "--render",
        action="store_true",
        help="print each finding and question item's summary reference fragment, one per line, and exit",
    )
    parser.add_argument(
        "--emit-batch",
        action="store_true",
        help="print the forge-native one-call review body for a payload with zero violations, and exit",
    )
    parser.add_argument("--event", default="COMMENT", choices=("COMMENT", "REQUEST_CHANGES", "APPROVE"), help="review event; gating checks status and removes the advisory suffix")
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

    if args.emit_batch:
        violations = validate(payload)
        if violations:
            for line in violations:
                print(line)
            return 1
        try:
            batch = emit_batch(payload, args.event)
        except ValueError as error:
            print(error)
            return 1
        print(json.dumps(batch, indent=2))
        return 0

    if args.render:
        fragments, violations = render(payload)
        for line in fragments:
            print(line)
        for line in violations:
            print(line)
        return 1 if violations else 0

    violations = validate(payload)
    for line in violations:
        print(line)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
