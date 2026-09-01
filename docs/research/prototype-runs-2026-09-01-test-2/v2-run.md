# v2 run — `code-review-publish-2` against `redis/redis#15680`

**2026-09-01.** Data only. Not published to the PR.

## Metadata

| | |
| --- | --- |
| Skill | `code-review-publish-2` (PR #14, at commit `f42f708`) |
| Architecture | axis finders → 1 mandatory fresh-context verifier (skipped: finders returned no candidates) |
| Originating issue | none → Requirements axis `Not applicable`, Code axis runs alone (per SKILL) |
| Agents spawned | 1 (Code finder; no verifier) |
| Total sub-agent tokens | unavailable from this harness |
| Tool uses (self-reported) | ~46 |
| Wall clock (orchestrator-measured sub-agent span) | ~9 min |
| Candidates raised | 0 |
| Verdicts | none — verify step skipped by rule |
| Findings for publication | **0** |
| Questions | 0 |
| Coverage | complete (5/5 files) |
| Derived status | **Approved (advisory)** — coverage complete, nothing blocking, no open questions |

## Code finder — full report (verbatim)

All reads complete, diff and enclosing code analyzed. Final report:

### Metadata

| | |
| --- | --- |
| Total tool invocations | ~46 (3 initial reads + 43 bash/read calls; all read-only git/grep/sed) |
| Approx elapsed time | ~20 minutes (sub-agent self-estimate; orchestrator measured ~9 min) |
| Files inspected | `redis.conf` (diff hunk), `src/cluster_legacy.c` (`clusterSetMaster`, `updateShardId`, `assignShardIdToNode`, `clusterHandleSlaveFailover`, `clusterGetSlaveRank`, `clusterBuildMessageHdr`, `clusterProcessPacket` sub-replica safeguard, role-update block), `src/replication.c` (`replicationSetMaster`, `replicationUnsetMaster`, `replicationCacheMaster`, `replicationCacheMasterUsingMyself`, `replicationDiscardCachedMaster`, `replicationResurrectCachedMaster`, `replicationHandleMasterDisconnection`, `replicationCreateMasterClient`, `replicationGetSlaveOffset`, `slaveTryPartialResynchronization`, rdb-channel handshake, full-sync completion), `src/server.h` (diff hunk), `src/server.c` (INFO replication section), `tests/unit/cluster/replica-migration.tcl` (full, head), `tests/test_helper.tcl` (discovery mechanism), base `CONTRIBUTING.md` |
| Commands I could not run | No compile/test run (would create untracked build artifacts inside the repo tree; the run forbids writing to the repository), no `gh`/network (forbidden by run design; origin is a local path) |

### Manifest coverage

| File | Status | Reason |
| --- | --- | --- |
| `redis.conf` | reviewed | Diff hunk read; added doc paragraph checked against actual failover behavior (`cluster_legacy.c:4454-4480` data_age check) — accurate, including the "automatic" qualifier (manual failover intentionally bypasses) |
| `src/cluster_legacy.c` | reviewed | Enclosing function `clusterSetMaster` read in full at head; all 6 callers identified; mechanism traced end-to-end (shard capture, cached-master discard, `repl_down_since` consumers) |
| `src/replication.c` | reviewed | Only hunk is removal of a now-redundant forward declaration (moved to `server.h`); verified definition still exists and declaration in `server.h` matches |
| `src/server.h` | reviewed | Declaration added in the replication prototype block next to `replicationCacheMaster`; matches definition signature |
| `tests/unit/cluster/replica-migration.tcl` | reviewed | Full 378-line file read; second commit's removed check analyzed; log-message patterns cross-checked against real log strings; test discovery confirmed via `glob` in `tests/test_helper.tcl:39` |

### Candidates

None.

The Code axis review found nothing meeting the candidate bar. The things I specifically tried to convict and could not:

1. **Ordering of `replicationDiscardCachedMaster()` after `replicationSetMaster()`** — correct: `replicationSetMaster()` synchronously frees the old master client (caching it via `freeClient` → `replicationCacheMaster`), synthesizes a cached master from my own replid when `was_master`, and starts a non-blocking connect; the PSYNC handshake decision (`slaveTryPartialResynchronization`, src/replication.c:2952-2982) happens later in the event loop, after the discard, so a cross-shard replica always sends `PSYNC ? -1`.
2. **`server.repl_down_since = 0` while disconnected** — its only logic consumer is the data-age computation at `src/cluster_legacy.c:4460` (`(unixtime - repl_down_since) * 1000`), which is precisely the intended blocking effect. Every other consumer (INFO, src/server.c:6865, 6904) already treats 0 as "never down" and prints `-1`/`0`, so no bogus stats. This also makes the migrated replica consistent with a never-synced fresh replica, matching the `redis.conf` text.
3. **"Reports offset zero until first sync" claim** — holds in both disk-based and diskless (rdb-channel) modes: `replicationGetSlaveOffset()` (src/replication.c:5056) returns 0 because neither `server.master` nor `cached_master` is set during transfer; `replicationCreateMasterClient` (which sets `reploff = master_initial_offset`) is only called at full-sync completion, inside one event-loop turn.
4. **shard_id adoption race** — I checked whether gossip could advance `myself->shard_id` to the new shard before `clusterSetMaster` runs, making `shard_changed` a false negative. It cannot: `updateShardId` propagates to a node's replicas only in the `node->slaveof == NULL` branch (src/cluster_legacy.c:944-951), and a master's shard_id only changes when it demotes (at which point `slaveof != NULL`), so a replica still following the old master never adopts the new shard id early.
5. **Second commit ("remove unnecessary check")** — removes a timing-dependent assertion that replica 7 never logs "I'm a sub-replica!" in the non-sub-replica variant; in that variant the grandmaster safeguard can legitimately fire before replica migration re-points 7, so the removed check was flaky, not protective. Correct removal.
6. **Standards** — no `CLAUDE.md`, `AGENTS.md`, or `CODING_STANDARDS.md` exists at the base; `CONTRIBUTING.md` at base is CLA text only. No documented repository standard governs these files, so no standards findings are possible.

### Notes

- **No originating issue**: per run instructions the Requirements axis was treated as `Not applicable` and nothing was derived from the PR body. I did, however, use the body's behavioral claims (offset 0, repl_down_since reset, validity-factor semantics) as claims to verify against the code, and all of them check out — including the shun-lee comment's ordering claim, which I re-derived independently rather than trusting.
- **Base-branch guidance**: checked `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `CODING_STANDARDS.md` at `065d3970` via `git show` — none exist except the CLA-only CONTRIBUTING.md. No scoped guidance files under `src/` or `tests/`.
- **Deliberate-behavior dispositions (gate 8)**: manual `CLUSTER FAILOVER` by an unsynchronized cross-shard replica remains possible (the data-age check is explicitly bypassed for manual failovers, src/cluster_legacy.c:4472-4478) — pre-existing behavior, operator-initiated, and the PR body scopes its protection to *automatic* failover. The `redis.conf` sentence "a replica that has not completed its first synchronization ... is considered to have been disconnected since forever" is broader than the code (same-shard re-points do not reset `repl_down_since`), but the same-shard case is intentionally allowed to partial-resync (its history is valid), and the divergence converges as soon as sync completes — I judged this an intentional model simplification, not a defect, but flag it here in case the orchestrator disagrees.
- **Tests not run**: I chose not to build or run the new test file — a build would deposit object files in the clone, which this run forbids. Static verification was done instead: the log-string assertions (`"Start of election"`, `"Currently unable to failover: Disconnected from master for longer than allowed"`, `"I'm a sub-replica!"`, `"rank #0"`, `"offset 0"`) all match real log lines in `cluster_legacy.c`; the 8 `start_cluster` scenario combinations match the 2×2×2 parameter matrix of the two procs; test discovery is by glob (`tests/test_helper.tcl:39`), so the new file runs without a manifest edit.
- The change is small, matches its stated design, mirrors merged Valkey #885/#944, and carries a thorough test matrix. I found no defect I could state with a concrete trigger, per the rubric's asymmetric bar.

## Would-be published review

Per the skill, phase 4 belongs to the orchestrator; with no candidates, no verifier, and complete
coverage the derived status is `Approved` under `publishing.md`'s ladder, event `COMMENT`:

**Approved (advisory)** — no findings.

Orchestrator note: the finder flagged one judgment call in its Notes — the `redis.conf` sentence
about first-synchronization state being broader than the code — and did not raise it as a candidate.
Under the skill's rules an unraised observation does not become a question; it is recorded here as
run data only.

## Notes on the run

- Requirements axis was `Not applicable` by the skill's own no-issue rule; the finder still used the
  PR body's behavioral claims as claims to check (all passed).
- The finder acquitted candidates using base-branch reading (no standards files exist at base) and
  by re-deriving the shun-lee comment's ordering claims from source instead of trusting them.
- No verifier ran: the skill skips step 3 when finders return no candidates on a first review.
- Worktree left clean; nothing published.
