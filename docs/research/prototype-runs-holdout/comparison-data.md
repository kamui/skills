# Comparison data — holdout evaluation

**Status: template; no run has been recorded.** The layout follows
[test 4's `comparison-data.md`](../prototype-runs-2026-09-01-test-4/comparison-data.md); #60 fills
every section as cells complete. The cost section is fixed now by #67 so that every run is recorded
the same way and the arms are ranked on the same column.

## Comparison boundaries

Written by #60 before the first cell: what is comparable across arms (same cohort, same packet,
same model), and what is not.

## Run continuity

One row per run that was interrupted and re-run. Under #60's rules an interrupted run is discarded
and its cell re-run clean; record the discard here.

## Cost

One row per run, pasted verbatim from `python3 docs/research/tools/cost_split.py --row "<arm> seed <n>"`
(see [`README.md`](README.md#metering-per-run) for the inputs). Token cells are the harness-reported
figures where the harness meters them and self-reported estimates elsewhere; the payload and report
cells carry their byte sizes and whether the token count is `metered` or `est.` at 4 bytes per token.
**Production-shaped** is the harness total minus the research report.

### Per run

| Run | Harness total | Instruction load | Repository reads | Private records | Review payload | Research report | Production-shaped |
| --- | --- | --- | --- | --- | --- | --- | --- |
| _(target a) v5b seed 1_ | | | | | | | |

Group rows by target, arms in the order v5b, v2a, v5b-without-verifier, then the Fable tier-split runs.
Where a run's primary was not metered, say so in the row's harness-total cell and treat the row as a
lower bound in the ranking.

### Per arm — ranked on production-shaped

Arms are ranked on the median **production-shaped** figure across their runs, not on the raw harness
total. The raw column stays for continuity with the corpus, whose figures are all raw and therefore
upper bounds for production.

| Rank | Arm | Runs | Median production-shaped | Median harness total | Median research-report share |
| --- | --- | --- | --- | --- | --- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

Report the research-report share (report tokens over harness total) per arm as well: it is the
correction factor the aggregate analysis's §7 conclusion 8 waits on, and it is expected to differ by
arm.

## Output

Per run: status, finding count by priority, questions, observations, verifier dispatches. Written by
#60.

## Ground-truth matrix

Per target: one row per ground-truth item, one column per run. Written by #60 after each target's
ground truth is committed and before any of its cells run.

## False findings and false acquittals

Both counted, per run, checked against the pinned code. Written by #60.

## Action calibration

Per run against the adjudicated band written before the runs. Written by #60.

## Model verification

`message.model` from every transcript belonging to this evaluation, per run. Written by #60 before
scoring.

## Sandbox and hygiene disclosures

Per run, as self-reported. Written by #60.
