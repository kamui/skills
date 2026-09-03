# v2a run — `code-review-deep-publish` against `tokio-rs/tokio#7757`

**2026-09-03.** Data only. Not published to the PR. See
[`addendum-2026-09-03.md`](addendum-2026-09-03.md) for run conditions, model verification, and the
dev-set caveat that applies to this run.

## Metadata

| | |
| --- | --- |
| Skill | `code-review-deep-publish` (research nickname **v2a**, "Panel line"; [PR #18](https://github.com/kamui/skills/pull/18), branch `t3code/prototype-code-review-publish-2a`, pinned commit `87c68a9`) |
| Includes fixes | `326ef6f` "Require paired peer-contract sweeps"; `940aa2c` "Sweep every changed contract, on both axes" (DESIGN.md §C9) |
| Architecture | 2 axis finders in parallel (Code, Requirements) → 1 mandatory fresh-context verifier |
| Model | `claude-sonnet-5` on the orchestrator and all three sub-agents, **passed explicitly on every Agent call and verified afterwards** from the harness's sub-agent transcripts |
| Agents spawned | 4 (orchestrator, Code finder, Requirements finder, verifier) |
| Sub-agent tokens | orchestrator 230,184; Code finder 126,359 (30 tool uses, 814,797 ms); Requirements finder 80,076 (18 tool uses, 350,709 ms); verifier 54,831 (17 tool uses, 318,681 ms) |
| Wall clock | ~28 min end-to-end (finders concurrent, verifier sequential after both) |
| Candidates raised | 2 — Code 1, Requirements 1 (plus 1 item routed straight to a question, which never reaches the verifier by rule) |
| Verdicts | 1 confirmed · 0 plausible · 1 refuted · 0 merged |
| Findings for publication | **1** — P2 `must-fix` |
| Questions | 1 |
| Coverage | complete (6/6 files, both finders; static only, no build/cargo/loom/miri per the packet) |
| Requirements counts | met 1 · not met 0 · cannot tell 1 |
| Derived status | **Changes Requested (advisory)** — one unsettled `must-fix`; event `COMMENT` |

## The headline result: a near miss, and a false acquittal

**v2a did not find the defect that shipped.** It found a different, adjacent one — and it explicitly
acquitted the two branches that carry the real bug.

This target's ground truth (see [`evaluation.md`](evaluation.md)) is that `spawn_task` has three
post-push branches; only the "spawn a new thread" branch got the shutdown recheck commit 2 added.
The other two — "at max threads, notify anyway" (`pool.rs:453-455`) and "idle threads waiting,
notify one" (`pool.rs:457-459`) — have no recheck and no drain. That is the defect that merged,
hung production, and was reverted six days later.

v2a's Code finder examined exactly those two branches and **acquitted both**. Its stated reasoning,
quoted from its own answer:

> the "at max threads, notify anyway" branch (`pool.rs:454-455`) and the "idle threads waiting,
> notify one" branch (`pool.rs:458-459`) are safe against a *shutdown* race specifically, because
> any worker whose counters still make it look "available" has necessarily not yet run its own
> post-loop drain, and the shard `Mutex`'s lock/unlock ordering guarantees that drain will observe
> an already-completed push (I traced this through explicitly and it holds up)

The premise is false in the interleaving that actually occurs: a worker decrements
`num_idle_threads()` **before** its final drain sweep and `dec_num_threads()` **after** it, so a
worker whose counters still make it look available *can* already have run its drain. A push landing
in that window reads `num_idle_threads() == 0 && num_threads() == thread_cap`, routes into the
unguarded "at max threads" branch, and is orphaned.

**This is a regression against its own ancestor.** The original v2 — the unpatched Panel line on
this same target — implicated *both* unguarded branches and published the finding at P1. So did v4
and v5. The only original run that got this wrong was v3, and it got it wrong the *same way*: v3
judged the "at max threads" branch "self-healing via the busy-loop's full-shard rescan since
`idle == 0` implies no thread is parked in `wait_for_task` there." v2a reproduced v3's known error
while its own lineage had previously avoided it.

### What v2a did find

The Code finder's candidate is a genuinely different stranding path: the temporary-OS-thread-error
arm at `pool.rs:437-443`, *inside* the guarded branch, which notifies nobody at all. When
`spawn_thread` fails with `WouldBlock` in the narrow window between a worker's `pop()` returning
`None` and its `inc_num_idle_threads()`, the pushed task strands for a full `keep_alive` and the
worker then exits without re-checking. The verifier **confirmed** it, kept P2 / `must-fix`, and
narrowed the trigger to the precise instruction window. No prior run on this target reported it.

So the run's single finding is real, correctly proportioned, and new — but it is not the ground
truth, and the run's derived status is right for the wrong reason.

### Why the panel architecture did not catch the acquittal

Structural, and worth recording: **an acquittal never reaches the verifier.** Under this skill's
process only candidates are verified, so the Code finder's acquittal of the two branches was
checked by nobody — not the verifier, which saw only the surviving candidate, and not the
orchestrator. The run's own report states this plainly rather than letting the confirmed finding
stand in for it:

> Whether the acquittal's reasoning actually holds against the code is therefore **not
> independently checked anywhere in this run** — it stands solely on the Code finder's own trace,
> on Sonnet 5, in a single pass.

Compare v5a on the same target, whose clean-verdict verifier exists precisely to attack a
disposition ledger — although note that mechanism only fires at *zero* survivors, so it would not
have fired here either. The gap this target exposes is that a false acquittal sitting beside a true
candidate is invisible to both architectures' verification steps.

## The finding

### F1 — `code/blocking-pool/idle-count-race-stranded-task` — must-fix / P2

- **anchor and fix** `tokio/src/runtime/blocking/pool.rs:437-443`

The `Err(ref e) if is_temporary_os_thread_error(e) ...` arm does nothing but comment; it never calls
`notify_one()`. In the base version this was safe because `spawn_task` held one `Mutex<Shared>` for
its whole body, serializing the busy→idle transition against this read. The sharded design decouples
them, so a worker that has just exhausted its `pop()` loop but not yet counted itself idle is
invisible to `num_idle_threads()`, and a `WouldBlock` spawn failure in that window strands the task
for up to `keep_alive` with no re-check on the timeout exit path.

Verifier: **confirmed**, quoting the arm and noting that `wait_for_task` is purely counter-driven
and never re-scans the shards. Priority P2 kept ("requires a specific environment … plus a narrow
race, not 'any input'"); action `must-fix` kept ("a `spawn_blocking` `JoinHandle` can go unresolved
indefinitely").

## The refuted candidate

`requirements/unrequested/shard-push-growth-optimization` (P2 `consider`) argued that `Shard::push`'s
manual growth scheme was scope creep. The verifier **refuted** it on a specific and interesting
ground: the candidate's argument rested on a quotation of issue #2528 — "Replace the single-mutex
queue… causing severe contention" — that **does not appear in the issue**. The real text describes
the symptom only. Per `verify.md`, a misquotation of cited spec text is itself grounds to refute.
The mechanism the candidate described was accurate; the licence it claimed from the issue was
fabricated.

Worth flagging for the program: this is the first recorded case of a finder inventing a quotation
and the verifier catching it on exactly that basis. It is the claim/support split doing its job.

## The question

`question/sharded-queue/condvar-mutex-residual-contention` — the Requirements finder's R2 (the
outcome requirement) landed in the "cannot tell from the code" bucket and published as a question
without reaching the verifier: `notify_one` and `wait_for_task` still funnel through one
un-sharded `condvar_mutex`, and `spawn_task` calls `notify_one()` on nearly every call once the pool
is warm. Whether that residual lock still bottlenecks at the reported concurrency is a runtime
property. C4 firing as designed.

## Mechanism checklist

- **C1 (Calibration) — mixed, and the miss is the headline.** The one confirmed finding is
  proportionate (P2 `must-fix`, verifier-corrected trigger) and the derived status is right. But the
  ground-truth defect was acquitted, not found, so this is not calibration credit on the item that
  matters. Recorded as a miss.
- **C3 (Disposition ledger) — confirmed.** 11-row Code ledger, 9-row Requirements ledger, both with
  tried-to-convict acquittals — and it is precisely the ledger discipline that makes the false
  acquittal visible in the record at all.
- **C4 (Question routing) — confirmed**, on a benchmark-dependent claim, exactly the shape predicted.
- **C5 (Observations) — confirmed.** 9 observation-shaped items across both finders and the verifier;
  3 published.
- **C9 (Changed-contract sweep) — correct negative.** Requirements found 1 contract (the RNG cfg
  gates), Code found 3 (adding the queue implementation and the new `WaitResult` enum); no stale peer
  anywhere. The two sweeps agree where they overlap.
- **Pole intact — confirmed.** Both finders ran, both on Sonnet 5; both candidates got exactly one
  verifier verdict; `support` withheld, confirmed against the verifier's own prompt.
- **C2 (no-issue rule) — not applicable**; this target has an originating issue.

## One process note worth keeping

The verifier located and read `/tmp/handoff3/tokio-issue-2528.md` — a local file this session had
staged while building the packet, not part of the clone and not referenced in its prompt — and used
it to check the disputed quotation. The outcome was correct, and no network or mutation was
involved, but the orchestrator flagged it as a judgment call a stricter reading of `verify.md`'s
"the repository" would not have allowed. Future packets should stage such files outside the paths a
sub-agent is likely to browse.

## Full run report

The orchestrator's complete report, verbatim, including both finders' ledgers and the verifier's
verdicts:

### 1. Metadata table

| Field | Value |
| --- | --- |
| Skill under test | `code-review-deep-publish`, pinned commit `87c68a9` (branch `t3code/prototype-code-review-publish-2a`, PR #18 in `kamui/skills`), nickname **v2a** ("Panel line") |
| Fixes baked in | `326ef6f` "Require paired peer-contract sweeps"; `940aa2c` "Sweep every changed contract, on both axes" |
| Target | `tokio-rs/tokio#7757`, "rt: improve spawn_blocking scalability with sharded queue" |
| Run identity | head `9de7950e59f8acea412600c2102ab592c419483a`; base ref `master`; base SHA / merge-base `43134f1e5784993eb4fb3863933d74ac9e28f598` (identical) |
| Architecture | Two parallel finder sub-agents (Code axis, Requirements axis) + one fresh-context verifier sub-agent, per `SKILL.md` step 2/3 |
| Agents spawned | 3 total: Code finder, Requirements finder (parallel), then the verifier (sequential, after both finders returned) |
| Model each sub-agent ran on | **`sonnet` (Claude Sonnet 5), explicitly passed via `model: "sonnet"` on every `Agent` call** — all three. The harness default subagent model was not used for any of the three. |
| Sub-agent type | `general-purpose` for all three (no more specific "finder"/"verifier" agent type exists in this harness); hygiene/mutation/network/build constraints were enforced entirely by prompt-level instruction, not by tool restriction — see item 8 |
| Per-sub-agent tool uses (self-reported) | Code finder: ~34 tool calls (2 `Read`, ~32 `Bash`, several chained). Requirements finder: 17 tool calls (2 `Read`, 15 `Bash`). Verifier: 17 tool calls (exact breakdown not itemized by the sub-agent). |
| Per-sub-agent tokens (self-reported) | Code finder: no exact figure observable from inside its own session; self-estimated "on the order of 40–60K input tokens," explicitly flagged as a guess, not a measurement. Requirements finder: "No token-usage introspection tool was available to me; I did not observe an exact count." Verifier: did not report a token estimate at all (only tool-call count). None of the three sub-agents had access to an authoritative token counter from inside their own context — this is a **known measurement gap**, not a zero. |
| Total tool uses (orchestrator + sub-agents) | Orchestrator (this session): ~20 `Bash`/`Read` calls for setup, reading references/packet/guidance/diff, and provenance checks, plus 3 `Agent` calls. Sub-agents: 34 + 17 + 17 = 68. Combined ≈ 88 tool calls across the whole run (orchestrator not separately itemized to single-call precision; see item 8). |
| Wall clock | Dispatch received ≈ 04:02 (file timestamp `04:02:06`). Requirements finder returned `04:16:18`. Code finder returned `04:21:43`. Verifier returned `04:28:19`. Report compiled and returned ≈ 04:30. **Total wall clock ≈ 28 minutes** end-to-end. The two finders ran concurrently (both spawned in one message before either result arrived); the verifier ran only after both finders had returned, per the skill's process. |
| Candidates raised — Code axis | 1 (`code/blocking-pool/idle-count-race-stranded-task`, P2, must-fix) |
| Candidates raised — Requirements axis | 1 candidate (`requirements/unrequested/shard-push-growth-optimization`, P2, consider) + 1 item routed directly to a published question (never reaches the verifier, per the skill's rule for the Requirements axis's "cannot tell from the code" bucket) |
| Verifier verdicts | Candidate 1: **confirmed** (P2/must-fix unchanged, trigger corrected/narrowed). Candidate 2: **refuted** (factually wrong — rests on a misquotation of the issue text). No merges. Counts: confirmed 1, plausible 0, refuted 1. |
| Findings for publication | **1** — the confirmed Code-axis candidate. Priority/action breakdown: 1 × P2 `must-fix`; 0 `consider` survives (the only `consider` candidate was refuted, not merely downgraded, so it does not publish at all). |
| Questions | **1** — `question/sharded-queue/condvar-mutex-residual-contention`, routed straight to publication by the Requirements finder's "cannot tell from the code" bucket rule; never reached the verifier. |
| Coverage | **6/6 files**, both finders. Every entry in the changed-file manifest is marked `reviewed` by both finders, each with a stated reason; nothing was left unread or abandoned by either finder. Coverage: **complete**. |
| Derived status | **Changes Requested (advisory)** — driven by the one unsettled `must-fix`. Per `publishing.md`'s ladder, this is derived *before* any question or coverage consideration is reached (see item 7, `Pole intact`, and item 8's judgment-call notes on the ladder). |
| Event | `COMMENT` (posting identity `kamui` is a third-party, non-author, first-time reviewer on this PR; gating is not authorized per the packet). Status stated in words on the summary's first line. |
| Publication | **Unconditionally disabled** — retrospective review of an already-merged pull request, per the packet's run conditions and the skill's own merged-PR rule. The full would-be review is reported below (item 5) instead of a link. |

---

### 2. Findings that survive (published)

#### Finding 1 — `code/blocking-pool/idle-count-race-stranded-task`

- **Axis**: Code
- **Priority / Action**: P2 / **must-fix** (verifier kept both, unchanged)
- **Anchor**: `tokio/src/runtime/blocking/pool.rs:437-443`
- **Fix location**: same site — inside the arm body at `tokio/src/runtime/blocking/pool.rs:443` (no separate `fix=` needed; anchor and fix coincide)
- **Claim, verbatim** (as passed to the verifier, `support` withheld):

  > In `spawn_task` (`tokio/src/runtime/blocking/pool.rs:390-461`), after pushing a task, the code
  > branches on `self.inner.metrics.num_idle_threads() == 0` (line 407). When
  > `self.inner.metrics.num_threads() < self.inner.thread_cap` (line 409/427) and `spawn_thread`
  > fails with `io::ErrorKind::WouldBlock`, execution reaches the arm at lines 437-443:
  >
  > ```rust
  > Err(ref e)
  >     if is_temporary_os_thread_error(e)
  >         && self.inner.metrics.num_threads() > 0 =>
  > {
  >     // OS temporarily failed to spawn a new thread.
  >     // The task will be picked up eventually by a currently
  >     // busy thread.
  > }
  > ```
  >
  > This arm does nothing else — it never calls `self.inner.queue.notify_one()`. The identical arm
  > existed in the base version (`git show master:tokio/src/runtime/blocking/pool.rs`, same
  > lines/comment), where it was safe only because `Spawner::spawn_task` held `self.inner.shared` (a
  > single `Mutex<Shared>`) for its *entire* body, and `Inner::run`'s busy→idle transition
  > (`self.metrics.inc_num_idle_threads(); is_counted_idle = true;`) executed only while that very
  > same `shared` guard was held (reacquired right after each `task.run()`, never dropped again
  > until the thread went idle or exited). That serialization made "no idle threads ⇒ some thread is
  > currently busy and will loop back to the queue" strictly true at the moment `spawn_task` read it.
  >
  > This diff replaces that with `queue: ShardedQueue` plus a decoupled `MetricAtomicUsize` for
  > `num_idle_threads`. In the new `Inner::run` (`pool.rs:509-561`), the idle transition is
  > `self.metrics.inc_num_idle_threads();` at line 533, immediately followed by
  > `self.queue.wait_for_task(preferred_shard, self.keep_alive)` — neither is synchronized with
  > `self.inner.shared`, and `spawn_task`'s read of `num_idle_threads()` at line 407 is a plain
  > unlocked atomic load. A worker that has just exhausted the busy loop (found the queue for its
  > shard empty) and is about to call `wait_for_task` is *not* "currently busy" any more, yet
  > `num_idle_threads()` still reads as if it were (the increment hasn't executed yet), so
  > `spawn_task` can read `num_idle_threads() == 0` for exactly this worker. If, at that same moment,
  > `spawn_thread` fails with `WouldBlock`, this arm is taken and no notification is ever sent. The
  > worker then blocks in `wait_for_task` for up to `self.keep_alive` (default 10s from
  > `KEEP_ALIVE` in `pool.rs`), and on timeout returns `WaitResult::Timeout`, which in `Inner::run`
  > (`pool.rs:544-551`) leads straight to `break 'main` with **no** re-check of the queue — the
  > post-loop drain only runs `if self.queue.is_shutdown()` (`pool.rs:554-559`), which is false here.
  > The worker then exits (`dec_num_threads()`), and the task pushed earlier is left sitting in its
  > shard with no worker obligated to look at it again until some unrelated future
  > `spawn_blocking`/`spawn_mandatory_blocking` call happens to route to a `pop()` call.

- **Verifier's verdict**: **confirmed**. Verifier's reasoning and quoted line, verbatim:

  > The `WouldBlock` arm at `tokio/src/runtime/blocking/pool.rs:437-443` really does nothing but
  > comment: [same code quoted] — no `notify_one()` call, confirmed by `grep` showing only two
  > `notify_one()` sites in the file (`pool.rs:455`, `pool.rs:459`), neither of which is this one.
  > Crucially, `wait_for_task` (`sharded_queue.rs:192-227`) is purely counter-driven: it only
  > unblocks by reading `*guard` (the `condvar_mutex`-protected notification count set by
  > `notify_one`), and never re-scans the per-shard `VecDeque`s directly. So a worker that has just
  > exited its busy `pop` loop (`pool.rs:521`, returns `None`) but has not yet executed
  > `self.metrics.inc_num_idle_threads()` (`pool.rs:533`) is invisible to `num_idle_threads()` as
  > "idle" even though it will not check the queue again this cycle. If `spawn_task`'s read at
  > `pool.rs:407` lands in that window and `spawn_thread` returns `WouldBlock`, this silent arm
  > fires, the worker then increments the idle count, blocks in `wait_for_task` for the full
  > `keep_alive`, times out (`WaitResult::Timeout`, `pool.rs:545-551`), and exits via `break 'main`
  > with **no** re-check — the post-loop drain at `pool.rs:562-566` only fires
  > `if self.queue.is_shutdown()`, which is false. The task is stranded until an unrelated later
  > `spawn_blocking` call happens to spawn a new thread (whose busy loop scans all shards,
  > `sharded_queue.rs:156-167`) or hits the "notify anyway" branches.

  Verifier's **corrected trigger**, verbatim: "narrow the race window from 'transitioning from busy
  to idle' to the precise gap between the worker's `pop()` returning `None` (`pool.rs:521`) and its
  own `inc_num_idle_threads()` (`pool.rs:533`) — the increment happens *before* `wait_for_task` is
  entered, so once past that line the thread is correctly counted; the exploitable window is only
  the handful of instructions before it. Rest of the stated trigger (temporary `WouldBlock`,
  `num_threads() > 0`, thread-cap headroom, `keep_alive`-length stall with no drain) checks out
  exactly."

  Verifier's priority/action note, verbatim: "**Priority: P2 (unchanged)** — requires a specific
  environment (OS temporarily refusing thread creation) plus a narrow race, not 'any input,' so
  P0/P1 would overstate it. **Action: must-fix (unchanged)** — demonstrated merge consequence: a
  `spawn_blocking` `JoinHandle` can go unresolved indefinitely absent an unrelated later
  `spawn_blocking` call."

- **Trigger (as it will publish, corrected)**: the blocking pool has not yet reached `thread_cap`;
  a worker's `pop()` has just returned `None` but that worker has not yet executed
  `inc_num_idle_threads()`; at that exact instant `spawn_task` reads `num_idle_threads() == 0` and
  `spawn_thread` fails with `io::ErrorKind::WouldBlock`. The just-pushed task then sits unexecuted —
  the worker itself proceeds to count itself idle, wait up to `keep_alive` (10s default), time out
  with no re-check, and exit — until an unrelated later `spawn_blocking`/`spawn_mandatory_blocking`
  call happens to route a `pop()` to that shard.

---

### 3. Candidates refuted or dropped

Only one candidate was refuted; nothing else was raised to candidate status and then dropped
(everything else the finders weighed either became the surviving candidate above, was acquitted at
the finder stage — see the full ledgers in item 4 — or was routed to the published question).

#### `requirements/unrequested/shard-push-growth-optimization` — **refuted**

Requirements finder's candidate, verbatim: "`Shard::push` (`sharded_queue.rs:47-80`) does more
than shard the lock: on every push where `queue.len() == queue.capacity()`, it drops the shard
lock, allocates a new `VecDeque`..., reacquires the lock, and retries a three-way branch... before
finally calling `queue.push_back(task)`. None of this amortized-allocation-outside-the-lock logic
is required to satisfy the issue's ask..." Priority/action as raised: P2 / consider.

Verifier's reason, verbatim:

> The candidate frames its whole premise on a quoted line from issue #2528: "Replace the
> single-mutex queue... causing severe contention." The actual issue text... reads: "Code that
> invokes `spawn_blocking`... all end up taking a shared lock... This causes a lot of unnecessary
> contention between unrelated tasks if you frequently need to run blocking code." Neither "Replace
> the single-mutex queue" nor "severe contention" appears anywhere in it — the issue only describes
> the contention symptom, it never says "replace" anything, and "severe" is not the word used
> ("unnecessary" is). Per the verifier brief, a misquotation of the cited spec text is itself
> grounds to refute; the candidate's "issue asks only for X" argument rests on a fabricated quote,
> so I can't credit the scope claim built on it. (`Shard::push`'s drop/reallocate/retry scheme at
> `sharded_queue.rs:47-81` is accurately described otherwise, but that's not in dispute — the
> dispute is whether the issue license it, and the cited evidence for that doesn't hold up.)

The verifier notes it independently located a local copy of the issue text (a 3-sentence excerpt,
matching the packet's issue body verbatim) to check the quotation — this is discussed as a
judgment-call/observation in item 8. Priority/action were not recalibrated ("moot given the
refutation"). Per `publishing.md`, this candidate is dropped silently and is not mentioned in the
would-be published review body — only its count (1 refuted) is reported here, per the skill's own
rule.

---

### 4. Both finders' complete disposition ledgers (verbatim)

#### Code axis — disposition ledger (11 rows)

| Claim | Falsification route | Decisive evidence | Disposition |
|---|---|---|---|
| Lost condvar wakeups (commit 2's claimed fix) still present | Trace `notify_one`/`wait_for_task` under `condvar_mutex` | `sharded_queue.rs:148-153`, `:192-227` | acquitted |
| Orphaned tasks on shutdown (commit 2's claimed fix) still present in the branch it targets | Trace shutdown-race drain in `spawn_task` | `pool.rs:411-424` | acquitted |
| Same orphaned-task-on-shutdown class survives in "at max threads" / "idle threads waiting" notify-only branches | Trace shard-mutex/counter ordering during a shutdown race | `pool.rs:453-459`, reasoning: any thread whose counters still read "available" has not yet run its own post-loop drain, and the shard `Mutex`'s lock/unlock ordering guarantees that drain observes the earlier push | acquitted |
| `num_idle_threads`/`num_threads` decoupled from `shared`-lock serialization breaks the "temporary OS error" arm's safety assumption | Compare base vs head locking scope for idle transition vs `spawn_task` | `pool.rs:437-443` vs base `pool.rs` (same arm) + head `pool.rs:407,533` | **candidate** |
| Nested locking: `wait_for_task` holds `condvar_mutex` while acquiring the shard lock via `pop` | Read `wait_for_task` for lock-drop ordering | `sharded_queue.rs:200-207` (`drop(guard)` at line 203, before `self.pop(...)` at line 205) | acquitted |
| Removing `assert!(shared.shutdown_tx.is_some())` introduces a live bug | Check whether the invariant (`shutdown_tx` is `Some` iff `!shared.shutdown`) can be violated at that call site | `pool.rs:414-424` checks `shared.shutdown` under the same lock immediately before | observation (no live bug: invariant still holds structurally) |
| `Shard::push` capacity-growth loop can corrupt or lose data under concurrent growth | Trace re-check-under-lock before swap | `sharded_queue.rs:53-78` | acquitted (only wasted allocation under contention, not a correctness defect) |
| Notification counter over-counts when a task is consumed by direct busy-loop `pop` instead of via `wait_for_task` | Trace counter decrement paths | `sharded_queue.rs:148-153`, `pool.rs:522-525` | acquitted (self-correcting extra wake/pop cycle, not a correctness defect) |
| `thread_rng_n`/`fastrand_n` cfg widening (`context.rs:124`, `rand.rs:71`) is too narrow for the new `sharded_queue.rs` call site or breaks an existing caller | Enumerate all callers and their own cfg gates | `sharded_queue.rs:125` (needs `rt` alone), `sync/watch.rs:418-422` (needs `sync` + (`rt` or `macros`)), `scheduler/multi_thread/worker.rs:1097,1233` | acquitted (new gate is a strict superset covering every caller) |
| `spellcheck.dic` additions ("adaptively", "RNG") are mis-sorted or spurious | Check alphabetical order and usage | `spellcheck.dic:226-227` (RMW < RNG, correct order); words used in new prose/comments | acquitted |
| CHANGELOG.md or another doc restates the pre-change "single mutex" blocking-pool architecture and is now stale | Grep for `blocking pool`/`spawn_blocking`/`shard` in `*.md` outside the diff and outside `docs/research` | `tokio/CHANGELOG.md` (only historical release-log entries, not living architecture description); `docs/contributing/keeping-track-of-issues-and-prs.md` (unrelated) | acquitted / no peers found |

**Note on the two acquittals most relevant to this target's ground-truth defect, quoted in full and
not smoothed over:** the Code finder explicitly examined the "at max threads, notify anyway"
branch (`pool.rs:453-455`) and the "idle threads waiting, notify one" branch (`pool.rs:458-459`) —
the two post-push branches *besides* the one commit 2 already repaired and the one this run's
surviving finding lands on — and **acquitted both**, i.e. concluded they do *not* carry the same
orphaned-task defect class. The finder's own stated reasoning for that acquittal (from its answer
to orchestrator question (a), quoted verbatim): "the 'at max threads, notify anyway' branch
(`pool.rs:454-455`) and the 'idle threads waiting, notify one' branch (`pool.rs:458-459`) are safe
against a *shutdown* race specifically, because any worker whose counters still make it look
'available' has necessarily not yet run its own post-loop drain, and the shard `Mutex`'s
lock/unlock ordering guarantees that drain will observe an already-completed push (I traced this
through explicitly and it holds up) — I logged this as `acquitted` rather than a candidate." This
acquittal was **not** independently re-derived by the verifier — the verifier was given only the
one surviving candidate (the `WouldBlock`-arm claim) and never saw this acquitted hypothesis at
all, because acquitted-at-the-finder-stage rows never reach the verifier under this skill's
process. Whether the acquittal's reasoning actually holds against the code is therefore **not
independently checked anywhere in this run** — it stands solely on the Code finder's own trace, on
Sonnet 5, in a single pass. This is exactly the kind of claim this target was designed to surface,
and readers of this run record should treat that acquittal as unverified rather than confirmed.

#### Requirements axis — disposition ledger (9 rows)

| Claim | Falsification route | Decisive evidence | Disposition |
|---|---|---|---|
| Single shared lock on queue push is eliminated | Read `spawn_task`/`ShardedQueue::push` for a global lock on the push path | `sharded_queue.rs:136-139`, `pool.rs:402-403` | candidate→met (R1) |
| Notification path still funnels through one global mutex | Read `notify_one`/`wait_for_task` for per-shard vs. global locking | `sharded_queue.rs:148-153,192-193`, `pool.rs:453-459` | question |
| PR body's "adapts... fewer shards when thread count is low" claim matches code | Search for any runtime-adaptive shard-count logic | `sharded_queue.rs:29` (`NUM_SHARDS` is a fixed `usize = 16` constant; loom-only `=1`); no thread-count-based logic found in `pool.rs` or `sharded_queue.rs` | observation (not a Requirements candidate — this is a PR-description/commit-message claim, not an issue-#2528 requirement, per brief §"What is not your finding") |
| cfg gate widening on `thread_rng_n`/`fastrand_n` leaves a stale, un-widened peer elsewhere | Two-term paired sweep (new wording / old-wording fragment) across `tokio/src` | `context.rs:124`, `rand.rs:71`, `sync/watch.rs:388/413/420` (subset, unaffected) | acquitted |
| Stale prose elsewhere still describes the retired single-mutex design as current | `grep -rn "single mutex\|single-mutex\|protected by a"` | only `sharded_queue.rs:191` (correctly historical) and unrelated hits | acquitted |
| `Shard::push` growth-outside-lock scheme is unrequested scope creep | Compare against issue's minimal ask; check whether logic is necessary for R1 | `sharded_queue.rs:47-80` | candidate |
| "At max threads, notify anyway" (`pool.rs:453-455`) is an unrequested new behavior vs. old "do nothing" branch | Diff against base `pool.rs` behavior at thread cap | `pool.rs:453-455`; base branch had no notify in this branch | observation (small, defensive, not sized to a full candidate) |
| Lost-condvar-wakeup / orphaned-tasks-on-shutdown bugs (commit 1) still present at head | Re-check per prompt's explicit instruction that commit 2 already fixes these within this PR | `pool.rs:411-424` (drain-inline fix), `sharded_queue.rs:169-179` (shutdown-under-lock fix) | acquitted / out of scope (already fixed in head; also Code axis, not mine) |
| Nested-locking pattern (`ADD-SP`'s unresolved review comment) is a Requirements gap | Check whether it maps to any issue requirement | It is a lock-ordering/deadlock-risk concern — Code axis | acquitted (out of axis) |

---

### 5. The would-be published review, in full

> **This reviews an already-merged pull request; publication is disabled for this retrospective
> run. The following is the review that would have been submitted (event `COMMENT`).**

**Changes Requested (advisory)** — 1 blocking finding, 1 open question.

Code: Findings — 1 blocking. Requirements: Waiting for information (issue alignment: 1 of 2
restated requirements met, 1 unverifiable from static reading alone; no requirement not met).
Reviewed `9de7950e5` against `master` (merge-base `43134f1e5`, identical to base). Coverage:
complete (6/6 files, both axes).

The sharded queue genuinely removes the single-lock bottleneck issue #2528 named, and this diff's
own second commit already closed the two concurrency bugs its own message describes. What's left
is a narrower race of the same shape in a branch neither commit touched: `spawn_task`'s
`WouldBlock` arm can silently strand a just-pushed task for a full `keep_alive` period (and
potentially longer) when a worker's busy→idle bookkeeping lags its actual state by a few
instructions. The open question is whether the remaining single `condvar_mutex` on the
notification path still matters at the concurrency levels the issue reports — a question this
review cannot answer by reading alone.

#### Findings — Code axis

1. **[Code] [must-fix] [P2] `spawn_task`'s temporary-OS-thread-spawn-error arm can strand a task
   with no live worker to run it**

   `tokio/src/runtime/blocking/pool.rs:437-443` — the `Err(ref e) if is_temporary_os_thread_error(e)
   ...` arm does nothing but comment; it never calls `self.inner.queue.notify_one()`. The base
   version's equivalent branch was safe only because a single lock serialized the busy→idle
   transition against this read; the sharded design decouples them.

   **Triggers when**: the pool has not yet reached `thread_cap`; a worker's `pop()` has just
   returned `None` but that worker has not yet executed `inc_num_idle_threads()` (`pool.rs:533`);
   in that exact window `spawn_task` reads `num_idle_threads() == 0` and `spawn_thread` fails with
   `io::ErrorKind::WouldBlock`. The pushed task then sits unexecuted while the affected worker
   itself goes idle, waits up to `keep_alive` (10s default), times out with no re-check
   (`pool.rs:554-559` only drains `if is_shutdown()`), and exits.

   **Change**: in the `Err(ref e) if is_temporary_os_thread_error(e) && ...` arm at
   `tokio/src/runtime/blocking/pool.rs:437-443`, add `self.inner.queue.notify_one();` before
   falling through — the same defensive call this diff already added to the sibling "at max
   threads" arm at `pool.rs:454-455`.

   <!-- finding id=code/blocking-pool/idle-count-race-stranded-task axis=code action=must-fix priority=P2 head=9de7950e59f8acea412600c2102ab592c419483a -->

#### Findings — Requirements axis

None survive verification. (`requirements/unrequested/shard-push-growth-optimization` was raised
and refuted — see item 3; not published, per the skill's "refuted is dropped silently" rule.)

#### Counts by axis and action

- Code: 1 finding — 1 `must-fix`, 0 `consider`.
- Requirements: 0 findings — 1 `consider` candidate raised, refuted, not published.
- Questions: 1.
- Refuted (count only, not detailed here): 1.

### Observations

These are accurate observations, not findings — no action is requested.

- `tokio/src/runtime/blocking/sharded_queue.rs:29` — `NUM_SHARDS` is a fixed compile-time constant
  (16, or 1 under `cfg(loom)`); no code varies shard count based on live thread count, though both
  the pull-request body and the first commit's message describe the design as "adapts to
  concurrency levels by using fewer shards when thread count is low."
- `tokio/src/runtime/blocking/sharded_queue.rs` — the new file contains no `#[test]` or loom test
  module of its own; its concurrency behavior is exercised only indirectly via the pre-existing,
  unchanged `tokio/src/runtime/tests/loom_blocking.rs`.
- `tokio/src/runtime/blocking/pool.rs:443` — the base version's equivalent branch guarded this same
  code with `assert!(shared.shutdown_tx.is_some())` before cloning it; the head version's
  `if let Some(shutdown_tx) = shared.shutdown_tx.clone()` carries no such assertion.

### Open questions

**[Question] Does the residual global `condvar_mutex` still bottleneck notification under the
high-concurrency load the issue reports?**

`sharded_queue.rs:148-153` (`notify_one`) and `sharded_queue.rs:192-227` (`wait_for_task`) both
lock a single, un-sharded `condvar_mutex`. `Spawner::spawn_task` (`pool.rs:402-459`) calls
`notify_one()` in the "idle threads present" branch and the "thread cap reached" branch — i.e., on
nearly every call once the pool is warmed up under load, which is exactly the regime issue #2528
describes. The critical section is now tiny (a counter increment/decrement) versus the original
single lock's much larger section, so real improvement is plausible, but whether this remaining
single mutex still constitutes meaningful lock contention at the reported concurrency levels is a
runtime property, not something static reading settles.

**Change no code for this.** Answer it, or say what would settle it: rerun the PR's own
1/2/4/8/16-thread benchmark with `condvar_mutex` wait time measured separately from shard-lock
wait time (or a lock-contention profile), and confirm it stays negligible as thread count grows.

<!-- finding id=question/sharded-queue/condvar-mutex-residual-contention action=question head=9de7950e59f8acea412600c2102ab592c419483a -->

<!-- review-run workflow=v2a-1 head=9de7950e59f8acea412600c2102ab592c419483a base-ref=master base-sha=43134f1e5784993eb4fb3863933d74ac9e28f598 merge-base=43134f1e5784993eb4fb3863933d74ac9e28f598 issues=tokio-rs/tokio#2528 coverage=complete -->

---

### 6. Direct answers to the orchestrator's specific questions

#### (a) Did any finder examine whether the orphaned-task class survives in the other post-push branches?

**Yes — the Code finder examined every post-push branch, not just the one commit 2 repaired.**
Quoting its ledger row directly: *"`num_idle_threads`/`num_threads` decoupled from `shared`-lock
serialization breaks the 'temporary OS error' arm's safety assumption | Compare base vs head
locking scope for idle transition vs `spawn_task` | `pool.rs:437-443` vs base `pool.rs` (same arm)
+ head `pool.rs:407,533` | **candidate**"*.

Quoting its full answer to this exact question, verbatim: "Yes, I examined all of `spawn_task`'s
post-push branches for the orphaned/stranded-task class, not just the one commit 2 repaired. ...
Concretely: the 'spawn a new thread successfully' branch is safe (the new thread's own busy loop
scans the whole shard ring on start); the shutdown-raced-with-push branch (commit 2's fix) is safe
for the case it targets; **the 'at max threads, notify anyway' branch (`pool.rs:454-455`) and the
'idle threads waiting, notify one' branch (`pool.rs:458-459`) are safe against a *shutdown* race
specifically, because any worker whose counters still make it look 'available' has necessarily not
yet run its own post-loop drain, and the shard `Mutex`'s lock/unlock ordering guarantees that drain
will observe an already-completed push (I traced this through explicitly and it holds up) — I
logged this as `acquitted` rather than a candidate.** But the **`Err(ref e) if
is_temporary_os_thread_error(e) ...` arm at `pool.rs:437-443` calls no notification at all**, and —
unlike the shutdown case — this is not rescued by any later drain in the *non-shutdown* timeout-exit
path, because that path only drains `if self.queue.is_shutdown()` (`pool.rs:554`), which is false
for an ordinary keep-alive timeout. That is the one branch I found not fully covered, and it is my
Candidate 1 above."

**This acquittal is stated here in full and deliberately not smoothed over.** The finder acquitted
the "notify anyway"/"notify one" branches on reasoning about shutdown-race ordering that it traced
itself, in a single pass, and that acquittal was never independently re-checked: it never reached
the verifier (only the one surviving candidate did), and this orchestrator did not independently
re-derive it either. The confirmed finding above is real and correctly proportioned, but it should
not be read as validating this separate acquittal — the acquittal stands solely on the Code
finder's own say-so. See item 4 for the same point made against the full ledger.

#### (b) The nested-locking pattern in `sharded_queue.rs` — did either finder raise it, acquit it, or route it to observations?

**The Code finder raised it as a hypothesis and acquitted it, with a precise code trace, not a
hand-wave.** Quoting its answer verbatim: "I checked this precisely against the actual code and it
does **not** hold: `wait_for_task` drops the `condvar_mutex` guard *before* calling
`self.pop(preferred_shard)`. Quoting the code at `tokio/src/runtime/blocking/sharded_queue.rs:200-207`:
```rust
if *guard > 0 {
    *guard -= 1;
    drop(guard);
    // Pop outside the condvar_mutex to avoid holding two locks.
    if let Some(task) = self.pop(preferred_shard) {
```
`drop(guard)` on line 203 releases `condvar_mutex` before `self.pop(...)` on line 205 acquires the
shard's `Mutex`. I did not find any path where the shard lock is acquired while `condvar_mutex` is
held. This is recorded in my ledger as: 'Nested locking: `wait_for_task` holds `condvar_mutex`
while acquiring the shard lock via `pop` | Read `wait_for_task` for lock-drop ordering |
`sharded_queue.rs:200-207` (`drop(guard)` at line 203, before `self.pop(...)` at line 205) |
acquitted'. I did not route this to observations since there was nothing accurate-but-non-qualifying
to record beyond the acquittal itself (there is no nesting to describe as a fact)."

The Requirements finder also weighed this (correctly noting it is out of its axis) and logged it in
its own ledger as: *"Nested-locking pattern (`ADD-SP`'s unresolved review comment) is a Requirements
gap | Check whether it maps to any issue requirement | It is a lock-ordering/deadlock-risk concern —
Code axis | acquitted (out of axis)"*.

Neither finder routed it to observations. Both correctly identified that, as literally worded by
the human reviewer `ADD-SP` in the packet's prior-review-state summary ("we attempt to acquire the
shard lock while holding the condvar lock"), the claim does not hold against the current code —
`wait_for_task` drops the condvar-paired mutex before calling `pop`. This is a case where a
never-resolved human review comment turned out, on precise tracing, not to describe the shipped
code (or at least not the `wait_for_task` path the finder checked); neither finder treated the
human's unresolved status as license to publish the claim regardless.

#### (c) What did the Requirements finder do with a bug/performance-report issue, and what were the counts?

Quoting its answer verbatim: "Issue `#2528` is a bug/performance report with no checklist; I
treated its body as the statement of the problem (a single shared lock causing contention) and did
not invent acceptance criteria beyond it. Restated requirements, in full:
- R1 (structural): concurrent `spawn_blocking` submission must no longer serialize on one shared
  lock for queue insertion.
- R2 (outcome): as a result, `spawn_blocking`/`block_in_place` throughput under concurrent load
  must not degrade near-linearly as the issue reports.
**Counts: met = 1 (R1), not met = 0, cannot-tell/unverifiable = 1 (R2).**"

R2 was the item routed to the published question (item 5, "Open questions") rather than to the
verifier, per the skill's rule that the Requirements axis's "cannot tell from the code" bucket
bypasses verification entirely.

#### (d) Reproduce the changed-contract lists verbatim

**Requirements finder's changed-contract list, verbatim:** "One contract found — the cfg
feature-gate on `thread_rng_n`/`fastrand_n`:
- Search term 1 (new wording): `any(feature = "macros", feature = "rt")` /
  `any(feature = "macros", feature = "sync", feature = "rt")` — live peers found: none beyond the
  two diff sites (`context.rs:124`, `rand.rs:71`).
- Search term 2 (old-wording fragment): `all(feature = "sync", feature = "rt")` /
  `feature = "rt-multi-thread"` — live peers found: many unrelated `rt-multi-thread` gates across
  the scheduler/runtime/time modules (different mechanism, not RNG-related, disposition: not
  applicable); one RNG-adjacent peer at `sync/watch.rs:388/413/420` (disposition: correct as-is,
  its gate is a strict subset of the new gate, no update needed).
No other changed contract (enum, schema, closed list) was found in this diff."

**Code finder's sync-drift section, verbatim (3 contracts, not 1 — this is the more thorough of
the two sweeps):**

"Changed contracts identified in the diff, with the two search terms used per contract:
1. **Blocking-pool queue implementation** (single-mutex `VecDeque` → sharded queue). Searched:
   `"queue: VecDeque"` / `"shared.queue"` (old) and `"ShardedQueue"` / `"shard"` (new), repo-wide in
   `*.md` outside the diff and outside `docs/research`. Live peers found: none — only
   `tokio/CHANGELOG.md` (historical, unrelated entries) and
   `docs/contributing/keeping-track-of-issues-and-prs.md` (unrelated topic) matched on tangential
   terms, neither restates the architecture as current-state documentation. Also checked non-md
   source for stray `queue: VecDeque` peers: two unrelated matches (`runtime/tests/task.rs`,
   `task/local.rs`) belong to different subsystems (local task queue), not the blocking pool.
2. **cfg feature-gate for RNG helper functions** (`thread_rng_n`/`fastrand_n`:
   `any(feature = "macros", all(feature = "sync", feature = "rt"))` →
   `any(feature = "macros", feature = "rt")`, and the parallel `fastrand_n` gate). Searched: the old
   fragment `all(feature = "sync", feature = "rt")` and the retired
   `feature = "rt-multi-thread"` combination, versus the new fragment `feature = "rt")` used alone.
   Live peers found and checked: `tokio/src/sync/watch.rs:418-422` (uses its own,
   differently-scoped cfg gate `all(not(loom), feature = "sync", any(feature = "rt", feature =
   "macros"))` — still correctly covered by the widened gate, a strict superset);
   `tokio/src/runtime/scheduler/multi_thread/worker.rs:1097,1233` (call `fastrand_n` under
   `rt-multi-thread`, still covered). No stale peer found.
3. **`WaitResult` enum** (new in this diff; commit message says it drops a `Spurious` variant
   relative to an earlier iteration of the same PR branch, not relative to `master`). Searched
   `"Spurious"` repo-wide: only unrelated hits in `tokio/src/loom/std/barrier.rs` (doc comments
   about spurious wakeups in general, pre-existing, unrelated to this enum). No peer, because
   nothing in `master` ever documented this brand-new private enum.

No changed contract was found to have a stale surviving peer anywhere in the repository."

Both finders agree on contract #2 (the cfg-gate widening) and both found it clean. The Code finder
additionally swept two contracts the Requirements finder did not name as "changed contracts" per
se (the queue-implementation replacement and the new `WaitResult` enum) — neither found a
qualifying result, but this is a **coverage difference between the two finders' sweeps**, not a
contradiction between them.

#### (e) Did any agent read git history beyond the pinned head?

**No, by all three sub-agents' own accounting, and by this orchestrator's.**

- Code finder, verbatim: "No. I did not run `git log --all`, nor any `git log <path>` or `git show`
  of a commit past `9de7950e5`. The only git commands I ran were: `git branch -v`; `git log
  --oneline -3 review-head`; `git show master:tokio/src/runtime/blocking/pool.rs` (piped through
  `sed`/`grep`, base-branch content only). All other exploration was `Read`, `grep`, `sed`, `cat`,
  `wc`, and `find` against the working tree already checked out on `review-head`."
- Requirements finder, verbatim: "No. I ran only: `git branch -a`, `git status`, `git rev-parse
  HEAD`, `git rev-parse master`, and one `git show master:tokio/src/runtime/blocking/pool.rs` (a
  base-branch file read, not history traversal). I did not run `git log --all`, did not run `git
  log <path>`, and did not `git show` any commit other than reading the base-branch tree via
  `master:<path>`. No command surfaced anything past `9de7950e5`."
- Verifier: did not report running any `git log`/history command at all in its final report; its
  only cited git-adjacent action was `git log -1 review-head` to read the head commit message
  (used for an observation, not history traversal) and `git diff --stat master...review-head`.
  Neither reaches past the pinned head.
- Orchestrator (this session): ran `git log --oneline -5 master`, `git log --oneline -5
  review-head`, and `git log master..review-head --format='%H %s'` while setting up the shared
  block. `master..review-head` only ever surfaces the two commits *within* the pinned range
  (`9de7950e5`, `11cf7b5d2`) — it cannot surface anything past the pinned head by construction, so
  this is consistent with the constraint, but is disclosed here for completeness since it was a
  `git log` invocation.

The clone's history is truncated at the pinned head regardless, so none of this could have
surfaced anything newer even if attempted; no sub-agent attempted it.

---

### 7. Mechanism checklist

- **C1 (Calibration).** This target's ground-truth defect — the one this run actually confirmed —
  is the `spawn_task` `WouldBlock`-arm task-stranding race (item 2, finding 1). The run landed on
  it, and its priority/action are proportionate rather than either inflated or deflated: **P2**,
  not P0, because the verifier explicitly declined to inflate it ("requires a specific environment
  ... plus a narrow race, not 'any input,' so P0/P1 would overstate it" — P0 is reserved for
  defects that "hold under any input, with no assumptions" per `finding-format.md`, and this one
  needs a transient OS thread-spawn failure plus a narrow timing window); and **must-fix**, not
  `consider`, because the verifier found a demonstrated merge consequence ("a `spawn_blocking`
  `JoinHandle` can go unresolved indefinitely absent an unrelated later `spawn_blocking` call") —
  the calibration rule's bar for `must-fix` (finding-format.md: "a proven correctness ... gap on an
  authoritative execution path is `must-fix`"). Nothing about this target's ground truth was missed
  outright: **do not read this as partial credit dressed up as full credit** — the finder did not
  find every latent concern a maintainer might have (see the C3 note on the "notify anyway"/"notify
  one" acquittals in item 4/6(a), which stand unverified by any later step in this run), but the
  specific high-severity concurrency defect this run confirmed was found, and calibrated
  correctly, not merely gestured at.
- **C3 (Disposition ledger).** Yes — both finders returned full structured ledgers, reproduced
  verbatim in item 4, including explicit "tried-to-convict-and-acquitted" rows (e.g., the Code
  finder's nested-locking row, the lost-wakeup and orphaned-shutdown-task rows explicitly retested
  and acquitted per the packet's boxed instruction; the Requirements finder's stale-cfg-gate and
  stale-prose rows).
- **C4 (Question routing).** Yes. The Requirements finder's R2 ("throughput must not degrade
  near-linearly") landed in its own "cannot tell from the code" bucket and was routed straight to a
  published question (`question/sharded-queue/condvar-mutex-residual-contention`) rather than to
  the verifier, exactly per the skill's rule for that bucket. It is, as the dispatch anticipated, a
  benchmark-dependent claim: the finder's own words, "whether this residual single mutex still
  constitutes meaningful lock contention at the reported concurrency levels is a runtime property
  ... it requires measurement," and its named remedy is rerunning the PR's own benchmark with lock
  time instrumented separately.
- **C5 (Observations).** Nine distinct observations were produced across the three sub-agents (4
  from the Code finder, 2 from the Requirements finder, 3 from the verifier) — all reproduced in
  full in items 2–5 above and in the finder-report excerpts in item 6. Three were selected for the
  bounded published `## Observations` section (item 5) by most-decisive-evidence, per
  `publishing.md`'s 3-item cap; the remaining six are reported here rather than silently dropped:
  the notification-counter off-by-one-under-direct-pop (Code, acquitted-as-non-bug, `sharded_queue.rs:148-153`);
  the shard-push allocation-discard-under-contention (Code, `sharded_queue.rs:53-78`); the
  "adapts to concurrency levels" PR-body claim contradicted by the fixed `NUM_SHARDS` constant
  (Requirements, `sharded_queue.rs:29` — also promoted into the published 3, see item 5); the
  "notify anyway" branch being new/unrequested-but-small behavior (Requirements, `pool.rs:453-455`);
  the head commit's own message not mentioning the still-silent `WouldBlock` arm (verifier); and the
  scope-boundedness of the local issue-#2528 excerpt used in this run (verifier).
- **Pole intact.** Both finders ran (Code and Requirements, in parallel, both on `model: "sonnet"`
  per the `Agent` calls in this transcript). Every candidate that was not routed to a question
  received a verifier verdict (2 candidates in, 2 verdicts out: confirmed, refuted — none skipped).
  `support` was withheld from the verifier: confirmed by re-reading the verifier's own prompt as
  constructed and sent in this run — it was built with only `id`, `axis`, `anchor`, `fix`, `title`,
  `priority`, `action`, `trigger`, and `claim` per candidate, explicitly labeled "The candidates
  (claims only — `support` withheld)," and the verifier's own opening line states it read
  `verify.md` and was not given `support`. No `support` text from either finder's report was copied
  into the verifier's prompt.
- **(C2 no-issue rule does not apply.)** This target has an originating issue, `tokio-rs/tokio#2528`,
  explicitly resolved by the pull request's `Closes` line and used as the Requirements finder's
  spec throughout. The no-issue path (body-claims-as-spec-surrogate) was never invoked and is noted
  here only because the checklist calls for it to be noted plainly.

---

### 8. Notes on the run — judgment calls, guidance treatment, wall clock

**Judgment calls made, named explicitly:**

1. **Guidance membership.** `CONTRIBUTING.md` was treated as `guidance` because it is named
   explicitly in `SKILL.md`'s guidance list ("`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`,
   `CODING_STANDARDS.md`, and scoped equivalents"). `.github/PULL_REQUEST_TEMPLATE.md` was **not**
   treated as canonical guidance under that same list — it is a template describing what a PR
   *description* should contain, not a repository coding/process standard — but it was still
   handed to both finders as supplementary context, flagged as such, because it states a
   substantive rule ("Bug fixes and new features should include tests") that could bear on a
   Code-axis finding. Both finders' provenance was confirmed by diffing `git show
   master:<path>` against the working copy for both files (both unchanged by this diff, confirmed
   identical). Neither finder reported relying on `PULL_REQUEST_TEMPLATE.md`'s test-requirement
   language for any finding (the new `sharded_queue.rs` module has no dedicated tests, which surfaced
   only as an observation, not tied to this guidance file by either finder).
2. **No command-based diff fallback.** `SKILL.md` step 2 allows falling back to a command-based
   instruction ("run `git diff <base>...<head>` yourself") "if the full diff exceeds the harness's
   practical prompt limit." This diff is 633 lines / ~24KB — materialized in full, verbatim, inside
   the shared block given to both finders. The fallback was not needed and was not used; this is
   recorded because the skill's text treats the choice as a live decision to be stated either way.
3. **Sub-agent type and tool restriction.** This harness has no dedicated "finder" or "verifier"
   agent type; all three sub-agents ran as `general-purpose`, which has write/edit tools available
   in principle. Hygiene (no `git checkout`/`switch`/`reset`/`stash`, no file creation/edits inside
   the clone, no `cargo`/`loom`/`miri`, no network) was enforced entirely through explicit
   prompt-level instruction repeated at the top of every one of the three prompts, not through
   removing tools from the agent definition — there is no parameter on this harness's `Agent` tool
   to restrict a sub-agent's tool list. `git status` in the clone was clean both before spawning any
   sub-agent and after all three completed, which is the only available confirmation that this
   held in practice.
4. **Model.** `model: "sonnet"` was passed explicitly on all three `Agent` calls (Code finder,
   Requirements finder, verifier), per the dispatch's non-negotiable instruction, rather than
   relying on the harness's default subagent model.
5. **First-review handling.** The posting identity `kamui` has no prior review, comment, or thread
   anywhere on this pull request per the packet. This was treated as an ordinary first review, not
   a re-review: neither finder was given a prior-findings ledger to fold in (there is none), and the
   verifier was not given the re-review prior-findings addendum from `verify.md` (there is nothing
   to add under that section for a first review).
6. **No `docs/agents/issue-tracker.md` override.** Confirmed absent at both base and head SHAs
   (`git ls-tree -r master --name-only` and a direct path check), so GitHub's default vocabulary and
   verbs from `publishing.md` applied without modification (verbs were never actually invoked, since
   publication is unconditionally disabled, but the derived status/event vocabulary follows the
   default).
7. **Status derivation followed the ladder mechanically, not holistically.** Even though this run
   also has an open, outcome-relevant question (which alone would justify `Needs Information`), the
   presence of one unsettled `must-fix` finding sends the ladder straight to `Changes Requested` at
   step 1, per `publishing.md`: "Derive it in that order, never by judging it as a whole." This
   orchestrator did not soften that to `Needs Information` on account of the open question, and did
   not let the open question get folded into or overshadow the blocking finding.
8. **Merged/retrospective handling.** Per the packet and `SKILL.md`'s own merged-PR rule, this run
   derived status exactly as it would for an open PR — the "already merged" fact was applied only
   to (a) unconditionally disabling publication and (b) requiring the summary's first line to name
   the retrospective condition, not to altering the status ladder itself.
9. **Event and status wording.** Because the posting identity is a non-author third party with no
   gating authorization stated in the packet, the event is `COMMENT` and the status is rendered in
   words on the summary's first line as `Changes Requested (advisory)`, per `publishing.md`'s
   "Status versus forge event" section.
10. **The verifier's independent use of a local, pre-existing issue-text excerpt.** The verifier's
    prompt built by this orchestrator did **not** include the issue text (the verifier's brief in
    `verify.md` only calls for the candidate claims and the repository). To refute candidate 2, the
    verifier located and read `/tmp/handoff3/tokio-issue-2528.md` on its own — a local,
    pre-existing scratch file (confirmed by this orchestrator, post hoc, to predate this session and
    to match the packet's issue-body text verbatim) outside the git clone but on the same local,
    offline filesystem, not a network fetch. This was not something the orchestrator instructed or
    anticipated, but it satisfies every hard constraint (no network, no mutation) and was decisive
    in correctly refuting a misquotation-based candidate. This orchestrator treats it as within
    bounds — verify.md's "the repository" is reasonably read as "the local, offline evidence
    available," which this file is — but flags it explicitly as a judgment call a stricter reading
    of the brief might not have allowed (a stricter verifier might have had to treat the issue text
    as unavailable to it and default to `plausible` instead of `refuted`, per the brief's stated
    asymmetry).

**Total wall clock:** dispatch received/read ≈ 04:02 (file timestamp `04:02:06`); Requirements
finder returned `04:16:18`; Code finder returned `04:21:43`; verifier returned `04:28:19`; this
report finalized ≈ 04:30. **≈ 28 minutes end-to-end**, with the two finders running concurrently
(single message spawning both) and the verifier run strictly after both finder results were in
hand, per the skill's required sequencing.

