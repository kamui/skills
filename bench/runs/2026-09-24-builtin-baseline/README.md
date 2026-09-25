# Run 2026-09-24-builtin-baseline: the first scored run

`review-code` (arm A) against Claude Code's built-in `/code-review` on Sonnet 5 (B) and Opus 5.5
(C) and Codex CLI's `codex review` (D), on the ten targets (i)–(r): 4 arms × 10 targets × 2
replicates, 80 planned cells. The narrative, the preregistered questions, the grid, the budget and
the stopping rule are in
[`docs/research/builtin-review-benchmark-2026-09-24/`](../../../docs/research/builtin-review-benchmark-2026-09-24/README.md);
every chargeable step is in its [`ledger.md`](../../../docs/research/builtin-review-benchmark-2026-09-24/ledger.md).

**Frozen 2026-09-24.** `manifest.json` carries `frozen_at`; `freeze_commit` names the commit that
introduced it. Nothing in the manifest changes after the first dispatch except by an appended
deviation naming the cells it invalidates (design §4). No scored cell had been dispatched at the
freeze; the pilot ran on 2026-09-25 (below).

## Files

| Path | Holds |
| --- | --- |
| `manifest.json` | the frozen run: arms resolved with file hashes, the `review-code` tree, the pinned CLI versions and expected prompt hashes; the cohort with register versions and packet, diff and provisioning identities; the 80 planned cells; the caps; the sealed order; the rates used; the execution policy |
| `charges.jsonl` | every charge that is not an attempt (the shakedown, the hunts, the adjudications, the probes), counted against the cap by `run_cell.py` |
| `probes/att-00N/` | the three pre-dispatch probes on the toy fixture, filed by `file_attempt.py` under run id `2026-09-24-builtin-baseline-probe` |
| `attempts/att-NNN/` | one record per dispatched cell, written by `run_cell.py` (the pilot's att-001 to att-004 so far; att-002 and att-004 re-filed with `--replay`) |
| `scoring/<target>/mapping.v<M>.json` | blind adjudication per target (none yet) |
| `results.v<M>.json` | `score.py` output (none yet) |

## Pins

| What | Pinned as | Where it came from |
| --- | --- | --- |
| Claude Code | `2.1.282` (`~/.local/share/claude/versions/2.1.282`) | the version installed on the suite machine at the freeze; the shakedown ran `2.1.281` |
| Codex CLI | `0.156.1` (`~/.local/share/mise/installs/node/24.19.0/bin/codex`, the npm package) | the version the shakedown ran; the machine's node moved to 24.21.0 on 2026-09-24, after which a bare `codex` resolved to a 0.149.1 standalone install |
| `skills/review-code` | tree `c3c53da5381dace16876b0f5b7abe4bccc6bc58b` | `HEAD:skills/review-code` at the freeze commit's parent (`fc5929c`) |
| built-in prompt variants | Sonnet `665e2e51…`, Opus `bf131e06…`; Codex rubric `ec60e7f3…` | observed by the probes below, registered in `bench/harness/` |
| rates | Sonnet 5 and Opus 5.5 `as_of 2026-09-24`, GPT-6 Astra `as_of 2026-09-24` | `bench/rates.json`; the Claude entries were read from the pricing page on the freeze day |
| method, rubric, metric code | `bf3c25f5…`, v1, `33c78ced…` | the one-shot method's last commit; `bench/rubric/scoring.v1.md`; the last commit to `bench/tools/` |

**Both CLIs are pinned through a run-local `bin/` directory**, `~/.t3/bench-runs/2026-09-24-builtin-baseline/bin/`,
holding `claude → ~/.local/share/claude/versions/2.1.282` and `codex → ~/.local/share/mise/installs/node/24.19.0/bin/codex`.
`dispatch.sh` calls `claude` and `codex` by name, so every dispatch of this run is made with that
directory first on `PATH`; `file_attempt.py` marks an attempt whose CLI version differs from the
pin harness-invalid, and a pin that has to change mid-grid is a deviation. Claude Code's
auto-update is off in the maintainer's settings (`autoUpdates: false`, copied into every fresh
home). Node itself is not pinned: the Codex npm package runs its own native binary, and the node
each target was smoke-checked with is recorded in its `provisioning.platform` and in its
`smoke.json` `platform`, not in its allowance — i–n were measured on `v24.19.0` and o–r, after the
machine's upgrade, on `v24.21.0`.

## Pre-dispatch probes (2026-09-24, ledger S22–S24)

Each probe ran the arm through `dispatch.sh` under the pinned `bin/` on the toy fixture of
[`2026-09-24-toy`](../2026-09-24-toy/README.md), then was filed with `file_attempt.py` against the
version the manifest pins. They are observations of the toolchain, not cells; the fixture is never
pooled with scored targets.

| Probe | Arm | CLI | Model | Prompt | Diff command | Disposition | Cost ($) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `probes/att-001` | B | claude-code 2.1.282 | claude-sonnet-5 | `665e2e51…` `high effort → 3+5 angles × 6 candidates → 1-vote verify` | `git diff main...HEAD` | valid completed | 0.11 |
| `probes/att-002` | C | claude-code 2.1.282 | claude-opus-5-5 | `bf131e06…` `high effort → 8 inline angles → dedup (no verify)` | `git diff main...review-head` | valid completed | 0.10 |
| `probes/att-003` | D | codex-cli 0.156.1 | gpt-6-astra | `ec60e7f3…` review rubric | `git diff main...review-head` | valid completed | 0.13 list |

Both built-in variants hash exactly as they did on 2.1.281, so the arm files' expected variants
stand and `bench/harness/claude-code.json` gained a `2.1.282` entry pointing at the same bodies.
Two differences from the shakedown are recorded there: the Opus probe diffed the argument's range
rather than `main...HEAD`, and it returned its findings as a fenced JSON array rather than a
`ReportFindings` call. Arm A has no probe: it runs the same `claude` binary the B and C probes
observed, its skill tree is resolved by git, and a $0.50 fixture run would observe nothing the
manifest does not already pin. The Codex probe's rollout reports the plan's quota at 62% of the
weekly window, resetting 2026-09-26T09:19:52Z.

## Sealed order

The manifest's `sealed_order` was generated once, before any dispatch, as follows. The pilot cells
come first: (i) and (n) under B and D, replicate 1 (README §6). Then replicate 1 of every other
cell, target by target: the ten target ids in the order given by `random.Random(seed).shuffle`
over the id-sorted list, with `seed` the first 16 hex digits of the SHA-256 of the ten
`packet_sha256` values concatenated in id order (`9923346520887961045`), and within each target the
four arms in A, B, C, D order rotated by the target's position (position 0 starts at A, 1 at B,
and so on), skipping the pilot cells already placed. Then replicate 2 in the same target order,
each target a block of four arms rotated one step further. The resulting target order is
q, p, r, i, l, k, n, o, m, j.

## Caps and the stopping rule

| Cap | Value |
| --- | --- |
| Spend | $250 for the whole experiment, counting `charges.jsonl` ($28.31 at the freeze) and every attempt at its metered cost, Codex at list-price equivalent |
| Closeout reserve | $25, protected from the start |
| Attempts | 84 (80 cells and at most 4 replacements) |
| In flight | 2 |
| Per-attempt bound | the arm file's `budget_usd_per_attempt` (A $5, B $2.50, C $5, D $3), reserved while an attempt is in flight; `dispatch.sh` also passes `--max-budget-usd 15` to Claude |

`run_cell.py` refuses a dispatch whose bound does not fit in cap − spent − reserve, one attempt at
a time; no cap check in `bench/tools` works at block granularity. Replicate 1 runs first across all
forty cells; replicate-2 blocks then run in the sealed target order until the next block's
conservative bound no longer fits, and the unrun blocks are reported as unattempted (README §6).

**The block gate of README §6 is the operator's, not `--next`'s.** Before starting each
replicate-2 block, compare `--status`'s `room_usd` against that block's conservative bound — $15.50
for the four arms — and stop the run there if it does not fit. Left to `--next` alone, a room
figure between one arm's bound and $15.50 would let the block's cheaper arms dispatch and refuse
the rest, and a half-run block cannot be repaired inside the cap. README §6 expects $210 of cell
spend, with a $310 conservative bound, against the $196.69 of room this manifest freezes, and says
plainly that the expected total already exceeds the cap; the gate is expected to bind, not
hypothetical.

## Dispatching

```sh
export PATH="$HOME/.t3/bench-runs/2026-09-24-builtin-baseline/bin:$PATH"
python3 bench/tools/run_cell.py --run bench/runs/2026-09-24-builtin-baseline --status
python3 bench/tools/run_cell.py --run bench/runs/2026-09-24-builtin-baseline --next \
    --quota "<the plan quota as the last Codex rollout reported it>"
```

Before each dispatch `run_cell.py` re-validates the manifest, re-hashes the four arm files, and
compares the target's `packet.md` and diff identity against the cohort entry. The cohort's
`provisioning_sha256` is not one of those gates, and nothing else re-derives it either:
`compare.py` reads the value out of each run's manifest to compare runs under the comparison
contract, never off the live target. So nothing holds a target's live `provisioning` block against
the freeze, and the prose fields pass straight through: `render_policy` writes the live
`provisioning.allowance` and `provisioning.unavailable` into the reviewer's `input.md`, so an edit
to either reaches the reviewer unrefused. The cache archive is the one part checked live. On the
eight targets whose `provisioning.cache.build` is non-empty, `provision.py prepare` restores the
archive only when its sha256 matches the live `dependency_identity` entry, and `run_cell.py` turns
that failure into an `InputError` before any reviewer starts — but it checks the live file, not the
freeze, so an edit that moves the archive and its entry together still passes, and `l-bokeh-9232`
and `n-ripgrep-2957` (`cache.kind: none`) have no archive to check. Treat that block as frozen with
the manifest, record any change to it as a deviation, and re-derive the hash by hand with
`compare.py --provisioning-hash bench/targets/<id>` whenever a target's provisioning is touched.

Every filed attempt gets a ledger row. The first four cells are the pilot; they double as the
demonstration that focused-test execution works under D and B on suite targets whose review needs
a test run ((i) runs pytest from its provisioned virtualenv; (n) runs scratch zsh), which README
§10 left open at the freeze. Scoring waits for every planned attempt to be filed: the sealed
registers are then opened with `seal.py` (`docs/research/builtin-review-benchmark-2026-09-24/sealed/README.md`)
and `score.py` runs with `--opened`.

## Pilot (2026-09-25)

The first four cells of the sealed order, (i) and (n) under B and D, ran on 2026-09-25 between
00:33Z and 00:36Z, two in flight, with the pinned `bin/` on `PATH`. Each finished in under a
minute. The ledger has a row per attempt.

| Attempt | Cell | Disposition | Metered ($) | What the reviewer did |
| --- | --- | --- | --- | --- |
| att-001 | (i) / B / 1 | valid completed | 0.19 | one `git diff`; 7 items |
| att-002 | (i) / D / 1 | valid completed (re-filed; first filed stopped) | 0.26 list | read the change, the clone and its own dependency cache's urllib3 sources; 3 findings, verdict `patch is incorrect` |
| att-003 | (n) / B / 1 | valid completed | 0.08 | one `git diff`; 4 items |
| att-004 | (n) / D / 1 | valid completed, empty (re-filed; first filed stopped) | 0.20 list | ran offline zsh checks of the completion script; no finding, verdict `patch is correct` |

**Focused execution.** The Codex arm ran commands under the target's allowance on (n), so the D
adapter's execution path works on a suite target. The Sonnet built-in ran nothing beyond one
`git diff` on either target, though its adapter allows `Bash`; that is the arm's own choice and
is recorded, not repaired.

**Harness defects.** Both Codex reviews ran to completion and exited 0, and both were stopped by
post-processing. `normalize_review.py` knew only Codex's single-finding marker, `Review comment:`.
With several findings Codex CLI 0.156.1 writes `Full review comments:`, and with none it prints its
summary alone; both came back `unresolved`, which `dispatch.sh` turns into a stop. The read audit
also read the slash after a glob, as in `python*/site-packages/...`, as the start of an absolute
path and flagged att-002's reads of its own cache. The toy fixture had one finding per review, so
none of these paths had run before. Commit `0200519` fixes all three with tests, and the manifest
records the move of `bench/tools` as a deviation that invalidates nothing: the change touches no
reviewer input or execution condition, and att-001 and att-003 re-audit and re-normalize
identically. Re-processed into scratch files with the fixed tools, att-002 parses to three items
with no audit violation, and att-004 to an empty review. The glob fix also stopped the audit
reading a word that starts with a slash and then a glob, such as `/*/x`, as an absolute path.
Commit `552a6f8` keeps glob characters inside an absolute path, and the manifest's third deviation
records it; the paths extracted from the four attempts' recorded commands are unchanged, so no
filed attempt changes. The same fix dropped the flag on a dot-led glob that bash expands to `..`,
such as `cat .*/.*/<path>`. Commit `f1a4343` judges such a segment as `..`, and the fourth
deviation records it; every path extracted from the four attempts' commands stays inside the
attempt directory, so no filed attempt changes.

**How att-002 and att-004 count: re-filed, no replacement.** The method reruns a cell, consuming
a replacement, when a harness repair changes inputs or execution conditions (method §3); this
repair changed neither, so the maintainer chose to re-file both from their own outputs rather than
spend two of the four replacements discarding two complete reviews. Commit `6f61765` lets
`file_attempt.py --replay` supersede a stop the wrapper wrote only because its normalizer failed
after a zero exit, once the replayed normalizer parses; the stop is kept as `stop.recorded.json`
and noted in the record. Re-filed at that revision, att-002 is valid with three parsed items and a
clean audit, and att-004 is valid and empty. Each takes its stop instant as `completed_at` and keeps
a null `payload_validated_at`, because the replay stamps no validation time. Usage is unchanged; the
transcript archives were rewritten, with new hashes, and passed the restoration check. The
manifest's second deviation records this and invalidates nothing. The pilot therefore closes with
four valid attempts and no replacement used, and the sealed order continues at
`q-soba-195/review-code-sonnet-high/1` on the maintainer's go.

