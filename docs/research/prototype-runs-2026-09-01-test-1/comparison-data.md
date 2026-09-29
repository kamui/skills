# Comparison data — v2–v5 plus v2a/v5a on `kamui/shortlist#66`

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

**2026-09-01–03. Data only.** This is a from-scratch consolidation of every run record in this
directory: [v2](v2-run.md), [v3](v3-run.md), [v4](v4-run.md), [v5](v5-run.md),
[v2a before C9](v2a-run-pre-c9.md), [v2a after C9](v2a-run.md), and [v5a](v5a-run.md).
Interpretation is in [evaluation.md](evaluation.md). The separate
[Fable 5.1 v2a run](../prototype-runs-2026-09-01-test-1-fable/comparison-data.md) is not pooled into
these tables.

## Comparison boundaries

There are two internally useful cohorts, not one seven-way cost experiment:

| Cohort        | Runs                         | Model / harness                                  | What may be compared                                                 |
| ------------- | ---------------------------- | ------------------------------------------------ | -------------------------------------------------------------------- |
| Original      | v2, v3, v4, v5               | Claude Opus 5 (1M), High reasoning / Claude Code | Output, tokens, tools, and run shape within the four-way cohort      |
| Sonnet retest | v2a pre-C9, v2a post-C9, v5a | `claude-sonnet-5`, default reasoning / `t3code`  | Finding behavior; the two v2a runs form a controlled C9 before/after |

The model, reasoning setting, harness, metering boundary, and run dates differ between cohorts.
Their cost columns must not be differenced. V2a and v5a were also designed after their authors had
seen this target, so all retest results are development-set mechanism checks, not holdout estimates
of general review quality.

## Cost and shape — original cohort

|                  | v2                                       | v3                  | v4                                         | v5                                                   |
| ---------------- | ---------------------------------------- | ------------------- | ------------------------------------------ | ---------------------------------------------------- |
| Architecture     | 2 axis finders + mandatory verifier      | integrated reviewer | integrated reviewer + conditional verifier | integrated reviewer + consequence-triggered verifier |
| Agents spawned   | 3                                        | 1                   | 2                                          | 2                                                    |
| Sub-agent tokens | **253,712**                              | **110,630**         | **175,824**                                | **174,563**                                          |
| Breakdown        | 91,333 + 99,834 finders; 62,545 verifier | 110,630 reviewer    | 128,616 reviewer; 47,208 verifier          | 128,013 reviewer; 46,550 verifier                    |
| Tool uses        | 118                                      | 49                  | 78                                         | 64                                                   |
| Wall clock       | ~851 s                                   | ~663 s              | ~879 s                                     | ~986 s                                               |
| Verifier         | mandatory; ran                           | optional; skipped   | conditional; ran                           | consequence-triggered; ran                           |

V3 used 44% of v2's tokens. V4 and v5 were within 1% of one another and each spent about 27% of
its measured tokens on verification.

## Cost and shape — Sonnet retest

Nested-agent metering differs by run, so the two token rows are reported separately rather than
collapsed into a misleading total.

|                                | v2a pre-C9                                  | v2a post-C9                                                | v5a                                                  |
| ------------------------------ | ------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------- |
| Skill commit                   | `5db5903`                                   | `87c68a9`                                                  | `c5f76df`                                            |
| Architecture                   | 2 axis finders + mandatory verifier         | 2 axis finders + mandatory verifier                        | integrated reviewer + consequence-triggered verifier |
| Child agents                   | 3                                           | 3                                                          | 1 verifier                                           |
| Primary / outer-wrapper tokens | 182,133                                     | 218,249                                                    | 160,853 for the whole outer run                      |
| Internal child-agent tokens    | 246,621                                     | 272,657 (112,792 + 103,578 + 56,287)                       | not separately broken out                            |
| Child-agent tool uses          | 106                                         | 107                                                        | included in the reported 64-tool outer run           |
| Wall clock                     | ~726 s child-agent path; ~1,551 s outer run | ~20 min finder dispatch through verifier; ~25–30 min total | ~758 s                                               |
| Verifier                       | ran; 1 candidate                            | ran; 5 candidates                                          | ran; 1 survivor                                      |

The post-C9 v2a record calls the complete run four agents when it includes the outer orchestrator
and three when it counts spawned children. This table uses the latter definition consistently.

## Output

|                             | v2                             | v3                            | v4                             | v5             | v2a pre-C9   | v2a post-C9                           | v5a                   |
| --------------------------- | ------------------------------ | ----------------------------- | ------------------------------ | -------------- | ------------ | ------------------------------------- | --------------------- |
| Candidates raised           | 6 (+1 passed along)            | 10                            | 10                             | 6              | 1            | 5                                     | 4                     |
| Pre-publication disposition | 2 refuted, 1 merged            | 9 dropped                     | 8 dropped                      | 4 dropped      | 0 refuted    | 5 confirmed, 2 cross-axis merges      | 3 refuted             |
| **Findings**                | **4**                          | **1**                         | **2**                          | **2**          | **1**        | **3**                                 | **1**                 |
| Blocking findings           | 2                              | 1                             | 0                              | 0              | 0            | 1                                     | 1                     |
| Priority / action           | P1 must-fix ×2; P2 consider ×2 | P2 blocking                   | P2 consider; P3 consider       | P3 consider ×2 | P3 consider  | P1 must-fix; P1 consider; P3 consider | P2 must-fix           |
| Questions                   | 0                              | 0                             | 0 to author; 1 to orchestrator | 0              | 0            | 0                                     | 0                     |
| Coverage                    | complete                       | complete; fetch gap disclosed | incomplete, then recovered     | complete       | complete     | complete                              | complete              |
| **Derived status**          | **Changes Requested**          | **Changes Requested**         | **Approved**                   | **Approved**   | **Approved** | **Changes Requested**                 | **Changes Requested** |

All statuses are advisory. V4 was the only review actually published; every other run was data-only.

## Finding-level agreement

“Dropped” includes finder acquittal, primary falsification, or verifier refutation. “Missed” means
the item is absent from the run's candidate, acquittal, question, and observation records.

| Item                                                                | v2                     | v3                      | v4                      | v5                         | v2a pre-C9                           | v2a post-C9               | v5a                        |
| ------------------------------------------------------------------- | ---------------------- | ----------------------- | ----------------------- | -------------------------- | ------------------------------------ | ------------------------- | -------------------------- |
| Narrow skill's closed refresh list (`shortlist-narrow/SKILL.md:46`) | P1 must-fix            | P2 blocking             | P2 consider             | P3 consider                | **missed**                           | P1 must-fix; both axes    | P2 must-fix                |
| Bundle contract's stale Kind list (`search-bundle-format.md:208`)   | P1 must-fix            | dropped                 | P3 consider             | P3 consider                | P3 consider                          | P1 consider; both axes    | not raised                 |
| Commerce-only timestamp regex (`validate-completion.py:2949`)       | **P2 consider**        | dropped                 | not raised              | not raised                 | not raised                           | **missed**                | observation, not a finding |
| AC4 freshness expectation has no defined carrier                    | **P2 consider**        | requirement marked met  | dropped                 | requirement marked met     | acquitted as pre-existing/unaffected | not raised                | not raised                 |
| Research skill still says obligations are add-only                  | acquitted / not raised | dropped                 | dropped                 | not raised                 | not raised                           | P3 consider               | not raised                 |
| Attestation test treats an incomplete fixture as complete           | refuted                | dropped after execution | dropped after execution | acquitted before candidacy | not raised                           | acquitted after tests     | not raised                 |
| ADR / `PROJECT_BRIEF.md` obligation lists                           | not raised             | dropped                 | dropped                 | dropped                    | observations / acquittals            | observations / acquittals | observations / acquittals  |

The later 2026-09-02 addendum describes the timestamp regex and AC4 carrier as new to the Fable
run. The primary [v2 record](v2-run.md) already contains the same regex at the same fix line as F3
and the AC4 carrier as F4. This rewrite uses the raw run record as the source of truth and treats
the later Fable results as independent
rediscoveries, not first discoveries.

## Requirement-ledger comparison

The original issue has 10 acceptance criteria, but the post-C9 v2a run restated them as 11 rows.
Counts are therefore run-native and are not a common score.

|             | Met | Partial / not met                           | Unverifiable / cannot tell |
| ----------- | --: | ------------------------------------------- | -------------------------: |
| v2          |   7 | 3 (AC1, AC4, AC6)                           |                          0 |
| v3          |   8 | 2 (AC5 protocol-only, AC6 partial)          |                          0 |
| v4          |  10 | 0; three marked “met, with propagation gap” |                          0 |
| v5          |  10 | 0                                           |                          0 |
| v2a pre-C9  |   9 | 1                                           |                          0 |
| v2a post-C9 |   9 | 2                                           |                          0 |
| v5a         |   9 | 1                                           |                          0 |

All original runs and the post-C9 v2a run executed both suites: 290 Python and 60 Node tests passed.
V5a re-ran the 290 Python tests and deliberately omitted the unrelated Node suite, disclosing that
choice in its coverage line.

## Verifier behavior

| Run         | Input / trigger                            | Verdicts                        | Material effect                                                                           |
| ----------- | ------------------------------------------ | ------------------------------- | ----------------------------------------------------------------------------------------- |
| v2          | every candidate; finder `support` withheld | 4 confirmed, 2 refuted, 1 merge | removed two false claims, merged a duplicate, corrected triggers; blockers remained       |
| v3          | not invoked                                | —                               | sole blocker received no fresh check                                                      |
| v4          | 2 survivors; `support` withheld            | 2 confirmed                     | corrected Narrow mechanism and cut an overstated bundle impact                            |
| v5          | 2 survivors; claim and raw citations only  | 2 confirmed                     | replaced a weak trigger and changed P2 must-fix to P3 consider, moving status to Approved |
| v2a pre-C9  | 1 candidate; `support` withheld            | 1 confirmed                     | narrowed the bundle-contract trigger; no action change                                    |
| v2a post-C9 | 5 candidates; `support` withheld           | 5 confirmed, 2 merges           | retained the Narrow item as must-fix; corrected the Research-skill trigger                |
| v5a         | sole must-fix survivor                     | 1 confirmed                     | confirmed the Narrow item and its blocking action                                         |

## Distinguishing observations

- The model-matched v2a before/after is the cleanest mechanism result in this directory. C9 changed
  the Narrow item from absent in both ledgers to independently raised by both axes. It also increased
  the returned finding set from one to three.
- C9 did not make recall exhaustive. The post-C9 Sonnet run missed the validator regex even though
  its reported old-fragment sweep should have approached it, and its Requirements finder failed to
  return the required row-wise disposition ledger.
- V5a's repo-wide peer sweep found the exact Narrow sibling it was introduced to find. It did not
  reproduce the bundle-contract or regex findings, and it made the Narrow drift blocking.
- The same Narrow fact spans the full action range: P1/P2 blocker in four runs and P2/P3 advisory in
  three. Agreement on the defect is much stronger than agreement on merge consequence.
- V5 is still the only run here whose verifier crossed the blocking boundary in the safer direction
  while preserving the finding.
- The separate Fable run found four advisory drifts and produced the corpus's only `plausible`
  verdict on this target. Its different model and interrupted execution keep it outside the cost
  cohort, but its unique recall is material evidence of run variance.

## Publication outcome

V4 was selected after the original v2–v4 comparison and published as
[review 5076220814](https://github.com/kamui/shortlist/pull/66#pullrequestreview-5076220814), with
the Narrow and bundle-contract findings as non-blocking `consider` comments and an
`Approved (advisory)` summary. The later runs were withheld to preserve the research condition.
