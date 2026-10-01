**Changes Requested (advisory)** — 1 must-fix finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix the DatePicker widget so its displayed value updates to the just-selected day on the first click for users in positive-UTC-offset timezones (issue #9129), instead of showing the previous day until the same date is selected a second time.

**Issue fit:** Met — direct execution confirms the round-trip display is now correct for UTC+ users (e.g. `Europe/Paris`, `Pacific/Auckland`). The PR's other checklist items (tests added, release-doc entry) are template boilerplate naming no separate checkable outcome; tests were added in later commits, and no release-doc entry is required since no public API or feature was added.

**Coverage:** Complete merge-base diff reviewed (`bokehjs/src/lib/models/widgets/date_picker.ts`, `tests/integration/widgets/test_datepicker.py`); Python-side date serialization (`bokeh/core/property/datetime.py`, `bokeh/util/serialization.py`) inspected as a risk-led read; the 3 new Selenium integration tests traced by execution-semantics (setup, call, assertions) — none exercises the regression below and none is suspicious. The project's Selenium suite and build are unavailable offline in this run, so their execution is unavailable, not a pass.

**Reviewed:** `36549bca3a63d581f7b68d08054a7813c1e6a499` against merge-base `ccb4bcb4c2b841d89b0e88303a97bf4604a5795f`.

## Findings

- [P1] [must-fix] Fix reintroduces off-by-one date for negative-UTC-offset users — anchor [`bokehjs/src/lib/models/widgets/date_picker.ts:82-83`](https://github.com/bokeh/bokeh/blob/36549bca3a63d581f7b68d08054a7813c1e6a499/bokehjs/src/lib/models/widgets/date_picker.ts?plain=1#L82-L83)

<!-- review-run head=36549bca3a63d581f7b68d08054a7813c1e6a499 base-ref=master base-sha=ccb4bcb4c2b841d89b0e88303a97bf4604a5795f merge-base=ccb4bcb4c2b841d89b0e88303a97bf4604a5795f workflow=v5b-10 context=67da918baa5c99b51074a5c2571c86b72d41fbd5a85a7413003e00d89cf65a51 issues=bokeh/bokeh#9129 coverage=complete -->

---

### Finding: `bokehjs/src/lib/models/widgets/date_picker.ts:82-83`

**[P1] [must-fix] Fix reintroduces off-by-one date for negative-UTC-offset users**

**Triggers when:** A `DatePicker` is given an explicit `value`, `min_date`, or `max_date` and is viewed in a browser whose local timezone is behind UTC (any US, Canadian, or South American zone, `Pacific/Honolulu`, etc.).

**Impact:** `_unlocal_date` now shifts every input `Date` by `getTimezoneOffset()` before reading its calendar day. The initial `value`/`min_date`/`max_date` always arrive as a UTC-midnight timestamp (Bokeh's Python `Date` property serializes any date that way), so for a positive offset this shift pushes the timestamp into the previous UTC day before the day is read. The widget's initial displayed value and its effective selectable range are silently one calendar day earlier than configured, for the entire western hemisphere and much of the Pacific — the same class of bug issue #9129 reports, now on the opposite side of UTC.

**Change:** In `_unlocal_date`, only apply the timezone-offset shift to a `Date` that represents local midnight (the value Pikaday's `onSelect` produces before the round trip through `toDateString()`); keep the UTC-midnight-safe `date.toISOString().substr(0,10)` extraction — this function's own merge-base behavior — for `defaultDate`, `minDate`, and `maxDate`.

<!-- finding id=bokehjs/date-picker-unlocal-date-negative-offset-regression head=36549bca3a63d581f7b68d08054a7813c1e6a499 priority=P1 action=must-fix blocking=true kind=bug -->
