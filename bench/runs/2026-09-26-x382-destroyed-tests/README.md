# Run 2026-09-26-x382-destroyed-tests: #382 alone on frozen A

The [#389 preregistration](../../../docs/research/builtin-review-benchmark-2026-09-24/README.md#13-preregistered-follow-up-isolated-a-changes-2026-09-25)
row for [#382](https://github.com/kamui/skills/issues/382): arm A (`review-code` on Sonnet 5 at
`high`) with the destroyed-test-protection bullet added to the frozen A tree and nothing else, on
k, j, l, m and q, three replicates each, 15 planned cells. The maintainer chose the
coverage-inclusive policy on 2026-09-26 and approved the billed runs and the acceptance-path check
the same day, against the issue's $10.62 review-only estimate.

**Frozen 2026-09-26.** `manifest.json` carries `frozen_at`; `freeze_commit` names the commit that
introduced it. After the first dispatch, the manifest changes only by an appended deviation.

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
