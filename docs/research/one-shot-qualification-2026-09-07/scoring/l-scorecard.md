# Scorecard — target `l` (bokeh/bokeh #9232)

**Disclosure required by the rules:** the trailer HTML comments in these payloads carry a
`context=<hash>` field. `blind-6ecce4.md` and `blind-e1737e.md` carry the identical hash
(`9ce7772c...`), and `blind-a1ffdc.md` and `blind-a3a741.md` carry a second identical hash
(`67da918b...`). This looks like it could be a reviewer/run identifier that leaks which blind
files pair up. I did not use it to inform any judgment below, did not try to figure out what it
means, and I'm flagging it per the instructions rather than acting on it.

Register has exactly one material defect, **GT-l1** (the west-of-UTC regression in
`_unlocal_date`). All four reviews recover it. Scoring differentiates on fix sufficiency,
calibration of secondary findings, and evidence quality.

---

## `blind-6ecce4.md`

**1. Recovered defect IDs:** GT-l1.

Quote (finding body): *"`_unlocal_date` now subtracts a positive `getTimezoneOffset()` from that UTC-midnight instant, rolling the displayed date and the selectable min/max bounds back one calendar day. This reintroduces the same class of bug #9129 reported, now for UTC-negative zones -- including PST, the zone this fix was manually verified in, because that manual test exercised only the after-selection path."*

Reasoning: names the exact mechanism (offset applied to a UTC-midnight-anchored instant), the exact scope (value, min_date, max_date), the exact trigger class (negative-offset/west-of-UTC zones), and the consequence (one-day rollback). It also correctly explains *why* manual PST testing missed it (only the post-selection path was exercised) — matching the register's own "preexisting hints" analysis. Clears the specificity bar with room to spare.

**2. Missed defect IDs:** none (register has only GT-l1).

**3. Fix sufficiency:** `sufficient`.

Quote: *"In `_unlocal_date`, only apply the `getTimezoneOffset()` correction to a `Date` parsed from the client-side `toDateString()` round trip; derive the calendar day directly from `getUTCFullYear()/getUTCMonth()/getUTCDate()` when the input already represents a UTC-midnight instant."*

This distinguishes by **anchor** (was this `Date` built from a local-midnight string or a UTC timestamp?), which is the axis the register requires ("only apply the offset correction to inputs it can establish are local-midnight-anchored"). It doesn't spell out the runtime discriminator (e.g., checking `typeof this.model.value` before wrapping in `new Date()`), but the described rule, if implemented, restores correct output in every case: value/min_date/max_date all stay UTC-read (no shift) on the Python-set path, and the post-`_on_select` re-render (which re-parses `toDateString()`) still gets the shift, preserving the #9129 fix. No manifestation is left uncorrected.

**4. Findings not in register:**
- Observation: *"`_unlocal_date` mutates its `date` parameter in place via `date.setTime(...)` rather than operating on a copy, though all three current call sites pass a freshly constructed `Date` so nothing observes the mutation today."* — `true but not material`. Verified against source (`date_picker.ts:68,70,71` each pass `new Date(...)` literals). This is the exact item the register lists under "Not ground truth" and explicitly says has "no failure scenario." Correctly kept as an observation, not elevated to a finding.

**5. Action/severity errors:** none. The single must-fix P1 is well-supported (concrete regression, corroborated mechanism); the mutation note is correctly kept non-blocking.

**6. Questions, observations, hygiene items:** 1 observation (mutation-in-place, above); 0 questions; 0 other hygiene items. The observation is answerable from the material the reviewer had (yes — it's a static code-read fact) and would not change the review's verdict either way.

**7. Derived status:** "Changes Requested (advisory) — 1 must-fix finding." Coverage declared **complete**: *"Complete merge-base diff reviewed (2 files, +104/-2); Python-side date serialization (...) and sibling integration tests inspected; behavior reproduced with Node under multiple `TZ` settings."*

**8. False clean:** No. The review affirmatively requests changes and names a must-fix defect.

**9. Duplicates:** none — one finding, one observation, addressing different things.

---

## `blind-a1ffdc.md`

**1. Recovered defect IDs:** GT-l1.

Quote: *"`_unlocal_date` now shifts every input `Date` by `getTimezoneOffset()` before reading its calendar day. The initial `value`/`min_date`/`max_date` always arrive as a UTC-midnight timestamp (Bokeh's Python `Date` property serializes any date that way), so for a positive offset this shift pushes the timestamp into the previous UTC day before the day is read. The widget's initial displayed value and its effective selectable range are silently one calendar day earlier than configured, for the entire western hemisphere and much of the Pacific — the same class of bug issue #9129 reports, now on the opposite side of UTC."*

Reasoning: same mechanism, same scope, same trigger class as the other three reviews; clears the specificity bar.

**2. Missed defect IDs:** none.

**3. Fix sufficiency:** `partial`.

Quote: *"In `_unlocal_date`, only apply the timezone-offset shift to a `Date` that represents local midnight (the value Pikaday's `onSelect` produces before the round trip through `toDateString()`); keep the UTC-midnight-safe `date.toISOString().substr(0,10)` extraction — this function's own merge-base behavior — for `defaultDate`, `minDate`, and `maxDate`."*

I checked this against the source (`date_picker.ts:66-73`): `defaultDate` is populated from `this._unlocal_date(new Date(this.model.value))`, and `this.model.value` is the **same property** that `_on_select` overwrites with a `toDateString()` string (`_on_select`, line 95). Because `connect_signals` re-runs `render()` on every `model.change` (line 54), the very next render after a user selection reconstructs `defaultDate` from that just-written local-midnight string — i.e., the "keep old behavior for `defaultDate`" instruction, read literally, reverts to the pre-fix (unshifted) algorithm for exactly the post-selection path this PR was written to fix, which the register's reproduction table shows is broken pre-fix for every east-of-UTC zone (Case A). The proposed fix distinguishes by **property name** (`defaultDate`/`minDate`/`maxDate` vs. the on-select path) rather than by the underlying anchor of the data, and `defaultDate`/`value` is not consistently one anchor — it's precisely the property whose anchor changes across the PR's own primary scenario. As literally written this fix trades the west-of-UTC regression (GT-l1) for reintroducing the east-of-UTC bug (#9129) on the round-trip path — the exact failure mode the register calls out by name: *"A fix that 'solves' the west-of-UTC regression by reintroducing the east-of-UTC bug does not satisfy this."* It is not `absent` (a concrete change is proposed) and not fully `sufficient`; `partial` is the right classification — it would fix the initial-load manifestation of GT-l1 (and `min_date`/`max_date`, which are never round-tripped) but not the full contract.

**4. Findings not in register:** none — no observations, no consider items, no other findings.

**5. Action/severity errors:** none directly (the P1 must-fix itself is well warranted); the fix-sufficiency defect above is scored under item 3, not as an action error (the finding's asserted defect and priority are correct — it's the *proposed remedy* that's flawed).

**6. Questions, observations, hygiene items:** 0 of any kind. This is the leanest of the four reviews — no mutation-in-place note, no test-coverage suggestion.

**7. Derived status:** "Changes Requested (advisory) — 1 must-fix finding." Coverage declared **complete**: *"Complete merge-base diff reviewed (...); Python-side date serialization (...) inspected as a risk-led read; the 3 new Selenium integration tests traced by execution-semantics (...) — none exercises the regression below and none is suspicious."*

**8. False clean:** No.

**9. Duplicates:** none (single finding).

---

## `blind-a3a741.md`

**1. Recovered defect IDs:** GT-l1.

Quote: *"The widget displays the day before the one actually set — e.g. `DatePicker(value=datetime.date(2019, 9, 20))` renders as \"Sep 19 2019\" for a Los Angeles user on first paint — reproducing the exact class of off-by-one bug reported in #9129, mirrored onto timezones behind UTC instead of ahead of it."*

Reasoning: concrete worked example plus correct mechanism (`min_date`/`max_date` "are never converted to a string client-side, so they hit this path on every render for as long as they are set"). Clears the bar.

**2. Missed defect IDs:** none.

**3. Fix sufficiency:** `sufficient`.

Quote: *"In `_unlocal_date`, only apply the `getTimezoneOffset()`-based shift to a date built from a local-time representation (the `_on_select`/`toDateString()` round trip). A date that already represents UTC midnight of the target day — anything reaching this function straight from `this.model.value`, `this.model.min_date`, or `this.model.max_date` **before the browser has rewritten it** — must not be shifted, or the three call sites need to be told apart so the offset math applies only to the case it was designed for."*

This is the only one of the four fix proposals that explicitly names the ambiguity a1ffdc's proposal falls into — it flags that `this.model.value` can be either anchor depending on whether "the browser has rewritten it," and states the requirement as "the three call sites need to be told apart," i.e., by anchor, not by name. That is exactly the register's required axis. It doesn't hand over a diff, but as a corrective instruction it is complete and would not reintroduce #9129.

**4. Findings not in register:**
- Consider finding: *"The suite cannot detect the exact class of day-off-by-one regression this PR both fixes and reintroduces, because it never checks the initially rendered date and never runs under a non-UTC clock, unlike every sibling widget-test file in this directory."* — `true but not material`. Verified against `tests/integration/widgets/test_datepicker.py`: `test_basic` only asserts on the title label and console errors; `test_js_on_change_executes` and `test_server_on_change_round_trip` only assert post-click values; none asserts the initial rendered value. The register explicitly rules this "not a material defect distinct from GT-l1" but affirms it as a real gap — the review's own text ("Closing this without action is a correct response") shows it understood and correctly scored this as non-blocking.
- Observation: *"`_unlocal_date` mutates its `date` parameter directly via `setTime`, though every call site in `render()` passes a freshly constructed, unaliased `Date`, so the mutation currently has no observable effect."* — `true but not material`, same register item as in 6ecce4, correctly demoted.

**5. Action/severity errors:** none. P1 must-fix on GT-l1 is warranted; the P3 consider on test coverage is correctly non-blocking (matches the register's own classification, down to citing the same `bryevdv` 2019-09-27 comment the register cites as the "preexisting hint").

**6. Questions, observations, hygiene items:** 1 observation (mutation), 1 consider/hygiene finding (test timezone coverage), 0 questions. Both are answerable from the material the reviewer had (both are static-code and test-content facts, no execution needed) and neither would change the review's overall verdict — they're correctly kept out of the must-fix path.

**7. Derived status:** "Changes Requested (advisory) — 1 must-fix finding, 1 consider finding." Coverage declared **complete**: *"Complete — both changed files reviewed in full (...); the Python `Date`-property serialization pipeline, sibling widget-test conventions, and the PR's review thread were also inspected; no applicable repository-rule files exist for the changed paths."* (Verified: no `AGENTS.md`/`CLAUDE.md`/etc. at the merge-base per the packet's own guidance table.)

**8. False clean:** No.

**9. Duplicates:** none — the P1, the P3, and the observation each address distinct concerns.

---

## `blind-e1737e.md`

**1. Recovered defect IDs:** GT-l1.

Quote: *"`_unlocal_date` now shifts every input `Date` by `getTimezoneOffset()` before extracting its calendar date. That shift is only correct when the input was built by re-parsing `toDateString()`'s local-midnight string (the post-selection round trip this PR targets). For the property's original UTC-anchored timestamp (the initial/programmatic value, or `min_date`/`max_date`), the same shift pushes the calendar date backward by one day for every timezone behind UTC. The picker's initial default date, and its min/max bounds, then display one calendar day earlier than the value Python sent..."*

Reasoning: precise mechanism, precise scope, precise trigger. Clears the bar. Also backed by the broadest stated reproduction of the four: *"verified by execution across 7 IANA zones spanning UTC−9:30 to UTC+14"* (naming Pacific/Kiritimati [UTC+14] and Pacific/Marquesas [UTC−9:30], both real IANA zones — this is genuine half-hour/45-minute-offset-adjacent stress-testing beyond the register's own 5-zone table).

**2. Missed defect IDs:** none.

**3. Fix sufficiency:** `sufficient`.

Quote: *"In `bokehjs/src/lib/models/widgets/date_picker.ts`, only apply the local-to-UTC compensation when the input `Date` came from re-parsing `toDateString()`'s local-midnight string; skip it when the input is the property's original UTC-anchored timestamp. For example, have `_on_select` store a UTC-midnight timestamp (`Date.UTC(date.getFullYear(), date.getMonth(), date.getDate())`) instead of a bare local date string, so both call sites' input already share one UTC-anchored representation and `_unlocal_date` no longer needs to guess which kind of `Date` it received."*

This is the most concrete of the four proposals: rather than asking the function to infer anchor at read time (the ambiguity a1ffdc's proposal trips over and a3a741 explicitly flags as unresolved), it removes the ambiguity at the source by making `_on_select` write a uniformly UTC-anchored representation. That is exactly the class of fix the register cites as what upstream ultimately did ("removing the ambiguity at the source ... rather than as UTC-instant timestamps that get reinterpreted through a local clock" — here inverted to make everything UTC-anchored instead of everything an ISO string, but the same principle: one anchor convention, no guessing). Implemented as described, every manifestation (initial value, min_date, max_date, and the post-selection round trip) reads correctly in every timezone.

**4. Findings not in register:**
- Consider finding: *"None of the tests vary timezone, so the suite cannot regression-protect the timezone-dependent behavior this PR fixes. `test_js_on_change_executes` and `test_server_on_change_round_trip` only assert the value after a click; neither they nor `test_basic` assert the picker's initial displayed date at all."* — `true but not material`, verified against the test file (same check as for a3a741's parallel finding). Also backs the "ambient timezone" claim with a specific, checked fact: *"neither `.travis.yml` nor `.appveyor.yml` sets `TZ`."* I verified this directly: `git show review-head:.travis.yml` and `:.appveyor.yml` contain no `TZ`/timezone directive (a substring false-positive from a base64 `secure:` token was the only "TZ"-like hit, and it isn't a timezone setting). This is a correctly-scoped, evidence-backed, non-blocking finding matching the register's own classification.
- Observation: *"`_unlocal_date` mutates its `date` argument in place via `date.setTime(...)` rather than operating on a copy; all three current call sites in `render()` construct a fresh `Date` for this argument, so no observable effect results today."* — `true but not material`, same register item, correctly demoted.

**5. Action/severity errors:** none. P1 on GT-l1 is warranted; the P3 consider on test coverage is correctly non-blocking.

**6. Questions, observations, hygiene items:** 1 observation (mutation), 1 consider/hygiene finding (test timezone coverage, with a more specific CI-config claim than a3a741's parallel finding), 0 questions. Both answerable from material on hand; neither changes the verdict.

**7. Derived status:** "Changes Requested (advisory) — 1 must-fix finding, 1 consider finding." Coverage declared **complete**: *"Complete merge-base diff reviewed (2 files ...); both changed files reviewed in full. Focused execution: a scratch Node reproduction of `_unlocal_date` (old vs. new) was run across 7 IANA timezones ... The Selenium integration tests this PR adds could not be executed (no browser/npm install available in this environment); traced by code instead..."* — explicitly distinguishes what was executed from what was only traced, an honest and precise coverage statement.

**8. False clean:** No.

**9. Duplicates:** none — P1, P3, and observation each address distinct concerns.

---

## Cross-review table

| Review | Recovered | Recall (R/D) | Fix sufficiency | False findings | Action errors | Observations/hygiene | Questions | False clean | Status |
|---|---|---|---|---|---|---|---|---|---|
| `blind-6ecce4.md` | GT-l1 | 1/1 | sufficient | 0 | 0 | 1 (mutation) | 0 | No | Changes Requested — 1 must-fix; coverage complete |
| `blind-a1ffdc.md` | GT-l1 | 1/1 | partial | 0 | 0 | 0 | 0 | No | Changes Requested — 1 must-fix; coverage complete |
| `blind-a3a741.md` | GT-l1 | 1/1 | sufficient | 0 | 0 | 2 (mutation + test-coverage consider) | 0 | No | Changes Requested — 1 must-fix, 1 consider; coverage complete |
| `blind-e1737e.md` | GT-l1 | 1/1 | sufficient | 0 | 0 | 2 (mutation + test-coverage consider) | 0 | No | Changes Requested — 1 must-fix, 1 consider; coverage complete |

## New candidates

None. Every non-register item raised across the four reviews (the in-place mutation in `_unlocal_date`, and the new test file's failure to assert the initial rendered value or vary timezone) is explicitly enumerated and dispositioned as non-material in the register's "Not ground truth" section, and I independently re-verified both against the source (`date_picker.ts` call sites all pass fresh `Date` literals; `test_datepicker.py` never asserts pre-selection state and no CI config sets `TZ`). No review raised any claim outside that set. Confidence: high — this is a narrow, fully-diffed target (8 changed lines in the one substantive file) and all four reviews converged on the same single defect and the same two subordinate observations, none of which needs further adjudication.

## Summary judgment

All four reviews recover the sole material defect (GT-l1) with specificity that clears the bar, back it with real execution evidence (Node reproductions under multiple timezones), correctly withhold false-clean, and correctly avoid elevating the register's known non-material items (in-place mutation, test-coverage gap) into blocking findings. The differentiator is fix quality: `blind-a1ffdc.md`'s proposed remedy, read literally, distinguishes cases by property name (`defaultDate`/`minDate`/`maxDate`) rather than by data anchor, and `defaultDate` is not consistently one anchor — the same call site carries the local-midnight anchor on the very re-render this PR's own fix is supposed to correct. That makes its fix `partial` rather than `sufficient`. The other three propose anchor-aware corrections; `blind-e1737e.md`'s is the most concrete (moves the fix to the write side, in `_on_select`, eliminating the ambiguity entirely) and pairs it with the broadest verified timezone sweep. `blind-a3a741.md` and `blind-e1737e.md` additionally surface the (non-material, but real and register-anticipated) test-coverage gap as a correctly-scoped, non-blocking "consider" item, citing accurate supporting evidence I independently checked.
