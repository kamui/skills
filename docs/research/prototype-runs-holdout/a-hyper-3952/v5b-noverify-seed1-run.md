# Run document — holdout target (a), cell `v5b-noverify-seed1`

**Orchestrator metadata (added after the run; the researcher's record, not the reviewer's).**

| | |
| --- | --- |
| Packet | `packets/a/packet.md`, SHA-256 `c94a8d3ed431594d9acd0803bac2558d9227aa58733404f1a5fd416a6e3bf1f2` |
| Root agent / primary | `a16d8a35655d7a321` / `a16d8a35655d7a321` |
| Payload | [`v5b-noverify-seed1-payload.md`](v5b-noverify-seed1-payload.md), 5672 bytes |
| Report (this file, below the preamble) | 35101 bytes as written by the reviewer |
| Closed out | 2026-09-04T21:37:43.350174+00:00 |
| Problems at close-out | none |

## Model and effort verification (every assistant line of every transcript)

| Agent | Role | Definition | `message.model` | `effort` | Transcript |
| --- | --- | --- | --- | --- | --- |
| `a16d8a35655d7a321` | primary | general-purpose | `claude-sonnet-5`×129 | `high`×129 | `agent-a16d8a35655d7a321.jsonl` |

## Billed usage (`transcript_usage.py --prices 2,10 --report <this report>`)

```
agent-a16d8a35655d7a321.jsonl
turns                        68 (API requests; 129 assistant lines)
tool calls                   70
text-only turns               1
input                       136 tokens (uncached)
cache write             159,810 tokens
cache read            6,299,290 tokens
output                   83,959 tokens (thinking 53,916)
models             claude-sonnet-5
wall                    0:17:44
cost                       2.50 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

TOTAL
turns                        68 (API requests; 129 assistant lines)
tool calls                   70
text-only turns               1
input                       136 tokens (uncached)
cache write             159,810 tokens
cache read            6,299,290 tokens
output                   83,959 tokens (thinking 53,916)
models             claude-sonnet-5
wall                    0:17:44 (summed over transcripts)
cost                       2.50 $ at 2/10 per M, cache write ×1.25, cache read ×0.1
production-shaped          2.41 $ (output 75,184 after subtracting the report's 8,775 est. tokens)
```

Row for `comparison-data.md`:



| (a) v5b-noverify seed 1 | claude-sonnet-5 | 68 | 70 | 1 | 136 | 159,810 | 6,299,290 | 83,959 | 53,916 | 0:17:44 | 2.50 | 8,775 | **2.41** |

Per agent:

| primary a16d8a35655d7a321 | claude-sonnet-5 | 68 | 70 | 1 | 136 | 159,810 | 6,299,290 | 83,959 | 53,916 | 0:17:44 | 2.50 | — | — |



---

# Research report — cell `a/v5b-noverify-seed1`

Target `hyperium/hyper#3952`, arm `v5b-noverify (ablation: verification disabled)`, seed 1.
Skill pin: `legacy reviewer` at `main 2f06662 minus references/verifier.md (workflow=v5b-1, ablation)`.
Dispatch: `/tmp/holdout/dispatch/a/v5b-noverify-seed1.md`.

The complete rendered review (summary + finding comments) is at
`/tmp/holdout/reports/a/v5b-noverify-seed1-payload.md`. This file is the run record.

---

## 1. Metadata

| Field | Value |
| --- | --- |
| Target | `hyperium/hyper#3952` — "fix(http1): poll_loop writes when ready" |
| Arm | v5b-noverify (ablation: verification disabled), workflow=v5b-1 |
| Seed | 1 |
| Skill pin | `/tmp/holdout/skills/v5b-noverify/` (`main 2f06662` minus `references/verifier.md`) — confirmed absent: `ls references/` shows only `output-contract.md`, `re-review.md`, `review-rubric.md` |
| Model — primary reviewer (me, this context) | `claude-sonnet-5`, as instructed. No model-selection tool of my own to introspect; reporting the model named in the dispatch and trusting the harness ran it as configured. |
| Model — sub-agents | **None spawned.** See §4. |
| Verification trigger fired? | **No.** See §7 for the full reasoning: neither finding is `must-fix`, security, data-loss/corruption, destructive-migration, or an externally observable compatibility break, so neither candidate meets the mandatory-verification bar; it was not zero-survivor mode (two candidates survived as findings); and related-acquittal mode never activates because no initial batch was ever dispatched. The one `concurrency`-kind candidate raised (the `poll_loop` fix itself) was **dropped** in primary falsification, not a survivor, so it never entered the must-fix/security/etc. set either. Consequently the ablation's "verifier unavailable → withhold + incomplete coverage" fallback **was not invoked**, because nothing in this run's candidate set ever required a verifier. This is a judgment call; see §10. |
| Candidates raised | 8 (see full ledger, §3) |
| Candidates surviving primary falsification | 5: 2 `must-fix`-eligible-check-passed `consider` findings, 3 `observation`s |
| Verifier verdicts | None — no verifier ran (ablation; also none was ever triggered — see above) |
| Findings for publication | 2, both `[P2] [consider]`, kind `maintainability`, `blocking=false` |
| Questions | 0 |
| Observations | 3 (at the output contract's cap) |
| Coverage | **Complete** — all 3 changed files reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs`, `tests/ready_stream.rs`); every rubric risk-directed check given an evidence-backed outcome (§5); no unresolved input, no fetch failure (packet supplied everything; run was offline as required) |
| Derived status | `Approved (advisory)` — 0 unsettled must-fix, coverage complete, 0 open questions. `(advisory)` suffix added because the event is `COMMENT` (no gating authorization was given; this is also a third-party, non-self review of a merged PR, so `COMMENT` applies regardless) |
| My own token usage | The harness does not report token usage to me in this context; I have no figure to give. |
| Wall clock | Not instrumented at task start. Two timestamps captured mid-run: `2026-09-04T21:29:49Z` (after context-script run, before payload assembly) and `2026-09-04T21:33:44Z` (after validation passed). Total elapsed time from dispatch start to report completion was longer than that 4-minute window because it includes the initial reading of the dispatch, skill, and packet beforehand; I did not capture a start timestamp, so I cannot give a precise total. |

---

## 2. Findings that survive, in full

Both are rendered verbatim (prose + trailer) in the payload file. Repeated here per the report's own requirement.

### Finding 1 — `hyper/ready-stream-ci-wiring`

- **Priority/action:** P2 / consider (`blocking=false`)
- **Kind:** maintainability
- **Anchor:** `Cargo.toml:243-246` (RIGHT) — the new `[[test]] name = "ready_stream" ... required-features = ["full", "tracing"]` block
- **Fix location:** `.github/workflows/CI.yml:92` — the `test` job's `run: cargo test ${{ matrix.features }}` line
- **Claim:** The new regression test is not compiled or run by any CI job.
- **Trigger scenario:** CI's `test` job (the only job in the workflow that runs `cargo test`) invokes it with `matrix.features: --features full`. `full` does not include the `tracing` feature (`Cargo.toml`'s `full = ["client","http1","http2","server"]`), and no RUSTFLAGS is set there.
- **Verification status and evidence:**
  - `required-features = ["full", "tracing"]` (`Cargo.toml:243-246`) — a Cargo test target whose required features are not all enabled under the invoking `cargo test` command is silently skipped (well-established, stable Cargo behavior; not something I could execute here, but it is not in dispute).
  - `src/trace.rs:5-9`: `#[cfg(all(not(hyper_unstable_tracing), feature = "tracing"))] compile_error!(...)` — building the `hyper` crate itself with `--features tracing` **without** `RUSTFLAGS='--cfg hyper_unstable_tracing'` fails to compile at all (this is unconditional; `mod trace;` in `src/lib.rs:108` is not itself feature-gated). So even enabling `tracing` in the `test` job's feature list without also setting the RUSTFLAGS would break the whole job, not just skip the one test.
  - `.github/workflows/CI.yml`: read in full (339 lines, all jobs: `ci-pass`, `style`, `test`, `msrv`, `miri`, `features`, `ffi`, `ffi-header`, `ffi-cargo-c`, `doc`, `check-external-types`, `udeps`, `minimal-versions`, `semver`). Only the `features` job ever sets `RUSTFLAGS: "--cfg hyper_unstable_tracing..."` together with the `tracing` feature (line 173), but that job runs `cargo hack --no-dev-deps check --feature-powerset --depth 2 --features tracing --skip ffi` (line 171) — `check`, not `test`, and `--no-dev-deps` explicitly excludes dev-dependencies and dev-only targets (the `tests/` directory), so it never builds `tests/ready_stream.rs` either. No other job combines `cargo test`, `--features ...tracing`, and the RUSTFLAGS.
  - Also checked: the PR body's own documented run command (`RUSTFLAGS='--cfg hyper_unstable_tracing' cargo test --test ready_stream --features full,tracing`) is exactly the combination missing from CI — this is a manual-only invocation the author documented for humans, not something CI performs.
  - `dispatch.md`/skill rubric note: this is squarely a new-test-file hygiene finding under the general "worth the author's time / proportionate rigor" gates (rubric's enumerated hygiene bullets are examples, not exhaustive; this is the same class of concern — a new test whose only invocation path bypasses the project's actual verification pipeline).

### Finding 2 — `hyper/ready-stream-no-timeout`

- **Priority/action:** P2 / consider (`blocking=false`)
- **Kind:** maintainability
- **Anchor:** `tests/ready_stream.rs:242-244` (RIGHT) — `while let Some(chunk) = client_stream.recv().await { bytes_received += chunk.len(); }`
- **Fix location:** same (omitted from trailer since anchor == fix)
- **Claim:** The new pathological regression test has no timeout guard around its response-read loop.
- **Trigger scenario:** the exact class of bug this PR fixes — a write-ready future whose waker is never signaled — recurs in a future edit to `poll_loop`.
- **Verification status and evidence:**
  - `tests/ready_stream.rs:242-244`, read in full as part of the new file (already complete in the diff, `new=yes` per the context script's manifest — no separate re-read needed): the client-side read loop has no `tokio::time::timeout`, no `#[tokio::test(..., timeout = ...)]`-equivalent, nothing bounding it.
  - Established sibling convention, checked via `grep -c timeout tests/server.rs tests/client.rs tests/integration.rs`: `server.rs` 21 occurrences, `client.rs` 29 occurrences, `integration.rs` 1 occurrence, virtually all wrapping comparable connection-completion waits in `tokio::time::timeout(Duration::from_secs(N), ...)` (e.g. `tests/client.rs:2388`, `tests/server.rs:2389`, `tests/server.rs:2782`). `grep -n timeout tests/ready_stream.rs` returns nothing.
  - Consequence, demonstrated rather than speculated: this specific test exists to catch a stall/deadlock. Without a bound, the one failure mode it is built to detect is exactly the failure mode that makes it hang instead of fail — the weakest possible signal for the exact regression it is meant to guard against, and (combined with Finding 1, if fixed in isolation) a hang in CI is a much worse failure experience than a clean assertion failure.

---

## 3. Complete private disposition ledger

One row per candidate raised, in the order encountered. `disposition` is one of `survivor` (published as a finding), `observation` (published in the summary's Observations section), or `dropped` (not published).

| id | kind | disposition | claim (one line) | decisive evidence pointer | falsification / routing reason |
| --- | --- | --- | --- | --- | --- |
| `dispatch/poll-loop-write-wake` | concurrency | dropped | The new `wants_write_again` gate could still leave a path where neither the read nor the write side registers a waker before `poll_loop` returns `Ready(Ok(()))`, reintroducing (a narrower form of) the deadlock the PR fixes. | `src/proto/h1/dispatch.rs:165-198` | Traced every exit path of the loop body exhaustively (see §5 "poll_loop trace"): the only way to hit `return Poll::Ready(Ok(()))` is `wants_write_again == false && wants_read_again == false`, and `wants_write_again == false` splits into `can_write_again()==false` (nothing left to write — no waker needed) or `conn_ready==false` (the just-executed `poll_flush` returned `Pending`, which by the `Poll` contract obliges the transport to have already registered a waker). Both sub-cases are covered; there is no third path. This exactly matches the invariant `seanmonstar` states in the 2025-10-28 review ("we need to make sure both sides either registered a waker, or that we will poll again with the `yield_once` util"). No bug found; falsified. |
| `dispatch/can-write-again-mut-self` | maintainability | observation | `can_write_again(&mut self)` takes `&mut self` though its body only reads `self.body_rx`. | `src/proto/h1/dispatch.rs:444-447` | Fails gate 1 (meaningful impact — negligible; no behavior, ownership, or borrow-checker consequence demonstrated) and gate 7 (worth the author's time is marginal for a private one-line helper). Accurate and decisive, so routed to `Observations` rather than dropped outright. |
| `tests/ready-stream-shared-duplex-fixture` | maintainability | dropped | `tests/ready_stream.rs`'s custom `TxReadyStream` reimplements an in-memory transport instead of reusing `tests/client.rs`'s `tokio::io::duplex`/`setup_duplex_test_server` convention. | Review thread comments, `tests/ready_stream.rs:18` on commit `f2aa734e5` (2025-10-28 through 2025-10-31) | Falsified on two independent grounds: (1) rubric gate 6 — the review record explicitly discusses this exact question (`lthiery`, 2025-10-31: a `tokio::io::duplex`-based fixture "can't" deterministically reproduce the pathological once-Pending-then-ready sequence the test needs; `seanmonstar`, 2025-10-31: "if it's a complicated edge case, perhaps that's fine as-is, then" — read as acceptance, not as leaving the question open; see §10 for the alternate reading I considered and rejected). (2) Independently, `grep -rln 'duplex\|InMemory\|mock\|DuplexStream\|tokio::io::duplex' tests/*.rs tests/support/*.rs` shows the duplex helper (`setup_duplex_test_server`) is local to `tests/client.rs`'s own test module, not exported from `tests/support/`, so there is no actual shared/support-module convention being bypassed — the rubric's "declared but unused shared fixture" hygiene check does not even apply here. |
| `hyper/ready-stream-ci-wiring` | maintainability | **survivor** | The regression test is never built or run by any CI job. | `Cargo.toml:243-246`, `.github/workflows/CI.yml` (all 339 lines read), `src/trace.rs:5-9` | Passes all 8 admission gates; see §2, Finding 1. |
| `hyper/ready-stream-no-timeout` | maintainability | **survivor** | The regression test's response-read loop has no timeout, so the exact regression it exists to catch makes it hang instead of fail. | `tests/ready_stream.rs:242-244`; sibling convention counts in `tests/server.rs` (21), `tests/client.rs` (29) | Passes all 8 admission gates; see §2, Finding 2. |
| `tests/ready-stream-colon-spacing` | maintainability | observation | `TxReadyStream`'s `poll_since_write:bool,` field (one field in a six-field struct) omits the space after the colon that every sibling field has. | `tests/ready_stream.rs:23` (vs. lines 20-25 for the siblings) | Fails gate 1 (no functional consequence) and is plausibly not even caught by `cargo fmt --check` — `rustfmt` has a known limitation formatting the bodies of arbitrary macro invocations, and this struct is declared inside `pin_project! { ... }`, so I could not establish with static reading alone whether CI's `style` job would actually flag it (no execution permitted). Routed to `Observations` as an accurate, decisive, in-diff-provable inconsistency rather than asserted as a CI-failing finding, since I could not resolve the tooling question. |
| `tests/ready-stream-missing-assertion` | maintainability | observation | `body_test` accumulates `bytes_received` but never asserts it against the expected `TOTAL_CHUNKS * CHUNK_SIZE` total (or any value); only an `info!` log reports it. | `tests/ready_stream.rs:241-248` | Fails gate 4 specifically (proven consequence): a future response-corruption bug is a plausible but unproven consequence — I did not establish that any other part of the suite would fail to catch it, so I could not prove this test's weak assertion is the load-bearing gap for a corruption class of bug the way I could for the stall class of bug. Accurate fact with a decisive pointer, consequence unproven → `Observations`, not a finding. |
| `dispatch/tracing-dev-dependency-placement` | maintainability | dropped | (Checked, not actually raised as a defect) whether `tracing-subscriber = "0.3"` (`Cargo.toml:69`) is correctly scoped to `[dev-dependencies]` and whether the `tracing` crate the test imports is available under the `full,tracing` feature combination the test targets. | `Cargo.toml:22,42,45,69,96` | Confirmed correct on inspection: `tracing-subscriber` sits under `[dev-dependencies]` (only used by the test's `init_tracing()`), and `tracing` is the existing optional main dependency gated by the existing `tracing` feature (`tracing = ["dep:tracing"]`, `Cargo.toml:96`), which the new test's `required-features` correctly references. No defect; recorded here only because it was actively checked as part of Finding 1's supporting investigation, not because it was ever a live candidate. |

Total: 8 candidates raised, 2 survivors (published as findings), 3 observations (published, at the cap), 3 dropped.

---

## 4. Sub-agent dispatches

---

## 5. Everything consulted beyond the diff

Every file, command, and search below, in the order performed. "Case-insensitive?" and "Repo-wide?" columns are stated explicitly per the dispatch's requirement.

| # | What | Repo-wide? | Case-insensitive? | Purpose / outcome |
| --- | --- | --- | --- | --- |
| 1 | Read `/tmp/holdout/dispatch/a/v5b-noverify-seed1.md` in full | n/a | n/a | The assignment itself |
| 2 | `find /tmp/holdout/skills/v5b-noverify -type f` | n/a (skill dir only) | n/a | Confirm skill snapshot contents, confirm `references/verifier.md` absent |
| 3 | `ls` on packet dir, clone dir, work dir, reports dir | n/a | n/a | Orient; **this incidentally listed filenames (not content) of sibling seeds' work/report files** — disclosed in §9 |
| 4 | Read `SKILL.md` in full | n/a | n/a | Required first read |
| 5 | Read `packet.md` in full | n/a | n/a | Pinned run identity, PR body, prior review state, guidance-file table |
| 6 | Read `references/review-rubric.md` in full | n/a | n/a | Required |
| 7 | Read `references/output-contract.md` in full | n/a | n/a | Required |
| 8 | Read `references/re-review.md` in full | n/a | n/a | Checked applicability; **not applicable** (posting identity `kamui` has no prior review/reply/trailer-bearing comment on this PR — first review) |
| 9 | Read `DESIGN.md` (first 80 lines only) | n/a | n/a | Not a `SKILL.md`-required read; skimmed for orientation only, not relied upon for any finding |
| 10 | `git branch -a`, `git log --oneline -5 review-head`, `git log --oneline -5 master` in the clone | n/a | n/a | Confirm clone hygiene (branch pins) before touching anything; see §8 |
| 11 | `ls references/ \| grep -i verif` | skill dir only | yes | Positive confirmation `verifier.md` is absent |
| 12 | `python3 scripts/review_context.py --merge-base f9f8f440... --head f2aa734e5...` (run once, exit 0) | n/a | n/a | The one sanctioned diff/manifest/ranges/history read for step 2/3 |
| 13 | Read `context_output.md` (the script's own output) across several ranges, covering all 719 lines | n/a | n/a | Manifest, complete diff (all 3 files, function-context), ranges, history |
| 14 | `grep -n "^@@"` and `grep -n "^+"` on `context_output.md` (my own scratch file, not the repo) | n/a (own scratch output) | no | Locate the actual changed lines inside the large function-context block |
| 15 | `grep -n "note: no function context"` on `context_output.md` | n/a | no | Confirmed every hunk had real function context (no note fired) |
| 16 | `ls tests/`, `ls tests/support` | n/a (one directory) | n/a | Orient for the new-test-file hygiene checks |
| 17 | `grep -rln 'duplex\|in.memory\|InMemory\|mock\|DuplexStream\|tokio::io::duplex' tests/*.rs tests/support/*.rs` | scoped to `tests/` and `tests/support/`, not the whole repo | **no** (mixed-case alternation happens to catch common casings, but the flag itself was not set — disclosed as a limitation) | Establish local in-memory-transport test convention |
| 18 | `grep -n 'duplex\|in.memory\|InMemory\|mock\|DuplexStream' tests/client.rs` | one file | no | Same |
| 19 | `grep -n 'fn.*duplex\|tokio::io::duplex\|struct.*Mock\|struct.*Duplex' tests/client.rs tests/support/*.rs` | scoped | no | Find the exact duplex helper |
| 20 | `grep -n '^use\|^pub use' tests/client.rs \| grep -i 'support\|mock\|duplex'` | one file | yes (second grep) | Confirm the duplex helper is not exported from `support` |
| 21 | `grep -n 'async fn\|struct\|impl' tests/server.rs \| head -40` | one file | no | Scan for a comparable pathological-future helper already existing in `server.rs` (none relevant found) |
| 22 | `grep -n '^\[dev-dependencies\]\|^\[dependencies\]\|^\[features\]\|tracing-subscriber\|^tokio-test\|^tokio-util' Cargo.toml` + `sed -n` ranges `45-71`, `71-110` | one file | no | Confirm `tracing-subscriber` placement and the existing `tracing` feature/dependency wiring |
| 23 | `grep -rn hyper_unstable_tracing . --exclude-dir=.git` | **whole repo**, excluding `.git` | no (cfg identifiers are case-sensitive by language rule, so case-sensitivity here is the correct sensitivity, not a limitation) | Trace every place the unstable-tracing cfg gate is referenced: `Cargo.toml`, `src/lib.rs`, `.github/workflows/CI.yml`, `src/trace.rs` |
| 24 | Read `src/trace.rs:1-20` | one file | n/a | Confirmed the `compile_error!` gate that makes Finding 1's mechanism airtight |
| 25 | `grep -n 'mod trace\|feature = "tracing"' src/lib.rs` | one file | no | Confirmed `mod trace;` is unconditional |
| 26 | Read `.github/workflows/CI.yml` in full, across several `sed -n` ranges covering all 339 lines | one file (but the file itself enumerates every CI job in the repo) | n/a | Enumerated every job; none runs `cargo test` with both `tracing` and the required RUSTFLAGS |
| 27 | `grep -n 'cargo test' .github/workflows/CI.yml` | one file | no | Located all 3 `cargo test` invocations in the workflow |
| 28 | Read `.github/workflows/bench.yml` in full, and the first 5 lines of `.github/workflows/external-types.toml` | n/a | n/a | Confirmed no other workflow file touches this test |
| 29 | `grep -n 'poll_since_write' tests/ready_stream.rs`; `sed -n '14,26p' tests/ready_stream.rs` | one file | no | Located and confirmed the colon-spacing observation |
| 30 | `grep -n '' tests/ready_stream.rs \| sed -n '230,249p'` | one file | n/a | Line-numbered view of the client-read loop and `body_test`'s end, for exact anchor lines |
| 31 | `grep -n 'ready_stream\|\[\[test\]\]' Cargo.toml`; `sed -n '233,249p' Cargo.toml` | one file | no | Located the exact `[[test]]` block and its line range for the anchor |
| 32 | `grep -n 'tokio::time::timeout\|time::timeout\|\.timeout(' tests/server.rs tests/client.rs tests/integration.rs tests/support/*.rs` + a `grep -c timeout` loop over `server.rs`/`client.rs`/`integration.rs` + `grep -n timeout tests/ready_stream.rs` | scoped to `tests/` | no | Established the sibling timeout-guard convention for Finding 2, and confirmed `ready_stream.rs` has zero occurrences |
| 33 | `grep -rn 'fn wants_read_again' src/`; `grep -n 'fn wants_read_again' -A 15 src/proto/h1/conn.rs` | `src/` (repo-wide within `src`) | no | Confirmed `wants_read_again` is unchanged, stateful (`notify_read` flag), and its own Pending-path waker responsibility is pre-existing and out of scope |
| 34 | `grep -n body_rx src/proto/h1/dispatch.rs` | one file | no | Confirmed `can_write_again`'s `self.body_rx.is_some()` matches the field's use everywhere else in the file, including its true type `Pin<Box<Option<Bs>>>` |
| 35 | `git show master:CONTRIBUTING.md` (read in full) | n/a | n/a | Applied the one tracked repository-guidance file present at the merge-base (packet §7); found no test/CI-wiring rule stated or implied |
| 36 | `sed -n '165,200p'` and `sed -n '443,448p'` on `src/proto/h1/dispatch.rs` | one file | n/a | Exact line numbers for `poll_loop` and `can_write_again` in the real file (not just the diff), used for anchors and the disposition ledger |
| 37 | Built `context_input.json` and ran `python3 scripts/context_fingerprint.py context_input.json` once | n/a | n/a | The `context` digest — see §6 |
| 38 | `python3 scripts/validate_review.py --render` (twice: once failed on a missing full-length trailer while I was staging the payload, once succeeded after adding the run trailer) | n/a | n/a | Generated the exact summary-reference fragments, pasted verbatim into the summary body |
| 39 | `python3 scripts/validate_review.py` (default mode) | n/a | n/a | Exit 0, zero violations |
| 40 | `python3 scripts/validate_review.py --emit-batch` | n/a | n/a | Produced the would-be one-call forge batch JSON as an extra artifact in the work directory (not itself one of the two required deliverables, kept for evidence) |

No `cargo`, `rustc`, `miri`, `curl`, `gh`, `git fetch/pull`, or any network call was made, per the binding conditions. No `git checkout`, `git switch`, `git reset`, or `git stash` was run; the clone was never mutated (confirmed by inspection — no destructive command appears anywhere in the command list above).

---

## 6. The `context` digest and its inputs

Digest: `13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5`

Computed once with `python3 /tmp/holdout/skills/v5b-noverify/scripts/context_fingerprint.py /tmp/holdout/work/a/v5b-noverify-seed1/context_input.json`, from this normalized input (exactly what `output-contract.md` specifies: `pr` title/body, `issues`, `specs`, `guidance`):

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

- `pr.title` / `pr.body`: taken verbatim from packet §3 (the pull-request body) and the packet's title line.
- `issues`: `[]` — packet §4 states "None ... Record `issues=none`." The run trailer's `issues=none` field reflects this.
- `specs`: `[]` — no user-supplied spec for this cell.
- `guidance`: `[]` — packet §7 lists only `CONTRIBUTING.md` as present at the merge-base, and `CONTRIBUTING.md` is **not** one of the three tracked categories the output contract's `guidance` digest field draws from (root `AGENTS.md`, root `CLAUDE.md`, path-scoped `AGENTS.md`/`CLAUDE.md` in an ancestor of a changed path, or root `CONTEXT.md`). All three categories are confirmed absent at the merge-base per packet §7's table (`no` for `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`). `CONTRIBUTING.md` was still read and applied as ordinary repository guidance under the rubric's "Repository rules" section (§5, item 35) — it just does not enter the digest.

---

## 7. Mechanism checklist

| Mechanism | Fired? | Where / why |
| --- | --- | --- |
| Question channel | **Did not fire.** | No candidate met the static-unresolvability bar — every fact needed to admit or falsify a candidate was available from the diff, the repository's own files, or the review record. No question was published. |
| Clean-verdict verification (zero-survivor mode) | **Did not fire.** | Not zero-survivor: 2 candidates survived as findings. |
| Related-acquittal verification | **Did not fire.** | Requires "at least one candidate survives **and the initial candidate batch is dispatched**." No initial batch was ever dispatched (see next row), so this mode's precondition was never met, independent of the ablation. |
| Mandatory independent verification (initial candidate batch) | **Did not fire.** | Mandatory verification triggers for: (a) any surviving candidate proposed as `must-fix` — I have none; (b) any candidate involving security/authorization, data loss/corruption, destructive migration, or an externally observable compatibility break — neither finding touches any of these (both are CI/test-hygiene, `maintainability`, `consider`); the traced `concurrency`-kind candidate (`dispatch/poll-loop-write-wake`) was **dropped**, not a survivor, so it was never even eligible to trigger this. Given none of my candidates qualifies, **this arm's ablation (no `verifier.md`, no verifier dispatch) never actually gated anything in this particular run** — a normal (non-ablated) run of this same cell would also have dispatched zero verifier batches. This determination is itself a judgment call; see §10. |
| Follow-up verifier round | **Did not fire.** | No initial batch, so no follow-up round is possible under the skill's "at most one fresh follow-up batch after the initial batch" rule. |
| Deferral handling | **Fired once.** | `dispatch/tests/ready-stream-shared-duplex-fixture` (§3): `lthiery`'s 2025-10-31 comment ends with a stated intent to "take another critical pass ... and see what I can do to simplify," which reads like the rubric's example deferral language. I treated the thread's **final** content — `seanmonstar`'s 2025-10-31 reply, "if it's a complicated edge case, perhaps that's fine as-is, then" — as closing that deferral with acceptance rather than leaving it open, and dropped the candidate under gate 6 rather than publishing a question. See §10 for the alternate reading I considered. |
| Retrospective mode | **Fired.** | `merged: true` per the packet; the summary body carries `**Mode:** Retrospective review of merged pull request; publication disabled.` immediately after the status line, and no write was attempted anywhere — the payload file is the rendered would-be review, per the dispatch's rule 2. |

---

## 8. History discipline

I read history **only at or before** the pinned head, never beyond it (nothing beyond `f2aa734e5` exists in the clone in any case, per the packet's binding condition 3).

Exact history commands run:
- `git branch -a` (clone hygiene / orientation)
- `git log --oneline -5 review-head`
- `git log --oneline -5 master`
- The context script's own `## history` section (part of the single `review_context.py` run in §5 item 12), which reports the last commits before the merge-base that touched `Cargo.toml` and `src/proto/h1/dispatch.rs` — read as part of the sanctioned single context output, not fetched separately.

No `git show <commit>` was run against any commit other than `git show master:CONTRIBUTING.md` and (implicitly, via `review_context.py --self-test`-free operation) the two blob reads the script itself performs; I did not run `git log` or `git show` against any individual historical commit's full diff or message beyond the `--oneline -5` orientation calls above. No candidate's disposition depended on any commit content beyond what the context script's `## diff` and `## history` sections already supplied.

---

## 9. Sandbox disclosure

Two items outside the strict enumerated sandbox (clone, skill snapshot, packet directory, my own work/report/payload paths), disclosed per rule 6:

1. **The dispatch file itself**, `/tmp/holdout/dispatch/a/v5b-noverify-seed1.md` — read in full as the very first action. This is my assignment, not part of the review's evidence base, and is not in the rule's enumerated list; I read it because the task requires it and treat this as implicitly authorized, but disclose it for completeness.
2. **Directory listings** of `/tmp/holdout/work/a/` and `/tmp/holdout/reports/a/` at the very start of the run (before creating my own subdirectory) incidentally showed the **filenames** of other seeds' work directories and report files (`v5b-seed1`, `v5b-seed2`, `v5b-seed3`, and their `-meta.json`/`-payload.md`/`-run.md` files). I did not open, read, or otherwise use the **content** of any of those files at any point in this run — my ledger, findings, and report were built entirely from this cell's own packet, clone, and skill snapshot.

No other run's clone, report, or payload was read.

---

## 10. Notes

**Judgment calls on rubric/contract ambiguities:**

1. **Whether the ablation's "verifier unavailable → withhold + incomplete coverage" rule applies when no candidate meets the mandatory-verification bar.** The dispatch text says "mandatory verification is incomplete, every candidate that required it stays unpublished, and coverage is reported incomplete." I read "candidate that required it" narrowly — as the set of candidates that meet `SKILL.md`'s own mandatory-verification trigger (surviving `must-fix`, or security/data-loss/destructive-migration/compatibility-break) — rather than broadly, as "every candidate in a run where a verifier happens to be unavailable." Under the narrow reading, since neither of my two findings meets that bar, and the one `concurrency`-kind candidate I raised was dropped (not a survivor) rather than published, nothing in this run ever "required" verification, so the withholding rule has nothing to act on and coverage is **not** downgraded to incomplete on that account. I believe the narrow reading is correct because it is the literal trigger condition `SKILL.md` itself defines, and because the dispatch's own ablation clause is phrased as an instance of "SKILL.md's handling rule for a verifier that fails or cannot inspect required evidence" — i.e. it borrows the existing rule rather than creating a new, broader one. I flag this because a broader reading (treat every run in this arm as inherently coverage-incomplete, regardless of what was actually found) is also textually supportable, and would change my derived status from `Approved (advisory)` to `Incomplete`.

2. **Whether the review-thread deferral about the custom `TxReadyStream` fixture was left open or closed.** GitHub's own thread-resolution flag (packet §6: "thread unresolved") argues for treating it as open. I instead read the **content** of the final message in the thread (`seanmonstar`'s acceptance) as authoritative over the UI flag, consistent with the rubric's general instruction to judge acceptance from what the review record "explicitly addresses," and dropped the candidate under gate 6 rather than routing it as a question. Had I weighted the unresolved-thread flag more heavily, this would have become a published question instead of a dropped candidate (it would not have become a finding either way, since no static evidence settles which fixture shape is "correct" — only the maintainer's opinion does).

3. **Whether the missing-space struct field (`poll_since_write:bool,`) is a live CI-failing defect or merely an in-diff inconsistency.** I could not resolve, from static reading alone, whether `rustfmt --check` (run by the `style` job over every tracked `.rs` file, `.github/workflows/CI.yml`'s `style` job) actually flags a struct field declared inside a `pin_project! { ... }` macro invocation, because `rustfmt` has a known limitation formatting the bodies of arbitrary (non-whitelisted) macro invocations, and running `cargo fmt --check` was not permitted (no execution). I chose the more conservative routing (`Observations`, not a finding asserting a CI failure) rather than assert a mechanism I could not verify. Flagged here as the specific reason this fact did not become a third finding.

4. **What I treated as "guidance" versus general context.** Per the output contract, only root `AGENTS.md`/`CLAUDE.md`, path-scoped instances covering a changed path, and root `CONTEXT.md` feed the `context` digest's `guidance` field. `CONTRIBUTING.md` (present at the merge-base per packet §7) was read and applied under the rubric's separate "Repository rules" section, but correctly excluded from the digest computation. This is stated in the contract, not actually ambiguous, but I record the distinction here since it is easy to conflate.

**Wall clock:** see §1 — not precisely instrumented from task start; the only two captured timestamps bound a roughly 4-minute window in the middle of the run (context-script completion through post-validation), and total elapsed time including the initial reads of the dispatch, skill, and packet was longer than that window.
