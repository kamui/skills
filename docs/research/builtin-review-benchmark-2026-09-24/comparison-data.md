# Comparison data — built-in reviewer benchmark

No scored cell has run. This file holds the Phase 0 adapter fixtures: one wrapper run per arm on
the toy repository (one Python file; the head commit adds `average()` that divides by
`len(prices)` while its docstring and the packet say empty carts are common). Every arm found the
defect; the rows show what each adapter captures, not review quality.

Rows are pasted from `transcript_usage.py --row` (A, B, C) and `codex_usage.py --row` (D) at the
rates in `ledger.md`. `Wall` is the agent span sum, not elapsed time; elapsed comes from
`timing.json`.

## Toy fixtures (2026-09-24)

| Run / agent | Model | Turns | Tool calls | Text-only turns | Input | Cache write | Cache read | Output | Thinking | Wall | Billed cost ($) | Report output (est.) | Production-shaped ($) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| toy A review-code sonnet high | claude-sonnet-5 | 17 | 21 | 2 | 34 | 69,974 (5m 14,790, 1h 55,184) | 742,161 | 9,003 | 1,216 | 0:01:36 | 0.50 | — | — |
| toy B2 builtin sonnet `--effort high` | claude-sonnet-5 | 2 | 1 | 1 | 4 | 12,235 | 28,446 | 461 | 147 | 0:00:03 | 0.04 | — | — |
| toy C2 builtin opus `--effort high` | claude-opus-5-5 | 3 | 2 | 1 | 6 | 6,561 | 36,649 | 953 | 55 | 0:00:10 | 0.07 | — | — |
| toy D codex default | gpt-6-astra | 4 | 3 | 1 | 5,023 | 0 | 25,216 | 562 | 0 | 0:00:20 | 0.10 | — | — |

| Run | Variant or rubric observed | Executed diff | Native verdict | Items | Elapsed to completion |
| --- | --- | --- | --- | --- | --- |
| A | `review-code` tree `6862d993a1499009a4d59d54a38a1d34daef9ea7`; one fresh-context sonnet verifier; reproduced the error at the head | `git diff main...review-head` via the skill's store | `Changes Requested` | 1 finding, `P2` `must-fix` | 89 s |
| B2 | `high effort → 3+5 angles × 6 candidates → 1-vote verify (recall-biased) → ≤10 findings`; no fan-out on the five-line diff | `git diff main...HEAD` | `findings` (JSON block) | 1 finding | 5 s |
| C2 | `high effort → 8 inline angles → dedup (no verify) → ≤10 findings` | `git diff main...review-head` | `findings` (ReportFindings) | 1 finding, `CONFIRMED` | 6 s |
| D | Codex review rubric (child rollout) | `git diff base...review-head` | `patch is incorrect` (rollout `overall_correctness`) | 1 finding, `P2` | 20 s |

Read audits: A, B2, C2 and D all pass with zero violations after the audit learned to expand
`~` against the fresh home, to record ancestor guidance probes, and to accept the reviewer's
`TMPDIR` inside the attempt directory (A's run predates the `TMPDIR` change and was audited with
its `/tmp/review-code-*` store allowed explicitly). A's reviewer ran `git checkout --detach` and
switched back; the tree identity at exit matched the one at dispatch, and the grid treats any
mismatch as harness-invalid.

Fixture directories: `~/.t3/bench-runs/toy/{A,B2,C2,D}/` (not committed; each holds
`prompt.txt`, `dispatch.txt`, `stdout.*`, `stderr.txt`, `timing.json`, `audit.json`,
`payload.json` or `artifacts/`, `normalized.json`, and the fresh `home/`).
