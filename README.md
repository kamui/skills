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
npx skills@latest add kamui/skills --skill code-review-address
npx skills@latest add kamui/skills --skill implement-publish
```

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

[Codex](https://developers.openai.com/codex/skills), [Claude Code](https://code.claude.com/docs/en/skills), and [Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md) honor explicit-only metadata for manually invoked skills. [OpenCode](https://opencode.ai/docs/skills/) currently has no documented equivalent, so `code-review-address` also carries an explicit-only instruction in its description.

## Skills

### `code-review-publish`

Reviews a change and publishes one pull-request line comment per finding plus a review summary comment on the pull request. When the pull-request author and the reviewer are the same user, the summary is posted as a general pull-request comment. Nothing is published to the originating issue, which serves only as the spec source.

The skill uses the best matching model-invoked code-review skill available. If none is installed, the model performs the review directly. It keeps repository-standards and originating-spec findings separate.

It activates when a caller asks to review an issue-linked pull request and intends to post comments or a review to that pull request. Read-only review requests do not activate it. You can also invoke it directly:

```text
$code-review-publish
```

The host agent needs access to the pull request to publish the review.

### `code-review-address`

Addresses every review comment on a pull request, makes warranted changes, replies directly even when no change is needed, and resolves or reacts to comments when the provider supports those actions.

The skill is deliberately independent of a particular code-review or implementation skill. Normal skill routing can select another installed skill when useful; if none applies, the model handles the work directly.

This skill is manually invoked:

```text
$code-review-address
```

Use the equivalent explicit skill syntax in other harnesses. The host agent needs write access to the pull request to post replies, resolve threads, and add reactions.

### `implement-publish`

Implements the work described by a spec, issue, or set of tickets, then opens one pull request containing the implementation. It delegates the implementation to the best matching installed skill, creates a suitable branch when the current one is not pull-request ready, and links the spec source in the pull-request body.

It stops at the pull request. Run `code-review-publish` afterwards to review it.

It activates when a caller asks to implement work from a spec or issue and publish the result as a pull request. You can also invoke it directly:

```text
$implement-publish
```

The host agent needs access to the forge to create the pull request.
