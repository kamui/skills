# Evaluating six agentic code-review runs after a later defect discovery

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

## Conclusion

The most useful architectural findings are therefore negative and specific:

1. candidate-only verification cannot catch a false acquittal when nothing survives;
2. a clean-verdict verifier can still agree with a false acquittal when it does not challenge the
   decisive branch precondition;
3. status and complete-coverage claims can agree across every run while the code-level conclusion
   is wrong; and
4. one run per model/skill is too little evidence for either clean approval or model ranking.

## Controlled method and cohort boundaries

Every run used the same pinned code identity:

| Input             | Pinned value                                             |
| ----------------- | -------------------------------------------------------- |
| Pull request      | `redis/redis#15680`, merged at run time                  |
| Head              | `c54fa4184e7db1ea30c91916f6c0aeb12b5c3f61`               |
| Base / merge-base | `065d397030712fe216e795720ae0affd3211212c` on `unstable` |
| Diff              | 5 files, +401/−1, two commits                            |
| Originating issue | none                                                     |
| Prior state       | one approval and a detailed technical LGTM               |
| Execution         | network, builds, and tests forbidden; static review only |

The original cohort used GLM-5.3-Flash at High reasoning under opencode. The Sonnet retest used
`claude-sonnet-5` at default reasoning under `t3code`. The Fable round used
`claude-fable-5-1` and suffered rate-limit interruptions. Architecture comparisons are meaningful
within a cohort; tokens and capability are not comparable across them.

The later skills are development-set: their authors had seen the original results, although the
specific `updateShardId()` defect had not been reported there. This makes mechanism observations
useful but prevents a holdout-quality claim.

## The defect the original evaluation missed

The new guard in `clusterSetMaster()` computes whether `myself->shard_id` differs from the new
master's shard. On the ordinary path that happens before `myself` adopts the new shard and works.
The sub-replica safeguard has another ordering:

1. a demoted master sends a packet naming a new master the receiving node does not yet know;
2. the lookup fails, so the sender remains slave-flagged with `sender->slaveof == NULL`;
3. `updateShardId(sender, ...)` treats `slaveof == NULL` as the propagation case and rewrites the
   shard ID of attached replicas, including `myself`;
4. when the grandmaster later becomes known, the safeguard calls `clusterSetMaster()` for
   `myself`; and
5. the new guard compares the already-rewritten shard ID with the grandmaster and gets false, so it
   skips both cached-master discard and `repl_down_since = 0`.

The shared Sonnet error was the assertion that the demotion handler _always_ sets
`sender->slaveof` before calling `updateShardId()`. It does only when the named master is already
known. Both Sonnet reports read the success branch and failed to reason through the lookup-failure
branch that makes the safeguard necessary.

## Why the unanimous approval is misleading

The original four runs explored 29 candidates and dropped all of them. That still demonstrates
restraint: they did not publish speculative findings about discard ordering, sentinel semantics, or
same-shard behavior. It does not demonstrate correctness, because candidate breadth did not include
the failing state transition.

The Sonnet retest is more revealing:

“Complete coverage” means every file and required check has an evidence-backed disposition. It does
not mean every disposition is correct. This target is the clearest example in the corpus of process
completeness and substantive correctness diverging.

## Verification: skipped, successful, and unsuccessful

The expanded corpus exercises three verification shapes on the same defect.

### Clean-verdict failure

Sonnet v5a sent its full ledger to a clean-verdict verifier because the change touches failover and
data integrity. The verifier revisited the candidate and strengthened the false argument. This shows
that simply broadening verifier input from survivors to the ledger does not guarantee correction.
The prompt needs an explicit adversarial task: identify the weakest premise, enumerate the opposite
branch of every conditional it relies on, and construct or refute the full state transition.

### Clean-verdict success plus follow-up

Fable v5a's clean-verdict batch upheld the ledger too, but its permitted observation aside noticed
the unresolved-master branch. The primary traced the consequence, admitted a late must-fix
candidate, and the one permitted follow-up batch confirmed it. Both G3 and N3 were load-bearing.
The fact emerged through an aside rather than a formal re-open, suggesting the verifier output
contract may be classifying its most valuable result under the wrong channel.

These success and failure cases occurred with the same skill and target. Verifier presence is not a
quality metric; what the verifier is required to falsify is.

## The no-issue path

That is a genuine improvement in contract design. It did not save this review because the claim
about sub-replica coverage was marked met on bad static reasoning. The lesson is not to remove the
body-claims ledger; it is to treat high-risk “met” rows as acquittals eligible for adversarial
verification.

## The `redis.conf` observation

The configuration paragraph says generally that a replica which has not completed first sync with
its current master is considered disconnected since forever. The implementation resets
`repl_down_since` only on cross-shard re-point; same-shard re-points deliberately retain valid
history.

This validates the Observations channel even though it does not compensate for the missed blocker.

## Prior review state

The existing approval and detailed LGTM did not make any run stop early. Several original runs and
both retest architectures independently re-derived the `freeClient()` →
`replicationCacheMaster()` ordering and correctly confirmed it. The failure lived in the LGTM's
broader claim that placing the guard inside `clusterSetMaster()` covers every re-point path. The
placement is appropriate; the predicate can already have been corrupted before that call.

This is useful evidence against a simplistic anchoring explanation. Human and agent reviewers all
validated the prominent happy-path ordering and missed the less obvious precondition failure.

## Model and run sensitivity

On Fable, both prototypes found the defect. On Sonnet, both reached and acquitted it. That does not
license a general model ranking:

- there is one target and one observation per model/prototype cell;
- target 3 supplies the opposite kind of evidence, where Sonnet v5a finds the shipped defect;
- the Fable executions were interrupted; and
- architecture, model sampling, and the exact reasoning path remain entangled.

It does license a methodological conclusion: absence must be replicated, especially before an
unattended reviewer emits a clean approval on a high-risk change.

## Prototype verdicts

**V2 — careful on the visible paths, structurally weak without an issue.** It made the best original
`redis.conf` observation but switched off Requirements review and missed the real defect.

**V3 — widest original candidate set, same blind spot.** Eleven candidates and explicit
falsification did not reach the failing propagation path. Its idea of verifying a high-risk clean
verdict was correct; later evidence shows such a verifier must do more than reread conclusions.

**V4 — strongest body-claim ledger in the original round, still wrong.** Its complete static review
and extra arithmetic checks demonstrate breadth without decisive state-machine coverage.

**V5 — efficient clean path, no evidence of safety here.** Its output was disciplined but no
verifier ran and the target later proved defect-bearing.

**V5a — best mechanisms, inconsistent execution quality.** The Fable run's G3/N3 chain found and
confirmed the defect as must-fix. The Sonnet run's G3 check examined the same row and made the wrong
case more confident. This is evidence for the pipeline shape and against assuming one execution is
reliable.

## Recommendation

Keep the v5a-style integrated reviewer, bounded Observations, high-risk clean-verdict check, and one
follow-up batch. Change the verification policy in two ways:

1. verify high-risk acquittals even when another candidate survives, rather than restricting ledger
   review to a zero-finding outcome; and
2. require the verifier to attack branch preconditions and construct the complete state transition,
   not merely confirm cited lines and call-site order.

For evaluation, run repeated seeds on this pinned target with the defect pre-registered and the
mirror truncated. Score whether the exact propagation branch is found, whether the action is
blocking, and whether the verifier corrects a seeded false acquittal. Keep model identity explicit
on every agent and report confidence intervals or at least replicate counts. Until then, no clean
verdict from a single run on a failover/data-integrity change should be treated as strong evidence
of absence.

## Limits
