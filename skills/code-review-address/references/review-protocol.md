# Review protocol

Mirrored verbatim in `code-review-publish` and `code-review-address`; edit both together.

## Where a review goes

Use the forge's own review system whenever it has one. A review is a single reviewable unit — a body plus the line comments attached to it — and it reads as a review to a person, rather than as loose chatter scattered on the pull request.

Fall back to one general pull-request comment carrying the summary and results only when the forge has no review system, or it refuses the review. On GitHub, `event: COMMENT` is accepted even when the reviewer authored the pull request; only `APPROVE` and `REQUEST_CHANGES` are refused there, so authoring the pull request is not itself a reason to fall back.

Inside a review, every finding that names code is a line comment on that code. The body carries the summary and the index and nothing that belongs on a line. A finding that names a file rather than a line attaches to that file, still inside the review; only a finding belonging to neither a line nor a file becomes a general comment.

The pull request under review is a fixed target. Neither skill opens, retargets, or closes one — reviewing a change and fixing it both happen on the pull request that already exists, so its threads keep pointing at the code they describe. Opening a pull request is `implement-publish`'s job.

## Finding comments

`code-review-publish` posts one comment per finding:

```markdown
**[Code] Duplicated validation in `parseOrder`**

`src/order.ts:42` repeats the shape in `src/cart.ts:18`. `CODING_STANDARDS.md` §3: one home per rule.

**Change**: extract `assertOrderShape` and call it from both.

<!-- finding id=code/order-ts/duplicated-validation head=a1b2c3d -->
```

- Bold title line, axis tag first: `[Code]` or `[Requirements]`.
- `[Code]` covers correctness, documented repository standards, and implementation quality.
- `[Requirements]` covers missing, partial, incorrect, or unrequested behavior against the originating spec.
- A finding is blocking unless it says otherwise. Unmarked means the change should not merge until this is settled, and that is what the author reads it as.
- Evidence: the `file:line` and concrete behavior; cite the documented rule or originating requirement when one applies.
- A **Change**: line naming the concrete edit.
- Six lines or fewer above the trailer. Whoever acts on it, human or agent, acts from this comment alone.
- The trailer is an HTML comment: invisible in the rendered view, present in the raw body via `gh api`.

`[Optional]` is the one severity marker, for a finding worth saying and not worth blocking on — a nice-to-have, a preference, or food for thought the author may close unactioned. It goes after the axis tag and rides the trailer:

```markdown
**[Code] [Optional] `formatDate` could read the locale from context**

...

<!-- finding id=code/format-date/locale-from-context severity=optional head=a1b2c3d -->
```

Mark it where it belongs and nowhere else. Every finding labelled optional is a review that blocks nothing; none labelled is a review where a nit stops a merge.

The `id` slugs the axis (`code` or `requirements`), file, and finding title — never a line number, since lines drift between rounds and the id has to survive that. One finding against the same code keeps one id across every round. Prior findings with legacy `standards` or `spec` ids retain those ids on re-review; renaming one would break its thread correlation.

## Reply comments

`code-review-address` replies once per item:

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
| `declined` | correct to leave as-is | the technical reason |
| `needs-info` | cannot act without an answer | the focused question |
| `blocked` | warranted, not yet possible | the blocker and the next step |

## Questions

Either skill may ask rather than guess. A reviewer that cannot tell whether code is correct without knowing something, and an addresser that cannot act on a finding without an answer, both put the question on the pull request instead of inventing a position. State exactly what information is needed and who should provide it.

Ask only after the legwork fails — the answer is not in the code, the spec, the standards, or the history. A question that reading would have answered costs a round and buys nothing.

Where a user is in the session, ask them directly; it is faster and they may unblock it at once. Otherwise the pull request is the channel, because the question has to outlive the session that raised it. A reviewer's question is a line comment tagged `[Question]` on the code it concerns:

```markdown
**[Question] Is the 30s timeout here deliberate?**

`src/fetch.ts:88` sets 30s where every other caller uses 5s. The spec is silent and the history shows no rationale. If it is deliberate, a comment saying why would stop the next reader changing it.

<!-- question id=question/fetch-ts/timeout-30s head=a1b2c3d -->
```

An addresser asks by replying `needs-info` on the thread it is stuck on, and leaves it open. This disposition belongs to an existing finding and never determines the review status directly: the finding keeps its original severity, so a blocking one still means `Changes Requested` while an optional one does not. It is distinct from the reviewer's `Needs Information` status.

A reviewer's whole-change question, such as a required missing spec, belongs under `## Open questions` in the review body rather than on an arbitrary line. Give it the same `question id=... head=...` trailer as a line question. It has no thread to resolve. The addresser answers it inside the round's single addressing summary: add one concise `answered` entry for the question and its `<!-- reply to=<question id> disposition=answered head=<head> -->` trailer. Multiple whole-change answers share that summary but keep one entry and trailer apiece. The next review correlates the reply trailer, treats the question as answered, and omits it from `## Open questions`.

Severity tells an addresser what a decline costs. An optional finding can be declined on preference without causing `Changes Requested`. Everything else is blocking, including a human's comment carrying no label at all, and holds the review at `Changes Requested` until the reviewer settles it — so declining there needs a reason built to convince the reviewer, not merely to record a position.

A question is not a finding. It carries no axis, counts toward no axis total, and never counts toward the round cap — an unanswered question is not a disputed point, just an open one. Re-reviews link to the same open question rather than posting it again. It keeps the review at `Needs Information` until someone answers it, the reviewer withdraws it as irrelevant, or the reviewer determines its answer cannot change the verdict; it never ages into approval. An unattended loop stops and reports what it is waiting for. Answer a line question with `answered` and resolve its thread; answer a whole-change question through the general-comment path above. A question that turns out to expose a defect becomes a finding in the next review, with its own id.

Questions still open at the end of a run go under `## Open questions` in the summary, so whoever picks the pull request up next sees what is waiting on them.

## Reactions

Where the forge supports them, a reaction is a cheap signal riding on top of a reply, never standing in for one. Either side may use them — a reviewer on a reply, an addresser on a finding — to say what a reply would otherwise spend a sentence on:

| Reaction | Says |
| --- | --- |
| `+1` | agreed, acting on it |
| `eyes` | seen, work in progress |
| `-1` | disagreed; the reply carries the reason |
| `confused` | unclear; the reply asks the question |
| `hooray`, `heart`, `rocket` | a genuinely good catch, worth saying so |

One reaction per comment is plenty. A reaction never closes an item: every comment still earns its reply.

## Thread state

A thread stays open only while it still asks something of someone. Both skills close threads, and either may reopen one.

Resolve a thread when:

- the reviewer verdicts it `fixed`, `accepted`, or `obsolete`;
- its work is done and needs no reviewer verdict — a question answered, a finding already addressed by code the reviewer can see;
- it went outdated or stopped being relevant — the file was deleted, the approach was replaced, the finding was withdrawn.

A `declined` reply does not resolve its own thread. Declining states a position; the reviewer accepting it is what settles the disagreement, and closing early would hide a live dispute from the round cap.

`code-review-address` resolves each thread as it finishes that thread — reply posted, change live — rather than batching resolutions at the end. Threads sitting at `needs-info` or `blocked` stay open.

`code-review-publish` resolves what it verdicts `fixed`, `accepted`, or `obsolete`, and its own findings once it withdraws them. A stale thread left from an earlier round is the reviewer's to close, not something the addresser inherits.

Reopen a thread rather than file a fresh finding, which would strand the original discussion: the fix regressed, a later commit undid it, or a reply claimed more than the code delivered. Post a new reply on the thread saying why it reopened.

Resolve nothing whose reply is still missing. Where only the other party can resolve a thread, report that rather than claiming it.

## Verdicts and the round cap

Re-reviewing, `code-review-publish` reads each prior finding and its reply, then verdicts it against the code. Verify against the diff: a reply's word is evidence of intent, not of outcome.

| Verdict | Means | The thread |
| --- | --- | --- |
| `fixed` | the code now satisfies the finding | resolves |
| `accepted` | a `declined` reply whose reasoning the reviewer accepts | resolves |
| `obsolete` | the code the finding described is gone | resolves |
| `not-fixed` | the finding still stands against the current code | stays open |

`fixed` names the finding's fate, not the reply's credibility, so it cannot be read as "the finding is confirmed still present" — that state is `not-fixed`.

A finding `declined` once and then verdicted `not-fixed` is **disputed**. Publish stops re-posting it and lists it under `## Disputed` in the summary for a human to settle. Two rounds is the cap on any one finding, and that cap is what stops an agent loop re-litigating a point forever.

## Status

Every completed review reaches one status. The findings tell the author what to change; the status tells them where the change stands — blocked, waiting on an answer, or approved. Without it the author reads every line comment to work out what has to happen next, which is the one question they opened the review to answer.

| Status | Means | Forge event |
| --- | --- | --- |
| `Changes Requested` — rendered `Changes Requested (advisory)` in a non-gating body | at least one blocking finding is unsettled | `REQUEST_CHANGES` when authorized; otherwise `COMMENT` |
| `Needs Information` | no blocking finding is unsettled, but an unanswered question could change the verdict | `COMMENT` |
| `Approved` — rendered `Approved (advisory)` in a non-gating body | nothing blocks the merge and no outcome-changing question is unanswered | `APPROVE` when authorized; otherwise `COMMENT` |

`Needs Information` is deliberately narrow: it is valid only while a question satisfying the Questions contract remains unanswered and could change the verdict.

Before deriving it, classify both axes as Passed, Findings, or `Not applicable`; add Waiting for information where a qualifying question prevents completion:

| Axis outcome | Means |
| --- | --- |
| Passed | assessed with no findings |
| Findings | assessed with at least one blocking or optional finding |
| `Not applicable` | deliberately outside this review because no requirement or rule calls for it |
| Waiting for information | a qualifying open question prevents completing assessment; may accompany Findings |

The question itself remains axis-free. Anything else left unassessed means the review did not finish: abort before publishing and report the operational failure. An incomplete review has no status and cannot fall through to `Approved`.

Derive the status in order rather than judging it separately:

- Any unsettled blocking finding, disputed ones included, means `Changes Requested`. A blocking finding settles when the reviewer verdicts it `fixed`, `accepted`, or `obsolete` — until then it counts, whatever its thread says.
- With no unsettled blocking finding, any unanswered question whose answer could change the verdict means `Needs Information`.
- Otherwise the review is `Approved`. Optional findings and answered questions do not hold it back — they are the author's to close.

With no originating spec, Requirements is `Not applicable` unless the user or repository workflow requires one; a required missing spec makes that axis Waiting for information.

Authorization never changes the status. It changes only which forge event may carry it. When the forge permits only a comment, render `Changes Requested` or `Approved` in its defined advisory form; `Needs Information` already uses `COMMENT` as its native event.

A disputed blocking finding holds the status at `Changes Requested` and needs a person. The round cap stops that finding being re-posted; it does not turn a blocker into a merge.

### Where the status goes

The status is the conclusion; the forge event is its transport. Submit `APPROVE` or `REQUEST_CHANGES` only where the user or the repository's documented workflow authorizes this identity to gate a merge. Those events carry the status without restating it in the body.

Use `COMMENT` for `Needs Information`, and for any self-review or unauthorized review. Where the event cannot carry the status, the summary's first line states it in words instead:

```markdown
**Changes Requested (advisory)** — 1 blocking finding.

Requirements: Passed. Code: Findings — 1 blocking, 2 optional.
```

For a needs-information review, the first line carries the actionable question:

```markdown
**Needs Information** — @octocat, confirm whether retries must preserve request order.

Requirements: Waiting for information. Code: Passed.
```

The examples use the table's defined display forms. This covers a forge with no review system and a review whose event the forge will not take: GitHub refuses `APPROVE` and `REQUEST_CHANGES` on your own pull request, and an unauthorized reviewer submits `COMMENT` whatever the status. A bare `COMMENT` carries none of those meanings, so the body has to.

A status can move without the head moving — a decline accepted, a question answered, an `already-addressed` reply verdicted `fixed`, nothing recommitted. Publishing that new status takes a new review: a review's state is fixed at submission, and the update endpoint rewrites a body, not a state. On GitHub inspect the superseded review's state before dismissing it. `COMMENTED` carries no gate, so a new review alone settles it. A later gate event supersedes the same identity's earlier gate state; in particular, `APPROVE` clears `CHANGES_REQUESTED`. A new `COMMENT` cannot clear an old `APPROVED` or `CHANGES_REQUESTED` state, so dismiss that gating review when the semantic status moves to `Needs Information` or another non-gating form.

Where the forge refuses a required dismissal — a branch protection rule can restrict who may dismiss a review — write the new semantic status in the body and report the exact stale gating state as needing an authorized actor. Changing the conclusion to match the stale event would state a result the review did not reach.

## Review summary

One general pull-request comment or review body:

- the status on the first line, where no review event carries it, with what drives it — never below the index, never left to be inferred from the counts;
- the per-axis outcome: Passed, Findings, or `Not applicable`, plus Waiting for information where it applies;
- the reviewed head SHA and the comparison base;
- an index of findings — axis tag, `[Optional]` where it applies, title, and link to each line comment;
- per-axis counts split blocking and optional, and the worst finding within each axis;
- re-reviewing: the prior head, and one verdict line per prior finding;
- `## Disputed`, when any finding has hit the cap;
- `## Open questions`, when any question is unanswered, linking each line question and carrying the stable id for each whole-change question.

The line comment is where a finding lives; the summary indexes and totals. Restating finding text in the summary makes the human read everything twice.

A batched review creates its body and its comments in one call, so the comment URLs do not exist yet when that body is written. Publish in two phases: submit the review with a body carrying the index by `file:line`, read the created comment URLs back, then update the review body with the links. Where the second phase fails, the `file:line` index still stands on its own — never block the review on it.

## Addressing summary

Resolving every thread leaves a pull request looking untouched. The forge collapses resolved threads, so a round that answered everything and a round that did nothing render the same, and the reviewer has to expand each one to find out which. `code-review-address` closes a round with one general pull-request comment:

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
- what still needs someone: `declined` awaiting a verdict, `needs-info` awaiting an answer, `blocked` items and their blocker;
- the checks run;
- whether the round is finished or waiting — the sentence the reviewer would otherwise open every thread to infer.

One comment per round, never one per item. Whole-change question answers are the only per-item detail in this comment because those questions have no threads: give each a concise answer entry and its own reply trailer in the summary. Every other item's detail stays in its thread, and the summary only indexes it. Re-running at the same head updates that comment rather than posting a second.

Where the forge routes review requests, ask for a re-review from the identity whose review the round addressed. That puts the round in their queue instead of leaving it to be noticed, and it is the counterpart to the reviewer's status — the reviewer says where the change stands, the addresser says it is ready to be looked at again. A re-request does not clear an earlier `REQUEST_CHANGES`; only a later review from that identity, or a dismissal, does.

## Humans in the loop

Trailers speed up the agent path; they never gate it. A finding or reply written by a human carries no trailer — read it as prose, infer its disposition, and reply to it exactly as to any other. Never skip an item for lacking a trailer, and never address a human reviewer by writing a trailer on their behalf.

## GitHub verbs

If this repo's `docs/agents/issue-tracker.md` names a forge other than GitHub, follow that file instead.

`gh api` substitutes `{owner}` and `{repo}` from the clone, so the paths below are copy-pasteable as written.

**Posting identity**: `gh api user --jq .login`. Compare with `gh pr view <n> --json author` to detect a self-review.

**Resolve the pull request**: `gh pr view <n> --json number,url,author,headRefName,baseRefName,headRefOid,state,body`. `headRefOid` is the head SHA to record as reviewed.

### Reading review activity

- **Reviews**: `gh api repos/{owner}/{repo}/pulls/<n>/reviews --jq '.[] | {id, user: .user.login, state, commit_id, body}'`. `commit_id` is the head that review covered; it differing from the current `headRefOid` is what makes a run a re-review.
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

- **One review carrying every line comment** — a single call producing a single timeline entry:

  ```sh
  gh api --method POST repos/{owner}/{repo}/pulls/<n>/reviews --input - <<'JSON'
  { "commit_id": "<head sha>",
    "event": "COMMENT",
    "body": "<summary markdown>",
    "comments": [
      { "path": "src/order.ts", "line": 42, "side": "RIGHT", "body": "..." }
    ] }
  JSON
  ```

  Batch all findings into that one `comments` array. One call per finding produces one empty-bodied review per finding.

  For `Changes Requested` or `Approved`, use `REQUEST_CHANGES` or `APPROVE` where authorized. Use `COMMENT` for `Needs Information` and every non-gating review. A `COMMENT` means the body states the status in words, using the table's advisory form where it defines one.

  `line` must be a line the diff touches, on `side` `RIGHT` (or `LEFT` for a deleted line); a range takes `start_line` plus `line`. To comment on a file as a whole, set `"subject_type": "file"` and omit `line`.

- **Self-review**: `event: "COMMENT"` is accepted on your own pull request. `APPROVE` and `REQUEST_CHANGES` return 422 there, so the body's status line is the whole signal.
- **Reply to an inline comment**: `gh api --method POST repos/{owner}/{repo}/pulls/<n>/comments/<comment_id>/replies -f body='...'`, addressing the thread's first comment id.
- **General comment**: `gh pr comment <n> --body-file -` with a heredoc. This is where an addressing summary goes; find an earlier one to update by grepping `issues/<n>/comments` for its `addressed head=` trailer.
- **Request a re-review**: `gh pr edit <n> --add-reviewer <login>`, or `gh api --method POST repos/{owner}/{repo}/pulls/<n>/requested_reviewers -f 'reviewers[]=<login>'`. Take `<login>` from the review being addressed. Authoring the pull request is no bar to requesting one: GitHub returns 422 only when `<login>` is the pull request's own author, or the account cannot review it. Where one identity both reviewed and addressed, that refusal is certain and the summary comment is the whole signal.
- **Edit a comment**: `gh api --method PATCH repos/{owner}/{repo}/pulls/comments/<id> -f body='...'`; for a general comment, `repos/{owner}/{repo}/issues/comments/<id>`.
- **Update a review body**: `gh api --method PUT repos/{owner}/{repo}/pulls/<n>/reviews/<review_id> -f body='...'`. This is the second phase of a linked index — the POST that creates the review returns the comment ids its `_links` resolve from. It takes a body and nothing else, so a status change needs a new review rather than an edit to this one.
- **Supersede or dismiss a review**: a later gating event from the same identity supplies its current gate state; in particular, `APPROVE` clears an earlier `REQUEST_CHANGES`. A `COMMENT` leaves an earlier `APPROVED` or `CHANGES_REQUESTED` state standing. To clear a gate without replacing it: `gh api --method PUT repos/{owner}/{repo}/pulls/<n>/reviews/<review_id>/dismissals -f message='...' -f event=DISMISS`. Write access is the baseline, and a branch protection rule restricting who may dismiss a review can refuse it anyway — a `403` there is an answer, not something to retry.
- **Add a reaction**: `gh api --method POST repos/{owner}/{repo}/pulls/comments/<id>/reactions -f content=eyes`; for a general comment, `repos/{owner}/{repo}/issues/comments/<id>/reactions`. Content is one of `+1`, `-1`, `laugh`, `confused`, `heart`, `hooray`, `rocket`, `eyes`. A review object itself takes no reactions — react to its comments.
- **Resolve or reopen a thread**: GraphQL only, no REST equivalent.

  ```sh
  gh api graphql -f query='mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -f id=<thread node id>
  gh api graphql -f query='mutation($id:ID!){ unresolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -f id=<thread node id>
  ```
