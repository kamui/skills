# Evaluation — medium primary with pinned high verifiers (issue #124)

**2026-09-06.** Fourteen planned cells; every attempt, its disposition and its cost are in
[`ledger.md`](ledger.md), every per-attempt row in [`comparison-data.md`](comparison-data.md),
and the per-target scoring in [`scoring/`](scoring/). The preregistration is
[`README.md`](README.md) §1; the screening rule is applied here exactly as frozen there.
Known-Hyper and fresh-target outcomes are reported separately, as the ticket requires.

## What ran

_Filled at close-out._

## Results by target

### (a) `hyperium/hyper#3952` — regression fixture, GT-a1 (the hot loop)

Six valid completed attempts, three per arm ([`scoring/a.md`](scoring/a.md)).

| Arm | GT-a1 recovered | Target recall | False findings | False clean | Fix level | Verifier batches |
| --- | --- | --- | --- | --- | --- | --- |
| `high` | 1 of 3 (att-01) | 33% | 0 | 2 of 3 (att-04, att-05) | invariant ×1, none ×2 | 1 of 3 |
| `medium` | 3 of 3 | 100% | 0 | 0 of 3 | invariant ×3 | 3 of 3 |

The two control misses share one shape: the primary raised the concurrency candidate, dropped it
in its own falsification ("consequence unproven"), kept two accurate test-hygiene `consider`
items, and so met no mandatory trigger — two survivors made zero-survivor mode inapplicable and
none was `must-fix`. The pinned skill then requires no verifier, the review approves, and nothing
checks the acquittal. The holdout's `v5b` seed 3 acquitted GT-a1 through a verifier that overshot;
here the acquittal never reached one. All three candidate-arm primaries published GT-a1 as
`must-fix` (P1, P1, P0, kind `concurrency`/`performance`), each with an invariant-level fix
(gate continuation on real write progress), and each therefore ran a verifier batch that confirmed
it. Every `consider` item in both arms was accurate and inside the register's "not ground truth"
allowance; no attempt asserted the iteration bound, the dev-dependency or the `Future`-contract
doubt as a defect.

### (g) `tokio-rs/bytes#698` — fresh, GT-g1 (capacity no longer consumed)

Four valid completed attempts, two per arm ([`scoring/g.md`](scoring/g.md)).

| Arm | GT-g1 recovered | Target recall | False findings | False clean | Verifier batches |
| --- | --- | --- | --- | --- | --- |
| `high` | 0 of 2 | 0% | 0 | 2 of 2 | 2 (clean-verdict) |
| `medium` | 0 of 2 | 0% | 0 | 2 of 2 | 2 |

All four approved after a verifier batch. The miss is not an effort effect: the change's stated
purpose ("reuse the full capacity") was taken as the specification, so the observable
capacity/cursor contract change was never a candidate in three attempts and was raised and
acquitted as `intentional` in the fourth (att-07, control), whose clean-verdict batch did not
re-open it. Two attempts (att-09 candidate, att-10 control) executed code at the head; att-09
measured the exact difference (capacity retained at the head, consumed at the merge-base) and
reported it as the optimization working. The register's plausible non-defects were all handled
correctly; no false findings.

### (h) `etcd-io/etcd#18749` — fresh, adjudicated clean

_Filled after the four (h) cells._

## Screening rule

_Applied at close-out over all fourteen cells; known-Hyper and fresh subsets reported separately._

## Cost

_Filled at close-out: matched pairs, absolute medians, all-attempt spend, ticket total._

## Limitations

_Filled at close-out._
