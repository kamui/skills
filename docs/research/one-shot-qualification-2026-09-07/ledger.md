# Ticket ledger — issue #137 (one-shot qualification grid, 2026-09-07 UTC)

All times UTC. The bundle is dated by UTC; the working day started on the evening of 2026-09-06
local (Pacific). Spend is billed dollars at Sonnet 5 list ($2/$10 per M tokens, cache write ×1.25
five-minute tier and ×2.0 one-hour tier, cache read ×0.1) from
[`transcript_usage.py`](../tools/transcript_usage.py) unless a row says otherwise. Session quota:
the harness reports none; `unknown` unless a notice arrives.

## Caps (written before any chargeable work)

| Cap | Value | Basis |
| --- | --- | --- |
| Planned cells | 24 | ticket #137: 6 targets × 2 arms × 2 replicates |
| Replacement cap | 2 (26 attempts) | method §1, ticket #137 |
| Pre-freeze allowance (setup, probes, target vetting, adjudication) | $15.00 | #96 pre-freeze allowance; recorded here before the first probe |
| Grading/closeout reserve | $5.00 | #96; blind adjudication of unexpected findings |
| Spend cap (ticket total) | provisional $150.00, finalized in README §Budget gate before the first reviewer dispatch | method §1: `min(1.5 × projected, $150)`; #96 absolute ceiling $150 |
| Concurrency | at most 2 cells in flight | method §3 |

This ledger row is written before any chargeable experimental preparation or capability probe for
#137, as #96 requires. Nothing below it had been spent when it was committed.

## Setup and probe entries

| # | Time | Entry | Agents / transcripts | Spend |
| --- | --- | --- | --- | --- |
| S1 | 03:52–04:16 | **Configuration probe.** Headless `claude -p --model sonnet --effort high` sessions, roots and their children, scanned with `agent_effort.py --expect-model claude-sonnet-5 --expect-effort high`: `claude-sonnet-5` and `high` on 100% of assistant lines of every root and every child, with **no** agent definition — a child inherits its parent's effort. The probe rides the vetting-hunt transcripts of S3–S6 rather than paying for dedicated probe sessions, so it carries no separate charge. | the S3–S6 transcripts | $0.00 |
| S2 | 03:49–04:05 | **Pins, snapshots and harness checks (no model cost).** Both skill trees extracted with `git archive` and re-hashed with `git write-tree`: candidate `bea6be14…`, control `867cf3ff…`, both matching #136's pins. `validate_review.py --self-test` passes on both (control 70 cases, candidate 105); each arm's own example payload validates and renders at exit 0. Runner, dispatch template, timing sidecar, close-out, blinding and aggregation tooling written; the runner dry-run-tested on targets (n), (k) and (j) — correct heads, clean trees after provisioning, fully rendered prompts, sidecars created — and the dry-run artefacts deleted. | — | $0.00 |
| S3 | 03:52–04:17 | **Vetting hunt: changed-test correctness — DISCARDED, no report.** Headless Sonnet 5 / `high`. The session fanned out to four background sub-agents, which hit GitHub's 30-per-minute code-search limit and stalled; the runtime then terminated the root under its 600-second background-wait ceiling (`Background tasks still running after 600s; terminating`). No report was produced. Recorded as a discarded pre-freeze cost; it is not subtracted from anything. The failure is why every later helper is told to work single-threaded, why `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` is exported in the cell runner, and why the cell dispatch template requires `run_in_background: false` on every sub-agent. | `358d6dd9-0f75-410e-ad56-b777f3a70b81` + 4 children | **$3.29** (harness self-report $3.348) |
| S4 | 03:52–04:14 | **Vetting hunt: ordinary behavioural defect + ordinary clean control.** Chose **`bokeh/bokeh#9232`** (l) and **`BurntSushi/ripgrep#2957`** (n); reproduced (l) deterministically across six timezones with a standalone Node script. Report: [`hunts/hunt-ordinary.md`](hunts/hunt-ordinary.md). | `02d75619-d16a-458c-9c62-5c0741260877` + children | $3.00 (harness $2.997) |
| S5 | 03:58–05:24 | **Vetting hunt: cross-file obligation.** Chose **`trpc/trpc#5017`** (j); alternates `scrapy/scrapy#6993` and `clap-rs/clap#6212` recorded. Reproduced the regression offline with `tsc` at the head and its absence at the merge-base. The most expensive helper in this bundle. Report: [`hunts/hunt-crossfile.md`](hunts/hunt-crossfile.md). | `e14b2f8d-8cf5-4f16-8f0f-cbc93a8b601e` + children | **$8.82** (harness $9.088) |
| S6 | 04:02–04:18 | **Vetting hunt: clean high-risk control.** Chose **`grpc/grpc-go#7390`** (m), with a full programmatic edit-provenance table proving no record was edited after the merge instant. Report: [`hunts/hunt-clean-highrisk.md`](hunts/hunt-clean-highrisk.md). | `e21d69bf-5baa-486e-9613-5a1c8539b346` | $1.90 (harness $1.901) |
| S7 | 04:17–04:33 | **Vetting hunt: changed-test correctness, re-run single-threaded** after S3. Chose **`graphql/graphql-js#1582`** (k), confirmed by `graphql/graphql-js#4774` (2026-06-02), which names #1582 and says the test "no longer exercised the no-stack fallback path". Report: [`hunts/hunt-changed-test.md`](hunts/hunt-changed-test.md). | `a595dda5-1567-4c80-8e45-b9d0e582eb08` | $2.66 (harness $2.663) |
| S8 | 04:37–04:49 | **Independent ground-truth adjudication, six sessions**, one per target, each told to treat the hunt's proposal as an unproven hypothesis and to rule against it if the evidence did not hold. Results: (i) **2** material defects (the adjudicator split the shared-context defect from the import-time CA-loading move and deduplicated a third proposed candidate away), (j) 1, (k) 1, (l) 1, (m) **clean**, (n) **clean**. Every defect was ruled an unintended error rather than the pull request's promised change. Registers sealed in each target directory before the freeze. | `b5b2fb38…` $1.09, `9239cfa1…` $1.59, `39cf420e…` $0.64, `20df790b…` $1.00, `744a2959…` $1.22, `2bc57433…` $1.17 | $6.71 |
| S9 | 03:49–04:38 | **Provisioning (no model cost).** Staging clones of `psf/requests`, `trpc/trpc`, `graphql/graphql-js`, `bokeh/bokeh`, `grpc/grpc-go`, `BurntSushi/ripgrep` (and of `cockroachdb/pebble` and `quic-go/quic-go`, both later rejected); truncated mirrors with negative checks; offline caches — Python virtualenv, pnpm store (1.1 GB), npm cache (87 MB), Go module cache (250 MB) and build cache (309 MB). Packets built and hashed; the context-build size and arm-identity check run on all six targets. | — | $0.00 |

**Pre-freeze subtotal (S1–S9): $26.38** against the $15.00 allowance — an overrun of $11.38,
recorded as a dated deviation in the README's §3 rather than absorbed silently. Its two causes are
in the rows above: the discarded S3 hunt ($3.29 for no report) and the S5 cross-file hunt ($8.82,
4.6× the median of the other three). The overrun does not move the ticket's $150 cap: the projection
becomes $26.38 pre-freeze + $74.16 cells + $6.20 replacements + $5.00 grading reserve ≈ **$111.74**,
still inside it. Metering-CLI figures are authoritative per method §5; the harness self-reports are
shown beside them and sum $0.44 higher across the five hunts, a residual noted rather than merged.

## Attempt ledger

Dispatch records are written before each root dispatch (method §3).

| Attempt | Cell | Dispatch record | Session | Phase reached | Disposition | Replacement | Meter row |
| --- | --- | --- | --- | --- | --- | --- | --- |

_(rows appended as they occur)_
