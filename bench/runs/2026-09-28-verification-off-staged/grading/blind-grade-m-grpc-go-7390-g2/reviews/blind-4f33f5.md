# Review blind-4f33f5

### Item 1
Location: (no file)
Claim: updateAddrs's `go ac.resetTransportAndUnlock()` now launches while ac.mu is still locked, and the function's own deferred `ac.transport.GracefulClose()` runs immediately afterward in the same goroutine, synchronously blocking on `ac.mu.Lock()` inside `onClose` until the spawned goroutine releases it — unlike the prior explicit-unlock-then-go order, and unlike tearDown's still-explicit unlock-before-GracefulClose pattern a few hundred lines below; this briefly serializes the two goroutines but a mandatory verification pass confirmed no cyclic wait exists (updateConnectivityState dispatches to the balancer asynchronously via the callback serializer), so it is not a hang.
Consequence: clientconn.go:977-996, clientconn.go:1573-1575, verification premise-2-no-lock-cycle-on-handoff (holds)
Fix: —
