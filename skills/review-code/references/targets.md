# Targets

Read when pinning a pull request, range, or working-tree target.

## Pull request

Resolve originating issues from closing references, then other explicit PR-body links, user-supplied issues/specs, then unique branch or commit references. Use every clearly relevant issue. With none, use the change description and report issue alignment unavailable; a required missing issue is an `issue-required` material question, not a stop or coverage gap alone.

Resolve the repository, pull request, reviewer identity, base ref and SHA, head SHA, merge-base, state, and merged state. Return `target-closed-unmerged` when the target is closed without merge: it is abandoned or rejected. Invocation permits reviewing a draft. A merged pull request is reviewable only when invoked as a retrospective or audit review; its record carries the retrospective Mode line, and `review-code` never publishes.

Before the fetch, create the pull-request private directory outside the working tree with `mktemp -d`, never a predictable shared path; context construction reuses it. Fetch the pull request, its closing issues with their comments, and its reviews, review threads, and comments as **one persisted logical collection**, running in the reviewed repository against the pull request's base repository:

```sh
python3 scripts/forge_packet.py fetch --repo <owner>/<repo> --pr <pr> --dir <private-dir> [--issue <reference> ...]
```

Pass each explicitly referenced non-closing issue from the resolution order above that you already know, such as a user-supplied issue or a unique branch or commit reference, as `--issue <number>` or `--issue <owner>/<repo>#<number>`; one already among the closing issues is skipped. The helper follows every connection to its last page, saves each response, and writes `<private-dir>/packet.json`, the private record's forge section. It prints the packet's path, whether it is complete, and one `gap` line for every connection that did not finish. When the packet's pull-request body links further non-closing issues, run the same command once more with only those `--issue` values: it fetches just those and rewrites `packet.json`. Do not fetch these again later. On a non-zero exit, report its output and stop the step.

When inspection reads current CI for the pushed head, such as with `gh pr checks <pr>`, save its output to a new file in `<private-dir>`.

Compute the merge-base locally with `git merge-base <base SHA> <head SHA>` from the packet's `pr`; the forge does not return it. On another forge, make the equivalent smallest set of calls and save them as the same packet. Build the context store once in the same directory with `python3 scripts/review_context.py --merge-base <merge-base> --head <head> --store <private-dir>/review-context.json`; a re-review adds `--base-ref <base> --prior-head <prior head>`.

When the packet holds any prior review, reply, or trailer-bearing comment from the reviewer identity, this run is a re-review. Match that identity with a trailing `[bot]` ignored on both sides: this packet's `author{login}` omits the `[bot]` suffix that the same app's REST records carry, so an unnormalized compare makes every app re-review look like a first review. On a match: read [`prior-state.md`](prior-state.md) now and record the prior state it names. Treat comments without trailers as first-class evidence. On every pull-request run, record every explicit deferral of a design, naming, or API-shape decision found in any participant's review comments, with its author, the comment, the surface it concerns, and the current decision the record shows; inspection treats each as open under the intent rule, not as acceptance, and publishes it only under the Recorded deferrals rule below. The packet and store pin `head`, `base`, `merge-base`, `state`, `merged`, and the base repository URL that coordinate links resolve under as the run identity, and the finalizer takes them from there; when an orchestrator supplies phase 1 and its packet omits `merged`, that is an unrecoverable input under the rubric's Questions, observations, and gaps — derive provisional `Incomplete` and return the request to the caller; do not infer it.

### Recorded deferrals

Every explicit deferral recorded above stays visible in the private record with its author, the comment, the surface it concerns, and the current decision the record shows. A deferral leaves intent unsettled — the deferred question is open, not accepted — but an open deferral is not by itself an unanswered current-merge question. When the recorded decision accepts a preview, experimental, or otherwise pre-stable surface for this merge and postpones reconsideration to the preview period or a named later gate before stabilization, record the row and do not reopen the author's decision. Publish about a recorded deferral only when the current change crosses the deferred release boundary — it stabilizes, un-previews, or otherwise releases the surface under the repository's ordinary compatibility promise — or contradicts an applicable repository rule, which is a repository-rule finding rather than a question, or leaves a material decision presently unresolved under the question rule. This rule governs the deferred question itself; a defect on the same surface that passes the admission gates is an ordinary finding. A later comment, commit, or linked change that resolves the deferred decision closes the item: the record says so and nothing publishes. A qualifying question cites the deferral's author and comment, the surface, and the current decision, and like every question is non-actionable with no priority.

## Range or working tree

The target stays local even when the forge supplies a base: local HEAD may be ahead of the pushed head. There is no forge packet, posting identity, or recorded review-comment deferral, and every local run is a first review. Issue retrieval still follows the repository's issue tracker.

### Resolve and pin

A range is a named ref, `<base>...<head>`, `<base>..<head>`, or “since X”. Interpret both separators as a merge-base diff. A single ref or “since X” supplies the base and uses `HEAD` as head; “the current branch” uses that branch's HEAD and the base inference below. Resolve both commits with `git rev-parse --verify <ref>^{commit}` and compute `git merge-base <base SHA> <head SHA>`. An unresolved ref or merge-base returns `target-unresolved`; never silently review another ref. A range on a dirty tree records “uncommitted changes not reviewed” in Coverage; excluded work is outside this target, not an incomplete review of its committed diff.

An explicit working-tree request, or a session prompt naming nothing or “my changes”, selects the working tree. Before snapshotting in session mode, state that it includes tracked changes and non-ignored untracked files and take scope directives, so scratch files or non-ignored secrets can be set aside with a reason before inspection and never enter a verifier brief. On a bare prompt with a dirty tree, also confirm the working-tree target. An unanswered confirmation leaves the target unresolved. One-shot callers must name a local target and its base up front; a bare one-shot invocation, including on a dirty tree, returns `target-unresolved` without a snapshot. Session mode with no human turn reports the ask and stops if the target or base remains unresolved.

For a branch or working tree, resolve the base in this order:

1. The caller's explicit base. A detached HEAD requires this; without it, session asks and one-shot returns `target-unresolved`.
2. The base of the branch's open pull request (`gh pr view <branch> --json state,baseRefName,url`, `OPEN` only). Report the PR URL as the base source; neither fetch its review packet nor substitute its pushed head for local HEAD.
3. The remote's default branch, then `origin/HEAD` when set.

For a short base branch name (explicit or inferred), prefer `origin/<base>` over a possibly stale local `<base>`; an explicit SHA or fully qualified ref keeps its exact meaning. Pin the resolved base SHA and record which source supplied it. If the current branch is the resolved base branch, set base to real `HEAD`: a working-tree review then contains only uncommitted changes. With no resolvable base, session asks before falsification and stops if unanswered; one-shot returns `target-unresolved`. A failed optional lookup falls through to the next source.

### Snapshot and context

For a working tree, record real `HEAD`, compute its merge-base with the resolved base, and create a private directory outside the working tree with `mktemp -d`. An unborn HEAD returns `snapshot-failed`. Run once:

```sh
python3 scripts/review_context.py --worktree --merge-base <pinned merge-base> --store <private-dir>/review-context.json
```

This is also the shared context build: retain its output and store and do not snapshot or build again there. A non-zero exit is reported with the script's output: `snapshot-failed` when named by the snapshot operation, otherwise `script-failure`. Its `snapshot` section's `head` is the run head. A working-tree snapshot with an empty manifest and no dirty submodule content returns `nothing-to-review`. An empty explicitly requested range can still produce a record with an empty ledger.

The snapshot leaves the real index, refs, and working files unchanged, and working files win over staging. Submodules are gitlinks at their checked-out commits; dirty submodule content is unreviewed and must be named under Coverage gaps, making coverage incomplete unless the user deliberately set it aside with a reason.

Snapshots are unreferenced loose objects that `git gc --prune=now` can remove; the saved record retains snapshot identity and the manifest after that. Refs under `refs/review-code/session/` are leftovers from earlier versions of this skill; report them and delete them with `git update-ref -d` only on the user's authorization.

### Description and record inputs

Read real commit messages with `git log --reverse --format='%H%n%B' <merge-base>..<real head>`. For a range, real head is its pinned head; for a snapshot it is `source_head`, so no snapshot commit enters the description. Save each raw message at `commit-<sha7>` and cite a promise as `commit-<sha7>/"<quoted phrase>"`. Uncommitted changes supply no description text.

Resolve issues from user specs and then a unique branch-name or real commit-message reference, following `docs/agents/issue-tracker.md` when present. Read each relevant issue and its comments once and preserve the inputs for the ledger. With no issue or spec, use the commit messages; with no messages either, the ledger is empty and `Issue fit` names no source. A required-but-unresolved issue follows target pinning's material-question routing, not a stop.

A local target has no packet digest. In the composition, a range names `run.target_kind: range` and `target`, the range as written; both local targets name `base_ref`, `base_sha`, `issues`, `specs` and `change_description`, the saved real commit messages byte for byte; the finalizer derives the rest of the run identity. Omit `repository_url` so coordinates stay code spans, including fix sites and deleted files; unpushed commits must not become broken forge links. Retain base source and any base-inference PR URL in the run's private identity and Coverage prose. A local record is reported without forge writes or a Mode line.
