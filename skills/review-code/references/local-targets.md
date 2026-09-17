# Local targets

Read at step 1 for a range or working tree. The target stays local even when the forge supplies a base: local HEAD may be ahead of the pushed head. There is no forge packet, posting identity, or recorded review-comment deferral. One-shot local runs are first reviews. In session mode, a recheck requested after fixes reads [`re-review.md`](re-review.md#prior-state-sources) with the same session’s persisted session record as prior state. At local-session start, read its [snapshot lifetime](re-review.md#session-snapshot-lifetime) rules and create the session private directory outside the working tree; use a fresh run subdirectory for each review. Issue retrieval still follows the repository's issue tracker.

## Resolve and pin

A range is a named ref, `<base>...<head>`, `<base>..<head>`, or “since X”. Interpret both separators as a merge-base diff. A single ref or “since X” supplies the base and uses `HEAD` as head; “the current branch” uses that branch's HEAD and the base inference below. Resolve both commits with `git rev-parse --verify <ref>^{commit}` and compute `git merge-base <base SHA> <head SHA>`. An unresolved ref or merge-base returns `target-unresolved`; never silently review another ref. A range on a dirty tree records “uncommitted changes not reviewed” in Coverage; excluded work is outside this target, not an incomplete review of its committed diff.

An explicit working-tree request, or a session prompt naming nothing or “my changes”, selects the working tree. Before snapshotting in session mode, state that it includes tracked changes and non-ignored untracked files and take scope directives, so scratch files or non-ignored secrets can be set aside with a reason before inspection and never enter a verifier brief. On a bare prompt with a dirty tree, also confirm the working-tree target. An unanswered confirmation leaves the target unresolved. One-shot callers must name a local target and its base up front; a bare one-shot invocation, including on a dirty tree, returns `target-unresolved` without a snapshot. Session mode with no human turn reports the ask and stops if the target or base remains unresolved.

For a branch or working tree, resolve the base in this order:

1. The caller's explicit base. A detached HEAD requires this; without it, session asks and one-shot returns `target-unresolved`.
2. An open pull request for the branch: `gh pr view <branch> --json state,baseRefName,url`. Use `baseRefName` only when state is `OPEN`. Mention the PR URL and its role in base inference in the report; do not fetch its review packet or substitute its pushed head for local HEAD.
3. The remote's default branch: `gh repo view --json defaultBranchRef` or `git remote show origin`.
4. `origin/HEAD`, when set, via `git symbolic-ref refs/remotes/origin/HEAD`.

For a short base branch name (explicit or inferred), prefer `origin/<base>` over a possibly stale local `<base>`; an explicit SHA or fully qualified ref keeps its exact meaning. Pin the resolved base SHA and record which source supplied it. If the current branch is the resolved base branch, set base to real `HEAD`: a working-tree review then contains only uncommitted changes. With no resolvable base, session asks before falsification and stops if unanswered; one-shot returns `target-unresolved`. These read-only forge lookups inform the base only. Failure of an optional lookup is recoverable through the next source.

## Snapshot and context

For a working tree, record real `HEAD`, compute its merge-base with the resolved base, and use a fresh run subdirectory in session mode, or create a private directory outside the working tree with `mktemp -d` in one-shot mode. An unborn HEAD returns `snapshot-failed`. Run once:

```sh
python3 scripts/review_context.py --worktree --merge-base <pinned merge-base> --store <private-dir>/review-context.json
```

For a session recheck, use the command and continuity checks in [`re-review.md`](re-review.md#session-recheck) instead. Protect each session snapshot under its snapshot-lifetime rules before relying on it. This is also step 2's context build: retain its output and store and do not snapshot or build again there. A non-zero exit is reported with the script's output: `snapshot-failed` when named by the snapshot operation, otherwise `script-failure`. The output's `snapshot` object/section prints `head`, `tree`, `source_head`, `parent`, `chain`, and `dirty_submodules`. Pin `head` as the run head and save all these fields plus the manifest. On a first review, a working-tree snapshot with an empty manifest and no dirty submodule content returns `nothing-to-review`; a usable session prior record instead continues through prior-item classification even when every change was reverted. An empty explicitly requested range can still produce a record with an empty ledger.

The temporary `GIT_INDEX_FILE` is seeded with `git read-tree HEAD`, then `git add -A`, `git write-tree`, and `git commit-tree`. The real index, refs, and working files stay unchanged. Working files win over staging, including staged deletions with a file still on disk and staged-then-edited files. Submodules are gitlinks at their checked-out commits; dirty submodule content is unreviewed and must be named under Coverage gaps, making coverage incomplete unless the user deliberately set it aside with a reason. Configured clean filters run on newly added untracked files and may have their normal side effects.

`--worktree --parent <prior snapshot>` chains a session recheck; `--prior-head <prior snapshot>` also builds its delta sections. The snapshot commit message is `review-code snapshot source=<real HEAD SHA>`. With the same source HEAD, the new parent is the prior snapshot (`chain: chained`), so the prior is an ancestor and the three-dot delta is exactly the tree delta. If real HEAD moved through a commit, merge, or rebase, parent resets to real HEAD (`chain: reset`); that prior is unusable as review state and the next review must be full even if ordinary ancestry checks would pass. With no prior, `chain: first`. A non-snapshot or unreadable parent reports `snapshot-failed`.

Snapshots are unreferenced loose objects. They survive the configured `gc.pruneExpire` (two weeks by default), but `git gc --prune=now` can remove them. The saved record retains snapshot identity and the manifest after that; session refs follow [`re-review.md`](re-review.md#session-snapshot-lifetime).

## Description and record inputs

Read real commit messages with `git log --reverse --format='%H%n%B' <merge-base>..<real head>`. For a range, real head is its pinned head; for a snapshot it is `source_head`, so no snapshot commit enters the description. Save each raw message at `commit-<sha7>` and cite a promise as `commit-<sha7>/"<quoted phrase>"`. Uncommitted changes supply no description text.

Resolve issues from user specs and then a unique branch-name or real commit-message reference, following `docs/agents/issue-tracker.md` when present. Read each relevant issue and its comments once and preserve the inputs for the ledger and digest. With no issue or spec, use the commit messages; with no messages either, the ledger is empty and `Issue fit` names no source. A required-but-unresolved issue follows step 1's material-question routing, not a stop.

Supply the fingerprint inputs directly to `python3 scripts/context_fingerprint.py`: `pr` has `title` equal to the range as written or `worktree tree=<tree hash>`, and `body` equal to the saved real commit messages; `issues`, `specs`, and `guidance` follow `review-record.md`. The tree hash, not the snapshot commit, makes an unchanged working tree digest stable.

For composition, supply `run.target_kind: range|worktree`, `target` for the range as written, `tree` for a working tree, `change_description` with those commit messages (empty string when none), and `specs` with any supplied spec identities. Keep `issues` as the resolved issue coordinates, `merged: false`, and omit `repository_url` so coordinates stay code spans, including fix sites and deleted files; unpushed commits must not become broken forge links. Retain base source and any base-inference PR URL in the run's private identity and Coverage prose. Continue at step 2 using the shared rubric, then render and return the record artifacts the caller's `profile` selects at step 5 — the same payload, fragments, and batch as for a pull request under `publishable`, or the one local record under `implementation-gate`; local records are reported without forge writes or a Mode line.
