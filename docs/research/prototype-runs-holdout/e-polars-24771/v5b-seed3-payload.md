**Changes Requested (advisory)** — 1 must-fix finding, 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Speed up `Duration`/interval string parsing by switching to raw-byte, single-pass parsing (2–5x faster) for both Polars duration strings and SQL `INTERVAL` strings, without changing accepted syntax.

**Issue fit:** No linked issue (`issues=none`); judged against the PR's own stated intent. The byte-level, single-pass rewrite is met; one unstated syntax widening is noted below (Finding 2).

**Coverage:** Complete merge-base diff reviewed (3 files, full function-context ranges); every non-test caller of `Duration::parse`/`try_parse`/`parse_interval`/`try_parse_interval` traced across the repository (batched whole-repo grep); static review only, no execution (offline clone, no network, per run conditions).

**Reviewed:** `2db2ee17d` against merge-base `b3241e0d5`.

## Findings

- [P2] [must-fix] Bound the digit-accumulation loop against i64 overflow — anchor [`crates/polars-time/src/windows/duration.rs:238-243`](https://github.com/pola-rs/polars/blob/2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f/crates/polars-time/src/windows/duration.rs?plain=1#L238-L243)
- [P3] [consider] Reject any leading sign in interval-mode parsing — anchor [`crates/polars-time/src/windows/duration.rs:184-194`](https://github.com/pola-rs/polars/blob/2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f/crates/polars-time/src/windows/duration.rs?plain=1#L184-L194)

## Observations

- The diff bundles an unrelated docstring change for `pl.row_index()` (a `versionadded` directive and a reordered `warning` block) into an otherwise Duration-parsing performance PR. Evidence: `py-polars/src/polars/functions/lazy.py:2677`.

<!-- review-run head=2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f base-ref=main base-sha=b3241e0d50b5e9196fa0b070811e3d043157c5ba merge-base=b3241e0d50b5e9196fa0b070811e3d043157c5ba workflow=v5b-1 context=8a3fdbf4182fd48ccc3ec93bc9482efa8acf756a2be726e682e310d456478186 issues=none coverage=complete -->

---

## Inline comments

### `crates/polars-time/src/windows/duration.rs:238-243` (RIGHT)

**[P2] [must-fix] Bound the digit-accumulation loop against i64 overflow**

**Triggers when:** A duration or interval string's leading numeral has enough digits to exceed `i64::MAX` (e.g. `"9999999999999999999d"`, 19 nines), reaching `Duration::try_parse`/`parse`/`try_parse_interval`/`parse_interval` from any public call site — `group_by_dynamic`'s `every`/`period`/`offset`, `rolling_*`'s `window_size`, `date_range`'s `interval`, `join_asof`'s `tolerance`, `dt.offset_by`, or a SQL `INTERVAL` literal.

**Impact:** The rewritten digit loop (`n = n * 10 + (s[pos] - b'0') as i64`) has no bound and no checked arithmetic. In a release build (this repository does not set `overflow-checks` for `[profile.release]`, so it defaults to `false`), the multiplication silently wraps and `_parse` returns `Ok(Duration{..})` with a garbage value instead of an error — a wrong window/offset/tolerance/range with no signal to the caller. In a dev/test build (Cargo's implicit `overflow-checks=true` default, unmodified in this repo), the same input panics with a raw "attempt to multiply with overflow" instead of the merge-base's clean `InvalidOperation` error.

**Change:** In `crates/polars-time/src/windows/duration.rs`, bound the digit-accumulation loop (reject once the value would exceed `i64::MAX`) or restore checked parsing such as `s[digit_start..pos].parse::<i64>()`/`checked_mul`+`checked_add`, so an oversized numeral in a duration or interval string returns a clean `InvalidOperation` error in every build profile.

<!-- finding id=polars-time/duration-parse-digit-overflow head=2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f priority=P2 action=must-fix blocking=true kind=bug -->

### `crates/polars-time/src/windows/duration.rs:184-194` (RIGHT)

**[P3] [consider] Reject any leading sign in interval-mode parsing**

**Triggers when:** A SQL `INTERVAL` literal begins with a `+` sign, e.g. `INTERVAL '+3 days'` — `interval_to_duration` only rejects a literal containing `-` (`crates/polars-sql/src/sql_expr.rs:1099-1100`), not `+`, before calling `Duration::parse_interval`.

**Impact:** The leading-sign consumption at `duration.rs:184-194` runs unconditionally regardless of `as_interval`, so the merge-base's guarantee — reject any `+`/`-` at all in interval mode, front or not (base `duration.rs:179-195`) — is silently dropped for a lone leading sign. `INTERVAL '+3 days'` now parses as a positive 3-day interval instead of raising `InvalidOperation: "plus signs are not currently supported in interval strings"`; that error string (`duration.rs:212`) is now dead for this path, since it fires only on a second sign.

**Change:** Gate the leading-sign consumption on `!as_interval`, or explicitly validate and reject a leading sign when `as_interval` is true, restoring the merge-base's "no sign notation at all in interval mode" guarantee — or, if accepting a leading `+` is intentional, update the now-stale error text and add a test alongside the existing `-`-rejection test in `py-polars/tests/unit/sql/test_literals.py`.

Closing this without action is a correct response.

<!-- finding id=polars-time/duration-parse-interval-leading-sign head=2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f priority=P3 action=consider blocking=false kind=bug -->
