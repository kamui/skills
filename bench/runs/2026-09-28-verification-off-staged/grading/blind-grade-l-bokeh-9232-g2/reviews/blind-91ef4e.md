# Review blind-91ef4e

### Item 1
Location: bokehjs/src/lib/models/widgets/date_picker.ts:82-83
Claim: _unlocal_date now mis-shifts UTC-midnight timestamps in negative-UTC-offset zones. Construct `DatePicker(value=datetime.date.today())` (the exact reproduction from the originating issue) or set `min_date`/`max_date` from Python, then render the widget while the browser's local timezone has a negative UTC offset (e.g. `America/New_York`, `America/Los_Angeles`, any Americas zone).
Consequence: The picker's initial or programmatically-set displayed date (and the effective min/max bounds) is silently rendered one calendar day before the value the caller actually set, for every user in a negative-UTC-offset timezone. This is the same class of off-by-one-day defect issue #9129 reports, now moved onto the opposite set of timezones and onto the initial-value path instead of only the post-selection path.
Fix: Do not apply the same `getTimezoneOffset()` subtraction to both input shapes `_unlocal_date` receives. `this.model.value`/`min_date`/`max_date` set from Python arrive as a UTC-midnight instant (`bokeh/util/serialization.py`'s `convert_datetime_type` serializes a `datetime.date` as milliseconds since epoch computed against a UTC epoch, and the JS-side property is untyped `p.Any`), while `_on_select`'s `date.toDateString()` round trip arrives as a local-midnight instant. Distinguish the two call sites in `bokehjs/src/lib/models/widgets/date_picker.ts:63-72` (for example by normalizing `_on_select` to emit the same UTC-midnight representation the server uses) so `_unlocal_date` only ever needs to correct one input shape, instead of adding back the local offset unconditionally.

### Item 2
Location: (no file)
Claim: The new integration tests in `tests/integration/widgets/test_datepicker.py` never vary `TZ` and only assert against the CI clock's own timezone, so even if the Selenium suite were run here it would not have exercised (and could not have caught) this change's timezone-direction-dependent regression.
Consequence: tests/integration/widgets/test_datepicker.py:119-176 sets no TZ and asserts fixed literals such as `'Mon Sep 16 2019'`; bokehjs/src/lib/models/widgets/date_picker.ts:82-83 is the timezone-sensitive logic.
Fix: —
