**Approved (advisory)** — 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Stop a failed write transaction from calling `txnWrite.End()` before the server panics, so a partially-applied write can no longer bump the KV revision/consistency index or get committed to the backend ahead of the crash (issue #18679).

**Issue fit:** Met — the fix removes the premature `txnWrite.End()` call on the write-failure path and the new `TestWriteTxnPanicWithoutApply` test verifies both the panic and that the backend's on-disk hash is unchanged; tracing `storeTxnWrite.End()`/`batchTx.Unlock()` confirms the removed call is exactly what would have bumped `s.currentRev` and allowed a periodic commit to persist the partial write.

**Coverage:** Complete merge-base diff reviewed (2/2 chunks); focused test `go test ./etcdserver/txn/... -run TestWriteTxnPanicWithoutApply -v -count=1` run once at the head: pass; full package `go test ./etcdserver/txn/...` run once at the head: pass.

**Reviewed:** `8a0fd66db` against merge-base `bb381d473`.

## Findings

- [P3] [consider] Close the leaked test backend after the panic assertion — anchor [`server/etcdserver/txn/txn_test.go:343`](https://github.com/etcd-io/etcd/blob/8a0fd66db3291bd6397a1341dc07ad41294a3caf/server/etcdserver/txn/txn_test.go?plain=1#L343)

<!-- review-run head=8a0fd66db3291bd6397a1341dc07ad41294a3caf base-ref=main base-sha=bb381d473c24ff2cd771f109c63443e03ac459c2 merge-base=bb381d473c24ff2cd771f109c63443e03ac459c2 workflow=v5b-10 context=b426a180c6d5eedfb74e651cbfe245a3ebe02b34253886d3f1b4edb4fe43f7a8 issues=etcd-io/etcd#18679 coverage=complete -->

---

### Finding detail

**[P3] [consider] Close the leaked test backend after the panic assertion**

**Triggers when:** `TestWriteTxnPanicWithoutApply` runs; the panic inside `Txn` leaves the backend's shared `batchTx` mutex locked, because `txn.go` no longer calls `txnWrite.End()` on the write-failure path.

**Impact:** The backend's periodic-commit goroutine blocks forever trying to reacquire that mutex, and the `bePath` bbolt file descriptor stays open for the rest of the test binary's life. Every other `betesting.NewDefaultTmpBackend` call in this file pairs it with `betesting.Close` or a `t.Cleanup`; this one has neither.

**Change:** Add a `t.Cleanup`/`defer` that closes `b`, or, if closing here would itself hang because the `batchTx` stays locked, add a short comment stating cleanup is intentionally skipped so the leak is a documented decision instead of a silent gap.

Closing this without action is a correct response.

<!-- finding id=txn/panic-test-backend-leak head=8a0fd66db3291bd6397a1341dc07ad41294a3caf priority=P3 action=consider blocking=false kind=maintainability -->
