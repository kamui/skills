# Review report

Status **Changes Requested**; coverage `complete`. `render_review.py` generated this report from the validated composition. The summary body below is the one the payload carries.

**Changes Requested (advisory)** — 1 must-fix finding.

**Intent:** Add CSV output to the statement command while keeping text as the default, with the requested header, decimal values, and CSV round-trip behavior.

**Issue fit:** Issue #3's four acceptance criteria are met. The new CSV export also exposes formula-leading descriptions as spreadsheet formulas when accountants open a statement.

**Coverage:** Reviewed all three changed files, the statement and account paths, the CLI callers, existing tests, and base guidance. The repository's 16-test suite passed at 0eb283dfe715341548387bf65af857affedf5dfa. A separate CLI check passed for newline and quote round-trip and default text output; it also reproduced the formula-leading cell. The initial fresh verifier confirmed the finding. The supplied packet has complete issue and review coverage; no live forge or CI read was performed.

**Reviewed:** `0eb283d` against merge-base `2301c83`.

## Findings

- [P2] [must-fix] Prevent formula execution from exported descriptions — anchor [`ledger/export.py:18`](https://github.com/example/ledger/blob/0eb283dfe715341548387bf65af857affedf5dfa/ledger/export.py?plain=1#L18)

<!-- review-run head=0eb283dfe715341548387bf65af857affedf5dfa base-ref=main base-sha=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab merge-base=2301c83ee0b2ba0248fe3d2d1f6cd481963545ab workflow=v5b-25 packet_context=02f8e5cc19a99022c291144b2ce7827adcebedb35f8948a16f0b72feed469ced supplied_inputs=no issues=example/ledger#3 coverage=complete -->

## Run

Head, base, merge-base, workflow, packet identity, issues and coverage are in the run trailer above.

- Repository: `example/ledger`
- Target: pull-request
- Merged: no

## Line comments

The full body of each line-anchored item the summary indexes.

### `ledger/export/formula-leading-description`

**[P2] [must-fix] Prevent formula execution from exported descriptions**

**Triggers when:** A valid ledger entry has a description beginning with `=`, such as `=1+1`, and an accountant opens its CSV statement in a spreadsheet.

**Impact:** The description is emitted as a formula cell, so the spreadsheet evaluates it instead of displaying the recorded text. The CLI reproduces `2026-09-02,=1+1,-4.50,95.50` for such an entry.

**Change:** Neutralize formula-leading descriptions at the CSV export boundary for spreadsheet use, while preserving the required round-trip behavior for commas, quotes, and newlines.

<!-- finding id=ledger/export/formula-leading-description head=0eb283dfe715341548387bf65af857affedf5dfa priority=P2 action=must-fix blocking=true kind=security -->

## Requirements

- `issue-3/acceptance-criterion-1` (acceptance): met. ledger/cli.py:13,35,44; focused CLI check confirms CSV selection and default text
- `issue-3/acceptance-criterion-2` (acceptance): met. ledger/export.py:10,17; tests/test_export.py:17-20
- `issue-3/acceptance-criterion-3` (acceptance): met. ledger/statement.py:7-20 and ledger/export.py:18; tests/test_export.py:22-24
- `issue-3/acceptance-criterion-4` (acceptance): met. ledger/export.py:16-18; tests/test_export.py:22-24; focused CLI check confirms a newline, comma, and quote round-trip through csv.reader
- ``pr-body/"reuses `statement_rows`"`` (supporting): met. ledger/export.py:8,18

## File coverage

- `ledger/cli.py`: reviewed
- `ledger/export.py`: reviewed
- `tests/test_export.py`: reviewed

## Check evidence

- `python3 -m unittest discover -s tests -v` at `0eb283dfe715341548387bf65af857affedf5dfa`: reviewer-executed, 16 tests passed; run from repository root with bytecode writes disabled and TMPDIR under the private directory
- `python3 /home/jack/.cache/rc357x/root/publishable/work/review/check_csv.py` at `0eb283dfe715341548387bf65af857affedf5dfa`: reviewer-executed, CLI CSV and text assertions passed; formula-leading cell reproduced; input and temporary file kept in the private directory

## Verification

- Allowance: initial batch spent, follow-up unspent.
- Batch `initial` (initial), `foreground codex exec -m gpt-6-sol -c model_reasoning_effort=high; awaited exit 0`: bundle `/home/jack/.cache/rc357x/root/publishable/work/review/initial-v2`, raw return `/home/jack/.cache/rc357x/root/publishable/work/review/initial-return/raw-return.json`, accounting `/home/jack/.cache/rc357x/root/publishable/work/review/initial-v2/accounting.json`.
- Candidate `ledger/export/formula-leading-description`, trigger `must-fix`, batch `initial`: confirmed.

## Routed

- Unresolved: none.
- Disputed: none.

## Artifacts

- record: `/home/jack/.cache/rc357x/root/publishable/work/review/record.json`
- payload: `/home/jack/.cache/rc357x/root/publishable/work/review/payload.json`
- batch: `/home/jack/.cache/rc357x/root/publishable/work/review/batch.json`
- composition: `/home/jack/.cache/rc357x/root/publishable/work/review/composition.json`
- packet: `/home/jack/.cache/rc357x/root/publishable/work/review/packet.json`
- private_dir: `/home/jack/.cache/rc357x/root/publishable/work/review`
- store: `/home/jack/.cache/rc357x/root/publishable/work/review/review-context.json`
- skill_root: `/home/jack/.cache/rc357x/skill`
