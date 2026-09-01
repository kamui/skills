# Design notes

Why this skill is shaped the way it is. Written alongside the prototype so the reasoning survives the session that produced it.

## The problem

`code-review-publish` does not review. Its step 2 delegates: "invoke the model-invoked review skill whose description best matches the change." On a machine with Matt Pocock's `code-review` installed, that is what it lands on — not by design, but by description matching.

That is a reasonable default and a poor commitment. The reviewer is the part that determines whether the published review is worth reading, and it was being chosen by whatever happened to be installed.

## What the research found

A survey of thirteen published reviewers and review prompts — Anthropic's `code-review` plugin, Claude Code's built-in `/code-review`, `/security-review`, `pr-review-toolkit`, OpenAI Codex's review rubric, Qodo pr-agent, `obra/superpowers`, `claude-code-action`, `ai-pr-reviewer`, the closed hosted tools, and the community persona collections — is recorded in `docs/research/agentic-code-review-candidates.md`.

Its central finding drives this skill's whole shape:

**No published artifact combines a real requirements axis with serious false-positive machinery.** The two families split cleanly.

- The precision leaders — Codex's rubric, Anthropic's plugin, the Claude Code built-in, `/security-review` — are **all code-only**. Not one of them reads the originating issue.
- The requirements-capable artifacts — pr-agent's `TicketCompliance`, superpowers' plan alignment, Pocock's Spec axis — all have weak-to-absent noise control.

So there is nothing to adopt whole. This skill takes the precision rubric from one family, the requirements axis from the other, and adds a verification stage that neither publishes.

Relevant evidence beyond the prompt reading, with the caveats it deserves:

- **c-CRAB** (arXiv 2603.23448) measured four agents against human PR reviews. The union of all four scored 41.5% against 32.1% for the best single one — stacking reviewers buys much less than expected, because they miss the same things. Its manual usefulness audit *inverted* the pass-rate ranking, and the authors warn that agents over-raise robustness and testing concerns relative to humans.
- **There is no controlled measurement** that a confidence threshold, a verify pass, or diff-only context reduces false-positive rate. The `>80% confidence` and three-state-verdict patterns are converged industry practice across four Anthropic artifacts and Codex. Convergence is meaningful; it is not measurement. Nobody's threshold is empirically calibrated.

## The constraints this skill was built against

1. **Called often.** Token cost per run is a first-class concern, not an afterthought.
2. **One-shot and unattended.** It runs to post a review. Anything that stops to ask the user is a liability.
3. **Two readers.** A human triages the output *and* an agent may act on it. Either might respond.
4. **The linked issue is read.** Requirements coverage is kept, deliberately, as the thing most published reviewers lack.
5. **The protocol is not binding.** `code-review-publish`'s `references/review-protocol.md` is directional here. It was built around the previous reviewer's output shape, and this skill's finding contract carries fields it has no slot for.

Constraint 3 is the one that most distinguishes this skill from everything surveyed. A human reads severity as advice and applies judgment. An agent reads it as an instruction and does the work. A review written for only one of them fails the other.

## Decisions

### Base on the Codex rubric

Apache-2.0, single Markdown file, zero interactivity. Three properties decided it:

- Its **eight qualifying criteria** are the best-stated flag/no-flag test found anywhere. Four of them each kill a class of finding outright: "introduced in the commit", "the author would likely fix it", "must identify the other parts provably affected", "clearly not just an intentional change".
- Its **output contract** is the only one of the candidates designed for findings read at volume — per-finding priority and confidence, tight line ranges, explicit brevity rules.
- It carries **no orchestration**, so it composes with whatever phase structure is imposed. Pocock's skill and pr-agent both arrive with structure that would have to be dismantled first.

The cost is that it has no requirements axis at all, so reading the issue became a mandatory graft rather than an optional one.

### Graft the Requirements axis from pr-agent

`TicketCompliance` is the only structured requirements prompt in public. Three parts were taken:

- **Restate the requirements first, in the model's own words.** Checking a diff against requirements that were never restated is where invented requirements come from — the model reads the diff, infers what the issue "must have" wanted, then reports the diff for failing to do it.
- **The "cannot tell from the code" bucket.** Without it an uncertain requirement becomes either a false finding or a silent omission.
- **The asymmetric flag rule** — thorough on bugs and security, demanding on everything lower.

### Graft the scope-creep bucket from Pocock

`TicketCompliance` is compliance-shaped: it walks from requirements to code. It has no slot for *behavior in the diff that nobody asked for*, which only shows walking the other way. Pocock's Spec brief is where that comes from, and it is the one thing his skill has that neither other candidate does.

The Fowler smell baseline was **not** taken. A twelve-item design-taste checklist handed to an agent with an instruction to find instances is close to the worst-case prompt shape for precision.

### Keep the verify pass — and drop the fan-out

An earlier draft of this reasoning argued that "called often" ruled out a verify pass. That was wrong, and the correction matters enough to record.

It conflated two things that co-occur in the surveyed pipelines:

- **Fan-out** — five parallel finders in Anthropic's plugin, ten in the built-in's high-effort variant — multiplies the *expensive* pass, since every finder re-reads the whole diff and its context. Frequency genuinely argues against this, and c-CRAB's union result is evidence it buys little.
- **Verification** adds a *cheap* pass. The finder ingests the full diff plus enclosing functions; the verifier ingests a short claim list plus narrow windows around each cited line.

The passes are not symmetric, so verification does not double anything. And frequency amplifies the savings as well as the cost: a false positive that survives costs a human's attention, or — in a publish-then-address loop — an entire round where an agent dutifully fixes a non-bug. Verification is plausibly net token-negative.

So: one finder per axis, no fan-out, one verifier.

### The fresh context is the mechanism

The verifier receives the claims and the repository, not the finders' reasoning. Asking the same context "are you sure?" returns agreement, because the finding is already in its history as something it asserted. That is a self-consistency check and worth almost nothing. A verifier that never saw the argument has to reconstruct the bug from the code or fail to.

The three-state vocabulary — `confirmed` / `plausible` / `refuted`, defaulting to `plausible`, with `refuted` requiring a quoted line that proves it — is preferred over a bare confidence float because it forces the verifier to produce evidence rather than a number. A verifier that refutes on uncertainty deletes real bugs and reports a clean review; one that confirms on plausibility passes the finders' noise straight through. The middle verdict exists so neither has to happen.

### `plausible` publishes as a question, not a finding

This follows directly from constraint 3. An agent handed an unproven finding will change working code to satisfy a scenario nobody demonstrated. Asking costs a round; a wrong fix costs a round *and* the code.

### Action alongside priority

The core of the dual-audience contract. `priority` (P0–P3) is the human's triage order. `action` (`must-fix` / `consider` / `question`) is the agent's instruction. Requiring an agent to infer an action from a rank is where over-compliance comes from — agents fix a P3 as readily as a P0.

Action derives from priority by a stated rule, so one judgment produces both renderings and they cannot drift.

### `consider` carries an explicit permission line

A human seeing an optional label closes it unactioned; an agent frequently does the work anyway. So the low band says it in words — "Closing this without action is a correct response" — rather than trusting a label to imply it. Without this line, every finding becomes work regardless of its label, and the precision machinery grafted in upstream is undone at the last step.

### `Triggers when` is a required field

For a human, a diagnosis is enough — they work the fix out. An agent handed only a diagnosis invents one, and has no test for whether its fix worked. The trigger field is what makes a finding checkable by whoever acts on it. A candidate that cannot name its trigger is routed to a question.

### Pre-existing bugs are out of scope

Codex criterion 4. This is contested and the alternative is defensible: Claude Code's built-in explicitly puts bugs on unchanged lines of a touched function *in* scope, because the change re-exposes them. The strict reading is taken here because every finding this skill publishes becomes a work request against the author of this change. The counter-argument is recorded in `references/code-axis.md` so it can be flipped after seeing real output.

## What is original

The dual-audience finding contract: `action` beside `priority`, the explicit permission line, the required `trigger`, the trailer as machine-authoritative copy of the human-facing tag line, and the routing of verified-`plausible` candidates to questions. That contract is the reason the skill is assembled rather than adopted, and it is what `references/finding-format.md` exists to specify.

Claude Code's built-in `/code-review` informed the *design* of `references/verify.md` — its three-state vocabulary and refute-with-evidence asymmetry are good engineering. It is proprietary and compiled into the CLI; no text is taken from it, and none should be. Its `ReportFindings` tool schema is worth studying as independent confirmation of the dual-audience premise: it carries both `summary` and `short_summary` for two rendering contexts, a distinct `failure_scenario`, and an `outcome` field set only when re-reporting after fixes — an agent-response channel built into the finding itself.

## Known friction, from the first real run

Tested against `kamui/shortlist#65`, an issue-linked PR with nine acceptance criteria. Two finders produced 4 candidates; the verifier confirmed 3, merged 1 as a duplicate of another, refuted 0, corrected one trigger it found overstated, and demoted one priority. Three findings published. Two problems surfaced. Both were the same mistake in two places — **one field doing two jobs for two different consumers** — and both are now resolved in the contract.

**Anchoring versus the fix site.** `file`/`line` was carrying both "where the reader should see this" and "where the edit goes." The forge constrains the first (GitHub takes line comments only on diff lines) and nothing constrains the second. Two of three findings in this run had fix sites outside the diff — one in `CONTEXT.md`, untouched by the change; one at a validator gate the change never edited.

Resolved by splitting `anchor` from `fix`, with an ordered ladder for choosing the anchor when the fix site is not in the diff: the line that makes the finding true, else the line that most directly demonstrates it, else the review body — never an unrelated line picked just to get a line comment. The trailer gained a `fix=` key, which matters more than it looks under constraint 3: a human reads the `Change` prose and goes where it says, but an agent that parsed only the anchor would edit the wrong line.

**What the verifier may see.** `evidence` was carrying both "what is alleged" and "why the finder believes it." Passing it whole erodes the fresh-context property the verify step depends on; stripping it aggressively starves the verifier and biases it toward refuting. The claims were compressed by hand for this run.

Resolved by splitting `claim` from `support` at the finder, so the boundary is in the schema rather than in a judgment call at hand-off time. The test: **the claim describes the artifact; the support describes the finder.** Quoted repository and spec lines are facts about the artifact and stay in the claim, so the split withholds argument rather than evidence. Only `support` is withheld — and withholding it is correct rather than merely tolerable, because a verifier told a demonstration already succeeded believes it, and the step decays into agreement. `support` also gives a finder somewhere to put hedging that currently leaks into the published finding.

**Not yet exercised:** the re-review path, the round cap, thread resolution, and the `Needs Information` status. The first run produced no `plausible` verdicts, so the question path is untested end to end.
