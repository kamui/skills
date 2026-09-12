# Proposed specification: a future bounded-discovery study

**Status: `proposed`, awaiting qualification.** This specification is **not frozen, not qualified and
not authorized to dispatch**, and merging it makes it none of those. It selects no target, runs no
probe, charges nothing, opens no seal and appends nothing to any ledger. Every numeric ceiling in it
is a proposal to be recomputed, every runtime control in it is a claim to be re-established, and every
row marked `unknown` or `budget-dependent` stays that way until a freeze supplies evidence.

Written for [#207](https://github.com/kamui/skills/issues/207), the freeze gate of a possible future
bounded-discovery study, which is **blocked by [#199](https://github.com/kamui/skills/issues/199)**.
#199 stays open; it closes when #207's probes meet its ten requirements on the runtime and the targets
a study actually dispatches with.

**A study may never be ticketed at all.** [#153](https://github.com/kamui/skills/issues/153) decided
the [#138](https://github.com/kamui/skills/issues/138) epic `inconclusive` for both candidate arms and
**recommended no confirmation study**. This document exists so that the question of what such a study
would have to look like is answered before anyone is tempted to answer it under time pressure, not
because the entry condition has been met.

## 0. How to read this document

| Marking | Meaning |
| --- | --- |
| `tooling-delivered` | A prospective control exists in the repository and synthetic tests exercise it. It establishes the mechanical behaviour it tests and **nothing** about a runtime, a target or a blind. |
| `specified-only` | This document states the requirement. No synthetic test in this repository covers it and no runtime evidence exists. |
| `unknown` | The value or the answer depends on a fact about the future runtime that has not been probed. Named, not guessed. |
| `budget-dependent` | The choice cannot be made until requalified rates exist. Named, not guessed. |

[`readiness.json`](readiness.json) carries the same rows in machine-readable form and
[`scripts/check_spec.py`](scripts/check_spec.py) refuses a row that claims more than this vocabulary
allows — in particular, it refuses any status that asserts a requirement is established, frozen,
qualified or authorized. [`probes.md`](probes.md) is the probe catalogue this document's requirements
point at. **No probe in it has been run.**

## 1. Authority and inputs read

This specification carries forward, and does not replace:

- the [design](../bounded-discovery-prototype/DESIGN.md) — record schemas, state transitions, access
  boundaries and the arm definitions;
- the [#149 preregistration](../bounded-discovery-runs-2026-09-08/preregistration.md) — the frozen
  experiment values of the closed grid, which are the starting point for a new freeze and not a
  frozen input to it;
- the [#149 dispatch template](../bounded-discovery-runs-2026-09-08/dispatch-template.md) — the launch
  shapes and prompts, which a future freeze must re-render (section 12, D2);
- [#148's target criteria](../bounded-discovery-prototype/targets/criteria.md) — E1–E11, the roles and
  the per-target preparation checklist, applied unchanged to new candidates;
- the [one-shot method](../code-review-one-shot-method.md) — scoring and accounting definitions;
- the [#151 closeout](../bounded-discovery-closeout-2026-09-10/README.md) and its
  [fidelity assessment](../bounded-discovery-closeout-2026-09-10/fidelity-assessment.json) — what the
  pilot could and could not establish;
- the [#153 decision](../bounded-discovery-decision-2026-09-11/README.md) and its
  [evaluation](../bounded-discovery-decision-2026-09-11/evaluation.md) — the verdict, the interpretation
  limits, and the revealed truth;
- the [#199 readiness tooling](../bounded-discovery-readiness-2026-09-12/README.md) — the prospective
  controls this document binds requirements to.

Where this document and one of those disagree about an **experiment value**, none of them governs yet:
this one is a proposal and the #149 values belong to a closed grid. Where they disagree about a
**schema** or a **scoring definition**, the design and the method govern, as they always have.

## 2. Hypothesis, preserved

> **Does bounding an independent discovery worker and deferring initial verification until its claims
> are admitted recover more material defects than spending the same verification budget on a stronger
> verifier alone, without adding false findings and without exceeding a 1.25 matched cost ratio?**

Carried verbatim from preregistration section 2. **The contrast is preserved.** #153 did not refute
this hypothesis and did not support it: eighteen of twenty-four cells never ran, two of the three
buggy targets were never attempted, and no attempt is a valid completed outcome. The one row where
both candidate arms recovered what the control approved is, in the decision's own words, "a hypothesis
for a future freeze, not evidence for one".

Two screens, separately: **B against A** and **C against A**. **C against B** is reported as the
discovery-and-timing contrast with identical verifiers and is not a gate. Section 12 lists every
proposed change to the closed design and justifies it; nothing outside that list is changed.

## 3. Arms and arm invariants

| Arm | Primary | Verification | Finder |
| --- | --- | --- | --- |
| A | the pinned policy under test | the policy's own conditional fresh verification, workers at the **control** configuration | none |
| B | identical to A | identical policy and triggers, workers at the **candidate** configuration | none |
| C | identical to A | identical to B, deferred until the discovery barrier | one bounded finder at the candidate configuration |

### 3.1 Invariant across A, B and C

Every one of these is an invariant a freeze must be able to demonstrate, not an intention:

1. **The source packet is byte-identical.** One common packet per target, built once, containing no
   arm's findings, no truth register, no category label, no later fix and no curator narrative.
2. **The primary is identical** in policy, prompt bytes, model, effort, execution permissions, session
   shape, cache-accounting method and whole-review ceiling.
3. **B's and C's verifier definitions are byte-identical**, and both name the same model and effort;
   C's finder names that same model and effort with a discovery task instead of a verification task.
4. **Tools differ only where the treatment requires it.** The finder gets `Read`, `Grep` and `Glob` —
   no shell, no sub-agent, no write tool — because a bounded read-only discovery pass over a selected
   scope *is* the treatment and because it must never verify. Every verifier keeps the shell so it can
   check evidence outside the finder's frontier, in every arm alike.
5. **Every verifier is a distinct fresh context** from the primary, the finder and any prior verifier.
   C has at most one finder, one initial verifier and one follow-up. Reusing a discovery context as a
   verifier is invalid by the design's `Worker` record.
6. **One whole-review ceiling per attempt**, identical across arms. C's finder sublimit is charged
   **inside** it, never in addition.
7. **The scope hash is reused across A, B and C** and both replicates. A and B retain it as preparation
   metadata only: it adds no discovery instruction to their primary or verifier.
8. **One payload contract.** Every arm writes the same single JSON file with the same key set in every
   outcome. This is new (section 12, D2) and it is an invariant because its absence was the pilot's
   structural tell.
9. **Coordinator instructions differ only where C's finder, barrier and admission sequence require it.**

### 3.2 What legitimately differs, and is not a confound to be denied

C's primary conversation necessarily diverges after it receives the finder's claims. That is the
treatment. C/B measures discovery plus its required timing and integration work, not a prompt-only
effect. C's primary also runs as two invocations of one session, because the barrier requires the
primary to freeze before it sees any claim; that extra process boundary is part of C's treatment
(preregistration deviation 4, carried forward).

### 3.3 The coordinator is not an arm, and its model is not an experimental variable

Three model-bearing roles exist and this specification keeps them separate. Confusing them is how a
study accidentally reports its own orchestration as a treatment.

| Role | Who | Model choice | Charged | Verified per assistant line |
| --- | --- | --- | --- | --- |
| **Experimental workers** | each cell's primary, finder and verifiers | **frozen by the freeze**, per arm and role | yes, as review consumption | **yes** — a mismatch or an unobservable setting invalidates the attempt |
| **Preparation helpers** | #148's adjudicator and scope selector | frozen by the target-preparation freeze, recorded with the prompt, context and output hashes | yes, under `pre-freeze` | yes, for the selector |
| **Coordinator and its helpers** | the orchestrating session and script that prepare, dispatch and settle cells; the curator; any fresh-context reviewer of the study's own bundles | an **operational** choice, recorded in the freeze record and nowhere else | no — ordinary ticket work outside measured experimental spend, by the design's section 6 convention, disclosed rather than asserted free | no |

Rules that follow, and that a freeze must state:

- **A coordinator model is never inherited by a cell.** Every worker's model and effort come from the
  frozen dispatch, supplied at session start, and are re-observed from the transcript afterwards.
- **The repository's own subagent-model default** (`AGENTS.md`: default a top-tier parent's subagents
  to the next lower tier) governs coordinator helpers only. An experimental worker's model is whatever
  the freeze pinned, at whatever tier that is, and a general default must never silently retier it.
- **Changing the coordinator's model is not a deviation** from the experiment and does not invalidate
  an attempt; changing a worker's model is a fidelity failure that does.
- The coordinator's model is nonetheless **recorded**, because its judgments — admission routing,
  loss-stage classification, dedup decisions the design assigns to a model — are part of the
  measurement's provenance.

## 4. Model and effort candidates

**Candidates, not qualified settings.** These are the pilot's pair, preserved so the contrast is the
one #138 intended. Every one of them must be re-established on the runtime a study actually dispatches
with (section 7, P01) before a freeze may name it.

| Role | Proposed candidate | Provenance | Status |
| --- | --- | --- | --- |
| Primary, every arm | `claude-sonnet-5`, effort `high` | #124's retained default, in the measured Claude/Sonnet runtime | `unknown` until re-observed |
| Verifiers, arm A (control) | `claude-sonnet-5`, effort `high` | the pinned policy's own conditional verification | `unknown` until re-observed |
| Verifiers, arms B and C (candidate) | `claude-opus-5`, effort `high` | the treatment | `unknown` until re-observed |
| Finder, arm C | `claude-opus-5`, effort `high`, read-only tools | the treatment | `unknown` until re-observed |

- **"Stronger" is the treatment hypothesis, not an established ranking.** No measurement in this
  repository compares these two models as review verifiers on a common target set. If B does not beat
  A, the honest reading is that this configuration change did not help on these targets.
- **Effort is `high` everywhere.** PR #183 measured effort inside one model and did not qualify medium
  for adoption (cost ratio 0.94 against ≤ 0.80), so the treatment moves the model tier instead.
- **No silent substitution.** If the runtime at freeze time does not offer one of the two
  configurations, or cannot be observed to have applied it, the study **stops**; it does not
  substitute a neighbouring model and relabel the arm. A substitution is a different experiment and
  needs its own freeze and its own justification in this document's section 12.
- **Distinctness must be re-established, not assumed.** The freeze re-runs the equivalent of #149's
  probes 1 and 5: request both configurations, observe them on every root and child assistant line,
  and repeat the observation inside the exact cell configuration. A per-call field or a definition
  created mid-session does not establish a child setting; a definition supplied at startup did, on the
  pilot's runtime, and whether it still does is `unknown`.
- **Model identifiers and the effort vocabulary may have changed.** The freeze records the runtime's
  own identifiers verbatim; this document's strings are the pilot's and are not a claim about any
  current catalog.

## 5. Evidence boundaries

### 5.1 Access classes and who may know truth

Unchanged from the design's section 3. An `ArtifactRef` carries `access` of `reviewer-common`,
`primary-private`, `finder-private`, `verifier-private`, `coordinator-only` or `evaluator-only`, and
**a hash or a directory name is not an access boundary** — the boundary is enforced on the filesystem,
the process and tool surface, the history surface, the network surface and prompt assembly.

- The **curator** may know truth. The **scope selector** is a separate fresh read-only context that has
  never seen it. One agent that has read the answer cannot become blind by omitting it from its next
  prompt.
- The **finder** receives the common packet, the selected scope and its quota, and never the primary's
  conclusions, another attempt's artifacts or any truth. It returns a complete discovery artifact even
  when empty, never rules on supplied primary claims and never turns a negative search into a global
  safety conclusion.
- **Verifiers** receive the pinned baseline's compact candidate fields, ranges, permitted coordinates,
  raw check evidence and required compact ledger rows — no private support, no full discovery output,
  no primary conversation, no truth and no origin-based endorsement.
- Output stores stay **mutually unreadable until release**, and only the primary receives finder claims,
  only after both freezes.

### 5.2 Reviewer isolation, and what changed under the evaluator's feet

The control that actually holds is **absence**: the material is not on the machine while a cell runs.
The pilot's isolation probes established that tightening to a restriction flag with a shell allow list
does not close the interpreter path — an allow-listed `python3` read a canary outside every permitted
root and opened a raw socket — so confinement was never the control and must not be treated as one.

**This repository now contains revealed truth in cleartext.** #153 committed the four #138 registers,
their leak sets, the schedule, the packets, the redaction map and the candidate inventory under
[`revealed/`](../bounded-discovery-decision-2026-09-11/revealed/). The candidate inventory alone names
**28 pull requests** with each one's category and eligibility result, and — for those examined that far
— the curator's hypothesis and the upstream record confirming it. Consequences a freeze must carry:

1. **Every checkout and every worktree of this repository is forbidden material** for a cell — more
   strongly than in #149, where the hazard was the preregistration and `targets/README.md`. The pilot
   host carried 188 worktrees plus the primary checkout; absence of all of them is the requirement,
   and a host that cannot reach that state uses the container regime below and says so.
2. **The exclusion set for target selection grows** (section 6, gap 8).
3. **Masking stays label masking, not guaranteed blinding**, and every surviving cue is listed before
   the freeze rather than discovered at grading. A mask token is always a sequential token, never a
   digest: a hash is only opaque when its input has real entropy, and a digest over an enumerable
   secret *is* the secret.

**Isolation regime (`unknown`, probe P16).** The pilot could not reach host absence and ran each cell
in a container mounting only its permitted roots, with the absence check run inside that container
against the host paths and the mount set asserted from the runtime's own inspection. Section 12 (D4)
proposes freezing that regime prospectively instead of carrying it as a deviation. Cells under a
different regime are not comparable to the pilot's — which is fine, because a future study is a fresh
grid and compares only within itself.

**The key.** #149 made moving the truth key off the machine mandatory rather than optional. That stays
mandatory. Committed ciphertext may remain; without the key it is inert.

### 5.3 Interpretation limits carried in

- The pinned policy's **permitted omissions** are part of the treatment in every arm. A and B may
  legitimately dispatch no verifier under the pinned rules; those outcomes and their costs are counted,
  never forced into a batch and never excluded as substantive misses.
- **Verification runs in the foreground in every arm, by choice.** The pilot's probe 10 established
  that the runtime supported background sub-agents, so the constraint is the experiment's. Read the
  arms' elapsed distributions as the harness's timing, not the policy's production timing.
- A **selector miss is part of the measured strategy** and never grounds for reselection.
- The control's false clean on the pilot's buggy target is a known gap in the pinned policy, already
  carried in #129's limits. It is not a regression this design measures.

## 6. Requirements carried from #199, with their controls and tests

Every row is a requirement on a future freeze. "Control" is the prospective code that implements the
mechanical part; "Tests" are the synthetic tests that exercise it; "Still required" is what only a
runtime, a real target or a real dispatch can supply. [`readiness.json`](readiness.json) is the
machine-readable form and [`probes.md`](probes.md) holds the probe definitions.

### gap-1 — Exact launch and configuration retention · `tooling-delivered`

The requested `--model`, `--effort`, `--max-budget-usd`, restriction flag and allow-list values are
retained **before process creation**, per phase and per worker, in an exclusively created, flushed and
fsynced record, together with the runtime and image identity and the frozen worker definitions. A
record survives a launch that never starts. Retention failure prevents that launch. The recorded argv
proves the **requested** settings; transcripts and result envelopes establish what actually ran.

- Control: [`run_cell.py`](../bounded-discovery-pilot-2026-09-09/scripts/run_cell.py) `retain_launch`,
  called from the phase and finder launch paths.
- Tests: `test_review_fixes.py::test_failed_launch_keeps_exact_argv_before_subprocess`,
  `::test_finder_launch_retains_requested_controls`.
- Still required (P17): retain a real launch in each arm, compare all arms against the frozen
  allowances, and probe a failed launch on the actual runtime. Five pilot attempts are permanently
  `unresolved` for want of exactly this.

### gap-2 — Per-role accounting and filtered-transcript provenance · `tooling-delivered`

Settlement supplies a **role for every transcript**, records `usage_per_role` reconciling to the total,
and refuses an unknown session identity rather than defaulting it. Filtered copies — the ones a
provider error forces — carry explicit labels from their original inputs plus a `sources.json` mapping
with source and copy digests, in per-copy directories so equal basenames cannot overwrite each other.
Missing usage retains conservative bounds; it is never zero and never all-primary.

- Control: `run_cell.py` `meter_roles`, `role_of` and `without_synthetic`, over the pinned
  [`meter_split.py`](../bounded-discovery-runs-2026-09-08/scripts/meter_split.py).
- Tests: `test_review_fixes.py::test_settlement_retains_roles_including_filtered_provider_error`,
  `::test_unknown_metering_role_is_refused`.
- Still required (P18): exercise primary, finder and verifier costs on real transcripts, including a
  provider error that forces filtered copies, and reconcile per-role totals to the settled charge.
- **Open question (`unknown`):** the current coordinator groups every verifier session as `worker`. A
  study that reports verification cost by ordinal — initial against follow-up — needs finer attribution
  than that, and the freeze must either add it or state that the analysis does not distinguish them.

### gap-3 — Contemporaneous lifecycle enforcement · `tooling-delivered`

Attempt-open and attempt-close events are written **when they happen**, through the coordinator's
claim-before-reservation path, so the ledger's own refusals — a reused attempt id, the attempt cap, a
replacement whose predecessor was not closed as documented invalidity — gate an actual dispatch. In the
pilot all sixteen lifecycle events were written inside one 27 ms window half an hour after the last
settlement: the money was contemporaneous and the lifecycle was a reconstruction, so none of those
refusals ever gated anything.

- Control: [`budget.py`](../bounded-discovery-readiness-2026-09-12/scripts/budget.py) `attempt_event`
  and `transact`; `run_cell.py`'s claim-before-reservation dispatch path.
- Tests: `test_adapter.py::test_phase_attempt_caps_corruption_and_attempt_identity`,
  `::test_attempt_replacement_and_concurrency_caps`,
  `::test_atomic_budget_reservations_and_settlements` (all re-run against the prospective
  implementation by `test_budget.py`); `test_review_fixes.py::test_refused_reservation_closes_budget_without_worker_usage`.
- Still required (P19): probe duplicate ids, concurrency, the attempt and replacement caps and an
  ineligible replacement on the real ledger, and **assert that no worker process starts after a
  refusal**. Check that open precedes launch and that close follows actual terminal accounting.
  Historical `claim-history` is reconstruction and supplies no evidence of prospective enforcement.

### gap-4 — Frozen sandbox and scratch allowances · `tooling-delivered`

A detected read outside the permitted roots **fails settlement**, and a settlement-time acceptance
cannot grant an allowance the freeze did not. Directory boundaries and lexical `..` traversal are both
checked. The pilot accepted one such read as "tidiness"; the frozen rule had no such exception and the
closeout had to invalidate the attempt.

- Control: `run_cell.py` `audit_reads` — no acceptance path.
- Tests: `test_review_fixes.py::test_sandbox_acceptance_and_prefix_or_traversal_cannot_pass`.
- Still required (P20): freeze **every** permitted root, including the scratch and image allowance
  (section 12, D3), identically across arms before probing; then probe an actual outside read and a
  tidiness acceptance, and require both to fail. A detector false positive is fixed in the detector and
  re-probed **before** the freeze, never excused at settlement.
- **Limit, stated:** the audit is a transcript path detector, not an interpreter and not a proof
  against symlinks or arbitrary shell programs. Actual isolation is section 5.2's regime; this is the
  rule's mechanical enforcement, not its guarantee.

### gap-5 — Completed shutdown probes over the recorded real roots · `tooling-delivered`

The cell root is recorded **outside the seal while it still exists**, its digest is pinned in the
dispatch record, and the stop gate sweeps precisely those roots. Eleven checks, all required, no
corroborating class and no exception: a check clears only when its probe **completed** *and* its
condition held. The pilot's gate passed a sweep that exited 1 on directories it could not enter and
swept a root the cells never used; the real root was only readable from the evidence the gate itself
released.

- Controls: [`roots.py`](../bounded-discovery-readiness-2026-09-12/scripts/roots.py),
  [`shutdown.py`](../bounded-discovery-readiness-2026-09-12/scripts/shutdown.py), and `run_cell.py`
  `dispatch_roots`.
- Tests: `test_roots.py::test_record_is_exclusive_and_absence_uses_actual_root`,
  `::test_record_must_survive_root_removal`, `::test_incomplete_probe_establishes_nothing`;
  `test_shutdown.py::test_a_complete_gate_clears_and_authorizes_the_seal`,
  `::test_a_record_that_is_not_the_pinned_one_blocks`, `::test_a_record_inside_the_seal_establishes_nothing`,
  `::test_a_surviving_root_blocks_even_as_a_dangling_symlink`, `::test_an_unreadable_parent_is_an_incomplete_probe`,
  `::test_a_missing_timed_out_or_failed_process_probe_establishes_nothing`,
  `::test_an_unreachable_runtime_is_not_a_clearance`, `::test_a_replayed_capture_keeps_its_own_age`,
  `::test_a_held_ledger_lock_is_a_failed_read_not_a_quiet_ledger`,
  `::test_authorization_refuses_a_ledger_that_moved_after_clearance`,
  `::test_authorize_refuses_a_stale_incomplete_or_forged_gate`;
  `test_review_fixes.py::test_dispatch_requires_the_actual_unsealed_root`.
- Still required (P21): create the record before dispatch, bind it to the config, pin its digest
  outside the seal, run `shutdown.py check` after the workers stop, and call `shutdown.py authorize
  --ledger` immediately before the seal is opened — probing the host again rather than re-scoring an
  old capture. Permission denial, timeout, a missing executable, an unreachable container runtime, a
  wrong or unrecorded root and a stale replayed capture each establish nothing and block clearance.
  Retain every root's parent until the check completes.

### gap-6 — Uniform payload production and validation across arms · `tooling-delivered`

Every arm writes **one** payload file with **one** key set in every outcome: a `summary.body`, an
`items` array that always exists, and a `stop` member that is null or names why the attempt ended.
Findings carry items and a body; a clean result carries the empty array and a body; a stopped or
unavailable attempt carries the empty array and an empty body, and an item is never invented for one.
Unknown keys are refused at every level. In the pilot only one arm emitted structured items, so a
populated array named its arm and the "anonymous" packets carried a structural tell.

- Controls: [`payload.py`](../bounded-discovery-readiness-2026-09-12/scripts/payload.py) (`validate`,
  `emit`, `accept`, `uniformity`); `run_cell.py` `payload_contract` binding at dispatch and acceptance
  at settlement.
- Tests: `test_payload.py::test_every_outcome_validates_under_one_key_set`,
  `::test_arm_specific_structure_is_refused`, `::test_a_second_payload_form_is_refused_and_its_content_is_left_alone`,
  `::test_the_pinned_contract_validator_gates_a_review_and_skips_a_stop`,
  `::test_three_arms_under_one_contract_pass_with_full_outcome_coverage`,
  `::test_a_missing_arm_or_outcome_blocks_masking`, `::test_the_pilot_tell_is_refused`,
  `::test_a_field_only_one_arm_carries_blocks_until_it_is_ruled_on`;
  `test_review_fixes.py::test_dispatch_requires_a_pinned_payload_contract`,
  `::test_dispatch_requires_the_prepared_contract_to_match_the_pin`,
  `::test_every_arm_is_settled_under_one_contract_and_keeps_its_findings`,
  `::test_a_stopped_attempt_gets_a_stopped_payload_and_no_invented_items`,
  `::test_a_markdown_only_payload_is_refused_rather_than_masked`,
  `::test_an_arm_specific_structure_invalidates_the_attempt`,
  `::test_a_contract_that_changed_since_dispatch_accepts_nothing`.
- Still required (P22): **render a dispatch template that writes the contract payload** — the #149
  template writes the Markdown form only, which settlement refuses to mask rather than converting
  (section 12, D2) — pin the study's own output-contract validator, probe the findings, clean and
  stopped outcomes in **each** arm, and run `payload.py uniformity` over every receipt before anything
  is masked. A field only one arm carries blocks masking until the freeze rules on it by name.

### gap-7 — A required evidence judgment for every shell command's network use · `tooling-delivered`

Every retained shell command carries a recorded judgment that either establishes that no traffic
occurred or binds the command to retained proxy events. **No command is passed on its spelling**:
arbitrary interpreters hide networking behind imports, aliases and child processes. The pilot's audit
checked paths only, so proxy bypass is unaudited for every historical attempt.

- Control: `run_cell.py` `audit_network`, against the
  [`egress_proxy.py`](../bounded-discovery-runs-2026-09-08/scripts/egress_proxy.py) log.
- Tests: `test_review_fixes.py::test_direct_socket_evidence_requires_a_recorded_judgment`,
  `::test_indirect_network_and_ordinary_shell_both_require_review`.
- Still required (P23): freeze this as a **requirement**, not a coordinator feature, and retain each
  command's judgment against the proxy log — including commands that look local and indirect
  interpreter traffic. An unreviewed command or an unresolved proxy bypass invalidates fidelity.

### gap-8 — Fresh targets and reviewer isolation · `specified-only`

#153 revealed all four #138 registers, their leak sets, the schedule and the candidate inventory. The
four pull requests stay reserved and cannot be reused blind; issue closure or a renamed slot cannot
restore blindness.

- Rule: apply [#148's criteria](../bounded-discovery-prototype/targets/criteria.md) E1–E11 unchanged to
  **newly selected** candidates, with new registers, new leak sets, a newly sealed inventory and a
  fresh selector context per target.
- **The reservation list grows by rule, not by hand.** #148 section 7's list is extended with: the four
  #138 targets (`clap-rs/clap#6212`, `grpc/grpc-go#7417`, `nats-io/nats-server#6593`,
  `nats-io/nats-server#7395`); the two excluded registers' pull requests (`grpc/grpc-go#8519`,
  `golang-jwt/jwt#456`); and **every pull request named in the revealed candidate inventory** — 28 in
  total at this writing — because that file publishes each candidate's category and eligibility result,
  and the hypothesis and confirmation for those examined that far. The freeze derives that set from
  [`revealed/targets/inventory.md`](../bounded-discovery-decision-2026-09-11/revealed/targets/inventory.md)
  rather than transcribing it.
- The mix stays **three buggy and one clean**, one per category C1–C4, purposively sampled: a mechanism
  pilot, not a prevalence estimate.
- Still required (P24): the full per-target preparation checklist — pins, truncated mirror with
  negative leak-set checks, packet build, offline provisioning, adjudication, sealing, one selector
  run, manifest — for four new targets. **No selection happens in this document.**
- **Carried cue to avoid repeating:** one pilot slot's selector output characterised a lock as a hazard
  drawing on the pull request's own body text, and was kept as delivered because reselecting after
  seeing it would have been worse than the cue. A freeze records any equivalent cue **before** dispatch
  rather than at grading.

### gap-9 — Requalification of every runtime control · `unknown`

**Every** control in the old preregistration section 4 must be re-established on the runtime a future
study actually dispatches with, before the freeze. None of them is carried forward as a current
capability claim. The #153 observation that Claude Code 2.1.268 removes the Bash tool outright under
`--restricted` is **historical evidence to re-probe**, not a fact about any runtime a study would use —
and if it holds, the frozen dispatch template cannot run as written, because the primary needs an
interpreter for the policy's own validator and the per-target execution allowance.

- Control: none. This is probe evidence or it is nothing.
- Still required (P00–P16): the full catalogue in [`probes.md`](probes.md), starting with the runtime
  inventory (version, help output, image and configuration) that pins what every other probe ran on.
- **An unsupported control stops the study.** It is not designed around, and a control that cannot be
  observed is not a pass.

### gap-10 — Ledger stop and conservative accounting after termination · `tooling-delivered`

The ledger gains an atomic, immutable terminal `stop` that preserves the prior event chain, the actual
cost, the reservations and the retained uncertainty. After it, new attempts, pre-freeze and review
reservations, cap freezing and a second stop are all refused; existing work can still settle, attempts
can still close, and protected grading and closeout reservations remain possible under the existing
gates. **A stop does not terminate workers and does not establish that they stopped** — that is gap 5's
gate — and it must not release unknown costs or rewrite the handoff.

- Control: `budget.py` `stop` and `require_running`.
- Tests: `test_budget.py::test_stop_retains_money_and_history_then_settles`,
  `::test_stop_refuses_restart_but_allows_protected_closeout`,
  `::test_stop_before_freeze_does_not_release_pre_freeze_reservation`,
  `::test_concurrent_stops_append_exactly_once`,
  `::test_missing_evidence_and_unreadable_input_exit_codes`.
- Still required (P25): exercise stop with outstanding reservations and retained uncertainty, then a
  subsequent settlement and attempt closure and a refused new review dispatch; retain the producing
  ticket, the reason and the handoff evidence; separately cancel workers and pass the shutdown probes.
- **Scope, decided here:** a future study runs on **its own ledger** with its own cap. The #138 ledger
  stays exactly as #153 left it — $50.3304587 actual, $0.164316 retained uncertainty, an unbroken
  eighty-eight-event chain and no terminal stop — and the decision bundle remains that epic's closing
  record. This specification appends nothing to it, and a future freeze must not either.

### study-isolation — The isolation regime and the repository hazard · `unknown`

See section 5.2. The regime itself (host absence, container mounts, or both) is `unknown` until P16
establishes what the future host can reach, and the freeze states which one it froze and what it
therefore cannot claim.

### study-budget — Cap, ceilings, allowances · `budget-dependent`

Section 9. Nothing numeric is chosen here.

### study-frozen-inputs — The frozen-input chain · `specified-only`

The chain the pilot did establish, three links deep, for all eight of its attempts, and which a new
freeze must re-establish over its own rendered template: the dispatch template against its pin, each
rendered prompt against the digest sealed beside it, and that same file against the value published in
the public cell summary. "No unfilled placeholder" stays a dispatch precondition.

- Control: `run_cell.py`'s rendering path, whose `--self-test` covers placeholder substitution and
  refusal. No `test_*` case in this repository covers the chain end to end, which is why this row is
  `specified-only` rather than `tooling-delivered`.
- Still required (P26): re-establish all three links over the study's own template and prompts.

## 7. Required probes

[`probes.md`](probes.md) is the catalogue: twenty-seven probes in two groups — requalification of the
old preregistration section 4 (P00–P16, starting with the runtime inventory every other probe is read
against) and the #199 controls on a real runtime and real targets (P17–P26) — each with what it must
establish, what refuses it, and whether it needs paid model sessions.

**No probe has been run and none may be run from this document.** A paid probe needs its own
reservation on the study's ledger, inside a pre-freeze subtotal a freeze has not yet set. The pilot's
thirteen capability probes cost $1.0418428 and retained $0.082158 of uncertainty; that is the closed
grid's figure, offered as an order of magnitude and not as a budget.

**A probe that did not complete establishes nothing.** Any non-zero exit blocks its step: retain the
output, fix the cause and re-probe. An incomplete probe is never turned into passing evidence, and an
unobservable setting is never a pass.

## 8. Cells, order, replacement and the schedule

Preserved from the closed design, because these are the units the screens need:

- **Twenty-four planned cells**: four slots × A/B/C × two fresh replicates. A replicate is an ordinal,
  not a reproducible sample — the runtime exposes no seed.
- **Contiguous A/B/C triples**, so a budget or runtime stop leaves whole triples: the unit the matched
  cost ratio and per-target recall both need.
- **The order rule is frozen in the clear; the resolved order is sealed**, because naming the pilot pair
  in the clear would identify the clean slot by elimination. Pilot = the adjudicated clean slot and the
  lowest-numbered buggy slot, replicate 1, arms A/B/C per slot with the clean slot first; then replicate
  1 of the remaining slots and all of replicate 2, slots in numeric order.
- **One cell at a time.** Two live cells on one machine are readable by each other through the same
  interpreter path. This costs wall-clock time and nothing else.
- **Replacement is earned only by documented infrastructure or input invalidity**, and it invalidates
  exactly the comparison cells whose affected status changes; unrelated faithful cells stand. A valid
  substantive miss, a false finding and a skill timeout are **results**, not rerun opportunities. If
  required invalidation exceeds the allowance, **stop and close out the partial experiment**.
- **The allowance itself is `budget-dependent`** (section 9). The pilot's three replacements against a
  27-attempt cap proved thin: closing out its six unresolved-or-invalid attempts would have needed six
  replacements against the one that remained.

## 9. Budget and accounting · `budget-dependent`

**No cap, ceiling or allowance is chosen in this document.** Every figure below is a method for
computing one, not a value.

| Item | How a freeze sets it | Status |
| --- | --- | --- |
| Rate card | the dated rates of the runtime at freeze time, recorded as a pinned file | `unknown` |
| Per-cell projection | measured attempts under the pinned policy at those rates, per arm; A from control cells, B repricing the verifier children at the candidate tier's ratio, C adding a finder priced from the selector sessions plus admission and falsification of finder claims | `budget-dependent` |
| Whole-review dollars per attempt | the enforced ceiling, plus one-call headroom, because the allowance is checked **after** a call completes | `budget-dependent` |
| Token, request, command and wall-clock ceilings | audited after the fact — the runtime has no hard token control — with the dollar allowance the enforced one | `budget-dependent` |
| Finder sublimit | charged **inside** the arm ceiling, never in addition | `budget-dependent` |
| Frozen cap | `min(1.5 × projection, ceiling)`, recorded once with `cap-freeze`, refusing a cap below the sunk spend or one that cannot also hold the protected reserve | `budget-dependent` |
| Replacement allowance and attempt cap | from the projection and the observed cell-cost spread, stated with the risk rather than smoothed | `budget-dependent` |
| Grading and closeout reserve | protected, and reachable after the terminal stop | `budget-dependent` |

Accounting rules that are **not** budget-dependent and are carried forward unchanged:

- **Settle from the runtime self-report and from the retained per-request records; when they differ,
  charge the larger and record the difference as a reconciliation residual.** The pilot's runtime
  billed a small untranscripted request in six of thirteen probes; meter from both sources rather than
  treating the gap as noise.
- An attempt that produced **no self-report** settles from its transcript and retains one further
  request at the largest observed per-request cost as uncertainty.
- **Retained uncertainty comes off the remaining allowance.** A session that may yet be billed is not
  headroom, and a terminal stop does not release it.
- Review consumption, one-off setup and selection, and charged grading are **separate columns**. Shared
  setup is charged once to the study, never once per arm and never omitted.
- Matched cost compares billed cells **from this grid only**; another grid's absolute dollars are not
  transplanted. Each cell is charged all of its attempts, discarded predecessors included.
- **The risk is stated prospectively, not smoothed.** If the projection's headroom is thin, what
  protects the study is the ledger's atomic reservation refusing the first dispatch that cannot fit,
  and the contiguous-triple order leaving an interpretable partial grid. A design that shrinks when
  money runs short is not one of the protections.

## 10. Screening, failure and stop rules

### 10.1 The screen

Preregistration section 8, preserved, applied by a pinned scorer over explicit adjudicated fields only.
Screen **B against A** and **C against A** separately; every criterion must hold:

1. **zero** raw false finding items in the candidate arm, invalid attempts included;
2. no worse false-clean count **and** no worse false-clean rate;
3. no worse completion;
4. macro material recall: at least a 20% relative gain with a positive absolute gain, in **both** the
   all-attempt and the completed-only view; where the control's macro recall is 0, +10 percentage
   points instead;
5. median matched billed cell-cost ratio ≤ 1.25, cells matched by target and replicate.

Reported beside, as evidence and not gates: sufficient-outcome recall, aggregate fix sufficiency,
unjustified action errors, priority errors, and zero-recovery attempts that did not claim clean.

**False clean is frozen independently** of recovery credit, reviewer priority or action, and fix
sufficiency: an attempt on an adjudicated buggy target that explicitly returns Approved / clean / no
material defects is false clean even if it recovered the defect. A published `Approved` status *is* an
explicit clean return.

**Blockers force `inconclusive`:** unresolved material truth, a planned cell without a **valid
completed** outcome — attempted but invalid or unfinished counts as missing, not present — or a changed
clean/buggy mix. One thing outranks them: a supported raw false finding **rejects** the arm outright on
its own evidence, and the verdict is `fail`, not `inconclusive`. A partial run reports what it measured.

A complete positive screen recommends a **fresh confirmation study** against the then-current policy.
Four targets and two replicates support neither an equivalence claim nor a promotion.

### 10.2 What invalidates an attempt

| Condition | Consequence |
| --- | --- |
| Model or effort mismatch on any assistant line, or an unobservable setting | fidelity failure; the attempt is invalid, never relabelled as an equivalent treatment |
| A read outside the frozen permitted roots | invalid on protocol grounds, with no settlement acceptance path |
| A shell command with no recorded network-evidence judgment, or an unresolved proxy bypass | fidelity failure |
| A dispatch with no retained launch record | the launch is prevented, not recorded afterwards |
| A missing, changed or unbound payload contract; a refused payload; a second payload form | settlement problem; the attempt is operationally invalid |
| A missing or malformed finder in arm C | operational failure: cancel remaining work, preserve partial stores, close the attempt. **No restart, no silent arm B substitution, no clean inference.** |
| A required verifier that fails, times out, omits an id or cannot inspect decisive evidence | record the missing dispatch, ruling or evidence; withhold the unconfirmed finding; derive with incomplete verification |
| Reaching the attempt's dollar ceiling | `stopped-budget` — a **measured result**, not infrastructure invalidity, and not replacement-eligible |

### 10.3 What stops the study

- **An unsupported or unobservable runtime control** (gap 9).
- **Required invalidation exceeding the replacement allowance** — stop and close out the partial
  experiment rather than raising the allowance mid-grid.
- **A reservation that cannot fit under the cap** — the ledger refuses the dispatch; the study stops at
  a triple boundary.
- **A failed or incomplete shutdown probe** — nothing sealed is opened.
- **Any non-zero exit from a pinned script** — read the handoff rather than dispatching again.

### 10.4 Terminal sequence

1. Record the terminal decision and its reason.
2. `budget.py … stop` with the producing ticket, the reason and the retained handoff reference.
3. Cancel workers; settle outstanding bounds; leave retained uncertainty retained.
4. Archive or remove the cell workspaces, keeping each recorded root's parent readable.
5. `shutdown.py check` over the recorded roots and the ledger; every check must be established.
6. `shutdown.py authorize --gate … --ledger …` immediately before the seal is opened.
7. Only then reveal, join, score and decide.

## 11. Evidence needed to approve the freeze

A freeze is approvable when **all** of the following exist and are retained. Anything missing leaves the
study unfrozen; there is no partial-credit path.

1. **A runtime inventory** — version, help output, image identity and configuration — pinned by digest,
   naming the runtime every probe below ran on and every cell will dispatch with.
2. **Every probe in [`probes.md`](probes.md) completed**, with its record retained and its verdict
   read from the probe's own output. Not one of them excused, deferred or inferred.
3. **Every row of [`readiness.json`](readiness.json)** moved from its current status to established
   evidence, with the evidence named. `check_spec.py` refuses a status that claims establishment, so
   the freeze supplies its own record rather than editing this one.
4. **Four fresh targets** prepared end to end under #148's criteria, sealed, with the extended
   reservation set applied and every surviving blinding cue listed.
5. **Pins**: policy commit and skill tree, method, design, adapter, coordinator, scorer, rate card,
   payload contract, the study's own output-contract validator, the roots record digest and the
   rendered dispatch template — each by digest in a manifest, with a verifier that recomputes all of
   them, the git pins, the scope-to-packet bindings and the ledger reconciliation, and exits non-zero
   on any drift. Run it before every dispatch.
6. **A ledger** opened for this study with its `cap-freeze` recorded against the projection, the
   protected reserve set, and the pre-freeze spend reconciled.
7. **The roots record** created while the roots exist, outside every cell root and outside the seal,
   with its digest bound in the coordinator config.
8. **A dispatch template** rendered for each arm that writes the contract payload, with the
   no-unfilled-placeholder assertion as a dispatch precondition, and a probed findings / clean /
   stopped outcome in each arm.
9. **A sealed schedule** whose resolved order is not readable in the clear.
10. **A recorded dispatch authorization** — an explicit decision, on the ticket, that this study runs.
    **This document is not that decision and cannot become one by being merged.**

## 12. Proposed changes to the closed design, each justified

The contrast is preserved. These are the only changes proposed, and each names why the closed design
cannot simply be re-dispatched.

**D1 — Fresh targets (forced).** #153 revealed the four registers, the leak sets, the schedule and the
28-candidate inventory. Blindness cannot be restored by closing an issue or renaming a slot.
*Justification:* without this the study measures reviewers who could read the answer from the
repository that hosts their harness. See gap-8.

**D2 — The dispatch template must write the contract payload.** The #149 template instructs the Markdown
payload form only; settlement now refuses to mask a Markdown-only payload rather than converting it.
*Justification:* uniform payload shape is gap 6, and a converted payload would reintroduce the tell at
the conversion step. *Disclosed risk:* requiring a structured payload changes what **every** arm writes
relative to the pilot, so the pilot's per-cell costs and elapsed times are not directly transferable to
the new projection, and the requirement must be identical in every arm so no arm gains a structural
advantage. The **content** policy under test is unchanged: the policy's own validator and emitter still
govern what a finding says; only the envelope it is delivered in is frozen.

**D3 — A prospectively frozen scratch allowance.** Either the frozen permitted roots include a named
per-cell scratch directory, identical in every arm and named in the dispatch prompt, or they do not and
there is no scratch. Either way the coordinator applies the frozen rule with **no acceptance path**.
*Justification:* the pilot lost an attempt because a cell redirected a `git show` from its own pinned
clone into a container-local scratch path outside the permitted roots, and the coordinator accepted it
at settlement as tidiness. A rule cannot be relaxed after the attempt it governs; it can be written
before. See gap-4.

**D4 — The container isolation regime is frozen prospectively, not carried as a deviation.** The pilot
declared host absence as the control, could not reach it, and ran cells in containers mounting only
their permitted roots under a dated deviation. *Justification:* the regime determines what the study can
claim about isolation, so it belongs in the freeze with its mount set asserted and recorded, and with
the residual reach it does not close stated in the same place. See section 5.2 and P16.

**D5 — The prospective ledger implementation is pinned, including `stop`.** *Justification:* gap 10; the
#138 grid could not close on its own ledger. The historical implementation stays byte-identical so the
old freeze still verifies. This is an intentional frozen/prospective fork, not two implementations to
synchronize.

**D6 — The replacement allowance and attempt cap are recomputed, not inherited.** *Justification:* the
pilot's three replacements were demonstrably insufficient for its own failure rate. `budget-dependent`;
no number is proposed here, and the stop rule for exceeding whatever is chosen is unchanged.

**D7 — The launch shape may have to change, and the freeze decides on probe evidence.** If the restriction
flag no longer admits a shell allow list, the frozen launch cannot run as written, because the primary
needs an interpreter for the policy's validator and the per-target execution allowance. *Candidate
routes, both `unknown`:* keep the restriction flag and move every shell need out of the cell; or drop it
and rest confinement on the container regime plus the allow list, disclosing that the interpreter path
was never closed either way. *Justification:* this is not a free choice — it changes what "execution
permissions are identical across arms" is a statement about — so it is made once, before the freeze,
with the probe record beside it, and it stops the study if neither route is supported. See gap-9 and P15.

**Unchanged, deliberately:** the hypothesis; the three arms and their invariants; the 24-cell grid, its
contiguous-triple order and its sealed schedule; one cell at a time; the screen and its five criteria;
the false-clean definition; the foreground-verification rule; the scope selector protocol and the
selector-miss rule; the target mix; the access classes; and the per-role settlement obligation.

## 13. Unknowns, marked

| # | Unknown | Resolved by |
| --- | --- | --- |
| U1 | The runtime: version, whether a shell exists under the restriction flag, whether a startup-supplied worker definition still binds child model and effort, whether the effort vocabulary is unchanged | P01–P16 |
| U2 | Whether the proposed model candidates exist and are observably distinct on that runtime | P01 |
| U3 | The rate card, the per-cell projection, and therefore every ceiling, the cap, the replacement allowance and the attempt cap | P01–P16 then section 9 |
| U4 | The isolation regime the future host can actually reach | P16 |
| U5 | Whether per-role metering needs initial/follow-up verifier granularity for the intended analysis | freeze decision, gap-2 |
| U6 | The four targets: none is selected, and none may be selected from this document | P24 |
| U7 | Whether a study is warranted at all | the #207 entry condition; #153 recommended none |

## 14. What this document does not do

- It does not freeze, qualify or authorize anything, and it does not become a freeze by being merged.
- It selects no target, opens no seal, runs no probe and charges nothing.
- It changes no historical artifact: the pilot, closeout, grading and decision bundles, their sealed
  material, the #138 ledger and #149's frozen inputs are all untouched, and #199 stays open.
- It claims nothing about any runtime. Every runtime statement in it is about the pilot's runtime, at
  the pilot's date, offered as evidence to re-probe.
- It recommends no arm, sets no threshold and changes no default.
