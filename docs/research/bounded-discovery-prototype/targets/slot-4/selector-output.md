I have no `Write` (or any file-writing) tool available in this session — only `Read`, `Grep`, `Glob`, `ListAgents`, `ReportFindings`, `ScheduleWakeup`, `Skill`, `ToolSearch`, and `Workflow` are present, and I confirmed via `ToolSearch` that no deferred `Write`/`Edit`/file-creation tool exists either. I cannot place files under `output/`. Per instructions ("you have only file-reading tools... Do not try to work around that"), I'm not attempting a workaround (e.g. shell) — I'm delivering the two required outputs verbatim below instead, so the orchestrator can persist them.

## `output/selection.json`

```json
{
  "selected": {
    "kind": "S1",
    "roots": [
      {
        "path": "server/stream.go",
        "symbol": "setupMirrorConsumer",
        "start": 3146,
        "end": 3305
      }
    ],
    "rationale": "Both hunks in the diff sit inside stream.(*stream).setupMirrorConsumer and rework how the spawned goroutine reaches the mirror's sync.WaitGroup before calling Wait() on it: hunk 1 (head/server/stream.go:3146) captures mirrorWg := &mirror.wg as a local pointer at the top of the locked function, and hunk 2 (head/server/stream.go:3305) changes the unlocked background goroutine to call mirrorWg.Wait() instead of mirror.wg.Wait(). The PR body's own race trace (WARNING: DATA RACE on mirror.wg.Wait() at server/stream.go:3372/3304 in the pre-fix source) confirms the hunk is squarely about a WaitGroup used for goroutine-completion synchronization guarded by mset.mu ('Lock should be held.' at head/server/stream.go:3113), so it is unambiguously S1 (concurrency/progress: a WaitGroup wait/notify pair guarding a background task's lifecycle). No other supported surface of any kind exists in this diff (it touches one file, one function, no tests, no doc/contract elsewhere in the diff), so S1 is trivially first under the priority rule and there is no tie to break by path/symbol/line.",
    "citations": [
      "diff.patch:9",
      "diff.patch:18",
      "head/server/stream.go:3146",
      "head/server/stream.go:3305",
      "head/server/stream.go:3113-3114",
      "head/server/stream.go:3372-3373"
    ],
    "frontier": [
      {
        "from": "setupMirrorConsumer",
        "kind": "callee",
        "citation": "head/server/stream.go:3375-3376",
        "to": {"path": "server/stream.go", "symbol": "processMirrorMsgs", "start": 2778, "end": 2844}
      },
      {
        "from": "setupMirrorConsumer",
        "kind": "callee",
        "citation": "head/server/stream.go:3375-3382",
        "to": {"path": "server/server.go", "symbol": "startGoRoutine", "start": 3980, "end": 3980}
      },
      {
        "from": "setupMirrorConsumer",
        "kind": "caller",
        "citation": "head/server/stream.go:3033",
        "to": {"path": "server/stream.go", "symbol": "retryMirrorConsumer", "start": 3028, "end": 3034}
      },
      {
        "from": "setupMirrorConsumer",
        "kind": "caller",
        "citation": "head/server/stream.go:3104",
        "to": {"path": "server/stream.go", "symbol": "scheduleSetupMirrorConsumerRetry", "start": 3088, "end": 3107}
      },
      {
        "from": "setupMirrorConsumer",
        "kind": "contract",
        "citation": "head/server/stream.go:529",
        "to": {"path": "server/stream.go", "symbol": "sourceInfo.wg", "start": 513, "end": 533}
      },
      {
        "from": "processMirrorMsgs",
        "kind": "callee",
        "citation": "head/server/stream.go:2781",
        "to": {"path": "server/stream.go", "symbol": "sourceInfo.wg", "start": 513, "end": 533}
      },
      {
        "from": "processMirrorMsgs",
        "kind": "callee",
        "citation": "head/server/stream.go:2840",
        "to": {"path": "server/stream.go", "symbol": "retryMirrorConsumer", "start": 3028, "end": 3034}
      },
      {
        "from": "scheduleSetupMirrorConsumerRetry",
        "kind": "caller",
        "citation": "head/server/stream.go:2759",
        "to": {"path": "server/stream.go", "symbol": "retryDisconnectedSyncConsumers", "start": 2737, "end": 2767}
      },
      {
        "from": "retryMirrorConsumer",
        "kind": "callee",
        "citation": "head/server/stream.go:3021",
        "to": {"path": "server/stream.go", "symbol": "cancelMirrorConsumer", "start": 3017, "end": 3022}
      }
    ],
    "exclusions": [
      "head/server/stream.go:513-533 — sourceInfo struct (incl. the wg field) is a contract source cited in the frontier but is itself untouched by the diff, so it is not a selectable root.",
      "head/server/stream.go:3459-3520 — trySetupSourceConsumer/setupSourceConsumer (the non-mirror source path) is a structurally similar function but has no analogous si.wg.Wait()/Add() throttle and is not touched by the diff; excluded as outside the diff even though it is a plausible sibling for an S2 read.",
      "head/server/stream.go:2846-2957 — processInboundMirrorMsg is reachable from processMirrorMsgs (hop 2 from root) but is not touched by the diff and adds no new edge relevant to the wg fix; left out of the frontier to stay within two hops of substance."
    ],
    "unavailable_edges": [
      "Looked for a sibling implementation of the same wg-capture pattern in the regular (non-mirror) source-consumer path by grepping 'si.wg' and '.wg.(Wait|Add|Done)' across server/stream.go; only mirror.wg.Done() (head/server/stream.go:2781) and mirror.wg.Add(1) (head/server/stream.go:3373) exist, so no S2 sibling-consistency obligation could be established for this hunk.",
      "Looked for an originating issue or spec statement beyond the PR body; packet.md section 4 records 'issues=none', so no S2 contract source outside the diff/comments was available."
    ]
  },
  "alternatives": [
    {
      "kind": "S1",
      "path": "server/stream.go",
      "symbol": "setupMirrorConsumer",
      "start": 3146,
      "end": 3305,
      "why_this_kind": "Only supported surface in the diff: both hunks change how the unlocked background goroutine reaches the mirror's sync.WaitGroup, per the WaitGroup-usage race trace in the PR body.",
      "citations": ["diff.patch:9", "diff.patch:18", "head/server/stream.go:3146", "head/server/stream.go:3305"],
      "rank_under_rule": 1
    }
  ],
  "no_supported_surface": false,
  "notes": "The diff is a single 3-line change in one function, so there was no real competition to rank: no S2 obligation source (no issue, no doc, no sibling implementation using the same wg-throttle pattern) and no S3 changed test exist anywhere in diff.patch, leaving exactly one supported surface. I treated the two hunks (the mirrorWg declaration and its later use) as one S1 surface rather than two, since a supported surface can be 'a symbol the diff adds or modifies' and both hunks modify the same function/closure around the same WaitGroup pointer; splitting them into two roots would not have changed the selection (both are S1, same path/symbol, and the rule only needs one region to select) but would have overstated their independence. I could not verify from the diff alone why capturing &mirror.wg into a local pointer removes the race reported in the PR body (the field's memory address does not change by taking its address into a variable); that causal question is for the discovery/review worker, not for scope selection, and I did not speculate about it further. Separately: this session had no Write/Edit tool available (confirmed via ToolSearch), so this JSON could not be persisted to output/selection.json — it is delivered inline in the final response instead."
}
```

## `output/report.md`

```markdown
# Scope-selector report — nats-io/nats-server#7395

## Files read, in order
1. `packet.md` — full read.
2. `diff.patch` — full read (22 lines; 1 file, 2 hunks).
3. `head/server/stream.go:3120-3419` — context around both hunks; located `setupMirrorConsumer` body, the spawned goroutine, `processMirrorMsgs`/`retrySourceConsumerAtSeq`/`cancelSourceInfo` neighbors.
4. `head/server/stream.go:505-549` — `sourceInfo` struct definition (the `wg sync.WaitGroup` field).
5. `head/server/stream.go:3090-3124` — top of `setupMirrorConsumer`, the `scheduleSetupMirrorConsumerRetry` tail, and the "Lock should be held." contract comment.
6. `base/server/stream.go:3260-3399` — pre-fix version of the goroutine, to identify the exact `mirror.wg.Add(1)` (line 3372) and `mirror.wg.Wait()` (line 3304) call sites named in the PR body's race trace.
7. `base/server/stream.go:3110-3149` — pre-fix top of `setupMirrorConsumer`, confirming no `mirrorWg` variable existed pre-fix.
8. `head/server/stream.go:3000-3039` — `setMirrorErr`, `cancelMirrorConsumer`, `retryMirrorConsumer` (callers of `setupMirrorConsumer`).
9. `head/server/stream.go:2775-2790` — `processMirrorMsgs` signature and its deferred `mirror.wg.Done()`.
10. `head/server/stream.go:3085-3091` — `scheduleSetupMirrorConsumerRetry` doc comment/signature.
11. `head/server/stream.go:2700-2957` — `mirrorInfo`, `retryDisconnectedSyncConsumers` (caller of `scheduleSetupMirrorConsumerRetry`), full body of `processMirrorMsgs`, and `processInboundMirrorMsg`.
12. `head/server/stream.go:3085-3091` (re-read narrower) — exact `scheduleSetupMirrorConsumerRetry` line range.

## Searches run
- `Grep "type sourceInfo struct"` in `head/server` → `stream.go:513`.
- `Grep "setupMirrorConsumer\(\)"` in `head/server` → 3 hits (2 call sites + definition), all in `stream.go`.
- `Grep "retryMirrorConsumer\(\)|func \(mset \*stream\) processMirrorMsgs|\.wg\.(Done|Add|Wait)"` in `head/server/stream.go` → located `processMirrorMsgs` def, its `wg.Done()`, 4 `retryMirrorConsumer()` call sites, `retryMirrorConsumer` def, `wg.Add(1)` site.
- `Grep "func \(mset \*stream\) setupSourceConsumer|si\.wg|siWg"` in `head/server/stream.go` → only `setupSourceConsumer`/`setupSourceConsumers` defs; no `si.wg`/`siWg` usage anywhere (checked whether the non-mirror source path shares the same WaitGroup-throttle pattern — it does not).
- `Grep "func \(mset \*stream\) trySetupSourceConsumer"` in `head/server/stream.go` → single def at line 3503.
- `Grep "\.wg\.(Wait|Add|Done)"` in `head/server/stream.go` → confirmed only 2 non-declaration usages exist in the whole file (`Done` at 2781, `Add` at 3373); `Wait` only appears via the diff's own `mirrorWg.Wait()`, which this grep pattern (anchored to `.wg.`) does not match after the rename, confirming the rename fully replaced the old call site.
- `Grep "scheduleSetupMirrorConsumerRetry\(\)"` in `head/server/stream.go` → 6 hits: definition + 5 call sites (2759, 3151, 3253, 3294, 4289).
- `Grep "func \(s \*Server\) startGoRoutine"` in `head/server` → `server.go:3980`.

## Surfaces considered and how the rule ordered them
Only one supported surface exists in the diff:

- **S1** — `server/stream.go`, function `setupMirrorConsumer`, spanning the two hunks (`head/server/stream.go:3146` declaring `mirrorWg := &mirror.wg`, and `head/server/stream.go:3305` changing the wait call to `mirrorWg.Wait()`). Qualifies as S1 because it is a `sync.WaitGroup` wait/notify pair guarding completion of the previous `processMirrorMsgs` goroutine before starting a new one, under a "Lock should be held" contract, and the PR's own attached race-detector trace names exactly this WaitGroup access as the race. Ranked 1st and selected — trivially, since it is the only supported surface of any kind.

No S2 candidate was found: `issues=none` per packet.md §4, no doc comment states an obligation this hunk must discharge beyond its own local comment, no interface/trait is involved, and the one plausible sibling (`trySetupSourceConsumer`/`setupSourceConsumer` for regular, non-mirror sources) does not share the `wg`-based throttle pattern at all (confirmed by grep — zero `si.wg`/`siWg` hits), so there is no consistency obligation to cite.

No S3 candidate exists: the changed-file manifest is `server/stream.go` only (packet.md §2); no test file appears in `diff.patch`.

## Not read, and why
- `packet.md` §7's listed guidance files (`CONTRIBUTING.md`, `.github/CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md`) were not opened. They are not referenced by anything in `diff.patch` and the mechanical selection rule only needs supported surfaces *inside the diff*; none of these files establish an obligation the changed hunk must discharge (no interface/schema/doc-comment link), so reading them would not have changed the selection.
- Nothing outside `/tmp/bd148/selector/nats-server-7395` was read or needed; `head/server/server.go:3980` (`startGoRoutine`, used only as a frontier citation) is inside the permitted `head/` tree.
- No `git`/history commands were run of any kind (no shell tool is available in this session regardless); I did not read anything beyond the pinned head, and no attempt was made to reach network or origin.

## Tooling note
This session has no `Write`/`Edit`/file-creation tool (verified via `ToolSearch`), so `output/selection.json` and `output/report.md` could not be written to disk under the packet's `output/` directory. Both are delivered verbatim in the final chat response instead.
```