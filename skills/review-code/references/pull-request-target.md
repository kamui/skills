# Pull-request target

Read at step 1 for a pull request, after the target kind is inferred. `SKILL.md`'s Originating issues subsection supplies the resolution order this file names.

Resolve the repository, pull request, posting identity, base ref and SHA, head SHA, merge-base, state, and merged state. Return `target-closed-unmerged` when the target is closed without merge: it is abandoned or rejected. Invocation permits reviewing a draft. A merged pull request is reviewable only when invoked as a retrospective or audit review; record any separately explicit merged-target publication authorization for the summary Mode line; `review-code` itself never publishes.

Fetch the pull request, its closing issues with their comments, and its reviews, review threads, and comments as **one persisted logical collection**: run the root query below once, then one continuation query per bounded connection whose `pageInfo.hasNextPage` is `true`, repeating each with the returned `endCursor` until it is `false`, and save every response as returned to its own file (`> forge-1.json`, `> forge-2.json`, …), a failed call included. Fetch each explicitly referenced non-closing issue from the resolution order above once with the issue query below and save it the same way. Then run `python3 scripts/forge_packet.py normalize forge-*.json > packet.json` exactly once and keep the packet as the private record's forge section; do not fetch these again later. The helper only normalizes the saved JSON and names a gap for every connection that did not finish; on a non-zero exit, report its output and stop the step. On GitHub:

```sh
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
      comments(first:100){ totalCount pageInfo{ hasNextPage endCursor } nodes{ fullDatabaseId author{login} body createdAt updatedAt lastEditedAt url } } } } }' > forge-1.json
```

Continuations bind `after` to the connection's `endCursor` (`-F after=<cursor>`, declared as `$after:String`) and return the same node fields and `totalCount pageInfo{ hasNextPage endCursor }` as above:

- a pull-request connection: `repository(owner:$owner,name:$name){ pullRequest(number:$number){ reviews(first:100,after:$after){ … } } }`, and likewise for `reviewThreads`, `comments`, and `closingIssuesReferences`;
- an issue's comments: `repository(owner:$owner,name:$name){ issue(number:$issue){ number url comments(first:100,after:$after){ … } } }`;
- a thread's comments: `node(id:$thread){ ... on PullRequestReviewThread { id comments(first:100,after:$after){ … } } }`;
- an explicitly referenced issue: the issue shape with `number title body url updatedAt lastEditedAt` and its `comments(first:100)` connection, no `after`.

`fullDatabaseId` is the stable numeric id the fingerprint and re-review rules use; `databaseId` is deprecated on review and review-comment types and is accepted only as a fallback. `lastEditedAt` is `null` until an object is edited. Thread resolution carries no timestamp, which the re-review reference's later-state check accounts for.

`baseRepository.url` is `summary.repository_url`. Compute the merge-base locally with `git merge-base <baseRefOid> <headRefOid>`; the forge does not return it. On another forge, make the equivalent smallest set of calls.

When the packet holds any prior review, reply, or trailer-bearing comment from the posting identity, this run is a re-review: read [`references/re-review.md`](re-review.md) now and record the prior state it names. Treat comments without trailers as first-class evidence. On every pull-request run, record every explicit deferral of a design, naming, or API-shape decision found in any participant's review comments, with its author, the comment, the surface it concerns, and the current decision the record shows; step 3 treats each as open under gate 6, not as acceptance, and publishes it only under the rubric's Recorded deferrals rule. Pin `head`, `base`, and `merge-base` as the run identity, and record `state` and `merged` explicitly alongside them; when an orchestrator supplies phase 1 and its packet omits `merged`, that is an unrecoverable input under the rubric's Uncertainty routing — derive provisional `Incomplete` and return the request to the caller; do not infer it. Record the base repository's canonical web URL beside the run identity (`baseRepository.url` from the fetch above); it becomes `summary.repository_url` in the validator payload and is what the summary's coordinate links resolve under.
