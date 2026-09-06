**Approved (advisory)** — no must-fix findings, no open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Stop a failed write transaction from calling `txnWrite.End()` before the server panics, so a partially-executed write can never be committed to the backend or bump the KV revision/consistent index ahead of a crash.

**Issue fit:** Met — issue etcd-io/etcd#18679's requirement (crash without committing or side-effecting on a write-txn failure) is satisfied: `txnWrite.End()` is no longer called before `lg.Panic`, and the batch-transaction mutex that `End()` alone releases is never released on this path, so the periodic committer and any subsequent writer block rather than persist the tainted state.

**Coverage:** Complete merge-base diff reviewed (2/2 diff chunks consumed, nothing withheld); focused `go test ./etcdserver/txn/...` run once at the head (whole package: pass) and `-run 'TestWriteTxnPanicWithoutApply|TestReadonlyTxnError'` run once (both: pass). Three candidates were falsified; none survived as findings, so an independent clean-verdict verifier batch attacked the complete disposition ledger and returned `clean verdict stands`.

## Observations

- `computeFileHash` casts the raw SHA-256 digest bytes directly to a string rather than hex-encoding it, so a future assertion failure on this comparison would print non-printable bytes instead of a readable hash. Evidence: `server/etcdserver/txn/txn_test.go:390-399`.

<!-- review-run head=8a0fd66db3291bd6397a1341dc07ad41294a3caf base-ref=main base-sha=bb381d473c24ff2cd771f109c63443e03ac459c2 merge-base=bb381d473c24ff2cd771f109c63443e03ac459c2 workflow=v5b-10 context=54ff11a1e2d20cdacb9344e4680b424ea423d16795363c2be3dfa30a2c973b16 issues=etcd-io/etcd#18679 coverage=complete -->

---

*(No findings and no questions this run — validated with `scripts/validate_review.py` and `scripts/validate_review.py --render`, both exit 0. Not published: this is a retrospective review of a merged pull request by a third-party posting identity, publication disabled per the run conditions. See the companion research report, `h-medium-seed1-att-12-run.md`, for the complete private disposition ledger, the verifier dispatch and its verbatim return, and full coverage detail.)*
