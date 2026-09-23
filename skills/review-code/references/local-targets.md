# Local targets

Read when pinning the target for a range or working tree. The target stays local even when the forge supplies a base: local HEAD may be ahead of the pushed head. There is no forge packet, posting identity, or recorded review-comment deferral, and every local run is a first review. Issue retrieval still follows the repository's issue tracker.

## Resolve and pin

A range is a named ref, `<base>...<head>`, `<base>..<head>`, or “since X”. Interpret both separators as a merge-base diff. A single ref or “since X” supplies the base and uses `HEAD` as head; “the current branch” uses that branch's HEAD and the base inference below. Resolve both commits with `git rev-parse --verify <ref>^{commit}` and compute `git merge-base <base SHA> <head SHA>`. An unresolved ref or merge-base returns `target-unresolved`; never silently review another ref. A range on a dirty tree records “uncommitted changes not reviewed” in Coverage; excluded work is outside this target, not an incomplete review of its committed diff.

An explicit working-tree request, or a session prompt naming nothing or “my changes”, selects the working tree. Before snapshotting in session mode, state that it includes tracked changes and non-ignored untracked files and take scope directives, so scratch files or non-ignored secrets can be set aside with a reason before inspection and never enter a verifier brief. On a bare prompt with a dirty tree, also confirm the working-tree target. An unanswered confirmation leaves the target unresolved. One-shot callers must name a local target and its base up front; a bare one-shot invocation, including on a dirty tree, returns `target-unresolved` without a snapshot. Session mode with no human turn reports the ask and stops if the target or base remains unresolved.

For a branch or working tree, resolve the base in this order:

1. The caller's explicit base. A detached HEAD requires this; without it, session asks and one-shot returns `target-unresolved`.
2. The base of the branch's open pull request (`gh pr view <branch> --json state,baseRefName,url`, `OPEN` only). Report the PR URL as the base source; neither fetch its review packet nor substitute its pushed head for local HEAD.
3. The remote's default branch, then `origin/HEAD` when set.

For a short base branch name (explicit or inferred), prefer `origin/<base>` over a possibly stale local `<base>`; an explicit SHA or fully qualified ref keeps its exact meaning. Pin the resolved base SHA and record which source supplied it. If the current branch is the resolved base branch, set base to real `HEAD`: a working-tree review then contains only uncommitted changes. With no resolvable base, session asks before falsification and stops if unanswered; one-shot returns `target-unresolved`. A failed optional lookup falls through to the next source.

## Snapshot and context

For a working tree, record real `HEAD`, compute its merge-base with the resolved base, and create a private directory outside the working tree with `mktemp -d`. An unborn HEAD returns `snapshot-failed`. Run once:

```sh
python3 scripts/review_context.py --worktree --merge-base <pinned merge-base> --store <private-dir>/review-context.json
```

This is also the shared context build: retain its output and store and do not snapshot or build again there. A non-zero exit is reported with the script's output: `snapshot-failed` when named by the snapshot operation, otherwise `script-failure`. Its `snapshot` section's `head` is the run head. A working-tree snapshot with an empty manifest and no dirty submodule content returns `nothing-to-review`. An empty explicitly requested range can still produce a record with an empty ledger.

The snapshot leaves the real index, refs, and working files unchanged, and working files win over staging. Submodules are gitlinks at their checked-out commits; dirty submodule content is unreviewed and must be named under Coverage gaps, making coverage incomplete unless the user deliberately set it aside with a reason.

Snapshots are unreferenced loose objects that `git gc --prune=now` can remove; the saved record retains snapshot identity and the manifest after that. Refs under `refs/review-code/session/` are leftovers from earlier versions of this skill; report them and delete them with `git update-ref -d` only on the user's authorization.

## Description and record inputs

Read real commit messages with `git log --reverse --format='%H%n%B' <merge-base>..<real head>`. For a range, real head is its pinned head; for a snapshot it is `source_head`, so no snapshot commit enters the description. Save each raw message at `commit-<sha7>` and cite a promise as `commit-<sha7>/"<quoted phrase>"`. Uncommitted changes supply no description text.

Resolve issues from user specs and then a unique branch-name or real commit-message reference, following `docs/agents/issue-tracker.md` when present. Read each relevant issue and its comments once and preserve the inputs for the ledger and digest. With no issue or spec, use the commit messages; with no messages either, the ledger is empty and `Issue fit` names no source. A required-but-unresolved issue follows target pinning's material-question routing, not a stop.

Save the fingerprint input under `rendering.md`'s Identity with both `pr` and `issues`: `pr.title` is the range as written or `worktree tree=<tree hash>`, and `pr.body` the saved real commit messages, byte for byte. The tree hash, not the snapshot commit, makes an unchanged working tree digest stable. When an issue's comments could not be obtained verbatim, pass `comments_available: false` and no comments rather than an empty list.

For composition, a range names `run.target_kind: range`, and both targets name `base_ref` and `base_sha`; the finalizer derives the rest of the run identity. Omit `repository_url` so coordinates stay code spans, including fix sites and deleted files; unpushed commits must not become broken forge links. Retain base source and any base-inference PR URL in the run's private identity and Coverage prose. Either profile's local record is reported without forge writes or a Mode line.
