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

All three skills are model-invocable, so a driving agent can run the loop end to end. Each is also directly invocable by name in [Codex](https://developers.openai.com/codex/skills), [Claude Code](https://code.claude.com/docs/en/skills), [Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md), and [OpenCode](https://opencode.ai/docs/skills/).

## Skills

The three skills compose into a loop: `implement-publish` opens a pull request, `code-review-publish` reviews it, `code-review-address` works the feedback, and the review runs again. A shared review protocol is what makes the hand-offs work; see [The review protocol](#the-review-protocol).

### `code-review-publish`

Reviews a change and publishes it through the forge's review system: the summary as the review body, and one line comment per finding on the code that finding names. Where a forge has no review system or refuses the review, the summary falls back to a single pull-request comment. Nothing is published to the originating issue, which serves only as the spec source.

The skill uses the best matching model-invoked code-review skill available. If none is installed, the model performs the review directly. It keeps **Code** findings about correctness and implementation quality separate from **Requirements** findings about fidelity to the originating spec, and reaches one status — `Changes Requested`, `Approved`, or `Feedback` — so the author knows whether anything stops the merge before reading a single finding.

It activates when a caller asks to review an issue-linked pull request and intends to post comments or a review to that pull request. Read-only review requests do not activate it. You can also invoke it directly:

```text
$code-review-publish
```

The host agent needs access to the pull request to publish the review.

### `code-review-address`

Addresses every review comment on a pull request, makes warranted changes, replies directly even when the answer is pushback, and resolves each thread as it finishes it. Re-addressing a pull request, it can reopen a thread that was resolved too early. Each round closes with one summary comment and a re-review request, so a pull request whose threads are all resolved does not read as one where nothing happened.

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

## The review protocol

`code-review-publish` and `code-review-address` each ship `references/review-protocol.md`, the contract they hand work across. It fixes one shape for a finding comment and one for a reply, so both stay readable to a person and parseable by an agent:

```markdown
**[Code] Duplicated validation in `parseOrder`**

`src/order.ts:42` repeats the shape in `src/cart.ts:18`. `CODING_STANDARDS.md` §3: one home per rule.

**Change**: extract `assertOrderShape` and call it from both.

<!-- finding id=code/order-ts/duplicated-validation head=a1b2c3d -->
```

The trailer is invisible in GitHub's rendered view and present in the raw body through `gh api`. Its `id` slugs the axis, file, and finding title rather than a line number, so one finding keeps one identity across rounds even as the code moves under it. Replies carry the mirror form and a disposition — `implemented`, `already-addressed`, `answered`, `declined`, `needs-info`, or `blocked`.

A finding is blocking unless its title line says `[Optional]`, which marks the nice-to-have the author may close unactioned. Those add up to one status per review: `Changes Requested` while any blocking finding is unsettled, `Approved` where nothing blocks the merge, `Feedback` where nothing blocks it but the review cannot vouch for the change — approval unauthorized, an axis unassessed, or an open question that could change a verdict. The status is derived from the findings, not judged separately.

Where the forge has a review system, the submitted event is the status, and `APPROVE` or `REQUEST_CHANGES` goes out only where the user or the repository's documented workflow authorizes the reviewer to gate a merge. Where no event can carry it — no review system, a self-authored pull request GitHub will only take a `COMMENT` on, or an unauthorized reviewer — the summary's first line states the status in words, since a bare `COMMENT` tells the author nothing about whether anything stops the merge. `Feedback` is the third status rather than `Commented` because on that path every entry on the pull request is already a comment.

Either skill can ask instead of guess. A reviewer that cannot judge code without knowing something raises a `[Question]` rather than inventing a finding an agent would then dutifully "fix"; an addresser stuck on a finding replies `needs-info`. Both ask a user in the session where there is one, and otherwise leave the question on the pull request, where it outlives the run — which is what makes the agent-to-human handoff work. Unanswered questions are listed in the summary.

Trailers speed the agent path but never gate it. A human reviewer's comment carries none, and both skills read it as prose and reply to it like any other.

Findings live on the lines they name, never bundled into the review body — the body indexes and totals. Every comment earns a reply, including one that rejects the finding. Both skills close threads as they finish them, whether the thread was fixed, answered, declined, or simply went obsolete, and either can reopen one whose fix regressed. The pull request under review is a fixed target: neither skill opens, retargets, or closes one, and fixes land on its existing head branch. Where the forge supports reactions, both skills use them as a signal on top of a reply: `+1` agreed, `eyes` in progress, `-1` disagreed with the reason in the reply, `confused` where the comment is unclear.

Resolving every thread is what makes a round invisible: the forge collapses resolved threads, so a round that answered everything renders like one that did nothing. `code-review-address` closes each round with a single general comment — the head it addressed, counts by disposition linked to their threads, what still needs someone, the checks run — and, where the forge routes them, a re-review request putting the round in the reviewer's queue. One comment however large the round; the detail stays in the threads.

Re-reviewing, `code-review-publish` verdicts each prior finding against the code rather than against its reply — `fixed`, `accepted`, `obsolete`, or `not-fixed`. A decline does not close its own thread: the addresser states the position, and the reviewer's `accepted` verdict is what settles it, so a disagreement cannot be closed by the party that lost it. A finding declined once and then verified still unfixed is **disputed**: it stops being re-posted and is listed in the summary for a person to settle. Two rounds is the cap on any one finding, which is what keeps an unattended loop from re-litigating the same point forever.

The two copies of the file are byte-identical because skills install one at a time and neither can point at the other's copy. Edit them together.
