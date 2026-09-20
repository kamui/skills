#!/usr/bin/env python3
"""Compose the review-code validator payload from authoritative fields
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
    python3 scripts/compose_review.py --profile implementation-gate --store <store> composition.json > record.json
    python3 scripts/compose_review.py - < composition.json
    python3 scripts/compose_review.py --example [--profile implementation-gate]   # print a minimal input

Exit codes: ``0`` the composed payload validated and was printed as JSON;
``1`` one or more violations, one line each as ``<location>: <rule>:
<detail>`` on stdout and no payload; ``2`` the input or store could not be
read, named on stderr.

Profiles. ``--profile publishable`` (the default, and what every existing
caller receives unchanged) prints the validator payload that
``validate_review.py --emit-batch`` projects into the forge batch and
``--render`` prints fragments for. ``--profile implementation-gate`` is for a
committed local ``range`` reviewed under ``mode: one-shot`` by a caller that
consumes the record itself (``implement-publish`` step 4): the composition
is validated by exactly the same rules, then printed as one local record,
``implementation-gate-record/1``, whose top-level ``summary`` and ``items``
are the validated payload (so ``validate_review.py < record.json`` still
exits 0) beside the pinned run, its status, and the ``record`` section
below. No batch is projected and no fragment file is rendered: a local
target has no ``repository_url``, so every fragment is already the code span
the summary body carries, and the batch has no consumer outside the
publisher. The profile changes which artifact is printed and requires the
``record`` section; it changes no admission, rendering, status, or coverage
rule.

Every profile runs the semantic record checks: run identity and the
40-hex SHAs, the ``context`` digest, anchor side and, with ``--store``,
anchor provenance against the pinned manifest, finding fields and their
order, priority/action/blocking agreement, duplicate stable ids, question
form, the observation cap, status against unsettled blockers and coverage,
coverage gaps, and — when a ``record`` section is supplied — the ledger,
file-accounting, check-evidence, verification, and routed-item
contradictions listed with that section. ``validate_review.py``'s
``summary-reference`` blob-link rule, the ``--emit-batch`` projection, and
the gating ``--event`` grammar are specific to a forge payload: the first
is vacuous without ``repository_url`` and the other two never run in the
implementation-gate profile.

Input schema (JSON object)::

    {
      "run": {
        "target_kind": "pull-request",            # default; range | worktree
        "target": "main...HEAD",                  # required for range; as requested
        "tree": "<40-hex tree SHA>",              # required only for worktree
        "change_description": "<commit messages>", # required on local targets; may be empty
        "specs": [],                              # local supplied spec identities, optional
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
      ],
      "record": {                                # required by --profile implementation-gate; optional otherwise
        "repository": "/abs/path/to/repo",       # the pinned repository: its path or owner/repo coordinate
        "paths": {                               # every value an absolute path; these four keys are required
          "private_dir": "/tmp/x", "store": "/tmp/x/review-context-<head>.json",
          "composition": "/tmp/x/composition.json",
          "addenda": "/tmp/x/addenda",           # continuations append addendum-<n>.json here; the record itself never changes
          "evidence_packet": "/tmp/x/evidence.md" # optional; any further named path is kept as given
        },
        "ledger": {
          "requirements": [{"source": "issue-123/acceptance-criterion-2", "class": "acceptance",
                            "disposition": "partial", "evidence": "src/payments.ts:42 ..."}],
          "candidates": [{"id": "payments/retry-idempotency", "kind": "requirement", "disposition": "survivor",
                          "verification": "independent-confirmed", "evidence": "src/payments.ts:42"},
                         {"id": "queue/retry-order", "kind": "bug", "disposition": "question", "evidence": "..."},
                         {"id": "payments/retry-budget", "kind": "maintainability", "disposition": "dropped",
                          "evidence": "src/retry-policy.ts:20 bounds the budget"}]  # optional "attackable": true, "material": true
        },
        "files": [{"path": "src/payments.ts", "state": "reviewed"},
                  {"path": "docs/notes.md", "state": "ignored", "reason": "generated changelog"}],
        "check_evidence": [{"check": "python3 scripts/test_x.py", "head": "<reviewed head>", "outcome": "accepted",
                            "reason": "same command, clean tree at the reviewed head, full output read"},
                           {"check": "python3 scripts/test_y.py", "head": "<earlier head>", "outcome": "historical",
                            "reason": "the delta reaches none of its inputs"}],
        "verification": {
          "batches": [{"name": "initial", "bundle": "/tmp/x/initial", "raw_return": "/tmp/x/initial/raw-return.json",
                       "accounting": "/tmp/x/initial/accounting.json", "operation": "Agent run_in_background=false"}],
          "follow_up_spent": false,
          "clean_verdict": "not-required",       # stands | outstanding | not-required
          "outstanding": []                      # mandatory work no permitted batch could carry
        },
        "routed": {"unresolved": [], "disputed": [], "unrecoverable_inputs": []}
      }
    }

The ``record`` section carries the private record's accounting so the
printed local record is complete without the composition conversation.
Its checks are contradictions between fields the reviewer already decided,
never judgments: a requirement row has a source, a class (``acceptance``,
``supporting``, ``artifact``) and a disposition (``met``, ``partial``,
``not-verifiable``); candidate ids are unique; every rendered finding is a
``survivor`` row and every rendered question a ``question`` row, a
``survivor`` or ``question`` row is rendered, a rendered finding's row
names the same ``kind`` the finding does, and a rendered finding names
its ``verification`` -- ``independent-confirmed`` for a ``must-fix``,
``security``, or ``compatibility`` finding, which requires a recorded batch,
otherwise ``primary-confirmed``; every file is ``reviewed``, ``ignored``
with a reason, or ``unreviewed``, once, and with ``--store`` the files are
exactly the pinned manifest's paths; an ``unreviewed`` file, outstanding
verification, an ``outstanding`` clean verdict, or an unrecoverable input
contradicts ``coverage=complete``; check evidence at the reviewed head is
``accepted``, ``reviewer-executed`` (with its selection reason),
``failed``, or ``unavailable``, and ``historical`` evidence is attributed to
a different head with the reason the delta leaves it unaffected -- a
result is never relabelled at the reviewed head; at most two batches are
recorded and ``follow_up_spent`` is true exactly when a second one was
dispatched; and with no material survivor -- a ``must-fix`` at any kind, a
``consider`` of kind ``bug``, ``compatibility``, ``concurrency``,
``invariant``, ``security``, or ``performance``, or a ``survivor`` row the
reviewer marks ``"material": true`` because its claim is an externally
observable compatibility break under another kind -- and at least one
*attackable* ledger row -- any ``kind`` but ``maintainability`` or
``requirement``, any row a verifier ``refuted`` whatever its kind, or a row
the reviewer marks ``"attackable": true`` because its acquittal rests on a
safety premise -- the clean verdict is ``stands`` over a recorded batch or
``outstanding``, never ``not-required``; with no attackable row, an empty
ledger included, ``not-required`` is the only consistent value short of a
recorded batch. ``routed.unresolved`` and ``routed.disputed`` name rendered
or prior item ids.

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
PROFILES = ("publishable", "implementation-gate")
RECORD_SCHEMA = "implementation-gate-record/1"
RECORD_PATHS = ("private_dir", "store", "composition", "addenda")
REQUIREMENT_CLASSES = ("acceptance", "supporting", "artifact")
REQUIREMENT_DISPOSITIONS = ("met", "partial", "not-verifiable")
VERIFICATIONS = ("independent-confirmed", "primary-confirmed")
MANDATORY_KINDS = ("security", "compatibility")
MATERIAL_CONSIDER_KINDS = ("bug", "compatibility", "concurrency", "invariant", "security", "performance")
UNATTACKABLE_KINDS = ("maintainability", "requirement")  # a row of these kinds is attackable only when refuted or marked
FILE_STATES = ("reviewed", "ignored", "unreviewed")
EVIDENCE_OUTCOMES = ("accepted", "historical", "reviewer-executed", "failed", "unavailable")
CLEAN_VERDICTS = ("stands", "outstanding", "not-required")
BATCH_CAP = 2  # one initial plus one follow-up


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
    kind = run.get("target_kind", "pull-request")
    if kind not in ("pull-request", "range", "worktree"):
        report.add("run.target_kind", "schema", "expected pull-request, range, or worktree")
    fields["target_kind"] = kind
    fields["target"] = read_line(report, "run", run, "target") if kind == "range" else None
    tree = run.get("tree")
    if kind == "worktree" and (not isinstance(tree, str) or not vr.COMMIT_SHA_RE.fullmatch(tree)):
        report.add("run.tree", "schema", "worktree requires a full 40-hex tree SHA")
    fields["tree"] = tree
    if kind in ("range", "worktree"):
        description = run.get("change_description")
        if not isinstance(description, str):
            report.add("run.change_description", "schema", "local targets require commit messages (empty string when none)")
        specs = run.get("specs", [])
        if not isinstance(specs, list) or not all(isinstance(s, str) and s.strip() for s in specs):
            report.add("run.specs", "schema", "specs must list supplied spec identities")
        fields["change_description"], fields["specs"] = description, specs
        if run.get("merged") is not False or run.get("repository_url") is not None:
            report.add("run", "schema", "local targets require merged=false and omit repository_url")
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


def read_rows(report: vr.Report, location: str, value: Any, keys: tuple[str, ...]) -> list[tuple[str, dict[str, Any]]]:
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


def read_lines(report: vr.Report, location: str, value: Any) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() and "\n" not in v for v in value):
        report.add(location, "schema", f"`{location.rsplit('.', 1)[-1]}` must be a list of one-line entries")
        return []
    return value


def read_record(
    report: vr.Report,
    record: Any,
    run: dict[str, Any],
    findings: list[dict[str, Any]],
    questions: list[dict[str, Any]],
    priors: list[dict[str, Any]],
    store: dict[str, Any] | None,
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
            report.add("record.paths", "record-paths", f"`{key}` is required so a fresh continuation can find the retained state")
    for key, value in paths.items():
        if not isinstance(value, str) or not value.startswith("/"):
            report.add(f"record.paths.{key}", "record-paths", "must be an absolute path")
    fields["paths"] = paths

    ledger = record.get("ledger")
    if not isinstance(ledger, dict):
        report.add("record.ledger", "schema", "`ledger` must be an object with `requirements` and `candidates`")
        ledger = {}
    requirements = read_rows(report, "record.ledger.requirements", ledger.get("requirements"), ("source", "class", "disposition", "evidence"))
    for where, row in requirements:
        if row["class"] not in REQUIREMENT_CLASSES:
            report.add(where, "ledger", f"`class` must be one of {list(REQUIREMENT_CLASSES)}")
        if row["disposition"] not in REQUIREMENT_DISPOSITIONS:
            report.add(where, "ledger", f"`disposition` must be one of {list(REQUIREMENT_DISPOSITIONS)}")
    candidates = read_rows(report, "record.ledger.candidates", ledger.get("candidates"), ("id", "kind", "disposition", "evidence"))
    rows: dict[str, tuple[str, dict[str, Any]]] = {}
    material = False
    attackable = False
    for where, row in candidates:
        if row["kind"] not in vr.KINDS:
            report.add(where, "ledger", f"`kind` must be one of {list(vr.KINDS)}")
        if row["id"] in rows:
            report.add(where, "stable-id", f"candidate `{row['id']}` is already listed by {rows[row['id']][0]}; a stable id names one defect concept")
        rows[row["id"]] = (where, row)
        if "material" in row and not isinstance(row["material"], bool):
            report.add(where, "schema", "`material` must be a boolean when present")
        material = material or (row.get("material") is True and row["disposition"] == "survivor")
        if "attackable" in row and not isinstance(row["attackable"], bool):
            report.add(where, "schema", "`attackable` must be a boolean when present")
        attackable = attackable or row["kind"] not in UNATTACKABLE_KINDS or row["disposition"] == "refuted" or row.get("attackable") is True
    rendered: dict[str, tuple[str, dict[str, Any]]] = {f["id"]: ("finding", f) for f in findings}
    rendered.update({q["id"]: ("question", q) for q in questions})
    confirmed = False
    for identity, (item_type, item) in rendered.items():
        if identity not in rows:
            report.add("record.ledger.candidates", "ledger", f"rendered {item_type} `{identity}` has no candidate row; every rendered item is a ledger survivor")
            continue
        where, row = rows[identity]
        expected = "survivor" if item_type == "finding" else "question"
        if row["disposition"] != expected:
            report.add(where, "ledger", f"`{identity}` renders as a {item_type}, so its disposition is `{expected}`, not `{row['disposition']}`")
        if item_type != "finding":
            continue
        if row["kind"] != item["kind"]:
            report.add(where, "ledger", f"`{identity}` renders as a `{item['kind']}` finding, so its row's `kind` is `{item['kind']}`, not `{row['kind']}`")
        verification = row.get("verification")
        mandatory = "must-fix" if item["action"] == "must-fix" else item["kind"] if item["kind"] in MANDATORY_KINDS else None
        if mandatory is not None and verification != "independent-confirmed":
            report.add(where, "verification", f"`{identity}` is {mandatory}, which requires `verification: independent-confirmed`; a candidate still needing mandatory confirmation stays unpublished")
        elif verification not in VERIFICATIONS:
            report.add(where, "verification", f"a rendered finding carries `verification` of one of {list(VERIFICATIONS)}")
        confirmed = confirmed or verification == "independent-confirmed"
    for identity, (where, row) in rows.items():
        if row["disposition"] in ("survivor", "question") and identity not in rendered:
            report.add(where, "ledger", f"`{identity}` is a {row['disposition']} with no rendered item; a withheld candidate carries the disposition that withholds it")
    fields["ledger"] = {"requirements": [r for _w, r in requirements], "candidates": [r for _w, r in candidates]}

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
        elif not vr.COMMIT_SHA_RE.match(row["head"]):
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

    verification = record.get("verification")
    if not isinstance(verification, dict):
        report.add("record.verification", "schema", "`verification` must be an object with `batches`, `follow_up_spent`, `clean_verdict`, and `outstanding`")
        verification = {}
    batches = read_rows(report, "record.verification.batches", verification.get("batches", []), ("name", "bundle", "raw_return", "accounting", "operation"))
    for where, batch in batches:
        for key in ("bundle", "raw_return", "accounting"):
            if not batch[key].startswith("/"):
                report.add(f"{where}.{key}", "record-paths", "must be an absolute path")
    if len(batches) > BATCH_CAP:
        report.add("record.verification.batches", "verification", "the cap is one initial plus one follow-up batch; a worker change grants no further batch")
    spent = verification.get("follow_up_spent")
    if not isinstance(spent, bool):
        report.add("record.verification.follow_up_spent", "schema", "`follow_up_spent` must be a boolean")
    elif spent != (len(batches) >= BATCH_CAP):
        report.add("record.verification.follow_up_spent", "verification", f"`follow_up_spent` is {str(spent).lower()} with {plural(len(batches), 'batch')} recorded; the follow-up is spent exactly when a second batch was dispatched")
    outstanding = read_lines(report, "record.verification.outstanding", verification.get("outstanding", []))
    clean = verification.get("clean_verdict")
    if clean not in CLEAN_VERDICTS:
        report.add("record.verification.clean_verdict", "verification", f"`clean_verdict` must be one of {list(CLEAN_VERDICTS)}")
    material = material or any(f["action"] == "must-fix" or f["kind"] in MATERIAL_CONSIDER_KINDS for f in findings)
    if clean == "not-required" and not material and attackable:
        report.add("record.verification.clean_verdict", "verification", "no material survivor remains and the ledger holds an attackable row, so the complete candidate ledger needs a clean-verdict attack: `stands` when a batch ruled, `outstanding` when no permitted batch could carry it")
    if clean == "stands" and not batches:
        report.add("record.verification.clean_verdict", "verification", "`stands` names a batch ruling over the complete ledger, and no batch is recorded")
    if confirmed and not batches:
        report.add("record.verification.batches", "verification", "`independent-confirmed` names a verifier verdict, and no batch is recorded")
    if (clean == "outstanding" or outstanding) and coverage != "incomplete":
        report.add("record.verification", "coverage-gaps", "outstanding verification contradicts `run.coverage=complete`; budget exhaustion never establishes a clean verdict")
    fields["verification"] = {"batches": [b for _w, b in batches], "follow_up_spent": spent, "clean_verdict": clean, "outstanding": outstanding}

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


def compose(
    composition: Any, store: dict[str, Any] | None = None, profile: str = "publishable"
) -> tuple[dict[str, Any] | None, list[str]]:
    """Return ``(result, violations)``: the validated payload, or under ``implementation-gate`` the local record
    carrying it; ``None`` unless the composition validated with zero violations."""
    report = vr.Report()
    if not isinstance(composition, dict):
        report.add("input", "schema", "the composition input must be a JSON object")
        return None, report.lines
    run = read_run(report, composition.get("run"))
    if profile == "implementation-gate" and run is not None:
        if run["target_kind"] != "range":
            report.add("run.target_kind", "profile", "`implementation-gate` reviews a committed local range; a working tree or pull request keeps the publishable profile")
        if run["prior_head"] is not None:
            report.add("run.prior_head", "profile", "a one-shot local range is a first review; a continuation appends an addendum beside the record instead of a delta re-review")
    if profile == "implementation-gate" and "record" not in composition:
        report.add("record", "profile", "`implementation-gate` returns one local record, so the composition carries `record`: ledgers, file accounting, check evidence, verification accounting, routed items, and paths")
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
    record = None
    if run is not None and "record" in composition:
        record = read_record(report, composition["record"], run, [f for _l, f, _t in findings], [q for _l, q, _t in questions], [p for _l, p in priors], store)
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
    if profile != "implementation-gate":
        return payload, []
    issues = composition["run"]["issues"]
    pinned = {
        "repository": record["repository"], "target": run["target"], "head": run["head"], "base_ref": run["base_ref"],
        "base_sha": run["base_sha"], "merge_base": run["merge_base"], "context": run["context"],
        "issues": sorted(issues), "specs": run["specs"], "coverage": run["coverage"],
    }
    return {
        "schema": RECORD_SCHEMA, "profile": profile, "workflow": vr.WORKFLOW, "run": pinned, "status": summary["status"],
        "summary": payload["summary"], "items": payload["items"], "record": record,
    }, []


def load_json(path: str, what: str) -> Any:
    try:
        if path == "-":
            return json.load(sys.stdin)
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as error:
        print(f"compose_review: cannot read {what} {path}: {error}", file=sys.stderr)
        raise SystemExit(2)


def example_composition(profile: str) -> dict[str, Any]:
    """The docstring's example as a composition input; ``--example`` prints it and it composes at exit 0."""
    head, base, merge_base = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678", "b2c3d4e5f60718293a4b5c6d7e8f90123456789a", "d4e5f60718293a4b5c6d7e8f90123456789abcde"
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
        "run": {"head": head, "base_ref": "main", "base_sha": base, "merge_base": merge_base,
                "context": "91d34a2f4c869867167f0b31da7c207f4528e12e3d1ef4f107a5eabb4c18718e",
                "issues": ["acme/payments#123"], "coverage": "complete", "merged": False},
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
    if profile == "publishable":
        composition["run"]["repository_url"] = "https://github.com/acme/payments"
        return composition
    composition["run"].update({"target_kind": "range", "target": "main...HEAD", "change_description": "Add retries for charge submission",
                               "specs": ["/abs/path/to/spec.md"]})
    private = "/tmp/review-code-XXXXXX"
    composition["record"] = {
        "repository": "/abs/path/to/checkout",
        "paths": {"private_dir": private, "store": f"{private}/review-context-{head}.json",
                  "composition": f"{private}/composition.json", "addenda": f"{private}/addenda",
                  "skill_root": "/abs/path/to/skills/review-code", "evidence_packet": "/abs/path/to/results.md",
                  "spec": "/abs/path/to/spec.md"},
        "ledger": {
            "requirements": [{"source": "issue-123/acceptance-criterion-2", "class": "acceptance", "disposition": "partial",
                              "evidence": "src/payments.ts:42 creates a key per attempt"}],
            "candidates": [{"id": "payments/retry-idempotency", "kind": "requirement", "disposition": "survivor",
                            "verification": "independent-confirmed", "evidence": "src/payments.ts:42"},
                           {"id": "queue/retry-order", "kind": "bug", "disposition": "question", "evidence": "src/queue.ts:7"},
                           {"id": "payments/retry-budget", "kind": "maintainability", "disposition": "dropped",
                            "evidence": "src/retry-policy.ts:20 bounds the budget"}],
        },
        "files": [{"path": "src/payments.ts", "state": "reviewed"}, {"path": "src/queue.ts", "state": "reviewed"},
                  {"path": "docs/notes.md", "state": "ignored", "reason": "generated changelog"}],
        "check_evidence": [{"check": "pnpm test payments", "head": head, "outcome": "accepted",
                            "reason": "same command, clean tree at the reviewed head, full output read"}],
        "verification": {"batches": [{"name": "initial", "bundle": f"{private}/initial", "raw_return": f"{private}/initial/raw-return.json",
                                      "accounting": f"{private}/initial/accounting.json", "operation": "Agent run_in_background=false"}],
                         "follow_up_spent": False, "clean_verdict": "not-required", "outstanding": []},
        "routed": {"unresolved": ["queue/retry-order"], "disputed": [], "unrecoverable_inputs": []},
    }
    return composition


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compose the validator payload of a review-code review from authoritative fields and authored prose."
    )
    parser.add_argument("input", nargs="?", default="-", help="composition JSON file, or - for stdin")
    parser.add_argument(
        "--store",
        help="the run's persisted review context (review-context-<head>.json); its pinned manifest and run identity check every anchor",
    )
    parser.add_argument(
        "--profile",
        default="publishable",
        choices=PROFILES,
        help="publishable prints the validator payload (default); implementation-gate prints one validated local record for a committed range and requires the `record` section",
    )
    parser.add_argument("--example", action="store_true", help="print a minimal composition input for the profile, then exit")
    args = parser.parse_args()
    if args.example:
        print(json.dumps(example_composition(args.profile), indent=2))
        return 0
    if args.store is not None:
        EVENT.update(event="payload-composed", store=args.store)
    composition = load_json(args.input, "composition input")
    EVENT.update(composition=composition)
    store = None
    if args.store is not None:
        store = load_json(args.store, "store")
        if not isinstance(store, dict):
            print(f"compose_review: store {args.store} is not a JSON object", file=sys.stderr)
            return 2
    result, violations = compose(composition, store, args.profile)
    if violations:
        for line in violations:
            print(line)
        return 1
    print(json.dumps(result, indent=2))
    return 0


# What a --store composition hands run_events.py; recording never changes the result.
EVENT: dict[str, Any] = {}


if __name__ == "__main__":
    import time

    started_ns = time.monotonic_ns()
    try:
        status = main()
    except SystemExit as stop:  # load_json exits from inside main
        status = stop.code
    try:
        import run_events

        run_events.record(EVENT, status, started_ns, "compose_review.py")
    except Exception:
        pass
    raise SystemExit(status)
