# Review report

Profile `implementation-gate`; status **Changes Requested**; coverage `complete`. `finalize_review.py` generated this report from the validated composition. The summary body below is the one the payload carries.

**Changes Requested (advisory)** — 1 must-fix finding.

**Intent:** Let `ledger statement` take inclusive `--since`/`--until` bounds, with an opening balance, a running balance that continues from it, a bounded closing balance, exit 2 on bad dates, and README docs (spec ledger-spec/statement-date-filter; commits e16a48c, 2ba4046).

**Issue fit:** Partial. Criteria 1, 2, 4, 5 and 6 are met; criterion 3 is not met when an account's entries are not in date order, which `post()`, `transfer()` and `load()` permit. Source: user-supplied spec; commit messages in the range.

**Coverage:** Complete merge-base diff (4 files) reviewed. Supplied unittest run (17 tests, exit 0) and the criterion-5 CLI exercises were accepted: same head 2ba4046, clean tree. I reproduced the out-of-order case once with a disposable JSON file; a verifier confirmed the finding by trace. No test runs the out-of-order case, so the passing suite says nothing about it. Uncommitted changes: none. Python 3.11+ `date.fromisoformat` also accepts compact forms such as `20260901`, which criterion 5's `YYYY-MM-DD` wording does not address; not raised as a finding.

**Reviewed:** Range `2301c83ee0b2ba0248fe3d2d1f6cd481963545ab...2ba40465ef91f15b2963a4b12e80f46ee0e9efae`: `2ba4046` against merge-base `2301c83`.

## Findings

- [P2] [must-fix] Start the running balance at the opening balance — anchor `ledger/statement.py:34-36`

<!-- review-run head=2ba40465ef91f15b2963a4b12e80f46ee0e9efae base-ref=main base-sha=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab merge-base=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab workflow=v5b-24 context=d86d6199d90e3c13840489b4804e27fa4e58e6830b9d6ded210666ef9d0044ac issues=none coverage=complete -->

## Run

Head, base, merge-base, workflow, context digest, issues and coverage are in the run trailer above.

- Repository: `/tmp/rcs-savings/treatment/implementation-gate/repo`
- Target: range `2301c83ee0b2ba0248fe3d2d1f6cd481963545ab...2ba40465ef91f15b2963a4b12e80f46ee0e9efae`
- Merged: no
- Specs: `ledger-spec/statement-date-filter`

## Line comments

The full body of each line-anchored item the summary indexes.

### `ledger/statement/running-balance-posting-order`

**[P2] [must-fix] Start the running balance at the opening balance**

**Triggers when:** An account whose posting order differs from date order (for example a 2026-09-05 entry posted before a 2026-08-01 entry) is rendered with `--since 2026-09-01`.

**Impact:** The row prints running balance 100.00 beside opening balance 50.00 and amount 100.00 (it should be 150.00, the closing balance), so the statement contradicts criterion 3. Entries dated after `--until` but posted earlier inflate listed rows the same way.

**Change:** In `statement_rows`, initialise `running` to `balance_before(account, since)` when `since` is given (else 0) and add only the amounts of rows that pass the filter.

**Source:** spec-ledger-spec/statement-date-filter/criterion-3

<!-- finding id=ledger/statement/running-balance-posting-order head=2ba40465ef91f15b2963a4b12e80f46ee0e9efae priority=P2 action=must-fix blocking=true kind=requirement -->

## Requirements

- `spec-ledger-spec/statement-date-filter/criterion-1` (acceptance): met. ledger/cli.py:37-38 adds --since/--until parsed by iso_day; statement.py filters inclusively
- `spec-ledger-spec/statement-date-filter/criterion-2` (acceptance): met. ledger/statement.py render_statement emits `Opening balance:` from balance_before (entries < since) right after the heading
- `spec-ledger-spec/statement-date-filter/criterion-3` (acceptance): partial. Listing is correct, but statement_rows:34-41 accumulates running over every entry in posting order, so it diverges from opening balance plus listed rows when entries are not date-ordered; reproduced and verifier-confirmed (ledger/statement/running-balance-posting-order)
- `spec-ledger-spec/statement-date-filter/criterion-4` (acceptance): met. render_statement closing uses balance_through(until) or account.balance() when until is absent
- `spec-ledger-spec/statement-date-filter/criterion-5` (acceptance): met. inputs/criterion-5.txt: invalid date and reversed range both exit 2 with stderr messages; cli.py main check and tests/test_filter.py
- `spec-ledger-spec/statement-date-filter/criterion-6` (acceptance): met. README.md:7 example and lines 11-12 describe both options

## File coverage

- `README.md`: reviewed
- `ledger/cli.py`: reviewed
- `ledger/statement.py`: reviewed
- `tests/test_filter.py`: reviewed

## Check evidence

- `python3 -m unittest discover -s tests -v` at `2ba40465ef91f15b2963a4b12e80f46ee0e9efae`: accepted, exact head, clean tree, 17 tests pass, output read; covers only date-ordered data
- `criterion-5 CLI exercises (invalid --since, reversed range)` at `2ba40465ef91f15b2963a4b12e80f46ee0e9efae`: accepted, exact head, clean tree, both exit 2, output read in criterion-5.txt

## Verification

- Allowance: initial batch spent, follow-up unspent.
- Batch `initial` (initial), `Agent run_in_background=false`: bundle `/tmp/rcs-savings/treatment/implementation-gate/work/initial`, raw return `/tmp/rcs-savings/treatment/implementation-gate/work/initial-return.json`, accounting `/tmp/rcs-savings/treatment/implementation-gate/work/initial/accounting.json`.
- Candidate `ledger/statement/running-balance-posting-order`, trigger `must-fix`, batch `initial`: confirmed.

## Routed

- Unresolved: none.
- Disputed: none.

## Artifacts

- record: `/tmp/rcs-savings/treatment/implementation-gate/work/record.json`
- addenda: `/tmp/rcs-savings/treatment/implementation-gate/work/addenda`
- composition: `/tmp/rcs-savings/treatment/implementation-gate/work/composition.json`
- fingerprint_input: `/tmp/rcs-savings/treatment/implementation-gate/work/fingerprint.json`
- private_dir: `/tmp/rcs-savings/treatment/implementation-gate/work`
- store: `/tmp/rcs-savings/treatment/implementation-gate/work/review-context.json`
- skill_root: `/tmp/rcs-savings/skills/1684cf4/skills/review-code`
- evidence_packet: `/tmp/rcs-savings/treatment/implementation-gate/inputs/evidence.md`
- spec: `/tmp/rcs-savings/treatment/implementation-gate/inputs/spec.md`
