# Comparison data — v2–v5 plus v2a/v5a on `tokio-rs/tokio#7757`

> **Promotion status:** “v5” is the historical prototype name used by this record. PR #17 promoted
> that workflow to `skills/code-review-publish` on `main`; new work should invoke
> `/code-review-publish` without the `-5` suffix.

**2026-09-01–03. Data only.** This consolidates every run record in this directory:
[v2](v2-run.md), [v3](v3-run.md), [v4](v4-run.md), [v5](v5-run.md), [v2a](v2a-run.md), and
[v5a](v5a-run.md). Interpretation is in [evaluation.md](evaluation.md); retest controls are in
[addendum-2026-09-03.md](addendum-2026-09-03.md).

This target has externally checkable ground truth: the pull request shipped, caused a production
`spawn_blocking` hang, was reverted six days later, and was re-landed four months later with a
different synchronization design.

## Comparison boundaries

| Cohort   | Runs           | Model / harness                               | History available                                                      |
| -------- | -------------- | --------------------------------------------- | ---------------------------------------------------------------------- |
| Original | v2, v3, v4, v5 | session-default Claude Sonnet 5 / Claude Code | mirror accidentally contained post-merge history; v4 found and used it |
| Retest   | v2a, v5a       | explicit `claude-sonnet-5` / `t3code`         | mirror truncated at the pinned head; revert and re-land unreachable    |

The retest closes the history contamination but uses later, development-set skills. Cost meters
also differ. Behavioral results may be compared with the caveats attached; token totals cannot be
treated as one six-way cost experiment.

## Cost and shape

|                     | v2                        | v3                             | v4                             | v5                             | v2a                                       | v5a                                            |
| ------------------- | ------------------------- | ------------------------------ | ------------------------------ | ------------------------------ | ----------------------------------------- | ---------------------------------------------- |
| Architecture        | 2 axis finders + verifier | integrated reviewer + verifier | integrated reviewer + verifier | integrated reviewer + verifier | 2 axis finders + verifier                 | integrated reviewer + verifier                 |
| Reported run agents | 3                         | 1 verifier child               | 1 verifier child               | 1 verifier child               | primary + 3 children                      | primary + 1 child                              |
| Reported tokens     | 227,934 across 3 children | 66,414 verifier only           | 56,443 verifier only           | 54,438 verifier only           | 491,450 across primary, finders, verifier | 276,985 across primary and verifier            |
| Tool uses           | ~95                       | ~34                            | ~68                            | ~46 + verifier 11              | ~88                                       | 67 (primary 51 + verifier 16)                  |
| Wall clock          | ~21 min                   | ~25 min                        | ~29 min                        | ~19–22 min                     | ~28 min                                   | primary span unavailable; verifier ~3 min 39 s |
| Verifier            | mandatory                 | conditional; ran               | mandatory; ran                 | consequence-triggered; ran     | mandatory; ran                            | candidate-mode; ran                            |

The original v3/v4/v5 token cells meter only verifiers while v2 includes both finders and verifier.
They are not evidence that v2 costs three to four times as much. The retest cells include their
primaries and are also not directly comparable to the original cells.

## Output

|                   | v2                     | v3                    | v4                    | v5                       | v2a                   | v5a                      |
| ----------------- | ---------------------- | --------------------- | --------------------- | ------------------------ | --------------------- | ------------------------ |
| Candidates        | 3: 2 Code + 1 question | 2 formal              | 2                     | 6 considered, 1 rendered | 2 + 1 direct question | 7                        |
| Dropped / refuted | 0 verifier-eligible    | 1 refuted             | 1 refuted             | 5 falsified              | 1 refuted             | 6 dropped/refuted/routed |
| **Findings**      | **2**                  | **1**                 | **1**                 | **1**                    | **1**                 | **1**                    |
| Blocking findings | 1                      | 1                     | 1                     | 1                        | 1                     | 1                        |
| Priority spread   | P1, P2                 | P1                    | P0                    | P1                       | P2                    | P1                       |
| Questions         | 1                      | 0                     | 0                     | 0                        | 1                     | 1                        |
| Observations      | no bounded section     | none                  | none                  | none                     | 3 published           | 3 published              |
| Coverage          | complete, 6/6          | complete, 6/6         | complete, 6/6         | complete, 6/6            | complete, 6/6         | complete, 6/6            |
| **Status**        | **Changes Requested**  | **Changes Requested** | **Changes Requested** | **Changes Requested**    | **Changes Requested** | **Changes Requested**    |

All statuses are advisory. Status is unanimous and does not distinguish whether a run found the
defect that actually shipped.

## Ground-truth finding matrix

The production regression is the unguarded post-push branches in `Spawner::spawn_task`: branch A
received a shutdown recheck; branches B (“at max threads”) and C (“idle worker”) only notify and can
strand a queued task after every worker has passed its final drain.

|                               | v2                          | v3                                                                 | v4                                                        | v5                          | v2a                                     | v5a                                                          |
| ----------------------------- | --------------------------- | ------------------------------------------------------------------ | --------------------------------------------------------- | --------------------------- | --------------------------------------- | ------------------------------------------------------------ |
| Ground-truth branches B and C | **found both**              | **partial**: found C; checked B and wrongly called it self-healing | **found both**                                            | **found both**              | **examined both and wrongly acquitted** | **found both**                                               |
| Priority / action             | P1 must-fix                 | P1 must-fix                                                        | P0 must-fix                                               | P1 must-fix                 | absent                                  | P1 must-fix                                                  |
| Hindsight status              | blind to later history      | blind                                                              | **contaminated by revert/re-land history**                | blind                       | truncated / blind                       | truncated / blind                                            |
| Proposed fix quality          | per-branch shutdown recheck | worker-side accounting repair                                      | spawner-side atomic claim, rewritten using actual re-land | per-branch shutdown recheck | —                                       | **invariant-level central repair after verifier correction** |

V5a is the only history-truncated run that both found the full ground-truth branch set and published
an invariant-level fix. It is development-set evidence, so the result validates the N2 mechanism on
this target rather than proving general superiority.

## Secondary candidates and disagreements

| Item                                                             | v2                        | v3                 | v4                    | v5         | v2a                                            | v5a                             |
| ---------------------------------------------------------------- | ------------------------- | ------------------ | --------------------- | ---------- | ---------------------------------------------- | ------------------------------- |
| Temporary `WouldBlock` arm can strand a task (`pool.rs:437-443`) | not raised                | not raised         | not raised            | not raised | **confirmed P2 must-fix**                      | dropped as pre-existing         |
| Mandatory work drains on caller thread                           | **confirmed P2 consider** | not raised         | not raised            | not raised | not raised                                     | not raised                      |
| `fastrand_n` cfg could compile dead code                         | checked / not raised      | verifier refuted   | verifier refuted      | falsified  | not the survivor                               | not raised                      |
| Residual `condvar_mutex` contention                              | question                  | not raised         | not raised            | not raised | question                                       | not raised                      |
| Fixed `NUM_SHARDS` vs “adapts to concurrency” claim              | not raised                | not raised         | not raised            | not raised | observation                                    | question                        |
| Unresolved nested-lock concern from prior review                 | not separately traced     | traced and cleared | not separately traced | weighed    | acquitted with trace                           | refuted at head; observation    |
| `Shard::push` growth optimization as scope creep                 | not raised                | not raised         | not raised            | not raised | candidate refuted after fabricated issue quote | preference dropped; observation |

The `WouldBlock` disagreement is about change attribution. V2a's verifier treated the arm's safety
argument as broken by this refactor even though the arm text is unchanged. V5a treated byte-identical
base code as pre-existing and dropped it. The program needs an explicit rule for behavior whose code
is unchanged but whose synchronization assumptions changed.

## Verifier contributions

| Run | Material verifier effect                                                                                               |
| --- | ---------------------------------------------------------------------------------------------------------------------- |
| v2  | confirmed two Code findings and narrowed the ground-truth trigger                                                      |
| v3  | corrected the mechanism from shard affinity to “no worker remains”; refuted the cfg candidate                          |
| v4  | refuted the cfg candidate and rewrote the fix using reachable post-merge history                                       |
| v5  | tightened trigger/impact and proved adjacent loom tests do not model the interleaving                                  |
| v2a | confirmed the adjacent `WouldBlock` finding and caught a fabricated issue quotation; never saw the false B/C acquittal |
| v5a | confirmed the shipped defect and rejected the narrow branch-by-branch patch, replacing it with an invariant-level fix  |

V2a demonstrates the claim/support split working on a fabricated quotation and failing structurally
on an acquittal outside its input. V5a demonstrates N2 working on exactly the bug class it was meant
to address.

## Questions and observations

- V2 and v2a both published the empirical question whether the remaining `condvar_mutex` can satisfy
  the issue's scalability goal under higher concurrency.
- V5a published a different question: whether the fixed 16-shard implementation is the code behind
  the body/commit's “adapts to concurrency” benchmark claim.
- V2a and v5a both used bounded observations for accurate, non-verdict facts. V5a's three slots
  include the cleared nested-lock concern and manual growth complexity; v2a's include fixed-shard
  behavior and related audit facts.

## Methodology correction

The original mirror was not truncated. V4 discovered the actual revert and corrected re-land via
`git log --all`, after independently deriving a candidate. Its P0 and upstream-matching repair are
therefore not blind evidence of architecture quality. The v2a/v5a mirror contains no object newer
than the pinned head, and every agent reported reading no later history. The retest resolves this
specific contamination.
