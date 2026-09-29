# v2 run — `snapshot-path-omitted` against `tokio-rs/tokio#7757`

**2026-09-01.** Data only. Not published to the PR.

## Metadata

| | |
| --- | --- |
| Skill | `snapshot-path-omitted` (PR #14) |
| Architecture | Two axis finders (Code, Requirements) spawned in parallel, sub-agent per axis → one fresh-context verifier spawned for the Code axis's 2 candidates → orchestrator assembles and would-publish one review. Full four-role design as written; no fan-out beyond the mandated one-finder-per-axis. |
| Agents spawned | 3 — Code-axis finder (general-purpose sub-agent), Requirements-axis finder (general-purpose sub-agent, run in parallel with the first), fresh-context verifier (general-purpose sub-agent, spawned after both finders returned, given only claims/anchors/triggers, not `support`) |
| Total sub-agent tokens | 116,441 (Code finder) + 60,193 (Requirements finder) + 51,300 (verifier) = **227,934** self-reported subagent tokens (orchestrator-level context not separately metered) |
| Tool uses (self-reported) | Orchestrator: ~31 (10 Read, 17 Bash, 3 Agent spawns, 1 Write). Sub-agents: 35 (Code finder) + 16 (Requirements finder) + 13 (verifier) = 64. Grand total ≈ 95. |
| Wall clock (self-measured) | 2026-09-01 18:03:03 UTC → 18:23:44 UTC (start of substantive work to verifier completion), report assembly to follow ≈ 21 minutes for the review pipeline itself |
| Candidates raised | 3 — 2 Code-axis candidates (sent to verifier) + 1 Requirements-axis item from the "cannot tell from the code" bucket (routed directly to a question, per judgment call below, not sent to the verifier) |
| Candidates surviving falsification/verification | 2 of 2 verifier-eligible candidates confirmed (100%); the 1 Requirements question stands on its own track, unverified/unverifiable by design |
| Verifier verdicts | `confirmed` × 2, `plausible` × 0, `refuted` × 0. No merges (both candidates ruled genuinely distinct defects). One priority left unchanged in each case; one trigger tightened (Candidate A, see below) |
| Findings for publication | **2** (1 `must-fix`/P1, 1 `consider`/P2, both Code axis) |
| Questions | 1 (Requirements axis, "cannot tell from the code" bucket) |
| Coverage | Complete, 6/6 files (both finders independently marked every changed file `reviewed` with a reason; no file skipped, no fetch failed) |
| Derived status | **Changes Requested (advisory)** |

## Full reviewer report(s) — verbatim

### Code axis finder — verbatim

# Code axis findings — tokio sharded blocking-pool queue PR

## Candidates

### Candidate 1

- `id`: `code/pool-rs/shutdown-race-notify-branches-skip-recheck`
- `anchor`: `tokio/src/runtime/blocking/pool.rs:459`
- `fix`: `tokio/src/runtime/blocking/pool.rs:403-404` (move/duplicate the shutdown recheck here, unconditionally, before branching)
- `title`: spawn_task's shutdown recheck only covers 1 of 3 post-push branches
- `claim`: `Spawner::spawn_task` (pool.rs:390-462) checks `self.inner.queue.is_shutdown()` once at entry (line 392), pushes the task (line 403), then picks one of three branches on `metrics.num_idle_threads()`/`metrics.num_threads()`. Only the "spawn a new thread" branch (409-424) rechecks `shared.shutdown` and, if true, drains the queue via `task.shutdown_or_run_if_mandatory()`. The other two branches — "at max threads, notify anyway" (453-455) and "there are idle threads waiting" (457-459) — call only `self.inner.queue.notify_one()` with no shutdown recheck and no drain. `ShardedQueue::notify_one()` (sharded_queue.rs:148-153) only bumps a counter and pings whatever is currently parked on the condvar; it does nothing if every worker has already exited. `num_idle_threads()`/`num_threads()` are `Ordering::Relaxed` loads taken with **no lock held** at this point — unlike the pre-PR single-mutex design, where the equivalent reads/writes always happened while holding `shared`, which is what made Relaxed safe there.
- `trigger`: A pool with a small `max_blocking_threads` (e.g. 1). The sole worker is finishing its final task or its own post-shutdown drain (pool.rs:562-567) at the same instant `BlockingPool::shutdown()`/`Drop` sets the shutdown flag; the worker decrements `num_threads`/`num_idle_threads` at nearly the same instant a concurrent `spawn_blocking`/`spawn_mandatory_blocking` call reaches `spawn_task`, pushes its task, and reads a stale `num_idle_threads()==0 && num_threads()==thread_cap` (or stale `num_idle_threads()>0`). `notify_one()` then reaches no listener, `is_shutdown()` is never rechecked on this path, and no worker ever drains that shard again — the task (and its `JoinHandle`) is silently orphaned; if mandatory (e.g. a flush via `spawn_mandatory_blocking`, `tokio/src/fs/file.rs:756`), the mandatory work never runs.
- `change`: Recheck `self.inner.queue.is_shutdown()` unconditionally right after the push (pool.rs:403-404), before branching on idle/thread-cap state, and drain there if true — instead of only inside the "spawn a new thread" branch.
- `priority`: P1

Support (not for verifier): confirmed via `git show` that commit1 introduced the sharded design and commit2 added the recheck only in the spawn-branch. I could not run loom or stress-test the interleaving (constraints forbid it), so I can't empirically prove this is hit; the race window is a few instructions wide plus whatever Relaxed cross-core visibility delay exists. I'm confident the code path genuinely lacks the recheck on two of three branches; I'm not fully certain how practically reachable it is outside of loom's exhaustive search.

### Candidate 2

- `id`: `code/pool-rs/mandatory-task-runs-on-caller-thread`
- `anchor`: `tokio/src/runtime/blocking/pool.rs:421`
- `title`: Shutdown-race drain runs mandatory blocking tasks on the caller's thread
- `claim`: When the recheck at pool.rs:414 finds `shared.shutdown` true, it drains the whole queue inline on the *calling* thread: `while let Some(task) = self.inner.queue.pop(0) { self.inner.metrics.dec_queue_depth(); task.shutdown_or_run_if_mandatory(); }` (pool.rs:419-422). `Task::shutdown_or_run_if_mandatory` (pool.rs:163-166) calls `self.task.run()` for `Mandatory::Mandatory` tasks — i.e. it runs the user's blocking closure synchronously, on whatever thread called `spawn_blocking`/`spawn_mandatory_blocking` (potentially a tokio async worker thread), not a dedicated blocking-pool thread. This is inconsistent with the early-return check a few lines above in the same function (pool.rs:392-399), which handles the identical "task submitted after shutdown began" race by calling only `task.task.shutdown()` — explicitly never running it — with the comment "it's fine to shutdown this task (even if mandatory) because it was scheduled after the shutdown of the runtime began."
- `trigger`: Runtime shutdown races with a `spawn_mandatory_blocking` call (used by `tokio/src/fs/file.rs:756` and `:827` for flush-on-drop) issued from a tokio worker thread, landing in the pool.rs:414 branch. Any mandatory tasks then in the queue (this one and any others pushed by other threads) run synchronously inside `spawn_task` on that worker thread, blocking it for the duration of the flush instead of offloading it.
- `change`: In the drain loop at pool.rs:419-422, call `task.task.shutdown()` (matching line 396) instead of `task.shutdown_or_run_if_mandatory()`, or if guaranteeing mandatory tasks run here is intentional, run the drain from a spawned helper thread rather than the caller's own thread.
- `priority`: P2

Support (not for verifier): verified via `git show 11cf7b5d...:tokio/src/runtime/blocking/pool.rs` that this exact `shutdown_or_run_if_mandatory()` call at this site is new in commit2, not commit1. The comment at line 417 ("Drain it here so mandatory tasks still run") shows some deliberate intent to guarantee mandatory tasks execute, but doesn't address *where* they execute — I don't think the caller-thread-blocking angle was considered, but I can't be certain it wasn't a deliberate tradeoff. Flagging for the verifier to weigh.

## File manifest

| File | Status | Reason |
|---|---|---|
| `spellcheck.dic` | reviewed | Adds "RNG" (used in new sharded_queue.rs comments — legitimate) and "adaptively" (added to dict but not used anywhere in the tree — a dead dictionary entry with zero behavioral effect; pedantic nit, not reported). |
| `tokio/src/runtime/blocking/mod.rs` | reviewed | Adds `mod sharded_queue;`, correctly scoped inside the existing `cfg_rt!` gate on the parent module in `runtime/mod.rs`. No issue. |
| `tokio/src/runtime/blocking/pool.rs` | reviewed | Candidates 1 and 2 above. |
| `tokio/src/runtime/blocking/sharded_queue.rs` | reviewed | New file, read in full. The notify-counter/shutdown-flag mechanism is internally correct (increment-under-lock-then-notify, is_shutdown-checked-first pattern). The lock-avoiding `VecDeque` growth in `Shard::push` is self-correcting under contention (worst case extra allocation churn, not a correctness bug). `NUM_SHARDS=1` under `cfg(loom)` is a reasonable tractability measure. No standalone defect in this file; the defects found are in how `pool.rs` orchestrates calls into it (see Candidates 1–2). |
| `tokio/src/runtime/context.rs` | reviewed | Widens `thread_rng_n`'s cfg from `any(macros, all(sync, rt))` to `any(macros, rt)`. Necessary and correct: the new `sharded_queue.rs::next_push_index` calls `thread_rng_n` under plain `rt` (the blocking pool only requires `rt`, not `sync`). Verified the existing `sync::watch` call site (gated on `sync && (rt || macros)`) remains covered by the new, broader cfg. No issue. |
| `tokio/src/util/rand.rs` | reviewed | Widens `fastrand_n`'s cfg similarly (needed as a superset of `thread_rng_n`'s new gate and the existing `rt-multi-thread` callers, since `rt-multi-thread` implies `rt`). Noted a possible new `dead_code` warning for `fastrand_n` under a `sync`-only feature build (no `rt`, no `macros`) that didn't exist under the old cfg — but this is compiler/lint territory, out of scope per the review brief's exclusion list, so not reported as a finding. |

## Base-branch standards check

Checked `git show 43134f1e...:CONTRIBUTING.md` and `docs/contributing/*.md` — process/tooling documents only (cargo commands, clippy version, PR/review etiquette), no coding-standard or invariant rules applicable to `tokio/src/runtime/blocking/`. Confirmed via `git ls-tree` that no `README.md` or similar scoped guidance file exists under `tokio/src/runtime/blocking/` at the base commit. No standards-citation candidates arise from this PR; both findings above are plain correctness claims, not standards violations.

## Completeness note

No loom, build, or test execution was performed (per hard constraints), so Candidate 1 in particular rests on static reasoning about atomic-ordering/timing rather than an executed reproduction — this is flagged explicitly in that candidate's support field for the verifier to weigh. All six manifest files were read in full and no file was skipped.

---

### Requirements axis finder — verbatim

# Requirements-axis findings — tokio spawn_blocking sharded queue (issue #2528)

## Step 1 — Requirements restated (before reading the diff for compliance)

The issue is a short, informal contention bug report, not a spec with acceptance criteria. Restating what it actually **requires**, as distinct from what it merely describes:

- **R1 — De-contend the shared lock.** "Code that invokes `spawn_blocking`, or `block_in_place` (which internally calls `spawn_blocking`), all end up taking a shared lock" at `tokio/src/runtime/blocking/pool.rs` (pre-PR ~line 153). The requirement is: stop routing every concurrent `spawn_blocking`/`block_in_place` call through one shared lock that serializes unrelated tasks.
- **R2 — Don't let the cost scale up with load.** "The problem is exacerbated as load increases, because more calls to `spawn_blocking` causes each individual call to become more expensive." The requirement is: the per-call cost should not keep growing as concurrent blocking-spawn load increases.

Everything else in the issue text — "each call holds up an executor thread," the specific pre-PR line number, the general framing of why contention is bad — is background/motivation, not a separate acceptance criterion. The issue does not require:
- any specific mechanism (sharding is the author's choice, not something asked for),
- a particular shard count or adaptive shard count,
- preserving single-thread/low-concurrency latency,
- any specific benchmark result or number.

I did not sharpen these into anything more testable than what's written; the issue itself gives no numeric target or specific design.

## Step 2 — Sorting against the diff

**R1 — Met.**
The diff replaces the single `Mutex<Shared>` + `Condvar` that guarded the whole queue with:
- `tokio/src/runtime/blocking/sharded_queue.rs` — 16 independently-locked `Shard`s (`NUM_SHARDS = 16`, `#[cfg(not(loom))]`), each holding its own `VecDeque<Task>` behind its own `Mutex`. `push()` picks a shard via `thread_rng_n`.
- `tokio/src/runtime/blocking/pool.rs` — `Inner::shared` is now scoped to thread-bookkeeping only (`shutdown`, `shutdown_tx`, `worker_threads`, …); the hot enqueue path (`Spawner::spawn_task`) no longer takes `shared.lock()` at all except on the rare thread-spawn-ramp-up path.
- `block_in_place` (in `tokio/src/runtime/scheduler/{block_in_place.rs,multi_thread/worker.rs}` and `tokio/src/task/blocking.rs`) is untouched by the diff and still funnels through the same `Spawner`/`spawn_task` entry point, so it inherits the fix transitively — consistent with the issue's own description of `block_in_place` as calling `spawn_blocking` internally.

This is a direct, code-verifiable structural response to "all end up taking a shared lock": the single coarse lock guarding push+pop+notify+state is gone, replaced by 16 shard locks for the queue plus a separate, much smaller lock (`condvar_mutex`) purely for the notification counter.

**R2 — Cannot tell from the code (question, not a finding).**
Whether per-call cost stays flat as load increases is an empirical/runtime claim; it can't be settled by reading code, and I was told not to build/bench/loom this repo. I can, however, point to one structural fact that bears directly on it and that a benchmark alone wouldn't surface as a code question: in `Spawner::spawn_task` (`tokio/src/runtime/blocking/pool.rs`), the two branches that fire whenever the pool is busy —

```rust
} else {
    // At max threads, notify anyway in case threads are waiting
    self.inner.queue.notify_one();
}
} else {
    // There are idle threads waiting, notify one
    self.inner.queue.notify_one();
}
```

— both call `ShardedQueue::notify_one()` (`tokio/src/runtime/blocking/sharded_queue.rs:148`), which unconditionally takes the single, non-sharded `condvar_mutex` to increment `num_notify` before signalling the condvar. So under the exact scenario the issue names as worst-case — the pool saturated at `thread_cap` with no idle threads, many concurrent `spawn_blocking` callers — essentially every call still serializes on one global mutex, just with a far smaller critical section (an integer increment) than the original design (which guarded the whole `VecDeque` push/pop plus all pool state). Whether that shrunk critical section is enough to keep per-call cost flat as concurrency grows, or whether it becomes the new bottleneck at very high thread counts, is not something static reading resolves — it needs contended-load measurement (or a loom model with realistic worker counts, which is explicitly out of scope here). Who would know: whoever re-runs the PR's own benchmark methodology at concurrency well past 16 threads, or profiles `condvar_mutex` contention under a `thread_cap`-saturated workload.

**Counts: 1 met (R1), 0 not met, 1 unverifiable/question (R2).**

## Step 3 — Scope creep (behavior nobody asked for)

Checked every changed file for behavior the issue didn't call for. Found none that qualifies as creep:

- `sharded_queue.rs`'s new `ShardedQueue` abstraction has exactly one caller (`pool.rs`) but it *is* the mechanism of the fix itself, not an incidental addition — not creep.
- `NUM_SHARDS = 1` under `cfg(loom)` (commit 2) is test-infrastructure only, explicitly justified in the commit message ("keep loom's state space tractable"), not user-visible — not creep.
- The `cfg` gate widenings on `thread_rng_n` (`tokio/src/runtime/context.rs`) and `fastrand_n` (`tokio/src/util/rand.rs`) are private, crate-internal, and strictly additive (old-true combinations remain true; only a new combination — `rt` without `sync`/`rt-multi-thread` — becomes available). This is required so `sharded_queue.rs`'s call to `thread_rng_n` compiles for the current-thread runtime (feature `rt` without `sync`). No public API changed, no new config surface — not creep, just necessary plumbing.
- `spellcheck.dic` additions ("RNG" is used in the new doc comments; "adaptively" is added but — as far as I could find — never actually used in any comment in this diff, in `pool.rs`, `sharded_queue.rs`, or `mod.rs`). This looks like a leftover from an edited-away comment (possibly related to the PR body's claim about "using fewer shards when thread count is low," which I could not find implemented anywhere — `NUM_SHARDS` is a fixed constant, not adaptive). This is not behavior, so it doesn't fit the scope-creep bucket, but it's worth flagging as a stray artifact.

**No scope-creep candidates filed** (0 unrequested-behavior findings).

## Candidate

**id**: `question/sharded-queue-rs/global-notify-mutex-under-load`
**anchor**: `tokio/src/runtime/blocking/sharded_queue.rs:148`
**title**: Does the shared `condvar_mutex` in `notify_one` limit R2's goal under saturation?
**claim**: The issue requires ("the problem is exacerbated as load increases, because more calls to `spawn_blocking` causes each individual call to become more expensive") that per-call cost not scale up with concurrent load. In the diff, `Spawner::spawn_task` (`tokio/src/runtime/blocking/pool.rs`) calls `ShardedQueue::notify_one()` on essentially every invocation once the pool has no idle threads (both the "at max threads" and "idle threads waiting" branches), and `notify_one()` (`tokio/src/runtime/blocking/sharded_queue.rs:148`) unconditionally locks a single, non-sharded `condvar_mutex` to increment `num_notify`. The queue storage is sharded (16 shards) but the notification path is not.
**support**: Read `pool.rs`'s full diff and `sharded_queue.rs` in full; traced `spawn_task`'s branches and confirmed `block_in_place` shares the same entry point via unmodified call sites in `scheduler/block_in_place.rs`, `scheduler/multi_thread/worker.rs`, `task/blocking.rs`. Did not build, benchmark, or run loom (disallowed for this review), so I cannot say whether the shrunk critical section (one integer increment vs. the old full-queue-and-state lock) is sufficient to keep per-call cost flat at concurrency beyond the PR's own 16-thread benchmark, or whether it becomes a new bottleneck at higher thread counts. The PR's own benchmark table is evidence about what the author built, not proof of the property, per this axis's rules.
**trigger** (what would confirm/refute it): running the PR's own benchmark methodology at higher concurrency than 16 threads with the pool saturated at `thread_cap`, or profiling `condvar_mutex` acquisition rate under that load, would show whether per-call cost stays flat or starts climbing again.
**change**: no code change proposed — this is a question, not a finding. Change no code for this; answer it (e.g., with contention profiling data at higher thread counts) or state that this is an accepted tradeoff.
**priority**: n/a (question, not prioritized)

## Changed-file manifest

| File | Status | Reason |
|---|---|---|
| `spellcheck.dic` | reviewed | Dictionary support for new doc comments ("RNG"); the "adaptively" entry appears unused anywhere in this diff's actual comments — noted as a stray artifact, not a requirements finding since it isn't behavior. |
| `tokio/src/runtime/blocking/mod.rs` | reviewed | Registers the new `sharded_queue` private submodule; pure plumbing, no requirements implication. |
| `tokio/src/runtime/blocking/pool.rs` | reviewed | This is the file the issue names directly (pre-PR shared-lock line ~153); the diff here is the core of the fix (R1) and the two bugfixes described in commit 2. |
| `tokio/src/runtime/blocking/sharded_queue.rs` | reviewed | New file implementing the sharded queue and notification counter — the actual mechanism satisfying R1; also the site of the R2 open question above. |
| `tokio/src/runtime/context.rs` | reviewed | Necessary `cfg` widening on `thread_rng_n` so the new call site compiles under `rt` without requiring `sync`; verified additive-only against existing callers (`sync::watch`, `macros::support`), not creep. |
| `tokio/src/util/rand.rs` | reviewed | Companion `cfg` widening on `fastrand_n` for the same reason as `context.rs`; not creep. |

No files were left unreviewed.

---

### Verifier — verbatim

(Given only: candidate id/axis/anchor/fix/title/claim/trigger/priority for the 2 Code candidates. `support` withheld, per `verify.md`.)

## Verifier report

I read the full `spawn_task` (pool.rs:390-463), `Task::shutdown_or_run_if_mandatory` (pool.rs:163-168), all of `sharded_queue.rs` (`push`/`pop`/`notify_one`/`is_shutdown`/`shutdown`/`wait_for_task`), the worker loop `Inner::run` (pool.rs:510-580), the pre-PR (base commit) version of `spawn_task`/`shutdown` for comparison, the PR's own two commits (`11cf7b5d` introduces the sharded queue, `9de7950e` claims to fix "orphaned tasks on shutdown"), and the `spawn_mandatory_blocking` call site in `tokio/src/fs/file.rs` (`poll_write`, line ~756).

### Candidate A — `code/pool-rs/shutdown-race-notify-branches-skip-recheck`

**Verdict: confirmed.**

The claim is accurate on every factual point I could check:

- The three branches are exactly as described: "spawn a new thread" (pool.rs:409-424, rechecks `shared.shutdown` and drains), "at max threads, notify anyway" (453-455), and "idle threads waiting" (457-459) — the latter two call only `self.inner.queue.notify_one()` with no shutdown recheck:
  ```
  } else {
      // At max threads, notify anyway in case threads are waiting
      self.inner.queue.notify_one();
  ```
- `num_idle_threads`/`num_threads` are indeed `Ordering::Relaxed` loads with no lock held at the call sites (pool.rs:38-43, invoked at 407/409/427).
- Critically, the base-commit version of `spawn_task` held `self.inner.shared.lock()` for the *entire* function body — push, branch decision, and notify all happened under one lock that `shutdown()` also takes, making the race structurally impossible pre-PR. This diff removed that serialization when it split the queue into per-shard locks plus a separate `condvar_mutex`, and the second commit's fix (`9de7950e`, commit message: "Orphaned tasks on shutdown... Fix: when spawn_task discovers shutdown after pushing, drain the queue inline") only patched the one branch that happens to re-acquire `shared`. The other two branches were left untouched by that same commit's diff.
- I traced a concrete trigger without needing the "idle threads" branch at all: with `thread_cap = 1`, the sole worker exits via `WaitResult::Shutdown` (pool.rs:541-544), which decrements `num_idle_threads` immediately but only decrements `num_threads` later, after its own drain loop, at line 570. A concurrent `spawn_task` that passes the entry `is_shutdown()` check just before `queue.shutdown()` runs, pushes its task, then reads `num_idle_threads()==0` and `num_threads()==1==thread_cap` (stale — the exiting worker hasn't reached its `dec_num_threads()` yet) lands in the "at max threads, notify anyway" branch with no recheck at all. Because `pop()` scans all 16 shards in one non-atomic pass and the exiting worker's final drain loop (562-567) only runs the scan until it sees one clean sweep, a push landing in a shard already checked in that sweep is missed permanently.

Corrected/tightened trigger: no need for the "idle threads still waiting" case in the trigger text — the "at max threads, notify anyway" branch alone reproduces it, driven purely by `num_threads()` not yet being decremented on the exiting worker's path. Priority: keep **P1** — it requires a specific narrow-pool-plus-shutdown-race configuration, so not P0, but it silently drops tasks/orphans `JoinHandle`s and breaks the "guaranteed to run" contract of `spawn_mandatory_blocking`, which is P1-grade.

### Candidate B — `code/pool-rs/mandatory-task-runs-on-caller-thread`

**Verdict: confirmed.**

`Task::shutdown_or_run_if_mandatory` at pool.rs:163-168 is exactly as quoted:
```
fn shutdown_or_run_if_mandatory(self) {
    match self.mandatory {
        Mandatory::NonMandatory => self.task.shutdown(),
        Mandatory::Mandatory => self.task.run(),
    }
}
```
and the drain loop at pool.rs:419-422 calls this inline inside `spawn_task`, i.e. on whatever thread invoked `spawn_blocking`/`spawn_mandatory_blocking`. `spawn_mandatory_blocking` is called from `tokio/src/fs/file.rs` inside `poll_write`/`poll_write_vectored` (confirmed at the cited lines), which executes on a Tokio worker thread as part of driving a future — so `task.run()` here runs the flush's blocking `std` I/O synchronously on an async worker thread. This is a real inconsistency against the early-return path at pool.rs:392-399, which handles the identical post-shutdown-submission case by calling only `task.task.shutdown()`, never `run()`, with the comment quoted correctly by the candidate. Since this drain branch is reached by the same race window established for Candidate A (and is in fact the *easier*-to-reach of the two, since it doesn't require the thread count to be stale at cap — just the shutdown flag to flip between the entry check and the lock re-acquisition), the trigger is concrete, not speculative. Priority: keep **P2** — it stalls a worker thread for the duration of one flush during a shutdown race, not a data-loss or permanent-hang defect.

### Deduplication

Not merged. They sit at neighboring code but describe distinct defects: A is about the *absence* of recheck/drain in two of three branches (tasks dropped entirely, never run); B is about the *existing* recheck/drain (in the third branch) running mandatory work on the wrong thread (task still runs, just synchronously on the caller). Fixing A by copy-pasting the pattern from the third branch into the other two would not fix B — it would spread B's defect to all three branches. Fixing B (e.g., dispatching the drain's mandatory work to a dedicated thread instead of running inline) would not fix A's missing-recheck gap. Worth a coordination note for whoever fixes A: don't propagate B's inline-run pattern when closing A's gap.

### Summary

| id | verdict | priority |
|---|---|---|
| code/pool-rs/shutdown-race-notify-branches-skip-recheck | confirmed | P1 (unchanged) |
| code/pool-rs/mandatory-task-runs-on-caller-thread | confirmed | P2 (unchanged) |

Merge list: none.
Counts: confirmed 2, plausible 0, refuted 0.

One thing outside my mandate to rule on but worth flagging in one line: `WaitResult::Timeout` (pool.rs:545-557) exits a worker without draining or checking whether it's the last thread and tasks are pending in its shard — a related but separate potential lost-task path the finders didn't raise.

---

### Orchestrator's integrated assessment

Independently re-verified (outside the sub-agents) before treating the two confirmed Code candidates as publishable:

- `git diff 43134f1e5784993eb4fb3863933d74ac9e28f598...9de7950e59f8acea412600c2102ab592c419483a --unified=0` for `pool.rs` shows the whole `Spawner::spawn_task` region (lines ~390–462) is diff-touched (hunks `@@ -394,3 +391,2@@` through `@@ -444,8 +458,2@@`).
- Line 459 in the head tree is exactly `self.inner.queue.notify_one();` inside the "idle threads waiting" branch (Candidate A's anchor).
- Lines 403–404 are exactly `self.inner.queue.push(task); self.inner.metrics.inc_queue_depth();` (Candidate A's fix site).
- Line 421 is exactly `task.shutdown_or_run_if_mandatory();` inside the shutdown-race drain (Candidate B's anchor).
- `tokio/src/runtime/blocking/sharded_queue.rs` is a wholly new file (added in this diff), so any line in it, including line 148 (`pub(super) fn notify_one`), is a valid diff anchor for the Requirements question.

All three anchors validate. Requirements axis: R1 (met) has no candidate to publish; R2 is carried as the one open question. No scope-creep candidates. Axis classifications: **Code = Findings** (1 must-fix, 1 consider); **Requirements = Waiting for information** (1 of 2 requirements met and code-verifiable, 1 genuinely cannot be settled by static review — this is a deliberate call short of `Passed`, since one requirement's compliance is still open, not "verified true"). Status ladder (`publishing.md`): an unsettled `must-fix` (Candidate A, P1) is present, so status is **Changes Requested** regardless of the open question — the ladder stops at step 1 and never reaches the "any open question" branch. Posting identity `kamui` has no established gating authorization in this packet, so the event is `COMMENT` with the status stated in words: **Changes Requested (advisory)**.

## Would-be published review

Per `references/publishing.md`: one `gh api` call, `commit_id` = full head SHA, `event: COMMENT` (no gating authorization on record for `kamui`), body + both line comments submitted together.

```sh
gh api --method POST repos/tokio-rs/tokio/pulls/7757/reviews --input - <<'JSON'
{
  "commit_id": "9de7950e59f8acea412600c2102ab592c419483a",
  "event": "COMMENT",
  "body": "**Changes Requested (advisory)** — 1 blocking finding, 1 optional, 1 open question.\n\nCode: Findings — 1 blocking, 1 optional. Requirements: Waiting for information — 1 of 2 requirements met and verified from the code; 1 (per-call cost under load) cannot be settled by static review.\nReviewed `9de7950` against `master` (merge-base `43134f1`). Coverage: complete (6/6 files).\n\nThis replaces the blocking pool's single coarse mutex with a 16-shard queue, a proportionate response to the linear contention issue #2528 describes, and the two bugs the initial split introduced (lost wakeups, orphaned tasks on shutdown) are genuinely fixed within the scope commit 2 claims for them. But that same fix left a gap of its own: two of the three post-push branches in `spawn_task` never re-check shutdown after pushing, relying on unlocked `Relaxed` reads that were safe under the old single-mutex design but are not under this one, and a neighboring branch runs mandatory blocking work on the caller's own thread instead of the pool. Whether the design's one remaining serialization point — a single non-sharded mutex on the notification path — keeps per-call cost flat at concurrency past what the PR measured is the open question below.\n\n### Code\n- [P1] [must-fix] `spawn_task`'s shutdown recheck misses 2 of 3 post-push branches — `tokio/src/runtime/blocking/pool.rs:459`\n- [P2] [consider] Shutdown-race drain runs mandatory blocking tasks on the caller's thread — `tokio/src/runtime/blocking/pool.rs:421`\n\n### Requirements\nNo findings. R1 (de-contend the shared lock) met. R2 (cost should not scale with load) — see open question.\n\nCounts: Code 2 (1 must-fix, 1 consider). Requirements 0 findings, 1 question.\n\n## Open questions\n\n**[Question] Does the single `condvar_mutex` in `ShardedQueue::notify_one` limit the issue's \"cost shouldn't scale with load\" goal?**\n\nThe queue storage in `sharded_queue.rs` is sharded across 16 locks, but the notification path is not: `Spawner::spawn_task` calls `self.inner.queue.notify_one()` on essentially every invocation once the pool has no idle threads, and `notify_one()` (`tokio/src/runtime/blocking/sharded_queue.rs:148`) unconditionally locks one shared, non-sharded `condvar_mutex` to increment `num_notify`. Issue #2528 asked that per-call cost not keep growing as concurrent `spawn_blocking` load increases; whether the shrunk critical section (one integer increment vs. the old full-queue-and-state lock) is enough to keep that flat past the PR's own 16-thread benchmark, or becomes a new bottleneck at higher concurrency, is a runtime/load question static reading and this review's no-build/no-bench constraints cannot settle.\n\n**Change no code for this.** Answer it with contention profiling or the PR's own benchmark methodology run at concurrency higher than 16 threads with the pool saturated — or state this is an accepted tradeoff.\n\n<!-- finding id=question/sharded-queue-rs/global-notify-mutex-under-load action=question head=9de7950 -->\n\n<!-- review-run head=9de7950 base-ref=master base-sha=43134f1 merge-base=43134f1 issues=tokio-rs/tokio#2528 coverage=complete -->",
  "comments": [
    {
      "path": "tokio/src/runtime/blocking/pool.rs",
      "line": 459,
      "side": "RIGHT",
      "body": "**[Code] [must-fix] [P1] `spawn_task`'s shutdown recheck misses 2 of 3 post-push branches**\n\n`tokio/src/runtime/blocking/pool.rs:459` — after pushing to the sharded queue, `spawn_task` recognizes shutdown only in the \"spawn a new thread\" branch (which rechecks `shared.shutdown` and drains). The \"at max threads\" (pool.rs:454) and \"idle threads waiting\" (pool.rs:458-459) branches call only `self.inner.queue.notify_one()`, with no recheck. `num_idle_threads()`/`num_threads()` are `Ordering::Relaxed` loads taken without a lock — unlike the pre-PR single-mutex design where the equivalent state was always read under `shared`. When shutdown flips between the push and this read, `notify_one()` reaches no listener and the task is silently orphaned.\n\n**Triggers when**: a pool with a small `max_blocking_threads` (e.g. 1) shuts down at the same instant a concurrent `spawn_blocking`/`spawn_mandatory_blocking` call pushes a task and reads a stale `num_threads()` before the exiting worker has decremented it (the worker decrements `num_idle_threads` immediately on exit but `num_threads` only after its own drain loop) — the task and its `JoinHandle` are orphaned with no worker left to drain that shard; if mandatory, the mandatory work never runs.\n\n**Change**: recheck `self.inner.queue.is_shutdown()` unconditionally right after the push at `tokio/src/runtime/blocking/pool.rs:403-404`, before branching on idle/thread-cap state, and drain there if true — rather than only inside the \"spawn a new thread\" branch.\n\n<!-- finding id=code/pool-rs/shutdown-race-notify-branches-skip-recheck axis=code action=must-fix priority=P1 fix=tokio/src/runtime/blocking/pool.rs:403 head=9de7950 -->"
    },
    {
      "path": "tokio/src/runtime/blocking/pool.rs",
      "line": 421,
      "side": "RIGHT",
      "body": "**[Code] [consider] [P2] Shutdown-race drain runs mandatory blocking tasks on the caller's thread**\n\n`tokio/src/runtime/blocking/pool.rs:421` — when the recheck at `pool.rs:414` finds `shared.shutdown` true, the drain loop calls `task.shutdown_or_run_if_mandatory()` inline, on whatever thread called `spawn_blocking`/`spawn_mandatory_blocking` — not a dedicated blocking-pool thread. `Task::shutdown_or_run_if_mandatory` (`pool.rs:163-166`) runs the mandatory task's closure synchronously (`self.task.run()`) in that case. This is inconsistent with the earlier, functionally identical race handled at `pool.rs:392-399`, which shuts the task down without ever running it, commented \"it's fine to shutdown this task (even if mandatory) because it was scheduled after the shutdown of the runtime began.\"\n\n**Triggers when**: runtime shutdown races with a `spawn_mandatory_blocking` call (e.g. `tokio/src/fs/file.rs`'s flush-on-drop path) issued from a Tokio worker thread and lands in the `pool.rs:414` branch — the mandatory task then runs synchronously on that worker thread instead of being offloaded, blocking it for the duration.\n\n**Change**: in the drain loop at `pool.rs:419-422`, either shut the task down (matching the earlier branch's handling) instead of running it inline, or run the drain from a spawned helper thread rather than the caller's own thread — whichever behavior is intended for mandatory work racing shutdown.\n\nClosing this without action is a correct response.\n\n<!-- finding id=code/pool-rs/mandatory-task-runs-on-caller-thread axis=code action=consider priority=P2 head=9de7950 -->"
    }
  ]
}
JSON
```

Per `publishing.md`, the second phase (`PUT .../reviews/<review_id>` to fold in the created comment URLs) does not apply here since no real submission occurred — the `file:line` index in the body above stands on its own, which is the documented fallback when the link-patch phase is unavailable.

## Notes on the run

- **Judgment call — the Requirements "cannot tell from the code" item bypassed the verifier.** `requirements-axis.md` Step 2 says items in this bucket "become questions, not findings" — a disposition reached at the finder itself, not something phrased as a claim about a code defect (`confirmed`/`plausible`/`refuted` presupposes something the code either does or doesn't do; "does per-call cost scale with load at 64 threads" is not answerable by reading code regardless of verifier effort). I therefore did not send it to the verifier and instead treated it as already resolved into a question, publishing it directly. This reading is consistent with `SKILL.md`'s "Finders that return no candidates... make this step unnecessary" language (verification exists to adjudicate defect claims) but the skill's text does not explicitly carve this bucket out of verification, so a stricter reading would have sent all 3 candidates to the verifier. Flagging this as the one place I deviated from a literal, mechanical reading of "give the verifier every candidate."
- **The verifier confirmed both candidates outright** — no `plausible` verdicts this run, so (as in the skill's own first documented run against `shortlist#65`) the question-routing-from-`plausible` path remains untested by this run too; the only question published here came from the Requirements "cannot tell" bucket, not from a downgraded Code/Requirements candidate.
- **Base-branch standards check came back empty.** No `CLAUDE.md`/`AGENTS.md` exist in this repository at any point; `CONTRIBUTING.md` and `docs/contributing/*.md` are entirely about human PR/review process (cargo invocations, clippy pinning, community etiquette), not code standards. The Code finder correctly did not manufacture a standards citation to justify either finding — both are argued as plain correctness claims, which is the right outcome per `code-axis.md`'s explicit "do not manufacture findings because a standards file exists" instruction.
- **The packet's own framing ("verify commit 2's fixes are actually fixed, look for anything neither commit's own review caught") is exactly what surfaced Candidate A.** Commit 2's stated fix ("when spawn_task discovers shutdown after pushing, drain the queue inline") is real and correct for the one branch it touches — but both finder and verifier independently established that fix was applied to only 1 of 3 structurally identical branches that needed it. This is the kind of thing a human diff review of "does commit 2 fix bug X" (yes) can miss if it doesn't also ask "does this fix generalize to every place the same precondition applies" (no).
- **Requirements axis classification ("Waiting for information" rather than "Passed") is a second judgment call.** `publishing.md`'s axis vocabulary is `Passed`/`Findings`/`Not applicable`/`Waiting for information`, and doesn't map cleanly onto "1 of 2 requirements met, 1 unverifiable, 0 not-met, 0 creep." I chose `Waiting for information` because R2's status is not resolved as true, only as unfalsifiable-by-code; `Passed` would overstate that R2 was checked and found compliant, which understates the open question's weight. Since the overall status is dominated by the Code axis's unsettled `must-fix` regardless, this classification only affects the summary's precision, not the derived status.
- **Anchors were independently re-derived and checked against the live file**, not taken on the sub-agents' word — all three (`pool.rs:459`, `pool.rs:403-404`, `pool.rs:421`) matched exactly, and the question's anchor (`sharded_queue.rs:148`) is valid because the whole file is new in this diff. No anchor needed to fall back down the ladder to file- or body-level attachment.
- **Nothing was suppressed.** The two Code findings and one question above are everything either finder raised and the verifier did not refute; no candidate was dropped for being inconvenient, and no filler finding was added to look thorough. The verifier's one-line aside about `WaitResult::Timeout` (a related but separate potential lost-task path neither finder raised) was correctly kept out of the verdict list per its own brief ("do not smuggle it in as a verdict") and is reported here only as color, not as a finding — it was not added to the published payload.
- **Publication was genuinely not attempted** — no `gh` call was made against `tokio-rs/tokio` at any point; the JSON payload above is the literal input that `references/publishing.md` specifies, constructed but never sent, consistent with the run's mandatory conditions.
