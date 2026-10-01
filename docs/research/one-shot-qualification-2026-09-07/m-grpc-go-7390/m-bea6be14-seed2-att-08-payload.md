**Approved (advisory)** — 0 must-fix findings, 0 open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Hold `ac.mu` across the call into the renamed `resetTransportAndUnlock` from both of its callers, `addrConn.connect()` and `addrConn.updateAddrs()`, instead of releasing the mutex and letting the callee re-acquire it, so no concurrent caller can observe the pre-connect `Idle` state and start a second connection attempt.

**Issue fit:** Met — issue #7365's root cause (two `tryAllAddrs` attempts because the old `resetTransport` only set `Connecting` after re-acquiring a lock its caller had briefly released) is closed by holding the lock continuously from the state check into the state update in both callers; the pull-request body's promise that "no concurrent requests are able to start" and the release note's claim of fixing "a race that could lead to orphaned connections" are met by the same evidence (`clientconn.go:914-922`, `clientconn.go:990-996`, `clientconn.go:1234-1262`). The pull request's own supporting claim of running the regression test for 100000 attempts without a flake is not independently reproducible within this review's offline execution budget and is recorded as not-verifiable rather than confirmed; it is not contradicted by the runs performed here.

**Coverage:** Complete merge-base diff reviewed (`clientconn.go`, +6/−7, one chunk, no gaps). No test file is part of this diff, so the rubric's Changed-tests section does not apply; two existing tests that already exercise the changed lock-handoff paths were each run once, offline, under the race detector: `go test ./test/ -run 'Test/SubConnEmpty' -race` (pass) and `go test ./xds/internal/xdsclient/tests/ -run 'Test/AuthorityRevive$' -race -count=300` (pass, 300/300). `go build ./...` also succeeds at the reviewed head.

**Reviewed:** `76ef33f44a600c3ed1a385979fd1dfbcade3fbb6` against merge-base `daab56344e612097fd50c46c433de5d9b6013837`.

## Observations

- Holding `ac.mu` across the `go ac.resetTransportAndUnlock()` spawn in `updateAddrs` leaves that function's own deferred `ac.transport.GracefulClose()` cleanup blocked until the spawned goroutine releases the lock, a handoff that `tearDown` avoids in the same file by unlocking explicitly before calling `GracefulClose`. Evidence: `clientconn.go:983-996`, `clientconn.go:1571-1583`.

<!-- review-run head=76ef33f44a600c3ed1a385979fd1dfbcade3fbb6 base-ref=master base-sha=daab56344e612097fd50c46c433de5d9b6013837 merge-base=daab56344e612097fd50c46c433de5d9b6013837 workflow=v5b-10 context=f0155084ea615627d1b844b4677bc814d2838e1cc2d664afaa658b3c115356dd issues=grpc/grpc-go#7365 coverage=complete -->
