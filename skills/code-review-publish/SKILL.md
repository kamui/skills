---
name: code-review-publish
description: "Legacy two-axis review: run the mattpocock/skills code-review skill on a pull request and publish its findings under review-protocol.md. Superseded by review-code-publish; use only when the caller explicitly asks for the legacy protocol."
disable-model-invocation: true
---

# Publish code review (legacy)

Review the change, then publish each finding to the pull request as its own comment, under one status saying whether the change is good to merge. The Code and Requirements axes stay separate throughout. The originating issue is the spec source only; publish nothing to it.

Read [`references/review-protocol.md`](references/review-protocol.md) first: it defines where a review goes, the comment shape, the severity and status vocabularies, the disposition and verdict vocabularies, questions, thread state, the round cap, and the `gh` verbs.

## Process

### 1. Resolve the targets

Read `docs/agents/issue-tracker.md` when present, then resolve the pull request, its head SHA, the originating issue serving as spec source, and the posting identity under `references/review-protocol.md`'s Posting identity rule. The tracker doc declares the reviewing app and client id, or a literal review-token command used as-is. For an app without a literal command, invoke `review-bot` when installed and take its returned login and command. Its absence or any `unavailable` result falls back to the authenticated user, records the reason in the report, and withholds gating; resolution never stops the run. A token refused at publication still stops the write. The fixed point defaults to the merge-base of the pull request with its base branch, which is what the pull request already means; take a different one only when the user supplies it. Ask before any external write if the pull request or issue is ambiguous.

Where the change has no pull request, stop and report that. A review publishes to a pull request that already exists; opening one is `implement-publish`'s job.

Fetch any earlier review from the posting identity, matching logins with a trailing `[bot]` ignored: its `commit_id`, its finding and question ids, the replies and thread state, and any general comments answering whole-change questions. An earlier review at a different head makes this run a re-review.

### 2. Run the review

Invoke the `code-review` skill from `mattpocock/skills` by name, `/code-review` or `$code-review`, and no other reviewer. Invoke the installed skill, not a built-in `/code-review` command of the same name. Where it is not installed, stop before publishing and report the install command: `npx skills@latest add mattpocock/skills --skill code-review`. Never substitute your own review for it.

It reviews `git diff <fixed-point>...HEAD`, so run it with `HEAD` at the pull request's head SHA. Where the current checkout is elsewhere or has uncommitted changes, run it from a temporary detached worktree at that SHA and remove the worktree afterward. Pass it the fixed point and the spec source from step 1, or state that there is none, so it reports "no spec available" rather than asking.

Map its axes before publication: **Standards** findings become **Code**, and **Spec** findings become **Requirements**. Classify both axes with the protocol's outcomes. With no spec, do not invent requirements: mark Requirements `Not applicable` unless the user or repository workflow requires a spec; where one is required, ask for it and mark the axis Waiting for information. If `code-review` fails or returns a report that cannot be classified, stop before publishing and report it.

Re-reviewing, keep the original fixed point as the comparison base and evaluate the full pull-request diff, using the earlier head only to locate intervening changes. Verdict every prior finding against the current code.

Where a verdict turns on something the code, spec, standards, and history do not answer, raise a question rather than guess a finding — a fabricated finding costs a round and an agent will dutifully "fix" it. Ask a user in the session if there is one; otherwise carry it as a `[Question]` per the protocol.

Normalize each finding to an axis, severity, title, evidence, requested change, and stable id. Severity is a judgment about the merge, not about the finding's interest, and blocking is the default the author will assume: label `[Suggestion]` only where they may act on it or close it unactioned, and leave everything the change should not merge without unmarked. A baseline smell `code-review` reports as a judgement call is `[Suggestion]`; a documented-standard breach or a Spec finding is blocking unless the author may close it unactioned. These are authoritative for publication; do not merge or rerank the axes.

### 3. Publish once

Publish through the forge's review system: one review whose body is the summary and whose line comments are the findings, submitted together. Every finding that names code goes on that code, not into the body — the body indexes, the line comments carry the detail. Index by `file:line` in that first call, then update the review body with the comment links once the call returns them.

Every completed review reaches one of the protocol's three statuses. Derive it only after the findings, questions, and axis outcomes are complete, using the protocol's ordered ladder.

Forge permission chooses the event, not the status: submit `REQUEST_CHANGES` or `APPROVE` only where the protocol's Where the status goes section authorizes this identity to gate a merge. Otherwise submit `COMMENT` and state the status on the summary's first line, with the per-axis outcome under it. Render a non-gating `Changes Requested` or `Approved` in its advisory form defined by the protocol.

Fall back to a single general pull-request comment only where the protocol's Where a review goes section allows; on your own pull request use its Self-review `gh` verb instead, whose `COMMENT` says nothing about the merge, so the written status line is what carries it there.

- A prior finding still present gets a reply on its existing thread, not a new comment.
- A finding at the round cap goes under `## Disputed` in the summary and gets no line comment.
- A question goes on the code it concerns, counts toward no axis, and is listed under `## Open questions` until answered. A whole-change question follows the protocol's body-level question path.

Then close out the threads this review settles: everything it verdicts `fixed`, `accepted`, or `obsolete`, plus its own findings it has withdrawn. An `accepted` verdict is how a decline you agree with gets closed — the addresser leaves it open for you. Reopen any thread whose fix regressed or whose reply claimed more than the code delivered, saying why in a new reply. Leave threads that still ask something of someone open.

Before writing, check for an existing review from this identity at this head, and compare its status as well as its head. Where the status is unchanged that review still stands: a forge that allows it takes an updated review body, and where the line comments are already published and unchangeable, report the review as already published rather than posting a second one. Where the status has moved at the same head — a decline accepted, a question answered, nothing recommitted — publish a new review carrying the new event and summary, without re-posting line comments that are already up. Dismiss the superseded review only where it carried a gating state the new event cannot replace; a `COMMENT` superseding another `COMMENT` needs no dismissal. A refused required dismissal leaves the stale gate in place: write the new status in the body and report the exact stale state as needing an authorized actor. Attempt each write once; on an ambiguous result read the target before a single retry, then report the failure rather than posting again.

Finish with the status, links to the review and its comments, counts by axis and severity, disputed findings, open questions, and anything that failed to publish.
