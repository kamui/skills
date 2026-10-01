**Approved (advisory)** — 0 must-fix findings, 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Prevent concurrent `addrConn` connection attempts by having `connect()` and `updateAddrs()` keep holding `ac.mu` across the state check and into the renamed `resetTransportAndUnlock`, instead of releasing and letting it re-acquire the lock, closing the window that let the same address be dialed twice and orphan a transport (fixes grpc/grpc-go#7365, the `Test/AuthorityRevive` flake).

**Issue fit:** Met — the lock is now held continuously from the Idle/state check through the transition to Connecting in both callers, closing the race window the issue's root-cause analysis identified; the PR author verified 100000 local runs without a repeat of the flake, and this run's own 25x `-race` run of `Test/AuthorityRevive` and a full `-race` run of the `grpc` package and the `test` package's `TestSubConnEmpty` (which exercises the same reconnect-with-live-transport path) all pass cleanly.

**Coverage:** Complete merge-base diff (clientconn.go, +6/-7, 3 hunks) reviewed with full function context; both call sites of the renamed function, the lock-handoff into a spawned goroutine, and the `GracefulClose`/`onClose` interaction were traced against base and head; no other repository-tracked guidance file applies.

**Reviewed:** `76ef33f4` against merge-base `daab5634`.

## Findings

- [P3] [consider] Correct the resetTransportAndUnlock doc comment's "unconditionally" claim — anchor [`clientconn.go:1231-1233`](https://github.com/grpc/grpc-go/blob/76ef33f44a600c3ed1a385979fd1dfbcade3fbb6/clientconn.go?plain=1#L1231-L1233)

<!-- review-run head=76ef33f44a600c3ed1a385979fd1dfbcade3fbb6 base-ref=master base-sha=daab56344e612097fd50c46c433de5d9b6013837 merge-base=daab56344e612097fd50c46c433de5d9b6013837 workflow=v5b-1 context=54df6e3e94181396829de01409ee9a3ed8294ea2b0d64049f75e9d2ee9abb4f0 issues=grpc/grpc-go#7365 coverage=complete -->

---

### Finding comment — inline on `clientconn.go:1231-1233` (`RIGHT`)

**[P3] [consider] Correct the resetTransportAndUnlock doc comment's "unconditionally" claim**

**Triggers when:** A reader (human or agent) relies on the doc comment for `resetTransportAndUnlock` without re-deriving its body, in particular for a call where `ac.ctx` is already canceled when the function runs (for example, a concurrent `ClientConn` teardown).

**Impact:** The comment states the function "unconditionally connects the addrConn," but the function's first lines return immediately — unlocking `ac.mu` without attempting any connection — whenever `acCtx.Err() != nil`. A maintainer trusting the comment's wording could assume every call performs a connection attempt and misjudge backoff or lock-handoff reasoning that depends on that assumption.

**Change:** In `clientconn.go`, reword the comment to state the early-return case, e.g. "connects the addrConn unless its context has already been canceled, in which case it unlocks and returns without connecting."

Closing this without action is a correct response.

<!-- finding id=clientconn/reset-transport-and-unlock-doc-comment head=76ef33f44a600c3ed1a385979fd1dfbcade3fbb6 priority=P3 action=consider blocking=false kind=maintainability -->
