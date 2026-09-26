#!/usr/bin/env python3
"""Compose, validate and write review-code's record, payload, batch and report in one call.

Usage:
    python3 scripts/render_review.py --store STORE [--packet PACKET] [--prior-record RECORD] PRIVATE_DIR
    python3 scripts/render_review.py --check [--head SHA] [--lineage RECORD ...] PRIVATE_DIR
    python3 scripts/render_review.py --emit-batch [--event COMMENT|REQUEST_CHANGES|APPROVE] [PAYLOAD] < payload.json
    python3 scripts/render_review.py --example
    python3 scripts/render_review.py --self-test

Finalization reads PRIVATE_DIR/composition.json: the judgments and prose the
reviewer authored (`--example` prints a pull request's) with the private
`record` accounting: `repository`, `requirements`, `files`, `check_evidence`,
`verification` (`tasks`, `batches`, `outstanding`) and `routed`
(`unresolved`, `disputed`, `unrecoverable_inputs`), each written, empty lists
included. Nothing judged is defaulted. Mechanical fields an input owns may be
omitted and are filled first; an explicit copy that disagrees is refused, and
an omitted field no input establishes is named:

    STORE              run.head, run.merge_base; with a working-tree snapshot,
                       run.target_kind (worktree) and run.tree
    PACKET             run.target_kind (pull-request), run.base_ref,
                       run.base_sha, run.merged, run.repository_url,
                       run.issues, and run.packet_context, the digest
                       forge_packet.py computes from the packet's intent; its
                       pinned head must be the store's
    run.specs          run.supplied_inputs: `yes` when the caller supplied
                       issues or specs, else `no`
    a local target     run.merged (false); it has no packet_context
    this run           record.paths private_dir, store, composition, skill_root
    each batch         `name` and `phase` from its bundle's manifest.json,
                       `raw_return` from its accounting report, which must
                       be a verifier-accounting/3 report of that
                       verifier-manifest/3 bundle: the same bundle_id and
                       the manifest's SHA-256
    the batches        record.verification.allowance: each flag is spent when
                       its batch is recorded here or the prior record spent it
    RECORD             record.lineage: the prior's lineage plus the prior

A local target writes `run.target_kind` (`range` or `worktree`), `target`
for a range, `base_ref`, `base_sha`, `issues`, `specs` and
`change_description` (its commit messages, possibly empty).

`--prior-record` makes the run a re-review of a finalized local
`review-code-record/1` after fixes. It is refused unless that record carries
this finalization protocol with its report present, reviewed a local target,
and shares this run's repository, base ref and base SHA. Then the composition
must classify every finding and question the prior renders, exactly once and
with its action, in `prior_items`; render an open one (`still-open`,
`not-verifiable`, `disputed`) again under its id, a must-fix staying must-fix,
and a settled one (`fixed`, `accepted`, `obsolete`) never; keep every prior
`outstanding` and `routed` entry unless a task this run ruled on settled it
(a carried confirmation settles nothing); record a batch only for a phase the
prior left unspent; and name, for a carried confirmation, `confirmed_in` (the
prior or a record in its lineage) and the `batch` whose accounting report
confirmed it, which must be the provenance the prior's own task carries.
`run.prior_head`, when a delta review sets it, is the prior's head, and the
prior's coverage must be complete. Without a prior record a local target has
no prior items.

Each prior item may add `reply` (drafted reply prose, or null), `thread_id`
and `comment_id`: both null for an item without a forge thread, otherwise the
thread's node id and its first comment's numeric id in the read-only
`--packet`. A reply needs a thread, a `disputed` item has none, and the
finalizer appends the prior-item trailer to `fixed`, `accepted`, `obsolete`
and `still-open` replies. These fields never reach the payload.

The composer renders the finding, question and observation syntax, trailers,
the summary's status line, counts, indexes, sections, Mode line and run
trailer (`workflow`, `packet_context`, `supplied_inputs`) from the authored
fields, checks every contradiction it can decide (run identity, anchors
against the pinned manifest, priority and action, stable ids, status against
blockers and coverage, requirement, file, check-evidence, verification and
routed accounting) and validates the payload it composed. Rulings are checked
against the accounting reports their batches name. It decides no judgment.

Stages, in order: `prior-record`, `derive`, `accounting`, `compose`, then
`record.json`, `payload.json`, `batch.json` and `report.md`, each staged as
`<artifact>.part` and promoted only after every stage passed, the report last:
it is the success marker. The record carries the run, status, summary and
items, prior items, the accounting, `lineage`, `prior_record` and
`finalization` (this protocol, the report path, the inputs and each prior
item's rendered reply). Earlier output in PRIVATE_DIR is removed first, the
report first, and a failed write removes what this run staged. A prior record
inside PRIVATE_DIR is refused. A private directory has one writer at a time.
Success prints `status`, `coverage`, then one `<name> <absolute path>` line
per output, the report last. A failing stage prints `<stage> failed with exit
<status>; later stages did not run:` and its violations, one
`<location>: <rule>: <detail>` line each.

`--check` modifies nothing: it prints the same lines for a record this
protocol finalized in PRIVATE_DIR, with its report, payload and batch present,
and otherwise one `unconsumable:` line per reason. `--head` requires the
record's head; each `--lineage RECORD` requires the record to be RECORD or to
descend from it, which rejects a sibling that forked from an earlier record.

`--emit-batch` validates a payload and prints the forge-native one-call review
body: `commit_id`, `event`, `body` and one `comments` entry per line-anchored
finding or question. A gating `--event` checks the advisory status line and
removes its suffix, then re-validates. It never posts.

Exit codes:
    0  finalized, a consumable record, an emitted batch, or a passing self-test
    1  a content violation or refusal, or an unconsumable record under --check
    2  an input, store or packet cannot be read, or an output
       cannot be removed, written or promoted
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any

import forge_packet as fp
import review_context as rc
from account_verifier_return import ACCOUNTING_FORMAT
from build_verifier_prompt import MANIFEST_FORMAT

# --- payload validation ----------------------------------------------------

WORKFLOW = "v5b-27"
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
    "packet_context",
    "supplied_inputs",
    "issues",
    "coverage",
)
FINDING_REQUIRED = ("id", "head", "priority", "action", "blocking", "kind")
FINDING_OPTIONAL = ("fix",)
QUESTION_REQUIRED = ("id", "head", "action")
QUESTION_OPTIONAL = ()

COMMIT_SHA_RE = re.compile(r"\A[0-9a-f]{40}\Z")
DIGEST_RE = re.compile(r"\A[0-9a-f]{64}\Z")
SUPPLIED_INPUTS = ("yes", "no")
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
    packet_context = fields.get("packet_context")
    if packet_context is not None and packet_context != "none" and not DIGEST_RE.match(packet_context):
        report.add(location, "trailer-grammar", "`packet_context` must be a 64-character lowercase SHA-256 digest, or `none` on a local target")
    supplied = fields.get("supplied_inputs")
    if supplied is not None and supplied not in SUPPLIED_INPUTS:
        report.add(location, "trailer-grammar", f"`supplied_inputs={supplied}` must be one of {list(SUPPLIED_INPUTS)}")
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
                    detail += "; the body carries its bare code-span form, so let the composer render the fragment"
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
            "`summary.anchors` is no longer part of the payload; the body is checked against the fragments the composer renders",
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
    if "**Change:**" in mask_code(markdown):
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
    labels = list(re.finditer(r"Evidence:", mask_code(text)))
    claim = text[:labels[0].start()] if labels else text
    evidence = text[labels[0].end():] if labels else ""
    if len(labels) != 1 or not evidence.strip():
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




# --- composition -----------------------------------------------------------

STATUSES = ("Changes Requested", "Incomplete", "Needs Information", "Approved")
ADVISORY_STATUSES = ("Changes Requested", "Approved")
CLASSIFICATIONS = ("fixed", "accepted", "obsolete", "still-open", "not-verifiable", "disputed")
OPEN_CLASSIFICATIONS = ("still-open", "not-verifiable", "disputed")
PRIOR_ACTIONS = ("must-fix", "consider", "question")
FILE_SIDES = ("LEFT", "RIGHT", "UNKNOWN")
MANIFEST_FILE_SIDES = {"D": "LEFT", "A": "RIGHT", "C": "RIGHT", "M": "RIGHT", "R": "RIGHT", "T": "RIGHT"}
MODE_LINE = "**Mode:** Retrospective review of merged pull request."
UNANCHORED_NOTE = (
    "The forge's review batch cannot carry a file subject, so each finding below carries its complete prose here."
)
ITEM_INDEX_RE = re.compile(r"items\[(?P<index>[0-9]+)\]")
LOCAL = ("range", "worktree")
RECORD_SCHEMA = "review-code-record/1"
# The record paths every record names; the skill root is where a publisher or caller runs this skill's scripts from.
RECORD_PATHS = ("private_dir", "store", "composition", "skill_root")
# Finalization writes this discriminator into every record; a prior record must carry it with its report present.
FINALIZATION_PROTOCOL = "review-code-finalization/2"
REQUIREMENT_CLASSES = ("acceptance", "supporting", "artifact")
REQUIREMENT_DISPOSITIONS = ("met", "partial", "not-verifiable")
MANDATORY_KINDS = ("security", "compatibility")
TRIGGERS = ("must-fix", "security", "data-integrity", "destructive-migration", "compatibility", "prior-must-fix", "optional")
PREMISE_AREAS = ("security", "data-integrity", "destructive-migration", "compatibility", "concurrency")
CANDIDATE_RULINGS = ("confirmed", "refuted", "unresolved", "withheld", "pending")
PREMISE_RULINGS = ("holds", "fails", "unresolved", "withheld", "pending")
PHASES = ("initial", "follow-up")
FILE_STATES = ("reviewed", "ignored", "unreviewed")
EVIDENCE_OUTCOMES = ("accepted", "historical", "reviewer-executed", "failed", "unavailable")
BATCH_CAP = 2  # one initial plus one follow-up


def token(value: str) -> bool:
    return bool(TOKEN_RE.match(value)) and not BAD_PERCENT_RE.search(value)


def encode_path(path: str) -> str:
    """Percent-encode a coordinate path for a trailer value.

    Spaces, percent signs, and every character outside printable ASCII are
    encoded as the ``%XX`` bytes of their UTF-8 form; nothing else changes, so
    the value is one printable ASCII token and ``blob_url``
    recovers the raw path by decoding it once.
    """
    encoded: list[str] = []
    for char in path:
        if char in ("%", " ") or not ("!" <= char <= "~"):
            encoded.append("".join(f"%{byte:02X}" for byte in char.encode("utf-8")))
        else:
            encoded.append(char)
    return "".join(encoded)


def abbreviate(sha: str) -> str:
    return sha[:7]


def plural(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def read_text(report: Report, location: str, obj: dict[str, Any], key: str, required: bool = True) -> str | None:
    value = obj.get(key)
    if value is None:
        if required:
            report.add(location, "schema", f"`{key}` is required and must be a non-empty string")
        return None
    if not isinstance(value, str) or not value.strip():
        report.add(location, "schema", f"`{key}` must be a non-empty string")
        return None
    return value


def read_line(report: Report, location: str, obj: dict[str, Any], key: str, required: bool = True) -> str | None:
    value = read_text(report, location, obj, key, required)
    if value is not None and "\n" in value:
        report.add(location, "schema", f"`{key}` is a single line")
        return None
    return value


def read_id(report: Report, location: str, obj: dict[str, Any]) -> str | None:
    identity = read_line(report, location, obj, "id")
    if identity is not None and not token(identity):
        report.add(location, "stable-id", f"`id={identity}` must be a single printable ASCII token with `%` percent-encoded")
        return None
    return identity


def check_prose_labels(report: Report, location: str, key: str, prose: str, observation: bool = False) -> None:
    """A labelled field's prose may quote a label only inside code."""
    masked = mask_code(prose)
    labels = re.compile(r"\*\*(?P<label>Triggers when|Impact|Change|Source|Evidence|Why it matters):\*\*")
    for match in labels.finditer(masked):
        report.add(
            location,
            "field-label",
            f"`{key}` contains the label `**{match.group('label')}:**` outside a code block or code span; "
            "the composer renders each label once, so a literal label belongs in a code span",
        )
    if observation and "Evidence:" in masked:
        report.add(location, "field-label", f"`{key}` contains `Evidence:` outside code; the composer appends the evidence pointer")
    if PERMISSION_SENTENCE in masked:
        report.add(location, "field-label", f"`{key}` contains the permission sentence; the composer adds it to a `consider` finding")


def check_anchor_input(report: Report, location: str, anchor: Any) -> None:
    if not isinstance(anchor, dict):
        report.add(location, "schema", "`anchor` must be an object")
        return
    if anchor.get("type") == "file" and "side" in anchor and anchor["side"] not in FILE_SIDES:
        report.add(location, "anchor-provenance", f"a file anchor's `side` is one of {list(FILE_SIDES)}, not `{anchor.get('side')!r}`")
    check_anchor(report, location, anchor)


def compose_fix(report: Report, location: str, fix: Any) -> str | None:
    if not isinstance(fix, dict):
        report.add(location, "schema", "`fix` must be an object with `path`, `start_line`, and optional `end_line`")
        return None
    path = read_line(report, location, fix, "path")
    start = fix.get("start_line")
    end = fix.get("end_line", start)
    for key, value in (("start_line", start), ("end_line", end)):
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            report.add(location, "fix-coordinate", f"`{key}` must be an integer of at least 1")
            return None
    if end < start:
        report.add(location, "fix-coordinate", "`end_line` must be at or after `start_line`")
        return None
    if path is None:
        return None
    coordinate = f"{encode_path(path)}:{start}" if end == start else f"{encode_path(path)}:{start}-{end}"
    return coordinate


def compose_finding(report: Report, location: str, finding: Any, head: str) -> dict[str, Any] | None:
    if not isinstance(finding, dict):
        report.add(location, "schema", "a finding must be an object")
        return None
    identity = read_id(report, location, finding)
    title = read_line(report, location, finding, "title")
    priority, action, kind = finding.get("priority"), finding.get("action"), finding.get("kind")
    if priority not in PRIORITIES:
        report.add(location, "priority-action", f"`priority` must be one of {list(PRIORITIES)}, not `{priority!r}`")
    if action not in ACTIONS:
        report.add(location, "priority-action", f"`action` must be one of {list(ACTIONS)}, not `{action!r}`")
    if kind not in KINDS:
        report.add(location, "priority-action", f"`kind` must be one of {list(KINDS)}, not `{kind!r}`")
    if priority == "P0" and action == "consider":
        report.add(location, "priority-action", "P0 is inherently `must-fix`; a P0 `consider` is contradictory")
    blocking = finding.get("blocking")
    derived = action == "must-fix"
    if blocking is None:
        blocking = derived
    elif not isinstance(blocking, bool):
        report.add(location, "priority-action", "`blocking` must be a boolean when present")
    elif action in ACTIONS and blocking != derived:
        report.add(
            location,
            "priority-action",
            f"`blocking={str(blocking).lower()}` contradicts `action={action}`; `must-fix` is blocking and `consider` is not",
        )
    prose: dict[str, str | None] = {}
    for key in ("trigger", "impact", "change"):
        prose[key] = read_text(report, location, finding, key)
    prose["source"] = read_text(report, location, finding, "source", required=False)
    for key, text in prose.items():
        if text is not None:
            check_prose_labels(report, location, key, text)
    anchor = finding.get("anchor")
    check_anchor_input(report, f"{location}.anchor", anchor)
    fix = None
    if finding.get("fix") is not None:
        fix = compose_fix(report, f"{location}.fix", finding["fix"])
        fix_path = finding["fix"].get("path") if isinstance(finding["fix"], dict) else None
        anchor_path = anchor.get("path") if isinstance(anchor, dict) else None
        if isinstance(fix_path, str) and fix_path != anchor_path and prose["change"] is not None and fix_path not in prose["change"]:
            report.add(
                location,
                "fix-site",
                f"`fix` names `{fix_path}`, which differs from the anchor, so the visible `change` prose must name that path too; "
                "the trailer is never authoritative",
            )
    if identity is None or title is None or any(prose[key] is None for key in ("trigger", "impact", "change")):
        return None
    if priority not in PRIORITIES or action not in ACTIONS or kind not in KINDS or not isinstance(blocking, bool):
        return None
    paragraphs = [
        f"**[{priority}] [{action}] {title}**",
        f"**Triggers when:** {prose['trigger']}",
        f"**Impact:** {prose['impact']}",
        f"**Change:** {prose['change']}",
    ]
    if prose["source"] is not None:
        paragraphs.append(f"**Source:** {prose['source']}")
    if action == "consider":
        paragraphs.append(PERMISSION_SENTENCE)
    trailer = (
        f"<!-- finding id={identity} head={head} priority={priority} action={action} "
        f"blocking={'true' if blocking else 'false'} kind={kind}"
    )
    if fix is not None:
        trailer += f" fix={fix}"
    trailer += " -->"
    item: dict[str, Any] = {
        "type": "finding",
        "id": identity,
        "markdown": "\n\n".join(paragraphs),
        "trailer": trailer,
        "priority": priority,
        "action": action,
        "blocking": blocking,
        "kind": kind,
        "anchor": anchor,
    }
    if fix is not None:
        item["fix"] = fix
    return item


def compose_question(report: Report, location: str, question: Any, head: str) -> dict[str, Any] | None:
    if not isinstance(question, dict):
        report.add(location, "schema", "a question must be an object")
        return None
    identity = read_id(report, location, question)
    title = read_line(report, location, question, "title")
    for key in ("priority", "blocking", "kind", "fix"):
        if question.get(key) is not None:
            report.add(location, "question-form", f"a question carries no `{key}`")
    prose = {key: read_text(report, location, question, key) for key in ("evidence", "why_it_matters", "answer")}
    for key, text in prose.items():
        if text is None:
            continue
        check_prose_labels(report, location, key, text)
        masked = mask_code(text)
        if "**Change:**" in masked:
            report.add(location, "question-form", f"`{key}` states a `**Change:**` field; a question requests no code change")
        if QUESTION_FRAMING in masked:
            report.add(location, "question-form", f"`{key}` contains the `{QUESTION_FRAMING}` framing; the composer adds it before `answer`")
    anchor = question.get("anchor")
    check_anchor_input(report, f"{location}.anchor", anchor)
    if identity is None or title is None or any(text is None for text in prose.values()):
        return None
    markdown = "\n\n".join(
        [
            f"**[Question] {title}**",
            f"**Evidence:** {prose['evidence']}",
            f"**Why it matters:** {prose['why_it_matters']}",
            f"**{QUESTION_FRAMING}.** {prose['answer']}",
        ]
    )
    return {
        "type": "question",
        "id": identity,
        "markdown": markdown,
        "trailer": f"<!-- question id={identity} head={head} action=question -->",
        "anchor": anchor,
    }


def compose_observation(report: Report, location: str, observation: Any) -> dict[str, Any] | None:
    if not isinstance(observation, dict):
        report.add(location, "schema", "an observation must be an object")
        return None
    fact = read_text(report, location, observation, "fact")
    evidence = read_text(report, location, observation, "evidence")
    if fact is None or evidence is None:
        return None
    for key, text in (("fact", fact), ("evidence", evidence)):
        check_prose_labels(report, location, key, text, observation=True)
    return {"type": "observation", "markdown": f"{fact} Evidence: {evidence}"}


def read_prior_item(report: Report, location: str, prior: Any) -> dict[str, Any] | None:
    if not isinstance(prior, dict):
        report.add(location, "schema", "a prior item must be an object")
        return None
    identity = read_id(report, location, prior)
    classification = prior.get("classification")
    if classification not in CLASSIFICATIONS:
        report.add(location, "prior-item", f"`classification` must be one of {list(CLASSIFICATIONS)}, not `{classification!r}`")
    action = prior.get("action")
    if action not in PRIOR_ACTIONS:
        report.add(location, "prior-item", f"`action` must be one of {list(PRIOR_ACTIONS)}, not `{action!r}`")
    note = read_line(report, location, prior, "note")
    if identity is None or classification not in CLASSIFICATIONS or action not in PRIOR_ACTIONS or note is None:
        return None
    return {"id": identity, "classification": classification, "action": action, "note": note}


def read_run(report: Report, run: Any) -> dict[str, Any] | None:
    if not isinstance(run, dict):
        report.add("run", "schema", "`run` must be an object")
        return None
    fields: dict[str, Any] = {}
    kind = run.get("target_kind", "pull-request")
    if kind not in ("pull-request", "range", "worktree"):
        report.add("run.target_kind", "schema", "expected pull-request, range, or worktree")
    fields["target_kind"] = kind
    fields["target"] = read_line(report, "run", run, "target") if kind == "range" else None
    tree = run.get("tree")
    if kind == "worktree" and (not isinstance(tree, str) or not COMMIT_SHA_RE.fullmatch(tree)):
        report.add("run.tree", "schema", "worktree requires a full 40-hex tree SHA")
    fields["tree"] = tree
    if kind in LOCAL:
        description = run.get("change_description")
        if not isinstance(description, str):
            report.add("run.change_description", "schema", "local targets require commit messages (empty string when none)")
        fields["change_description"] = description
        if run.get("merged") is not False or run.get("repository_url") is not None:
            report.add("run", "schema", "local targets require merged=false and omit repository_url")
    specs = run.get("specs", [])
    if not isinstance(specs, list) or not all(isinstance(s, str) and s.strip() and "\n" not in s for s in specs):
        report.add("run.specs", "schema", "`specs` must list the identities of caller-supplied issues or specs, one line each (empty for none)")
        specs = []
    fields["specs"] = specs
    supplied = run.get("supplied_inputs")
    if supplied not in SUPPLIED_INPUTS:
        report.add("run.supplied_inputs", "trailer-grammar", f"`supplied_inputs` must be one of {list(SUPPLIED_INPUTS)}, not `{supplied!r}`")
    elif (supplied == "yes") != bool(specs):
        report.add("run.supplied_inputs", "trailer-grammar",
                   f"`supplied_inputs={supplied}` contradicts {len(specs)} caller-supplied issue or spec identities in `specs`")
    fields["supplied_inputs"] = supplied
    for key in ("head", "base_sha", "merge_base"):
        value = run.get(key)
        if not isinstance(value, str) or not COMMIT_SHA_RE.match(value):
            report.add(f"run.{key}", "trailer-sha", f"`{key}` must be exactly 40 lowercase hexadecimal characters")
        fields[key] = value
    base_ref = run.get("base_ref")
    if not isinstance(base_ref, str) or not token(base_ref):
        report.add("run.base_ref", "trailer-grammar", "`base_ref` must be a single printable ASCII token")
    fields["base_ref"] = base_ref
    for retired, why in (("context", "the model-authored context digest is retired; the pull request's `packet_context` comes from the packet"),
                         ("publication_authorized", "review-code-publish alone decides whether a merged target publishes")):
        if retired in run:
            report.add(f"run.{retired}", "schema", f"omit `{retired}`: {why}")
    packet_context = run.get("packet_context")
    if kind in LOCAL:
        if packet_context is not None:
            report.add("run.packet_context", "trailer-grammar", "a local target has no packet, so it carries no `packet_context`")
        packet_context = "none"
    elif not isinstance(packet_context, str) or not DIGEST_RE.match(packet_context):
        report.add("run.packet_context", "trailer-grammar",
                   "`packet_context` must be the 64-character lowercase SHA-256 digest forge_packet.py computes from the packet")
    fields["packet_context"] = packet_context
    issues = run.get("issues")
    if not isinstance(issues, list) or not all(isinstance(issue, str) and ISSUE_RE.match(issue) for issue in issues):
        report.add("run.issues", "trailer-grammar", "`issues` must be a list of `owner/repo#number` coordinates (empty for none)")
        fields["issues"] = None
    else:
        fields["issues"] = ",".join(sorted(issues)) if issues else "none"
    coverage = run.get("coverage")
    if coverage not in COVERAGE:
        report.add("run.coverage", "trailer-grammar", f"`coverage` must be one of {list(COVERAGE)}, not `{coverage!r}`")
    fields["coverage"] = coverage
    merged = run.get("merged")
    if not isinstance(merged, bool):
        report.add(
            "run.merged",
            "schema",
            "`merged` must be a boolean recorded from the pinned packet; a missing `merged` is an unrecoverable input, not something to infer",
        )
    fields["merged"] = merged
    prior_head = run.get("prior_head")
    if prior_head is not None and (not isinstance(prior_head, str) or not COMMIT_SHA_RE.match(prior_head)):
        report.add("run.prior_head", "trailer-sha", "`prior_head` must be exactly 40 lowercase hexadecimal characters when present")
    fields["prior_head"] = prior_head
    repository_url = run.get("repository_url")
    if repository_url is not None and (not isinstance(repository_url, str) or not REPOSITORY_URL_RE.match(repository_url)):
        report.add("run.repository_url", "schema", "`repository_url` must be the base repository's canonical http(s) web URL when present")
        repository_url = None
    fields["repository_url"] = repository_url
    return fields


def read_summary(report: Report, summary: Any, coverage: Any) -> dict[str, Any] | None:
    if not isinstance(summary, dict):
        report.add("summary", "schema", "`summary` must be an object")
        return None
    fields: dict[str, Any] = {}
    status = summary.get("status")
    if status not in STATUSES:
        report.add("summary.status", "status-consistency", f"`status` must be one of {list(STATUSES)}, not `{status!r}`; the reviewer selects it")
    fields["status"] = status
    if "gating" in summary:
        report.add("summary.gating", "publication-boundary", "inspect composition is advisory; omit `gating` and let the publisher select --emit-batch --event")
    for key in ("intent", "issue_fit", "coverage"):
        fields[key] = read_text(report, "summary", summary, key)
        if fields[key] is not None:
            for match in re.finditer(r"\*\*(Intent|Issue fit|Coverage|Reviewed|Mode):\*\*", mask_code(fields[key])):
                report.add(f"summary.{key}", "field-label", f"`{key}` contains the composer-owned label `{match.group(0)}` outside code")
    ambiguities = summary.get("ambiguities", [])
    if not isinstance(ambiguities, list):
        report.add("summary.ambiguities", "schema", "`ambiguities` must be a list")
        ambiguities = []
    entries: list[dict[str, str]] = []
    for index, ambiguity in enumerate(ambiguities):
        location = f"summary.ambiguities[{index}]"
        if not isinstance(ambiguity, dict):
            report.add(location, "schema", "an ambiguity must be an object")
            continue
        term = read_line(report, location, ambiguity, "term")
        applied = read_line(report, location, ambiguity, "applied")
        readings = ambiguity.get("readings")
        if not isinstance(readings, list) or len(readings) < 2 or not all(isinstance(r, str) and r.strip() and "\n" not in r for r in readings):
            report.add(location, "schema", "`readings` must list at least two supportable readings, each one line")
            continue
        if term is not None and applied is not None:
            entries.append({"term": term, "readings": readings, "applied": applied})
    fields["ambiguities"] = entries
    gaps = summary.get("coverage_gaps", [])
    if not isinstance(gaps, list) or not all(isinstance(gap, str) and gap.strip() and "\n" not in gap for gap in gaps):
        report.add("summary.coverage_gaps", "schema", "`coverage_gaps` must be a list of one-line entries")
        gaps = []
    if coverage == "incomplete" and not gaps:
        report.add(
            "summary.coverage_gaps",
            "coverage-gaps",
            "`run.coverage` is `incomplete`, so `coverage_gaps` must name each uncovered file, check, connection, or verification",
        )
    if coverage == "complete" and gaps:
        report.add("summary.coverage_gaps", "coverage-gaps", "`coverage_gaps` is non-empty, which contradicts `run.coverage=complete`")
    fields["coverage_gaps"] = gaps
    return fields


def check_status(
    report: Report,
    status: Any,
    coverage: Any,
    findings: list[dict[str, Any]],
    questions: list[dict[str, Any]],
    priors: list[dict[str, Any]],
) -> None:
    """The mechanical implications of the output contract's status precedence.

    A must-fix finding, or a prior must-fix item that is still open, not
    verifiable, or disputed, is an unsettled blocker and forces ``Changes
    Requested``; with no blocker, incomplete coverage forces ``Incomplete``;
    ``Needs Information`` needs an open question. Whether an open question could
    change the verdict stays the reviewer's choice between ``Needs Information``
    and ``Approved``.
    """
    if status not in STATUSES:
        return
    blockers = [f["id"] for f in findings if f["action"] == "must-fix"]
    blockers += [p["id"] for p in priors if p["action"] == "must-fix" and p["classification"] in OPEN_CLASSIFICATIONS]
    open_questions = len(questions) + sum(1 for p in priors if p["action"] == "question" and p["classification"] in OPEN_CLASSIFICATIONS)
    if blockers and status != "Changes Requested":
        report.add(
            "summary.status",
            "status-consistency",
            f"`{status}` contradicts the unsettled must-fix item(s) {', '.join(f'`{b}`' for b in blockers)}; "
            "an unsettled blocker is `Changes Requested`",
        )
    elif not blockers and status == "Changes Requested":
        report.add("summary.status", "status-consistency", "`Changes Requested` needs an unsettled must-fix finding or prior item; none is supplied")
    if not blockers and coverage == "incomplete" and status != "Incomplete":
        report.add("summary.status", "status-consistency", f"`{status}` contradicts `run.coverage=incomplete` with no known blocker; that is `Incomplete`")
    if coverage == "complete" and status == "Incomplete":
        report.add("summary.status", "status-consistency", "`Incomplete` contradicts `run.coverage=complete`; name the gap or select another status")
    if status == "Needs Information" and open_questions == 0:
        report.add("summary.status", "status-consistency", "`Needs Information` needs at least one open question; none is supplied")


def check_identities(
    report: Report,
    findings: list[tuple[str, dict[str, Any]]],
    questions: list[tuple[str, dict[str, Any]]],
    priors: list[tuple[str, dict[str, Any]]],
    carried: bool = False,
) -> None:
    """Stable ids name one item; a pull-request prior item is answered on its thread, never posted again. On a local
    ``prior_record`` run (``carried``) an open prior item is instead carried as a rendered item under its own id."""
    seen: dict[str, str] = {}
    for location, item in findings + questions:
        if item["id"] in seen:
            report.add(location, "stable-id", f"`id={item['id']}` is already used by {seen[item['id']]}; a stable id names one defect concept")
        seen[item["id"]] = location
    prior_seen: dict[str, str] = {}
    new_types = {item["id"]: ("finding" if item["type"] == "finding" else "question") for _l, item in findings + questions}
    for location, prior in priors:
        if prior["id"] in prior_seen:
            report.add(location, "stable-id", f"prior item `{prior['id']}` is already listed by {prior_seen[prior['id']]}")
        prior_seen[prior["id"]] = location
        prior_type = "question" if prior["action"] == "question" else "finding"
        if carried:
            if new_types.get(prior["id"]) is not None and prior["classification"] not in OPEN_CLASSIFICATIONS:
                report.add(location, "stable-id", f"prior {prior_type} `{prior['id']}` is {prior['classification']}, so it is "
                           "settled and not rendered again; a new defect takes a new id")
        elif new_types.get(prior["id"]) == prior_type:
            report.add(
                location,
                "stable-id",
                f"prior {prior_type} `{prior['id']}` is replied to on its existing thread under references/prior-state.md; "
                f"a new {prior_type} with the same id would post a duplicate comment",
            )


def require_file_sides(report: Report, items: list[tuple[str, dict[str, Any]]]) -> None:
    """Without a store there is no pinned manifest to derive a file anchor's side from."""
    for location, item in items:
        anchor = item.get("anchor")
        if isinstance(anchor, dict) and anchor.get("type") == "file" and "side" not in anchor:
            report.add(
                f"{location}.anchor",
                "anchor-provenance",
                "without `--store` a file anchor names its `side`: `LEFT` for a file the change deletes, `RIGHT` for a file at the head, "
                "or `UNKNOWN` when the path or revision is unestablished; with `--store` the pinned manifest supplies it",
            )


def check_store(report: Report, store: dict[str, Any], run: dict[str, Any], items: list[tuple[str, dict[str, Any]]]) -> None:
    """Check anchors against the persisted review context's pinned manifest and run identity, and derive an
    omitted file-anchor side the manifest establishes."""
    if store.get("format") != rc.STORE_FORMAT or not isinstance(store.get("context"), dict):
        report.add("store", "schema", f"expected a `{rc.STORE_FORMAT}` envelope with a `context` object from review_context.py --store")
        return
    context = store["context"]
    if run.get("target_kind") == "worktree":
        snapshot = context.get("snapshot", {})
        if not isinstance(snapshot, dict) or snapshot.get("tree") != run.get("tree") or snapshot.get("head") != run.get("head"):
            report.add("run.tree", "run-identity", "worktree identity disagrees with the store's snapshot")
    for key, run_key in (("head", "head"), ("merge_base", "merge_base")):
        if context.get(key) != run.get(run_key):
            report.add(f"run.{run_key}", "run-identity", f"the store was built for {key} `{context.get(key)}`, not `{run.get(run_key)}`")
    manifest = context.get("manifest")
    if not isinstance(manifest, list):
        report.add("store", "schema", "the store carries no `manifest` list")
        return
    known: set[str] = set()
    deleted: set[str] = set()
    added: set[str] = set()
    file_sides: dict[str, set[str | None]] = {}
    for entry in manifest:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        known.add(entry["path"])
        file_sides.setdefault(entry["path"], set()).add(MANIFEST_FILE_SIDES.get(str(entry.get("status", ""))[:1]))
        if str(entry.get("status", "")).startswith("D"):
            deleted.add(entry["path"])
        if str(entry.get("status", "")).startswith("A"):
            added.add(entry["path"])
    for location, item in items:
        anchor = item.get("anchor")
        if not isinstance(anchor, dict) or not isinstance(anchor.get("path"), str):
            continue
        path = anchor["path"]
        if path not in known:
            report.add(f"{location}.anchor", "anchor-provenance", f"`{path}` is not in the pinned merge-base manifest; an anchor names a changed file")
            continue
        if anchor.get("type") == "file" and "side" not in anchor:
            derived = file_sides[path]
            if len(derived) == 1 and None not in derived:
                item["anchor"] = {**anchor, "side": next(iter(derived))}
            else:
                report.add(
                    f"{location}.anchor",
                    "anchor-provenance",
                    f"the pinned manifest does not establish one revision for `{path}`, so the file anchor names its `side`: "
                    "`UNKNOWN` with the missing evidence explained in the item, unless other evidence establishes `LEFT` or `RIGHT`",
                )
            continue
        side = anchor.get("side")
        if path in deleted and side == "RIGHT":
            report.add(f"{location}.anchor", "anchor-provenance", f"`{path}` is a `D` entry of the pinned manifest, so its side is `LEFT`, not `RIGHT`")
        elif anchor.get("type") == "line" and path in added and side == "LEFT":
            report.add(f"{location}.anchor", "anchor-provenance", f"`{path}` is an `A` entry of the pinned manifest, so its side is `RIGHT`, not `LEFT`")
        elif anchor.get("type") == "file" and path not in deleted and side == "LEFT":
            report.add(f"{location}.anchor", "anchor-provenance", f"`{path}` is not a `D` entry of the pinned manifest, so `LEFT` does not apply")


def index_entry(item: dict[str, Any], title: str, fragment: str) -> str:
    if item["type"] == "finding":
        return f"- [{item['priority']}] [{item['action']}] {title} — {fragment}"
    return f"- [Question] {title} — {fragment}"


def body_carried(item: dict[str, Any], title: str, fragment: str) -> str:
    return f"{index_entry(item, title, fragment)}\n\n{item['markdown']}\n\n{item['trailer']}"


def compose_body(
    report: Report,
    run: dict[str, Any],
    summary: dict[str, Any],
    findings: list[tuple[str, dict[str, Any], str]],
    questions: list[tuple[str, dict[str, Any], str]],
    observations: list[dict[str, Any]],
    priors: list[dict[str, Any]],
    trailer: str,
) -> str:
    identity = {"head": run["head"], "merge_base": run["merge_base"], "repository_url": run["repository_url"]}
    fragments: dict[str, str] = {}
    owners: dict[str, str] = {}
    for location, item, _title in findings + questions:
        fragment = render_reference(item, identity)
        if fragment is None:
            report.add(f"{location}.anchor", "anchor-shape", "cannot render a coordinate fragment from this anchor or fix")
            fragment = ""
        elif fragment in owners:
            report.add(
                location,
                SUMMARY_REFERENCE,
                f"renders the same anchor and fix fragment as {owners[fragment]}; the summary carries each fragment once, "
                "so two distinct defects need distinct anchors or fix sites",
            )
        else:
            owners[fragment] = location
        fragments[location] = fragment

    must_fix = sum(1 for _l, f, _t in findings if f["action"] == "must-fix")
    consider = len(findings) - must_fix
    open_priors = [p for p in priors if p["classification"] in ("still-open", "not-verifiable")]
    disputed = [p for p in priors if p["classification"] == "disputed"]
    counts: list[str] = []
    if must_fix:
        counts.append(plural(must_fix, "must-fix finding"))
    if consider:
        counts.append(plural(consider, "consider finding"))
    if questions:
        counts.append(plural(len(questions), "open question"))
    if open_priors:
        counts.append(f"{plural(len(open_priors), 'prior item')} still open")
    if disputed:
        counts.append(plural(len(disputed), "disputed prior finding"))
    status = summary["status"]
    if status in ADVISORY_STATUSES:
        status += " (advisory)"
    first = f"**{status}** — {', '.join(counts) if counts else 'no findings'}."
    if run["prior_head"] is not None:
        first += f" Delta review of `{abbreviate(run['prior_head'])}..{abbreviate(run['head'])}`."
    paragraphs = [first]
    if run["merged"]:
        paragraphs.append(MODE_LINE)
    reviewed = f"`{abbreviate(run['head'])}` against merge-base `{abbreviate(run['merge_base'])}`."
    issue_fit = summary["issue_fit"]
    if run["target_kind"] != "pull-request":
        if run["target_kind"] == "worktree":
            reviewed = f"Working tree snapshot `{run['head']}` (tree `{run['tree']}`) against merge-base `{abbreviate(run['merge_base'])}`."
        else:
            reviewed = f"Range `{run['target']}`: {reviewed}"
        sources = []
        if run["issues"] != "none":
            sources.append("originating issues")
        if run["specs"]:
            sources.append("user-supplied spec")
        if run["change_description"].strip():
            sources.append("commit messages in the range")
        source = "; ".join(sources) if sources else "no source (no issue, spec, or commit messages)"
        issue_fit += f" Source: {source}."
    paragraphs.extend(
        [
            f"**Intent:** {summary['intent']}",
            f"**Issue fit:** {issue_fit}",
            f"**Coverage:** {summary['coverage']}",
            f"**Reviewed:** {reviewed}",
        ]
    )

    inline = [(l, f, t) for l, f, t in findings if f["anchor"].get("type") == "line"]
    unanchored = [(l, f, t) for l, f, t in findings if f["anchor"].get("type") != "line"]
    if inline:
        paragraphs.append("## Findings\n\n" + "\n".join(index_entry(f, t, fragments[l]) for l, f, t in inline))
    if questions:
        entries = [
            index_entry(q, t, fragments[l]) if q["anchor"].get("type") == "line" else body_carried(q, t, fragments[l])
            for l, q, t in questions
        ]
        paragraphs.append("## Open questions\n\n" + "\n\n".join(entries))
    if observations:
        paragraphs.append("## Observations\n\n" + "\n".join(f"- {o['markdown']}" for o in observations))
    if summary["ambiguities"]:
        lines = []
        for entry in summary["ambiguities"]:
            readings = "; ".join(f"({chr(97 + i)}) {r}" for i, r in enumerate(entry["readings"]))
            lines.append(f"- **{entry['term']}** — {readings}. Applied: {entry['applied']}")
        paragraphs.append("## Ambiguities\n\n" + "\n".join(lines))
    if unanchored:
        paragraphs.append(f"## Unanchored findings\n\n{UNANCHORED_NOTE}\n\n" + "\n\n".join(body_carried(f, t, fragments[l]) for l, f, t in unanchored))
    if disputed:
        paragraphs.append("## Disputed\n\n" + "\n".join(f"- `{p['id']}` — disputed: {p['note']}" for p in disputed))
    accounted = [p for p in priors if p["classification"] != "disputed"]
    if accounted:
        paragraphs.append("## Prior findings\n\n" + "\n".join(f"- `{p['id']}` — {p['classification']}: {p['note']}" for p in accounted))
    if summary["coverage_gaps"]:
        paragraphs.append("## Coverage gaps\n\n" + "\n".join(f"- {gap}" for gap in summary["coverage_gaps"]))
    paragraphs.append(trailer)
    return "\n\n".join(paragraphs) + "\n"


def translate(line: str, locations: list[str]) -> str:
    """Rewrite a validator violation's ``items[<n>]`` to the composition input location it came from."""

    def replace(match: re.Match[str]) -> str:
        index = int(match.group("index"))
        return locations[index] if index < len(locations) else match.group(0)

    return ITEM_INDEX_RE.sub(replace, line)


def read_rows(report: Report, location: str, value: Any, keys: tuple[str, ...]) -> list[tuple[str, dict[str, Any]]]:
    """``(location, row)`` for each object whose named keys are non-empty single lines, at its input index; a row
    missing one is reported and skipped, and later violations still name the surviving rows' own indexes."""
    if not isinstance(value, list):
        report.add(location, "schema", f"`{location.rsplit('.', 1)[-1]}` must be a list of objects")
        return []
    rows: list[tuple[str, dict[str, Any]]] = []
    for index, raw in enumerate(value):
        where = f"{location}[{index}]"
        if not isinstance(raw, dict):
            report.add(where, "schema", "expected an object")
        elif all(read_line(report, where, raw, key) is not None for key in keys):
            rows.append((where, raw))
    return rows


def read_lines(report: Report, location: str, value: Any) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() and "\n" not in v for v in value):
        report.add(location, "schema", f"`{location.rsplit('.', 1)[-1]}` must be a list of one-line entries")
        return []
    return value


def names_task(entries: list[str], identity: str) -> bool:
    """Whether an ``outstanding`` entry names a task: the id alone, or the id followed by ``:`` and a reason."""
    return any(entry == identity or entry.startswith(identity + ":") for entry in entries)


def task_id(entry: str) -> str:
    """The task or item id an ``outstanding`` or routed entry names: the text before ``:``."""
    return entry.split(":", 1)[0].strip()


def load_object(path: str) -> tuple[dict[str, Any] | None, str]:
    """A JSON object read from an absolute path, or ``None`` and why it cannot establish anything."""
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, ValueError) as error:
        return None, f"cannot be read ({error.__class__.__name__})"
    return (value, "") if isinstance(value, dict) else (None, "is not a JSON object")


def finalization_problem(doc: dict[str, Any]) -> str:
    """Why a record's finalization cannot be consumed, or ``""``.

    A record is consumable only when it names this protocol and the report it names exists: finalization promotes
    that report last, so an interrupted run never reads as success. A record without ``finalization``, or naming any
    other protocol, establishes nothing.
    """
    finalization = doc.get("finalization")
    if finalization is None:
        return "carries no finalization marker"
    protocol = finalization.get("protocol") if isinstance(finalization, dict) else None
    if protocol != FINALIZATION_PROTOCOL:
        return f"names finalization protocol {json.dumps(protocol)}, not `{FINALIZATION_PROTOCOL}`"
    report = finalization.get("report")
    if not isinstance(report, str) or not report.startswith("/"):
        return "names no absolute finalization report"
    if not os.path.isfile(report):
        return f"names finalization report `{report}`, which does not exist, so its finalization did not complete"
    return ""


def role_list(doc: dict[str, Any], section: str, role: str) -> list[Any]:
    """``doc[section][role]`` when it is a list; anything malformed reads as empty and so establishes nothing."""
    value = doc.get(section)
    value = value.get(role) if isinstance(value, dict) else None
    return value if isinstance(value, list) else []


def accounted_ruling(accounting: str, role: str, identity: str) -> tuple[str | None, str]:
    """The ruling a verifier accounting report establishes for one task id: its ruling, ``withheld``, or ``None`` and why."""
    doc, why = load_object(accounting)
    if doc is None:
        return None, f"accounting report `{accounting}` {why}"
    if identity in role_list(doc, "withheld", role):
        return "withheld", ""
    if identity not in role_list(doc, "accounted", role):
        return None, f"accounting report `{accounting}` does not account for `{identity}` among its {role}"
    for record in role_list(doc, "return", role):
        if isinstance(record, dict) and record.get("id") == identity:
            if role == "premises":
                return record.get("ruling"), ""
            if record.get("verdict") == "refuted" and record.get("basis") == "unresolved":
                return "unresolved", ""
            return record.get("verdict"), ""
    return None, f"accounting report `{accounting}` holds no returned record for `{identity}`"


# --- prior record ---------------------------------------------------------------------------------------------------


def same_path(explicit: Any, owned: str) -> bool:
    return isinstance(explicit, str) and (os.path.abspath(explicit) == os.path.abspath(owned)
                                          or os.path.realpath(explicit) == os.path.realpath(owned))


def load_prior(path: str) -> tuple[dict[str, Any] | None, list[str]]:
    """The state a ``prior_record`` run continues, or ``None`` and one refusal line per reason.

    A prior record is a finalized ``review-code-record/1`` of a local target. Its open items are the findings and
    questions it renders; a record written before this schema (an implementation-gate record or an addenda chain)
    is not a prior record.
    """
    report = Report()
    where = "prior_record"
    if not isinstance(path, str) or not path.startswith("/"):
        report.add(where, "prior-record", f"`{path}` is not an absolute path")
        return None, report.lines
    doc, why = load_object(path)
    if doc is None:
        report.add(where, "prior-record", f"`{path}` {why}")
        return None, report.lines
    if doc.get("schema") != RECORD_SCHEMA:
        report.add(where, "prior-record", f"`{path}` is a {json.dumps(doc.get('schema'))} record, not `{RECORD_SCHEMA}`; review "
                   "an earlier record's head in full from its base without a prior record, with a new allowance, and "
                   "say so in coverage")
        return None, report.lines
    why = finalization_problem(doc)
    if why:
        report.add(where, "prior-record", f"`{path}` {why}")
        return None, report.lines
    run, record = doc.get("run"), doc.get("record")
    verification = record.get("verification") if isinstance(record, dict) else None
    routed = record.get("routed") if isinstance(record, dict) else None
    lineage = doc.get("lineage")
    if not (isinstance(run, dict) and isinstance(verification, dict) and isinstance(routed, dict)
            and isinstance(verification.get("allowance"), dict) and isinstance(verification.get("tasks"), list)
            and isinstance(verification.get("batches"), list) and isinstance(verification.get("outstanding"), list)
            and isinstance(lineage, list) and all(isinstance(entry, str) and entry.startswith("/") for entry in lineage)
            and isinstance(doc.get("items"), list)):
        report.add(where, "prior-record", f"`{path}` lacks the record's run, verification, routed state, items or lineage")
        return None, report.lines
    if run.get("target_kind") not in LOCAL:
        report.add(where, "prior-record", f"`{path}` reviewed a {run.get('target_kind')}; a prior record continues a local target")
        return None, report.lines
    items = {item["id"]: {"type": item["type"], "action": item.get("action", "question") if item["type"] == "finding" else "question"}
             for item in doc["items"] if isinstance(item, dict) and item.get("type") in ("finding", "question")}
    allowance = verification["allowance"]
    return {
        "path": path, "doc": doc, "head": run.get("head"), "base_ref": run.get("base_ref"), "base_sha": run.get("base_sha"),
        "coverage": run.get("coverage"),
        "repository": record.get("repository"), "lineage": list(lineage), "items": items,
        "allowance": {flag: allowance.get(flag) is True for flag in ("initial_spent", "follow_up_spent")},
        "outstanding": [e for e in verification["outstanding"] if isinstance(e, str)],
        "routed": {key: [e for e in routed.get(key) or [] if isinstance(e, str)] for key in ("unresolved", "disputed", "unrecoverable_inputs")},
        "tasks": {t["id"]: t for t in verification["tasks"] if isinstance(t, dict) and isinstance(t.get("id"), str)},
        "batches": {b["name"]: b.get("accounting") for b in verification["batches"] if isinstance(b, dict) and isinstance(b.get("name"), str)},
    }, []


def carried_accounting(prior: dict[str, Any], chain_record: str, batch: str) -> tuple[str | None, str]:
    """The accounting report a record in the prior's chain holds for ``batch``."""
    if same_path(chain_record, prior["path"]):
        doc_batches = prior["batches"]
    else:
        doc, why = load_object(chain_record)
        if doc is None:
            return None, f"`{chain_record}` {why}"
        why = finalization_problem(doc)
        if why:
            return None, f"`{chain_record}` {why}"
        verification = doc.get("record", {}).get("verification") if isinstance(doc.get("record"), dict) else None
        batches = verification.get("batches") if isinstance(verification, dict) else None
        doc_batches = {b.get("name"): b.get("accounting") for b in batches or [] if isinstance(b, dict)}
    accounting = doc_batches.get(batch)
    if not isinstance(accounting, str):
        return None, f"`{chain_record}` records no batch `{batch}` with an accounting report"
    return accounting, ""


def check_carried(report: Report, location: str, task: dict[str, Any], prior: dict[str, Any] | None,
                  rendered_findings: set[str]) -> None:
    """A carried confirmation names the record and batch whose accounting confirmed it, through the prior's own entry."""
    identity, source, batch = task["id"], task.get("confirmed_in"), task.get("batch")
    if prior is None:
        report.add(location, "verification", f"task `{identity}` carries a confirmation, which only a prior_record run does")
        return
    if task["type"] != "candidate" or task["ruling"] != "confirmed":
        report.add(location, "verification", "`confirmed_in` carries a `confirmed` candidate task only")
        return
    if identity not in rendered_findings:
        report.add(location, "verification", f"task `{identity}` carries a confirmation for a finding this record does not render")
    if not isinstance(source, str) or not source.startswith("/") or not isinstance(batch, str) or not batch:
        report.add(location, "verification", "a carried confirmation names an absolute `confirmed_in` record and its `batch`")
        return
    chain = [prior["path"], *prior["lineage"]]
    if not any(same_path(source, entry) for entry in chain):
        report.add(location, "verification", f"`confirmed_in` `{source}` is neither the prior record nor in its lineage")
        return
    earlier = prior["tasks"].get(identity)
    if earlier is None or earlier.get("type") != "candidate" or earlier.get("ruling") != "confirmed":
        report.add(location, "verification", f"the prior record holds no confirmed candidate task `{identity}` to carry")
        return
    if earlier.get("trigger") != task.get("trigger"):
        report.add(location, "verification", f"task `{identity}` carries trigger `{task.get('trigger')}`, but the prior "
                   f"record confirmed it under `{earlier.get('trigger')}`")
    provenance = (earlier.get("confirmed_in"), earlier.get("batch"))
    if provenance[0] is None:
        provenance = (prior["path"], earlier.get("batch"))
    if not (same_path(source, provenance[0]) and batch == provenance[1]):
        report.add(location, "verification", f"task `{identity}` names `{source}#{batch}`, but the prior record's confirmation "
                   f"came from `{provenance[0]}#{provenance[1]}`; carry that provenance unchanged")
        return
    accounting, why = carried_accounting(prior, source, batch)
    if accounting is not None:
        established, why = accounted_ruling(accounting, "candidates", identity)
        if established is not None and established != "confirmed":
            why = f"accounting report `{accounting}` establishes `{established}`, not `confirmed`"
    if why:
        report.add(location, "verification", f"task `{identity}`: {why}; a carried confirmation stands only on the "
                   "verifier result that accounted for it")


def check_prior(report: Report, prior: dict[str, Any], run: dict[str, Any], record: Any, items: list[dict[str, Any]],
                priors: list[tuple[str, dict[str, Any]]], tasks: list[dict[str, Any]], outstanding: list[str]) -> None:
    """What a ``prior_record`` run keeps from its prior: identity, classified open items and surviving state."""
    if run["target_kind"] not in LOCAL:
        report.add("prior_record", "prior-record", "a prior record continues a local target; a pull request carries prior state from its packet")
        return
    repository = record.get("repository") if isinstance(record, dict) else None
    if not (repository == prior["repository"] or (isinstance(repository, str) and isinstance(prior["repository"], str)
                                                   and repository.startswith("/") and same_path(repository, prior["repository"]))):
        report.add("record.repository", "prior-record", f"reviews {json.dumps(repository)}, but the prior record reviewed "
                   f"{json.dumps(prior['repository'])}")
    for key in ("base_ref", "base_sha"):
        if run.get(key) != prior[key]:
            report.add(f"run.{key}", "prior-record", f"`{run.get(key)}` differs from the prior record's `{prior[key]}`; a "
                       "re-review after fixes keeps its base")
    if run.get("prior_head") is not None and run["prior_head"] != prior["head"]:
        report.add("run.prior_head", "prior-record", f"a delta review from the prior record starts at its head `{prior['head']}`")
    elif run.get("prior_head") is not None and prior["coverage"] != "complete":
        report.add("run.prior_head", "prior-record", "the prior record's coverage is incomplete, so this run reviews the full "
                   "diff, not the delta")

    rendered = {item["id"]: item for item in items if item["type"] in ("finding", "question")}
    classified: dict[str, dict[str, Any]] = {}
    for location, item in priors:
        classified[item["id"]] = item
        earlier = prior["items"].get(item["id"])
        if earlier is None:
            report.add(location, "prior-record", f"`{item['id']}` is not an open item of the prior record")
            continue
        if item["action"] != earlier["action"]:
            report.add(location, "prior-record", f"`{item['id']}` was `{earlier['action']}` in the prior record, not `{item['action']}`")
        if item["classification"] in OPEN_CLASSIFICATIONS:
            again = rendered.get(item["id"])
            if again is None or again["type"] != earlier["type"]:
                report.add(location, "prior-record", f"open prior {earlier['type']} `{item['id']}` is {item['classification']}, so this "
                           "record renders it again under its id; the record is complete without the prior")
            elif earlier["action"] == "must-fix" and again.get("action") != "must-fix":
                report.add(location, "prior-record", f"open prior must-fix `{item['id']}` stays `must-fix` until a classification "
                           "settles it")
    for identity in prior["items"]:
        if identity not in classified:
            report.add("prior_items", "prior-record", f"the prior record's open item `{identity}` is unclassified; classify "
                       "every open prior finding and question")

    settled = {task["id"] for task in tasks if task.get("ruling") not in ("pending", "withheld") and "confirmed_in" not in task}
    kept = {task_id(entry) for entry in outstanding}
    for entry in prior["outstanding"]:
        if task_id(entry) not in kept and task_id(entry) not in settled:
            report.add("record.verification.outstanding", "prior-record", f"drops `{entry}`; outstanding work survives until a "
                       "task in this run settles it")
    routed = record.get("routed") if isinstance(record, dict) and isinstance(record.get("routed"), dict) else {}
    for key, entries in prior["routed"].items():
        current = routed.get(key) if isinstance(routed.get(key), list) else []
        for entry in entries:
            if entry not in current and task_id(entry) not in settled:
                report.add(f"record.routed.{key}", "prior-record", f"drops `{entry}`; routed items survive until a task in this "
                           "run settles them")


def read_verification(
    report: Report, verification: Any, coverage: Any, findings: list[dict[str, Any]], questions: list[dict[str, Any]],
    prior: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Check verification tasks, batches, allowance, and outstanding work for contradictions; see the docstring."""
    where = "record.verification"
    rendered = rendered_ids(findings, questions)
    if not isinstance(verification, dict):
        report.add(where, "schema", "`verification` must be an object with `tasks`, `batches`, `allowance`, and `outstanding`")
        verification = {}
    outstanding = read_lines(report, f"{where}.outstanding", verification.get("outstanding", []))
    if outstanding and coverage != "incomplete":
        report.add(f"{where}.outstanding", "coverage-gaps", "outstanding verification contradicts `run.coverage=complete`; required work that did not finish never establishes safety")

    batches = read_rows(report, f"{where}.batches", verification.get("batches", []), ("name", "phase", "bundle", "raw_return", "accounting", "operation"))
    names: dict[str, str] = {}
    phases: set[str] = set()
    for location, batch in batches:
        for key in ("bundle", "raw_return", "accounting"):
            if not batch[key].startswith("/"):
                report.add(f"{location}.{key}", "record-paths", "must be an absolute path")
        if batch["phase"] not in PHASES:
            report.add(location, "verification", f"`phase` must be one of {list(PHASES)}")
        elif batch["phase"] in phases:
            report.add(location, "verification", f"a second `{batch['phase']}` batch; the allowance is one initial plus one follow-up batch")
        if batch["name"] in names:
            report.add(location, "verification", f"batch `{batch['name']}` is recorded twice")
        names[batch["name"]] = batch["accounting"]
        phases.add(batch["phase"])
    if len(batches) > BATCH_CAP:
        report.add(f"{where}.batches", "verification", "the cap is one initial plus one follow-up batch; a worker change grants no further batch")

    allowance = verification.get("allowance")
    if not isinstance(allowance, dict) or not all(isinstance(allowance.get(k), bool) for k in ("initial_spent", "follow_up_spent")):
        report.add(f"{where}.allowance", "schema", "`allowance` must be an object with boolean `initial_spent` and `follow_up_spent`")
        allowance = {"initial_spent": None, "follow_up_spent": None}
    if "carried_from" in allowance:
        report.add(f"{where}.allowance.carried_from", "verification", "`carried_from` is retired; a prior_record run carries its prior's spent flags")

    tasks = read_rows(report, f"{where}.tasks", verification.get("tasks", []), ("id", "type", "ruling"))
    rendered_findings = {finding["id"] for finding in findings}
    by_id: dict[str, dict[str, Any]] = {}
    for location, task in tasks:
        identity = task["id"]
        if identity in by_id:
            report.add(location, "stable-id", f"task `{identity}` is listed twice; a task id names one task")
        by_id[identity] = task
        if task["type"] == "candidate":
            if task.get("trigger") not in TRIGGERS:
                report.add(location, "verification", f"a candidate task's `trigger` must be one of {list(TRIGGERS)}")
            if task["ruling"] not in CANDIDATE_RULINGS:
                report.add(location, "verification", f"a candidate task's `ruling` must be one of {list(CANDIDATE_RULINGS)}")
            if (task["ruling"] == "unresolved" and task.get("trigger") != "optional"
                    and identity not in {q["id"] for q in questions} and not names_task(outstanding, identity)):
                report.add(location, "verification", f"required candidate `{identity}` is unresolved, so it renders as a question with its id or stays in `outstanding`")
        elif task["type"] == "safety-premise":
            if task.get("area") not in PREMISE_AREAS:
                report.add(location, "verification", f"a safety-premise task's `area` must be one of {list(PREMISE_AREAS)}")
            for key in ("premise", "evidence"):
                read_line(report, location, task, key)
            if task["ruling"] not in PREMISE_RULINGS:
                report.add(location, "verification", f"a safety-premise task's `ruling` must be one of {list(PREMISE_RULINGS)}")
            if task.get("trigger", "optional") != "optional":
                report.add(location, "verification", "a safety-premise task carries `trigger` only as `optional`, for a premise added as optional scrutiny")
            reopened = task.get("reopened_as")
            if reopened is not None and not (isinstance(reopened, str) and reopened.strip() and "\n" not in reopened):
                report.add(location, "schema", "`reopened_as` must be a one-line item id when present")
                reopened = None
            if task["ruling"] == "fails" and not (reopened in rendered or (reopened and names_task(outstanding, reopened))):
                report.add(location, "verification", f"premise `{identity}` fails, so `reopened_as` names the candidate it reopened as a rendered item or an `outstanding` entry")
            if (task["ruling"] == "unresolved" and task.get("trigger") != "optional"
                    and reopened not in {q["id"] for q in questions} and not names_task(outstanding, identity)):
                report.add(location, "verification", f"premise `{identity}` is unresolved, so it names a rendered question in `reopened_as` or stays in `outstanding`")
        else:
            report.add(location, "verification", "`type` must be `candidate` or `safety-premise`")
            continue
        batch = task.get("batch")
        accounting, why = None, ""
        if "confirmed_in" in task:
            check_carried(report, location, task, prior, rendered_findings)
            continue
        if isinstance(batch, str) and batch.startswith("carried:"):
            report.add(location, "verification", "`carried:` batch references are retired; a carried confirmation names its record in `confirmed_in` and its batch in `batch`")
            continue
        if task["ruling"] == "pending" and batch is None:
            pass
        elif batch not in names:
            report.add(location, "verification", f"task `{identity}` names batch {json.dumps(batch)}, which is not recorded; only a `pending` task has none")
        else:
            accounting = names[batch]
        if task["ruling"] in ("pending", "withheld"):
            why = ""  # claims no verifier result, so a batch that produced no report still records it
        elif accounting is not None:
            established, why = accounted_ruling(accounting, "candidates" if task["type"] == "candidate" else "premises", identity)
            if established is not None and established != task["ruling"]:
                why = f"accounting report `{accounting}` establishes `{established}`, not `{task['ruling']}`"
        if why:
            report.add(location, "verification", f"task `{identity}`: {why}; a ruling stands only on the verifier result that accounted for it")
        if task["ruling"] in ("withheld", "pending") and task.get("trigger") != "optional" and not names_task(outstanding, identity):
            report.add(location, "verification", f"`{identity}` is {task['ruling']} required work, so `outstanding` names it")

    for finding in findings:
        mandatory = "must-fix" if finding["action"] == "must-fix" else finding["kind"] if finding["kind"] in MANDATORY_KINDS else None
        task = by_id.get(finding["id"], {})
        if mandatory is not None and not (task.get("type") == "candidate" and task.get("trigger") not in (None, "optional")
                                          and task.get("ruling") == "confirmed"):
            report.add(f"{where}.tasks", "verification", f"rendered finding `{finding['id']}` is {mandatory}, which requires a candidate task with its id, a mandatory `trigger`, and `ruling: confirmed`; a candidate still needing mandatory confirmation stays unpublished")

    carried = prior["allowance"] if prior is not None else {"initial_spent": False, "follow_up_spent": False}
    spent = {"initial": allowance["initial_spent"], "follow-up": allowance["follow_up_spent"]}
    flag = {"initial": "initial_spent", "follow-up": "follow_up_spent"}
    for phase in PHASES:
        if phase in phases and carried[flag[phase]]:
            report.add(f"{where}.batches", "verification", f"the prior record already spent its {phase} batch; a run from a "
                       "prior record spends only what the prior left, and a worker change grants no further batch")
        if spent[phase] is False and (phase in phases or carried[flag[phase]]):
            report.add(f"{where}.allowance.{flag[phase]}", "verification",
                       f"`{flag[phase]}` is false while a `{phase}` batch is recorded" if phase in phases else
                       f"`{flag[phase]}` is false, but the prior record spent it; spent allowance never falls below the prior's")
        if spent[phase] is True and phase not in phases and not carried[flag[phase]]:
            report.add(f"{where}.allowance.{flag[phase]}", "verification",
                       f"`{flag[phase]}` is true with no `{phase}` batch recorded here or spent by a prior record")
    if "follow-up" in phases and not ("initial" in phases or carried["initial_spent"]):
        report.add(f"{where}.batches", "verification", "a follow-up batch needs the initial batch spent first")
    return {"tasks": [t for _w, t in tasks], "batches": [b for _w, b in batches],
            "allowance": {"initial_spent": spent["initial"], "follow_up_spent": spent["follow-up"]},
            "outstanding": outstanding}


def rendered_ids(findings: list[dict[str, Any]], questions: list[dict[str, Any]]) -> set[str]:
    return {item["id"] for item in findings + questions}


def read_record(
    report: Report,
    record: Any,
    run: dict[str, Any],
    findings: list[dict[str, Any]],
    questions: list[dict[str, Any]],
    priors: list[dict[str, Any]],
    store: dict[str, Any] | None,
    prior: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Check the private record's accounting for contradictions with the rendered items and run; see the docstring."""
    if not isinstance(record, dict):
        report.add("record", "schema", "`record` must be an object")
        return {}
    fields: dict[str, Any] = {"repository": read_line(report, "record", record, "repository")}
    coverage = run.get("coverage")

    paths = record.get("paths")
    if not isinstance(paths, dict):
        report.add("record.paths", "schema", "`paths` must be an object of absolute paths")
        paths = {}
    for key in RECORD_PATHS:
        if key not in paths:
            report.add("record.paths", "record-paths", f"`{key}` is required so a later reader can find the retained state")
    for key, value in paths.items():
        if not isinstance(value, str) or not value.startswith("/"):
            report.add(f"record.paths.{key}", "record-paths", "must be an absolute path")
    fields["paths"] = paths

    requirements = read_rows(report, "record.requirements", record.get("requirements"), ("source", "class", "disposition", "evidence"))
    for where, row in requirements:
        if row["class"] not in REQUIREMENT_CLASSES:
            report.add(where, "requirements", f"`class` must be one of {list(REQUIREMENT_CLASSES)}")
        if row["disposition"] not in REQUIREMENT_DISPOSITIONS:
            report.add(where, "requirements", f"`disposition` must be one of {list(REQUIREMENT_DISPOSITIONS)}")
    fields["requirements"] = [r for _w, r in requirements]
    rendered = rendered_ids(findings, questions)

    files = read_rows(report, "record.files", record.get("files"), ("path", "state"))
    states: dict[str, str] = {}
    for where, row in files:
        if row["state"] not in FILE_STATES:
            report.add(where, "file-accounting", f"`state` must be one of {list(FILE_STATES)}")
        if row["state"] == "ignored":
            read_line(report, where, row, "reason")
        if row["path"] in states:
            report.add(where, "file-accounting", f"`{row['path']}` is accounted for twice")
        states[row["path"]] = row["state"]
    if "unreviewed" in states.values() and coverage != "incomplete":
        report.add("record.files", "coverage-gaps", "an `unreviewed` file contradicts `run.coverage=complete`")
    if store is not None and isinstance(store.get("context"), dict) and isinstance(store["context"].get("manifest"), list):
        manifest = {e["path"] for e in store["context"]["manifest"] if isinstance(e, dict) and isinstance(e.get("path"), str)}
        for path in sorted(manifest - states.keys()):
            report.add("record.files", "file-accounting", f"`{path}` is in the pinned merge-base manifest and has no accounting row")
        for path in sorted(states.keys() - manifest):
            report.add("record.files", "file-accounting", f"`{path}` is not in the pinned merge-base manifest; accounting covers changed files")
    fields["files"] = [r for _w, r in files]

    evidence = read_rows(report, "record.check_evidence", record.get("check_evidence", []), ("check", "head", "outcome"))
    for where, row in evidence:
        if row["outcome"] not in EVIDENCE_OUTCOMES:
            report.add(where, "check-evidence", f"`outcome` must be one of {list(EVIDENCE_OUTCOMES)}")
        elif not COMMIT_SHA_RE.match(row["head"]):
            report.add(where, "trailer-sha", "`head` must be exactly 40 lowercase hexadecimal characters")
        elif row["outcome"] == "historical":
            if row["head"] == run.get("head"):
                report.add(where, "check-evidence", "historical evidence is attributed to its original head, not the reviewed head; evidence for the reviewed state is `accepted` or `reviewer-executed`")
            read_line(report, where, row, "reason")
        else:
            if row["head"] != run.get("head"):
                report.add(where, "check-evidence", f"`{row['outcome']}` evidence is attributed to the reviewed head; a result from another head is `historical` and is never relabelled")
            if row["outcome"] == "reviewer-executed":
                read_line(report, where, row, "reason")
    fields["check_evidence"] = [r for _w, r in evidence]

    fields["verification"] = read_verification(report, record.get("verification"), coverage, findings, questions, prior)

    routed = record.get("routed", {})
    if not isinstance(routed, dict):
        report.add("record.routed", "schema", "`routed` must be an object")
        routed = {}
    known = set(rendered) | {p["id"] for p in priors}
    for key in ("unresolved", "disputed"):
        for identity in read_lines(report, f"record.routed.{key}", routed.get(key, [])):
            if identity not in known:
                report.add(f"record.routed.{key}", "stable-id", f"`{identity}` is not a rendered or prior item id")
    unrecoverable = read_lines(report, "record.routed.unrecoverable_inputs", routed.get("unrecoverable_inputs", []))
    if unrecoverable and coverage != "incomplete":
        report.add("record.routed.unrecoverable_inputs", "coverage-gaps", "an unrecoverable input contradicts `run.coverage=complete`; it derives provisional `Incomplete`")
    fields["routed"] = {key: routed.get(key, []) for key in ("unresolved", "disputed", "unrecoverable_inputs")}
    return fields


def compose(composition: Any, store: dict[str, Any] | None = None,
            prior: dict[str, Any] | None = None) -> tuple[dict[str, Any] | None, list[str]]:
    """Return ``(payload, violations)``: the validated payload, or ``None`` unless the composition validated with zero
    violations."""
    payload, _fields, violations = compose_record(composition, store, prior)
    return payload, violations


def compose_record(composition: Any, store: dict[str, Any] | None = None, prior: dict[str, Any] | None = None
                   ) -> tuple[dict[str, Any] | None, dict[str, Any], list[str]]:
    """Return ``(payload, fields, violations)``; ``fields`` holds the checked run, status and ``record`` accounting the
    finalizer writes into ``record.json``. ``prior`` is the state ``load_prior`` read for a ``prior_record`` run."""
    report = Report()
    if not isinstance(composition, dict):
        report.add("input", "schema", "the composition input must be a JSON object")
        return None, {}, report.lines
    run = read_run(report, composition.get("run"))
    summary = read_summary(report, composition.get("summary"), run["coverage"] if run else None)
    head = run["head"] if run and isinstance(run["head"], str) else "0" * 40

    def read_list(key: str) -> list[Any]:
        value = composition.get(key, [])
        if not isinstance(value, list):
            report.add(key, "schema", f"`{key}` must be a list")
            return []
        return value

    findings: list[tuple[str, dict[str, Any], str]] = []
    for index, raw in enumerate(read_list("findings")):
        item = compose_finding(report, f"findings[{index}]", raw, head)
        if item is not None:
            findings.append((f"findings[{index}]", item, raw["title"]))
    questions: list[tuple[str, dict[str, Any], str]] = []
    for index, raw in enumerate(read_list("questions")):
        item = compose_question(report, f"questions[{index}]", raw, head)
        if item is not None:
            questions.append((f"questions[{index}]", item, raw["title"]))
    observations: list[tuple[str, dict[str, Any]]] = []
    raw_observations = read_list("observations")
    if len(raw_observations) > MAX_OBSERVATIONS:
        report.add(
            "observations",
            "observation-cap",
            f"{len(raw_observations)} observations exceed the cap of {MAX_OBSERVATIONS}; the reviewer publishes the three with the most "
            "decisive evidence and records each of the rest as `observation (unpublished, cap)` — the composer never selects or drops one",
        )
    for index, raw in enumerate(raw_observations):
        item = compose_observation(report, f"observations[{index}]", raw)
        if item is not None:
            observations.append((f"observations[{index}]", item))
    priors: list[tuple[str, dict[str, Any]]] = []
    for index, raw in enumerate(read_list("prior_items")):
        prior_item = read_prior_item(report, f"prior_items[{index}]", raw)
        if prior_item is not None:
            priors.append((f"prior_items[{index}]", prior_item))
    if run is not None and run["target_kind"] in LOCAL and prior is None and priors:
        report.add("prior_items", "prior-record", "a local target carries prior state only from a prior record")

    check_identities(report, [(l, f) for l, f, _t in findings], [(l, q) for l, q, _t in questions], priors,
                     carried=prior is not None)
    if store is None:
        require_file_sides(report, [(l, i) for l, i, _t in findings + questions])
    elif run is not None:
        check_store(report, store, run, [(l, i) for l, i, _t in findings + questions])
    if run is not None and summary is not None:
        check_status(report, summary["status"], run["coverage"], [f for _l, f, _t in findings], [q for _l, q, _t in questions], [p for _l, p in priors])
    record = None
    if run is not None and "record" in composition:
        record = read_record(report, composition["record"], run, [f for _l, f, _t in findings], [q for _l, q, _t in questions],
                             [p for _l, p in priors], store, prior)
    if prior is not None and run is not None:
        verification = (record or {}).get("verification") or {}
        check_prior(report, prior, run, composition.get("record"), [i for _l, i, _t in findings + questions], priors,
                    verification.get("tasks", []), verification.get("outstanding", []))
    if report.lines or run is None or summary is None:
        return None, {}, report.lines

    trailer = (
        f"<!-- review-run head={run['head']} base-ref={run['base_ref']} base-sha={run['base_sha']} "
        f"merge-base={run['merge_base']} workflow={WORKFLOW} packet_context={run['packet_context']} "
        f"supplied_inputs={run['supplied_inputs']} issues={run['issues']} coverage={run['coverage']} -->"
    )
    body = compose_body(report, run, summary, findings, questions, [o for _l, o in observations], [p for _l, p in priors], trailer)
    if report.lines:
        return None, {}, report.lines
    payload: dict[str, Any] = {"summary": {"body": body, "trailer": trailer}, "items": []}
    if run["repository_url"] is not None:
        payload["summary"]["repository_url"] = run["repository_url"]
    locations: list[str] = []
    for location, item, _title in findings + questions:
        payload["items"].append(item)
        locations.append(location)
    for location, item in observations:
        payload["items"].append(item)
        locations.append(location)
    violations = [translate(line, locations) for line in validate(payload)]
    if violations:
        return None, {}, violations
    return payload, {"run": run, "status": summary["status"], "record": record,
                     "prior_items": [p for _l, p in priors]}, []


def example_composition() -> dict[str, Any]:
    """What the reviewer writes for a pull request; the finalizer fills the rest, and ``--example`` prints it.

    The finalizer fills run identity from the store and packet, ``supplied_inputs`` from ``specs``, the record's own
    paths, the spent allowance, and each batch's name, phase and raw return from its bundle and accounting report, so
    the example omits them. Every judgment field is shown, with a prior item's drafted thread reply.
    """
    head = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
    finding = {
        "id": "payments/retry-idempotency", "title": "Preserve the idempotency key across retries",
        "priority": "P1", "action": "must-fix", "kind": "requirement",
        "trigger": "The server commits a charge but its response times out and the client retries.",
        "impact": "The retry uses a new idempotency key and can submit a second charge.",
        "change": "In `src/retry-policy.ts`, reuse one idempotency key across every attempt for the same logical charge.",
        "source": "Issue #123, acceptance criterion 2.",
        "anchor": {"type": "line", "path": "src/payments.ts", "start_line": 42, "end_line": 42, "side": "RIGHT"},
        "fix": {"path": "src/retry-policy.ts", "start_line": 18},
    }
    composition: dict[str, Any] = {
        "run": {"coverage": "complete", "specs": []},
        "summary": {"status": "Changes Requested",
                    "intent": "Add retries for charge submission without changing payment semantics.",
                    "issue_fit": "Partial — retry availability is implemented, but acceptance criterion 2's idempotency guarantee remains open.",
                    "coverage": "Complete merge-base diff reviewed; payment callers inspected; focused `retry-policy` test run once at the head: pass."},
        "findings": [finding],
        "questions": [{"id": "queue/retry-order", "title": "Must retries preserve request order?",
                       "evidence": "The new queue retries at the tail, while existing callers consume it as FIFO. The issue, tests, and history do not establish whether reordering is allowed.",
                       "why_it_matters": "The answer determines whether this is a merge-blocking regression.",
                       "answer": "Confirm whether retry order is part of the contract; the maintainer answer settles whether the candidate should re-open as a finding.",
                       "anchor": {"type": "file", "path": "src/queue.ts", "side": "RIGHT"}}],
        "observations": [{"fact": "The first configuration sentence covers same-shard re-points more broadly than the implementation does.",
                          "evidence": "`redis.conf:1903`, `src/replication.c:2701`."}],
    }
    private = "/tmp/review-code-XXXXXX"
    composition["prior_items"] = [{"id": "queue/drop-on-full", "classification": "fixed", "action": "must-fix",
                                   "note": "The queue now blocks when full.", "reply": "Fixed: a full queue now blocks instead of dropping the charge.",
                                   "thread_id": "PRRT_kwDOABCD12", "comment_id": 1001}]
    composition["record"] = {
        "repository": "acme/payments",
        "requirements": [{"source": "issue-123/acceptance-criterion-2", "class": "acceptance", "disposition": "partial",
                          "evidence": "src/payments.ts:42 creates a key per attempt"}],
        "files": [{"path": "src/payments.ts", "state": "reviewed"}, {"path": "src/retry-policy.ts", "state": "reviewed"},
                  {"path": "src/queue.ts", "state": "reviewed"}, {"path": "docs/notes.md", "state": "ignored", "reason": "generated changelog"}],
        "check_evidence": [{"check": "pnpm test payments", "head": head, "outcome": "accepted",
                            "reason": "same command, clean tree at the reviewed head, full output read"}],
        "verification": {
            "tasks": [{"id": "payments/retry-idempotency", "type": "candidate", "trigger": "must-fix", "batch": "initial", "ruling": "confirmed"},
                      {"id": "premise-1", "type": "safety-premise", "area": "data-integrity",
                       "premise": "The charge lookup always succeeds before `submitCharge()` records the charge.",
                       "evidence": "src/charges.ts:31", "batch": "initial", "ruling": "holds"}],
            "batches": [{"bundle": f"{private}/initial", "accounting": f"{private}/initial/accounting.json",
                         "operation": "Agent run_in_background=false"}],
            "outstanding": []},
        "routed": {"unresolved": ["queue/retry-order"], "disputed": [], "unrecoverable_inputs": []},
    }
    return composition



# --- finalize -------------------------------------------------------------------------------------------------------

SKILL_ROOT = Path(__file__).resolve().parent.parent
REPORT = "report.md"
OUTPUTS = ("record.json", "payload.json", "batch.json")
# Leftovers of the retired profiles, removed with the other stale output so none reads as this run's.
RETIRED_OUTPUTS = ("fragments.md",)
RECORD_SECTIONS = ("repository", "paths", "requirements", "files", "check_evidence", "verification", "routed")
VERIFICATION_SECTIONS = ("tasks", "batches", "outstanding")
ROUTED_SECTIONS = ("unresolved", "disputed", "unrecoverable_inputs")
TRAILED = ("fixed", "accepted", "obsolete", "still-open")
# Where the finalizer fills a key, the keys take the order compositions have always written them in, so a derived
# record serializes as a transcribed one did; a fully written object keeps its own order.
PATH_ORDER = ("private_dir", "store", "composition", "skill_root")
BATCH_ORDER = ("name", "phase", "bundle", "raw_return", "accounting", "operation")


class Stop(Exception):
    """A stage or write failed; its output is already printed."""

    def __init__(self, status: int) -> None:
        super().__init__(status)
        self.status = status


def fail(stage: str, status: int, output: str) -> Stop:
    sys.stdout.write(f"{stage} failed with exit {status}; later stages did not run:\n{output}")
    sys.stdout.flush()
    return Stop(status)


def read_json(path: Path, what: str, stage: str = "derive") -> Any:
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as error:
        raise fail(stage, 2, f"render_review: cannot read {what} {path}: {error}\n")


def same_set(explicit: Any, owned: list[str]) -> bool:
    return isinstance(explicit, list) and all(isinstance(v, str) for v in explicit) and sorted(explicit) == sorted(owned)


def same_lineage(explicit: Any, owned: list[str]) -> bool:
    return (isinstance(explicit, list) and len(explicit) == len(owned)
            and all(same_path(a, b) for a, b in zip(explicit, owned)))


def settle(report: Report, holder: dict[str, Any], key: str, owned: Any, where: str, source: str, same: Any = None) -> None:
    """Fill an omitted mechanical field from the input that owns it; refuse an explicit copy that disagrees."""
    if owned is None:
        if key not in holder:
            report.add(where, "derived-field", f"`{key}` is omitted and {source} does not establish it")
    elif key not in holder:
        holder[key] = owned
    elif not (same(holder[key], owned) if same else holder[key] == owned):
        report.add(where, "derived-field", f"`{key}={json.dumps(holder[key], ensure_ascii=False)}` conflicts with "
                   f"{json.dumps(owned, ensure_ascii=False)} from {source}; omit it and the finalizer supplies it")


def ordered(value: dict[str, Any], written: set[str], order: tuple[str, ...]) -> dict[str, Any]:
    if set(value) == written:
        return value
    return {**{key: value[key] for key in order if key in value}, **{k: v for k, v in value.items() if k not in order}}


def text_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def derive_packet(report: Report, run: dict[str, Any], packet: dict[str, Any], context: dict[str, Any]) -> None:
    pr = packet.get("pr")
    if not isinstance(pr, dict):
        report.add("packet", "schema", "the packet carries no `pr` section; normalize the saved pages with forge_packet.py")
        return
    settle(report, run, "target_kind", "pull-request", "run", "the packet")
    pinned = text_or_none(pr.get("head_sha"))
    if pinned is not None and isinstance(context.get("head"), str) and pinned != context["head"]:
        report.add("run.head", "derived-field", f"the packet pins head `{pinned}`, but the store was built for `{context['head']}`")
    settle(report, run, "base_ref", text_or_none(pr.get("base_ref")), "run", "the packet")
    settle(report, run, "base_sha", text_or_none(pr.get("base_sha")), "run", "the packet")
    settle(report, run, "merged", pr.get("merged") if isinstance(pr.get("merged"), bool) else None, "run", "the packet")
    settle(report, run, "repository_url", text_or_none(packet.get("repository_url")), "run", "the packet")
    fingerprint = packet.get("fingerprint")
    issues = fingerprint.get("issues") if isinstance(fingerprint, dict) else None
    coordinates = [issue.get("coordinate") for issue in issues if isinstance(issue, dict)] if isinstance(issues, list) else []
    coordinates = coordinates if isinstance(issues, list) and all(isinstance(c, str) for c in coordinates) else None
    settle(report, run, "issues", coordinates, "run", "the packet's linked issues", same_set)
    try:
        digest = fp.packet_context(packet)
    except fp.PageError as error:
        report.add("packet", "schema", str(error))
        return
    settle(report, run, "packet_context", digest, "run", "the packet's intent, as forge_packet.py hashes it")


def derive_batch(report: Report, where: str, batch: dict[str, Any]) -> None:
    """A batch's identity from its bundle manifest and its raw return from the accounting report reconciled."""
    bundle, accounting = batch.get("bundle"), batch.get("accounting")
    manifest_bytes, manifest, identity = None, {}, {}
    if isinstance(bundle, str):
        try:
            manifest_bytes = (Path(bundle) / "manifest.json").read_bytes()
            manifest = json.loads(manifest_bytes)
            manifest = manifest if isinstance(manifest, dict) else {}
            identity = manifest["batch"] if isinstance(manifest.get("batch"), dict) else {}
        except (OSError, ValueError):
            manifest_bytes, manifest = None, {}
    source = f"bundle manifest `{bundle}/manifest.json`"
    settle(report, batch, "name", text_or_none(identity.get("id")), where, source)
    settle(report, batch, "phase", text_or_none(identity.get("phase")), where, source)
    reconciled: Any = {}
    if isinstance(accounting, str):
        reconciled, _why = load_object(accounting)
        reconciled = reconciled or {}
    settle(report, batch, "raw_return", text_or_none(reconciled.get("raw_return")), where, f"accounting report `{accounting}`", same_path)
    if manifest_bytes is None or not reconciled:
        return
    formats = (manifest.get("format"), reconciled.get("format"))
    if formats != (MANIFEST_FORMAT, ACCOUNTING_FORMAT):
        report.add(where, "derived-field", f"bundle `{bundle}` and accounting report `{accounting}` are {json.dumps(formats[0])} and "
                   f"{json.dumps(formats[1])}, not `{MANIFEST_FORMAT}` and `{ACCOUNTING_FORMAT}`; rebuild and reaccount the batch")
    elif (reconciled.get("bundle_id") != manifest.get("bundle_id")
          or reconciled.get("manifest_sha256") != hashlib.sha256(manifest_bytes).hexdigest()):
        report.add(where, "derived-field", f"accounting report `{accounting}` accounts a return to another manifest than `{bundle}/manifest.json`")


def derive_run(report: Report, run: dict[str, Any], packet: Any, store: Any) -> None:
    """Run identity from the store and packet, and the supplied-inputs marker from the caller's specs."""
    context = store.get("context") if isinstance(store, dict) and isinstance(store.get("context"), dict) else {}
    settle(report, run, "head", text_or_none(context.get("head")), "run", "the store")
    settle(report, run, "merge_base", text_or_none(context.get("merge_base")), "run", "the store")
    snapshot = context.get("snapshot") if isinstance(context.get("snapshot"), dict) else None
    if snapshot is not None:
        settle(report, run, "target_kind", "worktree", "run", "the store's working-tree snapshot")
    if run.get("target_kind") == "worktree":
        settle(report, run, "tree", text_or_none((snapshot or {}).get("tree")), "run", "the store's snapshot")
    if isinstance(packet, dict) and packet.get("schema") == fp.SCHEMA:
        derive_packet(report, run, packet, context)
    if run.get("target_kind") in LOCAL:
        settle(report, run, "merged", False, "run", "a local target")
    specs = run.get("specs", [])
    if isinstance(specs, list):
        settle(report, run, "supplied_inputs", "yes" if specs else "no", "run", "`run.specs`")


def derive(args: argparse.Namespace, private: Path, composition: Any, packet: Any, store: Any,
           prior: dict[str, Any] | None) -> tuple[Any, list[str]]:
    """The composition with omitted mechanical fields filled from the inputs that own them, and every conflict."""
    report = Report()
    if not isinstance(composition, dict):
        return composition, []  # the accounting check names the malformed input
    composition = copy.deepcopy(composition)
    if isinstance(composition.get("run"), dict):
        derive_run(report, composition["run"], packet, store)
    record = composition.get("record")
    if not isinstance(record, dict):
        return composition, report.lines
    paths = record.setdefault("paths", {})
    if isinstance(paths, dict):
        written = set(paths)
        owned = {"private_dir": str(private), "store": os.path.abspath(args.store),
                 "composition": str(private / "composition.json"), "skill_root": str(SKILL_ROOT)}
        for key, value in owned.items():
            settle(report, paths, key, value, "record.paths", "this finalizer run", same_path)
        record["paths"] = ordered(paths, written, PATH_ORDER)
    lineage = [*prior["lineage"], prior["path"]] if prior is not None else []
    settle(report, record, "lineage", lineage, "record", "the prior record's lineage and the prior record itself", same_lineage)
    verification = record.get("verification")
    batches = verification.get("batches") if isinstance(verification, dict) else None
    for index, batch in enumerate(batches if isinstance(batches, list) else []):
        if isinstance(batch, dict):
            written = set(batch)
            derive_batch(report, f"record.verification.batches[{index}]", batch)
            batches[index] = ordered(batch, written, BATCH_ORDER)
    if isinstance(verification, dict) and isinstance(batches, list):
        phases = {batch.get("phase") for batch in batches if isinstance(batch, dict)}
        carried = prior["allowance"] if prior is not None else {"initial_spent": False, "follow_up_spent": False}
        spent = {"initial_spent": carried["initial_spent"] or "initial" in phases,
                 "follow_up_spent": carried["follow_up_spent"] or "follow-up" in phases}
        source = "this record's batches and the prior record's spent flags" if prior is not None else "this record's batches"
        settle(report, verification, "allowance", spent, "record.verification", source)
    return composition, report.lines


# --- accounting ---------------------------------------------------------------


def packet_threads(packet: Any, report: Report) -> dict[str, int | None]:
    """Each packet thread's node id and its first comment's numeric id."""
    if not isinstance(packet, dict) or packet.get("schema") != fp.SCHEMA or not isinstance(packet.get("threads"), list):
        report.add("packet", "schema", f"expected a `{fp.SCHEMA}` packet from forge_packet.py normalize")
        return {}
    threads: dict[str, int | None] = {}
    for thread in packet["threads"]:
        if isinstance(thread, dict) and isinstance(thread.get("id"), str):
            comments = thread.get("comments")
            first = comments[0].get("id") if isinstance(comments, list) and comments and isinstance(comments[0], dict) else None
            threads[thread["id"]] = int(first) if isinstance(first, str) and first.isdigit() else None
    return threads


def check_replies(report: Report, priors: Any, packet: Any) -> None:
    if not isinstance(priors, list):
        return  # the composer names a malformed list
    threads = None if packet is None else packet_threads(packet, report)
    for index, prior in enumerate(priors):
        where = f"prior_items[{index}]"
        if not isinstance(prior, dict):
            continue
        reply, thread, comment = prior.get("reply"), prior.get("thread_id"), prior.get("comment_id")
        if reply is not None and not (isinstance(reply, str) and reply.strip()):
            report.add(where, "prior-reply", "`reply` is the drafted reply prose, or null for none")
            reply = None
        if isinstance(reply, str) and "<!-- prior-item" in reply:
            report.add(where, "prior-reply", "`reply` carries a prior-item trailer; the finalizer appends it where required")
        if prior.get("classification") == "disputed" and reply is not None:
            report.add(where, "prior-reply", "a disputed item is not reposted, so it drafts no `reply`")
        if thread is None and comment is None:
            if reply is not None:
                report.add(where, "prior-reply", "a drafted `reply` needs the packet's `thread_id` and `comment_id` for its existing thread")
            continue
        if not (isinstance(thread, str) and thread) or not (isinstance(comment, int) and not isinstance(comment, bool)):
            report.add(where, "prior-reply", "`thread_id` (node id) and `comment_id` (integer) are both set, or both null for an item without a forge thread")
        elif threads is None:
            report.add(where, "prior-reply", "thread ids are checked against the forge packet; pass `--packet`")
        elif thread not in threads:
            report.add(where, "prior-reply", f"`thread_id={thread}` names no thread in the packet")
        elif threads[thread] != comment:
            report.add(where, "prior-reply", f"`comment_id={comment}` is not the first comment of thread `{thread}` in the packet ({threads[thread]})")


def check_accounting(composition: Any, packet: Any) -> list[str]:
    """Presence of every accounting section, never defaulted, and packet-bound reply ids; the composer checks content."""
    report = Report()
    if not isinstance(composition, dict):
        report.add("input", "schema", "the composition input must be a JSON object")
        return report.lines
    record = composition.get("record")
    if not isinstance(record, dict):
        report.add("record", "accounting", "finalization requires the private `record` accounting; nothing is defaulted")
    else:
        for key in RECORD_SECTIONS:
            if key not in record:
                report.add("record", "accounting", f"`{key}` is required; write an empty list when there is none")
        for key, keys in (("verification", VERIFICATION_SECTIONS), ("routed", ROUTED_SECTIONS)):
            if isinstance(record.get(key), dict):
                for inner in keys:
                    if inner not in record[key]:
                        report.add(f"record.{key}", "accounting", f"`{inner}` is required; nothing is defaulted")
    check_replies(report, composition.get("prior_items", []), packet)
    return report.lines


def rendered_replies(composition: dict[str, Any]) -> list[dict[str, Any]]:
    """Each prior item's thread ids and drafted reply, with the prior-item trailer appended where required."""
    head = composition["run"]["head"]
    replies = []
    for prior in composition.get("prior_items", []):
        body = prior.get("reply")
        if body is not None and prior["classification"] in TRAILED:
            body = (f"{body.rstrip()}\n\n<!-- prior-item id={prior['id']} "
                    f"classification={prior['classification']} head={head} -->")
        replies.append({"id": prior["id"], "classification": prior["classification"],
                        "thread_id": prior.get("thread_id"), "comment_id": prior.get("comment_id"), "body": body})
    return replies


# --- report -------------------------------------------------------------------


def code(value: Any) -> str:
    text = str(value)
    ticks = "`" * (max((len(run) for run in re.findall(r"`+", text)), default=0) + 1)
    pad = " " if text.startswith("`") or text.endswith("`") else ""
    return f"{ticks}{pad}{text}{pad}{ticks}"


def fenced(text: str) -> str:
    ticks = "`" * max(3, max((len(run) for run in re.findall(r"`+", text)), default=0) + 1)
    return f"{ticks}markdown\n{text.rstrip(chr(10))}\n{ticks}"


def ids(values: list[str]) -> str:
    return ", ".join(code(value) for value in values) if values else "none"


def render_report(record_doc: dict[str, Any], composition: dict[str, Any], replies: list[dict[str, Any]],
                  outputs: list[tuple[str, Path]]) -> str:
    record, run_fields = composition["record"], composition["run"]
    parts = [f"# Review report\n\nStatus **{record_doc['status']}**; coverage `{run_fields['coverage']}`. `render_review.py` "
             "generated this report from the validated composition. The summary body below is the one the payload carries.",
             record_doc["summary"]["body"].rstrip("\n")]

    target = run_fields.get("target_kind", "pull-request")
    lines = [f"- Repository: {code(record['repository'])}", f"- Target: {target}"
             + (f" {code(run_fields['target'])}" if run_fields.get("target") else "")
             + (f", tree `{run_fields['tree']}`" if run_fields.get("tree") else ""),
             f"- Merged: {'yes' if run_fields.get('merged') else 'no'}"]
    if run_fields.get("prior_head"):
        lines.append(f"- Prior head: `{run_fields['prior_head']}`")
    if run_fields.get("specs"):
        lines.append(f"- Supplied issues or specs: {ids(run_fields['specs'])}")
    if record_doc["prior_record"]:
        lines.append(f"- Prior record: {code(record_doc['prior_record'])}")
    if record_doc["lineage"]:
        lines.append(f"- Lineage: {ids(record_doc['lineage'])}")
    parts.append("## Run\n\nHead, base, merge-base, workflow, packet identity, issues and coverage are in the run trailer "
                 "above.\n\n" + "\n".join(lines))

    inline = [item for item in record_doc["items"] if item["type"] != "observation" and item["anchor"].get("type") == "line"]
    if inline:
        parts.append("## Line comments\n\nThe full body of each line-anchored item the summary indexes.\n\n"
                     + "\n\n".join(f"### {code(item['id'])}\n\n{item['markdown']}\n\n{item['trailer']}" for item in inline))

    parts.extend(ledger_sections(record, record_doc["prior_record"]))

    if replies:
        entries = []
        for reply in replies:
            where = (f"Thread {code(reply['thread_id'])}, first comment `{reply['comment_id']}`." if reply["thread_id"]
                     else "No forge thread.")
            body = f"Drafted reply:\n\n{fenced(reply['body'])}" if reply["body"] is not None else "No drafted reply."
            entries.append(f"### {code(reply['id'])}: {reply['classification']}\n\n{where} {body}")
        parts.append("## Prior-item replies\n\n" + "\n\n".join(entries))

    paths = [f"- {name}: {code(path)}" for name, path in outputs]
    paths += [f"- {key}: {code(value)}" for key, value in record["paths"].items() if value not in {str(p) for _n, p in outputs}]
    parts.append("## Artifacts\n\n" + "\n".join(paths))
    return "\n\n".join(parts) + "\n"


def ledger_sections(record: dict[str, Any], prior_record: str | None) -> list[str]:
    """The requirement, file, check-evidence, verification and routed ledgers."""
    parts = []
    rows = [f"- {code(r['source'])} ({r['class']}): {r['disposition']}. {r['evidence']}" for r in record["requirements"]]
    parts.append("## Requirements\n\n" + ("\n".join(rows) or "None recorded."))
    rows = [f"- {code(f['path'])}: {f['state']}" + (f", {f['reason']}" if f.get("reason") else "") for f in record["files"]]
    parts.append("## File coverage\n\n" + ("\n".join(rows) or "No changed file."))
    rows = [f"- {code(e['check'])} at `{e['head']}`: {e['outcome']}" + (f", {e['reason']}" if e.get("reason") else "")
            for e in record["check_evidence"]]
    parts.append("## Check evidence\n\n" + ("\n".join(rows) or "None used."))

    verification = record["verification"]
    allowance = verification["allowance"]
    lines = [f"- Allowance: initial batch {'spent' if allowance['initial_spent'] else 'unspent'}, follow-up "
             f"{'spent' if allowance['follow_up_spent'] else 'unspent'}"
             + (f", counting what the prior record {code(prior_record)} spent." if prior_record else ".")]
    for batch in verification["batches"]:
        lines.append(f"- Batch {code(batch['name'])} ({batch['phase']}), {code(batch['operation'])}: bundle "
                     f"{code(batch['bundle'])}, raw return {code(batch['raw_return'])}, accounting {code(batch['accounting'])}.")
    for task in verification["tasks"]:
        batch = code(task["batch"]) if task.get("batch") else "none"
        if task.get("confirmed_in"):
            batch += f" of {code(task['confirmed_in'])}"
        if task["type"] == "candidate":
            lines.append(f"- Candidate {code(task['id'])}, trigger `{task['trigger']}`, batch {batch}: {task['ruling']}.")
        else:
            line = (f"- Safety premise {code(task['id'])}, area `{task['area']}`"
                    + (", optional" if task.get("trigger") == "optional" else "")
                    + f", batch {batch}: {task['ruling']}. {task['premise']} Evidence: {task['evidence']}")
            if task.get("reopened_as"):
                line += f" Reopened as {code(task['reopened_as'])}."
            lines.append(line)
    lines.extend(f"- Outstanding: {entry}" for entry in verification["outstanding"])
    parts.append("## Verification\n\n" + "\n".join(lines))

    routed = record["routed"]
    parts.append("## Routed\n\n" + "\n".join([f"- Unresolved: {ids(routed['unresolved'])}.",
                                                f"- Disputed: {ids(routed['disputed'])}."]
                                               + [f"- Unrecoverable input: {entry}" for entry in routed["unrecoverable_inputs"]]))
    return parts


# --- outputs ------------------------------------------------------------------


def status_lines(status: Any, coverage: Any, outputs: list[tuple[str, Path]]) -> str:
    return "".join([f"status {status}\n", f"coverage {coverage}\n"] + [f"{name} {path}\n" for name, path in outputs])


def output_paths(private: Path) -> list[tuple[str, Path]]:
    return [(name.split(".")[0], private / name) for name in OUTPUTS] + [("report", private / REPORT)]


def remove(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def finalize(args: argparse.Namespace, private: Path) -> int:
    if args.prior_record is not None:
        prior_path = Path(os.path.abspath(args.prior_record))
        if prior_path.parent == private or os.path.realpath(prior_path.parent) == os.path.realpath(private):
            print(f"finalize refused: the prior record `{prior_path}` lives in `{private}`; a run from a prior record "
                  "writes its new record in a new private directory")
            return 1
    try:
        for name in (REPORT, *OUTPUTS, *RETIRED_OUTPUTS):  # the report first: it is the success marker
            remove(private / name)
            remove(private / f"{name}.part")
    except OSError as error:
        print(f"render_review: cannot remove stale output: {error}", file=sys.stderr)
        return 2

    composition = read_json(private / "composition.json", "composition")
    packet = read_json(Path(args.packet), "packet") if args.packet else None
    store = read_json(Path(args.store), "store")
    if not isinstance(store, dict):
        raise fail("derive", 2, f"render_review: store {args.store} is not a JSON object\n")
    prior = None
    if args.prior_record is not None:
        prior, problems = load_prior(os.path.abspath(args.prior_record))
        if problems:
            raise fail("prior-record", 1, "".join(line + "\n" for line in problems))
    composition, violations = derive(args, private, composition, packet, store, prior)
    if violations:
        raise fail("derive", 1, "".join(line + "\n" for line in violations))
    violations = check_accounting(composition, packet)
    if violations:
        raise fail("accounting", 1, "".join(line + "\n" for line in violations))
    payload, fields, violations = compose_record(composition, store, prior)
    if violations:
        raise fail("compose", 1, "".join(line + "\n" for line in violations))
    batch = emit_batch(payload)

    outputs = output_paths(private)
    replies = rendered_replies(composition)
    given = {"store": args.store, "packet": args.packet, "prior_record": args.prior_record}
    given = {name: os.path.abspath(path) if path else None for name, path in given.items()}
    run_fields = {key: value for key, value in fields["run"].items() if key != "change_description"}
    run_fields["issues"] = sorted(composition["run"]["issues"])
    record_doc = {"schema": RECORD_SCHEMA, "workflow": WORKFLOW, "run": run_fields, "status": fields["status"],
                  "summary": payload["summary"], "items": payload["items"], "prior_items": fields["prior_items"],
                  "record": {**fields["record"], "paths": composition["record"]["paths"]},
                  "lineage": composition["record"]["lineage"], "prior_record": given["prior_record"]}
    try:
        inputs = [(name, Path(path)) for name, path in given.items() if path and name != "store"]
        report = render_report(record_doc, composition, replies, outputs[:-1] + [("composition", private / "composition.json")] + inputs)
    except (KeyError, TypeError, AttributeError) as error:  # the composer validated these shapes
        raise fail("report", 1, f"render_review: cannot render the report from the validated input: {error!r}\n")
    record_doc["finalization"] = {"protocol": FINALIZATION_PROTOCOL, "report": str(private / REPORT), "inputs": given,
                                  "replies": replies}
    staged = {"payload.json": (json.dumps(payload, indent=2) + "\n").encode("utf-8"),
              "batch.json": (json.dumps(batch, indent=2) + "\n").encode("utf-8"),
              "record.json": (json.dumps(record_doc, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
              REPORT: report.encode("utf-8")}

    parts: list[Path] = []
    promoted: list[Path] = []
    try:
        for name, data in staged.items():
            part = private / f"{name}.part"
            parts.append(part)
            part.write_bytes(data)
        for name in staged:  # insertion order ends with the report
            os.replace(private / f"{name}.part", private / name)
            promoted.append(private / name)
    except BaseException as error:
        for path in parts + promoted[::-1]:
            try:
                remove(path)
            except OSError:
                pass
        if not isinstance(error, OSError):
            raise
        print(f"render_review: cannot write output: {error}; nothing this run wrote is left consumable", file=sys.stderr)
        return 2
    sys.stdout.write(status_lines(fields["status"], composition["run"]["coverage"], outputs))
    return 0


def check(args: argparse.Namespace, private: Path) -> int:
    """Read-only: whether PRIVATE_DIR holds a consumable record, at the expected head and lineage when named."""
    source = private / "record.json"
    doc, why = load_object(str(source))
    if doc is None:
        print(f"unconsumable: {source} {why}")
        return 1
    outputs = output_paths(private)
    problems = []
    if doc.get("schema") != RECORD_SCHEMA:
        problems.append(f"{source} is a {json.dumps(doc.get('schema'))} record, not `{RECORD_SCHEMA}`")
    why = finalization_problem(doc)
    if why:
        problems.append(f"{source} {why}")
    elif not same_path(doc["finalization"]["report"], str(private / REPORT)):
        problems.append(f"{source} names report `{doc['finalization']['report']}`, not this directory's")
    problems += [f"{path} is missing" for _name, path in outputs[:-1] if not path.exists()]
    run = doc.get("run") if isinstance(doc.get("run"), dict) else {}
    if args.head is not None and run.get("head") != args.head:
        problems.append(f"{source} reviews head `{run.get('head')}`, not `{args.head}`")
    lineage = doc.get("lineage") if isinstance(doc.get("lineage"), list) else []
    for entry in args.lineage or []:
        if not (same_path(entry, str(source)) or any(same_path(entry, earlier) for earlier in lineage)):
            problems.append(f"{source} does not descend from `{os.path.abspath(entry)}`; its lineage is "
                            f"{json.dumps(lineage)}, so it may have forked from an earlier record")
    if problems:
        for problem in problems:
            print(f"unconsumable: {problem}")
        return 1
    sys.stdout.write(status_lines(doc.get("status"), run.get("coverage"), outputs))
    return 0


# --- self-test -------------------------------------------------------------

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
    f"merge-base={MERGE_BASE} workflow={WORKFLOW} packet_context={CONTEXT} "
    "supplied_inputs=no issues=acme/payments#123 coverage=complete -->"
)

# The contract's summary example carries these two fragments byte-for-byte;
# `render_reference` on the contract payload's items must reproduce them.
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
            f"workflow={WORKFLOW}", "workflow=v5b-19"
        )

    def older_context_trailer(payload):
        for key in ("trailer", "body"):
            payload["summary"][key] = payload["summary"][key].replace(
                f"packet_context={CONTEXT} supplied_inputs=no", f"context={CONTEXT}")

    def malformed_packet_context(payload):
        for key in ("trailer", "body"):
            payload["summary"][key] = payload["summary"][key].replace(f"packet_context={CONTEXT}", "packet_context=abc123")

    def malformed_supplied_inputs(payload):
        for key in ("trailer", "body"):
            payload["summary"][key] = payload["summary"][key].replace("supplied_inputs=no", "supplied_inputs=maybe")

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
        ("older context= run trailer without packet identity", _mutate(older_context_trailer), "trailer-grammar"),
        ("malformed packet_context", _mutate(malformed_packet_context), "trailer-grammar"),
        ("malformed supplied_inputs", _mutate(malformed_supplied_inputs), "trailer-grammar"),
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
# code-span renders without ``repository_url``, the fragments of the contract example and of the
# deleted-file review, the fragment and ``validate`` with an abbreviated merge-base, and the bare
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
    def fragments(payload: dict[str, Any]) -> list[str | None]:
        identity = run_identity(payload["summary"], run_trailer_fields(payload["summary"]))
        return [render_reference(item, identity) for _index, item in referenced_items(payload["items"])]

    if fragments(valid_payload()) != [FINDING_FRAGMENT, QUESTION_FRAGMENT]:
        failures.append(f"fragments of the contract example: got {fragments(valid_payload())!r}")
    if fragments(deleted_file_payload()) != [FINDING_FRAGMENT, DELETED_FRAGMENT]:
        failures.append(f"fragments of the deleted-file review: got {fragments(deleted_file_payload())!r}")
    no_merge_base = deleted_file_payload()
    no_merge_base["summary"]["trailer"] = no_merge_base["summary"]["trailer"].replace(MERGE_BASE, "d4e5f60")
    no_merge_base["summary"]["body"] = no_merge_base["summary"]["body"].replace(MERGE_BASE, "d4e5f60")
    if fragments(no_merge_base) != [FINDING_FRAGMENT, None]:
        failures.append(f"fragments with an abbreviated merge-base: got {fragments(no_merge_base)!r}")
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
        failures.append(f"bare code span: expected the rendering hint, got: {'; '.join(bare)}")
    failures.extend(emit_batch_cases())
    for failure in failures:
        print(failure)
    if failures:
        print(f"render_review: {len(failures)} self-test case(s) failed")
        return 1
    print(f"render_review: self-test passed ({len(passing) + len(failing_cases()) + AD_HOC_CASES + EMIT_BATCH_CASES} cases, emit-batch included)")
    return 0



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("private_dir", nargs="?", help="directory holding composition.json (finalize and --check)")
    parser.add_argument("--store", help="the run's review_context.py store; required to finalize")
    parser.add_argument("--packet", help="the run's forge packet, read-only: pull-request identity, packet_context and thread ids")
    parser.add_argument("--prior-record", help="a local record this run continues after fixes, read-only")
    parser.add_argument("--check", action="store_true", help="read-only: whether PRIVATE_DIR holds a consumable record")
    parser.add_argument("--head", help="with --check: the head the record must review")
    parser.add_argument("--lineage", action="append", metavar="RECORD",
                        help="with --check: a record the checked record must be or descend from; repeatable")
    parser.add_argument("--emit-batch", nargs="?", const="-", metavar="PAYLOAD",
                        help="print the forge-native one-call review body for a valid payload (stdin by default)")
    parser.add_argument("--event", default="COMMENT", choices=("COMMENT", "REQUEST_CHANGES", "APPROVE"),
                        help="with --emit-batch: review event; gating checks status and removes the advisory suffix")
    parser.add_argument("--example", action="store_true", help="print what the reviewer writes for a pull request, then exit")
    parser.add_argument("--self-test", action="store_true", help="run the embedded payload fixtures and exit")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.example:
        print(json.dumps(example_composition(), indent=2))
        return 0
    if args.emit_batch is not None:
        try:
            if args.emit_batch == "-":
                payload = json.load(sys.stdin)
            else:
                with open(args.emit_batch, encoding="utf-8") as handle:
                    payload = json.load(handle)
        except (OSError, ValueError) as error:
            print(f"render_review: {error}", file=sys.stderr)
            return 2
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
    if args.private_dir is None:
        parser.error("PRIVATE_DIR is required to finalize or --check")
    private = Path(os.path.abspath(args.private_dir))
    if args.check:
        return check(args, private)
    if args.head is not None or args.lineage:
        parser.error("--head and --lineage apply only with --check")
    if args.store is None:
        parser.error("--store is required unless --check")
    try:
        return finalize(args, private)
    except Stop as stop:
        return stop.status


if __name__ == "__main__":
    raise SystemExit(main())
