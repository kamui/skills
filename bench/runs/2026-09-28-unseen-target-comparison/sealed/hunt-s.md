# Hunt (s): data loss or destructive migration, buggy

Started 2026-09-28. Single-threaded. Toolchain: node 24 (mise), python3, uv, go (mise); **no cargo**, no fd.

## Inventory (in order examined)

| # | Repo | PR | Merged | Lines/Files | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 | E10 | Result |
|---|------|----|--------|-------------|----|----|----|----|----|----|----|----|----|-----|--------|
| 1 | pingcap/tidb | #52400 (culprit named by issue #71448, fix #71453) | 2024 | n/c | pass | **fail**: merged 2024, before 2025-10-01 | n/c | n/c | n/c | n/c | n/c | n/c | n/c | n/c | dropped |
| 2 | ClickHouse/ClickHouse | #104969 (culprit named by fix #116898) | 2026-08-27 | +263/-26, 11 files (PR API) | pass | pass | **fail**: 11 files > 10 | n/c | n/c | (C++ full build; would also fail) | n/c | n/c | n/c | n/c | dropped |
| 3 | Tencent/teamai-cli | #378 (culprit named by fix #383) | 2026-09-01 | +301/-121, 12 files (PR API) | pass | pass | **fail**: 12 files > 10 | n/c | n/c | n/c | n/c | n/c | n/c | **fail**: licence "Other" (not OSI per GitHub) | dropped |
| 4 | grafana/grafana | culprit of fix #131837 (hardcoded `refresh: 'onDashboardLoad'` in `replaceVariableDatasources`) | ≤ 2026-04-20 (present at a232785144) | n/c | pass | **fail** for preferred window: culprit ≤ 2026-04; kept as fallback only | n/c | n/c | n/c | n/c | n/c | n/c | n/c | n/c | parked |
| 5 | infiniflow/ragflow | #18883 (referenced by follow-up fix #19026) | 2026-08-29 | +82/-11, 2 files (PR API) | pass | pass | pass (PR API) | n/c | n/c | n/c | n/c | **fail**: the read-modify-write overwrite race fixed by #19026 predates #18883 (diff shows the Get→SetObj RMW unchanged); not introduced by this PR | **fail** as a culprit attribution | n/c | dropped |
| 6 | BasedHardware/omi | #15977 (culprit named by issue #17300) | 2026-09-22 | +106/-8, 4 files (PR API) | pass | pass | pass (PR API) | n/c | n/c | n/c | n/c | **fail**: #15977's own body promises "an unparseable legacy value is treated as empty", i.e. the reported behaviour was the tested contract | **fail**: only confirmation is open bounty PR #17299 / issue #17300 by an external bounty account, no maintainer response | pass (MIT) | dropped |
| 7 | chatwoot/chatwoot | #15362 (referenced by issue #16039) | 2026-08-12 | +23/-6, 5 files (PR API) | pass | pass | n/c | n/c | n/c | n/c | n/c | n/c | **fail**: issue #16039 open, no maintainer reply, and blames `FORMATTING[...].nodes = []`, not #15362; outbound message formatting, not stored data | n/c | dropped |
| 8 | PostHog/posthog | culprits behind fixes #95369 / #94508 (warehouse-sources xmin reset, `record_partition_measurement` clobber) | 2026-07..09 | n/c | pass | pass | n/c | n/c | n/c | **fail (expected)**: Django model/e2e tests need live Postgres/ClickHouse services; multi-GB repo | n/c | n/c | not traced further | pass (MIT, ee/ excluded) | dropped on E6 |
| 9 | seaweedfs/seaweedfs | #10585 (referenced by fix #10589) | 2026-08-05 | +207/-4, 6 files | pass | pass | n/c | n/c | n/c | n/c | n/c | **fail**: #10589 fixes the plain PUT path, which already retired the marker before the write; #10585 did not introduce it | **fail** as culprit | pass | dropped |
| 10 | seaweedfs/seaweedfs | #10965 (referenced by fix #10973) | 2026-08-26 | +109/-27, 5 files | pass | pass | n/c | n/c | n/c | n/c | n/c | **fail**: #10973 is "the second half ... #10965 left open", pre-existing; also mount metadata cache, not stored data | **fail** | pass | dropped |
| 11 | seaweedfs/seaweedfs | #8441 (volume.merge; corruption fixed by #10565, issue #10563) | 2026-02-25 | +1760/-286, 7 files (PR API) | pass | fallback-window only | **fail**: 2046 lines > 400 | n/c | n/c | n/c | n/c | n/c | n/c | pass | dropped |
| 12 | seaweedfs/seaweedfs | **#10735** fix(redis2): remove orphaned directory index members on listing | 2026-08-13T17:53:33Z | +160/-0, 2 files (git numstat MB..head) | pass | pass (preferred window; confirmations #10743/#10745 merged 2026-08-13) | pass | **pass** exit 0, default cutoff = merge instant, 0 omissions | pass (GitHub reviews/threads; bots only) | **pass**: `go test -overlay` probe, clone `chmod -R a-w`, 12.1 s head (cold) / ~4.3 s others, tracked tree clean | pass (diff + `FindEntry` + `redis_cluster_store.go`/child-index contract) | pass (PR promised removing *orphans* only) | pass: maintainer PRs #10743, #10745 name the data loss | pass (Apache-2.0) | **PASS: recommended** |
| 13 | seaweedfs/seaweedfs | #10782 (referenced by follow-up #10783) | 2026-08-17 | +86/-3, 2 files | pass | pass | n/c | n/c | n/c | n/c | n/c | **fail**: #10783 calls it "the milder half of the same race" that #10782 left behind, i.e. pre-existing | **fail** as culprit | pass | dropped |
| 14 | seaweedfs/seaweedfs | #11108 (stacked under #11109) | 2026-09-03 | +231/-16, 5 files | pass | pass | n/c | n/c | n/c | n/c | n/c | **fail**: o_excl upsert race (#11079) predates both PRs | **fail** | pass | dropped |
| 15 | kubeshop/testkube | #8172 (named by follow-up #8179) | 2026-08-26 | +27/-6, 2 files (PR API) | pass | pass | pass (PR API) | n/c | n/c | n/c | n/c | n/c | weak: #8179 by the same author, overwritten field is per-step resource metadata in runner state, marginal "stored data" | **doubtful**: GitHub licence "other" | dropped |
| 16 | prometheus/prometheus | #19460 (named by follow-up #19664) | 2026-09-08 | +136/-11, 2 files (PR API) | pass | pass | pass (PR API) | n/c | n/c | n/c | n/c | n/c | **fail** for slot: #19664 names query panics ("Prevent query panics during series eviction"), a crash with no stored-data consequence | pass | dropped (out of slot) |
| 17 | grafana/mimir | culprit of fix #16493 (`lastConsumedOffset := startOffset` in `consumePartitionSection`) | ≤ 2025-11-03 (line present at 3a801f4923) | n/c | pass | **fail**: culprit predates 2025-10..2026-06 history checked; not fresh | n/c | n/c | n/c | n/c | n/c | n/c | n/c | n/c | dropped |

Search log (all through `gh`, paced): repo-scoped `gh search prs` over ~60 storage/DB/ORM/CMS repos; raw `search/issues` phrase queries; and `scratch/trace.py`, which takes data-loss fix PRs and issues merged or created from 2026-07-10 on ("data loss", "silently dropped", "regression" + overwrites/corrupt/"are lost"/migration/backfill/wipes, "follow-up to #", "introduced in #", labels `data-loss`/`dataloss`/"data loss"), keeps repos with at least 300 stars, and resolves every `#N` in the body to a PR merged on or after 2026-07-01. Outputs are in `scratch/trace*.out`. Most hits were fixes for code that was already old, or AI-generated trails with no maintainer behind them.

---

## Recommendation

**Primary: seaweedfs/seaweedfs#10735.** It is the first candidate in inventory order that passes E1–E10.

**Alternate: none found.** No second candidate passed E1–E10 within this dispatch. Rows 1–11 and 13–17 are the closest misses, each with the criterion it fails. The nearest were grafana culprit of #131837 (fails E2: older than 2026-04; its frontend tests need a multi-GB yarn install), ClickHouse#104969 (fails E3: 11 files; also a C++ build) and teamai-cli#378 (fails E3: 12 files; fails E10: licence "Other").

### seaweedfs/seaweedfs#10735: fix(redis2): remove orphaned directory index members on listing

- **Author**: `petedodd-pd` (Peter Dodd). **Merged**: 2026-08-13T17:53:33Z by squash, as `f7ae2d4dd5f08826606f50761e8d7dc6f5a7ce3b`. **Base branch**: `master`. **Licence**: Apache-2.0.
- **Head**: `6c8fde6642cd428e884cc9c9d88c9aaa189c4bf1`. **PR-recorded base**: `db5a086d048c5c2d6e51e82bb070d20df04d688d`. **Computed `git merge-base`** on a full clone: `db5a086d048c5c2d6e51e82bb070d20df04d688d`. They **agree**.
- **Commits**: `9f9962800` "remove orphaned directory index members on listing", then `6c8fde664` "keep the index member when a concurrent insert recreates the value". The second commit is the head.
- **Manifest** (`git diff --numstat MB head`): `weed/filer/redis2/universal_redis_store.go` +17/-0, `weed/filer/redis2/universal_redis_store_test.go` +143/-0. That is 160 lines in 2 files.
- **Originating issue**: none. The PR body cites no issue. It mentions #10736 only as a related proposal.

**Prior review record, up to the merge instant.** There was no human review. Two bot reviews were submitted, both COMMENTED:
- `greptile-apps[bot]` at 2026-08-13T11:39Z, a P1 inline comment: "**Concurrent recreation loses index membership** If another request recreates the same path after `FindEntry` returns not found but before this `ZRem` executes, the cleanup removes the member just restored by `InsertEntry`".
- `coderabbitai[bot]` at 2026-08-13T11:41Z, rated Major: "Make stale-member cleanup atomic with the value check ... Use an atomic Redis operation, transaction, or Lua script".

Two conversation comments are bot summaries. The author answered the race with the second commit, adding an `EXISTS` re-check and a `ZAddNX` restore. **No one raised the defects described below**: replica-routed reads, a directory member whose child index is still live, and super-large directories. The PR body in fact claims the super-large case is unreachable: "the index key does not exist for those directories at all ... the new call is unreachable".

**The defect.** It sits in `weed/filer/redis2/universal_redis_store.go` at the head:
- `ListDirectoryEntries` (line 176) now calls `store.removeOrphanedDirectoryListMember(...)` at line 208 whenever `FindEntry` (line 97, a plain `GET`) returns `filer_pb.ErrNotFound`.
- The helper (lines 237–251) does `ZRem` (238), then `Exists` on the value key (245), and restores with `ZAddNX` (250) only if `EXISTS` reports the key present.

The cleanup treats one not-found read as proof that the entry is orphaned and irrecoverably removes the index member of an entry that is still live.

- **Violated contract, from the PR's own body**: "Only a positively confirmed absent value leaves the member removed", and "A member cannot legitimately outlive a missing value".
- **Config contract, one hop away**:
  - `redis_cluster_store.go:53-54` passes `ReadOnly: readOnly, RouteByLatency: routeByLatency` into `redis.ClusterOptions`.
  - The scaffold, `weed/command/scaffold/filer.toml:287-290`, says: "allows reads from slave servers or the master, but all writes still go to the master" and "automatically use the closest Redis server for reads".
  - go-redis `osscluster.go:63`: RouteByLatency "automatically enables ReadOnly".
- **Trigger 1 (replica lag, confirmed by #10745)**:
  1. A redis_cluster2 filer runs with `routeByLatency = true`.
  2. `InsertEntry("/d/f")` writes the value `SET` to the master of the value key's slot. The member lives under a different slot, because the keys carry no hash tag.
  3. A listing of `/d` reads the member. `GET /d/f` then hits a replica of the value slot that has not applied the write yet, so it returns nil.
  4. `ZREM` goes to the master. `EXISTS` asks the same lagging replica and gets 0, so there is no restore.
- **Trigger 2 (directory with live children, confirmed by #10743 item 4)**:
  1. Directory `/d/sub`'s own value key is gone (maxmemory eviction or an out-of-band `DEL`, both routes the PR body names), but `/d/sub\x00` still holds `child`.
  2. Listing `/d` removes the `sub` member.
- **Consequence for stored data**:
  - Trigger 1: the directory-index ZSET, which is persisted filer metadata, loses the member of a live entry. #10745 says: "The entry vanishes from every listing until it is re-inserted."
  - Trigger 2: the live subtree is detached. #10743 says: "nothing can list it or recursively delete it afterwards, and its keys leak forever".
  - Neither case can be repaired automatically, because `UpdateEntry` never re-adds members.
- **Confirming upstream record** (all by maintainer `chrislusf`, all merged 2026-08-13):
  - #10745 "redis2: orphan cleanup existence checks must not read replicas". Merge `0481f712b1c41ed333ea0fd7a52d3cd232218b22`, head `75ffbd8e780a6e74e1778ee634b5a9aba823f0eb`. Verbatim: "That turns the #10735 cleanup destructive under replica lag: an insert lands on the master, a listing's `GET` hits a replica that has not applied it yet, the not-found branch fires, the `ZREM` removes the live member on the master — and the compensating `EXISTS` asks the same lagging replica, gets 0, and skips the restore. The entry vanishes from every listing until it is re-inserted. Before the cleanup existed, that same stale read cost a transient one-page miss, not a lost index member."
  - #10743 "redis2: harden the orphaned index member cleanup". Merge `abd36cbf92cbc06f8dd86d72d0fdbc7cab6a8d93`, head `9d076beada7ed0b75842919d2d03ad46aa829169`. Verbatim: "For a member whose value key was lost ... but whose own child index still exists, stripping the member detaches a live subtree: nothing can list it or recursively delete it afterwards, and its keys leak forever." The same PR also names two more defects: the super-large-directory case ("the cleanup would strip them irrecoverably") and the request context cancelling the restore ("permanently de-indexing a live, concurrently recreated entry").
- **Corrective outcome**: the listing cleanup may remove a directory-index member only when the entry's value is authoritatively absent, meaning absent on the key's master and not on a possibly stale replica view. It must also be absent with no live child index under that path, and outside super-large directories. The repair must not be abandoned halfway by caller cancellation. Live entries must stay listed and reachable by `DeleteFolderChildren`.

**Tempting false positives.** Each looks like a bug but is not one at the head:
1. *The `keyPrefix` is doubled or missing.* It is neither. `dirListKey` is already prefixed at line 178 and is reused as is. The value key goes through `store.getKey(string(path))` once, the same way `FindEntry` does it.
2. *A transient Redis error deletes members.* It cannot. `FindEntry` returns the bare `filer_pb.ErrNotFound` sentinel only for `redis.Nil` and wraps every other error. The guard compares by identity (`err == filer_pb.ErrNotFound`), so a connection error breaks out of the loop instead.
3. *The concurrent-recreate race the bots flagged remains.* On single-view transports (a single node, or a cluster without replica reads) the `ZREM`, `EXISTS`, `ZAddNX` compensation converges in both interleavings, as the PR body argues.
4. *It should be one `MULTI` or Lua script over both keys.* Under `redis_cluster2` that is `CROSSSLOT`, because the value key and the index key carry no hash tag. Its absence is a constraint, not the defect.
5. *The TTL-expiry branch at lines 214-218 destroys a concurrent recreate.* It does, but that code predates this PR. #10744 treats it as "the pre-existing race #10735 deliberately left open".

**Leak set.** A truncated mirror must exclude everything after the reviewed head `6c8fde66`. The PR's final head equals the reviewed head, so there are no later branch heads.
- SHAs: merge `f7ae2d4dd5f08826606f50761e8d7dc6f5a7ce3b`; #10743 `abd36cbf92cbc06f8dd86d72d0fdbc7cab6a8d93` (head `9d076beada7ed0b75842919d2d03ad46aa829169`); #10744 `7d0fff32db881a6b87dead580de382b54afcccdc` (head `5222902c4251ced151e0f5fa64d040f9be745d07`); #10745 `0481f712b1c41ed333ea0fd7a52d3cd232218b22` (head `75ffbd8e780a6e74e1778ee634b5a9aba823f0eb`); #10746 `0de7ff5eb8fa00a2cd0e5b748259b41b83348390` (head `c0242d1344a9ed130ebf5be00d6fe9406391bf7d`, which enables the gated redis tests); #10783 `5c43c03b76c0c319b1d5f33ffa2985df9e727906` (head `8042c1b512a83958b2c72e484dd2ade997645d72`, later edits to redis2).
- Issue and PR numbers whose content gives the answer away: #10743, #10744, #10745, #10746, #10783.

**Provisioning and test evidence I actually ran.**
- **Provisioning**:
  - `git clone https://github.com/seaweedfs/seaweedfs.git`: 11.7 s, 417 MB.
  - `git fetch origin pull/10735/head pull/10744/head pull/10745/head`.
  - `git checkout 6c8fde66`.
  - `go list -deps ./weed/filer/redis2`: 4.6 s. The modules were already present in `~/go/pkg/mod`, outside the clone.
- **Read-only setup**:
  - `git archive` of the merge-base `db5a086`, of #10743's merge `abd36cbf9` and of #10745's merge `0481f712b` into `scratch/tree-{mb,fix43,fix45}`.
  - Then `chmod -R a-w` on the clone and on all three trees. `touch seaweedfs/x` gives "Permission denied".
- **Focused command**, the same one in every tree:
  `GOFLAGS=-mod=readonly go test -overlay scratch/e6/overlay-<tree>.json -count=1 -run TestProbe -v ./weed/filer/redis2/`
  - The overlay adds `scratch/e6/orphan_probe_test.go`, which lives outside the clone, as an in-package test.
  - That test drives `ListDirectoryEntries` through a fake `redis.UniversalClient`. Reads (GET, EXISTS) come from a replica view; writes and scripts (ZREM, ZADD NX, EVAL/EVALSHA) go to the master.
  - Build output goes to `~/.cache/go-build` and modules to `~/go/pkg/mod`. Nothing is written inside the clone.
  - The upstream gated tests were not run, because they need a live redis-server (a service).
- **Results**:

| Tree | Exit | Duration | Result |
|---|---|---|---|
| head `6c8fde66` (the clone) | 1 | 12.1 s, cold | FAIL `TestProbeReplicaLagKeepsLiveMember` ("directory index lost the live member "live": index=map[], master value still present=true"); FAIL `TestProbeDirectoryWithLiveChildrenKeepsMember` ("directory index lost "sub" whose child index still holds map[child:true]") |
| merge-base `db5a086` | 0 | 4.2 s | both PASS |
| after #10743 `abd36cbf9` | 1 | 4.4 s | directory case PASS; replica case still FAIL |
| after #10745 `0481f712b` | 0 | 4.2 s | both PASS |

- **Tracked tree**: `git -C seaweedfs status --porcelain` printed 0 lines after the runs, so it stayed clean. **E6 read-only requirement: PASS.**
- **Caveat**: the replica probe models go-redis's documented routing (reads to replicas under ReadOnly/RouteByLatency, scripts to the master) inside the fake; it does not run a real replica. The directory probe makes no routing assumption.

**E4**: `build_packet.py --repo seaweedfs/seaweedfs --pr 10735 --head 6c8fde66… --merge-base db5a086… --base-sha db5a086… --staging scratch/seaweedfs --target s --out scratch/packet-10735.md` exited **0**. Cutoff: the default, `2026-08-13T17:53:33Z`, the merge instant. Omitted: `{'reviews': 0, 'thread_comments': 0, 'conversation': 0, 'issue_comments': 0}`. The packet covered 2 files, 2 commits, 2 reviews, 2 thread comments and 2 conversation comments.

**Confidence: high** that this is a real, maintainer-confirmed data-loss defect introduced by #10735.
- The owner shipped two same-day fixes, and each names the destructive consequence and blames #10735 explicitly.
- The behaviour flips exactly between merge-base, head and the fix commits in my runs.
- The diff is small, and the defect is reachable through `FindEntry` plus the cluster-store options, or the child-index contract.

Two caveats:
- **Medium on the reviewer-difficulty profile.** The replica variant needs outside knowledge of go-redis routing, so the directory-with-children variant (#10743 item 4) is the more statically visible framing.
- **Prior review.** The bots flagged a related race, which the head does fix, so graders should accept the replica, directory and super-large defects and not credit a re-report of the bot race.

Note: `scratch/seaweedfs` and `scratch/tree-*` are still `chmod a-w`. Run `chmod -R u+w` before deleting them.
