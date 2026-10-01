# Comparison data — issue #153, the #138 pilot after grading

Every attempt the epic dispatched, joined after #152's rulings froze: the arm and target from the
sealed schedule and redaction map, operational validity from #151's fidelity assessment, completion
and cost from its manifest and reconciliation, and the per-attempt scoring fields from #152's
amended derived fields. Eighteen of the twenty-four planned cells were never attempted and appear
here as missing. The screening verdicts are in [`evaluation.md`](evaluation.md); the scorer's own
output is [`scorecard-v2.md`](scorecard-v2.md) (graded truth) and [`scorecard-v1.md`](scorecard-v1.md)
(truth as registered before grading).

## 1. Truth after grading

| Slot | Target | Status | Defects as registered (v1) | Defects after grading | Attempted |
| --- | --- | --- | --- | --- | --- |
| slot-1 | clap-rs/clap#6212 | buggy | GT-p1 | GT-p1, GT-p2 (v2) | yes |
| slot-2 | grpc/grpc-go#7417 | clean | none | none (v1) | yes |
| slot-3 | nats-io/nats-server#6593 | buggy | GT-r1 | GT-r1 (v1) | no |
| slot-4 | nats-io/nats-server#7395 | buggy | GT-s1 | GT-s1 (v1) | no |

The clean/buggy mix is unchanged by grading: the one clean slot stays clean, and the buggy slot the
pilot ran on gained a second, adjudicator-confirmed defect, which moves its recall denominator from one
to two for every attempt on it. Two buggy slots were never attempted, so every macro over buggy targets
is unavailable rather than zero.

## 2. Per-attempt rows

`D_t` and `R_i` are against the graded truth (v2); the v1 column shows recovery against the register as
frozen. `Valid` is #151's operational validity: no attempt is `valid`, because the launch argv was never
retained (five `unresolved`) or a protocol rule was broken (three `invalid`). False clean is a property of
the published status on a buggy target. `V` is whether a verifier batch ran and what it received.

Duplicates are items beyond the first on a concept the attempt already claimed (supported or
false alike); bundled is one item naming more than one concept, which is not a duplicate. Both are
counted over the ruled items, so a zero is established, not omitted.

| Pos | Attempt | Cell | Arm | Validity | Completion | Status | `D_t` | `R_i` (v2) | Recall v2 | Recall v1 | Sufficient / partial | Raw items | Concepts | Duplicates | Bundled | False findings | False clean | V | Settled |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | position-01-attempt-1 | slot-2-A-replicate-1 | A | invalid | stopped-runtime | Incomplete | 0 (clean) | — | N/A | N/A | — | 0 | 0 | 0 | 0 | 0 | N/A | n/a | $0.0000000 |
| 1 | position-01-attempt-2 | slot-2-A-replicate-1 | A | unresolved | complete | Approved | 0 (clean) | — | N/A | N/A | — | 1 | 1 | 0 | 0 | 0 | N/A | clean-verdict batch | $3.8595330 |
| 2 | position-02-attempt-1 | slot-2-B-replicate-1 | B | unresolved | complete | Approved | 0 (clean) | — | N/A | N/A | — | 0 | 0 | 0 | 0 | 0 | N/A | clean-verdict batch | $3.8777270 |
| 3 | position-03-attempt-1 | slot-2-C-replicate-1 | C | invalid | stopped-runtime | Incomplete | 0 (clean) | — | N/A | N/A | — | 0 | 0 | 0 | 0 | 0 | N/A | n/a | $1.5838690 |
| 3 | position-03-attempt-2 | slot-2-C-replicate-1 | C | unresolved | complete | Approved | 0 (clean) | — | N/A | N/A | — | 1 | 1 | 0 | 0 | 0 | N/A | clean-verdict batch | $7.0003047 |
| 4 | position-04-attempt-1 | slot-1-A-replicate-1 | A | unresolved | complete | Approved | 2 | — | 0.000 | 0.000 | — | 2 | 2 | 0 | 0 | 0 | **yes** | none (policy) | $4.5304828 |
| 5 | position-05-attempt-1 | slot-1-B-replicate-1 | B | invalid | complete | Changes Requested | 2 | GT-p1, GT-p2 | 1.000 | 1.000 | GT-p2 / GT-p1 | 1 | 2 | 0 | 1 | 0 | no | candidate batch (1, 0 finder-origin) | $6.3671277 |
| 6 | position-06-attempt-1 | slot-1-C-replicate-1 | C | unresolved | stopped-budget | Changes Requested | 2 | GT-p1, GT-p2 | 1.000 | 1.000 | GT-p2 / GT-p1 | 2 | 2 | 0 | 0 | 0 | no | candidate batch (2, 1 finder-origin) | $9.0040632 |

Raw items across the six packets: 7, of which 3 findings, 0 false findings, 0 false non-finding items, 0 unresolved rulings, 0 action errors, 0 priority errors, 1 unsupported explicit safety claims. Concepts claimed: 8 over 7 items; duplicate items on a concept: 0 (of them false: 0); bundled items: 1.

## 3. Arm scorecards (frozen scorer, graded truth)

| Arm | Attempts | Valid completed | Completion | Macro recall (all) | Macro recall (completed) | False clean | Raw false findings | Sufficient-outcome recall | Fix sufficiency | Billed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 3 | 0 | 0.000 | n/a | n/a | 1 (1.000) | 0 | 0.000 | n/a | $8.3900158 |
| B | 2 | 0 | 0.000 | n/a | n/a | 0 (0.000) | 0 | 0.500 | 0.500 | $10.2448547 |
| C | 3 | 0 | 0.000 | n/a | n/a | 0 (0.000) | 0 | 0.500 | 0.500 | $17.5882369 |

Both macros are unavailable in every arm: two of the three buggy targets have no attempt, and no
attempt is a valid completed outcome. The per-target figures below are what was measured.

### Per-target recall on the one buggy target attempted

| Arm | Attempts on slot-1 | Recall v2 (all attempts) | Recall v1 (all attempts) | Valid completed | Recovered | Sufficient fixes | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 1 | 0.000 | 0.000 | 0 | — | — | position-04-attempt-1: unresolved, complete |
| B | 1 | 1.000 | 1.000 | 0 | GT-p1, GT-p2 | GT-p2 | position-05-attempt-1: invalid, complete |
| C | 1 | 1.000 | 1.000 | 0 | GT-p1, GT-p2 | GT-p2 | position-06-attempt-1: unresolved, stopped-budget |

Against v1 the two recovering attempts hold one recovery each and no sufficient fix, because the one
fix ruled sufficient restores the defect that grading added (GT-p2), not the registered one (GT-p1).

## 4. Screens

### Against graded truth (v2)

**B against A — inconclusive.**

- zero candidate-arm false findings — pass: 0 raw false finding items (0 of them in invalid or incomplete attempts)
- no worse false-clean count or rate — pass: B: 0 (0.0) against A: 1 (1.0)
- no worse completion — pass: B: 0.0 against A: 0.0
- macro material recall gain (all attempts) — inconclusive: a buggy target has no attempts in this view, so the macro is unavailable
- macro material recall gain (completed only) — inconclusive: a buggy target has no attempts in this view, so the macro is unavailable
- matched billed cell-cost ratio — pass: median 1.205 over 2 matched pairs (gate <= 1.25)
- blocked — macro material recall is unavailable in the all attempts view
- blocked — macro material recall is unavailable in the completed only view
- blocked — planned cells with no attempt: slot-1-A-replicate-2, slot-1-B-replicate-2, slot-1-C-replicate-2, slot-2-A-replicate-2, slot-2-B-replicate-2, slot-2-C-replicate-2, slot-3-A-replicate-1, slot-3-A-replicate-2, slot-3-B-replicate-1, slot-3-B-replicate-2, slot-3-C-replicate-1, slot-3-C-replicate-2, slot-4-A-replicate-1, slot-4-A-replicate-2, slot-4-B-replicate-1, slot-4-B-replicate-2, slot-4-C-replicate-1, slot-4-C-replicate-2
- blocked — planned cells attempted but with no valid completed outcome: slot-1-A-replicate-1, slot-1-B-replicate-1, slot-1-C-replicate-1, slot-2-A-replicate-1, slot-2-B-replicate-1, slot-2-C-replicate-1

**C against A — inconclusive.**

- zero candidate-arm false findings — pass: 0 raw false finding items (0 of them in invalid or incomplete attempts)
- no worse false-clean count or rate — pass: C: 0 (0.0) against A: 1 (1.0)
- no worse completion — pass: C: 0.0 against A: 0.0
- macro material recall gain (all attempts) — inconclusive: a buggy target has no attempts in this view, so the macro is unavailable
- macro material recall gain (completed only) — inconclusive: a buggy target has no attempts in this view, so the macro is unavailable
- matched billed cell-cost ratio — fail: median 2.106 over 2 matched pairs (gate <= 1.25)
- blocked — macro material recall is unavailable in the all attempts view
- blocked — macro material recall is unavailable in the completed only view
- blocked — planned cells with no attempt: slot-1-A-replicate-2, slot-1-B-replicate-2, slot-1-C-replicate-2, slot-2-A-replicate-2, slot-2-B-replicate-2, slot-2-C-replicate-2, slot-3-A-replicate-1, slot-3-A-replicate-2, slot-3-B-replicate-1, slot-3-B-replicate-2, slot-3-C-replicate-1, slot-3-C-replicate-2, slot-4-A-replicate-1, slot-4-A-replicate-2, slot-4-B-replicate-1, slot-4-B-replicate-2, slot-4-C-replicate-1, slot-4-C-replicate-2
- blocked — planned cells attempted but with no valid completed outcome: slot-1-A-replicate-1, slot-1-B-replicate-1, slot-1-C-replicate-1, slot-2-A-replicate-1, slot-2-B-replicate-1, slot-2-C-replicate-1

### Against truth as registered (v1)

**B against A — inconclusive.**

- zero candidate-arm false findings — pass: 0 raw false finding items (0 of them in invalid or incomplete attempts)
- no worse false-clean count or rate — pass: B: 0 (0.0) against A: 1 (1.0)
- no worse completion — pass: B: 0.0 against A: 0.0
- macro material recall gain (all attempts) — inconclusive: a buggy target has no attempts in this view, so the macro is unavailable
- macro material recall gain (completed only) — inconclusive: a buggy target has no attempts in this view, so the macro is unavailable
- matched billed cell-cost ratio — pass: median 1.205 over 2 matched pairs (gate <= 1.25)
- blocked — macro material recall is unavailable in the all attempts view
- blocked — macro material recall is unavailable in the completed only view
- blocked — planned cells with no attempt: slot-1-A-replicate-2, slot-1-B-replicate-2, slot-1-C-replicate-2, slot-2-A-replicate-2, slot-2-B-replicate-2, slot-2-C-replicate-2, slot-3-A-replicate-1, slot-3-A-replicate-2, slot-3-B-replicate-1, slot-3-B-replicate-2, slot-3-C-replicate-1, slot-3-C-replicate-2, slot-4-A-replicate-1, slot-4-A-replicate-2, slot-4-B-replicate-1, slot-4-B-replicate-2, slot-4-C-replicate-1, slot-4-C-replicate-2
- blocked — planned cells attempted but with no valid completed outcome: slot-1-A-replicate-1, slot-1-B-replicate-1, slot-1-C-replicate-1, slot-2-A-replicate-1, slot-2-B-replicate-1, slot-2-C-replicate-1

**C against A — inconclusive.**

- zero candidate-arm false findings — pass: 0 raw false finding items (0 of them in invalid or incomplete attempts)
- no worse false-clean count or rate — pass: C: 0 (0.0) against A: 1 (1.0)
- no worse completion — pass: C: 0.0 against A: 0.0
- macro material recall gain (all attempts) — inconclusive: a buggy target has no attempts in this view, so the macro is unavailable
- macro material recall gain (completed only) — inconclusive: a buggy target has no attempts in this view, so the macro is unavailable
- matched billed cell-cost ratio — fail: median 2.106 over 2 matched pairs (gate <= 1.25)
- blocked — macro material recall is unavailable in the all attempts view
- blocked — macro material recall is unavailable in the completed only view
- blocked — planned cells with no attempt: slot-1-A-replicate-2, slot-1-B-replicate-2, slot-1-C-replicate-2, slot-2-A-replicate-2, slot-2-B-replicate-2, slot-2-C-replicate-2, slot-3-A-replicate-1, slot-3-A-replicate-2, slot-3-B-replicate-1, slot-3-B-replicate-2, slot-3-C-replicate-1, slot-3-C-replicate-2, slot-4-A-replicate-1, slot-4-A-replicate-2, slot-4-B-replicate-1, slot-4-B-replicate-2, slot-4-C-replicate-1, slot-4-C-replicate-2
- blocked — planned cells attempted but with no valid completed outcome: slot-1-A-replicate-1, slot-1-B-replicate-1, slot-1-C-replicate-1, slot-2-A-replicate-1, slot-2-B-replicate-1, slot-2-C-replicate-1

## 5. Matched cost

Cells matched by target and replicate, each charged every attempt including its discarded predecessor.
Two pairs exist; the other six planned pairs per contrast have no member.

| Target | Replicate | A | B | C | B/A | C/A | C/B |
| --- | --- | --- | --- | --- | --- | --- | --- |
| slot-1 | 1 | $4.5304828 | $6.3671277 | $9.0040632 | 1.405 | 1.987 | 1.414 |
| slot-2 | 1 | $3.8595330 | $3.8777270 | $8.5841737 | 1.005 | 2.224 | 2.214 |

Medians over the two pairs: B/A 1.205, C/A 2.106, C/B 1.814 (gate ≤ 1.25 for the two screens; C/B is reported, not gated).

### Spend by arm and role

Per-role figures are #151's recovered split from the retained per-transcript costs; the residual is the
settled charge no transcript accounts for, carried as unassigned.

| Arm | Attempts | Primary | Verifier | Finder | Unassigned residual | Settled |
| --- | --- | --- | --- | --- | --- | --- |
| A | 3 | $7.7481640 | $0.6244660 | $0 | $0.0173858 | $8.3900158 |
| B | 2 | $8.4330350 | $1.7767460 | $0 | $0.0350737 | $10.2448547 |
| C | 3 | $12.1541070 | $2.8375500 | $2.5600680 | $0.0365119 | $17.5882369 |

### Spend columns for the epic

| Column | USD |
| --- | --- |
| Pre-freeze (targets, probes) | 10.9378407 |
| Shared setup and selection, charged once | 0.1527100 |
| Review attempts, all eight, discards included | 36.2231074 |
| Charged grading (#152) | 3.0168006 |
| This decision (#153) | 0 |
| Retained uncertainty | 0.164316 |

## 6. Elapsed time

Root elapsed is the whole attempt from dispatch to exit; the sidecar events come from #130's timing
record inside the sealed evidence. A stopped attempt's duration is censored at the stop and is not a
completion. Every arm ran its verifier in the foreground by the frozen rule, so these are this harness's
timings, not the policy's production timing.

| Attempt | Arm | Completion | Root elapsed | To validated payload | To completion | Censored |
| --- | --- | --- | --- | --- | --- | --- |
| position-01-attempt-1 | A | stopped-runtime | n/a | n/a | n/a | yes |
| position-01-attempt-2 | A | complete | 31.1 min | 29.8 min | 31.0 min | no |
| position-02-attempt-1 | B | complete | 20.2 min | 19.0 min | 20.2 min | no |
| position-03-attempt-1 | C | stopped-runtime | 8.2 min | n/a | 8.2 min | yes |
| position-03-attempt-2 | C | complete | 31.3 min | 26.0 min | 31.3 min | no |
| position-04-attempt-1 | A | complete | 18.5 min | 14.4 min | 18.5 min | no |
| position-05-attempt-1 | B | complete | 27.8 min | 23.8 min | 27.8 min | no |
| position-06-attempt-1 | C | stopped-budget | 35.8 min | n/a | 35.8 min | yes |

## 7. Where each defect was found or lost

Coordinator judgments from each attempt's own stage records, made after the rulings froze
([`loss-stages.json`](loss-stages.json) carries the evidence pointers). `Admissible` is the screen's view
once operational validity is joined.

| Attempt | Arm | Defect | Outcome | Stage or origin | Verified | Fix | Admissible |
| --- | --- | --- | --- | --- | --- | --- | --- |
| position-04-attempt-1 | A | GT-p1 | missed | never-discovered; also omitted-from-verification-by-policy | — | — | — |
| position-04-attempt-1 | A | GT-p2 | missed | never-discovered; also omitted-from-verification-by-policy | — | — | — |
| position-05-attempt-1 | B | GT-p2 | recovered | origin: primary | independent-confirmed | sufficient | no: invalid on protocol grounds: a read outside the permitted roots (fidelity-assessment.json), replacement-eligible and never replaced |
| position-05-attempt-1 | B | GT-p1 | recovered | origin: verifier-added | independent-confirmed | partial | no: invalid on protocol grounds: a read outside the permitted roots (fidelity-assessment.json), replacement-eligible and never replaced |
| position-06-attempt-1 | C | GT-p2 | recovered | origin: primary | independent-confirmed | sufficient | no: stopped-budget and operationally unresolved: not a valid completed outcome |
| position-06-attempt-1 | C | GT-p1 | recovered | origin: finder; also publication-or-cap-loss | independent-confirmed | partial | no: stopped-budget and operationally unresolved: not a valid completed outcome |

On the clean target, arm C's finder raised two concurrency claims and the primary rejected both
before verification; both rejections were correct, and the clean-verdict batch upheld them.

### Scope selector

| Slot | Selected scope | Defect sites | Miss |
| --- | --- | --- | --- |
| slot-1 | `clap_builder/src/parser/parser.rs Parser::parse 130-144` | GT-p1 at parser.rs:135-138; GT-p2 at parser.rs:135-138 | no |
| slot-2 | `xds/internal/balancer/priority/balancer.go run 260-289` | none | no |

## 8. Unattempted cells

18 of 24 planned cells were never dispatched and stay unavailable: `slot-1-A-replicate-2`, `slot-1-B-replicate-2`, `slot-1-C-replicate-2`, `slot-2-A-replicate-2`, `slot-2-B-replicate-2`, `slot-2-C-replicate-2`, `slot-3-A-replicate-1`, `slot-3-A-replicate-2`, `slot-3-B-replicate-1`, `slot-3-B-replicate-2`, `slot-3-C-replicate-1`, `slot-3-C-replicate-2`, `slot-4-A-replicate-1`, `slot-4-A-replicate-2`, `slot-4-B-replicate-1`, `slot-4-B-replicate-2`, `slot-4-C-replicate-1`, `slot-4-C-replicate-2`.

