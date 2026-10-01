# Clean-verdict exposure on every surface — issue #202

Paper check for [#202](https://github.com/kamui/skills/issues/202), part of
[#129](https://github.com/kamui/skills/issues/129). Evidence and the pre-change production rule
are pinned at `5c08cf65d8c3e8d0969a1c05d74e9c7699af3658` (`v5b-12`). This check was completed
before editing the rule. No experimental reviewer call, paid grid, rescoring, or snapshot edit
was performed. The implementation advances production to `v5b-13`; future measurements must
identify that separate commit.

## Decision and method

Remove the surface qualification from the existing **no-material-survivor** mode. Every review
with zero findings receives a complete-ledger clean-verdict attack, and retaining only hygiene
findings cannot suppress it. Keep the material-survivor definition introduced by #185, candidate
verification, related-acquittal mode, verifier configuration and task depth, and the total cap of
one initial plus one follow-up batch. A new list of qualifying surfaces would leave the same
classification gap for the next unlisted surface.

The narrower alternative, attacking only literal zero-finding approvals on new surfaces, covers
clap and one ripgrep attempt but misses all four tRPC attempts and both repaired ripgrep attempts:
their payloads retain hygiene findings. This is why the extension uses #185's existing mode.

Hold the recorded claims, evidence, dispositions and outputs fixed and replay dispatch eligibility
only. Classify surviving claims under the current material-survivor definition, independently of
the experiments' adjudicated recovery scores. A check that runs is additional exposure, not a
claim that its acquittals would be overturned or that a defect would be recovered. The verifier
still attacks supplied dispositions and does not become a finder.

Sources: #137's [pins](one-shot-qualification-2026-09-07/README.md),
[all 24 outcomes and batch presence](one-shot-qualification-2026-09-07/comparison-data.md), and
the per-attempt payloads and complete disposition ledgers linked below; #138's
[eight attempts, six output packets, costs and validity](bounded-discovery-decision-2026-09-11/comparison-data.md),
[loss-stage evidence](bounded-discovery-decision-2026-09-11/loss-stages.json), and
[revealed packets](bounded-discovery-decision-2026-09-11/revealed/packets/grading-packets.json).
The #137 arms are trees `bea6be143582e75bada966ee85964623ef31f167` (repaired, `v5b-10`)
and `867cf3ff0d9f097259699be4f55aa147c98a3a5d` (historical, pre-#70 `v5b-1`). #138 used
the pinned #136 policy, with the worker and finder contrasts its decision records. None of those
pins acquires this rule retroactively.

## All targets and attempts

`R` and `H` mean #137's repaired and historical arms. Counts below are findings, not raw items:
an observation is not a survivor. Every numbered attempt is included, even when its status means
this rule adds nothing.

| Target | Attempts and recorded outcome | Recorded verification | Under the new trigger |
| --- | --- | --- | --- |
| psf/requests#6667 (i) | R 01/04, H 02/03: Changes Requested | Candidate batch in all four | Unchanged: material survivors remain |
| trpc/trpc#5017 (j) | R 09/12: Approved + 1 hygiene each; H 10/11: Approved + 2 hygiene each | None | Four initial complete-ledger attacks |
| graphql/graphql-js#1582 (k) | R 17/20: Approved + 1/2 consider; H 18/19: Approved + 2/1 consider | None | Four initial complete-ledger attacks under the claim classification below |
| bokeh/bokeh#9232 (l) | R 13/16, H 14/15: Changes Requested | Candidate batch in all four | Unchanged: material survivors remain |
| grpc/grpc-go#7390 (m) | R 05/08, H 06: Approved, zero findings; H 07: Approved + 1 hygiene | Clean-verdict in 05/08/06; none in 07 | Existing three attacks unchanged; 07 gains one versus history, already required by #185 |
| BurntSushi/ripgrep#2957 (n) | R 21/24: Approved + 1 hygiene each; H 22: Approved, zero findings; H 23: Changes Requested | None in 21/24/22; candidate in 23 | Three initial complete-ledger attacks; 23 unchanged |
| grpc/grpc-go#7417 (#138 slot-2) | position-01-attempt-2 (A), 02-attempt-1 (B), 03-attempt-2 (C): Approved, zero findings | Clean-verdict in all three | Unchanged; no additional worker |
| clap-rs/clap#6212 (#138 slot-1) | position-04-attempt-1 (A): Approved, zero findings; 05-attempt-1 (B) and 06-attempt-1 (C): Changes Requested | None in A; candidate in B/C | One initial complete-ledger attack for A; B/C unchanged |

#138's discarded position-01-attempt-1 and position-03-attempt-1 stopped at runtime with
Incomplete and no approval; neither gains an approval check. Position 06 stopped on budget even
though its written output says Changes Requested. All eight attempts remain in the accounting.
No #138 attempt is certified valid: the five unresolved and three invalid attempts retain that
status. The two other reserved targets were never attempted and supply no historical verdict.

**GraphQL classification matters.** All four (k) payloads report a test that passes while exercising
the wrong branch, not a failing test or a runtime constructor regression. The current rubric's
Changed tests rule and #185's test example (historical source path omitted)
classify that as optional test quality; the other surviving claim is a declaration-consistency
suggestion with no demonstrated runtime break. Thus these are hygiene for routing, even though
the evaluator counted the test defect as material recovery and H 18/19 labelled it `kind=bug`.
The recorded labels and scores stay intact. If one instead mechanically preserved those two old
`bug` labels as material survivors, 18/19 would not gain a batch: the total below would be two
lower. The production rule calls for classifying the claim, so the main count uses that reading.

There are **13 added initial batches versus the recorded dispatches**: 12 in #137 and one in
#138. Relative to production `v5b-12`, the incremental count is **12**, since #185 already covers
(m) 07. Restricting the replay to the repaired #137 arm plus #138's control gives **seven** new
batches (j 09/12, k 17/20, n 21/24, clap 04), with no older-kind classification ambiguity.
These are exposure counts over selected historical attempts, not a production dispatch rate.

## What the added batches receive

Each batch receives its existing pinned repository/base/head/merge-base, source and rule
coordinates, and the **complete candidate disposition ledger**, including hygiene survivors and
rows routed to observations. Each row carries id, kind, one-line claim, disposition, one-line
falsification reason and decisive evidence pointer; unavailable evidence stays named unavailable.
The primary's narrative support and later ground truth are withheld. The following is an index
to the actual ledgers, not a replacement brief filtered to promising rows. Recorded issue-fit
checks that explicitly never became candidate rows remain issue-fit context.

| Added attempt | Complete ledger source and content handed to the batch |
| --- | --- |
| j R09 | [§3](one-shot-qualification-2026-09-07/j-trpc-5017/j-bea6be14-seed1-att-09-run.md#3-complete-private-disposition-ledger): unused fixture survivor, dropped `overwrite-any-distributive-branching` and `overwrite-perf-regression`, dead-branch observation. The any acquittal cites `utils.ts:12-19`, context defaults and `middleware.ts`/`procedureBuilder.ts` call sites. |
| j R12 | [§3](one-shot-qualification-2026-09-07/j-trpc-5017/j-bea6be14-seed2-att-12-run.md#3-complete-private-disposition-ledger): fixture survivor, dead-branch observation, refuted never behavior, recorded compatibility acquittal, dropped compile-cost and filename claims. The compatibility premise says operands resolve to objects or pass an `UnsetMarker` guard. |
| j H10 | [§3](one-shot-qualification-2026-09-07/j-trpc-5017/j-867cf3ff-seed1-att-10-run.md#3-complete-private-disposition-ledger): C1/C2 hygiene survivors and D1/D2/D3 drops (never behavior, filename, compile cost); retain D4's explicitly non-candidate fix check as context. D1 compares the old and new `Overwrite<X, never>` in `utils.ts`. |
| j H11 | [§3](one-shot-qualification-2026-09-07/j-trpc-5017/j-867cf3ff-seed2-att-11-run.md#3-complete-private-disposition-ledger): dead-branch and unused-fixture survivors, filename observation, recorded changeset drop, array-mapping and unknown-context drops. The latter cites `utils.ts:59-63`'s object default. |
| k R17 | [§3](one-shot-qualification-2026-09-07/k-graphql-js-1582/k-bea6be14-seed1-att-17-run.md): C1 declaration drift routed to observation, C2 test-quality survivor; L1/L2 are explicitly issue-fit rows. Evidence compares `GraphQLError.js:25,94` and the stack-fixture probe. |
| k R20 | [§3](one-shot-qualification-2026-09-07/k-graphql-js-1582/k-bea6be14-seed2-att-20-run.md): C1–C7 drops (zero-argument fixture, shared state, casts, AST lookup, suppression, pre-existing type drift, public-type intent), F1/F2 declaration/test-quality survivors. Shared-state and AST acquittals retain their bug-kind depth. |
| k H18 | [§3](one-shot-qualification-2026-09-07/k-graphql-js-1582/k-867cf3ff-seed1-att-18-run.md): C1–C8, including C3/C4 survivors, dropped constructor/type/position/AST/cast/suppression hypotheses. Preserve the recorded C4 bug kind in the evidence; eligibility is classified above. |
| k H19 | [§3](one-shot-qualification-2026-09-07/k-graphql-js-1582/k-867cf3ff-seed2-att-19-run.md): stack-fixture survivor, O1 type-drift observation, T1 resolved request, D1 shared-fixture mutation, D2 zero-argument coverage and D3 position arithmetic drops. |
| m H07 | [§3](one-shot-qualification-2026-09-07/m-grpc-go-7390/m-867cf3ff-seed2-att-07-run.md#3-complete-private-disposition-ledger): doc-comment survivor, dropped lock-handoff concurrency claim and missed-caller bug claim. `clientconn.go:922,996,1234`, `balancer_wrapper.go:255-265` and the retained race-test output support the acquittals. This is #185's existing exposure. |
| n R21 | [§3](one-shot-qualification-2026-09-07/n-ripgrep-2957/n-bea6be14-seed1-att-21-run.md#3-complete-private-disposition-ledger): grammar survivor; compinit prerequisite, autoload, CI completion, prompt-style and changelog dispositions. In particular, `faq/code-fence-prompt-style` calls the `$ source` versus `fpath` difference cosmetic at `FAQ.md:127-135`. |
| n R24 | [§3](one-shot-qualification-2026-09-07/n-ripgrep-2957/n-bea6be14-seed2-att-24-run.md#3-complete-private-disposition-ledger): grammar survivor and two requirement drops, source-before-compinit and fpath ordering, with retained execution evidence and convention/intent reasons; code-fence observation retained as recorded. |
| n H22 | [§3](one-shot-qualification-2026-09-07/n-ripgrep-2957/n-867cf3ff-seed1-att-22-run.md#3-complete-private-disposition-ledger): cand-1 through cand-5, all dropped/refuted: pre-compinit sourcing, prerequisite documentation, heading style, grammar, autoload regression. Pointers include `rg.zsh:441-446` and `FAQ.md:100,108,116,126-141`. |
| clap A04 | Authenticated pilot `./position-04/work/research-report.md` §3: C1 redundant `check_terminator` calls (performance, observation; `parser.rs:136,414`), C2 test-name mismatch (requirement, observation; `tests/builder/multiple_values.rs:1662`), C3 minimum-values bypass (bug, dropped as pre-existing; `parser.rs:133-143`, custom-terminator reproduction). All three go, including both observations. |

The clap report was read from the [sealed pilot archive](bounded-discovery-pilot-2026-09-09/sealed/README.md)
after decryption and checking its compressed plaintext SHA-256 against the published
`8d23ced49a5a5d2c129889e8a2b00c9060ed13d89eee2430a4c1216a5345f5cd`.
Its [public loss-stage record](bounded-discovery-decision-2026-09-11/loss-stages.json) corroborates
the three claims and absence of verification. Neither adjudicated clap defect was a primary
candidate. C3's premise would now be exposed, but recovering the trailing-values or option-state
defects remains unknown; the successful candidate arms had different inputs and workers.

## Incremental cost at the recorded rates

#137's clean-verdict worker charges are **$0.532058** (R05), **$0.388314** (R08) and
**$0.235155** (H06), from `usage_json.transcripts` in the corresponding
[meter records](one-shot-qualification-2026-09-07/metering/cells/). All used Sonnet 5/high,
with recorded input/output prices $2/$10 per million, cache writes ×1.25 (5m) or ×2 (1h),
reads ×0.1. These are that experiment's rates, not a current price quote. Its median worker
charge is $0.388314; observed range $0.235155–$0.532058.

#138's control clean-verdict worker cost **$0.624466**, the entire A worker column in
[the role split](bounded-discovery-decision-2026-09-11/comparison-data.md#spend-by-arm-and-role).
Only position-01-attempt-2 ran an A worker. Use it as the within-grid proxy for clap A04;
the B/C stronger-worker charges do not estimate this production-rule change.

| Scope | Additional initial batches | Worker-only estimate |
| --- | --- | --- |
| All #137 outputs versus recorded dispatches | 12 | 12 × $0.388314 = **$4.659768**; observed-charge sensitivity $2.821860–$6.384696 |
| #138 clap control versus recorded dispatch | 1 | **$0.624466** |
| Combined versus recorded dispatches | 13 | **$5.284234**; sensitivity $3.446326–$7.009162 |
| Combined incremental to production v5b-12 (#185 already covers m H07) | 12 | 11 × $0.388314 + $0.624466 = **$4.895920**; sensitivity $3.211171–$6.477104 |
| Repaired #137 arm plus #138 control only | 7 | 6 × $0.388314 + $0.624466 = **$2.954350** |

The historical-kind sensitivity excluding k H18/H19 subtracts $0.776628 from either combined
median estimate. These are arithmetic workload proxies, not billed new spend, forecasts, confidence
intervals, or cost caps. Ledger size, kind and reconstruction depth vary. Primary reconciliation
and a possible follow-up add cost; charging another equal-size worker to every new initial would
double its worker estimate, but does not bound real follow-up cost. Existing candidate work is
not recharged. No latency or recall gain is estimated.

## Transition checks before release

| State | Required behavior |
| --- | --- |
| Ordinary surface, zero findings, complete pass | One initial complete-ledger clean-verdict attack before approval |
| Ordinary surface, hygiene only | Same attack; no hygiene exception |
| Empty candidate ledger | Dispatch still required; return a scoped empty-ledger conclusion, with no invented claim or global safety assertion |
| Hygiene candidate needs a difficult trace, initial not sent | Candidate verdict and complete-ledger attack share the initial batch, after the complete pass |
| Eligible early candidate dispatch occurred before no-material eligibility was known | After primary completion and reconciliation, the remaining follow-up carries the full updated ledger if it has not already been attacked |
| Last material candidate refuted on any surface | Recompute; use the follow-up for the complete updated ledger, even if hygiene remains |
| Clean-verdict attack completed, no new required work | No self-retrigger merely because zero/material-free findings remain |
| Required attack first becomes necessary after follow-up is spent, or a required ruling fails | Verification and coverage incomplete; no third batch and no clean approval from exhaustion |
| Clean attack re-opens a row | Primary falsification, then remaining mandatory confirmation; an unconfirmed mandatory claim stays unpublished and coverage incomplete |
| Outcome-changing unanswered question or coverage gap remains | A clean-verdict conclusion does not clear it; derive status under the existing contract |

This changes exposure only. #137 and #138 retain their published inconclusive decisions and
measurement artifacts. #199 still gates any future experimental freeze. No stronger verifier,
finder, promotion, study dispatch or issue-state change is part of this delivery.
