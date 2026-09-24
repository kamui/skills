# Review report

Status **Changes Requested**; coverage `complete`. `render_review.py` generated this report from the validated composition. The summary body below is the one the payload carries.

**Changes Requested (advisory)** — 3 must-fix findings.

**Intent:** Add owner-controlled, read-only statement delegation for individual accounts while preserving existing owner and staff permissions.

**Issue fit:** Partial. The new predicates and Ledger.grant/revoke methods cover the intended cases when callers use them, but public grant state and existing statement and posting paths do not enforce the issue's absolute access requirements.

**Coverage:** Reviewed all three changed files and the relevant base and head account, authorization, statement, CLI, documentation, and test paths. The three changed tests passed once at the pinned head (focused-test-output.txt); that run does not exercise the bypass paths. The supplied packet is complete, and the initial verifier batch accounted for all three findings and both scoped safety premises.

**Reviewed:** `a13922e` against merge-base `2301c83`.

## Findings

- [P2] [must-fix] Protect the delegate grant state from direct mutation — anchor [`ledger/accounts.py:24`](https://github.com/example/ledger/blob/a13922e76f42d9757608530348200affbf3bde2f/ledger/accounts.py?plain=1#L24)
- [P2] [must-fix] Check delegated access before printing a statement — anchor [`ledger/auth.py:15-16`](https://github.com/example/ledger/blob/a13922e76f42d9757608530348200affbf3bde2f/ledger/auth.py?plain=1#L15-L16); fix [`ledger/cli.py:40`](https://github.com/example/ledger/blob/a13922e76f42d9757608530348200affbf3bde2f/ledger/cli.py?plain=1#L40)
- [P2] [must-fix] Reject delegates on the entry posting path — anchor [`ledger/auth.py:6`](https://github.com/example/ledger/blob/a13922e76f42d9757608530348200affbf3bde2f/ledger/auth.py?plain=1#L6); fix [`ledger/accounts.py:66`](https://github.com/example/ledger/blob/a13922e76f42d9757608530348200affbf3bde2f/ledger/accounts.py?plain=1#L66)

<!-- review-run head=a13922e76f42d9757608530348200affbf3bde2f base-ref=main base-sha=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab merge-base=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab workflow=v5b-25 packet_context=a67729ccd893ae2f7bd5cf79fcbafccc32d8a4b10fe9a2fa4fe55f193169ffec supplied_inputs=no issues=example/ledger#5 coverage=complete -->

## Run

Head, base, merge-base, workflow, packet identity, issues and coverage are in the run trailer above.

- Repository: `example/ledger`
- Target: pull-request
- Merged: no

## Line comments

The full body of each line-anchored item the summary indexes.

### `ledger/public-delegate-set`

**[P2] [must-fix] Protect the delegate grant state from direct mutation**

**Triggers when:** Code holding an Account reference obtained from Ledger.get adds its own user name to account.delegates without calling Ledger.grant.

**Impact:** can_view then authorizes that user for this account despite no owner grant; the owner-only LedgerError guard is bypassed.

**Change:** Keep grant state behind an owner-checked update path, with no mutable grant set exposed through Account references.

**Source:** Issue #5, acceptance criterion 2.

<!-- finding id=ledger/public-delegate-set head=a13922e76f42d9757608530348200affbf3bde2f priority=P2 action=must-fix blocking=true kind=security -->

### `ledger/cli-view-bypass`

**[P2] [must-fix] Check delegated access before printing a statement**

**Triggers when:** A delegate runs the documented statement command for another account in a readable multi-account ledger file.

**Impact:** The command renders the requested account without consulting can_view. The caller already has the underlying file, but the documented statement path does not honor the per-account delegate restriction.

**Change:** In ledger/cli.py, connect the delegate-facing statement path to a caller identity and role check before render_statement, while preserving existing owner and staff access.

**Source:** Issue #5, acceptance criterion 3.

<!-- finding id=ledger/cli-view-bypass head=a13922e76f42d9757608530348200affbf3bde2f priority=P2 action=must-fix blocking=true kind=requirement fix=ledger/cli.py:40 -->

### `ledger/post-bypass`

**[P2] [must-fix] Reject delegates on the entry posting path**

**Triggers when:** A delegate with a Ledger reference calls Ledger.post with a valid amount after receiving statement access.

**Impact:** Ledger.post appends an entry and changes the balance, even though can_post returns false for the delegate and the issue promises read-only access.

**Change:** In ledger/accounts.py or an authorized posting entry point, require a role decision before a delegate-facing post can append an entry; keep the internal loader's existing behavior available.

**Source:** Issue #5, acceptance criterion 4.

<!-- finding id=ledger/post-bypass head=a13922e76f42d9757608530348200affbf3bde2f priority=P2 action=must-fix blocking=true kind=requirement fix=ledger/accounts.py:66 -->

## Requirements

- `issue-5/acceptance-criterion-1` (acceptance): partial. ledger/accounts.py:52-64 implements in-memory owner grant and revoke; ledger/accounts.py:66-75 still permits direct entry posting through Ledger.post.
- `issue-5/acceptance-criterion-2` (acceptance): partial. ledger/accounts.py:55-64 rejects nonowners through grant/revoke, but ledger/accounts.py:24 exposes the mutable grant set through Ledger.get at :45-48.
- `issue-5/acceptance-criterion-3` (acceptance): partial. ledger/auth.py:15-16 scopes can_view, but ledger/cli.py:35-40 renders any requested account without that decision.
- `issue-5/acceptance-criterion-4` (acceptance): partial. ledger/auth.py:20-22 denies delegate posting through can_post, but ledger/accounts.py:66-75 has no caller or role check.
- `issue-5/acceptance-criterion-5` (acceptance): met. ledger/auth.py:11-22 preserves the owner, auditor, and teller branches, and the base and head call paths are unchanged for those roles.
- ``pr-body/"Adds a `delegate` role."`` (acceptance): met. ledger/auth.py:6 adds delegate to ROLES.
- ``pr-body/"Owners grant and revoke delegates with `Ledger.grant` and `Ledger.revoke`"`` (acceptance): met. ledger/accounts.py:52-64 defines both methods and checks account.owner before mutation.
- ``pr-body/"`can_view` admits a delegate only for accounts that list them."`` (acceptance): met. ledger/auth.py:15-16 returns membership in the supplied account's delegates set for the delegate role.

## File coverage

- `ledger/accounts.py`: reviewed
- `ledger/auth.py`: reviewed
- `tests/test_delegates.py`: reviewed

## Check evidence

- `env PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest discover -s tests -p test_delegates.py -v` at `a13922e76f42d9757608530348200affbf3bde2f`: reviewer-executed, Exit 0; three changed tests passed; raw output copied to focused-test-output.txt. These tests check the helper predicates and Ledger.grant/revoke, not the documented CLI or direct Ledger.post.

## Verification

- Allowance: initial batch spent, follow-up unspent.
- Batch `initial` (initial), `Awaited foreground codex exec -m gpt-6-sol with model_reasoning_effort=high; exit 0`: bundle `/home/jack/.cache/rc357x/root/required-verification/work/review/initial`, raw return `/home/jack/.cache/rc357x/root/required-verification/work/review/initial/repaired-return.json`, accounting `/home/jack/.cache/rc357x/root/required-verification/work/review/initial/accounting-repaired.json`.
- Candidate `ledger/public-delegate-set`, trigger `security`, batch `initial`: confirmed.
- Candidate `ledger/cli-view-bypass`, trigger `must-fix`, batch `initial`: confirmed.
- Candidate `ledger/post-bypass`, trigger `must-fix`, batch `initial`: confirmed.
- Safety premise `premise-delegate-view-gate`, area `security`, batch `initial`: holds. For a caller using can_view with role delegate, access is false unless that Account's delegates set contains the user. Evidence: ledger/auth.py:11-17; tests/test_delegates.py:14-16
- Safety premise `premise-owner-grant-check`, area `security`, batch `initial`: holds. Calls through Ledger.grant or Ledger.revoke with a nonowner user string raise LedgerError before changing delegates. Evidence: ledger/accounts.py:45-64; tests/test_delegates.py:22-29

## Routed

- Unresolved: none.
- Disputed: none.

## Artifacts

- record: `/home/jack/.cache/rc357x/root/required-verification/work/review/record.json`
- payload: `/home/jack/.cache/rc357x/root/required-verification/work/review/payload.json`
- batch: `/home/jack/.cache/rc357x/root/required-verification/work/review/batch.json`
- composition: `/home/jack/.cache/rc357x/root/required-verification/work/review/composition.json`
- packet: `/home/jack/.cache/rc357x/root/required-verification/work/review/packet.json`
- private_dir: `/home/jack/.cache/rc357x/root/required-verification/work/review`
- store: `/home/jack/.cache/rc357x/root/required-verification/work/review/review-context.json`
- skill_root: `/home/jack/.cache/rc357x/skill`
- verifier_original_return: `/home/jack/.cache/rc357x/root/required-verification/work/review/initial/worker-last-message.md`
