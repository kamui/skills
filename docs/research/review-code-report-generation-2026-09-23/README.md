# Generated review reports, issue #342

[#342](https://github.com/kamui/skills/issues/342) moves the complete review report from model authorship to `finalize_review.py`. This note records the offline check the issue requires before merge: the new finalizer replayed on [#341's archived baseline cells](../review-code-artifact-savings-2026-09-22/README.md). No model ran. The workflow stays `v5b-24`.

## Method

[`demo.py`](demo.py) copies each baseline cell's committed private directory into a temporary directory. It rewrites only the private-directory prefix in `composition.json`, then runs this checkout's finalizer with `--compact` on the saved composition. No composition field is added. Public outputs are compared with the committed baseline bytes after mapping the prefix back; the gate record is compared with its `finalization` removed. [`demo.json`](demo.json) holds the rows. The continuation cell is out of scope because it writes an addendum, which has no finalizer until #345.

```sh
python3 docs/research/review-code-report-generation-2026-09-23/demo.py --output docs/research/review-code-report-generation-2026-09-23/demo.json
```

## Result

| Cell | Finalizer | Public bytes against baseline | Model-authored report, baseline | Generated `report.md` | Return under `artifacts` |
| --- | --- | --- | ---: | ---: | ---: |
| publishable | exit 0 | `payload.json`, `batch.json`, `fragments.md` identical | 10,054 chars | 7,257 chars | 295 chars |
| implementation-gate | exit 0 | `record.json` identical apart from `finalization` | 9,351 chars | 7,071 chars | 263 chars |
| required-verification | refused at `accounting` | none produced | 12,692 chars | none | none |

In both cells that finalize, each item body and the summary body appear exactly once in the generated report. The cells' `composition.json` already carried every accounting section, so they author no extra field. Their hand-written report goes away: the model now returns the finalizer's status and paths, or relays the generated file under `complete`.

The required-verification composition had no `record`, which the earlier composer allowed for a publishable review. Its 12,692-character report gave requirements, file coverage, check evidence and verification only as prose. Under the new precondition the model must author those sections as structured fields, and the finalizer renders them. This is a shift from prose to fields, not a reduction, and it is the stronger precondition's cost.

## Limits

These are character counts over three saved compositions, not usage measurements. They show that report authorship and repeated output leave the post-validation tail. They do not show turn, token, cost or latency effects, and they make no recall claim; #347 runs the paired measurement. The generated report is shorter than the hand-written ones because it drops narration those reports added, such as a restated summary and prose about how the run went. It keeps the run identity, every body, ledger row, routed item and drafted reply. It does not carry the pull request's open state or the reviewer identity, because the composition does not hold them.
