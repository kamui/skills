# Scorecard: m-grpc-go-7390, mapping v2

Register v1 (5a40b59e0c38), rubric v1, scored at 2026-09-28T13:04:41Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 e7f9f5f897af9c77dc1225d2ed54dc0bf37b4a8784d7fbc9566346d0c11ac0aa; session 02ef4124-4539-4323-9fa2-615fd77e15df; read audit clean.

## att-001 (review-code-sonnet-high-enforced-x394-control), blind-6590e8

Verdict 'Changes Requested'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error True, group none. Quote: "the deferred GracefulClose() still fires synchronously in the *caller's* goroutine ... onClose's first statement is ac.mu.Lock() (clientconn.go:1351) — blocking that goroutine ... until the just-spawned resetTransportAndUnlock goroutine happens to reach its own Unlock(). It only avoids a hard deadlock today because resetTransportAndUnlock's prefix has no other blocking call". The facts check out: GracefulClose calls t.onClose inline (internal/transport/http2_client.go:1055), and the spawned goroutine holds ac.mu only through non-blocking bookkeeping and updateConnectivityState before unlocking (clientconn.go:1235-1262). The item itself concedes there is no deadlock. The stated consequence is a bounded wait of the caller behind cheap bookkeeping, plus a hypothetical future fragility. The register rules both of these are not defects: handing the locked mutex to the goroutine is intended, and the extended critical section and its serialization are the PR's disclosed purpose. The proposed `go t.GracefulClose()` is a harmless hardening. Since the consequence is not fabricated but is below the materiality threshold, this is non-material rather than a false finding.

## att-002 (review-code-sonnet-high-enforced-verification-off), blind-a71d0a

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "that deferred call (when ac.transport != nil) now blocks until the spawned `go ac.resetTransportAndUnlock()` goroutine reaches its own unlock ... this is a behavior tightening, not a defect." This is accurate (clientconn.go:983-996, onClose at clientconn.go:1351, GracefulClose calling onClose inline at http2_client.go:1055), and the item explicitly declines to call it a defect. It matches the register's non-defect on intended serialization, so it is an observation below the threshold.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "Commit 6214c9dd1's message, 'Make callers of resetBackoff() lock the mutex,' misdescribes its own diff". This is true: `git show 6214c9dd1` changes connect(), updateAddrs() and renames resetTransport to resetTransportAndUnlock, and it does not touch resetBackoff. It is commit-message hygiene with no effect on code behavior, so it is non-material.

## att-012 (review-code-sonnet-high-enforced-verification-off), blind-baa031

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "No new test was added or changed by this diff; the fix's correctness rests on the pre-existing ... `Test/AuthorityRevive` integration test and the author's manual reruns". This is true: the diff touches only clientconn.go (packet §2). The register lists 'No new unit test was added for the concurrency fix' as a coverage-hygiene non-defect, so it is non-material.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "Commit `6214c9dd1`'s message, 'Make callers of resetBackoff() lock the mutex', does not describe its content". This is true per `git show 6214c9dd1`, which changes the connect/updateAddrs/resetTransport locking handoff and does not touch resetBackoff. It is commit-message hygiene only, so it is non-material. It makes a different claim from item 1, so there is no duplicate group.

## att-013 (review-code-sonnet-high-enforced-x394-control), blind-4f33f5

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "the function's own deferred `ac.transport.GracefulClose()` runs immediately afterward in the same goroutine, synchronously blocking on `ac.mu.Lock()` inside `onClose` until the spawned goroutine releases it ... this briefly serializes the two goroutines but ... no cyclic wait exists ... so it is not a hang." Accurate: GracefulClose calls onClose inline (http2_client.go:1055), onClose locks ac.mu (clientconn.go:1351), and the spawned goroutine releases it after cheap bookkeeping (clientconn.go:1261-1262). The item explicitly concludes there is no defect. This is an observation of the brief serialization the register lists as intended (non_defects on lock handoff and on the extended critical section), so it is below the finding threshold.

## att-022 (review-code-sonnet-high-enforced-x394-control), blind-f95bcf

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "No regression test was added for the fixed race itself; the author instead verified manually that Test/AuthorityRevive stopped flaking over 100000 local attempts". This is accurate per packet §2 and §3. The register lists the missing new unit test as a coverage-hygiene non-defect, so it is non-material.

## att-023 (review-code-sonnet-high-enforced-verification-off), blind-2f4255

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `false-finding`, fix n/a, priority error n/a, group none. Quote: "Release ac.mu before spawning the reconnect goroutine in updateAddrs" ... "Fix: Call ac.mu.Unlock() before go ac.resetTransportAndUnlock() in updateAddrs; unlike connect()'s Idle check, this branch never runs when ac.state is Idle, so releasing the lock here does not reopen the race this change fixes." The underlying fact is accurate: at head the deferred ac.transport.GracefulClose() (clientconn.go:983-987) runs while ac.mu is still held for the spawned goroutine. http2Client.GracefulClose calls t.onClose inline (internal/transport/http2_client.go:1055), and onClose starts with ac.mu.Lock() (clientconn.go:1351), so the caller waits briefly. The item's safety argument is wrong, though. clientconn.go:990-992 sets connectivity.Idle when len(addrs)==0 just before the spawn, so the branch can run in Idle state, and unlocking there would let a concurrent connect() see Idle and start a second resetTransport: the exact race the PR fixes. Worse, resetTransportAndUnlock (clientconn.go:1231-1265) assumes the lock is held and unlocks it unconditionally, so the prescribed Unlock-before-spawn would double-unlock (fatal 'unlock of unlocked mutex') or release another holder's lock. The only real consequence is a bounded wait, which the register rules is the disclosed, intended effect (non_defects: lock handoff across the goroutine is fine; extending the critical section is intentional). The defect it asserts is not a defect, and the support it gives is contradicted by the code.

## New candidates

None.
