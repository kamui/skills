# Unseen-target comparison of verification-off

Part of [#409](https://github.com/kamui/skills/issues/409). Refs
[#380](https://github.com/kamui/skills/issues/380). The [staged run](../2026-09-28-verification-off-staged/README.md)
passed the variant that removes `review-code`'s independent verification phase on five exposed
targets. #380 requires one more check before adoption: the same comparison on at least two unseen
targets, one buggy and one clean, with three replicates per arm. This run is that check.

The maintainer approved this comparison and its **$60 cap** on 2026-09-28, and chose the decision
rule below before any target was chosen.

## Frozen inputs

- Control skill tree: `5e12864b52b6c0c52b9b1b1f41d5b22fa2576676`, arm
  `review-code-sonnet-high-enforced-x394-control`, as in the staged run.
- Variant skill tree: `59e7df1b15096ccb029b35df78bbc54311795650`, arm
  `review-code-sonnet-high-enforced-verification-off`, as in the staged run. The difference is the
  staged run's [candidate patch](../2026-09-28-verification-off-staged/candidate.patch).
- Both arm files are unchanged since the staged run. Primary reviewer and any worker are
  `claude-sonnet-5` at high effort.
- Claude Code **2.1.284**, a byte copy at `~/.t3/bench-cache/cli/2.1.284`, SHA-256
  `5cd90aabd83f8a15136c35aa37bb1d92b348993573316643dc3fe4e04afbf88f`.
- Isolation profile `claude-strict-v2`, `mode: one-shot`, `profile: publishable`,
  `return_format: artifacts`, and the staged run's execution policy text.
- Rubric v1, the original method revision, and the grader template the staged run used.

Reviewers receive the factual packet, the source diff, the execution policy and one skill tree.
They receive no issue text, register, grade or earlier output.

## Departures

| From | Departure | Why |
| --- | --- | --- |
| #380 | The control is tree `5e12864`, not frozen A `c3c53da` | The variant was cut from `5e12864`. A control at `c3c53da` would test the removal and every change between the two trees at once |
| #380 | The decision rule below replaces "candidate recall does not fall and the clean target has 0 false findings" | At three replicates the literal rule rejects a variant with no effect 27–54% of the time, so its verdict carries little information either way. The maintainer chose the matched rule on 2026-09-28. The literal conditions are still reported |
| Staged run | Claude Code 2.1.284, not 2.1.282 | The updater deleted 2.1.282. Both arms run on the same pin, so the pair stays matched, but these cells do not pool with the staged run's |

## Targets

| Order | Target | Pull request | Truth | Shape | Changed | Merged |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | [`t-rclone-9699`](../../targets/t-rclone-9699/) | rclone/rclone#9699, "lib/batcher: prevent commits racing shutdown" | clean | clean, high risk (concurrency) | 95 lines in 2 Go files, 6 of them production code | 2026-08-01 |
| 2 | [`s-seaweedfs-10735`](../../targets/s-seaweedfs-10735/) | seaweedfs/seaweedfs#10735, "fix(redis2): remove orphaned directory index members on listing" | buggy, 1 registered defect | data loss in a persistence layer | 160 lines in 2 Go files, 17 of them production code | 2026-08-13 |

Both merged after 2026-07-01, and the clean target's cleanliness window runs 58 days to 2026-09-28.
Both are Go, and the focused tests of each run offline with the clone read-only, as the
[smoke records](../../targets/t-rclone-9699/smoke.json) show. The registers, hunt reports and
rulings stay sealed until every attempt is filed: the [`sealed/`](sealed/) ciphertexts, with
plaintext hashes in `sealed/SHA256SUMS` and each `target.json`.

The clean hunt's first passing candidate was taken over its alternate, rclone#9711, because #9711
carries an intended behaviour change that graders could dispute. The buggy hunt found one passing
candidate. The adjudicator of the buggy target registered one of the defects the hunt proposed and
ruled a second non-material.

Neither target has been reviewed by any arm, and neither pull request is in the
[list of used pull requests](prompts/used-pull-requests.txt) given to the hunts. Each was chosen by
a headless Opus 5.5 hunt from the builtin-review benchmark's
[hunt template](../../../docs/research/builtin-review-benchmark-2026-09-24/prompts/hunt-template.md)
with [this run's slots](prompts/hunt-slots.json), then ruled on by an independent adjudicator from
that benchmark's adjudicator template. Neither session saw any reviewer output. Each register is
sealed with `seal.py` before any dispatch, and `target.json` records the plaintext's hash.

## Cells and order

Twelve cells: both arms, three replicates, on each target. One attempt runs at a time.

The clean target runs first, all six cells, and is graded before the buggy target starts. Within
each target the arm that runs first alternates by replicate: control, variant; variant, control;
control, variant.

## Decision rule

Every rule compares the variant with its control on the same target.

| Outcome | Rule |
| --- | --- |
| Reject | On the buggy target, the variant's registered-defect recoveries, summed over its three reviews, are at least 2 below the control's |
| Reject | On the clean target, the number of the variant's reviews carrying a false finding is at least 2 above the control's |
| Inconclusive | The caps run out before every planned cell has a valid attempt |
| Inconclusive | The control dispatches a verifier batch in fewer than 2 of its 6 reviews, so the run cannot observe the removed part |
| Pass | None of the above |

A false finding is the grader's `false` class under rubric v1. A non-material finding is not
false. A pass is not adoption.

**Early stop.** When the clean target's grading already meets the second reject rule, the buggy
target is not dispatched and the run ends rejected. No other early stop exists.

**Reported beside the verdict, deciding nothing:** #380's literal conditions (the variant's
recoveries at least the control's; zero false findings in the variant's clean reviews); false
findings on the buggy target; in-jurisdiction false or non-material findings, as the staged run
defined them; `must-fix` and sufficient remedies on recovered defects; verdicts; cost and elapsed
time per arm; verifier batches.

### What the rule can detect

[`simulate.py`](simulate.py) computes the rule's outcome rates exactly under swept per-review
rates, since rates on unseen targets are unknown. Rejection rates:

| Scenario | Adopted rule | #380 literal |
| --- | ---: | ---: |
| No effect | 2–23% | 27–54% |
| Variant loses 40% of recoveries | 13–70% | 49–91% |
| Variant loses 70% of recoveries | 17–95% | 58–99% |
| Variant adds 0.33 to the clean false-finding rate | 30–46% | 61–80% |

The spread covers one or two registered defects, a per-review recovery rate from 0.3 to 0.9, and a
control false-finding rate from 1/30 to 1/6. With one buggy and one clean target, the rule catches
a large, systematic loss often and a small one rarely. It is a screen for failure on code the
variant has not seen. The staged run's 15 pairs remain the main evidence on recall.

## Caps

| Cap | Value |
| --- | ---: |
| Planned cells | 12 |
| Replacements for invalid attempts | 2 |
| Maximum attempts | 14 |
| Reserved per attempt | $5 |
| Closeout reserve | $3 |
| Approved ceiling: hunts, adjudication, reviews, grading | **$60** |

Hunts and adjudication are charged in [`charges.jsonl`](charges.jsonl) before the freeze, so
`run_cell.py` counts them against the cap. They cost **$10.46**: hunts $4.55 (buggy) and $2.28 (clean), adjudication
$2.29 and $1.34, each metered from its transcript at the Opus 5.5 rate and equal to the CLI's own
figure. That leaves $46.54 for reviews, grading and replacements after the closeout reserve. Twelve
reviews at the staged run's mean of $2.60 and two gradings come to about $32. Replace an invalid or stopped attempt at once, in filing
order. A valid miss, a false finding or a skill timeout is never replaced. Cells, caps and rules do
not change after an outcome is seen.

## Grading

Grade each target once all its attempts are filed, in one blind Opus 5.5 high session holding every
attempt on it, with the grader template the staged run used. The grader sees no arm, tree, cost,
native action or verdict. An `unresolved` new candidate goes to an independent adjudicator before
the decision. Grading and adjudication count against the cap.

## Launch checklist

1. Commit the targets, the manifest and this protocol. Record that commit as the manifest's freeze
   and metric revision.
2. Run the free native isolation checks and the target smokes on this host with the pinned CLI and
   a local fake API.
3. Set `frozen_at`. Confirm zero claims for this run and charges equal to the setup rows.
4. Check the OAuth login's `expiresAt` covers the next attempt. Unset every `CLAUDE*`,
   `ANTHROPIC*` and `AI_AGENT` variable of the orchestrating session. Set `BENCH_CLAUDE` to the
   pinned executable and put the sandbox tools on `PATH`. Dispatch with `run_cell.py --next`.
5. File and audit each attempt before the next dispatch. Act on a stopping condition at once.
