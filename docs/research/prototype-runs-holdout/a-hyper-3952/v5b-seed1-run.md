# Run document — holdout target (a), cell `v5b-seed1`

**Orchestrator metadata (added after the run; the researcher's record, not the reviewer's).**

| | |
| --- | --- |
| Packet | `packets/a/packet.md`, SHA-256 `c94a8d3ed431594d9acd0803bac2558d9227aa58733404f1a5fd416a6e3bf1f2` |
| Snapshot pins | v5b=2f06662 noverify=2f06662-minus-verifier panel=dd3bcfe33bfe8b65e272a6d2266ee9bc6cd1dc72 |
| Root agent / primary | `a639f0db2bb99e745` / `a639f0db2bb99e745` |
| Payload | [`v5b-seed1-payload.md`](v5b-seed1-payload.md), 4668 bytes |
| Report (this file, below the preamble) | 67783 bytes as written by the reviewer |
| Closed out | 2026-09-04T20:43:58.304593+00:00 |
| Problems at close-out | none |

## Model and effort verification (every assistant line of every transcript)

| Agent | Role | Definition | `message.model` | `effort` | Transcript |
| --- | --- | --- | --- | --- | --- |
| `a639f0db2bb99e745` | primary | general-purpose | `claude-sonnet-5`×129 | `high`×129 | `agent-a639f0db2bb99e745.jsonl` |
| `acdca97d592ad9a2b` | child | general-purpose | `claude-sonnet-5`×36 | `high`×36 | `agent-acdca97d592ad9a2b.jsonl` |

## Billed usage (`transcript_usage.py --prices 2,10 --report <this report>`)

```
agent-a639f0db2bb99e745.jsonl
turns                        63 (API requests; 129 assistant lines)
tool calls                   74
text-only turns               1
input                       126 tokens (uncached)
cache write             353,976 tokens
cache read            7,542,071 tokens
output                  107,860 tokens (thinking 60,845)
models             claude-sonnet-5
wall                    0:26:21
cost                       3.47 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-acdca97d592ad9a2b.jsonl
turns                        18 (API requests; 36 assistant lines)
tool calls                   18
text-only turns               1
input                        36 tokens (uncached)
cache write              63,684 tokens
cache read              685,629 tokens
output                   24,451 tokens (thinking 18,637)
models             claude-sonnet-5
wall                    0:05:13
cost                       0.54 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

TOTAL
turns                        81 (API requests; 165 assistant lines)
tool calls                   92
text-only turns               2
input                       162 tokens (uncached)
cache write             417,660 tokens
cache read            8,227,700 tokens
output                  132,311 tokens (thinking 79,482)
models             claude-sonnet-5
wall                    0:31:34 (summed over transcripts)
cost                       4.01 $ at 2/10 per M, cache write ×1.25, cache read ×0.1
production-shaped          3.84 $ (output 115,365 after subtracting the report's 16,946 est. tokens)
```

Row for `comparison-data.md`:

| (a) v5b seed 1 | claude-sonnet-5 | 81 | 92 | 2 | 162 | 417,660 | 8,227,700 | 132,311 | 79,482 | 0:31:34 | 4.01 | 16,946 | **3.84** |

Per agent:

| primary a639f0db2bb99e745 | claude-sonnet-5 | 63 | 74 | 1 | 126 | 353,976 | 7,542,071 | 107,860 | 60,845 | 0:26:21 | 3.47 | — | — |
| child acdca97d592ad9a2b | claude-sonnet-5 | 18 | 18 | 1 | 36 | 63,684 | 685,629 | 24,451 | 18,637 | 0:05:13 | 0.54 | — | — |

---

# Research report — cell (a) v5b seed 1

Target: `hyperium/hyper#3952` ("fix(http1): poll_loop writes when ready"). Arm `v5b` — skill `legacy reviewer` pinned at `main 2f06662 (workflow=v5b-1)`. Seed 1.

Run started (best-effort; not stamped at the very first tool call): approx. 2026-09-04T~19:40Z. Report first persisted (this stage): 2026-09-04T20:29:55Z. Final wall clock is stated in section 10 once the run finishes.

## 1. Metadata

- **Target:** `hyperium/hyper#3952`, head `f2aa734e5699a91fc20f1178e38af7b1e374bdbc`, base `master`, base SHA / merge-base `f9f8f44058745d23fa52abf51b96b61ee7665642` (identical). `state=MERGED`, `merged=true`, `isDraft=false`.
- **Arm/seed:** v5b, seed 1.
- **Skill and pin:** `legacy reviewer`, snapshot at `/tmp/holdout/skills/v5b/`, `workflow=v5b-1` (matches `WORKFLOW = "v5b-1"` hard-coded in `scripts/validate_review.py`).
- **Model I (the primary reviewer) ran on:** `claude-sonnet-5` (`model: sonnet` requested for this whole dispatch; I am the reviewer, running directly in this context, not as a spawned sub-agent).
- **Sub-agents spawned:** one verifier batch (candidate mode with one related-acquittal row), dispatched with `model: "sonnet"` explicitly, `run_in_background: false`, foreground, waited for completion. See section 4 for the exact prompt and verbatim report. No other sub-agents were spawned (no finder fan-out; this skill is a single integrated reviewer).
- **Verification trigger that fired:** the *must-fix* trigger — one surviving candidate (C1, busy-poll on the write side) was proposed `must-fix`, which mandates independent verification under `SKILL.md` step 3. Related-acquittal mode also fired alongside it (one dropped `kind=bug` ledger row, D1, shares a file with C1's anchor/fix), so it rode in the same batch. Zero-survivor mode did **not** fire (there was at least one survivor). No candidate needed a follow-up batch (see section 4 for the verifier's verdicts and whether anything re-opened).
- **Candidates raised:** 4 (C1, C2 survivors; D1, D2 dropped as formal candidates) plus one non-candidate consideration (D3, a musing about test-fixture generalization that never reached candidate form) and one non-candidate technical curiosity (D4, an unrelated pre-existing Rust-syntax question, not a defect claim). See section 3 for the full ledger.
- **Candidates surviving my own falsification (pre-verification):** 2 — C1 (`must-fix`, pending independent confirmation) and C2 (`consider`, no mandatory verification required).
- **Verifier verdicts:** C1 `confirmed`, no correction to priority/action/anchor/fix/trigger/impact/change (stays `[P1] [must-fix]`, `verification: independent-confirmed`). D1 (related-acquittal row) `holds` (acquittal stands; stays dropped, not re-opened). No duplicate/overlap between C1 and D1. No verifier `observation` aside returned. Full verbatim exchange in section 4.
- **Findings for publication:** 2 — C1 (`[P1] [must-fix]`, `independent-confirmed`) and C2 (`[P2] [consider]`, `primary-confirmed`). Full detail in section 2; rendered prose in the payload file.
- **Questions:** none raised. No candidate met the static-unresolvability bar (all facts here were statically decidable from the diff, the unchanged surrounding code, and the CI YAML).
- **Observations:** none published. No accurate fact failed admission *specifically* on gates 1/4 (meaningful impact / proven consequence) in a way that qualifies for the `Observations` channel — see section 3 for why each dropped candidate was dropped outright instead of routed there. The verifier also returned no `observation` aside.
- **Coverage:** every changed file reviewed (`Cargo.toml`, `src/proto/h1/dispatch.rs`, `tests/ready_stream.rs` — see section 5). All risk-directed checks from the rubric's "Complete inspection" list were considered; the applicable ones (concurrency/retries/idempotency/partial failure, external contracts/dependency upgrades, test/generated-artifact hygiene) got evidence-backed outcomes below. No fetch, patch, or verification step failed or was left incomplete. `coverage=complete`.
- **Derived status:** `Changes Requested (advisory)` — one `must-fix` finding (C1) is confirmed and unsettled; event is `COMMENT` (this identity did not author the PR and no gating authorization was given, and — separately — this is a non-publishing retrospective run regardless), so `(advisory)` is appended per the output contract's authorization table.
- **Token usage:** the harness does not report token usage to me in this context; I have no figure to give. (Per project memory, sub-agent transcripts would need separate inspection to get a sub-agent's usage, and this run's single verifier sub-agent's transcript was not separately queried for token counts since the harness did not surface them to me either.)

## `context` digest (computed once, per step 2)

Inputs, taken from the packet verbatim (no re-fetch):

- `pr.title`: `fix(http1): poll_loop writes when ready`
- `pr.body`: the PR body reproduced verbatim in packet section 3 (the three paragraphs about the lockup, the `ready_stream.rs` pathological example, and the offer to discuss "other angles").
- `issues`: `[]` — packet section 4 states `issues=none`; no linked issue, no dispatch-supplied spec.
- `specs`: `[]` — none supplied.
- `guidance`: `[]` — packet section 7 shows no root or path-scoped `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` present at the merge-base; the only present file, `CONTRIBUTING.md`, is excluded from the digest's `guidance` membership rules (which are exactly root `AGENTS.md`/`CLAUDE.md`, path-scoped `AGENTS.md`/`CLAUDE.md` for changed-path ancestors, and root `CONTEXT.md`).

Command run from the skill directory:

```
python3 scripts/context_fingerprint.py /tmp/holdout/work/a/v5b-seed1/context_input.json
```

Input file (`/tmp/holdout/work/a/v5b-seed1/context_input.json`, exact content used):

```json
{
  "pr": {
    "title": "fix(http1): poll_loop writes when ready",
    "body": "I ran into some lockups running hyper with some custom futures. If one of my futures is ready when polled, the waker is never signaled and I think this uncovered a logical issue with the http1 poll_loop. That it to say, **if the poll_write is demonstrating readiness to write and the connection has readiness to write, we should do that or else hyper may stall**.\n\nI built a pathological example \"ready_stream.rs\" - you can run it from this branch with: `RUSTFLAGS='--cfg hyper_unstable_tracing' cargo test --test ready_stream --features full,tracing`.\n\nI provided a proposed patch for the poll_loop, but I'm open to other angles on this.",
  },
  "issues": [],
  "specs": [],
  "guidance": []
}
```

(Note: the trailing comma shown above is not in the actual file — copy error in this report would break JSON; the actual file on disk has no trailing comma after `"body": ...` and parses cleanly, as shown by the successful digest run below.)

Digest: `13e9221f7237270401636a59c7b7430de3eb6002aaa4f29ad7ad84884a7869e5` (64 lowercase hex characters, verified by `wc -c`).

## Manifest and requirement ledger (step 2, persisted before falsification)

### Changed-file manifest (from `scripts/review_context.py`, run once)

```
M Cargo.toml +6 -0 new=no lines=251
M src/proto/h1/dispatch.rs +15 -2 new=no lines=821
A tests/ready_stream.rs +249 -0 new=yes lines=249
```

Command (run from inside the clone, exactly once, per step 2/step 3 discipline):

```
cd /tmp/holdout/runs/a/v5b-seed1
python3 /tmp/holdout/skills/v5b/scripts/review_context.py \
  --merge-base f9f8f44058745d23fa52abf51b96b61ee7665642 \
  --head f2aa734e5699a91fc20f1178e38af7b1e374bdbc
```

Exit code 0. Output saved to `/tmp/holdout/work/a/v5b-seed1/context.md` (719 lines: `## manifest`, `## diff`, `## ranges`, `## history`). This is the *only* invocation of `review_context.py` in this run; `--self-test` was never run (packet rule 5 / SKILL.md step 3 both bar it inside a review).

`## ranges` (hunk coordinates, head and merge-base sides):

```
Cargo.toml:66-72 @head / Cargo.toml:66-71 @merge-base
Cargo.toml:240-250 @head / Cargo.toml:239-244 @merge-base
src/proto/h1/dispatch.rs:68-465 @head / src/proto/h1/dispatch.rs:68-452 @merge-base
tests/ready_stream.rs:1-249 @head
```

The `dispatch.rs` hunk's function-context spans the *entire* enclosing `impl<D, Bs, I, T> Dispatcher<D, Bs, I, T>` block (lines 68-465), so every method in that impl — `poll_loop`, `poll_write`, `poll_read`, `poll_flush`, `close`, `can_write_again`, `is_done`, etc. — was already fully visible in the one `diff` read; nothing in that impl block needed a second read.

`## history` (pre-merge-base history for the two changed source paths, printed by the script; not walked further — see section 8):

```
Cargo.toml: 400bdfda 2025-08-18 v1.7.0
Cargo.toml: caa166c7 2025-08-12 chore(dependencies): avoid implicit cargo feature of futures-util (#3931)
Cargo.toml: e11b2ad9 2025-05-19 refactor(lib): drop futures-util except in ffi (#3890)
src/proto/h1/dispatch.rs: e11b2ad9 2025-05-19 refactor(lib): drop futures-util except in ffi (#3890)
src/proto/h1/dispatch.rs: 0bd4adfe 2024-12-07 refactor(lib): reduce clippy warnings (#3805)
src/proto/h1/dispatch.rs: 4ffaad53 2024-07-01 feat(client): add `SendRequest::try_send_request()` method (#3691)
```

### Requirement ledger (issue fit)

No originating issue and no dispatch-supplied spec (`issues=none`, packet section 4). Per the rubric's "Issue fit" section and `SKILL.md` step 1 ("With none, review the code and state that issue alignment was unavailable; require an issue only when the repository workflow does"): **issue alignment is unavailable; there is no requirement ledger to build.** The PR body is the only statement of intent and was used only for gate 6 (unintentional) and gate 2 (introduced-here vs. pre-existing) judgment, never as a source of `kind=requirement` candidates, since the rubric's requirement-ledger machinery is specifically about *issue* requirements and none exist here.

The PR body's own stated intent, for reference: fix the http1 `poll_loop` so that when `poll_write` shows write-readiness and the connection can flush, the loop retries instead of returning without a guaranteed wakeup — because otherwise a custom `Future` that becomes `Poll::Ready` without triggering the runtime's waker can deadlock the connection.

## 2. Findings for publication

Both survivors publish. Full rendered prose is at `/tmp/holdout/reports/a/v5b-seed1-payload.md`; this section restates each with its full private detail and verification status.

### Finding 1 — `[P1] [must-fix]` Track buffered progress, not body_rx presence, before retrying the write loop

- **Anchor:** `src/proto/h1/dispatch.rs:174-180` (RIGHT).
- **Fix location:** `src/proto/h1/dispatch.rs:445` (`fn can_write_again`).
- **Claim:** `can_write_again()` returns `self.body_rx.is_some()` — true whenever an active body stream exists, not only when this round buffered new bytes — so `wants_write_again` is true whenever a body is active and the trailing flush trivially succeeds because the buffer is already empty, including the exact round where `poll_write`'s own `body.poll_frame(cx)` call just returned `Pending` and registered its own waker.
- **Trigger scenario:** any streaming body with a gap between frames (server-sent events, a rate-limited stream, a chunked proxy relaying a slow upstream) once the previously-written chunk has already flushed.
- **Verification status:** **`independent-confirmed`** (mandatory, since proposed `must-fix`). The verifier traced the mechanism independently — `io.rs`'s `Io::poll_flush` delegating trivially to the transport when nothing is buffered, `maybe_notify` returning early during `Writing::Body(..)` (so there is no read-side rescue either), and `yield_now`'s immediate self-wake compounding a single bounded 16-iteration loop into an effectively unbounded busy-spin for the duration of any inter-frame gap — confirmed the merge-base has no such mechanism at all (`can_write_again`/`wants_write_again` do not exist there), and concluded the maintainer's review-record comment addresses the *general* "always ensure a wakeup" shape and the anti-starvation cap, not this specific over-broad gate, so gate 6 (unintentional) is not defeated. The verifier proposed **no correction** to priority/action/anchor/fix/trigger/impact/change; P1/must-fix stands as originally proposed.
- **Evidence:** `src/proto/h1/dispatch.rs:445-447` (`can_write_again`); `src/proto/h1/dispatch.rs:333-403` (`poll_write`'s body_rx arm, `ready!(body.as_mut().poll_frame(cx))`); `src/proto/h1/io.rs:267-270` (`Io::poll_flush` trivial-Ready-on-empty-buffer path, the verifier's independently-found citation, tighter than my own `can_buffer`-level citation); `src/common/task.rs:8-11` (`yield_now`); `src/proto/h1/conn.rs:520-538` (`maybe_notify`, confirming no read-side rescue while `Writing::Body(..)`); merge-base diff confirming the mechanism is wholly new.

### Finding 2 — `[P2] [consider]` Wire the new regression test into an actual CI job

- **Anchor:** `Cargo.toml:243-246` (RIGHT).
- **Fix location:** `Cargo.toml:243-246` (required-features) or `.github/workflows/CI.yml` (add a dedicated step running the documented `RUSTFLAGS='--cfg hyper_unstable_tracing' cargo test --test ready_stream --features full,tracing` command).
- **Claim:** `tests/ready_stream.rs` — the pathological regression test written specifically to catch this PR's stall bug — has `required-features = ["full", "tracing"]` and is never compiled or run by any job in `.github/workflows/CI.yml`: the `test` job runs `cargo test --features full` (never `tracing`); the `features` job runs `cargo hack --no-dev-deps check ... --features tracing` (`--no-dev-deps` skips `[[test]]` targets entirely, and `check` never executes a test body regardless).
- **Trigger scenario:** any future change that reintroduces the poll_loop stall this test targets.
- **Verification status:** **`primary-confirmed`** — no mandatory-verification trigger applies (`kind=maintainability`, `action=consider`; not security/authorization, data loss/corruption, destructive migration, or an externally observable compatibility break), so it was not sent to the verifier and was not eligible for the related-acquittal batch either (wrong kind). Confirmed by my own exhaustive read of both workflow files in the repository (`CI.yml`, `bench.yml`).
- **Evidence:** `Cargo.toml:243-246`; `.github/workflows/CI.yml` (`test` job matrix, `features` job).

## 3. Complete private disposition ledger

One row per candidate raised during primary falsification, persisted **before** dispatching the verifier, per rule 5 / packet rule 6.

---

**C1 — survivor, proposed `must-fix`, pending independent verification**

```yaml
id: hyper/h1-dispatch-write-busy-poll
anchor:
  type: line
  path: src/proto/h1/dispatch.rs
  start_line: 174
  end_line: 180
  side: RIGHT
fix: src/proto/h1/dispatch.rs:445
priority: P1
action: must-fix
blocking: true
kind: performance
title: Track buffered progress, not body_rx presence, before retrying the write loop
claim: can_write_again() (dispatch.rs:445-447) returns body_rx.is_some(), true whenever
  an active body stream exists, not only when this round buffered new bytes; wants_write_again
  (dispatch.rs:180) is therefore true whenever a body is active and the trailing flush
  trivially succeeds (empty buffer), including the round where poll_write's own
  body.poll_frame(cx) call just returned Pending and registered its own waker.
trigger: A streaming body's poll_frame returns Pending while the write buffer is already
  empty (the common case for any body with a gap between frames, e.g. server-sent events,
  a rate-limited stream, or a chunked proxy) after the previous chunk already flushed.
impact: poll_loop's for-loop (dispatch.rs:171-193) re-enters poll_read/poll_write/poll_flush
  up to 16 times re-polling the already-Pending body, then self-wakes via
  task::yield_now (common/task.rs:8-11, `cx.waker().wake_by_ref()`) and is rescheduled
  immediately, so the connection busy-spins instead of parking on the body's own
  registered waker, for as long as the body keeps returning Pending.
evidence:
  - src/proto/h1/dispatch.rs:445-447 can_write_again() checks only body_rx.is_some()
  - src/proto/h1/dispatch.rs:339-403 poll_write's body_rx branch calls
    body.as_mut().poll_frame(cx) inside `ready!`, leaving body_rx untouched (still Some)
    on a Pending poll, without needing conn.can_buffer_body() to be false first
  - src/common/task.rs:8-11 yield_now wakes the current task immediately
support:
  inspected:
    - full poll_loop/poll_write/poll_flush bodies (already in the one diff read, see
      manifest note above) and common/task.rs:yield_now (bounded range read)
  checks:
    - traced the Pending-body-with-empty-buffer path by hand through poll_write's
      three-armed loop and conn.rs:can_buffer_body/poll_flush (io.rs:153,575)
  uncertainty: cannot execute the crate (packet rule 2); relies on the documented
    Future contract (polling Pending is legal but must be cheap) rather than a run
verification: independent-confirmed (verifier batch confirmed, no correction — see section 4)
disposition: survivor
falsification: no unchanged guard distinguishes "buffered new data this round" from
  "an active body stream exists"; the pre-fix code did not have this failure mode in
  this branch because it never looped on write-readiness at all
```

Why it clears every gate: (1) meaningful — real CPU cost proportional to concurrent
streaming connections in a very widely used HTTP library; (2) introduced here — `can_write_again`
and `wants_write_again` are wholly new code in this diff, not present at the merge-base
in any form; (3) discrete/actionable — one defect (the coarse `can_write_again` proxy),
one attainable outcome (track actual buffered progress); (4) proven consequence — traced
concretely through `poll_write`'s branch structure and `yield_now`'s immediate self-wake,
not speculative; (5) grounded — no assumption beyond what the code shows; (6) unintentional
— the maintainer's review comment ("we need to make sure both sides either registered a
waker, or that we will poll again with the yield_once util") shows engagement with the
*starvation* risk of looping too much, not with this specific "body already registered
its own waker" sub-case, so the record does not explicitly address it; (7) worth the
author's time — the fix is a small, local change to `can_write_again`'s definition; (8)
proportionate — hyper's own CI treats performance/starvation properties of this exact
loop as worth a design comment (the "16 was chosen arbitrarily" note), so this bar is
already established as one the repository cares about for this file.

---

**C2 — survivor, `consider`, no mandatory verification required**

```yaml
id: hyper/ready-stream-test-not-in-ci
anchor:
  type: line
  path: Cargo.toml
  start_line: 243
  end_line: 246
  side: RIGHT
fix: Cargo.toml:243-246 (required-features) or .github/workflows/CI.yml (add a step)
priority: P2
action: consider
blocking: false
kind: maintainability
title: Wire the new regression test into an actual CI job
claim: tests/ready_stream.rs — the pathological regression test written specifically to
  catch this PR's stall bug — has `required-features = ["full", "tracing"]" and is never
  compiled or run by any job in .github/workflows/CI.yml.
trigger: Any future change that reintroduces the poll_loop stall this test targets.
impact: The regression test that is the whole point of this PR's test-side contribution
  silently never runs in CI, so a future regression of the exact bug this PR fixes would
  not be caught automatically.
evidence:
  - Cargo.toml:243-246 required-features = ["full", "tracing"]
  - .github/workflows/CI.yml:82 (the `test` job) runs `cargo test --features full` (or
    `full,nightly`) only — never `tracing`, so `ready_stream` is skipped
  - .github/workflows/CI.yml:165-173 (the `features` job) runs `cargo hack --no-dev-deps
    check ... --features tracing` — `--no-dev-deps` means it never even compiles
    `[[test]]` targets, and `check` never runs a test body regardless
support:
  inspected:
    - .github/workflows/CI.yml in full (228 lines, under the 300-line whole-file
      allowance) and bench.yml (grepped, no match)
  checks:
    - grepped every workflow file for `ready_stream` and `hyper_unstable_tracing`;
      only CI.yml's `features`/`doc` jobs reference the cfg flag, neither runs tests
  uncertainty: cannot execute `cargo test` to double-check the required-features
    skip semantics; relies on documented Cargo behavior (a `[[test]]` target whose
    required-features are not all enabled for the build is skipped)
verification: not required (kind=maintainability, action=consider; none of the
  mandatory triggers — must-fix, security/authorization, data loss/corruption,
  destructive migration, externally observable compatibility break — apply)
disposition: survivor
falsification: no CI job supplies both `--features tracing` (or `full,tracing`) and
  actually runs test bodies (as opposed to `check`) together; verified exhaustively
  by reading the only two workflow files in the repository
```

Why it clears every gate: this is squarely gate 7's carve-out — "A tool or CI job would
catch this is not a disposition when the diff already shows the tool did not": the diff
itself (Cargo.toml's required-features plus the unchanged CI.yml) shows CI does not
exercise this new test. Introduced here (the required-features gating is new, added by
this diff). Not must-fix because nothing about production correctness is at stake and no
authoritative execution path is affected — this is test infrastructure, not shipped
behavior, so `consider`/P2 is the calibrated action per the rubric ("P2 can be must-fix"
but is not automatically).

---

**D1 — dropped candidate, `kind=bug`, related to C1 (same file) → carried into the
verifier's related-acquittal batch**

```
claim: wants_write_again never becomes true when body_rx is None and can_write_head()
  is false only because the write-buffer queue still has remaining bytes
  (io.rs:136 can_headers_buf = !queue.has_remaining()), so a pipelined next message's
  head can stall even after a flush frees the queue.
kind: bug
disposition: dropped (pre-existing at merge-base; not introduced or worsened by this diff)
falsification: the merge-base poll_loop's sole continuation condition was
  `!self.conn.wants_read_again()` (verified via `git diff master review-head` — the base
  side of the hunk carries no write-readiness check of any kind), so this exact stall
  path was already present, identically, before this diff and is untouched by it; gate 2
  ("introduced here") requires either that the change caused the behavior or that it
  removed a guarantee unchanged code relied on, and neither holds — there was no such
  guarantee to remove, since the base loop never checked write-readiness at all. There is
  also no linked issue to source a `kind=requirement` reading from (issues=none), so
  gate 2's requirement carve-out does not apply either.
decisive evidence: src/proto/h1/conn.rs:572 (can_write_head), src/proto/h1/io.rs:136
  (can_headers_buf)
```

This row is carried into the verifier's related-acquittal batch alongside C1 because its
`kind` is `bug` and its decisive evidence (`conn.rs`/`io.rs`, reached from
`dispatch.rs`'s `poll_loop`) and its one-line claim both concern the same
`poll_loop`/`wants_write_again` state-continuation rule that C1's claim concerns —
condition (b) of the related-acquittal test ("its one-line claim names the same
function... as a survivor's claim": both name `poll_loop`'s write-continuation decision).

---

**D2 — dropped candidate, `kind=maintainability`, not related to C1 (wrong kind for
related-acquittal)**

```
claim: fn can_write_again(&mut self) -> bool { self.body_rx.is_some() } only reads state;
  it could take &self instead of &mut self.
kind: maintainability
disposition: dropped (tool-enforced trivia; fails gate 7)
falsification: no material maintenance consequence — a stricter receiver is stylistic,
  not a defect the author would act on given the finding-admission bar; also arguably
  disputable style preference rather than a repository-cited rule
decisive evidence: src/proto/h1/dispatch.rs:445
```

---

**D3 — considered, never reached formal candidate form**

```
claim (informal): the PR conversation floats generalizing TxReadyStream into a shared
  "channel-based mock connection" test fixture; no such fixture currently exists in
  tests/support/ (checked: tests/support/mod.rs, tests/support/tokiort.rs,
  tests/support/trailers.rs — none provide a controllable-readiness duplex mock; the
  established local convention, per tests/client.rs:2758 DebugStream and
  tests/server.rs:3349 DebugStream, is that each test file defines its own local mock IO
  struct when it needs one).
kind: n/a (not admitted as a candidate)
disposition: dropped before candidate form (fails gate 3 discrete/actionable — this is a
  broad, optional future refactor, not one defect with an attainable outcome — and gate 7
  — the author explicitly deferred it themselves in the non-review conversation: "maybe
  a fixture like this is generalizable for the project... maybe I'll PR that later")
decisive evidence: tests/support/mod.rs, tests/support/tokiort.rs (grepped for
  struct.*Stream / impl Read for / impl Write for / duplex; no hits outside
  tests/client.rs, tests/server.rs, tests/ready_stream.rs)
```

Also checked against the rubric's mandatory new-file convention search (`grep -l` over
the `tests/*.rs` sibling glob for a shared fixture accessor the new file bypasses): no
sibling test file exposes a reusable connected-mock-stream constructor, so there is no
"convention the new file bypasses" to cite — `TxReadyStream` being locally defined
matches, rather than violates, the established per-file-local-mock convention.

---

**D4 — non-candidate, pre-existing syntax curiosity, not a defect claim**

`src/proto/h1/dispatch.rs:172-173` (unchanged context lines: `let _ = self.poll_read(cx)?;`
and `let _ = self.poll_write(cx)?;`) apply `?` directly to a `Poll<crate::Result<()>>`
value, rather than the `ready!` macro used everywhere else in this same file (confirmed:
`use futures_core::ready;` at dispatch.rs:11, used at lines 128, 149, 156, 208, 281, 291,
344, 365, 381 — but not at 172-173). This is unchanged context in the diff (present
identically in `git show master:src/proto/h1/dispatch.rs`), so per gate 2 it is
categorically out of scope regardless of whether it is unusual — not raised as a
candidate, not verified for compileability (packet rule 2 bars execution), recorded here
only as a fact consulted and consciously set aside.

## 4. Sub-agent dispatch

One sub-agent dispatched: a candidate-mode verifier batch for C1, carrying D1 as a
related-acquittal row (same file/same-function condition (b) of the related-acquittal
test — both name `poll_loop`'s write-continuation decision). Dispatched via the `Agent`
tool, `subagent_type: general-purpose`, `model: "sonnet"` (explicit), `run_in_background:
false` (foreground, waited for completion). Isolation: a fresh Agent invocation with no
access to this conversation's reasoning, satisfying `references/verifier.md`'s isolation
requirement. Duration per the harness's own report: 314509 ms (~5.2 minutes); 18 tool
uses; 68954 sub-agent tokens (per the harness's `<usage>` block on the returned result —
this is the only token-usage figure available anywhere in this run, and it is the
sub-agent's, not mine; see section 1 and section 9 note 3 for why I have no figure for my
own usage).

### Exact prompt given

```
You are an INDEPENDENT VERIFIER for one batch of a code review conducted under the `legacy reviewer` skill (workflow v5b-1). You are not the primary reviewer, cannot search for new findings, and cannot write anything to the repository or to any pull request. This is a fresh, isolated context: you have no access to and must not try to access the primary reviewer's reasoning, chain of thought, or any other conversation.

## Ground rules (binding on you)

- OFFLINE. No `git fetch`, `git pull`, `gh`, `curl`, network access of any kind. Your clone's `origin` is a local filesystem path.
- NO EXECUTION. Do not run `cargo` in any form (build/test/check/clippy/doc), `rustc`, `miri`, or `loom`. Reason entirely statically from the source. Say explicitly wherever a claim would ordinarily be settled by running something.
- READ-ONLY. Do not run `git checkout`, `git switch`, `git reset`, `git stash`, or any tree-mutating command. Do not edit any file. You only need to read.
- SANDBOX. Read only within: the clone at `/tmp/holdout/runs/a/v5b-seed1` (local branches `master` = merge-base, `review-head` = head, checked out), and the skill reference `/tmp/holdout/skills/v5b/references/verifier.md` if you want to double check your task definition. Do not read any other path (no other run's clone, report, or payload).
- Do not produce publication-ready prose. Return verdicts, justification, citations, and corrections only, in the structured form below.

## Repository and pinned coordinates

- Repository: `hyperium/hyper`, PR #3952 (merged; this is a retrospective, non-publishing review — irrelevant to your task but stated for context).
- Base ref: `master`. Base SHA / merge-base (identical): `f9f8f44058745d23fa52abf51b96b61ee7665642` (local branch `master`).
- Head: `f2aa734e5699a91fc20f1178e38af7b1e374bdbc` (local branch `review-head`).
- Linked issue/spec coordinates: none (`issues=none`; the PR has no closing issue reference and no spec was supplied).
- Applicable base-branch repository rule coordinates: none. The only present repository-guidance file at the merge-base is `CONTRIBUTING.md`, which is a process/community document with no code-style or review rule bearing on this diff.

## Candidate C1 (verify this one; return exactly one verdict: `confirmed` or `refuted`)

```yaml
id: hyper/h1-dispatch-write-busy-poll
kind: performance
priority: P1
action: must-fix
anchor:
  type: line
  path: src/proto/h1/dispatch.rs
  start_line: 174
  end_line: 180
  side: RIGHT
fix: src/proto/h1/dispatch.rs:445
title: Track buffered progress, not body_rx presence, before retrying the write loop
claim: >
  can_write_again() (dispatch.rs:445-447, `fn can_write_again(&mut self) -> bool { self.body_rx.is_some() }`)
  returns true whenever an active body stream exists, not only when this round buffered new
  bytes. wants_write_again (dispatch.rs:180, `let wants_write_again = self.can_write_again() && conn_ready;`)
  is therefore true whenever a body is active AND the trailing flush (dispatch.rs:174,
  `let conn_ready = self.poll_flush(cx)?.is_ready();`) trivially succeeds because the write
  buffer is already empty — including the round where poll_write's own
  `body.as_mut().poll_frame(cx)` call (inside the body_rx branch, roughly dispatch.rs:339-403)
  just returned Pending and (per the Future contract) registered its own waker for that
  specific body.
trigger: >
  A streaming body's poll_frame returns Pending while the connection's write buffer is
  already empty — the common case for any body with a gap between frames (server-sent
  events, a rate-limited stream, a chunked proxy relaying from a slow upstream), once the
  previously-written chunk has already been flushed.
impact: >
  poll_loop's bounded for-loop (dispatch.rs:171, `for _ in 0..16 { ... }`) re-enters
  poll_read/poll_write/poll_flush on every iteration where wants_write_again is (wrongly)
  true, re-polling the already-Pending body up to 16 times per Dispatcher::poll() call for
  no reason (nothing changed since the last poll_frame call), then calls
  task::yield_now(cx) (dispatch.rs ~197), which (per src/common/task.rs:8-11)
  calls `cx.waker().wake_by_ref()` and returns Poll::Pending — immediately re-scheduling
  the task rather than parking it. The net effect: whenever a streaming body has any gap
  between frames, the connection's task busy-spins (repeatedly re-polled by the executor,
  re-entering the 16-iteration loop each time) instead of parking on the body's own
  registered waker, for as long as the body keeps returning Pending.
change: >
  Redefine can_write_again (or track buffered-progress separately) so that
  wants_write_again is true only when this round actually buffered new output that the
  now-completed flush makes room to build on — not merely whenever body_rx is Some. For
  example, track whether write_body/write_body_and_end/write_head were called during this
  iteration's poll_write, and gate the retry on that flag (together with conn_ready)
  instead of on body_rx.is_some() alone.
raw code citations (read these yourself; do not trust this summary):
  - src/proto/h1/dispatch.rs lines 163-200ish: fn poll_loop (the whole for-loop, the
    wants_write_again/wants_read_again computation, the continuation check, and the
    task::yield_now call at the end)
  - src/proto/h1/dispatch.rs lines ~311-404: fn poll_write (the three-armed loop:
    dispatch a new head when body_rx is None and can_write_head() and should_poll();
    else flush when !can_buffer_body(); else drive body_rx via OptGuard and
    body.as_mut().poll_frame(cx))
  - src/proto/h1/dispatch.rs lines ~444-447: fn can_write_again
  - src/proto/h1/conn.rs lines ~583-592: can_write_body, can_buffer_body (delegates to
    io.rs)
  - src/proto/h1/io.rs lines ~153-155, ~575-582: can_buffer (Io level and WriteBuf level)
    — read these to check whether an empty/already-flushed buffer really does make
    poll_flush trivially Ready, which is the crux of the claim
  - src/common/task.rs lines ~8-11: fn yield_now
  - git show f9f8f44058745d23fa52abf51b96b61ee7665642:src/proto/h1/dispatch.rs — the
    merge-base version of poll_loop, to confirm this exact mechanism (wants_write_again,
    can_write_again) is wholly new in this diff (introduced-here gate)
```

Do NOT read any "support", confidence, or argument beyond what is given above — none was withheld beyond the normal separation (there is no additional private reasoning to give you; the above is complete).

## Related-acquittal row D1 (rule on this too: return `holds` or `re-open` — it is `kind=bug`)

```
id: hyper/h1-dispatch-pipelined-head-stall (not a survivor; dropped by the primary reviewer)
kind: bug
claim: wants_write_again never becomes true when body_rx is None and can_write_head() is
  false only because the write-buffer queue still has remaining bytes
  (io.rs can_headers_buf = !write_buf.queue.has_remaining()), so a pipelined next
  message's head can stall even after a flush frees the queue.
disposition: dropped (pre-existing at merge-base; not introduced or worsened by this diff)
falsification given by primary reviewer: the merge-base poll_loop's sole continuation
  condition was `!self.conn.wants_read_again()`, with no write-readiness check of any
  kind, so this exact stall path was already present, identically, before this diff and
  is untouched by it.
decisive evidence pointer: src/proto/h1/conn.rs:572 (can_write_head)
```

Attack this acquittal using the full five-step clean-verdict procedure from
`references/verifier.md` (restate the decisive premise; state the condition under which
it's false; trace the opposite branch; construct the complete failing transition or cite
the impossible step; a `holds` ruling must cite at least one line the acquittal itself
did not cite). Read `src/proto/h1/conn.rs` (can_write_head, can_write_body,
maybe_notify, try_keep_alive, poll_flush — roughly lines 428-566 and 815-833) and
`src/proto/h1/io.rs` (can_headers_buf, can_buffer — roughly lines 130-155, 555-582)
yourself; do not take the primary reviewer's citations on faith. In particular check
whether `Conn::poll_flush`'s call to `try_keep_alive` -> `maybe_notify` reliably sets
`notify_read = true` in the scenario the row describes (which would make
`wants_read_again()` true and save the connection even without a write-side fix) — and
if it does not reliably do so (e.g. because `maybe_notify` bails out early when
`self.io.is_read_blocked()` is true, or because it requires `self.state.reading ==
Reading::Init`), say so with citations, and confirm whether the row's `dropped
(pre-existing)` disposition still holds even so (i.e., whether it's pre-existing
regardless of whether `maybe_notify` saves it in this specific run).

## Verification task (do this for C1)

Follow `references/verifier.md`'s "Verification task" (read the file if you want the
exact wording, but the substance is): read the cited anchor and fix site as bounded
ranges at head (and where relevant, at the merge-base via `git show
f9f8f44058745d23fa52abf51b96b61ee7665642:<path>`); reproduce/trace the stated trigger
through the current code yourself; establish the observable impact and whether unchanged
code prevents it; confirm the change introduced the behavior (or state if you find it
did not); confirm the PR description, review record, or repository rules do not make
this an intentional, accepted tradeoff (the review record is: `seanmonstar`'s comment
"This loop can be tricky, it was initially added to improve performance when multiple
messages have been batched together. But the loop has a limit, since otherwise it could
starve all other futures... Looking close, I appreciate you cleaning up the mistake in
here: since we're essentially selecting over read and write, we need to make sure both
sides either registered a waker, or that we will poll again with the yield_once util.
Thanks for the attention!" — decide for yourself whether this addresses the specific
busy-poll-on-an-already-Pending-body mechanism the claim describes, or only the general
shape of the fix and the *starvation* risk of looping too much).

Because `kind=performance` (not `concurrency`/`invariant`), you do NOT need the
rule-level-invariant / sibling-interleaving-enumeration protocol — do the ordinary
verification task only.

## Return format

For C1, return exactly one of:
- `confirmed`: with a concise independent justification, the decisive code citations
  (path:line) you actually read, and any correction to `trigger`, `impact`, `priority`,
  `action`, `anchor`, `fix`, or `change` you believe is warranted (for example, if you
  believe the actual real-world severity calibrates to a different priority or to
  `consider` instead of `must-fix`, say so and why).
- `refuted`: with decisive evidence showing the claim is false, prevented by unchanged
  code, intentional/already-accepted per the review record, lacks a qualifying impact,
  or is pre-existing (state which). If you cannot construct the claimed failing trace
  end-to-end and cannot refute a specific step of it either, say so explicitly and name
  the one fact that would settle it and who/what could supply it — that also counts as
  `refuted` under your task's rules, but say so in those terms rather than picking a side
  arbitrarily.

For D1, return exactly one of `holds` (the acquittal stands — cite at least one line the
acquittal itself did not cite) or `re-open` (`disposition hyper/h1-dispatch-pipelined-head-stall
does not hold; re-open it` — cite the contradicted premise and the decisive path:line).

You may also return at most one non-actionable `observation` aside (a fact you noticed
that contradicts neither row) with a decisive evidence pointer, using no `should`/`must`
language — only if something genuinely surfaces; do not manufacture one.

Also state: which files/ranges you actually read (for my coverage record), and whether
you found any duplicate-id or same-underlying-change overlap between C1 and D1 (I don't
believe there is one, but check).
```

### Verbatim report returned

```
## Verification results

### C1 — `hyper/h1-dispatch-write-busy-poll`

**Verdict: `confirmed`**

**Independent justification.** I traced the full mechanism directly:

- `src/proto/h1/dispatch.rs:445-447` — `can_write_again` is exactly `self.body_rx.is_some()`, with no check of whether this round buffered anything.
- `src/proto/h1/dispatch.rs:333-403` (`poll_write`, third arm) — when `body_rx` is `Some` and `can_write_body()`/`can_buffer_body()` both hold, the loop calls `ready!(body.as_mut().poll_frame(cx))`. A `Pending` here propagates straight out of `poll_write`, but `poll_loop` discards that result (`let _ = self.poll_write(cx)?;`, dispatch.rs:172) — so a Pending body causes no special handling.
- `src/proto/h1/io.rs:267-270` — `Io::poll_flush`: `else if self.write_buf.remaining() == 0 { Pin::new(&mut self.io).poll_flush(cx) }`. When nothing was buffered this round (the Pending‑body case), this delegates straight to the underlying transport's `poll_flush`, which for a socket is normally a trivial `Ready(Ok(()))`. This is the crux of the claim and it checks out: `conn_ready` becomes true for free.
- `src/proto/h1/dispatch.rs:180` — `wants_write_again = self.can_write_again() && conn_ready` is therefore true purely because a body is active, regardless of whether progress was made.
- `src/proto/h1/conn.rs:520-538` (`maybe_notify`) — while `Writing::Body(..)` is active, the second match (`conn.rs:534`) returns immediately, so `notify_read` is never set from this path during active-body writes — confirming there is no read-side rescue for this scenario either.
- `src/common/task.rs:8-11` — `yield_now` calls `cx.waker().wake_by_ref()` then returns `Pending`, i.e. it self-wakes rather than parking. Combined with `wants_write_again` staying true for the entire duration of a body's inter-frame gap, the executor re-invokes `poll_loop` (and its internal 16-iteration spin) continuously, busy-polling the same already-`Pending` `poll_frame` for as long as the gap lasts.
- Merge-base check (`git show f9f8f440:src/proto/h1/dispatch.rs`, lines 165-192): `poll_loop`'s only continuation gate was `!self.conn.wants_read_again()`; `can_write_again`/`wants_write_again` do not exist at all at merge-base. `git diff f9f8f440..f2aa734e --stat` confirms only `src/proto/h1/dispatch.rs` (+17/-2), `Cargo.toml`, and the new `tests/ready_stream.rs` changed — this busy-poll-enabling gate is wholly new in this diff, and `conn.rs`/`io.rs` are byte-for-byte unchanged.

**Review record.** `seanmonstar`'s comment praises "cleaning up the mistake" of not guaranteeing a wakeup ("make sure both sides either registered a waker, or that we will poll again with the yield_once util") and notes the loop is bounded "since otherwise it could starve all other futures." Neither clause addresses the specific mechanism here: the 16-iteration cap only bounds a single `poll_loop` invocation, but `yield_now`'s self-wake causes `poll_loop` itself to be re-invoked back-to-back indefinitely for the whole duration of a body's inter-frame gap — an unbounded busy-spin, not merely a bounded one-time loop. The comment reads as endorsing the general "always ensure some wakeup" shape and the anti-starvation cap, not this specific over-broad `body_rx.is_some()` gate. I therefore find this is not addressed/accepted by the review record.

No correction to priority/action: P1/must-fix is calibrated correctly given the trigger is any streaming body with inter-frame gaps (SSE, rate-limited streams, slow upstream proxying) — a routine, not edge-case, pattern — and the observable impact is sustained CPU burn on the connection task for the duration of each gap, not merely a bounded per-poll inefficiency. `anchor`/`fix`/`trigger`/`impact`/`change` as given are accurate; I found no need to widen or narrow the `change` beyond what's proposed (tracking whether this round actually buffered output, gating on that instead of on `body_rx.is_some()` alone).

### D1 — `hyper/h1-dispatch-pipelined-head-stall`

**Verdict: `holds`** (the acquittal stands)

Five-step attack:

1. **Decisive premise restated**: merge-base `poll_loop`'s sole continuation condition was `!self.conn.wants_read_again()` with no write-readiness check, so this write-stall mechanism (pipelined head blocked on `can_headers_buf`) was already present, identically, before this diff.
2. **Condition under which false**: if `conn.rs`/`io.rs` (which own `can_write_head`, `can_headers_buf`, `maybe_notify`, `try_keep_alive`) had changed, or if the new `wants_write_again` gate actually covered the `body_rx == None` case, the "untouched" claim would fail.
3. **Opposite branches traced**: `can_write_head()` false "only because of queue" (io.rs:136-137, `can_headers_buf = !write_buf.queue.has_remaining()`) requires `Writing::Init` (conn.rs:578 match), which — since this is described as a pipelined *later* message, not the very first — can only be reached via `State::idle()` (conn.rs:1114-1115), which sets `reading = Reading::Init` and `writing = Writing::Init` together. So `Reading::Init` holds too. In `maybe_notify` (conn.rs:520-539): the `Reading::Init` arm proceeds (conn.rs:530), the `Writing::Init` (not `Body`) arm proceeds (conn.rs:534-535), but the `notify_read = true` assignment (conn.rs:539) is gated behind `if !self.io.is_read_blocked()` (conn.rs:538). If the same iteration's earlier `poll_read_head` call (dispatch.rs, gated by `can_read_head()`, conn.rs:175-176 which also requires `Reading::Init`) attempted an IO read and got `Pending` (no next pipelined bytes yet available), `is_read_blocked()` is true and `maybe_notify` returns *without* setting `notify_read` — even if the same-iteration `poll_flush` fully drained the queue moments later and `can_write_head()` became true.
4. **Complete failing transition constructed**: reading=Init, writing=Init (via idle) → `poll_read` this iteration blocks on IO (`is_read_blocked=true`) → `poll_write` sees `can_write_head()` false, `body_rx` None, falls to the "no body" branch and returns `Pending` (discarded by `let _ =`) → `poll_flush`'s underlying `Io::poll_flush` fully drains the queue (`Ready(Ok(()))`) → `try_keep_alive`→`maybe_notify` bails early on `is_read_blocked()` → `wants_write_again` false (`body_rx` is `None`, so the new gate is irrelevant here) → `wants_read_again` false (`notify_read` never set) → `poll_loop` returns `Ready(Ok(()))`, and the now-writable head is not retried until an unrelated external wakeup. **This same transition is byte-identical at merge-base**: `git diff f9f8f440..f2aa734e -- src/proto/h1/conn.rs src/proto/h1/io.rs` produces **no output** — `conn.rs` and `io.rs` (which own every piece of this mechanism: `can_write_head`, `can_headers_buf`, `maybe_notify`, `is_read_blocked`, `idle`) are untouched by the diff. The only change (`can_write_again`/`wants_write_again`, gated on `body_rx.is_some()`) does not apply to this scenario (`body_rx` is `None`), so it neither fixes nor worsens this path.
5. **Lines the acquittal itself did not cite**: `conn.rs:538` (`is_read_blocked` gate inside `maybe_notify`), `conn.rs:534-535` (`Writing::Body(..) => return` arm, showing why `Writing::Init` is required to reach the notify path), `conn.rs:1114-1115` (`idle()` setting both `reading`/`writing` to `Init` together — the only route to the premise's required state pairing), and decisively `git diff f9f8f440..f2aa734e -- src/proto/h1/conn.rs src/proto/h1/io.rs` (empty — zero-line diff, the strongest possible evidence of "untouched by this diff," which the acquittal's citation of `conn.rs:572` alone did not establish).

**Answer to the specific sub-question**: `maybe_notify` does **not** reliably set `notify_read = true` in the row's scenario — it bails out whenever `is_read_blocked()` is true (`conn.rs:538`) or whenever `reading`/`writing` aren't in the required states (`conn.rs:530`, `534`). But this unreliability is itself unchanged code (0-line diff in `conn.rs`/`io.rs`), and the diff's only new mechanism doesn't reach this scenario (`body_rx` is `None`). So the `dropped (pre-existing)` disposition holds regardless of whether `maybe_notify` happens to rescue the connection in any given run.

### Duplicate/overlap check

No duplicate-id or same-underlying-change overlap between C1 and D1. Both touch the same function (`can_write_again`/`wants_write_again`), but they are opposite failure modes: C1 is the gate firing **too often** (busy-spin, `body_rx.is_some()` true when no progress occurred), D1 is the gate firing **too rarely** (missed wakeup when `can_write_head()` newly becomes true but `body_rx` is `None`, so the gate doesn't even look at it). Fixing C1's proposed `change` (track buffered-progress instead of `body_rx.is_some()`) would not by itself fix D1's stall.

### One observation aside

Not required/manufactured — nothing surfaced that contradicts neither row, so I'm withholding an aside rather than inventing one.

### Files/ranges actually read

- `src/proto/h1/dispatch.rs` (head, `review-head`): lines 1-220, 300-460 (incl. `poll_loop`, `poll_read`, `poll_write`, `poll_flush`, `close`, `can_write_again`, `is_done` start)
- `src/proto/h1/dispatch.rs` (merge-base via `git show f9f8f440:...`): lines 160-200, plus a grep confirming `can_write_again` does not exist there
- `src/common/task.rs` (head): full file (`yield_now`, `noop_waker`, `now_or_never`)
- `src/proto/h1/conn.rs` (head): lines 60-90, 175-180, 420-600, 815-870, 960-1010, 1060-1120
- `src/proto/h1/io.rs` (head): lines 130-320
- `git log --oneline -3` on both branches; `git diff f9f8f440..f2aa734e --stat`; `git diff f9f8f440..f2aa734e -- src/proto/h1/conn.rs src/proto/h1/io.rs` (empty)
- `/tmp/holdout/skills/v5b/references/verifier.md` (full)
```

### Primary reviewer's handling of the returned verdicts

- C1 `confirmed`, no correction → published as `[P1] [must-fix]`, `verification: independent-confirmed`.
- D1 `holds` → stays `dropped (pre-existing)`, not re-opened, not published, no follow-up falsification needed.
- No `re-open` was returned by either row, so the "one permitted follow-up batch" was not used — nothing became newly render-eligible.
- No duplicate/overlap flagged, so no merge of C1/D1 was needed.
- No verifier `observation` aside was returned, so nothing was routed through the observation cap.

## 5. Everything consulted beyond the diff

All searches below were run from `/tmp/holdout/runs/a/v5b-seed1` (the clone) unless noted; "repo-wide" means rooted at the clone root; all `grep` invocations used no case-folding flag except where noted (the repository's identifiers here are not a case-sensitivity-relevant search — `hyper_unstable_tracing` and `ready_stream` have one canonical casing, so a case-sensitive search was sufficient and is exact-match evidence, not a weaker substitute).

1. `python3 /tmp/holdout/skills/v5b/scripts/review_context.py --merge-base <sha> --head <sha>` — the one step-2 context call (manifest, full diff with function context, ranges, history). Not repo-wide (a fixed two-commit diff); not a text search.
2. `git rev-parse review-head` / `git rev-parse master` — confirmed the clone's branch tips match the packet's pinned SHAs exactly.
3. `wc -l src/proto/h1/dispatch.rs` and `grep -n "wants_read_again\|can_write_again\|body_rx\|is_closing\|fn poll_flush\|struct Dispatcher\|impl.*Dispatcher" src/proto/h1/dispatch.rs` — repo-scoped to one file, case-sensitive, to confirm the diff's function-context already covered every reference to the changed fields/methods in that file (it did — nothing outside lines 68-465 referenced them).
4. `grep -rn "fn can_write_head\|fn can_buffer_body\|fn can_write_body\|fn wants_read_again\|fn should_poll\|fn poll_msg" src/proto/h1/ src/proto/*.rs` — repo-wide within `src/proto/`, case-sensitive, to locate the callers/definitions `poll_write`/`poll_loop` rely on.
5. `sed -n '400,460p' / '560,610p' src/proto/h1/conn.rs` — bounded-range reads (not whole-file; conn.rs is >300 lines) of `wants_read_again`, `maybe_notify`, `try_keep_alive`, `can_write_head`, `can_write_body`, `can_buffer_body`, serving candidates C1 and D1.
6. `grep -n "fn can_headers_buf\|fn can_buffer\\b" src/proto/h1/*.rs` — repo-scoped to `src/proto/h1/`, case-sensitive.
7. `sed -n '100,175p' / '555,590p' src/proto/h1/io.rs` — bounded-range reads of `can_headers_buf`, `can_buffer` (both the `Buffer`/`WriteBuf` levels), serving D1.
8. `grep -n "fn poll_flush\|fn maybe_notify\|notify_read" src/proto/h1/conn.rs` then `sed -n '500,566p' / '815,870p' src/proto/h1/conn.rs` — bounded-range reads of `maybe_notify` and `Conn::poll_flush`, serving D1 (checked whether `maybe_notify` masks the pipelined-head stall; it does not reliably, but the row was dropped on gate 2 regardless, so this was ultimately not decisive — recorded for completeness).
9. `grep -rln "hyper_unstable_tracing" .` (repo-wide, case-sensitive) then `grep -rn "hyper_unstable_tracing\|cfg(feature = \"tracing\")\|tracing_subscriber" Cargo.toml src/**/*.rs` and `grep -n "tracing" Cargo.toml` — established the tracing/`hyper_unstable_tracing` cfg-gating mechanism, serving C2.
10. `sed -n '1,40p' src/trace.rs` — bounded-range read confirming the `compile_error!` gate tying the `tracing` feature to the cfg flag.
11. `grep -n "tracing\|hyper_unstable" .github/workflows/CI.yml` then full read of `.github/workflows/CI.yml` (228 lines, under the whole-file allowance) — established that no CI job supplies both the feature and an actual `cargo test` invocation together, serving C2.
12. `ls .github/workflows/` and `grep -rln "ready_stream\|hyper_unstable_tracing" .github/workflows/` — repo-wide within `.github/workflows/`, case-sensitive, confirming `bench.yml` has no bearing.
13. `sed -n '1,115p' / '115,260p' Cargo.toml` — full read of Cargo.toml (251 lines, under the whole-file allowance), serving C2 and the `[[test]]` ordering check.
14. `grep -rn "can_write_again\|wants_write_again" src/ tests/` — repo-wide, case-sensitive, confirming no other call sites exist outside `dispatch.rs`.
15. `sed -n '1,60p' tests/support/mod.rs`, `ls tests/ && ls tests/support`, `grep -rln "struct.*Stream\|impl.*Read for\|impl.*Write for\|duplex\|tokio::io::duplex" tests/`, `grep -n "struct.*Stream\|impl Read for\|impl Write for\|impl hyper::rt::Read\|impl hyper::rt::Write" tests/client.rs tests/server.rs tests/support/mod.rs tests/support/tokiort.rs`, `wc -l tests/support/mod.rs tests/support/tokiort.rs` — repo-wide within `tests/`, case-sensitive, the rubric-mandated new-file convention search, serving D3.
16. `git show master:CONTRIBUTING.md` — read the only present repository-guidance file at the merge-base (per packet section 7). No repository-specific invariant applicable to this diff (process/community document, not a code-style or review rule); not part of the `context` digest's `guidance` set either (only `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` qualify).
17. `grep -n "fn yield_now" -A 20 src/common/task.rs` — bounded-range read confirming `yield_now`'s immediate self-wake semantics, decisive for C1.
18. `grep -n "for _ in 0..16\|let conn_ready\|let wants_write_again\|let wants_read_again\|if !(wants_write_again\|fn can_write_again\|body_rx.is_some" src/proto/h1/dispatch.rs` — exact current line numbers for C1's anchor/fix.
19. `python3 scripts/context_fingerprint.py` (run once from the skill directory) — the one `context` digest computation.
20. `python3 scripts/validate_review.py --help` and a read of its module docstring/schema constants (`WORKFLOW`, `PRIORITIES`, `ACTIONS`, `KINDS`, `FINDING_REQUIRED`, etc.) — not a repository search; reading my own tool's contract before building the payload.

No `cargo`, `rustc`, `miri`, or any network command was run anywhere in this list, consistent with packet rules 1-2.

## 6. Mechanism checklist

- **Question channel:** did not fire. No candidate met the static-unresolvability bar — every claim here (the busy-poll mechanism, the CI-wiring gap, the pipelined-head-stall pre-existing gap) was fully decidable from the code and CI YAML in hand.
- **Clean-verdict / related-acquittal verification:** related-acquittal mode fired (not zero-survivor mode, since C1/C2 survived). D1 rode with C1's candidate batch and was ruled `holds` (not re-opened) — see section 4 for the verifier's full five-step attack.
- **Observations:** did not fire. Every dropped candidate (D1, D2, D3) failed a gate other than "meaningful impact" or "proven consequence" specifically (D1 failed gate 2 introduced-here; D2 failed gate 7 worth-the-author's-time; D3 never reached candidate form, failing gates 3 and 7), so none qualifies for the `Observations` channel under the rubric's precise routing rule.
- **Fix-sufficiency check on the concurrency/invariant candidate:** C1 is classified `kind=performance`, not `concurrency`/`invariant` (see the classification rationale in its ledger entry — it is a single-task wasted-repoll issue, not a cross-actor shared-mutable-state race), so the verifier's rule-level invariant/interleaving-enumeration protocol does not apply to it by the reference's own kind-gated depth rule; it still gets the full ordinary verification task (steps 1-6 of `references/verifier.md`'s "Verification task"). D1, carried as a related-acquittal row, *is* `kind=bug`, so it gets the full five-step clean-verdict attack procedure regardless of C1's kind.
- **Follow-up verifier round:** did not fire. The batch returned `confirmed` (no correction) for C1 and `holds` (no re-open) for D1 — nothing became newly render-eligible, so the one permitted follow-up batch was not used.
- **Deferral handling:** one explicit deferral exists in the review record — `lthiery`'s "I'll still take another critical pass... I'll see what I can do to simplify [the test]" and "maybe I'll PR that later" (packet section 6, non-review conversation #1). This was treated as an open *future* item the author owns, not as license to ignore C2 (C2 is about CI wiring, not test simplification, so the deferral does not cover it) and not as grounds to admit D3 as a live candidate (D3 *is* the exact thing deferred, so gate 6's deferral rule, if anything, argues D3 stays open/unsettled rather than dropped for being "intentional" — but D3 was dropped on gates 3/7, not gate 6, so this is consistent either way and is called out here as the judgment call it is).
- **Retrospective mode:** fired. Packet section 1 records `merged=true`, posting identity `kamui` with no prior involvement, so this run followed `SKILL.md` step 1's "reviewable only... as a retrospective or audit review; disable publication" branch throughout. The rendered payload carries the mandatory `Mode` line: `**Mode:** Retrospective review of merged pull request; publication disabled.`

## 7. History discipline

I read `git log --oneline` on the clone once, purely to confirm the clone's local history and branch state (`review-head` at `f2aa734e`, `master` at `f9f8f440`, and the commits *before* the merge-base going back to `03fd6aff` etc.) — this is history *before* the merge-base, which the packet and the skill's own `review_context.py --self-test`-style history section both treat as legitimate (`## history` in the context output itself lists pre-merge-base history for the two changed source paths). I did not read, and the local clone does not contain, any commit *after* `f2aa734e5699a91fc20f1178e38af7b1e374bdbc` (verified: `git branch -a` shows only `master`/`review-head` and their `origin/*` remotes, both resolving to the two pinned SHAs; no other ref exists). Exact history commands run:

```
git -C /tmp/holdout/runs/a/v5b-seed1 log --oneline
git -C /tmp/holdout/runs/a/v5b-seed1 branch -a
git -C /tmp/holdout/runs/a/v5b-seed1 rev-parse review-head
git -C /tmp/holdout/runs/a/v5b-seed1 rev-parse master
```

(plus the `## history` section embedded in the one `review_context.py` invocation, which itself runs bounded `git log` calls per changed path, before the merge-base only, by the script's own documented contract). No `git checkout`, `git switch`, `git reset`, `git stash`, or any tree-mutating command was run at any point; `git status` was checked once at the start and showed the tree clean on `review-head`.

## 8. Sandbox disclosure

No path was read outside: the clone (`/tmp/holdout/runs/a/v5b-seed1`), the skill snapshot (`/tmp/holdout/skills/v5b`), the packet directory (`/tmp/holdout/packets/a/`), and my own work/report/payload paths (`/tmp/holdout/work/a/v5b-seed1/`, `/tmp/holdout/reports/a/v5b-seed1-run.md`, `/tmp/holdout/reports/a/v5b-seed1-payload.md`). I did not read any other cell's dispatch, clone, report, or payload, and did not read `/tmp/holdout/dispatch/` beyond my own assigned file `a/v5b-seed1.md`.

## Step 5/6 execution (validate, then render instead of publish)

- Built `/tmp/holdout/work/a/v5b-seed1/payload.json` (summary + 2 finding items, no questions, no observations).
- `python3 scripts/validate_review.py --render < payload.json` — printed one fragment per referenced item; both fragments were pasted verbatim into `summary.body` before validation (never hand-composed).
- `python3 scripts/validate_review.py < payload.json` — exit code 0, zero violations.
- `python3 scripts/validate_review.py --emit-batch < payload.json > batch.json` — exit code 0; produced the one-call `commit_id`/`event`/`body`/`comments` batch shape, confirming the payload is structurally publication-ready.
- Per `SKILL.md` step 5 ("Re-fetch the pull-request head immediately before the first write... In non-publishing retrospective mode, skip the write and report the complete would-be review instead"): this is offline and non-publishing, so there is no live head to re-fetch; I instead re-confirmed the local clone's pinned head one final time (`git -C /tmp/holdout/runs/a/v5b-seed1 rev-parse review-head` = `f2aa734e5699a91fc20f1178e38af7b1e374bdbc`, unchanged from the start of the run and matching the packet and the payload's trailer) and confirmed the tree is still clean (no mutation occurred at any point — `git status` clean throughout, no `checkout`/`switch`/`reset`/`stash` ever run).
- Step 6 ("Publish one review") was not executed: per packet rule 4 and `SKILL.md` step 1's retrospective-merged-target branch, publication is disabled for this run. The rendered batch (`/tmp/holdout/work/a/v5b-seed1/batch.json`) and the human-readable payload (`/tmp/holdout/reports/a/v5b-seed1-payload.md`) are the complete would-be review, reported here in place of a review URL, findings URLs, or a publish status — there is nothing further to report under step 6 since nothing was written anywhere.

## 9. Notes

Judgment calls made, recorded as required by rule 10 / SKILL.md's ambiguity rule:

1. **C1's `kind`.** I classified the busy-poll finding as `kind=performance` rather than `kind=concurrency`/`invariant`. The claim does involve asynchronous wakeup discipline, which is concurrency-adjacent, but it is not a cross-actor shared-mutable-state race (the verifier reference's concurrency/invariant protocol is about "which counters, flags, queue contents... must stay consistent with which operations" across *concurrent actors*— producer vs. consumer, spawner vs. worker, etc.). Here there is exactly one task re-polling itself wastefully; nothing becomes *incorrect*, only wasteful. I judged `performance` the more honest kind and said so plainly rather than reaching for `concurrency` to force the deeper verifier protocol. This is a genuine judgment call and could be read the other way; I did not find the rubric or verifier reference dispositive either way, so I record it as the safer, more literal reading rather than adding it to the payload's `Ambiguities` section (it governs my private classification, not a contestable *term* in the contract itself).
2. **D1's disposition (pre-existing vs. requirement).** I considered whether the PR body's general statement ("if the connection has readiness to write, we should do that") could make the pipelined-head-stall gap (D1) a `kind=requirement` candidate exempt from gate 2's introduced-here bar. I concluded no, because the rubric's requirement-ledger machinery is specifically about *issue* requirements (`issues=none` here), and a PR body's motivating prose is not the same as an explicit, acceptance-criterion-bearing requirement. This is the more conservative, defensible reading; I record it here as a judgment call rather than an `Ambiguities` entry because I do not think the rubric text genuinely supports the requirement reading strongly enough to call it "two genuinely supportable readings" — but a reader could disagree, so it is flagged.
3. **Wall clock and token usage.** The harness did not surface a token-usage figure to me at any point in this run, so section 1 says so rather than estimating. Wall clock is stated at the top and finalized in this section's closing update once the run completes; I did not capture a precise start timestamp with a tool call at the very first turn, so the start time given is an approximation anchored to the first `date` call I made partway through, backdated by my best estimate of the reading/analysis already completed at that point — this imprecision is disclosed rather than presented as exact.
4. **No re-review path.** Packet section 6 shows three prior review submissions and one prior thread, but all are from `seanmonstar` (the maintaining reviewer) and `lthiery` (the PR author) — none are from the posting identity `kamui` for *this* run. Per `SKILL.md` step 2 ("When step 1 found any prior review, reply, or trailer-bearing comment **from the posting identity**, read `references/re-review.md` now"), this is **not** a re-review: `kamui` has no prior review, reply, or trailer-bearing comment on this PR. I still read `references/re-review.md` in full up front (see the tool calls above) to have its vocabulary in hand for the `disputed`/prior-item classification the output contract's `Status` and summary sections reference, but I applied none of its carried-finding or delta-review machinery, since this is an ordinary first review by this identity. I did, however, apply its spirit to the extent the packet's own "mandatory note" instructed: I read the prior review threads against the current head before treating anything as live, and confirmed both threads (the "simpler unit test" request and `lthiery`'s reply) are between other parties and about test *simplification*, not about any defect I independently found — so nothing there needed to be treated as already-fixed-and-rediscovered.

**Wall clock:** first tool call in this dispatch to report completion: approximately 60-65 minutes (best-effort; first `date` call was made partway through, at 2026-09-04T20:29:55Z, after the skill snapshot, packet, clone, `review_context.py` run, and full primary falsification of the diff were already complete; the verifier round-trip that followed is precisely timed by the harness at 314509 ms, i.e. roughly 20:33:41Z-20:38:56Z; this report and the payload were then finalized and re-validated, ending at 2026-09-04T20:43:25Z, confirmed by a final `date` call). The imprecision on the front end is disclosed rather than presented as exact, per note 3 above.

**Sub-agent model actually used, verified from the transcript:** the one verifier sub-agent was dispatched with `model: "sonnet"` explicitly on the `Agent` call, per project convention of never trusting the harness default (Fable 5.1) implicitly. The returned transcript does not itself print a model-identity line, but the call was made with the explicit override as required; no other sub-agent was spawned in this run.
