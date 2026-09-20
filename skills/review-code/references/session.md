# Review session

Load only in session mode, after step 5 has produced the immutable review record. One-shot callers do not load this reference.

Present the complete would-be review: summary, findings, and questions, retaining the script-rendered commit-pinned links. Then list every unresolved routed item as a question the user can answer; local rechecks apply carried answers and chosen readings under [`re-review.md`](re-review.md#session-recheck) first:

- For each ambiguity, give both supported readings and the one applied, and ask which reading should govern.
- For each unrecoverable input, name the missing input, what it gates, and who can supply it; ask for that input.
- For each open material question, including an unanswered required issue, state how the answer settles the recorded decision and who can answer it.

In a headless session, each ask becomes a line in the report; an unanswered request supplies neither a decision nor authorization.

## Three artifacts

Keep these at separate named paths in the review's private directory:

- The **review record** is the complete immutable return from step 5, including its private ledgers, identity, status, composition, validated payload, and batch. Its status never changes.
- The **session layer** records every user decision at an increasing `session/<n>` source coordinate, with the user's words, affected stable ids or ledger rows, what it would change, and the record's settlement field it applies through. Retain claims, supplied inputs, and requests at such coordinates too, distinguished from decisions, so their evidence and resulting amendments have a premise to cite.
- The **session record** starts as a copy of the review record and carries amendments: evidence-justified changes to a disposition, ledger row, or coverage entry. Each amendment records its before/after fields, decisive evidence, and the layer entry it takes as its premise. It has its own derived status and separately rendered and validated artifacts.

Keep `session/<n>` coordinates and amendment provenance in the private record only, outside composition fields, prose, trailers, and rendered artifacts. The session report names decisions in plain language and shows which ones any status difference depends on; its private companion maps them to their coordinates.

## Decisions are authoritative; facts are claims

A user may choose a supported reading, answer a product or maintainer question, or set scope. Record the decision in the layer, then apply the recorded settlement field: which candidate re-opens, which row closes, or which obligation is discharged. A decision alone is a layer entry; a material answer produces an amendment through that settlement field. Scope changes retain explicit file accounting and reasons for ignored paths.

A statement about the code, such as “that branch is unreachable,” is a claim to falsify under the rubric. Split a mixed answer into its decision and factual premises. Change a disposition only on decisive evidence; the speaker's authority is not evidence about code. If the user challenges an independently confirmed finding and the bounded re-falsification leaves it standing, retain the finding and its blocking effect and record the disagreement as disputed in the session layer. Do not settle it by who spoke last or turn a current finding into a forge prior item to represent the dispute.

`accepted` reuses `re-review.md`'s residual-risk meaning: an authorized human explicitly accepted the residual risk. The skill cannot determine whether the user has that authority. Record the user's explicit acceptance as a layer entry with that limitation; it produces **no amendment**, changes neither status, and leaves the finding's action and blocking effect intact. Technical evidence that defeats a finding instead follows re-falsification below.

## Re-falsify, do not re-review

Use the rubric's Uncertainty routing recovery rule as the owner: re-run only the falsifications the answer or supplied input gates. A late artifact re-opens only its gated rows and candidates; remove its coverage gap only after that work completes. Keep unrelated dispositions and evidence. For an answered material question, follow its settlement field and keep its stable concept id if it becomes a finding.

Work under the references the review loaded, from the skill root the record names. After compaction, re-read `review-rubric.md` and `review-record.md` before any re-falsification, and `rendering.md` before re-rendering. Load any reference the new work needs even if the original review did not need it. For the further batch below, read `verifier-handoff.md` and `verifier-return.md` from that root; the builder embeds the worker's procedure. Use that root's scripts rather than another installation.

A requested longer trace or focused test stays within the rubric's Complete inspection and Changed tests bounds: bounded reads, a disposable test environment, the applicable time limits, and recorded command/head/result or a named execution gap. No production service, credentials, destructive external effect, or reviewed-source edit is permitted. A request for depth does not start unrelated discovery or imply a test passed when it was not run.

### Verification budget

Preserve the review's verification accounting, including whether its follow-up batch is spent. Re-opened candidates keep step 3's mandatory-verification triggers, batch contents, isolation, handoff/accounting, reconciliation, and incomplete-coverage rules. An unspent follow-up remains available under those rules; do not restart the initial batch.

When an answer re-opens a candidate needing mandatory verification after the follow-up is spent, the user may authorize **one further verifier batch per session**. Before dispatch, explain the pending candidate and ledger work, the cost of another isolated verification pass (including any bounded test execution), and that this consumes the session's sole further batch. Record the explicit authorization and its scope in the layer; batch all eligible pending work together. This is the only departure from the core's one-initial-plus-one-follow-up cap, and it applies only after the immutable record exists.

Count that authorization as spent on dispatch, including a failed or incomplete batch. If authorization is absent, isolation is unavailable, or the further batch has been spent, withhold anything still requiring confirmation and record the verification gap; already verified unrelated findings remain. Reconcile under step 3, including its clean-verdict trigger: any newly required work left without a permitted batch keeps verification and coverage incomplete. Budget exhaustion never establishes a clean verdict.

## Validate every amendment

After each amendment, derive the session status under `review-record.md`, retaining stable ids and the pinned code identity. Update the session copy of the authoritative composition fields and authored prose under `rendering.md`; keep layer coordinates in its private companion. Use step 5's composer, validation/render, and batch-emission procedure with the recorded absolute scripts and store, staging each revision at new private paths and making it current only after every command exits 0. Preserve the original artifacts and prior trailers. An amendment that closes a private ledger row may leave the rendered fields unchanged; it still requires recomposition and validation.

On a non-zero exit, report the violations, repair the composition input, and repeat that procedure. An unresolved failure returns `script-failure`; retain the last valid session record and mark the attempted amendment pending, never present an unvalidated revision as current.

After every turn, show the immutable review record beside the current valid session record, each with its status and complete would-be review, followed by the layer decisions and disputes. State which layer decisions the session status depends on, even when no code changed. On acceptance of a `must-fix`, for example, both statuses remain `Changes Requested (advisory)` and the acceptance appears beside them. A layer-only entry needs no recomposition because neither record changed.

## Fixes and exit

Fixes are outside the record. A request to fix hands off to implementation separately from this read-only review. Once reviewed code changes, mark both records stale for the new code and stop amending them. A requested local recheck returns to step 1 with the same session’s persisted session record under [`re-review.md`](re-review.md#session-recheck); that reference owns continuity, delta scope, layer carry-forward, and run-budget handling. A pull-request recheck continues to take prior state only from its packet.

At local-session exit, release the owned snapshot refs under [`re-review.md`](re-review.md#session-snapshot-lifetime). At exit, summarize decisions, findings accepted, disputed, or re-opened, and questions answered or still open. Keep the decision-to-coordinate mapping in the named private session layer, and report its path alongside both records and statuses. If stale, show that qualification with both statuses.

Nothing from the session reaches the forge. For a publication request, direct the user to `review-code-publish`, which performs its own one-shot review and knows nothing of the session layer. A later one-shot review receives no session decisions or amendments; publication of a discussed record remains deferred.
