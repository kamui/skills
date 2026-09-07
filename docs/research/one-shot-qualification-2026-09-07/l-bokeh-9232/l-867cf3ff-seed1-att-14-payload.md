# Review payload — `bokeh/bokeh#9232` (would-be publication, retrospective mode: publication disabled)

Posting identity: `kamui`. Event: `COMMENT`. This review was never published; it is rendered here exactly as `scripts/validate_review.py --emit-batch` would have submitted it in one forge-native review call, had publication been authorized.

## Summary (review body)

**Changes Requested (advisory)** — 1 must-fix finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix DatePicker's displayed value being one day behind the selected date for users in UTC+ timezones (issue #9129) by adjusting `_unlocal_date`'s timezone handling, and add an integration-test scaffold for the widget.

**Issue fit:** Partial — the reported UTC+ after-selection symptom is fixed, but the same change introduces a symmetric one-day-early regression for UTC-negative timezones on the initial value and on `min_date`/`max_date`, which are never re-derived through the corrected code path.

**Coverage:** Complete merge-base diff reviewed (2 files, +104/-2); Python-side date serialization (`bokeh/util/serialization.py`, `bokeh/core/property/datetime.py`, `bokeh/core/json_encoder.py`) and sibling integration tests inspected; behavior reproduced with Node under multiple `TZ` settings.

**Reviewed:** `36549bca3` against merge-base `ccb4bcb4`.

## Findings

- [P1] [must-fix] Restore correct date display for timezones behind UTC — anchor [`bokehjs/src/lib/models/widgets/date_picker.ts:82-83`](https://github.com/bokeh/bokeh/blob/36549bca3a63d581f7b68d08054a7813c1e6a499/bokehjs/src/lib/models/widgets/date_picker.ts?plain=1#L82-L83)

## Observations

- `_unlocal_date` mutates its `date` parameter in place via `date.setTime(...)` rather than operating on a copy, though all three current call sites pass a freshly constructed `Date` so nothing observes the mutation today. Evidence: `bokehjs/src/lib/models/widgets/date_picker.ts:78-83`.

<!-- review-run head=36549bca3a63d581f7b68d08054a7813c1e6a499 base-ref=master base-sha=ccb4bcb4c2b841d89b0e88303a97bf4604a5795f merge-base=ccb4bcb4c2b841d89b0e88303a97bf4604a5795f workflow=v5b-1 context=9ce7772c753e38225d78d80e2051b0392b6f3d727d0e3d5e217b78ba72c338ff issues=bokeh/bokeh#9129 coverage=complete -->

## Line comment 1 of 1 — `bokehjs/src/lib/models/widgets/date_picker.ts:82-83` (RIGHT)

**[P1] [must-fix] Restore correct date display for timezones behind UTC**

**Triggers when:** A user whose browser timezone is behind UTC (`getTimezoneOffset() > 0`, e.g. `America/Los_Angeles`) loads a document whose `DatePicker.value`, `min_date`, or `max_date` was set from Python; these arrive as a UTC-midnight timestamp (`bokeh/util/serialization.py:183-184`), and `min_date`/`max_date` are never reassigned any other way.

**Impact:** `_unlocal_date` now subtracts a positive `getTimezoneOffset()` from that UTC-midnight instant, rolling the displayed date and the selectable min/max bounds back one calendar day. This reintroduces the same class of bug #9129 reported, now for UTC-negative zones -- including PST, the zone this fix was manually verified in, because that manual test exercised only the after-selection path.

**Change:** In `_unlocal_date`, only apply the `getTimezoneOffset()` correction to a `Date` parsed from the client-side `toDateString()` round trip; derive the calendar day directly from `getUTCFullYear()/getUTCMonth()/getUTCDate()` when the input already represents a UTC-midnight instant.

**Source:** Issue #9129.

<!-- finding id=bokehjs/date-picker-west-of-utc-regression head=36549bca3a63d581f7b68d08054a7813c1e6a499 priority=P1 action=must-fix blocking=true kind=bug -->
