<!--
Derived from the OpenAI Codex review rubric:
https://github.com/openai/codex/blob/81de4f251cfdaf32ecb85e2160ebfc11a562d44b/codex-rs/prompts/templates/review/rubric.md

Copyright 2025 OpenAI
SPDX-License-Identifier: Apache-2.0

Modified for issue-linked, tool-using change review; candidate
falsification; complete-diff coverage; and dual-use published comments.
See ../THIRD_PARTY_NOTICES.md and ../licenses/Apache-2.0.txt.
-->

<!-- DRAFT. Replaces review-rubric.md, conformance.md, released-compatibility.md,
changed-tests.md, and check-evidence.md. The verifier builder embeds the sections
marked (embedded) by heading. -->

# Review rubric

Specific user instructions and applicable base-branch repository rules override these defaults. Intent sources never lower the evidence bar.

## Admission

Admit every distinct, actionable defect with a proven trigger, a meaningful consequence, grounded intent, and a remedy proportionate to this repository's practices. Preferences, tool-enforced trivia, speculative downstream harm, and unfinished research stay out. An authoritative instruction can be defective when you demonstrate the contradiction and its concrete consequence. A tool that ought to catch a defect does not refute one present in the diff.

**Introduced here.** A code defect must be introduced or materially worsened by this change. Compare base and head guarantees: removing a lock, ordering, ownership rule, or validation can break unchanged code. A path already unsafe under the same guarantees is pre-existing. An explicit requirement instead makes its outcome this change's responsibility, even when the gap lies entirely in unchanged code.

**Falsify.** Attack each candidate through its actual trigger, guards, callers, tests, configuration, history, and intent. Verify every citation and the real repair site. For synchronization drift, find the consumers across the repository under old and new vocabulary and compare their base state. Deduplicate by defect and requested outcome.

**Intent.** Sources can establish a deliberate change, subject to Released compatibility. Approval or merge accepts only what the review explicitly addressed. Approval of an unreleased public API is provisional.

**Deferrals.** An explicit deferral of a design, naming, or API-shape decision in any participant's review comment leaves that decision open without making it a question for this merge. Record its author, comment, surface, and current decision. Publish about it only when this change releases the deferred surface, breaks an applicable repository rule, or leaves a material decision unresolved. A later comment or commit that settles it closes it. A defect on the same surface is an ordinary finding.

## Requirements ledger

List checkable outcomes from explicit issues and specs, then from the change description: the PR title and body, or a range's real commit messages. Include acceptance criteria, invariants, non-goals, and concrete behavior, compatibility, performance, or preservation promises. Generic adjectives and restatements add no row, and implementation supplies evidence, never requirements. With no issue, spec, or commit message the ledger is empty and the summary says issue alignment was unavailable; a missing required issue is an `issue-required` question.

Each row keeps its outcome, source coordinate, class, disposition, and decisive evidence. Coordinates look like `issue-123/acceptance-criterion-2`, `spec-<identity>/<section>`, `pr-title`, `pr-body/"<quoted phrase>"`, and `commit-<sha7>/"<quoted phrase>"`. The class is **acceptance requirement** or **supporting assertion**, such as a reported measurement. Dispositions are `met`, `partial`, or `not-verifiable`; explain anything short of met.

An omitted or contradicted acceptance requirement can be a `kind=requirement` finding. A contradicted supporting assertion needs an independently qualifying defect. Judge the required outcome and accept indirect implementations. Unmentioned behavior qualifies only through a non-goal violation, a material expansion of permissions, API, or data behavior, or another admitted defect. Read supplied measurements and their methods before calling a row unverifiable. An explicit performance threshold without settling evidence is a question; an unverified adjective, or a supplied measurement you could not repeat on another machine, is not.

**Conformance.** When a source or repository convention requires conformance to a versioned artifact (a stub, binding, or SDK tracking a release; a schema; generated code and its generator input), take its pinned export surface or version delta and add one acceptance row per public addition, removal, rename, or changed signature, at `artifact-<identity>@<version>/<path>:<name>`. A search only locates: read the consumer's definition, alias, re-export, and conditional-export sites before ruling. Conventions that tolerate an omission produce no row; cite them once. An artifact you cannot obtain produces no rows, never rows reconstructed from the submitted diff, and a coverage gap naming the surfaces it would have covered.

## Released compatibility (embedded)

When a promise changes an externally observable contract of released code (return values, ordering, error shapes, cursor or length semantics, visible side effects), give the row a `compliance` disposition and a separate `compatibility` disposition, and raise a linked `kind=compatibility` candidate even when compliance is `met`. Establish the released contract from versioned documentation, existing tests, and in-repo callers. Dispose it as `preserved` with evidence, `supported-break` with a release decision and migration, `violated` with a demonstrated introduced violation, or `unresolved` with the remaining gap. Intent, approval, or a benchmark alone never closes compatibility, and an absent in-repo counterexample does not prove every downstream caller safe. Inability to enumerate downstream consumers alone creates no question.

## Changed tests (embedded)

**Inspecting.** For every test function the change adds or substantively changes, read setup, the call under test, the assertions, and cleanup in execution order. Decide whether the assertions observe the claimed behavior, and whether setup or cleanup semantics defeat the test: a deferred cleanup evaluated at the statement, a fixture torn down before the call, a mock never armed, a value read after it was cleared. Summarize a table-driven group by its mechanism plus each departing row. Moved, renamed, or reformatted tests carry no new obligation.

**Running.** Where the repository names a cheap focused command and a disposable environment is available, run the changed test or smallest affected group once at the pinned head. Bound each command at five minutes and provisioning at ten unless the caller sets tighter limits. Keep caches and build output out of the reviewed tree, and use no production service, credentials, or destructive external effect. Run a suite at most once per review, never to reproduce a focused failure. Reuse an exact-head CI run of the same test when its log is readable. Record the command, head, exit status, and decisive output lines, or what was unavailable. Unavailable execution is never a pass, and it leaves coverage complete when a trace settles the case.

- A reproducible assertion failure the diff introduces is a `bug` candidate, ordinarily `must-fix` when CI runs the test. The test's expectation governs unless intent or a repository rule shows the expectation is wrong.
- A setup, network, or toolchain failure is unavailable evidence: decide the case by trace.
- A failure also present at the merge-base is pre-existing unless the change worsens it or a requirement owns it.
- A test that cannot fail, or a regression test that also passes at the merge-base, supports at most a `maintainability` `consider` finding.
- A pass is evidence about the test, never proof the product change is sufficient.

## Supplied checks

Reuse a supplied result only when its identity and scope match the obligation, it ran on the exact reviewed head with unchanged relevant inputs and a matching environment, and it completed with readable output. An incomplete, skipped, or unreadable result proves nothing. Evidence from an earlier head stays historical at that head and never satisfies an exact-head obligation. Reuse never replaces changed-test inspection or verification. Account for each supplied check as accepted, historical, reviewer-executed, or unused, with a reason for the last three.

## Questions, observations, and gaps

A material question names a fact or decision no available static source can settle, who or what can answer it, and how the answer changes correctness, a requirement, a release obligation, or this merge. Record which candidate reopens or requirement closes. Incomplete research is never a question. A candidate routed to a question keeps its stable id.

An observation is an accurate, non-actionable fact with decisive evidence that lacks a qualifying consequence, or a verifier aside. A proven low-impact defect is still a finding. Publish at most three, one sentence and an evidence pointer each. Observations never affect status or hold unfinished candidates.

For a contestable contract term, record both supportable readings and the safer one applied as an ambiguity, and route a question or gap if it blocks a settled decision. An unavailable input leaves coverage incomplete; recovery reruns the affected falsification before the gap closes. A required unresolved verification task ends as a question or outstanding work.

## Priority and action

Priority measures demonstrated impact, urgency, and reach: `P0` a universal release blocker or critical failure, `P1` a serious urgent defect, `P2` an ordinary material defect, `P3` a low-impact worthwhile defect. Visibility and confirmation never raise it.

Action is independent. A proven correctness, security, or explicit-requirement gap on an authoritative execution path, including agent-facing instructions and CI-run tests, is `must-fix` at any priority. A maintainability improvement with canonical behavior intact, test hygiene, and optional consistency are `consider`. P0 is always `must-fix`.

A repository-rule finding cites the base-branch rule file and its smallest supporting range, and the rule must add something beyond generic correctness advice.

## Survivor record

Keep each survivor's stable id, kind, priority, action, claim, trigger, impact, change, anchor, optional distinct fix site, and decisive evidence and sources. Kinds are `bug`, `compatibility`, `concurrency`, `invariant`, `security`, `performance`, `maintainability`, and `requirement`; use `concurrency` or `invariant` for shared-state rules. Keep the falsifiable claim apart from private support, which never enters a verifier brief. A stable id names the path and defect concept, never a line number, and survives across heads. A confirmed candidate keeps its confirmation when its priority or action is lowered.
