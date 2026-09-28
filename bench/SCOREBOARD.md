# Reviewer benchmark scoreboard

This page holds the headline numbers of the reviewer benchmark, one section per suite. A suite fixes its targets, packets, diffs, registers and rubric, and every row is marked on each target it did not run or ran under a different identity. The legend under each table says which direction is better for each column. The method and its rules are in [README.md](README.md).

The page is generated from `bench/scoreboard.json`. Regenerate it with `python3 bench/tools/scoreboard.py`. `python3 bench/tools/scoreboard.py --check` fails when it is stale.

## Sonnet 5.5 re-bench, twelve targets

The Sonnet 5.5 rows come from the 2026-09-28 re-bench on Claude Code 2.1.284, three replicates per target. The Sonnet 5, Opus 5.5 and Codex rows come from earlier runs with two or three replicates per target, and each ran only some of the twelve targets. Every arm ran in a fresh home with the network off. The notes under the tables give each row's CLI and isolation.

The 12 targets and their register versions come from [`2026-09-28-sonnet-5-5-rebench`](runs/2026-09-28-sonnet-5-5-rebench/README.md). Rows come from:

- [`2026-09-28-sonnet-5-5-rebench`](runs/2026-09-28-sonnet-5-5-rebench/README.md), not scored yet, for `claude-builtin-sonnet-5-5`, `review-code-sonnet-5-5`
- [`2026-09-28-verification-off-staged`](runs/2026-09-28-verification-off-staged/README.md), `results.v2.json`, for `review-code-sonnet-5-5e12864`
- [`2026-09-28-unseen-target-comparison`](runs/2026-09-28-unseen-target-comparison/README.md), `results.v1.json`, for `review-code-sonnet-5-5e12864`
- [`2026-09-24-builtin-baseline`](runs/2026-09-24-builtin-baseline/README.md), `results.v3.json`, for `review-code-sonnet-5-c3c53da`, `claude-builtin-sonnet-5`, `claude-builtin-opus-5-5`, `codex-builtin`

### Each row on the targets it ran

Rows here cover different target sets, so their numbers do not compare directly. The next table compares each row with the reference on the targets both ran.

| Reviewer | Version | Targets | Valid reviews | Recall | Missed every bug | Approved a buggy change | False findings | Noise per review | Sufficient fixes | Cost per attempt | Median time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Code built-in /code-review, Sonnet 5.5 high (reference) | claude-code 2.1.284 | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| /review-code, Sonnet 5.5 high | 5e12864 (main since #406, 2026-09-27) | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| /review-code, Sonnet 5 high | 5e12864 (main since #406, 2026-09-27) | 7 of 12 | 21/21 | 47% | 6/15 | 5/15 | 0 (0.00 per review) | 1.0 | 6/9 | $2.88 | 12m 9s |
| /review-code, Sonnet 5 high | c3c53da (main from #370, 2026-09-24) | 9 of 12 | 18/18 | 76% | 2/14 | 6/14 | 0 (0.00 per review) | 1.0 | 9/14 | $0.79 | 2m 18s |
| Claude Code built-in /code-review, Sonnet 5 high | claude-code 2.1.282 | 9 of 12 | 18/18 | 87% | 1/14 | 0/14 | 2 (0.11 per review) | 2.6 | 7/16 | $0.14 | 26s |
| Claude Code built-in /code-review, Opus 5.5 high | claude-code 2.1.282 | 9 of 12 | 18/18 | 86% | 2/14 | 0/14 | 6 (0.33 per review) | 6.1 | 9/16 | $0.36 | 1m 19s |
| Codex CLI codex review, GPT-6 Astra default | codex-cli 0.156.1 | 9 of 12 | 18/18 | 62% | 4/14 | 2/14 | 0 (0.00 per review) | 0.2 | 8/10 | $0.29 † | 31s |

- **/review-code, Sonnet 5 high** at 5e12864 (main since #406, 2026-09-27) did not run `j-trpc-5017`, `n-ripgrep-2957`, `o-astro-16079`, `q-soba-195`, `r-base-ui-5460`.
- **/review-code, Sonnet 5 high** at c3c53da (main from #370, 2026-09-24) did not run `s-seaweedfs-10735`, `t-rclone-9699` and is not comparable on `j-trpc-5017` (register v2, suite v3).
- **Claude Code built-in /code-review, Sonnet 5 high** at claude-code 2.1.282 did not run `s-seaweedfs-10735`, `t-rclone-9699` and is not comparable on `j-trpc-5017` (register v2, suite v3).
- **Claude Code built-in /code-review, Opus 5.5 high** at claude-code 2.1.282 did not run `s-seaweedfs-10735`, `t-rclone-9699` and is not comparable on `j-trpc-5017` (register v2, suite v3).
- **Codex CLI codex review, GPT-6 Astra default** at codex-cli 0.156.1 did not run `s-seaweedfs-10735`, `t-rclone-9699` and is not comparable on `j-trpc-5017` (register v2, suite v3).

### Each row against the reference

Each row is paired with the reference, Claude Code built-in /code-review, Sonnet 5.5 high, on the targets both ran. Each cell shows this row, then the reference. The reference is not scored yet, so every pair is pending.

| Reviewer | Version | Shared targets | Valid reviews | Recall | Missed every bug | Approved a buggy change | False findings | Noise per review | Sufficient fixes | Cost per attempt | Median time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| /review-code, Sonnet 5.5 high | 5e12864 (main since #406, 2026-09-27) | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| /review-code, Sonnet 5 high | 5e12864 (main since #406, 2026-09-27) | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| /review-code, Sonnet 5 high | c3c53da (main from #370, 2026-09-24) | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| Claude Code built-in /code-review, Sonnet 5 high | claude-code 2.1.282 | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| Claude Code built-in /code-review, Opus 5.5 high | claude-code 2.1.282 | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |
| Codex CLI codex review, GPT-6 Astra default | codex-cli 0.156.1 | pending | pending | pending | pending | pending | pending | pending | pending | pending | pending |

Higher is better for valid reviews, recall and sufficient fixes. Lower is better for missed every bug, approved a buggy change, false findings, noise, cost and time. Recall is the macro mean over buggy targets. Per-review figures divide by valid completed reviews. Cost divides the metered price at the run's rates by every included attempt.

† List-price equivalent. These attempts ran on a plan that consumes quota, not dollars, so the figure prices their tokens at list rates.

- **Claude Code built-in /code-review, Sonnet 5.5 high** at claude-code 2.1.284. Safe mode, no sandbox.
- **/review-code, Sonnet 5.5 high** at 5e12864 (main since #406, 2026-09-27). Enforced sandbox (claude-strict-v2), claude-code 2.1.284.
- **/review-code, Sonnet 5 high** at 5e12864 (main since #406, 2026-09-27). Enforced sandbox. The control arm of the #409 experiments, from two runs, on claude-code 2.1.282 for five targets and 2.1.284 for two.
- **/review-code, Sonnet 5 high** at c3c53da (main from #370, 2026-09-24). No sandbox, claude-code 2.1.282.
- **Claude Code built-in /code-review, Sonnet 5 high** at claude-code 2.1.282. Safe mode, no sandbox. A different built-in prompt from Sonnet 5.5's, with 3+5 angles and a verify step.
- **Claude Code built-in /code-review, Opus 5.5 high** at claude-code 2.1.282. Safe mode, no sandbox.
- **Codex CLI codex review, GPT-6 Astra default** at codex-cli 0.156.1. Workspace-write sandbox with network access off. Cost is list-price equivalent, because the maintainer's plan bills quota.

### Per target

Each cell is attempt-level recall, or clean when the target has no registered defect, then the raw false-finding count.

| Target | Shape | Claude Code built-in /code-review, Sonnet 5.5 high | /review-code, Sonnet 5.5 high | /review-code, Sonnet 5 high | /review-code, Sonnet 5 high | Claude Code built-in /code-review, Sonnet 5 high | Claude Code built-in /code-review, Opus 5.5 high | Codex CLI codex review, GPT-6 Astra default |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Version |  | claude-code 2.1.284 | 5e12864 (main since #406, 2026-09-27) | 5e12864 (main since #406, 2026-09-27) | c3c53da (main from #370, 2026-09-24) | claude-code 2.1.282 | claude-code 2.1.282 | codex-cli 0.156.1 |
| `i-requests-6667` | concurrency, shared mutable state | *pending* | *pending* | 33% · 0 FF | 67% · 0 FF | 83% · 0 FF | 100% · 0 FF | 33% · 0 FF |
| `j-trpc-5017` | cross-file type obligation outside the diff | *pending* | *pending* | *not run* | *not comparable (register v2, suite v3)* | *not comparable (register v2, suite v3)* | *not comparable (register v2, suite v3)* | *not comparable (register v2, suite v3)* |
| `k-graphql-js-1582` | changed-test correctness | *pending* | *pending* | 100% · 0 FF | 100% · 0 FF | 100% · 0 FF | 100% · 1 FF | 100% · 0 FF |
| `l-bokeh-9232` | ordinary behavioural change | *pending* | *pending* | 100% · 0 FF | 100% · 0 FF | 100% · 0 FF | 100% · 0 FF | 100% · 0 FF |
| `m-grpc-go-7390` | clean, high risk (concurrency) | *pending* | *pending* | clean · 0 FF | clean · 0 FF | clean · 0 FF | clean · 2 FF | clean · 0 FF |
| `n-ripgrep-2957` | promised change that does not work as pasted (documentation, shell surface) | *pending* | *pending* | *not run* | 100% · 0 FF | 100% · 1 FF | 100% · 0 FF | 0% · 0 FF |
| `o-astro-16079` | security: authorization or injection, web backend | *pending* | *pending* | *not run* | 67% · 0 FF | 100% · 1 FF | 100% · 1 FF | 100% · 0 FF |
| `p-hono-5067` | released-compatibility break, public API or SDK | *pending* | *pending* | 0% · 0 FF | 100% · 0 FF | 100% · 0 FF | 100% · 2 FF | 100% · 0 FF |
| `q-soba-195` | refactor claiming no behaviour change, large mostly mechanical diff | *pending* | *pending* | *not run* | clean · 0 FF | clean · 0 FF | clean · 0 FF | clean · 0 FF |
| `r-base-ui-5460` | frontend component logic, React | *pending* | *pending* | *not run* | 0% · 0 FF | 25% · 0 FF | 0% · 0 FF | 0% · 0 FF |
| `s-seaweedfs-10735` | data loss in a persistence layer | *pending* | *pending* | 0% · 0 FF | *not run* | *not run* | *not run* | *not run* |
| `t-rclone-9699` | clean, high risk (concurrency) | *pending* | *pending* | clean · 0 FF | *not run* | *not run* | *not run* | *not run* |

*not run* means no run of the row included the target. *not comparable* means the row's run graded the target under a different register, packet or diff than this suite. *pending* means the row's run is not scored yet.
