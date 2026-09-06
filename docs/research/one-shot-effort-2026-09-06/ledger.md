# Ticket ledger — issue #124 (one-shot effort experiment, 2026-09-06)

All times UTC. Spend is billed dollars at Sonnet 5 list ($2/$10 per M, cache write ×1.25 five-minute tier, ×2.0 one-hour tier, read ×0.1) from `transcript_usage.py` unless a row says otherwise. Session quota: the harness reports none; `unknown` unless a notice arrives.

## Caps (written before any chargeable work)

| Cap | Value | Basis |
| --- | --- | --- |
| Planned cells | 14 | ticket: 3 seeds × 2 arms on Hyper + 2 seeds × 2 arms × 2 fresh targets |
| Replacement cap | 2 (16 attempts) | method §1 |
| Pre-freeze allowance (setup, probes, target vetting, adjudication) | $15.00 | #96 pre-freeze allowance; recorded here before the first probe |
| Grading/closeout reserve | $5.00 | #96; blind adjudication of unexpected findings |
| Spend cap (ticket total) | provisional $90.00, finalized in README §Budget gate before dispatch | method §1: min(1.5 × projected, $150) |
| Concurrency | at most 2 cells in flight | method §3 |

## Setup and probe entries

| # | Time | Entry | Agents / transcripts | Spend |
| --- | --- | --- | --- | --- |
| S1 | 07:47:16 | In-session dispatch through `.claude/agents/v5b-primary-effort-medium.md` (written 07:46, after session start): `Agent type 'v5b-primary-effort-medium' not found`, twice; the runtime docs say a new `agents` directory is watched only after restart. Setup outcome, not evidence about effort. | none billed | $0.00 |
| S2 | 07:47:16 | In-session plain dispatch (`model: sonnet`, no definition): default effort observed `high` on 3/3 assistant lines, `claude-sonnet-5`. | `30e14d23…/subagents/agent-acd43aa861b85b810.jsonl` | $0.04 |
| S3 | 07:49:06–07:49:28 | Headless `claude -p --model sonnet --effort medium --agents <verifier definition>`; root `medium` 4/4 lines; child via `v5b-verifier-effort-high` `high` 3/3; plain child inherited `medium` 2/2. Adapter validated; inheritance hazard confirmed. | session `50663fac-9fe9-4f75-bacd-df423471d002` (+2 children) under `-private-tmp-effort124-probes` | $0.12 |
| S4 | 07:51:12–07:51:23 | Headless `--effort high` control shape: root `high` 3/3; child via definition `high` 2/2. | session `574f61a8-68fa-4c87-82b0-2ec0051e3c46` (+1 child) | $0.06 |
| S5 | 07:47–08:09 | Target vetting: two Sonnet helper agents (clean high-risk slot; buggy reasoning-heavy slot), in-session, network read-only. Clean slot: bbolt#1179 (too recent), jwt#456 (too mechanical), quic-go#5220 (backup), **etcd#18749 (chosen)**. Buggy slot: libuv#4400 (rejected: no confirmed defect of its own), **bytes#698 (chosen)**, requests#6667 (backup), pebble#5743, etcd#17563. Reports in `hunts/`. | in-session sub-agents `a3534a9ddbf24722a` ($3.16), `a96ff317a54441dad` ($2.28) | $5.44 |
| S6 | 08:00–08:12 | Provisioning (no model cost): staging clones of `tokio-rs/bytes` and `etcd-io/etcd`, truncated mirrors `g.git`/`h.git` with negative checks, offline cargo cache (59 MB, `cargo test --offline --test test_bytes` 84 passed in 2.5 s) and Go module/build caches (253 MB + 560 MB; `go test ./etcdserver/txn/...` 6–9 s, `-race` 8–13 s, `go vet` 2 s). Packets built, then **rebuilt with a merge-time cutoff** after the first build was found to carry post-merge comments (g: 3 conversation comments including the downstream breakage report; h: 2 conversation and 2 issue comments). Final packet SHA-256: g `a16ca69e…4392e`, h `3a797bb5…8b6a`. | — | $0.00 |
| S7 | 08:04–08:16 | Independent adjudicators (Sonnet, in-session): register for (g) (GT-g1 reproduced at the head with #728's test, passing at the merge-base) and (h) (clean; apply path traced to an unrecovered re-panic; goroutine leak reproduced only under a recovering harness). Sealed as `g-bytes-698/register.md` and `h-etcd-18749/register.md` with calibration addenda. | `a03daed41f0a6842d` ($0.51), `ade203887d5ed959a` ($0.95) | $1.46 (corrected 08:17 from a $2.19 figure written before the meter ran) |

| S8 | 09:12 | Setup failure, no root dispatched: the first `run_cell.sh g …` calls for att-07/att-08 died at clone preparation (`cannot force update the branch 'master' used by worktree`: the fresh mirrors' `HEAD` points at the base branch, Hyper's did not). Runner fixed to detach before moving the base branch; the two empty clones were removed and the same attempt IDs were dispatched at 09:12–09:13 — no reviewer root ran under the failed calls, so they are not attempts. | — | $0.00 |

Pre-freeze subtotal (S1–S7): **$7.12** of the $15 allowance. Stage-2 freeze commit: `edfb4b38aaa5fcd11497f5191b5ddb81b4fc8ae1` (2026-09-06T08:15:40Z).

## Attempt ledger

Dispatch records are written before each root dispatch (method §3). Stage-1 freeze commit: `30c2f2f9c0e098df77ac2324c589f7a64d83dada` (2026-09-06T07:55:02Z). Expected durations cite the holdout's Hyper `v5b` cells (root-to-completion unavailable there; primary assistant spans 26–52 min, median ~31 min) for `high`, and `no matched observation` on Hyper for `medium` (the holdout's medium cells on (b)/(c) spanned ~16 min).

| Attempt | Cell | Dispatch record | Session | Phase reached | Disposition | Replacement | Meter row |
| --- | --- | --- | --- | --- | --- | --- | --- |
| att-01 | (a) `high` r1 | 07:55:17Z (record written 07:55, freeze commit 07:55:02Z); attempt 1/16; $0.22 spent (probes) + vetting pending; quota `unknown`; expected ~31 min (26–52); in flight 0→1 | `ef808bef-5d11-4b8d-a67f-237f06217494` (+1 verifier `aec115b5b6c51557d`) | result | valid completed 08:29:05Z; sidecar complete (payload 1898 s, completion 2027 s); effort `high`×141 primary, `high`×42 verifier | first | 2 transcripts, $5.23 (harness self-report $5.256) |
| att-03 | (a) `medium` r2 | 08:29:30Z; attempt 3/16; $15.73 spent of $110 (setup $7.12 + cells $8.61); quota `unknown`; expected ~21 min (1 matched: 20.6); in flight 0→1 | `27fe9788-c0e3-41f4-97e5-33a6bb27f0dc` (+1 verifier `aa3107dab5db31dc4`) | result | valid completed 08:46:47Z; sidecar complete (payload 893 s, completion 1037 s); effort `medium`×105 primary, `high`×19 verifier | first | 2 transcripts, $2.86 (harness $2.863) |
| att-04 | (a) `high` r2 | 08:29:34Z; attempt 4/16; $15.73; quota `unknown`; expected ~34 min (1 matched: 33.8); in flight 1→2 | `867c8ab3-cab8-4145-95b9-1681074f97d4` (no child: **no verifier batch dispatched**) | result | valid completed 08:47:05Z; sidecar complete (payload 778 s, completion 1051 s); effort `high`×117 primary; completion under the skill's coverage rule judged at scoring | first | 1 transcript, $3.09 (harness $3.088) |
| att-05 | (a) `high` r3 | 08:47:33Z; attempt 5/16; $21.68 spent of $110 (setup $7.12 + cells $14.56); quota `unknown`; expected ~26 min (2 matched: 17.5, 33.8); in flight 0→1 | `deb0a66a-5704-4390-81e6-63726f010b53` (no child: **no verifier batch dispatched**) | result | valid completed 09:04:12Z; sidecar complete (payload 791 s, completion 1000 s); effort `high`×95 primary | first | 1 transcript, $2.72 (harness $2.720) |
| att-06 | (a) `medium` r3 | 08:47:37Z; attempt 6/16; $21.68; quota `unknown`; expected ~19 min (2 matched: 17.3, 20.6); in flight 1→2 | `7817f5bd-e6be-4d96-bcb9-e34c39e62008` (+1 verifier `ade0a6bb3fa325798`) | result | valid completed 09:11:38Z; sidecar complete (payload 1403 s, completion 1443 s); effort `medium`×94 primary, `high`×36 verifier | first | 2 transcripts, $3.73 (harness $3.733) |
| att-07 | (g) `high` r1 | 09:12:52Z (after S8); attempt 7/16; $28.13 spent of $110 (setup $7.12 + cells $21.01); quota `unknown`; expected `no matched observation` on (g) (Hyper `high` 16.7–33.8 min); in flight 0→1 | `8b096eb9-699b-4eca-b96a-49491c584173` (+1 verifier `aee44cfae02b8f6d5`) | result | valid completed 09:27:24Z; sidecar complete (payload 707 s, completion 872 s); effort `high`×84 primary, `high`×28 verifier | first | 2 transcripts, $2.29 (harness $2.318) |
| att-09 | (g) `medium` r2 | 09:28Z; attempt 9/16; $33.09 spent of $110 (setup $7.12 + cells $25.97); quota `unknown`; expected ~12 min (1 matched: 12.4); in flight 0→1 | see `g-medium-seed2-att-09-session.txt` | | | first | |
| att-10 | (g) `high` r2 | 09:28Z; attempt 10/16; $33.09; quota `unknown`; expected ~15 min (1 matched: 14.5); in flight 1→2 | see `g-high-seed2-att-10-session.txt` | | | first | |
| att-08 | (g) `medium` r1 | 09:13:13Z (after S8); attempt 8/16; $28.13; quota `unknown`; expected `no matched observation` on (g) (Hyper `medium` 17.3–24.0 min); in flight 1→2 | `8d2e0f62-97ca-4789-9a30-3917093548b6` (+1 verifier `a1f48bc56104cf70b`) | result | valid completed 09:25:38Z; sidecar complete (payload 689 s, completion 744 s); effort `medium`×115 primary, `high`×22 verifier | first | 2 transcripts, $2.67 (harness $2.671) |
| att-02 | (a) `medium` r1 | 07:55:18Z; attempt 2/16; $0.22 + vetting pending; quota `unknown`; expected `no matched observation` (~16 min by analogy); in flight 1→2 | `ff59299b-9185-43ba-94f6-5c1347da6a6d` (+1 verifier `abe188378d59cf75c`) | result | valid completed 08:15:53Z; sidecar complete (payload 1016 s, completion 1234 s); effort `medium`×105 primary, `high`×25 verifier | first | 2 transcripts, $3.38 (harness self-report $3.385) |
