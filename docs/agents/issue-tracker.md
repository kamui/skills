# Issue tracker: GitHub

Issues and specs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`; `gh` does this automatically when run inside a clone.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view <number> --comments` and `gh pr diff <number>` for the diff.
- **List external PRs for triage**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` then keep only `authorAssociation` of `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE` (drop `OWNER`/`MEMBER`/`COLLABORATOR`).
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either: resolve with `gh pr view 42` and fall back to `gh issue view 42`.

## Pull request review operations

Reviewing and replying on a pull request needs verbs this file does not carry (batched review submission, inline replies, GraphQL thread resolution). `review-code` returns the review record without forge writes; `review-code-publish` ships `references/publication.md` for review submission, thread replies, and resolution; `code-review-publish` ships `references/review-protocol.md` and `resolve-review` ships `references/addressing-protocol.md` for their operations. These references apply to this GitHub repository as written.

## Reviewing identity

Reviews publish as the **NitpikBot** GitHub App, not as the human who authored the pull request, so GitHub's review system is usable on a repository where the same person writes and reviews: an app review is not a self-review, and `APPROVE` and `REQUEST_CHANGES` are available to it.

- **Review-token command**: `nitpikbot token <owner>/<repo>`, which prints a short-lived installation token. The publication blocks run it through `sh -c` and export `GH_TOKEN` for every forge write a review makes — the review itself, its inline comments, thread replies, thread resolutions, dismissals. Always name the repository; never let the runner infer one from a remote. Keep the token in the environment rather than in a command line: the timing wrapper records `argv`.
- **Ad-hoc calls**: `nitpikbot run <owner>/<repo> -- <command>` runs one command as the app. Write it out literally; held in a shell variable and expanded in command position it would run as a single command name under `zsh`.
- **Its login**: `nitpikbot run <owner>/<repo> -- gh api graphql -f query='{viewer{login}}' --jq .data.viewer.login`, or the same call with `GH_TOKEN` from the token command. `gh api user` returns HTTP 403 for an app token and must not be used for it.
- **Everything else stays the human's**: commits, pushes, opening pull requests, replies to review comments, and addressing summaries. An addressing round has to come from the pull-request author.
- **The suffix differs by API**: REST calls this identity `nitpikbot[bot]` and GraphQL calls it `nitpikbot`. Compare logins with a trailing `[bot]` ignored on both sides.
- **No re-review request**: GitHub routes review requests to users and teams only, and `@nitpikbot[bot]` notifies nobody. An addressing round asks this reviewer for nothing; whatever runs the app starts the next review.
- **Absent runner**: `nitpikbot` is an optional external tool. Where it is missing or cannot authenticate, review as the authenticated user under the ordinary self-review rules rather than failing the run.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body. `gh issue create --label wayfinder:map`.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue (`gh api` on the sub-issues endpoint). Where sub-issues aren't enabled, add the child to a task list in the map body and put `Part of #<map>` at the top of the child body. Labels: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: GitHub's **native issue dependencies**, the canonical, UI-visible representation. Add an edge with `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where `<blocker-db-id>` is the blocker's numeric **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, _not_ the `#number` or `node_id`). GitHub reports `issue_dependencies_summary.blocked_by` (open blockers only, the live gate). Where dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the child body. A ticket is unblocked when every blocker is closed.
- **Frontier query**: list the map's open children (`gh issue list --state open`, scoped to the map's sub-issues / task list), drop any with an open blocker (`issue_dependencies_summary.blocked_by > 0`, or an open issue in the `Blocked by` line) or an assignee; first in map order wins.
- **Claim**: `gh issue edit <n> --add-assignee @me`, the session's first write.
- **Resolve**: `gh issue comment <n> --body "<answer>"`, then `gh issue close <n>`, then append a context pointer (gist + link) to the map's Decisions-so-far.
