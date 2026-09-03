# Comparison data — Fable v2a and v5a on `redis/redis#15680`

**2026-09-02. Data only.** This consolidates the local [v2a](v2a-run.md) and [v5a](v5a-run.md)
records. Run conditions and interruptions are in [addendum-2026-09-02.md](addendum-2026-09-02.md);
analysis is in [evaluation.md](evaluation.md). The original and model-matched Sonnet runs live in
the [main test-2 directory](../prototype-runs-2026-09-01-test-2/comparison-data.md).

Both prototypes used `claude-fable-5-1` for the review work and verifier dispatches. V5a's final
11 primary turns switched to Claude Opus 5 after a rate-limit resume; those turns only read the
already-complete follow-up report, selected and validated the payload, and wrote the run record.

## Cost and shape

|                          | v2a                                                                                              | v5a                                                                  |
| ------------------------ | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| Skill commit             | `87c68a9`                                                                                        | `c5f76df`                                                            |
| Architecture             | 2 axis finders + mandatory verifier                                                              | integrated reviewer + clean-verdict verifier + bounded follow-up     |
| Agents on completed path | orchestrator, 2 finders, verifier                                                                | primary, 2 verifiers                                                 |
| Tokens                   | partial: Requirements resumed segment 123,085; verifier 54,052; Code and orchestrator unreported | primary 684,404 across 3 resumed segments; verifiers 81,660 + 77,108 |
| Tool uses                | 100 across recorded roles                                                                        | ~84 across primary and verifiers                                     |
| Wall clock               | split across two rate-limit windows; no single span                                              | 10 h 11 m elapsed, mostly suspended                                  |
| Verifier shape           | one mandatory candidate batch                                                                    | one clean-verdict batch, then one late-candidate batch               |

Neither cost column is usable for architecture ranking. V2a has missing usage; v5a's primary total
is inflated by repeated context reconstruction; both were interrupted.

## Output

|                    | v2a                             | v5a                                                                   |
| ------------------ | ------------------------------- | --------------------------------------------------------------------- |
| Candidates raised  | 2: Requirements 2, Code 0       | 19: 18 primary-ledger rows + 1 late candidate                         |
| Primary survivors  | 2                               | 1 after the clean-verdict aside was traced                            |
| Verifier result    | 2 confirmed                     | clean verdict stands on 18 rows; follow-up confirmed 1 late candidate |
| **Findings**       | **2**: P2 consider, P3 consider | **1**: P2 must-fix                                                    |
| Blocking findings  | 0                               | 1                                                                     |
| Questions          | 2                               | 0                                                                     |
| Observations       | 9 raised; 3 would publish       | 1 published                                                           |
| Coverage           | complete, 5/5; static only      | complete, 5/5; static only                                            |
| **Derived status** | **Approved (advisory)**         | **Changes Requested (advisory)**                                      |

V2a's status reflects an explicit judgment that neither open question could change the verdict. A
stricter “any open question holds” reading would yield Needs Information; the run records that
alternative.

## Finding agreement

| Item                                                                             | v2a                                                    | v5a                                                                             |
| -------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------- |
| `updateShardId()` propagation defeats `shard_changed` at `cluster_legacy.c:5428` | confirmed P2 consider                                  | confirmed P2 must-fix; late candidate                                           |
| `redis.conf` first-sentence scope mismatch                                       | Requirements: confirmed P3 consider; Code: observation | primary: observation; clean verifier upheld                                     |
| Ordinary known-grandmaster sub-replica path                                      | explicitly acquitted                                   | primary near-miss refuted; later distinguished from failing unknown-master path |
| Test timing under `cluster-node-timeout 1000`                                    | open question plus observation                         | examined several test concerns; timing not raised                               |
| Lineage against redis #15530 / Valkey #885/#944                                  | open question; unavailable offline                     | unavailable context, not raised                                                 |

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

V2a's verifier and both v5a verifiers reconstructed the relevant branches independently. The new
tests start with all nodes known and do not cover this packet-ordering path.

## Verification mechanics

| Mechanism                            | Observed result                                                                                             |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| v2a mandatory candidate verification | confirmed both Requirements findings; Code returned none                                                    |
| v5a G3 clean-verdict batch           | upheld all 18 dispositions but used its one aside to identify the unknown-master branch                     |
| v5a primary follow-through           | converted the aside into a full consequence trace and late must-fix candidate                               |
| v5a N3 follow-up                     | confirmed the candidate and kept P2/must-fix                                                                |
| v5a N2 fix-sufficiency               | evaluated all six `clusterSetMaster()` callers and widened the fix to preserve legitimate shard convergence |

G3 was decisive even though its formal verdict said “clean verdict stands.” Without the aside, the
defect remained acquitted; without N3, the late candidate could not have been independently verified.

## No-issue and question handling

V2a exercised its no-issue rule: the Requirements finder created a 16-row body-claims ledger,
tested stated scope boundaries, disclosed issue alignment unavailable, and inferred no requirement
from the diff. Two statically unresolved matters bypassed candidate verification and became
questions. V5a also stated issue alignment unavailable but resolved every candidate statically.

## Cross-model replication

|                        | Fable v2a                          | Sonnet v2a                   | Fable v5a          | Sonnet v5a                    |
| ---------------------- | ---------------------------------- | ---------------------------- | ------------------ | ----------------------------- |
| Defect                 | found                              | missed after false acquittal | found              | missed after false refutation |
| Findings               | 2                                  | 0                            | 1                  | 0                             |
| Questions              | 2                                  | 0                            | 0                  | 0                             |
| Status                 | Approved                           | Approved                     | Changes Requested  | Approved                      |
| Clean-verdict verifier | not applicable; candidates existed | skipped by v2a rule          | decisive via aside | ran and reinforced the error  |

This is evidence of run/model sensitivity, not a general Fable-versus-Sonnet ranking. Target 3
supplies a counterexample to any simple model ordering.

## Data-quality caveats

- V2a's original orchestrator was lost after finder dispatch; the session compiled the verifier and
  final status from saved, byte-identical reports.
- V5a resumed three times and crossed models only after review and verification were complete.
- Tests were reviewed statically and never executed.
- V2a/v5a are development-set designs, one run each.
