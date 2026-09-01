# Publishing

How the findings reach the pull request, what status they add up to, and the forge verbs.

If `docs/agents/issue-tracker.md` names a forge other than GitHub, follow that file for the verbs and keep the semantics below.

## Status

Every completed review reaches exactly one status. The findings tell the author what to change; the status tells them where the change stands. Without it they have to read every line comment to work out the one thing they opened the review to learn.

| Status | Means |
| --- | --- |
| `Changes Requested` | at least one `must-fix` finding is unsettled |
| `Needs Information` | no unsettled `must-fix`, but an open question could change the verdict |
| `Approved` | nothing blocks the merge and no outcome-changing question is open |

Derive it in that order, never by judging it as a whole:

1. Any unsettled `must-fix`, disputed ones included → `Changes Requested`. A `must-fix` settles only when this review verdicts it `fixed`, `accepted`, or `obsolete` — not when the author replies to it.
2. Otherwise, any open question whose answer could change the verdict → `Needs Information`.
3. Otherwise → `Approved`. `consider` findings and answered questions do not hold a review back; they are the author's to close.

A question keeps a review at `Needs Information` until someone answers it, you withdraw it, or you determine its answer cannot change the verdict. It never ages into approval.

Classify each axis before deriving the status — `Passed`, `Findings`, `Not applicable`, or `Waiting for information`. Anything left unassessed means the review did not finish: stop before publishing and report the operational failure. An incomplete review has no status and must never fall through to `Approved`.

With no originating issue, Requirements is `Not applicable`.

## Status versus forge event

The status is the conclusion; the event is its transport, and authorization changes only the transport.

Submit `APPROVE` or `REQUEST_CHANGES` only where the caller or the repository's documented workflow authorizes this identity to gate a merge. Otherwise submit `COMMENT` and state the status in words on the summary's first line, rendered `Changes Requested (advisory)` or `Approved (advisory)`. `Needs Information` uses `COMMENT` natively.

GitHub refuses `APPROVE` and `REQUEST_CHANGES` on your own pull request and accepts `COMMENT` there, so authoring the pull request is not a reason to fall back to a general comment — it is a reason the body has to carry the status.

## The summary

The review body:

- the status on the first line where the event does not carry it, with what drives it;
- the per-axis outcome;
- the reviewed head SHA and the comparison base;
- **one short paragraph, two or three sentences**, reading the findings as a whole: what the change does, what drives the status, what to deal with first. It generalizes — a pattern several findings share, one fault behind them, the shape of the risk — rather than reciting them, and names at most the two or three findings that decide the outcome. This is the only place that generalizes, and it earns its space by saying what no single finding says. A review with one finding or none says so in a sentence;
- an index of findings, worst first within each axis, each entry carrying its tags, title, and a link to its comment;
- counts by axis and action;
- re-reviewing: the prior head and one verdict line per prior finding;
- `## Open questions`, when any are unanswered;
- `## Disputed`, when any finding has hit the round cap.

Do not restate finding text outside the index — the line comment is where a finding lives, and repeating it makes the reader read everything twice. Do not mention refuted candidates; report the count to the caller in the session instead.

```markdown
**Changes Requested (advisory)** — 1 blocking finding, 1 open question.

Code: Findings — 1 blocking, 2 optional. Requirements: Passed.
Reviewed `a1b2c3d` against `main` (merge-base `9e8d7c6`).

Retries are the thing to fix: the new path swallows validation errors the queue downstream
assumes have already been raised. The two optional findings are the same duplicated shape
either side of it and clear up with it. The open question is whether the 30s timeout is
deliberate; if it is, nothing else here blocks.
```

## One review, one call

Submit the body and every line comment together. One call, one timeline entry.

```sh
gh api --method POST repos/{owner}/{repo}/pulls/<n>/reviews --input - <<'JSON'
{ "commit_id": "<head sha>",
  "event": "COMMENT",
  "body": "<summary markdown>",
  "comments": [
    { "path": "src/order.ts", "line": 47, "side": "RIGHT", "body": "..." }
  ] }
JSON
```

One call per finding produces one empty review per finding, which is the failure mode this shape exists to avoid.

`line` is the finding's `anchor`, and must be a line the diff touches — `finding-format.md` § Anchor and fix site is what chose it, so do not re-derive one here. `side` is `RIGHT` (`LEFT` for a deleted line); a range takes `start_line` plus `line`. For a whole file, set `"subject_type": "file"` and omit `line`. A finding the ladder gave no honest anchor goes in the body, with its `fix` site named there.

The comment URLs do not exist when the body is written, so publish in two phases: submit with the index by `file:line`, read back the created comment URLs, then `PUT repos/{owner}/{repo}/pulls/<n>/reviews/<review_id> -f body='...'` with the links. If the second phase fails, the `file:line` index stands on its own — never block a review on it.

## Re-review

Reading prior activity:

- reviews — `gh api repos/{owner}/{repo}/pulls/<n>/reviews --jq '.[] | {id, user: .user.login, state, commit_id, body}'`. `commit_id` differing from the current `headRefOid` is what makes a run a re-review.
- inline comments — `gh api repos/{owner}/{repo}/pulls/<n>/comments`. Cite `original_line` for location; `line` goes null once a push outdates the comment.
- thread state — GraphQL only:

  ```sh
  gh api graphql -f query='
    query($owner:String!,$repo:String!,$pr:Int!){
      repository(owner:$owner,name:$repo){ pullRequest(number:$pr){
        reviewThreads(first:100){ nodes{
          id isResolved isOutdated path line
          comments(first:1){ nodes{ databaseId } } } } } } }
  ' -f owner=<owner> -f repo=<repo> -F pr=<n>
  ```

Correlate prior findings by trailer `id`, not by line. Verdict each against the current code — a reply's word is evidence of intent, not of outcome, so check the diff:

| Verdict | Means | Thread |
| --- | --- | --- |
| `fixed` | the code now satisfies the finding | resolve |
| `accepted` | a decline whose reasoning you accept | resolve |
| `obsolete` | the code it described is gone | resolve |
| `not-fixed` | it still stands against the current code | leave open |

Reply on the existing thread rather than posting a new comment: `gh api --method POST repos/{owner}/{repo}/pulls/<n>/comments/<comment_id>/replies -f body='...'`, addressing the thread's first comment id.

Resolve what you settle, and your own withdrawn findings:

```sh
gh api graphql -f query='mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -f id=<thread node id>
```

Reopen — `unresolveReviewThread` — rather than filing a fresh finding when a fix regressed or a reply claimed more than the code delivered, and say why in a new reply. Leave open anything that still asks something of someone.

**The round cap.** A finding declined once and then verdicted `not-fixed` is disputed. Stop re-posting it, list it under `## Disputed`, and leave it for a person. Two rounds is the cap on any one finding. A disputed `must-fix` still holds the status at `Changes Requested` — the cap stops the argument, it does not turn a blocker into a merge.

## Publishing twice

Before writing, check for an existing review from this identity at this head and compare its status as well as its head.

- Same head, same status — that review stands. Update its body if the forge allows; otherwise report it as already published. Do not post a second.
- Same head, moved status — a decline accepted, a question answered — publish a new review carrying the new event and summary, without re-posting line comments that are already up. A review's state is fixed at submission; the update endpoint rewrites a body, not a state.
- Dismiss a superseded review only where it carried a gate the new event cannot replace. A later `APPROVE` clears an earlier `REQUEST_CHANGES`; a `COMMENT` supersedes another `COMMENT` with no dismissal needed, and cannot clear a standing `APPROVED` or `CHANGES_REQUESTED`.

  ```sh
  gh api --method PUT repos/{owner}/{repo}/pulls/<n>/reviews/<review_id>/dismissals -f message='...' -f event=DISMISS
  ```

  A branch protection rule can refuse this. A `403` is an answer, not something to retry: write the new status in the body and report the stale gating state as needing an authorized actor.

## Reactions

Where the forge has them, a reaction rides on top of a reply and never replaces one: `+1` agreed and acting, `eyes` seen and in progress, `-1` disagreed with the reason in the reply, `confused` unclear with the question in the reply, `hooray`/`heart`/`rocket` a genuinely good catch. One per comment.

```sh
gh api --method POST repos/{owner}/{repo}/pulls/comments/<id>/reactions -f content=eyes
```
