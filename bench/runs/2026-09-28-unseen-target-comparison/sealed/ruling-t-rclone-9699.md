# Ruling: t-rclone-9699

## Target

- rclone/rclone#9699, "lib/batcher: prevent commits racing shutdown", by `lntutor`. Opened 2026-07-30T17:06:34Z. Merged 2026-08-01T11:29:45Z by `ncw` (`gh pr view 9699 --json ...`).
- Head `0b87bc4788cd50664b82dd7e74c78aa2c7fc3b1c`. The PR-recorded base and `git merge-base 0b87bc47 master` are both `862ed2b7ace176a919ed7b3a49fe5e01a5744992`. The PR has one commit. The timeline events are `committed`, `review_requested`, `reviewed`, `merged` and `closed`, with no `head_ref_force_pushed`.
- Landed as `7f6207fae2386d747347199936d56a105cbdf557` (parent `5dd34275dcbb485de2f6f7ce5d52242237c191f3`). `git diff 0b87bc47 7f6207fae -- lib/batcher` is empty.
- Manifest (`git diff --numstat 862ed2b7 0b87bc47`): `lib/batcher/batcher.go` +6/-0 and `lib/batcher/batcher_test.go` +89/-0.
- Closes #9687, "batcher: Commit can be admitted after the shutdown marker". Licence MIT (`gh api repos/rclone/rclone/license` → `MIT`).
- The change (line numbers are for `batcher.go` at head):
  - It adds `admitMu sync.Mutex` (line 50).
  - `Commit` locks it at line 267 and unlocks on the closed early return (line 270) or after the `b.in <-` send (line 281). The sync-mode `<-resp` wait (line 286) is outside the lock.
  - `Shutdown` locks it at line 243, around `close(b.closed)` (line 245) and the quit-marker send (line 251), and unlocks at line 252, before `b.wg.Wait()`.

## Verdict

adjudicated clean

## Defect register

none

**Why it is clean.** `commitLoop` (lines 189–231) is the only reader of `b.in`, and it never takes `admitMu`. It exits only when it receives `quit`. The quit marker is sent only by `Shutdown` while it holds `admitMu`, directly after `close(b.closed)`.

Take any `Commit` that passed the closed check. It holds `admitMu` until its send has completed, so its request is in the FIFO `b.in` before the marker. `commitLoop` therefore reads it before `quit`, and commits it either in-loop or in the post-loop `if len(requests) > 0 { commit() }` (lines 228–230). `Shutdown` waits on `b.wg` until that has happened.

Any `Commit` that takes `admitMu` after `Shutdown` has released it sees `closed` and returns `FatalError("batcher is shutting down")`. There is no third case.

The only lock-holder that blocks is a sender on a full `b.in`. That wait ends when `commitLoop` makes progress, and `commitLoop` never waits on the lock. So the lock adds no cycle. It also adds no wait that `Shutdown` did not already have at the merge-base: there, `Shutdown` blocked on the same full-channel send.

Neither backend's `commitBatch` (`backend/dropbox/dropbox.go`, `backend/googlephotos/googlephotos.go`) calls back into the batcher. `git grep` of their `commitBatch` bodies finds no `batcher`, `Commit(` or `Shutdown`.

## Reproduction

Environment: go1.26.5 linux/amd64, with `GOFLAGS=-mod=readonly GOPROXY=off`. Modules were already in `~/go/pkg/mod`, and `go list -deps -test ./lib/batcher` took 0.2 s at head. I used detached worktrees `work/head` (0b87bc47) and `work/base` (862ed2b7) of a clone of `/home/jack/.t3/bench-cache/staging/rclone.git`. The first block ran with `chmod -R a-w` on both worktrees.

| Rev | Command | Exit | Wall | Result |
|---|---|---|---|---|
| head | `go vet ./lib/batcher` | 0 | 0.9 s | clean |
| head | `go test -count=1 ./lib/batcher` | 0 | 5.1 s | `ok 4.319s` |
| head | `go test -race -count=5 ./lib/batcher` | 0 | 24.2 s | `ok 22.608s` |
| head | `go test -count=1 -run TestBatcherCommitRacingShutdown -v ./lib/batcher` | 0 | 0.7 s | sync and async PASS |
| base | `go vet ./lib/batcher` | 0 | 0.6 s | clean |
| base | `go test -count=1 ./lib/batcher` | 0 | 4.7 s | `ok 4.120s` |
| base | `go test -race -count=5 ./lib/batcher` | 0 | 22.8 s | `ok 21.615s` |
| base | same `-run TestBatcherCommitRacingShutdown` | 0 | 0.4 s | no tests to run (the test does not exist at base) |

`git status --porcelain` was empty in both worktrees after these runs.

Scratch checks I wrote and ran myself. The files are in `work/scratch/` and the logs are `stress-*.log` and `fullqueue-*.log`. I copied each test into a worktree, ran it, and deleted it afterwards.

1. **The head's regression test against merge-base code.** I extracted the base with `git archive 862ed2b7` into `scratch/mb-overlay` and overlaid the head's `batcher_test.go`. Then I ran `go test -count=1 -run TestBatcherCommitRacingShutdown -v ./lib/batcher`: exit 1 in 4 s. It fails with `commit hung while racing shutdown` (sync) and `accepted commit was dropped during shutdown` (async). The test detects the #9687 defect, which matches ncw's review statement.
2. **Stress, `zz_adjudication_test.go` `TestAdjudicationStress`.** Each iteration runs 8 concurrent `Commit`s against one `Shutdown`, with batch size 2, a 1 ms timeout, 2000 iterations, both modes, and with and without the commit function blocking the first batch so that `b.in` is full while senders and `Shutdown` contend. It asserts that nothing hangs (10 s deadline), that every error is "batcher is shutting down", and that every nil-returning `Commit` was committed.
   - Head: exit 0 in 83 s. All 4 configurations pass over 8000 iterations. Accepted/rejected counts per config: 112/15888, 661/15339, 130/15870, 846/15154. So the accept path, including accepts while the queue was full, was exercised.
   - Base: exit 1 in 21 s. All 4 configurations fail: `HANG: a Commit never returned` (sync, with and without a full queue) and `DROPPED: item-N accepted (nil error) but never committed` (async, with and without a full queue).
   - The ★ objections below (deadlock, hang with a full queue, dropped items) are therefore contradicted at head, and the defect the PR fixes is real at base.
3. **Full queue with a stalled loop, `zz_fullqueue_test.go` `TestAdjudicationFullQueue`.** Async mode, size 1. The commit function blocks. Item a is in the commit, b fills the buffer, and c (context already cancelled) blocks on the send. Then `Shutdown` starts, then a late `Commit` d.
   - Head (exit 0, 2 s): before release, c, d and `Shutdown` are all blocked. After release, `Shutdown` returns, c gets `nil` and is admitted, and d gets `batcher is shutting down`.
   - Base (exit 0, 2 s): before release, c and `Shutdown` are blocked, but d returns `batcher is shutting down` at once. After release, `Shutdown` returns and c gets `nil`.
   - `Shutdown` blocks equally at both revisions, and the cancelled caller blocks equally at both, so that behaviour is pre-existing. The one behavioural difference is that during shutdown with a full queue, a *late* `Commit` is rejected only after the blocked sender's send completes, instead of immediately. That delay is bounded by one batch commit. See the not-ground-truth entries on this below.

Cleanliness window: 2026-08-01T11:29:45Z → 2026-09-28 (58 days).
- `git log 7f6207fae..master -- lib/batcher` (master `9dc8b71ae`, committed 2026-09-26) returned nothing. `git diff --stat 7f6207fae master -- lib/batcher` is empty.
- `gh api search/issues` queries:
  - `repo:rclone/rclone batcher created:>=2026-07-31` → #9929, #9712, #9713.
  - `repo:rclone/rclone 9699` → only #9699 and an unrelated 2019 issue, #3129.
  - `admitMu` → none.
  - `"batcher is shutting down"` → #8068, #6409, #9687 and #9690, all created before the merge.
  - `batcher deadlock` → none.
  - `"lib/batcher" updated:>=2026-08-01` → #9929, #9699, #9687 and an unrelated #9355.
- #9712 and #9713 are dropbox context PRs. #9929 (pentaoa, 2026-09-16) is open with 0 reviews and 0 comments. It touches `lib/batcher` to honour ctx while waiting to enqueue: the pre-existing #7025/#9690 issue, not a report against this change.
- No revert, fix or bug report against the change exists in the window.

## Not ground truth

A correct review must not assert any of these as a material defect.

1. ★ **"Commit holds `admitMu` across a blocking channel send, so it deadlocks with Shutdown or the commit loop."** False. `commitLoop` never takes `admitMu` and drains `b.in` until it sees `quit`. `quit` can only be enqueued under `admitMu`, so it is behind every admitted request. A blocked sender waits only on loop progress. Stress (2) with a full queue: no hang over 4000 iterations at head.
2. ★ **"Shutdown holds `admitMu` while sending the quit marker into a possibly full channel, so Shutdown and Commits hang."** False. The loop drains, and waiting Commits then see `closed` and return FatalError. `Shutdown` blocked on a full `b.in` at the merge-base too (check 3). The vetting claim that there is "no new wait" is overstated: late *Commit* callers now wait for the lock instead of failing fast (item 7). `Shutdown`'s own wait is unchanged.
3. ★ **"Items admitted just before shutdown are dropped (async uploads that returned nil are lost), or sync callers hang."** False at head, true at base. That is exactly what the PR fixes. `b.in` is FIFO, the marker follows every admitted request, the post-loop `commit()` flushes the remainder, and `Shutdown` waits on `b.wg`. Stress (2): zero drops or hangs at head, and both at base.
4. **"Serialising Commit through a mutex defeats batching or throughput."** False. The critical section is a non-blocking select, `fs.Debugf`, `make` and a send into a channel buffered to `opt.Size`. The sync-mode `<-resp` wait (line 286) is after `Unlock`, so concurrent callers still share a batch. Senders onto a full channel were already serialised by the channel itself.
5. **"Unlock is not deferred, so the lock leaks on some path."** False. Both exits unlock (lines 270 and 281), and nothing between Lock and Unlock can panic in normal operation. Using `defer` would be wrong anyway: it would hold the lock across the sync `<-resp` wait and serialise batches. Style only.
6. **"A cancelled ctx is ignored while blocked, and the cancelled caller now holds `admitMu` and delays shutdown."** The ctx part is true but pre-existing: #7025 (2023) and #9690, which ncw closed as a duplicate on 2026-07-30 and described as "bounded (idle timeout + commit duration), so this is slow cancellation, not a hang". Check 3 shows the cancelled caller and `Shutdown` block identically at base and head. The follow-on #9929 addresses it and is unreviewed. It is not introduced by this PR.
7. **"During shutdown with a full queue, a late Commit now blocks on `admitMu` instead of failing fast with 'batcher is shutting down'."** True (check 3), but not material. The wait is bounded by the blocked sender's send, which is one batch commit, and that is the same thing `Shutdown` itself waits on at both revisions. The caller still gets the same FatalError, or is admitted and committed. No data loss, hang or contract violation results.
8. **"`sync.Mutex` is unfair, so Commits can starve Shutdown and keep being admitted after shutdown began."** Not a defect. Go's mutex enters starvation mode after a waiter waits 1 ms (`starvationThresholdNs = 1e6` in `internal/sync/mutex.go`) and hands off FIFO. Any Commit that wins the lock before `Shutdown` is enqueued before the marker and committed, so it is correct, not lost.
9. **"Just use `select { case b.in <- req: case <-b.closed: }` or close `b.in` instead."** Not a defect in the PR, and both alternatives are worse. With both cases ready, a select picks one at random, so a request can still land after the marker. Closing `b.in` panics concurrent senders, which the existing comment at lines 247–250 already rules out.
10. **"Commit when batching is off now holds the mutex forever and blocks other callers."** Pre-existing misuse. The doc comment says "This should not be called if batching is off". With `opt.Size == 0` there is no `commitLoop`, and the unbuffered send already blocked forever at base. Both backends check `Batching()` first (dropbox.go:2121, googlephotos.go:1225).
11. **"Re-entrant Commit or Shutdown from the commit callback deadlocks on `admitMu`."** Hypothetical and pre-existing. Neither backend's `commitBatch` calls the batcher. A callback calling `Shutdown` would deadlock on `wg.Wait` at base anyway, and a callback `Commit` onto a full channel would block at base too.
12. **"`fs.Debugf` or logging I/O runs under the lock."** True and inconsequential. Formatting happens only at debug level, and the test deliberately exploits the pause. No measured cost.
13. **"The regression test is timing-based (100 ms, 1 s timeouts) and flaky."** Not a product defect. At head it passes whatever the timing, because Shutdown cannot pass the lock early. At base it could in principle pass spuriously if the Commit's send beats the quit send. It failed deterministically for me (check 1) and for ncw. Test hygiene at most.
14. **"The test mutates the global `ci.LogLevel`, which is racy or not parallel-safe."** `-race -count=5` passes at head. The test is not `t.Parallel()`. The write happens before the goroutines that read it are started or released, which gives a happens-before edge through channel operations. The level is restored so that `Shutdown`'s `fs.Infof` does not call the blocking `String()`.
15. **"The test reads the unexported `b.closed` field."** It is an in-package test (`package batcher`). Fine.
16. **"Shutdown calls `atexit.Unregister` and `fs.Infof` outside the lock, or holds the lock across a potentially long send."** The ordering is unchanged from base except for the lock. Holding it across the send is the point of the fix: it makes marker insertion atomic with closing admission.

## Preexisting hints

Every packet contains the review record up to the merge instant:
- ncw's review on #9699 (APPROVED, 2026-08-01T11:28:37Z): "Nice fix - thank you :-) The `blockingStringer` trick to pause `Commit` deterministically between the closed-check and the send is neat. I verified the test does its job by running it against the unfixed code." This supports the change. Nobody raised any of the tempting objections.
- ncw's comment on #9687 (2026-07-30T16:28:26Z), if the issue thread is in the packet: "Confirmed, and reproduced ... a `Commit` that passes the closed-check just before `close(b.closed)` but whose send lands after the quit marker is accepted into the channel and never read. In sync mode the caller blocks forever; in async mode the upload is silently dropped. ... Affects dropbox and google photos." This describes the defect the PR fixes, not a defect in the PR.
- The #9687 body poses the design question: "Should admission and insertion of the shutdown marker be serialized so every accepted request is either processed or explicitly rejected?" The PR's mutex answers it.
- No participant gestured at deadlock, lock-held send, batching throughput or ctx concerns before the cutoff.

## Leakage

A truncated mirror must exclude:
- `7f6207fae2386d747347199936d56a105cbdf557`: the landed commit ("... - fixes #9687"). Its message and position on master reveal acceptance.
- `5dd34275dcbb485de2f6f7ce5d52242237c191f3` (its parent), and every master commit not reachable from merge-base `862ed2b7`. That is 43 commits in `862ed2b7..5dd34275` and 398 in `862ed2b7..master` at tip `9dc8b71ae99496460f07373674609571918bfb9c`, including the tip itself. The mirror should hold only the ancestry of `862ed2b7` plus the head `0b87bc47`. There are no later PR branch heads (no force-pushes).

Issues and PRs whose content leaks the answer or post-dates the cutoff:
- #9929: the open follow-on on the admission lock and ctx. It names the "admission lock" and the shutdown-delay concern.
- #9690 and #7025: the pre-existing ctx issue. ncw's #9690 note rules on the bounded-wait semantics.
- #9711 and #9689: the sibling vfs shutdown-race fix by the same author from the same batch of reports. Low direct relevance, but it reveals the maintainer's acceptance pattern.
- #9699's own merged state and the post-merge closure of #9687 (closed 2026-08-01T11:29:46Z).
- #9687's body is the originating issue and belongs in the packet.

## Confidence and limits

Confidence: high that the change is clean.
- The production diff is 6 lines, and I read the full lifecycle (`New`, `commitBatch`, `commitLoop`, `Shutdown`, `Commit`) at head.
- The head's regression test fails at base and passes at head.
- My independent stress test found hangs and drops at base in all 4 configurations, and none at head over 8000 iterations, including with a full queue.
- `-race -count=5` is clean at head.
- Nothing has touched `lib/batcher` in the 58 days since the merge, and no report cites the change.

Limits:
- Stress testing samples interleavings and cannot enumerate them. The no-deadlock and no-drop argument above is static reasoning over the only reader of `b.in`, and the tests support it.
- The stress run at head was not repeated under `-race`, only the package suite was.
- The late-Commit rejection delay (item 7) is ruled non-material because it is bounded and has no loss or hang. A benchmark operator who treats shutdown fail-fast latency as a requirement could argue otherwise. No rclone document states such a requirement.
- The vetting pass's statement that "Shutdown also blocked on a full b.in before this change, so there is no new wait" is correct for `Shutdown` but overstated for late Commit callers (check 3).
- #7025 is closed (2023-06-28), even though ncw's #9690 comment says the ctx fix "will be tracked there". This has no bearing on the ruling.
- I verified the vetting pass's other factual claims (metadata, manifest, merge-base agreement, review text, search results, the base failure of the regression test) and found them correct.
