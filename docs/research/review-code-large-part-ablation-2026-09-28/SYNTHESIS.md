# How this note was produced

[README.md](README.md) is the synthesis of an arena run on 2026-09-28. Three candidates wrote the
same analysis independently from one brief. One was picked as the base, and the best parts of the
other two were folded into it.

## Seats

| Seat | Model | Result |
| --- | --- | --- |
| Candidate 1 | Claude Opus 5.5, high effort | Completed |
| Candidate 2 | Claude Opus 5.5, high effort | Completed |
| Candidate 3 | Claude Fable 5.1, high effort | Completed. **Base** |
| Cross-judge | Claude Opus 5.5, high effort | Saw the candidates by number only |
| Picker | Claude Fable 5.1 | Read all three, scored, grafted and verified |

**Dropout.** The requested Codex GPT-6 Astra seat did not run. Codex refused the model for this
account: "The 'gpt-6-astra' model is not supported when using Codex with a ChatGPT account". The
seat went to a second Opus candidate.

**Bias to weigh.** The picker and the base share a model. The cross-judge is a different model
and reached the same base without knowing which model wrote which candidate.

## The pick

| Criterion | Candidate 1 | Candidate 2 | Candidate 3 |
| --- | :---: | :---: | :---: |
| Large functional parts, measured | 5 / 5 | 4 / 4 | 4 / 4 |
| Grounded benefit claims | 4 / 4 | 4 / 3 | 5 / 4 |
| Comparison with the built-in reviewers | 4 / 4 | 5 / 4 | 5 / 5 |
| Runnable, observable ablations | 5 / 5 | 4 / 5 | 4 / 4 |
| Staged test design | 4 / 4 | 3 / 4 | 5 / 5 |
| Decision usefulness and honesty | 4 / 4 | 4 / 4 | 5 / 5 |
| **Total** | **26 / 26** | **24 / 24** | **28 / 27** |

Each cell is the picker's score, then the judge's.

Candidate 3 is the base for three reasons.

- **It counted every filed composition, not only the valid ones.** That is how it found the
  three `must-fix` findings the verifier confirmed and grading ruled false. The other two
  excluded those attempts and concluded that verification never touched precision.
- **It buys a matched control from the first cell** for the lowest price of the three.
- **Its scripts are the easiest to extend.** Each variant edit has to match its source text
  exactly once, so a moved line fails loudly.

## Convergence

All three candidates reached these independently, so the note ships them as the consensus:

- Independent verification is the first part to test.
- The requirements ledger produced no finding, and the pinned targets cannot show its benefit.
- Re-review and the pull-request target cannot be tested on the pinned targets.
- The admission core is the likely source of precision and is not a removal candidate.
- Historical reviews cannot serve as the control.

## Grafts

| From | What was taken | Where it is |
| --- | --- | --- |
| Candidate 2 | The idea of simulating a pass rule's error rates. Rewritten to read recovery rates from the filed grades and to model this note's own stages | `measure.py rules`; README section 5 |
| Candidate 2 | Counting a finalizer refusal by its "failed with exit" text, because a pipeline around the finalizer can still exit 0 | `was_refused` in `measure.py`; README section 2, R |
| Candidate 2 | "Cost follows turns, not bytes", with the cost of one kilobyte | README Result and section 2 |
| Candidate 2 | Turning off reviewer-run execution, recorded as considered and deferred | README section 6 |
| Candidate 1 | The part by loaded-set matrix, reconciled to the budget test's five totals. Applied to the base's section-level parts | `measure.py sizes`; README section 1 |
| Candidate 1 | The premise-only variant, tested on a trimmed copy, as the fallback fixed in advance | `variants.py S`; README section 4 |
| Candidate 1 | What premise-only batches cost. Recomputed under the base's allocation | `measure.py phases`; README section 2, V |
| Candidate 1 | The built-in reviewers' prompt sizes and discovery strategies | README section 3 |
| Cross-judge | Shares of spend are reported as attributed spend, not as the expected saving | README section 4 |
| Cross-judge | The precision claim is marked weak: another model, and a difference of two reviews | README section 3 |
| Cross-judge | The 31 of 32 confirmations are given both readings, including a lenient verifier | README section 2, V |

## Changes to the base

| Base claim | Problem | Change |
| --- | --- | --- |
| Stage 2 margins of 1 on recall, action and remedy, cost limit 0.85 | The simulation shows they reject a variant that changes nothing 63% of the time | Margins of 3 and a cost limit of 0.90: 25% |
| Stage 1 rejects when the variant misses any defect its control recovers, on 2 of 3 targets | Rejects a harmless variant 12% to 24% of the time on recall alone | Rejects when the variant recovers nothing and its control recovers something: 2% to 10% |
| "50 finalized at first run; 18 refused" | Counted only tool errors. The cross-judge found 14 refusals in 35 baseline runs, not 4 | 46 of 115 runs refused; 33 of 65 reviews finished without a refusal |
| "180 source reads in 27 reviews", with a count of the fields looked up | Not produced by the base's script | Replaced with a reproducible count: at least 127 reads in 26 reviews. The link to the missing example fields is marked as inference |
| Detection probabilities of 0.84 and 0.34 | Assumed a control with no in-jurisdiction finding | Replaced with simulated rates |
| Trimmed copies written under the note's directory | Would write inside the repository | Copies go to a temporary directory |
| Script paths fixed to one checkout | Not portable | Derived from the script's location |

## Rejected

| From | What | Why |
| --- | --- | --- |
| Candidate 1 | A 20-cell first stage at about $55 | The base's 8 cells buy a matched control for about $21 |
| Candidate 1 | Finalizer failures of 3 in 25, and source reads in 2 of 20 baseline reviews | Undercounted; its pattern stops at `\|` inside a search |
| Candidate 1 | "Seven partial rows violate `output.md:13`" | All seven are supporting rows. Every acceptance row short of `met` sits in a review with a finding |
| Candidate 2 | A first stage with no control | Its own note argues no usable baseline exists under enforced isolation |
| Candidate 2 | Rejecting on one "attributable" false finding, settled by replaying it through a verifier | One event decides, and the replay step has never been tried |
| Candidate 2 | A split of 54 historical and 10 enforced reviews | The #384 matched run is enforced. The enforced population is 13 |
| Candidate 2 | Source reads in 39 of 64 reviews | Its pattern also matches composition writes |
| Candidate 2 | Reviewer-run execution as the second candidate | 1.6 KB, and the highest recall risk on the targets where recall is weakest |
| Candidate 2 | "Premise batches are a small share" | Counted baseline worker cost only. They are 7% to 10% of spend |

## Verification

| Check | Result |
| --- | --- |
| Every `measure.py` subcommand runs from this directory | Pass: `sizes`, `exercise`, `outcomes`, `phases`, `machinery`, `rules` |
| The part matrix totals equal the budget test's | Pass: 73,188, 29,684, 48,405, 60,582, 57,598 |
| The cost join equals every filed charge | Pass: largest difference $0.000001 |
| The grafted refusal count changes only refusal figures | Pass: the phase report differs from the base's in the four refusal lines and nowhere else |
| `variants.py --tests base V S Q` | Pass. Base, S and Q pass all ten test files. V fails the four expected test cases and no others |
| Every `path:line` citation names an existing file and line | Pass: 59 checked. 12 are section ranges that end on the blank line before the next heading |
| Counts checked by an independent script written before the candidates were read | Pass: compositions, rulings, false findings by attempt, and skill trees per arm |
| The repository after the run | Only this directory is new. One bytecode cache left by the cross-judge in `skills/review-code/scripts/` was removed |

Not verified:

- **No review was run.** Every claim about what a variant would do is a hypothesis.
- **The four failing test cases for V were not fixed.** The check shows which tests break, not
  that a repaired variant passes.
- **Two borrowed counts were not recomputed:** that 10 of 34 recovered defects cite run output,
  which is a keyword match, and the built-ins' discovery strategies, which are the benchmark's
  own labels.
