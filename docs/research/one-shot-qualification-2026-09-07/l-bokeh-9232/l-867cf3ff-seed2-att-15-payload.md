<!--
This is the review exactly as it would be posted, rendered by
`scripts/validate_review.py --emit-batch` from a payload that validated with
zero violations (`scripts/validate_review.py`, exit 0). Publication is
disabled for this run (retrospective review of a merged pull request,
posting identity `kamui` who did not author the PR); nothing here was sent
anywhere. Target: bokeh/bokeh#9232. Would-be event: COMMENT. Would-be
commit_id: 36549bca3a63d581f7b68d08054a7813c1e6a499.
-->

# Review summary (would-be review body)

**Changes Requested (advisory)** — 1 must-fix finding, 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix `DatePicker`'s displayed date lagging one day behind the selected date for users in UTC+ timezones, by having `_unlocal_date` compensate for the browser's local/UTC offset before reformatting.

**Issue fit:** Partial — the reported UTC+ display-after-selection bug (#9129) is fixed in every timezone tested, but the same helper now applies the same offset compensation to values that arrive from the server already at UTC midnight (`value` before interaction, `min_date`, `max_date`), which reproduces the identical off-by-one symptom for every timezone behind UTC instead.

**Coverage:** Complete — both changed files reviewed in full (`bokehjs/src/lib/models/widgets/date_picker.ts`, `tests/integration/widgets/test_datepicker.py`); the Python `Date`-property serialization pipeline, sibling widget-test conventions, and the PR's review thread were also inspected; no applicable repository-rule files exist for the changed paths.

**Reviewed:** `36549bca3` against merge-base `ccb4bcb4c`.

## Findings

- [P1] [must-fix] Guard `_unlocal_date`'s offset shift against already-UTC-midnight input — anchor [`bokehjs/src/lib/models/widgets/date_picker.ts:82-83`](https://github.com/bokeh/bokeh/blob/36549bca3a63d581f7b68d08054a7813c1e6a499/bokehjs/src/lib/models/widgets/date_picker.ts?plain=1#L82-L83)

## Unanchored findings

**[P3] [consider] Add initial-value and cross-timezone coverage to the new DatePicker tests**

**Triggers when:** A future change reintroduces a timezone-dependent display bug — as this PR's own `_unlocal_date` change does, see the finding above — and nothing in the suite would catch it.

**Impact:** The suite cannot detect the exact class of day-off-by-one regression this PR both fixes and reintroduces, because it never checks the initially rendered date and never runs under a non-UTC clock, unlike every sibling widget-test file in this directory.

**Change:** Add an assertion in `test_basic` (or a new test) that the initially rendered input value matches the Python-set `value` (and that `min_date`/`max_date` bound the calendar as expected) immediately after `bokeh_model_page(...)`, and exercise the suite under at least one UTC+ and one UTC− system timezone.

**Source:** PR review thread, 2019-09-27T16:39:29Z (`bryevdv`): timezone variation across the test system was suggested but never implemented.

Closing this without action is a correct response.

anchor [`tests/integration/widgets/test_datepicker.py`](https://github.com/bokeh/bokeh/blob/36549bca3a63d581f7b68d08054a7813c1e6a499/tests/integration/widgets/test_datepicker.py) (file)

## Observations

- `_unlocal_date` mutates its `date` parameter directly via `setTime`, though every call site in `render()` passes a freshly constructed, unaliased `Date`, so the mutation currently has no observable effect. Evidence: `bokehjs/src/lib/models/widgets/date_picker.ts:82-83`.

<!-- review-run head=36549bca3a63d581f7b68d08054a7813c1e6a499 base-ref=master base-sha=ccb4bcb4c2b841d89b0e88303a97bf4604a5795f merge-base=ccb4bcb4c2b841d89b0e88303a97bf4604a5795f workflow=v5b-1 context=9ce7772c753e38225d78d80e2051b0392b6f3d727d0e3d5e217b78ba72c338ff issues=bokeh/bokeh#9129 coverage=complete -->

---

# Inline review comment (would post on the diff)

### `bokehjs/src/lib/models/widgets/date_picker.ts:82-83` (side: RIGHT)

**[P1] [must-fix] Guard `_unlocal_date`'s offset shift against already-UTC-midnight input**

**Triggers when:** A user whose system timezone is west of UTC (e.g. `America/Los_Angeles`, UTC−7/−8, or any other negative offset) loads a page with a `DatePicker` whose `value` was set from Python and has not yet been edited in the browser, or that has `min_date`/`max_date` set at all — these two properties are never converted to a string client-side, so they hit this path on every render for as long as they are set.

**Impact:** The widget displays the day before the one actually set — e.g. `DatePicker(value=datetime.date(2019, 9, 20))` renders as "Sep 19 2019" for a Los Angeles user on first paint — reproducing the exact class of off-by-one bug reported in #9129, mirrored onto timezones behind UTC instead of ahead of it.

**Change:** In `_unlocal_date`, only apply the `getTimezoneOffset()`-based shift to a `date` built from a local-time representation (the `_on_select`/`toDateString()` round trip). A `date` that already represents UTC midnight of the target day — anything reaching this function straight from `this.model.value`, `this.model.min_date`, or `this.model.max_date` before the browser has rewritten it — must not be shifted, or the three call sites need to be told apart so the offset math applies only to the case it was designed for.

**Source:** Issue #9129 — the fix must not merely move the reported symptom to a different set of timezones.

<!-- finding id=bokehjs/date-picker/unlocal-date-utc-negative-regression head=36549bca3a63d581f7b68d08054a7813c1e6a499 priority=P1 action=must-fix blocking=true kind=bug -->

(No question comments. The `[P3] [consider]` finding has a whole-file anchor, which GitHub's one-call review batch cannot represent as a file-subject comment, so its complete prose is rendered only in the `Unanchored findings` section of the summary above, not as a second inline comment. The observation has no inline comment or trailer by contract; it is rendered only in the `Observations` section of the summary above.)
