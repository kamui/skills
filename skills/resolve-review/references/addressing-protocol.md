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

Resolve each thread together with its own confirmed reply and live change. The ordered write pass in the Thread write loop section posts an item's reply and then resolves that item's thread before moving to the next item, never as a detached sweep of resolutions after the replies. Threads sitting at `needs-info` or `blocked` stay open. A stale thread left from an earlier round is the reviewer's to close, not something the addresser inherits.

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

`pnpm test` green at `5844a3c`. Every other thread resolved.

<!-- reply to=question/retry-order disposition=answered head=5844a3c -->
<!-- addressed head=5844a3c -->
```

- the head it addressed at, and the commits carrying the changes;
- counts by disposition, each item linked to its thread;
- a file coordinate the summary names outside a linked thread item rendered as an immutable link at the addressed full head SHA — `https://<host>/<owner>/<repo>/blob/<full sha>/<path>?plain=1#L<line>`, `#L<start>-L<end>` for a range, neither the query nor the fragment for a whole file — with the code-formatted coordinate as its text, never a branch URL or a bare code span;
- what still needs someone: `declined` awaiting a verdict, `needs-info` awaiting an answer, `blocked` items and their blocker;
- each check under the Check evidence section's Reporting rule: the head and input state it establishes, any failure that decides the outcome, and any remaining verification gap;
- where the forge will not route a re-review request and the reviewing identity is not an app, one line asking for one by mentioning that identity;
- whether the round is finished or waiting — the sentence the reviewer would otherwise open every thread to infer.

One comment per round, never one per item. Whole-change question answers are the only per-item detail in this comment because those questions have no threads: give each a concise answer entry and its own reply trailer in the summary. Every other item's detail stays in its thread, and the summary only indexes it. Re-running at the same head updates that comment rather than posting a second.

Every round ends by asking the identity whose review it addressed to look again. That is the counterpart to the reviewer's status — the reviewer says where the change stands, the addresser says it is ready to be looked at again — and it belongs in their queue rather than waiting to be noticed.

Where the forge routes review requests, make the ask a review request. A re-request does not clear an earlier `REQUEST_CHANGES`; only a later review from that identity, or a dismissal, does.

Where the forge will not route one — it has no review requests at all, or it refuses this one because the identity to ask is the pull request's own author — the summary carries the ask instead, as a line mentioning that identity: `Re-requesting review from @<login>.` The mention notifies them, which is what the request was for. An app reviewer is the exception that takes neither form: GitHub routes a review request only to a user or a team, and `@<app>[bot]` notifies nobody, so where the review being addressed carries REST `user.type` of `Bot`, make no request and write no mention — the orchestrator that runs the app triggers its next review. Settle which form applies before writing the summary, by that `user.type` and then by comparing that identity's login against the pull request's author and nothing else, and never report the forge's refusal on the pull request: the ask is the signal a reader wants, and a paragraph about a rejected API call is noise around it.

## Check evidence

A **check** is one named verification: a repository command such as a focused test invocation, a suite, a linter, or a build, or a CI check run. Its **evidence** is one recorded result: the command or check-run identity, the full head SHA it ran at, its input state, the exit status or conclusion, and what it covered. Input state is a clean tree at that head, or the uncommitted source, fixtures, generated inputs, dependency and configuration changes, and relevant environment it also saw. Coverage includes skipped tests and matrix legs that did not run.

**Selecting.** For each change, choose the focused commands the repository documents for the behavior it changes and for what depends on that behavior. A test file named after a changed file is a lead, not a selection; follow the callers, fixtures, and configuration the change reaches. A documentation-only change needs a test invocation only when a documented check covers that documentation, such as a docs build or a test that reads it. Changes that share one meaningful check run it once, after the last of them is in place. Repository and caller test policy bounds every choice.

**Reusing.** A successful result stands in for a new run of the same check only when every condition holds:

- it is the same check: the same command and scope, or the same check-run identity;
- it ran at the exact full head SHA being verified, and a run on uncommitted work counts only for the commit made from exactly that tree;
- its relevant inputs and environment still match, with no uncommitted source, fixture, generated input, dependency, configuration, or relevant environment change since it ran, whatever `HEAD` says;
- it passed with the coverage the check requires.

Evidence that meets them is reused wherever the round reaches that check again. Evidence that fails any of them is not reusable.

**Invalidating.** When step 3's findings cause further changes, list the earlier evidence those changes invalidate: every check whose inputs they touch. Rerun the focused checks that cover their effects. Rerun the affected broader suite too when they touch shared dependencies or configuration, change cross-module behavior, or have uncertain reach, however many suites already ran this round. Evidence they do not reach needs no rerun and still establishes only the head and input state it ran with. The step-3 reviewer and future CI do not substitute for this verification before the publication gate.

**CI.** Before citing or reusing CI for a head, read its check runs with the Reading check runs verb below. A check run is reusable evidence only when the read is complete, its `head_sha` is the full candidate SHA, it is `completed` with conclusion `success`, and it runs the required suite or check with the required coverage. A green unrelated job, an incomplete matrix, skipped tests, and a result from a different head or merge commit establish nothing for that check. Missing evidence, including an incomplete read or an unpushed head, is unavailable, never zero work required: run the check or report the gap. This is the exact-head, same-check rule the review rubric applies to CI.

**Reporting.** Replies and the addressing summary name each check with the head and input state it establishes, such as `` `pnpm test` green at `5844a3c` ``. Keep it concise. Name any failed check that decides the outcome and any remaining verification gap. An earlier success never covers a later change it did not run against.

## Humans in the loop

Trailers speed up the agent path; they never gate it. A finding or reply written by a human carries no trailer — read it as prose, infer its disposition, and reply to it exactly as to any other. Never skip an item for lacking a trailer, and never address a human reviewer by writing a trailer on their behalf.

## GitHub verbs

If this repo's `docs/agents/issue-tracker.md` names a forge other than GitHub, follow that file instead.

`gh api` substitutes `{owner}` and `{repo}` from the clone, so the paths below are copy-pasteable as written.

**Posting identity**: `gh api user --jq .login`. This skill always writes as that identity and never as a reviewing app: an app reviews, and the replies and summary are the addresser's own. Compare with `gh pr view <n> --json author` to detect a self-review, ignoring a trailing `[bot]` on either login.

**Resolve the pull request**: `gh pr view <n> --json number,url,author,headRefName,baseRefName,headRefOid,state,body`. `headRefOid` is the head SHA to record as addressed. The collection block below runs this read in the same invocation and saves it as `pr.json`, so only the number `<n>` is needed before it runs.

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

**New since inventory**: step 6 of `resolve-review` runs the block again into a new directory, and both runs must be complete. Then list the ids that the re-fetched collections carry and step 1's did not. Leave out this round's own writes: pass each id a confirmed write created, such as a disposition reply or the round summary, as `<collection>:<id>` (for example `inline-comments:4011948515` or `general-comments:3201`). GitHub wraps each inline reply in its own empty review. The command also leaves out a review whose id is the `pull_request_review_id` of an excluded inline reply. Match on those ids, not on the author, because the reviewer and the addresser can be the same identity:

```sh
python3 - <step 1 directory> <step 6 directory> <collection>:<id>... <<'PY'
import json, sys
own = set(sys.argv[3:])
def load(d, name):
    with open("%s/%s.json" % (d, name), encoding="utf-8") as f:
        return json.load(f)
def ids(d, name):
    return {r["id"] for r in load(d, name)}
for c in load(sys.argv[2], "inline-comments"):
    if "inline-comments:%s" % c["id"] in own and c.get("pull_request_review_id") is not None:
        own.add("reviews:%s" % c["pull_request_review_id"])
for name in ("reviews", "inline-comments", "general-comments", "threads"):
    for i in sorted(ids(sys.argv[2], name) - ids(sys.argv[1], name), key=str):
        if "%s:%s" % (name, i) not in own:
            print("new %s %s" % (name, i))
PY
```

Each `new` line is feedback that arrived after the inventory, not a write this round made. It is unaddressed, and the round summary says so.

### Reading check runs

Read the check runs for one full candidate head SHA with the block below, never with a single-page call. Run it as one shell invocation after replacing `<private-dir>` with step 1's collection directory and `<sha>` with the full 40-hex head SHA. It is POSIX `sh` that also runs unchanged under `bash` and `zsh`.

```sh
d=<private-dir> sha=<sha>
case $sha in *[!0123456789abcdef]*) len=0 ;; *) len=${#sha} ;; esac
if [ "$len" -ne 40 ]; then echo "check runs need a full 40-hex head SHA, got '$sha'"; exit 2; fi
out="$d/check-runs.$sha"
rm -f "$out.json"
cat > "$d/check_runs.py" <<'PY'
import json, os, re, sys

pages_path, sha, out = sys.argv[1:4]

def fail(msg):
    print("incomplete check-runs %s: %s" % (sha, msg))
    sys.exit(1)

try:
    with open(pages_path, encoding="utf-8") as f:
        pages = json.load(f)
except OSError as e:
    print("unreadable %s: %s" % (pages_path, e))
    sys.exit(2)
except ValueError as e:
    fail("malformed JSON: %s" % e)
if not isinstance(pages, list) or not pages:
    fail("expected a non-empty array of pages")
totals, seen, order = set(), {}, []
for page in pages:
    if not isinstance(page, dict) or type(page.get("total_count")) is not int \
            or not isinstance(page.get("check_runs"), list):
        fail("page without total_count and check_runs")
    totals.add(page["total_count"])
    for run in page["check_runs"]:
        if not isinstance(run, dict) or type(run.get("id")) is not int:
            fail("check run without an integer id")
        if run["id"] not in seen:
            seen[run["id"]] = run
            order.append(run["id"])
        elif json.dumps(seen[run["id"]], sort_keys=True) != json.dumps(run, sort_keys=True):
            fail("check run %d changed during the read" % run["id"])
if len(totals) != 1:
    fail("total_count changed during the read")
total = totals.pop()
if len(order) != total:
    fail("%d of %d check runs read" % (len(order), total))

def text(value):
    return value if isinstance(value, str) else None

records = []
for run in (seen[i] for i in order):
    app, suite = run.get("app") or {}, run.get("check_suite") or {}
    link = text(run.get("details_url")) or text(run.get("html_url")) or ""
    workflow = re.search(r"/actions/runs/(\d+)", link)
    records.append(dict(
        id=run["id"], name=text(run.get("name")), head_sha=text(run.get("head_sha")),
        at_requested_head=run.get("head_sha") == sha,
        app=text(app.get("slug")) if isinstance(app, dict) else None,
        check_suite_id=suite.get("id") if isinstance(suite, dict) else None,
        workflow_run_id=int(workflow.group(1)) if workflow else None,
        status=text(run.get("status")), conclusion=text(run.get("conclusion")),
        url=text(run.get("html_url")) or text(run.get("details_url"))))
with open(out + ".tmp", "w", encoding="utf-8") as f:
    json.dump(dict(requested_sha=sha, total_count=total, check_runs=records), f)
os.replace(out + ".tmp", out)
for r in records:
    print("%s%s %s id=%d app=%s workflow_run=%s %s" % (
        "" if r["at_requested_head"] else "other-head ", r["conclusion"] or r["status"],
        json.dumps(r["name"]), r["id"], r["app"], r["workflow_run_id"], r["url"]))
print("complete %s" % out)
PY
gh api --paginate --slurp --method GET "repos/{owner}/{repo}/commits/$sha/check-runs" \
  -f per_page=100 -f filter=latest > "$out.pages.json" 2> "$out.stderr"
gh_rc=$?; echo "$gh_rc" > "$out.status"
if [ "$gh_rc" -ne 0 ]; then echo "incomplete check-runs $sha: gh exited $gh_rc, see $out.stderr"; exit 1; fi
python3 "$d/check_runs.py" "$out.pages.json" "$sha" "$out.json"
```

The block keeps the raw slurped pages (`check-runs.<sha>.pages.json`), `gh` stderr, and exit status beside the result, and removes any earlier `check-runs.<sha>.json` before reading. It writes that file only when `gh` exits `0`, every page carries `total_count` and `check_runs`, no check run changed during the read, and the distinct runs number exactly `total_count`. Each record retains `requested_sha` at the top level and, per run, `id`, `name`, `head_sha`, `at_requested_head`, the app slug, `check_suite_id`, `workflow_run_id` read from an Actions details URL, `status`, `conclusion`, and the evidence `url`; an unavailable field is null. It prints one line per run, with `other-head` before any run whose `head_sha` differs, then `complete <file>` with exit status `0`. Otherwise it prints `incomplete check-runs <sha>: <reason>` and exits `1`, and exit `2` means the SHA was not a full one or the pages could not be read. An incomplete read is unavailable evidence. `filter=latest` keeps the most recent run of each check, so a rerun's failure replaces an earlier success. Commit statuses posted outside the Checks API are not read here and stay unavailable.

### Writing review activity

- **Reply to an inline comment**: `gh api --method POST repos/{owner}/{repo}/pulls/<n>/comments/<comment_id>/replies -f body='...'`, addressing the thread's first comment id.
- **General comment**: `gh pr comment <n> --body-file -` with a heredoc. This is where an addressing summary goes; find an earlier one to update by searching the complete `general-comments.json` collection for its `addressed head=` trailer. When that collection is incomplete, run the block again before posting. If it is still incomplete, post no summary and report the gap, because an earlier summary may sit on the missing page.
- **Request a re-review**: `gh pr edit <n> --add-reviewer <login>`, or `gh api --method POST repos/{owner}/{repo}/pulls/<n>/requested_reviewers -f 'reviewers[]=<login>'`. Take `<login>` from the review being addressed. Where that review carries REST `user.type` of `Bot`, make no request and write no mention: GitHub routes a request only to a user or a team, and `@<login>` notifies an app of nothing. Otherwise, authoring the pull request is no bar to requesting one: GitHub returns 422 (`Review cannot be requested from pull request author`) only when `<login>` is the pull request's own author, or the account cannot review it. Check `<login>` against the author from `gh pr view <n> --json author` before calling, and decide the remaining choice on that comparison alone: where they match, skip the call GitHub is certain to refuse and put `Re-requesting review from @<login>.` in the summary comment instead. Who addressed the round says nothing about who authored the pull request — a maintainer reviewing and later addressing a contributor's pull request is not its author, and that request routes. Where an unforeseen 422 lands after that comment is posted, edit the comment to carry the mention rather than retrying the request or reporting the refusal.
- **Edit a comment**: `gh api --method PATCH repos/{owner}/{repo}/pulls/comments/<id> -f body='...'`; for a general comment, `repos/{owner}/{repo}/issues/comments/<id>`.
- **Resolve or reopen a thread**: GraphQL only, no REST equivalent.

  ```sh
  gh api graphql -f query='mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -f id=<thread node id>
  gh api graphql -f query='mutation($id:ID!){ unresolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -f id=<thread node id>
  ```

### Thread write loop

Thread replies, resolutions, and reopenings run through one loop. Write `writes.jsonl` once, into step 1's collection directory, from the ledger whose drafts step 3 checked. Put one JSON object per thread item on each line, and use the host's file-writing tool rather than a shell `echo`. That ledger is only as complete as the collection block: an item missing from an incomplete collection gets no row, and the gap stays reported.

- `id`: the ledger key, the finding id or the comment id.
- `comment_id`: the thread's `firstCommentId`; `thread_id`: its node `id` from `threads.json`.
- `body`: the drafted reply exactly as drafted, or null when this identity's reply on that item is already confirmed. A null body never excuses a missing reply.
- `action`: `resolve` for `implemented`, `already-addressed`, and `answered` items, and for a thread gone outdated or irrelevant whose work is complete; `reopen` for a thread resolved too early (the fix regressed, a later commit undid it, or a reply over-claimed), with the reply saying why; `none` for `declined`, `needs-info`, and `blocked`. Outdated is a reason to resolve, not a new disposition.
- `is_resolved` (optional): the thread's `isResolved` from `threads.json`, so an already-satisfied state is skipped rather than written again.

When ledger items share one thread, only the thread's last row carries its `action`, and the earlier rows carry `none`; the action then waits until every reply on the thread is confirmed. The action is `reopen` when any item needs the thread reopened. Otherwise it is `none` when any item is `declined`, `needs-info`, or `blocked`, and `resolve` only when every item on the thread resolves. Each item keeps its own reply row.

A review body's reply and whole-change question answers have no thread and keep their routes, the general comment and the addressing summary.

Run as one shell invocation after replacing `<private-dir>` with step 1's collection directory and `<pr>` with the pull request number:

```sh
d=<private-dir> pr=<pr>
cat > "$d/writes.py" <<'PY'
import hashlib, json, os, re, sys

d, cmd, args = sys.argv[1], sys.argv[2], sys.argv[3:]
WRITES, RESULTS = os.path.join(d, "writes.jsonl"), os.path.join(d, "write-results.jsonl")
RAW = os.path.join(d, "write-responses")
FIELDS = ("id", "comment_id", "thread_id", "body", "action")
MUTATION = {"resolve": "resolveReviewThread", "reopen": "unresolveReviewThread"}
READ = ("query($id:ID!){ viewer{ login } node(id:$id){ ... on PullRequestReviewThread{ isResolved "
        "comments(last:100){ pageInfo{ hasPreviousPage } nodes{ fullDatabaseId databaseId url body "
        "author{ login } replyTo{ fullDatabaseId databaseId } } } } } }")

def jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f.read().split("\n") if line]

def get(obj, *path):
    for key in path:
        obj = obj.get(key) if isinstance(obj, dict) else None
    return obj

def bare(login):  # REST reports an app as `name[bot]`, GraphQL as `name`
    return login[:-5] if isinstance(login, str) and login.endswith("[bot]") else login

def number(comment):
    raw = get(comment, "fullDatabaseId")
    try:
        return int(get(comment, "databaseId") if raw is None else raw)
    except (TypeError, ValueError):
        return None

def op(row, step):  # (target, body digest) of a required write, or None
    if step == "reply":
        body = row["body"]
        return None if body is None else (row["comment_id"], hashlib.sha256(body.encode("utf-8")).hexdigest())
    if step == "none" or row.get("is_resolved") is (step == "resolve"):
        return None
    return (row["thread_id"], None)

def confirmed(results, row, step, key):
    return any(r["item"] == row["id"] and r["step"] == step and r["outcome"] == "confirmed"
               and [r["target"], r["body_sha256"]] == list(key) for r in results)

def append(row, i, step, kind, key, outcome, reason=None, **extra):
    rec = dict(item=row["id"], index=i, step=step, kind=kind, target=key[0] if key else None,
               body_sha256=key[1] if key else None, outcome=outcome, reason=reason, **extra)
    with open(RESULTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def validate():
    try:
        with open(WRITES, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print("unreadable writes.jsonl: %s" % e)
        sys.exit(2)
    problems, ids, threads, replies, count = [], set(), {}, set(), 0
    try:
        jsonl(RESULTS)
    except (OSError, ValueError) as e:
        problems.append("write-results.jsonl is unreadable or malformed: %s" % e)
    for n, line in enumerate(text.split("\n"), 1):
        if not line:
            continue
        count += 1
        try:
            row = json.loads(line)
        except ValueError:
            row = None
        if not isinstance(row, dict):
            problems.append("line %d: not a JSON object" % n)
            continue
        bad = ["missing %s" % k for k in FIELDS if k not in row]
        bad += ["unknown field %s" % k for k in sorted(set(row) - set(FIELDS) - {"is_resolved"})]
        if not bad:
            item, cid, tid, body, action = (row[k] for k in FIELDS)
            if not isinstance(item, str) or not item:
                bad.append("id is not a non-empty string")
            if cid is not None and (type(cid) is not int or cid <= 0):
                bad.append("comment_id is not a positive integer or null")
            if tid is not None and (not isinstance(tid, str) or not tid):
                bad.append("thread_id is not a non-empty string or null")
            if body is not None and (not isinstance(body, str) or not body):
                bad.append("body is not a non-empty string or null")
            if action not in ("resolve", "reopen", "none"):
                bad.append("action is not resolve, reopen, or none")
            if row.get("is_resolved") is not None and type(row["is_resolved"]) is not bool:
                bad.append("is_resolved is not a boolean or null")
        if not bad:
            if body is not None and (cid is None or tid is None):
                bad.append("a reply needs comment_id and thread_id")
            if action != "none" and tid is None:
                bad.append("%s needs thread_id" % action)
            if item in ids:
                bad.append("duplicate id %s" % item)
            if action != "none" and tid in threads:
                bad.append("second thread action on %s" % tid)
            elif tid in threads:
                bad.append("row on thread %s follows that thread's action on line %d" % (tid, threads[tid]))
            if body is not None and (cid, body) in replies:
                bad.append("duplicate reply to comment %s" % cid)
            ids.add(item)
            if action != "none" and tid not in threads:
                threads[tid] = n
            if body is not None:
                replies.add((cid, body))
        problems += ["line %d: %s" % (n, b) for b in bad]
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print(count)

def next_step(i, part, no_read):
    rows, results = jsonl(WRITES), jsonl(RESULTS)
    row = rows[i]
    step = "reply" if part == "reply" else row["action"]
    key = op(row, step)

    def skip(outcome, reason):
        append(row, i, step, "skip", key, outcome, reason)
        print("skip")
        sys.exit(0)
    if key is None:
        skip("skipped", {"reply": "no reply required", "none": "no thread action"}.get(step, "thread already in that state"))
    if step != "reply" and any(r["thread_id"] == row["thread_id"] and r["body"] is not None
                               and not confirmed(results, r, "reply", op(r, "reply")) for r in rows):
        skip("blocked", "reply not confirmed")
    if confirmed(results, row, step, key):
        skip("skipped", "already confirmed")
    mine = [r for r in results if r["item"] == row["id"] and r["step"] == step and r["kind"] != "skip"]
    same = [r for r in mine if [r["target"], r["body_sha256"]] == list(key)]
    attempts = lambda kind: len({r["attempt"] for r in mine if r["kind"] == kind})
    writes, last = attempts("write"), same[-1]["outcome"] if same else None
    if last == "failed":
        skip("blocked", "refused earlier; not retried")
    if last == "ambiguous" and no_read:
        skip("blocked", "reconciliation unsettled; not retried")
    if last == "ambiguous":
        tag = "%s-read%d" % (step, attempts("read") + 1)
        request = {"query": READ, "variables": {"id": row["thread_id"]}}
    elif writes >= 2:
        skip("blocked", "retry budget spent")
    elif step == "reply":
        tag, request = "reply-write%d" % (writes + 1), {"body": row["body"]}
    else:
        tag = "%s-write%d" % (step, writes + 1)
        request = {"query": "mutation($id:ID!){ %s(input:{threadId:$id}){ thread{ isResolved } } }" % MUTATION[step],
                   "variables": {"id": row["thread_id"]}}
    kind, attempt = tag.split("-")[1].rstrip("0123456789"), tag.split("-")[1]
    append(row, i, step, kind, key, "ambiguous", "attempt started; no result recorded", attempt=attempt)
    with open(os.path.join(RAW, "%d.%s.request.json" % (i, tag)), "w", encoding="utf-8") as f:
        json.dump(request, f, ensure_ascii=False)
    print(("reply %s %d" % (tag, row["comment_id"])) if tag.startswith("reply-write") else "graphql " + tag)

def refusal(rc, doc, err):
    code = re.search(r"HTTP (\d{3})", err)
    if get(doc, "errors") or (code and code.group(1)[0] == "4" and code.group(1) not in ("408", "429")):
        return "failed", "refused: " + (code.group(0) if code else "GraphQL errors")
    return "ambiguous", "exit %d without a conclusive refusal" % rc

def record(i, tag, rc):
    row = jsonl(WRITES)[i]
    step, attempt = tag.split("-")
    kind, key, want = ("read" if attempt.startswith("read") else "write"), op(row, step), step == "resolve"
    base = os.path.join(RAW, "%d.%s" % (i, tag))
    extra = dict(attempt=attempt, exit=rc, response=base + ".response.json", stderr=base + ".stderr")
    texts = []
    for path in (extra["response"], extra["stderr"]):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                texts.append(f.read())
        except OSError:
            texts.append("")
    try:
        doc = json.loads(texts[0])
    except ValueError:
        doc = None
    if kind == "read":
        node, viewer = get(doc, "data", "node"), get(doc, "data", "viewer", "login")
        nodes, earlier = get(node, "comments", "nodes"), get(node, "comments", "pageInfo", "hasPreviousPage")
        state = get(node, "isResolved")
        if rc != 0 or get(doc, "errors") or not isinstance(node, dict) or not viewer:
            outcome, reason = "ambiguous", "reconciliation read failed"
        elif step != "reply":
            outcome, reason = (("confirmed", "thread already in that state") if state is want else
                               ("absent", "thread state unchanged") if type(state) is bool else
                               ("ambiguous", "reconciliation read without isResolved"))
            extra["is_resolved"] = state
        elif not isinstance(nodes, list) or type(earlier) is not bool:
            outcome, reason = "ambiguous", "reconciliation read without comments or pageInfo"
        else:
            match = [c for c in nodes if bare(get(c, "author", "login")) == bare(viewer)
                     and number(get(c, "replyTo")) == row["comment_id"] and get(c, "body") == row["body"]]
            if match:
                outcome, reason = "confirmed", "matching reply already posted"
                extra.update(url=match[-1].get("url"), created_id=number(match[-1]))
            elif not earlier:
                outcome, reason = "absent", "no matching reply on the thread"
            else:
                outcome, reason = "ambiguous", "thread has comments before the 100 read"
    elif step == "reply":
        if rc == 0 and type(get(doc, "id")) is int and isinstance(get(doc, "html_url"), str) \
                and get(doc, "in_reply_to_id") == row["comment_id"]:
            outcome = "confirmed"
            reason = None if doc.get("body") == row["body"] else "returned body differs from the request"
            extra.update(url=doc["html_url"], created_id=doc["id"])
        elif rc == 0:
            outcome, reason = "ambiguous", "exit 0 without id, html_url, and in_reply_to_id"
        else:
            outcome, reason = refusal(rc, doc, texts[1])
    else:
        state = get(doc, "data", MUTATION[step], "thread", "isResolved")
        extra["is_resolved"] = state
        if rc == 0 and state is want:
            outcome, reason = "confirmed", None
        elif rc == 0 and type(state) is bool:
            outcome, reason = "failed", "returned isResolved %s" % json.dumps(state)
        elif rc == 0:
            outcome, reason = "ambiguous", "exit 0 without isResolved"
        else:
            outcome, reason = refusal(rc, doc, texts[1])
    append(row, i, step, kind, key, outcome, reason, **extra)
    print("%s %s %s: %s%s%s" % (row["id"], step, kind, outcome, "" if reason is None else " (%s)" % reason,
                                " " + extra["url"] if extra.get("url") else ""))

def summary():
    results, done, idle, unresolved = jsonl(RESULTS), 0, 0, []
    for row in jsonl(WRITES):
        for step in ("reply", row["action"]):
            key = op(row, step)
            if key is None:
                idle += 1
            elif confirmed(results, row, step, key):
                done += 1
            else:
                last = ([r for r in results if r["item"] == row["id"] and r["step"] == step] or [{}])[-1]
                unresolved.append("unresolved %s %s: %s%s%s" % (
                    row["id"], step, last.get("outcome", "not attempted"),
                    " (%s)" % last["reason"] if last.get("reason") else "",
                    ", see %s" % last["stderr"] if last.get("stderr") else ""))
    print("writes: %d confirmed, %d not required, %d unresolved" % (done, idle, len(unresolved)))
    for line in unresolved:
        print(line)
    sys.exit(1 if unresolved else 0)

if cmd == "validate":
    validate()
elif cmd == "next":
    next_step(int(args[0]), args[1], args[2:] == ["--no-read"])
elif cmd == "record":
    record(int(args[0]), args[1], int(args[2]))
else:
    summary()
PY
cat > "$d/write-loop.sh" <<'SH'
d=$1 pr=$2
w() { python3 "$d/writes.py" "$d" "$@"; }
mkdir -p "$d/write-responses" || exit 2
n=$(w validate); rc=$?
if [ "$rc" -eq 1 ]; then echo "$n"; echo "writes.jsonl refused; nothing was written"; exit 3; fi
if [ "$rc" -ne 0 ]; then echo "$n"; exit 2; fi
i=0
while [ "$i" -lt "$n" ]; do
  for part in reply action; do
    after=
    while :; do
      next=$(w next "$i" "$part" $after) || exit 2
      set -- $next
      [ "$1" = skip ] && break
      base="$d/write-responses/$i.$2"
      if [ "$1" = reply ]; then
        gh api --method POST "repos/{owner}/{repo}/pulls/$pr/comments/$3/replies" --input "$base.request.json" \
          > "$base.response.json" 2> "$base.stderr"
      else
        gh api graphql --input "$base.request.json" > "$base.response.json" 2> "$base.stderr"
      fi
      w record "$i" "$2" "$?" || exit 2
      case $2 in *-read*) after=--no-read ;; *) break ;; esac
    done
  done
  i=$((i + 1))
done
w summary
SH
sh "$d/write-loop.sh" "$d" "$pr"
```

The loop validates the whole file before its first write. A row that is not a JSON object, lacks or adds a field, has a mistyped value, lacks an id its operation needs (a reply needs `comment_id` and `thread_id`, a thread action needs `thread_id`), repeats an id, a reply body to one comment, or an action on one thread, or puts any row after its thread's action row refuses the file. The loop then prints one line per violation and `writes.jsonl refused; nothing was written`, and exits 3. Otherwise it takes items in file order, one write at a time. It posts the reply when `body` is non-null and performs the thread action only after every reply on that thread is confirmed; a thread with no reply to post leaves the action to run directly. Bodies travel as JSON request files through `--input` and are never evaluated or interpolated as shell, so multiline text, quotes, backslashes, Unicode, and trailing newlines arrive unchanged. A failed item does not stop the items after it.

Each attempt keeps its request, raw response, and stderr under `write-responses/`. Before its `gh` call it appends a started row to `write-results.jsonl`, and after the call a compact result row: item, step, kind (`write`, `read`, or `skip`), target, body digest, exit, outcome, reason, returned URL, created comment id or `isResolved`, and the file paths. A reply is `confirmed` only when the response carries an integer `id`, an `html_url`, and an `in_reply_to_id` equal to the target comment. A thread action is `confirmed` only when it returns the requested `isResolved`, and a returned opposite state is `failed`. An exit 0 without those fields is `ambiguous`. A non-zero exit is `failed` for GraphQL errors or an HTTP 4xx refusal other than 408 or 429, and `ambiguous` otherwise. A thread action while any reply on its thread is not confirmed is recorded `blocked` and checked again on a rerun, and an action already in the requested state or `none` is `skipped`. The loop prints one line per attempt, then `writes: <n> confirmed, <n> not required, <n> unresolved` with one `unresolved` line per required operation that is not confirmed. It exits 0 only when none is unresolved and 1 otherwise; an all-skipped or already-confirmed run exits 0. Exit 2 means the loop could not run.

After reading the results, reconcile by running the same block again. It re-validates and skips every confirmed operation, matching item, target, and exact body digest, so an earlier confirmation never covers a changed body or target. An attempt with a started row and no result row, as when the loop is interrupted mid-write, counts as `ambiguous`. For an operation whose last attempt was `ambiguous`, it first reads that thread's `isResolved`, the posting identity (`viewer`), and the thread's last 100 comments. A reply from that identity to the target comment with the exact body, stable trailer included, or the requested thread state confirms the operation without writing; that identity match ignores a trailing `[bot]`, which REST carries and GraphQL omits for the same app. A read showing neither permits the single retry of that operation alone. A failed read, or a thread with comments before the window, stays `ambiguous` with nothing retried. Each operation has at most two write attempts across every run against one results file, and a `failed` refusal is not retried. A reply confirmed before a failed action is never posted again, and a reply confirmed on a rerun is followed by its still-required action in the same run. Report every `unresolved` line as a reply or thread that failed to publish; never claim it closed.
