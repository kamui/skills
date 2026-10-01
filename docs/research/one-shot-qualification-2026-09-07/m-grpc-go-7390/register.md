# Target

- Repository: `grpc/grpc-go`
- Pull request: [#7390](https://github.com/grpc/grpc-go/pull/7390) — "grpc: hold ac.mu while calling resetTransport to prevent concurrent connection attempts"
- Head SHA: `76ef33f44a600c3ed1a385979fd1dfbcade3fbb6` (merge commit; the actual content-bearing commit on `master` is `45d44a73`)
- Merge-base: `daab56344e612097fd50c46c433de5d9b6013837`
- Merged: 2024-07-09T20:27:27Z, author Arjan Singh Bal (`arjan-bal`), approved by `purnesh42H` and maintainer `dfawley`.
- Files touched: only `clientconn.go`, 6 insertions / 7 deletions (`git diff daab5634..76ef33f4 -- clientconn.go`).
- Motivating issue: [#7365](https://github.com/grpc/grpc-go/issues/7365), "Flaky Test/AuthorityRevive" (0.4%, 399/100000 runs). Root cause per `arjan-bal`'s investigation on that issue: `addrConn.connect()` released `ac.mu` after checking `ac.state == Idle` but *before* `resetTransport()` re-acquired it and set state to `Connecting`, leaving a window where a second, concurrent `connect()` call also observed `Idle` and started a second connection attempt (`tryAllAddrs` called twice, one transport orphaned).

# Verdict

adjudicated clean — `D_m = 0`

# Defect register

None. No material defect was found in this change, at the pinned head or in the two years of subsequent history available in the clone.

# Reproduction

All commands run from a real checkout (`git worktree`) of the exact SHAs, Go 1.27.0 darwin/arm64.

1. **Build.**
   - Head (`76ef33f4`): `go build ./...` → clean, exit 0.
2. **Targeted unit tests, with race detector, at head:**
   ```
   cd head && go test -race -run 'Test/(CloseConnectionWhenServerPrefaceNotReceived|ConnectParamsWithMinConnectTimeout|ResetConnectBackoff|ResolverServiceConfigBeforeAddressNotPanic|ResolverServiceConfigWhileClosingNotPanic|UpdateAddresses_NoopIfCalledWithSameAddresses|WithConnectParams)$' -v .
   ```
   Result: **all 7 pass**, total 5.64s. (These are every test in the top-level `grpc` package whose name suggests coverage of `connect`/`updateAddrs`/backoff/state-transition logic; there is no unit test with "resetTransport" in its name — the only regression evidence the PR author supplied was the flaky-test count below.)
3. **Same tests at merge-base (`daab5634`):** identical command → **all 7 pass**, 5.64s. No pre-existing failure masked by the change; no regression introduced against this suite.
4. **Stress-reproduction attempt of the original race**, `TestAuthorityRevive` (the flaky test named in issue #7365), at merge-base (pre-fix) only, without `-race` (matching how the original 0.4% flake was characterized — a logic race, not a data race caught by `-race`):
   ```
   cd base && go test -run 'Test/AuthorityRevive$' -count=1500 ./xds/internal/xdsclient/tests/...
   ```
   Result: `ok … 192.352s`, **0 failures in 1500 runs**. This does **not** reproduce the reported race locally — expected, since the original report describes a 0.4% flake rate observed on Google's CI ("forge") that depends on scheduler/goroutine-timing conditions this sandboxed run evidently doesn't hit at the same rate (single-machine, likely different core count/contention profile, and the original issue itself only saw 399/100000). I did not have budget to run 100,000 iterations. This is `unresolved` as an independent reproduction; the evidentiary basis for the pre-fix bug rests on the primary-source investigation quoted below, not on a reproduction I generated myself.
   - Primary-source evidence instead: `arjan-bal`'s root-cause comment on #7365 (quoted above) with an actual double-`tryAllAddrs`-invocation log capture, and the PR body's own claim: "Verified that Test/AuthorityRevive no longer flakes for 100000 attempts with the change" — a scale of reproduction outside this session's budget.
5. **Static trace of every return path of `resetTransportAndUnlock`** (`clientconn.go`, head, lines 1231-1296) confirms the lock contract holds — see "Ground-truth surface" below for the full path enumeration.

# Not ground truth

Plausible-sounding objections that a reviewer might raise, and why each is not a material defect:

1. **"Handing a locked `sync.Mutex` to a new goroutine via `go ac.resetTransportAndUnlock()` in `updateAddrs` is unsafe / non-idiomatic."**
   Reason it's not a defect: Go's `sync.Mutex` has no goroutine-affinity or ownership tracking (unlike some other languages' non-reentrant locks) — any goroutine may call `Unlock` on a mutex locked by another goroutine. This is a recognized, if uncommon, Go pattern precisely for the "acquire now, unlock inside the deferred work" case. It was raised and explicitly discussed by the author on the PR itself (see Preexisting hints) and is the entire mechanism the fix relies on to close the race window; it is intentional design, not an oversight.

2. **"`resetTransportAndUnlock`'s contract ('caller must hold the lock, callee guarantees release') is not statically or dynamically enforced — a future caller could get it wrong."**
   Reason it's not a material defect *for this PR*: this is a design-level extensibility concern (raised and consciously accepted by the reviewers themselves, see below), not a defect in the code as merged. There are exactly two call sites, both audited above and both correct. If (hypothetically) a mismatched caller were added later, Go's runtime would panic loudly on an unlock-of-unlocked-mutex, and the repo already relies on this exact convention (`...Locked`-suffixed helper methods) elsewhere without compile-time enforcement. Style/hygiene, not correctness-with-consequence.

3. **"No new unit test was added for the concurrency fix itself; the diff is 0 lines of test changes."**
   Reason it's not a material defect: test-coverage gaps are explicitly excluded from "material" by the rubric unless they demonstrate a specific unverified failure mode. Coverage here comes from the fact that the change is provably correct by direct inspection (every return path unlocks exactly once — verified above) and was validated against the actual flaky integration test before merge (100k-iteration run, no test-suite regression). This is a legitimate coverage-hygiene observation, not a correctness defect.

4. **"The `go ac.resetTransportAndUnlock()` goroutine in `updateAddrs` is untracked — `ClientConn.Close()` can return before it exits, which could look like a resource/goroutine leak."**
   Reason it's not a defect introduced by this PR: this pattern (`updateAddrs` spawning an untracked goroutine to run the reset logic) predates this PR — the pre-image was `ac.mu.Unlock(); go ac.resetTransport()`, already untracked. This PR only moved the `Unlock()` call from the caller into the callee; it did not add or remove the goroutine or its trackedness. The broader "goroutines can outlive Close()" concern is real but is a pre-existing, separate architectural issue, tracked independently as issue [#8655](https://github.com/grpc/grpc-go/issues/8655) ("Allow waiting for all goroutines to exit on client connection close") and attempted (but closed, unmerged) in PR [#8666](https://github.com/grpc/grpc-go/pull/8666); neither references or attributes the issue to #7390's locking change. A narrower, unrelated fix for a different goroutine-leak path was later merged as `e05f643e` ("close canceled transport synchronously", #8786) in `createTransport`, again not touching `resetTransportAndUnlock`'s locking.

5. **"Extending the critical section (holding `ac.mu` across `updateConnectivityState` and into the handoff) increases lock contention / could serialize things that used to run in parallel."**
   Reason it's not a defect: this is the literal, disclosed, intended effect of the fix ("hold ac.mu … to prevent concurrent connection attempts" — the PR title). Serializing concurrent connection *attempts* for the same `addrConn` is the correctness property being restored, not a performance regression; the lock is held only across cheap, non-blocking bookkeeping (state transitions), never across the actual dial (`ac.mu.Unlock()` happens before `ac.tryAllAddrs(...)` in every path).

# Preexisting hints

The review record shows the reviewers explored exactly the two concerns this adjudication was asked to test, and converged on the design that ships at head:

- `purnesh42H` (2024-07-04): *"May be we can make the resetTransport() in the same critical section instead of releasing lock and aquiring again in resetTransport()?"* — this is the suggestion that became the PR's actual mechanism.
- `arjan-bal` (2024-07-04), reacting to that suggestion, explicitly named the deadlock/double-unlock risk this adjudication was asked to test for: *"We could rename `resetTransport` to `resetTransportLocked` and expect the callers to hold the lock while calling this method. However, `resetTransport` releases the lock temporarily. Add to this that ac.updateAddrs calls `resetTransport` in a new go routine so it can't hold the lock till `resetTransport` completes. It feels a little risky to make that change. I don't know for sure, but I feel we could end up in a situation where the lock is not released correctly resulting in a deadlock. I don't want do make that change as the first option."* The team nonetheless converged on this approach four days later (commit `c3a3d1c4`, "Update conn state to prevent concurrent connection attempts"), i.e. they took the risk deliberately and iterated on it under review rather than being unaware of it.
- `purnesh42H` (on the final `resetTransportAndUnlock` naming) pressed on enforceability: *"i meant just having a doc doesn't enforce the mutex should be locked. Unlocking a mutex that is not locked in Go will result in a runtime panic."* — `arjan-bal` and `dfawley` (maintainer) both concluded the doc comment plus panic-on-misuse plus race-detector-covered tests were sufficient (`dfawley`: *"I think the name of the function and the comment should be sufficient for this."*). This is a disclosed, accepted trade-off, not an unnoticed gap.
- `dfawley` requested the exact doc comment that ships at head (*"Please add a short comment here: ... ac.mu must be held by the caller, and this function will guarantee it is released."*), which was added in `ff977b39` and is the contract text quoted in the task prompt.
- `dfawley` also asked about user-visible impact of the underlying bug (*"What is the user-visible symptom here? A memory leak?"*), and `arjan-bal` answered concretely: *"only one transport is closed when the subConn is updated (`ac.transport`) and the other transport is orphaned. The orphaned transports get closed when the server is shutdown at the end of the test."* — i.e. the pre-fix bug's consequence (orphaned transport, not a crash or permanent leak within an active connection) is disclosed and matches the release note ultimately used: "client: fix race that could lead to orphaned connections and associated resources."

None of the reviewers, in this record, identified a residual defect in the merged code — the "deadlock" concern above was about *whether to attempt* the change, and was resolved by the implementation actually shipped (which this adjudication independently verified path-by-path).

# Leakage

A truncated mirror for this evaluation must exclude:

**Commits/SHAs:**
- `76ef33f44a600c3ed1a385979fd1dfbcade3fbb6` (given head) and `45d44a73` (the actual master commit it merges to) — these *are* the answer.
- `c3a3d1c48adcf492696029fa946d606e5e7ba40a`, `6214c9dd1cd421727852b03cafceac7c9e9eb973`, `ff977b39` — the PR's own intermediate commits, showing the design iteration (including the "Add doc comment" commit that produced the exact contract text quoted in the task).
- `daab56344e612097fd50c46c433de5d9b6013837` — merge-base; fine to include as a boundary, but its neighborhood in `git log` immediately surfaces the PR.

**Issues/PRs whose content gives away the answer or invites false-positive conflation:**
- Issue **#7365** — contains the full root-cause analysis and the double-`tryAllAddrs` log capture; directly gives away both the pre-fix bug and its fix.
- PR **#7390** review thread itself — contains the reviewers' own deadlock-risk discussion quoted above.
- Issue **#6914** — referenced in the PR thread as an unrelated flaky test; low risk but mentioned in the same comment thread.
- Issue **#8655** and PR **#8666** — a *different*, pre-existing untracked-goroutine/Close() issue that superficially resembles a "goroutine leak from this PR's `go ac.resetTransportAndUnlock()`" and could tempt a reviewer into a false-positive material-defect claim; a mirror should exclude these or a reviewer should be told they postdate and are unrelated to this change.
- PR **#8786** (`e05f643e`) and PR **#8787** (`85ede8e4`) — later, unrelated touches to `createTransport`/`connect()` in the same file; not fixes of this PR's defect, but close enough in subject matter to bias a reviewer.
- PRs **#8738**, **#7498**, **#7378** — later feature commits that also touch `resetTransportAndUnlock`/`updateAddrs` (metrics, pickfirst dualstack, locality) without altering the locking contract; irrelevant but should be excluded from any "what happened later" search surface to avoid noise.

# Adjudicator's confidence and limits

- **High confidence** in the core claim: every return path of `resetTransportAndUnlock` at the pinned head (`clientconn.go:1234-1296`) was manually traced and locks/unlocks exactly once per path, with no double-unlock and no path that returns while erroneously holding or erroneously having dropped the lock relative to its contract. Both call sites (`connect()` at line 922, `updateAddrs()` at line 996) hold `ac.mu` at the call and neither touches `ac.mu` afterward, satisfying the "guarantee released" contract including the goroutine-handoff case.
- **High confidence** on "nothing reverted or repaired this": `git log -S"resetTransportAndUnlock" --all` returns exactly one commit (the PR itself) in a full clone with history through 2026-09; three later commits touch the same functions but only add unrelated metrics/features without altering lock structure (diffed and confirmed above).
- **Medium confidence, disclosed as `unresolved`**, on independently reproducing the pre-fix race: 1500 local iterations of `TestAuthorityRevive` at merge-base produced 0 failures, which does not confirm the ~0.4% flake independently — plausibly an artifact of local scheduling/timing differing from the CI environment where it was originally observed, and/or the reported rate being low enough that 1500 runs isn't a reliable sample (expected ~6 failures at the reported rate, so a true miss is unlikely but not impossible; I did not have budget for 100,000 runs). I did not attempt a `-race`-detector-based structural reproduction (e.g., artificially delaying the scheduler) that might raise the hit rate; that would strengthen the base-line finding further if desired.
- I did not run the full `grpc-go` test suite (would take considerably longer than budget allowed) — only the tests plausibly exercising `connect`/`updateAddrs`/backoff paths in the top-level package, at both revisions, under the race detector.
