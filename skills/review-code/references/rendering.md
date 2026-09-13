# Rendering the review record

Load at `SKILL.md` step 5. `review-record.md` owns fields, eligibility, status, coverage, and identity; this reference owns their visible syntax and repair.

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

## Observations

```markdown
## Observations

- The first configuration sentence covers same-shard re-points more broadly than the implementation does. Evidence: `redis.conf:1903`, `src/replication.c:2701`.
```

## Summary body

Keep the body useful without duplicating inline comments:

```markdown
**Changes Requested (advisory)** — 1 must-fix finding, 1 open question.

**Intent:** Add retries for charge submission without changing payment semantics.

**Issue fit:** Partial — retry availability is implemented, but acceptance criterion 2's idempotency guarantee remains open.

**Coverage:** Complete merge-base diff reviewed; payment callers inspected; focused `retry-policy` test run once at the head: pass.

**Reviewed:** `a1b2c3d` against merge-base `d4e5f6a`.

## Findings

- [P1] [must-fix] Preserve the idempotency key across retries — anchor [`src/payments.ts:42`](https://github.com/acme/payments/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/payments.ts?plain=1#L42); fix [`src/retry-policy.ts:18`](https://github.com/acme/payments/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/retry-policy.ts?plain=1#L18)

## Open questions

- [Question] Must retries preserve request order? — anchor [`src/queue.ts`](https://github.com/acme/payments/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/queue.ts) (file)

<!-- review-run head=a1b2c3d4e5f60718293a4b5c6d7e8f9012345678 base-ref=main base-sha=b2c3d4e5f60718293a4b5c6d7e8f90123456789a merge-base=d4e5f60718293a4b5c6d7e8f90123456789abcde workflow=v5b-17 context=91d34a2f4c869867167f0b31da7c207f4528e12e3d1ef4f107a5eabb4c18718e issues=acme/payments#123 coverage=complete -->
```

Trailer fields are single ASCII tokens separated by spaces. Every commit SHA in every trailer is the full 40 lowercase hexadecimal characters; visible prose may abbreviate it. Percent-encode spaces and percent signs inside coordinate values. Represent issues as sorted, comma-separated `owner/repo#number` coordinates, or `issues=none`; never put literal spaces in the value. The anchor coordinate is the durable summary reference: `path:line` for a single-line anchor, `path:start-end` for a range, or `path` plus the visible `(file)` marker for a file anchor. Add the fix coordinate when it differs. The caller reports forge URLs after publication without editing the review body.

`Intent` restates the change's purpose from its sources, and `Issue fit` gives the ledger's outcome. With no originating issue (`issues=none`), `Issue fit` states that issue alignment was unavailable and names the source the ledger was built from — the pull-request title and body, or a user-supplied spec — and gives each `not-verifiable` promise its disposition. When the repository workflow requires an issue and none resolves, `Issue fit` explicitly says the ledger came from the pull-request text and the missing issue renders as a whole-change `[Question]` in `Open questions`. Neither line repeats a `not-verifiable` claim as an established fact.

The first paragraph is the status in bold, then an em dash and the counts the items imply: must-fix findings, `consider` findings, open questions, prior items still open, and disputed prior findings, each named only when non-zero, or `no findings` for a clean review; a delta re-review appends the range `re-review.md` requires. Keep the ordinary summary near 200 words before conditional sections. A merged-target audit always adds a `Mode` line after that paragraph: `**Mode:** Retrospective review of merged pull request; publication disabled.` by default, or `**Mode:** Retrospective review of merged pull request; publication separately authorized.` when that authorization exists. The `Mode` line is mandatory whenever `merged` is true, regardless of how the target was supplied. Include only non-empty conditional sections, in this order after `Findings`: `Open questions`, `Observations`, `Ambiguities`, `Unanchored findings`, `Disputed`, `Prior findings`, and `Coverage gaps`. `Ambiguities` names the contestable term, gives both supportable readings, and states which reading governed the run. `Disputed` lists each disputed prior item and `Prior findings` every other prior item, each as its stable id in a code span, its classification, and one line of evidence, so every prior item appears in exactly one of the two. An unanchored finding contains its complete finding-comment prose plus the decisive evidence coordinate and optional fix coordinate, rendered as the same generated fragment (Summary references), followed by its trailer so the body-carried item stays correlatable across heads like an inline comment. A file-anchored finding's entry goes in `Unanchored findings` instead of `Findings` when the forge cannot represent a file subject inside the same review batch, so its fragment still appears exactly once; keep its visible `(file)` coordinate so this transport fallback is not mistaken for missing evidence. A file-anchored question renders the same way under `Open questions`: its index entry, its complete prose, and its trailer. A clean review says so briefly. Do not narrate other dropped candidates or add scores, effort estimates, generic praise, empty security/test sections, or repeated finding prose.

### Summary references

Every finding and question entry in the body — in `Findings`, `Open questions`, and `Unanchored findings` alike — carries its coordinates as the fragment `python3 scripts/validate_review.py --render` prints for that item, inserted verbatim by the composer; the reviewer never composes a URL by hand. With `summary.repository_url` set to the base repository's canonical web URL (`baseRepository.url` from step 1's batched fetch), a `RIGHT` line anchor, a file anchor, and a fix site each render as a Markdown link whose text is the unchanged code-formatted coordinate and whose target is the commit-pinned blob URL at the run trailer's full head SHA: `?plain=1#L<line>` or `?plain=1#L<start>-L<end>` on every line link so a rendered file opens as source, neither on a file link, and the path percent-decoded once then encoded once. The `(file)` marker stays visible after a file link. A file anchor on a file the change deletes carries `"side": "LEFT"` and links at the run trailer's full merge-base SHA instead, the only revision the file exists at; a deleted file's forge path is its merge-base path, so no path is guessed. A file anchor without `side`, or with `"side": "RIGHT"`, links at the head as before. Derive `LEFT` and the pre-image path from the full pinned merge-base changed-file manifest (`D`), never from a filename or the delta manifest. If that evidence cannot establish the correct path/revision, use `"side": "UNKNOWN"`: the renderer retains ``anchor `<path>` (file)`` as an unlinked coordinate, and the item explains the missing evidence. `UNKNOWN` is file-only. The file-anchor fields remain `type`, `path`, and optional `side`; a per-item revision override is invalid. Legacy anchors without `side` retain their head semantics, so the caller must propagate known deletion or unknown provenance before rendering. The link is known before submission, so one-call publication is unchanged and nothing depends on a post-publication body rewrite.

```markdown
anchor [`src/payments.ts:42`](https://github.com/acme/payments/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/payments.ts?plain=1#L42); fix [`src/retry-policy.ts:18`](https://github.com/acme/payments/blob/a1b2c3d4e5f60718293a4b5c6d7e8f9012345678/src/retry-policy.ts?plain=1#L18)
```

The validator's `summary-reference` rule checks the body by string equality against those generated fragments: each item's fragment appears exactly once, the body carries one `anchor ` entry per finding and question item and one `; fix ` entry for exactly the items that have a fix, and — when `repository_url` is present — every blob link in the body outside those fragments points at the run head, so a bare code-span coordinate for a `RIGHT` or file anchor, a linked `LEFT` line anchor, a deleted-file anchor linked at the head, a malformed or disagreeing coordinate, a skipped fix, and a moving branch or stray merge-base link all fail under that one name. An entry is the word `anchor ` or the sequence `; fix ` followed by a coordinate in backticks or a link, so prose in the body — complete finding prose in `Unanchored findings` included — may use the word anchor freely but must not write a coordinate in that shape outside the generated fragments.

A `LEFT` line anchor stays a code span with its fix still linked: the line belongs to the merge-base, but the forge requires a renamed file's new path for it, and that path may not exist at the merge-base, so no revision is guessed for it. Observation evidence and prior-finding references stay code spans because nothing records which revision their prose was read against. Rename links and structured provenance for those pointers remain deferred until a separate demonstrated case and bounded scope justify them; the deleted-file anchor above is implemented on a demonstrated failure. Without `repository_url` — a forge whose URL shape is not GitHub's — every coordinate renders as a code span in the same positions.

### Composition

With `--store`, the composer checks the `review-context-store/1` envelope produced by `review_context.py`, then reads identity and the full manifest from its `context` object. Line and file anchors name the manifest's `path`; a rename's `old_path` is provenance only. Deleted lines use `LEFT`, added lines use `RIGHT`, and modified or renamed lines may use either side at the manifest path. The composer checks those supplied choices without choosing a side or establishing hunk membership.

`python3 scripts/compose_review.py --store <store> composition.json > payload.json` renders every repetitive syntax this contract states from the reviewer's authoritative fields and authored prose, validates the result with `validate_review.py`, and prints the validator payload; `validate_review.py --emit-batch` then projects that payload unchanged, and `--render` prints its fragments for the final report. The composition input carries, for each finding, its stable `id`, `title`, `priority`, `action`, `kind`, `anchor` (a file anchor with an explicit `side`), optional `fix` site (`path`, `start_line`, optional `end_line`, the path raw as the manifest lists it), and the prose of `trigger`, `impact`, `change`, and optional `source`; for each question, its `id`, `title`, `anchor`, and the prose of `evidence`, `why_it_matters`, and `answer`; for each observation, its `fact` and `evidence`; for each prior item, its `id`, `classification`, `action`, and one-line `note`; for the run, the pinned identity, `context` digest, issue list, `coverage`, `merged` with any separate publication authorization, `repository_url`, and `prior_head` on a delta re-review; and for the summary, its `status`, the `intent`, `issue_fit`, and `coverage` prose, `ambiguities`, and `coverage_gaps`. Composition always returns the advisory record and refuses a `summary.gating` input; the publisher selects any authorized gating event through `--emit-batch --event`. The script's docstring is the exact schema.

Code renders from those fields: the title line and its tags, the labelled fields in order, the permission sentence, the question framing, each trailer with the fix coordinate percent-encoded, the status paragraph with its counts and `(advisory)` marker, the `Mode` line, the delta range, the `Reviewed` line, every index entry with its generated fragment, the body-carried prose and trailer of file-anchored items, the conditional sections, and the run trailer. Prose is copied byte for byte, code and suggestion blocks included; nothing is truncated, reordered, or dropped. The reviewer still decides every semantic field: admission, priority, action, kind, stable id, the anchor's side from the pinned manifest, the fix site, question and observation eligibility, which three observations publish when more qualify, prior-item classification, coverage, and status. The composer refuses, naming the field, a contradiction those fields expose or a judgment they omit — a `blocking` that disagrees with `action`, a P0 `consider`, a duplicate stable id, a prior item repeated as a new item of the same type, a file anchor without `side`, a `fix` outside the anchor's file that the `change` prose does not name, a status that contradicts an unsettled must-fix item or incomplete coverage or lacks the question it claims, incomplete coverage without a named gap, a fourth observation, a field label outside code inside a field's prose — and never resolves one; with `--store` it also refuses an anchor the pinned merge-base manifest or run identity contradicts. A non-zero exit prints violations, each at its composition-input location, and no payload. Prior items are accounted for in `Disputed` and `Prior findings` only; their thread replies are drafted and posted under `re-review.md` and the publication procedure and never enter the batch of new comments.


## Repair a rejected comment

When the caller reports a conclusive malformed-comment rejection, repair its anchor. If no valid anchor exists, move its complete visible finding prose into an `Unanchored findings` body section with the decisive evidence coordinate and optional fix coordinate. Change the composition input, re-run the composer to recompute counts, status, indexes, and the validated payload, then re-emit the batch, return the repaired record to the caller for its publication checks. Never drop a verified finding to make a batch succeed.

Before returning, confirm that the visible priority, action, change, and fix site agree with the trailer and forge anchor. Repair a mismatch; if a consistent valid inline form is impossible, move the complete finding to `Unanchored findings`. Never choose hidden metadata over visible prose or omit a verified finding.
