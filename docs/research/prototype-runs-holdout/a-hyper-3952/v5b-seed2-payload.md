**Changes Requested (advisory)** — 1 must-fix finding, 2 consider findings, 2 observations.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix `Dispatcher::poll_loop` (`src/proto/h1/dispatch.rs`) so that when the connection is write-ready and there is more body to send, the loop retries the write instead of exiting and relying on a wakeup a misbehaving custom future/transport might never deliver.

**Issue fit:** No linked issue; issue alignment is not applicable (`issues=none`). Judged against the pull-request body's own stated intent: partial — the added `wants_write_again` retry condition is provably unreachable outside a connection-closing interleaving (see Observations), and that same closing interleaving introduces a new livelock (see Findings).

**Coverage:** Complete merge-base diff reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs`, `tests/ready_stream.rs`); `poll_write`/`poll_read`/`poll_read_head`/`close`/`is_done` read in full, plus the relevant `Conn`/`Buffered` callees in `src/proto/h1/conn.rs` and `src/proto/h1/io.rs`; `.github/workflows/CI.yml` and `CONTRIBUTING.md` checked for applicable process rules. Static only, per this run's binding conditions (no `cargo`/execution).

**Reviewed:** `f2aa734e5` against merge-base `f9f8f440`.

## Findings

- [P1] [must-fix] Stop poll_loop from spinning when close() leaves body_rx set — anchor [`src/proto/h1/dispatch.rs:172-194`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/src/proto/h1/dispatch.rs?plain=1#L172-L194); fix [`src/proto/h1/dispatch.rs:438`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/src/proto/h1/dispatch.rs?plain=1#L438)
- [P2] [consider] Wire the new ready_stream regression test into CI — anchor [`Cargo.toml:243-246`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/Cargo.toml?plain=1#L243-L246); fix [`.github/workflows/CI.yml:71`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/.github/workflows/CI.yml?plain=1#L71)
- [P2] [consider] Assert the transferred byte count in body_test — anchor [`tests/ready_stream.rs:241-248`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L241-L248); fix [`tests/ready_stream.rs:248`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L248)

## Observations

- The new `poll_loop` doc comment has an unbalanced parenthesis. Evidence: `src/proto/h1/dispatch.rs:177`.
- The new `wants_write_again` term in `poll_loop` is unreachable during ordinary non-closing steady-state body streaming; it only evaluates once `close()` has already run earlier in the same iteration. Evidence: `src/proto/h1/dispatch.rs:335-364`, `src/proto/h1/dispatch.rs:172-173`.

<!-- review-run head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc base-ref=master base-sha=f9f8f44058745d23fa52abf51b96b61ee7665642 merge-base=f9f8f44058745d23fa52abf51b96b61ee7665642 workflow=v5b-1 context=13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5 issues=none coverage=complete -->

---

## Finding comments (as they would be posted inline on the diff)

### `src/proto/h1/dispatch.rs:172-194` (RIGHT)

**[P1] [must-fix] Stop poll_loop from spinning when close() leaves body_rx set**

**Triggers when:** The read side calls `close()` while a response body is still streaming (`body_rx.is_some()`) — e.g. `poll_read_head`'s read-error branch, its EOF-with-write-already-closed branch, or its "dispatch no longer receiving messages" branch — and the connection's own flush succeeds, which is the ordinary case.

**Impact:** `poll_loop`'s `wants_write_again` term stays true forever because nothing clears `body_rx` once `is_closing` is set, so the loop never takes its early exit; after 16 no-op iterations it self-wakes via `task::yield_now` and repeats forever. `poll_inner` never reaches `is_done()`, so the connection livelocks instead of shutting down.

**Change:** In `close()` (`src/proto/h1/dispatch.rs`), clear `self.body_rx` (and `self.body_tx`), or force `wants_write_again` to `false` whenever `self.is_closing` is true, so `poll_loop` exits on the same iteration it did before this change, regardless of `body_rx`'s leftover value.

<!-- finding id=hyper/dispatch-poll-loop-closing-livelock head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P1 action=must-fix blocking=true kind=concurrency fix=src/proto/h1/dispatch.rs:438 -->

### `Cargo.toml:243-246` (RIGHT)

**[P2] [consider] Wire the new ready_stream regression test into CI**

**Triggers when:** CI runs as currently configured on this pull request's head.

**Impact:** `tests/ready_stream.rs` requires `full` and `tracing` together, but no CI job enables both with `cargo test`, so this dedicated regression test for the fixed stall never runs automatically.

**Change:** Add `tracing` to one of the `test` job's feature sets in `.github/workflows/CI.yml` (or add a dedicated matrix entry), so `cargo test --features full,tracing` runs in CI.

Closing this without action is a correct response.

<!-- finding id=hyper/ready-stream-test-not-wired-into-ci head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P2 action=consider blocking=false kind=maintainability fix=.github/workflows/CI.yml:71 -->

### `tests/ready_stream.rs:241-248` (RIGHT)

**[P2] [consider] Assert the transferred byte count in body_test**

**Triggers when:** Any run of `body_test`, including one where the connection closes early or the fixed stall recurs.

**Impact:** The test has no `assert`/`panic!`/`.expect()`, so it passes even on far fewer than the expected bytes; and because there is no per-test timeout and the mock's `panic_task` never actually panics, a recurrence of the targeted stall would hang the test rather than fail it.

**Change:** Add `assert_eq!(bytes_received, TOTAL_CHUNKS * CHUNK_SIZE)` after the receive loop, and assert on (or propagate) the server task's connection result instead of only logging it.

Closing this without action is a correct response.

<!-- finding id=hyper/ready-stream-test-no-assertions head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P2 action=consider blocking=false kind=maintainability fix=tests/ready_stream.rs:248 -->
