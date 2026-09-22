# Expected outcomes (adjudicator only)

**Do not give this file, or a link to it, to any working reviewer or verifier.** It pairs with the inputs in [comparison.md](comparison.md). Expected outcomes come from the cited adjudications and upstream events, never from a reviewer's own conclusion.

At freeze, #333's independent adjudicator must confirm the two fresh-sample expectations, C7 and C8, before any attempt. Each rests on one published review and its addressing record, not on an adjudication.

## Definitions

- **Recovered.** A published finding names the registered defect's mechanism and requests a sufficient outcome. Priority may differ; the action must be `must-fix` wherever the row says `must-fix`.
- **False clean.** On a buggy case, the status is `Approved` or `Needs Information` with the registered defect unrecovered.
- **Unsupported blocker.** A `must-fix` finding that the adjudicator rules false or not introduced here.
- **Contract break.** Any of these:
  - the payload or record fails `validate_review.py`;
  - the trailer grammar changes, other than the workflow identifier;
  - a record or addendum does not match its schema in [private-contracts.md](private-contracts.md);
  - the spent allowance is reset or reinterpreted upward.

## Per case

| Id | Registered truth | Expected status (both arms) | Treatment-specific expectation | Failure to investigate |
| --- | --- | --- | --- | --- |
| C1 | One material defect: when the new master's ID does not resolve locally, the demoted sender's `slaveof` stays null. `updateShardId()` then propagates the shard ID, the new equality guard in the flattening path reports no change, and stale cached-master state stays eligible for failover. Must-fix. Sources: [test-2 Fable evaluation](../prototype-runs-2026-09-01-test-2-fable/evaluation.md#why-the-defect-is-credible). | `Changes Requested` | A safety-premise task in the failover area whose premise covers the master lookup, ruled `fails` and reopened as a candidate that is then `confirmed` (a follow-up is allowed). A primary finding confirmed by candidate verification also counts. | `Approved`: a false clean. A safety-premise check that ran and missed it: inspect how the premises were selected. |
| C2 | GT-p1: the value-terminator change leaves a path that bypasses the minimum-values check (`parser.rs:135-138` at head). GT-p2 is a second registered item. Sources: #138 [comparison data](../bounded-discovery-decision-2026-09-11/comparison-data.md) and its revealed register. | `Changes Requested` | Not a named high-risk area, so no safety-premise task is required. Recovery depends on the primary. | A treatment miss where the baseline recovers is the epic's accepted recall tradeoff made concrete. Investigate it and report it; do not tune toward it. |
| C3 | GT-j1: `Overwrite`'s new object gate drops inferred context/input properties when middleware params come from an unconstrained generic type parameter. Fixed upstream by trpc/trpc#5039. Source: [#137 (j) register](../one-shot-qualification-2026-09-07/j-trpc-5017/register.md). | `Changes Requested` | Hygiene `consider` findings may appear. They must not stand in for GT-j1, and they do not change the status. | `Approved` with only hygiene findings: the false-clean shape #202 named. |
| C4 | GT-c1: `stubs/redis/redis/__init__.pyi` was not updated for the two new public names the issue requires. T-c2 and T-c3 are the same class of omission. Source: [holdout (c)](../prototype-runs-holdout/README.md). | `Changes Requested` | A `kind=requirement` `must-fix` finding whose fix site is the unchanged file. | A finding dropped as "not introduced here": a gate-2 regression. |
| C5 | A released-compatibility break: full-consumption `advance` leaves capacity unchanged (64 instead of 53 in the traced case), contradicting released 1.6.0 behavior and documentation. Source: [DESIGN.md bytes trace](../../../skills/review-code/DESIGN.md#bytes-paper-regression-at-the-pinned-head). | `Changes Requested` | A `compatibility` finding with a candidate task whose trigger is `compatibility`, ruled `confirmed`. | Publication without a confirmed task: a mandatory-verification break. |
| C6 | No material defect (adjudicated clean). Source: [#137 (m)](../one-shot-qualification-2026-09-07/). | `Approved` (`consider` findings allowed) | At least one safety-premise task in the concurrency area, ruled `holds`. Coverage complete. | Any `must-fix`: an unsupported blocker. `Approved` with no premise task on this concurrency change: a skipped required check. |
| C7 | One must-fix: "Preserve the follow-up for refuted requirement blockers" ([published finding](https://github.com/kamui/skills/pull/320)), fixed in `1701a62` and `573f1bf`. The adjudicator confirms at freeze. | `Changes Requested` | Nothing beyond recovery. | Loss of the known blocker. |
| C8 | No material defect: published `Approved`, no findings, no later correction known. The adjudicator confirms at freeze. | `Approved` | Nothing specific. Recorded verification work is reported for cost. | Any `must-fix`. |
| C9 | Phase 1: must-fix "Retain and invalidate acceptance evidence on the same terms as a check" ([published finding](https://github.com/kamui/skills/pull/302)). Phase 2: fixed by `884f322` (one `consider` was published there historically). | Phase 1 `Changes Requested`; phase 2 `Approved` | The phase-2 addendum is `implementation-gate-addendum/2`, and its `allowance` equals phase 1's. Cross-version run: `record_format: implementation-gate-record/1`, the spent allowance is derived from the version-1 batch count, and no version-1 file is written. | The allowance is reset, the chain validation is skipped, or a version-1 `clean_verdict: outstanding` becomes `stands`. |
| C10 | The fixed id stays fixed. The synthetic change adds a new must-fix candidate: retrying an ambiguous write without reading the target can duplicate pull-request writes. | `Incomplete` | The new candidate appears in `outstanding` with no batch available, and it is not published as a finding. Coverage is incomplete. | `Approved`, a new batch dispatched beyond the allowance, or an unconfirmed `must-fix` published. |

## Cross-case checks

- Every published `must-fix` or `security`/`compatibility` finding has a `confirmed` candidate task. In the baseline this is `independent-confirmed`.
- No attempt reports `coverage=complete` while any required task is `pending`, `withheld`, or listed in `outstanding`.
- Payloads validate with the arm's own `validate_review.py`, and trailers differ between the arms only in `workflow`.
