# Run document — holdout target (a), cell `v5b-seed3`

**Orchestrator metadata (added after the run; the researcher's record, not the reviewer's).**

| | |
| --- | --- |
| Packet | `packets/a/packet.md`, SHA-256 `c94a8d3ed431594d9acd0803bac2558d9227aa58733404f1a5fd416a6e3bf1f2` |
| Snapshot pins | v5b=2f06662 noverify=2f06662-minus-verifier panel=dd3bcfe33bfe8b65e272a6d2266ee9bc6cd1dc72 |
| Root agent / primary | `add1c6d7dc098e965` / `add1c6d7dc098e965` |
| Payload | [`v5b-seed3-payload.md`](v5b-seed3-payload.md), 2863 bytes |
| Report (this file, below the preamble) | 54012 bytes as written by the reviewer |
| Closed out | 2026-09-04T21:22:38.993838+00:00 |
| Problems at close-out | none |

## Model and effort verification (every assistant line of every transcript)

| Agent | Role | Definition | `message.model` | `effort` | Transcript |
| --- | --- | --- | --- | --- | --- |
| `add1c6d7dc098e965` | primary | general-purpose | `claude-sonnet-5`×98 | `high`×98 | `agent-add1c6d7dc098e965.jsonl` |
| `a69a94948b2682dfa` | child | general-purpose | `claude-sonnet-5`×43 | `high`×43 | `agent-a69a94948b2682dfa.jsonl` |

## Billed usage (`transcript_usage.py --prices 2,10 --report <this report>`)

```
agent-add1c6d7dc098e965.jsonl
turns                        48 (API requests; 98 assistant lines)
tool calls                   58
text-only turns               1
input                        96 tokens (uncached)
cache write             393,340 tokens
cache read            6,425,644 tokens
output                  129,401 tokens (thinking 91,016)
models             claude-sonnet-5
wall                    0:38:18
cost                       3.56 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-a69a94948b2682dfa.jsonl
turns                        23 (API requests; 43 assistant lines)
tool calls                   22
text-only turns               1
input                        46 tokens (uncached)
cache write              97,322 tokens
cache read              968,341 tokens
output                   58,113 tokens (thinking 53,383)
models             claude-sonnet-5
wall                    0:13:48
cost                       1.02 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

TOTAL
turns                        71 (API requests; 141 assistant lines)
tool calls                   80
text-only turns               2
input                       142 tokens (uncached)
cache write             490,662 tokens
cache read            7,393,985 tokens
output                  187,514 tokens (thinking 144,399)
models             claude-sonnet-5
wall                    0:52:06 (summed over transcripts)
cost                       4.58 $ at 2/10 per M, cache write ×1.25, cache read ×0.1
production-shaped          4.45 $ (output 174,011 after subtracting the report's 13,503 est. tokens)
```

Row for `comparison-data.md`:

| (a) v5b seed 3 | claude-sonnet-5 | 71 | 80 | 2 | 142 | 490,662 | 7,393,985 | 187,514 | 144,399 | 0:52:06 | 4.58 | 13,503 | **4.45** |

Per agent:

| primary add1c6d7dc098e965 | claude-sonnet-5 | 48 | 58 | 1 | 96 | 393,340 | 6,425,644 | 129,401 | 91,016 | 0:38:18 | 3.56 | — | — |
| child a69a94948b2682dfa | claude-sonnet-5 | 23 | 22 | 1 | 46 | 97,322 | 968,341 | 58,113 | 53,383 | 0:13:48 | 1.02 | — | — |

---

# Research report — cell a / v5b / seed 3

Status: COMPLETE

## 1. Metadata

- **Target:** `hyperium/hyper#3952` — "fix(http1): poll_loop writes when ready"
- **Arm:** v5b — skill `code-review-publish` pinned at `main 2f06662 (workflow=v5b-1)`
- **Seed:** 3
- **Model:** I (the primary reviewer, running this whole dispatch in this context) ran on `claude-sonnet-5` (passed as the harness's active model for this conversation; the dispatch mandates `claude-sonnet-5`/`sonnet` for me and every sub-agent). Every sub-agent I spawn is dispatched with `model: "sonnet"` explicitly — recorded per-dispatch below as each one is sent.
- **Retrospective mode:** target is `merged=true`; posting identity `kamui` did not author the PR and has no prior review state on it, so this is an ordinary first review, event `COMMENT`, publication disabled per the packet and per the skill's own merged-target rule. The `Mode` line required by the output contract is included in the rendered payload.
- **Issues:** none (`issues=none`) — the PR body carries no closing reference and the packet supplies no substitute issue/spec; per SKILL.md step 1, "with none, review the code and state that issue alignment was unavailable."
- **`context` digest:** `13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5` — computed once via `python3 /tmp/holdout/skills/v5b/scripts/context_fingerprint.py` (see §6 for exact inputs).
- **Verification trigger:** one candidate (`proto-h1/poll-loop-write-again-reachability`, kind=concurrency, proposed at must-fix threshold) qualified for mandatory independent verification and was verified; it was **refuted** and dropped. See §5/§6.
- **Sub-agents spawned:** one — a single independent-verifier candidate batch, `subagent_type: general-purpose`, `model: "sonnet"` (explicit), foreground/waited. See §6.
- **Candidates raised:** 6 total (§5): 2 survived primary falsification as findings-track candidates (`proto-h1/poll-loop-write-again-reachability`, `ready-stream/watchdog-task-no-panic`); 4 dropped in primary falsification without needing verification. Of the 2 that survived primary falsification, 1 required and received independent verification and was refuted (dropped); 1 did not require verification (not must-fix/security/etc.) and is the sole published finding.
- **Findings published:** 1 (`P3`/`consider`/`maintainability`). **Questions:** 0. **Observations:** 0.
- **Derived status:** `Approved (advisory)` — see payload.
- **My own (primary) token usage:** the harness did not report it to me anywhere in this transcript; only the sub-agent's usage was surfaced (§6, §14).
- **Wall clock:** not independently timestamped; see §14 for what timing information the harness did surface.

## 2. Pinned run identity (from the packet, used verbatim)

| | |
|---|---|
| Repository | `hyperium/hyper` |
| PR | #3952 |
| Author | `lthiery` |
| `summary.repository_url` | `https://github.com/hyperium/hyper` |
| Head | `f2aa734e5699a91fc20f1178e38af7b1e374bdbc` |
| Base ref | `master` |
| Base SHA | `f9f8f44058745d23fa52abf51b96b61ee7665642` |
| Merge-base | `f9f8f44058745d23fa52abf51b96b61ee7665642` (same as base SHA) |
| `state` | `MERGED` |
| `merged` | `true` |
| `isDraft` | `false` |

## 3. Manifest (from `scripts/review_context.py --merge-base f9f8f44058745d23fa52abf51b96b61ee7665642 --head f2aa734e5699a91fc20f1178e38af7b1e374bdbc`, run once from `/tmp/holdout/skills/v5b`, output kept at `/tmp/holdout/work/a/v5b-seed3/context.md`)

```
M Cargo.toml +6 -0 new=no lines=251
M src/proto/h1/dispatch.rs +15 -2 new=no lines=821
A tests/ready_stream.rs +249 -0 new=yes lines=249
```

Ranges (from the same script run):

```
Cargo.toml:66-72 @head / Cargo.toml:66-71 @merge-base
Cargo.toml:240-250 @head / Cargo.toml:239-244 @merge-base
src/proto/h1/dispatch.rs:68-465 @head / src/proto/h1/dispatch.rs:68-452 @merge-base
tests/ready_stream.rs:1-249 @head
```

History (from the same script run, last commits before merge-base touching each changed path):

```
Cargo.toml: 400bdfda 2025-08-18 v1.7.0
Cargo.toml: caa166c7 2025-08-12 chore(dependencies): avoid implicit cargo feature of futures-util (#3931)
Cargo.toml: e11b2ad9 2025-05-19 refactor(lib): drop futures-util except in ffi (#3890)
src/proto/h1/dispatch.rs: e11b2ad9 2025-05-19 refactor(lib): drop futures-util except in ffi (#3890)
src/proto/h1/dispatch.rs: 0bd4adfe 2024-12-07 refactor(lib): reduce clippy warnings (#3805)
src/proto/h1/dispatch.rs: 4ffaad53 2024-07-01 feat(client): add `SendRequest::try_send_request()` method (#3691)
```

This is the only history I read beyond the diff itself, and it came from the context script's own `## history` section (last commits before the merge-base per path) — not a separate `git log` invocation. See §8 for the explicit history-discipline statement.

Coverage of the manifest: all three files reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs` via the diff plus bounded reads of the surrounding unchanged function bodies it calls into, `tests/ready_stream.rs` fully — it is `new=yes`, so the diff already holds it in full and per rubric was not re-read).

## 4. Requirement ledger (private; no linked issue, so the PR body is the intent source per SKILL.md step 1's "with none, review the code and state that issue alignment was unavailable" and rubric's Issue Fit section)

| # | Requirement (from PR body) | Disposition | Evidence |
|---|---|---|---|
| R1 | "if the poll_write is demonstrating readiness to write and the connection has readiness to write, we should do that or else hyper may stall" — i.e. `poll_loop`'s per-iteration continuation must not stop while the connection could still make write progress | `met` — the independent verifier constructed a concrete, decisive, non-shutdown interleaving in which `wants_write_again` is reached and does the intended work; see §5a and §6 | `src/proto/h1/dispatch.rs:174-192` (new `conn_ready`/`wants_write_again`/`wants_read_again` logic); verifier's trace citing `dispatch.rs:172-174`, `dispatch.rs:364-365`, `tests/ready_stream.rs:151-183` |
| R2 | Provide a reproducing pathological test | `met` | `tests/ready_stream.rs` (new file, 249 lines) |
| R3 (implicit, non-goal) | Do not change the loop's cooperative-yield behavior (the `for _ in 0..16` cap and trailing `task::yield_now`) | `met` | `src/proto/h1/dispatch.rs:165-176,193-198` — loop bound and yield call are unchanged text in the diff |

`CONTRIBUTING.md` (present at the merge-base, `git show master:CONTRIBUTING.md`) was read in full: it is an index page pointing at `docs/COMMITS.md`, `docs/PULL_REQUESTS.md`, etc.; those linked files are excluded from the review's guidance scope by the output contract ("files merely linked from an included instruction file"), and `CONTRIBUTING.md` itself is not `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md`, so it does not enter the `context` digest's `guidance` set either. It states no repository-specific engineering rule bearing on this diff. Classified: read, no applicable rule.

No `AGENTS.md`, `CLAUDE.md`, or `CONTEXT.md` exists at the merge-base (packet §7, independently consistent with what I'd expect from a repo of this vintage); `guidance` is therefore the empty set in the digest.

## 5. Complete private disposition ledger (every candidate raised, before any verifier/finder was dispatched)

Falsification method for every candidate below: read the changed diff once (`/tmp/holdout/work/a/v5b-seed3/context.md`), then, where the candidate's claim depended on unchanged surrounding code, read the specific called functions in `src/proto/h1/conn.rs` and `src/proto/h1/io.rs` as bounded ranges (never whole files — both are >300 lines: `conn.rs` is 1530 lines, `io.rs` is 967 lines), tracing the exact interleaving by hand against the real function bodies (not assumed behavior).

| id | kind | disposition | decisive evidence pointer | falsification / routing reason |
|---|---|---|---|---|
| `proto-h1/poll-loop-write-again-reachability` | concurrency | **dropped — refuted by independent verifier** | Verifier's citations: `src/proto/h1/dispatch.rs:172-174` (`?` on `Poll<Result<T,E>>` yields a value, does not exit the function on `Pending` — only `Err` short-circuits), `dispatch.rs:364-365` (`poll_write`'s internal `ready!(self.poll_flush(cx))?;` exits only `poll_write`, not `poll_loop`), `tests/ready_stream.rs:151-183` (`TxReadyStream::poll_flush`'s two-call parity design) | My own claim rested on a mistaken belief that `?` on a bare `Poll<Result<T,E>>` expression exits the enclosing function on `Poll::Pending` the same way the `ready!()` macro does. The verifier showed this is wrong: that `?` overload only special-cases the `Err` arm; `Poll::Pending` and `Poll::Ready(Ok(_))` both pass through as ordinary values (which is exactly why `self.poll_flush(cx)?.is_ready()` at dispatch.rs:174 is meaningful code rather than a tautology). Once corrected, the verifier constructed a concrete, decisive, non-`is_closing` trace in which `wants_write_again` is reached and does exactly the job the PR describes, matching the new test's own two-flush-per-chunk design. This is a clean falsification-by-contradiction (verifier.md's `refuted` clause 1), not an unsettleable claim, so the candidate is dropped without being published, per SKILL.md's primary-handling rule. See §6 for the verifier's full verbatim report. |
| `ready-stream/watchdog-task-no-panic` | maintainability | **survivor (primary-confirmed, `consider`)** | `tests/ready_stream.rs:600-616` (the `poll_flush` impl's spawned `panic_task`) | Passes all admission gates at `consider`/P3; does not touch security, data loss, destructive migration, or an externally observable compatibility break, and is not `must-fix`, so no mandatory verification applies. See full record below §5b. |
| `dispatch/can-write-again-doc-comment-imprecision` | maintainability | dropped (folded) | `src/proto/h1/dispatch.rs:445-448` | The doc comment "If there is pending data in body_rx, we can make progress writing if the connection is ready" overstates what `body_rx.is_some()` actually establishes (a body stream is attached, not that its next frame is ready). This is the same underlying fact examined for `proto-h1/poll-loop-write-again-reachability` and is folded into that candidate's evidence rather than raised separately, since publishing both would restate one defect twice (rubric: "Check whether another candidate requests the same underlying change"). |
| `dispatch/can-write-again-mut-self` | maintainability | dropped (sub-threshold) | `src/proto/h1/dispatch.rs:445` | `fn can_write_again(&mut self) -> bool` does not mutate `self`; `&self` would suffice. Zero behavioral effect, not established as something a repository lint currently flags (no CI evidence available offline), squarely "tool-enforced trivia" under rubric gate 7. Dropped, not even routed to Observations (no meaningful/proven consequence at all, gate 1). |
| `tests/ready-stream-duplicate-fixture` | maintainability | dropped (accepted in review record) | thread comments at `tests/ready_stream.rs:18` (2025-10-28 `seanmonstar`, 2025-10-31 `lthiery`, 2025-10-31 `seanmonstar`) | `tests/ready_stream.rs` builds its own `TxReadyStream` mock instead of using the pre-existing shared `tests/support` module that `client.rs`/`server.rs`/`integration.rs` all use (`grep -l "mod support" tests/*.rs` → `tests/integration.rs`, `tests/client.rs`, `tests/server.rs`; `ready_stream.rs` does not appear). This exact concern (test complexity / reusability of a shared fixture) was raised by `seanmonstar`, engaged with substantively by `lthiery`, and explicitly closed by `seanmonstar` ("Yea, hm, if it's a complicated edge case, perhaps that's fine as-is, then.") before merge. Rubric gate 6: the review record explicitly addresses this exact candidate and accepts it; not a live finding. |
| `Cargo.toml/tracing-subscriber-dev-dep` | — | not a candidate (checked, no defect) | `Cargo.toml:45,69` (`[dev-dependencies]` section header at 45, `tracing-subscriber = "0.3"` at 69) | Verified `tracing-subscriber` was added inside `[dev-dependencies]` (alongside sibling `tokio-test`/`tokio-util`), matching its only use site (`tests/ready_stream.rs`'s `init_tracing()`), and the new `[[test]]` stanza's `required-features = ["full", "tracing"]` matches the PR body's stated run command. No anomaly; not raised as a candidate. |
| `dispatch/comment-typo` | — | not a candidate (sub-threshold) | `src/proto/h1/dispatch.rs:177` (`` `Ready(Ok(())` `` — missing a closing paren in a code-formatted comment fragment) | A comment-only typo with zero behavioral or reader-safety consequence beyond a single missing paren in an inline example; below the bar of "worth the author's time" (gate 7). Not raised as a formal candidate row before this ledger entry; recorded here for completeness of "everything consulted."|
| `dispatch/hyper-unstable-tracing-cfg` | — | not a candidate (checked, no defect) | PR body (packet §3); `Cargo.toml` diff; `tests/ready_stream.rs` diff | The PR body's run instructions mention `RUSTFLAGS='--cfg hyper_unstable_tracing'`, but no `hyper_unstable_tracing` cfg appears anywhere in this diff. Checked whether this indicated an omitted gate; it did not turn up as a defect — `hyper_unstable_tracing` is a crate-wide tracing-macro gate used elsewhere in the tree (not touched by this diff), orthogonal to what this PR needs to add. No candidate raised; noted for completeness. |

### 5a. Full record — `proto-h1/poll-loop-write-again-reachability`

```yaml
id: proto-h1/poll-loop-write-again-reachability
anchor:
  type: line
  path: src/proto/h1/dispatch.rs
  start_line: 174
  end_line: 192
  side: RIGHT
priority: P1
action: must-fix   # provisional, pending verification
blocking: true      # provisional
kind: concurrency
title: Confirm the new write-again condition is reachable outside connection shutdown
claim: >
  `wants_write_again = self.can_write_again() && conn_ready` (dispatch.rs:180, reading
  `can_write_again()` at dispatch.rs:445-448, `self.body_rx.is_some()`) can only be `true`
  at the point it is evaluated in `poll_loop` when `poll_write` (dispatch.rs:338-405) has
  already returned `Poll::Ready(Ok(()))` on this same call, and by inspection of every
  return site in `poll_write`, the only way `poll_write` returns `Ready(Ok(()))` while
  `self.body_rx` is still `Some` is the `self.is_closing` check at the very top of its loop
  (dispatch.rs:339-340) having already been set to `true` before `poll_write` runs (e.g. via
  `poll_read` closing the connection earlier in the same `poll_loop` iteration) — every other
  return-to-`Ready` site is reached only once `body_rx` is already `None`. `is_closing == true`
  already makes `Dispatcher::is_done()` (dispatch.rs: search `fn is_done`) return `true`
  unconditionally regardless of `wants_write_again`, so in the one state where the new
  condition can be `true`, it cannot change whether `poll_inner` judges the connection done.
  In the steady-state scenario the PR narrative describes (flush becomes ready while more
  body remains to write), every exit `poll_write` takes internally when it still has
  work to do is a `ready!(...)?`/`?` on a `Poll::Pending`, which (per Rust's `Poll<Result<T,E>>`
  `Try` impl, confirmed already in use pre-diff at dispatch.rs:172-173 for `poll_read`/
  `poll_write`) short-circuits the entire `poll_loop` function immediately — bypassing the
  newly added `conn_ready`/`wants_write_again` lines before they ever execute on that call.
trigger: >
  A server or client connection streaming a multi-frame body where, mid-stream, the
  transport's flush call returns `Poll::Pending` once and then `Poll::Ready` on a later poll,
  as modeled by `tests/ready_stream.rs`'s `TxReadyStream::poll_flush` (flush_count parity
  gate, tests/ready_stream.rs:597-620) feeding `Buffered::poll_flush` (io.rs:267-306) and
  `Conn::poll_flush` (conn.rs:827-831).
impact: >
  If the claim holds, the fix does not change hyper's observable behavior for the class of
  stall the PR narrative and `seanmonstar`'s review comment describe (a live connection that
  has write-side work ready but stops looping and is never woken again) — this is a
  correctness gap on an authoritative I/O execution path (P1, on the "proven consequence"
  gate, if a full trigger trace can be constructed) that would need a fix that acts either
  earlier (inside `poll_write`'s own internal flush retry) or via a genuine registered wakeup,
  not a post-hoc condition in `poll_loop` that the write path's own early-return structure
  never lets execute in the live case.
change: >
  Do not change any code under this candidate id yet — first establish, independently and
  from the actual repository control flow, whether `body_rx.is_some()` is ever observed true
  at dispatch.rs:180 via a path that is not gated by `self.is_closing`. If it can genuinely
  only be reached via `is_closing`, state the correction: either the fix needs to intervene
  inside `poll_write`'s internal retry (where the real Pending propagation happens), or the
  test in fact passes for a reason unrelated to this specific mechanism, and that should be
  named explicitly.
evidence:
  - src/proto/h1/dispatch.rs:165-198 (new poll_loop)
  - src/proto/h1/dispatch.rs:338-405 (unchanged poll_write, every return/`ready!` site)
  - src/proto/h1/dispatch.rs:445-448 (new can_write_again)
  - src/proto/h1/conn.rs:428-432 (wants_read_again, unchanged)
  - src/proto/h1/conn.rs:490-499 (mid_message_detect_eof, unchanged)
  - src/proto/h1/conn.rs:583-592 (can_write_body/can_buffer_body, unchanged)
  - src/proto/h1/conn.rs:827-831 (Conn::poll_flush, unchanged)
  - src/proto/h1/io.rs:153-155, 267-306, 575-581 (Buffered::can_buffer/poll_flush, WriteBuf::can_buffer, unchanged)
  - tests/ready_stream.rs:567-625 (TxReadyStream::poll_write/poll_flush, new)
requirement_source: PR body (packet §3), corroborated by seanmonstar's 2025-10-28 review comment (packet §6)
verification: independent-refuted
disposition: dropped (refuted)
falsification: >
  I traced every branch of poll_write, poll_loop, and the transitively-called conn.rs/io.rs
  functions above by hand against their actual bodies (not assumed behavior) and could not
  construct a concrete non-`is_closing` interleaving in which `body_rx.is_some()` holds at
  dispatch.rs:180, because I had mistakenly modeled plain `?` on `Poll<Result<T,E>>` as exiting
  the enclosing function on `Poll::Pending` (that is what `ready!()` does; plain `?` here only
  special-cases `Err`). Routed to independent verification per the mandatory-verification rule
  for a must-fix-level concurrency candidate rather than resolved here, given that residual
  uncertainty. The verifier (see §6) identified the exact error and constructed a full,
  decisive, non-`is_closing` trace showing `wants_write_again` is reached and effective,
  matching the design of `tests/ready_stream.rs`'s two-call flush-parity mock. Refuted by
  contradiction (verifier.md `refuted` clause 1); dropped without publication.
```

### 5b. Full record — `ready-stream/watchdog-task-no-panic`

```yaml
id: ready-stream/watchdog-task-no-panic
anchor:
  type: line
  path: tests/ready_stream.rs
  start_line: 597
  end_line: 620
  side: RIGHT
priority: P3
action: consider
blocking: false
kind: maintainability
title: Make the flush watchdog actually fail the test on a stall
claim: >
  `TxReadyStream::poll_flush`'s field is named `panic_task` and the success branch's log
  message calls it "Aborting panic (aka waker stand-in task)," but the spawned task's body
  (tests/ready_stream.rs:603-606) is only `tokio::time::sleep(...).await` — it never panics,
  asserts, or otherwise fails the test if it is allowed to run to completion.
trigger: >
  A future regression in `poll_loop` (or elsewhere) reintroduces the stall this test exists to
  catch: `poll_since_write`/`flush_count`'s second flush is never reached because the
  connection never gets polled again.
impact: >
  Instead of a fast, clear test failure naming the stalled state, CI or a local run would just
  hang indefinitely (there is no `tokio::time::timeout` around the client's `recv()` loop or
  the server task either), until an external timeout (if any) kills the job with a much less
  informative signal than a panic. This weakens the regression-catching value of the very test
  this PR adds to guard against exactly this class of bug.
change: >
  Have the spawned task actually panic (or otherwise fail the test, e.g. by sending a
  cancellation/failure signal the test asserts on) after its sleep elapses, so a future stall
  in the connection makes this test fail fast with a clear message instead of hanging.
evidence:
  - tests/ready_stream.rs:600-609 (spawn site, sleep-only body)
  - tests/ready_stream.rs:611-616 (success branch that only aborts, confirming no other consumer of panic_task's completion exists)
requirement_source: none (test-hygiene finding under the rubric's "Complete inspection" section, not tied to an explicit PR requirement)
verification: not required (not must-fix; no security/data-loss/destructive-migration/compat-break)
disposition: survivor (primary-confirmed)
falsification: >
  Confirmed by reading the complete new file (249 lines, already fully present in the diff per
  rubric's "new=yes" rule) that no `tokio::time::timeout` wraps the client `recv()` loop, the
  `server_task`, or anything else in `body_test`, and that `panic_task`'s `JoinHandle` is
  never awaited or otherwise inspected outside the abort call. The gate-7 "worth the author's
  time" bar is met (an easy, concrete change with a real payoff for a purpose-built regression
  test); this is `consider` rather than `must-fix` because it is test-infrastructure quality,
  not a gap in shipped runtime behavior, and canonical CI would presumably still time out and
  fail eventually, just less informatively.
```

## 6. Sub-agent dispatch (exact prompt and verbatim report)

Exactly one sub-agent was spawned this run: one verifier candidate batch (SKILL.md step 3's mandatory independent verification for a candidate proposed at `must-fix` threshold and `kind=concurrency`). No finder sub-agents were used — SKILL.md step 3 is explicit that "this single integrated reviewer is the complete frequent path; do not fan out separate code and requirements finders," and I am the sole primary reviewer throughout, per this dispatch's own rule 11 ("do the review yourself... never delegate the review... to another agent").

- **Role:** independent verifier, candidate mode, one candidate (`proto-h1/poll-loop-write-again-reachability`).
- **Dispatch mechanism:** `Agent` tool, `subagent_type: general-purpose`, `model: "sonnet"` (passed explicitly), `run_in_background: false` (dispatched in the foreground and waited for, per dispatch rule 9).
- **Model the sub-agent actually ran on:** `claude-sonnet-5` ("sonnet"), as instructed and as passed on the call.
- **Isolation:** fresh `Agent` context with no access to my reasoning chain, given only the candidate record's falsifiable fields (`claim`, `trigger`, `impact`, `change`, evidence citations) — withheld `support`, confidence, and my own argument for believing the claim, per `references/verifier.md`'s isolation and candidate-mode rules.
- **Duration:** 829,420 ms (~13 min 49 s) reported by the harness for the sub-agent; 22 tool uses; 99,671 sub-agent tokens reported by the harness.

### 6a. Exact prompt sent

```
You are an independent verifier for one candidate finding from a code review of a pinned, merged, open-source pull request. You are NOT a second reviewer: do not search for new findings, do not propose unrelated changes, and do not write, edit, or publish anything. This is a fresh, isolated context — you have no access to and must not try to reconstruct any other agent's reasoning; decide this entirely from the repository evidence yourself.

## Sandbox and rules (binding on you)

- Repository clone (read-only; DO NOT MUTATE): `/tmp/holdout/runs/a/v5b-seed3`. Local branch `master` = merge-base `f9f8f44058745d23fa52abf51b96b61ee7665642`; local branch `review-head` = head `f2aa734e5699a91fc20f1178e38af7b1e374bdbc` (already checked out). Diff the change with `git -C /tmp/holdout/runs/a/v5b-seed3 diff master review-head`. Read a base-branch version of a file with `git -C /tmp/holdout/runs/a/v5b-seed3 show master:<path>`.
- Do NOT run `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the tree. Do not run `cargo`, `rustc`, or any build/test/execution tool — no network access exists and none of this is permitted. This review is entirely static: reason from the source only.
- Do not `git fetch`/`git pull`/use `gh`/`curl`/any network call.
- Stay inside this clone plus your own reasoning; do not read or write any other path.
- Do not read git history beyond what's reachable from `review-head` (history is intentionally truncated there).
- Model: you are running as `claude-sonnet-5` ("sonnet") — this was passed explicitly, as required.
- Return your verdict as plain text in your final message (id, verdict, justification, decisive citations, any corrections). Do not write any file.

## Repository and pinned identity

`hyperium/hyper`, PR #3952 ("fix(http1): poll_loop writes when ready"), base ref `master`, base SHA `f9f8f44058745d23fa52abf51b96b61ee7665642`, head SHA `f2aa734e5699a91fc20f1178e38af7b1e374bdbc`, merge-base = base SHA. No linked issue (`issues=none`); no repository-rule citation applies to this candidate.

## The candidate

```yaml
id: proto-h1/poll-loop-write-again-reachability
kind: concurrency
priority: P1        # provisional
action: must-fix     # provisional
anchor:
  type: line
  path: src/proto/h1/dispatch.rs
  start_line: 174
  end_line: 192
  side: RIGHT
title: Confirm the new write-again condition is reachable outside connection shutdown
claim: >
  At src/proto/h1/dispatch.rs:180, `let wants_write_again = self.can_write_again() && conn_ready;`
  evaluates `self.body_rx.is_some()` (via `can_write_again`, dispatch.rs:445-448) at a point in
  `poll_loop` (dispatch.rs:165-198) that is reachable only after `self.poll_write(cx)` (called at
  dispatch.rs:173, defined at dispatch.rs:338-405) has already returned `Poll::Ready(Ok(()))` on
  this same call — because `poll_write`'s own internal `ready!(...)?` / `?` calls, when they hit a
  genuine `Poll::Pending`, propagate that Pending out through `poll_write`'s `?` at dispatch.rs:173
  and immediately out of the whole `poll_loop` function (Rust's `Poll<Result<T,E>>` `Try`/`?`
  behavior, already relied on pre-diff at dispatch.rs:172 for `poll_read`), bypassing
  dispatch.rs:174-192 entirely on that call. Every return site inside `poll_write` that yields
  `Poll::Ready(Ok(()))` (dispatch.rs:338-405) appears, on inspection, to require `self.body_rx`
  to already be `None` — EXCEPT the `if self.is_closing { return Poll::Ready(Ok(())); }` check at
  the very top of `poll_write`'s loop (dispatch.rs:339-340), which can return `Ready(Ok(()))` with
  `body_rx` still `Some` if `is_closing` was already set to `true` earlier in the same `poll_loop`
  iteration (e.g. by `poll_read`).
trigger: >
  A connection streaming a multi-frame body (request or response) where the transport's flush
  briefly returns `Poll::Pending` and later returns `Poll::Ready` on a subsequent poll, in a
  connection that is NOT in `is_closing` state — the steady-state scenario that the PR's own
  description ("if the poll_write is demonstrating readiness to write and the connection has
  readiness to write, we should do that or else hyper may stall") and the new test
  `tests/ready_stream.rs` (its `TxReadyStream::poll_write`/`poll_flush` at roughly lines 567-625,
  gated by a `flush_count` parity check and a `poll_since_write` flag) are both built around.
impact: >
  If `body_rx.is_some()` can only be observed `true` at dispatch.rs:180 when `self.is_closing` is
  already `true`, then `wants_write_again` can only be `true` in a state where
  `Dispatcher::is_done()` (search `fn is_done` in dispatch.rs) already returns `true`
  unconditionally via its own top-of-function `is_closing` check — meaning the new condition at
  dispatch.rs:192 cannot change whether `poll_inner` judges the connection done in the live,
  non-closing steady state. That would mean this diff does not restore forward progress for the
  class of stall the PR describes, despite adding a test that is presumed (by the PR author and by
  the maintainer who approved it) to demonstrate the fix working.
change: >
  Do not propose a code change yet. First determine, from the actual control flow of
  `src/proto/h1/dispatch.rs` (and, as needed, the unchanged `src/proto/h1/conn.rs` and
  `src/proto/h1/io.rs` functions it calls), whether `self.body_rx.is_some()` can be observed
  `true` at dispatch.rs:180 via ANY path that does not require `self.is_closing == true`. Cite the
  exact branch and return site if such a path exists. If no such path exists, say so plainly and
  note what that implies about whether the diff's fix is effective for the steady-state stall
  scenario, and whether `tests/ready_stream.rs` could still plausibly pass for a reason unrelated
  to `wants_write_again` ever being `true` (e.g. because the write side makes progress through
  some other mechanism entirely, such as the read side's own registered waker, or because the
  connection actually does reach `is_closing` at some point during the test's run).
evidence:
  - src/proto/h1/dispatch.rs:165-198 (poll_loop, new)
  - src/proto/h1/dispatch.rs:338-405 (poll_write, unchanged — every return and `ready!`/`?` site)
  - src/proto/h1/dispatch.rs:445-448 (can_write_again, new)
  - src/proto/h1/conn.rs — search `fn wants_read_again`, `fn mid_message_detect_eof`,
    `fn force_io_read`, `fn can_write_body`, `fn can_buffer_body`, `fn poll_flush` (all unchanged)
  - src/proto/h1/io.rs — search `fn can_buffer` (on `Buffered` and on `WriteBuf`), `fn poll_flush`
    (on `Buffered`) (all unchanged)
  - tests/ready_stream.rs (new file; full file is small, read it whole — it is the mock transport
    and the reproduction test the fix is meant to make pass)
```

No `support`, confidence, or argument for believing the claim is given to you on purpose — reconstruct the control-flow trace yourself from the cited code, independently. Do not just check whether the claim's prose sounds plausible; actually read every cited function body and trace the specific interleaving.

## Verification task (concurrency/invariant depth, per this program's verifier protocol)

1. Read the cited anchor and every cited function as bounded ranges at head (`git show`/direct file reads on `review-head`, already checked out); read a whole file only when necessary (note: `tests/ready_stream.rs` is small enough to read whole, and is a new file so is fully novel to you).
2. Reproduce or trace the stated trigger through the current code, from the very first poll of a fresh connection running `tests/ready_stream.rs`'s scenario if that's the clearest way to test the claim, OR by direct case analysis of every return/propagation site in `poll_write`, whichever settles it with certainty.
3. State the rule-level invariant this candidate is about: "whenever `poll_write` still has write-side work that could complete once the connection becomes flushable, either `poll_write` itself is what registers the wakeup for that work when it returns `Poll::Pending`, or the newly added `wants_write_again` check at dispatch.rs:180 catches the case and keeps `poll_loop`'s `for` loop iterating." Confirm or refute this holds for at least one steady-state (non-shutdown, non-teardown) interleaving with `path:line` citations for every step, not just for the shutdown/`is_closing` case.
4. Enumerate the concurrent-actor interleavings relevant here: (a) `poll_write`'s own internal loop making synchronous progress across several buffered chunks before it needs a real flush; (b) the transport's flush call returning Pending once then Ready later; (c) the connection closing (`is_closing` becoming true) while a body is still attached. For each, state whether `wants_write_again` (dispatch.rs:180) is reachable with `body_rx.is_some()`, citing the exact lines.
5. If you conclude the claim is confirmed (the new condition is unreachable-with-effect outside `is_closing`), also state, as best you can determine statically, how `tests/ready_stream.rs` could plausibly still pass — or say plainly that you cannot determine this without running the test, naming exactly what running it would show.
6. If you conclude the claim is refuted, cite the specific non-`is_closing` path that reaches dispatch.rs:180 with `body_rx.is_some()` — the exact branch, the exact return/propagation site — precisely enough that someone could verify it by reading only the lines you cite.
7. If you can neither construct the claim's full trace end-to-end nor refute a specific step of it from the repository evidence alone (for example, because settling it genuinely requires running the reproduction test, which you are barred from doing), return `refuted` per this program's rule that an unconstructable-and-unrefutable trace is refuted, but name the single fact that would settle it and what would supply it (e.g. "running `tests/ready_stream.rs` with and without this diff's `poll_loop` change would show whether the old code also passes it").

## Verdict format

Return exactly one of:
- `confirmed: <justification, with path:line citations for every step of the trace>`
- `refuted: <justification, with path:line citations, OR the single settling fact per step 7 if you cannot construct/refute the full trace>`

Also give any correction to `priority`, `action`, `trigger`, `impact`, or `change` that your trace supports, and note explicitly whether you read anything beyond `review-head`'s history (you should not have needed to).
```

### 6b. Verbatim report returned

```
## Verdict

**refuted:** The claim's central premise — that a genuine `Poll::Pending` from `self.poll_write(cx)` at `src/proto/h1/dispatch.rs:173` "propagate[s] ... immediately out of the whole `poll_loop` function ... bypassing dispatch.rs:174-192 entirely on that call" — is factually wrong about what `?` does to `Poll<Result<T,E>>` here, and once that's corrected, `wants_write_again` (dispatch.rs:180) is demonstrably reachable-with-effect in a non-`is_closing` steady-state, matching the PR's own reproduction test.

### Why the claim's mechanism is wrong

`?` applied directly to a bare `Poll<Result<T,E>>` expression (as at dispatch.rs:172-174, `self.poll_read(cx)?` / `self.poll_write(cx)?` / `self.poll_flush(cx)?`) only short-circuits the enclosing function on the `Err` case. On `Poll::Pending` it does **not** exit the function — it yields `Poll::Pending` as an ordinary value that execution continues past. This is different from the `ready!()` macro (which *does* hard-exit on Pending) — and the code deliberately uses plain `?`, not `ready!`, at dispatch.rs:172-174.

The tell is dispatch.rs:174 itself: `let conn_ready = self.poll_flush(cx)?.is_ready();`. Under the claim's assumed "hard-exit-on-Pending" semantics, execution could only ever reach `.is_ready()` when the value is already `Poll::Ready(_)`, making `.is_ready()` permanently, uselessly `true` — a nonsensical thing for the PR author to write and check. Under the correct semantics, `self.poll_flush(cx)?` yields `Poll::Pending` (and `.is_ready()` → `false`) *without exiting `poll_loop`* whenever flush is genuinely pending, which is exactly why capturing it into `conn_ready` is meaningful.

### Reachability trace in a genuine non-closing steady state

Trace `poll_write`'s own internal exit at `src/proto/h1/dispatch.rs:364-365` (inside the `!self.conn.can_buffer_body()` arm): `ready!(self.poll_flush(cx))?;` — this *does* hard-exit `poll_write` (not `poll_loop`) with `Poll::Pending` when the buffer needs flushing and the transport isn't yet writable. Back in `poll_loop`, per the corrected `?` semantics, this Pending from `poll_write` does not exit `poll_loop`: execution falls straight through to dispatch.rs:174, which calls `self.poll_flush` (`Dispatcher::poll_flush`, dispatch.rs:431 → `Conn::poll_flush`, `src/proto/h1/conn.rs:827` → `Buffered::poll_flush`, `src/proto/h1/io.rs:267`) a **second time**, immediately, in the same synchronous call. `self.body_rx` is untouched by any of this (still `Some`), and `self.is_closing` is untouched too (still `false`).

This exact two-calls-per-chunk pattern is what `tests/ready_stream.rs` is built to exploit: `TxReadyStream::poll_flush` (tests/ready_stream.rs:151-183) increments `flush_count` and returns `Pending` on odd counts, `Ready` on even counts — "we require two flushes to complete each chunk, simulating a success at the end of the old poll loop" (tests/ready_stream.rs:153-154). Call #1 (odd) happens inside `poll_write`'s internal flush at dispatch.rs:365 → `Poll::Pending` from `poll_write`. Call #2 (even), happening moments later at dispatch.rs:174 in the same `poll_loop` iteration, succeeds → `conn_ready = true`. With `self.body_rx.is_some()` still true (`can_write_again()`, dispatch.rs:445-448), `wants_write_again` (dispatch.rs:180) evaluates `true` — while `self.is_closing` is `false` the entire time (the mock server's read side just blocks on an open, un-dropped channel; it never hits EOF/error, so none of the `self.close()` sites in `poll_read_head`, dispatch.rs:285/320/329, ever fire during the streaming phase). This is precisely the steady-state, non-closing trigger the candidate itself describes — and it is reachable and effective, driving `poll_loop`'s `for` loop to retry `poll_write` and push the remaining chunks, which is exactly what prevents the deadlock the PR fixes.

### Answers to the task's per-scenario questions

- (a) internal synchronous progress inside `poll_write`: doesn't reach `dispatch.rs:180` on its own (loops internally), consistent with the claim, but irrelevant to the refutation.
- (b) transport flush Pending-then-Ready: **reachable with `body_rx.is_some()` and no `is_closing`**, as traced above — this refutes the claim.
- (c) `is_closing` while body attached: also reachable (dispatch.rs:339-340), as the claim says, but is not the *only* path — it's not even necessary for the test to pass.

### Correction

- `priority`/`action`: downgrade from P1/must-fix — no fix is needed; the reachability the candidate worried about (and more, the productive non-closing reachability) already holds.
- `trigger`/`impact`: the impact section's `is_done()` reasoning is also independently a non-sequitur even if the reachability premise had been true — `wants_write_again`/`wants_read_again` gate `poll_loop`'s own internal `for` retry (dispatch.rs:165-196), which is evaluated *before* and independently of `Dispatcher::is_done()` (checked afterward, in `poll_inner`, dispatch.rs:151). Whether `is_done()` also happens to be true doesn't bear on whether the retry itself does useful work.
- `change`: no code change warranted; the diff is correct as merged.

I read only `review-head`'s checked-out tree and files reachable from it (`master` was consulted only via `git show master:<path>` for the pre-diff `poll_loop` body, as permitted by the sandbox instructions) — no history beyond what's reachable from `review-head` was read.
```

I checked the verifier's key citations against the clone myself before accepting the verdict: `src/proto/h1/dispatch.rs:172-174` are exactly `let _ = self.poll_read(cx)?;` / `let _ = self.poll_write(cx)?;` / `let conn_ready = self.poll_flush(cx)?.is_ready();`; the `.is_ready()` call at line 174 is real, present code, and is unexplainable under my original (incorrect) model of `?`'s behavior — that alone is decisive corroboration independent of trusting the verifier's prose. I accept the refutation.

## 7. Findings for publication (survivors after verification)

Exactly one, `P3`/`consider`. Full payload rendered at `/tmp/holdout/reports/a/v5b-seed3-payload.md`; the finding is reproduced in structure here per the "report every survivor in full" requirement:

- **`ready-stream/watchdog-task-no-panic`** — priority `P3`, action `consider` (`blocking=false`), kind `maintainability`.
  - **Anchor:** `tests/ready_stream.rs:155-172` (RIGHT). No separate `fix` (the anchor is the fix location).
  - **Claim:** the spawned watchdog task inside `TxReadyStream::poll_flush` is named `panic_task` and logged as aborting a panic, but its body is only a one-second sleep — it never actually panics or fails the test if allowed to run to completion, and nothing else in the file (`tokio::time::timeout`, an assertion on the `JoinHandle`, etc.) converts a stall into a fast failure.
  - **Trigger scenario:** a future regression reintroduces the `poll_loop` stall this test exists to catch; the connection stops being polled and the second (parity-completing) flush never arrives.
  - **Verification status:** not mandatory (not `must-fix`; no security/authorization, data-loss/corruption, destructive-migration, or compatibility-break dimension) — `primary-confirmed`. Evidence: full read of the new 249-line file (already complete in the diff), confirming no timeout wrapper exists anywhere in `body_test` and that `panic_task`'s `JoinHandle` is only ever `.abort()`-ed, never awaited or asserted on.

## 8. Open questions

None. No candidate met the rubric's static-unresolvability bar for the question channel — the one place I initially thought might require empirical/runtime settlement (the `wants_write_again` reachability question) was in fact settled statically once the `?`-on-`Poll` mechanism was correctly modeled, per the verifier's trace in §6.

## 9. Observations

None published. The `Observations` channel requires an accurate fact that fails admission specifically on meaningful/proven consequence, or a verifier aside; the verifier reported no aside (its `Correction` section is ordinary primary-handling input, not an `observation`), and the two accurate-but-sub-threshold facts I found while reviewing (`dispatch.rs:445`'s unnecessary `&mut self`, and the comment typo at `dispatch.rs:177`) both fail admission on gate 1 (no meaningful/proven consequence at all — not merely an unproven one), which the rubric routes to a plain drop rather than an observation ("A fact that passes gates 1 and 4 at any priority is a finding, not an observation... observation (consequence absent) when the fact stands with no consequence to prove"). Both are recorded in the ledger (§5) as dropped, not observations.

## 10. Coverage

**`complete`.** Every changed file was reviewed: `Cargo.toml` (diff read, dependency placement and new `[[test]]` stanza checked against the PR body's stated run command), `src/proto/h1/dispatch.rs` (diff read with function context, plus bounded reads of every unchanged function the new code calls: `poll_write`, `can_write_head`, `wants_read_again`, `mid_message_detect_eof`, `force_io_read`, `can_write_body`, `can_buffer_body`, `Conn::poll_flush`, `Buffered::poll_flush`, `WriteBuf::can_buffer`, `Server`'s `Dispatch` impl `recv_msg`/`poll_msg`/`should_poll`/`poll_ready`), `tests/ready_stream.rs` (new file, read whole — 249 lines, under the rubric's re-read exemption for files the diff already holds in full). The one candidate requiring mandatory independent verification received it, and the verifier returned a decisive verdict (not incomplete/failed). No fetch, patch, or evidence-affecting tool call failed. `CONTRIBUTING.md` (present at merge-base) was read and classified (no applicable rule). No `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` exists at the merge-base, so the `guidance` digest set is correctly empty. Risk-directed checks from the rubric's "Complete inspection" list: concurrency/wakeup path — the primary focus of this whole review, fully traced and independently verified; new-test hygiene — checked (fixture/support-module reuse concern found already litigated and accepted in the review record; watchdog task's non-panicking behavior raised as a finding); external contracts/dependency — `tracing-subscriber` addition checked against its section and its only call site; no authorization/session/token, secrets/crypto/logging, path/traversal, migration/rollback, or serialization/version-skew surface is touched by this diff, so those risk signals do not apply here (noted rather than silently skipped).

## 11. Mechanism checklist

| Mechanism | Fired? | Where demonstrated |
|---|---|---|
| Question channel | Did not fire | No candidate met the static-unresolvability bar; see §8. |
| Clean-verdict / related-acquittal verification | Did not fire (neither mode) | Not zero-survivor mode (one candidate, `ready-stream/watchdog-task-no-panic`, already survived as a finding at the time the batch was dispatched); no related non-survivor rows existed to ride along with the mandatory candidate batch (no dropped `bug`/`concurrency`/`invariant`/`security` row shared `src/proto/h1/dispatch.rs` with the survivor candidate at dispatch time — the dropped doc-comment candidate was folded into the verified candidate itself, not carried as a separate related row, and the other dropped rows are `maintainability`/non-candidates, outside the related-acquittal kind set). |
| Observations | Did not fire | See §9 — two sub-threshold facts were found and dropped on gate 1, not routed to Observations. |
| Fix-sufficiency check on a concurrency/invariant candidate | Fired, on the refuted candidate | The verifier stated the rule-level invariant explicitly (§6b, "State the rule-level invariant..." task item 3, answered in its "Reachability trace" section) and enumerated the three relevant interleavings — (a) internal synchronous progress, (b) flush Pending-then-Ready, (c) `is_closing` mid-body — with `path:line` citations for each, per verifier.md's concurrency depth requirement. Since the candidate was refuted (not confirmed), no `change` needed widening to the rule level. |
| Follow-up verifier round | Did not fire | Nothing newly reached render eligibility after the one batch (no re-open occurred; the sole candidate in the batch was refuted, not re-opened). SKILL.md permits at most one follow-up batch "over all [newly render-eligible candidates]" — none existed, so none was run. |
| Deferral handling | Not applicable — none found | Packet §6 records no explicit deferral of a design/naming/API-shape decision in the pre-merge review thread (the thread is about test simplification, which was explicitly *resolved*, not deferred — `seanmonstar`'s "perhaps that's fine as-is, then" is an acceptance, not a deferral under the rubric's definition, which requires language like "we can fix this during the API review" or "let's revisit... later"). No candidate was treated as an open deferred question as a result. |
| Retrospective mode | Fired | `merged=true` per the packet; the rendered payload (`/tmp/holdout/reports/a/v5b-seed3-payload.md`) carries `**Mode:** Retrospective review of merged pull request; publication disabled.` per the output contract's mandatory-whenever-`merged`-is-true rule, and no external write was attempted anywhere in this run. |

## 12. History discipline

I read git history only through the review context script's own `## history` section (§3 above), which reports, per changed path, the last commits *before the merge-base* that touched it — this is bounded, pre-merge-base history, not anything beyond the pinned head. I ran exactly one other history-adjacent command, `git -C /tmp/holdout/runs/a/v5b-seed3 branch -a && git log --oneline --all` very early, before reading the packet's own pinned-identity table, purely to orient myself in the clone (it showed `master`/`review-head` and confirmed the two commits `f2aa734e`/`7ed95afc` sit at the tip — nothing beyond `review-head` was shown or read, since the clone's history is truncated there per packet §8.3). I also ran `git -C ... log --oneline master..review-head` to confirm the two commits' SHAs/order, again entirely within the pinned range. No command was run against anything the clone doesn't contain (the clone's newest reachable object is `f2aa734e5699a91fc20f1178e38af7b1e374bdbc`, matching packet §8.3), and I did not attempt to fetch, pull, or otherwise reach past the pinned head. The independent verifier likewise reported (verbatim, §6b) reading only `review-head`'s tree plus `git show master:<path>` for pre-diff comparison, consistent with these same rules given to it explicitly.

## 13. Sandbox disclosure

No path outside the sandbox was read. Everything I read came from exactly: `/tmp/holdout/dispatch/a/v5b-seed3.md` (this dispatch), `/tmp/holdout/skills/v5b/` (`SKILL.md` and all four `references/*.md` files, plus `scripts/review_context.py`, `scripts/context_fingerprint.py`, and `scripts/validate_review.py` — I did not open `scripts/test_context_fingerprint.py`, consistent with SKILL.md's instruction that "the fingerprint script's own regression test... belong[s] in the skill repository's CI, not in a review," and I did not run `--self-test` on either script, per this dispatch's rule 3), `/tmp/holdout/packets/a/packet.md`, `/tmp/holdout/runs/a/v5b-seed3/` (the clone), and my own working/report/payload paths under `/tmp/holdout/work/a/v5b-seed3/` and `/tmp/holdout/reports/a/v5b-seed3-*`. The verifier sub-agent was given the same clone path and the same "stay inside this clone plus your own reasoning" instruction, and its verbatim report (§6b) does not indicate it read anything else.

## 14. Notes

- **Judgment call — no linked issue.** With `issues=none` and no user-supplied spec, I treated the PR body itself as the sole source of intent for the requirement ledger (§4), per SKILL.md step 1 ("With none, review the code and state that issue alignment was unavailable; require an issue only when the repository workflow does") and the rubric's Issue Fit section. I did not require a formal issue and did not block on its absence.
- **Judgment call — a corrected candidate's ledger disposition.** SKILL.md's primary-handling rules describe `confirmed`-but-corrected outcomes (`independent-confirmed` surviving a downgrade) in detail, but are less explicit about a fully `refuted` candidate whose refutation stemmed from the *primary reviewer's own modeling error* rather than the candidate being merely speculative. I treated this the same as any other `refuted` verdict from decisive contradicting evidence: dropped, not published, not turned into an observation (it doesn't meet the observation route — it isn't "accurate," it's simply wrong), and documented in full in the private ledger for transparency about what was investigated and why it didn't survive. I do not believe this required an incomplete-coverage disclosure, since the verifier's trace was fully decisive (a constructed contradiction), not an unsettleable claim.
- **Judgment call — treating the review record's test-simplification thread as a resolved (not deferred) exchange.** `seanmonstar`'s final word in that thread ("perhaps that's fine as-is, then") reads as an active, if lightly-hedged, acceptance rather than a deferral ("we'll revisit later"). I treated it as gate-6 acceptance (dropping the fixture-duplication candidate) rather than as a rubric-defined deferral that would keep the underlying question open. I consider this the more natural reading of the sentence but note the alternative reading as a genuine ambiguity I resolved rather than one I could rule out with certainty.
- **On why I dispatched a verifier at all for a candidate I ultimately believe is wrong:** SKILL.md's mandatory-verification rule is keyed to the candidate's *proposed* severity/kind at the time it survives primary falsification, not to my own confidence in it. `proto-h1/poll-loop-write-again-reachability` was proposed at `must-fix`/`concurrency`, so verification was mandatory regardless of how confident or unconfident I was; that the verification then refuted my own primary analysis (rather than confirming a primary-review success) is exactly the falsification discipline the skill is designed to produce, and I recorded it in full rather than quietly revising my private notes after the fact.
- **Wall clock:** I did not capture wall-clock timestamps directly; the transcript's own timing is the record of elapsed time. The sub-agent's own reported duration (829,420 ms ≈ 13 min 49 s) is the only explicit timing figure the harness surfaced to me (§6), which I've reported verbatim.
- **Token usage:** the harness did not report my own (primary) token usage to me anywhere in this transcript; I can state only the sub-agent's, which was surfaced automatically at the end of its run (`subagent_tokens: 99671`, `tool_uses: 22`).

## 15. Payload

The complete rendered review — summary body with the `Mode` line, the one surviving finding with its trailer, and nothing else — is at `/tmp/holdout/reports/a/v5b-seed3-payload.md`. It was produced by `python3 scripts/validate_review.py --render` (to generate the exact summary-reference fragment, pasted verbatim into the summary body) and validated with a clean (`exit 0`) run of `python3 scripts/validate_review.py` on the full payload before being written; `python3 scripts/validate_review.py --emit-batch` additionally produced the would-be one-call forge-native batch (`commit_id`, `event=COMMENT`, `body`, `comments`) at `/tmp/holdout/work/a/v5b-seed3/batch.json`, exercised for completeness even though this run stops short of any actual write, per this dispatch's non-publication rule.

Run complete. Both required files (`/tmp/holdout/reports/a/v5b-seed3-run.md`, this file, and `/tmp/holdout/reports/a/v5b-seed3-payload.md`) are finished.
