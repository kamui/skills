# review-code simplification: staged draft

The artifact-savings epic (#340) made review-code's mechanics cheaper to author, but the skill stayed large: 88 KB of runtime prose, 25 KB always loaded, about 60K words of non-test Python, and a 53K-word history installed with it. Its combined measurement (#347) found no overall cost or latency saving, more finalizer repairs under the stricter preconditions, and verifier returns still inline under Claude Code. This stage cuts the machinery instead of automating it, and keeps what makes the skill better than a plain review prompt.

## What stays

1. **Review against intent.** A requirements ledger from issues, specs, and the change description. An omission in unchanged code still counts.
2. **A high admission bar, enforced by falsification.** A code defect must be introduced or worsened here; an explicit requirement can make an unchanged omission this change's responsibility. Both need a proven trigger and consequence and an attainable remedy. Priority is separate from action.
3. **Independent verification where a wrong call is costly.** A fresh-context verifier gets claims and evidence only. Verification is mandatory for `must-fix` and the risk areas, a safety-premise attack runs on high-risk no-blocker conclusions, and the allowance is one batch plus one follow-up.
4. **Honest completeness.** A complete pinned diff with truncation recovery, per-file coverage, and status precedence `Changes Requested` > `Incomplete` > `Needs Information` > `Approved`.
5. **Continuity.** Stable ids, classified prior items, disputes, and a duplicate-review shortcut.
6. **The model judges and scripts do the mechanics.**

## Decisions

| Decision | Effect |
| --- | --- |
| One record shape; no `profile` input | Every run writes `record.json`, `report.md`, `payload.json`, `batch.json`. `fragments.md` has no consumer and goes. `compose_review.py`, `validate_review.py` and `finalize_review.py` merge into one `render_review.py`, keeping `--check` and `--emit-batch --event`, the only entry `review-code-publish` uses. |
| Continuation is a re-review | A local run takes `prior_record` and writes a new, complete record in a new directory linked to it. The primary rechecks fixed findings itself; new mandatory candidates, materially changed mandatory claims and required safety premises still need verification within the carried allowance. Addenda, chain walking, replacement records, the version-1 mapping and `continue_review.py` go. See Prior-record check. |
| PR fetch moves into a script | `forge_packet.py fetch` runs the GraphQL root and continuation queries through `gh` and normalizes them, a recorded departure like `review-bot`'s. |
| Inline verifier returns only | The file transport, `--inline-fallback` and the transport choice go. The builder creates a unique `bundle_id` for each immutable bundle, saves it in the manifest and prints it in the brief. The worker echoes it without computing a hash. Accounting checks it alongside the existing bundle integrity, role, ID and evidence checks. Rebuilding a bundle creates a new ID even when the batch name and candidate IDs are unchanged. |
| Script-computed packet identity | `context_fingerprint.py` and the model-authored `fingerprint.json` go. `forge_packet.py` computes a digest from normalized packet intent; the trailer carries `packet_context=` and `supplied_inputs=yes\|no`. The old `context=` remains parseable but cannot establish the new identity. See Duplicate-review identity. `audit-code-publish` keeps its own script copies. |
| Session reruns keep their own allowance | As today, an answer or code change in `session` starts a fresh run with its own allowance. Only a caller continuing after fixes, such as `implement-publish`, passes `prior_record` and shares the allowance. |
| Mode decides the return | `return_format` goes: `session` presents `report.md`, and `one-shot` returns the finalizer's status line and paths, which is what both skill callers pass today. |
| Publication authorization leaves review-code | The merged-target authorization input goes. The retrospective Mode line reads only "Retrospective review of merged pull request", and `review-code-publish` alone decides whether to publish. |
| No timing log | `run_events.py`, its tests and the hooks in other scripts go, along with every `wrap` prefix in review-code and review-code-publish. Timing for later measurements comes from transcript tool-call timestamps, which `transcript_usage.py` already parses. |
| History leaves the installed skill | `HISTORY.md` moves under `docs/`; `DESIGN.md` keeps only the current design. |

### Prior-record check

The one-hop check replaces the chain validator, so it must keep what that validator enforced. `render_review.py` refuses a `prior_record` run unless:

- the prior record carries its finalization marker and the same repository and base;
- every prior open finding and question is classified, and every `outstanding` and `routed` entry survives unless a task in this run settled it;
- the spent allowance flags are at least the prior's;
- each carried confirmation names the prior record and a batch whose accounting establishes it (`confirmed_in`), transitively through the prior's own carried entries;
- the record's `lineage` is the prior's lineage plus the prior itself. `implement-publish` retains its latest accepted record and requires that record in the final lineage, alongside the dispatched records. Parent equality alone cannot detect a sibling that reuses an ancestor's unspent allowance.

A fixed prior finding on this local path does not itself consume another verifier batch. An exhausted allowance alone does not make the run incomplete; unfinished required verification does. PR re-reviews retain independent verification of prior `must-fix` findings whose fate the code decides.

### Duplicate-review identity

Keep the complete-packet and thread-state checks. Reuse a review only when head, base, merge-base, workflow and `packet_context` match, both runs record `supplied_inputs=no`, and `later-state` settles every relevant item. Here `supplied_inputs` means caller-supplied issues or specs. An absent marker or digest refuses the shortcut. This also rejects a prior review that used a supplied spec when the current caller supplies none.

Compute `packet_context` from the packet's normalized PR title/body and linked-issue coordinates, title/body and comment records, including comment availability/completeness. Include the set of linked issues, so adding or removing an older issue changes the digest. `later-state` remains necessary for reviews, replies and thread resolution, but cannot detect an issue comment that disappeared. Compute and check the digest in scripts using the persisted packet; the model neither transcribes the fingerprint inputs nor supplies the digest. Base equality already fixes the tracked base-version guidance. Local runs need no packet digest.

## Target layout

| File | Replaces | Loaded |
| --- | --- | --- |
| `SKILL.md` ([draft](SKILL.draft.md)) | `SKILL.md` | Always |
| `rubric.md` ([draft](rubric.draft.md)) | `review-rubric.md`, `conformance.md`, `released-compatibility.md`, `changed-tests.md`, `check-evidence.md` | Always |
| `targets.md` | `pull-request-target.md`, `local-targets.md` | Step 1 |
| `prior-state.md` | `re-review.md`, `continuation-addendum.md` | A re-review |
| `verification.md` | `verifier-handoff.md` | A batch |
| `output.md` | `rendering.md` | Step 7 |
| `verifier.md`, `verifier-concurrency.md` | also `verifier-return.md` | Worker brief only |

The builder embeds the rubric's Released compatibility and Changed tests sections by heading; Supplied checks stays primary-only.

**Undrafted files must keep.** `targets.md`: dirty submodule content is a coverage gap; a short base name prefers `origin/<base>`, and a base equal to the current branch means `HEAD`; local records carry no `repository_url`, so unpushed commits never become forge links; a packet without `merged` gives a provisional `Incomplete`; `[bot]` login normalization (moves into `forge_packet.py` where possible). `verification.md`: dispatch only after the full pass; reconciliation of corrections, safety rulings and duplicate groups; a changed mandatory claim is reconfirmed in the follow-up or withheld; repair fixes encoding only.

## Size

The two drafts total 20,262 bytes as staged. Removing only the draft notices on activation leaves an always-loaded pair under 20 KB, including the license notice, replacing a common set of about 32 KB. The files they replace total 38,413 bytes; changed tests and check evidence were already loaded on every path. The rest of the layout is not drafted; `test_instruction_budget.py` sets new limits as each change lands.

## Sequence

1. **Prose and history.** Consolidate references into the target layout and move `HISTORY.md`, keeping today's semantics: `SKILL.md` still names the profiles, addenda and fingerprint. Fix consumer paths in the same change (`implement-publish/SKILL.md` names `check-evidence.md`, `implement-publish/references/continuation.md` names `continuation-addendum.md`, `review-code-publish/SKILL.md` names `rendering.md`). No workflow bump.
2. **One record, prior records, scripted identity.** `render_review.py`, `prior_record` with the check above, `forge_packet.py`'s packet digest and the new trailer fields, the plain retrospective Mode line, and the draft `SKILL.md` activated without `profile`, `return_format` or publication authorization. Rewrite `implement-publish`'s gate call and `continuation.md`, and drop those inputs from `review-code-publish`'s invocation. One workflow bump covers the record, state and trailer changes; each open pull request gets one fresh review. The packet digest works with today's saved-response normalization before scripted fetching lands.
3. **Verifier.** Inline only and the helper-generated bundle ID echo. Mechanics only, no workflow bump; the private manifest and accounting formats change.
4. **Fetch and timing.** `forge_packet.py fetch`; delete `run_events.py` and remove `wrap` from both skills. Mechanics only, no bump.

`finish-it` changes through its dependencies only.

## Acceptance

For #357 and #358, map each rejection or preservation rule enforced by a removed mechanism to its replacement and a focused fixture, or record an explicit behavior change in `DESIGN.md`. Deliberate removals must remain consistent with What stays and the epic's Contracts; recording a removal does not waive them. Keep the one-hop lineage and allowance checks, state retention, bundle pairing and mutable-input identity covered.

- **#356:** retain examples of requirement omissions in unchanged code and a diff that weakens its own guidance, which must still be judged against the base version.
- **#357:** test a fixed ordinary `must-fix` with both batches spent and no new mandatory work; it can complete after the primary's recheck. Test deleted issue comments, added and removed older linked issues, prior-only supplied specs, absent identity markers, and equal complete inputs. Keep the existing fork, carried-confirmation and allowance fixtures.
- **#358:** reject a return from another run or rebuilt brief with the same batch name and candidate IDs. Keep role, ID, evidence, encoding-repair and withholding fixtures.

In #357, run one bounded reviewer-and-caller exercise using the four available archived #341 tasks. Reseed the continuation as a `prior_record`, so it tests the new route rather than the legacy full-review fallback. Exercise the applicable caller's local artifact-consumption path without forge writes. Check the final head, lineage, carried blockers, allowance and incomplete-result handling. Keep exhausted-allowance edge cases in deterministic CLI fixtures. Record instruction loads, repair loops and known-defect recovery as observations. A missing exercise is an explicit acceptance gap; it is not replaced by script tests or the old unavailable ten-case study. #358 and #359 need focused CLI checks unless those checks expose an integration gap.

The epic retains its at-most-20-KB always-loaded target. These exercises establish no comparative recall, precision, cost or latency advantage. The [older holdout's corrected result](../prototype-runs-holdout/evaluation.md) is three failed criteria, one undecidable and one passed; its timing totals sum overlapping agent spans. The [current rewrite acceptance](../review-code-rewrite-2026-09-22/acceptance/README.md) is inconclusive, and the [artifact comparison](../review-code-artifact-savings-2026-09-22/combined.md) establishes no overall savings or recall improvement. Structural validation does not prove that a reviewer found every defect.

## Considered and rejected

- **Dropping observations.** They keep accurate, non-actionable facts from becoming low-value `consider` findings or summary padding, and the verifier's aside needs a channel outside its verdicts. The saving is a few sentences.
- **Merging the `concurrency` and `invariant` kinds.** It saves one word, changes public vocabulary, and `invariant` also covers shared-state rules unrelated to threads.
