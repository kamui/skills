# Ordinary-defect hunt — report

Two candidates verified with real `gh`/`git`/build commands on this machine. Both meet every hard
constraint. One alternate is documented for each, with the specific reason it was not chosen.

**A note on data hygiene.** While searching, I ran into several recently-filed GitHub issues
(scikit-hep/awkward#4205, pallets/click#3731, gijzelaerr/python-snap7#813/#816,
srcdslab/torchlight#128) that explicitly identify themselves as AI-generated bug reports
("🤖 Generated with Claude Code", "Claude wrote up the explanation and fix below"), several with
near-future timestamps (e.g. python-snap7 PR #806 merged 2026-08-10, less than a month before
today). One (pallets/click#3731) was explicitly rejected by the maintainer as unreadable AI slop
and never confirmed by a real fix. These are not prompt injections directed at me — just planted
or synthetic-looking content with no genuine independent confirmation behind them — so I excluded
all of them as evidence and went looking for older, organically-filed bug histories instead. Both
final candidates below predate this pattern (2019 and 2024/2019 respectively) and were checked
comment-by-comment for the same red flags.

---

## Candidate A — ordinary behavioural defect

**Repository:** `bokeh/bokeh` — BSD-3-Clause, 20,445 stars, real project (PyData/Anaconda-adjacent,
maintained by Bryan Van de Ven and others). Language: TypeScript (bokehjs), so this spreads the
grid away from Go/Rust.

**PR:** [#9232 "Fixed issue of Datepicker displaying the wrong date for users in UTC+…"](https://github.com/bokeh/bokeh/pull/9232)
**Author:** madkopp (Adam Kopp) · **Merged by:** bryevdv (Bryan Van de Ven, MEMBER)
**Merged at:** 2019-10-03T15:52:02Z · **Base branch:** `master`

### SHAs

- PR-recorded `headRefOid`: `36549bca3a63d581f7b68d08054a7813c1e6a499`
- PR-recorded `baseRefOid`: `ccb4bcb4c2b841d89b0e88303a97bf4604a5795f`
- Squash-merge commit on `master`: `ec1e525c9a8ad128e29b3b74beb732e79a0db437` (single parent
  `2f89b8f526027e2ed0ba0bf6d81aca6a822828a6` — GitHub squash-merge, message
  `"Fixed issue of Datepicker displaying the wrong date for users in UTC+… (#9232)"`)
- **`git merge-base` I computed** on a full (blob-filtered, full-history) clone:
  `git merge-base ccb4bcb4c2b841d89b0e88303a97bf4604a5795f 2f89b8f526027e2ed0ba0bf6d81aca6a822828a6`
  → `ccb4bcb4c2b841d89b0e88303a97bf4604a5795f`.
  **This equals the PR-recorded `baseRefOid` exactly** — the base branch had moved forward by other
  commits between PR-open and merge, but the PR's own base is still the true merge-base, confirming
  a clean linear history with no silent rebase/backdating.

### Changed-file manifest (106 lines total, 2 files — well inside the 250/6 budget)

| file | + | - |
|---|---|---|
| `bokehjs/src/lib/models/widgets/date_picker.ts` | 6 | 2 |
| `tests/integration/widgets/test_datepicker.py` (new file) | 98 | 0 |
| **total** | **104** | **2** |

### Originating issue

[#9129 "\[BUG\]Datepicker displayed value is not updating correctly"](https://github.com/bokeh/bokeh/issues/9129)
(filed 2019-07-30): in UTC+ (east-of-UTC) timezones, picking a date in the widget displayed the
previous day until picked a second time. PR #9232 fixes exactly this — the promised behaviour
change.

### Prior review record

- 2 formal PR reviews (both `bryevdv`, state `COMMENTED`), 12 issue-level comments over
  2019-09-22 → 2019-10-06, contributors `madkopp` and `bryevdv`.
- The whole thread is about (a) whether the fix works on `bryevdv`'s machine in PST, and
  (b) intermittent Selenium/"interrogation" CI flakiness unrelated to the diff. **Nobody discusses
  the input-format assumption that causes the regression** — it is invisible in review because both
  reviewers only exercised the same-format (`toDateString()`→`toDateString()`) round trip that the
  new integration test covers.
- Representative quotes:
  - `bryevdv`, 2019-09-26: *"OK this seems to be working great for me in PST … I'd like to merge
    this tomorrow if one or both of you can you test this out locally as well?"*
  - `bryevdv`, 2019-10-03: *"OK I can't get the flaky integration test to pass on the branch. Not
    sure why this happens sometimes. I am going to go ahead and merge to see if it resolves on
    master."*

### The defect

**File:** `bokehjs/src/lib/models/widgets/date_picker.ts`, function `_unlocal_date` (lines ~78–88
post-fix). Verbatim post-fix body:

```ts
_unlocal_date(date: Date): Date {
  const timeOffsetInMS = date.getTimezoneOffset() * 60000
  date.setTime(date.getTime() - timeOffsetInMS)

  const datestr = date.toISOString().substr(0, 10)
  const tup = datestr.split('-')
  return new Date(Number(tup[0]), Number(tup[1])-1, Number(tup[2]))
}
```

`_unlocal_date` is called from three places in `render()`: on `defaultDate` (from
`this.model.value`), `minDate` (from `this.model.min_date`), and `maxDate` (from
`this.model.max_date`). **The fix silently assumes every `Date` it receives represents local
midnight of the intended day** — true for the one path the new test exercises (`_on_select`'s
`date.toDateString()` output, which JS's non-ISO Date parser reads as local midnight) — and applies
a `getTimezoneOffset()` correction to compensate. But `min_date`/`max_date`, and any `value` that
has round-tripped as an ISO date string (`"YYYY-MM-DD"`, the format Python `datetime.date`
naturally serializes to, and per ECMA-262 §21.4.3.2 parsed by `Date()` as **UTC** midnight, not
local), hit the same function. For those inputs the correction shifts the date backward by the
local UTC offset, landing on the previous UTC calendar day whenever the offset is negative (any
timezone **west** of UTC — the US, all of the Americas, etc.). East-of-UTC and UTC timezones are
unaffected because the shift there moves *forward* into the same day.

- **Expected behaviour:** `_unlocal_date` returns the same calendar day it was given, in every
  timezone, for every legitimate input format the property can carry.
- **Trigger:** any west-of-UTC user with a `DatePicker.min_date`/`max_date` set from a
  `datetime.date`, or any value that arrives as an ISO string rather than the `toDateString()`
  format — exactly the round-trip scenario in the confirming issue below.
- **Demonstrated consequence:** off-by-one-day display, confirmed live below.

### Confirming later issue/PR

[**Issue #9494**](https://github.com/bokeh/bokeh/issues/9494), filed 2019-12-02T23:21:06Z by
`rstrutt` — *"\[BUG\] DatePicker display off-by-one in non-GMT timezone after upgrade to 1.4.0"*:

> "After the fix of [this issue](https://github.com/bokeh/bokeh/pull/9232/commits/472e4770d363b3914bb478f0a6c3a83787b20c0d) in 1.4, I observe the following issue; In the EST timezone, if I
> update a DatePicker based on the value of another DatePicker, I get a different date (1 day
> previous to the selected date). If the browser is located in a GMT timezone then I do not
> observe the issue."

Closed 2020-01-17T04:00:39Z by [**PR #9509 "Flatpickr"**](https://github.com/bokeh/bokeh/pull/9509)
(head `ec557b685bf941658b0a569db2ee4ae4d917045e`, merge commit
`16d3d0efcc91a4206be0c3f11ede33f9fc03cda9`, base `16a7acdff98102619b68f244a904062b8875dd76`),
which replaced Pikaday with Flatpickr wholesale. Maintainer `bryevdv`, closing comment:

> "#9509 fixes this and many other datepicker issues (as well as adds selenium tests) for 2.0 but
> note that the implementation was switched to Flatpickr, and also now date values can *only* be
> expressed as ISO date strings, or `datetime.date` and nothing else (in particular no more
> datetime values which caused endless trouble with time zones)."

That sentence is the project's own after-the-fact admission that the local/UTC format ambiguity
`_unlocal_date` never resolved was the root cause of "endless trouble."

**Corrective outcome a correct review must require:** either normalize every call site to a single
unambiguous date representation before it reaches `_unlocal_date` (which is what #9509 eventually
does, by fixing the value contract to ISO-only), or make `_unlocal_date` detect/handle both input
conventions; and add a regression test that exercises `min_date`/`max_date` (not just same-format
`value`↔`value` round trips) in a non-UTC, negative-offset timezone.

### Tempting false positives (candidate A)

1. **"`date.setTime(...)` mutates the caller's `Date` object in place — aliasing bug."** False:
   every call site (`defaultDate`, `minDate`, `maxDate` in `render()`) passes a freshly constructed
   `new Date(...)` literal as the argument, so there is no shared/aliased object across the three
   calls; the in-place mutation is locally contained and harmless by itself.
2. **"The `var`→`const` follow-up commit (`7aae927cf`) might have silently changed scoping/hoisting
   behaviour."** False, verified: `git show 7aae927cf -- .../date_picker.ts` is a pure
   `var timeOffsetInMS` → `const timeOffsetInMS` rename plus two comment-casing edits; no logic
   changed.
3. **"The repeated CI flakiness discussed in review ('flaky interrogation tests', 'signal: killed'
   errors) means the code itself is nondeterministic."** False: `bryevdv` explicitly diagnosed this
   as pre-existing Selenium/CI infrastructure flakiness unrelated to the diff ("There is nothing to
   fix, we have a couple of flaky interrogation tests that have not been addressed yet" / "signal:
   killed errors in the cmd/shfmt-style test scripts" — unrelated macOS runner issue, not this PR's
   logic).

### SHAs a truncated mirror must exclude

- `ec1e525c9a8ad128e29b3b74beb732e79a0db437` (squash-merge of #9232 itself — this is the PR under
  review, must stay visible, but its **later history must be hidden**)
- `472e4770d363b3914bb478f0a6c3a83787b20c0d`, `7aae927cf09820e74a58108ea45facc0f6aa695c`,
  `e92066d593fa2c88ffe732dbaeb3303fff996a15`, `4215c2d0b956eca3dc714b6c11c7fedb440013c9`,
  `36549bca3a63d581f7b68d08054a7813c1e6a499` (the PR's own branch commits — fine to show, they are
  pre-merge)
- `ec557b685bf941658b0a569db2ee4ae4d917045e` (PR #9509 head) and
  `16d3d0efcc91a4206be0c3f11ede33f9fc03cda9` (PR #9509 squash-merge) — **must hide**, this is the fix
- Issue **#9494** and PR **#9509** — hide both numbers and all their comments

### Test evidence I actually ran

Bokeh's own regression coverage for this widget is the Selenium integration test the PR itself
adds (`tests/integration/widgets/test_datepicker.py`), which needs a running browser + webdriver —
not offline-runnable in 5 minutes. There is **no unit test anywhere in `bokehjs/test` referencing
`_unlocal_date` or `date_picker`** (confirmed: `grep -rl "unlocal_date" bokehjs/` inside the full
clone returns only the source file itself, and `bokehjs/package.json` has no standalone unit-test
script, only `build`/`dev-build`). So I extracted `_unlocal_date` verbatim (pre-fix and post-fix)
into a standalone Node script — pure `Date` semantics, no bokeh build, no network:

```
$ TZ=America/New_York node bokeh_repro.js   # west of UTC
$ TZ=Europe/Paris node bokeh_repro.js       # east of UTC
$ TZ=UTC node bokeh_repro.js
```

**Provisioning:** none beyond Node (already present, `v24.19.0`). **Run time:** <1s per invocation.

**Output (abbreviated, full run took ~2s total across 6 timezones):**

```
TZ = America/New_York
pre-fix   | local-format input  "Fri Sep 20 2019" -> Fri Sep 20 2019  OK
pre-fix   | ISO-format input    "2019-09-20"      -> Fri Sep 20 2019  OK
post-fix  | local-format input  "Fri Sep 20 2019" -> Fri Sep 20 2019  OK
post-fix  | ISO-format input    "2019-09-20"      -> Thu Sep 19 2019  WRONG (expected Fri Sep 20 2019)

TZ = Europe/Paris
pre-fix   | local-format input  "Fri Sep 20 2019" -> Thu Sep 19 2019  WRONG (expected Fri Sep 20 2019)
pre-fix   | ISO-format input    "2019-09-20"      -> Fri Sep 20 2019  OK
post-fix  | local-format input  "Fri Sep 20 2019" -> Fri Sep 20 2019  OK
post-fix  | ISO-format input    "2019-09-20"      -> Fri Sep 20 2019  OK

TZ = UTC
pre-fix   | local-format input  "Fri Sep 20 2019" -> Fri Sep 20 2019  OK
pre-fix   | ISO-format input    "2019-09-20"      -> Fri Sep 20 2019  OK
post-fix  | local-format input  "Fri Sep 20 2019" -> Fri Sep 20 2019  OK
post-fix  | ISO-format input    "2019-09-20"      -> Fri Sep 20 2019  OK
```

Also ran `Pacific/Kiritimati`, `Etc/GMT-14`, `Asia/Kolkata` — every east-of-UTC/UTC zone matches
the `TZ=Europe/Paris` pattern (pre-fix broken, post-fix fixed); every west-of-UTC zone matches
`TZ=America/New_York` (pre-fix fine, post-fix broken on ISO input). This exactly reproduces both
#9129 (pre-fix, east-of-UTC) and #9494 (post-fix, west-of-UTC) from opposite ends, at both the
merge-base and the head commit. Script and output are saved at
`/tmp/qual137/hunts/bokeh_repro.js`.

### Confidence: **High**

The defect is statically visible by reading `_unlocal_date` and its three call sites — no
telemetry or fuzzing needed. It is independently confirmed by a real, organically-filed issue
(2019, plain human bug report, closed by a real maintainer's fix PR) with a verbatim admission of
the root cause. I reproduced both the pre-fix bug and the post-fix regression deterministically
with a standalone offline script. The one soft spot: bokeh's own test suite never exercises this
exact path (I had to build the reproduction myself rather than run a project-native test) — flagged
above, not hidden.

---

## Candidate B — genuinely clean PR

**Repository:** `BurntSushi/ripgrep` — dual MIT/Unlicense (GitHub reports `Unlicense` as primary
SPDX id), 68,020 stars, real project (maintained by Andrew Gallant / BurntSushi). Language: Rust
project, but the changed surface is a zsh completion script + docs — deliberately different
ecosystem/shape from candidate A's JS timezone bug.

**PR:** [#2957 "feat(completion): support sourcing zsh completion dynamically"](https://github.com/BurntSushi/ripgrep/pull/2957)
**Author:** vegerot (Max Coplan) · **Merged by:** BurntSushi
**Merged at:** 2024-12-31T13:23:13Z · **Base branch:** `master`

### SHAs

- PR-recorded `headRefOid`: `855bfa6cdae4f4fe8762f892fc4957635397083e`
- PR-recorded `baseRefOid`: `79cbe89deb1151e703f4d91b19af9cdcc128b765`
- Squash-merge commit on `master`: `94305125ef33b86151b6cd2ce2b33d641f6b6ac3` (single parent
  `79cbe89deb1151e703f4d91b19af9cdcc128b765` — i.e. merged directly onto its own base, no
  intervening commits)
- **`git merge-base` I computed** on a full clone:
  `git merge-base 79cbe89deb1151e703f4d91b19af9cdcc128b765 855bfa6cdae4f4fe8762f892fc4957635397083e`
  → `79cbe89deb1151e703f4d91b19af9cdcc128b765`. **Equals the PR-recorded base exactly**, and also
  equals the merge commit's sole parent — a clean fast-forward-shaped squash merge, nothing hidden.

### Changed-file manifest (33 lines total, 2 files)

| file | + | - |
|---|---|---|
| `FAQ.md` | 20 | 3 |
| `crates/core/flags/complete/rg.zsh` | 9 | 1 |
| **total** | **29** | **4** |

### Originating issue

[#2956 "Can't source zsh completions directly"](https://github.com/BurntSushi/ripgrep/issues/2956)
(filed 2024-12-30): `source <(rg --generate=complete-zsh)` fails with
`_arguments:comparguments:327: can only be called from completion function` when the user's shell
already has a completion system loaded.

### Prior review record

10 inline review comments across 3 participants (`BurntSushi` owner, `vegerot` author,
`okdana` contributor) plus 3 issue-level comments — substantial back-and-forth on a 33-line diff.
Key substantive exchanges:

- `BurntSushi`: *"Why are we suggesting this method? I'm okay with supporting it as long as it
  doesn't have any costs to doing so, but I don't see a good reason to specifically highlight it in
  the docs."* — pushed on the FAQ wording, resolved by `vegerot` adding a caveat about the 4ms
  overhead, then `BurntSushi` closing comment: *"I've left it in the FAQ and fixed up the wording by
  adding an appropriate caveat emptor … the text now makes it clear that the 'generate and source'
  approach is slower."*
- `okdana`, on the original redundant fallback code: *"i would suggest this as more idiomatic (and
  faster) than the `type` method: `if [[ $funcstack[1] == _rg ]] || (( ! $+functions[compdef] ))
  ; then`* — this exact line is what got merged.
- **The tempting-but-false moment, on the record:** `vegerot`, discussing why the original draft
  had redundant fallback logic: *"I originally wrote this as [...] But `ci/test-complete` didn't
  like that. ~~I feel like the test is wrong~~ (nvm I am wrong!), because realistically you will
  either have `compdef` or will run the completion as `_rg`."* The author's own first instinct —
  that the project's CI test must be wrong — was wrong; the test correctly required both branches
  to be handled, which is what forced the real fix into shape.

### Cleanliness evidence

- `git log --oneline -- crates/core/flags/complete/rg.zsh` on current HEAD (16 commits after
  #2957) shows no commit that touches the merged `funcstack`/`compdef` lines again; the later
  commits are unrelated (`compadd -q to -r`, `_numbers`, colour/type-spec completion, hyperlink
  format, etc.).
- `git show HEAD:crates/core/flags/complete/rg.zsh | grep -A6 funcstack` on the current default
  branch shows the exact block from #2957, byte-for-byte unchanged, still carrying its own
  `# See https://github.com/BurntSushi/ripgrep/issues/2956` / `#2957` comments.
- `gh search issues --repo BurntSushi/ripgrep "funcstack"` / `"compdef"` → **zero results**.
- `gh search issues --repo BurntSushi/ripgrep "zsh completion"` (15 results, full history) → the
  only entries in the relevant window are #2956 itself (pre-fix, expected) and an unrelated 2025
  macOS-install issue (#3050); nothing post-dates or complains about #2957.

**The surface a correct review must NOT assert as a defect:** the merged
`if [[ $funcstack[1] == _rg ]] || (( ! $+functions[compdef] )); then _rg "$@"; else compdef _rg rg;
fi` block looks, on a quick read, like it silently drops the previous unconditional `_rg "$@"` call
for the normal (`compdef` available) case — as if regular fpath/compinit-based completion
registration might now be broken. It is not: `compdef _rg rg` **is** the correct, idiomatic way to
register a completion function for lazy invocation by zsh's completion system; the previous
unconditional call was the actual bug (it eagerly invoked `_arguments` outside a real completion
context, which is exactly what #2956 reported).

### Tempting false positives (candidate B)

1. **"Dropping the unconditional `_rg \"$@\"` call breaks completion registration when `compdef` is
   available."** False — verified by running the merged code with a stub `compdef` defined: it
   correctly takes the `compdef _rg rg` branch and registers cleanly (see test evidence below).
2. **"Matching on `$funcstack[1] == _rg` by literal function name is fragile — any other function
   named `_rg` in the user's shell would false-trigger the self-source branch."** Tempting, but this
   *is* the standard, intended zsh idiom for self-referential completion files: this very file
   defines the function `_rg` itself, so the guard is checking "am I currently executing as my own
   completion function" by design, not guessing at an arbitrary collision.
3. **"`(( ! $+functions[compdef] ))` might wrongly treat `compdef` as absent if it's defined as an
   alias rather than a function, since `$+functions` only sees functions."** False in this context:
   zsh's real completion system (`compinit`) always defines `compdef` as a shell **function**, never
   an alias, so `$+functions[compdef]` is exactly the right existence check.
4. **The original PR author's own doubt, on the record:** *"I feel like the test is wrong (nvm I am
   wrong!)"* (`vegerot`, quoted above in full) — the CI test (`ci/test-complete`-adjacent shell
   behavior) was in fact correct; the author's initial suspicion that it was buggy was the false
   lead, not the final merged code.

### SHAs a truncated mirror must exclude

Nothing needs hiding for cleanliness (there is no later fix to hide), but to prevent the reviewer
from seeing the review's own resolution before reviewing, a mirror should still exclude anything
past the merge:
- No later commits touch this code (verified above) — there is nothing to hide on the "fix" axis.
- If wanting to hide the review discussion itself (not required by the constraints, but consistent
  with how A's mirror should look), hide PR **#2957**'s own review/comment thread and issue **#2956**.

### Test evidence I actually ran

**Reproduction of the exact issue #2956 failure mode + refutation of tempting false positive #1,**
using the pre-fix and post-fix `rg.zsh` fetched at the merge-base and merge SHAs, no build needed:

```
$ curl -s https://raw.githubusercontent.com/BurntSushi/ripgrep/79cbe89deb1151e703f4d91b19af9cdcc128b765/crates/core/flags/complete/rg.zsh -o pre-fix.zsh
$ curl -s https://raw.githubusercontent.com/BurntSushi/ripgrep/94305125ef33b86151b6cd2ce2b33d641f6b6ac3/crates/core/flags/complete/rg.zsh -o post-fix.zsh
$ zsh run_test.sh
```

**Provisioning:** none beyond `zsh` (preinstalled on macOS, `5.9`) and `curl` (one-time fetch of two
files). **Run time:** 0.29s total.

**Output:**

```
--- pre-fix  (merge-base 79cbe89d) ---
  scenario A: compdef already defined (compinit has run, like #2956's reporter)
    _rg:341: command not found: _arguments
    exit status: 1
  scenario B: compdef NOT defined (compinit has not run yet)
    _rg:341: command not found: _arguments
    exit status: 1

--- post-fix (merge      94305125, PR #2957) ---
  scenario A: compdef already defined (compinit has run, like #2956's reporter)
    REGISTERED: compdef _rg rg
    exit status: 0
  scenario B: compdef NOT defined (compinit has not run yet)
    _rg:341: command not found: _arguments
    exit status: 1
```

This is a clean, deterministic demonstration: pre-fix errors in *both* scenarios (matching #2956);
post-fix fixes exactly scenario A (the one #2956's reporter hit — completion system already
loaded) *by taking the `compdef _rg rg` branch*, which directly refutes tempting false positive #1
above; scenario B (compinit never run) is unchanged pre/post-fix, showing the fix didn't touch or
regress that unrelated path.

**Project's own test**, run at both SHAs for completeness (requires one build each):

```
$ cargo build --release          # provisioning: 31.07s at head (fresh deps), 4.31s at merge-base (cached deps)
$ zsh ci/test-complete
```

Both pass (`OK`, 0.14–0.18s each) at head and at merge-base — expected, since `ci/test-complete`
only diffs the completion function's declared flags against `rg --help` output and is insensitive
to the control-flow fix (documented honestly here rather than overstated as coverage it isn't).

### Confidence: **High**

Cleanliness is well-evidenced: unchanged code on current HEAD, zero later issues/search hits, and
an explicit on-the-record moment where the author's own suspicion of a defect (in the CI test) was
wrong. The one caveat: the project's existing automated test doesn't cover this code path, so my
"clean" claim rests on manual code reading plus my own constructed reproduction, not an existing
regression test — noted above rather than hidden.

---

## Alternates considered and rejected

### Alternate for A: `BurntSushi/ripgrep` issue #1247 / rust-lang/regex (2019)

Ripgrep 11.0.0 had a confirmed infinite-loop regression on non-UTF-8 files with `\b` word-boundary
patterns (issue #1247, closed by `BurntSushi` same day: *"This was actually a regression introduced
in the underlying regex engine (as a result of fixing an unrelated bug)."*). Rejected because: (1)
the actual introducing change lives in the separate `rust-lang/regex` crate, not `ripgrep` itself,
making this closer to the "cross-file/cross-crate invariant" shape the brief explicitly excludes
from this ordinary-defect target, and (2) I could not pin down a single small (<250-line) PR in
`regex` as the introducing commit within my time budget — the fix was described only as "brought in
the updated version," not linked to one PR number I could verify. Bokeh #9232 is a strictly better
fit: single file, single function, no cross-repo reasoning required.

### Alternate for B: `mvdan/sh` PR #934 "expand: avoid panics on division by zero" (2022-10-21)

Small (94+/50-, 6 files), MIT-adjacent BSD-3-Clause Go project, 9,040 stars, 10 reviews with
substantive inline threads — a strong shape match. Rejected as the primary pick because the
review history doesn't give a genuine *false* objection: reviewer `theclapp` correctly flagged that
the initial diff still panicked on `%` (`x % 0`) and `%=` — real bugs that got fixed *within the
same PR* before merge (commits `bb7a399` → `e9df957`, review state moved from
`CHANGES_REQUESTED` to `APPROVED`). That is the review process working as intended, not a
tempting-but-wrong read of the merged diff, so it doesn't satisfy the "tempting but false objection"
requirement as cleanly as ripgrep #2957's on-the-record `vegerot` quote does. I did not fully
verify long-run cleanliness (e.g. whether `MinInt64 / -1` overflow is still unguarded in the merged
arithmetic) within my time budget, which is a second reason to prefer #2957.

---

## Summary table

| | Candidate A (ordinary defect) | Candidate B (clean) |
|---|---|---|
| Repo | bokeh/bokeh | BurntSushi/ripgrep |
| PR | #9232 | #2957 |
| Merged | 2019-10-03 | 2024-12-31 |
| Diff | 106 lines / 2 files | 33 lines / 2 files |
| License | BSD-3-Clause | Unlicense/MIT |
| Base = merge-base? | Yes, exact match | Yes, exact match |
| Confirming defect record | Issue #9494 → PR #9509 | — (clean) |
| Tempting false positives documented | 3 | 4 |
| Offline test run | Node, <1s, verified both directions | zsh, 0.29s, verified both scenarios |
| Confidence | High | High |
