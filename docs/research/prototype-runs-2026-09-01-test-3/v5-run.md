# v5 run — `code-review-publish-5` against `tokio-rs/tokio#7757`

**2026-09-01.** Data only. Not published to the PR.

## Metadata

| | |
| --- | --- |
| Skill | `code-review-publish-5` (PR #17) |
| Architecture | One integrated primary reviewer (full merge-base diff + private requirement ledger + falsification) followed by exactly one batched, fresh-context verifier for the single candidate that reached `must-fix`, per the skill's consequence-triggered rule. No fan-out of separate standards/spec/reviewer agents — matches the skill's "frequent path" design. |
| Agents spawned | 1 — the mandatory verifier (`references/verifier.md`), run via `Agent` tool with `isolation: worktree` and no inherited conversation, given only the candidate's `claim`/`trigger`/`impact`/evidence citations (no primary-reviewer `support` narrative or conclusion), for the one candidate proposed as `must-fix` that also falls under "data loss or corruption" / "externally observable compatibility break". |
| Total sub-agent tokens | 54,438 (reported by the verifier sub-agent's usage block: 11 tool uses, ~227s duration) |
| Tool uses (self-reported) | ~46 total: ~10 Read, ~34 Bash (git show/diff/log, grep, sed, wc -l, one Python invocation to run the fingerprint script), 1 Agent (verifier), 1 Write (this file). Approximate — no automatic instrumentation, counted by hand from the transcript. |
| Wall clock (self-measured) | 2026-09-01 18:03:43 UTC start → 2026-09-01 18:22:38 UTC last check before writing this file (~19 minutes of inspection/verification; a few more minutes to compose this report) |
| Candidates raised | 6 considered during falsification; 1 admitted (see next row for survivors) |
| Candidates surviving falsification | 1 (`runtime-blocking/spawn-task-shutdown-race`, P1/must-fix). 5 others were traced and actively disproven or found to lack a qualifying consequence during primary falsification (see "Candidate disposition ledger" below) and never became formal render-eligible candidates. |
| Verifier verdicts | 1 verifier run, 1 candidate submitted, verdict `confirmed` (with two accepted corrections tightening `trigger`/`impact`, no change to `priority`/`action`/`anchor`) |
| `context` fingerprint | `b5721a83a77671a31e27868f99928c9a480a5adc4aaaf343ca11353f557ce8af` (computed by `scripts/context_fingerprint.py` from `pr.title`/`pr.body` verbatim from the packet, `issues=[tokio-rs/tokio#2528]` verbatim from the packet, `specs=[]`, `guidance=[]` — no repository-rule file materially supported any finding, so none was included) |
| Findings for publication | **1** (P1, must-fix) |
| Questions | 0 |
| Coverage | Complete — 6/6 changed files reviewed (none ignored, none unreviewed); no caveat needed in the body |
| Derived status | **Changes Requested (advisory)** |

## Full reviewer report — verbatim

### Run identity

| | |
| --- | --- |
| Repository | `tokio-rs/tokio` (local clone `/tmp/tokio-review/run-v5`, offline mirror remote) |
| Pull request | #7757 — "rt: improve spawn_blocking scalability with sharded queue" |
| Head | `9de7950e59f8acea412600c2102ab592c419483a` (branch `review-head`) |
| Base ref / base SHA / merge-base | `master` / `43134f1e5784993eb4fb3863933d74ac9e28f598` (identical — `master` is pinned to the merge-base) |
| Draft/closed state | Merged. Explicit invocation for this research run permits reviewing a merged/closed target per `SKILL.md` §1; status below is derived as it would be for an open PR. |
| Originating issue | #2528 "Heavy contention on blocking", resolved via the PR body's closing reference — highest-priority resolution order per `SKILL.md` §1 |
| `docs/agents/issue-tracker.md` (base branch) | Not present — confirmed via `git show master:docs/agents/issue-tracker.md` (fatal: path does not exist). No special posting-identity/resolution instructions apply beyond the skill's own defaults. |
| Posting identity | `kamui` — no prior threads on this PR anywhere in its history (confirmed against the packet's prior-review-state section); this is an ordinary first review, `COMMENT` event, no gating authorization |

### Requirement ledger (private during review; disclosed here per the run's reporting requirement)

| Requirement / non-goal | Source | Disposition | Evidence |
| --- | --- | --- | --- |
| Reduce heavy lock contention on the blocking pool's shared task queue | Issue #2528 (explicit problem statement) | **Met** | The single `Mutex<VecDeque<Task>>` guarding the whole queue is replaced by `ShardedQueue` with 16 independently-locked shards (`tokio/src/runtime/blocking/sharded_queue.rs:29-38`); push contention is distributed across shards by `next_push_index`. This is a structural, verifiable fix for the named mechanism (a single lock serializing all `spawn_blocking` callers), independent of whether the PR's specific benchmark numbers can be reproduced (they were not re-run — no benchmarking permitted under this run's conditions, and the ledger disposition does not depend on them). |
| Benchmark claims in the PR body (13.3ms→17.8ms at 1 thread, up to −91% at 16 threads) | PR body | **Not-verifiable** | Builds/benchmarks are forbidden under this run's conditions. The claimed 1-thread regression is disclosed and explained (sharding overhead) rather than hidden, so it does not read as an undisclosed regression; nothing in the code contradicts the plausibility of the claimed improvement at higher concurrency. |
| No explicit non-goals or acceptance criteria beyond "reduce contention" | Issue #2528 | N/A | The issue is a short problem report with no bullet list of acceptance criteria, invariants, or explicitly out-of-scope items. |
| Preserve existing shutdown/mandatory-task guarantees (`spawn_mandatory_blocking` "guaranteed to run unless shutdown already in progress", implicit invariant of an executor primitive, not stated by the issue) | Repository behavior contract (doc comment at `pool.rs`, pre-existing) | **Partial** — see finding below | The contention fix does not by itself touch this guarantee, but the locking refactor needed to achieve the sharding removes an atomicity property the old code relied on for this guarantee in two of three code paths. |

No path-scoped or root repository instruction file (e.g. `CONTRIBUTING.md`) was cited as materially supporting any admitted finding, so `guidance` is empty in the `context` fingerprint input.

### Candidate disposition ledger (private falsification record, disclosed for this research run)

| # | Candidate | Falsification outcome | Disposition |
| - | --- | --- | --- |
| 1 | `spawn_task`'s two `notify_one()`-only branches (`pool.rs:453-460`) omit the shutdown recheck that the sibling spawn-new-thread branch (`pool.rs:411-424`) performs, reopening the "orphaned task on shutdown" bug class that commit 2 only partially fixed | **Survived** primary falsification: traced against pre-PR single-lock code (`git show master:.../pool.rs`) to confirm "introduced here"; traced the worker exit sequence (`num_idle_threads` decremented before the drain sweep, `num_threads` decremented after) to construct a concrete interleaving; checked the two closest pre-existing loom tests and found neither actually models this exact interleaving (one races on the same thread with program-order sequencing, the other reaches only the already-protected branch because it starts from zero threads) | Rendered as `must-fix`, sent to mandatory verifier, `confirmed` |
| 2 | The same "idle==0 && under-cap" branch's own inner double-check of `thread_cap` (two concurrent `spawn_task` calls both see room to spawn, race for the lock, second recheck fails) | **Falsified**: whenever `num_idle_threads()==0`, at least one worker is already busy-looping or about to be, and that worker's BUSY-loop `pop()` scans *all* shards before it can go idle, so the task is picked up on that worker's next iteration without needing a notification. No permanent loss. | Dropped — no consequence |
| 3 | `Shard::push`'s manual grow-outside-lock retry loop (`sharded_queue.rs:48-81`) is unusual/over-engineered versus plain `VecDeque::push_back` | **Falsified as a defect** (traced the retry loop for double-free/lost-item bugs — none found; worst case under heavy concurrent growth is extra retries, not incorrectness). Considered as a maintainability `consider` but dropped: no demonstrated reader/maintenance consequence beyond subjective unfamiliarity, and Tokio's scheduler code elsewhere uses comparably low-level custom structures, so it is not clearly disproportionate for this repository. | Dropped — fails rubric gate 4 (no demonstrated consequence) |
| 4 | Widened `#[cfg(...)]` gates on `thread_rng_n` (`context.rs:124`) and `fastrand_n` (`rand.rs:71`) might under- or over-gate, breaking some feature combination | **Falsified as a defect, confirmed necessary**: `tokio/src/runtime/blocking` is compiled only under `#[cfg(feature = "rt")]` (`cfg_rt!` macro, `runtime/mod.rs:554-560`); the new `sharded_queue.rs` calls `thread_rng_n` unconditionally under that gate. `Cargo.toml` shows `rt = []` does *not* imply `sync`, so the pre-PR cfg (`macros` or `sync`+`rt`) would have failed to compile `--features rt` alone once the new file was added — the widening is a required companion fix, not a regression. Cross-checked all other callers (`sync::watch.rs` via `BigNotify`, `scheduler/multi_thread/worker.rs`, `macros/select.rs`) and found no caller whose own gate is now broader than the new `thread_rng_n`/`fastrand_n` gate. | Dropped — verified correct, not a defect |
| 5 | Sharding removes the old queue's single global FIFO ordering across all blocking tasks | Checked for a documented ordering contract for `spawn_blocking`/`block_in_place` (doc comments, `handle.rs`) — none found; the issue does not mention ordering; FIFO was an implementation detail of the old `VecDeque`, never a stated guarantee. | Dropped — not a violated requirement or non-goal (rubric's issue-fit section) |
| 6 | `cfg(loom)` forcing `NUM_SHARDS=1` might hide multi-shard-specific bugs from the loom suite | Confirmed the confirmed finding above (candidate 1) is shard-count-independent (the missing recheck is about lock/flag ordering, not shard selection — `pop()` scans all shards regardless of count), so this doesn't change the verdict on any admitted finding; noted only as evidence context, not raised standalone. | Folded into candidate 1's evidence, not a separate finding |

### Coverage

| File | Status | Notes |
| --- | --- | --- |
| `spellcheck.dic` | Reviewed | Two words added (`adaptively`, `RNG`), header count bumped `314→316` — arithmetic consistent, no issue |
| `tokio/src/runtime/blocking/mod.rs` | Reviewed | Adds `mod sharded_queue;` only |
| `tokio/src/runtime/blocking/pool.rs` | Reviewed | Full refactor read line-by-line against pre-PR (`git show master:...`) version; see finding |
| `tokio/src/runtime/blocking/sharded_queue.rs` | Reviewed | New file, read in full; shard push/pop/notify/wait/shutdown mechanics traced |
| `tokio/src/runtime/context.rs` | Reviewed | `cfg` widening on `thread_rng_n`, verified necessary and correct (candidate 4 above) |
| `tokio/src/util/rand.rs` | Reviewed | `cfg` widening on `fastrand_n`, verified necessary and correct (candidate 4 above) |

Risk checks (rubric "Complete inspection" list), evidence-backed outcomes:

- **Authorization/sessions/tokens/public exposure** — not applicable to this diff (no such surface touched).
- **Secrets, cryptography, logging, sensitive data** — not applicable.
- **Path normalization, file serving, traversal, symlinks** — not applicable.
- **Migrations, destructive operations, rollback, compatibility** — no data migration; checked the shutdown/rollback path of the blocking pool specifically → led to the one admitted finding.
- **Retries, idempotency, partial failure, stale state, concurrency** — this is the core of the change; traced push/pop/notify/shutdown interleavings against the pre-PR single-mutex design → one confirmed finding (shutdown race in two of three `spawn_task` branches); one other candidate (the inner double-check race) traced and falsified.
- **External contracts, dependency upgrades, serialization, version skew** — checked the `cfg` feature-gate widening on `thread_rng_n`/`fastrand_n` against `Cargo.toml`'s feature graph and every caller → verified correct/necessary, not a regression.

Coverage is **complete**: every changed file reviewed, no ignored/unreviewed files, every applicable risk-directed check has an evidence-backed outcome, and the one mandatory verification completed with a definite verdict (not incomplete/failed).

### Falsification note on `master` and the "already-fixed" bugs

Per the packet's history note, commit 2 (`9de7950e`, already included in the reviewed head) fixed two bugs from commit 1: lost condvar wakeups and orphaned tasks on shutdown via the spawn-new-thread path. Both fixes were re-traced against the current code and confirmed present and functioning:

- Lost-wakeup fix: `ShardedQueue::notify_one`/`wait_for_task` (`sharded_queue.rs:148-153,192-227`) use a notification counter under `condvar_mutex`, mirroring the original single-mutex `num_notify` pattern — confirmed no wakeup can be lost between a worker's check and its `condvar.wait_timeout`.
- Orphaned-task fix (spawn-new-thread branch only): `pool.rs:411-424` explicitly rechecks `shared.shutdown` after acquiring the lock and drains inline if shutdown raced in — confirmed present and correctly scoped to that branch.

The review then asked, per the packet's explicit instruction to "look for anything neither commit's own review caught": does the *same* fix need to exist in the other two branches of `spawn_task`? It does — see the admitted finding.

### Independent verifier's report — verbatim

The verifier was run as a fresh, isolated `general-purpose` sub-agent (worktree isolation, no inherited conversation), given the candidate's `id`, `kind`, `priority`, `action`, `anchor`, `fix`, `title`, `claim`, `trigger`, `impact`, `change`, and raw evidence citations only — explicitly withholding the primary reviewer's `support`/confidence/reasoning, per `references/verifier.md`.

```
verdict: confirmed
justification: |
  I verified the claim independently against the head tree and refuted no part of it.

  (1) Control flow confirmed. pool.rs:390-463: `spawn_task` does its shutdown check
  lock-free at line 392 (`self.inner.queue.is_shutdown()`), pushes into a per-shard
  mutex at line 403, and only *one* of the three post-push branches re-acquires
  `self.inner.shared.lock()` (line 411) and rechecks `shared.shutdown` (line 414) with
  an inline drain (419-423). The other two branches — line 453-456 (`num_idle == 0`
  and `num_threads() >= thread_cap`) and 457-460 (`num_idle > 0`) — call
  `self.inner.queue.notify_one()` and return `Ok(())` with no shutdown recheck and no
  fallback drain. `notify_one` (sharded_queue.rs:148-153) only bumps a counter under
  `condvar_mutex` and signals; it does not consult the shutdown flag, so it is a no-op
  for correctness once all workers have left `wait_for_task`.

  (2) The race is reachable with a plain sequentially-consistent interleaving; no
  exotic memory-model behavior is needed. With `thread_cap == 1` and one idle worker:
    - T1 (spawner) evaluates `is_shutdown()` at pool.rs:392 → false, then stalls.
    - T2 runs `BlockingPool::shutdown` (pool.rs:241-276): sets `shared.shutdown`, calls
      `queue.shutdown()` (sharded_queue.rs:170-179), then blocks in `shutdown_rx.wait`.
    - Worker wakes with `WaitResult::Shutdown` (pool.rs:541), decrements
      `num_idle_threads` at line 542 *before* the drain, breaks, and runs its final
      drain sweep at pool.rs:562-567 over all shards — finds nothing, because T1 has
      not pushed yet. It is now stalled just before `dec_num_threads()` at line 570.
    - T1 resumes: `queue.push(task)` (line 403). Reads `num_idle_threads()` → 0 (the
      worker already decremented at 542). Reads `num_threads()` → still 1 (line 570 not
      yet executed), so `1 < 1` is false → falls into the *unprotected* branch at
      453-456, calls `notify_one()`, returns `Ok(())`.
    - Worker then decrements `num_threads`, drops its `shutdown_tx`, and exits.
  The task is left in the shard's `VecDeque` with no live consumer. The decisive window
  is precisely between the worker finishing its drain scan (line 566) and
  `dec_num_threads()` (line 570) — during which `num_threads()` still reads `thread_cap`.
  (The 457-460 branch additionally needs a stale relaxed read of `num_idle_threads`,
  since a still-idle worker would be woken and would drain — loom-reachable, but the
  453-456 branch does not need that, so the finding stands on its own.)

  (3) No recovery path exists. `BlockingPool::shutdown` (241-276) never drains the queue
  itself. Any later `spawn_task` returns early at line 399 without draining. The only
  three `queue.pop` sites are pool.rs:419 (the protected branch), 522 and 563 (worker
  loops), all of which are gone. When the last `Handle` drops, the `Task` is dropped via
  `UnownedTask::drop` (task/mod.rs:567-575), which only decrements refcounts — it never
  transitions the task to complete, so the `JoinHandle` waker is never signaled. Awaiting
  the handle hangs permanently, and for `spawn_mandatory_blocking` (documented at
  pool.rs:192-195 as "guaranteed to run unless a shutdown is already taking place") a
  `Some(handle)` return that never runs breaks the contract.

  (4) Introduced by this PR. `git show master:tokio/src/runtime/blocking/pool.rs`
  shows `spawn_task` acquiring `self.inner.shared.lock()` as its first statement and
  holding it for the entire body — the shutdown check, `shared.queue.push_back(task)`,
  and the `num_idle_threads`/`num_threads` decision were all atomic under it. Pre-PR the
  queue lived *inside* `Shared`, and worker `dec_num_threads()` also executed while
  holding that same lock (master run(): `self.metrics.dec_num_threads()` precedes
  `drop(shared)`), and every busy worker re-acquired the lock and re-ran its
  `shared.queue.pop_front()` loop before it could go idle or exit. So observing
  `num_idle == 0 && num_threads == cap` under the lock guaranteed `cap` live busy
  threads that would each re-scan the queue. The interleaving above was structurally
  impossible before this PR.

  (5) `shutdown_rx.wait` gives no protection. blocking/shutdown.rs: the channel is a
  `oneshot` whose `Sender` is cloned only into worker threads; `wait` returns when the
  last worker drops its clone. It is purely a refcount/thread-exit rendezvous and
  establishes no happens-before with an in-flight `spawn_task` on an unrelated thread.

  (6) Not covered by the existing loom tests, and not documented as intentional.
  `git diff master review-head -- tokio/src/runtime/tests/loom_blocking.rs` is empty, so
  both named tests are unchanged. `spawn_blocking_then_shutdown` does force the second
  spawn through 453-456/457-460, but `let jh3 = rt_hdl.spawn_blocking(...)` and
  `drop(rt)` are sequential on the *same* thread — program order gives `spawn_task`
  happens-before shutdown, so there is no race for loom to explore; the test passes
  legitimately. `spawn_mandatory_blocking_should_run_even_when_shutting_down_from_other_thread`
  does race a concurrent `drop(rt)`, but on a fresh 0-thread runtime, so
  `num_idle == 0 && num_threads() == 0 < thread_cap` routes it into the *protected*
  branch at 409-452 — it covers the already-fixed bug, not this one. (Both tests would
  detect an orphan if reached — `loom::future::block_on` / `rx.recv()` would block and
  loom would report a deadlock — but neither model reaches the interleaving. Note also
  `NUM_SHARDS = 1` under loom, sharded_queue.rs:31-32.) Commit 9de7950e's message frames
  "Orphaned tasks on shutdown" as a bug being fixed, and the code comment at
  pool.rs:415-417 frames the recheck as necessary; nothing in the commits or comments
  presents the remaining two branches as an accepted tradeoff. It is an incomplete fix,
  not a deliberate one.
decisive_citations:
  - tokio/src/runtime/blocking/pool.rs:392 — shutdown check is now lock-free, decoupled from the push.
  - tokio/src/runtime/blocking/pool.rs:403 — push goes into a per-shard mutex unrelated to `shared`/`condvar_mutex`.
  - tokio/src/runtime/blocking/pool.rs:411-424 — the one branch that rechecks `shared.shutdown` and drains inline ("Shutdown raced with our push").
  - tokio/src/runtime/blocking/pool.rs:453-456 — `num_threads() >= thread_cap` branch: bare `notify_one()`, no recheck, no drain.
  - tokio/src/runtime/blocking/pool.rs:457-460 — `num_idle > 0` branch: bare `notify_one()`, no recheck, no drain.
  - tokio/src/runtime/blocking/pool.rs:541-543 vs 562-570 — worker decrements `num_idle_threads` BEFORE its final drain sweep but `num_threads` AFTER it, creating the window in which `num_idle == 0 && num_threads == thread_cap` while no drainer remains.
  - tokio/src/runtime/blocking/pool.rs:241-276 — `BlockingPool::shutdown` never drains the queue; it only sets flags and waits.
  - tokio/src/runtime/blocking/sharded_queue.rs:148-153 — `notify_one` only bumps a counter/signals; it is a no-op once no worker is in `wait_for_task`.
  - tokio/src/runtime/blocking/sharded_queue.rs:192-227 — `wait_for_task` returns `Shutdown` on the shutdown flag; there is no post-exit consumer and no ordering primitive tying a later `push` to a worker's completed drain.
  - git show master:tokio/src/runtime/blocking/pool.rs (`fn spawn_task`) — pre-PR the whole body ran under one held `shared` lock that also guarded the queue and `dec_num_threads`, making this interleaving impossible.
  - tokio/src/runtime/blocking/shutdown.rs (`Receiver::wait`) — oneshot refcount rendezvous over worker `Sender` clones only; no happens-before with a racing `spawn_task`.
  - tokio/src/runtime/task/mod.rs:567-575 — `UnownedTask::drop` only decrements refcounts, so an orphaned task never completes its `JoinHandle`.
  - tokio/src/runtime/tests/loom_blocking.rs (`spawn_blocking_then_shutdown`) — `spawn_blocking` and `drop(rt)` are sequential on the same thread, so no spawn/shutdown race is modeled.
  - tokio/src/runtime/tests/loom_blocking.rs (`spawn_mandatory_blocking_should_run_even_when_shutting_down_from_other_thread`) — 0-thread runtime routes the racing spawn into the already-protected 409-452 branch.
corrections:
  trigger: |
    Tighten the window: the orphan does not require the last worker to have *exited*
    before the push. It requires only that every worker finished its post-`'main` drain
    sweep (pool.rs:566) before the push became visible, while at least one of them has
    not yet reached `dec_num_threads()` (pool.rs:570) — that is exactly what makes
    `num_idle_threads() == 0 && num_threads() == thread_cap` hold and routes the caller
    into pool.rs:453-456. Reaching pool.rs:457-460 additionally needs a stale relaxed
    read of `num_idle_threads`, since a genuinely still-idle worker would wake and drain;
    the 453-456 path needs no such stale read.
  impact: |
    Same correction as trigger: "has already ... exited BEFORE the racing task's push"
    should read "has already completed its final drain sweep before the push, with
    `num_threads` not yet decremented". Also worth stating that practical reachability
    requires the pool to be at `thread_cap` (default 512, but 1 in `max_blocking_threads(1)`
    configurations, which the repo's own loom test uses), and that the orphaned task is
    never cleaned up: dropping it only decrements refcounts, so the `JoinHandle` hangs
    rather than erroring.
  priority: none
  action: none
  anchor: none
  fix: none
  change: none
duplicate_of: none
```

The primary reviewer validated both corrections against the diff (they are consistent with what was independently traced before dispatch) and adopted the tightened `trigger`/`impact` wording verbatim into the rendered finding below. `priority`, `action`, and `anchor` were left as proposed since the verifier found no basis to change them.

### Rendered finding (private record)

```yaml
id: runtime-blocking/spawn-task-shutdown-race
anchor:
  type: line
  path: tokio/src/runtime/blocking/pool.rs
  start_line: 453
  end_line: 460
  side: RIGHT
priority: P1
action: must-fix
blocking: true
kind: bug
title: Recheck shutdown before notifying in the two unguarded spawn_task branches
claim: >
  Spawner::spawn_task's "pool already at thread_cap" and "an idle worker exists"
  branches (pool.rs:453-460) call queue.notify_one() without rechecking shutdown,
  unlike the sibling spawn-new-thread branch (pool.rs:411-424); pre-PR the whole
  function was atomic under one lock, making this race structurally impossible.
trigger: >
  Every worker alive when BlockingPool::shutdown() begins finishes its final
  post-shutdown drain sweep (pool.rs:566) before a racing spawn_task's push becomes
  visible, while at least one worker has not yet reached dec_num_threads() (pool.rs:570)
  — so num_idle_threads()==0 and num_threads()==thread_cap both hold and the caller
  is routed into the unguarded pool.rs:453-456 branch (457-460 additionally needs a
  stale relaxed read of num_idle_threads).
impact: >
  The pushed task is permanently orphaned in its shard's queue with no live consumer;
  dropping it only decrements refcounts (task/mod.rs:567-575), so it never completes.
  spawn_blocking's JoinHandle hangs forever if awaited; spawn_mandatory_blocking's
  "guaranteed to run unless shutdown already in progress" contract silently breaks —
  Some(handle) is returned for a task that never runs.
evidence:
  - tokio/src/runtime/blocking/pool.rs:392,403,411-424,453-460
  - tokio/src/runtime/blocking/pool.rs:541-543 vs 562-570
  - tokio/src/runtime/blocking/sharded_queue.rs:148-153,192-227
  - git show master:tokio/src/runtime/blocking/pool.rs fn spawn_task (pre-PR single-lock atomicity)
  - tokio/src/runtime/tests/loom_blocking.rs (spawn_blocking_then_shutdown, spawn_mandatory_blocking_should_run_even_when_shutting_down_from_other_thread) — unchanged by this PR, neither models this exact interleaving
support:
  inspected:
    - full pool.rs and sharded_queue.rs (current and pre-PR via git show)
    - loom_blocking.rs existing tests and their construction
    - Cargo.toml feature graph, cfg_rt! macro, all callers of thread_rng_n/fastrand_n (separate candidate, not this one)
  checks:
    - manually traced idle/thread-count/lock interplay across old vs new code
    - confirmed loom_blocking.rs unmodified via git diff master review-head
    - confirmed no drain path exists after BlockingPool::shutdown() returns
  uncertainty: >
    Could not execute loom to directly observe the interleaving (forbidden by this
    run's conditions); relied on static trace plus an independently confirmed verifier
    pass that reached the same conclusion via its own citations.
requirement_source: none
change: >
  In both unguarded branches (pool.rs:453-456, 457-460), recheck shutdown (e.g. via
  self.inner.shared.lock() or self.inner.queue.is_shutdown()) after the push and drain
  the task with shutdown_or_run_if_mandatory() when shutdown is discovered, mirroring
  the recheck already present at pool.rs:413-424.
verification: independent-confirmed
```

## Would-be published review

Re-fetch-before-write and stale-head checks are simulated as passing (publication is disabled for this run; there is no live head to re-fetch). The payload below is exactly what phase 6 (`SKILL.md` §6) would submit as one forge-native review.

**Batch payload** (`gh api --method POST repos/tokio-rs/tokio/pulls/7757/reviews --input <payload>`):

```json
{
  "commit_id": "9de7950e59f8acea412600c2102ab592c419483a",
  "event": "COMMENT",
  "body": "**Changes Requested (advisory)** — 1 must-fix finding.\n\n**Intent:** Replace the blocking pool's single global mutex with a 16-way sharded queue to fix severe lock contention under concurrent `spawn_blocking` (issue #2528), building on this PR's own second commit, which already fixed two shutdown races (lost condvar wakeups, and orphaned tasks via the spawn-new-thread path).\n\n**Issue fit:** Met — the sharded design directly and structurally addresses the reported contention; the disclosed 1-thread overhead is a transparent, explained tradeoff, not a hidden regression.\n\n**Coverage:** Complete merge-base diff reviewed (6/6 changed files); cfg/feature-flag consistency for the widened `thread_rng_n`/`fastrand_n` gates verified against all call sites and `Cargo.toml`'s feature graph (no issue); the shutdown/concurrency risk check produced one confirmed finding, independently verified in a fresh isolated pass.\n\n**Reviewed:** `9de7950e` against merge-base `43134f1e`.\n\n## Findings\n\n- [P1] [must-fix] Recheck shutdown before notifying in the two unguarded `spawn_task` branches — anchor `tokio/src/runtime/blocking/pool.rs:453-460`\n\n<!-- review-run head=9de7950e59f8acea412600c2102ab592c419483a base-ref=master base-sha=43134f1e5784993eb4fb3863933d74ac9e28f598 merge-base=43134f1e5784993eb4fb3863933d74ac9e28f598 workflow=v5-1 context=b5721a83a77671a31e27868f99928c9a480a5adc4aaaf343ca11353f557ce8af issues=tokio-rs/tokio#2528 coverage=complete -->",
  "comments": [
    {
      "path": "tokio/src/runtime/blocking/pool.rs",
      "start_line": 453,
      "start_side": "RIGHT",
      "line": 460,
      "side": "RIGHT",
      "body": "**[P1] [must-fix] Recheck shutdown before notifying in the two unguarded `spawn_task` branches**\n\n**Triggers when:** `spawn_task` reaches its \"pool already at `thread_cap`\" or \"an idle worker exists\" branch (lines 453-460) while `BlockingPool::shutdown()` is concurrently tearing the pool down on another thread. Every worker alive at that moment can finish its final post-shutdown drain sweep and reach `dec_num_threads()` (or a still-idle worker can be read stale) before this push's task becomes visible to any drainer.\n\n**Impact:** The pushed task is permanently orphaned in its shard's queue — dropping it only decrements refcounts, it never completes. `spawn_blocking`'s `JoinHandle` hangs forever if awaited, and `spawn_mandatory_blocking`'s \"guaranteed to run unless shutdown already in progress\" contract silently breaks: `Some(handle)` is returned for a task that never runs.\n\n**Change:** In both branches (lines 453-456 and 457-460), recheck shutdown (e.g. via `self.inner.shared.lock()` or `self.inner.queue.is_shutdown()`) after the push and drain the task with `shutdown_or_run_if_mandatory()` when shutdown is discovered, mirroring the recheck already present at lines 413-424 for the sibling spawn-new-thread branch. Before this PR the whole function ran under one lock, which made this race impossible; the fine-grained locking introduced here reopens it for two of the three branches.\n\n<!-- finding id=runtime-blocking/spawn-task-shutdown-race head=9de7950e priority=P1 action=must-fix blocking=true kind=bug -->"
    }
  ]
}
```

**Semantic status:** Changes Requested (advisory) — the posting identity (`kamui`) has no separate gating authorization on this repository, so the forge event is `COMMENT` per the output contract's authorization table, with `(advisory)` appended to the semantic status written in the body.

## Notes on the run

- **The central judgment call of this run** was whether the `spawn_task` shutdown-race candidate cleared the rubric's "proven consequence" gate from static reading alone, given that builds/tests/loom execution were forbidden. My own trace constructed a concrete interleaving and confirmed (via `git show master:...`) that the old single-lock design made it structurally impossible — strong "introduced here" evidence — but I could not rule out that an existing loom regression test would have caught it in CI. Rather than resolve that uncertainty unilaterally (by either suppressing the finding or asserting confidence I didn't have), I let it survive to the skill's mandatory verifier, which is exactly the situation `code-review-publish-5`'s hybrid architecture is designed for: the verifier independently re-derived the same conclusion, went further by identifying that the two *closest* pre-existing loom tests don't actually model this exact interleaving (one is same-thread/sequential, the other starts from zero threads and only reaches the already-protected branch), and tightened the trigger/impact language. This is the one point in the run where the skill's own process materially changed the outcome versus what I'd have published on primary judgment alone.
- **Verifier trigger, precisely:** `SKILL.md` §3 triggers mandatory verification for "every surviving candidate proposed as must-fix, plus every candidate involving security or authorization, data loss or corruption, destructive migration, or an externally observable compatibility break." My one candidate qualified on *both* counts independently — it was proposed `must-fix`, and a permanently hung `JoinHandle` that silently breaks `spawn_mandatory_blocking`'s documented "guaranteed to run" contract reads as an externally observable compatibility/correctness break. `SKILL.md` also explicitly says "Artifact names such as 'contract,' `SKILL.md`, or 'public' do not trigger verification by themselves" — I did not invoke verification merely because the word "contract" appears in a doc comment; I invoked it because the candidate was independently must-fix and because I could construct a genuine observable-hang scenario, not because of the label.
- **Five other candidates were considered and fell before formal admission** (see the candidate disposition ledger above) — mostly on rubric gate 4 ("proven consequence") or because closer tracing showed the surrounding code already prevents the failure. None of them were manufactured to pad the review; they're recorded because the exercise asked for an honest account of what was actually considered, not just what survived.
- **The ADD-SP maintainer comment** in the packet's prior-review-state section ("I'd like to take some time to think about the nested locking issue... The PR proceeded to approval on the design as committed") lines up closely with the category of concern in the admitted finding, though not with its precise mechanism as traced here. Per the rubric's falsification step 5/6, this history was weighed as evidence that the concern was *raised and left unresolved* rather than *examined and deliberately accepted* — the latter would have been grounds to treat it as intentional and drop it; the former is not, so the finding stands.
- **No requirement gaps, no compatibility/security findings, and no repository-rule findings** were found elsewhere in the diff. The `cfg` feature-gate widening in `context.rs`/`rand.rs` looked, on first read, like exactly the kind of narrow "did this compile-time gate get relaxed correctly" risk the rubric calls out under "external contracts... version skew" — it turned out to be a necessary and correct companion change to the new file, not a defect, and is recorded in the coverage table as a verified-safe risk check rather than a finding.
- **Coverage caveat placement:** none needed — coverage is complete and the body says so plainly, per the output contract's instruction that a clean-coverage review states so briefly rather than adding an empty "Coverage gaps" section.
- **Things flagged but not actionable in this run:** the PR body's benchmark table could not be independently reproduced (builds/benchmarks forbidden); this is recorded in the requirement ledger as `not-verifiable` rather than as a finding, since nothing contradicts its plausibility and the disclosed 1-thread regression is transparent rather than hidden.
