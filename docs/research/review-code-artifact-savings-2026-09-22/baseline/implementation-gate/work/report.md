# Review: ledger-spec/statement-date-filter

**Mode:** one-shot **Profile:** implementation-gate
**Repository:** `/tmp/rcs-savings/baseline/implementation-gate/repo`
**Target (range):** `2301c83ee0b2ba0248fe3d2d1f6cd481963545ab...2ba40465ef91f15b2963a4b12e80f46ee0e9efae`
**Base:** `main` @ `2301c83ee0b2ba0248fe3d2d1f6cd481963545ab` (also the merge-base)
**Head:** `2ba40465ef91f15b2963a4b12e80f46ee0e9efae` (branch `date-filter`)
**Context digest:** `c6f93b91a90cfb272435e704bdf117d13f1b236401814c252ef638cb376ff7c5`
**Workflow:** `v5b-24` **Schema:** `implementation-gate-record/2`
**Skill root:** `/tmp/rcs-savings/skills/d8c2dd9/skills/review-code`

## Status: **Approved**

No `must-fix` issues; coverage is complete; no open material questions.

## Summary

**Intent:** Let `ledger statement` accept optional inclusive `--since`/`--until` date bounds, add an opening-balance line and range-scoped closing balance, and document the new flags.

**Issue fit:** Met — all six `spec-ledger-spec/statement-date-filter` criteria are satisfied: bounded, inclusive filtering; the opening-balance line and its before-`--since` sum; range-restricted rows with running balances that continue from the opening balance; the `--until`-scoped (or whole-history) closing balance; exit-2 rejection of an invalid date or a reversed range; and the README update. Source: user-supplied spec; the two commit messages in the range.

**Coverage:** Complete merge-base diff reviewed (`README.md`, `ledger/cli.py`, `ledger/statement.py`, `tests/test_filter.py`). Unchanged `ledger/accounts.py`, `ledger/auth.py`, and the three pre-existing test modules (`test_accounts.py`, `test_auth.py`, `test_cli.py`, `test_statement.py`) were inspected for regressions and callers of the touched functions; none found — the new `since`/`until` parameters default to `None` and every existing call site is untouched. Caller-supplied `unittest discover` (17/17 pass) and the two criterion-5 CLI exercises were accepted as exact-head, clean-tree evidence. The reviewer additionally ran four focused CLI invocations (`--until`-only, `--since`-only, and two non-canonical date strings) to settle a candidate about date-format strictness by trace/execution.

## Findings

None.

## Questions

None.

## Observations (1)

- `iso_day` (`ledger/cli.py:25-30`) delegates entirely to `date.fromisoformat`, which on Python ≥3.11 (the reviewed environment runs 3.14.7) accepts ISO 8601 forms other than `YYYY-MM-DD` — e.g. `--since 2026-W01-1` (a week-date string) parses as `2025-12-29` instead of being rejected. This is looser than spec item 1's documented format and item 5's invalid-date rejection. Impact judged below the finding bar: an accidental no-dash typo (`20260901`) still resolves to the identical, correct date, and the only genuinely divergent inputs are exotic ISO variants a user would not type by accident when following the documented `YYYY-MM-DD` format. Evidence: reviewer execution, `--since 2026-W01-1` exits 0 and opens with `2025-12-29` rather than exiting 2 (see check evidence below).

## Requirement outcomes

| # | Source | Class | Disposition | Evidence |
|---|--------|-------|-------------|----------|
| 1 | `spec-ledger-spec/statement-date-filter/1` | acceptance | **met** | `ledger/cli.py:40-41` adds optional `--since`/`--until`; `ledger/statement.py:37-40` filters entries with inclusive `day<since` / `day>until` bounds |
| 2 | `spec-ledger-spec/statement-date-filter/2` | acceptance | **met** | `ledger/statement.py:48-49` prints `Opening balance: ` right after the heading when `since` is set, using `balance_before` (`statement.py:17-19`), the sum of entries dated before `since` |
| 3 | `spec-ledger-spec/statement-date-filter/3` | acceptance | **met** | `ledger/statement.py:27-42`: rows outside `since..until` are skipped after `running` is incremented, so the first listed row's running balance equals `balance_before(since)` plus its own amount; `tests/test_filter.py:27-31` confirms `Opening balance: 100.00` followed by running `60.00` for a `-40.00` row |
| 4 | `spec-ledger-spec/statement-date-filter/4` | acceptance | **met** | `ledger/statement.py:52-53` uses `balance_through(until)` (`statement.py:22-24`, sum of entries dated on or before `until`) when `until` is set, else `account.balance()` |
| 5 | `spec-ledger-spec/statement-date-filter/5` | acceptance | **met** | `ledger/cli.py:25-30` (`iso_day` raises `ArgumentTypeError`, argparse exits 2) and `cli.py:48-50` (explicit `since>until` check, exit 2 with stderr message); `inputs/criterion-5.txt` records exit 2 for `2026-13-01` and for a reversed `--since`/`--until` at head `2ba4046` |
| 6 | `spec-ledger-spec/statement-date-filter/6` | acceptance | **met** | `README.md:7` adds an example invocation with both flags; `README.md:12` documents both as inclusive and optional and states the opening/closing balance behavior |

## Per-file coverage

| File | State |
|------|-------|
| `README.md` | reviewed |
| `ledger/cli.py` | reviewed |
| `ledger/statement.py` | reviewed |
| `tests/test_filter.py` | reviewed |

Diff coverage from `review_context.py`: 4/4 chunks consumed, complete (no missing/truncated chunks). Context files read for regression/consistency but not part of the changed-file manifest: `ledger/accounts.py`, `ledger/auth.py`, `tests/test_accounts.py`, `tests/test_auth.py`, `tests/test_cli.py`, `tests/test_statement.py`, `AGENTS.md`.

## Check evidence

| Check | Head | Outcome | Reason |
|-------|------|---------|--------|
| `python3 -m unittest discover -s tests -v` | `2ba4046…` | accepted | Caller-supplied; exact reviewed head, clean committed tree, matching Python 3.14.7/stdlib-only environment, complete readable output showing 17/17 pass (`inputs/unittest-head.txt`) |
| `python3 -m ledger.cli statement /dev/null 1001 --since 2026-13-01` | `2ba4046…` | accepted | Caller's criterion-5 exercise (invalid date); exact head, exit 2, output in `inputs/criterion-5.txt` |
| `python3 -m ledger.cli statement /dev/null 1001 --since 2026-09-03 --until 2026-09-01` | `2ba4046…` | accepted | Caller's criterion-5 exercise (reversed range); exact head, exit 2, output in `inputs/criterion-5.txt` |
| `... statement <tmp.json> 1001 --until 2026-09-01` (no `--since`) | `2ba4046…` | reviewer-executed | No supplied evidence exercised `--until` alone; confirmed no opening-balance line and closing balance restricted to on/before `until`, no crash |
| `... statement <tmp.json> 1001 --since 2026-09-01` (no `--until`) | `2ba4046…` | reviewer-executed | No supplied evidence exercised `--since` alone; confirmed opening balance prints and closing balance covers every entry (`until` absent) |
| `... statement <tmp.json> 1001 --since 20260901` | `2ba4046…` | reviewer-executed | Investigated `iso_day`'s reliance on `date.fromisoformat`; non-dashed form parses to the same correct date, no divergence |
| `... statement <tmp.json> 1001 --since 2026-W01-1` | `2ba4046…` | reviewer-executed | Confirmed `date.fromisoformat` accepts an ISO week-date string outside `YYYY-MM-DD`, exits 0 with an unexpected `2025-12-29` date instead of exiting 2; basis for the published observation |

No test suite was run a second time by the reviewer; the caller's `unittest discover` result was reused per `check-evidence.md`.

## Verification

No candidate was proposed `must-fix`, none touches security/authorization/data-loss/destructive-migration/released-compatibility, and this is a first review (no prior `must-fix` to recheck). The safety-premise check does not apply: the change is a display-only filter over an in-memory ledger with no data mutation, auth, migration, or concurrency surface. No verification tasks were opened; no worker was dispatched.

**Allowance:** `initial_spent: false`, `follow_up_spent: false` — fully unspent (0 of 1 initial batch, 0 of 1 follow-up used).

## Routed items

None — no unresolved ambiguities, disputes, or unrecoverable inputs.

## Coverage gaps

None. Every changed file was reviewed; the caller's evidence was sufficient and accepted; no required check, input, or verification was left unfinished.

## Artifacts

- Private working directory: `/tmp/rcs-savings/baseline/implementation-gate/work/private.4XwGSs/`
- Review context store: `/tmp/rcs-savings/baseline/implementation-gate/work/private.4XwGSs/review-context.json`
- Composition input: `/tmp/rcs-savings/baseline/implementation-gate/work/private.4XwGSs/composition.json`
- **Record (implementation-gate-record/2):** `/tmp/rcs-savings/baseline/implementation-gate/work/private.4XwGSs/record.json`
- **Addenda directory (empty — no continuation yet):** `/tmp/rcs-savings/baseline/implementation-gate/work/private.4XwGSs/addenda/`
- Raw diff/manifest/chunk transcript: `/tmp/rcs-savings/baseline/implementation-gate/work/private.4XwGSs/context-output.md`
- Saved commit messages: `commit-e16a48c.txt`, `commit-2ba4046.txt`
- Fingerprint input: `/tmp/rcs-savings/baseline/implementation-gate/work/private.4XwGSs/fingerprint-input.json`
- Run-timing events (script-appended, not hand-edited): `/tmp/rcs-savings/baseline/implementation-gate/work/private.4XwGSs/run-events.jsonl`
- This report: `/tmp/rcs-savings/baseline/implementation-gate/work/report.md`

No forge writes, publication, or source mutation occurred. This local record was not passed to `review-code-publish`.
