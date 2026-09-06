# Review payload — `hyperium/hyper#3952` (a-high-seed2-att-04)

Rendered exactly as it would be published, had publication been authorized. This is a **retrospective
review of a merged pull request**; publication is disabled per the run conditions, so nothing below was
sent anywhere. Posting identity: `kamui` (third party; not the PR author; no prior comments/reviews from
this identity on the PR, so this is a first review, not a re-review). Event: `COMMENT`.

## Summary (review body)

**Approved (advisory)** — 0 must-fix findings, 2 consider findings.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix a hyper HTTP/1 `poll_loop` stall: when `poll_write` has more body data ready and the
connection reports write-readiness, the loop now retries instead of returning `Ready` and relying solely
on read-side readiness, matching the PR body's stated promise.

**Issue fit:** Unavailable — the pull request carries no closing or explicit issue reference; the ledger
is built from the pull-request title and body alone. Both identified promises are met: the `poll_loop`
now continues when write is ready even if read is not (`src/proto/h1/dispatch.rs:148-167`), and the
pathological repro the author describes building exists at `tests/ready_stream.rs` and is runnable with
the documented command.

**Coverage:** Complete merge-base diff reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs`,
`tests/ready_stream.rs`); `poll_loop`'s read/write-select invariant traced against
`src/proto/h1/conn.rs`'s `wants_read_again`/`can_write_head`/`can_write_body`/`can_buffer_body`;
`tests/ready_stream.rs`'s `body_test` inspected in execution order; `.github/workflows/CI.yml` and
`Cargo.toml` `required-features` cross-checked for whether the new test executes anywhere in CI; no
execution performed (offline, no-cargo run condition) — all conclusions are static.

**Reviewed:** `f2aa734e5` against merge-base `f9f8f440`.

## Findings

- [P2] [consider] ready_stream regression test never runs in CI — anchor [`Cargo.toml:243-246`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/Cargo.toml?plain=1#L243-L246); fix [`.github/workflows/CI.yml:92`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/.github/workflows/CI.yml?plain=1#L92)
- [P2] [consider] ready_stream test can't fail: no assertion and no working stall watchdog — anchor [`tests/ready_stream.rs:241-248`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L241-L248); fix [`tests/ready_stream.rs:159`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L159)

<!-- review-run head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc base-ref=master base-sha=f9f8f44058745d23fa52abf51b96b61ee7665642 merge-base=f9f8f44058745d23fa52abf51b96b61ee7665642 workflow=v5b-10 context=13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5 issues=none coverage=complete -->

---

## Inline finding comments (as they would post on the diff)

### Comment 1 — `Cargo.toml:243-246` (RIGHT), fix `.github/workflows/CI.yml:92`

**[P2] [consider] ready_stream regression test never runs in CI**

**Triggers when:** CI runs on any push or pull request against this repository.

**Impact:** No CI job ever builds or executes `tests/ready_stream.rs`, so a future regression of the
exact poll_loop write-starvation stall this change fixes would go undetected. The `test` job's matrix
only passes `--features full` (never `tracing`), so `required-features = ["full", "tracing"]` makes
Cargo skip the target outright; the only job that enables `tracing` (with the required
`RUSTFLAGS=--cfg hyper_unstable_tracing`) runs `cargo hack --no-dev-deps check`, which neither compiles
dev-dependencies nor executes tests.

**Change:** Add a CI step that runs `RUSTFLAGS='--cfg hyper_unstable_tracing' cargo test --test
ready_stream --features full,tracing` (or an equivalent invocation with both the feature and the cfg
flag), or drop the `tracing` requirement so the test runs under the existing `full`-feature test job.

Closing this without action is a correct response.

<!-- finding id=hyper/ready-stream-ci-coverage-gap head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P2 action=consider blocking=false kind=maintainability fix=.github/workflows/CI.yml:92 -->

### Comment 2 — `tests/ready_stream.rs:241-248` (RIGHT), fix `tests/ready_stream.rs:159`

**[P2] [consider] ready_stream test can't fail: no assertion and no working stall watchdog**

**Triggers when:** `body_test` runs to completion, or the stall this change fixes reoccurs.

**Impact:** The receive loop only accumulates `bytes_received` and logs it
(`tests/ready_stream.rs:241-248`); nothing asserts it equals the expected `TOTAL_CHUNKS * CHUNK_SIZE`,
so a truncated or reordered response would still pass. Separately, `TxReadyStream::poll_flush`'s
`panic_task` (`tests/ready_stream.rs:158-160`) only sleeps for one second and returns — it never calls
`panic!` — so if the poll_loop stall this PR fixes were reintroduced, the test would hang indefinitely
instead of failing with a diagnostic.

**Change:** After the receive loop, assert `bytes_received == TOTAL_CHUNKS * CHUNK_SIZE`; have the
spawned watchdog task actually `panic!` (or otherwise fail the test) once its timeout elapses instead of
silently returning.

Closing this without action is a correct response.

<!-- finding id=hyper/ready-stream-no-fail-signal head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P2 action=consider blocking=false kind=maintainability fix=tests/ready_stream.rs:159 -->

---

No open questions, no observations, no ambiguities, no coverage gaps, no unanchored findings, no
disputed items, and no prior-findings section: none of these conditional sections qualified this run
(see the research report for why each was empty).
