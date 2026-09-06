# Comparison data — one-shot effort experiment (issue #124)

Every attempt on every target, both arms, in the method's three cost views. Rows are added as cells
close out; nothing is deleted. Billed usage rows come from
`python3 docs/research/tools/transcript_usage.py <root.jsonl> <subagents/agent-*.jsonl> --prices 2,10 --report <run.md> --timing <timing.json>`.

## Comparison boundaries

**Comparable across arms and replicates on one target:** the packet (byte-identical, SHA-256 below),
the mirror and clone construction, the skill snapshot (tree `bea6be14…`), the model
(`claude-sonnet-5` on every line), the runtime shape (one headless `claude -p` session per cell,
the primary as its root, verifiers as its children through the `v5b-verifier-effort-high`
definition), the dispatch prompt (arm-blind), and the scoring register. Within a target, the two
arms' cells form matched pairs by replicate.

**Comparable across targets:** recall, false-finding, false-clean and completion counts only.
Billed cost is not; targets differ in diff size, repository size and language.

**Not directly comparable to the holdout grid.** Those cells ran as in-session sub-agents whose
cache writes were metered at the 5-minute tier; every headless session here wrote the 1-hour tier,
which `transcript_usage.py` prices at ×2.0 of the input rate (the `5m`/`1h` split is printed in each
row). Both arms pay it equally, so matched ratios are unaffected, but absolute dollars here are
higher than the holdout's for the same work. The holdout's Hyper `v5b` rows are historical
regression evidence, not controls.

| Target | Packet SHA-256 | Mirror refs | Register version |
| --- | --- | --- | --- |
| (a) `hyperium/hyper#3952` | `c94a8d3ed431594d9acd0803bac2558d9227aa58733404f1a5fd416a6e3bf1f2` | `master`=`f9f8f440…`, `review-head`=`f2aa734e…` | holdout README v1 (GT-a1) |

## Model and effort verification

One row per transcript, every assistant line scanned (`agent_effort.py`).

| Attempt | Cell | Agent | Definition | `message.model` | `effort` | Transcript |
| --- | --- | --- | --- | --- | --- | --- |
| att-01 | (a) `high` r1 | primary | `--effort high` | `claude-sonnet-5`×141 | `high`×141 | `ef808bef-5d11-4b8d-a67f-237f06217494.jsonl` |
| att-01 | (a) `high` r1 | verifier | `v5b-verifier-effort-high` | `claude-sonnet-5`×42 | `high`×42 | `agent-aec115b5b6c51557d.jsonl` |
| att-02 | (a) `medium` r1 | primary | `--effort medium` | `claude-sonnet-5`×105 | `medium`×105 | `ff59299b-9185-43ba-94f6-5c1347da6a6d.jsonl` |
| att-02 | (a) `medium` r1 | verifier | `v5b-verifier-effort-high` | `claude-sonnet-5`×25 | `high`×25 | `agent-abe188378d59cf75c.jsonl` |

## Billed usage per attempt

Header from `transcript_usage.py --header`; the last two columns are the report subtraction and
the production-shaped figure.

| Run | Model | Turns | Tool calls | Text-only | Input | Cache write | Cache read | Output | Thinking | Wall | Cost $ | Report est. tokens | Production-shaped $ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| (a) `high` r1 att-01 | claude-sonnet-5 | 88 | 101 | 2 | 176 | 338,323 (5m 79,525, 1h 258,798) | 11,337,925 | 173,160 | 114,714 | 0:45:07 | 5.23 | 15,660 | **5.08** |
| (a) `medium` r1 att-02 | claude-sonnet-5 | 59 | 77 | 2 | 118 | 250,536 (5m 49,176, 1h 201,360) | 6,644,248 | 112,540 | 50,346 | 0:24:26 | 3.38 | 13,690 | **3.25** |

## Timing per attempt

| Attempt | Cell | Mode | Root dispatched | Payload validated | Completed | Elapsed to payload (s) | Elapsed to completion (s) | Agent span sum (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| att-01 | (a) `high` r1 | render-only | 2026-09-06T07:55:17Z | 2026-09-06T08:26:55Z | 2026-09-06T08:29:05Z | 1898 | 2027 | 2707 |
| att-02 | (a) `medium` r1 | render-only | 2026-09-06T07:55:18Z | 2026-09-06T08:12:15Z | 2026-09-06T08:15:53Z | 1016 | 1234 | 1466 |

## Outcomes per attempt

| Attempt | Cell | Complete | Status | Findings (priority/action) | Questions | Observations | Verifier batches | Recovered defect IDs | Recall | False items (raw / unique) | False clean | Fix sufficiency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Matched cost pairs

All-attempt cell cost (every attempt mapped to the cell), candidate / control, matched by target and replicate.

| Target | Replicate | `high` cell $ (attempts) | `medium` cell $ (attempts) | Ratio |
| --- | --- | --- | --- | --- |

## Sandbox and hygiene disclosures

| Attempt | Disclosure |
| --- | --- |
