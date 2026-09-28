# Which large parts of `review-code` are worth testing for removal

Analysis only, at commit `ca29bad`. No skill text, script, test or limit was changed, no
benchmark was dispatched and no model-backed review was run. `skills/review-code` at this commit
is tree `5e12864b52b6c0c52b9b1b1f41d5b22fa2576676`, the tree the #394 run names as its control
(`bench/runs/2026-09-27-x394-staged-guardrail/README.md:74-75`).

Paths are relative to the repository root. Inside tables, `SKILL.md`, `references/…` and bare
script names are under `skills/review-code/`.

Every figure comes from two scripts beside this note. `measure.py` gives sizes, exercise counts,
outcome joins, cost attribution and the error rates of the test rules. `variants.py` builds
trimmed copies in a temporary directory and runs the budget check and the tests on them. Both
only read the repository. [SYNTHESIS.md](SYNTHESIS.md) records how this note was produced.

## Result

Issue #394 asked which paragraphs could go. This note asks which **parts** earn their place. A
part is a mechanism that can be switched off as one unit.

| Part | Instruction bytes | Share of recorded spend | What the filed record shows | Verdict |
| --- | ---: | ---: | --- | --- |
| Independent verification | 25,284 (35% of the runtime set) | 18.5% | The verifier disagreed with the reviewer 2 times in 93 rulings. Both times the review got worse | **Test first** |
| Requirements ledger | 3,333 | About 1% | 263 rows, no requirement finding. No pinned target can show its benefit | Test second, only as an extra arm |
| Record and finalizer contract | 5,760, plus 4,459 of example | 11.6%, plus 9.8% reading script source | 46 of 115 finalizer runs were refused. 26 of 65 reviews read the finalizer's source | Repair for free first |
| Re-review and pull-request target | 14,768 | About 2% | 0 of 65 reviews exercise either | Cannot be tested on these targets |
| Admission core | 5,196 | Not separable | The likely source of the skill's precision. Rewording it lost defects twice | Keep |
| Skill frame, status, modes | 5,971 | Not separable | Status is the decision callers gate on | Keep |
| Local pinning and context store | 5,913 | 3.3% | The pinned diffs are too small to exercise it | Keep |
| Changed tests and execution | 2,954 | 10.0% | Carries #382, the one retained addition | Defer |
| Supplied checks, released compatibility | 4,009 | Not separable | Barely exercised | Defer |

Five findings shape everything below.

1. **Verification is the only large part with evidence against it.** It is a third of the
   instruction text and about a fifth of the spend. Across every filed review it changed an
   outcome twice. It refuted a real defect, and it confirmed a finding that grading ruled false.
2. **Cost follows model turns, not bytes.** `review-code` makes 20 requests per review and the
   built-in reviewer on the same model makes 4. One kilobyte of instructions costs about $0.002
   to $0.004 per review. No byte saving can repay a paid run. Only removing turns can.
3. **Removing verification does not close the cost gap.** It would leave `review-code` at about
   four and a half times the built-in's cost. Roughly a third of the spend goes to looking at
   the change. The rest is process.
4. **No test can use historical reviews as its control.** Reviews under the current harness cost
   3.6 times the baseline's and take five times as long. The current tree has no filed review at
   all. The first purchase has to include control cells.
5. **The pass rules matter as much as the variant.** #394's Stage 2 recall rule would have
   rejected a change that does nothing about nine times in ten. The first draft of this note's
   own rules did so 63% of the time. The rules in section 5 are set by simulation and state their error rates.

**First test:** verification off against a matched control, eight cells, **$40 cap**, about $21
expected. Section 7 has the detail.

## 1. Map of the skill as functional parts

Sizes are bytes from the files (`measure.py sizes`). The eleven parts cover all 73,188 bytes of
the runtime set. The column totals equal the five figures `test_instruction_budget.py` measures.

Loaded sets: RT runtime files, AL always loaded, RV review, RQ required verifier, RR re-review,
WB source of the worker brief. RV, RQ and RR include the helper output a path prints.

| Id | Part | Instruction text | RT | AL | RV | RQ | RR | WB | Scripts, bytes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| V | Independent verification | `SKILL.md:41-56`; `references/verification.md`; `references/verifier.md`; `references/verifier-concurrency.md` | 25,284 | 2,461 | 2,461 | 14,638 | 2,461 | 12,988 | `build_verifier_prompt.py` 17,962; `account_verifier_return.py` 12,482; 16,929 of `render_review.py` |
| P | Re-review and prior state | `references/prior-state.md` | 9,193 | 0 | 0 | 0 | 9,193 | 0 | 17,279 of `render_review.py`; part of `forge_packet.py` |
| K | Skill frame: inputs, boundaries, steps, status, modes | `SKILL.md:1-40`, `:57-67`, `:74-80` | 5,971 | 5,971 | 5,971 | 5,971 | 5,971 | 0 | none |
| L | Local pinning and context store | `references/targets.md:1-4`, `:29-67` | 5,913 | 0 | 8,687 | 8,687 | 8,687 | 0 | `review_context.py` 98,915 |
| R | Record, finalizer and rendering contract | `references/output.md`; `SKILL.md:68-73` | 5,760 | 5,760 | 10,219 | 10,219 | 10,219 | 0 | `render_review.py` 198,145 |
| F | Pull-request target | `references/targets.md:5-28` | 5,575 | 0 | 5,575 | 5,575 | 5,575 | 0 | `forge_packet.py` 70,789 |
| A | Admission core | `references/rubric.md:1-26`, `:68-86` | 5,196 | 5,196 | 5,196 | 5,196 | 5,196 | 0 | none |
| Q | Requirements ledger | `references/rubric.md:27-38` | 3,333 | 3,333 | 3,333 | 3,333 | 3,333 | 0 | none |
| T | Changed tests and execution | `references/rubric.md:47-59` | 2,954 | 2,954 | 2,954 | 2,954 | 2,954 | 0 | the builder embeds it in every brief |
| S | Supplied check evidence | `references/rubric.md:60-67` | 2,057 | 2,057 | 2,057 | 2,057 | 2,057 | 0 | none |
| C | Released compatibility | `references/rubric.md:39-46` | 1,952 | 1,952 | 1,952 | 1,952 | 1,952 | 0 | the builder embeds it when supplied |
| | **Total** | | **73,188** | **29,684** | **48,405** | **60,582** | **57,598** | 12,988 | |

Units nested inside a part, which a narrower variant could remove:

| Unit | Inside | Bytes |
| --- | --- | ---: |
| Safety premises | V | 2,194 |
| Concurrency bug-class check | V | 2,381 |
| Conformance rows | Q | 1,574 |
| Modes | K | 1,151 |
| Status | K | 767 |
| Licence header | A | 434 |

This map assigns whole sections. `verification.md` and `verifier.md` also hold lines about
supplied checks, conformance, compatibility and changed tests. Counting those lines under their
own parts puts verification at about 21.9 KB. The removal measured in section 4 is the same
either way.

Not in any loaded set: `DESIGN.md` 30,199, `licenses/Apache-2.0.txt` 11,357,
`THIRD_PARTY_NOTICES.md` 1,391, `agents/openai.yaml` 181, and the test files.

**What a review loads in practice.** All 65 valid reviews are range targets. Each read
`SKILL.md`, `targets.md`, `rubric.md` and `output.md` (`measure.py phases`). Beyond that:

| Source | Valid reviews that read it | Reviews it applies to |
| --- | ---: | ---: |
| `verification.md`, 9,835 B | 64 of 65 | 38 dispatched a batch |
| `prior-state.md`, 9,193 B | 16 of 65 | 0 are re-reviews |
| `verifier.md`, worker-only | 15 of 65 | 0; the builder embeds it |
| `verifier-concurrency.md`, worker-only | 14 of 65 | 0; the builder embeds it |
| The pull-request half of `targets.md`, 5,575 B | 65 of 65 | 0 are pull requests |
| Source of `render_review.py` | 26 of 65 | not an instruction file |

The load conditions in `SKILL.md` do not stop these reads. Under enforced isolation 12 of 13
reviews read `prior-state.md` on a first review.

## 2. What each large part is assumed to provide, and the evidence

### Populations

| Population | Valid reviews | Mean cost | Median elapsed | Primary requests per review |
| --- | ---: | ---: | ---: | ---: |
| Frozen baseline arm A | 20 | $0.75 | 134 s | 17.9 |
| #381 to #385 variants, no enforced isolation | 32 | $1.11 | 175 s | 24.3 |
| Enforced isolation: #384 matched, #384 staged gate, #394 | 13 | $2.72 | 650 s | 56.7 |

85 `review-code` compositions are filed outside the toy run. 65 come from valid reviews. The
other 20 are harness-invalid for access-audit reasons that have nothing to do with review
quality. They are excluded from every rate below and cited only as evidence of how a mechanism
behaves.

### Where the money goes

**Measured.** `measure.py phases` joins each archived `review-code` transcript to its priced
requests. The join's total equals every filed charge to within $0.000001. It reads only
`review-code` archives and prints only aggregates.

**Estimated.** The split between phases. It charges each request to the action it emits. The
#386 audit left 93.4% of cost unattributed
(`docs/research/builtin-review-benchmark-2026-09-24/a-phase-audit.md:120`). This closes that gap
with a stated allocation. **It is not what removal would save.** Removing a phase also shrinks
the context of every later request, and the reviewer may spend the freed effort elsewhere. Other
defensible allocation rules put verification between 15% and 20%.

Share of spend by turn:

| Activity | Baseline, 20 | Enforced isolation, 13 | All valid, 65 |
| --- | ---: | ---: | ---: |
| Inspecting the repository | 13.2% | 30.5% | 22.7% |
| Running tests and scratch experiments | 12.0% | 8.7% | 10.0% |
| **Looking at the change, subtotal** | **25.2%** | **39.2%** | **32.7%** |
| Reading `SKILL.md`, rubric, output, targets | 25.9% | 7.0% | 15.5% |
| Reading helper examples and help | 7.4% | 5.0% | 6.0% |
| Reading script source | 1.7% | 15.2% | 9.8% |
| Context store: build and selector reads | 5.1% | 1.4% | 3.3% |
| Verification: primary side and its references | 11.5% | 8.6% | 9.9% |
| Verification: worker requests | 6.6% | 10.7% | 8.6% |
| Record authoring and finalizer | 13.1% | 10.9% | 11.6% |
| Closing message | 3.4% | 1.6% | 2.4% |

**What a kilobyte costs.** One kilobyte is about 250 tokens. It is written to the cache once and
read on every later request. At the frozen rates that is about $0.002 per review at 20 requests
and $0.004 at 57. #394's seven removals saved about 0.7 KB, worth less than a cent per review.

### V. Independent verification

**Assumed benefit.** A fresh-context verifier removes false findings before they publish and
challenges the premises behind a clean verdict (`skills/review-code/DESIGN.md:9`).

**Measured, from the filed records** (`measure.py exercise`, `outcomes`, `machinery`):

| Measure | Valid reviews, 65 | All filed, 85 |
| --- | ---: | ---: |
| Reviews that dispatched a batch | 38 | 57 |
| Batches with safety premises only | 12 | 24 |
| Follow-up batches | 0 | 1 |
| Candidate tasks | 32 | 39 |
| Candidates confirmed | 31 | 38 |
| Candidates refuted | 1 | 1 |
| Safety-premise tasks | 29 | 54 |
| Premises ruled `holds` | 29 | 53 |
| Premises ruled `fails` | 0 | 1 |
| Questions, outstanding tasks | 0 | 0 |

**Every ruling that changed an outcome, and what grading said about it:**

- **The one refutation removed a real defect.** In the #383 run a tRPC review raised a
  compatibility candidate, the verifier refuted it as intended behaviour, and the review was
  `Approved` (`bench/runs/2026-09-26-x383-consumer-comparison/attempts/att-006/composition.json:78-82`,
  `bench/runs/2026-09-26-x383-consumer-comparison/README.md:100`). An independent adjudicator
  then reproduced the claim and registered it as GT-j3
  (`bench/targets/j-trpc-5017/register.v3.json:47-61`).
- **The one failed premise produced a false finding.** It reopened as a candidate, a follow-up
  batch confirmed it, and grading ruled it false
  (`bench/runs/2026-09-27-x384-matched-isolation/attempts/att-003/composition.json:135-142`,
  `bench/runs/2026-09-27-x384-matched-isolation/scoring/r-base-ui-5460/mapping.v1.json:68`). The
  attempt is harness-invalid.

**What the confirmations were worth.** Of 38 graded findings that carry a `confirmed` ruling, 34
are registered defects, 3 are false findings and 1 is a non-material blocker. The three false
findings are in harness-invalid attempts, one of them on the clean gRPC target.

The 31 confirmations in 32 valid candidates have two readings. Either the reviewer's own
falsification had already filtered well, or the verifier is a lenient filter. The three confirmed
false findings support the second reading. The filed record cannot separate them.

**What the verifier never saw.** The only false finding in a valid review is a `consider`
performance finding in a review with no batch
(`bench/runs/2026-09-27-x394-staged-guardrail/attempts/att-008/composition.json:25-28`). The
finalizer requires confirmation only of `must-fix`, security and compatibility findings
(`skills/review-code/scripts/render_review.py:905`, `:1988-1993`).

**Premises did not reach the missed defects.** 16 valid reviews approved a buggy change with
nothing recovered. Two of them raised premises, and all of those held.

**Measured, cost.**

| | Baseline | Enforced isolation |
| --- | ---: | ---: |
| Reviews with a batch | 10 of 20 | 8 of 13 |
| Mean cost, with and without a batch | $0.93, $0.58 | $3.20, $1.95 |
| Verification's spend per review with a batch | $0.23 to $0.34, 25% to 36% | $0.82 to $1.14, 26% to 36% |
| Same, when the batch holds premises only | $0.26 to $0.36 | $0.89 to $1.22 |
| Verifier wait plus model time on the phase | 59 s of 179 s | 288 s of 869 s |
| Builder runs refused | 5 of 15 | 8 of 19 |

The lower figure in each range charges verification for its own output and the context it added.
The higher one adds its turns. Reviews without a batch still spend 3% to 5% reading its
instructions. Verification in reviews whose batch holds premises only is 7% to 10% of all
recorded spend, and 13% to 17% under enforced isolation.

**Evidence for the part, outside the filed benchmark.** The design history records one valid
refutation in a prototype run (`docs/review-code/HISTORY.md:556`), and a prototype verifier that
caught a fabricated citation
(`docs/research/prototype-runs-2026-09-01-test-4/comparison-data.md:159`). The same history
records a verifier that upheld a wrong refutation
(`docs/research/prototype-runs-2026-09-01-test-2/comparison-data.md:71`). Those runs predate the
current design and are not graded under this benchmark's registers.

**Inferred.** A verifier may deter weak candidates before dispatch. Dropped candidates leave no
record (`skills/review-code/SKILL.md:37`), so the filed data cannot show it. Only a matched run
can.

### R. Record and finalizer

**Assumed benefit.** A validated record that callers consume without parsing prose.
`review-code-publish` posts `batch.json`
(`skills/review-code-publish/references/publication.md:103`) and `implement-publish` reads
`report.md` (`skills/implement-publish/SKILL.md:51-53`).

**Measured.**

- All 65 valid reviews produced a filed payload.
- 46 of 115 finalizer runs were refused. 36 of 65 reviews needed two or more runs. Under enforced
  isolation 10 of 23 runs were refused and 3 of 13 reviews finished without a refusal.
- Record authoring is 11.6% of spend and reading script source 9.8%. Under enforced isolation
  they are 10.9% and 15.2%.
- At least 26 of 65 reviews read the source of `render_review.py`, 127 times. 122 of those reads
  come before the first finalizer run, so they are contract lookups, not repairs. Under enforced
  isolation it is 10 of 13 reviews and 82 reads. The count covers direct reads and searches only.
- `render_review.py --example` prints a composition whose `run` holds only `coverage` and
  `specs`. The six local-target fields are given in prose only
  (`skills/review-code/references/output.md:25`, `skills/review-code/references/targets.md:67`).
  Every pinned target is a range target.
- The composition is 77% bookkeeping by bytes. Findings and observations are 23%.

**Inferred.** The source reads look for the fields the example omits. Of the 26 reviews, the
reads of 8 name `change_description`, of 6 `repository` and of 6 `target_kind`. Most name no
field, so this is not established.

**Not measurable here.** The pinned targets publish nothing. The benchmark can see the record's
cost and cannot see its value to a caller.

### Q. Requirements ledger

**Assumed benefit.** Listing requirements before reading the diff catches omitted or
contradicted requirements (`skills/review-code/SKILL.md:35`).

**Measured.**

- 263 rows in 65 valid reviews, 4.0 per review. 179 are acceptance rows that ended `met`.
- No valid review carries a `kind=requirement` finding. Every acceptance row short of `met` sits
  in a review that carries a finding of another kind, so the ledger mirrored findings and never
  originated one.
- No row has an `artifact-` source, so conformance (1,574 B) was never exercised.
- The benchmark feeds the ledger on every target, because the pull-request text arrives as a
  supplied spec (`bench/tools/dispatch.sh:112`). None of the 13 registered defects is an omitted
  requirement. All are regressions the change introduced.

**Inferred.** Reading intent first may help discovery. The filed data cannot separate that from
inspection.

### The other parts

| Part | Assumed benefit | Measured | What the pinned targets cannot show |
| --- | --- | --- | --- |
| L context store | Complete-diff coverage and bounded output | 3.3% of spend. All 181 files are `reviewed` | Truncation recovery: the reviews average 2.8 changed files |
| T changed tests | Evidence from focused runs | Execution is 10.0% of spend. 64 reviewer-executed checks in 42 reviews. #382's rule raised GT-k1 to `must-fix` in 3 of 3 (`bench/runs/2026-09-26-x382-destroyed-tests/README.md:70`) | Whether a run, not a trace, decided a finding |
| A admission core | Precision | 1 false finding in 65 valid reviews. Wording changes here lost registered defects twice (`skills/review-code/DESIGN.md:120`) | Nothing: every review exercises it |
| K status and action | A merge decision | 4 of 8 baseline approvals carried a recovered defect at `consider` (`docs/research/builtin-review-benchmark-2026-09-24/README.md:532-535`). 0 questions in 85 compositions | Session mode |
| P re-review | State carried across reviews | 0 prior items in 85 compositions | Everything |
| F pull-request target | Forge inputs and deferrals | 0 pull-request targets | Everything |
| S supplied checks | Reuse of caller evidence | 3 accepted checks, all from pull-request text | The benchmark supplies no check evidence |

## 3. Comparison with the built-in reviewers

Arm figures are from `docs/research/builtin-review-benchmark-2026-09-24/README.md:447-452` and
`:478-483`. Requests and items per review are from the filed attempt records. No built-in or
Codex transcript was read.

| Per valid review | A `review-code` | B built-in Sonnet | C built-in Opus | D Codex |
| --- | ---: | ---: | ---: | ---: |
| Billed requests | 20.1 | 3.8 | 8.7 | 4.6 |
| Output tokens, median | 14,400 | 2,635 | 8,194 | 631 |
| Cost | $0.75 | $0.13 | $0.38 | $0.30 |
| Instruction bytes | 48,405 on the review path | 6,541 | 5,657 | not recorded |
| Items reported | 1.75 | 3.75 | 8.35 | 0.85 |
| Recall | 0.708 | 0.792 | 0.844 | 0.573 |
| False findings | 0.00 | 0.10 | 0.35 | 0.00 |

**What the built-ins do without.**

| | A | B | C | D |
| --- | --- | --- | --- | --- |
| Discovery | One reviewer, one pass | 3+5 angles, 6 candidates | 8 inline angles | One pass |
| Verification | Mandatory for `must-fix` and risk areas; safety premises | One vote, recall-biased | None | None |
| Requirements ledger, per-file coverage, status | Yes | No | No | No |
| Record for a caller | Four validated artifacts | A list of findings | A list of findings | A list of findings |
| Approving form | `Approved` | An empty list only | An empty list only | An empty list only |

Discovery and verification are the variant labels at `bench/harness/claude-code.json:9-20`. B
against C is not a model ablation, because their prompts differ
(`docs/research/builtin-review-benchmark-2026-09-24/README.md:52-54`).

**Which parts plausibly explain each difference.** All of this is inference.

| Difference | Most plausible part | Basis | Strength |
| --- | --- | --- | --- |
| Fewer false findings | A, the admission bar | D runs the rubric that `rubric.md` derives from (`skills/review-code/references/rubric.md:2-3`) with no verifier, ledger or record, and also has 0 false findings. V's rulings never removed a false finding | Weak. D is another model, and 0.00 against 0.10 is two reviews, inside the benchmark's own noise caveat (`docs/research/builtin-review-benchmark-2026-09-24/README.md:545-546`) |
| Less noise | A, and the three-observation cap | A reports 1.75 items against 3.75. 66 of A's 81 non-material items in valid reviews are observations | Moderate |
| Lower recall | No part adds discovery effort | A spends $0.19 a review looking at the change, where B's whole review costs $0.13 and covers several angles. 4 of 70 observations were defects demoted to non-actionable facts | Moderate |
| Approvals of buggy changes | K status and the `consider` action | An empty list is the built-ins' only approving form (`docs/research/builtin-review-benchmark-2026-09-24/README.md:529-531`). Half of A's approvals carried a recovered defect | Strong |
| About five times the cost | Turn count: instructions, R, V | 20 requests against 3.8. Two thirds of A's spend is process | Strong |

Every defect A recovered in the baseline was also recovered by B and C
(`docs/research/builtin-review-benchmark-2026-09-24/README.md:485-498`). What A buys with its
process is fewer false findings and less noise. The evidence points at the rubric more than at
the machinery around it, and that is the claim the first test checks.

## 4. Ranked shortlist

The spend figures below are what the record attributes to each part. The saving from removing a
part is the thing the test measures. It is not known in advance.

### 1. V: remove the independent verification phase

| | |
| --- | --- |
| Size | 25,284 B of text, 35% of the runtime set. Measured on a trimmed copy: always loaded 29,684 → 26,516, review 48,405 → 45,237, runtime total 73,188 → 47,197 |
| Text that changes | Delete `SKILL.md:41-56` and step 6 (`:38`). Drop the verification clauses at `SKILL.md:59`, `:64`, `:80`, `rubric.md:45`, `:53`, `:64`, `:72`, `:74`, `:86`, `output.md:3`, `:35`. Stop loading `verification.md`, `verifier.md` and `verifier-concurrency.md`; adoption deletes them |
| Scripts that change | Remove the confirmation requirement at `render_review.py:1988-1993`. Adoption deletes `build_verifier_prompt.py`, `account_verifier_return.py` and `test_verifier_handoff.py`, and changes `test_instruction_budget.py`, which imports the builder |
| What breaks | Four test cases that assert the requirement: three in `test_render_review.py` and one in `test_render_composition.py`. Every other test file passes (`variants.py --tests V`). `skills/implement-publish/references/continuation.md:17` and `prior-state.md:31` describe carried confirmations and need follow-up |
| Attributed spend | 18.5% overall. 25% to 36% of each review that dispatches a batch. One to five minutes of elapsed time |
| Hypothesis | The reviewer's own falsification already does the filtering. Removing the verifier changes neither false findings nor recall, and lowers cost |
| Targets that can observe it | Requests (7 of 7 valid reviews dispatched a batch), Bokeh (6 of 6), gRPC (8 of 8, premises only), Hono (5 of 7). Partly GraphQL, tRPC and Base UI (3 each) |
| Targets that cannot | ripgrep (0 of 4) and soba (1 of 10). Astro cannot run under enforced isolation. No target has a destructive migration or data loss |
| Shows the part pays | The variant carries more false or non-material findings among those the verifier would have ruled on, or loses recall or remedy quality, by the margins in section 5 |
| Shows it does not | Matched on those measures within the margins, and cheaper by the margin in section 5 |
| Main risk | Deterrence the record cannot show. A false `must-fix` blocks a merge, so one of them costs more than one missed `consider`. A pass on five small targets says little about security and migration changes, where the verifier claims its value |

**Fallback, fixed in advance.** If V is rejected on candidate confirmation, test safety premises
alone (`variants.py --tests S`). It removes the Safety premises paragraph of `SKILL.md` and the
reconcile rule in `verification.md`: always loaded 29,684 → 28,996, required verifier 60,582 →
59,643. It needs no script change and every test passes. The worker's premise section stays,
because `test_verifier_handoff.py:141-143` asserts its heading. All 29 premises held in valid
reviews, and verification in premise-only reviews is 7% to 10% of all spend.

### 2. Q: remove the requirements ledger

| | |
| --- | --- |
| Size | 3,333 B at `rubric.md:27-38` plus 147 B elsewhere. Measured: always loaded 29,684 → 26,204, every path down 3,480 |
| Text that changes | Delete the section. Step 3 becomes "read intent before the diff". Three phrases in Released compatibility stop naming the row. `record.requirements` is written empty |
| Scripts that change | None. The finalizer checks row shape only (`render_review.py:2049-2055`) |
| What breaks | Nothing: all ten test files pass (`variants.py --tests Q`). The conformance procedure at `verifier.md:46-49` loses its source of rows |
| Attributed spend | About 1%. The rows are about 1.3 KB of output per review |
| Hypothesis | The ledger does not change findings on these targets |
| Targets that can observe it | All, for harm: lost recall on GraphQL, Bokeh, ripgrep and Hono |
| Targets that cannot | None can show the benefit. No registered defect is an omitted requirement |
| Shows the part pays | Recall or correct action falls against the matched control |
| Shows it does not | No loss within the margins. That is a statement about these targets only |
| Main risk | Adopting on evidence that cannot see the case the ledger exists for. Adoption should wait for one target with an omitted acceptance criterion |

### 3. R: stop asking the reviewer for record bookkeeping

| | |
| --- | --- |
| Size | 5,760 B of text and 4,459 B of example loaded by every review. `render_review.py` is 198,145 B |
| Variant | The reviewer writes status, coverage, findings, questions and observations. The finalizer derives the file list and the local run identity from the store |
| Scripts that change | The composition readers and the example in `render_review.py`, and their fixtures. This is new script work |
| Attributed spend | Part of the 21% that record authoring and source reading take. Not estimable before the free step below |
| Targets that can observe it | All, for cost, time and payload validity. None can observe a caller |
| Main risk | It trades instruction text for script. The free repair may be the whole gain |

**Free first step.** Make `--example` print a local-target composition. It removes nothing and
adds no instruction file. It is the largest cost finding in this note that needs no experiment.
It is a change to the skill, so it lands on its own and stays out of the V test, whose control
is the current tree. The V test's control cells give the source-read and refusal counts to
compare against once it lands.

## 5. Test plan

### Why the control comes first

- **The current tree has no filed review.** Every filed attempt ran the frozen tree `c3c53da` or
  a variant of it. The #394 control arm,
  `bench/arms/review-code-sonnet-high-enforced-x394-control.json`, names the current tree and was
  never dispatched.
- **The current harness changed behaviour.** Under isolation 3 of 18 attempts carry a false
  finding, against 1 of 67 without it. Two of the three are invalid attempts and all three ran
  variant trees, so this is a warning and not a rate.
- **Recall under the current harness is unmeasured.** The #394 reviews recovered defects on 2 of
  6 buggy targets (`bench/runs/2026-09-27-x394-staged-guardrail/README.md:22-31`). The baseline
  recovered every defect on four of those targets. Nothing separates the trim from the harness.
- **Control cells are shared.** One control arm serves every variant tested under the same
  frozen harness.

### Rules common to every stage

Fixed before any dispatch, in the manifest:

1. **Matched pairs.** Control and variant run back to back on each target and replicate, order
   alternating, one review at a time.
2. **Jurisdiction.** Each false or non-material finding is classed before arm identity opens. It
   is *in jurisdiction* when the removed part governed it. For V that is a finding with action
   `must-fix` or kind `security` or `compatibility`. For Q it is a finding of kind `requirement`
   or one whose source is a requirement coordinate.
3. **No single event decides.** One false finding in one variant review is recorded and compared
   with the control. It rejects nothing alone.
4. **Differences, not counts.** Every rule compares the variant with its control over the same
   cells.
5. **Blind grading** with the existing template, all attempts of a target graded together, arm
   hidden. Invalid attempts are replaced within the cap and never graded into a rule.
6. **No extension.** Cells, caps and margins do not change after an outcome.

**The #394 event under these rules.** It was one `consider` performance finding with no control.
It is outside V's and Q's jurisdiction. It would be recorded and compared, and would reject
nothing.

### First test: V, staged

**Stage 0, free.** Build the variant tree, update the four test cases, run the tests and the
budget check, and repeat the native isolation checks with the fake API.

**Stage 1, futility.** Eight cells: control and variant on Requests, Bokeh, Hono and gRPC,
replicate 1.

| Outcome | Rule |
| --- | --- |
| Reject | On two or more of the four targets, the variant carries an in-jurisdiction false or non-material finding and its control does not |
| Reject | On two or more of the three buggy targets, the variant recovers no defect and its control recovers one |
| Reject | The variant's total review cost over the four targets is not below the control's |
| Stop, inconclusive | The control dispatches a batch on fewer than three of the four targets, so the stage cannot observe the part |
| Clear | None of the above. Stage 1 cannot pass the variant |

**Stage 2, decision.** 22 cells: replicates 2 and 3 on the same four targets, and three
replicates of GraphQL. With Stage 1 this gives 15 matched pairs.

| Measure over the 15 pairs | The variant passes when |
| --- | --- |
| Reviews carrying an in-jurisdiction false or non-material finding | Variant minus control is at most 1 |
| Reviews carrying any false finding | Variant minus control is at most 2 |
| Registered defects recovered | Variant total is at least control total minus 3, and no defect the control recovers 3 of 3 is recovered 0 of 3 |
| `must-fix` on recovered defects | Variant total is at least control total minus 3 |
| Sufficient remedies on recovered defects | Variant total is at least control total minus 3 |
| Invalid attempts | Variant is at most control plus 1 |
| Cost and elapsed | Median over targets of the variant-to-control ratio is at most 0.90 for each |

Any measure outside its margin rejects. A pass sends V to #380's unseen-target comparison, which
is a separate purchase.

### What these rules can and cannot detect

`measure.py rules` simulates both stages from the filed per-defect recovery rates. It assumes
reviews are independent and that the variant truly costs 0.75 of the control. It models the
false-finding, recall, action, remedy and cost rules. The any-false-finding, invalid-attempt and
elapsed rules are not modelled and can only add rejections, so Stage 2's figures are lower bounds.

| Scenario | Stage 1 rejects | Stage 2 rejects |
| --- | ---: | ---: |
| Variant changes nothing | 8% | 25% |
| Variant changes nothing, and control recall is 0.7 of the filed rate | 16% | 28% |
| Variant loses 20% of recoveries | 17% | 54% |
| Variant loses 40% of recoveries | 33% | 83% |
| Variant adds an in-jurisdiction false finding to 10% of reviews | 7% | 47% |
| Variant adds one to 25% of reviews | 28% | 90% |

The last two rows give the false-finding rule alone. The other rules add their own rejections.

For comparison, the same simulation on stricter rules:

| Rule set | Rejects a variant that changes nothing |
| --- | ---: |
| This note's rules | 25% |
| Margins of 1 on recall, action and remedy, and a cost limit of 0.85 | 63% |
| #394's Stage 2 recall rule alone: no target's recall below the control's, nine targets, 3 reviews per arm | 93% |

Three things follow.

- **A quarter of harmless variants still fail.** 15 pairs cannot do better without margins so
  loose that they miss real losses. A rejection at the edge of a margin is weak evidence.
- **A small loss can pass.** A variant that loses 20% of recoveries passes about half the time.
  The test is built to catch a part that matters a lot, not one that matters a little.
- **No single rule dominates.** Recall, action, remedy and cost each reject 6% to 8% of
  harmless variants in Stage 2.
- **The cost rule depends on the true saving.** If the variant saves 15% and not 25%, the cost
  rule alone rejects a third of the time. That is intended: a variant that saves less than 10%
  is not worth the change.

### Cost

From filed reviews of the same targets under enforced isolation: Requests $4.28, Bokeh $1.94,
Hono $1.89, gRPC $3.28 and $3.72, GraphQL $1.24. Those reviews ran the #394 trimmed tree and the
#384 trees, not the current tree, so every estimate inherits that difference.

| Stage | Cells | Expected reviews | Grading | Cap |
| --- | ---: | ---: | ---: | ---: |
| 1 | 8 | $11.60 control, about $8.70 variant | $0.80 | **$40** |
| 2 | 22 | about $47 | $1.00 | $70 |
| Both | 30 | about $69 with grading | | $110 |

The caps reserve $5 for each attempt in flight and $5 for closeout, as the #394 manifest did.

### Sharing and isolation

- **Can share a run and its control cells:** V, Q and the premise fallback, as separate arms.
  Q's first stage needs the variant on GraphQL, Bokeh, ripgrep and Hono and the control on
  GraphQL and ripgrep: six cells, about $11, because V's stage already buys the Bokeh and Hono
  controls.
- **Must not share a tree:** any two candidates. #407 put seven removals in one patch and its
  failure could not be assigned to one.
- **Cannot be tested on pinned targets at all:** P and F.
- **R** needs its free step and a specified variant before any cell is bought.

## 6. Examined and not proposed for a test

| Part | Bytes | Reason |
| --- | ---: | --- |
| P re-review and F pull-request target | 14,768 | No pinned target exercises them. A test needs a pull-request fixture with a prior review first. The load is a separate matter: 5,575 B of `targets.md` reach every local review and `prior-state.md` reached 16 reviews it did not apply to. Splitting `targets.md` by target kind changes no rule and is worth about 2% of cost, below what a paid run should decide |
| A admission core | 5,196 | The part most likely responsible for A's precision. #381 and #385 changed its wording and lost registered defects (`skills/review-code/DESIGN.md:120`) |
| K status, action and modes | 5,971 | Status is the decision and the callers' gate. Its effect on approvals is a policy, which #381 already tested |
| L context store | 5,913 | 3.3% of spend. The finalizer validates anchors against the store (`skills/review-code/scripts/render_review.py:1418`). The pinned diffs are too small to show what it is for |
| T changed tests and execution | 2,954 | Execution is 10% of spend, so turning it off was considered. It holds #382, the one addition the epic retained. By a keyword match, 10 of 34 recovered defects cite run output, including the only recoveries of GT-j2 and GT-r2, on the targets where recall is already weakest. Reconsider after V |
| C released compatibility | 1,952 | Seven `compatibility` findings in valid reviews. Under 2 KB, and the builder embeds it by heading. It would follow Q |
| S supplied checks | 2,057 | The pinned targets supply no check evidence. `implement-publish` reads the section (`skills/implement-publish/SKILL.md:24`). It could move behind a load condition, which needs no paid run |
| A "minimal skill" arm that removes every weak part at once | | The cheapest way to question everything, but a failure cannot be assigned to a part. That is #407's problem |
| Scripts, as bytes | 398,293 | Script bytes never enter the context. Their cost is the turns they take, counted under V, R and L |

## 7. Recommended first test and budget

Buy **Stage 1 of the V test**: eight cells, control and variant on Requests, Bokeh, Hono and
gRPC, under `claude-strict-v2`, with Stage 2 and its rules frozen in the same manifest.

- **Budget:** $40 cap for Stage 1, about $21 expected. Approve Stage 2's $70 cap only after a
  clear.
- **What it settles whatever the variant does:** the current tree's false-finding rate, recall,
  cost and time in the current harness, on four targets. Every later test needs those numbers.
- **Before it, at no cost:** Stage 0.
- **What is at stake:** 26 KB of instruction text, 30 KB of scripts, and an attributed fifth of
  the spend and a quarter of the elapsed time.

## Limits of this note

- **The cost split is an allocation.** Totals match the filed charges. The division between
  phases follows a stated rule and is not what removal would save.
- **The error rates come from a simulation.** It uses recovery rates from reviews that mostly ran
  without enforced isolation, and treats reviews as independent.
- **Precision is attributed to the admission core by inference.** No run has tested it.
- **Why reviews under isolation cost 3.6 times more** is not established. The harness, the later
  tree and chance are not separated by any filed run.
- **Whether verifier corrections changed a field or restated it** was not checked. 25 of the 32
  candidate returns carry corrections.
- **The V edit list** covers the always-loaded text and the finalizer. `prior-state.md` and the
  callers are named, not edited or tested.
- **The built-ins' internals** come from filed attempt records and the benchmark's variant
  labels.

## Problems noticed outside the task

- `render_review.py --example` shows no local-target `run` fields, and every benchmark review
  needs them.
- `verification.md` is read by reviews that dispatch nothing: 26 of 65.
- `rubric.md:72` allows a "verifier aside" as an observation. No worker return in 38 carries one.
- The question channel is unused: 0 questions in 85 compositions, all one-shot.
- In 12 of the 20 invalid attempts the first audit violation is a path under `/tmp`, mostly the
  review's private directory. No attempt under isolation has one.

## Reproduce

```sh
cd docs/research/review-code-large-part-ablation-2026-09-28
python3 -B measure.py sizes
python3 -B measure.py exercise
python3 -B measure.py outcomes
python3 -B measure.py phases       # reads review-code transcript archives only
python3 -B measure.py machinery    # same
python3 -B measure.py rules
python3 -B variants.py --tests base V S Q   # copies go to a temporary directory
```
