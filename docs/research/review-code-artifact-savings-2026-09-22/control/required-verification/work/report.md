# Review — example/ledger#6 "Let delegates read statements"

**Status: Approved (advisory)** — 1 `consider` finding; no blocker. Gating withheld.

## Identity
- Repository: `/tmp/rcs-savings/control/required-verification/repo` (https://github.com/example/ledger); PR #6, state OPEN, merged false, not draft
- Head `a13922e76f42d9757608530348200affbf3bde2f`; base ref `main`; base = merge-base `2301c83ee0b2ba0248fe3d2d1f6cd481963545ab`
- Mode one-shot, profile publishable; reviewer `reviewer`; packet `inputs/packet.json` (complete, no prior review state, so first review)
- Workflow v5b-24; context digest `0a72f34a0de2b71f1b30b8c3a0632038c1055de08f6a976fce5b959763524489`
- Skill root `/tmp/rcs-savings/skills/d8c2dd9/skills/review-code`; store `/tmp/rcs-savings/control/required-verification/work/store`

## Summary
Adds a `delegate` role: `Account.delegates`, `Ledger.grant`/`revoke` (owner-only), and a `can_view` branch admitting a delegate only for accounts that list them. All five acceptance criteria of #5 are met. The one finding is a non-blocking repository-rule inconsistency.

## Findings
**[P3] [consider] `ledger/grant-owner-check-outside-auth` — Move the owner check for grant and revoke into auth.py** (invariant; anchor `ledger/accounts.py:54-63` RIGHT)
- Triggers when: `Ledger.grant` and `Ledger.revoke` each decide authorization inline with `account.owner != user`, while `auth.py` holds the same owner comparison in `can_view`.
- Impact: base `AGENTS.md:6` says authorization decisions live in `ledger/auth.py`; the owner rule for managing delegates now lives in two modules and can drift. Behavior is correct today.
- Change: add `can_manage(user, account)` to `ledger/auth.py` reusing the owner semantics and call it from both `grant` and `revoke`, raising `LedgerError` on refusal. `auth.py` imports `Account` from `accounts.py`, so import lazily or under `TYPE_CHECKING`.
- Verification: confirmed by the initial-batch verifier (optional scrutiny; the finding is `consider`).

## Questions / observations
None.

## Requirement outcomes
| Source | Outcome | Evidence |
| --- | --- | --- |
| issue-5/acceptance-criterion-1 (owner grants and revokes read-only access) | met | `accounts.py:52-64`; test `test_only_owner_grants_and_revokes` |
| issue-5/acceptance-criterion-2 (owner only, else `LedgerError`, nothing changes) | met | check precedes mutation at `accounts.py:54-57,61-64`; unknown account raises in `get` first |
| issue-5/acceptance-criterion-3 (view only granting accounts) | met | `auth.py:15-16`, per-instance `default_factory` set |
| issue-5/acceptance-criterion-4 (never posts) | met | `can_post` is teller-only (`auth.py:20-22`) |
| issue-5/acceptance-criterion-5 (others unchanged) | met | owner/auditor/teller/unknown branches identical to base |
| pr-body/"`can_view` admits a delegate only for accounts that list them" | met | `auth.py:15-16` |

## Per-file coverage (all reviewed)
- `ledger/accounts.py` — reviewed
- `ledger/auth.py` — reviewed
- `tests/test_delegates.py` (added) — reviewed. Inspected in execution order: the assertions observe grant/view scoping, delegate posting refusal, and non-owner refusal. Minor gap, not admitted: the refusal test does not assert `delegates` is unchanged after a refused call. It is decided by trace, and the verifier held that premise.

## Check evidence
- Reviewer-executed: `python3 -m unittest discover -s tests` at head `a13922e`, run once via the `run_events.py` wrapper: 17 tests, OK. Run in the repository and `__pycache__` output was removed afterward. No CI or supplied check evidence was in the inputs.

## Verification
- Batch `initial` (Sonnet 5 worker, model sonnet, `run_in_background: false`, awaited; bundle `work/initial`, raw return `work/raw-return.json`, accounting `work/accounting.json`, exit 0).
- Candidate `ledger/grant-owner-check-outside-auth`: confirmed.
- Safety premises (all `holds`): `premise-refused-grant-revoke-no-change`, `premise-delegate-view-scoped`, `premise-delegate-never-posts`.
- Allowance: initial spent, follow-up unspent.

## Ambiguities
- AGENTS.md's second clause speaks of comparing roles; the owner check compares identity. Supportable readings: (a) the first clause governs any authorization decision (applied; the finding stays `consider`); (b) only role comparisons are covered, so no finding. Neither reading blocks merge.
- Recorded deferrals: none. Unrecoverable inputs: none. Routed items: none.

## Coverage
Complete.

## Artifacts (all under `/tmp/rcs-savings/control/required-verification/work`)
`payload.json`, `batch.json`, `fragments.md`, `composition.json`, `verify-input.json`, `initial/` (`brief.md`, `input.json`, `manifest.json`), `raw-return.json`, `accounting.json`, `store`, `run-events.jsonl`, `report.md`.

Would-be review body (from `batch.json`, unpublished):

> **Approved (advisory)** — 1 consider finding. … Reviewed `a13922e` against merge-base `2301c83`.
> - [P3] [consider] Move the owner check for grant and revoke into auth.py — anchor [`ledger/accounts.py:54-63`](https://github.com/example/ledger/blob/a13922e76f42d9757608530348200affbf3bde2f/ledger/accounts.py?plain=1#L54-L63)
