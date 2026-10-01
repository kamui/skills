**Approved (advisory)** — 0 must-fix findings, 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Stop a failed write transaction from calling `txnWrite.End()` before panicking, so a partially-applied write can never be unlocked, revision-bumped, or backend-committed ahead of the crash.

**Issue fit:** Met — etcd-io/etcd#18679 asked that a node on which a write txn fails crash without committing the partial write or bumping the KV revision/consistency index; the diff removes the `txnWrite.End()` call that ran before `lg.Panic`, and tracing the backend's locking (`server/storage/backend/batch_tx.go`, `server/storage/mvcc/kvstore_txn.go`) shows the batchTx mutex now stays held until the process exits, so neither the periodic committer nor the read-buffer writeback that `End()` used to trigger can run before the crash.

**Coverage:** Complete merge-base diff reviewed (2 files, both fully diffed with function context); risk-led check of the write-apply call path for a panic-recovery wrapper (none found) and of every other `.Panic(` site in `server/etcdserver` for the same end-before-panic pattern (none found); focused `go test ./etcdserver/txn/... -run TestWriteTxnPanicWithoutApply -v` run once at the reviewed head: pass (0.04s).

**Reviewed:** `8a0fd66db3291bd6397a1341dc07ad41294a3caf` against merge-base `bb381d473c24ff2cd771f109c63443e03ac459c2`.

## Findings

- [P3] [consider] Close the backend explicitly in TestWriteTxnPanicWithoutApply — anchor [`server/etcdserver/txn/txn_test.go:343-345`](https://github.com/etcd-io/etcd/blob/8a0fd66db3291bd6397a1341dc07ad41294a3caf/server/etcdserver/txn/txn_test.go?plain=1#L343-L345); fix [`server/etcdserver/txn/txn_test.go:343`](https://github.com/etcd-io/etcd/blob/8a0fd66db3291bd6397a1341dc07ad41294a3caf/server/etcdserver/txn/txn_test.go?plain=1#L343)

## Observations

- The new invariant comment contains a typo, "aply" for "apply". Evidence: `server/etcdserver/txn/txn_test.go:377`.
- `computeFileHash` returns the raw digest bytes cast to a string rather than a hex-encoded string, so a failed comparison would print unescaped binary instead of a readable hash. Evidence: `server/etcdserver/txn/txn_test.go:592`.

<!-- review-run head=8a0fd66db3291bd6397a1341dc07ad41294a3caf base-ref=main base-sha=bb381d473c24ff2cd771f109c63443e03ac459c2 merge-base=bb381d473c24ff2cd771f109c63443e03ac459c2 workflow=v5b-10 context=b426a180c6d5eedfb74e651cbfe245a3ebe02b34253886d3f1b4edb4fe43f7a8 issues=etcd-io/etcd#18679 coverage=complete -->

---

## Inline comments (as they would post on the reviewed head)

### Comment 1 — `server/etcdserver/txn/txn_test.go:343-345` (side: RIGHT)

**[P3] [consider] Close the backend explicitly in TestWriteTxnPanicWithoutApply**

**Triggers when:** Any run of `TestWriteTxnPanicWithoutApply`, the only test in this file that never calls `betesting.Close`.

**Impact:** The backend's periodic-commit goroutine (`go b.run()` in `server/storage/backend/backend.go`) and its open bbolt file handle are never stopped by this test; they stay live until the whole package's test binary exits, instead of being released when the test function returns like the immediately preceding `TestReadonlyTxnError`.

**Change:** In `server/etcdserver/txn/txn_test.go`, add `defer betesting.Close(t, b)` right after `b, bePath := betesting.NewDefaultTmpBackend(t)`, matching `TestReadonlyTxnError` above it.

Closing this without action is a correct response.

<!-- finding id=etcd-txn-test-backend-close head=8a0fd66db3291bd6397a1341dc07ad41294a3caf priority=P3 action=consider blocking=false kind=maintainability fix=server/etcdserver/txn/txn_test.go:343 -->
