# Evaluating four agentic code-review prototypes against a pull request with a known, real regression

**2026-09-01.** This analyzes the third controlled four-way run of `code-review-publish-2` through
`code-review-publish-5` (v2-v5), against
[`tokio-rs/tokio#7757`](https://github.com/tokio-rs/tokio/pull/7757). Unlike the first two targets —
a documentation/schema PR in the reviewer author's own repository (test 1) and a merged, cleanly
reviewed C concurrency PR with no known defect (test 2) — this target has an independently verifiable
ground-truth outcome: it shipped a real regression, was reverted six days later, and the corrected
fix took four more months to re-land.

Raw records: [method and inputs](README.md),
[v2](v2-run.md), [v3](v3-run.md), [v4](v4-run.md), [v5](v5-run.md), and
[comparison data](comparison-data.md).

## Conclusion

**All four prototypes independently identified the real defect that caused this PR's production
incident, and all four unanimously derived `Changes Requested`.** This is the strongest positive
result across all three tests: a change that went through 52 review-comment threads and four months
of maintainer attention, and was still approved and merged with a bug that hung production
`spawn_blocking` callers, was caught by all four architectures working from a single static pass over
the merge-base diff, with no build, no test execution, and no loom.

That headline needs three immediate qualifications:

- **One run (v4) had access to information the other three did not.** The local mirror clone used
  for all four runs was not truncated to pre-merge history, and v4 discovered — by chance, via a
  routine `git log --all` check — that this exact PR was reverted (`tokio-rs/tokio#8057`) for the
  exact bug class it was independently tracing. This did not manufacture v4's finding (it had already
  derived the mechanism statically before finding the revert), but it materially strengthened v4's
  confidence and priority (P0, the only P0 of the four). See
  [The hindsight-contamination problem](#the-hindsight-contamination-problem).
- **One run (v3) has a checkable factual error in its supporting analysis**, even though its
  published finding is independently valid. It dismissed the exact code branch that turned out to be
  the historically-confirmed root cause as "self-healing," based on a premise that direct inspection
  of the code does not support. See [v3's dismissed branch](#v3s-dismissed-branch).
- **Priority calibration split 3-to-1 on the identical defect** (P0 from v4, P1 from v2/v3/v5) — a
  real inter-rater disagreement about how to weigh a race with a narrow trigger window against a
  permanent, contract-breaking hang, independent of the hindsight question above.

## Controlled method

| Input | Pinned value |
| --- | --- |
| Pull request | [`tokio-rs/tokio#7757`](https://github.com/tokio-rs/tokio/pull/7757), merged 2026-04-10 |
| Head | `9de7950e59f8acea412600c2102ab592c419483a` |
| Base and merge-base | `43134f1e5784993eb4fb3863933d74ac9e28f598` on `master` |
| Diff | 6 files, +340/−126, two commits |
| Specification | Originating issue [#2528](https://github.com/tokio-rs/tokio/issues/2528), closed by this PR |
| Prior review state | 52 comment threads, 5 participants, one `APPROVED` (`Darksonn`), one raised-then-unresolved design concern (`ADD-SP`, nested locking) |
| Posting identity | `kamui`, not the author — ordinary first review, `COMMENT` |
| Model / harness | Claude Sonnet 5, Claude Code `Agent` tool (`general-purpose` sub-agents) — **identical across all four runs**, unlike test 2 vs test 1 |

Each run got an offline clone with `origin` pointed at a local mirror path, the same phase-1 packet
verbatim (including an explicit instruction to treat commit 2's fixes as already applied, not
rediscover them), publication disabled, and network/builds/tests forbidden. See
[conditions held constant](README.md#conditions-held-constant).

### This one is directly comparable, unlike test 2

Test 2 changed the model and harness alongside the target, so nothing about the four-way comparison
there could be isolated from those confounds. Here, all four runs share model and harness with each
other **and** with test 1 (Claude Sonnet 5 vs test 1's "Claude Opus 5 (1M context)" — a different
model tier, so cross-test comparison is still not exact, but the within-test comparison is clean and
the harness — Claude Code's own `Agent` tool — is identical to test 1's).

### What ground truth is available — and its limit

**This is the first test with strong, independently checkable ground truth.** `tokio-rs/tokio#7757`
merged, caused a real hang reported as `tokio-rs/tokio#8056`, was reverted six days later
(`tokio-rs/tokio#8057`, "this commit introduced a regression that causes programs using
`spawn_blocking` to hang ... the hang still occurs with `NUM_SHARDS` set to 1"), and a corrected,
opt-in re-land shipped four months after that (`tokio-rs/tokio#8337`). I independently confirmed all
three commits exist in the local mirror and read the revert's own commit message directly — this is
not a claim taken on any run's word. The mechanism all four runs describe (a race between
`Spawner::spawn_task`'s idle/thread-count read and a worker's exit sequence in
`tokio/src/runtime/blocking/pool.rs`) is exactly the kind of defect that class of bug report
describes.

**The limit:** ground truth here is "this specific PR, as merged, was wrong" — it does not tell us
whether each run's *specific* proposed fix is the one upstream actually shipped. v4's verifier
checked this directly and found upstream's eventual fix (`8b13642a`) took a different shape (the
*spawner* claims the idle worker atomically under a coordination lock, rather than the worker
acknowledging after the fact) than any of the four runs' own `change:` proposals recommended
verbatim — v4's was closest, and its verifier explicitly rewrote the fix guidance to match upstream's
actual approach after finding it. This is real, useful information, and also a small instance of the
same hindsight problem: v4 could sharpen its fix by reading the actual solution; nothing in v2/v3/v5's
process. See below.

## The convergent finding

All four runs, independently and without seeing each other's output, identified the same structural
defect: `Spawner::spawn_task` (`tokio/src/runtime/blocking/pool.rs:390-463`) has three branches after
pushing a task to the new sharded queue. Only one of them — "no idle threads, spawn a new one" — was
given the shutdown recheck that the PR's own second commit added to fix "orphaned tasks on shutdown."
The other two branches call only `queue.notify_one()`, with no recheck and no fallback drain, and
`notify_one()` is a silent no-op once every worker has already left `wait_for_task`.

I independently re-read the relevant code myself (not just each run's citations) to check this
before writing this evaluation:

```rust
// tokio/src/runtime/blocking/pool.rs — post-push branch dispatch
if self.inner.metrics.num_idle_threads() == 0 {
    if self.inner.metrics.num_threads() < self.inner.thread_cap {
        // ... spawn-new-thread branch: rechecks shared.shutdown, drains inline if raced
    } else {
        // At max threads, notify anyway in case threads are waiting
        self.inner.queue.notify_one();      // <- no recheck at all
    }
} else {
    // There are idle threads waiting, notify one
    self.inner.queue.notify_one();          // <- no recheck at all
}
```

and the worker's exit sequence:

```rust
WaitResult::Shutdown => {
    self.metrics.dec_num_idle_threads();    // decremented here
    break 'main;
}
// ... drain loop over all shards, then:
self.metrics.dec_num_threads();             // decremented only here, after the drain
```

`dec_num_idle_threads()` happens before the worker's final drain sweep; `dec_num_threads()` happens
after it. A push landing in the window between those two — after the drain sweep found nothing
(because the push hadn't happened yet) but before the thread count decrements — reads
`num_idle_threads() == 0 && num_threads() == thread_cap`, routes into the unguarded "at max threads"
branch, and is orphaned: no worker will ever call `pop()` on that shard again, and the `JoinHandle`
never resolves. I confirmed `ShardedQueue::pop` scans all `NUM_SHARDS` shards starting from a
preferred offset, so this is not a shard-visibility bug — it's a pure ordering race between two
independently-decremented atomics that used to be one field, updated under one lock, before this PR
split the queue.

**Every element of that trace appears, independently derived, in at least three of the four reports**
(v2's Candidate 1, v4's verifier's justification steps 1–4, v5's verifier's justification steps 1–4
all construct the identical interleaving with the identical two line-pairs as the decisive citation).
This is not four runs agreeing because they all read the same PR body — the PR body and both commit
messages describe the bug as *already fixed*; finding that it wasn't required tracing control flow
the packet did not point at.

### Framing differences

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Branch(es) named | Both unguarded branches | The idle-notify branch only | Both, via idle-count accounting timing | Both, explicitly |
| Named mechanism | Stale `Relaxed` reads racing a worker's shutdown exit | A keep-alive-*timeout* race (not shutdown) | A worker claims a task before its idle-count decrement is visible | Worker decrements idle-count before its drain sweep completes |
| Priority | P1 | P1 | **P0** | P1 |

v3's mechanism (a keep-alive timeout, not a shutdown) is a **different, additional, and also real**
race in the same branch: `WaitResult::Timeout` also decrements `num_idle_threads` before any
downstream bookkeeping, and nothing in the shutdown path re-scans for tasks that arrive after a
timeout-driven exit. This is a genuine second path to the same consequence that v2/v4/v5 did not
separately name (v2's trigger is shutdown-specific; v4/v5's traces are shutdown-specific too). v3's
report is therefore not redundant with the others — it independently found a related defect via a
different interleaving. Where v3's analysis has a problem is not this finding; it's the branch it
*cleared*.

## v3's dismissed branch

v3 ran a named risk check against the "at max threads, notify anyway" branch (`pool.rs:453-455`) —
the same branch v2, v4, and v5 (and their verifiers) all identify as the historically-confirmed root
cause — and recorded:

> checked whether it shares the same defect as the idle-branch bug, found it's self-healing via the
> busy-loop's full-shard rescan since `idle == 0` implies no thread is parked in `wait_for_task` there.

This premise does not hold. `num_idle_threads() == 0` is also the state immediately after the *last*
worker has decremented its own idle count on the way to exiting (`WaitResult::Shutdown =>
{ dec_num_idle_threads(); break 'main; }`) — there is no live busy-looping thread in that state, only
a thread mid-exit that has not yet reached `dec_num_threads()`. This is exactly the window v2's
Candidate 1, v4's verifier, and v5's verifier all construct as the trigger, and it is exactly the
window the real `tokio-rs/tokio#8056` hang and its revert (`#8057`) describe. I checked this against
the code directly rather than taking any run's characterization on trust (see the code excerpt
above): the "at max threads" branch has no recheck of any kind, and nothing about `idle == 0`
implies a live rescanning thread.

This does not undermine v3's published finding — the idle-notify branch it did name is independently
a real defect, confirmed by v3's own verifier through a distinct mechanism. But it means v3's report,
read as a complete risk assessment of the file, contains a specific, checkable claim that is wrong,
and that claim happens to be about the exact branch where the real production incident originated.
An automated reviewer whose "self-healing, cleared" language reaches a human reader carries the same
false-reassurance risk as an outright missed finding, even when a sibling finding elsewhere in the
same report happens to trigger the correct overall status.

## The hindsight-contamination problem

v4's report states plainly that it found the revert history "by chance," attributes it to a
legitimate local-evidence read (no network call was made — the objects were already in the offline
mirror), and uses it as "decisive history evidence... stronger than the candidate claimed." This is
disclosed candidly in v4's own Notes section, and I have independently confirmed every commit it
cites exists and says what it claims. But it changes what v4's P0 priority is evidence of.

The verifier's own priority justification reads: *"Impact wording 'or, in the worst case, ever' should
be firmer: with a long-lived blocking task this is a deterministic deadlock, which is why it was a
release-blocking revert."* The deterministic-deadlock mechanism was independently derived from static
control-flow tracing (steps 1–4 of the verifier's justification, which do not depend on the history).
The **P0-vs-P1 threshold call**, though, is reinforced by "which is why it was a release-blocking
revert" — a piece of reasoning that is only available because v4 already knows the outcome. Take the
history away, and v4's case for P0 over P1 rests on the same static argument v2/v3/v5's verifiers had
in front of them, and none of the other three crossed that threshold on it.

This does not mean v4's severity call is wrong — a deterministic permanent-hang deadlock that silently
breaks a documented "guaranteed to run" contract is a defensible P0 on the rubric's own terms without
any history at all. It means **this run cannot be used as evidence that v4's architecture calibrates
severity better than the others'** on this data point, because the calibration was not blind. A repeat
of this experiment with the mirror's history truncated at the merge-base (see
[README.md](README.md#methodology-note-hindsight-contamination)) would be needed to settle whether the
3-to-1 P1/P0 split reflects an architectural difference or an information difference.

## What each verifier actually changed

Unlike test 2, where no verifier ran in any of the four architectures, **every verifier in this test
fired and did real work**:

- **v2's verifier** confirmed both Code candidates outright but tightened Candidate A's trigger,
  dropping the "idle threads still waiting" case as unnecessary and pinning the mechanism to the "at
  max threads" branch's stale `num_threads()` read alone — a real narrowing that makes the published
  finding's trigger description more precise than the unverified draft.
- **v3's verifier** corrected a specific mechanism error: v3's own theory was that the orphaned task
  was "hidden by shard affinity"; the verifier established the actual cause is simpler and different
  — no worker remains alive to call `pop()` at all, regardless of which shard the task landed in. It
  also independently falsified v3's second candidate (the `fastrand_n` cfg claim) by finding a
  module-level gate v3 had walked past.
- **v4's verifier** rewrote the fix recommendation to match what upstream's actual, eventual re-land
  did (spawner-side atomic claim under a coordination lock, not worker-side after-the-fact
  acknowledgment) — the single most concrete, most upstream-accurate piece of guidance in any of the
  four reports, though only available because the verifier could read the real fix. It also refuted
  the same `fastrand_n` cfg candidate v3 raised, via the identical citation, independently.
- **v5's verifier** tightened both `trigger` and `impact` wording and went further than v5's own
  falsification by checking whether either of the two closest pre-existing loom regression tests
  models this exact interleaving — finding that neither does, for two different reasons (one is
  same-thread/sequential by construction, the other starts from a zero-thread runtime and only
  reaches the already-protected branch).

**Two verifiers (v3, v4) independently caught the identical mistake** — a claim that `fastrand_n`'s
widened `cfg` attribute could compile unreachable, dead code under a `sync`-only build feature
combination — via the identical citation (`tokio/src/util/mod.rs:61`'s module-level gate on
`mod rand;`). This is the clearest evidence across all three tests that two structurally different
verification architectures, given the same wrong claim, converge on the same correction using the
same evidence — a good sign for the mechanism's reliability, independent of which specific
verification-trigger rule dispatched it.

## Secondary results

- **v2's parallel Requirements axis is the only channel across all four architectures that produced
  an open question**, and it is a good one: whether the design's one remaining non-sharded lock (the
  `condvar_mutex` in `notify_one`) is enough to keep per-call cost flat past the PR's own 16-thread
  benchmark, or becomes a new bottleneck at higher concurrency. This is exactly the kind of claim that
  cannot be settled by static reading and that this run's no-build/no-benchmark constraint cannot
  answer either — v2 correctly routed it to a question rather than manufacturing a verdict either way.
  v3/v4/v5 have no architectural channel to publish an item like this at all; it would either become
  a (unverifiable, and therefore probably dropped) candidate or be omitted.
- **v2 alone published a second, independently confirmed finding** — that the shutdown-race drain
  branch runs mandatory blocking work synchronously on the caller's thread rather than the pool,
  inconsistent with the identical race handled a few lines above in the same function. This is a real,
  distinct P2 that no other run raised, and it is architecture-attributable: v2's separate Code-axis
  finder, working the full diff independently of a Requirements pass, had capacity to keep pursuing
  candidates near the main finding that the three integrated single-reviewer architectures did not
  surface (not because they couldn't, but because none of their reports mention checking it).
- **v2's total cost (227,934 self-reported sub-agent tokens across 3 sub-agents) is roughly 3–4× any
  other run's** (54k–66k, each with exactly one verifier sub-agent). On this PR, that cost bought two
  additional real deliverables (the P2 finding, the open question) beyond what the single-reviewer
  architectures produced. Whether that trade is worth it in general is not something one PR settles,
  but it is the clearest cost/output contrast across all three tests so far — the other three
  architectures are within roughly a factor of 1.2 of each other in both cost and output on this PR.

## The unresolved "closed pull request" rule

v3's report surfaces something the other three reports do not discuss, but that plausibly applies to
all of them equally, since they share a common lineage: `SKILL.md`'s phase 1 instructs the reviewer to
"stop on a closed pull request or ambiguous target," carving out an explicit exception only for
drafts. Read literally, this PR — merged, hence closed — should have triggered an immediate stop with
no review at all. v3 discusses this tension explicitly and chooses to proceed (reasoning: explicit
invocation, the skill's own design anticipates evaluation against known-outcome PRs, and publication
was disabled regardless). v2, v4, and v5 do not mention this rule at all in their notes, which is
itself ambiguous: it may mean their skill variants read the rule differently, phrase it differently,
or simply that those runs didn't surface the tension in their reports. This is worth a direct textual
check across all four `SKILL.md`s before the next test, because it bears on a real operational
question distinct from anything else this test measures: **should any of these skills be usable for
retrospective review of an already-merged PR at all**, and if so, on what basis should "closed" be
read as "abandoned/rejected" rather than "resolved with a known outcome"?

## Prototype verdicts

**v2 — highest recall, highest cost.** Found the primary defect, a second independently valid finding
the other three missed, and the only genuine open question — at roughly 3–4× the token cost of any
other run. Its no-issue Requirements-axis weakness from test 2 did not recur here (this PR has an
issue), so this test cannot re-confirm or refute that finding; it can confirm the architecture's
capacity for broader coverage on a target rich enough to reward it.

**v3 — a real second finding, undermined by a factual miss on the primary one.** Independently found
a genuine, distinct race (the keep-alive-timeout path) and had its own verifier catch a real mistake
on a secondary candidate. But its explicit dismissal of the branch that turned out to be the actual
historically-confirmed root cause, on a premise that doesn't hold under direct inspection, is the
kind of error that matters more than its zero-defects test-2 record might suggest: a reviewer that
says "checked, self-healing" about the one thing that actually broke production is a specific failure
mode, not a generic miss.

**v4 — most upstream-accurate fix, most contaminated priority.** Its verifier's rewritten fix
recommendation is the single most technically precise piece of guidance across all four reports, and
its P0 is defensible on the merits — but both were reached with access to the actual outcome, which
none of the other three had. This run cannot be read as evidence that v4's architecture calibrates
severity or specificity better than the others; it can be read as evidence that when a verifier is
given license to consult "history," and real history happens to be sitting in the local clone, it
will use it, for better (accuracy) and for worse (an uncontrolled advantage).

**v5 — cleanest independent replication of the core finding.** Matched v2/v4's branch identification
and mechanism closely, without touching the historical record, and its verifier did the most
additional falsification work of any run that didn't have the answer key (checking two loom tests
against the interleaving and finding both inapplicable, for different, specific reasons). This is the
run this test's core question is best answered by: an architecture with no access to hindsight found
the real, production-confirmed bug through disciplined static tracing alone.

## What test 3 adds to the running recommendation

Tests 1 and 2 recommended advancing v5 with one correction, and running a frozen, blinded evaluation.
Test 3 adds:

1. **Truncate the offline mirror's history to the merge-base before any future run.** This is a
   methodology fix, not a skill fix: v4 did nothing against its own rubric by using local git history
   that was available to it, but a fair comparison requires that no run have access to information a
   contemporaneous reviewer could not have had.
2. **Re-run the "at max threads, notify anyway" branch question specifically against v3**, since its
   miss here is a factual claim about code, not a difference in judgment calibration, and is
   reproducible without any new target.
3. **The "closed pull request" stop rule needs a direct answer**, not a per-run judgment call. If
   these skills are meant to be usable for retrospective/audit review of merged PRs (which this
   three-test research program has now done three times), the rule should say so explicitly, with
   whatever safeguards (no gating authorization, publication disabled by default, etc.) that use case
   needs — rather than leaving each run to decide whether "explicit invocation" is enough license to
   override a stated hard stop.
4. **This test cannot adjudicate the P0-vs-P1 split**, because one of the two positions had
   information the other three did not. A blinded, history-truncated re-run on the same PR would
   settle whether that split is architectural or informational.

## Limits

- **n = 1 per prototype, one target**, same as tests 1 and 2 — no repeated seeds, no statistical
  power.
- **Hindsight contamination in v4**, disclosed and analyzed above; this run's priority-calibration
  result is not blind and should not be generalized from.
- **v3's factual miss is n = 1**, not a demonstrated pattern; it should be checked again before being
  treated as characteristic of that architecture.
- **No loom, build, or test execution was performed** in any run — every finding rests on static
  trace-through plus (for the primary claim) independent corroboration from real-world outcome data,
  not an executed reproduction inside this experiment itself.
- **Model tier differs from test 1** (Sonnet 5 here vs. an Opus-tier 1M-context model there), though
  harness (Claude Code's `Agent` tool) and, for the first time, model *and* harness are held constant
  **within** this test across all four runs — the cleanest within-test comparison of the three tests
  so far.
- **The `plausible` verdict and the published author-facing question-to-author mechanism remain
  under-tested**: this test contributes one more real `question` (v2's), but zero `plausible`
  verifier verdicts — twelve runs across three tests, zero `plausible` instances.
