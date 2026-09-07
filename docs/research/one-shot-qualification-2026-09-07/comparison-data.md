# Comparison data — issue #137 qualification grid

Every cell of the 24-cell grid, with verification, billed usage, timing and scored outcome. The
screening verdict is in [`evaluation.md`](evaluation.md); the preregistration and deviations are in
[`README.md`](README.md); every attempt and dollar is in [`ledger.md`](ledger.md).

Arms are identified by pinned skill tree, never by the `workflow` trailer: `bea6be14` is the
repaired #136 baseline (`v5b-10`), `867cf3ff` the historical control (`v5b-1`, pre-#70). All times
UTC. Costs are billed dollars from `transcript_usage.py --prices 2,10` over the root and every
sub-agent transcript.

## 1. Verification of the frozen conditions

`close_cell.py` scanned `message.model` and the top-level `effort` on **every assistant line of
every transcript** — 24 roots and 12 sub-agents, 2,676 assistant lines in total — before any cell
was scored. Result: `claude-sonnet-5` and `high` on 100% of lines, in both arms, primary and child.
Zero problems on all 24 attempts. Every clone passed its negative leak checks before dispatch, and
every clone with pre-installed dependencies passed the post-provisioning dirty-tree check.

| Check | Result |
| --- | --- |
| Model on every assistant line | `claude-sonnet-5`, 24/24 attempts |
| Effort on every assistant line (primary and child) | `high`, 24/24 attempts |
| Sub-agents dispatched outside the declared transport | none |
| Leak SHA reachable in any clone | none |
| Clone tree mutated by a reviewer | none |
| Reviewer read outside its sandbox | none reported |
| Attempts with `problems: []` | 24/24 |

## 2. Per-attempt rows

`R_i` is unique material defects recovered, scored blind against the target's register (version 2
for target (n); see §5). `V` is whether a verifier batch ran. Status is the review's own derived
status.

| Attempt | Target | Arm | Rep | `D_t` | `R_i` | Recall | Fix sufficiency | False findings | False clean | V | Status | Cost | Elapsed to completion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| att-01 | (i) | repaired | 1 | 2 | GT-i1, GT-i2 | 2/2 | partial, sufficient | 0 | no | yes | Changes Requested | $4.50 | 27.1 min |
| att-04 | (i) | repaired | 2 | 2 | GT-i1 | 1/2 | partial | 0 | no | yes | Changes Requested | $4.22 | 26.1 min |
| att-02 | (i) | historical | 1 | 2 | GT-i1, GT-i2 | 2/2 | partial, sufficient | 0 | no | yes | Changes Requested | $7.02 | 33.2 min |
| att-03 | (i) | historical | 2 | 2 | GT-i1, GT-i2 | 2/2 | partial, sufficient | 0 (1 unsupported sub-claim inside a true finding) | no | yes | Changes Requested | $5.66 | 30.6 min |
| att-09 | (j) | repaired | 1 | 1 | — | 0/1 | N/A | 0 | **yes** | no | Approved | $2.02 | 11.3 min |
| att-12 | (j) | repaired | 2 | 1 | — | 0/1 | N/A | 0 | **yes** | no | Approved | $2.22 | 12.5 min |
| att-10 | (j) | historical | 1 | 1 | — | 0/1 | N/A | 0 | **yes** | no | Approved | $2.34 | 13.9 min |
| att-11 | (j) | historical | 2 | 1 | — | 0/1 | N/A | 0 | **yes** | no | Approved | $2.20 | 12.6 min |
| att-17 | (k) | repaired | 1 | 1 | GT-k1 | 1/1 | sufficient | 0 | no | no | Approved + 1 consider | $2.21 | 12.5 min |
| att-20 | (k) | repaired | 2 | 1 | GT-k1 | 1/1 | sufficient | 0 | no | no | Approved + 2 consider | $2.21 | 13.4 min |
| att-18 | (k) | historical | 1 | 1 | GT-k1 | 1/1 | sufficient | 0 | no | no | Approved + 2 consider | $1.97 | 11.2 min |
| att-19 | (k) | historical | 2 | 1 | GT-k1 | 1/1 | sufficient | 0 | no | no | Approved + 1 consider | $2.16 | 12.1 min |
| att-13 | (l) | repaired | 1 | 1 | GT-l1 | 1/1 | partial | 0 | no | yes | Changes Requested | $2.98 | 18.2 min |
| att-16 | (l) | repaired | 2 | 1 | GT-l1 | 1/1 | sufficient | 0 | no | yes | Changes Requested | $4.31 | 22.0 min |
| att-14 | (l) | historical | 1 | 1 | GT-l1 | 1/1 | sufficient | 0 | no | yes | Changes Requested | $2.54 | 14.8 min |
| att-15 | (l) | historical | 2 | 1 | GT-l1 | 1/1 | sufficient | 0 | no | yes | Changes Requested | $3.96 | 24.9 min |
| att-05 | (m) | repaired | 1 | 0 | — | N/A | N/A | 0 | N/A | yes | Approved | $4.61 | 26.6 min |
| att-08 | (m) | repaired | 2 | 0 | — | N/A | N/A | 0 | N/A | yes | Approved | $6.78 | 33.1 min |
| att-06 | (m) | historical | 1 | 0 | — | N/A | N/A | 0 | N/A | yes | Approved | $2.86 | 17.6 min |
| att-07 | (m) | historical | 2 | 0 | — | N/A | N/A | 0 | N/A | **no** | Approved | $2.46 | 11.6 min |
| att-21 | (n) | repaired | 1 | 1 | — | 0/1 | N/A | 0 | **yes** | no | Approved + 1 consider | $2.45 | 15.7 min |
| att-24 | (n) | repaired | 2 | 1 | — | 0/1 | N/A | 0 | **yes** | no | Approved + 1 consider | $2.53 | 14.4 min |
| att-22 | (n) | historical | 1 | 1 | — | 0/1 | N/A | 0 | **yes** | no | Approved | $2.21 | 11.0 min |
| att-23 | (n) | historical | 2 | 1 | **GT-n1** | 1/1 | sufficient | 0 | no | yes | Changes Requested | $2.58 | 16.6 min |

Twenty-four dispatched attempts, twenty-four valid completed, twenty-four planned cells, zero
replacements, zero session-limit notices, no unattempted cell.

## 3. Recall by target and arm

`D_t` is the adjudicated unique material defect count. Clean targets have recall N/A, never 100%.
Attempt-level and completed-only views are identical here because every attempt completed validly.

| Target | Shape | `D_t` | repaired | historical |
| --- | --- | --- | --- | --- |
| (i) `psf/requests#6667` | concurrency / shared mutable state | 2 | (2/2 + 1/2)/2 = **75%** | (2/2 + 2/2)/2 = **100%** |
| (j) `trpc/trpc#5017` | cross-file obligation | 1 | (0 + 0)/2 = **0%** | (0 + 0)/2 = **0%** |
| (k) `graphql/graphql-js#1582` | changed-test correctness | 1 | (1 + 1)/2 = **100%** | (1 + 1)/2 = **100%** |
| (l) `bokeh/bokeh#9232` | ordinary behavioural change | 1 | (1 + 1)/2 = **100%** | (1 + 1)/2 = **100%** |
| (n) `BurntSushi/ripgrep#2957` | frozen clean; **buggy after revision** | 1 | (0 + 0)/2 = **0%** | (0 + 1)/2 = **50%** |
| (m) `grpc/grpc-go#7390` | clean, high-risk | 0 | N/A | N/A |
| **Macro material recall** | 5 buggy targets | | **55.0%** | **70.0%** |

Union recall, diagnostic only: repaired 60%, historical 80% macro. Union cannot satisfy a per-review
threshold and is shown only to separate "no seed found it" from "one seed found it".

**Macro on the frozen four buggy targets**, before the register revision, for reference:
repaired (75 + 0 + 100 + 100)/4 = **68.75%**, historical (100 + 0 + 100 + 100)/4 = **75.0%**. The
revision widens the gap; it does not create it.

## 4. False cleans, false findings, completion

False clean is counted over attempts on buggy targets — five targets, ten attempts per arm after
the revision.

| Quantity | repaired | historical |
| --- | --- | --- |
| False cleans (count / rate over buggy attempts) | **4 / 10 = 40%** | **3 / 10 = 30%** |
| — on (j) | 2 | 2 |
| — on (n) | 2 | 1 |
| Completed-only false cleans | 4 / 10 | 3 / 10 |
| Raw false findings, all 24 attempts | **0** | **0** |
| Unique false claims | 0 | 0 |
| Action / severity errors | 0 | 0 |
| Unsupported sub-claims inside true findings | 0 | 1 (att-03) |
| Zero-recovery attempts on buggy targets that did **not** claim clean | 0 | 0 |
| Valid completed / dispatched | 12/12 = 100% | 12/12 = 100% |
| Valid completed planned cells | 12/12 | 12/12 |

Every zero-recovery attempt on a buggy target returned Approved, so the false-clean count and the
zero-recovery count coincide in both arms.

## 5. Truth-set revision

| | Version 1 (sealed pre-dispatch) | Version 2 (post-grid) |
| --- | --- | --- |
| `D_i` | 2 | 2 |
| `D_j` | 1 | 1 |
| `D_k` | 1 | 1 |
| `D_l` | 1 | 1 |
| `D_m` | 0 | 0 |
| `D_n` | **0 (clean)** | **1 (GT-n1)** |
| Buggy / clean target mix | 4 / 2 | **5 / 1** |
| Macro recall, repaired | 68.75% | **55.0%** |
| Macro recall, historical | 75.0% | **70.0%** |

One new candidate was escalated across the whole grid: GT-n1, raised by exactly one cell (att-23).
It went to an independent adjudicator with the arm, replicate and cost labels removed
([`adjudication/nc1-ruling.md`](adjudication/nc1-ruling.md)), which ruled it **material**. Every
arm and attempt was then rescored against version 2. No other unexpected finding anywhere in the
grid survived as a new candidate: all the rest were classified `true but not material`, and several
were pre-empted by name in their register's "not ground truth" list.

This is a truth-set revision, not changed reviewer performance. Both the version-1 and version-2
scores are shown above.

## 6. Fix sufficiency and efficiency

| Quantity | repaired | historical |
| --- | --- | --- |
| Total recoveries `Σ R_i` | 7 | 9 |
| Sufficient fixes `Σ S_i` | 4 | 7 |
| Aggregate fix sufficiency | 4/7 = **57%** | 7/9 = **78%** |
| Sufficient-outcome macro recall | 40.0% | 60.0% |
| All-attempt spend | $41.04 | $37.96 |
| Spend per recovery | $5.86 | $4.22 |
| Spend per valid completed attempt | $3.42 | $3.16 |

Both arms recovered GT-i1 only through its client-certificate manifestation and never through the
silent discard of an adapter's own `ssl_context`, so **every** GT-i1 recovery in the grid is
`partial`. That is a shared gap, not a difference between arms.

## 7. Billed cost and matched pairs

Matched cost charges each cell all its attempts; there were no replacements, so cell cost equals
attempt cost throughout.

| Target | Rep | repaired | historical | ratio |
| --- | --- | --- | --- | --- |
| (i) | 1 | $4.50 | $7.02 | 0.642 |
| (i) | 2 | $4.22 | $5.66 | 0.745 |
| (j) | 1 | $2.02 | $2.34 | 0.864 |
| (j) | 2 | $2.22 | $2.20 | 1.008 |
| (k) | 1 | $2.21 | $1.97 | 1.120 |
| (k) | 2 | $2.21 | $2.16 | 1.024 |
| (l) | 1 | $2.98 | $2.54 | 1.173 |
| (l) | 2 | $4.31 | $3.96 | 1.090 |
| (m) | 1 | $4.61 | $2.86 | 1.613 |
| (m) | 2 | $6.78 | $2.46 | 2.754 |
| (n) | 1 | $2.45 | $2.21 | 1.111 |
| (n) | 2 | $2.53 | $2.58 | 0.981 |
| **Matched median ratio** | | | | **1.057** (n=12) |

Twelve complete matched pairs, no zero-cost control, no unknown charge. The spread is wide — 0.64
to 2.75 — and the median sits close to parity because the two arms trade places by target: the
repaired arm is markedly cheaper on (i) and markedly more expensive on the clean high-risk target
(m), where it ran a clean-verdict batch in both cells and the control ran one in only one.

Per-arm distributions over all twelve cells:

| Quantity | repaired (min / median / max) | historical (min / median / max) |
| --- | --- | --- |
| Billed cost | $2.02 / **$2.75** / $6.78 | $1.97 / **$2.50** / $7.02 |
| Production-shaped estimate | $1.94 / $2.60 / $6.62 | $1.90 / $2.39 / $6.85 |
| Elapsed to validated payload | 6.8 / **13.7** / 30.8 min | 7.1 / **11.8** / 31.1 min |
| Elapsed to completion | 11.3 / **16.9** / 33.2 min | 11.0 / **14.4** / 33.2 min |
| Agent span sum | 11.3 / 18.2 / 36.7 min | 10.9 / 15.1 / 37.3 min |
| Thinking tokens | 35,600 / 46,625 / 81,845 | 28,653 / 40,282 / 83,635 |
| Assistant turns | 42 / 55.5 / 132 | 42 / 54.5 / 129 |
| Tool calls | 49 / 64.5 / 138 | 46 / 63.5 / 141 |

Per-arm absolute medians and per-target medians:

| Target | repaired median | historical median |
| --- | --- | --- |
| (i) | $4.36 | $6.34 |
| (j) | $2.12 | $2.27 |
| (k) | $2.21 | $2.07 |
| (l) | $3.64 | $3.25 |
| (m) | $5.70 | $2.66 |
| (n) | $2.49 | $2.39 |

The production-shaped column subtracts an estimate of the research-report output cost. It is an
**estimate**, not billed spend, and no gate uses it. Tail figures are the observed maximum in a
twelve-cell sample, not a distributional tail.

## 8. Verifier-batch presence per attempt

The ticket requires, per attempt, which verification mode ran and whether every acquitted
`concurrency` / `invariant` / `security` / `bug` row on a high-risk surface was ever ruled on by a
verifier. Presence is read from the transcripts — a batch either produced a sub-agent transcript or
it did not — not from the reviewer's own narration.

| | repaired | historical |
| --- | --- | --- |
| Attempts that dispatched a verifier batch | **6 / 12** | **6 / 12** |
| Attempts with no verification of any kind | 6 / 12 | 6 / 12 |
| Batches beyond the first (follow-up) | 0 | 0 |

Per target, and the mode observed:

| Target | Surface | repaired | historical |
| --- | --- | --- | --- |
| (i) | concurrency / shared state, high risk | candidate batch in both cells | candidate batch in both cells |
| (j) | type-level inference, ordinary | **none in either cell** | **none in either cell** |
| (k) | changed test, ordinary | **none in either cell** | **none in either cell** |
| (l) | ordinary behavioural | candidate batch in both cells | candidate batch in both cells |
| (m) | concurrency, high risk, clean | clean-verdict batch in both cells | clean-verdict batch in one cell, **none in att-07** |
| (n) | documentation / shell, ordinary | none in either cell | none in att-22; candidate batch in att-23 |

Two exposures are worth naming, and neither separates the arms in the direction the repaired
release was expected to improve:

1. **The zero-survivor gap appears in the control, not the candidate.** On (m), the adjudicated
   clean high-risk target, `att-07` (historical) published `Approved` having dispatched no verifier
   at all. Its own ledger's acquittals on a concurrency surface were therefore never independently
   ruled on. The repaired arm ran a clean-verdict batch in both of its (m) cells. This is the
   failure shape #124 recorded on Hyper, and here it lands on the historical arm. It cost nothing
   in correctness — the target is clean and `att-07` was right — but the verdict was unverified.
2. **On (j) neither arm verified anything, in any cell, and all four returned Approved.** The
   surface is a widely-fanned-out `@internal` type primitive whose call sites live in untouched
   files. Neither arm's zero-survivor trigger fires there: neither rules a TypeScript type-inference
   surface a concurrency, failover, data-integrity, security or authorization boundary, so
   zero-survivor mode is simply inapplicable, and with no survivor there is no candidate batch and
   no related-acquittal set. Both arms are **faithful to their own rules**; this is a policy gap
   shared by both, not a dispatch failure in either, and not something the repaired release
   narrowed.

Early dispatch (#70/PR #125) exists only in the repaired arm. It never changed an outcome here: no
attempt in either arm ran more than one batch, so there were no late mandatory candidates, no
follow-up rounds, and no incompleteness attributable to a batch dispatched early. The mechanism was
not exercised by this grid.
