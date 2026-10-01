# Model-tier-split evaluation arm — Sonnet 5 primary, Opus 5 verifier

## 1. Hypothesis

**A Sonnet 5 primary reviewer with an Opus 5 verifier preserves v5a's recall and calibration on the
adjudicated target set at materially lower cost than an all-Opus configuration.**

Two observations from the aggregate analysis motivate testing it rather than assuming it:

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
