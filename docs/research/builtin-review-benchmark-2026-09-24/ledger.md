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
| S9 | wrapper run C (opus, `high` argument only) | valid | claude-opus-5-5 | 0.10 | ran the `low` variant: the argument alone does not select it |
| S10 | wrapper run D (stdin prompt) | valid | gpt-6-astra | 0.10 | `overall_correctness` recovered from the rollout |
| S11 | wrapper run C2 (opus, `--effort high` + argument, base `main`) | valid | claude-opus-5-5 | 0.07 | `high effort → 8 inline angles → dedup (no verify)` variant |
| S12 | wrapper run B2 (sonnet, `--effort high` + argument, base `main`) | valid | claude-sonnet-5 | 0.04 | `3+5 angles × 6 candidates → 1-vote verify` variant |
| S13 | wrapper run A (pinned `skills/review-code` tree `6862d993`, fresh home, sonnet high) | valid | claude-sonnet-5 | 0.50 | one verifier; 17 requests; 89 s |

Running total of metered setup spend is kept in `comparison-data.md` once it exists; the rows
above sum to about `$1.04` billed plus `$0.56` Codex list-price.

## Attempts

None dispatched. The attempt table opens with the pilot (README §6).
