**Approved (advisory)** — 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix a poll_loop deadlock where the http1 dispatcher could stop looping while the write side still had readiness to make progress, per the PR body's own description; add a pathological regression test (`tests/ready_stream.rs`) reproducing the stall.

**Issue fit:** No linked issue; the PR body is the only stated intent, and its described defect (loop exits while write is ready to continue) is met — traced `wants_write_again` (`src/proto/h1/dispatch.rs:180`) to a reachable, effective non-shutdown interleaving matching the new test's two-call flush-parity mock (verified independently).

**Coverage:** Complete merge-base diff reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs`, `tests/ready_stream.rs`, the last new in full); risk-directed checks on the concurrency/wakeup path, dependency placement, and new-test hygiene all have an evidence-backed outcome.

**Reviewed:** `f2aa734e` against merge-base `f9f8f440`.

## Findings

- [P3] [consider] Make the flush watchdog actually fail the test on a stall — anchor [`tests/ready_stream.rs:155-172`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L155-L172)

<!-- review-run head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc base-ref=master base-sha=f9f8f44058745d23fa52abf51b96b61ee7665642 merge-base=f9f8f44058745d23fa52abf51b96b61ee7665642 workflow=v5b-1 context=13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5 issues=none coverage=complete -->

---

### Finding: Make the flush watchdog actually fail the test on a stall

**[P3] [consider] Make the flush watchdog actually fail the test on a stall**

**Triggers when:** A future regression reintroduces the stall this test exists to catch — the connection stops being polled and the second flush that completes a chunk's pair never arrives.

**Impact:** The spawned watchdog task is named `panic_task` and its removal is logged as "Aborting panic," but its body (`tokio::time::sleep(...).await`) never panics, asserts, or otherwise fails the test if it runs to completion. No `tokio::time::timeout` wraps the client's receive loop or the server task either, so a real stall shows up as an indefinite hang instead of a clear, fast test failure.

**Change:** In `tests/ready_stream.rs`, have the spawned watchdog task actually panic (or otherwise fail the test, e.g. by signalling a flag the test asserts on) once its sleep elapses, so a future stall makes this test fail fast with a clear message instead of hanging.

Closing this without action is a correct response.

<!-- finding id=ready-stream/watchdog-task-no-panic head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P3 action=consider blocking=false kind=maintainability -->
