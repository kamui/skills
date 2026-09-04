# Comparison data — holdout evaluation

**Status: template; no run has been recorded.** The layout follows
[test 4's `comparison-data.md`](../prototype-runs-2026-09-01-test-4/comparison-data.md); #60 fills
every section as cells complete. The cost section is fixed by #67 and #89 so that every run is
recorded the same way and the arms are ranked on billed production-shaped cost.

## Comparison boundaries

Written by #60 before the first cell: what is comparable across arms (same cohort, same packet,
same model), and what is not.

## Run continuity

One row per run that was interrupted and re-run. Under #60's rules an interrupted run is discarded
and its cell re-run clean; record the discard here.

## Cost

### Per run — billed usage

One row per run, pasted verbatim from
`python3 docs/research/tools/transcript_usage.py <paths> --prices 2,10 --report <run.md> --row "<arm> seed <n>"`
(see [`README.md`](README.md#metering-per-run) for the inputs); the header below is the script's
`--header` output. **Billed cost** prices every API request. **Production-shaped** subtracts the
research report's estimated output cost and is the field used for ranking.

| Run / agent | Model | Turns | Tool calls | Text-only turns | Input | Cache write | Cache read | Output | Thinking | Wall | Billed cost ($) | Report output (est.) | Production-shaped ($) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| _(target a) v5b seed 1_ | | | | | | | | | | | | | |

Group rows by target, arms in the order v5b, v2a, v5b-without-verifier, then `v5b-effort-medium`
on targets (b) and (c) only (see [`README.md`](README.md#lower-effort-primary-arm)), then the Fable
tier-split runs.

### Per arm — ranked on billed production-shaped cost

Arms are ranked on the median **production-shaped billed cost** across their runs, not on raw billed
cost or the legacy harness context-size figure.

| Rank | Arm | Runs | Median production-shaped billed cost | Median billed cost | Median research-report cost share |
| --- | --- | --- | --- | --- | --- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

Report the research-report cost share (estimated report output cost over billed cost) per arm as
well: it is the correction factor the aggregate analysis's §7 conclusion 8 waits on, and it is
expected to differ by arm.

### Legacy context-size companion

One row per run, pasted verbatim from
`python3 docs/research/tools/cost_split.py --row "<arm> seed <n>"`. The header below is that script's
`--header` output. Token cells are harness-reported where the harness meters them and self-reported
estimates elsewhere; payload and report cells carry their byte sizes and whether the token count is
`metered` or `est.` at 4 bytes per token. This table preserves the historical split and does not
determine the ranking.

| Run | Harness total | Instruction load | Repository reads | Private records | Review payload | Research report | Production-shaped |
| --- | --- | --- | --- | --- | --- | --- | --- |
| _(target a) v5b seed 1_ | | | | | | | |

Where a run's primary was not metered, pass `--harness-note "primary not metered"` so the legacy
harness-total cell says so; treat that companion row as a lower bound.

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

## Effort verification

For every run, the effort as passed and as verified from the transcript's top-level `effort` field,
read from the same lines as `message.model`, per sub-agent: the primary and each verifier batch. The
`v5b-effort-medium` rows show `medium` on the primary and the default on every verifier; every other
row shows the default throughout. A row whose verified value differs from the value passed is a
discarded run and is recorded under Run continuity, not here. Alongside it, per sub-agent: turns,
tool calls, thinking tokens, and wall clock, copied from that sub-agent's row in the
[billed-usage table](#per-run--billed-usage) above (`transcript_usage.py` on the same transcript),
the figures #68 compares across the arm. The `Thinking` column is the one the arm exists to move;
the rest show whether lower effort also consolidated the primary's turns and tool calls.

| Run | Sub-agent | Effort passed | Effort verified | Turns | Tool calls | Thinking | Wall clock |
| --- | --- | --- | --- | --- | --- | --- | --- |
| _pre-grid probe (transcript path)_ | `v5b-primary-effort-medium` | `medium` | | | | | |
| _(target b) v5b-effort-medium seed 1_ | primary | `medium` | | | | | |
| _(target b) v5b-effort-medium seed 1_ | verifier batch 1 | default | | | | | |

The `v5b` rows on targets (b) and (c) are the arm's controls; fill their turns, tool calls,
thinking, and wall here too, so the comparison reads off one table.

## Sandbox and hygiene disclosures

Per run, as self-reported. Written by #60.
