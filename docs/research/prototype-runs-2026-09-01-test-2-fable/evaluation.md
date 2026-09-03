# Evaluating the Fable v2a/v5a retest on `redis/redis#15680`

**2026-09-02.** This evaluates two patched review architectures on the pinned Redis pull request
that the original v2–v5 comparison and two human reviewers had called clean. Both Fable runs found
the same previously unreported defect.

Sources: [README](README.md), [v2a](v2a-run.md), [v5a](v5a-run.md),
[run addendum](addendum-2026-09-02.md), and [comparison data](comparison-data.md). The later Sonnet
reruns are evaluated in the [main test-2 record](../prototype-runs-2026-09-01-test-2/evaluation.md).

## Conclusion

**Both architectures independently found the same real control-flow gap; v5a produced the stronger
review outcome and the more instructive mechanism trace.** V2a published the defect as P2
`consider`, leaving the status Approved. V5a published it as P2 `must-fix`, yielding Changes
Requested, and its verifier generalized the fix across all `clusterSetMaster()` callers.

V5a's advantage on this run came from two mechanisms working together. Its primary initially
acquitted a near-miss. The high-risk clean-verdict verifier noticed the missing unknown-master
branch as an aside; the primary traced the consequence; a bounded follow-up verifier confirmed the
late candidate. The formal clean verdict did not reopen anything, so the aside channel—not the
declared verdict—carried the decisive information.

V2a provides different value. Its separate Requirements finder found the code defect and the
`redis.conf` scope mismatch, exercised the no-issue claims ledger, and surfaced two legitimate
questions. Its Code finder returned no candidates. The result shows why the Requirements axis can
increase recall, but also why priority and action must be independent: a demonstrated failover-gap
against the pull request's own coverage claim was not made blocking.

Neither cost record is usable, and neither run establishes a model or architecture ranking. Both
were development-set, interrupted executions on one target. Their shared defect trace nevertheless
stands on its evidence and overturns the original “clean target” interpretation.

## Method

Both runs reviewed head `c54fa4184` against merge-base `065d3970`, five changed files, no
originating issue, and the same prior approval/LGTM packet. The offline mirror was truncated so no
newer commit was reachable. Network, builds, and tests were forbidden.

Every review and verifier dispatch ran on `claude-fable-5-1`. V5a's final report-assembly segment
switched to Opus after a resume, but the candidate ledger, both verifier prompts and results, and
context digest already existed. That caveat matters for strict model accounting, not for who found
or verified the defect.

Both runs suffered session rate limits. Saved prompts and reports were preserved, clone cleanliness
was rechecked, and v2a's finder `support` was mechanically removed before verification. Findings
remain interpretable; active time and token totals do not.

## Why the defect is credible

The defect is not inferred from agreement alone. Each report gives a checkable state sequence:

- the new master's ID does not resolve locally, leaving the demoted sender's `slaveof` pointer
  null;
- `updateShardId()` tests pointer nullness rather than role flags and propagates the new shard ID to
  attached replicas;
- the sub-replica's ID changes before the flattening safeguard calls `clusterSetMaster()`;
- the newly added equality guard therefore reports no shard change; and
- stale cached-master state and the old disconnection timestamp remain eligible for failover logic.

The v2a verifier reconstructed this from the code without finder `support`. V5a's clean verifier
found the missing branch independently, and its follow-up verifier reconstructed trigger, impact,
and sibling-call-site exposure. Three verifier passes across two architectures converge on the same
mechanism.

The evidence remains static: tests were forbidden and no dynamic reproduction was run. That limits
frequency estimates, not the existence of the reachable path.

## Severity disagreement

V2a kept P2 `consider` because the trigger requires a node-discovery ordering and a failover before
first synchronization. V5a kept P2 `must-fix` because the result is a demonstrated data-integrity
failure on a path the pull request explicitly claims to protect.

V5a's action is better calibrated. Trigger rarity can lower priority without making a proven stale-
history promotion path optional. Action should answer whether merge depends on correcting the
behavior; priority should answer urgency/frequency. P2/must-fix expresses that distinction.

## G3 and N3

The clean-verdict mechanism justified its cost, but its output vocabulary was awkward. The verifier
returned “clean verdict stands” for every ledger row and did not formally reopen the near-miss. Its
one observation aside identified the exact missing branch but stopped before tracing consequence.
The primary had to recognize the aside as candidate-shaped and do the remaining work.

N3 was then load-bearing. The candidate appeared after the first batch had already completed. A
strict one-batch workflow would either discard a real blocker or publish it without independent
confirmation. One bounded follow-up preserved independence without creating an unbounded review
loop.

The design implication is to let a clean-verdict verifier formally return “reopen” whenever an
aside contradicts a decisive premise. Valuable discoveries should not depend on the primary
promoting an observation against the nominal verdict.

## Fix sufficiency

V5a's follow-up verifier did more than confirm the bug. It treated the candidate as an invariant
failure, enumerated all six `clusterSetMaster()` callers, distinguished the intended convergence
paths from the failing pre-propagation path, and corrected the repair so legitimate shard-ID updates
would not be broken.

That is the right verifier role for state-machine findings: not just “does this example fail?” but
“what invariant failed, where else is it enforced, and does the proposed fix close the class without
breaking sibling paths?” The run supplies direct evidence for keeping N2.

## V2a's no-issue path

Unlike v2, v2a did not disable Requirements review merely because no issue was linked. It treated
the pull-request body as the specification surrogate, separated background claims from 13 checkable
claims, tested scope boundaries, and disclosed issue alignment unavailable. That is a clear
contract improvement.

It also produced two honest questions: external lineage could not be checked offline, and static
reading could not settle timing reliability under the configured timeout. The latter could become a
test-flakiness consideration but not change the core correctness verdict, which is why the run kept
Approved despite the questions.

The body-claims channel is also how v2a framed the sub-replica gap as a Requirements finding. This
is evidence that a Requirements pass can discover a code defect when it tests behavioral claims
rather than only documentation compliance.

## The `redis.conf` split

Both axes noticed that the first new configuration sentence applies generally to never-synchronized
replicas while the code's reset is cross-shard-only. V2a's Requirements axis made it P3 `consider`;
its Code axis made it an observation. V5a chose Observation.

Observation is the better calibration. Same-shard history remains valid, so the code is deliberate
and correct; the text is only broader than its implementation. A bounded, explicitly non-actionable
channel preserves the useful fact without manufacturing a merge concern.

## Contrast with the Sonnet rerun

Both Sonnet reruns reached the right hypothesis and rejected it. V2a's finder checked only that the
direct update targeted `sender`, not the propagation from `sender` to attached replicas. V5a's
primary asserted the sender's `slaveof` pointer was always set, and its clean-verdict verifier
reinforced that error. The difference does not retract the Fable finding because the Fable traces
contain the missing branch and were independently verified.

Nor does it prove Fable is generally stronger. On the Tokio target, Sonnet v5a found the known
production regression and generated the best fix in the expanded corpus. The responsible conclusion
is target/run variance and inadequate replication, not a model leaderboard.

## Prototype verdicts

**V2a — useful breadth, weak action calibration.** It exercised the repaired no-issue path, found
both material facts through Requirements, and surfaced two questions. The Code axis added no
finding, and the proven failover defect remained optional.

**V5a — stronger result through a fragile route.** It blocked the defect, used N3 correctly, and
improved the fix at invariant level. The primary and formal clean-verdict result initially missed
the bug; success depended on promoting an aside.

## Recommendation

Carry forward v5a's integrated shape, clean-verdict ledger check, bounded follow-up, and N2
fix-sufficiency analysis. Add v2a's body-claims/no-issue discipline and question channel. Tighten
clean-verdict output so a contradicted acquittal is formally reopened, and make high-risk
Requirements “met” rows eligible for verification even when other findings survive.

Then rerun this target with repeated, explicit-model seeds. Score the exact unknown-master branch,
action (`must-fix` versus `consider`), and whether the verifier corrects a seeded false acquittal.
Do not compare costs until runs complete without interruption under one metering boundary.
