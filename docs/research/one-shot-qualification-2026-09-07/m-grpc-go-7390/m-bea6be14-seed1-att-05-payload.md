**Approved** — 0 findings, 0 open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Close a race in `addrConn.connect`/`addrConn.updateAddrs` where releasing `ac.mu` before `resetTransport()` re-acquired it let two concurrent connection attempts both observe `Idle` and both dial, orphaning one of the two resulting transports (grpc/grpc-go#7365).

**Issue fit:** Met — callers of the renamed `resetTransportAndUnlock` now hold `ac.mu` across the idle/ready check and the transition to `Connecting`, closing the window the issue's root-cause analysis describes. The PR's "Test/AuthorityRevive no longer flakes for 100000 attempts" claim is a supporting assertion, not independently reproduced at that scale; it was spot-checked at 30 `-race` iterations (pass) instead.

**Coverage:** Complete merge-base diff reviewed (`clientconn.go`, +6/-7, 1/1 diff chunks, nothing withheld). No test function was added or substantively changed by this diff, so the rubric's Changed-tests section has no scope here. Two pre-existing tests were run once each, offline, as candidate verification (not required by Changed tests): `Test/SubConnEmpty` (`./test/`, pass, ~0.01s, confirms no self-deadlock on the live-transport `GracefulClose` path) and `Test/AuthorityRevive` (`./xds/internal/xdsclient/tests/`, `-race -count=30`, pass, 5.9s).

**Reviewed:** `76ef33f4` against merge-base `daab5634`.

<!-- review-run head=76ef33f44a600c3ed1a385979fd1dfbcade3fbb6 base-ref=master base-sha=daab56344e612097fd50c46c433de5d9b6013837 merge-base=daab56344e612097fd50c46c433de5d9b6013837 workflow=v5b-10 context=54df6e3e94181396829de01409ee9a3ed8294ea2b0d64049f75e9d2ee9abb4f0 issues=grpc/grpc-go#7365 coverage=complete -->
