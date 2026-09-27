# Scorecard: m-grpc-go-7390, mapping v1

Register v1 (5a40b59e0c38), rubric v1, scored at 2026-09-27T07:10:57Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 9bdfe4aace399434bbb4ef6106c9d60457ecf9971cd6793d64555e68f843b78a; session 4eb3e724-bfb7-4a08-b9c5-23582be34707; read audit clean.

## att-003 (review-code-sonnet-high), blind-e6e6d8

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "the same goroutine's deferred `ac.transport.GracefulClose()` (clientconn.go:986) now runs while ac.mu is still held ... this path now briefly blocks on the spawned goroutine's own unlock instead of running lock-free" and "verified non-deadlocking (premise-2, ruling `holds`)". The fact is accurate: the diff removes `ac.mu.Unlock()` before `go ac.resetTransportAndUnlock()` in updateAddrs, so the deferred GracefulClose (clone/clientconn.go:985-986) runs with ac.mu held by the handed-off lock; http2Client.GracefulClose calls t.onClose synchronously (internal/transport/http2_client.go:1045-1056), and onClose does ac.mu.Lock() (clientconn.go:1351). Since ac.cancel() was already called, onClose just adjusts params and returns once the spawned goroutine releases ac.mu, which resetTransportAndUnlock does before tryAllAddrs on every path without touching the old transport. The item itself concludes it is non-deadlocking and proposes no fix; it is a correct observation of brief extra blocking, in line with the register's non-defect on the extended critical section. Below the finding threshold.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "The new private contract on resetTransportAndUnlock, that ac.mu is held by the caller on entry, is enforced only by its doc comment and Go's unlock-of-an-unlocked-mutex panic, not by a code-level check; reviewers explicitly discussed and declined adding one." Accurate (clientconn.go:1231-1234 doc comment; packet review threads 10-17), but this is exactly register non_defect #2: a design/extensibility concern that was disclosed and accepted, with both call sites audited correct. No defect or fix asserted; non-material observation.

## New candidates

None.
