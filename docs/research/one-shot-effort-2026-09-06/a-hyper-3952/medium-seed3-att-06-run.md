# Research report — hyperium/hyper#3952 — cell a-medium-seed3, attempt att-06

## 1. Metadata

- **Target:** `hyperium/hyper#3952` — "fix(http1): poll_loop writes when ready"
- **Cell / attempt:** `a-medium-seed3` / `att-06`
- **Skill:** `code-review-publish` (snapshot at `/tmp/effort124/skill/skills/code-review-publish/`)
- **Model I ran on:** `claude-sonnet-5`
- **Sub-agents spawned:** one, `subagent_type: "v5b-verifier-effort-high"`, `model: "sonnet"`, `run_in_background: false` — see §4 for its role, exact prompt, and verbatim report.
- **Verification trigger fired:** yes — mandatory verification for a surviving `must-fix`, `kind=concurrency` candidate (`dispatch/poll-loop-write-busy-spin`), which also carried `verifier-concurrency.md`'s bug-class check. One initial candidate batch was dispatched (see §4), carrying that candidate plus, under related-acquittal mode, the non-survivor ledger row `dispatch/poll-loop-closing-spin` (same file, same `kind=concurrency`, same claimed state field `body_rx`/`can_write_again`). The verifier **re-opened** that related row (`disposition dispatch/poll-loop-closing-spin does not hold; re-open it`), with a full clean-verdict trace showing my "bounded, one-time" disposition was wrong — it is in fact an **unbounded livelock**, more severe than the general spin, and citing a line (`dispatch.rs:149`) my own ledger row had not cited. I re-falsified it myself as primary per the re-open rule and merged it into `dispatch/poll-loop-write-busy-spin`'s scope rather than publishing a second finding, since both share the identical root cause and identical fix; I judged this merge fully covered by the evidence the same fresh-context verifier batch already produced, so no second (follow-up) batch was needed — see §10 for that judgment call. The verifier also corrected my anchor/fix line numbers: the numbers I supplied in the candidate record did not match the real file (I had mis-transcribed hunk-relative line numbers rather than reading the actual post-diff file positions); I use the verifier's corrected coordinates, confirmed by my own direct re-read of the file (see §5), in the published finding.
- **Candidates raised:** 4 (see §3 ledger)
- **Candidates surviving primary falsification:** 2 (`dispatch/poll-loop-write-busy-spin` — widened to cover both the general streaming-Pending spin and the `is_closing` livelock — as `must-fix`/`concurrency`; `tests/ready-stream-no-assertions` as `consider`/`maintainability`)
- **Verifier verdicts:** `dispatch/poll-loop-write-busy-spin` → `confirmed`, with anchor/fix correction and full concurrency bug-class check; `dispatch/poll-loop-closing-spin` (related non-survivor row) → **re-opened** (`does not hold`), re-falsified by me and merged into the confirmed finding's scope rather than published separately
- **Findings for publication:** 2 — see §2
- **Questions:** 0
- **Observations:** 0 published (0 qualifying candidates were routed there; see §3)
- **Coverage:** complete — every changed file reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs`, `tests/ready_stream.rs`); targeted risk checks (concurrency/select-loop invariant, test hygiene) executed with evidence-backed outcomes; no packet gaps, no withheld/missing diff chunks after recovery reads (see §5); focused test execution unavailable per run conditions (offline, no cargo) — traced by semantics instead, as the rubric permits.
- **Derived status:** `Changes Requested (advisory)` — one unsettled `must-fix` finding (`event=COMMENT`, retrospective/advisory; publication disabled).
- **Token usage:** the harness did not report a token-usage figure to me for my own context in this session; I have no number to give for the primary. The one sub-agent's completion did report usage (`subagent_tokens: 78929`, `tool_uses: 21`, `duration_ms: 422414`), reproduced verbatim in §4.

## 2. Findings for publication (full detail)

### Finding 1 — `dispatch/poll-loop-write-busy-spin`

- **Priority / action:** P0 / must-fix / blocking=true (raised from my initial P1 after the verifier's re-open trace on the related `is_closing` row showed an unbounded livelock, not just wasted CPU)
- **Kind:** concurrency
- **Anchor:** `src/proto/h1/dispatch.rs:171-195` (RIGHT) — the `poll_loop` for-body computing `wants_write_again`/`wants_read_again` and the loop-continuation decision
- **Fix location:** `src/proto/h1/dispatch.rs:445-447` (the `can_write_again` method), read together with `165-200` (`poll_loop`) and `336-427` (`poll_write`'s `is_closing` short-circuit at 338-339 and its Pending body-frame path)
- **Claim:** `can_write_again` (`dispatch.rs:445-447`) returns `self.body_rx.is_some()` — a level-triggered presence check with no reset — regardless of whether this iteration's `poll_write` actually made write progress. `wants_read_again` (`conn.rs:428-431`), the pre-existing read-side analog, is instead edge-triggered: it reads and resets a one-shot `notify_read` flag set only at genuine state-transition sites, so a `Pending` read with no real state transition correctly evaluates `false`. This asymmetry has two demonstrated consequences:
  1. **General streaming spin:** whenever a response/request body's `poll_frame` returns `Pending` while `body_rx` stays `Some` and `poll_flush` no-ops to `Ready` (nothing new buffered — `Conn::poll_flush` at `conn.rs:827-830` unconditionally reaches `Ready(Ok(()))` when the underlying writer had nothing to flush), `wants_write_again` (`dispatch.rs:180`) is `true` on every iteration regardless of `poll_frame`'s outcome, so `poll_loop`'s bounded `for _ in 0..16` loop (`dispatch.rs:171-196`) always exhausts all 16 iterations and then self-wakes via `task::yield_now` (`dispatch.rs:200`, `common/task.rs:8-11`: `cx.waker().wake_by_ref(); Poll::Pending`) — a genuine self-rescheduling busy spin, not a park on the body's own registered waker, that repeats for as long as the body remains open and intermittently `Pending`.
  2. **`is_closing` livelock (more severe, unbounded):** `poll_write`'s `is_closing` branch (`dispatch.rs:338-339`) returns immediately without ever touching `body_rx`, and `close()` (`dispatch.rs:438-442`) never clears it either. If `is_closing` becomes `true` while `body_rx` is still `Some` (e.g., `dispatch.poll_ready` returns `Err(())` mid-stream, `dispatch.rs:281-288`, triggering `self.close()`), `body_rx` is permanently `Some`; `poll_flush` keeps no-oping to `Ready` (it does not consult closed-write state), so `wants_write_again` is `true` forever. The loop never reaches its `return Poll::Ready(Ok(()))` exit (`dispatch.rs:192-195`); it runs all 16 iterations, `task::yield_now` self-wakes, and — critically — `poll_inner`'s `ready!(self.poll_loop(cx))?` (`dispatch.rs:149`) means `is_done()` (`dispatch.rs:151,449-464`) is **never evaluated** while this cycle repeats. This is not a bounded, one-time teardown cost; it is a permanent livelock that also blocks the connection from ever completing shutdown.
- **Verification status and evidence:** `independent-confirmed` via a fresh-context verifier batch (full prompt and verbatim response in §4). The verifier confirmed the general-spin candidate exactly as claimed, corrected my anchor/fix line numbers to the ones above, ran the full `verifier-concurrency.md` 5-step bug-class check (stated the rule-level invariant, confirmed the failing interleaving needs no shutdown — a pure steady-state trace fails — enumerated the producer-vs-consumer write-side and read-vs-write sibling interleavings, confirmed protection on the `!can_buffer_body` backpressure path, confirmed `change` was already rule-level), and additionally **re-opened** the related non-survivor row `dispatch/poll-loop-closing-spin` that I had dropped as "bounded" — the verifier's clean-verdict trace (§4) shows `is_done()` is provably never reached while the spin continues (citing `dispatch.rs:149`, a line my own ledger row had not cited), so the closing-path manifestation is unbounded, not bounded. I re-falsified that re-opened row myself as primary and, agreeing with the verifier's evidence, merged its (worse) consequence into this finding's scope rather than publishing it separately, since both manifestations share the identical root cause (`can_write_again`'s coarse presence check) and identical fix.
- **Trigger scenario:** (a) Any response/request body whose `Body::poll_frame` returns `Poll::Pending` at least once while streaming with the connection not write-buffer-blocked — the common case for proxies, streamed downloads, SSE, or any producer that isn't always instantly ready — causes a sustained busy spin for as long as the body remains open. (b) A body that is still streaming when the dispatcher decides to close the connection (for example, the user service's message channel closing or erroring mid-response) causes a **permanent** livelock that never resolves and blocks connection shutdown entirely.

**Change:** Make the write-continuation signal reflect whether this iteration's `poll_write` call actually produced forward progress (wrote a new frame/head, or otherwise transitioned buffered-write state), not merely that a body handle is still open — mirroring `wants_read_again`'s edge-triggered semantics — and apply that same per-iteration progress check on the `is_closing` short-circuit path too (a no-op iteration during closing must not count as "wants write again" either), so the loop only continues when there is concrete evidence of further synchronous write work and otherwise returns and relies on a genuinely registered waker.

<!-- finding id=dispatch/poll-loop-write-busy-spin head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P0 action=must-fix blocking=true kind=concurrency fix=src/proto/h1/dispatch.rs:445 -->

### Finding 2 — `tests/ready-stream-no-assertions`

- **Priority / action:** P3 / consider / blocking=false
- **Kind:** maintainability
- **Anchor:** `tests/ready_stream.rs:240-248` (RIGHT) — the `body_test` function's response-consumption loop and its closing `info!` call
- **Fix location:** same as anchor (`tests/ready_stream.rs:240-248`)
- **Claim:** `body_test` contains zero `assert!`/`assert_eq!`/`expect`-style assertions on the observed behavior (confirmed by a batched, case-sensitive `grep -n "assert"` over the file, 0 matches). The only observation of the response is `bytes_received`, which is logged via `info!(bytes_received, "Client done receiving bytes")` and never compared against the expected total (`TOTAL_CHUNKS * CHUNK_SIZE` = 1 MiB) or validated against the HTTP response framing. The test's own receive loop (`while let Some(chunk) = client_stream.recv().await { ... }`) terminates on channel closure regardless of how many bytes actually arrived, so a regression that delivers a truncated or malformed response — anything short of a full stall — passes this test silently.
- **Verification status and evidence:** `primary-confirmed` only; not independently verified (does not meet a mandatory-verification trigger: not `must-fix`, not security/auth, not data-loss/corruption, not a destructive migration, not an externally observable compatibility break). Falsified against the rubric's Changed-tests rule ("a test that asserts nothing about the call... observes nothing") and the explicit review-record deferral: `seanmonstar`'s and `lthiery`'s pre-merge thread on `tests/ready_stream.rs:18` discussed only whether the *test setup* could be *simplified*, never the absence of assertions, so gate 6 (unintentional) is not defeated by that deferral for this specific claim.
- **Trigger scenario:** Any future regression to `poll_write`/`poll_loop` that causes the server to send fewer bytes than expected, send them out of order, or otherwise corrupt the streamed body — without literally hanging the connection open forever — would let `body_test` pass, because nothing checks `bytes_received` against the expected total.

**Change:** Add `assert_eq!(bytes_received, TOTAL_CHUNKS * CHUNK_SIZE);` (or an equivalent check on the received bytes) after the receive loop in `body_test`, so the test actually validates the behavior it exercises rather than only its ability to terminate.

`Closing this without action is a correct response.`

<!-- finding id=tests/ready-stream-no-assertions head=f2aa734e5699a91fc20f1178e38af7b1e374bdbc priority=P3 action=consider blocking=false kind=maintainability fix=tests/ready_stream.rs:240 -->

## 3. Private disposition ledger (complete)

| id | kind | disposition | decisive evidence | falsification / reason |
| --- | --- | --- | --- | --- |
| `dispatch/poll-loop-write-busy-spin` | concurrency | **survivor → must-fix (P0), independent-confirmed** | `src/proto/h1/dispatch.rs:171-196,445-447`; `src/proto/h1/conn.rs:428-431,827-830`; `src/common/task.rs:8-11` | Traced: `can_write_again` is a presence check (`body_rx.is_some()`), not a per-iteration progress check; `wants_read_again` (the pre-existing analog) is edge-triggered (`notify_read`, consumed once) so it does not share this flaw. `poll_flush` no-ops to `Ready` when nothing buffered, so `conn_ready` is true on the very iteration a `Pending` body left nothing new to flush. `task::yield_now` self-wakes (`cx.waker().wake_by_ref()`) rather than parking, so the 16-iteration cap does not stop the spin, it only paces it. Verifier confirmed independently, corrected the anchor/fix coordinates, and additionally established (via the related re-opened row) that the same defect produces an unbounded livelock during `is_closing`, not just a bounded/pacing cost (see §4). |
| `dispatch/poll-loop-closing-spin` | concurrency | **re-opened by verifier → re-falsified by primary → merged into `dispatch/poll-loop-write-busy-spin`'s scope, not published as a separate finding** | `src/proto/h1/dispatch.rs:149` (`ready!(self.poll_loop(cx))?` gating `is_done()` at 151, the line my own ledger row had not cited), `dispatch.rs:338-339` (`poll_write`'s `is_closing` branch), `dispatch.rs:438-442` (`close()`, which never touches `body_rx`), `conn.rs:827-830` | My original disposition ("dropped: bounded, one-time cost during teardown, exits via `is_done()` at the next level up") was **wrong**: the verifier proved `is_done()` is only reached after `poll_loop` returns `Ready`, and while `wants_write_again` stays true the loop never returns `Ready` — it keeps self-waking via `yield_now` — so `is_done()` is never evaluated during the spin and the condition is a permanent livelock, not a bounded episode. I accepted this correction (re-falsification confirms the re-open) and merged it into Finding 1 rather than publishing a second finding, since both share the identical root cause (`can_write_again`) and identical remedy — see §10 for why I chose a merge over a second finding, and why I judged no additional follow-up batch was needed to publish the merged claim. |
| `tests/ready-stream-no-assertions` | maintainability | **survivor → consider, primary-confirmed** | `tests/ready_stream.rs:240-248`; batched `grep -n "assert"` over the file (0 hits) | See Finding 2 above. Not mandatory-verification-eligible (maintainability/consider is never a mandatory-verification trigger on its own). |
| `dispatch/wants-write-again-double-flush` | bug | **dropped (no consequence)** | `src/proto/h1/dispatch.rs:174` (head) vs. the merge-base's `let _ = self.poll_flush(cx)?;` | Considered whether capturing `conn_ready` from `self.poll_flush(cx)?.is_ready()` calls `poll_flush` an extra time versus the base version. Traced: base version already called `self.poll_flush(cx)?` once per iteration; the head version calls it exactly once too, only now binding its readiness. No extra call, no side-effect duplication. Refuted, basis `contradicted` (the premise of an extra flush call is false on inspection of both base and head text). |

## 4. Sub-agent dispatches (verbatim)

### Dispatch 1 — verifier candidate batch (`v5b-verifier-effort-high`, `model: "sonnet"`, `run_in_background: false`)

**Prompt given** (verbatim, exactly as sent to the `Agent` tool):

```
You are an independent verifier for one candidate batch in the code-review-publish skill (candidate mode).
You have a completely fresh context: you do not see the primary reviewer's reasoning, only what is below.
Read references/verifier.md and references/verifier-concurrency.md at
/tmp/effort124/skill/skills/code-review-publish/references/ IN FULL before you do anything else, and follow
their evidence procedure and verdict format exactly. Do not search for new findings beyond what is below,
except the single permitted non-actionable observation aside.

RUN CONDITIONS BINDING ON YOU (same as the primary reviewer's):
1. Offline: no git fetch/pull, no gh, no curl, no network of any kind.
2. No execution: do not run cargo/rustc/miri/loom in any form. Static reasoning only; the skill's own
   scripts are exempt but you should not need them.
3. History is truncated at the pinned head (f2aa734e5699a91fc20f1178e38af7b1e374bdbc) on purpose. Do not
   try to fetch or reconstruct anything beyond it. Report explicitly whether you read any history beyond
   the pinned head and which history commands you ran, in your reply.
4. Do not mutate the clone: no git checkout/switch/reset/stash or anything that changes the tree. If you
   accidentally mutate it, run `git -C /tmp/effort124/runs/a-medium-seed3-att-06 reset --hard review-head`
   and disclose it in your reply.
5. Stay inside this sandbox only: the clone at /tmp/effort124/runs/a-medium-seed3-att-06, the skill
   snapshot at /tmp/effort124/skill/skills/code-review-publish/, and this prompt. Do not read any other
   run's clone, report, or payload, and disclose if you do.
6. You render nothing: no publication-ready prose, no trailers, no comment shapes. Return only the
   structured verdicts references/verifier.md's "Verdicts" section defines, plus the clean-verdict
   ruling on the one related row below.
7. Finish in this dispatch; do not ask anyone anything. If something is genuinely missing, say so in
   your reply rather than stopping.

REPOSITORY AND PINNED COORDINATES:
- Clone: /tmp/effort124/runs/a-medium-seed3-att-06 (local branches: `master` = merge-base
  f9f8f44058745d23fa52abf51b96b61ee7665642, `review-head` = head f2aa734e5699a91fc20f1178e38af7b1e374bdbc,
  currently checked out). You may read files from this clone directly with your own tools (e.g. Read/Grep),
  including `git show master:<path>` for base-branch text, rather than relying only on the ranges quoted
  below — the ranges below are provided for convenience but you should confirm them against the actual
  files in the clone.
- No linked issue (issues=none); no pr-title/pr-body requirement coordinate is cited by either candidate
  below, so PR text is not required for these candidates.
- No `artifact-` coordinate is cited by either candidate.

RELEVANT FILES TO READ DIRECTLY (do this yourself; ranges below are a starting pointer, not a substitute):
- `src/proto/h1/dispatch.rs` at head (currently checked out as `review-head`): the whole `impl<D, Bs, I, T> Dispatcher<D, Bs, I, T>` block, roughly lines 68-465, especially `poll_loop` (~line 130-165), `poll_write` (~line 175-260), `poll_flush`, `close`, and the new `can_write_again` method (~line 187-190).
- `src/proto/h1/dispatch.rs` at the merge-base: `git show master:src/proto/h1/dispatch.rs` and look at the same region — at the merge-base, `poll_loop`'s body only has:
  ```
  let _ = self.poll_read(cx)?;
  let _ = self.poll_write(cx)?;
  let _ = self.poll_flush(cx)?;
  if !self.conn.wants_read_again() {
      return Poll::Ready(Ok(()));
  }
  ```
  and there is no `can_write_again` method at the merge-base.
- `src/proto/h1/conn.rs` at head: `wants_read_again` (~line 428-432) and `poll_flush` (~line 827-832).
- `src/common/task.rs` at head: `yield_now` (~line 8-10).

CANDIDATE 1:
id: dispatch/poll-loop-write-busy-spin
kind: concurrency
priority: P1
action: must-fix
anchor: src/proto/h1/dispatch.rs:139-146 (RIGHT)
fix: src/proto/h1/dispatch.rs:187-190
title: poll_loop busy-spins whenever a streaming body is open but Pending
claim: `can_write_again` (`self.body_rx.is_some()`) is a coarse presence check, not a per-iteration
  progress check, so `wants_write_again` can be true on every iteration of poll_loop's bounded 16-iteration
  loop even when this iteration's poll_write made no progress because the body's poll_frame returned
  Pending, causing the loop to exhaust its 16 iterations and then self-wake via task::yield_now
  (which calls cx.waker().wake_by_ref() rather than parking), repeating indefinitely for as long as the
  body remains open — a busy-loop instead of a real wait on the body's own registered waker.
trigger: A response/request body whose poll_frame returns Poll::Pending at least once while streaming,
  with the connection not write-buffer-blocked (poll_flush is Ready because nothing new was buffered).
impact: Continuous CPU consumption on that connection's task for as long as the body remains open,
  instead of parking until the body's real waker fires. This affects any streaming body with realistic
  gaps in readiness (proxies, streamed downloads, SSE, long-poll-style handlers).
change: Track whether this iteration's poll_write call actually made write progress (e.g., whether
  poll_frame returned Ready), and gate wants_write_again on that per-iteration signal together with
  conn_ready, mirroring wants_read_again's edge-triggered semantics, rather than on body_rx presence alone.
raw code citations: see ranges above (dispatch.rs:139-146, 187-190; conn.rs 428-432, 827-832;
  common/task.rs:8-10).
requirement or rule citation: none (Code candidate, not requirement-sourced).

CANDIDATE 2 (related non-survivor row, ruled under clean-verdict task per related-acquittal mode, not a
candidate verdict):
id: dispatch/poll-loop-closing-spin
kind: concurrency
claim: During self.is_closing, poll_write and poll_read both return immediately (dispatch.rs, the
  `if self.is_closing { return Poll::Ready(Ok(())); }` branch near the top of each) without touching
  body_rx, so body_rx can remain Some while closing; wants_write_again can still evaluate true, causing
  up to 16 pointless-but-bounded iterations before the loop exits via is_done() one level up in
  poll_inner.
disposition: dropped (consequence bounded — 16 cheap iterations once during teardown, not a sustained
  spin; does not independently clear gate 1 at must-fix)
decisive evidence: src/proto/h1/dispatch.rs (is_closing branch in poll_write), and the wants_write_again
  computation in poll_loop
falsification reason: bounded, one-time cost during teardown; not proven to recur or compound.

TASK:
1. For candidate 1: follow verifier.md's Verification task steps 1-6, plus verifier-concurrency.md's
   5-step bug-class check in full (state the invariant at rule level; state whether the failing
   interleaving requires shutdown/teardown and, if not, trace a steady-state interleaving to holds/fails;
   enumerate sibling interleavings — producer body vs. poll_loop consumer, and contrast with the read
   side's wants_read_again which does NOT share this flaw; enumerate sibling code paths the rule governs;
   widen `change` to the rule level if the proposed fix is narrower than the bug class). Return exactly
   one verdict: confirmed or refuted (with basis), decisive citations, any correction to
   trigger/impact/priority/action/anchor/fix/change, and any scoped safety ruling with full 5-step
   attack depth.
2. For the related row (candidate 2): apply the clean-verdict task's procedure (restate the decisive
   premise, state the condition under which it's false, trace the opposite branch, construct or refute
   the failing transition, cite at least one line the ledger row didn't cite) and return exactly one of
   `holds` or `disposition dispatch/poll-loop-closing-spin does not hold; re-open it`.
3. You may return at most one non-actionable `observation` aside if an accurate, sub-threshold fact
   surfaces incidentally — it must not rule on either item above and must carry a decisive path:line
   citation and no `should`/`must` language.

Return your verdicts as structured records (id, verdict/ruling, basis, citations, corrections, scoped
safety rulings, bug-class widening) — not publication-ready prose. Do not write to any file. Do not
mutate the clone. At the end, explicitly state (a) whether you read any history beyond the pinned head
and which commands, and (b) whether you read any path outside the declared sandbox.
```

**Verbatim report returned by the verifier:**

```
## Verifier Report — batch for run `a-medium-seed3-att-06`

### Candidate 1: `dispatch/poll-loop-write-busy-spin`

**Verdict: confirmed**

**Basis (decisive evidence):**

- `poll_loop` (src/proto/h1/dispatch.rs:165-200) runs up to 16 iterations. Each iteration calls `poll_write` (172), then `poll_flush` (174), then computes `wants_write_again = self.can_write_again() && conn_ready` (180) and `wants_read_again = self.conn.wants_read_again()` (189); it only exits the loop via `return Poll::Ready(Ok(()))` at 192-195 when both are false. If the loop exhausts all 16 iterations it falls through to `task::yield_now(cx)` (198-200), which is `common/task.rs:8-11` — `cx.waker().wake_by_ref(); Poll::Pending` — a self-reschedule, not a park on any body-registered waker.
- `poll_write`'s body path (336-427) reaches `let item = ready!(body.as_mut().poll_frame(cx));` at line 381. `ready!` returns `Poll::Pending` from `poll_write` on a Pending `poll_frame`, without touching `body_rx` (the `OptGuard` at 368-427 only clears `body_rx` when `clear_body` is explicitly set, which never happens on this early-return branch, confirmed by `OptGuard::drop` at 504-509).
- `can_write_again` (444-447) is `self.body_rx.is_some()` — a level-triggered presence check with no reset, unlike `wants_read_again` (conn.rs:428-431), which reads-and-resets a one-shot `notify_read` flag set only at genuine state-transition sites (conn.rs:563, 1123, 1131). This is the exact edge-triggered/level-triggered asymmetry the candidate claims, and it does not affect the read side.
- Trace: with `body_rx = Some`, `poll_frame` Pending, and nothing buffered to flush, `poll_flush` (431-436 / conn.rs:827-830) returns `Ready(Ok(()))` every iteration ⇒ `conn_ready = true` ⇒ `wants_write_again = true` every iteration regardless of whether `poll_frame` made progress ⇒ loop runs all 16 iterations, then `yield_now` self-wakes and the cycle repeats indefinitely until the body itself produces data — a genuine unbounded steady-state busy spin, not a bounded event.
- Introduced-here (Code candidate, task step 4): at merge-base (`git show master:src/proto/h1/dispatch.rs`), `poll_loop` had no write-readiness looping condition at all — it unconditionally checked only `wants_read_again()` once per iteration and returned after a single pass regardless of write state. No analogous multi-iteration write-spin existed before this diff; the diff's addition of `wants_write_again`/`can_write_again` is what introduces the described spin. Nothing in the commit (`f2aa734e`, message "fix(http1): poll_loop writes when ready", no body) documents accepting this as an intentional tradeoff.

**Anchor/fix correction (material):** The supplied `anchor: dispatch.rs:139-146` and `fix: dispatch.rs:187-190` do not point at the described mechanism in this clone — 139-146 is `poll_inner`'s signature/boilerplate, and 187-190 is a comment plus the `wants_read_again` line inside `poll_loop`, not the `can_write_again` method. Corrected:
- **anchor:** `src/proto/h1/dispatch.rs:171-195` (the `poll_loop` for-body computing `wants_write_again`/`wants_read_again` and the loop-continuation decision).
- **fix:** `src/proto/h1/dispatch.rs:444-447` (`can_write_again`), read together with `165-200` (`poll_loop`) and `336-427` (`poll_write`'s Pending path).

**Scoped safety / bug-class check (verifier-concurrency.md, 5 steps):**

1. **Invariant at rule level:** The per-iteration write-continuation signal (`wants_write_again`) must be true only when this iteration made genuine forward progress on the write side (or is about to, without needing an external wakeup); it must never remain true solely because a resource (`body_rx`) still exists while blocked on an already-registered external waker. `wants_read_again`'s edge-triggered `notify_read` flag correctly implements this rule for reads; `can_write_again`'s `body_rx.is_some()` does not implement it for writes.
2. **Shutdown required? No.** Traced above as a pure steady-state interleaving (open streaming body, no error, no teardown) — **fails** in steady state, citing dispatch.rs:180, 445-447, 381, and conn.rs:827-830.
3. **Sibling interleavings:**
   - *Body producer vs. poll_loop consumer*: the producer's only channel to stop the spin is waking the registered waker `W` from `poll_frame`'s `cx`; the consumer (poll_loop) ignores that channel because it self-wakes via `yield_now`'s `wake_by_ref` after 16 iterations regardless of `W`. Fails.
   - *Write side vs. read side*: `wants_read_again` (conn.rs:428-431) does **not** share this flaw — it is consumed-and-reset, so a Pending read with no real state transition correctly yields `false` on the next check. Confirmed asymmetry.
4. **Sibling code paths governed by `can_write_again`:**
   - The `!self.conn.can_buffer_body()` / io-backpressure path (dispatch.rs:364-365, `ready!(self.poll_flush(cx))?`) is **already protected**: an unwritable io causes the outer `conn_ready` (line 174) to become `false` too, so `wants_write_again` correctly goes false. Not part of the bug.
   - The `is_closing` short-circuit path (dispatch.rs:338-339) is **not protected** — see candidate 2 below, which the primary's ledger scoped as bounded but which is in fact the same unprotected gate, with a worse (permanent) consequence.
5. **Widen `change`:** The candidate's proposed change ("track whether this iteration's poll_write call actually made write progress... gate wants_write_again on that... mirroring wants_read_again's edge-triggered semantics") is already stated at rule level and, if applied uniformly (including to the `is_closing` short-circuit, which trivially makes "no progress"), also closes the sibling `is_closing` spin reopened below. No further narrowing correction needed to `change` itself, but flag for the primary that the fix's correctness should be checked against both the Pending-body case and the `is_closing` case, since both share the same root-cause gate.

Priority/action (P1/must-fix) stand — confirmed as a genuine, common-workload, steady-state, unbounded CPU spin, not a bounded/rare event.

---

### Related row: `dispatch/poll-loop-closing-spin`

**Ruling: `disposition dispatch/poll-loop-closing-spin does not hold; re-open it`**

1. **Restated premise:** the row asserts the is_closing spin is "bounded — 16 cheap iterations once during teardown" because "the loop exits via `is_done()` one level up in `poll_inner`."
2. **Condition under which false:** if `body_rx` remains `Some` when `is_closing` becomes `true`, and the underlying io's flush keeps returning `Ready(Ok(()))` (no backpressure), then `wants_write_again` (dispatch.rs:180, `can_write_again()` at 445-447 reading only `self.body_rx.is_some()`) stays `true` on every iteration forever, since nothing on the `is_closing` path ever clears `body_rx`.
3. **Opposite branch traced:** `poll_write`'s `is_closing` branch (dispatch.rs:338-339) returns `Ready(Ok(()))` immediately, before reaching the `body_rx.is_none() && ...` head-write branch or the `OptGuard`/body-clearing branch (364-427) — `body_rx` is never read past this point, never set to `None`. `close()` itself (438-442) only sets `is_closing`, `close_read()`, `close_write()`; it never touches `body_rx` either. `conn.poll_flush` (conn.rs:827-830) calls the raw io's flush unconditionally — it does not consult `Writing::Closed` state, so it keeps returning `Ready(Ok(()))` trivially once any buffered bytes have drained.
4. **Complete failing transition:** t0 — `poll_read_head`'s `dispatch.poll_ready` returns `Err(())` (dispatch.rs:281-288) while a response `body_rx` is actively streaming (a realistic case: graceful-shutdown signal arrives mid-SSE/streamed response) → `self.close()` sets `is_closing = true` (285, 438-442). t1 — every subsequent `poll_write` call short-circuits at 338-339, `body_rx` permanently `Some`. t2 — `poll_flush` returns `Ready(Ok(()))` (conn.rs:827-830) ⇒ `conn_ready = true`. t3 — `wants_write_again = true && true = true` every iteration (180, 445-447); `wants_read_again` false. t4 — the loop never reaches the `return Poll::Ready(Ok(()))` exit (192-195), runs all 16 iterations, then `task::yield_now` (198-200 / common/task.rs:8-11) returns genuine `Poll::Pending` and self-wakes via `wake_by_ref`. t5 — `poll_inner`'s `ready!(self.poll_loop(cx))?` (149) propagates that `Pending` immediately, so `is_done()` (151, 449-464) is **never evaluated** in this cycle — the "exits via `is_done()` one level up" premise the row relies on never fires. t6 — the self-wake reschedules the task immediately; t1-t5 repeat indefinitely. Net effect: not a bounded 16-iteration event but a permanent busy-spin/livelock that also prevents the connection from ever reaching shutdown while this state persists.

**Decisive citations not cited by the ledger row:** dispatch.rs:149 (`ready!(self.poll_loop(cx))?` — shows `is_done()` at 151 is gated behind `poll_loop` returning `Ready`, never reached while the spin continues), dispatch.rs:445-447 (`can_write_again`), conn.rs:827-830 (`poll_flush` ignores `Writing` state), dispatch.rs:198-200 and common/task.rs:8-11 (`yield_now` self-wakes rather than parking).

This re-open shares candidate 1's root cause (the same `can_write_again` gate) but has a more severe, unbounded consequence (permanent livelock blocking shutdown, not a one-time bounded cost), so the primary should consider merging its severity signal into candidate 1's fix scope rather than treating it as a separately dropped, low-consequence row.

---

### Observation aside

None offered — no additional sub-threshold fact surfaced that doesn't already bear on the two rulings above.

---

### Disclosures

(a) History read beyond the pinned head: none. Commands run were local-only and did not fetch or reconstruct anything past `f2aa734e5699a91fc20f1178e38af7b1e374bdbc`: `git log --oneline -5 review-head`, `git log --oneline -5 master`, `git rev-parse HEAD`, `git show master:src/proto/h1/dispatch.rs` (merge-base file text), `git show f2aa734e... --stat`, `git log -1 --format=%B f2aa734e...`. No fetch/pull/network commands were used.

(b) Sandbox: all files read were within `/tmp/effort124/runs/a-medium-seed3-att-06` (src/proto/h1/dispatch.rs, src/proto/h1/conn.rs, src/common/task.rs) and `/tmp/effort124/skill/skills/code-review-publish/references/` (verifier.md, verifier-concurrency.md). No other run's clone, report, or payload was read. The clone was not mutated (read-only `Read`/`Grep`/`git show`/`git log` only).

<usage>subagent_tokens: 78929 tool_uses: 21 duration_ms: 422414</usage>
```

**Note on the verifier's own history commands:** the verifier ran `git log --oneline -5 review-head`, `git log --oneline -5 master`, `git rev-parse HEAD`, `git show master:src/proto/h1/dispatch.rs`, `git show f2aa734e... --stat`, and `git log -1 --format=%B f2aa734e...`. Every one of these reads content *at or before* the pinned head/merge-base (a `git show`/`git log -1` of the pinned head itself, and of the merge-base branch tip, is not a traversal past the pinned boundary); none of these commands fetch or reconstruct anything beyond `f2aa734e5699a91fc20f1178e38af7b1e374bdbc`, consistent with the run conditions.

## 5. Everything consulted beyond the diff

All reads below were performed by me (the primary reviewer) in this same context, not delegated, except where explicitly attributed to the verifier dispatch in §4.

- `python3 scripts/review_context.py --merge-base f9f8f44058745d23fa52abf51b96b61ee7665642 --head f2aa734e5699a91fc20f1178e38af7b1e374bdbc --store <tmpdir>/review-context-f2aa734e5699a91fc20f1178e38af7b1e374bdbc.json` — run once, from inside the clone (`/tmp/effort124/runs/a-medium-seed3-att-06`), invoking the script by absolute path from the skill snapshot. The diff section came back `withheld` (26769 bytes across 3 chunks vs. a 22791-byte bound left after the manifest/ranges/history sections). Not repo-wide/case-insensitive (not a search).
- `python3 scripts/review_context.py --from <store> --path Cargo.toml --chunk 1` — recovered the Cargo.toml diff chunk (537 bytes, consumed).
- `python3 scripts/review_context.py --from <store> --path src/proto/h1/dispatch.rs --chunk 1` — recovered the dispatch.rs diff chunk (17172 bytes, consumed). This chunk already carried full function context for the entire `impl` block (unified-diff hunk spanning lines 68-465 @head / 68-452 @merge-base), so no separate `--function-context` flag was needed. **Caveat (see §10):** the diff's hunk-relative line numbers in the unified-diff header do not equal the real file's absolute line numbers once counted past the hunk's own `@@` marker offsets; I initially mis-transcribed candidate coordinates from the diff text directly instead of re-reading the actual file, which the verifier caught and corrected (§4). I then independently confirmed the corrected coordinates with a direct `Read`/`grep -n` of the real file (below).
- `python3 scripts/review_context.py --from <store> --path tests/ready_stream.rs --chunk 1` — recovered the ready_stream.rs diff chunk (9060 bytes, consumed). This is a new file, so per the rubric it is already fully present in the diff and not read again.
- `## chunks` inventory after all three reads: `diff coverage: complete (3/3 chunks consumed)` — confirms no omitted patch remains.
- `git -C /tmp/effort124/runs/a-medium-seed3-att-06 log --oneline -5 review-head` — confirmed the pinned head commit and its immediate ancestry (`f2aa734e`, `7ed95afc`, `f9f8f440`, `5803a9c0`, `e1e1f2b4`) matches the packet's commit table; this is history *at or before* the pinned head only (no read beyond it).
- `git -C /tmp/effort124/runs/a-medium-seed3-att-06 diff master review-head --stat` — confirmed the changed-file manifest and line counts match the packet's manifest exactly (`Cargo.toml +6/-0`, `src/proto/h1/dispatch.rs +15/-2`, `tests/ready_stream.rs +249/-0`).
- `git -C /tmp/effort124/runs/a-medium-seed3-att-06 status` — confirmed a clean working tree before starting (no pre-existing mutation to disclose).
- `grep -n "fn wants_read_again" -A 15 src/proto/h1/conn.rs` (single file, case-sensitive, not repo-wide) — read `Conn::wants_read_again`'s edge-triggered `notify_read` semantics, decisive for falsifying/confirming the busy-spin candidate.
- `cat src/common/task.rs` (whole file, 43 lines — under the rubric's ≤300-line whole-file-read allowance) — read `task::yield_now`'s self-wake (`cx.waker().wake_by_ref()`) semantics, decisive for the same candidate.
- `grep -n "fn poll_flush" -A 25 src/proto/h1/conn.rs` (single file, case-sensitive, not repo-wide) — read `Conn::poll_flush`'s no-op-when-empty behavior, decisive for confirming `conn_ready` is `true` on a `Pending`-body iteration.
- `grep -n "assert" tests/ready_stream.rs` and `grep -n "TOTAL_CHUNKS\|CHUNK_SIZE\|bytes_received" tests/ready_stream.rs` (single new file, case-sensitive) — confirmed zero assertions in the new test, decisive for Finding 2.
- `sed -n '1,30p;55,90p' Cargo.toml` and `grep -n '^tracing\|"tracing"\|\[features\]' Cargo.toml` — confirmed the new `tracing-subscriber` dependency and `[[test]] ready_stream` block sit in the pre-existing dev-dependency/test-registration conventions (an existing `tracing` optional feature and an existing `required-features = ["full", "tracing"]` pattern used elsewhere at line 109), so no Cargo.toml candidate was admitted.
- `git -C /tmp/effort124/runs/a-medium-seed3-att-06 show master:CONTRIBUTING.md | head -80` — read the base-branch `CONTRIBUTING.md` present at the merge-base per the packet's §7 guidance table. Classified as **not** a `guidance` file for the digest (it is not `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md`, the only three categories the output contract's digest definition admits) and, on reading, it carries no repository-specific coding standard bearing on this diff (generic contribution-process document: code of conduct, issue triage, PR process links, documentation notes) — so no repository-rule finding was manufactured from its mere existence, per the rubric's "do not manufacture findings because a rule file exists."
- `grep -rn "hyper_unstable_tracing"` scoped to `src/` (two files: `src/trace.rs`, `src/lib.rs`) — confirmed the PR body's `RUSTFLAGS='--cfg hyper_unstable_tracing'` invocation is pre-existing crate-internal tracing infrastructure unrelated to the new test's direct use of the `tracing` crate macros, so the new test does not depend on that cfg to compile or run; no candidate followed from this.
- `python3 scripts/context_fingerprint.py /tmp/effort124/work/a-medium-seed3-att-06/fingerprint_input.json` — computed the `context` digest once (see §6).
- **After the verifier's correction**, I re-confirmed the real file's line numbers myself directly: `grep -n "fn poll_loop\|wants_write_again\|wants_read_again\|fn can_write_again\|fn poll_write\|is_closing\|yield_now" src/proto/h1/dispatch.rs`, then `Read` of `dispatch.rs` at offset 165/limit 36, offset 336/limit 6, and offset 440/limit 10, to verify `poll_loop` at 165-200, `wants_write_again` at 180, `wants_read_again` at 189, the loop guard at 192-195, `poll_write`'s `is_closing` branch at 338-339, `close()` at 438-442, and `can_write_again` at 445-447 — all matching the verifier's corrected coordinates exactly.

**Focused test execution:** none run. Per the run conditions (binding, packet §8 item 2) execution of `cargo`/`rustc` in any form is disallowed offline; the rubric's Changed-tests section states this as "unavailable execution... stated as unavailable... it never becomes a pass." I traced `body_test`'s decisive lines by semantics instead (see Finding 2 and the ledger), which the rubric permits and treats as settling the case without needing execution, since the trace itself (zero assertions) is fully decisive by inspection.

## 6. Context digest and its inputs

- **Digest:** `13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5`
- **Computed with:** `python3 scripts/context_fingerprint.py <input.json>` (no `--packet` flag, since no `forge_packet.py normalize` output exists in this offline cell — the packet supplied is a pre-resolved Markdown packet, not raw forge JSON pages. Per `SKILL.md`/output-contract.md: "On a forge without that packet, supply `pr`, `issues`, `specs`, and `guidance` directly from the exact reviewed inputs.")
- **Inputs supplied** (`/tmp/effort124/work/a-medium-seed3-att-06/fingerprint_input.json`):
  - `pr.title`: `"fix(http1): poll_loop writes when ready"` (packet §1/§3)
  - `pr.body`: the verbatim pull-request body reproduced in packet §3
  - `issues`: `[]` (packet: "Originating issue(s): none — the PR body carries no closing reference; `issues=none`")
  - `specs`: `[]` (no user-supplied spec)
  - `guidance`: `[]` — per output-contract.md's exhaustive membership rules (root/path-scoped `AGENTS.md`/`CLAUDE.md`, root `CONTEXT.md` only), and packet §7 confirms none of those three files exist at the merge-base; `CONTRIBUTING.md` exists but is explicitly outside the digest's `guidance` categories.
  - `comments_available` / `comments_complete`: not applicable — no issues, so no issue-comment connection exists to mark.

## 7. Mechanism checklist

- **Question channel:** did not fire. No candidate met the static-unresolvability bar (every candidate I raised was fully decidable from the diff, unchanged surrounding code, and cited history — no empirical/runtime fact or unrecorded product decision was needed). 0 questions published.
- **Clean-verdict or related-acquittal verification:** related-acquittal mode fired, not zero-survivor mode. At least one candidate (`dispatch/poll-loop-write-busy-spin`) survived as a finding requiring mandatory verification, so the initial candidate batch was dispatched; the related non-survivor row `dispatch/poll-loop-closing-spin` (same `kind=concurrency`, same file, same claimed state — `wants_write_again`/`can_write_again`) rode that same batch under the related-acquittal criteria and received a **`re-open`** ruling (§4), citing a line (`dispatch.rs:149`) my own ledger row had not cited — satisfying the clean-verdict task's step 5 requirement that a ruling cite at least one line the row itself did not. The re-opened row re-entered primary falsification (§3); I accepted the correction and merged its (worse) consequence into Finding 1's scope.
- **Observations:** did not publish any. The verifier offered none (its "Observation aside" section explicitly returned nothing). 0 observations in the payload.
- **Fix-sufficiency check on the concurrency candidate:** yes — the verifier's concurrency bug-class check (§4) explicitly stated the rule-level invariant, ran the shutdown-vs-steady-state question (answered: does NOT require shutdown; a pure steady-state interleaving fails), enumerated sibling interleavings (producer-vs-consumer on the write side: fails; write-vs-read: read side unaffected), enumerated sibling code paths (the `!can_buffer_body` backpressure path: already protected via `conn_ready`; the `is_closing` path: not protected, and in fact worse than the ledger's original disposition claimed), and confirmed `change` was already rule-level as submitted, while flagging that the fix's implementation must be checked against both manifestations.
- **Follow-up verifier round:** not run. Only one candidate batch was dispatched. A row was re-opened (`dispatch/poll-loop-closing-spin`), which under the skill's rules is eligible to ride "the existing follow-up batch" — but I judged (§10) that the same fresh-context verifier had already produced complete, decisive, cited evidence for the re-opened row's merged claim within this one batch, so no second batch was needed to publish the merged finding. Total batches used: 1 of the allowed 1-initial-plus-1-follow-up cap.
- **Deferral handling:** the pre-merge review thread on `tests/ready_stream.rs:18` contains an explicit deferral by `lthiery`: "I'll still take another critical pass at what I've done here next week and I'll see what I can do to simplify," about test *simplification*, and `seanmonstar`'s own general review comment ("since we're essentially 'selecting' over read and write, we need to make sure both sides either registered a waker, or that we will poll again with the `yield_once` util") describes the *intended* correctness property the fix should have — which the busy-spin/livelock finding shows the implementation did not fully achieve (it satisfies "we will poll again" in the narrow sense of looping, but via an imprecise presence-based spin rather than a precise per-iteration progress signal or a genuinely registered waker, and in the `is_closing` case it doesn't even reliably "poll again" toward completion — it livelocks). Per the rubric, an explicit deferral marks the deferred question *open*, not accepted; I treated the test-simplification deferral as open but not dispositive for Finding 2 (the deferral concerned setup complexity, not the specific missing-assertion claim), and treated `seanmonstar`'s approval as covering only what the review record explicitly discussed (the waker-registration goal in the abstract), not the specific coarse-presence-check implementation detail that Finding 1 identifies — so gate 6 (unintentional) is not defeated for either finding.
- **Retrospective mode:** fired as instructed by the packet and run conditions. The target is `merged=true`; this run followed the skill through to the point of publication and rendered the complete would-be review instead of writing anything, with the mandatory `Mode` line included in the payload (`/tmp/effort124/reports/a/a-medium-seed3-att-06-payload.md`).

## 8. History discipline

I read no history beyond the pinned head (`f2aa734e5699a91fc20f1178e38af7b1e374bdbc`). The only history-adjacent commands run by me were:

- `git -C /tmp/effort124/runs/a-medium-seed3-att-06 log --oneline -5 review-head` — lists the pinned head and four ancestors, all at or before the pinned head.
- `git -C /tmp/effort124/runs/a-medium-seed3-att-06 diff master review-head --stat` — a diff between the pinned merge-base and pinned head, not a history traversal.
- `git -C /tmp/effort124/runs/a-medium-seed3-att-06 show master:CONTRIBUTING.md` — reads a file's content *at* the pinned merge-base (`master`), not history beyond it.
- `git -C /tmp/effort124/runs/a-medium-seed3-att-06 status` — working-tree status only.

No `git log` beyond `-5` from the pinned head, no `git fetch`/`git pull`, no traversal past `f2aa734e5`. The verifier sub-agent's own commands (`git log --oneline -5 review-head`, `git log --oneline -5 master`, `git rev-parse HEAD`, `git show master:src/proto/h1/dispatch.rs`, `git show f2aa734e... --stat`, `git log -1 --format=%B f2aa734e...`) are reproduced verbatim in §4 and likewise stay at or before the pinned boundary.

## 9. Sandbox disclosure

No path outside the declared sandbox (the clone at `/tmp/effort124/runs/a-medium-seed3-att-06`, the skill snapshot at `/tmp/effort124/skill/skills/code-review-publish/`, the packet directory at `/tmp/effort124/packets/a/`, and my own work/report/payload/timing paths under `/tmp/effort124/work/a-medium-seed3-att-06/` and `/tmp/effort124/reports/a/`) was read by me or, per its own disclosure, by the verifier sub-agent.

## 10. Notes — judgment calls on ambiguities

- **No `forge_packet.py normalize` packet.json existed** (this cell supplies a pre-resolved Markdown packet, not raw GraphQL pages, per the dispatch's binding offline condition). I treated this as the documented "forge without that packet" branch of the `context` digest instructions and supplied `pr`/`issues`/`specs`/`guidance` directly, rather than treating the missing `packet.json` as an unrecoverable input under the rubric's Uncertainty routing — the packet's own preamble states "Phase 1... has already been performed by the orchestrator," and packet §8 states this phase is satisfied by the packet itself, so I read this as the intended substitution, not a gap.
- **`CONTRIBUTING.md` guidance classification:** I read it (present per packet §7) but excluded it from the digest's `guidance` array, since the output contract's `guidance` definition is an exhaustive three-category list (`AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`) that does not include `CONTRIBUTING.md`. I still read it for review purposes (repository-rule applicability), consistent with "Apply root and path-scoped instruction files... with normal precedence," but it turned out to carry no repository-specific rule bearing on this diff.
- **My own candidate coordinates were initially wrong, and the verifier caught it.** When I drafted the candidate record for the verifier batch, I copied line numbers from the unified-diff hunk text (which uses hunk-relative `@@ -a,b +c,d @@` offsets) rather than re-reading the real post-diff file's absolute line numbers, producing an anchor/fix that pointed at the wrong statements (`poll_inner`'s signature instead of `poll_loop`'s body; a comment line instead of `can_write_again`). The verifier, which read the actual files directly rather than trusting my supplied ranges, caught and corrected this. This is a real methodological gap in how I built the candidate record (I should have re-read the actual file before finalizing coordinates, as the rubric's "confirm a valid, minimal changed-line or file anchor" falsification step requires) rather than a case where the reference material was ambiguous; I disclose it plainly rather than characterizing it as a defensible judgment call. I independently re-verified the corrected coordinates myself afterward (§5) before publishing.
- **Merging the re-opened `is_closing` row into Finding 1 instead of dispatching a follow-up batch and/or publishing a second finding:** the skill's text says a re-opened row "re-enters primary falsification" and that newly render-eligible records (including re-opened dispositions) ride "at most one fresh follow-up batch." I judged that dispatching a *second* verifier batch here would have asked a fresh context to re-verify a claim that the *same* fresh-context verifier had already independently traced to a fully cited, decisive conclusion within the very batch that re-opened it (the clean-verdict ruling on `dispatch/poll-loop-closing-spin` already is a complete, cited, adversarial trace — not a primary assertion the verifier merely agreed with). Since the follow-up-batch machinery exists to give an *unverified* new/re-opened claim its mandatory fresh-context check, and this claim already received exactly that check as part of discharging the related-acquittal ruling, I treated the requirement as already satisfied and did not spend the follow-up batch. This is a genuine judgment call under ambiguous wording, and I flag it explicitly as such: a stricter reading could require spending the follow-up batch regardless, purely because the row was formally "re-opened." I chose the reading that avoids a redundant re-verification of already-cited, already-adversarially-traced evidence, but I record the alternative reading here for the record.
- **Publishing one merged finding instead of two:** having accepted the re-open, I judged the shared root cause (`can_write_again`) and shared remedy made two separate, overlapping findings on the same three lines confusing rather than more useful, and merged them into Finding 1's `claim`/`trigger`/`impact`, raising its priority from P1 to P0 to reflect the more severe (livelock, not just CPU-wasting) manifestation. An alternative reading could have kept them as two findings (a P1 CPU-spin finding and a separate P0/livelock finding) with cross-references; I judged one finding describing both manifestations of the identical defect was clearer and avoided implying two separate remedies were needed.
- **Finding 1's kind:** I used `kind=concurrency` rather than `kind=performance`, because the defect is precisely a broken cross-path state rule (the write-continuation signal's relationship to the read-continuation signal and to the loop's termination guarantee) that benefits from — and received — the verifier's concurrency bug-class check (invariant statement, steady-state trace, sibling interleaving/path enumeration, sibling code-path enumeration). This is a judgment call the rubric explicitly permits ("Use `concurrency` or `invariant` when sibling paths share the broken state rule").
- **No repository CI logs were available to me** (offline, no network) to check whether `tests/ready_stream.rs` is actually exercised in CI at all, or whether any `--cfg hyper_unstable_tracing`-gated feature might affect it; I did not claim CI executed or would execute this test, and the payload's Coverage line states focused execution was unavailable rather than implying a pass.
- **Finding 2's evidence budget:** the rubric caps evidence at "at most two decisive evidence facts" for an ordinary finding; I used one (`tests/ready_stream.rs:240-248` plus the batched `grep` result, treated as a single decisive fact — "zero assertions in the file") to stay within budget while still being falsifiable and specific.

Payload file: [`/tmp/effort124/reports/a/a-medium-seed3-att-06-payload.md`](file:///tmp/effort124/reports/a/a-medium-seed3-att-06-payload.md)
