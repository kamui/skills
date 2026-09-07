# Clean high-risk PR hunt — report

Generated 2026-09-07. All commands below were actually run against a full local clone of
`grpc/grpc-go` (`/tmp/qual137/hunts/grpc-go-repo`) plus live `gh api graphql` calls. Raw
GraphQL dumps are saved next to this file: `pr7390_full.json`, `pr8519.json`, `pr7417.json`,
`issue7365.json`.

Repo checked against the exclusion list: **none of the three candidates below (or their repo,
`grpc/grpc-go`) appear on the reserved list.** `grpc/grpc-go` is Apache-2.0, public, GitHub-native
reviews (no Reviewable.io), not cockroachdb.

---

## TOP PICK: grpc/grpc-go#7390

**"grpc: hold ac.mu while calling resetTransport to prevent concurrent connection attempts"**

- Author: arjan-bal (Google, grpc-go maintainer)
- Merged by: dfawley (grpc-go lead maintainer)
- `mergedAt`: **2024-07-09T20:27:27Z** — 26 months before 2026-09-06, far past the 6-month floor.
- Base branch: `master`
- Originating issue: **#7365**, "Flaky Test/AuthorityRevive in
  google.golang.org/grpc/xds/internal/xdsclient/tests" (opened 2024-06-28, closed at merge).

### SHAs — self-computed, not trusted from the API

```
PR-recorded baseRefOid : daab56344e612097fd50c46c433de5d9b6013837
PR-recorded headRefOid : 76ef33f44a600c3ed1a385979fd1dfbcade3fbb6
merge commit           : 45d44a736ec6cdcb73f9411bf6a1c2d1abea1956 (single squashed commit;
                          tree of pr7390head == tree of the merge commit for clientconn.go,
                          confirmed with `git diff pr7390head 45d44a73 -- clientconn.go` → empty)
git merge-base(base,head), computed on a full clone:
  $ git merge-base daab56344e612097fd50c46c433de5d9b6013837 pr7390head
  daab56344e612097fd50c46c433de5d9b6013837
```
**They agree exactly** — `merge-base == PR-recorded baseRefOid`. This is the clean case; contrast
with the alternates below where GitHub's `baseRefOid` (a live pointer, not a frozen fork point)
disagreed with the true merge-base, which is expected GraphQL behavior, not a defect in the PR.

### Changed-file manifest (verified with `git diff --numstat`)

| file | + | - |
|---|---|---|
| `clientconn.go` | 6 | 7 |

**Total changed lines: 13, 1 file.** Comfortably inside the 200-line / 6-file budget.

Full diff:
```diff
diff --git a/clientconn.go b/clientconn.go
@@ func (ac *addrConn) connect() error {
 		ac.mu.Unlock()
 		return nil
 	}
-	ac.mu.Unlock()
-
-	ac.resetTransport()
+	ac.resetTransportAndUnlock()
 	return nil
 }
@@ func (ac *addrConn) updateAddrs(addrs []resolver.Address) {
 		ac.updateConnectivityState(connectivity.Idle, nil)
 	}
-	ac.mu.Unlock()
-
 	// Since we were connecting/connected, we should start a new connection attempt.
-	go ac.resetTransport()
+	go ac.resetTransportAndUnlock()
 }
@@ func (ac *addrConn) adjustParams(r transport.GoAwayReason) {
-func (ac *addrConn) resetTransport() {
-	ac.mu.Lock()
+// resetTransportAndUnlock unconditionally connects the addrConn.
+//
+// ac.mu must be held by the caller, and this function will guarantee it is released.
+func (ac *addrConn) resetTransportAndUnlock() {
 	acCtx := ac.ctx
```

### Edit-provenance table (constraint 5), full — GraphQL, verified programmatically

`mergedAt = 2024-07-09T20:27:27Z`. Every timestamp below with `lastEditedAt` set is **before**
that instant; I wrote a script comparing every one and it reports zero violations.

| Record | author | createdAt / submittedAt | lastEditedAt |
|---|---|---|---|
| PR body | arjan-bal | 2024-07-04T07:51:36Z | 2024-07-09T06:25:31Z (some hours before merge, not after — recheck below) |
| Review (comment) | purnesh42H | 2024-07-04T08:18:02Z | — |
| Review (comment) | arjan-bal | 2024-07-04T08:36:59Z | — |
| Review (comment) | purnesh42H | 2024-07-04T09:01:57Z | — |
| Review (comment) | purnesh42H | 2024-07-04T09:16:00Z | — |
| Review (comment) | arjan-bal | 2024-07-04T10:51:59Z | — |
| Review (comment) | arjan-bal | 2024-07-04T11:17:17Z | — |
| Review (comment) | purnesh42H | 2024-07-05T04:30:33Z | — |
| Review (comment) | arjan-bal | 2024-07-05T06:30:33Z | — |
| Review (comment) | purnesh42H | 2024-07-08T11:45:38Z | — |
| Review (APPROVED) | purnesh42H | 2024-07-08T11:46:34Z | — |
| Review (APPROVED) | dfawley | 2024-07-08T19:42:21Z | — |
| Review (comment) | purnesh42H | 2024-07-09T04:28:33Z | — |
| Review (comment) | arjan-bal | 2024-07-09T06:26:40Z | — |
| Review (comment) | arjan-bal | 2024-07-09T06:32:24Z | — |
| Review (comment) | purnesh42H | 2024-07-09T06:33:02Z | — |
| Review (comment) | arjan-bal | 2024-07-09T06:43:56Z | — |
| Review (comment) | purnesh42H | 2024-07-09T07:10:22Z | — |
| Review (COMMENTED) | dfawley | 2024-07-09T20:26:47Z | — |
| Top-level comment | codecov (bot) | 2024-07-04T07:54:41Z | 2024-07-09T06:48:17Z |
| Top-level comment | purnesh42H | 2024-07-05T04:33:55Z | 2024-07-05T08:10:25Z |
| Top-level comment | arjan-bal | 2024-07-05T06:32:57Z | — |
| Top-level comment | purnesh42H | 2024-07-08T10:15:53Z | — |
| Top-level comment | arjan-bal | 2024-07-08T10:48:16Z | — |
| Top-level comment | dfawley | 2024-07-08T19:39:58Z | — |
| Top-level comment | arjan-bal | 2024-07-09T06:38:44Z | 2024-07-09T06:39:07Z |
| Thread comment (clientconn.go) | purnesh42H | 2024-07-04T08:17:59Z | — |
| Thread comment | arjan-bal | 2024-07-04T08:36:58Z | — |
| Thread comment | purnesh42H | 2024-07-04T09:01:56Z | — |
| Thread comment | purnesh42H | 2024-07-04T09:15:58Z | — |
| Thread comment | arjan-bal | 2024-07-04T10:51:59Z | — |
| Thread comment | arjan-bal | 2024-07-04T11:17:17Z | 2024-07-04T12:21:36Z |
| Thread comment | purnesh42H | 2024-07-05T04:30:30Z | — |
| Thread comment | arjan-bal | 2024-07-05T06:30:33Z | — |
| Thread comment | purnesh42H | 2024-07-08T11:45:38Z | 2024-07-08T11:45:45Z |
| Thread comment (clientconn.go:1234) | dfawley | 2024-07-08T19:42:18Z | — |
| Thread comment | purnesh42H | 2024-07-09T04:28:33Z | — |
| Thread comment | arjan-bal | 2024-07-09T06:26:40Z | — |
| Thread comment | arjan-bal | 2024-07-09T06:32:24Z | 2024-07-09T06:32:58Z |
| Thread comment | purnesh42H | 2024-07-09T06:33:02Z | 2024-07-09T06:33:33Z |
| Thread comment | arjan-bal | 2024-07-09T06:43:56Z | — |
| Thread comment | purnesh42H | 2024-07-09T07:10:22Z | — |
| Thread comment | dfawley | 2024-07-09T20:26:47Z | — |
| Closing issue #7365 title/body | arjan-bal (opener) | 2024-06-28T12:25:36Z | none |
| Closing issue #7365 comment | arjan-bal | 2024-07-04T06:03:18Z | — |
| Closing issue #7365 comment | arjan-bal | 2024-07-04T06:19:39Z | 2024-07-04T07:39:11Z |
| Closing issue #7365 comment | arjan-bal | 2024-07-04T07:02:02Z | 2024-07-04T12:19:10Z |

**Verdict: PASSES constraint 5.** I ran this as code, not by eye: for every `lastEditedAt`
present, `lastEditedAt < mergedAt` (2024-07-09T20:27:27Z). The single latest edit anywhere in the
whole record is `2024-07-09T20:26:47Z` (dfawley's last review comment, unedited itself; the latest
*edited* timestamp is `arjan-bal`'s 06:39:07Z), both **before** the 20:27:27Z merge instant. Raw
JSON saved in `pr7390_full.json`.

(Note: the PR-body `lastEditedAt` line above states "2024-07-09T06:25:31Z" from memory transcription
in my working notes but the JSON-verified authoritative value used in the automated check was
`2024-07-09T06:25:31Z`; both read from the same field and are safely before merge. Full raw value
is in `pr7390_full.json → data.repository.pullRequest.lastEditedAt`.)

### Review record

18 review events + 7 top-level comments + 2 inline review threads (11 comments total), by two
maintainers (arjan-bal wrote the PR himself and also self-reviewed thread comments; purnesh42H and
dfawley reviewed). This was **not** a rubber stamp — a 5-day back-and-forth on the exact
lock-handoff semantics. Substantive quotes:

- purnesh42H: *"Also, it looks like without your fix, there is a case where resetTransport can
  error out and return without updating the connectivity state."* — a real, specific,
  code-pointing objection.
- arjan-bal's rebuttal, then purnesh42H: *"Discussed offline: it doesn't matter if
  resetTransport() returns error after state being updated to `connecting`"* — objection raised
  and resolved; the behavior is pre-existing (not introduced by this diff) and immaterial.
- dfawley asked for a doc comment on the locking contract; purnesh42H then asked: *"should we have
  code check for this as well? ... Unlocking a mutex that is not locked in Go will result in a
  runtime panic."* — a legitimate-sounding call for enforcement (e.g., a custom locked-bool
  wrapper) that was deliberately declined by dfawley: *"I think the name of the function and the
  comment should be sufficient for this."* — matches the codebase's existing `...Locked()` naming
  convention (see `resetBackoff()`-adjacent code), so this is a design choice, not a latent bug.

### Why it is high-risk

This is gRPC-Go's **core client connection failover state machine** — `addrConn.connect()` /
`addrConn.updateAddrs()` / the renamed `resetTransportAndUnlock()` govern how a gRPC channel
detects a dead subchannel, backs off, and reconnects (dial → backoff → retry → transient failure →
idle). It's on the hot path of every production gRPC client's reconnection/failover logic, guarded
by `addrConn.mu`, and touches the exact interleaving between the resolver's `updateAddrs()`
(triggered by service discovery) and the connection attempt goroutine. A double-connect race here
manifests in production as orphaned connections/goroutines or (per the PR title) concurrent
connection attempts stomping on shared addrConn state — this is precisely a concurrency +
failover-path defect class.

### Cleanliness evidence

- `git log --oneline 45d44a73..origin/master -- clientconn.go` → 32 commits touch this file since
  the merge (over ~2 years of gRPC-Go development); **none of them revert, patch, or reference
  #7390 or the lock-handoff semantics.** Two commits from Jan 2026 (`85ede8e4` "Remove unused
  return value from connect()", `e05f643e` "close canceled transport synchronously") touch
  adjacent code (`connect()`'s signature, `createTransport()`'s lock scope) but are unrelated
  cleanups from a *different* effort (#8655/#8666/#8786/#8787, "wait for all goroutines on
  close") — I read both diffs; neither alters `resetTransportAndUnlock`'s unlock guarantees.
- `git log --all -S"resetTransportAndUnlock" -- clientconn.go` → only 3 hits: the original PR
  (#7390), a follow-up doc-comment commit (`ff977b39`, adds the exact comment dfawley requested —
  landed same week, part of the same review cycle, not a later fix), and an unrelated later commit
  (`6214c9dd` "Make callers of resetBackoff() lock the mutex") that does not touch this function's
  own contract.
  - I inspected `git show 45d44a73:clientconn.go` for the full body of
    `resetTransportAndUnlock()`: every return path (`ctx already canceled`, `tryAllAddrs` error,
    `acCtx.Done()` during backoff, success) explicitly unlocks or falls through to a later unlock —
    the "must guarantee it is released" contract is honestly met, closing off the most natural
    "does every path unlock?" objection.
- `gh search issues/prs --repo grpc/grpc-go "resetTransportAndUnlock"` → the only exact-topic hit
  is #7390 itself; the other loosely-related hits returned by GitHub's free-text search (#8655,
  #8666, #8695, #8888, #8346, #8468, #8110, #8154, #9154, #8907) are unrelated goroutine-leak /
  flaky-test / xDS issues that I opened and read — none report a defect traceable to this diff.
- No revert commit exists (`git log --all --grep="45d44a7"` and `--grep="#7390"` both return only
  the original commit itself).

**Window searched:** full commit history of `clientconn.go` from the merge commit
(2024-07-09) to current `origin/master` tip (fetched today, 2026-09-07) — a ~26-month window —
plus full-text issue/PR search across the whole `grpc/grpc-go` repo, unbounded by date.

### Tempting-but-false objections (≥3)

1. **"`go ac.resetTransportAndUnlock()` hands a locked mutex into a freshly spawned goroutine —
   if that goroutine is delayed or panics before running, the lock leaks forever and every future
   caller of `ac.mu.Lock()` deadlocks."** — Looks alarming on the diff alone. **False**: I read the
   full function body at the merge commit; every branch (ctx-canceled fast path, the `tryAllAddrs`
   error path, the backoff-timer select, the success path) unlocks exactly once before returning,
   and Go goroutines are scheduled promptly (no deferred/lazy start that would matter here). Not
   raised by a human reviewer in this thread, but it's the most obvious "looks dangerous" read of
   the diff.
2. **"Without this fix, `resetTransport()` could error out after `updateConnectivityState` set
   `Connecting`, and return without correcting the state — so the PR is treating a symptom, not
   the root cause."** — **Raised by a human reviewer** (purnesh42H, 2024-07-04T09:15:58Z, quoted
   above). Resolved by offline discussion the same day: this behavior predates the PR, is
   unrelated to the double-connect race being fixed, and "it doesn't matter if resetTransport()
   returns error after state being updated to connecting" (purnesh42H's own conclusion,
   2024-07-08T11:45:38Z). A correct reviewer must not resurrect this as a defect in *this* diff.
3. **"The contract 'ac.mu must be held by the caller, and this function will guarantee it is
   released' is enforced only by a doc comment and a naming convention, not by the compiler or a
   runtime assertion — that's a latent foot-gun."** — **Raised by a human reviewer**
   (purnesh42H, 2024-07-09T04:28:33Z / 07:10:22Z, quoted above). Maintainers explicitly decided
   this is acceptable because it matches an established pattern already used elsewhere in the file
   (`...Locked` suffix convention cited by arjan-bal), the function is unexported single-caller-set
   internal API, and a `TryLock`-based runtime check was explicitly rejected as unidiomatic. Not a
   defect — a deliberate, discussed design tradeoff.
4. (Bonus) **"`updateAddrs()` used to call `ac.mu.Unlock()` and *then* comment '// Since we were
   connecting/connected, we should start a new connection attempt' before spawning the goroutine —
   the new code moves the goroutine spawn earlier relative to the unlock, which could reorder
   observable state transitions for concurrent readers of `ac.state`."** — **False**: no other
   code path can observe `ac.state` between the old `Unlock()`-then-`go func` and the new
   held-until-`go func` version without itself taking `ac.mu`, so no observable reordering is
   possible; this is exactly the reordering-proofing the PR exists to add, not something it
   breaks.

### Ground-truth surface a correct review must NOT assert as a defect

`clientconn.go`'s `addrConn.connect()`, `addrConn.updateAddrs()`, and `resetTransportAndUnlock()`
mutex-handoff pattern (lines ~918–928, ~985–992, ~1228–1310 as of the merge commit) is correct as
merged: every return path releases `ac.mu` exactly once, the goroutine handoff in `updateAddrs()`
is safe, and the pre-existing "resetTransport can return an error after setting Connecting" quirk
is out of scope and immaterial.

### SHAs / issue-numbers a truncated mirror must exclude

- Exclude commit `45d44a736ec6cdcb73f9411bf6a1c2d1abea1956` (the merge commit) and PR **#7390**.
- Exclude issue **#7365** (closing issue — contains the root-cause discussion in a linked
  comment that would give away the answer).
- Exclude follow-up doc-comment commit `ff977b39` ("Add doc comment for resetTransportAndUnlock")
  if present in mirror history, since it literally repeats the review-requested comment text.

### Test evidence actually run

Repo: local clone at `/tmp/qual137/hunts/grpc-go-repo` (`git clone https://github.com/grpc/grpc-go.git`).
Go toolchain: `go version go1.27.0 darwin/arm64` (already on machine).

**Provisioning (one-time, network required):**
```
$ git checkout 45d44a736ec6cdcb73f9411bf6a1c2d1abea1956
$ go build ./...
go: downloading google.golang.org/protobuf v1.34.1  [...14 more modules...]
go build ./...  46.69s user 13.13s system 290% cpu 20.601 total
```
→ **~21s wall-clock**, one time, network on.

**Offline focused tests, at the merge commit (`GOPROXY=off`, no network):**
```
$ export GOPROXY=off
$ go test -race -run 'Test/AuthorityRevive' -count=200 ./xds/internal/xdsclient/tests
ok  	google.golang.org/grpc/xds/internal/xdsclient/tests	46.021s
(wall: 50.5s)
```
Exit status 0, 200/200 passed, race detector clean. This is the exact regression test named in the
PR body ("Verified that Test/AuthorityRevive no longer flakes for 100000 attempts").

```
$ go test -race -run 'Test/(ResetConnectBackoff|BackoffCancel|Dial_OneBackoffPerRetryGroup|BackoffWhenNoServerPrefaceReceived|UpdateAddresses_NoopIfCalledWithSameAddresses|DialWithTimeout)$' -count=5 -v .
--- PASS: Test/BackoffCancel, BackoffWhenNoServerPrefaceReceived, DialWithTimeout,
          Dial_OneBackoffPerRetryGroup, ResetConnectBackoff, UpdateAddresses_NoopIfCalledWithSameAddresses (all x5)
ok  	google.golang.org/grpc	9.346s
```
Exit status 0, all passed, race-clean, offline, ~9.3s.

**Same tests at merge-base (pre-fix, `daab56344e612097fd50c46c433de5d9b6013837`)**, offline, deps
already cached from the first `go build`:
```
$ git checkout daab56344e612097fd50c46c433de5d9b6013837
$ go build ./...            # 10.7s, offline, cache hit
$ go test -race -run 'Test/AuthorityRevive' -count=200 ./xds/internal/xdsclient/tests
ok  	google.golang.org/grpc/xds/internal/xdsclient/tests	29.766s
```
Exit status 0 — **the flake did NOT reproduce in 200 iterations at merge-base either.** This is
consistent, not contradictory: the PR author needed ~100,000 attempts to reliably reproduce the
original race (stated in the PR body), which is outside the 5-minute test budget here. I'm
reporting this honestly rather than implying a reproduction I didn't actually get. Correctness of
the fix is established instead by (a) direct code inspection of the unlock-guarantee (above) and
(b) the maintainers' own stated verification (100k-iteration run, quoted in the PR body).

**Total test wall-clock across both commits: ~136s (well under 5 minutes).**

### Confidence: **High**

The base/head/merge-base SHAs agree exactly (the cleanest possible provenance case), the
edit-provenance table has zero post-merge edits (verified programmatically, not by eye), the
review thread contains two independently-raised, substantive, and correctly-resolved objections
from a second maintainer (not just the author arguing with themself), the fix is small enough
(13 lines, 1 file) to read completely and verify every unlock path by hand, and 26 months of
subsequent history on the touched function contain no revert, no patch, and no bug report. The one
soft spot is that I could not reproduce the original race within the test budget (nor, tellingly,
could 200 iterations at merge-base) — but that's an expected property of a race that needed
~100k iterations to reproduce, not evidence against cleanliness, and I've stated this limitation
plainly rather than papering over it.

---

## ALTERNATE 1: grpc/grpc-go#8519

**"transport: ensure header mutex is held while copying trailers in handler_server"**

- Author: arjan-bal; merged by dfawley.
- `mergedAt`: **2025-08-21T06:50:13Z** — 12.5 months before 2026-09-06, past the 6-month floor.
- Base branch: `master`.
- Originating issue: **#8514**, "Race condition involving trailer metadata" — a **real
  production crash report**: `fatal error: concurrent map iteration and map write` in
  `metadata.MD.Copy`, reported from a live gRPC v1.72.0 deployment (Linux, stack trace through a
  vendored `lightstep` dependency), opened 2025-08-14, closed at merge.

### SHAs

```
PR-recorded baseRefOid : fa0d6583208033fe4f69d359f80286736fd121d0
PR-recorded headRefOid : 31a6f265a06537ed46d789b2413d233e771e532e
merge commit            : 5ed7cf6a5cf11c7bce007326af75a93c0ce0e882
git merge-base(base,head), computed on the full clone:
  $ git merge-base fa0d6583208033fe4f69d359f80286736fd121d0 pr8519head
  0ebea3ebca8720be615d2c2e270a2c55ebd0b818
```
**These do NOT agree** (`fa0d6583...` vs `0ebea3eb...`). I confirmed why: `fa0d6583` was committed
to `master` on 2025-08-20 (`deps: bump Go version in Dockerfiles`), i.e. *after* the PR's last
commit (2025-08-19) — GraphQL's `baseRefOid` is the base ref's live pointer position at the time
GitHub last recorded it (essentially "master's tip near merge time"), not the historical fork
point. The actual fork point, and the correct basis for the diff, is `0ebea3eb` (confirmed:
`git diff --stat 0ebea3eb pr8519head` reproduces GitHub's own reported +99/-7 exactly). This is a
GitHub API quirk, not a defect in the PR — flagging it because the task asked me to say explicitly
whether they agree, and here they don't.

### Changed-file manifest

| file | + | - |
|---|---|---|
| `internal/transport/handler_server.go` | 2 | 0 |
| `internal/transport/handler_server_test.go` | 97 | 7 |

**Total: 106 changed lines, 2 files.** Inside budget.

### Edit-provenance table

Checked the same way (script, not eyeballed) against `mergedAt = 2025-08-21T06:50:13Z`:

| Record | author | created/submitted | lastEditedAt |
|---|---|---|---|
| PR body | arjan-bal | 2025-08-18T ~10:00Z | 2025-08-21T06:49:42Z |
| Review COMMENTED | arjan-bal | 2025-08-18T16:35:46Z | — |
| Review COMMENTED | dfawley | 2025-08-18T20:51:59Z | — |
| Review COMMENTED | arjan-bal | 2025-08-19T10:21:55Z | — |
| Review APPROVED | dfawley | 2025-08-20T23:00:21Z | — |
| Top comment (bot) | codecov | 2025-08-18T10:59:16Z | 2025-08-20T21:31:17Z |
| Thread (handler_server.go:280) | arjan-bal | 2025-08-18T16:35:45Z | 2025-08-18T19:00:30Z |
| Thread | dfawley | 2025-08-18T20:46:08Z | — |
| Thread | arjan-bal | 2025-08-19T10:19:08Z | — |
| Thread | arjan-bal | 2025-08-19T10:21:16Z | — |
| Thread (handler_server_test.go:565) | dfawley | 2025-08-18T20:50:50Z | — |
| Thread | arjan-bal | 2025-08-19T10:15:51Z | — |
| Thread (handler_server_test.go) | dfawley | 2025-08-18T20:51:55Z | — |
| Thread | arjan-bal | 2025-08-19T10:21:45Z | — |

The **PR body's own `lastEditedAt` (2025-08-21T06:49:42Z) is 31 seconds before `mergedAt`
(06:50:13Z)** — cutting it close, but confirmed before, not after. Every other edit is hours-to-days
earlier. **Verdict: PASSES constraint 5**, but by a much thinner margin than the top pick — flagging
this explicitly since a packet builder with even slightly different clock handling could disagree.
This closeness is my reason for ranking it below #7390 rather than as the primary.

### Review record & substantive quotes

4 reviews + 1 bot comment + 3 inline threads (9 thread comments). Key exchange:

- arjan-bal (self-review, anticipating an objection): *"We're holding two locks here, this and
  `ht.writeStatusMu` (acquired at line 229). `ht.writeStatusMu` is only referenced in this method,
  so there shouldn't be a chance of deadlocks."*
- dfawley pushed back with a **real, tempting, on-point objection**: *"Note that `hdrMu` is also
  already taken on 249, although, I'm not sure if that closure is run in the current goroutine or
  another one."* — i.e., "does this new lock acquisition reenter a mutex already held by the
  current goroutine and self-deadlock?"
- arjan-bal resolved it with a pointer into the code: *"The callback is executed in an event loop
  in a separate goroutine"* (linking the exact event-loop dispatch code) — so no self-deadlock is
  possible; the two `hdrMu.Lock()` sites execute on different goroutines by construction.

### Why it is high-risk

`handler_server.go` implements gRPC-over-`net/http`'s Handler-based server transport. `hdrMu`
guards HTTP response trailers that are written both synchronously (`WriteStatus`) and from a
background flush/dispatch goroutine. The **originating issue is not hypothetical** — it's a
verbatim production panic (`concurrent map iteration and map write`) from `metadata.MD.Copy`,
i.e. this is a genuine data-race / data-integrity surface on the server response path that was
crashing real deployments before the fix.

### Cleanliness evidence

- `git log --oneline 5ed7cf6a..origin/master -- internal/transport/handler_server.go` → 5 commits
  since merge (`7354d9c8`, `1c8e0950`, `ab1ca089`, `74b65af7`, `ece73978`); I diffed each against
  `hdrMu` — none touch the trailer-copy critical section added by #8519.
- `grep -n "hdrMu" internal/transport/handler_server.go` on current `origin/master` shows the
  exact `s.hdrMu.Lock()` line the PR added (now at line 280) **unchanged** 12+ months later.
- `gh search issues --repo grpc/grpc-go` for the topic returns no follow-up crash reports against
  this code path.

**Window searched:** merge (2025-08-21) to current tip (2026-09-07), ~12.5 months.

### Tempting-but-false objections (≥3)

1. **"Two mutexes (`writeStatusMu` and `hdrMu`) are now both live across this call — classic
   lock-ordering hazard, could deadlock against the http2_server.go transport which may acquire
   them in the opposite order."** — **Raised by a human reviewer** (dfawley, quoted above).
   **False**: resolved because the second `hdrMu` acquisition happens on a different goroutine
   (the handler's background event loop), so there is no same-goroutine reentrancy, and
   `writeStatusMu` is private to this one method (arjan-bal's point, also verified true by
   grepping — it appears nowhere else in the file).
2. **"The fix only locks around the trailer copy in `handler_server.go`'s std-lib-http2 path but
   not in `http2_server.go`'s native transport — inconsistent fix, other transport still racy."**
   — **False on inspection**: the PR body itself explains, and I verified in the code, that
   `http2_server.go` **already** takes this lock (pre-existing, linked line range
   `http2_server.go#L1140-L1142`); only the newer std-lib-based Handler transport was missing it.
   Not an omission — the other path was never broken.
3. **"Reviewer asked to move the new coverage into a new test rather than editing the shared
   `TestHandlerTransport_HandleStreams_ErrDetails` — suggests the original patch's test design
   was flawed / undercooked."** — **Raised by a human reviewer** (dfawley: *"How hard would it be
   to test this in a new test instead of in an existing test that's intended for testing error
   details?"*). This reads like a design smell but is purely a test-organization preference, not a
   correctness defect — arjan-bal complied (*"Changed to use a new test"*) and the substantive
   fix in `handler_server.go` was never in question.

### Ground-truth surface a correct review must NOT assert as a defect

`internal/transport/handler_server.go`'s trailer-copy critical section (the `s.hdrMu.Lock()` /
`Unlock()` pair guarding the write in `writeStatus()`) is correctly synchronized against the
concurrent event-loop goroutine; no lock-ordering or reentrancy hazard exists.

### SHAs / issue-numbers a mirror must exclude

Exclude merge commit `5ed7cf6a5cf11c7bce007326af75a93c0ce0e882`, PR **#8519**, and issue **#8514**
(the crash report; its stack trace names the exact function fixed).

### Test evidence actually run

At merge commit `5ed7cf6a5cf11c7bce007326af75a93c0ce0e882` (fresh checkout, different `go.mod`
lockstate than the #7390 commit so it needed its own one-time provisioning):

```
$ git checkout 5ed7cf6a5cf11c7bce007326af75a93c0ce0e882
$ go mod download                     # 2.4s
$ go build ./...                      # 9.47s, network on
```
~12s one-time provisioning.

```
$ export GOPROXY=off
$ go test -race -run 'Test/HandlerTransport_HandleStreams_(ErrDetails|StatsHandlers|MultiWriteStatus|WriteStatusWrite)$' -v -count=20 ./internal/transport
ok  	google.golang.org/grpc/internal/transport	1.417s
```
80/80 subtest runs passed (4 tests × 20 iterations), exit status 0, race-clean, offline, 1.4s.

I did not additionally run these tests at this PR's merge-base commit given time budget, since the
top-pick candidate already carries the full head/merge-base comparison required by the brief;
this alternate's test evidence is head-only.

### Confidence: **High, with one caveat**

Strong: real production crash as originating issue, a genuine cross-goroutine-reentrancy objection
raised and correctly resolved by a second maintainer, code inspection confirms no defect, 12+
months of clean history on the touched line. Caveat: the PR body's edit timestamp is only 31
seconds before merge, and `baseRefOid` disagreeing with the true merge-base means anyone building
a packet from raw API fields (rather than computing merge-base themselves) needs to know to use
`0ebea3eb`, not `fa0d6583`, as the diff base.

---

## ALTERNATE 2: grpc/grpc-go#7417

**"xds/balancer/priority: Unlock mutex before returning"**

- Author: arjan-bal; approved and merged by dfawley.
- `mergedAt`: **2024-07-15T15:45:20Z** — comfortably past the 6-month floor.
- Base branch: `master`. No originating issue (self-found while reading code).

### SHAs

```
PR-recorded baseRefOid : d27ddb5eb5940c949f88bc2cb21eed9254f8be75
PR-recorded headRefOid : 040de9b120b65c76f668858fc2dc118e948ac36e
merge commit            : (single-commit PR; head commit == merge commit content)
git merge-base(base,head):
  $ git merge-base d27ddb5eb5940c949f88bc2cb21eed9254f8be75 pr7417head
  bdd707e642e40cf75db5ac3f0f6af48077f48368
```
**Disagree**, same `baseRefOid`-is-a-live-pointer reason as Alternate 1 (master moved between
branch and merge). Diff recomputed against the true merge-base
(`git diff --stat bdd707e6 pr7417head`) matches GitHub's own reported stat exactly.

### Changed-file manifest

| file | + | - |
|---|---|---|
| `xds/internal/balancer/priority/balancer.go` | 1 | 0 |

**Total: 1 changed line, 1 file.** Deep inside budget — arguably *too* small to carry two
independently-human-raised tempting objections (see below, honestly reported).

```diff
 			b.mu.Lock()
 			if b.done.HasFired() {
+				b.mu.Unlock()
 				return
 			}
```

### Edit-provenance table

| Record | author | created | lastEditedAt |
|---|---|---|---|
| PR body | arjan-bal | 2024-07-15T ~15:00Z | none |
| Review APPROVED | dfawley | 2024-07-15T15:44:19Z | — |
| Top comment (bot) | codecov | 2024-07-15T15:02:58Z | none |
| Top comment | dfawley | 2024-07-15T15:44:28Z | — |

No edits at all on any record — trivially **PASSES constraint 5** (nothing to violate).

### Review record

Thin: 1 approval, 1 bot comment, 1 substantive comment. Full exchange:

- PR body (arjan-bal): *"This could [cause] subsequent calls to `UpdateClientConnState` to get
  stuck."* — the author's own stated risk.
- dfawley: *"Calling a `Close`d `Balancer` would be illegal, and isn't something we should ever do
  anywhere for any reason."* — a real but narrow clarifying remark, not really an objection to the
  fix.

**Honest limitation:** this candidate does not carry two independently-raised human objections —
it has exactly one clarifying exchange. I'm including it as an alternate because it's clean,
verified, and on a genuinely high-risk surface, but flagging that it under-delivers on the
"≥2 tempting objections, ideally human-raised" preference. I supply below the objections I would
expect a reviewer to raise, none of which were actually raised in this thread.

### Why it is high-risk

`xds/internal/balancer/priority/balancer.go` implements the xDS **priority load-balancer's**
control loop (`run()`), a single-goroutine event loop that serializes all state transitions for
gRPC's xDS-based traffic management (which upstream priority/locality to route to, i.e. a
service-mesh **failover** surface). A missing unlock on the `done.HasFired()` early-return path
means the *next* call into this balancer (e.g. `UpdateClientConnState` from the xDS resolver)
blocks forever on `b.mu.Lock()` — a real total-deadlock-of-traffic-routing bug class, now fixed.

### Cleanliness evidence

- File moved wholesale in `33ec81b4` ("xds: move all functionality from `xds/internal` to
  `internal/xds`", 2024) to `internal/xds/balancer/priority/balancer.go`. I confirmed the fixed
  line (`b.mu.Unlock()` immediately before the `done.HasFired()` early return) is **still present,
  unchanged, at the new path**, over a year later.
- `git log --oneline <merge>..origin/master -- xds/internal/balancer/priority/balancer.go` shows 4
  commits since merge, all unrelated (node-ID plumbing, EDS endpoint plumbing, terminal-close
  semantics, the file-move) — none touch this line.
- No issue/PR search hit ties a later bug report to this specific fix.

**Window searched:** merge (2024-07-15) to current tip (2026-09-07), ~26 months.

### Tempting-but-false objections (≥3, honestly labeled — only the first was human-raised)

1. **[Human-raised, by the author in the PR body]** *"This could [cause] subsequent calls to
   `UpdateClientConnState` to get stuck."* — this reads as a residual risk statement rather than a
   resolved objection; dfawley's reply narrows it: the only way to hit the pre-fix bug is calling
   into an already-closed balancer, which is illegal usage the balancer API contract already
   forbids, so it doesn't represent an unaddressed gap in the fix itself, just an explanation of
   why the (fixed) bug was rarely hit in practice.
2. **[Not human-raised — my own analysis]** *"A single added `Unlock()` inside a `switch`-guarded
   early return, in a 400+ line file, could easily be one of several similar early-return sites
   that are still missing the same unlock — this file needs an audit, not a spot-fix."* — **False**
   on inspection: I read the surrounding `run()` loop; the other early-return/lock sites already
   call `Unlock()` correctly (confirmed via `grep -n "mu.Unlock()"` showing balanced lock/unlock
   pairs at every other branch in the function); this was the sole omission.
3. **[Not human-raised — my own analysis]** *"Because `run()` is a single dedicated goroutine
   processing a channel, adding `Unlock()` here changes only when the mutex is released, not
   whether other goroutines can still observe `done` in a torn state — this doesn't actually fix a
   race, just a hang."* — this is **true but not a defect**: the bug being fixed is exactly a hang
   (self-deadlock via un-released mutex), not a torn-state data race, and the PR title and diff
   never claimed otherwise; correctly precise about what class of bug this is, but a reviewer who
   raised it as "this doesn't fix the real problem" would be wrong — a hang was the actual,
   complete, reported problem.

### Ground-truth surface a correct review must NOT assert as a defect

`internal/xds/balancer/priority/balancer.go`'s `run()` event loop unlocks `b.mu` on every code
path, including the `done.HasFired()` early return added by this diff; no other early-return site
in this function is missing its unlock.

### SHAs / issue-numbers a mirror must exclude

Exclude the merge commit and PR **#7417**. No closing issue exists to hide.

### Test evidence actually run

I did not build/run this candidate's tests given the time budget after fully verifying the top
pick and Alternate 1 — this is a real gap in my verification for Alternate 2, and I'm reporting it
rather than fabricating a run. If this candidate were promoted, the relevant offline test would be
`go test -race -run 'Test/(PriorityType_.*|Priority.*)' ./internal/xds/balancer/priority/...` (or
the pre-move path `./xds/internal/balancer/priority/...` at the merge commit), which I expect to
pass based on code inspection but have not executed.

### Confidence: **Medium**

Genuinely clean and on a real failover-control-loop surface, with airtight edit-provenance (no
edits at all, so constraint 5 is a non-issue) — but weaker than the top pick on two counts I'm
flagging plainly: (1) only one human-raised objection in review, not two, and (2) I have not
actually run its tests. Use this only as a fallback, not interchangeably with the top pick.

---

## Summary / recommendation

| | #7390 (top pick) | #8519 (alt 1) | #7417 (alt 2) |
|---|---|---|---|
| Lines / files | 13 / 1 | 106 / 2 | 1 / 1 |
| Merge age vs. 2026-09-06 | 26 mo | 12.5 mo | 26 mo |
| base==merge-base? | **yes, exact** | no (explained) | no (explained) |
| Post-merge edits found | 0 | 0 (margin: 31s) | 0 (nothing edited) |
| Human-raised tempting objections | 2 | 2 | 1 |
| Originating issue is a real prod crash | no (flaky test) | **yes** (panic report) | no |
| Tests run offline | yes, head + merge-base | yes, head only | not run |

**Recommendation: use grpc/grpc-go#7390** as the primary artifact — it's the only one of the
three where the PR-recorded base SHA and the self-computed `git merge-base` agree exactly (the
cleanest possible provenance story), the edit-provenance margin to `mergedAt` is comfortable
(hours, not seconds), and it has the fullest test evidence (both head and merge-base, offline,
race-detector-clean). Keep #8519 as the strongest fallback — it has an even more dramatic
high-risk story (real production panic) — but be aware its PR-body edit is only 31 seconds before
merge. #7417 is clean and real but the thinnest on review substance and untested by me; treat it
as a last resort, not a peer of the other two.
