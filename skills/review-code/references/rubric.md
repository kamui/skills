<!--
Derived from the OpenAI Codex review rubric:
https://github.com/openai/codex/blob/81de4f251cfdaf32ecb85e2160ebfc11a562d44b/codex-rs/prompts/templates/review/rubric.md

Copyright 2025 OpenAI
SPDX-License-Identifier: Apache-2.0

Modified for issue-linked, tool-using change review; candidate
falsification; complete-diff coverage; and dual-use published comments.
See ../THIRD_PARTY_NOTICES.md and ../licenses/Apache-2.0.txt.
-->

# Review rubric

Specific user instructions and applicable base-branch repository rules override these defaults. Intent sources never lower the evidence bar.

## Admission

Admit every distinct, actionable defect with a proven trigger, a meaningful consequence, grounded intent, and an attainable remedy proportionate to this repository's practices. Preferences, tool-enforced trivia, speculative downstream harm, and unfinished research stay out. An authoritative instruction can be defective when you demonstrate the contradiction and its concrete reader or execution consequence. A tool that ought to catch a defect does not refute one present in the diff.

**Introduced here.** A code defect must be introduced or materially worsened by this change. Compare base and head guarantees: removing a lock, ordering, ownership rule, or validation can break unchanged code. A path already unsafe under the same guarantees is pre-existing. An explicit requirement instead makes its outcome this change's responsibility, even when the omission predates the diff or lies entirely in unchanged code.

**Falsify.** Attack each candidate through its actual trigger, guards, callers, tests, configuration, history, and intent. Verify every citation and the real repair site. For synchronization drift, find the consumers across the repository under old and new vocabulary and compare their base state and shared-rule history. Deduplicate by defect and requested outcome. Dropped candidates leave no record.

**Intent.** Sources can establish a deliberate change, subject to Released compatibility. Approval or merge accepts only what the review explicitly addressed. Approval of an unreleased public API is provisional, and an explicit deferral leaves that decision open; on a pull request, `targets.md`'s Recorded deferrals decides whether it affects this merge.

## Requirements ledger

Before compliance inspection, list checkable outcomes from explicit issues and specs, then from the change description: the PR title and body, or a range's real commit messages. Include acceptance criteria, invariants, non-goals, and concrete behavior, compatibility, performance, or preservation promises. Generic adjectives and restatements add no row; implementation supplies evidence, never requirements. With no issue, spec, or commit message the ledger is empty.

Each row keeps its outcome, source coordinate, class, disposition, and decisive evidence. Coordinates include `issue-123/acceptance-criterion-2`, `spec-<identity>/<section>`, `pr-title`, `pr-body/"<quoted phrase>"`, and `commit-<sha7>/"<quoted phrase>"`. The class is **acceptance requirement** or **supporting assertion**, such as a reported measurement or local test result. Dispositions are `met`, `partial`, or `not-verifiable`; explain anything short of met, and give a met row only its evidence pointer.

An omitted or contradicted acceptance requirement can be a `kind=requirement` finding; a contradicted supporting assertion needs an independently qualifying defect. Judge the required outcome, accepting indirect implementations and never demanding an unstated representation. Unmentioned behavior qualifies only through a non-goal violation, a material expansion of permissions, API, or data behavior, or another admitted defect. Read supplied measurements and methods before calling a row unverifiable, and record what a missing fact could change or why nothing material depends on it. An explicit performance threshold without settling evidence is a question; an unverified adjective, or a measurement you could not repeat on another machine, is not.

**Conformance.** When a source or repository convention requires conformance to a versioned artifact (a stub, binding, or SDK tracking a release; a schema; generated code and its generator input), the artifact is a third row source. Take its pinned export surface, or for a bump the delta between pinned versions (a compare, export list, changelog API section, or generated-symbol list), not its tree file by file. Add one acceptance row per public addition, removal, rename, or changed signature or field at `artifact-<identity>@<version or range>/<path>:<name>`; public means exported, documented, or un-underscored at module level. Private internals, incidental mentions in tests or prose, and what a repository convention explicitly tolerates add no row; cite that convention once. A tolerated widening is a candidate only on its own consequence, never as a missing name.

Locate each obligation in the consuming tree, unchanged files included. A search only locates: read the definition, or the alias, re-export, conditional or platform-guarded export, and documented-exception sites that could supply the name, and compare signature or fields. A demonstrated omission or contradiction is `partial` and a `kind=requirement` candidate sourced at the `artifact-` coordinate; an untouched consumer, or a name it never carried, refutes nothing when this change owns conformance. An artifact you cannot obtain adds no rows, never rows rebuilt from the submitted diff, and a coverage gap naming it and the consumer surfaces it would cover; enumerate its rows once supplied.

## Released compatibility

When a ledger promise changes an externally observable contract of released code (return values, cursor, capacity, or length semantics, ordering, error shapes, side effects visible through public methods), give the row a `compliance` disposition (`met`, `partial`, or `not-verifiable`: is the promise implemented) and a separate `compatibility` disposition (is the change supported). Before judging compliance, raise a linked `kind=compatibility` candidate, keep its id in the row, and falsify it even when compliance is `met`.

Establish the released contract from versioned documentation and examples, existing tests, and in-repo callers of the changed method, recording versions, coordinates, and inspected scope; compare the promise against them and the base and head code. Intent, approval, or a benchmark alone never closes compatibility. Dispose it `preserved` with evidence in the inspected scope, `supported-break` with an applicable release decision and supported migration or compatibility handling, `violated` with a demonstrated introduced violation, or `unresolved` with the remaining gap. An absent in-repo counterexample does not prove every downstream caller safe.

`violated` is a candidate under the ordinary gates, including introduced-here and proven consequence, and the compatibility verification trigger; the author's promise alone does not refute it. A supported breaking release is not automatically a defect. For `unresolved`, finish the available legwork, then apply the question rule, naming the settling fact, the obligation it bears on, and how the answer settles it. Inability to enumerate downstream consumers alone creates neither a mandatory question nor `Needs Information`: with no concrete conflict or material open decision, keep the residual gap and disposition privately, without claiming global safety. Missing required sources or unfinished checks still leave coverage incomplete.

## Changed tests

**Inspecting.** For each test function the change adds or substantively changes, read setup and fixtures, the call, the assertions, and cleanup in execution order; moved, renamed, or reformatted tests owe nothing new. Decide whether the assertions observe the claimed behavior (none on the call, or only on setup, observe nothing), and whether setup or cleanup defeats the test under the language's rules: a deferred cleanup whose arguments are evaluated at the statement, a fixture torn down before the call, a mock never armed, a value read after it was cleared. Summarize a table-driven group by its mechanism plus each departing row. Trace each suspicious or unexecuted case through its decisive lines; write no other trace unless it decides a candidate.

**Running.** When the repository names a cheap focused command (a per-test or per-package invocation its docs name) and a safe disposable environment exists, run the changed test or the smallest affected group once at the pinned head. Keep the reviewed tree and identity intact, and caches, build output, and harnesses disposable. Bound each command and provisioning by the caller's, packet's, or repository's run policy, else five and ten minutes. Use no production service, credentials, or destructive external effect; never run a suite to reproduce a focused failure, and at most one suite per review. Reuse a readable exact-head CI run of the same test. Record command, head, exit status, and decisive output lines, or what was unavailable (toolchain, offline dependencies, runner). Unavailable execution is never a pass, and leaves coverage complete when a trace settles the case.

- A reproducible assertion failure the diff introduces is a `bug` candidate. The test's expectation governs unless the issue, change description, or a repository rule shows it wrong; `Change` names whichever of test or product the evidence shows wrong, else the failing expectation. Priority follows impact; a CI-run test is an authoritative path, so ordinarily `must-fix`, verified under the red-test rule.
- A setup, network, or toolchain failure is unavailable evidence, not a test failure: decide by trace.
- A failure also present at the merge-base (run the command there once, or read base CI, only when needed) is pre-existing unless the change materially worsens it or a requirement owns it.
- A test that cannot fail, asserts nothing on the call, or as a regression test passes at the merge-base supports at most a `maintainability` `consider` candidate meeting the ordinary bar; otherwise it is an observation or dropped.
- A pass is evidence about the test, never proof the product change suffices; dispositions and falsification rest on the product code.

## Supplied checks

Check evidence is shared context plus one line per check; expanded records remain valid. Context names the full commit SHA, clean or dirty state, relevant environment, and changed fixtures, generated inputs, dependencies, or configuration. Each line names a command or check-run identity, result, readable output reference, scope the command does not show, and any skip or incomplete run, overriding context where it differs. Read a result's relevant output, not unrelated logs. Unknown reuse facts make evidence unavailable for that obligation; missing metadata alone is no finding or gap.

Supplied results never prove correctness. Reuse one only when its identity and scope match the obligation; it ran on the exact full reviewed head with unchanged relevant source, fixtures, generated inputs, dependencies, and configuration, in a matching environment; it completed successfully with readable output; and coverage suffices. A run on uncommitted work counts only for the commit made from exactly that tree. An incomplete, unreadable, skipped, or cancelled result proves nothing. A new head invalidates without forcing reruns: unaffected evidence stays historical at its original head, never relabelled, and cannot satisfy a new-head obligation. Uncertain reach, changed inputs or environment, narrow coverage, or a candidate outside it needs a focused check or trace you select; a broad earlier pass never settles a new suspected defect. Reuse never replaces changed-test inspection, verification, or safety-premise challenges, never widens execution authority, and keeps test failures, environment failures, and missing checks distinct.

Account for each supplied check by identity, original head, and disposition (accepted, historical, reviewer-executed, or unused/unavailable, with a reason for the last three), referencing the supplied summary, preserving structured fields, and grouping matching heads and reasons in `summary.check_details`. Execute under Changed tests, repeating only a focused test that decides a candidate.

## Questions, observations, and gaps

A material question names a fact or decision no available static source can settle, who or what measurement can answer it, and how the answer changes correctness, an acceptance criterion, a release obligation, or this merge, and records which candidate reopens or requirement closes. Incomplete research is never a question. A candidate routed to a question keeps its stable id.

An observation is an accurate, non-actionable fact with decisive evidence but no qualifying consequence, or a verifier aside; a proven low-impact defect is a finding. Observations never hold unfinished candidates or safety assertions and never affect status. Publish at most three, one sentence and evidence pointer each; keep the rest privately as `observation (unpublished, cap)`.

For a contestable contract term, record both supportable readings and the safer one applied as an ambiguity, and route a question or gap if it prevents a settled decision. An unavailable input leaves coverage incomplete: name its effect and gated candidate ids and request it from the orchestrator; recovery reruns the affected falsification before the gap closes. A required unresolved verification task ends as a qualifying question or outstanding work, never a private drop.

## Priority and action

Priority measures demonstrated impact, urgency, and reach: `P0` a universal release blocker or critical failure, `P1` a serious urgent defect, `P2` an ordinary material defect, `P3` a low-impact worthwhile defect. Visibility and confirmation never raise it.

Action is independent. A proven correctness, security, or explicit-requirement gap on an authoritative execution path, agent-facing instructions included, is `must-fix` at any priority. Documented configuration, supported APIs and subclasses, and trust or security settings are authoritative paths; narrow reach lowers priority, never action. Maintainability with canonical behavior intact, test or fixture hygiene, and optional consistency are `consider` absent a correctness or requirement gap; a generated artifact contradicting its source is judged as that gap. P0 is always `must-fix`; otherwise neither artifact type nor repair size decides action. Before verification, recheck each `consider` candidate and observation; one proving such a gap becomes `must-fix`.

A repository-rule finding cites the base-branch rule file and its smallest supporting range, and the rule must add a repository-specific invariant, scope, remedy, or verification requirement beyond generic correctness advice.

## Survivor record

Keep each survivor's stable id, kind, priority, action, claim, trigger, impact, change, anchor, optional distinct fix site, and decisive evidence and sources. Kinds are `bug`, `compatibility`, `concurrency`, `invariant`, `security`, `performance`, `maintainability`, and `requirement`; use `concurrency` or `invariant` for shared-state rules needing the verifier's bug-class check. Keep the falsifiable claim apart from private support, which never enters a verifier brief. Only primary-admitted survivors render, confirmed when required, and a confirmation survives a lowered priority or action.
