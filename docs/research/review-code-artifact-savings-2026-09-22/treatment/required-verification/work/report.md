# Review report

Profile `publishable`; status **Approved**; coverage `complete`. `finalize_review.py` generated this report from the validated composition. The summary body below is the one the payload carries.

**Approved (advisory)** — no findings.

**Intent:** Add a read-only `delegate` role that owners grant and revoke per account (issue #5; PR title/body).

**Issue fit:** All five acceptance criteria of #5 and the PR-body promises are met.

**Coverage:** Complete merge-base diff (3 files) reviewed; full unittest suite run once at the head, 17 tests pass; two authorization safety premises checked by one fresh verifier batch, both hold.

**Reviewed:** `a13922e` against merge-base `2301c83`.

## Observations

- `Ledger.grant` and `Ledger.revoke` also raise LedgerError for an unknown account via `get`, which their docstrings do not name. Evidence: `ledger/accounts.py:52-64`, `AGENTS.md`.

<!-- review-run head=a13922e76f42d9757608530348200affbf3bde2f base-ref=main base-sha=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab merge-base=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab workflow=v5b-24 context=0a72f34a0de2b71f1b30b8c3a0632038c1055de08f6a976fce5b959763524489 issues=example/ledger#5 coverage=complete -->

## Run

Head, base, merge-base, workflow, context digest, issues and coverage are in the run trailer above.

- Repository: `example/ledger`
- Target: pull-request
- Merged: no

## Requirements

- `issue-5/acceptance-criterion-1` (acceptance): met. ledger/accounts.py:52-64 grant/revoke; tests/test_delegates.py:test_only_owner_grants_and_revokes
- `issue-5/acceptance-criterion-2` (acceptance): met. ledger/accounts.py:54-56,61-63 owner check precedes mutation; test asserts LedgerError for non-owner
- `issue-5/acceptance-criterion-3` (acceptance): met. ledger/auth.py:15-16 membership in the account's own delegates set; test_grant_lets_delegate_view_that_account_only
- `issue-5/acceptance-criterion-4` (acceptance): met. ledger/auth.py:22 can_post is teller-only, unchanged; test_delegate_never_posts
- `issue-5/acceptance-criterion-5` (acceptance): met. ledger/auth.py:11-17 non-delegate branches unchanged; existing test_auth tests pass
- `pr-body/"can_view admits a delegate only for accounts that list them"` (acceptance): met. ledger/auth.py:15-16

## File coverage

- `ledger/accounts.py`: reviewed
- `ledger/auth.py`: reviewed
- `tests/test_delegates.py`: reviewed

## Check evidence

- `python3 -B -m unittest discover -s tests -v` at `a13922e76f42d9757608530348200affbf3bde2f`: reviewer-executed, Ran 17 tests, OK; output at work/run-events.jsonl timing event; no caller or CI evidence supplied

## Verification

- Allowance: initial batch spent, follow-up unspent.
- Batch `initial` (initial), `Agent subagent_type=general-purpose model=sonnet run_in_background=false`: bundle `/tmp/rcs-savings/treatment/required-verification/work/initial`, raw return `/tmp/rcs-savings/treatment/required-verification/work/initial-return.json`, accounting `/tmp/rcs-savings/treatment/required-verification/work/initial/accounting.json`.
- Safety premise `premise-1`, area `security`, batch `initial`: holds. can_view admits a delegate only through the account's own delegates set, mutable only via owner-gated grant/revoke. Evidence: ledger/auth.py:15-16; ledger/accounts.py:24,52-64
- Safety premise `premise-2`, area `security`, batch `initial`: holds. Owner, auditor, teller, and unknown-role can_view results are unchanged and can_post stays teller-only. Evidence: ledger/auth.py:6-22

## Routed

- Unresolved: none.
- Disputed: none.

## Artifacts

- payload: `/tmp/rcs-savings/treatment/required-verification/work/payload.json`
- batch: `/tmp/rcs-savings/treatment/required-verification/work/batch.json`
- fragments: `/tmp/rcs-savings/treatment/required-verification/work/fragments.md`
- composition: `/tmp/rcs-savings/treatment/required-verification/work/composition.json`
- packet: `/tmp/rcs-savings/treatment/required-verification/work/packet.json`
- fingerprint_input: `/tmp/rcs-savings/treatment/required-verification/work/fingerprint.json`
- private_dir: `/tmp/rcs-savings/treatment/required-verification/work`
- store: `/tmp/rcs-savings/treatment/required-verification/work/store`
- skill_root: `/tmp/rcs-savings/skills/1684cf4/skills/review-code`
