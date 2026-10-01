**Changes Requested (advisory)** — 2 must-fix findings, 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Speed up `Duration::parse`/`parse_interval` (Polars duration strings and SQL `INTERVAL` strings) by parsing raw bytes in one pass instead of a UTF-8 pre-scan plus a second pass, while preserving existing parsing behavior and error handling.

**Issue fit:** No linked issue (`issues=none`); judged against the pull request's own stated goals — operate on raw bytes, do parsing and checks in a single pass, add explanatory comments — all three are met. The claimed 2-5x speedup is not independently re-verified; this review is entirely static.

**Coverage:** Complete merge-base diff reviewed for all three changed files. Risk-directed checks covered signed-integer overflow, interval-mode sign validation, non-ASCII error-message display, and every reachable public entry point into `Duration::_parse`.

**Reviewed:** `2db2ee1` against merge-base `b3241e0d`.

## Findings

- [P1] [must-fix] Reject a leading sign in interval-mode parsing instead of silently accepting it — anchor [`crates/polars-time/src/windows/duration.rs:184-194`](https://github.com/pola-rs/polars/blob/2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f/crates/polars-time/src/windows/duration.rs?plain=1#L184-L194)
- [P2] [must-fix] Guard the leading-integer accumulation against i64 overflow — anchor [`crates/polars-time/src/windows/duration.rs:239-243`](https://github.com/pola-rs/polars/blob/2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f/crates/polars-time/src/windows/duration.rs?plain=1#L239-L243)
- [P3] [consider] Decode the offending character correctly in the "expected leading integer" error message — anchor [`crates/polars-time/src/windows/duration.rs:232-235`](https://github.com/pola-rs/polars/blob/2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f/crates/polars-time/src/windows/duration.rs?plain=1#L232-L235)

## Observations

- This pull request's first commit also reorders the `row_index()` docstring in `py-polars/src/polars/functions/lazy.py`, unrelated to the described duration/interval parsing change. Evidence: `py-polars/src/polars/functions/lazy.py:2680`.

<!-- review-run head=2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f base-ref=main base-sha=b3241e0d50b5e9196fa0b070811e3d043157c5ba merge-base=b3241e0d50b5e9196fa0b070811e3d043157c5ba workflow=v5b-1 context=8a3fdbf4182fd48ccc3ec93bc9482efa8acf756a2be726e682e310d456478186 issues=none coverage=complete -->

---

## Finding comments

### 1. [P1] [must-fix] Reject a leading sign in interval-mode parsing instead of silently accepting it

Anchor: `crates/polars-time/src/windows/duration.rs:184-194` (RIGHT)

**[P1] [must-fix] Reject a leading sign in interval-mode parsing instead of silently accepting it**

**Triggers when:** An interval-mode duration string begins with `+` or `-`, such as `Duration::try_parse_interval("-3 days")`, or a SQL `INTERVAL` literal beginning with `+` (the SQL layer only guards against `-`).

**Impact:** The leading sign is silently consumed and the call succeeds instead of erroring; for `-`, the returned `Duration` carries `negative: true`, a materially different, wrong result with no error at all.

**Change:** In the leading-sign block, bail with `"{sign} signs are not currently supported in interval strings"` when `as_interval` is true and a leading `+`/`-` is found, instead of silently consuming it and continuing.

<!-- finding id=polars-time/duration-interval-sign-validation-bypass head=2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f priority=P1 action=must-fix blocking=true kind=bug -->

### 2. [P2] [must-fix] Guard the leading-integer accumulation against i64 overflow

Anchor: `crates/polars-time/src/windows/duration.rs:239-243` (RIGHT)

**[P2] [must-fix] Guard the leading-integer accumulation against i64 overflow**

**Triggers when:** A duration or interval string's leading integer has enough digits to overflow `i64`, such as `"99999999999999999999d"` (20 nines).

**Impact:** The unchecked `n = n * 10 + digit` accumulation panics in a debug/dev build (`overflow-checks` defaults to `true` there) or silently wraps to an incorrect, possibly negative `i64` in a release build (`overflow-checks` defaults to `false`), returning `Ok` with a wrong `Duration` and no error. Every public duration-string entry point (`offset_by`, `rolling_*`, `date_range`, `group_by_dynamic`, `join_asof`'s `tolerance`, SQL `INTERVAL`) passes an unbounded user string straight into this parser.

**Change:** Replace the unchecked accumulation with a checked form (`checked_mul`/`checked_add`, or slice-and-`parse::<i64>()` as before) that bails with `InvalidOperation` on overflow instead of panicking or wrapping.

<!-- finding id=polars-time/duration-integer-literal-overflow head=2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f priority=P2 action=must-fix blocking=true kind=bug -->

### 3. [P3] [consider] Decode the offending character correctly in the "expected leading integer" error message

Anchor: `crates/polars-time/src/windows/duration.rs:232-235` (RIGHT)

**[P3] [consider] Decode the offending character correctly in the "expected leading integer" error message**

**Triggers when:** A duration or interval string begins with a non-ASCII, non-digit, non-sign byte, such as a string starting with `"日"`.

**Impact:** The error message casts the raw leading byte to `char` (`ch as char`), which for a multi-byte UTF-8 lead byte displays the wrong character (e.g. `'æ'` instead of `'日'`) in the `InvalidOperation` message.

**Change:** Decode the byte position back to the actual `char` from the original string (or otherwise avoid a raw `u8 as char` cast) before formatting the "found '...'" message.

Closing this without action is a correct response.

<!-- finding id=polars-time/duration-parse-error-char-mojibake head=2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f priority=P3 action=consider blocking=false kind=bug -->
