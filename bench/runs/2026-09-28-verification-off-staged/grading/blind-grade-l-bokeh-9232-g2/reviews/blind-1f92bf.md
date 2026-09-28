# Review blind-1f92bf

### Item 1
Location: bokehjs/src/lib/models/widgets/date_picker.ts:82-83
Claim: Skip the offset shift for dates that are already absolute timestamps. A browser west of UTC (e.g. America/New_York, America/Sao_Paulo) renders a DatePicker whose value, min_date, or max_date came from Python, e.g. `DatePicker(value=datetime.date.today())` -- issue #9129's own repro.
Consequence: Python encodes those fields as an absolute UTC-midnight timestamp (bokeh/util/serialization.py:184, wired into JSON encoding at bokeh/core/json_encoder.py:186), which `toISOString()` already read correctly pre-fix. The newly added offset subtraction now shifts that instant into the prior UTC day, so the shown date -- and the min/max bounds, which have no other producer -- are one calendar day early.
Fix: Apply the offset shift only to the locally-parsed string `_on_select` produces; for a value that is already an absolute timestamp, read `getUTCFullYear`/`getUTCMonth`/`getUTCDate` directly instead of shifting and re-reading local `toISOString()`.

### Item 2
Location: (no file)
Claim: test_js_on_change_executes and test_server_on_change_round_trip only distinguish pre-fix from post-fix `_unlocal_date` behavior when the runner's TZ has a nonzero offset; .travis.yml sets no TZ, so under a UTC runner both tests pass identically whether or not the timezone fix (or this regression) is present.
Consequence: tests/integration/widgets/test_datepicker.py; .travis.yml has no TZ directive; node repro shows old==new="Fri Sep 20 2019" at TZ=UTC for both the string and numeric-timestamp paths.
Fix: —
