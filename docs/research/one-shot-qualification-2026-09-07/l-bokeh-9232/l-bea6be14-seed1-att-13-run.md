# Research report — `l-bea6be14-seed1-att-13` (bokeh/bokeh#9232)

**Status: COMPLETE.** Payload validated (`scripts/validate_review.py` exit 0), `payload_validated_at` marked in the timing sidecar. One `must-fix` finding, independently confirmed. Derived status: **Changes Requested (advisory)**. Payload: [`l-bea6be14-seed1-att-13-payload.md`](l-bea6be14-seed1-att-13-payload.md).

## 1. Metadata

- Target: `bokeh/bokeh#9232` ("Fixed issue of Datepicker displaying the wrong date for users in UTC+ timezones.")
- Cell: `l-bea6be14-seed1`, attempt `att-13`
- Skill snapshot: `/tmp/qual137/snapshots/bea6be14/skills/code-review-publish/`
- `workflow` identifier: **`v5b-10`** (from `references/output-contract.md`'s example trailer: `` `workflow=v5b-10` versions this package's review behavior``; the validator embeds/checks this same string — confirmed against `scripts/validate_review.py` at rendering time below).
- Model: I (the primary reviewer, this whole run) ran on **claude-sonnet-5**. The one sub-agent I dispatch (the mandatory verifier for the surviving `must-fix` candidate) also runs on **claude-sonnet-5**, invoked with `subagent_type: "general-purpose"`, `model: "sonnet"`, `run_in_background: false`, per the cell's run conditions and rule 8.
- Posting identity: `kamui` (third party, did not author the PR, has no prior comments/reviews on it per the packet) → first review, **not** a re-review. `references/re-review.md` was read only to *confirm* it does not apply (its trigger condition — "a prior review, reply, or trailer-bearing comment from the posting identity" — is not met; `bryevdv`/`madkopp` prior review activity belongs to the author and a maintainer, not to `kamui`). Confirmed empirically: `git log`/`git branch -a`/`git status` on the clone show only the pinned commits and clean tree; no re-fetch was attempted (offline).
- Target state: `MERGED` (2019-10-03T15:52:02Z) → retrospective review, publication disabled per packet and per `SKILL.md` step 1 / Boundaries section. `Mode` line included in the rendered summary.
- Event if this were published: `COMMENT` (ordinary third-party review; no gating authorization exists or is claimed).

## 2. Skill reading order followed

Read, in full, from the skill snapshot directory only:
1. `SKILL.md`
2. `references/review-rubric.md`
3. `references/output-contract.md`
4. `references/verifier.md`
5. `references/conformance.md` — read to confirm it does **not** apply: no issue, PR text, or repository convention makes this change conform to a versioned artifact (stub/binding/SDK/schema/generated source). No conformance rows added.
6. `references/verifier-concurrency.md` — read to confirm it does **not** apply: no candidate's `kind` is `concurrency` or `invariant` (the surviving candidate is `kind: bug`, a pure date-arithmetic defect, not a cross-path state/lock rule).
7. `references/re-review.md` — read to confirm it does **not** apply (see above).

No other review skill's references were consulted. No behavior was borrowed from `code-review-publish-legacy` or any other skill.

## 3. Step 1 — Pin the review

Fully satisfied by the packet (`/tmp/qual137/packets/l/packet.md`), per the cell's binding run conditions (§1 "Phase 1 (target resolution) has already been performed") and per the cell dispatch's rule that phase 1 is satisfied by the packet including its `merged` field. No network calls were made or attempted. Pinned identity used verbatim:

| | |
|---|---|
| Repository | `bokeh/bokeh`, `summary.repository_url = https://github.com/bokeh/bokeh` |
| PR | #9232 |
| Head SHA | `36549bca3a63d581f7b68d08054a7813c1e6a499` |
| Base ref | `master` |
| Base SHA / merge-base | `ccb4bcb4c2b841d89b0e88303a97bf4604a5795f` (identical) |
| `state` / `merged` | `MERGED` / `true` |
| Originating issue | `bokeh/bokeh#9129` (closing reference in PR body) |
| Posting identity | `kamui` — first review, retrospective, publication disabled |

Repository guidance at merge-base (packet §7, verified there by direct lookup in the mirror): none of `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, `CONTRIBUTING.md`, `CODEOWNERS` exist at the merge-base for any ancestor of the changed paths. Only `.github/PULL_REQUEST_TEMPLATE.md` exists, which is **not** one of the three categories the output contract's `guidance` digest field enumerates (root `AGENTS.md`/`CLAUDE.md`, path-scoped `AGENTS.md`/`CLAUDE.md` in an ancestor of a changed path, root `CONTEXT.md`). I classified it as excluded from `guidance` on that basis and did not read it as a review standard (a PR template is not an instruction file to changed-path authors in the rubric's Repository rules sense; it is the *submission* form the author filled in, already reproduced verbatim in the packet). `guidance = []` (empty array) in the context-digest input below.

## 4. Step 2 — Private review context

### 4.1 Context digest (`context`)

No raw `forge-*.json` pages were available in this sandbox — only the orchestrator-normalized `packet.md`. Per the cell's rule "Use its pinned values verbatim; do not re-resolve anything" and per `context_fingerprint.py`'s documented fallback ("On a forge without that packet, supply `pr`, `issues`, `specs`, and `guidance` directly from the exact reviewed inputs"), I built the digest input directly from the packet's verbatim text rather than running `forge_packet.py normalize` (there is no saved forge page to normalize). I wrote a small parsing script (`/tmp/qual137/work/l-bea6be14-seed1-att-13/build_fingerprint_input.py`) that mechanically extracts, from `packet.md`, the fenced-code-block bodies of:
- the PR body (packet §3, verbatim between the fences),
- the issue body (packet §4, verbatim between the fences),
- all 18 issue comments (packet §4, each `**N.** <timestamp> · `<author>`` header followed by its fenced body), preserving author, ISO timestamp, and body text exactly.

This produced `/tmp/qual137/work/l-bea6be14-seed1-att-13/fingerprint_input.json` with:
```json
{
  "pr": {"title": "Fixed issue of Datepicker displaying the wrong date for users in UTC+ timezones.", "body": "<packet §3 verbatim>"},
  "issues": [{"coordinate": "bokeh/bokeh#9129", "title": "[BUG]Datepicker displayed value is not updating correctly", "body": "<packet §4 verbatim>", "comments": [18 comments, id=1..18, author, created_at=updated_at (no edits recorded in packet), body]}],
  "specs": [],
  "guidance": []
}
```
Command and result:
```
$ python3 scripts/context_fingerprint.py /tmp/qual137/work/l-bea6be14-seed1-att-13/fingerprint_input.json
67da918baa5c99b51074a5c2571c86b72d41fbd5a85a7413003e00d89cf65a51
```
exit 0.

**`context = 67da918baa5c99b51074a5c2571c86b72d41fbd5a85a7413003e00d89cf65a51`**, computed **once**, per SKILL.md step 3's instruction to compute it once from the packet.

**Judgment calls / limitations disclosed for this digest (see Notes §11 also):**
- The packet's issue comments are numbered 1–18 in display order but carry **no forge `fullDatabaseId`/`databaseId`**. `context_fingerprint.py` requires a non-negative integer `id` per comment (used only for the comment's own sort key, not otherwise semantically load-bearing in the digest beyond ordering + dedup). I used the packet's own 1-based display order as the synthetic `id`, which reproduces the *same relative order* the real numeric ids would (comments are already listed in chronological/creation order in the packet, and GitHub's `fullDatabaseId`s are monotonic with creation time), so the digest's `comments` array sorts identically to how it would with real forge ids. This makes the digest a faithful, order-correct fingerprint of the pinned inputs, but it is **not bit-identical** to whatever digest an earlier phase-1 run with real forge ids would have produced, since `id` is embedded (as a string) inside each normalized comment object. I flag this rather than silently presenting the digest as a byte-for-byte reproduction of a hypothetical live-fetch run.
- `updated_at` was set equal to `created_at` for every comment, since the packet records no edits (no `lastEditedAt` shown, and the "prior review" section's mandatory note only discusses already-fixed review feedback, not issue-comment edits).
- The PR title used is the literal string from commit 1's message (`Fixed issue of Datepicker displaying the wrong date for users in UTC+ timezones.`), because the packet's own metadata table renders the title with a mid-word ellipsis (`...UTC+…`) that is evidently a table-width truncation artifact, not the literal pinned title; the commit message is the only complete, unambiguous rendering of the same string in the packet. This is a judgment call, recorded here and in Notes §11.

### 4.2 Private review context build (`review_context.py`)

First review (no `--prior-head`). Ran, from inside the clone, exactly once:
```
STORE=/var/folders/.../tmp.cQ24Bf47AZ/review-context-36549bca3a63d581f7b68d08054a7813c1e6a499.json
python3 .../scripts/review_context.py --merge-base ccb4bcb4c2b841d89b0e88303a97bf4604a5795f --head 36549bca3a63d581f7b68d08054a7813c1e6a499 --store "$STORE"
```
Exit 0. Output printed in full (not withheld — the whole diff fit under the 24000-byte bound):

- **manifest** (2 files): `M bokehjs/src/lib/models/widgets/date_picker.ts +6 -2 new=no lines=129`; `A tests/integration/widgets/test_datepicker.py +98 -0 new=yes lines=98`.
- **diff**: complete unified diff for both files (reproduced in full in my working notes; not re-pasted here — see §5).
- **ranges**: `bokehjs/src/lib/models/widgets/date_picker.ts:45-98 @head`; `bokehjs/src/lib/models/widgets/date_picker.ts:45-94 @merge-base`; `tests/integration/widgets/test_datepicker.py:1-98 @head`.
- **history** (pre-merge-base, i.e. ancestor history — not beyond the pinned head): `date_picker.ts` last touched by `e8b22ef16` (2019-08-19, #9171), `475828e23` (2019-07-13, #9062), `aa8f3028e` (2019-06-12, #8989) — none relevant to the reviewed hunk (init-code generation, prior datepicker update, CSS modularization).
- **chunks**: `diff coverage: complete (2/2 chunks consumed)` — no `missing` chunks, no truncation, no omitted patch.

Both changed files are fully covered by the printed diff plus (for `date_picker.ts`, which is 129 lines, i.e. ≤300) a full-file read from the clone (`cat -n bokehjs/src/lib/models/widgets/date_picker.ts`), which the rubric's Complete inspection section permits without further justification for files at or under 300 lines. `test_datepicker.py` is a wholly new 98-line file already fully present in the diff (rubric: "A file the diff adds is already fully present in it and is not read again").

### 4.3 Requirement ledger (rubric's Issue fit)

Sources, in required order: (1) originating issue `bokeh/bokeh#9129`; (2) PR title/body (packet §3, template checklist only, no free-form description beyond `- [x] issues: fixes #9129`). No user-supplied spec. No versioned-artifact conformance (`conformance.md` does not apply — no stub/binding/schema/generated-source tracking is implicated).

| Row | Source coordinate | Class | Outcome required | Disposition | Evidence |
|---|---|---|---|---|---|
| R1 | `issue-9129/body` + comments 1–7 (`bryevdv`, `PierreLB6`, `madkopp`) | acceptance requirement | For a user in a positive-UTC-offset timezone (UTC+, e.g. France, UK-BST), the DatePicker's **displayed** value must update to the just-selected day on the first click, not the selected day minus one, without requiring a second identical selection. | **met** | `bokehjs/src/lib/models/widgets/date_picker.ts:82-83` (added offset shift) — verified by direct execution (Node, `TZ=Europe/Paris`, `TZ=Pacific/Auckland`): the old `_unlocal_date` mis-renders the round-tripped selection as the prior day, the new one renders it correctly. See §5.3 for the full repro. |
| R2 | `pr-title` / `pr-body/"fixes #9129"` | (restates R1) | — | no separate row — rubric: "a pull-request sentence that restates an issue requirement adds none." | — |
| R3 | `pr-body` checklist `"tests added / passed"` (left unchecked `[ ]` at PR-open time) | supporting assertion, not an acceptance requirement (template boilerplate, no concrete outcome named) | — | not a ledger row — no checkable named outcome per rubric ("a generic word... with no named referent produces no row"); superseded in fact by later commits 4–5 which add `tests/integration/widgets/test_datepicker.py`. | — |
| R4 | `pr-body` checklist `"release document entry (if new feature or API change)"` (unchecked) | non-goal / not applicable | This is a bug fix, not a new feature or API change, so no release doc is required. | met (non-goal correctly not triggered) | No API surface added (verified: `date_picker.ts` diff only touches a private `_unlocal_date` method's body; no exported symbol changes; `tests/integration/widgets/test_datepicker.py` is new but is a test file, not public API). |

**Issue fit summary:** R1 (the only substantive acceptance requirement) is **met** — the code demonstrably now displays the correct day for positive-UTC-offset users on first selection, per direct execution. However, primary falsification (step 5 below) finds that the *implementation* of that fix removes a merge-base guarantee for a different, unstated population (negative-UTC-offset users), which is a **Code** bug candidate under gate 2, not a failure of R1 itself — the issue's own stated requirement is satisfied; the regression is an unintended side effect the issue never mentions and the review record never discusses.

## 5. Step 3 — Review once, then falsify

The diff was read exactly once from the `review_context.py --store` output (§4.2); it was never re-read via `git show` of individual commits and never re-generated. `--function-context` (the tool's default hunk framing) already showed each hunk's enclosing method (`_unlocal_date`, and the whole new test file), so per the rubric I additionally read the **whole** `date_picker.ts` file (129 lines, ≤300, permitted without further justification) to see the two call sites of `_unlocal_date` (`render()`, lines 68/70–71) and the unchanged `_on_select` (lines 90–97) that supplies the round-trip value. `test_datepicker.py` needed no further read: a wholly new 98-line file is already fully present in the diff.

### 5.1 Risk-led discovery

Named promised behavior (from R1): "the displayed value updates correctly for UTC+ users." Risk signals from the rubric's Complete inspection list that this diff puts at stake: none of authorization/secrets/path-normalization/migrations/concurrency/external-contracts apply to a pure client-side date-formatting helper. The one applicable signal is **test and generated-artifact hygiene** (new test file) and, more importantly, the rubric's general falsification duty to check "whether unchanged surrounding code prevents the failure" and "the base-branch guarantee" for gate 2 — which is exactly what surfaced the survivor below. Two targeted bounded reads were made under this rule, each recorded here with its outcome and each counted once in file accounting:

1. **Read:** `render()`'s two other call sites of `_unlocal_date` (`defaultDate`, `minDate`, `maxDate`, lines 68, 70–71 of `date_picker.ts`, already inside the full-file read above). **Outcome:** all three pass the same `_unlocal_date` function; there is no branch anywhere that treats the initial `value`/`min_date`/`max_date` path differently from the post-selection round-trip path, so a change to `_unlocal_date` is not scoped to one call site — settling the question of whether the fix's blast radius includes the initial-value display, not just the post-click redisplay.
2. **Read:** the Python-side serialization of `DatePicker.value`/`min_date`/`max_date` (`bokeh/core/property/datetime.py:51-76`, `bokeh/util/serialization.py:152-184`), to establish what numeric representation the initial `value`/`min_date`/`max_date` actually arrive at the browser as. **Outcome:** `Date.transform()` accepts a `datetime.date`/`datetime.datetime` unchanged (only strings/numbers are coerced), and `convert_datetime_type()` serializes any `datetime.date`/`datetime.datetime` via `(dt.datetime(*obj.timetuple()[:6]) - DT_EPOCH).total_seconds() * 1000` — i.e. treating the naive Python date as if it were UTC midnight, with **no timezone parameter or adjustment**. This settles that `new Date(this.model.value)` in the browser receives a timestamp representing exact UTC midnight for the configured day, in every browser timezone — the scenario the base-branch `_unlocal_date` (`date.toISOString().substr(0,10)`) was specifically written to handle correctly (its own comment: "the date comes in as a UTC timestamp").

Both reads settled their stated uncertainty; neither risk was widened further.

### 5.2 Candidates raised and falsified

**Candidate C1 — survivor.**

- **claim:** Unconditionally shifting `date` by `date.getTimezoneOffset() * 60000` before deriving the calendar-day string makes `_unlocal_date` return the *previous* day whenever its input already represents UTC midnight (the initial `value`, `min_date`, and `max_date`, per §5.1.2) and the browser's local timezone is *behind* UTC (`getTimezoneOffset() > 0`, i.e. the Americas, much of the Pacific, etc.).
- **Falsification attempted:**
  1. *Trace the alleged trigger through the current code* — traced `render()` → `_unlocal_date(new Date(this.model.value))` with `this.model.value` a UTC-midnight timestamp (established in §5.1.2) at head (`date_picker.ts:78-88`).
  2. *Check whether unchanged surrounding code prevents the failure* — no; `render()`, `connect_signals()`, `_on_select()` are unchanged and supply no guard distinguishing the two call sites.
  3. *Check callers/tests/types/CI* — the new `test_datepicker.py` (§5.4 below) never asserts on the *initial* displayed value's date text (only `test_basic` checks the *title label*, not the date), so it cannot have caught this; no CI evidence in the packet addresses it either (the one relevant human test, comment "this seems to be working great for me in PST" from `bryevdv`, §5.5, was run in a **negative**-offset zone but evidently wasn't checked against the exact initial date shown, or exercised only the click-a-date path).
  4. *Gate-2 introduced-here check, by its guarantee test:* base-branch guarantee at `git show ccb4bcb4c2b841d89b0e88303a97bf4604a5795f:bokehjs/src/lib/models/widgets/date_picker.ts:78-83` — `date.toISOString().substr(0,10)` with **no offset shift**, which correctly extracts the calendar day from a UTC-midnight input **regardless of browser timezone** (`toISOString()` is always UTC). Head code (`date_picker.ts:82-83`) inserts `date.setTime(date.getTime() - date.getTimezoneOffset()*60000)` before that same extraction, which — for `getTimezoneOffset() > 0` — subtracts real wall-clock hours from a UTC-midnight timestamp, pushing it into the *previous* UTC day before extraction. This is squarely "the change removed a guarantee unchanged code relied on": the guarantee that `_unlocal_date` is correct for a UTC-midnight input, which `render()`'s `defaultDate`/`minDate`/`maxDate` call sites still rely on, holds at the merge-base and does not hold at head, for timezones behind UTC.
  5. *Gate-6 intentional check* — nothing in the issue, PR body, or the two prior review threads (packet §6: only the `.idea/vcs.xml` file-removal thread, both empty-body review submissions, and eight non-review comments about CI flakes and adding tests) discusses negative-offset timezones or the initial-value display at all. `bryevdv`'s "working great for me in PST" (PST = UTC−8, a negative-offset zone) is the closest thing to a human check in that regime, but it addresses "working" as a general impression during ad hoc manual testing, not a specific check of the initial displayed value/min/max against the configured date — it does not "explicitly address" this candidate under the rubric's gate-6 standard, and the review record never discusses the initial-value path at all.
  6. *Verify citation scope* — the cited base-branch/head lines are the exact 6-line function; no wider rule citation needed.
  7. *Search review threads/CI for the same issue* — none found (packet §6 is the complete prior-review record; no other thread mentions this).
  8. *Confirm anchor* — `bokehjs/src/lib/models/widgets/date_picker.ts:82-83`, `RIGHT` side (added lines), valid minimal 2-line anchor.
  - **Direct execution (Node, offline, under the cell's execution allowance):** see §5.3. Reproduced the regression and the fix's correctness on both sides of the UTC boundary, using the actual head-branch function body verbatim and a UTC-midnight input timestamp matching the Python-side serialization traced in §5.1.2.
  - **Result:** candidate survives falsification. Priority **P1** (serious, broadly affecting — every negative-UTC-offset timezone; this is the identical *class* of bug the PR exists to fix, now on the opposite hemisphere), action **must-fix**, `blocking: true`, `kind: bug`.

**Other candidates raised and dropped** (full ledger with falsification reasons in §7):
- **D1** — missing test coverage for the negative-offset regression. Folded into C1's `Change`/evidence rather than published separately: it is not itself a proven defect (Changed-tests admits at most a `maintainability`/`consider` candidate for a test that "passes without exercising the behavior it claims," and none of the three new tests claims to exercise timezone-dependent initial-value display at all, so that specific bullet does not apply), and the rubric bars manufacturing an observation "merely to preserve a dropped candidate." Recorded as `observation (consequence absent)`.
- **D2** — `max_date=datetime.utcnow()` in the new tests as a non-deterministic/wall-clock-dependent test parameter. Traced to `bryevdv` (a maintainer) authoring this exact test content verbatim in the prior-review record (packet §6, non-review comment 7) and it being accepted as-is; not introduced by any ambiguity the author invented, and it does not by itself change any assertion's pass/fail boundary (`max_date` is never asserted against). Dropped: `no-consequence`, `pre-existing` review-record choice.
- **D3** — PR checklist's unchecked "tests added / passed" / "release document entry" boxes. Not ledger rows at all (rubric: no named checkable outcome; superseded by later commits; not a feature/API change). Dropped at the ledger-construction stage, not carried as falsified candidates.
- **D4** — accuracy of the updated code comment (lines 79–81) describing the fix's intent. Not raised as an independent candidate; the comment's claim ("agnostic to their local system's timezone") is the same claim C1 falsifies, so it is folded into C1 rather than double-counted.
- **D5** — `render()`'s picker-destroy-and-recreate-on-every-render pattern (lines 57-61) as a possible resource-lifecycle or duplicate-instance concern. Pre-existing at the merge-base, untouched by this diff (gate 2 fails: not introduced here, and the change does not materially worsen it). Dropped: `pre-existing`.
- **D6** — fixture hygiene on the new test file (unused fixtures / missing per-sibling convention). Batched search: `grep -l "bokeh_model_page\|bokeh_server_page" tests/integration/widgets/*.py` (repo-scoped to the sibling directory as the rubric specifies for this check, not repo-wide — this is the sibling-glob check, distinct from the whole-repo case-insensitive sweep the propagation-drift rule requires elsewhere) → 21 sibling files use the same fixtures; both fixtures the new file declares (`bokeh_model_page`, `bokeh_server_page`) are referenced in their test bodies (`page = ...(...)`, then `page.driver`/`page.results`/`page.has_no_console_errors()`). No unused fixture, no missing per-language/per-platform variant marker (not a table-style entry file). Dropped: `no-consequence`.

### 5.3 Direct execution — reproducing C1 (offline, node v24.19.0, under the cell's execution allowance)

Script `/tmp/qual137/work/l-bea6be14-seed1-att-13/unlocal_test.js` implements the **exact** merge-base (`unlocalOld`) and head (`unlocalNew`) bodies of `_unlocal_date` verbatim (copy-pasted from the file, not reconstructed from memory), and exercises both call paths:
- **Path A** ("initial value"): `new Date(Date.UTC(2019, 8, 20, 0, 0, 0))` — a UTC-midnight timestamp, matching §5.1.2's traced Python-side serialization of `value=datetime(2019, 9, 20)` (or `min_date`/`max_date`).
- **Path B** ("round trip after selection"): `new Date(2019, 8, 20).toDateString()` (Pikaday's click handler constructs a **local**-midnight `Date`; `_on_select` — unchanged code, `date_picker.ts:90-97` — stores `date.toDateString()` as the new `model.value`; `render()` re-invokes `_unlocal_date(new Date(this.model.value))` on that string), matching the exact mechanism the issue describes.

Command and full output:
```
$ TZ=Europe/Paris node unlocal_test.js       # UTC+2 (summer) — the reported-bug regime
getTimezoneOffset (minutes) = -120
Path A (initial value) OLD -> Fri Sep 20 2019
Path A (initial value) NEW -> Fri Sep 20 2019
Path B (redisplay after select) OLD -> Thu Sep 19 2019      # <- reproduces issue #9129
Path B (redisplay after select) NEW -> Fri Sep 20 2019      # <- fixed correctly

$ TZ=America/New_York node unlocal_test.js   # UTC-4 (summer, EDT)
getTimezoneOffset (minutes) = 240
Path A (initial value) OLD -> Fri Sep 20 2019
Path A (initial value) NEW -> Thu Sep 19 2019                # <- NEW regression: wrong by one day
Path B (redisplay after select) OLD -> Fri Sep 20 2019
Path B (redisplay after select) NEW -> Fri Sep 20 2019

$ TZ=UTC node unlocal_test.js
getTimezoneOffset (minutes) = 0
Path A: OLD/NEW both Fri Sep 20 2019; Path B: OLD/NEW both Fri Sep 20 2019   (offset zero, no divergence either way)

$ TZ=Pacific/Auckland node unlocal_test.js   # UTC+12/+13
getTimezoneOffset (minutes) = -720
Path A (initial value) OLD -> Fri Sep 20 2019
Path A (initial value) NEW -> Fri Sep 20 2019
Path B (redisplay after select) OLD -> Thu Sep 19 2019
Path B (redisplay after select) NEW -> Fri Sep 20 2019

$ TZ=Pacific/Honolulu node unlocal_test.js   # UTC-10, no DST
getTimezoneOffset (minutes) = 600
Path A (initial value) OLD -> Fri Sep 20 2019
Path A (initial value) NEW -> Thu Sep 19 2019                 # <- NEW regression again
Path B (redisplay after select) OLD -> Fri Sep 20 2019
Path B (redisplay after select) NEW -> Fri Sep 20 2019
```
Each command completed in well under one second; exit status 0 in every case. This is a deterministic pure-function repro of the actual head-branch code, not a simulation of unrelated logic, and it directly demonstrates: (a) the fix genuinely repairs the reported issue for positive-offset zones (Paris, Auckland) on Path B; (b) the fix introduces the mirror-image defect for negative-offset zones (New York, Honolulu) on Path A, which Path A never had before; (c) zero-offset and positive-offset Path A are unaffected either way.

### 5.4 Changed tests (rubric's Changed tests section)

`tests/integration/widgets/test_datepicker.py` is a wholly new file (no pre-existing version to diff against), so every one of its three test functions is "added" and gets the full inspection:

- **`test_basic`** — setup: constructs a `DatePicker` with `title='Select date'`; call: `bokeh_model_page(dp)`; assertion: `el.text == "Select date"` on `.foo label`, plus `page.has_no_console_errors()`. Observes only the title label, not any date; not suspicious, not related to C1; execution unavailable (Selenium/browser not available per run conditions §8.2 of the packet — "The project's own build and its Selenium integration suite are NOT available (no browser, no npm install, no network)"). Traced by inspection only: assertions are non-trivial (checks live DOM text) and do not depend on timezone.
- **`test_js_on_change_executes`** — setup/call: opens the picker (`el.click()` on `.foo input`), clicks `button[data-pika-day="16"]`; assertions: `results['value'] == 'Mon Sep 16 2019'` (JS-side `CustomJS` recorder) and `.bk-input`'s `value` attribute equals the same string. Traced: Sep 16, 2019 is in fact a Monday (verified by calendar arithmetic: Sep 1, 2019 was a Sunday, +15 days = Sunday + 2 weeks + 1 day = Monday). This test exercises exactly **Path B** (selection round-trip), which §5.3 shows the fix repairs correctly in *every* tested timezone including negative-offset ones — so this test's assertions hold regardless of C1, and it would not catch C1 even if it were run under `TZ=America/New_York`, because the picker would still show September (only the pre-selected `defaultDate` day-of-month is off by one, not the month), so clicking `data-pika-day="16"` still selects the 16th correctly. Not suspicious for C1; execution unavailable (Selenium), traced by semantics instead.
- **`test_server_on_change_round_trip`** — setup: a `bokeh_server_page` with a `DatePicker` and an `on_change` callback storing `(old, new)` into a `ColumnDataSource`; call: click a date, then trigger a `CustomAction` to record `source.data`; assertions: `d0.timetuple()[:3] == (2019, 9, 20)` (the pre-existing `value`, i.e. **Path A** in a round trip through the server) and `d1.timetuple()[:3] == (2019, 9, 16)` (the newly selected value, i.e. Path B). This is the one test whose first assertion (`d0`) does touch Path A — but it asserts on the *value the callback receives*, which is `old = date.toDateString()` from the **previous** `_on_select` call, i.e. it is exercising the round-trip mechanism (Path B semantics) for the *old* value too, not the picker's true initial `defaultDate` render before any interaction; the very first time the callback fires is on the *first* click, and `old` is populated from Bokeh's property-change machinery reading back `this.model.value` as already set at construction — this still resolves through `new Date(this.model.value)`/`toDateString()` without ever going through `_unlocal_date` again for the "old" value (only `render()`'s three call sites route through `_unlocal_date`; the on-change callback payload is the raw property value, not a re-rendered display value). I traced this and confirm it is **not** a Path-A check of the *displayed* defaultDate text, so it does not exercise C1 either. Execution unavailable (Selenium + running Bokeh server); traced by inspection of `_on_select`/`on_change`/property-transport semantics instead of run.

**No usable local command or environment exists to execute any of these three tests** (they require a real browser via Selenium and, for the third, a running Bokeh server; the packet's run conditions explicitly withhold both, and no exact-head CI log for this specific PR is present in the sandbox to reuse). This is recorded as **execution unavailable**, not a pass, per the rubric ("Unavailable execution is stated as unavailable: it never becomes a pass"). The trace above settles all three cases (none is suspicious, none decides C1), so per the rubric this does **not** by itself make coverage incomplete.

### 5.5 Prior-review record cross-check (packet §6)

Reviewed fully (it is small): two empty-body review submissions (`bryevdv`, `madkopp`, both on the now-irrelevant, already-removed `.idea/vcs.xml` file — that thread is resolved and the file is not part of the final diff, confirmed by the manifest showing only 2 changed files); eight non-review comments, the relevant ones being: `bryevdv` "OK this seems to be working great for me in PST" (2019-09-26, this is the negative-offset regime C1 concerns, but is a general "working great" remark, not a specific check of the initial displayed value — does not settle gate 6 against C1, per §5.2 step 5); `bryevdv` supplying the exact test-file content later published verbatim in the diff (2019-09-29) — confirmed by direct diff (`diff <(cat test_radio_button_group.py) <(cat test_datepicker.py)`, §5.4 note) that the merged file matches `bryevdv`'s suggestion essentially line-for-line, restructured to the `DatePicker` API. No explicit deferral of any design/naming/API-shape decision appears anywhere in this record (the rubric's Uncertainty-routing "explicit deferral" rule — nothing to carry forward as an open question on that basis).

### 5.6 Own token usage

The harness does not surface a running token-usage figure to me during this session (no tool in my toolset reports it, and none appeared in any tool result). I can only report the one number the harness *did* surface: the verifier sub-agent's own self-reported usage, `subagent_tokens: 40496`, `tool_uses: 16`, `duration_ms: 162493` (§7.1/§7.2). My own (primary) token usage for this entire run is therefore stated as: **not available to me / not reported by the harness.**

## 6. Complete candidate ledger (persisted before verifier dispatch, per rule 6)

### 6.1 Survivor — full private record

```yaml
id: bokehjs/date-picker-unlocal-date-negative-offset-regression
anchor:
  type: line
  path: bokehjs/src/lib/models/widgets/date_picker.ts
  start_line: 82
  end_line: 83
  side: RIGHT
fix: bokehjs/src/lib/models/widgets/date_picker.ts:82-83   # same as anchor; omitted in rendering
priority: P1
action: must-fix
blocking: true
kind: bug
title: Unconditional offset shift breaks initial date for negative-UTC-offset users
claim: "_unlocal_date unconditionally shifts `date` by `date.getTimezoneOffset()*60000` before
  reading its UTC calendar day, so for a browser timezone behind UTC
  (`getTimezoneOffset() > 0`) any UTC-midnight input (the widget's initial `value`,
  `min_date`, or `max_date`, as Bokeh's Python-side `Date` property always
  serializes them) is read back one calendar day earlier than intended."
trigger: A DatePicker with an explicit value, min_date, or max_date, rendered in a
  browser whose local timezone is behind UTC (e.g. any US/Canada/South America zone,
  Pacific/Honolulu, etc.)
impact: The widget's initial displayed value and its effective selectable date range
  (min/max) are silently one calendar day earlier than configured, reintroducing for
  negative-offset users the same class of off-by-one bug issue #9129 reports for
  positive-offset users.
evidence:
  - bokehjs/src/lib/models/widgets/date_picker.ts:82-83 (unconditional offset shift, head)
  - bokehjs/src/lib/models/widgets/date_picker.ts:78-83 at merge-base (git show
    ccb4bcb4c2b841d89b0e88303a97bf4604a5795f) — no offset shift, correct for any
    UTC-midnight input regardless of timezone
support:
  inspected:
    - full file (129 lines) + Python-side Date.transform/convert_datetime_type
  checks:
    - node repro of unlocalOld/unlocalNew across TZ=Europe/Paris, America/New_York,
      UTC, Pacific/Auckland, Pacific/Honolulu for both call paths (see run report §5.3)
  uncertainty: Pikaday's own use of minDate/maxDate for calendar boundary enforcement
    is not independently vendored/re-verified in this sandbox; the initial-value
    display consequence itself is verified directly.
requirement_source: none (Code candidate, not a requirement gap)
change: Only derive the calendar day via the timezone-offset shift for a Date that
  represents local midnight (the value produced by Pikaday's onSelect callback);
  leave the UTC-midnight-safe `toISOString().substr(0,10)` extraction (the
  merge-base behavior) for `defaultDate`/`minDate`/`maxDate`, or equivalently
  branch on whether the input's local time-of-day is already midnight before
  applying the shift.
verification: independent-confirmed   # pending: candidate batch dispatched below
disposition: survivor
falsification: No unchanged guard in render() or in the Python-side property
  transform prevents a negative-offset browser from receiving a UTC-midnight
  value/min_date/max_date; the base-branch guarantee that _unlocal_date is
  correct for any UTC-midnight input (git show <merge-base>:...:78-83) is
  removed at head for such timezones (git show <head>:...:82-83).
```

### 6.2 Complete compact ledger (all raised candidates, survivors and dropped)

| id | kind | disposition | decisive evidence | falsification / drop reason | Verifier ruling required? |
|---|---|---|---|---|---|
| `bokehjs/date-picker-unlocal-date-negative-offset-regression` (C1) | bug | **survivor** (must-fix) | `date_picker.ts:82-83` (head) vs `:78-83` (merge-base); node repro §5.3 | passed all 8 falsification steps; direct execution confirms trigger+impact | **Yes** — mandatory: SKILL.md step 3, "Independently verify every surviving candidate proposed as `must-fix`." |
| D1 missing negative-offset regression-test coverage | maintainability | dropped → `observation (consequence absent)` | none of the 3 new tests asserts on initial displayed value (§5.4) | rubric bars an observation "merely to preserve a dropped candidate"; the underlying fact (missing coverage) is folded into C1's `change`, not independently published; it also does not clear the Changed-tests bullet ("test passes without exercising the behavior it claims") since none of the tests claims to exercise this | No — not a survivor, not `kind` bug/concurrency/invariant/security, and shares no anchor/claim with C1 beyond the same file's general subject, so the related-acquittal rule's file/claim test is not met (different lines, different named function-level claim: "coverage is missing" vs. "the shift is wrong"); not sent to verifier. |
| D2 `max_date=datetime.utcnow()` non-determinism in tests | maintainability | dropped: `pre-existing`/`no-consequence` | packet §6 non-review comment 7 (`bryevdv`'s verbatim suggested test, 2019-09-29) matches merged file (diff check, §5.4) | authored and accepted by a maintainer verbatim; never asserted against; no consequence | No — not `bug`/`concurrency`/`invariant`/`security` kind, not a survivor. |
| D3 PR checklist boxes (`tests added/passed`, `release doc`) | requirement (candidate, not admitted to ledger) | dropped at ledger-construction (no row) | packet §3 | no named checkable outcome (rubric: generic template checkbox, no named referent); R4 disposed `met` (non-goal correctly inapplicable) | No — never became a candidate. |
| D4 accuracy of updated code comment (lines 79-81) | (subsumed) | dropped: folded into C1 | same lines as C1 | same underlying claim as C1; not double-counted | No — folded, not separately ruled. |
| D5 `render()` destroy/recreate pattern (lines 57-61) | maintainability | dropped: `pre-existing` | `git show <merge-base>:...:57-61` identical to head | unchanged by this diff; gate 2 fails (not introduced here, not materially worsened) | No — `pre-existing`, not `bug` kind admitted as survivor, gate-2 fails outright. |
| D6 test fixture hygiene (`bokeh_model_page`/`bokeh_server_page` usage/convention) | maintainability | dropped: `no-consequence` | `grep -l "bokeh_model_page\|bokeh_server_page" tests/integration/widgets/*.py` → 21 sibling files; both declared fixtures referenced in bodies | matches sibling convention; no unused fixture | No. |

**Zero-survivor clean-verdict mode does not apply** (C1 survives as a finding). **Related-acquittal mode**: none of D1–D6 is `kind ∈ {bug, concurrency, invariant, security}` **and** shares C1's anchor file/line or names the same function/branch/state field/lock as C1's claim (D4 is the closest — same lines — but it was folded into C1 rather than kept as a separate ledger row, per the rubric's Observations rule against manufacturing near-duplicate rows; there is therefore no second row at C1's anchor for the verifier to rule on). So the verifier batch below carries **C1 only**, no related-acquittal rows.

## 7. Independent verification (mandatory — C1 is `must-fix`)

Trigger sentence quoted from `SKILL.md` step 3: *"Independently verify every surviving candidate proposed as `must-fix`, plus every candidate involving security or authorization, data loss or corruption, destructive migration, or an externally observable compatibility break."* C1 is proposed `must-fix`, so verification is mandatory. `kind: bug` (not `concurrency`/`invariant`), so `references/verifier-concurrency.md` is **not** included in the brief. No `artifact-` coordinate is cited, so `references/conformance.md`'s verifier addendum does not apply either.

**Early-dispatch analysis (SKILL.md step 3):** the diff does *not* touch "a concurrency or failover path, a data-integrity surface, or a security or authorization boundary" (it is a pure client-side date-formatting helper plus a new offline test file), so the rule barring early dispatch on those surfaces does not apply. However, early dispatch requires (a) the complete diff inspected and manifest finished — true, both files are `reviewed` (§4.2, §5) — and (b) every mandatory-verification candidate has completed primary falsification, together with every related-acquittal row — true (C1 falsified in §5.2, no related rows exist per §6.2). There are no further `consider` candidates left outstanding after C1 that would run "while the batch runs" (D1–D6 were already falsified/dropped before this point, in §5.2/§6.2), so there is no separate parallel work to interleave with the dispatch; I dispatch the one candidate batch now, immediately following the complete falsification pass, which satisfies the "as soon as" trigger without leaving any pending falsification behind it.

### 7.1 Verifier dispatch

Sub-agent: 1 dispatched, role = independent candidate-mode verifier, `subagent_type: "general-purpose"`, `model: "sonnet"`, `run_in_background: false`. Isolation: a fresh `Agent` call carries no prior conversation context (this satisfies `references/verifier.md`'s Isolation section — "Do not inherit the primary review conversation, its chain of reasoning, or prior finder output").

**Exact prompt given** (verbatim, matching `verifier.md`'s candidate-mode input list: repo + pinned SHAs; linked issue coordinates since C1 cites none of `pr-title`/`pr-body`/`artifact-`; the `ranges` line for the candidate's anchor; the candidate record with `id/kind/priority/action/anchor/fix/title/claim/trigger/impact/change` and raw code citations; **no** `support`/confidence/argument; permission to inspect cited code and narrow callers/tests/config/history/issue text; rules 1–7 and rule 9 restated per the cell's dispatch instructions):

```
You are an independent verifier for one code-review candidate. This is a controlled,
offline research evaluation — no network access, no repository mutation, no publication.

RULES BINDING ON YOU (verbatim from the parent's dispatch — follow all of them):
1. Do not borrow behavior from any other review skill; you are performing exactly the
   verification task in references/verifier.md (reproduced below), nothing else.
2. Do not run `git checkout`, `git switch`, `git reset`, `git stash`, or any command that
   mutates the tree in /tmp/qual137/runs/l-bea6be14-seed1-att-13. Read-only git commands only
   (git show, git log, git diff, git blame, grep, cat).
3. Focused execution IS permitted, offline, outside the clone: you may write and run scratch
   Node.js (v24.19.0) under /tmp/qual137/work/l-bea6be14-seed1-att-13/ (create a subdirectory
   for your own scratch files if useful), including with a TZ environment variable set, to
   check the behavior of code you read. Five minutes per command. Do NOT attempt the project's
   own build or its Selenium integration suite (unavailable: no browser, no npm install, no
   network). Nothing may be added to or changed in the clone.
4. Do not read any git history beyond the pinned head 36549bca3a63d581f7b68d08054a7813c1e6a499
   in /tmp/qual137/runs/l-bea6be14-seed1-att-13 (it is truncated there on purpose; nothing newer
   exists locally). You may freely read merge-base and head content and ancestor history.
5. Stay inside: the clone at /tmp/qual137/runs/l-bea6be14-seed1-att-13, this prompt's content,
   and scratch files you create under /tmp/qual137/work/l-bea6be14-seed1-att-13/. Do not read
   any other path (no other run's clone, report, or payload). If you do read anything outside
   these, say so explicitly in your report so it can be disclosed.
6. This is a one-shot dispatch: finish and return your verdict in this same turn. Do not ask
   anyone anything or wait for a reply.
7. You are verifying ONE candidate only. Do not search the rest of the pull request for new
   findings. Do not render publication prose, trailers, or comment shapes — return only the
   structured verdict fields below.

REPOSITORY AND PINNED COORDINATES:
- Clone: /tmp/qual137/runs/l-bea6be14-seed1-att-13 (offline; local branch `master` = merge-base,
  local branch `review-head` = head, checked out).
- merge-base = ccb4bcb4c2b841d89b0e88303a97bf4604a5795f ; head = 36549bca3a63d581f7b68d08054a7813c1e6a499
- Originating issue: bokeh/bokeh#9129 ("[BUG]Datepicker displayed value is not updating
  correctly") — the reported symptom: for users in positive-UTC-offset timezones (e.g. France
  UTC+2, UK BST), after selecting a date in the DatePicker widget, the displayed value showed
  the selected day minus one day; selecting the same day a second time displayed it correctly.
  No repository rule coordinate applies (no AGENTS.md/CLAUDE.md/CONTEXT.md exists for this path
  at the merge-base).

RANGES (from scripts/review_context.py) for the candidate's anchor:
  bokehjs/src/lib/models/widgets/date_picker.ts:45-98 @head
  bokehjs/src/lib/models/widgets/date_picker.ts:45-94 @merge-base

CANDIDATE TO VERIFY:
id: bokehjs/date-picker-unlocal-date-negative-offset-regression
kind: bug
priority: P1
action: must-fix
anchor: {type: line, path: bokehjs/src/lib/models/widgets/date_picker.ts, start_line: 82, end_line: 83, side: RIGHT}
fix: bokehjs/src/lib/models/widgets/date_picker.ts:82-83 (same as anchor)
title: Unconditional offset shift breaks initial date for negative-UTC-offset users
claim: "_unlocal_date unconditionally shifts `date` by `date.getTimezoneOffset()*60000` before
  reading its UTC calendar day, so for a browser timezone behind UTC
  (`getTimezoneOffset() > 0`) any UTC-midnight input (the widget's initial `value`, `min_date`,
  or `max_date`, as Bokeh's Python-side `Date` property always serializes them) is read back
  one calendar day earlier than intended."
trigger: A DatePicker with an explicit value, min_date, or max_date, rendered in a browser
  whose local timezone is behind UTC (e.g. any US/Canada/South America zone, Pacific/Honolulu).
impact: The widget's initial displayed value and its effective selectable date range (min/max)
  are silently one calendar day earlier than configured.
change: Only derive the calendar day via the timezone-offset shift for a Date that represents
  local midnight (the value produced by Pikaday's onSelect callback); leave the UTC-midnight-safe
  `toISOString().substr(0,10)` extraction (the merge-base behavior) for
  `defaultDate`/`minDate`/`maxDate`, or equivalently branch on whether the input's local
  time-of-day is already midnight before applying the shift.
raw code citations offered (verify independently, do not trust):
  - bokehjs/src/lib/models/widgets/date_picker.ts:78-88 (head, whole _unlocal_date method)
  - bokehjs/src/lib/models/widgets/date_picker.ts:57-76 (head, render(), the three call sites
    of _unlocal_date: defaultDate, minDate, maxDate)
  - bokehjs/src/lib/models/widgets/date_picker.ts:78-83 at merge-base (same method before this PR)
  - bokeh/core/property/datetime.py:51-76 (Python Date property transform/validate)
  - bokeh/util/serialization.py:152-184 (convert_datetime_type — how a datetime.date/datetime
    becomes the numeric value sent to the browser)
No `support`, confidence, or argument is supplied — form your own independent judgment.

VERIFICATION TASK (from references/verifier.md — perform all of it):
1. Read the cited anchor and actual fix site as bounded ranges at head and at the merge-base
   (`git show <merge-base>:<path>` with a line range), then only enough surrounding context to
   decide the claim. Read a whole file only when a conditional the claim depends on cannot be
   located otherwise; say so.
2. Reproduce or trace the stated trigger through the current code.
3. Establish the observable impact and whether unchanged code prevents it.
4. For this Code candidate, confirm that the change introduced the behavior, or that it removed
   the guarantee an unchanged path relied on; state which of the two applies and cite the
   base-branch guarantee (`git show <merge-base>:<path>`) and the head-branch code that no
   longer provides it.
5. Confirm that the issue, pull-request description, rules, history, or review record do not
   make it intentional. A maintainer's approval/LGTM/merge establishes intent only for what the
   review record explicitly addresses.
6. Check whether another candidate requests the same underlying change (none is supplied here,
   so this is trivially satisfied).
7. Any assertion you make that a path is safe/unreachable/handled/correct is a "scoped safety
   ruling": state the path, state/ordering conditions, and exact premise, and trace the opposite
   branch of every conditional that premise depends on before asserting it (per
   references/verifier.md's Scoped safety rulings section). Do not assert safety on the strength
   of one working trace alone.
8. Return exactly one verdict: `confirmed` (decisive evidence establishes the trigger,
   qualifying impact, requested outcome, and the Code introduced-here condition) or `refuted`
   (with exactly one basis: contradicted / prevented / intentional / pre-existing / no-consequence
   / unresolved — and for `unresolved`, name the single settling fact and who/what could supply it).
   Also return any correction to trigger/impact/priority/action/anchor/fix/change, and any single
   non-actionable `observation` aside if an accurate sub-threshold fact surfaces incidentally
   (no `should`/`must` language). Do not return publication-ready prose — structured fields only.

You are encouraged to write and run a small Node.js script under
/tmp/qual137/work/l-bea6be14-seed1-att-13/ (your own subdirectory) to empirically check the
claimed behavior of `_unlocal_date` at head and at merge-base under different TZ values, using
the exact function bodies you read from the repository (do not take my word for their content —
read them yourself with `git show`).

Report back: your verdict, basis, decisive citations (path:line at head and at merge-base, plus
any command you ran with its output), any corrections, and any observation aside. Also report:
every file/path you read, every command you ran (with exit status), and explicitly confirm
whether you stayed within the sandbox in rule 5 or read anything outside it.
```

### 7.2 Verifier's verbatim report

*(recorded immediately below as returned, before any further primary-side action)*

Sub-agent handle: `ad2abe740225b2775`. Reported token usage: `subagent_tokens: 40496`, `tool_uses: 16`, `duration_ms: 162493`.

```
## Verdict: CONFIRMED

## Basis
Decisive evidence establishes trigger, impact, and that this specific diff hunk introduced the regression (not a pre-existing condition, not intentional, not prevented by other code).

## Decisive citations

**Head** — `bokehjs/src/lib/models/widgets/date_picker.ts:78-89` (`git show 36549bca3a63d581f7b68d08054a7813c1e6a499:bokehjs/src/lib/models/widgets/date_picker.ts`):
```
82    const timeOffsetInMS = date.getTimezoneOffset() * 60000
83    date.setTime(date.getTime() - timeOffsetInMS)
```
applied unconditionally inside `_unlocal_date`, which is called at lines 57-70 for `defaultDate: this._unlocal_date(new Date(this.model.value))`, `minDate`, and `maxDate` — all three fed a UTC-midnight `Date` derived from the server-serialized value.

**Merge-base** — `git show ccb4bcb4c2b841d89b0e88303a97bf4604a5795f:bokehjs/src/lib/models/widgets/date_picker.ts:78-83`: no offset shift, just `date.toISOString().substr(0,10)`, correctly UTC-midnight-safe.

**Diff** — `git diff ccb4bcb4c2b841d89b0e88303a97bf4604a5795f 36549bca3a63d581f7b68d08054a7813c1e6a499 -- bokehjs/src/lib/models/widgets/date_picker.ts` shows the two lines added by commit `472e4770d` ("Fixed issue of Datepicker displaying the wrong date for users in UTC+ timezones"), confirming the fix was scoped only to ahead-of-UTC ("UTC+") timezones and never addressed behind-UTC ones.

**Python serialization confirms UTC-midnight semantics of initial value/min/max**: `bokeh/util/serialization.py` `convert_datetime_type` for `dt.date`: `(dt.datetime(*obj.timetuple()[:6]) - DT_EPOCH).total_seconds() * 1000` — treats the date's Y/M/D as a naive UTC timestamp, i.e. UTC midnight.

**Empirical reproduction** (Node v24.19.0, script at `/tmp/qual137/work/l-bea6be14-seed1-att-13/verify/test.js`, using the exact head and merge-base function bodies read above, target date June 5 2019 UTC-midnight):

```
=== America/New_York (behind UTC, offset=240) ===
HEAD defaultDate result: Tue Jun 04 2019   <- WRONG, one day early
BASE defaultDate result: Wed Jun 05 2019   <- correct

=== Pacific/Honolulu (behind UTC, offset=600) ===
HEAD defaultDate result: Tue Jun 04 2019   <- WRONG
BASE defaultDate result: Wed Jun 05 2019   <- correct

=== Europe/Paris (ahead of UTC, offset=-120) ===
HEAD defaultDate result: Wed Jun 05 2019   <- correct (unaffected)
BASE defaultDate result: Wed Jun 05 2019   <- also correct at base

HEAD onSelect-reread result: Wed Jun 05 2019  <- fixed by this PR (the original issue #9129 symptom)
BASE onSelect-reread result: Tue Jun 04 2019  <- reproduces original bug at base
```
(all runs exit 0)

This cleanly separates the two effects: the PR's shift correctly fixes the `onSelect`-then-reread path for ahead-of-UTC users (the originally reported issue), but that same unconditional shift corrupts the `defaultDate`/`minDate`/`maxDate` paths for behind-UTC users, which were correct at merge-base. Since `_unlocal_date` is one function serving both call sites, the fix cannot distinguish "local-midnight Date from Pikaday's `onSelect`" from "UTC-midnight Date from the server-serialized initial value/min/max" — exactly the mechanism the candidate describes.

## Criterion checks
- **Introduced-here vs. removed guarantee**: introduced-here. Merge-base's `_unlocal_date` correctly read UTC-midnight `Date` objects (guarantee: `toISOString().substr(0,10)` on a UTC-midnight Date always returns the correct calendar day, timezone-independent). Head's added lines 82-83 destroy that guarantee for any browser with `getTimezoneOffset() > 0`.
- **Intentional?** No. The introducing commit's own message ("Fixed issue of Datepicker displaying the wrong date for users in UTC+ timezones") scopes the fix to ahead-of-UTC only; nothing in the subsequent "Made a shell for the integration test…" or "update tests" commits exercises or acknowledges behind-UTC timezones — the added Selenium tests (`tests/integration/widgets/test_datepicker.py`) run under the CI machine's ambient (presumably UTC) timezone with no TZ variation, so they would not have caught this and give no evidence of deliberate acceptance.
- **Pre-existing?** No — merge-base was correct for this exact path/timezone combination (shown above).
- **No-consequence?** No — `_unlocal_date`'s entire purpose (per both versions' own comments) is to hand Pikaday a `Date` whose local Y/M/D fields equal the intended calendar day, because Pikaday reads local getters; producing a `Date` one day off, three call sites deep (`defaultDate`, `minDate`, `maxDate`), directly changes what is initially displayed/selectable, with no other transform in this file undoing it before it reaches Pikaday.
- **Duplicate candidate**: none supplied — trivially satisfied.

## Scoped safety ruling made
None asserted beyond what's empirically shown; I did not assert Pikaday's internal handling is safe from vendored source (not present in the clone, no `node_modules`/npm install per the constraints) — instead I relied on the file's own comments plus the direct, verified fact that `_unlocal_date`'s return value itself is the wrong calendar day, which is the decisive fact regardless of Pikaday's further handling.

## Corrections
None. Trigger, impact, anchor (82-83), fix location, and priority/action (P1/must-fix) all check out against the read code and the empirical trace.

## Observation (non-actionable aside)
The merge-base already had the *opposite*-direction bug (ahead-of-UTC `onSelect`-reread showing the previous day, reproduced above as `BASE onSelect-reread: Tue Jun 04 2019`), which is the exact symptom in bokeh/bokeh#9129; this PR's real defect is scoping the correction to the wrong input shape (any `Date`) instead of the specific one that needed it (a local-midnight `Date` from Pikaday's `onSelect`).

## Full audit trail
**Files/paths read** (all inside the authorized clone or my own scratch dir):
- `/tmp/qual137/runs/l-bea6be14-seed1-att-13` — `git log --oneline -1`, `git branch -a`
- `bokehjs/src/lib/models/widgets/date_picker.ts` at head (`36549bca3`) and merge-base (`ccb4bcb4c`), via `git show <rev>:<path>`
- `git diff ccb4bcb4c2b841d89b0e88303a97bf4604a5795f 36549bca3a63d581f7b68d08054a7813c1e6a499 -- bokehjs/src/lib/models/widgets/date_picker.ts`
- `bokeh/core/property/datetime.py` at head via `git show`
- `bokeh/util/serialization.py` (lines 140-200) at head via `git show`
- `git log --oneline ccb4bcb4c..36549bca3` (whole repo, and scoped to the date_picker.ts path) — both within the merge-base..head range, not beyond head, so within rule 4
- `git show 472e4770d --stat`, `git show 472e4770d -s --format=fuller`, `git show 4215c2d0b --stat`, `git show 36549bca3 --stat` — all commits within the merge-base..head ancestor range
- `tests/integration/widgets/test_datepicker.py` at head via `git show`
- `find . -iname "pikaday*"` in the clone (confirmed no vendored pikaday source present, no node_modules)
- My own scratch file `/tmp/qual137/work/l-bea6be14-seed1-att-13/verify/test.js`, executed with `node` under four `TZ` values.

**Commands run**: all listed above via Bash; all exited 0 with no errors. No `git checkout`/`switch`/`reset`/`stash` or any tree-mutating command was run. No build or Selenium suite was attempted.

**Sandbox confirmation**: I stayed entirely within the authorized clone at `/tmp/qual137/runs/l-bea6be14-seed1-att-13`, this prompt's content, and my own scratch directory under `/tmp/qual137/work/l-bea6be14-seed1-att-13/`. I did not read any other run's clone, report, or payload, and read no path outside the stated boundaries.
```

### 7.3 Primary reconciliation of the verifier's return

Validated against the diff: the verifier's citations (`date_picker.ts:78-89` head, `:78-83` merge-base, `bokeh/util/serialization.py` `convert_datetime_type`) match exactly what I read in §5.1–5.3; its independent Node repro (using June 5 2019 rather than my September 20 2019, and adding `America/New_York`/`Pacific/Honolulu`/`Europe/Paris`) reaches the identical qualitative conclusion via an independently-chosen example date and independently-written script. No duplicate candidate exists to merge. No correction was returned to `trigger`/`impact`/`priority`/`action`/`anchor`/`fix`/`change`, so the candidate's fields stand as drafted in §6.1. The verifier's one `observation` aside ("the PR's real defect is scoping the correction to the wrong input shape...") restates the same mechanism as the confirmed finding rather than surfacing an unrelated sub-threshold fact; per the rubric's Observations section ("A fact belongs to exactly one channel") I fold it into the finding's own `Change` text rather than publishing it a second time as a body-level Observation.

**Disposition updated:** `bokehjs/date-picker-unlocal-date-negative-offset-regression` → **`independent-confirmed`**, `verification: independent-confirmed`. This is the only candidate requiring mandatory verification (§6.2); no related-acquittal rows existed to co-verify; zero-survivor clean-verdict mode never applied (C1 survived from the start). No re-opened rows, no follow-up batch needed — **one initial batch, zero follow-up batches**, within the "one initial plus one follow-up" cap.

## 8. Step 4 — Re-review

Skipped. First review (§1, §3): the posting identity `kamui` has no prior review, reply, or trailer-bearing comment in the packet, so `SKILL.md` step 1's re-review trigger is not met.

## 9. Step 5 — Validate before writing

Manual pre-checks before running the script: the cited evidence locations (`date_picker.ts:82-83` head, `:78-83` merge-base) and the fix location (same lines, so `fix` is omitted from the trailer per the output contract's "Omit `fix` when it is the anchor") were both re-confirmed real by direct `git show`/`cat -n` reads in §5 and by the verifier's independent reads in §7.2. `Source` was **deliberately omitted**: the finding is a Code regression the change itself introduces, not a gap against an explicit requirement — citing issue #9129 as `Source` would misleadingly suggest the issue demands this fix, when the issue is in fact what R1 already shows **met**; the regression is unrelated to what the issue asked for. Question/observation eligibility: no question was raised (no static-unresolvability gap survived falsification — the June-5/September-20 empirical reproductions in §5.3 and §7.2 settle the fact deterministically); no observation was published (the verifier's own aside restates the confirmed finding's mechanism rather than an unrelated sub-threshold fact, so per the rubric's one-fact-one-channel rule it was folded into the finding rather than duplicated in a body-level `Observations` section, per §7.3). Deduplication: only one survivor exists; no merge needed. Coverage entry and summary status computed in §10 below.

Ran, in order:
```
$ python3 scripts/validate_review.py --render /tmp/qual137/work/l-bea6be14-seed1-att-13/payload.json
anchor [`bokehjs/src/lib/models/widgets/date_picker.ts:82-83`](https://github.com/bokeh/bokeh/blob/36549bca3a63d581f7b68d08054a7813c1e6a499/bokehjs/src/lib/models/widgets/date_picker.ts?plain=1#L82-L83)
```
— pasted verbatim into the summary's `## Findings` line (exact string equality, not hand-composed).
```
$ python3 scripts/validate_review.py /tmp/qual137/work/l-bea6be14-seed1-att-13/payload.json
(no output)
EXIT=0
```
Zero violations on the first full validation pass (one earlier attempt failed only because `--render` needs the run trailer's `head` present before the fragment can be generated — a bootstrapping order issue, not a content violation; resolved by drafting the trailer first, rendering, then splicing the fragment in). Immediately after this exit-0 validation, ran, per the cell's instructions:
```
$ python3 /tmp/qual137/mark_event.py /tmp/qual137/reports/l/l-bea6be14-seed1-att-13-timing.json payload_validated_at
payload_validated_at 2026-09-07T08:07:04.559689+00:00
```
No further payload edits were made after this point, so no re-validation or second `mark_event.py` call was needed.

## 10. Step 6 — Publish (retrospective: render and stop)

Per the packet's binding run condition 4 and `SKILL.md`'s Boundaries section ("retrospective review of a merged pull request is non-publishing by default") and the packet's explicit statement (`kamui` did not author the PR, has no prior activity, target is `MERGED` → retrospective review, publication disabled): **no write was attempted.** No head re-fetch was performed (there is nothing to re-fetch offline, and no write follows it). The batch was rendered exactly as `--emit-batch` would produce it for publication, and is reported below in place of a review URL, per the cell's instruction to "render the review exactly as it would be posted... and stop":
```
$ python3 scripts/validate_review.py --emit-batch /tmp/qual137/work/l-bea6be14-seed1-att-13/payload.json > batch.json
EXIT=0
```
`batch.json`'s `commit_id` = `36549bca3a63d581f7b68d08054a7813c1e6a499` (the reviewed head), `event` = `COMMENT` (no gating authorization exists or is claimed), `body` = the summary above, `comments` = one entry at `bokehjs/src/lib/models/widgets/date_picker.ts:82-83` (`side: RIGHT`, `start_line: 82`, `start_side: RIGHT`, `line: 83`) carrying the finding's full markdown plus its trailer. The complete rendered review (summary + the one finding, in the exact prose that would post) is at [`l-bea6be14-seed1-att-13-payload.md`](l-bea6be14-seed1-att-13-payload.md).

**Would-be review report** (in place of the URL/status-read-back this step would otherwise report):
- **Status:** Changes Requested (advisory) — non-gating `COMMENT` event, retrospective mode.
- **Reviewed head:** `36549bca3a63d581f7b68d08054a7813c1e6a499` (unchanged from the pinned head throughout the run; no drift possible offline).
- **Coverage:** complete.
- **Review URL:** none — publication disabled; nothing was written anywhere.
- **Finding URLs:** none — same reason; the finding's would-be inline location is `bokehjs/src/lib/models/widgets/date_picker.ts:82-83` at the reviewed head, rendered above.
- **Open questions:** none.
- **Disputed findings:** none (first review).
- **Anything that failed to publish:** nothing attempted; publication was never authorized for this retrospective target.

## 11. Status derivation

Per the output contract: one `must-fix` finding is unsettled (it is newly raised on a first review, not disputed, and not `not-verifiable` — it is `independent-confirmed`) → **`Changes Requested`**. Using `COMMENT` (no gating authorization) → body reads **"Changes Requested (advisory)"**, per the contract's rule to add `(advisory)` to `Changes Requested`/`Approved` under `COMMENT`.

## 12. Mechanism checklist

| Mechanism | Fired? | Where demonstrated |
|---|---|---|
| Question channel | **Did not fire.** | No candidate reached the static-unresolvability bar (rubric's Issue-fit question rule / Uncertainty routing): C1's fact was settled deterministically by direct execution (§5.3, §7.2), not left as an open empirical/product question. |
| Clean-verdict / related-acquittal verification | **Related-acquittal: did not fire** (no non-survivor row shared C1's anchor/claim per §6.2's explicit check). **Zero-survivor mode: did not fire** (C1 survived from the start, so the trigger condition — "when zero candidates survive *as findings*" — was never met). |
| Observations | **Did not fire** (published channel). The verifier returned one `observation` aside (§7.2); it was evaluated and folded into the finding's `Change` prose rather than published separately, per the rubric's one-fact-one-channel rule (§7.3, §9). No body-level `Observations` section appears in the payload. |
| Fix-sufficiency check on any concurrency/invariant candidate | **N/A / did not fire.** C1's `kind` is `bug`, not `concurrency`/`invariant`; `references/verifier-concurrency.md` was read (§2) only to confirm this and was correctly excluded from the verifier brief (§7). |
| Follow-up verifier round | **Did not fire.** Zero corrections, zero re-opened rows, zero newly-related rows after the first batch (§7.3) — "one initial batch, zero follow-up batches." |
| Deferral handling | **Did not fire — none found.** §5.5 explicitly checked the complete prior-review record (packet §6) for an explicit design/naming/API-shape deferral and found none. |
| Retrospective mode | **Fired.** `Mode` line present in the summary body (§10, payload file); publication skipped throughout; the would-be review reported in place of a review URL (§10). |
| Early dispatch of the verifier batch, relative to the falsification pass | **Fired — dispatched immediately after the complete falsification pass finished** (§7, "Early-dispatch analysis"). The diff does not touch a concurrency/failover/data-integrity/security surface, so the bar against early dispatch on those surfaces did not apply; by the time of dispatch, the complete diff was inspected, the manifest was finished, C1 had completed primary falsification, and no related-acquittal rows or other pending mandatory candidates remained — there was in fact no further `consider` falsification left to run "in the background" alongside the batch, since D1–D6 were already disposed before dispatch (§5.2/§6.2), so this run's early-dispatch and after-the-pass dispatch coincide in wall-clock terms; the analysis is recorded regardless, per the skill's instruction to record the dispatch timing rule explicitly. |

## 13. History discipline

I did **not** read any history beyond the pinned head `36549bca3a63d581f7b68d08054a7813c1e6a499`. Exact history-touching commands run, all within the merge-base..head ancestor range or older:
- `git log --oneline -5 review-head` (primary, §"clone structure" check) — lists the 5 pinned commits, oldest `472e4770d` (2019-09-22) to newest `36549bca3` (2019-10-02, the pinned head).
- `git branch -a` and `git status` (primary) — confirms clean tree, no drift, `origin` is local.
- `git show ccb4bcb4c2b841d89b0e88303a97bf4604a5795f:bokehjs/src/lib/models/widgets/date_picker.ts` (primary, §5.2 gate-2 check) — the merge-base blob, an ancestor state, not "beyond the head."
- `scripts/review_context.py`'s internal `history` section (primary, §4.2) — surfaced three pre-merge-base commits touching `date_picker.ts` (`e8b22ef16`, `475828e23`, `aa8f3028e`, all 2019-06 to 2019-08, i.e. ancestors of the merge-base) — read as printed output only, no separate `git log`/`git show` issued by me for them.
- The verifier sub-agent (§7.2, its own "Full audit trail") ran `git log --oneline ccb4bcb4c..36549bca3` (the merge-base..head range, explicitly not beyond head) and `git show <sha> --stat`/`-s --format=fuller` for the four commits on the reviewed head plus the head commit itself — all within the pinned range, none newer than `36549bca3`.

No `git fetch`, `git pull`, `git log` unbounded, or any command targeting a ref newer than `36549bca3` was run by me or by the sub-agent I dispatched.

## 14. Sandbox disclosure

All reads and writes stayed within: the skill snapshot (`/tmp/qual137/snapshots/bea6be14/skills/code-review-publish/`), the packet (`/tmp/qual137/packets/l/packet.md`), the clone (`/tmp/qual137/runs/l-bea6be14-seed1-att-13/`), my own work directory (`/tmp/qual137/work/l-bea6be14-seed1-att-13/`), and my own report/payload/timing paths (`/tmp/qual137/reports/l/l-bea6be14-seed1-att-13-*`). The verifier sub-agent confirmed the same boundaries for itself (§7.2).

**One incidental exposure to disclose:** in an early `ls -la` call I listed the contents of the shared directory `/tmp/qual137/reports/l/` to confirm my own report/payload/timing paths existed before writing to them; that listing incidentally showed the **file names** (not contents) of another cell's artifacts already present there — `l-867cf3ff-seed1-att-14-session.txt` and `l-867cf3ff-seed1-att-14-timing.json`. I did not open, read, or otherwise use either file; only their names were visible in the directory listing. Disclosed here per rule 7 ("Report any other path you read") out of caution, though strictly only a listing, not a read of file content, occurred.

## 15. Everything consulted beyond the diff (exhaustive)

**Files read in full or in bounded ranges** (all under the clone unless noted):
- `bokehjs/src/lib/models/widgets/date_picker.ts` — whole file (129 lines, ≤300, permitted without further justification), at head via `cat -n` and at merge-base via `git show <merge-base>:<path>` (bounded, lines 76-88 shown).
- `tests/integration/widgets/test_datepicker.py` — wholly new, fully present in the diff (§4.2); no separate read.
- `bokeh/models/widgets/inputs.py` — bounded range, lines 248-288 (`grep -n "class DatePicker" -A 40`), to find the Python-side `DatePicker.value`/`min_date`/`max_date` property declarations.
- `bokeh/core/property/datetime.py` — whole file (167 lines, ≤300), to read `Date.transform()`/`Date.validate()`.
- `bokeh/util/serialization.py` — bounded range, lines 140-210 (`Read` with offset/limit), to read `convert_datetime_type()`.
- `tests/integration/widgets/test_radio_button_group.py` — whole file, diffed against the new `test_datepicker.py` (`diff <(cat ...) <(cat ...)`) to establish that the new test file matches `bryevdv`'s prior-review-supplied template (§5.4, §5.5) — this is the rubric's "bounded read to establish local convention" for a new test file, done via a full-file diff rather than a line read since the comparison itself needed the whole sibling file.
- `.github/PULL_REQUEST_TEMPLATE.md` — **not read**; classified from its presence alone (packet §7) as outside the `guidance` digest categories and not consulted as a review standard (§3).

**Searches run** (all recorded with scope and case-sensitivity):
- `grep -l "bokeh_model_page\|bokeh_server_page" tests/integration/widgets/*.py` — scoped to the sibling directory `tests/integration/widgets/` (the rubric's "sibling glob" check for a new test file, deliberately *not* repo-wide — this is the narrower per-new-file convention check, distinct from the whole-repo case-insensitive sweep the propagation-drift rule requires for a different kind of candidate, which did not arise here since no synchronization-drift candidate was raised). Case-sensitive (fixture names are exact identifiers; no case-insensitivity requirement applies to this specific check). Result: 21 matches.
- `grep -n "class DatePicker" -A 40 bokeh/models/widgets/inputs.py` — single-file, case-sensitive, to locate the Python property block.
- `grep -n "class Date" bokeh/core/property/*.py` — scoped to one directory's `*.py` files, case-sensitive, to locate the `Date`/`Datetime` property classes.
- `grep -rn "datetime.date\|convert_datetime_type\|def transform_array\|def convert_date" bokeh/util/serialization.py bokeh/core/json_encoder.py` — two named files, case-sensitive, to locate the serialization entry points.
- No repo-wide or case-insensitive sweep was run, because no candidate in this review required the propagation/synchronization-drift procedure (rubric's Falsify-every-candidate §7, "For propagation or synchronization drift...") — this diff has no peer-artifact/shared-vocabulary surface (it is a single client-side helper method plus one new, wholly self-contained test file).

**Focused execution run** (offline, node v24.19.0, under the cell's execution allowance — none of this is the project's own build or Selenium suite, both correctly withheld):
- `/tmp/qual137/work/l-bea6be14-seed1-att-13/build_fingerprint_input.py` (Python, not a test — data-extraction tooling for the context digest) — exit 0, <1s.
- `python3 scripts/context_fingerprint.py /tmp/qual137/work/l-bea6be14-seed1-att-13/fingerprint_input.json` — exit 0, <1s, printed digest.
- `python3 scripts/review_context.py --merge-base ... --head ... --store ...` — exit 0, <1s, full output captured §4.2.
- `/tmp/qual137/work/l-bea6be14-seed1-att-13/unlocal_test.js` under `TZ=Europe/Paris`, `TZ=America/New_York`, `TZ=UTC`, `TZ=Pacific/Auckland`, `TZ=Pacific/Honolulu` — 5 separate `node` invocations, each exit 0, each <1s, well within the 5-minute-per-command bound. Full output in §5.3.
- `python3 scripts/validate_review.py --render`, `python3 scripts/validate_review.py` (validate), `python3 scripts/validate_review.py --emit-batch` — each exit 0, <1s, output in §9/§10.
- `python3 /tmp/qual137/mark_event.py .../timing.json payload_validated_at` — exit implied 0 (produced the expected stdout line and updated file, §9).
- The verifier sub-agent independently ran its own Node script (`/tmp/qual137/work/l-bea6be14-seed1-att-13/verify/test.js`) under 3 `TZ` values plus several `git show`/`git log --stat`/`find` commands, all exit 0 per its own report (§7.2).

No Selenium test, no `npm install`, no browser, and no project build were attempted anywhere in this run, per the packet's execution allowance.

## 16. Coverage

Both changed files `reviewed`:
- `bokehjs/src/lib/models/widgets/date_picker.ts` — reviewed (diff + whole-file read + gate-2 base/head comparison + risk-led caller/serialization reads).
- `tests/integration/widgets/test_datepicker.py` — reviewed (wholly new, fully in diff; all 3 test functions traced under the Changed-tests section, §5.4).

No `unreviewed` file. No packet gap (`comments_available: true`, no `comments_complete: false` marker, no failed continuation named in the packet). No omitted patch (`review_context.py`'s `chunks` inventory: `diff coverage: complete (2/2 chunks consumed)`, no `missing` chunk). Selenium/browser execution was unavailable but its absence was settled by execution-semantics trace for all three test functions (§5.4), which the rubric states does not by itself make coverage incomplete. **Coverage: complete.**

## 17. Notes — judgment calls on ambiguities in the skill's contract

1. **No raw forge JSON pages were available**, only the orchestrator-normalized `packet.md`. I treated this the same as `context_fingerprint.py`'s documented "forge without that packet" fallback and built the digest input directly from the packet's verbatim text via a small extraction script, rather than fabricating or skipping `forge_packet.py normalize`. I disclosed the resulting digest's dependence on a synthetic (order-based) comment `id` rather than a real `fullDatabaseId`, since the packet does not carry the latter (§4.1). This is the single largest reproducibility caveat in this run: a hypothetical sibling run with access to real forge ids would compute a **different** SHA-256 (the id is embedded per-comment), even though both digests would reflect the identical pinned inputs in identical order. I chose to compute and report the achievable digest rather than treating this as an "unrecoverable input" under the Uncertainty-routing rule, because the rubric's unrecoverable-input route is for inputs that gate a *candidate disposition* ("name exactly what the input could change and which candidate dispositions it gates") — the missing real forge comment-ids gate nothing in this review's admitted findings; they only affect exact digest reproducibility across hypothetical replicate runs, which is a property of the harness's data availability, not of this PR's evidence.
2. **PR title reconstruction**: the packet's identity table renders the title with a mid-string ellipsis (`...UTC+…`), which I judged to be a markdown-table-width truncation artifact rather than the literal pinned title, and used the complete, unambiguous string from commit 1's message instead (identical prefix, no ellipsis, and matching the general subject the packet unambiguously establishes). I disclosed this substitution rather than embedding the truncated string (which would have been a visibly wrong/incomplete title) or silently guessing a different completion.
3. **`.github/PULL_REQUEST_TEMPLATE.md` classification**: I read the output contract's `guidance` field definition narrowly (root/path-scoped `AGENTS.md`/`CLAUDE.md`, root `CONTEXT.md` only) and excluded the PR template from both the digest's `guidance` array and from repository-rule findings consideration, since it is the submission form the author filled in (already reproduced verbatim in the packet as the PR body) rather than a standards document imposed on the diff's changed paths. I did not treat this as a contestable term needing an `Ambiguities` entry, because the output contract's membership list is explicit and exhaustive ("These membership rules are exhaustive") and a PR template plainly does not match any of the three listed categories — this was not a close call.
4. **No `Ambiguities`/`Unanchored findings`/`Coverage gaps`/`Open questions`/`Disputed`/`Prior findings` sections appear in the payload** — each was considered and found genuinely empty (§9, §10, §16), consistent with the output contract's instruction to include only non-empty conditional sections.
5. **Priority calibration (P1 vs P2) for C1**: I judged P1 ("urgent defect with serious or broadly affecting consequences") over P2 ("ordinary, concrete defect with material impact") because the defect affects an entire hemisphere's worth of timezones and is the *exact* defect class (off-by-one date display) the PR exists to fix, just for the un-tested half of the world — not a borderline call, but recorded as a judgment since the rubric leaves priority to reviewer discretion within its four-tier description.
6. **`Source` omission on the one finding**: judged that citing issue #9129 as `Source` would be actively misleading (the issue's requirement is `met`; the finding is an unrelated regression the fix introduces), so `Source` was omitted per the output contract's "omit unless materially supports the finding" rule, rather than included merely because an issue exists.
7. **Verifier's `observation` aside**: judged to restate C1's own mechanism (not a new, unrelated, sub-threshold fact) and therefore folded into the finding's prose rather than published as a second, separate `Observations` bullet — a one-fact-one-channel judgment call recorded in §7.3 and §9.



