---
name: implement-publish
description: Implement work from a spec, issue, or set of tickets and open a pull request for it. Use when the caller wants the implementation published as a pull request, not just written.
---

# Implement and publish

Implement the work, then open one pull request linked to its spec. This skill stops at the pull request; reviewing it is `code-review-publish`'s job.

## Process

### 1. Resolve the targets

Read `docs/agents/issue-tracker.md` when present, then resolve the spec — the issue, tickets, or written specification describing the work — and the base branch to merge into. Ask the user before any external write if either is ambiguous.

### 2. Prepare the branch

Follow the repository's branch and commit conventions. If the current branch is unsuitable as a pull-request head under them, branch from the base before any work starts. Implement on a branch, never on the base.

### 3. Implement

Honor an implementation skill the user names. Otherwise invoke the model-invoked implementation skill whose description best matches the work; invoking this skill authorizes reaching it. Failing that, implement directly.

End with the work committed on the branch and the relevant checks run.

### 4. Open the pull request

Check for an existing pull request from this head before creating one:

```sh
gh pr list --head <branch> --base <base> --state open --json number,url
```

Update that one's body if it exists; otherwise push and `gh pr create --base <base> --head <branch> --title "..." --body-file -`. Either way, exactly one pull request, and its body must:

- summarize the change;
- link the originating issue or tickets as the spec source, or name and link the specification when the spec lives outside the forge;
- list the verification performed.

Leave issue status, labels, and assignees alone.

Attempt each write once; on an ambiguous result read the target before a single retry, then report the failure rather than writing again.

Finish with the pull request link, head SHA, branch, spec source, and anything that failed.
