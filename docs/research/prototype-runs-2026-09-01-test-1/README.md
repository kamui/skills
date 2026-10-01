# Review experiment data

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

**2026-09-01.** Raw outputs and metadata from running four code-review prototypes against one
pull request under controlled conditions. **Data only** — the analysis of this run lives in
[`evaluation.md`](evaluation.md).

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

- Each run got its own clone at the same head, with `main` pinned to the base SHA, so no run could
  disturb another's working tree.
- Phase 1 (target resolution) was done once by the orchestrator and handed to every run identically:
  same run identity, same manifest, same issue text, same "no prior review state".
- V2-v4 were not allowed to publish during comparison. V4 was selected and published only after
  those three runs finished. V5 ran later with publication disabled and controlled prior-review
  state `none`, so the existing live v4 review could not influence its first-review result.
- Each prototype's own reference documents were treated as authoritative and its phase structure
  followed as written, including its own fan-out and verification policy.
- **Harness and model:** every run (orchestrator and all sub-agents) used **Claude Opus 5 (1M
  context)** at the **High** reasoning setting, driven by the **Claude Code** CLI harness. Sub-agents
  were spawned with Claude Code's `Agent` tool (general-purpose agents); the orchestrator handed each
  skill's reference files and the phase-1 brief to the reviewer as paths it read itself.
- Sub-agent token counts, tool-use counts, and wall-clock spans are as reported by that harness for
  all four runs, so the cost columns are directly comparable. Orchestrator tokens are not included.
  A verifier's tokens and tool calls are reported separately from its primary's rather than folded
  into them.

## What differs between the runs

Only the skill under test:

| | v3 (PR #13) | v4 (PR #16) | v5 (PR #17) |
| --- | --- | --- | --- |
| Architecture | 1 integrated reviewer, self-falsification | 1 integrated reviewer + conditional fresh-context verifier | 1 integrated reviewer + consequence-triggered fresh-context verifier |
| Verification | only for high-risk/large/coupled changes | mandatory for `must-fix`, security, data-loss, contract changes | mandatory for `must-fix` and enumerated consequential risks; artifact names alone do not trigger |

## Files

- `v3-run.md` — output and metadata
- `v4-run.md` — output and metadata
- `v5-run.md` — output and metadata
- `comparison-data.md` — side-by-side metadata table, extended after the v5 run
- `evaluation.md` — the analysis of this run

## Reproducing

The pinned inputs and run files permit a replay against the same head. Because v4 is now published
live, a controlled replay must use the recorded `none` prior-review state rather than reading current
PR review state; publication should remain disabled unless the test explicitly evaluates re-review.
