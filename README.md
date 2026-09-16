# kamui/skills

Agent skills I use across coding projects.

## Install

Install from GitHub with the [`skills`](https://github.com/vercel-labs/skills) CLI:

```sh
npx skills@latest add kamui/skills
```

To install selected skills:

```sh
npx skills@latest add kamui/skills --skill review-code-publish --skill review-code
npx skills@latest add kamui/skills --skill audit-code-publish
npx skills@latest add kamui/skills --skill resolve-review
npx skills@latest add kamui/skills --skill implement-publish --skill review-code
npx skills@latest add kamui/skills --skill finish-it --skill implement-publish --skill review-code-publish --skill resolve-review --skill review-code
npx skills@latest add kamui/skills --skill code-review-publish  # legacy, kept for historical purposes
npx skills@latest add mattpocock/skills --skill code-review    # required by code-review-publish
npx skills@latest add kamui/skills --skill reviewbot           # optional: publish reviews as a GitHub App
```

Use `review-code-publish` for routine pull-request reviews. Explicitly use `audit-code-publish` for independent investigation of requirements completeness, API conformance, and contracts affected beyond the diff. Originally `code-review-deep-publish`, it retains the Panel workflow, and the [audit roadmap](skills/audit-code-publish/DESIGN.md#positioning) tracks the planned system-guarantee and executable-evidence checks, which have not shipped. Its higher cost and high-risk effectiveness require matched evaluation; no general cost or safety advantage is claimed.

Skill names start with the verb for what the skill does and end in `-publish` when the skill writes to the forge, which leaves `/code-review` to the harness and to skills installed from other sources. Issue #245 renamed `code-review-publish` to `review-code-publish`, `code-audit-publish` to `audit-code-publish`, and `code-review-address` to `resolve-review`. The legacy two-axis reviewer, `code-review-publish-legacy` until then, took the freed `code-review-publish` name afterward and is one of two exceptions to the convention: it is named for the two-axis `code-review` skill from `mattpocock/skills` that it publishes. `finish-it` is the other: it orchestrates the three publishing skills rather than publishing anything of its own, and it is invoked as the phrase a person says, so it carries no `-publish` suffix. See `CHANGELOG.md` to migrate an existing install.

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

Four skills are model-invocable, so a driving agent can run the loop end to end, and `reviewbot` is model-invocable so those skills can reach it; the legacy `code-review-publish` and `finish-it` are not model-invocable and run only when invoked by name, and `audit-code-publish` is explicit-only. A plain read-only review request now selects `review-code` in session mode for the working tree, current branch, range, or pull request; `review-code-publish` is for posting and calls it with `mode: one-shot`. Each skill is also directly invocable by name in [Codex](https://developers.openai.com/codex/skills), [Claude Code](https://code.claude.com/docs/en/skills), [Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md), and [OpenCode](https://opencode.ai/docs/skills/).

Skills that ship scripts run them with `python3` on the standard library alone, Python 3.9 or newer, and need `git`; `reviewbot` needs `openssl` instead. macOS and Linux, including WSL, are the supported platforms; native Windows is not.

## Skills

The skills compose into a loop: `implement-publish` opens a pull request, `review-code-publish` reviews it, `resolve-review` works the feedback, and the review runs again. `finish-it` drives that loop unattended, one fresh subagent per step. Their visible comment and reply contracts keep the hand-offs readable to both people and agents; see [The review handoff](#the-review-handoff). `audit-code-publish` occupies the reviewer slot when an independent audit is requested. Its investigation stays bounded by the pull request’s affected contracts and code; it is not an automatic additional review stage.

### `review-code`

The shared review core returns a validated record, emitted batch, and complete would-be review without writing to the forge. Plain review requests and explicit `$review-code` select it; `review-code-publish` calls it with `mode: one-shot` for posting. Absent `mode`, it runs in session mode: ask before falsification, present the record and routed questions afterward, and leave the record unchanged; headless asks become report lines. It reviews pull requests, merge-base ranges, and working-tree snapshots including non-ignored untracked files. Local targets omit forge links and keep the working tree and index unchanged. `/code-review` is left to the harness and the two-axis skill installed from another source.

### `review-code-publish`

Invokes `review-code` with `mode: one-shot` to review the complete merge-base diff and publishes one forge-native review containing every verified finding. One integrated reviewer checks both implementation behavior and issue fit against a private evidence rubric, falsifies each candidate, and invokes one fresh batched verifier for every proposed `must-fix` and other consequential claim — security, data loss, compatibility. A mechanical validator checks the assembled payload before anything is written. `review-code/scripts/review_context.py` builds the changed-file manifest, function-context diff, and per-hunk ranges in one call.

A missing issue required by the repository workflow produces a `[Question]` instead of a stop: the ledger uses the pull-request text and, absent blockers or other coverage gaps, the status is `Needs Information`.

Each finding carries an impact priority and an independent action: `must-fix` blocks the merge, while `consider` is optional. The review reaches `Changes Requested`, `Incomplete`, `Needs Information`, or `Approved`, and reports its coverage. Publication is atomic against a freshly checked head; findings without an honest line anchor remain complete in the review body rather than being attached to unrelated code.

Findings, questions, and observations are separate channels, so uncertainty routes to a question instead of becoming a finding an agent would dutifully "fix". A run trailer records the workflow version and a context digest, so an unchanged pull request is reported rather than re-reviewed. This workflow was evaluated as the v5a prototype; it supersedes the v5 workflow that previously filled this skill and the two-axis reviewer, now kept as the legacy `code-review-publish` for historical purposes.

It activates when a caller asks to review an issue-linked pull request and intends to post comments or a review to that pull request. Read-only review requests do not activate it. You can also invoke it directly:

```text
$review-code-publish
```

The host agent needs access to the pull request to publish the review.

### `code-review-publish`

The original two-axis reviewer, kept for historical purposes. It runs the [`code-review`](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md) skill from `mattpocock/skills`, which must be installed, at the pull request's head. Its **Standards** findings become **Code** and its **Spec** findings become **Requirements**. It publishes them as line comments under one status, using the shared review protocol below. It is not model-invocable: `review-code-publish` should be used instead, and this skill runs only when explicitly invoked by name:

```text
$code-review-publish
```

### `resolve-review`

Addresses every review comment on a pull request, makes warranted changes, replies directly even when the answer is pushback, and resolves each thread as it finishes it. Re-addressing a pull request, it can reopen a thread that was resolved too early. Each round closes with one summary comment and an ask for a re-review, so a pull request whose threads are all resolved does not read as one where nothing happened.

Before pushing fixes or posting disposition replies, a fresh-context subagent reviews the addressing round for incomplete fixes and regressions, then checks the proposed replies against the code. It receives the original feedback and repository evidence without the implementation conversation. Unresolved feedback keeps its protocol disposition and remains open for the original reviewer.

The skill is deliberately independent of a particular code-review or implementation skill. Normal skill routing can select another installed skill when useful; if none applies, the model handles the work directly.

It activates when review feedback on a pull request needs working through, including as the fix step of a review loop. You can also invoke it directly:

```text
$resolve-review
```

The host agent needs write access to the pull request to post replies and resolve threads.

### `implement-publish`

Implements the work described by a spec, issue, or set of tickets, then opens one pull request containing the implementation. It delegates the implementation to the best matching installed skill, creates a suitable branch when the current one is not pull-request ready, and links the spec source in the pull-request body.

Before pushing or opening the pull request, it has a fresh-context general-purpose subagent invoke `review-code` in one-shot mode on the local base-to-head range. It addresses blocking findings, then re-verifies them and inspects the complete fix delta so the review still covers the final committed head — resuming the same reviewer where the host can wait for that continuation, otherwise handing the phase to one fresh isolated reviewer whose completion it can await. Every phase runs on a route that returns the result while the step is still active, and the step names the operation it used. `review-code-publish` handles the published review afterward.

It activates when a caller asks to implement work from a spec or issue and publish the result as a pull request. You can also invoke it directly:

```text
$implement-publish
```

The host agent needs access to the forge to create the pull request.

### `finish-it`

Runs one delivery: a spec, issue, branch, or pull request goes through `implement-publish`, one `review-code-publish` review, and rounds of `resolve-review` followed by `review-code-publish`, each step in its own fresh-context subagent that receives a fixed handoff packet and reads everything else from the pull request. It resumes from wherever the pull request already is: given a pull request with one round done it runs two more, and given one with many it still runs at least one. The round total defaults to 3 and is set in the invocation text (`rounds: 5`). The first round always runs, an already-approved pull request included; from the second on it stops early on `Approved` or when a round makes no progress. A prose spec becomes an issue first, so every step has one stable spec source. It never merges.

It is not model-invocable and runs only when invoked by name:

```text
$finish-it
```

It requires `implement-publish`, `review-code-publish`, `resolve-review`, and `review-code`, and stops before any write when one is missing. The host agent needs access to the forge for every write those skills make.

### `reviewbot`

Optional. Mints a GitHub App's installation token and resolves the identity a repository declares as its reviewing app, so a review can publish as the app rather than as the pull request's author. Its script, `scripts/review_token.py`, has two subcommands: `token` prints a short-lived token scoped to one named repository, and `whoami` reports the app, both login forms, the installation, and the exact review-token command a publisher runs. A dependent calls its Resolve entry point with the client id and the pull request's base repository, and on any failure (not installed, no key, key unreadable, app not installed on the repository, forge refusal, network failure) falls back to the authenticated user and withholds gating. A person invokes it as `$reviewbot` to create and install the app and place the key; see [Reviewing as a GitHub App](#reviewing-as-a-github-app).

```text
$reviewbot
```

## Reviewing as a GitHub App

A repository that wants its reviews published under a GitHub App declares the app in `docs/agents/issue-tracker.md`:

```text
## Reviewing identity

- **Reviewing app**: <app name>
- **Client id**: <client id>
```

An optional third field, **Review-token command**, gives a literal shell command for a repository whose token comes from somewhere else; when present it is used as-is. Creating the app, choosing its permissions, installing it on every reviewed repository, and placing its private key at `~/.config/reviewbot/<client id>.pem` are walked through in [`skills/reviewbot/references/setup.md`](skills/reviewbot/references/setup.md). The key is the only per-machine item and never lives in a repository or under the synced skills directory.

## The review handoff

`review-code-publish` and `implement-publish` require `review-code` as one of the two named install-alone exceptions; `finish-it`, which requires all three publishing skills and `review-code`, is the other. Both call it in one-shot mode: the publisher reviews a pull request for posting, while `implement-publish` reviews its local base-to-head range before publication.

`review-code` owns finding admission through [`review-rubric.md`](skills/review-code/references/review-rubric.md), record semantics through [`review-record.md`](skills/review-code/references/review-record.md), and visible output through [`rendering.md`](skills/review-code/references/rendering.md). `review-code-publish` owns forge writes through [`publication.md`](skills/review-code-publish/references/publication.md). `resolve-review` owns replies, dispositions, thread state, and round closeout through its [`addressing-protocol.md`](skills/resolve-review/references/addressing-protocol.md).

A published finding is understandable from visible prose alone: its title states priority and action, and its `Triggers when`, `Impact`, and `Change` fields explain the defect and requested outcome. Optional findings explicitly say they may be closed without action. Hidden trailers add stable ids, reviewed heads, and correlation metadata for agents, but human comments without trailers remain first-class input.

The addresser evaluates every item against the current code and replies with one visible disposition: `implemented`, `already-addressed`, `answered`, `declined`, `needs-info`, or `blocked`. A reply states intent rather than proof, so the next review verifies it against the code. Findings that survive one verified decline become disputes for a person instead of looping indefinitely.

The reviewer submits one semantic status after coverage is known: `Changes Requested` for unsettled `must-fix` findings, `Incomplete` for unfinished material coverage or verification, `Needs Information` for an outcome-changing unanswered question, and `Approved` otherwise. Forge authorization controls only whether that status travels as `REQUEST_CHANGES`, `APPROVE`, or the default `COMMENT`; it never changes the conclusion.

The internal `workflow=v5b-20` trailer versions review behavior for deduplication and re-review continuity. Issue #119 bumped it from `v5b-1` to `v5b-2` for scoped verifier safety rulings and post-refutation clean-verdict checks, issue #84 bumped it to `v5b-3` for merge-base links on deleted-file anchors, issue #121 bumped it to `v5b-4` for the claims ledger built from the pull-request text before compliance review, issue #122 bumped it to `v5b-5` for the execution-order inspection and focused execution of changed tests, issue #123 bumped it to `v5b-6` for versioned-artifact obligations enumerated into that ledger, issue #132 bumped it to `v5b-7` for the persisted forge packet whose pagination completeness and edit timestamps now gate deduplication, issue #134 bumped it to `v5b-8` for the validator's refusal of a finding without exactly one non-empty `Triggers when`, `Impact`, and `Change` field in that order, issue #135 bumped it to `v5b-9` for risk-led discovery, under which the primary may inspect an unchanged interface for a named risk before any candidate exists, issue #136 bumped it to `v5b-10` as the late bump owed to issue #70, whose early-dispatch change gave the follow-up batch a trigger it did not have while the identifier stayed at `v5b-1`, issue #185 bumped it to `v5b-11` for the clean-verdict attack that now depends on whether a material survivor remains rather than on whether any hygiene finding survived, issue #186 bumped it to `v5b-12` for separate compliance and compatibility dispositions on promises to change released behavior, issue #202 bumped it to `v5b-13` for complete-ledger clean-verdict attacks whenever no material finding survives, on every surface, and issue #139 bumped it to `v5b-14` for question admission that requires a named decision with a concrete effect on this merge, recorded deferrals that publish only when the change crosses the deferred boundary or leaves a material decision unresolved, and priority calibrated from demonstrated impact and reach rather than from confirmation. Issue #84 completes the paired provenance repair in `v5b-15` and audit `v2b-6`: whole-file findings and questions carry side/path from the pinned merge-base manifest, known deletions link there, and unestablished provenance stays explicitly unlinked. Issue #220 bumped it to `v5b-16` for the composition interface: `scripts/compose_review.py` renders comment, trailer, index, count, and section syntax from the reviewer's authoritative fields and authored prose, refuses contradictory or missing judgments by name, and validates before printing the payload, and a file-anchored finding or question carries its complete prose and trailer in the body. Issue #231 bumps it to `v5b-17`: `review-code` adds caller modes and a missing workflow-required issue now yields a review question instead of a stop; one fresh review per open pull request at its next run is accepted. Issue #277 bumps it to `v5b-18` and audit `v2b-6` to `v2b-7`: prior state now keys on the reviewer identity rather than on whoever writes everything else, so a review published by a GitHub App recognizes its own earlier reviews, and every login comparison ignores the trailing `[bot]` that REST carries and GraphQL omits; one fresh review per open pull request at its next run is accepted. Issue #280 advances it to `v5b-19`: unedited marked classification replies and their empty container reviews no longer defeat deduplication, while edits to the candidate review or its original comments remain later state. Issue #294 advances it to `v5b-20`: the core now takes an optional caller-supplied check-evidence input, accepts an item only when its identity, inputs, environment, completeness, and coverage match the review obligation, treats a new head as an invalidation boundary rather than an automatic rerun obligation, and keeps accepted, historical, and reviewer-executed evidence distinct in the record. The [#202 paper check](docs/research/clean-verdict-any-surface-2026-09-11.md) records historical exposure and measured-cost estimates without changing the experimental snapshots. A `v5b-1` trailer therefore names two different verification behaviors, and only the commit SHA that produced a review separates them. It is not a skill name. Callers and new prototypes invoke `$review-code-publish` from `main`.

## The review protocol

`code-review-publish` ships `references/review-protocol.md`, and `resolve-review` ships its addresser-side subset as `references/addressing-protocol.md`. The protocol fixes one shape for a finding comment and one for a reply, so both stay readable to a person and parseable by an agent:

```markdown
**[Code] Duplicated validation in `parseOrder`**

`src/order.ts:42` repeats the shape in `src/cart.ts:18`. `CODING_STANDARDS.md` §3: one home per rule.

**Change**: extract `assertOrderShape` and call it from both.

<!-- finding id=code/order-ts/duplicated-validation head=a1b2c3d -->
```

The trailer is invisible in GitHub's rendered view and present in the raw body through `gh api`. Its `id` slugs the axis, file, and finding title rather than a line number, so one finding keeps one identity across rounds even as the code moves under it. Replies carry the mirror form and a disposition — `implemented`, `already-addressed`, `answered`, `declined`, `needs-info`, or `blocked`.

A finding is blocking unless its title line says `[Suggestion]`, which marks the nice-to-have the author may close unactioned. The review reaches `Changes Requested` while any blocking finding is unsettled; otherwise it reaches `Needs Information` only when a concrete unanswered question could change the verdict; otherwise it is `Approved`. The question names the missing information and who should provide it, so the author knows how to move the review forward.

Forge permission chooses the submitted event, not the semantic status. `APPROVE` or `REQUEST_CHANGES` goes out only where the user or the repository's documented workflow authorizes the reviewer to gate a merge. `Needs Information`, a self-authored pull request, or an unauthorized reviewer uses `COMMENT` and states the status on the summary's first line, since a bare `COMMENT` says nothing about what should happen next. In that body, `Changes Requested` and `Approved` use the defined advisory forms so a recommendation cannot be mistaken for a gate.

Either skill can ask instead of guess. A reviewer that cannot judge code without knowing something raises a `[Question]` rather than inventing a finding an agent would then dutifully "fix"; an addresser stuck on a finding replies `needs-info`. Both ask a user in the session where there is one, and otherwise leave the question on the pull request, where it outlives the run — which is what makes the agent-to-human handoff work. A whole-change answer is recorded inside the addressing summary, preserving one general comment per round. Unanswered questions are listed in the summary and hold `Needs Information` until answered or withdrawn; they never age into approval.

Trailers speed the agent path but never gate it. A human reviewer's comment carries none, and both skills read it as prose and reply to it like any other.

Findings live on the lines they name, never bundled into the review body — the body indexes and totals. Every comment earns a reply, including one that rejects the finding. Both skills close threads as they finish them, whether the thread was fixed, answered, declined, or simply went obsolete, and either can reopen one whose fix regressed. The pull request under review is a fixed target: neither skill opens, retargets, or closes one, and fixes land on its existing head branch.

Resolving every thread is what makes a round invisible: the forge collapses resolved threads, so a round that answered everything renders like one that did nothing. `resolve-review` first reconciles the pull request title and description with the resulting diff and originating spec, preserving issue links and context that remain valid. It then closes the round with a single general comment — the head it addressed, counts by disposition linked to their threads, what still needs someone, each check with the head and input state it establishes — and an ask for a re-review that puts the round in the reviewer's queue. Where the forge routes review requests, that ask is a review request; where it will not route one — no review requests at all, or the reviewer is the pull request's own author — the summary carries a line mentioning the reviewer, which notifies them just the same. The forge's refusal is never itself reported on the pull request. One comment however large the round; the detail stays in the threads.

Re-reviewing, `code-review-publish` verdicts each prior finding against the code rather than against its reply — `fixed`, `accepted`, `obsolete`, or `not-fixed`. A decline does not close its own thread: the addresser states the position, and the reviewer's `accepted` verdict is what settles it, so a disagreement cannot be closed by the party that lost it. A finding declined once and then verified still unfixed is **disputed**: it stops being re-posted and is listed in the summary for a person to settle. Two rounds is the cap on any one finding, which is what keeps an unattended loop from re-litigating the same point forever.

Skills install one at a time, so neither file can point at the other; a change to the shared vocabulary lands in both.
