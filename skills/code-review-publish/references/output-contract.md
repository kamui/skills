# Review output contract

The review is **human-readable, agent-actionable, and mechanically correlatable**. Visible prose is authoritative. Hidden trailers speed up re-review and automated addressing but never gate understanding; human comments without trailers receive the same semantic treatment.

## Finding comment

```markdown
**[P1] [must-fix] Preserve the idempotency key across retries**

**Triggers when:** The server commits a charge but its response times out and the
client retries.

**Impact:** The retry uses a new idempotency key and can submit a second charge.

**Change:** In `src/retry-policy.ts`, reuse one idempotency key across every attempt
for the same logical charge.

**Source:** Issue #123, acceptance criterion 2.

<!-- finding id=payments/retry-idempotency head=a1b2c3d priority=P1 action=must-fix blocking=true kind=requirement fix=src/retry-policy.ts:18 -->
```

The title, trigger, impact, and change must make sense without the trailer. Omit `Source` unless an issue or repository rule materially supports the finding. The two action forms are:

- `[must-fix]`, `action=must-fix`, and `blocking=true` for an outcome required before merge.
- `[consider]`, `action=consider`, and `blocking=false` for optional feedback. Append the exact sentence `Closing this without action is a correct response.` after `Change`.

Priority and action are separate fields. P0 is inherently `must-fix`; otherwise do not derive action mechanically from priority. In particular, P2/P3 do not mean optional. Do not publish a non-actionable observation.

The forge anchor and the repair site may differ. The inline API fields identify the changed-line `anchor`; optional trailer field `fix=<path>:<line>` identifies where the author or agent should edit. Omit `fix` when it is the anchor. Name a different fix site in the visible `Change` text as well, because the trailer is never authoritative.

Stable ids describe the path and defect concept, never a line number. Keep the same id while the same defect survives across heads.

Kinds are compact internal routing aids: `bug`, `security`, `performance`, `maintainability`, or `requirement`. They do not need a visible axis tag.

## Question comment

```markdown
**[Question] Must retries preserve request order?**

**Evidence:** The new queue retries at the tail, while existing callers consume it
as FIFO. The issue, tests, and history do not establish whether reordering is allowed.

**Why it matters:** The answer determines whether this is a merge-blocking regression.

**Next step:** Confirm whether retry order is part of the contract; do not change
code solely for this question.

<!-- question id=queue/retry-order head=a1b2c3d action=question -->
```

Ask only after repository evidence is exhausted. A question is not a finding and has no priority. Whole-change questions belong in the review body rather than on an arbitrary line.

When a `plausible` candidate becomes a question, retain its stable concept id and change only the trailer type from `finding` to `question`. This keeps later answers and any code-decided finding correlated across runs.

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

1. `Changes Requested` when any `must-fix` finding is unsettled, including a disputed or not-verifiable blocker.
2. `Incomplete` when no blocker is known but material coverage or verification did not finish.
3. `Needs Information` when coverage is complete and an unanswered question could change the verdict.
4. `Approved` otherwise. `consider` findings do not prevent approval.

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
**Changes Requested (advisory)** — 1 must-fix finding.

**Intent:** Add retries for charge submission without changing payment semantics.

**Issue fit:** Partial — retry availability is implemented, but acceptance criterion 2's idempotency guarantee remains open.

**Coverage:** Complete merge-base diff reviewed; payment callers and focused tests inspected.

**Reviewed:** `a1b2c3d` against merge-base `d4e5f6a`.

## Findings

- [P1] [must-fix] Preserve the idempotency key across retries — anchor `src/payments.ts:42`; fix `src/retry-policy.ts:18`

<!-- review-run head=a1b2c3d base-ref=main base-sha=b2c3d4e merge-base=d4e5f6a workflow=v5-2 context=91d34a2f4c869867167f0b31da7c207f4528e12e3d1ef4f107a5eabb4c18718e issues=acme/payments#123 coverage=complete -->
```

`workflow=v5-2` versions this package's review behavior. Increment it whenever admission, verification, rendering, or state semantics change. Compute `context` with [`../scripts/context_fingerprint.py`](../scripts/context_fingerprint.py), supplying JSON objects `pr`, `issues`, `specs`, and `guidance` from the exact reviewed inputs. Each issue includes `coordinate`, `title`, `body`, and comments with `id`, `author`, timestamps, and `body`; each guidance entry has `path` and full `blob_sha`. A spec uses its URL or coordinate as `identity`; the helper derives a content identity for inline text when it is omitted. The helper normalizes order and prints the full SHA-256. Recompute it rather than trusting PR-supplied metadata.

Trailer fields are single ASCII tokens separated by spaces. Percent-encode spaces and percent signs inside coordinate values. Represent issues as sorted, comma-separated `owner/repo#number` coordinates, or `issues=none`; never put literal spaces in the value. The anchor coordinate is the durable summary reference: `path:start-end` for a line anchor or `path` plus the visible `(file)` marker for a file anchor. Add the fix coordinate when it differs. Return forge URLs to the caller after publication instead of editing the review body.

Keep the ordinary summary near 200 words before conditional sections. Include only non-empty conditional sections: `Open questions`, `Unanchored findings`, `Disputed`, `Prior findings`, and `Coverage gaps`. An unanchored finding contains its complete finding-comment prose plus the decisive evidence coordinate and optional fix coordinate. A file-anchored finding also goes in `Unanchored findings` when the forge cannot represent a file subject inside the same review batch; keep its visible `(file)` coordinate so this transport fallback is not mistaken for missing evidence. A clean review says so briefly. Do not narrate dropped candidates or add scores, effort estimates, generic praise, empty security/test sections, or repeated finding prose.

## Coverage

Coverage is `complete` only when every changed file is reviewed or deliberately ignored with a reason, every risk-directed check has an evidence-backed outcome, and every required fetch or verification completed.

An incomplete review may publish verified findings already found, but its body must identify the uncovered files or checks and cannot claim the change is clean.

## Publication invariants

- Re-fetch the head immediately before writing; a stale or unreadable head aborts all publication.
- Submit one review body and all new line comments in one forge-native review call. Include file-level comments there only when that batch endpoint documents file subjects; otherwise move their complete prose into the body before the call.
- Inline anchors use the correct diff side: `RIGHT` for added/current lines and `LEFT` for deleted lines.
- If the forge conclusively rejects a batch before creating a review because one comment is malformed, repair its anchor. If no valid anchor exists, move its complete visible finding prose into an `Unanchored findings` body section with the decisive evidence coordinate and optional fix coordinate. Recompute counts, status, index entries, and the complete payload; confirm no review exists; then retry at most once. Never drop a verified finding to make a batch succeed.
- A general comment is a fallback only when a non-gating native review is unavailable or refused.
- Re-read the target after an ambiguous write result before one retry.
- Store the run trailer in the summary and finding/question trailers in raw comment bodies.
- Before writing, confirm that the visible priority, action, change, and fix site agree with the trailer and forge anchor. Repair a mismatch; if a consistent valid inline form is impossible, move the complete finding to `Unanchored findings`. Never choose hidden metadata over visible prose or omit a verified finding.

On GitHub, the `Create a review for a pull request` batch documents line comments but not file subjects. Keep file-anchored findings in `Unanchored findings` rather than making a separate write through the review-comment endpoint or inventing an unrelated line. The one-call batch shape is:

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

Post it with `gh api --method POST repos/{owner}/{repo}/pulls/<pr>/reviews --input <payload>`. GitHub's separate review-comment endpoint documents `subject_type: "file"`, but using it would break this workflow's atomic one-review publication invariant. Use the equivalent forge-native operation elsewhere.
