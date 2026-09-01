# Comparison data — v2, v3, v4, v5 on `tokio-rs/tokio#7757`

> **Promotion status:** “v5” is the historical prototype name used by this record. PR #17 promoted that workflow to `skills/code-review-publish` on `main`; new experiments should invoke `/code-review-publish` without the `-5` suffix.

**2026-09-01. Data only.** Every number here is measured or directly observed; the analysis is in
[`evaluation.md`](evaluation.md). All runs used Claude Code's `Agent` tool (`general-purpose`
sub-agents) at this session's default model. See [README.md](README.md#methodology-note-hindsight-contamination)
for a load-bearing caveat about v4's use of post-merge git history not available to the other three.

## Cost and shape

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Agents spawned | 3 (Code finder, Requirements finder, verifier) | 1 (verifier) | 1 (verifier) | 1 (verifier) |
| Sub-agent tokens (self/harness-reported) | 116,441 + 60,193 + 51,300 = 227,934 | 66,414 (verifier only) | 56,443 (verifier only) | 54,438 (verifier only) |
| Tool uses (self-reported) | ~95 total (orchestrator ~31 + sub-agents 64) | ~34 (+ verifier's own, batched in) | ~43 primary + 25 verifier = ~68 | ~46 primary (+ verifier's own 11) |
| Wall clock (self-measured) | ~21 min | ~25 min | ~29 min | ~19–22 min |
| Verifier used? | Yes — fresh-context, 2 candidates batched | Yes — conditional trigger (high-impact candidate hard to prove statically) | Yes — mandatory (both candidates proposed `must-fix`) | Yes — consequence-triggered (`must-fix` + compatibility break) |

## Output

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Candidates raised | 3 (2 Code + 1 Requirements question) | 2 formal (+ 2 risk-checks cleared pre-candidate) | 2 | 6 considered, 1 formally rendered |
| Dropped before publication | 0 of 2 verifier-eligible (both confirmed); question stands alone | 1 (refuted by verifier: cfg dead-code claim) | 1 (refuted by verifier: cfg dead-code claim) | 5 (falsified/no-consequence during primary review) |
| **Findings** | **2** (1 must-fix P1, 1 consider P2) | **1** (must-fix P1) | **1** (must-fix P0) | **1** (must-fix P1) |
| Blocking findings | 1 | 1 | 1 | 1 |
| Priority spread | P1, P2 | P1 | P0 | P1 |
| Questions | 1 | 0 | 0 | 0 |
| Coverage reported | complete (6/6) | complete (6/6) | complete (6/6) | complete (6/6) |
| **Derived status** | **Changes Requested (advisory)** | **Changes Requested (advisory)** | **Changes Requested (advisory)** | **Changes Requested (advisory)** |

**All four runs derived `Changes Requested`** — a first across all three tests: test 1 split on
status, test 2 was unanimous `Approved`, and here all four unanimously request changes, each backed
by an independently-derived must-fix finding.

## The convergent finding

All four runs independently identified the same underlying defect: `Spawner::spawn_task`
(`tokio/src/runtime/blocking/pool.rs`) has three branches after pushing to the new sharded queue, but
only one of them (the "spawn a new thread" branch) rechecks the shutdown flag and drains the queue if
shutdown raced in — a recheck the PR's own second commit added specifically to fix "orphaned tasks on
shutdown." The other two branches call only `notify_one()`, with no recheck, reopening the same bug
class the second commit thought it had closed.

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Branch(es) implicated | Both unguarded branches (`pool.rs:453-455` and `:457-459`) | The idle-notify branch only (`pool.rs:457-460`); the "at max threads" branch (`:453-455`) was checked and judged self-healing | Both, via a "protocol inversion" framing centered on `num_idle_threads` accounting timing | Both unguarded branches (`pool.rs:453-460`), explicitly including the "at max threads" branch |
| Specific mechanism | Stale `Relaxed` reads of `num_idle_threads`/`num_threads` racing a worker's shutdown exit | A *keep-alive-timeout* race: `wait_for_task`'s timeout decision returns before `Inner::run` decrements `num_idle_threads` | A worker claims a task inside `wait_for_task` before `Inner::run` decrements `num_idle_threads` for it — "the spawner reads a stale idle count for a worker that already stopped being available" | Worker decrements `num_idle_threads` (on `WaitResult::Shutdown`) before its drain sweep finishes and before `dec_num_threads()` — the precise window later confirmed by v4's historical citation |
| Priority assigned | P1 | P1 | **P0** | P1 |
| Verifier's independent contribution | Confirmed both candidates; tightened candidate A's trigger to not need the idle-branch case | Confirmed the finding; corrected the "hidden by shard affinity" framing (no worker remains, not a scan miss) | Confirmed with corrections; found the historical revert (see README caveat); sharpened the fix to match what upstream's actual re-land did | Confirmed with corrections; identified that neither of the two closest existing loom tests models this exact interleaving |
| Fix proposed | Recheck shutdown unconditionally right after push, before branching | Have `wait_for_task` decrement idle count itself, atomically with its timeout decision | Move the idle-worker claim to the spawner, atomically with the `num_idle_threads()` read, under a coordination lock | Recheck shutdown in both unguarded branches, mirroring the existing recheck |

**v3 is the one partial outlier**, and the disagreement is checkable, not just a difference in
framing: v3 explicitly examined the "at max threads, notify anyway" branch (`pool.rs:453-455`) as a
named risk check and concluded it was "self-healing via the busy-loop's full-shard rescan since
`idle == 0` implies no thread is parked in `wait_for_task` there." The premise doesn't hold in the
exact interleaving v2, v4, and v5 (and the verifier in each of those three runs) constructed: `idle ==
0` also occurs when the *last* worker has just finished exiting — decremented its idle count on the
way out, but not yet decremented its thread count — which is precisely the window the real,
historically-confirmed bug lives in. v3 still published a real, independently-valid P1 finding
against the sibling branch via a different (also real) race, so its overall verdict is not wrong, but
its risk-check dismissal of the other branch is the one factual claim across all four reports that
direct inspection of `pool.rs` does not support. See [evaluation.md](evaluation.md) for the verified
line-by-line trace.

## Secondary candidates and disagreements

| Candidate | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Shutdown-race drain runs `spawn_mandatory_blocking` work on the caller's thread (`pool.rs:421`) | **Raised, confirmed, published** (P2 consider) | Not raised | Not raised | Not raised |
| `fastrand_n`/`thread_rng_n` `cfg` widening could compile a dead-code path under `sync`-only builds | Checked by the Requirements finder, judged out of scope (lint territory), not raised as a candidate | **Raised, refuted by verifier** (module-level gate on `mod rand;` already prevents it) | **Raised, refuted by verifier** (same module-level gate) | Checked during falsification, found necessary and correct, not raised |
| Does the single non-sharded `condvar_mutex` in `notify_one` limit the issue's "cost shouldn't scale with load" goal under saturation? | **Raised as an open question** (Requirements axis) | Not raised | Not raised | Not raised |
| Nested shard-lock / `condvar_mutex` locking pattern (the `ADD-SP` prior-review concern named in the packet) | Not separately traced | **Explicitly traced**, single consistent lock order found, no cycle | Not separately traced | Weighed as evidence that the concern was "raised and left unresolved," not "examined and accepted" |

v3 and v4 converged independently on the same refuted candidate (`fastrand_n` cfg dead code) and were
both corrected by their own verifiers via the identical citation (`tokio/src/util/mod.rs:61`'s
module-level gate) — the clearest case across all three tests of two independent architectures making
the same specific static-analysis mistake and having their own verification step catch it.

Only v2's Requirements axis raised the `condvar_mutex`-under-saturation question — a genuine
open empirical question about the design's remaining serialization point that no other run's
architecture had a channel to surface at all (v3/v4/v5 have no separate requirements axis or question
mechanism outside a candidate ledger).
