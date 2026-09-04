# Comparison data — holdout evaluation

**Status: boundaries and ground-truth rows written; no run has been recorded.** The layout follows
[test 4's `comparison-data.md`](../prototype-runs-2026-09-01-test-4/comparison-data.md); #60 fills
every section as cells complete. The cost section is fixed by #67 and #89 so that every run is
recorded the same way and the arms are ranked on billed production-shaped cost.

## Comparison boundaries

Written before the first cell.

**Comparable across arms and seeds on one target:** the packet (byte-identical; SHA-256 recorded
below), the mirror and clone construction, the model (`claude-sonnet-5` on every agent), the
harness session shape (each run's orchestrator a background sub-agent, verifiers its children),
the conditions list in the README, and the scoring rubric. Within a target, every run is one
cohort and its billed figures rank against each other.

**Comparable across targets:** dimension scores only, as counts per target; billed cost is not,
because the targets differ in diff size, repository size, and language.

**Not comparable:** anything against tests 1–4. Those cohorts ran earlier skill versions
(`v5a-1`, `v2a-1`), one seed, and, before test 4, un-truncated mirrors or inherited models. The
holdout grid is the first data on `v5b-1`.

**Arm-specific caveats.** `v5b-noverify` withholds every candidate that needed mandatory
verification, so its recall is the primary's recall before verification and its status is always
`Incomplete` or `Changes Requested`; compare its ledger, not only its payload, to `v5b`'s. The
Panel arm's row label records whether it ran as `v2a` (with merged fixes) or `v2b` (after #59).
`v5b-effort-medium` differs from `v5b` in the primary's effort and nothing else, on targets (b)
and (c) only. Target (f) is the only publishing target; its runs are one seed at a time and have
network access to the fork.

| Target | Packet SHA-256 | Snapshot commits (`v5b` / Panel) |
| --- | --- | --- |
| (a) | _pending_ | _pending_ |
| (b) | _pending_ | _pending_ |
| (c) | _pending_ | _pending_ |
| (d) | _pending_ | _pending_ |
| (e) | _pending_ | _pending_ |
| (f) first / re-review | _pending_ | _pending_ |

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

Items are defined per target in [`README.md`](README.md#targets). Cells take `found`, `raised`,
`acquitted`, or `not raised` per the scoring rule; one column per run, filled after each cell
completes. Target (b)'s matrix has no recall rows; its false-finding and false-acquittal counts
are in the next section.

### (a) `hyperium/hyper#3952`

| | v5b s1 | v5b s2 | v5b s3 | Panel s1 | Panel s2 | Panel s3 | noverify s1 | noverify s2 | noverify s3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **GT-a1** — flush readiness taken as write readiness; hot loop on unbuffered writers | | | | | | | | | |
| **GT-a1 fix** (dimension 4: `invariant` / `branch` / `none`) | | | | | | | | | |

### (c) `python/typeshed#9458`

| | v5b s1 | v5b s2 | v5b s3 | Panel s1 | Panel s2 | Panel s3 | noverify s1 | noverify s2 | noverify s3 | effort s1 | effort s2 | effort s3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **GT-c1** — `__init__.pyi` missing `CredentialProvider`, `UsernamePasswordCredentialProvider` | | | | | | | | | | | | |
| T-c2 — `default_backoff` missing from both `__init__.pyi` | | | | | | | | | | | | |
| T-c3 — `MaxConnectionsError` missing from `exceptions.pyi` | | | | | | | | | | | | |

### (d) `astral-sh/uv#4424`

| | v5b s1 | v5b s2 | v5b s3 | Panel s1 | Panel s2 | Panel s3 | noverify s1 | noverify s2 | noverify s3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **GT-d1** — `prefer-*` value naming, deferred in review, reshaped by #4602 | | | | | | | | | |
| T-d2 — `EnvironmentPreference::Any → OnlySystem` undescribed | | | | | | | | | |

### (e) `pola-rs/polars#24771`

| | v5b s1 | v5b s2 | v5b s3 | Panel s1 | Panel s2 | Panel s3 | noverify s1 | noverify s2 | noverify s3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **GT-e1** — question published on the benchmark claim | | | | | | | | | |
| T-e1 — unchecked integer accumulation | | | | | | | | | |

### (f) `spf13/cobra#1938` — first review at `R1`

| | v5b s1 | v5b s2 | v5b s3 | Panel s1 | Panel s2 | Panel s3 | noverify s1 | noverify s2 | noverify s3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **GT-f1** — test unsets env vars at `defer` time | | | | | | | | | |
| **GT-f2** — exported `GetEnvConfig` with unexported suffixes | | | | | | | | | |
| GT-f3 — `off` sentinel vs `ACTIVE_HELP=0` convention | | | | | | | | | |

### (f) re-review at `R2`

One row per prior item the run published, with the adjudicated classification from the README
and the classification the run gave; plus the stale-head probe's outcome (`no write` /
`wrote`).

| Run | Prior item | Adjudicated | Run's classification | Reply posted on thread | Delta named `97b7001..1107319` | Stale probe |
| --- | --- | --- | --- | --- | --- | --- |
| _(f) v5b seed 1_ | | | | | | |

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
tool calls, thinking tokens, and wall clock, copied from that sub-agent's block in the run document
(the `transcript_usage.py` output pasted there under item 1 of the
[metering rule](README.md#metering-per-run); the [billed-usage table](#per-run--billed-usage) above
carries only each run's total row), the figures #68 compares across the arm. The `Thinking` column
is the one the arm exists to move; the rest show whether lower effort also consolidated the
primary's turns and tool calls.

| Run | Sub-agent | Effort passed | Effort verified | Turns | Tool calls | Thinking | Wall clock |
| --- | --- | --- | --- | --- | --- | --- | --- |
| _pre-grid probe (transcript path)_ | `v5b-primary-effort-medium` | `medium` | | | | | |
| _(target b) v5b-effort-medium seed 1_ | primary | `medium` | | | | | |
| _(target b) v5b-effort-medium seed 1_ | verifier batch 1 | default | | | | | |

The `v5b` rows on targets (b) and (c) are the arm's controls; fill their turns, tool calls,
thinking, and wall here too, so the comparison reads off one table.

## Sandbox and hygiene disclosures

Per run, as self-reported. Written by #60.
