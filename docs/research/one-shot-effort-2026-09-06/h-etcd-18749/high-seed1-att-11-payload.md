**Approved (advisory)** — 0 must-fix findings, 0 open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Stop a failed write transaction from ending (committing) before the server panics, so a partially-applied write can never bump the KV revision or persist to the backend before the crash removes the node from service.

**Issue fit:** Met — etcd-io/etcd#18679's acceptance requirement (crash without committing a failed write txn) is satisfied by removing the pre-panic `txnWrite.End()` call; the renamed `TestWriteTxnPanicWithoutApply` asserts both the panic and an unchanged backend-file hash.

**Coverage:** Complete merge-base diff reviewed (2/2 files, 2/2 diff chunks); risk-directed checks on the write-txn lock/consistency path and the standalone Put/DeleteRange apply paths both settled with no consequence; focused `go test ./etcdserver/txn/... -run TestWriteTxnPanicWithoutApply` run once at the head: pass; `go test ./etcdserver/txn/...` (whole changed package) run once: pass.

**Reviewed:** `8a0fd66db3291bd6397a1341dc07ad41294a3caf` against merge-base `bb381d473c24ff2cd771f109c63443e03ac459c2`.

<!-- review-run head=8a0fd66db3291bd6397a1341dc07ad41294a3caf base-ref=main base-sha=bb381d473c24ff2cd771f109c63443e03ac459c2 merge-base=bb381d473c24ff2cd771f109c63443e03ac459c2 workflow=v5b-10 context=14f8b1a52f049875a1427f65019f2ec00a6d0f35b8a43fe9e37574a47c1a8146 issues=etcd-io/etcd#18679 coverage=complete -->
