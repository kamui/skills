# Evaluating the Fable v5a retest on `redis/redis#15680`

## Conclusion

V5a's advantage on this run came from two mechanisms working together. Its primary initially
acquitted a near-miss. The high-risk clean-verdict verifier noticed the missing unknown-master
branch as an aside; the primary traced the consequence; a bounded follow-up verifier confirmed the
late candidate. The formal clean verdict did not reopen anything, so the aside channel—not the
declared verdict—carried the decisive information.

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

## Why the defect is credible

The defect is not inferred from agreement alone. Each report gives a checkable state sequence:

- the new master's ID does not resolve locally, leaving the demoted sender's `slaveof` pointer
  null;
- `updateShardId()` tests pointer nullness rather than role flags and propagates the new shard ID to
  attached replicas;
- the sub-replica's ID changes before the flattening safeguard calls `clusterSetMaster()`;
- the newly added equality guard therefore reports no shard change; and
- stale cached-master state and the old disconnection timestamp remain eligible for failover logic.

The evidence remains static: tests were forbidden and no dynamic reproduction was run. That limits
frequency estimates, not the existence of the reachable path.

## Severity disagreement

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

## The `redis.conf` split

Observation is the better calibration. Same-shard history remains valid, so the code is deliberate
and correct; the text is only broader than its implementation. A bounded, explicitly non-actionable
channel preserves the useful fact without manufacturing a merge concern.

## Contrast with the Sonnet rerun

Nor does it prove Fable is generally stronger. On the Tokio target, Sonnet v5a found the known
production regression and generated the best fix in the expanded corpus. The responsible conclusion
is target/run variance and inadequate replication, not a model leaderboard.

## Prototype verdicts

**V5a — stronger result through a fragile route.** It blocked the defect, used N3 correctly, and
improved the fix at invariant level. The primary and formal clean-verdict result initially missed
the bug; success depended on promoting an aside.

## Recommendation

Then rerun this target with repeated, explicit-model seeds. Score the exact unknown-master branch,
action (`must-fix` versus `consider`), and whether the verifier corrects a seeded false acquittal.
Do not compare costs until runs complete without interruption under one metering boundary.
