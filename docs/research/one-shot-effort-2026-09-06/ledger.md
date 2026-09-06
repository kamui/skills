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
| S7 | 08:04–08:16 | Independent adjudicators (Sonnet, in-session): register for (g) (GT-g1 reproduced at the head with #728's test, passing at the merge-base) and (h) (clean; apply path traced to an unrecovered re-panic; goroutine leak reproduced only under a recovering harness). Sealed as `g-bytes-698/register.md` and `h-etcd-18749/register.md` with calibration addenda. | `a03daed41f0a6842d` ($0.77), `ade203887d5ed959a` ($1.42) | $2.19 |

Pre-freeze subtotal (S1–S7): **$7.85** of the $15 allowance.

## Attempt ledger

Dispatch records are written before each root dispatch (method §3). Stage-1 freeze commit: `30c2f2f9c0e098df77ac2324c589f7a64d83dada` (2026-09-06T07:55:02Z). Expected durations cite the holdout's Hyper `v5b` cells (root-to-completion unavailable there; primary assistant spans 26–52 min, median ~31 min) for `high`, and `no matched observation` on Hyper for `medium` (the holdout's medium cells on (b)/(c) spanned ~16 min).

| Attempt | Cell | Dispatch record | Session | Phase reached | Disposition | Replacement | Meter row |
| --- | --- | --- | --- | --- | --- | --- | --- |
| att-01 | (a) `high` r1 | 07:55:17Z (record written 07:55, freeze commit 07:55:02Z); attempt 1/16; $0.22 spent (probes) + vetting pending; quota `unknown`; expected ~31 min (26–52); in flight 0→1 | see `a-high-seed1-att-01-session.txt` | | | first | |
| att-02 | (a) `medium` r1 | 07:55:18Z; attempt 2/16; $0.22 + vetting pending; quota `unknown`; expected `no matched observation` (~16 min by analogy); in flight 1→2 | see `a-medium-seed1-att-02-session.txt` | | | first | |
