<!-- Rendered by scripts/score_attempts.py from the third case in scripts/scoring-fixtures.json.
     Every number is synthetic. It shows the shape of the scorecard #152 and #153 will read;
     it is not a result and describes no real attempt. -->

# Scorecard: issue-138-fixture (truth v1)

| Arm | Attempts | Valid completed | Completion | Macro recall (all) | Macro recall (completed) | False clean | Raw false findings | Action errors | Sufficient-outcome recall | Billed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 6 | 6 | 1.000 | 0.250 | 0.250 | 2 (0.500) | 0 | 0 | 0.333 | $18.00 |
| B | 6 | 6 | 1.000 | 1.000 | 1.000 | 0 (0.000) | 0 | 0 | 0.667 | $20.40 |
| C | 6 | 6 | 1.000 | 1.000 | 1.000 | 0 (0.000) | 0 | 0 | 1.000 | $21.80 |

## Screen: B against A — **pass**

- **zero candidate-arm false findings** — pass: 0 raw false finding items (0 of them in invalid or incomplete attempts)
- **no worse false-clean count or rate** — pass: B: 0 (0.0) against A: 2 (0.5)
- **no worse completion** — pass: B: 1.0 against A: 1.0
- **macro material recall gain (all attempts)** — pass: 1.000 against 0.250: +300.0% relative, +0.750 absolute (gate +20% relative and positive absolute)
- **macro material recall gain (completed only)** — pass: 1.000 against 0.250: +300.0% relative, +0.750 absolute (gate +20% relative and positive absolute)
- **matched billed cell-cost ratio** — pass: median 1.133 over 6 matched pairs (gate <= 1.25)

A positive screen recommends a fresh confirmation study against the then-current integrated policy. It is not a promotion and not an equivalence claim: four targets and two replicates cannot support one.

## Screen: C against A — **pass**

- **zero candidate-arm false findings** — pass: 0 raw false finding items (0 of them in invalid or incomplete attempts)
- **no worse false-clean count or rate** — pass: C: 0 (0.0) against A: 2 (0.5)
- **no worse completion** — pass: C: 1.0 against A: 1.0
- **macro material recall gain (all attempts)** — pass: 1.000 against 0.250: +300.0% relative, +0.750 absolute (gate +20% relative and positive absolute)
- **macro material recall gain (completed only)** — pass: 1.000 against 0.250: +300.0% relative, +0.750 absolute (gate +20% relative and positive absolute)
- **matched billed cell-cost ratio** — pass: median 1.200 over 6 matched pairs (gate <= 1.25)

A positive screen recommends a fresh confirmation study against the then-current integrated policy. It is not a promotion and not an equivalence claim: four targets and two replicates cannot support one.
