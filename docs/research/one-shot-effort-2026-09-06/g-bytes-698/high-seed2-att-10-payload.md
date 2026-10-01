**Approved (advisory)** — 0 must-fix findings, 0 open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Make `<BytesMut as Buf>::advance` automatically reuse the buffer's full existing capacity when `cnt` consumes everything remaining (equivalent to `clear()`), instead of always going through `advance_unchecked`'s position-shifting/promotion machinery.

**Issue fit:** No originating issue; alignment judged against the pull-request title and body, the only statement of intent. Both of its promises are met: `advance` now takes the `cnt == remaining()` fast path automatically (`src/bytes_mut.rs:1069-1073`), and the optimization was deliberately kept out of `advance_unchecked`, preserving `split_to`/`split_off`'s expectation that `advance_unchecked` always performs a real position shift, as the pull-request author and a maintainer agreed in the review discussion.

**Coverage:** Complete merge-base diff reviewed (1 file, `src/bytes_mut.rs`, +8/-0, single hunk). Inspected `set_len`, `advance_unchecked`, `capacity`, `truncate`/`clear`/`resize`, the vec-position bookkeeping (`get_vec_pos`/`set_vec_pos`), and the `Buf::advance` trait contract as bounded ranges around the changed hunk. No test function was added or changed by this diff, so the changed-tests check does not apply; CI results are unavailable offline. As additional focused verification permitted for this run, a scratch program exercising full-consume, partial-advance, zero-advance, over-advance-panics, and post-`split_to` scenarios was run once against the reviewed head and passed. One clean-verdict verifier batch attacked the complete disposition ledger and returned `clean verdict stands`.

**Reviewed:** `7052d24` against merge-base `ce09d7d`.

## Observations

- The new fast path in `advance()` duplicates the effect of the existing `clear()`/`truncate(0)` helpers, which already reset `len` to 0 under the same `set_len` safety contract. Evidence: `src/bytes_mut.rs:1069-1073`, `src/bytes_mut.rs:424-431`.

<!-- review-run head=7052d2454a2370ab9583f63711df89f3bd7bec83 base-ref=master base-sha=ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401 merge-base=ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401 workflow=v5b-10 context=ea94526181af0db99933265225e9cb726540a9c0b839990daee177aff1f81e5e issues=none coverage=complete -->
