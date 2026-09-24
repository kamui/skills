# Review report

Status **Changes Requested**; coverage `complete`. `render_review.py` generated this report from the validated composition. The summary body below is the one the payload carries.

**Changes Requested (advisory)** — 1 must-fix finding, 1 consider finding, 2 prior items still open.

**Intent:** Add account freezing: a frozen account accepts no new entries until it is unfrozen (spec `ledger-spec/account-freeze`).

**Issue fit:** Partial — freezing, unfreezing, refused postings and refused transfers out of a frozen account are implemented; criterion 2's refusal of transfers into a frozen account is not. Source: user-supplied spec; commit messages in the range.

**Coverage:** Complete merge-base diff reviewed (2 files), with the fix delta `864eea8..03ce7cd` read in full. Reviewer-executed `python3 -m unittest discover -s tests -v` at the head: 17 tests, pass.

**Reviewed:** Range `main...03ce7cd85d34afda4ae47f06d7958ea906b3fcc1`: `03ce7cd` against merge-base `2301c83`.

## Findings

- [P1] [must-fix] Refuse transfers that touch a frozen account — anchor `ledger/accounts.py:85-86`; fix `ledger/accounts.py:85`
- [P3] [consider] Name the frozen-account error in the post docstring — anchor `ledger/accounts.py:65-66`; fix `ledger/accounts.py:61`

## Prior findings

- `accounts/frozen-transfer-bypass` — still-open: ledger/accounts.py:85-86 at 03ce7cd refuses a frozen source only; a transfer into a frozen account still reaches the credit append at ledger/accounts.py:90
- `accounts/post-docstring-frozen` — still-open: ledger/accounts.py:61 at 03ce7cd still lists no frozen-account error in the post docstring

<!-- review-run head=03ce7cd85d34afda4ae47f06d7958ea906b3fcc1 base-ref=main base-sha=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab merge-base=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab workflow=v5b-25 packet_context=none supplied_inputs=yes issues=none coverage=complete -->

## Run

Head, base, merge-base, workflow, packet identity, issues and coverage are in the run trailer above.

- Repository: `/home/jack/.cache/rc357x/root/continuation/repo`
- Target: range `main...03ce7cd85d34afda4ae47f06d7958ea906b3fcc1`
- Merged: no
- Supplied issues or specs: `ledger-spec/account-freeze`
- Prior record: `/home/jack/.cache/rc357x/root/continuation/seed/r1/record.json`
- Lineage: `/home/jack/.cache/rc357x/root/continuation/seed/r1/record.json`

## Line comments

The full body of each line-anchored item the summary indexes.

### `accounts/frozen-transfer-bypass`

**[P1] [must-fix] Refuse transfers that touch a frozen account**

**Triggers when:** A transfer names a frozen account as its target.

**Impact:** `Ledger.transfer` refuses a frozen source but appends the credit to a frozen target, so that account is credited despite the freeze that spec criterion 2 forbids.

**Change:** In `Ledger.transfer` (`ledger/accounts.py:85`), also raise `LedgerError` before appending either entry when the target account is frozen.

**Source:** Spec `ledger-spec/account-freeze`, criterion 2.

<!-- finding id=accounts/frozen-transfer-bypass head=03ce7cd85d34afda4ae47f06d7958ea906b3fcc1 priority=P1 action=must-fix blocking=true kind=bug fix=ledger/accounts.py:85 -->

### `accounts/post-docstring-frozen`

**[P3] [consider] Name the frozen-account error in the post docstring**

**Triggers when:** A caller reads `Ledger.post`'s docstring to learn which errors to handle.

**Impact:** The docstring still lists only zero amounts, overdrafts, and unknown accounts, although `post` now raises `LedgerError` for a frozen account.

**Change:** Add the frozen-account case to the `Ledger.post` docstring at `ledger/accounts.py:61`.

**Source:** `AGENTS.md`: every public function's docstring names the errors it raises.

Closing this without action is a correct response.

<!-- finding id=accounts/post-docstring-frozen head=03ce7cd85d34afda4ae47f06d7958ea906b3fcc1 priority=P3 action=consider blocking=false kind=maintainability fix=ledger/accounts.py:61 -->

## Requirements

- `ledger-spec/account-freeze/criterion-1` (acceptance): met. ledger/accounts.py:52-58 sets and clears `frozen` through `self.get`, which raises for an unknown account
- `ledger-spec/account-freeze/criterion-2` (acceptance): partial. ledger/accounts.py:85-86 refuses a frozen source; ledger/accounts.py:90 still credits a frozen target
- `ledger-spec/account-freeze/criterion-3` (acceptance): met. ledger/accounts.py:65-66 raises before the append at ledger/accounts.py:70; tests/test_freeze.py:15-21
- `ledger-spec/account-freeze/criterion-4` (acceptance): met. ledger/accounts.py:56-58; tests/test_freeze.py:23-27
- `ledger-spec/account-freeze/criterion-5` (acceptance): met. `Account.balance` and `render_statement` never read `frozen`; tests/test_freeze.py:29-31

## File coverage

- `ledger/accounts.py`: reviewed
- `tests/test_freeze.py`: reviewed

## Check evidence

- `python3 -m unittest discover -s tests -v` at `03ce7cd85d34afda4ae47f06d7958ea906b3fcc1`: reviewer-executed, the fix changes ledger/accounts.py, which the suite covers; 17 tests, pass

## Verification

- Allowance: initial batch spent, follow-up unspent, counting what the prior record `/home/jack/.cache/rc357x/root/continuation/seed/r1/record.json` spent.
- Candidate `accounts/frozen-transfer-bypass`, trigger `must-fix`, batch `initial` of `/home/jack/.cache/rc357x/root/continuation/seed/r1/record.json`: confirmed.

## Routed

- Unresolved: none.
- Disputed: none.

## Prior-item replies

### `accounts/frozen-transfer-bypass`: still-open

No forge thread. No drafted reply.

### `accounts/post-docstring-frozen`: still-open

No forge thread. No drafted reply.

## Artifacts

- record: `/home/jack/.cache/rc357x/root/continuation/seed/r2/record.json`
- payload: `/home/jack/.cache/rc357x/root/continuation/seed/r2/payload.json`
- batch: `/home/jack/.cache/rc357x/root/continuation/seed/r2/batch.json`
- composition: `/home/jack/.cache/rc357x/root/continuation/seed/r2/composition.json`
- prior_record: `/home/jack/.cache/rc357x/root/continuation/seed/r1/record.json`
- private_dir: `/home/jack/.cache/rc357x/root/continuation/seed/r2`
- store: `/home/jack/.cache/rc357x/root/continuation/seed/r2/review-context-03ce7cd85d34afda4ae47f06d7958ea906b3fcc1.json`
- skill_root: `/home/jack/.cache/rc357x/skill`
- spec: `/home/jack/.cache/rc357x/root/continuation/inputs/spec.md`
