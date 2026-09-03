# v2a / v5a re-test of `redis/redis#15680` — Fable 5.1 run (test 2, 2026-09-02)

**Data only.** This directory holds the 2026-09-02 re-test of the two patched prototypes against
test 2's pinned target. It is kept separate from
[`../prototype-runs-2026-09-01-test-2/`](../prototype-runs-2026-09-01-test-2/) — which holds the
original v2, v3, v4, v5 comparison — for one reason:

**These runs executed on `claude-fable-5-1`, not the Sonnet 5 tier the program intended.** The Sonnet 5 re-run has since been done and lives in [`../prototype-runs-2026-09-01-test-2/`](../prototype-runs-2026-09-01-test-2/) — and it found **nothing**, missing the defect this round found. That makes the data here more load-bearing, not less; see that directory's `addendum-2026-09-03.md` for the comparison. The
dispatches inherited the harness's configured default model instead of setting one explicitly, and
the drift was discovered only after both runs completed, by reading `message.model` out of the
harness's own sub-agent transcripts. The Sonnet 5 re-run now sits beside the original comparison, not here. The data is retained rather than discarded
because the round produced a substantive result that does not depend on the tier:

**Both prototypes independently found a real, verifier-confirmed defect in a change that all four
original prototypes, plus a human `APPROVED` review and a detailed technical LGTM, had called
clean** — `updateShardId()`'s propagation defeating the pull request's own new `shard_changed`
guard at `src/cluster_legacy.c:5428`. They disagreed on the merge consequence: v5a published it
`must-fix` (Changes Requested), v2a `consider` (Approved). Both runs were on the same model, so
that head-to-head comparison stands on its own terms; what does not stand is any comparison of
these columns against the original GLM-5.3-Flash round or against test 1's Sonnet 5 runs.

## Files

- [`v2a-run.md`](v2a-run.md) — `code-review-deep-publish`, two axis finders + mandatory verifier
- [`v5a-run.md`](v5a-run.md) — `code-review-publish-5a`, integrated reviewer + clean-verdict and
  follow-up verifier batches
- [`addendum-2026-09-02.md`](addendum-2026-09-02.md) — run conditions, model verification, packet
  reconstruction, mirror truncation, side-by-side table, finding-level agreement, regression watch

The pinned target, its manifest, and the original four runs' data are in
[`../prototype-runs-2026-09-01-test-2/`](../prototype-runs-2026-09-01-test-2/).
