---
name: implement-publish
description: Implement work from a spec, issue, or set of tickets and open a pull request for it. Use when the caller wants the implementation published as a pull request, not just written.
---

# Implement and publish

Implement the work, review it locally with a fresh-context subagent, then open one pull request linked to its spec. This skill stops at the pull request; `code-review-publish` handles the published review.

## Process

### 1. Resolve the targets

Read `docs/agents/issue-tracker.md` when present, then resolve the spec — the issue, tickets, or written specification describing the work — and the base branch to merge into. The spec includes every issue the user provides and every one inferred from the request, branch name, or commits; record each so the pull request can account for it. Ask the user before any external write if either is ambiguous.

### 2. Prepare the branch

Follow the repository's branch and commit conventions. If the current branch is unsuitable as a pull-request head under them, branch from the base before any work starts. Implement on a branch, never on the base.

### 3. Implement

Honor an implementation skill the user names. Otherwise invoke the model-invoked implementation skill whose description best matches the work; invoking this skill authorizes reaching it. Failing that, implement directly.

End with the work committed on the branch and the relevant checks run. Keep implementation and review local until step 5.

### 4. Review before publishing

Spawn a separate reviewer with fresh context, without inheriting the implementation conversation. Use the host's context-isolation option, such as `fork_turns="none"` where available. Give it the repository path, base and head SHAs, the merge-base diff command, every spec source resolved in step 1, and the locations of repository instructions and coding standards. Supply user requirements and clarifications as source material, excluding the implementor's reasoning and conclusions.

The reviewer inspects the diff and relevant surrounding code independently for correctness, regressions, compliance with repository standards, and fidelity to the spec. Keep the review read-only and return findings internally, with file and line references, supporting evidence, and a distinction between blocking defects and optional suggestions. Report coverage gaps or missing information that prevents a judgment.

Evaluate every finding against the code and spec. Fix warranted defects, rerun affected checks, and commit the fixes. Return the updated head to the reviewer for verification and review of the new changes, keeping the implementation conversation excluded. Record an evidence-based reason for declining a finding; a disputed blocking defect remains unresolved.

Proceed only when the reviewer has covered the final committed head and no blocking defects or material coverage gaps remain. If an isolated reviewer is unavailable or a blocker cannot be resolved, report the limitation and stop before publishing. Include the review outcome and any remaining optional findings in the final handoff.

### 5. Open the pull request

Push the head branch first — an existing pull request advertises whatever its head points at, so skipping the push leaves the work invisible on a pull request that looks updated. Then check for one before creating another:

```sh
gh pr list --head <branch> --base <base> --state open --json number,url
```

Update that one's body if it exists; otherwise `gh pr create --base <base> --head <branch> --title "..." --body-file -`. Either way, exactly one pull request, and its body must:

- summarize the change;
- reference every issue resolved in step 1, each with its disposition: **closes** it, using the forge's closing keyword so the merge closes the issue; **partially implements** it, naming what remains open; or **affects** it, stating how. When the spec lives outside the forge, name and link the specification instead;
- list the verification performed.

Leave issue status, labels, and assignees alone.

Attempt each write once; on an ambiguous result read the target before a single retry, then report the failure rather than writing again.

Finish with the pull request link, head SHA, branch, spec source, and anything that failed.
