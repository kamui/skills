# Scorecard: m-grpc-go-7390, mapping v1

Register v1 (5a40b59e0c38), rubric v1, scored at 2026-09-28T06:33:27Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 5aedc1f8a0065d3a77ebe7479d7b2b2e2bddcb11d1fa1369263b86cbb5e06e3a; session e67beb37-ee1a-4305-90a8-3d2c30a1ef85; read audit clean.

## att-001 (review-code-sonnet-high-enforced-x394-control), blind-59b24b

Verdict 'Changes Requested'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `false-finding`, fix n/a, priority error n/a, group none. Quote: "Don't defer GracefulClose while ac.mu is still held by the spawned goroutine ... blocking that goroutine, which is the balancer's single CallbackSerializer, until the just-spawned resetTransportAndUnlock goroutine happens to reach its own Unlock(). It only avoids a hard deadlock today because resetTransportAndUnlock's prefix has no other blocking call." The mechanics are accurate (clone/clientconn.go:983-996 defers ac.transport.GracefulClose(); http2_client.go:1055 calls t.onClose inline; onClose locks ac.mu at clientconn.go:1351). But the item asserts this as a defect needing a fix, and the consequence does not hold up. The review itself concedes there is no deadlock. The wait is bounded by resetTransportAndUnlock's prefix (clientconn.go:1235-1262): reading ac.ctx/addrs, bs.Backoff, minConnectTimeout, and updateConnectivityState. That last call goes through acbw.updateState -> serializer.Schedule (balancer_wrapper.go:256; callback_serializer.go:64-65, an unbounded buffer Put), so it never blocks on the serializer the caller is running on. The head also doesn't create the contention: at the pre-image, `go ac.resetTransport()` immediately re-acquired ac.mu (resetTransport began with ac.mu.Lock()) and raced the same deferred GracefulClose->onClose for it. The register rules this surface out as a defect: non_defects cover handing the locked mutex across the `go` boundary and the lengthened critical section ("The lock covers only cheap state bookkeeping and is released before tryAllAddrs in every path"), and clean_basis names this handoff as the surface a correct review must not assert as a defect. The "latent future deadlock" argument is speculative, and preexisting_hints record that the team discussed the risk and accepted it. No material consequence is supported.

## att-002 (review-code-sonnet-high-enforced-verification-off), blind-a899ce

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "that deferred call ... now blocks until the spawned `go ac.resetTransportAndUnlock()` goroutine reaches its own unlock ... this is a behavior tightening, not a defect." This is accurate: the deferred GracefulClose at clientconn.go:985-987 triggers onClose, which locks ac.mu (clientconn.go:1351), and ac.mu is held until resetTransportAndUnlock unlocks at clientconn.go:1262. The item explicitly declines to call it a defect, which matches the register's non-defect on the extended critical section. It is a correct observation below the finding threshold.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "Commit 6214c9dd1's message, 'Make callers of resetBackoff() lock the mutex,' misdescribes its own diff, which touches connect(), updateAddrs() and resetTransport()/resetTransportAndUnlock(), not resetBackoff()." Verified with git show 6214c9dd1: the diff renames resetTransport to resetTransportAndUnlock and updates the call sites in connect() and updateAddrs(). It does not touch resetBackoff. The claim is true, but a commit message has no effect on code behavior (the PR was squash-merged), so this is hygiene only.

## New candidates

None.
