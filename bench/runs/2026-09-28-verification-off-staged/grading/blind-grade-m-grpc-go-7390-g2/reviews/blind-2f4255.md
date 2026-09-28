# Review blind-2f4255

### Item 1
Location: clientconn.go:986-996
Claim: Release ac.mu before spawning the reconnect goroutine in updateAddrs. updateAddrs takes the branch where an active transport exists and the addresses changed: it defers ac.transport.GracefulClose(), sets ac.transport = nil, then calls go ac.resetTransportAndUnlock() without unlocking ac.mu first.
Consequence: When updateAddrs returns, the deferred GracefulClose() runs on the same goroutine and its onClose closure calls ac.mu.Lock(); since ac.mu is still held, only handed to the freshly spawned goroutine, that call now blocks until the new goroutine's setup runs and releases it — a wait base code never had, since it unlocked before spawning.
Fix: Call ac.mu.Unlock() before go ac.resetTransportAndUnlock() in updateAddrs; unlike connect()'s Idle check, this branch never runs when ac.state is Idle, so releasing the lock here does not reopen the race this change fixes.
