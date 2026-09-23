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

Use these admission rules throughout the review. Specific user instructions and applicable base-branch repository rules override defaults; intent sources never lower the evidence bar.

## Finding admission

Admit every distinct, actionable defect that has meaningful, proven consequences, grounded intent, and an attainable remedy proportionate to this repository's practices. Preferences, tool-enforced trivia, speculative downstream harm, and unfinished research do not qualify. An authoritative instruction can be defective: demonstrate the contradiction and its concrete reader or execution consequence. A tool that ought to catch a defect does not refute one present in the diff.

A Code defect must be introduced or materially worsened here. Compare base and head guarantees: removing a lock, ordering, ownership rule, or validation can break unchanged code. A path already unsafe under the same guarantees is pre-existing. An explicit requirement instead makes its outcome this change's responsibility, even when the omission predates the diff or lies entirely in unchanged code.

Try to disprove each candidate through its actual trigger, guards, callers, tests, configuration, history, and intent. Verify citations and the real repair site. For synchronization drift, establish the consumers across the repository using old and new vocabulary, then compare their base state and shared-rule history. Deduplicate by defect and requested outcome. Dropped candidates leave no record.

Intent may establish a deliberate change, subject to the released-compatibility procedure below. Approval or merge accepts only what the review explicitly addressed. Approval of an unreleased public API is provisional; an explicit deferral leaves that decision open. On PRs, the target reference's Recorded deferrals rule determines whether that decision affects this merge.

## Issue fit

Before compliance inspection, list checkable outcomes from explicit issues/specs, then the change description, PR title/body or real range commit messages. Include acceptance criteria, invariants, non-goals, and concrete behavior, compatibility, performance, or preservation promises. Generic adjectives and restated requirements add no row. Implementation supplies evidence, never requirements. With no commits or spec a local ledger is empty.

Each row retains its outcome, source coordinate, class, disposition, and decisive evidence. Coordinates include `issue-123/acceptance-criterion-2`, `spec-<identity>/<section>`, `pr-title`, `pr-body/"<quoted phrase>"`, and `commit-<sha7>/"<quoted phrase>"`. Classes distinguish an **acceptance requirement** from a **supporting assertion**, such as a reported measurement or local test result. Dispositions are `met`, `partial`, or `not-verifiable`. Explain an incomplete or contradicted outcome; a met row needs only its evidence pointer.

An omitted or contradicted acceptance requirement can be a `kind=requirement` finding. A supporting assertion's contradiction needs an independently qualifying defect. Judge the required outcome, allowing indirect implementations; do not demand an unstated representation. Unmentioned behavior qualifies only through a non-goal violation, material expansion of permissions/API/data behavior, or another admitted defect.

- When a source or repository convention requires conformance to a versioned artifact, read [`conformance.md`](conformance.md). It adds artifact obligations, including unchanged consumers.
- When a promise changes an externally observable released contract, read [`released-compatibility.md`](released-compatibility.md). Compliance with intent does not establish compatibility.

Read supplied measurements and their methods before declaring a row unverifiable. Record what a missing fact could change, or why no material decision depends on it. Neither an unverified adjective nor failure to repeat a supplied measurement on another machine creates a question. An explicit performance threshold without settling evidence does.

## Questions, observations, and gaps

A material question names a fact or decision no available static source can settle, who or what measurement can answer it, and how the answer changes correctness, an acceptance criterion, a release obligation, or this merge decision. Record which candidate reopens or requirement closes. Incomplete research is not a question. A candidate routed to a question keeps its stable id.

An accurate non-actionable fact with decisive evidence may be an observation when it lacks qualifying consequence or arrives as a verifier aside. A proven low-impact defect remains a finding. Do not use observations to retain unfinished candidates or safety assertions. Publish at most three observations, one sentence and evidence pointer each; keep excess eligible facts privately as `observation (unpublished, cap)`. They never affect status.

For a contestable contract term, record both supportable readings and the applied safer reading as an ambiguity. If that prevents a settled decision, also route the material question or coverage gap. An unavailable input leaves coverage incomplete: name its effect and gated candidate ids and request it from the orchestrator. Recovery reruns the affected falsifications before removing the gap. A required unresolved verifier task ends as a qualifying question or outstanding work, never a private drop.

## Priority and action

Priority measures demonstrated impact, urgency, and reach: `P0` universal release blocker or critical failure; `P1` serious urgent defect; `P2` ordinary material defect; `P3` low-impact worthwhile defect. Visibility and independent confirmation do not raise priority.

Action is independent. A proven correctness, security, or explicit-requirement gap on an authoritative execution path is `must-fix`, including agent-facing instructions and P2/P3 defects. A maintainability improvement with canonical behavior intact is `consider`. P0 is always `must-fix`; otherwise neither artifact type nor repair size decides action.

A repository-rule finding cites the applicable base-branch file and smallest supporting range. The rule must add a repository-specific invariant, scope, remedy, or verification requirement beyond generic correctness advice.

Test/fixture hygiene and optional consistency are `maintainability` and `consider` when no correctness or requirement gap is established. A generated artifact contradicting its source is judged under that proven gap, not downgraded to hygiene.

## Survivor record

Retain stable concept id, kind, priority, action, claim, trigger, impact, change, anchor, optional different fix site, and decisive evidence and sources. Kinds are `bug`, `compatibility`, `concurrency`, `invariant`, `security`, `performance`, `maintainability`, and `requirement`; use concurrency/invariant for shared state rules needing the verifier's bug-class check. Keep the falsifiable claim separate from private support, which never enters a verifier brief. Only primary-admitted survivors render, with independent confirmation when required. A confirmed candidate retains that confirmation if its priority or action is lowered.
