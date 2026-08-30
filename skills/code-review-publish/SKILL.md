---
name: code-review-publish
description: Review an issue-linked pull request and publish the findings to it as line comments and a review summary. Use when the caller wants a review posted to the pull request, not just reported back.
---

# Publish code review

Review the change, then publish each finding to the pull request as its own comment, under one status saying whether the change is good to merge. The Code and Requirements axes stay separate throughout. The originating issue is the spec source only; publish nothing to it.

Read [`references/review-protocol.md`](references/review-protocol.md) first: it defines where a review goes, the comment shape, the severity and status vocabularies, the disposition and verdict vocabularies, questions, reactions, thread state, the round cap, and the `gh` verbs.

## Process

### 1. Resolve the targets

Read `docs/agents/issue-tracker.md` when present, then resolve the pull request, its head SHA, the originating issue serving as spec source, and the posting identity. The fixed point defaults to the merge-base of the pull request with its base branch, which is what the pull request already means; take a different one only when the user supplies it. Ask before any external write if the pull request or issue is ambiguous.

Where the change has no pull request, stop and report that. A review publishes to a pull request that already exists; opening one is `implement-publish`'s job.

Fetch any earlier review from the posting identity: its `commit_id`, its finding comments and their ids, and the replies, thread ids, and resolution state on those threads. An earlier review at a different head makes this run a re-review.

### 2. Run the review

Honor a code-review skill the user names. Otherwise invoke the model-invoked review skill whose description best matches the change, passing it the fixed point, the spec source, and — re-reviewing — the earlier reviewed head. Failing that, review both axes directly: **Code** (correctness, documented repository standards, and code quality) and **Requirements** (missing, partial, incorrect, or unrequested behavior against the originating spec). With no spec, mark the Requirements axis unavailable rather than inventing requirements. If the selected reviewer calls these axes Standards and Spec, map them to Code and Requirements before publication.

Re-reviewing, keep the original fixed point as the comparison base and evaluate the full pull-request diff, using the earlier head only to locate intervening changes. Verdict every prior finding against the current code.

Where a verdict turns on something the code, spec, standards, and history do not answer, raise a question rather than guess a finding — a fabricated finding costs a round and an agent will dutifully "fix" it. Ask a user in the session if there is one; otherwise carry it as a `[Question]` per the protocol.

Normalize each finding to an axis, severity, title, evidence, requested change, and stable id. Severity is a judgment about the merge, not about the finding's interest, and blocking is the default the author will assume: label `[Optional]` only where they may act on it or close it unactioned, and leave everything the change should not merge without unmarked. Labelling every finding optional is a review that blocks nothing; labelling none is a review where a nit stops a merge. These are authoritative for publication; do not merge or rerank the axes.

### 3. Publish once

Publish through the forge's review system: one review whose body is the summary and whose line comments are the findings, submitted together. Every finding that names code goes on that code, not into the body — the body indexes, the line comments carry the detail. Index by `file:line` in that first call, then update the review body with the comment links once the call returns them.

Every review reaches one status — `Changes Requested`, `Approved`, or `Feedback` — derived from the unsettled blocking findings per the protocol. Submit it as the review event where the user or repository workflow authorizes this identity to gate a merge, and let the pull request carry it from there. Where no event can carry it — the forge has no review system, the pull request is your own, or approval is unauthorized — the summary's first line states the status in words, with the per-axis outcome under it.

Fall back to a single general pull-request comment holding the summary and results only when the forge has no review system or refuses the review. Authoring the pull request yourself is not such a refusal on GitHub, where `event: COMMENT` is accepted — but that `COMMENT` says nothing about the merge, so the written status line is what carries it there.

- A finding about a whole file attaches to that file, still inside the review; only a finding belonging to neither a line nor a file becomes a general pull-request comment.
- A prior finding still present gets a reply on its existing thread, not a new comment.
- A finding at the round cap goes under `## Disputed` in the summary and gets no line comment.
- A question goes on the code it concerns, counts toward no axis, and is listed under `## Open questions` until answered.
- React on a reply where a reaction says what a sentence would, per the protocol.

Then close out the threads this review settles: everything it verdicts `fixed`, `accepted`, or `obsolete`, plus its own findings it has withdrawn. An `accepted` verdict is how a decline you agree with gets closed — the addresser leaves it open for you. Reopen any thread whose fix regressed or whose reply claimed more than the code delivered, saying why in a new reply. Leave threads that still ask something of someone open.

Before writing, check for an existing review from this identity at this head, and compare its status as well as its head. Where the status is unchanged that review still stands: a forge that allows it takes an updated review body, and where the line comments are already published and unchangeable, report the review as already published rather than posting a second one. Where the status has moved at the same head — a decline accepted, a question answered, nothing recommitted — publish a new review carrying the new event and summary, without re-posting line comments that are already up, and dismiss the superseded review where the forge needs that to clear it. A refused dismissal means no event carries the new status: write it in the body and report the stale blocker as needing an authorized actor. Attempt each write once; on an ambiguous result read the target before a single retry, then report the failure rather than posting again.

Finish with the status, links to the review and its comments, counts by axis and severity, disputed findings, open questions, and anything that failed to publish.
