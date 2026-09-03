# Evaluating six agentic code-review runs against a shipped regression

> **Promotion status:** “v5” is the historical prototype name used by this record. PR #17 promoted
> that workflow to `skills/code-review-publish` on `main`; new work should invoke
> `/code-review-publish` without the `-5` suffix. **Superseded 2026-09-03:** PR #42 replaced that skill with **v5a**, so `/code-review-publish` now invokes v5a, not the v5 workflow this record tests. `skills/code-review-publish-legacy` is the v1 legacy reviewer, and v5 is no longer on `main` — pin it from `571f31d`.

**2026-09-01–03.** This reevaluates v2–v5 together with the later v2a/v5a runs on
[`tokio-rs/tokio#7757`](https://github.com/tokio-rs/tokio/pull/7757). The pull request shipped a
production `spawn_blocking` hang, was reverted six days later, and was corrected four months later.

Sources: [README](README.md), [v2](v2-run.md), [v3](v3-run.md), [v4](v4-run.md), [v5](v5-run.md),
[v2a](v2a-run.md), [v5a](v5a-run.md), [retest addendum](addendum-2026-09-03.md), and
[comparison data](comparison-data.md).

## Conclusion

**All six runs requested changes, but only four found the full defect that shipped.** V2, v4, v5,
and v5a identified both unguarded post-push branches. V3 found a real sibling race in one branch but
explicitly cleared the historically decisive “at max threads” branch on false reasoning. V2a found
a different adjacent stranding path and explicitly acquitted both ground-truth branches, reproducing
v3's error. Its status was right for the wrong reason.

The strongest new result is v5a's fix-sufficiency check. In a history-truncated clone, its primary
found both branches but proposed the same narrow repair pattern that had already failed in the pull
request: copy a check into more branches. The verifier rejected that remedy, named the shared
invariant, enumerated all sibling paths, and moved the fix to one central synchronization point.
That is the shape the real correction required. It is the first direct evidence that N2 changes a
published fix rather than merely confirming one.

The most transferable negative result is the verification hole. V2a's false acquittal never reached
its verifier because another candidate survived. V5a's ledger-wide clean-verdict check also would
not have fired with a survivor. A high-risk false acquittal beside a true finding is invisible to
both architectures as written.

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

The original mirror contained post-merge history. Only v4 read it. V4 had already derived its
candidate statically, but the revert and actual re-land strengthened its P0 and repair guidance.
The retest mirror was rebuilt from only the base and head; the later commits were unreachable. V2a
and v5a are therefore history-blind, but they are also development-set prototypes designed after
the earlier target results were known.

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
| v2  | full B/C defect at P1, plus an advisory caller-thread finding       |
| v3  | branch C / timeout projection at P1                                 |
| v4  | full B/C defect at P0, with hindsight available                     |
| v5  | full B/C defect at P1                                               |
| v2a | different `WouldBlock` stranding path at P2; ground truth acquitted |
| v5a | full B/C defect at P1                                               |

A status-only score would mark all six successful. The finding-level record shows one partial hit,
one miss, three blind full hits, and one contaminated full hit. Evaluation must score the defect and
fix, not only the final ladder state.

## V2a: a confirmed adjacent finding and a false acquittal

V2a's Code finder stated that B and C are safe because any worker still represented by the counters
must not yet have completed its final drain, and shard-lock ordering makes the drain observe the
push. The code gives the opposite ordering: idle count falls before the drain, while thread count
falls after it. The finder inspected the right branches and recorded a checkable false reassurance.

Its surviving finding is different. If `spawn_thread` returns temporary `WouldBlock` during a
narrow busy-to-idle transition, the match arm neither notifies nor rechecks. V2a's verifier confirmed
a stranding trace and retained P2 `must-fix`. V5a dropped the same arm as pre-existing because its
text is byte-identical at base.

Both readings expose a needed rule. “Introduced here” cannot be decided only by whether the line
changed when a refactor invalidates an unchanged branch's synchronization assumptions. Conversely,
an unchanged, already-broken behavior should not automatically become this pull request's blocker.
The reviewer should compare the relied-on invariant at base and head and state whether the change
made the previously safe path unsafe.

V2a's verifier also caught a Requirements finder quotation that does not occur in issue #2528 and
refuted the scope-creep candidate built on it. That is clean evidence that withholding finder
`support` and checking the cited spec can stop confident fabrication.

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

V2a verifies only candidates. Its B/C acquittal stayed in the Code ledger and was checked by nobody.
V5a can send a full ledger to a clean-verdict verifier, but only when zero findings survive. Because
v2a had a different survivor—and v5a would have had one in the analogous situation—neither design
protects against a false acquittal adjacent to a true finding.

This is not hypothetical. It is exactly where the ground truth sat in v2a. The disposition ledger
still helped by preserving the error for later audit, but auditability after the run is not a safety
mechanism during the review.

A better trigger is bug-class based: when a consequential candidate survives, include every
acquittal about sibling branches or the same invariant in the verifier packet. That bounds cost more
tightly than verifying the full ledger on every non-clean review while covering this failure mode.

## Other verifier behavior

The original verifier results remain useful:

- v2 narrowed its trigger while confirming both findings;
- v3 corrected “hidden by shard affinity” to the actual no-worker-remains mechanism and refuted a
  false cfg claim;
- v4 independently refuted the same cfg claim but used future history to rewrite its fix;
- v5 proved that neither adjacent loom test covered the failing interleaving; and
- v2a independently checked the temporary-thread-error trace and the issue quotation.

Fresh verification consistently improves some detail. It does not guarantee that every relevant
claim enters the batch or that a proposed remedy closes the full invariant.

## Questions and observations

V2 and v2a both surfaced the empirical question whether the remaining single `condvar_mutex`
becomes the next scalability bottleneck above the published benchmark range. That is an appropriate
question: static review cannot settle it, and turning it into a correctness finding would be
speculation.

V5a's question is narrower: the body says shard count adapts to concurrency, while the code fixes
`NUM_SHARDS` at 16. Static reading cannot determine whether the published benchmark measured this
head or an earlier adaptive draft. The question channel preserves that uncertainty.

V2a/v5a also demonstrate the value of bounded observations for cleared prior-review concerns and
accurate maintainability facts. These channels increase artifact honesty without diluting the
finding bar.

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

**V2a — right status, wrong defect.** It found a plausible adjacent blocker and exposed both a
fabricated quotation and a structured false acquittal. On ground-truth recall it regressed from v2.

**V5a — strongest artifact, development-set evidence.** It found the full defect without later
history and its verifier generalized the fix. This is a mechanism success on one known target, not
a final winner declaration.

## Recommendation

Advance the integrated v5a line with N2, bounded observations/questions, and one follow-up verifier
round. Add a targeted ledger-review rule: every high-consequence survivor brings along acquittals
from the same invariant or sibling branches. Preserve v2a's explicit disposition records and spec-
quotation checks, but do not use the two-finder panel as the default frequent path.

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

- V2a and v5a are development-set designs, one run each.
- V4's original result used post-merge history.
- The experiment did not build, run tests, loom, or dynamically reproduce the race.
- Original cost meters exclude integrated primaries and cannot be compared with retest totals.
- Model identity is aligned only at a coarse family level across cohorts; harness and sampling differ.
