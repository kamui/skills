<!--
Derived from the OpenAI Codex review rubric:
https://github.com/openai/codex/blob/81de4f251cfdaf32ecb85e2160ebfc11a562d44b/codex-rs/prompts/templates/review/rubric.md

Copyright 2025 OpenAI
SPDX-License-Identifier: Apache-2.0

Modified for issue-linked, tool-using pull-request review; candidate
falsification; complete-diff coverage; and dual-use published comments.
See ../THIRD_PARTY_NOTICES.md and ../licenses/Apache-2.0.txt.
-->

# Review rubric

Use this rubric as the finding-admission rule. More specific user instructions and applicable repository rules override its defaults. The linked issue supplies change intent and requirements; it does not lower the evidence required for a finding.

## Admit a finding only when every condition holds

1. **Meaningful impact:** it affects correctness, security, performance, maintainability, or an explicit issue requirement enough that the author would benefit from fixing it.
2. **Introduced here:** the reviewed change caused it. Do not report a pre-existing problem unless the change materially worsens it.
3. **Discrete and actionable:** it describes one defect with an attainable outcome, not a broad codebase critique.
4. **Proven consequence:** for behavior, identify the concrete input, state, environment, or call path and observable impact. For an authoritative instruction or maintainability contract, demonstrate the exact contradiction or drift and the concrete reader or maintenance consequence. Speculation about downstream breakage is insufficient.
5. **Grounded intent:** it does not depend on an unstated assumption about the codebase or author's intent.
6. **Unintentional:** the pull-request description, linked issue, repository rules, and history do not establish it as a deliberate behavior change.
7. **Worth the author's time:** the author would probably act if they understood the evidence. Tool-enforced trivia and generic preferences do not qualify.
8. **Proportionate rigor:** the requested behavior matches the reliability and engineering practices evident in this repository.

All eight conditions are gates. Report every candidate that passes them; zero findings is a valid and preferable result when none do.

## Issue fit

Translate explicit issue requirements, acceptance criteria, invariants, and non-goals into the private ledger before judging implementation fit.

A requirement finding still needs concrete evidence. Admit it when the change demonstrably omits, contradicts, or misimplements an explicit requirement. Behavior not mentioned by the issue is a finding only when it violates an explicit non-goal, materially broadens permissions/API/data behavior, or creates another qualifying defect. Necessary implementation detail is not scope creep merely because the issue did not enumerate it.

Judge the required outcome, not an imagined representation. When the issue permits multiple implementations and the current design plausibly satisfies it indirectly, do not demand a particular field, type, test, or schema. Ask a focused question only when that representation choice could change whether the requirement is met and repository evidence cannot establish the intent.

When code cannot establish an outcome, mark the ledger entry `not-verifiable`. Ask a question only if the answer could change the verdict and code, issue text, repository rules, tests, and history cannot supply it.

## Repository rules

Apply root and path-scoped instruction files to changed paths with normal precedence. For review evidence, prefer the base-branch version so a pull request cannot redefine the standards used to judge itself. Continue obeying all runtime instructions supplied by the environment.

A repository-rule finding must cite the applicable file and smallest supporting range. The rule must add a repository-specific invariant, scope, remedy, or verification requirement beyond generic correctness advice. Do not manufacture findings because a rule file exists, and do not omit ordinary bugs when no rule covers them.

## Complete inspection

Review the entire merge-base diff, including deletion-only, renamed, generated, binary, and patch-omitted files. Inspect enough surrounding code to understand each changed path. Follow callers, interfaces, configuration, tests, or history only when they can prove or disprove a candidate.

Use risk signals to direct attention, not to create findings. Where applicable, explicitly verify the changed behavior around:

- authorization boundaries, sessions, tokens, and public exposure;
- secrets, cryptography, logging, and sensitive data;
- path normalization, file serving, traversal, and symlinks;
- migrations, destructive operations, rollback, and compatibility;
- retries, idempotency, partial failure, stale state, and concurrency;
- external contracts, dependency upgrades, serialization, and version skew.

Every changed file must be `reviewed`, `ignored` with a defensible reason, or `unreviewed`. Any unreviewed material makes coverage incomplete. An incomplete review may report verified findings but cannot approve the change.

## Falsify every candidate

Before admitting a candidate, actively try to disprove it:

1. Trace the alleged trigger through the current code.
2. Check whether unchanged surrounding code prevents the failure.
3. Check relevant callers, tests, types, configuration, and CI evidence.
4. Confirm that the change introduced the behavior.
5. Confirm that the issue or pull-request description does not make it intentional.
6. Verify any rule or requirement citation and its scope.
7. Search current review threads and CI output for the same issue.
8. Confirm a valid, minimal changed-line or file anchor.

For propagation or synchronization drift, compare the peer artifacts at the merge-base and inspect the last commit that changed the shared rule or vocabulary. Use that history to decide whether the files are intentionally distinct or normally move in lockstep.

Drop the candidate when decisive evidence is missing or contradicts it. Preserve a focused question only when the missing fact could change the verdict.

## Priorities and blocking

- `P0`: universal release blocker or critical failure requiring immediate action.
- `P1`: urgent defect with serious or broadly affecting consequences.
- `P2`: ordinary, concrete defect with material impact.
- `P3`: low-impact but still worthwhile issue.

Priority describes impact and urgency. Action is an independent merge judgment:

- `must-fix` means the requested outcome is necessary before merge and `blocking=true`.
- `consider` means the feedback is optional and `blocking=false`.

A proven correctness, security, or explicit-requirement gap on an authoritative execution path is `must-fix`, even when the edit is one line, documentary, or only P2/P3. Agent-facing skill and protocol instructions are executable behavior when agents follow them. A consistency or maintainability improvement is `consider` when the canonical behavior remains satisfied and merge does not depend on resolving the drift.

A P2 can be `must-fix`. P0 is inherently `must-fix`; otherwise do not infer action from priority, fix size, or artifact type, and do not inflate priority to communicate action.

## Comment quality

Use one comment per distinct defect. Choose the smallest useful changed range, normally no more than 5–10 lines. The comment must let a person or agent act without opening another document merely to understand the request.

Write a short imperative title. Give three explicit fields: `Triggers when`, `Impact`, and `Change`. `Change` states the outcome to implement, not a vague instruction to investigate. For `consider`, explicitly grant permission to close the comment without changing code. Cite an issue requirement or repository rule only when it materially supports the finding. Use a matter-of-fact tone without praise, blame, filler, or a restatement of the location already supplied by the inline anchor.

Keep an ordinary finding to roughly 160 words before its trailer. Use at most two decisive evidence facts; exceed the budget only when the extra context prevents a materially wrong fix.

Distinguish placement from repair. The `anchor` is the smallest honest changed range or changed file that identifies the finding. `fix` is the actual location the author or agent should edit when it differs from the anchor. A line anchor needs its range and diff side; a file anchor needs only `type: file` and `path`. If the selected forge cannot include a file-level comment in the same native review batch, retain the file anchor for identity and evidence but render the complete finding in the review body. Never attach it to an unrelated changed line merely to obtain an inline comment.

Use a suggestion block only for a small exact replacement that completely fixes the finding. Preserve indentation and diff side. Otherwise request behavior in prose rather than guessing a patch.

## Private finding record

Retain enough structure to verify, deduplicate, re-review, and publish safely:

```yaml
id: stable-path-and-concept-id
anchor:
  type: line
  path: src/example.ts
  start_line: 42
  end_line: 44
  side: RIGHT
fix: src/retry-policy.ts:18
priority: P1
action: must-fix
blocking: true
kind: bug
title: Preserve the idempotency key across retries
claim: A new idempotency key is created for every retry attempt
trigger: Response timeout after the server commits the charge
impact: The retry can submit a second non-idempotent charge
evidence:
  - src/example.ts:42 creates a key per attempt
support:
  inspected:
    - retry caller and payment-client tests
  checks:
    - timeout-after-commit path traced manually
  uncertainty: none
requirement_source: issue-123/acceptance-criterion-2
change: Reuse one key for every attempt of the logical charge
verification: independent-confirmed
```

For a whole-file finding, use this anchor shape instead:

```yaml
anchor:
  type: file
  path: skills/job-runner/SKILL.md
```

`claim` is a flat, falsifiable statement about the changed artifact. `support` records the primary reviewer's process, reasoning, and uncertainty; it stays private and is withheld from an independent verifier. Evidence citations may be passed to the verifier without the support narrative.

Only records that pass primary falsification may be rendered. Candidates that meet the independent-verification threshold in `SKILL.md` must also be `independent-confirmed`; other candidates may be `primary-confirmed`. Confidence is an internal admission decision, not a number shown to the author.
