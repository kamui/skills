# Bounded discovery: design and handoff

## 1. Authority and inspected revisions

This implements the design in [#146](https://github.com/kamui/skills/issues/146) for the
active [#138](https://github.com/kamui/skills/issues/138) epic. This document owns state
transitions and record schemas; the [one-shot method](../code-review-one-shot-method.md)
owns scoring; [#149](https://github.com/kamui/skills/issues/149) owns frozen experiment values.
No shipped skill, default, publisher, or general agent framework changes here.

Inspected repository revision: `face533044492ca06e11134751d9ea457ed6e429` (2026-09-07 local
date); current skill tree: `f9a195bed7fa0d9182de5eaef4a5a8cf35b0d1b4`. Read the actual
[`SKILL.md`](../../../skills/code-review-publish/SKILL.md),
[`verifier.md`](../../../skills/code-review-publish/references/verifier.md), its
[`concurrency procedure`](../../../skills/code-review-publish/references/verifier-concurrency.md),
rubric and output contract at that revision. The method inspected was also at this revision;
the companion method changes in this handoff must be included in #149's final method pin.

The experimental common policy is the [#136 snapshot](../code-review-one-shot-baseline.md):
commit `83bc170e8ae9c5f2d6a6941a94f25f6748a36ed6`, skill tree
`bea6be143582e75bada966ee85964623ef31f167`, workflow `v5b-10`. Comparing that skill directory
with the inspected revision changes only its DESIGN runtime note, not executable policy.
#149 must pin exact artifacts, not resolve a moving `main` or rely on the workflow name.
Later #185/#186 repairs stay outside this comparison even if shipped before dispatch.

Evidence and constraints read:

- [#119](https://github.com/kamui/skills/issues/119): scoped safety rulings, unresolved bases,
  post-refutation clean checks, and the two-batch cap; #70 early timing remains in A/B.
- [PR #183](https://github.com/kamui/skills/pull/183) and its
  [comparison](../one-shot-effort-2026-09-06/comparison-data.md): hygiene survivors could
  suppress zero-survivor verification. Medium primary failed the cost screen (0.94 versus
  <=0.80); the measured Claude/Sonnet default remains high primary/high baseline verifiers.
- Corrected #137 evidence at `bdd1c4a36ba9d4bb0890a66b9579203bc9f3ea19`,
  [comparison §§6,8](../one-shot-qualification-2026-09-07/comparison-data.md) and
  [metering ledger](../one-shot-qualification-2026-09-07/ledger.md): the tRPC callers were
  inspected before rejection; Requests recovery did not imply a sufficient remedy.
- Downstream interfaces: #147 implements this design; #148 prepares targets and scopes;
  #149 freezes controls; #150/#151 collect or close out; #152 adjudicates blindly;
  #153 joins operational stages to frozen truth and decides. A completed prerequisite may
  deliver a stop artifact, so issue closure alone never authorizes dispatch.

## 2. Treatment and common preparation

| Arm | Primary | Additional work |
| --- | --- | --- |
| A | Integrated #136 policy | Baseline conditional fresh verification |
| B | Same policy, prompt, model and effort | Only verifier configuration changes from A |
| C | Same policy, prompt, model and effort | One bounded finder; B's separate fresh verifiers after the discovery barrier |

B/C verifier model, effort, task prompt bytes, and execution permissions are identical.
C's finder uses that same selected worker configuration, with a discovery task instead of a
verification task. A/B have no finder. Every verifier is distinct from the primary, finder,
and any prior verifier. C has at most one finder, one initial verifier, and one follow-up.
All workers and continuations consume the arm's common whole-review ceiling.

#149 prospectively selects an actually distinct stronger worker configuration and records
model/effort identifiers plus evidence for the intended capability difference. Stronger is a
treatment hypothesis, not an established ranking. The common primary follows #124's retained
default; another runtime needs its own supported controls and observed-setting evidence.

All arms share the exact legitimate source packet, primary policy/prompt, model/effort,
execution permissions, session shape, cache-accounting method, and whole-review ceilings.
Coordinator instructions differ only to implement C's finder/barrier/admission sequence.
The primary's later evidence and conversation can differ after receiving discoveries;
C/B measures discovery plus its required timing/integration work, not a prompt-only effect.

Prepare a common source packet once from permitted PR/spec text, base-branch rules, pinned
diff and manifest using the method's cutoff/provenance checks. It contains no arm's findings,
primary safety conclusions, hidden category label, truth register, later fixes, or curator
narrative. Build permitted-history mirrors and offline disposable clones with equivalent
dependencies and safe focused execution. Each primary still inspects the complete change,
all mandatory tests and requirement rows, including outside the discovery scope.

The curator may know truth; the scope selector is a separate fresh, read-only context that
has never seen it. #148 freezes candidate inventory/order and objective exclusion criteria
before selecting targets, then runs the selector exactly once on each chosen target's common
inputs. Select a supported concurrency/progress surface first, conformance second, changed-test
surface third. Within a category order by normalized repository-relative path (case-sensitive
lexical order), then symbol and line. Record every supported alternative and the legitimate
citations for selecting one. A semantic model-assisted choice records its model, effort,
prompt, context and output hashes; a fixed prompt does not make it deterministic.

Freeze allowed root paths/symbols, the named risk/obligation, and a caller/callee/contract
frontier with a default maximum of two expansion hops. Roots are hop 0; each expansion names
the source symbol, destination range, edge kind and citation establishing that edge. A bounded
read may follow an allowed edge to establish a trigger or refutation; unrelated files are
outside scope. A path allowance means the recorded symbol/range, not arbitrary whole-file
search. Record requested evidence beyond the frontier as unavailable under the experimental
bound. Exhaustion or an empty search cannot establish safety beyond the inspected scope.

Reuse the exact scope hash across A/B/C and both replicates (A/B retain it as preparation
metadata; it adds no discovery instruction to their primary or verifier). Keep selector
misses. Never reselect to hit a known bug. If no supported surface exists, record an objective
eligibility failure under the predeclared selection rule, not an empty clean result. An eligible
clean target still gets C's one finder. Numeric finder token/time limits belong to #149.

## 3. Record schemas and access boundaries

Schema version is `bounded-discovery-v1`. The tables define required fields and invariants for
#147, not a new runtime implementation. JSON objects use UTF-8; hashes are SHA-256 of exact
stored bytes, except explicitly named Git commit/tree OIDs. IDs are nonempty strings unique
in their namespace and never recycled; references must resolve. UTC timestamps are observed
timezone-qualified events. Null means not yet produced/not applicable with a reason; use
`unknown` plus an evidence-gap reason when the trace cannot establish a fact. Preserve original
records and append revisions/events rather than silently overwriting a frozen record.

An `ArtifactRef` is `{uri, sha256, access}` with access `reviewer-common`, `primary-private`,
`finder-private`, `verifier-private`, `coordinator-only`, or `evaluator-only`. URIs must resolve
within enforced permitted roots; a hash or a directory name is not an access boundary.
An `EvidenceRef` is `{artifact, locator, observed_at, availability, reason}`; locator is a
source `path:line`/range or transcript request/tool-output coordinate. Availability is
`inspected`, `not-inspected`, `unavailable`, or `unknown`. `not-inspected` requires positive
evidence of omission (for example a complete access trace); silence in a report means unknown.

| Record | Required fields and constraints |
| --- | --- |
| `SourcePacket` | `schema_version`, `packet_id`, repository/PR, canonical `repository_url`, PR `state` and boolean `merged`, posting/review identity, `base_ref`, base/head/merge-base OIDs, `cutoff`, PR/spec/rule refs, diff/manifest/ranges refs, provenance/completeness results, permitted-history identity, dependency and execution-policy refs, content hash. Missing identity/state (including `merged`) or incomplete provenance cannot become a ready packet. |
| `SelectedScope` | `scope_id`, source hash, selector context/config/prompt refs, `selection_mode` (`mechanical` or `model-assisted`), supported alternatives and ranked paths, selected surface, legitimate rationale/citations, roots `{path,symbol,start,end}`, frontier edges, `max_hops` (default 2), exclusions/unavailable edges, frozen output hash and timestamp. No truth IDs or category labels. |
| `ExperimentConfig` | experiment/method/design/policy/prototype pins; common primary prompt/config, A worker config, B/C worker config and identical verifier task refs; C finder discovery-task ArtifactRef (exact prompt bytes/hash) and config ref equal to B/C worker config, absent for A/B; target/packet/scope refs; ordered 24 cell IDs; runtime/session/cache controls; limits for tokens/dollars/wall time/commands/finder; ledger ref and grading reserve; requested/observed setting evidence. #149 freezes positive numeric limits; null limits block benchmark dispatch. |
| `Attempt` | unique `attempt_id`, cell `(target,arm,replicate)`, predecessor/replacement ordinal, config/source/scope hashes, runtime/session ID, lifecycle state, worker/event/batch/claim refs, timing/usage refs, validity, completeness, no-batch decisions, final payload ref or absence reason. Root dispatch starts the attempt; setup has no attempt ID. |
| `Worker` | unique `context_id`, attempt or preparation ID, role (`selector`, `primary`, `finder`, `initial-verifier`, `follow-up-verifier`), requested config and observed-setting refs, packet hash, permitted read/write roots, output store, start/freeze/termination events, all request/continuation IDs and meter refs. Reusing a discovery context as verifier is invalid. |
| `Freeze` | `freeze_id`, context/attempt/role, input packet hash, complete output artifact hash, coordinator timestamp, state of manifest and first falsification pass (primary) or scope pass (finder). Partial/malformed streams cannot freeze. A frozen output is immutable; later primary work is a new phase artifact. |
| `CrossFeed` | event ID, attempt, source/destination contexts, released artifact hash, both discovery freeze IDs, finder termination event, coordinator timestamp. Only primary receives finder claims after both freezes. Other-attempt and evaluator artifacts have no release route. |
| `Claim` | stable local ID, claimed `origin` (`primary`, `finder`, `both`, `unknown`), source local IDs/freeze refs, canonical ID and model-authored dedup decision/evidence, kind, claim/trigger/impact/change, anchor/fix/raw citations, requirement refs, inspected evidence refs, admission/verification/publication records described below. Source identity survives semantic merges. |
| `VerificationBatch` | batch ID, ordinal (`initial`, `follow-up`), mode (`candidate`, `clean-verdict`, `mixed`, `related-acquittal`), fresh context ID, task/config/packet hashes, baseline trigger decisions, supplied candidate IDs and ledger-row IDs, dispatch/return events, per-ID rulings, completeness/failure reason. At most one of each ordinal. An initial `related-acquittal`-only batch is not independently triggered by that mode. |
| `NoBatchDecision` | phase (`initial` or `follow-up`), baseline clause, survivor IDs, high-risk-surface decision/evidence, candidate/related/zero-survivor trigger decisions, reason (`no-eligible-trigger`, `no-new-required-work`, `policy-permitted-omission`, `required-unavailable`, `unknown`), affected row IDs and evidence. Record explicitly even when the attempt has zero batches. |
| `AcquittalCoverage` | for every acquitted high-risk row: row ID, kind, evidence surface, stated safety premise, asserted bounded scope, inspected pointers, disposition evidence, each applicable baseline trigger and decision/evidence, batches required/received, returned rulings or gap, policy/fidelity classification. Keep ordinary acquittals too when recorded; high-risk rows are exhaustive. |

Admission is `{disposition, evidence, at_phase}` where disposition is `survives`, `rejected`,
`duplicate`, `question`, `observation`, or `unknown`. Preserve the original disposition text
alongside the normalized value, including risk checks rejected before a formal candidate.
For a raised-and-acquitted claim also require `{safety_premise, asserted_scope,
disposition_evidence}`; record `unknown` if absent. Retain private support in the originating
store, not in verifier packets. Capturing existing review/tool evidence is uniform across arms
and adds no discovery instructions, stronger falsification demand, or new verification trigger
to their common policy. A passive collector records explicit model judgments; missing narration
stays unknown rather than provoking an additional review pass.

Verification is `{required, trigger_evidence, supplied_batch_ids, rulings, disposition}`.
Disposition distinguishes `not-required-policy`, `confirmed`, `refuted`, `unresolved`,
`missing-required-dispatch`, `missing-required-ruling`, `pending`, and `unknown`. Candidate
rulings retain baseline `confirmed`/`refuted`; a refutation has basis `contradicted`, `prevented`,
`intentional`, `pre-existing`, `no-consequence`, or `unresolved`, with the settling fact for the
last. Ledger rulings use `holds`/`re-open`, with scoped evidence and any unavailable fact. Every
safety ruling preserves path/state conditions and opposite-branch evidence under #119; an
uncited safety assertion cannot narrow a finding. Zero-survivor batches also carry their
baseline batch conclusion. No new verifier verdict vocabulary is introduced.

Publication is `{disposition, payload_item_id, evidence}` with `rendered`, `withheld`,
`not-admitted`, `pending`, or `unknown`; record why (including cap, scope dispute, or missing
confirmation). Here rendered means validated would-be publication: all grid arms are render-only.
Origin, admission, verification, publication, runtime validity and review completion are distinct
fields. Agreement between discoverers is not confirmation, and a withheld claim is not recovery.

Access policy: primary and finder start with common source, their role task and permitted clone
only; finder additionally receives selected scope and its quota. Keep output stores mutually
unreadable until release. Finder receives neither primary conclusions nor another run's artifacts.
Its task is to identify bounded candidate claims with triggers, impacts and raw citations, and
report inspected ranges, frontier expansions and unavailable evidence. It returns a complete
discovery artifact even when empty. It never rules on supplied primary claims, performs a
verification task, or turns negative search into a global safety conclusion.
Verifiers receive the pinned baseline's compact candidate fields, ranges, permitted issue/rule
coordinates, raw check evidence and required compact ledger rows. They receive no private support,
full discovery output, primary conversation, truth, or origin-based endorsement. Follow-up uses a
new context with only its required records. Normal verification can inspect narrow necessary
evidence outside the finder frontier; that frontier never limits primary mandatory work.

Enforce these rules on filesystem, process/tool, history and network read surfaces, as well as
prompt assembly. #147 must test canaries in primary, other-attempt and truth stores using actual
finder tools. Record audited limitations; missing mandatory isolation or a detected leak prevents
a faithful run. Offline packets cannot share an evaluator checkout accessible by absolute path.

## 4. Scheduling and terminal review states

For A/B, use baseline conditional triggers and #70 timing unchanged: after the full diff/manifest
and mandatory falsifications, an eligible batch may run while remaining low-risk work finishes.
Concurrency/failover, data-integrity, and security/authorization changes wait for the full pass.
Both modes retain the late-related-row follow-up trigger. A stronger worker is charged and
evaluated only when actually dispatched; no-batch outcomes remain part of the sample.

C's state machine:

1. `prepared → discovering`: validate pins, access controls, attempt and atomic budget
   reservation; start separate fresh primary and finder with distinct stores.
2. `discovering → frozen`: primary finishes complete inspection and its first falsification
   pass; finder finishes its bounded independent pass. Coordinator accepts two complete immutable
   freeze records and terminates the finder. Each can finish first; neither reads the other's
   discovery stream before its own freeze. No initial verifier has started.
3. `frozen → admitting`: record the release event; primary receives only compact finder
   claims/citations, falsifies them, and semantically deduplicates the union. Model records
   primary/finder/both origins; no script infers equivalence from matching text. Empty discovery
   still completes the barrier and creates no additional verification trigger.
4. `admitting → initial-verification` or `reconciling`: apply baseline triggers to the complete
   admitted union. Send every ordinarily eligible candidate, whatever its origin/scope, and all
   required related rows to B's fresh initial task. For zero findings on a baseline high-risk
   surface send the complete compact disposition ledger to the clean-verdict task. Otherwise
   record no-batch reason and continue. The finder has no verification continuation or restart.
5. `initial-verification → reconciling`: validate corrections and scope against the diff,
   merge IDs, re-falsify reopened rows and finish any remaining work. Recompute post-refutation
   zero-survivor eligibility. Collect all newly eligible candidates and newly related rows into
   the one fresh follow-up; use the complete updated ledger when the clean trigger applies.
6. `reconciling → follow-up-verification → rendering`: use at most that single follow-up,
   including mixed candidate/ledger tasks when needed. Re-falsify its returns; never dispatch a
   third verifier. Record missing required work and withhold unconfirmed claims. Render valid
   unrelated findings using the pinned validator/emitter and record exact completion or stop.

`rendering → closed` stores the validated result and final status; `closed` is an operational
terminal state, not a claim of complete review coverage. Set review completeness separately
under the method. Any active state can instead enter `stopped` with a terminal Handoff and
retained partial artifacts. Closed/stopped attempts accept accounting closeout events only;
a replacement has a new attempt ID and starts at `prepared`.

In this table, **derive** means apply the pinned output contract: known unsettled must-fix
blocker → Changes Requested; otherwise incomplete coverage/verification → Incomplete;
otherwise an outcome-changing unanswered question → Needs Information; otherwise Approved.
Known blockers take precedence but do not hide incomplete coverage. A bounded clean ruling
validates supplied dispositions only. Operational invalidity is recorded separately from status.

| Input / event | Next task | Allowed rendered findings and status |
| --- | --- | --- |
| No findings, ordinary surface, empty finder | C completes both freezes/admission; A/B normal pass; no eligible trigger recorded | No findings; derive (Approved only if otherwise complete) |
| Primary-only survivor | Normal eligible initial verification; C waits for barrier | Confirmed mandatory or baseline-eligible optional findings; derive |
| Finder-only survivor (C) | Primary falsifies/adopts; distinct fresh initial verifier if eligible | Same eligibility as primary origin; no automatic second verification |
| Both discover the same defect | Preserve both source IDs; model merges to one canonical claim before dispatch | At most one finding for the concept/outcome; independent discovery is not verification |
| Primary mandatory candidate outside finder scope | Send it and ordinarily required related rows to normal verification | Confirmation required; finder bound cannot exclude it |
| High-risk zero-survivor, including a clean target | Initial clean-verdict task over full disposition ledger; C after barrier | No finding unless reopened, re-falsified and verified when required; derive |
| Hygiene survivors plus unrelated high-risk acquittal | Follow actual trigger decisions; without eligible candidate batch, zero-survivor is false | Baseline may render hygiene and approve; log policy-permitted omission, not failed dispatch |
| Missing/failing/malformed finder (C) | Cancel remaining work as needed, preserve partial stores, close attempt; no restart or silent B substitution | Only already validated artifacts retained; treatment incomplete, operational failure explicit; no clean inference |
| Initial verifier confirms survivor | Reconcile scoped corrections; follow-up only for newly required work | Confirmed finding may render; derive |
| Initial verifier refutes last survivor on high-risk surface | Fresh follow-up clean attack over entire updated ledger, including refuted row | Valid refutation stands; no global approval from refutation alone |
| Refutation basis unresolved | Route settling fact through baseline uncertainty/coverage rules; required follow-up if triggered | Withhold candidate; question or incomplete coverage as baseline requires, never safety from uncertainty |
| Scope dispute in cited safety ruling | Primary re-falsifies; changed mandatory claim uses remaining follow-up | Unsettled disputed finding withheld; verified unrelated findings allowed; derive with gap |
| Late candidate or newly related row | Collect with all pending work into fresh follow-up, even if only a related row remains | Every required ID needs its corresponding verdict/ruling |
| Follow-up reopens a mandatory candidate, or leaves zero survivors requiring a new clean check | Re-falsify; record required work unavailable at cap | No third batch; unconfirmed reopened claim withheld, unrelated verified findings allowed; incomplete coverage |
| Required verifier fails, times out, omits ID or cannot inspect decisive evidence | Record missing required dispatch/ruling/evidence and close under baseline gap rules | Unconfirmed finding withheld; derive with incomplete verification |
| Early runtime/budget/invalid-input stop (including before any root) | Cancel in-flight work, settle/reserve costs, write stop and unattempted manifest | Available claims retained for grading; no fabricated payload, completion, or clean conclusion |

## 5. Failure-stage capture and worked fixtures

Stage evidence is operational, not ground truth. #147 validates IDs, fields, hashes, order and
explicit dispositions. Models decide admission, semantic identity, triggers, scope, truth and
remedies. Only after #152's independent truth rulings freeze does #153 join claim/stage records
to defect IDs. Never place this section's evaluator annotations in reviewer packets.

Keep these axes separate: evidence `not-inspected` / `inspected` / `unavailable` / `unknown`;
raised-and-rejected admission; policy-permitted non-verification; failed mandatory dispatch;
verifier refutation/unresolved; and publication/cap loss. Multiple stages can apply to one row.
A missing published finding does not identify which stage lost it. A terse report cannot prove
missing inspection. A scoped unsupported safety premise is recorded as claimed until independent
adjudication establishes whether it was wrong.

### Fixture H: hygiene survivors and an unrelated acquittal

This is a paper routing fixture shaped by PR #183, not a new replay or truth claim. Run the
same explicit primary records through A/B, and through C with an independently frozen empty
finder. `H1` and `H2` are `maintainability/consider` survivors settled by local evidence.
`Q1` is an acquitted `concurrency` row with decisive pointer `src/queue.rs:40`, safety premise
"the idle worker cannot miss the wake", and bounded scope "idle transition under queue lock".
Its record points to the inspected read and original disposition evidence. Hygiene anchors/fixes
are in `tests/unused.rs` and `docs/examples.md`, with no shared function/branch/state/lock.

| Row | Admission | Baseline trigger / batch receipt | Verification / publication |
| --- | --- | --- | --- |
| H1, H2 | survives, primary | no must-fix or consequential trigger; no difficult reconstruction; no batches | `not-required-policy`; optional render |
| Q1 | rejected, primary | non-survivor; unrelated to H1/H2; no candidate batch; zero-survivor false | `not-required-policy`; `not-admitted`; coverage records `policy-permitted-omission` |

The attempt has `NoBatchDecision(initial, policy-permitted-omission)` with H1/H2 survivor IDs,
Q1 affected ID, high-risk surface true, zero-survivor false, and no related trigger. Empty C
discovery leaves this result unchanged. Do not force Q1 into verification or classify this as
runtime invalidity. Variant H-required: make H1 an independently admitted must-fix and make Q1
related by the pinned same-file rule; the initial batch now requires H1 verdict and Q1 ledger
ruling. No dispatch is `missing-required-dispatch`; a dispatched batch omitting Q1's return is
`missing-required-ruling`. These variants test mechanics, not whether the safety premise holds.

### Fixture T: paired unresolved-generic and concrete-type acquittals

Historical source is corrected #137 [comparison §8](../one-shot-qualification-2026-09-07/comparison-data.md),
with [att-12's ledger, trigger decision and tool reads](../one-shot-qualification-2026-09-07/j-trpc-5017/j-bea6be14-seed2-att-12-run.md).
All four tRPC reviews recorded `Overwrite<` caller searches plus reads of `middleware.ts` and
`procedureBuilder.ts`; all rejected the behavior/compatibility concern before verification.
Their resolved-object premise missed unresolved generic operands. This is evaluator evidence
about those historical records, not a new instruction to any experimental reviewer.

The following abbreviated records inherit schema v1, attempt-local IDs and ArtifactRefs to those
sources; synthetic records use `fixture://` locators resolved by #147's fake adapter only.

| Field | T-generic (historical-shaped) | T-concrete (synthetic supported counterpart) |
| --- | --- | --- |
| Row / origin | `T1`, primary; preserve att-12 local `internal/overwrite-compat-break` | `T2`, primary |
| Kind / claim | preserve original `requirement/compatibility` text; normalized requirement; changed Overwrite may break router inference | bug; Overwrite may fail on the specified concrete object pair |
| Inspected evidence | att-12 §5 commands 8–10; `middleware.ts:65,81,103,120,136`, `procedureBuilder.ts:38-44` | `fixture://concrete.ts:1-3`: `type A={a:string}; type B={b:number};` and an assertion for this exact pair |
| Stated safety premise | operands are already resolved object shapes due to `_ctx_out: {}` and UnsetMarker guards | this specified concrete A/B pair evaluates to the asserted merged object |
| Asserted scope | all existing callers, including inferred router shapes; preserve the recorded overbroad scope | only that concrete A/B instantiation; generic operands unassessed |
| Admission / disposition evidence | rejected before formal candidate admission; att-12 §3 compatibility row and §10 note 3 reasoning | rejected; fake supplied decisive concrete-type assertion, no extrapolation |
| Batch trigger / receipt | surviving hygiene does not qualify; rejected concern not eligible; ordinary type-inference surface; `[]` | same routing assumptions: ordinary surface, optional local hygiene survivor, `[]` |
| Verification / publication | `not-required-policy`; `not-admitted` | `not-required-policy`; `not-admitted` |
| Evaluator-only outcome | inspected premise failed for unresolved generic operands; not missing inspection or mandatory dispatch | supported for the stipulated concrete pair; no global safety claim |

The unresolved-generic fixture preserves evidence inspection, safety premise, bounded assertion,
rejection and policy-permitted omission as distinct fields. A/B and C with empty finder preserve
those inputs and routing. If a C finder supplies a new eligible generic claim in a fake variant,
record it as finder-origin, admit/deduplicate it, and route it normally; that is not proof that a
real finder would discover it. T-unavailable supplies a failed caller read: mark that pointer
`unavailable`, retain the stated gap; T-unknown lacks access evidence: mark `unknown`. Neither
can be converted mechanically to `not-inspected` or safe. A complete access log showing a named
range was never read can support the separate `not-inspected` case.

Every used #137 target remains reserved: Requests #6667, tRPC #5017, GraphQL.js #1582, Bokeh
#9232, grpc-go #7390 and ripgrep #2957, alongside #124's bytes #698, etcd #18749 and previous
holdout/prototype targets. These fixtures consume no fresh-target slots.

### Fixture R: recovery and remedy sufficiency

Keep an evaluator-only `OutcomeJoin` with `truth_version`, frozen ruling ref, attempt ID,
payload item ID, defect ID, `recovered`, `sufficient_outcome` (`sufficient`, `partial`,
`insufficient`, `unknown`, `not-applicable`), action/priority errors, false-clean flag and
evidence. #152/#153 populate it; the adapter does not infer these fields from claim text.

Requests GT-i1 is recovered by a client-certificate finding, but the remedy omits the adapter's
own `ssl_context` manifestation: `recovered=true`, `sufficient_outcome=partial`, as recorded in
corrected #137 comparison §6. Recovery and sufficient-outcome recall therefore differ. A second
synthetic outcome has a recovered material defect with a sufficient fix at `consider` and
status Approved: it is still false clean under the method. Neither fix sufficiency nor recovery
nor reviewer action changes that status-based flag on an adjudicated buggy target.

## 6. One budget, metering and stop artifacts

[ledger.json](ledger.json) opens the experiment ledger before chargeable setup or probes.
Owner is `kamui`, the epic owner; each event also names its operating ticket and actor. Current
actual/reserved experimental spend is zero. Ordinary implementation/document work is outside
measured experimental spend. This does not assert the user session itself was free. No paid
grid calls, target setup or real capability probes are authorized by this design work.

One $150 ceiling covers the entire epic, with a cumulative $15 pre-freeze subtotal inside it.
Setup/selector/probes, every review/discard/replacement, metering, charged grading and synthesis
all count. #149 freezes `min(1.5 × projected full experimental cost, $150)` after reconciling sunk
spend and reserving conservatively for grading/closeout. It can reduce the cap only while retaining
incurred charges; a projection plus reserve that cannot fit produces a stop, not a smaller
post-hoc design. Null reserve/configuration values mean the gate is not yet established.

`BudgetEvent` requires immutable `event_id`, previous event ID, observed timestamp, ticket/actor,
phase (`pre-freeze`, `review`, `grading`, `closeout`), operation (`open`, `reserve`, `settle`,
`release`, `cap-freeze`, `stop`), attempt/helper/request refs when applicable, reservation ID,
actual cost delta, reservation delta, uncertainty bound, rate/usage evidence, and reason. Amounts
are nonnegative decimal USD values except explicit reservation-release deltas. Corrections append
a linked adjustment event with its evidence; previous entries remain auditable. Snapshot totals
must reconcile to events and are never authoritative over them.

#147 implements atomic reservation before concurrent dispatch: existing actual spend + all
in-flight upper bounds + separately protected grading/closeout reserve + new allowance must fit
the total cap and applicable phase/attempt ceilings. Worker sublimits stay inside the review's
reservation, not added again or granted as extra budget. Transfer part of the protected reserve
to a grading/closeout operation atomically when that phase begins; never count it twice. Settle
actual usage and release unused reservation only when evidence is complete; delayed/missing
usage retains a conservative upper bound. Reserve one-call headroom and cancellation costs.
A runtime without hard token controls needs an enforceable conservative request allowance or
must report unsupported. No worker can spend another's reservation.

One epic has 24 planned cells (four targets × three arms × two fresh replicates), including
six pilot cells. Three replacements maximum, 27 attempts maximum, for documented infrastructure
or input invalidity only. Invalidate exactly the affected comparison cells; an affected triplet
can consume all three replacements. A valid substantive miss, false finding or skill timeout
does not earn a retry. Never erase predecessors or restart the finder to bypass this cap.
Freeze balanced/interleaved order and at most two concurrent cells in #149.

Reuse [#130's timing schema](../prototype-runs-holdout/README.md#metering-per-run) unchanged:
`completion_mode`, `root_dispatched_at`, `payload_validated_at`, `completed_at`. All cells use
`render-only`; stopped attempts retain `stopped_at` in their Attempt/stop artifact, outside the
completion sidecar, and report censored duration. Missing completion is null, not a guessed
event. Record worker start/freeze/end separately; overlapping worker spans are not root elapsed.

Meter every request/continuation of primary, finder, initial/follow-up verifier and preparation
helpers. Retain request ID, actual model and observed effort, uncached input, cache-write by
tier/TTL, cache-read, output (thinking counted once), tool charges and dated actual rates.
Reuse `tools/transcript_usage.py` and supported `tools/agent_effort.py` from the parent research
directory by pinned path; #147 introduces only mechanical adapters. Preserve durable per-request
inputs, per-helper/attempt meter outputs and controlled transcript refs, including discarded
setup. Temporary paths alone are not delivery. Unknown settings or usage stay explicit and may
block fidelity/cost conclusions. Compare matched billed cells; do not transplant old cache-tier
prices. Report review consumption separately from shared preparation and grading; shared work
is charged once to the epic, not billed repeatedly to arms or silently omitted.

Inventory runtime features from local version/help/config evidence cheaply in #147. Define
minimal toy probes for #149 covering freshness, actual stronger settings, file-read isolation,
cancellation, concurrent reservation and reproduction of billed totals from retained usage.
Every real probe counts inside the existing setup allowance. PR #183's Claude Code 2.1.263
observation (startup verifier definition worked, per-call effort or mid-session definition did
not) is evidence to re-probe, not portable support. Unsupported distinct worker settings produce
a runtime stop, not a relabeled identical configuration or silent provider/model substitution.

`Handoff` requires `{schema_version, artifact_id, stage, disposition, created_at, evidence,
ledger_ref, actual_usd, reserved_usd, uncertainty_usd, available_claims, unattempted_cells,
dispatch_authorized, next_stage}`. Disposition is exactly one of:

| Disposition | Meaning and required evidence |
| --- | --- |
| `ready` | This stage's deliverable is usable. State which stage; design-ready is not runtime-ready or permission to run a grid. #149 additionally requires usable prerequisite artifacts, committed preregistration, verified controls and budget fit. |
| `stopped-runtime` | Required context/configuration/access/cancellation/metering capability is unavailable; include observed probe/version evidence and missing control. |
| `stopped-budget` | Next reservation, phase allowance, grading reserve or attempt/replacement cap cannot fit; include gate calculation and unattempted work. |
| `stopped-invalid` | Unrecoverable packet/config/hash/isolation/protocol invalidity; include affected cells, evidence and any replacement disposition. |

A stop is immutable, names the producing ticket and reason, preserves incurred/reserved/unknown
cost and available claims, and enumerates every unattempted cell or pre-freeze symbolic slot.
Before target freeze use `slot-1..4 × A/B/C × replicate-1..2`, explicitly unassigned rather than
inventing PR identities. After freeze use exact cell IDs and keep attempted failures separately.
Cancel in-flight work and append settlements; do not overwrite the original stop. A manifest
can contain no successful payload and still support closeout. #150/#151 propagate no-dispatch
closeout, #152 grades available claims only, #153 reports operational feasibility or bounded
evidence; no successful grid output is a prerequisite for those steps.

## 7. Acceptance for the implementation handoff

#147's fake adapter must exercise every transition-table row, distinct discovery/verifier IDs,
freeze ordering and immutable hashes, compact handoff without support, whole-primary verification
outside finder scope, complete supplied-ID rulings, settings/pin mismatch, terminal no-cell
closeout, and two simultaneous reservations that cannot both fit. Include H/H-required,
T-generic/T-concrete/T-unavailable/T-unknown, and the separate R grading fields. Inspect actual
read controls with canaries, not just generated prompts. Scripts validate explicit records;
paper or fake-worker success demonstrates scheduling/identity/accounting, never recall.

This design is delivered when its schemas, transitions, fixtures, open ledger and method
exception are committed. #147 supplies executable checks; #148 supplies independent target
preparation; #149 supplies final pins, numeric limits and metered capability evidence before any
reviewer dispatch. A positive later screen recommends fresh confirmation against the then-current
integrated policy; it neither promotes a default nor authorizes further runs automatically.
