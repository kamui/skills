# Research report — `hyperium/hyper#3952`, cell `a-high-seed2`, attempt `att-04`

Skill under evaluation: `code-review-publish` (snapshot at `/tmp/effort124/skill/skills/code-review-publish/`).
Payload (rendered review): [`a-high-seed2-att-04-payload.md`](./a-high-seed2-att-04-payload.md).

## 1. Metadata

| Field | Value |
| --- | --- |
| Target | `hyperium/hyper#3952` — "fix(http1): poll_loop writes when ready" |
| Cell / attempt | `a-high-seed2` / `att-04` |
| Skill | `code-review-publish` (this run's snapshot; `workflow=v5b-10` per `output-contract.md` / `validate_review.py`) |
| Primary reviewer model | `claude-sonnet-5` (this session) |
| Sub-agents spawned | **None.** No mandatory-verification trigger fired (see §7); no sub-agent was dispatched, so there is no second model to report. |
| Verification trigger fired | **None.** Neither survivor (`hyper/ready-stream-ci-coverage-gap`, `hyper/ready-stream-no-fail-signal`) was proposed `must-fix`, and neither touches security/authorization, data loss/corruption, destructive migration, or an externally observable compatibility break — the only mandatory triggers `SKILL.md` step 3 defines. Zero-survivor clean-verdict mode also did not apply because two candidates survived as findings. See §7 for the full mechanism checklist. |
| Candidates raised | 4 (see §3 ledger): 2 survivors, 2 dropped |
| Candidates surviving primary falsification | 2 (`hyper/ready-stream-ci-coverage-gap`, `hyper/ready-stream-no-fail-signal`), both `primary-confirmed` (neither required independent verification) |
| Verifier verdicts | None (no batch dispatched) |
| Findings for publication | 2, both `[P2] [consider]`, `kind=maintainability`, `blocking=false` — see §2 |
| Questions | 0 |
| Observations | 0 |
| Coverage | `complete` (every changed file reviewed; every risk-directed check has an evidence-backed outcome; no fetch or verification left outstanding) |
| Derived status | `Approved (advisory)` (0 unsettled `must-fix`; no incomplete coverage/verification; no open question that could change the verdict) |
| Own token usage | Not exposed by this harness to the model; I have no figure to report. |

### Sub-agent roster

None were dispatched. This is the honest, skill-mandated outcome for this diff, not an omission: the rubric's mandatory-verification list is narrow (must-fix, security/authorization, data loss/corruption, destructive migration, externally observable compatibility break), and my two survivors are both `consider`/`maintainability` test-and-CI-hygiene findings that fall outside it. I did seriously entertain a `concurrency`-kind candidate against the core `poll_loop` fix (ledger row `dispatch/poll-loop-write-retry-gap`, §3) — the kind of claim that, had it survived primary falsification as a `must-fix`, would have mandated a `v5b-verifier-effort-high` batch under `references/verifier.md` and `references/verifier-concurrency.md`. It did not survive: my own falsification (§7, and the trace in §5) found no concrete failing interleaving beyond the one the merged fix and its test already address, so there was nothing to hand to a verifier and no batch was warranted or dispatched.

## 2. Findings for publication (verbatim, with verification status)

### Finding 1 — `hyper/ready-stream-ci-coverage-gap`

- **Priority / action:** P2 / `consider` (`blocking=false`)
- **Kind:** `maintainability`
- **Anchor:** `Cargo.toml:243-246` (RIGHT) — the new `[[test]] name = "ready_stream" ... required-features = ["full", "tracing"]` block
- **Fix location:** `.github/workflows/CI.yml:92` (the `test` job's `cargo test ${{ matrix.features }}` step)
- **Claim:** No CI job in `.github/workflows/CI.yml` ever builds or executes `tests/ready_stream.rs`.
- **Trigger scenario:** CI runs on any push or pull request against the repository, exactly as it already does on every commit.
- **Verification status and evidence:** `primary-confirmed`; not independently verified (not a mandatory-verification trigger; see §1). Decisive evidence, all read directly, none executed (offline / no-cargo run condition):
  - `Cargo.toml:246` sets `required-features = ["full", "tracing"]` on the new test target — the only test/example/bench target in the whole file that requires anything beyond `"full"` (confirmed by grepping every other `required-features` line in `Cargo.toml`; all 26 others read `["full"]`).
  - `.github/workflows/CI.yml:65-92` (`test` job): `matrix.features` is `--features full` (stable/beta) or `--features full,nightly` (nightly) — never `tracing`. Per Cargo's documented `required-features` semantics, a target whose required features are not all enabled is silently skipped, not built and not run.
  - `.github/workflows/CI.yml:149-173` (`features` job): the only job that sets `RUSTFLAGS: "--cfg hyper_unstable_tracing"` and enables the `tracing` feature also passes `cargo hack --no-dev-deps check` — `--no-dev-deps` excludes dev-dependency-only targets (all test targets) from being compiled at all, and `check` never executes anything even for targets it does compile.
  - `src/trace.rs:5-11`: `#[cfg(all(not(hyper_unstable_tracing), feature = "tracing"))] compile_error!(...)` — confirms the `tracing` feature is genuinely gated behind the `RUSTFLAGS` cfg flag the PR body itself documents (`RUSTFLAGS='--cfg hyper_unstable_tracing' cargo test --test ready_stream --features full,tracing`), so no CI job can accidentally run it without deliberately combining both.
  - No other workflow file (`bench.yml`, `external-types.toml`) references `tracing` or `ready_stream`.
  - This claim required a cross-module trace (`Cargo.toml` + `.github/workflows/CI.yml`'s several jobs + `src/trace.rs`'s compile gate) to establish, which is exactly the bar `SKILL.md` step 3 sets for admitting an ordinary `consider` survivor without a verifier batch: I completed that reconstruction myself in the primary pass and consider it decisive, so no batch was needed to settle it.

### Finding 2 — `hyper/ready-stream-no-fail-signal`

- **Priority / action:** P2 / `consider` (`blocking=false`)
- **Kind:** `maintainability`
- **Anchor:** `tests/ready_stream.rs:241-248` (RIGHT) — the client receive loop and its trailing log line
- **Fix location:** `tests/ready_stream.rs:159` (inside the spawned watchdog task body)
- **Claim:** The new regression test has no way to fail cleanly: its receive loop asserts nothing about the bytes it collects, and its stall watchdog (`panic_task`) never calls `panic!`.
- **Trigger scenario:** `body_test` runs to completion (no assertion fires even on a wrong/truncated response), or — more importantly — the exact `poll_loop` write-starvation stall this PR fixes is reintroduced in a future change (the test then hangs with no diagnostic instead of failing fast).
- **Verification status and evidence:** `primary-confirmed`; not independently verified (single-file trace, not a mandatory trigger). Decisive evidence:
  - `tests/ready_stream.rs:241-248`:
    ```rust
    let mut bytes_received = 0;
    while let Some(chunk) = client_stream.recv().await {
        bytes_received += chunk.len();
    }
    server_task.abort();
    info!(bytes_received, "Client done receiving bytes");
    ```
    There is no `assert_eq!`/`assert!` anywhere in the function; `bytes_received` is only logged. `TOTAL_CHUNKS = 16` and `CHUNK_SIZE = 64 * 1024` are known constants (`tests/ready_stream.rs:210,220`), so `bytes_received == TOTAL_CHUNKS * CHUNK_SIZE` is a directly checkable invariant that the test does not check.
  - `tests/ready_stream.rs:152-166` (`TxReadyStream::poll_flush`): on the first of every pair of flushes, it spawns `self.panic_task = Some(tokio::spawn(async { tokio::time::sleep(Duration::from_secs(1)).await; }))` — the spawned future's body is only the sleep; there is no `panic!` call anywhere in the file. The comments (`// Spawn panic task if not already spawned`, `"Aborting panic (aka waker stand-in task)"`) name an intent (fail the test if the connection never becomes ready to flush) that the code does not implement.
  - `#[tokio::test(flavor = "multi_thread", worker_threads = 2)]` carries no timeout, so if the underlying stall this PR fixes reoccurred, `client_stream.recv()` at line 242 would block forever with no automatic failure signal from either the assertion or the watchdog.
  - I did not execute this test (no-cargo run condition for this cell); the trace above is a bounded semantics reading of the function's setup, call, assertions, and cleanup as the rubric's Changed Tests section requires, not a claim about what the test does when run.

Both findings render with the `Closing this without action is a correct response.` sentence (mandatory for `consider` findings per the output contract) and validate cleanly — see §6 for the exact `validate_review.py`/`--render`/`--emit-batch` transcript.

## 3. Complete private disposition ledger

| id | kind | disposition | decisive evidence | falsification / reason |
| --- | --- | --- | --- | --- |
| `hyper/ready-stream-ci-coverage-gap` | maintainability | **survivor** (primary-confirmed, `consider`/P2) | `Cargo.toml:246`; `.github/workflows/CI.yml:65-92,149-173`; `src/trace.rs:5-11` | n/a — survived; see Finding 1 |
| `hyper/ready-stream-no-fail-signal` | maintainability | **survivor** (primary-confirmed, `consider`/P2) | `tests/ready_stream.rs:152-166,241-248` | n/a — survived; see Finding 2 |
| `dispatch/poll-loop-write-retry-gap` | concurrency | dropped (consequence unproven) | `src/proto/h1/dispatch.rs:165-196,445-447`; `src/proto/h1/conn.rs:428-432,572-592` | Claim entertained: "the `wants_write_again = can_write_again() && conn_ready` predicate (body_rx.is_some() && last poll_flush was Ready) still leaves some interleaving where the connection can make write progress but neither `wants_write_again` nor `wants_read_again` is true, so `poll_loop` returns `Ready` and the task is never re-polled." Falsified by completing the available static legwork rather than by a decisive counter-fact: (a) `wants_read_again()` (`conn.rs:428`) is a genuine one-shot `notify_read` flag from `Conn`'s own state machine, and `can_write_again()` (`dispatch.rs:445`) is deliberately the coarser "is there still a body being written" check the PR author chose; (b) the only pathological scenario I could construct — a custom `poll_flush`/`poll_frame` that returns `Pending` once without arming a real waker, then becomes `Ready` on the very next poll — is exactly what `tests/ready_stream.rs`'s `TxReadyStream::poll_flush` models, and I traced it by hand (see §5): each `poll_loop` iteration calls `poll_flush` twice (once inside `Dispatcher::poll_write`'s internal `ready!(self.poll_flush(cx))?` when the write buffer is full, once again explicitly at `dispatch.rs:174`), so the pending/ready alternation the mock produces resolves to `Ready` within the *same* task poll without needing an external wake, before the bounded 16-iteration loop exhausts; (c) the maintainer's own pre-merge review comment explicitly names this exact invariant ("since we're essentially 'selecting' over read and write, we need to make sure both sides either registered a waker, or that we will poll again with the `yield_once` util") and approved the fix on that basis — under gate 6 this is acceptance of what the review record explicitly addresses, though I did not rely on it alone. I found no path where `dispatch.poll_msg` (a separate, unaffected waker source) or the body's own `poll_frame` (which arms its own waker when genuinely `Pending`) is left unaccounted for. This is `dropped (consequence unproven)` rather than an outright refutation: I could not construct a concrete failing state transition, but I also cannot claim exhaustive proof of the rule for every interleaving beyond the one tested — see §7's fix-sufficiency note and §10's judgment-call notes. |
| `dispatch/can-write-again-mut-self` | maintainability | dropped (no meaningful impact) | `src/proto/h1/dispatch.rs:445-447` (`fn can_write_again(&mut self) -> bool { self.body_rx.is_some() }`) vs. `dispatch.rs:449` (`fn is_done(&self) -> bool`, an analogous read-only predicate declared `&self` two lines later) | `can_write_again` takes `&mut self` but only reads `self.body_rx`; it could be `&self` like the structurally similar `is_done`. Dropped on gates 1/4/7: the method is private, called only from a context that already holds `&mut self`, so this has zero functional or call-site consequence — pure signature trivia. Considered routing to `Observations` but the rubric's Observations section says not to spend a slot preserving a candidate that fails admission on triviality alone when the fact itself carries no real interest; I judged this did not clear that bar and left it out of the summary entirely. |

No candidate reached `must-fix`; none involved security/authorization, data loss/corruption, destructive migration, or a compatibility break; none required a verifier. The `Issue fit` ledger (below) is separate from this candidate ledger and carries no `partial`/`not-verifiable` rows, so it produced no question either.

### Issue-fit ledger (rubric's "Issue fit" section; `issues=none`, built from PR title + body only)

| Row | Source | Class | Disposition | Evidence |
| --- | --- | --- | --- | --- |
| `poll_loop` must retry when write is ready even if read is not, or hyper may stall | `pr-body/"if the poll_write is demonstrating readiness to write and the connection has readiness to write, we should do that or else hyper may stall"` | acceptance requirement (PR promise of a concrete outcome) | **met** | `src/proto/h1/dispatch.rs:174,180,189,192` — `wants_write_again` is computed and OR'd into the loop's continue condition alongside `wants_read_again` |
| A pathological repro (`ready_stream.rs`) demonstrating the bug exists and is runnable with the documented command | `pr-body/"I built a pathological example \"ready_stream.rs\" - you can run it from this branch with: RUSTFLAGS=... cargo test --test ready_stream --features full,tracing"` | supporting assertion | **met** | `tests/ready_stream.rs` exists (249 lines, new file); `Cargo.toml:243-246` registers it under exactly the stated feature/cfg combination |

Neither row is `partial` or `not-verifiable`, so the Issue fit ledger produced no question under the static-unresolvability rule.

## 4. Sub-agent dispatches

**None.** No verifier batch was dispatched (§1, §7). There is no exact prompt or verbatim report to reproduce for this cell.

## 5. Everything consulted beyond the diff

All of the following were read from the offline clone at `/tmp/effort124/runs/a-high-seed2-att-04` (branch `review-head`, checked out at the pinned head `f2aa734e5699a91fc20f1178e38af7b1e374bdbc`; branch `master` pinned to the merge-base `f9f8f44058745d23fa52abf51b96b61ee7665642`) unless noted otherwise. No command executed cargo/rustc/miri/loom; every read below is a plain file read, `git show`, or `grep`.

1. **Skill snapshot** (`/tmp/effort124/skill/skills/code-review-publish/`): `SKILL.md`, `references/review-rubric.md`, `references/output-contract.md`, `references/verifier.md`, `references/verifier-concurrency.md` — read in full before doing anything else. (`references/re-review.md` and `references/conformance.md` were *not* read: re-review does not apply because the posting identity `kamui` has no prior comment/review on the PR per the packet, and no versioned artifact is referenced by any source, so conformance does not apply.)
2. **Phase-1 packet** (`/tmp/effort124/packets/a/packet.md`): read in full; every pinned fact (head/base/merge-base SHAs, PR body, commit list, prior-review transcript, repository-guidance table, run conditions) taken verbatim, not re-resolved.
3. `git branch -a`, `git log --oneline -5 review-head`, `git status` in the clone — to confirm the pinned branches/head and a clean tree before touching anything. This only looked *backward* from the pinned head (older, already-merge-base-side commits `f9f8f440`, `5803a9c0`, `e1e1f2b4`); it did not attempt to read anything newer than the pinned head, and nothing newer exists in this truncated clone.
4. `git show master:CONTRIBUTING.md` — the one repository-guidance file the packet's table marks present at the merge-base. Read in full (short file). Classified as a general contributor-onboarding index (links to `docs/PULL_REQUESTS.md`, `docs/COMMITS.md`, etc., which are themselves excluded from the digest's `guidance` set and from consideration here as "merely linked from an included instruction file"); it states no repository-specific coding standard, invariant, or verification requirement applicable to `Cargo.toml`, `src/proto/h1/dispatch.rs`, or `tests/ready_stream.rs`, so it produced no repository-rule finding.
5. `git show master:docs/agents/issue-tracker.md` — exit `fatal: path 'docs/agents/issue-tracker.md' does not exist in 'master'`, confirming its absence (SKILL.md step 1 names this file; the packet's guidance table doesn't list it, and I independently confirmed the negative rather than only trusting the table).
6. `python3 scripts/review_context.py --merge-base f9f8f44058745d23fa52abf51b96b61ee7665642 --head f2aa734e5699a91fc20f1178e38af7b1e374bdbc --store <private mktemp -d>/review-context-f2aa734e5699a91fc20f1178e38af7b1e374bdbc.json` — run exactly once from inside the clone, exit 0. Diff was `withheld` (26769 bytes across 3 chunks vs. a 22791-byte remaining bound); manifest, ranges, and history sections printed whole. Recovered per SKILL.md step 2's instructions with two further `--from` reads against the same store, no rebuild:
   - `--from <store> --path Cargo.toml --path src/proto/h1/dispatch.rs` (both fit one bound together) — printed the complete diff for both files with `--function-context`-equivalent enclosing context; chunk inventory afterward showed `2/3 consumed`.
   - `--from <store> --path tests/ready_stream.rs` — printed the complete new-file diff; chunk inventory afterward showed `3/3 consumed` (diff coverage complete).
   The private store path was created with `mktemp -d` outside the working tree and used consistently for both recovery reads, per the read-discipline the reference specifies.
7. `sed -n '1,80p' Cargo.toml` and `sed -n '220,260p' Cargo.toml` (head) — to see the `[dev-dependencies]` and `[[test]]` sections in full surrounding context (the diff hunks alone don't show the section headers), confirming `tracing-subscriber = "0.3"` landed under `[dev-dependencies]` (not a production dependency) and that the new `[[test]]` block sits alphabetically between `integration` and `server`, matching the file's existing ordering convention.
8. `grep -n -B2 -A2 "required-features" Cargo.toml` — batched, single search, case-sensitive (the token has one fixed casing in TOML keys; a case-insensitive search would not have found anything different) confirming `ready_stream` is the only one of 27 `required-features` declarations in the file that names anything beyond `["full"]`.
9. `grep -rn "hyper_unstable_tracing" --include="*.rs" --include="*.toml" -i .` (repo-wide, case-insensitive) — located every reference to the cfg flag: `Cargo.toml:104,110` (rustdoc-args), `src/lib.rs:63,68` (doc comment), `src/trace.rs:5,9` (the `compile_error!` gate). This is the search that established the `tracing` feature's compile-time gate.
10. `ls .github/workflows/` and `grep -rln "fmt" .github/workflows/` then `grep -rn "tracing" .github/workflows/*.yml` (repo-wide within the workflows directory, case-sensitive) — located every CI reference to `tracing`/`ready_stream`; confirmed no other workflow file (`bench.yml`, `external-types.toml`) mentions either.
11. `sed -n '1,260p' .github/workflows/CI.yml` and `sed -n '260,400p' .github/workflows/CI.yml` — read the entire CI workflow file (it is short enough to read whole; this is the "current CI" SKILL.md step 3 directs the reviewer to read) to enumerate every job's feature/`RUSTFLAGS` combination: `style` (rustfmt --check), `test` (matrix: `--features full` / `full,nightly`, no tracing, no RUSTFLAGS), `msrv` (`--features full`), `miri` (`http1,http2,client,server,nightly`, no tracing), `features` (`cargo hack --no-dev-deps check --feature-powerset ... --features tracing` with `RUSTFLAGS: "--cfg hyper_unstable_tracing ..."` — the only job with the cfg flag, but `--no-dev-deps check`, never `test`), `ffi`/`ffi-header`/`ffi-cargo-c`/`doc`/`check-external-types`/`udeps`/`minimal-versions`/`semver` (none touch tracing or dev-test targets relevantly). This full read is what established Finding 1.
12. `Read src/trace.rs` in full (129 lines, under the 300-line whole-file threshold) — confirmed the exact `compile_error!` condition (`all(not(hyper_unstable_tracing), feature = "tracing")`) gating the `tracing` feature, and that every `trace!`/`debug!`/etc. macro used inside `dispatch.rs` (e.g. the unchanged `trace!("poll_loop yielding ...")` at the tail of `poll_loop`) is itself feature-gated the same way, confirming the new test's dependence on the unstable cfg flag is real and repo-wide, not specific to the test file.
13. `grep -n "wants_read_again\|fn wants_write_again\|can_buffer_body\|can_write_body\|can_write_head" src/proto/h1/conn.rs` then `sed -n '415,445p;565,600p' src/proto/h1/conn.rs` — a targeted, risk-led-discovery bounded read of `Conn`'s state-predicate methods (`wants_read_again`, `can_write_head`, `can_write_body`, `can_buffer_body`), not touched by the diff, to decide whether the new `can_write_again()` predicate at the `Dispatcher` level is a sound analogue of the existing read-side predicate. Risk served: concurrency/select-over-read-and-write correctness (the risk signal list's "retries, idempotency, partial failure, stale state, and concurrency" item). Decisive outcome: `wants_read_again` is a genuine one-shot `notify_read` flag maintained by `Conn`'s own state machine (`conn.rs:428-432`), a materially different and more precise mechanism than the new `can_write_again`'s `body_rx.is_some()` check — an asymmetry I traced through rather than assumed, and did not find to constitute a gap (see ledger row `dispatch/poll-loop-write-retry-gap`).
14. `grep -n "mod tests\|#\[test\]\|#\[tokio::test\]" src/proto/h1/dispatch.rs` then `sed -n '719,821p' src/proto/h1/dispatch.rs` — read the three pre-existing unit tests in `dispatch.rs`'s own `mod tests` (`client_read_bytes_before_writing_request`, `client_flushing_is_not_ready_for_next_request`, `body_empty_chunks_ignored`). These are unmodified by the diff (outside the changed line ranges the manifest reports), so the rubric's Changed Tests section does not apply to them; read only to confirm none of them directly exercises `poll_loop`'s retry predicate in a way that the change could have silently broken. None does (they test client-side read-before-write ordering, client flush/backpressure signaling, and empty-chunk body handling — none constructs the write-ready-but-not-read-ready scenario this PR addresses).
15. `grep -n "ready_stream\|tracing" .github/workflows/*.yml .github/workflows/*.toml` (repeat, repo-wide within workflows, case-sensitive) and `grep -n "panic_task\|flush_count\|Aborting panic\|Spawn panic" tests/ready_stream.rs` — batched searches to pin exact line numbers for the trailers/anchors in the two findings.
16. `grep -n "fn poll_loop\|wants_write_again\|wants_read_again\|fn can_write_again\|conn_ready" src/proto/h1/dispatch.rs` — final line-number confirmation for the report's citations (`dispatch.rs:165,174,180,189,192,445`).

No test was executed (run condition 2 forbids cargo/rustc/miri/loom in any form for this cell); every "Changed Tests" conclusion above is a bounded semantics trace of `tests/ready_stream.rs`'s `body_test`, stated as such, never implied to be a pass or fail from execution.

## 6. Context digest

Computed once, per SKILL.md step 3 / output-contract.md, from the packet — not from a `forge_packet.py normalize` JSON (none exists in this offline cell; no forge fetch was performed, per the run conditions, and the packet substitutes for phase 1 in full). I supplied `pr.title`/`pr.body` directly from the packet's pinned PR title and body, `issues: []` (packet section 1: "Originating issue(s): none"), `specs: []` (no user-supplied spec), and `guidance: []` (packet section 7: no root/path-scoped `AGENTS.md`/`CLAUDE.md`, no root `CONTEXT.md` at the merge-base; `CONTRIBUTING.md` is not a member of the digest's `guidance` category list per `output-contract.md`'s exhaustive membership rules).

Input (`/tmp/effort124/work/a-high-seed2-att-04/fingerprint_input.json`):

```json
{
  "pr": {
    "title": "fix(http1): poll_loop writes when ready",
    "body": "I ran into some lockups running hyper with some custom futures. If one of my futures is ready when polled, the waker is never signaled and I think this uncovered a logical issue with the http1 poll_loop. That it to say, **if the poll_write is demonstrating readiness to write and the connection has readiness to write, we should do that or else hyper may stall**.\n\nI built a pathological example \"ready_stream.rs\" - you can run it from this branch with: `RUSTFLAGS='--cfg hyper_unstable_tracing' cargo test --test ready_stream --features full,tracing`.\n\nI provided a proposed patch for the poll_loop, but I'm open to other angles on this."
  },
  "issues": [],
  "specs": [],
  "guidance": []
}
```

Command: `python3 scripts/context_fingerprint.py /tmp/effort124/work/a-high-seed2-att-04/fingerprint_input.json`

Digest: `13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5`

This value appears in the run trailer of both the payload and the batch below (`context=13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5`).

### Validation transcript

```
$ python3 scripts/validate_review.py --render < payload.json
anchor [`Cargo.toml:243-246`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/Cargo.toml?plain=1#L243-L246); fix [`.github/workflows/CI.yml:92`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/.github/workflows/CI.yml?plain=1#L92)
anchor [`tests/ready_stream.rs:241-248`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L241-L248); fix [`tests/ready_stream.rs:159`](https://github.com/hyperium/hyper/blob/f2aa734e5699a91fc20f1178e38af7b1e374bdbc/tests/ready_stream.rs?plain=1#L159)
(exit 0)

$ python3 scripts/validate_review.py < payload.json
(no output, exit 0 — zero violations)

$ python3 scripts/validate_review.py --emit-batch < payload.json > batch.json
(exit 0; batch.json holds the one-call review body reproduced verbatim in the payload report)
```

First `--render`/`validate` attempt without the trailing `Closing this without action is a correct response.` sentence failed with `items[0]: field-order: ...` / `items[1]: field-order: ...` (both `consider` findings were missing the mandatory closing sentence); fixed by appending it after `Change` in both findings' markdown, then re-validated clean. That is the only violation encountered and fixed in this run.

Immediately after the final exit-0 validation, ran `python3 /tmp/effort124/mark_event.py /tmp/effort124/reports/a/a-high-seed2-att-04-timing.json payload_validated_at` as instructed; the sidecar now reads `payload_validated_at: "2026-09-06T08:42:32.314871+00:00"`.

## 7. Mechanism checklist

- **Question channel:** did not fire. Both Issue-fit ledger rows are `met` (§3); no candidate's settling fact was statically unresolvable in a way that could change the merge decision. No question was drafted or dropped.
- **Clean-verdict or related-acquittal verification:** did not fire, in either mode. Zero-survivor mode requires zero candidates surviving as findings — two survived — so it never applied, regardless of the diff's concurrency surface. Related-acquittal mode requires an initial candidate batch to be dispatched — none was, because no candidate met a mandatory-verification trigger — so it never applied either. No row was re-opened; there is nothing to re-open.
- **Observations:** did not fire. One candidate (`dispatch/can-write-again-mut-self`, §3) was seriously considered for the Observations channel — it is accurate and has a decisive pointer — but I judged it failed the Observations section's own bar ("the fact itself must stand") because it has no consequence at all (a private, single-call-site method's `&mut self` vs `&self` signature), and elected not to spend a slot on it. Zero observations were published; this was a deliberate exclusion, not an omission I overlooked.
- **Fix-sufficiency check on the concurrency candidate:** partially applicable. `dispatch/poll-loop-write-retry-gap` (§3) was dropped before reaching `confirmed`, so it never went to a verifier and `verifier-concurrency.md`'s formal bug-class procedure (state the invariant at rule level; ask the shutdown-vs-steady-state question; enumerate sibling interleavings before sibling paths; enumerate sibling code paths; widen `change` to the rule) was never run as a verifier task. I did informally apply the same discipline in primary falsification: I named the invariant at rule level ("every path that returns `Poll::Pending` from `poll_loop` must have registered a wake, directly or by re-entering the loop, for every actor — read side and write side — that could make the connection progress"), I asked whether the failing interleaving needs shutdown/teardown (no — the PR's own scenario is steady-state: an in-flight response body write, no shutdown involved) and traced a steady-state interleaving to a `holds` verdict by hand (§5 item 13, §3's ledger row), and I did enumerate the two concurrent actors sharing the rule (the read side via `wants_read_again`'s `notify_read` flag, and the write side via `can_write_again`'s `body_rx.is_some()` check) rather than treating them as one. I did not enumerate every sibling code path beyond `poll_write`'s body-writing branch (e.g., the pipelined-next-head-write branch, which I reasoned is governed by `dispatch.poll_msg`'s own independent waker and out of scope, but did not exhaustively re-derive from first principles for every state). This is a real, disclosed limit of primary-only falsification without a verifier batch — see §10.
- **Follow-up verifier round:** did not fire — there was no initial batch to follow up.
- **Deferral handling:** one explicit deferral is on the record and was tracked. `lthiery`'s pre-merge thread comment ("I'll still take another critical pass at what I've done here next week and I'll see what I can do to simplify") followed by `seanmonstar`'s "Yea, hm, if it's a complicated edge case, perhaps that's fine as-is, then." I read this as the review record closing on the specific concern raised there — test complexity/simplifiability — as an accepted trade-off (gate 6: a maintainer's approval establishes acceptance of what the record explicitly addresses), not as an open deferred question, since the final exchange reads as resolution rather than postponement. I deliberately did **not** raise a "this test is too complex" finding on that basis. I did **not** treat this acceptance as covering either of my two published findings: neither the CI-never-runs gap nor the missing-assertion/missing-panic defect was ever mentioned in that thread, so gate 6 does not block them.
- **Retrospective mode:** fired as instructed. The summary includes `**Mode:** Retrospective review of merged pull request; publication disabled.` (mandatory whenever `merged` is true per output-contract.md, regardless of how the target was supplied); no external write of any kind was attempted; SKILL.md step 6 was followed through to the point of producing the `--emit-batch` output and then stopped, per the packet's run condition 4.

## 8. History discipline

I read history only as follows, and never anything newer than the pinned head (`f2aa734e5699a91fc20f1178e38af7b1e374bdbc`), which does not exist locally in any case (the clone is truncated there by design):

- `git branch -a` — listed `master`, `review-head`, and their `origin/*` remotes (local filesystem remote, not `github.com`).
- `git log --oneline -5 review-head` — showed the pinned head and four older commits back to the merge-base and one commit before it (`f9f8f440`, `5803a9c0`, `e1e1f2b4`), all already reachable and already implied by the merge-base pin; this is normal ancestor context, not a probe beyond the pinned point.
- `git status` — confirmed a clean working tree on `review-head` before any reads.
- `git show master:CONTRIBUTING.md` and `git show master:docs/agents/issue-tracker.md` — base-branch blob reads at the pinned merge-base SHA (via the `master` branch, which the harness force-pinned to the merge-base), not history traversal.
- `scripts/review_context.py`'s own `## history` section (part of its normal output, not a separate command I ran) printed the last commit touching each changed path *before* the merge-base (`Cargo.toml`: `400bdfda`, `caa166c7`, `e11b2ad9`; `src/proto/h1/dispatch.rs`: `e11b2ad9`, `0bd4adfe`, `4ffaad53`) — this is the tool's built-in "pre-merge-base history" feature for context, not an extra git command I issued, and it is bounded to *before* the merge-base, i.e., still not beyond the pinned head.

I did not run `git log` on any commit after the pinned head, did not `git fetch`/`git pull`, and did not attempt to reach anything the packet's run condition 3 says does not exist locally.

## 9. Sandbox disclosure

One incidental exposure to disclose: `ls -la /tmp/effort124/reports/a/` (run once, early, to see what already existed at my own output paths before writing to them) listed the **names** of other cells' output files in the same shared reports directory — `a-high-seed1-att-01-{meta.json,payload.md,run.md,session.txt,timing.json}` and `a-medium-seed1-att-02-{...}` and `a-medium-seed2-att-03-{session.txt,timing.json}`. I did not open, `cat`, `grep`, or otherwise read the *contents* of any of those files, and I do not know what they contain beyond their filenames and sizes shown by `ls -la`. I disclose the directory listing itself per rule 7 ("report any other path you read") out of caution, even though no content from another run's clone, report, or payload was read. No other path outside the clone (`/tmp/effort124/runs/a-high-seed2-att-04`), the skill snapshot, the packet directory, my work directory (`/tmp/effort124/work/a-high-seed2-att-04`), and my own report/payload/timing paths was touched.

## 10. Notes — judgment calls on the skill's contract

1. **No packet.json / forge_packet.py normalize output exists in this cell.** `output-contract.md`'s digest recipe assumes either `--packet packet.json` (from a real forge fetch) or direct `pr`/`issues`/`specs`/`guidance` JSON "on a forge without that packet." I treated this offline, packet.md-only cell as the latter case and supplied the fields directly from the packet's pinned title/body/guidance table, since re-fetching is explicitly forbidden by the run conditions and the packet explicitly stands in for phase 1. I consider this the only reading consistent with rule 1 ("offline... your skill's phase 1 asks you to resolve the target from the forge, that phase is satisfied by this packet").
2. **`guidance: []` for the digest, despite `CONTRIBUTING.md` being present at the merge-base.** `output-contract.md`'s membership rules for the digest's `guidance` field are exhaustive and name only root/path-scoped `AGENTS.md`/`CLAUDE.md` and root `CONTEXT.md`. `CONTRIBUTING.md` is not in that list, so it is excluded from the digest even though the rubric's separate "Repository rules" section directs me to *apply* it (which I did, finding nothing applicable). I treated these as two independent obligations — compute the digest per its own exhaustive list, and separately consult repository guidance per the rubric — rather than reconciling them, since the skill draws that boundary explicitly.
3. **Treating the `dispatch/poll-loop-write-retry-gap` candidate as "dropped" rather than continuing to chase it into a verifier batch.** The rubric's Falsify section allows dropping "when decisive evidence contradicts it or the reviewer has not completed the available static legwork." I judged the static legwork complete (traced the relevant `Conn` predicates, the exact pathological scenario the merged test encodes, and the maintainer's own review comment) without finding either a decisive contradiction or a decisive confirmation. Absent a `must-fix`-caliber claim I could stand behind, I did not manufacture one merely to trigger verification — SKILL.md is explicit that verification is consequence-triggered, not a checkbox to exercise regardless of whether a candidate earns it.
4. **Merging what could have been two test-quality candidates (no assertion; watchdog never panics) into one finding.** Both live in `tests/ready_stream.rs` and compound the same observable consequence ("this test cannot fail cleanly"), so I treated them as one discrete, actionable defect per the rubric's Comment quality section ("Use one comment per distinct defect") rather than two, while still citing both locations as the two allowed decisive evidence facts.
5. **Not treating the PR's own repro instructions (`RUSTFLAGS=... cargo test --test ready_stream --features full,tracing`) as satisfying "the author already knows and accepts this."** The PR body only claims the test is *runnable* with that command; it never claims or implies that CI *does* run it that way. I did not read the author's manual-repro instructions as foreclosing Finding 1 under gate 6, since the review record (including the three review submissions and the two threads) never discusses CI wiring at all.
6. **Priority calibration (P2, not P1 or P3, for both findings).** Neither finding threatens the correctness of the already-merged, already-scrutinized production fix; both concern the durability of the *regression test's* protective value. I set P2 rather than P3 because the concrete risk each guards against (a silent reintroduction of a real production stall bug) is significant even though the finding itself is about tooling rather than runtime behavior; I set P2 rather than P1 because there is no live, current-state defect in shipped behavior — only reduced future detection coverage.
