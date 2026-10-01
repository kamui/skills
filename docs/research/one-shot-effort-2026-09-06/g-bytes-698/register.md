# Sealed defect register — target (g) tokio-rs/bytes#698 at 7052d245

## Material defects

### GT-g1 — `<BytesMut as Buf>::advance` stops shrinking `capacity()` when consuming the full remaining length
- Expected behavior: consuming bytes through `Buf::advance` reduces `BytesMut::capacity()` by the amount consumed, exactly as the sibling "consume" operation `split_to`/`split()` does. `BytesMut::reserve`'s own doc example and `BytesMut::split`'s doc example (`assert_eq!(buf.capacity(), 64)` after `split()`, i.e. after consuming via `split_to(len())`) establish this as the crate's own documented, load-bearing behavior of "consuming = shrinking capacity" for handles that view into a larger allocation.
- What the head does instead: in `impl Buf for BytesMut::advance` (src/bytes_mut.rs:1068-1085 at head 7052d245), a new fast path was inserted:
  ```
  1071:        if cnt == self.remaining() {
  1072:            // SAFETY: Zero is not greater than the capacity.
  1073:            unsafe { self.set_len(0) };
  1074:            return;
  1075:        }
  ```
  `set_len` (src/bytes_mut.rs:519-522) only sets `self.len`; it never touches `self.ptr` or `self.cap`. The normal path below it, `advance_unchecked` (src/bytes_mut.rs:872-905), moves `self.ptr` forward by `count` and does `self.cap -= count` (src/bytes_mut.rs:902-904). So whenever `cnt == remaining()` (the common "I consumed everything" case), `advance` now leaves `capacity()` completely unchanged instead of shrinking it to 0/`capacity() - cnt`. Any other `cnt < remaining()` still goes through the old, correct `advance_unchecked` path — only the full-consumption case is affected.
- Trigger: call `.advance(n)` on a `BytesMut` where `n == buf.remaining()` (including the common case of consuming everything then continuing to read/write the same handle), on any handle that has been carved out of a larger allocation via `split_to`/`split_off` (or any handle at all, since even a top-level `with_capacity` buffer exhibits `capacity()` no longer shrinking).
- Demonstrated consequence:
  - Downstream: issue tokio-rs/bytes#725 ("BytesMut::advance no longer advances cursor") reports that aws/s2n-quic's reassembler (`buffer::reassembler::slot::Slot`) and its `buffer::reader::Storage for BytesMut` impl rely on `advance` reducing `remaining`/`capacity` to maintain the invariant `self.data.capacity() == self.end_allocated() - self.start()` used to detect a full/bounded slot. Breaking that invariant caused aws/s2n-quic#2289, filed as "bytes 1.7.0 breaks s2n-quic" with reported effect "causes s2n-quic to hang"; the project's fix was to pin `bytes` to 1.6.1. bytes 1.7.0 (commit `03fdde9`, "chore: prepare v1.7.0 (#724)") is the release that shipped 7052d245's behavior.
  - My own reproduction: cloned tokio-rs/bytes at head `7052d2454a2370ab9583f63711df89f3bd7bec83`, added the verbatim regression test body from PR #728 (`advance_bytes_mut_remaining_capacity`, from commit `ed7d5ff39e39c2802c0fa9e2fc308f6a3e0beda7`) as `tests/test_issue728_regression.rs`, and ran:
    ```
    $ cargo test --test test_issue728_regression
    ```
    Result at head 7052d245 (0.00s test runtime once compiled, ~3.3s total incl. compile):
    ```
    testing capacity=0, len=0, advance=0
    testing capacity=1, len=0, advance=0
    testing capacity=1, len=1, advance=0
    testing capacity=1, len=1, advance=1
    thread 'advance_bytes_mut_remaining_capacity' panicked at tests/test_issue728_regression.rs:30:17:
    assertion `left == right` failed: Buf::advance should reduce the remaining capacity
      left: 1
     right: 0
    test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out
    ```
    (This exactly matches the failure quoted in PR #728's own description.) The failing case is `capacity=1, len=1, advance=1`: after `buf.advance(1)` on a length-1, capacity-1 buffer, `buf.capacity()` is `1` (unchanged) instead of the expected `0`.
  - Same test at the merge-base `ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401` (checked out in the same clone, test file re-added):
    ```
    $ cargo test --test test_issue728_regression
    test advance_bytes_mut_remaining_capacity ... ok
    test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.48s
    ```
- Evidence: diff `ce09d7d3..7052d245` (`git diff ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401 7052d2454a2370ab9583f63711df89f3bd7bec83 -- src/bytes_mut.rs`, 8 lines added, 0 removed, file `src/bytes_mut.rs`); tokio-rs/bytes#725; tokio-rs/bytes#726 (revert, merge `f488be48d07d899dc428c5cd7f5c11a95bf7716c`, body: "Too much code relies on this behavior. We can't change it."); tokio-rs/bytes#728 (regression test, merge `ed7d5ff39e39c2802c0fa9e2fc308f6a3e0beda7`); aws/s2n-quic#2289 (closed 2024-08-02, same day #726 opened); PR #698's own body ("I'm not sure the `Buf` API allows it") — the author flagged the uncertainty at review time and it was approved anyway (review by `braddunbar`, `Darksonn` commented only on code style, not semantics).
- Required corrective outcome (what a sufficient fix must restore): `BytesMut::advance(cnt)` must reduce `capacity()` by exactly `cnt` in all cases, matching `advance_unchecked`'s behavior and the observable contract exercised by `split()`/`split_to()`. Concretely, the fix must make the `advance_bytes_mut_remaining_capacity` test (PR #728) pass — i.e., simply revert the fast-path special case (as PR #726 did) or replace it with an implementation that still decrements both `len` and `cap` (e.g., moving `ptr` forward as `advance_unchecked` does, or an equivalent bookkeeping change) rather than leaving `cap` untouched.
- Partial fixes that would NOT be sufficient: keeping the `set_len(0)`-only fast path but only for `KIND_VEC` (or only for top-level, non-split buffers) — the s2n-quic reassembler slots and the regression test exercise plain `BytesMut::with_capacity` buffers (KIND_VEC) directly, so restricting by representation does not help. Likewise, only fixing `capacity()`'s *reported* value without actually reclaiming/shrinking the writable window would not satisfy the invariant `capacity() == end_allocated() - start()` that downstream code depends on; the fix must be behavioral, not cosmetic.

## Plausible non-defects (a finding asserting any of these is a false finding)
- "The `unsafe { self.set_len(0) }` call is a memory-safety violation (use-after-consumption, exposing uninitialized memory, or aliasing another live `BytesMut`/`Bytes`)." — False. `set_len` only asserts `len <= self.cap` (src/bytes_mut.rs:519), and `0 <= cap` always holds. The reused byte range `ptr..ptr+cap` was already exclusively owned by this handle both before and after the call (no other handle can observe or write to it — `split_to`/`split_off` partition capacity into disjoint, non-overlapping ranges by construction, and `freeze()` consumes `self` rather than aliasing it). The bytes exposed as "spare capacity" after `set_len(0)` were previously initialized data (whatever was read), not uninitialized memory, so `spare_capacity_mut`'s `MaybeUninit<u8>` contract is not violated either. This is a semantic/contract bug (GT-g1), not a soundness bug.
- "The fast path breaks `KIND_VEC`'s `vec_pos` tracking (used to rebuild the original `Vec` on drop) because it doesn't call `set_vec_pos`." — False. `vec_pos` tracks the offset of `self.ptr` from the start of the original allocation. The new fast path does not move `self.ptr` at all (unlike `advance_unchecked`, which updates `vec_pos` precisely because it *does* move `ptr`), so `vec_pos` and `ptr` remain mutually consistent; `Drop`'s `rebuild_vec(self.ptr.as_ptr(), self.len, self.cap, off)` (src/bytes_mut.rs:1044-1047) still reconstructs the correct `Vec`.
- "`advance(0)` on an already-empty/zero-capacity buffer panics or misbehaves under the new code." — False. When `remaining() == 0` and `cnt == 0`, the fast path's condition `cnt == self.remaining()` is true and `set_len(0)` is a pure no-op (`len` was already 0). Confirmed by the reproduction test's first several iterations (`capacity=0,len=0,advance=0` and `capacity=1,len=0,advance=0`) passing before the failure occurs at `capacity=1,len=1,advance=1`.
- "This interacts badly with `unsplit`, causing two adjacent `BytesMut` handles to silently merge incorrectly after an `advance`." — False. `try_unsplit`'s contiguity check (src/bytes_mut.rs:906-923) compares `other.ptr` against `self.ptr.add(self.len)`; since the fast path never changes `self.ptr`, and `self.len` becomes 0, this reduces to `other.ptr == self.ptr`, which is exactly the same condition that would hold under the pre-#698 behavior for a handle whose `len` had been driven to 0 by full consumption at that address. No new merge is enabled or missed by this change.

## Calibration
- Expected review status on a correct review: REQUEST_CHANGES (or equivalent "not mergeable as-is") at the time of #698 — but note this is a hindsight judgment given the change's own author flagged uncertainty ("I'm not sure the `Buf` API allows it") and no test was added to pin the documented capacity-shrinking behavior. A rigorous reviewer checking `BytesMut`'s own doc examples (`split()`'s `assert_eq!(buf.capacity(), 64)`, `reserve()`'s doc) against the new `advance` fast path could have caught the inconsistency pre-merge; that is the standard this register holds a review to, independent of the fact the real-world review approved it and it later had to be reverted (#726) and regression-tested (#728).
- Priority and action band for GT-g1: High / must-fix-before-release (in the historical record this was reverted within one release cycle as a behavior-breaking regression with a real downstream production incident — "causes s2n-quic to hang" — not a cosmetic or performance-only issue). Action: revert or otherwise restore capacity-shrinking semantics; add/keep a regression test pinning the invariant (as #728 did).

## Things a reviewer cannot know from the pinned head (so they are not required)
- That aws/s2n-quic specifically, or any other named downstream crate, depends on this exact behavior — that only became known via issue #725 filed by an s2n-quic maintainer (`camshaft`) after the release, and via aws/s2n-quic#2289. A reviewer at the pinned head has no way to enumerate every downstream consumer of `capacity()`-after-`advance` semantics.
- That the change would specifically manifest as a "hang" in s2n-quic rather than a panic, data corruption, or other symptom — that requires knowledge of s2n-quic's internal reassembler logic, which is not visible from the bytes repository.
- The exact revert/test PR numbers (#726, #728) and their timing — these are downstream historical facts, not derivable from the #698 diff itself.

## Orchestrator's calibration addendum (sealed with the register, before any (g) dispatch)

- Adjudicated by an independent Sonnet adjudicator (ledger S7) from primary sources, with the
  orchestrator's own reading of `src/bytes_mut.rs` at the head confirming the mechanism (the fast
  path sets `len` only; `advance_unchecked` moves `ptr` and decrements `cap`). No reviewer output
  existed when this was written.
- **Recovery of GT-g1** requires a published finding (any priority) whose claim is that the new
  `cnt == remaining()` path leaves `capacity()`/the cursor unchanged where the previous behavior
  consumed capacity, i.e. an externally observable behavior change of `BytesMut` for callers that
  read `capacity()` after `advance`. Naming a specific downstream consumer is not required. A
  question alone ("does the `Buf` API allow this?") does not recover it; nor does an observation.
- **Band:** `Changes Requested`; GT-g1 `must-fix` at P1 (P0 acceptable), `kind` `bug`,
  `invariant` or `compatibility`. A `consider` on GT-g1 is an action error but still a recovery.
  `Approved` with no GT-g1 item is a false clean. A finding whose only claim is one of the four
  plausible non-defects above is a false finding.
- **Sufficient fix:** removes the fast path or makes it decrement `cap` (and move `ptr`) like
  `advance_unchecked`; a fix that only special-cases one representation is partial.
- **Not ground truth:** the `assert!` ordering after the early return (hygiene, at most
  `consider`); the absence of a new test (accurate, hygiene-level, at most `consider`).
