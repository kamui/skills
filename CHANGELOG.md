# Changelog

## [Unreleased]

### Added

- `references/review-protocol.md`, mirrored in `code-review-publish-legacy` and `code-review-address`: one comment shape for findings and replies, carrying a rendered-invisible trailer so a finding keeps a stable id across review rounds; a shared disposition vocabulary; and a `gh` verb reference covering batched review submission, inline replies, and GraphQL thread resolution and reopening.
- Questions as a first-class item on both sides. A reviewer that cannot judge code without knowing something raises a `[Question]` instead of guessing a finding; an addresser stuck on a finding replies `needs-info`. A whole-change question carries a stable id in the review body and closes when its answer entry and reply trailer appear in the round's addressing summary. Questions count toward no axis and toward no round cap; the same open question is not re-posted, and it holds `Needs Information` until answered or withdrawn rather than aging into approval.
- An `answered` disposition, which the prose already assumed and the vocabulary lacked.
- A two-round cap per finding. A finding declined once and then verified unfixed becomes disputed, and is listed for a human to settle instead of being re-posted, so a review loop cannot re-litigate one point forever.
- `implement-publish`, which implements the work described by a spec, issue, or set of tickets and opens one pull request for it, delegating implementation to the best matching installed skill.
- An addressing summary. `code-review-address` closes each round with one general pull-request comment — the head addressed, counts by disposition linked to their threads, whole-change answers with their reply trailers, what still needs someone, the checks run, and whether the round is finished or waiting — and requests a re-review from the identity whose review it addressed where the forge routes them. Resolving every thread had left the pull request looking untouched, since the forge collapses what is resolved: a round that answered everything and a round that did nothing rendered the same. One comment per round however large it was; only whole-change answers carry per-item detail there because they have no thread.
- A status on every completed review: `Changes Requested` while any blocking finding is unsettled, `Needs Information` only where a concrete unanswered question could change the verdict, and `Approved` otherwise. Each axis records Passed, Findings, or `Not applicable`, plus Waiting for information where needed; an operationally unassessed axis aborts publication instead of falling through to approval.
- The status rides the forge's review event where one can carry it, and is written on the summary's first line where none can — `Needs Information`, no review system, a self-authored pull request GitHub will only take a `COMMENT` on, or a reviewer unauthorized to gate a merge. A non-gating `Changes Requested` or `Approved` uses its defined advisory form. A status that moves without the head moving — a decline accepted, a question answered — is published as a new review, since a review's state is fixed at submission and GitHub's update endpoint rewrites only the body. A superseded `COMMENT` needs no dismissal; only a gating state the new event cannot replace does.
- A severity on every finding. Blocking is the default and goes unmarked, since that is what an author assumes a review comment means; only the exception is labelled `[Suggestion]`, in the title line and in the trailer as `severity=optional`. The status derives from it, an author can close an optional finding unactioned, and `code-review-address` reads it to know which findings must clear before the pull request can merge — treating anything unmarked, a human's comment included, as blocking.
- Review events carry the status only where the user or the repository's documented workflow authorizes the reviewer to gate a merge; otherwise the review is submitted as `COMMENT` with the status written in the body. Permission changes the transport, never an `Approved` conclusion into `Needs Information`.
- A scripts convention in `docs/agents/scripts.md`: skill scripts are standard-library Python 3.9+ on macOS and Linux, do mechanical work only, and are invoked as `python3 scripts/<name>.py` from `SKILL.md`. Skills that ship scripts declare the requirement in their `compatibility` frontmatter.

### Changed

- `code-audit-publish` attributes a regression to the guarantee a change removed rather than to the lines it touched. Unchanged code is in scope when the diff removed or weakened a lock, ordering constraint, ownership rule, validated invariant, check, or bound it relied on, so a byte-identical path that was safe at the merge-base and is unsafe at the head is this change's defect, cited with both revisions, the consumer, and the trigger. A path already unsafe at the merge-base stays pre-existing, and a refactor that preserves the guarantee introduces nothing. The verifier's `pre-existing` refutation has to compare the same path, trigger, and governing guarantee at base and head, and rules `plausible` where it cannot reconstruct the base state. Such a finding takes its fix site from the repair it proposes — the changed line when the protection should be restored there, the untouched consumer when the removal is deliberate and the consumer must adapt — and the existing anchor ladder runs from that, never by giving the consumer a fabricated diff coordinate. The Requirements-candidate exception and the paired old/new documentation sweep keep their own rules. Review protocol `v2b-1` to `v2b-2`.
- Rename `code-review-deep-publish` to `code-audit-publish` for the independent audit direction. Keep explicit-only invocation and the existing `v2b-1` review protocol; requirements/contract investigation is the current foundation, with stronger guarantee audits and verification tracked as future work. Historical run identities remain unchanged.
- `implement-publish` accounts for every issue provided or inferred, not just a spec link: the pull-request body names each with a disposition — closes it via the forge's closing keyword, partially implements it with what remains open, or affects it with how — so a reader sees the pull request's effect on each ticket.
- The v5a calibrated hybrid replaces the v5 workflow as `code-review-publish`, model-invocable like the rest of the loop: one integrated reviewer inspects the complete merge-base diff against a private rubric, `must-fix` and high-consequence findings are verified in a fresh context before publication, questions and observations are separate channels, and a mechanical validator gates every write. The former two-axis reviewer remains as `code-review-publish-legacy`, which is not model-invocable and is kept for historical purposes; invoke it explicitly only when the legacy two-axis protocol is specifically wanted.
- The round-closing re-review ask no longer depends on the forge accepting a review request. Where the forge routes none, or refuses this one because the reviewing identity authored the pull request, the addressing summary carries `Re-requesting review from @<login>.` instead — the mention notifies them, which is what the request was for. `code-review-address` settles which form applies before writing the summary and no longer explains the forge's refusal on the pull request, where a paragraph about a rejected API call was noise around the ask itself.
- `code-review-address` reconciles the pull request title and description with the final diff and originating spec before closing an addressing round, updating stale metadata while preserving still-valid context and issue links.
- Review findings use `[Code]` for correctness and implementation quality and `[Requirements]` for fidelity to the originating spec. New stable ids use `code/` and `requirements/`; legacy `standards/` and `spec/` ids keep their original values across re-reviews.
- `code-review-address` is model-invocable, so a review loop can reach it as its fix step.
- `code-review-publish-legacy` publishes through the forge's review system when it has one, submitting the summary as the review body with every finding batched as a line comment on the code it names. A general pull-request comment is now the fallback for a forge with no review system or one that refuses the review, not the default for a self-authored pull request.
- `code-review-publish-legacy` submits every line comment in one batched review rather than one review per finding, and its summary indexes findings instead of restating them.
- `code-review-address` resolves each thread as it finishes it rather than batching resolutions, and either skill can reopen a thread resolved too early.
- Review verdicts are `fixed`, `accepted`, `obsolete`, and `not-fixed`. `confirmed` was ambiguous — it could be read as the finding being confirmed still present, which is what `not-fixed` names — and there was no verdict for accepting a decline, so a reasoned refusal had nowhere to land.
- A `declined` reply no longer resolves its own thread. Declining states a position; the reviewer's `accepted` verdict settles it, so a live disagreement stays visible to the round cap instead of being closed by the party that lost it.
- `code-review-publish-legacy` publishes a linked summary index in two phases, since a batched review creates its body and comments in one call and the comment URLs do not exist until it returns.
- `implement-publish` pushes the head branch before both the existing-pull-request and create paths. Pushing only on the create path left an existing pull request advertising a head without the new work.
- Both skills close threads, and the bar for closing widened past "its work is done" to cover threads gone obsolete, outdated, or irrelevant. A stale thread from an earlier round is the reviewer's to close.
- The pull request under review is a fixed target: neither review skill opens, retargets, or closes one. `code-review-publish-legacy` stops and reports when a change has no pull request, and `code-review-address` commits fixes to the pull request's existing head branch rather than branching away from it.
- `code-review-publish-legacy` takes its fixed point from the pull request's own merge-base with its base branch instead of asking for one, so a review can run unattended.
- A finding scoped to a whole file attaches to that file inside the review rather than falling out to a general pull-request comment.
- All three skills drop their capability-negotiation prose. Both review skills read their forge verbs from the shipped protocol reference; `implement-publish` needs only two commands and carries them inline. The freed budget went into the behaviour above rather than into a shorter file: `code-review-publish-legacy` is 1,184 words against 820, `code-review-address` 1,172 against 839, `implement-publish` 358 against 459, with the 4,141-word protocol reference loaded only when a review skill reaches for it.

### Removed

- Reactions from the review protocol and both skills that used it. A reaction repeated what the reply's disposition and trailer already said, its main reader is an agent that reads the reply body rather than the reaction, and posting one cost a request per comment.

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
