# Review blind-280b8f

### Item 1
Location: (no file)
Claim: updateAddrs() spawns `go ac.resetTransportAndUnlock()` while still holding ac.mu, so the mutex stays continuously locked across a goroutine handoff until the new goroutine reaches its first Unlock() — an unusual pattern reviewers (purnesh42H, dfawley) explicitly discussed and accepted via the function's name and doc comment rather than a compile- or runtime-enforced check.
Consequence: clientconn.go:940-996 and :1234-1262; review thread comments at clientconn.go:1231 dated 2024-07-08T19:42:18Z through 2024-07-09T20:26:47Z, ending with dfawley concluding that the function's name and doc comment were sufficient documentation of the locking contract.
Fix: —

### Item 2
Location: (no file)
Claim: resetTransportAndUnlock's early `acCtx.Err() != nil` return skips the connectivity.Connecting transition entirely; this pre-existing behavior (unchanged by this diff beyond the lock removal) was raised and explicitly dismissed by reviewers as immaterial.
Consequence: clientconn.go:1234-1238; review thread comment at clientconn.go:923 dated 2024-07-08T11:45:38Z: 'Discussed offline: it doesn't matter if resetTransport() returns error after state being updated to connecting.'
Fix: —
