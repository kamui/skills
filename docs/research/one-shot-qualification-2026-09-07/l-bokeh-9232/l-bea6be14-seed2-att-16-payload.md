# Review payload — `bokeh/bokeh#9232` (rendered, not published)

Retrospective review of a merged pull request; publication is disabled for this run.
This is the review exactly as it would have been submitted as one forge-native review
(`event: COMMENT`, `commit_id: 36549bca3a63d581f7b68d08054a7813c1e6a499`) had publication been authorized.

## Summary (review body)

**Changes Requested (advisory)** — 1 must-fix finding, 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix the DatePicker widget displaying a date one day earlier than the one the user selected, for users in UTC+ timezones, by adjusting `_unlocal_date` to compensate for the browser's local-to-UTC offset before extracting the calendar date; adds an integration-test shell for the widget.

**Issue fit:** Met — bokeh/bokeh#9129's reported round-trip display bug is fixed in every timezone tested (verified by execution across 7 IANA zones spanning UTC−9:30 to UTC+14). The same diff introduces a new, distinct regression on a different code path through the same function (see the must-fix finding below).

**Coverage:** Complete merge-base diff reviewed (2 files: `bokehjs/src/lib/models/widgets/date_picker.ts`, `tests/integration/widgets/test_datepicker.py`); both changed files reviewed in full. Focused execution: a scratch Node reproduction of `_unlocal_date` (old vs. new) was run across 7 IANA timezones (UTC, Europe/Paris, Europe/London, Pacific/Kiritimati, America/Los_Angeles, Pacific/Marquesas, Asia/Kolkata) — pass/fail as described in the findings below. The Selenium integration tests this PR adds could not be executed (no browser/npm install available in this environment); traced by code instead, per the rubric's Changed Tests section.

**Reviewed:** `36549bca3` against merge-base `ccb4bcb4`.

## Observations

- `_unlocal_date` mutates its `date` argument in place via `date.setTime(...)` rather than operating on a copy; all three current call sites in `render()` construct a fresh `Date` for this argument, so no observable effect results today. Evidence: `bokehjs/src/lib/models/widgets/date_picker.ts:68,70-71,82-83`.

## Findings

- [P1] [must-fix] Fix the negative-UTC-offset regression in `_unlocal_date` — anchor [`bokehjs/src/lib/models/widgets/date_picker.ts:82-83`](https://github.com/bokeh/bokeh/blob/36549bca3a63d581f7b68d08054a7813c1e6a499/bokehjs/src/lib/models/widgets/date_picker.ts?plain=1#L82-L83); fix [`bokehjs/src/lib/models/widgets/date_picker.ts:82`](https://github.com/bokeh/bokeh/blob/36549bca3a63d581f7b68d08054a7813c1e6a499/bokehjs/src/lib/models/widgets/date_picker.ts?plain=1#L82)
- [P3] [consider] Vary timezone in the new DatePicker integration tests — anchor [`tests/integration/widgets/test_datepicker.py:52-70`](https://github.com/bokeh/bokeh/blob/36549bca3a63d581f7b68d08054a7813c1e6a499/tests/integration/widgets/test_datepicker.py?plain=1#L52-L70)

<!-- review-run head=36549bca3a63d581f7b68d08054a7813c1e6a499 base-ref=master base-sha=ccb4bcb4c2b841d89b0e88303a97bf4604a5795f merge-base=ccb4bcb4c2b841d89b0e88303a97bf4604a5795f workflow=v5b-10 context=67da918baa5c99b51074a5c2571c86b72d41fbd5a85a7413003e00d89cf65a51 issues=bokeh/bokeh#9129 coverage=complete -->

## Inline comments

### bokehjs/src/lib/models/widgets/date_picker.ts:82-83 (side RIGHT)

**[P1] [must-fix] Fix the negative-UTC-offset regression in `_unlocal_date`**

**Triggers when:** A browser with a negative UTC offset (for example `America/Los_Angeles` or `Pacific/Marquesas`) renders a `DatePicker` whose `value`, `min_date`, or `max_date` was set from Python — the ordinary `DatePicker(value=datetime.date.today())` construction from the issue's own repro script — before any user selection has occurred.

**Impact:** `_unlocal_date` now shifts every input `Date` by `getTimezoneOffset()` before extracting its calendar date. That shift is only correct when the input was built by re-parsing `toDateString()`'s local-midnight string (the post-selection round trip this PR targets). For the property's original UTC-anchored timestamp (the initial/programmatic value, or `min_date`/`max_date`), the same shift pushes the calendar date backward by one day for every timezone behind UTC. The picker's initial default date, and its min/max bounds, then display one calendar day earlier than the value Python sent — the same class of off-by-one-day defect this PR sets out to fix, now affecting the opposite half of the globe on a different code path through the same function.

**Change:** In `bokehjs/src/lib/models/widgets/date_picker.ts`, only apply the local-to-UTC compensation when the input `Date` came from re-parsing `toDateString()`'s local-midnight string; skip it when the input is the property's original UTC-anchored timestamp. For example, have `_on_select` store a UTC-midnight timestamp (`Date.UTC(date.getFullYear(), date.getMonth(), date.getDate())`) instead of a bare local date string, so both call sites' input already share one UTC-anchored representation and `_unlocal_date` no longer needs to guess which kind of `Date` it received.

<!-- finding id=bokehjs/date-picker-unlocal-date-negative-offset head=36549bca3a63d581f7b68d08054a7813c1e6a499 priority=P1 action=must-fix blocking=true kind=bug fix=bokehjs/src/lib/models/widgets/date_picker.ts:82 -->

### tests/integration/widgets/test_datepicker.py:52-70 (side RIGHT)

**[P3] [consider] Vary timezone in the new DatePicker integration tests**

**Triggers when:** CI or a local run executes `tests/integration/widgets/test_datepicker.py` in its ambient, unset timezone — neither `.travis.yml` nor `.appveyor.yml` sets `TZ`, and none of the three new tests sets it either.

**Impact:** None of the tests vary timezone, so the suite cannot regression-protect the timezone-dependent behavior this PR fixes. `test_js_on_change_executes` and `test_server_on_change_round_trip` only assert the value after a click; neither they nor `test_basic` assert the picker's initial displayed date at all. A future regression in `_unlocal_date` — including the negative-offset regression flagged separately in this review — would pass this suite regardless of which zone CI happens to run in.

**Change:** Add at least one case that fixes the browser/test-runner's zone to a positive-UTC-offset value and one to a negative-UTC-offset value, and assert both the picker's initial displayed date and its value after a selection in each, so a future change to `_unlocal_date` is caught regardless of which zone CI happens to run in.

Closing this without action is a correct response.

<!-- finding id=bokehjs/date-picker-integration-tests-timezone-coverage head=36549bca3a63d581f7b68d08054a7813c1e6a499 priority=P3 action=consider blocking=false kind=maintainability -->
