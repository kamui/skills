---
name: code-review-address
description: Address every review comment on a pull request, make the warranted changes, and reply to each one. Use when review feedback on a pull request needs working through, including as the fix step of a review loop.
---

# Address code review

Evaluate every review comment, make the warranted changes, and reply to every one. A disagreement or a no-change decision still earns a reply.

Read [`references/review-protocol.md`](references/review-protocol.md) first: it defines the comment shape, the severity and status vocabularies, the disposition vocabulary, questions, thread state, the addressing summary, the round cap, and the `gh` verbs.

Invoking this skill authorizes the replies, resolutions, thread actions, pull-request title and description edits, round summary, and re-review request below. Fixes land as commits on the pull request's existing head branch, so its threads keep pointing at the code they describe — this skill opens no pull request of its own. Commits and pushes otherwise follow the repository's normal conventions.

## Process

### 1. Inventory the feedback

Read `docs/agents/issue-tracker.md` when present, then resolve the pull request, its head SHA and branch. Ask before editing code if it is ambiguous.

Fetch every piece of review feedback: inline comments, their thread resolution state, review bodies, and general pull-request comments that carry feedback. Skip automated status messages unless they ask for a change.

Build a ledger keyed by finding id, falling back to the comment id for anything without a trailer. Record author, location, thread, resolution state, priority, action, requested change, and whether this identity already replied. Treat `[Suggestion]` and `[consider]` findings as optional, and `[must-fix]` findings as blocking; for current `code-review-publish` trailers, `action=consider blocking=false` is optional and `action=must-fix blocking=true` is blocking. Anything without one of those optional markers is blocking, a human's comment included. A review body is its own ledger item when it carries feedback its inline comments do not.

### 2. Evaluate and address each item

Honor an implementation skill the user names. Otherwise invoke the model-invoked implementation skill whose description best matches the work; invoking this skill authorizes reaching it. Failing that, implement directly.

Check each item against the current code, the diff, the originating spec, and documented repository standards, then assign a disposition from the protocol. Do not accept feedback on authority — a reviewer, human or agent, can be wrong about this codebase, and can be right in general without being right for this change. A **Change**: line names what the reviewer would do; whether it should be done here is yours to settle. Where the concern is valid but the requested fix is not, implement the better alternative and say so.

A reviewer's `[Question]` is a ledger item like any other: prepare its answer and mark it `answered` in the ledger. Post the answer and resolve the thread in step 4.

A finding you already declined and the reviewer has raised again is a dispute, not a repeat. Answer the reviewer's counter-argument rather than restating the original rationale, and where neither side moves, say plainly that it needs a human call — the protocol's round cap stops it there.

Action sets the bar for a decline, not for whether an item earns a reply. An optional `[Suggestion]` or `[consider]` finding is a proposal to weigh, and the protocol's default on one is to decline: implementing it takes an affirmative reason — a real defect underneath it, a documented standard behind it, or code this change already touches — and where none holds, decline it in a sentence and move on. Weigh it before the fix looks easy, because ease is not a reason. Every blocking or unmarked finding holds the review at `Changes Requested` until the reviewer verdicts it `fixed`, `accepted`, or `obsolete`, so leaving one unaddressed keeps the pull request from merging — clear those first, and where one is genuinely wrong, decline it with a reason built to convince the reviewer.

Uncertainty resolves to `needs-info`, never to silent compliance or a silent decline — but ask only once the code, spec, standards, and history have failed to answer it. Put the question to a user in the session if there is one; otherwise leave it on the thread, where it outlives this run.

Apply every warranted change, run the relevant checks, and commit the fixes locally. Prepare replies from the resulting diff. Defer pushes, disposition replies, and thread resolutions until step 3 is complete; questions needed to unblock the work may still be asked as above.

### 3. Review the addressing round

Spawn a separate reviewer with fresh context, without inheriting the implementation conversation. Use the host's context-isolation option, such as `fork_turns="none"` where available. Give it the repository path, the starting head SHA recorded in step 1 and final committed head SHA, the original feedback with stable ledger ids, the spec and user clarifications, and the locations of repository instructions and coding standards.

Keep the review read-only and focused on this addressing round. Have the reviewer independently inspect the original concerns, the diff between those heads, and relevant surrounding code for incomplete fixes and regressions. It returns its assessment with file and line references, supporting evidence, and any coverage gaps before receiving the proposed dispositions and replies. Then provide those drafts and the protocol so it can check every item's claims and decline rationale against the evidence. This check also applies to rounds with no code changes.

Evaluate its findings, fix warranted defects, rerun affected checks, and commit any further changes. Correct unsupported reply claims and dispositions. Have the reviewer verify the final committed head and revised drafts, keeping the implementation conversation excluded. Proceed when it has covered the round and no blocking defects introduced by the fixes or unsupported completion claims remain. Unresolved original feedback may still proceed as an accurate `needs-info`, `blocked`, or `declined` reply, with the thread left open under the protocol.

If an isolated reviewer is unavailable, a material coverage gap prevents verification, or a blocking defect in the fixes cannot be resolved, report the limitation to the caller and stop before pushing or publishing disposition replies. The internal review does not settle disputes on the original reviewer's behalf or replace the re-review request in step 5.

### 4. Reply to every item

If this round added commits, push them to the pull request's existing head branch. Confirm that the live head matches the reviewed head before posting disposition replies. If the head changes, reconcile the changes and repeat step 3 for the resulting head before proceeding.

Every item earns a reply, pushing back included — a rejected finding is answered, not ignored. Post one reply per ledger item lacking one, in the protocol's shape, carrying the evidence its disposition requires. Queue each whole-change question's answer entry and reply trailer for the round's addressing summary rather than posting a separate general comment. Reply to a review body when it holds feedback its threads do not; leave the per-thread detail in the threads.

Resolve each thread as you finish it, not in a batch at the end: reply posted and change live, then resolve. That covers items implemented, already addressed, or answered, and threads gone outdated or irrelevant — the file deleted, the approach replaced. Leave `needs-info` and `blocked` threads open, and resolve nothing whose reply or code change is still missing. A `declined` thread stays open too: declining states a position, and the reviewer accepting it is what settles the disagreement. Where only the reviewer can resolve, report that instead of claiming it.

Re-addressing a pull request, reopen any thread resolved too early — the fix regressed, a later commit undid it, or the earlier reply claimed more than the code delivered — and say why in a new reply on it.

### 5. Close out the round

Reconcile the pull request title and description as the protocol's Addressing summary section directs.

Resolving every thread leaves the pull request looking untouched, since the forge collapses what is resolved. Post one general pull-request comment in the protocol's shape: the head addressed, counts by disposition with each item linked to its thread where it has one, any whole-change answer entries and reply trailers, what still needs someone, and the checks run. A thread link stays the link for a ledger item; where the summary names a further file coordinate outside one, it is the protocol's immutable link at the addressed head, never a bare code span or a branch URL. Say plainly whether the round is finished or waiting — a round ending at `needs-info` or `blocked` is not done, and this is where the reviewer learns that without opening every thread.

One comment, however large the round. The per-item detail is already in the threads; a summary that restates it makes the reviewer read everything twice, and a comment per item is what the threads exist to avoid. Re-running against the same head updates that comment rather than adding a second.

Ask the identity whose review this round addressed to look again, so the round lands in their queue instead of waiting to be noticed. Where the forge routes review requests, make the ask a review request; authoring the pull request is no bar to that, since GitHub refuses only a request whose target is the pull request's own author. Where the forge will not route one — it routes none, or the target is the pull request's own author — the summary comment carries the ask as a line mentioning that identity, which notifies them just the same. Settle which form applies before writing the summary, by comparing that identity's login against the pull request's author, and never spend the summary explaining that the forge refused the request.

### 6. Verify

Re-fetch the pull request metadata and review activity, then reconcile them against the final diff, spec, and ledger. Attempt each write once; on an ambiguous result read the target before a single retry. Finish only when the title and description reflect the resulting change and every item has a confirmed reply or a reported failure.

Report counts by disposition, blocking findings cleared and any still open, the code changes and checks run, title and description changes or confirmation that each stayed accurate, threads resolved, reopened, and left open, questions asked and answered, the round summary and how the re-review was asked for — routed by the forge or mentioned in the summary — and links to anything needing follow-up. Every file or coordinate that report names is a link, not a bare code span: the forge's immutable blob link at the addressed full head SHA under the protocol's rule where one exists, and the host's supported workspace-file link only where no forge URL does. Links to anything needing follow-up remain mandatory.
