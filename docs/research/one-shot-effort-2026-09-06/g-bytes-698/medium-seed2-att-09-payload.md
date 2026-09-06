**Approved (advisory)** — 0 findings, 0 open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Make `<BytesMut as Buf>::advance` reuse the buffer's full spare capacity, matching `clear()`, when the advanced count consumes the entire remaining length, instead of always going through `advance_unchecked`'s allocation-shrinking path.

**Issue fit:** No originating issue; alignment was judged against the pull-request title and body. Both extracted outcomes are met: the full-consume fast path reuses capacity exactly as promised, and the optimization was deliberately kept out of `advance_unchecked` (which `split_to`/`split_off` also call and which must actually move the position).

**Coverage:** Complete merge-base diff reviewed (1 file, `src/bytes_mut.rs`, +8/−0); function context, `set_len`, `advance_unchecked`, `reserve`/`reserve_inner`, and `clear`/`truncate` inspected for the `ptr`/`len`/`cap`/`vec_pos` invariant the change touches. Focused execution: `cargo test --test test_bytes advance` at the head — pass (7 passed, 0 failed); a scratch capacity-reuse probe at the head and at the merge-base confirms the described optimization (capacity retained 64→64 at head vs. 64→53 at the merge-base for an identical full-consume sequence).

**Reviewed:** `7052d24` against merge-base `ce09d7d3`.

<!-- review-run head=7052d2454a2370ab9583f63711df89f3bd7bec83 base-ref=master base-sha=ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401 merge-base=ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401 workflow=v5b-10 context=ea94526181af0db99933265225e9cb726540a9c0b839990daee177aff1f81e5e issues=none coverage=complete -->
