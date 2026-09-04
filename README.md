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
npx skills@latest add kamui/skills --skill code-review-publish-legacy  # legacy, kept for historical purposes
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

Three skills are model-invocable, so a driving agent can run the loop end to end; `code-review-publish-legacy` is not model-invocable and runs only when invoked by name. Each skill is also directly invocable by name in [Codex](https://developers.openai.com/codex/skills), [Claude Code](https://code.claude.com/docs/en/skills), [Pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md), and [OpenCode](https://opencode.ai/docs/skills/).

Skills that ship scripts run them with `python3` on the standard library alone, Python 3.9 or newer, and need `git`. macOS and Linux, including WSL, are the supported platforms; native Windows is not.

## Skills

The skills compose into a loop: `implement-publish` opens a pull request, `code-review-publish` reviews it, `code-review-address` works the feedback, and the review runs again. Their visible comment and reply contracts keep the hand-offs readable to both people and agents; see [The review handoff](#the-review-handoff).

### `code-review-publish`

Reviews the complete merge-base diff and publishes one forge-native review containing every verified finding. One integrated reviewer checks both implementation behavior and issue fit against a private evidence rubric, falsifies each candidate, and invokes one fresh batched verifier for every proposed `must-fix` and other consequential claim — security, data loss, compatibility. A mechanical validator checks the assembled payload before anything is written.

Each finding carries an impact priority and an independent action: `must-fix` blocks the merge, while `consider` is optional. The review reaches `Changes Requested`, `Incomplete`, `Needs Information`, or `Approved`, and reports its coverage. Publication is atomic against a freshly checked head; findings without an honest line anchor remain complete in the review body rather than being attached to unrelated code.

Findings, questions, and observations are separate channels, so uncertainty routes to a question instead of becoming a finding an agent would dutifully "fix". A run trailer records the workflow version and a context digest, so an unchanged pull request is reported rather than re-reviewed. This workflow was evaluated as the v5a prototype; it supersedes the v5 workflow that previously filled this skill and the two-axis reviewer, now kept as `code-review-publish-legacy` for historical purposes.

It activates when a caller asks to review an issue-linked pull request and intends to post comments or a review to that pull request. Read-only review requests do not activate it. You can also invoke it directly:

```text
$code-review-publish
```

The host agent needs access to the pull request to publish the review.

### `code-review-publish-legacy`

The former `code-review-publish`, kept for historical purposes. It reviews a change along two axes — **Code** (correctness and implementation quality) and **Requirements** (fidelity to the originating spec) — and publishes the findings as line comments under one status, using the shared review protocol below. It is not model-invocable: `code-review-publish` should be used instead, and this skill runs only when explicitly invoked by name:

```text
$code-review-publish-legacy
```

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

The internal `workflow=v5a-1` trailer remains the behavior version for deduplication and re-review continuity. It is not a skill name. Callers and new prototypes invoke `$code-review-publish` from `main`.

## The review protocol

`code-review-publish-legacy` and `code-review-address` each ship `references/review-protocol.md`. It fixes one shape for a finding comment and one for a reply, so both stay readable to a person and parseable by an agent:

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

Findings live on the lines they name, never bundled into the review body — the body indexes and totals. Every comment earns a reply, including one that rejects the finding. Both skills close threads as they finish them, whether the thread was fixed, answered, declined, or simply went obsolete, and either can reopen one whose fix regressed. The pull request under review is a fixed target: neither skill opens, retargets, or closes one, and fixes land on its existing head branch. Where the forge supports reactions, both skills use them as a signal on top of a reply: `+1` agreed, `eyes` in progress, `-1` disagreed with the reason in the reply, `confused` where the comment is unclear.

Resolving every thread is what makes a round invisible: the forge collapses resolved threads, so a round that answered everything renders like one that did nothing. `code-review-address` first reconciles the pull request title and description with the resulting diff and originating spec, preserving issue links and context that remain valid. It then closes the round with a single general comment — the head it addressed, counts by disposition linked to their threads, what still needs someone, the checks run — and an ask for a re-review that puts the round in the reviewer's queue. Where the forge routes review requests, that ask is a review request; where it will not route one — no review requests at all, or the reviewer is the pull request's own author — the summary carries a line mentioning the reviewer, which notifies them just the same. The forge's refusal is never itself reported on the pull request. One comment however large the round; the detail stays in the threads.

Re-reviewing, `code-review-publish-legacy` verdicts each prior finding against the code rather than against its reply — `fixed`, `accepted`, `obsolete`, or `not-fixed`. A decline does not close its own thread: the addresser states the position, and the reviewer's `accepted` verdict is what settles it, so a disagreement cannot be closed by the party that lost it. A finding declined once and then verified still unfixed is **disputed**: it stops being re-posted and is listed in the summary for a person to settle. Two rounds is the cap on any one finding, which is what keeps an unattended loop from re-litigating the same point forever.

The two copies of the file are byte-identical because skills install one at a time and neither can point at the other's copy. Edit them together.
