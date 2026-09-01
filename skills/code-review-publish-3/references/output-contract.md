# Review output contract

The review is **human-readable, agent-actionable, and mechanically correlatable**. Visible prose is authoritative. Hidden trailers speed up re-review and automated addressing but never gate understanding; human comments without trailers receive the same semantic treatment.

## Finding comment

```markdown
**[P1] Preserve the idempotency key across retries**

When the server commits a charge but the response times out, this branch creates
a new key for the retry and can submit a second charge.

**Required change:** Reuse one idempotency key across every attempt for the same
logical charge.

**Source:** Issue #123, acceptance criterion 2.

<!-- finding id=payments/retry-idempotency head=a1b2c3d priority=P1 kind=requirement blocking=true -->
```

The title, trigger, impact, and action must make sense without the trailer. Omit `Source` unless an issue or repository rule materially supports the finding. Use `**Suggestion:**` and `blocking=false` for non-blocking feedback. Do not publish a non-actionable observation.

Stable ids describe the path and defect concept, never a line number. Keep the same id while the same defect survives across heads.

Kinds are compact internal routing aids: `bug`, `security`, `performance`, `maintainability`, or `requirement`. They do not need a visible axis tag.

## Question comment

```markdown
**[Question] Must retries preserve request order?**

The new queue retries at the tail, while existing callers assume FIFO order. The
issue and history do not establish whether reordering is allowed. An answer changes
whether this is a blocking regression.

<!-- question id=queue/retry-order head=a1b2c3d -->
```

Ask only after repository evidence is exhausted. A question is not a finding and has no priority. Whole-change questions belong in the review body rather than on an arbitrary line.

## Replies and prior state

Read replies as prose first. Recognize these visible dispositions when present:

| Disposition | Meaning | Required evidence |
| --- | --- | --- |
| `implemented` | the requested change was made | what changed, commit, verification |
| `already-addressed` | current code already satisfies it | the decisive location or behavior |
| `answered` | a question was resolved without code | the answer and its source |
| `declined` | the author intentionally leaves it unchanged | technical or product rationale |
| `needs-info` | action needs a missing answer | the smallest focused question |
| `blocked` | the change is warranted but cannot proceed | blocker and next step |

An agent reply may carry this optional trailer:

```markdown
**Implemented** in `9f1e0aa` — retries now reuse the logical charge's key.

**Verification:** `pnpm test payments` passes with a timeout-after-commit case.

<!-- reply to=payments/retry-idempotency disposition=implemented head=9f1e0aa -->
```

Never require or add a trailer on a human's behalf. Verify replies against current code. A reply states intent; it does not prove outcome.

On re-review, classify each prior item as `fixed`, `accepted`, `obsolete`, `still-open`, or `not-verifiable`. Resolve the first three. `Accepted` means the rereviewer verified that technical evidence makes the finding fail the rubric, or an authorized human explicitly accepted the residual risk; the author's `declined` disposition alone is not acceptance. Keep the other states open, replying on the existing thread rather than creating a duplicate. A declined item that remains after one verified re-review becomes `disputed`; list it for a person and stop re-posting it.

## Status

Derive one semantic status after findings, questions, coverage, and prior state are complete:

1. `Changes Requested` when any blocking finding is unsettled, including a disputed or not-verifiable blocker.
2. `Incomplete` when no blocker is known but material coverage or verification did not finish.
3. `Needs Information` when coverage is complete and an unanswered question could change the verdict.
4. `Approved` otherwise. Non-blocking suggestions do not prevent approval.

Authorization changes only the forge event, never the semantic status:

| Status | Authorized gating event | Default event |
| --- | --- | --- |
| Changes Requested | `REQUEST_CHANGES` | `COMMENT` |
| Incomplete | none | `COMMENT` |
| Needs Information | none | `COMMENT` |
| Approved | `APPROVE` | `COMMENT` |

Always write the semantic status in the body. Add `(advisory)` to `Changes Requested` or `Approved` when using `COMMENT`.

## Summary body

Keep the body useful without duplicating inline comments:

```markdown
**Changes Requested (advisory)** — 1 required change.

**Intent:** Add retries for charge submission without changing payment semantics.

**Issue fit:** Partial — retry availability is implemented, but acceptance criterion 2's idempotency guarantee remains open.

**Coverage:** Complete merge-base diff reviewed; payment callers and focused tests inspected.

**Reviewed:** `a1b2c3d` against merge-base `d4e5f6a`.

## Findings

- [P1] Preserve the idempotency key across retries — `src/payments.ts:42`

<!-- review-run head=a1b2c3d base-ref=main base-sha=b2c3d4e merge-base=d4e5f6a rubric=codex-81de4f2 issues=acme/payments#123 coverage=complete -->
```

Trailer fields are single ASCII tokens separated by spaces. Represent issues as sorted, comma-separated `owner/repo#number` coordinates, or `issues=none`; never put spaces in the value. The `file:line` finding index remains the durable summary reference. Return forge URLs to the caller after publication instead of editing the review body.

Include only non-empty conditional sections: `Open questions`, `Disputed`, `Prior findings`, and `Coverage gaps`. A clean review says so briefly. Do not add scores, effort estimates, generic praise, empty security/test sections, or repeated finding prose.

## Coverage

Coverage is `complete` only when every changed file is reviewed or deliberately ignored with a reason, every risk-directed check has an evidence-backed outcome, and every required fetch or verification completed.

An incomplete review may publish verified findings already found, but its body must identify the uncovered files or checks and cannot claim the change is clean.

## Publication invariants

- Re-fetch the head immediately before writing; a stale or unreadable head aborts all publication.
- Submit one review body and all new inline comments in one forge-native review call.
- Inline anchors use the correct diff side: `RIGHT` for added/current lines and `LEFT` for deleted lines.
- If the forge conclusively rejects a batch before creating a review because one comment is malformed, repair or omit only that comment, confirm no review exists, and retry the batch at most once.
- A general comment is a fallback only when a non-gating native review is unavailable or refused.
- Re-read the target after an ambiguous write result before one retry.
- Store the run trailer in the summary and finding/question trailers in raw comment bodies.

On GitHub, the batched shape is:

```json
{
  "commit_id": "<reviewed head>",
  "event": "COMMENT",
  "body": "<summary>",
  "comments": [
    {
      "path": "src/payments.ts",
      "line": 42,
      "side": "RIGHT",
      "body": "<finding>"
    }
  ]
}
```

Post it with `gh api --method POST repos/{owner}/{repo}/pulls/<pr>/reviews --input <payload>`. Use the equivalent forge-native operation elsewhere.
