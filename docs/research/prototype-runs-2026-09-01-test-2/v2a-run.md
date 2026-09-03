# v2a run — `code-review-deep-publish` against `redis/redis#15680` (Sonnet 5)

**2026-09-03.** Data only. Not published to the PR. This run replaces the 2026-09-02 Fable 5.1 run
held in [`../prototype-runs-2026-09-01-test-2-fable/`](../prototype-runs-2026-09-01-test-2-fable/).
See [`addendum-2026-09-03.md`](addendum-2026-09-03.md) for conditions, model verification, and the
dev-set caveat.

## Metadata

| | |
| --- | --- |
| Skill | `code-review-deep-publish` (**v2a**, "Panel line"), pinned `87c68a9` |
| Model | `claude-sonnet-5` on the orchestrator and both finders, passed explicitly and verified from the harness transcripts |
| Agents spawned | 3 (orchestrator + 2 finders). **Verifier skipped by rule** — both finders returned zero candidates |
| Sub-agent tokens | orchestrator 147,212; Code finder 81,653 (42 tool uses); Requirements finder 88,942 (32 tool uses) |
| Candidates raised | **0** — Code 0, Requirements 0 |
| Findings for publication | **0** |
| Questions | 0 |
| Observations | 2 (both from the Requirements finder) |
| Coverage | complete (5/5 files, both finders; static only) |
| Requirements counts | met 11 · not met 0 · cannot tell 0 (body-claims surrogate, no originating issue) |
| Derived status | **Approved (advisory)** |

## The headline: this run found less than the Fable run it replaces

The Fable run on this exact target, packet, and clone produced two verifier-confirmed findings —
including the `updateShardId` propagation defect at `src/cluster_legacy.c:5428` that no prior
prototype or human reviewer had reported. This Sonnet run produced **none**.

The Requirements finder reached the right hypothesis and acquitted it:

> Sub-replica flattening: `shard_changed` false-negative because gossip already updated
> `myself->shard_id` | Read gossip-handling block preceding the flattening check |
> `src/cluster_legacy.c:3221-3234` updates `sender`, not `myself` | **acquitted**

The acquittal is wrong in the same way the target-3 v2a acquittal was wrong: the cited call updates
`sender` directly, but when `sender->slaveof` is `NULL` — which happens whenever the demoted
master's new master is not yet in this node's table — `updateShardId` takes its *propagation*
branch and rewrites the shard id of every node in `sender`'s slave list, `myself` included. The
finder checked the direct update and never examined the propagation branch.

**Because both finders returned zero candidates, the verifier was skipped by rule** (SKILL.md step
3), so this acquittal was checked by nobody. The same structural gap the target-3 round exposed:
verification only sees candidates.

Neither finder raised the `redis.conf` first-sentence scope item in any bucket — not as a
candidate, not as an acquittal, not as an observation. The Fable run's Code finder routed it to
observations and its Requirements finder published it as a P3 finding.

## Process notes

- **The orchestrator treated the session's nudge message as untrusted.** When the session relayed
  that both finders had completed (standing in for the notification a paused parent does not
  receive), the orchestrator independently confirmed the report files existed, read them in full,
  checked their line citations against the diff, verified the quoted ledger row appeared verbatim,
  and re-ran the `redis.conf` grep itself rather than accepting the claim. It recorded all of this
  at the top of its report. Correct behavior, and worth preserving as evidence that relayed
  instructions were not taken as authority.
- **Disclosure on that message:** both finders had already returned before it was sent, so it could
  not have shaped the review's findings — only which disclosures the report makes. It asked for two
  specific statements (the acquittal quoted in full, and whether the `redis.conf` item appeared
  anywhere). Recorded here so the record shows what the session asked for.
- **Prior third-party review state was withheld from both finders**, a judgment call the
  orchestrator made and documented. The Fable run's orchestrator made the same call — verified by
  grepping its saved shared block — so this is not a difference between the two runs.

## Full run report

The orchestrator's complete report, verbatim, including both finders' ledgers:

### 1. Metadata

| Field | Value |
| --- | --- |
| Skill | `code-review-deep-publish` (v2a, "Panel line"), pinned `87c68a9` |
| Architecture | Two parallel finder sub-agents (Code, Requirements) + one fresh-context verifier (conditionally) |
| Target | `redis/redis#15680`, "Prevent data loss after cross-shard replica migration" |
| base / head / merge-base | `065d397030712fe216e795720ae0affd3211212c` / `c54fa4184e7db1ea30c91916f6c0aeb12b5c3f61` / `065d397030712fe216e795720ae0affd3211212c` (base = merge-base) |
| Review kind | Retrospective review of a **merged** PR; posting identity `kamui`, not the author; event would be `COMMENT`; publication unconditionally disabled |
| Agents spawned | 2 (Code finder, Requirements finder). **Verifier was skipped by rule** — both finders returned zero candidates, and SKILL.md step 3 says explicitly: "Finders that return no candidates on a first review make this step unnecessary; skip it." This was a rule-triggered skip, not a discretionary one. |
| Model on every Agent call | `sonnet` (Sonnet 5), passed explicitly on both `Agent` calls |
| Per-sub-agent tokens / tool uses | **Not available to me.** The harness returns each background sub-agent's final report text, not a token/tool-use ledger; I have no introspection into what either finder ran internally beyond what its own report narrates (e.g., specific `grep`/read operations it names as its falsification routes). Stating this explicitly per the dispatch's instruction to say so if the harness doesn't report it. |
| Per-sub-agent wall clock (proxy) | Both finder prompts were finalized and both `Agent` calls launched at **04:44:53 EDT**. The Code finder's report file was written at **04:51:21** (~6.5 min). The Requirements finder's report file was written at **04:52:54** (~8.0 min). These are file-timestamp proxies for completion, not harness-reported wall clock. |
| Total tool uses | Not available (see above). |
| Total run wall clock (mine) | Approximate, not precisely instrumented: reading SKILL.md/references/packet/guidance and assembling the shared block ran before 04:44:53; finder outputs landed by 04:52:54; verdict derivation and this report followed immediately after. Call it roughly 15–20 minutes end to end; I do not have a logged start timestamp precise enough to give a tighter figure, and I say so rather than inventing one. |
| Candidates raised — Code axis | **0** |
| Candidates raised — Requirements axis | **0** |
| Verdicts (confirmed/plausible/refuted/merged) | **None — no verifier ran.** Nothing reached verification because nothing reached candidacy. No candidate was refuted by a verifier; the finders' own pre-candidacy hypotheses were "acquitted" internally (their own disposition-ledger mechanism), which is a different thing from a verifier's `refuted` verdict. |
| Findings for publication | **0** (0 must-fix, 0 consider, 0 questions) |
| Questions | **0** |
| Coverage | **5/5 files**, both finders — `redis.conf`, `src/cluster_legacy.c`, `src/replication.c`, `src/server.h`, `tests/unit/cluster/replica-migration.tcl` — every entry `reviewed` by both finders, none `ignored`, nothing left unfinished by either. Coverage = **complete**. |
| Derived status | **Approved (advisory)** — retrospective review of an already-merged pull request. Axis outcomes: Code = Passed; Requirements = Passed (issue alignment: unavailable). |

---

### 2. Findings that survive verification

**None.** Zero candidates were raised by either finder, so nothing was submitted to a verifier and there
is nothing to report as a surviving finding.

---

### 3. Candidates refuted or dropped

**None reached candidate status**, so none were refuted by a verifier (there was no verifier run) and
none were "dropped" in the sense of a candidate discarded after being raised. What exists instead is each
finder's own pre-candidacy disposition ledger — every hypothesis the finder considered and acquitted
*before* it would have become a candidate. Those ledgers are reproduced in full, verbatim, in section 4
below, per the dispatch's instruction not to summarize them away.

---

### 4. Both finders' complete disposition ledgers (verbatim)

#### Code finder — disposition ledger (11 rows, all acquitted)

| Claim | Falsification route | Decisive evidence | Disposition |
|---|---|---|---|
| `shard_changed` computed after mutation, comparing stale data | Traced statement order in `clusterSetMaster` | `src/cluster_legacy.c:5428` runs before `myself->slaveof=n`/`updateShardId` at :5438-5439 | acquitted |
| `replicationDiscardCachedMaster()` races with an already-issued PSYNC to the new master | Checked whether `connectWithMaster()` sends PSYNC synchronously | `src/replication.c:3538` (`connectWithMaster`) only opens a non-blocking socket; PSYNC is sent later from `syncWithMaster()` callback, after this call stack returns | acquitted |
| Discarding cached master after `replicationSetMaster()` returns is too late / redundant | Checked whether `replicationSetMaster`'s internal discard already covers every path | Internal discard only fires in the `was_master` branch (`src/replication.c:3648-3651`); the pre-existing-replica branch leaves a stale cached master from the old shard's master, so the explicit `clusterSetMaster` discard at `src/cluster_legacy.c:5446` is necessary, not redundant | acquitted |
| `server.repl_down_since = 0` is clobbered by later replication-state code inside the same call | Traced `replicationSetMaster` → `freeClient` → `replicationCacheMaster` → `replicationHandleMasterDisconnection` write order vs. the assignment in `clusterSetMaster` | `replicationHandleMasterDisconnection` (`src/replication.c:3720`, "server.repl_down_since = server.unixtime") runs *inside* `replicationSetMaster`, before `clusterSetMaster`'s own `= 0` assignment at :5453, which executes last | acquitted |
| `repl_down_since = 0` breaks `INFO`'s `master_link_down_since_seconds` field by making it read as "unknown" (-1) while genuinely disconnected | Checked the field's ternary and compared to the pre-existing "never synced" sentinel convention | `src/server.c:6904-6905` treats `repl_down_since == 0` as sentinel "N/A" already, matching the existing meaning used at first-ever connection (`src/server.c:2517`, "Never connected, repl is down since EVER."); the PR deliberately reuses this existing convention | acquitted |
| `data_age` computation in `clusterGetFailoverAuthTime`/failover gate doesn't actually use 0 as a sentinel, so validity-factor gating breaks | Checked `src/cluster_legacy.c:4460` | `data_age = server.unixtime - server.repl_down_since` with no zero-guard, so `repl_down_since=0` yields a large data_age and correctly blocks failover per `cluster-replica-validity-factor` | acquitted (confirms design intent) |
| Removed forward declaration in `replication.c` breaks compilation of earlier call sites (`replicationDiscardCachedMaster` used at lines 2296, 3650, 3688, all before its definition at 4738) | Checked whether `server.h` (which now declares it) is included before those call sites | `src/replication.c:29` includes `server.h` before any use; `src/server.h:3588` now carries the declaration | acquitted |
| Sync drift: `redis.conf` prose addition orphans a peer description of `cluster-replica-validity-factor` elsewhere (docs, `config.c`) | Repo-wide grep for the config name and for a short fragment of "disconnected since forever" | `grep -rln "cluster-replica-validity-factor"` → only `redis.conf`, `tests/unit/cluster/replica-migration.tcl`, `src/config.c`; `src/config.c:3399` has no prose, only a one-line internal comment; the addition is new nuance, not a replacement of existing text | acquitted |
| `updateShardId(myself, n->shard_id)` misclassifies because `node->slaveof` is set before the call | Read `updateShardId` body against call-site ordering | `myself->slaveof = n` happens (`:5438`) before `updateShardId` (`:5439`); the "slaveof != NULL" branch then trivially matches since `node->slaveof->shard_id == shard_id` (same node `n`), which is intended, pre-existing behavior unrelated to this PR's new field | acquitted |
| Test's `wait_for_condition` checks `[lindex [R N role] 4] <= 0` incorrectly relies on an offset that isn't actually cleared | Checked `roleCommand`'s offset field vs. `replicationGetSlaveOffset()` | `src/replication.c:4607` (`ROLE`) reports `server.master ? server.master->reploff : -1`; `-1` (handshake) or `0` (post-full-sync-start) both satisfy `<= 0`, matching intended states | acquitted |
| Removed test assertion in "remove unnecessary check" commit hides a regression | Read the full diff of `c54fa4184` | Only 4 lines removed from the new test file itself (an assertion the same PR had just added one commit earlier); no production code touched | acquitted |

Code finder's own summary: "No candidates met the bar. I traced every hunk (`clusterSetMaster`'s new
`shard_changed` capture and conditional discard/reset block, the `replicationDiscardCachedMaster`
prototype relocation, and the `redis.conf` doc addition) against the full call graph — `replicationSetMaster`,
`replicationCacheMaster`/`replicationCacheMasterUsingMyself`, `replicationDiscardCachedMaster`,
`replicationHandleMasterDisconnection`, `replicationGetSlaveOffset`, `roleCommand`, `clusterGetSlaveRank`,
`clusterHandleSlaveFailover`'s validity-factor gate, and the `INFO replication` output — and every path is
internally consistent with the stated intent."

Code finder observations: **none** ("None that fail the candidate bar but are worth separately noting;
the doc paragraph, code, and test all agree and are internally consistent.")

Code finder's changed-file manifest — all 5 files marked `reviewed`, each with a stated reason (enclosing
function read, call graph traced, cross-file declaration checked, static-only test read); none `ignored`;
"no file was skipped and no check was left unfinished."

#### Requirements finder — disposition ledger (12 rows: 10 acquitted, 2 observations)

| Claim | Falsification route | Decisive evidence | Disposition |
|---|---|---|---|
| `shard_changed` captured after shard ID already updated (stale) | Read line order in `clusterSetMaster` | `src/cluster_legacy.c:5427` vs `:5439` | acquitted |
| `replicationDiscardCachedMaster()` ineffective because `replicationSetMaster`'s own `replicationCacheMasterUsingMyself()` repopulates cached_master after the discard | Trace call order inside `replicationSetMaster` vs `clusterSetMaster` | `src/replication.c:3649-3651` runs before `src/cluster_legacy.c:5447`, not after | acquitted |
| Offset briefly non-zero during PSYNC handshake because `server.master` gets set early | Grep `replicationCreateMasterClient(` call sites | `src/replication.c:2219,2740,4725` — only set at full-sync completion or self-cache synth | acquitted |
| `repl_down_since=0` clobbered by another write path before the failover check runs | Grep all `repl_down_since =` writers | `src/replication.c:2742,3720,3748,4764`, `src/server.c:2517` — none fire in the pending-sync window | acquitted |
| Sub-replica flattening: `shard_changed` false-negative because gossip already updated `myself->shard_id` | Read gossip-handling block preceding the flattening check | `src/cluster_legacy.c:3221-3234` updates `sender`, not `myself` | acquitted |
| Explicit `CLUSTER REPLICATE` doesn't route through `clusterSetMaster`, making C13's claim moot | Grep "replicate" subcommand handler | `src/cluster_legacy.c:6386-6419` calls `clusterSetMaster(n)` | acquitted |
| validity_factor=0 also disables the rank penalty, not just the data-age gate | Read `clusterHandleSlaveFailover`/`clusterGetSlaveRank` | `src/cluster_legacy.c:4279-4294` unconditional; gate at `:4473` is separate | acquitted |
| Non-zero-validity block on the migrated replica never clears (permanent) | Trace `repl_state`/`repl_down_since` transition at sync success | `src/replication.c:2739-2741` resets both together | acquitted |
| `test_nonempty_replica` node isn't actually "non-empty" pre-switch, undermining test-name claim | Read cluster setup + key writes in test source | test source: `R 3 set key_977613 ...` + `wait_for_ofs_sync [Rn 3] [Rn 7]` before `R 7 cluster replicate` | acquitted |
| Fresh/uninitialized `shard_id` causes a harmless false-positive `shard_changed` on first-ever join | Check state of `cached_master`/`repl_down_since` on a brand-new node | both already NULL/0 by default (`src/server.c:2517`) — no-op | acquitted |
| Prototype relocation (`replication.c`→`server.h`) is unrequested new public API / scope creep | Judge against "new public interface" creep criterion | enabling plumbing only, required by the new caller, not a new capability | observation |
| Commit `c54fa4184` removes a log-message assertion (`assert_equal 0 [count_log_message -7 "I'm a sub-replica"]`) for the non-sub-replica variant | Judge against body claims / Requirements axis scope | `tests/unit/cluster/replica-migration.tcl` diff in commit `c54fa4184` | observation |

**This is the row named directly in item 6d/mid-run message, quoted in full and verified verbatim against
the finder's actual output file:**

> `Sub-replica flattening: \`shard_changed\` false-negative because gossip already updated \`myself->shard_id\` | Read gossip-handling block preceding the flattening check | \`src/cluster_legacy.c:3221-3234\` updates \`sender\`, not \`myself\` | acquitted`

Its stated rationale is that the gossip-driven `updateShardId(sender, master->shard_id)` call that precedes
the sub-replica flattening check mutates the *sender* node's shard-id field (the demoted intermediate
master being flattened away), not `myself`'s — so by the time `clusterSetMaster` runs for the sub-replica
itself, `myself->shard_id` still reflects the old shard, and the `memcmp` against the new master's
`shard_id` correctly evaluates true. **No verifier ran on this run, so this acquittal was checked by
nobody but the finder that produced it** — it never went to a fresh-context check because it never crossed
the candidate threshold in the first place, and the verifier step overall was skipped by rule since both
finders returned zero candidates.

#### Requirements finder's restated body-claims ledger (13 rows)

Background/motivation (not independently checkable, restated for completeness, not sorted into a bucket):
- B1. A replica moved cross-shard carries cached replication history from the old shard.
- B2. Pre-fix, such a replica could participate in failover on that invalid history and be promoted with stale/unrelated data.

Checkable behavioral claims (11, all sorted **Met**):
- C3. The same risk exists when a sub-replica is flattened after its master moves shards, and the fix covers that path too.
- C4. The change captures the cross-shard transition **before** `updateShardId()` adopts the new shard ID.
- C5. The change discards the cached master on a cross-shard transition.
- C6. The change resets `repl_down_since` to its initial value of zero on a cross-shard transition.
- C7. This treats the node like a newly configured replica that has never synchronized with its current master.
- C8. Until first sync with the new master succeeds, the replica reports offset zero.
- C9. When `cluster-replica-validity-factor` is zero, the replica remains eligible for failover but is ranked behind every eligible replica with an established offset.
- C10. (validity=0) This preserves availability while reducing the replica's chance of being promoted.
- C11. Resetting `repl_down_since` to zero treats the replica as having never connected to its current master.
- C12. With non-zero `cluster-replica-validity-factor`, the existing data-age check prevents an automatic failover until first sync succeeds.
- C13. Tests cover automatic replica migration, explicit `CLUSTER REPLICATE`, and sub-replica flattening, each with zero and non-zero validity factors.

Non-checkable provenance (not requirements): the "follows up PR #15530 discussion" reference; the Valkey
#885/#944 attribution and "tests are based on Valkey's" claim (about another repository, unverifiable
offline). **No explicit non-goals are stated anywhere in the body**, per the finder's own report.

Counts: **Met: 11** (C3–C13). **Not met: 0.** **Cannot tell / unverifiable: 0.**

Requirements finder observations (2, both bounded to a fact + evidence pointer, no "should"/"must"):
- `src/replication.c` drops the file-local forward declaration of `replicationDiscardCachedMaster` and `src/server.h:3589` adds the public one — pure declaration relocation with no behavior change.
- Commit `c54fa4184` ("remove unnecessary check") deletes a 4-line assertion in the `sigstop`/non-sub-replica test variant that verified log message "I'm a sub-replica" never appeared for node 7; this slightly reduces that variant's rigor but is not itself a body-claims gap.

Requirements finder's changed-file manifest — all 5 files marked `reviewed`; `tests/unit/cluster/replica-migration.tcl` explicitly annotated "reviewed (statically, not executed)"; "no file was left unfinished."

---

### 5. The would-be published review, in full

> **Approved (advisory)** — retrospective review of an already-merged pull request. 0 blocking findings, 0 open questions.
>
> Code: Passed. Requirements: Passed (issue alignment: unavailable).
> Reviewed `c54fa4184` against `unstable` (merge-base `065d3970`). Coverage: complete (5/5 files, both finders).
>
> Two independent finders traced every hunk of this fix — the `shard_changed` capture, the conditional
> `replicationDiscardCachedMaster()`/`repl_down_since` reset, and the redocumentation in `redis.conf` —
> against the full replication and cluster-failover call graph, and neither raised a candidate that survived
> its own gate. There is no originating issue for this pull request; the Requirements axis instead verified
> every behavioral claim in the pull-request body against the code and found all eleven checkable claims
> met, with no stated non-goals to check and no scope creep. This is a clean review: nothing here blocks
> the (already-merged) change.
>
> ## Observations
>
> These are accurate observations, not findings — no action is requested.
> - `src/replication.c` drops the file-local forward declaration of `replicationDiscardCachedMaster`; `src/server.h:3589` adds the public one in its place — a declaration relocation with no behavior change.
> - Commit `c54fa4184` removes a 4-line log-message assertion in the `sigstop`/non-sub-replica test variant that checked `"I'm a sub-replica"` never logged for node 7.
>
> ## Open questions
>
> None.
>
> <!-- review-run workflow=v2a-1 head=c54fa4184e7db1ea30c91916f6c0aeb12b5c3f61 base-ref=unstable base-sha=065d397030712fe216e795720ae0affd3211212c merge-base=065d397030712fe216e795720ae0affd3211212c issues=none coverage=complete -->

No line comments exist to render (zero findings). Publication was not attempted: there is no network
access in this environment and the run conditions unconditionally disable publication for a retrospective
review by a non-author third party.

---

### 6. Specific answers requested by the dispatch

#### (a) The `redis.conf` scope mismatch — did anyone raise, acquit, or observe it?

**It appears nowhere in either finder's output — not as a candidate, not as an acquittal row, not as an
observation.** I confirmed this by grepping both finder report files for "disconnected since forever,"
"first synchronization," "has not completed," "scope mismatch," and "re-point"/"repoint"; the only hit was
the Code finder's *unrelated* sync-drift ledger row (row 8 in its table above), which searched for that
exact phrase for a different purpose — checking whether some *other* file in the repo carries stale prose
about `cluster-replica-validity-factor` — and found none, which is a different question from the one the
dispatch is asking about.

The mismatch itself, stated precisely: the diff's new `redis.conf` paragraph says, as a general rule:

> "A replica that has not completed its first synchronization with its current master is considered to
> have been disconnected since forever."

That sentence is written as an unconditional statement about *any* replica that hasn't yet completed a
first sync with its current master. But the code only resets `server.repl_down_since = 0` inside
`if (shard_changed)` in `clusterSetMaster` (`src/cluster_legacy.c`) — i.e., only on a **cross-shard**
re-point. A same-shard re-point through the same function (e.g., `CLUSTER REPLICATE` to a different master
within the same shard, or certain sub-replica re-pointing that stays within a shard) sets `shard_changed`
to `false` and never touches `repl_down_since`, even though that replica, too, "has not completed its first
synchronization with its current master" by the doc's own wording. Depending on what `repl_down_since` held
before the switch (most likely a recent-past value from being disconnected during the re-point, not zero —
per the Code finder's own citation of `src/server.c:2517`'s "never connected" sentinel semantics), this
plausibly leaves such a replica read as recently-disconnected rather than "disconnected since forever,"
the opposite of what the general first sentence claims for it. Neither finder examined this angle at all —
both finders' many hypotheses about `repl_down_since` (rows checking whether it gets clobbered, whether it
breaks `INFO`, whether the data-age gate uses it correctly) all assumed the cross-shard path as given and
never asked whether the doc's own generality claim holds for the non-cross-shard re-point path the code
does not special-case. I am not asserting this is a confirmed defect — no verifier examined it — only that
it is a real candidate-shaped scope question that this run's two finders did not surface in any form.

#### (b) The Requirements finder's ledger in the no-issue path

The Requirements finder used the **pull-request body's behavioral claims and its explicit non-goals**, per
`requirements-axis.md`'s § No issue rule, exactly as the dispatch instructed. It restated **13 rows**
total: 2 background/motivation statements (B1, B2, explicitly not sorted into a bucket because they are not
independently checkable) plus **11 checkable behavioral claims** (C3–C13). It found **no explicit
non-goals stated anywhere in the body** and said so plainly rather than inventing any.

Counts: **11 met, 0 not met, 0 cannot-tell/unverifiable.** Every checkable claim resolved definitively by
static tracing.

Yes — the finder's own report opens with "**Issue alignment is unavailable.**" and states the reason (no
`Closes #n`/`Fixes #n`/bare `#n` resolves to an available issue) before proceeding under § No issue. My own
would-be-published summary (section 5) carries the skill's required framing as "Requirements: Passed
(issue alignment: unavailable)" beside the axis outcome, per `publishing.md`'s "With no originating issue,
the Requirements axis still classifies normally... and the summary states **issue alignment: unavailable**
beside its outcome."

#### (c) The prior third-party state — ordering claims about `freeClient()` → `replicationCacheMaster()`

**Neither finder saw the prior third-party review state at all.** I made a deliberate judgment call (see
section 8) not to include sundb's `APPROVED` review or shun-lee's LGTM comment in either finder's prompt,
because SKILL.md's shared-block construction rule enumerates a closed list of ingredients (run identity,
manifest, commit list, diff, guidance files, the finding-format path) and separately gates "prior findings
and disposition ledger" content on being a **re-review from the posting identity** — which this is not
(`kamui` has no earlier review on this PR; the packet confirms this explicitly). So the finders could
neither adopt nor ignore the ordering claims as text, because they were never handed that text.

That said, the Code finder **independently re-derived the same ordering fact from source**, while checking
a different hypothesis (whether `server.repl_down_since = 0` gets clobbered by later code in the same call
stack): its ledger row traces "`replicationSetMaster` → `freeClient` → `replicationCacheMaster` →
`replicationHandleMasterDisconnection`" and confirms this chain runs and completes *before*
`clusterSetMaster`'s own `repl_down_since = 0` assignment executes last. This is the same
`freeClient()`→`replicationCacheMaster()` ordering shun-lee's comment asserted ("discarding the cached
master after `replicationSetMaster()` (which is where the old master gets cached via `freeClient()` ->
`replicationCacheMaster()`) ... looks correct"), reached independently from source rather than adopted from
the prior comment, and reaching the same conclusion. I (the orchestrator) am the one who read the prior
review text, as the packet instructed me to weigh it as evidence; I judged it corroborated rather than
contradicted by the finder's independent trace, and did not feed it to either sub-agent as an instruction
or a shortcut.

#### (d) The changed-contract list and sync-drift section, verbatim

**Requirements finder's changed-contract sweep (verbatim):**

> No renamed/extended/narrowed/retired enum, vocabulary, or schema field was found in this diff — it adds
> a new conditional branch inside an existing function, adds documentation prose, and relocates one
> function prototype. Searches run as due diligence:
> - Search term 1 (new/existing wording): `cluster-replica-validity-factor` — repo-wide hits in
>   `redis.conf`, `tests/unit/cluster/replica-migration.tcl`, `src/config.c:3399`,
>   `src/cluster_legacy.c:4340,5451`. All consistent with the new documentation; no stale peer found.
> - Search term 2 (base-branch fragment / related internal symbol): `cluster_slave_validity_factor` — hits
>   in `src/config.c:3399`, `src/cluster_legacy.c:4473,4476`, `src/server.h:2646`. All pre-existing and
>   unaffected by the diff.
> - `replicationDiscardCachedMaster` — hits only in its definition (`src/replication.c:4738`) and its two
>   declarations (removed local one, added `src/server.h:3589`); no orphaned duplicate declaration found.
>
> No live peer carries stale text; the sweep is closed with no gap.

The finder found **no changed contract** in the load-bearing sense the sweep is designed to catch (no
retired closed list, no renamed enum/vocabulary/schema field); it ran the sweep anyway as due diligence on
the closest analog (the `cluster-replica-validity-factor` documentation addition and the relocated
`replicationDiscardCachedMaster` prototype) and reports it closed with no gap.

**Code finder's "Sync drift from a changed rule" section, verbatim (its one ledger row addressing it):**

> Sync drift: `redis.conf` prose addition orphans a peer description of `cluster-replica-validity-factor`
> elsewhere (docs, `config.c`) | Repo-wide grep for the config name and for a short fragment of
> "disconnected since forever" | `grep -rln "cluster-replica-validity-factor"` → only `redis.conf`,
> `tests/unit/cluster/replica-migration.tcl`, `src/config.c`; `src/config.c:3399` has no prose, only a
> one-line internal comment; the addition is new nuance, not a replacement of existing text | acquitted

The Code finder returned no separate dedicated sync-drift subsection beyond this one ledger row; it treated
the sync-drift check as one hypothesis among its eleven and acquitted it on the same repo-wide-grep
evidence basis the brief requires.

---

### 7. Mechanism checklist

- **C2 (No-issue rule):** Yes. The Requirements finder ran against the pull-request body's behavioral
  claims and explicit non-goals (finding none of the latter) per `requirements-axis.md` § No issue,
  restating 13 rows and sorting the 11 checkable ones (11 met / 0 not met / 0 cannot-tell). My
  would-be-published summary (section 5) discloses "Requirements: Passed (issue alignment: unavailable)"
  beside the axis outcome, matching `publishing.md`'s required phrasing. Demonstrated in section 6(b) above.

- **C3 (Disposition ledger):** Yes. Both finders returned structured, compact-row disposition tables
  including every acquitted (tried-to-convict-and-failed) hypothesis: 11 rows from the Code finder (all
  acquitted), 12 rows from the Requirements finder (10 acquitted, 2 routed to observation). Both ledgers
  are reproduced verbatim in section 4.

- **C5 (Observations):** The Code finder's Observations section is empty (explicitly: "None that fail the
  candidate bar but are worth separately noting"). The Requirements finder's Observations section carries
  2 items: the `replication.c`→`server.h` prototype relocation, and the removed log-message assertion in
  commit `c54fa4184`. No verifier ran, so there are no verifier observations. **The `redis.conf` scope item
  did not land in Observations** — confirmed by direct grep of both finder files (section 6(a)); it does
  not appear in either finder's output in any section.

- **Pole intact:** Both finders ran (Code and Requirements, in parallel, both on `model: sonnet`). Every
  candidate got a verifier verdict, **or the verifier was skipped because both finders returned zero
  candidates** — this run is the latter case, explicitly: 0 candidates from Code, 0 from Requirements, so
  per SKILL.md step 3's own exception clause the verifier step was not spawned. `support` withholding is
  moot for this run since no verifier prompt was ever constructed (there was nothing to withhold `support`
  from); had a verifier run, I would have withheld every `support` field per the skill's mandatory rule, as
  planned before either finder's result was known.

- **C1 (calibration) and C4 (question-routing):** Not applicable here, as the dispatch anticipated. With
  zero candidates from either axis, there was no priority/action recalibration for a verifier to perform
  (C1 needs a confirmed candidate to recalibrate), and no `plausible` verdict existed to route to a question
  (C4 needs a verifier-plausible candidate, and no verifier ran at all). Noting this plainly rather than
  forcing either mechanism to appear.

---

### 8. Notes on the run — judgment calls, guidance treatment, timing

1. **`CONTRIBUTING.md` guidance-membership call.** SKILL.md names `CONTRIBUTING.md` explicitly, by type, in
   its list of guidance files ("Guidance includes `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`,
   `CODING_STANDARDS.md`, and scoped equivalents"). This repository's `CONTRIBUTING.md` is, on inspection,
   a CLA plus generic contribution-process text (how to fork/branch/PR, issue-tracker etiquette, licensing)
   with no code style, naming, testing, or implementation-standard content whatsoever. I resolved the
   ambiguity by the literal, name-based reading rather than a content-based filter: I included it in the
   shared block as delivered guidance material (with base-branch provenance recorded, per SKILL.md), but
   told both finders plainly that it contains no rule a standards citation could point to, so neither would
   manufacture a citation to satisfy the "guidance must be considered" requirement. This is the judgment
   call the packet flagged as "one of the mechanisms this run exists to observe," and neither finder in
   fact cited it for anything — consistent with its content.

2. **Withholding the prior third-party review state from the finders.** I did not include sundb's
   `APPROVED` review or shun-lee's LGTM comment in either finder's shared block. SKILL.md's shared-block
   construction enumerates a closed set of ingredients, and its provision for carrying prior material
   forward ("append the prior findings and disposition ledger for that axis") is scoped to a re-review *of
   the posting identity's own earlier review* — `kamui` has none here, per the packet. Feeding third-party
   review prose into the finder prompt as if it were standing material risked functioning as an anchor
   ("a prior reviewer already checked this ordering") rather than as evidence a finder independently weighs.
   I instead read it myself, as the orchestrator, per the packet's explicit instruction to weigh it as
   evidence — see section 6(c) for how that played out.

3. **The Cursor Bugbot auto-generated summary block appended to the PR body.** I judged this to be
   third-party commentary about the diff, not part of the author's stated behavioral claims/non-goals, and
   told the Requirements finder explicitly to treat it that way rather than fold it into the body-claims
   ledger. This is a judgment call about what "the pull-request body" means for the § No issue substitute:
   I read it as the author-authored prose only.

4. **No diff-size fallback needed.** The full diff was ~20 KB (459 lines), comfortably inside normal prompt
   limits, so I did not invoke SKILL.md's "if the full diff exceeds the harness's practical prompt limit"
   command-based fallback for either finder. Both received the full diff text inline in the shared block.

5. **Verifier skip.** Not really a judgment call — SKILL.md states this exception outright — but I want it
   on record as a deliberate, rule-following decision rather than an omission: both finders returned zero
   candidates, so per SKILL.md step 3 the verifier step "is unnecessary" and I skipped it, and I am saying
   so explicitly here as the dispatch required.

6. **Total wall clock for my own run.** I do not have a precisely logged start timestamp for this run
   (reading the dispatch file, SKILL.md, and all five reference files preceded any timestamped artifact).
   Using the earliest artifact I can point to (the finder prompt files, finalized and both `Agent` calls
   launched at 04:44:53 EDT) through the last finder output landing (04:52:54 EDT) as a lower bound, plus
   the reading/assembly work before that and the verdict-derivation/report-writing work after it, my best
   honest estimate is **roughly 15–20 minutes** end to end. I am flagging this as an estimate rather than a
   measurement.

7. **Mid-run message handling.** Documented in full at the top of this report: I treated the in-session
   message claiming to relay both finders' results as unverified until I confirmed it myself against the
   actual files, their timestamps, and their content's technical consistency with the diff I had already
   read directly. Nothing in this report rests on that message's claims alone.

