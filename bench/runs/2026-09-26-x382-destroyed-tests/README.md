# Run 2026-09-26-x382-destroyed-tests: #382 alone on frozen A

The [#389 preregistration](../../../docs/research/builtin-review-benchmark-2026-09-24/README.md#13-preregistered-follow-up-isolated-a-changes-2026-09-25)
row for [#382](https://github.com/kamui/skills/issues/382): arm A (`review-code` on Sonnet 5 at
`high`) with the destroyed-test-protection bullet added to the frozen A tree and nothing else, on
k, j, l, m and q, three replicates each, 15 planned cells. The maintainer chose the
coverage-inclusive policy on 2026-09-26 and approved the billed runs and the acceptance-path check
the same day, against the issue's $10.62 review-only estimate.

**Frozen 2026-09-26.** `manifest.json` carries `frozen_at`; `freeze_commit` names the commit that
introduced it. After the first dispatch, the manifest changes only by an appended deviation. That
commit was never pushed. The branch carries a rebased copy, `acc2bb0`, committed after the runs,
with the same manifest blob, as the manifest's deviations record.

## Pins

| What | Pinned as |
| --- | --- |
| Control | arm A's original two valid replicates per target in [`2026-09-24-builtin-baseline`](../2026-09-24-builtin-baseline/README.md), scored by `results.v3.json`; tree `c3c53da5381dace16876b0f5b7abe4bccc6bc58b`. No baseline rerun. |
| Candidate tree | `8af0e1af8868e5e46f825acd76a3c8ce9740e0e3` = the control tree with `candidate.patch` applied (local ref `refs/bench/x382-candidate-tree`) |
| Patch | `candidate.patch`, SHA-256 `b2219ebbb92decfae0370371d49ff9489e43d620d4d122371e477c91b9eb415e`: #382's bullet verbatim after the ineffective-test bullet in `references/rubric.md`, 221 bytes and 37 words |
| Arm | `bench/arms/review-code-sonnet-high.json`, SHA-256 `b1e566c1…` (unchanged); `mode: one-shot`, `profile: publishable`, `return_format: artifacts`; Sonnet 5 at `high` for the primary and every worker |
| Claude Code | `2.1.282`, the control's version, through `~/.t3/bench-runs/2026-09-26-x382-destroyed-tests/bin/claude` |
| Cohort | the control manifest's packet, diff and provisioning hashes; registers v2 for (j), v1 elsewhere, as `results.v3.json` uses |
| Order | replicate 1 across k, j, l, m, q, then replicate 2, then 3 |
| Caps | 17 attempts, 2 replacements, $40 including grading and adjudication, $5 per attempt, $5 grading reserve |
| Rates, method, rubric, metric code | Sonnet 5 and Opus 5.5 `as_of 2026-09-24`; `bf3c25f5…`, scoring v1, `8073b48c…` |

## Decision rule

**Pass** only if all of these hold at the fixed stopping point:

- GT-k1 is recovered with a sufficient remedy and `must-fix` in 3/3, and GraphQL approvals are 0/3.
- The adjudicated non-material tRPC assertion and Bokeh timezone coverage are not promoted.
- (k) and (l) recall stay 3/3.
- (m) and (q) have zero false findings, and no target gains a false finding or non-material blocker.
- Correct action, sufficient remedy and validity do not get worse on comparable recoveries.

**Reject** on a measured failure. **Inconclusive** if the cap or missing valid cells prevents a verdict.
A miss is never replaced, and no threshold changes after results.

The acceptance-path check (a GraphQL packet whose description explicitly accepts losing the
no-stack coverage) is a diagnostic outside the planned cells and outside this decision.

## Results (2026-09-26)

**Disposition: inconclusive by the frozen rule, unless the validity drop counts as a measured
failure.** Every measured threshold holds, and the recall, false-finding, action and remedy guardrails
hold over valid reviews. Validity among (l)'s recoveries fell from frozen A's 2/2 to 3/4, because
att-013 recovered GT-l1 but was harness-invalid. The rule does not say whether a harness failure
counts against validity. If it does, the disposition is reject. That reading is the maintainer's.

(m) finished with 2 of its 3 planned valid reviews. Its third cell was harness-invalid twice: the
first attempt, att-014, and the replacement, att-017, both wrote the review's private directory
under `/tmp`, outside the attempt's roots. The same happened once on (l), att-013, whose
replacement att-016 was valid. That used both replacements and all 17 attempts, and a miss is never
replaced.

The graded invalid (m) reviews agree with the valid ones: both Approved with no false finding.
The bullet does not touch private-directory handling, and frozen A lost att-071 the same way.

`results.v1.json` comes from `score.py`, with mapping v1 on every target. Each target was graded
once, blind, by `grade.py`: Opus 5.5 at `high`, `--safe-mode`, a clean read audit and no new
candidates. "Frozen A" is the control's two valid reviews per target, from `results.v3.json`.

| Target | Candidate valid reviews | Recovery (attempt level) | Native action on the recovery | Fix | Approved on buggy | False findings | Frozen A |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (k) GraphQL | 3, one incomplete | GT-k1 3/3 | `must-fix` P2 3/3 | sufficient 3/3 | 0/3 | 0 | GT-k1 2/2 sufficient, `consider` with priority errors 2/2, approved 2/2 |
| (j) tRPC | 3 | 0/3 | — | — | 3/3 | 0 | 0/2, approved 2/2 |
| (l) Bokeh | 3 | GT-l1 3/3 valid, 3/4 with the invalid att-013 | `must-fix` (P2, P2, P1) | sufficient 3/3 | 0/3 | 0 | GT-l1 2/2 sufficient, approved 0/2 |
| (m) gRPC, clean | 2 of 3 | — | — | — | — | 0 (also 0 on both invalid attempts) | 0 |
| (q) Soba, clean | 3 | — | — | — | — | 0 | 0 |

- **Thresholds:** GT-k1 is recovered with a sufficient remedy and `must-fix` in 3/3, and GraphQL approvals fall from 2/2 to 0/3.
- **Negative cases:** the unasserted tRPC `voidWithMiddleware` fixture stays an observation (att-007) under an Approved verdict. The Bokeh timezone-coverage finding stays `consider` P3 in all four (l) reviews. Neither is promoted.
- **Guardrails:** (k) and (l) recall stay 3/3 over valid reviews. At attempt level, where the invalid att-013 counts as zero, `results.v1.json` gives (l) 0.75 against frozen A's 1.0. No target has a false finding or a non-material blocker. The only `must-fix` items are the GT-k1 and GT-l1 recoveries.
- **Action, fixes and validity:** priority errors fall from 2 to 0, and every recovery is `must-fix` with a sufficient fix. Invalid attempts rose to 3 of 17, from frozen A's 1 of 21 (0 of 10 on these targets); every one is the `/tmp` private directory. On (k), att-006 is valid and graded, but its review reported incomplete coverage because the run allowance permits only mocha and Flow was not run. `results.v1.json` therefore scores that cell `incomplete` and counts 2 completed valid reviews on (k). Under scoring v1 its GT-k1 recovery still counts.
- **Dollars:** $13.97 for 17 reviewer attempts, $0.79 mean per valid review ($0.82 per attempt) against frozen A's $0.71 on these targets. Grading was $1.23 and the two diagnostics $1.37, so the run total is $16.57 against the $40 cap. That is above the issue's $10.62 review-only estimate: the three invalid attempts cost $2.89.
- **Latency:** median elapsed-to-payload over valid reviews is 158 s (14 reviews), against frozen A's 119 s on the same targets (10 reviews). The per-target medians rise most on (j), 99 → 179 s, and (k), 93 → 154 s.

## Acceptance-path diagnostic

The candidate tree reviewed (k) twice more, on the same pins, with section 3's empty
pull-request body replaced. The files are under `diagnostics/`, with the exact `input.md` for each.

| Attempt | Body | Verdict | GT-k1 item | Cost |
| --- | --- | --- | --- | --- |
| att-901 | names the lost no-stack coverage and explicitly accepts losing it | Approved | `consider` P3, marked advisory because the author accepted the loss; the lost protection is still reported | $0.60 |
| att-902 | describes the fixture swap only | Changes Requested | `must-fix` P3 with the stackless-original fix | $0.77 |

Both match #382's expectations. Explicit acceptance of the named loss clears the blocker and keeps
the loss visible, while a description of the swap alone still gets `must-fix`. This is one review
per body, so it shows the path works, not how often it does.
