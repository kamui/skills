# Continuation result: ledger-spec/account-freeze

**Status: Approved. Coverage: complete.** (advisory)

Head `b96a362e99ce4f5b6b1fe26ad02fda66e8343723` on `freeze`, base `main` at `2301c83`. Reviewed head was `03ce7cd`.

## Chain validation
- The record is `implementation-gate-record/2`, at head `864eea8`.
- The earlier addendum is `implementation-gate-addendum/2` with `864eea8` → `03ce7cd`.
- This continuation starts at `03ce7cd`.
- The record's `repository` matches, and the branch history `864eea8 → 03ce7cd → b96a362` matches the chain.
- No missing files and no broken links.

## State inherited
- The record had one open must-fix (`accounts/frozen-transfer-bypass`) and one consider (`accounts/post-docstring-frozen`).
- The earlier addendum left the must-fix `still-open`, because a transfer into a frozen account was still allowed.
- Allowance carried in: initial spent, follow-up unspent. There were no questions, routed items, or outstanding entries.

## Fixed findings
- `accounts/frozen-transfer-bypass`: **fixed**. `ledger/accounts.py:89-91` refuses a frozen source or target before the balance check and both appends (`:94-95`).
- `accounts/post-docstring-frozen`: **fixed**. The `Ledger.post` docstring (`ledger/accounts.py:61-64`) now names the frozen-account error. The `transfer` docstring was updated too.

## Fix delta
- `git diff 03ce7cd...b96a362` changes 2 files, both `reviewed`: `ledger/accounts.py` and `tests/test_freeze.py`.
- No new findings and no new questions.
- The new test `test_frozen_account_refuses_transfers_both_ways` observes the behavior it claims. It checks refusal in both directions, success after unfreeze, and unchanged balances.

## Requirements
Criterion 2 moves from `partial` to `met`. The other rows are unchanged.

## Checks
- **Suite:** the caller-supplied full suite at `b96a362` passed (exit 0, 18 tests). I did not re-run the suite.
- **Focused run:** I ran `python3 -m unittest tests.test_freeze -v` myself: 4 tests, OK.
- **Retention and invalidation:** I checked the caller's decision against the delta. Invalidating the earlier-head results is correct, because the fix changes `ledger/accounts.py` and the freeze tests. Nothing is carried forward.

## Verification
This change affects a data-integrity invariant and reached no blocker, so the safety-premise check applied.
- **Batch:** one follow-up batch, dispatched with model sonnet and `run_in_background: false`, and awaited.
- **Allowance:** initial and follow-up are now both spent.
- **Return:** accounted, exit 0.
- **`premise-transfer-check-before-mutation`:** `holds`. The frozen check precedes both appends, so a refused transfer changes no account.
- **`premise-no-other-entry-path`:** `holds`. Only `post` and `transfer` create entries; the CLI reaches entries only through `post`.
- I checked both rulings against the code myself.

## Artifacts
- **Addendum (new):** `/tmp/rcs-savings/control/continuation/review/addenda/addendum-b96a362e99ce4f5b6b1fe26ad02fda66e8343723.json`
- **Follow-up bundle:** `/tmp/rcs-savings/control/continuation/work/follow-up/` (`input.json`, `brief.md`, `manifest.json`, `raw-return.json`, `accounting.json`). The original input is `work/fu-input.json`.
- **Delta context store:** `/tmp/rcs-savings/control/continuation/work/store.json`
- The record and the earlier addendum are unchanged. The repository is unmodified and no network or publication was used.
