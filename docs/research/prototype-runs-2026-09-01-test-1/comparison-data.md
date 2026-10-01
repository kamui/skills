# Comparison data — v3–v5 plus v5a on `kamui/shortlist#66`

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

## Cost and shape — original cohort

|                  | v3                  | v4                                         | v5                                                   |
| ---------------- | ------------------- | ------------------------------------------ | ---------------------------------------------------- |
| Architecture     | integrated reviewer | integrated reviewer + conditional verifier | integrated reviewer + consequence-triggered verifier |
| Agents spawned   | 1                   | 2                                          | 2                                                    |
| Sub-agent tokens | **110,630**         | **175,824**                                | **174,563**                                          |
| Breakdown        | 110,630 reviewer    | 128,616 reviewer; 47,208 verifier          | 128,013 reviewer; 46,550 verifier                    |
| Tool uses        | 49                  | 78                                         | 64                                                   |
| Wall clock       | ~663 s              | ~879 s                                     | ~986 s                                               |
| Verifier         | optional; skipped   | conditional; ran                           | consequence-triggered; ran                           |

## Cost and shape — Sonnet retest

Nested-agent metering differs by run, so the two token rows are reported separately rather than
collapsed into a misleading total.

|                                | v5a                                                  |
| ------------------------------ | ---------------------------------------------------- |
| Skill commit                   | `c5f76df`                                            |
| Architecture                   | integrated reviewer + consequence-triggered verifier |
| Child agents                   | 1 verifier                                           |
| Primary / outer-wrapper tokens | 160,853 for the whole outer run                      |
| Internal child-agent tokens    | not separately broken out                            |
| Child-agent tool uses          | included in the reported 64-tool outer run           |
| Wall clock                     | ~758 s                                               |
| Verifier                       | ran; 1 survivor                                      |

## Output

|                             | v3                            | v4                             | v5             | v5a                   |
| --------------------------- | ----------------------------- | ------------------------------ | -------------- | --------------------- |
| Candidates raised           | 10                            | 10                             | 6              | 4                     |
| Pre-publication disposition | 9 dropped                     | 8 dropped                      | 4 dropped      | 3 refuted             |
| **Findings**                | **1**                         | **2**                          | **2**          | **1**                 |
| Blocking findings           | 1                             | 0                              | 0              | 1                     |
| Priority / action           | P2 blocking                   | P2 consider; P3 consider       | P3 consider ×2 | P2 must-fix           |
| Questions                   | 0                             | 0 to author; 1 to orchestrator | 0              | 0                     |
| Coverage                    | complete; fetch gap disclosed | incomplete, then recovered     | complete       | complete              |
| **Derived status**          | **Changes Requested**         | **Approved**                   | **Approved**   | **Changes Requested** |

All statuses are advisory. V4 was the only review actually published; every other run was data-only.

## Finding-level agreement

“Dropped” includes finder acquittal, primary falsification, or verifier refutation. “Missed” means
the item is absent from the run's candidate, acquittal, question, and observation records.

| Item                                                                | v3                      | v4                      | v5                         | v5a                        |
| ------------------------------------------------------------------- | ----------------------- | ----------------------- | -------------------------- | -------------------------- |
| Narrow skill's closed refresh list (`shortlist-narrow/SKILL.md:46`) | P2 blocking             | P2 consider             | P3 consider                | P2 must-fix                |
| Bundle contract's stale Kind list (`search-bundle-format.md:208`)   | dropped                 | P3 consider             | P3 consider                | not raised                 |
| Commerce-only timestamp regex (`validate-completion.py:2949`)       | dropped                 | not raised              | not raised                 | observation, not a finding |
| AC4 freshness expectation has no defined carrier                    | requirement marked met  | dropped                 | requirement marked met     | not raised                 |
| Research skill still says obligations are add-only                  | dropped                 | dropped                 | not raised                 | not raised                 |
| Attestation test treats an incomplete fixture as complete           | dropped after execution | dropped after execution | acquitted before candidacy | not raised                 |
| ADR / `PROJECT_BRIEF.md` obligation lists                           | dropped                 | dropped                 | dropped                    | observations / acquittals  |

## Requirement-ledger comparison

|             | Met | Partial / not met                           | Unverifiable / cannot tell |
| ----------- | --: | ------------------------------------------- | -------------------------: |
| v3          |   8 | 2 (AC5 protocol-only, AC6 partial)          |                          0 |
| v4          |  10 | 0; three marked “met, with propagation gap” |                          0 |
| v5          |  10 | 0                                           |                          0 |
| v5a         |   9 | 1                                           |                          0 |

## Verifier behavior

| Run         | Input / trigger                            | Verdicts                        | Material effect                                                                           |
| ----------- | ------------------------------------------ | ------------------------------- | ----------------------------------------------------------------------------------------- |
| v3          | not invoked                                | —                               | sole blocker received no fresh check                                                      |
| v4          | 2 survivors; `support` withheld            | 2 confirmed                     | corrected Narrow mechanism and cut an overstated bundle impact                            |
| v5          | 2 survivors; claim and raw citations only  | 2 confirmed                     | replaced a weak trigger and changed P2 must-fix to P3 consider, moving status to Approved |
| v5a         | sole must-fix survivor                     | 1 confirmed                     | confirmed the Narrow item and its blocking action                                         |

## Publication outcome
