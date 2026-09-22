# review-code rewrite: staged draft (issue #329)

This is the design stage of [#328](https://github.com/kamui/skills/issues/328), for [#329](https://github.com/kamui/skills/issues/329). **Nothing here is active.** The installed `skills/review-code` at `7387c169c9b5b23c5c679efb7110c9c07fc3f7f3` is unchanged. Its scripts still enforce `implementation-gate-record/1` and the complete-ledger verifier modes. The draft lives under `docs/research/`, so `scripts/sync-global-skills` never installs it.

| File | Contents |
| --- | --- |
| [SKILL.draft.md](SKILL.draft.md) | The new entrypoint: 1,091 words of body |
| [private-contracts.md](private-contracts.md) | `implementation-gate-record/2` and `implementation-gate-addendum/2`, the version-1 transition, and a consumer for each retained field |
| [consumers.md](consumers.md) | Heading and marker extraction, timing events, public contracts, and cross-skill command tests, each with an owning ticket |
| [comparison.md](comparison.md) | Baseline pin, matched conditions, bounds, and ten reviewer-input cases |
| [expected-outcomes.md](expected-outcomes.md) | Expected results, kept apart from reviewer inputs |

## Answers the owner should get from the draft alone

- **What triggers verification?** A surviving candidate triggers it when it is proposed `must-fix`, when it concerns security or authorization, data loss or corruption, a destructive migration, or a released-compatibility break, or when it is a code-decided prior `must-fix` on a pull-request re-review. A no-blocker conclusion on one of those areas, or on a concurrency or failover invariant, adds a safety-premise check. Anything else is optional scrutiny.
- **What blocks merge?** An unsettled `must-fix` finding (`Changes Requested`). An `Incomplete` review cannot approve either.
- **What does incomplete mean?** No blocker is known, but something required did not finish:
  - a changed file stayed unreviewed;
  - a required check or input was missing;
  - required verification had no awaited route, failed, or needed a batch after the allowance was spent.
- **What does the result contain?**
  - status and summary;
  - findings, questions, and observations;
  - requirement outcomes;
  - per-file coverage and the check evidence used;
  - verification tasks and the remaining allowance;
  - routed items;
  - profile artifacts.

These are the Verification and Result sections of the draft.

## Consequential behavior changes

The epic's Agreed direction decided these deliberately. #332 records them in DESIGN.md and the CHANGELOG when it activates them.

1. **No clean-verdict attack.** The complete-ledger and related-acquittal verifier modes go, along with the material-survivor and attackable-row classifications. A low-risk review with no blocker gets no independent scrutiny unless the primary asks for it. This is the recall tradeoff that C2 and C3 measure.
2. **A safety-premise check replaces them on high-risk no-blocker conclusions.** It attacks a few named premises, not every acquittal.
3. **No exhaustive candidate ledger.** Dropped candidates leave no record. Only rendered items, requirement outcomes, and verification tasks persist.
4. **No early verifier dispatch.** Batches are dispatched after the full pass.
5. **No early first-review context build.** #330 does this, which reverses #258. Reconcile it with queued #260 before any prefetch work.
6. **Fixed recipes removed.** The whole-file thresholds, read justifications, batched-search recipes, and routine narration go. The reviewer chooses how to read.
7. **Private record version 2.** It carries a version-1 transition that never resets spent allowance, and it closes a version-1 outstanding clean-verdict obligation explicitly rather than as `stands`.
8. **Workflow identifier bump at activation.** The duplicate-review shortcut therefore misses once, so each open pull request gets one fresh review.

Kept unchanged:

- caller inputs, stops, and statuses;
- finding, question, and observation prose;
- trailers, except `workflow`;
- payload and batch shapes;
- thread-state semantics;
- mandatory candidate confirmation;
- the one-initial-plus-one-follow-up cap;
- awaited batches;
- `unresolved` handling;
- supplied-evidence rules;
- line-anchor sides, `UNKNOWN` provenance, fetch completeness, truncated-diff recovery, timing events, and review freshness.

## Reference layout for #332

The draft names a layout. #332 may adjust names within [consumers.md](consumers.md)'s constraints. A reference stays only when it holds a substantial conditional procedure or an exact interface.

| Draft reference | Replaces | Loaded when |
| --- | --- | --- |
| `review-rubric.md` (shortened: admission gates, requirement ledger, material questions, priorities) | the same file | Always |
| `rendering.md` (authoring contract and examples) | `rendering.md`, `review-record.md` | At render |
| `verification.md` (tasks, brief and accounting commands, reconciliation) | `verifier-handoff.md`, `verifier-return.md` | A batch is needed |
| `continuation.md` | `continuation-addendum.md` | Continuation after fixes |
| `pull-request-target.md`, `local-targets.md`, `re-review.md`, `changed-tests.md`, `check-evidence.md`, `conformance.md`, `released-compatibility.md` | themselves, trimmed | Their branch |
| `verifier.md`, `verifier-concurrency.md` | themselves, with the premise task replacing the clean-verdict task | Built into the brief only |

## Acceptance criteria → where

| #329 criterion | Where |
| --- | --- |
| Mandatory candidate verification, the high-risk safety-premise check, optional scrutiny, one initial plus one follow-up across continuations, incomplete outcomes | SKILL.draft.md, Verification |
| Concrete record and addendum schemas and version transition; every retained field has a consumer | private-contracts.md |
| The owner can answer the four questions from the draft | SKILL.draft.md, Verification and Result; summarized above |
| Consumer map: heading extraction, timing, public addressing, cross-skill tests; no new orchestration framework | consumers.md |
| Baseline pin and small comparison manifest covering the named categories, the historical recovery, and a fresh sample | comparison.md (C1 historical, C7–C8 fresh) |
| Expected outcomes kept apart from inputs; matched model, effort, and evidence; bounded attempts and spend; no campaign launched | expected-outcomes.md, comparison.md Matched conditions and Bounds |
