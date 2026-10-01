# v3 run — `snapshot-path-omitted` against `redis/redis#15680`

**2026-09-01.** Data only. Not published to the PR.

## Metadata

| | |
| --- | --- |
| Skill | `snapshot-path-omitted` (PR #13) |
| Architecture | 1 integrated reviewer, self-falsification; conditional batched verifier (not triggered) |
| Agents spawned | 1 (no verifier — zero survivors) |
| Total sub-agent tokens | unavailable from this harness |
| Tool uses (self-reported) | 35 |
| Wall clock (orchestrator-measured sub-agent span) | ~19 min |
| Candidates raised | 11 (7 refuted, 4 dropped in falsification) |
| Candidates surviving falsification | 0 |
| Verifier verdicts | none — no survivor qualified; rubric's "high-risk change" disjunct noted, list empty |
| Findings for publication | **0** |
| Questions | 0 |
| Coverage | complete (5/5 files) |
| Derived status | **Approved (advisory)** |

## Full reviewer report (verbatim)

# Review report — redis/redis#15680 (snapshot-path-omitted prototype run)

### Metadata

| | |
| --- | --- |
| Total tool invocations | 35 (4 Read, 29 Bash, 2 sandbox ctx_execute; Grep/Glob tools unused — content search ran via `git grep` in Bash) |
| Files inspected | /tmp/redis-phase1-packet.md; SKILL.md; review-rubric.md; output-contract.md; `redis.conf`; `src/cluster_legacy.c` (changed hunks + `clusterSetMaster`, `clusterLogCantFailover`, `clusterGetSlaveRank`, `clusterHandleSlaveFailover` data-age block, `updateShardId`, both `I'm a sub-replica` sites, replica-migration and CLUSTER REPLICATE call sites); `src/replication.c` (`replicationSetMaster`, `replicationCacheMaster`/`DiscardCachedMaster`/`ResurrectCachedMaster`, `replicationGetSlaveOffset`, `roleCommand`, all 4 `repl_down_since` sites); `src/server.h` (declaration region); `src/server.c` (INFO `master_link_down_since_seconds` block); `src/debug.c` (grep-scoped, ROLE not present there); `tests/unit/cluster/replica-migration.tcl` (full); `tests/support/cluster_util.tcl`, `tests/support/util.tcl`, `tests/support/cli.tcl`, `tests/test_helper.tcl`, `tests/cluster/run.tcl`, `runtest-cluster`, `.github/workflows/ci.yml`, `.github/workflows/daily.yml` |
| Commands not run and why | No server build or test execution (`make`/`runtest`/`runtest-cluster` create build artifacts and spawn processes — outside this run's read-only constraints; also the new test spins up 12 clusters of 8 nodes); no `gh`/curl/git fetch (network prohibited; origin is a local path); no CI run logs consulted (not available offline) |

### Coverage

| File | Status | Reason |
| --- | --- | --- |
| `redis.conf` | reviewed | Doc addition validated against code behavior (see risk check 4) |
| `src/cluster_legacy.c` | reviewed | Full hunk + enclosing `clusterSetMaster` + all 6 callers + failover data-age/rank/offset consumers |
| `src/replication.c` | reviewed | Deleted forward declaration + `replicationSetMaster`/cache lifecycle/`roleCommand` |
| `src/server.h` | reviewed | Added declaration; no other users affected |
| `tests/unit/cluster/replica-migration.tcl` | reviewed | Full 378-line file; every helper, log pattern, and assertion cross-checked against source |

**Coverage: complete.** Every changed file reviewed; no unreviewed material; both commits (including the `remove unnecessary check` delta) inspected.

### Requirement ledger

| Entry | Disposition |
| --- | --- |
| Originating issue | **unavailable** — no closing reference, no linked issue, nothing resolvable from branch/commit names. Per SKILL §1, reviewed the code and stated issue alignment was unavailable. |
| Non-goals from PR body | None stated. |
| Body claim: capture `shard_changed` before `updateShardId()` | satisfied — `cluster_legacy.c:5427` precedes `updateShardId` at :5441 |
| Body claim: discard cached master on cross-shard move | satisfied — `replicationDiscardCachedMaster()` in the `if (shard_changed)` block |
| Body claim: reset `repl_down_since` to zero | satisfied — `server.repl_down_since = 0` |
| Body claim: reports offset zero until first sync | satisfied — `replicationGetSlaveOffset()` returns 0 once `server.master` and `server.cached_master` are both NULL (replication.c:5056); it feeds both the gossip offset (cluster_legacy.c:3759) and the failover rank (cluster_legacy.c:4288) |
| Body claim: non-zero validity factor blocks automatic failover until first sync | satisfied — `data_age = (unixtime - repl_down_since) * 1000` (cluster_legacy.c:4460) becomes astronomically large with `repl_down_since = 0`, failing the check at :4479; after first sync, `repl_state == CONNECTED` switches data-age to `lastinteraction` |
| Body claim: zero validity factor keeps eligibility but worst rank | satisfied — check bypassed when `cluster_slave_validity_factor` is 0; `clusterGetSlaveRank` counts slaves with higher `repl_offset`, so offset 0 ranks last |
| Body claim: tests cover migration, `CLUSTER REPLICATE`, sub-replica flattening, both factors | satisfied — 12 `start_cluster` variants present |

### Risk checks

| Check (rubric-derived) | Outcome | Evidence |
| --- | --- | --- |
| Stale state across re-parenting (the core risk) | **clean** | `replicationSetMaster` frees the old master client (caching it via `freeClient`→`replicationCacheMaster`) *before* the PR's discard, so the stale-shard cache is always removed; for demoted masters it discards-then-caches own params, and the PR's later discard removes exactly that stale own-shard cache. Ordering verified at replication.c:3621–3646 vs cluster_legacy.c:5443–5453. |
| Partial failure / retries (PSYNC fallback, handshake retry) | **clean** | Cached master discarded ⇒ no `CONTINUE` against unrelated history is possible; `replicationCron` retry path unaffected; `repl_down_since = 0` is exactly the state of a never-synchronized replica (same value set at replication.c:2742 on connect-complete) |
| Concurrency / idempotency of the reset | **clean** | Re-invoking `clusterSetMaster` for the same master yields `shard_changed == 0` (shard IDs already adopted), so no repeated reset; same-shard re-pointing is untouched by design (deliberate per PR body and shun-lee's review) |
| Compatibility / version skew | **clean** | A peer with unknown/zero `shard_id` only causes a conservative extra full sync + blocked auto-failover until sync — identical to a newly configured replica; no unsafe path. `shard_id` is a fixed `char[CLUSTER_NAMELEN]` array, so the `memcmp` cannot dereference NULL |
| Config/docs surface | **clean** | redis.conf text matches code exactly, including the "automatic" qualifier (manual failover bypasses the validity check by design, and the doc does not claim otherwise) |
| Public exposure / secrets / authz | **clean (N/A)** | No new commands, config keys, or network surface; only a header declaration move |
| Downstream consumers of `repl_down_since = 0` | **clean** | Only three read sites exist: cluster data-age (cluster_legacy.c:4460, handled correctly) and INFO `master_link_down_since_seconds`, which maps 0 to `-1` (server.c:6903) — semantically consistent with "disconnected since forever". ROLE reports `server.master->reploff` or -1 (replication.c:4601), unaffected |
| Test/CI wiring | **clean** | All test helpers exist (`start_cluster` accepts a custom slot allocator; `normalize_cluster_slots`, `wait_for_ofs_sync`, `count_log_message`, `verify_log_message`, `pause_process`, `rediscli_tls_config` all present); every expected log string exists in source ("Currently unable to failover: Disconnected from master for longer than allowed.", "Start of election delayed … (rank #%d, offset %lld).", "I'm a sub-replica!"); `unit/cluster` runs in the main suite that PR CI executes (`./runtest --verbose --tags -slow`) |

### Candidates and dispositions

No candidates survived; **zero admitted findings**.

| # | Candidate | Disposition | Evidence |
| --- | --- | --- | --- |
| C1 | Test waits on `[lindex [R x role] 4] <= 0` assuming ROLE element 4 reflects `repl_down_since = 0` (would make the wait fail with a huge down-since value) | **refuted** | ROLE always returns 5 elements for a replica; element 4 is `server.master ? server.master->reploff : -1` (replication.c:4601), i.e. the sync offset, not down-since — the assertion correctly detects "not yet synced" |
| C2 | Test log-message patterns don't exist in source | **refuted** | All three patterns verified verbatim in cluster_legacy.c (:4339, :4361, :2529/:3261) |
| C3 | `repl_down_since = 0` misread as "connected" elsewhere, weakening failover safety | **refuted** | Read sites enumerated (only cluster_legacy.c:4460 and server.c INFO); both handle 0 correctly |
| C4 | Discard is redundant/wrong because `replicationSetMaster` already discards for demoted masters | **refuted** | `replicationSetMaster` discards then *re-caches own params* (`replicationCacheMasterUsingMyself`, replication.c:3641–3643); the PR's later discard removes that stale own-shard cache — the intended behavior, not a double-discard bug |
| C5 | Same-shard re-point may keep a cached master with unrelated history, enabling bad partial resync | **refuted** | Same shard implies shared replication-history chain; preserving it is deliberate (PR body + shun-lee review) and pre-existing behavior unchanged |
| C6 | All-zero `n->shard_id` (mixed-version/unknown peer) causes spurious reset | **dropped** | Effect is only a conservative full sync and blocked auto-failover until sync — identical to "newly configured replica" semantics; no harmful trigger found; speculation per rubric gate 4 |
| C7 | Reset blocks needed failovers, e.g. manual | **refuted** | Validity check is explicitly bypassed for manual failovers (cluster_legacy.c:4476–4483); automatic failover blocking is the PR's stated intent |
| C8 | INFO `master_link_down_since_seconds:-1` regression | **dropped** | Intentional "disconnected since forever" semantics, matches a fresh replica's state; cosmetic and deliberate |
| C9 | Test suite weight: 12 × 8-node clusters + redis-cli rebalance per run | **dropped** | Consistent with existing `unit/cluster` conventions; matrix is the PR's stated deliverable; not a defect |
| C10 | `assert {[lindex [R 7 role] 4] <= 0}` right after `CLUSTER REPLICATE` is racy | **refuted** | `rdb-key-save-delay 100000000` is set on primary 0 *before* the replicate; cross-shard move forces a full sync that hangs in BGSAVE, so reploff stays ≤ 0 deterministically |
| C11 | With validity factor 0, an offset-0 migrated replica could win the election and the test would fail on `[s -4 role] eq {master}` | **dropped** | Election delay is `rank * 1000ms` plus 0.5–1s, so the rank-0 synchronized replica wins first in practice; the test explicitly tolerates and checks the scheduling race; mirrors upstream Valkey test design; no code defect |

### Verifier decision

**Nothing qualifies for a batched independent verifier.** No candidate survived the falsification pass, so there is no candidate proof for a verifier to attack. The diff does touch core failover-eligibility paths (the rubric's "high-risk change" disjunct), so if the orchestrator wants additional assurance for the *zero-finding conclusion itself*, it may run one verifier over the falsification log in §Candidates and dispositions — but strictly under the rubric's "give it the candidates" framing, the list is empty.

### Would-be published review

*(Publication disabled — nothing was written. The exact payload that phase 6 would have submitted, as one forge-native review with `event: COMMENT`, `commit_id: c54fa4184e7db1ea30c91916f6c0aeb12b5c3f61`, and zero inline comments:)*

**Summary body (verbatim):**

```markdown
**Approved (advisory)** — no required changes.

**Intent:** Prevent a replica re-pointed to a master in another shard (replica migration, `CLUSTER REPLICATE`, or sub-replica flattening) from failing over with stale replication history, by discarding the cached master and resetting `repl_down_since` until the first full sync with the new master completes.

**Issue fit:** Not assessed — no originating issue was available for this pull request; reviewed against the behavior stated in the PR body.

**Coverage:** Complete merge-base diff reviewed (5 files); failover data-age and rank logic, cached-master lifecycle, offset reporting, all `repl_down_since` consumers, the new test's helpers and log-message targets, and CI wiring inspected.

**Reviewed:** `c54fa4184e7db1ea30c91916f6c0aeb12b5c3f61` against merge-base `065d397030712fe216e795720ae0affd3211212c`.

<!-- review-run head=c54fa4184e7db1ea30c91916f6c0aeb12b5c3f61 base-ref=unstable base-sha=065d397030712fe216e795720ae0affd3211212c merge-base=065d397030712fe216e795720ae0affd3211212c rubric=codex-81de4f2 issues=none coverage=complete -->
```

**Inline comments:** none — zero findings, zero questions.

### Notes

- The PR is already merged; per the packet, status was derived as for an open PR and nothing was published. With complete coverage and no blockers/questions, the derived status is `Approved`; since gating is not authorized and the default event is `COMMENT`, the body carries `(advisory)`.
- No base-branch guidance files apply (`docs/agents/issue-tracker.md` does not exist at the base SHA); the repository has no per-path instruction files affecting these paths.
- Prior third-party state (sundb APPROVED, shun-lee's detailed LGTM) is consistent with this run's conclusions; shun-lee's ordering claims about `freeClient`→`replicationCacheMaster` and `replicationSetMaster` were independently re-verified here against source, not taken on trust.
- The second commit (`c54fa4184`, "remove unnecessary check") deletes a counter-assertion (`count_log_message -7 "I'm a sub-replica"`) that was not guaranteed to hold for the non-sub-replica variant — a justified test-stability fix.
- The new test is heavyweight (12 clusters × 8 nodes, redis-cli rebalance, SIGSTOP/shutdown) but follows existing `unit/cluster` conventions and runs in PR CI's suite (`./runtest --tags -slow`); no `-slow` tag is needed by local convention.
- Offline-run limitation: actual CI run results for this PR could not be read; CI wiring was verified from workflow files only. The new test was not executed (would build artifacts/spawn servers), so test-pass evidence rests on the code-level cross-checks above plus the PR's merged state.

## Notes on the run

- Highest candidate count of the four runs (11), all killed by self-falsification inside one context.
- The only run to explicitly note the rubric's "high-risk change" disjunct could have triggered a
  verifier even with an empty survivor list, and framed its empty list as the reason it did not.
- Worktree left clean; nothing published.
