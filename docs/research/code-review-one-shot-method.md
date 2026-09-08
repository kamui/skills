# One-shot code-review evaluation method

**Defined 2026-09-05 for [#131](https://github.com/kamui/skills/issues/131).** This is the
authoritative method for the current-skill experiments. It defines a protocol and synthetic
scoring examples; experiment bundles report their own results. This method authorizes no
paid dispatch. The active #138 design/preparation work can begin independently of prior grids;
its benchmark dispatch still requires the usable inputs and frozen controls described below.
Each experiment must meet its ticket's prerequisites and freeze its own pins, targets,
configuration, and spend before starting.

## 1. Freeze the experiment

Commit the preregistration in the experiment's dated research bundle before inspecting any
candidate-arm output. Record its commit and timestamps, the method commit, hypothesis, arms,
planned cells, pilot order, replacement policy, thresholds below, and stopping caps. Subsequent
changes get a dated deviation with the original rule retained; they are never described as
preregistered. Shared prerequisites are [#136](https://github.com/kamui/skills/issues/136)
(repaired policy), [#130](https://github.com/kamui/skills/issues/130) (elapsed events),
[#96](https://github.com/kamui/skills/issues/96) (attempt accounting and reset-aware scheduling,
§3 below) and [#97](https://github.com/kamui/skills/issues/97) (cache pricing). Check their
completion before dispatch.

| Experiment | Frozen comparison and size | Prospective screening rule |
| --- | --- | --- |
| [#137](https://github.com/kamui/skills/issues/137) | Exact repaired #136 skill versus historical `3ff624a0a8b57e7096d8ad8263ac64a3fb3ccd83`; same model, effort and verifier configuration. Six fresh PRs: four buggy, two adjudicated clean; two runs per arm/PR = 24 planned cells. Two-target paired pilot first, with its valid rows included. At most two replacement cells: 26 attempts total. | Zero candidate-arm false findings, no additional false-clean outcomes, no worse completion rate, at least +10 percentage points in macro material recall, and at most 25% higher matched median billed cost. |
| [#124](https://github.com/kamui/skills/issues/124) | Same repaired skill, high/medium primaries with verifier effort fixed at high or the higher tested default. Three seeds per arm on known Hyper plus two per arm on each of two fresh reasoning-heavy PRs (including a clean high-risk case) = 14 cells. At most two replacement cells: 16 attempts total. | Zero candidate-arm false findings, no additional false-clean outcomes, no lower macro material recall or worse completion rate, and at least 20% lower matched median billed cost. Otherwise retain the default. |
| [#138](https://github.com/kamui/skills/issues/138) | Active separate experiment: A is the #136 integrated baseline; B changes only verifier configuration; C adds one bounded finder and defers initial verification until discovery admission, using B's separate fresh verifiers. Four fresh targets (three buggy, one clean), A/B/C, two replicates = 24 planned cells, including six pilot cells. **Three replacements maximum / 27 attempts across the epic.** [#146 design](bounded-discovery-prototype/DESIGN.md) owns schemas/transitions; [#149's preregistration](bounded-discovery-runs-2026-09-08/preregistration.md) (frozen 2026-09-08, disposition `ready`) fixes the pins, the stronger worker (`claude-opus-5`/`high` against `claude-sonnet-5`/`high`), the selected scopes, the equal $9.00 whole-review ceiling, the sealed cell order and the $150 cap. | Screen B and C separately against A: zero false findings; no worse false-clean count/rate or completion; >=20% relative macro material-recall gain and positive absolute gain (A=0 requires +10 percentage points), in both attempt-level and completed-only views; median matched billed cell-cost ratio <=1.25. Report sufficient-outcome recall and action errors separately. C/B measures discovery plus timing with identical verifiers. A complete positive screen recommends fresh confirmation, not promotion. |

For #138, preparation is active now; there is no residual-gap entry gate or requirement to
wait for #137. #149 required usable #147/#148 artifacts plus #136/#130/#96/#97 prerequisites, and
read each disposition before freezing; its bundle is where that grid's preregistration lives.
#124 is complete: its retained-default decision supplies the common primary configuration
(high primary/high baseline verifier in the measured Claude/Sonnet runtime); PR #183 did not
qualify medium for adoption. #137's corrected negative screen and changed truth/target mix inform
interpretation, not a mandatory benchmark gate. Read prerequisite dispositions: a terminal stop
requires no-dispatch closeout, even when the producing issue is closed. Keep #136 policy common
to A/B/C, including permitted omissions; later #185/#186 repairs require a separate comparison.

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
assumptions and a maximum spend of `min(1.5 × projected spend, $150)` per experiment, including
pilot, replacements, invalidated/discarded attempts, setup, artifact processing, charged grading
and synthesis. #124 and #137 retain their historical ticket budgets. **#138 has one shared epic
budget**, not a fresh allowance per child: [its ledger](bounded-discovery-prototype/ledger.json)
opens before chargeable setup/probes, with a $150 absolute ceiling and a $15 cumulative pre-freeze
subtotal inside it. #149 reconciles sunk charges before freezing the total cap and a conservative
grading/closeout reserve. Its cap may decrease but cannot discard sunk spend. Atomically reserve
in-flight allowances plus the protected reserve before dispatch; missing usage retains an upper
bound. Stop if the full scope and reserve cannot fit. Record equal per-pair execution and run
budgets (equal across all three #138 arms); finder sublimits are inside C's whole-review ceiling.
Before each dispatch, check remaining spend against a conservative upper bound for the next
work and observe available session/reset limits; §3's dispatch record is where both are
written down. Stop and report incomplete evidence if runtime, attempt or spend caps prevent
completion. Model substitution or buying a paid service requires a new decision. This method
itself does not spend that budget.

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
the frozen cutoff, guidance and evidence for every arm/seed; disclose preexisting hints. Build them
with [`tools/build_packet.py`](tools/build_packet.py), the packet source for this method: it renders
that content from one forge query and the staging mirror, omits every review, thread comment,
conversation comment and issue comment first published after the cutoff — the merge instant by
default — and reports what it omitted to stdout rather than into the packet. Before rendering, it
validates timezone-aware source metadata, historical body/edit provenance, and completeness on
every required GraphQL or REST history route. Unavailable pre-cutoff text or incomplete history
exits `1` without writing a packet; a future date quoted in specification prose remains permitted.
This validation does not prove the absence of answers elsewhere in the reviewer’s environment;
the isolation and evaluator-material exclusions above still apply. Caller-supplied extra sections
need their own established provenance before inclusion.

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
adjudication and auditing, without giving them recovery credit.

When a harness repair changes inputs or execution conditions, invalidate exactly the affected
comparison cells, including previously successful counterparts, and rerun under one frozen
repair. Each rerun consumes a replacement attempt. The default cap is two replacements; #138
prospectively allows **three replacements / 27 total attempts across the epic**, sufficient for
one affected A/B/C triplet. Unrelated faithful cells stand. If necessary reruns exceed the
applicable cap, stop and close out the partial experiment. A valid substantive miss, false
finding or skill timeout is not a rerun opportunity. This #138 exception leaves #124/#137 and
the historical two-replacement examples below unchanged.
A replacement never erases its predecessor. Count an invalid attempt as operationally incomplete;
separately identify harness failures and skill failures. All planned cells need valid completed
outcomes before claiming a successful full-grid screen; otherwise report provisional comparisons
and the missing evidence.

### Dispatch record and session limits

Before each root dispatch, write a dispatch record into the ticket's attempt ledger: the cell and
the new attempt ID; the expected duration and its basis (observed elapsed-to-completion of matched
prior attempts as min/median/max, or `no matched observation`); what is known about the session's
quota and reset (the latest figures the harness or provider reported, with their timestamps, or
`unknown`); the attempts and spend already used against the ticket's caps; and the cells in flight.
A conservative upper bound for the attempt must fit inside the remaining spend cap and the
remaining attempt cap, or the dispatch does not happen.

Dispatch at most two cells concurrently until the ticket's own evidence supports more. This is a
conservative starting heuristic, not a measured cost optimum: concurrency changes how many attempts
one limit event stops, not what an attempt bills. Test 4 is the historical evidence. One
session-limit event stopped all four first attempts in flight. The two Skeptic-line attempts had
produced nothing usable; their four discarded transcripts billed $3.60 of that session's $16.82.
The two Panel-line attempts had finished their Find phase, and that $5.58 of orchestrator and
finder spend was reused, so it sits inside the $13.22 the four completed runs billed rather than
in the discard figure
([test-4 billed usage](prototype-runs-2026-09-01-test-4/comparison-data.md#billed-usage-added-2026-09-89)).
Cite these as what one limit event cost once, not as a forecast of savings; nothing here says that
halving concurrency halves spend.

A known insufficient quota or window delays dispatch until the reported reset. A reset time alone
says when a limit lifts, not how much quota is available now or afterwards; never infer quota from
it, and record `unknown` where nothing was reported. When any request returns a session-limit
notice: record the notice text, its arrival time and the reset it reports in the ledger; stop new
dispatch; start nothing else until the reported reset has passed. Wait only within what the runtime
supports (its longest single wait, no busy polling) and within what the user has said about their
availability, and tell the user that dispatch is paused and until when. If the reset lies beyond
those limits, stop and report the grid's state; a later session resumes from the ledger, and the
ledger says the grid spanned sessions.

### Attempt ledger

Every attempt, however it ends, gets one ledger row: attempt ID; cell (target, arm, replicate);
session identity and root transcript; the phase reached (`root dispatch` when nothing past the
dispatch ran, `primary`, `verifier`, `validation`, `publication`/`result`); disposition and reason
(`valid completed`, `stopped: session-limit notice`, `harness-invalid`, `skill failure`); whether
it is the cell's first attempt, a replacement `k of limit` inside the frozen cap (normally 2;
#138 uses 3), or a replacement the cap refuses (then nothing is dispatched and the row marks
the cell incomplete); and its meter row from
the existing metering CLI,
`python3 docs/research/tools/transcript_usage.py <paths> --prices IN,OUT --row "<attempt ID>"`,
run over every transcript the attempt produced, aborted verifiers included. The CLI skips the
harness's synthetic notice lines, so a transcript with billed turns followed by a notice prices its
billed turns. A transcript whose only assistant line is the notice makes the CLI exit `2` with
`no billed assistant turns`; write that row by hand with zero turns and `$0.00`, the CLI's stderr
line as evidence and the reason `notice, no billable request`. It is still an attempt: the root was
dispatched, it stands in the completion denominator as a harness failure, and its retry is a
replacement inside the cap like any other, which is what makes dispatching into an exhausted window
expensive.

Keep three cost views apart and label each. **Per-arm valid-run cost** sums the arm's valid
completed attempts. **All-attempt cost**, per cell and per arm, adds every discarded, stopped or
invalid attempt mapped to the cell; §4's matched cost uses this view, and the chosen arm's cost is
never quoted with its discards subtracted. **Experiment total** (ticket total for #124/#137;
shared epic total for #138) adds setup, selector/probes, tool/repro charges, notice-only rows,
artifact processing and charged grading/closeout; the spend cap governs it, and discarded spend
is never dropped from it. Report review-attempt consumption separately from preparation and
grading. Shared setup is charged once to the experiment, not repeated in every arm's cell cost.
The valid-run view alone, or the older practice of assigning discards to "the session, not to any run",
does not replace the other two.

Persist each completed expensive phase (the primary's ledger and payload draft, a finished verifier
batch) to the attempt's files before the next phase starts, so a stopped attempt leaves evidence.
Evidence is all it leaves. A run resumed in a fresh context from a persisted phase is a new attempt
row marked `continuity: resumed from <attempt>`, never an uninterrupted replicate; it is a valid
completed cell only where the preregistration allowed resumed continuity in advance, and otherwise
it is diagnostic and the cell needs a clean replacement inside the cap. Test 4's Panel runs, whose
Verify phase ran in fresh orchestrators over persisted finder reports, are the disclosed historical
case ([run continuity](prototype-runs-2026-09-01-test-4/comparison-data.md#run-continuity)).

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
| False findings | Raw item count and unique false-claim count per attempt; sum adjudicated raw false counts over all attempts per arm for screening, including harness-invalid attempts. Also report the invalid-attempt subtotal separately; invalidation cannot erase a false finding from the screen. Optional false-item fraction = raw false items / all raw finding items, N/A for zero items; this is not material recall. |
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
the experiment total. Record cache tier/TTL, currency and discounts actually applicable. Unknown
cache tiers or missing usage get explicit uncertainty/bounds, never a silently assumed cheap tier
or zero charge. Use #97's supported accounting when available; no estimate establishes a billed
cost threshold when the uncertainty could change the decision.

Use #130's [timing sidecar and recording steps](prototype-runs-holdout/README.md#metering-per-run).
Create it immediately before root dispatch and update it on final validation and completion.
Capture timezone-qualified ISO-8601 **root dispatch**, **final validated payload**, and **final
publication/result** events as they occur, with completion mode (`publication`, `result` for
production without publication, or `render-only`). Elapsed-to-payload is payload minus root;
elapsed-to-completion is publication/result minus root. Missing events stay unavailable; invalid
ordering is an input error. In render-only mode the final result is completion, with publication
absent. For failed attempts retain stop events and observed duration as censored attempt time,
not fabricated completion. Keep the historical sum of worker transcript spans as **agent span
sum**, since parent waits overlap children. Root first/last assistant timestamps can be a labeled
proxy only. Do not infer exact elapsed events from retrospective narrative. Meter with
`python3 docs/research/tools/transcript_usage.py <paths> --prices IN,OUT --timing <timing.json> --json`;
the `timing` object carries elapsed seconds separately from `total.agent_span_sum_seconds`.
Keep failed-attempt stop events in the attempt record, outside the completion sidecar schema.

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
clean is 1/4 buggy attempts (25%), or 1/3 completed buggy attempts. Total zero-recovery count on
buggy targets is 1 (B/1); zero-recovery attempts on buggy targets that did not claim clean number
0, since B/1 returned Approved. False findings total zero; the duplicate count is one. Fix sufficiency
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

## Worked attempt ledger

**Invented rows only; no reviewer was dispatched.** A hypothetical ticket has 24 planned cells, a
two-replacement cap (26 attempts), a $120 spend cap and hypothetical billed dollars. Before this
excerpt six attempts were valid, $19.40 was spent and nothing was in flight. Times are one evening
in one session (PDT), quota was never reported (`unknown` throughout), and every dispatch record's
expected duration was 25 minutes, the median of three matched prior attempts (20–32). Rows
abbreviate §3's fields; `in flight a→b` is the count before and after the dispatch.

| Attempt | Cell | Dispatch record | Phase reached | Disposition | Replacement | Meter row |
| --- | --- | --- | --- | --- | --- | --- |
| att-07 | B/1 | 22:14; attempt 7/26; $19.40 spent; in flight 0→1 | result | valid completed 22:41, sidecar complete | first | 2 transcripts, $3.10 |
| att-08 | D/2 | 22:16; 8/26; $19.40; in flight 1→2 | verifier | stopped 22:52: session-limit notice in the verifier, `resets 23:00`; primary ledger persisted 22:38; no validated payload; stop event kept in the attempt record | first | primary $2.20 + verifier's 9 billed turns $0.35 = $2.55 |
| att-09 | E/1 | 22:50; 9/26; $22.50; in flight 1→2 | root dispatch | notice, no billable request: only assistant line is the notice; CLI exit 2 `no billed assistant turns` | first | by hand: 0 turns, $0.00 |
| — | — | 22:52: notice recorded; no new dispatch until 23:00; user told | — | — | — | — |
| att-10 | D/2 | 23:05; 10/26; $25.05; reset passed, quota `unknown`; in flight 0→1 | result | valid completed 23:31 | replacement 1 of 2, predecessor att-08 | 2 transcripts, $3.25 |
| att-11 | E/1 | 23:07; 11/26; $25.05; in flight 1→2 | result | valid completed 23:33 | replacement 2 of 2, predecessor att-09 | 2 transcripts, $2.90 |
| att-12 | F/1 | 23:40; 12/26; $31.20; in flight 0→1 | primary | stopped 23:58: second notice, `resets 04:00`; nothing persisted yet | first | 1 transcript, $1.40 |
| — | F/1 | 23:58: replacement would be 3 of 2 | — | refused: over cap; F/1 ends incomplete with att-12 as its only attempt | over cap, not dispatched | — |
| — | — | 23:58: reset is beyond the runtime's longest wait and the user's stated availability; session closed, grid state reported | — | — | — | — |

The replacement cap binds before the attempt count does: 24 planned first attempts are reserved,
so a third replacement is refused at attempt 13 of 26. Fourteen planned cells remain with fourteen
attempts, and the next session, resuming from the ledger, knows that any further failure ends its
cell incomplete. The grid can no longer claim a successful full-grid screen; it reports provisional
comparisons with F/1 missing.

Cost views for the excerpt. Valid-run cost is $3.10 + $3.25 + $2.90 = $9.25 over three valid
attempts. All-attempt cost adds $2.55 + $0.00 + $1.40 and is $13.20 over six dispatched attempts;
the two limit events cost $3.95, reported as such and subtracted nowhere. Cell D/2's matched cost
is $5.80, its two attempts, not the $3.25 of the attempt that completed. Spend after att-12 is
$19.40 + $13.20 = $32.60 of $120. Completion in the excerpt is 3/6 attempts and 3/4 cells, with
three session-limit failures (two billed, one notice-only), all harness failures. att-08's
persisted primary ledger and att-12's transcript go to adjudication with zero recovery credit;
both attempts are incomplete, not false clean. Had att-10 instead resumed att-08's persisted
primary in a fresh verifier context, its row would read `continuity: resumed from att-08` and,
absent a preregistered allowance, D/2 would still need a clean replacement.

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
