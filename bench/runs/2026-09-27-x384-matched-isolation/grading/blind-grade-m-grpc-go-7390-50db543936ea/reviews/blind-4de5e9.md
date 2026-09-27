# Review blind-4de5e9

### Item 1
Location: (no file)
Claim: The deferred `ac.transport.GracefulClose()` in `updateAddrs()` (clientconn.go:986) now runs while `ac.mu` is still logically held (ownership transferred to the goroutine spawned at clientconn.go:996), so its synchronous `onClose` callback (clientconn.go:1351-1353) can briefly block on `ac.mu.Lock()` until that goroutine reaches its own unlock — a latency change from the prior code, not a deadlock (confirmed by verified premise-3).
Consequence: clientconn.go:983-996; clientconn.go:1351-1353; internal/transport/http2_client.go:1045-1058
Fix: —
