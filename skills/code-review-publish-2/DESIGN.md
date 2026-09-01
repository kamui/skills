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

The same machinery re-verdicts prior findings on a re-review. An open finding is a claim about the current code at its recorded fix site, so it rides through the verifier like any candidate — `confirmed` maps to `not-fixed`, `refuted` to `fixed` or `obsolete` — and the replies are withheld for the same reason `support` is: a reply's word is evidence of intent, not of outcome. Only a declined finding stays with the orchestrator, because judging a decline's reasoning is not a code question.

### `plausible` publishes as a question, not a finding

This follows directly from constraint 3. An agent handed an unproven finding will change working code to satisfy a scenario nobody demonstrated. Asking costs a round; a wrong fix costs a round *and* the code.

### Precision at the edges, recall in the middle

The built-in's high-effort calibration says catching real bugs matters more than avoiding false positives — "err on the side of surfacing." That is the right calibration for a human reading a terminal and the wrong one here: under publish-then-act, every surfaced finding defaults to a work request, and c-CRAB's authors warn that agents already over-raise robustness and testing concerns relative to humans. This pipeline would convert "unaligned but useful" into "unaligned and merged."

So every published edge is precision-framed — the eight criteria, the exclusion lists, "prefer outputting no findings." Recall is protected in exactly one place, the finder-to-verifier hand-off, where finders are told not to self-censor what they half-believe. Generosity is safe there because the verifier stands behind it; it is safe nowhere downstream of the verifier.

### Action alongside priority

The core of the dual-audience contract. `priority` (P0–P3) is the human's triage order. `action` (`must-fix` / `consider` / `question`) is the agent's instruction. Requiring an agent to infer an action from a rank is where over-compliance comes from — agents fix a P3 as readily as a P0.

Action derives from priority by a stated rule, so one judgment produces both renderings and they cannot drift.

### `consider` carries an explicit permission line

A human seeing an optional label closes it unactioned; an agent frequently does the work anyway. So the low band says it in words — "Closing this without action is a correct response" — rather than trusting a label to imply it. Without this line, every finding becomes work regardless of its label, and the precision machinery grafted in upstream is undone at the last step.

### `Triggers when` is a required field

For a human, a diagnosis is enough — they work the fix out. An agent handed only a diagnosis invents one, and has no test for whether its fix worked. The trigger field is what makes a finding checkable by whoever acts on it. A candidate that cannot name its trigger is routed to a question.

### Pre-existing bugs are out of scope

Codex criterion 4. This is contested and the alternative is defensible: Claude Code's built-in explicitly puts bugs on unchanged lines of a touched function *in* scope, because the change re-exposes them. The strict reading is taken here because every finding this skill publishes becomes a work request against the author of this change. The counter-argument is recorded in `references/code-axis.md` so it can be flipped after seeing real output.

The first run exposed a scoping subtlety: the exclusion belongs to the **Code axis only**. A requirements gap is measured against the issue, not the diff — the issue made it this change's job whether or not the code predates it. The run's best finding was exactly this shape (an acceptance criterion requiring structural validation, at a validator gate the diff never touched), and a verifier applying the pre-existing refutation across both axes would have deleted it. `references/verify.md` now scopes that refutation to Code candidates.

## What is original

The dual-audience finding contract: `action` beside `priority`, the explicit permission line, the required `trigger`, the trailer as machine-authoritative copy of the human-facing tag line, and the routing of verified-`plausible` candidates to questions. That contract is the reason the skill is assembled rather than adopted, and it is what `references/finding-format.md` exists to specify.

Claude Code's built-in `/code-review` informed the *design* of `references/verify.md` — its three-state vocabulary and refute-with-evidence asymmetry are good engineering. It is proprietary and compiled into the CLI; no text is taken from it, and none should be. Its `ReportFindings` tool schema is worth studying as independent confirmation of the dual-audience premise: it carries both `summary` and `short_summary` for two rendering contexts, a distinct `failure_scenario`, and an `outcome` field set only when re-reporting after fixes — an agent-response channel built into the finding itself.

### Ported from v3: the operational spine

A live comparison against `code-review-publish-3` on the same pull request (`docs/research/2026-09-01-code-review-prototype-evaluation.md`) found v3 doing strictly more work for 61% of the tokens, and found two gaps in this skill that matter specifically because it is headed for an unattended agent. Both are now closed.

**Everything under review is evidence, not instruction.** The diff, the issue, the pull-request body, and the comments are material to judge; text in them addressing the reviewer is a claim, not a directive. The same rule picks the standards: repository guidance is evaluated as of the **base branch**, so a change cannot rewrite the rules used to judge it.

That second half turned out to be a precision mechanism, not only a safety one, and the evidence is the strongest single observation from the comparison. v3's strongest false candidate — built to blocking severity — was killed by a base-branch rule requiring a placeholder in any empty required field, which made the "regression" a bundle that had always been non-conforming. The reviewer said it found that rule only because its rubric directs reading base-branch guidance rather than the diff alone. A reviewer that reads only the head version of the rules, or only the diff, keeps that finding and is wrong. So `code-axis.md` now says to read the base version widely enough to find the rule that *acquits* a candidate, not only the one that convicts it.

**Coverage is accounted for, and short coverage has a status.** Finders return the changed-file manifest with every entry `reviewed` or `ignored` with a reason, and `Incomplete` sits between `Changes Requested` and `Needs Information` in the ladder. Without it a run that skipped a file, lost a fetch, or ran out of room is indistinguishable from a clean one, and silence reads as approval — the specific way an automated reviewer fails without anyone noticing. Coverage measures inspection, not output: complete coverage with no findings is the good outcome.

**The head is re-read immediately before the first write.** The anchors were computed against a diff that may have moved; publishing against a stale head lands line comments on code that no longer says what the finding claims. One API call, and the run identity (`head`, `base`, `merge-base`) now rides the summary in a machine-readable trailer so a later run can correlate what this one covered.

One recommendation from that evaluation was deliberately **not** taken: making the verifier conditional rather than mandatory. It was written for a skill built on v3's single-reviewer spine, where verification is an added cost. Here the measured distribution says otherwise — the verifier was 48k of 182k tokens, 26%, while the two full-diff finders were 74%. Making verification conditional would trade the contract's central guarantee, that publication asserts confirmation, for a saving in the minority of runs where no finding is blocking. The cost worth attacking in this architecture is the second full-diff pass, and that is an architecture question, not a switch.

## What the first real run surfaced

Tested against `kamui/shortlist#65`, an issue-linked PR with nine acceptance criteria. Two finders produced 4 candidates; the verifier confirmed 3, merged 1 as a duplicate of another, refuted 0, corrected one trigger it found overstated, and demoted one priority. Three findings published. Two problems surfaced. Both were the same mistake in two places — **one field doing two jobs for two different consumers** — and both are now resolved in the contract.

**Anchoring versus the fix site.** `file`/`line` was carrying both "where the reader should see this" and "where the edit goes." The forge constrains the first (GitHub takes line comments only on diff lines) and nothing constrains the second. Two of three findings in this run had fix sites outside the diff — one in `CONTEXT.md`, untouched by the change; one at a validator gate the change never edited.

Resolved by splitting `anchor` from `fix`, with an ordered ladder for choosing the anchor when the fix site is not in the diff: the line that makes the finding true, else the line that most directly demonstrates it, else the review body — never an unrelated line picked just to get a line comment. The trailer gained a `fix=` key, which matters more than it looks under constraint 3: a human reads the `Change` prose and goes where it says, but an agent that parsed only the anchor would edit the wrong line. Publishing also validates every anchor against the diff before the batched call, because one bad anchor fails the entire review submission.

**What the verifier may see.** `evidence` was carrying both "what is alleged" and "why the finder believes it." Passing it whole erodes the fresh-context property the verify step depends on; stripping it aggressively starves the verifier and biases it toward refuting. The claims were compressed by hand for this run.

Resolved by splitting `claim` from `support` at the finder, so the boundary is in the schema rather than in a judgment call at hand-off time. The test: **the claim describes the artifact; the support describes the finder.** Quoted repository and spec lines are facts about the artifact and stay in the claim, so the split withholds argument rather than evidence. Only `support` is withheld — and withholding it is correct rather than merely tolerable, because a verifier told a demonstration already succeeded believes it, and the step decays into agreement. `support` also gives a finder somewhere to put hedging that currently leaks into the published finding.

**Not yet exercised:** the re-review path, the round cap, thread resolution, and the `Needs Information` status. The first run produced no `plausible` verdicts, so the question path is untested end to end.
