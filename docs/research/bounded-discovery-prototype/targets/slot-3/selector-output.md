I do not have a file-write tool in this session (Write/Edit were not present, and `ToolSearch` found none) — only `Read`, `Grep`, `Glob`, and unrelated tools (cron, monitor, worktree, design-sync, messaging). I cannot literally create `output/selection.json` or `output/report.md`. Per the harness rules I won't try to work around that with another mechanism. I'm reproducing both outputs verbatim below so the content is available even though it isn't persisted to `output/`.

## output/selection.json

```json
{
  "selected": {
    "kind": "S1",
    "roots": [
      {"path": "server/raft_chain_of_blocks_helpers_test.go", "symbol": "RCOBStateMachine.applyEntry", "start": 116, "end": 140}
    ],
    "rationale": "This hunk changes lock discipline around sm.Lock()/sm.Unlock(): instead of holding the state-machine lock for the whole function (defer sm.Unlock()), it now copies sm.n, unlocks, and only then calls n.Applied(ce.Index) — and n.Applied acquires the raft node's own lock (head/server/raft.go:1065). That is exactly the nested-lock/deadlock hazard the PR body names (rg.lockAll() locks all raft nodes while another goroutine may be holding a state machine's lock and needs the raft lock), so the hunk is S1 (lock discipline / deadlock avoidance) by definition. Under the mechanical rule, S1 outranks S2 and S3, and among the six S1 hunks in this diff (propose/applyEntry/createSnapshot in both raft_chain_of_blocks_helpers_test.go and raft_helpers_test.go), path 'server/raft_chain_of_blocks_helpers_test.go' sorts lexically before 'server/raft_helpers_test.go', and within that file symbol name 'applyEntry' sorts before 'createSnapshot' and 'propose', making it first.",
    "citations": [
      "diff.patch:22-34",
      "diff.patch:35-44",
      "head/server/raft_chain_of_blocks_helpers_test.go:116-140",
      "head/server/raft.go:1064-1066"
    ],
    "frontier": [
      {"from": "RCOBStateMachine.applyEntry", "kind": "caller", "citation": "head/server/raft_helpers_test.go:177", "to": {"path": "server/raft_helpers_test.go", "symbol": "smLoop", "start": 160, "end": 185}},
      {"from": "RCOBStateMachine.applyEntry", "kind": "contract", "citation": "head/server/raft_helpers_test.go:35", "to": {"path": "server/raft_helpers_test.go", "symbol": "stateMachine", "start": 28, "end": 42}},
      {"from": "RCOBStateMachine.applyEntry", "kind": "callee", "citation": "head/server/raft_chain_of_blocks_helpers_test.go:128", "to": {"path": "server/raft_chain_of_blocks_helpers_test.go", "symbol": "RCOBStateMachine.applyBlock", "start": 236, "end": 259}},
      {"from": "RCOBStateMachine.applyEntry", "kind": "callee", "citation": "head/server/raft_chain_of_blocks_helpers_test.go:130", "to": {"path": "server/raft_chain_of_blocks_helpers_test.go", "symbol": "RCOBStateMachine.loadSnapshot", "start": 335, "end": 362}},
      {"from": "RCOBStateMachine.applyEntry", "kind": "callee", "citation": "head/server/raft_chain_of_blocks_helpers_test.go:139", "to": {"path": "server/raft.go", "symbol": "(*raft).Applied", "start": 1064, "end": 1100}},
      {"from": "RCOBStateMachine.applyEntry", "kind": "callee", "citation": "head/server/raft_chain_of_blocks_helpers_test.go:120", "to": {"path": "server/raft_chain_of_blocks_helpers_test.go", "symbol": "RCOBStateMachine.logDebug", "start": 84, "end": 88}},
      {"from": "smLoop", "kind": "caller", "citation": "head/server/raft_helpers_test.go:153", "to": {"path": "server/raft_helpers_test.go", "symbol": "cluster.createRaftGroupWithPeers", "start": 121, "end": 155}},
      {"from": "stateMachine", "kind": "contract", "citation": "head/server/raft_helpers_test.go:224", "to": {"path": "server/raft_helpers_test.go", "symbol": "stateAdder.applyEntry", "start": 224, "end": 244}},
      {"from": "(*raft).Applied", "kind": "caller", "citation": "head/server/jetstream_cluster.go:1276", "to": {"path": "server/jetstream_cluster.go", "symbol": "jetStream.monitorCluster", "start": 1141, "end": 1331}}
    ],
    "exclusions": [
      "head/server/raft_chain_of_blocks_helpers_test.go:102-114 — RCOBStateMachine.propose, same-kind (S1) surface, ranked after applyEntry: 'applyEntry' < 'propose' alphabetically within the same file",
      "head/server/raft_chain_of_blocks_helpers_test.go:281-333 — RCOBStateMachine.createSnapshot, same-kind (S1) surface, ranked after applyEntry: 'applyEntry' < 'createSnapshot' alphabetically within the same file",
      "head/server/raft_helpers_test.go:218-222 — stateAdder.propose, S1 surface, ranked after because 'server/raft_chain_of_blocks_helpers_test.go' < 'server/raft_helpers_test.go' lexically",
      "head/server/raft_helpers_test.go:224-244 — stateAdder.applyEntry, S1 surface and sibling implementer of the same stateMachine.applyEntry contract; ranked after by path, referenced only as a hop-2 contract edge, not itself in scope",
      "head/server/raft_helpers_test.go:314-325 — stateAdder.snapshot, S1 surface, ranked after by path",
      "head/server/raft_test.go:812-891 — TestNRGTermDoesntRollBackToPtermOnCatchup, S3 (changed test) surface, lower priority than any S1 surface present in this diff"
    ],
    "unavailable_edges": [
      "Looked for a direct call/callee/contract edge from RCOBStateMachine.applyEntry to smGroup.lockAll (head/server/raft_helpers_test.go:88-92) — the routine the PR body names as the deadlock's other side (it Locks every raft node while a state machine's own lock may be held elsewhere). Grepped 'lockAll()' across head/server: it is invoked only from test bodies (e.g. head/server/raft_test.go:830,847,861), never from applyEntry or any of its callees/callers found here. No such edge exists, so it stays outside the two-hop frontier even though it explains why the lock reordering in the root hunk matters."
    ]
  },
  "alternatives": [
    {"kind": "S1", "path": "server/raft_chain_of_blocks_helpers_test.go", "symbol": "RCOBStateMachine.applyEntry", "start": 116, "end": 140, "why_this_kind": "Removes defer sm.Unlock(); copies sm.n and unlocks before calling n.Applied(ce.Index), which itself locks the raft node (head/server/raft.go:1065) — deadlock-avoidance lock reordering.", "citations": ["diff.patch:22-44", "head/server/raft_chain_of_blocks_helpers_test.go:116-140"], "rank_under_rule": 1},
    {"kind": "S1", "path": "server/raft_chain_of_blocks_helpers_test.go", "symbol": "RCOBStateMachine.createSnapshot", "start": 281, "end": 333, "why_this_kind": "Unlocks sm before calling n.InstallSnapshot and re-locks after — same lock-reordering pattern to avoid holding sm's lock across a call into the raft node.", "citations": ["diff.patch:47-59", "head/server/raft_chain_of_blocks_helpers_test.go:320-325"], "rank_under_rule": 2},
    {"kind": "S1", "path": "server/raft_chain_of_blocks_helpers_test.go", "symbol": "RCOBStateMachine.propose", "start": 102, "end": 114, "why_this_kind": "Removes defer sm.Unlock(); copies sm.n, unlocks, then calls n.ForwardProposal(data) — same lock-reordering pattern.", "citations": ["diff.patch:5-21", "head/server/raft_chain_of_blocks_helpers_test.go:102-114"], "rank_under_rule": 3},
    {"kind": "S1", "path": "server/raft_helpers_test.go", "symbol": "stateAdder.applyEntry", "start": 224, "end": 244, "why_this_kind": "Removes defer a.Unlock(); copies a.n, unlocks, then calls n.Applied(ce.Index) — identical pattern to the selected root, implementing the same stateMachine.applyEntry contract.", "citations": ["diff.patch:76-93", "head/server/raft_helpers_test.go:224-244"], "rank_under_rule": 4},
    {"kind": "S1", "path": "server/raft_helpers_test.go", "symbol": "stateAdder.propose", "start": 218, "end": 222, "why_this_kind": "Drops the a.Lock()/defer a.Unlock() entirely around a.n.ForwardProposal, using a.node() (which itself locks/unlocks internally) instead — lock-scope reduction.", "citations": ["diff.patch:67-74", "head/server/raft_helpers_test.go:218-222"], "rank_under_rule": 5},
    {"kind": "S1", "path": "server/raft_helpers_test.go", "symbol": "stateAdder.snapshot", "start": 314, "end": 325, "why_this_kind": "Copies a.sum/a.n under lock, unlocks, then calls rn.InstallSnapshot outside the lock — same lock-reordering pattern.", "citations": ["diff.patch:100-113", "head/server/raft_helpers_test.go:314-325"], "rank_under_rule": 6},
    {"kind": "S3", "path": "server/raft_test.go", "symbol": "TestNRGTermDoesntRollBackToPtermOnCatchup", "start": 812, "end": 891, "why_this_kind": "The hunk adds two lines (nc.Flush() + time.Sleep(100ms)) inside this existing test function, i.e. it modifies a test; it is the PR's stated de-flake mechanism (ensuring interest propagation before publishing the append-entry) but does not itself add/touch a lock, atomic, channel, goroutine, or other S1 construct.", "citations": ["diff.patch:121-129", "head/server/raft_test.go:868-871"], "rank_under_rule": 7}
  ],
  "no_supported_surface": false,
  "notes": "The tie-break (path, then symbol name, then start line) selects RCOBStateMachine.applyEntry over RCOBStateMachine.createSnapshot and RCOBStateMachine.propose in the same file purely because 'applyEntry' < 'createSnapshot' < 'propose' alphabetically; all three hunks in that file carry equal S1 severity and fix the same deadlock pattern (unlock sm before calling into the RaftNode), so this ordering is arbitrary with respect to actual risk — the other two are recorded as immediate alternatives (ranks 2-3), and the near-identical stateAdder trio in raft_helpers_test.go follow at ranks 4-6. The raft_test.go hunk (nc.Flush()+time.Sleep, S3) is thematically a synchronization fix (waiting for interest propagation) but uses no explicit lock/atomic/channel/goroutine/timeout/retry/cancellation construct, so it was kept as S3 rather than reclassified S1; even if reclassified it would not outrank the raft_chain_of_blocks_helpers_test.go hunks under path ordering, so the selection is unaffected either way. No S2-only surface (an obligation stated purely outside the diff, without any S1 construct in the same hunk) was found; the stateMachine interface's doc comment at raft_helpers_test.go:32 ('This will call forward as needed so can be called on any node') arguably makes the two propose hunks dually S2, but S1 already covers them so this does not change ranking. I read no history beyond the pinned head 282d01c54 and ran no git commands of any kind — only Read/Grep against the packet/diff/head trees provided. I did not read base/ (not needed: all citations are diff+head as required) or the repo-guidance files (CONTRIBUTING.md, .github/CODEOWNERS, .github/PULL_REQUEST_TEMPLATE.md) since packet.md §7 already records their presence and they carry no obligation bearing on which hunk is S1/S2/S3. This session had no file-write tool (Write/Edit not found via ToolSearch), so output/selection.json and output/report.md could not be physically written to disk; both are reproduced verbatim in my response instead, and I flagged this rather than trying to route around it."
}
```

## output/report.md

```markdown
# Selector report — nats-server-6593

## Files read, in order
1. `packet.md` — full (pinned identity, manifest, PR body, commits, prior review, repo-guidance table, run conditions)
2. `diff.patch` — full (offset 1-133), then re-read in two slices (offset 1-60, offset 60-124) to pin exact diff.patch line numbers per hunk
3. `head/server/raft_chain_of_blocks_helpers_test.go` — offset 95-169 (propose/applyEntry/leaderChange/stop), offset 295-339 (createSnapshot tail/loadSnapshot head), offset 84-93 (logDebug), offset 236-259 (applyBlock), offset 335-362 (loadSnapshot)
4. `head/server/raft_helpers_test.go` — offset 210-339 (waitGroup/propose/applyEntry/leaderChange/proposeDelta/stop/restart/total/snapshot/waitOnTotal), offset 1-60 (imports, stateMachine interface, smGroup, smLoop start), offset 120-154 (createRaftGroupWithPeers), offset 150-194 (smLoop body, stateAdder struct head)
5. `head/server/raft_test.go` — offset 850-889 (TestNRGTermDoesntRollBackToPtermOnCatchup tail incl. the added Flush/Sleep), offset 888-902 (function end / next test start)
6. `head/server/raft.go` — offset 20-74 (RaftNode interface incl. Applied), offset 1064-1108 ((*raft).Applied body)
7. `head/server/jetstream_cluster.go` — offset 1265-1284 (monitorCluster's n.Applied call site)

Not read: `base/` tree (not needed — task requires diff+head citations only, and base content wasn't relevant to classifying hunks or building the frontier); `CONTRIBUTING.md`, `.github/CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md` (packet.md §7 already records their presence/absence; none states an obligation the diff must discharge, so they don't produce an S2 surface and weren't needed). Nothing outside `/tmp/bd148/selector/nats-server-6593` was read. No git commands were run and no history beyond the pinned head `282d01c54` was consulted — the packet's §8 "Run conditions" git commands were ignored per instructions in favor of the provided `head/`/`base/`/`diff.patch` trees.

## Searches run
- `Grep` `func \(sm \*RCOBStateMachine\) applyBlock|func \(sm \*RCOBStateMachine\) loadSnapshot` in `head/server/raft_chain_of_blocks_helpers_test.go`
- `Grep` `func \(sm \*RCOBStateMachine\) createSnapshot` in `head/server/raft_chain_of_blocks_helpers_test.go`
- `Grep` `Applied\(index uint64\)|Applied\(uint64\)` in `head/server`
- `Grep` `\.Applied\(` in `head/server`
- `Grep` `applyEntry` in `head/server`
- `Grep` `func \(rg smGroup\) lockAll|func.*lockAll` in `head/server`
- `Grep` `lockAll\(\)` in `head/server/raft_test.go`
- `Grep` `func \(sm \*RCOBStateMachine\) logDebug` in `head/server/raft_chain_of_blocks_helpers_test.go`
- `Grep` `^func \(js \*jetStream\)|^func.*monitorCluster` in `head/server/jetstream_cluster.go`

## Surfaces considered and how the rule ordered them

The diff (3 files, +34/-13, 1 commit) contains exactly two kinds of supported surface: **S1** (six lock-discipline hunks, all removing `defer sm.Unlock()`/`defer a.Unlock()` in favor of unlocking before calling into the `RaftNode`, to avoid a nested-lock deadlock with `smGroup.lockAll()` as described in the PR body) and **S3** (one changed-test hunk). No S2-only surface was found — no hunk discharges an obligation stated *purely* outside the diff without also being an S1 lock hunk itself.

S1 candidates, in rule order (path, then symbol name, then start line):
| Rank | Path | Symbol | Start |
|---|---|---|---|
| 1 (selected) | server/raft_chain_of_blocks_helpers_test.go | RCOBStateMachine.applyEntry | 116 |
| 2 | server/raft_chain_of_blocks_helpers_test.go | RCOBStateMachine.createSnapshot | 281 |
| 3 | server/raft_chain_of_blocks_helpers_test.go | RCOBStateMachine.propose | 102 |
| 4 | server/raft_helpers_test.go | stateAdder.applyEntry | 224 |
| 5 | server/raft_helpers_test.go | stateAdder.propose | 218 |
| 6 | server/raft_helpers_test.go | stateAdder.snapshot | 314 |

S3 candidate (lower priority than any S1 surface, listed for completeness):
| Rank | Path | Symbol | Start |
|---|---|---|---|
| 7 | server/raft_test.go | TestNRGTermDoesntRollBackToPtermOnCatchup | 812 |

`server/raft_chain_of_blocks_helpers_test.go` sorts before `server/raft_helpers_test.go` sorts before `server/raft_test.go` (case-sensitive lexical, `c` < `h` < `t` at the first differing character). Within the winning file, symbol names sort `applyEntry < createSnapshot < propose`, putting `RCOBStateMachine.applyEntry` first. Selected: **S1, `server/raft_chain_of_blocks_helpers_test.go`, `RCOBStateMachine.applyEntry`, head lines 116-140**.

## Frontier built for the selected root
- Hop 1 caller: `smLoop` (head/server/raft_helpers_test.go:160-185), calls `sm.applyEntry(ce)` at line 177.
- Hop 1 contract: `stateMachine` interface (head/server/raft_helpers_test.go:28-42), declares `applyEntry(ce *CommittedEntry)` at line 35.
- Hop 1 callees: `RCOBStateMachine.applyBlock` (raft_chain_of_blocks_helpers_test.go:236-259, called at line 128), `RCOBStateMachine.loadSnapshot` (raft_chain_of_blocks_helpers_test.go:335-362, called at line 130), `(*raft).Applied` (raft.go:1064-1100, called at line 139 — itself takes `n.Lock()` at raft.go:1065, which is the concrete deadlock hazard), `RCOBStateMachine.logDebug` (raft_chain_of_blocks_helpers_test.go:84-88, called at line 120 and elsewhere in the function).
- Hop 2 (from `smLoop`): caller `cluster.createRaftGroupWithPeers` (raft_helpers_test.go:121-155), spawns `go smLoop(sm)` at line 153.
- Hop 2 (from `stateMachine` contract): sibling implementer `stateAdder.applyEntry` (raft_helpers_test.go:224-244), must satisfy the same interface method and carries the identical lock-reordering fix.
- Hop 2 (from `(*raft).Applied`): production caller `jetStream.monitorCluster` (jetstream_cluster.go:1141-1331), calls `n.Applied(ce.Index)` at line 1276 — the real (non-test) analog of the pattern the root implements.
- Unavailable: no call/callee/contract edge exists from `RCOBStateMachine.applyEntry` (or any hop-1/hop-2 symbol found) to `smGroup.lockAll` (raft_helpers_test.go:88-92), the routine named in the PR body as the other side of the deadlock; it is invoked only from test bodies (raft_test.go:830, 847, 861), never from the applyEntry call chain, so it falls outside the two-hop frontier by definition even though it motivates the fix.

## Anything not established / not read
- Did not read `base/` — not required for diff+head citations.
- Did not read `CONTRIBUTING.md`, `.github/CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md` — packet.md §7 already records them and none states an obligation relevant to hunk classification.
- No history beyond pinned head `282d01c54` was read; no git commands were run.
- This session had no file-write tool available (`Write`/`Edit` absent from the tool list and from `ToolSearch` results for "Write", "Edit", "FileWrite", "CreateFile", and a broad "create or overwrite a file on disk" query), so `output/selection.json` and `output/report.md` were not physically written — both are given verbatim in the assistant's final response instead.
```

**Flag for the orchestrator:** this run had no tool capable of writing to `output/`, so nothing was persisted at `/tmp/bd148/selector/nats-server-6593/output/`. The two files' intended contents are given in full above.