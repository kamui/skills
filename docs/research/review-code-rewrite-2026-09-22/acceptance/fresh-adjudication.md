# C7 and C8 freeze adjudication

Adjudicated on 2026-09-22 for issue #333. This is adjudicator-only freeze vetting, not a matched benchmark attempt. Do not include this report, its reproduction, the expected-outcomes document, or the historical review records in working reviewer inputs. No repository files or forge state were changed.

## Decision

Retain C7 as buggy with one registered must-fix and expected status `Changes Requested`. Retain C8 as the clean control with expected status `Approved`. C8's clean classification rests on direct comparison and focused execution, not on the historical approval alone. An independently substantiated new defect must still receive adjudication; a finding is not false merely because the case was registered clean.

## Pinned sources

- C7, kamui/skills#320: merge-base `c7a7afca3cb1164c256eb44ae814ecf581352c40`, head `1956058ea055937ed812b1ea893a783521a2cda0`.
- C7 addressing commits: `1701a620fa30b5650b1e4fbc3f9a358baf3d530b` and `573f1bf07ddf58bc0eed2b6a6b9094dd9fd9c77e`.
- C8, kamui/skills#325: merge-base `160d1201bed57d96de6fc8b1ae657bd098aa2de6`, head `0ea287f0c07fda09b9d063612353dcef37f38063`.
- Local Git objects supplied the source diffs and extracted execution copies. Forge captures were `/tmp/issue-333/pr320.json`, `/tmp/issue-333/graphql-320.json`, `/tmp/issue-333/pr325.json`, and `/tmp/issue-333/graphql-325.json`.
- Registration and construction rules were `docs/research/review-code-rewrite-2026-09-22/expected-outcomes.md` and `comparison.md`.

## C7

The registered finding is confirmed: preserve the follow-up after the verifier refutes the last material requirement candidate. At the pinned head, `SKILL.md` step 3 still defines a must-fix at any kind as material. Its new attackable predicate excludes `requirement` and `maintainability` unless the primary marks a safety premise. The follow-up now requires an attackable row and incorrectly asserts that a refuted material candidate always qualifies. A requirement blocker refuted by a cited fact, without a safety premise, contradicts that assertion.

The composer repeats the defect in `read_record`: its attackable predicate checks kind and the explicit mark, but not the refuted disposition. With no findings left, one refuted requirement row, one initial batch, `follow_up_spent: false`, and `clean_verdict: not-required`, it accepts `Approved`. That removes a required independent follow-up while reporting complete coverage.

I reproduced the same composition input against extracted base, head, and addressed source:

| Source | Result |
| --- | --- |
| `c7a7afc` | Exit 1, clean-verdict verification refusal |
| `1956058` | Exit 0, `Approved` |
| `573f1bf` | Exit 1, clean-verdict verification refusal |
| `573f1bf`, with the follow-up recorded and `clean_verdict: stands` | Exit 0, `Approved` |

The [reproduction input](adjudication-evidence/c7-reproduction.json) and outputs are retained in [adjudication-evidence](adjudication-evidence/), as `c7-base-reproduction.out`, `c7-head-reproduction.out`, `c7-fix-reproduction.out`, and `c7-fix-follow-up.out`. The input derives from the pinned head's existing `gate_composition` fixture, removes surviving items, and supplies the refuted requirement row. This is a structural composer reproduction, not an actual review dispatch.

Commit `1701a62` adds `disposition == "refuted"` to the composer predicate, updates the procedural rule, and adds refusal/acceptance cases for the missing/present follow-up. Commit `573f1bf` clarifies the explanation, including unresolved verdicts, without changing behavior. These changes directly repair the reproduced mechanism.

The historical published finding was submitted at `2026-09-20T17:24:27Z` on `1956058`; its implemented reply names both fixes at `2026-09-20T17:52:25Z`. The resolved thread and addressing summary corroborate the mechanism but are not the basis for accepting it. Historical source: https://github.com/kamui/skills/pull/320#discussion_r4057628770.

Confidence is high for the registered defect and its repair. Keep one registered consequential outcome. The broad assertion that there can be no other defect is not established by this targeted adjudication.

## C8

The complete six-file diff supports the promised extraction. The old heredoc and new `eligibility` function perform the same JSON, identity, target-state, nested connection completeness, local commit, and merge-base checks. The old `defer` prints and exits zero; the new function raises `Deferred`, caught by the new CLI branch to print the same verdict and return zero. Unexpected shape errors still exit nonzero and reach the unchanged shell fallback with visible stderr. The shell still stops on root-query or build failure, keeps build output private, and uses the reviewed repository as its working directory. The new absolute script placeholder is documented and bound in both affected command-replay tests. The existing normalization and later-state CLI branches retain their behavior.

Executed from a complete extracted `skills/review-code` tree at `0ea287f`:

- Four `test_command_chains.Chains` root-block tests covering eligible builds, unproven first-review state, unavailable commit/merge-base, and visible query/build failures.
- `test_run_events.RunEventTests.test_documented_wrapped_commands_run`.
- `forge_packet.py --self-test`.

All five unittest cases passed in 4.212 seconds, and the self-test passed. The code inspection found no consequential introduced defect. The historical advisory approval at `2026-09-22T20:21:17Z` on the same head and the captured absence of threads/comments are corroboration only. Historical source: https://github.com/kamui/skills/pull/325.

Confidence is moderately high for the clean-control classification within this small extraction. I did not rerun all ten script suites or exercise a live forge. The captures establish no later correction within their returned data, not that no later correction can exist anywhere. The truthy non-object JSON exception is retained behavior, not an introduced defect.

## Freeze construction caveat

Both supplied PR320 body captures contain edits made after the published finding. They explicitly name refuted rows, the requirement-blocker example, the addressing commits, and later review outcomes. The addressing summary also says the description was edited. Removing reviews and comments alone will therefore leave answer leakage in C7's packet.

Obtain a dated pre-review body, or explicitly record a bounded reconstruction and its source limits before admitting C7 as a valid matched input. Do not present the captured current body as an exact pre-review snapshot. This packet-provenance limitation does not weaken the source-level defect adjudication. PR325's body contains no comparable historical-outcome leak in the supplied capture.
