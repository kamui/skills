# Removal candidates for review-code, issue #394

[#394](https://github.com/kamui/skills/issues/394) asks for whole sections or rules to be removed from `review-code`'s instruction text where their absence would not change a review decision. This note ranks the candidates. It is analysis only: no skill text, script, test, or limit was changed, and no benchmark was dispatched.

All citations are at commit `05e336791ffd7f42abb74421df47032405fe0b52`. Paths starting with `SKILL.md` or `references/` are relative to `skills/review-code/`. Script names are under `skills/review-code/scripts/`. Byte figures are `wc -c` on the extracted span, and a whole-paragraph span includes the blank line that follows it.

## Result

Eleven removals are recommended in two tiers. Tier A is seven whole paragraphs. Tier B is one more paragraph and three complete rule sentences.

| Set | Bytes removed | Always loaded | Runtime total |
| --- | ---: | ---: | ---: |
| Today | 0 | 29,684 | 73,188 |
| Tier A | 1,989 | 28,968 | 71,199 |
| Tier A + B | 2,940 | 28,017 | 70,248 |

Both tiers end below the 29,444-byte always-loaded size from before epic #380, so either meets the issue's second acceptance item.

Three limits apply to this result.

- **No large section qualifies.** Every section over 600 bytes has a consumer, a builder dependency, or a rule with no other owner. The decision-neutral text is about 4% of the runtime set.
- **The #386 audit names no phase to cut.** It leaves 93.4% of cost unattributed (`docs/research/builtin-review-benchmark-2026-09-24/a-phase-audit.md:120`) and says clean-verdict cost "does not establish that the checks can safely be removed" (`a-phase-audit.md:134-137`). The issue's third category is empty.
- **This will not move the cost gap.** Tier A + B removes 1,667 always-loaded bytes, roughly 420 tokens per request. #394 offsets the epic's additions. It does not address the 5.3x cost ratio (`docs/research/builtin-review-benchmark-2026-09-24/README.md:512-517`, 15.99 / 3.04).

## Tier A: whole paragraphs, high confidence

Sets: RT runtime total, AL always loaded, RV review, RQ required verifier, RR re-review.

| Rank | ID | Span | Bytes | Sets | Why its absence changes no decision |
| ---: | --- | --- | ---: | --- | --- |
| 1 | R1 | `references/output.md:15-16` | 598 | RT AL RV RQ RR | The reviewer cannot author the layout. The composition input has no body field (`render_review.py:1280-1329`) and `compose_body` builds every part the paragraph lists (`render_review.py:1488-1600`). |
| 2 | R2 | `references/output.md:19-20` | 118 | RT AL RV RQ RR | The workflow string is a script constant (`render_review.py:130`) that the reviewer never writes. The sentence addresses maintainers. |
| 3 | R3 | `references/prior-state.md:3-4` | 369 | RT RR | A load condition inside the file it gates, plus a contents list. `SKILL.md:34` and `references/targets.md:23` own the condition. |
| 4 | R4 | `references/prior-state.md:34-35` | 255 | RT RR | The finalizer refuses a pre-protocol record and its refusal text carries the same instruction (`render_review.py:1727-1730`). The caller states the rule too (`skills/implement-publish/references/continuation.md:21`). |
| 5 | R7 | `references/verification.md:3-4` | 241 | RT RQ | Load condition owned by `SKILL.md:38` and `:43`. Ruling values are at `SKILL.md:47` and `:49`, and the finalizer refuses any other (`render_review.py:908-909`). |
| 6 | R8 | `references/targets.md:59-60` | 329 | RT RV RQ RR | Snapshot pruning and leftover-ref housekeeping. Neither sentence bears on a finding, status, or coverage. The pruning note duplicates `review_context.py:14-16`. |
| 7 | R9 | `references/targets.md:3-4` | 79 | RT RV RQ RR | Load condition owned by `SKILL.md:33`. |

Two independent passes over the text both chose R1. It is the strongest single removal.

**One caveat on R1.** Its "aim below 100 summary words" target has no other owner and no script checks it. It governs length, not a decision, so it bears on the cost guardrail only.

**R7 pays more than its set membership suggests.** The budget test counts `verification.md` only on the required-verifier path, but the audit records it read in all 20 valid baseline reviews, including the 10 with no batch (`a-phase-audit.md:223-225`).

**Dangling references.**

- R2: `skills/review-code/DESIGN.md:20` says `output.md` owns identity. The #394 DESIGN entry has to move that ownership and carry the increment rule, which appears nowhere else in those words.
- R8: reverses a retention made on 2026-09-20 (`docs/review-code/HISTORY.md:1127`). The DESIGN entry should say so.
- The others leave nothing dangling. No script reads `prior-state.md` or `verification.md`.

## Tier B: whole rules, medium to medium-high confidence

| Rank | ID | Span | Bytes | Sets | Why its absence changes no decision |
| ---: | --- | --- | ---: | --- | --- |
| 8 | R10 | `references/output.md:25`, bytes 456-697 | 242 | RT AL RV RQ RR | `references/targets.md:67` states the same field list, and `skills/review-code/DESIGN.md:17` names `targets.md` as owner. The finalizer names any missing field (`render_review.py:1204`, `:1209-1215`, `:1250-1252`). |
| 9 | R5 | `SKILL.md:34`, bytes 309-467 | 159 | RT AL RV RQ RR | The sentence before it already delegates the shortcut to `prior-state.md`. `forge_packet.py:1171-1181` checks every condition the sentence lists. |
| 10 | R6 | `references/output.md:21`, bytes 1-297 | 297 | RT AL RV RQ RR | The finalizer derives `packet_context`, refuses a disagreeing copy (`render_review.py:2323-2332`), and writes `none` for a local target (`render_review.py:1241-1245`). |
| 11 | O3 | `references/output.md:11-12` | 253 | RT AL RV RQ RR | Question and observation substance stays at `references/rubric.md:70` and `:72`. The finalizer refuses a priority or `Change` field on a question (`render_review.py:724-732`) and `should` or `must` in an observation (`render_review.py:757-758`). |

**Why these rank below tier A.**

- R5, R6 and R10 are complete sentences inside a paragraph that stays. Each is one whole rule, but the issue asks for sections or rules and a paragraphs-only reading excludes them.
- R6 leaves the fourth sentence of `output.md:21` in place on purpose. `run.specs` defaults to an empty list when omitted (`render_review.py:1216`), so that sentence is not enforced.
- O3 is decision-neutral but may cost repairs. 53 of the 78 retained compositions carry observations, and without the `should`/`must` hint some runs may be refused once. "Whole-change questions go in the body" has no other owner, and the term is still used at `references/output.md:13`.

R10 is the only tier B removal the #394 guardrail run can observe on every review, because 77 of the 78 retained compositions are range targets.

## Optional, not recommended for the first change

| ID | Span | Bytes | Reason to hold back |
| --- | --- | ---: | --- |
| R11 | `references/output.md:33`, bytes 1-169 | 169 | Describes what the script does. Duplicates `SKILL.md:70`. Low value. |
| R12 | `references/output.md:35`, bytes 1-88 and 357-460 | 192 | Two non-adjacent sentences from one paragraph. Each duplicates `SKILL.md:72`, but this is the closest item to scattered trimming. |
| O1 | `references/rubric.md:72`, bytes 259-382 | 124 | The finalizer enforces the observation cap (`render_review.py:2151-2157`), but the cap binds in 7 of 78 retained runs, so repairs would rise. |
| O2 | `references/rubric.md:66-67` | 394 | The only prose naming the check dispositions. The finalizer does not require a reason for `unavailable` or `failed` (`render_review.py:2078-2092`), so part of the rule is unenforced. |
| O4 | `references/verifier-concurrency.md:5-6` | 275 | Breaks `test_verifier_handoff.py:265`, which asserts the removed text. Confirmed by running the suite on a trimmed copy. |

## Rejected

| ID | Span | Bytes | Why rejected |
| --- | --- | ---: | --- |
| N4 | `references/verifier.md:54-78`, worked JSON example | 656 | The accounting helper requires the exact top-level keys (`account_verifier_return.py:126-127`) and withholds every task in a role whose array is missing (`:131-133`). Inside the encoding section, the example is the only text that names `candidates` and `premises`. A withheld required task forces `Incomplete`. |
| N5 | `references/prior-state.md:23-24`, delta summary | 229 | The finalizer writes the delta range only when `run.prior_head` is set (`render_review.py:1539-1540`). It never derives that field, and no instruction names it. This paragraph is the only loaded text requiring a delta review to show its range. |
| N1 | `references/verification.md:19-20`, premise reconciliation | 251 | Sits on the protected safety-premise path and is the only prose naming `reopened_as`. |
| N2 | `SKILL.md:51-52`, optional scrutiny | 165 | Unused in the retained compositions, which reflects the benchmark's shape and is not evidence of neutrality. |
| N3 | `references/verifier.md:38-45`, worker supplied-check rules | 1,322 | The builder uses its heading as a boundary. Removing it is a builder change, which the issue excludes. |

## Totals

Measured on trimmed copies of the tree, not projected.

| Set | Today | Limit today | Tier A | Tier A + O3 | Tier A + B |
| --- | ---: | ---: | ---: | ---: | ---: |
| Runtime total | 73,188 | 74,000 | 71,199 | 70,946 | 70,248 |
| Always loaded | 29,684 | 31,000 | 28,968 | 28,715 | 28,017 |
| Review | 48,405 | 49,000 | 47,281 | 47,028 | 46,330 |
| Required verifier | 60,582 | 62,000 | 59,217 | 58,964 | 58,266 |
| Re-review | 57,598 | 59,000 | 55,850 | 55,597 | 54,899 |
| Verifier instructions | 17,701 | 18,000 | 17,701 | 17,701 | 17,701 |
| Verifier example brief | 21,199 | 22,000 | 21,199 | 21,199 | 21,199 |

Limits at the next thousand:

| Set | Tier A | Tier A + O3 | Tier A + B |
| --- | ---: | ---: | ---: |
| Runtime total | 72,000 | 71,000 | 71,000 |
| Always loaded | 29,000 | 29,000 | 29,000 |
| Review | 48,000 | 48,000 | 47,000 |
| Required verifier | 60,000 | 59,000 | 59,000 |
| Re-review | 56,000 | 56,000 | 55,000 |
| Verifier instructions | 18,000 | 18,000 | 18,000 |
| Verifier example brief | 22,000 | 22,000 | 22,000 |

- **Headroom differs a lot by tier.** Tier A leaves 32 always-loaded bytes under 29,000. Tier A + B leaves 983. Tier A + O3 leaves 54 bytes on runtime total and 36 on required verifier.
- **Three limits can fall today with no removal.** Always loaded, required verifier and re-review were raised by a thousand for #382 (`8af0d24`), and the later reverts brought the sizes back under the lower thousand.
- **No recommended removal lowers the verifier sets.**

### Pre-epic baseline

The always-loaded set was 29,444 bytes before the epic: 9,091 + 15,256 + 5,097 for `SKILL.md`, `rubric.md` and `output.md`. That holds at `72fe530` (the parent of the first #381 change), at `5b8c1c5`, and in the frozen A tree `c3c53da`.

The 240 bytes the tree carries above that baseline are the retained #382 bullet at `references/rubric.md:57` (221 bytes), 15 more bytes in `rubric.md` from the presentation change `de3edfa`, and a net 4 bytes in `output.md`. #381, #383, #384 and #385 were all reverted.

## What the guardrail run can and cannot see

Of the 78 retained compositions under `bench/runs/*/attempts/`, 77 are range targets. None has a question or a prior item. So the #394 validation run exercises the text around R1, R2, R6, R7, R9 and R10 on every review, and cannot observe R3, R4 or R5 (re-reviews) or R8 (working-tree snapshots). Those four rest on script and duplicate evidence alone.

## Restore signals

| Signal in the trimmed tree's runs | Restore |
| --- | --- |
| Median per-target cost or elapsed-to-payload rises, with longer summaries | R1 |
| `observation-form` or `question-form` refusals appear | O3 |
| Refusals naming `run.target`, `run.issues` or `run.change_description` rise | R10 |
| `derived-field` refusals for `packet_context` appear | R6 |
| A validity regression on any target | R1 first, then the tier B set |

## Sections examined and kept

| Section | Bytes | Why a reader would expect it | Why it stays |
| --- | ---: | --- | --- |
| `SKILL.md:41-56`, Verification | 2,461 | #386 and #387 targeted its cost | Protected by the issue. The audit declines to call it dispensable (`a-phase-audit.md:134-137`, `:233`). The finalizer enforces confirmation (`render_review.py:1989-1993`) but not which candidates are mandatory or when a premise is owed. |
| `SKILL.md:57-67`, Status | 767 | The finalizer checks status against blockers and coverage (`render_review.py:1332-1368`) | Status is the decision. The script leaves `Needs Information` against `Approved` to the reviewer, and cannot derive coverage. |
| `SKILL.md:74-80`, Modes | 1,151 | Session text is inert in one-shot, which every skill caller and the benchmark use | `session` is the default for a person. Parts repeat at `references/targets.md:37`, `:41` and `:45`, but the unique rules do not separate into whole paragraphs. |
| `references/rubric.md:1-12`, licence header | 434 | Loaded on every run and carries no rule | Apache-2.0 requires modified files to carry a change notice and to retain attribution (`skills/review-code/licenses/Apache-2.0.txt:97-104`). |
| `references/rubric.md:17-26`, Admission | 1,696 | Largest block of judgment prose | Protected by the issue. |
| `references/rubric.md:35-38`, Conformance | 1,574 | No `artifact-` row in any retained composition | It defines when a requirement row exists. The builder requires its bundle (`build_verifier_prompt.py:128-129`) and `references/verifier.md:46-48` depends on it. The benchmark cannot detect its loss. |
| `references/rubric.md:39-46`, Released compatibility | 1,952 | Long and conditional | The builder embeds it by heading (`build_verifier_prompt.py:305`). Seven retained findings are `compatibility`. |
| `references/rubric.md:47-59`, Changed tests | 2,954 | Long | The builder embeds it by heading (`build_verifier_prompt.py:302`) and `test_verifier_handoff.py:248-251` asserts the embedding. It holds the #382 bullet. |
| `references/rubric.md:60-65`, Supplied checks format and reuse | 1,663 | Near copy of `references/verifier.md:40-44`; default input is none | `skills/implement-publish/SKILL.md:24` and `skills/implement-publish/references/continuation.md:15` read it. The worker never loads the rubric, so the two copies serve different readers. |
| `references/rubric.md:76-83`, Priority and action | 1,009 | Partly enforced (`render_review.py:1060-1061`) | #381's rejected variants lost registered defects (`skills/review-code/DESIGN.md:120`), so this text is known to move outcomes. |
| `references/rubric.md:84-86`, Survivor record | 617 | Field list and kinds are enforced by both scripts (`build_verifier_prompt.py:139-141`) | It carries the rule that a confirmation survives a lowered priority, which the baseline exercised (`a-phase-audit.md:198`), and the kind choice that triggers the concurrency check. `references/verification.md:29` refers to it by name. |
| `references/output.md:7`, `:9`, `:13`, authoring contract | 609 + 404 + 621 | Several sentences restate finalizer checks | Each paragraph mixes enforced sentences with judgment rules. Cutting the enforced sentences is scattered trimming, and `skills/review-code/DESIGN.md:42` already records more finalizer repairs as an open risk. |
| `references/targets.md:25-28`, Recorded deferrals | 1,458 | Long; pull-request only | Precision rule from #139, referenced by `references/rubric.md:25`. 77 of 78 retained compositions are range targets, so the guardrail cannot see it. |
| `references/prior-state.md:13-18`, Duplicate-review shortcut | 1,842 | Describes what `forge_packet.py shortcut` prints | The reviewer must interpret the lines, and the exit-1 thread-state match is a judgment. |
| `references/verification.md:25-42`, Build input | 3,140 | The builder refuses by field | `--example` shows no `conformance` or `released_compatibility`, and `docs/review-code/HISTORY.md:1105` kept these on purpose. |
| `references/verification.md:43-63`, Commands and artifacts | 3,066 | Describes script exits | Structural repair was exercised in the baseline (`a-phase-audit.md:200`). |
| `references/verifier-concurrency.md:7-15` | 1,892 | Repeats rubric rules | Worker-only text. A malformed return withholds its tasks and spends the allowance, which changes coverage and status. 44 retained premises are `concurrency`. |

## Problems noticed outside the change

- `references/rubric.md:66` names the disposition `unused/unavailable` and omits `failed`. The finalizer accepts `failed` and `unavailable` and refuses `unused` (`render_review.py:912`).
- `run.prior_head` is named only in the finalizer's docstring (`render_review.py:57`). No reference and no `--example` output names it, and the finalizer does not derive it from the store.
- The finalizer does not require a `reason` for an `unavailable` or `failed` check, though `references/rubric.md:66` does.
- `references/targets.md:31` says every local run is a first review. `references/prior-state.md:7` allows a local re-review with a `prior_record`.
- `docs/research/builtin-review-benchmark-2026-09-24/comparison-data.md:3-7` is still a placeholder saying no scored cell has run.
- #394 cites `ledger.md:123` for the 5.3x ratio. That line is an attempt row. The ratio comes from `README.md:512-517`.

## Verification

`measure.py` extracts the pinned commit into a temporary directory, removes the named spans from the copy, and runs the copy's budget check and tests. It refuses a span whose size differs from the figure recorded here. The checkout is never written.

| Tree | Always loaded | Tests under `skills/review-code/scripts/` |
| --- | ---: | --- |
| Untrimmed | 29,684 | 9 of 9 pass |
| Tier A | 28,968 | 9 of 9 pass |
| Tier A + O3 | 28,715 | 9 of 9 pass |
| Tier A + B | 28,017 | 9 of 9 pass |
| O4 alone | 29,684 | `test_verifier_handoff.py` fails |

```sh
python3 docs/research/review-code-removal-candidates-2026-09-27/measure.py --tests R1 R2 R3 R4 R7 R8 R9
python3 docs/research/review-code-removal-candidates-2026-09-27/measure.py --tests R1 R2 R3 R4 R7 R8 R9 R10 R5 R6 O3
```

Not verified:

- **Behaviour.** No benchmark was dispatched, so the no-regression and cost guardrails in #394's validation plan are untested.
- **Repair frequency** after removing authoring hints.
- **The effect of R3, R4, R5 and R8**, which the benchmark's targets cannot exercise.
