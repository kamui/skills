**Approved (advisory)** — 0 must-fix findings, 0 open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Hold `ac.mu` for the full state-check-to-`Connecting` transition around `resetTransport` (renamed `resetTransportAndUnlock`) so two racing `connect()`/`updateAddrs()` calls cannot both observe `Idle` and start parallel connection attempts, fixing the flaky `Test/AuthorityRevive`.

**Issue fit:** Met — the lock is now held continuously from the `Idle`/state check in `connect()` and `updateAddrs()` through the `Connecting` transition inside `resetTransportAndUnlock`, closing exactly the window issue #7365 root-caused; `resetTransportAndUnlock`'s locking contract is documented as reviewers requested.

**Coverage:** Complete merge-base diff reviewed (`clientconn.go`, +6/-7, the only changed file); both call sites of the renamed function and its every lock/unlock path traced at head and merge-base; `CONTRIBUTING.md` inspected (no applicable rule). `go build ./...`, `go vet ./...`, `go test -race .` (root package), and `go test -race -count=30 -run 'Test/AuthorityRevive$' ./xds/internal/xdsclient/tests/...` all pass.

**Reviewed:** `76ef33f44a600c3ed1a385979fd1dfbcade3fbb6` against merge-base `daab56344e612097fd50c46c433de5d9b6013837`.

<!-- review-run head=76ef33f44a600c3ed1a385979fd1dfbcade3fbb6 base-ref=master base-sha=daab56344e612097fd50c46c433de5d9b6013837 merge-base=daab56344e612097fd50c46c433de5d9b6013837 workflow=v5b-1 context=9157346dcb3de279261074223f827a5cfc7088691f1c9b3e28d020f3d70bca25 issues=grpc/grpc-go#7365 coverage=complete -->
