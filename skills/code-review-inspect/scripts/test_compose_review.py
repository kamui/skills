#!/usr/bin/env python3
"""Exercise compose_review.py through its CLI: composition, refusal, and batch agreement.

Usage: python3 scripts/test_compose_review.py
Inputs: local fixture compositions; no repository or forge access.
Exit 0: all checks pass; exit 1: a check fails; exit 2: the CLI cannot run.

Every fixture composes a payload, validates it with validate_review.py, and
projects it with --emit-batch, so the three scripts are checked in agreement.
Refusal fixtures assert the rule name and that no payload is printed.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import validate_review as vr

COMPOSER = Path(__file__).with_name("compose_review.py")
VALIDATOR = Path(__file__).with_name("validate_review.py")
HEAD = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
BASE = "b2c3d4e5f60718293a4b5c6d7e8f90123456789a"
MERGE_BASE = "d4e5f60718293a4b5c6d7e8f90123456789abcde"
PRIOR = "0123456789abcdef0123456789abcdef01234567"
CONTEXT = "91d34a2f4c869867167f0b31da7c207f4528e12e3d1ef4f107a5eabb4c18718e"
REPO = "https://github.com/acme/payments"
BLOB = f"{REPO}/blob/{HEAD}"
FINDING_FRAGMENT = (
    f"anchor [`src/payments.ts:42`]({BLOB}/src/payments.ts?plain=1#L42); "
    f"fix [`src/retry-policy.ts:18`]({BLOB}/src/retry-policy.ts?plain=1#L18)"
)
QUESTION_FRAGMENT = f"anchor [`src/queue.ts`]({BLOB}/src/queue.ts) (file)"


def run(script: Path, stdin: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args], input=stdin, capture_output=True, encoding="utf-8", check=False
    )


def base_composition() -> dict:
    """The output contract's example review as a composition input."""
    return {
        "run": {
            "head": HEAD, "base_ref": "main", "base_sha": BASE, "merge_base": MERGE_BASE, "context": CONTEXT,
            "issues": ["acme/payments#123"], "coverage": "complete", "repository_url": REPO, "merged": False,
        },
        "summary": {
            "status": "Changes Requested",
            "intent": "Add retries for charge submission without changing payment semantics.",
            "issue_fit": "Partial — retry availability is implemented, but acceptance criterion 2's idempotency guarantee remains open.",
            "coverage": "Complete merge-base diff reviewed; payment callers inspected; focused `retry-policy` test run once at the head: pass.",
        },
        "findings": [
            {
                "id": "payments/retry-idempotency", "title": "Preserve the idempotency key across retries",
                "priority": "P1", "action": "must-fix", "kind": "requirement",
                "trigger": "The server commits a charge but its response times out and the\nclient retries.",
                "impact": "The retry uses a new idempotency key and can submit a second charge.",
                "change": "In `src/retry-policy.ts`, reuse one idempotency key across every attempt\nfor the same logical charge.",
                "source": "Issue #123, acceptance criterion 2.",
                "anchor": {"type": "line", "path": "src/payments.ts", "start_line": 42, "end_line": 42, "side": "RIGHT"},
                "fix": {"path": "src/retry-policy.ts", "start_line": 18},
            }
        ],
        "questions": [
            {
                "id": "queue/retry-order", "title": "Must retries preserve request order?",
                "evidence": "The new queue retries at the tail, while existing callers consume it\nas FIFO. The issue, tests, and history do not establish whether reordering is allowed.",
                "why_it_matters": "The answer determines whether this is a merge-blocking regression.",
                "answer": "Confirm whether retry order is part of the contract;\nthe maintainer answer settles whether the candidate should re-open as a finding.",
                "anchor": {"type": "file", "path": "src/queue.ts", "side": "RIGHT"},
            }
        ],
        "observations": [
            {
                "fact": "The first configuration sentence covers same-shard re-points more broadly than the implementation does.",
                "evidence": "`redis.conf:1903`, `src/replication.c:2701`.",
            }
        ],
    }


def composed(composition: dict, name: str, *args: str) -> tuple[dict, dict, str]:
    """Compose, then validate and project the printed payload; return (payload, batch, raw stdout)."""
    result = run(COMPOSER, json.dumps(composition), *args)
    assert result.returncode == 0, (name, result.returncode, result.stdout, result.stderr)
    assert result.stderr == "", (name, result.stderr)
    payload = json.loads(result.stdout)
    checked = run(VALIDATOR, result.stdout)
    assert checked.returncode == 0, (name, checked.stdout)
    emitted = run(VALIDATOR, result.stdout, "--emit-batch")
    assert emitted.returncode == 0, (name, emitted.stdout)
    batch = json.loads(emitted.stdout)
    assert batch["commit_id"] == HEAD and batch["body"] == payload["summary"]["body"], name
    inline = [item for item in payload["items"] if item["type"] != "observation" and item["anchor"]["type"] == "line"]
    assert len(batch["comments"]) == len(inline), (name, batch["comments"])
    for item in payload["items"]:
        if item["type"] == "observation":
            assert item["markdown"] in payload["summary"]["body"], (name, item)
            continue
        fragment = vr.render_reference(item, {"head": HEAD, "merge_base": MERGE_BASE, "repository_url": REPO})
        assert payload["summary"]["body"].count(fragment) == 1, (name, fragment)
        if item["anchor"]["type"] != "line":
            # A body-carried item keeps its complete prose and trailer in the body, once.
            assert payload["summary"]["body"].count(item["markdown"]) == 1, (name, item["id"])
            assert payload["summary"]["body"].count(item["trailer"]) == 1, (name, item["id"])
        else:
            assert item["markdown"] not in payload["summary"]["body"], (name, item["id"])
            assert any(comment["body"] == f"{item['markdown']}\n\n{item['trailer']}" for comment in batch["comments"]), name
    return payload, batch, result.stdout


def refused(composition: dict, rule: str, name: str, *args: str, needle: str | None = None) -> str:
    result = run(COMPOSER, json.dumps(composition), *args)
    assert result.returncode == 1, (name, result.returncode, result.stdout, result.stderr)
    rules = {line.split(": ", 2)[1] for line in result.stdout.splitlines() if line.count(": ") >= 2}
    assert rule in rules, (name, rule, result.stdout)
    assert '"summary"' not in result.stdout and "commit_id" not in result.stdout, (name, result.stdout)
    if needle is not None:
        assert needle in result.stdout, (name, needle, result.stdout)
    return result.stdout


def finding(**overrides) -> dict:
    value = base_composition()["findings"][0]
    value.update(overrides)
    return value


def consider(**overrides) -> dict:
    value = finding(id="payments/retry-naming", title="Name the retry budget constant", priority="P3", action="consider",
                    kind="maintainability", change="Name the budget constant in `src/payments.ts` after the policy it bounds.",
                    anchor={"type": "line", "path": "src/payments.ts", "start_line": 50, "end_line": 50, "side": "RIGHT"})
    del value["fix"]
    value.update(overrides)
    return value


def main() -> int:
    # Ordinary finding, whole-change question, observation: the contract example, byte for byte where the contract renders it.
    contract = base_composition()
    payload, batch, stdout = composed(contract, "contract example")
    body = payload["summary"]["body"]
    assert body.startswith("**Changes Requested (advisory)** — 1 must-fix finding, 1 open question.\n\n**Intent:**"), body
    assert f"## Findings\n\n- [P1] [must-fix] Preserve the idempotency key across retries — {FINDING_FRAGMENT}\n\n" in body
    assert f"## Open questions\n\n- [Question] Must retries preserve request order? — {QUESTION_FRAGMENT}\n\n**[Question]" in body
    assert "## Observations\n\n- The first configuration sentence" in body
    assert f"**Reviewed:** `{HEAD[:7]}` against merge-base `{MERGE_BASE[:7]}`." in body
    assert payload["items"][0]["markdown"] == vr.FINDING_MARKDOWN and payload["items"][1]["markdown"] == vr.QUESTION_MARKDOWN
    assert payload["items"][0]["trailer"] == vr.valid_payload()["items"][0]["trailer"]
    assert payload["summary"]["trailer"] == vr.RUN_TRAILER
    assert batch["comments"][0]["path"] == "src/payments.ts" and batch["comments"][0]["line"] == 42
    rendered = run(VALIDATOR, stdout, "--render")
    assert rendered.stdout == f"{FINDING_FRAGMENT}\n{QUESTION_FRAGMENT}\n", rendered.stdout
    assert run(COMPOSER, json.dumps(contract)).stdout == stdout, "composition is deterministic"
    for section in ("## Unanchored findings", "## Disputed", "## Prior findings", "## Coverage gaps", "## Ambiguities", "**Mode:**"):
        assert section not in body, section
    assert vr.validate(vr.valid_payload()) == [] and vr.validate(vr.unanchored_payload()) == [], "historical validator inputs remain readable"
    print("ok contract example: compose/validate/emit-batch agree, deterministic")

    # Optional finding: the permission sentence is rendered last, blocking derives from action, conflicts are refused.
    optional = base_composition()
    optional["findings"].append(consider())
    payload, batch, _ = composed(optional, "consider finding")
    item = payload["items"][1]
    assert item["markdown"].startswith("**[P3] [consider] Name the retry budget constant**") and item["blocking"] is False
    assert item["markdown"].endswith(f"**Source:** Issue #123, acceptance criterion 2.\n\n{vr.PERMISSION_SENTENCE}"), item["markdown"]
    assert item["trailer"].endswith("blocking=false kind=maintainability -->") and len(batch["comments"]) == 2
    shared = base_composition()
    shared["findings"].append(consider(anchor=finding()["anchor"], fix=finding()["fix"], change=finding()["change"]))
    refused(shared, "summary-reference", "two findings sharing one anchor and fix", needle="findings[1]")
    assert "— 1 must-fix finding, 1 consider finding, 1 open question." in payload["summary"]["body"]
    assert "- [P3] [consider] Name the retry budget constant — " in payload["summary"]["body"]
    refused({**optional, "findings": [finding(), consider(blocking=True)]}, "priority-action", "consider marked blocking")
    refused({**optional, "findings": [finding(blocking=False)]}, "priority-action", "must-fix marked non-blocking")
    refused({**optional, "findings": [finding(), consider(priority="P0")]}, "priority-action", "P0 consider")
    refused({**optional, "findings": [finding(kind="style")]}, "priority-action", "unknown kind")
    refused({**optional, "findings": [finding(change=f"Do it.\n\n{vr.PERMISSION_SENTENCE}")]}, "field-label", "authored permission sentence")
    print("ok consider finding: permission sentence, derived blocking, conflicting metadata refused")

    # Clean review, gating, and the advisory marker.
    clean = base_composition()
    clean.update({"findings": [], "questions": [], "observations": []})
    clean["summary"]["status"] = "Approved"
    payload, batch, _ = composed(clean, "clean review")
    assert payload["summary"]["body"].startswith("**Approved (advisory)** — no findings.\n") and batch["comments"] == []
    clean["summary"]["gating"] = True
    payload, _, _ = composed(clean, "gating approval")
    assert payload["summary"]["body"].startswith("**Approved** — no findings.\n")
    print("ok clean review: no findings, advisory marker follows gating")

    # Questions: a line-anchored question is a comment; a whole-change question lives in the body with its prose.
    questions = base_composition()
    line_question = copy.deepcopy(questions["questions"][0])
    line_question.update({"id": "queue/retry-window", "title": "Is the retry window bounded?",
                          "anchor": {"type": "line", "path": "src/queue.ts", "start_line": 7, "end_line": 9, "side": "RIGHT"}})
    questions["questions"].append(line_question)
    payload, batch, _ = composed(questions, "line and whole-change questions")
    assert len(batch["comments"]) == 2 and batch["comments"][1]["start_line"] == 7 and batch["comments"][1]["line"] == 9
    assert "— 1 must-fix finding, 2 open questions." in payload["summary"]["body"]
    assert f"- [Question] Is the retry window bounded? — anchor [`src/queue.ts:7-9`]({BLOB}/src/queue.ts?plain=1#L7-L9)" in payload["summary"]["body"]
    bad = base_composition()
    bad["questions"][0]["answer"] = "**Change:** reorder the queue."
    refused(bad, "question-form", "question requesting code")
    bad = base_composition()
    bad["questions"][0]["evidence"] = f"{vr.QUESTION_FRAMING}. Already framed."
    refused(bad, "question-form", "question with authored framing")
    bad = base_composition()
    bad["questions"][0]["priority"] = "P2"
    refused(bad, "question-form", "question with priority")
    print("ok questions: line anchor is a comment, whole-change question is body-carried, malformed forms refused")

    # Observations: three publish; a fourth is refused with the private-record disposition named, never dropped.
    observations = base_composition()
    observations["observations"] = [
        {"fact": f"Fact number {n} stands on its own.", "evidence": f"`src/file{n}.ts:{n}`."} for n in range(1, 4)
    ]
    payload, _, _ = composed(observations, "three observations")
    assert payload["summary"]["body"].count("\n- Fact number ") == 3
    observations["observations"].append({"fact": "A fourth fact.", "evidence": "`src/file4.ts:4`."})
    refused(observations, "observation-cap", "four observations", needle="observation (unpublished, cap)")
    bad = base_composition()
    bad["observations"][0]["fact"] = "The configuration covers same-shard re-points. The implementation narrows it."
    refused(bad, "observation-form", "two-sentence observation", needle="observations[0]")
    bad = base_composition()
    bad["observations"][0]["fact"] = "The configuration should cover same-shard re-points."
    refused(bad, "observation-form", "observation using should", needle="observations[0]")
    print("ok observations: cap refused with the disposition named, validator locations translated")

    # Code and suggestion blocks are preserved verbatim; a literal label counts only outside code.
    suggestion = base_composition()
    suggestion["findings"][0]["change"] = (
        "Reuse one key across every attempt in `src/retry-policy.ts`:\n\n```suggestion\n"
        "const key = attempt.idempotencyKey; // **Impact:** and **Change:** here are code, not fields\n```"
    )
    payload, batch, _ = composed(suggestion, "suggestion block")
    assert suggestion["findings"][0]["change"] in payload["items"][0]["markdown"]
    assert suggestion["findings"][0]["change"] in batch["comments"][0]["body"]
    span = base_composition()
    span["findings"][0]["change"] = "Keep the `**Impact:**` label in `src/retry-policy.ts`. Reuse one key."
    composed(span, "label inside a code span")
    bare = base_composition()
    bare["findings"][0]["change"] = "Reuse one key in `src/retry-policy.ts`.\n\n**Impact:** restated here."
    refused(bare, "field-label", "literal label outside code", needle="findings[0]")
    print("ok code blocks: suggestion and code-span labels preserved, bare label refused")

    # Fix sites: omitted, distinct and named, distinct and unnamed, ranged, and a path needing percent-encoding.
    no_fix = base_composition()
    del no_fix["findings"][0]["fix"]
    payload, _, _ = composed(no_fix, "fix omitted")
    assert "fix=" not in payload["items"][0]["trailer"] and "fix" not in payload["items"][0]
    assert f"— anchor [`src/payments.ts:42`]({BLOB}/src/payments.ts?plain=1#L42)\n" in payload["summary"]["body"]
    unnamed = base_composition()
    unnamed["findings"][0]["change"] = "Reuse one idempotency key across every attempt."
    refused(unnamed, "fix-site", "fix site not named in change", needle="src/retry-policy.ts")
    same_file = base_composition()
    same_file["findings"][0]["change"] = "Reuse one idempotency key across every attempt."
    same_file["findings"][0]["fix"] = {"path": "src/payments.ts", "start_line": 40, "end_line": 41}
    payload, _, _ = composed(same_file, "ranged fix in the anchor's file")
    assert payload["items"][0]["fix"] == "src/payments.ts:40-41" and "fix=src/payments.ts:40-41 -->" in payload["items"][0]["trailer"]
    encoded = base_composition()
    encoded["findings"][0]["change"] = "Document the key in docs/my 100% file.md."
    encoded["findings"][0]["fix"] = {"path": "docs/my 100% file.md", "start_line": 3}
    payload, _, _ = composed(encoded, "fix path percent-encoded")
    assert payload["items"][0]["fix"] == "docs/my%20100%25%20file.md:3"
    assert f"; fix [`docs/my%20100%25%20file.md:3`]({BLOB}/docs/my%20100%25%20file.md?plain=1#L3)" in payload["summary"]["body"]
    bad = base_composition()
    bad["findings"][0]["fix"] = {"path": "src/retry-policy.ts", "start_line": 20, "end_line": 18}
    refused(bad, "fix-coordinate", "reversed fix range")
    print("ok fix sites: omitted, ranged, encoded, unnamed refused")

    # Anchors: LEFT line, deleted file, unknown provenance, missing provenance.
    left_line = base_composition()
    left_line["findings"][0]["anchor"] = {"type": "line", "path": "src/payments.ts", "start_line": 40, "end_line": 40, "side": "LEFT"}
    payload, batch, _ = composed(left_line, "LEFT line anchor")
    assert batch["comments"][0]["side"] == "LEFT"
    assert f"— anchor `src/payments.ts:40`; fix [`src/retry-policy.ts:18`]({BLOB}/src/retry-policy.ts?plain=1#L18)" in payload["summary"]["body"]
    deleted = base_composition()
    deleted["questions"][0]["anchor"] = {"type": "file", "path": "src/legacy-queue.ts", "side": "LEFT"}
    payload, batch, _ = composed(deleted, "deleted file question")
    assert f"anchor [`src/legacy-queue.ts`]({REPO}/blob/{MERGE_BASE}/src/legacy-queue.ts) (file)" in payload["summary"]["body"]
    unknown = base_composition()
    unknown["questions"][0]["anchor"] = {"type": "file", "path": "reported/path.ts", "side": "UNKNOWN"}
    payload, _, _ = composed(unknown, "UNKNOWN provenance")
    assert "— anchor `reported/path.ts` (file)\n" in payload["summary"]["body"] and f"{BLOB}/reported" not in payload["summary"]["body"]
    legacy = base_composition()
    legacy["questions"][0]["anchor"] = {"type": "file", "path": "src/queue.ts"}
    refused(legacy, "anchor-provenance", "file anchor without side", needle="questions[0].anchor")
    bad = base_composition()
    bad["findings"][0]["anchor"] = {"type": "line", "path": "src/payments.ts", "start_line": 44, "end_line": 42, "side": "RIGHT"}
    refused(bad, "anchor-shape", "reversed line anchor")
    bad = base_composition()
    bad["findings"][0]["anchor"] = {"type": "file", "path": "src/payments.ts", "side": "BOTH"}
    refused(bad, "anchor-provenance", "file anchor with a bad side")
    print("ok anchors: LEFT line, deleted file, UNKNOWN, missing or malformed provenance refused")

    # The pinned manifest checks anchor provenance without deciding it.
    with tempfile.TemporaryDirectory() as directory:
        store_path = Path(directory) / f"review-context-{HEAD}.json"
        store = {
            "head": HEAD, "merge_base": MERGE_BASE,
            "manifest": [
                {"status": "M", "path": "src/payments.ts", "old_path": None},
                {"status": "R", "path": "src/queue.ts", "old_path": "src/old-queue.ts"},
                {"status": "D", "path": "src/legacy-queue.ts", "old_path": None},
                {"status": "A", "path": "src/retry-policy.ts", "old_path": None},
            ],
        }
        store_path.write_text(json.dumps(store), encoding="utf-8")
        composed(base_composition(), "manifest agrees", "--store", str(store_path))
        composed(deleted, "manifest D entry with LEFT", "--store", str(store_path))
        renamed = base_composition()
        renamed["questions"][0]["anchor"] = {"type": "line", "path": "src/old-queue.ts", "start_line": 3, "end_line": 3, "side": "LEFT"}
        composed(renamed, "LEFT line on a rename's old path", "--store", str(store_path))
        at_head = copy.deepcopy(deleted)
        at_head["questions"][0]["anchor"]["side"] = "RIGHT"
        refused(at_head, "anchor-provenance", "deleted file marked RIGHT", "--store", str(store_path), needle="`D` entry")
        as_unknown = copy.deepcopy(deleted)
        as_unknown["questions"][0]["anchor"]["side"] = "UNKNOWN"
        composed(as_unknown, "deleted file marked UNKNOWN is the reviewer's call", "--store", str(store_path))
        undeleted = base_composition()
        undeleted["questions"][0]["anchor"]["side"] = "LEFT"
        refused(undeleted, "anchor-provenance", "present file marked LEFT", "--store", str(store_path))
        refused(unknown, "anchor-provenance", "path outside the manifest", "--store", str(store_path), needle="reported/path.ts")
        stale = base_composition()
        stale["run"]["head"] = PRIOR
        refused(stale, "run-identity", "store built for another head", "--store", str(store_path))
        missing = run(COMPOSER, json.dumps(base_composition()), "--store", str(Path(directory) / "absent.json"))
        assert missing.returncode == 2 and "absent.json" in missing.stderr, missing
    print("ok manifest: D/LEFT agreement checked, unknown paths and stale stores refused")

    # Stable ids: duplicates and malformed ids are refused.
    duplicate = base_composition()
    duplicate["questions"][0]["id"] = "payments/retry-idempotency"
    refused(duplicate, "stable-id", "duplicate id across finding and question")
    spaced = base_composition()
    spaced["findings"][0]["id"] = "payments/retry idempotency"
    refused(spaced, "stable-id", "id with a space")
    print("ok stable ids: duplicates and malformed ids refused")

    # Statuses: each of the four, with the contradictions the contract's precedence makes decidable.
    approved_with_blocker = base_composition()
    approved_with_blocker["summary"]["status"] = "Approved"
    refused(approved_with_blocker, "status-consistency", "Approved with a must-fix", needle="payments/retry-idempotency")
    changes_without_blocker = base_composition()
    changes_without_blocker["findings"] = [consider()]
    refused(changes_without_blocker, "status-consistency", "Changes Requested without a blocker")
    needs_info = base_composition()
    needs_info["findings"] = [consider()]
    needs_info["summary"]["status"] = "Needs Information"
    payload, _, _ = composed(needs_info, "Needs Information")
    assert payload["summary"]["body"].startswith("**Needs Information** — 1 consider finding, 1 open question.")
    needs_info["questions"] = []
    refused(needs_info, "status-consistency", "Needs Information without a question")
    incomplete_marked_complete = base_composition()
    incomplete_marked_complete["findings"] = [consider()]
    incomplete_marked_complete["summary"]["status"] = "Incomplete"
    refused(incomplete_marked_complete, "status-consistency", "Incomplete with complete coverage")
    incomplete = base_composition()
    incomplete["findings"] = [consider()]
    incomplete["questions"] = []
    incomplete["run"]["coverage"] = "incomplete"
    incomplete["summary"]["status"] = "Incomplete"
    incomplete["summary"]["coverage_gaps"] = [
        "`reviewThreads` continuation 2 failed; a reply there could change `payments/retry-naming`.",
        "Verification of `payments/retry-budget` did not finish; it stays unpublished.",
    ]
    payload, batch, _ = composed(incomplete, "incomplete coverage with a verified unrelated finding")
    assert payload["summary"]["body"].startswith("**Incomplete** — 1 consider finding.") and len(batch["comments"]) == 1
    assert "## Coverage gaps\n\n- `reviewThreads` continuation 2 failed" in payload["summary"]["body"]
    assert "coverage=incomplete -->" in payload["summary"]["trailer"]
    approved_incomplete = copy.deepcopy(incomplete)
    approved_incomplete["summary"]["status"] = "Approved"
    refused(approved_incomplete, "status-consistency", "Approved with incomplete coverage")
    del incomplete["summary"]["coverage_gaps"]
    refused(incomplete, "coverage-gaps", "incomplete coverage without a named gap")
    gaps_but_complete = base_composition()
    gaps_but_complete["summary"]["coverage_gaps"] = ["a gap"]
    refused(gaps_but_complete, "coverage-gaps", "coverage gaps with complete coverage")
    blocker_incomplete = base_composition()
    blocker_incomplete["run"]["coverage"] = "incomplete"
    blocker_incomplete["summary"]["coverage_gaps"] = ["Verification of `payments/retry-budget` did not finish."]
    payload, _, _ = composed(blocker_incomplete, "blocker takes precedence over incomplete coverage")
    assert payload["summary"]["body"].startswith("**Changes Requested (advisory)**") and "## Coverage gaps" in payload["summary"]["body"]
    print("ok statuses: all four composed, contradictions with blockers, coverage, and questions refused")

    # Re-review: prior items are accounted for in the summary only and never enter the batch; disputed blockers hold status.
    rereview = base_composition()
    rereview["run"]["prior_head"] = PRIOR
    rereview["findings"] = [consider()]
    rereview["prior_items"] = [
        {"id": "payments/retry-idempotency", "classification": "disputed", "action": "must-fix",
         "note": "declined twice; the timeout-after-commit trace still holds at `src/payments.ts:42`."},
        {"id": "payments/retry-logging", "classification": "fixed", "action": "consider",
         "note": "implemented in `9f1e0aa`; the focused test passes at the head."},
        {"id": "payments/retry-budget", "classification": "still-open", "action": "must-fix",
         "note": "the reply states intent; the head still creates a key per attempt."},
        {"id": "queue/ordering", "classification": "not-verifiable", "action": "question", "note": "no maintainer answer yet."},
    ]
    payload, batch, _ = composed(rereview, "re-review with prior items")
    body = payload["summary"]["body"]
    assert body.startswith(
        "**Changes Requested (advisory)** — 1 consider finding, 1 open question, 2 prior items still open, 1 disputed prior finding. "
        f"Delta review of `{PRIOR[:7]}..{HEAD[:7]}`.\n"
    ), body
    assert "## Disputed\n\n- `payments/retry-idempotency` — disputed: declined twice" in body
    assert "## Prior findings\n\n- `payments/retry-logging` — fixed: implemented" in body
    assert "- `payments/retry-budget` — still-open:" in body and "- `queue/ordering` — not-verifiable:" in body
    for prior in rereview["prior_items"]:
        assert body.count(f"`{prior['id']}`") == 1, prior["id"]
        assert not any(prior["id"] in comment["body"] for comment in batch["comments"]), prior["id"]
    assert len(batch["comments"]) == 1 and "payments/retry-naming" in batch["comments"][0]["body"]
    approved = copy.deepcopy(rereview)
    approved["summary"]["status"] = "Approved"
    refused(approved, "status-consistency", "Approved over a disputed prior must-fix", needle="payments/retry-budget")
    reposted = copy.deepcopy(rereview)
    reposted["findings"].append(finding(id="payments/retry-budget"))
    refused(reposted, "stable-id", "still-open prior finding re-posted as a new finding", needle="duplicate comment")
    converted = copy.deepcopy(rereview)
    converted["questions"][0]["id"] = "payments/retry-budget"
    composed(converted, "prior finding carried as a question keeps its id")
    requestion = copy.deepcopy(rereview)
    requestion["questions"][0]["id"] = "queue/ordering"
    refused(requestion, "stable-id", "open prior question re-posted as a new question")
    bad = copy.deepcopy(rereview)
    bad["prior_items"][0]["classification"] = "declined"
    refused(bad, "prior-item", "unknown prior classification")
    print("ok re-review: prior accounting in the summary only, disputed blocker holds status, duplicates refused")

    # Retrospective review of a merged target: the Mode line is mandatory and the would-be batch still emits.
    merged = base_composition()
    merged["run"]["merged"] = True
    payload, batch, _ = composed(merged, "retrospective default")
    assert vr_mode(payload) == "**Mode:** Retrospective review of merged pull request; publication disabled." and len(batch["comments"]) == 1
    merged["run"]["publication_authorized"] = True
    payload, _, _ = composed(merged, "retrospective authorized")
    assert vr_mode(payload) == "**Mode:** Retrospective review of merged pull request; publication separately authorized."
    absent = base_composition()
    del absent["run"]["merged"]
    refused(absent, "schema", "packet without merged", needle="run.merged")
    print("ok retrospective: Mode line follows merged and authorization, missing merged refused")

    # File fallback: re-anchoring a rejected line comment on its file moves the complete prose into the body.
    fallback = base_composition()
    fallback["findings"][0]["anchor"] = {"type": "file", "path": "src/payments.ts", "side": "RIGHT"}
    payload, batch, _ = composed(fallback, "file fallback")
    body = payload["summary"]["body"]
    file_fragment = f"anchor [`src/payments.ts`]({BLOB}/src/payments.ts) (file); fix [`src/retry-policy.ts:18`]({BLOB}/src/retry-policy.ts?plain=1#L18)"
    assert "## Findings" not in body and f"## Unanchored findings\n\n{vr_note()}\n\n- [P1] [must-fix] Preserve the idempotency key across retries — {file_fragment}\n\n**[P1] [must-fix]" in body
    assert body.count(file_fragment) == 1 and batch["comments"] == []
    assert "— 1 must-fix finding, 1 open question." in body
    print("ok file fallback: body-carried finding with prose, trailer, and fragment once")

    # Ambiguities and issue coordinates render mechanically.
    ambiguous = base_composition()
    ambiguous["run"]["issues"] = ["acme/payments#9", "acme/payments#123"]
    ambiguous["summary"]["ambiguities"] = [
        {"term": "released contract", "readings": ["the tagged release", "the default branch"], "applied": "reading (a), the safer one."}
    ]
    payload, _, _ = composed(ambiguous, "ambiguities and issues")
    assert "## Ambiguities\n\n- **released contract** — (a) the tagged release; (b) the default branch. Applied: reading (a), the safer one." in payload["summary"]["body"]
    assert "issues=acme/payments#123,acme/payments#9 " in payload["summary"]["trailer"]
    none = base_composition()
    none["run"]["issues"] = []
    payload, _, _ = composed(none, "no issues")
    assert "issues=none " in payload["summary"]["trailer"]
    plain = base_composition()
    del plain["run"]["repository_url"]
    result = run(COMPOSER, json.dumps(plain))
    assert result.returncode == 0, result.stdout
    plain_payload = json.loads(result.stdout)
    assert "repository_url" not in plain_payload["summary"] and "anchor `src/payments.ts:42`; fix `src/retry-policy.ts:18`" in plain_payload["summary"]["body"]
    assert run(VALIDATOR, result.stdout).returncode == 0
    print("ok summary: ambiguities, sorted issues, none, code-span fallback without repository_url")

    unreadable = run(COMPOSER, "{not json")
    assert unreadable.returncode == 2 and "compose_review" in unreadable.stderr, unreadable
    not_object = run(COMPOSER, "[]")
    assert not_object.returncode == 1 and "schema" in not_object.stdout, not_object
    print("ok input: unreadable input exits 2, non-object exits 1")
    return 0


def vr_mode(payload: dict) -> str:
    return payload["summary"]["body"].split("\n\n")[1]


def vr_note() -> str:
    return "The forge's review batch cannot carry a file subject, so each finding below carries its complete prose here."


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"FAIL {error}")
        raise SystemExit(1)
    except OSError as error:
        print(f"test_compose_review: cannot run {COMPOSER}: {error}", file=sys.stderr)
        raise SystemExit(2)
