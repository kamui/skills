# Pull-request target

Read at step 1 for a pull request, after the target kind is inferred. `SKILL.md`'s Originating issues subsection supplies the resolution order this file names.

Resolve the repository, pull request, reviewer identity, base ref and SHA, head SHA, merge-base, state, and merged state. Return `target-closed-unmerged` when the target is closed without merge: it is abandoned or rejected. Invocation permits reviewing a draft. A merged pull request is reviewable only when invoked as a retrospective or audit review; record any separately explicit merged-target publication authorization for the summary Mode line; `review-code` itself never publishes.

Before the fetch, create the pull-request private directory outside the working tree with `mktemp -d`, never a predictable shared path; step 2 reuses it. `<run-events-script>` is the absolute path of this skill's `scripts/run_events.py`, so each fetch still runs in the reviewed repository. Run every forge fetch in this file as `python3 <run-events-script> wrap --private-dir <private-dir> --event forge-fetched --data role=<role> --data connection=<connection> -- <fetch command>`, with any stdout redirect outside the wrapper. The wrapper exits with the fetch's own status and appends one timing event; exit 2 with a `run_events:` line on stderr means the wrapper could not run the fetch, which is a failed call.

Fetch the pull request, its closing issues with their comments, and its reviews, review threads, and comments as **one persisted logical collection**: run the root invocation below once (`role=root`, `connection=root`), then one continuation query per bounded connection whose `pageInfo.hasNextPage` is `true`, repeating each with the returned `endCursor` until it is `false`, and save every response as returned to its own file (`> <private-dir>/forge-1.json`, `> <private-dir>/forge-2.json`, …), a failed call included. Fetch each explicitly referenced non-closing issue from the resolution order above once with the issue query below and save it the same way. Then run `python3 scripts/forge_packet.py normalize <private-dir>/forge-*.json > <private-dir>/packet.json` exactly once and keep the packet as the private record's forge section; do not fetch these again later. The helper only normalizes the saved JSON and names a gap for every connection that did not finish; on a non-zero exit, report its output and stop the step.

The root invocation also decides, mechanically, whether step 2's first-review context build can run now, as one invocation with the fetch rather than a later tool call. Its guard reads the saved root page with standard-library JSON parsing and reports `eligible` only when all of the following are established from that page and the local clone: the target is `OPEN` and not merged, with `title`, `baseRefName`, `state`, `merged`, and 40-hex `baseRefOid` and `headRefOid` present and valid; `<reviewer-login>` is known; no review, thread comment, or pull-request comment on the page is authored by that identity, compared with a trailing `[bot]` ignored; `reviews`, `reviewThreads`, `comments`, and every returned thread's `comments` connection each carry `pageInfo.hasNextPage: false` with `totalCount` equal to the nodes returned, so first-review status is proven rather than inferred from top-level exhaustion; and both pinned commits are present locally with a resolvable merge-base. Any other state prints `deferred: <reason>` and exit 0, and step 2 keeps its current build: a missing commit or unresolved merge-base defers, introducing no fetch or failure policy. On `eligible` the invocation runs the existing first-review build with the pinned merge-base and head and the step-2 store path, redirecting its stdout to `<private-dir>/context-build.out`, so the compliance diff is persisted privately rather than printed before the intent sources and requirement ledger exist; the store the build writes is the same store step 2 would build, byte for byte. A root-query failure prints the saved response and stops with the fetch's exit status; a build failure prints the build's stdout and stderr and stops with its exit status. Report either and stop the step. A supplied phase-1 packet replaces this fetch and runs neither the guard nor the early build. On GitHub, `<review-context-script>` is the absolute path of this skill's `scripts/review_context.py`:

```sh
d=<private-dir> reviewer=<reviewer-login> events=<run-events-script> context=<review-context-script>
python3 "$events" wrap --private-dir "$d" --event forge-fetched --data role=root --data connection=root -- \
gh api graphql -F owner='{owner}' -F name='{repo}' -F number=<pr> -f query='
query($owner:String!,$name:String!,$number:Int!){
  repository(owner:$owner,name:$name){ url
    pullRequest(number:$number){
      title body state merged isDraft baseRefName baseRefOid headRefOid updatedAt lastEditedAt
      baseRepository{ url }
      closingIssuesReferences(first:20){ totalCount pageInfo{ hasNextPage endCursor } nodes{ number title body url updatedAt lastEditedAt
        comments(first:100){ totalCount pageInfo{ hasNextPage endCursor } nodes{ fullDatabaseId author{login} createdAt updatedAt lastEditedAt body url } } } }
      reviews(first:100){ totalCount pageInfo{ hasNextPage endCursor } nodes{ fullDatabaseId author{login} state body submittedAt updatedAt lastEditedAt commit{oid} url } }
      reviewThreads(first:100){ totalCount pageInfo{ hasNextPage endCursor } nodes{ id isResolved isOutdated path line originalLine diffSide
        comments(first:100){ totalCount pageInfo{ hasNextPage endCursor } nodes{ fullDatabaseId author{login} body createdAt updatedAt lastEditedAt replyTo{ fullDatabaseId } pullRequestReview{ fullDatabaseId } url } } } }
      comments(first:100){ totalCount pageInfo{ hasNextPage endCursor } nodes{ fullDatabaseId author{login} body createdAt updatedAt lastEditedAt url } } } } }' > "$d/forge-1.json"
rc=$?
if [ "$rc" -ne 0 ]; then echo "root query failed with exit $rc; no early build:"; cat "$d/forge-1.json"; exit "$rc"; fi
python3 - "$d/forge-1.json" "$reviewer" > "$d/early-build.txt" <<'PY'
import json, re, subprocess, sys
root, reviewer = sys.argv[1], sys.argv[2]
sha = re.compile(r"^[0-9a-f]{40}$")
def defer(reason):
    print("deferred:", reason); sys.exit(0)
def login(value):
    value = value.get("login") if isinstance(value, dict) else value
    return (value if isinstance(value, str) else "").lower().removesuffix("[bot]")
def complete(connection):
    if not isinstance(connection, dict): return False
    info, nodes, total = connection.get("pageInfo"), connection.get("nodes"), connection.get("totalCount")
    return (isinstance(info, dict) and info.get("hasNextPage") is False and isinstance(nodes, list)
            and isinstance(total, int) and total == len(nodes))
def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")
try:
    with open(root, encoding="utf-8") as handle: page = json.load(handle)
except Exception as error: defer(f"root page unreadable ({error.__class__.__name__})")
if not isinstance(page, dict) or page.get("errors"): defer("root page carries errors")
pr = ((page.get("data") or {}).get("repository") or {}).get("pullRequest")
if not isinstance(pr, dict): defer("root page has no pullRequest")
if not login(reviewer): defer("posting identity unknown")
base, head = pr.get("baseRefOid"), pr.get("headRefOid")
if not (isinstance(base, str) and sha.match(base) and isinstance(head, str) and sha.match(head)
        and isinstance(pr.get("title"), str) and isinstance(pr.get("baseRefName"), str)
        and isinstance(pr.get("state"), str) and isinstance(pr.get("merged"), bool)):
    defer("required root fields missing or invalid")
if pr["state"] != "OPEN" or pr["merged"]: defer(f"target state {pr['state']} merged={str(pr['merged']).lower()}")
reviews, threads, comments = pr.get("reviews"), pr.get("reviewThreads"), pr.get("comments")
if not (complete(reviews) and complete(threads) and complete(comments)): defer("a review-state connection is not proven complete")
nodes = list(reviews["nodes"]) + list(comments["nodes"])
for thread in threads["nodes"]:
    replies = thread.get("comments") if isinstance(thread, dict) else None
    if not complete(replies): defer("a thread's comments are not proven complete")
    nodes.extend(replies["nodes"])
if any(isinstance(node, dict) and login(node.get("author")) == login(reviewer) for node in nodes):
    defer("prior state from the posting identity")
for name, oid in (("base", base), ("head", head)):
    if git("cat-file", "-e", f"{oid}^{{commit}}").returncode != 0: defer(f"{name} commit {oid} not present locally")
merge_base = git("merge-base", base, head)
if merge_base.returncode != 0 or not sha.match(merge_base.stdout.strip()): defer("merge-base unresolved")
print("eligible", merge_base.stdout.strip(), head)
PY
read -r verdict merge_base head < "$d/early-build.txt"
if [ "$verdict" = eligible ]; then
  python3 "$context" --merge-base "$merge_base" --head "$head" --store "$d/review-context-$head.json" \
    > "$d/context-build.out" 2> "$d/context-build.err"
  rc=$?
  if [ "$rc" -ne 0 ]; then echo "early context build failed with exit $rc:"; cat "$d/context-build.out" "$d/context-build.err"; exit "$rc"; fi
fi
cat "$d/early-build.txt"
```

Continuations run with `role=continuation`, bind `after` to the connection's `endCursor` (`-F after=<cursor>`, declared as `$after:String`), and return the same node fields and `totalCount pageInfo{ hasNextPage endCursor }` as above:

- a pull-request connection, whose name is its `connection`: `repository(owner:$owner,name:$name){ pullRequest(number:$number){ reviews(first:100,after:$after){ … } } }`, and likewise for `reviewThreads`, `comments`, and `closingIssuesReferences`;
- an issue's comments (`connection=issue-comments`): `repository(owner:$owner,name:$name){ issue(number:$issue){ number url comments(first:100,after:$after){ … } } }`;
- a thread's comments (`connection=thread-comments`): `node(id:$thread){ ... on PullRequestReviewThread { id comments(first:100,after:$after){ … } } }`;
- an explicitly referenced issue (`role=issue`, `connection=issue`): the issue shape with `number title body url updatedAt lastEditedAt` and its `comments(first:100)` connection, no `after`.

When step 3 reads current CI for the pushed head, run each CI read, such as `gh pr checks <pr>`, through the same wrapper with `--data role=ci --data connection=ci`, redirecting its stdout to a new file in `<private-dir>`.

`fullDatabaseId` is the stable numeric id the fingerprint and re-review rules use; `databaseId` is deprecated on review and review-comment types and is accepted only as a fallback. `lastEditedAt` is `null` until an object is edited. Thread resolution carries no timestamp, which the re-review reference's later-state check accounts for.

`baseRepository.url` is `summary.repository_url`. Compute the merge-base locally with `git merge-base <baseRefOid> <headRefOid>`; the forge does not return it. On another forge, make the equivalent smallest set of calls.

When the packet holds any prior review, reply, or trailer-bearing comment from the reviewer identity, this run is a re-review. Match that identity with a trailing `[bot]` ignored on both sides: this packet's `author{login}` omits the `[bot]` suffix that the same app's REST records carry, so an unnormalized compare makes every app re-review look like a first review. On a match: read [`references/re-review.md`](re-review.md) now and record the prior state it names. Treat comments without trailers as first-class evidence. On every pull-request run, record every explicit deferral of a design, naming, or API-shape decision found in any participant's review comments, with its author, the comment, the surface it concerns, and the current decision the record shows; step 3 treats each as open under gate 6, not as acceptance, and publishes it only under the rubric's Recorded deferrals rule. Pin `head`, `base`, and `merge-base` as the run identity, and record `state` and `merged` explicitly alongside them; when an orchestrator supplies phase 1 and its packet omits `merged`, that is an unrecoverable input under the rubric's Uncertainty routing — derive provisional `Incomplete` and return the request to the caller; do not infer it. Record the base repository's canonical web URL beside the run identity (`baseRepository.url` from the fetch above); it becomes `summary.repository_url` in the validator payload and is what the summary's coordinate links resolve under.
