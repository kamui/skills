**Approved (advisory)** — no findings, no open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Reuse buffer capacity in `<BytesMut as Buf>::advance` by resetting the length to 0 instead of shifting the pointer through the allocation machinery, whenever the amount advanced equals the whole remaining length.

**Issue fit:** Issue alignment was unavailable — no closing or other explicit issue reference exists; the ledger was built from the pull-request title and body. Both promises (automatic capacity reuse on a full-length advance; keep the optimization out of `advance_unchecked` because `split_to`/`split_off` depend on it unconditionally shifting the pointer) are met, and the author's own stated uncertainty about `Buf`-trait compliance is settled: the trait's documented contract for `advance` (only that `chunk()` returns a slice `cnt` bytes further in, and that `cnt == 0` never panics) is satisfied.

**Coverage:** Complete merge-base diff reviewed (1 file, `src/bytes_mut.rs`, +8/−0, 1/1 diff chunks consumed). The diff adds or changes no test function, so the Changed Tests section did not apply and no execution was owed. Seven candidates were raised and independently falsified to zero survivors; because the change is unsafe pointer/length/capacity bookkeeping in the crate's core buffer type, a zero-survivor clean-verdict verification ran over the complete candidate ledger and returned `clean verdict stands`.

**Reviewed:** `7052d2454a2370ab9583f63711df89f3bd7bec83` against merge-base `ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401`.

<!-- review-run head=7052d2454a2370ab9583f63711df89f3bd7bec83 base-ref=master base-sha=ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401 merge-base=ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401 workflow=v5b-10 context=ea94526181af0db99933265225e9cb726540a9c0b839990daee177aff1f81e5e issues=none coverage=complete -->
