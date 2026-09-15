---
name: resolve-review
description: Address every review comment on a pull request, make the warranted changes, and reply to each one. Use when review feedback on a pull request needs working through, including as the fix step of a review loop.
---

# Resolve code review

Evaluate every review comment, make the warranted changes, and reply to every one. A disagreement or a no-change decision still earns a reply.

Read [`references/addressing-protocol.md`](references/addressing-protocol.md) first: it defines how to read a finding, the reply shape and disposition vocabulary, questions, thread state, the round cap, the addressing summary, and the `gh` verbs. When the repository's `docs/agents/issue-tracker.md` is known to be present, read it with the protocol in one tool invocation when the complete output fits the host's output limit; otherwise use bounded or separate reads here and recover every missing portion, and a host without multi-read support reads them consecutively.

Invoking this skill authorizes the replies, resolutions, thread actions, pull-request title and description edits, round summary, and re-review request below. Fixes land as commits on the pull request's existing head branch, so its threads keep pointing at the code they describe — this skill opens no pull request of its own. Commits and pushes otherwise follow the repository's normal conventions.

## Process

### 1. Inventory the feedback

Read `docs/agents/issue-tracker.md` when present, unless the opening read already loaded it, then resolve the pull request number. Ask before editing code if it is ambiguous.

Run the protocol's collection block once. That one invocation saves the pull request metadata, with its head SHA and branch, and every piece of review feedback: inline comments, their thread resolution state, review bodies, and general pull-request comments that carry feedback. Record the block's directory for step 6. When a collection comes back incomplete, report the coverage gap. Address only the feedback the block did fetch, and give no disposition that depends on a missing item. Skip automated status messages unless they ask for a change.

Build a ledger keyed by finding id, falling back to the comment id for anything without a trailer. Record author, location, thread, resolution state, priority, action, requested change, and whether this identity already replied. Classify each item blocking or optional under the protocol's Reading a finding section. A review body is its own ledger item when it carries feedback its inline comments do not.

### 2. Evaluate and address each item

Honor an implementation skill the user names. Otherwise invoke the model-invoked implementation skill whose description best matches the work; invoking this skill authorizes reaching it. Failing that, implement directly.

Check each item against the current code, the diff, the originating spec, and documented repository standards, then assign a disposition from the protocol. Do not accept feedback on authority — a reviewer, human or agent, can be wrong about this codebase, and can be right in general without being right for this change. Where the concern is valid but the requested fix is not, implement the better alternative and say so.

A reviewer's `[Question]` is a ledger item like any other: prepare its answer and mark it `answered` in the ledger. Post the answer and resolve the thread in step 4.

A finding you already declined and the reviewer has raised again is a dispute, not a repeat. Answer the reviewer's counter-argument rather than restating the original rationale, and where neither side moves, say plainly that it needs a human call — the protocol's round cap stops it there.

Action sets the bar for a decline, not for whether an item earns a reply. An optional finding is a proposal to weigh under the protocol's default: decline it in a sentence unless one of the protocol's affirmative reasons holds, and weigh it before the fix looks easy, because ease is not a reason. Every blocking finding holds the review at `Changes Requested` until the reviewer settles it with `fixed`, `accepted`, or `obsolete`, so leaving one unaddressed keeps the pull request from merging — clear those first, and where one is genuinely wrong, decline it with a reason built to convince the reviewer.

Uncertainty resolves to `needs-info`, never to silent compliance or a silent decline — but ask only once the code, spec, standards, and history have failed to answer it. Put the question to a user in the session if there is one; otherwise leave it on the thread, where it outlives this run.

Apply every warranted change and commit the fixes locally. Verify them under the protocol's Check evidence section: select the documented checks the changes reach, run each shared check once for the changes that share it, and reuse evidence that still establishes the committed head rather than running it again. Prepare replies from the resulting diff. Defer pushes, disposition replies, and thread resolutions until step 3 is complete; questions needed to unblock the work may still be asked as above.

### 3. Review the addressing round

Spawn a separate reviewer with fresh context, without inheriting the implementation conversation. Use the host's context-isolation option, such as `fork_turns="none"` where available. Give it the repository path, the starting head SHA recorded in step 1 and final committed head SHA, the original feedback with stable ledger ids, the spec and user clarifications, and the locations of repository instructions and coding standards.

Run every reviewer phase in this step on an **awaited** route: the independent assessment, the check of drafted dispositions and replies, and each re-verification after further fixes or revised drafts. An awaited route's tool call delivers the completed result while this pass stays active: a foreground dispatch (`run_in_background: false`, or the host's equivalent), a blocking continuation, a supported join, or a runtime-managed suspension that resumes this pass without a final hand-back. An acknowledgment, an agent id, a pending notice, or a delay is not completion, and ending the turn leaves the result unreachable. Choose each phase's route before sending it, from the host's tools or established behavior, without changing global runtime settings. Continue the same reviewer when its continuation is awaited. Otherwise, once the previous phase has completed, run the next phase as one **fresh continuation**: a new isolated reviewer on an awaited route that replaces that phase, never a second reviewer beside a pending one, a retry of a failed phase, or a way past a partial result. When no awaited route exists, stop with `review-wait-unavailable` before dispatching, naming the phase, the missing operation, and any pending work. A hand-back with a phase pending is a failed pass, not a report.

Keep the review read-only and focused on this addressing round. Have the reviewer independently inspect the original concerns, the diff between those heads, and relevant surrounding code for incomplete fixes and regressions. It returns its assessment with file and line references, supporting evidence, and any coverage gaps before receiving the proposed dispositions and replies. Then provide those drafts and the protocol so it can check every item's claims and decline rationale against the evidence. This check also applies to rounds with no code changes.

Retain each completed assessment with its evidence, and what a fresh continuation needs: the stable ledger ids, original concerns, starting and final heads, authoritative spec updates, coverage gaps, and the protocol, never the implementation conversation. Missing or mismatched retained state is a coverage gap. A fresh continuation first records its own evidence-backed assessment of the head it checks, then reads the drafts: store them as a separate file named with that read order, never inline in its initial brief. An approval covers only the head and draft set it checked.

Evaluate its findings, fix warranted defects, and commit any further changes. List the earlier evidence those changes invalidate and rerun the checks the protocol's Invalidating rule requires; this reviewer does not stand in for them. Correct unsupported reply claims and dispositions. Have the reviewer verify the final committed head and revised drafts, keeping the implementation conversation excluded. Proceed when it has covered the round and no blocking defects introduced by the fixes or unsupported completion claims remain. Unresolved original feedback may still proceed as an accurate `needs-info`, `blocked`, or `declined` reply, with the thread left open under the protocol.

If an isolated reviewer is unavailable, a material coverage gap prevents verification, or a blocking defect in the fixes cannot be resolved, report the limitation to the caller and stop before pushing or publishing disposition replies. The internal review does not settle disputes on the original reviewer's behalf or replace the re-review request in step 5.

### 4. Reply to every item

If this round added commits, push them to the pull request's existing head branch. Confirm that the live head matches the reviewed head before posting disposition replies. If the head changes, reconcile the changes and repeat step 3 for the resulting head before proceeding.

Every item earns a reply, pushing back included — a rejected finding is answered, not ignored. Draft one reply per ledger item lacking one, in the protocol's shape, carrying the evidence its disposition requires. Queue each whole-change question's answer entry and reply trailer for the round's addressing summary rather than posting a separate general comment. Reply to a review body when it holds feedback its threads do not; leave the per-thread detail in the threads.

Resolve each thread together with its confirmed reply, under the protocol's Thread state section. That covers items implemented, already addressed, or answered, and threads gone outdated or irrelevant — the file deleted, the approach replaced. Leave `needs-info` and `blocked` threads open, and resolve nothing whose reply or code change is still missing. A `declined` thread stays open too, under that section. Where only the reviewer can resolve, report that instead of claiming it.

Re-addressing a pull request, reopen any thread resolved too early — the fix regressed, a later commit undid it, or the earlier reply claimed more than the code delivered — and say why in a new reply on it.

Post the thread replies, resolutions, and reopenings by writing `writes.jsonl` from the step-3-checked drafts and running the protocol's thread write loop once. Reconcile and retry only through the loop's rerun rules, and report every `unresolved` line it prints.

### 5. Close out the round

Reconcile the pull request title and description as the protocol's Addressing summary section directs.

Resolving every thread leaves the pull request looking untouched, since the forge collapses what is resolved. Post one general pull-request comment in the protocol's shape: the head addressed, counts by disposition with each item linked to its thread where it has one, any whole-change answer entries and reply trailers, what still needs someone, and each check with the head and input state it establishes and any remaining verification gap. A thread link stays the link for a ledger item; where the summary names a further file coordinate outside one, it is the protocol's immutable link at the addressed head, never a bare code span or a branch URL. Say plainly whether the round is finished or waiting — a round ending at `needs-info` or `blocked` is not done, and this is where the reviewer learns that without opening every thread.

One comment, however large the round. The per-item detail is already in the threads; a summary that restates it makes the reviewer read everything twice, and a comment per item is what the threads exist to avoid.

Ask the identity whose review this round addressed to look again, in the form the protocol's Addressing summary section selects: a review request where the forge routes one, otherwise a mention line in the summary comment. Settle which form applies before writing the summary.

### 6. Verify

Re-fetch the pull request metadata and review activity by running the same collection block again, under the same completeness rule as step 1. Reconcile them against the final diff, spec, and ledger. List the ids that are new since step 1 with the protocol's New since inventory command, and pass it the ids of the replies and summary this round wrote, taking reply ids from the `created_id` of confirmed rows in `write-results.jsonl`. Those writes, and the review GitHub creates around each reply, are left out. Each remaining new item is unaddressed: name it in the round summary, updating that comment, and do not absorb it silently. If either run was incomplete, report incomplete coverage rather than a finished reconciliation. Attempt each write once; on an ambiguous result read the target before a single retry. Finish only when the title and description reflect the resulting change and every item has a confirmed reply or a reported failure.

Report counts by disposition, blocking findings cleared and any still open, the code changes and the checks with the heads they establish, the internal review outcome and any remaining optional findings, any title or description changes, threads resolved, reopened, and left open, questions asked and answered, the round summary and how the re-review was asked for — routed by the forge or mentioned in the summary — and links to anything needing follow-up. Every file or coordinate that report names is a link, not a bare code span: the forge's immutable blob link at the addressed full head SHA under the protocol's rule where one exists, and the host's supported workspace-file link only where no forge URL does. Links to anything needing follow-up remain mandatory.
