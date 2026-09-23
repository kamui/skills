# Derived finalization metadata, issue #343

[#343](https://github.com/kamui/skills/issues/343) has `finalize_review.py` fill the mechanical fields that a saved input already owns, instead of the model copying them into `composition.json`. This note records the offline check the issue requires before merge: the new finalizer replayed on [#341's archived baseline cells](../review-code-artifact-savings-2026-09-22/README.md), with and without the fields the baseline model transcribed. No model ran, and the workflow stays `v5b-24`.

## Method

[`demo.py`](demo.py) materializes the #341 archive into a temporary root with `savings_archive.py`, then copies each baseline cell's private directory into its task. It rewrites two prefixes, the realization root and the baseline's installed skill root, in `composition.json` and in each accounting report's `raw_return`. Bundle manifests stay byte for byte, so each report's `manifest_sha256` still pairs with its bundle. Each cell is finalized in its own repository, with its packet on a pull request and a saved fingerprint input. The gate cell's input is the `fingerprint-input.json` its model wrote. The pull-request cells get `{"specs": []}`, because their reviews had no spec. Each cell is finalized twice:

- **transcribed**: the composition exactly as the baseline model wrote it. Derivation accepts an explicit field only when it equals the value its saved input owns, so this arm checks every copy, the context digest included.
- **derived**: the same composition with every field the finalizer now derives removed. That is run identity, the record's own paths, and each batch's name, phase and raw return.

[`demo.json`](demo.json) holds the rows.

```sh
python3 docs/research/review-code-metadata-derivation-2026-09-23/demo.py --output docs/research/review-code-metadata-derivation-2026-09-23/demo.json
```

## Result

| Cell | Transcribed | Derived | Public bytes against baseline | Digest against baseline | Mechanical leaves removed |
| --- | --- | --- | --- | --- | ---: |
| publishable | exit 0 | exit 0 | `payload.json`, `batch.json`, `fragments.md` identical in both arms | equal | 16 of 85 |
| implementation-gate | exit 0 | exit 0 | `record.json` identical apart from `finalization`, in both arms | equal | 13 of 97 |
| required-verification | refused at `accounting` | refused at `accounting` | none produced | derive passed, so equal | 8 of 46 |

In both cells that finalize, the two arms produce identical public bytes, and both match the committed baseline. The pull-request cell drops the head, merge-base, base ref and SHA, merged state, repository URL, issues, target kind, digest, four record paths, and its batch's name, phase and raw return. The gate cell drops its run identity, target, commit messages, spec identity, digest and five record paths. #341 counted 30 and 34 mechanical leaves in these compositions. Most of the rest are file paths (a file's state is a judgment, so its row stays), task rulings and allowance flags (the accounting reports check them, and the issue keeps confirmation out of structural accounting), and fields no saved input owns: a range's target kind and base, the repository, and supplied evidence and spec paths. The required-verification composition has no `record`, which #342 made a precondition. It still cannot finalize, but its derive stage passed in both arms: its eight run-identity leaves derive, and its transcribed digest equals the recomputed one.

The procedure also drops a step. A first review no longer runs `context_fingerprint.py`: it saves the input file and names it to the finalizer. A re-review still runs it once, before the duplicate-review shortcut, and the finalizer rejects that digest if the saved inputs change. The baseline cells made 2, 4 and 4 Bash calls naming `context_fingerprint.py`, counting help and example loads. The gate cell also read its source twice. The input shape still comes from `context_fingerprint.py --example`, so this counts fewer required commands, not fewer loads.

## Limits

These are replays of three saved compositions, not usage measurements. They show that fields a saved input owns no longer need transcribing and that the output is unchanged. They show no turn, token, cost or latency effect, and make no recall claim; #347 runs the paired measurement. A model could still copy a derived field. The finalizer then checks the copy against its source, which is stricter than before, when only `head` and `merge_base` were checked against the store. The continuation cell is out of scope because it writes an addendum; #345 owns that.
