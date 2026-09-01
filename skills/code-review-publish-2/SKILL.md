---
name: code-review-publish-2
description: "Prototype reviewer. Review an issue-linked pull request on two axes — Code and Requirements — verify every candidate finding in a fresh context, and publish the survivors as line comments under one status. Findings are written to be acted on by a human or an agent. Use when the caller explicitly asks for code-review-publish-2; otherwise prefer code-review-publish."
---

# Publish code review (prototype)

Review the pull request, verify what the review found, publish what survives.

This is a prototype of `code-review-publish` built on a different reviewer. It does the reviewing itself rather than delegating to whichever review skill happens to be installed, because the finding contract below is the point of the skill and a delegated reviewer will not honor it.

Two properties govern every decision here:

**Never ask the user anything.** This runs unattended to post a review. Where you would ask, publish a `question` finding instead and let the status carry it. The one exception is an operational failure that prevents reviewing at all — stop and report that rather than publishing a review you could not complete.

**Every finding has two readers.** A human triages it; an agent acts on it. A human reads severity as advice and applies judgment; an agent reads it as an instruction and does the work. So each finding carries a human-facing priority *and* an agent-facing action, and the low band says in words that closing it unactioned is correct. See [`references/finding-format.md`](references/finding-format.md), which is the contract the whole skill exists to produce.

## Process

### 1. Resolve the targets

Read `docs/agents/issue-tracker.md` when present for the forge's verbs. Then resolve, without asking:

- the pull request, its head SHA (`headRefOid`), and its base branch;
- the comparison base — the merge-base of the head with the base branch, which is what the pull request already means. Take a different fixed point only when the caller supplies one;
- the originating issue, from `Closes #n` / `Fixes #n` / a bare `#n` in the pull request body, then the branch name, then the commit messages. This is the spec source. Read it with its comments;
- the posting identity (`gh api user --jq .login`), and whether it authored the pull request;
- any earlier review from that identity: its `commit_id`, its findings' ids and trailers, the replies on those threads, and thread resolution state.

No pull request means there is nothing to publish to. Stop and report it; opening one is `implement-publish`'s job.

No originating issue is a normal state, not a failure. The Requirements axis becomes `Not applicable` and the Code axis runs alone. Do not invent requirements, and do not fall back to the pull request description as a spec — a description written by the author restates the diff, so checking the diff against it always passes.

An earlier review at a different head makes this a re-review. Keep the original comparison base; use the earlier head only to locate what changed since.

### 2. Find

Spawn **two sub-agents in parallel**, one per axis. No further fan-out: extra finders over the same diff multiply the expensive pass and buy little, because they miss the same things.

Give each the comparison base, the head, the diff command (`git diff <base>...<head>`, three-dot), the commit list, and the absolute path to its brief, which it reads first:

- **Code** — [`references/code-axis.md`](references/code-axis.md). Correctness, documented repository standards, implementation quality.
- **Requirements** — [`references/requirements-axis.md`](references/requirements-axis.md). Also give it the issue text. Missing, partial, or incorrect behavior against the spec, plus behavior the spec never asked for.

Both return *candidates*, not findings. A candidate is not yet publishable and the finders are told to be generous within their rubric: a finder that silently drops what it half-believes bypasses step 3, which is where half-believed things are supposed to be settled.

Re-reviewing, also give each finder the prior findings for its axis so it does not re-derive them from scratch under new ids.

### 3. Verify

Spawn **one sub-agent with a fresh context** and the brief in [`references/verify.md`](references/verify.md). Give it the merged candidate list and the repository. Do not give it the finders' reasoning.

The fresh context is the entire mechanism. A verifier that has already seen why the finder believed something agrees with itself, which checks nothing. A verifier that has only the claim must reconstruct it from the code or fail to.

It returns one verdict per candidate — `confirmed`, `plausible`, or `refuted` — and a deduplicated list. Then:

- `refuted` is dropped silently. It never reaches the pull request and is not mentioned in the summary.
- `confirmed` becomes a finding at its priority.
- `plausible` becomes a **question**, whatever its priority. The mechanism is real but the trigger is not established, and an agent handed that as a finding will change working code to satisfy a scenario nobody has demonstrated. Asking costs a round; a wrong fix costs a round *and* the code.

If the verifier returns nothing, that is a clean review, not a failure.

Carry the Requirements finder's restated requirement list and its met / not-met / unverifiable counts through to step 4. The axis outcome is derived from those, not from how many findings survived verification: an axis whose requirements are all met is `Passed`, and so is one whose every candidate was refuted. Both are different statements from `Not applicable`, which means the axis was never in scope.

### 4. Publish once

Follow [`references/publishing.md`](references/publishing.md) for the comment shape's transport, the status ladder, and the forge verbs.

One review: the summary as its body, the findings as its line comments, submitted in one call. Every finding that names code goes on that code — the body indexes, the line comments carry the detail, and whoever acts on a finding acts from its comment alone.

Re-reviewing, verdict every prior finding against the current code before writing anything, reply on its existing thread rather than posting a new comment, and resolve what you settle. A finding declined once and still standing is disputed: list it in the summary and stop re-posting it. Two rounds is the cap on any one finding, and that cap is what stops two agents re-litigating a point forever.

Attempt each write once. On an ambiguous result, read the target before a single retry, then report the failure rather than posting again.

Finish by reporting: the status, the review link, counts by axis and action, the questions raised, anything dropped as refuted (count only), and anything that failed to publish.

## Why this shape

The goals, the research behind them, and the decisions they forced are in [`DESIGN.md`](DESIGN.md), including the ones still contested.

The reviewing rubric is adapted from OpenAI Codex's review rubric; the requirements axis from Qodo pr-agent's ticket-compliance prompt; the scope-creep bucket from Matt Pocock's `code-review`; the exclusion taxonomy from Anthropic's `code-review` plugin. All permissively licensed — see [`references/ATTRIBUTION.md`](references/ATTRIBUTION.md).

The reason it is assembled rather than adopted whole: no published reviewer combines a real requirements axis with serious false-positive machinery. The artifacts with the best precision rubrics never read the issue; the ones that check the change against its spec barely filter. This skill takes the precision rubric from one family and the requirements axis from the other, and adds the verify pass neither publishes.

`references/review-protocol.md` in `code-review-publish` is the ancestor of the comment shape, the status ladder, the disposition vocabulary, and the round cap. It is directional here, not binding: this skill's finding contract carries fields that protocol has no slot for, and the two are not interchangeable on one pull request.
