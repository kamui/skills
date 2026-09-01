# Evaluating three agentic code reviewers against a live pull request

**2026-09-01.** Compares `code-review-publish-2` (PR #14), `code-review-publish-3` (PR #13), and Matt Pocock's `code-review`, for one goal: a one-shot, non-interactive reviewer whose output is read by both humans and agents, destined for an automated review agent.

**Disclosure.** I wrote v2 in the session that produced this document. Findings below were hunted adversarially against v2 and the other two were steelmanned. Two defects in v2 and two in v3 are recorded; readers should still weight the base-choice recommendation accordingly.

## Headline

Both prototypes were run against the same pull request, `kamui/shortlist#65`, and both published real reviews. **v3 did more work for 61% of the tokens.** But the two runs are not comparable on finding quality, because they reviewed different revisions — v3 reviewed the revision that had already been fixed in response to v2's review. v3's zero findings are therefore not evidence about its recall, and the decisive experiment has not been run.

On design: v3 has the stronger operational spine and, on live evidence, filtering discipline that works. v2 has the stronger verification mechanism and dual-audience contract. Neither is complete.

## Method, and the caveat that governs everything

Both prototypes were executed faithfully — reference documents read as authoritative, phase structure followed, sub-agents spawned as each skill specifies. In both cases the orchestrator did phase 1 (target resolution) and publication; the reviewing and verification phases ran in sub-agents so token cost could be measured.

**The runs reviewed different heads.**

| | v2 run | v3 run |
| --- | --- | --- |
| Head reviewed | `1c25a91` | `55e1f25` |
| Diff from merge-base | 8 files, +194/−6 | 9 files, +245/−18 |
| Prior review state | none | 3 findings, all replied `implemented` |
| Result | 3 findings, Changes Requested | 0 findings, Approved |

Between the two runs, the PR author addressed v2's review and pushed a fix commit. v3 reviewed the *repaired* code. It found nothing because there was materially less to find — not because it looked less hard. Any comparison of finding counts between these two runs is meaningless, and this document does not make one.

What the v3 run *does* support are claims about cost, coverage behavior, re-review rigor, and falsification discipline, all of which are measurable independent of how buggy the target was.

## What actually happened

### v2 at `1c25a91` — 3 findings, Changes Requested

Two axis finders in parallel produced 4 candidates. Both independently found the closed-`Kind`-enum problem from different angles — the Code finder as a doc/validator contradiction at P3, the Requirements finder as an unmet acceptance criterion at P1. The fresh-context verifier merged them keeping the Requirements framing, confirmed 3, refuted 0, **corrected an overstated trigger** (the Code finder claimed runtime provenance corruption; the verifier grepped and found nothing under `skills/` reads `CONTEXT.md`, so the impact was maintenance drift), **demoted that finding P2→P3** on the corrected impact, and caught a wrong line reference in another claim.

All three findings were subsequently accepted and fixed by the author. Precision on this run: 3/3.

### v3 at `55e1f25` — 0 findings, Approved, coverage complete

A single tool-using reviewer built a 9-file coverage manifest, a 9-criterion requirement ledger, ran both test suites to completion (288 Python, 60 node), executed the rubric's applicable risk checks, raised **9 candidates and killed all 9 in falsification**, and verified the three prior findings against current code.

Three things in that run are worth extracting.

**It verified replies instead of trusting them.** For the structural-validation finding it copied the base-branch validator, ran base and head against the *same* malformed mid-Research bundle, and observed base printing `structurally valid Shortlist bundle; pool is incomplete` where head rejected it. That is a differential probe, not a reading of the diff, and it is the correct standard for "a reply states intent, not outcome."

**Its base-branch-guidance rule earned its place.** The strongest killed candidate — that the now-unconditional syntax check would reject legitimately in-progress obligations — was built to P2/blocking before being killed by `record-schemas.md:3`, a base-branch rule already requiring a placeholder in any empty required field. The bundle that previously passed was already non-conforming. The reviewer noted it found the killing rule *only* because the rubric directs reading base-branch guidance for changed paths rather than only the diff. That is a concrete finding-quality benefit from a rule I had previously classified as merely an injection defense.

**The kills were decisive, not timid.** Reviewing all 9: two were killed by evidence discovered through probing, one by a repo-wide grep, and six by gate 7 ("worth the author's time") on taste-level observations — fixture heading conventions, a debatable `Other` classification, cosmetic error ordering. None was a drop-on-uncertainty.

## Measured cost

| | v2 | v3 |
| --- | --- | --- |
| Sub-agent tokens | **182,196** (69,333 + 64,505 + 48,358) | **110,971** |
| Tool calls | 96 | 61 |
| Sub-agent wall clock | ~602 s (finders parallel, then verifier) | ~718 s (serial) |
| Agents spawned | 3 | 1 |
| Scope delivered | findings only | findings + 9-file coverage manifest + 9-criterion ledger + risk checks + 3 prior-finding verifications |

v3 used **61% of v2's tokens while delivering strictly more scope**, on a slightly larger diff. My pre-run estimate was "v3 plausibly 40–50% cheaper"; the direction was right and the estimate was, if anything, conservative given the extra scope.

The trade I had not identified: **v3 is cheaper but slower.** v2's finders run in parallel, so its wall clock is roughly max(finders) + verifier. v3's single reviewer is serial. For an automated agent running unattended, cost almost certainly dominates latency — this favors v3 more than the token numbers alone suggest.

Add roughly 40–60k of orchestrator context to each for a total-run figure. Pocock's stack was not re-measured; its 400-word output caps constrain nothing on the input side, and its wrapper adds a normalization pass.

## Architecture

| | Pocock | v2 | v3 |
| --- | --- | --- | --- |
| Size | 87 lines | 767 lines, 5 refs | 437 lines, 2 refs |
| Phases | 5 | 4 | 6 |
| Agents/run | 2 | 1–3 | 1 (+1 conditional) |
| Verification | none | mandatory, **separate context** | self-falsification, same context |
| Publishes | no (needs wrapper) | yes | yes |
| Coverage accounting | none | none | per-file manifest, fail-closed |
| Injection boundary | none | none | yes |

The architectural divergence is the verification boundary. v2 buys it with a fresh agent that never saw the finder's reasoning. v3 buys economy by having one mind generate and falsify its own candidates. v2's choice is mechanism-backed — a context that already asserted something agrees with itself. v3's is evidence-backed: my own prior research found **no controlled measurement** that a separate verify pass reduces false-positive rate, only converged industry practice.

The v3 run is one data point for v3's side: self-falsification killed 9 candidates decisively, including one built to blocking severity. It is not proof — the same mind can still fail to doubt itself on a claim it is invested in, and this run had no such claim.

## Corrections to my pre-run analysis

**Wrong: "v3's falsification is drop-on-uncertainty with a recall cost."** I read *"drop the candidate when decisive evidence is missing"* as licensing uncertainty-drops on exactly the hardest bug class. On this run it did not behave that way — every kill was evidence-driven. The concern is not refuted, because this PR contained no hard-to-prove concurrency or race-class candidate, which is where the failure mode would appear. But I stated it more confidently than the evidence then supported, and the one live run points the other way.

**Overstated: "v3 hits context pressure on large diffs sooner."** Directionally sound, but 9 files at 61 tool calls showed no strain. The concern applies at a scale neither prototype has been tested at.

**Understated: v3's base-branch-guidance rule.** I filed it under operational hardening. The run showed it doing finding-quality work — it was the mechanism that killed the strongest false candidate.

**Overstated: v2's stale-head gap.** I called it a defect that "an author pushing mid-review gets misanchored comments." True as a within-run race, but this test did not trigger it: the head moved *between* runs, and both skills re-resolve the head at phase 1. v3's re-fetch-before-write is still the stronger design — it closes a window v2 leaves open — but no live evidence of harm was produced.

**Confirmed: v3's coverage discipline is real, not aspirational.** The manifest was populated with specific evidence per file, including which surrounding code was read. It is the feature most directly aimed at the false-approval risk in an automated loop, and it worked.

## Defects

**v3, unfixed — gate 2 is unscoped over requirement findings.** The rubric's admission gates are conjunctive over all findings, and gate 2 says *"Introduced here: the reviewed change caused it. Do not report a pre-existing problem."* A requirements gap is measured against the issue, not the diff: the issue made it this change's job whether or not the code predates it. The best finding of the v2 run was exactly this shape — an acceptance criterion unmet at a validator gate the diff never touched. A literal reading of gate 2 kills it; v3's Issue-fit section arguably rescues it, and that ambiguity is the bug. This is the same unscoped-exclusion defect v2 had and fixed. **Recommended fix: scope gate 2 to non-requirement kinds explicitly.**

**v3, minor — priority/blocking independence is underspecified.** Separating impact from merge judgment is more expressive than v2's derivation rule, but nothing states which priorities default to blocking. That invites run-to-run variance, which is precisely what an automated pipeline should not have.

**v2, unfixed — no injection boundary.** v2 says nothing about treating PR text, issue text, and diffs as untrusted, and nothing about judging standards against the base-branch version of guidance files. For an unattended agent processing arbitrary PRs this is the most important gap in the document, and v3's handling of it is the single strongest line in any of the three skills.

**v2, unfixed — no coverage accounting.** A v2 finder that silently skips a file produces a clean review. There is no `Incomplete` status and no manifest, so zero-findings-from-unfinished-work can become approval.

**Pocock — unchanged assessment.** Not competitive as the reviewer core for these goals: one clause of noise control, a taste-based smell checklist that manufactures candidates, free-prose findings the wrapper must lossily normalize, and a hard stop instructing the user to run `/setup-matt-pocock-skills` when `issue-tracker.md` is absent — fatal in an unattended loop outside this ecosystem. Its durable contributions (two-axis separation, merge-base fixed point, spec-line-quoted findings, scope creep) already live inside both prototypes.

## What the run did not test

**v3's finding-path output contract was never exercised.** Zero findings means zero inline comments: no `Required change:` / `Suggestion:` label, no priority rendering, no anchoring decision, no suggestion block. Everything published was summary body. The run says nothing about v3's dual-audience quality on the path that matters.

**v2's question path remains untested** across both of its runs — neither produced a `plausible` verdict.

**Neither prototype has been tested on a clean PR with no defects,** where false-positive rate is directly measurable, nor on a large diff.

## Verdict

**v3 has the better skeleton and now has live evidence for its economy and discipline. v2 has the better verification mechanism and the better dual-audience finding contract.** The v3 run moved the balance toward v3 more than I expected, chiefly on cost-per-scope and on the demonstrated value of base-branch guidance.

For an automated review agent, the synthesis remains: **take v3's operational spine** — injection boundary, base-branch guidance evaluation, fail-closed coverage, stale-head protection, one-reviewer frequent path — **and port from v2**:

1. The **fresh-context verifier, made mandatory for blocking findings only** and conditional elsewhere. This splits the difference between the two cost models: the expensive check is spent only where a false positive becomes a work request.
2. The **anti-over-refutation asymmetry** — `plausible` by default, `refuted` only with a quoted line, and the explicit realistic-state list (races, cold-cache nils, lost regex anchors) that must not be refuted as speculative. v3 has no equivalent, and this is where its falsification is most likely to fail on a harder PR.
3. **`plausible` → question rather than drop**, so an unproven-but-real mechanism asks instead of vanishing.
4. The **explicit permission line** on non-blocking findings and the **required trigger field**, which are v2's concrete guards against agent over-compliance and its only mechanism giving an addressing agent a test for its own fix.

Plus v3's own gate-2 scoping fix.

## The decisive experiment, not yet run

**Run v3 against head `1c25a91`** — the original revision, where three real findings are known to exist and were subsequently accepted and fixed by the author. That is the apples-to-apples recall test, with a verified answer key, and it is the single most informative measurement still available. If v3 finds all three, its cheaper architecture wins outright and the verifier port becomes optional. If it finds one or two, the fresh-context verifier is earning its cost and the synthesis above is right.

Secondary: run both against a known-clean PR to measure false-positive rate directly, which is the number neither prototype has produced and the one an automated loop most depends on.
