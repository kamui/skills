# Scorecard — target `m` (grpc/grpc-go#7390)

## Ground truth summary

Register verdict: **adjudicated clean — `D_m = 0`**. No `GT-` entries exist on this target. Every
published "material" finding by any review is therefore either (a) a **false finding**, (b) a
**true-but-not-material** fact, or (c) a **new candidate** requiring separate adjudication. No review
can "recover" a defect because none exists; no review can be **false clean** because there is no
material defect to have missed. The register's §"Not ground truth" lists five specific objections a
reviewer might raise and explains why none is material; §"Preexisting hints" shows the human reviewers
already explored and consciously accepted the lock-handoff/enforcement risk.

I verified the relevant source directly in `/tmp/qual137/transport-check/m` (see per-review sections)
rather than taking any review's claims on faith.

---

## Review `blind-5439c5.md`

**Verbatim content (full):**
```
Approved (advisory) — 0 must-fix findings, 0 open questions.
Mode: Retrospective review of merged pull request; publication disabled.
Intent: Hold ac.mu for the full state-check-to-Connecting transition around resetTransport
(renamed resetTransportAndUnlock) so two racing connect()/updateAddrs() calls cannot both
observe Idle and start parallel connection attempts, fixing the flaky Test/AuthorityRevive.
Issue fit: Met — the lock is now held continuously from the Idle/state check in connect() and
updateAddrs() through the Connecting transition inside resetTransportAndUnlock, closing exactly
the window issue #7365 root-caused; resetTransportAndUnlock's locking contract is documented as
reviewers requested.
Coverage: Complete merge-base diff reviewed (clientconn.go, +6/-7, the only changed file); both
call sites of the renamed function and its every lock/unlock path traced at head and merge-base;
CONTRIBUTING.md inspected (no applicable rule). go build ./..., go vet ./..., go test -race .
(root package), and go test -race -count=30 -run 'Test/AuthorityRevive$'
./xds/internal/xdsclient/tests/... all pass.
Reviewed: 76ef33f4… against merge-base daab5634…
```

1. **Recovered defect IDs:** none (no `GT-` entries exist; N/A).
2. **Missed defect IDs:** none (there are none to miss).
3. **Fix sufficiency:** N/A.
4. **Findings not in the register:** none published — zero findings, zero observations, zero
   questions. Nothing to classify.
5. **Action/severity errors:** none (no findings to mis-prioritize).
6. **Questions/observations/hygiene items:** 0 questions, 0 observations, 0 hygiene items.
7. **Derived status:** "Approved (advisory)". Declares coverage **complete** ("Complete merge-base
   diff reviewed … the only changed file"). No caveat of incompleteness.
8. **False clean:** No — the target genuinely has `D_m = 0`, so "Approved, 0 findings" is the
   correct verdict. (Not false clean by definition, since there is no material defect to miss.)
9. **Duplicates:** none.

Notes: the "Issue fit" and "Coverage" narrative match the register's own account almost point for
point (continuous-lock-holding mechanism, doc-comment contract, no test-file changes in the diff).
The specific test invocations claimed (`go vet ./...`, `-race -count=30` on `AuthorityRevive`) are
plausible given the packet's run conditions and not contradicted by anything in the clone. This is
the thinnest of the four reviews — correct but adds no independent verification detail (e.g., no
mention of the lock-handoff-into-goroutine subtlety, no doc-comment nuance) beyond restating that the
mechanism works.

---

## Review `blind-5b6dd9.md`

**Verbatim summary (relevant excerpt):**
```
Approved (advisory) — 0 must-fix findings, 0 open questions.
...
Issue fit: Met — issue #7365's root cause (two tryAllAddrs attempts because the old resetTransport
only set Connecting after re-acquiring a lock its caller had briefly released) is closed by holding
the lock continuously from the state check into the state update in both callers; ... The pull
request's own supporting claim of running the regression test for 100000 attempts without a flake
is not independently reproducible within this review's offline execution budget and is recorded as
not-verifiable rather than confirmed; it is not contradicted by the runs performed here.
```

**Observation (verbatim):**
```
Holding `ac.mu` across the `go ac.resetTransportAndUnlock()` spawn in `updateAddrs` leaves that
function's own deferred `ac.transport.GracefulClose()` cleanup blocked until the spawned goroutine
releases the lock, a handoff that `tearDown` avoids in the same file by unlocking explicitly before
calling `GracefulClose`. Evidence: `clientconn.go:983-996`, `clientconn.go:1571-1583`.
```

1. **Recovered defect IDs:** none (N/A, clean target).
2. **Missed defect IDs:** none.
3. **Fix sufficiency:** N/A.
4. **Findings not in the register:**
   - The one item above is filed as an **Observation**, not a blocking/must-fix finding, and no fix
     is proposed or demanded.
   - **Classification: `true but not material`.** I verified this directly:
     - The diff (`git diff daab5634 76ef33f4 -- clientconn.go`) shows the pre-image had an explicit
       `ac.mu.Unlock()` in `updateAddrs` immediately before `go ac.resetTransport()`; the PR deletes
       that explicit unlock and transfers unlock responsibility into the spawned goroutine via
       `resetTransportAndUnlock`.
     - `updateAddrs` (clientconn.go:985-987) does `defer ac.transport.GracefulClose()` when
       `ac.transport != nil`, and that defer fires when `updateAddrs` returns — i.e. right after
       `go ac.resetTransportAndUnlock()` is spawned, while `ac.mu` is still locked (nothing in
       `updateAddrs` unlocks it on this path any more).
     - `http2Client.GracefulClose()` (internal/transport/http2_client.go:1045) synchronously calls
       `t.onClose(...)`, and the `onClose` closure passed in by `createTransport`
       (clientconn.go:1351-1352) does `ac.mu.Lock(); defer ac.mu.Unlock()`. So the deferred
       `GracefulClose()` call in `updateAddrs` really does block on `ac.mu` until the spawned
       `resetTransportAndUnlock` goroutine releases it — confirming the claim.
     - `tearDown` (clientconn.go:1569-1571) does explicitly `ac.mu.Unlock()` before calling
       `curTr.GracefulClose()`/`Close()`, confirming the contrast drawn.
     - However, this is **not material**: it is bounded lock contention, not a deadlock — the
       spawned goroutine has no dependency on the blocked caller and always proceeds to unlock
       (either immediately, if `acCtx.Err() != nil`, or after cheap state-transition bookkeeping,
       per `resetTransportAndUnlock`'s traced body). It matches register "Not ground truth" #5
       (extending the critical section is the fix's disclosed, intended mechanism) and does not
       demonstrate any consequence (no hang, no correctness change, no resource leak). The reviewer
       itself does not claim a deadlock or a required fix — it is filed purely as an informational
       observation, correctly calibrated below the material bar.
5. **Action/severity errors:** none — the item carries no priority/action tag and demands no action;
   there is no mismatch between evidence and requested action because none is requested.
6. **Questions/observations/hygiene items:** 1 observation (above); answerable from the material the
   reviewer had (source + packet, no execution needed beyond what's already run); its answer (true,
   non-material) would not change the review's verdict, and did not.
7. **Derived status:** "Approved (advisory)". Declares coverage **complete** ("Complete merge-base
   diff reviewed … no gaps"), and explicitly flags the PR's own 100k-iteration claim as
   "not independently reproducible … recorded as not-verifiable rather than confirmed" — a well
   calibrated, honest incompleteness caveat on a *secondary* evidentiary point (not on its own
   coverage).
8. **False clean:** No — correct verdict on this clean target.
9. **Duplicates:** none (single observation).

This is the strongest of the four on genuine, source-verified insight: the lock-handoff-into-defer
interaction is real, correctly evidenced with line numbers, correctly contrasted with `tearDown`'s
different pattern, and correctly filed as non-blocking since it isn't actually harmful.

---

## Review `blind-dfeab0.md`

**Verbatim content (full):**
```
Approved — 0 findings, 0 open questions.
...
Issue fit: Met — callers of the renamed resetTransportAndUnlock now hold ac.mu across the
idle/ready check and the transition to Connecting, closing the window the issue's root-cause
analysis describes. The PR's "Test/AuthorityRevive no longer flakes for 100000 attempts" claim is
a supporting assertion, not independently reproduced at that scale; it was spot-checked at 30
-race iterations (pass) instead.
Coverage: Complete merge-base diff reviewed (clientconn.go, +6/-7, 1/1 diff chunks, nothing
withheld). No test function was added or substantively changed by this diff, so the rubric's
Changed-tests section has no scope here. Two pre-existing tests were run once each, offline, as
candidate verification (not required by Changed tests): Test/SubConnEmpty (./test/, pass,
~0.01s, confirms no self-deadlock on the live-transport GracefulClose path) and
Test/AuthorityRevive (./xds/internal/xdsclient/tests/, -race -count=30, pass, 5.9s).
Reviewed: 76ef33f4 against merge-base daab5634.
```

1. **Recovered defect IDs:** none (N/A, clean target).
2. **Missed defect IDs:** none.
3. **Fix sufficiency:** N/A.
4. **Findings not in the register:** none published. Zero findings, zero observations. The
   "Coverage" line's factual claim — that `TestSubConnEmpty` "confirms no self-deadlock on the
   live-transport GracefulClose path" — is worth checking since it is the closest thing to an
   affirmative technical claim in this review:
   - Verified `test/subconn_test.go:48`: `TestSubConnEmpty` "tests that removing all addresses from
     a SubConn and then re-adding them does not cause a panic and properly reconnects" — this does
     exercise `updateAddrs` with a live transport and the `GracefulClose`/reconnect path discussed
     above under `blind-5b6dd9`. The claim is accurate and directly relevant to the exact lock-handoff
     interaction that review flagged, though this review doesn't discuss the interaction itself —
     it only reports the test result. **Classification: `true but not material`** (a supporting test
     fact, not a finding).
   - Confirmed `Test/SubConnEmpty` and `Test/AuthorityRevive` are valid `-run` patterns for this repo
     (grpc-go's `test/end2end_test.go:95` defines a single `func Test(t *testing.T)` that fans out
     into subtests named after each `(s) TestXxx` method via `grpctest`), so the invocation syntax
     is legitimate, not fabricated.
5. **Action/severity errors:** none.
6. **Questions/observations/hygiene items:** 0 questions, 0 observations, 0 hygiene items.
7. **Derived status:** "Approved" (no "(advisory)" qualifier, unlike the other three — the header
   itself is just formatting and doesn't change the substance). Declares coverage **complete**
   ("Complete merge-base diff reviewed … nothing withheld") and is explicit that the diff's own test
   coverage is out of scope because no test file changed — an accurate, honest scoping statement, not
   evasion.
8. **False clean:** No — correct verdict.
9. **Duplicates:** none.

This review's test selection (spot-checking `TestSubConnEmpty` for the live-transport reconnect path)
independently targets exactly the lock-handoff scenario `blind-5b6dd9` calls out as an observation,
and correctly reports it passes — i.e., it empirically confirms there is no actual deadlock there,
which corroborates my own source-level tracing above.

---

## Review `blind-e81c70.md`

**Verbatim summary (relevant excerpt):**
```
Approved (advisory) — 0 must-fix findings, 1 consider finding.
...
Coverage: Complete merge-base diff (clientconn.go, +6/-7, 3 hunks) reviewed with full function
context; both call sites of the renamed function, the lock-handoff into a spawned goroutine, and
the GracefulClose/onClose interaction were traced against base and head; no other repository-
tracked guidance file applies.
```

**Finding (verbatim):**
```
[P3] [consider] Correct the resetTransportAndUnlock doc comment's "unconditionally" claim
Triggers when: A reader (human or agent) relies on the doc comment for resetTransportAndUnlock
without re-deriving its body, in particular for a call where ac.ctx is already canceled when the
function runs (for example, a concurrent ClientConn teardown).
Impact: The comment states the function "unconditionally connects the addrConn," but the
function's first lines return immediately — unlocking ac.mu without attempting any connection —
whenever acCtx.Err() != nil. A maintainer trusting the comment's wording could assume every call
performs a connection attempt and misjudge backoff or lock-handoff reasoning that depends on that
assumption.
Change: In clientconn.go, reword the comment to state the early-return case, e.g. "connects the
addrConn unless its context has already been canceled, in which case it unlocks and returns
without connecting."
Closing this without action is a correct response.
```

1. **Recovered defect IDs:** none (N/A, clean target).
2. **Missed defect IDs:** none.
3. **Fix sufficiency:** N/A (no register defect recovered), but noting the finding's own proposed
   fix for completeness: the review proposes a one-line reword of the doc comment
   (`clientconn.go:1231-1233`) to state the early-return case explicitly. If this were treated as a
   standalone (non-material) documentation nit, the proposed reword would be **sufficient** to
   resolve the inaccuracy it identifies.
4. **Findings not in the register:**
   - **Classification: `true but not material`.** Verified directly against
     `clientconn.go:1231-1236`:
     ```
     // resetTransportAndUnlock unconditionally connects the addrConn.
     //
     // ac.mu must be held by the caller, and this function will guarantee it is released.
     func (ac *addrConn) resetTransportAndUnlock() {
         acCtx := ac.ctx
         if acCtx.Err() != nil {
             ac.mu.Unlock()
             return
         }
         ...
     ```
     The comment does say "unconditionally connects," and the function does have an early return
     that unlocks and returns without connecting when `acCtx.Err() != nil`. So the literal wording
     of the doc comment is imprecise — this part of the finding is factually correct. It is not a
     defect in the register's sense: it demonstrates no consequence (the *lock* contract —
     "will guarantee it is released" — the part that actually matters for correctness and that the
     human reviewers pressed on at length, per the register's "Preexisting hints" — is upheld on
     every path, including this one). The finding itself doesn't claim a functional consequence
     beyond a hypothetical future maintainer's confusion, and is explicitly filed as [P3] [consider]
     with "Closing this without action is a correct response" — i.e. self-calibrated as optional
     documentation polish, not a required fix. This is a correct, well-bounded severity call.
5. **Action/severity errors:** none — the finding is filed at the lowest priority tier (P3/consider,
   non-blocking, "closing without action is correct"), which matches its actual (non-material,
   wording-only) weight. No mismatch between evidence and requested action.
6. **Questions/observations/hygiene items:** 0 open questions; 1 hygiene/documentation-wording item
   (the finding above, functionally a hygiene note despite being filed in the "Findings" channel
   rather than an "Observations" channel). Answerable from the material the reviewer had (pure
   source read, no execution needed); its answer (true, cosmetic) would not change the overall
   verdict, and did not.
7. **Derived status:** "Approved (advisory)" with 1 non-blocking consider-level item. Declares
   coverage **complete** ("Complete merge-base diff … reviewed with full function context … traced
   against base and head").
8. **False clean:** No — correct verdict; the one item is explicitly non-blocking and consciously
   left open as optional, not asserted as clean-with-a-gap.
9. **Duplicates:** none.

---

## Cross-review table

| Review | Recovered IDs | Recall (R/D) | Fix sufficiency | False findings (count) | Action errors | Questions | Observations | False clean | Status |
|---|---|---|---|---|---|---|---|---|---|
| `blind-5439c5` | none | 0/0 | N/A | 0 | 0 | 0 | 0 | No | Approved (advisory), coverage complete |
| `blind-5b6dd9` | none | 0/0 | N/A | 0 | 0 | 0 | 1 (true-but-not-material) | No | Approved (advisory), coverage complete |
| `blind-dfeab0` | none | 0/0 | N/A | 0 | 0 | 0 | 0 | No | Approved, coverage complete |
| `blind-e81c70` | none | 0/0 | N/A | 0 | 0 | 0 | 1 (true-but-not-material, filed as a P3/consider finding) | No | Approved (advisory), coverage complete |

`D = 0` for this target, so `R/D` is reported as `0/0` (undefined/vacuous — not a penalty) for all
four; none missed anything because there is nothing to miss, and none fabricated a material claim.

## New candidates (consolidated across reviews)

Two candidate observations were raised (by `blind-5b6dd9` and `blind-e81c70` respectively); neither
review characterized its item as a material defect, and my own source verification agrees with both
that they are **not material**. I list them here only because the task requires surfacing anything
resembling a "new candidate" claim for separate adjudication, even when the originating review itself
already scoped it as non-blocking.

1. **Lock-handoff blocks `updateAddrs`'s own deferred `GracefulClose` (raised by `blind-5b6dd9`, as
   an Observation).**
   - Evidence checked: pre/post diff of `clientconn.go` confirms the explicit `ac.mu.Unlock()` before
     `go ac.resetTransport()` was removed; `http2Client.GracefulClose()` synchronously calls
     `onClose`, which locks `ac.mu`; `tearDown` unlocks before calling `GracefulClose`/`Close` for
     exactly this reason (documented in its own comment).
   - Ruling: **not material**. It is bounded, self-resolving lock contention (the goroutine holding
     the lock always releases it promptly; no cross-goroutine dependency creates a cycle), not a
     deadlock, hang, or correctness change. `blind-dfeab0`'s independent execution of
     `TestSubConnEmpty` (which exercises exactly this reconnect-with-live-transport path) passing in
     ~0.01s is consistent with "no observable deadlock in practice."
   - Confidence: **high** that this is not material, based on direct code tracing plus a passing
     test that exercises the exact path. What would raise it to material: evidence of an actual
     unbounded block or livelock (e.g., if the spawned goroutine's fast path could itself block
     indefinitely on something requiring the caller to proceed first) — I traced `resetTransportAndUnlock`
     and found no such dependency, so I consider this settled rather than merely provisional.

2. **`resetTransportAndUnlock` doc comment says "unconditionally" but has an early-return path
   (raised by `blind-e81c70`, as a P3/consider finding).**
   - Evidence checked: `clientconn.go:1231-1236`, confirmed the comment text and the early-return
     both exist as quoted.
   - Ruling: **not material** — a real wording imprecision with no demonstrated functional
     consequence; the part of the contract that matters for correctness ("this function will
     guarantee [`ac.mu`] is released") holds on every path, including the early-return one. This is
     squarely a documentation/hygiene item, correctly filed at the lowest priority.
   - Confidence: **high**. Settled by direct text comparison; no further evidence would change this.

No other candidate claims were raised by any of the four reviews (the other two, `blind-5439c5` and
`blind-dfeab0`, published zero findings/observations beyond their summary narrative).

## Process notes

- I did not attempt to identify or compare reviewer identity across the four files. I did notice that
  two of the four files' trailing HTML comments carry an identical `context=` hash value; I have not
  used this, or any other apparent identifier, to inform any score or ranking above — each review was
  scored solely on its own published text against the register and the source.
- All source-level claims quoted above (the diff, the `GracefulClose`/`onClose` lock chain, the
  `resetTransportAndUnlock` doc comment and early return, the existence and behavior of
  `TestSubConnEmpty`, and the `grpctest` subtest-naming convention) were independently verified against
  `/tmp/qual137/transport-check/m` in this session, not taken on any review's word.
