---
name: implement-publish
description: Implement work from a spec, issue, or set of tickets and open a pull request for it. Use when the caller wants the implementation published as a pull request, not just written.
---

# Implement and publish

Implement the work, review it locally with a fresh-context subagent, then open one pull request linked to its spec. This skill stops at the pull request; `review-code-publish` handles the published review.

## Process

### 1. Resolve the targets

Read `docs/agents/issue-tracker.md` when present, then resolve the spec — the issue, tickets, or written specification describing the work — and the base branch to merge into. The spec includes every issue the user provides and every one inferred from the request, branch name, or commits; record each so the pull request can account for it. Ask the user before any external write if either is ambiguous.

### 2. Prepare the branch

Follow the repository's branch and commit conventions. If the current branch is unsuitable as a pull-request head under them, branch from the base before any work starts. Implement on a branch, never on the base.

### 3. Implement

Honor an implementation skill the user names. Otherwise invoke the model-invoked implementation skill whose description best matches the work; invoking this skill authorizes reaching it. Failing that, implement directly.

End with the work committed on the branch and the relevant checks run. Keep implementation and review local until step 5.

### 4. Review before publishing

Spawn one **general-purpose** reviewer as a resumable subagent in a fresh context that inherits none of the implementation conversation; use `fork_turns="none"` or the host's equivalent. State its model tier in the dispatch: one tier below a top-tier implementor, otherwise the harness default; the verifier `review-code` may dispatch inherits that tier rather than dropping again. Use a general-purpose type because it must be able to dispatch that verifier; `Explore` and `Plan` types that lack the `Agent` tool are unsuitable.

Run every reviewer phase in this step, the first review and each continuation below, on an **awaited** route: one whose tool call delivers the completed result while this step stays active. A foreground dispatch (`run_in_background: false`, or the host's equivalent), a blocking continuation, a supported join, or a runtime-managed suspension that resumes this step without a final hand-back qualifies. An acknowledgment, an agent id, a pending notice, or a delay is not completion, and ending the turn leaves the result unreachable. Choose each phase's route before sending it, from the host's tools or established behavior, without changing global runtime settings. When no awaited route exists, stop with `review-wait-unavailable` before dispatching, naming the phase, the missing operation, and any work already pending. A hand-back with a phase pending is a failed step, not a report; a reviewer that fails or returns a partial review keeps the coverage routing below.

Brief the reviewer to invoke `review-code` with `mode: one-shot` on the range from the base to the committed head, passing every spec source resolved in step 1 as the user-supplied spec. Have it return the complete would-be review — summary, findings, questions, and coverage — plus the routed items and record paths needed to resume. The core builds its own context, so do not pass a merge-base diff command. Its read-only bound applies: the reviewed source is never changed, while focused tests run only in a disposable environment under the rubric's Changed tests section.

Read the returned review. Treat every `must-fix` finding as blocking and every `consider` finding as optional; report coverage gaps and unresolved questions. Evaluate every finding against the code and spec. Fix warranted defects, rerun affected checks, and commit the fixes. Record an evidence-based reason for declining a finding; a disputed blocking defect remains unresolved.

After committing fixes, continue the same reviewer with the new head and the stable ids fixed when resuming it is awaited. When the host's resumption returns before its result, as a message-based resume that acknowledges and runs in the background does, choose a **fresh continuation** before sending anything: one new isolated general-purpose reviewer at the same tier, dispatched on an awaited route. It replaces the completed reviewer's next phase; it is never a second reviewer beside a pending one, a retry of a failed review, or a way past a partial result. Brief it with the repository, applicable instructions and every spec source, the base and full reviewed and final head SHAs, the original record paths, the complete review and its routed items, the fixed stable ids, every unresolved or disputed finding and material question, and the existing finding, coverage, and verification state, including whether the follow-up batch is spent. It first confirms each record path is readable and belongs to that review and reviewed head; missing or mismatched state is a reported coverage gap, never a clean addendum.

Either continuation returns an addendum appended beside the original record, which stays unchanged. The addendum re-verifies each fixed finding against the new head with bounded reads and focused tests, and inspects the complete fix delta (`git diff <reviewed head>...<final head>`) under the rubric's Complete inspection rules. It falsifies every new candidate and dispatches one verifier batch containing every new candidate that meets `review-code`'s mandatory-verification trigger, waiting for that batch before it returns. Changing workers keeps stable ids, verification accounting, test restrictions, and the batch cap; it grants no extra batch. A finding the addendum cannot settle remains blocking. When the fix delta is too large to inspect as a delta, replace the addendum with a fresh-context one-shot review of the full base-to-final-head range that accounts for every outstanding finding and question.

Proceed only when the reviewer has covered the final committed head and no blocking defects or material coverage gaps remain. A further commit voids coverage of the earlier head. If an isolated reviewer is unavailable or a blocker cannot be resolved, report the limitation and stop before publishing. Carry the review results into the final handoff in step 5, and hand back only after step 5 has pushed the reviewed head and its pull request exists.

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

Finish with the pull request link, head SHA, branch, spec source, review outcome, any remaining optional findings, and anything that failed.
