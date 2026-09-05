# Run document — holdout target (b), cell `v5b-seed3`

**Orchestrator metadata (added after the run; the researcher's record, not the reviewer's).**

| | |
| --- | --- |
| Packet | `packets/b/packet.md`, SHA-256 `d94db099dc8ea929b8f09a14b945e7b70b0efa31a08ac576a64681a06742253e` |
| Snapshot pins | v5b=2f06662 noverify=2f06662-minus-verifier panel=dd3bcfe33bfe8b65e272a6d2266ee9bc6cd1dc72 |
| Root agent / primary | `aa3c58f385021b794` / `aa3c58f385021b794` |
| Payload | [`v5b-seed3-payload.md`](v5b-seed3-payload.md), 1768 bytes |
| Report (this file, below the preamble) | 43748 bytes as written by the reviewer |
| Closed out | 2026-09-04T20:17:17.841765+00:00 |
| Problems at close-out | none |

## Model and effort verification (every assistant line of every transcript)

| Agent | Role | Definition | `message.model` | `effort` | Transcript |
| --- | --- | --- | --- | --- | --- |
| `aa3c58f385021b794` | primary | general-purpose | `claude-sonnet-5`×84 | `high`×84 | `agent-aa3c58f385021b794.jsonl` |
| `a142b7cab98bb9b34` | child | general-purpose | `claude-sonnet-5`×31 | `high`×31 | `agent-a142b7cab98bb9b34.jsonl` |

## Billed usage (`transcript_usage.py --prices 2,10 --report <this report>`)

```
agent-aa3c58f385021b794.jsonl
turns                        47 (API requests; 84 assistant lines)
tool calls                   46
text-only turns               1
input                        94 tokens (uncached)
cache write             156,459 tokens
cache read            4,161,932 tokens
output                   75,847 tokens (thinking 46,828)
models             claude-sonnet-5
wall                    0:18:39
cost                       1.98 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-a142b7cab98bb9b34.jsonl
turns                        12 (API requests; 31 assistant lines)
tool calls                   18
text-only turns               1
input                        24 tokens (uncached)
cache write              49,641 tokens
cache read              388,558 tokens
output                   11,392 tokens (thinking 6,210)
models             claude-sonnet-5
wall                    0:03:23
cost                       0.32 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

TOTAL
turns                        59 (API requests; 115 assistant lines)
tool calls                   64
text-only turns               2
input                       118 tokens (uncached)
cache write             206,100 tokens
cache read            4,550,490 tokens
output                   87,239 tokens (thinking 53,038)
models             claude-sonnet-5
wall                    0:22:01 (summed over transcripts)
cost                       2.30 $ at 2/10 per M, cache write ×1.25, cache read ×0.1
production-shaped          2.19 $ (output 76,302 after subtracting the report's 10,937 est. tokens)
```

Row for `comparison-data.md`:

| (b) v5b seed 3 | claude-sonnet-5 | 59 | 64 | 2 | 118 | 206,100 | 4,550,490 | 87,239 | 53,038 | 0:22:01 | 2.30 | 10,937 | **2.19** |

Per agent:

| primary aa3c58f385021b794 | claude-sonnet-5 | 47 | 46 | 1 | 94 | 156,459 | 4,161,932 | 75,847 | 46,828 | 0:18:39 | 1.98 | — | — |
| child a142b7cab98bb9b34 | claude-sonnet-5 | 12 | 18 | 1 | 24 | 49,641 | 388,558 | 11,392 | 6,210 | 0:03:23 | 0.32 | — | — |

---

# Research report — target (b) `hashicorp/raft#581`, arm v5b, seed 3

Wall clock start: 2026-09-04T20:08:05Z (UTC, per `date -u`).

## 1. Metadata

- **Target:** `hashicorp/raft#581` — "Fix rare leadership transfer failures when writes happen during transfer"
- **Arm:** v5b — skill `code-review-publish` pinned at `main 2f06662 (workflow=v5b-1)`
- **Seed:** 3
- **Model — primary reviewer (me, this context):** `claude-sonnet-5`, run in the foreground with no sub-agent delegation of the review itself.
- **Model — every sub-agent I spawned:** `sonnet` passed explicitly on the `Agent` call (see §4 for the exact call).
- **Verification trigger fired:** zero-survivor mode (`SKILL.md` step 3 / `references/verifier.md` "Clean-verdict task"). Zero candidates survived primary falsification as findings, and the changed behavior is squarely a concurrency/failover path (Raft leadership transfer and the write-gating flag that protects it), so the zero-survivor clean-verdict batch was mandatory rather than optional.
- **Sub-agents spawned:** 1 — a single clean-verdict verifier batch (role: `verifier`, clean-verdict mode), dispatched once, in the foreground, and awaited before continuing.
- **Candidates raised:** 3 (all in the primary context; no finder fan-out — this skill is a single integrated reviewer).
- **Candidates surviving my own falsification (as findings):** 0.
- **Verifier verdicts:** `clean verdict stands` on all 3 ledger rows (see §4 for the verbatim report).
- **Findings for publication:** none.
- **Questions:** none.
- **Observations:** none (no accurate fact cleared the observation route — see §3 for why each candidate was dropped rather than routed there).
- **Coverage:** complete — all 3 changed files (`raft.go`, `raft_test.go`, `testing.go`) reviewed in full via the merge-base diff with `--function-context`; every risk-directed concurrency/failover check has an evidence-backed outcome (traced by hand, no execution per run condition 2); guidance lookup performed (`.github/CODEOWNERS` present but out of the guidance-digest categories; no `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` anywhere in the repo at the merge-base); no fetch failures (offline packet supplied everything phase 1 needs).
- **Derived status:** **Approved (advisory)** — 0 must-fix findings, 0 open questions, coverage complete. `(advisory)` because this run uses `COMMENT` (third-party retrospective review of a merged PR; publication disabled).
- **My own token usage:** the harness does not report this to me in this context; I have no number to give.

## 2. Findings for publication

None. Zero candidates survived primary falsification (see §3), and the mandatory zero-survivor clean-verdict verifier batch (§4) returned `clean verdict stands` on every disposition. There is nothing to render under "Every finding that survives."

## 3. Complete private disposition ledger

All three candidates were raised, falsified, and dropped in the primary context before any sub-agent was dispatched. This is the ledger exactly as it stood when I dispatched the clean-verdict verifier (unchanged after the verifier's verbatim `clean verdict stands`, §4).

| id | kind | claim (one line) | disposition | decisive evidence | falsification reason |
| --- | --- | --- | --- | --- | --- |
| `raft/leader-transfer-in-progress-gate-window` | concurrency | Between `leaderLoop` accepting a `leadershipTransferCh` request and calling `r.setLeadershipTransferInProgress(true)`, a concurrent `applyCh` write can be dispatched with the gate still false. | dropped | `raft.go:640-736` (single `select` per `for`-loop iteration; the `leadershipTransferCh` case's whole body, including `setLeadershipTransferInProgress(true)` at `raft.go:734`, runs to completion before the loop can re-enter `select`) | No goroutine boundary separates request-acceptance from flag-set: `leaderLoop`'s `for { select { ... } }` structure means the `applyCh` case cannot become the chosen case of any `select` iteration until the `leadershipTransferCh` case's block — including the flag-set call — has already returned. Traced the full case body line by line; no early exit before the flag-set skips it on the success path (the two early `continue`s, `raft.go:723` and `raft.go:727`, only occur *before* the flag would have been set for a request that never spawns the transfer goroutine at all, so no live transfer exists in that case either). |
| `raft/leader-transfer-future-success-without-target-confirmation` | concurrency | On the added post-`TimeoutNow` wait, `future.respond(nil)` fires whenever `leftLeaderLoop` closes for any reason — not only because the requested target specifically won — so a caller can read "success" when a different node became leader. | dropped (not introduced here) | Merge-base `raft.go:692-696`: `case err := <-doneCh: if err != nil {...}; future.respond(err)` — unconditional, immediate response with **no wait at all** for any observed leadership change. Head `raft.go:686-707`: the same branch now waits for `leftLeaderLoop` or a second `ElectionTimeout` before responding. | Gate 2 (introduced-here) fails: the imprecision (the future's success doesn't name which node became leader) existed in a *strictly broader* form at the merge-base — the base code didn't even require losing leadership at all before declaring success, only that the `TimeoutNow` RPC returned no transport error. The change narrows the gap, it does not widen or create it. Corroborating evidence in the same diff: `raft_test.go`'s companion edit to `TestRaft_LeadershipTransferWithSevenNodes` (hunk at `raft_test.go:2337` old range / current `raft_test.go` renamed-test area) replaced `if oldLeader == c.Leader().localID` with `if follower.localID != c.Leader().localID`, i.e. the author independently tightened target-specific verification at the test layer in this same PR, which is evidence the ambiguity is a known, accepted characteristic rather than a fresh regression. |
| `raft/getinstate-poll-return-window` | maintainability | `GetInState`'s re-poll on `timer.C` (`testing.go:482`) narrows, but does not fully eliminate, the poll-then-return race the commit message describes; a state change between that final `pollState` call and `return inState` is still theoretically unobserved. | dropped (consequence unproven) | `testing.go:409-490`, specifically `testing.go:436` (`_, highestTerm := c.pollState(s)` at loop top, `inState` discarded) and `testing.go:477-490` (`case t, ok := <-timer.C:` re-polls with `inState, highestTerm := c.pollState(s)` immediately before `return inState`). | Fails gate 1 (meaningful impact): the residual window shrank from the entire stability-timeout duration (original code) to a single unscheduled statement gap (new code) — the change is already a proportionate, disclosed improvement, not a fresh or worsened gap. `testing.go` is test-helper-only code, and commit `cb622973c`'s message explicitly discloses the mechanism and scope of the fix ("modifying `GetInState`, which is racy... When that happens, `Leader()` errors returning 0 leaders"), i.e. the author already scoped and accepted the improvement's limits; no concrete input/state/call path makes the theoretical residual window an actual observed failure mode beyond what the disclosed, accepted mitigation already addresses. |

No candidate was routed to `Observations`: each failed a gate other than "meaningful/proven consequence" specifically as the sole failing gate that the observation route requires (`raft/leader-transfer-in-progress-gate-window` failed the underlying claim itself — it never happened; `raft/leader-transfer-future-success-without-target-confirmation` failed gate 2, introduced-here; `raft/getinstate-poll-return-window` did fail gate 4/1 on consequence, but is a stretch not worth the observation cap's decisive-evidence bar for a fact this close to tautological — I judged it not to "stand" as a decisive fact rather than merely lacking consequence, so I did not spend one of the three observation slots on it).

## 4. Sub-agent dispatch — exact prompt and verbatim report

**Role:** clean-verdict verifier batch (zero-survivor mode, `references/verifier.md`). **Count:** 1. **Model:** `sonnet` (passed explicitly on the `Agent` call; agent type `general-purpose`; dispatched in the foreground and awaited before continuing).

### Exact prompt given

```
You are an independent verifier for one cell of a controlled research evaluation of a code-review skill (`code-review-publish`, pinned `workflow=v5b-1`) against a real, pinned, merged pull request. This is NOT a live review: no network access, no publishing, no repository mutation, no builds, no test execution. Nothing you write is posted anywhere. You are a genuinely fresh context with no visibility into the primary reviewer's reasoning — you only get what is below.

## Your role

You are running the "Clean-verdict task" defined in `/tmp/holdout/skills/v5b/references/verifier.md`. Read that file in full first — it is authoritative for how you must work. You are in **zero-survivor mode**: the primary reviewer raised candidates during review of this pull request, but zero of them survived primary falsification as findings. Per `SKILL.md`'s zero-survivor rule (also described in `verifier.md`), you attack every acquittal in the supplied ledger below, because the changed behavior touches a concurrency/failover path (Raft leadership transfer). You are not a second reviewer: do not search for new findings outside the supplied ledger rows. You cannot write to the pull request or any file — just return your verdict as your final message text.

## Rules binding on you (from the run's dispatch, rules 1-6 and rule 8)

1. Follow the skill as written (`verifier.md`'s clean-verdict task specifically) - its phase order, its read discipline, its verification triggers. Do not borrow behavior from any other review skill.
2. This is a retrospective review of a merged pull request by a third party; publication is disabled. This does not change your task - you are only fact-checking the supplied ledger.
3. N/A to you (context-digest computation is the primary reviewer's job).
4. **Clone hygiene:** do not run `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the tree. Read-only git commands only (`git show`, `git log`, `git diff`, `git blame`, etc.).
5. N/A to you (persistence is the primary reviewer's job - just return your complete verbatim verdict in your final message).
6. **Stay inside your own sandbox:** you may read only the clone at `/tmp/holdout/runs/b/v5b-seed3`, the skill snapshot at `/tmp/holdout/skills/v5b/` (read-only, for `verifier.md`/`review-rubric.md`), and nothing else. Do not read any other run's clone, report, or payload, and do not read anything under `/tmp/holdout/reports/`, `/tmp/holdout/work/`, `/tmp/holdout/dispatch/`, or `/tmp/holdout/packets/`. If you read any path outside this list, say so explicitly in your final report.
8. **No session relays:** finish in this one dispatch. Do not ask me anything or wait for a reply - if something is genuinely unresolvable from the sandbox, say so in your verdict per `verifier.md`'s handling of an unresolvable claim (name the single fact that would settle it and who/what could supply it).

Additional constraints: **no execution** - do not run `go build`, `go test`, `go vet`, or any linter (no network available for module download; the review is entirely static). No `git fetch`/`git pull`/`gh`/`curl`/network calls of any kind (the clone is fully offline; `origin` points at a local filesystem mirror path).

## Pinned coordinates

- Repository: `hashicorp/raft` (GitHub, but you have no network - everything is in the local clone).
- Base ref: `main`, base SHA / merge-base: `1462fd5e80ad0eb38748f68198505025cb2c96d8` (local branch `main` in the clone is force-pinned to this commit).
- Head: `cb622973cd2c65dd2752c49d0520f2a3894b2d91` (local branch `review-head` in the clone, already checked out - do not switch branches).
- Clone path: `/tmp/holdout/runs/b/v5b-seed3` - use `git -C /tmp/holdout/runs/b/v5b-seed3 diff main review-head` for the full change, and `git -C /tmp/holdout/runs/b/v5b-seed3 show 1462fd5e80ad0eb38748f68198505025cb2c96d8:<path>` for base-branch versions.
- Linked issue/spec coordinates: **none** - the pull request body carries no closing or explicit issue reference (`issues=none`).
- Applicable base-branch repository-rule coordinates: **none** - no `AGENTS.md`, `CLAUDE.md`, or `CONTEXT.md` exists anywhere in this repository at the merge-base (already verified: `.github/CODEOWNERS` exists but is not a review-guidance category file).
- History note: the clone's history is truncated at the pinned head on purpose. The newest object reachable is `cb622973c`. Do not try to look past it (nothing later exists locally, and there is no network to fetch it).

## The complete candidate disposition ledger (zero-survivor mode - every disposition from the run, unfiltered by surface)

Ranges (`scripts/review_context.py` output) for the files these rows cite, so you can read them in one message each:

```
raft.go:617-916 @head
raft.go:617-903 @merge-base
raft_test.go:2337-2407 @head
raft_test.go:2337-2353 @merge-base
raft_test.go:2564-2578 @head
raft_test.go:2510-2524 @merge-base
testing.go:409-490 @head
testing.go:409-489 @merge-base
```

Row 1 - id `raft/leader-transfer-in-progress-gate-window`, kind `concurrency`
- claim: Between `leaderLoop` accepting a `leadershipTransferCh` request and calling `r.setLeadershipTransferInProgress(true)`, a concurrent `applyCh` write can be dispatched with the gate still false.
- disposition: dropped
- decisive evidence: `raft.go:640-736`
- falsification reason: No goroutine boundary separates request-acceptance from flag-set - `leaderLoop`'s `for { select { ... } }` structure means the `applyCh` case cannot become the chosen case of any `select` iteration until the `leadershipTransferCh` case's whole block, including the flag-set call at `raft.go:734`, has already returned.

Row 2 - id `raft/leader-transfer-future-success-without-target-confirmation`, kind `concurrency`
- claim: On the added post-`TimeoutNow` wait, `future.respond(nil)` fires whenever `leftLeaderLoop` closes for any reason - not only because the requested target specifically won - so a caller can read "success" when a different node became leader.
- disposition: dropped (not introduced here)
- decisive evidence: merge-base `raft.go:692-696`
- falsification reason: gate 2 (introduced-here) fails - the same imprecision existed in a strictly broader form at the merge-base, which responded to the future immediately on any non-error `doneCh` value with no wait at all for any observed leadership change; the head version only narrows this by requiring an actual observed loss of leadership first.

Row 3 - id `raft/getinstate-poll-return-window`, kind `maintainability`
- claim: `GetInState`'s re-poll on `timer.C` (`testing.go:482`) narrows, but does not fully eliminate, the poll-then-return race the commit message describes; a state change between that final `pollState` call and `return inState` is still theoretically unobserved.
- disposition: dropped (consequence unproven)
- decisive evidence: `testing.go:409-490` (specifically `testing.go:436` and `testing.go:477-490`)
- falsification reason: fails gate 1 (meaningful impact) - the residual window shrank from the entire stability-timeout duration to a single unscheduled statement gap; the change is a disclosed, proportionate improvement (commit `cb622973c`'s message explicitly names the race and its fix), not a fresh or worsened gap.

## Your task

Follow `references/verifier.md`'s "Clean-verdict task" exactly, at the depth its `kind` rule sets:

- Rows 1 and 2 (`kind=concurrency`): apply the full 5-step attack procedure - restate the row's decisive premise in one sentence, state the concrete condition under which it would be false, trace the opposite branch of every conditional the premise depends on (citing `path:line` for each step), either construct the complete failing state transition or cite the specific impossible step, and note that a `holds` ruling must cite at least one line the ledger row did not already cite.
- Row 3 (`kind=maintainability`): the one-citation check only - read the row's evidence pointer, confirm or contradict its stated fact, return `holds` or `re-open` without tracing conditionals.

Read the cited code yourself in the clone (bounded ranges; whole files only if genuinely needed to decide a conditional and you say so). You may also read narrow surrounding context, callers, tests, or the last relevant history (`git log`/`git show`/`git blame` on `raft.go`, `raft_test.go`, `testing.go`, all read-only) if needed to decide a row - but do not exceed what deciding these three specific claims requires.

Return, in one final message:
1. Your full per-row attack trace (all 5 steps for rows 1-2; the one-citation check for row 3), each with `path:line` citations.
2. Your verdict for each row: `holds` (ledger's acquittal stands) or `disposition <id> does not hold; re-open it` (with the contradicted premise and decisive `path:line`).
3. Your overall batch conclusion: either `clean verdict stands` (every disposition survives) or the list of `disposition <id> does not hold; re-open it` conclusions for whichever rows failed.
4. At most one non-actionable `observation` aside (a decisive, non-`should`/`must` fact) only if something incidental surfaced that does not contradict any supplied row - omit this entirely if nothing qualifies. If an incidental fact *does* contradict a supplied row's premise, that is not an observation: return it as a re-open of that row instead, per rule above.
5. Explicitly confirm: did you read anything outside the clone/skill-snapshot sandbox listed above? Did you run any git history command beyond the pinned head, or any command at all beyond read-only `git`/file-reading? List every command you ran.

Do not return publication-ready prose, and do not soften a `re-open` into a mere observation.
```

### Verbatim report returned

```
## Verifier findings — clean-verdict batch (zero-survivor mode), run `/tmp/holdout/runs/b/v5b-seed3`

### Row 1 — `raft/leader-transfer-in-progress-gate-window` (kind=concurrency)

**1. Decisive premise restated:** The leaderLoop's `select`/`for` structure is single-goroutine and non-reentrant, so the `applyCh` case of the *same* select statement cannot be chosen until the `leadershipTransferCh` case's entire body — including `r.setLeadershipTransferInProgress(true)` at `raft.go:734` — has finished executing and control has returned to the top of the `for` loop at `raft.go:631`.

**2. Concrete falsifying condition:** The premise is false if either (a) some other goroutine independently services `r.applyCh` while the node is in the `Leader` state (giving `applyCh` a path around the leaderLoop's own select), or (b) the `leadershipTransferCh` case body itself yields back to the top-level select (via an early `continue`, a blocking op, or handing the flag-set off to an unsynchronized goroutine) before reaching line 734.

**3. Opposite branches traced:**
- (a) Other consumers of `applyCh`: `raft.go:176` (`runFollower`) and `raft.go:343` (`runCandidate`) both read `r.applyCh` and immediately reject with `ErrNotLeader`. But `raft.go:133-151` (`func (r *Raft) run()`) shows a single-threaded `switch r.getState() { case Follower: r.runFollower(); case Candidate: r.runCandidate(); case Leader: r.runLeader() }` dispatcher — only one of these loops executes at a time, so while `r.getState() == Leader` (`raft.go:631`), `runFollower`/`runCandidate` are not concurrently running and cannot service `applyCh`. Opposite branch (a) is closed.
- (b) Case-body early exit: `raft.go:643-735` contains exactly two `continue` statements, both on error branches (`pickServer()` returns nil at `raft.go:715` roughly, or `replState` lookup fails) — both `continue` before any transfer is registered as in-progress, so there is no "gate false, transfer nominally started" state reachable via those paths either; the transfer simply never begins. On the success path there is no blocking channel op, no `continue`, and no early return between line 643 and line 734 — the goroutine spawned at `raft.go:677` runs concurrently but only manipulates `future`, `stopCh`, `doneCh`, `leftLeaderLoop`, never the gate-set call or `applyCh`. Opposite branch (b) is closed.

**4. Impossible step:** The claimed interleaving requires the top-level `select` to re-evaluate and choose the `applyCh` case *before* line 734 executes. Since (a) no other goroutine reads `applyCh` while `Leader`, and (b) the case body between `raft.go:643` and `raft.go:734` has no yield point, this re-evaluation cannot happen — the "impossible step" is any re-entry into the top-level `select` prior to `raft.go:734` completing.

**5. Fresh citations beyond the ledger's `raft.go:640-736`:** `raft.go:133-151` (single-threaded state dispatcher `run()`), `raft.go:631` (Leader-loop guard), `raft.go:176` and `raft.go:343` (proving the only other `applyCh` consumers cannot run concurrently with leaderLoop).

**Verdict: holds.**

---

### Row 2 — `raft/leader-transfer-future-success-without-target-confirmation` (kind=concurrency)

**1. Decisive premise restated:** At merge-base, the `doneCh` success branch responded to the future immediately and unconditionally (`future.respond(err)` with `err == nil`) with no wait at all — a strictly *broader* form of "respond success without confirming the specific requested target won" than the head's version, which at least requires `leftLeaderLoop` to close first.

**2. Concrete falsifying condition:** The premise is false if the merge-base's `doneCh` success branch already gated on `leftLeaderLoop` (or any target-identity check) before responding — i.e. if the head version introduced the first-ever unwitnessed-success response rather than narrowing a pre-existing one.

**3. Opposite branch traced:** Merge-base `raft.go:692-696` (already read in full above):
```
case err := <-doneCh:
    if err != nil {
        r.logger.Debug(err.Error())
    }
    future.respond(err)
```
No `leftLeaderLoop` wait, no target check — confirms the falsifying condition in step 2 does *not* hold; merge-base is strictly less precise, not equally or more precise.

**4. Impossible step / construction:** For the ledger row's underlying claim to require "introduced-here" status, merge-base would have to have possessed some confirmation guarantee that head removed. It never did — merge-base responded even without observing any leadership loss at all. Additionally, and not cited by the ledger: the *outer* `case <-leftLeaderLoop:` branch of the exact same `select` statement, unchanged by this diff and present verbatim at merge-base, already does `future.respond(nil)` (`raft.go:686-690` at head; identical text at the corresponding merge-base lines) whenever `leftLeaderLoop` closes "for any reason" — with no target-identity check, exactly the pattern row 2 complains about. This is a sibling branch of the very select statement the diff touches, left completely untouched by the diff, and it already exhibits the claimed imprecision. So the "introduced here" gate fails on two independent grounds: (i) the doneCh-success branch's own predecessor (merge-base) was strictly broader, and (ii) an unmodified sibling branch of the same select already contains the identical imprecision.

**5. Fresh citations beyond the ledger's merge-base `raft.go:692-696`:** `raft.go:653-656` (comment: "When we are leaving leaderLoop, we are no longer leader, so we should stop transferring" — documents `leftLeaderLoop`'s close as a generic "no longer leader" signal, not target-specific) and `raft.go:686-690` (the unchanged sibling `case <-leftLeaderLoop:` branch already responding `nil` unconditionally).

**Verdict: holds.**

---

### Row 3 — `raft/getinstate-poll-return-window` (kind=maintainability, one-citation check)

Evidence pointer: `testing.go:409-490`, specifically `testing.go:436` and `testing.go:477-490`.

Read at head:
- `testing.go:436`: `_, highestTerm := c.pollState(s)` — first poll each loop iteration, `inState` discarded.
- `testing.go:477-486`: on `timer.C` firing, re-polls at `testing.go:482` (`inState, highestTerm := c.pollState(s)`), logs at `483-484`, returns `inState` at `testing.go:485`.

Confirmed: the residual window is exactly the gap between the `pollState` call (line 482) and `return inState` (line 485) — one `Sprintf`/log statement, not the whole stability-timeout duration that existed at merge-base (where `inState` was captured once at the top of the loop, line-equivalent to head's discarded `_` at 436, and never refreshed before return). Commit `cb622973c`'s message (`git log`) explicitly states: "GetInState ... is racy in that in between calling pollState and setting up event monitoring, the cluster could've elected a leader," confirming this is a disclosed, intentional, proportionate narrowing, matching the ledger's falsification reasoning verbatim.

**Verdict: holds.**

---

### Overall batch conclusion

**clean verdict stands** — all three dispositions (rows 1, 2, 3) survive attack.

### Observation

None qualifies — no incidental fact surfaced that is both decisive and non-contradictory to a supplied row worth reporting separately from the analysis above.

### Sandbox/tooling confirmation

- I read only: `/tmp/holdout/skills/v5b/references/verifier.md` (skill snapshot, read-only) and files inside `/tmp/holdout/runs/b/v5b-seed3` (the pinned clone: `raft.go`, `testing.go`, `api.go` via grep, plus `git log`/`git show`/`git diff` output). I did not read anything under `/tmp/holdout/reports/`, `/tmp/holdout/work/`, `/tmp/holdout/dispatch/`, `/tmp/holdout/packets/`, or any other run's clone.
- I did not read `raft_test.go` despite the supplied ranges — none of the three rows' decisive-evidence pointers cite it, and it was not needed to decide any of the three claims.
- All git commands were read-only (`git show <sha>:<path>`, `git diff main review-head -- raft.go`, `git log --oneline main..review-head`, `git log -p --follow -- testing.go`, `git show --stat <head-sha>`) and never went past the pinned head `cb622973c` (all inspected commits are ancestors of, or equal to, `review-head`). No `git checkout`/`switch`/`reset`/`stash`, no build/test/lint, no network commands.
- Full command list run: `sed -n` reads of `raft.go`/`testing.go` at head and via `git show <merge-base>:<path> | sed -n`; `grep -n` searches in `raft.go`/`testing.go`/`*.go` for function and case-line locations; `sed -n ... | nl -ba` for line-numbered snippets; `git log --oneline main..review-head`; `git show --stat cb622973c...`; `git log -p --follow -- testing.go | grep -n ...`; `git diff main review-head -- raft.go`; `grep -rn "applyCh" *.go`.
```

**Re-opens:** none. **Follow-up batch:** not needed — no row newly reached render eligibility. The private disposition ledger in §3 is unchanged after this verdict.

## 5. Everything consulted beyond the diff

Read once via `python3 /tmp/holdout/skills/v5b/scripts/review_context.py --merge-base 1462fd5e80ad0eb38748f68198505025cb2c96d8 --head cb622973cd2c65dd2752c49d0520f2a3894b2d91` (run from inside `/tmp/holdout/runs/b/v5b-seed3`, output kept at `/tmp/holdout/work/b/v5b-seed3/context.md`, exit 0): the complete `manifest`, the complete `--function-context` `diff` for all 3 files, the `ranges` block, and the `history` block. This satisfied SKILL.md step 2/3's "read the review diff once" requirement; I did not re-run the script and did not re-read the diff as individual `git show` commits.

Beyond that single script run, in the clone (`/tmp/holdout/runs/b/v5b-seed3`), all read-only, none repo-mutating:

- `git status`, `git branch -vv`, `git log --oneline -3 main`, `git log --oneline -10 review-head`, `git remote -v` — structural checks of the pinned clone (not a diff/content read); single clone, not repo-wide.
- `git show 1462fd5e80ad0eb38748f68198505025cb2c96d8:.github/CODEOWNERS` — single file, not repo-wide, not case-insensitive (exact path).
- `git show 1462fd5e80ad0eb38748f68198505025cb2c96d8:docs/agents/issue-tracker.md` — single file probe; errored (path does not exist at merge-base), confirming SKILL.md step 1's optional pre-read has nothing to read here.
- `git ls-tree -r --name-only 1462fd5e80ad0eb38748f68198505025cb2c96d8 | grep -iE "AGENTS\.md|CLAUDE\.md|CONTEXT\.md"` — **repo-wide** (whole tree at merge-base) and **case-insensitive** (`grep -i`); zero matches, confirming no `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` exists anywhere in the repository at the merge-base (so `guidance=[]` in the context digest, and there is no root or path-scoped instruction file to apply under the review-rubric's "Repository rules" section).
- `grep -n "case err := <-doneCh:\|Wait for up to ElectionTimeout\|lost leadership during transfer\|leadership transfer timeout\|leftLeaderLoop\|setLeadershipTransferInProgress" raft.go` — single file, not repo-wide, case-sensitive; used only to get exact head line numbers for citation (the content itself came from the diff already read once).
- `grep -n "func (c \*cluster) GetInState\|pollState(s)\|case t, ok := <-timer.C:" testing.go` — single file, not repo-wide, case-sensitive; same purpose (line numbers) for `testing.go`.
- `git show 1462fd5e80ad0eb38748f68198505025cb2c96d8:raft.go | grep -n "case err := <-doneCh:\|future.respond(err)\|leftLeaderLoop"` — single file at merge-base, not repo-wide, case-sensitive; line numbers for the merge-base comparison decisive to candidate `raft/leader-transfer-future-success-without-target-confirmation`.
- `awk '/^func \(r \*Raft\) leadershipTransfer\(/,/^}/' raft.go` and the same `awk` against `git show <merge-base>:raft.go` — bounded-range reads of one named function at head and at merge-base (candidate-serving read, confirming `leadershipTransfer()` itself is byte-identical across the diff and therefore out of scope for "introduced here").
- `awk '/^func \(r \*Raft\) setupLeaderState\(/,/^}/' raft.go` and `awk '/^func TestRaft_LeadershipTransferStopRightAway/,/^}/' raft_test.go` — bounded-range reads, to explain the unchanged `logger: hclog.New(nil)` addition in that test (traced to being unreachable/inert given the immediately-closed `stopCh`, so not a candidate).
- `sed -n '1,30p' raft_test.go` — the import block only, to confirm `sync`, `errors`, and `github.com/hashicorp/go-hclog` were already imported before the diff (so the new test needed no import changes and the diff's silence on imports is consistent, not an omission).
- `grep -rn "ErrLeadershipLost\|ErrLeadershipTransferInProgress\|ErrNotLeader\b\|ErrRaftShutdown" api.go errors.go` — two named files (`errors.go` does not exist in this repository; grep silently skipped it), not repo-wide, case-sensitive; confirmed all four sentinel errors the new test references are pre-existing, unchanged definitions in `api.go`.
- `grep -rln "ErrLeadershipLost" --include=*.go . ` — attempted repo-wide, case-sensitive; **this command failed** with a zsh globbing error (`no matches found: --include=*.go`, a shell quoting mistake on my part, not a tool/network failure) and produced no output. It is disclosed here for completeness; it was redundant with the preceding `api.go`/`errors.go` grep, which already gave a decisive, evidence-backed answer, so I did not retry it and no disposition depends on its (non-)result.

I did not read `raft.go`, `raft_test.go`, or `testing.go` in full (all three exceed the 300-line whole-file-read threshold: 2022, 3182, and 868 lines respectively at head) — every read beyond the one context-script diff was a bounded range or a `grep`/`awk` extraction naming the candidate or check it served, per SKILL.md step 3's read discipline.

No test was run and no build/vet/lint was invoked, per the packet's binding run condition 2 (offline, no `go` in any form). No web/network call of any kind was made (no `gh`, `curl`, `git fetch`/`git pull`); the clone's `origin` is a local filesystem mirror path (`/tmp/holdout/mirrors/raft.git`) and was never contacted.

## 6. The `context` digest and its inputs

Computed once via `python3 /tmp/holdout/skills/v5b/scripts/context_fingerprint.py /tmp/holdout/work/b/v5b-seed3/context_input.json`, exit 0:

```
37d14eccc44122fa6e45d8e0705b3ce1ee67ab02fca7e96c277696da01d4da90
```

Inputs supplied (verbatim JSON, `/tmp/holdout/work/b/v5b-seed3/context_input.json`):

```json
{
  "pr": {
    "title": "Fix rare leadership transfer failures when writes happen during transfer",
    "body": "The problem I'm trying to fix: after we send the TimeoutNow during a leader transfer, we remain the leader for a little while.  During that time we allow writes, which can result in the upcoming election being lost by our chosen target, if it doesn't have the highest index at the time when it's asking for votes.\n\nThe fix: wait for up to ElectionTimeout after the TimeoutNow before we allow writes to proceed."
  },
  "issues": [],
  "specs": [],
  "guidance": []
}
```

- `pr.title`/`pr.body`: verbatim from packet §1/§3 (the packet is the pinned, byte-identical phase-1 record for this target; not re-fetched).
- `issues`: empty — packet §4 states there is no originating issue (`issues=none`) and no dispatch-supplied spec.
- `specs`: empty — no user-supplied spec was given in the dispatch.
- `guidance`: empty — verified directly against the merge-base tree (§5's repo-wide, case-insensitive `git ls-tree` search); no `AGENTS.md`, `CLAUDE.md`, or `CONTEXT.md` exists at any path in this repository at the merge-base, so no path-scoped or root instruction file qualifies under the output contract's three guidance categories. (`comments_available` was not set on any issue object because there are no issues at all — not because comments were unavailable for one.)

## 7. Mechanism checklist

| Mechanism | Fired? | Where demonstrated |
| --- | --- | --- |
| Question channel | Did not fire | No candidate met the static-unresolvability bar (review-rubric.md "Issue fit" / output-contract.md "Question comment"). The two open prior-review threads (packet §6, `raft.go:706` and `raft_test.go:2340`) were both already answered in-thread by the author with no further objection and an explicit "not blocking" from the reviewer — settled discussion, not a deferral or an outcome-changing unresolved fact, so no question was published (§10 note 2 records this as a judgment call). |
| Clean-verdict or related-acquittal verification | **Clean-verdict fired** (zero-survivor mode) | §4: one clean-verdict batch, 3 ledger rows, all `holds`, overall `clean verdict stands`, zero re-opens. Related-acquittal mode did not apply (it requires at least one surviving candidate in the same batch; there were none). |
| Observations | Did not fire | §3's closing paragraph and §10 note 6: no candidate's sole failing gate was "meaningful/proven consequence" in a way I judged worth the observation cap's decisive-evidence bar; the verifier's optional observation aside also returned none. |
| Fix-sufficiency check on a concurrency/invariant candidate | Did not fire | Not applicable — that check (`references/verifier.md`, "For every confirmed kind=concurrency or kind=invariant candidate") only runs on a *confirmed* candidate from a candidate-mode batch. Both `concurrency`-kind rows here were dropped in primary falsification before ever becoming survivors, so verification ran under the shallower clean-verdict task instead (still full 5-step attack depth per their kind, just not the bug-class rule-level/interleaving-enumeration check, which is reserved for a `confirmed` verdict on a live candidate). |
| Follow-up verifier round | Did not fire | Zero re-opens from the clean-verdict batch (§4), so no record newly reached render eligibility and the one permitted follow-up batch was not used. |
| Deferral handling | Considered, none found | §10 note 2: both prior-review threads examined against re-review.md's/rubric gate 6's deferral language ("we can fix this during the API review," etc.); neither thread uses deferral language — both are closed, answered discussions with an explicit non-blocking sign-off, so neither was carried forward as an open item. |
| Retrospective mode | **Fired** | Packet §1 (`merged=true`, posting identity `kamui` never authored or reviewed this PR) triggers SKILL.md step 1's retrospective-review path; the payload (`/tmp/holdout/reports/b/v5b-seed3-payload.md`) carries the mandatory `**Mode:** Retrospective review of merged pull request; publication disabled.` line, and step 6 was followed through to "render instead and stop" rather than any external write. |

## 8. History discipline

I did not read any history beyond the pinned head `cb622973cd2c65dd2752c49d0520f2a3894b2d91`. This is both a directive (packet run condition 3) and a physical constraint of the clone (nothing newer than `cb622973c` is reachable in the mirror at all). Exact history-touching commands I ran, all confined to the pinned range or older:

- `git log --oneline -3 main` — 3 commits at and before the merge-base (`1462fd5`, `b96f998`, `fb42781`); older than the merge-base, not "beyond the head."
- `git log --oneline -10 review-head` — the 7 PR commits plus 3 pre-merge-base commits; `review-head` **is** the pinned head, so this lists nothing newer than it.
- The one `review_context.py` run's own `## history` section (§5) — its designed output lists, per changed file, the commits immediately **before** the merge-base (e.g. `raft.go: d09d941 2023-10-10 ...`), which is the script's normal pre-merge-base history feature, not a manual read past the head.
- The verifier sub-agent independently ran `git log --oneline main..review-head`, `git show --stat cb622973c...`, and `git log -p --follow -- testing.go`, and self-reported (§4, "Sandbox/tooling confirmation") that every inspected commit is an ancestor of, or equal to, `review-head`, with no `git fetch`/`git pull` and no command past the pinned head.

No `git fetch`, `git pull`, `gh`, or `curl` was run by me or by the verifier at any point.

## 9. Sandbox disclosure

Paths I read, all inside the sandbox the dispatch and packet define:

- `/tmp/holdout/dispatch/b/v5b-seed3.md` (my own dispatch)
- `/tmp/holdout/skills/v5b/SKILL.md`, `/tmp/holdout/skills/v5b/references/{review-rubric.md,output-contract.md,re-review.md,verifier.md}`, `/tmp/holdout/skills/v5b/scripts/{review_context.py,context_fingerprint.py,validate_review.py}` (help text/schema only for the latter two; ran them, did not read `test_context_fingerprint.py`, `DESIGN.md`, `THIRD_PARTY_NOTICES.md`, `licenses/`, or `agents/` — not named by SKILL.md as required reading)
- `/tmp/holdout/packets/b/packet.md` (my own target's packet)
- `/tmp/holdout/runs/b/v5b-seed3/**` (my own clone, read-only git operations only)
- `/tmp/holdout/work/b/v5b-seed3/**` (my own scratch/work directory, files I created)
- `/tmp/holdout/reports/b/v5b-seed3-run.md` and `/tmp/holdout/reports/b/v5b-seed3-payload.md` (my own report and payload, while writing them)

I did not read any other run's clone (`/tmp/holdout/runs/**` other than `b/v5b-seed3`), any other target's packet, any other cell's dispatch or report/payload, or anything outside `/tmp/holdout/` and the working directory tools operate from. The verifier sub-agent self-reported (§4) that it stayed within `/tmp/holdout/runs/b/v5b-seed3` and `/tmp/holdout/skills/v5b/references/verifier.md` only, and read nothing under `/tmp/holdout/reports/`, `/tmp/holdout/work/`, `/tmp/holdout/dispatch/`, or `/tmp/holdout/packets/`. No path outside the sandbox was read by either of us.

## 10. Notes

Judgment calls on ambiguity in the skill's contract, and what I treated as guidance:

1. **No linked issue.** SKILL.md step 1 says "Use every clearly relevant issue. With none, review the code and state that issue alignment was unavailable; require an issue only when the repository workflow does." I read this as: judge `Issue fit` against the pull request's own stated problem/fix text (packet §3) rather than leaving `Issue fit` empty, since that text is the only available statement of intent and the output-contract's summary format still expects an `Issue fit` line. I did not treat this as requiring a formal issue-tracker fetch (none exists — `docs/agents/issue-tracker.md` is absent, confirmed by direct probe).
2. **Prior-review threads vs. deferral.** Rubric gate 6 treats an *explicit* deferral ("we can fix this during the API review," "good enough for now") as evidence a question is open. Packet §6's two threads (the `leaderLoop`/`continue` structural discussion and the reproduction-frequency question) are both closed, answered discussions with the reviewer explicitly saying "not blocking" — I judged neither uses deferral language, so I did not carry either forward as an open question, and I did not treat the packet's "already fixed in the reviewed head" instruction as applying here either (it wasn't fixed later — it was settled by discussion, a distinct case the packet doesn't explicitly name, so I applied gate 6's plain "maintainer approval establishes acceptance of what the record explicitly addresses" rule instead).
3. **`.github/CODEOWNERS` classification.** Present at the merge-base (packet §7), but it names none of the three guidance categories (`AGENTS.md`/`CLAUDE.md`/`CONTEXT.md`) and is an ownership-routing file, not a coding/behavioral standard, so I excluded it from both the `guidance` digest field and the review-rubric's "Repository rules" analysis. Recorded here as the packet's §7 footnote directed ("record how you classified it").
4. **No-execution constraint is not a coverage gap.** The packet's run condition 2 forbids any `go`/build/test/lint execution. None of my three candidates' dispositions depended on a fact only execution could settle (all three were resolved by static structural tracing of `select`/goroutine semantics and symbol resolution), so I did not open a `Coverage gaps` section in the payload; I disclose the constraint itself here instead, as the packet directs ("say so where a claim would ordinarily be settled by running something").
5. **Kind classification for dropped candidates.** The rubric does not force a specific `kind` on a candidate that never survives; I classified both leadership-transfer candidates as `concurrency` (rather than plain `bug`) because their claims are fundamentally about cross-goroutine timing, which routed them through the clean-verdict task's full 5-step attack depth rather than the shallower one-citation check — a deliberately conservative choice given this diff touches a failover-critical mechanism.
6. **Withheld observation.** I considered publishing the `getinstate-poll-return-window` fact as one of the up-to-three `Observations`, but judged it too close to tautological (true of nearly any poll-then-return pattern) to meet the "decisive" bar the output contract sets for that capped, summary-only channel, and recorded it only in the private ledger (§3) instead.

**Wall clock:** 2026-09-04T20:08:05Z start → 2026-09-04T20:15:24Z last-write-before-this-note (report finalized immediately after), all UTC per `date -u`. Total elapsed: approximately 7 minutes for the full run (context-script execution, primary falsification of 3 candidates, one foreground verifier dispatch and wait, digest computation, payload validation/render, and both files written to completion).
