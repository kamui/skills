# Evaluation — issue #137 qualification grid

**The screen fails.** On six fresh execution-enabled targets, the repaired `code-review-publish`
snapshot (#136, `v5b-10`) recovered **fewer** material defects per completed review than the
historical control (`v5b-1`, pre-#70) and produced **more** false-clean outcomes, at a matched
billed cost close to parity. The measured baseline is retained. The qualification is additionally
**incomplete** because the frozen four-buggy/two-clean target mix did not survive adjudication.

Data: [`comparison-data.md`](comparison-data.md). Preregistration and deviations:
[`README.md`](README.md). Attempts and spend: [`ledger.md`](ledger.md).

## 1. The screening rule, applied

The rule was frozen in stage 1 before any reviewer ran. Candidate is the repaired arm.

| # | Gate | Threshold | Measured | Verdict |
| --- | --- | --- | --- | --- |
| 1 | Raw false findings, candidate arm, all attempts | zero | **0** | **pass** |
| 2 | False-clean outcomes | no increase | **6 (60%) vs 5 (50%)** | **fail** |
| 3 | Completion rate | not worse | 12/12 vs 12/12 | pass |
| 4 | Macro material recall, attempt-level | ≥ +10 pp | **55.0% vs 70.0% — 15 pp lower** | **fail** |
| 4b | Macro material recall, completed-only | ≥ +10 pp | 55.0% vs 70.0% — identical to 4 | **fail** |
| 5 | Matched median billed cost ratio | ≤ 1.25 | **1.057** | pass |

Two gates fail, and gate 4 fails in the wrong direction by a wide margin. Under the frozen decision
rule this is a negative screen: **the historical baseline is retained**, and nothing here authorises
adopting or reverting anything.

The failure stage is **recall and false-clean on fresh targets**, not cost and not precision. The
repaired release's cost is acceptable and its precision is perfect; it simply did not find more.

## 2. Where the difference comes from

Four of the five buggy targets are ties. The whole gap sits in two cells.

| Target | Shape | repaired | historical | Difference |
| --- | --- | --- | --- | --- |
| (k) `graphql-js#1582` | changed-test correctness | 100% | 100% | none |
| (l) `bokeh#9232` | ordinary behavioural | 100% | 100% | none |
| (j) `trpc#5017` | cross-file obligation | 0% | 0% | none — both miss it entirely |
| (i) `requests#6667` | concurrency / shared state | 75% | 100% | one repaired cell missed GT-i2 |
| (n) `ripgrep#2957` | promised change that does not work | 0% | 50% | one historical cell found GT-n1 |

- **(i)**: `att-04` (repaired) recovered GT-i1 but not GT-i2, the move of CA-bundle loading from
  lazy per-request to eager import time. The other three cells recovered both. One cell out of four.
- **(n)**: `att-23` (historical) was the only cell in the entire grid to notice that the `.zshrc`
  snippet the pull request adds carries a `$ ` prompt prefix and therefore cannot work as pasted.
  Three cells returned Approved.

That is the entire measured difference: two cells. A fifteen-point macro gap resting on two cells
out of twenty-four is not evidence that the historical policy is *better*; it is evidence that the
repaired policy is **not detectably better**, which is what this grid was built to test and what it
answers.

## 3. What both arms miss, identically

**The cross-file shape defeats both — and not for want of looking.** On (j) all four cells missed
GT-j1 and all four returned Approved. The change gates the `@internal` `Overwrite` type on
`extends object`; the obligation it breaks lives at call sites in two files the diff never touches,
where naked generic type parameters flow in. Every one of the four run reports records tracing
those call sites: a batched grep for every `Overwrite<` use and bounded reads of `middleware.ts` and
`procedureBuilder.ts`. The failure stage is the reasoning about what those reads showed, not
whether they happened. All four acquitted on the same two facts — `_ctx_out` originates from an
object literal in `deriveParamsFromConfig`, and the input sites sit behind an `UnsetMarker` guard —
and concluded that every operand reaching `Overwrite` is a resolved object type; `att-12` writes
"`_ctx_out` is always derived from an object type" in the very row that drops the compatibility
risk. None asked what an *unresolved* type parameter at a generic middleware factory does to a
distributive conditional, which is exactly GT-j1's trigger — and three of the four had correctly
reasoned about distributive collapse on `never` in the same ledger, so the mechanism class was
known and applied to the wrong edge. Because those acquittals were dropped in the primary pass,
because each cell's survivors were hygiene `consider` items that trigger no batch, and because a
type-inference surface is not in either arm's zero-survivor vocabulary, no verifier ever attacked
them (`comparison-data.md` §8). **Both arms are faithful to their own rules here.** This is the
clearest actionable finding in the grid and it is a gap in the *current* skill, not a regression:
it belongs to #129 as a question about how generic-parameter instantiation is reasoned about at
call sites, and about which acquittals earn a verifier, not to this comparison.

**GT-i1 was never fully recovered by anyone.** All seven GT-i1 recoveries across both arms found the
shared-`SSLContext` hazard through its client-certificate manifestation and none found the silent
discard of a custom adapter's own `ssl_context` — the manifestation that actually generated the
upstream bug reports. Every GT-i1 fix in the grid is therefore `partial`.

**Both arms approve while reporting the defect — which is false clean under the frozen rule.** On
(k), all four cells recovered GT-k1 with a sufficient fix and all four still derived `Approved` with
the finding at `consider`. The blind scorer exempted them because the defect was reported; the
method's definition does not, since it flags any attempt that *explicitly returns Approved* on a
buggy target, and the scoring prompt carried the same wording. The corrected count in
`comparison-data.md` §4 applies the frozen definition. A reviewer that finds a test which cannot
fail and tells the author to merge anyway has passed the change as clean, whatever it says below the
status line. It is identical in both arms — two cells each — so it moves both counts and neither
gate's direction.

## 4. Precision, verification and cost

**Zero false findings in 24 attempts, both arms.** Every published finding outside the registers was
checked against the source by a blind scorer and classified `true but not material`; several were
pre-empted by name in the registers' "not ground truth" lists. One historical attempt (`att-03`)
embedded an unsupported sub-claim — a hostname-override trigger with no mechanism in the codebase —
inside an otherwise true finding; it is recorded separately and does not meet the raw false-finding
definition. Zero observed false findings in a 24-attempt pilot is not a precision guarantee for
either arm.

**Verifier presence is identical: 6 of 12 attempts in each arm.** Neither arm ran a second batch
anywhere in the grid. Two exposures, both detailed in `comparison-data.md` §8:

- The zero-survivor gap #124 recorded on Hyper reappeared here **in the control**: `att-07`
  published `Approved` on the clean high-risk concurrency target with no verifier dispatched at all,
  leaving its concurrency acquittals unruled. The repaired arm verified both of its cells on that
  target. The control was right, but unverified.
- On (j) neither arm verified anything in any cell, and the rules of neither arm required it.

**#70's early dispatch was never exercised.** It exists only in the repaired arm, and since no
attempt in either arm ran more than one batch, there were no late mandatory candidates, no follow-up
rounds, and no incompleteness attributable to it. This grid measures nothing about it.

**Cost is near parity, with a wide spread.** Matched median ratio 1.057 against a ≤ 1.25 gate. The
arms trade places by target: the repaired arm is 26–36% cheaper on (i) and 61–175% more expensive
on (m), where its extra spend bought the clean-verdict batches the control skipped. Elapsed time is
close: median 16.9 min repaired against 14.4 min historical, tails identical at 33.2 min.

## 5. Why this qualification is incomplete

All 24 planned cells ran and completed validly, with no replacements and no session-limit event —
so the grid is complete as *executed*. It is incomplete as a *qualification* for one reason:

**The frozen target mix did not survive adjudication.** Stage 2 froze four buggy and two clean
targets. One cell then published a finding on the clean control (n) that the sealed register had not
considered; an independent adjudicator, blind to arm and replicate, ruled it material. `D_n` moved
0 → 1 and the mix became five buggy and one clean. Method §4 is explicit that a changed target mix
cannot silently satisfy the frozen design, so no full positive screen was available from the moment
that ruling landed — regardless of the numbers.

That does not weaken the negative result, but it does change which gates carry it. Gate 4 fails
under **both** truth sets: on the original four buggy targets the macro was 68.75% repaired against
75.0% historical, already 6 points the wrong way against a +10-point gate. Gate 2 is different:
under version 1 the false-clean counts are **equal**, 4/8 against 4/8 — (j)'s two zero-recovery
approvals and (k)'s two recovered-but-Approved cells in each arm — so gate 2 *passes* there and
fails only once (n)'s revision adds two repaired approvals against one historical. The revision
widened the recall gap and created the false-clean gap; the verdict does not depend on it, because
gate 4 fails either way.

Also worth stating plainly: GT-n1 is, by the adjudicator's own ruling, **the pull request's promised
change failing** — the class #124 identified and this ticket capped at one of four buggy targets.
It arrived by revision on a target frozen as clean, which the preregistration did not contemplate.
It is reported here separately for that reason. Excluding (n) entirely gives 68.75% against 75.0% —
still a failed screen.

## 6. Limitations

- **Twenty-four cells, six targets, two replicates.** Every figure here is a small-sample
  observation. The 15-point macro gap rests on two cells; a single different outcome in either
  would move it by 10 points. Nothing here establishes a population difference between the arms, in
  either direction.
- **Zero false findings does not establish an error rate** for either arm.
- **One model, one effort, one runtime.** `claude-sonnet-5` at `high`, headless Claude Code
  `2.1.263` on one macOS machine. #124 retained `high` as the default and this grid holds it fixed;
  neither result licenses an effort or model recommendation.
- **Headless sessions write the 1-hour cache tier** (priced ×2.0). Absolute dollars here are not
  comparable to the holdout's in-session cells; the matched ratios within this grid are.
- **The grid avoids the bounded-recovery path by design.** Every target's context build is under
  24,000 bytes and byte-identical between arms, so #133's chunked recovery — which only the repaired
  arm has — was never needed. On a large diff the arms would differ in a way this grid deliberately
  does not measure. `cockroachdb/pebble#5743` was rejected for exactly that reason and remains a
  fair target for a future experiment that wants to measure it.
- **Four of six targets are documentation-, type- or test-level.** The grid is light on deep runtime
  concurrency. (i) and (m) carry that shape; (j), (k), (l) and (n) do not.
- **The orchestrator saw two payloads' structure** (`att-01`, `att-02` headers) during a validity
  check before scoring began. Scoring itself was done by independent blind scorers on redacted
  copies, and the orchestrator scored nothing.
- **`att-07`'s and `att-23`'s outcomes each turn on one cell.** Both are reported as single
  observations, not as properties of their arms.

## 7. Decision

**Retain the measured baseline.** The repaired snapshot does not qualify on this evidence: it
recovers fewer material defects per completed review and returns more false cleans than the
historical control, while matching it on precision, completion and cost. This is a negative screen
under a preregistered rule, which is a completed experiment, not a failed one.

Nothing in this result argues for reverting to `v5b-1`. The repaired release carries mechanical
guarantees the control does not (#136's acceptance record), and the historical arm's advantage here
is two cells wide. What the grid establishes is narrower and more useful: **the accumulated policy
changes between `v5b-1` and `v5b-10` did not move measured material recall on fresh targets**, and
the recall ceiling is set by gaps both versions share.

Two of those gaps are worth filing against #129 rather than re-testing here:

1. **Caller tracing happened and still missed: acquittals at generic call sites reasoned only about
   resolved types.** Target (j): all four cells traced every `Overwrite` call site and acquitted on
   the assumption that every operand is a concrete object or is guarded, never asking what an
   unconstrained type parameter at a generic middleware factory does to a distributive conditional.
   The fix is not "trace callers" — they did — but a rule that a change to a generic type's
   conditional structure is checked against an unresolved type-parameter operand, and that such an
   acquittal on an `@internal` primitive with wide fan-out is presented to a verifier rather than
   dropped silently.
2. **Zero-survivor verification does not reach surfaces that are high-risk in consequence but not in
   vocabulary.** A type-inference primitive that every context composition depends on is not a
   "concurrency, failover, data-integrity, security or authorization" surface under either arm's
   wording, so acquittals there are never attacked.

The epic's baseline question (#71) is answered for this configuration: there is no measured recall
improvement to bank.
