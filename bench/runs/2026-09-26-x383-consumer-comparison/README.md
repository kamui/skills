# Run 2026-09-26-x383-consumer-comparison: #383 alone on frozen A

The [#389 preregistration](../../../docs/research/builtin-review-benchmark-2026-09-24/README.md#13-preregistered-follow-up-isolated-a-changes-2026-09-25)
row for [#383](https://github.com/kamui/skills/issues/383): arm A (`review-code` on Sonnet 5 at
`high`) with the shared-helper consumer-comparison paragraph added to the frozen A tree and nothing
else, on j, i, p, m and q, three replicates each, 15 planned cells. The maintainer approved the
billed run on 2026-09-26, against the issue's $12.66 review-only estimate.

**Frozen 2026-09-26.** `manifest.json` carries `frozen_at`; `freeze_commit` names the commit that
introduced it. After the first dispatch, the manifest changes only by an appended deviation.

## Pins

| What | Pinned as |
| --- | --- |
| Control | arm A's original two valid replicates per target in [`2026-09-24-builtin-baseline`](../2026-09-24-builtin-baseline/README.md), scored by `results.v3.json`; tree `c3c53da5381dace16876b0f5b7abe4bccc6bc58b`. No baseline rerun. |
| Candidate tree | `207b72c5bc1e7ec5c85ebfe43bfc6c3354df9805` = the control tree with `candidate.patch` applied (local ref `refs/bench/x383-candidate-tree`) |
| Patch | `candidate.patch`, SHA-256 `e982088f4efdd0defe5e597f5937708bb6b09ef22ca9fa290165f94e9576b953`: #383's paragraph verbatim after the ledger-gated trigger paragraph in `references/rubric.md`'s Released compatibility, 256 bytes and 38 words, byte-identical to the paragraph in main's `skills/review-code/references/rubric.md` |
| Arm | `bench/arms/review-code-sonnet-high.json`, SHA-256 `b1e566c1…` (unchanged); `mode: one-shot`, `profile: publishable`, `return_format: artifacts`; Sonnet 5 at `high` for the primary and every worker |
| Claude Code | `2.1.282`, the control's version, through `~/.t3/bench-runs/2026-09-26-x383-consumer-comparison/bin/claude` |
| Cohort | the control manifest's packet, diff and provisioning hashes; registers v2 for (j) and (i), v1 elsewhere, as `results.v3.json` uses |
| Order | replicate 1 across j, i, p, m, q, then replicate 2, then 3 |
| Caps | 17 attempts, 2 replacements, $45 including grading and adjudication, $5 per attempt, $5 grading reserve |
| Rates, method, rubric, metric code | Sonnet 5 and Opus 5.5 `as_of 2026-09-24`; `bf3c25f5…`, scoring v1, `8073b48c…` |

## Decision rule

**Pass** only if all of these hold at the fixed stopping point:

- GT-j1 and GT-j2 are each recovered in at least 2/3.
- Requests recall is at least 2/3, with GT-i1 recovered in 3/3.
- Hono GT-p1 is recovered in 3/3.
- (m) and (q) have zero false findings, and no target gains a false finding or non-material blocker.
- Correct action, sufficient remedy and validity do not get worse on comparable recoveries.
- Historical per-target recall holds: (i) at least 2/3, (p) 3/3.

Hypothetical type differences and pre-existing array behavior on Hono are not defects; the register
rules on them. Input-matrix coverage is diagnostic, not recovery.

**Reject** on a measured failure. **Inconclusive** if the cap or missing valid cells prevents a verdict.
A miss is never replaced, and no threshold changes after results.

Whether each (j) review compared helper inputs inside actual consumer compositions (middleware
pipelines, procedure builders) or only probed isolated helper outputs is recorded as a diagnostic
for #383's acceptance item, outside this decision.
