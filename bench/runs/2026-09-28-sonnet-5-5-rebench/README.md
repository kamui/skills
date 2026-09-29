# Run 2026-09-28-sonnet-5-5-rebench: the built-in and `review-code` on Sonnet 5.5

Claude Code's built-in `/code-review` and `review-code` as it is on `main`, both on Sonnet 5.5 at
high effort, on all twelve suite targets with three replicates each: 2 arms × 12 targets × 3
replicates, 72 planned cells. The built-in is the reference `review-code` has to beat. The scored
numbers go to [`bench/SCOREBOARD.md`](../../SCOREBOARD.md).

This run measures where the two reviewers stand on a new model. It decides nothing about a
`review-code` change, so it has no pass rule.

## Files

| Path | Holds |
| --- | --- |
| `manifest.json` | the frozen run: both arms with file hashes, the `review-code` tree, the CLI pin and the expected built-in prompt; the twelve-target cohort; the 72 planned cells; the caps; the sealed order; the rate entry; the execution policy |
| `order.py` | derives `planned_cells` and `sealed_order` from the cohort; `--check` compares them with the manifest |
| `charges.jsonl` | every charge that is not an attempt: the probes and the grading sessions |
| `probes/att-001/` | the built-in arm's pre-dispatch probe on the toy fixture, filed under run id `2026-09-28-sonnet-5-5-rebench-probe` |
| `attempts/att-NNN/` | one record per dispatched attempt, written by `run_cell.py` |
| `scoring/<target>/` | the blind mapping and scorecard per target, written by `grade.py map` |
| `results.v<M>.json` | `score.py` output |

## Arms

| Arm | What runs | Isolation |
| --- | --- | --- |
| `claude-builtin-sonnet-5-5-high` | `/code-review main...review-head high` with `--model claude-sonnet-5-5 --effort high` | `--safe-mode`, a fresh home, the read audit |
| `review-code-sonnet-5-5-high-enforced` | the `review-code` skill at tree `5e12864b`, which is `origin/main:skills/review-code` at `5919888`, with `--model claude-sonnet-5-5 --effort high` and its workers on `sonnet` | `claude-strict-v2`: an enforced filesystem and network sandbox, a read-only clone, a fresh home, the read audit |

Both arm files are new. Each copies its Sonnet 5 predecessor (`claude-builtin-sonnet-high` and
`review-code-sonnet-high-enforced-x394-control`) and changes only the model, the expected built-in
prompt, and the `review-code` attempt bound, raised from $5 to $8 because no Sonnet 5.5 review
cost had been observed.

**The isolation differs between arms, as in every earlier built-in comparison.** The runner has
sandbox support for `review-code` only. The built-in runs as it did in the 2026-09-24 baseline, so
its Sonnet 5 and Sonnet 5.5 rows differ in the model and the CLI alone. The scoreboard names the
difference.

## Pins and probes

| What | Pinned as | Evidence |
| --- | --- | --- |
| Claude Code | `2.1.284`, a byte copy at `~/.t3/bench-cache/cli/2.1.284` (sha256 `5cd90aab…`) | the version of the #411 run; the run's launcher puts a `claude` link to the copy first on `PATH` and sets `BENCH_CLAUDE` to it |
| model | `claude-sonnet-5-5` for both arms | the alias probe in `charges.jsonl`: `--model sonnet` and `--model claude-sonnet-5-5` were both answered by `claude-sonnet-5-5`, so `review-code`'s `sonnet` workers run Sonnet 5.5; `file_attempt.py` marks any other observed model harness-invalid |
| built-in prompt | `bf131e06…`, `high effort → 8 inline angles → dedup (no verify) → ≤10 findings` | `probes/att-001`: valid, one `git diff main...HEAD`, a fenced JSON array, $0.05 |
| `skills/review-code` | tree `5e12864b52b6c0c52b9b1b1f41d5b22fa2576676` | `git rev-parse origin/main:skills/review-code` at the freeze |
| rates | `claude-sonnet-5-5` `as_of 2026-09-28`: $2 input, $10 output, $0.20 cache read | the pricing page read on 2026-09-28; the same figures as Sonnet 5 |

**The built-in's prompt changed with the model.** On 2.1.281 and 2.1.282, Sonnet 5 received the
body `665e2e51…` (`3+5 angles × 6 candidates → 1-vote verify`) and Opus 5.5 received `bf131e06…`.
On 2.1.284, Sonnet 5.5 receives `bf131e06…`. A Sonnet 5 to Sonnet 5.5 change in the built-in's
numbers is therefore a product change as well as a model change. `bench/harness/claude-code.json`
records the observation. The new arm scores priority by rank, like the Opus arm that ran the same
body.

## Cohort

All twelve targets, each at its latest register: `i-requests-6667` v2, `j-trpc-5017` v3,
`n-ripgrep-2957` v2, and v1 elsewhere. The six regression targets (i to n) are `regression`, and
the six vetted fresh targets (o to t) are `fresh`. Every register is plaintext in the repository,
so grading needs no `--opened` directory. `provision.py check` passed for all twelve mirrors before
the freeze.

`o-astro-16079`'s focused tests build fixtures into the clone. Under `claude-strict-v2` the clone
is read-only, so `review-code` cannot run them there, as in the #394 run. The target stays in the
cohort, because the scoreboard compares the reviewers on the whole suite.

## Sealed order

`order.py` derives it. The target order is `random.Random(seed).shuffle` over the id-sorted cohort,
with `seed` the first 16 hex digits of the SHA-256 of the twelve `packet_sha256` values
concatenated in id order (`2310561838200223714`), as in the 2026-09-24 baseline. The order is t, i,
o, m, p, r, j, n, s, l, q, k. All 36 built-in cells come first, replicate by replicate, and then
the 36 `review-code` cells the same way. The maintainer funded the built-in first.

## Caps and gates

| Cap | Value |
| --- | --- |
| Spend | $125: $25 for the built-in and $100 for `review-code`, as approved on 2026-09-28, counting `charges.jsonl` and every attempt at its metered cost |
| Closeout reserve | $12, for blind grading |
| Attempts | 76 (72 cells and at most 4 replacements) |
| In flight | 2 |
| Per-attempt bound | the arm file's `budget_usd_per_attempt`: built-in $2.50, `review-code` $8 |

`run_cell.py` enforces the total. The split between the arms is the operator's to hold, at two
gates:

1. **After the built-in's 36 cells.** The built-in's attempts plus the probes must be at most $25.
   They are expected at $5 to $15.
2. **After `review-code`'s replicate 1.** Project replicates 2 and 3 at twice replicate 1's metered
   cost. If the projection plus spent plus the reserve exceeds $125, stop and ask the maintainer
   before any further dispatch.

A harness-invalid or stopped attempt is replaced with `run_cell.py --replace` when its cause is the
harness, and the reason is recorded in the ledger.

## Grading and scoring

Each target is graded once, after all six of its attempts are filed, by one Opus 5.5 high session
that sees both arms' reviews blind (`grade.py prepare`, `dispatch`, `map`), with the grader template
of the 2026-09-24 baseline. A dispatch that exits 1 is graded again from a new `prepare`. When all
twelve are mapped, `score.py` writes `results.v1.json`, and `bench/tools/scoreboard.py` regenerates
the scoreboard.

## Dispatching

```sh
L=~/.t3/bench-cache/sonnet55-2026-09-28/bin/launch.sh
$L python3 -B bench/tools/run_cell.py --run bench/runs/2026-09-28-sonnet-5-5-rebench --status
$L python3 -B bench/tools/run_cell.py --run bench/runs/2026-09-28-sonnet-5-5-rebench --next
```

`launch.sh` unsets the orchestrating session's `CLAUDE*`, `ANTHROPIC*` and `AI_AGENT` variables,
puts the pinned CLI and the sandbox tools on `PATH`, and runs its arguments.

## Results

Dispatched 2026-09-28 23:08Z to 2026-09-29 03:32Z. All 72 cells are filed in 74 attempts, and each
target has one blind mapping over both arms. `results.v1.json` is `score.py` output over the
twelve v1 mappings. The headline numbers are on the [scoreboard](../../SCOREBOARD.md).

| | Built-in | `review-code` |
| --- | --- | --- |
| Valid completed reviews | 36 of 36 | 31 of 36 |
| Recall, every planned review | 75% | 67% |
| Recall, completed reviews only | 79% | 82% |
| Reviews that missed every registered defect | 3 of 27 | 3 of 22 |
| Reviews that approved a buggy change | 0 of 27 | 5 of 22 |
| False findings | 27 in 36 reviews | 0 in 31 |
| Noise items per review | 5.2 | 1.7 |
| Recovered defects with a sufficient fix | 9 of 31 | 16 of 22 |
| Metered cost | $4.66, $0.12 per attempt | $38.13, $1.06 per attempt |
| Median time to completion | 38 s | 3 min 28 s |

**The built-in finds as much and flags far more that is wrong.** Its 27 false findings fall on 8
of the 12 targets: 10 on `r-base-ui-5460`, and 5 on the three clean targets. On the
nine targets both runs graded under the same register, the Sonnet 5 built-in had 2 false findings in
18 reviews. The Sonnet 5.5 row runs a different prompt, so the rise belongs to the model and the
prompt together.

**`review-code` never reported a false finding, and 5 of its 36 reviews are incomplete.** Four
stopped when the sandbox denied a Bash command. The reviewer reported the denial and ended without
writing its artifacts, although the denial text invites another route. They are att-050
(`k-graphql-js-1582`), att-052 and att-064 (`i-requests-6667`), and att-070 (`n-ripgrep-2957`). The fifth, att-074 (`k-graphql-js-1582`), finished and reported its own
coverage incomplete. None was replaced: the method replaces a stop only when the harness caused it,
and the same profile denied commands in 24 of 51 Sonnet 5 reviews across the #394 and #409 runs
without one stop. Counted as reviews that recovered nothing, the four stops take `review-code`'s
recall from 82% on completed reviews to 67%. Its five approvals of a buggy change are on
`j-trpc-5017` (1), `n-ripgrep-2957` (2) and `r-base-ui-5460` (2).

**Spend.** $51.48 of the $125 cap: the built-in $4.66, `review-code` $38.13, the probes $0.08, and
14 grading sessions $8.62. Two of those sessions were `o-astro-16079`'s failed gradings ($1.16),
whose cause the third deviation records. The built-in stayed inside its $25 share, and the
projection at gate 2 ($26 for replicates 2 and 3) held: they cost $25.27.
