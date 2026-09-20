---
name: implement-publish
description: Implement work from a spec, issue, or set of tickets and open a pull request for it. Use when the caller wants the implementation published as a pull request, not just written.
---

# Implement and publish

Implement the work, review it locally with a fresh-context subagent, then open one pull request linked to its spec. This skill stops at the pull request; `review-code-publish` handles the published review.

## Process

### 1. Resolve the targets

Read `docs/agents/issue-tracker.md` when present. Resolve the spec, forge, source and target repositories, and base branch from repository configuration, Git remotes, and the user's request. Record every issue, ticket, or written specification supplied by the user or inferred from the request, branch name, or commits for the pull request to address. Ask before any external write if the spec or publication target is ambiguous.

### 2. Prepare the branch

Follow the repository's branch and commit conventions. If the current branch is unsuitable as a pull-request head under them, branch from the base before any work starts. Implement on a branch, never on the base.

### 3. Implement

Use the implementation skill the user names, otherwise the best-matching model-invoked implementation skill. Implement directly if none applies.

Read **Supplied check evidence** in `review-code`'s `references/review-rubric.md` for the verification format and reuse criteria. Save a compact summary:

- Shared full commit SHA, clean/dirty input state and relevant environment.
- One line per check: command or check-run identity, result and readable output reference. Include relevant exceptions and coverage limits; link to logs instead of copying them.
- For required acceptance exercises that checks do not settle: criterion, method and observation under the same shared context, without correctness claims.

For initial implementation and review fixes, report missing required evidence and why it is missing. Do not add verification solely to populate the summary.

Apply these **verification rules** to implementation and review fixes:

- Run the repository's documented focused checks for changed behavior and its dependents. Documentation-only changes need tests only when documented checks cover them.
- Batch related changes before running shared checks once; group review fixes sharing a check into one continuation.
- Rerun checks when changes may affect their inputs, environment or covered behavior. Run the affected broader suite for shared dependency or configuration changes, cross-module changes, or uncertain impact, even if it passed earlier.
- Reuse success only for the same check at the exact head, with unchanged relevant inputs and environment and sufficient coverage. Uncommitted runs count only for the commit made from exactly that tree.
- Repeat required acceptance exercises when changes affect their criterion, method or inputs.
- Retain unaffected results at their original head and input state without rerunning solely because the head changed. They cannot satisfy checks explicitly required at the new head.

Finish with committed changes and recorded verification results. Keep implementation and review local until step 5.

### 4. Review before publishing

Spawn one resumable **general-purpose** reviewer capable of dispatching a verifier. Give it a fresh context with no implementation conversation, using `fork_turns="none"` or equivalent. Report the selected tier.

Every review and continuation must use an **awaited** route that delivers its completed result while this step stays active: foreground dispatch (`run_in_background: false` or equivalent), blocking continuation, supported join, or runtime-managed suspension that resumes this step without a final hand-back. Acknowledgments, agent ids, pending notices, and delays do not establish completion. Choose the route before dispatch from available tools or established host behavior, without changing global runtime settings. Name each phase's actual host operation in the final report. If no awaited route exists, stop before dispatch with `review-wait-unavailable`, naming the phase, missing operation, and pending work. Handing back with a phase pending fails this step. Failed or partial reviews follow the coverage rules below, not this unavailable-route stop.

Brief the reviewer to invoke `review-code` with `mode: one-shot` and `profile: implementation-gate` on the range from the base to the committed head, passing every spec source resolved in step 1 as the user-supplied spec. Require the complete output defined in its Return section, including `record.json` and the paths needed to resume. Supply target refs, leaving context construction, review execution, and artifact generation to `review-code` under its own rules.

Give the reviewer the saved verification results and missing required evidence. Pass checks as `review-code`'s caller-supplied check evidence. Include observations and artifact references without implementation discussion or correctness claims. The reviewer validates results it relies on and reports material verification gaps. Keep the results' path with the review record so another reviewer can continue.

Read the returned review. Treat every `must-fix` finding as blocking and every `consider` finding as optional; report coverage gaps and unresolved questions. Evaluate every finding against the code and spec. Fix warranted defects, verify them under step 3's rules, and commit the fixes. Record an evidence-based reason for declining a finding; a disputed blocking defect remains unresolved.

After committing fixes, read and follow [the continuation procedure](references/continuation.md) before choosing or dispatching the next reviewer phase. Include that reference in the continuation brief.

Publish only after review covers the final committed head with no blocking defects or material coverage gaps. Any later commit requires review. If an isolated reviewer is unavailable or a blocker remains unresolved, report it and stop before publishing. Hand back the review results only after step 5 pushes the reviewed head and its pull request exists.

### 5. Open the pull request

Use the resolved forge's available CLI, API, or integration. Push the reviewed head through its supported workflow, then find any open pull request matching the source repository and branch and target repository and branch. Update its body if one exists; otherwise create one with a title and body. End with exactly one pull request at the reviewed head. Its body must:

- summarize the change;
- link every issue resolved in step 1 with its disposition: **closes**, using supported automatic closure on merge when available and noting when unavailable; **partially implements**, naming what remains open; or **affects**, stating how. For a spec outside the forge, name and link it;
- summarize verification results and remaining gaps, sharing head and input state across checks and acceptance observations where they match. Identify each acceptance criterion and keep historical results attributed to their original head.

Leave issue status, labels, and assignees alone.

Attempt each write once; on an ambiguous result read the target before a single retry, then report the failure rather than writing again.

Finish with the pull request link, head SHA, branch, spec source, review outcome, the host operation each reviewer phase ran on, any remaining optional findings, and anything that failed.
