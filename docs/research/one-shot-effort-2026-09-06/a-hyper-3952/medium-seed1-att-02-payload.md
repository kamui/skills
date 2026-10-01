# Review payload — `hyperium/hyper#3952` (retrospective, publication disabled)

This is the review exactly as it would be published — summary body, every finding with its trailer —
rendered by `scripts/validate_review.py --emit-batch` and stopped before any write, per the run
conditions' retrospective-mode instruction. Event would be `COMMENT` (posting identity `kamui`, a
third party, no gating authorization). Commit pinned: `f2aa734e5699a91fc20f1178e38af7b1e374bdbc`.

## Summary body

**Changes Requested (advisory)** — 1 must-fix finding, 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix a real deadlock/stall in the http1 `Dispatcher::poll_loop`: when `poll_write` demonstrates readiness to write and the connection is ready, the loop should retry the write instead of yielding without a guaranteed wakeup.

**Issue fit:** No originating issue; ledger built from the pull-request title and body. The core promise (`pr-body/"if the poll_write is demonstrating readiness to write and the connection has readiness to write, we should do that or else hyper may stall"`) is met: `wants_write_again`/`wants_read_again` in `poll_loop` widen the loop's continuation gate to cover the write side, closing the deadlock the pathological `TxReadyStream` mock in `tests/ready_stream.rs` reproduces.

**Coverage:** Complete merge-base diff reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs`, `tests/ready_stream.rs`); `Conn`'s `poll_flush`/`can_buffer_body`/`wants_read_again` (`src/proto/h1/conn.rs`) and `Buffered::poll_flush` (`src/proto/h1/io.rs`) inspected as unchanged callees the change depends on; no CI or focused-test execution available (no network/toolchain access in this run; the new test's logic was decided by a full semantics trace instead).

## Findings

- [P1] [must-fix] `poll_loop` busy-spins on any body that is not always instantly ready — anchor [`src/proto/h1/dispatch.rs:176-180`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/src/proto/h1/dispatch.rs?plain=1#L176-L180); fix [`src/proto/h1/dispatch.rs:445`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/src/proto/h1/dispatch.rs?plain=1#L445)
- [P3] [consider] Assert the received byte count in `body_test` — anchor [`tests/ready_stream.rs:241-248`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L241-L248)

<!-- review-run head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc base-ref=master base-sha=f9f8f44058745d23fa52abf51b96b61ee7665642 merge-base=f9f8f44058745d23fa52abf51b96b61ee7665642 workflow=v5b-10 context=13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5 issues=none coverage=complete -->

## Finding comments (as they would be posted as line comments)

### `src/proto/h1/dispatch.rs:176-180` (RIGHT)

**[P1] [must-fix] `poll_loop` busy-spins on any body that is not always instantly ready**

**Triggers when:** A request or response body streams more than one frame and its `poll_frame` does not resolve synchronously every time (any body other than one backed by an always-ready in-memory stream — one reading from disk, waiting on a timer, backpressured, or fed from another task), while the write buffer is already flushed and there is no read data to retry (`wants_read_again()` false, the ordinary non-pipelined case).

**Impact:** `can_write_again()` returns only `self.body_rx.is_some()`, with no signal about whether `poll_frame` actually returned `Ready` this iteration. Because `Buffered::poll_flush` (`src/proto/h1/io.rs:267-271`) trivially resolves `Ready` whenever nothing is buffered, `wants_write_again` stays `true` in this state regardless of the body's real readiness, so `poll_loop` runs its full 16-iteration budget every time. Because `task::yield_now` (`src/common/task.rs:9`) wakes the task itself before returning `Pending`, this is not a one-time bounded cost: the connection's task is immediately re-queued and repeats the same 16-iteration spin continuously, for as long as the body stays not-ready — an unthrottled busy loop, not the merge-base's single-iteration exit.

**Change:** In `can_write_again` (or its caller), require a signal that `poll_write` actually made progress or that the body itself transitioned to ready this iteration — e.g. a flag `poll_write` sets when it observes real forward motion — instead of the mere presence of `body_rx`.

<!-- finding id=dispatch/poll-loop-write-busy-spin head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P1 action=must-fix blocking=true kind=performance fix=src/proto/h1/dispatch.rs:445 -->

### `tests/ready_stream.rs:241-248` (RIGHT)

**[P3] [consider] Assert the received byte count in `body_test`**

**Triggers when:** A future regression truncates or corrupts the streamed response body (for example, a partial-write path that miscounts remaining frames) while still allowing the connection to close cleanly.

**Impact:** `body_test` never asserts that `bytes_received` equals the expected total; it only logs the count. The test's only real pass/fail signal is whether the future resolves at all (the hang this PR fixes), so a truncated body would still make the test pass in CI.

**Change:** Add an assertion that `bytes_received == TOTAL_CHUNKS * CHUNK_SIZE` (or an equivalent decisive check) before the test ends.

Closing this without action is a correct response.

<!-- finding id=tests/ready-stream-no-assertion head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P3 action=consider blocking=false kind=maintainability -->

## Open questions

None.

## Observations

None published (see the research report §7 for why one incidental fact was folded into finding 1's evidence instead).
