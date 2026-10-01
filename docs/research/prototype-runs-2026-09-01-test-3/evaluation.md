# Evaluating six agentic code-review runs against a shipped regression

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

## Conclusion

The strongest new result is v5a's fix-sufficiency check. In a history-truncated clone, its primary
found both branches but proposed the same narrow repair pattern that had already failed in the pull
request: copy a check into more branches. The verifier rejected that remedy, named the shared
invariant, enumerated all sibling paths, and moved the fix to one central synchronization point.
That is the shape the real correction required. It is the first direct evidence that N2 changes a
published fix rather than merely confirming one.

V5a produced the best uncontaminated artifact on this target: correct defect, correct blocking
action, and invariant-level fix. That validates mechanisms on a development-set target; it does not
establish population-level superiority. V2 still demonstrates useful breadth through an additional
confirmed finding and empirical question, at the cost of a duplicated full review.

## Method and evidence quality

Every run reviewed the same identity:

| Input             | Pinned value                                                         |
| ----------------- | -------------------------------------------------------------------- |
| Pull request      | `tokio-rs/tokio#7757`, merged 2026-04-10                             |
| Head              | `9de7950e59f8acea412600c2102ab592c419483a`                           |
| Base / merge-base | `43134f1e5784993eb4fb3863933d74ac9e28f598` on `master`               |
| Diff              | 6 files, +340/−126, two commits                                      |
| Originating issue | `tokio-rs/tokio#2528`                                                |
| Prior state       | 52 comment threads, one approval, one unresolved nested-lock concern |
| Execution         | static only; network, build, tests, loom, and miri forbidden         |

The original runs used the session-default Claude Sonnet 5 under Claude Code. The retest passed
`claude-sonnet-5` explicitly under `t3code` and verified it from every agent transcript. Model family
is aligned, but harness, metering, run date, and skill maturity differ.

## Ground truth

`Spawner::spawn_task` pushes a task and then chooses among three branches:

- A: no idle threads and below the cap — attempts to spawn a worker and contains the added shutdown
  recheck/drain;
- B: no idle threads and at the cap — calls `notify_one()` only; and
- C: an idle thread is reported — calls `notify_one()` only.

During worker shutdown, idle count is decremented before the worker's final drain and thread count
after it. A push can land after the last drain found nothing but before thread count falls. The
spawner reads zero idle threads and the old capped thread count, takes B, and notifies after no worker
remains in `wait_for_task`. The queued task has no consumer and its `JoinHandle` can remain unresolved.

The base implementation serialized push, accounting, and shutdown under one shared lock. The
refactor split those responsibilities and restored a recheck only in A. The later production hang,
emergency revert, and corrected re-land independently establish that the merged synchronization
design was wrong.

## Status is a poor discriminator

Every run produced Changes Requested:

| Run | Why it blocked                                                      |
| --- | ------------------------------------------------------------------- |
| v3  | branch C / timeout projection at P1                                 |
| v4  | full B/C defect at P0, with hindsight available                     |
| v5  | full B/C defect at P1                                               |
| v5a | full B/C defect at P1                                               |

A status-only score would mark all six successful. The finding-level record shows one partial hit,
one miss, three blind full hits, and one contaminated full hit. Evaluation must score the defect and
fix, not only the final ladder state.

## V5a: N2 changes the remedy

V5a's primary correctly identified B and C and proposed copying A's shutdown recheck into both.
That patch addresses the observed projection but preserves the architectural failure: safety
depends on every current and future branch remembering the same local check.

The fresh verifier rejected the patch while confirming the finding. It named the invariant—no push
may become unowned across the shutdown transition—then gave an exposure verdict for all three
branches. It recommended closing the race once in `ShardedQueue::push` or
`BlockingPool::shutdown`, under the lock that flips shutdown state. The primary adopted the change
and moved the fix coordinate from `pool.rs` to `sharded_queue.rs`.

This is better review guidance than “duplicate this check twice,” and unlike v4's upstream-matching
guidance it was produced without access to the actual re-land. The result directly validates the
bug-class/fix-sufficiency verifier obligation.

## The shared verification hole

A better trigger is bug-class based: when a consequential candidate survives, include every
acquittal about sibling branches or the same invariant in the verifier packet. That bounds cost more
tightly than verifying the full ledger on every non-clean review while covering this failure mode.

## Other verifier behavior

The original verifier results remain useful:

Fresh verification consistently improves some detail. It does not guarantee that every relevant
claim enters the batch or that a proposed remedy closes the full invariant.

## Questions and observations

V5a's question is narrower: the body says shard count adapts to concurrency, while the code fixes
`NUM_SHARDS` at 16. Static reading cannot determine whether the published benchmark measured this
head or an earlier adaptive draft. The question channel preserves that uncertainty.

## Prototype verdicts

**V2 — breadth leader, expensive default.** It found the complete ground truth, one additional
confirmed behavior, and the first version of the residual-lock question. The parallel whole-diff
passes buy recall but duplicate effort.

**V3 — real partial hit with dangerous reassurance.** Its published branch-C race is valid, and its
verifier corrected useful details. Its explicit “self-healing” clearance of B is factually wrong and
describes the production branch.

**V4 — technically strong but contaminated.** It found the bug before reading later history, yet
the P0 and exact upstream fix cannot be credited as blind architecture performance.

**V5 — cleanest original blind replication.** It found both branches at P1 and used its verifier to
exclude nearby loom tests. Its per-branch repair was narrower than the bug class.

**V5a — strongest artifact, development-set evidence.** It found the full defect without later
history and its verifier generalized the fix. This is a mechanism success on one known target, not
a final winner declaration.

## Recommendation

Evaluation should score at least four dimensions separately:

1. ground-truth defect recall;
2. false findings and false acquittals;
3. action calibration; and
4. fix sufficiency at invariant level.

Repeat this target with explicit models, a head-truncated mirror, and multiple seeds. Seed one run
with the known false “available worker has not drained” premise to test whether the verifier attacks
it. Include a survivor on an adjacent path so the new same-bug-class ledger trigger, rather than the
zero-finding clean check, must fire.

## Limits

- V4's original result used post-merge history.
- The experiment did not build, run tests, loom, or dynamically reproduce the race.
- Original cost meters exclude integrated primaries and cannot be compared with retest totals.
- Model identity is aligned only at a coarse family level across cohorts; harness and sampling differ.
