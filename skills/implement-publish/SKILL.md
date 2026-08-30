---
name: implement-publish
description: Implement work from a spec, issue, or set of tickets, then publish it as a new pull request. Use only when the caller intends implementation work published as a pull request.
---

# Implement and publish

Implement the work the user supplied, then publish it as a pull request linked to its spec. The skill creates the pull request; it does not review the change.

## Process

### 1. Resolve the targets

Read the repository's issue-tracker instructions, including `docs/agents/issue-tracker.md` when present. Resolve:

- the spec: the issue, tickets, or written specification describing the work;
- the base branch to merge into;
- the connected forge capabilities for creating pull requests and its default branch.

Follow repository-specific instructions for fetching and writing tracker data. Treat forge tools by capability, not vendor name. If the spec or base branch is ambiguous, ask the user before any external write. If a target or write capability is absent, continue with the supported target and record the gap for the final report.

### 2. Prepare the branch

Follow the repository's branch and commit conventions. If the current branch is unsuitable as a pull-request head under those conventions, create a branch from the base branch before any work starts. Never implement on the base branch.

### 3. Implement

Honor an implementation skill the user names. Otherwise, invoke the model-invoked implementation skill whose description best matches the requested work; the caller's invocation of this skill authorizes reaching it. If no implementation skill is available, implement the work directly.

The implementation must end with the work committed on the branch and the relevant checks run. Follow the repository's conventions for committing and pushing; do not invent a commit policy.

### 4. Publish the pull request

Push the branch, then create exactly one pull request from it into the base branch. Before writing, look for an open pull request from this head branch into the base branch. If one exists, update its body when the provider supports edits and report it as an existing publication instead of creating another. Do not create duplicates.

The pull request must:

- summarize the implemented change;
- link the originating issue or tickets and identify them as the spec source, or name and link the specification used when the spec is not tracked in the forge;
- list the verification performed.

Do not change issue status, labels, assignees, or other tracker fields directly.

Attempt each external write once. If a write returns an ambiguous result, read the target before deciding whether a retry is safe. Stop after one confirmed retry and report any remaining failure instead of continuing.

Finish with the pull request link, the head SHA, the branch, the spec source, and any unsupported or failed capabilities.
