# Review blind-ba1acb

### Item 1
Location: bokehjs/src/lib/models/widgets/date_picker.ts:82-83
Claim: Don't re-offset already-correct UTC-midnight dates in _unlocal_date. `_unlocal_date` now unconditionally subtracts `date.getTimezoneOffset()*60000` before reading the calendar day. `this.model.value` arrives on first render as the numeric UTC-midnight timestamp Bokeh's `Date` property serializes (`bokeh/util/serialization.py:convert_datetime_type`), and `min_date`/`max_date` always arrive that way — never through the toDateString() string round-trip the offset math is meant to cancel.
Consequence: For any user in a timezone behind UTC (America/New_York, Pacific/Honolulu, etc.), subtracting a positive `getTimezoneOffset()` pushes that UTC-midnight instant into the previous UTC day, so the picker's initial `defaultDate` and its `minDate`/`maxDate` bounds show the day before the one actually configured. Reproduced in Node: a value/min_date/max_date of July 30 renders as 'Mon Jul 29 2019' under TZ=America/New_York and TZ=Pacific/Honolulu, both before and independent of any user click.
Fix: In `bokehjs/src/lib/models/widgets/date_picker.ts`, apply the `getTimezoneOffset()` correction only to a `Date` that was constructed by parsing a local-time string (the `_on_select` → render round trip); leave a `Date` built from a numeric UTC-midnight timestamp untouched, since `toISOString().substr(0,10)` already reads the correct day for it without any offset.

### Item 2
Location: (no file)
Claim: The three added integration tests all run in whatever single timezone the executing machine/CI uses and never vary TZ, so as written they provide no evidence for or against either the fixed UTC+ path or the regression above.
Consequence: tests/integration/widgets/test_datepicker.py (whole file, no TZ manipulation).
Fix: —
