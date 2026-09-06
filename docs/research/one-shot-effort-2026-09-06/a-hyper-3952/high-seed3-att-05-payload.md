**Approved (advisory)** — 0 must-fix findings, 2 consider findings.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix the http1 `poll_loop` so it keeps writing a streamed response body while the connection remains write-ready, instead of returning early and stalling once there is nothing left to read.

**Issue fit:** Issue alignment was unavailable — the pull request carries no closing or explicit issue reference; the ledger was built from the pull-request title and body. Both rows are met: the loop now retries writing when `can_write_again()` is true and the last flush succeeded (`src/proto/h1/dispatch.rs`), and the promised `tests/ready_stream.rs` pathological example exists and is structurally consistent with its documented manual repro command; execution of that command was not performed under this run's no-execution constraint.

**Coverage:** Complete merge-base diff reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs`, `tests/ready_stream.rs`). Concurrency risk traced through `Conn::poll_flush` (`src/proto/h1/conn.rs:827`) and `Buffered::poll_flush` (`src/proto/h1/io.rs:267`) to confirm the fix restores forward progress for the reported stall. CI wiring inspected (`.github/workflows/CI.yml`) for the new test's feature gating. No focused test executed — static review only, per this run's no-execution constraint; no execution result is implied to have passed.

**Reviewed:** `f2aa734e5` against merge-base `f9f8f440`.

## Findings

- [P2] [consider] Wire the `ready_stream` regression test into CI — anchor [`Cargo.toml:243-246`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/Cargo.toml?plain=1#L243-L246); fix [`.github/workflows/CI.yml:69`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/.github/workflows/CI.yml?plain=1#L69)
- [P3] [consider] Assert transferred bytes in the `ready_stream` test — anchor [`tests/ready_stream.rs:242-244`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L242-L244); fix [`tests/ready_stream.rs:244`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L244)

## Ambiguities

- The term "explicit deferral of a design, naming, or API-shape decision" could be read broadly to include a maintainer's request to simplify a test's implementation, or narrowly to cover only public interface/API decisions. `seanmonstar` asked for a simpler `ready_stream.rs` unit test and `lthiery` said they would "take another critical pass ... and see what I can do to simplify," but the reviewed head carries no further commits reflecting that pass and the thread stayed unresolved. This run applied the narrow reading, so no open question was raised for the readability request itself; the overlapping, checkable part of the concern — that the test does not verify what it claims — is instead captured as the second finding above.

<!-- review-run head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc base-ref=master base-sha=f9f8f44058745d23fa52abf51b96b61ee7665642 merge-base=f9f8f44058745d23fa52abf51b96b61ee7665642 workflow=v5b-10 context=13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5 issues=none coverage=complete -->

---

## Finding 1 (rendered as it would be posted, inline on `Cargo.toml:243-246`)

**[P2] [consider] Wire the `ready_stream` regression test into CI**

**Triggers when:** Any CI job in `.github/workflows/CI.yml` runs `cargo test`, since every job's `--features` argument omits `tracing`.

**Impact:** The `ready_stream` test's `required-features = ["full", "tracing"]` (`Cargo.toml:246`) makes Cargo silently skip it whenever `tracing` is disabled, and enabling `tracing` without `RUSTFLAGS='--cfg hyper_unstable_tracing'` hard-fails the build (`src/trace.rs:5`). No job sets both, so this regression test for the reported `poll_loop` stall never runs automatically; only a manual local run with the exact PR-body command exercises it.

**Change:** In `.github/workflows/CI.yml`, add a `test`-job matrix leg (or new job) that runs `cargo test --features full,tracing` with `RUSTFLAGS: "--cfg hyper_unstable_tracing"` set, so `ready_stream` executes on every pull request.

Closing this without action is a correct response.

<!-- finding id=hyper/dispatch/ready-stream-ci-gap head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P2 action=consider blocking=false kind=maintainability fix=.github/workflows/CI.yml:69 -->

## Finding 2 (rendered as it would be posted, inline on `tests/ready_stream.rs:242-244`)

**[P3] [consider] Assert transferred bytes in the `ready_stream` test**

**Triggers when:** `cargo test --test ready_stream --features full,tracing` runs to completion without hanging.

**Impact:** `body_test` only loops on `client_stream.recv()` and logs `bytes_received`; it never asserts the byte count against `TOTAL_CHUNKS * CHUNK_SIZE` or checks the response status (`tests/ready_stream.rs:241-244`). A future regression that closes the connection early (dropping `server_stream` before the full body is written) would end the `recv()` loop and let the test pass with a truncated body.

**Change:** In `tests/ready_stream.rs`, assert `bytes_received == TOTAL_CHUNKS * CHUNK_SIZE` (and the response status) right after the receive loop.

Closing this without action is a correct response.

<!-- finding id=hyper/tests/ready-stream-missing-assertions head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P3 action=consider blocking=false kind=maintainability fix=tests/ready_stream.rs:244 -->
