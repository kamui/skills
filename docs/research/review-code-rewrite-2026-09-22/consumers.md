# Consumer map

This map lists what reads each interface the rewrite touches, as of `7387c169c9b5b23c5c679efb7110c9c07fc3f7f3`. It covers four kinds of dependency:

- exact-heading prompt extraction;
- timing interfaces;
- public addressing contracts;
- cross-skill command tests.

No replacement orchestration framework is introduced. Each row names the ticket that must keep the consumer working.

## Exact-heading and marker extraction

These consumers split reference files on literal text. Renaming or moving the text breaks them, and the script refuses with `instruction boundary changed`.

| Consumer | Extracts | From | Rewrite impact | Owner |
| --- | --- | --- | --- | --- |
| `build_verifier_prompt.py` `render()` | The whole file | `references/verifier.md`, `verifier-return.md` | The Clean-verdict task and the complete-ledger/related-acquittal wording give way to the safety-premise task. The brief is regenerated from the new text. README's layout folds `verifier-return.md` into `verification.md`, which the primary loads: either keep a separate verifier-facing return file, or have the builder extract a marked section so the worker never receives dispatch or reconciliation instructions. | #331, #332 |
| `build_verifier_prompt.py` | `## Inspect and run` … `## Primary focused-test recording` | `references/changed-tests.md` | Keep both headings, or change the boundaries and the file together. | #331, #332 |
| `build_verifier_prompt.py` | `**Released compatibility.**` to EOF | `references/released-compatibility.md` | Keep the marker. | #332 |
| `build_verifier_prompt.py` | `The caller may supply a compact verification summary.` to EOF | `references/check-evidence.md` | Keep the sentence. `implement-publish` also cites this file by name. | #332 |
| `build_verifier_prompt.py` | `## Verifier brief` to EOF | `references/conformance.md` | Keep the heading. | #332 |
| `build_verifier_prompt.py` | The whole file, for `concurrency`/`invariant` candidates | `references/verifier-concurrency.md` | Unchanged. | — |
| `test_command_chains.py` `command()` | The `finalize_review.py` command lines | `SKILL.md` step 5 | The draft moves rendering into `references/rendering.md`. Either keep the two literal commands in `SKILL.md` or point the test at the new owner. | #332 |
| `test_command_chains.py` | The root fetch and guarded early-build block | `references/pull-request-target.md` | #330 removes the early build. Its tests go with it, and the root fetch block stays. | #330 |
| `test_run_events.py` | Wrapped fetch and write commands | `pull-request-target.md`, `review-code-publish/references/publication.md` | Keep the wrap lines. | #330, #332 |
| `resolve-review/scripts/run_block.py` | Marked `sh` fences | `resolve-review/references/addressing-protocol.md` | Unchanged; out of scope. | — |
| `test_thread_writes.py` | The shared write-loop fence, byte-identical in two files | `publication.md`, `addressing-protocol.md` | Unchanged. | — |
| `implement-publish` SKILL and `continuation.md` | Anchor links `../SKILL.md#3-implement`, `#4-review-before-publishing`; prose names `review-code`'s `references/check-evidence.md`, `references/continuation-addendum.md`, and "Return section" | `implement-publish`, `review-code` | The draft renames the continuation reference and replaces "Return" with "Result". Update both names in the same change, or keep the old ones. | #331, #332 |
| `review-code-publish` SKILL | Names "Modes section", "render-and-validate step", and `references/rendering.md` | `review-code` | Keep a Modes heading, and keep rendering in `rendering.md`. | #332 |

## Timing interfaces

| Interface | Producer | Consumer | Rewrite impact | Owner |
| --- | --- | --- | --- | --- |
| `context-built` event (`target`, `head`, `merge_base`, `prior_head`, `store`) | `review_context.py` | `run_events.py summarize` | Unchanged. After #330, a pull-request first review produces it from step 2, not the root block. | #330 |
| `verifier-brief-built`, `verifier-return-accounted` (`phase`, `mode`, `candidates`, `ledger_rows`, `full_ledger_rows`) | `build_verifier_prompt.py`, `account_verifier_return.py` | `run_events.py summarize`: `by_mode`, `complete_ledger_zero_rows`, `complete_ledger_nonzero_rows`, `ledger_rows_unknown` | `mode` values `complete-ledger` and `related-acquittal` go away, and a `premises` count replaces `ledger_rows`. Keep reading old events so earlier runs still summarize, and report a missing field as unknown, not zero. | #331 |
| `payload-composed` (`status`, `coverage`, counts) | `compose_review.py` | `summarize` | Unchanged. | — |
| `forge-fetched`, `focused-test-ran`, `forge-written` wrapped events | `run_events.py wrap` | `summarize` | Unchanged. The early-build removal changes when fetches occur, not their events. | #330 |
| `policy.workflow` on events | `validate_review.WORKFLOW` | `summarize`, research joins | Bumped at activation. Joins must key on the skill commit, as DESIGN.md already requires, and not on the identifier alone. | #332 |
| `resolve-review` `timeline` file | `resolve-review` | its step-6 cost section | Unchanged; out of scope. | — |

## Public addressing and publication contracts

These interfaces are preserved. The only change is the workflow identifier in the trailer.

| Contract | Defined in | Consumer | Constraint |
| --- | --- | --- | --- |
| Finding prose: title, `Triggers when`, `Impact`, `Change`, optional `Source`; `[P0-3]` and `[must-fix]`/`[consider]` labels | `review-record.md`, `rendering.md`, `validate_review.py` | `resolve-review` `addressing-protocol.md` (blocking rule), human readers | Byte-compatible shape. |
| Hidden trailers: the run trailer `review-run head= base-ref= base-sha= merge-base= workflow= context= issues= coverage=`, and item trailers carrying the stable `id`, `priority`, `action`, and `blocking` | `validate_review.py` | `resolve-review` ledger keying, `re-review.md` duplicate-review shortcut | Only `workflow` changes. The shortcut compares `workflow`, so every open pull request gets one fresh review after activation. That is expected, and #277 accepted the same cost. |
| Question shape and `[Question]` tag | `review-record.md` | `resolve-review` `answered` disposition | Unchanged. |
| `payload.json` → `batch.json` (`--emit-batch`, `--event`) | `validate_review.py` | `review-code-publish` `publication.md` | Unchanged. |
| Prior-item classifications, drafted replies, thread node ids, `writes.jsonl` | `re-review.md`, `publication.md` | `review-code-publish` thread writes | Unchanged. |
| Stops: `target-unresolved`, `target-closed-unmerged`, `duplicate-review`, `snapshot-failed`, `nothing-to-review`, `script-failure` | `SKILL.md` | `review-code-publish`, `implement-publish`, `finish-it` (through them) | Names unchanged. |
| Review status values | `review-record.md`, `STATUSES` | `finish-it` stop on `Approved`, `implement-publish` gate | Unchanged. |
| Caller inputs: `mode`, `profile`, target, issues/spec, reviewer identity, phase-1 packet, check evidence, test policy, scope directives, inputs supplied up front, shortcut, merged authorization | `SKILL.md` Caller table | `review-code-publish`, `implement-publish`, `finish-it`, `audit-code-publish` (identity only) | Names unchanged. The draft groups four rarely used inputs into one table row, but their names stay. |

## Private record consumers

See [private-contracts.md](private-contracts.md#consumers-of-each-retained-field). Two callers read the local record:

- `implement-publish` step 4 reads its status, findings, routed items, and outstanding verification to decide whether it may publish.
- `implement-publish`'s `continuation.md` reads the record and its addenda for the head chain, open items, allowance, and coverage.

`review-code-publish`, `resolve-review`, and `finish-it` never read `record.json`. They consume the published review, the payload, the batch, and the prior-item state.

## Cross-skill command tests

| Test | Covers | Rewrite impact | Owner |
| --- | --- | --- | --- |
| `review-code/scripts/test_command_chains.py` | `SKILL.md` finalize commands; the `pull-request-target.md` root block; publisher freshness and submission; dismissal; token blocks in `audit-code-publish` and `legacy reviewer` | Update the finalize extraction if step 5 moves, and remove the early-build cases. Keep the other blocks. | #330, #332 |
| `review-code/scripts/test_thread_writes.py` | Byte-identical write loop in `publication.md` and `addressing-protocol.md`; installed-path runs | Unchanged. | — |
| `review-code/scripts/test_run_events.py` | Wrapped commands in two references; `summarize` verification counters | Update the verification counters for the new modes, and keep old-event fixtures. | #331 |
| `review-code/scripts/test_verifier_handoff.py` | Build and account modes; projection; return rules | Replace the complete-ledger and related-acquittal cases with safety-premise cases. Keep candidate-only cases. | #331 |
| `review-code/scripts/test_compose_review.py` | `implementation-gate-record/1` checks | Add version-2 checks; see private-contracts.md. The old clean-verdict fixtures go. | #331 |
| `review-code/scripts/test_instruction_budget.py` | Byte budget over `SKILL.md`, rubric, record, rendering | Update the file list for the final layout, and lower `BUDGET` to the accepted result. | #332, #333 |
| `resolve-review` fixture suites | The addressing protocol blocks | Unchanged. | — |

The instructions win over the scripts, as `docs/agents/scripts.md` states: where the draft and a script disagree, the script changes in the owning ticket. Until it does, the draft stays inactive.
