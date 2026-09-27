# Scorecard: m-grpc-go-7390, mapping v1

Register v1 (5a40b59e0c38), rubric v1, scored at 2026-09-27T12:14:37Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 87bacc3616168f863cdbbe34b6fdf32992942477ee1ea7882bc134486b1b0c31; session 20d536fa-ca93-4736-9448-e7f1e0553d5d; read audit clean.

## att-005 (review-code-sonnet-high-isolated-lifecycle), blind-61d263

Verdict 'Changes Requested'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `false-finding`, fix n/a, priority error n/a, group none. Quote: "it is a genuine, previously nonexistent synchronization dependency on the shared address-update path" and Fix: "Before updateAddrs returns, unlock ac.mu explicitly (as at the merge-base) ... have the spawned reconnect goroutine acquire ac.mu itself at entry instead of assuming the caller's lock carries over". The underlying fact (deferred GracefulClose -> onClose -> ac.mu.Lock at clientconn.go:985-987/1351 waits for the handed-off lock) is true. By the item's own account the wait is bounded, and there is no deadlock: the lock is held via the handoff, not by the same goroutine. So the tearDown comment at clientconn.go:1573-1575 about self-held locks does not apply. The "previously nonexistent" framing is also overstated: at the merge-base, resetTransport re-acquired ac.mu at entry, so the deferred onClose could already contend with it. The register rules both the lock handoff across `go ac.resetTransportAndUnlock()` and the extended critical section/contention as non-defects. Its clean_basis names the handoff as the surface a correct review must not assert as a defect. This item asserts exactly that as a defect needing a fix. The proposed fix, unlocking before the spawn and re-acquiring in the goroutine, is the pre-image. It would reopen the race window the PR closes (issue #7365, concurrent connection attempts and orphaned connections). The asserted material defect is not supported.

## att-006 (review-code-sonnet-high-isolated-lifecycle), blind-560dbe

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "the goroutine running updateAddrs briefly blocks inside GracefulClose's synchronous onClose callback until that unlock; the verified safety premise found no cyclic dependency, so this is added lock contention, not a defect." Fix: "—". The code confirms it: the deferred GracefulClose (clientconn.go:985-987) runs after the handoff at 996. onClose locks ac.mu (1351), and resetTransportAndUnlock unlocks after cheap bookkeeping (1231-1261). The item says outright that this is not a defect. That matches the register non-defect: "Extending the critical section ... increases lock contention ... disclosed, intended effect". This is an accurate, inconsequential observation.

## att-007 (review-code-sonnet-high-isolated-lifecycle), blind-4de5e9

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "its synchronous `onClose` callback (clientconn.go:1351-1353) can briefly block on `ac.mu.Lock()` until that goroutine reaches its own unlock — a latency change from the prior code, not a deadlock"; Fix: "—". The fact holds at head: updateAddrs defers ac.transport.GracefulClose() (clientconn.go:985-987) and then calls `go ac.resetTransportAndUnlock()` (996) with ac.mu held. GracefulClose calls t.onClose synchronously (internal/transport/http2_client.go:1051-1055), and onClose does ac.mu.Lock() (clientconn.go:1351). resetTransportAndUnlock releases ac.mu after bookkeeping only (clientconn.go:1231-1261), so any wait is bounded. The item itself says this is not a deadlock and proposes no change. It matches the register non-defect that extending the critical section adds contention by design. This is an accurate observation below the finding threshold.

## att-008 (review-code-sonnet-high-isolated-control), blind-2b6a43

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

(no items)

## New candidates

None.
