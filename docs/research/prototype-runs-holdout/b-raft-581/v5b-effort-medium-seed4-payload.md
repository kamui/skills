**Approved (advisory)** — 0 must-fix findings, 0 open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** After sending `TimeoutNow` during a leadership transfer, the old leader used to accept writes again as soon as the RPC was confirmed sent, even though the new leader had not yet won its election; those writes could make the target lose the election it was being handed. The fix waits for up to `ElectionTimeout` after a successfully-sent `TimeoutNow`, keeping writes blocked until either the node observably steps down or the timeout elapses.

**Issue fit:** Not applicable — no originating issue; `issues=none`. The PR body is the only statement of intent, and the implementation matches it: the `leadershipTransferInProgress` write-gate (unchanged call sites at `raft.go:645,826,836,846,859`) is held until the new nested wait in the leadership-transfer goroutine resolves.

**Coverage:** Complete merge-base diff reviewed (`raft.go`, `raft_test.go`, `testing.go`; deletion-only and generated files: none present). Risk-directed concurrency/failover check performed on the leader loop's leadership-transfer goroutine, including a zero-survivor clean-verdict independent-verifier pass over three raised-and-dropped candidates (two stacked-timeout/race concerns and one re-opened-then-re-falsified error-text concern); all three remain non-findings after verification. No security, authorization, migration, or serialization surface is touched by this change. Static review only; no build, test, or lint was executed (offline, no-network run).

**Reviewed:** `cb62297` against merge-base `1462fd5`.

<!-- review-run head=cb622973cd2c65dd2752c49d0520f2a3894b2d91 base-ref=main base-sha=1462fd5e80ad0eb38748f68198505025cb2c96d8 merge-base=1462fd5e80ad0eb38748f68198505025cb2c96d8 workflow=v5b-1 context=37d14eccc44122fa6e45d8e0705b3ce1ee67ab02fca7e96c277696da01d4da90 issues=none coverage=complete -->
