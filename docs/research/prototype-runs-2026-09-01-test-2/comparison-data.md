# Comparison data — v2–v5 plus Sonnet v2a/v5a on `redis/redis#15680`

> **Promotion status:** “v5” is the historical prototype name used by this record. PR #17 promoted
> that workflow to `skills/code-review-publish` on `main`; new work should invoke
> `/code-review-publish` without the `-5` suffix.

**2026-09-01–03. Data only.** This consolidates every run record in this directory:
[v2](v2-run.md), [v3](v3-run.md), [v4](v4-run.md), [v5](v5-run.md), [v2a](v2a-run.md), and
[v5a](v5a-run.md). Analysis is in [evaluation.md](evaluation.md). The materially different
[Fable v2a/v5a round](../prototype-runs-2026-09-01-test-2-fable/comparison-data.md) is reported
separately and referenced here because it established the defect the runs in this directory missed.

## Comparison boundaries

| Cohort               | Runs           | Model / harness                        | Metering                                               |
| -------------------- | -------------- | -------------------------------------- | ------------------------------------------------------ |
| Original             | v2, v3, v4, v5 | GLM-5.3-Flash, High / opencode         | no token data; tool counts self-reported               |
| Sonnet retest        | v2a, v5a       | `claude-sonnet-5`, default / `t3code`  | per-agent token data available, with nested boundaries |
| Separate Fable round | v2a, v5a       | `claude-fable-5-1`, default / `t3code` | interrupted; partial/inflated totals                   |

Only within-cohort behavioral comparisons are controlled. The target, model, harness, and meter all
changed between the original and retest cohorts. V2a/v5a are development-set prototypes whose
authors had seen this target's earlier results.

## Cost and shape — original cohort

|                | v2                       | v3                      | v4                      | v5                      |
| -------------- | ------------------------ | ----------------------- | ----------------------- | ----------------------- |
| Agents spawned | 1; Requirements axis N/A | 1                       | 1                       | 1                       |
| Tokens         | unavailable              | unavailable             | unavailable             | unavailable             |
| Tool uses      | ~46                      | 35                      | 30                      | 37                      |
| Wall clock     | ~9 min                   | ~19 min                 | ~22 min                 | ~6 min                  |
| Verifier       | skipped; no candidates   | skipped; zero survivors | skipped; zero survivors | skipped; zero survivors |

Wall clock did not track candidates, tools, or architecture and is not a cost measure.

## Cost and shape — Sonnet retest

|                | v2a                                                     | v5a                                            |
| -------------- | ------------------------------------------------------- | ---------------------------------------------- |
| Architecture   | 2 parallel finders; verifier only if a candidate exists | integrated reviewer + clean-verdict verifier   |
| Run agents     | primary orchestrator + 2 finders                        | primary + 1 verifier                           |
| Primary tokens | 147,212                                                 | 188,196                                        |
| Child tokens   | Code 81,653; Requirements 88,942                        | verifier 69,277                                |
| Reported tools | finders 42 + 32; primary not enumerated                 | primary 71; verifier 39                        |
| Wall clock     | finder phase ~8 min; ~15–20 min estimated end to end    | primary wrapper ~22 min; verifier ~6 min       |
| Verifier       | skipped by rule; both finders returned zero candidates  | G3 clean-verdict batch; `clean verdict stands` |

These numbers are not comparable to the original cohort. Even within this table, primary wrappers
and child meters are listed separately to avoid silently changing the accounting boundary.

## Output

|                             | v2                                    | v3                   | v4             | v5             | v2a Sonnet                                          | v5a Sonnet                                       |
| --------------------------- | ------------------------------------- | -------------------- | -------------- | -------------- | --------------------------------------------------- | ------------------------------------------------ |
| Candidates raised           | 0                                     | 11                   | 10             | 8              | 0                                                   | 5                                                |
| Pre-publication disposition | —                                     | 7 refuted, 4 dropped | 10 dropped     | 8 dropped      | finder ledgers: 23 acquittal/observation rows total | 4 refuted, 1 observation; verifier upheld ledger |
| **Findings**                | **0**                                 | **0**                | **0**          | **0**          | **0**                                               | **0**                                            |
| Questions                   | 0                                     | 0                    | 0              | 0              | 0                                                   | 0                                                |
| Observations                | no formal section; one important note | none published       | none published | none published | 2                                                   | 2                                                |
| Coverage                    | complete, 5/5                         | complete, 5/5        | complete, 5/5  | complete, 5/5  | complete, 5/5                                       | complete, 5/5                                    |
| **Status**                  | **Approved**                          | **Approved**         | **Approved**   | **Approved**   | **Approved**                                        | **Approved**                                     |

All statuses are advisory and all reviews were data-only. Output unanimity is not accuracy: the
separate Fable round found a confirmed defect in this same pinned head.

## Material-theme agreement

| Theme                                                                                   | v2                    | v3                                   | v4                      | v5                    | v2a Sonnet                      | v5a Sonnet                                         |
| --------------------------------------------------------------------------------------- | --------------------- | ------------------------------------ | ----------------------- | --------------------- | ------------------------------- | -------------------------------------------------- |
| `updateShardId()` propagation can pre-set `myself->shard_id`, defeating `shard_changed` | not raised            | not raised                           | not raised              | not raised            | **examined, wrongly acquitted** | **raised, wrongly refuted; clean verifier upheld** |
| `redis.conf` first sentence is broader than the cross-shard-only reset                  | note to orchestrator  | called exact                         | called exact            | called exact          | missed                          | observation, verifier upheld                       |
| Discard-after-`replicationSetMaster` ordering / stale cache                             | checked, acquitted    | refuted                              | falsified               | dropped               | acquitted                       | dropped                                            |
| `repl_down_since = 0` downstream semantics                                              | checked, acquitted    | refuted                              | falsified               | dropped               | acquitted                       | dropped                                            |
| Same-shard re-point preserves partial resync                                            | checked               | refuted candidate / behavior cleared | non-goal verified       | dropped; non-goal met | body claim marked met           | observation explains doc mismatch                  |
| Manual failover bypass                                                                  | checked, pre-existing | refuted                              | falsified, pre-existing | dropped, pre-existing | acquitted                       | checked in call-site sweep                         |
| Removed test assertion weakens one negative case                                        | noted                 | inspected                            | dropped                 | dropped               | observation                     | verifier nuance → observation                      |

The first row is decisive. The Fable round later reconstructed the exact path and three fresh
verifiers confirmed it. The two Sonnet runs reached the hypothesis but made the same false premise:
they assumed the demoted sender always has `slaveof` set before `updateShardId()`. When the new
master is unknown, `sender->slaveof` remains `NULL`; propagation reaches the attached sub-replica
before its own `clusterSetMaster()` call.

## Cross-model result on the confirmed defect

|                     | Fable v2a              | Sonnet v2a               | Fable v5a                                   | Sonnet v5a                                    |
| ------------------- | ---------------------- | ------------------------ | ------------------------------------------- | --------------------------------------------- |
| Candidate treatment | Requirements candidate | finder acquittal         | late candidate from clean-verifier aside    | primary candidate, then refuted               |
| Fresh verification  | confirmed              | skipped; zero candidates | clean batch exposed it; follow-up confirmed | clean batch examined it and upheld refutation |
| Publication         | P2 consider            | absent                   | P2 must-fix                                 | absent                                        |
| Status              | Approved               | Approved                 | Changes Requested                           | Approved                                      |

This table measures run/model sensitivity, not model rank. One target and one sample per cell cannot
support “Fable is better.” It does establish that a clean result from one run is weak evidence of
absence.

## No-issue handling

No originating issue exists. The run-native behavior changed materially across generations:

|            | Requirements treatment                                                           |
| ---------- | -------------------------------------------------------------------------------- |
| v2         | axis declared `Not applicable`; body checks happened informally in Code notes    |
| v3         | issue alignment unavailable; structured body-claims ledger                       |
| v4         | issue alignment unavailable; body claims plus non-goal ledger                    |
| v5         | issue alignment unavailable; body claims plus non-goal ledger                    |
| v2a Sonnet | Requirements finder ran; 11 checkable body claims marked met; unavailable stated |
| v5a Sonnet | integrated body-intent review; unavailable stated                                |

V2a repairs v2's architectural collapse on issueless pull requests. The resulting ledger is more
auditable, but here one “met” conclusion depends on the false sub-replica acquittal.

## Verification behavior

- No verifier ran in the original four runs.
- V2a Sonnet skipped verification by its explicit zero-candidate rule. The false acquittal therefore
  had no independent reader.
- V5a Sonnet did run its high-risk clean-verdict check over all five dispositions. It inspected the
  relevant row, repeated the missing branch-precondition error, and strengthened the refutation.
- Fable v5a ran the same mechanism over the same target and found the missing branch through the
  verifier's aside channel; its bounded follow-up then confirmed the candidate.

The clean-verdict mechanism is exercised here in both success and failure. Dispatching a verifier is
not sufficient; the verifier must actively challenge the decisive premise of each high-risk
acquittal.

## Data correction relative to the original synthesis

The original `comparison-data.md` described this target as a clean change with unanimous restraint.
That was a reasonable statement from the evidence available on 2026-09-01, but it is no longer a
valid description of the expanded record. The Fable finding is not retracted by later Sonnet misses:
three independent verifiers reconstructed the path from code. This rewrite treats the target as a
defect-bearing pull request whose defect was missed by all six runs in this directory.
