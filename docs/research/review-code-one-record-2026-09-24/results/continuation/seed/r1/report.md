# Review report

Status **Changes Requested**; coverage `complete`. `render_review.py` generated this report from the validated composition. The summary body below is the one the payload carries.

**Changes Requested (advisory)** — 1 must-fix finding, 1 consider finding.

**Intent:** Add account freezing: a frozen account accepts no new entries until it is unfrozen (spec `ledger-spec/account-freeze`).

**Issue fit:** Partial — freezing, unfreezing, refused postings, and readable balances are implemented; criterion 2's refusal of transfers into and out of a frozen account is not. Source: user-supplied spec; commit messages in the range.

**Coverage:** Complete merge-base diff reviewed (2 files); `Ledger.transfer` and the statement and CLI readers inspected. Reviewer-executed `python3 -m unittest discover -s tests -v` at the head: 17 tests, pass.

**Reviewed:** Range `main...864eea86ab86bf5a3375898bc606933ea20696cc`: `864eea8` against merge-base `2301c83`.

## Findings

- [P1] [must-fix] Refuse transfers that touch a frozen account — anchor `ledger/accounts.py:65-66`; fix `ledger/accounts.py:85`
- [P3] [consider] Name the frozen-account error in the post docstring — anchor `ledger/accounts.py:65-66`; fix `ledger/accounts.py:61`

<!-- review-run head=864eea86ab86bf5a3375898bc606933ea20696cc base-ref=main base-sha=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab merge-base=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab workflow=v5b-25 packet_context=none supplied_inputs=yes issues=none coverage=complete -->

## Run

Head, base, merge-base, workflow, packet identity, issues and coverage are in the run trailer above.

- Repository: `/home/jack/.cache/rc357x/root/continuation/repo`
- Target: range `main...864eea86ab86bf5a3375898bc606933ea20696cc`
- Merged: no
- Supplied issues or specs: `ledger-spec/account-freeze`

## Line comments

The full body of each line-anchored item the summary indexes.

### `accounts/frozen-transfer-bypass`

**[P1] [must-fix] Refuse transfers that touch a frozen account**

**Triggers when:** A transfer names a frozen account as its source or its target.

**Impact:** `Ledger.transfer` appends both entries without reading `frozen`, so the frozen account is debited or credited despite the freeze that spec criterion 2 forbids.

**Change:** In `Ledger.transfer` (`ledger/accounts.py:85`), raise `LedgerError` before appending either entry when the source or target account is frozen.

**Source:** Spec `ledger-spec/account-freeze`, criterion 2.

<!-- finding id=accounts/frozen-transfer-bypass head=864eea86ab86bf5a3375898bc606933ea20696cc priority=P1 action=must-fix blocking=true kind=bug fix=ledger/accounts.py:85 -->

### `accounts/post-docstring-frozen`

**[P3] [consider] Name the frozen-account error in the post docstring**

**Triggers when:** A caller reads `Ledger.post`'s docstring to learn which errors to handle.

**Impact:** The docstring still lists only zero amounts, overdrafts, and unknown accounts, although `post` now raises `LedgerError` for a frozen account.

**Change:** Add the frozen-account case to the `Ledger.post` docstring at `ledger/accounts.py:61`.

**Source:** `AGENTS.md`: every public function's docstring names the errors it raises.

Closing this without action is a correct response.

<!-- finding id=accounts/post-docstring-frozen head=864eea86ab86bf5a3375898bc606933ea20696cc priority=P3 action=consider blocking=false kind=maintainability fix=ledger/accounts.py:61 -->

## Requirements

- `ledger-spec/account-freeze/criterion-1` (acceptance): met. ledger/accounts.py:52-58 sets and clears `frozen` through `self.get`, which raises for an unknown account
- `ledger-spec/account-freeze/criterion-2` (acceptance): partial. ledger/accounts.py:65-66 refuses postings; ledger/accounts.py:83-88 appends transfer entries without a frozen check
- `ledger-spec/account-freeze/criterion-3` (acceptance): met. ledger/accounts.py:65-66 raises before the append at ledger/accounts.py:70; tests/test_freeze.py:15-21
- `ledger-spec/account-freeze/criterion-4` (acceptance): met. ledger/accounts.py:56-58; tests/test_freeze.py:23-27
- `ledger-spec/account-freeze/criterion-5` (acceptance): met. `Account.balance` and `render_statement` never read `frozen`; tests/test_freeze.py:29-31

## File coverage

- `ledger/accounts.py`: reviewed
- `tests/test_freeze.py`: reviewed

## Check evidence

- `python3 -m unittest discover -s tests -v` at `864eea86ab86bf5a3375898bc606933ea20696cc`: reviewer-executed, no caller evidence was supplied; the suite covers the changed ledger rules

## Verification

- Allowance: initial batch spent, follow-up unspent.
- Batch `initial` (initial), `Agent subagent_type=general-purpose model=sonnet run_in_background=false`: bundle `/home/jack/.cache/rc357x/root/continuation/review/initial`, raw return `/home/jack/.cache/rc357x/root/continuation/review/initial/raw-return.json`, accounting `/home/jack/.cache/rc357x/root/continuation/review/initial/accounting.json`.
- Candidate `accounts/frozen-transfer-bypass`, trigger `must-fix`, batch `initial`: confirmed.

## Routed

- Unresolved: none.
- Disputed: none.

## Artifacts

- record: `/home/jack/.cache/rc357x/root/continuation/seed/r1/record.json`
- payload: `/home/jack/.cache/rc357x/root/continuation/seed/r1/payload.json`
- batch: `/home/jack/.cache/rc357x/root/continuation/seed/r1/batch.json`
- composition: `/home/jack/.cache/rc357x/root/continuation/seed/r1/composition.json`
- private_dir: `/home/jack/.cache/rc357x/root/continuation/seed/r1`
- store: `/home/jack/.cache/rc357x/root/continuation/review/review-context-864eea86ab86bf5a3375898bc606933ea20696cc.json`
- skill_root: `/home/jack/.cache/rc357x/skill`
- spec: `/home/jack/.cache/rc357x/root/continuation/inputs/spec.md`
