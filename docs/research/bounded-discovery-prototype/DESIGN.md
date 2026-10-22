# Bounded discovery: design and handoff

## 1. Authority and inspected revisions

This document implements the design in [#146](https://github.com/kamui/skills/issues/146) for the
active [#138](https://github.com/kamui/skills/issues/138) epic. This document owns state
transitions and record schemas. The [one-shot method](../code-review-one-shot-method.md) owns
scoring, and [#149](https://github.com/kamui/skills/issues/149) owns frozen experiment values.
This work changes no shipped skill, default, publisher, or general agent framework.

The inspected repository revision is `face533044492ca06e11134751d9ea457ed6e429`, with a local
date of 2026-09-07. The current skill tree is `f9a195bed7fa0d9182de5eaef4a5a8cf35b0d1b4`. The
design work read the actual `SKILL.md`, `verifier.md`, its `concurrency procedure`, the rubric,
and the output contract at that revision. This document omits the historical source paths of the
first three. The inspected method was also at this
revision. #149's final method pin must include the companion method changes in this handoff.

The experimental common policy is the [#136 snapshot](../code-review-one-shot-baseline.md). It
consists of commit `83bc170e8ae9c5f2d6a6941a94f25f6748a36ed6`, skill tree
`bea6be143582e75bada966ee85964623ef31f167`, and workflow `v5b-10`. A comparison of that skill
directory with the inspected revision shows a change only in its DESIGN runtime note, not in
executable policy. #149 must pin exact artifacts. It must not resolve a moving `main` or rely on
the workflow name. The later #185 and #186 repairs stay outside this comparison, even if they
ship before dispatch.

The design work read the following evidence and constraints.

- [#119](https://github.com/kamui/skills/issues/119) covers scoped safety rulings, unresolved
  bases, post-refutation clean checks, and the two-batch cap. The #70 early timing remains in
  arms A and B.
- [PR #183](https://github.com/kamui/skills/pull/183) and its
  [comparison](../one-shot-effort-2026-09-06/comparison-data.md) showed that hygiene survivors
  could suppress zero-survivor verification. A medium primary failed the cost screen with 0.94,
  where the screen required at most 0.80. The measured Claude/Sonnet default remains a high
  primary with high baseline verifiers.
- The corrected #137 evidence at `bdd1c4a36ba9d4bb0890a66b9579203bc9f3ea19` includes
  [comparison sections 6 and 8](../one-shot-qualification-2026-09-07/comparison-data.md) and the
  [metering ledger](../one-shot-qualification-2026-09-07/ledger.md). It shows that the reviews
  inspected the tRPC callers before the rejection. It also shows that the Requests recovery did
  not imply a sufficient remedy.
- The downstream interfaces are as follows. #147 implements this design. #148 prepares targets
  and scopes. #149 freezes controls. #150 and #151 collect or close out. #152 adjudicates blindly.
  #153 joins operational stages to frozen truth and makes the decision. A completed prerequisite
  may deliver a stop artifact, so closing an issue never authorizes dispatch by itself.

## 2. Treatment and common preparation

| Arm | Primary | Additional work |
| --- | --- | --- |
| A | Integrated #136 policy | Baseline conditional fresh verification |
| B | Same policy, prompt, model and effort | Only the verifier configuration differs from A |
| C | Same policy, prompt, model and effort | One bounded finder, then B's separate fresh verifiers after the discovery barrier |

Arms B and C use an identical verifier model, effort, task prompt bytes, and execution
permissions. C's finder uses that same selected worker configuration, with a discovery task
instead of a verification task. Arms A and B have no finder. Every verifier is distinct from the
primary, the finder, and any prior verifier. Arm C has at most one finder, one initial verifier,
and one follow-up. All workers and continuations count against the arm's common whole-review
ceiling.

#149 selects, in advance, a stronger worker configuration that is actually distinct. It records
the model and effort identifiers and the evidence for the intended capability difference. The
word stronger names a treatment hypothesis, not an established ranking. The common primary
follows #124's retained default. Another runtime needs its own supported controls and
observed-setting evidence.

All arms share the exact legitimate source packet, the primary policy and prompt, the model and
effort, the execution permissions, the session shape, the cache-accounting method, and the
whole-review ceilings. The coordinator instructions differ only where they implement C's
sequence of finder, barrier, and admission. After the primary receives discoveries, its later
evidence and conversation can differ. The comparison of C with B measures discovery plus its
required timing and integration work, not an effect of the prompt alone.

Prepare one common source packet from the permitted PR and spec text, the base-branch rules, and
the pinned diff and manifest. Use the method's cutoff and provenance checks. The packet contains
no arm's findings, primary safety conclusions, hidden category label, truth register, later
fixes, or curator narrative. Build permitted-history mirrors and offline disposable clones with
equivalent dependencies and safe focused execution. Each primary still inspects the complete
change and all mandatory tests and requirement rows, including those outside the discovery
scope.

The curator may know truth. The scope selector is a separate, fresh, read-only context that has
never seen it. #148 freezes the candidate inventory, its order, and the objective exclusion
criteria before it selects targets. It then runs the selector exactly once on the common inputs
of each chosen target. Select a supported concurrency or progress surface first, a conformance
surface second, and a changed-test surface third. Within a category, order candidates by
normalized repository-relative path in case-sensitive lexical order, then by symbol, then by
line. Record every supported alternative and the legitimate citations for selecting one. A
semantic model-assisted choice records its model, effort, prompt, context, and output hashes. A
fixed prompt does not make that choice deterministic.

Freeze the allowed root paths and symbols, the named risk or obligation, and a frontier of
caller, callee, and contract edges. The frontier has a default maximum of two expansion hops.
Roots are hop 0. Each expansion names the source symbol, the destination range, the edge kind,
and the citation that establishes that edge. A bounded read may follow an allowed edge to
establish a trigger or a refutation. Unrelated files are outside scope. A path allowance covers
the recorded symbol or range, not an arbitrary search of the whole file. Record requested
evidence beyond the frontier as unavailable under the experimental bound. Exhaustion or an empty
search cannot establish safety beyond the inspected scope.

Reuse the exact scope hash across arms A, B, and C and both replicates. Arms A and B retain it as
preparation metadata. It adds no discovery instruction to their primary or verifier. Keep
selector misses. Never reselect to hit a known bug. If no supported surface exists, record an
objective eligibility failure under the predeclared selection rule, not an empty clean result.
An eligible clean target still gets C's one finder. #149 owns the numeric token and time limits
for the finder.

## 3. Record schemas and access boundaries

The schema version is `bounded-discovery-v1`. The tables define required fields and invariants
for #147, not a new runtime implementation. JSON objects use UTF-8. Hashes are SHA-256 digests of
the exact stored bytes, except for Git commit and tree OIDs that are named explicitly. IDs are
nonempty strings. Each ID is unique in its namespace and is never recycled. References must
resolve. UTC timestamps are timezone-qualified and record observed events. Null means that a
value is not yet produced or is not applicable, and the null carries a reason. When the trace
cannot establish a fact, use `unknown` with an evidence-gap reason. Preserve the original records
and append revisions or events. Never silently overwrite a frozen record.

An `ArtifactRef` is `{uri, sha256, access}`. The access value is `reviewer-common`,
`primary-private`, `finder-private`, `verifier-private`, `coordinator-only`, or
`evaluator-only`. URIs must resolve within enforced permitted roots. A hash or a directory name
is not an access boundary. An `EvidenceRef` is `{artifact, locator, observed_at, availability,
reason}`. The locator is a source `path:line` or range, or a coordinate in a transcript request
or tool output. Availability is `inspected`, `not-inspected`, `unavailable`, or `unknown`. The
value `not-inspected` requires positive evidence of omission, for example a complete access
trace. Silence in a report means unknown.

| Record | Required fields and constraints |
| --- | --- |
| `SourcePacket` | `schema_version`, `packet_id`, repository/PR, canonical `repository_url`, PR `state` and boolean `merged`, posting/review identity, `base_ref`, base/head/merge-base OIDs, `cutoff`, PR/spec/rule refs, diff/manifest/ranges refs, provenance/completeness results, permitted-history identity, dependency and execution-policy refs, content hash. A packet with missing identity or state, including `merged`, or with incomplete provenance cannot become ready. |
| `SelectedScope` | `scope_id`, source hash, selector context/config/prompt refs, `selection_mode` (`mechanical` or `model-assisted`), supported alternatives and ranked paths, selected surface, legitimate rationale/citations, roots `{path,symbol,start,end}`, frontier edges, `max_hops` (default 2), exclusions/unavailable edges, frozen output hash and timestamp. It contains no truth IDs or category labels. |
| `ExperimentConfig` | experiment/method/design/policy/prototype pins; common primary prompt/config, A worker config, B/C worker config and identical verifier task refs; C finder discovery-task ArtifactRef (exact prompt bytes/hash) and config ref equal to B/C worker config, absent for A/B; target/packet/scope refs; ordered 24 cell IDs; runtime/session/cache controls; limits for tokens/dollars/wall time/commands/finder; ledger ref and grading reserve; requested/observed setting evidence. #149 freezes positive numeric limits. Null limits block benchmark dispatch. |
| `Attempt` | unique `attempt_id`, cell `(target,arm,replicate)`, predecessor/replacement ordinal, config/source/scope hashes, runtime/session ID, lifecycle state, worker/event/batch/claim refs, timing/usage refs, validity, completeness, no-batch decisions, final payload ref or absence reason. Root dispatch starts the attempt. Setup has no attempt ID. |
| `Worker` | unique `context_id`, attempt or preparation ID, role (`selector`, `primary`, `finder`, `initial-verifier`, `follow-up-verifier`), requested config and observed-setting refs, packet hash, permitted read/write roots, output store, start/freeze/termination events, all request/continuation IDs and meter refs. Reusing a discovery context as a verifier is invalid. |
| `Freeze` | `freeze_id`, context/attempt/role, input packet hash, complete output artifact hash, coordinator timestamp, state of the manifest and first falsification pass for the primary or of the scope pass for the finder. Partial or malformed streams cannot freeze. A frozen output is immutable. Later primary work is a new phase artifact. |
| `CrossFeed` | event ID, attempt, source/destination contexts, released artifact hash, both discovery freeze IDs, finder termination event, coordinator timestamp. Only the primary receives finder claims, after both freezes. Other-attempt and evaluator artifacts have no release route. |
| `Claim` | stable local ID, claimed `origin` (`primary`, `finder`, `both`, `unknown`), source local IDs/freeze refs, canonical ID and model-authored dedup decision/evidence, kind, claim/trigger/impact/change, anchor/fix/raw citations, requirement refs, inspected evidence refs, admission/verification/publication records described below. Source identity survives semantic merges. |
| `VerificationBatch` | batch ID, ordinal (`initial`, `follow-up`), mode (`candidate`, `clean-verdict`, `mixed`, `related-acquittal`), fresh context ID, task/config/packet hashes, baseline trigger decisions, supplied candidate IDs and ledger-row IDs, dispatch/return events, per-ID rulings, completeness/failure reason. An attempt has at most one batch of each ordinal. That mode does not independently trigger an initial batch that has only the `related-acquittal` mode. |
| `NoBatchDecision` | phase (`initial` or `follow-up`), baseline clause, survivor IDs, high-risk-surface decision/evidence, candidate/related/zero-survivor trigger decisions, reason (`no-eligible-trigger`, `no-new-required-work`, `policy-permitted-omission`, `required-unavailable`, `unknown`), affected row IDs and evidence. Record it explicitly, even when the attempt has zero batches. |
| `AcquittalCoverage` | for every acquitted high-risk row: row ID, kind, evidence surface, stated safety premise, asserted bounded scope, inspected pointers, disposition evidence, each applicable baseline trigger and decision/evidence, batches required/received, returned rulings or gap, policy/fidelity classification. Keep ordinary acquittals too when they are recorded. The high-risk rows must be exhaustive. |

Admission is `{disposition, evidence, at_phase}`. The disposition is `survives`, `rejected`,
`duplicate`, `question`, `observation`, or `unknown`. Preserve the original disposition text next
to the normalized value. This includes risk checks that were rejected before they became a formal
candidate. For a raised-and-acquitted claim, also require `{safety_premise, asserted_scope,
disposition_evidence}`, and record `unknown` if it is absent. Retain private support in the
originating store, not in verifier packets. All arms capture existing review and tool evidence in
the same way. This capture adds no discovery instructions, no stronger falsification demand, and
no new verification trigger to their common policy. A passive collector records explicit model
judgments. When narration is missing, the value stays unknown, and the collector does not prompt
an additional review pass.

Verification is `{required, trigger_evidence, supplied_batch_ids, rulings, disposition}`. The
disposition distinguishes `not-required-policy`, `confirmed`, `refuted`, `unresolved`,
`missing-required-dispatch`, `missing-required-ruling`, `pending`, and `unknown`. Candidate
rulings keep the baseline values `confirmed` and `refuted`. A refutation has a basis of
`contradicted`, `prevented`, `intentional`, `pre-existing`, `no-consequence`, or `unresolved`.
The last basis also records the settling fact. Ledger rulings use `holds` or `re-open`, with
scoped evidence and any unavailable fact. Under #119, every safety ruling preserves path and state
conditions and the evidence from the opposite branch. An uncited safety assertion cannot narrow a
finding. Zero-survivor batches also carry their baseline batch conclusion. This design introduces
no new verdict vocabulary for verifiers.

Publication is `{disposition, payload_item_id, evidence}`. Its disposition is `rendered`,
`withheld`, `not-admitted`, `pending`, or `unknown`. Record the reason, including the cap, a scope
dispute, or a missing confirmation. Here, rendered means a validated would-be publication, because
all grid arms are render-only. Origin, admission, verification, publication, runtime validity, and
review completion are distinct fields. Agreement between discoverers is not confirmation, and a
withheld claim is not recovery.

The access policy is as follows. The primary and the finder start with only the common source,
their role task, and the permitted clone. The finder also receives the selected scope and its
quota. Keep their output stores unreadable to each other until release. The finder receives
neither primary conclusions nor another run's artifacts. Its task is to identify bounded
candidate claims with triggers, impacts, and raw citations. It also reports inspected ranges,
frontier expansions, and unavailable evidence. It returns a complete discovery artifact even when
the artifact is empty. It never rules on supplied primary claims, never performs a verification
task, and never turns a negative search into a global safety conclusion. Verifiers receive the
pinned baseline's compact candidate fields, ranges, permitted issue and rule coordinates, raw
check evidence, and required compact ledger rows. They receive no private support, full discovery
output, primary conversation, truth, or origin-based endorsement. A follow-up uses a new context
with only its required records. Normal verification can inspect narrow, necessary evidence outside
the finder frontier. That frontier never limits the primary's mandatory work.

Enforce these rules on the read surfaces for the filesystem, processes and tools, history, and the
network, and also in prompt assembly. #147 must use the actual finder tools to test canaries in
the primary, other-attempt, and truth stores. Record audited limitations. Missing mandatory
isolation or a detected leak prevents a faithful run. Offline packets cannot share an evaluator
checkout that is accessible by absolute path.

## 4. Scheduling and terminal review states

For arms A and B, use the baseline conditional triggers and the #70 timing unchanged. After the
full diff and manifest and the mandatory falsifications, an eligible batch may run while the
remaining low-risk work finishes. Changes to concurrency or failover, data integrity, and security
or authorization wait for the full pass. Both modes retain the late-related-row follow-up trigger.
The experiment charges and evaluates a stronger worker only when the coordinator actually
dispatches it. No-batch outcomes remain part of the sample.

Arm C uses the following state machine.

1. `prepared → discovering`: Validate the pins, the access controls, the attempt, and the atomic
   budget reservation. Start a separate fresh primary and a separate fresh finder with distinct
   stores.
2. `discovering → frozen`: The primary finishes its complete inspection and its first
   falsification pass. The finder finishes its bounded independent pass. The coordinator accepts
   two complete, immutable freeze records and terminates the finder. Either one can finish first.
   Neither reads the other's discovery stream before its own freeze. No initial verifier has
   started.
3. `frozen → admitting`: Record the release event. The primary receives only the compact finder
   claims and citations, falsifies them, and deduplicates the union by meaning. The model records
   whether each origin is primary, finder, or both. No script infers equivalence from matching
   text. An empty discovery still completes the barrier and creates no additional verification
   trigger.
4. `admitting → initial-verification` or `reconciling`: Apply the baseline triggers to the
   complete admitted union. Send every ordinarily eligible candidate, whatever its origin or
   scope, and all required related rows to B's fresh initial task. If the review has zero findings
   and touches a baseline high-risk surface, send the complete compact disposition ledger to the
   clean-verdict task. Otherwise, record the no-batch reason and continue. The finder gets no
   verification continuation and no restart.
5. `initial-verification → reconciling`: Validate the corrections and the scope against the diff,
   merge IDs, re-falsify reopened rows, and finish any remaining work. Recompute post-refutation
   zero-survivor eligibility. Collect all newly eligible candidates and newly related rows into
   the one fresh follow-up. When the clean trigger applies, use the complete updated ledger.
6. `reconciling → follow-up-verification → rendering`: Use at most that single follow-up. It can
   include mixed candidate and ledger tasks when needed. Re-falsify its returns. Never dispatch a
   third verifier. Record missing required work and withhold unconfirmed claims. Render valid
   unrelated findings with the pinned validator and emitter, and record the exact completion or
   stop.

The `rendering → closed` transition stores the validated result and the final status. The
`closed` state is an operational terminal state, not a claim of complete review coverage. Set
review completeness separately under the method. Any active state can instead enter `stopped`
with a terminal Handoff and retained partial artifacts. Closed and stopped attempts accept only
accounting closeout events. A replacement has a new attempt ID and starts at `prepared`.

In this table, **derive** means applying the pinned output contract. A known, unsettled must-fix
blocker yields Changes Requested. Otherwise, incomplete coverage or verification yields
Incomplete. Otherwise, an unanswered question that would change the outcome yields Needs
Information. Otherwise, the status is Approved. Known blockers take precedence, but they do not
hide incomplete coverage. A bounded clean ruling validates only the supplied dispositions. Record
operational invalidity separately from status.

| Input / event | Next task | Allowed rendered findings and status |
| --- | --- | --- |
| No findings, ordinary surface, empty finder | C completes both freezes and admission; A and B run the normal pass; no eligible trigger is recorded | No findings; derive, with Approved only if the review is otherwise complete |
| Primary-only survivor | Normal eligible initial verification; C waits for the barrier | Confirmed mandatory or baseline-eligible optional findings; derive |
| Finder-only survivor in C | Primary tries to falsify it and adopts it only if it survives; a distinct fresh initial verifier runs if it is eligible | Same eligibility as a primary-origin claim; no automatic second verification |
| Both discover the same defect | Preserve both source IDs; the model merges them into one canonical claim before dispatch | At most one finding for the concept or outcome; independent discovery is not verification |
| Primary mandatory candidate outside finder scope | Send it and the ordinarily required related rows to normal verification | Confirmation required; the finder bound cannot exclude it |
| High-risk zero-survivor, including a clean target | Initial clean-verdict task over the full disposition ledger; C runs it after the barrier | No finding unless it is reopened, re-falsified, and verified when required; derive |
| Hygiene survivors plus unrelated high-risk acquittal | Follow the actual trigger decisions; without an eligible candidate batch, zero-survivor is false | Baseline may render hygiene and approve; log a policy-permitted omission, not a failed dispatch |
| Missing, failing, or malformed finder in C | Cancel remaining work as needed, preserve partial stores, and close the attempt; no restart or silent substitution of B | Only already validated artifacts are retained; the treatment is incomplete and the operational failure is explicit; no clean inference |
| Initial verifier confirms survivor | Reconcile scoped corrections; a follow-up runs only for newly required work | Confirmed finding may render; derive |
| Initial verifier refutes last survivor on high-risk surface | Fresh follow-up clean attack over the entire updated ledger, including the refuted row | Valid refutation stands; no global approval from refutation alone |
| Refutation basis unresolved | Route the settling fact through the baseline uncertainty and coverage rules; required follow-up if triggered | Withhold the candidate; question or incomplete coverage as the baseline requires, never safety from uncertainty |
| Scope dispute in cited safety ruling | Primary re-falsifies; a changed mandatory claim uses the remaining follow-up | Unsettled disputed finding withheld; verified unrelated findings allowed; derive with gap |
| Late candidate or newly related row | Collect it with all pending work into a fresh follow-up, even if only a related row remains | Every required ID needs its corresponding verdict or ruling |
| Follow-up reopens a mandatory candidate, or leaves zero survivors requiring a new clean check | Re-falsify; record the required work as unavailable at the cap | No third batch; unconfirmed reopened claim withheld, unrelated verified findings allowed; incomplete coverage |
| Required verifier fails, times out, omits ID or cannot inspect decisive evidence | Record the missing required dispatch, ruling, or evidence and close under the baseline gap rules | Unconfirmed finding withheld; derive with incomplete verification |
| Early runtime, budget, or invalid-input stop, including before any root | Cancel in-flight work, settle or reserve costs, and write the stop and the unattempted manifest | Available claims retained for grading; no fabricated payload, completion, or clean conclusion |

## 5. Failure-stage capture and worked fixtures

Stage evidence is operational, not ground truth. #147 validates IDs, fields, hashes, order, and
explicit dispositions. Models decide admission, semantic identity, triggers, scope, truth, and
remedies. #153 joins claim and stage records to defect IDs only after #152's independent truth
rulings freeze. Never place this section's evaluator annotations in reviewer packets.

Keep the following axes separate. The first is the evidence state, which is `not-inspected`,
`inspected`, `unavailable`, or `unknown`. The others are raised-and-rejected admission,
policy-permitted non-verification, failed mandatory dispatch, a verifier refutation or unresolved
ruling, and loss at publication or at the cap. Multiple stages can apply to one row. A missing
published finding does not identify which stage lost it. A terse report cannot prove missing
inspection. Record a scoped, unsupported safety premise as claimed until independent adjudication
establishes whether it was wrong.

### Fixture H: hygiene survivors and an unrelated acquittal

This is a paper routing fixture based on PR #183. It is not a new replay or a truth claim. Run
the same explicit primary records through arms A and B, and through arm C with an independently
frozen empty finder. `H1` and `H2` are `maintainability/consider` survivors that local evidence
settled. `Q1` is an acquitted `concurrency` row. Its decisive pointer is `src/queue.rs:40`. Its
safety premise is "the idle worker cannot miss the wake", and its bounded scope is "idle
transition under queue lock". Its record points to the inspected read and the original
disposition evidence. The hygiene anchors and fixes are in `tests/unused.rs` and
`docs/examples.md`, and they share no function, branch, state, or lock with Q1.

| Row | Admission | Baseline trigger / batch receipt | Verification / publication |
| --- | --- | --- | --- |
| H1, H2 | survives, primary | no must-fix or consequential trigger; no difficult reconstruction; no batches | `not-required-policy`; optional render |
| Q1 | rejected, primary | non-survivor; unrelated to H1 and H2; no candidate batch; zero-survivor false | `not-required-policy`; `not-admitted`; coverage records `policy-permitted-omission` |

The attempt has `NoBatchDecision(initial, policy-permitted-omission)`. It lists H1 and H2 as the
survivor IDs and Q1 as the affected ID. It sets high-risk surface to true and zero-survivor to
false, and it has no related trigger. An empty discovery in C leaves this result unchanged. Do
not force Q1 into verification, and do not classify this as runtime invalidity. In variant
H-required, make H1 an independently admitted must-fix, and make Q1 related through the pinned
same-file rule. The initial batch then requires a verdict for H1 and a ledger ruling for Q1. If
no batch is dispatched, the result is `missing-required-dispatch`. If a dispatched batch omits the
return for Q1, the result is `missing-required-ruling`. These variants test mechanics, not whether
the safety premise holds.

### Fixture T: paired unresolved-generic and concrete-type acquittals

The historical source is the corrected #137 [comparison section 8](../one-shot-qualification-2026-09-07/comparison-data.md),
together with [att-12's ledger, trigger decision and tool reads](../one-shot-qualification-2026-09-07/j-trpc-5017/j-bea6be14-seed2-att-12-run.md).
All four tRPC reviews recorded `Overwrite<` caller searches and reads of `middleware.ts` and
`procedureBuilder.ts`. All four rejected the behavior or compatibility concern before
verification. Their premise assumed resolved objects and missed unresolved generic operands. This
is evaluator evidence about those historical records, not a new instruction to any experimental
reviewer.

The following abbreviated records inherit schema v1, attempt-local IDs, and ArtifactRefs to those
sources. Synthetic records use `fixture://` locators, and only #147's fake adapter resolves them.

| Field | T-generic (historical-shaped) | T-concrete (synthetic supported counterpart) |
| --- | --- | --- |
| Row / origin | `T1`, primary; preserve att-12 local `internal/overwrite-compat-break` | `T2`, primary |
| Kind / claim | preserve original `requirement/compatibility` text; normalized requirement; changed Overwrite may break router inference | bug; Overwrite may fail on the specified concrete object pair |
| Inspected evidence | att-12 section 5, commands 8 to 10; `middleware.ts:65,81,103,120,136`, `procedureBuilder.ts:38-44` | `fixture://concrete.ts:1-3`: `type A={a:string}; type B={b:number};` and an assertion for this exact pair |
| Stated safety premise | operands are already resolved object shapes because of `_ctx_out: {}` and UnsetMarker guards | this specified concrete A/B pair evaluates to the asserted merged object |
| Asserted scope | all existing callers, including inferred router shapes; preserve the recorded overbroad scope | only that concrete A/B instantiation; generic operands unassessed |
| Admission / disposition evidence | rejected before formal candidate admission; att-12 section 3 compatibility row and section 10 note 3 reasoning | rejected; the fake supplied a decisive concrete-type assertion, with no extrapolation |
| Batch trigger / receipt | surviving hygiene does not qualify; rejected concern not eligible; ordinary type-inference surface; `[]` | same routing assumptions: ordinary surface, optional local hygiene survivor, `[]` |
| Verification / publication | `not-required-policy`; `not-admitted` | `not-required-policy`; `not-admitted` |
| Evaluator-only outcome | inspected premise failed for unresolved generic operands; not missing inspection or mandatory dispatch | supported for the stipulated concrete pair; no global safety claim |

The unresolved-generic fixture keeps evidence inspection, safety premise, bounded assertion,
rejection, and policy-permitted omission as distinct fields. Arms A and B, and arm C with an empty
finder, preserve those inputs and that routing. A fake variant may have a C finder supply a new
eligible generic claim. In that case, record the claim as finder-origin, admit and deduplicate
it, and route it normally. That result does not prove that a real finder would discover it.
T-unavailable supplies a failed caller read. Mark that pointer `unavailable` and retain the
stated gap. T-unknown lacks access evidence, so mark it `unknown`. Neither variant can be
converted mechanically to `not-inspected` or to safe. A complete access log that shows a named
range was never read can support the separate `not-inspected` case.

Every #137 target that was used remains reserved. These targets are Requests #6667, tRPC #5017,
GraphQL.js #1582, Bokeh #9232, grpc-go #7390, and ripgrep #2957. #124's bytes #698, etcd #18749,
and the previous holdout and prototype targets also remain reserved. These fixtures use no
fresh-target slots.

### Fixture R: recovery and remedy sufficiency

Keep an evaluator-only `OutcomeJoin` record. It holds `truth_version`, the frozen ruling ref, the
attempt ID, the payload item ID, the defect ID, and `recovered`. It also holds a
`sufficient_outcome` of `sufficient`, `partial`, `insufficient`, `unknown`, or `not-applicable`,
along with action and priority errors, a false-clean flag, and evidence. #152 and #153 populate
it. The adapter does not infer these fields from claim text.

A client-certificate finding recovers Requests GT-i1, but its remedy omits the adapter's own
`ssl_context` manifestation. The corrected #137 comparison section 6 records this as
`recovered=true` and `sufficient_outcome=partial`. Recovery and sufficient-outcome recall
therefore differ. A second, synthetic outcome recovers a material defect with a sufficient fix at
`consider`, and its status is Approved. Under the method, that outcome is still false clean.
Neither fix sufficiency nor recovery nor reviewer action changes that status-based flag on an
adjudicated buggy target.

## 6. One budget, metering and stop artifacts

[ledger.json](ledger.json) opens the experiment ledger before any chargeable setup or probes. The
owner is `kamui`, the epic owner. Each event also names its operating ticket and actor. The current
actual and reserved experimental spend is zero. Ordinary implementation and document work is
outside the measured experimental spend. This does not claim that the user session itself was
free. This design work authorizes no paid grid calls, no target setup, and no real capability
probes.

One $150 ceiling covers the entire epic, with a cumulative $15 pre-freeze subtotal inside it.
Setup, the selector, probes, every review, discard, and replacement, metering, charged grading,
and synthesis all count. #149 freezes `min(1.5 × projected full experimental cost, $150)` after it
reconciles sunk spend and reserves conservatively for grading and closeout. It can reduce the cap
only while it retains incurred charges. If a projection plus reserve cannot fit, the result is a
stop, not a smaller post-hoc design. Null reserve or configuration values mean that the gate is
not yet established.

A `BudgetEvent` requires an immutable `event_id`, the previous event ID, an observed timestamp,
the ticket and actor, a phase, and an operation. The phase is `pre-freeze`, `review`, `grading`,
or `closeout`. The operation is `open`, `reserve`, `settle`, `release`, `cap-freeze`, or `stop`.
The event also requires attempt, helper, and request refs when applicable, a reservation ID, the
actual cost delta, the reservation delta, an uncertainty bound, rate and usage evidence, and a
reason. Amounts are nonnegative decimal USD values, except explicit reservation-release deltas.
A correction appends a linked adjustment event with its evidence. Previous entries remain
auditable. Snapshot totals must reconcile to the events and are never authoritative over them.

#147 implements atomic reservation before concurrent dispatch. The existing actual spend, plus all
in-flight upper bounds, plus the separately protected grading and closeout reserve, plus the new
allowance must fit the total cap and the applicable phase and attempt ceilings. Worker sublimits
stay inside the review's reservation. They are not added again or granted as extra budget. When
the grading or closeout phase begins, transfer part of the protected reserve to that operation
atomically. Never count that part twice. Settle actual usage and release the unused reservation
only when the evidence is complete. When usage is delayed or missing, keep a conservative upper
bound. Reserve headroom for one call and for cancellation costs. A runtime without hard token
controls needs an enforceable, conservative request allowance, or it must report itself as
unsupported. No worker can spend another worker's reservation.

One epic has 24 planned cells, which is four targets times three arms times two fresh replicates.
These include six pilot cells. The epic allows at most three replacements and at most 27 attempts,
and only for documented infrastructure or input invalidity. Invalidate exactly the affected
comparison cells. An affected triplet can use all three replacements. A valid substantive miss, a
false finding, or a skill timeout does not earn a retry. Never erase predecessors or restart the
finder to get around this cap. In #149, freeze a balanced, interleaved order and at most two
concurrent cells.

Reuse [#130's timing schema](../prototype-runs-holdout/README.md#metering-per-run) unchanged. Its
fields are `completion_mode`, `root_dispatched_at`, `payload_validated_at`, and `completed_at`. All
cells use `render-only`. Stopped attempts keep `stopped_at` in their Attempt or stop artifact,
outside the completion sidecar, and report a censored duration. Missing completion is null, not a
guessed event. Record the start, freeze, and end of each worker separately. Overlapping worker
spans do not count as root elapsed time.

Meter every request and continuation of the primary, the finder, the initial and follow-up
verifiers, and the preparation helpers. Retain the request ID, the actual model and observed
effort, uncached input, cache writes by tier and TTL, cache reads, output with thinking counted
once, tool charges, and the dated actual rates. Reuse `tools/transcript_usage.py` and the
supported `tools/agent_effort.py` from the parent research directory by pinned path. #147
introduces only mechanical adapters. Preserve durable inputs for each request, meter outputs for
each helper and attempt, and controlled transcript refs, including those for discarded setup.
Temporary paths alone do not count as delivery. Unknown settings or usage stay explicit and may
block conclusions about fidelity or cost. Compare matched billed cells, and do not carry over old
cache-tier prices. Report review consumption separately from shared preparation and grading.
Charge shared work once to the epic. Do not bill it repeatedly to arms or silently omit it.

In #147, inventory runtime features cheaply from local version, help, and config evidence. Define
minimal toy probes for #149 that cover freshness, actual stronger settings, file-read isolation,
cancellation, concurrent reservation, and reproduction of billed totals from retained usage. Every
real probe counts inside the existing setup allowance. PR #183 observed in Claude Code 2.1.263
that a startup verifier definition worked, while neither per-call effort nor a mid-session
definition worked. That observation is evidence to re-probe, not portable support. Unsupported
distinct worker settings produce a runtime stop. They never produce a relabeled identical
configuration or a silent substitution of provider or model.

A `Handoff` requires `{schema_version, artifact_id, stage, disposition, created_at, evidence,
ledger_ref, actual_usd, reserved_usd, uncertainty_usd, available_claims, unattempted_cells,
dispatch_authorized, next_stage}`. Its disposition is exactly one of the following values.

| Disposition | Meaning and required evidence |
| --- | --- |
| `ready` | This stage's deliverable is usable. State which stage it is. Design-ready does not mean runtime-ready and does not give permission to run a grid. #149 also requires usable prerequisite artifacts, a committed preregistration, verified controls, and a budget fit. |
| `stopped-runtime` | A required context, configuration, access, cancellation, or metering capability is unavailable. Include the observed probe or version evidence and the missing control. |
| `stopped-budget` | The next reservation, phase allowance, grading reserve, or attempt or replacement cap cannot fit. Include the gate calculation and the unattempted work. |
| `stopped-invalid` | An unrecoverable packet, config, hash, isolation, or protocol invalidity exists. Include the affected cells, the evidence, and any replacement disposition. |

A stop is immutable. It names the producing ticket and the reason. It preserves the incurred,
reserved, and unknown cost and the available claims. It lists every unattempted cell or
pre-freeze symbolic slot. Before the target freeze, use `slot-1..4 × A/B/C × replicate-1..2`, and
mark these slots explicitly unassigned rather than inventing PR identities. After the freeze, use
exact cell IDs and keep attempted failures separate. Cancel in-flight work and append
settlements. Do not overwrite the original stop. A manifest can contain no successful payload and
still support closeout. #150 and #151 propagate a no-dispatch closeout. #152 grades only the
available claims. #153 reports operational feasibility or bounded evidence. None of those steps
requires a successful grid output.

## 7. Acceptance for the implementation handoff

#147's fake adapter must exercise every row of the transition table. It must also exercise
distinct discovery and verifier IDs, freeze ordering and immutable hashes, a compact handoff
without support, whole-primary verification outside the finder scope, complete rulings for
supplied IDs, a settings or pin mismatch, a terminal no-cell closeout, and two simultaneous
reservations that cannot both fit. Include fixtures H and H-required, the T-generic, T-concrete,
T-unavailable, and T-unknown fixtures, and the separate R grading fields. Inspect actual read
controls with canaries, not just generated prompts. Scripts validate explicit records. Success on
paper or with fake workers demonstrates scheduling, identity, and accounting, never recall.

This design counts as delivered when its schemas, transitions, fixtures, open ledger, and method
exception are committed. #147 supplies executable checks. #148 supplies independent target
preparation. #149 supplies final pins, numeric limits, and metered capability evidence before any
reviewer dispatch. A positive later screen recommends fresh confirmation against the then-current
integrated policy. It neither promotes a default nor authorizes further runs automatically.
