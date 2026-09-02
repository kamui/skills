# kamui/skills

Agent skills I use across coding projects.

## Install

Install from GitHub with the [`skills`](https://github.com/vercel-labs/skills) CLI:

```sh
npx skills@latest add kamui/skills
```

To install only one skill:

```sh
npx skills@latest add kamui/skills --skill code-review-publish
npx skills@latest add kamui/skills --skill code-review-deep-publish
npx skills@latest add kamui/skills --skill code-review-address
npx skills@latest add kamui/skills --skill implement-publish
```

Use `code-review-publish` for routine pull-request reviews. Use `code-review-deep-publish` for large or high-risk changes and review-skill evaluation runs, where the extra recall is worth roughly 1.5× the token cost.

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

The three routine-loop skills are model-invocable, so a driving agent can run the loop end to end. `code-review-deep-publish` is explicit-only. Each is directly invocable by name in [Codex](https://developers.openai.com/codex/skills), [Claude Code](https://code.claude.com/docs/en/skills), [Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md), and [OpenCode](https://opencode.ai/docs/skills/).

## Skills

The three skills compose into a loop: `implement-publish` opens a pull request, `code-review-publish` reviews it, `code-review-address` works the feedback, and the review runs again. Their visible comment and reply contracts keep the hand-offs readable to both people and agents; see [The review handoff](#the-review-handoff). `code-review-deep-publish` replaces the routine reviewer for a high-risk escalation or an evaluation run; it is not another loop stage.

### `code-review-publish`

Reviews the complete merge-base diff and publishes one forge-native review containing every verified finding. One integrated reviewer checks both implementation behavior and issue fit, falsifies each candidate, and invokes one fresh batched verifier only for proposed blockers and other consequential claims. The visible prose is authoritative; trailers support correlation and re-review without hiding meaning.

Each finding carries an impact priority and an independent action: `must-fix` blocks the merge, while `consider` is optional. The review reaches `Changes Requested`, `Incomplete`, `Needs Information`, or `Approved`, and reports its coverage. Publication is atomic against a freshly checked head; findings without an honest line anchor remain complete in the review body rather than being attached to unrelated code.

This workflow was evaluated as the v5 prototype in PR #17 and is now the production skill on `main`. New experiments that need that workflow invoke `code-review-publish` without the `-5` suffix.

It activates when a caller asks to review an issue-linked pull request and intends to post comments or a review to that pull request. Read-only review requests do not activate it. You can also invoke it directly:

```text
$code-review-publish
```

The host agent needs access to the pull request to publish the review.

### `code-review-address`

Addresses every review comment on a pull request, makes warranted changes, replies directly even when the answer is pushback, and resolves each thread as it finishes it. Re-addressing a pull request, it can reopen a thread that was resolved too early. Each round closes with one summary comment and an ask for a re-review, so a pull request whose threads are all resolved does not read as one where nothing happened.

The skill is deliberately independent of a particular code-review or implementation skill. Normal skill routing can select another installed skill when useful; if none applies, the model handles the work directly.

It activates when review feedback on a pull request needs working through, including as the fix step of a review loop. You can also invoke it directly:

```text
$code-review-address
```

The host agent needs write access to the pull request to post replies and resolve threads.

### `implement-publish`

Implements the work described by a spec, issue, or set of tickets, then opens one pull request containing the implementation. It delegates the implementation to the best matching installed skill, creates a suitable branch when the current one is not pull-request ready, and links the spec source in the pull-request body.

It stops at the pull request. `code-review-publish` reviews it from there.

It activates when a caller asks to implement work from a spec or issue and publish the result as a pull request. You can also invoke it directly:

```text
$implement-publish
```

The host agent needs access to the forge to create the pull request.

## The review handoff

`code-review-publish` owns finding admission, review status, and publication through [`references/review-rubric.md`](skills/code-review-publish/references/review-rubric.md) and [`references/output-contract.md`](skills/code-review-publish/references/output-contract.md). `code-review-address` owns replies, dispositions, thread state, and round closeout through its [`review-protocol.md`](skills/code-review-address/references/review-protocol.md).

A published finding is understandable from visible prose alone: its title states priority and action, and its `Triggers when`, `Impact`, and `Change` fields explain the defect and requested outcome. Optional findings explicitly say they may be closed without action. Hidden trailers add stable ids, reviewed heads, and correlation metadata for agents, but human comments without trailers remain first-class input.

The addresser evaluates every item against the current code and replies with one visible disposition: `implemented`, `already-addressed`, `answered`, `declined`, `needs-info`, or `blocked`. A reply states intent rather than proof, so the next review verifies it against the code. Findings that survive one verified decline become disputes for a person instead of looping indefinitely.

The reviewer submits one semantic status after coverage is known: `Changes Requested` for unsettled `must-fix` findings, `Incomplete` for unfinished material coverage or verification, `Needs Information` for an outcome-changing unanswered question, and `Approved` otherwise. Forge authorization controls only whether that status travels as `REQUEST_CHANGES`, `APPROVE`, or the default `COMMENT`; it never changes the conclusion.

The internal `workflow=v5-2` trailer remains the behavior version for deduplication and re-review continuity. It is not a skill name. Callers and new prototypes invoke `$code-review-publish` from `main`.
