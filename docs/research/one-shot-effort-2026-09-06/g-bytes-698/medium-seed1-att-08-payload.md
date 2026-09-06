**Approved (advisory)** — 0 must-fix findings, 0 open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Make `BytesMut`'s `Buf::advance` reclaim its full capacity instead of shrinking it when `cnt` consumes the buffer's entire remaining length, avoiding the allocation-shifting cost of the general path.

**Issue fit:** No originating issue is linked; issue alignment was unavailable, so the ledger was built from the pull-request title and body. The promised optimization is met: `advance` now resets `len` to 0 in place, preserving `ptr`/`cap`, whenever `cnt == remaining()`.

**Coverage:** Complete merge-base diff reviewed (1 file, `src/bytes_mut.rs`, +8/-0); `split_off`/`split_to`/`advance_unchecked`/`reserve`/`try_unsplit` inspected as risk-led discovery around the changed length/capacity invariant; focused test `bytes_buf_mut_reuse_when_fully_consumed` run once at the head: pass.

**Reviewed:** `7052d24` against merge-base `ce09d7d`.

## Observations

- In a release build, no runtime check backs the new fast path's safety comment because `set_len`'s bound check is a `debug_assert!` rather than a release-mode `assert!`. Evidence: `src/bytes_mut.rs:519-520`.

<!-- review-run head=7052d2454a2370ab9583f63711df89f3bd7bec83 base-ref=master base-sha=ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401 merge-base=ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401 workflow=v5b-10 context=b19e2ac89ccb022d2cfda436d3aa59b37bc648825a8660eaf944299b36ebe99f issues=none coverage=complete -->
