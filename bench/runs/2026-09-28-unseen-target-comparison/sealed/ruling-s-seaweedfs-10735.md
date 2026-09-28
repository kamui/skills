# Ruling: s-seaweedfs-10735

## Target

- `seaweedfs/seaweedfs#10735`, "fix(redis2): remove orphaned directory index members on listing", by `petedodd-pd`. Squash-merged 2026-08-13T17:53:33Z as `f7ae2d4dd5f08826606f50761e8d7dc6f5a7ce3b`.
- Reviewed head: `6c8fde6642cd428e884cc9c9d88c9aaa189c4bf1`. PR-recorded base and computed `git merge-base`: both `db5a086d048c5c2d6e51e82bb070d20df04d688d`. The head equals the PR's final `headRefOid` (from `gh pr view`).
- Commits: `9f9962800` (the cleanup), then `6c8fde664` (`EXISTS` re-check plus `ZAddNX` restore).
- Manifest (`git diff --numstat db5a086d 6c8fde66`):
  - `weed/filer/redis2/universal_redis_store.go`: +17/-0
  - `weed/filer/redis2/universal_redis_store_test.go`: +143/-0
- Slot: (s), unintended data loss.

## Verdict

1 material defect

## Defect register

### GT-s1: The cleanup trusts replica-routed reads, so it permanently de-indexes live entries under `redis_cluster2` replica reads

**Location at the head.** File `weed/filer/redis2/universal_redis_store.go`:
- `ListDirectoryEntries` (l.176) calls `store.removeOrphanedDirectoryListMember(ctx, dirListKey, path, fileName)` (l.208) whenever `FindEntry` returns `filer_pb.ErrNotFound`. `FindEntry` (l.97-102) is a plain `GET`, and `redis.Nil` maps to `ErrNotFound`.
- `removeOrphanedDirectoryListMember` (l.237-251) does:
  - `ZRem` on the index (l.238);
  - then `Exists` on the value key (l.245);
  - and returns without restoring when `Exists` reports 0 (l.246-247). Otherwise it calls `ZAddNX` (l.250).

**Violated contract.** The PR body says:
- "Only a positively confirmed absent value leaves the member removed."
- "The compensating form uses only single-key commands and behaves identically on all three transports."

The configured transports break both statements:
- `RedisCluster2Store` embeds `UniversalRedis2Store`.
- `redis_cluster_store.go:40-41` reads `useReadOnly` and `routeByLatency`, and l.53-54 passes them as `redis.ClusterOptions{ReadOnly, RouteByLatency}`.
- The scaffold `weed/command/scaffold/filer.toml:287-290` (`[redis_cluster2]`, l.269) says "allows reads from slave servers or the master, but all writes still go to the master" and "automatically use the closest Redis server for reads".
- go-redis v9.21.0 `osscluster.go`:
  - l.62-64: RouteByLatency "automatically enables ReadOnly".
  - l.205-206: `opt.ReadOnly = true` when `RouteByLatency || RouteRandomly`.
  - l.2399-2405, `cmdNode`: a read-only-flagged command (`GET`, `EXISTS`, `ZRANGEBYLEX`) goes to `slotReadOnlyNode`, which is `slotClosestNode` under RouteByLatency and a slave otherwise. Writes (`ZREM`, `ZADD`) go to `slotMasterNode`.

Under these options, neither the `GET` nor the `EXISTS` is an authoritative check that the value is absent.

**Trigger.**
1. A `redis_cluster2` filer runs with `routeByLatency = true` (a documented scaffold key) or `useReadOnly = true`.
2. `InsertEntry("/d/f")` issues `SET` on the master of the value key's slot, then `ZADD NX` on the index key's master. The keys `<prefix>/d/f` and `<prefix>/d\x00` carry no hash tag, so they normally live in different slots with independent replication lag.
3. A listing of `/d` sees member `f` (its index replica is current). `GET /d/f` goes to the value slot's closest node, a replica that has not yet applied the `SET`, and returns nil.
4. `ZREM` removes `f` on the master. `EXISTS /d/f` goes to the same lagging replica and returns 0, so the helper returns without `ZAddNX`.

**Demonstrated consequence.**
- The live entry's member is permanently gone from the persisted directory index. It stays gone after the replica catches up:
  - `FindEntry` still finds the value, but no listing of `/d` shows it.
  - Overwrites don't heal it. `Filer.CreateEntry` on an existing path goes to `Filer.UpdateEntry` → `store.UpdateEntry` → `doInsertEntry` (`SET` only, l.92-95), which never re-adds the member.
  - `DeleteFolderChildren("/d")` (l.145-170) iterates members only, so a recursive delete of `/d` leaks the value key.
  - If `f` is a directory, its whole subtree becomes unreachable by listing from the parent.
- At the merge-base, the same stale read costs only a one-listing miss.
- My reproduction (below) shows exactly this at the head, and convergence at the merge-base.
- Maintainer confirmation, #10745 (`chrislusf`, merge `0481f712b1c4`): "an insert lands on the master, a listing's `GET` hits a replica that has not applied it yet, the not-found branch fires, the `ZREM` removes the live member on the master — and the compensating `EXISTS` asks the same lagging replica, gets 0, and skips the restore. The entry vanishes from every listing until it is re-inserted. Before the cleanup existed, that same stale read cost a transient one-page miss, not a lost index member."

**Required corrective outcome.**
- A listing-triggered cleanup may leave a directory-index member removed only after confirming that the value key is absent on an authoritative view: the key's master, or any read that cannot be served by a lagging replica.
- Any sufficient fix must keep live entries listed and reachable by `DeleteFolderChildren` under every supported `redis2` transport, including `redis_cluster2` with `routeByLatency` or `useReadOnly`.

Acceptable shapes include:
- a master-routed existence check (upstream uses a one-key Lua `EXISTS`, which go-redis always sends to the master);
- disabling the cleanup when replica reads are enabled;
- reading from the master for the triggering `GET`.

A fix that only re-orders commands or adds another replica-routed `EXISTS` is not sufficient.

**Intended or unintended.** Unintended. The PR promised the opposite: that a live entry is never left de-indexed.

**Static reachability.** It is reachable one hop from the diff, inside the same package. `redis_cluster_store.go` constructs the client that `UniversalRedis2Store` methods use, and the scaffold documents replica reads. Seeing it requires knowing that go-redis cluster routes read-flagged commands to replicas.

**Manifestations** (one defect, one corrective outcome):
- (a) A file entry's member is lost.
- (b) A directory entry's member is lost, which detaches its subtree from the parent listing and from recursive delete.
- (c) `GET` reads the lagging replica and `EXISTS` reads it too. There is no restore in either case.

## Reproduction

**Harness.** `probe/adjudication_probe_test.go` is an in-package test injected with `go test -overlay`, so the tracked trees stay untouched.
- It drives the real `UniversalRedis2Store` through a fake `redis.UniversalClient`:
  - writes (`SET`, `DEL`, `ZADDNX`, `ZREM`) go to a master map;
  - reads (`GET`, `EXISTS`, `ZRANGEBYLEX`) go to a replica map;
  - scripts (`EVALSHA`/`EVAL`, needed only by the #10745 tree) read the master.
- A key marked "lagging" doesn't replicate until it is released.
- No redis-server is installed, so the upstream gated tests (`RUN_REDIS_TESTS=1`) were not run.

**Command**, run in each worktree:
`GOCACHE=$WORK/gocache GOFLAGS=-mod=readonly GOPROXY=off go test -overlay ../probe/overlay-<tree>.json -count=1 -run TestAdjProbe -v ./weed/filer/redis2/`

Logs are in `runs/<tree>.log`. After the runs, `git status --porcelain` printed 0 lines in all four trees.

| Tree | Exit | Duration | ReplicaLag | SingleViewControl | RecreateRace (both interleavings) | DirectoryWithLiveChildren |
|---|---|---|---|---|---|---|
| head `6c8fde66` | 1 | 1.5 s warm (13.2 s cold, first run) | **FAIL** | PASS | PASS | FAIL (see Not ground truth) |
| merge-base `db5a086d` | 0 | 1.4 s (4.5 s first run) | PASS | PASS | PASS | PASS |
| #10743 `abd36cbf9` | 1 | 1.6 s | **FAIL** | PASS | PASS | PASS |
| #10745 `0481f712b` | 0 | 1.6 s | PASS | PASS | PASS | PASS |

**Probe outputs.**
- Head, `TestAdjProbeReplicaLag`:
  - "listing after catch-up and UpdateEntry: []"
  - "after DeleteFolderChildren(/d): value key "pfx:/d/f" still present=true"
  - "LIVE ENTRY LOST FROM INDEX: listing=[], index=map[], value present=true"
- Merge-base, same test:
  - "listing after catch-up and UpdateEntry: [f]"
  - the value is removed by `DeleteFolderChildren`.
- The single-view recreate race passes in both interleavings at the head: an insert between `GET` and `ZREM`, and an insert after `EXISTS`. The fix commit therefore closes the bot-flagged race on single-view transports.

**Harness note.** On the first pass, the #10745 tree failed `insert-after-exists`. The cause was the harness: the post-`EXISTS` hook was attached only to `Exists`, and #10745 routes the check through `EvalSha`. After I attached the hook to the script path too, that case passes. The head and merge-base results were identical on both passes.

## Not ground truth

1. **"Directory `/d/sub` whose value key is gone but whose child index `/d/sub\x00` is live has its member stripped" (#10743 item 4).** The mechanism is real and reproduced: the head strips `sub` and the merge-base keeps it. The material consequence the vetting claims does not hold against the merge-base:
   - `sub` is absent from the listing of `/d` in both trees, because `FindEntry` fails in both.
   - `ListDirectoryEntries("/d/sub")` still returns `child` at the head.
   - `DeleteFolderChildren` is one level deep (l.159-167), and filer recursion (`filer_delete_entry.go:83-98`) only descends into entries that listing returns. So `/d/sub/child`'s value leaks after a recursive delete of `/d` at the merge-base too. The probe prints "/d/sub/child value present=true" in both trees.
   - The only difference: the head also leaves the `/d/sub\x00` ZSET behind.
   - Any later write under `/d/sub/` re-attaches the directory in both trees: `ensureParentDirectoryEntry` → `InsertEntry` → `ZAddNX`.

   The state is already corrupt (eviction or an out-of-band `DEL`). The PR adds one leaked key and loses no live data. Ruling: **non-material**. An accurate report of it is `non-material`, not `false-finding`. A report that claims live data becomes lost or unlistable relative to the pre-PR code overstates the consequence. A directory that is live but read from a lagging replica is GT-s1(b), not this item.
2. **"Super-large directories: the PR's unreachability claim is wrong and the cleanup strips members irrecoverably" (#10743 item 2).**
   - The claim of unreachability is factually wrong for a directory added to `superLargeDirectories` after it accumulated members, because a legacy ZSET remains.
   - The cleanup only strips legacy members whose value is absent. Those are entries deleted after the conversion, and `DeleteEntry` skips `ZRem` for them (l.132-134).
   - Listing a super-large directory is unsupported by design: `filer.ErrUnsupportedSuperLargeDirectoryListing` (`weed/filer/filerstore.go:15`). The legacy index already omits every entry created after the conversion.

   Ruling: **non-material**, an accurate observation with no demonstrated consequence on a supported path.
3. **"Request cancellation or a client timeout can abandon the restore after `ZREM` landed" (#10743 item 3).**
   - This is true in principle. The helper uses the caller's `ctx`, and a `ZREM` error (l.238-239) returns without restoring.
   - Harm requires two coincidences: a concurrent same-path recreate inside the `GET`→`EXISTS` window, and a cancellation or timeout between two back-to-back single-key commands.
   - For a genuine orphan, an abandoned restore is the correct outcome.
   - There is no reproduction and no downstream report.

   Ruling: **non-material** (a narrow hypothetical).
4. **"`keyPrefix` is doubled or missing."** It is neither. `dirListKey` is prefixed once at l.178 and reused. The value key goes through `store.getKey` once (l.245), the same way `FindEntry` builds it (l.99).
5. **"A transient Redis error deletes members."** `FindEntry` returns the bare sentinel only for `redis.Nil` (l.100-101) and wraps every other error (l.104-105). The guard compares by identity (l.207). An `EXISTS` error restores the member (l.246 falls through to l.250).
6. **"The concurrent-recreate race the bots flagged remains."** On single-view transports it converges in both interleavings. The probe `TestAdjProbeSingleViewRecreateRace` passes at the head. This is a false finding unless it is tied to replica routing, and then it is GT-s1.
7. **"It must be one `MULTI` or Lua script over both keys."** That is `CROSSSLOT` under `redis_cluster2`, because the keys carry no hash tag. Its absence is a constraint, not the defect. Upstream's fix uses a one-key script.
8. **"The TTL-expiry branch (l.214-218) destroys a concurrent recreate."** True, but that code predates this PR (it is unchanged in the diff). The PR body discloses it as "Deliberately not included", and #10744 fixed it separately. It was not introduced by this change.
9. **"Listing now writes to Redis and costs an extra `ZREM`/`EXISTS` per orphan."** This is one-time per orphan and is the PR's intended behaviour. It is not material.
10. **"`glog.V(0)` logs per missing member."** This predates the PR (l.206). Hygiene.
11. **"The new tests are skipped in CI (`RUN_REDIS_TESTS`)."** True at the head (fixed later in #10746). It is test coverage, not a product defect.
12. **"The scaffold key `readOnly` is ignored; the code reads `useReadOnly`."** True (`filer.toml:288` against `redis_cluster_store.go:27,40`), but it predates the PR. It is a config-doc bug, not part of this change. It matters only in that `routeByLatency` is the scaffold-reachable trigger for GT-s1.

## Preexisting hints

These are pre-cutoff review-record comments. There was no human review, and all four comments below are bot comments.
- `greptile-apps[bot]`, 2026-08-13T11:39:01Z, P1 inline at l.208: "**Concurrent recreation loses index membership** If another request recreates the same path after `FindEntry` returns not found but before this `ZRem` executes, the cleanup removes the member just restored by `InsertEntry`". This gestures at the ground-truth surface: a live entry is de-indexed because the not-found read is stale. It names only the concurrency mechanism, which the head fixes for single-view transports.
- `coderabbitai[bot]`, 2026-08-13T11:41:46Z, Major: "Make stale-member cleanup atomic with the value check ... Use an atomic Redis operation, transaction, or Lua script". Same surface.
- `greptile-apps[bot]` summary (created 11:38:58Z, last updated 14:16:05Z, reviewed commit `6c8fde66`): "resolves the previously reported concurrent-recreation race", with "Confidence Score: 5/5".
- `coderabbitai[bot]` walkthrough, 11:09:00Z: no substantive content.
- No participant mentions replicas, `routeByLatency`/`useReadOnly`, cluster routing, child indexes, super-large directories, or cancellation. I checked this with a regex over all review, inline and conversation bodies.
- The PR body asserts "behaves identically on all three transports", which is the false premise behind GT-s1.

## Leakage

These must be excluded from any truncated mirror (everything after the reviewed head `6c8fde66`).

**Commits:**
- `f7ae2d4dd5f08826606f50761e8d7dc6f5a7ce3b`: merge of #10735.
- `4fb5d15019234e46274650e7333b97f151ea4eec` (head `89c5d3442dc1babf6cd94a961877f71f1f139ed9`): #10742, the sibling redis-v1 cleanup by `chrislusf`. It was opened 17:08Z, before the merge instant, and its body describes the child-index and `WithoutCancel` hardening.
- `abd36cbf92cbc06f8dd86d72d0fdbc7cab6a8d93` (head `9d076beada7ed0b75842919d2d03ad46aa829169`): #10743.
- `7d0fff32db881a6b87dead580de382b54afcccdc` (head `5222902c4251ced151e0f5fa64d040f9be745d07`): #10744.
- `0481f712b1c41ed333ea0fd7a52d3cd232218b22` (head `75ffbd8e780a6e74e1778ee634b5a9aba823f0eb`): #10745, the GT-s1 fix. It also renames the scaffold key to `useReadOnly`.
- `0de7ff5eb8fa00a2cd0e5b748259b41b83348390` (head `c0242d1344a9ed130ebf5be00d6fe9406391bf7d`): #10746, which enables the gated redis tests in CI.
- `5c43c03b76c0c319b1d5f33ffa2985df9e727906` (head `8042c1b512a83958b2c72e484dd2ade997645d72`): #10783, later redis2 edits.

**Issues and PRs:** #10742, #10743, #10744, #10745, #10746, #10783. #10736 (an issue on remote-mount TTL entries, cited on l.81 of the #10735 body) does not reveal the defect and need not be excluded.

The PR's final head equals the reviewed head, so there are no later branch heads.

## Confidence and limits

- **High** that GT-s1 is a real, unintended defect introduced by #10735:
  - it is reproduced at the head and absent at the merge-base;
  - it is fixed exactly by #10745;
  - the maintainer confirmed it verbatim.
- **Limit: the replica model.** The probe models go-redis replica routing with a fake client. It does not run a real Redis cluster with replication lag. I verified the routing by reading go-redis v9.21.0 source (`cmdNode`, `slotReadOnlyNode`, the options init). An end-to-end run on a real 3-master/3-replica cluster with `routeByLatency=true` and a paused replica would settle it fully.
- **Deliberate disagreement with the vetting.** I rule the directory-with-live-children case non-material, although the maintainer fixed it in #10743. My comparison against the merge-base shows no loss of live data, only one extra leaked ZSET in a state that eviction or `DEL` has already corrupted.
- **The vetting's config chain is partly wrong.** The scaffold key `readOnly` is dead (the code reads `useReadOnly`), so only `routeByLatency` (or a hand-written `useReadOnly`) triggers GT-s1.
- **Unverified.** The upstream gated tests were not run, because no redis-server was available. I did not verify how often real lag makes the trigger happen; replication in Redis is asynchronous, so the window is real but workload-dependent.
