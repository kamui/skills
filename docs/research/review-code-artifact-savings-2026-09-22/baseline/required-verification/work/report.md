# review-code — one-shot / publishable

Target: `https://github.com/example/ledger/pull/6` ("Let delegates read statements")
Repository (checkout used): `/tmp/rcs-savings/baseline/required-verification/repo`
Skill root: `/tmp/rcs-savings/skills/d8c2dd9/skills/review-code`
Private store/work directory: `/tmp/rcs-savings/baseline/required-verification/work/private`

## Run identity

| Field | Value |
|---|---|
| head | `a13922e76f42d9757608530348200affbf3bde2f` |
| base_ref | `main` |
| base_sha / merge_base | `2301c83ee0b2ba0248fe3d2d1f6cd481963545ab` |
| state | OPEN, not merged |
| reviewer identity | `reviewer` |
| packet prior-review state | none (no reviews/threads/comments in packet) → not a re-review |
| context digest (`v5b-24`) | `0a72f34a0de2b71f1b30b8c3a0632038c1055de08f6a976fce5b959763524489` |
| repository_url | `https://github.com/example/ledger` |
| profile | `publishable` |
| mode | `one-shot` |

Phase-1 fetch was supplied, not performed live: `scripts/forge_packet.py normalize` was already run by the caller over `inputs/forge-1.json` to produce `inputs/packet.json`; both were read as-is and treated as the persisted forge section (`pr.merged: false` is present, so no unrecoverable-input gap on that field). No live forge or network calls were made at any point in this run.

## Status: **Changes Requested**

2 confirmed `must-fix` findings block merge (see below). No open material questions; coverage is complete.

## Intent and issue fit

**Intent:** Add a `delegate` role so an account owner can grant and revoke another user's read-only statement access (PR body, closes issue `example/ledger#5`).

**Issue fit — `example/ledger#5` "Let owners delegate statement access":**

| # | Acceptance criterion | Disposition | Evidence |
|---|---|---|---|
| 1 | Owner can grant/revoke another user read-only access, and revoke it | met | `ledger/accounts.py:52-64` — `Ledger.grant`/`Ledger.revoke` |
| 2 | Only the owner can grant/revoke; anyone else gets `LedgerError`, nothing changes | met | `ledger/accounts.py:54-57,61-64` — ownership check raises before any mutation in both methods |
| 3 | A delegate can view only the accounts that granted them access | met | `ledger/auth.py:15-16` (`if role == "delegate": return user in account.delegates`); confirmed by `tests/test_delegates.py::test_grant_lets_delegate_view_that_account_only` |
| 4 | A delegate can never post entries | met | `ledger/auth.py:20-22` `can_post` unchanged (`role == "teller"` only); confirmed by `tests/test_delegates.py::test_delegate_never_posts` |
| 5 | Owner, auditor, and teller access is unchanged | met | `ledger/auth.py` diff shows only an added `ROLES` entry and an added `delegate` branch; the owner/auditor/teller branches are untouched, and `tests/test_auth.py` (pre-existing) still passes unmodified |

No commits or spec beyond the PR title/body/issue were available or needed; no non-goal or permission-expansion issue was found outside the above rows. No requirement is `partial` or `not-verifiable`.

## Coverage

| File | Status |
|---|---|
| `ledger/accounts.py` | reviewed |
| `ledger/auth.py` | reviewed |
| `tests/test_delegates.py` | reviewed (added test; inspected in execution order, see below) |

All 3 changed files reviewed; none ignored or unreviewed. Manifest and diff pulled via `scripts/review_context.py --merge-base 2301c83... --head a13922e... --store .../store.json` (chunk inventory: 3/3 diff chunks consumed, complete). Also read in full at head for context: `ledger/cli.py`, `ledger/statement.py`, `AGENTS.md`, `tests/test_auth.py`, `tests/test_accounts.py`, `tests/test_cli.py`, `tests/test_statement.py`; and at merge-base: `ledger/accounts.py`, `ledger/auth.py` (to confirm what the diff introduced vs. pre-existing).

**Changed-test inspection** (`tests/test_delegates.py`, new file, 3 test functions): each test's `setUp` opens two real accounts through the real `Ledger`; each assertion observes the call under test directly (`can_view`/`can_post`/`grant`/`revoke`/`assertRaises(LedgerError)`) — none are vacuous, none assert only on their own setup. No suspicious execution-order issue (no deferred cleanup, no unarmed mock, no fixture torn down early).

**Focused-test execution** (wrapped via `scripts/run_events.py wrap ... --event focused-test-ran`, recorded in `private/run-events.jsonl`):
- `python3 -m unittest tests.test_delegates -v` at head `a13922e76f4...` — exit 0, 3/3 pass.
- `python3 -m unittest discover -s tests -v` at head `a13922e76f4...` (full suite, run once) — exit 0, 17/17 pass, no regression anywhere else.

**Check evidence:** none was supplied by the caller; both runs above were reviewer-executed.

## Findings

### [P2] [must-fix] Move the owner check for grant/revoke into `ledger/auth.py`
- id: `ledger/grant-revoke-auth-placement` · kind: `security`
- **Triggers when:** Any call to `Ledger.grant` or `Ledger.revoke`.
- **Impact:** `Ledger.grant` and `Ledger.revoke` each inline an identical ownership comparison (`if account.owner != user: raise LedgerError(...)`) directly in `ledger/accounts.py` instead of routing the decision through `ledger/auth.py`, which is where every other authorization decision (`can_view`, `can_post`) lives, and which already encodes the equivalent owner check inside `can_view`'s fallback branch (`return account.owner == user`). Authorization logic ends up split across two modules and duplicated verbatim across the two new methods: a future change to who may administer delegate access (e.g. letting a co-owner grant) now requires editing `accounts.py` in two places instead of `auth.py` once.
- **Change:** Add an `ledger/auth.py` function (e.g. `can_manage_delegates(user, account)`) that encapsulates the ownership check, and have `Ledger.grant`/`Ledger.revoke` call it instead of comparing `account.owner` to `user` themselves.
- **Source:** `AGENTS.md:7` — "Authorization decisions live in `ledger/auth.py`; callers never compare roles themselves."
- **Anchor:** [`ledger/accounts.py:52-64`](https://github.com/example/ledger/blob/a13922e76f42d9757608530348200affbf3bde2f/ledger/accounts.py?plain=1#L52-L64) (RIGHT)
- **Fix site:** [`ledger/auth.py:18`](https://github.com/example/ledger/blob/a13922e76f42d9757608530348200affbf3bde2f/ledger/auth.py?plain=1#L18)
- **Verification:** mandatory (proposed must-fix, and concerns authorization) — **confirmed**, see Verification section.

### [P3] [must-fix] Document the unknown-account error in grant/revoke docstrings
- id: `ledger/grant-revoke-docstring-errors` · kind: `requirement`
- **Triggers when:** Calling `Ledger.grant` or `Ledger.revoke` with a number that is not in `self.accounts`.
- **Impact:** Both methods call `self.get(number)`, which raises `LedgerError` for an unknown account, but each docstring says only "Raises LedgerError unless user owns the account," omitting that cause — unlike `post`'s and `transfer`'s docstrings, which explicitly enumerate "an unknown account" alongside their other raise conditions, per this repository's own documented convention.
- **Change:** Reword each docstring to name both causes, e.g. "Raises LedgerError for an unknown account or when user does not own it."
- **Source:** `AGENTS.md:6` — "Every public function's docstring names the errors it raises."
- **Anchor:** [`ledger/accounts.py:53`](https://github.com/example/ledger/blob/a13922e76f42d9757608530348200affbf3bde2f/ledger/accounts.py?plain=1#L53) (RIGHT) (`revoke`'s docstring at line 60 carries the identical omission)
- **Verification:** mandatory (proposed must-fix) — **confirmed**, see Verification section.

## Questions

None. No fact material to the merge decision was left unsettled by static inspection.

## Observations (1 of max 3)

- `ledger/cli.py` has no notion of a caller's identity or role, so the new delegate role and `Ledger.grant`/`revoke` are reachable only through the library API, not through the shipped `statement` command. Evidence: `ledger/cli.py:35-44` (`main()` calls `render_statement(ledger.get(args.account))` unconditionally, with no user/role argument). Non-actionable: no acceptance criterion, non-goal, or repository rule requires CLI wiring for this PR, so this does not qualify as a finding.

## Verification (mandatory candidate verification)

Both findings above are `proposed must-fix`, which mandates independent verification before publication (also true independently for the `security`-kind finding, per the "about security or authorization" trigger).

- **Batch:** one initial batch, phase `initial`, batch id `initial`. No follow-up batch was needed or used (allowance: 1 of 1 initial + 0 of 1 follow-up spent).
- **Build:** `python3 scripts/build_verifier_prompt.py private/verifier-input-initial.json --output private/bundle-initial` → exit 0. Bundle: `private/bundle-initial/{input.json,brief.md,manifest.json}`.
- **Dispatch:** fresh-context worker (Agent tool, `general-purpose`, model `sonnet`, high effort, `run_in_background: false`, awaited synchronously), given only `brief.md` and `manifest.json` absolute paths plus the repository path and pinned SHAs — no primary reasoning was shared.
- **Return:** saved verbatim as `private/bundle-initial/raw-return.json`. `manifest_sha256` echoed by the worker (`e873b9101bd734e00c7c5bc3c6462f03aa6411190817b6f5bef9516be5fbe1fe`) matches the actual manifest file hash (independently recomputed).
- **Accounting:** `python3 scripts/account_verifier_return.py --bundle private/bundle-initial --output private/bundle-initial/accounting.json private/bundle-initial/raw-return.json` → exit 0, structurally complete. Both candidates accounted, none withheld, no violations.
- **Rulings:**
  - `ledger/grant-revoke-auth-placement` → **confirmed**. Verifier independently re-derived the same lines (`accounts.py:55`, `accounts.py:62`, `auth.py:17`) and confirmed via `git show <merge-base>:ledger/accounts.py` / grep that `grant`/`revoke`/`delegate` are entirely absent at the merge-base, i.e. this is newly introduced code, not a pre-existing omission.
  - `ledger/grant-revoke-docstring-errors` → **confirmed**. Verifier confirmed `self.get()`'s own docstring ("Raises LedgerError when it does not exist") is reached before the owner check in both new methods, and that `post`/`transfer` enumerate the "unknown account" cause while `grant`/`revoke` do not.
  - No `duplicate_groups` suggested, no corrections applied, no safety_rulings recorded (none were requested), `observation: null`.
- **Premises:** none were required — the primary pass ended with two confirmed must-fix candidates, so the review already concludes with a blocker; the safety-premise check ("run when the review would conclude with no blocker") does not apply, and no additional premises were added to a follow-up.
- I (the primary) independently re-verified every cited coordinate against the actual file contents before reconciling; all citations are accurate.

Both findings, being confirmed, publish as `must-fix` and drive the `Changes Requested` status.

## Artifacts

All under `/tmp/rcs-savings/baseline/required-verification/work/private/` unless noted:

| Artifact | Path |
|---|---|
| Context store (step 2) | `private/store.json` |
| Rendered diff/manifest/ranges/chunks | `private/context.md` |
| Verifier input (candidates authored) | `private/verifier-input-initial.json` |
| Verifier bundle (input/brief/manifest) | `private/bundle-initial/{input.json,brief.md,manifest.json}` |
| Verifier raw return (verbatim) | `private/bundle-initial/raw-return.json` |
| Verifier accounting report | `private/bundle-initial/accounting.json` |
| Composition input (authored) | `private/composition.json` |
| **Payload (publishable finding/summary bodies)** | `private/payload.json` |
| **Batch (single forge-comment-shaped bundle)** | `private/batch.json` |
| **Fragments (rendered anchor/fix links)** | `private/fragments.md` |
| Run timing events (append-only, untouched) | `private/run-events.jsonl` |
| This report | `/tmp/rcs-savings/baseline/required-verification/work/report.md` |

No reviewed source was modified. No forge write, publish, or network call was made at any point (`review-code-publish` was not invoked). All script invocations above used absolute paths under `/tmp/rcs-savings/skills/d8c2dd9/skills/review-code`.

## Coverage completeness statement

Coverage is complete: every changed file is reviewed, the mandatory verification batch was dispatched and awaited with a structurally-complete, fully-accounted return, the changed test was inspected and executed, the full suite was run once with no regression, and no required input, fetch, or check evidence is missing. Nothing here is incomplete or withheld.
