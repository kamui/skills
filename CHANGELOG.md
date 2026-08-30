# Changelog

## [Unreleased]

### Added

- `references/review-protocol.md`, mirrored in `code-review-publish` and `code-review-address`: one comment shape for findings and replies, carrying a rendered-invisible trailer so a finding keeps a stable id across review rounds; a shared disposition vocabulary; and a `gh` verb reference covering batched review submission, inline replies, reactions, and GraphQL thread resolution and reopening.
- Questions as a first-class item on both sides. A reviewer that cannot judge code without knowing something raises a `[Question]` line comment instead of guessing a finding; an addresser stuck on a finding replies `needs-info`. Either asks a user in the session where there is one, and otherwise leaves the question on the pull request so it outlives the run. Questions count toward no axis and toward no round cap, and unanswered ones are listed under `## Open questions` in the summary.
- An `answered` disposition, which the prose already assumed and the vocabulary lacked.
- A two-round cap per finding. A finding declined once and then verified unfixed becomes disputed, and is listed for a human to settle instead of being re-posted, so a review loop cannot re-litigate one point forever.
- `implement-publish`, which implements the work described by a spec, issue, or set of tickets and opens one pull request for it, delegating implementation to the best matching installed skill.
- A status on every review: `Changes Requested` while any blocking finding is unsettled, `Approved` where nothing blocks the merge, `Feedback` where nothing blocks it but the review cannot vouch for the change. A summary that reported only per-axis findings left the author inferring from the counts whether any of them actually stopped the merge.
- The status rides the forge's review event where one can carry it, and is written on the summary's first line where none can — no review system, a self-authored pull request GitHub will only take a `COMMENT` on, or a reviewer unauthorized to gate a merge. `Feedback` is named for the third status rather than `Commented` because on that path every entry on the pull request is already a comment. A status that moves without the head moving — a decline accepted, a question answered — is published as a new review, since a review's state is fixed at submission and GitHub's update endpoint rewrites only the body.
- A severity on every finding. Blocking is the default and goes unmarked, since that is what an author assumes a review comment means; only the exception is labelled `[Optional]`, in the title line and in the trailer as `severity=optional`. The status derives from it, an author can close an optional finding unactioned, and `code-review-address` reads it to know which findings must clear before the pull request can merge — treating anything unmarked, a human's comment included, as blocking.
- Review events follow the status only where the user or the repository's documented workflow authorizes the reviewer to gate a merge; otherwise the review is submitted as `COMMENT` with the status written in the body.

### Changed

- Review findings use `[Code]` for correctness and implementation quality and `[Requirements]` for fidelity to the originating spec. New stable ids use `code/` and `requirements/`; legacy `standards/` and `spec/` ids keep their original values across re-reviews.
- `code-review-address` is model-invocable, so a review loop can reach it as its fix step.
- `code-review-publish` publishes through the forge's review system when it has one, submitting the summary as the review body with every finding batched as a line comment on the code it names. A general pull-request comment is now the fallback for a forge with no review system or one that refuses the review, not the default for a self-authored pull request.
- `code-review-publish` submits every line comment in one batched review rather than one review per finding, and its summary indexes findings instead of restating them.
- `code-review-address` resolves each thread as it finishes it rather than batching resolutions, and either skill can reopen a thread resolved too early.
- Review verdicts are `fixed`, `accepted`, `obsolete`, and `not-fixed`. `confirmed` was ambiguous — it could be read as the finding being confirmed still present, which is what `not-fixed` names — and there was no verdict for accepting a decline, so a reasoned refusal had nowhere to land.
- A `declined` reply no longer resolves its own thread. Declining states a position; the reviewer's `accepted` verdict settles it, so a live disagreement stays visible to the round cap instead of being closed by the party that lost it.
- `code-review-publish` publishes a linked summary index in two phases, since a batched review creates its body and comments in one call and the comment URLs do not exist until it returns.
- `implement-publish` pushes the head branch before both the existing-pull-request and create paths. Pushing only on the create path left an existing pull request advertising a head without the new work.
- Both skills close threads, and the bar for closing widened past "its work is done" to cover threads gone obsolete, outdated, or irrelevant. A stale thread from an earlier round is the reviewer's to close.
- The pull request under review is a fixed target: neither review skill opens, retargets, or closes one. `code-review-publish` stops and reports when a change has no pull request, and `code-review-address` commits fixes to the pull request's existing head branch rather than branching away from it.
- `code-review-publish` takes its fixed point from the pull request's own merge-base with its base branch instead of asking for one, so a review can run unattended.
- A finding scoped to a whole file attaches to that file inside the review rather than falling out to a general pull-request comment.
- Reactions are documented as a signal riding on top of a reply rather than an optional extra, with the reaction-to-meaning mapping both skills share.
- All three skills drop their capability-negotiation prose. Both review skills read their forge verbs from the shipped protocol reference; `implement-publish` needs only two commands and carries them inline. The freed budget went into the behaviour above rather than into a shorter file: `code-review-publish` is 1122 words against 820, `code-review-address` 863 against 839, `implement-publish` 358 against 459, with the 3,117-word protocol reference loaded only when a review skill reaches for it.

## [0.0.2] - 2026-08-29

### Changed

- `code-review-publish` publishes only to the pull request: one review summary comment plus one line comment per finding, submitted together as a single pull-request review. When the pull-request author and the reviewer are the same user, the summary is posted as a general pull-request comment.
- `code-review-publish` treats the originating issue as the spec source only and no longer records the review in the issue tracker.
- `code-review-publish` supports re-reviews: when an earlier review exists at a different head SHA, prior findings are reassessed as resolved, still present, obsolete, or superseded, follow-ups go to existing threads, and the summary records both head SHAs.

## [0.0.1] - 2026-08-28

### Added

- `code-review-publish`, which reviews an issue-linked pull request, publishes one pull-request comment per finding, and records the review in the issue tracker when supported.
- `code-review-address`, which evaluates every pull-request review comment, makes warranted changes, replies to every comment, and resolves or reacts to feedback when supported.
- Setup and installation through the `skills` CLI for Codex, Claude Code, Pi, and OpenCode, plus provenance-checked global synchronization from GitHub `main` with systemd and launchd timers.

[0.0.1]: https://github.com/kamui/skills/releases/tag/v0.0.1
[0.0.2]: https://github.com/kamui/skills/releases/tag/v0.0.2
[Unreleased]: https://github.com/kamui/skills/compare/v0.0.2...HEAD
