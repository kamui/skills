# Publishing

How the findings reach the pull request, what status they add up to, and the forge verbs.

The finding shape and finding trailer remain in [`finding-format.md`](finding-format.md).

If `docs/agents/issue-tracker.md` names a forge other than GitHub, follow that file for the verbs and keep the semantics below.

## Status

Every completed review reaches exactly one status. The findings tell the author what to change; the status tells them where the change stands. Without it they have to read every line comment to work out the one thing they opened the review to learn.

| Status | Means |
| --- | --- |
| `Changes Requested` | at least one `must-fix` finding is unsettled |
| `Incomplete` | nothing blocking is known, but the review did not inspect everything it should have |
| `Needs Information` | coverage is complete and no `must-fix` is unsettled, but an open question could change the verdict |
| `Approved` | coverage is complete, nothing blocks the merge, and no outcome-changing question is open |

Derive it in that order, never by judging it as a whole:

1. Any unsettled `must-fix`, disputed ones included → `Changes Requested`. A `must-fix` settles only when this review verdicts it `fixed`, `accepted`, or `obsolete` — not when the author replies to it.
2. Otherwise, coverage short of complete → `Incomplete`.
3. Otherwise, any open question whose answer could change the verdict → `Needs Information`.
4. Otherwise → `Approved`. `consider` findings and answered questions do not hold a review back; they are the author's to close.

The ladder keys on **action alone**. Priority never enters the derivation: a `P1 consider` holds nothing back, and a `P2 must-fix` blocks. A run that finds itself raising a priority to move the status is doing the derivation backwards.

`Incomplete` is the status that stops a truncated run from reading as a clean one. A review that skipped a file, lost a fetch, or abandoned a check has not earned `Approved`, and the two are indistinguishable from the outside unless the review says so. It publishes whatever it did verify and names what it did not — findings from an incomplete review are still findings. It is not a failure state: an operational failure that prevents classification still stops the run before publishing.

A question keeps a review at `Needs Information` until someone answers it, you withdraw it, or you determine its answer cannot change the verdict. It never ages into approval.

Coverage is `complete` only when every file in the changed-file manifest is `reviewed` or `ignored` with a defensible reason, and every fetch and check the run started either finished or is named as unfinished. It measures inspection, not output: a complete review with no findings is the good outcome.

Classify each axis before deriving the status — `Passed`, `Findings`, or `Waiting for information`. An axis is `Waiting for information` when an open question prevents completing its assessment; the question itself still carries no axis and counts toward no total. A bounded gap — a changed file the run could not read, a check it started and did not finish — is a coverage shortfall, not an unclassified axis: classify the axis on what was inspected, name the gap in the coverage line, and let step 2 of the ladder yield `Incomplete`, which publishes the verified findings with `COMMENT`. Stop before publishing only on an operational failure that leaves an axis with no classification at all — a finder that never returned, a diff that could not be read — and report that failure to the caller instead. A review with no status publishes nothing, and nothing falls through to `Approved`.

With no originating issue, the Requirements axis still classifies normally — it ran against the pull request body's claims and non-goals — and the summary states **issue alignment: unavailable** beside its outcome.

A retrospective review of a merged pull request publishes only when the caller explicitly enabled publication, and its summary's first line names the condition: this reviews an already-merged change.

## Status versus forge event

The status is the conclusion; the event is its transport, and authorization changes only the transport.

Submit `APPROVE` or `REQUEST_CHANGES` only where the caller or the repository's documented workflow authorizes this identity to gate a merge. Otherwise submit `COMMENT` and state the status in words on the summary's first line, rendered `Changes Requested (advisory)` or `Approved (advisory)`. `Needs Information` and `Incomplete` use `COMMENT` natively — neither has a gating form, and `Incomplete` must never be carried by `APPROVE` whatever the authorization.

GitHub refuses `APPROVE` and `REQUEST_CHANGES` on your own pull request and accepts `COMMENT` there, so authoring the pull request is not a reason to fall back to a general comment — it is a reason the body has to carry the status.

## The summary

The review body:

- the status on the first line where the event does not carry it, with what drives it;
- the per-axis outcome;
- the run identity — reviewed head, base ref, and merge-base — and the coverage line, naming the uncovered files where coverage is short;
- **one short paragraph, two or three sentences**, reading the findings as a whole: what the change does, what drives the status, what to deal with first. It generalizes — a pattern several findings share, one fault behind them, the shape of the risk — rather than reciting them, and names at most the two or three findings that decide the outcome. This is the only place that generalizes, and it earns its space by saying what no single finding says. A review with one finding or none says so in a sentence;
- an index of findings, worst first within each axis, each entry carrying its tags, its title, and its anchor as a rendered coordinate fragment — followed by `; fix` and the fix's fragment when the fix differs — the title linking its comment once phase 2 has read the comment URLs back;
- counts by axis and action;
- re-reviewing: the prior head and one verdict line per prior finding;
- `## Observations`, when any exist;
- `## Open questions`, when any are unanswered;
- `## Disputed`, when any finding has hit the round cap.

`## Observations` is bounded and explicitly non-actionable: at most **three** items, each one sentence plus one `file:line` evidence pointer, none carrying "should" or "must" language, none anchored as a line comment, none counted in any total. It opens with the sentence "These are accurate observations, not findings — no action is requested." It exists so an accurate fact that failed the finding bar — a finder's sub-threshold observation, a verifier aside — surfaces instead of dying out-of-band. More than three means the reviewer is smuggling findings; keep the three with the most decisive evidence and drop the rest. The evidence pointer stays a code span, never a link — Coordinate links says why.

Do not restate finding text outside the index — the line comment is where a finding lives, and repeating it makes the reader read everything twice. Do not mention refuted candidates; report the count to the caller in the session instead.

```markdown
**Changes Requested (advisory)** — 1 blocking finding, 1 open question.

Code: Findings — 1 blocking, 2 optional. Requirements: Passed.
Reviewed `a1b2c3d` against `main` (merge-base `9e8d7c6`). Coverage: complete.

Retries are the thing to fix: the new path swallows validation errors the queue downstream
assumes have already been raised. The two optional findings are the same duplicated shape
either side of it and clear up with it. The open question is whether the 30s timeout is
deliberate; if it is, nothing else here blocks.

- [Code] [must-fix] [P1] — `parseOrder` swallows the validation error on the retry path — anchor [`src/order.ts:47`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/src/order.ts?plain=1#L47)
- [Code] [consider] [P2] — `retryOnce` drops the idempotency key across attempts — anchor [`src/order.ts:61`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/src/order.ts?plain=1#L61); fix [`src/retry-policy.ts:18`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/src/retry-policy.ts?plain=1#L18)
- [Code] [consider] [P3] — the quickstart still documents the synchronous call — anchor [`docs/ops.md`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/docs/ops.md)

**[Code] [consider] [P3] the quickstart still documents the synchronous call**

[`docs/ops.md`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/docs/ops.md) — the diff rewrites the file and keeps the synchronous sequence as the first example, while the queue path is the documented default now.

**Change**: rewrite the quickstart's first example against the queue path.

Closing this without action is a correct response.

<!-- finding id=code/ops-md/sync-quickstart axis=code action=consider priority=P3 head=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 -->

## Open questions

**[Question] Is the 30s queue timeout deliberate?**

The new queue path defaults to 30s — [`src/config.ts`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/src/config.ts) is where the diff sets it — where every caller it replaces used 5s. The issue is silent on timeouts and the history shows no rationale. If it is deliberate, a comment saying why would stop the next reader changing it.

**Change no code for this.** Answer it, or say what would settle it.

<!-- finding id=question/queue-timeout-30s action=question head=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 -->

## Observations

These are accurate observations, not findings — no action is requested.

- The retry loop logs each attempt at `info` level (`src/retry-policy.ts:31` in the pre-image).
```

This body is the phase-1 fixture: every index entry, body-resident finding, and whole-change question carries its coordinate as a rendered fragment whose text is the unchanged coordinate, and the observations pointer is a code span. Phase 2 makes each index title link to its comment and leaves every file fragment byte-identical.

## Coordinate links

Every file coordinate the body carries is rendered by `python3 scripts/link_coordinate.py`, which owns the URL rule so no review composes a URL by hand. A coordinate the rule can express renders as a link whose visible text is the unchanged coordinate:

```markdown
anchor [`src/order.ts:47`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/src/order.ts?plain=1#L47)
```

- the link resolves under the base repository's canonical web URL at the reviewed full head SHA — immutable across force-pushes, readable from outside the pull request, never a branch URL or an abbreviated SHA;
- a line or range carries `?plain=1#L<line>` or `?plain=1#L<start>-L<end>`; a file anchor carries neither;
- a distinct fix site renders its own fragment and follows the anchor as `; fix` with its fragment;
- a `LEFT` anchor stays a code span: it belongs to the merge-base, and merge-base and rename links are [issue #84](https://github.com/kamui/skills/issues/84)'s item;
- an observation's evidence pointer stays a code span: the ledger row behind it does not record the side or revision the evidence was read at, and structured provenance is [issue #84](https://github.com/kamui/skills/issues/84)'s item.

Render each fragment with the script's `render` command, and `check` a fragment already written whenever the body is assembled or updated; a non-zero exit stops the step — report the script's output and fix the inputs, never the fragment by hand. File links sit beside the comment links, not in place of them: a comment link reaches the thread, a file link reaches the code the finding was read against.

## One review, one call

**Re-read the head immediately before this call.** If it differs from the reviewed head, or cannot be read, publish nothing and report the stale review — the anchors were computed against a diff that has moved, so every line comment risks landing on code that no longer says what the finding claims. This check costs one API call and is the difference between a stale review and a wrong one.

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

Validate every anchor against the diff before submitting — `git diff <base>...<head> --unified=0` gives the touched ranges cheaply, and one comment on an untouched line fails the entire batched call. An anchor that fails validation moves down the ladder to the body, never into a doomed request.

`line` is the finding's `anchor`, and must be a line the diff touches — `finding-format.md` § Anchor and fix site is what chose it, so do not re-derive one here. `side` is `RIGHT` (`LEFT` for a deleted line — a `LEFT` anchor stays a code span in the body; Coordinate links says why); a range takes `start_line` plus `line`. This call takes line comments only: GitHub documents `subject_type: file` on its single-comment endpoint, not in this call's `comments[]`, and one entry without a valid `line` fails the whole batch. So a finding whose honest anchor is a whole file goes in the body, as does a finding the ladder gave no anchor, each appearing there in full with its anchor and `fix` coordinates rendered as the same fragments (Coordinate links).

End the body with a run trailer, so a later run can correlate what this one covered without re-deriving it:

```
<!-- review-run workflow=v2a-1 head=<full 40-hex sha> base-ref=<branch> base-sha=<full 40-hex sha> merge-base=<full 40-hex sha> issues=<owner/repo#n,...|none> coverage=<complete|incomplete> -->
```

Values are single tokens with no spaces; list issues sorted and comma-separated. Every SHA in a trailer is full-width, 40 hex characters — trailers are machine-read across rounds and abbreviations are ambiguous over time. Short SHAs stay fine in visible prose. `workflow=v2a-1` identifies which reviewer contract produced the run, so a later run knows whose trailer vocabulary it is reading; the trailer's pinned SHAs are this run's identity record.

The comment URLs do not exist when the body is written, so publish in two phases: submit with the index entries carrying their rendered coordinate fragments — the phase-1 body is complete and clickable on its own — then read back the created comment URLs and `PUT repos/{owner}/{repo}/pulls/<n>/reviews/<review_id> -f body='...'` with each entry's title now linked to its comment and every file fragment left byte-identical. If the second phase fails, the phase-1 body stands on its own — never block a review on it.

Questions ride inside the same review, anchored by the same ladder. A whole-change question, and any finding the ladder sent to the body, appears there in full — tag line through trailer — under `## Open questions` or under its axis in the index, with the anchor and `fix` coordinates its prose names rendered as the same fragments (Coordinate links).

## Re-review

`id` slugs the axis, the file, and the finding — `code/order-ts/swallowed-validation-error`. **Never a line number**: lines drift between rounds and the id has to survive that. One finding against the same code keeps one id across every round, which is what lets a re-review correlate it to its thread and verdict it rather than posting it again.

A candidate the verifier ruled `plausible` publishes as a question and takes a `question/...` id, not the axis id it was proposed under. If a later round confirms it, it becomes a finding under its own axis id and the question resolves as answered. The two ids stay distinct on purpose: the record then shows a question that turned out to expose a defect, rather than a finding that silently changed shape between rounds.

A responding agent replies with a matching trailer:

```
<!-- reply to=<finding id> disposition=<implemented|already-addressed|answered|declined|needs-info|blocked> head=<full 40-hex sha> -->
```

and a re-review writes its verdict on the thread:

```
<!-- verdict on=<finding id> verdict=<fixed|accepted|obsolete|not-fixed> head=<full 40-hex sha> -->
```

`fixed` names the finding's fate, not the reply's credibility — a finding that still stands is `not-fixed`. `accepted` is how a decline you agree with gets closed.

## Humans without trailers

A finding or reply written by a person carries no trailer. Read it as prose, infer what it means, and treat it exactly as any other item. Never skip something for lacking a trailer, and never write a trailer on a person's behalf. The trailers speed up the agent path; they do not gate it.

## Thread handling

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

Correlate prior findings by trailer `id`, not by line. The verify step supplies the verdict wherever it turns on the code; judging a decline is the reviewer's own call. Either way a reply's word is evidence of intent, not of outcome:

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

