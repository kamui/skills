# Ledger — built-in reviewer benchmark

Every chargeable step, in order. Prices: Sonnet 5 `$2/$10`; Opus 5.5 `$4/$20`; GPT-6 Astra `$10/$50`
list-price equivalent (the Codex account is a ChatGPT plan, `plan_type: prolite`; the plan's quota
is the real constraint and is recorded per D dispatch once the grid starts). Cap: **$250**
experiment total, closeout reserve `$25` (README §6). Nothing below is a scored cell.

## Setup (Phase 0 shakedown, 2026-09-24, toy repository)

| # | Step | Valid | Model | Billed / list ($) | Notes |
| --- | --- | --- | --- | --- | --- |
| S1 | claude `/code-review` under the normal home | invalid | claude-sonnet-5 | 0.09 | user skill shadowed the built-in |
| S2 | claude built-in, `--safe-mode`, sonnet, `high` argument + `--effort high` | valid | claude-sonnet-5 | 0.04 | `high` variant, JSON block |
| S3 | codex review under the normal home | invalid | gpt-6-astra | 0.20 | read the maintainer's `review-code` skill |
| S4 | codex review, clean home under `/tmp`, `--base` | valid | gpt-6-astra | 0.11 | no prompt possible with `--base` |
| S5 | claude built-in, fresh home, no `--model`, no effort | valid | claude-opus-5-5 | 0.10 | `low` variant, ReportFindings |
| S6 | codex review, clean home outside `/tmp`, stdin prompt, `workspace-write` | valid | gpt-6-astra | 0.15 | rubric present, range honoured |
| S7 | codex reviewer of the draft plan (`gpt-6-astra`, reasoning high, read-only) | n/a | gpt-6-astra | not metered (normal home; review, not a probe) | `review-1.md` |
| S8 | wrapper run B (sonnet, `high` argument only) | valid | claude-sonnet-5 | 0.10 | `high` variant; diffed `main...HEAD` |
| S9 | wrapper run C (opus, `high` argument only) | harness-invalid (att-002) | claude-opus-5-5 | 0.10 | ran the `low` variant: the argument alone does not select it |
| S10 | wrapper run D (stdin prompt) | harness-invalid (att-003) | gpt-6-astra | 0.10 | `overall_correctness` recovered from the rollout; `find ..` read the other attempts' clones |
| S11 | wrapper run C2 (opus, `--effort high` + argument, base `main`) | valid | claude-opus-5-5 | 0.07 | `high effort → 8 inline angles → dedup (no verify)` variant |
| S12 | wrapper run B2 (sonnet, `--effort high` + argument, base `main`) | valid | claude-sonnet-5 | 0.04 | `3+5 angles × 6 candidates → 1-vote verify` variant |
| S13 | wrapper run A (pinned `skills/review-code` tree `6862d993`, fresh home, sonnet high) | valid | claude-sonnet-5 | 0.50 | one verifier; 17 requests; 89 s |

The rows above sum to about `$1.04` billed plus `$0.56` Codex list-price. S8–S13 are filed as the
suite run `bench/runs/2026-09-24-toy` (attempts att-001 to att-006), metered again from their
transcripts at the `bench/rates.json` entries; there S11 prices at `$0.059`, because the recorded
Opus 5.5 cache-read rate is `$0.20` per million tokens where this row used a one-tenth ratio. A
seventh fixture attempt (att-007, `$0.09` list) re-ran D after the wrapper's timing fix.

## Setup (step 6, 2026-09-24, fresh targets (o)–(r))

Each row is one headless Claude Code 2.1.281 session, `claude -p --model claude-opus-5-5 --effort high`,
single-threaded (`--disallowedTools Agent`), under the maintainer's normal home with network and
`gh`, working in a scratch directory under `~/.t3/bench-cache/sealed/`. Opus 5.5 at `high`, not
Sonnet 5 as in #137, because the maintainer asked for Opus 5.5 high on every helper. Every
assistant line of every transcript is `claude-opus-5-5` at `high`, no session started a sub-agent,
and each row is metered from its transcript by `transcript_usage.py` at the `rates.json` Opus 5.5
entry ($4/$20, cache reads $0.20), which agrees with the harness's own figure to the cent except
S18 ($1.87 self-reported). Hunts ran from `prompts/hunt-template.md` filled per slot from
`prompts/hunt-slots.json`, adjudications from `prompts/adjudicator-template.md`; the prompt column
is the SHA-256 prefix of the rendered prompt. Reports and rulings are sealed in [`sealed/`](sealed/README.md).

| # | Step | Session | Prompt | Result | Billed ($) |
| --- | --- | --- | --- | --- | --- |
| S14 | hunt (o), started 18:40Z, 71 min | `6e27aa37…` | `3fed7989fa8d` | a candidate from the fallback window only; no qualifying merge on or after 2026-07-01 among 31 examined | 6.94 |
| S15 | hunt (p), 18:40Z, 18 min | `172d5c7e…` | `e4c1c2eeecb5` | a primary and an alternate from the preferred window, 14 examined | 5.16 |
| S16 | hunt (q), 18:40Z, 20 min | `f6154857…` | `ec698fc725d1` | a primary and an alternate from the preferred window, 4 examined | 3.98 |
| S17 | hunt (r), 18:40Z, 17 min | `f4e7a986…` | `93294af51db6` | a primary and an alternate from the preferred window, 5 examined | 3.60 |
| S18 | adjudication (r), 18:58Z | `3b77fba3…` | `799e1e87e1bb` | the slot's expected status confirmed; register sealed | 1.86 |
| S19 | adjudication (p), 18:59Z | `84a9076b…` | `34c2a9f4a9d7` | the slot's expected status confirmed; register sealed | 1.26 |
| S20 | adjudication (q), 19:01Z | `3f2ae047…` | `1b7c0d52cf5a` | the slot's expected status confirmed; register sealed | 2.07 |
| S21 | adjudication (o), 19:51Z | `0413d38b…` | `a2f5bddbe60a` | the slot's expected status confirmed; register sealed | 1.42 |

Step 6 setup so far: **$26.29**, all Opus 5.5 at API list price. Provisioning the four targets
(mirrors, caches, smoke checks) ran no model and is not charged. These rows become the first lines
of the frozen run's `charges.jsonl`, which `run_cell.py` counts against the cap.

## Attempts

None dispatched. The attempt table opens with the pilot (README §6).
