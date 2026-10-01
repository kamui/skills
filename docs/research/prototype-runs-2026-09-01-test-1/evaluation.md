# Evaluating six agentic code-review prototypes on one pinned pull request

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

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

The controls also do not create complete ground truth. This target is documentation/schema-heavy,
the reviewer author and pull-request author are the same person, and disputed severity was not
independently adjudicated. The evidence is strongest for observable search, verification, and
calibration behavior.

## Architecture, output, and cost

The full measurements are in [comparison data](comparison-data.md). The outcome summary is:

|                | v3                | v4       | v5       | v5a               |
| -------------- | ----------------- | -------- | -------- | ----------------- |
| Findings       | 1                 | 2        | 2        | 1                 |
| Blocking       | 1                 | 0        | 0        | 1                 |
| Status         | Changes Requested | Approved | Approved | Changes Requested |
| Fresh verifier | no                | yes      | yes      | yes               |

### Narrow refresh drift: stable fact, unstable action

The factual case is strong. The stage entrypoint says to follow the generalized protocol but later
restates a closed list at the point of execution. The changed fixture supplies a Research-origin
Volatile class outside that restatement. History also shows the two documents were previously
updated together.

The action is not stable:

| Run         | Action                               |
| ----------- | ------------------------------------ |
| v3          | P2 blocking                          |
| v4          | P2 consider                          |
| v5          | P3 consider after verifier downgrade |
| v5a         | P2 must-fix                          |

### Freshness expectation: specification ambiguity

The question treatment is the most defensible. It is also the only `plausible` verdict in this
target's expanded corpus, proving that the branch is reachable even though the Sonnet cohort did
not exercise it.

## The C9 before/after

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

**V5a — targeted discovery success, limited breadth here.** The peer sweep found its intended
sibling with a simpler integrated shape. This run alone offers no evidence that its blocker was
better calibrated or that its recall is broader than v5's.

## Recommendation and remaining experiments

Carry forward the integrated v5/v5a line, with:

Before making a prototype-level claim, freeze the workflow and run repeated, blinded seeds on new
adjudicated targets. Include unchanged-file requirement omissions, open-list-to-closed-list drift,
an intentionally ambiguous schema requirement, and a low-impact candidate proposed as must-fix.
Report model identity explicitly on every agent, keep cost cohorts separate, and verify both
findings and high-risk acquittals. This target shows why: search success, finding completeness, and
merge calibration are three different outcomes.
