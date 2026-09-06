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
| S5 | 07:47–… | Target vetting: two Sonnet helper agents (clean high-risk slot; buggy reasoning-heavy slot), in-session, network read-only. Metered at close. | in-session sub-agents `a3534a9ddbf24722a`, `a96ff317a54441dad` | pending |
