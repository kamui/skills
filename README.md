# kamui/skills

Agent skills I use for coding projects and medical-provider research.

## Install

Install from GitHub with the [`skills`](https://github.com/vercel-labs/skills) CLI:

```sh
npx skills@latest add kamui/skills
```

To install selected skills:

```sh
npx skills@latest add kamui/skills --skill review-code-publish --skill review-code
npx skills@latest add kamui/skills --skill resolve-review
npx skills@latest add kamui/skills --skill implement-publish --skill review-code
npx skills@latest add kamui/skills --skill finish-it --skill implement-publish --skill review-code-publish --skill resolve-review --skill review-code
npx skills@latest add kamui/skills --skill review-bot          # optional: publish reviews as a GitHub App
npx skills@latest add kamui/skills --skill find-medical-specialist
```

Use `review-code-publish` for routine pull-request reviews.

Skill names start with the verb for what the skill does and end in `-publish` when the skill writes to the forge, which leaves `/code-review` to the harness and to skills installed from other sources. Issue #245 standardized the publishing skill names and renamed `code-review-address` to `resolve-review`. `finish-it` orchestrates the three publishing skills rather than publishing anything of its own, and is invoked as the phrase a person says, so it carries no `-publish` suffix. See `CHANGELOG.md` to migrate an existing install.

The installer asks which supported agents and installation scope to use.

To target Codex, Claude Code, Pi, and OpenCode explicitly:

```sh
npx skills@latest add kamui/skills -a codex -a claude-code -a pi -a opencode
```

## Keep global skills in sync

Install the per-user timer once on each machine:

```sh
scripts/install-sync-timer
```

The timer runs every 15 minutes and calls `scripts/sync-global-skills`. Run that command directly when you want an immediate update.

The sync command treats this repository's GitHub `main` branch as authoritative. It installs new and changed skills globally, then removes skills that disappeared from the repository only when `~/.agents/.skill-lock.json` identifies their source as `kamui/skills`. It verifies the final files and records the synchronized commit under `${XDG_STATE_HOME:-$HOME/.local/state}/kamui-skills`.

The timer installer supports systemd user services on Linux and launchd agents on macOS. Re-run it if this repository moves to a different local path.

## Compatibility

The skills use the open `SKILL.md` format. Their core behavior and model-selection rules live in standard Markdown instructions. Harness-specific metadata is used only where invocation controls differ.

Installation has been checked with the `skills` CLI targets for Codex, Claude Code, Pi, and OpenCode. Other harnesses that support Agent Skills should also work. `agents/openai.yaml` adds optional Codex and ChatGPT interface metadata; other harnesses can ignore it.

The four skills on the implementation and review loop are model-invocable, and `review-bot` is model-invocable so those skills can reach it; `finish-it` is model-invocable only when the user says the explicit phrase "Finish it". `find-medical-specialist` requires explicit invocation in Codex through its interface policy. A plain read-only review request now selects `review-code` in session mode for the working tree, current branch, range, or pull request; `review-code-publish` is for posting and calls it with `mode: one-shot`. Each skill is also directly invocable by name in [Codex](https://developers.openai.com/codex/skills), [Claude Code](https://code.claude.com/docs/en/skills), [Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md), and [OpenCode](https://opencode.ai/docs/skills/).

Skills that ship scripts run them with `python3` on the standard library alone, Python 3.9 or newer, and need `git`; `review-bot` needs `openssl` instead. macOS and Linux, including WSL, are the supported platforms; native Windows is not.

`find-medical-specialist` ships no scripts and needs current web research. A browser or spreadsheet tool may be used when needed to inspect provider pages or author the CSV. It works independently of the coding and review skills.

## Benchmark

The review-code benchmark lives in [`kamui/code-review-bench`](https://github.com/kamui/code-review-bench). Its [scoreboard](https://github.com/kamui/code-review-bench/blob/main/bench/SCOREBOARD.md) compares `review-code` with built-in reviewers on real pull requests.

## Skills

The skills compose into a loop: `implement-publish` opens a pull request, `review-code-publish` reviews it, `resolve-review` works the feedback, and the review runs again. `finish-it` drives that loop unattended, one fresh subagent per step. Their visible comment and reply contracts keep the hand-offs readable to both people and agents; see [The review handoff](#the-review-handoff).

### `review-code`

The shared review core returns a validated record, emitted batch, and complete would-be review without writing to the forge. Plain review requests and explicit `$review-code` select it; `review-code-publish` calls it with `mode: one-shot` for posting. Absent `mode`, it runs in session mode: ask before falsification, present the record and routed questions afterward, and leave the record unchanged; headless asks become report lines. It reviews pull requests, merge-base ranges, and working-tree snapshots including non-ignored untracked files. Local targets omit forge links and keep the working tree and index unchanged. `/code-review` is left to the harness and the two-axis skill installed from another source.

A manual prompt or built-in reviewer can use the same review abilities. Choose `review-code` when the result needs to satisfy a standing contract: check promised outcomes beyond the diff, challenge consequential claims independently, disclose coverage and uncertainty, and preserve findings in a validated record across fixes. The model chooses the investigation and proof strategy. This is a workflow commitment, not a claim of higher recall or precision.

### `review-code-publish`

Invokes `review-code` with `mode: one-shot` to review the complete merge-base diff and publishes one forge-native review containing every verified finding. One integrated reviewer checks both implementation behavior and issue fit against a private evidence rubric, falsifies each candidate, and invokes one fresh batched verifier for every proposed `must-fix` and other consequential claim — security, data loss, compatibility. A mechanical validator checks the assembled payload before anything is written. `review-code/scripts/review_context.py` builds the changed-file manifest, function-context diff, and per-hunk ranges in one call.

A missing issue required by the repository workflow produces a `[Question]` instead of a stop: the ledger uses the pull-request text and, absent blockers or other coverage gaps, the status is `Needs Information`.

Each finding carries an impact priority and an independent action: `must-fix` blocks the merge, while `consider` is optional. The review reaches `Changes Requested`, `Incomplete`, `Needs Information`, or `Approved`, and reports its coverage. Publication is atomic against a freshly checked head; findings without an honest line anchor remain complete in the review body rather than being attached to unrelated code.

Findings, questions, and observations are separate channels, so uncertainty routes to a question instead of becoming a finding an agent would dutifully "fix". A run trailer records the workflow version and a context digest, so an unchanged pull request is reported rather than re-reviewed. This workflow was evaluated through successive prototypes before becoming the current review publisher.

It activates when a caller asks to review an issue-linked pull request and intends to post comments or a review to that pull request. Read-only review requests do not activate it. You can also invoke it directly:

```text
$review-code-publish
```

The host agent needs access to the pull request to publish the review.

### `resolve-review`

Addresses every review comment on a pull request, makes warranted changes, replies directly even when the answer is pushback, and resolves each thread as it finishes it. Re-addressing a pull request, it can reopen a thread that was resolved too early. Each round closes with one summary comment and an ask for a re-review, so a pull request whose threads are all resolved does not read as one where nothing happened.

Before pushing fixes or posting disposition replies, a fresh-context subagent reviews the addressing round for incomplete fixes and regressions, then checks the proposed replies against the code. It receives the original feedback and repository evidence without the implementation conversation. Unresolved feedback keeps its protocol disposition and remains open for the original reviewer.

The skill is deliberately independent of a particular code-review or implementation skill. It follows an implementation skill the user names; otherwise the model chooses how to investigate, implement, and verify the work.

It activates when review feedback on a pull request needs working through, including as the fix step of a review loop. You can also invoke it directly:

```text
$resolve-review
```

The host agent needs write access to the pull request to post replies and resolve threads.

### `implement-publish`

Implements the work described by a spec, issue, or set of tickets, then opens one pull request containing the implementation. The model chooses how to implement, within the user's instructions, any implementation skill they name, and repository conventions. It works on a branch suitable as a pull-request head and links each spec source in the pull-request body.

Before pushing or opening the pull request, it has a fresh-context subagent invoke `review-code` in one-shot mode on the local base-to-head range. It publishes only when that review is `Approved` with complete coverage at the commit it pushes. `Needs Information`, `Changes Requested`, and `Incomplete` all keep the work local: it fixes warranted findings or supplies what the reviewer asked for, then continues the review from its latest accepted record, resuming the same reviewer or handing the phase to another isolated one. Every phase runs on a route that returns the result while the step is still active. `review-code-publish` handles the published review afterward.

It activates when a caller asks to implement work from a spec or issue and publish the result as a pull request. You can also invoke it directly:

```text
$implement-publish
```

The host agent needs access to the forge to create the pull request.

### `finish-it`

Runs one delivery: a spec, issue, branch, or pull request goes through `implement-publish`, one `review-code-publish` review, and rounds of `resolve-review` followed by `review-code-publish`, each step in its own fresh-context subagent that receives a fixed handoff packet and reads everything else from the pull request. It resumes from wherever the pull request already is: given a pull request with one round done it has two rounds remaining, and given one with many it still has at least one. The round total defaults to 3 and is set in the invocation text (`rounds: 5`). When the delivery's own first review approves with nothing to address, it runs no rounds. Otherwise the first round always runs, a pull request that entered already approved included. After any completed round it stops early on `Approved` at the current head when the skill's empty ledger check holds; from the second round on it also stops when a round makes no progress. A prose spec becomes an issue first, so every step has one stable spec source. It never merges.

The model invokes it only when the user says the explicit phrase "Finish it"; it also runs when invoked by name:

```text
$finish-it
```

It requires `implement-publish`, `review-code-publish`, `resolve-review`, and `review-code`, and stops before any write when one is missing. The host agent needs access to the forge for every write those skills make.

### `review-bot`

Optional. Mints a GitHub App's installation token and resolves the identity a repository declares as its reviewing app, so a review can publish as the app rather than as the pull request's author. Its script, `scripts/review_token.py`, has two subcommands: `token` prints a short-lived token scoped to one named repository, and `whoami` reports the app, both login forms, the installation, and the exact review-token command a publisher runs. A dependent calls its Resolve entry point with the client id and the pull request's base repository, and on any failure (not installed, no key, key unreadable, app not installed on the repository, forge refusal, network failure) falls back to the authenticated user and withholds gating. A person invokes it as `$review-bot` to create and install the app and place the key; see [Reviewing as a GitHub App](#reviewing-as-a-github-app).

```text
$review-bot
```

### `find-medical-specialist`

Finds and compares specialists using Zocdoc and the two strongest local hospital systems for the requested specialty. It screens credentials, location, exact insurance plan and appointment availability, then reads written patient reviews for clinical concerns and positives. It keeps one ranked CSV with source links, screening decisions and review coverage, updating the same file on follow-up searches using the [42-column schema](skills/find-medical-specialist/references/csv-schema.md).

Supply the specialty, search area, appointment deadline or time horizon, and exact insurance plan or an explicit self-pay search. The skill researches providers; it does not diagnose, recommend treatment, book appointments or contact offices.

```text
$find-medical-specialist
```

## Reviewing as a GitHub App

A repository that wants its reviews published under a GitHub App declares the app in `docs/agents/issue-tracker.md`:

```text
## Reviewing identity

- **Reviewing app**: <app name>
- **Client id**: <client id>
```

An optional third field, **Review-token command**, gives a literal shell command for a repository whose token comes from somewhere else; when present it is used as-is. Creating the app, choosing its permissions, installing it on every reviewed repository, and placing its private key at `~/.config/review-bot/<client id>.pem` are walked through in [`skills/review-bot/references/setup.md`](skills/review-bot/references/setup.md). The key is the only per-machine item and never lives in a repository or under the synced skills directory.

## The review handoff

`review-code-publish` and `implement-publish` require `review-code` as one of the two named install-alone exceptions; `finish-it`, which requires all three publishing skills and `review-code`, is the other. Both call it in one-shot mode: the publisher reviews a pull request for posting, while `implement-publish` reviews its local base-to-head range before publication.

`review-code` owns finding admission through [`rubric.md`](skills/review-code/references/rubric.md), record semantics through the Return section of [`SKILL.md`](skills/review-code/SKILL.md#return), and visible output through [`output.md`](skills/review-code/references/output.md). `review-code-publish` owns forge writes through [`publication.md`](skills/review-code-publish/references/publication.md). `resolve-review` owns replies, dispositions, thread state, and round closeout through its [`addressing-protocol.md`](skills/resolve-review/references/addressing-protocol.md).

A published finding is understandable from visible prose alone: its title states priority and action, and its `Triggers when`, `Impact`, and `Change` fields explain the defect and requested outcome. Optional findings explicitly say they may be closed without action. Hidden trailers add stable ids, reviewed heads, and correlation metadata for agents, but human comments without trailers remain first-class input.

The addresser evaluates every item against the current code and replies with one visible disposition: `implemented`, `already-addressed`, `answered`, `declined`, `needs-info`, or `blocked`. A reply states intent rather than proof, so the next review verifies it against the code. Findings that survive one verified decline become disputes for a person instead of looping indefinitely.

The reviewer submits one semantic status after coverage is known: `Changes Requested` for unsettled `must-fix` findings, `Incomplete` for unfinished material coverage or verification, `Needs Information` for an outcome-changing unanswered question, and `Approved` otherwise. Forge authorization controls only whether that status travels as `REQUEST_CHANGES`, `APPROVE`, or the default `COMMENT`; it never changes the conclusion.

Each published review ends with a hidden `workflow=` trailer naming the version of the review rules. When the latest review at the current head carries the current version, the duplicate-review shortcut skips the pull request instead of reviewing it again. Raising the version after a rule change gives each open pull request one fresh review. [`output.md`](skills/review-code/references/output.md#identity) says when to raise it, and the [design history](docs/review-code/HISTORY.md#workflow-versions) says how to find what an earlier version changed.

## Review comments and replies

`review-code-publish` defines the finding and publication format in [`references/publication.md`](skills/review-code-publish/references/publication.md). `resolve-review` defines reply dispositions and thread handling in [`references/addressing-protocol.md`](skills/resolve-review/references/addressing-protocol.md). The review handoff keeps comments readable to people and parseable by agents; update both references when changing terms they share.
