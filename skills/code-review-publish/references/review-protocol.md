# Review protocol

`resolve-review` carries the addresser's side of this protocol in its own `references/addressing-protocol.md`; a change to the shared vocabulary lands in both files.

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
- `[Code]` covers documented repository standards and code smells, which are judgement calls.
- `[Requirements]` covers missing, partial, incorrect, or unrequested behavior against the originating spec.
- A finding is blocking unless it says otherwise. Unmarked means the change should not merge until this is settled, and that is what the author reads it as.
- Evidence: the `file:line` and concrete behavior; cite the documented rule or originating requirement when one applies.
- A **Change**: line naming the concrete edit.
- Six lines or fewer above the trailer. Whoever acts on it, human or agent, acts from this comment alone.
- The trailer is an HTML comment: invisible in the rendered view, present in the raw body via `gh api`.

The current `review-code-publish` contract labels findings `[P0]` through `[P3]` and then `[must-fix]` or `[consider]`; its trailers carry matching `priority`, `action`, and `blocking` fields. When addressing those findings, map `[must-fix]` or `action=must-fix blocking=true` to blocking, and `[consider]` or `action=consider blocking=false` to the optional semantics below. A visible action/trailer mismatch is malformed feedback to clarify rather than silently choosing one.

For legacy reviews, `[Suggestion]` is the one severity marker for a finding worth saying and not worth blocking on — a nice-to-have, a preference, or food for thought the author may close unactioned. It goes after the axis tag and rides the trailer:

```markdown
**[Code] [Suggestion] `formatDate` could read the locale from context**

...

<!-- finding id=code/format-date/locale-from-context severity=optional head=a1b2c3d -->
```

Mark it where it belongs and nowhere else. Every finding labelled optional is a review that blocks nothing; none labelled is a review where a nit stops a merge.

The `id` slugs the axis (`code` or `requirements`), file, and finding title — never a line number, since lines drift between rounds and the id has to survive that. One finding against the same code keeps one id across every round. Prior findings with legacy `standards` or `spec` ids retain those ids on re-review; renaming one would break its thread correlation.

## Reply comments

`resolve-review` replies once per item:

```markdown
**Implemented** in `9f1e0aa` — extracted `assertOrderShape`; both call sites use it. `pnpm test` green at `9f1e0aa`.

<!-- reply to=code/order-ts/duplicated-validation disposition=implemented head=9f1e0aa -->
```

The bold word is the disposition:

| Disposition | Means | The reply carries |
| --- | --- | --- |
| `implemented` | change made | what changed, the check and the head it passed at, the commit |
| `already-addressed` | the code already satisfied it | where |
| `answered` | a question resolved, no code change | the answer |
| `declined` | correct to leave as-is, or not this change's job | the reason: technical for a blocking finding, scope or preference for an optional one |
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

An optional finding is a proposal, and the addresser's job on one is to decide it rather than to perform it. Implementing takes an affirmative reason — a real defect underneath it, a documented standard behind it, or code this change already touches — and absent one the finding is declined. Implementing on reflex is how a reviewer's passing preference becomes unrequested change in someone else's pull request, widening the diff every later reader has to verify and burying the work the pull request exists for. Declining is an ordinary outcome there, not a failure to engage, and it costs a sentence: an optional decline has to be honest, where a blocking one has to be persuasive.

A question is not a finding. It carries no axis, counts toward no axis total, and never counts toward the round cap — an unanswered question is not a disputed point, just an open one. Re-reviews link to the same open question rather than posting it again. It keeps the review at `Needs Information` until someone answers it, the reviewer withdraws it as irrelevant, or the reviewer determines its answer cannot change the verdict; it never ages into approval. An unattended loop stops and reports what it is waiting for. Answer a line question with `answered` and resolve its thread; answer a whole-change question through the general-comment path above. A question that turns out to expose a defect becomes a finding in the next review, with its own id.

Questions still open at the end of a run go under `## Open questions` in the summary, so whoever picks the pull request up next sees what is waiting on them.

## Thread state

A thread stays open only while it still asks something of someone. Both skills close threads, and either may reopen one.

Resolve a thread when:

- the reviewer verdicts it `fixed`, `accepted`, or `obsolete`;
- its work is done and needs no reviewer verdict — a question answered, a finding already addressed by code the reviewer can see;
- it went outdated or stopped being relevant — the file was deleted, the approach was replaced, the finding was withdrawn.

A `declined` reply does not resolve its own thread. Declining states a position; the reviewer accepting it is what settles the disagreement, and closing early would hide a live dispute from the round cap.

`resolve-review` resolves each thread together with its own confirmed reply and live change. Its ordered write pass posts an item's reply and then resolves that item's thread before moving to the next item, never as a detached sweep of resolutions after the replies. Threads sitting at `needs-info` or `blocked` stay open.

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
- a short paragraph, two or three sentences, reading the findings as a whole: what the change does, what drives the status, and what to deal with first. It generalizes — a pattern several findings share, one fault behind them, the shape of the risk — rather than reciting them, and it names at most the two or three findings that decide the outcome. A review with one finding or none says that in a sentence;
- the reviewed head SHA and the comparison base;
- an index of findings, ordered within each axis worst first — blocking before optional, and within each of those whatever the author should reach for first. Each entry carries the axis tag, `[Suggestion]` where it applies, the title, and a link to its line comment. Ordering is what makes the top of the index the place to start, so nothing separately announces the worst finding;
- per-axis counts split blocking and optional;
- re-reviewing: the prior head, and one verdict line per prior finding;
- `## Disputed`, when any finding has hit the cap;
- `## Open questions`, when any question is unanswered, linking each line question and carrying the stable id for each whole-change question.

The line comment is where a finding lives; the summary orients, indexes, and totals. The paragraph is the one place that generalizes, and it earns its space by saying what no single finding says; outside it, restating finding text makes the human read everything twice.

Together, on a review whose event cannot carry the status:

```markdown
**Changes Requested (advisory)** — 1 blocking finding.

Requirements: Passed. Code: Findings — 1 blocking, 2 optional.

Retries are the one thing to fix here: the new path reorders requests the queue downstream assumes are ordered. The two optional findings are the same duplicated shape either side of it, and clear up with it. The rest of the change reads clean against both axes.
```

Where the forge event carries the status, the axis line opens the body instead, with the paragraph following it.

A batched review creates its body and its comments in one call, so the comment URLs do not exist yet when that body is written. Publish in two phases: submit the review with a body carrying the index by `file:line`, read the created comment URLs back, then update the review body with the links. Where the second phase fails, the `file:line` index still stands on its own — never block the review on it.

## Addressing summary

Before closing the round, reconcile the pull request title and description against the resulting diff and originating spec. Edit either field when it no longer describes the change accurately or completely; preserve issue links and still-valid context, and describe the resulting behavior rather than the review chronology. An already-accurate field stays unchanged. In the summary comment, mention only fields actually edited during the round; omit unchanged fields even when the other field changed.

Resolving every thread leaves a pull request looking untouched. The forge collapses resolved threads, so a round that answered everything and a round that did nothing render the same, and the reviewer has to expand each one to find out which. `resolve-review` closes a round with one general pull-request comment:

```markdown
**Addressed** at `5844a3c` — 2 implemented, 1 answered, 1 declined.

- `implemented` — [verdict vocabulary](url), [dismissal authority](url)
- `answered` — `question/retry-order`: retries preserve request order
- `declined` — [axis tag rename](url), open for your verdict

`pnpm test` green at `5844a3c`. Every other thread resolved.

<!-- reply to=question/retry-order disposition=answered head=5844a3c -->
<!-- addressed head=5844a3c -->
```

- the head it addressed at, and the commits carrying the changes;
- counts by disposition, each item linked to its thread;
- a file coordinate the summary names outside a linked thread item rendered as an immutable link at the addressed full head SHA — `https://<host>/<owner>/<repo>/blob/<full sha>/<path>?plain=1#L<line>`, `#L<start>-L<end>` for a range, neither the query nor the fragment for a whole file — with the code-formatted coordinate as its text, never a branch URL or a bare code span;
- what still needs someone: `declined` awaiting a verdict, `needs-info` awaiting an answer, `blocked` items and their blocker;
- each check with the head and input state it establishes, any failure that decides the outcome, and any remaining verification gap;
- where the forge will not route a re-review request and the reviewing identity is not an app, one line asking for one by mentioning that identity;
- whether the round is finished or waiting — the sentence the reviewer would otherwise open every thread to infer.

One comment per round, never one per item. Whole-change question answers are the only per-item detail in this comment because those questions have no threads: give each a concise answer entry and its own reply trailer in the summary. Every other item's detail stays in its thread, and the summary only indexes it. Re-running at the same head updates that comment rather than posting a second.

Every round ends by asking the identity whose review it addressed to look again. That is the counterpart to the reviewer's status — the reviewer says where the change stands, the addresser says it is ready to be looked at again — and it belongs in their queue rather than waiting to be noticed.

Where the forge routes review requests, make the ask a review request. A re-request does not clear an earlier `REQUEST_CHANGES`; only a later review from that identity, or a dismissal, does.

Where the forge will not route one — it has no review requests at all, or it refuses this one because the identity to ask is the pull request's own author — the summary carries the ask instead, as a line mentioning that identity: `Re-requesting review from @<login>.` The mention notifies them, which is what the request was for. An app reviewer is the exception that takes neither form: GitHub routes a review request only to a user or a team, and `@<app>[bot]` notifies nobody, so where the review being addressed carries REST `user.type` of `Bot`, make no request and write no mention — the orchestrator that runs the app triggers its next review. Settle which form applies before writing the summary, by that `user.type` and then by comparing that identity's login against the pull request's author and nothing else, and never report the forge's refusal on the pull request: the ask is the signal a reader wants, and a paragraph about a rejected API call is noise around it.

## Humans in the loop

Trailers speed up the agent path; they never gate it. A finding or reply written by a human carries no trailer — read it as prose, infer its disposition, and reply to it exactly as to any other. Never skip an item for lacking a trailer, and never address a human reviewer by writing a trailer on their behalf.

## GitHub verbs

If this repo's `docs/agents/issue-tracker.md` names a forge other than GitHub, follow that file instead.

`gh api` substitutes `{owner}` and `{repo}` from the clone, so the paths below are copy-pasteable as written.

**Posting identity**: read `docs/agents/issue-tracker.md` for **Reviewing app** and **Client id**, or an optional literal **Review-token command**. Use a literal command as-is without consulting `review-bot`, reading its login with `GH_TOKEN=$(sh -c '<review-token command>') gh api graphql -f query='{viewer{login}}' --jq .data.viewer.login`; `gh api user` is refused for an app token. A command that is absent, that fails, or whose token cannot authenticate is not an error. For an app without a literal command, invoke `review-bot`'s Resolve entry point when installed with the client id and the pull request's base repository as `<owner>/<repo>`, never the checkout's remote. Take its returned login and command verbatim. If the skill is absent or returns any `unavailable` result, or the literal command fails, resolve `gh api user --jq .login`, record the fallback reason in the report, and withhold gating. Resolution never stops the run; the publication-time stop for an unusable token is unchanged. With no app or command declared, use the authenticated user. Compare with `gh pr view <n> --json author` to detect a self-review, ignoring a trailing `[bot]` on either login.

**Resolve the pull request**: `gh pr view <n> --json number,url,author,headRefName,baseRefName,headRefOid,state,body`. `headRefOid` is the head SHA to record as reviewed. The collection block below runs this read in the same invocation and saves it as `pr.json`, so only the number `<n>` is needed before it runs.

### Collecting review activity

Every list below is a collection: reviews, inline comments, general pull-request comments, and review threads. Fetch each one completely with the block below, not with a single-page `gh api` call. A single call returns one page, and feedback on a later page silently misses the ledger. The same block also reads the pull request metadata above into `pr.json`. Run the block as one shell invocation after replacing `<owner>`, `<repo>`, and `<n>`. It is POSIX `sh` that also runs unchanged under `bash` and `zsh`.

The block writes into a fresh private directory from `mktemp -d`, one distinct file set per read. The metadata read keeps its raw output (`pr.raw.json`), stderr (`pr.stderr`), and exit status (`pr.status`), and `pr.json` is written only when `gh` exits `0` and the output is a JSON object with an integer `number` and a full 40-hex `headRefOid`. Each collection keeps its raw slurped pages (`<name>.pages.json`), `gh` stderr (`<name>.stderr`), and `gh` exit status (`<name>.status`). The block records `gh`'s status before anything reads the output, so no formatter downstream can hide a failed continuation page. The flattener runs only after `gh` exits `0`. It rejects any response that is not JSON, any GraphQL `errors` or partial `data`, and any page chain that does not end in `hasNextPage: false`. Exact repeats of one stable id collapse to one record. When one id arrives with different content, as when a comment is edited mid-fetch, the block re-reads that item with its single-item verb and keeps the fresh copy. It never drops either version silently. `<name>.json`, a flat JSON array, is written only when every page is present and valid. REST records keep every field GitHub returned. Each thread record keeps its GraphQL node `id` and adds `firstCommentId`, the numeric REST id of its first comment, read from `fullDatabaseId` or, only when that is absent, from the deprecated `databaseId`.

The last line reads `complete <dir>` with exit status `0`, or `incomplete <dir>` with exit status `1` after one `incomplete <name>: <reason>` line per failed read, `pr` included. An incomplete collection is a coverage gap: preserve the directory, report the gap, and never treat feedback missing from it as addressed. Files that did arrive in an incomplete directory are not a complete inventory. The block is not a transactional snapshot. A live pull request can gain feedback while the block runs.

```sh
d=$(mktemp -d "${TMPDIR:-/tmp}/review-activity.XXXXXX") || exit 2
cat > "$d/flatten.py" <<'PY'
import json, os, re, sys

def fail(msg, code=1):
    print(msg)
    sys.exit(code)

def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except OSError as e:
        fail("unreadable %s: %s" % (path, e), 2)
    except ValueError as e:
        fail("malformed JSON in %s: %s" % (path, e))

def rest_pages(pages):
    if not isinstance(pages, list) or not pages:
        fail("expected a non-empty array of pages")
    for page in pages:
        if not isinstance(page, list):
            fail("page is not an array")
        for rec in page:
            if not isinstance(rec, dict) or type(rec.get("id")) is not int:
                fail("record without an integer id")
            yield rec["id"], rec

def thread_node(node):
    if not isinstance(node, dict) or not isinstance(node.get("id"), str):
        fail("thread without a node id")
    first = ((node.get("comments") or {}).get("nodes") or [None])[0]
    if not isinstance(first, dict):
        fail("thread %s without a first comment" % node["id"])
    raw = first.get("fullDatabaseId")
    if raw is None:
        raw = first.get("databaseId")
    try:
        cid = int(raw)
    except (TypeError, ValueError):
        fail("thread %s without a first comment id" % node["id"])
    return node["id"], dict(node, firstCommentId=cid)

def thread_pages(pages):
    if not isinstance(pages, list) or not pages:
        fail("expected a non-empty array of pages")
    for i, page in enumerate(pages):
        if not isinstance(page, dict) or page.get("errors"):
            fail("GraphQL errors or a non-object page")
        try:
            conn = page["data"]["repository"]["pullRequest"]["reviewThreads"]
            nodes, info = conn["nodes"], conn["pageInfo"]
            more, cursor = info["hasNextPage"], info["endCursor"]
        except (KeyError, TypeError):
            fail("partial data or missing pageInfo")
        last = i == len(pages) - 1
        if not isinstance(nodes, list) or more is not (not last) or (more and not isinstance(cursor, str)):
            fail("incomplete pagination metadata on page %d" % (i + 1))
        for node in nodes:
            yield thread_node(node)

def fresh_record(kind, path):
    doc = load(path)
    if kind == "threads":
        if not isinstance(doc, dict) or doc.get("errors") or not isinstance((doc.get("data") or {}).get("node"), dict):
            fail("fresh copy %s is an error or partial data" % path)
        return thread_node(doc["data"]["node"])
    if not isinstance(doc, dict) or type(doc.get("id")) is not int:
        fail("fresh copy %s without an integer id" % path)
    return doc["id"], doc

def write(out, value):
    with open(out + ".tmp", "w", encoding="utf-8") as f:
        json.dump(value, f)
    os.replace(out + ".tmp", out)

kind, src, out, fresh_paths = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
if kind == "pr":
    doc = load(src)
    if not isinstance(doc, dict) or type(doc.get("number")) is not int \
            or not re.fullmatch(r"[0-9a-f]{40}", str(doc.get("headRefOid"))):
        fail("pull request metadata without an integer number and a full headRefOid")
    write(out, doc)
    print("pull request %d at %s" % (doc["number"], doc["headRefOid"]))
    sys.exit(0)
records = thread_pages(load(src)) if kind == "threads" else rest_pages(load(src))
seen, order, conflicts = {}, [], []
for key, rec in records:
    if key not in seen:
        seen[key] = rec
        order.append(key)
    elif json.dumps(seen[key], sort_keys=True) != json.dumps(rec, sort_keys=True) and key not in conflicts:
        conflicts.append(key)
fresh = dict(fresh_record(kind, p) for p in fresh_paths)
missing = [k for k in conflicts if k not in fresh]
if missing:
    for k in missing:
        print("conflict %s" % k)
    sys.exit(3)
flat = [fresh.get(k, seen[k]) for k in order]
write(out, flat)
print("%d records" % len(flat))
PY
owner=<owner> repo=<repo> pr=<n> incomplete=0
threads_query='query($owner:String!,$repo:String!,$pr:Int!,$endCursor:String){
  repository(owner:$owner,name:$repo){ pullRequest(number:$pr){
    reviewThreads(first:100, after:$endCursor){
      pageInfo{ hasNextPage endCursor }
      nodes{ id isResolved isOutdated path line
        comments(first:1){ nodes{ fullDatabaseId databaseId } } } } } } }'
thread_node_query='query($id:ID!){ node(id:$id){ ... on PullRequestReviewThread{
  id isResolved isOutdated path line
  comments(first:1){ nodes{ fullDatabaseId databaseId } } } } }'
collect() { # <name> <kind> <single-item path, or "thread"> <gh api arguments...>
  name=$1 kind=$2 one=$3; shift 3
  gh api --paginate --slurp "$@" > "$d/$name.pages.json" 2> "$d/$name.stderr"
  gh_rc=$?; echo "$gh_rc" > "$d/$name.status"
  if [ "$gh_rc" -ne 0 ]; then
    echo "incomplete $name: gh exited $gh_rc, see $d/$name.stderr"; incomplete=1; return
  fi
  python3 "$d/flatten.py" "$kind" "$d/$name.pages.json" "$d/$name.json" > "$d/$name.result"; rc=$?
  if [ "$rc" -eq 3 ]; then
    set --
    for id in $(sed -n 's/^conflict //p' "$d/$name.result"); do
      if [ "$one" = thread ]; then
        gh api graphql -f query="$thread_node_query" -f id="$id" > "$d/$name.fresh.$id.json" 2>> "$d/$name.stderr"
      else
        gh api "$one/$id" > "$d/$name.fresh.$id.json" 2>> "$d/$name.stderr"
      fi || { echo "incomplete $name: re-reading conflicting $id failed, see $d/$name.stderr"; incomplete=1; return; }
      set -- "$@" "$d/$name.fresh.$id.json"
    done
    python3 "$d/flatten.py" "$kind" "$d/$name.pages.json" "$d/$name.json" "$@" > "$d/$name.result"; rc=$?
  fi
  if [ "$rc" -ne 0 ]; then
    echo "incomplete $name: $(tr '\n' ' ' < "$d/$name.result")"; incomplete=1; rm -f "$d/$name.json"
  fi
}
gh pr view "$pr" --repo "$owner/$repo" --json number,url,author,headRefName,baseRefName,headRefOid,state,body \
  > "$d/pr.raw.json" 2> "$d/pr.stderr"
gh_rc=$?; echo "$gh_rc" > "$d/pr.status"
if [ "$gh_rc" -ne 0 ]; then
  echo "incomplete pr: gh exited $gh_rc, see $d/pr.stderr"; incomplete=1
elif ! python3 "$d/flatten.py" pr "$d/pr.raw.json" "$d/pr.json" > "$d/pr.result"; then
  echo "incomplete pr: $(tr '\n' ' ' < "$d/pr.result")"; incomplete=1; rm -f "$d/pr.json"
fi
collect reviews rest "repos/$owner/$repo/pulls/$pr/reviews" \
  --method GET "repos/$owner/$repo/pulls/$pr/reviews" -f per_page=100
collect inline-comments rest "repos/$owner/$repo/pulls/comments" \
  --method GET "repos/$owner/$repo/pulls/$pr/comments" -f per_page=100
collect general-comments rest "repos/$owner/$repo/issues/comments" \
  --method GET "repos/$owner/$repo/issues/$pr/comments" -f per_page=100
collect threads threads thread \
  graphql -f query="$threads_query" -f owner="$owner" -f repo="$repo" -F pr="$pr"
if [ "$incomplete" -eq 0 ]; then echo "complete $d"; else echo "incomplete $d"; exit 1; fi
```

The collections, each read from `$d/<name>.json`:

- **Pull request metadata** (`pr.json`): the object the Resolve the pull request verb returns. `headRefOid` is the head SHA, and `headRefName` the branch.
- **Reviews** (`reviews.json`): `id`, `user.login`, `state`, `commit_id`, `body`. `commit_id` is the head that review covered.
- **Inline comments** (`inline-comments.json`): `id`, `in_reply_to_id`, `user.login`, `path`, `original_line`, `line`, `body`. Cite `original_line` for location, because `line` becomes `null` once a later push outdates the comment. A reply's `in_reply_to_id` names its thread's first comment, so replies on any page correlate to a thread through `firstCommentId`.
- **General pull-request comments** (`general-comments.json`): `id`, `user.login`, `body`. A pull request is an issue, so a summary posted as a general comment lives under `issues`, not `pulls`.
- **Review threads** (`threads.json`): GraphQL only, because REST does not expose whether a thread is resolved. `id` is the thread node id needed to resolve it, `isResolved` and `isOutdated` its state, and `firstCommentId` the REST id of its first comment. `comments(first:1)` fetches only that first comment; the paginated inline-comment collection supplies every reply.

Targeted rereads stay targeted. To confirm one write or one item, read only that item, never the whole collection:

- **One review**: `gh api repos/{owner}/{repo}/pulls/<n>/reviews/<review_id>`.
- **One inline comment**: `gh api repos/{owner}/{repo}/pulls/comments/<comment_id>`, with no `<n>` in that path.
- **One general comment**: `gh api repos/{owner}/{repo}/issues/comments/<comment_id>`.

### Writing review activity

When resolution selected the reviewing app, the posting identity is that app, and the review's own writes below run as it: **One review carrying every line comment**, **Update a review body**, **Supersede or dismiss a review**, **Resolve or reopen a thread** for a thread the review settles or reopens, and **Reply to an inline comment** for a verdict it writes. The addressing round's writes stay the authenticated user: the same reply verb used for a disposition reply, **Resolve or reopen a thread** for a thread it settles or reopens, **General comment** for the addressing summary, and **Request a re-review**. Every one of those verbs is written bare below; where an app publishes, each of the review's own runs inside the block that acquires its token, and none of the addressing round's does. A review write left as a bare `gh api` publishes as the authenticated user, and the next run's prior-review lookup, keyed on that app login, then finds nothing, so every re-review restarts as a first review with no carried findings.

Acquire the token in the shell invocation that makes the write, and export it only once it is proved:

```sh
app=$(sh -c '<review-token command>') || app=
if [ -z "$app" ] || ! GH_TOKEN=$app gh api "repos/{owner}/{repo}" --silent; then
  echo "the review-token command yielded no usable token; nothing was written"; exit 3
fi
GH_TOKEN=$app; export GH_TOKEN
<the review write this invocation makes>
```

Run the command through `sh -c` rather than expanding it in command position, where a multiword command is read as one command name under `zsh`. Use the returned or literal review-token command for the pull request's base repository, never a repository inferred from the checkout's remote. Preserve the returned command's shell quoting, and quote any single quote it contains when embedding it in the single-quoted `sh -c` argument. Keep the token in the environment, never on a command line, and, as this block does, export it only once it is proved, so an unusable one leaves whatever credential the authenticated user already had in place. Acquire it in the same shell invocation as the write it covers, as the block above does: an exported variable does not survive to the next invocation, and a write run in a shell of its own publishes as the authenticated user however the previous one ended. Prove it before the first write rather than testing it for emptiness alone: a token minted against the wrong repository, or one whose installation was suspended, is non-empty and then refused on every write.

The fallback to the authenticated user belongs to identity resolution, not to publication. A command that is absent, that fails, or whose token cannot authenticate is not an error when step 1 resolves the posting identity: resolve the authenticated user instead, record the fallback reason, withhold gating, and review under the self-review rule below. Once the run has resolved the app, though, its prior-state matching and its event derive from that login, so a token that stops working at publication time writes nothing and reports the unusable token. Publishing that same review as the authenticated user would leave it invisible to the next run's app-keyed lookup, and `APPROVE` and `REQUEST_CHANGES` are refused with 422 on a pull request that user authored, while they are available to an app.

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
- **General comment**: `gh pr comment <n> --body-file -` with a heredoc. This is where an addressing summary goes; find an earlier one to update by searching the complete `general-comments.json` collection for its `addressed head=` trailer. When that collection is incomplete, run the block again before posting. If it is still incomplete, post no summary and report the gap, because an earlier summary may sit on the missing page.
- **Request a re-review**: `gh pr edit <n> --add-reviewer <login>`, or `gh api --method POST repos/{owner}/{repo}/pulls/<n>/requested_reviewers -f 'reviewers[]=<login>'`. Take `<login>` from the review being addressed. Where that review carries REST `user.type` of `Bot`, make no request and write no mention: GitHub routes a request only to a user or a team, and `@<login>` notifies an app of nothing. Otherwise, authoring the pull request is no bar to requesting one: GitHub returns 422 (`Review cannot be requested from pull request author`) only when `<login>` is the pull request's own author, or the account cannot review it. Check `<login>` against the author from `gh pr view <n> --json author` before calling, and decide the remaining choice on that comparison alone: where they match, skip the call GitHub is certain to refuse and put `Re-requesting review from @<login>.` in the summary comment instead. Who addressed the round says nothing about who authored the pull request — a maintainer reviewing and later addressing a contributor's pull request is not its author, and that request routes. Where an unforeseen 422 lands after that comment is posted, edit the comment to carry the mention rather than retrying the request or reporting the refusal.
- **Edit a comment**: `gh api --method PATCH repos/{owner}/{repo}/pulls/comments/<id> -f body='...'`; for a general comment, `repos/{owner}/{repo}/issues/comments/<id>`.
- **Update a review body**: `gh api --method PUT repos/{owner}/{repo}/pulls/<n>/reviews/<review_id> -f body='...'`. This is the second phase of a linked index — the POST that creates the review returns the comment ids its `_links` resolve from. It takes a body and nothing else, so a status change needs a new review rather than an edit to this one.
- **Supersede or dismiss a review**: a later gating event from the same identity supplies its current gate state; in particular, `APPROVE` clears an earlier `REQUEST_CHANGES`. A `COMMENT` leaves an earlier `APPROVED` or `CHANGES_REQUESTED` state standing. To clear a gate without replacing it: `gh api --method PUT repos/{owner}/{repo}/pulls/<n>/reviews/<review_id>/dismissals -f message='...' -f event=DISMISS`. Write access is the baseline, and a branch protection rule restricting who may dismiss a review can refuse it anyway — a `403` there is an answer, not something to retry.
- **Resolve or reopen a thread**: GraphQL only, no REST equivalent.

  ```sh
  gh api graphql -f query='mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -f id=<thread node id>
  gh api graphql -f query='mutation($id:ID!){ unresolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -f id=<thread node id>
  ```
