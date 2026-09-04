# Review payload — `hyperium/hyper#3952` (holdout target (a), arm v5b-noverify, seed 1)

This is the review exactly as it would be published (retrospective mode: rendered and not
posted). Summary body first, then each finding comment with its trailer. Nothing else was
rendered — no observations trailer (observations live only in the summary body, as the
output contract specifies), no questions (none were admitted), no unanchored findings.

## Summary (review body)

**Approved (advisory)** — 0 must-fix findings, 2 consider findings, 0 open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix a deadlock in the HTTP/1 dispatcher's `poll_loop`: when a flush succeeds and body data is still pending, the loop must retry the write path rather than exiting on the read-side signal alone, or a waker is never registered and the connection stalls.

**Issue fit:** No linked issue; the pull request body is the sole statement of intent, and it is met — `wants_write_again` (retry when body data remains and the flush just succeeded) is added alongside the unchanged `wants_read_again`, matching the invariant the author and maintainer both describe in review: either side registers a waker, or the loop yields and polls again.

**Coverage:** Complete merge-base diff reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs`, `tests/ready_stream.rs`). The full `poll_loop`/`poll_write`/`poll_read`/`poll_flush` interaction was traced against the base version and against the maintainer's stated waker invariant. `Cargo.toml`'s dependency and test-target placement, and `.github/workflows/CI.yml`'s job matrix, were inspected for the new test's wiring. No execution was performed (offline, static review only, per this run's binding conditions).

**Reviewed:** `f2aa734e5` against merge-base `f9f8f440`.

## Findings

- [P2] [consider] Wire the `ready_stream` regression test into CI — anchor [`Cargo.toml:243-246`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/Cargo.toml?plain=1#L243-L246); fix [`.github/workflows/CI.yml:92`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/.github/workflows/CI.yml?plain=1#L92)
- [P2] [consider] Bound the `ready_stream` client-read loop with a timeout — anchor [`tests/ready_stream.rs:242-244`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L242-L244)

## Observations

- `TxReadyStream`'s `poll_since_write:bool,` field omits the space after the colon that every sibling field in the same struct carries. Evidence: `tests/ready_stream.rs:23`.
- `body_test` counts `bytes_received` but never asserts it against the expected `TOTAL_CHUNKS * CHUNK_SIZE` total, so a response-corruption regression would not fail the test. Evidence: `tests/ready_stream.rs:241-248`.
- `can_write_again` takes `&mut self` though its body only reads `self.body_rx`. Evidence: `src/proto/h1/dispatch.rs:445-447`.

<!-- review-run head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc base-ref=master base-sha=f9f8f44058745d23fa52abf51b96b61ee7665642 merge-base=f9f8f44058745d23fa52abf51b96b61ee7665642 workflow=v5b-1 context=13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5 issues=none coverage=complete -->

## Finding comments

### Finding: hyper/ready-stream-ci-wiring

**[P2] [consider] Wire the `ready_stream` regression test into CI**

**Triggers when:** CI's `test` job runs `cargo test ${{ matrix.features }}` with
`matrix.features: --features full` — the only job in this repository that runs `cargo test`.

**Impact:** `ready_stream`'s `required-features = ["full", "tracing"]` (Cargo.toml:243-246)
makes Cargo silently skip it under `--features full`, and hyper's `mod trace` refuses to
compile with the `tracing` feature unless `RUSTFLAGS='--cfg hyper_unstable_tracing'` is also
set (src/trace.rs:5-9) — no CI job sets both together. The `features` job checks the `tracing`
feature but with `cargo hack --no-dev-deps check`, which never builds `tests/`. This pull
request's own regression test for the fixed deadlock never runs in CI.

**Change:** Add a step that runs `RUSTFLAGS='--cfg hyper_unstable_tracing' cargo test --test
ready_stream --features full,tracing`, or drop the test's `tracing` requirement so it runs
under the existing `full` matrix.

Closing this without action is a correct response.

<!-- finding id=hyper/ready-stream-ci-wiring head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P2 action=consider blocking=false kind=maintainability fix=.github/workflows/CI.yml:92 -->

### Finding: hyper/ready-stream-no-timeout

**[P2] [consider] Bound the `ready_stream` client-read loop with a timeout**

**Triggers when:** the exact stall this pull request fixes (a write-ready future whose waker
is never signaled) recurs in a future change to `poll_loop`.

**Impact:** `tests/ready_stream.rs:242-244`'s `while let Some(chunk) = client_stream.recv().await`
has no bound. Every comparable wait in this crate's other connection tests is wrapped in
`tokio::time::timeout` (`tests/server.rs`: 21 occurrences; `tests/client.rs`: 29). Without one
here, a recurrence of the bug this file exists to catch makes the test hang indefinitely
instead of failing.

**Change:** Wrap the read loop in `tokio::time::timeout(Duration::from_secs(N), ...)`, matching
the sibling convention, and fail the test explicitly when it elapses.

Closing this without action is a correct response.

<!-- finding id=hyper/ready-stream-no-timeout head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P2 action=consider blocking=false kind=maintainability -->
