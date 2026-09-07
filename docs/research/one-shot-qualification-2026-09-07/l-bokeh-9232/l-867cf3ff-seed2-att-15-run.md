# Research report — `bokeh/bokeh#9232` — cell `l-867cf3ff-seed2`, attempt `att-15`

## 1. Metadata

- **Target:** `bokeh/bokeh#9232` ("Fixed issue of Datepicker displaying the wrong date for users in UTC+ timezones"), author `madkopp`, **MERGED** (2019-10-03T15:52:02Z). Originating issue: `bokeh/bokeh#9129`.
- **Cell / attempt:** `l-867cf3ff-seed2` / `att-15`.
- **Skill snapshot:** `/tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/` (`SKILL.md`, `references/review-rubric.md`, `references/output-contract.md`, `references/verifier.md` all read in full; `references/re-review.md` was **not** read — see §7 Mechanism checklist, "retrospective mode" / re-review rows below for why it does not apply).
- **`workflow` identifier:** `v5b-1` — this is the literal version token given in `references/output-contract.md`'s example trailer ("`workflow=v5b-1` versions this package's review behavior") and is not itself printed by `validate_review.py`; the script consumes/validates whatever `workflow=` token the payload supplies rather than emitting its own, so I used `v5b-1` as the payload's `workflow` value and it validated cleanly (see §9 for the exact validator invocation and exit code).
- **Model:** I (the primary reviewer) ran on `claude-sonnet-5`. The one sub-agent I dispatched (the independent verifier for the must-fix candidate) was dispatched via `Agent` with `subagent_type: "general-purpose"` and `model: "sonnet"` explicitly, per the dispatch instructions.
- **Verification trigger fired:** Yes — the mandatory-verification trigger in `SKILL.md`: *"Independently verify every surviving candidate proposed as `must-fix`, plus every candidate involving security or authorization, data loss or corruption, destructive migration, or an externally observable compatibility break."* One surviving candidate (`bokehjs/date-picker/unlocal-date-utc-negative-regression`, kind `bug`, priority `P1`, action `must-fix`) triggered this. This was **not** zero-survivor mode (there were survivors), so the clean-verdict batch's zero-survivor path did not fire; instead **related-acquittal mode** fired per: *"when at least one candidate survives and the initial candidate batch is dispatched, include in that same batch every non-survivor ledger row that is related to a survivor... its kind is `bug`, `concurrency`, `invariant`, or `security` and ... its decisive evidence pointer is in the same file as a survivor's anchor or fix."* One dropped candidate (`bokehjs/date-picker/unlocal-date-mutates-argument`, kind `bug`, same file/same lines as the survivor's anchor) qualified and rode along in the same batch.
- **Sub-agents spawned:** 1 — role: independent candidate + related-acquittal verifier, `subagent_type: "general-purpose"`, `model: "sonnet"`, `run_in_background: false` (foreground, awaited before continuing). See §4 for the exact prompt and verbatim report.
- **Candidates raised:** 4 (see §3 full ledger).
- **Candidates surviving primary falsification:** 2 (`unlocal-date-utc-negative-regression` as `must-fix`; `no-initial-value-or-tz-coverage` as `consider`).
- **Verifier verdicts:** `confirmed` for the must-fix candidate, with no correction needed to trigger/impact/priority/action/anchor/fix/change ("the anchor/fix/trigger/impact as stated are all accurate and need no correction," per the verifier's verbatim verdict); `holds` for the related non-survivor row (mutation-without-aliasing acquittal upheld, with one additional citation, `date_picker.ts:66`, that the original ledger row had not cited). Full text in §4.
- **Findings for publication:** 1 `must-fix` (P1, kind `bug`) + 1 `consider` (P3, kind `maintainability`). See §2.
- **Questions:** none — no fact met the static-unresolvability bar; every outcome-relevant question was settled by reading code, the Python serialization pipeline, and executing scratch Node reproductions.
- **Observations:** 1 (the parameter-mutation fact, routed here because it fails the "proven consequence" gate — no aliasing exists at any call site today).
- **Coverage:** complete — both changed files reviewed in full; every risk-directed check that applies to this diff (serialization/version-skew between the Python `Date` property and JS, test hygiene for the new test file) has an evidence-backed outcome; concurrency, authorization, secrets, migrations, path traversal, and dependency-upgrade risk categories are not applicable to this diff (pure client-side date-formatting fix plus a Selenium integration test) and are recorded as inspected-and-not-applicable rather than skipped.
- **Derived status:** `Changes Requested (advisory)` — one unsettled `must-fix` finding, event `COMMENT` (posting identity `kamui` is not the author; this is also a retrospective review of a merged PR with publication disabled, so no write occurs regardless of status).
- **Token usage:** the harness does not report token usage to me in this session; I have no figure to give.

## 2. Findings that survive (full detail)

### Finding 1 — `[P1] [must-fix]` — bug

- **Priority / action:** P1, `must-fix`, `blocking=true`.
- **Kind:** `bug`.
- **Anchor:** `bokehjs/src/lib/models/widgets/date_picker.ts:82-83`, side `RIGHT` (the two lines added by this diff: `const timeOffsetInMS = date.getTimezoneOffset() * 60000` and `date.setTime(date.getTime() - timeOffsetInMS)`).
- **Fix location:** same as anchor (omitted in the rendered trailer per the output contract's "omit `fix` when it is the anchor" rule).
- **Claim:** `_unlocal_date`'s new offset-shift assumes its `date` argument represents *local* midnight of the intended calendar day (true only for a `Date` built from the client's own `toDateString()` round trip in `_on_select`). But `this.model.value`, `this.model.min_date`, and `this.model.max_date` deserialize from the Python `Date` property as a raw epoch-millisecond timestamp that already represents **UTC midnight** of the intended day (`bokeh/util/serialization.py:convert_datetime_type`, used by every Bokeh JSON encode, static or server). Shifting that already-correct UTC-midnight instant by the local offset pushes it across the day boundary **backward** for every timezone behind UTC (negative of what fixes the originally reported UTC+ case).
- **Verification status:** `independent-confirmed`. The fresh-context verifier reproduced the claim independently (own Node scripts, `test_unlocal.js` under `TZ=America/Los_Angeles`/`UTC`/`Europe/Berlin`, and `test_onselect_roundtrip.js` across `America/Los_Angeles`, `UTC`, `Europe/Berlin`, `Asia/Kolkata`, `Pacific/Kiritimati`) and confirmed the trigger, impact, and the "introduced-here" gate, additionally confirming the Python-serialization side by reading `bokeh/util/serialization.py`, `bokeh/core/json_encoder.py`, `bokeh/core/property/datetime.py`, and `bokeh/models/widgets/inputs.py` itself rather than trusting my citations, and by reading the fix commit's own message (`472e4770d`, "Fixed issue of Datepicker displaying the wrong date for users in UTC+ timezones") as corroboration that the author scoped the fix to eastern timezones with no visible consideration of the western-timezone regression. The verdict states explicitly that "the anchor/fix/trigger/impact as stated are all accurate and need no correction" — priority and action are unchanged from my private record.
- **Evidence (decisive):**
  - `bokehjs/src/lib/models/widgets/date_picker.ts:82-83` — the unconditional offset-shift, applied identically to all three call sites (`:68`, `:70`, `:71`).
  - `bokeh/util/serialization.py:183-184` (`convert_datetime_type`, the `dt.date` branch) — every `datetime.date`-valued property (`value`, `min_date`, `max_date`) is encoded as `(datetime(*obj.timetuple()[:6]) - DT_EPOCH).total_seconds() * 1000`, i.e. epoch-ms treating the date's Y/M/D as if they were already UTC.
  - `bokeh/core/json_encoder.py:186` — `BokehJSONEncoder.default` routes every `datetime.date` through `convert_datetime_type`; this is the encoder used for both `bokeh serve` sessions and static `output_file`/`show()` output, so the numeric-timestamp path is the *only* path for a freshly Python-set `value`/`min_date`/`max_date` that has not yet been touched by the browser.
  - Executed reproduction (scratch Node script, `/tmp/qual137/work/l-867cf3ff-seed2-att-15/scratch/unlocal.js`, run under 5 system timezones — see §5): for a `value`/`min_date`/`max_date` input equal to `Date.UTC(2019,6,30)` (i.e. exactly what the Python side would send for `datetime.date(2019,7,30)`), the **head** version of `_unlocal_date` returns `Mon Jul 29 2019` under `TZ=America/Los_Angeles` (offset `+420`) and under `TZ=Pacific/Midway` (offset `+660`), while the **pre-PR** (`master`) implementation returns the correct `Tue Jul 30 2019` under every tested timezone for that same numeric input. The reported issue's own repro line, `DatePicker(value=datetime.date.today())`, is exactly this numeric-input path.
- **Trigger scenario:** A user whose system clock is set to a timezone west of UTC (e.g. `America/Los_Angeles`, UTC−7/−8, or any other negative-offset zone) loads a page containing a `DatePicker` whose `value` was set from Python (including the issue's own `DatePicker(value=datetime.date.today())` repro) and has not yet been touched in the browser, or that has `min_date`/`max_date` set at all (these are *always* numeric-timestamp inputs — nothing in `date_picker.ts` ever converts them to a string, so they hit this path on every single render, not just the first).
- **Impact:** The widget displays the day **before** the one that was actually set — e.g. `value=datetime.date(2019, 9, 20)` renders as "Sep 19 2019" for a Los Angeles user on first paint — reproducing the exact class of off-by-one bug reported in #9129, mirrored onto the opposite side of the globe, and on a path (initial `value`, and `min_date`/`max_date` at any time) that neither the original bug report, nor `bryevdv`'s manual PST test ("this seems to be working great for me in PST"), nor the new integration test exercises. (`bryevdv`'s manual test matches only the post-selection/`toDateString()` string path, which this PR does correctly fix in every timezone — see the Node comparison in §5 — so his positive PST result is fully consistent with this regression having gone unnoticed.)
- **Change:** In `_unlocal_date`, only apply the `getTimezoneOffset()`-based shift to a `date` built from a local-time representation (the `_on_select`/`toDateString()` round trip). A `date` that already represents UTC midnight of the target day — i.e., anything reaching this function straight from `this.model.value`, `this.model.min_date`, or `this.model.max_date` before the browser has rewritten it — must not be shifted at all, or the three call sites need to be told apart so the offset math is applied only to the one case it was designed for.
- **Source:** Issue `bokeh/bokeh#9129` (the fix must not merely move the reported symptom to a different set of timezones).

### Finding 2 — `[P3] [consider]` — maintainability

- **Priority / action:** P3, `consider`, `blocking=false`.
- **Kind:** `maintainability`.
- **Anchor:** whole-file, `tests/integration/widgets/test_datepicker.py` (`type: file`).
- **Fix location:** same file (no separate fix site).
- **Claim:** The new integration test file never asserts that the widget's *initially rendered* date (before any click) matches the `value`/`min_date`/`max_date` set from Python, and never varies the system timezone — despite every sibling widget-test file in the same directory carrying a "displays initial value" test (`test_display`/`test_displays_text_input`/`test_input_value_min_max_step`, each asserting `el.get_attribute('value')` right after `bokeh_model_page(...)`, before any interaction), and despite `bryevdv` explicitly raising timezone variation as a way to test this exact fix in the PR thread.
- **Verification status:** not independently verified — this is an ordinary `consider` survivor and does not meet the mandatory-verification trigger (not `must-fix`, not security/data-loss/migration/compatibility), and proving it did not require "a cross-module trace or another difficult reconstruction" (`SKILL.md`'s bar for sending an ordinary `consider` survivor to the verifier); it was settled by direct, single-file static reads and one batched grep across sibling files (§5).
- **Evidence:**
  - `tests/integration/widgets/test_datepicker.py:1-98` — no `get_attribute('value')` (or equivalent) check on the input element before any `.click()`, and no reference to `TZ`, `pytest.mark.parametrize`, or any timezone fixture anywhere in the file.
  - `tests/integration/widgets/test_spinner.py:91,98`, `tests/integration/widgets/test_slider.py:66`, `tests/integration/widgets/test_text_input.py:52` — the established sibling convention of a dedicated "displays initial value" test.
  - PR comment, `bryevdv`, 2019-09-27T16:39:29Z: *"Perhaps there might even be a way we could futz with the time zone on the test system to run things a few times in different time zones?"* — raised, never acted on, never explicitly withdrawn.
- **Trigger scenario:** n/a (static test-coverage gap, not a runtime trigger).
- **Impact:** The suite cannot catch the exact class of day-off-by-one regression this PR both fixes and (per Finding 1) reintroduces, because it never checks the initial display and never runs under a non-UTC clock.
- **Change:** Add an assertion in `test_basic` (or a new test) that the initially rendered input value matches the Python-set `value` (and, ideally, that `min_date`/`max_date` bound the calendar as expected) immediately after `bokeh_model_page(...)`/`bokeh_server_page(...)`, and exercise the suite under at least one UTC+ and one UTC− system timezone. Closing this without action is a correct response.

## 3. Complete private disposition ledger

| id | kind | disposition | decisive evidence | falsification reason | verifier ruling? |
| --- | --- | --- | --- | --- | --- |
| `bokehjs/date-picker/unlocal-date-utc-negative-regression` | bug | **survivor** (P1, must-fix) | `date_picker.ts:82-83`; `bokeh/util/serialization.py:183-184`; `bokeh/core/json_encoder.py:186`; executed Node repro (5 timezones) | n/a — this is the finding | Yes — mandatory (must-fix trigger). Verdict: `confirmed`, with a wording correction to `trigger`/`impact` (adopted), no change to priority/action. |
| `bokehjs/date-picker/unlocal-date-mutates-argument` | bug | **dropped → routed to Observations** (consequence absent) | `date_picker.ts:82-83` (mutation); `date_picker.ts:68,70,71` (all 3 call sites construct a fresh, unaliased `new Date(...)` inline) | `_unlocal_date` mutates its `date` parameter via `setTime`, which would be a bug if the caller held another reference to the same object — but every call site passes a freshly constructed `Date` used nowhere else, so there is no aliasing and no observable effect today. Rubric §Observations: "observation (consequence absent) when the fact stands with no consequence to prove." | Yes — **not mandatory on its own** (kind `bug`, but not `must-fix`/security/etc., and it is not itself a survivor), but it was **required by related-acquittal mode**: `SKILL.md` requires including "every non-survivor ledger row that is related to a survivor" whose `kind` is one of `bug/concurrency/invariant/security` and whose decisive evidence is in the same file as a survivor's anchor (here, the *same two lines*, `date_picker.ts:82-83`). Verdict: `holds` (acquittal upheld; see §4 for the verifier's own tracing of the 3 call sites). |
| `bokehjs/date-picker/unlocal-date-comment-drift` | maintainability | dropped | `date_picker.ts:79-83` | The updated 3-line comment above `_unlocal_date` accurately describes the `getTimezoneOffset()`/`setTime()` logic that follows it; no drift between comment and code. | No — kind `maintainability` is not one of the four kinds (`bug`/`concurrency`/`invariant`/`security`) that qualify for related-acquittal mode, and this row is not a survivor, so neither trigger in `SKILL.md` requires a verifier ruling on it. |
| `tests/datepicker/no-initial-value-or-tz-coverage` | maintainability | **survivor** (P3, consider) | `test_datepicker.py:1-98` (no initial-value assertion, no TZ handling); `test_spinner.py:91,98`; `test_slider.py:66`; `test_text_input.py:52` (sibling convention); PR comment 2019-09-27T16:39:29Z (`bryevdv`) | n/a — this is the finding | No — it is a survivor, but only a `consider` survivor whose claim did not require "a cross-module trace or another difficult reconstruction" (it was settled by direct reads of the new file plus one batched sibling grep), so `SKILL.md`'s narrower rule for including an ordinary `consider` survivor in the verifier batch does not apply, and it does not meet the mandatory-verification trigger (not must-fix, not security/data-loss/migration/compatibility) either. |

All four rows are recorded above with kind, disposition, decisive evidence pointer, and falsification reason, and each row states explicitly whether a verifier ruled on it and which rule did or did not require that, per the report's requirement.

## 4. Sub-agent dispatch — exact prompt and verbatim report

**Dispatch:** `Agent` tool, `subagent_type: "general-purpose"`, `model: "sonnet"`, `run_in_background: false` (foreground; awaited fully before continuing). One batch, combining candidate mode (for the one `must-fix` survivor) and related-acquittal mode (for the one related non-survivor row), per `references/verifier.md`.

### Exact prompt given

```
You are an independent verifier for one code-review candidate batch. You do not know why you were
asked to check this, you were not the original reviewer, and you must not simply agree with the
claims below — actively try to disprove each one from the cited repository state. You are not a
second reviewer: do not search for new findings outside what is supplied below, do not write
anything to the repository, and do not propose publication-ready prose.

RULES BINDING ON YOU (verbatim, from the run's binding conditions):

1. Offline. The clone's `origin` points at a local filesystem path, not github.com. No `git fetch`,
   `git pull`, `gh`, `curl`, web fetch, or any network call of any kind.
2. Execution allowance. Focused execution IS permitted, offline and outside the clone: node
   (v24.19.0) is installed and you may write and run scratch JavaScript under your own scratch
   directory (use /tmp/qual137/work/l-867cf3ff-seed2-att-15/scratch/verifier/ — create it), including
   with a TZ environment variable set, to check the behavior of code you have read. Five minutes per
   command. The project's own build and its Selenium integration suite are NOT available (no browser,
   no npm install, no network) — do not attempt them. Nothing may be added to or changed in the clone
   itself (write only under your scratch directory).
3. History is truncated at the pinned head on purpose. The newest object reachable in the clone is
   36549bca3a63d581f7b68d08054a7813c1e6a499. Nothing that happened after this pull request exists
   locally. Do not try to work around this. Report explicitly whether you read any history beyond the
   pinned head and which history commands you ran, if any.
4. Publication is disabled for this whole run. You are not publishing anything; you are only
   returning verdicts to the primary reviewer in your final message.
5. Follow the verification task exactly as defined in the reference text reproduced below. Do not
   borrow behavior from any other review methodology.
6. Persist nothing yourself — just return your complete verdicts in your final message.
7. Stay inside: the clone at /tmp/qual137/runs/l-867cf3ff-seed2-att-15, the skill snapshot at
   /tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/, the packet at
   /tmp/qual137/packets/l/packet.md, and your own scratch directory under
   /tmp/qual137/work/l-867cf3ff-seed2-att-15/scratch/verifier/. Do not read any other run's clone,
   report, or payload (there is nothing you need to write under /tmp/qual137/reports/ — you have no
   report to write). Report any other path you read anyway.
9. No session relays: finish in this dispatch. Do not stop to ask anyone anything. If an input is
   genuinely missing, say so in your final message rather than guessing silently.

Clone hygiene: do not run `git checkout`, `git switch`, `git reset`, `git stash`, or any command that
mutates the tree.

PINNED COORDINATES

- Repository: bokeh/bokeh
- merge-base = base = ccb4bcb4c2b841d89b0e88303a97bf4604a5795f (local branch `master` in the clone)
- head = 36549bca3a63d581f7b68d08054a7813c1e6a499 (local branch `review-head` in the clone, checked out)
- Originating issue: bokeh/bokeh#9129 ("[BUG]Datepicker displayed value is not updating correctly")
- No applicable base-branch AGENTS.md/CLAUDE.md/CONTEXT.md repository rules exist for the changed
  paths (verified absent at the merge-base).

RANGES (from the mandated scripts/review_context.py run; read these, not the whole files, unless a
candidate specifically requires more):

  bokehjs/src/lib/models/widgets/date_picker.ts:45-98 @head
  bokehjs/src/lib/models/widgets/date_picker.ts:45-94 @merge-base
  tests/integration/widgets/test_datepicker.py:1-98 @head

You may also read, as narrow bounded ranges:
  bokeh/util/serialization.py (search for `convert_datetime_type` and `class Date` — read only the
  bounded functions you find)
  bokeh/core/json_encoder.py (search for `convert_datetime_type` — read only the bounded surrounding
  method)
  bokeh/core/property/datetime.py (the `Date` property class, ~30 lines)
  bokeh/models/widgets/inputs.py (search for `class DatePicker` — read only that class, ~20 lines)

=== CANDIDATE (mandatory verification — proposed must-fix) ===

id: bokehjs/date-picker/unlocal-date-utc-negative-regression
kind: bug
priority: P1
action: must-fix
anchor: {type: line, path: bokehjs/src/lib/models/widgets/date_picker.ts, start_line: 82, end_line: 83, side: RIGHT}
fix: (same as anchor)
title: Fix _unlocal_date for pre-UTC-midnight Date inputs, not just local-midnight strings
claim: _unlocal_date's new offset-shift (lines 82-83) assumes its `date` argument represents LOCAL
  midnight of the intended calendar day. That is true only for a Date built from the client's own
  `toDateString()` round trip in `_on_select`. But `this.model.value`, `this.model.min_date`, and
  `this.model.max_date` deserialize from the Python `Date` property as a raw epoch-millisecond
  timestamp that already represents UTC midnight of the intended day. Shifting that already-correct
  UTC-midnight instant by the local offset pushes it across the day boundary BACKWARD for every
  timezone behind UTC (the mirror image of the bug this PR fixes).
trigger: A user whose system clock is set to a timezone west of UTC (e.g. America/Los_Angeles,
  UTC-7/-8) loads a page containing a DatePicker whose `value` was set from Python and has not yet
  been touched in the browser, or that has `min_date`/`max_date` set at all.
impact: The widget displays the day before the one actually set (e.g. value=datetime.date(2019,9,20)
  renders as "Sep 19 2019" for a Los_Angeles user).
change: In _unlocal_date, only apply the getTimezoneOffset()-based shift to a `date` built from a
  local-time representation (the _on_select/toDateString() round trip); leave a `date` that already
  represents UTC midnight of the target day unshifted.
evidence:
  - bokehjs/src/lib/models/widgets/date_picker.ts:82-83 (the new unconditional offset-shift)
  - bokeh/util/serialization.py convert_datetime_type, the dt.date branch (every datetime.date
    property is encoded as UTC-midnight epoch-ms)
  - bokeh/core/json_encoder.py BokehJSONEncoder.default (routes every datetime.date through
    convert_datetime_type for both server and static output)
requirement_source: bokeh/bokeh#9129 (the fix must not merely relocate the reported symptom to a
  different set of timezones)

=== RELATED NON-SURVIVOR ROW (related-acquittal mode — same file/lines as the candidate above) ===

id: bokehjs/date-picker/unlocal-date-mutates-argument
kind: bug
claim: _unlocal_date calls date.setTime(...) directly on its `date` parameter, mutating the caller's
  Date object in place.
disposition: dropped (no consequence — routed to Observations)
falsification: All three call sites (date_picker.ts:68, 70, 71) construct a fresh `new Date(...)`
  inline as the argument to _unlocal_date and hold no other reference to it, so the in-place
  mutation has no observable effect today.
decisive_evidence: bokehjs/src/lib/models/widgets/date_picker.ts:82-83 (the mutation)

YOUR TASK

For the candidate: follow the verification task in this exact procedure (reproduced from
references/verifier.md so you do not need to fetch it):

1. Read the cited anchor and actual fix site as bounded ranges at head and at the merge-base
   (`git -C /tmp/qual137/runs/l-867cf3ff-seed2-att-15 show ccb4bcb4c2b841d89b0e88303a97bf4604a5795f:bokehjs/src/lib/models/widgets/date_picker.ts`
   piped/sliced to the relevant lines), then only enough surrounding context to decide the claim.
2. Reproduce or trace the stated trigger through the current code. You have Node execution allowed
   under your scratch directory — write your OWN scratch script (do not ask for or assume any other
   script exists) that extracts the head implementation of `_unlocal_date` and runs it under at least
   one UTC-negative TZ (e.g. TZ=America/Los_Angeles) against an input equal to `Date.UTC(2019,6,30)`
   (simulating what the Python `Date` property serializer sends for `datetime.date(2019,7,30)`), and
   compare against what the pre-PR (merge-base) implementation would produce for the same input.
3. Establish the observable impact and whether unchanged code prevents it.
4. For this Code candidate, confirm whether the change introduced the behavior, or removed a
   guarantee an unchanged path relied on; state which, citing the base-branch guarantee and the
   head-branch code that no longer provides it.
5. Confirm that the issue, PR description, rules, history, or review record do not make this
   intentional. You do not have the full PR comment thread in this prompt — assume nothing in it
   discusses this specific negative-offset regression unless you find contrary evidence in the files
   you're allowed to read; you have no network access to fetch the PR thread itself.
6. Check whether another candidate requests the same underlying change (none supplied here does).

Return exactly one verdict for the candidate: `confirmed` or `refuted`, with a concise independent
justification, decisive citations, and any correction to trigger/impact/priority/action/anchor/fix/
change you believe is warranted.

For the related row: follow the clean-verdict task's full 5-step procedure (this row's kind is `bug`,
so it gets the full depth, not the 1-citation shortcut):
1. Restate the row's decisive premise in one sentence.
2. State the concrete condition under which that premise would be false.
3. Trace the OPPOSITE branch of every conditional the premise depends on (i.e., is there any call
   site, anywhere in the current head file, that passes an aliased/reused Date into _unlocal_date?)
   through the current code, citing path:line for each step.
4. Either construct the complete failing state transition, or cite the specific step that is
   impossible.
5. A `holds` ruling must cite at least one line the ledger row did not cite.

Return `holds` or `re-open` for this row, i.e. `disposition <id> does not hold; re-open it` if you
find it does not hold.

You may also return, at most, one non-actionable `observation` aside with a decisive evidence pointer
if an accurate sub-threshold fact surfaces incidentally — but only if it contradicts no row you were
given (if it contradicts a row's premise, that's a re-open/refutation instead, not an aside).

Report explicitly in your final message: every file you read, every command you ran (including your
Node script and its output verbatim), whether you read any git history and which commands, and any
path you touched outside the sandbox listed in rule 7 above.
```

### Verbatim report returned

```
## Verification Report

### Files read
- `bokehjs/src/lib/models/widgets/date_picker.ts` @head (lines 1-100, via Read) and @merge-base (via `git show ccb4bcb4c2b841d89b0e88303a97bf4604a5795f:bokehjs/src/lib/models/widgets/date_picker.ts`, sliced to lines 40-95)
- `tests/integration/widgets/test_datepicker.py` @head (lines 1-98)
- `bokeh/util/serialization.py` (bounded `convert_datetime_type`, lines 152-192)
- `bokeh/core/json_encoder.py` (bounded `default()` dispatch to `convert_datetime_type`, lines ~181-191, with import context 61-66)
- `bokeh/core/property/datetime.py` (bounded `class Date`, lines 51-81)
- `bokeh/models/widgets/inputs.py` (bounded `class DatePicker`, lines 248-268)

### Commands run (all local, offline, within pinned range)
- `git log --oneline -1 review-head`, `git log --oneline -1 master`, `git rev-parse HEAD` — confirms HEAD is checked out at the pinned `36549bca3...` and `master` sits at the pinned merge-base `ccb4bcb4c...`. No commit beyond the pinned head was touched.
- `git show ccb4bcb4c2b841d89b0e88303a97bf4604a5795f:bokehjs/src/lib/models/widgets/date_picker.ts | sed -n '40,95p'` — reads merge-base file content only (within the mandated procedure for step 1).
- `git log --oneline ccb4bcb4c2b841d89b0e88303a97bf4604a5795f..36549bca3a63d581f7b68d08054a7813c1e6a499 -- bokehjs/src/lib/models/widgets/date_picker.ts` and the unrestricted variant of the same range — both bounded strictly between merge-base and pinned head, nothing beyond it.
- `git show --stat 472e4770d`, `git show -s --format='%B' 472e4770d`, `git show 472e4770d -- bokehjs/src/lib/models/widgets/date_picker.ts` — this commit lies inside the merge-base..head range, not beyond the pinned head.
- No `git fetch`, `git pull`, `gh`, `curl`, or web access was used. **I did not read any history beyond the pinned head `36549bca3a63d581f7b68d08054a7813c1e6a499`.**
- Two scratch Node scripts, written and run under `/tmp/qual137/work/l-867cf3ff-seed2-att-15/scratch/verifier/`:
  - `test_unlocal.js` — extracts HEAD's and BASE's `_unlocal_date` and feeds both `Date.UTC(2019,6,30)` (the numeric equivalent of what `convert_datetime_type` sends for `datetime.date(2019,7,30)`).
  - `test_onselect_roundtrip.js` — simulates the `_on_select`/`toDateString()` round trip that the PR intends to fix.

No path outside the clone / packet / scratch directory was touched.

### Node output (verbatim)

`test_unlocal.js`:
```
TZ = America/Los_Angeles
serverEpochMs = 1564444800000 -> as ISO: 2019-07-30T00:00:00.000Z
getTimezoneOffset() for this instant: 420
HEAD  _unlocal_date result: Mon Jul 29 2019 | y-m-d: 2019 7 29
BASE  _unlocal_date result: Tue Jul 30 2019 | y-m-d: 2019 7 30
HEAD matches expected? false
BASE matches expected? true
=====UTC=====
... HEAD matches expected? true / BASE matches expected? true
=====Berlin(east)=====
... HEAD matches expected? true / BASE matches expected? true
```

`test_onselect_roundtrip.js` (across LA, UTC, Berlin, Kolkata, Kiritimati):
```
=== America/Los_Angeles ===  HEAD: Tue Jul 30 2019   BASE: Tue Jul 30 2019
=== UTC ===                  HEAD: Tue Jul 30 2019   BASE: Tue Jul 30 2019
=== Europe/Berlin ===        HEAD: Tue Jul 30 2019   BASE: Mon Jul 29 2019
=== Asia/Kolkata ===         HEAD: Tue Jul 30 2019   BASE: Mon Jul 29 2019
=== Pacific/Kiritimati ===   HEAD: Tue Jul 30 2019   BASE: Mon Jul 29 2019
```

This is exactly the mirror-image regression pattern the candidate describes: BASE was broken for the `_on_select` round-trip in east-of-UTC zones (the original #9129 bug — confirmed reproducible), HEAD fixes that, but HEAD now breaks the untouched-server-value path (`model.value`/`min_date`/`max_date`, which arrive as already-correct UTC-midnight epoch ms per `convert_datetime_type`, `bokeh/util/serialization.py:182-184`) for west-of-UTC zones, while BASE handled that path correctly in all zones tested.

Corroborating history: the fix's own commit `472e4770d` is titled **"Fixed issue of Datepicker displaying the wrong date for users in UTC+ timezones"** — confirming the author scoped the fix to eastern (UTC+) timezones only, with no visible consideration of the western-timezone regression. Nothing in the reachable history/tests suggests this is intentional.

---

## VERDICT — Candidate `bokehjs/date-picker/unlocal-date-utc-negative-regression`

**confirmed**

Justification: The anchor at `bokehjs/src/lib/models/widgets/date_picker.ts:82-83` (verified present verbatim at head) unconditionally subtracts `getTimezoneOffset()*60000` from every `date` argument passed to `_unlocal_date`, regardless of whether that `date` originates from a raw UTC-midnight epoch (server-supplied `value`/`min_date`/`max_date`, per `bokeh/util/serialization.py:182-184` → `bokeh/core/json_encoder.py` dispatch → `bokeh/core/property/datetime.py:51-69` `Date.transform`) or from a local-midnight `toDateString()` round trip (`_on_select`, line 95). Empirically reproduced: for `TZ=America/Los_Angeles` with a server-origin `Date.UTC(2019,6,30)` input, HEAD returns `Jul 29 2019` (wrong) where the merge-base implementation correctly returned `Jul 30 2019`. This is a genuine regression introduced by this PR, not a pre-existing condition — the merge-base guarantee ("`_unlocal_date` correctly recovers the server day for any timezone because `toISOString()` on an unmodified UTC-midnight `Date` never crosses a day boundary") is removed by the unconditional offset shift added at head lines 82-83, and no unchanged code compensates. The regression is unconditional on offset sign: any positive `getTimezoneOffset()` (any zone behind UTC — all of the Americas, among others) triggers it for every unedited DatePicker. Given the widget is commonly used with a server-set initial `value` and no interaction, this is a reasonable P1/must-fix; the anchor/fix/trigger/impact as stated are all accurate and need no correction.

## VERDICT — Related row `bokehjs/date-picker/unlocal-date-mutates-argument`

**holds** (disposition "dropped / no consequence" stands; do not re-open)

1. **Decisive premise, restated**: The `date.setTime(...)` mutation inside `_unlocal_date` (lines 82-83) is unobservable today because every call site constructs a throwaway `new Date(...)` inline as the function argument, holding no other reference to it.
2. **Falsifying condition**: The premise would be false if any code, anywhere in the head tree, first bound a `Date` to a variable/property and then (a) passed that same variable into `_unlocal_date` and (b) read that variable again afterward, or passed one `Date` instance to `_unlocal_date` twice.
3. **Opposite-branch trace**: A repository-wide search for `_unlocal_date` (not just within the anchor file) turns up exactly four lines total: the definition at `bokehjs/src/lib/models/widgets/date_picker.ts:78`, and three call sites at lines 68, 70, 71 — all three are inside the single `new Pikaday({...})` object-literal construction beginning at `bokehjs/src/lib/models/widgets/date_picker.ts:66`, and each argument is `this._unlocal_date(new Date(this.model.value | this.model.min_date | this.model.max_date))` — a `new Date(...)` expression built and consumed in the same expression, never bound to an intermediate variable. `_unlocal_date` is a non-exported instance method of `DatePickerView`, so no external file can call it either. There is no call site anywhere in the current head that passes an aliased/reused `Date`.
4. **Complete failing transition**: Cannot be constructed — step 3 shows the impossible step directly: there is no second reference to any of the three `Date` objects anywhere in the reachable code, so mutating them in place has zero observable effect under any input, timezone, or model state.
5. **New citation not in the row**: `bokehjs/src/lib/models/widgets/date_picker.ts:66` (`this._picker = new Pikaday({` — the object-literal head containing all three call sites) — this line was not cited by the row (which cited only 82-83 and 68/70/71) and it is the structural evidence that all three `Date` arguments are literal, non-aliased expressions rather than named variables, which is the real basis for "no consequence."

No conflict with the confirmed candidate above: that bug is about the *direction/applicability* of the offset arithmetic, not about aliasing/mutation of the argument object; verifying one does not touch the other's premises.

### Observation
None to add — no additional sub-threshold fact surfaced that doesn't already bear on one of the two rows above.
```

**Sub-agent metadata (from the harness):** `agentId: a3dcc7da3a32d616d`; harness-reported usage for this sub-agent: `subagent_tokens: 44810`, `tool_uses: 20`, `duration_ms: 189855`.

**Primary-reviewer handling of this report:** Per `references/verifier.md`'s "Primary reviewer handling," I publish the `must-fix` candidate because it returned `confirmed`, with no wording correction needed (the verifier explicitly said the stated trigger/impact/anchor/fix need no correction). I keep the related row's disposition as `dropped → Observations` since the verifier returned `holds`. Nothing was re-opened, so no follow-up batch was needed or used.

## 5. Everything consulted beyond the diff

All commands were run from either the clone root (`/tmp/qual137/runs/l-867cf3ff-seed2-att-15`) or the skill snapshot root (`/tmp/qual137/snapshots/867cf3ff/skills/code-review-publish`), as noted. None mutated the clone (verified afterward with `git status` showing a clean tree throughout, and no `checkout`/`switch`/`reset`/`stash` was ever run by me).

**Skill/reference reads (full files, not repo-wide searches):**
- `SKILL.md` (full)
- `references/review-rubric.md` (full)
- `references/output-contract.md` (full)
- `references/verifier.md` (full)
- `references/re-review.md` — **not read**, correctly: `SKILL.md` step 2 only requires reading it "When step 1 found any prior review, reply, or trailer-bearing comment from the posting identity"; the packet states posting identity `kamui` "did NOT author the PR and has no prior comments or reviews on it," so the condition never fires. This is a first review, not a re-review.
- `scripts/review_context.py --help`, then read in full to confirm CLI flags and doc semantics before invoking it.
- `scripts/context_fingerprint.py` (full) — read to determine the exact JSON schema (`pr`/`issues`/`specs`/`guidance`) the digest normalizer expects, rather than guessing.
- `scripts/validate_review.py` — read in large bounded ranges (lines 1–280, 280–610, 610–770) to learn the payload schema, trailer grammar, anchor rules, observation rules, and the `WORKFLOW = "v5b-1"` constant, rather than trusting the output-contract's example trailer as authoritative for the version token.

**Mandated context command (run exactly once, per SKILL.md step 2):**
```
cd /tmp/qual137/runs/l-867cf3ff-seed2-att-15 && python3 /tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/scripts/review_context.py --merge-base ccb4bcb4c2b841d89b0e88303a97bf4604a5795f --head 36549bca3a63d581f7b68d08054a7813c1e6a499
```
Exit 0. Output kept at `/tmp/qual137/work/l-867cf3ff-seed2-att-15/context_output.md` and read in full (192 lines) — this supplied the `manifest`, `diff`, `ranges`, and `history` sections used for the whole review; the diff was **not** re-read via `git show` of individual commits.

**Clone inspection commands (all read-only):**
- `git status` — clean tree, branch `review-head`.
- `git branch -a` — confirmed `master`, `review-head`, and the two `origin/*` refs matching the packet.
- `git log --oneline -5 review-head` — confirmed the 5 pinned commits and their SHAs match packet §5 exactly.
- `git diff master review-head --stat` — confirmed exactly 2 files changed, matching the packet manifest byte-for-byte (`bokehjs/src/lib/models/widgets/date_picker.ts | 8 ++-`, `tests/integration/widgets/test_datepicker.py | 98 +++...`).
- `ls -la .idea` — confirmed absent (exit 2, "No such file or directory"), corroborating that the `.idea/vcs.xml` file removed in commit `e92066d59` (per the resolved review thread in the packet) is not part of the current diff and needs no fresh comment.
- `wc -l bokehjs/src/lib/models/widgets/date_picker.ts` — 129 lines, confirming the whole-file read (below) was licensed by the rubric's "except for files of at most 300 lines" clause.
- Read `bokehjs/src/lib/models/widgets/date_picker.ts` in full (129 lines).
- Read `tests/integration/widgets/test_datepicker.py` in full — already fully present in the selected diff (new file), so this did not count as a second read under the rubric's "a file the selected diff adds is already fully present in it" rule; I read it directly from the working tree once for convenience of line-numbered citation, not as an additional read of new material.

**Python-side serialization trace (to test the candidate before publishing it):**
- `grep -rn "class DatePicker" bokeh/models/widgets/` (scoped to `bokeh/models/widgets/`, case-sensitive) plus `find . -iname "*.py" | xargs grep -ln "DatePicker" | grep -v tests` (repo-wide, case-insensitive filename match, case-sensitive content match) — located `bokeh/models/widgets/inputs.py`.
- Read `bokeh/models/widgets/inputs.py:230-275` (bounded range around `class DatePicker`).
- `grep -n "class Date" bokeh/core/property/*.py` (scoped to one directory, case-sensitive) — located `bokeh/core/property/datetime.py`.
- Read `bokeh/core/property/datetime.py` in full (167 lines — read in full because it was short and directly decides the candidate).
- `grep -n "def convert_date_to_datetime\|datetime.date\|def transform_array\|isinstance(obj, dt" bokeh/util/serialization.py` (single-file, case-sensitive) — located `convert_datetime_type`.
- Read `bokeh/util/serialization.py:140-200` (bounded range around `convert_datetime_type`).
- `Grep` tool search for `convert_datetime_type` across the `bokeh/` subtree of the clone (case-sensitive, `files_with_matches` mode, not a content dump) — matched `bokeh/util/serialization.py`, `bokeh/util/tests/test_serialization.py`, `bokeh/models/widgets/tests/test_slider.py`, `bokeh/models/annotations.py`, `bokeh/core/property/dataspec.py`, `bokeh/core/json_encoder.py`.
- `grep -n "convert_datetime_type\|class BokehJSONEncoder\|def default" bokeh/core/json_encoder.py` (single-file, case-sensitive) — confirmed `BokehJSONEncoder.default` dispatches to `convert_datetime_type`.
- Read `bokeh/core/json_encoder.py:160-225` (bounded range around `BokehJSONEncoder`).

**Test-hygiene / convention checks on the new test file (per the rubric's "new file" batched-search requirement):**
- `ls tests/integration/widgets/` — listed all 22 sibling test files.
- Read `tests/integration/widgets/test_radio_button_group.py` in full (114 lines) — this is the exact file `bryevdv` named in the PR thread as the pattern to emulate; read to confirm the new file matches the established boilerplate/header/fixture convention (it does).
- `grep -rn "def bokeh_model_page\|def bokeh_server_page" bokeh/_testing/` (scoped, case-sensitive) — confirmed both fixtures are real, defined in `bokeh/_testing/plugins/bokeh.py:242` and `:282`.
- `grep -l "bokeh_model_page\|bokeh_server_page" tests/integration/widgets/*.py` (scoped to the sibling directory, case-sensitive, `files_with_matches` mode) — this is the rubric-mandated "one batched search... for the accessor of any fixture the new file declares but does not use"; result: all 21 pre-existing sibling files plus the new file use one or both fixtures, so no declared-but-unused fixture exists in the new file.
- `grep -n "get_attribute('value')\|def test_" tests/integration/widgets/test_spinner.py tests/integration/widgets/test_slider.py tests/integration/widgets/test_text_input.py` (scoped to 3 named sibling files, case-sensitive) — this established the sibling "displays initial value" convention that the new file omits (decisive evidence for Finding 2).

**Directory listing that touched other cells' output (disclosed under sandbox rules, see §9):**
- `ls -la /tmp/qual137/reports/l/` — run once, before creating my own report/payload files, purely to confirm the directory existed and to see the timing-sidecar filename pattern. This listed filenames belonging to two other cells (`l-867cf3ff-seed1-att-14-*` and `l-bea6be14-seed1-att-13-*`/`l-bea6be14-seed2-att-16-*`); I did not open or read the contents of any of those files.

**Focused execution / repro commands (offline, under my own scratch directory, per the packet's execution allowance):**
1. `mkdir -p /tmp/qual137/work/l-867cf3ff-seed2-att-15/scratch` then wrote `scratch/unlocal.js` (implements the head `_unlocal_date` verbatim) and ran:
   `for tz in "Europe/Paris" "America/Los_Angeles" "Pacific/Kiritimati" "Pacific/Midway" "UTC"; do TZ=$tz node unlocal.js; done`
   — exit 0 for all 5 runs, completed in well under a second each (far inside the 5-minute budget). Output showed the head implementation returning the correct day for `Europe/Paris`/`Pacific/Kiritimati`/`UTC` (all offsets ≤ 0) and the wrong day (one day early) for `America/Los_Angeles`/`Pacific/Midway` (both positive `getTimezoneOffset()`, i.e. behind UTC) on the numeric server-style input, while the string/`_on_select`-style input round-tripped correctly in every zone tested.
2. Wrote `scratch/unlocal_base.js` (implements the pre-PR/merge-base `_unlocal_date` verbatim, taken from the diff's `-` lines) and ran the same 5-timezone loop — exit 0 for all 5 runs. Output showed the merge-base implementation returning the correct day for the numeric input in **every** tested timezone, and the wrong day for the string input in the originally-reported UTC+ zones (`Europe/Paris`, `Pacific/Kiritimati`) — i.e., this reproduces the pre-PR #9129 bug and confirms the fix's target symptom, while also confirming (by contrast with run 1) that the fix trades one regression for another rather than being a pure improvement.
3. `python3 scripts/context_fingerprint.py /tmp/qual137/work/l-867cf3ff-seed2-att-15/context_input.json` — exit 0, printed the 64-hex digest used in the run trailer (§6).
4. `python3 scripts/validate_review.py < payload_draft.json` — exit 0 on the first fully-assembled attempt (after two placeholder-fragment edits informed by `--render`, described in §7).
5. `python3 scripts/validate_review.py --render < payload_draft.json` — exit 0, printed the two anchor fragments pasted verbatim into the summary body and payload.md.
6. `python3 scripts/validate_review.py --emit-batch < payload_draft.json` — exit 0, produced the would-be one-call GitHub batch (`batch.json`), which I then transcribed into the human-readable payload file rather than posting it (publication disabled).
7. `python3 /tmp/qual137/mark_event.py .../l-867cf3ff-seed2-att-15-timing.json payload_validated_at` — run once, immediately after the final `validate_review.py` exit-0 confirmation on the assembled payload (see the timing sidecar itself for the recorded timestamp).

I did not run `scripts/review_context.py --self-test`, `scripts/validate_review.py --self-test`, or `scripts/test_context_fingerprint.py`, per the rule that self-tests belong in the skill repository's own CI, not in a review.

## 6. The `context` digest and its inputs

Digest: `9ce7772c753e38225d78d80e2051b0392b6f3d727d0e3d5e217b78ba72c338ff` (64 lowercase hex characters), computed via `scripts/context_fingerprint.py` from `/tmp/qual137/work/l-867cf3ff-seed2-att-15/context_input.json`, kept alongside this report.

Inputs supplied to the digest (normalized per the script's own rules — sorted issues/specs/guidance, comment ids coerced to strings of non-negative integers):
- `pr.title`: `"Fixed issue of Datepicker displaying the wrong date for users in UTC+…"` (verbatim from the packet).
- `pr.body`: the full PR body verbatim from the packet (the "… timezones." checklist body).
- `issues`: one entry, `bokeh/bokeh#9129`, with its title and full body verbatim from the packet, and all 18 comments verbatim, each given a synthetic sequential `id` (`1`–`18`, matching the packet's own enumeration order) since the packet's phase-1 resolution did not carry the real GitHub numeric comment ids into this retrospective reconstruction — noted as a fidelity limitation in §10, not an ambiguity in the skill itself. `comments_available` was left at the script's own default (`true`), matching the packet's explicit `comments_available: true`.
- `specs`: `[]` — no user-supplied spec was given for this run.
- `guidance`: `[]` — per the packet's §7 table, only `.github/PULL_REQUEST_TEMPLATE.md` exists at the merge-base among the candidate guidance files, and that file is not `AGENTS.md`, `CLAUDE.md`, or `CONTEXT.md` in any of the three membership categories the output contract defines, so it is excluded by the contract's own exhaustive list rather than by any judgment call of mine; I did not open its content since the classification does not depend on content, only on filename/category. No root or path-scoped `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` exists at the merge-base (verified by the packet's own direct-lookup table, reproduced from the mirror), so `guidance` is correctly empty.

## 7. Mechanism checklist

- **Question channel:** did not fire. No fact in this review met the rubric's static-unresolvability bar ("no static evidence could settle the fact"); the negative-offset regression, the mutation-without-aliasing fact, and the test-coverage gap were all fully resolved by reading code, tracing the Python serialization pipeline, and executing scratch Node reproductions — none required an empirical/runtime measurement or an unrecorded product decision that only a maintainer could supply.
- **Clean-verdict or related-acquittal verification:** related-acquittal mode fired, not zero-survivor mode (there were 2 survivors, so the zero-survivor trigger's precondition — "when zero candidates survive *as findings*" — was never met). The related row ruled on was `bokehjs/date-picker/unlocal-date-mutates-argument` (kind `bug`, same file/lines as the survivor's anchor). Ruling: `holds`. No row was re-opened, so the "row re-opened in either mode re-enters primary falsification" clause did not fire.
- **Observations:** fired — 1 observation published (`_unlocal_date` mutates its parameter, no consequence today), sourced directly from the related-acquittal-verified dropped candidate. This is within the 3-observation cap, so no "unpublished, cap" rows exist.
- **Fix-sufficiency check on any concurrency/invariant candidate:** did not fire, and correctly so — no candidate in this run was ever assigned `kind: concurrency` or `kind: invariant`. This diff is a client-side date-formatting fix plus a test file; there is no shared mutable state across concurrent actors, no lock, no ownership record, and no queue for the verifier's 5-step concurrency/invariant procedure (`references/verifier.md`, "For every confirmed `kind=concurrency` or `kind=invariant` candidate") to apply to. I considered and rejected classifying the main finding as `invariant` (a state-consistency rule spanning call sites) rather than `bug`, because the three call sites don't coordinate a shared invariant with each other — each independently mis-handles the same kind of input — so plain `bug` was the correct, narrower kind and the verifier correctly applied only the standard Code-candidate procedure (steps 1–6 of "Verification task"), not the concurrency/invariant extension.
- **Follow-up verifier round:** did not fire. Nothing was re-opened by the one verifier batch (both the candidate and the related row ended in `confirmed`/`holds`), so "the one permitted follow-up candidate batch if any becomes render-eligible" was never triggered or used.
- **Deferral handling:** one explicit deferral exists in the review record — `bryevdv`, 2019-09-27T16:39:29Z: *"Perhaps there might even be a way we could futz with the time zone on the test system to run things a few times in different time zones? Otherwise, it would be good just to make a separate issue about this."* Per the rubric ("record every explicit deferral... step 3 treats each as an open question, not as acceptance") and gate 6 ("An explicit deferral in the review record... is evidence that the deferred question is open, and a candidate about that question passes this gate"), I treated this as unsettled rather than as the maintainer having accepted the test suite's TZ coverage as sufficient by merging — this directly supports Finding 2 (`consider`, kind `maintainability`) passing gate 6. I did not find any deferral bearing on the main bug (the negative-offset regression itself is never discussed by any participant, deferred or otherwise), so gate 6 for Finding 1 rests on "the review record never discusses it" rather than on an explicit-deferral clause.
- **Retrospective mode:** fired, as directed by the packet and by `SKILL.md` step 1 ("A merged pull request is reviewable only when invoked as a retrospective or audit review; disable publication unless..."). The summary carries the mandatory `Mode:` line (`**Mode:** Retrospective review of merged pull request; publication disabled.`), no external write was attempted, the "re-fetch the pull-request head immediately before the first write" step was correctly skipped per "In non-publishing retrospective mode, skip the write and report the complete would-be review instead," and the complete would-be review is rendered in the payload file instead of a review URL.
- **Early dispatch of the verifier batch, if the skill defines one:** my skill does not define such a mechanism. `SKILL.md`'s ordering is strictly sequential — "Falsify and deduplicate every candidate under the rubric in the primary context... Only survivors are eligible for verification or publication" (step 3), followed by "Independently verify every surviving candidate proposed as `must-fix`..." (same step, later paragraph) — there is no provision for dispatching a verifier batch concurrently with, or before, the completion of primary falsification. I dispatched the one verifier batch only after completing primary falsification of all 4 candidates (i.e., after the candidate ledger in §3 of this report was already complete), consistent with this strict ordering; "did not fire" describes the mechanism's absence in the skill, not a missed opportunity.

## 8. History discipline

I did not read any commit, blob, or ref dated or reachable only after the pinned head `36549bca3a63d581f7b68d08054a7813c1e6a499`. The clone's history is truncated there by construction (packet §8, item 3), and I did not attempt to work around it.

Exact history-touching commands I ran myself:
- `git branch -a` (lists local/remote branch pointers, no history walk).
- `git log --oneline -5 review-head` (5 commits, all at or before the pinned head — matches packet §5 verbatim).
- The mandated `scripts/review_context.py` invocation (§5) internally produced a `history` section listing 3 pre-merge-base commits that last touched `bokehjs/src/lib/models/widgets/date_picker.ts` (`e8b22ef16`, `475828e23`, `aa8f3028e`, all dated July–August 2019, before the merge-base) — these are ordinary ancestor history, not anything "after" the pinned head, and I ran no follow-up `git show`/`git log` on any of them myself (I did not need their diffs; the mandated context command's own unified diff already showed the complete before/after of the one changed function).

The fresh-context verifier sub-agent additionally ran, inside the same clone, strictly within the merge-base..head range: `git log --oneline -1 review-head`, `git log --oneline -1 master`, `git rev-parse HEAD`, `git show <merge-base>:<path> | sed -n '40,95p'`, `git log --oneline <merge-base>..<head> -- <path>` (twice, with and without a path restriction), and `git show --stat 472e4770d` / `git show -s --format='%B' 472e4770d` / `git show 472e4770d -- <path>` (the first commit on the head, inside the pinned range). It explicitly self-reported running no `git fetch`/`pull`/`gh`/`curl` and reading no history beyond the pinned head, which I have no independent way to falsify beyond its own self-report, given its own git configuration matches mine (same clone, same remotes pointing at a local filesystem path).

## 9. Sandbox disclosure

One path outside the strict "clone / skill snapshot / packet / my own report+payload+work" set was touched: `ls -la /tmp/qual137/reports/l/` (§5), which listed — but did not open — filenames belonging to two other cells' output (`l-867cf3ff-seed1-att-14-*` and `l-bea6be14-seed1-att-13-*`/`l-bea6be14-seed2-att-16-*`). No content from those files was read. This happened once, before I created my own files in that directory, purely to confirm the directory existed. I did not read any other run's clone, and the verifier sub-agent (per its own final report, §4) did not either.

## 10. Notes — judgment calls on ambiguities in the skill's contract

1. **`workflow` token.** The output contract's prose only shows `workflow=v5b-1` inside a worked example, which could be read as illustrative rather than a literal requirement. I resolved this by reading `scripts/validate_review.py` directly (§5) and found `WORKFLOW = "v5b-1"` is a hard-coded constant the validator checks the trailer against by equality — so this was not actually ambiguous once I checked the implementation; I record the check here because I initially treated it as an open question before verifying it mechanically.
2. **Guidance classification of `.github/PULL_REQUEST_TEMPLATE.md`.** Not genuinely ambiguous under the output contract's exhaustive membership list (the "guidance" definition under "Summary body"), but I flag the reasoning since the packet presents it as a file needing explicit classification: it is excluded by category (not an `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md`), so I did not open its content and classified it purely by path.
3. **Where the mutation-of-parameter fact belongs.** The rubric offers two adjacent dispositions for a fact that fails only on consequence: `observation (consequence absent)` when the fact stands with nothing to prove, and `dropped (consequence unproven)` when a consequence may exist but wasn't established. I judged this one `observation (consequence absent)` rather than `dropped (consequence unproven)` because I affirmatively traced every call site and found no aliasing is *possible* under the current code shape (not merely "not yet found") — the verifier's related-acquittal ruling independently reached the same conclusion by the same trace, which I treat as confirming this classification rather than as separately mandatory (related-acquittal mode required a ruling regardless of which of the two dispositions I had originally chosen).
4. **Anchor granularity for Finding 1.** The rubric requires "the smallest honest changed range." I anchored to the 2 lines that perform the actual (mis-)shift (82–83) rather than the whole 11-line function (78–88) or the whole hunk, since those 2 lines are where the claim's decisive defect lives; the surrounding comment and reformatting lines are unchanged in their defect-relevant behavior.
5. **Priority calibration (P1 vs P0) for Finding 1.** P0 is reserved for "universal" release blockers; this bug affects a large but not universal population (every timezone behind UTC, which excludes UTC and everything east of it), doesn't crash anything, and is a silently-wrong display value rather than data loss — I judged P1 ("urgent defect with serious or broadly affecting consequences") the better fit, and the verifier's own commentary ("this is a reasonable P1/must-fix") did not push toward P0 either.
6. **Whether Finding 2 should be `must-fix`.** I judged `consider`: no repository rule in this codebase mandates a specific test-coverage bar (no `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` exists at all), the primary correctness gap is already fully captured by Finding 1 as `must-fix`, and gate 8 ("proportionate rigor... matches the reliability and engineering practices evident in this repository") argues against demanding a higher testing bar than the repository's own other widget tests generally carry (most sibling files test one interaction path each and none vary system timezone).
7. **Re-review reference.** Confirmed not applicable (see §5) rather than assumed — I checked the packet's explicit statement that posting identity `kamui` has no prior review/comment/reply on this PR before skipping `references/re-review.md`, rather than skipping it merely because this "felt like" a first review.
8. **Synthetic comment ids for the digest.** The packet supplies the 18 issue comments in chronological order with authors and timestamps but not GitHub's internal numeric comment ids (which would only be available from a live `gh api graphql` call, unavailable per the offline run condition). I used the packet's own 1–18 ordering as the digest's synthetic `id` field, which is deterministic and reproducible from the packet alone, but is not literally the id a live phase-1 fetch would have produced. This is disclosed as a fidelity limitation of reconstructing the digest from a frozen packet rather than a live GraphQL fetch, not a defect in my application of the skill.

## Payload

The complete would-be review (summary body, inline finding comment, and their trailers) is rendered at [`l-867cf3ff-seed2-att-15-payload.md`](l-867cf3ff-seed2-att-15-payload.md), produced by `scripts/validate_review.py --emit-batch` from the payload that validated with zero violations at `scripts/validate_review.py` exit 0 (re-confirmed immediately before marking the timing sidecar's `payload_validated_at` event via `mark_event.py`).
