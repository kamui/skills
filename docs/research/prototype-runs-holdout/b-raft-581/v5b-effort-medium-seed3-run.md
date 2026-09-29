# Run document — holdout target (b), cell `v5b-effort-medium-seed3`

**Orchestrator metadata (added after the run; the researcher's record, not the reviewer's).**

| | |
| --- | --- |
| Packet | `packets/b/packet.md`, SHA-256 `d94db099dc8ea929b8f09a14b945e7b70b0efa31a08ac576a64681a06742253e` |
| Snapshot pins | v5b=2f06662 noverify=2f06662-minus-verifier panel=dd3bcfe33bfe8b65e272a6d2266ee9bc6cd1dc72 |
| Root agent / primary | `a69f1c909185a5678` / `a69f1c909185a5678` |
| Payload | [`v5b-effort-medium-seed3-payload.md`](v5b-effort-medium-seed3-payload.md), 1651 bytes |
| Report (this file, below the preamble) | 38606 bytes as written by the reviewer |
| Closed out | 2026-09-04T18:56:15.818724+00:00 |
| Problems at close-out | none |

## Model and effort verification (every assistant line of every transcript)

| Agent | Role | Definition | `message.model` | `effort` | Transcript |
| --- | --- | --- | --- | --- | --- |
| `a69f1c909185a5678` | primary | v5b-primary-effort-medium | `claude-sonnet-5`×63 | `medium`×63 | `agent-a69f1c909185a5678.jsonl` |
| `a4023da2f4c91a65d` | child | v5b-verifier-effort-high | `claude-sonnet-5`×35 | `high`×35 | `agent-a4023da2f4c91a65d.jsonl` |

## Billed usage (`transcript_usage.py --prices 2,10 --report <this report>`)

```
agent-a69f1c909185a5678.jsonl
turns                        32 (API requests; 63 assistant lines)
tool calls                   32
text-only turns               1
input                        64 tokens (uncached)
cache write             115,127 tokens
cache read            2,268,761 tokens
output                   49,434 tokens (thinking 18,456)
models             claude-sonnet-5
wall                    0:13:02
cost                       1.24 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-a4023da2f4c91a65d.jsonl
turns                        18 (API requests; 35 assistant lines)
tool calls                   17
text-only turns               1
input                        36 tokens (uncached)
cache write              42,429 tokens
cache read              521,479 tokens
output                    9,173 tokens (thinking 4,722)
models             claude-sonnet-5
wall                    0:02:52
cost                       0.30 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

TOTAL
turns                        50 (API requests; 98 assistant lines)
tool calls                   49
text-only turns               2
input                       100 tokens (uncached)
cache write             157,556 tokens
cache read            2,790,240 tokens
output                   58,607 tokens (thinking 23,178)
models             claude-sonnet-5
wall                    0:15:54 (summed over transcripts)
cost                       1.54 $ at 2/10 per M, cache write ×1.25, cache read ×0.1
production-shaped          1.44 $ (output 48,955 after subtracting the report's 9,652 est. tokens)
```

Row for `comparison-data.md`:

| (b) v5b-effort-medium seed 3 | claude-sonnet-5 | 50 | 49 | 2 | 100 | 157,556 | 2,790,240 | 58,607 | 23,178 | 0:15:54 | 1.54 | 9,652 | **1.44** |

Per agent:

| primary a69f1c909185a5678 | claude-sonnet-5 | 32 | 32 | 1 | 64 | 115,127 | 2,268,761 | 49,434 | 18,456 | 0:13:02 | 1.24 | — | — |
| child a4023da2f4c91a65d | claude-sonnet-5 | 18 | 17 | 1 | 36 | 42,429 | 521,479 | 9,173 | 4,722 | 0:02:52 | 0.30 | — | — |

---

# Research report — `hashicorp/raft#581`, arm `v5b-effort-medium`, seed 3

Payload file: `/tmp/holdout/reports/b/v5b-effort-medium-seed3-payload.md`

## 1. Metadata

- Target: `hashicorp/raft#581` — "Fix rare leadership transfer failures when writes happen during transfer"
- Arm: `v5b-effort-medium`; skill `legacy reviewer` pinned at `main 2f06662 (workflow=v5b-1)`
- Seed: 3
- Primary reviewer model: `claude-sonnet-5`, run at effort `medium` (one step below harness default), dispatched through the `v5b-primary-effort-medium` agent definition, doing the entire review in this single context (no delegation of the review itself).
- Sub-agents spawned: **one** verifier batch, role = clean-verdict verifier (zero-survivor mode), dispatched via `subagent_type: "v5b-verifier-effort-high"`, `model: "sonnet"`, run in the foreground, effort inherited at `high` per that definition's pin. See §4 for the full prompt and verbatim report.
- Verification trigger that fired: **zero-survivor mode**. Zero candidates survived as findings (the sole surviving fact was routed to `Observations`, which the skill's zero-survivor rule explicitly does not count as a survivor), and the changed behavior is squarely a concurrency/failover path (`raft.go` `leaderLoop`'s leadership-transfer handling). Related-acquittal mode did not apply (no survivor to anchor it to). Mandatory-verification-by-kind (must-fix / security / data-loss / destructive-migration / compat-break) did not fire because no candidate reached `must-fix` or those kinds.
- Candidates raised: 7 (6 falsified/dropped in the primary context, 1 routed to Observations). Candidates surviving primary falsification as findings: 0.
- Verifier verdict: `clean verdict stands` for all 6 ledger rows attacked (see §4).
- Findings for publication: **none**.
- Questions: **none** — no outcome-changing fact was statically unresolvable.
- Observations: **one**, published (see payload; cap of 3 not exceeded).
- Coverage: complete — all 3 changed files reviewed, all reachable risk checks (concurrency/failover path around leadership transfer) evidence-backed.
- Derived status: **Approved (advisory)** — retrospective, non-publishing, `Mode` line included per contract.
- Token usage: the harness does not report token usage to me in this context; I have no figure to give.

## 2. Findings that survive

None. Zero findings were admitted; the only accurate sub-threshold fact is published as an Observation (not a finding) in the payload.

## 3. Complete private disposition ledger

All candidates were raised and falsified in the single primary-review pass (step 3), against the full function-context diff from `review_context.py` (see §5) plus targeted reads confirming gating call sites.

| id | kind | claim (one line) | disposition | decisive evidence | falsification reason |
| --- | --- | --- | --- | --- | --- |
| `raft/leadertransfer-wait-scope` | concurrency | The new post-TimeoutNow wait (raft.go:696-709) might not actually block writes/other leader-only ops for its full duration, reopening the original race. | dropped (acquitted) | raft.go:78 (`defer r.setLeadershipTransferInProgress(false)` at goroutine top, fires only when the goroutine — including the new nested select — returns), raft.go:826,836,846,859 (`applyCh`, `userRestoreCh`, `configurationsCh`, `configurationChangeChIfStable` all gate on `r.getLeadershipTransferInProgress()`) | The atomic flag set at raft.go:135 (`r.setLeadershipTransferInProgress(true)`) is only cleared by the deferred call, which cannot run until the enclosing goroutine — including the added nested `select` — returns; every write/leader-only path already checks the same flag before this change, unmodified by the diff, so the wait window is provably closed for the whole extended duration. |
| `raft/leadertransfer-concurrent-start` | concurrency | A second `LeadershipTransfer` request could start (new `leftLeaderLoop`/`stopCh`/goroutine) while the first transfer's added wait is still running, corrupting shared state. | dropped (acquitted) | raft.go:643-648 (`if r.getLeadershipTransferInProgress() { ...future.respond(ErrLeadershipTransferInProgress); continue }`, unchanged by this diff) | The same atomic in-progress flag gates entry into the whole `case future := <-r.leadershipTransferCh` block; since the flag stays true through the added wait (see prior row), a second request is rejected with `ErrLeadershipTransferInProgress` before it can construct a new `leftLeaderLoop`/`stopCh`/goroutine, so no concurrent transfer state can exist. |
| `raft/leadertransfer-double-respond` | concurrency | The nested `select` added at raft.go:700-708 could pick two branches (or race with the outer select) and call `future.respond` twice, e.g. panicking on the future's internal completion channel. | dropped (acquitted) | raft.go:692-710 (single `select` statement with exactly two cases, evaluated once) | A Go `select` executes exactly one ready case per evaluation; the outer select's `case err := <-doneCh:` and the new nested select execute at most once each per goroutine lifetime, and the nested select's two cases (`time.After` / `leftLeaderLoop`) are mutually exclusive within that one evaluation, so `future.respond` is reachable from exactly one of the three total call sites in this goroutine per invocation. |
| `raft/leadertransfer-timeout-hang` | concurrency | If `leftLeaderLoop` never closes (e.g. the node never actually steps down) the new wait could block forever, leaking the goroutine and never releasing the leadership-transfer-in-progress flag. | dropped (acquitted) | raft.go:701-704 (`case <-time.After(r.config().ElectionTimeout): ...future.respond(err)`) | The nested select's other case is a bounded `time.After(r.config().ElectionTimeout)`, so the goroutine is guaranteed to unblock, respond, and return (releasing the flag via the deferred call) within one `ElectionTimeout` even if `leftLeaderLoop` never closes. |
| `raft/getinstate-restale-race` | bug | The `GetInState` rewrite (testing.go:445,494-496) might still read a stale `inState` snapshot at the moment the timer fires, reproducing the exact bug the commit message describes fixing. | dropped (acquitted) | testing.go:445 (`_, highestTerm := c.pollState(s)` at loop top, `inState` no longer captured there), testing.go:494 (`inState, highestTerm := c.pollState(s)` freshly polled inside the `case t, ok := <-timer.C:` branch, immediately before `return inState`) | The rewrite removes the only site that captured a possibly-stale `inState` and instead polls fresh, synchronously, at the exact moment the stability timer fires and the function is about to return it — the value returned can no longer be older than the timer-fire instant, which is what the commit message's race concerned. |
| `raft/leadertransferwithwrites-followers-index` | bug | The new test's `follower := c.Followers()[0]` (raft_test.go, new `TestRaft_LeadershipTransferWithWrites`) could panic on an empty slice if the 7-node cluster hasn't converged when the test starts. | dropped (acquitted) | testing.go:502-509 (`func (c *cluster) Followers() []*Raft { ... if len(followers) != expFollowers { c.t.Fatalf(...) } ...}`) | `Followers()` (unchanged helper) calls `t.Fatalf` and halts the test before returning if the follower count doesn't match `len(c.rafts)-1`, so indexing `[0]` can only execute once that invariant holds; this is the same pattern already used unmodified by the adjacent `TestRaft_LeadershipTransferWithSevenNodes` test. |
| `raft/leadertransfer-timeout-message-ambiguity` | maintainability | raft.go:702 (`fmt.Errorf("leadership transfer timeout")`) duplicates the exact wording already used by the pre-existing outer-select timeout branch (raft.go:80-84), so a reader correlating debug logs cannot tell whether the RPC itself timed out or whether the RPC succeeded and only the post-TimeoutNow settle period elapsed. | **routed to Observations** (fails gate 1/4: no proven functional consequence, purely a debug-log clarity fact) | raft.go:80-84, raft.go:701-704 | Both branches log and return the byte-identical error string `"leadership transfer timeout"` for two distinct causes (RPC-level timeout vs. post-success settle timeout); this is an accurate, decisive fact but has no demonstrated functional or correctness consequence — only a debugging-clarity one — so it fails finding gate 1 (meaningful impact) / gate 4 (proven consequence) rather than being a defect; published as the run's one Observation instead of a finding. |

No duplicates were found among these six non-survivors plus the one observation; each concerns a distinct mechanism.

## 4. Sub-agent dispatch — verifier (zero-survivor clean-verdict batch)

Trigger: zero survivors as findings, concurrency/failover-path change (`raft.go` leadership-transfer handling in `leaderLoop`). Per `SKILL.md` step 3 / `references/verifier.md`, this required exactly one clean-verdict batch carrying the complete candidate disposition ledger (all 7 rows, including the one routed to Observations, since zero-survivor mode is never filtered by risk surface).

**Dispatch:** `Agent` tool, `subagent_type: "v5b-verifier-effort-high"`, `model: "sonnet"`, `run_in_background: false` (foreground, awaited).

### Exact prompt given

```
You are the independent verifier for one holdout-evaluation review cell. Follow
`/tmp/holdout/skills/v5b/references/verifier.md` exactly, in its "Clean-verdict task"
mode, zero-survivor variant. Do not act as a second reviewer: do not search for new
findings, do not write anything, do not run `go build`/`go test`/`go vet`/any linter,
and make no network call of any kind (the clone's origin is a local path). This is
retrospective review of a merged, closed pull request; nothing you do is published.

Rules that bind you (same as the primary reviewer's dispatch, rules 1-6 plus this
rule 8):
1. Follow the verifier reference exactly; do not borrow behavior from any other
   review skill.
2. This is a retrospective review; you are not publishing anything.
3. N/A here (you do not compute the context digest).
4. Clone hygiene: do not run `git checkout`, `git switch`, `git reset`, `git stash`,
   or any tree-mutating command. If you mutate the tree by accident, stop and report
   it; do not attempt to fix it yourself.
5. N/A here (you are not writing the report file).
6. Stay inside this sandbox only: the clone at
   `/tmp/holdout/runs/b/v5b-effort-medium-seed3` (read-only; `main` is pinned to the
   merge-base `1462fd5e80ad0eb38748f68198505025cb2c96d8`, `review-head` is checked
   out at head `cb622973cd2c65dd2752c49d0520f2a3894b2d91`), and the skill reference
   file named above. Do not read any other run's clone, report, or payload. Report
   any other path you read.
8. You get no further sub-agents; do this yourself in your own fresh context.

Repository: hashicorp/raft. Base ref: main. Base SHA / merge-base:
1462fd5e80ad0eb38748f68198505025cb2c96d8 (identical). Head:
cb622973cd2c65dd2752c49d0520f2a3894b2d91. No linked issue (issues=none). No
repository-scoped AGENTS.md/CLAUDE.md/CONTEXT.md exist at the merge-base for the
changed paths (raft.go, raft_test.go, testing.go) — there is no applicable base-branch
rule coordinate.

Use `git -C /tmp/holdout/runs/b/v5b-effort-medium-seed3 diff main review-head` for
the change and `git -C /tmp/holdout/runs/b/v5b-effort-medium-seed3 show
main:<path>` for base versions, exactly as the reference instructs; do not fetch
network, do not run go tooling.

This is a **zero-survivor clean-verdict batch**: the complete candidate disposition
ledger below is provided; every row is a non-survivor (dropped or routed to
Observations) from the primary reviewer's pass. Attack each acquittal at the depth
`references/verifier.md` sets for its `kind` (full 5-step procedure for `bug` and
`concurrency` rows; the one-citation check for `maintainability`). You are given only
the compact ledger form (claim, kind, disposition, decisive evidence, falsification
reason) — no primary `support` narrative. Return exactly one batch conclusion:
`clean verdict stands`, or one `disposition <id> does not hold; re-open it` line per
row whose acquittal you find contradicted or unsupported, citing the failed
disposition step and decisive evidence. You may also return at most one
non-actionable `observation` aside if an incidental fact surfaces that contradicts no
supplied row.

## Ledger (7 rows)

1. id: raft/leadertransfer-wait-scope | kind: concurrency
   claim: The new post-TimeoutNow wait (raft.go:696-709) might not actually block
   writes/other leader-only ops for its full duration, reopening the original race.
   disposition: dropped (acquitted)
   evidence: raft.go:78 (defer r.setLeadershipTransferInProgress(false) at goroutine
   top); raft.go:826,836,846,859 (applyCh/userRestoreCh/configurationsCh/
   configurationChangeChIfStable all gate on r.getLeadershipTransferInProgress())
   falsification: The flag set at raft.go:135 is only cleared by the deferred call,
   which cannot run until the goroutine (including the new nested select) returns;
   every write/leader-only path already checks the same flag, unmodified by the diff.

2. id: raft/leadertransfer-concurrent-start | kind: concurrency
   claim: A second LeadershipTransfer request could start (new leftLeaderLoop/
   stopCh/goroutine) while the first transfer's added wait is still running,
   corrupting shared state.
   disposition: dropped (acquitted)
   evidence: raft.go:643-648 (if r.getLeadershipTransferInProgress() {...
   future.respond(ErrLeadershipTransferInProgress); continue}, unchanged by this diff)
   falsification: The same in-progress flag gates entry into the whole
   leadershipTransferCh case; since the flag stays true through the added wait, a
   second request is rejected before it can construct new transfer state.

3. id: raft/leadertransfer-double-respond | kind: concurrency
   claim: The nested select added at raft.go:700-708 could pick two branches (or
   race with the outer select) and call future.respond twice.
   disposition: dropped (acquitted)
   evidence: raft.go:692-710 (single select statement, exactly two cases, evaluated
   once)
   falsification: A Go select executes exactly one ready case per evaluation; the
   outer select's doneCh case and the new nested select each execute at most once
   per goroutine lifetime, and the nested select's two cases are mutually exclusive
   within that one evaluation.

4. id: raft/leadertransfer-timeout-hang | kind: concurrency
   claim: If leftLeaderLoop never closes, the new wait could block forever, leaking
   the goroutine and never releasing the leadership-transfer-in-progress flag.
   disposition: dropped (acquitted)
   evidence: raft.go:701-704 (case <-time.After(r.config().ElectionTimeout): ...
   future.respond(err))
   falsification: The nested select's other case is a bounded
   time.After(r.config().ElectionTimeout), guaranteeing the goroutine unblocks,
   responds, and returns (releasing the flag) within one ElectionTimeout even if
   leftLeaderLoop never closes.

5. id: raft/getinstate-restale-race | kind: bug
   claim: The GetInState rewrite (testing.go:445,494-496) might still read a stale
   inState snapshot at the moment the timer fires, reproducing the bug the commit
   message describes fixing.
   disposition: dropped (acquitted)
   evidence: testing.go:445 (_, highestTerm := c.pollState(s) at loop top, inState no
   longer captured there); testing.go:494 (inState, highestTerm := c.pollState(s)
   freshly polled inside the timer-fired case, immediately before return inState)
   falsification: The rewrite removes the only site that captured a possibly-stale
   inState and instead polls fresh, synchronously, at the exact moment the stability
   timer fires and the function is about to return it.

6. id: raft/leadertransferwithwrites-followers-index | kind: bug
   claim: The new test's follower := c.Followers()[0] (new
   TestRaft_LeadershipTransferWithWrites) could panic on an empty slice if the
   7-node cluster hasn't converged when the test starts.
   disposition: dropped (acquitted)
   evidence: testing.go:502-509 (func (c *cluster) Followers() []*Raft { ... if
   len(followers) != expFollowers { c.t.Fatalf(...) } ...})
   falsification: Followers() (unchanged helper) calls t.Fatalf and halts the test
   before returning if the follower count doesn't match len(c.rafts)-1, so indexing
   [0] can only execute once that invariant holds.

7. id: raft/leadertransfer-timeout-message-ambiguity | kind: maintainability
   claim: raft.go:702's fmt.Errorf("leadership transfer timeout") duplicates the
   exact wording already used by the pre-existing outer-select timeout branch
   (raft.go:80-84), so a reader correlating debug logs cannot tell whether the RPC
   itself timed out or whether it succeeded and only the post-success settle period
   elapsed.
   disposition: routed to Observations (fails gate 1/4: no proven functional
   consequence, purely a debug-log clarity fact)
   evidence: raft.go:80-84; raft.go:701-704
   falsification: n/a (not acquitted as a dropped bug candidate; routed on
   consequence, not falsified as false) — apply the maintainability one-citation
   check: confirm or contradict that both branches log the identical string.

Read the two ranges yourself before ruling: `git -C
/tmp/holdout/runs/b/v5b-effort-medium-seed3 show
cb622973cd2c65dd2752c49d0520f2a3894b2d91:raft.go | sed -n '600,720p'` and `git -C
/tmp/holdout/runs/b/v5b-effort-medium-seed3 show
cb622973cd2c65dd2752c49d0520f2a3894b2d91:testing.go | sed -n '400,500p'` (and the
merge-base versions with `1462fd5e80ad0eb38748f68198505025cb2c96d8` in place of the
head SHA) to get exact current line numbers before citing anything, since line
numbers above are from the primary reviewer's independent count and could be off by
a line or two.
```

### Verbatim report returned

*(pasted exactly as returned by the sub-agent; dispatched with `subagent_type: "v5b-verifier-effort-high"`, `model: "sonnet"`, `run_in_background: false`, and awaited before this report was finalized)*

> ## Verifier report — cell v5b-effort-medium-seed3 (7-row zero-survivor ledger)
>
> All evidence read directly from `/tmp/holdout/runs/b/v5b-effort-medium-seed3` via `git show`/`git diff` against `main` (1462fd5e) and `review-head` (cb622973). No other run's clone, report, or payload was touched. No `go` tooling, no network, no tree mutation.
>
> **Row 1 — raft/leadertransfer-wait-scope (concurrency, full 5-step): HOLDS**
> Premise: the leadership-transfer-in-progress flag is cleared exactly once, only by `defer r.setLeadershipTransferInProgress(false)` at raft.go:678, and that defer belongs to the goroutine literal that also contains the new nested wait (raft.go:700-708), so it cannot run until that wait resolves. Opposite-branch check: is there any other writer of the flag to false, or any path that skips the defer? `grep` for `setLeadershipTransferInProgress` across raft.go found exactly one `true`-setter (raft.go:734, before the goroutine launch) and exactly one `false`-setter (raft.go:678, the defer). No panic-recovery path bypasses a defer in Go, so the defer always fires when the goroutine returns, and the goroutine cannot return before the nested select at 700-708 completes. Verified every gated path is unchanged and still checks the same flag: raft.go:826-828 (applyCh), 836-838 (userRestoreCh), 846-848 (configurationsCh), 859-861 (configurationChangeChIfStable). Acquittal confirmed; falsification argument is airtight.
>
> **Row 2 — raft/leadertransfer-concurrent-start (concurrency, full 5-step): HOLDS**
> Premise: raft.go:645-648 (`if r.getLeadershipTransferInProgress() { ...continue }`) gates entry to the whole `leadershipTransferCh` case, unmodified by the diff (confirmed via `git diff main review-head -- raft.go`, which touches only lines 692-711). Opposite-branch check: could the flag flip to false between the check and the new wait completing? No — per Row 1, the flag is provably still true throughout the new wait (same defer/goroutine argument). A second transfer request during that window hits the same guard and is rejected via `future.respond(ErrLeadershipTransferInProgress)` at 647. Acquittal confirmed.
>
> **Row 3 — raft/leadertransfer-double-respond (concurrency, full 5-step): HOLDS**
> Read raft.go:660-712 directly. The nested select is exactly two cases (700-708: `time.After` at 701, `leftLeaderLoop` at 705), reached only from the `err == nil` branch of the outer select's `doneCh` case (692-696/709), itself one of exactly three mutually exclusive outer cases (680 time.After, 686 leftLeaderLoop, 692 doneCh). Opposite-branch check: could the outer case's `err != nil` branch (695) and the nested select's respond (704/707) both fire? No — they're on disjoint branches of the same `if/else` (693-709); only one executes per goroutine run. Go select semantics guarantee exactly one ready case fires per evaluation; there is no loop wrapping either select, so each executes at most once. `future.respond` is called at most once per goroutine execution across all reachable paths (684, 690, 695, 704, 707 — five call sites, mutually exclusive). Acquittal confirmed.
>
> **Row 4 — raft/leadertransfer-timeout-hang (concurrency, full 5-step): HOLDS**
> raft.go:700-708 nested select has exactly two cases; one is `case <-time.After(r.config().ElectionTimeout)` (701-704), unconditionally present and independent of `leftLeaderLoop`. Opposite-branch check: if `leftLeaderLoop` never closes (e.g., leaderLoop never returns), the bounded `time.After` case still fires after one `ElectionTimeout`, executing `future.respond(err)` (704) and returning, which triggers the deferred flag-clear (678). No unbounded wait exists in the new code. Acquittal confirmed.
>
> **Row 5 — raft/getinstate-restale-race (bug, full 5-step): HOLDS**
> Base (`main`) testing.go:436 captured `inState, highestTerm := c.pollState(s)` once per loop iteration, then the timer-fired branch (originally ~line 471-473 in base) returned that same iteration-start snapshot — a real staleness window spanning up to the full re-armed `timeout` (raft.go/testing.go:427-449 base). Head testing.go:436 discards `inState` from the loop-top poll (`_, highestTerm := c.pollState(s)`) and testing.go:482 re-polls synchronously (`inState, highestTerm := c.pollState(s)`) immediately before `return inState` at 485, inside the `case t, ok := <-timer.C` branch (477). `pollState` (testing.go:394-407) is a direct synchronous read of `r.State()`/`r.getCurrentTerm()` over `c.rafts` with no caching — confirmed by reading its body. Opposite-branch check: is there any intervening step between the timer firing (477) and the fresh poll (482) that could stale it again? No — it's the next two statements, no loop re-entry, no channel wait in between. Acquittal confirmed.
>
> **Row 6 — raft/leadertransferwithwrites-followers-index (bug, full 5-step): HOLDS**
> `Followers()` (testing.go:502-509, unchanged by diff — confirmed absent from `git diff main review-head -- testing.go`) calls `c.t.Fatalf(...)` at 506 when `len(followers) != expFollowers`, before returning. Opposite-branch check: does `c.Followers()[0]` at raft_test.go:2379 run in a goroutine where `Goexit` (which `Fatalf` triggers) wouldn't halt the test? Read the actual new test: line 2379's `c.Followers()[0]` call sits on the test's main goroutine, not inside the writer goroutine spawned at 2352-2377 (which only touches `leader.Apply`/`c.Leader()`, never `Followers()`). `Fatalf`'s `runtime.Goexit()` therefore halts the correct goroutine before the index expression executes. Acquittal confirmed.
>
> **Row 7 — raft/leadertransfer-timeout-message-ambiguity (maintainability, one-citation check): HOLDS**
> `grep -n '"leadership transfer timeout"' ` over head raft.go returns exactly two hits: line 682 (pre-existing outer-select timeout branch, present verbatim in base) and line 702 (the new nested-select timeout branch added by this diff). Both use the identical string `"leadership transfer timeout"`. This confirms the row's stated fact (duplicate wording). Since the row was routed to Observations on a consequence gate, not falsified as untrue, and the one-citation check confirms rather than contradicts the cited fact, the disposition stands.
>
> No incidental fact contradicting any row surfaced. No observation aside is warranted.
>
> ## Batch conclusion
>
> **clean verdict stands**

Sub-agent usage reported by the harness for this dispatch: `subagent_tokens: 44894`, `tool_uses: 17`, `duration_ms: 174932`.

Note on line-number tolerance: the verifier's own count (e.g. raft.go:678/682/700-708/734 for the defer, both timeout-message sites, and the nested select) differs by a small constant offset from the primary reviewer's independent count in the dispatch prompt (raft.go:78/80-84/700-709/135 relative to the printed diff hunk) because the primary cited offsets from the diff hunk's local numbering in the dispatch text versus the verifier's citations from directly reading the live head blob with `git show`. Both counts identify the same code (confirmed by matching surrounding text: `defer r.setLeadershipTransferInProgress(false)`, `fmt.Errorf("leadership transfer timeout")` at both sites, the two-case nested select) — this is a citation-numbering artifact of the dispatch prompt's line-number scheme, not a disagreement about which code was inspected or ruled on.

### Model / effort actually used

The verifier ran as `v5b-verifier-effort-high` with `model: "sonnet"` as instructed, i.e. `claude-sonnet-5` at the harness-default effort (`high`), independent of and unaffected by the primary reviewer's `medium` effort setting, per the agent definition's pin.

No re-open resulted, so no follow-up candidate batch was needed or run; the single verifier dispatch satisfies "at most one fresh follow-up batch" trivially (zero needed).

## 5. Everything consulted beyond the diff

- `python3 /tmp/holdout/skills/v5b/scripts/review_context.py --merge-base 1462fd5e80ad0eb38748f68198505025cb2c96d8 --head cb622973cd2c65dd2752c49d0520f2a3894b2d91` run once from the skill directory context (output saved to `/tmp/holdout/work/b/v5b-effort-medium-seed3/context_output.md`). Provided the manifest, the full function-context diff for all three files, the `ranges` block, and the pre-merge-base `history` block. Not a repo-wide search.
- `git -C /tmp/holdout/runs/b/v5b-effort-medium-seed3 log --oneline -3 review-head` and `... -3 main` — confirmed the packet's pinned head/merge-base against the local clone. Not a search.
- `git -C /tmp/holdout/runs/b/v5b-effort-medium-seed3 remote -v` — confirmed the clone's `origin` is the local mirror path, not `github.com` (offline-hygiene check). Not a search.
- `git -C /tmp/holdout/runs/b/v5b-effort-medium-seed3 diff main review-head --stat` — confirmed the packet's file/line-count manifest matches the clone. Not a search.
- `git -C /tmp/holdout/runs/b/v5b-effort-medium-seed3 show main:raft.go | sed -n '600,920p'` — read the base-branch version of the whole `leaderLoop`/`leadershipTransfer`/`checkLeaderLease` region as a bounded range, to compare the base-branch guarantee against the head-branch code for the introduced-here gate. Not a repo-wide search (single file, single range).
- `git -C /tmp/holdout/runs/b/v5b-effort-medium-seed3 grep -n "func (r \*Raft) leadershipTransfer" -A 60 raft.go` — bounded read of the unchanged `leadershipTransfer` function to check what `doneCh <- nil`/`doneCh <- err` mean and whether it touches `r.logger` (relevant to the `TestRaft_LeadershipTransferStopRightAway` logger-field addition). Single-file, not case-insensitive, not repo-wide.
- `grep -n "func (r \*Raft) setupLeaderState" -A 20 raft.go` and `sed -n '2555,2580p' raft_test.go` — bounded reads confirming `setupLeaderState` doesn't touch `r.logger` and reading the exact `TestRaft_LeadershipTransferStopRightAway` test body. Single-file, not repo-wide.
- `sed -n '1,40p' raft_test.go` (import block) — confirmed `errors`, `sync`, `sync/atomic`, `github.com/hashicorp/go-hclog` are all already imported, so the new test introduces no new import/hygiene issue. Single-file, not repo-wide.
- `git -C /tmp/holdout/runs/b/v5b-effort-medium-seed3 show main:.github/CODEOWNERS` — read the one present guidance-adjacent file listed in packet §7; determined it carries no repository-specific review invariant (just ownership routing), so it contributes nothing to the review-rubric's "repository rules" gate and is excluded from the `guidance` digest input per the output contract's membership rules (it is not `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md`). Not a search.
- `git -C /tmp/holdout/runs/b/v5b-effort-medium-seed3 show main:docs/agents/issue-tracker.md` — confirmed absence (non-zero exit, "does not exist"), consistent with the packet. Not a search.
- `grep -n "case err := <-doneCh:" -A 20 raft.go`, `grep -n "leadershipTransferInProgress" raft.go`, `grep -n "func (c \*cluster) Followers" -A 10 testing.go`, `sed -n '390,406p' raft.go`, `grep -n "getLeadershipTransferInProgress" raft.go` — bounded, single-file, case-sensitive greps used to pin exact current line numbers and confirm every gating call site (`applyCh`, `userRestoreCh`, `configurationsCh`, `configurationChangeChIfStable`) for the candidate-falsification evidence in §3. Not repo-wide, not case-insensitive (no propagation/synchronization-drift candidate was raised that would require the rubric's whole-repository case-insensitive sweep).

No test suite, linter, `go build`, `go vet`, or `go run` was executed anywhere in this run, per the packet's binding "no execution" condition; every claim above is settled by static reading.

## 6. Context digest and inputs

- Digest: `37d14eccc44122fa6e45d8e0705b3ce1ee67ab02fca7e96c277696da01d4da90`
- Computed once via `python3 /tmp/holdout/skills/v5b/scripts/context_fingerprint.py /tmp/holdout/work/b/v5b-effort-medium-seed3/context_input.json`
- Inputs supplied (verbatim from the packet, no re-resolution):
  - `pr.title`: "Fix rare leadership transfer failures when writes happen during transfer"
  - `pr.body`: the PR body verbatim from packet §3 (see `context_input.json`)
  - `issues`: `[]` (packet §4/§1: no closing reference, `issues=none`)
  - `specs`: `[]` (none supplied)
  - `guidance`: `[]` (packet §7: no root or path-scoped `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` exists at the merge-base for any changed path; `.github/CODEOWNERS` is not a member of the digest's `guidance` category under the output contract's exhaustive membership rules)
- Input file retained at `/tmp/holdout/work/b/v5b-effort-medium-seed3/context_input.json`.

## 7. Mechanism checklist

- **Question channel:** did not fire. No candidate reached the static-unresolvability bar; every candidate was settled by code reading (confirmed by both the primary pass and the verifier). No question is published.
- **Clean-verdict / related-acquittal verification:** clean-verdict mode fired, zero-survivor variant (see §4). Rows attacked: all 7 ledger rows (6 dropped + 1 observation-routed), per the rule that zero-survivor mode carries the complete ledger unfiltered by risk surface. No row was re-opened; `clean verdict stands` was returned for every row.
- **Observations:** one published — `raft/leadertransfer-timeout-message-ambiguity`, routed because it fails admission specifically on meaningful/proven consequence (gate 1/4) while remaining an accurate, decisively evidenced fact. See payload for its rendered form.
- **Fix-sufficiency check on concurrency/invariant candidates:** four `concurrency`-kind rows were raised (rows 1-4 in §3/§4); none survived to become a finding, so no `change` needed rule-level widening. The verifier's full 5-step procedure was nonetheless applied to all four (per the kind-based depth rule) and confirmed each acquittal at the rule level — e.g. row 1's ruling explicitly traces both writers of the shared flag and all four gated read sites, i.e. it states the invariant ("the in-progress flag must never read false while the transfer goroutine — including its new wait — is still pending") and enumerates the sibling read/write sites rather than a single transition.
- **Follow-up verifier round:** not run. Zero rows were re-opened by the single clean-verdict batch, so no candidate newly reached render eligibility and the "at most one fresh follow-up batch" allowance was unused.
- **Deferral handling:** the prior review record (packet §6) contains no explicit deferral of a design/naming/API-shape decision ("we can fix this during API review", "let's revisit later", etc.) — `banks`'s thread comment is a design-alternative question that the author answered and the reviewer explicitly marked non-blocking ("not blocking!"), which is a settled discussion, not an open deferral. It was treated as closed, not as an open question, per the rubric's distinction between an explicit deferral and an ordinary resolved review exchange.
- **Retrospective mode:** fired. The target is `merged: true` (packet §1); this run followed the retrospective, non-publishing path throughout — no write was attempted, and the payload's summary carries the mandatory `Mode` line: `**Mode:** Retrospective review of merged pull request; publication disabled.`

## 8. History discipline

I did not read any history beyond the pinned head. History commands actually run:

- `git -C /tmp/holdout/runs/b/v5b-effort-medium-seed3 log --oneline -3 review-head`
- `git -C /tmp/holdout/runs/b/v5b-effort-medium-seed3 log --oneline -3 main`

Both are bounded to the last 3 commits reachable from the pinned `review-head`/`main` refs already present in the (truncated) clone — they did not, and per the packet's binding condition 3 could not, reach anything past the pinned head `cb622973c`. The `## history` block printed by `review_context.py` (reproduced in §5's context-output artifact) lists the last pre-merge-base commit that touched each changed file (`raft.go`, `raft_test.go`, `testing.go`); I read that block but did not run any additional `git log`/`git show` against those older commits beyond what the script itself printed, since no candidate's falsification required inspecting them further.

## 9. Sandbox disclosure

No path outside the sandbox (the clone at `/tmp/holdout/runs/b/v5b-effort-medium-seed3`, the skill snapshot at `/tmp/holdout/skills/v5b/`, the packet directory `/tmp/holdout/packets/b/`, and this run's own work/report/payload paths under `/tmp/holdout/work/b/v5b-effort-medium-seed3/` and `/tmp/holdout/reports/b/`) was read during this run.

## 10. Notes

- **Ambiguity — "worth the author's time" vs. the timeout-message-duplication fact (row 7):** the rubric's Observations rule and gate 4 ("proven consequence") could arguably be read either way for a fact whose only consequence is *reduced debugging clarity* rather than a functional defect. Reading A (applied here): a debugging-clarity-only consequence is not a "proven consequence" for finding-admission purposes because it never manifests as an observable program behavior difference — it fails gate 4 outright and belongs in Observations. Reading B: the indistinguishability of the two log lines is itself a directly demonstrated (not speculative) fact, so gate 4 is met and gate 1's "meaningful impact... enough that the author would benefit" is satisfied at P3/consider. I applied Reading A (the safer, narrower reading, consistent with "zero findings is a valid and preferable result when none do" and the instruction not to inflate low-value facts into findings) and recorded this choice here rather than in the payload's `Ambiguities` section, because the term in tension (`proven consequence`) is a routing judgment about one already-non-actionable fact, not a live axis affecting the review's semantic status either way — under Reading B the same fact would be `P3`/`consider`, which still would not change the derived status (`Approved`, since `consider` never blocks). Both readings produce the same net effect on the published review below the priority-1 threshold at which I judged the `Ambiguities` section warranted, so I did not add a formal `Ambiguities` entry to the summary body.
- **Judgment call — prior-review thread treatment:** treated `banks`'s design-alternative question and `ncabatoff`'s answer (packet §6, threads 1-2) as a closed, non-blocking discussion (per `banks`'s own "not blocking!" in the review submission) rather than as an open item to re-litigate or re-raise as a question, consistent with rubric gate 6 (maintainer approval establishes acceptance of what the review record explicitly addresses) and the distinction from an explicit deferral (§7).
- **Judgment call — guidance digest membership:** `.github/CODEOWNERS` (the only present file from packet §7's guidance survey) was excluded from the `context` digest's `guidance` array because the output contract's membership rules (output-contract.md, "guidance is exactly...") enumerate only `AGENTS.md`, `CLAUDE.md`, and root `CONTEXT.md`; `CODEOWNERS` matches none of those three categories. This is a mechanical application of an exhaustive rule, not a genuine two-reading ambiguity, so no `Ambiguities` entry was warranted.
- **Effort-level note:** running at `medium` effort (one step below default), I bounded the candidate search to the mechanisms directly implicated by the diff's stated intent (the added wait's blocking scope, its termination guarantee, its interaction with concurrent transfer requests and with `future.respond`) plus the two test/testing.go changes' own correctness, rather than additionally re-deriving alternative implementations of the leadership-transfer protocol or auditing unrelated `leaderLoop` branches (`verifyCh`, `commitCh`, `bootstrapCh`, etc.) that the diff does not touch and that no candidate implicated. This is a scope judgment consistent with the rubric's "use risk signals to direct attention, not to create findings" and "complete inspection" (every changed file was reviewed; unchanged, undisturbed branches of the same `select` were read as printed context but not independently re-audited beyond confirming they don't call `getLeadershipTransferInProgress` differently than before).
- **Wall clock:** approximately 25 minutes from reading the dispatch file to completing both output files, including the one foreground verifier round-trip.
