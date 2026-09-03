# v2a run — `code-review-deep-publish` against `redis/redis#15680`

**2026-09-02.** Data only. Not published to the PR. See
[`addendum-2026-09-02.md`](addendum-2026-09-02.md) for run conditions, model/harness, and the
dev-set caveat that applies to this run.

## Metadata

| | |
| --- | --- |
| Skill | `code-review-deep-publish` (research nickname **v2a**, "Panel line"; [PR #18](https://github.com/kamui/skills/pull/18), branch `t3code/prototype-code-review-publish-2a`, pinned commit `87c68a9`) |
| Includes fixes | `326ef6f` "Require paired peer-contract sweeps" (handoff 5); `940aa2c` "Sweep every changed contract, on both axes" (DESIGN.md §C9) |
| Architecture | 2 axis finders in parallel (Code, Requirements) → 1 mandatory fresh-context verifier |
| Model | `claude-fable-5-1` on every agent (orchestrator, both finders, verifier), verified from the harness's sub-agent transcripts — not the Sonnet 5 tier intended; see the addendum |
| Agents spawned | 4 on the completed path (orchestrator, Code finder, Requirements finder, verifier); the orchestrator was killed by the session rate limit after spawning the finders, and the Requirements finder was resumed once — see "How this run was executed" |
| Sub-agent tokens | **partially instrumented.** Verifier 54,052 (13 tool uses, 223,422 ms / ~3.72 min). Requirements finder, resumed segment only: 123,085 (1 tool use, 194,058 ms) on top of an uncaptured 42-tool-use first segment. Code finder (23 tool uses) and orchestrator (21 tool uses): tokens not captured — both were killed by the rate limit after finishing their work but before returning, and the harness reports usage only on a clean return. No comparable total exists |
| Tool uses (sub-agents) | 100 (orchestrator 21, Code finder 23, Requirements finder 42 + 1, verifier 13) |
| Wall clock | not a single span: attempt 1 ran ~16 min before the kill (17:25–17:41); the resumed Requirements finder ran ~3.2 min and the verifier ~3.7 min after the 22:20 reset |
| Candidates raised | 2 — Requirements 2, Code 0 |
| Verdicts | 2 confirmed · 0 plausible · 0 refuted · 0 merged |
| Findings for publication | **2** — P2 `consider`, P3 `consider` |
| Questions | 2 (Requirements "cannot tell from the code" bucket; never reach the verifier by rule) |
| Coverage | complete (5/5 files, both finders; tests reviewed statically, not executed, per the packet) |
| Requirements ledger | body-claims surrogate, 16 rows: met 13 · not met 0 · cannot tell 1 (plus 2 partial gaps raised as the candidates) |
| Axis outcomes | Requirements: `Findings`, with "issue alignment unavailable" · Code: `Passed` (zero candidates) |
| Derived status | **Approved (advisory)** — no `must-fix`; both questions judged unable to change the verdict (see "Status derivation") |

## Findings

### F1 — `requirements/sub-replica-flatten-shard-propagated-before-setmaster` — consider / P2

- **anchor** `src/cluster_legacy.c:5428`
- **fix** `src/cluster_legacy.c:5428`

The new guard compares `myself->shard_id` with the new master's shard id. When a demoted master's
PONG names a new master this node does not yet know, the role block leaves `sender->slaveof`
`NULL`, so the sender's shard-id ping extension takes `updateShardId`'s propagation branch and
rewrites `myself->shard_id` to the new shard *before* any `clusterSetMaster` call. When the
grandmaster later becomes known and the sub-replica safeguard flattens `myself` onto it,
`shard_changed` is 0 and neither the cached-master discard nor the `repl_down_since` reset runs —
the exact state the PR body says a flattened sub-replica must not carry into an election.

Verifier: **confirmed**, reconstructing the full path from the code (`:5428`, `:943-948`,
`:3226`, `:2782`, `:5437-5438`, `:3263`, `src/replication.c:3748`) and sharpening the trigger: the
window is not "same tick" but the whole handshake period, because a node learned by gossip sits in
the table under a random name with `CLUSTER_NODE_HANDSHAKE` and `clusterLookupNode(hdr->slaveof)`
fails for it throughout. The new tests never reach the path (every scenario is `start_cluster 4 4`
with all nodes known; no `CLUSTER MEET` in the file). Priority P2 and action `consider` kept: a
proven gap against the body's own sub-replica claim, but the merge consequence needs a node-join
race plus the new master failing before first sync; the ordinary flatten path is handled
correctly.

**Nothing in the original v2–v5 comparison raised this.** All four runs and both human reviewers
called the target clean. See the addendum's regression watch for the cross-prototype comparison:
v5a's own clean-verdict verifier found the same mechanism in this round and recorded it as an
observation with "no consequence traced".

### F2 — `requirements/conf-first-sync-rule-overgeneralizes` — consider / P3

- **anchor** `redis.conf:1795`
- **fix** `redis.conf:1795-1796`

The new conf sentence "A replica that has not completed its first synchronization with its current
master is considered to have been disconnected since forever" states a general rule; the code
produces that state only on process start and on a cross-shard `clusterSetMaster`. A same-shard
re-point keeps the disconnection timestamp from `replicationHandleMasterDisconnection`. Verifier:
**confirmed** by enumerating every writer of `repl_down_since`; P3 `consider` kept as a
documentation-scope drift whose next sentence already names the real trigger.

**This is the `redis.conf` scope item** the original comparison recorded as accurate but
sub-threshold (only v2's finder noticed it, as a note). This run's Requirements axis raised it as a
candidate and the verifier confirmed it; the Code axis independently routed the same fact to
observations. Both dispositions are defensible under the contract; the Requirements frame won
because the finder tied it to the body's scoping claim.

## Open questions (finder-side "cannot tell from the code" bucket; not verified by rule)

- **Q1** Whether the change matches what was agreed in the linked redis/redis#15530 review thread
  and whether the tests are faithful ports of Valkey #885/#944 — the referenced discussions are not
  in the repository and the clone is offline.
- **Q2** Whether the 12 new test blocks pass reliably under `cluster-node-timeout 1000`, given the
  "Currently unable to failover" log line is suppressed for `node_timeout + 5000` ms after the
  master's FAIL and the test waits up to 50 s. Reading cannot settle timing; the Code finder's
  ledger reached the same place from the other direction and recorded the thin margin as an
  observation.

## Status derivation (session judgment call)

`publishing.md`'s ladder: no unsettled `must-fix`; coverage complete; then "any open question whose
answer could change the verdict → `Needs Information`", otherwise `Approved`. The session, acting
as orchestrator for the compile step, judged that neither question can change the verdict: Q1's
answer is about lineage, not correctness, and Q2's worst-case answer is a flaky test, which lands
as a `consider` finding and holds nothing back. Hence **`Approved (advisory)`** (gating not
authorized; `COMMENT` event). The alternative reading — any open question holds the review at
`Needs Information` until answered — would give `Needs Information`; this is recorded so the
comparison can apply either rule consistently. A `consider`-only review with two published
questions is the shape either way.

## The `redis.conf` item and the third-party state, per finder

| | Requirements finder | Code finder | Verifier |
| --- | --- | --- | --- |
| `redis.conf:1795` first-sentence scope | candidate R2 (P3 consider), tied to the body's cross-shard scoping | ledger row "Doc sentence … is broader than the code" → **observation** (not a candidate) | confirmed R2; own observations do not repeat it |
| `sundb` `APPROVED` (empty) and `shun-lee` LGTM ordering claims | re-derived from source: `src/cluster_legacy.c:5428` before `:5439`; discard at `:5446` after `replicationSetMaster()` at `:5441`, cache created at `src/replication.c:3650-3651` / `freeClient → replicationCacheMaster`; `connectWithMaster()` only schedules | re-derived independently: ledger rows 1 and 3 (`connectWithMaster()` non-blocking, `syncWithMaster` handler; `:5428` before `:5439`) | re-derived for F1's ordinary-path acquittal (`:3234` runs with `sender->slaveof` set, non-propagating branch) |

Neither finder's ledger cites the comments as evidence; both treated them as claims to check.

## Would-be published review

Summary body (first line carries the status because the event is `COMMENT`):

> **Approved (advisory)** — retrospective review of a merged change; 2 advisory findings, 2 open
> questions; issue alignment unavailable (no originating issue; reviewed against the body's claims
> and non-goals).
>
> The change does what the body says on every path the new tests exercise: the cross-shard
> transition is captured before the shard id is adopted, the cached master is discarded after it
> is created, and a never-synced replica reports offset zero and fails the data-age check under a
> non-zero validity factor. One gap survives verification: the guard keys on `myself->shard_id`,
> which the shard-id ping extension can rewrite ahead of the flatten when the grandmaster is still
> in handshake, so a sub-replica flattened during a node-join race skips both resets (F1). The
> conf paragraph also states the "since forever" rule more broadly than the code applies it (F2).
> Deal with F1 first; F2 is a rewording.
>
> Requirements — `Findings` (issue alignment unavailable): F1 `src/cluster_legacy.c:5428` P2
> consider; F2 `redis.conf:1795` P3 consider. Code — `Passed`.
>
> ## Observations
> These are accurate observations, not findings — no action is requested.
> - After a cross-shard move `INFO replication` reports `master_link_down_since_seconds:-1` and
>   excludes the gap from `total_disconnect_time` until first sync — `src/server.c:6904-6905`.
> - A replica restarted between a cross-shard move and its first full sync rebuilds a cached master
>   from the RDB and re-attaches without passing `clusterSetMaster`, so it reports the old shard's
>   offset until the sync completes; unchanged by this diff — `src/server.c:7819`.
> - The new tests exercise only the empty-master form of replica migration; the orphaned-master form
>   shares `clusterSetMaster` but is disabled in every block by `cluster-migration-barrier 999` —
>   `tests/unit/cluster/replica-migration.tcl:198`.
>
> ## Open questions
> - Q1 — lineage against redis/redis#15530 and Valkey #885/#944 (not checkable offline).
> - Q2 — reliability of the 12 new blocks under `cluster-node-timeout 1000` given the
>   `node_timeout + 5000` ms log suppression at `src/cluster_legacy.c:4333-4336`; settle by
>   running `./runtest --single unit/cluster/replica-migration` repeatedly.
>
> Run: head `c54fa4184`, base `unstable` @ `065d39703`, merge-base identical; coverage 5/5;
> candidates 2, confirmed 2, refuted 0; publication disabled (research run).

Line comments would carry F1 and F2 in full at their anchors. Observations were capped at three of
the nine observation-shaped items the two finders and the verifier produced; the six dropped are
all in the verbatim reports below.

## How this run was executed

- **Attempt 1 (orchestrated, 17:25).** The session dispatched one orchestrator sub-agent from
  `/tmp/handoff3/dispatch-v2a-target2.txt`. It read the skill, packet, references, and base
  `CONTRIBUTING.md`; wrote the shared block (`/tmp/handoff3/v2a-target2-shared-block.md`, 31 KB,
  pinned identity, manifest, full diff, prior review state, the whole `CONTRIBUTING.md` as the
  applicable guidance, "there is no originating issue") and the two axis blocks; and spawned both
  finders in parallel. The Code finder completed its review and wrote its report to
  `/tmp/handoff3/v2a-target2-code-finder-report.md` but was killed by the session rate limit before
  returning it; the Requirements finder was killed mid-investigation (42 tool calls in); the
  orchestrator was killed while waiting. An earlier 13:13 dispatch had been killed before reading
  anything.
- **Attempt 2 (resumed, 22:21).** After the limit reset the session resumed the Requirements
  finder in place, with its context intact, by message; it finished its remaining reads and
  returned its report (also written to `/tmp/handoff3/v2a-target2-req-finder-report.md`). The
  session then built the verifier prompt programmatically from the two finder report files —
  stripping every `support` line (checked mechanically: zero `support` fields in
  `/tmp/handoff3/dispatch-v2a-target2-verifier.txt`) and passing both claims verbatim with the PR
  body as spec surrogate — and dispatched the verifier as a fresh sub-agent. Dedup (none), axis
  outcomes, and the status derivation were done by the session per `verify.md` / `publishing.md`.
  The orchestrator was not resumed.
- **Guidance membership:** the orchestrator treated base `CONTRIBUTING.md` as the sole applicable
  guidance file and included it in full in the shared block; both finders acquitted it as imposing
  no code standard (CLA plus process text). No `AGENTS.md`, `CLAUDE.md`, or scoped equivalents
  exist at base.
- **Clone hygiene:** `/tmp/handoff3/run-v2a-target2` was `git status`-clean at `c54fa4184` before
  every dispatch and after the verifier returned. No build or test execution by any agent.
- **What the interruption changes:** finders' inputs were byte-identical (the orchestrator's saved
  prompt files); the Requirements finder's context was continuous across the resume; the verifier
  received only the finders' final claims. Cost figures are incomplete (see Metadata) and the
  finders' wall clock overlapped only in attempt 1.

## Mechanism checklist

- **C2 (No-issue rule) — confirmed.** The orchestrator's Requirements axis block told the finder
  to apply the brief's "No issue" section; the finder opened with "Issue alignment is unavailable",
  built a 16-row body-claims ledger (author claims A1–A11, scope boundaries S1–S2, bot-only claims
  B1–B2), tested the non-goals as boundaries, inferred nothing from the diff, and the would-be
  summary carries "issue alignment unavailable" beside the axis outcome.
- **C3 (Disposition ledger) — confirmed.** Code finder: 21 rows (0 candidates, 18 acquittals, 3
  observations). Requirements finder: 24 rows (2 candidates, 2 questions, 2 observations, 18
  acquittals), plus the 16-row claims ledger and a 3-row changed-contract table.
- **C5 (Observations) — confirmed, with a split.** The `redis.conf` item landed in the Code
  finder's Observations (as the original comparison's evaluation hoped a calibrated run would do)
  *and* as a verifier-confirmed P3 `consider` finding from the Requirements axis. Nine
  observation-shaped items in total across both finders and the verifier; three would publish.
- **C9 (Changed-contract sweep) — demonstrated, no stale peer.** The Requirements finder wrote
  three contracts (the conf rule text, the prototype relocation, the `clusterSetMaster`
  post-condition) with paired searches and every live peer dispositioned; the Code finder's
  sync-drift section covered the same ground and found no stale peer. Correct outcome on a target
  with no known drift.
- **Pole intact — confirmed, with the execution deviation above.** Both finders ran to completion
  (Requirements after a resume); both candidates received exactly one verifier verdict; `support`
  withheld, checked mechanically. The "cannot tell" bucket (Q1, Q2) correctly bypassed the
  verifier.
- **C1 (Calibration) and C4 (Question routing) — not the target's mechanisms**, as expected; but
  note that C4's question channel did carry two finder-side questions here by rule, and C1's
  calibration outcome (a real code gap landing P2 `consider`, not `must-fix`) is consistent with
  the target-1 result.

## Verbatim reports

### Code-axis finder report

#### 1. Candidates

no candidates

#### 2. Sync drift from a changed rule

Qualifying contracts touched by the diff:

1. **`cluster-replica-validity-factor` documented rule (`redis.conf:1795-1800`)** — the diff adds a normative sentence ("A replica that has not completed its first synchronization with its current master is considered to have been disconnected since forever ... can't start an automatic failover until its first synchronization succeeds"). Nothing was retired; the pre-existing rule text ("since the last interaction with the master", `redis.conf:1785-1793`) is unchanged.
   - New-wording search (case-insensitive, whole repo at `review-head`): `since forever` and `first synchroni` → `redis.conf:1795-1799` (the change itself), `src/cluster_legacy.c:5450` (the change's own comment), `tests/unit/cluster/replica-migration.tcl:124` (the change's own test comment), `redis.conf:616` and `src/module.c:12727` (unrelated uses of "first synchronization" about replica data sets / module events — not restatements of the failover rule). Disposition: no stale peer.
   - Old-wording search (case-insensitive, whole repo at `unstable`): `validity.factor|validity_factor|repl_down_since|disconnected since` → `redis.conf:1788-1808` (canonical, updated by the diff), `src/config.c:3399` (config registration, no prose rule), `src/server.h:2505,2646` (field comments, still accurate), `src/server.c:2517` comment "Never connected, repl is down since EVER" (consistent with the new rule), `tests/cluster/tests/06-slave-stop-cond.tcl:37-38` and `tests/cluster/tests/includes/init-tests.tcl:52` (tests that set the config; they do not restate the rule), `tests/unit/acl.tcl:1592,1609` (unrelated "disconnected since"). Disposition: no stale peer.
2. The move of the `replicationDiscardCachedMaster` prototype from `src/replication.c` to `src/server.h` is a declaration relocation, not a rule, vocabulary, enum, schema field, or enumeration — does not qualify. `git grep` at `review-head` shows exactly one declaration (`src/server.h:3589`) and no other file-local prototype.
3. The new test file introduces no enumeration or vocabulary that other files restate (`proc my_slot_allocation` / `get_my_primary_peer` are defined nowhere else: `grep -rn "proc my_slot_allocation\|proc get_my_primary_peer" tests/` → only this file).

#### 3. Disposition ledger

| claim | falsification route | decisive evidence | disposition |
| --- | --- | --- | --- |
| PSYNC can be sent before `replicationDiscardCachedMaster()` runs because `replicationSetMaster()` already called `connectWithMaster()` | check whether connect/handshake is synchronous | `src/replication.c:3671` `connectWithMaster()` is a non-blocking connect; PSYNC is sent from the `syncWithMaster` handler (`src/replication.c:2980-2982`) on a later event-loop turn | acquitted |
| `myself->shard_id` may already equal `n->shard_id` on the sub-replica flatten path (cascade in `updateShardId` when a master's shard id changes), so `shard_changed` is false and the stale cached master survives | trace where `myself->shard_id` can be rewritten before `clusterSetMaster` | cascade only when `node->slaveof == NULL` (`src/cluster_legacy.c:942-948`); in `clusterProcessPacket` the role switch sets `sender->slaveof` (3234) before the sub-replica safeguard (3244), slots update (3295) and ping-ext (3349), so the demoted master already has `slaveof` set when its new shard id arrives; ping ext is per-sender and gossip carries no shard id | acquitted |
| `shard_changed` is computed after `updateShardId(myself, n->shard_id)` and therefore always false | read order in `clusterSetMaster` | `src/cluster_legacy.c:5428` computes before `5439` updates | acquitted |
| After discard, the replica still reports a non-zero offset during the stalled full sync because `server.master` is created early (rdb-channel replication) | find all `replicationCreateMasterClient` callers | only `src/replication.c:2740` (after payload load) and `4725` (synthesized cached master, then discarded); `replicationGetSlaveOffset()` returns 0 with neither master nor cached master (`src/replication.c` `replicationGetSlaveOffset`) | acquitted |
| `repl_down_since = 0` makes `data_age` overflow or misbehave in `clusterHandleSlaveFailover` | inspect the arithmetic | `src/cluster_legacy.c:4460` `(mstime_t)(server.unixtime - 0) * 1000` ≈ 1.7e12 fits `long long`; only compared against the validity window at 4471-4474 | acquitted |
| `repl_down_since = 0` is misread as "never connected" by some other consumer (Sentinel, cron, INFO) with a wrong outcome | enumerate all readers | readers are `src/cluster_legacy.c:4460` (intended) and `src/server.c:6865,6904` (INFO `master_link_down_since_seconds:-1`, which is the documented "since forever" semantics); Sentinel does not run in cluster mode | acquitted |
| A same-shard re-point (e.g. demoted master after failover) now loses its partial-resync ability | check gating | discard and reset are inside `if (shard_changed)` (`src/cluster_legacy.c:5445`); same-shard `memcmp` is 0 | acquitted |
| Previously a cross-shard PSYNC could legitimately succeed (shared history) and the change turns it into a needless full sync | look for a history-sharing cross-shard case | full sync clears `replid2` (`src/replication.c:2760-2762` comment "secondary ID / offset are cleared"), so a node that changed shard cannot carry the old shard's history; the pre-change PSYNC would be rejected anyway | acquitted |
| Cross-shard move disables automatic failover of an orphaned master (replica migration at 4693) until first sync, reducing availability | judge intent | `redis.conf:1795-1800` documents exactly this trade-off and the zero-factor escape; gate 8 (intentional) | acquitted |
| Doc sentence "A replica that has not completed its first synchronization with its current master is considered to have been disconnected since forever" is broader than the code | find a case where a never-synced replica has a non-zero `repl_down_since` | same-shard re-point (`shard_changed == 0`) goes through `freeClient(server.master)` → `replicationHandleMasterDisconnection` → `src/replication.c:3748` sets `repl_down_since = server.unixtime`; the replica is treated as disconnected since that instant, not forever, until its PSYNC completes | observation |
| A replica restarted between a cross-shard move and its first full sync still reports the old shard's offset (restart path bypasses `clusterSetMaster`) | check startup path | `src/server.c:7819` `replicationCacheMasterUsingMyself()` from RDB replid/offset; `src/cluster_legacy.c:5029` re-attaches via `replicationSetMaster` directly; behavior identical at base — criterion 4 fails | observation |
| Address-change re-point at `src/cluster_legacy.c:2344` bypasses the new logic | check whether it can cross shards | it re-targets the same `myself->slaveof` node with a new address; shard cannot differ | acquitted |
| Test precondition `[lindex [R 3 role] 4] <= 0` never holds | check ROLE reply | `roleCommand` returns `server.master ? reploff : -1` (`src/replication.c` `roleCommand` last line); `server.master` is NULL until `src/replication.c:2740` | acquitted |
| `wait_for_log_messages` in the validity-10 branches silently passes when the message never appears | read helper tail | `tests/support/util.tcl:256-262` calls `fail` on exhaustion | acquitted |
| "Currently unable to failover: Disconnected from master..." is never logged within the wait window | trace `clusterLogCantFailover` throttling | `src/cluster_legacy.c:4322-4337` logs once `fail_time` is older than `node_timeout + 5000` ms (≈6 s), well inside the 50 s wait | acquitted |
| Slot 0 may be rebalanced to primary 1 or 2 instead of primary 0, breaking `get_my_primary_peer 3 eq $addr` | reason about `--cluster rebalance` weight 0 tie-break | the entry node (`$addr` = primary 0) is loaded first by the cluster manager and receives the single surplus slot; same construction is used by `tests/unit/cluster/cli.tcl:349-393`; not a code defect in this change | acquitted |
| In the `sigstop` + validity-10 variants replica 4's `data_age` can exceed the 20 s allowance after ~8 s pause plus up to 10 s since the master's last PING, delaying its failover until `repl-timeout` (60 s) and risking the 50 s `wait_for_condition` | compute bounds | allowance `10000 + 1000*10` ms (`src/cluster_legacy.c:4471-4474`); worst case ≈ 18-21 s at resume vs 21 s limit; on overflow the link drops at `lastinteraction + 60 s` (`src/replication.c:185`) and failover follows ≈ 40-43 s after resume; passes on paper, margin is thin — no demonstrable failure | observation |
| `verify_log_message -7 "*I'm a sub-replica!*" 0` may fail because replica 7 could move via the 2512 path instead | check gating | `R 7 config set cluster-allow-replica-migration no` makes the 2512 branch require `sender_slots == migrated_our_slots` (5462 vs 1), so 7 can only flatten via 2531/3263 | acquitted |
| Removed local prototype of `replicationDiscardCachedMaster` leaves another TU without a declaration | grep | `git grep replicationDiscardCachedMaster review-head` → only `src/server.h:3589` declares; compiler territory anyway | acquitted |
| Double log "using my own master parameters to synthesize a cached master" immediately followed by "Discarding previously cached master state" on the demoted-master cross-shard path | judge severity | cosmetic; `src/replication.c:4712`, `4742`; a senior reviewer would not block on it | acquitted |
| `CONTRIBUTING.md` imposes a standard the change breaks | read base file | file is CLA + process text only; no code standard | acquitted |

#### 4. Observations

- The added sentence at `redis.conf:1795-1796` ("A replica that has not completed its first synchronization with its current master is considered to have been disconnected since forever") is broader than the code: only the cross-shard branch at `src/cluster_legacy.c:5453` zeroes `repl_down_since`, while a same-shard re-point keeps the disconnection timestamp set at `src/replication.c:3748`.
- A replica restarted after a cross-shard move but before its first full sync rebuilds a cached master from the RDB's replid/offset at `src/server.c:7819` and re-attaches through `src/cluster_legacy.c:5029` without passing `clusterSetMaster`, so it reports the old shard's offset until the full sync completes (behavior unchanged by this diff).
- In the `sigstop` variants with validity factor 10, replica 4 stays in `REPL_STATE_CONNECTED` while paused, so its `data_age` at resume is bounded by the master's 10 s PING period plus the ≈8 s pause against a 20 s allowance (`src/cluster_legacy.c:4471-4474`); if exceeded, failover waits for the 60 s `repl-timeout` at `src/replication.c:185` inside the test's 50 s `wait_for_condition` (`tests/unit/cluster/replica-migration.tcl:143`).

#### 5. Manifest

| file | status | reason |
| --- | --- | --- |
| `redis.conf` | reviewed | doc paragraph checked against `clusterHandleSlaveFailover` and both `repl_down_since` writers; over-breadth recorded as an observation |
| `src/cluster_legacy.c` | reviewed | `clusterSetMaster` read in full with all six call sites (2512, 2531, 3263, 4693, 6311, 6419), `updateShardId`, `clusterProcessPacket` ordering, `clusterHandleSlaveFailover`, `clusterGetSlaveRank`, `clusterLogCantFailover` |
| `src/replication.c` | reviewed | prototype removal; `replicationSetMaster`, `replicationHandleMasterDisconnection`, `replicationCacheMaster*`, `replicationDiscardCachedMaster`, `replicationGetSlaveOffset`, `roleCommand`, master-client creation sites |
| `src/server.h` | reviewed | prototype addition; no duplicate declaration elsewhere |
| `tests/unit/cluster/replica-migration.tcl` | reviewed | static review of both procs and all twelve `start_cluster` blocks against `tests/support/cluster_util.tcl`, `tests/support/util.tcl`, `tests/support/cli.tcl`, `tests/test_helper.tcl`; timing margin recorded as an observation |

Nothing left unfinished. No build, no test execution, no network, no clone mutation.


### Requirements-axis finder report

**Issue alignment is unavailable.** This pull request has no originating issue. The spec surrogate is the pull-request body's behavioral claims and explicit non-goals, walked from claim to code. The three external links in the body (redis/redis#15530 discussion, Valkey #885/#944) are not issues and were not reachable offline; they were not used as spec. The Cursor bot summary was treated as a restatement of the author's claims (weight: corroborating, not additional), except where it introduces a claim of its own (noted as B-claims below).

#### 1. Body-claims ledger

Behavioral claims (A = author text, B = bot summary only, S = scope boundary / non-goal):

| # | Claim (restated) | Bucket | Evidence |
| --- | --- | --- | --- |
| A1 | The cross-shard transition is captured before `updateShardId()` adopts the new shard id | Met | `src/cluster_legacy.c:5428` computes `shard_changed` from `myself->shard_id` vs `n->shard_id`; `updateShardId(myself, n->shard_id)` is at `:5439`, after it |
| A2 | On a cross-shard move the cached master is discarded, so the replica performs a full sync with the new master | Met | `src/cluster_legacy.c:5446` runs after `replicationSetMaster()` (`:5441`), which is where the cache is created (`src/replication.c:3650-3651` for a demoted master; `src/networking.c` freeClient → `replicationCacheMaster` for a replica). With `cached_master == NULL`, `syncWithMaster` sends `PSYNC ? -1` (`src/replication.c:2971-2974`). `connectWithMaster()` only schedules the handshake, so the discard precedes the PSYNC |
| A3 | On a cross-shard move `repl_down_since` is reset to 0 | Met | `src/cluster_legacy.c:5453`, after `replicationSetMaster()` (whose freeClient path sets it to `unixtime` at `src/replication.c:3748`). No later code re-arms it before the first sync completes: the only writers are `src/replication.c:2742` (full sync loaded), `:3720` (unset master), `:3748` (master client freed — impossible while `server.master == NULL`; `server.master` is only created at `:2740` after load and at `:4725`), `:4764` (partial resync), `src/server.c:2517` (init) |
| A4 | Until the first sync with the new master succeeds, the replica reports offset zero | Met | `replicationGetSlaveOffset()` (`src/replication.c:5056-5066`) returns 0 when `server.master == NULL` and `server.cached_master == NULL`; the election log at `src/cluster_legacy.c:4504-4509` prints that value; `ROLE` prints `-1` (`src/replication.c:4608`), which the test checks as `<= 0`. On base the cached offset survived the whole transfer because FULLRESYNC handling (`src/replication.c:3012-3040`) does not discard it — only `replicationAttachToNewMaster` at load (`:2296`) does — so the diff is what makes this true during the transfer window. Holds for rdb-channel replication too: `server.master` is not created during the transfer (`src/replication.c:3980-4000`) |
| A5 | With validity factor 0 the replica stays failover-eligible but ranks behind every eligible replica with an established (non-zero) offset | Met | `src/cluster_legacy.c:4472-4482` skips the data-age gate when the factor is 0; `clusterGetSlaveRank()` (`:4279-4294`) counts siblings with `repl_offset > 0` ahead of an offset-0 node; rank adds 1 s per position (`:4496-4497`). Ties with other offset-0 siblings are not ordered — body says "reducing its chance", not excluding, so consistent |
| A6 | With a non-zero validity factor, the existing data-age check prevents an automatic failover until the first sync succeeds | Met | While `repl_state != REPL_STATE_CONNECTED` (all handshake/TRANSFER states, `src/replication.c:3509`, `:3989`), `data_age = (unixtime - 0) * 1000` (`src/cluster_legacy.c:4460`) exceeds any threshold → `CLUSTER_CANT_FAILOVER_DATA_AGE` (`:4476-4478`). Manual failover bypasses it (`:4476`), matching "automatic". First sync sets CONNECTED and `repl_down_since = 0` together (`src/replication.c:2741-2742`), after which `lastinteraction` is used |
| A7 | The node is treated like a newly configured replica that has never synchronized with its current master | Met | Same initial state as `src/server.c:2517` (`repl_down_since = 0`, "Never connected"), no cached master |
| A8 | The same protection covers a sub-replica flattened after its master moves across shards | Met in the ordinary path; one race not covered → candidate R1 | Flattening calls `clusterSetMaster(grandmaster)` at `src/cluster_legacy.c:2531` and `:3263`. In `clusterProcessPacket` the role/slaveof update (`:3156-3236`) and the safeguard (`:3244-3269`) run before `clusterProcessPingExtensions` (`:3352`); the slaveof branch of `updateShardId` (`:948-950`) does not propagate to the sub-replica, so `myself->shard_id` is still the old shard when `clusterSetMaster` runs and `shard_changed` is true. The exception is when the demoted master's PONG names a grandmaster this node does not yet know — see R1 |
| A9 | Tests cover automatic replica migration, explicit `CLUSTER REPLICATE`, and sub-replica flattening, each with validity factor 0 and non-zero | Met (statically) | `tests/unit/cluster/replica-migration.tcl:37-236` (8 `start_cluster` blocks: sub_replica false/true × factor 0/10 × shutdown/sigstop) and `:238-378` (4 blocks: `CLUSTER REPLICATE` × factor × shutdown/sigstop). "Automatic replica migration" here is the empty-master variant only; the orphaned-master variant (`clusterHandleSlaveMigration`) is explicitly suppressed by `cluster-migration-barrier 999` — see Observation O1 |
| A10 | Motivation: on base, before the first full sync the replica can still participate in failover using the old shard's history | Met (base behavior confirmed) | Base `clusterSetMaster` (`git show unstable:src/cluster_legacy.c`) has no discard/reset; `replicationGetSlaveOffset` returned `cached_master->reploff`; `repl_down_since` was `unixtime` |
| S1 | Non-goal / boundary: only cross-shard re-points are affected; same-shard re-points keep partial resync | Met | Everything is under `if (shard_changed)` (`src/cluster_legacy.c:5445`); same-shard sibling promotion leaves `shard_changed == 0` because the promoted sibling already carries the master's shard id (`:3234`) |
| S2 | Non-goal / boundary: with factor 0, "availability-first" behavior is preserved (replica still eligible) | Met | `src/cluster_legacy.c:4472` |
| B1 | Bot: `CLUSTER SETSLOT` re-point path is also covered | Met | `src/cluster_legacy.c:6419` calls `clusterSetMaster(n)` |
| B2 | Bot: `redis.conf` documents the behavior | Met, but the wording overgeneralizes → candidate R2 | `redis.conf:1795-1800` |
| A11 | "Follows up our comment in #15530" and "tests are based on valkey's" | Cannot tell from the code (not behavioral; sources unavailable offline) | — |

**Counts:** Met 13 (A1–A10, S1, S2, B1; A8 and B2 counted Met with a candidate attached for the partial gap), Not met 0 as a whole claim (two partial gaps raised as candidates R1 and R2), Cannot tell 1 (A11, non-behavioral). No claim was inferred from the diff.

#### 2. Changed-contract list

Three changed contracts were written down before sorting; all three swept.

| Contract | New-wording search | Old-wording search | Live peers and disposition |
| --- | --- | --- | --- |
| C-a: Validity-factor rule text in `redis.conf` — adds a normative statement "not completed its first synchronization … disconnected since forever" | `grep -rni "since forever\|first synchronization\|never synchronized\|never connected" src redis.conf tests` | Old rule fragment: `"cluster-replica-validity-factor"` / `"validity_factor"` / `"repl_down_since"` across `redis.conf src/config.c src/server.c src/cluster*.c` | `src/server.c:2517` (init comment "Never connected, repl is down since EVER") — consistent, governs startup; `src/cluster_legacy.c:4339-4341` (cant-failover message) — unchanged mechanism, consistent; `src/config.c:3399` (config definition) — no rule text, consistent; `src/server.c:6865-6866, 6904-6905` (INFO fields derived from `repl_down_since`) — different mechanism, now report `-1`/0 after a cross-shard move (Observation O2); `redis.conf:616` (unrelated "first synchronization" in RDB section) — different mechanism; `tests/unit/cluster/replica-migration.tcl:124` — new file, consistent. No stale peer carrying an old closed rule. The new sentence itself is broader than the code (R2) |
| C-b: `replicationDiscardCachedMaster()` visibility — moves from a file-local prototype (`src/replication.c:44` on base) to `src/server.h:3589` | `grep -rn replicationDiscardCachedMaster src tests` | Same term (base `git show unstable:src/server.h` has no declaration; base `replication.c:44` has it) | Callers `src/replication.c:2296, 3650, 3688`, `src/cluster_legacy.c:5446`, definition `:4738`, comment `:4650`, test comment `tests/integration/replication.tcl:2040` — all consistent; no other local prototype remains |
| C-c: `clusterSetMaster()` post-condition — a cross-shard re-point now implies no cached master and `repl_down_since == 0` | `grep -n clusterSetMaster src/cluster_legacy.c` | Same term on base | Callers `:2512` (slot-loss migration), `:2531` and `:3263` (sub-replica flattening), `:4693` (orphaned-master migration), `:6311` (`CLUSTER REPLICATE`), `:6419` (`SETSLOT NODE`) — all route through the new guard. Other `replicationSetMaster` call sites in cluster code (`:2344` nodes.conf load, `:5029` cron reconnect) do not change shard and are governed by startup state (`src/server.c:2517`) — different mechanism, consistent |

#### 3. Candidates

##### R1

- `id`: `requirements/sub-replica-flatten-shard-propagated-before-setmaster`
- `anchor`: `src/cluster_legacy.c:5428`
- `fix`: `src/cluster_legacy.c:5428` (same site)
- `title`: Cross-shard guard is skipped if the new shard id was propagated before flattening
- `claim`: The body states "The same risk exists when a sub-replica is flattened after its master moves across shards" and that the change "captures the cross-shard transition". The guard at `src/cluster_legacy.c:5428` compares `myself->shard_id` with `n->shard_id`. `updateShardId()` (`src/cluster_legacy.c:942-947`) rewrites the shard id of every slave of a node that it still records as a master (`node->slaveof == NULL`), including `myself`. When a demoted master's PONG names a new master this node has not yet met, the role block at `src/cluster_legacy.c:3163-3236` leaves `sender->slaveof == NULL` (`master` lookup fails, so the `if (master && sender->slaveof != master)` update at `:3229` is skipped), and `clusterProcessPingExtensions` at `:3352` then calls `updateShardId(sender, <new shard>)` on a node with `slaveof == NULL`, propagating the new shard id onto `myself`. When the grandmaster later becomes known and the safeguard at `:3244-3263` (or `:2531`) calls `clusterSetMaster(grandmaster)`, `myself->shard_id` already equals `grandmaster->shard_id`, so `shard_changed` is 0 and neither `replicationDiscardCachedMaster()` nor `server.repl_down_since = 0` runs. The flattened replica then keeps the old shard's cached offset and a fresh `repl_down_since`, which is exactly the state the body says must not be allowed to win an election.
- `support`: Static trace only; not executed. The precondition (a replica whose master is re-pointed to a node the replica has not learned of yet) is narrow: `redis-cli --cluster rebalance` checks cluster agreement first, so it needs a scripted `CLUSTER MEET` immediately followed by `CLUSTER REPLICATE`/`SETSLOT NODE` on the master. Within that precondition the bypass ordering is the likely one, because discovering the grandmaster triggers a handshake PONG (which carries its shard-id extension) faster than the demoted master's next periodic PONG. I am unsure whether maintainers consider this window in scope; the verifier should re-derive the `updateShardId` branch and the packet-processing order independently.
- `trigger`: Replica R of master M; M is re-pointed to master N in another shard (via `CLUSTER REPLICATE N` or losing its last slot to N) while R does not yet have N in its node table; R receives M's PONG (slaveof=N, shard-id ext = N's shard), then N's PONG, then M's next PONG. R is flattened onto N without the cross-shard reset and, if N fails before R's first sync, R can start an election with M's old offset and a recent `repl_down_since`.
- `change`: Decide the cross-shard condition from replication history rather than from the (possibly already propagated) shard id — e.g. at `src/cluster_legacy.c:5428` also treat the move as cross-shard when `myself->slaveof` was a slave of `n` (flattening) and `myself->slaveof`'s shard id differed from `n`'s at the time of demotion; or record the old shard id before `updateShardId` rewrites it in the propagation branch (`:942-947`) so `clusterSetMaster` can compare against the shard id `myself` synchronized under. Add a test where the grandmaster is `CLUSTER MEET`ed and the master re-pointed in the same tick.
- `priority`: P2
- `action`: consider

##### R2

- `id`: `requirements/conf-first-sync-rule-overgeneralizes`
- `anchor`: `redis.conf:1795`
- `fix`: `redis.conf:1795-1796` (same site)
- `title`: redis.conf states a rule the code applies only to cross-shard moves
- `claim`: `redis.conf:1795-1796` now says "A replica that has not completed its first synchronization with its current master is considered to have been disconnected since forever." The code only produces that state for a cross-shard re-point (`src/cluster_legacy.c:5445-5453`) and for a freshly started process (`src/server.c:2517`). For a same-shard re-point — the ordinary case after a failover, when a replica follows the promoted sibling — `clusterSetMaster` leaves `repl_down_since` at the value set by `replicationHandleMasterDisconnection` (`src/replication.c:3748`, current time), so until its first PSYNC with the new master completes the replica's data age is measured from the disconnection, not "since forever", and with a non-zero validity factor it remains eligible to fail over. The body scopes the behavior to cross-shard moves ("This treats the node like a newly configured replica" for "a replica ... reconfigured to follow a master in another shard"); the conf sentence drops that scope. The following sentence ("This includes a replica that has moved to a different shard") reads as one example of a general rule the code does not implement.
- `support`: Read both branches of `clusterSetMaster` and every `repl_down_since` writer. The existing doc block above it (`redis.conf:1776-1793`) is otherwise accurate about the mechanism. Low stakes; a wording fix.
- `trigger`: An operator reading `redis.conf` concludes that any replica which has not yet synced with its current master cannot fail over under a non-zero validity factor; after a same-shard failover, a replica that has not yet completed PSYNC with the new master can still start an election within the validity window.
- `change`: Reword `redis.conf:1795-1800` to scope the rule to its actual triggers, e.g. "A replica that has never synchronized with its current master — a freshly started replica, or one that has moved to a different shard and has not yet synchronized with its new master — is considered to have been disconnected since forever."
- `priority`: P3
- `action`: consider

#### 4. Questions

- **Q1 (A11):** Whether the change matches what was agreed in the redis/redis#15530 review thread and whether the tests are faithful ports of Valkey #885/#944. No static evidence can settle it: the referenced discussions are not in the repository and the clone is offline. Settled by reading the linked thread and the two Valkey PRs and comparing them with `tests/unit/cluster/replica-migration.tcl` and `src/cluster_legacy.c:5427-5454`.
- **Q2 (A9, runtime):** Whether the 12 new test blocks actually pass and are not flaky under the `cluster-node-timeout 1000` / `CLUSTER_CANT_FAILOVER_RELOG_PERIOD` timing (the "Currently unable to failover" line is suppressed for `node_timeout + 5000` ms after the master's FAIL, `src/cluster_legacy.c:4333-4336`, and the test waits up to 50 s). Reading cannot settle timing; settled by running `./runtest --single unit/cluster/replica-migration` repeatedly (e.g. `--loop` or 20 iterations) on CI.

#### 5. Disposition ledger

| claim | falsification route | decisive evidence | disposition |
| --- | --- | --- | --- |
| `shard_changed` is computed before the shard id is adopted | read order in `clusterSetMaster` | `src/cluster_legacy.c:5428` vs `:5439` | acquitted |
| Discard happens before the cache is created (wrong order) | read `replicationSetMaster` for cache creation | `src/replication.c:3650-3651`, `src/cluster_legacy.c:5441` then `:5446` | acquitted |
| PSYNC could still be sent with the cached master before the discard | check whether `connectWithMaster` runs the handshake synchronously | handshake is an event-loop handler (`src/replication.c:3553`, `syncWithMaster`) | acquitted |
| `repl_down_since` gets re-armed before first sync completes | enumerate all writers | `src/replication.c:2742, 3720, 3748, 4764`, `src/server.c:2517`; `:3748` needs `server.master`, created only at `:2740`/`:4725` | acquitted |
| rdb-channel transfer creates `server.master` early, breaking offset-0 / data-age | grep `server.master =` | only `src/replication.c:2220` via `:2740` after load | acquitted |
| Offset stays non-zero because FULLRESYNC already discards the cache on base (diff redundant) | read FULLRESYNC branch | `src/replication.c:3012-3040` does not discard; only `:2296` at load — diff is load-bearing | acquitted |
| Validity factor 0 still blocks the replica | read data-age gate | `src/cluster_legacy.c:4472` short-circuits on factor 0 | acquitted |
| Rank does not penalize offset 0 | read `clusterGetSlaveRank` | `src/cluster_legacy.c:4290-4293` | acquitted |
| Manual failover is also blocked (body says "automatic") | read gate | `src/cluster_legacy.c:4476 if (!manual_failover)` | acquitted |
| Sub-replica's own shard id is rewritten before flattening in the ordinary path | trace `clusterProcessPacket` order and `updateShardId` branches | role block `:3156-3236` precedes ext `:3352`; slaveof branch `:948-950` does not propagate | acquitted |
| Sub-replica's shard id is rewritten first when the grandmaster is unknown | same trace with `master == NULL` | `:3229` skipped → `sender->slaveof == NULL` → `:942-947` propagates onto `myself`; later `:5428` compares equal | candidate (R1) |
| Same-shard re-point wrongly treated as cross-shard because sibling's shard id is random/unknown | read where a replica's shard id is learned | `src/cluster_legacy.c:3234`, `:2780`, nodes.conf `:562-570` converge replicas onto the master's shard | acquitted |
| A cluster re-point path bypasses `clusterSetMaster` | grep `replicationSetMaster(` callers | `src/cluster_legacy.c:2344, 5029` are startup/reconnect, not shard moves | acquitted |
| `SETSLOT`, `CLUSTER REPLICATE`, orphaned-master migration all covered | grep `clusterSetMaster(` callers | `:2512, :2531, :3263, :4693, :6311, :6419` | acquitted |
| redis.conf sentence overgeneralizes to same-shard re-points | read same-shard branch of `clusterSetMaster` and `:3748` | `repl_down_since = unixtime` retained when `shard_changed == 0` | candidate (R2) |
| Tests cover orphaned-master replica migration | read test overrides | `tests/unit/cluster/replica-migration.tcl:198` `cluster-migration-barrier 999` disables it | observation (O1) |
| `repl_down_since = 0` changes INFO output (unrequested behavior) | grep `repl_down_since` in server.c | `src/server.c:6904-6905` → `master_link_down_since_seconds:-1` | observation (O2) |
| `server.h` export / removal of local prototype is scope creep | check necessity | `src/cluster_legacy.c:5446` needs it; no other prototype | acquitted |
| Second commit ("remove unnecessary check") removed protection from `src` | `git show c54fa4184 -- src` | no `src` hunks in that commit; it touched only the test | acquitted |
| Test file is discovered by the runner | read `tests/test_helper.tcl:39-42` glob | `unit/cluster/*.tcl` globbed | acquitted |
| Test helpers used exist with matching signatures | grep procs | `tests/support/util.tcl:168,217,223,233,823,833`, `cluster_util.tcl:17,172`, `test_helper.tcl:129,160,167,240,254`, `cli.tcl:1` | acquitted |
| Body's Valkey/#15530 lineage claims | offline | not checkable | question (Q1) |
| Test timing/flakiness | runtime | `src/cluster_legacy.c:4333-4336` | question (Q2) |

#### 6. Observations

- **O1** The new tests exercise the empty-master form of replica migration only; the orphaned-master form (`clusterHandleSlaveMigration`, `src/cluster_legacy.c:4693`) shares `clusterSetMaster` but is disabled in every block by `cluster-migration-barrier 999` (`tests/unit/cluster/replica-migration.tcl:198`).
- **O2** After a cross-shard move, `INFO replication` reports `master_link_down_since_seconds:-1` and excludes the gap from `total_disconnect_time` until the first sync, because both derive from `repl_down_since` (`src/server.c:6904-6905`, `:6865-6866`); the body does not mention this side effect.
- **O3** `ROLE` reports `-1` (not 0) for the offset while `server.master == NULL` (`src/replication.c:4608`); the body's "reports offset zero" is literally true for `INFO`/election logging via `replicationGetSlaveOffset()` (`src/replication.c:5056`) and the test accommodates `ROLE` with `<= 0` (`tests/unit/cluster/replica-migration.tcl:94-95`).
- **O4** The second commit (`c54fa4184`, "remove unnecessary check") contains no `src/` hunks; the whole source change is in `8b3c50521`.

#### 7. Manifest

| File | Status | Reason |
| --- | --- | --- |
| `redis.conf` | reviewed | Carries the new normative rule text (contract C-a); compared against the code paths it describes; candidate R2 |
| `src/cluster_legacy.c` | reviewed | Sole behavioral change; every claim A1–A8, S1, S2, B1 traced here, plus all `clusterSetMaster` callers and the packet-processing order; candidate R1 |
| `src/replication.c` | reviewed | Only removes the file-local prototype (contract C-b); read `replicationSetMaster`, cache/discard/resurrect, `replicationGetSlaveOffset`, PSYNC handshake and `readSyncBulkPayload` to verify A2–A4, A6 |
| `src/server.h` | reviewed | Adds the public declaration required by `src/cluster_legacy.c:5446`; not creep |
| `tests/unit/cluster/replica-migration.tcl` | reviewed (statically, not executed) | Verified the 12 blocks match claim A9's matrix, helper procs exist, and the file is globbed by the runner; runtime behavior is Q2 |

Nothing left unfinished within the axis. Not done, by constraint: no build, no test execution, no access to the three linked external discussions.


### Verifier report

#### Candidate 1 — `requirements/sub-replica-flatten-shard-propagated-before-setmaster`

**Verdict: `confirmed`**

Justification: I reconstructed the full path from the code — when the demoted master's new master is unknown to this node, `clusterProcessPingExtensions` writes the new shard id onto `myself` through `updateShardId`'s slave-propagation branch before any `clusterSetMaster` call, so the guard the PR adds compares two already-equal shard ids and skips both resets.

Supporting lines (all head, `/tmp/handoff3/run-v2a-target2/src/cluster_legacy.c`):
- `:5428` — `int shard_changed = memcmp(myself->shard_id, n->shard_id, CLUSTER_NAMELEN) != 0;` (the only input to the reset at `:5442-5454`)
- `:943-948` — `if (node->slaveof == NULL) { assignShardIdToNode(node, ...); for (... clusterNodeNumSlaves(node) ...) ... assignShardIdToNode(slavenode, shard_id, ...)` — rewrites every recorded slave, and `myself` is in the old master's slave list via `clusterNodeAddSlave(n,myself)` at `:5441`.
- `:3226` — `if (master && sender->slaveof != master) {` — the only place a PONG sets `sender->slaveof`; with `master == NULL` (`clusterLookupNode(hdr->slaveof)` at `:3164` fails) the sender is flagged `CLUSTER_NODE_SLAVE` at `:3212-3214` but `slaveof` stays `NULL`.
- `:2782` — `updateShardId(sender, ext_shardid);` — unconditional, reached from `:3352` on every PING/PONG with a known sender, after the role block. With `sender->slaveof == NULL` this takes the propagation branch above.
- The demoted master does advertise the new shard: in its own `clusterSetMaster`, `myself->slaveof = n;` (`:5437`) precedes `updateShardId(myself, n->shard_id);` (`:5438`), so the `else if (memcmp(node->slaveof->shard_id, shard_id, ...) == 0)` branch at `:951` adopts it.
- Later flatten at `:3263` `clusterSetMaster(grandmaster);` (or `:2531`) then sees `shard_changed == 0`; `replicationSetMaster` (`src/replication.c`) never touches `repl_down_since`, so it keeps the value `replicationHandleMasterDisconnection` set at `src/replication.c:3748` (`server.repl_down_since = server.unixtime;`), and the cached master is retained.

Line-number drift in the claim: the "master changed" update is at `:3226-3234`, not `:3229`; `updateShardId`'s propagation branch is `:943-948`, not `:942-947`. Content of every quoted site is accurate, so this is not a misquotation.

Corrected trigger (sharpened, not replaced): the window is not "same tick" — it lasts from the moment M is re-pointed until R completes the handshake with N. A node learned via gossip sits in R's table under a random name with `CLUSTER_NODE_HANDSHAKE` (see `getNodeFromLinkAndMsg` at `:2786-2792`, "the node still has a random name thus not truly known"), so `clusterLookupNode(hdr->slaveof)` fails for N throughout the handshake, not only when N is entirely absent. Concretely: `CLUSTER MEET` N into the cluster, then (before R's handshake with N completes) `CLUSTER REPLICATE N` on M; R receives M's PONG (`slaveof=N`, shard-id extension = N's shard) → R's `myself->shard_id` becomes N's; N's handshake completes and N's PONG marks it master; M's next PONG sets `M->slaveof = N` and the safeguard flattens R onto N with `shard_changed == 0`. If N fails before R's first full sync, R passes the data-age check at `:4460` with a recent `repl_down_since` and offers M's old offset.

The new tests do not reach this path: every scenario is `start_cluster 4 4` with all eight nodes known before the move (`tests/unit/cluster/replica-migration.tcl:213-243`, `:364-378`); there is no `CLUSTER MEET` anywhere in the file.

Priority: **P2** (kept). Action: **consider** (kept). It is a proven gap against the body's own claim ("The same risk exists when a sub-replica is flattened…"), but the merge consequence needs a node-join race plus the new master failing before first sync; the ordinary flatten path (grandmaster already known, whether master or not-yet-promoted) is handled correctly, which I traced: with `master` known the update at `:3234` runs with `sender->slaveof` already set, so `updateShardId` takes the non-propagating branch and `myself->shard_id` is untouched until `clusterSetMaster`.

#### Candidate 2 — `requirements/conf-first-sync-rule-overgeneralizes`

**Verdict: `confirmed`**

Justification: the conf sentence is quoted verbatim and states a general rule, while the code only produces the "since forever" state (`repl_down_since == 0`) on process start and on a cross-shard `clusterSetMaster`; a same-shard re-point measures data age from the last disconnection.

Supporting lines:
- `redis.conf:1795-1796` — `# A replica that has not completed its first synchronization with its current` / `# master is considered to have been disconnected since forever.` — matches the claim exactly.
- Every write of `repl_down_since` in the tree (`grep -n repl_down_since src/`): `src/server.c:2517` (init to 0), `src/cluster_legacy.c:5453` (inside `if (shard_changed)` only), `src/replication.c:2742` and `:4764` (set to 0 on successful full/partial sync), `src/replication.c:3720` (set to 0 when becoming a master), `src/replication.c:3748` — `server.repl_down_since = server.unixtime;` on master disconnection. `replicationSetMaster` (`src/replication.c`) does not assign it. No path zeroes it on a same-shard re-point.
- `src/cluster_legacy.c:4460` — `data_age = (mstime_t)(server.unixtime - server.repl_down_since) * 1000;` — the consumer that the conf paragraph is describing.

Trigger: as stated by the candidate; unchanged. (After a same-shard failover, a replica re-pointed to the promoted sibling that has not completed PSYNC with it has `repl_down_since` equal to the time its old master link dropped, so under a non-zero validity factor it remains eligible within the window — contrary to the conf sentence.)

Priority: **P3** (kept). Action: **consider** (kept) — the canonical behavior the PR implements is correct; this is a doc-scope drift, and the follow-on sentence at `redis.conf:1796-1797` ("This includes a replica that has moved to a different shard…") already names the real trigger, so the fix is a rewording.

#### Merge list

None. Candidate 1 is a guard-input defect in `clusterSetMaster`; Candidate 2 is a documentation-scope defect. Fixing either leaves the other in place.

#### Counts

- confirmed: 2
- plausible: 0
- refuted: 0

#### Observations

- After a cross-shard move, `INFO replication` reports `master_link_down_since_seconds:-1` (the "never connected" sentinel) for a replica that was connected moments earlier, and the `current_disconnect_time` accumulator is forced to 0 for the same reason — `src/server.c:6904-6905` and `src/server.c:6865-6866`.
- When the node being re-pointed cross-shard was itself a master (`was_master`), `replicationSetMaster` first caches a synthetic master from `myself` (`src/replication.c`, `replicationCacheMasterUsingMyself()` in the `if (was_master)` block) and the new `replicationDiscardCachedMaster()` at `src/cluster_legacy.c:5444` immediately drops it, so a demoted master moving shards always full-syncs — `src/cluster_legacy.c:5444`.
- The new test file's flatten scenarios only cover the case where the grandmaster is already a known, established master before the rebalance (`start_cluster 4 4`, rebalance via `redis-cli --cluster rebalance`) — `tests/unit/cluster/replica-migration.tcl:75-99`.
