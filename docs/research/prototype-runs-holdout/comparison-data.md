# Comparison data — holdout evaluation

**Status: the reduced grid's runs are recorded (see `evaluation.md` for what was cut).** The layout follows
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

One row per discarded or stopped run. Under #60's rules an interrupted run is discarded and its cell
re-run clean; a discarded seed number is retired.

| Run | Why | Billed | Where |
| --- | --- | --- | --- |
| (b) v5b-effort-medium seed 1 | discarded: verifier batch (a472781e1d951ee69) ran at effort `medium` (inherited from the primary), README rule "verified effort differs from passed"; root a9b5e1373c8572231 delegated the review to abb0bc7c39caba7f3 | $2.43 billed (wrapper $0.08) | reports/b/discarded/ |
| (c) v5b-effort-medium seed 1 | discarded: verifier batch (a07ff12905fc98f0d) ran at effort `medium`; root a424123345d73ce6e delegated the review to aa52c42a418dab3ee | $3.64 billed | reports/c/discarded/ |
| (b) v5b-effort-medium seed 2 (first dispatch, ad7fc47c349cfe251) | stopped by the orchestrator after ~2 min, dispatched with the pre-fix note; seed number kept (no review output produced) | see discarded-agent row | — |

No session-limit event occurred during the grid. Discarded-agent rows for the two seed-1 effort cells
are the rows above; the stopped `ad7fc47c349cfe251` dispatch produced no review output.

## Cost

### Per run — billed usage

One row per run, pasted verbatim from
`python3 docs/research/tools/transcript_usage.py <paths> --prices 2,10 --report <run.md> --row "<arm> seed <n>"`
(see [`README.md`](README.md#metering-per-run) for the inputs); the header below is the script's
`--header` output. **Billed cost** prices every API request. **Production-shaped** subtracts the
research report's estimated output cost and is the field used for ranking.

| Run / agent | Model | Turns | Tool calls | Text-only turns | Input | Cache write | Cache read | Output | Thinking | Wall | Billed cost ($) | Report output (est.) | Production-shaped ($) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| (a) v5b seed 1 | claude-sonnet-5 | 81 | 92 | 2 | 162 | 417,660 | 8,227,700 | 132,311 | 79,482 | 0:31:34 | 4.01 | 16,946 | **3.84** |
| (a) v5b seed 2 | claude-sonnet-5 | 84 | 89 | 2 | 168 | 467,346 | 8,630,250 | 153,327 | 101,070 | 0:34:17 | 4.43 | 16,666 | **4.26** |
| (a) v5b seed 3 | claude-sonnet-5 | 71 | 80 | 2 | 142 | 490,662 | 7,393,985 | 187,514 | 144,399 | 0:52:06 | 4.58 | 13,503 | **4.45** |
| (a) v5b-noverify seed 1 | claude-sonnet-5 | 68 | 70 | 1 | 136 | 159,810 | 6,299,290 | 83,959 | 53,916 | 0:17:44 | 2.50 | 8,775 | **2.41** |
| (b) v5b seed 1 | claude-sonnet-5 | 76 | 82 | 2 | 152 | 356,321 | 6,648,796 | 110,333 | 60,026 | 0:30:39 | 3.32 | 15,106 | **3.17** |
| (b) v5b seed 2 | claude-sonnet-5 | 66 | 73 | 2 | 132 | 330,274 | 6,058,532 | 99,844 | 55,324 | 0:25:17 | 3.04 | 14,026 | **2.90** |
| (b) v5b seed 3 | claude-sonnet-5 | 59 | 64 | 2 | 118 | 206,100 | 4,550,490 | 87,239 | 53,038 | 0:22:01 | 2.30 | 10,937 | **2.19** |
| (b) v5b-noverify seed 1 | claude-sonnet-5 | 54 | 59 | 1 | 108 | 133,274 | 4,422,116 | 50,067 | 27,400 | 0:11:15 | 1.72 | 7,245 | **1.65** |
| (b) v5b-effort-medium seed 2 | claude-sonnet-5 | 69 | 69 | 2 | 138 | 261,842 | 4,508,235 | 70,552 | 29,908 | 0:21:57 | 2.26 | 12,366 | **2.14** |
| (b) v5b-effort-medium seed 3 | claude-sonnet-5 | 50 | 49 | 2 | 100 | 157,556 | 2,790,240 | 58,607 | 23,178 | 0:15:54 | 1.54 | 9,652 | **1.44** |
| (b) v5b-effort-medium seed 4 | claude-sonnet-5 | 47 | 46 | 2 | 94 | 244,367 | 2,816,796 | 75,105 | 39,195 | 0:21:59 | 1.93 | 12,735 | **1.80** |
| (c) v5b seed 1 | claude-sonnet-5 | 91 | 99 | 2 | 182 | 238,191 | 10,753,479 | 79,345 | 29,742 | 0:18:19 | 3.54 | 11,733 | **3.42** |
| (c) v5b seed 2 | claude-sonnet-5 | 97 | 100 | 2 | 194 | 456,230 | 11,475,554 | 98,083 | 47,841 | 0:26:41 | 4.42 | 16,819 | **4.25** |
| (c) v5b seed 3 | claude-sonnet-5 | 105 | 117 | 2 | 210 | 291,938 | 14,501,101 | 114,392 | 58,619 | 0:25:35 | 4.77 | 14,818 | **4.63** |
| (c) panel seed 1 | claude-sonnet-5 | 207 | 231 | 6 | 414 | 1,102,092 | 24,340,413 | 262,733 | 113,193 | 1:17:09 | 10.25 | 26,539 | **9.99** |
| (c) panel seed 2 | claude-sonnet-5 | 192 | 209 | 6 | 384 | 1,060,460 | 17,037,523 | 253,948 | 104,718 | 1:17:44 | 8.60 | 17,607 | **8.42** |
| (c) panel seed 3 | claude-sonnet-5 | 211 | 246 | 6 | 422 | 1,056,736 | 18,879,797 | 281,727 | 161,896 | 1:33:18 | 9.24 | 10,772 | **9.13** |
| (c) v5b-noverify seed 1 | claude-sonnet-5 | 101 | 100 | 1 | 202 | 268,758 | 15,377,076 | 93,855 | 61,120 | 0:20:47 | 4.69 | 8,740 | **4.60** |
| (c) v5b-effort-medium seed 2 | claude-sonnet-5 | 79 | 88 | 2 | 158 | 178,343 | 6,920,091 | 57,550 | 15,236 | 0:13:28 | 2.41 | 9,731 | **2.31** |
| (c) v5b-effort-medium seed 3 | claude-sonnet-5 | 135 | 133 | 2 | 270 | 430,648 | 14,492,029 | 107,087 | 48,159 | 0:29:38 | 5.05 | 12,242 | **4.92** |
| (c) v5b-effort-medium seed 4 | claude-sonnet-5 | 81 | 79 | 2 | 162 | 207,922 | 7,599,611 | 57,712 | 17,736 | 0:17:04 | 2.62 | 11,103 | **2.51** |
| (d) v5b seed 1 | claude-sonnet-5 | 93 | 96 | 1 | 186 | 223,107 | 12,880,895 | 83,882 | 55,654 | 0:18:08 | 3.97 | 8,639 | **3.89** |
| (d) v5b seed 2 | claude-sonnet-5 | 74 | 79 | 1 | 148 | 191,191 | 8,982,539 | 51,552 | 30,532 | 0:12:03 | 2.79 | 6,692 | **2.72** |
| (d) v5b seed 3 | claude-sonnet-5 | 75 | 80 | 1 | 150 | 227,473 | 9,823,595 | 60,070 | 48,481 | 0:15:45 | 3.13 | 8,760 | **3.05** |
| (d) panel seed 1 | claude-sonnet-5 | 156 | 175 | 6 | 312 | 739,951 | 16,595,974 | 231,254 | 90,602 | 1:01:18 | 7.48 | 61,208 | **6.87** |
| (d) panel seed 2 | claude-sonnet-5 | 133 | 161 | 3 | 266 | 545,639 | 11,145,975 | 141,333 | 78,198 | 0:49:24 | 5.01 | 11,474 | **4.89** |
| (d) panel seed 3 | claude-sonnet-5 | 179 | 198 | 8 | 358 | 1,101,584 | 21,799,460 | 205,511 | 69,509 | 1:14:47 | 9.17 | 15,776 | **9.01** |
| (d) v5b-noverify seed 1 | claude-sonnet-5 | 68 | 72 | 1 | 136 | 210,551 | 9,077,616 | 65,210 | 40,720 | 0:13:51 | 2.99 | 7,975 | **2.91** |
| (e) v5b seed 1 | claude-sonnet-5 | 92 | 93 | 2 | 184 | 249,684 | 9,726,463 | 112,083 | 63,956 | 0:25:09 | 3.69 | 12,458 | **3.57** |
| (e) v5b seed 2 | claude-sonnet-5 | 98 | 101 | 2 | 196 | 288,320 | 11,839,337 | 120,949 | 67,205 | 0:29:37 | 4.30 | 17,830 | **4.12** |
| (e) v5b seed 3 | claude-sonnet-5 | 112 | 110 | 2 | 224 | 464,205 | 12,032,208 | 126,727 | 67,274 | 0:34:27 | 4.83 | 16,207 | **4.67** |
| (f) v5b seed 1-probe | claude-sonnet-5 | 45 | 49 | 1 | 90 | 136,826 | 3,803,424 | 67,197 | 44,785 | 0:13:11 | 1.77 | 6,592 | **1.71** |
| (f) v5b seed 1-r1 | claude-sonnet-5 | 41 | 50 | 1 | 82 | 143,560 | 3,625,251 | 62,776 | 38,444 | 0:12:00 | 1.71 | 6,998 | **1.64** |
| (f) v5b seed 1-r2 | claude-sonnet-5 | 47 | 49 | 1 | 94 | 158,224 | 4,538,632 | 56,133 | 33,190 | 0:12:49 | 1.86 | 6,626 | **1.80** |

Group rows by target, arms in the order v5b, v2a, v5b-without-verifier, then `v5b-effort-medium`
on targets (b) and (c) only (see [`README.md`](README.md#lower-effort-primary-arm)), then the Fable
tier-split runs.

### Per arm — ranked on billed production-shaped cost

Arms are ranked on the median **production-shaped billed cost** across their runs, not on raw billed
cost or the legacy harness context-size figure.

| Arm | Runs | Median production-shaped ($) | Median billed ($) | Median report share | Median thinking | Median turns |
| --- | --- | --- | --- | --- | --- | --- |
| v5b | 18 | 3.50 | 3.62 | 3.4% | 55,489.0 | 78.5 |
| v2a (Panel, with merged fixes) | 6 | 8.71 | 8.88 | 2.2% | 97,660.0 | 185.5 |
| v5b-noverify | 4 | 2.66 | 2.75 | 3.1% | 47,318.0 | 68.0 |
| v5b-effort-medium | 6 | 2.23 | 2.33 | 4.8% | 26,543.0 | 74.0 |

### Per target

| Target | Arm | Runs | Median production-shaped ($) | Median billed ($) | Median thinking | Median output | Median turns | Median tool calls |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| (a) | v5b | 3 | 4.26 | 4.43 | 101,070 | 153,327 | 81 | 89 |
| (a) | v5b-noverify | 1 | 2.41 | 2.50 | 53,916 | 83,959 | 68 | 70 |
| (b) | v5b | 3 | 2.90 | 3.04 | 55,324 | 99,844 | 66 | 73 |
| (b) | v5b-noverify | 1 | 1.65 | 1.72 | 27,400 | 50,067 | 54 | 59 |
| (b) | v5b-effort-medium | 3 | 1.80 | 1.93 | 29,908 | 70,552 | 50 | 49 |
| (c) | v5b | 3 | 4.25 | 4.42 | 47,841 | 98,083 | 97 | 100 |
| (c) | v2a (Panel, with merged fixes) | 3 | 9.13 | 9.24 | 113,193 | 262,733 | 207 | 231 |
| (c) | v5b-noverify | 1 | 4.60 | 4.69 | 61,120 | 93,855 | 101 | 100 |
| (c) | v5b-effort-medium | 3 | 2.51 | 2.62 | 17,736 | 57,712 | 81 | 88 |
| (d) | v5b | 3 | 3.05 | 3.13 | 48,481 | 60,070 | 75 | 80 |
| (d) | v2a (Panel, with merged fixes) | 3 | 6.87 | 7.48 | 78,198 | 205,511 | 156 | 175 |
| (d) | v5b-noverify | 1 | 2.91 | 2.99 | 40,720 | 65,210 | 68 | 72 |
| (e) | v5b | 3 | 4.12 | 4.30 | 67,205 | 120,949 | 98 | 101 |
| (f) | v5b | 3 | 1.71 | 1.77 | 38,444 | 62,776 | 45 | 49 |

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

Cells take `found`, `raised`, `acquitted`, or `not raised` per the README's scoring rule; the
adjudication behind each cell is in [`evaluation.md`](evaluation.md). Arms and seeds that were cut
are absent. Target (b) has no recall rows; its acquittal checks are in the next section.

### (a) `hyperium/hyper#3952`

| | v5b s1 | v5b s2 | v5b s3 | noverify s1 |
| --- | --- | --- | --- | --- |
| **GT-a1** — flush readiness taken as write readiness; hot loop on unbuffered writers | **found** (steady-state mechanism) | found, closing-path projection only | acquitted | acquitted |
| **GT-a1 fix** (dimension 4) | **invariant** (progress-gated retry) | branch (clear `body_rx` on `close()`) | none | none |

### (c) `python/typeshed#9458`

| | v5b s1 | v5b s2 | v5b s3 | effort s2 | effort s3 | effort s4 | noverify s1 | Panel s1 | Panel s2 | Panel s3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **GT-c1** — `__init__.pyi` missing `CredentialProvider`, `UsernamePasswordCredentialProvider` | not raised | not raised | **found** | not raised | **found** | not raised | not raised | **found** | **found** | **found** (consider; under) |
| T-c2 — `default_backoff` missing from both `__init__.pyi` and `backoff.pyi` | not raised | not raised | **found** | not raised | not raised | not raised | raised (withheld) | **found** | **found** | **found** |
| T-c3 — `MaxConnectionsError` missing from `exceptions.pyi` | not raised | not raised | not raised | not raised | not raised | not raised | not raised | **found** | **found** | **found** |
| `can_read_destructive` missing on the async parser/connection classes (adjudicated true) | found | found | not raised | found | found | found | raised (withheld) | found | found | found |
| `ExpiryT` still `float \| timedelta` (**not ground truth**: `CONTRIBUTING.md:454` asks for `float`) | — | — | — | — | — | — | — | P2 consider (in band) | **P1 must-fix (false)** | acquitted |

### (d) `astral-sh/uv#4424`

| | v5b s1 | v5b s2 | v5b s3 | noverify s1 | Panel s1 | Panel s2 | Panel s3 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **GT-d1** — `prefer-*` value naming, deferred in review, reshaped by #4602 | raised | raised | raised | raised | **found** (question) | **found** (question) | **found** (question) |
| T-d2 — `EnvironmentPreference::Any → OnlySystem` undescribed | dropped (traced to `e783a799`) | observation | observation | dropped | **found** (P2 consider, confirmed) | observation | **found** (P2 consider, confirmed) |

### (e) `pola-rs/polars#24771`

| | v5b s1 | v5b s2 | v5b s3 |
| --- | --- | --- | --- |
| **GT-e1** — question published on the benchmark claim | not raised | raised (ledger `not-verifiable`) | not raised |
| T-e1 — unchecked integer accumulation | found, P2 must-fix (over) | found, P1 must-fix (over) | found, P2 must-fix (over) |
| interval-mode leading sign accepted (un-anticipated; adjudicated true, P3 in band) | found, P1 must-fix (over) | found, P2 must-fix | found, P3 consider |

### (f) `spf13/cobra#1938` — first review at `R1`

| | v5b s1 |
| --- | --- |
| **GT-f1** — test unsets env vars at `defer` time | not raised |
| **GT-f2** — exported `GetEnvConfig` with unexported suffixes | not raised |
| GT-f3 — `off` sentinel vs `ACTIVE_HELP=0` convention | not raised |

### (f) re-review at `R2`

| Run | Prior item | Adjudicated | Run's classification | Reply posted on thread | Delta named `97b7001..1107319` | Stale probe |
| --- | --- | --- | --- | --- | --- | --- |
| (f) v5b seed 1 | `completions/getenvconfig-test-missing-subtests` (P3 consider) | fixed (`9740ecead`) | fixed | yes, `disposition=implemented` | yes | **no write** (re-fetch saw `276cddd6…`) |

## False findings and false acquittals

Both counted, per run, checked against the pinned code. Written by #60.

## Action calibration

Per run against the adjudicated band written before the runs. Written by #60.

## Model verification

`message.model` from every transcript belonging to this evaluation, read from every assistant line by
`finish_cell.py` at close-out and recorded in each run document's preamble. 77 transcripts across 34 runs; every assistant line reports `claude-sonnet-5`. The discarded seed-1 effort cells and the effort probes are listed under Run continuity and
Effort verification.

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
| pre-grid probe (definition alone) | agent-a831e533fc1365206.jsonl | `v5b-primary-effort-medium` | passed `medium` | verified `medium`, `claude-sonnet-5` |
| default-effort reference (plain sonnet dispatch, target-(b) hunt) | agent-adfbfabe6c519acea.jsonl | none | default | verified `high` on 378 lines, `claude-sonnet-5` |
| nested probe, primary | agent-a22696902ac02da05.jsonl | `v5b-primary-effort-medium` | `medium` | verified `medium` |
| nested probe, verifier through `v5b-verifier-effort-high` | agent-a3a1cb298e2222f03.jsonl | `v5b-verifier-effort-high` | `high` | verified `high`, `claude-sonnet-5` |
| first nested probe (definition not yet loaded) | agent-a4abbb7c4e6e230f7.jsonl | — | — | `Agent type 'v5b-verifier-effort-high' not found`; setup failure, not evidence |
| (b) v5b-effort-medium seed 2 | primary `ac9a0fec564b65899` | `medium` | `medium` | 47 | 46 | 15,171 | 0:16:03 |
| (b) v5b-effort-medium seed 2 | child `a44acc1c456ea0466` | `high` (definition) | `high` | 22 | 23 | 14,737 | 0:05:54 |
| (b) v5b-effort-medium seed 3 | primary `a69f1c909185a5678` | `medium` | `medium` | 32 | 32 | 18,456 | 0:13:02 |
| (b) v5b-effort-medium seed 3 | child `a4023da2f4c91a65d` | `high` (definition) | `high` | 18 | 17 | 4,722 | 0:02:52 |
| (b) v5b-effort-medium seed 4 | primary `a197db3d8e16201b3` | `medium` | `medium` | 38 | 37 | 17,206 | 0:16:14 |
| (b) v5b-effort-medium seed 4 | child `aa226a9fc5f73210a` | `high` (definition) | `high` | 9 | 9 | 21,989 | 0:05:45 |
| (b) v5b seed 1 | primary `a5230ed13aca04d71` | default | `high` | 50 | 57 | 38,114 | 0:24:15 |
| (b) v5b seed 1 | child `a86c8b7a1169ca54b` | default | `high` | 26 | 25 | 21,912 | 0:06:24 |
| (b) v5b seed 2 | primary `a50c530936f2b2486` | default | `high` | 56 | 64 | 41,658 | 0:20:40 |
| (b) v5b seed 2 | child `a70b009a771ea9a2c` | default | `high` | 10 | 9 | 13,666 | 0:04:37 |
| (b) v5b seed 3 | primary `aa3c58f385021b794` | default | `high` | 47 | 46 | 46,828 | 0:18:39 |
| (b) v5b seed 3 | child `a142b7cab98bb9b34` | default | `high` | 12 | 18 | 6,210 | 0:03:23 |
| (c) v5b-effort-medium seed 2 | primary `a54cc9962f441e686` | `medium` | `medium` | 71 | 75 | 13,874 | 0:12:18 |
| (c) v5b-effort-medium seed 2 | child `aafc129b2c74d2738` | `high` (definition) | `high` | 8 | 13 | 1,362 | 0:01:10 |
| (c) v5b-effort-medium seed 3 | primary `a3048b835a5c910d4` | `medium` | `medium` | 104 | 103 | 41,356 | 0:25:11 |
| (c) v5b-effort-medium seed 3 | child `af982b29c19a33d66` | `high` (definition) | `high` | 31 | 30 | 6,803 | 0:04:27 |
| (c) v5b-effort-medium seed 4 | primary `a4cbce050dde55fb7` | `medium` | `medium` | 74 | 73 | 15,914 | 0:15:42 |
| (c) v5b-effort-medium seed 4 | child `aee5c2423bc7b796f` | `high` (definition) | `high` | 7 | 6 | 1,822 | 0:01:23 |
| (c) v5b seed 1 | primary `a95659cf3780c6630` | default | `high` | 83 | 87 | 28,397 | 0:17:00 |
| (c) v5b seed 1 | child `aef1d09930a80d732` | default | `high` | 8 | 12 | 1,345 | 0:01:19 |
| (c) v5b seed 2 | primary `ae667a557f210796a` | default | `high` | 80 | 84 | 37,549 | 0:22:22 |
| (c) v5b seed 2 | child `a876f18ae79e06179` | default | `high` | 17 | 16 | 10,292 | 0:04:19 |
| (c) v5b seed 3 | primary `a7b9b18bb6a21757a` | default | `high` | 94 | 99 | 54,587 | 0:23:31 |
| (c) v5b seed 3 | child `af856f2a044aded9d` | default | `high` | 11 | 18 | 4,032 | 0:02:05 |

The `v5b` rows on targets (b) and (c) are the arm's controls, filled here so the comparison reads
off one table. Each run's elapsed time is its primary's wall: in all twelve runs the verifier's
span (first to last assistant timestamp) lies inside the primary's, because the primary dispatched
it in the foreground and waited, so the summed `wall` in the billed-usage table over-counts by the
verifier's span. `evaluation.md` reports the per-target medians of these columns and of elapsed
time against the controls.

## Sandbox and hygiene disclosures

Per run, as self-reported. Written by #60.
