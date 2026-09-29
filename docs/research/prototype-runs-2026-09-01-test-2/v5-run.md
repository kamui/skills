# v5 run — `snapshot-path-omitted` against `redis/redis#15680`

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

**2026-09-01.** Data only. Not published to the PR.

## Metadata

| | |
| --- | --- |
| Skill | `snapshot-path-omitted` (PR #17, workflow `v5-2`) |
| Architecture | 1 integrated reviewer + consequence-triggered batched fresh-context verifier (not triggered) |
| Agents spawned | 1 (no verifier — zero survivors) |
| Total sub-agent tokens | unavailable from this harness |
| Tool uses (self-reported) | 37 |
| Wall clock (orchestrator-measured sub-agent span) | ~6 min |
| Candidates raised | 8 (all dropped in primary falsification) |
| Candidates surviving primary falsification | 0 |
| Verifier verdicts | none |
| Findings for publication | **0** |
| Questions | 0 |
| Coverage | complete (5/5 files; tests statically verified, not executed) |
| Derived status | **Approved (advisory)** — no findings |

## Full reviewer report (verbatim)

# Review report — redis/redis#15680 (prototype `snapshot-path-omitted`, calibrated hybrid v5)

### Metadata

| Item | Value |
| --- | --- |
| Total tool invocations | 37 (5 `read`, 32 `bash`; no verifier, no network) |
| Files inspected | `/tmp/redis-phase1-packet.md`; skill + both references + `context_fingerprint.py` (usage only); `redis.conf` (diff); `src/cluster_legacy.c` (diff, `clusterSetMaster`, `clusterHandleSlaveFailover`, `clusterGetSlaveRank`, `updateShardId`, all 6 `clusterSetMaster` call sites, cant-failover log strings, base `clusterSetMaster`); `src/replication.c` (diff, `replicationSetMaster`, `replicationCacheMaster`/`...UsingMyself`, `replicationDiscardCachedMaster`, `replicationResurrectCachedMaster`, `replicationGetSlaveOffset`, `cancelReplicationHandshake`, `repl_down_since` sites, base decl); `src/server.h` (diff); `src/server.c:6845–6915` (INFO replication), `src/server.c:2517`; `tests/unit/cluster/replica-migration.tcl` (full); `tests/support/util.tcl`, `tests/support/cluster_util.tcl`, `tests/test_helper.tcl`; `runtest`, `runtest-cluster`; `.github/workflows/ci.yml`, `daily.yml` (grep); base `CONTRIBUTING.md` |
| Commands not run | `make`/`runtest*` — building redis creates build artifacts and running the new 8-cluster tests is disproportionate for a sandboxed review; tests were statically inspected instead. `gh`/network/fetch — forbidden by the controlled-run contract. Verifier — no qualifying survivor (see §6). Nothing else material was skipped. |

### Coverage

| File | Disposition |
| --- | --- |
| `redis.conf` | reviewed — doc paragraph verified against actual `data_age` behavior (cluster_legacy.c:4455–4474) |
| `src/cluster_legacy.c` | reviewed — full patch plus enclosing function, callers, failover eligibility/rank/offset code |
| `src/replication.c` | reviewed — deleted forward declaration, plus every `repl_down_since`/cached-master interaction |
| `src/server.h` | reviewed — declaration moved from `replication.c` to shared header; no duplicate left (`grep` across `src/`) |
| `tests/unit/cluster/replica-migration.tcl` | reviewed — full 378-line file, helper procs, log-pattern strings vs server strings, `start_cluster` slot-allocator arity, negative srv-index semantics |

**Coverage: complete** (merge-base diff fully inspected; every risk-directed check has an evidence-backed outcome). Caveat recorded in §8: tests were statically verified, not executed.

### Requirement ledger

**Issue alignment:** unavailable — no originating issue (packet: no closing reference, no linked issue). Per SKILL phase 1, reviewed the code and state that issue alignment was unavailable. Repository guidance at base `065d3970`: no `AGENTS.md`, no `docs/agents/issue-tracker.md`; base `CONTRIBUTING.md` contains only generic process guidance — no repository-rule findings applicable to the changed paths.

PR-body claims / non-goals:

| Claim / non-goal | Disposition | Decisive evidence |
| --- | --- | --- |
| Cross-shard transition captured **before** `updateShardId()` adopts the new shard ID | met | `clusterSetMaster` head: `int shard_changed = memcmp(...)` precedes `updateShardId(myself, n->shard_id)` (cluster_legacy.c:5428, 5441) |
| Cached master discarded on cross-shard move | met | cluster_legacy.c:5445 `replicationDiscardCachedMaster()` inside `if (shard_changed)`, after `replicationSetMaster()` — which is what caches the old-shard history (`freeClient(server.master)` → `replicationCacheMaster`, replication.c:3627; or `replicationCacheMasterUsingMyself()` for a demoted master, replication.c:3651) |
| `repl_down_since` reset to 0 ("never synchronized", "disconnected since forever") | met | cluster_legacy.c:5453; "0 = down since forever" is the established interpretation (server.c:2517 comment; `INFO` guards `repl_down_since ? ... : -1` at server.c:6904–6905) |
| Until first sync succeeds, replica reports offset zero and is ranked behind established-offset replicas (validity factor 0) | met | `replicationGetSlaveOffset()` returns 0 when `master==NULL && cached_master==NULL` (replication.c:5056–5067); `clusterGetSlaveRank()` counts peers with greater offset (cluster_legacy.c:4279–4293); data-age check bypassed when `cluster_slave_validity_factor` is 0 (cluster_legacy.c:4468–4476) |
| Non-zero validity factor prevents **automatic** failover until first sync succeeds | met | `data_age = (unixtime − repl_down_since) × 1000` with `repl_down_since=0` → astronomically above threshold; only manual failover bypasses (cluster_legacy.c:4460, 4468–4476); persists across connect retries (`cancelReplicationHandshake` never touches `repl_down_since`) |
| Same-shard failovers untouched (implied non-goal: partial resync preserved) | met | `shard_changed` false for same-shard re-points (promotion of co-shard replica, same-shard sub-replica flattening, `CLUSTER REPLICATE` to current shard); verified across all six `clusterSetMaster` call sites |
| Tests cover migration, `CLUSTER REPLICATE`, sub-replica flattening, both validity factors | met | `test_migrated_replica` ×8 (migration + flattening, factors 0/10, shutdown/sigstop); `test_nonempty_replica` ×4 with explicit `R 7 cluster replicate` (line 272) |

### Risk checks

| Check (rubric-derived, from actual paths) | Outcome |
| --- | --- |
| Stale state → failover with invalid history (the PR's whole point) | **Positive:** cross-shard re-point now forces offset 0 + data-age "forever"; stale cached history cannot win an election. Evidence: cluster_legacy.c:5444–5453, 4455–4476 |
| False positive on same-shard failover (availability regression) | **Negative (no defect):** `shard_changed` is false for same-shard re-points; partial resync path untouched. Verified via `updateShardId` semantics and all 6 call sites (2512, 2531, 3263, 4693, 6311, 6419) |
| Ordering of discard vs `replicationSetMaster` (does the old master get re-cached after the discard?) | **Negative:** caching happens *inside* `replicationSetMaster` (line 3627/3651); the PR discards strictly after; no reentrancy window (cluster work is deferred via `clusterDoBeforeSleep`) |
| Compatibility / observable contracts (`INFO replication`, replicationCron consumers of `repl_down_since == 0`) | **Negative:** all consumers guarded — server.c:6865 (`current_disconnect_time = repl_down_since ? ... : 0`), 6904 (`... : -1`); cluster_legacy.c:4460 is the intended consumer; no other readers (repo-wide grep) |
| Destructive migration / rollback / secrets / auth / path handling | **Negative:** none present in the diff |
| Serialization/version skew (older peers without shard IDs) | **Negative (conservative):** if `n->shard_id` is zeros while `myself->shard_id` is real, `shard_changed` is true → discard + reset, which is the safe direction; a fresh node (both zero) has no cached master and `repl_down_since` already 0 from init |
| CI exposure of new tests | **Positive:** `unit/cluster` is in `test_dirs` of `test_helper.tcl:28–36`, so PR CI (`runtest --tags -slow`) runs the new tests; cluster tests also run in `daily.yml` `runtest-cluster` |

### Candidates and dispositions

Every candidate raised, with falsification outcome. **Zero survivors.**

| # | Candidate | Falsification outcome |
| --- | --- | --- |
| C1 | Discard placed *after* `replicationSetMaster()` is too late / wrong — old history might survive or the discard might be discarded again | **Dropped.** Caching occurs inside `replicationSetMaster` (both the replica case via `freeClient(server.master)`→`replicationCacheMaster` and the demoted-master case via `replicationCacheMasterUsingMyself`); the PR's discard is the last writer and covers both. Matches shun-lee's independent analysis. |
| C2 | `repl_down_since = 0` while disconnected breaks `INFO replication` (`master_link_down_since_seconds` ≈ 1.7 billion) and `current_disconnect_time` | **Dropped.** Both consumers are already guarded for 0 (server.c:6865, 6904) and the "0 = down since forever" reading is pre-existing (server.c:2517). `master_link_down_since_seconds:-1` during connect retries is consistent with intent. |
| C3 | Same-shard failovers regress (cached master wrongly discarded → lost partial resync) | **Dropped.** `shard_changed` is false whenever shard IDs match; promotion of a co-shard replica and same-shard flattening preserve history. |
| C4 | Commit 2 (`remove unnecessary check`) weakens the test by deleting the "never logs *I'm a sub-replica*" assertion in the sigstop/non-sub case | **Dropped.** Deliberate (commit message). Substantively justified: in the non-sub case replica 7's re-point to primary 0 may legitimately traverse the flattening path (or the direct migration path), so the assertion was race-dependent; removing it removes a flaky assertion, not a guard on the code under test. Test-only; fails rubric conditions 6 and 7. |
| C5 | Manual failover (`CLUSTER FAILOVER`) still bypasses the data-age check on an unsynced cross-shard replica → promotion with unrelated data remains possible | **Dropped.** Pre-existing, operator-directed behavior, explicitly unchanged by this PR; the PR body and `redis.conf` claim scope "automatic failover" only. Not introduced here; not a violation of an explicit non-goal. |
| C6 | Cross-shard re-point to a peer with an all-zero `shard_id` (or stale shard IDs) misclassifies `shard_changed` | **Dropped.** Misclassification in either direction is either conservative (spurious discard → extra full sync, availability cost only) or a no-op (fresh node has no cached history). No proven consequence. |
| C7 | `verify_log_message -7 "*I'm a sub-replica!*"` / `*Start of election*offset 0*` / `*Disconnected from master for longer than allowed*` patterns don't match actual server log strings | **Dropped.** Each pattern verified against the emitting code: cluster_legacy.c:2529/3261, 4358 ("Start of election delayed ... (rank #%d, offset %lld)"), 4339+4357. Helper semantics (`string match` over the log tail, negative `srv` indices, `start_cluster` 5-arg slot-allocator form) all confirmed in `tests/support/*.tcl` and `test_helper.tcl`. |
| C8 | `replicationDiscardCachedMaster` declaration duplication (removed from `replication.c`, added to `server.h`) | **Dropped.** Exactly one declaration remains, in `server.h:3589`, visible to both TUs; no other forward declaration of it exists. |

### Verifier decision

**No survivor qualifies for verification.** No candidate survived falsification at all; consequently there is no `must-fix` survivor and no survivor involving security/authorization, data loss or corruption, destructive migration, or an externally observable compatibility break. Artifact names alone do not trigger, and none of the dropped candidates reached rendering. **A clean run needs no verifier — no batched verifier run was required or performed.** There are also no ordinary `consider` survivors to batch.

### Would-be published review

**Status derivation:** no `must-fix` findings, no open questions, coverage complete → `Approved`. Publication disabled by the run; default (non-gating) event would be `COMMENT`, so the body carries `(advisory)`. Nothing is blocked pending verification (no verification required). In a live run, phase 5's head re-fetch would precede the write.

Would-be summary body (verbatim; no inline comments):

```markdown
**Approved (advisory)** — clean review; no findings.

**Intent:** Prevent replicas from being promoted with stale or unrelated data when
they are re-pointed to a master on another shard (replica migration, `CLUSTER
REPLICATE`, sub-replica flattening), by discarding the cached master and reporting
offset zero until the first full sync with the new master succeeds.

**Issue fit:** No originating issue; reviewed the code directly. The change
implements the described behavior on every `clusterSetMaster` re-point path, and
same-shard failovers are untouched.

**Coverage:** Complete merge-base diff reviewed; failover eligibility, rank,
offset reporting, cached-master lifecycle, INFO consumers, all six re-point call
sites, the new test file against helper procs and server log strings, and CI test
exposure were inspected. Tests were statically reviewed, not executed.

**Reviewed:** `c54fa418` against merge-base `065d397`.

<!-- review-run head=c54fa4184e7db1ea30c91916f6c0aeb12b5c3f61 base-ref=unstable base-sha=065d397030712fe216e795720ae0affd3211212c merge-base=065d397030712fe216e795720ae0affd3211212c workflow=v5-2 context=8645d6297bc7bcbc4beca7fe5829214198f432fabeef89f30e9dfca0da50d884 issues=none coverage=complete -->
```

### Notes

- **Verifier-trigger classification:** none of the C1–C7 candidates was proposed as `must-fix`, and none implicated the consequence classes; the nearest miss was C3/C1 (cached-master lifecycle — data-loss-adjacent *if broken*), but falsification proved the change correct, and the verification trigger applies to surviving candidates only.
- **Fingerprint input classification:** `issues=none` (no originating issue, per packet). `specs=[]`; `guidance=[]` — base branch has no `AGENTS.md`/`docs/agents/*` and `CONTRIBUTING.md` contains no path-scoped rules. The digest was computed from the packet's verbatim PR body and the four prior-review comments; the packet gives no timestamp for `sundb`'s review body (recorded as null), so the digest is faithful to the packet as reviewed, not to live forge state.
- **Base-branch guidance findings:** none — no instruction files govern the changed paths at `065d3970`.
- **Test-execution gap:** the new tests (and the removed assertion) were verified statically (helper existence/signatures, log-string matches, `start_cluster` slot allocation covering 0–16383, negative-index `srv` semantics) because building redis was disallowed in this sandbox. This is recorded in the coverage note; it is not an unresolved evidence-affecting tool failure, but a real publication would ideally have CI green as corroboration — CI's PR path does run `unit/cluster`.
- **Base-branch evaluation:** all guidance/code evaluation (e.g., `replicationSetMaster`, `updateShardId`, `INFO` guards) was checked against `065d3970` where the head version could differ; no drift was found affecting any disposition.
- Prior third-party state (sundb APPROVED, shun-lee LGTM) was read as evidence; no thread exists for the posting identity (`kamui`), so no replies are due and no re-review state carries.

## Notes on the run

- Fastest of the four runs (~6 min) with the second-highest candidate count (8), all killed in
  primary falsification.
- Only run to record its fingerprint-input classification decision (specs vs guidance vs evidence)
  as an explicit ambiguity note.
- Worktree left clean; nothing published.
