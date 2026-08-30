# Changelog

## [Unreleased]

### Added

- `implement-publish`, which implements the work described by a spec, issue, or set of tickets and opens one pull request for it, delegating implementation to the best matching installed skill.

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
