# One-shot code-review evaluation method

**Defined 2026-09-05 for [#131](https://github.com/kamui/skills/issues/131).** This is the
authoritative method for the next current-skill experiments. It defines a protocol and a
synthetic scoring example; it reports no experiment execution or results and authorizes no
paid dispatch. Each experiment must meet its ticket's prerequisites and freeze its own pins,
targets, configuration, and spend before starting.

## 1. Freeze the experiment

Commit the preregistration in the experiment's dated research bundle before inspecting any
candidate-arm output. Record its commit and timestamps, the method commit, hypothesis, arms,
planned cells, pilot order, replacement policy, thresholds below, and stopping caps. Subsequent
changes get a dated deviation with the original rule retained; they are never described as
preregistered. Shared prerequisites are [#136](https://github.com/kamui/skills/issues/136)
(repaired policy), [#130](https://github.com/kamui/skills/issues/130) (elapsed events),
[#96](https://github.com/kamui/skills/issues/96) (attempt accounting), and
[#97](https://github.com/kamui/skills/issues/97) (cache pricing). Check their completion before dispatch.

| Experiment | Frozen comparison and size | Prospective screening rule |
| --- | --- | --- |
| [#137](https://github.com/kamui/skills/issues/137) | Exact repaired #136 skill versus historical `3ff624a0a8b57e7096d8ad8263ac64a3fb3ccd83`; same model, effort and verifier configuration. Six fresh PRs: four buggy, two adjudicated clean; two runs per arm/PR = 24 planned cells. Two-target paired pilot first, with its valid rows included. At most two replacement cells: 26 attempts total. | Zero candidate-arm false findings, no additional false-clean outcomes, no worse completion rate, at least +10 percentage points in macro material recall, and at most 25% higher matched median billed cost. |
| [#124](https://github.com/kamui/skills/issues/124) | Same repaired skill, high/medium primaries with verifier effort fixed at high or the higher tested default. Three seeds per arm on known Hyper plus two per arm on each of two fresh reasoning-heavy PRs (including a clean high-risk case) = 14 cells. At most two replacement cells: 16 attempts total. | Zero candidate-arm false findings, no additional false-clean outcomes, no lower macro material recall or worse completion rate, and at least 20% lower matched median billed cost. Otherwise retain the default. |
| [#138](https://github.com/kamui/skills/issues/138) | Later, separate preregistration after #137/#124 results and its residual-discovery-gap entry condition. Consult that ticket for its three-arm design and thresholds. | No extra arm is authorized inside either evaluation above. Freeze its own targets, thresholds, equal maximum per-run budgets and spend cap before dispatch. |

For #137, cover cross-file conformance outside the diff, changed-test correctness,
concurrency/progress, and ordinary behavioral change. For #124, probe requested versus observed
primary/verifier effort in the actual installed runtime before the grid. Unsupported independent
effort controls are missing evidence. Record #70/PR #125 early dispatch in the repaired snapshot;
measure late mandatory candidates, follow-up use and incompleteness. A transport-only adapter
for the historical control must be pinned and documented, with equivalent normalized inputs for
both arms; it cannot backport improved discovery or admission policy.

Use separate fresh targets for #137 and #124, or preregister overlap before inspecting outputs.
Hyper, Typeshed and Cobra from the old holdout are regression fixtures, never fresh holdouts.
Do not pool unlike target sets or change model/policy mid-comparison.

**Budget gate:** using the actually available model and dated rate evidence, compute projected
spend for the full planned grid plus setup/probes and tool/repro charges. Write the estimate's
assumptions and a maximum spend of `min(1.5 × projected spend, $150)` per ticket, including pilot,
replacements, invalidated/discarded attempts and setup. Record equal per-pair execution and run
budgets. Before each dispatch, check remaining spend against a conservative upper bound for the
next work and observe available session/reset limits. Stop and report incomplete evidence if
runtime, attempt or spend caps prevent completion. Model substitution or buying a paid service
requires a new decision. This method itself does not spend that budget.

Zero newly adjudicated false findings is a small-pilot screening constraint, not a precision
guarantee; zero observed failures does not establish a population error rate. Failed or
inconclusive screens retain the measured baseline/default and name the failure stage. Quality
improvement that misses the cost gate is a reported tradeoff, not adoption. Unresolved truth or
missing usage that could change a threshold makes the decision inconclusive.

## 2. Prepare identical inputs and isolated execution

For every target pin repository/PR, base ref and SHA, head SHA, computed merge-base, diff manifest,
review identity and prior-review cutoff. Pin every arm's skill SHA and supporting definitions,
model identifier, requested and observed effort for primary and verifiers, runtime/version,
exact dispatch prompts, packet hash, dependency versions and timestamped configuration probes.
A seed means a fresh independent dispatch/context and clone; record an API seed if available,
otherwise label it a replicate ordinal. Freeze balanced/interleaved arm order and matching by
PR and replicate before running; retain actual order and cache/session conditions.

Independently collect and check ground truth before reviewer dispatch. Store a sealed defect
register with stable defect IDs, expected behavior, demonstrated consequence, evidence and
required corrective outcome. Record clean-target adjudication and plausible non-defects too.
The adjudicator must work independently of reviewer conclusions. Keep future fixes, hidden
answers and adjudicator notes outside reviewer-accessible directories, packets, history and
network paths. Build truncated mirrors containing only permitted history; record negative object
checks for known future fixes in each clone. Check any preinstalled dependency material for
answer leakage. Packets include the same legitimate specification, prior review state through
the frozen cutoff, guidance and evidence for every arm/seed; disclose preexisting hints.

Allow safe focused tests and repros in isolated disposable target clones. Preinstall/pin
dependencies where practical, with network setup completed before dispatch; reviewers run offline.
Default limits are **five minutes per focused command** and **ten minutes provisioning per target**.
Record any override prospectively, with its reason and equal application to both arms. Preserve
the target source tree and review identity; put generated build/cache files and temporary repro
harnesses in disposable locations. Record commands, exit status, timeout, logs and before/after
source identity checks. Exclude production services, credentials and destructive external effects.
Report unavailable paths honestly and give both arms the same constraint. A setup failure or a
failure also present at base is not automatically a new defect introduced by the PR; check the
base or establish the changed mechanism independently.

Preparation is complete when pins, sealed truth, leakage checks, execution allowances, setup
outcomes, cost projection and thresholds are recorded. Run harness/helper checks before reviewer
dispatch rather than charging each reviewer to demonstrate them.

## 3. Preserve every attempt and its output

A **cell** is one planned `(target, arm, replicate)` slot. An **attempt** starts at reviewer root
dispatch and has a unique never-reused ID. Every retry is another attempt mapped to its original
cell, with a reason and predecessor. Setup/probes that never dispatch a reviewer are separate
budget entries, not fabricated review attempts. Undispatched cells remain visible as unattempted.

Each attempt stores the final review payload separately from the research report/ledger, raw
transcripts of every worker/request, command logs, usage and timing sidecars, validity and
completion disposition. Render-only payloads are scored as the review that would be published;
keep the selected publication mode identical across a pair. No review is posted to an upstream
target without authorization. Preserve partial outputs, failures, discarded attempts and their
spend; record missing metering explicitly.

**Completed** means the pinned skill's required coverage, mandatory verification, validation and
final result/publication finished. A completed review can still miss bugs. An incomplete review
can have individually validated publishable findings; score those findings, but retain incomplete
status. A mandatory candidate reopened but still unpublishable contributes zero recovery. A
research ledger's discovery, refutation, confirmation or reopen is diagnostic, not a substitute
for a publishable finding. A harness-invalid attempt has zero admissible recovery in the
attempt-level score and remains in its denominators and cost totals; retain its raw claims for
auditing rather than treating them as valid skill evidence.

When a harness repair changes inputs or execution conditions, invalidate every affected pair,
including its previously successful counterpart, and rerun under one frozen repair. Each rerun
consumes a replacement attempt; if this cannot fit the two-replacement cap, end incomplete.
A replacement never erases its predecessor. Count an invalid attempt as operationally incomplete;
separately identify harness failures and skill failures. All planned cells need valid completed
outcomes before claiming a successful full-grid screen; otherwise report provisional comparisons
and the missing evidence.

## 4. Adjudicate and score

A **material defect** is an actionable correctness, security, data-integrity, compatibility,
meaningful performance, or explicit-requirement failure with demonstrated consequence. Link the
trigger, violated behavior and consequence to evidence at the pinned review identity. Deduplicate
manifestations sharing the underlying defect and required corrective outcome; separate defects
only when those differ. Assign final payload findings to defect IDs once per attempt. A true
material finding remains a recovery when its priority is wrong; record that priority/action error
separately. A partial symptom can recover the defect while its proposed fix is insufficient.

A **false finding** is a published/would-be finding whose asserted defect or consequence is
contradicted by the evidence or lacks the required support after adjudication. Retain counts of
both raw false finding items and unique underlying false claims (deduplicated within an attempt,
not across seeds); the zero-finding screen uses raw counts. Track unresolved adjudications
separately. Score questions (including whether answerable and outcome-changing), optional hygiene,
observations, unsupported acquittals, duplicate items and severity/action mistakes in separate
columns. They cannot increase material recall. A true fact requesting unjustified blocking action
gets an action error even when it is not a false factual finding; a fabricated material consequence
is also a false finding.

Unexpected plausible true findings go to independent adjudication with arm, model, seed and
performance labels removed. Check evidence and merge duplicates before unblinding. Version the
updated defect register, then rescore every arm/attempt against that same set. Report old/new
per-target defect counts, recall and clean/buggy classifications; if a clean target becomes buggy,
the changed target mix cannot silently satisfy the frozen four-buggy/two-clean design. Report the
deviation and incomplete qualification or obtain a new preregistration. Unresolved material truth
prevents a success claim.

### Denominators and comparison

Let `D_t` be the adjudicated unique material defects on target `t`, `R_i` the unique material
defects recovered in attempt `i`'s admissible final payload, and `S_i` those recovered defects with
sufficient proposed fixes. A sufficient fix restores the required outcome for all known
manifestations, with evidence; classify each as sufficient, partial/insufficient, absent, or
unresolved. Absent/unresolved fixes stay in the denominator, with zero sufficiency credit.

| Quantity | Definition and denominator |
| --- | --- |
| Per-attempt recovery and recall | Report `R_i` IDs/count and `R_i / D_t`. On adjudicated clean PRs (`D_t = 0`), recall is N/A, never 100%. |
| Fix sufficiency | `S_i / R_i`, N/A if nothing recovered. Also report sufficient-outcome recall `S_i / D_t` for buggy targets so missing defects remain visible. |
| False findings | Raw item count and unique false-claim count per attempt; sum raw counts over all attempts per arm for screening, with invalid-attempt claims identified separately. Optional false-item fraction = raw false items / all raw finding items, N/A for zero items; this is not material recall. |
| False clean | An attempt on a buggy PR explicitly returns Approved/clean/no material defects. Record the flag even if it also declares operational incompleteness. An honest incomplete/unknown result alone is not false clean. Report count and rate over all attempts on buggy PRs, plus completed-only count/rate. Separately report zero-recovery attempts that did not claim clean. |
| Completion | Valid completed attempts / all dispatched attempts per arm, including discarded/invalid attempts. Also report valid completed planned cells / planned cells, unattempted cells, and failure reasons. |
| Target recall | Mean of per-attempt recalls for that arm/target, including incomplete, discarded and invalid attempts. Separately mean over valid completed attempts only. A target with no attempts (or no completed attempts in the latter view) is unavailable, not zero or silently excluded. |
| Macro material recall | Equal-weight mean of target recall over buggy targets, with target count shown. Compute attempt-level and completed-only versions separately; missing target means leave the full macro unavailable. Clean targets remain outside both recall denominators. The screen uses attempt-level macro; also require the ticket's recall threshold on completed-only macro to expose selection effects. |
| Aggregate fix sufficiency | Sum `S_i` / sum `R_i` across the indicated attempt set, with raw totals; report each target too. Repeated recovery in different attempts is repeated work, not deduplicated across runs. |
| Efficiency | Total billed spend / sum `R_i` over all attempts; undefined if none recovered. Also total spend / valid completed attempts. Show completed-only spend/recovery alongside, never as a replacement for all-attempt accounting. |
| Union recall | Distinct defects recovered across seeds / `D_t`; diagnostic only. It cannot satisfy a per-review adoption threshold. |

For each arm, show every target/seed/attempt row plus min, median, max and sample size for recall,
cost and elapsed time (tail = observed maximum in this small pilot). Compare false-clean counts
and rates on identical target sets; neither may increase for a successful screen. Preserve
completed-only distributions alongside all-attempt distributions.

For matched cost, charge a cell **all** its attempts, including discarded predecessors. Match
cells by target and replicate. For each complete matched pair compute candidate cell billed cost
/ control cell billed cost; the median of these ratios is the matched relative billed cost.
The #137 gate is `<= 1.25`; #124 is `<= 0.80`. Also show absolute arm medians, per-target medians,
all-attempt spend and unmatched costs. A zero-cost control makes its ratio unavailable. Missing
pairs or unknown charges prevent a full-grid cost pass; cheap incomplete exits cannot establish
savings. Keep paired differences and seed distributions visible instead of reporting only a
pooled number.

## 5. Meter cost and elapsed events

For each request in primary and child transcripts retain request ID, actual model, usage fields
and dated provider rate evidence. Deduplicate repeated transcript records of the same request.
Compute billed cost as `(uncached input × input rate + sum(cache-write tokens by known tier ×
tier rate) + cache-read tokens × read rate + output tokens including thinking × output rate) /
1,000,000`, for rates quoted per million tokens. Count thinking once if already included in output.
Add actual tool/repro charges and account for setup, probes and discarded attempts separately in
the ticket total. Record cache tier/TTL, currency and discounts actually applicable. Unknown
cache tiers or missing usage get explicit uncertainty/bounds, never a silently assumed cheap tier
or zero charge. Use #97's supported accounting when available; no estimate establishes a billed
cost threshold when the uncertainty could change the decision.

Use #130's timing sidecar and implemented schema. Capture timezone-qualified ISO-8601 **root
dispatch**, **final validated payload**, and **final publication/result** events as they occur,
with completion mode (`publish` or `render-only`). Elapsed-to-payload is payload minus root;
elapsed-to-completion is publication/result minus root. Missing events stay unavailable; invalid
ordering is an input error. In render-only mode the final result is completion, with publication
absent. For failed attempts retain stop events and observed duration as censored attempt time,
not fabricated completion. Keep the historical sum of worker transcript spans as **agent span
sum**, since parent waits overlap children. Root first/last assistant timestamps can be a labeled
proxy only. Do not infer exact elapsed events from retrospective narrative. #130 owns the schema
and CLI; this document does not claim that unfinished instrumentation already exists.

Report raw billed spend as the decision quantity. A production-shaped figure subtracting estimated
research-report output cost is an **estimate**, not billed spend; show its subtraction and
assumptions separately. It does not replace total spend or the matched billed-cost gate.

## Worked synthetic scorecard

**Invented arithmetic only; no reviewer was dispatched.** Targets A and B have respectively two
and one material defects; C is adjudicated clean. One arm has two planned cells per target. All
costs below are hypothetical billed dollars, with no setup cost or missing usage. A1 and A2 share
no underlying defect. All publishable recovered findings below have sufficient fixes.

| Target/replicate | Defects `D_t` | Final outcome | `R_i` | Recall | Fix sufficiency | False items | False clean | Complete | Cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A/1 | 2 | A1 published twice (one duplicate); A2 missed | 1 | 1/2 | 1/1 | 0 | 0 | yes | $4 |
| A/2 | 2 | A1 published; A2 reopened but mandatory verification unfinished, unpublished | 1 | 1/2 | 1/1 | 0 | 0 | no | $3 |
| B/1 | 1 | Bug missed; Approved | 0 | 0/1 | N/A | 0 | 1 | yes | $2 |
| B/2 | 1 | B1 published | 1 | 1/1 | 1/1 | 0 | 0 | yes | $4 |
| C/1 | 0 | Approved, no findings | 0 | N/A | N/A | 0 | N/A | yes | $1 |
| C/2 | 0 | Approved, no findings | 0 | N/A | N/A | 0 | N/A | yes | $2 |

There are six attempts and six planned cells, no replacements. Completion is 5/6 attempts and
5/6 cells. Target recall is A `(1/2 + 1/2)/2 = 50%`, B `(0 + 1)/2 = 50%`, C N/A; macro recall is
`(50% + 50%)/2 = 50%` across two buggy targets. Completed-only A recall is 50% (one run), B 50%
(two runs), so completed-only macro is also 50%, with the missing A completion explicit. False
clean is 1/4 buggy attempts (25%), or 1/3 completed buggy attempts; all-attempt zero-recovery
count on buggy targets is 1. False findings total zero; the duplicate count is one. Fix sufficiency
is 3/3 overall, while sufficient-outcome recall remains 50% macro: perfect fixes for reported
bugs do not imply that all bugs were found.

All-attempt spend is $16 for three recoveries, or $16/3 = $5.33 per recovery and $16/5 = $3.20 per
completed attempt. Completed-only spend is $13 for two recoveries ($6.50 each). Discarding A/2
would hide $3 of spend and a completion failure. Per-attempt cost min/median/max is $1/$2.50/$4;
completed-only it is $1/$2/$4. There is no matched-cost comparison because this example has one
arm. A's union recall is 1/2, B's is 1/1: macro union is 75%, which cannot replace 50% per-run
macro. A2's reopening earns no recovery credit, and the repeated A1 publication earns one.

For a denominator-update illustration, suppose an unexpected finding from a hypothetical second
arm is blindly confirmed as a distinct material defect B2, missed by both shown B attempts.
Version B's register from one defect to two and rescore every arm: the shown B recalls become
0/2 and 1/2, so target B recall becomes 25% and this arm's macro becomes 37.5%. Report both
`D_B: 1 -> 2` and `macro: 50% -> 37.5%`, preserving original raw rows and before/after scores
for both arms. This is a truth-set revision, not changed reviewer performance.

## Deliver the evidence and decision

Use the ticket's dated bundle: README with preregistration/pins/deviations, sealed-then-released
adjudication register and blinded decisions, per-attempt payload/report/transcript references,
cost/timing records, comparison-data with every target and seed, and evaluation with screening
verdicts and limitations. #137 and #124 authorize collection **and synthesis**; the older
[prototype runbook](adding-a-prototype-test.md)'s collection-only scope does not apply.

Keep historical observations in the [holdout method](prototype-runs-holdout/README.md) and
[evaluation](prototype-runs-holdout/evaluation.md) intact, with their dated interpretation notes.
Future experiment results must distinguish new measurements, historical regression evidence,
policy deviations and estimates. Stop at the attempt/spend cap and report what is missing.
