# Model-tier-split evaluation arm — Sonnet 5 primary, Opus 5 verifier

**2026-09-01.** This document specifies one experiment arm for the next evaluation round of the
`code-review-publish` line. It extends the protocol in
[Aggregate analysis § Before calling it: the evaluation protocol](prototype-runs-aggregate-tests-1-3-v2-v5.md#before-calling-it-the-evaluation-protocol),
whose item 4 puts a controlled model-tier comparison after — and only after — repeated seeds with one
model held constant. Nothing here changes a skill default: no `SKILL.md`, reference, or
`agents/openai.yaml` selects a tier as a result of this document. v5a's design record keeps
model-tier splits in its deliberate exclusions until this round runs.

## 1. Hypothesis

**A Sonnet 5 primary reviewer with an Opus 5 verifier preserves v5a's recall and calibration on the
adjudicated target set at materially lower cost than an all-Opus configuration.**

Two observations from the aggregate analysis motivate testing it rather than assuming it:

- **Recall at the Sonnet tier.** Test 3 (`tokio-rs/tokio#7757`) ran on Claude Sonnet 5, and every
  prototype caught the ground-truth production regression that 52 human review threads and an
  approval had missed, from a static pass over the merge-base diff
  ([experiment grid](prototype-runs-aggregate-tests-1-3-v2-v5.md#the-experiment-grid),
  [aggregate outcomes](prototype-runs-aggregate-tests-1-3-v2-v5.md#aggregate-outcomes)). The
  same analysis records that test 3's mirror history was not truncated at the merge-base, so its
  *severity calibration* is contaminated by hindsight
  ([methodology debts](prototype-runs-aggregate-tests-1-3-v2-v5.md#9-methodology-debts-that-gate-the-next-iteration));
  the recall observation is what carries here, and it is the reason this arm is plausible, not proven.
- **Restraint below the Opus tier.** Test 2 (`redis/redis#15680`) ran on GLM-5.3-Flash, a cheaper
  model than either Claude tier, and every prototype raised and killed its candidates — 29 across the
  four runs — publishing zero findings on a clean PR with no originating issue
  ([aggregate outcomes](prototype-runs-aggregate-tests-1-3-v2-v5.md#aggregate-outcomes)). The
  no-false-positives discipline is enforced by the falsification gates in the skill text, and it held
  without the strongest model.

Neither observation is a controlled tier comparison: model and harness changed *between* tests, so no
cross-test difference is attributable to tier alone. That is exactly what this arm measures.

## 2. Arms

All three arms run the **identical v5a skill text** (`workflow=v5a-1` or its successor, version-stamped
and frozen before the round) on the **identical targets**, with the same seeds, the same
history-truncated mirrors, and the same adjudicated ground truth.

| Arm | Primary reviewer context | Verifier context(s) | Role |
| --- | --- | --- | --- |
| A | Opus 5 | Opus 5 | Baseline; the configuration the current evidence describes |
| B | Sonnet 5 | Opus 5 | The hypothesis: cheap breadth, expensive adjudication |
| C | Sonnet 5 | Sonnet 5 | Floor arm; only meaningful if B passes |

The orchestrating context's model is recorded for every run in every arm (see § 6). Arms differ in
model assignment only — no arm may edit skill text, thresholds, or verifier triggers.

## 3. Cost math

Using test 1's measured v5 shape — 128k tokens in the primary context and 46.6k in the verifier
context, the only clean, comparable token data the program has
([economics](prototype-runs-aggregate-tests-1-3-v2-v5.md#8-economics-what-the-cost-data-actually-supports))
— and assuming an 80/20 input/output split within each context, at first-party prices of
Opus 5 $5/MTok input and $25/MTok output and Sonnet 5 $2/MTok input and $10/MTok output:

| Context | Tokens | Input (80%) | Output (20%) | Opus 5 $ | Sonnet 5 $ |
| --- | --- | --- | --- | --- | --- |
| Primary | 128,000 | 102,400 | 25,600 | $1.152 | $0.461 |
| Verifier | 46,600 | 37,280 | 9,320 | $0.419 | $0.168 |

| Arm | Primary $ | Verifier $ | Total $ per review | vs. arm A |
| --- | --- | --- | --- | --- |
| A — all Opus 5 | $1.152 | $0.419 | **$1.571** | — |
| B — Sonnet primary, Opus verifier | $0.461 | $0.419 | **$0.880** | −44% |
| C — all Sonnet 5 | $0.461 | $0.168 | **$0.629** | −60% |

Read these as the shape of the lever, not as a forecast: the 80/20 split is an assumption, test 1's
token counts are development-set, and the orchestrating context is unmetered in that data. Each run
of this round supplies its own measured tokens per context, and the table is recomputed from them.

## 4. Measurements per run

Record, per run and per context:

1. **Recall** — findings matched against the adjudicated ground truth for the target: true findings
   found, true findings missed, listed by ground-truth id.
2. **Precision and calibration** — findings that are false, plus findings that are true but
   miscalibrated (wrong priority, wrong `action`, wrong `blocking`), and the resulting semantic status.
3. **Verifier verdict quality** — every verdict (`confirmed`, `plausible`, `refuted`) against the
   adjudicated truth, plus whether the verifier corrected the primary's `change` at the invariant
   level where the bug class demanded it, and whether any clean-verdict batch re-opened a disposition
   correctly or spuriously.
4. **Tokens per context** — primary, each verifier batch, and the orchestrating context, reported
   separately; note explicitly which contexts the harness metered.
5. **Computed $** — from the measured tokens and the prices in § 3, itemized by context so a price
   change can be reapplied later.

Questions and observations published are recorded alongside, since a tier change could plausibly move
candidates between the finding, question, and observation channels without changing recall counts.

## 5. Decision rule

Apply mechanically, across the whole evaluation set rather than per target:

- **Adopt B as the default only if B loses no adjudicated true finding and adds no false finding
  relative to arm A across the evaluation set.** A miscalibrated-but-true finding is not a loss under
  this rule; record it and report it, but it does not by itself block adoption.
- **C is adopted only if B has already passed and C matches B** on the same two conditions — no
  adjudicated true finding lost, no false finding added.
- **Otherwise A stays the default.** A tie on findings with worse verifier verdict quality is not a
  pass; the two conditions are necessary, not sufficient, and the adopting decision must also state
  that verdict quality did not degrade.

Cost never overrides the recall condition: the arm exists to buy the same review for less, not a
weaker review for less.

## 6. Harness notes

- **Pinning the model per context.** The primary reviewer and each verifier batch run as sub-agents
  launched by the orchestrating context. In this harness the sub-agent is launched with an explicit
  model parameter — the `Agent`/`Task` tool's `model` field, set to `sonnet` or `opus` — so arm B is
  expressed as primary `model: sonnet` and verifier `model: opus`. Do not rely on a default: a
  sub-agent launched without the field inherits a configured default and silently invalidates the arm.
- **The orchestrating context.** Whatever tier drives the run must be recorded even when it performs
  no review work itself, because it reads inputs, assembles payloads, and publishes.
- **Where it is recorded.** Model assignment is per-run-record metadata. Each run record states the
  model for the orchestrating context, the primary context, and each verifier context, mirroring the
  existing `Model / harness` rows in the `prototype-runs-2026-09-01-test-*/v*-run.md` records and the
  [experiment grid](prototype-runs-aggregate-tests-1-3-v2-v5.md#the-experiment-grid). A run whose
  record does not state all three is excluded from the arm's results.
