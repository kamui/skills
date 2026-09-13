#!/usr/bin/env python3
"""Compose the code-review-inspect validator payload from authoritative fields
and authored prose.

The reviewer supplies the semantic fields it decided -- each finding's stable
id, priority, action, kind, anchor and fix site; each question's id and
anchor; each observation; each prior item's classification; the run identity,
coverage and status -- together with the prose it authored for every field.
This script renders the repetitive syntax those decisions imply exactly once:
finding and question titles and labelled fields, the ``consider`` permission
sentence, hidden trailers, the summary's status line and counts, its
``Findings``, ``Open questions`` and ``Unanchored findings`` indexes with the
commit-pinned coordinate fragments ``validate_review.py`` renders, the
``Observations``, ``Ambiguities``, ``Disputed``, ``Prior findings`` and
``Coverage gaps`` sections, the ``Mode`` line and the run trailer. It then
validates the composed payload with ``validate_review.py`` and prints it, so
the payload can never drift from what validated; ``validate_review.py
--emit-batch`` projects that payload into the forge batch exactly as before.

The script decides no review judgment. It does not admit or drop an item,
choose a priority, action, kind, status or classification, derive an anchor's
side, or select which observations publish. Input whose fields contradict
each other or omit a judgment is refused with the field named; nothing is
resolved on the reviewer's behalf. It performs no forge call and reads no
repository: ``--store`` reads the run's persisted review context only to check
anchors against the pinned merge-base manifest and the run identity.

Usage::

    python3 scripts/compose_review.py composition.json > payload.json
    python3 scripts/compose_review.py --store <dir>/review-context-<head>.json composition.json > payload.json
    python3 scripts/compose_review.py - < composition.json

Exit codes: ``0`` the composed payload validated and was printed as JSON;
``1`` one or more violations, one line each as ``<location>: <rule>:
<detail>`` on stdout and no payload; ``2`` the input or store could not be
read, named on stderr.

Input schema (JSON object)::

    {
      "run": {
        "head": "<full 40-hex head SHA>",
        "base_ref": "main",
        "base_sha": "<full 40-hex base SHA>",
        "merge_base": "<full 40-hex merge-base SHA>",
        "context": "<64-hex context digest from context_fingerprint.py>",
        "issues": ["acme/payments#123"],        # [] renders issues=none
        "coverage": "complete",                  # complete | incomplete
        "repository_url": "https://github.com/acme/payments",  # optional
        "merged": false,                         # required; true adds the Mode line
        "publication_authorized": false,         # optional; read only when merged
        "prior_head": "<full 40-hex SHA>"        # optional; a delta re-review
      },
      "summary": {
        "status": "Changes Requested",  # Changes Requested | Incomplete | Needs Information | Approved
        "intent": "<Intent line prose>",
        "issue_fit": "<Issue fit line prose>",
        "coverage": "<Coverage line prose>",
        "ambiguities": [{"term": "...", "readings": ["...", "..."], "applied": "..."}],  # optional
        "coverage_gaps": ["..."]        # required non-empty when run.coverage is incomplete
      },
      "findings": [
        {
          "id": "payments/retry-idempotency",
          "title": "Preserve the idempotency key across retries",
          "priority": "P1", "action": "must-fix", "kind": "requirement",
          "blocking": true,                       # optional; must agree with action when present
          "trigger": "...", "impact": "...", "change": "...",
          "source": "Issue #123, acceptance criterion 2.",   # optional
          "anchor": {"type": "line", "path": "src/payments.ts",
                     "start_line": 42, "end_line": 42, "side": "RIGHT"},
          "fix": {"path": "src/retry-policy.ts", "start_line": 18, "end_line": 18}  # optional; end_line optional
        }
      ],
      "questions": [
        {
          "id": "queue/retry-order",
          "title": "Must retries preserve request order?",
          "evidence": "...", "why_it_matters": "...",
          "answer": "Confirm whether retry order is part of the contract; ...",
          "anchor": {"type": "file", "path": "src/queue.ts", "side": "RIGHT"}
        }
      ],
      "observations": [{"fact": "One sentence.", "evidence": "`redis.conf:1903`."}],
      "prior_items": [
        {"id": "payments/retry-idempotency", "classification": "still-open",
         "action": "must-fix", "note": "..."}
      ]
    }

A file anchor names its ``side`` explicitly -- ``LEFT`` for a file the change
deletes, ``RIGHT`` for a file present at the head, ``UNKNOWN`` when the pinned
manifest cannot establish the path or revision -- because the side is the
reviewer's provenance judgment from the full merge-base manifest and the
composer must not default it. Paths are given raw, as the manifest lists
them; the composer percent-encodes a fix coordinate for the trailer and the
payload, and ``validate_review.py`` decodes it once when linking. A prior
item is accounted for in the summary only: its thread reply is drafted and
targeted under ``references/re-review.md`` and the publication procedure,
never inserted into the batch of new comments, so an id may not be both a
prior item and a new item of the same type. Prose is copied byte for byte;
labelled fields must not themselves contain a field label outside code, and
the permission sentence and question framing are added by the composer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

import review_context as rc
import validate_review as vr  # the sibling script; the skill installs alone

STATUSES = ("Changes Requested", "Incomplete", "Needs Information", "Approved")
ADVISORY_STATUSES = ("Changes Requested", "Approved")
CLASSIFICATIONS = ("fixed", "accepted", "obsolete", "still-open", "not-verifiable", "disputed")
OPEN_CLASSIFICATIONS = ("still-open", "not-verifiable", "disputed")
PRIOR_ACTIONS = ("must-fix", "consider", "question")
FILE_SIDES = ("LEFT", "RIGHT", "UNKNOWN")
MODE_DEFAULT = "**Mode:** Retrospective review of merged pull request; publication disabled."
MODE_AUTHORIZED = "**Mode:** Retrospective review of merged pull request; publication separately authorized."
UNANCHORED_NOTE = (
    "The forge's review batch cannot carry a file subject, so each finding below carries its complete prose here."
)
ITEM_INDEX_RE = re.compile(r"items\[(?P<index>[0-9]+)\]")


def token(value: str) -> bool:
    return bool(vr.TOKEN_RE.match(value)) and not vr.BAD_PERCENT_RE.search(value)


def encode_path(path: str) -> str:
    """Percent-encode a coordinate path for a trailer value.

    Spaces, percent signs, and every character outside printable ASCII are
    encoded as the ``%XX`` bytes of their UTF-8 form; nothing else changes, so
    the value is one printable ASCII token and ``validate_review.blob_url``
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


def read_text(report: vr.Report, location: str, obj: dict[str, Any], key: str, required: bool = True) -> str | None:
    value = obj.get(key)
    if value is None:
        if required:
            report.add(location, "schema", f"`{key}` is required and must be a non-empty string")
        return None
    if not isinstance(value, str) or not value.strip():
        report.add(location, "schema", f"`{key}` must be a non-empty string")
        return None
    return value


def read_line(report: vr.Report, location: str, obj: dict[str, Any], key: str, required: bool = True) -> str | None:
    value = read_text(report, location, obj, key, required)
    if value is not None and "\n" in value:
        report.add(location, "schema", f"`{key}` is a single line")
        return None
    return value


def read_id(report: vr.Report, location: str, obj: dict[str, Any]) -> str | None:
    identity = read_line(report, location, obj, "id")
    if identity is not None and not token(identity):
        report.add(location, "stable-id", f"`id={identity}` must be a single printable ASCII token with `%` percent-encoded")
        return None
    return identity


def check_prose_labels(report: vr.Report, location: str, key: str, prose: str, observation: bool = False) -> None:
    """A labelled field's prose may quote a label only inside code."""
    masked = vr.mask_code(prose)
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
    if vr.PERMISSION_SENTENCE in masked:
        report.add(location, "field-label", f"`{key}` contains the permission sentence; the composer adds it to a `consider` finding")


def check_anchor_input(report: vr.Report, location: str, anchor: Any) -> None:
    if not isinstance(anchor, dict):
        report.add(location, "schema", "`anchor` must be an object")
        return
    if anchor.get("type") == "file" and "side" not in anchor:
        report.add(
            location,
            "anchor-provenance",
            "a file anchor names its `side` explicitly: `LEFT` for a file the change deletes, `RIGHT` for a file at the head, "
            "or `UNKNOWN` when the pinned manifest cannot establish the path or revision; derive it from the full merge-base manifest",
        )
    elif anchor.get("type") == "file" and anchor.get("side") not in FILE_SIDES:
        report.add(location, "anchor-provenance", f"a file anchor's `side` is one of {list(FILE_SIDES)}, not `{anchor.get('side')!r}`")
    vr.check_anchor(report, location, anchor)


def compose_fix(report: vr.Report, location: str, fix: Any) -> str | None:
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


def compose_finding(report: vr.Report, location: str, finding: Any, head: str) -> dict[str, Any] | None:
    if not isinstance(finding, dict):
        report.add(location, "schema", "a finding must be an object")
        return None
    identity = read_id(report, location, finding)
    title = read_line(report, location, finding, "title")
    priority, action, kind = finding.get("priority"), finding.get("action"), finding.get("kind")
    if priority not in vr.PRIORITIES:
        report.add(location, "priority-action", f"`priority` must be one of {list(vr.PRIORITIES)}, not `{priority!r}`")
    if action not in vr.ACTIONS:
        report.add(location, "priority-action", f"`action` must be one of {list(vr.ACTIONS)}, not `{action!r}`")
    if kind not in vr.KINDS:
        report.add(location, "priority-action", f"`kind` must be one of {list(vr.KINDS)}, not `{kind!r}`")
    if priority == "P0" and action == "consider":
        report.add(location, "priority-action", "P0 is inherently `must-fix`; a P0 `consider` is contradictory")
    blocking = finding.get("blocking")
    derived = action == "must-fix"
    if blocking is None:
        blocking = derived
    elif not isinstance(blocking, bool):
        report.add(location, "priority-action", "`blocking` must be a boolean when present")
    elif action in vr.ACTIONS and blocking != derived:
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
    if priority not in vr.PRIORITIES or action not in vr.ACTIONS or kind not in vr.KINDS or not isinstance(blocking, bool):
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
        paragraphs.append(vr.PERMISSION_SENTENCE)
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


def compose_question(report: vr.Report, location: str, question: Any, head: str) -> dict[str, Any] | None:
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
        masked = vr.mask_code(text)
        if "**Change:**" in masked:
            report.add(location, "question-form", f"`{key}` states a `**Change:**` field; a question requests no code change")
        if vr.QUESTION_FRAMING in masked:
            report.add(location, "question-form", f"`{key}` contains the `{vr.QUESTION_FRAMING}` framing; the composer adds it before `answer`")
    anchor = question.get("anchor")
    check_anchor_input(report, f"{location}.anchor", anchor)
    if identity is None or title is None or any(text is None for text in prose.values()):
        return None
    markdown = "\n\n".join(
        [
            f"**[Question] {title}**",
            f"**Evidence:** {prose['evidence']}",
            f"**Why it matters:** {prose['why_it_matters']}",
            f"**{vr.QUESTION_FRAMING}.** {prose['answer']}",
        ]
    )
    return {
        "type": "question",
        "id": identity,
        "markdown": markdown,
        "trailer": f"<!-- question id={identity} head={head} action=question -->",
        "anchor": anchor,
    }


def compose_observation(report: vr.Report, location: str, observation: Any) -> dict[str, Any] | None:
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


def read_prior_item(report: vr.Report, location: str, prior: Any) -> dict[str, Any] | None:
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


def read_run(report: vr.Report, run: Any) -> dict[str, Any] | None:
    if not isinstance(run, dict):
        report.add("run", "schema", "`run` must be an object")
        return None
    fields: dict[str, Any] = {}
    for key in ("head", "base_sha", "merge_base"):
        value = run.get(key)
        if not isinstance(value, str) or not vr.COMMIT_SHA_RE.match(value):
            report.add(f"run.{key}", "trailer-sha", f"`{key}` must be exactly 40 lowercase hexadecimal characters")
        fields[key] = value
    base_ref = run.get("base_ref")
    if not isinstance(base_ref, str) or not token(base_ref):
        report.add("run.base_ref", "trailer-grammar", "`base_ref` must be a single printable ASCII token")
    fields["base_ref"] = base_ref
    context = run.get("context")
    if not isinstance(context, str) or not vr.DIGEST_RE.match(context):
        report.add("run.context", "trailer-grammar", "`context` must be the 64-character lowercase SHA-256 digest from context_fingerprint.py")
    fields["context"] = context
    issues = run.get("issues")
    if not isinstance(issues, list) or not all(isinstance(issue, str) and vr.ISSUE_RE.match(issue) for issue in issues):
        report.add("run.issues", "trailer-grammar", "`issues` must be a list of `owner/repo#number` coordinates (empty for none)")
        fields["issues"] = None
    else:
        fields["issues"] = ",".join(sorted(issues)) if issues else "none"
    coverage = run.get("coverage")
    if coverage not in vr.COVERAGE:
        report.add("run.coverage", "trailer-grammar", f"`coverage` must be one of {list(vr.COVERAGE)}, not `{coverage!r}`")
    fields["coverage"] = coverage
    merged = run.get("merged")
    if not isinstance(merged, bool):
        report.add(
            "run.merged",
            "schema",
            "`merged` must be a boolean recorded from the pinned packet; a missing `merged` is an unrecoverable input, not something to infer",
        )
    fields["merged"] = merged
    authorized = run.get("publication_authorized", False)
    if not isinstance(authorized, bool):
        report.add("run.publication_authorized", "schema", "`publication_authorized` must be a boolean when present")
    fields["publication_authorized"] = authorized
    prior_head = run.get("prior_head")
    if prior_head is not None and (not isinstance(prior_head, str) or not vr.COMMIT_SHA_RE.match(prior_head)):
        report.add("run.prior_head", "trailer-sha", "`prior_head` must be exactly 40 lowercase hexadecimal characters when present")
    fields["prior_head"] = prior_head
    repository_url = run.get("repository_url")
    if repository_url is not None and (not isinstance(repository_url, str) or not vr.REPOSITORY_URL_RE.match(repository_url)):
        report.add("run.repository_url", "schema", "`repository_url` must be the base repository's canonical http(s) web URL when present")
        repository_url = None
    fields["repository_url"] = repository_url
    return fields


def read_summary(report: vr.Report, summary: Any, coverage: Any) -> dict[str, Any] | None:
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
            for match in re.finditer(r"\*\*(Intent|Issue fit|Coverage|Reviewed|Mode):\*\*", vr.mask_code(fields[key])):
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
    report: vr.Report,
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
    report: vr.Report,
    findings: list[tuple[str, dict[str, Any]]],
    questions: list[tuple[str, dict[str, Any]]],
    priors: list[tuple[str, dict[str, Any]]],
) -> None:
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
        if new_types.get(prior["id"]) == prior_type:
            report.add(
                location,
                "stable-id",
                f"prior {prior_type} `{prior['id']}` is replied to on its existing thread under references/re-review.md; "
                f"a new {prior_type} with the same id would post a duplicate comment",
            )


def check_store(report: vr.Report, store: dict[str, Any], run: dict[str, Any], items: list[tuple[str, dict[str, Any]]]) -> None:
    """Check anchors against the persisted review context's pinned manifest and run identity."""
    if store.get("format") != rc.STORE_FORMAT or not isinstance(store.get("context"), dict):
        report.add("store", "schema", f"expected a `{rc.STORE_FORMAT}` envelope with a `context` object from review_context.py --store")
        return
    context = store["context"]
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
    for entry in manifest:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        known.add(entry["path"])
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
    report: vr.Report,
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
        fragment = vr.render_reference(item, identity)
        if fragment is None:
            report.add(f"{location}.anchor", "anchor-shape", "cannot render a coordinate fragment from this anchor or fix")
            fragment = ""
        elif fragment in owners:
            report.add(
                location,
                vr.SUMMARY_REFERENCE,
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
        paragraphs.append(MODE_AUTHORIZED if run["publication_authorized"] else MODE_DEFAULT)
    paragraphs.extend(
        [
            f"**Intent:** {summary['intent']}",
            f"**Issue fit:** {summary['issue_fit']}",
            f"**Coverage:** {summary['coverage']}",
            f"**Reviewed:** `{abbreviate(run['head'])}` against merge-base `{abbreviate(run['merge_base'])}`.",
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


def compose(composition: Any, store: dict[str, Any] | None = None) -> tuple[dict[str, Any] | None, list[str]]:
    """Return ``(payload, violations)``; the payload is ``None`` unless it validated with zero violations."""
    report = vr.Report()
    if not isinstance(composition, dict):
        report.add("input", "schema", "the composition input must be a JSON object")
        return None, report.lines
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
    if len(raw_observations) > vr.MAX_OBSERVATIONS:
        report.add(
            "observations",
            "observation-cap",
            f"{len(raw_observations)} observations exceed the cap of {vr.MAX_OBSERVATIONS}; the reviewer publishes the three with the most "
            "decisive evidence and records each of the rest as `observation (unpublished, cap)` — the composer never selects or drops one",
        )
    for index, raw in enumerate(raw_observations):
        item = compose_observation(report, f"observations[{index}]", raw)
        if item is not None:
            observations.append((f"observations[{index}]", item))
    priors: list[tuple[str, dict[str, Any]]] = []
    for index, raw in enumerate(read_list("prior_items")):
        prior = read_prior_item(report, f"prior_items[{index}]", raw)
        if prior is not None:
            priors.append((f"prior_items[{index}]", prior))

    check_identities(report, [(l, f) for l, f, _t in findings], [(l, q) for l, q, _t in questions], priors)
    if store is not None and run is not None:
        check_store(report, store, run, [(l, i) for l, i, _t in findings + questions])
    if run is not None and summary is not None:
        check_status(report, summary["status"], run["coverage"], [f for _l, f, _t in findings], [q for _l, q, _t in questions], [p for _l, p in priors])
    if report.lines or run is None or summary is None:
        return None, report.lines

    trailer = (
        f"<!-- review-run head={run['head']} base-ref={run['base_ref']} base-sha={run['base_sha']} "
        f"merge-base={run['merge_base']} workflow={vr.WORKFLOW} context={run['context']} "
        f"issues={run['issues']} coverage={run['coverage']} -->"
    )
    body = compose_body(report, run, summary, findings, questions, [o for _l, o in observations], [p for _l, p in priors], trailer)
    if report.lines:
        return None, report.lines
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
    violations = [translate(line, locations) for line in vr.validate(payload)]
    if violations:
        return None, violations
    return payload, []


def load_json(path: str, what: str) -> Any:
    try:
        if path == "-":
            return json.load(sys.stdin)
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as error:
        print(f"compose_review: cannot read {what} {path}: {error}", file=sys.stderr)
        raise SystemExit(2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compose the validator payload of a code-review-inspect review from authoritative fields and authored prose."
    )
    parser.add_argument("input", nargs="?", default="-", help="composition JSON file, or - for stdin")
    parser.add_argument(
        "--store",
        help="the run's persisted review context (review-context-<head>.json); its pinned manifest and run identity check every anchor",
    )
    args = parser.parse_args()
    composition = load_json(args.input, "composition input")
    store = None
    if args.store is not None:
        store = load_json(args.store, "store")
        if not isinstance(store, dict):
            print(f"compose_review: store {args.store} is not a JSON object", file=sys.stderr)
            return 2
    payload, violations = compose(composition, store)
    if violations:
        for line in violations:
            print(line)
        return 1
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
