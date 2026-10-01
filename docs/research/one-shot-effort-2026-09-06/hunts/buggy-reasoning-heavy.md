# Buggy-reasoning-heavy PR hunt

Scope: read-only research via `gh` + `git`. No GitHub writes were made. All clones were made
in `mktemp -d` directories and deleted after inspection.

Excluded repos/PRs per instructions: hyperium/hyper, hashicorp/raft, python/typeshed, astral-sh/uv,
pola-rs/polars, spf13/cobra, microsoft/playwright, tokio-rs/tokio, redis/redis, kamui/shortlist
(and any other PR in those repos). None of the candidates below touch those repos.

---

## 0. Vetted alternate: `libuv/libuv#4400` — REJECTED as primary candidate

**PR:** libuv/libuv#4400, "linux: exploit `eventfd` in `EPOLLET` mode to avoid syscall per wakeup"
Author: panjf2000. Merged 2024-07-29T23:59:41Z into `v1.x`.

- head `9295a8875351e60bb8287997490b7a6c86843339`, base `5d1ccc12c48099d720bb39f7430c480a52953039`
  (recorded base == merge-base; not rebased, confirmed with `git merge-base`).
- merge commit `e5cb1d3d3d4ab3178ac567fb6a7f0f4b5eef3083`.
- Files: `src/unix/async.c` (+32/-17), `src/unix/linux.c` (+14/-8). 2 files, ~71 changed lines.
- No originating issue (self-motivated optimization). Review: 3 reviews (bnoordhuis COMMENTED,
  saghul APPROVED, vtjnash APPROVED), 59 issue/PR comments — heavy discussion, including
  vtjnash's prescient warning about non-standard edge-trigger semantics and bnoordhuis's own
  comment "I'm somewhat worried this change may cause hard-to-debug regressions."

**What happened after merge:** libuv/libuv#4584 ("libuv 1.49.0 breaks dnstap test in BIND 9",
opened 2024-10-16, bisected to this commit) led to a same-day revert, PR #4585 ("Revert
'linux: eliminate a read on eventfd per wakeup (#4400)'", merged 2024-10-17,
merge `18d48bc13ce4a44efb9c37fd81cfdd9db7bc92b8`).

**Vetting conclusion (this is the point of vetting #4400 first):** the long discussion on #4584
shows the maintainers (bnoordhuis, vtjnash) converging on the theory that **the real defect is a
missing seq_cst memory fence in `uv_async_send()` when the async handle is already pending** —
a preexisting property of libuv, not something #4400 introduced. #4400 only removed the eventfd
`read()` syscall, which had been *incidentally* acting as extra latency that hid a downstream
consumer's (BIND9's `isc/async.c`, using `urcu`'s wfcqueue) latent race. libuv later hardened
`uv_async_send()` unconditionally to seq_cst in PR #5149 ("async: make seq_cst the default", merged
2026-06-03, files `src/unix/async.c`, `src/uv-common.c`, `src/uv-common.h`, `src/win/async.c`,
`docs/src/async.rst`, merge `cdc632c68feb3961f84ea109295db38dfa082347`) — **a separate PR, in
different files, not a fix to #4400's own diff.** The eventfd optimization was then relanded
**verbatim** as PR #4589 ("Reland ...(#4400)", merged 2026-06-08, merge
`076df9f50d74e169d0ed986974d2a4a00f96bc10`) on top of the already-seq_cst'd base — i.e. #4589's
diff is textually the same async.c/linux.c change as #4400, confirming the fix did not touch the
reland's own lines at all. Finally, BIND9 maintainer Mno-hime reported back on the issue thread:
**"It seems to be a problem on BIND 9 end. I created an MR with a possible fix."** — i.e. the
ultimate root cause was conceded to be in BIND9's own code, not libuv.

**Verdict:** #4400 introduced *no confirmed material defect of its own*. It is a case where an
optimization changed timing enough to expose a latent, never-fully-confirmed race in a downstream
consumer, prompting a precautionary revert and an unrelated hardening PR. This fails both "PR
introduced a real, later-confirmed material defect" and "statically visible in the diff" (the
debated invariant lives in BIND9's `lib/isc/async.c`, a different repository, and libuv's own
maintainers never agreed on the mechanism). **Do not use as the primary/backup candidate** —
recorded only because the task asked to vet it explicitly.

SHAs to exclude if ever mirroring this repo for an exercise: `e5cb1d3d3d4ab3178ac567fb6a7f0f4b5eef3083`
(buggy merge), `18d48bc13ce4a44efb9c37fd81cfdd9db7bc92b8` (revert), `cdc632c68feb3961f84ea109295db38dfa082347`
(seq_cst fix), `076df9f50d74e169d0ed986974d2a4a00f96bc10` (reland).

---

## 1. `tokio-rs/bytes#698` / revert `#726` — RECOMMENDED (top pick)

**Repository:** tokio-rs/bytes. **PR:** #698, "Reuse capacity when possible in
`<BytesMut as Buf>::advance` impl". **Author:** paolobarbolini. **Merged:** 2024-04-25T07:08:17Z.
**Base branch:** master.

- head `7052d2454a2370ab9583f63711df89f3bd7bec83`, base `ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401`.
  `git merge-base` == recorded base — not rebased.
- merge commit `baa5053572ed9e88ca1058ec2b5a3f08046c5a40`.
- **Changed-file manifest:** `src/bytes_mut.rs` +8/-0. One file, 8 lines. This is about as small
  as a real defect gets.
- **Originating issue:** none (author's own idea from reviewing their own code, no "Fixes:").
- **Prior review record:** 3 reviews (Darksonn COMMENTED, paolobarbolini COMMENTED,
  braddunbar COMMENTED then APPROVED) + 6 issue comments, all about code style (which variable
  to use, ordering of the assert vs. the new branch) and about *not* putting the check in
  `advance_unchecked` because `split_to`/`split_off` need a "real" advance. **Nobody flagged
  that `advance` reaching `remaining()` should still be required to physically move the cursor.**

**The defect:** `BytesMut::advance(cnt)` is documented/relied-upon (via the `Buf` trait contract)
to always physically advance the read cursor by `cnt`, i.e. reduce `remaining()`/capacity by
`cnt` bytes as a side effect, so a subsequent write-side operation can reuse the freed prefix.
The head diff (`src/bytes_mut.rs`, `impl Buf for BytesMut { fn advance }`) adds:
```rust
if cnt == self.remaining() {
    unsafe { self.set_len(0) };
    return;
}
```
When `cnt == remaining()`, instead of moving the start pointer forward by `cnt` (freeing the
consumed prefix but leaving the physical allocation's start where it was), the code resets the
**logical length to 0 while implicitly reusing the whole original capacity from offset 0**. This
silently changes what "the buffer" is made of: code that expects `advance` to shrink the
*addressable capacity* window (so that repeated `split_to`-like consumption converges toward an
empty, fully-detached `BytesMut`) instead gets an object that still owns/exposes the full original
backing allocation. Consumers who relied on `advance` implying "the capacity consumed by this call
is gone for good" get memory-management/aliasing surprises. Trigger: any `BytesMut` with
`cnt == remaining()` passed to `Buf::advance`. Consequence (confirmed downstream): in AWS's
`s2n-quic`, a `reassembler::Slot` and a `reader::Storage for BytesMut` impl relied on `advance`
monotonically reducing `remaining()`; after this change those invariants silently broke
(aws/s2n-quic#2289), corrupting buffer bookkeeping in a reassembly path. Exact lines: the added
8 lines in `fn advance` in `src/bytes_mut.rs` (visible with `git show baa5053572e -- src/bytes_mut.rs`).
Surrounding code a reviewer needs: `BytesMut::advance_unchecked` and `BytesMut::split_to`/`split_off`
in the same file (the PR discussion itself explains that `advance_unchecked` couldn't take this
optimization because `split_to`/`split_off` need a *real* advance — the reviewer needs to notice
that `advance` (called here) is used by the same category of external callers who assume the same
"real advance" property, just via the public `Buf` trait method rather than the internal one).

**Confirming issue/fix:** tokio-rs/bytes#725 "BytesMut::advance no longer advances cursor," opened
by camshaft (s2n-quic maintainer) 2024-08-01, with links to the two broken s2n-quic call sites.
Fixed by full revert PR #726 ("Revert 'Reuse capacity when possible...'"), merged 2024-08-01T20:38:17Z,
head `f400b119a9773973118eb4a4fc3dcb127974bcc9`, base `03fdde9dcfe69caf681ecaa1d97f8105a9c9a6c1`
(ancestor-check confirms base is ancestor of head — not rebased), merge commit
`f488be48d07d899dc428c5cd7f5c11a95bf7716c`, files `src/bytes_mut.rs` +0/-7 (mechanical inverse of #698).
A regression test then landed in PR #728 ("test: ensure BytesMut::advance reduces capacity"),
merged 2024-08-02T19:07:45Z, head `f50c007da958d4ed597e25b9e1f54f727f9953fe`, merge commit
`ed7d5ff39e39c2802c0fa9e2fc308f6a3e0beda7`, file `tests/test_bytes.rs` +37/-0. The PR body includes
the exact failing assertion against #698's commit: `assertion 'left == right' failed: Buf::advance
should reduce the remaining capacity`.
**Corrective invariant:** `Buf::advance(cnt)` on `BytesMut` must always reduce `remaining()`
(and therefore usable capacity from the current start) by exactly `cnt`, with no special-cased
short-circuit that reuses freed capacity as a hidden side effect — codified by the
`advance_bytes_mut_remaining_capacity` test in #728.
**No other defects were later found in this change** (single, clean root cause).

**Tempting false positives (not defects):**
- "`unsafe { self.set_len(0) }` is unsound" — false; 0 is always ≤ capacity, so this specific call
  is memory-safe by itself. The bug is a behavioral/API-contract violation, not a memory-safety bug.
- "the `cnt <= self.remaining()` assert ordering nit that braddunbar raised is the bug" — false;
  that's a redundant-check style nit, orthogonal to the actual defect.
- "off-by-one: should be `cnt == self.remaining() - 1`" — false; `cnt == self.remaining()` is the
  correct trigger condition for "fully consumed"; the bug is not in the condition, it's in what
  the branch *does* once triggered.

**SHAs a truncated mirror must exclude:** `baa5053572ed9e88ca1058ec2b5a3f08046c5a40` (buggy merge),
`f488be48d07d899dc428c5cd7f5c11a95bf7716c` (revert merge), `ed7d5ff39e39c2802c0fa9e2fc308f6a3e0beda7`
(regression-test merge). Also hide issue #725 and PRs #726/#728 themselves.

**Test suite:** `cargo test --test test_bytes` from the crate root.
Ran this in a temp clone at head `7052d2454a2370ab9583f63711df89f3bd7bec83`: **84 passed, 0
failed, runtime 0.09s** (whole invocation incl. process startup ~5.3s). Confirms the defect is
**not** caught by the suite at head — the only test that would catch it (`advance_bytes_mut_remaining_capacity`)
did not exist until #728, three months later. No network needed beyond the initial `git clone`;
building only needs a stable Rust toolchain (no external crates besides bytes' own dev-deps).

**Why this is reasoning-heavy:** the change looks like a pure micro-optimization ("just reuse
capacity when you'd end up empty anyway") and every reviewer comment is about *where* to put the
check, never about *whether* the resulting behavior change is safe. Spotting the defect requires
holding the `Buf`/`BufMut` capacity-management invariant in your head (that `advance` is a
*consuming, one-way* operation whose only allowed side effect is shrinking the addressable window)
and asking "does silently returning the freed capacity to the same object break any caller who
distinguishes 'has been consumed' from 'still addressable'?" — exactly the kind of invariant-tracing
the task wants, and it needs no runtime data or special platform: reading `fn advance` plus the two
neighboring methods (`advance_unchecked`, `split_to`) it's diffed against is sufficient. **Confidence
the defect is statically visible: high.**

---

## 2. `psf/requests#6667` / revert `#6767` — RECOMMENDED (co-top pick / alternate #1)

**Repository:** psf/requests. **PR:** #6667, "Avoid reloading root certificates to improve
concurrent performance". **Author:** agubelu. **Merged:** 2024-05-15T20:07:26Z. **Base branch:** main.

- head `4089f3dc65f783beaa53cc032958ab625440d0ac`, base `8dd3b26bf59808de24fd654699f592abf6de581e`.
  `git merge-base` == recorded base — not rebased.
- merge commit `9a40d1277807f0a4f26c9a37eea8ec90faa8aadc`.
- **Changed-file manifest:** `src/requests/adapters.py` +28/-18. One file.
- **Originating issue:** none (perf investigation written up in the PR body itself, with profiler
  output; no "Fixes:").
- **Prior review record:** 5 reviews (sigmavirus24 CHANGES_REQUESTED then APPROVED, agubelu
  COMMENTED, nateprewitt APPROVED, one unrelated bot-ish comment) and 21 issue comments. The
  reviewers *did* debate whether the shared context should be module-global vs. per-adapter
  (nateprewitt: "I was curious if we'd be better off doing this per-Adapter instance instead of
  globally") and sigmavirus24 raised, but did not block on, "I'm pretty sure SSLContext is not
  itself thread safe... loading it at the module will likely cause issues" — a partial, hedged
  warning that was talked out of blocking the merge (a CPython/OpenSSL SSL maintainer, `tiran`,
  weighed in only *after* merge with the precise mechanism).

**The defect:** `_urllib3_request_context()` in `src/requests/adapters.py` computes a **single,
process-wide, module-level `ssl.SSLContext`** at import time:
```python
_preloaded_ssl_context = create_urllib3_context()
_preloaded_ssl_context.load_verify_locations(extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH))
```
and then, whenever `verify is True`, unconditionally injects it into the per-request
`pool_kwargs`:
```python
elif verify is True:
    pool_kwargs["ssl_context"] = _preloaded_ssl_context
```
This `pool_kwargs` dict flows from `_urllib3_request_context` into
`HTTPAdapter._get_connection()` (`self.poolmanager.connection_from_host(**host_params,
pool_kwargs=pool_kwargs)`), which urllib3 merges on top of whatever was already configured on
`self.poolmanager` via `HTTPAdapter.init_poolmanager(**pool_kwargs)`. Two consequences, both
statically visible by tracing those three functions in `adapters.py` (`_urllib3_request_context`,
`_get_connection`, `init_poolmanager`):
1. **Compatibility break / silent override:** a custom `HTTPAdapter` subclass that sets its own
   `ssl_context` in `init_poolmanager` (a long-documented urllib3 pattern for custom CA stores or
   client-cert mTLS, e.g. `kwargs['ssl_context'] = self.context; return
   super().init_poolmanager(*args, **kwargs)`) gets that context **silently replaced** by the
   global default on every `verify=True` request, because the per-call `pool_kwargs` computed
   in `_urllib3_request_context` wins the merge. mTLS client certs configured this way stop being
   sent.
2. **Shared mutable state / concurrency hazard:** because the *same* `SSLContext` object instance
   is now handed to every connection pool across every `Session`/thread in the process, any code
   path that further configures the context (which is exactly what several affected users' custom
   adapters were doing) mutates a live object that other threads are simultaneously using for TLS
   handshakes. CPython core dev `tiran` confirmed on the issue thread: *"It is thread safe as
   long as you don't reconfigure it once it is used by a connection... changing ciphers,
   verification settings, or mTLS certs can lead to surprising behavior... unrelated to threads,
   can even occur in a single-threaded program."*

**Trigger:** any process that (a) mounts a custom `HTTPAdapter` setting its own `ssl_context`, or
(b) runs concurrent requests across threads with per-thread differing client certs against a
shared `Session`/adapter. **Consequence:** silently-dropped client certificates / wrong trust
store (compatibility+security-adjacent correctness bug), and in one reported case a **segmentation
fault** under `concurrent.futures` with per-thread client certs (user `mingshuang`, reproducer
posted on the PR thread). Exact lines: `src/requests/adapters.py`, function
`_urllib3_request_context` (the `elif verify is True: pool_kwargs["ssl_context"] =
_preloaded_ssl_context` line) plus the module-level `_preloaded_ssl_context = ...` initializer.
Surrounding code a reviewer needs: `HTTPAdapter.init_poolmanager` and `HTTPAdapter._get_connection`
in the same file, to see that a fresh per-call `pool_kwargs["ssl_context"]` silently shadows
whatever the adapter instance had already configured. (Full proof that urllib3's
`PoolManager.connection_from_host` performs this override — rather than requests — requires one
shallow hop into urllib3, which is outside this file; flag this as the one non-fully-self-contained
step.)

**Confirming issues:** psf/requests#6715 ("SSLV3_ALERT_HANDSHAKE_FAILURE after upgrade... custom
SSL adapter doesn't seem to be working anymore", closed by follow-up PR #6716) and #6717
("SSLCertVerificationError - unable to get local issuer certificate", closed as duplicate of
#6715) both reproduce the silent-override defect directly; #6764 ("permission denied regression
reading extracted certs with multiple users") and #6790 ("Import time regression") are *secondary*
regressions from the same PR (see false positives below) but not the core defect. **Fix/revert:**
PR #6767 ("Revert caching a default SSLContext"), merged 2025-06-13T16:42:08Z, head
`11d68c17bcd66bd3e2c5137b0a7aad7f59967102`, base `8ff173b186f135670879db9fbe1e68a6b5209c89`
(ancestor-confirmed, not rebased), merge commit `90fee0876aea97c639b3bf698d83a12876d2f160`, file
`src/requests/adapters.py` +16/-39 — fully removes the shared `_preloaded_ssl_context` and restores
per-`cert_verify`-call cert loading. Revert body: *"Due to the number of edge cases and concurrency
issues we've encountered with this change, we've decided the benefit doesn't currently outweigh the
pain."* An intermediate, incomplete mitigation, PR #6716 ("Allow for overriding of specific pool key
params", merged 2024-05-24T21:37:06Z, merge `145b5399486b56e00250204f033441f3fdf2f3c9`), tried to let
adapters override individual `pool_kwargs` keys but did not fully solve the shared-mutation hazard,
which is why the full revert (#6767) eventually shipped in 2.32.5.
**Corrective invariant:** a per-request/per-adapter TLS configuration (custom `ssl_context`, CA
bundle, client cert) must never be silently shadowed by a process-wide default, and a shared
`SSLContext` object must never be hedged behind `verify=True` where it can be mutated after being
handed to live connections — restored by removing the shared global entirely.
**Other defects found in the same change (secondary, same root PR):** #6764 (the eager
`extract_zipped_paths(DEFAULT_CA_BUNDLE_PATH)` call at import time re-triggers a pre-existing,
previously "won't fix" `/tmp/cacert.pem` multi-user permission race, issue #5994, now hit
unconditionally at import instead of lazily) and #6790 (import-time cert loading cost regression).

**Tempting false positives (not defects):**
- "the `/tmp/cacert.pem` permission bug (#6764) is *the* introduced defect" — no; that race
  pre-dates this PR (issue #5994, won't-fix years earlier); #6667 only made it unconditional at
  import instead of lazy, a secondary aggravation, not the core defect.
- "`create_urllib3_context()` failing at import time would crash all of `requests`" — a reported
  robustness concern (#6790), but a perf/robustness regression, not the defect that drove the revert.
- "the `os.path.isdir(verify)` branch for string `verify` is buggy" — false; unrelated, correct
  enhancement, not implicated in any follow-up issue.

**SHAs a truncated mirror must exclude:** `9a40d1277807f0a4f26c9a37eea8ec90faa8aadc` (buggy merge),
`145b5399486b56e00250204f033441f3fdf2f3c9` (intermediate partial-fix merge), `90fee0876aea97c639b3bf698d83a12876d2f160`
(revert merge). Also hide issues #6715/#6717/#6764/#6790 and PRs #6716/#6767.

**Test suite:** `pytest tests/test_requests.py -k "ssl or verify"` from the repo root (venv with
`pip install -e .` + `pytest pytest-httpbin`). Ran this at head `4089f3dc65f783beaa53cc032958ab625440d0ac`
in a temp clone/venv: **5 passed, 1 failed in 37.7s.** The one failure
(`test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert`) raised
`SSLCertVerificationError: ... Missing Authority Key Identifier` — this looks like an environment/
OpenSSL-version mismatch with the old pinned `pytest-httpbin` cert fixture on a modern OpenSSL
(3.x rejects the fixture's self-signed cert for missing AKI), **not** the concurrency/override
defect under investigation; the concurrency defect requires a custom-adapter or multithreaded
client-cert scenario that isn't in this targeted subset. Needs network only for `pip install`
(PyPI); the tests themselves use `pytest-httpbin`'s local server, no external network.

**Why this is reasoning-heavy:** the diff itself is an innocuous-looking one-line optimization
(cache and reuse a context object), and the danger only becomes apparent once you know two
outside facts that are *not* stated in the diff: (1) `ssl.SSLContext` is a mutable, stateful
object whose safety guarantees are conditional on "don't reconfigure after first use," and (2) a
long-standing, documented urllib3/requests extension pattern is to hand a *custom* per-adapter
`ssl_context` through `init_poolmanager`. A reviewer has to trace three functions across the file
to see that the newly-added line unconditionally clobbers that extension point, and separately
reason about the OpenSSL-level hazard of sharing one context across concurrent handshakes — this
is squarely "tracing invariants across call sites," not pattern-matching a known anti-pattern.
**Confidence the defect is statically visible: medium-high** — the override mechanism (part 1) is
fully visible in `adapters.py` alone; the concurrency/mutation hazard (part 2) requires outside
domain knowledge about `SSLContext` semantics (confirmed by `tiran`'s comment, not derivable from
the diff alone), so a reviewer without ssl-module background could miss the segfault-class risk
even after spotting the override.

---

## 3. `cockroachdb/pebble#5743` / revert `#5755` / re-fix `#5769` — alternate #2 (backup)

**Repository:** cockroachdb/pebble. **PR:** #5743, "internal/keyspan: fix interleaving iterator
edge case". **Author:** jbowens. **Merged:** 2026-01-23T22:07:50Z. **Base branch:** master.

- head `c93c72ba17b4a9cf4e484482c47f6272ed8fe9a6`, base recorded on the PR:
  `8b8a5dc48de282baf78e5b4b826872448017d6a7`. **`git merge-base` computed on a full-history clone
  is `d93d50ed215ab17ec095e1039b41915867cb8de6` — different from the recorded base, and the recorded
  base is *not* an ancestor of head.** This means the PR's actual diff base (what `gh pr diff`
  shows) is the older commit `d93d50ed...`, and the "base" field on the PR simply reflects wherever
  `master` had advanced to by the time of the API query/merge — the PR itself was **not kept
  rebased onto master's tip** before merging. Use `d93d50ed215ab17ec095e1039b41915867cb8de6` as the
  true diff base if reproducing.
- merge commit `057782e0f7c72100296c136453803b7ca90b93d4`.
- **Changed-file manifest:** `internal/keyspan/interleaving_iter.go` +128/-134,
  `internal/keyspan/interleaving_iter_test.go` +1/-1, `internal/keyspan/testdata/interleaving_iter`
  +42/-4, `internal/keyspan/testdata/interleaving_iter_masking` +4/-2,
  `testdata/iter_histories/probe_prefix` +0/-2. 5 files, ~318 changed lines (near the top of the
  size budget; testdata files are golden fixtures, not hand-reasoned code).
- **Originating issue:** none (no "Fixes:"/closing reference).
- **Prior review record:** 1 review, RaduBerinde APPROVED with "2 comments" per the Reviewable.io
  banner; **note:** cockroachdb's actual review discussion happens on the external Reviewable.io
  tool, and those inline comments are not retrievable via the GitHub REST/GraphQL PR-comments API
  (only a summary banner and 2 native GitHub comments — a CI bot notice and "jbowens: TFTR!" —
  are visible through `gh`). This is a real limitation for auditing "did anyone raise the defect":
  we can confirm the PR shipped with a single lightweight LGTM and no visible pushback, but cannot
  rule out something being said on Reviewable.io that isn't mirrored to GitHub.

**The defect:** the PR fixes a real bug (an interleaving iterator configured with an upper bound
`b` that does `SeekGE(b)` could leave state such that a later `Prev()` omits a span entirely) by
adding an upfront short-circuit in `InitSeekGE`/`InitSeekLT`/`SeekGE`/`SeekPrefixGE`/`SeekLT`:
```go
if i.opts.UpperBound != nil && i.cmp(key, i.opts.UpperBound) >= 0 {
    i.pos = posBeyondUpperBound
    return nil
}
i.keyspanSeekGE(key)   // <-- only reached if the bound check above did NOT return
```
The new bound check and early `return nil` were placed **before** the call to
`i.keyspanSeekGE(key)` (visible directly in the diff of `internal/keyspan/interleaving_iter.go`,
`InitSeekGE`/analogous spots in `SeekGE`/`SeekPrefixGE`/`SeekLT`), i.e. when the short-circuit
fires, **the child keyspan iterator is never seeked at all.** This breaks an invariant used
elsewhere in pebble's iterator stack — `TrySeekUsingNext` (in `iterator.go`/`level_iter.go`/
`merging_iter.go`) — which inspects the *actual* position the child iterators were left at to
decide whether a subsequent seek can be served via a cheap `Next()` instead of a full re-seek.
Skipping the child seek left stale/inconsistent child-iterator state whenever the short-circuit
path was taken. Trigger: `Seek[Prefix]GE`/`SeekLT` calls that land at-or-beyond an iterator bound
in the presence of range deletions requiring cascading seeks. Consequence: wrong query results
(a later positioning operation can read/serve the wrong key), found by CockroachDB's nightly
**metamorphic/fuzz testing**, not a hand-written unit test (pebble/pebble#5751 "TestMetaCockroachKVs
failed" and #5754 "TestMeta failed", both on commit `057782e0f7c7`). Exact lines: compare, in the
diff of `internal/keyspan/interleaving_iter.go`, the order of the new bound-check block relative to
`i.keyspanSeekGE(key)`/`i.keyspanSeekLT(key)` in each of `InitSeekGE`, `InitSeekLT`, `SeekGE`,
`SeekPrefixGE`, `SeekLT`. Surrounding code a reviewer needs: the `TrySeekUsingNext` implementations
in `iterator.go`/`level_iter.go` (a different file) — this is the invariant a purely local read of
`interleaving_iter.go` would not reveal by itself; the PR's own follow-up commit message spells it
out explicitly (see below), which is how this was actually confirmed rather than independently
re-derived here.

**Confirming issues/fix:** pebble#5751 and #5754 (both nightly metamorphic-test failures on
`057782e0f7c7`) led to revert PR #5755 ("Revert 'internal/keyspan: fix interleaving iterator edge
case'"), merged 2026-01-26T15:30:23Z, head `3fb2ab29ba2d55c8ba034a1298038b5371b461ab`, base
`057782e0f7c72100296c136453803b7ca90b93d4` (= the buggy merge commit; ancestor by construction),
merge commit `03153d8aca5561e52792a50eab3a78123f1436e3`, closing both #5751 and #5754. A corrected
re-fix landed as PR #5769 ("internal/keyspan: fix interleaving iterator edge case" — same title,
retried), merged 2026-02-09T15:32:21Z, base `79fc5832761458d415689c67a5697f5d1aae36eb`, head
`b378f549c0d483568a763914701e496f6c87fcc9`, merge commit `2d17333e4df36c46096e103983472b8aa5db1e46`.
**PR #5769's own body states the exact root cause of #5743's bug in so many words:** *"Note a
previous version of this commit (057782e) mistakenly elided the entire seek. This could result in
breaking the invariants around child iterator positioning that the top-level Iterator's
TrySeekUsingNext optimization relies upon."* The corrected code calls `i.keyspanSeekGE(key)` /
`i.keyspanSeekLT(key)` **unconditionally first**, then checks the bound and sets
`posSeekedBeyondUpperBound`/`posSeekedBeyondLowerBound` afterward, preserving child-iterator
positioning either way.
**Corrective invariant:** even when a seek is short-circuited from the caller's point of view
(because the target lies at/beyond a bound and yields no result), the child point/keyspan
iterators must still be physically repositioned, because other optimizations (`TrySeekUsingNext`)
read child-iterator position as ground truth regardless of what the parent iterator returned.
**No other defects were later found in this specific change** beyond the one described (the
re-fix in #5769 is otherwise structurally identical to #5743's approach, just reordered).

**Tempting false positives (not defects):**
- "renaming `saveSpanForward`/`saveSpanBackward` to a unified `saveSpan` + explicit
  `enforceBoundsForward`/`enforceBoundsBackward` is itself the bug" — false, a faithful mechanical
  refactor; the actual defect is purely about *when* `keyspanSeekGE`/`keyspanSeekLT` is invoked.
- "the new `posBeyondLowerBound`/`posBeyondUpperBound` enum constants shift `iota` values and break
  other switches" — false; Go reassigns all named constants consistently and consumers switch on
  names, not raw ints.
- "removing the old `i.span = nil` special-case comment in `SeekLT` is a regression" — false; that
  logic was subsumed into `enforceBoundsBackward`, not dropped (verifiable by reading it).

**SHAs a truncated mirror must exclude:** `057782e0f7c72100296c136453803b7ca90b93d4` (buggy merge),
`03153d8aca5561e52792a50eab3a78123f1436e3` (revert merge), `2d17333e4df36c46096e103983472b8aa5db1e46`
(re-fix merge). Also hide issues #5751/#5754 and PRs #5755/#5769.

**Test suite:** `go test ./internal/keyspan/...` from the module root would exercise the
datadriven interleaving-iterator tests directly; the actual defect, however, was only caught by
`go test -tags invariants ./internal/metamorphic -run TestMeta...` (randomized, long-running fuzz
tests, run nightly, not in the fast unit suite). Not run here — pebble needs a full Go module
fetch and the metamorphic suite alone routinely runs tens of minutes to hours, exceeding the
8-minute budget and needing network access to the Go module proxy. The fast `internal/keyspan`
unit tests likely pass at head (updated in the same PR to match new golden output) but would
**not** exercise the actual defect, consistent with "the defect usually is not caught by the
[fast] suite."

**Why this is reasoning-heavy:** the diff reorders calls across five sibling `Seek*`/`Init*`
methods in a hand-rolled iterator state machine; the only way to see the bug is to ask "is it safe
to skip seeking the child iterator when I'm not going to yield anything to *my* caller?" — which
requires knowing a non-adjacent piece of code (`TrySeekUsingNext`) depends on child-iterator
position as an out-of-band contract. That is "tracing invariants across call sites," not
pattern-matching. **Confidence statically visible: medium** — the mechanical fact (early-return
precedes the seek call) is squarely in the diff; the reason it matters needs `TrySeekUsingNext` in
a different file (bigger fan-out than "a few surrounding functions"), and review having happened
on Reviewable.io (opaque to `gh`) adds uncertainty about what reviewers actually saw.

---

## 4. `etcd-io/etcd#17563` / revert `#21435` — noted but NOT recommended (weaker fit)

**Repository:** etcd-io/etcd. **PR:** #17563, "Reuse events used for syncing watchers". **Author:**
serathius. **Merged:** 2024-12-02T18:01:08Z. Base `afb5c1d85b2f0ec24852c4d409bca8401dbdea6b`, head
`348c0cb2be84b9aa1800aca39df1fb9bc2bbf343` (a shallow-clone ancestor check did not resolve cleanly
in the time available — recommend a full, unshallowed clone before relying on this pairing).
Merge commit `6fa734266936dc50ea51996e56594b878acc3f11`. Files:
`server/storage/mvcc/watchable_store.go` +58/-23, `..._test.go` +106/-2, `watcher_test.go` +2/-2.
13 review threads (ahrtr/serathius back-and-forth) — a genuinely well-reviewed PR.

**What happened:** removing the `if !c.contains(string(kv.Key)) { continue }` filter from
`kvsToEvents` (needed so a computed event slice could be shared/reused across watchers with
overlapping-but-not-identical key ranges) meant events for **every** key in a revision range are
now retained regardless of whether any live watcher cares about them. Under watch-heavy,
wide-keyspace workloads (Kubernetes API server via etcd) this caused a confirmed memory blow-up
(issue etcd-io/etcd#21355, up to +162% max RSS at 250 nodes). Fixed by revert PR #21435 ("Revert
'Reuse events between sync loops'"), merged 2026-03-05T23:49:43Z, merge
`25c242cbef2427715833d9472df2375ea967651b`, closing #21355.

**Why this is ranked below the other three:** the defect is a resource/availability regression
(unbounded-relative-to-workload memory growth, eventually OOM) rather than a correctness/
concurrency/data-integrity/security bug in the strict sense the task enumerates, and — more
importantly — **it was only discovered via production-scale workload profiling** (kube-burner
density tests across 24–250 node clusters, pprof heap diffs), not by reasoning over the diff; even
etcd's own maintainers spent weeks building bespoke reproduction tooling before agreeing on the
mechanism. That is close to the task's own explicit caveat: "a defect that needs runtime data...
to see is weaker." It is included here only as a fourth data point, not as a top recommendation.
Merge-base for #17563 vs #21435 base was not independently reconciled in the time budget; treat
the SHAs above as provisional if this candidate is picked up later.

---

## Ranked recommendation

**Best candidate: `tokio-rs/bytes#698` (revert `#726`, regression test `#728`).**
Deciding reasons: smallest possible diff (8 added lines, one file) with a completely
self-contained defect — everything needed to reason about it (the `advance`/`advance_unchecked`/
`split_to` contract) lives in the same ~60-line region of one file; a clean, single confirmed
downstream break (s2n-quic) with an explicit bug report and a revert whose diff is the exact
inverse; no ambiguity about causation (unlike libuv#4400) and no cross-file invariant needed
(unlike pebble#5743); trivially reproducible test run (5s, no network beyond clone) that confirms
the existing suite does not catch it. This is the cleanest "read the diff, trace one invariant,
find the bug" exercise of the four.

**Backup candidate: `psf/requests#6667` (revert `#6767`).**
Deciding reasons: also a single-file, ~46-line diff, with an unusually rich confirmed-impact
trail (silent mTLS/cert-override reports, a reported segfault under concurrent client-cert usage,
and an explicit domain-expert comment from a CPython ssl-module maintainer nailing the mechanism)
— arguably *more* dramatic in consequence than bytes#698, which is why it's ranked a close second
rather than third. It's marked backup rather than co-winner only because fully proving the
override mechanism requires one shallow hop into urllib3's `PoolManager.connection_from_host`
(outside the requests repo itself), and because part of the hazard (SSLContext mutation-after-use
semantics) is domain knowledge not fully derivable from the diff alone — making it slightly less
"self-contained" than bytes#698, though still strong enough to use directly if a second candidate
is needed.

(cockroachdb/pebble#5743 is a solid third option if more difficulty/size is wanted, but its
cross-file invariant and opaque Reviewable.io review trail make it noticeably harder to package
as a clean single-sitting review than either of the top two.)
