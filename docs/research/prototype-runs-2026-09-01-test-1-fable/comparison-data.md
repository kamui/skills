# Comparison data — Fable v2a on `kamui/shortlist#66`

**2026-09-02. Data only.** This directory contains one post-C9 v2a run, not a head-to-head
architecture comparison. The local source is [v2a-run.md](v2a-run.md); shared conditions are in the
[2026-09-02 addendum](../prototype-runs-2026-09-01-test-1/addendum-2026-09-02.md). Analysis is in
[evaluation.md](evaluation.md).

The run is separated because every reviewing agent used `claude-fable-5-1`, while the intended
before/after used Sonnet 5. The later [model-matched Sonnet run](../prototype-runs-2026-09-01-test-1/v2a-run.md)
closes the C9 causality question; this record remains useful for model/run sensitivity.

## Cost and shape

|                            | Fable v2a post-C9                                                                                                                        |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Skill / commit             | `code-review-deep-publish` / `87c68a9`                                                                                                   |
| Architecture               | Code + Requirements finders, then mandatory fresh verifier                                                                               |
| Model                      | `claude-fable-5-1` on every completed review role                                                                                        |
| Attempts / agents          | 5 agents attempted; completed path was Code finder, second Requirements-finder attempt, and verifier, with the session compiling results |
| Completed-path tokens      | **249,628**: Code 75,860; Requirements 105,117; verifier 68,651                                                                          |
| Completed-path tools       | **74**: 25 + 29 + 20                                                                                                                     |
| Completed-path wall clock  | ~988 s, serial rather than the intended parallel-finder shape                                                                            |
| Excluded interruption cost | killed orchestrator 139,895 tokens / 20 tools / ~595 s, plus one killed Requirements-finder attempt with ~22 tools and unreported tokens |
| Verifier                   | mandatory; 8 candidates received verdicts                                                                                                |

The cost is a lower bound, not a comparable total. Rate-limit interruption changed the execution
shape and left part of the consumed work unmetered.

## Output

| Measure            | Result                                                           |
| ------------------ | ---------------------------------------------------------------- |
| Candidates         | 8: Requirements 5, Code 3                                        |
| Verifier verdicts  | 7 confirmed, 1 plausible, 0 refuted                              |
| Cross-axis merges  | 3                                                                |
| **Findings**       | **4**: P2 consider ×3, P3 consider ×1                            |
| Questions          | 1, converted from the plausible AC4 candidate                    |
| Observations       | 12 raised across roles; 3 would publish under the cap            |
| Coverage           | complete, 9/9 files                                              |
| Requirement result | met 8, not met 4, unverifiable 0 under the run's restatement     |
| **Derived status** | **Needs Information**: no blocker, one verdict-relevant question |

## Findings and question

| Item                                                           | Finder agreement       | Verifier result                            | Publication result          |
| -------------------------------------------------------------- | ---------------------- | ------------------------------------------ | --------------------------- |
| Commerce-only timestamp regex at `validate-completion.py:2949` | Requirements only      | confirmed                                  | P2 consider                 |
| Bundle contract omits `Volatile-claim class`                   | both axes              | confirmed; merged                          | P2 consider                 |
| Narrow skill retains closed refresh lists                      | both axes              | confirmed; merged                          | P2 consider                 |
| Research skill still describes obligations as add-only         | both axes              | confirmed; merged                          | P3 consider                 |
| AC4 has no defined freshness-expectation carrier               | Requirements candidate | plausible; factual overstatement corrected | open question; holds status |

The Code axis found both originally tracked documentation peers but missed the validator regex. The
Requirements axis's seven-row changed-contract table found all four published drifts and the AC4
ambiguity.

## Cross-model sensitivity

The closest comparison is the same post-C9 skill on the same target, packet, and clone under
Sonnet 5. The pre-C9 Sonnet run is included only to show the before-state.

|                           | Sonnet pre-C9            | Fable post-C9                | Sonnet post-C9    |
| ------------------------- | ------------------------ | ---------------------------- | ----------------- |
| Skill commit              | `5db5903`                | `87c68a9`                    | `87c68a9`         |
| Bundle drift              | found, Requirements only | found, both axes             | found, both axes  |
| Narrow drift              | missed                   | found, both axes             | found, both axes  |
| Timestamp regex           | not raised               | **found, Requirements only** | **missed**        |
| Research add-only wording | not raised               | found, both axes             | found, Code only  |
| AC4 carrier               | acquitted                | plausible → question         | not raised        |
| Candidates / findings     | 1 / 1                    | 8 / 4                        | 5 / 3             |
| Status                    | Approved                 | Needs Information            | Changes Requested |

The two post-C9 runs agree on the central peers and disagree on additional recall and action. Fable
found the regex and question; Sonnet made the Narrow item blocking. Neither result is a superset of
the other.

## Mechanism observations

- **C9 fired.** The Requirements finder wrote seven changed contracts first. Its closed-list →
  open-rule row and old-fragment sweep surfaced both the Narrow peer and the regex.
- **C3 held.** Requirements returned 29 disposition rows and Code 22, in addition to the contract
  table.
- **Independent verification held.** Every candidate received one verdict with finder `support`
  removed; three duplicate pairs were merged.
- **The `plausible` path fired.** The verifier accepted the factual absence of a defined schema
  carrier but rejected the claim that no free-text carrier exists, routing the matter to a question.
- **Execution shape did not hold.** The two finders did not complete in parallel and the session,
  rather than one intact orchestrator, performed final dispatch and compilation.

## Data reconciliation note

The shared addendum describes the timestamp regex and AC4 carrier as newly surfaced by this run.
The original [v2 record](../prototype-runs-2026-09-01-test-1/v2-run.md) already contains the same
regex at the same line as F3 and the freshness-carrier concern as F4. They are counted here as
independent rediscoveries. This does not weaken the Fable result; it prevents overstating novelty.
