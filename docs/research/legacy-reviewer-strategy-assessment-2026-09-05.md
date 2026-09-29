# legacy reviewer strategy assessment — 2026-09-05

The recommendation is to keep the current skill as the production baseline, improve discovery and verification handling, and test one small alternative that gives a fresh reviewer permission to discover missed defects on a bounded surface. Do not replace it with an always-on panel or implement the replica design in #88 as written. The current evidence supports neither a wholesale replacement nor confidence that further rubric additions alone will solve recall.

This assessment covers `snapshot-path-omitted` at `3ff624a0a8b57e7096d8ad8263ac64a3fb3ccd83`, verified against GitHub `main`, and all 13 open GitHub issues retrieved with their comments on 2026-09-05. Tickets focused solely on the v2a prototype are excluded; shared epics and the current-line replica proposal are included only for their relevant portions. Historical Panel results are used as comparison evidence, not as a recommendation to resume its backlog. No skill implementation or GitHub issue was changed. This document and its [empirical companion](legacy-reviewer-empirical-assessment-2026-09-05.md) are research artifacts.

## 1. What the evidence supports

The current architecture has valuable properties: a single integrated primary, explicit requirements, candidate falsification, independent confirmation for consequential findings, concise trigger/impact/change prose, and deterministic publication helpers. Its problem is not a lack of review ceremony. Its problem is that useful defects can disappear at several stages, and the safeguards largely operate on whatever the primary already thought of.

| Target | Current-line evidence | Practical implication |
| --- | --- | --- |
| Hyper concurrency regression | One of three v5b seeds recovered a rule-level fix; another found a closing-path projection; the third approved. Candidate verification also produced false safety conclusions. | Verification can improve a trace while still missing the actual regression or narrowing its remedy incorrectly. |
| Raft clean failover change | Three baseline seeds stayed clean. The lower-effort arm's erroneous premise was reopened and ultimately dropped for other valid reasons. | Verification can correct faulty reasoning without creating a false published finding. |
| Typeshed upstream conformance | Primary GT missing re-export found in one of three v5b seeds. The comparison Panel found all three designated omissions in each of three seeds. | Explicit enumeration of the expected upstream surface is a promising discovery mechanism; diff coverage alone is insufficient. |
| UV deferred naming | Current line found the deferral but published no question in three seeds; Panel did in all three. | This is a question-policy difference, not evidence of three missed runtime bugs. |
| Polars parser rewrite | True behavioral defects published, but severity inflated and the benchmark question omitted in all three seeds. | Bug discovery, priority calibration, and empirical-claim coverage need separate scores. |
| Cobra changed tests | First review recommended test naming while missing a test that could not pass; later state handling and stale-head abort worked. | Inspection of test conventions does not establish test correctness. Only one first-review seed exists here. |

Sources: [holdout evaluation](prototype-runs-holdout/evaluation.md), [ground truth and method](prototype-runs-holdout/README.md), [per-target measurements](prototype-runs-holdout/comparison-data.md). These are small, selected cases, not a population estimate. Zero adjudicated false findings is encouraging; it does not establish production precision, especially alongside severity errors and false clean conclusions.

The most useful causal distinction is:

1. **Never generated:** a required export in an unchanged file never becomes a candidate.
2. **Incorrectly dismissed:** a candidate is dropped on a false premise.
3. **Incorrectly narrowed:** a real concurrency finding describes or repairs only one projection.
4. **Correctly understood but not published:** an open decision or empirical claim fails the channel policy.
5. **Published but miscalibrated:** a true low-impact fact is escalated to urgent or blocking feedback.

Adding verifier rules can address 2 and 3. It cannot reliably address 1 when the verifier is explicitly forbidden to discover new claims. Loosening question admission addresses 4, with no necessary improvement in bug recall. These should not share one undifferentiated “quality” score.

## 2. Strategy and implementation assessment

### Preserve the useful foundation

Keep the integrated primary as the default until a matched experiment beats it. Keep independently checked high-consequence findings, full changed-file accountability, base-versus-head reasoning, stable defect identity, and atomic review publication. Preserve the distinction between an anchor and the actual repair site. The test/trace must establish a defect; the comment must make the failure and required outcome understandable without its hidden metadata.

The publication layer has substantial useful mechanical coverage. During this assessment, `validate_review.py --self-test` passed 70 cases, `test_context_fingerprint.py` passed eight groups, and `review_context.py --self-test` passed its reported cases. The holdout's live Cobra rounds also provide limited but real evidence for reply handling and stale-head protection. These checks establish their tested mechanics, not the truth of review findings.

Sources: skill (historical source path omitted), rubric (historical source path omitted), output contract (historical source path omitted).

### Shift attention toward discovering failures

The current rubric lets context expansion follow a candidate, and the verifier forbids unrelated discovery. This helps cost and precision but creates a structural blind spot: the reviewer sometimes needs to inspect an interface, caller, or expected artifact before it can name a candidate at all. Add a small discovery phase that asks what the change promises and which inputs, transitions, or consumers could falsify that promise. Permit bounded exploration for a named risk or invariant, not only for an already articulated defect.

For conformance changes, enumerate the expected upstream delta first. For a retry change, identify success-after-timeout and partial-failure behavior. For concurrency changes, identify the progress or ownership invariant and the relevant steady-state transition. For changed tests, examine setup, action, assertions, and cleanup in execution order. These are different evidence operations, not generic instructions to “be more thorough.”

The instruction to read the diff once is a useful default against duplicate ingestion. It should not prohibit a necessary reread after compaction, a contradictory trace, or incomplete function context. Avoid rigid savings rules that spend fewer input tokens by leaving an incorrect model of the code uncorrected.

### Simplify semantics before adding more branches

The current runtime documents total about 10,300 words, including conditional verifier and re-review references; the first-review mandatory skill/rubric/output-contract set alone is about 7,700 words. Size alone does not prove degraded quality, but overlapping exceptions make behavior hard to predict. Holdout failures show that the model can follow one rule correctly and still defeat its intended outcome through another rule.

Use one authoritative rule for each decision, with references from other files. Keep ordinary findings simple. Reserve the detailed concurrency procedure for the surfaces that need it. Keep publication syntax out of discovery prompts where feasible, and generate repeated metadata and summaries mechanically after judgments are settled. Do not encode every observed miss as a new mandatory paragraph in several files.

The verifier currently uses `refuted` for both a claim contradicted by evidence and a claim it cannot decide. That distinction already matters to the handling rules. Represent it explicitly in a compact verdict reason or an unresolved disposition. This need not resurrect the earlier unused `plausible` branch or introduce confidence scores. Failure to prove a claim is not proof that its surface is safe.

### Fix concrete implementation gaps

1. **Forge packet cannot supply the fingerprint inputs it requires.** The documented GraphQL query omits comment IDs, while `context_fingerprint.normalize()` requires a numeric ID for each issue comment. A direct probe with the query's available comment fields raises `issues[0].comments[0].id must be a non-negative integer`. Fetch the appropriate stable numeric field and normalize it mechanically; do not ask the model to invent identity or make another fetch after being told never to refetch. The same query omits `updatedAt` for PR/review-thread comments while later-state deduplication depends on edits.
2. **Completeness is asserted without pagination evidence.** The query has `first:10`, `first:100`, and `first:50` limits without `pageInfo`. Long review histories can therefore be silently incomplete. Fetch once into a persisted packet, with continuation requests as necessary; “one logical fetch” should not mean “one capped request regardless of completeness.” This matters to issue discovery as well as re-review.
3. **The documented large-diff fallback is unavailable.** Step 3 allows rerunning `review_context.py` split by path after output truncation, but its parser exposes no path-selection option. Add stable chunking or persisted selectable sections before relying on this escape hatch.
4. **The output validator protects formatting more thoroughly than essential prose.** Removing both `Triggers when` and `Impact` from the shipped valid-payload fixture still returns zero validation violations. Their factual sufficiency belongs to the reviewer, but their required presence and order are mechanical. Add those simple checks rather than trying to encode review judgment in regexes.

Sources and inspection locations: fetch and fallback instructions (historical source path omitted), fingerprint normalization (historical source path omitted), context CLI (historical source path omitted), finding validator (historical source path omitted). The missing-ID and missing-field cases were exercised in memory without modifying these files. Pagination and CLI mismatch were established by source inspection. The passing self-tests do not cover these integration gaps.

## 3. Cost, time, and evaluation

The strongest measured efficiency lever is primary effort. With verifiers held at high, the medium-primary arm reduced median billed cost from $3.04 to $1.93 on Raft and from $4.42 to $2.62 on Typeshed, approximately 37% and 41%. Thinking tokens fell approximately 46% and 63%, respectively. Published outcomes were comparable on those two targets, but Typeshed still missed its principal GT item in two of three seeds in both arms. Equal misses establish no recall improvement.

These are historical transcript-priced figures under the experiment's model and price settings, not current quotes or guarantees for other models and harnesses. `high` effort is not a portable unit of reasoning quality. Record actual model, effort, runtime, and observed inheritance; verify the supported adapter rather than treating `agents/openai.yaml` as the full runtime capability boundary.

Live [#124](https://github.com/kamui/skills/issues/124) and [#62](https://github.com/kamui/skills/issues/62) record a 2026-09-05 restatement of the original effort-adoption rule to count published outcomes. That is a reasonable product metric, but it is a post-result change and must remain labeled as such. The local merged evaluation still states the original result. The proposed three Hyper seeds are useful diagnostics; after other review-policy changes, compare against controls with the same updated policy, rather than confounding effort and prompt changes.

Important measurement repairs:

- **Use matched targets.** The broad $8.88/$3.62 Panel/current ratio mixes different target sets and includes Cobra re-review/probe rounds in the current arm. Matched production-shaped ratios are about 2.15× on Typeshed ($9.13/$4.25) and 2.25× on UV ($6.87/$3.05). The extra spend is substantial, but the pooled ratio is not a causal architecture comparison.
- **Measure real completion latency.** `transcript_usage.py` explicitly sums per-transcript wall durations. That can double-count overlap and parent waiting. Add root dispatch-to-final-result elapsed time; retain agent-time sums as a separate diagnostic. Do not use the summed figures as reliable end-to-end latency claims.
- **Allow production-shaped focused execution.** The holdout forbade execution except helper scripts, while the shipped skill permits focused checks. The Cobra result is evidence of a static-inspection failure, not evidence that test-assisted review fails. Future evaluation needs a safely isolated execution-enabled arm, using the same allowance for controls and challengers.
- **Preserve preregistered outcomes.** The README says fewer than three false-acquittal occurrences makes criterion 2 `not decidable`; the evaluation calls 0/2 a failure. Both observed failures matter, but the formal threshold result should follow the stated rule.
- **Use per-run recall.** Union recall across three seeds is diagnostic for diversity, not the experience of a one-shot user. Report per-run true material defects recovered, buggy PRs returned clean, false findings, fix sufficiency, priority calibration, useful questions separately, and cost/elapsed time distributions.
- **Treat used holdouts as regression fixtures.** Tickets now name the exact missed lines and desired outputs. Paper walkthroughs and reruns on these cases test regression repair, not generalization. Freeze changes and then evaluate fresh targets, with clean controls and blinded adjudication of both expected and unexpected findings.
- **Run a genuine verification ablation if testing necessity.** The present noverify arm withholds mandatory candidates by definition, often ending incomplete. It tests refusal behavior, not whether a primary-only publication policy offers better quality per token. Any primary-only experiment should remain nonpublishing and be scored under its own declared output policy.

Sources: [cost table](prototype-runs-holdout/comparison-data.md), [metering implementation](tools/transcript_usage.py), [method and success criteria](prototype-runs-holdout/README.md), [evaluation](prototype-runs-holdout/evaluation.md).

External evidence is consistent with caution, not a replacement decision. Anthropic documents specialized parallel finders followed by verification, showing that discovery and verification are distinct responsibilities; it provides no controlled comparison against this skill. [Official Code Review documentation](https://code.claude.com/docs/en/code-review). The c-CRAB authors report that the evaluated agents collectively solve only around 40% of their tasks, reinforcing that agentic code review remains difficult; that benchmark is not a quality estimate for this repository. [c-CRAB paper](https://arxiv.org/abs/2603.23448).

## 4. Ranked improvements

Rank is the recommended investment order, not a GitHub defect severity. Cost/time effects below are hypotheses unless explicitly tied to measurements.

| Rank | Improvement | Quality impact | Token/cost impact | Completion-time impact |
| --- | --- | --- | --- | --- |
| 1 | Repair verifier safety/dispute handling; narrowed #119 | High for false clean conclusions and fix sufficiency | Small typical increase; selective follow-up cost | Longer only on triggered difficult cases |
| 2 | Expected-behavior and artifact discovery; #123 plus the claims-ledger portion of #121 | High for omissions outside the diff and issue-less changes | Targeted additional retrieval; could avoid a second finder | Some extra analysis on conformance changes |
| 3 | Execution-first changed-test correctness; narrowed #122 | High for cheap, concrete failures | Potentially less reasoning than mandatory exhaustive traces | Usually one focused command; environment setup can dominate |
| 4 | Verified medium-primary/high-verifier configuration; #124 as an experiment | Maintain quality if reproduced; inherited effort becomes explicit | Best measured lever: 37–41% billed savings on two targets | Lower output suggests savings; measure elapsed directly |
| 5 | Consolidate protocol and fix packet/renderer integration gaps | Better reliability and fewer lost findings | Less repeated serialization and instruction overhead; unmeasured | Fewer recovery loops; unmeasured |
| 6 | Bounded independent discovery challenger | Potential recall gain beyond primary candidate set | Additional or reallocated audit spend; measure marginal useful findings | Can overlap primary work but critical path must be measured |
| 7 | Calibrate questions, optional feedback, and severity | Higher signal and less author burden | Small saving or neutral | Small saving or neutral |

Before comparing these, repair the measurement method above. Do not require every useful implementation fix to wait for a large benchmark; require behavioral evidence before declaring its recall benefit established.

### Alternative prototype worth testing

Keep the current context collection, output contract, and publication machinery. Test a medium-effort primary with a fresh audit worker on one bounded high-risk or conformance surface. Give the worker the pinned code, expected behavior, and risk boundary, withholding the primary's conclusions until its first pass is frozen. Unlike the current verifier, it may originate a defect on that surface. It then checks relevant surviving claims. Newly discovered findings still require primary falsification and the applicable confirmation standard; never publish unconfirmed discoveries merely to fit the budget.

Compare three isolated changes rather than bundling them: improved integrated primary alone; the same primary with a stronger candidate verifier; the same primary with a discovery-enabled auditor. Reuse a task boundary or a small adapter; do not copy the entire skill and build a new orchestration framework first. Preserve a bounded work policy and explicitly count incomplete outcomes when its limit prevents confirmation.

The hypothesis is that independence is valuable when it brings a different search scope or reasoning capability, not simply another vote on the primary's proposed claim. Test it at matched total cost as well as natural cost. Adopt only if new held-out cases show improved per-run material-defect recall and fewer false clean outcomes, without materially worse false findings or unusable latency. A 20–30% relative recall gain at no more than about 25% added cost would be a useful initial screening target, not a statistically established universal threshold. Choose exact acceptance bounds before running the experiment.

## 5. Every open issue: disposition and sequence

| Issue | Recommendation | Priority/order | Rationale and required rescope |
| --- | --- | --- | --- |
| [#119](https://github.com/kamui/skills/issues/119) verifier safety rulings | Continue, revise before implementation | P0; first quality fix | Correctly targets false safety claims. Distinguish refutation from uncertainty. Its proposed follow-up can reopen a real defect yet leave it unpublishable because confirmation budget is spent. Measure that one-shot failure explicitly; do not claim a reopened row is recovered recall. Avoid a third recursive batch. |
| [#123](https://github.com/kamui/skills/issues/123) requirement restatement and upstream delta | Continue | P1; second | Strong mechanism-specific evidence. Restate requirements before compliance inspection, inspect authoritative versioned deltas, and check semantics as well as name presence. An export grep cannot detect every signature, conditional export, or platform mismatch. Treat copying the Panel mechanism as a hypothesis until measured in the integrated primary. |
| [#122](https://github.com/kamui/skills/issues/122) changed-test tracing | Continue, narrow | P1; third | Run cheap changed tests when feasible; trace suspicious or unexecutable cases. Do not require 2–6k tokens of reasoning per changed test function regardless of observed execution. Twenty functions at the ticket's estimate add 40–120k tokens before verifier duplication. Require failures attributable to head, not merely environment setup or an unrelated existing failure. |
| [#124](https://github.com/kamui/skills/issues/124) effort configuration | Continue as measured adoption | P1; prepare alongside the first fixes | Best empirical efficiency proposal. Keep verifier effort explicit in supported runtimes. Freeze the policy for matched medium/high primary controls; include a reasoning-heavy case and fresh tasks. Three Hyper seeds against a broken historical baseline are insufficient for broad adoption. Avoid inventing a universal cross-model `high` requirement. |
| [#121](https://github.com/kamui/skills/issues/121) PR-body claims | Split | Ledger portion P1, alongside #123; blanket question policy defer | Behavioral, compatibility, and performance promises belong in the ledger. Do not automatically make every unverified justification `Needs Information`. Ask only when the missing evidence affects correctness, a release constraint, or a material decision; inspect supplied benchmark evidence first. A second architecture run is not inherently required for every speedup claim. |
| [#120](https://github.com/kamui/skills/issues/120) automatic deferred-decision question | Do not implement as written; close or rewrite | P3 | A deliberate preview-stage deferral can mean “accepted for this merge, revisit before stabilization.” Automatically reopening it can duplicate a human decision and create noise. Surface it only when a present release/compatibility decision depends on it; score question usefulness separately from bug recall. |
| [#88](https://github.com/kamui/skills/issues/88) lower-tier replica | Park or replace with the bounded auditor experiment | P2 research, after repairs | No demonstrated incremental recall from the weaker replica; reconciliation adds token and instruction cost. Its stronger-primary holdout controls did not run. A small premium over an already expensive all-strong-model baseline is not evidence of efficiency against the economical default. Require useful per-run bugs, not merely a routed disagreement or question on one target. |
| [#70](https://github.com/kamui/skills/issues/70) early verifier dispatch | Defer | P3 | Primarily latency, not token savings. Extra timing rules can increase follow-up/incomplete outcomes. Measure actual elapsed overlap first, stabilize #119, then overlap independent work without changing discovery scope. |
| [#84](https://github.com/kamui/skills/issues/84) full-fidelity links | Keep selectively | P3 | Implement concrete path/revision failures when encountered; do not build all forge/provenance options speculatively. Core actionability checks and packet completeness come first. Exclude the v2a-only parts. |
| [#97](https://github.com/kamui/skills/issues/97) cache-write tier pricing | Continue when metering next changes | P3; before a mixed-tier-cache experiment | Accounting correctness, not runtime savings. On incomplete or inconsistent split data, do not silently underprice; report the residual as unknown/bounded or use a declared fallback. Existing all-5m rows need no repricing claim. |
| [#96](https://github.com/kamui/skills/issues/96) session-limit discards | Refresh and complete in evaluation setup | P3 | Keep abort costs and reset-aware scheduling. The original “before #60” dependency is obsolete. Two-cell concurrency is a heuristic, not proof of reducing total billed waste; use observed quota and duration where available. Separate arm cost from session overhead. |
| [#71](https://github.com/kamui/skills/issues/71) efficiency epic | Rewrite its active plan | P1 planning | Replace stale savings guesses and completed checklist entries with measured #124 adoption, real elapsed metering, packet/render simplification, and discarded-cost accounting. Keep cost and quality measured together. |
| [#62](https://github.com/kamui/skills/issues/62) original quality epic | Close as delivered with mixed evaluation outcomes; link a fresh plan | Administrative | Its definition of done is checked and holdout completed. Failure of some hypotheses should not keep the implementation epic open forever. Do not use its proposed c/d-only rerun to validate #119 and #122, whose failures were on Hyper and Cobra. Exclude Panel-specific work from the new plan. |

Recommended execution sequence: correct the measurement record and epics; fix #119 and the small input/output integration defects; land #123 plus the claims-ledger half of #121; narrow and land #122; freeze and measure #124 with matched controls; then decide whether the bounded discovery prototype buys enough additional recall. Handle #96/#97 while preparing that evaluation. Leave #120, #70, the large parts of #84, and replica orchestration outside the critical path.

All five recent quality tickets defer the workflow bump to a separate future ticket, but no such open ticket appears in the fetched issue set. Add the release/version step to the active plan, or bump for each independently released semantic change. Do not leave behavior-changing releases sharing an identity merely because the intended final bump ticket was never created.

The product objective should be expected actionable defects recovered in one completed run, with a strict false-finding constraint and measured token/elapsed budgets. Correct questions and clean-review handling still matter, but neither more questions nor more elaborate ledgers are substitutes for that outcome.
