# Evaluating six agentic code-review prototypes on one pinned pull request

> **Promotion status:** “v5” is the historical prototype name used by this record. PR #17 promoted
> that workflow to `skills/code-review-publish` on `main`; new work should invoke
> `/code-review-publish` without the `-5` suffix. **Superseded 2026-09-03:** PR #42 replaced that skill with **v5a**, so `/code-review-publish` now invokes v5a, not the v5 workflow this record tests. `skills/code-review-publish-legacy` is the v1 legacy reviewer, and v5 is no longer on `main` — pin it from `571f31d`.

**2026-09-01–03.** This evaluates the original v2–v5 comparison and the later v2a/v5a mechanism
retests against one pinned revision of
[`kamui/shortlist#66`](https://github.com/kamui/shortlist/pull/66). V2a has two Sonnet records: a
superseded pre-C9 run and a post-C9 run, retained as a controlled before/after.

Raw records: [method and inputs](README.md), [v2](v2-run.md), [v3](v3-run.md), [v4](v4-run.md),
[v5](v5-run.md), [v2a before C9](v2a-run-pre-c9.md), [v2a after C9](v2a-run.md),
[v5a](v5a-run.md), the [2026-09-02 addendum](addendum-2026-09-02.md), the
[2026-09-03 addendum](addendum-2026-09-03.md), and [comparison data](comparison-data.md).
The model-drifted [Fable v2a run](../prototype-runs-2026-09-01-test-1-fable/evaluation.md) is
evaluated separately and used here only as sensitivity evidence.

## Conclusion

**The new runs validate two search mechanisms, but they do not displace the original conclusion
that v4/v5 produced the best-calibrated artifacts on this target.** The strongest new result is a
model-matched v2a before/after: after C9 required each finder to write and sweep every changed
contract, the Narrow sibling drift moved from completely absent to independently raised by both
axes. V5a's repo-wide peer-set sweep also found the exact Narrow sibling it was designed to find.

Those are mechanism successes, not general-quality wins:

- both Sonnet retest architectures turned the Narrow documentation drift into a merge blocker,
  while v4 and v5 retained the same fact as non-blocking advice;
- post-C9 v2a still missed the commerce-only validator regex, and its Requirements finder failed to
  return the required row-wise disposition ledger;
- v5a found only the Narrow drift, missing the bundle-contract drift and treating the regex only as
  an observation; and
- the Fable run found a broader set and the only ambiguous/question outcome, showing that one run
  per cell is too noisy to rank architectures by recall.

No single run is a complete ideal review. The best-supported publication remains advisory:
identify the Narrow entrypoint and bundle-contract lists as real, non-blocking synchronization
drift; mention the validator's commerce-only timestamp enforcement at most as a `consider` finding
or bounded observation; do not block on a new freshness field without resolving the specification
ambiguity. V4/v5 were closest to that shape. V5 remains the stronger architectural base because its
verifier alone demonstrated the valuable verdict “fact confirmed, merge consequence disproved.”
The v2a changed-contract sweep and v5a repo-wide peer discovery are worth carrying forward as
targeted mechanisms.

## Controlled method and evidence boundaries

All runs reviewed the same target identity:

| Input                 | Pinned value                                                       |
| --------------------- | ------------------------------------------------------------------ |
| Pull request          | [`kamui/shortlist#66`](https://github.com/kamui/shortlist/pull/66) |
| Head                  | `4349ff41ff4d134e09017662dd30420b80e8eb30`                         |
| Base / merge-base     | `ccd1842d742fd940b2afde4f903c7bdcb3a707eb` on `main`               |
| Diff                  | 9 files, +160/−6, one commit                                       |
| Specification         | `kamui/shortlist#45`; 10 acceptance criteria                       |
| Prior review state    | none                                                               |
| Publication authority | self-review; `COMMENT` only                                        |

The original four runs used Claude Opus 5 at High reasoning under Claude Code. The later Sonnet
runs used `claude-sonnet-5` at default reasoning under `t3code`. The Fable run used
`claude-fable-5-1` and suffered a rate-limit split. Results are comparable within a controlled
cohort, not as one seven-column model/cost ranking.

The original v2–v5 cohort is one run per prototype. The later v2a/v5a skills were designed after
their authors saw this target and the earlier results. They are therefore development-set tests of
named mechanisms. Runtime isolation prevents prior findings from entering a prompt; it cannot undo
design-time exposure.

The controls also do not create complete ground truth. This target is documentation/schema-heavy,
the reviewer author and pull-request author are the same person, and disputed severity was not
independently adjudicated. The evidence is strongest for observable search, verification, and
calibration behavior.

## Architecture, output, and cost

The full measurements are in [comparison data](comparison-data.md). The outcome summary is:

|                | v2                | v3                | v4       | v5       | v2a pre-C9 | v2a post-C9       | v5a               |
| -------------- | ----------------- | ----------------- | -------- | -------- | ---------- | ----------------- | ----------------- |
| Findings       | 4                 | 1                 | 2        | 2        | 1          | 3                 | 1                 |
| Blocking       | 2                 | 1                 | 0        | 0        | 0          | 1                 | 1                 |
| Status         | Changes Requested | Changes Requested | Approved | Approved | Approved   | Changes Requested | Changes Requested |
| Fresh verifier | yes               | no                | yes      | yes      | yes        | yes               | yes               |

Within the original cohort, v3 was cheapest at 110,630 tokens; v4 and v5 were effectively tied at
175,824 and 174,563; v2 cost 253,712. V2's duplicated whole-context pass bought breadth but not
better calibration.

The later figures use a different meter. V2a reports a primary wrapper and three internally metered
children; v5a reports one outer total. Adding or comparing those numbers as if they represented the
same boundary would be false precision. At the architectural level the stable conclusion remains:
the panel repeats the full review across two finders, while the integrated line pays for a verifier
only after primary falsification.

## What the expanded finding matrix says

### Narrow refresh drift: stable fact, unstable action

Every original prototype found the closed list in `skills/shortlist-narrow/SKILL.md:46`. The v2a
pre-C9 run was the first miss: neither finder raised or acquitted it. Post-C9, both Sonnet finders
raised it independently; v5a found it through the repo-wide old-wording/new-vocabulary sweep.

The factual case is strong. The stage entrypoint says to follow the generalized protocol but later
restates a closed list at the point of execution. The changed fixture supplies a Research-origin
Volatile class outside that restatement. History also shows the two documents were previously
updated together.

The action is not stable:

| Run         | Action                               |
| ----------- | ------------------------------------ |
| v2          | P1 must-fix                          |
| v3          | P2 blocking                          |
| v4          | P2 consider                          |
| v5          | P3 consider after verifier downgrade |
| v2a pre-C9  | missed                               |
| v2a post-C9 | P1 must-fix                          |
| v5a         | P2 must-fix                          |
| Fable v2a   | P2 consider                          |

The canonical protocol remains correct and the skill links to it, which argues against blocking.
The entrypoint is also an executed operational contract, which makes the drift more than cosmetic.
The available evidence supports `consider`; it does not distinguish P2 from P3. The Sonnet retests
demonstrate recall improvements but regress toward the same over-blocking behavior that weakened v2
and v3.

### Bundle Kind enumeration: real but low consequence

V2, v4, v5, v2a pre-C9, v2a post-C9, and the Fable v2a run all found the unchanged bundle summary
that omits `Volatile-claim class`; v3 dropped it and v5a did not raise it. The line is open-ended and
links to the canonical schema, so runtime omission is unproved. History shows the bundle summary
was updated with the same peer set on prior enum extensions. P3 `consider` is the best-supported
band; v2's P1 must-fix and post-C9 v2a's P1 priority overstate its consequence.

### Timestamp enforcement: rediscovery, not a new item

The commerce-only regex at `validate-completion.py:2949` was confirmed in the original v2 run as
F3, with a concrete generalized-versus-price fixture mutation. The later Fable v2a run independently
reconstructed the same asymmetry. V5a routed it to Observations; v3 dropped a related claim; the
post-C9 Sonnet v2a run missed it entirely.

The 2026-09-02 addendum calls the Fable result a “third drift” that no prior prototype had raised.
That conflicts with the raw [v2 run](v2-run.md), which names the same regex and fix line. This
evaluation follows the raw record. The repeated independent confirmation strengthens the factual
case, but the new judgment-only Freshness attestation makes the desired enforcement policy
debatable. A non-blocking finding or observation is warranted; a blocker is not.

### Freshness expectation: specification ambiguity

V2 confirmed a P2 finding that the Evidence schema has no defined carrier for a
“category-appropriate freshness expectation.” V3 and v5 marked the criterion met through required
`Observed` evidence; v4 dropped the candidate; pre-C9 v2a called it pre-existing; post-C9 Sonnet and
v5a did not raise it. The Fable verifier returned `plausible` and converted it to a question because
free-text fields can carry an expectation and the issue does not unambiguously require a structured
field.

The question treatment is the most defensible. It is also the only `plausible` verdict in this
target's expanded corpus, proving that the branch is reachable even though the Sonnet cohort did
not exercise it.

### Research entrypoint wording

Post-C9 v2a and Fable v2a confirmed that `shortlist-research/SKILL.md:39` says only “add” where the
protocol now says add, refine, or mark inapplicable. Earlier runs either dropped or did not raise it.
The stale paraphrase is factual; its demonstrated consequence is weaker than the Narrow item. P3
`consider` is the upper defensible bound, and an observation would also fit.

## The C9 before/after

The Sonnet pair holds the configured model, target, packet, clone, and harness constant and changes
the v2a skill from `5db5903` to `87c68a9`:

|                       | Before C9                | After C9                      |
| --------------------- | ------------------------ | ----------------------------- |
| Bundle drift          | Requirements axis only   | both axes                     |
| Narrow drift          | absent from both ledgers | both axes, verifier-confirmed |
| Candidates / findings | 1 / 1                    | 5 / 3 after two merges        |
| Status                | Approved                 | Changes Requested             |

The output exposes the causal mechanism: each finder first records the changed contract, and the
old-fragment sweep on the closed-list-to-open-rule change surfaces the sibling entrypoint. This is
good evidence that C9 changes search behavior as intended. It is not evidence that every such peer
will be found: the same run missed the regex, and one controlled pair cannot estimate recall.

C9 also has an auditability result. The Code finder returned a 20-row ledger; the Requirements
finder returned its changed-contract prose without the required one-row-per-hypothesis ledger. The
orchestrator correctly reported a partial C3 failure rather than reconstructing missing rows. A
mechanism intended to make search auditable needs its output-shape requirement enforced, not merely
stated.

## V5a's peer sweep

V5a's `ff94971` mechanism also fired exactly as designed: it started at repository root, searched
case-insensitively for old wording and new vocabulary, enumerated sibling skills, and surfaced
`shortlist-narrow/SKILL.md:46`. A fresh verifier repeated the search and confirmed the item.

That establishes the mechanism can repair the particular discovery failure that motivated it. The
same run did not find the bundle summary, treated the regex as a non-actionable observation, and
proposed a blocker. It is one development-set run, so the correct conclusion is “peer discovery
worked on its target,” not “v5a has better recall or calibration.”

## Verification behavior

Fresh verification remains the most valuable shared mechanism:

- v2 removed two false candidates and merged a cross-axis duplicate;
- v4 narrowed mechanisms and cut an unsupported impact;
- v5 confirmed the Narrow fact while rejecting its merge consequence, changing the status to
  Approved without erasing the finding;
- pre-C9 v2a narrowed the bundle trigger;
- post-C9 v2a corrected one trigger but confirmed all five candidates, including the blocker; and
- v5a confirmed its sole blocker without recalibration.

Only v5 demonstrates the full desired verdict vocabulary on this target: verification can preserve
a factual finding while changing priority and action. The retest verifiers show that independence
does not automatically improve calibration; a verifier can confidently agree with an over-strong
primary.

## Prototype verdicts

**V2 — broad recall, excessive action.** It found four substantive items, including the regex and
freshness-carrier issue later addenda accidentally described as new. Its verifier removed false
claims, but the priority-to-action coupling made two documentation drifts blockers at the highest
cost in the clean cohort.

**V3 — economical but under-verified.** It delivered complete coverage at the lowest measured cost,
but its sole blocking conclusion received no fresh check and it dropped a provable low-impact drift.

**V4 — strongest published artifact.** It retained the two central drifts as optional, improved
both through verification, recovered transparently from missing context, and published a defensible
advisory review.

**V5 — strongest base architecture.** It matched v4's material output at the same cost, with fewer
tools and the best observed action recalibration. Its development-set exposure and one-run evidence
still prohibit a categorical win.

**V2a — successful search experiment, not a better default.** C9 demonstrably recovered a missed
peer and the panel gives a rich audit trail when both axes comply. It is expensive, duplicated, and
its post-C9 run both missed another live drift and over-blocked the target.

**V5a — targeted discovery success, limited breadth here.** The peer sweep found its intended
sibling with a simpler integrated shape. This run alone offers no evidence that its blocker was
better calibrated or that its recall is broader than v5's.

## Recommendation and remaining experiments

Carry forward the integrated v5/v5a line, with:

1. v2a's explicit changed-contract inventory and paired old/new repo-wide sweep;
2. v5a's peer-set discovery rule;
3. action independent from priority and a verifier empowered to downgrade across the blocking
   boundary;
4. a required, mechanically checked disposition ledger for every reviewing role; and
5. an observation/question channel for accurate facts whose consequence or specification status is
   unresolved.

Before making a prototype-level claim, freeze the workflow and run repeated, blinded seeds on new
adjudicated targets. Include unchanged-file requirement omissions, open-list-to-closed-list drift,
an intentionally ambiguous schema requirement, and a low-impact candidate proposed as must-fix.
Report model identity explicitly on every agent, keep cost cohorts separate, and verify both
findings and high-risk acquittals. This target shows why: search success, finding completeness, and
merge calibration are three different outcomes.
