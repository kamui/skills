# Comparison data — v3–v5 plus v5a on `tokio-rs/tokio#7757`

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

This target has externally checkable ground truth: the pull request shipped, caused a production
`spawn_blocking` hang, was reverted six days later, and was re-landed four months later with a
different synchronization design.

## Comparison boundaries

The retest closes the history contamination but uses later, development-set skills. Cost meters
also differ. Behavioral results may be compared with the caveats attached; token totals cannot be
treated as one six-way cost experiment.

## Cost and shape

|                     | v3                             | v4                             | v5                             | v5a                                            |
| ------------------- | ------------------------------ | ------------------------------ | ------------------------------ | ---------------------------------------------- |
| Architecture        | integrated reviewer + verifier | integrated reviewer + verifier | integrated reviewer + verifier | integrated reviewer + verifier                 |
| Reported run agents | 1 verifier child               | 1 verifier child               | 1 verifier child               | primary + 1 child                              |
| Reported tokens     | 66,414 verifier only           | 56,443 verifier only           | 54,438 verifier only           | 276,985 across primary and verifier            |
| Tool uses           | ~34                            | ~68                            | ~46 + verifier 11              | 67 (primary 51 + verifier 16)                  |
| Wall clock          | ~25 min                        | ~29 min                        | ~19–22 min                     | primary span unavailable; verifier ~3 min 39 s |
| Verifier            | conditional; ran               | mandatory; ran                 | consequence-triggered; ran     | candidate-mode; ran                            |

## Output

|                   | v3                    | v4                    | v5                       | v5a                      |
| ----------------- | --------------------- | --------------------- | ------------------------ | ------------------------ |
| Candidates        | 2 formal              | 2                     | 6 considered, 1 rendered | 7                        |
| Dropped / refuted | 1 refuted             | 1 refuted             | 5 falsified              | 6 dropped/refuted/routed |
| **Findings**      | **1**                 | **1**                 | **1**                    | **1**                    |
| Blocking findings | 1                     | 1                     | 1                        | 1                        |
| Priority spread   | P1                    | P0                    | P1                       | P1                       |
| Questions         | 0                     | 0                     | 0                        | 1                        |
| Observations      | none                  | none                  | none                     | 3 published              |
| Coverage          | complete, 6/6         | complete, 6/6         | complete, 6/6            | complete, 6/6            |
| **Status**        | **Changes Requested** | **Changes Requested** | **Changes Requested**    | **Changes Requested**    |

All statuses are advisory. Status is unanimous and does not distinguish whether a run found the
defect that actually shipped.

## Ground-truth finding matrix

The production regression is the unguarded post-push branches in `Spawner::spawn_task`: branch A
received a shutdown recheck; branches B (“at max threads”) and C (“idle worker”) only notify and can
strand a queued task after every worker has passed its final drain.

|                               | v3                                                                 | v4                                                        | v5                          | v5a                                                          |
| ----------------------------- | ------------------------------------------------------------------ | --------------------------------------------------------- | --------------------------- | ------------------------------------------------------------ |
| Ground-truth branches B and C | **partial**: found C; checked B and wrongly called it self-healing | **found both**                                            | **found both**              | **found both**                                               |
| Priority / action             | P1 must-fix                                                        | P0 must-fix                                               | P1 must-fix                 | P1 must-fix                                                  |
| Hindsight status              | blind                                                              | **contaminated by revert/re-land history**                | blind                       | truncated / blind                                            |
| Proposed fix quality          | worker-side accounting repair                                      | spawner-side atomic claim, rewritten using actual re-land | per-branch shutdown recheck | **invariant-level central repair after verifier correction** |

V5a is the only history-truncated run that both found the full ground-truth branch set and published
an invariant-level fix. It is development-set evidence, so the result validates the N2 mechanism on
this target rather than proving general superiority.

## Secondary candidates and disagreements

| Item                                                             | v3                 | v4                    | v5         | v5a                             |
| ---------------------------------------------------------------- | ------------------ | --------------------- | ---------- | ------------------------------- |
| Temporary `WouldBlock` arm can strand a task (`pool.rs:437-443`) | not raised         | not raised            | not raised | dropped as pre-existing         |
| Mandatory work drains on caller thread                           | not raised         | not raised            | not raised | not raised                      |
| `fastrand_n` cfg could compile dead code                         | verifier refuted   | verifier refuted      | falsified  | not raised                      |
| Residual `condvar_mutex` contention                              | not raised         | not raised            | not raised | not raised                      |
| Fixed `NUM_SHARDS` vs “adapts to concurrency” claim              | not raised         | not raised            | not raised | question                        |
| Unresolved nested-lock concern from prior review                 | traced and cleared | not separately traced | weighed    | refuted at head; observation    |
| `Shard::push` growth optimization as scope creep                 | not raised         | not raised            | not raised | preference dropped; observation |

## Verifier contributions

| Run | Material verifier effect                                                                                               |
| --- | ---------------------------------------------------------------------------------------------------------------------- |
| v3  | corrected the mechanism from shard affinity to “no worker remains”; refuted the cfg candidate                          |
| v4  | refuted the cfg candidate and rewrote the fix using reachable post-merge history                                       |
| v5  | tightened trigger/impact and proved adjacent loom tests do not model the interleaving                                  |
| v5a | confirmed the shipped defect and rejected the narrow branch-by-branch patch, replacing it with an invariant-level fix  |

## Methodology correction
