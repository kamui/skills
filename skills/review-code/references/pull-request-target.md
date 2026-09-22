# Pull-request target

Read at step 1 for a pull request, after the target kind is inferred. `SKILL.md`'s Originating issues subsection supplies the resolution order this file names.

Resolve the repository, pull request, reviewer identity, base ref and SHA, head SHA, merge-base, state, and merged state. Return `target-closed-unmerged` when the target is closed without merge: it is abandoned or rejected. Invocation permits reviewing a draft. A merged pull request is reviewable only when invoked as a retrospective or audit review; record any separately explicit merged-target publication authorization for the summary Mode line; `review-code` itself never publishes.

Before the fetch, create the pull-request private directory outside the working tree with `mktemp -d`, never a predictable shared path; step 2 reuses it. `<run-events-script>` is the absolute path of this skill's `scripts/run_events.py`, so each fetch still runs in the reviewed repository. Run every forge fetch in this file as `python3 <run-events-script> wrap --private-dir <private-dir> --event forge-fetched --data role=<role> --data connection=<connection> -- <fetch command>`, with any stdout redirect outside the wrapper. The wrapper exits with the fetch's own status and appends one timing event; exit 2 with a `run_events:` line on stderr means the wrapper could not run the fetch, which is a failed call.

Fetch the pull request, its closing issues with their comments, and its reviews, review threads, and comments as **one persisted logical collection**: run the root invocation below once (`role=root`, `connection=root`), then one continuation query per bounded connection whose `pageInfo.hasNextPage` is `true`, repeating each with the returned `endCursor` until it is `false`, and save every response as returned to its own file (`> <private-dir>/forge-1.json`, `> <private-dir>/forge-2.json`, …), a failed call included. Fetch each explicitly referenced non-closing issue from the resolution order above once with the issue query below and save it the same way. Then run `python3 scripts/forge_packet.py normalize <private-dir>/forge-*.json > <private-dir>/packet.json` exactly once and keep the packet as the private record's forge section; do not fetch these again later. The helper only normalizes the saved JSON and names a gap for every connection that did not finish; on a non-zero exit, report its output and stop the step.

The root invocation also decides whether step 2's first-review context build can run now, in the same invocation as the fetch. `<forge-packet-script>` is the absolute path of this skill's `scripts/forge_packet.py`, whose `eligibility` subcommand reads the saved root page and the local clone and prints `eligible <merge-base> <head>` only for a proven first review of an open target whose commits are both local; its docstring lists the conditions. Anything else prints `deferred: <reason>`, and step 2 keeps its current build. On `eligible` the invocation runs the first-review build with the step-2 store path and persists its stdout to `<private-dir>/context-build.out`, so the compliance diff is not read before the intent sources and requirement ledger exist. A root-query or build failure prints what failed and stops with its exit status; report it and stop the step. A supplied phase-1 packet replaces this fetch and runs neither the guard nor the early build. On GitHub, `<review-context-script>` is the absolute path of this skill's `scripts/review_context.py`:

```sh
d=<private-dir> reviewer=<reviewer-login> events=<run-events-script> packet=<forge-packet-script> context=<review-context-script>
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
python3 "$packet" eligibility "$d/forge-1.json" --reviewer "$reviewer" > "$d/early-build.txt"
rc=$?
if [ "$rc" -ne 0 ]; then echo "deferred: eligibility guard failed with exit $rc" > "$d/early-build.txt"; fi
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

`baseRepository.url` is `summary.repository_url`. Compute the merge-base locally with `git merge-base <baseRefOid> <headRefOid>`; the forge does not return it. On another forge, make the equivalent smallest set of calls.

When the packet holds any prior review, reply, or trailer-bearing comment from the reviewer identity, this run is a re-review. Match that identity with a trailing `[bot]` ignored on both sides: this packet's `author{login}` omits the `[bot]` suffix that the same app's REST records carry, so an unnormalized compare makes every app re-review look like a first review. On a match: read [`references/re-review.md`](re-review.md) now and record the prior state it names. Treat comments without trailers as first-class evidence. On every pull-request run, record every explicit deferral of a design, naming, or API-shape decision found in any participant's review comments, with its author, the comment, the surface it concerns, and the current decision the record shows; step 3 treats each as open under gate 6, not as acceptance, and publishes it only under the Recorded deferrals rule below. Pin `head`, `base`, and `merge-base` as the run identity, and record `state` and `merged` explicitly alongside them; when an orchestrator supplies phase 1 and its packet omits `merged`, that is an unrecoverable input under the rubric's Uncertainty routing — derive provisional `Incomplete` and return the request to the caller; do not infer it. Record the base repository's canonical web URL beside the run identity (`baseRepository.url` from the fetch above); it becomes `summary.repository_url` in the validator payload and is what the summary's coordinate links resolve under.

**Recorded deferrals.** Every explicit deferral recorded above stays visible in the private record with its author, the comment, the surface it concerns, and the current decision the record shows. A deferral passes gate 6 — the deferred question is open, not accepted — but an open deferral is not by itself an unanswered current-merge question. When the recorded decision accepts a preview, experimental, or otherwise pre-stable surface for this merge and postpones reconsideration to the preview period or a named later gate before stabilization, record the row and do not reopen the author's decision. Publish about a recorded deferral only when the current change crosses the deferred release boundary — it stabilizes, un-previews, or otherwise releases the surface under the repository's ordinary compatibility promise — or contradicts an applicable repository rule, which is a repository-rule finding rather than a question, or leaves a material decision presently unresolved under the Material questions rule. This rule governs the deferred question itself; a defect on the same surface that passes the admission gates is an ordinary finding. A later comment, commit, or linked change that resolves the deferred decision closes the item: the record says so and nothing publishes. A qualifying question cites the deferral's author and comment, the surface, and the current decision, and like every question is non-actionable with no priority.
