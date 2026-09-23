# Review-code design

`review-code` inspects a pull request, committed range, or working tree and returns a validated review record. It does not publish. This file explains the current design for maintainers; [`SKILL.md`](SKILL.md) and its references define runtime behavior. The [design history](HISTORY.md) retains earlier rules, experiments, issue evidence, and release notes. Historical rules there may have been superseded.

## Review and verification

One reviewer reads the pinned change, checks its stated requirements, follows named risks into relevant unchanged code, and falsifies candidates before retaining them. This keeps the usual review in one context while giving requirement omissions and risks outside changed lines a path into the review. The reviewer accounts for every changed file, risk check, and required input before deriving coverage.

Independent verification is a separate, fresh-context step. A surviving candidate under a mandatory trigger becomes a required candidate task and needs a `confirmed` ruling to publish as a finding. When a review would have no blocker but the change touches a named safety area, the reviewer sends the concrete premises behind that conclusion as safety-premise tasks. The initial and follow-up batches share one allowance across the review and its continuations. The [verification-task change](HISTORY.md#verification-tasks-and-version-2-private-records-issue-331) explains why the former complete-ledger clean-verdict attack was retired. A low-risk clean review can finish without an independent verifier; its missed-defect risk remains open for the [bounded comparison](../../docs/research/review-code-rewrite-2026-09-22/README.md).

The reviewer judges evidence, admission, priority, and whether a safety area applies. Scripts build pinned context, package and account for verifier tasks, and reject contradictory records. Composition renders syntax and links from authoritative fields, so the reviewer does not assemble publication artifacts by hand. `review-code-publish` owns forge writes and their authorization.

## Rule ownership

| Concern | Current owner |
| --- | --- |
| Target resolution and pinned context | [`SKILL.md`](SKILL.md) Caller and Strategy, the conditional [local](references/local-targets.md) or [pull-request](references/pull-request-target.md) target reference, and [`review_context.py`](scripts/review_context.py) |
| Finding admission, issue fit, inspection, uncertainty, priority | [`review-rubric.md`](references/review-rubric.md); [changed tests](references/changed-tests.md), [conformance](references/conformance.md), [released compatibility](references/released-compatibility.md), and [check evidence](references/check-evidence.md) load when applicable |
| Verification triggers and batch allowance | [`SKILL.md`](SKILL.md) Verification; [handoff](references/verifier-handoff.md) and [return](references/verifier-return.md) govern a dispatched batch, and the [verifier brief](references/verifier.md) governs its worker |
| Record meaning, output profiles, rendered syntax, and the report | [`SKILL.md`](SKILL.md) Return, [`rendering.md`](references/rendering.md), the [composer](scripts/compose_review.py), [validator](scripts/validate_review.py), and [finalizer](scripts/finalize_review.py) |
| Prior reviews and implementation continuations | [`re-review.md`](references/re-review.md) and [`continuation-addendum.md`](references/continuation-addendum.md), respectively |
| Publication | [`review-code-publish`](../review-code-publish/SKILL.md) and its [publication reference](../review-code-publish/references/publication.md) |

Keep dated evidence and superseded decisions in [HISTORY.md](HISTORY.md). Update this file when the current architecture or rule ownership changes. The [instruction budget check](scripts/test_instruction_budget.py) requires a dated entry here before any measured-load limit rises; that rationale belongs with the current design.

## Concise runtime strategy, issue #332, 2026-09-22

Workflow `v5b-24` removes mandatory reading/search recipes and replaces the runtime manual with the strategy draft, selective procedures, and composer examples. It supersedes the historical inspection recipes and 73 KB budget; #331's verification policy and version-2 state remain. The always-loaded ceiling is now 26 KB, with separate limits for runtime total, expanded primary paths, and generated verifier briefs. [The runtime report](../../docs/research/review-code-rewrite-2026-09-22/runtime-layout.md) records the layout, justified entrypoint exception, baseline comparison, and limits. Word counts make no quality, latency, or cost claim; #333 owns the bounded comparison.

## Artifact-savings baseline, issue #341, 2026-09-22

The artifact-savings work (#340) optimizes mechanical authoring and helper discovery, not reference counts. Its [baseline](../../docs/research/review-code-artifact-savings-2026-09-22/README.md) maps each repeated field to the packet, store, input, chain file or judgment that owns it. It also archives four reconstructable interface tasks with a seeded version-2 continuation chain and freezes the paired Sonnet 5 High protocol. Feature changes must keep a mechanical field's authority and its existing check, and must leave judgments with the model. Workflow `v5b-24` and every private schema are unchanged.

## Generated reports and artifact returns, issue #342, 2026-09-23

The finalizer now writes `report.md`, so the model no longer writes the complete review a second time after validation. The report is the payload's summary body, the run identity the trailer does not carry, the full body of each line comment the summary only indexes, the private ledgers, routed state, and drafted prior-item replies. Every body appears once. Public payload, batch and fragment bytes are unchanged.

**Stronger precondition.** Finalization requires the composition's `record` for both profiles, with every section written explicitly and nothing defaulted. The composer still accepts a publishable composition without one, as earlier callers used it, but that alone cannot finalize. A publishable record requires `skill_root` in place of `addenda`. Prior items may carry `reply`, `thread_id` and `comment_id`, checked against the read-only `--packet`. The finalizer appends the prior-item trailer, and those fields never reach the payload. `--packet` is the argument #343 reuses for identity derivation.

**Returns.** `return_format: artifacts` lets skill callers take the finalizer's `--compact` status and paths and read the files themselves. `complete`, the default, still returns the whole review, and session and retrospective non-publishing output stay complete. Default finalizer stdout is unchanged.

**Success marker and state.** Outputs are staged, and `report.md` is promoted last. A new gate record, and the publishable composition kept in the private directory, carry `finalization` with protocol `review-code-finalization/1`, the profile, the absolute report path, and the rendered replies. A consumer, including the composer reading a carried chain file, accepts new-protocol output only when that report exists, and it refuses an unknown protocol. A record without `finalization` predates this change and keeps its existing validation. `implementation-gate-record/2` keeps its version: `finalization` is an additive key, and the protocol string is the discriminator. A rerun is refused before anything is modified while an addenda directory holds an addendum, or while an existing record cannot be read to name its addenda directory. An empty addenda directory is not an active chain.

**Workflow.** `v5b-24` is retained. Admission, verification, public rendering, and decision and state semantics are unchanged. The trailer text and its placement are the same; only who appends it changed. The [demonstration](../../docs/research/review-code-report-generation-2026-09-23/README.md) replays the finalizer on #341's archived cells: 9,351–10,054 hand-written report characters become a generated report, with no extra authored field. The PR primary load grows 2,853 bytes to 66,905 of 67,000, mostly because the publishable `--example` now shows the accounting it requires. No limit rises.
