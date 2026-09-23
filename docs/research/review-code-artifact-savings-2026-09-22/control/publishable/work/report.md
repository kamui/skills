# Review: example/ledger#4 — Add CSV statement export

**Status: Approved (advisory)** — no findings, no questions. Coverage complete.

## Identity
- Repository: https://github.com/example/ledger, PR #4 (open, unmerged, not draft); base ref `main`
- Head `0eb283dfe715341548387bf65af857affedf5dfa`; base and merge-base `2301c83ee0b2ba0248fe3d2d1f6cd481963545ab`
- Mode one-shot, profile publishable, reviewer identity `reviewer`, workflow v5b-24, context `45a2fe742898267c6a52acfad4ff52cb5b988f8eb671321fe4749f479997822f`
- Skill root: /tmp/rcs-savings/skills/d8c2dd9/skills/review-code
- Store: /tmp/rcs-savings/control/publishable/work/store; packet: /tmp/rcs-savings/control/publishable/inputs/packet.json (complete, no gaps, no prior reviews/threads, so first review; gating withheld)

## Summary
**Approved (advisory)** — no findings.

**Intent:** Add `--format csv` to `ledger statement` via a new `ledger/export.py` reusing `statement_rows` (PR body; closes #3).

**Issue fit:** Met — all four acceptance criteria of #3 (csv option with text default, header row, text decimal format, csv.reader round-trip) are implemented.

**Coverage:** All 3 changed files reviewed against the complete merge-base diff. Reviewer-executed full suite at the head in a disposable export: 16 tests, OK. Newline/CR descriptions checked to round-trip through csv.reader. No verification workers were needed: no must-fix, security, data-integrity, or compatibility candidate survived and no safety-premise check applied.

**Reviewed:** `0eb283d` against merge-base `2301c83`.

## Observations

- The round-trip test covers a comma and quotes but not the newline case named in acceptance criterion 4; a manual check shows `csv.writer` quoting handles it. Evidence: `tests/test_export.py:21-23`, `ledger/export.py:16-18`.

<!-- review-run head=0eb283dfe715341548387bf65af857affedf5dfa base-ref=main base-sha=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab merge-base=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab workflow=v5b-24 context=45a2fe742898267c6a52acfad4ff52cb5b988f8eb671321fe4749f479997822f issues=example/ledger#3 coverage=complete -->

## Requirement outcomes
| Source | Outcome | Evidence |
| --- | --- | --- |
| issue-3/acceptance-criterion-1 (`--format csv`, text default) | met | `ledger/cli.py` FORMATS, `--format` choices, default "text" |
| issue-3/acceptance-criterion-2 (header row) | met | `ledger/export.py` HEADER; test_header_and_rows |
| issue-3/acceptance-criterion-3 (decimal format) | met | rows come from `statement_rows`/`format_cents` |
| issue-3/acceptance-criterion-4 (round-trip) | met | csv.writer quoting; test covers comma/quotes; newline/CR checked manually |
| pr-body/"reuses `statement_rows`" | met | `ledger/export.py` |

## Per-file coverage
- `ledger/cli.py`: reviewed
- `ledger/export.py`: reviewed
- `tests/test_export.py`: reviewed (assertions observe the claimed behavior; setup sound)

Repository rules (base AGENTS.md): integer cents kept (formatting reuses existing helper), docstring names errors ("Raises nothing"), auth/account-state rules untouched.

## Check evidence
- Reviewer-executed at head, disposable git-archive export: `python3 -m unittest discover -s tests -v`, 16 tests OK (timing in /tmp/rcs-savings/control/publishable/work/run-events.jsonl). No CI or supplied check evidence in the packet.

## Verification
No workers spawned; none mandatory (no surviving must-fix, security, data-integrity or compatibility candidate; no safety-premise conclusion required). Batch allowance unused: initial batch 0/1, follow-up 0/1.

## Observations
- The round-trip test covers a comma and quotes but not the newline case in acceptance criterion 4; a manual check shows csv.writer quoting handles it (`tests/test_export.py:21-23`, `ledger/export.py:16-18`).

Dropped without record: none published. Unrecoverable inputs / ambiguities: none.

## Artifacts
- /tmp/rcs-savings/control/publishable/work/composition.json, payload.json, batch.json, fragments.md, context.out, fingerprint.out, run-events.jsonl, store
