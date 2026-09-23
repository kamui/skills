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
| Record meaning, output profiles, and rendered syntax | [`SKILL.md`](SKILL.md) Return, [`rendering.md`](references/rendering.md), and the [composer](scripts/compose_review.py) and [validator](scripts/validate_review.py) |
| Prior reviews and implementation continuations | [`re-review.md`](references/re-review.md) and [`continuation-addendum.md`](references/continuation-addendum.md), respectively |
| Publication | [`review-code-publish`](../review-code-publish/SKILL.md) and its [publication reference](../review-code-publish/references/publication.md) |

Keep dated evidence and superseded decisions in [HISTORY.md](HISTORY.md). Update this file when the current architecture or rule ownership changes. The [instruction budget check](scripts/test_instruction_budget.py) requires a dated entry here before any measured-load limit rises; that rationale belongs with the current design.

## Concise runtime strategy, issue #332, 2026-09-22

Workflow `v5b-24` removes mandatory reading/search recipes and replaces the runtime manual with the strategy draft, selective procedures, and composer examples. It supersedes the historical inspection recipes and 73 KB budget; #331's verification policy and version-2 state remain. The always-loaded ceiling is now 26 KB, with separate limits for runtime total, expanded primary paths, and generated verifier briefs. [The runtime report](../../docs/research/review-code-rewrite-2026-09-22/runtime-layout.md) records the layout, justified entrypoint exception, baseline comparison, and limits. Word counts make no quality, latency, or cost claim; #333 owns the bounded comparison.

## Artifact-savings baseline, issue #341, 2026-09-22

The artifact-savings work (#340) optimizes mechanical authoring and helper discovery, not reference counts. Its [baseline](../../docs/research/review-code-artifact-savings-2026-09-22/README.md) maps each repeated field to the packet, store, input, chain file or judgment that owns it. It also archives four reconstructable interface tasks with a seeded version-2 continuation chain and freezes the paired Sonnet 5 High protocol. Feature changes must keep a mechanical field's authority and its existing check, and must leave judgments with the model. Workflow `v5b-24` and every private schema are unchanged.
