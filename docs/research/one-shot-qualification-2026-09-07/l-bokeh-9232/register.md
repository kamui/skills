# Ground-truth register — bokeh/bokeh #9232

## Target

- Repository: `bokeh/bokeh`
- PR #9232, "Fixed issue of Datepicker displaying the wrong date for users in UTC+… timezones."
- Head SHA (pinned): `36549bca3a63d581f7b68d08054a7813c1e6a499`
- Merge-base: `ccb4bcb4c2b841d89b0e88303a97bf4604a5795f` (master)
- Merged: 2019-10-03T15:52:02Z by @bryevdv, authored by @madkopp
- Fixes issue #9129 ("Datepicker displayed value is not updating correctly")
- Diff at head vs. merge-base:
  - `bokehjs/src/lib/models/widgets/date_picker.ts`: 8 lines changed (`_unlocal_date` body)
  - `tests/integration/widgets/test_datepicker.py`: new file, 98 lines (Selenium integration tests)
- Commits in the PR: `472e4770` (the fix), `7aae927c` (var→const), `e92066d5` (drop `.idea/vcs.xml`), `4215c2d0` (test shell), `36549bca` (update tests, = pinned head)

## Verdict

**1 material defect** (`GT-l1`). The added integration test file is ruled separately below: it is internally correct but does not cover the defect and could not have caught it even in a non-UTC CI host.

## Defect register

### GT-l1 — `_unlocal_date`'s timezone correction is only valid for local-midnight input; it silently corrupts UTC-midnight input, shifting `value`/`min_date`/`max_date` back one day for every user west of UTC

**Location (at pinned head):** `bokehjs/src/lib/models/widgets/date_picker.ts`, function `_unlocal_date`, lines 78–87; called from `render()` at lines 68, 70, 71 on `this.model.value`, `this.model.min_date`, `this.model.max_date` respectively.

```ts
_unlocal_date(date: Date): Date {
  //Get the UTC offset (in minutes) of date (will be based on the timezone of the user's system).
  //Then multiply to get the offset in ms.
  //This way it can be used to recreate the user specified date, agnostic to their local systems's timezone.
  const timeOffsetInMS = date.getTimezoneOffset() * 60000
  date.setTime(date.getTime() - timeOffsetInMS)

  const datestr = date.toISOString().substr(0, 10)
  const tup = datestr.split('-')
  return new Date(Number(tup[0]), Number(tup[1])-1, Number(tup[2]))
}
```

**Expected behaviour / violated contract:** The function's own new comment states the requirement it must satisfy for every caller: it must "recreate the user specified date, agnostic to their local system's timezone." All three call sites in `render()` route through it, so the contract is "for any of `value`, `min_date`, `max_date`, display the calendar day the model actually holds, regardless of the viewer's timezone." It satisfies this only for one of the two anchor conventions those properties can carry.

**Mechanism.** `_unlocal_date` receives a JS `Date`, and the two possible ways such a `Date` can encode "a calendar day with no time" differ in what UTC instant they land on:
- *Local-midnight anchor*: the underlying instant is 00:00 in the **viewer's** zone. This is what `new Date(model.value)` produces when `model.value` is the plain string `_on_select` writes — `this.model.value = date.toDateString()` (e.g. `"Mon Sep 16 2019"`), which JS's non-ISO `Date` parser always interprets in **local** time.
- *UTC-midnight anchor*: the underlying instant is 00:00 **UTC**. This is what `new Date(model.value)` produces when `model.value`/`min_date`/`max_date` is the numeric millisecond timestamp Bokeh's Python side sends for any `Date`-typed property. Confirmed by reading `bokeh/util/serialization.py::convert_datetime_type` (at this head): for a `datetime.date`/`datetime.datetime`, it computes `(dt.datetime(*obj.timetuple()[:6]) - DT_EPOCH).total_seconds() * 1000`, i.e. it treats the naive `date`/`datetime` as if it were already UTC and returns ms-since-epoch — a UTC-midnight-anchored number, not an ISO string. `bokeh/core/json_encoder.py` routes every `Date`/`Datetime` property through this function. `DatePicker.value/min_date/max_date` are declared `p.Any` on the JS side (no further transform), so this raw number reaches `_unlocal_date` unchanged.

The fix added in this PR applies the same correction (`date.getTime() - getTimezoneOffset()*60000`) to both anchors. That correction is the exact fix for the local-midnight anchor (it is timezone-symmetric and produces the correct calendar day in every zone — verified below). Applied to the UTC-midnight anchor, it is wrong in the opposite direction from the original bug: it moves the effective instant backward by the local UTC offset for any timezone with a positive `getTimezoneOffset()` (i.e. every timezone strictly west of UTC), which can cross the UTC-midnight boundary into the previous calendar day.

**Trigger:** Any `DatePicker` whose `value`, `min_date`, or `max_date` is set from Python — the ordinary way any user of the widget sets these — and displayed in a browser whose system timezone is west of UTC (`Etc/GMT` and points west, e.g. `America/New_York`, `America/Los_Angeles`; anything with `getTimezoneOffset() > 0`). No user interaction is required; it manifests on the very first `render()`.

**Reproduction (this session, standalone Node reimplementation of the exact diff algorithm — see Reproduction section for the full harness and output):**

| TZ | Case A: local-midnight input (the `_on_select` round-trip this PR targets), intended 2019-07-30 | Case B: UTC-midnight input (the `value`/`min_date`/`max_date` anchor from Python), intended 2019-10-03 |
|---|---|---|
| Pacific/Auckland (UTC+13) | PRE=2019-07-29 (bug) → POST=**2019-07-30 (fixed)** | PRE=2019-10-03 (ok) → POST=**2019-10-03 (still ok)** |
| Europe/Paris (UTC+2) | PRE=2019-07-29 (bug) → POST=**2019-07-30 (fixed)** | PRE=2019-10-03 (ok) → POST=**2019-10-03 (still ok)** |
| UTC | PRE=2019-07-30 (ok) → POST=2019-07-30 (ok) | PRE=2019-10-03 (ok) → POST=2019-10-03 (ok) |
| America/New_York (UTC-5) | PRE=2019-07-30 (ok) → POST=2019-07-30 (ok) | PRE=2019-10-03 (ok) → POST=**2019-10-02 (REGRESSION)** |
| America/Los_Angeles (UTC-8) | PRE=2019-07-30 (ok) → POST=2019-07-30 (ok) | PRE=2019-10-03 (ok) → POST=**2019-10-02 (REGRESSION)** |

This is a faithful line-for-line re-implementation of the pre-fix and post-fix `_unlocal_date` bodies (identical algorithm, run under Node with `TZ` set), not a hypothetical.

**Demonstrated consequence (real-world, not just my reproduction):** Issue #9494, "[BUG] DatePicker display off-by-one in non-GMT timezone after upgrade to 1.4.0" (filed 2019-12-02, closed 2020-01-17 by PR #9509), reports exactly this: *"TimeZone: EST (Issue observed in EST but not in GMT)... if I update a DatePicker based on the value of another DatePicker, I get a different date (1 day previous to the selected date). If the browser is located in a GMT timezone then I do not observe the issue."* The reporter's minimal repro (`date_picker_b.value = new` inside an `on_change` callback on `date_picker_a`) round-trips the selected date through Python: `_on_select`'s string is coerced by `Date.transform` (`dateutil.parser.parse(value).date()`) back into a `datetime.date`, which is then re-serialized for `date_picker_b` via `convert_datetime_type` into a UTC-midnight-anchored timestamp — i.e. exactly the "Case B" input this defect mishandles, and exactly why it reproduces only in EST/west-of-UTC, never in GMT. The issue's body links directly to this PR's fix commit (`472e4770`) as the point the regression appeared. The maintainer (@bryevdv) later confirmed the root design flaw when closing it via PR #9509 ("Flatpickr"): *"now date values can only be expressed as ISO date strings, or `datetime.date` and nothing else (in particular no more datetime values which caused endless trouble with time zones)"*, and in review of that PR: *"I think ideally what should happen is for scalar `datetime.date` values to render as ISO datestrings... This solves the nonsense with datepicker and time zones."* PR #9509 fixes it by changing `Date`'s wire format from a timestamp to an ISO date string (eliminating the ambiguous anchor entirely) and replacing Pikaday/`_unlocal_date` outright with Flatpickr.

**Required corrective outcome:** Any sufficient fix must make the *displayed* calendar day for `value`, `min_date`, and `max_date` equal the calendar day the model actually holds, in every timezone, for both ways those properties can arrive at the widget (a freshly-typed/selected local date and a Python-supplied date). This can be reached either by making `_unlocal_date` (or its replacement) anchor-aware — i.e. only apply the offset correction to inputs it can establish are local-midnight-anchored — or, as upstream ultimately did, by removing the ambiguity at the source (serializing `Date`-typed properties as unambiguous calendar values, e.g. ISO date strings, rather than as UTC-instant timestamps that get reinterpreted through a local clock). A fix that "solves" the west-of-UTC regression by reintroducing the east-of-UTC bug does not satisfy this.

**Is this the behaviour change the PR promised, or an unintended error?** Distinct, unintended error. The PR's promised, tested, and demonstrably-achieved behaviour change is: users east of UTC (`getTimezoneOffset() < 0`) now see the correct day after selecting a date (Case A). That promise is kept — see the Case A row above holding for every zone, both east and west, with no regression. GT-l1 is a *side effect* of implementing that promise with a correction applied uniformly to a function whose input is not uniform in anchor convention; it strikes a different code path (Case B: the initial/programmatic `value`/`min_date`/`max_date`) that the reported bug (#9129) never touched and the PR's own tests never exercise.

## Reproduction

**Environment constraints.** This is a browser-integration bug (`bokehjs` TypeScript rendering + Selenium tests). The sandbox has no `node_modules` for `bokehjs` (would require a fresh `npm install` against the registry), no `selenium` Python package, and no `chromedriver`:
```
$ python3 -c "import selenium"          → ModuleNotFoundError: No module named 'selenium'
$ which chromedriver                    → not found
```
So the PR's own added tests (`tests/integration/widgets/test_datepicker.py`, marked `@pytest.mark.integration @pytest.mark.selenium`) cannot be executed in this environment at either the head or the merge-base commit (the file doesn't exist at the merge-base at all — it's new). I did not fabricate a pass/fail for them.

**What I ran instead:** a standalone Node re-implementation of `_unlocal_date`'s pre-fix and post-fix bodies (algorithm copied verbatim from the diff, not reinterpreted), executed under five `TZ` settings, in `/tmp/qual137/work/repro.js`:
```
$ node --version                                    # v24.19.0
$ for tz in "Pacific/Auckland" "Europe/Paris" "UTC" "America/New_York" "America/Los_Angeles"; do
    TZ=$tz node repro.js
  done
```
Output reproduced verbatim in GT-l1 above. Exit status 0 for all five runs; each run completes in well under 1s (pure computation, no I/O). This is not a test of the compiled `bokehjs` bundle, but it is an exact transcription of the two code bodies under diff — the only degrees of freedom are the `Date` inputs (chosen to model the two real input shapes analyzed from the Python serializer and the `_on_select` handler) and the host timezone, both of which are the entire content of the mechanism under review.

I could not additionally confirm this against a compiled `bokehjs` bundle or a live browser render (no network install path exercised — not attempted given the scope of this adjudication; noted as `unresolved` for that specific channel, though the algorithm-level reproduction above is direct and sufficient to establish the defect since the diff *is* the algorithm).

No JS unit test for `_unlocal_date` exists at either the merge-base or the head (`bokehjs/test/unit/models/widgets` has no date-picker file at this pin — checked via `git ls-tree`), so there is no pre-existing regression test whose pass/fail could be compared across the two commits.

## Not ground truth

Plausible-sounding objections that are **not** material defects:

- **"`_unlocal_date` mutates its `date` argument in place (`date.setTime(...)`), which is a side-effecting anti-pattern."** True as a style observation, but every call site (`render()`, lines 68/70/71) passes a freshly-constructed `new Date(...)` literal that is never read again by the caller, so the mutation has no observable aliasing consequence. No failure scenario.
- **"The fix doesn't handle DST-transition edge cases (`getTimezoneOffset()` differing between the original instant and the corrected one)."** Plausible in theory for values that sit right at a DST boundary, but I found no report, no test, and no reproduction showing a concrete wrong output from this; it's a hypothetical refinement of the real (confirmed) defect, not a separately demonstrated one. `unresolved` as a distinct defect — treat any such finding as part of GT-l1's mechanism, not a second item.
- **"The east-of-UTC fix itself is wrong / backwards."** Reproduction above (Case A, all five zones) shows it is correct in every tested zone, including at the exact UTC boundary. Not a defect.
- **"No JS unit test was added for `_unlocal_date`."** A real coverage gap (see Defect register and next section) but "insufficient test coverage" with no separate demonstrated failure of its own is not, by the task's rubric, a material defect distinct from GT-l1 — it's evidence of why GT-l1 escaped review, not a second defect.
- **"The PR's `- [ ] tests added / passed` checkbox was left unchecked."** Process/paperwork nit; tests were in fact added in later commits of the same PR. Not a code defect.
- **"Comment above `_unlocal_date` was replaced with a less precise one (no longer says 'this sucks')."** Documentation style preference, not material.
- **"Should have used `Intl`/a date library instead of manual offset arithmetic."** An architectural preference confirmed by hindsight (upstream did eventually replace the whole picker), but not something this diff was obligated to do to be correct, and not itself a defect in this diff.

## Preexisting hints

The review record up to the merge instant (2019-10-03T15:52:02Z) contains no comment that names GT-l1 specifically, but there is one comment that gestures at the exact class of testing that would have caught it, and one that (unknowingly) gives false confidence in the wrong direction:

- @bryevdv, 2019-09-27T16:39:29Z (pre-merge): *"Perhaps there might even be a way we could futz with the time zone on the test system to run things a few times in different time zones? Otherwise, it would be good just to make a separate issue about this."* — This is a direct, on-the-record recognition that the fix's correctness is timezone-dependent and that the test suite being added does not vary timezone. It does not identify the west-of-UTC regression, but it is exactly the gap whose absence let GT-l1 ship.
- @bryevdv, 2019-09-26T01:48:41Z (pre-merge): *"OK this seems to be working great for me in PST."* PST is west of UTC — precisely the zone class in which GT-l1 manifests. This is a near-miss in the wrong direction: it reads as validation, but per the mechanism above, manual testing in PST would only have shown Case A (the interactive `_on_select` round-trip, which is genuinely fixed everywhere) unless the tester also specifically checked that a freshly-loaded picker's `value`/`min_date`/`max_date` displayed the correct initial day — which none of the added tests do. It is not a hint pointing at the defect; it is evidence that the manual verification performed did not exercise the path that broke.
- @madkopp, 2019-10-06T19:11:41Z, raises the identical timezone-testing concern nearly verbatim ("We haven't done anything to change the system's timezone to test if that functionality holds up... It might not be a good idea to start changing system level things like that, especially not on the TravisCI workers") — but this is **after** the 2019-10-03T15:52:02Z merge, so it is disclosed here for completeness but does not count as a pre-merge hint.

No participant in the pre-merge record identifies the UTC-midnight/local-midnight anchor distinction, the Python-side serialization mechanism, or the specific west-of-UTC regression.

## Leakage

A truncated mirror used to evaluate a reviewer against this PR must exclude:

**SHAs (commits/diffs that would reveal the defect or its fix):**
- `16d3d0efcc` — squash-merge of PR #9509 ("Flatpickr") on `master`, which removes `_unlocal_date` entirely and fixes the root serialization ambiguity; its commit message and diff give away both the defect and the intended remediation.
- All individual PR #9509 commits: `03618bf8a623`, `998afc229aca`, `20e01ae0a8c9`, `ab27f2c46d31`, `40463bd5a25d`, `c2d9ecdfc15a`, `77dee3d151b4`, `a47c4c7ea6dc`, `c1030b196024`, `37fb7fc0f7e6`, `c3471d94d188`, `7621062cf615`, `0e6aea143847`, `ec557b685bf9`.
- Any later commit touching `bokehjs/src/lib/models/widgets/date_picker.ts` up through the Flatpickr rewrite (checked: only `16d3d0efcc` and an unrelated `83301c115c` "Switch to ES2017 target..." touch this file in that window — the latter is a mechanical toolchain commit with no semantic diff to `_unlocal_date` and is not itself a leak, but its presence in a `git log -- <path>` of that window is adjacent enough to `16d3d0efcc` that a truncated mirror should cut the file's history at the pinned head to be safe).
- `ec1e525c9a` — the squash-merge of PR #9232 itself on `master` (distinct SHA from the pinned head `36549bca...`, an artifact of GitHub's squash-merge). This is the PR under evaluation; whether to include it depends on how the harness presents "head" vs. "master" — flagging so the harness owner does not accidentally hand the reviewer both the linear PR commits *and* the squashed merge commit's neighborhood on `master`, which sits immediately next to `16d3d0efcc` in `git log --oneline -- date_picker.ts`, an easy accidental leak vector.

**Issue/PR numbers whose content gives away the answer:**
- Issue **#9494** — states the regression outright, names the affected timezone class (EST/non-GMT), and links straight to this PR's fix commit.
- PR **#9509** — the remediation; its description and review thread explain the anchor-format root cause in detail ("date values... caused endless trouble with time zones").
- Issue **#9835** ("Update current DatePicker value in UI") and its PR, if in scope of any later window — post-dates the Flatpickr rewrite, lower risk, but touches the same widget's date-value handling; exclude out of caution if a mirror window extends that far.

**Not leakage (safe to include):** Issue **#9129** — the originating bug this PR fixes (east-of-UTC `_on_select` round-trip). It describes only the reported symptom and the intended fix direction; it does not mention `min_date`/`max_date`, Python serialization, or any west-of-UTC behavior, so it does not give away GT-l1.

## Adjudicator's confidence and limits

High confidence in GT-l1: the mechanism is derived directly from primary source (the diff itself, `bokeh/util/serialization.py::convert_datetime_type`, `bokeh/core/json_encoder.py`, and `bokeh/core/property/datetime.py::Date.transform`, all read at the pinned head), independently reproduced with a faithful re-implementation of the exact algorithm under five real timezones, and independently corroborated by a real user bug report (#9494) whose reproduction script and reported symptom (EST-only, tracing to this exact commit) match the mechanism precisely, plus the fixing maintainer's own retrospective diagnosis in PR #9509.

Limits/unresolved:
- I did not build `bokehjs` or run a real browser against the compiled widget; the reproduction is at the algorithm level (a verbatim re-implementation of the diffed function), not an end-to-end DOM-level run. I consider this sufficient because the diff's entire behavioral surface is the function body reproduced, but flag it as `unresolved` for anyone wanting a literal in-browser confirmation.
- I did not execute the PR's added Selenium integration tests (environment lacks `selenium`/`chromedriver`); I reasoned from reading their assertions that they cannot detect GT-l1 (they never assert on the initially-rendered `value`/`min_date`/`max_date` display, only on the post-selection round trip), and separately noted no JS unit test of `_unlocal_date` exists to compare pass/fail across merge-base and head. Both are analytical conclusions from reading the test code, not from execution, and are marked as such above.
