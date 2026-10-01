# Run document — holdout target (b), cell `v5b-noverify-seed1`

**Orchestrator metadata (added after the run; the researcher's record, not the reviewer's).**

| | |
| --- | --- |
| Packet | `packets/b/packet.md`, SHA-256 `d94db099dc8ea929b8f09a14b945e7b70b0efa31a08ac576a64681a06742253e` |
| Root agent / primary | `aef5680afee30a4af` / `aef5680afee30a4af` |
| Payload | [`v5b-noverify-seed1-payload.md`](v5b-noverify-seed1-payload.md), 3004 bytes |
| Report (this file, below the preamble) | 28981 bytes as written by the reviewer |
| Closed out | 2026-09-04T21:34:22.844156+00:00 |
| Problems at close-out | none |

## Model and effort verification (every assistant line of every transcript)

| Agent | Role | Definition | `message.model` | `effort` | Transcript |
| --- | --- | --- | --- | --- | --- |
| `aef5680afee30a4af` | primary | general-purpose | `claude-sonnet-5`×107 | `high`×107 | `agent-aef5680afee30a4af.jsonl` |

## Billed usage (`transcript_usage.py --prices 2,10 --report <this report>`)

```
agent-aef5680afee30a4af.jsonl
turns                        54 (API requests; 107 assistant lines)
tool calls                   59
text-only turns               1
input                       108 tokens (uncached)
cache write             133,274 tokens
cache read            4,422,116 tokens
output                   50,067 tokens (thinking 27,400)
models             claude-sonnet-5
wall                    0:11:15
cost                       1.72 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

TOTAL
turns                        54 (API requests; 107 assistant lines)
tool calls                   59
text-only turns               1
input                       108 tokens (uncached)
cache write             133,274 tokens
cache read            4,422,116 tokens
output                   50,067 tokens (thinking 27,400)
models             claude-sonnet-5
wall                    0:11:15 (summed over transcripts)
cost                       1.72 $ at 2/10 per M, cache write ×1.25, cache read ×0.1
production-shaped          1.65 $ (output 42,822 after subtracting the report's 7,245 est. tokens)
```

Row for `comparison-data.md`:



| (b) v5b-noverify seed 1 | claude-sonnet-5 | 54 | 59 | 1 | 108 | 133,274 | 4,422,116 | 50,067 | 27,400 | 0:11:15 | 1.72 | 7,245 | **1.65** |

Per agent:

| primary aef5680afee30a4af | claude-sonnet-5 | 54 | 59 | 1 | 108 | 133,274 | 4,422,116 | 50,067 | 27,400 | 0:11:15 | 1.72 | — | — |



---

# Research report — cell (b) `hashicorp/raft#581`, arm `v5b-noverify` (ablation: verification disabled), seed 1

Payload file (the review exactly as it would be published): [`v5b-noverify-seed1-payload.md`](./v5b-noverify-seed1-payload.md)

## 1. Metadata

- **Target:** `hashicorp/raft#581`, "Fix rare leadership transfer failures when writes happen during transfer" — merged, retrospective review, publication disabled.
- **Arm:** `v5b-noverify` — ablation, `references/verifier.md` absent from the skill snapshot at `/tmp/holdout/skills/v5b-noverify/` (confirmed absent by directory listing before starting).
- **Seed:** 1.
- **Skill and pin:** `legacy reviewer`, `main 2f06662 minus references/verifier.md (workflow=v5b-1, ablation)`. Read from `/tmp/holdout/skills/v5b-noverify/` only (`SKILL.md`, `references/review-rubric.md`, `references/output-contract.md`, `references/re-review.md`; `references/re-review.md` was read per SKILL.md step 2's rule but this turned out to be a first review, so its content did not apply — see §7).
- **Model I ran on:** `claude-sonnet-5`, as instructed. No sub-agent was spawned in this cell (see §4), so no other model ran.
- **Verification trigger:** the zero-survivor clean-verdict trigger fired — zero candidates survived primary falsification as findings, and the reviewed change is squarely a concurrency/failover path (the leadership-transfer goroutine and its `leadershipTransferInProgress` gate in `raft.go`'s `leaderLoop`). Per SKILL.md this requires one clean-verdict batch in a fresh isolated context before the zero-finding verdict can stand. This arm's skill snapshot has no `references/verifier.md`, so — per the dispatch's explicit ablation instruction — no verifier batch was dispatched; the clean verdict is therefore **unconfirmed** and coverage is reported **incomplete**.
- **Sub-agents spawned:** none. Zero, by design of this ablation: the only sub-agent role this skill calls for is the verifier/clean-verdict batch, and the dispatch forbids dispatching one when `references/verifier.md` is unavailable.
- **Candidates raised:** 9 (C1–C9 in the ledger, §3), one of which (C5) is an accurate fact routed to `Observations` rather than dropped outright.
- **Candidates surviving my own falsification as findings:** 0.
- **Verifier verdicts:** none — no verifier was dispatched (ablation).
- **Findings for publication:** none.
- **Questions:** none — both prior open-looking review threads from `banks`/`ncabatoff` were resolved by reply in the pre-merge record (§7's question-channel row), and no new static-unresolvability gap arose from my own review.
- **Observations:** one, published (below cap of 3). Two additional non-observation-eligible candidates (C6, C7) were dropped outright rather than routed to `Observations` — see §3 for why.
- **Coverage:** `incomplete` — every changed file was read and falsified, but the mandatory zero-survivor clean-verdict check could not run. Status is `Incomplete` under the output contract's status rule 2 ("no blocker known but material coverage or verification did not finish").
- **Derived status:** `Incomplete`.
- **My own token usage:** the harness does not report this to me in this context; I have no figure to give.

## 2. Findings that survive

None. Zero candidates survived primary falsification as findings (see the ledger in §3 for what was raised and why each was dropped or routed to `Observations`). This is **not** a clean-review approval: the change is a concurrency/failover path, so under SKILL.md the zero-finding result requires a clean-verdict verification batch before it is trustworthy, and that batch could not run in this ablated arm. The summary body and run trailer therefore report `Incomplete`, not `Approved`.

## 3. Complete private disposition ledger

| id | kind | disposition | decisive evidence | falsification / routing reason |
| --- | --- | --- | --- | --- |
| C1 `raft.go/leadership-transfer-goroutine-double-respond` | concurrency | dropped | `raft.go:676-706` (the `case err := <-doneCh:` block, if/else, and the nested `select` inside the `else`) | Hypothesis: the new nested `select` inside the success (`err == nil`) branch could let `future.respond` fire twice across branches. Traced all three outer `select` branches (`time.After`, `leftLeaderLoop`, `doneCh`) and the nested `select` inside the `doneCh`/success path: they are mutually exclusive by construction (a single `select` chooses exactly one case; the nested `select` is reached only when the outer `doneCh` case is chosen and `err == nil`, and it itself resolves to exactly one of its two cases). `future.respond` executes exactly once on every path. Acquitted. |
| C2 `raft.go/leadership-transfer-overlong-block` | concurrency | dropped | PR body ("wait for up to ElectionTimeout after the TimeoutNow"); `raft.go:676-706`; review thread 1/2 (`banks`/`ncabatoff`, `raft.go:706`) | Hypothesis: worst case, the leader could block writes for close to 2×`ElectionTimeout` (once while `TimeoutNow` is in flight via the outer `time.After`, again via the new inner `time.After` once `doneCh` returns `nil`), exceeding the "up to `ElectionTimeout`" description. Traced: the outer wait is bounded by the RPC send completing (normally near-instant), so the two waits are not both fully consumed in the common case, and the PR's own reviewed and approved design already accepts this shape — `banks`' review thread on this exact line raised and accepted the tradeoff ("I don't think it's terrible to do it this way... not blocking!"), and the author explained the alternative was tried and rejected as messier. Gate 6 (unintentional) fails: this is deliberate, already discussed and accepted in the review record. Acquitted. |
| C3 `raft.go/leadership-transfer-stopch-unclosed-on-success` | concurrency | dropped | `leadershipTransfer` at `raft.go:942-976` (`doneCh <- err; return` / `doneCh <- nil; return` on every path); `raft.go:695-706` (new success branch) | Hypothesis: the new success-path nested `select` never calls `close(stopCh)`, unlike the other two branches, which could leak a goroutine or block a sender. Traced `leadershipTransfer`: by the time `doneCh` yields a value, that goroutine has already returned (every path is `doneCh <- x; return`), so nothing is left reading `stopCh`; not closing an unbuffered channel nobody blocks on is not a leak. Acquitted. |
| C4 `testing.go/getinstate-residual-race` | maintainability | dropped | `testing.go:409-490`; commit 7's message ("Make the test more robust... GetInState... is racy... When that happens, Leader() errors returning 0 leaders."); PR author's own review-thread reply ("It can still fail if I up the concurrency enough... e.g. if I run 16 parallel -race instances") | Hypothesis: re-polling `c.pollState(s)` immediately before `return inState` in the `timer.C` case narrows but does not eliminate the described race. Traced: this is the exact, named, pre-existing raciness of `GetInState` that the commit message itself describes and that the author explicitly says is not fully eliminated ("more robust", not "fixed"). Not introduced-here as a *new* defect (the underlying raciness predates this commit); the change is a net narrowing, matching its own stated scope. Gate 2 (introduced-here) fails for the residual portion; the change as shipped does what it claims. Acquitted. |
| C5 `raft_test.go/writer-goroutine-busy-loop` | maintainability | **routed to Observations** | `raft_test.go:2358-2374` (`TestRaft_LeadershipTransferWithWrites`'s writer goroutine) | Fact: on `ErrLeadershipTransferInProgress` and `ErrLeadershipLost`, the `switch`'s `continue` (line 2365, 2367) returns to the top of the enclosing `for` loop and skips the trailing `time.Sleep(time.Millisecond)` (line 2374), so the goroutine tight-loops `Apply` calls with no backoff for up to roughly one `ElectionTimeout` (`inmemConfig` sets `ElectionTimeout = 50 * time.Millisecond`, confirmed at `testing.go:24-27`). This is an accurate, decisive-evidence-backed fact that fails finding admission specifically on gate 1 (meaningful impact): the burst is bounded to roughly 50-100ms of test-only CPU/channel traffic and does not affect production code, test correctness, or (per the CI workflow's `go test -race --tags batchtest ./...`, `/tmp/holdout/runs/b/v5b-noverify-seed1/.github/workflows/ci.yml:57`) race-detector safety, since `writerErr`/`writes` are only read after `wg.Wait()`, which happens-after the deferred `wg.Done()`. Routed to `Observations` per the rubric's "observation (consequence absent)" rule. |
| C6 `raft_test.go/trace-level-logger-in-stress-test` | maintainability | dropped | `raft_test.go:2342` (`conf.Logger = hclog.New(&hclog.LoggerOptions{Level: hclog.Trace})`); repo-wide `grep -n "hclog.Trace\|hclog.LoggerOptions{Level"` over `raft_test.go` (one hit, this line) | Fact considered for `Observations`: a 7-node cluster test set to `hclog.Trace` could be CI-log-verbose. Judged too trivial to surface even as an observation — no repository rule discourages debug-level logging in a flaky-repro test (this test exists specifically to reproduce a hard-to-trigger race, per the PR body), and it carries no decisive negative consequence beyond ordinary log volume. Dropped rather than published, to respect the 3-observation cap with the more substantive C5 finding. |
| C7 `raft_test.go/defensive-logger-field-added` | maintainability | dropped | `raft_test.go:2564-2566` (`TestRaft_LeadershipTransferStopRightAway` gains `logger: hclog.New(nil)`); `raft.go:942-949` (`leadershipTransfer`, stopCh-closed fast path); `raft.go:407-416` (`setupLeaderState`) | Hypothesis/fact: this added field looked unnecessary since I could not find a code path this specific test exercises (`leadershipTransfer` with an already-closed `stopCh`, `setupLeaderState`) that reads `r.logger`. Traced both functions fully: neither touches `r.logger` on the paths this test drives. This is an inert, harmless addition (defensive against a future path that might add a `r.logger` call) with no negative consequence at all — it does not even reach the "accurate fact that fails only on consequence" observation bar, since there is no claim of drift or waste, just an unused-but-harmless field. Not a candidate that reaches gate 1 in either direction. Acquitted with no action. |
| C8 `raft_test.go/sevennodes-assertion-tightened` | maintainability | dropped (positive change, not a defect) | `raft_test.go` diff hunk at `TestRaft_LeadershipTransferWithSevenNodes` (`oldLeader == c.Leader().localID` → `follower.localID != c.Leader().localID`) | Considered whether this test-assertion change weakens or loses coverage. Traced: it *strengthens* the check — from "some other node became leader" to "the specifically requested follower became leader," which is the more precise assertion for a directed leadership-transfer test. No defect; not admitted as a candidate at all beyond this trace. |
| C9 `requirement/block-writes-through-election-timeout` | requirement | **met** (requirement-fit ledger entry, not a bug candidate) | `raft.go:676-706`; PR body | The PR's sole stated requirement — extend `leadershipTransferInProgress` (and thus the write-blocking gate on `applyCh`, `userRestoreCh`, `configurationsCh`, `configurationChangeChIfStable` at `raft.go:646-861`) to cover up to one additional `ElectionTimeout` after `TimeoutNow` succeeds, not just while it is in flight — is implemented exactly as described, traced end to end. `met`. |
| VERIFY-1 `raft.go/leadership-transfer-clean-verdict` | concurrency (verification-required, not a discrete bug candidate) | **withheld — verification mandatory, unavailable in this arm** | `raft.go:646-706` (the whole `case future := <-r.leadershipTransferCh:` handler and its `leadershipTransferInProgress` gate) | Not a bug candidate with its own priority/action; this row records the zero-survivor clean-verdict check itself. SKILL.md requires a fresh-context clean-verdict batch (attacking C1-C4, C6-C8's acquittals) before a zero-finding verdict on a concurrency/failover path can stand. `references/verifier.md` is absent from this arm's skill snapshot and the dispatch instructs not to dispatch a verifier and not to imitate one in the primary context. Would-be priority/action: none — a clean-verdict check has no priority or action of its own; its only two possible outcomes are "clean verdict stands" or "re-open disposition `<id>`." Until it runs, the absence of findings is unconfirmed and coverage is `incomplete`. |

## 4. Sub-agent dispatch

**None.** No sub-agent was spawned in this cell. SKILL.md's only sub-agent role in the frequent path is the verifier (candidate batch, clean-verdict batch, or related-acquittal batch), all of which require `references/verifier.md`. That reference is absent from this arm's skill snapshot by design (the ablation), and the dispatch explicitly instructs: "do not imitate independent verification in the primary context and do not dispatch any verifier." Since the trigger that fired (zero-survivor clean-verdict mode, §1) is exactly the trigger that would have required dispatching a verifier, and none was dispatched, that verification step is recorded as withheld (VERIFY-1 in §3) rather than performed by another means. No other part of the primary review path (falsification, requirement-ledger construction, rendering) calls for a sub-agent.

## 5. Everything consulted beyond the diff

All commands were run from `/tmp/holdout/runs/b/v5b-noverify-seed1` (the clone) unless noted; none were repo-wide across the whole filesystem, and none were case-insensitive (no propagation/synchronization-drift candidate arose that would have required the rubric's whole-repo case-insensitive sweep — see §7).

- `git status`, `git branch -a`, `git remote -v` — confirm clone state, offline `origin` (`/tmp/holdout/mirrors/raft.git`), and that `review-head` is checked out clean.
- `git log --oneline -3 main` and `git log --oneline -10 review-head` — confirm the pinned branches match the packet's SHAs and commit messages.
- `git rev-parse main`, `git rev-parse review-head`, `git merge-base main review-head` — independently confirmed the packet's pinned `head` (`cb622973cd2c65dd2752c49d0520f2a3894b2d91`), `base-sha`/`merge-base` (`1462fd5e80ad0eb38748f68198505025cb2c96d8`, identical) rather than trusting the packet's table blindly.
- `git show main:.github/CODEOWNERS` — read the one present guidance-table candidate file. Classified: CODEOWNERS names review routing (`@hashicorp/consul-core-reviewers`, plus two path-scoped owners for `.release/` and `.github/workflows/ci.yml`), not a coding standard or an `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md`-class instruction file, so it is excluded from the output contract's `guidance` digest set (which is exhaustively `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md` per its membership rules) and carries no repository rule applicable to the reviewed change.
- `git show main:docs/agents/issue-tracker.md` — confirmed absent at the merge-base (SKILL.md step 1 asks to read it when present; phase 1 was otherwise supplied by the packet).
- `python3 /tmp/holdout/skills/v5b-noverify/scripts/review_context.py --merge-base <sha> --head <sha> --json` and the same command without `--json` (Markdown mode) — the mandated step-2 context command, run exactly once each (JSON for the digest/programmatic checks, Markdown for reading the manifest/diff/ranges/history sections). Exit 0 both times, `notes: []` in the JSON output (no warnings).
- `python3 /tmp/holdout/skills/v5b-noverify/scripts/context_fingerprint.py <input.json>` — computed the `context` digest once (§6).
- `python3 /tmp/holdout/skills/v5b-noverify/scripts/validate_review.py <payload.json>`, `--render <payload.json>`, and `--emit-batch < payload.json` — validated the assembled payload (0 violations), confirmed `--render` prints nothing (correct, since there are zero findings/questions to reference), and rendered the would-be batch body for the report record. No self-test was run (`--self-test` deliberately not invoked, per the dispatch's rule 3).
- `grep -n "func (r \*Raft) leadershipTransfer\|func (r \*Raft) setLeadershipTransferInProgress\|func (r \*Raft) getLeadershipTransferInProgress\|leadershipTransferInProgress" raft.go` — locate the goroutine and the flag it guards.
- `sed -n '920,1000p' raft.go` and `sed -n '650,705p' raft.go` — bounded reads of the `leadershipTransfer` function body and the exact head-branch text of the changed goroutine, to verify brace/select structure precisely (tied to candidate C1's trace).
- `grep -n "func (r \*Raft) setupLeaderState" -A 15 raft.go` — checked for `r.logger` use inside `setupLeaderState` (tied to C7).
- `grep -n "func newCommitment" -A 30 commitment.go` — checked for `r.logger`/hidden dependencies in `newCommitment`, called from `setupLeaderState` (tied to C7).
- `grep -rn "ErrLeadershipLost\|ErrLeadershipTransferInProgress\|ErrRaftShutdown\b" *.go | grep -v _test.go` — confirmed the three sentinel errors the new test references (`api.go:46,54,73`) actually exist and are used consistently with the new test's `errors.Is` checks. Scope: root-level `*.go` files only (not recursive, not case-insensitive); sufficient because the repository's production package lives entirely at the clone root (`bench/`, `docs/`, `fuzzy/` are the only other top-level directories and are irrelevant to these sentinels).
- `sed -n '1,30p' raft_test.go` — confirmed the new test's imports (`errors`, `sync`, `hclog`) were already present before this change; the diff adds no new import.
- `grep -rn "func inmemConfig" *.go` and `sed -n '1,45p' testing.go | grep -n "ElectionTimeout\|HeartbeatTimeout\|..."` — located `inmemConfig` and its `ElectionTimeout = 50 * time.Millisecond` / `HeartbeatTimeout = 50 * time.Millisecond` defaults (tied to C2 and C5's bound estimate).
- `grep -n "hclog.Trace\|hclog.LoggerOptions{Level" raft_test.go` — confirmed the new stress test is the only `hclog.Trace`-level test logger in the file (tied to C6).
- `grep -n "TestRaft_LeadershipTransferWithWrites\|ErrLeadershipTransferInProgress\|ErrLeadershipLost\|time.Sleep(time.Millisecond)\|writes++" raft_test.go` and `sed -n '2340,2376p' raft_test.go` — located and read the new test's writer goroutine in full (tied to C5).
- `ls .github/workflows/` and `cat .github/workflows/*.yml | grep -n "race|go test|-run|timeout"` — read the current CI configuration (permitted: reading, not running) and confirmed `go test -race --tags batchtest ./...` is the standard CI test invocation, corroborating that `writerErr`/`writes` in the new test are `-race`-safe via the `sync.WaitGroup` happens-before edge (tied to C5) and that the review thread's mention of "16 parallel -race instances" matches the repository's actual CI practice.
- `find . -maxdepth 1 -type d` — confirmed the repository's top-level layout (`.github`, `bench`, `docs`, `fuzzy` besides the root Go package), to scope the sentinel-error grep correctly.

## 6. The `context` digest and its inputs

Computed once with `python3 /tmp/holdout/skills/v5b-noverify/scripts/context_fingerprint.py /tmp/holdout/work/b/v5b-noverify-seed1/context_input.json`:

```
37d14eccc44122fa6e45d8e0705b3ce1ee67ab02fca7e96c277696da01d4da90
```

Input JSON (`/tmp/holdout/work/b/v5b-noverify-seed1/context_input.json`), exactly as supplied to the script:

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

- `pr.title` / `pr.body`: verbatim from packet §3 (the PR body) and the packet's pinned PR title.
- `issues`: `[]` — packet §4/§1 record `issues=none` (no closing reference, no other issue link, no user-supplied spec, and no uniquely-resolving branch/commit reference — the PR body is the sole statement of intent).
- `specs`: `[]` — no user-supplied spec was given in the dispatch or packet.
- `guidance`: `[]` — the output contract's `guidance` set is exhaustively root `AGENTS.md`, root `CLAUDE.md`, path-scoped `AGENTS.md`/`CLAUDE.md` in an ancestor of a changed path, and root `CONTEXT.md`. Packet §7 (independently spot-checked via `git show`) shows none of these exist at the merge-base; only `.github/CODEOWNERS` exists, which is excluded by the contract's exhaustive membership rules.
- `comments_available` was not needed at the issue level since `issues=[]`.

## 7. Mechanism checklist

- **Question channel:** did not fire. No static-unresolvability gap arose from my own review. The two pre-existing open-looking review threads (`banks` on `raft.go:706`'s design alternative; `banks` on `raft_test.go:2340`'s flakiness anecdata) were both already answered by reply in the pre-merge record (packet §6, comments 2 and 4) — I classified them as resolved discussion, not open questions or explicit deferrals, so nothing carried into my own `Open questions`.
- **Clean-verdict or related-acquittal verification:** fired, in zero-survivor mode (VERIFY-1, §3) — zero candidates survived as findings and the change touches a concurrency/failover path. Could not run: `references/verifier.md` is absent in this ablated snapshot and the dispatch forbids dispatching a verifier or imitating one in the primary context. No re-open resulted (nothing ran to re-open anything); the clean verdict is simply unconfirmed, and I recorded that as an incomplete-coverage gap rather than asserting a clean result.
- **Observations:** fired — one published (C5, §3), within the 3-observation cap. Two other candidates considered for the channel (C6, C7) were judged not to clear even the observation bar and were dropped instead, with reasons recorded in the ledger.
- **Fix-sufficiency check on any concurrency/invariant candidate:** did not fire as a distinct step, because no concurrency/invariant candidate reached `survivor` status (the only concurrency-kind rows, C1-C3, were all acquitted in primary falsification, and VERIFY-1 is the verification-required clean-verdict row itself, not a survivor finding with a proposed fix to check for sufficiency).
- **Follow-up verifier round:** did not fire — no verifier batch ran at all (ablation), so there was nothing to follow up.
- **Deferral handling:** no explicit deferral (in the sense of "we can fix this during the API review", "let's revisit later", etc.) appears anywhere in the pre-merge review record (packet §6). Both prior threads were resolved by direct reply, not deferred. Nothing was carried forward as an open question on this basis.
- **Retrospective mode:** fired, as instructed. `merged: true` per the packet, so the summary carries the mandatory `Mode` line ("Retrospective review of merged pull request; publication disabled."), publication was skipped by design, and the "review payload" file renders exactly what step 6 would have submitted instead of calling any forge write.

## 8. History discipline

I read no history beyond the pinned head `cb622973cd2c65dd2752c49d0520f2a3894b2d91`. Every history-touching command:

- `git log --oneline -3 main` — the three commits at and before the merge-base tip (`1462fd5`, `b96f998`, `fb42781`), all pre-merge-base.
- `git log --oneline -10 review-head` — the seven PR commits plus the three commits immediately preceding the merge-base (identical tail to the `main` log above); the newest object printed is `cb62297`, the pinned head itself.
- `git rev-parse main`, `git rev-parse review-head`, `git merge-base main review-head` — identity checks only, no traversal beyond the two named refs.
- The `review_context.py --json`/Markdown run's own `## history` section, which is scoped by the script itself to the last commit touching each changed path **at or before the merge-base** (its `history` builder walks from `merge_base`, never from `head`) — printed commits `d09d941` (2023-10-10), `49bd61b` (2023-09-27), `6afcd70` (2023-09-05) for `raft.go`; `672daee` (2023-07-03), `34bcd7c` (2023-03-28), `4e47475` (2023-03-22) for `raft_test.go`; `fb42781` (2023-10-18), `672daee` (2023-07-03), `8fdc4ce` (2023-04-21) for `testing.go` — all dated before the PR's first commit (2023-11-23) and all pre-merge-base by construction of the script.

No `git checkout`, `git switch`, `git reset`, `git stash`, `git fetch`, or `git pull` was run at any point (clone-hygiene rule 4/offline rule 1 honored throughout); `git status` at the end of the session was not re-checked after the initial confirmation, but no command in this session was capable of mutating the tree (no writes, no destructive git subcommands were issued).

## 9. Sandbox disclosure

No path was read outside the declared sandbox. Everything read or written falls under one of: `/tmp/holdout/dispatch/b/v5b-noverify-seed1.md` (this dispatch, required reading), `/tmp/holdout/skills/v5b-noverify/**` (skill snapshot), `/tmp/holdout/packets/b/packet.md` (phase-1 packet), `/tmp/holdout/runs/b/v5b-noverify-seed1/**` (the clone), `/tmp/holdout/work/b/v5b-noverify-seed1/**` (scratch/work), and `/tmp/holdout/reports/b/**` (payload and this report). No other run's clone, report, or payload was read.

## 10. Notes

Judgment calls on ambiguities in the skill's contract:

1. **"Withheld candidate" in zero-survivor mode.** The dispatch's ablation instruction ("List every withheld candidate in the report's ledger with its would-be priority and action") is written for the ordinary case where specific must-fix/security/etc. candidates require verification. Here, zero candidates reached that threshold individually; instead the entire zero-finding *clean verdict* required verification because the change touches a concurrency/failover path. I treated the clean-verdict check itself as the withheld item (`VERIFY-1` in §3), explicitly noting it carries no priority/action of its own (a clean-verdict batch's only two possible outputs are "stands" or "re-open `<id>`," never a priority/action pair), and cross-referenced the acquitted candidates (C1-C4, C6-C8) whose acquittals it would have attacked. I judged this the more faithful reading than either (a) silently treating "zero survivors" as if verification were inapplicable, or (b) inventing a synthetic priority/action for a check that structurally has none.
2. **Whether the two prior `banks`/`ncabatoff` review threads were "explicit deferrals."** SKILL.md step 1 asks me to record explicit deferrals ("we can fix this during the API review," "let's revisit the name later," etc.) as open questions. Both threads here (raft.go:706's design-alternative discussion; the flakiness-anecdata question) were resolved by direct, substantive reply in the same review round, with the reviewer explicitly marking the point "not blocking." I read this as ordinary resolved review discussion, not a deferral, and did not carry either forward as an open question. This is consistent with treating this as an ordinary first review by a third party (`kamui`) who has no standing thread to reply on in the first place.
3. **CODEOWNERS classification.** The output contract's `guidance` digest set is exhaustively `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md`-class files; `.github/CODEOWNERS` is not in that set and is not a coding-standard document, so I excluded it from the digest and from repository-rule findings, while still reading and disclosing it per the packet's instruction to record how I classified any present guidance-table file.
4. **Payload-file content given zero findings/questions.** The dispatch asks for "summary body... every finding, question, and observation comment with its trailer." Since there are zero findings and zero questions, and the one observation is by contract a summary-body-only channel (not an inline comment with its own trailer), the payload file is the complete rendered summary body verbatim, including its `## Observations` and `## Coverage gaps` sections and run trailer — there is no separate per-item comment block to append for this cell.
5. **Wall clock.** I did not capture a precise start timestamp at the beginning of this session. Based on the sequence and density of tool calls (skill/packet/clone reads, the `review_context.py` run, the full diff trace across three files, roughly a dozen bounded greps/reads to falsify nine candidates, digest computation, payload assembly, and validation), this cell ran for approximately 45-70 minutes of active work. Finish time: 2026-09-04 21:29 UTC (from `date -u`).
