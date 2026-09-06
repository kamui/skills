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
| (g) `tokio-rs/bytes#698` | `a16ca69e7238cb189bca9fff0edca89688b1ccbd377fb8ace545b7412fa4392e` | `master`=`ce09d7d3…`, `review-head`=`7052d245…` | `g-bytes-698/register.md` v1 (GT-g1) |
| (h) `etcd-io/etcd#18749` | `3a797bb5dd9ada3a30c7e7b17961cbf61a2c74982dbd98655afe83b6cbec8b6a` | `main`=`bb381d47…`, `review-head`=`8a0fd66d…` | `h-etcd-18749/register.md` v1 (clean) |

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
| att-07 | (g) `high` r1 | primary | `--effort high` | `claude-sonnet-5`×84 | `high`×84 | `8b096eb9-699b-4eca-b96a-49491c584173.jsonl` |
| att-07 | (g) `high` r1 | verifier | `v5b-verifier-effort-high` | `claude-sonnet-5`×28 | `high`×28 | `agent-aee44cfae02b8f6d5.jsonl` |
| att-08 | (g) `medium` r1 | primary | `--effort medium` | `claude-sonnet-5`×115 | `medium`×115 | `8d2e0f62-97ca-4789-9a30-3917093548b6.jsonl` |
| att-08 | (g) `medium` r1 | verifier | `v5b-verifier-effort-high` | `claude-sonnet-5`×22 | `high`×22 | `agent-a1f48bc56104cf70b.jsonl` |
| att-09 | (g) `medium` r2 | primary | `--effort medium` | `claude-sonnet-5`×121 | `medium`×121 | `f72e6fb8-4333-460f-b30e-6c41f50d5e99.jsonl` |
| att-09 | (g) `medium` r2 | verifier | `v5b-verifier-effort-high` | `claude-sonnet-5`×32 | `high`×32 | `agent-ab58befac7acc04e7.jsonl` |
| att-10 | (g) `high` r2 | primary | `--effort high` | `claude-sonnet-5`×95 | `high`×95 | `3ed14c7c-2689-4e00-9409-2d3f68cf340d.jsonl` |
| att-10 | (g) `high` r2 | verifier | `v5b-verifier-effort-high` | `claude-sonnet-5`×16 | `high`×16 | `agent-a9df430c26b2c7d15.jsonl` |
| att-11 | (h) `high` r1 | primary | `--effort high` | `claude-sonnet-5`×126 | `high`×126 | `6c855ad3-cbe1-4b8b-a1a6-70a9adbc3d49.jsonl` |
| att-11 | (h) `high` r1 | verifier | `v5b-verifier-effort-high` | `claude-sonnet-5`×34 | `high`×34 | `agent-a297b8681a64e5ab6.jsonl` |
| att-12 | (h) `medium` r1 | primary | `--effort medium` | `claude-sonnet-5`×106 | `medium`×106 | `bacf51e0-3caa-4daf-8959-646c3f011709.jsonl` |
| att-12 | (h) `medium` r1 | verifier | `v5b-verifier-effort-high` | `claude-sonnet-5`×45 | `high`×45 | `agent-a07ca0bcd290ecbcb.jsonl` |

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
| (g) `high` r1 att-07 | claude-sonnet-5 | 52 | 63 | 2 | 104 | 175,593 (5m 25,921, 1h 149,672) | 4,326,171 | 75,928 | 37,219 | 0:16:16 | 2.29 | 14,068 | **2.15** |
| (g) `medium` r1 att-08 | claude-sonnet-5 | 68 | 80 | 2 | 136 | 182,828 (5m 37,437, 1h 145,391) | 6,624,649 | 66,630 | 25,368 | 0:14:41 | 2.67 | 11,348 | **2.55** |
| (g) `medium` r2 att-09 | claude-sonnet-5 | 79 | 85 | 2 | 158 | 206,730 (5m 48,654, 1h 158,076) | 7,197,303 | 71,972 | 27,983 | 0:18:01 | 2.91 | 12,706 | **2.79** |
| (g) `high` r2 att-10 | claude-sonnet-5 | 52 | 63 | 2 | 104 | 153,242 (5m 16,703, 1h 136,539) | 4,409,509 | 68,268 | 31,411 | 0:14:46 | 2.15 | 11,212 | **2.04** |
| (h) `high` r1 att-11 | claude-sonnet-5 | 75 | 95 | 2 | 150 | 234,918 (5m 67,578, 1h 167,340) | 7,485,493 | 82,575 | 36,305 | 0:20:37 | 3.16 | 13,883 | **3.02** |
| (h) `medium` r1 att-12 | claude-sonnet-5 | 69 | 91 | 2 | 138 | 227,999 (5m 46,120, 1h 181,879) | 6,310,878 | 87,703 | 36,382 | 0:20:42 | 2.98 | 12,501 | **2.86** |

## Timing per attempt

| Attempt | Cell | Mode | Root dispatched | Payload validated | Completed | Elapsed to payload (s) | Elapsed to completion (s) | Agent span sum (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| att-01 | (a) `high` r1 | render-only | 2026-09-06T07:55:17Z | 2026-09-06T08:26:55Z | 2026-09-06T08:29:05Z | 1898 | 2027 | 2707 |
| att-02 | (a) `medium` r1 | render-only | 2026-09-06T07:55:18Z | 2026-09-06T08:12:15Z | 2026-09-06T08:15:53Z | 1016 | 1234 | 1466 |
| att-03 | (a) `medium` r2 | render-only | 2026-09-06T08:29:30Z | 2026-09-06T08:44:23Z | 2026-09-06T08:46:47Z | 893 | 1037 | 1201 |
| att-04 | (a) `high` r2 | render-only | 2026-09-06T08:29:34Z | 2026-09-06T08:42:32Z | 2026-09-06T08:47:05Z | 778 | 1051 | 1047 |
| att-05 | (a) `high` r3 | render-only | 2026-09-06T08:47:32Z | 2026-09-06T09:00:43Z | 2026-09-06T09:04:12Z | 791 | 1000 | 997 |
| att-06 | (a) `medium` r3 | render-only | 2026-09-06T08:47:35Z | 2026-09-06T09:10:58Z | 2026-09-06T09:11:38Z | 1403 | 1443 | 1862 |
| att-07 | (g) `high` r1 | render-only | 2026-09-06T09:12:52Z | 2026-09-06T09:24:39Z | 2026-09-06T09:27:24Z | 707 | 872 | 976 |
| att-08 | (g) `medium` r1 | render-only | 2026-09-06T09:13:13Z | 2026-09-06T09:24:42Z | 2026-09-06T09:25:38Z | 689 | 744 | 881 |
| att-09 | (g) `medium` r2 | render-only | 2026-09-06T09:27:45Z | 2026-09-06T09:41:32Z | 2026-09-06T09:42:50Z | 827 | 905 | 1081 |
| att-10 | (g) `high` r2 | render-only | 2026-09-06T09:28:07Z | 2026-09-06T09:40:37Z | 2026-09-06T09:41:11Z | 751 | 784 | 886 |
| att-11 | (h) `high` r1 | render-only | 2026-09-06T09:43:11Z | 2026-09-06T09:57:19Z | 2026-09-06T10:00:04Z | 849 | 1013 | 1237 |
| att-12 | (h) `medium` r1 | render-only | 2026-09-06T09:43:32Z | 2026-09-06T09:59:39Z | 2026-09-06T10:00:19Z | 967 | 1007 | 1242 |

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
| (g) | 1 | 2.29 (att-07) | 2.67 (att-08) | 1.17 |
| (g) | 2 | 2.15 (att-10) | 2.91 (att-09) | 1.35 |
| (h) | 1 | 3.16 (att-11) | 2.98 (att-12) | 0.94 |

## Sandbox and hygiene disclosures

| Attempt | Disclosure |
| --- | --- |
