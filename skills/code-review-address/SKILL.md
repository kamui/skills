---
name: code-review-address
description: Manually invoked workflow to address every pull-request review comment and publish a direct response to each one. Load only when the caller explicitly invokes code-review-address.
disable-model-invocation: true
---

# Address code review

Evaluate every review comment, make the warranted changes, and publish a direct response to every comment. A disagreement or no-change decision still requires a reply.

## Process

### 1. Resolve the target and capabilities

Read the repository's issue-tracker instructions, including `docs/agents/issue-tracker.md` when present. Resolve the pull request, its current head SHA and branch, and the connected forge or issue-tracker capabilities for:

- inline review threads and comments;
- overall review bodies and pull-request comments;
- replies, thread resolution or closure, and reactions.

Treat tools by capability, not vendor name. Explicit invocation authorizes the replies, resolutions, closures, and reactions described here. Follow the repository's normal authorization and workflow for commits and pushes.

If the pull request is ambiguous, ask before editing code or writing externally. If a capability is absent, continue with the supported actions and record the gap.

### 2. Inventory all review feedback

Fetch all review feedback, including inline comments, review threads, overall review bodies, and general pull-request comments that contain review feedback. Exclude automated status messages unless they request a code or documentation change.

Create a ledger keyed by each item's stable identifier or URL. Record its author, location, parent review, current resolution state, requested change, and whether it already has a substantive response from the current posting identity. Do not respond twice.

An overall review body is a separate feedback item when it contains feedback not represented by its inline comments. If the provider cannot reply directly to it, use a pull-request-level reply that links to or clearly identifies the review.

### 3. Evaluate and address each item

Honor a review-resolution or implementation skill the user names. Otherwise, let normal skill routing select any applicable skill. If none applies, evaluate and implement the feedback directly.

Check each comment against the current code, diff, originating spec, and documented repository standards. Do not accept feedback blindly. Assign one disposition:

- **Implemented**: make the smallest warranted change and verify it proportionately.
- **Already addressed**: identify the code, change, or commit that addresses it.
- **No change required**: explain why the suggestion is inapplicable, incorrect, optional, or intentionally declined, with concrete evidence.
- **Clarification or alternative**: answer a question, ask a focused question when the evidence is insufficient, or propose a better solution than the requested change.
- **Blocked**: state the blocker and the remaining action.

Uncertainty is not a reason to accept feedback or silently decline it. Ask the reviewer for the missing information and leave the item open. When the concern is valid but the requested fix is not, explain the tradeoff and suggest or implement the better alternative.

Apply all warranted code changes and run relevant checks before publishing responses. Re-read the resulting diff so replies describe the actual state. Follow repository conventions for committing and pushing; do not invent a commit policy.

### 4. Reply to every item

Publish one direct, substantive reply for every ledger item that lacks one. Each reply must state the disposition and enough evidence for the reviewer to verify it:

- for an implementation, summarize the change and relevant verification, with a commit or location when available;
- for an already-addressed item, point to the existing implementation;
- for a no-change decision, give the concise technical or product rationale;
- for a clarification or alternative, answer, ask the focused question, or explain the proposed approach;
- for a blocked item, name the blocker and next step.

A reaction never substitutes for the required reply. When the provider supports reactions, add one only when its meaning is unambiguous and useful—for example, a positive acknowledgement for helpful feedback. Do not use negative or argumentative reactions.

Reply to an overall review when it contains independent feedback or when a review-level summary is needed to make the dispositions clear. Avoid duplicating every thread reply in that summary.

### 5. Resolve completed threads

After its reply is confirmed, resolve or close a thread when the provider supports it and no work remains. This includes items implemented, already addressed, answered without a code change, or closed with a justified no-change decision. Leave blocked, incomplete, or awaiting-clarification threads open.

Do not mark a thread resolved before its reply and any required code change are present. If only the reviewer can resolve it, report that limitation instead of claiming success.

### 6. Verify publication

Attempt each external write once. If a result is ambiguous, read the target before one safe retry. Do not duplicate replies, reactions, or resolution actions.

Re-fetch the review activity and reconcile it with the ledger. Finish only after every feedback item has a confirmed reply or a reported publication failure. Report:

- counts by disposition;
- code changes and checks run;
- replies posted or already present;
- threads resolved, left open, or unsupported;
- reactions added;
- failed actions and links or stable identifiers for anything requiring follow-up.
