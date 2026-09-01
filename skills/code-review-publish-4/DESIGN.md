# Design goals and priorities

This document records the reasoning behind the prototype. It is not part of the runtime instructions: `SKILL.md`, `references/review-rubric.md`, `references/output-contract.md`, and the conditionally loaded `references/verifier.md` remain authoritative.

## Problem being solved

`code-review-publish-4` is intended for frequent, non-interactive review of an existing pull request. One invocation must gather the pull request and issue context, review the entire change, and publish useful feedback without asking the caller to steer the analysis.

The quality of the human review and any later agent response both depend on the same foundation. The reviewer therefore needs to produce feedback that is:

- accurate enough that authors will trust and act on it;
- aware of the originating issue rather than judging only local code quality;
- complete about what it inspected, without manufacturing comments to appear thorough;
- understandable from visible prose by a human or an agent;
- safe to publish once, against the exact revision reviewed;
- economical enough to run routinely.

The existing `review-protocol.md` informed useful ideas such as stable finding identity, explicit dispositions, thread continuity, and visible semantic status. It was deliberately not treated as a compatibility specification or output schema for this prototype.

## Hybrid architecture at a glance

The prototype has one complete reviewer and, only when warranted, one narrower verifier:

1. The primary reviewer resolves the pull request and issues, builds one requirement ledger, inspects the full merge-base diff, finds candidates across both code behavior and issue fit, and tries to disprove each candidate.
2. Straightforward optional findings can proceed after that primary falsification. A clean review stops there.
3. Every proposed merge blocker and every surviving security, authorization, data-loss, destructive-migration, or public-contract candidate goes to one batched verifier with fresh context. Difficult cross-module optional findings may go too.
4. The verifier receives claims and raw citations, but not the primary reviewer's reasoning. It fact-checks only the supplied candidates and returns `confirmed`, `plausible`, or `refuted`; it neither searches for new findings nor publishes.
5. The primary reviewer drops refuted claims, turns only outcome-changing plausible claims into questions, renders confirmed findings, and performs the publication safety checks.

This is hybrid because the common path retains one integrated review rather than paying for multiple independent searches, while consequential assertions receive a second look that is less likely to inherit the first reviewer's assumptions.

## Priority order

### 1. High-signal findings

The first priority is minimizing weak or speculative feedback while retaining concrete defects the author would want to fix. The adapted Codex rubric is the finding-admission rule: a candidate needs meaningful impact, a proven trigger and consequence, evidence that this change introduced it, and an actionable remedy.

Every candidate is actively falsified before publication. Generic preferences, tool-enforced trivia, praise, scores, effort estimates, and checklist filler are excluded. A clean review is preferable to comments created merely to fill a template.

### 2. Fidelity to the originating issue

The linked issue supplies product intent, acceptance criteria, invariants, and non-goals. The reviewer converts those into a private requirement ledger and checks the implementation against it. This preserves the strongest part of Matt Pocock's review approach and PR-Agent's ticket context without exposing a repetitive compliance table.

Issue context does not reduce the evidence threshold. Missing or contradicted requirements become findings only when the code demonstrates the gap. Unknowns that could change the verdict become focused questions instead of accusations.

### 3. Complete inspection with fail-closed coverage

High signal must not be achieved by silently skipping difficult files. Every changed file—including deletions, renames, binaries, generated files, and omitted patches—is accounted for as reviewed, deliberately ignored with a reason, or unreviewed.

Coverage and comment volume are separate: inspect the complete merge-base diff, but publish only candidates that pass the rubric. Failed fetches, tool failures, or unfinished risk checks make the review incomplete; zero findings from incomplete work can never produce approval.

### 4. Equal usability for humans and agents

Visible prose is the authoritative interface. Each finding has explicit `Triggers when`, `Impact`, and `Change` fields, so either a person or an addressing agent can act without decoding metadata or opening another protocol document. Optional feedback explicitly says that closing without action is valid.

Stable hidden trailers support deduplication, thread correlation, and re-review automation. They never contain meaning omitted from the prose, and human comments without trailers remain first-class input. Priority communicates impact; the independent `must-fix` or `consider` action communicates whether the author must change code before merge. The review also distinguishes the changed-line anchor used by the forge from a different location that actually needs editing.

### 5. Safe, deterministic publication

The reviewer pins the base, merge-base, and head before analysis, then re-fetches the head immediately before writing. A stale or unreadable head aborts publication. New findings are submitted in one native review batch, using exact diff sides and the smallest useful anchors.

The semantic status is always written in the review body. The forge event is a permission decision, not the verdict: `COMMENT` is the default, and `APPROVE` or `REQUEST_CHANGES` is used only when the reviewer is separately authorized to gate the merge.

### 6. Routine-run efficiency

The frequent path uses one tool-using reviewer to gather candidates and falsify them. It does not copy the default multi-agent fan-out used by several review systems. A clean review or one containing only straightforward optional feedback pays for no second model pass.

At most one independent verifier handles all candidates that cross deterministic thresholds. Fresh context is important: the verifier gets a falsifiable artifact claim and raw evidence, not the primary reviewer's support narrative or conclusion. Batching retains the value of independent confirmation without starting one agent per finding.

Context expansion is surgical: diff, enclosing symbol, then only the callers, interfaces, configuration, tests, or history needed to resolve a candidate. The verifier instructions are a conditional reference, so normal runs do not spend context tokens loading them. A deterministic helper computes the input fingerprint without spending prompt tokens on serialization rules. This design record is never loaded during review.

### 7. Re-review continuity

A new run reads earlier reviews, replies, and thread state before generating feedback. Stable concept-based IDs survive line movement. Prior unresolved findings are verified against current code and carried forward rather than silently disappearing or being duplicated.

Full re-review is the default. Incremental review is allowed only with proven ancestry, base and merge-base continuity, complete prior coverage, and a bounded delta. A declined finding gets one verified re-review before becoming a human-visible dispute instead of entering an endless agent loop.

### 8. Clear provenance and portability

The core rubric is an attributed adaptation of the Apache-2.0 OpenAI Codex rubric, with its pinned source, modification notice, copyright, and license included in the package. Other systems influenced workflow choices, but their prompt text was not copied.

The skill uses portable Markdown instructions and forge-neutral concepts where practical. GitHub's batched review shape is included as the concrete implementation example because this repository uses GitHub.

## What was grafted from other approaches

| Source | Adapted contribution |
| --- | --- |
| OpenAI Codex | Finding-admission gates, priority calibration, concise actionable comments |
| Matt Pocock's code-review skill | Merge-base fixed point, originating issue/spec, repository-specific standards |
| PR-Agent | Ticket context, private requirement assessment, surgical context expansion |
| `misospace/pr-reviewer-action` | Fail-closed coverage, stale-head protection, carried findings, evaluation mindset |
| Docker and Anthropic review workflows | Candidate generation followed by deliberate falsification |
| Gemini, OpenHands, and GitHub Agentic Workflows | Untrusted-input boundaries, complete manifests, exact anchors, deduplication, one batched review |
| Existing local review protocol | Stable identities, dispositions, thread continuity, advisory status, prose-first interoperability |
| Prototype comparison findings | Claim/support isolation, conditional fresh verification, explicit action, and distinct anchor/fix locations |

## Deliberate non-goals

- Being a drop-in implementation of `review-protocol.md`.
- Modifying code, addressing comments, editing issue state, or merging the pull request.
- Running multiple standards/spec/reviewer agents on every pull request.
- Acting as a comprehensive security audit or a substitute for repository tests and CI.
- Publishing numeric confidence, code-quality scores, effort estimates, or generic praise.
- Treating an issue omission, risk keyword, style preference, or missing test as a finding without a demonstrated consequence.
- Using a gating review event merely because the semantic verdict is `Approved` or `Changes Requested`.

## How to evaluate the prototype

The useful comparison is behavioral rather than aesthetic. Test the prototype repeatedly on known-clean and known-defective pull requests and measure:

- recall of blocking and high-impact defects;
- false findings on clean changes;
- missed explicit issue requirements;
- duplicate findings and resurrected resolved findings;
- invalid or misleading line anchors;
- false approvals when coverage is incomplete;
- whether humans and addressing agents implement the intended remedy correctly;
- input/output tokens, tool calls, latency, and variance between runs.

The most important open design questions are whether the verifier thresholds produce the right recall/cost tradeoff in real pull requests, whether a broader deterministic intake helper is worth maintaining, and how much hidden structure improves re-review without making the visible review feel machine-oriented.
