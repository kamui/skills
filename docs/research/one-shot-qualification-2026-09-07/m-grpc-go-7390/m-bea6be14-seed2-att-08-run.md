# Research report — target (m) grpc/grpc-go#7390, cell m-bea6be14-seed2, attempt att-08

## 1. Metadata

- **Target:** `grpc/grpc-go#7390` — "grpc: hold ac.mu while calling resetTransport to prevent concurrent connection attempts", merged 2024-07-09T20:27:27Z.
- **Cell / attempt:** `m-bea6be14-seed2` / `att-08`.
- **Skill snapshot:** `/tmp/qual137/snapshots/bea6be14/skills/code-review-publish/` (`SKILL.md` + `references/review-rubric.md`, `references/output-contract.md`, `references/verifier.md`, `references/verifier-concurrency.md`; `references/re-review.md` and `references/conformance.md` were not loaded — neither branch condition fired, see §7 below).
- **Validator's `workflow` identifier:** `v5b-10` (constant `WORKFLOW` in `scripts/validate_review.py`).
- **Model I (the primary reviewer) ran on:** `claude-sonnet-5`, invoked in-context (no separate Agent dispatch for the primary review itself — the task specifies the primary review is done directly in this context, never delegated).
- **Sub-agents spawned:** exactly one, for the mandatory verification step (see §2/§4 below): role = independent clean-verdict verifier, count = 1, `subagent_type: "general-purpose"`, `model: "sonnet"` (explicit), `run_in_background: false`.
- **Verification trigger that fired:** SKILL.md step 3, *Zero-survivor mode*: "when zero candidates survive *as findings* — a candidate routed to `Observations` is not a survivor — and the changed behavior touches a concurrency or failover path, a data-integrity surface, or a security or authorization boundary, run one clean-verdict batch instead of a candidate batch." Zero candidates survived as findings (both raised candidates were falsified/dropped by the primary reviewer — see §3), and the changed behavior is squarely a concurrency path (mutex-hold-through-a-call/goroutine-handoff around `addrConn`'s connection-attempt state machine), so this sentence fired the clean-verdict batch.
- **Candidates raised:** 2 (`clientconn/updateaddrs-gracefulclose-lock-handoff`, kind `concurrency`; `clientconn/resettransportandunlock-doc-unconditionally`, kind `maintainability`).
- **Candidates surviving primary falsification:** 0.
- **Verifier verdicts:** see §4 — clean-verdict batch returned `clean verdict stands`.
- **Findings for publication:** 0.
- **Questions:** 0.
- **Observations:** 1 (published; 0 unpublished/capped).
- **Coverage:** complete (single changed file, fully reviewed, no gaps; risk-directed concurrency check evidence-backed by code trace and focused test execution).
- **Derived status:** `Approved (advisory)` — 0 unsettled must-fix findings, no open question, coverage complete, event `COMMENT` (posting identity `kamui` did not author the PR and holds no gating authorization; the target is additionally merged, so publication is disabled regardless — see Mode line).
- **Token usage:** the harness available to me in this session does not report my own token consumption anywhere I can read it; I have no figure to give here (stated per instruction, not omitted).

## 2. Context digest and its inputs

Computed once, per `SKILL.md` step 3 / output-contract.md, from the reconstructed forge packet (see §9 on how that packet was produced offline):

```
python3 scripts/context_fingerprint.py --packet packet.json -   (stdin: "{}", i.e. no specs, no guidance)
→ f0155084ea615627d1b844b4677bc814d2838e1cc2d664afaa658b3c115356dd
```

Inputs that fed it (via `--packet packet.json`'s `fingerprint` section, which is exactly `forge_packet.py normalize`'s output on the reconstructed root page):

- `pr.title`: "grpc: hold ac.mu while calling resetTransport to prevent concurrent connection attempts"
- `pr.body`: the pull-request body verbatim from packet.md §3 (mutex/resetTransport description, `Tested` section, `Fixes:` line, `RELEASE NOTES:` line).
- `issues`: one entry, `coordinate: grpc/grpc-go#7365`, `title: "Flaky Test/AuthorityRevive in google.golang.org/grpc/xds/internal/xdsclient/tests"`, `body`: the verbatim CI-log issue body from packet.md §4, `comments`: the 3 verbatim issue comments from packet.md §4 (`arjan-bal`, 2024-07-04T06:03:18Z / T06:19:39Z / T07:02:02Z), `comments_available` omitted (true, since all 3 were obtained), `comments_complete` omitted (true).
- `specs`: `[]` (none supplied).
- `guidance`: `[]` — per packet.md §7, no root or path-scoped `AGENTS.md`/`CLAUDE.md`, and no root `CONTEXT.md`, exist at the merge-base; `CONTRIBUTING.md` exists but is not one of the three digest-eligible categories the output contract's guidance membership rule enumerates, so it is correctly excluded from the digest (see §10, judgment call).

`fullDatabaseId` values used to reconstruct the forge page (reviews, review-thread comments, PR-level comments) are **synthetic sequential placeholders** I generated, because the packet gives verbatim review/comment text and timestamps but not the forge's internal numeric ids (I have no network access to fetch them for real). This is disclosed here because it is a deviation from "recompute the digest from the real fetched packet" — however, it has **zero effect on the digest itself**, because `context_fingerprint.py`'s `--packet` mode only reads `packet["fingerprint"]["pr"]` (title/body) and `packet["fingerprint"]["issues"]` (coordinate/title/body/comments), and none of those fields depend on review or PR-comment `fullDatabaseId`s — only the issue-comment ids do, and those three ids (`2000000101-103`) are internally consistent placeholders that do not collide or reorder (`context_fingerprint.py` sorts issue comments by `(int(id), canonical_key)`, and the three ascending placeholder ids preserve the same chronological order the verbatim timestamps already establish).

## 3. Manifest and requirement (issue-fit) ledger — persisted before verification

### 3.1 Changed-file manifest

```
M  clientconn.go   +6  −7   (git diff master review-head, merge-base daab56344e612097fd50c46c433de5d9b6013837 == base-sha)
```

One file, one diff hunk pair actually (two hunks in the printed unified diff, at `connect`/`updateAddrs` and at `resetTransport`→`resetTransportAndUnlock`), read in full from `scripts/review_context.py`'s single-call output (`diff coverage: complete (1/1 chunks consumed)`, `manifest`: `M clientconn.go +6 -7 new=no lines=1838`). Disposition: **reviewed** (complete). No other file is touched by the merge-base diff. Coverage: **complete**.

### 3.2 Issue-fit ledger

Built from the explicit closing issue `grpc/grpc-go#7365` (class: issue) and the pull-request title/body (class: pr-title / pr-body), in that source order, before reading the diff for compliance.

| # | Row (source coordinate) | Class | Disposition | Evidence |
|---|---|---|---|---|
| 1 | `issue-7365/root-cause` — "set state to Connecting while the caller of `resetTransport` still holds `ac.mu`, so no other caller can see the pre-connect `Idle` state before the lock is released" (from `arjan-bal`'s issue comment, 2024-07-04T07:02:02Z: "A simple fix it to set the state to connecting while addrConn.connect has the mutex locked... I tried it and it fixed the flakiness.") | acceptance requirement | **met** | `clientconn.go:914-922` (`connect()` now calls `ac.resetTransportAndUnlock()` while still holding `ac.mu`, no intervening `Unlock`), `clientconn.go:990-996` (`updateAddrs()` likewise holds the lock into `go ac.resetTransportAndUnlock()`), `clientconn.go:1234-1262` (`resetTransportAndUnlock` sets `connectivity.Connecting` before its first `ac.mu.Unlock()`) |
| 2 | `pr-body/"This ensures that no concurrent requests are able to start once caller of resetTransport does some validation and calls resetTransport."` | acceptance requirement (pull-request promise of a concrete outcome) | **met** | same evidence as row 1; corroborated by focused-test evidence in §5 (`TestSubConnEmpty`, `TestAuthorityRevive` ×300, both `-race` clean) |
| 3 | `pr-body/"RELEASE NOTES: - client: fix race that could lead to orphaned connections and associated resources."` | acceptance requirement (release-note promise) | **met** | same lock-ordering evidence; mechanism explained by `arjan-bal`'s non-review PR comment (2024-07-09T06:38:44Z): "only one transport is closed when the subConn is updated (`ac.transport`) and the other transport is orphaned" — the fix removes the second concurrent `tryAllAddrs` attempt that produced the second, orphaned transport |
| 4 | `pr-body/"Tested: Verified that Test/AuthorityRevive no longer flakes for 100000 attempts with the change."` | supporting assertion (author's own local measurement, not an acceptance criterion) | **not-verifiable** | Reproducing 100000 attempts is outside this review's offline execution budget (five minutes per focused command). No material decision is gated by this fact — the pull request is already merged (retrospective review) — so no question is published for it, per the rubric's Issue-fit routing ("neither the word 'justification' ... nor the absence of an independent reproduction of a measurement changes the status by itself"). Not contradicted: 300/300 runs of the same test passed under `-race` in this review (§5). |

**Issue fit:** Met.

## 4. Candidate ledger — complete, with every disposition, persisted before the verifier was dispatched

Both candidates below were raised, falsified, and dropped by the primary reviewer *before* any verifier was dispatched. Per SKILL.md's Zero-survivor mode, both rows (the complete disposition ledger) were then sent, unfiltered, to one clean-verdict verifier batch, because the changed behavior touches a concurrency path even though nothing survived as a finding.

| id | kind | disposition | decisive evidence pointer | ruled on by verifier? |
|---|---|---|---|---|
| `clientconn/updateaddrs-gracefulclose-lock-handoff` | concurrency | dropped (refuted, basis `prevented`) | `clientconn.go:983-996`; `test/subconn_test.go:48-126` (`TestSubConnEmpty`) | **yes** — zero-survivor clean-verdict batch, full 5-step attack (kind=concurrency) |
| `clientconn/resettransportandunlock-doc-unconditionally` | maintainability | dropped (gate 6, intentional) | `clientconn.go:1231-1233`; packet.md review-thread 2, comments 10 and 17 (`dfawley`) | **yes** — zero-survivor clean-verdict batch, one-citation check (kind=maintainability) |

Both rows were ruled on because SKILL.md's zero-survivor mode explicitly states the clean-verdict batch is "never filtered by risk surface" and must carry "the complete candidate disposition ledger" — there is no candidate that a rule *exempted* from the verifier's attack in this run.

### 4.1 Candidate `clientconn/updateaddrs-gracefulclose-lock-handoff` (full record)

```yaml
id: clientconn/updateaddrs-gracefulclose-lock-handoff
kind: concurrency
claim: >
  The deferred `ac.transport.GracefulClose()` registered in `addrConn.updateAddrs`
  (clientconn.go:986) self-deadlocks the calling goroutine when it fires, because
  the explicit `ac.mu.Unlock()` that used to precede the goroutine spawn was
  removed, so the lock is still logically held when the deferred call runs; and
  `GracefulClose()` synchronously calls `onClose()` (clientconn.go:1351-1352),
  which does `ac.mu.Lock()`.
trigger: >
  updateAddrs is called while ac.state == Ready (so ac.transport != nil) with a
  new address list that does not contain ac.curAddr, or while ac.state ==
  Connecting with a non-nil ac.transport — both fall through the early-return
  guards into the ac.transport != nil branch (clientconn.go:962-987).
impact: if real, the goroutine that called updateAddrs would hang forever inside
  ac.mu.Lock(), and since ac.mu is never released, every future connect(),
  updateAddrs(), or state read on this addrConn would also hang.
falsification: >
  Refuted, basis `prevented`. Go's `sync.Mutex` is not goroutine-owned: `Unlock()`
  from a different goroutine than the one that called `Lock()` is documented,
  legal Go behavior, and it is exactly the contract `resetTransportAndUnlock`'s
  new doc comment states ("ac.mu must be held by the caller, and this function
  will guarantee it is released") — the caller here is `updateAddrs`, and it
  hands the already-held lock to the goroutine spawned by
  `go ac.resetTransportAndUnlock()` rather than releasing it itself. That spawned
  goroutine's pre-unlock section (clientconn.go:1234-1262) is non-blocking: it is
  either an immediate `if acCtx.Err() != nil { ac.mu.Unlock(); return }`, or a
  few local computations followed by `ac.updateConnectivityState(Connecting, nil)`
  and `ac.mu.Unlock()` — no channel receive, I/O, or external call sits between
  the goroutine starting and its own `Unlock()`. So the deferred `GracefulClose`
  in the original goroutine blocks only briefly (goroutine-scheduling latency),
  not indefinitely: not a deadlock. I additionally traced that every code path
  that registers the `ac.transport != nil` defer *always* falls through to the
  `go ac.resetTransportAndUnlock()` statement with no intervening early return
  (clientconn.go:987-996), so the lock handoff and the defer registration are
  never separated. Empirically confirmed: `test/subconn_test.go`'s
  `TestSubConnEmpty` exercises exactly this branch (Ready with a live transport →
  UpdateAddresses to an empty list, i.e. ac.transport != nil, then re-adds
  addresses and successfully completes another RPC) and passes under `-race` in
  ~10ms; the issue's own regression test, `TestAuthorityRevive`, passes 300/300
  under `-race` (~42s total). Contrast: `tearDown` (clientconn.go:1545-1584)
  handles the identical `GracefulClose`-calls-`onClose`-needs-`ac.mu` hazard by
  explicitly unlocking *before* calling `GracefulClose` (not via defer, and with
  no goroutine handoff) — its own comment ("We have to release the lock before
  the call to GracefulClose/Close here because both of them call onClose(),
  which requires locking ac.mu.") confirms the hazard class is real and known to
  this codebase, but `updateAddrs`'s escape from it (goroutine handoff rather
  than pre-release) is a different, and here verified-safe, mechanism.
evidence:
  - clientconn.go:962-996 (updateAddrs, full changed function)
  - clientconn.go:1234-1263 (resetTransportAndUnlock, full function)
  - clientconn.go:1351-1377 (onClose closure)
  - clientconn.go:1545-1584 (tearDown, contrasting safe pattern)
  - test/subconn_test.go:48-126 (TestSubConnEmpty)
  - xds/internal/xdsclient/tests/authority_test.go:278 (TestAuthorityRevive)
disposition: dropped
verification: independent-confirmed — clean-verdict batch returned `holds`, full 5-step concurrency attack, citing 4 lines the primary ledger did not (see §5)
```

### 4.2 Candidate `clientconn/resettransportandunlock-doc-unconditionally` (full record)

```yaml
id: clientconn/resettransportandunlock-doc-unconditionally
kind: maintainability
claim: >
  The new doc comment "resetTransportAndUnlock unconditionally connects the
  addrConn" (clientconn.go:1231) overclaims: the function has an early-return
  path (acCtx.Err() != nil, clientconn.go:1236-1238) that unlocks and returns
  without connecting.
falsification: >
  Fails gate 6 (unintentional). This exact comment text was authored verbatim by
  reviewer dfawley in review-thread 2, comment 1 (2024-07-08T19:42:18Z, on commit
  6214c9dd1: "Please add a short comment here: ```go // resetTransportAndUnlock
  unconditionally connects the addrConn. // // ac.mu must be held by the caller,
  and this function will guarantee it is released.```"), adopted by the author
  verbatim, and the same thread's final comment from dfawley
  (2024-07-09T20:26:47Z: "I think the name of the function and the comment
  should be sufficient for this.") settles that the maintainer who wrote the
  wording considers it adequate. A maintainer-authored, maintainer-approved
  comment is deliberate, not an oversight the author would want fixed.
evidence:
  - clientconn.go:1231-1233 (comment text at head)
  - packet.md review-thread 2, comment 10 (dfawley, 2024-07-08T19:42:18Z)
  - packet.md review-thread 2, comment 17 (dfawley, 2024-07-09T20:26:47Z)
disposition: dropped
verification: independent-confirmed — clean-verdict batch returned `holds`, one-citation check, with a scope refinement on the falsification's evidence attribution (see §5)
```

*(Nothing in §4 above was edited after the verifier's return except the two `verification:` fields, exactly as promised before dispatch.)*

## 5. Verifier dispatch — exact prompt and verbatim report

**Timing relative to the falsification pass:** SKILL.md's early-dispatch provision (dispatching the verifier batch while remaining `consider` falsifications continue in the background) does **not** apply here: the diff touches a concurrency path, and SKILL.md explicitly excludes concurrency/failover/data-integrity/security surfaces from early dispatch ("do not dispatch early when the diff touches a concurrency or failover path... on those surfaces, dispatch after the complete pass"). Accordingly I dispatched the (sole) verifier batch **only after** the complete diff had been inspected, the manifest finished, and both candidates had completed primary falsification (§3–§4 above were fully written and persisted to this file first, per the run's rule 6 and SKILL.md's "Write the private record once per phase" / "Persist before you verify" instructions). There was no separate early batch and no background continuation to run concurrently with it, since primary falsification was already complete before dispatch.

**Sub-agent:** 1 dispatch, `subagent_type: "general-purpose"`, `model: "sonnet"` (explicit), `run_in_background: false`. Role: independent clean-verdict verifier (fresh, isolated context — no access to this conversation).

### 5.1 Exact prompt given to the verifier

> You are an independent verifier for a code-review skill (`code-review-publish`, `references/verifier.md` and `references/verifier-concurrency.md`). You have NOT seen the primary reviewer's reasoning or narrative — only the record below. Do not search for new findings. Do not write, edit, or publish anything.
>
> ## Your sandbox (binding on you)
>
> - Read-only. You may read inside: the clone at `/tmp/qual137/runs/m-bea6be14-seed2-att-08` (git repo, offline; `origin` is a local path, not github.com — do NOT run `git fetch`/`git pull`/`gh`/`curl`/any network call), the skill snapshot at `/tmp/qual137/snapshots/bea6be14/skills/code-review-publish/` (you already have `verifier.md` and `verifier-concurrency.md` inline below; you do not need to re-read them from disk, but may), and the packet at `/tmp/qual137/packets/m/packet.md`.
> - Do NOT run `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the tree in the clone. If you need to look at a file at a specific SHA, use `git show <sha>:<path>` — never check anything out.
> - History is truncated at the pinned head `76ef33f44a600c3ed1a385979fd1dfbcade3fbb6` on purpose; do not try to reach further history and report explicitly if you run any history command beyond what's needed to read the two pinned revisions below.
> - Focused test execution IS permitted, offline, exactly under these bounds: from the clone root, `GOMODCACHE=/tmp/qual137/gomodcache GOCACHE=/tmp/qual137/gocache GOFLAGS=-mod=mod GOPROXY=off`, five minutes per command, a given package's tests at most once per flag set, nothing added to or changed in the clone, scratch files only under `/tmp/qual137/work/m-bea6be14-seed2-att-08/` if you need any. You are not required to re-run anything the ledger already cites a command/exit-status/output for — treat that as an evidence citation, not the primary's interpretation — but you may re-run or extend it if you think it is decisive for a verdict.
> - Report any path you read outside this sandbox.
> - Render nothing publication-shaped: no trailers, comment markdown, or summary sections. Return compact structured verdicts only, as specified below.
>
> ## Mode: clean-verdict (zero-survivor)
>
> Zero candidates survived the primary reviewer's own falsification pass as findings. Because the changed behavior is a concurrency path (a mutex hold spanning a function call and, in one case, a goroutine spawn, inside gRPC-Go's `addrConn` connection-attempt state machine), the reviewer's skill requires one clean-verdict batch that attacks the *acquittals* rather than searching for new findings. Attack each row below using the Clean-verdict task from `verifier.md` (quoted in full below). Do not invent a new claim. Return `holds` or `re-open` for every row, with decisive evidence or the missing settling fact, plus exactly one batch conclusion (`clean verdict stands`, or `disposition <id> does not hold; re-open it` for each row that fails).
>
> ## Pinned coordinates
>
> - Repository: `grpc/grpc-go` (local clone at `/tmp/qual137/runs/m-bea6be14-seed2-att-08`).
> - Base ref: `master`; base SHA / merge-base: `daab56344e612097fd50c46c433de5d9b6013837` (identical — pinned local branch `master`).
> - Head: `76ef33f44a600c3ed1a385979fd1dfbcade3fbb6` (pinned local branch `review-head`, checked out).
> - Diff under review: `clientconn.go` only, +6/−7 lines (`git diff master review-head` inside the clone reproduces it; do not run `git checkout`/`git switch` to look at either revision — use `git show <sha>:clientconn.go` or read the checked-out `review-head` worktree directly for the head).
> - Originating issue: `grpc/grpc-go#7365` ("Flaky Test/AuthorityRevive..."), root cause per the issue thread: `addrConn.connect()`/`addrConn.updateAddrs()` used to release `ac.mu` and let the callee (`resetTransport`) re-acquire it and only then set state `Connecting`, leaving a window where a second caller could see stale `Idle` state and start a second connection attempt (`tryAllAddrs` called twice, an orphaned transport left behind).
> - The pull request (`grpc/grpc-go#7390`) renamed `resetTransport` to `resetTransportAndUnlock` and changed both call sites (`connect()`, `updateAddrs()`) to hold `ac.mu` continuously into the call, so `resetTransportAndUnlock` sets `Connecting` before releasing the lock for the first time.
>
> ## The complete candidate disposition ledger (both rows — attack both, unfiltered)
>
> ### Row 1
>
> ```
> id: clientconn/updateaddrs-gracefulclose-lock-handoff
> kind: concurrency
> claim: The deferred `ac.transport.GracefulClose()` registered in addrConn.updateAddrs
>   (clientconn.go:986, inside `if ac.transport != nil { defer ac.transport.GracefulClose(); ac.transport = nil }`)
>   self-deadlocks the calling goroutine when it fires at function return, because the
>   explicit `ac.mu.Unlock()` that used to precede the `go ac.resetTransport()` spawn was
>   removed by this diff (replaced by `go ac.resetTransportAndUnlock()`, clientconn.go:996,
>   with the lock still logically held), and `GracefulClose()` synchronously calls
>   `onClose()` (the closure defined at clientconn.go:1351-1377, passed to
>   `transport.NewClientTransport` in `createTransport`), which does `ac.mu.Lock()`
>   (clientconn.go:1352) — the same goroutine trying to re-lock a lock it never released.
> disposition: dropped
> falsification (basis: prevented): Go's sync.Mutex is not goroutine-owned; Unlock() from a
>   goroutine other than the one that called Lock() is legal and is exactly what
>   resetTransportAndUnlock's contract documents ("ac.mu must be held by the caller, and
>   this function will guarantee it is released" — clientconn.go:1231-1233). updateAddrs
>   hands the already-held lock to the goroutine spawned by
>   `go ac.resetTransportAndUnlock()` instead of releasing it itself. That spawned
>   goroutine's pre-unlock section (clientconn.go:1234-1245) is non-blocking (either an
>   immediate ctx-err bail-and-unlock, or a few local computations then
>   updateConnectivityState(Connecting) then Unlock — no I/O or channel receive in
>   between), so the deferred GracefulClose in the original goroutine blocks only for
>   goroutine-scheduling latency, not indefinitely. Empirically: test/subconn_test.go's
>   TestSubConnEmpty exercises exactly this branch (Ready with a live transport →
>   UpdateAddresses to an empty list, i.e. ac.transport != nil at clientconn.go:962) and
>   passes under `go test ./test/ -run 'Test/SubConnEmpty' -race` (exit 0, ~10ms,
>   no race reported); the issue's own regression test,
>   `go test ./xds/internal/xdsclient/tests/ -run 'Test/AuthorityRevive$' -race -count=300`,
>   passed 300/300 (exit 0, ~42s, no race reported).
> decisive evidence: clientconn.go:983-996
> ```
>
> ### Row 2
>
> ```
> id: clientconn/resettransportandunlock-doc-unconditionally
> kind: maintainability
> claim: The new doc comment "resetTransportAndUnlock unconditionally connects the
>   addrConn" (clientconn.go:1231) overclaims: the function has an early-return path
>   (`if acCtx.Err() != nil { ac.mu.Unlock(); return }`, clientconn.go:1236-1238) that
>   unlocks and returns without connecting, so it is not truly unconditional.
> disposition: dropped
> falsification (basis: intentional): This exact comment text was authored verbatim by
>   reviewer dfawley in a pull-request review comment (packet.md review-thread 2,
>   comment 10, 2024-07-08T19:42:18Z, on commit 6214c9dd1: "Please add a short comment
>   here: ```go // resetTransportAndUnlock unconditionally connects the addrConn. //
>   // ac.mu must be held by the caller, and this function will guarantee it is
>   released.```"), adopted by the PR author verbatim, and the same thread's final
>   comment from dfawley (packet.md review-thread 2, comment 17, 2024-07-09T20:26:47Z:
>   "I think the name of the function and the comment should be sufficient for this.")
>   is the maintainer who wrote the wording explicitly confirming it is adequate.
> decisive evidence: clientconn.go:1231-1233
> ```
>
> ## Verifier reference — `verifier.md` (verbatim, the sections you need)
>
> ### Isolation
> Run each permitted batch in a genuinely fresh context (this dispatch). The verifier fact-checks supplied records; it is not a second reviewer, cannot search for unrelated findings, and cannot write to the pull request.
>
> ### Clean-verdict task
> Attack each acquittal supplied to you, using its cited code and the narrow surrounding evidence needed to decide whether the disposition holds. Follow this procedure for every row you rule on, to the depth the kind rule below sets; scoped safety rulings always take all five steps:
>
> 1. Restate the row's decisive premise in one sentence — the fact the acquittal depends on.
> 2. State the concrete condition under which that premise would be false.
> 3. Trace the *opposite* branch of every conditional the premise depends on — a failed lookup, a NULL pointer, an error return, an empty list, a timeout, a counter already decremented — through the current code, citing `path:line` for each step.
> 4. Either construct the complete failing state transition from trigger to observable consequence, or cite the specific step that is impossible.
> 5. Re-reading the ledger's own reasoning and agreeing with it is not a verdict. A `holds` ruling on a fully attacked row — including every such row covered by `clean verdict stands` — must cite at least one line the ledger row did not cite.
>
> Attack depth follows the row's `kind`. The five steps apply in full to every row whose `kind` is `bug`, `concurrency`, `invariant`, or `security` (Row 1, above). Every other row — `performance`, `maintainability`, or `requirement` — gets a one-citation check instead unless it asserts safety: read the row's evidence pointer, confirm or contradict its stated fact, and return `holds` or `re-open` without tracing conditionals (Row 2, above).
>
> An `unresolved` row asserts an evidence gap, not safety; not applicable here (neither row's basis is `unresolved`).
>
> Return `holds` or `re-open` for every supplied ledger id with its decisive evidence or named unresolved gap. Also return exactly one batch conclusion:
> - `clean verdict stands` when every disposition survives that procedure; or
> - `disposition <id> does not hold; re-open it` for each supplied ledger row whose stated acquittal is contradicted or unsupported.
>
> Do not search the rest of the pull request for new findings. If an accurate, sub-threshold fact surfaces incidentally, you may return at most one explicitly non-actionable `observation` aside with a decisive evidence pointer and no `should`/`must` language — but do not use this to smuggle in a new finding.
>
> ### Scoped safety rulings
> Every assertion that a row's path is safe, unreachable, handled, or correct is a scoped acquittal, even inside a `holds` verdict. State the path, state/ordering conditions, and exact premise established; apply all five opposite-branch steps of the clean-verdict task to that safety premise, regardless of candidate kind (this applies to Row 1's "prevented" safety claim in particular — attack it fully). A working trace alone cannot establish safety on other branches. Cite the decisive evidence for the asserted scope. If evidence cannot settle the premise, record it as unresolved rather than safe.
>
> ## `verifier-concurrency.md` (verbatim — applies because Row 1's kind is `concurrency`)
>
> Include this reference in the verifier brief only when a supplied candidate's kind is concurrency or invariant. It extends verifier.md's verification task for every such candidate the verifier *re-opens as a live bug* (in clean-verdict mode, this applies if and only if you conclude Row 1 should be `re-open`ed rather than `holds`). It adds no verdict, no batch, and no candidate on its own — it only shapes what you must additionally state if you re-open Row 1.
>
> If you re-open Row 1, additionally:
> 1. State the invariant at the rule level, not the transition level: name which state/fields must stay consistent with which operations, and under which lock that consistency was guaranteed at the merge-base.
> 2. State whether the failing interleaving requires runtime shutdown/teardown/an error path; if so, also ask whether the same rule can fail in steady state, and trace at least one steady-state interleaving to a holds/fails verdict with path:line citations.
> 3. Enumerate sibling interleavings (which concurrent actors touch the shared state) before sibling code paths, citing where each actor reads/writes it.
> 4. Enumerate sibling code paths governed by the rule and state whether the existing fix protects each.
> 5. Widen `change` to the rule level if the existing fix (as merged) covers only one interleaving or path.
>
> ## What to return
>
> For each of the two rows: the row id, your verdict (`holds` or `re-open`), the step-by-step trace you performed (compact, but must include at least one `path:line` citation the ledger row did not already cite, per step 5 of the clean-verdict task), and your basis. Then the one batch conclusion. If you have a single non-actionable observation aside, include it separately, clearly labeled, with a decisive evidence pointer and no `should`/`must` language — otherwise omit that section entirely.

### 5.2 Verbatim report returned by the verifier

> ## Verification Results
>
> ### Row 1 — `clientconn/updateaddrs-gracefulclose-lock-handoff`
>
> **Verdict: holds**
>
> Step-by-step trace (concurrency kind, full 5 steps, including scoped-safety attack on the "prevented" premise):
>
> 1. **Decisive premise**: The pre-unlock section of `resetTransportAndUnlock` (the code the spawned goroutine G2 runs before it calls `ac.mu.Unlock()`) contains no blocking operation, so G1's deferred `GracefulClose()`→`onClose()`→`ac.mu.Lock()` (clientconn.go:1352) waits only for scheduling latency, not indefinitely.
>
> 2. **Condition that would falsify it**: any statement between `acCtx := ac.ctx` (clientconn.go:1235) and the first `ac.mu.Unlock()` (clientconn.go:1238 or 1259) blocks forever, panics without unlocking, or never runs (goroutine starvation/never-scheduled).
>
> 3. **Opposite-branch trace**:
>    - `acCtx.Err() != nil` branch (clientconn.go:1236-1238): immediate `Unlock`+`return` — non-blocking.
>    - `acCtx.Err() == nil` branch: `ac.dopts.bs.Backoff(ac.backoffIdx)` resolves to `internal/backoff/backoff.go:56-75` (`Exponential.Backoff`) — pure arithmetic, no lock, no channel op, no panic path (loop/compare/multiply only).
>    - Nil-pointer opposite branch: `ac.dopts.bs` is a **value type** (`Exponential` struct), defaulted at `dialoptions.go:681` (`bs: internalbackoff.DefaultExponential`) — a value-type method call cannot nil-deref, closing off the "NULL pointer before Unlock" failure mode the clean-verdict task requires checking.
>    - `ac.updateConnectivityState(connectivity.Connecting, nil)` (clientconn.go:1259 call site, defined at clientconn.go:1200-1215): `close(ac.stateChan)` is instantaneous; `ac.acbw.updateState(s, lastErr)` → `balancer_wrapper.go:255-264` calls `acbw.ccb.serializer.Schedule(...)`, which resolves to `internal/grpcsync/callback_serializer.go:64-66` — `cs.callbacks.Put(f)` on a `buffer.Unbounded`, confirmed non-blocking (enqueue-only, no synchronous execution, no bounded-queue backpressure).
>    - Goroutine-starvation opposite branch: `sync.Mutex.Lock()` parks the calling goroutine rather than spinning, so the runtime scheduler is guaranteed to run other runnable goroutines (including G2) even under `GOMAXPROCS=1`; no starvation deadlock is constructible.
>
> 4. **Failing state transition**: none constructible. Every statement in the pre-unlock path is either pure computation, an instantaneous channel close, or an enqueue onto an unbounded, non-blocking buffer. The specific step required for the claim to fail (a block or panic before `ac.mu.Unlock()` in G2) is impossible given the current code.
>
> 5. **New citations beyond the ledger's own**: `internal/backoff/backoff.go:56-75`, `dialoptions.go:681`, `balancer_wrapper.go:255-264`, `internal/grpcsync/callback_serializer.go:64-66`.
>
> Additionally, independently re-ran the ledger's cited regression test (not required, but decisive): `GOMODCACHE=/tmp/qual137/gomodcache GOCACHE=/tmp/qual137/gocache GOFLAGS=-mod=mod GOPROXY=off go test ./test/ -run 'Test/SubConnEmpty' -race -v` → `PASS`, exit 0, ~1.5s, no race detected — corroborates the ledger's citation independently rather than merely trusting it.
>
> Since Row 1 is not being re-opened, `verifier-concurrency.md`'s additional obligations do not apply.
>
> ### Row 2 — `clientconn/resettransportandunlock-doc-unconditionally`
>
> **Verdict: holds** (one-citation check, maintainability kind)
>
> - Confirmed `clientconn.go:1231-1233` verbatim: `// resetTransportAndUnlock unconditionally connects the addrConn.` / `// ac.mu must be held by the caller, and this function will guarantee it is released.`, immediately preceding the function that has the early-return-without-connecting branch at `clientconn.go:1236-1238`. The underlying code fact the finding relies on is real and undisputed.
> - Confirmed the packet.md quotes are accurate: comment 10 (`dfawley`, 2024-07-08T19:42:18Z) proposes this exact wording; comment 17 (`dfawley`, 2024-07-09T20:26:47Z) closes the thread with "I think the name of the function and the comment should be sufficient for this."
> - New citation the ledger didn't use: `git show daab5634:clientconn.go` (pre-PR `resetTransport`) has **no doc comment at all** — the comment is a wholly new addition, and comment 8 in the same review thread (`purnesh42H`, 2024-07-05, `clientconn.go:923`) already discusses the `acCtx.Err()` early-return-without-state-update branch *before* dfawley proposed the "unconditionally" wording three days later — supporting that the wording was chosen with the early-return branch already in view, i.e., intentional rather than an oversight.
>
> Batch conclusion: **clean verdict stands**
>
> Non-actionable observation (does not affect the verdict): comment 17's "sufficient for this" is a reply within the sub-thread about whether to *enforce* the locking contract in code (comments 11–16), not a reply that re-examines the "unconditionally connects" phrase specifically — the ledger's phrasing slightly overstates what comment 17 was endorsing, though the independent fact (comment 10's wording was proposed after comment 8's ctx.Err() discussion, and the pre-PR code had no comment at all) still supports "intentional" without relying on comment 17 for that part. Decisive evidence pointer: packet.md lines ~326-339 (comments 15-17).

*(Sub-agent tool metadata reported by the harness for this dispatch: 23 tool uses, ~219s duration, 49080 sub-agent tokens — reproduced here since the task asked for token usage where the harness reports it; that figure is the sub-agent's, not mine — see §1, my own usage is not reported to me anywhere.)*

### 5.3 What the primary did with the return

Both rows returned `holds`, each with at least one `path:line` citation the primary ledger did not carry (Row 1: four new citations in backoff/dialoptions/balancer_wrapper/callback_serializer; Row 2: the merge-base absence of any prior doc comment, plus the comment-8-precedes-comment-10 timeline). Batch conclusion `clean verdict stands`. Per SKILL.md step 3, this is exactly the required outcome — no row was re-opened, so no re-falsification and no follow-up batch is needed; the one-clean-verdict-batch use stays within the "one initial plus one follow-up" cap with the follow-up unused. I accepted both `holds` verdicts as-is.

**Citation-precision correction (self-caught during final validation, not by the verifier):** while assembling the payload I re-checked my own and the verifier's `path:line` citations for `resetTransportAndUnlock` against the actual head file with `awk 'NR>=1234 && NR<=1263'` and found two imprecise line spans that do not change any substance. My own ledger row (§4.1/§3.2) originally cited `clientconn.go:1234-1245` for "sets `connectivity.Connecting` before its first `ac.mu.Unlock()`" — the state-set and unlock are actually at lines 1261-1262, not within 1234-1245 (which only covers the function's opening ctx-err check and backoff/duration computation, before the state-set). I corrected the §3.2 table and the §4.1 ledger's own falsification prose (both under my control, not a record of something already sent elsewhere) and the payload, all to `clientconn.go:1234-1262` (the whole pre-unlock section, ending at the actual `Unlock()` line), and re-ran `validate_review.py`/`--render`/`--emit-batch` on the corrected payload (all exit 0 again) and re-ran the timing mark, both after this correction. §5.1's "exact prompt given to the verifier" necessarily still shows the original, uncorrected `1234-1245` citation, because that is a verbatim record of what was actually sent before I caught the imprecision — changing it would misrepresent history, so it stands uncorrected there by design, with this note as the correction of record. Separately, the verifier's own verbatim report (§5.2) cites "`clientconn.go:1259` call site" for `ac.updateConnectivityState(connectivity.Connecting, nil)`; the actual line is 1261 (off by two, likely a miscount, since 1259 is `connectDeadline := time.Now().Add(dialDuration)`, the line immediately before the blank line preceding the real call). I am not editing the verifier's verbatim quote in §5.2 to preserve an accurate record of what was actually returned, but per SKILL.md's "validate every correction against the diff" I checked the underlying claim itself (that `updateConnectivityState` runs, then `ac.acbw.updateState` enqueues non-blockingly, then `ac.mu.Unlock()` follows) against the real lines 1261-1262 and `balancer_wrapper.go`/`internal/grpcsync/callback_serializer.go`, and the substance holds regardless of the two-line miscount — the verdict `holds` is unaffected. Neither slip changes any admitted fact, gate, disposition, or the batch conclusion; both are recorded here in the interest of exhaustive, honest disclosure rather than because they are consequential.

One nuance I am recording rather than silently accepting: the verifier's observation on Row 2 is correct that comment 17 ("I think the name of the function and the comment should be sufficient for this") was replying inside the sub-thread about whether to *additionally enforce* the locking contract in code (comments 11–16: "should we have code check for this as well?" → "Can you suggest how to enforce the locking?" → "yeah it will probably require... a custom mutex" → "I think the name of the function and the comment should be sufficient for this."), not a second, independent re-endorsement of the literal word "unconditionally." This does not change Row 2's disposition (dfawley still authored and the author still adopted the comment text verbatim in comment 10, which is what gate 6 turns on — deliberate authorship, not a second sign-off on that specific word), but it is a real refinement of my falsification's evidentiary weight, and I record it here rather than overstating comment 17's scope in the published summary. I did not need to change any published prose because the summary and observation I drafted do not cite comment 17 as approving the word "unconditionally" specifically — they cite it (correctly) only as the thread's closing verdict that the doc-comment approach is adequate, which is what comment 17 actually says.

## 6. Findings for publication

**Zero.** No candidate survived primary falsification, and the required clean-verdict batch (§5) returned `clean verdict stands` on both dropped candidates, so neither is republished as a finding. There is nothing to render under `Findings` or `Unanchored findings`.

## 7. Questions

**Zero.** No statically unresolvable, outcome-changing fact was identified. The one candidate item that came closest — the PR's own "100000 attempts, no flake" measurement (Issue-fit row 4, §3.2) — is a *supporting assertion*, not an acceptance requirement, its absence of independent reproduction does not by itself warrant a question per the rubric's Issue-fit routing text, and no material decision is gated by it (the pull request is already merged). No question is published.

## 8. Observations

**One published** (cap is 3; nothing else qualified, so nothing was left on the cutting-room floor for the cap specifically — see below for what *was* dropped and why it is not an observation):

> Holding `ac.mu` across the `go ac.resetTransportAndUnlock()` spawn in `updateAddrs` leaves that function's own deferred `ac.transport.GracefulClose()` cleanup blocked until the spawned goroutine releases the lock, a handoff that `tearDown` avoids in the same file by unlocking explicitly before calling `GracefulClose`. Evidence: `clientconn.go:983-996`, `clientconn.go:1571-1583`.

This is the accurate residual fact behind candidate `clientconn/updateaddrs-gracefulclose-lock-handoff` (§4.1): the candidate itself failed admission on proven consequence (gate 4 — I proved there *is* no consequence, i.e. "observation (consequence absent)" under the rubric's own naming), but the underlying structural fact (an unusual, verified-safe lock-handoff pattern that differs from the codebase's own more conservative pattern for the identical hazard) is accurate, decisively evidenced, and worth a maintainer's attention without being actionable. It does not use "should"/"must" and is one sentence before its `Evidence:` pointer, matching `output-contract.md`'s Observations form (confirmed mechanically — see §11).

Candidate `clientconn/resettransportandunlock-doc-unconditionally` (§4.2) is **not** promoted to an observation: it failed admission on gate 6 (intentional/deliberate authorship), not on gates 1/4 (meaningful impact / proven consequence), and the rubric's Observations routing is specifically for facts that fail *only* on gates 1/4. A gate-6 drop stays entirely private.

## 9. Mechanism checklist

| Mechanism | Fired? | Where demonstrated |
|---|---|---|
| Question channel | **Did not fire.** | §7 — no statically unresolvable, outcome-changing fact existed; the one near-miss (the "100000 attempts" measurement) is a supporting assertion the rubric explicitly says does not by itself warrant a question. |
| Clean-verdict / related-acquittal verification | **Fired — clean-verdict (zero-survivor) mode.** | §1 (trigger sentence quoted), §4 (complete ledger persisted before dispatch), §5 (dispatch + verbatim `holds`/`holds`/`clean verdict stands`). Related-acquittal mode did not apply (it requires at least one *surviving* candidate in the same batch; there were none). No row was re-opened, so the "row re-opened... re-enters primary falsification" rule was not exercised. |
| Observations | **Fired.** | §8 — one observation published, drawn from the gate-4 residue of a falsified candidate; the gate-6 candidate was correctly withheld from this channel. |
| Fix-sufficiency check on a concurrency/invariant candidate | **N/A — no candidate was confirmed as a live bug**, so there was no fix to check for sufficiency; `verifier-concurrency.md`'s bug-class check (which only triggers "for every confirmed kind=concurrency or kind=invariant candidate") explicitly did not fire, and the verifier's report confirms it treated this correctly ("Since Row 1 is not being re-opened, verifier-concurrency.md's additional obligations do not apply."). |
| Follow-up verifier round | **Did not fire** — not needed. | §5.3 — `clean verdict stands` on the first (and only) batch leaves nothing to re-falsify; the cap ("one initial plus one follow-up batch") was not approached. |
| Deferral handling | **Fired, resolved as *not* an open deferral.** | §10 — the review record's two apparently-deferred threads ("Discussed offline: it doesn't matter if resetTransport() returns error after state being updated to connecting"; "I think the name of the function and the comment should be sufficient for this") are closing *resolutions*, not deferrals of a decision to a future point ("we can fix this during the API review", "let's revisit later") — I treated them as settled, not as open questions, and recorded that judgment call explicitly. |
| Retrospective mode | **Fired.** | The `Mode:` line in the summary body (§11/payload) and the packet's binding condition (target `merged: true`, posting identity did not author, no separate publication authorization) — publication is rendered and reported, never attempted. |
| Early dispatch of the verifier batch | **Explicitly did not fire — by rule, not by omission.** | §5, first line: SKILL.md's own exclusion ("do not dispatch early when the diff touches a concurrency or failover path... dispatch after the complete pass") applies to this diff, so I dispatched only after the complete falsification pass, not before. |

## 10. History discipline

I read history **only up to and including the pinned merge-base/head**, never beyond. Exact history commands run, all inside `/tmp/qual137/runs/m-bea6be14-seed2-att-08`:

- `git merge-base master review-head` → confirms merge-base `daab56344e612097fd50c46c433de5d9b6013837`.
- `git log --oneline master -1` and `git log --oneline review-head -1` — confirms the two pinned tips only (`daab5634 examples: Add OpenTelemetry example (#7296)`; `76ef33f4 Merge remote-tracking branch 'source/master'...`).
- `git diff --stat master review-head` — confirms `clientconn.go | 13 ++++++-------`, matching the packet's `+6/−7`.
- `scripts/review_context.py --merge-base <sha> --head <sha> --store ...` (run from the clone root) internally issued `git diff --name-status -M -z <merge-base>...<head>` and a unified diff of the same two pinned SHAs, plus `git log` scoped to `clientconn.go` bounded at the merge-base, printed under the tool's own `history` section: three commits, all dated **before** the merge-base (`2024-06-21`, `2024-05-24`, `2024-05-22`) — this is ordinary file-history-before-the-pin, not history beyond the pinned head.
- `git show daab56344e612097fd50c46c433de5d9b6013837:clientconn.go` and `git show daab56344e612097fd50c46c433de5d9b6013837:CONTRIBUTING.md` — merge-base blob reads, used for the falsification's base-branch guarantee check (gate 2) and for the repository-guidance read (packet §7).
- `git log --oneline -- test/subconn_test.go` — used only to confirm `TestSubConnEmpty` predates this PR (last touching commit `81b9df23`, well before `daab5634`); this is history *before* the pin, consulted to establish that the test is not part of the reviewed diff, not to look beyond the pinned head.

Nothing reachable only after `76ef33f44a600c3ed1a385979fd1dfbcade3fbb6` was read, requested, or referenced (the clone's history is truncated there in any case). The verifier sub-agent was instructed under the same constraint and reported no history command beyond reading the two pinned revisions with `git show`.

## 11. Sandbox disclosure

No path outside the declared sandbox (the clone at `/tmp/qual137/runs/m-bea6be14-seed2-att-08`, the skill snapshot at `/tmp/qual137/snapshots/bea6be14/skills/code-review-publish/`, the packet directory `/tmp/qual137/packets/m/`, and my own work/report/payload/timing paths under `/tmp/qual137/work/m-bea6be14-seed2-att-08/` and `/tmp/qual137/reports/m/`) was read by me or, per its own report, by the verifier sub-agent. `GOMODCACHE=/tmp/qual137/gomodcache` and `GOCACHE=/tmp/qual137/gocache` were used only as environment variables for `go test`/`go build` invocations (per the packet's execution allowance), not read as source material.

## 12. Everything consulted beyond the diff

**Files read (beyond the single-call diff read from `review_context.py`):**

- `clientconn.go` (head, `/tmp/qual137/runs/m-bea6be14-seed2-att-08/clientconn.go`) — targeted ranges 900-1010, 1200-1420, 1480-1520, 1540-1590 (bounded reads under the rubric's risk-led discovery: tracing `updateConnectivityState`, `onClose`/`createTransport`, `resetConnectBackoff`, and `tearDown` to settle the concurrency candidate's safety premise).
- `clientconn.go` at merge-base (`git show daab56344e612097fd50c46c433de5d9b6013837:clientconn.go`, piped through `grep -n resetTransport` / `grep -n resetBackoff`) — gate-2 base-branch guarantee check and a sweep for stray callers of the old name `resetTransport`.
- `test/subconn_test.go` (full file, 127 lines, ≤300-line whole-file-read exception) — to identify and confirm `TestSubConnEmpty` exercises the candidate's exact code path.
- `xds/internal/xdsclient/tests/authority_test.go` (grep only, for the `TestAuthorityRevive` definition line) — not read as a whole file; only the function signature location was needed to run it.
- `CONTRIBUTING.md` at merge-base (`git show daab5634...:CONTRIBUTING.md`) — read in full (it is short); classified as PR-workflow/contributor-process guidance, not a code-standards instruction file in the AGENTS.md/CLAUDE.md sense, so it produced no repository-rule candidate and (correctly, per the output contract's exhaustive membership rule) is excluded from the `guidance` digest field.

**Searches (all via `Grep`/`grep -n`, each noted with scope and case-sensitivity):**

- `grep -n "resetTransport"` and `grep -n "resetBackoff"` over `clientconn.go` at head and at merge-base — file-scoped (not repo-wide), case-sensitive (identifier search, case sensitivity is correct for a Go identifier).
- `grep -rn "func.*GracefulClose|onClose"` over the whole clone — **repo-wide**, case-sensitive; found `internal/transport/http2_client.go`, `internal/transport/transport.go`, plus several test files, narrowing the search to `http2_client.go` for the actual `GracefulClose`/`onClose` definitions.
- `grep -n "func Test.*UpdateAddr|updateAddrs("` over `clientconn_test.go` and `test/*.go` — **not** repo-wide (two explicit paths), case-sensitive; zero hits, prompting the next, wider search.
- `Grep` for `"UpdateAddresses"` — **repo-wide**, case-sensitive (a specific exported Go identifier); returned 17 files, from which `test/subconn_test.go` was selected as directly relevant (a SubConn-address-update integration test).
- `grep -n "func Test.*AuthorityRevive|AuthorityRevive"` over `xds/internal/xdsclient/tests/authority_test.go` — single-file, case-sensitive.
- `grep -n "^func Test("` over `test/*.go` — used to find the package's single top-level `Test` entry point (grpc-go's `grpctest.RunSubTests` convention) and its `RunSubTests` implementation (`internal/grpctest/grpctest.go`), needed only to construct the correct `-run 'Test/SubConnEmpty'` subtest path.

None of these searches were repo-wide *and* case-insensitive; none needed to be, since every search target was an exact Go identifier or a known filename, not free text or natural-language wording (the rubric's "search the whole repository, case-insensitively, for the rule's old wording" applies specifically to synchronization-drift candidates, which none of these were).

**Focused test/build commands run** (all offline, from the clone root, `GOMODCACHE=/tmp/qual137/gomodcache GOCACHE=/tmp/qual137/gocache GOFLAGS=-mod=mod GOPROXY=off`):

| Command | Exit | Duration | Outcome |
|---|---|---|---|
| `go test ./test/ -run 'Test/SubConnEmpty' -race -v -count=1` | 0 | ~1.2s (test itself ~10ms) | PASS — exercises the exact `updateAddrs`/`ac.transport != nil` branch the concurrency candidate was about; no race, no hang. |
| `go test ./xds/internal/xdsclient/tests/ -run 'Test/AuthorityRevive$' -race -v -count=20` | 0 | ~4.2s | PASS ×20 — the issue's own regression test, first pass to confirm the `-run` pattern and basic health. |
| `go test ./xds/internal/xdsclient/tests/ -run 'Test/AuthorityRevive$' -race -count=300` | 0 | ~41.8s | PASS 300/300 — higher-volume corroboration of the PR's own "100000 attempts, no flake" claim (not a reproduction at that scale, disclosed as such in Issue-fit row 4). |
| `go build ./...` | 0 | a few seconds | Clean build at the reviewed head — sanity check that the diff compiles and nothing else in the tree references the old `resetTransport` name. |

The verifier sub-agent additionally, independently, re-ran `go test ./test/ -run 'Test/SubConnEmpty' -race -v` (exit 0, ~1.5s, no race) — see §5.2.

## 13. Notes — judgment calls on the skill's contract

1. **Reconstructing the forge packet offline.** The skill's step 1 specifies fetching the pull request via `gh api graphql` and normalizing the saved pages with `forge_packet.py normalize`. This run has no network access; the packet at `/tmp/qual137/packets/m/packet.md` gives the same information pre-fetched and pinned, but not as raw `gh api graphql` JSON, and not with the forge's internal numeric ids (`fullDatabaseId`). I treated the packet's own binding instruction ("If your skill's phase 1 asks you to resolve the target from the forge, that phase is satisfied by this packet") as license to *reconstruct* a schema-valid root page from the packet's verbatim text and feed it through the real `forge_packet.py normalize` and `context_fingerprint.py --packet`, rather than skip the digest computation or hand-compute it outside the tooling. I used synthetic, internally-consistent sequential numeric ids for every review/comment/thread-comment node, since the packet does not supply real ones and I have no way to fetch them. I verified (§2) that this choice has zero effect on the actual digest value, because `context_fingerprint.py --packet` only reads `pr.{title,body}` and `issues[].{coordinate,title,body,comments[].{id,author,created_at,updated_at,body}}` — and the one place a synthetic id could matter (issue-comment ordering) is pinned by the verbatim timestamps regardless of the id values chosen. I disclose this as a deviation from literally running `gh api graphql`, which was impossible here, not as an uncontrolled guess.
2. **`comments_available`/`comments_complete` for the issue.** The packet states "comments_available: true" and lists all 3 issue comments with nothing marked truncated; I passed no `comments_available`/`comments_complete` override, matching the packet's own claim of completeness.
3. **CONTRIBUTING.md classification.** I read it (packet §7 requires this) and classified it as PR-workflow/contributor-process guidance rather than a code-standards instruction file. This matters for two things: (a) whether it belongs in the `guidance` digest field — it does not, because the output contract's guidance membership rule is an *exhaustive* enumeration of `AGENTS.md`/`CLAUDE.md`/root `CONTEXT.md`, and `CONTRIBUTING.md` matches none of those categories; and (b) whether it could produce a repository-rule finding — it could not, because its content (PR size, commit hygiene, CLA, test-running advice) does not "add a repository-specific invariant, scope, remedy, or verification requirement beyond generic correctness advice" applicable to the *content* of `clientconn.go`'s change.
4. **Two apparently-unresolved GitHub review threads treated as settled, not as open deferrals.** Both review threads in the packet remain `isResolved: false`/"thread unresolved" at the merge instant (a GitHub UI state, not necessarily a live technical disagreement). I read each thread's actual last comments and judged: thread 1 ends with "Discussed offline: it doesn't matter if resetTransport() returns error after state being updated to `connecting`" (`purnesh42H`, closing the concern purnesh42H itself raised) and thread 2 ends with "I think the name of the function and the comment should be sufficient for this" (`dfawley`, the maintainer who proposed the wording, closing the concern about enforcing the lock contract in code). Neither uses deferral language ("we can fix this later," "let's revisit," "good enough for now" applied to an *open* item) — both are conclusions. I therefore did not treat either as an open item under SKILL.md's explicit-deferral rule ("An explicit deferral... is evidence that the deferred question is *open*"), and did not manufacture a question or finding from either. This is a judgment call because GitHub's unresolved-thread flag could be (mis)read as "still open" by a less careful pass; I resolved it by reading the content, as the rubric requires ("Search current review threads and CI output for the same issue" in the falsification steps), not the metadata flag.
5. **Observation promotion from a dropped concurrency candidate.** I promoted the residual fact behind the dropped `clientconn/updateaddrs-gracefulclose-lock-handoff` candidate to a published Observation (§8) rather than leaving it fully private. This is a judgment call the rubric permits but does not mandate ("Route an accurate fact to Observations when it fails finding admission specifically on meaningful or proven consequence" — permissive framing, "route," not "must route every such fact"). I judged it worth the cap slot because it names a real, if safe, architectural asymmetry in the same file (`tearDown`'s explicit-unlock-then-close vs. `updateAddrs`'s defer-across-a-goroutine-handoff) that a future contributor extending either function could get wrong, and it has two decisive, cheap-to-check evidence pointers. I did not promote the dropped maintainability candidate (doc-comment wording) to an observation, because it failed on gate 6 (intentional), which the Observations section's routing text does not cover.
6. **No `re-review.md` or `conformance.md` branch.** `re-review.md` loads "when step 1 finds prior state from the posting identity" — the packet states posting identity `kamui` has no prior comments or reviews on this PR, so this is an ordinary first review, not a re-review; the reference was not loaded, and none of its delta/carried-finding/reply machinery applies. `conformance.md` loads "when a source names a versioned artifact" (a stub, binding, SDK-tracking-a-release, schema, or generated-source-and-generator-input) — nothing in the issue, PR text, or diff names such an artifact (this is a plain Go source-code concurrency fix, not generated or schema-tracking code), so it was not loaded and the Issue-fit ledger used only the two-source (issue + pull-request-text) form.
7. **Why the primary review itself was not delegated to a sub-agent.** The dispatch instructions for this cell are explicit that the review itself must be done by me, in this context, and that only sub-agents the skill's own process calls for may be spawned. The skill's frequent path ("This single integrated reviewer is the complete frequent path; do not fan out separate code and requirements finders") matches this: the only sub-agent SKILL.md's step 3 calls for is the verifier, dispatched once, as documented in §5.

## 14. Validation and the render-instead-of-publish step (SKILL.md steps 5–6)

- `python3 scripts/validate_review.py --render` on the assembled payload printed **no lines** (exit 0) — correct, since a `--render` fragment is only emitted per finding/question item and this review has zero of either; there is nothing to paste into the summary body's `Findings`/`Open questions` sections because neither section exists.
- `python3 scripts/validate_review.py` (plain mode) on the same payload: **exit 0, no violations.**
- Per rule 2 of this cell's binding conditions and the output contract's publication invariants ("Keep retrospective review of a merged pull request non-publishing unless the caller separately and explicitly authorized publication to that merged target" — not the case here), SKILL.md step 6 ("Publish one review") is rendered instead of executed: I ran `python3 scripts/validate_review.py --emit-batch payload.json > batch.json` (exit 0) to confirm the exact forge-native batch shape the validated payload would produce, but **no `gh api` call, or any other network/write call, was made** — the batch was generated and inspected locally only, never sent anywhere.
- The complete would-be review is the payload file: **[`/tmp/qual137/reports/m/m-bea6be14-seed2-att-08-payload.md`](/tmp/qual137/reports/m/m-bea6be14-seed2-att-08-payload.md)** — summary body (with the required `Mode:` line), the one observation, and the run trailer, exactly as `--render`/`--emit-batch` would have submitted it as a single `COMMENT`-event forge-native review with `comments: []` (there are no line-anchored items, since there are zero findings and zero questions).
- **Would-be status:** `Approved (advisory)`. **Would-be reviewed head:** `76ef33f44a600c3ed1a385979fd1dfbcade3fbb6` (re-verified against the packet's pinned head; the clone's `review-head` branch is checked out at this exact SHA — confirmed via `git log --oneline review-head -1` in §10 — so the stale-head publication guard has nothing to detect in this offline, single-snapshot run). **Would-be review URL / finding URLs:** none — nothing was posted, there is no forge response to report a URL from. **Open questions:** none. **Disputed findings:** none (first review, not a re-review; no prior state to dispute against — see §13 note 6). **Anything that failed to publish:** nothing failed; nothing was attempted, by design (retrospective, non-publishing mode).

