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
| att-03 | (a) `medium` r2 | primary | `--effort medium` | `claude-sonnet-5`×105 | `medium`×105 | `27fe9788-c0e3-41f4-97e5-33a6bb27f0dc.jsonl` |
| att-03 | (a) `medium` r2 | verifier | `v5b-verifier-effort-high` | `claude-sonnet-5`×19 | `high`×19 | `agent-aa3107dab5db31dc4.jsonl` |
| att-04 | (a) `high` r2 | primary | `--effort high` | `claude-sonnet-5`×117 | `high`×117 | `867c8ab3-cab8-4145-95b9-1681074f97d4.jsonl` |
| att-04 | (a) `high` r2 | verifier | — | no verifier batch dispatched | — | — |
| att-05 | (a) `high` r3 | primary | `--effort high` | `claude-sonnet-5`×95 | `high`×95 | `deb0a66a-5704-4390-81e6-63726f010b53.jsonl` |
| att-05 | (a) `high` r3 | verifier | — | no verifier batch dispatched | — | — |
| att-06 | (a) `medium` r3 | primary | `--effort medium` | `claude-sonnet-5`×94 | `medium`×94 | `7817f5bd-e6be-4d96-bcb9-e34c39e62008.jsonl` |
| att-06 | (a) `medium` r3 | verifier | `v5b-verifier-effort-high` | `claude-sonnet-5`×36 | `high`×36 | `agent-ade0a6bb3fa325798.jsonl` |

## Billed usage per attempt

Header from `transcript_usage.py --header`; the last two columns are the report subtraction and
the production-shaped figure.

| Run | Model | Turns | Tool calls | Text-only | Input | Cache write | Cache read | Output | Thinking | Wall | Cost $ | Report est. tokens | Production-shaped $ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| (a) `high` r1 att-01 | claude-sonnet-5 | 88 | 101 | 2 | 176 | 338,323 (5m 79,525, 1h 258,798) | 11,337,925 | 173,160 | 114,714 | 0:45:07 | 5.23 | 15,660 | **5.08** |
| (a) `medium` r1 att-02 | claude-sonnet-5 | 59 | 77 | 2 | 118 | 250,536 (5m 49,176, 1h 201,360) | 6,644,248 | 112,540 | 50,346 | 0:24:26 | 3.38 | 13,690 | **3.25** |
| (a) `medium` r2 att-03 | claude-sonnet-5 | 57 | 71 | 2 | 114 | 206,262 (5m 43,931, 1h 162,331) | 5,993,096 | 90,483 | 46,059 | 0:20:01 | 2.86 | 13,212 | **2.73** |
| (a) `high` r2 att-04 | claude-sonnet-5 | 60 | 67 | 1 | 120 | 181,724 (5m 0, 1h 181,724) | 7,486,990 | 86,299 | 55,695 | 0:17:27 | 3.09 | 9,636 | **2.99** |
| (a) `high` r3 att-05 | claude-sonnet-5 | 45 | 57 | 1 | 90 | 184,698 (5m 0, 1h 184,698) | 5,423,021 | 89,683 | 57,943 | 0:16:37 | 2.72 | 9,326 | **2.63** |
| (a) `medium` r3 att-06 | claude-sonnet-5 | 60 | 72 | 2 | 120 | 277,591 (5m 71,938, 1h 205,653) | 6,681,567 | 139,400 | 69,083 | 0:31:02 | 3.73 | 14,018 | **3.59** |

## Timing per attempt

| Attempt | Cell | Mode | Root dispatched | Payload validated | Completed | Elapsed to payload (s) | Elapsed to completion (s) | Agent span sum (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| att-01 | (a) `high` r1 | render-only | 2026-09-06T07:55:17Z | 2026-09-06T08:26:55Z | 2026-09-06T08:29:05Z | 1898 | 2027 | 2707 |
| att-02 | (a) `medium` r1 | render-only | 2026-09-06T07:55:18Z | 2026-09-06T08:12:15Z | 2026-09-06T08:15:53Z | 1016 | 1234 | 1466 |
| att-03 | (a) `medium` r2 | render-only | 2026-09-06T08:29:30Z | 2026-09-06T08:44:23Z | 2026-09-06T08:46:47Z | 893 | 1037 | 1201 |
| att-04 | (a) `high` r2 | render-only | 2026-09-06T08:29:34Z | 2026-09-06T08:42:32Z | 2026-09-06T08:47:05Z | 778 | 1051 | 1047 |
| att-05 | (a) `high` r3 | render-only | 2026-09-06T08:47:32Z | 2026-09-06T09:00:43Z | 2026-09-06T09:04:12Z | 791 | 1000 | 997 |
| att-06 | (a) `medium` r3 | render-only | 2026-09-06T08:47:35Z | 2026-09-06T09:10:58Z | 2026-09-06T09:11:38Z | 1403 | 1443 | 1862 |

## Outcomes per attempt

| Attempt | Cell | Complete | Status | Findings (priority/action) | Questions | Observations | Verifier batches | Recovered defect IDs | Recall | False items (raw / unique) | False clean | Fix sufficiency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Matched cost pairs

All-attempt cell cost (every attempt mapped to the cell), candidate / control, matched by target and replicate.

| Target | Replicate | `high` cell $ (attempts) | `medium` cell $ (attempts) | Ratio |
| --- | --- | --- | --- | --- |
| (a) | 1 | 5.23 (att-01) | 3.38 (att-02) | 0.65 |
| (a) | 2 | 3.09 (att-04) | 2.86 (att-03) | 0.93 |
| (a) | 3 | 2.72 (att-05) | 3.73 (att-06) | 1.37 |

## Sandbox and hygiene disclosures

| Attempt | Disclosure |
| --- | --- |
