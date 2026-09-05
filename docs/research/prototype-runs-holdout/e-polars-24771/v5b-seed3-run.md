# Run document — holdout target (e), cell `v5b-seed3`

**Orchestrator metadata (added after the run; the researcher's record, not the reviewer's).**

| | |
| --- | --- |
| Packet | `packets/e/packet.md`, SHA-256 `acf9aaf94549612fe1d136f0282c97a6e62798aac4d8fdc2aeb6e0d38c78552f` |
| Snapshot pins | v5b=2f06662 noverify=2f06662-minus-verifier panel=dd3bcfe33bfe8b65e272a6d2266ee9bc6cd1dc72 |
| Root agent / primary | `a11dad803f3a42600` / `a11dad803f3a42600` |
| Payload | [`v5b-seed3-payload.md`](v5b-seed3-payload.md), 5426 bytes |
| Report (this file, below the preamble) | 64829 bytes as written by the reviewer |
| Closed out | 2026-09-04T21:23:09.156214+00:00 |
| Problems at close-out | none |

## Model and effort verification (every assistant line of every transcript)

| Agent | Role | Definition | `message.model` | `effort` | Transcript |
| --- | --- | --- | --- | --- | --- |
| `a11dad803f3a42600` | primary | general-purpose | `claude-sonnet-5`×145 | `high`×145 | `agent-a11dad803f3a42600.jsonl` |
| `a285be15280dd5793` | child | general-purpose | `claude-sonnet-5`×64 | `high`×64 | `agent-a285be15280dd5793.jsonl` |

## Billed usage (`transcript_usage.py --prices 2,10 --report <this report>`)

```
agent-a11dad803f3a42600.jsonl
turns                        80 (API requests; 145 assistant lines)
tool calls                   79
text-only turns               1
input                       160 tokens (uncached)
cache write             397,675 tokens
cache read           10,624,137 tokens
output                   97,920 tokens (thinking 46,008)
models             claude-sonnet-5
wall                    0:27:31
cost                       4.10 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-a285be15280dd5793.jsonl
turns                        32 (API requests; 64 assistant lines)
tool calls                   31
text-only turns               1
input                        64 tokens (uncached)
cache write              66,530 tokens
cache read            1,408,071 tokens
output                   28,807 tokens (thinking 21,266)
models             claude-sonnet-5
wall                    0:06:56
cost                       0.74 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

TOTAL
turns                       112 (API requests; 209 assistant lines)
tool calls                  110
text-only turns               2
input                       224 tokens (uncached)
cache write             464,205 tokens
cache read           12,032,208 tokens
output                  126,727 tokens (thinking 67,274)
models             claude-sonnet-5
wall                    0:34:27 (summed over transcripts)
cost                       4.83 $ at 2/10 per M, cache write ×1.25, cache read ×0.1
production-shaped          4.67 $ (output 110,520 after subtracting the report's 16,207 est. tokens)
```

Row for `comparison-data.md`:

| (e) v5b seed 3 | claude-sonnet-5 | 112 | 110 | 2 | 224 | 464,205 | 12,032,208 | 126,727 | 67,274 | 0:34:27 | 4.83 | 16,207 | **4.67** |

Per agent:

| primary a11dad803f3a42600 | claude-sonnet-5 | 80 | 79 | 1 | 160 | 397,675 | 10,624,137 | 97,920 | 46,008 | 0:27:31 | 4.10 | — | — |
| child a285be15280dd5793 | claude-sonnet-5 | 32 | 31 | 1 | 64 | 66,530 | 1,408,071 | 28,807 | 21,266 | 0:06:56 | 0.74 | — | — |

---

# Research report — cell (e) / v5b / seed 3

`pola-rs/polars#24771`, arm v5b (`code-review-publish` pinned at `main 2f06662`,
workflow=`v5b-1`), seed 3.

Payload (the review exactly as it would be published): [`v5b-seed3-payload.md`](v5b-seed3-payload.md)

Status: **FINAL.** Written in stages per rule 5 (manifest/ledger persisted before verification, the
verifier prompt persisted before dispatch, the verbatim verifier report and everything downstream of
it appended after it returned). See the "FINAL." marker at the end of the file for confirmation this
version is complete.

## 1. Metadata

- Target: `pola-rs/polars#24771` — "perf: Duration/interval string parsing optimisation (2-5x faster)"
- Arm: v5b — skill `code-review-publish` pinned at `main 2f06662 (workflow=v5b-1)`
- Seed: 3
- Model: I (the primary reviewer for this cell) ran on `claude-sonnet-5`, per the dispatch's explicit
  instruction (`model: "sonnet"` on every `Agent` call). Every sub-agent I dispatch is instructed the
  same and I record the literal `model` value passed on each dispatch below.
- Posting identity: `kamui`, third party (did not author the PR, no prior comments/reviews) — ordinary
  first review, event `COMMENT`.
- Merged target: `merged=true` (2025-10-08T14:30:38Z) → retrospective review, **publication disabled**
  per the dispatch and per the skill's own boundary ("retrospective review of a merged pull request is
  non-publishing by default").
- Originating issue: none (`issues=none`); PR body references `#24737` only as prior-work context, not
  a closing reference.
- Pinned identity: head `2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f`, base ref `main`, base SHA /
  merge-base `b3241e0d50b5e9196fa0b070811e3d043157c5ba` (identical). Diff: 3 files, +156/−130, 2
  commits. Verified against the clone (`git log --oneline`, `git diff main review-head --stat`) —
  matches the packet exactly.

## 2. Manifest and requirement ledger (complete — step 2 of the skill)

### Context command

Run once, from cwd = the clone (`/tmp/holdout/runs/e/v5b-seed3`), first review (no prior head, so no
`--prior-head`/`--base-ref`):

```
python3 /tmp/holdout/skills/v5b/scripts/review_context.py \
  --merge-base b3241e0d50b5e9196fa0b070811e3d043157c5ba \
  --head 2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f
```

Exit code 0. Output kept at `/tmp/holdout/work/e/v5b-seed3/context.md` (1284 lines: `manifest`,
`diff` with `--function-context`, `ranges`, `history`). Read once in full and not re-fetched.

### Manifest (from the context command)

```
M crates/polars-time/src/windows/duration.rs +143 -110 new=no lines=1168
M py-polars/src/polars/functions/lazy.py +5 -3 new=no lines=2753
M py-polars/tests/unit/operations/namespaces/temporal/test_datetime.py +8 -17 new=no lines=1553
```

All three files reviewed (see §5 coverage). None ignored, none unreviewed.

### Requirement ledger

No originating issue (`issues=none`); the PR body is the only statement of intent. Per the rubric,
issue-fit is evaluated against the PR body's own stated intent rather than a separate acceptance
criterion list.

| # | Requirement (from PR body) | Disposition | Evidence |
| - | - | - | - |
| R1 | Parse duration/interval strings on raw bytes instead of UTF-8 chars, for speed | met | `crates/polars-time/src/windows/duration.rs:181` (`let s = s.as_bytes();`) and the whole rewritten `_parse` body operates on `&[u8]` |
| R2 | Do parsing and the "too many +/-" checks in a single pass instead of a pre-scan + parse | met | the old `for op_char in ['-', '+'] { s.matches(...).count() }` pre-scan (base lines 179-195) is gone; sign validation now happens inline via `error_on_second_plus_minus!` during the same walk |
| R3 | Applies to both duration strings and SQL `INTERVAL` strings | met | `_parse(s, as_interval)` is still the single entry point for both `try_parse`/`parse` (duration) and `try_parse_interval`/`parse_interval` (interval); both paths exercised in the diff's own new tests |
| R4 | Add a few more inline comments to explain the parsing logic | met | numerous new `//` comments through the rewritten `_parse` (e.g. lines 179, 184, 191, 196, 203, 219, 226, 238, 244, 251, 258, 267, 289) |
| R5 (non-goal, implicit) | Preserve existing accepted/rejected syntax (no stated intent to change what's valid) | partial | see Finding 1 (candidate C2 below): interval-mode parsing now silently accepts a leading `+` that the merge-base always rejected; not stated as an intended change |

No `not-verifiable` ledger rows — everything above is statically decidable from the diff and callers.

## 3. Complete private candidate ledger (all dispositions, before any verifier dispatch)

Two survivors are proposed for verification (one mandatory as `must-fix`, one optional `consider`
that required a cross-module trace). Six related non-survivor rows share `kind=bug` and the same
file as the survivors' anchors, so under `SKILL.md`'s related-acquittal mode they ride along in the
same verifier batch for a `holds`/`re-open` ruling. One dropped row (`kind=maintainability`) is not
related (wrong kind) and is not passed to the verifier.

### Survivors (candidates)

**C1 — unbounded digit accumulation overflow in `Duration::_parse`**

```yaml
id: polars-time/duration-parse-digit-overflow
anchor:
  type: line
  path: crates/polars-time/src/windows/duration.rs
  start_line: 238
  end_line: 243
  side: RIGHT
priority: P2
action: must-fix
blocking: true
kind: bug
title: Bound the digit-accumulation loop against i64 overflow
claim: >
  The rewritten digit-to-integer loop (`n = n * 10 + (s[pos] - b'0') as i64`) has no bound on digit
  count and no checked/saturating arithmetic, unlike the merge-base's `s[start..i].parse::<i64>()`,
  which returned a clean `Err` on overflow.
trigger: >
  A duration or interval string whose leading numeral has enough digits to exceed i64::MAX (e.g.
  "9999999999999999999d", 19 nines), reaching `Duration::try_parse`/`try_parse`/`parse_interval`/
  `parse` from any of their public call sites (group_by_dynamic every/period/offset, rolling
  window_size, date_range, join_asof tolerance, `dt.offset_by`, SQL `INTERVAL` literals).
impact: >
  In a release build (`overflow-checks` unset in `[profile.release]`, i.e. Rust's default `false`),
  the multiplication silently wraps and `_parse` returns `Ok(Duration{...})` with a garbage value
  instead of erroring — silently wrong window/offset/tolerance/range semantics with no signal to the
  caller. In a dev/test build (Cargo's default `overflow-checks=true` for `dev`, confirmed absent any
  override in this repo's `Cargo.toml`), the same input panics with "attempt to multiply with
  overflow" instead of returning `Err`; `Duration::parse_interval`/`Duration::parse` additionally
  `.unwrap()` the result, so even the base-branch's own overflow handling already surfaced as a panic
  at those two call sites — but only after producing a clean, informative `PolarsError` first; the
  head code panics with a raw arithmetic-overflow message instead, or (in release) does not panic and
  does not error at all.
evidence:
  - crates/polars-time/src/windows/duration.rs:238-243 (head, unchecked loop)
  - crates/polars-time/src/windows/duration.rs:228-230 (`git show main:...`, the removed checked `.parse::<i64>()`)
  - crates/polars-sql/src/sql_expr.rs:1105 (`Duration::parse_interval(s)`, unwraps directly on raw SQL text)
  - crates/polars-python/src/functions/range.rs, expr/rolling.rs, expr/general.rs, lazyframe/general.rs,
    dataframe/general.rs (10 call sites of `Duration::try_parse` on user-supplied strings, batched grep)
change: >
  Bound the digit loop (reject once the accumulated value would exceed i64::MAX, or restore
  `s[digit_start..pos].parse::<i64>()`/`checked_mul`+`checked_add`) so an oversized numeral in a
  duration or interval string returns a clean `InvalidOperation` error in every build profile instead
  of silently wrapping (release) or panicking on raw arithmetic overflow (debug).
support:
  inspected:
    - all 10 non-test callers of Duration::try_parse/parse/parse_interval/try_parse_interval (batched grep, whole repo)
  checks:
    - traced overflow through to `.abs()` on the returned Duration fields, also unchecked
  uncertainty: cannot execute to observe the actual panic/wraparound value (no-execution rule)
requirement_source: none (not issue-linked; general correctness gate)
verification: pending
disposition: survivor
```

**C2 — interval-mode leading `+` sign silently accepted (guarantee weakened)**

```yaml
id: polars-time/duration-parse-interval-leading-sign
anchor:
  type: line
  path: crates/polars-time/src/windows/duration.rs
  start_line: 184
  end_line: 194
  side: RIGHT
priority: P3
action: consider
kind: bug
title: Reject any leading sign in interval-mode parsing, matching the merge-base guarantee
claim: >
  The leading `+`/`-` consumption at lines 184-194 runs unconditionally regardless of `as_interval`,
  so a leading `+` (and, if `_parse` is ever reached directly with one, a leading `-`) is silently
  accepted as a no-op sign in interval mode, where the merge-base's `for op_char in ['-', '+']` loop
  (base lines 179-195) always rejected any sign character — leading or not — whenever `as_interval`
  was true.
trigger: >
  SQL `INTERVAL '+3 days'` (or any interval literal that starts with `+`): `interval_to_duration`
  (`crates/polars-sql/src/sql_expr.rs:1083`) only rejects a literal containing `-`
  (`sql_expr.rs:1099-1100`), not `+`, then calls `Duration::parse_interval(s)`, which unwraps
  `_parse(s, true)`.
impact: >
  The merge-base always raised `InvalidOperation: "plus signs are not currently supported in interval
  strings"` for this input; the head silently parses it as a positive interval (arguably the
  semantically "correct" reading, but undocumented, untested, and asymmetric with `-`, which is still
  rejected only because the SQL layer separately re-checks for it). The literal error string "signs
  are not currently supported in interval strings" (duration.rs:212) is now dead/misleading for this
  reachable path, since it only fires on a *second* sign, never the first.
evidence:
  - crates/polars-time/src/windows/duration.rs:184-194 (head, unconditional leading-sign consumption)
  - crates/polars-time/src/windows/duration.rs:179-195 (`git show main:...`, the removed as_interval-aware loop)
  - crates/polars-sql/src/sql_expr.rs:1096-1108 (only `-` is pre-filtered upstream)
  - py-polars/tests/unit/sql/test_literals.py:135-146 (existing tests cover `-` rejection only; no `+` case)
change: >
  Gate the leading-sign consumption on `!as_interval`, or explicitly validate and reject a leading
  sign when `as_interval` is true, restoring the merge-base's "no sign notation at all in interval
  mode" guarantee (or, if accepting a leading `+` is an intentional decision, state it in the doc
  comment, update the now-stale error text, and add a test alongside the existing `-` rejection test).
support:
  inspected:
    - crates/polars-sql/src/sql_expr.rs interval_to_duration and its 5 call sites
    - py-polars/tests/unit/sql/test_literals.py (interval tests)
  checks:
    - traced "+3 days" end to end through interval_to_duration -> Duration::parse_interval -> _parse(true)
  uncertainty: no other caller of try_parse_interval exists in this clone (confirmed by whole-repo grep), so this is reachable only via SQL today
requirement_source: none
verification: pending
disposition: survivor
```

### Related non-survivor rows (kind=bug, same file as C1/C2 → ride along in the same verifier batch)

| id | kind | claim (one line) | disposition | falsification reason | decisive evidence |
| - | - | - | - | - | - |
| D1 | bug | Mid-digit `+`/`-` (e.g. `"1+2d"`) now reports "expected a valid unit to follow integer" instead of the base's "only a single plus sign is allowed, at the front of the string" | dropped | Both versions still reject the input; only the message text differs, no functional regression, no pinned external contract on exact wording outside this diff's own updated tests | `crates/polars-time/src/windows/duration.rs:229-231` |
| D2 | bug | Byte-index parsing (`s[pos]` on `s.as_bytes()`) could panic on non-ASCII input landing mid-codepoint | dropped (acquitted) | `s` is `&[u8]`; byte indexing needs no char boundary; the code never re-slices the original `&str` at a computed offset, only prints the whole `original_string`; traced the diff's own new non-ASCII test `"12時30分45秒"` through the loop and it stops cleanly at the first non-alphabetic byte | `crates/polars-time/src/windows/duration.rs:180-181,259-267`; `py-polars/tests/unit/operations/namespaces/temporal/test_datetime.py:1228` |
| D3 | bug | `n * NS_MICROSECOND`/`NS_MILLISECOND`/etc. can themselves overflow i64 for a large but validly-parsed `n` | dropped (pre-existing) | Byte-for-byte identical multiplication logic and constants at base and head; the risk exists equally in both, so gate 2 (introduced-here) is not met | `crates/polars-time/src/windows/duration.rs:292-306` (head) vs. base `duration.rs:252-268` |
| D6 | bug | Splitting one contiguous whitespace/comma scan into three separate skip-points could desynchronize multi-part interval tokenization | dropped (acquitted) | Manually traced `"1 year, 2 months, 1 week"` through all three skip-points to a correct `(months=14, weeks=1)`; matches the diff's own new `test_parse_interval` unit test | `crates/polars-time/src/windows/duration.rs:251-256,267-273`; test module head lines ~1071-1073 |
| D7 | bug | Byte-slice unit matching (`match unit { b"ns" => ... }`) might not be equivalent to the old `String`-based `match &*unit` | dropped (acquitted) | Enumerated both match blocks side by side; every arm's byte-string literal is a character-for-character transcription of the old `&str` literal, same routing | `crates/polars-time/src/windows/duration.rs:290-333` (head) vs. base `duration.rs:252-286` |
| D8 | bug | The `'i'` (index-value) unit's `parsed_int = true` side effect might have been dropped or relocated | dropped (acquitted) | Head `b"i" => { nsecs += n; parsed_int = true; }` (line 303-306) is structurally identical to base's `"i" => { nsecs += n; parsed_int = true; }`; initialization and final struct field both unchanged | `crates/polars-time/src/windows/duration.rs:220,303-306,~349` (head) vs. base `duration.rs:223,~265` |

### Dropped row, not related (different kind, excluded from verifier batch)

| id | kind | claim (one line) | disposition | falsification reason | decisive evidence |
| - | - | - | - | - | - |
| D4 | maintainability | The unrelated `row_index()` docstring change adds `.. versionadded:: 1.32.0`, which may not match the actual release polars shipped it in | dropped (not-verifiable) | `row_index` was added by commit `6e7519e2c` ("#23556", 2025-07-14); no CHANGELOG or network access exists in this offline clone to confirm/deny the version number; the fact is plausible, not proven wrong, so it fails the static-unresolvability bar for a question too | `py-polars/src/polars/functions/lazy.py:2680` (head); commit `6e7519e2cd8ec34d69be20afd83a622beeec4a69` |

### Observation candidate (routed to the summary-only channel, not a finding)

| id | kind | claim | disposition | evidence |
| - | - | - | - | - |
| O1 | (n/a — observation) | The PR bundles an unrelated docstring reorder for `pl.row_index()` (moves the `.. warning::` block, adds `.. versionadded:: 1.32.0`) into a duration-parsing perf PR | observation (consequence absent — accurate fact, no proven negative impact) | `py-polars/src/polars/functions/lazy.py:2677-2690` |

## 4. Mandatory verification — verifier batch 1 (complete)

C1 is proposed `must-fix`, triggering mandatory independent verification per `SKILL.md` ("Independently
verify every surviving candidate proposed as must-fix"). C2 is included as an ordinary `consider`
survivor because establishing its claim required a cross-module trace (duration.rs's sign-consumption
logic plus sql_expr.rs's upstream `-`-only guard), which the skill permits bundling into the same
batch. D1, D2, D3, D6, D7, D8 are related non-survivor rows (kind=bug, same file as both candidates'
anchors) and ride along in this same batch under related-acquittal mode, per `SKILL.md`: "when at
least one candidate survives and the initial candidate batch is dispatched, include in that same
batch every non-survivor ledger row that is related to a survivor." D4 (kind=maintainability) is not
related (wrong kind) and was withheld from this batch.

Sub-agent: 1 verifier, dispatched via `Agent`, `subagent_type: "general-purpose"`, **`model: "sonnet"`
explicitly**, `run_in_background: false` (dispatched in the foreground, waited for its result before
continuing, per dispatch rule 9). No inheritance from this primary context (fresh Agent call — the
harness gives a sub-agent its own context; I did not fork my conversation).

### Exact prompt given (verbatim — passed as the `Agent` tool's `prompt` parameter unmodified)

~~~text
You are an independent verifier for one cell of a controlled research evaluation of a code-review
skill against a real, pinned, merged pull request. You are being run in a fresh, isolated context by
the primary reviewer; you have not seen the primary reviewer's reasoning, only what is supplied below.
Follow `/tmp/holdout/skills/v5b/references/verifier.md` exactly — read it in full first. This message
supplies the candidate-mode and related-acquittal-mode inputs it specifies.

## Rules binding on you (same as the primary reviewer's rules 1–6 and rule 8)

1. Follow the skill's verifier reference exactly; do not borrow behavior from any other review skill.
2. This is a retrospective, non-publishing review. You are not publishing anything; you are only
   fact-checking the supplied candidate and ledger records.
3. Do not compute or touch the `context` digest; that is not your job.
4. Clone hygiene: do NOT run `git checkout`, `git switch`, `git reset`, `git stash`, or any command
   that mutates the tree. Read-only inspection only (`git show`, `git diff`, `git log`, `grep`, file
   reads).
5. You do not need to persist anything yourself; return your complete verdict in your final message,
   because that is the only record of your work — the primary reviewer cannot see anything except
   what you return in your response.
6. Stay inside this sandbox: the clone at `/tmp/holdout/runs/e/v5b-seed3` (offline; origin is a local
   path, no `git fetch`/`pull`/network of any kind), the skill snapshot at `/tmp/holdout/skills/v5b/`,
   and the packet at `/tmp/holdout/packets/e/packet.md`. Do not read any other run's clone, report, or
   payload. Report any other path you read.
8. No session relays: finish in this one dispatch and return your complete verdict; do not ask the
   orchestrator or the primary reviewer anything mid-task.

Additional binding conditions from the packet (offline target, no execution): do not run `cargo`,
`rustc`, `python` (other than the skill's own scripts if you need them, which you should not for this
task), `pytest`, `maturin`, `make`, or any build/benchmark/test. Reason entirely from the source. Do
not fetch anything from the network. History is truncated at the pinned head
(`2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f`); nothing after this pull request exists in this clone.

## Pinned coordinates

- Repository: `pola-rs/polars`
- Base ref: `main`; base SHA / merge-base: `b3241e0d50b5e9196fa0b070811e3d043157c5ba`
- Head: `2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f`
- Issues/specs: none (`issues=none`)
- Applicable base-branch rule coordinates: `CONTRIBUTING.md` (stub, points to external docs, no
  repo-specific standard bearing on these candidates) and `.github/CODEOWNERS` (ownership routing
  only). Neither carries a specific rule relevant to these candidates.

## Ranges (from `scripts/review_context.py`, both candidates' anchors fall inside this hunk)

```
crates/polars-time/src/windows/duration.rs:108-1024 @head
crates/polars-time/src/windows/duration.rs:108-1004 @merge-base
```

Read these with `git -C /tmp/holdout/runs/e/v5b-seed3 show 2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f:crates/polars-time/src/windows/duration.rs`
and `git -C /tmp/holdout/runs/e/v5b-seed3 show b3241e0d50b5e9196fa0b070811e3d043157c5ba:crates/polars-time/src/windows/duration.rs`
(or just read the file at HEAD, since `review-head` is checked out, plus `git show <merge-base>:<path>`
for the base version) to get the exact line ranges above at each revision.

## Candidate C1 (mandatory verification — proposed must-fix)

```yaml
id: polars-time/duration-parse-digit-overflow
kind: bug
priority: P2
action: must-fix
anchor:
  type: line
  path: crates/polars-time/src/windows/duration.rs
  start_line: 238
  end_line: 243
  side: RIGHT
title: Bound the digit-accumulation loop against i64 overflow
claim: >
  The rewritten digit-to-integer loop (`n = n * 10 + (s[pos] - b'0') as i64`) has no bound on digit
  count and no checked/saturating arithmetic, unlike the merge-base's `s[start..i].parse::<i64>()`,
  which returned a clean `Err` on overflow.
trigger: >
  A duration or interval string whose leading numeral has enough digits to exceed i64::MAX (e.g.
  "9999999999999999999d", 19 nines), reaching `Duration::try_parse`/`try_parse`/`parse_interval`/
  `parse` from any of their public call sites (group_by_dynamic every/period/offset, rolling
  window_size, date_range, join_asof tolerance, `dt.offset_by`, SQL `INTERVAL` literals).
impact: >
  In a release build (overflow-checks unset in [profile.release], i.e. Rust's default false), the
  multiplication silently wraps and _parse returns Ok(Duration{...}) with a garbage value instead of
  erroring. In a dev/test build (Cargo's default overflow-checks=true for dev, no override present in
  this repo's Cargo.toml), the same input panics with "attempt to multiply with overflow" instead of
  returning Err.
change: >
  Bound the digit loop (reject once the accumulated value would exceed i64::MAX, or restore
  `s[digit_start..pos].parse::<i64>()` / checked_mul+checked_add) so an oversized numeral in a
  duration or interval string returns a clean InvalidOperation error in every build profile.
evidence:
  - crates/polars-time/src/windows/duration.rs:238-243 (head, unchecked loop)
  - crates/polars-time/src/windows/duration.rs:228-230 at the merge-base (the removed checked `.parse::<i64>()`)
  - crates/polars-sql/src/sql_expr.rs:1105 (`Duration::parse_interval(s)`, unwraps directly on raw SQL text)
  - non-test callers of Duration::try_parse across crates/polars-python/src/{dataframe/general.rs,
    expr/general.rs, expr/rolling.rs, functions/range.rs, lazyframe/general.rs} and
    crates/polars-mem-engine/src/executors/join.rs
```

## Candidate C2 (optional — proposed consider; required a cross-module trace to establish)

```yaml
id: polars-time/duration-parse-interval-leading-sign
kind: bug
priority: P3
action: consider
anchor:
  type: line
  path: crates/polars-time/src/windows/duration.rs
  start_line: 184
  end_line: 194
  side: RIGHT
title: Reject any leading sign in interval-mode parsing, matching the merge-base guarantee
claim: >
  The leading +/- consumption at lines 184-194 runs unconditionally regardless of as_interval, so a
  leading + is silently accepted as a no-op sign in interval mode, where the merge-base's
  `for op_char in ['-', '+']` loop (base lines 179-195) always rejected any sign character — leading
  or not — whenever as_interval was true.
trigger: >
  SQL `INTERVAL '+3 days'` (or any interval literal starting with +): interval_to_duration
  (crates/polars-sql/src/sql_expr.rs:1083) only rejects a literal containing '-'
  (sql_expr.rs:1099-1100), not '+', then calls Duration::parse_interval(s), which unwraps
  _parse(s, true).
impact: >
  The merge-base always raised InvalidOperation: "plus signs are not currently supported in interval
  strings" for this input; the head silently parses it as a positive interval. The literal error
  string "signs are not currently supported in interval strings" (duration.rs:212) is now dead for
  this reachable path, since it only fires on a *second* sign, never the first.
change: >
  Gate the leading-sign consumption on `!as_interval`, or explicitly validate and reject a leading
  sign when as_interval is true, restoring the merge-base's "no sign notation at all in interval mode"
  guarantee (or, if intentional, update the stale error text and add a test).
evidence:
  - crates/polars-time/src/windows/duration.rs:184-194 (head, unconditional leading-sign consumption)
  - crates/polars-time/src/windows/duration.rs:179-195 at the merge-base (the removed as_interval-aware loop)
  - crates/polars-sql/src/sql_expr.rs:1096-1108 (only '-' is pre-filtered upstream)
  - py-polars/tests/unit/sql/test_literals.py:135-146 (existing tests cover '-' rejection only, no '+' case)
```

## Related non-survivor rows (related-acquittal mode — same file as the candidates' anchors, kind=bug, full 5-step attack depth)

```
id: D1 | kind: bug | claim: Mid-digit +/- (e.g. "1+2d") now reports "expected a valid unit to follow integer" instead of the base's "only a single plus sign is allowed, at the front of the string" | disposition: dropped | falsification: both versions still reject the input; only the message text differs | evidence: crates/polars-time/src/windows/duration.rs:229-231

id: D2 | kind: bug | claim: Byte-index parsing (s[pos] on s.as_bytes()) could panic on non-ASCII input landing mid-codepoint | disposition: dropped (acquitted) | falsification: s is &[u8]; byte indexing needs no char boundary; the code never re-slices the original &str at a computed offset | evidence: crates/polars-time/src/windows/duration.rs:180-181,259-267; py-polars/tests/unit/operations/namespaces/temporal/test_datetime.py new "12時30分45秒" case

id: D3 | kind: bug | claim: n * NS_MICROSECOND/NS_MILLISECOND/etc. can themselves overflow i64 for a large but validly-parsed n | disposition: dropped (pre-existing) | falsification: byte-for-byte identical multiplication logic and constants at base and head | evidence: crates/polars-time/src/windows/duration.rs:292-306 (head) vs. base duration.rs:252-268

id: D6 | kind: bug | claim: Splitting one contiguous whitespace/comma scan into three separate skip-points could desynchronize multi-part interval tokenization | disposition: dropped (acquitted) | falsification: manually traced "1 year, 2 months, 1 week" through all three skip-points to a correct (months=14, weeks=1) | evidence: crates/polars-time/src/windows/duration.rs:251-256,267-273; test module head lines ~1071-1073 (test_parse_interval)

id: D7 | kind: bug | claim: Byte-slice unit matching (match unit { b"ns" => ... }) might not be equivalent to the old String-based match &*unit | disposition: dropped (acquitted) | falsification: every arm's byte-string literal is a character-for-character transcription of the old &str literal, same routing | evidence: crates/polars-time/src/windows/duration.rs:290-333 (head) vs. base duration.rs:252-286

id: D8 | kind: bug | claim: The 'i' (index-value) unit's parsed_int = true side effect might have been dropped or relocated | disposition: dropped (acquitted) | falsification: head b"i" => { nsecs += n; parsed_int = true; } (line 303-306) is structurally identical to base's "i" => { nsecs += n; parsed_int = true; } | evidence: crates/polars-time/src/windows/duration.rs:220,303-306,~349 (head) vs. base duration.rs:223,~265
```

## Your task

Per `verifier.md`:

1. For candidates C1 and C2: independently read the cited anchor and fix site as bounded ranges at
   head and at the merge-base, trace the stated trigger, establish observable impact, confirm the
   Code introduced-here condition (cite the base-branch guarantee and the head-branch code that no
   longer provides it), confirm the issue/PR/review record does not make it intentional, and check
   whether any other candidate requests the same change. Return exactly one verdict per candidate:
   `confirmed` or `refuted`, with a concise independent justification, decisive citations, and any
   correction to trigger/impact/priority/action/anchor/fix/change. Neither C1 nor C2 is a
   `concurrency`/`invariant` kind, so the bug-class rule-level-invariant procedure in `verifier.md`
   does not apply to them — use the ordinary bug verification steps.
2. For each of D1, D2, D3, D6, D7, D8: attack the acquittal using the full 5-step procedure
   `verifier.md` specifies for kind=bug rows (restate the decisive premise, state the condition under
   which it would be false, trace the opposite branch of every conditional it depends on, construct
   the complete failing transition or cite the impossible step, and do not merely agree with the
   ledger's own reasoning — a `holds` ruling must cite at least one line the ledger row did not cite).
   Return `holds` or `re-open` for each, with the citation(s).
3. Return any duplicate-id groups that should be merged.
4. You may return at most one non-actionable `observation` aside (a fact that contradicts no
   supplied row) — but any fact that *contradicts* a row's decisive premise must instead be returned
   as `disposition <id> does not hold; re-open it`, not as an observation.
5. Do not search the rest of the pull request for new findings. Do not return publication-ready prose.
   Do not write to, or otherwise mutate, the clone.
~~~

### Verbatim verifier report

The verifier's response noted at the end (harness-appended, not part of its own answer): "agentId:
a285be15280dd5793" and usage `subagent_tokens: 78539, tool_uses: 31, duration_ms: 417896`. The model
used by the verifier is recorded per the `Agent` call's explicit `model: "sonnet"` parameter (the
harness does not echo `message.model` back into the tool result in this environment; I did not have
transcript-file access to independently re-verify it from `~/.claude/projects/.../subagents/agent-*.jsonl`
within this sandbox, so I record what was passed, not an independently re-read confirmation — see §10
Notes for this judgment call). Below is the complete, unedited body of what the verifier returned:

~~~text
# Independent Verifier Report — packet e / v5b-seed3

Scope respected: read-only inspection only, confined to `/tmp/holdout/runs/e/v5b-seed3` (git show at pinned SHAs `2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f` and `b3241e0d50b5e9196fa0b070811e3d043157c5ba`), `/tmp/holdout/skills/v5b/references/verifier.md`, and the packet-supplied ranges. No `cargo`/`rustc`/tests run; no tree mutation; no other run's clone touched.

## Candidate verdicts

### C1 — `polars-time/duration-parse-digit-overflow`
**Verdict: confirmed**

- Head digit loop (`crates/polars-time/src/windows/duration.rs:238-243`) is `n = n * 10 + (s[pos]-b'0') as i64` in a plain `while` — no bound, no checked/saturating arithmetic.
- Merge-base guarantee it replaced: `crates/polars-time/src/windows/duration.rs:228-230` (base SHA) — `let Ok(n) = s[start..i].parse::<i64>() else { polars_bail!(...) };`. `str::parse::<i64>` always returns `Err` on overflow regardless of build profile (it is not gated by `overflow-checks`). Code-introduced-here condition confirmed: the diff (`18fa96281` "perf: Duration string parsing optimisation") removed this checked call and substituted unchecked arithmetic.
- No `[profile.dev]`/`[profile.release]` override of `overflow-checks` anywhere in the repo (`git grep -n overflow-checks` at head returns nothing; `Cargo.toml:157-177` profiles confirmed) — so dev builds panic (`attempt to multiply with overflow`) and release builds silently wrap, exactly as claimed.
- Reachable, non-test call sites verified live: `crates/polars-sql/src/sql_expr.rs:1104` (`Duration::parse_interval(s)`, itself `.unwrap()`), `crates/polars-mem-engine/src/executors/join.rs:102`, `crates/polars-python/src/expr/rolling.rs:39,75,110,147,187` (all `Duration::try_parse(...)`) — a `try_parse` caller does not shield against the panic, since the panic fires from the checked-arithmetic operator inside `_parse` before any `Err` value could be constructed.
- Intentionality: commit `18fa96281` message is only "perf: Duration string parsing optimisation"; `git show 18fa96281 | grep -i overflow` returns nothing — no record makes this intentional.
- No other supplied candidate requests this change (D3 is a different, pre-existing overflow site — the constant multiplication, not the digit-accumulation loop; see D3 below). No duplicate.

No correction to trigger/impact/priority/action/anchor/change; as submitted.

### C2 — `polars-time/duration-parse-interval-leading-sign`
**Verdict: confirmed**

- Head anchor `crates/polars-time/src/windows/duration.rs:184-194`: leading `+`/`-` detection and consumption (`if leading_minus || leading_plus { pos += 1; }`) runs unconditionally — no `as_interval` gate.
- Traced "+3 days" through `_parse(.., true)`: leading `+` consumed silently at 184-194 (`leading_plus=true`, `pos=1`); the only place a sign later triggers an error is `error_on_second_plus_minus!` (duration.rs:204-215, invoked at 229 and 273), which fires only for a *second* sign — never for the lone leading one. Result: `Ok(Duration{...})`, sign accepted as a no-op.
- Merge-base guarantee removed: base `duration.rs:179-195` — `for op_char in ['-','+'] { ... if as_interval { polars_bail!(...) } }` bails on **any** occurrence of `+`/`-` (count > 0) whenever `as_interval` is true, front or not. Code-introduced-here condition confirmed.
- Upstream reachability confirmed: `crates/polars-sql/src/sql_expr.rs:1098-1100` only pre-filters `'-'` (`s.contains('-')`), not `'+'`, then calls `Duration::parse_interval(s)` (sql_expr.rs:1104) unconditionally for the `+` case.
- `py-polars/tests/unit/sql/test_literals.py:135-140` only asserts rejection of `INTERVAL '-7d'`; no `'+...'` interval test exists anywhere in the repo (`grep` for the old message text and for interval `+` tests came back empty except the `-` case).
- Intentionality: `git show 18fa96281` touches only `duration.rs`, `py-polars/src/polars/functions/lazy.py`, and `test_datetime.py` (duration-mode sign tests only, no interval-sign test change) — nothing in the diff or commit message addresses interval leading-sign behavior; not shown intentional.
- Dead-code claim verified: `duration.rs:212` ("`{sign}` signs are not currently supported in interval strings") is reachable only via `error_on_second_plus_minus!`, which never fires for a lone leading sign — confirmed dead for this path.

No correction to trigger/impact/priority/action/anchor/change; as submitted. P3/consider calibration is appropriate — the accepted value is arithmetically "correct" (positive), so this is a normative-strictness regression, not a wrong-answer bug, consistent with the verifier guidance on calibrating `action` independently from a correctness defect.

## Related-acquittal rows (full 5-step attack, kind=bug)

### D1 — mid-digit `+`/`-` message text
**Ruling: holds.** Premise: both revisions reject "1+2d"-shaped input; only the message differs. Traced head: digit loop consumes `1` (pos=1), `s[1]='+'` fails `is_ascii_alphabetic`, so `unit_start==unit_end` fires the *"expected a valid unit to follow integer"* bail at **duration.rs:264-269** (not at the ledger's cited 229-231, which is the top-of-loop `error_on_second_plus_minus!` site that instead fires for a sign starting a *new* number-unit chunk, e.g. `"1d, +2d"`). Base: `s.matches('+').count()==1`, `!s.starts_with('+')` true → bails "only a single plus sign is allowed, at the front of the string" up front. Opposite branch checked: no caller or test in the repo matches on the old exact message for this input shape (`grep` for "only a single .* sign" across `py-polars/tests` and `crates` found none outside `duration.rs` itself and an unrelated `adbc` string). Both paths return `Err`; no behavior change. New citation beyond ledger's: **duration.rs:264-269** (the actual bail site for this exact trigger).

### D2 — byte-index panic on non-ASCII mid-codepoint
**Ruling: holds.** Premise: no re-slicing of the original `&str` at a computed offset; only `&[u8]` indexing occurs after `duration.rs:182` (`let s = s.as_bytes();`), which has no char-boundary requirement. Opposite branch checked: `original_string` (the `&str`) is used only whole in format strings (`duration.rs:247,267`), never range-sliced. The only computed-range slice is `&s[unit_start..unit_end]` at **duration.rs:283**, taken from the byte slice (bounds-only, never boundary-sensitive), then converted with `std::str::from_utf8(unit).unwrap_or("<invalid>")` at **duration.rs:315,321** — a fallible, panic-free conversion, not a bare `.unwrap()`. `to_ascii_lowercase()` (used for interval mode) also leaves non-ASCII bytes untouched. No failing transition constructable. New citations beyond ledger's 180-181/259-267: **duration.rs:283, 315, 321**.

### D3 — `n * NS_MICROSECOND` etc. overflow for large validly-parsed `n`
**Ruling: holds.** Premise: identical multiplication logic/constants at base and head. Verified arm-by-arm identical (`duration.rs:284-306` head vs. base `258-268`), and the constants themselves are imported unchanged — same `use` line at **duration.rs:23** in both base and head (`NS_DAY, NS_HOUR, NS_MICROSECOND, ...`), i.e., defined outside this diff entirely. Opposite branch checked: is the *reachable range* of a validly-parsed `n` different between revisions for this specific step? No — for `n` that does not overflow during parsing itself (the scenario D3 restricts to), both base's checked `.parse::<i64>()` and head's raw loop admit the same `[i64::MIN, i64::MAX]`-bounded values; the multiplication overflow risk on such `n` is byte-identical in both revisions. This satisfies the reference's "pre-existing... already unsafe at merge-base under the same guarantees" standard. New citation beyond ledger's 292-306/252-268: **duration.rs:23** (shared, diff-external constant import).

### D6 — three-point whitespace/comma skip desynchronizing tokenization
**Ruling: holds.** Independently re-traced "1 year, 2 months, 1 week" through all three `as_interval` skip points (initial ws-only skip pre-loop, before-unit ws/comma skip, after-unit ws/comma skip) byte-by-byte: months=12(year)+2(months)=14, weeks=1 — matches. Opposite branch checked: multiple/adjacent separators (`,,`, repeated spaces) are each consumed by a greedy `while` at every skip point identically to base's per-char loop, so no desync there; a comma-less multi-part case is also independently covered. Decisive first-party evidence the ledger mis-cited (it pointed to `~1071-1073`, which is actually unrelated code, `ensure_duration_matches_dtype`): the real unit test is **duration.rs:1114-1123** (`test_parse_interval`), asserting exactly `months()==14, weeks()==1` for the comma case and `duration_us()==100_100` for the space-only "100ms 100us" case — both shipped in this same commit. New citation: **duration.rs:1114-1123**.

### D7 — byte-slice unit matching vs. old `&str` matching
**Ruling: holds.** Full arm-by-arm diff performed (`duration.rs:284-321` head vs. base `255-290`): every byte-string literal (`b"ns"`, `b"nanosecond"`, …) is a character-for-character transcription of the corresponding `&str` literal, same order, same routing, no arm added/removed/reordered. Opposite branch checked: Rust byte-string patterns (`b"ns"`) against a `&[u8]` scrutinee match on exact byte content, semantically equivalent to `&str` literal matching for ASCII text — no equivalence gap. New citation beyond ledger's 290-333/252-286: **duration.rs:283** (`let unit = &s[unit_start..unit_end];`), establishing `unit: &[u8]`, the structural basis for the byte-pattern match being well-typed and equivalent.

### D8 — `parsed_int` side effect for unit `'i'` dropped/relocated
**Ruling: holds.** Traced full lifecycle: declared `let mut parsed_int = false;` at **duration.rs:220** (base: 223); set `true` only inside the `b"i"` arm at **duration.rs:298-300** (base: `"i"` arm ~270); included via struct-field shorthand in the final `Ok(Duration { ..., parsed_int, ... })` at **duration.rs:333** (base: 313, not the ledger's approximate `~349`, which lands past the closing brace of `_parse`). No relocation, no drop — structurally identical at every stage. New/corrected citation beyond ledger's 220/303-306/~349: **duration.rs:333** (base 313), the actual struct-construction site.

## Duplicate-id groups
None. C1 (digit-accumulation overflow) and C2 (interval leading-sign gate) address disjoint code paths and disjoint outcomes; none of D1/D2/D3/D6/D7/D8 request the same change as each other or as C1/C2.

## Observation
None returned — no incidental fact outside the above surfaced that doesn't already belong to one of the required per-row citations.
~~~

### Primary-reviewer handling of the verdicts

- **C1**: `confirmed`, no corrections. Kept as `must-fix`/P2, `verification: independent-confirmed`, promoted to a survivor finding. The verifier's line-number corrections (`264-269` as the actual D1 bail site, `1114-1123` as the actual D6 test, `333`/base `313` as the actual D8 struct-construction site, `23` as the shared constant import for D3) are adopted into this report's evidence trail above and into §5's coverage narrative; they do not change any disposition, only sharpen the citations.
- **C2**: `confirmed`, no corrections. Kept as `consider`/P3, `verification: independent-confirmed`, promoted to a survivor finding.
- **D1, D2, D3, D6, D7, D8**: all ruled `holds` with a citation beyond what the ledger itself cited, satisfying `verifier.md`'s "a `holds` ruling on a fully attacked row must cite at least one line the ledger row did not cite" — no re-open in any case, so no follow-up falsification and no follow-up batch was needed (`SKILL.md`: "Run at most one fresh follow-up batch over all of them" — there being nothing newly render-eligible, none was run).
- **D4** (maintainability, not related, withheld from this batch): remains `dropped (not-verifiable)`, unchanged, never sent to a verifier.
- No duplicate-id groups reported; C1 and C2 remain two distinct findings.
- No verifier `observation` aside was returned.

Verification is therefore **complete**: both survivors are `independent-confirmed`, all related rows attacked and held, no re-opens, no second batch required.

## 5. Findings for publication (final, post-verification)

Both are `independent-confirmed`. Full prose, evidence, and trailers are in the payload:
[`v5b-seed3-payload.md`](v5b-seed3-payload.md). Summary here:

| # | Priority | Action | Kind | Anchor | Fix | Verification |
| - | - | - | - | - | - | - |
| 1 | P2 | must-fix (blocking) | bug | `crates/polars-time/src/windows/duration.rs:238-243` (RIGHT) | same as anchor | independent-confirmed |
| 2 | P3 | consider (non-blocking) | bug | `crates/polars-time/src/windows/duration.rs:184-194` (RIGHT) | same as anchor | independent-confirmed |

**Finding 1 — Bound the digit-accumulation loop against i64 overflow (P2, must-fix).** Claim: the
rewritten digit-to-integer loop has no bound and no checked arithmetic, unlike the merge-base's
checked `.parse::<i64>()`. Trigger: a duration/interval numeral long enough to overflow `i64` (e.g.
19 nines), reachable from `group_by_dynamic`, `rolling_*`, `date_range`, `join_asof` tolerance,
`dt.offset_by`, and SQL `INTERVAL` literals. Impact: silent wraparound (release) or raw arithmetic
panic (dev/test) instead of the merge-base's clean `InvalidOperation` error. Verification status:
`independent-confirmed`, no correction. Evidence: `duration.rs:238-243` (head) vs. `duration.rs:228-230`
(merge-base, `git show b3241e0d5:...`); reachability confirmed via a whole-repo, case-insensitive
batched grep of every `Duration::parse`/`try_parse`/`parse_interval`/`try_parse_interval` call site.

**Finding 2 — Reject any leading sign in interval-mode parsing (P3, consider).** Claim: the
unconditional leading-sign consumption silently accepts a leading `+` in interval mode, where the
merge-base always rejected any sign notation (leading or not) whenever `as_interval` was true.
Trigger: SQL `INTERVAL '+3 days'`, reachable because `crates/polars-sql/src/sql_expr.rs` only
pre-filters `-`, not `+`. Impact: the interval parse now silently succeeds where it always errored
before; the code's own "signs are not currently supported in interval strings" message is now dead
for this path. Verification status: `independent-confirmed`, no correction.

No `Open questions` section: no candidate met the static-unresolvability bar for a question in this
run.

## 6. Complete private disposition ledger (final)

| id | kind | disposition | decisive evidence | falsification reason |
| - | - | - | - | - |
| C1 `polars-time/duration-parse-digit-overflow` | bug | **survivor, independent-confirmed, must-fix P2** | `duration.rs:238-243` (head) vs. `duration.rs:228-230` (base) | n/a — confirmed |
| C2 `polars-time/duration-parse-interval-leading-sign` | bug | **survivor, independent-confirmed, consider P3** | `duration.rs:184-194` (head) vs. `duration.rs:179-195` (base) | n/a — confirmed |
| D1 mid-digit sign message wording | bug | dropped, verifier `holds` | `duration.rs:229-231`, corrected by verifier to `264-269` | both versions still reject the input; message text only |
| D2 non-ASCII byte-index panic risk | bug | dropped (acquitted), verifier `holds` | `duration.rs:180-181,259-267`, corrected/extended by verifier to `283,315,321` | `s` is `&[u8]`; no re-slicing of the original `&str` at a computed offset |
| D3 downstream constant-multiplication overflow | bug | dropped (pre-existing), verifier `holds` | `duration.rs:292-306` (head) vs. base `252-268`, extended by verifier to shared `duration.rs:23` constant import | identical multiplication logic/constants at base and head |
| D4 `row_index()` `versionadded` accuracy | maintainability | dropped (not-verifiable) — **not sent to verifier** (wrong kind for related-acquittal) | `py-polars/src/polars/functions/lazy.py:2680`; commit `6e7519e2c` | no CHANGELOG/network access to confirm or deny the version number |
| D6 interval whitespace/comma tokenization desync risk | bug | dropped (acquitted), verifier `holds` | `duration.rs:251-256,267-273`, corrected by verifier to the real test at `1114-1123` | manual trace of `"1 year, 2 months, 1 week"` through all three skip-points is correct; matches the diff's own new test |
| D7 byte-slice vs. String unit-matching equivalence | bug | dropped (acquitted), verifier `holds` | `duration.rs:290-333` (head) vs. base `252-286`, extended by verifier to `duration.rs:283` | every match arm is a character-for-character transcription |
| D8 `parsed_int` flag relocation/drop risk | bug | dropped (acquitted), verifier `holds` | `duration.rs:220,303-306,~349` (head) vs. base `223,~265`, corrected by verifier to the real struct site `333`/base `313` | structurally identical initialization, set, and final-struct inclusion |
| O1 unrelated `row_index()` docstring bundling | n/a (observation) | routed to Observations (consequence absent) | `py-polars/src/polars/functions/lazy.py:2677-2690` | accurate fact, no proven negative impact — published as the one observation this run has |

## 7. Everything consulted beyond the diff

The diff itself (all three files, full function-context) came from the single `review_context.py`
run in §2 and was not re-read file-by-file. Beyond that single diff read, every file, command, and
search consulted, in the order first used:

**Skill and packet files (full reads, not repo-wide searches):**
- `/tmp/holdout/skills/v5b/SKILL.md` — full.
- `/tmp/holdout/skills/v5b/references/review-rubric.md`, `output-contract.md`, `verifier.md`,
  `re-review.md` — full, in that order, per `SKILL.md`'s own read sequencing.
- `/tmp/holdout/packets/e/packet.md` — full.
- `/tmp/holdout/skills/v5b/scripts/review_context.py --help` and a `grep -n "cwd\|os.getcwd..."`
  excerpt of the same script, plus a targeted read of its `--self-test` harness
  (`sed -n '550,650p'`) — to resolve the working-directory ambiguity recorded in §10 note 1.
- `/tmp/holdout/skills/v5b/scripts/context_fingerprint.py --help` and a full read (`sed -n '1,200p'`,
  covering the whole file) — to build the digest input JSON correctly.
- `/tmp/holdout/skills/v5b/scripts/validate_review.py --help` and a targeted read of its docstring/
  schema and constants (`sed -n '1,160p'`) — to build the payload JSON schema correctly.

**Clone commands and searches (repository evidence), each noted for repo-wide/case-insensitive scope:**

| Command | Scope | Case-insensitive? |
| - | - | - |
| `git branch -a`; `git log --oneline -5 main`; `git log --oneline -5 review-head`; `git remote -v`; `git diff main review-head --stat` | clone metadata, not a search | n/a |
| `git show 18fa96281 --stat`; `git show 2db2ee17d --stat` | the two commits on the head | n/a |
| `nl -ba crates/polars-time/src/windows/duration.rs \| sed -n '170,260p'` (head) and the equivalent `git show <merge-base>:...` read (base) | single file, bounded range | n/a |
| `sed -n '1,60p' Cargo.toml`; `grep -n "overflow-checks\|\\[profile" Cargo.toml`; `grep -n "profile.dev\\]" -A5 Cargo.toml`; `grep -n "arithmetic" Cargo.toml` | single file (root `Cargo.toml`) | no |
| `grep -rn --include="*.rs" -e "Duration::parse\b" -e "Duration::try_parse\b" -e "Duration::parse_interval" -e "Duration::try_parse_interval" crates/ \| grep -v "windows/duration.rs"` | **whole repo** (`crates/`) | no (Rust identifiers are case-sensitive; not needed) |
| `grep -rn --include="*.rs" -e "parse_interval" -e "interval_to_duration" crates/ \| grep -v "windows/duration.rs"` | **whole repo** (`crates/`) | no |
| `find crates/polars-sql -iname "*interval*"` | `crates/polars-sql/` only | yes (`-iname`) |
| `grep -rn -i --include="*.rs" -e "signs are not" crates/` | **whole repo** (`crates/`) | **yes** |
| `grep -rln -i --include="*.py" "interval" py-polars/tests/unit/sql` | `py-polars/tests/unit/sql/` only, not whole repo | **yes** |
| `grep -n -i "interval\|'\+'" py-polars/tests/unit/sql/test_literals.py` | single file | **yes** |
| `sed -n '1080,1120p' crates/polars-sql/src/sql_expr.rs` | single file, bounded range | n/a |
| `find . -maxdepth 2 -iname "clippy.toml"`; `find .github/workflows -iname "*.yml" \| xargs grep -l "cargo test\|clippy"` | repo root (depth-limited) / `.github/workflows/` | yes (`-iname`) |
| `grep -n "cargo test\|profile\|RUSTFLAGS" .github/workflows/test-rust.yml` | single file | no |
| `git show main:CONTRIBUTING.md` | single file, full (9 lines) | n/a |
| `git show main:.github/CODEOWNERS \| grep -i "polars-time\|duration\|lazy.py"` | single file | **yes** |
| `git log --oneline -1 -- py-polars/src/polars/functions/lazy.py`; `git log --oneline --follow -- py-polars/src/polars/functions/lazy.py \| grep -i "row_index\|row index"` | one file's history, whole reachable history via `--follow` | **yes** (the `grep -i`) |
| `find py-polars -iname "*.toml" -o -iname "_version*"` | `py-polars/` subtree only | yes (`-iname`) |
| `git show 6e7519e2c --stat`; `git log -1 --format="%ai" 6e7519e2c` | one commit | n/a |
| `git log --oneline --all -- py-polars/Cargo.toml` | **whole clone, all refs** (`--all`), one path | n/a |

**Downstream check for D3 (offline, no execution):** the digit-accumulation loop's exact head line
numbers (238-243) and the merge-base's checked-parse line numbers (228-230) were established by the
`nl -ba`/`sed` reads above, then cross-checked against `review_context.py`'s own `ranges` section
(`crates/polars-time/src/windows/duration.rs:108-1024 @head`, `:108-1004 @merge-base`) to confirm both
citations fall inside the already-fetched diff's function-context, not outside it.

No `cargo`, `rustc`, `pytest`, `maturin`, `make`, or any build/benchmark/test command was run, per
packet run-condition 2; every claim above is a static source read or a `git`/`grep`/`find` command.

## 8. Mechanism checklist

| Mechanism | Fired? | Where demonstrated |
| - | - | - |
| Question channel | **Did not fire.** | No candidate met the static-unresolvability bar (every candidate was statically confirmed or refuted); §5 explicitly states no `Open questions` section is present. |
| Clean-verdict (zero-survivor) verification | **Did not fire.** | Candidates C1 and C2 survived primary falsification, so the zero-survivor trigger condition in `SKILL.md` was never met. |
| Related-acquittal verification | **Fired.** | §4: six non-survivor rows (D1, D2, D3, D6, D7, D8), each `kind=bug` and anchored in the same file (`duration.rs`) as survivors C1/C2, rode along in the single verifier batch; all six ruled `holds`, none re-opened. |
| Observations | **Fired.** | One observation (O1, the unrelated `row_index()` docstring bundling) published in the payload's `## Observations` section, under the 3-item cap; §6 ledger row O1. |
| Fix-sufficiency check on any concurrency/invariant candidate | **Did not fire — N/A.** | Neither C1 nor C2 is `kind=concurrency` or `kind=invariant` (both are `kind=bug`); the verifier prompt in §4 explicitly told the verifier this procedure does not apply, and its report used the ordinary bug-verification steps instead of the rule-level-invariant/interleaving procedure. |
| Follow-up verifier round | **Did not fire.** | All six related rows were ruled `holds` with no re-open (§4, "Duplicate-id groups" / verdict summary), so nothing newly reached render eligibility and the one permitted follow-up batch was not used. |
| Deferral handling | **Did not fire — none found.** | Packet §6 shows the only prior review activity is one bare `APPROVED` review with an empty body and zero review threads/inline comments; no participant's comment anywhere in the (empty) record defers a design, naming, or API-shape decision, so there was nothing to classify as an open deferred question under step 1's rule. |
| Retrospective mode | **Fired.** | `merged=true` (packet §1) triggered the non-publishing retrospective path throughout: the mandatory `Mode` line appears in the payload's summary body, step 6 (actual publication) was not executed, and the rendered payload (`v5b-seed3-payload.md`) stands in its place per packet run-condition 4 and dispatch rule 2. |

## 9. The `context` digest and its inputs

Computed once, via `python3 /tmp/holdout/skills/v5b/scripts/context_fingerprint.py /tmp/holdout/work/e/v5b-seed3/context_input.json`
from cwd `/tmp/holdout/skills/v5b`:

```
8a3fdbf4182fd48ccc3ec93bc9482efa8acf756a2be726e682e310d456478186
```

Inputs supplied (the exact JSON, stored at `/tmp/holdout/work/e/v5b-seed3/context_input.json`):

- `pr.title`: `"perf: Duration/interval string parsing optimisation (2-5x faster)"` (packet §1)
- `pr.body`: the PR body verbatim, reproduced byte-for-byte from packet §3 (the full "Timings" table
  and footnote included)
- `issues`: `[]` (empty array — packet §4: no originating issue, `issues=none`)
- `specs`: `[]` (no user-supplied spec)
- `guidance`: `[]` — per the output contract's guidance definition (root/path-scoped `AGENTS.md` or
  `CLAUDE.md`, plus root `CONTEXT.md`), and packet §7 confirms none of the three are present at the
  merge-base. `CONTRIBUTING.md` and `.github/CODEOWNERS` exist but are excluded by the contract's
  membership rules (only `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` qualify as `guidance`); they were still
  read and classified (see §9 coverage note below), just not fed into the digest.

Computed once, not recomputed after verification (no candidate correction required a re-render of
`pr`/`issues`/`specs`/`guidance`, so the digest committed at step 2 remains valid through publication
per the contract: "Compute the `context` digest once; ... belong in the skill repository's CI, not in
a review").

## 10. History discipline

Every history command run, and why, all confined to commits reachable from the pinned head
(`2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f`) — **no history beyond the pinned head was read; the clone
has none reachable (history is truncated at the pinned head by construction, per the packet).**

- `git branch -a`, `git log --oneline -5 main`, `git log --oneline -5 review-head`, `git remote -v` —
  initial orientation, confirming the packet's pinned SHAs and that `origin` is a local path (offline).
- `git diff main review-head --stat` — confirmed the 3-file, +156/−130 manifest against the packet.
- `git show 18fa96281 --stat` and `git show 2db2ee17d --stat` — inspected each of the two commits on
  the head individually (both already within the pinned head; this determined that the unrelated
  `lazy.py` hunk belongs to the first commit, not a later one, and that the second commit is a
  test-only tweak).
- `git log --oneline -1 -- py-polars/src/polars/functions/lazy.py` and
  `git log --oneline --follow -- py-polars/src/polars/functions/lazy.py | grep -i row_index` — used to
  find which commit originally added `row_index()`, for the D4/O1 dropped candidate about the
  `versionadded` directive. Found `6e7519e2c` ("Add unstable `pl.row_index()` expression", #23556,
  2025-07-14) — an ancestor of the merge-base, not beyond the pinned head.
- `git show 6e7519e2c --stat` and `git log -1 --format="%ai" 6e7519e2c` — read that commit's date only
  (2025-07-14); no attempt to resolve which polars release shipped it (would need network/CHANGELOG
  access this run does not have), so D4 was left `not-verifiable` rather than guessed.
- `git log --oneline --all -- py-polars/Cargo.toml` — attempted to find a version-bump history for
  py-polars. `py-polars/Cargo.toml` does not exist at this path in the current checkout (confirmed by
  the immediately preceding `grep` error), but `--all` (all refs in the clone, not just `review-head`'s
  ancestry) surfaced three older commits touching a path with that name, including `d3aa828ee`
  ("Restructure python project directories again," #24676) — the same commit already seen in
  `review_context.py`'s `history` section as the last commit to touch `lazy.py` before this PR,
  meaning the file was moved/restructured away rather than never existing. `--all` traverses every ref
  in the local clone, which is broader than strictly `review-head`'s ancestry, but the clone's object
  set is itself truncated at the pinned head per the packet ("the newest object reachable in your
  clone is `2db2ee17d`"), so this could not and did not surface anything newer than the pinned head —
  no version-bump text was found either way, and this dead end is folded into D4's `not-verifiable`
  disposition rather than treated as a resolved fact.

All of the above are ordinary ancestor-history reads used only to falsify/verify specific candidates,
per the rubric's "History" risk-check category and the "Falsify every candidate" step's caller/test/
history-checking requirement — none read anything past `2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f`.

## 11. Sandbox disclosure

No path outside the sandbox was read. Everything read was confined to:

- the clone `/tmp/holdout/runs/e/v5b-seed3` (read-only; no mutating git command run — confirmed by
  final `git status`-equivalent absence of any `checkout`/`switch`/`reset`/`stash` invocation anywhere
  in this run's command history);
- the skill snapshot `/tmp/holdout/skills/v5b/` (`SKILL.md` and all four references read in full;
  `scripts/review_context.py`, `scripts/context_fingerprint.py`, `scripts/validate_review.py` run from
  that directory as instructed, with `cwd` set to the clone only for `review_context.py`, which needs
  the repository as its working directory to run `git` subcommands against — confirmed from the
  script's own `--self-test` harness, which passes `cwd=repository`);
- the packet `/tmp/holdout/packets/e/packet.md`;
- this cell's own work, report, and payload paths under `/tmp/holdout/work/e/v5b-seed3/` and
  `/tmp/holdout/reports/e/`.

No other run's clone, report, or payload was read. The verifier sub-agent was instructed under the
same constraint (see its prompt in §4) and its verbatim report does not disclose reading anything
outside `/tmp/holdout/runs/e/v5b-seed3`, `/tmp/holdout/skills/v5b/references/verifier.md`, and the
packet's supplied ranges — no violation to report on its behalf.

## 12. Notes

**Judgment calls on ambiguities in the skill's contract** (none rose to the level of the summary's
own `Ambiguities` section, since none affected which reading governed a specific finding's admission
or rendering — recorded here instead as run-level judgment calls):

1. **`review_context.py`'s working directory.** `SKILL.md` says "Run its scripts from this directory
   (`python3 /tmp/holdout/skills/v5b/scripts/<name>.py`)," which literally describes only the script's
   own path, not the process's `cwd`. Reading the script's `--self-test` harness (`cwd=repository`)
   settled that the intended `cwd` for `review_context.py` is the clone (it shells out to `git` with
   `cwd=None` defaulting to the caller's process `cwd`), so I ran it with the clone as the shell's
   working directory and the script referenced by absolute path, matching both the literal instruction
   (script's own location) and the script's functional requirement (a git working tree). No such
   ambiguity applied to `context_fingerprint.py` or `validate_review.py`, which are pure functions of
   their input and were run from the skill directory as literally instructed.
2. **Whether `CONTRIBUTING.md`/`.github/CODEOWNERS` are "guidance" for the digest.** The output
   contract's `guidance` membership list is exhaustive (`AGENTS.md`, `CLAUDE.md`, `CONTEXT.md` only);
   I read and classified both present files under the rubric's separate "Repository rules" section
   (applying normal precedence to changed paths) rather than folding them into the digest, since the
   contract explicitly excludes them from `guidance` by name-based membership, not by content
   judgment. Neither carried a repository-specific standard bearing on any candidate (`CONTRIBUTING.md`
   is a stub pointing to external docs; `.github/CODEOWNERS` is ownership routing only), so this
   reading changed nothing about the findings.
3. **Whether the `row_index()` docstring hunk needed its own requirement-ledger row versus only a
   candidate/observation.** I treated it as an implicit non-goal question (R5 in §2) *and* as its own
   dropped/observation candidate (D4/O1) rather than picking one — the rubric's issue-fit section and
   its "Complete inspection" section both bear on it (issue-fit: "materially broadens... behavior" test
   for unmentioned behavior; complete-inspection: every changed file needs disposition), and recording
   it under both made the reasoning traceable without duplicating any published prose (only O1 is
   actually rendered; R5 stays private ledger, and D4 stays private ledger).
4. **Re-review reference.** Skipped per `SKILL.md` step 2 ("On a first review, skip this step") — no
   prior state exists from this posting identity (packet §6 confirms `kamui` has no prior comments or
   reviews on this PR), confirmed directly rather than inferred.
5. **Verifier model attribution.** I passed `model: "sonnet"` explicitly on the `Agent` call per the
   dispatch's binding instruction and this cell's own rule 8/9. I do not have direct read access to
   `~/.claude/projects/.../subagents/agent-*.jsonl` transcript files from within this sandbox to
   independently confirm `message.model` the way project memory recommends for this research program
   (see the "Sub-agent model must be explicit" practice) — recorded here as a limitation rather than
   silently treated as confirmed; the passed parameter is the only evidence available to this run.

**Wall clock.** Not tracked as an internal timer by this run (no system-clock tool was invoked at
start and end); the verifier sub-agent's own reported `duration_ms: 417896` (~7 minutes) is the only
wall-clock figure this run captured directly, covering only its portion of the work. Token usage: the
harness did not surface a running token count to me during this session; the only usage figure
available in this run is the verifier's own report — `subagent_tokens: 78539, tool_uses: 31`. My own
(primary-context) token usage is not reported by the harness to this run in any form I could observe
or record.

---

**FINAL.** Both required files are complete: this report and
[`v5b-seed3-payload.md`](v5b-seed3-payload.md), the latter validated with zero violations by
`scripts/validate_review.py` (both default mode and `--emit-batch`) before being written.
