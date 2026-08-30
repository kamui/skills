---
name: code-review-address
description: Address every review comment on a pull request, make the warranted changes, and reply to each one. Use when review feedback on a pull request needs working through, including as the fix step of a review loop.
---

# Address code review

Evaluate every review comment, make the warranted changes, and reply to every one. A disagreement or a no-change decision still earns a reply.

Read [`references/review-protocol.md`](references/review-protocol.md) first: it defines the comment shape, the severity and status vocabularies, the disposition vocabulary, questions, reactions, thread state, the addressing summary, the round cap, and the `gh` verbs.

Invoking this skill authorizes the replies, resolutions, thread actions, pull-request title and description edits, round summary, and re-review request below. Fixes land as commits on the pull request's existing head branch, so its threads keep pointing at the code they describe — this skill opens no pull request of its own. Commits and pushes otherwise follow the repository's normal conventions.

## Process

### 1. Inventory the feedback

Read `docs/agents/issue-tracker.md` when present, then resolve the pull request, its head SHA and branch. Ask before editing code if it is ambiguous.

Fetch every piece of review feedback: inline comments, their thread resolution state, review bodies, and general pull-request comments that carry feedback. Skip automated status messages unless they ask for a change.

Build a ledger keyed by finding id, falling back to the comment id for anything without a trailer. Record author, location, thread, resolution state, severity, requested change, and whether this identity already replied. Only `[Optional]` findings are optional; anything unmarked is blocking, a human's comment included. A review body is its own ledger item when it carries feedback its inline comments do not.

### 2. Evaluate and address each item

Honor an implementation skill the user names. Otherwise invoke the model-invoked implementation skill whose description best matches the work; invoking this skill authorizes reaching it. Failing that, implement directly.

Check each item against the current code, the diff, the originating spec, and documented repository standards, then assign a disposition from the protocol. Do not accept feedback on authority — a reviewer, human or agent, can be wrong about this codebase. Where the concern is valid but the requested fix is not, implement the better alternative and say so.

A reviewer's `[Question]` is a ledger item like any other: answer it, mark it `answered`, and resolve the thread.

A finding you already declined and the reviewer has raised again is a dispute, not a repeat. Answer the reviewer's counter-argument rather than restating the original rationale, and where neither side moves, say plainly that it needs a human call — the protocol's round cap stops it there.

Severity sets the bar for a decline, not for whether an item earns a reply. An `[Optional]` finding can be declined on preference. Every unmarked one is blocking and holds the review at `Changes Requested` until the reviewer verdicts it `fixed`, `accepted`, or `obsolete`, so leaving one unaddressed keeps the pull request from merging — clear those first, and where one is genuinely wrong, decline it with a reason built to convince the reviewer.

Uncertainty resolves to `needs-info`, never to silent compliance or a silent decline — but ask only once the code, spec, standards, and history have failed to answer it. Put the question to a user in the session if there is one; otherwise leave it on the thread, where it outlives this run.

Apply every warranted change and run the relevant checks before replying. Re-read the resulting diff so each reply describes what the code now does, not what you set out to do.

### 3. Reply to every item

Every item earns a reply, pushing back included — a rejected finding is answered, not ignored. Post one reply per ledger item lacking one, in the protocol's shape, carrying the evidence its disposition requires. Queue each whole-change question's answer entry and reply trailer for the round's addressing summary rather than posting a separate general comment. Reply to a review body when it holds feedback its threads do not; leave the per-thread detail in the threads. Add a reaction where one says what a sentence would.

Resolve each thread as you finish it, not in a batch at the end: reply posted and change live, then resolve. That covers items implemented, already addressed, or answered, and threads gone outdated or irrelevant — the file deleted, the approach replaced. Leave `needs-info` and `blocked` threads open, and resolve nothing whose reply or code change is still missing. A `declined` thread stays open too: declining states a position, and the reviewer accepting it is what settles the disagreement. Where only the reviewer can resolve, report that instead of claiming it.

Re-addressing a pull request, reopen any thread resolved too early — the fix regressed, a later commit undid it, or the earlier reply claimed more than the code delivered — and say why in a new reply on it.

### 4. Close out the round

Reconcile the pull request's title and description against the resulting diff and originating spec. Edit either one when it no longer describes the change accurately or completely; preserve issue links and still-valid context, and describe the resulting behavior rather than the review chronology. An already-accurate field stays unchanged.

Resolving every thread leaves the pull request looking untouched, since the forge collapses what is resolved. Post one general pull-request comment in the protocol's shape: the head addressed, counts by disposition with each item linked to its thread where it has one, any whole-change answer entries and reply trailers, what still needs someone, and the checks run. Say plainly whether the round is finished or waiting — a round ending at `needs-info` or `blocked` is not done, and this is where the reviewer learns that without opening every thread.

One comment, however large the round. The per-item detail is already in the threads; a summary that restates it makes the reviewer read everything twice, and a comment per item is what the threads exist to avoid. Re-running against the same head updates that comment rather than adding a second.

Where the forge routes review requests, request a re-review from the identity whose review this round addressed, so it lands in their queue instead of waiting to be noticed. Authoring the pull request is no bar to that — GitHub refuses only a request whose target is the pull request's own author, which is certain where one identity both reviewed and addressed. Report a refusal rather than retrying it; the summary comment is the whole signal there.

### 5. Verify

Re-fetch the pull request metadata and review activity, then reconcile them against the final diff, spec, and ledger. Attempt each write once; on an ambiguous result read the target before a single retry. Finish only when the title and description reflect the resulting change and every item has a confirmed reply or a reported failure.

Report counts by disposition, blocking findings cleared and any still open, the code changes and checks run, title and description changes or confirmation that each stayed accurate, threads resolved, reopened, and left open, questions asked and answered, the round summary and whether a re-review was requested, and links to anything needing follow-up.
