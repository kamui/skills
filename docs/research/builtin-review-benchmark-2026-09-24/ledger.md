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
(mirrors, caches, smoke checks) ran no model and is not charged. These rows are in the frozen run's
`charges.jsonl`, which `run_cell.py` counts against the cap.

## Setup (freeze, 2026-09-24, pre-dispatch probes)

Each probe ran one arm through `dispatch.sh` on the toy fixture, under the run's pinned `bin/`
(`claude` 2.1.282, `codex` 0.156.1; see the run's README), and was filed with `file_attempt.py`
against the pinned version as `bench/runs/2026-09-24-builtin-baseline/probes/att-00N`. Costs are
`file_attempt.py`'s metering at the `rates.json` entries of 2026-09-24. The Codex rollout's last
`rate_limits` event put the ChatGPT plan (`plan_type: prolite`) at **62% of its weekly window
used, resetting 2026-09-26T09:19:52Z**; that is the quota the grid starts from.

| # | Step | Session | Result | Billed / list ($) |
| --- | --- | --- | --- | --- |
| S22 | probe B: built-in, sonnet, `--effort high`, 22:22Z | `ad178ae0…` | claude-code 2.1.282; prompt `665e2e51…` as on 2.1.281; `git diff main...HEAD`; valid | 0.11 |
| S23 | probe C: built-in, opus, `--effort high`, 22:22Z | `f856e5de…` | claude-code 2.1.282; prompt `bf131e06…` as on 2.1.281; diffed `main...review-head`; findings as a fenced JSON array; valid | 0.10 |
| S24 | probe D: `codex review`, defaults, 22:22Z | `01a0d583…` | codex-cli 0.156.1; rubric `ec60e7f3…`; `git diff main...review-head`; valid | 0.13 list |

Frozen run charges before any cell: **$28.31** (`charges.jsonl`: the shakedown $1.69, the hunts
and adjudications $26.29, the probes $0.33). Room under the cap after the $25 reserve: $196.69.

## Attempts

Opened 2026-09-24 before the pre-dispatch probes (S22–S24) and before any scored cell, as README
§10 required. Every dispatch of the frozen run `bench/runs/2026-09-24-builtin-baseline` gets a row
here when it is filed: the attempt id, the cell, the dispatch instant, the disposition, the metered
cost (billed dollars for Claude, list-price equivalent for Codex), and for Codex the plan quota
as the rollout's last `rate_limits` event reports it. The pilot ((i) and (n) under B and D, one
replicate each) runs first; its valid rows count.

| Attempt | Cell | Dispatched | Disposition | Billed / list ($) | Quota after (D) | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| att-001 | (i) / B / 1 | 00:33:55Z | valid completed 00:34:32Z | 0.19 | — | pilot; one `git diff`, no test run; 7 items |
| att-002 | (i) / D / 1 | 00:34:29Z | valid completed 00:35:15Z (re-filed; first filed stopped: normalization exit 1) | 0.26 list | 62% | pilot; 3 findings, verdict `patch is incorrect`; stopped by the normalizer defect below, re-filed from its own output; the old audit also flagged three reads of its own dependency cache |
| att-003 | (n) / B / 1 | 00:34:45Z | valid completed 00:35:04Z | 0.08 | — | pilot; one `git diff`, no scratch zsh; 4 items |
| att-004 | (n) / D / 1 | 00:35:10Z | valid completed 00:35:52Z (re-filed; first filed stopped: normalization exit 1) | 0.20 list | 63% | pilot; no finding (verdict `patch is correct`) after offline zsh checks; stopped by the normalizer defect below, re-filed from its own output |

All times 2026-09-25. Pilot spend $0.72 (Claude $0.27 billed, Codex $0.46 list). Run spend after the
pilot, charges included: $29.04; room under the cap after the reserve: $195.96.

**Pilot finding: three harness defects on Codex output, fixed in `0200519`.** Both Codex reviews ran
to completion and exited 0, but `normalize_review.py` knew only the single-finding marker
`Review comment:`. With several findings Codex CLI 0.156.1 writes `Full review comments:`, and with
none it prints its summary alone; both came back `unresolved`, so `dispatch.sh` wrote a stop. The
read audit also took the slash after a glob (`python*/site-packages/...`) as an absolute path.
The toy fixture had exactly one finding per review, so none of these paths had run. Re-normalized
and re-audited with the fixed tools, att-002 parses to three items with no violation and att-004
to an empty review. The maintainer chose to re-file both from their own outputs with no
replacement, since the repair changed no reviewer input or execution condition; `6f61765` lets
`file_attempt.py --replay` supersede a normalization-only stop, and the manifest's second deviation
records the re-filing. `552a6f8` keeps a leading glob (`/*/x`) inside an absolute path, which the
glob fix had stopped flagging; the third deviation records it, and no filed attempt's audit
changes. `f1a4343` judges a dot-led glob that bash expands to `..` (`.*/.*/<path>`) as a climb,
which the glob fix had also stopped flagging; the fourth deviation records it, and no filed
attempt's audit changes. `a49dd79` does the same for a `~` path (`~/.*/.*/<path>`); the fifth
deviation records it, and no filed attempt's commands contain `~`. No charge: nothing was dispatched. Replacements used: 0 of 4.
