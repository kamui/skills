# v4 run — `code-review-publish-4` against `redis/redis#15680`

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

**2026-09-01.** Data only. Not published to the PR.

## Metadata

| | |
| --- | --- |
| Skill | `code-review-publish-4` (PR #16) |
| Architecture | 1 integrated reviewer + conditional fresh-context verifier (not triggered) |
| Agents spawned | 1 (no verifier — zero survivors) |
| Total sub-agent tokens | unavailable from this harness |
| Tool uses (self-reported) | 30 |
| Wall clock (orchestrator-measured sub-agent span) | ~22 min |
| Candidates raised | 10 (all dropped in falsification; 0 refuted-by-verifier — no verifier) |
| Candidates surviving falsification | 0 |
| Verifier verdicts | none |
| Findings for publication | **0** |
| Questions | 0 |
| Coverage | complete (5/5 files) |
| Derived status | **Approved (advisory)** |

## Full reviewer report (verbatim)

# Review report — redis/redis#15680, prototype skill `code-review-publish-4`

### Metadata

| Item | Value |
|---|---|
| Total tool invocations | 30 (4 `read`, 25 `bash`/`grep`, 1 `write` for the context-fingerprint JSON input) |
| Files inspected | `redis.conf` (hunk + surrounding section), `src/cluster_legacy.c` (hunk + `clusterSetMaster`, `updateShardId`, `assignShardIdToNode`, `clusterHandleSlaveFailover`, `clusterGetSlaveRank`, `clusterLogCantFailover`, all 6 `clusterSetMaster` call sites, `nodeUpdateAddressIfNeeded`, `clusterUpdateSlotsConfigWith`, sub-replica safeguards, `clusterCron` re-point path), `src/replication.c` (hunk + `replicationSetMaster`, `replicationUnsetMaster`, `replicationHandleMasterDisconnection`, `replicationDiscardCachedMaster`, `replicationResurrectCachedMaster`, `replicationGetSlaveOffset`, `repl_down_since` lifecycle), `src/server.h` (hunk), `tests/unit/cluster/replica-migration.tcl` (full, incl. removed delta of commit 2), `tests/test_helper.tcl` (test discovery), `src/cluster_legacy.h` (shard_id field), `.github/workflows/` (listing) |
| Commands not run | No build/compile (prohibited: would create build artifacts). No test execution (cluster tests spawn 8-server clusters ×12; not proportionate for a merged-PR read-only run, and CI validated them pre-merge). No `gh`/`git fetch`/curl (network prohibited by run rules). No phase-5 head re-fetch (publication disabled, no forge access). No verifier invocation (no qualifying survivors). |

### Coverage

| File | Status | Reason |
|---|---|---|
| `redis.conf` | reviewed | Doc hunk verified against actual behavior in `cluster_legacy.c` |
| `src/cluster_legacy.c` | reviewed | Full hunk + enclosing `clusterSetMaster`, all callers, `updateShardId`, failover eligibility/rank paths |
| `src/replication.c` | reviewed | Deleted forward declaration; `replicationDiscardCachedMaster` definition and all users verified |
| `src/server.h` | reviewed | Added declaration; internal-only symbol |
| `tests/unit/cluster/replica-migration.tcl` | reviewed | Full file + delta of `c54fa4184`; registration auto-globbed by `tests/test_helper.tcl:33-42` (no registration needed) |

**Coverage: complete.** Every changed file reviewed; no unreviewed material; all risk checks have evidence-backed outcomes.

### Requirement ledger

**Issue alignment: unavailable** — no originating issue (no closing reference, no linked issue). Per SKILL phase 1, reviewed the code on its own merits. (Repository workflow does not require an issue.)

**PR-body claims checked (all verified in code):**

| Claim | Verdict |
|---|---|
| Capture cross-shard transition before `updateShardId()` adopts the new shard ID | Verified — `cluster_legacy.c:5427` precedes `updateShardId` at `:5439`; `myself->slaveof = n` at `:5437` guarantees the adoption branch in `updateShardId` (`:947`) fires |
| Discard cached master on cross-shard move | Verified — `cluster_legacy.c:5446` |
| Reset `repl_down_since` to zero | Verified — `cluster_legacy.c:5453` |
| Replica reports offset zero until first sync | Verified — `replicationGetSlaveOffset()` (`replication.c:5056`) returns 0 when neither master client nor cached master exists; consumed by rank (`cluster_legacy.c:4288`) and election offset |
| Non-zero validity factor blocks automatic failover until first sync | Verified — `cluster_legacy.c:4456-4467`: `repl_state != REPL_STATE_CONNECTED` ⇒ `data_age = (unixtime − repl_down_since)·1000` ≈ 1.78e12 ms ⇒ `CLUSTER_CANT_FAILOVER_DATA_AGE` ("Disconnected from master for longer than allowed", `:4339/:4357`); test asserts this log |
| Zero validity factor: eligible but ranked behind replicas with established offset | Verified — `clusterGetSlaveRank` (`cluster_legacy.c:4286-4295`) counts peers with greater `repl_offset` |
| Tests cover migration, `CLUSTER REPLICATE`, sub-replica flattening, both validity factors | Verified — 12 parametrized cases (2 shutdown kinds × 2 validity factors × 2 replica modes × migration/non-empty variants) |
| `redis.conf` documents the behavior | Verified — wording matches the `:4460` semantics; "automatic failover" correctly scoped (manual failover bypasses the data-age check by design, `:4463`) |
| Non-goal: same-shard failovers/partial resync untouched | Verified — `shard_changed` gate; same-shard re-points keep the cached master (histories are the same lineage by shard-id definition) |

**Prior state:** posting identity `kamui` has no earlier review — first review. `sundb`'s APPROVED review predates head commit `c54fa4184`; nothing to deduplicate against (no trailers, no threads on this identity).

### Risk checks

| Check (derived from actual paths/behavior) | Evidence-backed outcome |
|---|---|
| Authorization / sessions / tokens / public exposure | No surface touched. `server.h` change exposes an internal symbol only; no new command, config, or protocol field. **Clear.** |
| Secrets / crypto / logging / sensitive data | None touched. **Clear.** |
| Path normalization / file serving / traversal / symlinks | Not applicable to any changed path. **Clear.** |
| Migrations / destructive operations / rollback / compatibility | The destructive element is discarding the cached master (destroys partial-resync capability) — intentional and only for cross-shard moves where the history is provably invalid (different shard ⇒ different replication lineage). Same-shard paths untouched, so common-case partial resync is preserved. `memcmp` target is a fixed 40-byte array (`cluster_legacy.h:177`), random-initialized at node creation (`cluster_legacy.c:1361`) — never NULL/zero. **Clear.** |
| Retries / idempotency / partial failure / stale state / concurrency | Core check. Traced `repl_down_since` lifecycle (`replication.c:2742, 3720, 3748, 4764`) and its sole cluster reader (`cluster_legacy.c:4460`). At reset time `repl_state == REPL_STATE_CONNECT`, so `data_age` = epoch-scale → blocked for any non-zero factor; a mid-handshake drop goes through `cancelReplicationHandshake`, which does not resurrect a small `data_age`; `REPL_STATE_CONNECTED` is reachable only after the first sync succeeds, at which point failover with the new data is legitimate. The reset runs synchronously before any async connection callback, so no race. **Clear.** |
| External contracts / serialization / version skew | Cluster bus protocol, shard-id propagation (`updateShardId`), and PSYNC semantics unchanged; behavior matches Valkey #885/#944 lineage cited in the body. **Clear.** |

### Candidates and dispositions

All candidates below were raised, falsified in my own context, and **dropped**. No survivors.

| # | Candidate | Falsification outcome |
|---|---|---|
| C1 | `repl_down_since = 0` is misread somewhere as "connected / data_age 0", letting a stale replica win an election | Falsified. Only cluster reader is `cluster_legacy.c:4460`, and it uses `repl_down_since` only when `repl_state != REPL_STATE_CONNECTED`; at reset time state is `REPL_STATE_CONNECT` ⇒ `data_age` ≈ 1.78e12 ms ⇒ fails the validity check for any non-zero factor. Tests confirm the block ("Disconnected from master for longer than allowed"). |
| C2 | Cross-shard re-point paths bypassing `clusterSetMaster` miss the discard/reset: `nodeUpdateAddressIfNeeded` (`cluster_legacy.c:2344`), `clusterCron` (`:5029`) | Falsified. `:2344` re-points to the *same node* after an address update — no shard change possible. `:5029` only re-enables replication when `masterhost == NULL` for an already-designated `slaveof`, whose shard id was already adopted via a prior `clusterSetMaster`; a node with `masterhost == NULL` cannot hold a stale cached master (`replicationUnsetMaster` discards it at `replication.c:3688`; restart clears memory). |
| C3 | `memcmp(myself->shard_id, n->shard_id, ...)` on a NULL/unknown shard id | Falsified. `shard_id` is a fixed `char[40]` (`cluster_legacy.h:177`), random-initialized for every node (`cluster_legacy.c:1361`). No NULL, no all-zero realistic case; even a hypothetical zero id yields the conservative direction (force full sync). |
| C4 | `updateShardId` may not adopt `n`'s shard id because its replica branch compares `node->slaveof->shard_id` | Falsified. `myself->slaveof = n` (`cluster_legacy.c:5437`) executes before `updateShardId(myself, n->shard_id)` (`:5439`), so the adoption branch fires — consistent with `shun-lee`'s review. |
| C5 | Integer overflow in `data_age = (unixtime − repl_down_since) · 1000` with `repl_down_since = 0` | Falsified. `mstime_t` is `long long`; ~1.78e12 ms is far within range. |
| C6 | `INFO` `master_link_down_since_seconds` shows an epoch-sized value for the unsynced replica | Falsified as a finding: identical pre-existing semantics for any never-connected replica (`repl_down_since == 0` from boot); not introduced by this change; arguably the intended "disconnected since forever" reading. |
| C7 | Test hard-depends on `redis-cli --cluster rebalance` assigning slot 0 to primary 0 | Not disprovable statically, but redis-cli rebalancing is deterministic for a fixed cluster state, and the test fails loudly with diagnostics if the topology differs; PR merged with CI green. Fails rubric condition 7/8. |
| C8 | Removing the "I'm a sub-replica" assertion (commit 2) weakens the non-sub-replica test | Falsified. The flattened path is fully exercised by the dedicated `sub_replica` variants; the removed assertion was timing-sensitive (R 7 can transiently follow the grandmaster before migration re-points it). Acceptable test change, not a defect. |
| C9 | Manual failover (`CLUSTER FAILOVER`) bypasses the data-age check, so an unsynchronized cross-shard replica could be promoted manually | Falsified. Pre-existing design (`if (!manual_failover)` at `cluster_legacy.c:4463`), operator-initiated on that node, and the redis.conf text correctly scopes the guarantee to *automatic* failover. Not introduced by this change. |
| C10 | Test file cost: 12 × 8-node clusters, heavy CI time | Proportionate to repo norms for cluster tests (parameterized matrix is the point of the fix). Fails rubric condition 7. |

### Verifier decision

**No survivor qualifies for independent verification.** Zero candidates survived falsification, so nothing is proposed as must-fix, nothing concerns security/authorization, risks data loss or corruption, touches a destructive migration, or changes a public/external contract, and no `consider` survivor has module-spanning or difficult proof. Per SKILL phase 3 ("Do not invoke a verifier for a clean run"), **no batched verifier is invoked**. Publication is therefore **not** blocked pending verification.

### Would-be published review

Since there are no findings and no qualifying survivors, publication would be a single `COMMENT`-event review (no inline comments, no gating, `kamui` is not the author so self-review gating is not applicable anyway):

```markdown
**Approved (advisory)** — no findings.

**Intent:** Prevent cross-shard cluster replicas from participating in failover with their old shard's replication history until they complete a first full sync with the new master, by discarding the cached master and resetting `repl_down_since` on cross-shard re-points inside `clusterSetMaster`.

**Issue fit:** Issue alignment unavailable — no originating issue was linked. All behavioral claims in the pull-request body were verified against the code: cross-shard detection precedes shard-id adoption; cached master is discarded (forcing full sync and offset-0 reporting via `replicationGetSlaveOffset`); with a non-zero `cluster-replica-validity-factor` the replica cannot start an automatic failover until its first synchronization succeeds (`data_age` check in `clusterHandleSlaveFailover`); with a zero factor it stays eligible but ranks behind replicas with established offsets. Same-shard partial resynchronization is untouched, as stated.

**Coverage:** Complete merge-base diff reviewed (5 files). Inspected: `clusterSetMaster` and all six of its call sites, `updateShardId`/`assignShardIdToNode`, the `repl_down_since` lifecycle in `replication.c`, the failover data-age and rank computation, other `replicationSetMaster` re-point paths (`nodeUpdateAddressIfNeeded`, `clusterCron` re-enable), the full new test file and its auto-discovery by `tests/test_helper.tcl`, and base-branch repository guidance (none present in this repository at `065d3970`).

**Reviewed:** `c54fa4184e7db1ea30c91916f6c0aeb12b5c3f61` against merge-base `065d397030712fe216e795720ae0affd3211212c` (base ref `unstable`).

**Issue alignment unavailable:** no originating issue; reviewed against the pull-request body's stated behavior.

<!-- review-run head=c54fa4184e7db1ea30c91916f6c0aeb12b5c3f61 base-ref=unstable base-sha=065d397030712fe216e795720ae0affd3211212c merge-base=065d397030712fe216e795720ae0affd3211212c workflow=v4-1 context=96d9d5e87e8b8576446872d5ecb616d2f5b500d3e0a63d21cce8adf019d23179 issues=none coverage=complete -->
```

Inline comments: **none.**

### Notes

- **Head/base continuity:** `065d3970` is confirmed the merge-base of `c54fa4184` in this clone; diff is exactly the packet's 5-file manifest (+401/−1). Two commits: `8b3c50521` (substantive) and `c54fa4184` ("remove unnecessary check" — actually removes only a timing-sensitive test assertion about the "I'm a sub-replica" log, no code change).
- **Mechanism cross-check:** the offset-0 claim rests on `replicationDiscardCachedMaster()` removing `cached_master`, since `replicationGetSlaveOffset()` (`replication.c:5056-5070`) falls back to 0 only when both `server.master` and `cached_master` are absent — the PR's two mechanisms (discard + `repl_down_since = 0`) are jointly necessary and both present.
- **Base-branch guidance:** the redis clone at `065d3970` has no `AGENTS.md` and no `docs/agents/` guidance files; no repository-rule findings applicable.
- **Run protocol deviations:** head re-fetch (phase 5) not performed — no forge access; PR state is MERGED so no publication would occur regardless. The `context` digest was computed with `scripts/context_fingerprint.py` from the packet's verbatim PR title/body (including the appended Cursor summary block), `issues=[]`, `guidance=[]`.
- **Test-site observations (not findings):** the rebalance destination (slot 0 → primary 0) is deterministic redis-cli behavior but the test would fail (with diagnostics) if that changed; `pause_process` leaks into teardown on mid-test failure, which the framework's process cleanup covers.

## Notes on the run

- One of two runs to compute the `context` fingerprint with the skill's own script (the other being v5).
- The only run to trace a potential integer-overflow candidate on the data-age arithmetic.
- Worktree left clean; nothing published.
