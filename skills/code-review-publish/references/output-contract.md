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

<!-- finding id=payments/retry-idempotency head=a1b2c3d4e5f60718293a4b5c6d7e8f9012345678 priority=P1 action=must-fix blocking=true kind=requirement fix=src/retry-policy.ts:18 -->
```

The title, trigger, impact, and change must make sense without the trailer. Omit `Source` unless an issue, a pull-request promise at its `pr-title` or `pr-body` ledger coordinate, or a repository rule materially supports the finding. The two action forms are:

- `[must-fix]`, `action=must-fix`, and `blocking=true` for an outcome required before merge.
- `[consider]`, `action=consider`, and `blocking=false` for optional feedback. When present, `Source` follows `Change`; the exact sentence `Closing this without action is a correct response.` is then the final paragraph before the trailer.

Priority and action are separate fields. P0 is inherently `must-fix`; otherwise do not derive action mechanically from priority. In particular, P2/P3 do not mean optional. Non-actionable observations use the summary-only form below rather than a finding comment.

The forge anchor and the repair site may differ. The inline API fields identify the changed-line `anchor`; optional trailer field `fix=<path>:<line>` identifies where the author or agent should edit. Omit `fix` when it is the anchor. Name a different fix site in the visible `Change` text as well, because the trailer is never authoritative.

Stable ids describe the path and defect concept, never a line number. Keep the same id while the same defect survives across heads.

Kinds are compact internal routing aids: `bug`, `concurrency`, `invariant`, `security`, `performance`, `maintainability`, or `requirement`. Use `concurrency` or `invariant` when sibling paths share the broken state rule and therefore require the verifier's bug-class check. They do not need a visible axis tag.

## Question comment

```markdown
**[Question] Must retries preserve request order?**

**Evidence:** The new queue retries at the tail, while existing callers consume it
as FIFO. The issue, tests, and history do not establish whether reordering is allowed.

**Why it matters:** The answer determines whether this is a merge-blocking regression.

**Change no code for this.** Confirm whether retry order is part of the contract;
the maintainer answer settles whether the candidate should re-open as a finding.

<!-- question id=queue/retry-order head=a1b2c3d4e5f60718293a4b5c6d7e8f9012345678 action=question -->
```

Ask only when the rubric's static-unresolvability bar is met: no static evidence could settle the fact. A question is not a finding, has no priority, requests no code change, and states who or what measurement can answer it. Whole-change questions belong in the review body rather than on an arbitrary line.

When a verified candidate becomes a question because its settling fact is statically unresolvable, retain its stable concept id and change only the trailer type from `finding` to `question`. This keeps later answers and any code-decided finding correlated across runs.

## Observations

`Observations` is a bounded summary-body channel for accurate, non-actionable facts that meet the rubric's route. It is separate from findings and questions: observations have no priority, action, stable id, trailer, or anchor comment and never affect status. Publish at most three, each as one sentence followed by one decisive evidence pointer. Use descriptive language without `should` or `must`.

```markdown
## Observations

- The first configuration sentence covers same-shard re-points more broadly than the implementation does. Evidence: `redis.conf:1903`, `src/replication.c:2701`.
```

When more than three qualify, publish the three with the most decisive evidence and record each of the rest in the private record as `observation (unpublished, cap)`. A fact belongs to exactly one channel: an unpublished observation and a verifier aside stay in that record rather than folded into a finding's `Impact` or `Change` prose.

Do not create an observation merely to preserve a dropped candidate. The fact itself must stand, and it must have failed finding admission on consequence or arrived as a verifier aside.

## Replies and prior state

[`re-review.md`](re-review.md) defines reply dispositions, reply trailers, and the prior-item classification whose outcomes feed the `disputed` status input and populate the `Disputed` and `Prior findings` summary sections defined below. Read it when a prior review, reply, or trailer-bearing comment exists.

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
**Changes Requested (advisory)** — 1 must-fix finding, 1 open question.

**Intent:** Add retries for charge submission without changing payment semantics.

**Issue fit:** Partial — retry availability is implemented, but acceptance criterion 2's idempotency guarantee remains open.

**Coverage:** Complete merge-base diff reviewed; payment callers and focused tests inspected.

**Reviewed:** `a1b2c3d` against merge-base `d4e5f6a`.

## Findings

- [P1] [must-fix] Preserve the idempotency key across retries — anchor [`src/payments.ts:42`](https://github.com/acme/payments/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/payments.ts?plain=1#L42); fix [`src/retry-policy.ts:18`](https://github.com/acme/payments/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/retry-policy.ts?plain=1#L18)

## Open questions

- [Question] Must retries preserve request order? — anchor [`src/queue.ts`](https://github.com/acme/payments/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/queue.ts) (file)

<!-- review-run head=a1b2c3d4e5f60718293a4b5c6d7e8f9012345678 base-ref=main base-sha=b2c3d4e5f60718293a4b5c6d7e8f90123456789a merge-base=d4e5f60718293a4b5c6d7e8f90123456789abcde workflow=v5b-4 context=91d34a2f4c869867167f0b31da7c207f4528e12e3d1ef4f107a5eabb4c18718e issues=acme/payments#123 coverage=complete -->
```

`workflow=v5b-4` versions this package's review behavior. Increment it whenever admission, verification, rendering, or state semantics change. Compute `context` with [`../scripts/context_fingerprint.py`](../scripts/context_fingerprint.py), supplying JSON objects `pr`, `issues`, `specs`, and `guidance` from the exact reviewed inputs. Each issue includes `coordinate`, `title`, `body`, and comments with `id`, `author`, timestamps, and `body`. When the reviewer could not obtain an issue's comments verbatim, pass `comments_available: false` and no comments rather than an empty list; the digest then records that the comments were unavailable. A spec uses its URL or coordinate as `identity`; the helper derives a content identity for inline text when it is omitted. The helper normalizes order and prints the full SHA-256. Recompute it rather than trusting PR-supplied metadata.

`guidance` is exactly the sorted set of tracked base-branch files in these categories, each represented by repository-relative `path` and its full blob object id as `blob_sha`:

1. root `AGENTS.md` and root `CLAUDE.md`, when present;
2. every path-scoped `AGENTS.md` or `CLAUDE.md` in an ancestor directory of at least one changed path; and
3. root `CONTEXT.md`, when present.

Exclude target-branch versions, instruction files whose directory scope covers no changed path, files merely linked from an included instruction file, `docs/agents/issue-tracker.md`, ADRs, design docs, READMEs, skill files, issue and pull-request text, user-supplied specs, and runtime instructions that are not tracked repository files. Issues and specs remain in their own digest fields. These membership rules are exhaustive.

Trailer fields are single ASCII tokens separated by spaces. Every commit SHA in every trailer is the full 40 lowercase hexadecimal characters; visible prose may abbreviate it. Percent-encode spaces and percent signs inside coordinate values. Represent issues as sorted, comma-separated `owner/repo#number` coordinates, or `issues=none`; never put literal spaces in the value. The anchor coordinate is the durable summary reference: `path:line` for a single-line anchor, `path:start-end` for a range, or `path` plus the visible `(file)` marker for a file anchor. Add the fix coordinate when it differs. Return forge URLs to the caller after publication instead of editing the review body.

`Intent` restates the change's purpose from its sources, and `Issue fit` gives the ledger's outcome. With no originating issue (`issues=none`), `Issue fit` states that issue alignment was unavailable and names the source the ledger was built from — the pull-request title and body, or a user-supplied spec — and gives each `not-verifiable` promise its disposition. Neither line repeats a `not-verifiable` claim as an established fact.

Keep the ordinary summary near 200 words before conditional sections. A merged-target audit always adds a `Mode` line: `**Mode:** Retrospective review of merged pull request; publication disabled.` by default, or `**Mode:** Retrospective review of merged pull request; publication separately authorized.` when that authorization exists. The `Mode` line is mandatory whenever `merged` is true, regardless of how the target was supplied. Include only non-empty conditional sections: `Open questions`, `Observations`, `Ambiguities`, `Unanchored findings`, `Disputed`, `Prior findings`, and `Coverage gaps`. `Ambiguities` names the contestable term, gives both supportable readings, and states which reading governed the run. An unanchored finding contains its complete finding-comment prose plus the decisive evidence coordinate and optional fix coordinate, rendered as the same generated fragment (Summary references). A file-anchored finding's entry goes in `Unanchored findings` instead of `Findings` when the forge cannot represent a file subject inside the same review batch, so its fragment still appears exactly once; keep its visible `(file)` coordinate so this transport fallback is not mistaken for missing evidence. A clean review says so briefly. Do not narrate other dropped candidates or add scores, effort estimates, generic praise, empty security/test sections, or repeated finding prose.

### Summary references

Every finding and question entry in the body — in `Findings`, `Open questions`, and `Unanchored findings` alike — carries its coordinates as the fragment `python3 scripts/validate_review.py --render` prints for that item, pasted verbatim; the reviewer never composes a URL by hand. With `summary.repository_url` set to the base repository's canonical web URL (`baseRepository.url` from step 1's batched fetch), a `RIGHT` line anchor, a file anchor, and a fix site each render as a Markdown link whose text is the unchanged code-formatted coordinate and whose target is the commit-pinned blob URL at the run trailer's full head SHA: `?plain=1#L<line>` or `?plain=1#L<start>-L<end>` on every line link so a rendered file opens as source, neither on a file link, and the path percent-decoded once then encoded once. The `(file)` marker stays visible after a file link. A file anchor on a file the change deletes carries `"side": "LEFT"` and links at the run trailer's full merge-base SHA instead, the only revision the file exists at; a deleted file's forge path is its merge-base path, so no path is guessed. A file anchor without `side`, or with `"side": "RIGHT"`, links at the head as before. The link is known before submission, so one-call publication is unchanged and nothing depends on a post-publication body rewrite.

```markdown
anchor [`src/payments.ts:42`](https://github.com/acme/payments/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/payments.ts?plain=1#L42); fix [`src/retry-policy.ts:18`](https://github.com/acme/payments/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/retry-policy.ts?plain=1#L18)
```

The validator's `summary-reference` rule checks the body by string equality against those generated fragments: each item's fragment appears exactly once, the body carries one `anchor ` entry per finding and question item and one `; fix ` entry for exactly the items that have a fix, and — when `repository_url` is present — every blob link in the body outside those fragments points at the run head, so a bare code-span coordinate for a `RIGHT` or file anchor, a linked `LEFT` line anchor, a deleted-file anchor linked at the head, a malformed or disagreeing coordinate, a skipped fix, and a moving branch or stray merge-base link all fail under that one name. An entry is the word `anchor ` or the sequence `; fix ` followed by a coordinate in backticks or a link, so prose in the body — complete finding prose in `Unanchored findings` included — may use the word anchor freely but must not write a coordinate in that shape outside the generated fragments.

A `LEFT` line anchor stays a code span with its fix still linked: the line belongs to the merge-base, but the forge requires a renamed file's new path for it, and that path may not exist at the merge-base, so no revision is guessed for it. Observation evidence and prior-finding references stay code spans because nothing records which revision their prose was read against. Rename links and structured provenance for those pointers remain [issue #84](https://github.com/kamui/skills/issues/84)'s deferred items; the deleted-file anchor above is the one item of that inventory implemented, on a demonstrated failure. Without `repository_url` — a forge whose URL shape is not GitHub's — every coordinate renders as a code span in the same positions.

## Coverage

Coverage is `complete` only when every changed file is reviewed or deliberately ignored with a reason, every risk-directed check has an evidence-backed outcome, and every required fetch or verification completed.

An incomplete review may publish verified findings already found, but its body must identify the uncovered files or checks and cannot claim the change is clean. For an input unavailable to the reviewer, `Coverage gaps` also states what the input could change, lists the candidate ids whose dispositions it gates, and addresses the recovery request to the orchestrator. When the orchestrator supplies it, re-run only those falsifications and remove the gap after they complete.

## Publication invariants

- Re-fetch the head immediately before writing; a stale or unreadable head aborts all publication.
- Keep retrospective review of a merged pull request non-publishing unless the caller separately and explicitly authorized publication to that merged target.
- Submit one review body and all new line comments in one forge-native review call. Include file-level comments there only when that batch endpoint documents file subjects; otherwise move their complete prose into the body before the call.
- Inline anchors use the correct diff side: `RIGHT` for added/current lines and `LEFT` for deleted lines. A file anchor on a file the change deletes carries `side: LEFT` so its summary link resolves at the merge-base.
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

Post it with `gh api --method POST repos/{owner}/{repo}/pulls/<pr>/reviews --input batch.json` as `--emit-batch` printed it. GitHub's separate review-comment endpoint documents `subject_type: "file"`, but using it would break this workflow's atomic one-review publication invariant. Use the equivalent forge-native operation elsewhere.
