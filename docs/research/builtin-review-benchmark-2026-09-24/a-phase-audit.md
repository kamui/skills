# A review cost and elapsed-time audit

The 20 valid A reviews cost **$15.0843316** at the frozen rates. Candidate verifier workers
account for $0.7622641, clean-verdict verifier workers for $0.2323321, and primary requests for
$14.0897354. The retained records do not split primary charges among context building,
inspection, reference reads, and rendering. The invalid Astro attempt adds $0.9035311.
Together these reconcile to the published **$15.99**, including rounding.

This retrospective audit addresses [#386](https://github.com/kamui/skills/issues/386), within
[#380](https://github.com/kamui/skills/issues/380). It leaves
[#387](https://github.com/kamui/skills/issues/387) deferred: worker-reference reads are visible,
but their removable cost is not measured. No benchmark was dispatched, no scores or skill
instructions changed, and additional benchmark spend is $0.

## Scope and method

Inputs are pinned to repository commit `5b8c1c5b4dbda494da414d07e7008b5435c4357b` and run
[`2026-09-24-builtin-baseline`](../../../bench/runs/2026-09-24-builtin-baseline/manifest.json).
A used Sonnet 5, high effort, and skill tree `c3c53da5381dace16876b0f5b7abe4bccc6bc58b`.
The table below enumerates all 20 valid reviews and the separate invalid attempt.

Only those A attempts' committed `attempt.json`, `usage-requests.jsonl`, `audit.json`, and
`composition.json` supplied execution evidence. Existing scoring mappings supplied A's final
quality outcomes, using v2 for Requests, tRPC, and Bokeh and v1 for the other targets, as pinned
by [`results.v2.json`](../../../bench/runs/2026-09-24-builtin-baseline/results.v2.json).
No external transcript archive, attempt work directory, or B/C transcript was accessed.
Calculations and the detailed quality crosswalk stayed in disposable local files. This report
publishes aggregates and evidence locations, without command bodies, prompts, or transcript excerpts.

The calculation followed the request accounting in
[`file_attempt.py`](../../../bench/tools/file_attempt.py) and
[`transcript_usage.py`](../../../bench/tools/transcript_usage.py):

1. Deduplicate by request id, retaining each usage field's maximum and the earliest/latest
   observed timestamps. Check for duplicate ids across attempts too. The 21 files contain
   427 unique requests and no duplicate rows; the 20 valid reviews contain 403 requests.
2. Check that every request names A's frozen model and effort, and that its cache-write
   total equals its five-minute plus one-hour writes. All tiers are known; no fallback price
   is needed. Separate fresh input, the two cache-write tiers, cache reads, and output.
3. Resolve the model/date pair in the manifest against
   [`rates.json`](../../../bench/rates.json). Its 2026-09-24 prices per million tokens are
   $2 input, $2.50 five-minute writes, $4 one-hour writes, $0.20 cache reads, and $10 output.
   Multiply each token count by its price and divide by 1,000,000, using decimal arithmetic.
   Sum before rounding. Do not subtract reporting or thinking tokens.
4. Separate primary and worker requests by their transcript identifiers. Each worker-bearing
   attempt has exactly one worker transcript, one recorded initial verifier batch, and tasks
   of only one type. Classify that worker as candidate verification or clean-verdict verification
   from `record.verification.tasks`. Ten valid reviews have no worker or batch. Cross-check
   worker counts against `attempt.observed.subagent_count`; no mixed or follow-up batch needs
   a speculative split.
5. Compare each calculated charge with its attempt record and its A-only row in
   [`ledger.md`](ledger.md). Compare their sum with the A total in `results.v2.json`.
   Reconcile time separately using the recorded dispatch and payload events and the observed
   assistant timestamp envelopes, as defined below.

Worker assignment is an inference supported by the matching transcript count, recorded batch,
task type, and dispatch operation. The committed audit flattens commands and file reads across
actors and omits their timestamps/request ids. Consequently it cannot price a primary command,
separate a mixed request, or join a reference read to a charged request. A request also resends
cached context from earlier work; charging a whole request to its next tool would not measure
the marginal cost of that tool.

## Charge reconciliation

These are aggregate request charges per attempt, in dollars. `Primary` is unallocated across
primary accounting categories. `Worker` is candidate verification except for the two gRPC
rows, which are clean-verdict verification. `Elapsed` is dispatch to validated payload in
seconds. `Worker span` is the observed assistant envelope, not execution or critical-path time.

Target letters match the frozen cohort: i Requests, j tRPC, k GraphQL.js, l Bokeh, m gRPC,
n ripgrep, o Astro, p Hono, q soba, and r Base UI. Each attempt links to its retained artifacts.

| Attempt | Target / replicate | Calculated $ | Attempt record $ | Primary $ | Worker $ | Elapsed s | Worker span s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [att-005](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-005/) | q / 1 | 0.7421554 | 0.742155 | 0.7421554 | 0.0000000 | 112 | 0.000 |
| [att-046](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-046/) | q / 2 | 0.6018470 | 0.601847 | 0.6018470 | 0.0000000 | 87 | 0.000 |
| [att-013](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-013/) | p / 1 | 0.8597607 | 0.859761 | 0.7796744 | 0.0800863 | 139 | 12.347 |
| [att-049](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-049/) | p / 2 | 0.8668629 | 0.866863 | 0.7874432 | 0.0794197 | 146 | 12.270 |
| [att-016](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-016/) | r / 1 | 0.7705038 | 0.770504 | 0.7705038 | 0.0000000 | 130 | 0.000 |
| [att-052](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-052/) | r / 2 | 0.6687456 | 0.668746 | 0.6687456 | 0.0000000 | 131 | 0.000 |
| [att-018](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-018/) | i / 1 | 1.0273668 | 1.027367 | 0.9523368 | 0.0750300 | 224 | 12.629 |
| [att-055](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-055/) | i / 2 | 1.3324660 | 1.332466 | 1.2224730 | 0.1099930 | 297 | 25.030 |
| [att-020](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-020/) | l / 1 | 0.9118416 | 0.911842 | 0.8036794 | 0.1081622 | 175 | 21.431 |
| [att-062](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-062/) | l / 2 | 0.6758129 | 0.675813 | 0.5707174 | 0.1050955 | 136 | 17.402 |
| [att-027](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-027/) | k / 1 | 0.4515954 | 0.451595 | 0.4515954 | 0.0000000 | 66 | 0.000 |
| [att-065](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-065/) | k / 2 | 0.6866480 | 0.686648 | 0.6866480 | 0.0000000 | 120 | 0.000 |
| [att-029](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-029/) | n / 1 | 0.4461254 | 0.446125 | 0.4461254 | 0.0000000 | 92 | 0.000 |
| [att-068](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-068/) | n / 2 | 0.3925192 | 0.392519 | 0.3925192 | 0.0000000 | 71 | 0.000 |
| [att-031](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-031/) | o / 1 | 0.7973486 | 0.797349 | 0.6907912 | 0.1065574 | 160 | 30.678 |
| [att-074](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-074/) | o / 2 | 0.8433042 | 0.843304 | 0.7453842 | 0.0979200 | 153 | 19.169 |
| [att-034](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-034/) | m / 1 | 0.9712195 | 0.971220 | 0.8425226 | 0.1286969 | 178 | 30.416 |
| [att-079](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-079/) | m / 2 | 1.0006906 | 1.000691 | 0.8970554 | 0.1036352 | 180 | 19.765 |
| [att-041](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-041/) | j / 1 | 0.5810550 | 0.581055 | 0.5810550 | 0.0000000 | 118 | 0.000 |
| [att-082](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-082/) | j / 2 | 0.4564630 | 0.456463 | 0.4564630 | 0.0000000 | 80 | 0.000 |
| **20 valid reviews** | | **15.0843316** | **15.084333** | **14.0897354** | **0.9945962** | **2,795** | **201.137** |
| [att-071, invalid](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-071/) | o / 2 | 0.9035311 | 0.903531 | 0.8201494 | 0.0833817 | 158 | 16.614 |
| **All A attempts** | | **15.9878627** | **15.987864** | **14.9098848** | **1.0779779** | **2,953** | **217.751** |

Every attempt differs from its six-decimal filed charge by at most $0.0000005. Summing those
rounded charges gives the results file's $15.987864, $0.0000013 above the unrounded calculation.
Each A ledger row agrees within half a cent; their displayed sum is $15.99. The invalid
attempt is retained in the Astro replicate-2 cell's charge, which is $1.7468353 with att-074.
It supplies no valid-review quality evidence. Setup, grading, probes, and other arms are outside
this A-cell reconciliation, not unexplained residual charges.

## Accounting categories and token mix

The following partitions cover 100% of billed dollars. A dash means unavailable attribution,
not zero work. Primary preparation and return reconciliation for verifier batches remain in
`Unknown primary`; the worker rows measure only the worker's requests.

| Category | Valid-review $ | Share | Invalid-attempt $ | Attribution |
| --- | ---: | ---: | ---: | --- |
| Context building/fetch | — | — | — | Included in unknown primary |
| Primary inspection | — | — | — | Included in unknown primary |
| Primary reference reads/re-reads | — | — | — | Included in unknown primary |
| Candidate verifier batches, worker requests | 0.7622641 | 5.0534% | 0.0833817 | 8 valid batches, 9 confirmed candidates; 1 separate invalid batch |
| Clean-verdict verifier batches, worker requests | 0.2323321 | 1.5402% | 0.0000000 | 2 gRPC batches, 5 premises ruled holds |
| Rendering/repair | — | — | — | Included in unknown primary |
| Unknown primary | 14.0897354 | 93.4064% | 0.8201494 | No request-to-tool/phase join |
| **Total** | **15.0843316** | **100%** | **0.9035311** | All requests priced once |

| Population/category | Requests | Fresh input | Cache write 5m | Cache write 1h | Cache read | Output |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Valid, unknown primary | 358 | 716 | 0 | 1,661,237 | 23,569,877 | 272,938 |
| Valid, candidate verifier | 34 | 68 | 167,037 | 0 | 814,328 | 18,167 |
| Valid, clean-verdict verifier | 11 | 22 | 44,999 | 0 | 300,103 | 5,977 |
| **Valid total** | **403** | **806** | **212,036** | **1,661,237** | **24,684,308** | **297,082** |
| Invalid, unknown primary | 21 | 42 | 0 | 90,455 | 1,469,027 | 16,444 |
| Invalid, candidate verifier | 3 | 6 | 19,925 | 0 | 68,686 | 1,982 |
| **Invalid total** | **24** | **48** | **19,925** | **90,455** | **1,537,713** | **18,426** |
| **All A attempts** | **427** | **854** | **231,961** | **1,751,692** | **26,222,021** | **315,508** |

The worker-only clean-verdict charge is 1.54% of valid cost. Removing it cannot by itself
produce a 20% aggregate reduction. Its associated primary overhead is unknown, and its cost
does not establish that the checks can safely be removed. The audit does not test #387's
median per-target savings threshold.

## Elapsed time and overlap

All 20 valid attempts have dispatch, validated-payload, and completion events; payload and
completion agree. Their elapsed sum is 2,795 seconds and median is 133.5 seconds. The invalid
attempt reaches a validated payload and stops after 158 seconds, with no completion event.
These are sums of review latencies, not the experiment's calendar duration.

For each transcript, define its **observed envelope** as the earliest request `first_seen`
through the latest `last_seen`. These are assistant-record timestamps, not API starts or
tool start/end events. An envelope includes gaps, tool work, and waiting; it excludes work
before the first assistant record. Summed worker envelopes are therefore neither active
worker execution time nor additional critical-path time.

Every worker envelope sits inside its primary envelope. Candidate workers sum to 150.956
seconds and clean-verdict workers to 50.181 seconds across valid reviews. Actual worker
durations and their critical-path contributions are unavailable. **All 2,795 valid seconds
and 158 invalid seconds remain unknown by accounting category.** The envelope reconciliation
below accounts for the entire recorded elapsed interval without inventing phase durations.

| Timing quantity, seconds | 20 valid | Invalid att-071 | All A attempts |
| --- | ---: | ---: | ---: |
| Primary envelope sum | 2,699.818 | 155.671 | 2,855.489 |
| Worker envelope sum | 201.137 | 16.614 | 217.751 |
| Subtract primary/worker envelope overlap | 201.137 | 16.614 | 217.751 |
| Add recorded-window time outside envelopes | 99.809 | 2.329 | 102.138 |
| Subtract envelope overhang past payload timestamp | 4.627 | 0.000 | 4.627 |
| **Recorded dispatch-to-payload sum** | **2,795.000** | **158.000** | **2,953.000** |

The wrapper records whole seconds while request records retain milliseconds. Fourteen valid
attempts' final assistant timestamp exceeds the recorded payload time by 0.002–0.607 seconds,
totalling 4.627 seconds. This is consistent with timestamp truncation, not evidence of a
post-validation phase. Intersect envelopes with the recorded dispatch-to-payload window;
count the overhang separately rather than silently changing the wrapper event. The equation
above holds for each of the 21 attempts, not just the total.

There is also overlap **between** A attempts. The union of valid dispatch-to-payload windows
is 2,541 seconds; their sum exceeds that union by 254 seconds. Including att-071, the union
is 2,699 seconds, again with 254 seconds of overlap. Neither union includes gaps between A
attempts or measures time spent on other arms.

Astro replicate 2 has a separate retry-inclusive wait: 158 seconds for the invalid attempt,
101 seconds between its stop and replacement dispatch, and 153 seconds for att-074, totalling
412 seconds. Across the 20 cells, replacing that cell's 153-second final-attempt latency with
412 seconds gives 3,054 seconds of summed cell waits. The 101-second gap has no A request
charge and no known cause; it is not assigned to a review phase.

## Observed quality contributions

The private crosswalk compared the recorded verifier tasks, candidate inputs and returned
corrections embedded in A's audit commands, final compositions, and A-only mapping entries.
Only aggregate observations appear here. A correction field alone is not a demonstrated
improvement: several restate the input remedy. No available artifact establishes the
counterfactual review without that work, and final records cannot expose every dropped candidate.

| Category | Observation | What remains unproven |
| --- | --- | --- |
| Context building/fetch | All 20 final compositions report complete coverage and retain intent/coverage records. | The contribution of context building to a particular discovery and its marginal cost. These are reported outcomes, not a new completeness judgment. |
| Primary inspection | Final A outputs recover registered defects both with candidate verification and without it. The two GraphQL.js and two ripgrep reviews recover defects without workers; four Base UI/tRPC reviews without workers recover none. | The point of first discovery and any causal precision benefit of inspection substeps. |
| Primary reference reads/re-reads | Six valid audits include explicit reads of worker-only reference text. Two of those reviews have no worker, establishing primary reads there. | Actor attribution in the four worker-bearing audits, repeated-reading cost, and any quality contribution. |
| Candidate verifier batches | Eight valid batches confirm nine candidates; none of the recorded tasks is refuted. The candidates correspond to nine recovered defect instances across Hono, Requests, Bokeh, and Astro. Astro's two final priorities are lower than their input priorities; one return explicitly requests the downgrade and narrows the impact. Bokeh includes an anchor correction and remedy refinements. | New discovery caused by verification, prevented false findings, and a remedy becoming sufficient because of verification. No action changes are visible between these candidate inputs and final findings. |
| Clean-verdict verifier batches | Both gRPC reviews finish Approved with no findings, after three and two concurrency premises respectively are ruled holds. The existing mappings retain clean outcomes. | Whether the checks prevented a false finding or would detect a defect in another change. Preserving a clean verdict is an observed association, not proof of dispensability. |
| Rendering/repair | All valid payloads were filed successfully. Bokeh retains an accounting repair that changes a correction's anchor representation before final rendering. | The repair's price or a discovery benefit. A representation repair is not a changed defect verdict. |

The candidate classification was checked against
[att-055's composition](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-055/composition.json)
and audit: one worker, one initial batch, two candidate confirmations, and two corresponding
final findings. Its $0.1099930 worker charge covers both candidates; no evidence splits it
between them. The final Requests mapping still rates their remedies partial and flags the
compatibility finding's action. Confirmation did not establish remedy sufficiency or correct action.

Both clean-verdict classifications were checked against
[att-034](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-034/composition.json) and
[att-079](../../../bench/runs/2026-09-24-builtin-baseline/attempts/att-079/composition.json).
Each has one worker and one safety-premise batch, zero candidate tasks, zero findings, and no
outstanding verification. Their worker charges are $0.1286969 and $0.1036352; their observed
worker envelopes are 30.416 and 19.765 seconds. The two soba reviews also remain clean, with
no workers; different targets and risks make that a description, not an ablation.

## Reading overhead and the decision for #387

The six audits with explicit worker-reference reads are att-016, att-055, att-065, att-074,
att-034, and att-079. They contain eleven direct document reads: five of `verifier.md` and six
of `verifier-concurrency.md`. The two without workers are att-016 and att-065. The invalid
att-071 has two additional reads, excluded from the valid count. A byte count of a file was
not counted as a text read. Each valid audit also records one explicit read of each of
`targets.md`, `rubric.md`, `output.md`, and `verification.md`; those records show no repeated
direct read of those four files. This count covers explicit file reads and shell `cat`
operands, not text emitted by generated briefs/examples or content recovered after truncation.

Thus there is observable worker-reference reading, including primary reading where no worker
exists. There is **no measured dollar amount** for removing it, nor evidence that redundant
primary reads dominate. The maximum available cost pool is the unallocated $14.0897354,
which also pays for necessary work. It is not a savings estimate or an upper bound on safe
savings. This evidence does not satisfy #387's entry condition for its specific text change.
Keep that experiment deferred; do not substitute dropping clean-verdict batches.

## Minimal missing export

To refine attribution without a rerun, an authorized custodian would need to export metadata
only from these A attempts. Do not inspect prohibited work directories or proprietary B/C
transcripts to obtain it. Keep the export private and publish only resulting aggregates.

- A pseudonymous request/actor join, with parent-worker and verifier-batch relationships,
  reusing the retained usage totals. Include request start/end and tool start/end timestamps
  when actually retained; label absent events rather than reconstructing them from order.
- For each tool event, its operation class, source category, normalized skill reference name
  when relevant, and whether it is an initial read, repeat, or truncation recovery. Include
  returned token counts if available. Exclude command bodies, arguments containing source or
  prompt text, tool output, user data, and transcript prose.
- For verification and repair, pseudonymous candidate/premise ids, dispatch/return events,
  before/after action and priority, ruling, and categorical remedy/anchor changes. Preserve
  dropped-candidate metadata only if it already exists. Absence is not evidence of no drops.

These joins would permit event-level accounting and measured dispatch waits. Mixed requests,
cached context carried into later requests, and missing events would still need an unknown
bucket. Token counts alone cannot prove a marginal saving or causal quality benefit; the
preregistered A-only experiment in #387, including gRPC and soba, remains necessary before
adopting a cut. No history-reconstruction run is authorized or needed for this audit.

## Validation

Disposable calculations reconciled all 21 attempts with the frozen prices, per-attempt charges,
the A ledger rows, the 20 cells including Astro's replacement, and the A results total. All
cache tiers are known. Every recorded elapsed interval is accounted for with the explicit
unknown phase attribution, envelope overlaps, boundary discrepancy, and retry wait above.
The candidate case and both gRPC cases were checked against their retained compositions.

The unchanged instruction-budget check is
`PYTHONDONTWRITEBYTECODE=1 python3 -B skills/review-code/scripts/test_instruction_budget.py`.
Its measured always-loaded set remains 29,444 bytes against 30,000; **delta is 0 bytes**.
No limit, script, score, mapping, or review instruction changes. Publication inspection covers
the entire diff for raw traces, request/actor identifiers, timestamps, prompt excerpts, command
bodies, and proprietary content. Missing phase boundaries and marginal-cost evidence are
reported limitations of the retained dataset, not omitted charges or a reason to rerun it.
