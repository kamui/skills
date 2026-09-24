# Review report

Status **Changes Requested**; coverage `complete`. `render_review.py` generated this report from the validated composition. The summary body below is the one the payload carries.

**Changes Requested (advisory)** — 2 must-fix findings.

**Intent:** Add inclusive date bounds to account statements, with an opening balance, filtered rows, a closing balance, invalid-date errors, and README guidance.

**Issue fit:** Issue alignment was unavailable; the supplied statement-date-filter spec is the intent source. Criteria 3 and 5 are partial: a filtered row can carry an excluded credit, and the CLI accepts date spellings outside YYYY-MM-DD. The other four criteria are met in the inspected scope. Source: user-supplied spec; commit messages in the range.

**Coverage:** Reviewed all four changed files in the complete pinned merge-base diff, relevant account and statement callers, base repository guidance, and each new test's setup, call, assertions, and cleanup. Accepted the supplied clean-head 17-test suite and two CLI error exercises. A reviewer focused check at the same head reproduced both defects; its first invocation lacked PYTHONPATH and was rerun with the repository on the path. The fresh verifier confirmed both findings and ran the three changed tests successfully. No source or forge changes were made.

**Reviewed:** Range `2301c83ee0b2ba0248fe3d2d1f6cd481963545ab...2ba40465ef91f15b2963a4b12e80f46ee0e9efae`: `2ba4046` against merge-base `2301c83`.

## Findings

- [P2] [must-fix] Exclude out-of-range entries from displayed running balances — anchor `ledger/statement.py:39-40`
- [P2] [must-fix] Reject dates outside the documented YYYY-MM-DD format — anchor `ledger/cli.py:28`

<!-- review-run head=2ba40465ef91f15b2963a4b12e80f46ee0e9efae base-ref=main base-sha=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab merge-base=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab workflow=v5b-25 packet_context=none supplied_inputs=yes issues=none coverage=complete -->

## Run

Head, base, merge-base, workflow, packet identity, issues and coverage are in the run trailer above.

- Repository: `/home/jack/.cache/rc357x/root/implementation-gate/repo`
- Target: range `2301c83ee0b2ba0248fe3d2d1f6cd481963545ab...2ba40465ef91f15b2963a4b12e80f46ee0e9efae`
- Merged: no
- Supplied issues or specs: `ledger-spec/statement-date-filter`

## Line comments

The full body of each line-anchored item the summary indexes.

### `ledger/statement-running-balance-filter`

**[P2] [must-fix] Exclude out-of-range entries from displayed running balances**

**Triggers when:** Post a 100.00 credit dated October 1 before a 50.00 credit dated September 2, then request September 1 through September 30. Posting has no date-order guard.

**Impact:** The September row shows 150.00 while the opening balance is 0.00 and the closing balance is 50.00. The row therefore includes a credit excluded from the requested range.

**Change:** Start the accumulator at the balance before --since, when supplied, and add each entry only after confirming that its date is inside the range. Preserve posting order for displayed rows.

**Source:** Supplied statement-date-filter spec, criterion 3.

<!-- finding id=ledger/statement-running-balance-filter head=2ba40465ef91f15b2963a4b12e80f46ee0e9efae priority=P2 action=must-fix blocking=true kind=bug -->

### `ledger/cli-strict-date-format`

**[P2] [must-fix] Reject dates outside the documented YYYY-MM-DD format**

**Triggers when:** Run statement against a valid ledger with --since 20260901 or --since 2026-W36-2 on Python 3.14; the shared parser also handles --until.

**Impact:** Both commands return 0 with no stderr, although the spec requires status 2 and an error message for invalid option dates.

**Change:** Check the exact YYYY-MM-DD spelling before calling date.fromisoformat for either bound.

**Source:** Supplied statement-date-filter spec, criteria 1 and 5.

<!-- finding id=ledger/cli-strict-date-format head=2ba40465ef91f15b2963a4b12e80f46ee0e9efae priority=P2 action=must-fix blocking=true kind=requirement -->

## Requirements

- `spec-ledger-spec/statement-date-filter/1` (acceptance): met. ledger/cli.py:40-41 registers both optional date arguments; tests/test_filter.py:23-25 and README.md:7 cover inclusion.
- `spec-ledger-spec/statement-date-filter/2` (acceptance): met. ledger/statement.py:17-19,48-49 sums all earlier dated entries and places opening balance after the heading.
- `spec-ledger-spec/statement-date-filter/3` (acceptance): partial. ledger/statement.py:36-41 adds an excluded entry before filtering it; focused-check-output.txt:4-8 shows 150.00 for a 50.00 in-range credit.
- `spec-ledger-spec/statement-date-filter/4` (acceptance): met. ledger/statement.py:22-24,52-53 sums through --until, or uses all entries when absent.
- `spec-ledger-spec/statement-date-filter/5` (acceptance): partial. ledger/cli.py:28 accepts compact and week dates; focused-check-output.txt:9-10 shows status 0 without stderr. Supplied criterion-5.txt confirms status 2 for malformed month and reversed bounds.
- `spec-ledger-spec/statement-date-filter/6` (acceptance): met. README.md:7,12 documents both optional inclusive bounds.

## File coverage

- `README.md`: reviewed
- `ledger/cli.py`: reviewed
- `ledger/statement.py`: reviewed
- `tests/test_filter.py`: reviewed

## Check evidence

- `python3 -m unittest discover -s tests -v` at `2ba40465ef91f15b2963a4b12e80f46ee0e9efae`: accepted, Caller-supplied clean-head Python 3.14.7 run completed: 17 tests, none skipped, exit 0; inputs/unittest-head.txt read.
- `python3 -m ledger.cli statement /dev/null 1001 --since 2026-13-01` at `2ba40465ef91f15b2963a4b12e80f46ee0e9efae`: accepted, Caller-supplied criterion-5.txt shows exit 2 and argparse stderr for an invalid month; it does not exercise alternate ISO spellings.
- `python3 -m ledger.cli statement /dev/null 1001 --since 2026-09-03 --until 2026-09-01` at `2ba40465ef91f15b2963a4b12e80f46ee0e9efae`: accepted, Caller-supplied criterion-5.txt shows exit 2 and stderr for reversed bounds.
- `python3 -B work/review/focused_checks.py` at `2ba40465ef91f15b2963a4b12e80f46ee0e9efae`: reviewer-executed, Wrapped focused repro at the head exited 0 and produced both defect examples in focused-check-output.txt; the prior attempt failed to import ledger because PYTHONPATH was absent.

## Verification

- Allowance: initial batch spent, follow-up unspent.
- Batch `initial` (initial), `Fresh foreground codex exec -m gpt-6-sol -c model_reasoning_effort=high, awaited to completion`: bundle `/home/jack/.cache/rc357x/root/implementation-gate/work/review/initial`, raw return `/home/jack/.cache/rc357x/root/implementation-gate/work/review/initial/worker-last-message.md`, accounting `/home/jack/.cache/rc357x/root/implementation-gate/work/review/initial/accounting.json`.
- Candidate `ledger/statement-running-balance-filter`, trigger `must-fix`, batch `initial`: confirmed.
- Candidate `ledger/cli-strict-date-format`, trigger `must-fix`, batch `initial`: confirmed.

## Routed

- Unresolved: none.
- Disputed: none.

## Artifacts

- record: `/home/jack/.cache/rc357x/root/implementation-gate/work/review/record.json`
- payload: `/home/jack/.cache/rc357x/root/implementation-gate/work/review/payload.json`
- batch: `/home/jack/.cache/rc357x/root/implementation-gate/work/review/batch.json`
- composition: `/home/jack/.cache/rc357x/root/implementation-gate/work/review/composition.json`
- private_dir: `/home/jack/.cache/rc357x/root/implementation-gate/work/review`
- store: `/home/jack/.cache/rc357x/root/implementation-gate/work/review/review-context.json`
- skill_root: `/home/jack/.cache/rc357x/skill`
