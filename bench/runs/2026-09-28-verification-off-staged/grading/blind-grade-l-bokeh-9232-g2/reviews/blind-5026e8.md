# Review blind-5026e8

### Item 1
Location: bokehjs/src/lib/models/widgets/date_picker.ts:82-83
Claim: Guard `_unlocal_date`'s new offset shift to reparsed local-midnight inputs. A `DatePicker`'s `min_date`, `max_date`, or an unselected initial `value` is rendered in a browser whose local time zone lags UTC (a positive `getTimezoneOffset()`, e.g. `TZ=America/New_York`); those properties always arrive from Python as UTC-midnight epoch-ms timestamps.
Consequence: The new `getTimezoneOffset`/`setTime` lines subtract that offset unconditionally, shifting the UTC-midnight timestamp into the previous UTC day before `toISOString()` reads the calendar date, so the widget renders `min_date`, `max_date`, and the initial date one day earlier than the caller set; the merge-base code read the same input correctly.
Fix: Only apply the offset correction when `date` is not already at UTC midnight, e.g. guard the two new lines behind `if (date.getUTCHours() || date.getUTCMinutes() || date.getUTCSeconds())`, so wire-format UTC-midnight values stay untouched while the reparsed local-midnight round trip from `_on_select` still gets corrected.

### Item 2
Location: (no file)
Claim: `_unlocal_date` mutates its `date` parameter in place via `setTime`, which is only safe because both call sites pass a freshly constructed `Date` that nothing else reads afterward.
Consequence: bokehjs/src/lib/models/widgets/date_picker.ts:68-71,83.
Fix: —
