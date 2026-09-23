# Continuation chain helper, issue #345

[#345](https://github.com/kamui/skills/issues/345) adds `skills/review-code/scripts/continue_review.py`. It loads and validates an implementation-gate record's version-2 continuation chain, and composes the next addendum from the continuation's authored decisions. Before this, the addendum was hand-written under a prose contract and nothing validated it. This note records the offline replay the issue asks for: #341's continuation cell run through the helper. No model ran, and the workflow stays `v5b-24`.

## Method

[`demo.py`](demo.py) runs two arms. Each materializes the [#341 archive](../review-code-artifact-savings-2026-09-22/README.md)'s `continuation` task into its own temporary root with `savings_archive.py`. It then copies the baseline cell's follow-up verifier bundle into the task, rewriting only the realization-root prefix of the accounting report's `raw_return`, so the bundle manifest and its hash stay byte for byte. Next it builds the continuation store with `review_context.py --prior-head 03ce7cd`, and runs `continue_review.py compose` on an input taken from the addendum the baseline model wrote by hand:

- **transcribed**: that addendum exactly as written. The helper accepts an explicit field only when it equals the value the chain, store, bundle or accounting report owns, so this arm checks every copy.
- **derived**: the same addendum without the fields the helper now derives. Those are `format`, `workflow`, `record`, `record_format`, `reviewed_head`, `final_head`, `replaced_by_full_review`, `routed`, `verification.allowance`, `verification.outstanding`, and each batch's `name`, `phase` and `raw_return`.

[`demo.json`](demo.json) holds the rows.

```sh
python3 docs/research/review-code-continuation-composer-2026-09-23/demo.py --output docs/research/review-code-continuation-composer-2026-09-23/demo.json
```

## Result

| Arm | Exit | Authored leaves | #341 inventory: mechanical / judgment | Saved addendum against the baseline | Chain afterwards |
| --- | --- | ---: | --- | --- | --- |
| transcribed | 0 | 57 | 22 / 35 | identical, less `finalization` | `Approved`, complete, head `b96a362` |
| derived | 0 | 40 | 10 / 30 | identical, less `finalization` | `Approved`, complete, head `b96a362` |

Both arms save the same bytes, and those bytes equal the addendum the baseline model wrote, once `finalization` is removed and the realization root is restored. The derived input drops 17 of 57 leaves. Under #341's own inventory ([`interface_metrics.py fields`](../tools/interface_metrics.py)), the mechanical leaves fall from 22 to 10. The 10 that remain name the reviewer's own decisions or artifacts: two delta paths that key file states, one check-evidence head, the bundle, accounting and operation of the batch, and each task's batch name and ruling, which the accounting report checks. Five further leaves the inventory counted as judgment, `routed`, `outstanding` and `replaced_by_full_review`, now default to the chain's carried state. Writing them is still allowed, but a dropped entry is refused.

The helper also writes `addendum-b96a362….report.md`, a 5,340-byte complete current result, separate from the record's `report.md`. The baseline model wrote a 5,516-character `report.md` by hand. Establishing the chain's state took the baseline reviewer the record and one addendum (9,622 bytes) plus seven reads of helper source. `state --json` returns the reduced state in 7,378 bytes, including absolute paths under this checkout, and it validates the chain while doing so. These two figures are file sizes, not measured loads.

## Instruction cost

`continuation-addendum.md` grows 194 bytes, from 6,291 to 6,485, and `implement-publish`'s `continuation.md` grows 609 bytes, from 2,836 to 3,445. A reviewer that runs `--example` also reads 1,596 bytes of example input. The runtime total is 91,790 of 92,000 bytes, and no limit rises. This is reliability work: the chain was unvalidated before, and it is now checked on every read and write. It lands with explicit overhead and no claim of savings.

## Limits

This is a replay of one saved addendum, not a usage measurement. It shows that the fields a saved input owns no longer need transcribing, and that the output is unchanged. It shows no turn, token, cost or latency effect, and makes no recall claim; #347 runs the paired measurement. The seeded chain predates #342's finalization protocol, so it also exercises the pre-report reading path: the record and first addendum have no `finalization`, and the new addendum does. `test_continue_review.py` covers the remaining cases the issue lists: forks, cycles, replacements, interrupted writes, dropped state and version-1 routing.
