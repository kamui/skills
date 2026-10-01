# Comparison data — v3–v5 plus Sonnet v5a on `redis/redis#15680`

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

## Cost and shape — original cohort

|                | v3                      | v4                      | v5                      |
| -------------- | ----------------------- | ----------------------- | ----------------------- |
| Agents spawned | 1                       | 1                       | 1                       |
| Tokens         | unavailable             | unavailable             | unavailable             |
| Tool uses      | 35                      | 30                      | 37                      |
| Wall clock     | ~19 min                 | ~22 min                 | ~6 min                  |
| Verifier       | skipped; zero survivors | skipped; zero survivors | skipped; zero survivors |

Wall clock did not track candidates, tools, or architecture and is not a cost measure.

## Cost and shape — Sonnet retest

|                | v5a                                            |
| -------------- | ---------------------------------------------- |
| Architecture   | integrated reviewer + clean-verdict verifier   |
| Run agents     | primary + 1 verifier                           |
| Primary tokens | 188,196                                        |
| Child tokens   | verifier 69,277                                |
| Reported tools | primary 71; verifier 39                        |
| Wall clock     | primary wrapper ~22 min; verifier ~6 min       |
| Verifier       | G3 clean-verdict batch; `clean verdict stands` |

These numbers are not comparable to the original cohort. Even within this table, primary wrappers
and child meters are listed separately to avoid silently changing the accounting boundary.

## Output

|                             | v3                   | v4             | v5             | v5a Sonnet                                       |
| --------------------------- | -------------------- | -------------- | -------------- | ------------------------------------------------ |
| Candidates raised           | 11                   | 10             | 8              | 5                                                |
| Pre-publication disposition | 7 refuted, 4 dropped | 10 dropped     | 8 dropped      | 4 refuted, 1 observation; verifier upheld ledger |
| **Findings**                | **0**                | **0**          | **0**          | **0**                                            |
| Questions                   | 0                    | 0              | 0              | 0                                                |
| Observations                | none published       | none published | none published | 2                                                |
| Coverage                    | complete, 5/5        | complete, 5/5  | complete, 5/5  | complete, 5/5                                    |
| **Status**                  | **Approved**         | **Approved**   | **Approved**   | **Approved**                                     |

All statuses are advisory and all reviews were data-only. Output unanimity is not accuracy: the
separate Fable round found a confirmed defect in this same pinned head.

## Material-theme agreement

| Theme                                                                                   | v3                                   | v4                      | v5                    | v5a Sonnet                                         |
| --------------------------------------------------------------------------------------- | ------------------------------------ | ----------------------- | --------------------- | -------------------------------------------------- |
| `updateShardId()` propagation can pre-set `myself->shard_id`, defeating `shard_changed` | not raised                           | not raised              | not raised            | **raised, wrongly refuted; clean verifier upheld** |
| `redis.conf` first sentence is broader than the cross-shard-only reset                  | called exact                         | called exact            | called exact          | observation, verifier upheld                       |
| Discard-after-`replicationSetMaster` ordering / stale cache                             | refuted                              | falsified               | dropped               | dropped                                            |
| `repl_down_since = 0` downstream semantics                                              | refuted                              | falsified               | dropped               | dropped                                            |
| Same-shard re-point preserves partial resync                                            | refuted candidate / behavior cleared | non-goal verified       | dropped; non-goal met | observation explains doc mismatch                  |
| Manual failover bypass                                                                  | refuted                              | falsified, pre-existing | dropped, pre-existing | checked in call-site sweep                         |
| Removed test assertion weakens one negative case                                        | inspected                            | dropped                 | dropped               | verifier nuance → observation                      |

The first row is decisive. The Fable round later reconstructed the exact path and three fresh
verifiers confirmed it. The two Sonnet runs reached the hypothesis but made the same false premise:
they assumed the demoted sender always has `slaveof` set before `updateShardId()`. When the new
master is unknown, `sender->slaveof` remains `NULL`; propagation reaches the attached sub-replica
before its own `clusterSetMaster()` call.

## Cross-model result on the confirmed defect

|                     | Fable v5a                                   | Sonnet v5a                                    |
| ------------------- | ------------------------------------------- | --------------------------------------------- |
| Candidate treatment | late candidate from clean-verifier aside    | primary candidate, then refuted               |
| Fresh verification  | clean batch exposed it; follow-up confirmed | clean batch examined it and upheld refutation |
| Publication         | P2 must-fix                                 | absent                                        |
| Status              | Changes Requested                           | Approved                                      |

This table measures run/model sensitivity, not model rank. One target and one sample per cell cannot
support “Fable is better.” It does establish that a clean result from one run is weak evidence of
absence.

## No-issue handling

No originating issue exists. The run-native behavior changed materially across generations:

|            | Requirements treatment                                                           |
| ---------- | -------------------------------------------------------------------------------- |
| v3         | issue alignment unavailable; structured body-claims ledger                       |
| v4         | issue alignment unavailable; body claims plus non-goal ledger                    |
| v5         | issue alignment unavailable; body claims plus non-goal ledger                    |
| v5a Sonnet | integrated body-intent review; unavailable stated                                |

## Verification behavior

The clean-verdict mechanism is exercised here in both success and failure. Dispatching a verifier is
not sufficient; the verifier must actively challenge the decisive premise of each high-risk
acquittal.

## Data correction relative to the original synthesis

The original `comparison-data.md` described this target as a clean change with unanimous restraint.
That was a reasonable statement from the evidence available on 2026-09-01, but it is no longer a
valid description of the expanded record. The Fable finding is not retracted by later Sonnet misses:
three independent verifiers reconstructed the path from code. This rewrite treats the target as a
defect-bearing pull request whose defect was missed by all six runs in this directory.
