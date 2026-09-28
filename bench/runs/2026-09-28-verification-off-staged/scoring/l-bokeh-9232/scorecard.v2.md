# Scorecard: l-bokeh-9232, mapping v2

Register v1 (f5b761a87af4), rubric v1, scored at 2026-09-28T13:07:08Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 fab9a500c1f043869fb15e6750e3abf3d26982c49e521b6684c9a447a0afa827; session 6ed930ed-1e81-4d93-82c4-5de9526d10e5; read audit clean.

## att-005 (review-code-sonnet-high-enforced-x394-control), blind-91ef4e

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-l1`, fix sufficient, priority error False, group none. Quotes: 'mis-shifts UTC-midnight timestamps in negative-UTC-offset zones ... set min_date/max_date from Python ... rendered one calendar day before the value the caller actually set'; fix explains Python values 'arrive as a UTC-midnight instant (convert_datetime_type ... p.Any)' while '_on_select's date.toDateString() round trip arrives as a local-midnight instant'. Same mechanism as GT-l1. Fix: normalize _on_select to emit the same UTC-midnight representation the server uses so _unlocal_date only handles one input shape 'instead of adding back the local offset unconditionally' - removes the anchor ambiguity at the source, restoring correct display for both paths in every zone; consistent with required_outcome. (Calling west-of-UTC 'negative offset' is the conventional UTC-offset sign, not an error.)
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: 'The new integration tests ... never vary TZ ... could not have caught this change's timezone-direction-dependent regression.' Accurate coverage observation; register non_defects rule the added Selenium tests internally correct and note that they do not cover GT-l1 (no TZ variation, no assertion on initial value/min/max). grep finds no TZ in clone/.travis.yml. A test-gap remark, not a separately demonstrated defect.

## att-006 (review-code-sonnet-high-enforced-verification-off), blind-a6e445

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-l1`, fix sufficient, priority error False, group none. Quotes: 'Bokeh serializes a Python date as UTC-midnight epoch ms ... _unlocal_date ... now subtracts date.getTimezoneOffset() from every date it receives ... under TZ=America/New_York turns a 2019-09-20 UTC-midnight input into Thu Sep 19 2019: the shown default date and the min/max calendar boundary are off by one day'. Matches GT-l1 mechanism and demonstration. Fix: serialize the _on_select selection in a UTC-safe form 'so _unlocal_date can read UTC date components directly from server-supplied min_date/max_date/value without a blanket offset subtraction' - removes the ambiguity at the source for both arrival paths; satisfies required_outcome.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: 'test_basic ... asserts only the title label text and the absence of console errors ... never reads the picker's displayed date value'. True (tests/integration/widgets/test_datepicker.py:42-50), but register non_defects treat the tests' non-coverage as a gap, not a defect.

## att-016 (review-code-sonnet-high-enforced-verification-off), blind-ba1acb

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-l1`, fix sufficient, priority error False, group none. Quotes: 'this.model.value arrives on first render as the numeric UTC-midnight timestamp ... and min_date/max_date always arrive that way'; 'For any user in a timezone behind UTC ... pushes that UTC-midnight instant into the previous UTC day, so the picker's initial defaultDate and its minDate/maxDate bounds show the day before'. Same mechanism as GT-l1. Fix: 'apply the getTimezoneOffset() correction only to a Date that was constructed by parsing a local-time string (the _on_select -> render round trip); leave a Date built from a numeric UTC-midnight timestamp untouched' - anchor-aware correction, keeps the east fix, restores value/min/max in every zone.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: 'The three added integration tests all run in whatever single timezone ... never vary TZ'. Accurate coverage observation; register non_defects rule the added Selenium tests internally correct and note that they do not cover GT-l1 (no TZ variation, no assertion on initial value/min/max). grep finds no TZ in clone/.travis.yml. A test-gap remark, not a separately demonstrated defect.

## att-017 (review-code-sonnet-high-enforced-x394-control), blind-1f92bf

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-l1`, fix sufficient, priority error False, group none. Quotes: 'A browser west of UTC ... renders a DatePicker whose value, min_date, or max_date came from Python'; 'Python encodes those fields as an absolute UTC-midnight timestamp (bokeh/util/serialization.py:184 ...) ... The newly added offset subtraction now shifts that instant into the prior UTC day, so the shown date -- and the min/max bounds ... are one calendar day early.' Same mechanism as GT-l1 (date_picker.ts:82-83 unconditional getTimezoneOffset subtraction, render() lines 68-71). Fix: 'Apply the offset shift only to the locally-parsed string _on_select produces; for a value that is already an absolute timestamp, read getUTCFullYear/getUTCMonth/getUTCDate directly' - an anchor-aware correction that keeps the east-of-UTC fix and restores value/min_date/max_date in every zone, which is what required_outcome accepts.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: 'under a UTC runner both tests pass identically whether or not the timezone fix (or this regression) is present.' Accurate coverage observation; register non_defects rule the added Selenium tests internally correct and note that they do not cover GT-l1 (no TZ variation, no assertion on initial value/min/max). grep finds no TZ in clone/.travis.yml. A test-gap remark, not a separately demonstrated defect.

## att-026 (review-code-sonnet-high-enforced-x394-control), blind-5026e8

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-l1`, fix sufficient, priority error False, group none. Quotes: 'min_date, max_date, or an unselected initial value is rendered in a browser whose local time zone lags UTC ... those properties always arrive from Python as UTC-midnight epoch-ms timestamps'; 'subtract that offset unconditionally, shifting the UTC-midnight timestamp into the previous UTC day ... renders min_date, max_date, and the initial date one day earlier'. Matches GT-l1 mechanism and trigger exactly. Fix: guard the offset lines behind 'if (date.getUTCHours() || date.getUTCMinutes() || date.getUTCSeconds())' - anchor-aware: Python date values (UTC midnight) are left alone, while a local-midnight Date from _on_select's toDateString has nonzero UTC h/m in any non-UTC zone (and in UTC the correction is zero anyway), so both arrival paths display the held day in every zone without reintroducing the east-of-UTC bug. Heuristic, but satisfies required_outcome for date inputs.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: '_unlocal_date mutates its date parameter in place via setTime, which is only safe because both call sites pass a freshly constructed Date'. True (date_picker.ts:83) and the review itself notes it is safe; register non_defects rule this style only, no observable aliasing.

## att-027 (review-code-sonnet-high-enforced-verification-off), blind-f3585b

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-l1`, fix sufficient, priority error False, group none. Quotes: 'value, min_date, or max_date came from Python ... serializes that to an exact UTC-midnight timestamp'; '_unlocal_date now unconditionally subtracts getTimezoneOffset()*60000 ... rolls the instant back into the previous UTC day, so defaultDate/minDate/maxDate display and bound one day earlier'; Node trace NY/LA merge-base 'Tue Jan 15 2019' vs head 'Mon Jan 14 2019'. Matches GT-l1. Fix: 'Apply the offset correction only to a date built from the post-selection local-midnight string ... not to a date that already denotes an exact instant supplied by the server, so the calendar day ... survives unmodified in every timezone' - anchor-aware, satisfies required_outcome.
- item-1: `non-material`, fix n/a, priority error False, group none. Quote: 'At a UTC offset of zero, _unlocal_date's merge-base and head logic are byte-identical ... giving no regression protection'; suggests parametrizing TZ. Accurate coverage observation; register non_defects rule the added Selenium tests internally correct and note that they do not cover GT-l1 (no TZ variation, no assertion on initial value/min/max). grep finds no TZ in clone/.travis.yml. A test-gap remark, not a separately demonstrated defect. The proposed test improvement echoes the preexisting hint but does not assert a separate defect.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: '_unlocal_date mutates its date argument in place via setTime, which is harmless today'. True (date_picker.ts:83); register non_defects rule this style only with no observable aliasing.

## New candidates

None.
