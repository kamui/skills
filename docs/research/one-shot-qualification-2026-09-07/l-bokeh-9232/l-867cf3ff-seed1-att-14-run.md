# Research report — `bokeh/bokeh#9232` — cell `l-867cf3ff-seed1`, attempt `att-14`

**Status: COMPLETE.** Payload rendered (publication disabled per retrospective-merged-target rule) and validated with `scripts/validate_review.py` (exit 0) and `--emit-batch` (exit 0). Timing sidecar's `payload_validated_at` marked. Payload file: [`l-867cf3ff-seed1-att-14-payload.md`](l-867cf3ff-seed1-att-14-payload.md).

## 1. Metadata

- Target: `bokeh/bokeh#9232` ("Fixed issue of Datepicker displaying the wrong date for users in UTC+…")
- Cell: `l-867cf3ff-seed1`; attempt: `att-14`
- Skill snapshot: `/tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/`
- Skill `workflow` identifier reported by the validator: `v5b-1` (from `scripts/validate_review.py`'s `WORKFLOW = "v5b-1"` constant, confirmed by running `--self-test`-free inspection of the script; the payload's own run trailer will carry `workflow=v5b-1`)
- Model I (the primary reviewer) ran on: `claude-sonnet-5`
- Model every sub-agent ran on: `claude-sonnet-5` (passed explicitly as `model: "sonnet"` on the `Agent` call, per the cell's binding instruction)
- Posting identity: `kamui` (third party, did not author the PR, no prior review/comment from this identity on the PR)
- Retrospective mode: **yes** — PR is merged (`merged: true`), so this run follows SKILL.md's rule: "A merged pull request is reviewable only when invoked as a retrospective or audit review; disable publication..." Publication is disabled per the cell's binding conditions; the review is rendered exactly as it would be posted and reported in the research report instead of published.
- Verification trigger fired: **yes.** One candidate was raised and admitted as `must-fix`. SKILL.md's sentence: *"Independently verify every surviving candidate proposed as `must-fix`, plus every candidate involving security or authorization, data loss or corruption, destructive migration, or an externally observable compatibility break."* This candidate (the west-of-UTC display regression) is `must-fix`, so mandatory candidate-mode verification was required and run (see §4).
- Zero-survivor clean-verdict mode: did **not** fire (at least one candidate survived as a finding).
- Related-acquittal mode: did **not** fire. The only non-survivor ledger row (the parameter-mutation observation) has `kind=maintainability`, which is not one of the four qualifying kinds (`bug`, `concurrency`, `invariant`, `security`) that SKILL.md's related-acquittal rule requires, so it does not ride along with the mandatory verifier batch even though its decisive-evidence file is the same file as the survivor's anchor.
- Sub-agents spawned: **1** — one independent candidate-mode verifier, `subagent_type: "general-purpose"`, `model: "sonnet"`, `run_in_background: false` (foreground, awaited).
- Candidates raised: 2 (1 survivor/must-fix finding; 1 non-survivor routed to Observations).
- Candidates surviving primary falsification (eligible for verification/publication): 1.
- Verifier verdict: **`confirmed`**, no corrections to any field (see §9 for the verbatim report).
- Findings for publication: 1 (see §6).
- Questions: 0.
- Observations: 1 (parameter-mutation hazard; consequence absent today).
- Coverage: both changed files fully reviewed (each ≤300 lines: 129 and 98 lines respectively); all rubric risk-directed checks with an evidence-backed outcome (see §5, §7); coverage is `complete`.
- Derived status: **`Changes Requested (advisory)`** — event `COMMENT` (posting identity did not author the PR and no gating authorization exists; the target is merged and retrospective, so publication and any gating event are moot regardless). Per `output-contract.md`'s status rule 1, an unsettled `must-fix` finding (`independent-confirmed`, not yet addressed by the author) forces `Changes Requested`; `(advisory)` is appended because the event is `COMMENT`, not the authorized gating event.
- My own token usage: the harness does not report this to me in this transcript for the primary reviewer; I have no token-usage figure to give for myself. The one sub-agent's usage *was* reported by the harness: `subagent_tokens: 34241`, `tool_uses: 5`, `duration_ms: 94073` (see §9).

## 2. `context` digest and its inputs

Computed once via `python3 scripts/context_fingerprint.py /tmp/qual137/work/l-867cf3ff-seed1-att-14/context_input.json` from the skill snapshot directory:

```
9ce7772c753e38225d78d80e2051b0392b6f3d727d0e3d5e217b78ba72c338ff
```

Inputs (the exact JSON is preserved at `/tmp/qual137/work/l-867cf3ff-seed1-att-14/context_input.json`):

- `pr.title`: `Fixed issue of Datepicker displaying the wrong date for users in UTC+…` — taken **verbatim** from the packet's pinned run-identity table, ellipsis character included (the packet truncates it that way; see Notes §10 for the judgment call this required).
- `pr.body`: the packet's §3 verbatim body, starting `… timezones.` through the three-item checklist (`- [x] issues: fixes #9129`, two unchecked boxes) — again pinned verbatim including the leading ellipsis.
- `issues`: one issue, `bokeh/bokeh#9129`, title `[BUG]Datepicker displayed value is not updating correctly`, body verbatim from packet §4, and all 18 comments verbatim from packet §4 with `comments_available: true`. The packet gives no forge-native numeric comment ids, only a 1–18 enumeration order; I used that enumeration position as the digest's integer `id` field (a judgment call — see Notes §10).
- `specs`: `[]` — no user-supplied spec was given.
- `guidance`: `[]` — the merge-base guidance sweep (packet §7) found only `.github/PULL_REQUEST_TEMPLATE.md` present; per `output-contract.md`'s exhaustive guidance-membership rule (root/path-scoped `AGENTS.md`/`CLAUDE.md` plus root `CONTEXT.md` only), a PR template does not qualify, so `guidance` is empty. I additionally read `.github/PULL_REQUEST_TEMPLATE.md` at `master` (`git show master:.github/PULL_REQUEST_TEMPLATE.md`) to confirm it is the ordinary issue/PR-process checklist template and not a disguised `AGENTS.md`/`CLAUDE.md`.

## 3. Private requirement ledger (from step 2)

| # | Requirement (from issue #9129) | Disposition | Evidence |
| - | - | - | - |
| 1 | The DatePicker's displayed value must reflect the actual calendar day the user selected/was given, independent of the user's local timezone (issue reported specifically for UTC+ testers: France, UK, Germany). | **partial** | Node reproduction of the diff's exact `_unlocal_date` logic (§5) shows the after-selection path is now correct for UTC+ users (fixes the reported symptom), but the same change breaks the initial-load / server-set `value`/`min_date`/`max_date` path for any UTC-negative ("behind UTC") timezone — tied to Finding 1 in §2 below (candidate id `bokehjs/date-picker-west-of-utc-regression`). |

No explicit non-goals were stated in the issue or PR body.

## 4. Manifest / coverage

| File | Status | How reviewed |
| - | - | - |
| `bokehjs/src/lib/models/widgets/date_picker.ts` | reviewed | Whole file read (129 lines, ≤300-line threshold); diff read once from `review_context.py`'s `diff` section (function-context hunk, full `_unlocal_date`/`render` bodies already shown); cross-checked against `git show master:bokehjs/src/lib/models/widgets/date_picker.ts` implicitly via the `diff` output's `-` side, and against the issue's own inline quoted snippet of the pre-fix function (packet §4 comment 6) which matches the merge-base content. |
| `tests/integration/widgets/test_datepicker.py` | reviewed | New file, fully present in the single `diff` output (98 lines, ≤300); rubric's new-file hygiene checks applied (see §5). |

Repository guidance: `.github/PULL_REQUEST_TEMPLATE.md` present at merge-base, read and classified as **not** `guidance` under `output-contract.md`'s exhaustive membership rule (see §2). No root/path-scoped `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` exists at the merge-base for any changed path (confirmed by packet §7's mirror lookup; I did not re-verify by an independent `git show` because the packet states its rows were "verified by direct lookup in the mirror" and rule §7 of the run conditions tells me to treat every pinned fact as authoritative).

## 5. Everything consulted beyond the diff (commands, searches, execution)

All commands below were run from `/tmp/qual137/runs/l-867cf3ff-seed1-att-14` (the clone) or `/tmp/qual137/snapshots/867cf3ff/skills/code-review-publish` (the skill directory) or `/tmp/qual137/work/l-867cf3ff-seed1-att-14` (my work directory), never mutating the clone.

1. `python3 /tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/scripts/review_context.py --merge-base ccb4bcb4c2b841d89b0e88303a97bf4604a5795f --head 36549bca3a63d581f7b68d08054a7813c1e6a499` — exit 0. Produced the manifest, full diff, `ranges`, and `history` sections (192 lines), saved to `/tmp/qual137/work/l-867cf3ff-seed1-att-14/review_context_output.md`. Run exactly once, per SKILL.md §2/§3.
2. `git log --oneline -5 review-head` and `git branch -a` and `git status` in the clone — confirmed the clone's state (branch `review-head` checked out at `36549bca3`, tree clean, no history beyond the pinned head reachable — see §8).
3. `wc -l bokehjs/src/lib/models/widgets/date_picker.ts` → 129 lines; then a full `Read` of that file.
4. `grep -n "_unlocal_date" -r bokehjs` (via the `Grep` tool, repo-wide within `bokehjs/`, case-sensitive — the identifier has no case variants worth searching case-insensitively) — found exactly 3 call sites, all in `date_picker.ts` itself (lines 68, 70, 71), each wrapped in a freshly constructed `new Date(...)`. This is the decisive evidence that the parameter-mutation observation (§2 Observations) has no current consequence.
5. `grep -n "class DatePicker" bokeh/models/widgets/inputs.py` and a read of the surrounding lines — found `value = Date(...)`, `min_date = Date(default=None, ...)`, `max_date = Date(default=None, ...)`.
6. `Read` of `bokeh/core/property/datetime.py` in full (167 lines) — the `Date.transform()` method, showing that a numeric input becomes `datetime.date.fromtimestamp(value)` (server-side, local-time based) and a string input becomes `dateutil.parser.parse(value).date()` (naive, calendar-literal). This established the Python-side coercion behavior but is not itself the wire-serialization step.
7. `grep -n "convert_datetime_type|transform_value" -r bokeh` (via the `Grep` tool, repo-wide over `bokeh/`, not case-insensitive — identifiers are case-sensitive Python names) — found the wiring: `bokeh/core/json_encoder.py:186` calls `convert_datetime_type(obj)` inside the document's `BokehJSONEncoder`, and `bokeh/util/tests/test_serialization.py:118` asserts `convert_datetime_type(datetime.date(2016, 5, 11)) == 1462924800000.0` (a UTC-midnight epoch), confirming that a Python `datetime.date` assigned to `DatePicker.value`/`min_date`/`max_date` is sent to the browser as a UTC-midnight timestamp, not a local-time one.
8. `Read` of `bokeh/util/serialization.py` lines around 152–195 (`convert_datetime_type`), confirming `elif isinstance(obj, dt.date): return (dt.datetime(*obj.timetuple()[:6]) - DT_EPOCH).total_seconds() * 1000` with `DT_EPOCH = dt.datetime.utcfromtimestamp(0)` — a naive-datetime subtraction that treats the date's calendar components as already being UTC, i.e. produces the UTC-midnight instant for that calendar day.
9. `ls tests/integration/widgets/` and `grep -l "bokeh_server_page" tests/integration/widgets/*.py` (repo-wide over that directory, not case-insensitive) — the rubric's required batched sibling-glob search for the new test file's declared-but-possibly-unused fixture pattern. Found 11 sibling files using `bokeh_server_page`.
10. `grep -n "has_no_console_errors|def test_server|bokeh_server_page" tests/integration/widgets/test_radio_button_group.py tests/integration/widgets/test_checkbox_button_group.py` — showed the sibling convention: the `bokeh_server_page`-based round-trip test in both siblings has `page.has_no_console_errors()` **commented out** with `# XXX (bev) disabled until https://github.com/bokeh/bokeh/issues/7970 is resolved`, matching the new test's omission of that assertion in its own server round-trip test. This means the new test's omission is consistent with, not a deviation from, established convention — no hygiene finding.
11. `Read` of `tests/integration/widgets/test_radio_button_group.py` in full (115 lines) — the file bryevdv pointed to as "a somewhat similar case to emulate" (packet §6 comment 5), used as the convention baseline for item 10 above.
12. `git show master:.github/PULL_REQUEST_TEMPLATE.md` — read the only present guidance-candidate file; confirmed ordinary PR-process checklist, not `AGENTS.md`/`CLAUDE.md`-equivalent (see §2, §4).
13. Node execution (permitted per run condition 2 / packet §8.2), under `/tmp/qual137/work/l-867cf3ff-seed1-att-14/scratch/test_unlocal.js`: reproduced the exact pre-fix and post-fix `_unlocal_date` logic (copied verbatim from the diff and from the merge-base) against two input shapes — (A) a `Date` built from `Date.UTC(2019, 8, 20, 0, 0, 0)` (simulating the server-supplied UTC-midnight epoch for `value`/`min_date`/`max_date`), and (B) a `Date` parsed from the literal string `"Fri Sep 20 2019"` (simulating the `_on_select`→`toDateString()` round trip). Run three times, once per `TZ` value:
    - `TZ=Europe/Paris node .../test_unlocal.js` — exit 0, <1s. Output: Case A old→`Fri Sep 20 2019`, new→`Fri Sep 20 2019` (unchanged, correct); Case B old→`Thu Sep 19 2019` (the originally reported bug, reproduced), new→`Fri Sep 20 2019` (fixed).
    - `TZ=America/New_York node .../test_unlocal.js` — exit 0, <1s. Output: Case A old→`Fri Sep 20 2019` (correct), new→`Thu Sep 19 2019` (**newly wrong** — the regression this review's finding is about); Case B old→`Fri Sep 20 2019`, new→`Fri Sep 20 2019` (unaffected, still correct).
    - `TZ=UTC node .../test_unlocal.js` — exit 0, <1s. Output: both cases unaffected under either version (offset is 0), as expected.
    
    This is the decisive, reproducible evidence for the survivor finding.
14. No CI logs were available offline (no `gh`, no network); this diff includes no CI-configuration changes, so CI evidence was not applicable rather than a coverage gap. No project build or the Selenium integration suite was run, per run condition 5 (explicitly disallowed offline); the added test file's own execution against a real browser could not be checked, only its static hygiene (item 9–11 above) and its lack of coverage for the regression this review found (see Notes, §10).

## 6. Findings for publication

### Finding 1 — `bokehjs/date-picker-west-of-utc-regression`

- Priority/action: **P1 / must-fix / blocking=true**
- Kind: `bug`
- Anchor: `bokehjs/src/lib/models/widgets/date_picker.ts:82-83` (RIGHT)
- Fix location: same as anchor (omitted in the trailer per contract)
- Claim: The new offset-compensation code in `_unlocal_date` subtracts `date.getTimezoneOffset() * 60000` from every input `Date`. That is correct only when the input represents a client-parsed local-midnight instant (the `_on_select` → `toDateString()` round trip). It is wrong when the input already represents a UTC-midnight instant — which is exactly what `DatePicker.value`/`min_date`/`max_date` are on initial page load and on every server-driven update, per `bokeh/util/serialization.py`'s `convert_datetime_type`. For any timezone behind UTC (`getTimezoneOffset() > 0`), subtracting a positive offset from a UTC-midnight instant rolls the instant — and therefore the displayed calendar day — back into the previous day.
- Verification status: **independent-confirmed** (verifier batch dispatched and returned; see §4 sub-agent section below for the verbatim verdict).
- Evidence: `bokehjs/src/lib/models/widgets/date_picker.ts:82-83`; `bokeh/util/serialization.py:183-184` (corroborated by `bokeh/util/tests/test_serialization.py:118` and the wiring at `bokeh/core/json_encoder.py:186`); Node reproduction under `TZ=America/New_York` (§5 item 13): server-set value `2019-09-20T00:00:00Z` renders as `Fri Sep 20 2019` at the merge-base and as `Thu Sep 19 2019` at the head.
- Trigger scenario: A user whose browser timezone is behind UTC (e.g. `America/New_York`, `America/Los_Angeles`, most of the Americas and the Pacific) opens a Bokeh document containing a `DatePicker` whose `value`, `min_date`, or `max_date` was set from Python (a `datetime.date`), or receives a document patch that sets one of those from the server. `min_date`/`max_date` are affected on *every* render, not just initial load, because nothing in this widget ever re-assigns them through the string-parsing path the fix actually corrects.
- Impact: The displayed date (and the selectable min/max bounds) is off by one calendar day — one day earlier than the true value — for a large population of timezones, trading the originally reported UTC+ bug for a new, symmetric UTC− bug that was not covered by the manual testing recorded in the review thread (bryevdv's "this seems to be working great for me in PST" — PST is `America/Los_Angeles`, itself a UTC-negative zone — exercised only the after-selection path, which this reproduction shows is unaffected either way) nor by the added integration test (which never asserts the *initial* displayed value, only the value after a fresh selection).
- Suggested change: Do not apply the blanket `getTimezoneOffset()` shift to a `Date` that already represents a UTC-midnight instant. Normalize the two input shapes before the shared logic runs — for example, derive the calendar day from the input's own UTC accessors (`getUTCFullYear()/getUTCMonth()/getUTCDate()`) for the server-set path, and keep the local-offset compensation only for the client-parsed-string path — so both `UTC-behind` and `UTC-ahead` users see the correct day on every render, not just after a client-side selection.

## 7. Observations (summary-body channel)

- `_unlocal_date` mutates its `date` parameter in place via `date.setTime(...)` rather than operating on a copy, which would corrupt a caller-retained `Date` if one is ever added; today no caller retains a reference, since all three call sites (`bokehjs/src/lib/models/widgets/date_picker.ts:68,70,71`) pass a freshly constructed `new Date(...)` expression. Evidence: `bokehjs/src/lib/models/widgets/date_picker.ts:78-83`.

## 8. Complete private disposition ledger

| id | kind | disposition | decisive evidence | falsification reason | verifier ruling? |
| - | - | - | - | - | - |
| `bokehjs/date-picker-west-of-utc-regression` | bug | **survivor** (must-fix) | `bokehjs/src/lib/models/widgets/date_picker.ts:82-83`; `bokeh/util/serialization.py:183-184`; Node repro under `TZ=America/New_York` | n/a — passed all falsification gates | **Yes** — mandatory candidate-mode verification (proposed `must-fix`); see §4/§9 sub-agent dispatch below |
| `bokehjs/date-picker-mutates-parameter` | maintainability | dropped → routed to Observations (`observation (consequence absent)`) | `bokehjs/src/lib/models/widgets/date_picker.ts:78-83`; `grep -n "_unlocal_date" -r bokehjs` shows only 3 call sites, all fresh `new Date(...)` | Fails rubric gate 4 (proven consequence): no current caller retains the pre-mutation `Date`, so the mutation has zero observable effect today; it is a latent hazard, not a proven one — "Speculation about downstream breakage is insufficient" | **No** — SKILL.md requires mandatory verification only for `must-fix`/security/data-loss/destructive-migration/compatibility-break candidates, and related-acquittal riding-along only for non-survivor rows whose `kind` is `bug`/`concurrency`/`invariant`/`security`. This row's `kind` is `maintainability`, so neither rule applies; it was never put in front of the verifier. |

No other candidates were raised. The diff is small (+6/−2 in one file, +98/−0 new test file) and I did not find additional falsifiable claims after the two above (comment-wording style change, the removed `.idea/vcs.xml` — already resolved before the pinned head per the prior-review thread — and the test file's fixture/CSS-class usage were all checked and found unremarkable; none reached even observation-worthy status because they lack a decisive, non-trivial evidence pointer beyond "the code looks like X").

## 9. Sub-agent dispatch

**Dispatch 1 of 1 — candidate-mode verifier.** `Agent` tool, `subagent_type: "general-purpose"`, `model: "sonnet"`, `run_in_background: false` (foreground, awaited before continuing). Dispatched after primary falsification of both candidates was complete and the candidate ledger (§8) was fully written to this report file — this SKILL.md defines no "early dispatch before falsification" mechanism (checklist item 7 in the task: "if your skill defines one" — it does not; SKILL.md's only sequencing rule is "Read `references/verifier.md` when verification is required... run one initial candidate batch" *after* "Falsify and deduplicate every candidate under the rubric in the primary context," which is the order I followed).

### Exact prompt given to the verifier

```
You are an independent fresh-context verifier for one code-review candidate. You are NOT a second reviewer: do not search for new findings, do not write anything, do not modify any file. Follow exactly the verification task below; do not import any other review methodology.

## Binding operating rules (apply to you as well as the primary reviewer)

1. Offline. The clone's `origin` points at a local filesystem path, not github.com. No `git fetch`, `git pull`, `gh`, `curl`, or any network call, by you.
2. Execution allowance: node (v24.19.0) is installed; you may write and run scratch JavaScript under `/tmp/qual137/work/l-867cf3ff-seed1-att-14/scratch/` (your own subdirectory there is fine) to check code behavior you've read, including with a `TZ` environment variable set. Five minutes per command. Do NOT attempt the project's own build or its Selenium suite (unavailable offline). Do not add or change anything inside the clone.
3. History is truncated at the pinned head (`36549bca3a63d581f7b68d08054a7813c1e6a499`) on purpose in this clone. Do not try to work around that. If you run any `git log`/`git show` beyond what's needed, report exactly which commands.
4. Clone hygiene: do NOT run `git checkout`, `git switch`, `git reset`, `git stash`, or anything that mutates the working tree of `/tmp/qual137/runs/l-867cf3ff-seed1-att-14`. Read-only git commands (`git show`, `git diff`, `git log`) are fine.
5. Stay inside this sandbox only: the clone at `/tmp/qual137/runs/l-867cf3ff-seed1-att-14`, the skill snapshot at `/tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/`, the packet at `/tmp/qual137/packets/l/packet.md`, and your scratch subdirectory under `/tmp/qual137/work/l-867cf3ff-seed1-att-14/`. Do not read any other run's clone, report, or payload (in particular, do not read anything under `/tmp/qual137/reports/l/` other than nothing — you have no need to read report files at all). If you read anything outside this sandbox, say so explicitly in your report.
6. This is a one-shot task. Do not ask anyone anything; finish and return your verdict in this single response.

## Pinned run identity

- Repository: `bokeh/bokeh`, clone at `/tmp/qual137/runs/l-867cf3ff-seed1-att-14`
- Base ref: `master` (local branch `master`, pinned to the merge-base)
- Base SHA / merge-base: `ccb4bcb4c2b841d89b0e88303a97bf4604a5795f`
- Head SHA: `36549bca3a63d581f7b68d08054a7813c1e6a499` (local branch `review-head`, already checked out — do not switch branches)
- Originating issue: `bokeh/bokeh#9129` — "[BUG]Datepicker displayed value is not updating correctly". Summary: users in UTC+ timezones (France UTC+2, UK UTC+1, Germany UTC+2) reported that after selecting a date in the DatePicker widget, the displayed value showed one day earlier than the day actually clicked; the underlying value was correct. A maintainer (`bryevdv`) tested a fix "in PST" (America/Los_Angeles, a UTC-negative/west-of-UTC zone) and reported it "working great."

## `ranges` (from `scripts/review_context.py`, read these bounded ranges rather than the whole file if you prefer, though the file is short)

```
bokehjs/src/lib/models/widgets/date_picker.ts:45-98 @head
bokehjs/src/lib/models/widgets/date_picker.ts:45-94 @merge-base
```

Read the anchor/fix range at head with `Read` on `/tmp/qual137/runs/l-867cf3ff-seed1-att-14/bokehjs/src/lib/models/widgets/date_picker.ts`, and at merge-base with `git -C /tmp/qual137/runs/l-867cf3ff-seed1-att-14 show master:bokehjs/src/lib/models/widgets/date_picker.ts` (or `git show ccb4bcb4c2b841d89b0e88303a97bf4604a5795f:bokehjs/src/lib/models/widgets/date_picker.ts`).

## The candidate (verify this one candidate only)

```yaml
id: bokehjs/date-picker-west-of-utc-regression
kind: bug
priority: P1
action: must-fix
anchor:
  type: line
  path: bokehjs/src/lib/models/widgets/date_picker.ts
  start_line: 82
  end_line: 83
  side: RIGHT
fix: (same as anchor)
title: Fix breaks initial/min/max date display for timezones behind UTC
claim: >
  The new offset-compensation code added by this diff in `_unlocal_date` subtracts
  `date.getTimezoneOffset() * 60000` from every input `Date`. That is correct only
  when the input represents a client-parsed local-midnight instant (the `_on_select`
  -> `toDateString()` round trip, where the browser assigns `this.model.value` to a
  string like "Fri Sep 20 2019" and a later render does `new Date(this.model.value)`).
  It is wrong when the input already represents a UTC-midnight instant, which is what
  `DatePicker.value`/`min_date`/`max_date` are whenever they arrive from the Python/
  server side (see `bokeh/util/serialization.py`'s `convert_datetime_type`, wired into
  the document JSON encoder at `bokeh/core/json_encoder.py:186`, which serializes a
  Python `datetime.date` to a UTC-midnight epoch-ms timestamp -- confirmed by the
  existing test assertion `bokeh/util/tests/test_serialization.py:118`:
  `convert_datetime_type(datetime.date(2016, 5, 11)) == 1462924800000.0`). For any
  timezone behind UTC (`date.getTimezoneOffset() > 0`, e.g. every US/Canada/Latin-
  America zone, and PST specifically), subtracting a positive offset from a
  UTC-midnight instant rolls the instant, and therefore the rendered calendar day,
  back into the previous day.
trigger: >
  A user whose browser timezone is behind UTC (getTimezoneOffset() > 0) opens a
  document containing a DatePicker whose `value`, `min_date`, or `max_date` was set
  from Python (a `datetime.date`), or receives a server-side document patch setting
  one of those. `render()` calls `this._unlocal_date(new Date(this.model.value))`,
  and similarly for min_date/max_date, on every re-render (see connect_signals()),
  and min_date/max_date are never reassigned through the toDateString() string path,
  so they hit this bug on every render, not just initial load.
impact: >
  The displayed date, and the selectable min/max bounds, is off by one calendar day
  (one day too early) for any UTC-negative timezone, for the initial value and for
  min_date/max_date at all times. This trades the originally reported UTC+ bug for a
  new, symmetric UTC- bug.
change: >
  Do not apply the blanket getTimezoneOffset() shift to a Date that already
  represents a UTC-midnight instant; normalize the two input shapes (server-set
  UTC-midnight vs. client-parsed local-midnight-string) before the shared logic
  runs, e.g. by deriving the calendar day from the input's own UTC accessors
  (getUTCFullYear()/getUTCMonth()/getUTCDate()) for the server-set path, and
  reserving the local-offset compensation for the client-parsed-string path.
raw_code_citations:
  - "bokehjs/src/lib/models/widgets/date_picker.ts:78-88 (current _unlocal_date, head)"
  - "bokehjs/src/lib/models/widgets/date_picker.ts:66-73 (render(), the three call sites, head)"
  - "bokeh/util/serialization.py:152-195 (convert_datetime_type)"
  - "bokeh/core/json_encoder.py:186 (wiring convert_datetime_type into the document encoder)"
requirement_source: bokeh/bokeh#9129 (implicit: fix must not regress correct display for any other timezone while fixing UTC+)
```

## Verification task (from `references/verifier.md`, condensed for this single candidate)

1. Read the cited anchor and fix range (same location) at head and at merge-base (commands above), plus enough surrounding context (render(), _on_select(), connect_signals()) to decide the claim.
2. Independently reproduce or trace the stated trigger through the current code. You have node execution allowance: write your own scratch JS under `/tmp/qual137/work/l-867cf3ff-seed1-att-14/scratch/` reproducing the *exact* `_unlocal_date` function body as it appears at head (copy it verbatim from what you read), and as it appears at merge-base, and evaluate both against (a) a `Date` built to represent a UTC-midnight instant for a given calendar day (simulating a server-set value/min_date/max_date), and (b) a `Date` parsed from a `toDateString()`-format string (simulating the post-selection round trip). Run this under at least one UTC-negative TZ (e.g. `TZ=America/Los_Angeles`, matching bryevdv's "PST" test) and at least one UTC-positive TZ (e.g. `TZ=Europe/Paris`, matching the original bug reporters), each as a separate command invocation with the TZ environment variable set.
3. Establish the observable impact and whether any unchanged code prevents it (e.g., does anything else re-derive value/min_date/max_date before they reach `_unlocal_date`? does anything ensure min_date/max_date are never actually UTC-midnight-shaped in practice? check `bokeh/models/widgets/inputs.py`'s `DatePicker` property declarations and `bokeh/core/property/datetime.py`'s `Date.transform()` if useful).
4. For this Code candidate, confirm whether the change introduced the behavior (i.e., was the UTC-negative / server-set-value path correct at merge-base and wrong at head?), citing the merge-base guarantee and the head-branch code that no longer provides it.
5. Confirm that the issue, PR description/commits, or review thread do not establish this specific regression as an intentional, accepted tradeoff. (You have the issue and review-thread summary above; there is no need to re-fetch anything — it is offline anyway.)
6. Check whether this is the same underlying request as any other candidate — there is only one candidate here, so this step is trivially satisfied; just confirm you were given only one candidate.

For a `kind=bug` candidate (not `concurrency`/`invariant`), the extra bug-class interleaving checklist in verifier.md does not apply — only `concurrency`/`invariant` candidates get that.

## Verdict format

Return exactly one of:
- `confirmed`: decisive evidence establishes the trigger, qualifying impact, requested outcome, and that the change introduced the behavior (not pre-existing).
- `refuted`: decisive evidence shows the claim is false, prevented by unchanged code, intentional, lacks qualifying impact, or is pre-existing (already broken the same way at merge-base). If you cannot construct the claimed failing trace end-to-end and cannot refute a specific step either, that also counts as `refuted`, but then you must name, in one sentence, the single fact that would settle it and who/what could supply it.

Give: the verdict; a concise independent justification; the decisive code/execution citations (including your own node repro output); any correction you'd make to `trigger`, `impact`, `priority`, `action`, `anchor`, `fix`, or `change`; and, if one surfaces incidentally, at most one non-actionable `observation` aside with a decisive evidence pointer (only if it doesn't contradict this candidate's premise — if it does contradict the premise, that's not an aside, fold it into your verdict instead).

Do not produce publication-ready prose. Return your structured verdict as plain text in your final response.
```

### Verbatim verifier report

```
## Verdict: confirmed

### Independent justification

Read both versions directly:
- **Merge-base** `_unlocal_date` (`ccb4bcb4c2b841d89b0e88303a97bf4604a5795f:bokehjs/src/lib/models/widgets/date_picker.ts:78-83`): just does `date.toISOString().substr(0,10)` — no offset math.
- **Head** `_unlocal_date` (`bokehjs/src/lib/models/widgets/date_picker.ts:78-88`, candidate anchor lines 82-83): adds `const timeOffsetInMS = date.getTimezoneOffset()*60000; date.setTime(date.getTime() - timeOffsetInMS)` before the `toISOString()` call.

`render()` (lines 66-73, unchanged in shape across both versions) calls `_unlocal_date(new Date(this.model.value/min_date/max_date))` on every re-render (`connect_signals()` re-renders on `model.change`), for value, min_date, and max_date alike.

Traced the server-side path: `bokeh/models/widgets/inputs.py:253-263` declares `DatePicker.value/min_date/max_date` as `Date` properties; `bokeh/core/json_encoder.py:186` routes any `datetime.date` through `convert_datetime_type` (`bokeh/util/serialization.py:183-184`), which computes `(datetime(*obj.timetuple()[:6]) - DT_EPOCH).total_seconds()*1000` — i.e. treats the date as UTC midnight, exactly matching the cited test (`test_serialization.py:118`: `date(2016,5,11) -> 1462924800000.0`). The JS-side property type is `p.Any` (unchanged at head, `date_picker.ts:124-126`) — nothing transforms/normalizes this before it reaches `_unlocal_date`.

**Node repro** (verbatim function bodies copied from both versions), run under two real TZ settings:

```
--- TZ=America/Los_Angeles (PST, west of UTC) ---
serverDate.toISOString() = 2016-05-11T00:00:00.000Z
HEAD  unlocal_date(serverDate) = Tue May 10 2016   <-- WRONG (regression)
BASE  unlocal_date(serverDate) = Wed May 11 2016   <-- correct
clientDate (toDateString round-trip) local midnight Sep 20 2019
HEAD  unlocal_date(clientDate) = Fri Sep 20 2019   <-- correct
BASE  unlocal_date(clientDate) = Fri Sep 20 2019   <-- was already correct in PST

--- TZ=Europe/Paris (UTC+2, east of UTC) ---
HEAD  unlocal_date(serverDate) = Wed May 11 2016   <-- correct
BASE  unlocal_date(serverDate) = Wed May 11 2016   <-- correct
HEAD  unlocal_date(clientDate) = Fri Sep 20 2019   <-- fixed (was the #9129 bug)
BASE  unlocal_date(clientDate) = Thu Sep 19 2019   <-- original bug (off by one day early)
```

This is decisive and end-to-end:
- The diff correctly fixes the originally-reported bug (Paris/UTC+, client-parsed `toDateString()` round trip from `_on_select`).
- The same diff introduces a new, symmetric regression for UTC-negative zones (PST/Los_Angeles, and any west-of-UTC zone) specifically on the server-set value/min_date/max_date path (initial value, min_date, max_date on every render) — exactly bryevdv's own test zone, but a different code path than what he apparently exercised (the interactive select round trip, which is unaffected/still correct in PST).
- Merge-base did not have this defect (`toISOString()` of a UTC-midnight instant is timezone-invariant), so the change introduced the regression rather than it being pre-existing.
- Nothing in the unchanged Python/JS property machinery prevents `model.value`/`min_date`/`max_date` from arriving as UTC-midnight-epoch numbers — confirmed by tracing `Date` property → `convert_datetime_type` → `p.Any` JS property with no transform.
- Nothing in the provided issue/PR/thread context frames this as an accepted tradeoff; it reads as a genuine gap in manual verification (bryevdv tested "in PST" and it looked fine, but that almost certainly wasn't exercising the initial/min_date/max_date server-set path, which is exactly what breaks in PST).
- Only one candidate was given, satisfying the "same underlying request" check trivially.

### Corrections to the candidate's fields
None needed. `trigger`, `impact`, `anchor` (lines 82-83), and `change` are all accurate and well-targeted. `priority: P1` / `action: must-fix` is reasonable given this silently reintroduces the exact class of user-visible bug the diff was meant to close, just for the opposite half of the world's timezones, including the reference/spec-relevant zone (PST) the fix was manually validated against.

### Observation (non-actionable aside)
None beyond what's already folded into the verdict above (the bryevdv-test-coverage gap is part of the core justification, not a separate aside).
```

Sub-agent metadata reported by the harness: `agentId: afe59d7fb9e0a8a41`, `subagent_tokens: 34241`, `tool_uses: 5`, `duration_ms: 94073`.

### Primary-reviewer handling of the verdict

`confirmed`, no corrections needed to any field. Per `verifier.md`'s "Primary reviewer handling," I publish the mandatory-verification candidate as-is: `bokehjs/date-picker-west-of-utc-regression` is `P1`/`must-fix`/`blocking=true`, `verification: independent-confirmed`. No follow-up batch is needed (no candidate newly reached render eligibility; no clean-verdict or related-acquittal ruling occurred; nothing was re-opened).

## 10. Validation and payload rendering

- `python3 scripts/validate_review.py --render < payload_draft.json` (run from the skill directory) — exit 0, printed one fragment: `anchor [\`bokehjs/src/lib/models/widgets/date_picker.ts:82-83\`](https://github.com/bokeh/bokeh/blob/36549bca3a63d581f7b68d08054a7813c1e6a499/bokehjs/src/lib/models/widgets/date_picker.ts?plain=1#L82-L83)`, pasted verbatim into the summary body's `Findings` line (never hand-composed).
- `python3 scripts/validate_review.py < payload_draft.json` (final payload, fragment pasted in) — **exit 0**, zero violations reported.
- Immediately after that exit-0, ran `python3 /tmp/qual137/mark_event.py /tmp/qual137/reports/l/l-867cf3ff-seed1-att-14-timing.json payload_validated_at` — recorded `payload_validated_at: 2026-09-07T08:04:52.409561+00:00` in the timing sidecar. The payload was not changed after this point, so no second validation/mark was needed.
- `python3 scripts/validate_review.py --emit-batch < payload_draft.json` — exit 0, produced the one-call GitHub review batch (`commit_id`, `event: COMMENT`, `body`, one line `comments` entry spanning `start_line=82`/`line=83` on `RIGHT`). This is the exact shape SKILL.md §6 says to submit; it was rendered and inspected but never sent (no `gh api`, no network, per run condition 4/rule 2 of the cell).
- Because this is retrospective mode with publication disabled, SKILL.md §5's "re-fetch the pull-request head immediately before the first write" step and §6's actual submission step are both skipped by design (rule 2: "Where a step says 'publish', render instead and stop"). No stale-head check was performed because there is no write to protect; the pinned head (`36549bca3a...`) is what the payload is built and validated against throughout.
- Final rendered payload: [`/tmp/qual137/reports/l/l-867cf3ff-seed1-att-14-payload.md`](l-867cf3ff-seed1-att-14-payload.md) — the summary body and the one finding comment, exactly as `--emit-batch` would have submitted them, plus a one-line preamble noting the posting identity and non-publication.

## 11. Mechanism checklist

| Mechanism | Fired? | Where demonstrated |
| - | - | - |
| Question channel | **Did not fire.** | No candidate met the rubric's static-unresolvability bar (`review-rubric.md`'s "Ask only when... no static evidence could settle the fact"). The one must-fix candidate was fully resolved by reading code and running a Node reproduction; nothing remained an open, statically-unanswerable fact. |
| Clean-verdict / related-acquittal verification | **Clean-verdict: did not fire** (not zero-survivor — one candidate survived). **Related-acquittal: did not fire.** | §1 and §8: the only non-survivor row (`bokehjs/date-picker-mutates-parameter`) has `kind=maintainability`, outside the four qualifying kinds (`bug`/`concurrency`/`invariant`/`security`) SKILL.md's related-acquittal rule requires, so it was never included in the verifier batch. No re-open occurred either mode. |
| Observations | **Fired.** | §7 / payload: one observation published (the parameter-mutation hazard), under the 3-item cap, with the required single-sentence + `Evidence:` pointer form and no `should`/`must` language — confirmed by `validate_review.py`'s exit-0 pass, which enforces that form. |
| Fix-sufficiency check on a concurrency/invariant candidate | **Did not fire.** | The one survivor is `kind=bug`, not `concurrency`/`invariant`, so `verifier.md`'s five-step bug-class interleaving checklist (state-the-invariant-at-rule-level, steady-state check, sibling interleavings, sibling code paths, widen `change` to rule level) does not apply. The verifier explicitly noted this in its report ("the extra bug-class interleaving checklist in verifier.md does not apply — only concurrency/invariant candidates get that"). |
| Follow-up verifier round | **Did not fire.** | No candidate newly reached render eligibility after the initial batch (the initial batch's single candidate was `confirmed` with no corrections), and no clean-verdict/related-acquittal re-open occurred, so the "at most one fresh follow-up batch" provision was never invoked. |
| Deferral handling | **No explicit deferral found in the review record that bears on this finding.** bryevdv's comment "Perhaps there might even be a way we could futz with the time zone on the test system to run things a few times in different time zones?" (packet §6, non-review comment 5) is a suggestion, not a design/naming/API-shape deferral of the kind SKILL.md step 1 defines ("we can fix this during the API review", "let's revisit the name later"); it was never accepted or committed to, and no test covering multiple timezones was ultimately added. I treated it as context explaining *why* the added test doesn't cover the regression I found, not as an open deferred question requiring its own `Question` item — my own investigation already settled the underlying question (the code does regress for UTC-negative timezones), so nothing was left statically unresolvable for a reader to answer. |
| Retrospective mode | **Fired, throughout.** | Packet's pinned `merged: true` (§1 of the packet) triggered SKILL.md step 1's "A merged pull request is reviewable only when invoked as a retrospective or audit review; disable publication..." rule. The rendered summary carries the mandatory `**Mode:** Retrospective review of merged pull request; publication disabled.` line (payload file, summary body). No write was attempted anywhere in this run. |
| Early dispatch of the verifier batch (before falsification) | **This skill defines no such mechanism**, so nothing to fire early. SKILL.md's only sequencing is: falsify/deduplicate every candidate first (step 3, "Falsify and deduplicate every candidate under the rubric in the primary context... Only survivors are eligible for verification"), *then* "read `references/verifier.md` when verification is required... run one initial candidate batch." I dispatched the verifier (§9) only after the complete candidate ledger (§8) was falsified and written to this report, consistent with that ordering and with the cell's rule 6 ("Persist before you verify"). |

## 12. History discipline

I read **no history beyond the pinned head**. The only history-flavored commands run were:

- `git log --oneline -5 review-head` in the clone — shows the 5 commits already listed verbatim in the packet §5 table (`36549bca3` down to `472e4770d`), all reachable from and at-or-before the pinned head. Run only to confirm the clone's checked-out state, not to discover new information.
- `git branch -a` and `git status` — confirm branch layout (`master`, `review-head` checked out, `remotes/origin/HEAD`, `remotes/origin/master`, `remotes/origin/review-head`) and a clean working tree. No mutation.
- `review_context.py`'s own `history` section (part of the one context-command run, §5 item 1) printed 3 pre-merge-base commits that last touched `bokehjs/src/lib/models/widgets/date_picker.ts` (`e8b22ef16`, `475828e23`, `aa8f3028e`) — this is the tool's own bounded "history" output for the changed file, generated by the permitted helper script itself, not a manual `git log` I ran past the pinned head. I did not `git show` or otherwise inspect the content of any of those three commits, since no candidate's falsification needed them (the merge-base tree itself, via `git show master:<path>` implicit in the `diff`'s `-` side, was sufficient to establish "introduced here").
- I instructed the verifier sub-agent under the same constraint (rule 3 in its prompt) and it reported using only `git show <ref>:<path>` reads at the merge-base and head — no `git log` beyond that, and no attempt to reach past the pinned head.

Nothing reachable beyond `36549bca3a63d581f7b68d08054a7813c1e6a499` was read, by me or by the sub-agent.

## 13. Sandbox disclosure

No path outside the permitted sandbox (the clone, the skill snapshot, the packet directory, and my own work/report/payload/timing paths) was read. One incidental note: `ls /tmp/qual137/reports/l/` (run once, to confirm the reports directory existed and to see what I needed to create) listed filenames belonging to a different attempt on this same target, `l-bea6be14-seed1-att-13-*` — a different `snapshot`/config hash than mine (`bea6be14` vs. my `867cf3ff`). I did not open, read, or otherwise use the contents of any of those files; I only observed their names while listing the shared output directory I was told to write into. No other run's clone, report, or payload was read.

## 14. Notes — judgment calls on ambiguities in the skill's contract

1. **PR title/body given only as a truncated ellipsis in the packet.** The pinned run-identity table gives the PR title as `Fixed issue of Datepicker displaying the wrong date for users in UTC+…` and the body (packet §3) literally begins `… timezones.`. I could not re-fetch the untruncated text (offline, no network, and the packet explicitly says "do not attempt to re-resolve the target over the network"). I treated the packet's text as the authoritative pinned input verbatim, ellipsis included, for the `context` digest computation, rather than reconstructing a guessed full title (e.g. by borrowing the exact wording from commit 1's message, `"Fixed issue of Datepicker displaying the wrong date for users in UTC+ timezones."`, which is *plausibly* the untruncated title but is not what the packet actually pinned). This is a defensible reading of "use its pinned values verbatim; do not re-resolve anything" — I did not treat the commit message as a substitute for the pinned PR title/body.
2. **Issue-comment `id` field for the digest.** `context_fingerprint.py` requires a non-negative integer `id` per comment, but the packet gives comments only as a `1.`–`18.` enumeration, not forge-native comment IDs (unavailable offline). I used the enumeration position as the integer id. This affects only the exact digest value, not any admission/priority/routing decision in the review itself — the digest's purpose (detecting whether a later run's inputs match this one) is unaffected by this substitution as long as it's applied consistently, which it is within this single run.
3. **`.github/PULL_REQUEST_TEMPLATE.md` classification.** Treated as present-but-not-`guidance`, per `output-contract.md`'s exhaustive three-category `guidance` definition (root/path-scoped `AGENTS.md`/`CLAUDE.md`, root `CONTEXT.md`). I read it anyway (§5 item 12) to confirm it was the ordinary issue/PR-process checklist and not, for example, a repo convention document mislabeled by its filename — it was exactly the ordinary template, so this required no `Ambiguities` entry in the summary (the classification is unambiguous once the file's content is checked against the exhaustive rule).
4. **Whether the parameter-mutation fact belongs in `Observations` or should be dropped entirely.** I read `review-rubric.md`'s Observations section as requiring the fact to at least plausibly pass gate 1 (meaningful impact) while failing specifically on gate 4 (proven consequence) — as opposed to failing gate 1 outright, which would mean dropping it with no `Observations` mention at all (as I did for the comment-style nit). Mutating a caller-supplied object is a generally-recognized hazard (meaningful in the abstract) with a concretely, decisively *disprovable* current consequence (only 3 call sites, all verified fresh), which is exactly the "observation (consequence absent)" case the rubric names by that label. I did not route it as a full finding because gate 4 (proven consequence) is unambiguously unmet today, and I did not drop it silently because it is an accurate, evidence-backed fact about the changed code that a maintainer extending this function later would want on record.
5. **Priority calibration for the survivor (P1 vs. P0).** I read `review-rubric.md`'s P0 ("universal release blocker or critical failure") as requiring the defect to be effectively universal, not merely broad. The regression affects every UTC-negative timezone but leaves UTC-positive and UTC-zero timezones unaffected (in fact improved), so I classified it P1 ("urgent defect with serious or broadly affecting consequences") rather than P0. The verifier's report did not challenge this calibration when asked to correct `priority`/`action` if warranted.
6. **No `Ambiguities` summary section was published.** None of the above judgment calls are "a rubric or contract term [with] two genuinely supportable readings" in the sense SKILL.md step 3 uses the phrase (that mechanism is for admission/verification/status semantics, not for reconstructing missing forge metadata under an offline constraint) — so I recorded them here in the research report rather than as a payload `Ambiguities` entry, consistent with `output-contract.md`'s summary-body guidance to "not narrate other dropped candidates" or add content the contract doesn't call for.
