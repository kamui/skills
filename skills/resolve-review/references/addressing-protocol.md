# Addressing protocol

The addresser's side of the review protocol: how to read a finding, the reply shape and its dispositions, questions, thread state, the round cap, the addressing summary, and the `gh` verbs a round needs. The reviewer's side ships with the reviewing skill.

## Reading a finding

A reviewer's finding is one comment: a bold title line, evidence with `file:line`, a **Change**: line naming the concrete edit, and an HTML-comment trailer that is invisible in the rendered view and present in the raw body via `gh api`. The trailer's `id` is the finding's stable identity across rounds; key the ledger by it, and fall back to the comment id where there is no trailer.

- `review-code-publish` labels findings `[P0]` through `[P3]` and then `[must-fix]` or `[consider]`; its trailers carry matching `priority`, `action`, and `blocking` fields. `[must-fix]` or `action=must-fix blocking=true` is blocking; `[consider]` or `action=consider blocking=false` is optional. A visible action/trailer mismatch is malformed feedback to clarify rather than silently choosing one.
- A legacy `code-review-publish` finding opens with an axis tag, `[Code]` or `[Requirements]`, and is blocking unless its title carries `[Suggestion]` and its trailer `severity=optional`.
- Anything without one of those optional markers is blocking, a human's comment included.

A **Change**: line names what the reviewer would do; whether it should be done here is the addresser's to settle.

## Reply comments

`resolve-review` replies once per item:

```markdown
**Implemented** in `9f1e0aa` — extracted `assertOrderShape`; both call sites use it. `pnpm test` green.

<!-- reply to=code/order-ts/duplicated-validation disposition=implemented head=9f1e0aa -->
```

The bold word is the disposition:

| Disposition | Means | The reply carries |
| --- | --- | --- |
| `implemented` | change made | what changed, the check run, the commit |
| `already-addressed` | the code already satisfied it | where |
| `answered` | a question resolved, no code change | the answer |
| `declined` | correct to leave as-is, or not this change's job | the reason: technical for a blocking finding, scope or preference for an optional one |
| `needs-info` | cannot act without an answer | the focused question |
| `blocked` | warranted, not yet possible | the blocker and the next step |

## Questions

Ask rather than guess, and ask only after the legwork fails — the answer is not in the code, the spec, the standards, or the history. A question that reading would have answered costs a round and buys nothing. Where a user is in the session, ask them directly; otherwise the pull request is the channel, because the question has to outlive the session that raised it.

An addresser asks by replying `needs-info` on the thread it is stuck on, and leaves it open. This disposition belongs to an existing finding and never determines the review status directly: the finding keeps its original severity, so a blocking one still means `Changes Requested` while an optional one does not.

A reviewer's line question is tagged `[Question]` on the code it concerns. Answer it with `answered` and resolve its thread. A reviewer's whole-change question, such as a required missing spec, sits under `## Open questions` in the review body with a `question id=... head=...` trailer and has no thread. Answer it inside the round's single addressing summary: one concise `answered` entry for the question and its `<!-- reply to=<question id> disposition=answered head=<head> -->` trailer. Multiple whole-change answers share that summary but keep one entry and trailer apiece. The next review correlates the reply trailer and omits the question from `## Open questions`. A question that turns out to expose a defect becomes a finding in the next review, with its own id.

Severity tells an addresser what a decline costs. An optional finding can be declined on preference without causing `Changes Requested`. Everything else is blocking and holds the review at `Changes Requested` until the reviewer settles it — so declining there needs a reason built to convince the reviewer, not merely to record a position.

An optional finding is a proposal, and the addresser's job on one is to decide it rather than to perform it. Implementing takes an affirmative reason — a real defect underneath it, a documented standard behind it, or code this change already touches — and absent one the finding is declined. Implementing on reflex is how a reviewer's passing preference becomes unrequested change in someone else's pull request, widening the diff every later reader has to verify and burying the work the pull request exists for. Declining is an ordinary outcome there, not a failure to engage, and it costs a sentence: an optional decline has to be honest, where a blocking one has to be persuasive.

## Thread state

A thread stays open only while it still asks something of someone. Both sides close threads, and either may reopen one.

Resolve a thread when:

- the reviewer verdicts it `fixed`, `accepted`, or `obsolete`;
- its work is done and needs no reviewer verdict — a question answered, a finding already addressed by code the reviewer can see;
- it went outdated or stopped being relevant — the file was deleted, the approach was replaced, the finding was withdrawn.

A `declined` reply does not resolve its own thread. Declining states a position; the reviewer accepting it is what settles the disagreement, and closing early would hide a live dispute from the round cap.

Resolve each thread as you finish it — reply posted, change live — rather than batching resolutions at the end. Threads sitting at `needs-info` or `blocked` stay open. A stale thread left from an earlier round is the reviewer's to close, not something the addresser inherits.

Reopen a thread rather than file a fresh finding, which would strand the original discussion: the fix regressed, a later commit undid it, or a reply claimed more than the code delivered. Post a new reply on the thread saying why it reopened.

Resolve nothing whose reply is still missing. Where only the other party can resolve a thread, report that rather than claiming it.

## Verdicts and the round cap

Re-reviewing, the reviewer verdicts each prior finding against the code, not against its reply: `fixed` (the code now satisfies it), `accepted` (a `declined` reply whose reasoning the reviewer accepts), and `obsolete` (the code it described is gone) resolve the thread; `not-fixed` leaves it open. A reply's word is evidence of intent, not of outcome.

A finding `declined` once and then verdicted `not-fixed` is **disputed**. The reviewer stops re-posting it and lists it under `## Disputed` for a human to settle. Two rounds is the cap on any one finding, and that cap is what stops an agent loop re-litigating a point forever. A disputed blocking finding still holds the status at `Changes Requested`; the cap does not turn a blocker into a merge.

## Addressing summary

Before closing the round, reconcile the pull request title and description against the resulting diff and originating spec. Edit either field when it no longer describes the change accurately or completely; preserve issue links and still-valid context, and describe the resulting behavior rather than the review chronology. An already-accurate field stays unchanged. In the summary comment, mention only fields actually edited during the round; omit unchanged fields even when the other field changed.

Resolving every thread leaves a pull request looking untouched. The forge collapses resolved threads, so a round that answered everything and a round that did nothing render the same, and the reviewer has to expand each one to find out which. `resolve-review` closes a round with one general pull-request comment:

```markdown
**Addressed** at `5844a3c` — 2 implemented, 1 answered, 1 declined.

- `implemented` — [verdict vocabulary](url), [dismissal authority](url)
- `answered` — `question/retry-order`: retries preserve request order
- `declined` — [axis tag rename](url), open for your verdict

`pnpm test` green. Every other thread resolved.

<!-- reply to=question/retry-order disposition=answered head=5844a3c -->
<!-- addressed head=5844a3c -->
```

- the head it addressed at, and the commits carrying the changes;
- counts by disposition, each item linked to its thread;
- a file coordinate the summary names outside a linked thread item rendered as an immutable link at the addressed full head SHA — `https://<host>/<owner>/<repo>/blob/<full sha>/<path>?plain=1#L<line>`, `#L<start>-L<end>` for a range, neither the query nor the fragment for a whole file — with the code-formatted coordinate as its text, never a branch URL or a bare code span;
- what still needs someone: `declined` awaiting a verdict, `needs-info` awaiting an answer, `blocked` items and their blocker;
- the checks run;
- where the forge will not route a re-review request, one line asking for one by mentioning the reviewing identity;
- whether the round is finished or waiting — the sentence the reviewer would otherwise open every thread to infer.

One comment per round, never one per item. Whole-change question answers are the only per-item detail in this comment because those questions have no threads: give each a concise answer entry and its own reply trailer in the summary. Every other item's detail stays in its thread, and the summary only indexes it. Re-running at the same head updates that comment rather than posting a second.

Every round ends by asking the identity whose review it addressed to look again. That is the counterpart to the reviewer's status — the reviewer says where the change stands, the addresser says it is ready to be looked at again — and it belongs in their queue rather than waiting to be noticed.

Where the forge routes review requests, make the ask a review request. A re-request does not clear an earlier `REQUEST_CHANGES`; only a later review from that identity, or a dismissal, does.

Where the forge will not route one — it has no review requests at all, or it refuses this one because the identity to ask is the pull request's own author — the summary carries the ask instead, as a line mentioning that identity: `Re-requesting review from @<login>.` The mention notifies them, which is what the request was for. Settle which form applies before writing the summary, by comparing that identity's login against the pull request's author and nothing else, and never report the forge's refusal on the pull request: the ask is the signal a reader wants, and a paragraph about a rejected API call is noise around it.

## Humans in the loop

Trailers speed up the agent path; they never gate it. A finding or reply written by a human carries no trailer — read it as prose, infer its disposition, and reply to it exactly as to any other. Never skip an item for lacking a trailer, and never address a human reviewer by writing a trailer on their behalf.

## GitHub verbs

If this repo's `docs/agents/issue-tracker.md` names a forge other than GitHub, follow that file instead.

`gh api` substitutes `{owner}` and `{repo}` from the clone, so the paths below are copy-pasteable as written.

**Posting identity**: `gh api user --jq .login`. Compare with `gh pr view <n> --json author` to detect a self-review.

**Resolve the pull request**: `gh pr view <n> --json number,url,author,headRefName,baseRefName,headRefOid,state,body`. `headRefOid` is the head SHA to record as addressed.

### Reading review activity

- **Reviews**: `gh api repos/{owner}/{repo}/pulls/<n>/reviews --jq '.[] | {id, user: .user.login, state, commit_id, body}'`. `commit_id` is the head that review covered.
- **Inline comments**: `gh api repos/{owner}/{repo}/pulls/<n>/comments`. Fields that matter: `id`, `in_reply_to_id`, `path`, `original_line`, `line`, `body`. Cite `original_line` for location — `line` becomes `null` once a later push outdates the comment.
- **General pull-request comments**: `gh api repos/{owner}/{repo}/issues/<n>/comments`. A pull request is an issue, so a summary posted as a general comment lives under `issues`, not `pulls`.
- **One inline comment**: `gh api repos/{owner}/{repo}/pulls/comments/<comment_id>` — no `<n>` in that path.
- **Thread resolution state**: GraphQL only; REST does not expose whether a thread is resolved.

  ```sh
  gh api graphql -f query='
    query($owner:String!,$repo:String!,$pr:Int!){
      repository(owner:$owner,name:$repo){ pullRequest(number:$pr){
        reviewThreads(first:100){ nodes{
          id isResolved isOutdated path line
          comments(first:1){ nodes{ databaseId } } } } } } }
  ' -f owner=<owner> -f repo=<repo> -F pr=<n>
  ```

  `id` is the thread node id needed to resolve it. `comments.nodes[0].databaseId` maps the thread back to its REST comment id.

### Writing review activity

- **Reply to an inline comment**: `gh api --method POST repos/{owner}/{repo}/pulls/<n>/comments/<comment_id>/replies -f body='...'`, addressing the thread's first comment id.
- **General comment**: `gh pr comment <n> --body-file -` with a heredoc. This is where an addressing summary goes; find an earlier one to update by grepping `issues/<n>/comments` for its `addressed head=` trailer.
- **Request a re-review**: `gh pr edit <n> --add-reviewer <login>`, or `gh api --method POST repos/{owner}/{repo}/pulls/<n>/requested_reviewers -f 'reviewers[]=<login>'`. Take `<login>` from the review being addressed. Authoring the pull request is no bar to requesting one: GitHub returns 422 (`Review cannot be requested from pull request author`) only when `<login>` is the pull request's own author, or the account cannot review it. Check `<login>` against the author from `gh pr view <n> --json author` before calling, and decide on that comparison alone: where they match, skip the call GitHub is certain to refuse and put `Re-requesting review from @<login>.` in the summary comment instead. Who addressed the round says nothing about who authored the pull request — a maintainer reviewing and later addressing a contributor's pull request is not its author, and that request routes. Where an unforeseen 422 lands after that comment is posted, edit the comment to carry the mention rather than retrying the request or reporting the refusal.
- **Edit a comment**: `gh api --method PATCH repos/{owner}/{repo}/pulls/comments/<id> -f body='...'`; for a general comment, `repos/{owner}/{repo}/issues/comments/<id>`.
- **Resolve or reopen a thread**: GraphQL only, no REST equivalent.

  ```sh
  gh api graphql -f query='mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -f id=<thread node id>
  gh api graphql -f query='mutation($id:ID!){ unresolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -f id=<thread node id>
  ```
