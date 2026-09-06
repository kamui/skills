<!--
Review payload for hyperium/hyper#3952 — cell a-high-seed1, attempt att-01.
Retrospective review of a merged pull request; publication disabled.
This file renders exactly what would be posted as one forge-native review
(summary body + line comments, event=COMMENT), produced by
`scripts/validate_review.py --emit-batch` from the validated payload at
`/tmp/effort124/work/a-high-seed1-att-01/payload.json`. Nothing here was
posted anywhere.
-->

# Review summary body

**Mode:** Retrospective review of merged pull request; publication disabled.

**Changes Requested (advisory)** — 1 must-fix finding, 1 consider finding, 1 observation.

**Intent:** Fix a poll_loop stall where a body's write-readiness could be missed right after the connection finished flushing, so hyper does not deadlock waiting on a waker that will never fire.

**Issue fit:** Partial — the reported stall is fixed for the scenario the author describes, but the write-again condition the fix introduces is broader than the quoted promise (see the must-fix finding below); the pull request's repro-test claim (`tests/ready_stream.rs` exists and runs with the documented invocation) is met.

**Coverage:** Complete merge-base diff reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs`, `tests/ready_stream.rs`); poll_loop's unchanged read/flush/yield dependencies (`src/proto/h1/conn.rs`, `src/proto/h1/io.rs`, `src/common/task.rs`) inspected as bounded ranges to establish the guarantees the change now relies on; CI wiring (`.github/workflows/CI.yml`) inspected for the new test target. No test executed — offline, no `cargo`/toolchain available per the run's conditions; `tests/ready_stream.rs`'s `body_test` was inspected by trace only, execution unavailable.

**Reviewed:** `f2aa734e5699a91fc20f1178e38af7b1e374bdbc` against merge-base `f9f8f44058745d23fa52abf51b96b61ee7665642`.

## Findings

- [P1] [must-fix] Guard write-again on the body actually being ready, not merely present — anchor [`src/proto/h1/dispatch.rs:180-192`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/src/proto/h1/dispatch.rs?plain=1#L180-L192); fix [`src/proto/h1/dispatch.rs:445-447`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/src/proto/h1/dispatch.rs?plain=1#L445-L447)
- [P2] [consider] Wire the poll_loop regression test into CI and give it a pass/fail signal — anchor [`tests/ready_stream.rs:241-248`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L241-L248); fix [`Cargo.toml:246`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/Cargo.toml?plain=1#L246)

## Observations

- The pre-existing `!can_write_body()` branch in `poll_write` returns `Poll::Pending` with no waker registration visible in that branch itself, unrelated to and unchanged by this diff. Evidence: `src/proto/h1/dispatch.rs:424`.

<!-- review-run head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc base-ref=master base-sha=f9f8f44058745d23fa52abf51b96b61ee7665642 merge-base=f9f8f44058745d23fa52abf51b96b61ee7665642 workflow=v5b-10 context=13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5 issues=none coverage=complete -->

---

# Line comments (as they would be attached to the diff, event `COMMENT`)

## Comment 1 — `src/proto/h1/dispatch.rs:180-192` (RIGHT)

**[P1] [must-fix] Guard write-again on the body actually being ready, not merely present**

**Triggers when:** A response or request body is actively streaming (`body_rx` is `Some`) and its `poll_frame` returns `Pending` this cycle — the producer has nothing ready yet (a slow upstream, a paused SSE/long-lived chunked response, or the exact custom-future scenario this pull request describes) — while the connection's write buffer is already empty, so `poll_flush` trivially succeeds over an ordinary transport.

**Impact:** `can_write_again()` only checks `body_rx.is_some()`, so `wants_write_again` is true even though nothing was written this cycle. `poll_loop` spins through all 16 read/write/flush iterations on every poll, then calls `task::yield_now`, which unconditionally re-wakes the task — a continuous busy loop burning CPU instead of waiting on the body's own registered waker, for as long as the body stays paused.

**Change:** In `can_write_again` (`src/proto/h1/dispatch.rs:445-447`), track whether `poll_write` actually made forward progress this cycle — wrote a frame, or the body's `poll_frame` returned `Ready` — instead of merely `body_rx.is_some()`, so `wants_write_again` is true only when there is genuine write readiness to consume.

**Source:** Pull-request body: "if the poll_write is demonstrating readiness to write and the connection has readiness to write, we should do that or else hyper may stall."

<!-- finding id=dispatch/poll-loop-write-again-overbroad head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P1 action=must-fix blocking=true kind=concurrency fix=src/proto/h1/dispatch.rs:445-447 -->

## Comment 2 — `tests/ready_stream.rs:241-248` (RIGHT)

**[P2] [consider] Wire the poll_loop regression test into CI and give it a pass/fail signal**

**Triggers when:** A future change reintroduces this exact poll_loop deadlock, or a related regression in the read/write wake protocol.

**Impact:** `tests/ready_stream.rs` is the only `[[test]]` entry in `Cargo.toml` gated behind `required-features = ["full", "tracing"]`; CI's only `cargo test` job uses `--features full` (never `tracing`), and the only job that enables `tracing` runs `cargo hack check`, never `test`. `body_test` also asserts nothing about `bytes_received` and never bounds its receive loop with a timeout, so even run manually it can only hang, not fail.

**Change:** Either drop the `"tracing"` required-feature (matching the three sibling `[[test]]` entries, which require only `"full"`) so the CI `test` job exercises this file, or add a job that runs it with `--features full,tracing` and `--cfg hyper_unstable_tracing`; also assert `bytes_received == TOTAL_CHUNKS * CHUNK_SIZE` and wrap the receive loop in a bounded `tokio::time::timeout` in `tests/ready_stream.rs`.

**Source:** Pull-request body: "I built a pathological example \"ready_stream.rs\"..."

Closing this without action is a correct response.

<!-- finding id=tests/ready-stream-no-ci-signal head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P2 action=consider blocking=false kind=maintainability fix=Cargo.toml:246 -->

---

# Would-be forge call (never executed — publication disabled)

Event: `COMMENT`. Commit: `f2aa734e5699a91fc20f1178e38af7b1e374bdbc`. Produced by `python3 scripts/validate_review.py --emit-batch < payload.json`, exit 0, from the payload that also passed `python3 scripts/validate_review.py < payload.json` with exit 0 (zero violations). The full batch JSON (`commit_id`, `event`, `body`, `comments[]` with `path`/`line`/`side`/`start_line`/`start_side`/`body` per comment) is preserved at `/tmp/effort124/work/a-high-seed1-att-01/batch.json` for the record; its `body` and comment text are byte-identical to what is rendered above.
