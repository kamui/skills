# Hunt (t): clean change in high-risk code

## Inventory (in order examined)

| # | Repository | PR | Merged | Lines / files | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 | E10 | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | authelia/authelia | #12620 | 2026-08-02T16:01:12Z | 204 / 3 (+196/-8; prod +4/-8) | pass | pass (57 days) | pass | not run | pass | not run | pass | n/a | **fail**: not genuinely clean on my own reading | pass (Apache-2.0) | Removes `RLock` held across `Save()` (snapshot+`os.WriteFile`). `FileUserProvider.UpdatePassword/ChangePassword` do `SetUserDetails` then `Save` with no serialising lock (p.mutex only guards `setTimeoutReload`). After the change two concurrent updates can snapshot in order A,B but write B then A (lost update; A's shorter write over B's O_TRUNC'd longer write can leave a torn YAML file). Before, the RLock blocked the writer until the prior Save's write finished, so overlapping Saves wrote identical content. A real (narrow) regression, so dropped. Follow-ups on the path (#12704, #12755) fix other code. |
| 2 | rclone/rclone | #9699 | 2026-08-01T11:29:45Z | 95 / 2 (+95/-0; prod +6/-0) | pass | pass (58 days) | pass (numstat on full clone) | pass (rc=0, default cutoff = merge instant, 0 omissions) | pass (1 native review by ncw) | pass (go vet/test/-race at head and merge-base, clone `chmod -R a-w`, all rc=0, tree clean) | pass | n/a | pass (no commits to lib/batcher after merge; only related open PR #9929 is unreviewed and targets the pre-existing ctx issue #7025/#9690) | pass (MIT) | **Recommended.** Adds `admitMu` serialising `Commit` admission with `Shutdown`'s close+quit marker. |
| 3 | rclone/rclone | #9711 | 2026-08-01T11:44:43Z | 225 / 3 (+206/-19; prod +43/-19) | pass | pass (58 days) | pass | pass (rc=0, default cutoff, 0 omissions) | pass (1 native review by ncw) | pass (go vet, focused, -race, full `./vfs` at head and merge-base, clone `chmod -R a-w`, all rc=0, tree clean) | pass | n/a | pass (later vfs/vfs.go commits c62aa2adc, 1dab0f3ab, ebb1cc122, 30e79a017 fix or test other code; `setPollInterval`/`getStatus`/`Shutdown` poll block unchanged on master) | pass (MIT) | **Alternate.** Adds `VFS.pollMu`; `Shutdown` cancels ctx before closing `pollChan` under the lock. |

Screening only (listed via `gh pr list --search merged:2026-07-01..2026-08-03` and dropped on title or size without opening): etcd-io/bbolt, jackc/pgx, caddyserver/caddy, restic/restic, syncthing/syncthing, dexidp/dex, ory/fosite (no hits), pocketbase (no hits), coredns/coredns, go-git/go-git. None was opened after rclone gave two passing candidates. E1 check: `rg` over `used-pull-requests.txt` finds no entry for rclone, authelia, coredns, dex, go-git, caddy, syncthing or restic.

## Recommendation

Primary: **rclone/rclone#9699**. Alternate: **rclone/rclone#9711**. Both pass E1–E10. The search covered merges from 2026-07-01 to 2026-08-03, so both fall in the preferred window.

---

### Primary: rclone/rclone#9699, "lib/batcher: prevent commits racing shutdown"

- Author `lntutor`. Opened 2026-07-30T17:06:34Z. Merged **2026-08-01T11:29:45Z** by `ncw` into `master` (rebase-merge, landed as `7f6207fae2386d747347199936d56a105cbdf557`). Licence MIT (`COPYING`; `gh api repos/rclone/rclone/license` → MIT).
- Head `0b87bc4788cd50664b82dd7e74c78aa2c7fc3b1c`. PR-recorded base `862ed2b7ace176a919ed7b3a49fe5e01a5744992`. On a full clone, `git merge-base 0b87bc47 origin/master` returns `862ed2b7ace176a919ed7b3a49fe5e01a5744992`, so the two **agree**. The PR has a single commit and no force-pushes in its timeline.
- Manifest (`git diff --numstat` merge-base..head): `lib/batcher/batcher.go` +6/-0 and `lib/batcher/batcher_test.go` +89/-0. Total 95 lines in 2 files.
- Originating issue: #9687, "batcher: Commit can be admitted after the shutdown marker" (MikeeI, 2026-07-28, closed by the merge).
- Review record up to the merge: one native review, `ncw` APPROVED at 2026-08-01T11:28:37Z: "Nice fix - thank you :-) The `blockingStringer` trick to pause `Commit` deterministically between the closed-check and the send is neat. I verified the test does its job by running it against the unfixed code." There are no inline threads and no conversation comments. Nobody raised any of the tempting objections.

**The change.** It adds `admitMu sync.Mutex`. `Commit` takes it before the `<-b.closed` check and releases it after the (possibly blocking) `b.in <- request` send, or on the early-return path. `Shutdown` takes it around `close(b.closed)` plus the `b.in <- {quit:true}` send, then releases it before `b.wg.Wait()`.

**Surfaces a correct review must NOT flag as defects.** The ones marked ★ are the ones a reviewer would most likely call blocking.
1. ★ **"Commit holds a mutex across a blocking channel send, so it can deadlock with Shutdown or the commit loop."** This is false. `commitLoop` never takes `admitMu` and keeps draining `b.in` until it receives the quit marker. The marker can only be enqueued by `Shutdown` while it holds `admitMu`, so it is always behind every admitted request. A blocked sender therefore always makes progress. Hops: `commitLoop`, `Shutdown`.
2. ★ **"Shutdown holds admitMu while sending the quit marker into a possibly full buffered channel, so Commits and Shutdown hang."** This is false for the same reason: the loop drains. Any Commit waiting on the mutex then sees `closed` and returns `FatalError("batcher is shutting down")`. `Shutdown` also blocked on a full `b.in` before this change, so there is no new wait.
3. ★ **"Items admitted just before shutdown are dropped, especially async uploads that already returned nil."** This is false. `b.in` is FIFO and the quit marker is strictly after every admitted request. After `break outer`, `commitLoop` runs `if len(requests) > 0 { commit() }`, and `Shutdown` waits on `b.wg`.
4. **"Serialising Commit through a mutex defeats batching."** This is false. The critical section is a non-blocking select plus a send into a channel buffered to `opt.Size`. In sync mode the wait `<-resp` happens after `Unlock`, so concurrent callers still land in the same batch.
5. **"Unlock isn't deferred, so it leaks on some path."** This is false. Both exits (the closed early return and the fall-through after the send) unlock. The only code between Lock and Unlock is a select, `fs.Debugf`, `make` and a send. Style only.
6. **"The ctx argument is ignored while blocked, and a cancelled caller now holds admitMu."** This is true but pre-existing (#7025 from 2023, #9690 closed by ncw as a duplicate on 2026-07-30). Before the change the same caller blocked on the same send, and the other senders and `Shutdown` blocked on the full channel. The PR is not the cause.

**At least three tempting false positives with reasons:** items 1, 2 and 3 above, plus 4.

**Cleanliness evidence (window 2026-08-01 → 2026-09-28, 58 days):**
- `git log 7f6207fae..origin/master -- lib/batcher` (master tip `9dc8b71ae`, 2026-09-26) returns no commits. `git diff --stat 7f6207fae origin/master -- lib/batcher` is empty, and the head tree equals the landed tree for `lib/batcher`.
- Search queries (REST `search/issues`): `repo:rclone/rclone batcher created:>=2026-07-31` returned #9929, #9712 and #9713. #9712 and #9713 are dropbox context PRs that do not touch `lib/batcher`. #9929, "lib/batcher: honor context cancellation while waiting to enqueue", is **open with no reviews or comments** (pentaoa, 2026-09-16). It addresses the pre-existing ctx issue (#7025/#9690) and is not maintainer-accepted. `repo:rclone/rclone 9699` found only the PR itself. `repo:rclone/rclone admitMu` returned nothing. `"batcher is shutting down"` found only older issues and #9687/#9690.
- Nothing in that window fixes, reverts or reports the change.

**Provisioning and test evidence (run by me):**
- Clone: `git clone https://github.com/rclone/rclone.git` took 10 s (full clone). Then `git fetch origin pull/9699/head`.
- Provisioning at head: `go list -deps -test ./lib/batcher` took 0.7 s and downloaded 8 modules into `~/go/pkg/mod`, outside the clone. `GOCACHE=~/.cache/go-build` is also outside the clone.
- The focused commands ran with `chmod -R a-w` on the clone, `GOFLAGS=-mod=readonly GOPROXY=off`, go1.26.5 linux/amd64.

| Revision | Command | Exit | Time | Output |
|---|---|---|---|---|
| head 0b87bc47 | `go vet ./lib/batcher` | 0 | 6.2 s | clean |
| head | `go test -count=1 ./lib/batcher` | 0 | 6.0 s | ok 4.32 s |
| head | `go test -race -count=5 ./lib/batcher` | 0 | 32.3 s | ok 22.6 s |
| head | `go test -count=1 -run TestBatcherCommitRacingShutdown -v ./lib/batcher` | 0 | 0.7 s | sync and async subtests PASS |
| merge-base 862ed2b7 | `go vet ./lib/batcher` | 0 | 0.3 s | clean |
| merge-base | `go test -count=1 ./lib/batcher` | 0 | 4.6 s | ok 4.12 s |
| merge-base | `go test -race -count=5 ./lib/batcher` | 0 | 22.2 s | ok 21.6 s |

- `git status --porcelain` was empty after each read-only run, so the tracked tree stayed clean. **E6 read-only requirement: pass.**
- Extra check: I exported the merge-base with `git archive` into `scratch/rclone-mbtest`, outside the clone, and overlaid the head's `batcher_test.go`. `go test -run TestBatcherCommitRacingShutdown ./lib/batcher` then fails, as it should: `sync: commit hung while racing shutdown` and `async: accepted commit was dropped during shutdown`.

**E4:** exit 0. Cutoff was the default, the merge instant 2026-08-01T11:29:45Z. Omissions: reviews 0, thread_comments 0, conversation 0, issue_comments 0. The packet has 2 files, 1 commit, 1 review and 1 issue.

**Leak set:**
- SHAs: the landed commit `7f6207fae2386d747347199936d56a105cbdf557`, and every master commit after merge-base `862ed2b7` that is not on the PR branch. That includes `5dd34275dcbb485de2f6f7ce5d52242237c191f3` (the landed parent) and all later master history. The truncated mirror should hold only the merge-base ancestry plus head `0b87bc47`. There were no later PR branch heads.
- Numbers: #9929 (open follow-on PR on the admission lock and ctx), #9690 and #7025 (ctx discussion, including ncw's note on the batcher's design), and #9711 and #9689 (the sibling race fix by the same author). #9687 is the originating issue and belongs in the packet, not the leak set.

**Confidence: high.** The production diff is 6 lines, and I checked the full lifecycle (`New`, `commitLoop`, `Shutdown`, `Commit`) at head. The maintainer confirmed the regression test against unfixed code, and I reproduced both failures myself. The race suite passes 5× at head. Nothing has touched the file in 58 days. The residual risk is that the production change is small, so the tempting surface sits in about 10 lines plus two one-hop callees. It is enough for the ★ objections but narrow.

---

### Alternate: rclone/rclone#9711, "vfs: synchronize poll updates with shutdown"

- Author `lntutor`. Opened 2026-07-31T07:02:51Z. Merged **2026-08-01T11:44:43Z** by `ncw` into `master` (rebase-merge, landed as `f132aef29`, `d5275c4eb` and `1d03a7717`). Licence MIT.
- Head `fe0ec001e81d2d3d8991cee5ac7401421c0c57d8`. PR-recorded base `92fbc85f108bcb5a990c947025b15216fea6f5a5`. The computed `git merge-base` is `92fbc85f108bcb5a990c947025b15216fea6f5a5`, so they **agree**. The PR commits are `89df254d33d6`, `0b83554c83fa` and `fe0ec001e81d`.
- Manifest: `vfs/rc.go` +37/-16, `vfs/rc_test.go` +163/-0, `vfs/vfs.go` +6/-3. Total 225 lines in 3 files.
- Originating issue: #9689, "vfs: poll interval update can race with VFS shutdown" (MikeeI, 2026-07-28, closed by the merge).
- Review record: one native review, `ncw` APPROVED at 2026-08-01T11:44:33Z: "Thank you for these fixes - they look correct to me." No threads or comments. No objections were raised.

**The change.** It adds `VFS.pollMu`. The new `setPollInterval` holds the lock while it checks `vfs.ctx.Err()` and `pollChan != nil`, then selects on `pollChan <- interval`, a timeout and `vfs.ctx.Done()`. `getStatus` and the unsupported check both lock. `Shutdown` now calls `vfs.cancel()` first, then closes and nils `pollChan` under `pollMu`.

**Surfaces a correct review must NOT flag:**
1. ★ **"setPollInterval holds pollMu across an indefinite channel send (timeout ≤ 0 is the default), so Shutdown's `pollMu.Lock()` deadlocks."** This is false. `Shutdown` calls `vfs.cancel()` *before* taking the lock, and the send's select includes `<-vfs.ctx.Done()`. `vfs.ctx` comes from `context.WithCancel` in `New`.
2. ★ **"close(pollChan) can still race a sender and panic with a send on a closed channel."** This is false. Both the send and the close happen under `pollMu`, and a sender that acquires the lock after shutdown sees `ctx.Err() != nil` or `pollChan == nil` first.
3. ★ **"getStatus now locks pollMu and is called from rcPollInterval right after setPollInterval, so it self-deadlocks."** This is false. `setPollInterval` releases the lock through `defer` before it returns, and the `!intervalPresent` path unlocks explicitly before calling `getStatus`.
4. **"New writes `vfs.pollChan` and does the initial send without pollMu."** This is false as a race. `New` holds `activeMu` for its whole body (`defer activeMu.Unlock()`), and `getVFS` in `rc.go` needs `activeMu` to find the VFS, so no rc call can see it before `New` returns.
5. **"Moving `vfs.cancel()` before the close changes backend ChangeNotify teardown."** Both signals still fire. A backend loop exits on either one, and closing a channel with no reader is safe.
- A true-but-intended surface: a status query now waits behind an in-flight update. The PR body states the handler "holds a VFS-local mutex while checking and sending on the poll interval channel". The wait is bounded by the backend poll loop accepting the send, or by shutdown. At most a non-blocking remark.

**Cleanliness evidence (2026-08-01 → 2026-09-28):**
- `git log --since=2026-07-31 origin/master -- vfs/rc.go vfs/vfs.go vfs/rc_test.go` shows `c62aa2adc` (VFS reuse during shutdown, in `New`'s active-cache loop), `1dab0f3ab` (adds `Hold`), `ebb1cc122` (`AddVirtual` isDir) and `30e79a017` (adds `ActiveCount`). None of them touches the poll code. `git diff 1d03a7717 origin/master -- vfs/rc.go vfs/rc_test.go` is empty, and the `vfs.go` diff has no poll-related lines.
- Searches: `poll-interval created:>=2026-07-31`, `9711`, `pollMu` and `"VFS is shutting down"` found no fix or report attributable to the change. #9714 (merged 2026-08-18) is a VFS leak fix in mount/serve that does not touch the poll path.

**Test evidence** (clone `chmod -R a-w`, `GOFLAGS=-mod=readonly GOPROXY=off`). Provisioning was `go list -deps -test ./vfs`, rc 0, 9 s.

| Revision | Command | Exit | Time |
|---|---|---|---|
| head | `go vet ./vfs` | 0 | 19.7 s |
| head | `go test -count=1 -run TestRcPoll -v ./vfs` | 0 (4 subtests PASS) | 4.6 s |
| head | `go test -race -count=3 -run 'TestRc\|TestVFSNew\|TestVFSShutdown' ./vfs` | 0 | 27.8 s |
| head | `go test -count=1 ./vfs` | 0 | 18.3 s |
| merge-base | the same four | all 0 | 1.4 s / 2.5 s / 5.4 s / 18.1 s |

The tracked tree stayed clean (`git status --porcelain` empty), and fstest remotes go to the system temp dir. **E6 read-only requirement: pass.** The new tests are white-box (`vfs.pollMu`, `setPollInterval`), so they do not compile against the merge-base (`vfs.pollMu undefined`). I could not demonstrate a red run at the merge-base. The PR body reports a race-detector failure and a `send on closed channel` panic on unmodified master.

**E4:** exit 0. Default cutoff 2026-08-01T11:44:43Z. Omissions: 0 reviews, 0 thread comments, 0 conversation, 0 issue comments. The packet has 3 files, 3 commits, 1 review and 1 issue.

**Leak set:** the landed commits `f132aef29`, `d5275c4eb` and `1d03a7717`, plus all master history after merge-base `92fbc85f` (including `c62aa2adc` and `1dab0f3ab`); no later PR heads. Numbers: #9714, #9699 and #9687 (the sibling), and #9929.

**Confidence: medium-high.** The mechanism is sound and the tests pass read-only at both revisions. It ranks below #9699 because the status-query blocking is a real (intended) behaviour change a reviewer might note, and because I could not reproduce a red run at the merge-base.

---

### Closest miss

- **authelia/authelia#12620** (inventory #1) fails the "genuinely clean" bar. Removing the `RLock` in `FileUserDatabase.Save` means `ToDatabaseModel()` and `FileDatabaseModel.Write` no longer run as a unit against writers. `FileUserProvider.UpdatePassword` and `ChangePassword` call `SetUserDetails` and then `Save` with nothing serialising them (`p.mutex` only guards `setTimeoutReload`). Two concurrent password updates can therefore write their snapshots out of order, losing an update, or leave a torn YAML file (two `os.WriteFile` calls with O_TRUNC and different lengths). This is my own reading, with no upstream report. It is still disqualifying, because the slot requires no material defect.
