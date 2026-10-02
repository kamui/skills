---
name: implement-publish
description: Implement work from a spec, issue, or set of tickets and open a pull request for it. Use when the caller wants the implementation published as a pull request, not just written.
---

# Implement and publish

Take a specification through implementation and an independent local review, then publish it as exactly one pull request. Publishing means pushing the reviewed branch and creating or updating its pull request, never merging or deploying. `review-code-publish` owns the published review.

Implementation method, investigation, sequencing, tools, and additional verification are yours to choose within the user's instructions, any implementation skill they name, and repository conventions.

## Resolve the delivery

Resolve the forge, source and target repositories, base branch, and every issue, ticket, and written specification the change addresses, including those inferred from the request, branch, and commits. Use repository tracker configuration such as `docs/agents/issue-tracker.md` where present. Settle consequential ambiguity before any external write, continuing independent local work meanwhile.

If the `review-code` skill is not installed, report `missing-dependency: review-code` before implementing.

Work on a branch suitable as a pull-request head, never the base. Leave issue status, labels, and assignees alone.

## Implement and keep evidence

Complete the requested behavior and commit it. Run the repository's documented checks for affected behavior and its dependents. Choose further checks and acceptance exercises by the change's risks, verifying more broadly where impact is uncertain.

Keep a compact evidence summary under the Supplied checks section of `review-code`'s `references/rubric.md`, which owns its form and reuse rules. Add each acceptance exercise's criterion, method, and observation, and any required work that is missing and why. After a change, update it with which evidence still applies and which was replaced. Never rerun a check only to fill the summary.

## Review locally

Everything stays local until the gate passes.

Use a fresh-context reviewer that has not seen the implementation conversation and can dispatch `review-code`'s verifiers. Honor a reviewer tier the caller names, and keep the selected tier for every continuation.

Before dispatching or continuing a review, choose a route that returns the completed result while you stay active: a foreground result, or a dispatch followed by a supported wait. An acknowledgment or agent identifier is not completion. With no such route, dispatch nothing and report `review-wait-unavailable` with the phase, missing operation, and pending work. Never change global runtime settings to obtain one.

Brief the reviewer to invoke `review-code` with `mode: one-shot` on the local base-to-head range. Supply the repository, explicit base and committed head, every specification source, and the evidence summary with its gaps: observations and artifacts, without implementation rationale or correctness claims. Require the completed status, coverage, and the `record.json`, `payload.json`, `batch.json`, and `report.md` paths.

Read `report.md` and validate the record under the gate before accepting it. Keep every accepted record's absolute path, in order. Evaluate findings against the code and specification; fix warranted defects, verify, and commit. Decline a finding only with evidence; a disputed `must-fix` blocks until the review settles it.

After fixes or new information, even without a code change, continue the review by resuming the completed reviewer or using another isolated one. Supply the latest accepted record as `prior_record`, the unchanged base and specification sources, the previously reviewed and final commit SHAs, fixed finding ids, and updated evidence with retention or invalidation reasons.

`review-code` owns review scope, finding classification, carried confirmations, unresolved questions, and verifier accounting. Its verification allowance is shared across continuations: a changed worker, failed work, or a repair grants no fresh one, and a replacement reviewer cannot bypass pending work. A record from before `review-code-record/1` cannot be a prior record; brief a full base-to-head review without `prior_record` instead.

## Gate

Validate each returned record against the committed head it reviewed, every accepted record in order, and itself:

```sh
python3 <skill root>/scripts/render_review.py --check --head <committed head> --lineage <each accepted record> --lineage <candidate record> <private-dir>
```

`<skill root>` is the record's `record.paths.skill_root`. A non-zero exit means a missing report, an invalid record, another head, or a continuation that forked from an older accepted record. Discard that record and continue from the latest accepted one.

Exit 0 establishes usable artifacts that match the head and history, not approval. Publish only when the final record's check names the commit you will push and prints `status Approved` and `coverage complete`: no required review work, evidence, or verification is unfinished.

`Needs Information`, `Changes Requested`, and `Incomplete` all withhold publication. Resolve what the reviewer needs and continue the review; an unanswered question never authorizes publication. `consider` findings may remain after approval. Any later commit needs review. If the gate cannot be met, report why and stop before publishing.

## Publish

Push the reviewed head. Find an open pull request matching both source and target repositories and branches, and update its body or create one. Confirm exactly one matching open pull request at the reviewed head.

Follow the repository's title and body conventions. Otherwise write a briefing readable in under a minute with `## Why`, `## Scope`, `## Tradeoffs`, `## Blast Radius`, and `## Verification`, omitting empty sections. Link every specification source and issue by its actual relationship, state a partial implementation's remaining work, and use the forge's issue-closing syntax for completed issues or note its absence. Preserve each verification result's head, input state, and gaps. Link bulky evidence, and give before and after measurements for a performance claim.

Attempt each external write once. After an ambiguous result, read the target before one retry, then report unresolved failure rather than writing again.

Finish with the pull request URL, head commit, branch, specification sources, review outcome, remaining optional findings or questions, and anything that failed.
