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

A question keeps a review at `Needs Information` until someone answers it, you withdraw it, or you determine its answer cannot change the verdict. It never ages into approval. Only an outcome-changing fact no available source can settle is published as a question at all (`finding-format.md` § Settle, ask, or record), so a question that reaches the pull request is one whose answer the review is genuinely waiting on.

An unresolved record is never evidence that the code is correct. A `plausible` verdict, a file nobody read, a check left unfinished, a deferral the record leaves open: each is named where it belongs — the coverage line, `## Open questions`, or the run report — and none of them may be cited as a reason the change is safe. What they do to the status, the ladder decides in its own order: an unfinished check is a coverage shortfall, which reaches `Incomplete` at step 2 unless an unsettled `must-fix` has already settled the status at step 1.

Coverage is `complete` only when every file in the changed-file manifest is `reviewed` or `ignored` with a defensible reason, every fetch and check the run started finished, and every candidate the verifier was given came back with exactly one accounted verdict. Material nobody could read, a check nobody finished, a candidate withheld because its verdict was missing or malformed after the one repair, a related row left unruled, and a verifier that could not be run in an isolated context each leave coverage short: name each in the coverage line — `verification incomplete: <ids>` or `verification not isolated` — which is what turns unfinished evidence into `Incomplete` rather than into an approval. Candidates whose verdicts were accounted still publish beside that line, and an unsettled `must-fix` among them still takes precedence at step 1. It measures inspection, not output: a complete review with no findings is the good outcome, and a run that skipped the verifier because the finders returned no candidates records that explicitly rather than as a gap.

Classify each axis before deriving the status — `Passed`, `Findings`, or `Waiting for information`. An axis is `Waiting for information` when an open question prevents completing its assessment; the question itself still carries no axis and counts toward no total. A review-record deferral on the axis's subject keeps the Requirements axis at `Waiting for information` when it published as a question — that is, when its answer moves a decision this merge settles (`requirements-axis.md` § Step 2). A deferral the axis recorded instead, on a preview surface with the decision postponed to a later gate, leaves the axis free to pass and reaches the caller in the run report; the record still shows the decision open rather than accepted. A bounded gap — a changed file the run could not read, a check it started and did not finish — is a coverage shortfall, not an unclassified axis: classify the axis on what was inspected, name the gap in the coverage line, and let step 2 of the ladder yield `Incomplete`, which publishes the verified findings with `COMMENT`. Stop before publishing only on an operational failure that leaves an axis with no classification at all — a finder that never returned, a diff that could not be read — and report that failure to the caller instead. A review with no status publishes nothing, and nothing falls through to `Approved`.

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

`## Observations` is bounded and explicitly non-actionable: at most **three** items, each one sentence plus one `file:line` evidence pointer, none carrying "should" or "must" language, none anchored as a line comment, none counted in any total. It opens with the sentence "These are accurate observations, not findings — no action is requested." It exists so an accurate fact that failed the finding bar — a finder's sub-threshold observation, a verifier aside — surfaces instead of dying out-of-band. Pool the finders' observations with the verifier's and deduplicate the pool by `verify.md` § Deduplicate before the cap applies — the verifier never sees a finder's observation, so the orchestrator is where one that repeats another, or states a confirmed finding's fact, is dropped. More than three means the reviewer is smuggling findings; keep the three with the most decisive evidence and drop the rest. Drop from the pool, before the cap, any item asserting a consequence nobody established — "this path is safe", "the change is correct as merged" — and record it in the run report with its own marker, `observation (unpublished, unestablished consequence)`, so the cap's overflow record keeps measuring the cap. The channel carries facts whose absence of consequence was shown; an unproven one published as an accurate aside reads as a clean bill of health the run never earned. Record every observation the cap drops in the run report with the marker `observation (unpublished, cap)` and its evidence pointer; the caller receives them in the session report, not the pull request. Never fold a dropped observation or verifier aside into a finding's prose. The evidence pointer stays a code span, never a link — Coordinate links says why.

Do not restate finding text outside the index — the line comment is where a finding lives, and repeating it makes the reader read everything twice. Do not mention refuted candidates; report the count to the caller in the session instead.

```markdown
**Changes Requested (advisory)** — 1 blocking finding, 1 open question.

Code: Findings — 1 blocking, 2 optional. Requirements: Passed.
Reviewed `a1b2c3d` against `main` (merge-base `9e8d7c6`). Coverage: complete.

Retries are the thing to fix: the new path swallows validation errors the queue downstream
assumes have already been raised. The two optional findings are the same duplicated shape
either side of it and clear up with it. The open question is whether the 30s timeout fits the
gateway's request budget; if it does, nothing else here blocks.

- [Code] [must-fix] [P1] — `parseOrder` swallows the validation error on the retry path — anchor [`src/order.ts:47`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/src/order.ts?plain=1#L47)
- [Code] [consider] [P2] — `retryOnce` drops the idempotency key across attempts — anchor [`src/order.ts:61`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/src/order.ts?plain=1#L61); fix [`src/retry-policy.ts:18`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/src/retry-policy.ts?plain=1#L18)
- [Code] [consider] [P3] — the quickstart still documents the synchronous call — anchor [`docs/ops.md`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/docs/ops.md)

**[Code] [consider] [P3] the quickstart still documents the synchronous call**

[`docs/ops.md`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/docs/ops.md) — the diff rewrites the file and keeps the synchronous sequence as the first example, while the queue path is the documented default now.

**Triggers when**: a reader follows the quickstart's first example — they call the synchronous path the queue path replaced, and nothing in the document says so.

**Change**: rewrite the quickstart's first example against the queue path.

Closing this without action is a correct response.

<!-- finding id=code/ops-md/sync-quickstart axis=code action=consider priority=P3 head=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 -->

## Observations

These are accurate observations, not findings — no action is requested.

- The retry loop logs each attempt at `info` level (`src/retry-policy.ts:31` in the pre-image).

## Open questions

**[Question] Does the 30s queue timeout fit the gateway's request budget?**

The new queue path defaults to 30s — [`src/config.ts`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/src/config.ts) is where the diff sets it — where every caller it replaces used 5s. The issue is silent on timeouts, the history carries no rationale, and nothing in the repository records the gateway budget this path runs under, so whether the queue outlives it decides whether the new path times out at the caller. Whoever owns the gateway configuration can answer it; one request against staging would show it.

**Change no code for this.** Answer it, or say what would settle it.

<!-- finding id=question/queue-timeout-30s action=question head=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 -->
```

This body is the phase-1 fixture: every index entry, body-resident finding, and whole-change question carries its coordinate as a rendered fragment whose text is the unchanged coordinate, and the observations pointer is a code span. Phase 2 makes each index title link to its comment and leaves every file fragment byte-identical.

## Coordinate links

Every file coordinate the body carries is rendered by `python3 scripts/link_coordinate.py`, which owns the URL rule so no review composes a URL by hand. A coordinate the rule can express renders as a link whose visible text is the unchanged coordinate:

```markdown
anchor [`src/order.ts:47`](https://github.com/acme/payments/blob/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0/src/order.ts?plain=1#L47)
```

- an ordinary RIGHT link resolves under the base repository's canonical web URL at the reviewed full head SHA — immutable across force-pushes, readable from outside the pull request, never a branch URL or an abbreviated SHA;
- a line or range carries `?plain=1#L<line>` or `?plain=1#L<start>-L<end>`; a file anchor carries neither;
- a distinct fix site renders its own fragment and follows the anchor as `; fix` with its fragment;
- a known deleted whole-file anchor uses `--side LEFT --merge-base <pinned merge-base>` and links at that merge-base with its established pre-image path; `LEFT` lines and rename coordinates carrying `--old-path` remain code spans;
- an observation's evidence pointer stays a code span: the ledger row behind it does not record the side or revision the evidence was read at, and structured provenance remains deferred until a separate demonstrated case and bounded scope justify it.

The caller retains a publication record `{coordinate, side}` derived from the full pinned merge-base manifest (`D` establishes a deleted file's pre-image path), alongside the run's pinned `head` and `merge-base`. For both findings and questions, pass `coordinate` as `--coordinate`, `side` as `--side`, head as `--revision`, and merge-base as `--merge-base` to **both** render and check. A delta deletion alone does not establish a merge-base file. Keep this record through body fallback, payload repair, the index update and the caller report; the later audit payload-emitter implementation must consume these same fields and roles. The finder/accounting packets retain their existing grammar; the orchestrator owns this publication record.

`--revision` always remains the reviewed head. Only a bare whole-file coordinate with `LEFT` and a full 40-hex `--merge-base` selects the merge-base link. A missing merge-base with `LEFT` stays unlinked; a malformed supplied merge-base is an error. When the evidence cannot establish the correct pre-image path or revision, pass `--side UNKNOWN` with the reported whole-file coordinate and explain the missing evidence in the item: it renders a code span even when a merge-base is supplied. A supplied `--old-path` also stays unlinked; no rename reconstruction is attempted. `UNKNOWN` on a line is invalid. Omitted side retains legacy `RIGHT` semantics, so callers must carry known deletions/unknown provenance explicitly; the helper performs no repository or URL existence probes. There is no per-coordinate SHA override. Native review `commit_id` and finding/question trailer `head` remain the reviewed head; whole-file items stay body-resident and never become deleted-file line comments.

Render each fragment with the script's `render` command, and `check` a fragment already written whenever the body is assembled or updated; a non-zero exit stops the step — report the script's output and fix the inputs, never the fragment by hand. File links sit beside the comment links, not in place of them: a comment link reaches the thread, a file link reaches the code the finding was read against.

## The reviewer identity's token

Where `docs/agents/issue-tracker.md` names a reviewing app, the reviewer identity SKILL step 1 resolved is that app, and every write this review makes has to come from it: the review POST and its phase-2 body update, thread replies, thread resolutions and reopenings, and dismissals. A write left as a bare `gh api` publishes as the authenticated user instead, and the next run's prior-review lookup — keyed on the reviewer identity — then finds nothing, so every re-review restarts as a first review with no carried findings and the duplicate gate never fires.

Acquire the token in the shell invocation that makes the write, with that file's review-token command. Every write command below is written bare; where an app publishes, each of them runs inside this block:

```sh
app=$(sh -c '<review-token command>') || app=
if [ -z "$app" ] || ! GH_TOKEN=$app gh api "repos/{owner}/{repo}" --silent; then
  echo "the review-token command yielded no usable token; nothing was written"; exit 3
fi
GH_TOKEN=$app; export GH_TOKEN
<the review write this invocation makes>
```

Run the command through `sh -c` rather than expanding it in command position, where a multiword command is read as one command name under `zsh`. Name the repository in the command; never let the runner infer one from a remote, which is the fork on a fork checkout. Keep the token in the environment, never on a command line, and, as this block does, export it only once it is proved, so an unusable one leaves whatever credential the authenticated user already had in place. Acquire it in the same shell invocation as the write it covers, as the block above does: an exported variable does not survive to the next invocation, and a write run in a shell of its own publishes as the authenticated user however the previous one ended. Prove it before the first write rather than testing it for emptiness alone: a token minted against the wrong repository, or one whose installation was suspended, is non-empty and then refused on every write.

The fallback to the authenticated user belongs to identity resolution, not to publication. A command that is absent, that fails, or whose token cannot authenticate is not an error in SKILL step 1: resolve the authenticated user instead, record the fallback in the report, and review under the ordinary self-review rules above. Once the run has resolved the app, though, its prior-state matching, its duplicate gate and its event all derive from that login, so a token that stops working at publication time writes nothing and reports the unusable token. Publishing that same review as the authenticated user would leave it invisible to the next run's app-keyed lookup — the re-review would restart as a first review — and `APPROVE` or `REQUEST_CHANGES` on that user's own pull request is refused with 422 anyway.

## One review, one call

**Apply SKILL step 4's complete input freshness check before the first write.** A stale or unreadable head/base, changed evidence, or missing state stops publication until reassessed; a newly merged target requires separate explicit authority.

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
<!-- review-run workflow=v2b-7 head=<full 40-hex sha> base-ref=<branch> state=<OPEN|CLOSED|MERGED> merged=<true|false> base-sha=<full 40-hex sha> merge-base=<full 40-hex sha> context=<full 64-hex sha256> output=<full 64-hex sha256> issues=<owner/repo#n,...|none> coverage=<complete|incomplete> -->
```

Values are single tokens with no spaces; list issues sorted and comma-separated. Every SHA in a trailer is full-width, 40 hex characters — trailers are machine-read across rounds and abbreviations are ambiguous over time. Short SHAs stay fine in visible prose. `workflow=v2b-7` identifies which reviewer contract produced the run, so a later run knows whose trailer vocabulary it is reading; the trailer's pinned SHAs, explicit `state`/`merged`, and recomputed `context` are this run's identity record. Compute and check them under [`input-identity.md`](input-identity.md); a prior trailer without the digest is readable history but cannot suppress a current-contract review. Percent-encode spaces and percent signs in `base-ref`.

Before submission, save the exact prospective body and original line-comment bodies as review JSON with `body` and `comments` (`[{"body": "…"}, …]`, empty for a body-only review), and run `python3 scripts/forge_packet.py output-digest review.json`. Put the returned digest in the run trailer as `output`. The helper removes the entire run trailer from the hashed body to avoid a self-reference, preserves all other body bytes, sorts comment bodies while retaining duplicates, and hashes canonical UTF-8 JSON with SHA-256. It uses no ids or timestamps, so it works before comment ids exist. The pinned code identity covers coordinates; published comment coordinates are immutable. On non-zero exit, report the output and stop the write.

The comment URLs do not exist when the body is written, so publish in two phases: submit with the index entries carrying their rendered coordinate fragments — the phase-1 body is complete and clickable on its own — then read back the created comment URLs and prepare the final linked index. Recompute `output` from that exact final body and the **same original comment bodies sent in phase 1**, and `PUT repos/{owner}/{repo}/pulls/<n>/reviews/<review_id>` with the final body and its recomputed trailer together. Preserve every coordinate fragment byte-identically. If phase 2 fails, the phase-1 body and digest stand; do not rewrite the digest alone or derive a replacement baseline from later fetched/edited content. Subsequent replies and edits do not refresh `output`. Later runs compare current original content to this publication baseline, allowing both normal forge timestamp drift and the original index update while detecting later content changes. This digest records original output; it is not a signature or publication authority.

Questions ride inside the same review, anchored by the same ladder. A whole-change question, and any finding the ladder sent to the body, appears there in full — tag line through trailer — under `## Open questions` or under its axis in the index, with the anchor and `fix` coordinates its prose names rendered as the same fragments (Coordinate links).

## Re-review

`id` slugs the axis, the file, and the finding — `code/order-ts/swallowed-validation-error`. **Never a line number**: lines drift between rounds and the id has to survive that. One finding against the same code keeps one id across every round, which is what lets a re-review correlate it to its thread and verdict it rather than posting it again.

A candidate the verifier ruled `plausible` that the ladder admits as a question takes a `question/...` id, not the axis id it was proposed under; one the ladder records instead publishes nothing and keeps its axis id in the run report, so a later round can still correlate it. If a later round confirms it, it becomes a finding under its own axis id and the question resolves as answered. The two ids stay distinct on purpose: the record then shows a question that turned out to expose a defect, rather than a finding that silently changed shape between rounds.

A responding agent replies with a matching trailer:

```
<!-- reply to=<finding id> disposition=<implemented|already-addressed|answered|declined|needs-info|blocked> head=<full 40-hex sha> -->
```

and a re-review writes its verdict on the thread:

```
<!-- verdict on=<finding id> verdict=<fixed|accepted|obsolete|not-fixed> head=<full 40-hex sha> -->
```

`fixed` names the finding's fate, not the reply's credibility — a finding that still stands is `not-fixed`. `accepted` is how a decline you agree with gets closed, and it needs reasoning you can state in the reply that closes it. A decline is a position, not evidence: on its own it never settles a verified `must-fix`, and where its reasoning does not hold the verdict stays `not-fixed` and the finding is disputed.

## Humans without trailers

A finding or reply written by a person carries no trailer. Read it as prose, infer what it means, and treat it exactly as any other item. Never skip something for lacking a trailer, and never write a trailer on a person's behalf. The trailers speed up the agent path; they do not gate it.

## Thread handling

Read prior activity from step 1's normalized packet: `reviews` carries review ids, authors, bodies, commit and timestamps; `threads` carries node ids, `is_resolved`, original coordinates, and every comment/reply with numeric `id`, `review_id` and `reply_to`; `pr_comments` carries the full PR discussion. Use `original_line` when a push has out-dated a thread. These fields serve every round. The complete paginated collection and freshness calls live in `SKILL.md`; a capped ad-hoc fetch is not a substitute.

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

Apply [`input-identity.md`](input-identity.md)'s duplicate gate. Head/status equality alone never suppresses a review. When any identity, intent, guidance, discussion or thread input changed, complete the assessment even if the resulting aggregate status stays the same.

Publish one new review for the assessed current inputs, with every **new** eligible finding and the current summary, even at unchanged head/status. Correlate standing findings by their durable ids and reply on existing threads; do not repost them. Preserve new findings from either axis even when another standing `must-fix` already determines `Changes Requested`. A changed status likewise publishes the new summary and authorized event. If full identity and later-state checks pass but this run has already discovered new eligible material, it also publishes: the duplicate shortcut cannot discard findings. An exact duplicate with no new material is reported by its existing URL, without a write.

- Dismiss a superseded review only where it carried a gate the new event cannot replace. A later `APPROVE` clears an earlier `REQUEST_CHANGES`; a `COMMENT` supersedes another `COMMENT` with no dismissal needed, and cannot clear a standing `APPROVED` or `CHANGES_REQUESTED`.

  ```sh
  gh api --method PUT repos/{owner}/{repo}/pulls/<n>/reviews/<review_id>/dismissals -f message='...' -f event=DISMISS
  ```

  A branch protection rule can refuse this. A `403` is an answer, not something to retry: write the new status in the body and report the stale gating state as needing an authorized actor.
