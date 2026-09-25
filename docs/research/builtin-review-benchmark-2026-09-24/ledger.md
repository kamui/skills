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

### Replicate 1 (2026-09-25)

The sealed order's remaining 36 replicate-1 cells ran from 05:02Z to 05:40Z, two in flight, each
claimed with the Codex quota the newest rollout reported. Notes count the normalized items and the
audited commands; the dispositions are the filed ones after the re-audits the manifest's seventh to
eleventh deviations record.

| Attempt | Cell | Dispatched | Disposition | Billed / list ($) | Quota after (D) | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| att-005 | (q) / A / 1 | 05:02:17Z | valid completed 05:04:09Z | 0.74 | — | 2 items; 13 commands; re-audited to valid (seventh deviation): first filed harness-invalid on false network flags (`.go` file names, the allowed offline `go test`) |
| att-006 | (q) / B / 1 | 05:02:22Z | harness-invalid 05:02:43Z | 0.20 | — | 3 items; 2 commands; 1 subagent; harness-invalid: wrote and read `/tmp/pr.diff`, outside the roots; replaced by att-007 |
| att-007 | (q) / B / 1 | 05:08:02Z | valid completed 05:08:24Z | 0.20 | — | 2 items; 3 commands; 1 subagent; replacement 1 of 4, for att-006 |
| att-008 | (q) / C / 1 | 05:08:29Z | valid completed 05:09:32Z | 0.36 | — | 9 items; 6 commands; 1 subagent |
| att-009 | (q) / D / 1 | 05:08:34Z | valid completed 05:08:58Z | 0.27 list | 63% | empty review; 3 commands; 1 subagent |
| att-010 | (p) / B / 1 | 05:09:07Z | valid completed 05:09:38Z | 0.13 | — | 3 items; 4 commands; 1 subagent |
| att-011 | (p) / C / 1 | 05:09:42Z | valid completed 05:11:10Z | 0.40 | — | 10 items; 5 commands; 1 subagent; re-audited, unchanged (eighth deviation) |
| att-012 | (p) / D / 1 | 05:09:49Z | valid completed 05:10:21Z | 0.23 list | 63% | 1 item; 4 commands; 1 subagent; re-audited to valid (eighth deviation): first filed harness-invalid on `http://localhost/` read as a path |
| att-013 | (p) / A / 1 | 05:11:55Z | valid completed 05:14:14Z | 0.86 | — | 1 item; 19 commands; 1 subagent; re-audited to valid (ninth deviation): first filed harness-invalid on absent paths from scratch code (`'/a'`, a sed pattern) |
| att-014 | (r) / C / 1 | 05:12:07Z | valid completed 05:14:14Z | 0.54 | — | 10 items; 12 commands; 1 subagent; re-audited to valid (ninth deviation): first filed harness-invalid on absent paths from JSX and imports (`</Form>`, `/react`) |
| att-015 | (r) / D / 1 | 05:16:48Z | valid completed 05:17:25Z | 0.41 list | 63% | 1 item; 4 commands; 1 subagent |
| att-016 | (r) / A / 1 | 05:16:53Z | valid completed 05:19:03Z | 0.77 | — | 2 items; 16 commands |
| att-017 | (r) / B / 1 | 05:17:40Z | valid completed 05:18:08Z | 0.15 | — | 4 items; 4 commands; 1 subagent |
| att-018 | (i) / A / 1 | 05:18:09Z | valid completed 05:21:53Z | 1.03 | — | 2 items; 20 commands; 1 subagent; re-audited to valid (tenth deviation): first filed harness-invalid on the provisioned venv interpreter's symlink |
| att-019 | (i) / C / 1 | 05:19:04Z | valid completed 05:20:45Z | 0.45 | — | 10 items; 7 commands; 1 subagent |
| att-020 | (l) / A / 1 | 05:20:47Z | valid completed 05:23:42Z | 0.91 | — | 3 items; 23 commands; 1 subagent |
| att-021 | (l) / B / 1 | 05:24:25Z | valid completed 05:24:55Z | 0.15 | — | 5 items; 3 commands; 1 subagent |
| att-022 | (l) / C / 1 | 05:24:30Z | valid completed 05:25:26Z | 0.25 | — | 8 items; 3 commands; 1 subagent |
| att-023 | (l) / D / 1 | 05:24:57Z | valid completed 05:25:23Z | 0.22 list | 63% | 1 item; 3 commands; 1 subagent |
| att-024 | (k) / B / 1 | 05:25:32Z | valid completed 05:25:49Z | 0.09 | — | 3 items; 3 commands; 1 subagent |
| att-025 | (k) / C / 1 | 05:25:35Z | valid completed 05:26:26Z | 0.23 | — | 7 items; 3 commands; 1 subagent |
| att-026 | (k) / D / 1 | 05:25:58Z | valid completed 05:26:23Z | 0.20 list | 63% | 1 item; 3 commands; 1 subagent |
| att-027 | (k) / A / 1 | 05:26:31Z | valid completed 05:27:37Z | 0.45 | — | 1 item; 11 commands |
| att-028 | (n) / C / 1 | 05:26:27Z | valid completed 05:27:29Z | 0.22 | — | 8 items; 3 commands; 1 subagent |
| att-029 | (n) / A / 1 | 05:27:30Z | valid completed 05:29:02Z | 0.45 | — | 2 items; 9 commands |
| att-030 | (o) / D / 1 | 05:27:58Z | valid completed 05:28:53Z | 0.37 list | 63% | 1 item; 6 commands; 1 subagent |
| att-031 | (o) / A / 1 | 05:29:14Z | valid completed 05:31:54Z | 0.80 | — | 2 items; 14 commands; 1 subagent; re-audited to valid (eleventh deviation): first filed harness-invalid on `cd ../../..` resolved from the clone, not its recorded cwd |
| att-032 | (o) / B / 1 | 05:29:22Z | valid completed 05:29:46Z | 0.09 | — | 4 items; 3 commands; 1 subagent |
| att-033 | (o) / C / 1 | 05:30:07Z | valid completed 05:31:17Z | 0.30 | — | 10 items; 8 commands; 1 subagent |
| att-034 | (m) / A / 1 | 05:31:20Z | valid completed 05:34:18Z | 0.97 | — | 1 item; 20 commands; 1 subagent |
| att-035 | (m) / B / 1 | 05:35:04Z | valid completed 05:35:34Z | 0.17 | — | 1 item; 1 commands; 1 subagent |
| att-036 | (m) / C / 1 | 05:35:09Z | valid completed 05:36:09Z | 0.29 | — | 8 items; 2 commands; 1 subagent |
| att-037 | (m) / D / 1 | 05:35:37Z | valid completed 05:35:57Z | 0.25 list | 63% | empty review; 3 commands; 1 subagent |
| att-038 | (j) / B / 1 | 05:36:22Z | valid completed 05:37:02Z | 0.13 | — | 3 items; 3 commands; 1 subagent |
| att-039 | (j) / C / 1 | 05:36:35Z | valid completed 05:38:55Z | 0.55 | — | 9 items; 7 commands; 1 subagent |
| att-040 | (j) / D / 1 | 05:37:28Z | valid completed 05:38:10Z | 0.43 list | 63% | 1 item; 4 commands; 1 subagent |
| att-041 | (j) / A / 1 | 05:38:37Z | valid completed 05:40:35Z | 0.58 | — | 3 items; 12 commands |

All times 2026-09-25. Replicate-1 spend after the pilot: $14.83 (A $7.56, B $1.30, C $3.58, D $2.38
list), 37 attempts for 36 cells. Run spend, charges included: $43.86; room under the cap after the
reserve: $181.14. Replacements used: 1 of 4. The Codex plan stayed at 63% of its weekly window.

**Replicate-1 finding: the read audit misread legitimate reviewer work five ways, fixed in
`33b0c25`, `f563ef2`, `eb8cad3`, `2da77b4` and `fd5d2e9`.** The pilot's targets never ran a Go
command, a URL, TypeScript scratch code, a provisioned venv or a `cd` that carried across Claude
Bash calls, and each first appearance filed an attempt harness-invalid: a `.go` file name read as
the `go` tool and the allowed offline `go test` as a network command (att-005); `http://localhost/`
read as a path (att-012); route strings, JSX closing tags and import specifiers read as absolute
paths (att-013, att-014); the venv interpreter's provisioned symlink followed out of the roots
(att-018); and a `cd ../../..` resolved from the clone rather than the directory the transcript
records (att-031). Each fix has a test, each re-audit ran over every filed attempt, and each of the
six affected attempts was re-filed with `file_attempt.py --replay` with no replacement. One
violation was real: att-006 wrote the diff to `/tmp/pr.diff` although the policy sends scratch
files to the work directory and its `TMPDIR` was there, and it was replaced by att-007.

### Replicate 2 (2026-09-25)

The replicate-2 blocks ran in the sealed target order from 05:41Z to 06:20Z, two in flight. Before
each block's first cell the operator's gate (the run README's stopping rule) compared `room_usd`
with the block's $15.50 bound; it never bound, and the room never fell below $164.21.

| Attempt | Cell | Dispatched | Disposition | Billed / list ($) | Quota after (D) | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| att-042 | (q) / B / 2 | 05:41:57Z | harness-invalid 05:42:19Z | 0.17 | — | 3 items; 2 commands; 1 subagent; harness-invalid: wrote and read `/tmp/pr_diff.txt`, outside the roots; replaced by att-044 |
| att-043 | (q) / C / 2 | 05:42:02Z | valid completed 05:43:16Z | 0.35 | — | 10 items; 7 commands; 1 subagent |
| att-044 | (q) / B / 2 | 05:43:40Z | valid completed 05:44:01Z | 0.13 | — | 3 items; 2 commands; 1 subagent; replacement 2 of 4, for att-042 |
| att-045 | (q) / D / 2 | 05:44:09Z | valid completed 05:44:28Z | 0.28 list | 63% | empty review; 3 commands; 1 subagent |
| att-046 | (q) / A / 2 | 05:44:14Z | valid completed 05:45:41Z | 0.60 | — | 1 item; 9 commands |
| att-047 | (p) / C / 2 | 05:44:37Z | valid completed 05:46:04Z | 0.35 | — | 7 items; 4 commands; 1 subagent |
| att-048 | (p) / D / 2 | 05:45:51Z | valid completed 05:46:22Z | 0.22 list | 63% | 1 item; 3 commands; 1 subagent |
| att-049 | (p) / A / 2 | 05:46:13Z | valid completed 05:48:39Z | 0.87 | — | 1 item; 20 commands; 1 subagent |
| att-050 | (p) / B / 2 | 05:46:31Z | valid completed 05:47:01Z | 0.14 | — | 4 items; 4 commands; 1 subagent |
| att-051 | (r) / D / 2 | 05:47:15Z | valid completed 05:47:59Z | 0.51 list | 64% | 1 item; 5 commands; 1 subagent |
| att-052 | (r) / A / 2 | 05:48:13Z | valid completed 05:50:24Z | 0.67 | — | 2 items; 19 commands |
| att-053 | (r) / B / 2 | 05:48:53Z | valid completed 05:49:24Z | 0.12 | — | 5 items; 3 commands; 1 subagent |
| att-054 | (r) / C / 2 | 05:49:37Z | valid completed 05:52:12Z | 0.68 | — | 6 items; 16 commands; 1 subagent |
| att-055 | (i) / A / 2 | 05:50:25Z | valid completed 05:55:22Z | 1.33 | — | 3 items; 27 commands; 1 subagent |
| att-056 | (i) / B / 2 | 05:52:13Z | valid completed 05:52:55Z | 0.14 | — | 6 items; 2 commands; 1 subagent |
| att-057 | (i) / C / 2 | 05:52:56Z | valid completed 05:54:49Z | 0.47 | — | 9 items; 6 commands; 1 subagent |
| att-058 | (i) / D / 2 | 05:54:51Z | valid completed 05:55:40Z | 0.32 list | 64% | 3 items; 4 commands; 1 subagent |
| att-059 | (l) / B / 2 | 05:55:24Z | valid completed 05:55:52Z | 0.13 | — | 5 items; 2 commands; 1 subagent; re-audited to valid (twelfth deviation): first filed harness-invalid on a fallback `|| cd /tmp` that never ran |
| att-060 | (l) / C / 2 | 05:55:42Z | valid completed 05:56:38Z | 0.26 | — | 6 items; 5 commands; 1 subagent |
| att-061 | (l) / D / 2 | 05:58:34Z | valid completed 05:59:05Z | 0.22 list | 64% | 1 item; 3 commands; 1 subagent |
| att-062 | (l) / A / 2 | 05:58:39Z | valid completed 06:00:55Z | 0.68 | — | 2 items; 17 commands; 1 subagent |
| att-063 | (k) / C / 2 | 05:59:13Z | valid completed 06:00:00Z | 0.20 | — | 9 items; 2 commands; 1 subagent |
| att-064 | (k) / D / 2 | 06:00:07Z | valid completed 06:00:31Z | 0.20 list | 64% | 1 item; 3 commands; 1 subagent |
| att-065 | (k) / A / 2 | 06:00:39Z | valid completed 06:02:39Z | 0.69 | — | 2 items; 16 commands |
| att-066 | (k) / B / 2 | 06:01:02Z | valid completed 06:01:21Z | 0.15 | — | 2 items; 3 commands; 1 subagent |
| att-067 | (n) / D / 2 | 06:01:22Z | valid completed 06:01:47Z | 0.30 list | 64% | empty review; 4 commands; 1 subagent |
| att-068 | (n) / A / 2 | 06:01:48Z | valid completed 06:02:59Z | 0.39 | — | 2 items; 10 commands |
| att-069 | (n) / B / 2 | 06:02:40Z | valid completed 06:02:58Z | 0.08 | — | 4 items; 1 commands; 1 subagent |
| att-070 | (n) / C / 2 | 06:02:59Z | valid completed 06:04:35Z | 0.34 | — | 7 items; 9 commands; 1 subagent |
| att-071 | (o) / A / 2 | 06:03:19Z | harness-invalid 06:05:57Z | 0.90 | — | 1 item; 19 commands; 1 subagent; harness-invalid: stored its scratch path in `/tmp/pd071` and read it back; replaced by att-074 |
| att-072 | (o) / B / 2 | 06:04:54Z | valid completed 06:05:18Z | 0.10 | — | 5 items; 2 commands; 1 subagent |
| att-073 | (o) / C / 2 | 06:05:38Z | valid completed 06:07:01Z | 0.34 | — | 9 items; 9 commands; 1 subagent |
| att-074 | (o) / A / 2 | 06:07:38Z | valid completed 06:10:11Z | 0.84 | — | 2 items; 20 commands; 1 subagent; replacement 3 of 4, for att-071 |
| att-075 | (o) / D / 2 | 06:10:38Z | valid completed 06:11:34Z | 0.51 list | 64% | 1 item; 6 commands; 1 subagent |
| att-076 | (m) / B / 2 | 06:10:26Z | valid completed 06:10:49Z | 0.16 | — | 2 items; 1 commands; 1 subagent |
| att-077 | (m) / C / 2 | 06:10:53Z | valid completed 06:12:34Z | 0.38 | — | 6 items; 2 commands; 1 subagent |
| att-078 | (m) / D / 2 | 06:11:38Z | valid completed 06:12:02Z | 0.25 list | 64% | empty review; 3 commands; 1 subagent |
| att-079 | (m) / A / 2 | 06:12:05Z | valid completed 06:15:05Z | 1.00 | — | 1 item; 25 commands; 1 subagent; re-audited to valid (thirteenth deviation): first filed harness-invalid on `|go ...` inside a quoted rg pattern |
| att-080 | (j) / C / 2 | 06:13:01Z | valid completed 06:15:28Z | 0.57 | — | 9 items; 11 commands; 1 subagent |
| att-081 | (j) / D / 2 | 06:17:54Z | valid completed 06:18:40Z | 0.26 list | 64% | empty review; 4 commands; 1 subagent |
| att-082 | (j) / A / 2 | 06:17:59Z | valid completed 06:19:19Z | 0.46 | — | empty review; 8 commands |
| att-083 | (j) / B / 2 | 06:19:09Z | valid completed 06:19:53Z | 0.16 | — | 3 items; 4 commands; 1 subagent |

All times 2026-09-25. Replicate-2 spend: $16.93 (A $8.43, B $1.47, C $3.94, D $3.09 list), 42
attempts for 40 cells. Grid spend, pilot included: $32.48 for 83 attempts. Run spend, charges
included: $60.79; room under the cap after the reserve: $164.21. Replacements used: 3 of 4. The
Codex plan ended at 64% of its weekly window, resetting 2026-09-26T09:19:52Z.

**Replicate-2 finding.** Two more audit misreadings, fixed in `216e507` (a fallback `|| cd /tmp`
that never ran counted as a read) and `645607e` (a `|` inside a quoted `rg` pattern read as a pipe
into `go`), re-filed att-059 and att-079 with no replacement. Two real violations were replaced:
att-042 wrote the diff to `/tmp/pr_diff.txt`, as att-006 had on the same target and arm, and
att-071 (arm A) kept its scratch path in `/tmp/pd071`. The three `/tmp` files are left in place,
because a re-audit judges a path by whether it exists.

The copies, with their SHA-256 sums, are also kept outside the repository at
`~/.t3/bench-runs/2026-09-24-builtin-baseline/evidence/tmp/`, so a re-audit can restore them.

## Scoring (2026-09-25)

Scoring steps are charges in `charges.jsonl`, metered from each session's own transcript at its
`rates.json` entry. Fable 5.1 was added to `rates.json` on 2026-09-25 for this phase; no arm uses it.

| # | Step | Session | Result | Billed ($) |
| --- | --- | --- | --- | --- |
| S25 | independent review of the scoring plan: `claude -p --model claude-fable-5-1 --effort high`, read-only tools, no sub-agents, 18:23–18:31Z | `dc19ec16…` | 14 findings, all adopted; on its advice to grade with Fable 5.1, the maintainer kept Opus 5.5; every assistant line `claude-fable-5-1` | 5.47 |

Run spend after S25: $66.26; room under the cap after the reserve: $158.74.

### Grading, regression targets (i)–(n)

Each row is one `grade.py dispatch`: a fresh headless Claude Code 2.1.282 session, `--safe-mode`,
`claude-opus-5-5` at `high`, single-threaded, `--max-budget-usd 10`, from
`prompts/grader-template.md` (SHA-256 `e39af464…`), metered from its own transcript. Every
session's assistant lines are `claude-opus-5-5` and none started a sub-agent.

| # | Target | Session | Time (Z) | Result | Billed ($) |
| --- | --- | --- | --- | --- | --- |
| G1 | (i) | `fc3bf4c9…` | 20:38–20:42 | failed: `verdicts.json` left out each review's `items` wrapper, so `map` refused it; graded again as G7, not repaired | 1.23 |
| G2 | (j) | `6a8b1251…` | 20:39–20:42 | mapped: 4 recoveries, 1 false finding, 22 non-material, 1 unresolved (1 new candidate) | 0.92 |
| G3 | (k) | `cd6f7bb9…` | 20:42–20:44 | mapped: 8 recoveries, 1 false finding, 17 non-material | 0.49 |
| G4 | (l) | `d710b325…` | 20:42–20:44 | mapped: 13 recoveries, 17 non-material, 1 unresolved (1 new candidate) | 0.57 |
| G5 | (m) | `62b6e582…` | 20:44–20:46 | mapped: 2 false findings, 17 non-material | 0.67 |
| G6 | (n) | `0cdfe2fd…` | 20:44–20:46 | failed the read audit: it wrote `verdicts.json` one level above its directory (which holds nothing else) and moved it in; graded again as G8 | 0.64 |
| G7 | (i) | `4aa1d91a…` | 20:46–20:49 | mapped: 22 recoveries (GT-i1 15, GT-i2 7), 12 non-material, 9 unresolved (3 new candidates) | 0.99 |
| G8 | (n) | `7733bf50…` | 20:46–20:48 | mapped: 6 recoveries, 1 false finding, 20 non-material | 0.56 |

Regression grading: $6.07 for eight sessions, two of them failed and graded again from a new
`prepare` with new tokens. All six regression mappings were committed before any sealed register
was opened.

### Grading, fresh targets (o)–(r)

The four sealed registers were opened at 20:50:13Z with `seal.py open`, one file at a time into a
directory outside the repository, each matching the `plaintext_sha256` its `target.json` recorded;
the run is closed to dispatch from then on. Same configuration as G1–G8.

| # | Target | Session | Time (Z) | Result | Billed ($) |
| --- | --- | --- | --- | --- | --- |
| G9 | (o) | `d6d7f9d4…` | 20:50–20:52 | mapped: 16 recoveries, 2 false findings, 17 non-material | 0.62 |
| G10 | (p) | `3663c2d6…` | 20:50–20:52 | mapped: 9 recoveries, 2 false findings, 17 non-material | 0.64 |
| G11 | (q) | `7f0fc6b3…` | 20:52–20:54 | mapped: 33 non-material | 0.58 |
| G12 | (r) | `95be9165…` | 20:53–20:54 | mapped: 1 recovery (GT-r2), 30 non-material | 0.62 |

Grading in all: $8.54 for twelve sessions. Five new candidates, three on (i) and one each on (j)
and (l), are `unresolved` in mapping v1 and go to adjudication.

### Adjudication of new candidates

Each row is one headless Claude Code 2.1.282 session under a fresh home, `claude-opus-5-5` at
`high`, single-threaded, run through `grade.py dispatch` from `prompts/candidate-adjudication-template.md`
with the target's candidates (claim and the scorer's notes, arm, attempt and cost labels removed),
its register and the rubric, an offline provisioned clone, and network, `gh` and `git` for upstream
history. The read audit flagged only the allowed network commands. Rulings are in
[`adjudication/`](adjudication/).

| # | Target | Session | Time (Z) | Rulings | Billed ($) |
| --- | --- | --- | --- | --- | --- |
| A1 | (i) | `6ef3f56c…` | 20:53–20:59 | NC-1 true but below the bar (a non-defect); NC-2 and NC-3 one new material defect, GT-i3 | 1.68 |
| A2 | (j) | `0d24ddf2…` | 20:59–21:02 | NC-1 a new material defect, GT-j2 | 0.74 |
| A3 | (l) | `00d55259…` | 21:02–21:03 | NC-1 a duplicate of GT-l1 | 0.41 |

Registers (i) and (j) move to version 2; (l)'s stays at version 1.
