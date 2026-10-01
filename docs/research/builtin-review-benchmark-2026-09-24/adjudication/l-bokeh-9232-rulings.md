# Rulings: bokeh/bokeh#9232 (head 36549bca, merge-base ccb4bcb4)

## NC-1: duplicate of GT-l1

**Claim.** East of UTC, `_unlocal_date` adds the local offset to a non-midnight Python datetime. This pushes it past UTC midnight, so the widget shows or limits to the next day.

### 1. Is it true at the head? Yes, at the algorithm level

Code I read:
- `bokehjs/src/lib/models/widgets/date_picker.ts:78-87` at the head: the PR adds `date.setTime(date.getTime() - date.getTimezoneOffset()*60000)` before the existing `toISOString().substr(0,10)`.
- `bokeh/util/serialization.py` `convert_datetime_type`: a datetime becomes `(obj.replace(tzinfo=None) - DT_EPOCH)` ms. The time of day is kept and the value is treated as UTC.
- `bokeh/core/property/datetime.py`, `Date`:
  - `validate` accepts any `datetime.date`, and `datetime` is a subclass of it.
  - `transform` only converts numbers and strings.
  - The docstring says "Accept Date (but not DateTime) values."
- The PR's own tests pass `max_date=datetime.utcnow()`.

Scratch file `clone-work/nc1.js` holds verbatim copies of the old and new function bodies. I ran:

```
for tz in UTC Europe/Paris Asia/Tokyo Pacific/Auckland America/New_York America/Los_Angeles; do TZ=$tz node clone-work/nc1.js; done
```

Relevant output (full output shows every UTC case unchanged):

```
Europe/Paris         datetime(2019,9,20,23,30)    old: Fri Sep 20 2019  new: Sat Sep 21 2019
Asia/Tokyo           datetime(2019,9,20,23,30)    old: Fri Sep 20 2019  new: Sat Sep 21 2019
Asia/Tokyo           datetime(2019,9,20,20,0)     old: Fri Sep 20 2019  new: Sat Sep 21 2019
Pacific/Auckland     datetime(2019,9,20,12,0)     old: Fri Sep 20 2019  new: Sat Sep 21 2019
Pacific/Auckland     datetime(2019,9,20,20,0)     old: Fri Sep 20 2019  new: Sat Sep 21 2019
Pacific/Auckland     datetime(2019,9,20,23,30)    old: Fri Sep 20 2019  new: Sat Sep 21 2019
America/New_York     datetime(2019,9,20,0,0)      old: Fri Sep 20 2019  new: Thu Sep 19 2019   <- GT-l1
America/Los_Angeles  datetime(2019,9,20,3,0)      old: Fri Sep 20 2019  new: Thu Sep 19 2019   <- GT-l1
```

At the merge-base ("old") every case gives Fri Sep 20.

### 2. Was it introduced by this PR? Yes

The only change is the added offset subtraction.

### 3. Is it already in the register? Yes, it is GT-l1

The mechanism is the same:
- GT-l1's title says the correction "is valid only for local-midnight input". Subtracting the local offset from a UTC-anchored Python instant moves it into the wrong UTC day.
- For UTC-midnight input, only western zones cross a day boundary, and they go backwards.
- For a late time of day, eastern zones cross forwards. The fault is the same; only where it shows up differs.

GT-l1's required outcome already covers the case: "The displayed calendar day for value, min_date and max_date must equal the day the model holds, in every timezone, for … a Python-supplied date". Its named remedy, calendar-value (ISO date string) serialization as in #9509, removes this case too.

The register says "east-of-UTC and UTC cases stay correct". That describes the midnight demonstration only; it does not narrow the outcome.

Record this as an extra GT-l1 manifestation: *east of UTC, a Python datetime with a late time of day (e.g. `max_date=datetime.utcnow()` late in the UTC day) displays or limits to the next day.*

### 4. Materiality

It is material only as part of GT-l1. I ran a GitHub API search for DatePicker issues created 2019-10-01..2020-03-01. It returned only #9494 (EST, western), #9702 (DateRangeSlider) and #9509 (Flatpickr), so there is no separate downstream report of the eastern, non-midnight variant.

### 5. Counter-arguments

**For a separate defect.** A narrow patch could skip the correction only for exact UTC-midnight values. That would fix GT-l1's demonstrated western cases and leave this one broken, which suggests two defects.

I reject this. Such a patch fails GT-l1's outcome ("in every timezone", "a Python-supplied date"). A scorer should grade it as `partial` fix sufficiency, not treat it as a second defect.

**For not-material.** The `Date` docstring excludes DateTime, so this input could be called out of scope.

I don't rule on that basis. `validate` accepts datetime, and the PR's own tests use `datetime.utcnow()`, so the input is reachable and used. Scope does not change the outcome here, since the case is folded into GT-l1.

**Limits.** This is an algorithm-level re-implementation only. I did not run a browser or the compiled bokehjs.
