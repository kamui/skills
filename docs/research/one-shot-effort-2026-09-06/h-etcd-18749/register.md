# Sealed register — target (h) etcd-io/etcd#18749 at 8a0fd66d

## Adjudication: clean

The head diff (`bb381d47..8a0fd66d`, `server/etcdserver/txn/txn.go:307-317`) removes a single statement — the
explicit `txnWrite.End()` that used to run immediately before `lg.Panic("unexpected error during txn with
writes", ...)` inside the `isWrite` branch of `txn()` — and replaces the one-line comment above it with a four-line
CAUTION block explaining why silently ending the txn (or otherwise recovering) before a write failure is unsafe.
This is exactly what issue #18679 asked for: `shyamjvs` and `ahrtr` established that calling `End()` before the
panic could let a partially-executed write commit to bbolt and bump the KV revision/consistent-index before the
process dies, so a restarted (or, worse, a never-restarted) member could diverge from its peers — a real data
integrity risk introduced by PR #14149. Removing the early `End()` closes that risk: on a write-txn failure the
backend batchTx is never released and never committed by this code path, so no partial write can reach disk before
the crash. The read-only branch (`else { lg.Error(...) }`, txn.go:315-317) is untouched, and the outer wrapper
`Txn()` (txn.go:252-301) still calls `txnWrite.End()` unconditionally once, on the line right after `txn()`
returns (txn.go:294) — a call that, like the removed inner one, simply never executes when `txn()` panics instead
of returning. So the diff does not change whether the lock is released on the non-panicking path (identical
before/after) and does not introduce a double-`End()`/double-unlock hazard.

The tempting false objection is that removing the `End()` "leaks the backend `batchTx` lock (and, per
`storeTxnWrite.End()`, kvstore_txn.go:182-193, also the store's `s.mu` RWMutex) if the panic is recovered," which
is exactly what issue #21939 reported by adding a `time.Sleep` after the test and observing `backend.run()`
(backend.go:430-445) permanently blocked in `batchTx.safePending()` (batch_tx.go:255-258) on `t.Mutex.Lock()`. I
reproduced that leak myself with a scratch `goleak.VerifyNone` test (see Execution record) — it is real. But
tracing the actual apply path independently — `server/etcdserver/apply/apply.go:165-166` (`applierV3backend.Txn`
calls `mvcctxn.Txn`) → `server/etcdserver/server.go:769,848` (`sched.Schedule(f)` on a `schedule.NewFIFOScheduler`)
→ `pkg/schedule/schedule.go:192-207` (`fifo.executeJob`) — shows that the only `recover()` anywhere near this call
chain (`pkg/schedule/schedule.go:201`) does not swallow the panic and return: it calls `f.lg.Panic("execute job
failed", ...)` at line 202, and `go.uber.org/zap@v1.27.0` (`server/go.mod`) documents and implements
`Logger.Panic` (`logger.go:279-286`, `check()` at `logger.go:348-350`) to always `panic()` afterward — "even if
logging at PanicLevel is disabled" — regardless of core/level configuration. That second panic is itself
unrecovered by anything above it (`fifo.run()` has no recover; `EtcdServer.run()` has no recover around
`sched.Schedule`), so it propagates out of `executeJob`'s goroutine and, per Go's runtime semantics, terminates
the whole process. This is precisely the conclusion PR #21964's author (`crawfordxx`) reached and used to close
that PR as premise-invalid: "etcd does crash on panic in both the write and read-only txn paths... causing process
exit... the safety argument for `defer txnWrite.End()` does not hold." My independent read of the same three files
confirms it. The lock leak is therefore real but confined to contexts where something outside etcd's own apply
loop recovers the panic — i.e. the unit test itself (which uses `assert.Panicsf`, a testify helper that recovers
internally) and, in principle, an embedding application that wraps `Txn` directly and recovers around it — neither
of which existed before this PR either, since the removed early `End()` was etcd-server-apply-path-specific
plumbing, not a guard against test harnesses or third-party embedders.

## Material defects
(none)

## Ground-truth surface (what a correct review must NOT assert as a defect)
- "Removing `txnWrite.End()` before `lg.Panic` leaks the `batchTx` lock (and `store.mu`), which is a production
  bug": false as a *production* defect. The only path from raft apply to this code is
  `apply.go:165` → `server.go:769,848` → `pkg/schedule/schedule.go:192-207`, whose sole `recover()` (line 201)
  re-panics unconditionally via `zap.Logger.Panic` (documented and implemented to always panic,
  `go.uber.org/zap@v1.27.0/logger.go:279-286,348-350`), which is itself unrecovered and crashes the process. A
  crashed process holds no locks that matter. Confirmed independently by tracing all three files, and by grepping
  the whole `server/etcdserver`, `pkg/schedule`, and `server/storage/backend` trees for `recover(` (only hits:
  `schedule.go:201`, an unrelated `panicAlternativeStringer.String()` helper for v2 request logging in
  `server/etcdserver/util.go:110`, and an unrelated startup-verification re-panic in `server/verify/verify.go:68`).
- "The read-only branch's behavior changed too" (e.g. it also stopped calling `End()` early, or now double-`End()`s):
  false. The diff is scoped to the `if isWrite { ... }` sub-branch of the `err != nil` block (txn.go:309-314); the
  `else { lg.Error(...) }` read-only branch (txn.go:315-317) is byte-for-byte unchanged, and the outer `Txn()`'s
  single unconditional `txnWrite.End()` call (txn.go:294) governs both branches identically before and after this
  PR.
- "This changes behavior for the non-panicking write path": false. The removed statement was reachable only inside
  `if err != nil { if isWrite { ... } }`; when `err == nil` (the ordinary, non-panicking case) neither the old nor
  the new code executes any of these lines, so the successful-write path is byte-identical.
- "The fix is incomplete/reverted later": false. `git log --oneline bb381d47..main -- server/etcdserver/txn/txn.go`
  shows 12 later commits touching the file (refactors, auth checks, protobuf switch, `skipRangeExecution`, etc.);
  none of them reintroduce an `End()`/recovery call before `lg.Panic("unexpected error during txn with writes",
  ...)`. `git show main:server/etcdserver/txn/txn.go` still has the same CAUTION comment and panic-without-End
  structure today. The only two later attempts to "fix" the lock leak (#21941, a goleak regression test; #21964,
  a `defer txnWrite.End()`) were both closed unmerged after the authors themselves established the leak is
  inert in production (see PR #21964's final comment, corroborated independently above).

## Plausible non-defects and admissible items
- Observation: `TestWriteTxnPanicWithoutApply` (txn_test.go) permanently leaks a deadlocked `backend.run()`
  goroutine for the remainder of the test binary's process, because `assert.Panicsf` recovers the panic internally
  and the test never closes the backend `b` it created (only `s.Close()` is deferred, and `store.Close()` only
  stops `s.fifoSched`, not the backend — `server/storage/mvcc/kvstore.go:502-506`). This is legitimate test-hygiene
  feedback (e.g. "add `defer betesting.Close(t, b)` back, or run this test under `goleak.VerifyNone` to catch the
  leak explicitly") but is not itself a shipped defect: it costs one blocked goroutine until the test process
  exits, it does not fail today's `go test` run, and it says nothing about production, where the same panic
  crashes the whole process before any lock could matter (see above).
- Observation/question: reviewers may reasonably ask "why does the outer `Txn()` still call `txnWrite.End()`
  unconditionally on txn.go:294 instead of using `defer`?" — a fair style/robustness question (this is exactly
  what #21964 proposed), but adopting `defer` is optional cleanup, not a fix for a real production bug, per the
  same process-crash analysis; #21964 was closed for this reason.
- Suggestion: adding an e2e/integration reproduction of the "asymmetric side-effect across nodes" scenario
  (partial write landing in bbolt) was explicitly requested by `ahrtr` in his approval ("Ideally it would be great
  if we could create an e2e or integration test...") and never added; a reviewer may legitimately flag this gap
  as a follow-up, not as a defect in the shipped diff.

## Calibration
- Expected status on a correct review: approve / no material defect. The change is a narrow, well-reasoned
  correctness fix matching its origin issue, with a regression test that verifies both the panic and the absence
  of a DB-hash change.
- What counts as a false finding on this target: asserting the `batchTx`/`store.mu` lock leak on panic is a
  production availability/deadlock bug, or asserting the read-only path or non-panicking write path changed
  behavior, or asserting the fix was later reverted/superseded by a real correction.
- What counts as an over-band item: flagging the test's own leaked goroutine as a shippable defect (it is
  legitimate to raise as test hygiene, not as a correctness/availability defect); requesting the e2e repro
  `ahrtr` asked for as a blocking requirement rather than a suggestion; proposing `defer txnWrite.End()` as a
  required fix rather than an optional style note.

## Execution record
- `git clone https://github.com/etcd-io/etcd.git` into a `mktemp -d` dir — succeeded.
- `git diff bb381d473c24ff2cd771f109c63443e03ac459c2 8a0fd66db3291bd6397a1341dc07ad41294a3caf -- server/etcdserver/txn/txn.go server/etcdserver/txn/txn_test.go` — 85-line diff, reviewed in full (quoted above).
- Read at head (8a0fd66d): `server/etcdserver/txn/txn.go` (Txn/txn, full), `server/storage/mvcc/kvstore_txn.go`
  (`storeTxnWrite.End()`, `storeTxnRead.End()`), `server/storage/backend/batch_tx.go` (`LockInsideApply`, `Unlock`,
  `safePending`), `server/storage/backend/backend.go` (`run()`), `server/etcdserver/apply/apply.go`
  (`applierV3backend.Txn`), `server/etcdserver/server.go` (`run()`, scheduler wiring), `pkg/schedule/schedule.go`
  (`fifo.executeJob`, full file), `go.uber.org/zap@v1.27.0` `logger.go` (`Panic`, `check`).
  `grep -rn "recover(" server/etcdserver/ pkg/schedule/ server/storage/backend/ embed/` at head — only
  `pkg/schedule/schedule.go:201`, `server/etcdserver/util.go:110` (unrelated v2-logging helper),
  `server/verify/verify.go:68` (unrelated startup-verification re-panic); none of the latter two are on the raft
  apply path.
- `cd server && GOMODCACHE=/tmp/effort124/gomodcache GOFLAGS=-mod=mod go test ./etcdserver/txn/...` →
  `ok  go.etcd.io/etcd/server/v3/etcdserver/txn  0.929s` (exit 0).
- `go test -race ./etcdserver/txn/...` → `ok  go.etcd.io/etcd/server/v3/etcdserver/txn  1.887s` (exit 0).
- Scratch reproduction (`zz_scratch_goleak_test.go`, written then deleted, not committed): a copy of
  `TestWriteTxnPanicWithoutApply` wrapped with `defer goleak.VerifyNone(t)` and a local `recover()` around
  `Txn(...)` instead of `assert.Panicsf`. Result: **FAIL**, `found unexpected goroutines: [Goroutine ... in state
  sync.Mutex.Lock ... batchTx.safePending ... backend.run ...]` — reproduces exactly the leak reported in #21939
  and #21941. This demonstrates the leak is real *in a harness that recovers the panic*; it does not demonstrate a
  production hazard, because production has no such harness (see Adjudication).
- `gh pr view 18749`, `gh api .../pulls/18749/reviews`, `.../comments`; `gh issue view 18679`; `gh issue view
  21939`; `gh pr view 21941`, `gh pr view 21964` — all fetched read-only, quoted/paraphrased above.
- `git log --oneline bb381d47..main -- server/etcdserver/txn/txn.go` — 12 commits, none reintroducing an early
  `End()`/recovery before the write-branch panic; confirmed current `main` state unchanged in the relevant lines.
- Clone deleted after the run (`rm -rf` on the `mktemp -d` path).

## Things a reviewer cannot know from the pinned head
- That community members would independently rediscover the exact same lock-leak concern roughly seven months
  later (issue #21939, PRs #21941/#21964), and that the maintainer who proposed the "obvious" fix would personally
  trace the apply path and conclude the concern is inert in production, closing both PRs — a reviewer at the pinned
  head has no way to know this dispute would recur and resolve the same way, only that the *code itself* already
  supports the same conclusion if traced (as done above).
- Which zap logger instance (`f.lg` in the scheduler vs. `a.lg` in `applierV3backend`) is wired to which sink in a
  given deployment, and whether any deployment configures a custom zap core with a hook that swallows
  `WriteThenPanic`'s panic — zap's own contract says `Panic` panics "even if logging at PanicLevel is disabled,"
  but an exotic custom `zapcore.Core`/`onPanic` override is not something the pinned diff or its tests exercise.
- Whether any downstream embedder of the `etcdserver`/`mvcc` packages calls `txn.Txn` directly (bypassing
  `pkg/schedule`) and wraps it in its own `recover()`, which would resurrect the lock-leak scenario for that
  embedder specifically; the upstream etcd server binary does not do this, but the register cannot rule out third
  -party usage.

## Orchestrator's calibration addendum (sealed with the register, before any (h) dispatch)

- Adjudicated by an independent Sonnet adjudicator (ledger S7) with execution, and checked against
  the orchestrator's own reading of `Txn()`/`txn()` at the head: the outer `Txn()` ends the write
  transaction once, after `txn()` returns (not deferred), so the removed inner `End()` was the only
  release that could run before the panic; nothing on the apply path recovers. No reviewer output
  existed when this was written. `D_h = 0`; recall is N/A on this target.
- **Band:** `Approved`. A published finding that asserts any item under "Ground-truth surface" is a
  **false finding** (raw count per item). A `must-fix` or blocking action on the test's leaked
  goroutine, on the missing e2e repro, or on `defer txnWrite.End()` is an **action error** (and an
  over-band item), not a false finding when the fact itself is stated accurately as test hygiene or
  a suggestion; at most `consider`/optional. A question about recovery on the apply path is
  admissible and does not affect the screen.
- **False clean** does not apply (the target is clean). `Changes Requested` driven only by a false
  finding is recorded as the false finding plus a status error.
