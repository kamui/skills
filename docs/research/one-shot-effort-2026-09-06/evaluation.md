# Evaluation — medium primary with pinned high verifiers (issue #124)

**2026-09-06.** Fourteen planned cells; every attempt, its disposition and its cost are in
[`ledger.md`](ledger.md), every per-attempt row in [`comparison-data.md`](comparison-data.md),
and the per-target scoring in [`scoring/`](scoring/). The preregistration is
[`README.md`](README.md) §1; the screening rule is applied here exactly as frozen there.
Known-Hyper and fresh-target outcomes are reported separately, as the ticket requires.

## What ran

All fourteen planned cells ran as first attempts, all fourteen are valid completed attempts, and no
replacement was used (14 attempts of the 16 allowed). Every transcript line of every attempt shows
`claude-sonnet-5`; every control primary shows `high`, every candidate primary `medium`, and every
verifier batch (9 of 14 attempts dispatched one) `high` through the `v5b-verifier-effort-high`
definition ([comparison-data, Model and effort verification](comparison-data.md#model-and-effort-verification)).
No session-limit notice arrived; quota stayed `unknown` throughout. One setup failure (ledger S8)
dispatched no reviewer. Both freeze commits precede the dispatches they govern
(`30c2f2f` 07:55:02Z before att-01 at 07:55:17Z; `edfb4b3` 08:15:40Z before att-07 at 09:12:52Z),
and no Hyper payload was read before the stage-2 commit.

| Target | Planned | Valid completed | Replacements | Verifier batches (`high` / `medium`) |
| --- | --- | --- | --- | --- |
| (a) Hyper | 6 | 6 | 0 | 1 / 3 |
| (g) bytes | 4 | 4 | 0 | 2 / 2 |
| (h) etcd | 4 | 4 | 0 | 1 / 1 |

## Results by target

### (a) `hyperium/hyper#3952` — regression fixture, GT-a1 (the hot loop)

Six valid completed attempts, three per arm ([`scoring/a.md`](scoring/a.md)).

| Arm | GT-a1 recovered | Target recall | False findings | False clean | Fix level | Verifier batches |
| --- | --- | --- | --- | --- | --- | --- |
| `high` | 1 of 3 (att-01) | 33% | 0 | 2 of 3 (att-04, att-05) | invariant ×1, none ×2 | 1 of 3 |
| `medium` | 3 of 3 | 100% | 0 | 0 of 3 | invariant ×3 | 3 of 3 |

The two control misses share one shape: the primary raised the concurrency candidate, dropped it
in its own falsification ("consequence unproven"), kept two accurate test-hygiene `consider`
items, and so met no mandatory trigger — two survivors made zero-survivor mode inapplicable and
none was `must-fix`. The pinned skill then requires no verifier, the review approves, and nothing
checks the acquittal. The holdout's `v5b` seed 3 acquitted GT-a1 through a verifier that overshot;
here the acquittal never reached one. All three candidate-arm primaries published GT-a1 as
`must-fix` (P1, P1, P0, kind `concurrency`/`performance`), each with an invariant-level fix
(gate continuation on real write progress), and each therefore ran a verifier batch that confirmed
it. Every `consider` item in both arms was accurate and inside the register's "not ground truth"
allowance; no attempt asserted the iteration bound, the dev-dependency or the `Future`-contract
doubt as a defect.

### (g) `tokio-rs/bytes#698` — fresh, GT-g1 (capacity no longer consumed)

Four valid completed attempts, two per arm ([`scoring/g.md`](scoring/g.md)).

| Arm | GT-g1 recovered | Target recall | False findings | False clean | Verifier batches |
| --- | --- | --- | --- | --- | --- |
| `high` | 0 of 2 | 0% | 0 | 2 of 2 | 2 (clean-verdict) |
| `medium` | 0 of 2 | 0% | 0 | 2 of 2 | 2 |

All four approved after a verifier batch. The miss is not an effort effect: the change's stated
purpose ("reuse the full capacity") was taken as the specification, so the observable
capacity/cursor contract change was never a candidate in three attempts and was raised and
acquitted as `intentional` in the fourth (att-07, control), whose clean-verdict batch did not
re-open it. Two attempts (att-09 candidate, att-10 control) executed code at the head; att-09
measured the exact difference (capacity retained at the head, consumed at the merge-base) and
reported it as the optimization working. The register's plausible non-defects were all handled
correctly; no false findings.

### (h) `etcd-io/etcd#18749` — fresh, adjudicated clean

Four valid completed attempts, two per arm ([`scoring/h.md`](scoring/h.md)).

| Arm | Status | False findings | Action errors | Items published |
| --- | --- | --- | --- | --- |
| `high` | Approved ×2 | 0 | 0 | one P3 `consider` (test backend not closed); two accurate observations |
| `medium` | Approved ×2 | 0 | 0 | one P3 `consider` (same); one accurate observation with a wrong line pointer |

Every attempt raised the register's tempting objection (the lock leak on a recovered panic) and
falsified it on the absence of any recovery on the apply path, which is the register's own
reasoning. Both arms are correct and indistinguishable here.

## Screening rule

Applied over all fourteen valid completed cells, candidate (`medium`) against control (`high`),
exactly as frozen in README §1.1. Attempt-level and completed-only views coincide because every
attempt completed. Buggy targets for the macro: (a) and (g); (h) is outside the recall
denominators.

| Gate | Control `high` | Candidate `medium` | Known Hyper only | Fresh only | Result |
| --- | --- | --- | --- | --- | --- |
| 1. Zero candidate-arm raw false findings | 0 | **0** | 0 | 0 | **met** |
| 2. No more false-clean outcomes (buggy targets, 5 attempts per arm) | 4 / 80% | **2 / 40%** | 2 vs 0 | 2 vs 2 | **met** |
| 3a. Macro material recall not lower (2 buggy targets) | (33% + 0%) / 2 = 17% | **(100% + 0%) / 2 = 50%** | 33% vs 100% | 0% vs 0% | **met** |
| 3b. Completion rate not worse | 7/7 | 7/7 | 3/3 vs 3/3 | 4/4 vs 4/4 | **met** |
| 4. Matched median billed cost ratio `<= 0.80` | — | **0.94** (n = 7; pairs 0.65, 0.93, 1.37, 1.17, 1.35, 0.94, 0.78) | 0.93 (n = 3) | 1.05 (n = 4) | **not met** |

Sufficient-outcome recall (`S_i / D_t`) equals material recall in every attempt that recovered a
defect: all three candidate recoveries on Hyper carry invariant-level fixes; the control's one
recovery does too. Union recall is diagnostic only: 1/1 on (a) for both arms, 0/1 on (g) for both.

**Verdict: the screen fails at gate 4. The default effort is retained.** Gates 1–3 are met on the
full grid and on the known-Hyper subset; on the fresh subset gates 1–3 are met only trivially
(equal false cleans, zero recall in both arms on (g), no defects on (h)), which the ticket's rule
treats as insufficient for a runtime-specific recommendation on its own. Under the method, a
quality improvement that misses the cost gate is a reported tradeoff, not adoption. What is on
record: on the one reasoning-heavy target where the arms differ, the `medium` primary with pinned
`high` verifiers published the defect three times out of three with an invariant-level fix and
ran a verifier each time, while the `high` primary published it once and approved twice without
any verifier. Three seeds per arm on one target do not establish a population effect; the
holdout's `v5b` seeds 1–3 on the same target (found, closing-path projection, acquitted) show the
control's own spread.

## Cost

Raw billed dollars are the decision quantity. Every cell has exactly one attempt, so per-arm
valid-run cost, all-attempt cost and matched cost use the same fourteen numbers.

| View | `high` (n = 7) | `medium` (n = 7) |
| --- | --- | --- |
| Billed, median (min–max) | $2.88 ($2.15–$5.23) | $2.91 ($2.23–$3.73) |
| Production-shaped, median | $2.79 | $2.79 |
| Per-target billed median: (a) / (g) / (h) | $3.09 / $2.22 / $3.02 | $3.38 / $2.79 / $2.61 |
| Thinking tokens, median | 47,631 | 36,382 (−24%) |
| Output tokens, median | 82,575 | 87,703 |
| Turns / tool calls, median | 60 / 67 | 60 / 77 |
| Elapsed to completion, median | 1,000 s | 1,007 s |
| Arm total | $21.52 | $20.78 |

The holdout's −40% did not replicate. Three things account for it. The candidate primaries
thought less (−24% median thinking) but made as many requests and more tool calls, and each
request replays the whole context, which is where a run's dollars go; on the two buggy targets
the candidate arm's per-target medians are higher, not lower. The cheapest control cells are the
ones that skipped verification (att-04, att-05, att-14 dispatched no batch), so on Hyper the
control's approvals cost $2.72–$3.09 against $2.86–$3.73 for the candidate's must-fix reviews with
a confirmed verifier verdict; the matched ratio rewards the miss. And every headless session wrote
the 1-hour cache tier, priced at ×2.0, in both arms (per-row `5m`/`1h` splits in comparison-data),
which raises absolute dollars relative to the holdout's in-session cells without moving ratios.

**Ticket total:** $49.42 of the $110 cap — setup and probes $7.12 (S1–S7: probes $0.22, target
vetting $5.44, adjudication $1.46; provisioning $0) plus fourteen cells $42.30; no replacements,
no discarded attempts, no notice-only rows, no tool or repro charges. No closeout adjudication
spend: no unexpected plausible true finding arose, so no blinded adjudication was needed. The
maintainer's mid-grid instruction to run helper agents on Opus 5 at high effort (10:00Z,
recorded in the ledger) post-dates every helper dispatch; every helper here ran on Sonnet 5.

## Limitations

- **Sample size.** Seven cells per arm, one to three replicates per target. The recall and
  false-clean differences rest on three Hyper seeds per arm; the fresh pair added no
  discriminating evidence (four misses on (g), four correct approvals on (h)).
- **The fresh buggy target discriminated nothing.** GT-g1 is a contract change the pull request
  itself asks for; every attempt treated the stated purpose as the specification. That is a
  register-independent skill limitation (no rule makes "the promised behavior is an observable
  contract change" a candidate) and it caps what this grid can say about effort on fresh targets.
- **Verification is consequence-triggered, so the control's cheap approvals are a skill outcome.**
  Two Hyper controls and one etcd control approved with hygiene `consider` survivors and never ran
  a verifier; the method scores them as valid completed attempts. Whether that rule should change
  is outside this ticket.
- **Blinding was imperfect on replicate 1 of Hyper** (README §1.1 deviation): the control payload
  named its cell. All later payloads were redacted before reading.
- **Absolute dollars are not comparable to the holdout** (1-hour cache tier, headless sessions);
  ratios within this grid are.
- **One runtime, one model.** The adapter and the observed effort values are specific to Claude
  Code 2.1.263 headless sessions with `claude-sonnet-5`; nothing here transfers to another model
  family or effort scale.
- **`context` digests differed across attempts on (g) and (h)** despite identical packets; the
  fingerprint inputs were assembled differently by different reviewers. It did not affect scoring
  and is recorded for the skill's maintainers.
