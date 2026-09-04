**Changes Requested (advisory)** — 1 must-fix finding, 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix the http1 `poll_loop` so that when `poll_write` shows write-readiness and the connection can flush, the loop retries instead of returning without a guaranteed wakeup, preventing a stall with custom futures that become ready without triggering the runtime's waker.

**Issue fit:** Not applicable — no linked issue and no spec was supplied (`issues=none`); the pull-request body is the only stated intent, and the change plausibly satisfies it for the scenario it targets.

**Coverage:** Complete merge-base diff reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs`, `tests/ready_stream.rs`); `conn.rs`, `io.rs`, `common/task.rs`, `trace.rs`, `tests/support/*`, `CONTRIBUTING.md`, and both GitHub Actions workflow files inspected as bounded ranges or in full to trace callers, CI wiring, and repository guidance.

**Reviewed:** `f2aa734e` against merge-base `f9f8f440`.

## Findings

- [P1] [must-fix] Track buffered progress, not body_rx presence, before retrying the write loop — anchor [`src/proto/h1/dispatch.rs:174-180`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/src/proto/h1/dispatch.rs?plain=1#L174-L180); fix [`src/proto/h1/dispatch.rs:445`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/src/proto/h1/dispatch.rs?plain=1#L445)
- [P2] [consider] Wire the new regression test into an actual CI job — anchor [`Cargo.toml:243-246`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/Cargo.toml?plain=1#L243-L246)

<!-- review-run head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc base-ref=master base-sha=f9f8f44058745d23fa52abf51b96b61ee7665642 merge-base=f9f8f44058745d23fa52abf51b96b61ee7665642 workflow=v5b-1 context=13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5 issues=none coverage=complete -->

---

### Inline comment — `src/proto/h1/dispatch.rs:174-180` (RIGHT)

**[P1] [must-fix] Track buffered progress, not body_rx presence, before retrying the write loop**

**Triggers when:** A streaming body's `poll_frame` returns `Pending` while the connection's write buffer is already empty — the common case for any body with a gap between frames (server-sent events, a rate-limited stream, a slow upstream being proxied), once the previous chunk has already flushed.

**Impact:** `can_write_again()` only checks `body_rx.is_some()`, so `wants_write_again` is true whenever a body is active and the trailing flush trivially succeeds, even though nothing was written this round. `poll_loop` re-enters `poll_write` (re-polling the already-`Pending` body) up to 16 times, then self-wakes via `task::yield_now` and is rescheduled immediately — so the connection busy-spins instead of parking on the body's own registered waker, for as long as the gap lasts.

**Change:** In `can_write_again` (`dispatch.rs:445`), gate the retry on whether this round actually buffered new output (for example, a flag set when `write_body`/`write_body_and_end` is called), not merely on `body_rx.is_some()`.

<!-- finding id=hyper/h1-dispatch-write-busy-poll head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P1 action=must-fix blocking=true kind=performance fix=src/proto/h1/dispatch.rs:445 -->

---

### Inline comment — `Cargo.toml:243-246` (RIGHT)

**[P2] [consider] Wire the new regression test into an actual CI job**

**Triggers when:** A future change reintroduces the poll_loop stall this pull request fixes.

**Impact:** `tests/ready_stream.rs` — the pathological regression test written for this exact bug — has `required-features = ["full", "tracing"]`. The `test` job runs `cargo test --features full` only (never `tracing`), and the `features` job runs `cargo hack --no-dev-deps check ... --features tracing` (`--no-dev-deps` skips `[[test]]` targets, and `check` never runs a test body). No CI job compiles or runs this test, so a regression of the stall it targets would go uncaught.

**Change:** Add a CI step that runs `RUSTFLAGS='--cfg hyper_unstable_tracing' cargo test --test ready_stream --features full,tracing` (as documented in this pull request's own description), or move `tracing`/`tracing-subscriber` to plain dev-dependencies so the test can drop the `tracing` required-feature and run under the existing `full`-only `test` job.

Closing this without action is a correct response.

<!-- finding id=hyper/ready-stream-test-not-in-ci head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P2 action=consider blocking=false kind=maintainability -->
