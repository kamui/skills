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

Specific user instructions and applicable base-branch repository rules override these defaults. Intent establishes the desired outcome; evidence establishes whether the change delivers it.

## Admission

Report actionable defects with an established trigger, meaningful consequence, grounded intent, and a proportionate remedy. Challenge each suspicion with the strongest available counterevidence. Choose the investigation that can settle it; verify citations and the actual repair site. Deduplicate by defect and requested outcome. Drop contradicted candidates without recording the investigation history.

A code defect must be introduced or materially worsened here. Compare base and head guarantees, including guarantees removed from unchanged callers. An explicit requirement makes its outcome this change's responsibility even when the omission predates the diff. Agent-facing instructions can be defective when their contradiction has a concrete execution or reader consequence.

Preferences, speculative harm, and tool-enforced trivia do not qualify. An actual defect remains one even if another tool should catch it. Intent can justify a deliberate change, subject to released compatibility. Approval settles only what it addressed; deferred decisions follow `targets.md`'s Recorded deferrals.

## Requirements ledger

Derive checkable outcomes from supplied issues/specs and then the PR title/body or real commit messages, before inspecting compliance. Include acceptance criteria, invariants, non-goals, and concrete preservation or performance promises. Implementation is evidence, never the source of its own requirements. With no intent source, the ledger is empty.

Each row records the outcome, source coordinate, class (`acceptance requirement` or `supporting assertion`), disposition (`met`, `partial`, or `not-verifiable`), and decisive evidence. Use stable coordinates such as `issue-123/acceptance-criterion-2`, `spec-<identity>/<section>`, `pr-title`, `pr-body/"<quoted phrase>"`, or `commit-<sha7>/"<quoted phrase>"`.

Judge outcomes, allowing any implementation that satisfies them. An unmet acceptance requirement can be a `kind=requirement` finding. A contradicted supporting assertion needs an independently qualifying defect. Read supplied measurements before judging them; an unsettled explicit performance threshold is a question, while an unverified adjective is not.

When conformance to a versioned artifact is required, derive obligations from that pinned artifact or its version delta. Record each required public addition, removal, rename, or signature/field change at `artifact-<identity>@<version or range>/<path>:<name>`. Honor documented exceptions. Check the consuming definitions and exports, including aliases and conditional implementations; search misses alone do not prove omissions. A demonstrated mismatch is `partial` and a requirement candidate. An unavailable artifact creates a coverage gap; invent no obligations from the submitted diff.

## Released compatibility

For a promise changing a released observable contract, assess implementation and compatibility separately. Give its ledger row a `compliance` disposition (`met`, `partial`, or `not-verifiable`) and a linked `kind=compatibility` candidate, even when the promise is implemented.

Establish the contract from versioned documentation, tests, callers, and applicable release decisions. Intent, approval, or a benchmark alone does not establish compatibility. Record inspected versions and scope, then classify `compatibility` as `preserved`, `supported-break`, `violated`, or `unresolved`. A supported break needs an applicable release decision and migration or compatibility handling. A violation needs a demonstrated introduced consequence and ordinary finding admission.

For unresolved compatibility, name what could settle it and whether that fact could change the merge decision. Missing required sources leave coverage incomplete. Inability to enumerate every downstream consumer alone warrants neither a question nor a claim of global safety.

## Changed tests

Assess whether changed tests can detect the behavior they claim to protect. Follow enough of their setup, assertions, and cleanup to settle that question, using execution or a code trace as appropriate.

When the repository provides a cheap focused command and a safe disposable environment, run the changed test or the smallest affected group once at the pinned head. Reuse readable exact-head CI evidence of that same test. Keep the reviewed tree intact and build output disposable. Follow caller or repository run limits; otherwise allow five minutes per command and ten for provisioning. Use no production services, credentials, or destructive external effects. Run at most one suite and never a suite to reproduce a focused failure. Record the command, head, exit status, and decisive output, or why execution was unavailable.

A reproducible introduced assertion failure is a bug candidate; decide whether the product or expectation is wrong from the evidence. A CI test failure is ordinarily `must-fix` and needs independent confirmation. Environment failure is unavailable evidence. A code trace can settle a case without execution; unavailability alone is never a pass.

A weak new test is at most a maintainability `consider` finding under ordinary admission. Removing existing regression protection is a correctness `must-fix` unless explicitly accepted. A passing test establishes only what its assertions cover.

## Supplied checks

Evidence uses shared context plus one line per check; expanded records are also valid. Context identifies the full commit SHA, clean or dirty state, relevant environment, and relevant source, fixture, generated-input, dependency, or configuration changes. Each check identifies its command or run, result, readable output reference, scope, and any skipped or incomplete work.

Reuse evidence when its identity, inputs, environment, scope, and successful completion match the obligation. Read the relevant output. Exact-head obligations require the reviewed commit; an uncommitted run counts only for the commit made from exactly that tree. Earlier evidence remains historical at its original head. A new head does not automatically require rerunning everything: select a focused check or trace where the existing evidence cannot settle the question.

Supplied results do not replace changed-test inspection, independent verification, or safety-premise challenges. Missing metadata alone is neither a defect nor a coverage gap; judge what obligation remains unsettled. Keep test failures, environment failures, and missing checks distinct.

In `summary.check_details`, account for each supplied check as `accepted`, `historical`, `reviewer-executed`, or `unused/unavailable`, with its identity, original head, and a reason for the last three. Group shared context and reference supporting artifacts. Execute within Changed tests' bounds.

## Questions, observations, and gaps

A material question identifies an unavailable fact or decision, who or what can settle it, and how the answer changes the review. Finish available investigation first. Keep the candidate's stable id when routing it to a question.

An observation is an evidenced, non-actionable fact. Publish at most three, with one sentence and an evidence pointer each; keep others privately as `observation (unpublished, cap)`. Observations never hide unfinished candidates or safety assertions and do not affect status.

Record consequential competing readings as ambiguities, including the reading applied. Required evidence or unfinished verification leaves a coverage gap naming its effect, affected ids, and recovery input. Required unresolved verification becomes a qualifying question or outstanding work.

## Priority and action

Priority follows demonstrated impact, urgency, and reach: `P0` critical or universally blocking, `P1` serious and urgent, `P2` ordinarily material, `P3` low-impact but worthwhile. Confirmation does not raise priority.

Action is independent. A proven correctness, security, or explicit-requirement gap on an authoritative execution path is `must-fix`, even at P2 or P3. Maintainability, test hygiene, and optional consistency are `consider` when canonical behavior remains intact. P0 is always `must-fix`. A repository-rule finding cites the base rule and the repository-specific obligation it adds.

## Survivor record

Keep each survivor's stable id, kind, priority, action, claim, trigger, impact, change, anchor, optional distinct fix site, and decisive evidence and sources. Kinds are `bug`, `compatibility`, `concurrency`, `invariant`, `security`, `performance`, `maintainability`, and `requirement`. Keep private reasoning separate from the falsifiable claim sent to a verifier. Render only admitted findings, confirmed when required; lowering priority or action does not erase a confirmation.
