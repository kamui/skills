# Review: date-filter (2301c83...2ba4046), profile implementation-gate

**Status: Changes Requested**

Repository `/tmp/rcs-savings/control/implementation-gate/repo`; base `main` 2301c83ee0b2ba0248fe3d2d1f6cd481963545ab, head 2ba40465ef91f15b2963a4b12e80f46ee0e9efae (branch `date-filter`). Spec `ledger-spec/statement-date-filter`; no issue. Context digest `09d4e3a93ddd09132bfd9f2a2fbd02122e19a8e2fb4003442be82bc1b33ddd3a`; workflow v5b-24.

## Summary
- Intent: add inclusive `--since`/`--until` to `ledger statement`, with opening/closing balances, validation and README docs.
- Issue fit: criteria 1, 2, 4, 5, 6 met; criterion 3 partial (see finding).
- Coverage: complete. All four changed files reviewed (README.md, ledger/cli.py, ledger/statement.py, tests/test_filter.py). Supplied evidence accepted at the head on a clean tree: 17 unit tests pass; both criterion-5 CLI cases exit 2 with a stderr message. I reproduced the finding on a disposable out-of-order file. Verification: one batch, one candidate, confirmed; the follow-up allowance is unspent. No questions, no observations, nothing outstanding.

## Findings
### ledger/statement/running-balance-not-from-opening — Start row running balances from the opening balance (P2, must-fix, requirement)
- Anchor: `ledger/statement.py:33-41` (RIGHT). Source: spec criterion 3.
- Triggers when: `--since` is given for an account whose entries are not in date order (`Ledger.post` and the JSON loader accept any day), e.g. `[2026-09-05 +5000, 2026-08-01 +1000, 2026-09-10 -200]` with `--since 2026-09-01`.
- Impact: `Opening balance: 10.00` is followed by a first row with running balance 50.00 (should be 60.00), then 58.00 (should be 68.00). The statement contradicts its own opening balance and criterion 3. The added tests use date-ordered data and miss it.
- Change: in `statement_rows`, when `since` is given start `running` at `balance_before(account, since)` and add only in-range entries.
- Verification: confirmed by an independent worker (model sonnet, run_in_background=false).

## Requirements
| Source | Outcome |
| --- | --- |
| criterion-1 | met |
| criterion-2 | met |
| criterion-3 | **partial** |
| criterion-4 | met |
| criterion-5 | met (inputs/criterion-5.txt) |
| criterion-6 | met |
| commit-e16a48c/"Add inclusive --since and --until options with opening and closing balances." | partial (same gap) |

## Check evidence
Both supplied checks were accepted at head 2ba4046 (clean tree, output read): unittest 17 pass (date-ordered data only), and the criterion-5 exercises. No reviewer-run test suite; no missing required evidence.

## Artifacts
- record.json: /tmp/rcs-savings/control/implementation-gate/work/record.json
- addenda: /tmp/rcs-savings/control/implementation-gate/work/addenda
- composition.json: /tmp/rcs-savings/control/implementation-gate/work/composition.json
- store: /tmp/rcs-savings/control/implementation-gate/work/review-context.json
- verifier bundle: /tmp/rcs-savings/control/implementation-gate/work/initial; raw return: .../raw-return.json; accounting: .../accounting.json
- skill root: /tmp/rcs-savings/skills/d8c2dd9/skills/review-code
