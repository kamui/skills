# Review experiment data

Both prototypes used `claude-fable-5-1` for the review work and verifier dispatches. V5a's final
11 primary turns switched to Claude Opus 5 after a rate-limit resume; those turns only read the
already-complete follow-up report, selected and validated the payload, and wrote the run record.

## Cost and shape

|                          | v5a                                                                  |
| ------------------------ | -------------------------------------------------------------------- |
| Skill commit             | `c5f76df`                                                            |
| Architecture             | integrated reviewer + clean-verdict verifier + bounded follow-up     |
| Agents on completed path | primary, 2 verifiers                                                 |
| Tokens                   | primary 684,404 across 3 resumed segments; verifiers 81,660 + 77,108 |
| Tool uses                | ~84 across primary and verifiers                                     |
| Wall clock               | 10 h 11 m elapsed, mostly suspended                                  |
| Verifier shape           | one clean-verdict batch, then one late-candidate batch               |

## Output

|                    | v5a                                                                   |
| ------------------ | --------------------------------------------------------------------- |
| Candidates raised  | 19: 18 primary-ledger rows + 1 late candidate                         |
| Primary survivors  | 1 after the clean-verdict aside was traced                            |
| Verifier result    | clean verdict stands on 18 rows; follow-up confirmed 1 late candidate |
| **Findings**       | **1**: P2 must-fix                                                    |
| Blocking findings  | 1                                                                     |
| Questions          | 0                                                                     |
| Observations       | 1 published                                                           |
| Coverage           | complete, 5/5; static only                                            |
| **Derived status** | **Changes Requested (advisory)**                                      |

## Finding agreement

| Item                                                                             | v5a                                                                             |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `updateShardId()` propagation defeats `shard_changed` at `cluster_legacy.c:5428` | confirmed P2 must-fix; late candidate                                           |
| `redis.conf` first-sentence scope mismatch                                       | primary: observation; clean verifier upheld                                     |
| Ordinary known-grandmaster sub-replica path                                      | primary near-miss refuted; later distinguished from failing unknown-master path |
| Test timing under `cluster-node-timeout 1000`                                    | examined several test concerns; timing not raised                               |
| Lineage against redis #15530 / Valkey #885/#944                                  | unavailable context, not raised                                                 |

Both prototypes independently re-derived the prior LGTM's cache-ordering claims from source. V5a
then falsified the LGTM's broader statement that placing the guard inside `clusterSetMaster()`
covers every re-point path: the call site is appropriate, but its predicate can already be stale.

## The confirmed defect

The convergent path is:

1. a demoted master names a new master the receiving node does not yet know;
2. its `slaveof` pointer therefore remains `NULL`;
3. `updateShardId()` uses `slaveof == NULL` as its propagation condition and rewrites the shard ID
   of attached replicas, including the sub-replica under review;
4. the new master becomes known and the flattening safeguard calls `clusterSetMaster()`; and
5. `shard_changed` compares equal IDs and skips cache discard and the `repl_down_since` reset.

## Verification mechanics

| Mechanism                            | Observed result                                                                                             |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| v5a G3 clean-verdict batch           | upheld all 18 dispositions but used its one aside to identify the unknown-master branch                     |
| v5a primary follow-through           | converted the aside into a full consequence trace and late must-fix candidate                               |
| v5a N3 follow-up                     | confirmed the candidate and kept P2/must-fix                                                                |
| v5a N2 fix-sufficiency               | evaluated all six `clusterSetMaster()` callers and widened the fix to preserve legitimate shard convergence |

G3 was decisive even though its formal verdict said “clean verdict stands.” Without the aside, the
defect remained acquitted; without N3, the late candidate could not have been independently verified.

## Cross-model replication

|                        | Fable v5a          | Sonnet v5a                    |
| ---------------------- | ------------------ | ----------------------------- |
| Defect                 | found              | missed after false refutation |
| Findings               | 1                  | 0                             |
| Questions              | 0                  | 0                             |
| Status                 | Changes Requested  | Approved                      |
| Clean-verdict verifier | decisive via aside | ran and reinforced the error  |

This is evidence of run/model sensitivity, not a general Fable-versus-Sonnet ranking. Target 3
supplies a counterexample to any simple model ordering.

## Data-quality caveats
