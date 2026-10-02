---
name: resolve-review
description: Address pull-request review feedback, make warranted changes, and reply to every item. Use when working through review comments or as the addressing step of a review loop.
compatibility: Requires git and Python 3.9+ on macOS or Linux
---

# Resolve code review

Bring every review item to an evidence-backed disposition and a confirmed reply, or report what prevents it. Evaluate the concern against the code and the intended change. A reviewer can identify a valid problem while proposing the wrong fix. Choose the investigation, implementation, and verification methods that fit the work; the obligations below define what must be established before publication.

Invocation authorizes commits and pushes to the pull request's existing head branch, replies, thread actions, necessary title and description edits, one addressing summary, and a re-review request. Follow repository conventions and write as the addresser's authenticated identity. Keep this work on the existing pull request. Merging, dismissing reviews, and acting as a reviewing app require separate authorization.

Read the repository's `docs/agents/issue-tracker.md` when present. Use [the addressing protocol](references/addressing-protocol.md) for feedback identities, the reply shape, disposition and verdict vocabulary, thread state, check evidence, summaries, and forge operations. Read the sections needed for the current action, including its input and failure contracts. Use each operation's documented invocation from the target checkout. Collection, check-run reads, and thread writes have launcher commands using absolute installed paths; their executable bodies need not be loaded into model context. The new-since-inventory command has its own invocation. A non-zero result requires the documented failure handling, never an assumption of success.

## 1. Inventory

Identify the target pull request before editing, and ask when it is ambiguous. Collect its metadata and all pages of reviews, inline comments, general comments, and thread states using the protocol's collection block. Record the initial head, branch, collection directory, and every feedback item's stable id or comment id. Include human feedback and review-body feedback that adds something beyond its threads. Skip status-only automation messages.

Keep a ledger of each item's concern, prior discussion, disposition, and reply under its stable identity so feedback is neither lost nor answered twice. Apply the protocol's blocking and optional classifications. Report incomplete collection coverage and address only what was fetched. Missing feedback cannot receive a disposition or count as addressed.

## 2. Address

Make the changes the evidence warrants and prepare one reply per item in the protocol's shape. Follow a user-named implementation skill; otherwise choose the implementation approach. Weigh optional suggestions under the optional-finding default in the protocol's Questions section. Answer questions, explain disagreements, and use `needs-info` or `blocked` when the work cannot be settled. Ask a focused question after available evidence fails to answer it, through the session or the pull request as the caller permits.

A finding declined earlier that the original reviewer verdicts `not-fixed` is disputed. Answer the reviewer's counter-argument and say it needs a human decision under the protocol's two-round cap.

Commit the fixes and verify under the protocol's Check evidence section. Select checks for the changed behavior and its dependencies. Reuse valid evidence rather than repeating a check; record its command or CI identity, head, input state, result, and coverage. Apply the protocol's Invalidating rule after further changes. Earlier-head evidence remains attributed to that head and cannot meet an explicit check obligation at a different head.

Hold pushes, disposition replies, and thread resolutions until the independent review below completes. Questions needed to unblock the work may be asked earlier.

## 3. Review before publication

Use an isolated, read-only reviewer that receives the original concerns, initial and final committed heads, relevant spec and repository instructions, and check evidence, without the implementation conversation. Respect a caller-specified reviewer tier and repository model-selection rules.

The reviewer records its own evidence-backed assessment before seeing the proposed replies and dispositions, then checks their claims. This ordering also applies when no code changed. Retain the assessment and any coverage gaps. Approval covers the head and drafts actually inspected.

Wait for the completed review using a supported host operation. If none exists, stop before dispatch with `review-wait-unavailable`, naming the missing operation and any pending work. A pending reviewer or a partial assessment does not satisfy this gate. Fresh reviewers may replace completed phases only; pending work gets no competing replacement, and failed or partial phases stop publication. If isolation is unavailable, material coverage is missing, or a blocking defect introduced by the fixes remains, stop before pushing or publishing dispositions and report the reason.

Evaluate the first assessment's findings and commit warranted fixes. Correct unsupported claims and obtain review coverage of the final head and drafts. Choose continued, fresh, delta, or full assessment according to the changes and available host operations; preserve the assessment-before-drafts ordering and prior coverage. Starting with the first re-verification, further commits in this round are for blocking defects introduced by the fixes or unsupported reply claims. Report accepted optional follow-ups instead of extending the round.

This review does not settle a disagreement on the original reviewer's behalf or replace the re-review request.

## 4. Publish replies

Push any commits to the existing head branch. Confirm the live head equals the reviewed head before publishing dispositions. If it moved, reconcile the change and obtain review coverage of the resulting head first.

Publish the reviewed thread replies and actions through the protocol's `writes.jsonl` write loop. Preserve its exact reply bodies, confirmed-write reconciliation, and retry limits. Resolve only after the required replies and work are confirmed; leave `declined`, `needs-info`, and `blocked` items open. Reopen a prematurely resolved thread and explain why. Follow the protocol's routes for feedback without a thread and whole-change questions. Report every unresolved write and any permission that prevented a thread action.

## 5. Close out

Reconcile the title and description with the final change, preserving issue links and valid context. Post or update one addressing summary in the protocol's shape, including the `<!-- addressed head=<full SHA> -->` trailer at the pushed head, which equals the local head. Update the existing same-head summary on a rerun. Index the items, include each check with the head and input state it establishes, and say what still needs someone. Use immutable links for named file coordinates.

Request re-review from the identity whose feedback was addressed. Use the protocol's routing rules for a user, the pull request's own author, or an app reviewer. An app reviewer receives neither a request nor a mention.

## 6. Reconcile and report

Collect review activity again and compare it with the inventory using the protocol's New since inventory command, excluding this round's confirmed write ids and their generated empty reviews. Report new feedback as unaddressed and update the summary. An incomplete read prevents a claim of complete reconciliation. For writes outside the thread loop, reconcile an ambiguous result against the target before at most one retry.

Finish with the addressed head, summary link, disposition counts, changes and checks, independent review outcome, thread actions, re-review route, and links to remaining work or failures. Include the supported host operation used to await review. A round waiting on information or blocked work is waiting, not finished. Report cost measurements when requested and available, distinguishing measured runs from reused evidence and unavailable metrics.
