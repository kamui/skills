# Prototype run data — v2, v3, v4, v5 against `kamui/shortlist#66`

**2026-09-01.** Raw outputs and metadata from running four code-review prototypes against one
pull request under controlled conditions. **Data only — no analysis.** Analysis is a separate pass.

## The target

[`kamui/shortlist#66`](https://github.com/kamui/shortlist/pull/66) — "Seed category profiles into the
ledger and generalize Volatile-claim freshness". Author `kamui`, open, not draft.

Run identity, pinned once and given identically to all four runs:

| | |
| --- | --- |
| head | `4349ff41ff4d134e09017662dd30420b80e8eb30` |
| base ref | `main` |
| base SHA | `ccd1842d742fd940b2afde4f903c7bdcb3a707eb` |
| merge-base | `ccd1842d742fd940b2afde4f903c7bdcb3a707eb` |
| diff | 9 files, +160/−6, one commit `4349ff4` |
| originating issue | [#45](https://github.com/kamui/shortlist/issues/45), 10 acceptance criteria, 0 comments |
| prior review state | **none** — no reviews, no comments. Every run is a first review. |
| posting identity | `kamui`, who authored the PR → self-review, `COMMENT` event only |

Changed-file manifest:

```
M CONTEXT.md
M skills/shortlist/references/narrowing-protocol.md
M skills/shortlist/references/record-schemas.md
M skills/shortlist/references/research-protocol.md
M skills/shortlist/scripts/record_schemas.py
M skills/shortlist/scripts/validate-completion.py
M tests/fixtures/generalized-bundle-physical/ledger.md
A tests/fixtures/generalized-bundle-streaming/ledger.md
M tests/test_generalized_bundle.py
```

## Conditions held constant

- Each run got its own clone (`/tmp/run-v2`, `/tmp/run-v3`, `/tmp/run-v4`, `/tmp/run-v5`) at the same head, with
  `main` pinned to the base SHA, so no run could disturb another's working tree.
- Phase 1 (target resolution) was done once by the orchestrator and handed to every run identically:
  same run identity, same manifest, same issue text, same "no prior review state".
- V2-v4 were not allowed to publish during comparison. V4 was selected and published only after
  those three runs finished. V5 ran later with publication disabled and controlled prior-review
  state `none`, so the existing live v4 review could not influence its first-review result.
- Each prototype's own reference documents were treated as authoritative and its phase structure
  followed as written, including its own fan-out and verification policy.
- Sub-agent token counts are as reported by the harness for v2-v4. The v5 harness did not expose
  token or end-to-end wall-time totals; v5 reported 41 total tool calls. Orchestrator
  tokens are not included.

## What differs between the runs

Only the skill under test:

| | v2 (PR #14) | v3 (PR #13) | v4 (PR #16) | v5 (PR #17) |
| --- | --- | --- | --- | --- |
| Architecture | 2 axis finders in parallel + mandatory fresh-context verifier | 1 integrated reviewer, self-falsification | 1 integrated reviewer + conditional fresh-context verifier | 1 integrated reviewer + consequence-triggered fresh-context verifier |
| Verification | always | only for high-risk/large/coupled changes | mandatory for `must-fix`, security, data-loss, contract changes | mandatory for `must-fix` and enumerated consequential risks; artifact names alone do not trigger |

## Files

- `v2-run.md` — output and metadata
- `v3-run.md` — output and metadata
- `v4-run.md` — output and metadata
- `v5-run.md` — output and metadata, including the pre-run forward-test correction
- `comparison-data.md` — side-by-side metadata table, extended after the v5 run

## Reproducing

The pinned inputs and run files permit a replay against the same head. Because v4 is now published
live, a controlled replay must use the recorded `none` prior-review state rather than reading current
PR review state; publication should remain disabled unless the test explicitly evaluates re-review.
