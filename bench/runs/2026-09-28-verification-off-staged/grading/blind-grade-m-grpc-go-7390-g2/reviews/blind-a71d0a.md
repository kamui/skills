# Review blind-a71d0a

### Item 1
Location: (no file)
Claim: Removing the explicit ac.mu.Unlock() in updateAddrs before its deferred ac.transport.GracefulClose() means that deferred call (when ac.transport != nil) now blocks until the spawned `go ac.resetTransportAndUnlock()` goroutine reaches its own unlock, serializing the old transport's close against the new Connecting-state transition instead of letting them race; the full -race suite passed with no hang, so this is a behavior tightening, not a defect.
Consequence: clientconn.go:983-996, clientconn.go:1234-1262; reviewer-executed `go test -race -v .` (152/152 passed).
Fix: —

### Item 2
Location: (no file)
Claim: Commit 6214c9dd1's message, "Make callers of resetBackoff() lock the mutex," misdescribes its own diff, which touches connect(), updateAddrs() and resetTransport()/resetTransportAndUnlock(), not resetBackoff().
Consequence: git show 6214c9dd1cd421727852b03cafceac7c9e9eb973 (commit message vs. diff body).
Fix: —
