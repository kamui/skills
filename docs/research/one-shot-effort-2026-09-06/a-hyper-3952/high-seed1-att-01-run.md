# Research report — cell `a-high-seed1`, attempt `att-01`

## 1. Metadata

- **Target:** `hyperium/hyper#3952` — "fix(http1): poll_loop writes when ready" (author `lthiery`, association CONTRIBUTOR)
- **Cell/attempt:** `a-high-seed1` / `att-01`
- **Skill:** `legacy reviewer` at the snapshot pinned in `/tmp/effort124/skill/snapshot-path-omitted/` (workflow version `v5b-10` per `references/output-contract.md`)
- **Primary model:** `claude-sonnet-5` (this session)
- **Sub-agent model:** every sub-agent dispatched with `model: "sonnet"` (only sub-agents spawned are the mandatory verifier batch(es), `subagent_type: "v5b-verifier-effort-high"`) — recorded verbatim below as they are dispatched.
- **Verification trigger fired:** yes — one surviving candidate is proposed `must-fix` and has `kind: concurrency`, which is a mandatory-verification trigger under `SKILL.md` step 3. No zero-survivor clean-verdict mode fired (at least one candidate survived). No related-acquittal rows attach (checked below).
- **Run identity (from the packet, pinned verbatim, not re-resolved):**
  - Repository: `hyperium/hyper`; `summary.repository_url` = `https://github.com/hyperium/hyper`
  - Head SHA: `f2aa734e5699a91fc20f1178e38af7b1e374bdbc` (local branch `review-head`)
  - Base ref: `master`; Base SHA / merge-base: `f9f8f44058745d23fa52abf51b96b61ee7665642` (identical)
  - `state`: `MERGED`; `merged`: `true` (2025-11-10T14:51:16Z); `isDraft`: `false`
  - Posting identity: `kamui` — no prior comments/reviews from this identity on the PR → **first review, not a re-review**
  - Originating issue(s): none (`issues=none`); ledger built from PR title+body only
  - **Retrospective mode:** target is merged → publication disabled by default; this run renders the complete would-be review and stops, per the packet's binding condition and the skill's Boundaries section.
- **Coverage (final):** complete — all 3 changed files reviewed (diff chunks: 3/3 consumed per the context store's `## chunks` inventory), all risk-directed checks resolved with evidence, no fetch/packet gaps (this is an offline packet with no forge pagination to track).
- **Derived status:** `Changes Requested (advisory)` — see §status derivation below.
- **Token usage:** not reported to me by the harness in a form I can quote; I have no per-call token counter available in this environment, so I state plainly that I cannot report it rather than estimating.

## 2. Pin the review (step 1)

Performed entirely from the packet (`/tmp/effort124/packets/a/packet.md`), per the run conditions' offline rule. I additionally checked, from the local clone (a local read, not a network resolution), whether `docs/agents/issue-tracker.md` exists at the base branch, since `SKILL.md` step 1 names it explicitly and the packet's guidance table (§7) does not enumerate it:

```
git show master:docs/agents/issue-tracker.md
→ fatal: path 'docs/agents/issue-tracker.md' does not exist in 'master'  (exit 0, git reports the fatal message but the shell command itself returned normally)
```
Absent. No further action.

**Re-review check (judgment call):** The packet records substantial *prior* review state (from `seanmonstar` and `lthiery`), but none of it is from the posting identity `kamui`. `SKILL.md` step 1 triggers `references/re-review.md` only "when step 1 finds prior state from the posting identity." Since `kamui` has no prior comments/reviews on this PR, I treated this as a **first review** and did not apply the re-review reference's duplicate-review shortcut, delta-scope, or prior-item classification machinery. I did, however, read `re-review.md` for context and applied the packet's separate mandatory note: existing review threads and non-review comments from other participants are read as evidence for gate 6 (Unintentional / deliberate-acceptance) during falsification, not as "prior findings of this reviewer" requiring reply threads.

**Conformance check (judgment call):** `references/conformance.md` loads "when a source names a versioned artifact in step 2." Nothing in the PR body, diff, or repository convention here tracks a versioned schema, generated source, or SDK/binding release. I did not load it.

## 3. Repository guidance (step 1, continued)

Per the packet's §7 table (verified against the mirror, taken as authoritative pinned input, not re-checked): no `AGENTS.md`, `CLAUDE.md`, or `CONTEXT.md` at the merge-base, anywhere. `CONTRIBUTING.md` is present (blob `66043e1c…`). I read it in full from the base branch (`git show master:CONTRIBUTING.md`, 100 lines — under the ≤300-line whole-file threshold, so no "decision to record" was needed for reading it whole). It is a contributor-onboarding document (code of conduct, issue triage, links to `docs/PULL_REQUESTS.md`/`docs/COMMITS.md`, documentation and community-help guidance) with no coding standard, lint rule, or concurrency/API convention bearing on this diff. I classified it as **read, applicable-scope-checked, no repository-rule finding arises from it** — it contributes no rows to the `guidance` digest field either way, since the output contract's `guidance` category is restricted to `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md`, none of which exist here.

**`guidance` for the digest: `[]` (empty — no root or path-scoped `AGENTS.md`/`CLAUDE.md`, no root `CONTEXT.md`).**

## 4. Manifest (step 2)

```
M  Cargo.toml                    +6   −0
M  src/proto/h1/dispatch.rs      +15  −2
A  tests/ready_stream.rs         +249 −0
```

All three files: **reviewed**. None ignored, none unreviewed.

## 5. Requirement (Issue fit) ledger — built before reading the diff for compliance

No originating issue (`issues=none`); ledger built from the PR title and body alone, per the rubric's Issue fit section.

| Row | Source coordinate | Class | Text | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- |
| R1 | `pr-body/"if the poll_write is demonstrating readiness to write and the connection has readiness to write, we should do that or else hyper may stall"` | acceptance requirement | The loop must perform a write whenever poll_write demonstrates write-readiness and the connection is write-ready, or hyper may stall. | **partial** | The specific reported deadlock (the outer loop exiting before consuming a body write that became possible only because the connection just finished flushing) is fixed: `wants_write_again`/`conn_ready` (`src/proto/h1/dispatch.rs:174,180,192`) now keeps the loop going instead of returning early. But the implementation checks whether *a body exists* (`can_write_again()` = `body_rx.is_some()`, `src/proto/h1/dispatch.rs:445-447`), not whether *poll_write actually demonstrated readiness* this cycle — a materially broader condition than what the promise states. See finding `dispatch/poll-loop-write-again-overbroad` below. |
| R2 | `pr-body/"I built a pathological example \"ready_stream.rs\" - you can run it from this branch with: RUSTFLAGS='--cfg hyper_unstable_tracing' cargo test --test ready_stream --features full,tracing"` | supporting assertion | A repro test exists at `tests/ready_stream.rs` and is runnable with the quoted invocation. | **met** | `tests/ready_stream.rs` exists (249 new lines); `Cargo.toml:243-246` registers `[[test]] name = "ready_stream" path = "tests/ready_stream.rs" required-features = ["full", "tracing"]`, matching `--features full,tracing`; the `tracing` feature is documented "currently unstable" (`Cargo.toml:95-96`) and gated by the `hyper_unstable_tracing` cfg used identically in CI's own tracing-feature job (`.github/workflows/CI.yml:170-173`), matching the quoted `RUSTFLAGS` invocation exactly. (Not independently executed — see run conditions, no `cargo`.) |
| — | `pr-title` "fix(http1): poll_loop writes when ready" | — | Restates R1 in compressed form. | (no separate row — a title that restates the body's promise adds none, per the rubric.) | — |

**Issue fit summary:** Partial — the reported stall is fixed for the narrow scenario described, but the fix's write-again condition is broader than the promise, with a proven, concrete cost (§6 below).

## 6. Diff read (step 3) and everything consulted beyond it

### 6.1 Diff acquisition

Built the private context store once:
```
python3 /tmp/effort124/skill/snapshot-path-omitted/scripts/review_context.py \
  --merge-base f9f8f44058745d23fa52abf51b96b61ee7665642 \
  --head f2aa734e5699a91fc20f1178e38af7b1e374bdbc \
  --store /tmp/effort124/work/a-high-seed1-att-01/private/ctxC5Gs/review-context-f2aa734e5699a91fc20f1178e38af7b1e374bdbc.json
```
run from cwd `/tmp/effort124/runs/a-high-seed1-att-01` (the clone), exit 0. The private store directory was created with `mktemp -d` under my own per-attempt work directory (`/tmp/effort124/work/a-high-seed1-att-01/private/ctxC5Gs`), not a shared/predictable `/tmp` path, per step 2's warning.

The build call withheld the diff (26769 bytes across 3 chunks vs. a 22791-byte bound left after the manifest/ranges/history sections). Per the recovery procedure, I read it back from the store rather than rebuilding:
```
python3 …/review_context.py --from <store> --path Cargo.toml --path tests/ready_stream.rs
python3 …/review_context.py --from <store> --path src/proto/h1/dispatch.rs
```
Final `## chunks` inventory: `diff coverage: complete (3/3 chunks consumed)`. The complete merge-base diff was read exactly once; no per-file `git show` reread of the diff itself was used (only bounded reads of *unchanged* surrounding files, below, which is not the diff).

### 6.2 The diff itself (summary; full text was read via the store, not pasted twice here)

- **`Cargo.toml`** (+6/−0): adds `tracing-subscriber = "0.3"` under `[dev-dependencies]` (confirmed by section-header grep, line 45–70 range) and a new `[[test]] name = "ready_stream" path = "tests/ready_stream.rs" required-features = ["full", "tracing"]` entry alongside three siblings (`client`, `integration`, `server`), all of which require only `["full"]`.
- **`tests/ready_stream.rs`** (new, 249 lines — under the 300-line whole-file threshold, and a new file is already fully present in the diff, so no separate whole-file read was needed): a hand-rolled `TxReadyStream` transport (`Read`/`Write` impl over `mpsc` channels) whose `poll_write` only accepts a write once per "armed" cycle and whose `poll_flush` requires two calls per chunk to complete (deterministically reproducing the "ready-without-a-future-wakeup" pattern the PR describes), plus one `#[tokio::test(flavor = "multi_thread", worker_threads = 2)] async fn body_test()` that serves 16×64KiB chunks over this mock transport and drains the client side.
- **`src/proto/h1/dispatch.rs`** (+15/−2): the functional fix. `Dispatcher::poll_loop`'s termination condition changes from `if !self.conn.wants_read_again() { return Poll::Ready(Ok(())); }` to computing `conn_ready = self.poll_flush(cx)?.is_ready()`, `wants_write_again = self.can_write_again() && conn_ready`, `wants_read_again = self.conn.wants_read_again()`, and returning only `if !(wants_write_again || wants_read_again)`. A new private method `can_write_again(&mut self) -> bool { self.body_rx.is_some() }` is added, documented as "If there is pending data in body_rx, we can make progress writing if the connection is ready."

### 6.3 Bounded reads of unchanged code (risk-led discovery, per the rubric's Complete inspection section — each serves the named risk of the changed behavior: concurrency/waker liveness around the "select" the maintainer's own review comment names)

| Read | Range | Risk served | Decisive outcome |
| --- | --- | --- | --- |
| `src/proto/h1/conn.rs` | `wants_read_again` L428-432 | confirm the pre-existing read-side signal is narrow/self-resetting, not a persistent flag | `notify_read` is read-then-cleared in one line; it is set only by specific internal state transitions elsewhere in `conn.rs`, not "true whenever more reading is conceivable." This is the asymmetry that makes the *new* `can_write_again` (persistent while `body_rx.is_some()`, no auto-narrowing) a materially different, newly introduced condition, not a mirror of an existing pattern. |
| `src/proto/h1/conn.rs` | `can_write_head`/`can_write_body`/`can_buffer_body` L572-592 | confirm `can_write_body()` stays `true` for the whole `Writing::Body(..)` state, independent of whether the body has data ready this instant | Confirmed — `can_write_body()` only reflects the coarse `Writing` state enum, not data availability. |
| `src/proto/h1/conn.rs` | `Conn::poll_flush` L827-832 | confirm what "connection ready" (`conn_ready`) actually measures | `ready!(Pin::new(&mut self.io).poll_flush(cx))?` then trivially `Poll::Ready(Ok(()))` — delegates directly to the buffered-IO layer. |
| `src/proto/h1/io.rs` | `Buffered::poll_flush` L267-301 | confirm whether an empty write buffer makes `conn_ready` trivially/always `true` | `if self.write_buf.remaining() == 0 { Pin::new(&mut self.io).poll_flush(cx) }` — when nothing is buffered (the common steady state while waiting on a paused body), flush degrades to the *raw transport's* `poll_flush`, which for a real `TcpStream` is a documented no-op returning `Poll::Ready(Ok(()))` unconditionally (TCP has no userspace flush semantics). This settles that `conn_ready` is essentially always `true` whenever there is nothing queued to write — the condition this finding turns on. |
| `src/common/task.rs` | `yield_now` L1-11 | confirm what happens after 16 spins | `pub(crate) fn yield_now(cx: &mut Context<'_>) -> Poll<std::convert::Infallible> { cx.waker().wake_by_ref(); Poll::Pending }` — an explicit, unconditional self-wake, documented "so a future doesn't hog too much time," i.e. it bounds one `poll()` call's CPU, but does **not** avoid the task being rescheduled immediately. |
| `Cargo.toml` | `[[test]]` entries, whole-file grep | establish the sibling convention for the new test-target entry (rubric's "new entry in a file whose siblings carry variant markers" check) | `grep -n "^\[\[test\]\]" -A3 Cargo.toml` → the three sibling test targets (`client`, `integration`, `server`) all declare `required-features = ["full"]`; `ready_stream` is the only one that adds `"tracing"`. This is the batched, sibling-convention search the rubric requires before treating a new entry's divergence as a candidate. |
| `.github/workflows/CI.yml` | `test` job L54-96; `features` job L149-173 | establish whether CI ever actually *executes* `tests/ready_stream.rs` | The only job that runs `cargo test` (`test`, L91-92: `cargo test ${{ matrix.features }}`) uses `--features full`/`--features full,nightly` — never `tracing`. The only job that enables `tracing` (`features`, L170-173) runs `cargo hack … check`, never `test`. So `tests/ready_stream.rs`, gated on `required-features = ["full", "tracing"]`, is never compiled or run by any CI job. |

All of the above are unchanged files/ranges at head (identical to merge-base for the cited lines — I did not need `git show <merge-base>` diffing for these since none of them are part of the diff and none of the cited lines fall in a changed region); they were read to establish the guarantee the changed `poll_loop` code now depends on, per the rubric's risk-led discovery allowance, and each read is recorded above as one line with its risk and decisive outcome, per the rubric's discipline.

### 6.4 Batched searches (all run from the clone root `/tmp/effort124/runs/a-high-seed1-att-01`)

- `grep -n "fn poll_loop\|wants_write_again\|conn_ready\|wants_read_again\|fn can_write_again\|task::yield_now" src/proto/h1/dispatch.rs` — single-file, case-sensitive. Located exact line numbers for the anchor/fix.
- `grep -n "fn poll_flush\|fn wants_read_again\|fn can_write_body\|fn can_buffer_body\|fn can_read_body\|fn can_read_head" src/proto/h1/conn.rs` — single-file, case-sensitive. Located the unchanged-guarantee functions read in §6.3.
- `grep -rn "fn yield_now\|mod task" src/` — repo-wide under `src/`, case-sensitive. Located `src/common/task.rs`.
- `grep -n "tracing" Cargo.toml` and `grep -n "^\[\[test\]\]" -A3 Cargo.toml` — single-file, case-sensitive.
- `grep -rln "hyper_unstable_tracing" .` — **repository-wide**, case-sensitive (not case-insensitive; the token is a literal cfg identifier with one canonical spelling, so a case-insensitive sweep would not change the result — recorded here as a deliberate scope decision, not an oversight). Matched `Cargo.toml`, `.github/workflows/CI.yml`, `src/lib.rs`, `src/trace.rs`.
- `grep -n "hyper_unstable_tracing\|ready_stream\|features.*full\|RUSTFLAGS" .github/workflows/CI.yml` — single-file, case-sensitive.

No test or repro command was executed (run conditions §8 rule 2: no `cargo`, `rustc`, `miri`, `loom`; entirely static reasoning, stated as such rather than as a pass). This includes the changed test itself: `tests/ready_stream.rs`'s `body_test` was inspected by trace (setup → the two mock trait impls → the call under test → the (absent) assertions), not executed. No exact-head CI log was available to substitute (offline environment, no CI artifact access).

### 6.5 Changed-tests inspection (`tests/ready_stream.rs::body_test`, the only test function the change adds)

Traced in execution order:
- **Setup:** `TxReadyStream::new_pair()` wires two mock transports over `mpsc::unbounded_channel` pairs; `http1::Builder::new().max_buf_size(64 KiB)`; `service_fn` builds a 16×64KiB `StreamBody` from `futures_util::stream::iter(...)` over an already-fully-materialized `Vec` — this stream is **always synchronously `Ready`** until exhausted (it never returns `Pending`), so `body_test` does not itself exercise the "body's `poll_frame` is genuinely `Pending`" scenario my finding below turns on; it exercises a different (also real, now-fixed) hazard: the transport's `poll_write`/`poll_flush` toggling readiness independent of any waker.
- **Call under test:** `server_task` runs `http_builder.serve_connection(server_stream, service)`; the client side sends a literal `GET / HTTP/1.1 ...` request then loops `while let Some(chunk) = client_stream.recv().await { bytes_received += chunk.len(); }`.
- **Assertions:** **none.** `bytes_received` is only passed to `info!(bytes_received, "...")` — a log line, not a check. No `assert_eq!(bytes_received, TOTAL_CHUNKS * CHUNK_SIZE)`, no assertion that the response was well-formed, no assertion count at all in the file.
- **Cleanup:** `server_task.abort()` after the receive loop ends; the mock's `panic_task` (a 1s-sleep placeholder spawned as "a waker stand-in") is `.abort()`'d inside `poll_flush` once flushing completes, so it does not leak across test runs when the happy path is reached.
- **Termination mechanism if this exact bug regressed:** the receive loop ends only when `client_stream.recv()` returns `None`, i.e. when the paired `write_tx` is dropped, i.e. when `server_stream` is dropped, i.e. when `conn.await` completes. If `poll_loop` stalls (the bug this PR fixes, or a related future regression), `conn.await` never completes, `server_stream` is never dropped, and `client_stream.recv().await` blocks **forever** — there is no `tokio::time::timeout` anywhere in the file. The test's only failure mode is "hang," not "red."

This test function is a genuinely new file/entry under the rubric's "new or changed test... is code under review with its own standard," and per the rubric's sibling-convention check (§6.3 above: `Cargo.toml`'s three sibling `[[test]]` entries all use `required-features = ["full"]` only) plus §6.3's CI-job trace (only `cargo hack check`, never `cargo test`, ever enables `tracing`), this test is (a) excluded from every CI job that actually executes tests, and (b) incapable of failing loudly even when run manually, since it has no assertion and no timeout. This is `tests/ready-stream-no-ci-signal` below.

## 7. Complete candidate ledger (every candidate raised, with disposition)

| id | kind | claim (one line) | disposition | decisive evidence | falsification reason |
| --- | --- | --- | --- | --- | --- |
| `dispatch/poll-loop-write-again-overbroad` | concurrency | `can_write_again()` (`src/proto/h1/dispatch.rs:445-447`) returns true whenever `body_rx` is `Some`, not whenever `poll_write` demonstrated write readiness, so `wants_write_again` is true on essentially every iteration a body is open | **survivor — must-fix, P1 — verification: independent-confirmed** | §6.3 table rows (`io.rs:267-271`, `conn.rs:827-832`, `task.rs:8-11`) plus the trace in §8 below; verifier's independent bug-class check §8.2 | n/a — full record below |
| `tests/ready-stream-no-ci-signal` | maintainability | `tests/ready_stream.rs` is excluded from every CI job that runs tests, and its one test function has no assertion and no timeout | **survivor — consider, P2** | §6.3 CI.yml/Cargo.toml rows; §6.5 trace | n/a — full record below; no verification required (not `must-fix`; no security/data-loss/destructive-migration/compat-break trigger; the claim is a direct, single-file/single-diff fact needing no cross-module trace, so the rubric's exception for verifying an ordinary `consider` survivor does not apply) |
| `dispatch/can-write-again-mut-self` | maintainability | `can_write_again` takes `&mut self` though it only reads `self.body_rx` (a `Pin<Box<Option<_>>>` field it never mutates) | **dropped** | `src/proto/h1/dispatch.rs:445` | Fails gate 7 (worth the author's time): purely cosmetic, no maintenance or correctness cost demonstrated; harmless given the method is only ever called through `&mut self.can_write_again()` anyway inside a `&mut self` context, so there is no borrow-checker or API-ergonomics consequence to point to. |
| `dispatch/expose-loop-limit-config` | — (not a candidate) | `lthiery`'s non-review comment proposes exposing the loop's `16` limit as a config option "maybe I'll PR that later" | **dropped — not a candidate** | packet §6, non-review comment 1 (2025-10-31T04:32:16Z) | No admission gate is even reached: this is the PR author's own prose musing about a *future*, separate enhancement, explicitly self-deferred by its author as a possible later PR — not a claim about a defect in *this* diff. Nothing in the diff under review promises or requires this. |
| `tests/ready-stream-could-simplify` | maintainability | `TxReadyStream`'s hand-rolled mock (read_buffer/poll_since_write/flush_count/panic_task state) is complex and could plausibly be simplified, as `seanmonstar` originally asked | **dropped — intentional/accepted** | packet §6, review thread comments 1-2 (2025-10-28T14:42:40Z, 2025-10-31T04:27:56Z) and non-review comment 2 (2025-10-31T14:29:29Z: "Yea, hm, if it's a complicated edge case, perhaps that's fine as-is, then."), plus the unconditional `APPROVED` review (2025-11-10T14:47:34Z) | Gate 6 (Unintentional): this exact point was explicitly raised by the maintainer, explicitly answered by the author (why the complexity is load-bearing for deterministic repro), and explicitly, if tentatively, accepted by the maintainer before an unconditional approval and merge. I found no evidence beyond what the participants already weighed, so gate 7 (worth the author's time to re-litigate) also fails; re-raising it without new evidence would not be worth the author's time. Recorded as a live, already-considered deferral, not silently dropped — see §10 mechanism checklist, "deferral handling." |

No related-acquittal rows attach to the survivor `dispatch/poll-loop-write-again-overbroad`: checking every non-survivor row above against the related-acquittal test (kind ∈ {bug, concurrency, invariant, security} AND same file/anchor or same function/field/lock as the survivor) — `dispatch/can-write-again-mut-self` is `kind: maintainability` (fails the kind filter, even though it is the same file and same function `can_write_again`); `dispatch/expose-loop-limit-config` and `tests/ready-stream-could-simplify` are not `bug`/`concurrency`/`invariant`/`security` either. So the verifier batch below carries **candidate mode only**, no related-acquittal rows, and zero-survivor clean-verdict mode does not apply (at least one candidate survives as a finding).

## 8. Verifier dispatch

`dispatch/poll-loop-write-again-overbroad` is proposed `must-fix` and its `kind` is `concurrency` — both mandatory-verification triggers under `SKILL.md` step 3, and `kind: concurrency` also requires `references/verifier-concurrency.md`'s bug-class check to be included in the batch brief. `tests/ready-stream-no-ci-signal` is `consider`/`maintainability` and does not need a cross-module trace to decide, so it is not sent for verification (per the rubric, an ordinary `consider` survivor is sent "only when proving or refuting its existing claim requires a cross-module trace or another difficult reconstruction" — this one does not). No related-acquittal rows attach (§7). This is therefore **one initial candidate batch, one candidate, no clean-verdict/related-acquittal rows** — dispatched now, in the foreground, before any further falsification work proceeds, per rule 10.

Dispatched via `Agent` with `subagent_type: "v5b-verifier-effort-high"`, `model: "sonnet"`, `run_in_background: false`.

### 8.1 Exact prompt given (verbatim)

~~~markdown
# Independent verification batch — candidate mode

You are an independent verifier for the legacy reviewer skill (`hyperium/hyper#3952`, cell `a-high-seed1`, attempt `att-01`). You are fact-checking one supplied candidate. You are not a second reviewer: do not search for new findings beyond what is supplied, and you cannot write to the pull request. Read `references/verifier.md` and `references/verifier-concurrency.md` under `/tmp/effort124/skill/snapshot-path-omitted/` in full before proceeding — they own your evidence procedure, verdict vocabulary, and (for this candidate, whose kind is `concurrency`) the mandatory bug-class check. This prompt does not restate their content; follow them as written.

## Binding run conditions (apply to you exactly as they apply to the primary reviewer)

1. **Offline.** Your clone's `origin` points at a local filesystem path, not `github.com`. No `git fetch`, `git pull`, `gh`, `curl`, web fetch, or any network call of any kind.
2. **No execution.** Do not run `cargo` in any form (build, test, check, clippy, doc), `rustc`, `miri`, or `loom`. Reason entirely from the source; say so wherever a claim would ordinarily be settled by running something.
3. **History is truncated at the pinned head on purpose.** The newest object reachable in the clone is `f2aa734e5699a91fc20f1178e38af7b1e374bdbc`. Do not try to work around this. Report explicitly whether you read any history beyond the pinned head and which history commands you ran.
4. **Clone hygiene.** Do not run `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the tree. If you find the tree already mutated, stop and report it rather than repairing it yourself.
5. **Follow `references/verifier.md` and `references/verifier-concurrency.md` exactly as written.** Do not borrow behavior from any other review skill.
6. **Stay inside your sandbox.** Your clone (`/tmp/effort124/runs/a-high-seed1-att-01`), the skill snapshot (`/tmp/effort124/skill/snapshot-path-omitted/`), and this prompt's contents only. Do not read any other run's clone, report, or payload (in particular, do not read anything under `/tmp/effort124/reports/` or `/tmp/effort124/work/` outside what this prompt gives you). Report any other path you read anyway.
7. **Persist nothing yourself** — return your complete verdict in your response; there is no report file for you to write.
9. **No session relays.** Finish in this dispatch. Do not stop to ask anyone anything; if an input is genuinely missing, say so in your verdict rather than pausing.

## Repository and pinned coordinates

- Repository: `hyperium/hyper`, local clone at `/tmp/effort124/runs/a-high-seed1-att-01`
- Base/merge-base SHA: `f9f8f44058745d23fa52abf51b96b61ee7665642` (local branch `master`, pinned to this SHA)
- Head SHA: `f2aa734e5699a91fc20f1178e38af7b1e374bdbc` (local branch `review-head`, checked out)
- Diff: `git diff master review-head` (3 files, +270/−2)
- No linked issue (`issues=none`). The candidate below cites a pull-request-body promise as its requirement source; the exact quoted PR body is included with the candidate.
- No applicable base-branch repository-rule coordinate is cited by this candidate.

## Ranges (from `scripts/review_context.py`, for the candidate's anchor and fix — both in the same file)

```
src/proto/h1/dispatch.rs:68-465 @head
src/proto/h1/dispatch.rs:68-452 @merge-base
```

## The candidate

```yaml
id: dispatch/poll-loop-write-again-overbroad
kind: concurrency
priority: P1
action: must-fix
anchor:
  type: line
  path: src/proto/h1/dispatch.rs
  start_line: 180
  end_line: 192
  side: RIGHT
fix: src/proto/h1/dispatch.rs:445-447
title: Guard write-again on the body actually being ready, not merely present
claim: >
  can_write_again() at src/proto/h1/dispatch.rs:445-447 ("fn can_write_again(&mut self) -> bool {
  self.body_rx.is_some() }") returns true whenever body_rx is Some, regardless of whether poll_write
  demonstrated any write readiness this cycle. Combined with conn_ready = self.poll_flush(cx)?.is_ready()
  at line 174, wants_write_again (line 180) is true on essentially every poll_loop iteration where a
  body is open and the connection's write buffer happens to be empty (the common steady state while
  waiting on a body that has not yet produced its next frame), because an empty write buffer makes
  poll_flush trivially succeed over the ordinary TCP transport.
trigger: >
  A body actively streaming (body_rx is Some, e.g. a server response body or client request body mid-
  stream) whose poll_frame(cx) returns Poll::Pending this cycle (the body's own producer is not yet
  ready — a slow upstream, a paused SSE/long-lived chunked response, or the exact "custom futures"
  scenario the pull request's author describes running into), while the connection's write buffer is
  already empty (nothing new was written this cycle), so poll_flush trivially returns Ready over a real
  TcpStream (or any transport whose poll_flush is a no-op on an empty buffer).
impact: >
  poll_loop spins through all 16 read/write/flush iterations of its `for _ in 0..16` loop every single
  time it is polled (each iteration recomputes conn_ready=true and wants_write_again=true from the same
  unchanged body_rx.is_some()), then calls task::yield_now(cx), which unconditionally calls
  cx.waker().wake_by_ref() and returns Poll::Pending — immediately rescheduling the task. This repeats
  continuously for as long as the body remains open without producing new data, turning what should be
  an idle, parked connection (properly woken only when the body's own producer makes progress) into a
  continuous busy loop that consumes CPU on the executor instead of waiting on the body's registered
  waker.
change: >
  Track whether poll_write actually made forward progress this cycle (wrote a frame, or the body's
  poll_frame returned Ready with new data) instead of merely body_rx.is_some(), so wants_write_again is
  true only when there is genuine write readiness to consume this cycle, not whenever a body merely
  happens to still be open and the write buffer happens to be empty.
requirement_source: >
  pr-body/"if the poll_write is demonstrating readiness to write and the connection has readiness to
  write, we should do that or else hyper may stall"
raw_code_citations:
  - "src/proto/h1/dispatch.rs:165-200 (poll_loop, full function as changed)"
  - "src/proto/h1/dispatch.rs:444-447 (can_write_again, new method)"
  - "src/proto/h1/dispatch.rs:203-... (poll_write; specifically the OptGuard body-frame branch: `let item = ready!(body.as_mut().poll_frame(cx));`)"
  - "src/proto/h1/io.rs:267-271 (Buffered::poll_flush: `else if self.write_buf.remaining() == 0 { Pin::new(&mut self.io).poll_flush(cx) }`)"
  - "src/proto/h1/conn.rs:827-832 (Conn::poll_flush delegates to the io layer then trivially returns Ready)"
  - "src/proto/h1/conn.rs:428-432 (wants_read_again: contrast — a narrow, self-resetting flag, not persistently true)"
  - "src/common/task.rs:8-11 (yield_now: `cx.waker().wake_by_ref(); Poll::Pending`)"
raw_code_citations_note: >
  I am withholding my own reasoning/support narrative from you by design; independently read the cited
  lines (and the enclosing functions) at head and at the merge-base as the verification task requires,
  and reach your own verdict on the trigger, the impact, and whether gate 2 (introduced-here) is
  satisfied (this is 100% new code — can_write_again, conn_ready, and wants_write_again do not exist at
  the merge-base at all, so there is no pre-existing form of this exact condition to compare against;
  confirm this from `git show f9f8f44058745d23fa52abf51b96b61ee7665642:src/proto/h1/dispatch.rs`).
pull_request_body_verbatim: |
  I ran into some lockups running hyper with some custom futures. If one of my futures is ready when
  polled, the waker is never signaled and I think this uncovered a logical issue with the http1
  poll_loop. That it to say, **if the poll_write is demonstrating readiness to write and the connection
  has readiness to write, we should do that or else hyper may stall**.

  I built a pathological example "ready_stream.rs" - you can run it from this branch with:
  `RUSTFLAGS='--cfg hyper_unstable_tracing' cargo test --test ready_stream --features full,tracing`.

  I provided a proposed patch for the poll_loop, but I'm open to other angles on this.
review_record_context: >
  Reviewed and approved before merge by the repository maintainer `seanmonstar` (review state APPROVED,
  2025-11-10T14:47:34Z), after a review-thread discussion that concerned only whether the accompanying
  test (tests/ready_stream.rs) could be simplified — the maintainer's substantive comment on the *code*
  fix itself was: "Looking close, I appreciate you cleaning up the mistake in here: since we're
  essentially 'selecting' over read and write, we need to make sure both sides either registered a
  waker, or that we will poll again with the yield_once util." No participant in the review record
  discussed or accepted the specific busy-spin cost this candidate describes; do not treat the general
  approval as addressing this specific candidate unless you find the review record actually discusses
  it (per the task step 5 rule: a maintainer's approval establishes intent only for what the review
  record explicitly addresses).
focused_check_run: none — no test or repro command was executed for this candidate; this is a purely
  static claim.
```

## Your permission and task

You may inspect the cited code and any narrow callers, tests, configuration, or history needed to decide this candidate, within the clone at `/tmp/effort124/runs/a-high-seed1-att-01` and the skill snapshot at `/tmp/effort124/skill/snapshot-path-omitted/` only. Apply `references/verifier.md`'s verification task (all 6 steps) and, because this candidate's `kind` is `concurrency`, `references/verifier-concurrency.md`'s bug-class check in full (state the invariant at rule level; answer whether the failing interleaving requires shutdown/teardown/an error path, and if not, trace at least one steady-state interleaving to a `holds`/`fails` verdict with citations; enumerate sibling interleavings — e.g. producer-body-pending vs. connection-idle, spawner/steady-state read vs. write — before sibling code paths; widen `change` to the rule level if the proposed fix is narrower than the bug class). Return your verdict in the exact format `references/verifier.md`'s "Verdicts" section specifies: `confirmed` or `refuted` (with its named `basis`), decisive citations, any correction to `trigger`/`impact`/`priority`/`action`/`anchor`/`fix`/`change`, any scoped safety ruling, and any duplicate-id grouping. Do not render publication prose. If you find an incidental, non-actionable, in-scope observation, return it separately as the single permitted `observation` aside per `verifier.md`; do not fold it into the verdict.
~~~

### 8.2 Verbatim verifier report

Dispatched via `Agent(subagent_type: "v5b-verifier-effort-high", model: "sonnet", run_in_background: false)`. Returned agent id `aec115b5b6c51557d`; usage reported by the harness for this sub-agent: `subagent_tokens: 97182`, `tool_uses: 24`, `duration_ms: 683993`.

~~~markdown
## Verifier Report — candidate `dispatch/poll-loop-write-again-overbroad`

### Isolation / environment disclosure
Fresh read-only inspection of `/tmp/effort124/runs/a-high-seed1-att-01` only. No network, no cargo/rustc/miri/loom execution. History commands run (all confined to ancestors of the pinned head, nothing beyond `f2aa734e`): `git status --porcelain=2 --branch`, `git log --oneline -5 review-head`, `git branch -a`, `git rev-parse HEAD`, `git show f9f8f440...:src/proto/h1/dispatch.rs`, `git diff f9f8f440... f2aa734e... -- src/proto/h1/dispatch.rs`, `git log --oneline -- src/proto/h1/dispatch.rs | tail -20`, `git log --follow -p -- src/proto/h1/dispatch.rs | grep ...`, `git blame -L 172,173 master -- src/proto/h1/dispatch.rs`. Clone was clean (`branch.oid` matched head, no dirty files) — no hygiene issue to report.

### Verdict: `dispatch/poll-loop-write-again-overbroad` — **confirmed**

**Basis:** decisive trace establishes the trigger, the qualifying impact, and the Code "introduced-here" condition.

**Decisive mechanics verified independently:**

1. `?` on a bare `Poll<Result<T,E>>` expression in this codebase (e.g. `src/proto/h1/dispatch.rs:174` `let conn_ready = self.poll_flush(cx)?.is_ready();`) only short-circuits on the `Err` arm; `Poll::Pending` and `Poll::Ready(Ok(_))` both pass through as a `Poll<T>` to the next statement. This is provable from the code itself: `.is_ready()` is only defined on `Poll<T>`, so if `?` fully unwrapped to `()` (short-circuiting on `Pending` the way `ready!` does), `().is_ready()` would not compile. So lines 172–173 (`self.poll_read(cx)?; self.poll_write(cx)?;`) do **not** exit `poll_loop` when `poll_write` returns `Pending`; execution always reaches line 174 (`poll_flush`) and line 180 (`wants_write_again`) every iteration.
2. `can_write_again()` (`src/proto/h1/dispatch.rs:445-447`) is exactly `self.body_rx.is_some()` — it carries no "did this cycle make progress" bit.
3. When the body is mid-stream and `poll_frame` returns `Pending` (`src/proto/h1/dispatch.rs:381`, inside the `OptGuard` branch), `OptGuard`'s `clear_body` flag is untouched, so `Drop` (`src/proto/h1/dispatch.rs:504-509`) does not clear `body_rx` — it stays `Some`.
4. With nothing written this cycle, `Buffered::poll_flush` (`src/proto/h1/io.rs:267-271`) takes the `write_buf.remaining() == 0` branch and delegates straight to the transport's `poll_flush`, which is a practical no-op success over ordinary transports — `conn_ready = true`.
5. Hence `wants_write_again = can_write_again() && conn_ready` evaluates `true` on a cycle where the body demonstrated **no** readiness at all — exactly the candidate's claim.
6. Because `wants_write_again` stays `true` across the full body-pending window, `poll_loop`'s `for _ in 0..16` loop (`src/proto/h1/dispatch.rs:171-196`) never early-returns via line 192-195 and instead falls through to `task::yield_now(cx)` (`src/proto/h1/dispatch.rs:200`, defined `src/common/task.rs:8-11`), which unconditionally calls `wake_by_ref()` and returns `Pending` — an immediate, forced re-schedule. Since nothing changed, the next poll repeats the identical 16-iteration spin and forced wake, indefinitely, for as long as the body stays paused. This is a genuine, unbounded-in-time steady-state busy loop, not a one-shot safety-net poll.

**Introduced-here (gate 2) confirmed:** at merge-base (`git show f9f8f440...:src/proto/h1/dispatch.rs`, and the diff itself), the loop-continuation test was solely `!self.conn.wants_read_again()`; there was no `wants_write_again`/`can_write_again` at all. In that code, the same body-pending scenario would cause `poll_loop` to return `Poll::Ready(Ok(()))` after exactly one iteration (relying on the waker `poll_frame` registered), with no spin. `can_write_again`, `conn_ready`, and `wants_write_again` are 100% new in this diff, and they are the sole cause of the new spin behavior.

**Task step 5 (intentional?) — not established.** The maintainer's recorded comment ("we need to make sure both sides either registered a waker, or that we will poll again with the yield_once util") endorses the *general* bounded 16-then-yield safety-net architecture (which predates this PR and applies to the read side too), not the specific new failure mode of *indefinite, continuous* re-triggering of that safety net for as long as a body stays paused. The review thread's only substantive discussion was about simplifying the test file. This does not settle intent for the specific cost the candidate identifies, so `intentional` does not apply as a refutation basis.

### Bug-class check (`verifier-concurrency.md`), required because `kind=concurrency`

1. **Invariant at rule level:** `wants_write_again` (and its input `can_write_again()`) must be true only when a write-side sub-poll actually demonstrated fresh readiness during *this* poll cycle (new data written, or the flush transitioned from not-ready to ready), and false whenever the prior `poll_write` call returned `Pending` because an external producer/transport is not yet ready and has registered `cx`'s waker for later. Concretely: "`wants_write_again` must never be observed true when the only fact supporting it is `body_rx.is_some()` with no accompanying write progress this cycle."

2. **Does the failing interleaving require shutdown/teardown/an error path?** No. Traced above is a pure steady-state interleaving: a body mid-stream (server response body or client request body) whose producer has not yet produced the next frame, with an otherwise-idle, healthy connection (empty write buffer, no error). Verdict: **fails** — `path:line` citations: `src/proto/h1/dispatch.rs:180` (`wants_write_again`), `:445-447` (`can_write_again`), `:381` (`poll_frame` Pending), `:504-509` (`OptGuard` Drop keeps `body_rx` Some), `src/proto/h1/io.rs:267-271` (trivial flush success), `src/proto/h1/dispatch.rs:196-200` (forced wake + Pending).

3. **Sibling interleavings enumerated:**
   - *Producer-body-pending vs. connection-idle* (the traced case): **fails** — spurious spin, cited above.
   - *Producer-body-ready-but-buffer-full* (body genuinely has more data, `can_buffer_body()` false, needs a flush before it can write more): **holds/intended** — here `wants_write_again=true` correctly re-drives the loop after the flush completes; this is the scenario the PR's stated fix target ("poll_write is demonstrating readiness … we should do that") legitimately needs. Citations: `src/proto/h1/dispatch.rs:364-365` (`!can_buffer_body()` branch), `:180`.
   - *Read vs. write, steady state:* the read-side analog (`wants_read_again`, `src/proto/h1/conn.rs:428-432`) is a narrow, self-resetting flag (`notify_read`) set only on an actual state transition and consumed once read — it does **not** share this defect, because it tracks "did something change" rather than "is a value merely present." This asymmetry is itself the root cause: `can_write_again()` was implemented at a coarser (Some-ness) granularity than the read side's already-correct, narrower design.
   - *Spawner/steady-state read vs. write* and *claimant/releaser*-style pairs are not applicable here — there is no shared mutable resource contended by two schedulable actors beyond the single-task poll/waker protocol between `poll_loop` and the body's own producer, which is exactly the pair analyzed above.

4. **Sibling code paths governed by the rule:**
   - The "buffer full → flush → more body" path: protected/intended by the current design, unaffected by the proposed fix (still correctly re-drives).
   - The "body exhausted, `poll_frame` returns `Ready(None)`" and "trailers written" paths (`dispatch.rs:406-418`) clear `body_rx` via `clear_body`, so `can_write_again()` becomes false on the next check — not affected by the bug and not affected by the fix.
   - The unrelated bare `return Poll::Pending;` at `dispatch.rs:424` (no-body-rx, `can_write_body()` false) is a separate, pre-existing code path not touched by this diff or by `can_write_again()`; it is out of scope for this candidate's rule and I do not fold it into `change`. (Flagging only as a non-actionable **observation**, see below — it does not contradict or narrow this candidate's finding.)

5. **Widen `change` to rule level:** Not necessary — the candidate's `change` ("track whether poll_write actually made forward progress this cycle … instead of merely `body_rx.is_some()`") is already phrased at the rule level and targeted at the sole call site/definition (`can_write_again`, the only place this state is read), so it already restores the invariant for every failing interleaving found in steps 2–3 without narrowing to one path. No correction needed to `trigger`, `impact`, `priority`, `action`, `anchor`, or `fix`.

### Scoped safety rulings
None asserted by this candidate that require the 5-step attack (it does not claim any other path is safe/correct); I attacked the *implicit* premise "conn_ready is trivially true when nothing was written" and it holds under the cited `io.rs:267-271` code, and the premise "body_rx stays Some on Pending" holds under the cited `OptGuard` Drop logic (`dispatch.rs:504-509`) — both traced above with citations, not merely re-asserted.

### Corrections
None to `trigger`, `impact`, `priority`, `action`, `anchor`, `fix`, or `change` — all confirmed as stated.

### Duplicate grouping
Not applicable — single candidate supplied.

### Observation (non-actionable, incidental, does not affect the verdict above)
`src/proto/h1/dispatch.rs:424` (`poll_write`'s no-`body_rx`, `!can_write_body()` branch) does a bare `return Poll::Pending;` with no visible waker registration in that branch itself; this is pre-existing code (unchanged by this diff) and is a separate code path from the one this candidate addresses, so it neither confirms nor refutes this candidate's finding.
~~~

### 8.3 What the primary did with the return

Verdict is `confirmed`, no corrections to any field, no scope dispute, no duplicate grouping needed (single candidate). Per `SKILL.md` step 3, a mandatory-verification candidate publishes only when `confirmed` — it is. I set `dispatch/poll-loop-write-again-overbroad`'s `verification: independent-confirmed`, `disposition: survivor` (unchanged). Recomputed zero-survivor eligibility: not applicable, at least one candidate survives. No follow-up batch is needed: nothing became newly render-eligible, no ledger row first became related after this dispatch (checked again against the final ledger below — still none), and no row was re-opened.

I independently re-verified the two premises the bug-class check step 2/3 relies on before accepting the confirmation, rather than taking the verifier's citations on faith: I re-read `src/proto/h1/io.rs:267-271` and `src/proto/h1/dispatch.rs:368-426` myself in §6.3/§8 above (my own citations match the verifier's independently derived ones), and I re-derived the `?`-on-`Poll<Result<T,E>>` semantics myself before ever dispatching the verifier (§6, and confirmed again by the verifier's own independent proof-by-compilability argument, which matches mine). The two independent derivations agree.

**The verifier's observation** (`src/proto/h1/dispatch.rs:424`, a bare `return Poll::Pending;` with no waker registration visible in that branch) is routed under the rubric's Observations section, per `SKILL.md` step 3 ("Route a verifier `observation` aside through the rubric's Observations section... it never becomes a finding without full primary admission"). I independently re-read lines 356-430 (§ above) to confirm the fact before accepting it. Applying full primary admission gates myself: this is pre-existing code (unchanged by this diff, present verbatim at the merge-base too — confirmed by the fact the whole `poll_write` function is outside the diff's changed-line set), so it fails gate 2 (introduced-here) as a Code candidate for *this* review regardless of whether it is itself a latent bug elsewhere in the codebase; it is out of scope for admission as a finding here. It remains an accurate, evidence-backed, non-actionable fact I can publish as an **Observation** (one of the review's 3 allowed slots) since it stands with no established consequence *I* investigated further (I did not trace whether some caller/pre-existing guarantee protects that branch — that would be new legwork outside the scope of the introduced-here diff, and the rubric does not require me to fully resolve pre-existing code's safety before observing an accurate, out-of-scope fact about it).

## 9. Validate before writing (step 5) and render (step 6)

Assembled the payload at `/tmp/effort124/work/a-high-seed1-att-01/payload.json` (2 findings + 1 observation, run trailer, `summary.repository_url`). Rendered fragments with `python3 scripts/validate_review.py --render < payload.json` (exit 0) and pasted them verbatim into `summary.body`'s `## Findings` list — never hand-composed. Validated with `python3 scripts/validate_review.py < payload.json` — **exit 0, zero violations** on the first attempt (one prior in-progress draft, before the fragments were pasted in, was never run through the validator — I only ran the validator once the fragments were in place, so there is no discarded-violation history to report). Immediately after that exit-0 validation, ran:
```
python3 /tmp/effort124/mark_event.py /tmp/effort124/reports/a/a-high-seed1-att-01-timing.json payload_validated_at
```
which recorded `payload_validated_at: 2026-09-06T08:26:55.667086+00:00` in the timing sidecar (confirmed by reading the file back). The payload was not changed after this, so no second `mark_event.py` call was needed.

Produced the batch with `python3 scripts/validate_review.py --emit-batch < payload.json > batch.json` — exit 0. Per run condition §8 rule 4 / the packet's retrospective-mode instruction, publication is disabled: I did not attempt `gh api --method POST .../reviews`, did not re-fetch the PR head before a write (there is no write), and did not read back a published review. The complete would-be review — summary body, both line comments with their trailers, and the exact batch JSON that would have been posted — is rendered in full at `/tmp/effort124/reports/a/a-high-seed1-att-01-payload.md`. That file also preserves the emitted `batch.json`'s exact `commit_id`/`event`/`comments[].path`/`.line`/`.side`/`.start_line`/`.start_side` fields for the record.

**Derived status:** `Changes Requested (advisory)` — one `must-fix` finding is unsettled (it is newly confirmed by this review and has not been addressed in the merged code), so status rule 1 governs regardless of the other rules; `(advisory)` because the event is `COMMENT` (self-review-style default; no gating authorization exists or was sought for this identity). No open question exists, so rule 3 does not apply; coverage is complete, so rule 2 does not apply.

**What would have been reported after publication, had it not been disabled** (per `SKILL.md` step 6's final reporting instruction, adapted to retrospective mode): status `Changes Requested (advisory)`; reviewed head `f2aa734e5699a91fc20f1178e38af7b1e374bdbc`; coverage `complete`; review URL — none, publication disabled; finding "URLs" — the two rendered commit-pinned blob links in §_payload_ above (`.../src/proto/h1/dispatch.rs?plain=1#L180-L192` and `.../tests/ready_stream.rs?plain=1#L241-L248`, both pinned at the head SHA, plus their `fix` links); open questions — none; disputed findings — none (first review, not a re-review); nothing failed to publish because nothing was attempted (retrospective, non-publishing by design, not by failure).

## 10. Mechanism checklist

| Mechanism | Fired? | Where demonstrated |
| --- | --- | --- |
| Question channel | **Did not fire.** | No candidate's settling fact was statically unresolvable in a way that gated a material decision; both survivors were fully settled by static tracing plus independent verification. No `type: question` item in the payload. |
| Clean-verdict or related-acquittal verification | **Did not fire (correctly, per the rule's own gating).** | Zero-survivor mode requires *zero* candidates to survive as findings; two survived, so it never applied (§7, §8). Related-acquittal mode requires a non-survivor row sharing `kind ∈ {bug,concurrency,invariant,security}` and the same file/function/field as a survivor; checked explicitly in §7's closing paragraph — none qualified (`dispatch/can-write-again-mut-self` is same file/function but wrong kind). No re-open occurred. |
| Observations | **Fired — 1 of 3 slots used.** | The verifier's own permitted aside (§8.2) about `src/proto/h1/dispatch.rs:424`, routed through full primary admission (§8.3) and published in the payload's `## Observations` section. |
| Fix-sufficiency check on a concurrency/invariant candidate | **Fired — full bug-class check completed by the verifier, then independently sanity-checked by me.** | §8.2: rule-level invariant stated; steady-state-vs-shutdown question answered (steady state, "fails"); sibling interleavings enumerated (producer-pending/idle — fails; producer-ready/buffer-full — holds/intended; read-vs-write asymmetry noted); sibling code paths enumerated (buffer-full→flush→more-body; body-exhausted/trailers; the unrelated bare-Pending branch); `change` confirmed already at rule level, no widening needed. |
| Follow-up verifier round | **Did not fire.** | The single initial batch returned `confirmed` with no corrections, no scope dispute, and no newly-related or newly-render-eligible rows; §8.3 explicitly rechecked relatedness after the return and found none. Total batches used: 1 of the allowed 1-initial-plus-1-follow-up cap. |
| Deferral handling | **Fired — one explicit deferral found in the review record, treated as an open-but-not-live item, not silently dropped.** | `lthiery`'s non-review comment about exposing `16` as a config option is the PR author's own future-work aside, not a defect claim about this diff — recorded in the ledger (§7, row `dispatch/expose-loop-limit-config`) as "not a candidate," not silently ignored. Separately, the test-simplification thread (`seanmonstar` ↔ `lthiery`) is an *explicit deferral* under the rubric's gate-6 language ("I'll still take another critical pass... I'll see what I can do to simplify"); per the rubric, an explicit deferral means the deferred question is open, not accepted, purely on the *author's* say-so — but here the *maintainer* (an authorized human) responded after the fact ("perhaps that's fine as-is") and then unconditionally approved and merged, which is the review record itself settling the deferred question, not silent acceptance by omission. I recorded this reasoning explicitly in the ledger (§7, row `tests/ready-stream-could-simplify`) rather than treating the mere existence of a deferral as automatic license to raise a fresh finding with no new evidence. |
| Retrospective mode | **Fired — throughout.** | Packet §1 marks `merged: true`, publication disabled by default; the `Mode` line appears in the rendered summary (payload §"Review summary body"); no forge write was attempted anywhere in this run; §9 above explains what a hypothetical publication report would have said. |

## 11. History discipline

I read history **only within ancestors of the pinned head** (`f2aa734e5699a91fc20f1178e38af7b1e374bdbc`); I never attempted to reach anything after it (there is nothing after it in this clone by design, per run condition §8 rule 3). Exact history commands I ran, myself, in the primary context:

```
git branch -v
git log --oneline -5 master
git log --oneline -5 review-head
git status
git show master:docs/agents/issue-tracker.md      # confirms absence, exits non-zero internally but the shell command succeeded
git show master:CONTRIBUTING.md
```

No `git log` walking past the head, no `git fetch`/`git pull`, no attempt to reach a later commit. The verifier sub-agent separately disclosed its own history commands in its report (§8.2, "Isolation / environment disclosure"): `git status --porcelain=2 --branch`, `git log --oneline -5 review-head`, `git branch -a`, `git rev-parse HEAD`, `git show f9f8f440...:src/proto/h1/dispatch.rs`, `git diff f9f8f440... f2aa734e... -- src/proto/h1/dispatch.rs`, `git log --oneline -- src/proto/h1/dispatch.rs | tail -20`, `git log --follow -p -- src/proto/h1/dispatch.rs | grep ...`, `git blame -L 172,173 master -- src/proto/h1/dispatch.rs` — all likewise confined to ancestors of the pinned head (the verifier explicitly confirmed this and reported the clone as clean).

## 12. Sandbox disclosure

Every path I read was inside: the clone (`/tmp/effort124/runs/a-high-seed1-att-01`), the skill snapshot (`/tmp/effort124/skill/snapshot-path-omitted/`), the packet directory (`/tmp/effort124/packets/a/packet.md`), and my own work/report/payload/timing paths under `/tmp/effort124/work/a-high-seed1-att-01/` and `/tmp/effort124/reports/a/`. I additionally observed, via one `ls` listing only (not a read of contents), that `/tmp/effort124/reports/a/` contains sibling files for a different attempt (`a-medium-seed1-att-02-*`); I did not open or read any of that attempt's report, payload, or timing content, per rule 7/§8's sandbox instruction — disclosed here since the instruction asks me to report any other path I so much as touched. No other out-of-sandbox path was read by me or, per its own disclosure, by the verifier sub-agent.

## 13. Notes — judgment calls on the skill's contract

1. **Re-review non-applicability.** The packet carries substantial prior review state, but none from the posting identity `kamui`. I read `references/re-review.md` for background but did not treat this as a re-review, since `SKILL.md` step 1 gates that reference specifically on prior state "from the posting identity." I treated the packet's prior-review record purely as gate-6/gate-1 evidence during falsification (see §7's dropped rows), not as material requiring the re-review reference's delta scoping, duplicate-review shortcut, or reply-disposition machinery. I consider this the plain reading of the text, not a close call, but record it because the packet's own prior-review section is unusually large for a "first review."
2. **`conformance.md` not loaded.** No versioned artifact (schema, generated source, SDK/binding tracking a release) is named by the PR, diff, or repository convention. I did not load `references/conformance.md`. Plain reading, not a close call.
3. **Combining the two test-hygiene facts into one finding.** `tests/ready_stream.rs` not being wired into any CI job that runs tests, and its `body_test` having no assertion or timeout, are two distinct mechanical facts (§6.5) but I treated them as one defect ("this regression test provides no automated protection") with one anchor, one fix coordinate, and two evidence facts in one comment, rather than two separate `consider` findings. This is a judgment call under the rubric's "one comment per distinct defect" / "at most two decisive evidence facts" guidance — I judged both facts serve a single underlying claim (no regression signal) rather than two independent claims, and the 160-word budget and two-fact cap fit comfortably combined. A reviewer who judged these as two independently-actionable defects (CI wiring is fixable without touching the test; the assertion/timeout gap is fixable without touching CI) could reasonably have split them into two `consider` findings instead.
4. **Anchor/fix split for the same combined finding.** I anchored that finding on the test file (`tests/ready_stream.rs:241-248`, where the un-asserted, un-timed receive loop lives) and set `fix` to `Cargo.toml:246` (the `required-features` line, the more structural of the two repairs), naming the test-file assertion/timeout repair only in the visible `Change` prose rather than as a second fix coordinate — the output contract's `fix` trailer field is singular. This is a deliberate choice among several defensible anchor/fix pairings (I could instead have anchored on `Cargo.toml:246` with `fix` pointing at the test file); I judged the test file the more honest anchor because that is where the *reader* first notices the missing protection (a hang with no assertion), while `Cargo.toml`'s required-features line is the more mechanical single-line repair site.
5. **Priority calibration on the busy-spin finding.** I set `P1` rather than `P0`. `P0` is "universal release blocker or critical failure requiring immediate action" — this defect requires a specific, common-but-not-universal condition (an actively-streaming body that pauses mid-stream) to manifest; not every hyper connection triggers it (a fully-buffered, single-shot response body never does, per §6.5's trace of the shipped test's own `stream::iter` body, which never goes Pending). I judged this serious and broadly affecting (P1) rather than universal (P0). The verifier did not correct this priority, which I read as tacit agreement, but priority calibration remains my judgment call, not the verifier's to set (the verifier can correct priority/action but chose not to).
6. **Kind classification (`concurrency` vs. `performance`).** I classified the busy-spin finding as `concurrency` rather than `performance` because its root cause is a broken poll/waker liveness rule (the maintainer's own "selecting over read and write" framing) rather than an algorithmic inefficiency, and because `concurrency` is what triggers the verifier's mandatory bug-class check, which I judged this candidate needed (sibling-interleaving analysis, steady-state-vs-shutdown distinction) more than a plain performance review would provide. A reviewer who saw this primarily as a CPU-cost issue rather than a waker-protocol defect could reasonably have filed it as `performance` instead, which would not have required the concurrency bug-class check.

