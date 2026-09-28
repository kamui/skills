# Review blind-f3585b

### Item 1
Location: bokehjs/src/lib/models/widgets/date_picker.ts:82-83
Claim: Stop shifting server-supplied dates across the day boundary. A user whose browser timezone has a positive `getTimezoneOffset()` (west of UTC, e.g. `America/New_York` or `America/Los_Angeles` — most of the Americas) opens a `DatePicker` whose `value`, `min_date`, or `max_date` came from Python as a `datetime.date`. `bokeh/util/serialization.py:184` (`convert_datetime_type`) serializes that to an exact UTC-midnight timestamp, which is precisely the originating issue's own repro, `DatePicker(value=datetime.date.today())`.
Consequence: `_unlocal_date` now unconditionally subtracts `getTimezoneOffset()*60000` ms before reading the calendar day. For a UTC-midnight instant and a positive offset this rolls the instant back into the previous UTC day, so `defaultDate`/`minDate`/`maxDate` display and bound one day earlier than the real value. Node trace on `Date.UTC(2019,0,15,0,0,0)` under `TZ=America/New_York` (and `America/Los_Angeles`): merge-base prints `Tue Jan 15 2019`, head prints `Mon Jan 14 2019` — the same class of off-by-one-day bug this PR fixes, now hitting the opposite hemisphere of timezones on every initial render and on `min_date`/`max_date` always.
Fix: Apply the offset correction only to a date built from the post-selection local-midnight string (the `_on_select` round trip via `date.toDateString()`), not to a date that already denotes an exact instant supplied by the server, so the calendar day for `defaultDate`/`minDate`/`maxDate` survives unmodified in every timezone.

### Item 2
Location: tests/integration/widgets/test_datepicker.py:52-70
Claim: Exercise _unlocal_date at a non-UTC offset in the new tests. The Selenium suite runs with no `TZ` override, so it executes at the host's default offset (UTC in ordinary CI).
Consequence: At a UTC offset of zero, `_unlocal_date`'s merge-base and head logic are byte-identical (confirmed by Node trace), so `test_js_on_change_executes` and `test_server_on_change_round_trip` pass identically whether or not the fix -- or the regression above -- is present, giving no regression protection for the defect this PR addresses.
Fix: Add a case, or parametrize the existing ones, to run with `TZ` set to a non-UTC offset in each direction (e.g. `Europe/Paris` and `America/New_York`) and assert the displayed/selected date there too.

### Item 3
Location: (no file)
Claim: `_unlocal_date` mutates its `date` argument in place via `setTime`, which is harmless today only because every call site passes a freshly constructed `Date`.
Consequence: bokehjs/src/lib/models/widgets/date_picker.ts:68-71,83.
Fix: —
