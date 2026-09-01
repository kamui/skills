# Evaluating three agentic code reviewers against a live pull request

**2026-09-01.** An evaluation of three candidates for one job — a one-shot, non-interactive code reviewer whose published output is read by both humans and agents, intended to become the core of an automated review agent:

- **Matt Pocock's `code-review`** (`mattpocock/skills`, MIT, 87 lines) — the incumbent reviewer that `code-review-publish` currently lands on by description matching.
- **`code-review-publish-2`** ("v2", [kamui/skills#14](https://github.com/kamui/skills/pull/14)) — two axis finders in parallel plus a mandatory fresh-context verifier.
- **`code-review-publish-3`** ("v3", [kamui/skills#13](https://github.com/kamui/skills/pull/13)) — a single tool-using reviewer with self-falsification and fail-closed coverage.

Both prototypes were executed end to end against the same pull request, `kamui/shortlist#65`, and both published real reviews there. This document incorporates that live data.

**Disclosure.** I wrote v2 in the session that produced this document, then ran and published both prototypes' reviews myself. The analysis was done adversarially against v2 — two of its unfixed defects are recorded below — and v3 and Pocock were steelmanned. Weight the base-choice recommendation accordingly.

## Headline

**v3 did strictly more work for 61% of v2's tokens** (110,971 vs 182,196 sub-agent tokens), and its falsification and re-review discipline held up on a live run it was never designed-tested for. But **the two runs are not comparable on finding quality** — v3 reviewed the revision that had already been repaired in response to v2's review, so its zero findings measure nothing about recall. The decisive recall experiment has an answer key sitting in the PR history and has not been run.

On design: v3 has the stronger operational spine for automation; v2 has the stronger verification mechanism and dual-audience finding contract. Pocock is not competitive as the reviewer core for these goals. Neither prototype is complete; the synthesis is specified at the end.

## Method, and the caveat that governs everything

Both prototypes were run faithfully: reference documents treated as authoritative, phase structure followed, sub-agents spawned exactly as each skill specifies, publication done per each skill's output contract. In both runs the orchestrator did target resolution and publication; the reviewing phases ran in sub-agents so token cost could be measured.

**The runs reviewed different heads of the same PR:**

| | v2 run | v3 run |
| --- | --- | --- |
| Head reviewed | `1c25a91` | `55e1f25` |
| Diff from merge-base `a4726aa` | 8 files, +194/−6 | 9 files, +245/−18 |
| Prior review state | none | v2's 3 findings, all replied `implemented`, threads resolved |
| Published result | 3 findings, Changes Requested (advisory) | 0 findings, Approved (advisory), coverage complete |

Between the runs, the PR author addressed v2's review and pushed a fix commit. v3 reviewed the *repaired* code and found nothing partly because there was materially less to find. Any comparison of finding counts between these runs is meaningless, and this document does not make one. What the v3 run does support are claims about **cost, coverage behavior, re-review rigor, and falsification discipline** — all measurable independent of how buggy the target was.

## The two live runs

### v2 at `1c25a91` — 3 findings, Changes Requested

Two axis finders ran in parallel. The Code finder returned 2 candidates; the Requirements finder restated issue #44's nine acceptance criteria, judged 7 met, and returned 2 candidates for the other two. Both finders independently hit the closed-`Kind`-enum problem from different angles — the Code finder as a P3 doc/validator contradiction, the Requirements finder as a P1 unmet acceptance criterion.

The fresh-context verifier, given claims only:

- **merged the duplicate**, keeping the Requirements framing per its dedup rule;
- **confirmed 3, refuted 0**;
- **corrected an overstated trigger** — the Code finder claimed runtime provenance corruption; the verifier grepped, found nothing under `skills/` reads `CONTEXT.md`, and rewrote the impact as maintenance vocabulary drift;
- **demoted that finding P2→P3** on the corrected impact;
- caught a wrong line reference in another claim.

Published as one batched review: two `must-fix` P1 line comments (structural validation skipped until completion; `Kind` enum closed against criterion 2) and one `consider` P3. Two findings had fix sites outside the diff and were anchored by what became the anchor ladder.

**Loop closure:** the author subsequently implemented all three findings — including the debatable one — replied `implemented` on each thread with verification evidence, and resolved the threads. Precision on this run: 3/3 published findings accepted and acted on.

### v3 at `55e1f25` — 0 findings, Approved, coverage complete

A single tool-using reviewer (v3's frequent path — no fan-out, no delegated verifier, since the change was not unusually large, coupled, or high-risk) executed phases 2–4:

- built a **9-file coverage manifest**, every file `reviewed` with named evidence;
- built the **requirement ledger** and verified all nine acceptance criteria met, running both suites to completion (288 Python tests, 60 node);
- executed the rubric's applicable **risk checks** (migration/compatibility, external contracts, stale state, path handling) with per-check evidence, and marked authorization/secrets checks not-applicable with a basis;
- raised **9 candidates and killed all 9 in falsification**;
- classified all three prior findings **`fixed`** — by verification, not by trusting the replies.

Publication followed v3's output contract: stale-head re-fetch immediately before writing (head unchanged — publication authorized), one review with the `Intent:`/`Issue fit:`/`Coverage:`/`Reviewed:` body and a machine-readable run trailer (`rubric=codex-81de4f2 … coverage=complete`), and `fixed` verdict replies on the three prior threads.

Three observations from this run matter more than the clean result:

**It verified replies instead of trusting them.** For the structural-validation finding it copied the base-branch validator and ran base and head against the *same* malformed mid-Research bundle: base printed `structurally valid Shortlist bundle; pool is incomplete`, head rejected it. It also probed the reply's scoping claims — that the blank-template guarantee survives, and that no realistic dangling `S###` reference escapes plain validation — with constructed bundles rather than accepting the prose. That is the correct standard for "a reply states intent, not outcome."

**Its base-branch-guidance rule earned its place on precision, not just security.** The strongest killed candidate — that the now-unconditional syntax check would reject legitimately in-progress obligations — was built to P2/blocking before being killed by `record-schemas.md:3`, a *base-branch* rule already requiring a placeholder in any empty required field: the previously-passing bundle was already non-conforming. The reviewer noted it found the killing rule only because the rubric directs reading base-branch guidance for changed paths. I had classified that rule purely as injection defense; it did finding-quality work.

**The kills were decisive, not timid.** Of nine: two killed by probe-discovered evidence, one by a repo-wide grep, six by gate 7 ("worth the author's time") on taste-level observations — fixture heading conventions, a debatable `Other`-kind classification, cosmetic error ordering. None was a drop-on-uncertainty.

**Operator deviation, disclosed:** I included a note about a killed candidate in the published summary body. v3's contract says "do not publish a non-actionable observation"; that note arguably violates it. The deviation was mine, not the skill's.

## Measured cost

| | v2 | v3 |
| --- | --- | --- |
| Sub-agent tokens | **182,196** (finders 69,333 + 64,505; verifier 48,358) | **110,971** |
| Tool calls | 96 | 61 |
| Sub-agent wall clock | ~602 s (finders parallel, then verifier) | ~718 s (serial) |
| Agents spawned | 3 | 1 |
| Scope delivered | findings + requirement counts | findings + coverage manifest + requirement ledger + risk checks + 3 prior-finding verifications |

Add roughly 40–60k orchestrator tokens to each for a whole-run figure.

**v3 used 61% of v2's tokens while delivering strictly more scope on a slightly larger diff.** My pre-run estimate ("v3 plausibly 40–50% cheaper") was directionally right and conservative. The trade I had not identified: **v3 is cheaper but slower** — v2's finders parallelize, v3's single reviewer is serial. For an unattended agent, cost almost certainly dominates latency, which favors v3 further.

Pocock's stack was not re-measured. Its two 400-word-capped sub-agents constrain output, not input — input cost per finder is comparable to v2's — and its wrapper adds a lossy normalization pass to turn prose findings into publishable comments.

## Architecture

| | Pocock | v2 | v3 |
| --- | --- | --- | --- |
| Size | 87 lines | 767 lines, 5 refs | 437 lines, 2 refs |
| Phases | 5 | 4 | 6 |
| Agents/run | 2 finders | 1–3 (finders + verifier, both skippable) | 1 (+1 conditional verifier) |
| Verification | none | mandatory, **separate context** | self-falsification, same context |
| Publishes | no — needs the `code-review-publish` wrapper | yes | yes |
| Coverage accounting | none | none | per-file manifest, fail-closed, `Incomplete` status |
| Injection boundary | none | none | untrusted-input rule + base-branch guidance |
| Stale-head protection | n/a | none within a run | re-fetch before first write |
| Re-review | stateless (wrapper's protocol handles it) | prior findings ride through the verifier as claims | full-by-default; incremental only with proven ancestry and complete prior coverage |

The load-bearing divergence is the verification boundary. v2 buys independence with a fresh agent that never saw the finder's reasoning — mechanism-backed, since a context that already asserted something agrees with itself. v3 buys economy by having one mind generate and falsify its own candidates — evidence-backed, since prior research found **no controlled measurement** that a separate verify pass reduces false positives, only converged industry practice. The v3 run is one data point for v3's side: self-falsification killed nine candidates decisively, including one it had built to blocking severity. One run on one PR is not proof; the same mind can still fail to doubt a claim it is invested in, and this run contained no such claim.

## Corrections to the pre-run analysis

Recorded explicitly, since the pre-run comparison circulated before the live data existed.

**Wrong: "v3's falsification is drop-on-uncertainty with a recall cost."** I read *"drop the candidate when decisive evidence is missing"* as licensing silent deletion of exactly the hardest bug class. On this run every kill was evidence-driven, none uncertainty-driven. The concern is not refuted — the PR contained no hard-to-prove concurrency or race-class candidate, which is where the failure mode would appear — but I asserted it more confidently than the evidence supported, and the one live run points the other way.

**Overstated: v3's context-pressure risk.** Nine files at 61 tool calls showed no strain. The concern applies at a scale neither prototype has been tested at.

**Overstated: v2's stale-head gap.** Real as a within-run race, but this test did not trigger it — the head moved *between* runs, which both skills handle by re-resolving at phase 1. v3's re-fetch-before-write remains the stronger design; no live harm was demonstrated.

**Understated: v3's base-branch-guidance rule.** Filed pre-run under operational hardening; the run showed it killing the strongest false candidate. It is a precision mechanism as much as a security one.

**Confirmed: v3's coverage discipline is real, not aspirational.** The manifest carried per-file evidence including which surrounding code was read, and the risk checks were probed, not asserted.

## Defect register

**v3, open — rubric gate 2 is unscoped over requirement findings.** The eight admission gates are conjunctive over all findings, and gate 2 reads *"Introduced here: the reviewed change caused it. Do not report a pre-existing problem."* A requirements gap is measured against the issue, not the diff — the issue made it this change's job whether or not the code predates it. The best finding of the v2 run was exactly this shape: an acceptance criterion unmet at a validator gate the diff never touched. A literal gate-2 reading kills it; v3's Issue-fit section arguably rescues it; the ambiguity is the bug. This is the same unscoped-exclusion defect v2 had and fixed in `verify.md`. Fix: scope gate 2 to non-requirement kinds explicitly.

**v3, open — priority/blocking independence is underspecified.** Separating impact (`P0`–`P3`) from merge judgment (`Required change` vs `Suggestion`) is more expressive than v2's derivation rule, but nothing states which priorities default to blocking. That invites run-to-run variance — precisely what an automated pipeline should not have.

**v2, open — no injection boundary.** Nothing treats PR text, issue text, diffs, or comments as untrusted, and nothing evaluates standards against the base-branch version of guidance files, so a PR could in principle redefine the rules used to judge it. For an unattended agent on arbitrary PRs this is v2's most important gap, and v3's handling is the single strongest passage in any of the three skills.

**v2, open — no coverage accounting.** A finder that silently skips a file yields a clean review; there is no manifest and no `Incomplete` status, so zero-findings-from-unfinished-work can become approval.

**Pocock — structural, for these goals.** One clause of noise control; a taste-based Fowler-smell checklist that manufactures candidates ("possible Feature Envy" exists in almost any diff); findings as free prose a wrapper must lossily normalize into ids and severities; interactive branches, including a hard stop telling the user to run `/setup-matt-pocock-skills` when `docs/agents/issue-tracker.md` is absent — fatal in an unattended loop outside this ecosystem. Its durable contributions already live inside both prototypes: the two-axis separation, the merge-base fixed point, spec-line-quoted requirement findings, and the scope-creep bucket.

## What the runs did not test

- **v3's finding-path output contract.** Zero findings meant zero inline comments — no `Required change:`/`Suggestion:` rendering, no anchoring decision, no suggestion block. The run says nothing about v3's dual-audience quality on the path that matters most.
- **v2's question path.** Neither v2 run produced a `plausible` verdict, so `plausible`→question has never fired end to end.
- **False-positive rate on a known-clean PR** — the number an automated loop most depends on — for either prototype.
- **Large diffs**, where v2's partitioned contexts and v3's single context should diverge.

## Verdict

**v3 has the better skeleton for the automated future, and now has live evidence for its economy, coverage, and falsification discipline. v2 has the better verification mechanism, the richer agent-action contract, and the only demonstrated finding-precision record (3/3 accepted and implemented).** The live run moved the balance toward v3 more than predicted — chiefly on cost-per-scope and the demonstrated precision value of base-branch guidance.

For the automated review agent, the synthesis: **take v3's operational spine** — injection boundary, base-branch guidance evaluation, fail-closed coverage with `Incomplete`, stale-head re-fetch, single-reviewer frequent path, pinned-rubric run trailer — **and port four things from v2**:

1. The **fresh-context verifier, mandatory for blocking findings only**, conditional elsewhere. This splits the two cost models: the expensive independent check is spent exactly where a false positive becomes a work request for an agent.
2. The **anti-over-refutation asymmetry** — `plausible` by default, `refuted` only with a quoted line, plus the explicit realistic-state list (races, cold-cache nils, falsy zeros, lost regex anchors) that must not be dismissed as speculative. v3 has no equivalent, and this is where its falsification is most likely to fail on a harder PR.
3. **`plausible` → question rather than drop**, so an unproven-but-real mechanism asks instead of vanishing.
4. The **explicit permission line** on non-blocking findings ("Closing this without action is a correct response") and the **required trigger field** — v2's concrete guards against agent over-compliance, and the only mechanism that gives an addressing agent a test for whether its own fix worked.

Plus v3's gate-2 scoping fix, and a stated priority→blocking default to kill the variance.

## The decisive experiments, not yet run

1. **Run v3 against head `1c25a91`** — the original revision, where three real findings are known to exist and were all accepted and implemented by the author. This is the apples-to-apples recall test with a verified answer key, and the single most informative measurement still available. If v3 finds all three, its cheaper architecture wins outright and the ported verifier becomes optional; if it misses the requirements-shaped one, gate 2 is the likely culprit and the port list above is vindicated.
2. **Run both against a known-clean PR** to measure false-positive rate directly.
3. **Run both against a large diff** to locate v3's context ceiling and v2's cost ceiling.
