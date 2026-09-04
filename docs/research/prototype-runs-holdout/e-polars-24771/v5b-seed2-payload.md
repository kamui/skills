# Rendered review payload — pola-rs/polars#24771 (arm v5b, seed 2)

Retrospective review of a merged pull request; publication disabled (binding run condition 4 / packet §1).
Would-be forge call: `POST repos/pola-rs/polars/pulls/24771/reviews`, `commit_id=2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f`, `event=COMMENT`.
Posting identity: `kamui` (third-party reviewer, did not author the pull request).

This file is the exact review as it would have been published: the summary body, followed by each finding's/question's inline comment with its trailer. Nothing else is included.

---

## Summary (review body)

**Changes Requested (advisory)** — 2 must-fix findings, 1 consider finding, 2 observations.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Speed up `Duration::parse`/`Duration::parse_interval` (backing Polars duration strings and SQL `INTERVAL` literals) by parsing raw bytes in a single pass instead of iterating `char`s and pre-scanning the string for sign characters.

**Issue fit:** Not applicable — no originating issue is linked from the pull request body and none was supplied; the pull request's own body is the only stated intent (a performance change with no explicit non-goal or acceptance criterion to check).

**Coverage:** Complete merge-base diff reviewed (`crates/polars-time/src/windows/duration.rs`, `py-polars/src/polars/functions/lazy.py`, `py-polars/tests/unit/operations/namespaces/temporal/test_datetime.py`); base-branch comparisons via `git show`; the SQL-layer caller (`crates/polars-sql/src/sql_expr.rs`) and the prior commit `bfa1cf81c` inspected for the interval-sign regression; both must-fix findings independently confirmed by a fresh verifier sub-agent.

**Reviewed:** `2db2ee1` against merge-base `b3241e0`.

## Findings

- [P1] [must-fix] Reject an integer literal that overflows i64 instead of wrapping it silently — anchor [`crates/polars-time/src/windows/duration.rs:239-243`](https://github.com/pola-rs/polars/blob/2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f/crates/polars-time/src/windows/duration.rs?plain=1#L239-L243)
- [P2] [must-fix] Reject a leading sign on an interval string instead of silently accepting it — anchor [`crates/polars-time/src/windows/duration.rs:184-193`](https://github.com/pola-rs/polars/blob/2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f/crates/polars-time/src/windows/duration.rs?plain=1#L184-L193)
- [P3] [consider] Decode the offending byte instead of casting it when reporting an invalid duration character — anchor [`crates/polars-time/src/windows/duration.rs:229-235`](https://github.com/pola-rs/polars/blob/2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f/crates/polars-time/src/windows/duration.rs?plain=1#L229-L235)

## Observations

- For a duration string with two or more `-`/`+` signs none of which are leading (e.g. `1d-2h-3m`), the error text now reads "only a single minus sign is allowed, at the front of the string" where the merge-base read "duration string can only have a single minus sign" (no "at the front" qualifier), though both correctly reject the input. Evidence: `crates/polars-time/src/windows/duration.rs:214`.
- The diff also reorders `row_index()`'s docstring in `py-polars/src/polars/functions/lazy.py` and adds a `versionadded` directive for `1.32.0`, unrelated to duration/interval parsing. Evidence: `py-polars/src/polars/functions/lazy.py:2683`.

<!-- review-run head=2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f base-ref=main base-sha=b3241e0d50b5e9196fa0b070811e3d043157c5ba merge-base=b3241e0d50b5e9196fa0b070811e3d043157c5ba workflow=v5b-1 context=8a3fdbf4182fd48ccc3ec93bc9482efa8acf756a2be726e682e310d456478186 issues=none coverage=complete -->

---

## Inline comments

### crates/polars-time/src/windows/duration.rs:239-243 (side RIGHT)

**[P1] [must-fix] Reject an integer literal that overflows i64 instead of wrapping it silently**

**Triggers when:** A duration or interval string whose leading integer run has more digits than fit in `i64` is parsed, e.g. `Duration::parse("99999999999999999999d")` (20 digits).

**Impact:** The digit-accumulation loop computes `n = n * 10 + digit` with no overflow check, unlike the checked `s[start..i].parse::<i64>()` call it replaces (still present at the merge-base, which cleanly rejects an overflowing literal). This workspace's `Cargo.toml` sets no `overflow-checks = true` on `[profile.release]`/`[profile.dist-release]`, so a release build wraps the value silently instead of erroring, producing an incorrect `nsecs`/`days`/`weeks`/`months`; a debug build panics instead of returning `Err`. `Duration::parse`/`try_parse` back many public entry points (rolling and `group_by_dynamic` windows, `duration_range`, join tolerances) with no other bound on the literal.

**Change:** In the digit-accumulation loop, use checked arithmetic (`checked_mul`/`checked_add`) or bound the digit count, and bail with the existing "expected leading integer" error on overflow, restoring the merge-base's rejection of an out-of-range literal.

<!-- finding id=polars-time/duration-parse-integer-overflow head=2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f priority=P1 action=must-fix blocking=true kind=bug -->

### crates/polars-time/src/windows/duration.rs:184-193 (side RIGHT)

**[P2] [must-fix] Reject a leading sign on an interval string instead of silently accepting it**

**Triggers when:** `Duration::try_parse_interval`/`parse_interval` is called with a string carrying a leading `+`/`-`, e.g. `"-1d"` or `"+1d"`; reachable in-tree via a SQL literal such as `INTERVAL '+7d'`, since `crates/polars-sql/src/sql_expr.rs`'s own guard only checks the string for `-`, never `+`.

**Impact:** The leading-sign detection unconditionally consumes the sign regardless of `as_interval`. `try_parse_interval("-1d")` now returns `Ok(Duration{negative:true,...})` instead of the merge-base's `Err("minus signs are not currently supported in interval strings")`; a leading `+` is silently dropped with no error at all. This regresses the sign-validation this same author generalized three days earlier in `bfa1cf81c` (#24737, referenced by this pull request's own body), whose enforcement and its explanatory TODO comment were both removed here with no equivalent added.

**Change:** When `as_interval` is true, bail with the existing "signs are not currently supported in interval strings" message immediately on detecting a leading sign, before consuming it.

<!-- finding id=polars-time/duration-parse-interval-leading-sign head=2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f priority=P2 action=must-fix blocking=true kind=bug -->

### crates/polars-time/src/windows/duration.rs:229-235 (side RIGHT)

**[P3] [consider] Decode the offending byte instead of casting it when reporting an invalid duration character**

**Triggers when:** The first non-digit, non-sign byte of a duration/interval string is part of a multi-byte UTF-8 character, e.g. `Duration::parse("é5d")`.

**Impact:** The "expected leading integer" error formats the offending byte with `ch as char`, a raw byte-to-`char` cast, so a non-ASCII lead byte renders as the wrong character (e.g. `é`'s first byte, `0xC3`, prints as `Ã`) instead of the character actually typed. This function's two sibling error messages avoid the problem: one formats the original `&str`, the other decodes with `std::str::from_utf8`.

**Change:** Format the offending character from the original `&str` (or via `std::str::from_utf8` on a bounded slice) instead of casting the raw byte, matching the pattern already used at this function's other two bail sites.

Closing this without action is a correct response.

<!-- finding id=polars-time/duration-parse-non-ascii-error-char head=2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f priority=P3 action=consider blocking=false kind=bug -->
