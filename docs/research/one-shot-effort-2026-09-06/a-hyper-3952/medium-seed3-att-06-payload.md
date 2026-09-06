# Review payload — hyperium/hyper#3952 (rendered, not published — retrospective review of a merged pull request)

## Summary

**Mode:** Retrospective review of merged pull request; publication disabled.

**Changes Requested (advisory)** — 1 must-fix finding, 1 consider finding.

**Intent:** Fix a logical issue in the HTTP/1 `poll_loop`: when `poll_write` demonstrates write readiness and the connection is ready to write, the loop should keep writing instead of yielding and stalling.

**Issue fit:** Unavailable — no closing or explicit issue reference exists on the pull request; the ledger was built from the pull-request title and body alone. The pull-request body's core promise ("if the poll_write is demonstrating readiness to write and the connection has readiness to write, we should do that or else hyper may stall") is met for the general streaming case but, per Finding 1, the same write-continuation mechanism can busy-spin or permanently livelock rather than making bounded, waker-driven progress — so the promised outcome is only partially delivered.

**Coverage:** Complete merge-base diff reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs`, `tests/ready_stream.rs`); the `poll_loop`/`poll_write`/`can_write_again` concurrency surface and the new test's assertion coverage were both inspected with evidence-backed outcomes. Focused execution of `tests/ready_stream.rs` was unavailable (offline, no toolchain); its logic was traced by semantics instead of run.

**Reviewed:** `f2aa734e5699a91fc20f1178e38af7b1e374bdbc` against merge-base `f9f8f44058745d23fa52abf51b96b61ee7665642`.

## Findings

- [P0] [must-fix] poll_loop's write-continuation check can busy-spin or livelock while a body streams — anchor [`src/proto/h1/dispatch.rs:171-195`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/src/proto/h1/dispatch.rs?plain=1#L171-L195); fix [`src/proto/h1/dispatch.rs:445`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/src/proto/h1/dispatch.rs?plain=1#L445)
- [P3] [consider] Add an assertion to `body_test`'s response check — anchor [`tests/ready_stream.rs:240-248`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L240-L248); fix [`tests/ready_stream.rs:240`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L240)

<!-- review-run head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc base-ref=master base-sha=f9f8f44058745d23fa52abf51b96b61ee7665642 merge-base=f9f8f44058745d23fa52abf51b96b61ee7665642 workflow=v5b-10 context=13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5 issues=none coverage=complete -->

---

## Inline comment 1 — `src/proto/h1/dispatch.rs:171-195` (RIGHT)

**[P0] [must-fix] poll_loop's write-continuation check can busy-spin or livelock while a body streams**

**Triggers when:** A response or request body's `poll_frame` returns `Pending` at least once while `body_rx` is `Some`, or `body_rx` is still `Some` when `self.is_closing` becomes `true` (for example, the dispatch channel errors or closes mid-stream).

**Impact:** `can_write_again` only checks `self.body_rx.is_some()`, not whether this iteration's `poll_write` made real progress. Combined with `poll_flush` returning `Ready` immediately whenever nothing new was buffered, `wants_write_again` stays `true` on every iteration regardless of the body's actual readiness. In the ordinary streaming case this makes `poll_loop`'s bounded 16-iteration loop exhaust every iteration and then self-wake via `task::yield_now` (which self-wakes rather than parking), repeating for as long as the body is open — a busy spin instead of a real wait on the body's own registered waker. When `is_closing` is set while `body_rx` is still `Some`, the loop never reaches its `Ready` exit at all, so `is_done()` is never evaluated — a permanent livelock that also blocks the connection from ever completing shutdown.

**Change:** Track whether `poll_write` made genuine forward progress this iteration (for example, whether `poll_frame` returned `Ready`), and gate `wants_write_again` on that per-iteration signal — mirroring `wants_read_again`'s edge-triggered `notify_read` semantics — rather than on `body_rx`'s mere presence, including on the `is_closing` short-circuit path.

<!-- finding id=dispatch/poll-loop-write-busy-spin head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P0 action=must-fix blocking=true kind=concurrency fix=src/proto/h1/dispatch.rs:445 -->

## Inline comment 2 — `tests/ready_stream.rs:240-248` (RIGHT)

**[P3] [consider] Add an assertion to `body_test`'s response check**

**Triggers when:** A future regression to `poll_write`/`poll_loop` delivers a truncated, reordered, or otherwise corrupted streamed body without literally hanging the connection open forever.

**Impact:** `body_test` contains no `assert!`/`assert_eq!`/`expect`-style check on the response it receives. `bytes_received` is only logged via `info!`, never compared against the expected total (`TOTAL_CHUNKS * CHUNK_SIZE`). The receive loop terminates on channel closure regardless of how many bytes actually arrived, so such a regression would pass this test silently.

**Change:** Add `assert_eq!(bytes_received, TOTAL_CHUNKS * CHUNK_SIZE);` (or an equivalent check) after the receive loop in `body_test`, so the test validates the behavior it exercises rather than only its ability to terminate.

Closing this without action is a correct response.

<!-- finding id=tests/ready-stream-no-assertions head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P3 action=consider blocking=false kind=maintainability fix=tests/ready_stream.rs:240 -->
