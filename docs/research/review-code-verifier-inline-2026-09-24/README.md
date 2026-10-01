# Re-encoded #341 verifier returns, issue #358

[#358](https://github.com/kamui/skills/issues/358) replaces the verifier worker's `manifest_sha256` echo with a `bundle_id` that the builder generates for each bundle and prints in its brief. It also moves the private formats to `verifier-manifest/3` and `verifier-accounting/3`. The current helper refuses the four verifier bundles that [#341](../review-code-artifact-savings-2026-09-22/README.md) archived. This directory holds those returns re-encoded in the new format, so comparisons can keep using them. The originals are unchanged.

## Fixtures

| Fixture | Archived source | Tasks |
| --- | --- | --- |
| [`archive-continuation-initial`](fixtures/archive-continuation-initial/) | [archive continuation seed, initial batch](../review-code-artifact-savings-2026-09-22/archive/tasks/continuation/review/initial/) | 1 candidate, confirmed |
| [`baseline-publishable-initial`](fixtures/baseline-publishable-initial/) | [publishable cell, initial batch](../review-code-artifact-savings-2026-09-22/baseline/publishable/work/private/verify-initial/) | 1 candidate, confirmed |
| [`baseline-required-verification-initial`](fixtures/baseline-required-verification-initial/) | [required-verification cell, initial batch](../review-code-artifact-savings-2026-09-22/baseline/required-verification/work/private/bundle-initial/) | 2 candidates, confirmed |
| [`baseline-continuation-follow-up`](fixtures/baseline-continuation-follow-up/) | [continuation cell, follow-up batch](../review-code-artifact-savings-2026-09-22/baseline/continuation/work/followup/) | 2 safety premises, both `holds` |

Each fixture has a `bundle/` that this change's builder produced from the archived projected `input.json`. It has a fresh `bundle_id` and a brief carrying the current worker instructions. `raw-return.json` is the archived return with its `manifest_sha256` key replaced, in place, by that ID. No other key or value changes. The archived continuation seed is a template, so its `@TASK_ROOT@` is realized as `/tmp/rcs-savings/baseline/continuation`, the root the #341 baseline continuation cell used.

These are comparison inputs, not new verifier runs. The judgments answered the archived briefs, and pairing them with rebuilt bundles does not authorize a live return in the old format.

## Check

```sh
python3 docs/research/review-code-verifier-inline-2026-09-24/reencode_returns.py check
```

[`reencode_returns.py`](reencode_returns.py) `check` accounts each re-encoded return with the current `account_verifier_return.py`, working in a scratch copy of each bundle. For every fixture it found the following, and exited 0:

- the report's structural result, violations and accounted and withheld IDs equal the archived `accounting.json`;
- the accounted return equals the archived one once the identity key is set aside, so judgments and evidence are unchanged;
- the rebuilt bundle's projected input equals the archived input;
- the archived `verifier-manifest/2` bundle, accounted with its original return, is refused with exit 1 and no report.

`write` produced the fixtures, and it refuses to replace them. A rerun of `write` into an empty `fixtures/` would generate new bundle IDs, because every build gets its own.
