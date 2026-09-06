**Mode:** Retrospective review of merged pull request; publication disabled.

**Changes Requested (advisory)** — 1 must-fix finding, 1 consider finding.

**Intent:** Fix a poll_loop bug where, if the connection's write side is ready to write more but only the read side's `wants_read_again()` decided whether to keep polling, hyper could stall waiting on a waker that a custom future never signals; adds a pathological regression test (`tests/ready_stream.rs`) for it.

**Issue fit:** No originating issue; issue alignment is unavailable. Built from the pull-request title and body. Its one acceptance requirement — "if the poll_write is demonstrating readiness to write and the connection has readiness to write, we should do that or else hyper may stall" (pr-body) — is met: the added `wants_write_again` condition does make `poll_loop` continue when a body has more to write and the connection can flush, so the described stall is fixed. A defect in how that fix decides "more to write" is reported separately below.

**Coverage:** Complete merge-base diff reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs`, `tests/ready_stream.rs`); `poll_loop`'s enclosing impl block, `Buffered::poll_flush` (`src/proto/h1/io.rs`), `task::yield_now` (`src/common/task.rs`), and `Conn::wants_read_again`/`can_write_body`/`can_buffer_body` (`src/proto/h1/conn.rs`) inspected as risk-directed reads for the concurrency finding below; `.github/workflows/CI.yml` inspected for the new test's CI reachability. No execution: this is a static-only review (no `cargo`/`rustc`/`miri`/`loom`); the added `body_test` was inspected by tracing its setup, custom `Read`/`Write` stream, and its recv loop rather than run, per this run's execution ban.

**Reviewed:** `f2aa734e` against merge-base `f9f8f44`.

## Findings

- [P1] [must-fix] Fix poll_loop busy-spin when a streaming body is legitimately Pending — anchor [`src/proto/h1/dispatch.rs:180`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/src/proto/h1/dispatch.rs?plain=1#L180); fix [`src/proto/h1/dispatch.rs:445-447`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/src/proto/h1/dispatch.rs?plain=1#L445-L447)
- [P2] [consider] Wire the new `ready_stream` regression test into CI — anchor [`Cargo.toml:243-246`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/Cargo.toml?plain=1#L243-L246); fix [`.github/workflows/CI.yml:170-173`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/.github/workflows/CI.yml?plain=1#L170-L173)

## Observations

- The new `body_test` in `tests/ready_stream.rs` never asserts `bytes_received` against the `TOTAL_CHUNKS * CHUNK_SIZE` total it computes for the `content-length` header, so a truncated response would still make the test pass. Evidence: `tests/ready_stream.rs:242-243`, `tests/ready_stream.rs:224`.

<!-- review-run head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc base-ref=master base-sha=f9f8f44058745d23fa52abf51b96b61ee7665642 merge-base=f9f8f44058745d23fa52abf51b96b61ee7665642 workflow=v5b-10 context=13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5 issues=none coverage=complete -->

---

## Finding 1

**[P1] [must-fix] Fix poll_loop busy-spin when a streaming body is legitimately Pending**

**Triggers when:** A streaming body's `poll_frame` returns `Pending` (e.g. a slow upstream or paced channel) while the connection's write buffer is otherwise empty, so `Buffered::poll_flush` resolves `Ready` immediately.

**Impact:** `can_write_again()` returns true whenever `body_rx` is `Some`, regardless of whether `poll_write` made progress this round, so `wants_write_again` stays true through the whole gap between chunks. `poll_loop` never exits early, exhausts its 16-round budget, and `task::yield_now` unconditionally self-wakes — the connection's task is rescheduled immediately and repeats, busy-spinning at full CPU until the body next produces data.

**Change:** In `can_write_again`, track whether `poll_write` observed real progress or newly buffered data this round (edge-triggered, like `wants_read_again`'s `notify_read` bit), not merely whether `body_rx` still exists, so the loop parks instead of spinning while the body is genuinely blocked.

<!-- finding id=dispatch/write-busy-spin head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P1 action=must-fix blocking=true kind=concurrency fix=src/proto/h1/dispatch.rs:445-447 -->

## Finding 2

**[P2] [consider] Wire the new `ready_stream` regression test into CI**

**Triggers when:** A future change regresses the poll_loop write-readiness fix this pull request makes.

**Impact:** `tests/ready_stream.rs` is gated by `required-features = ["full", "tracing"]`, but CI's `test` job only ever passes `--features full` or `full,nightly`; the only job that adds `tracing` runs `cargo hack check`, never `cargo test`. Cargo silently skips a test target whose required features are unmet, so this regression test never runs automatically and a future reintroduction of the stall would go undetected.

**Change:** Add a CI step (or extend the existing `features` job) that runs `cargo test --features full,tracing` with `RUSTFLAGS="--cfg hyper_unstable_tracing"` so `ready_stream` executes on every push.

Closing this without action is a correct response.

<!-- finding id=cargo/ready-stream-ci-gap head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P2 action=consider blocking=false kind=maintainability fix=.github/workflows/CI.yml:170-173 -->
