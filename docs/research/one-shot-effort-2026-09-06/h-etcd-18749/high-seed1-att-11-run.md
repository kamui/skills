# Research report — cell `h-high-seed1`, attempt `att-11`

Target: `etcd-io/etcd#18749` — "Fix risk of a partial write txn being applied"
Skill: `code-review-publish` snapshot at `/tmp/effort124/skill/skills/code-review-publish/`
Pin source: `/tmp/effort124/packets/h/packet.md` (phase 1 already resolved by orchestrator; not re-fetched)

## 1. Metadata

- **Target / cell / attempt:** `etcd-io/etcd#18749`, cell `h-high-seed1`, attempt `att-11`.
- **Skill and pin:** `code-review-publish` (current, non-legacy). References loaded: `review-rubric.md`, `output-contract.md`, `verifier.md`, `verifier-concurrency.md` (read, but ultimately not attached to the verifier brief — see §7 note). `re-review.md` and `conformance.md` were **not** loaded: no prior state from posting identity `kamui` (packet confirms no prior comments/reviews from `kamui`), and no versioned artifact conformance is implicated by this change.
- **Model:** I (the primary reviewer) ran on `claude-sonnet-5`. The one verifier sub-agent I dispatched ran on `model: "sonnet"` via `subagent_type: "v5b-verifier-effort-high"`, per the dispatch's binding instruction.
- **Verification trigger that fired:** Zero-survivor clean-verdict mode (`SKILL.md` step 3). All candidates I raised were falsified/dropped at primary review; the change touches a data-integrity surface (cross-node write-txn consistency / KV revision and consistency-index bookkeeping) and a concurrency surface (backend batch-tx and store locks), so the mandatory clean-verdict batch fired even with zero survivors.
- **Sub-agents spawned:** 1 — role: clean-verdict verifier, `subagent_type: "v5b-verifier-effort-high"`, `model: "sonnet"`, `run_in_background: false`.
- **Candidates raised:** 5 (see ledger, §3). **Candidates surviving my own falsification:** 0.
- **Verifier verdicts:** all 5 ledger rows ruled `holds` (see §7 for the verbatim return) — no `disposition ... does not hold; re-open it`.
- **Findings for publication:** none (0 must-fix, 0 consider).
- **Questions:** none.
- **Observations:** none (no accurate fact cleared the observation bar; the one candidate close to the line — a comment typo — failed even that bar on triviality, see ledger row 4).
- **Coverage:** complete — both changed files fully reviewed (all diff chunks consumed, none `missing`); both risk-directed checks (data-integrity/partial-write and concurrency/lock-release) have evidence-backed outcomes; the sole changed test function was traced and executed at the pinned head.
- **Derived status:** `Approved (advisory)` — see §output-contract Status derivation in §9.
- **My own token usage:** not reported by the harness in any tool result visible to me in this session; I have no other way to obtain it, so I state it does not appear to be available rather than estimating.

Payload file: [`/tmp/effort124/reports/h/h-high-seed1-att-11-payload.md`](/tmp/effort124/reports/h/h-high-seed1-att-11-payload.md)

## 2. Run identity (pinned, from the packet — not re-resolved)

| | |
|---|---|
| Repository | `etcd-io/etcd`, `https://github.com/etcd-io/etcd` |
| PR | #18749, "Fix risk of a partial write txn being applied", author `shyamjvs` |
| Head | `8a0fd66db3291bd6397a1341dc07ad41294a3caf` |
| Base ref | `main` |
| Base SHA / merge-base | `bb381d473c24ff2cd771f109c63443e03ac459c2` (identical) |
| state / merged | `MERGED` / `true` (2024-10-24T09:25:08Z) |
| Originating issue | `etcd-io/etcd#18679` (closing reference) |
| Posting identity | `kamui`, third party, no prior state → first review, event `COMMENT` |
| Mode | Retrospective review of a merged pull request; **publication disabled** (not separately authorized) |

## 3. Requirement (Issue fit) ledger — built before reading the diff for compliance

Source order: (1) closing issue `etcd-io/etcd#18679`, (2) PR title/body. No versioned artifact is implicated (`conformance.md` not loaded).

| # | Outcome | Class | Source | Disposition | Evidence |
|---|---|---|---|---|---|
| R1 | "The etcd node on which write txn execution fails should crash without trying to commit the failed transaction (or other side effects like incrementing KV revision or CI)." | acceptance requirement | `issue-18679/what-did-you-expect` | **met** | `server/etcdserver/txn/txn.go:305-321` diff removes the `txnWrite.End()` call that used to run before `lg.Panic(...)` on a write-txn failure; `server/etcdserver/txn/txn_test.go:339-385`'s `TestWriteTxnPanicWithoutApply` asserts the panic still fires and the backing DB file's SHA-256 hash is unchanged before/after. Executed at head: pass (see §5). |
| R2 | "I was able to confirm this risk exists based on the unit test failing with txnWrite.End() still around." | supporting assertion | `pr-body/"I was able to confirm this risk exists..."` | **not-verifiable** (supporting, not a condition of acceptance; reproducing the pre-fix failure would require reverting the fix, which is out of bounds for this review) | No material decision is gated on this — it corroborates R1, which is independently met by the current test passing at head. |
| — | PR title "Fix risk of a partial write txn being applied" | — | `pr-title` | restates R1 — no separate row (rubric: "a pull-request sentence that restates an issue requirement adds none") | — |

No non-goal, compatibility, or performance promise appears in either source. `Issue fit: Met` for the one acceptance requirement.

## 4. Complete-diff coverage / manifest

Built once via `python3 scripts/review_context.py --merge-base bb381d473c24ff2cd771f109c63443e03ac459c2 --head 8a0fd66db3291bd6397a1341dc07ad41294a3caf --store <work>/private-store/review-context-8a0fd66db....json`, run from inside the clone. Output was not `withheld` — the whole diff, manifest, ranges, and history sections printed in one call (no bounded `--from` reads were necessary).

```
M server/etcdserver/txn/txn.go       +5  -4  lines=723
M server/etcdserver/txn/txn_test.go  +29 -3  lines=677
```

`## chunks` inventory: `diff coverage: complete (2/2 chunks consumed)` — no `missing` chunk. Both files: **reviewed**.

Function context printed by `--function-context` already covered the whole enclosing `txn()` function (`txn.go:305-328` at head, `305-327` at merge-base) and the whole enclosing test functions (`txn_test.go:339-385` and `:528-597` at head; `336-373` / `516-571` at merge-base), so no re-read of those enclosing symbols was needed.

## 5. Diff summary and Changed-tests inspection

**`server/etcdserver/txn/txn.go`** (the fix): in `txn()`, on a write-txn failure (`isWrite && err != nil`), the old code called `txnWrite.End()` immediately before `lg.Panic(...)`; the new code removes that call and only panics, with an expanded comment explaining the atomicity/consistency risk. This is exactly the requirement `etcd-io/etcd#18679` states (R1, met).

**`server/etcdserver/txn/txn_test.go`**: `TestWriteTxnPanic` is renamed to `TestWriteTxnPanicWithoutApply` and gains a before/after SHA-256 hash comparison of the backend's raw DB file around the `assert.Panicsf(...)` call, plus a new `computeFileHash` helper. `defer betesting.Close(t, b)` is replaced by `defer s.Close()` (retaining `b`'s temp path via `bePath`), and the assertions after the earlier prior-review thread's require/assert feedback (`require.NoErrorf`, `require.Equalf`) are already applied at head.

Changed-tests inspection (rubric's Changed tests section), execution order:
- **Setup:** fresh temp bbolt backend + `mvcc.Store`; cancelled `context.Context`.
- **Call under test:** `Txn(ctx, ..., txn, false, s, &lease.FakeLessor{})` where `txn` is `Success: [Put("foo","bar"), Range("foo")]` — the `Put` succeeds, the `Range` fails because `ctx` is already cancelled (traced through `executeTxn` → `executeRange` → `rangeKeys`'s `ctx.Done()` check at `server/storage/mvcc/kvstore_txn.go:102-104`), reproducing exactly the "partial write, later failure" shape the issue describes.
- **Assertions:** `assert.Panicsf` (recovers the panic internally, so execution continues after it — this exact question was the resolved prior-review thread on this same line; the head's code has no stray `defer` that would run only after that point, consistent with the thread's resolution) then `require.Equalf` on the before/after DB-file hash.
- **Cleanup:** `defer s.Close()`.
- **Table-driven?** No; single scenario, one full trace performed (not a "passing/fully understood group" needing compaction).

**Focused execution** (permitted under this run's execution allowance, offline, from the clone's `server/` module):

1. `cd /tmp/effort124/runs/h-high-seed1-att-11/server && GOMODCACHE=/tmp/effort124/gomodcache GOCACHE=/tmp/effort124/gocache GOFLAGS=-mod=mod GOPROXY=off go test ./etcdserver/txn/... -run TestWriteTxnPanicWithoutApply -v`
   — exit 0, wall time ~0.27s (test itself 0.06s). Decisive output line: `PANIC unexpected error during txn with writes {"error": "applyTxn: failed Range: rangeKeys: context cancelled: context canceled"}` followed by `--- PASS: TestWriteTxnPanicWithoutApply (0.06s)`, `PASS`, `ok go.etcd.io/etcd/server/v3/etcdserver/txn 0.271s`.
2. Same env, `go test ./etcdserver/txn/...` (whole changed package, run once under this flag set) — exit 0, `ok go.etcd.io/etcd/server/v3/etcdserver/txn 0.720s`, no failures.

No CI log for this exact head was available offline beyond the packet's Codecov comment ("All modified and coverable lines are covered by tests"); the PR's merge itself implies presubmit checks passed, but I did not treat that as a substitute for execution — I ran the test myself instead, per the rubric's preference for reuse-or-run.

## 6. Repository guidance

Per packet §7: no root/path-scoped `AGENTS.md`, `CLAUDE.md`, or root `CONTEXT.md` exist at the merge-base, so the output-contract's `guidance` fingerprint set is **empty** (`guidance=[]`). `CONTRIBUTING.md` and `.github/PULL_REQUEST_TEMPLATE.md` exist but are outside the three digest categories; I still read `CONTRIBUTING.md` (`git show main:CONTRIBUTING.md`) under the rubric's broader "Repository rules" section and found nothing beyond generic "all changes are expected to come with a unit test" (satisfied) and flaky-test/CI process notes not applicable here. `.github/PULL_REQUEST_TEMPLATE.md` is a one-line pointer to `CONTRIBUTING.md#contribution-flow`, not a rule. Neither yields a repository-rule finding.

## 7. Private candidate ledger — complete, with every disposition, written before verifier dispatch

All five candidates below were falsified/dropped at primary review, before any verifier dispatch.

| id | kind | claim (falsifiable) | disposition | decisive evidence | falsification reason |
|---|---|---|---|---|---|
| `txn/lock-not-released-on-panic-if-recovered` | concurrency | Removing `txnWrite.End()` before the panic in `txn()` leaves `store.mu` (RLock) and the backend batch-tx lock (`LockInsideApply`) held forever if the panic is ever recovered upstream of `Txn()`, deadlocking every future write transaction on the same store. | dropped (refuted — basis: `no-consequence`/`prevented`) | `server/etcdserver/txn/txn.go:309-317`; `server/storage/mvcc/kvstore_txn.go:147-153` (`Write()` takes `s.mu.RLock()` + `tx.LockInsideApply()`) | No `recover()` exists on the write-apply call path. Repo-wide, case-insensitive `recover()` search (see below) found matches only in `server/verify/verify.go`, `server/etcdserver/util.go` (an unrelated `Stringer.String()` logging helper), and test files (`raft_test.go`, `http_test.go`, `downgrade_test.go`, `verify_test.go`) — none on the `apply.go` / `uber_applier.go` / `server.go` call path from raft-apply to `txn.Txn`. `zap.Logger.Panic` always re-panics after logging; an unrecovered panic crashes the whole process by Go's default runtime behavior, which is exactly the outcome `etcd-io/etcd#18679` and its approving reviewers (`ahrtr`, `serathius`) intended (gate 6: intentional, established in the review record). |
| `txn/store-close-may-deadlock-on-abandoned-write-lock` | bug | `defer s.Close()` in `TestWriteTxnPanicWithoutApply` could hang because the abandoned write-txn's locks are never released, mirroring the earlier review-thread report that `defer betesting.Close(t, b)` blocked on an unbuffered channel write. | dropped (refuted — basis: `prevented`) | `server/storage/mvcc/kvstore.go:502-505` | `(*store).Close()` only does `close(s.stopc); s.fifoSched.Stop()` — it acquires neither `store.mu` nor the backend batch-tx lock, so it cannot block on the leaked write lock. Empirically confirmed: the focused test run (§5.1) completed in 0.06s with no hang. |
| `txn/put-deleterange-same-partial-write-risk` | requirement | The standalone helpers `Put()`/`DeleteRange()` (`server/etcdserver/txn/txn.go:34-56,97-110`, used by the apply layer's single-op path, `server/etcdserver/apply/apply.go:154,158`) still call `defer txnWrite.End()` unconditionally and don't panic on failure, so they carry the same "partial write persisted before crash" risk `etcd-io/etcd#18679` describes, left unfixed by this PR. | dropped (refuted — basis: `no-consequence`) | `server/etcdserver/txn/txn.go:58-92` (`put()`), `:114-131` (`deleteRange()`) | Traced every return path in both `put()` and `deleteRange()`: every error return happens **before** the function's sole mutating statement (`txnWrite.Put(...)` at line 92; `txnWrite.DeleteRange(...)` at line 132) — there is no error path after a mutation, so a standalone `Put`/`DeleteRange` request is all-or-nothing and cannot leave a partial write. The issue and PR problem statement concern only the multi-op `Txn()` request path, where independent sub-requests execute sequentially and a later one can fail after an earlier one already mutated shared state — a shape `Put`/`DeleteRange` do not have. |
| `txn/comment-typo-aply` | maintainability | The new comment in `TestWriteTxnPanicWithoutApply` reads "server panics after a write txn **aply** fails", a typo for "apply". | dropped (gate 1: no meaningful impact) | `server/etcdserver/txn/txn_test.go:377` | Cosmetic spelling error in a test comment; no effect on behavior, and not material enough to readability to pass gate 1 or the observation bar either (rubric: "Do not create an observation merely to preserve a dropped candidate"). |
| `txn/no-integration-e2e-repro-test` | requirement | Approving reviewer `ahrtr` asked "Ideally it would be great if we could create an e2e or integration test to reproduce the partially committed/persisted issue," and no such test was added. | dropped (gate 6: intentional/accepted) | packet §6, review submission `2024-10-20T08:23:30Z` (`ahrtr`, `APPROVED`) | The suggestion appears inside an `APPROVED` review, phrased as an aspiration ("would be great"), not a blocking ask, and the PR merged without it. Neither the originating issue nor the PR title/body mentions an e2e/integration-test requirement, so the Issue Fit ledger (§3) carries no row for it — gate 6 treats the maintainer's explicit approval, despite raising this exact point, as acceptance of the unit-test-only scope actually delivered. |

**Batched searches run while building this ledger** (all repo-wide over the clone, case-insensitive unless noted):

- `Grep pattern="recover\(\)"` over `/tmp/effort124/runs/h-high-seed1-att-11/server` (case-sensitive Go keyword; not meaningfully case-insensitive-ambiguous) → `files_with_matches`: `server/verify/verify.go`, `server/storage/backend/verify_test.go`, `server/etcdserver/version/downgrade_test.go`, `server/etcdserver/util.go`, `server/etcdserver/raft_test.go`, `server/etcdserver/api/rafthttp/http_test.go`. None on the apply/raft-loop call path.
- `Grep pattern="release locks before panic"` (`-i true`) over the whole clone → no matches (confirms the old comment text was fully removed, not merely relocated/duplicated elsewhere).
- `Grep pattern="txn\.Put\(|txn\.DeleteRange\(|txn\.Range\("` over the whole clone → located all callers of the standalone helpers (`apply.go:154,158,162`, `v3_server.go:135`, plus `mvcc` package's own tests and `lease/lessor.go:350`), used to build the `txn/put-deleterange-same-partial-write-risk` row.
- `Grep pattern="\.End\(\)"` over `server/etcdserver` → confirmed the only remaining `defer txnWrite.End()` sites are `Put()` (line 53) and `DeleteRange()` (line 109), and that the comment referencing `txn.End() early` is the new cautionary comment itself (line 312), not a second live call site.

## 8. Context digest

Computed once via `python3 scripts/context_fingerprint.py --packet <work>/packet.json -` with empty `specs`/`guidance` on stdin (`{}`).

- `pr.title`: "Fix risk of a partial write txn being applied"
- `pr.body`: the verbatim PR body from packet §3.
- `issues`: one issue, `etcd-io/etcd#18679`, title "Write txn shouldn't End() on a failure", body verbatim from packet §4, with its 7 comments verbatim (author, `created_at`/`updated_at` timestamps, body) from packet §4. `comments_available` true (not omitted), no `comments_complete: false` marker (the packet states the issue's 7 comments are complete through the frozen cutoff).
- `specs`: none.
- `guidance`: `[]` (see §6).

**Digest:** `14f8b1a52f049875a1427f65019f2ec00a6d0f35b8a43fe9e37574a47c1a8146`

**Judgment call (recorded under Notes, §12):** the forge normalization pipeline (`forge_packet.py normalize`) that would ordinarily assign each issue comment its stable numeric `fullDatabaseId` could not run — this run is offline and the packet gives comments as an ordered, numbered list without numeric ids. I assigned sequential ids `1`..`7` in packet order (the packet states the list is "verbatim, in order"). This is a construction necessity for a digest that the contract only defines over forge-fetched data; it does not affect anything else in the review.

## 9. Summary status derivation

Per output-contract.md "Status": no `must-fix` finding (unsettled or otherwise) → not `Changes Requested`. Coverage is complete and verification (the clean-verdict batch, §10) is complete → not `Incomplete`. No open question → not `Needs Information`. → **`Approved`**. Posting identity `kamui` has no gating authorization on this merged, retrospective target, so the event is `COMMENT` and the status line carries `(advisory)`: **`Approved (advisory)`**.

## 10. Verifier dispatch — zero-survivor clean-verdict batch

Trigger: zero candidates survived as findings (§7), and the change touches a data-integrity surface (cross-node write-txn consistency, KV revision/consistency-index bookkeeping on failure) and a concurrency surface (backend batch-tx / store locks) — both named risk surfaces in `SKILL.md` step 3's zero-survivor trigger list. One clean-verdict batch was dispatched with the complete candidate disposition ledger, unfiltered by risk surface, per the rule.

I did **not** attach `verifier-concurrency.md` to this batch's brief: that reference's own scope note says it applies "when a supplied *candidate*'s kind is concurrency or invariant" and extends the verifier's task "for every such candidate the verifier confirms" — this zero-survivor batch carries no live candidates, only already-dropped ledger rows subject to the clean-verdict task, whose "Attack depth" section already mandates the full five-step adversarial attack for any ledger row of kind `bug`, `concurrency`, `invariant`, or `security` (which covers the one `concurrency`-kind row here) without needing the concurrency-specific brief. This is recorded as a judgment call in §12.

Verifier sub-agent: `Agent` tool, `subagent_type: "v5b-verifier-effort-high"`, `model: "sonnet"`, `run_in_background: false`.

### Exact prompt given to the verifier

<details><summary>Full prompt (click to expand — reproduced verbatim)</summary>

```
You are an independent verifier for one clean-verdict batch under the code-review-publish skill's verifier protocol. You have NOT seen any primary reviewer reasoning beyond what is supplied below. Read `/tmp/effort124/skill/skills/code-review-publish/references/verifier.md` in full now (it owns your evidence procedure and the Clean-verdict task) before doing anything else.

## Binding rules (apply to you as this task's sub-agent)

1. Follow `verifier.md`'s Clean-verdict task exactly. You are ruling on already-dropped ledger rows, not searching for new findings.
2. This is an OFFLINE, read-only, non-mutating task. Do not run `git fetch`, `git pull`, `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the working tree. You may run read-only `git show`, `git log`, `git diff`, `grep`/ripgrep, and read files.
3. Focused Go test execution IS permitted, offline only, from the clone's `server/` module, with `GOMODCACHE=/tmp/effort124/gomodcache GOCACHE=/tmp/effort124/gocache GOFLAGS=-mod=mod GOPROXY=off`, 5 minutes per command, a given package's tests at most once per flag set, and nothing added to or changed in the clone. You should not need to run tests for this task, but it's available if a row's claim requires it.
7. Stay inside this sandbox only: the clone at `/tmp/effort124/runs/h-high-seed1-att-11` (read-only), the skill snapshot at `/tmp/effort124/skill/skills/code-review-publish/` (read-only, for reference docs only), and your own scratch output. Do not read or write anything under `/tmp/effort124/reports/`, `/tmp/effort124/work/`, `/tmp/effort124/packets/`, or any other run's directory. If you read anything outside this list, say so explicitly in your reply.
9. No session relays: finish in this one dispatch and return your complete verdict in your final reply. Do not ask anyone anything; if you cannot settle a row, say so in your ruling per the reference's `unresolved`/`re-open` rules.

## Pinned coordinates

- Repository: `etcd-io/etcd`, canonical URL `https://github.com/etcd-io/etcd`
- Clone (offline, local `origin`): `/tmp/effort124/runs/h-high-seed1-att-11`, local branch `review-head` checked out at head, local branch `main` pinned to the merge-base. Use `git show main:<path>` for merge-base versions, `git show review-head:<path>` or just read the working tree (already at head) for head versions.
- Head SHA: `8a0fd66db3291bd6397a1341dc07ad41294a3caf`
- Base ref: `main`; Base SHA / merge-base: `bb381d473c24ff2cd771f109c63443e03ac459c2` (identical)
- Changed files: `server/etcdserver/txn/txn.go` (+5/-4), `server/etcdserver/txn/txn_test.go` (+29/-3)
- Originating issue: `etcd-io/etcd#18679`, "Write txn shouldn't End() on a failure" — the issue asks that when a write transaction fails mid-execution (possibly after partially applying some operations), the etcd node must crash via panic WITHOUT committing/ending the transaction first (no KV revision bump, no consistency-index bump, no persisted partial write), because a write txn is never expected to fail and any silent recovery risks cross-node data inconsistency.
- PR title: "Fix risk of a partial write txn being applied"
- PR body (verbatim): "Fixes https://github.com/etcd-io/etcd/issues/18679\n\nI was able to confirm this risk exists based on the unit test failing with txnWrite.End() still around. I did have to add a few milliseconds of wait time between the txn End and panic to reliably reproduce it because it depends on whether backend commit happens in that window or not.\n\n/cc @serathius @ahrtr"
- Review record fact relevant to one row: `ahrtr` submitted an `APPROVED` review on 2024-10-20T08:23:30Z with body: "LGTM\n\nThanks @shyamjvs \n\nIdeally it would be great if we could create an e2e or integration test to reproduce the partially committed/persisted issue." The PR was subsequently merged without such a test being added.
- No repository-level AGENTS.md/CLAUDE.md/CONTEXT.md guidance files exist at the merge-base for this repo.

## The complete candidate disposition ledger — attack every row

Zero candidates survived primary falsification as findings. Attack each acquittal below using its cited code and any narrow surrounding evidence you need. Follow `verifier.md`'s Clean-verdict task procedure (restate the decisive premise; state the concrete falsifying condition; trace the opposite branch of every conditional the premise depends on, citing `path:line`; either construct a complete failing state transition or cite the specific impossible step; a `holds` ruling must cite at least one line the ledger row itself did not cite). Apply the full five-step attack to every row whose kind is `bug`, `concurrency`, `invariant`, or `security`; apply the one-citation check to rows of kind `requirement`/`maintainability`/`performance` unless they assert safety (row 5 below asserts an intentionality/acceptance premise from the review record, not a code-safety premise — treat it under the one-citation check: confirm or contradict its stated fact against the cited review-record evidence).

1. **id** `txn/lock-not-released-on-panic-if-recovered` — **kind** `concurrency`
   **claim:** Removing `txnWrite.End()` before the panic in `txn()` (server/etcdserver/txn/txn.go) leaves `store.mu` (RLock) and the backend batch-tx lock (acquired via `LockInsideApply()` inside `store.Write()`) held forever if the panic raised by `lg.Panic(...)` is ever recovered upstream of `txn.Txn(...)`'s caller, which would deadlock every future write transaction on the same store.
   **disposition:** dropped (refuted — basis: no-consequence/prevented)
   **decisive evidence cited:** `server/etcdserver/txn/txn.go:309-317`; `server/storage/mvcc/kvstore_txn.go:147-153` (`Write()` takes `s.mu.RLock()` then `tx.LockInsideApply()`, both released only in `End()`)
   **falsification reason given:** No `recover()` exists on the write-apply call path from the raft-apply loop through `applierV3backend`/`uberApplier` down to `txn.Txn`. A repo-wide search for `recover()` under `server/` found matches only in `server/verify/verify.go`, `server/etcdserver/util.go` (an unrelated `Stringer.String()` logging helper, not on the apply path), and test files (`raft_test.go`, `http_test.go`, `downgrade_test.go`, `verify_test.go`). `zap.Logger.Panic` always re-panics after logging, and Go's default runtime behavior for an unrecovered panic in any goroutine is to crash the entire process — the exact outcome the issue and its approving reviewers intended.
   **Your task:** Independently search `server/etcdserver/apply/`, `server/etcdserver/server.go`, and the raft-apply entry points for any `recover()` that could catch this panic before process termination. If you find none, trace at least one steady-state path (normal txn apply, not shutdown) from `raft node ready loop` → `apply` → `txn.Txn` to confirm there is no swallowing `recover()`, and separately confirm what `zap.Logger.Panic` actually does (re-panics vs. merely logs) by reading its source if vendored, or by citing etcd's own use of it elsewhere as evidence of its established semantics. State whether the row's premise (lock leak requires a `recover()` somewhere upstream) is itself correctly identified as the sole way this could bite, and rule `holds` or `re-open`.

2. **id** `txn/store-close-may-deadlock-on-abandoned-write-lock` — **kind** `bug`
   **claim:** In the new/renamed test `TestWriteTxnPanicWithoutApply` (server/etcdserver/txn/txn_test.go), `defer s.Close()` (an `mvcc.Store.Close()` call) could hang/deadlock because the panicking write transaction's locks (`store.mu` RLock and the backend batch-tx lock) are never released, mirroring the earlier PR review-thread's report that the previous `defer betesting.Close(t, b)` blocked on an unbuffered channel write.
   **disposition:** dropped (refuted — basis: prevented)
   **decisive evidence cited:** `server/storage/mvcc/kvstore.go:502-505`
   **falsification reason given:** `(*store).Close()` only does `close(s.stopc); s.fifoSched.Stop()` — it acquires neither `store.mu` nor the backend batch-tx lock, so it cannot block on the abandoned write lock. The primary reviewer separately ran `go test ./etcdserver/txn/... -run TestWriteTxnPanicWithoutApply -v` at the pinned head (`GOMODCACHE=/tmp/effort124/gomodcache GOCACHE=/tmp/effort124/gocache GOFLAGS=-mod=mod GOPROXY=off`) and it passed in 0.06s with no hang.
   **Your task:** Read `(*store).Close()` yourself and confirm it takes no lock the abandoned write-txn holds. Also read `fifoSched.Stop()`'s implementation to confirm it does not itself block on anything the panicking goroutine held. You may independently re-run the same focused test command (same flags, offline) if you want direct confirmation rather than relying on the primary's report — the run policy above permits it. Rule `holds` or `re-open`.

3. **id** `txn/put-deleterange-same-partial-write-risk` — **kind** `requirement`
   **claim:** The standalone helper functions `Put()` (server/etcdserver/txn/txn.go, calls `put()`) and `DeleteRange()` (calls `deleteRange()`) — used by the apply layer's single-op path (`server/etcdserver/apply/apply.go`) — still call `defer txnWrite.End()` unconditionally and do not panic on a write failure, so they are exposed to the same "partial write committed before crash" risk `etcd-io/etcd#18679` describes for the multi-op `txn()` path, and this PR left that unfixed.
   **disposition:** dropped (refuted — basis: no-consequence)
   **decisive evidence cited:** `server/etcdserver/txn/txn.go:58-92` (`put()`), `server/etcdserver/txn/txn.go:114-131` (`deleteRange()`)
   **falsification reason given:** Every error-return path inside `put()` occurs before its sole mutating statement (`txnWrite.Put(...)`, the function's last line); same structure in `deleteRange()` (every error return precedes `txnWrite.DeleteRange(...)`, the function's last line). Neither function has an error path that can fire *after* a mutation, so a standalone `Put`/`DeleteRange` request is all-or-nothing and cannot leave a partial write the way a multi-op `Txn()` request can (where an earlier sub-request's mutation can be followed by a later sub-request's failure).
   **Your task:** Read `put()` and `deleteRange()` in full yourself (not just the lines cited) and confirm there truly is no return statement carrying a non-nil error positioned after the mutating call in either function. If either function's mutating call is not actually its last statement, or if it can be reached along a path where a prior partial mutation already occurred, say so and re-open. Otherwise rule `holds`, citing a line the ledger row's falsification did not already cite (e.g. the actual return type/signature confirming no error is possible from the mutation call itself, or the full list of every `return nil, err` / `return nil, ...` site in each function).

4. **id** `txn/comment-typo-aply` — **kind** `maintainability`
   **claim:** The new comment in `TestWriteTxnPanicWithoutApply` reads "server panics after a write txn aply fails", a typo for "apply".
   **disposition:** dropped (gate 1: no meaningful impact)
   **decisive evidence cited:** `server/etcdserver/txn/txn_test.go:377`
   **falsification reason given:** cosmetic spelling error in a test comment; no effect on behavior, and not material enough to readability to justify a finding or even an observation.
   **Your task:** One-citation check only (this row does not assert safety). Confirm the typo exists at the cited line and confirm your independent judgment on whether "no meaningful impact" is a fair characterization (i.e., the comment is still otherwise comprehensible despite the typo). Rule `holds` or `re-open`.

5. **id** `txn/no-integration-e2e-repro-test` — **kind** `requirement`
   **claim:** Approving reviewer `ahrtr` asked "Ideally it would be great if we could create an e2e or integration test to reproduce the partially committed/persisted issue," and no such test was added by this PR.
   **disposition:** dropped (gate 6: intentional/accepted)
   **decisive evidence cited:** the `ahrtr` APPROVED review quoted above under "Review record fact"
   **falsification reason given:** the suggestion appears inside an `APPROVED` review, phrased as an aspiration ("would be great"), not a blocking ask; the PR merged without it; neither the originating issue `etcd-io/etcd#18679` nor the PR title/body mentions an e2e/integration-test requirement, so it never enters the Issue Fit ledger as a row, and gate 6 (the rubric's "Unintentional" finding-admission gate) treats the maintainer's explicit approval — despite raising this exact point — as acceptance of the unit-test-only scope actually delivered.
   **Your task:** One-citation check (this row asserts an intentionality/review-record premise, not a code-safety premise). Confirm from the diff (`server/etcdserver/txn/txn_test.go`) that indeed no e2e/integration-style test (as opposed to the unit test in `server/etcdserver/txn/txn_test.go`) was added by this PR — you may `grep` the diff/changed-file list for that confirmation. Confirm the characterization of `ahrtr`'s comment as non-blocking is a fair reading (there is no rule text available to you claiming otherwise). Rule `holds` or `re-open`.

## What to return

For each of the 5 ledger ids: `holds` or `re-open`, with your own decisive `path:line` citation (not merely the one already given), and for a `concurrency`/`invariant`/`bug`/`security` row, note explicitly that you traced the opposite branch of every conditional the premise depends on. Then give exactly one batch conclusion: `clean verdict stands`, or one `disposition <id> does not hold; re-open it` line per row that fails. You may also return at most one non-actionable `observation` aside with a decisive evidence pointer if an accurate, sub-threshold fact surfaces incidentally (no `should`/`must` language) — but do not search for unrelated new findings. Do not render any publication-ready prose; return compact verdict records only.
```

</details>

### Verbatim verifier report

<details><summary>Full verifier reply (click to expand — reproduced verbatim)</summary>

```
## Verifier findings — clean-verdict batch (5 rows)

**Scope note:** All evidence gathered from within the permitted sandbox only: the clone at `/tmp/effort124/runs/h-high-seed1-att-11` (read-only) and `/tmp/effort124/gomodcache/go.uber.org/zap@v1.27.0/logger.go` (the pinned Go module cache, permitted as "cited code and narrow surrounding evidence"). No tests were run (not needed to settle any row). Nothing was read under `/tmp/effort124/reports/`, `/tmp/effort124/work/`, `/tmp/effort124/packets/`, or other runs' directories.

---

### Row 1 — `txn/lock-not-released-on-panic-if-recovered` (concurrency) — **holds**

Decisive premise: the lock leak materializes only if a `recover()` exists somewhere upstream of `txn.Txn(...)` on the raft-apply path.

Opposite-branch trace (does a swallowing `recover()` exist?):
- `server/etcdserver/txn/txn.go:296` — `txnWrite.End()` is a plain sequential statement, not deferred, immediately after the call to `txn(...)` at line 295; a panic inside `txn()` skips it entirely, so `storeTxnWrite.End()` (`server/storage/mvcc/kvstore_txn.go:182-194`, which is the *only* place `s.mu.RUnlock()` and `tx.Unlock()` are called) never runs.
- `server/etcdserver/apply/uber_applier.go:111-132` — `dispatch()`'s deferred func (lines 125-132) runs during panic unwind but contains no `recover()`; it only records metrics, so it does not stop propagation.
- `server/etcdserver/server.go:818-837` — `run()`'s deferred cleanup (no `recover()`) likewise runs during unwind but re-lets the panic propagate.
- Full-repo `recover()` inventory in `server/`: `server/verify/verify.go:68` (unrelated verification helper), `server/etcdserver/util.go:110` (a `Stringer.String()` panic-safety wrapper for logging v2 requests, unrelated to the write-apply path — confirmed by reading `util.go:100-116`), and four test-only files. None sit between the raft-ready loop and `txn.Txn`.
- `zap@v1.27.0/logger.go:282` — doc comment: "The logger then panics, even if logging at PanicLevel is disabled," confirming `lg.Panic(...)` always re-panics rather than merely logging.

New citations beyond the ledger's own: `kvstore_txn.go:182-194`, `apply/uber_applier.go:111-132`, `server.go:818-837`, `zap@v1.27.0/logger.go:282-286`.

Conclusion: the row's premise is correctly identified as the sole way this could bite, and no such `recover()` exists on the steady-state apply path. **Holds.**

---

### Row 2 — `txn/store-close-may-deadlock-on-abandoned-write-lock` (bug) — **holds**

Decisive premise: `(*store).Close()` cannot block on the abandoned write-txn's locks because it never acquires `store.mu` or the backend batch-tx lock.

Opposite-branch trace: `(*store).Close()` (`server/storage/mvcc/kvstore.go:502-505`) does `close(s.stopc); s.fifoSched.Stop()` — neither touches `s.mu` or `s.b.BatchTx()`. Tracing `fifoSched.Stop()` itself (`pkg/schedule/schedule.go:150-156`): it takes `f.mu` (the scheduler's own private mutex, unrelated to `store.mu`), sets `f.cancel = nil`, and blocks on `<-f.donec`, which is closed by the scheduler's own `run()` goroutine — a resource entirely independent of the panicking write-txn's held locks.

New citation beyond the ledger's own: `pkg/schedule/schedule.go:150-156`.

**Holds.**

---

### Row 3 — `txn/put-deleterange-same-partial-write-risk` (requirement) — **holds**

Read `put()` and `deleteRange()` in full. Every error-return site in `put()`: `txn.go:70-72` (`return nil, err` from the previous-kv range lookup) and `txn.go:76-78` (`return nil, errors.ErrKeyNotFound`) — both precede the sole mutating call `txnWrite.Put(...)` at `txn.go:92`, whose return value is only used to build the success response at `txn.go:93-94`; there is no error path after it. Same structure in `deleteRange()`: the only error return is `txn.go:121-123` (`return nil, err` from the prev-kv range lookup), preceding the sole mutating call `txnWrite.DeleteRange(...)` at `txn.go:132`, followed only by the unconditional success return at `txn.go:133`.

New citation beyond the ledger's own: the exact return-statement line numbers `txn.go:70-72, 76-78, 92-94` (put) and `txn.go:121-123, 132-133` (deleteRange), confirming the complete enumeration of every error-return site in both functions and that neither can be reached after a partial mutation.

**Holds.**

---

### Row 4 — `txn/comment-typo-aply` (maintainability) — **holds** (one-citation check)

Confirmed the exact text at `server/etcdserver/txn/txn_test.go:377`: `// 1. server panics after a write txn aply fails`. The typo ("aply" for "apply") is present but the sentence remains fully comprehensible in context (paired with line 378's parallel "2. no writes..." comment). "No meaningful impact" is a fair characterization — cosmetic only.

**Holds.**

---

### Row 5 — `txn/no-integration-e2e-repro-test` (requirement, intentionality premise) — **holds** (one-citation check)

Confirmed from the diff that the only test-file change is `server/etcdserver/txn/txn_test.go`, and the only new test is `TestWriteTxnPanicWithoutApply` at `txn_test.go:342-383` — a package-level Go unit test using `betesting.NewDefaultTmpBackend` and `mvcc.NewStore` directly in-process, not an e2e/integration-harness test (no `tests/e2e` or `tests/integration` file was touched). So indeed no e2e/integration test was added by this PR, matching the row's stated fact.

On the "non-blocking" characterization: the quoted `ahrtr` review is `APPROVED` with body opening "LGTM" before raising the suggestion in aspirational language ("Ideally it would be great if..."), and the PR merged without it. Nothing in the supplied review record contradicts reading this as a non-blocking suggestion.

New citation beyond the ledger's own: `server/etcdserver/txn/txn_test.go:342-383` (confirming the only new test is a unit test, not an e2e/integration test).

**Holds.**

---

## Batch conclusion

**clean verdict stands**

No `observation` aside is warranted — no sub-threshold fact surfaced that wasn't already captured in ruling on the five rows above.
```

Agent metadata returned alongside the reply: `subagent_tokens: 72206`, `tool_uses: 23`, `duration_ms: 227011`.

</details>

### Reconciliation

All 5 rows returned `holds`, each with at least one decisive citation the primary ledger row did not itself cite (satisfying `verifier.md`'s "a `holds` ruling on a fully attacked row must cite at least one line the ledger row did not cite"). Batch conclusion: `clean verdict stands`. Per `SKILL.md` step 3, "a successful clean-verdict batch does not retrigger itself" and "refuting the last candidate is not a global clean verdict" (inapplicable here — nothing was refuted; every acquittal was reaffirmed). Zero-survivor eligibility was recomputed after the batch and remains zero survivors, zero re-opened rows. No follow-up batch was needed or dispatched — the one-batch verification is complete, and no mandatory verdict remains missing.

## 11. Validation and payload

`python3 scripts/validate_review.py --render < payload.json` → exit 0, no fragments printed (0 findings, 0 questions — nothing to paste into the body). `python3 scripts/validate_review.py < payload.json` → exit 0, no violations. `python3 scripts/validate_review.py --emit-batch < payload.json > batch.json` → exit 0; `batch.json` carries `commit_id=8a0fd66db3291bd6397a1341dc07ad41294a3caf`, `event=COMMENT`, the summary body verbatim, and `comments: []`.

Immediately after the final successful `validate_review.py` run (no violations), I ran `python3 /tmp/effort124/mark_event.py /tmp/effort124/reports/h/h-high-seed1-att-11-timing.json payload_validated_at`, which recorded `2026-09-06T09:57:19.978388+00:00`. The payload was not changed afterward, so no second validation/mark was needed.

Per step 6 ("In non-publishing retrospective mode, skip the write and report the complete would-be review instead") and the packet's binding condition 4, I did not call `gh api` or any publishing endpoint. The complete would-be review is the payload file: [`/tmp/effort124/reports/h/h-high-seed1-att-11-payload.md`](/tmp/effort124/reports/h/h-high-seed1-att-11-payload.md) — one summary body, zero finding/question/observation comments, `event=COMMENT`, status `Approved (advisory)`.

## 12. Mechanism checklist

- **Question channel:** did not fire. No candidate reached the static-unresolvability bar (rubric's Issue fit / Uncertainty routing "question" rule); the one `not-verifiable` ledger row (R2, §3, a supporting assertion) gates no material merge decision, so it publishes no question.
- **Clean-verdict or related-acquittal verification, which mode, which rows, any re-open:** fired in **zero-survivor mode** (§10). All 5 ledger rows attacked; all returned `holds`; batch conclusion `clean verdict stands`; **no row was re-opened**.
- **Observations:** did not fire. No accurate fact cleared the "fails admission on consequence" bar of the Observations route; the closest candidate (the comment typo, ledger row 4) failed even that bar on triviality and is recorded as `dropped (gate 1)`, not routed to Observations, per the rubric's explicit instruction not to manufacture an observation just to preserve a dropped candidate.
- **Fix-sufficiency check on any concurrency/invariant candidate:** ledger row 1 (`txn/lock-not-released-on-panic-if-recovered`, kind `concurrency`) is the one concurrency/invariant-kind row. It was never a live "candidate" carried into a candidate-mode batch (it was falsified at primary review before any batch was assembled), so `verifier-concurrency.md`'s candidate-mode "state the invariant at the rule level / enumerate sibling interleavings / widen `change`" checklist does not apply to it as written (that checklist extends the verifier's task "for every such candidate the verifier confirms," and this row was never confirmed — it was refuted at the primary stage and only re-attacked as an acquittal). The clean-verdict task's own five-step depth (mandatory for `kind ∈ {bug, concurrency, invariant, security}`) was applied to it instead, and the verifier's Row 1 ruling explicitly traces the opposite branch of the row's controlling conditional (whether a `recover()` exists upstream) across every actor on the path (`uber_applier.go` dispatch, `server.go` run loop, the full-repo `recover()` inventory) before ruling `holds`. This is recorded as a judgment call in §13.
- **Follow-up verifier round:** did not fire. `clean verdict stands` with no re-opened row means no follow-up batch was warranted or dispatched (`SKILL.md`: "A successful clean-verdict batch does not retrigger itself").
- **Deferral handling:** one explicit deferral-shaped comment exists in the review record — `ahrtr`'s "Ideally it would be great if we could create an e2e or integration test..." inside an `APPROVED` review. Per `SKILL.md` step 1's instruction to record every explicit deferral of a design/naming/API-shape decision as an open question rather than accepted, I evaluated whether this qualifies: it is not a deferral of a design/naming/API-shape decision (the fix's shape — remove the pre-panic `End()` call — was not deferred or left open by anyone; this is a suggestion for *additional, different* test coverage, raised and then not acted on inside an unconditional approval). I treated it under the ordinary gate-6 "unintentional" test rather than as a live open deferral, and recorded the reasoning and the dropped candidate it produced as ledger row 5 (§7), verified `holds` by the clean-verdict batch (§10 row 5). This is recorded as a judgment call in §13.
- **Retrospective mode:** fired throughout. The summary body carries the mandatory `**Mode:** Retrospective review of merged pull request; publication disabled.` line (output-contract.md: "The `Mode` line is mandatory whenever `merged` is true"). No `gh api` write call was made at any point in this run.

## 13. History discipline

I read no history beyond the pinned head. The only history-adjacent command run was `python3 scripts/review_context.py`'s own `## history` section, which is part of the standard step-2 context build (not a separate history read) and reports, from data already reachable at the pinned head, the last commits that touched each changed file **before** this PR (`0232686ca`, `9c3edfa0a`, `bd7f0dab3` for `txn.go`; `ff4a8df3a`, `aa9748416`, `76cbfd364` for `txn_test.go`) — all of these are ancestors of the merge-base/head, not anything "after" the pinned head. I did not run `git log` past `review-head`, did not run `git fetch`/`git pull`, and the clone's remote is a local filesystem path with no network reachability (confirmed implicitly — no fetch was attempted). Exact commands run, exhaustively:

- `git status`, `git log --oneline -5 --all`, `git branch -a` (orientation only, once, at the very start).
- `git rev-parse review-head`, `git rev-parse main`, `git merge-base main review-head` (SHA confirmation against the packet's pinned values).
- `git show main:CONTRIBUTING.md`, `git show main:.github/PULL_REQUEST_TEMPLATE.md` (base-branch guidance file reads, per packet §7 / rubric's Repository rules section).
- `python3 scripts/review_context.py --merge-base ... --head ... --store ...` (the one mandated step-2 context build).

No other `git log`, `git show <commit>`, or history-inspecting command was run by me. The verifier sub-agent's dispatch explicitly forbade `git fetch`/`pull`/`checkout`/`switch`/`reset`/`stash`, and its verbatim report (§10) shows only `git show`/file reads within the clone at the pinned branches; it did not report running any further history commands, and I have no other record of its exact command list beyond what it stated in its reply (its internal tool-call transcript was not returned to me — the harness gave me only its final report and the `tool_uses: 23` count).

## 14. Sandbox disclosure

I read/wrote only:
- The clone: `/tmp/effort124/runs/h-high-seed1-att-11` (read-only; confirmed clean via `git status` at the end — "nothing to commit, working tree clean" — no mutation occurred, so the rule-4 hard-reset recovery was never needed).
- The skill snapshot: `/tmp/effort124/skill/skills/code-review-publish/` (SKILL.md, all five references, and the three scripts I invoked).
- The packet: `/tmp/effort124/packets/h/packet.md`.
- My own work directory: `/tmp/effort124/work/h-high-seed1-att-11/` (created `packet.json`, `payload.json`, `batch.json`, and `private-store/review-context-8a0fd66db3291bd6397a1341dc07ad41294a3caf.json`).
- My own report/payload/timing paths under `/tmp/effort124/reports/h/`.
- One `mktemp -d` call (`/var/folders/.../T/tmp.EOGBj3478S`) was issued while I was still re-reading the skill's literal "create a private directory outside the working tree" instruction, before I re-read the dispatch's explicit designation of `/tmp/effort124/work/h-high-seed1-att-11/` as "the private store" location (see §15 judgment call). **Nothing was ever written into that mktemp directory** — I redirected to `private-store/` under my assigned work directory before running `review_context.py --store`. I disclose the stray `mktemp -d` call itself as a path touched outside the strict enumerated list, even though no data was written there and it was immediately abandoned.

The verifier sub-agent reported (verbatim, §10) that it additionally read `/tmp/effort124/gomodcache/go.uber.org/zap@v1.27.0/logger.go` from the pinned Go module cache — a path outside the clone/skill/packet/report list, but inside the execution allowance's `GOMODCACHE=/tmp/effort124/gomodcache` location that this run's binding conditions explicitly provision for Go tooling; I judge this in-bounds (it is the module cache the run conditions themselves designate) and disclose it here per its own self-report rather than silently accepting it.

One `ls -la /tmp/effort124/reports/h/` directory listing (run to confirm my own output files were written) incidentally showed the filenames — not the contents — of a sibling attempt's files, `h-medium-seed1-att-12-run.md`, `h-medium-seed1-att-12-session.txt`, `h-medium-seed1-att-12-timing.json`. I did not open or read any of those three files; disclosed here for completeness since rule 7 restricts me to my own report/payload paths and a directory listing technically surfaced another attempt's filenames.

## 15. Notes — judgment calls on the skill's contract

1. **Private store location.** `SKILL.md` step 2 literally says "Create a private directory outside the working tree (`mktemp -d`)". This dispatch's own instructions designate `/tmp/effort124/work/h-high-seed1-att-11/` as "Your working directory for payload JSON, scratch files, **the private store**, and script output" and restrict me to that path plus the clone/skill/packet/report paths (rule 7). I treated the dispatch's explicit, cell-specific designation as authoritative over the skill's generic instruction (which exists to avoid a *predictable, shared* `/tmp` location — a threat the dispatch's own per-attempt work directory already avoids) and put the store at `<work>/private-store/review-context-<head>.json`. I flag the one stray `mktemp -d` call this produced (§14) as a disclosed deviation, not a silent one.
2. **`packet.json` for the fingerprint digest.** The skill's step-1 forge fetch (`gh api graphql` + `forge_packet.py normalize`) is explicitly out of scope per the packet's binding condition 1 ("offline... that phase is satisfied by this packet"). But `context_fingerprint.py --packet` requires a `forge-packet/1`-schema JSON with a `fingerprint.pr`/`fingerprint.issues` shape that only `forge_packet.py normalize` ordinarily produces (from GraphQL responses carrying stable numeric `fullDatabaseId`s). I hand-built a minimal, schema-conformant `packet.json` from the packet's verbatim PR/issue text and comments, in the same order the packet lists them. Since the packet gives no numeric comment ids, I assigned sequential ids `1..7` in the packet's stated order. This is a necessary construction, not a resolved ambiguity in the reference text itself; I record it here because a different, non-sequential id assignment would change the digest, and the packet — being byte-identical across every arm/replicate on this target — gives every replicate the same information to make the same deterministic choice from.
3. **`guidance` fingerprint set vs. "Repository rules" review scope.** The output-contract's `guidance` digest field is explicitly limited to root/path-scoped `AGENTS.md`/`CLAUDE.md` and root `CONTEXT.md` — none exist here, so `guidance=[]`. I still read `CONTRIBUTING.md` under the rubric's broader, separately-scoped "Repository rules" section (which is not limited to the digest's three categories) as due diligence, per packet §7's instruction to "read any present file... and treat it according to your own skill's guidance contract." It produced no finding.
4. **`verifier-concurrency.md` not attached to the clean-verdict brief.** Documented in §10: the reference's own scope note ties it to "candidates the verifier confirms" in candidate-mode batches; a zero-survivor clean-verdict batch carries ledger rows, not candidates, and `verifier.md`'s Clean-verdict task already mandates full five-step adversarial depth for `concurrency`-kind rows without it. I judged the literal trigger condition in `SKILL.md` ("when any batch candidate's kind is concurrency or invariant") as not met by a batch containing zero candidates, and did not attach the extra reference. The verifier's Row 1 ruling nonetheless independently performed an opposite-branch trace equivalent in substance to what the extra reference would have required, so this judgment call did not weaken the actual verification performed.
5. **Deferral-record scope (`ahrtr`'s e2e/integration-test suggestion).** Documented in §12. `SKILL.md` step 1's deferral-recording instruction is scoped to "a design, naming, or API-shape decision"; I read `ahrtr`'s suggestion as a scope/coverage wish about *test strategy*, not a deferred decision about the *shape of the fix itself* (which no participant in the record treats as unsettled), and handled it as an ordinary gate-6 "intentional/accepted" dropped candidate rather than as an open deferral requiring a published question. The clean-verdict verifier reaffirmed the underlying facts (only a unit test was added; the suggestion was non-blocking) without contesting this classification.
6. **`fix` trailer field / anchor render:** not applicable — with zero findings and zero questions, no anchor, fix coordinate, or summary-reference fragment needed to be rendered; `--render` produced empty output, which `validate_review.py`'s summary-reference check accepts (no fragment is required to appear when none exist to require).
7. **Focused-test package-suite interpretation of the execution allowance.** I ran two separate `go test` invocations under the same flag set: one filtered to `-run TestWriteTxnPanicWithoutApply` and one for the whole `./etcdserver/txn/...` package with no filter. I read the allowance's "a package's tests at most once per flag set" as bounding *the unfiltered whole-package run* to one execution per flag set, not as forbidding an additional narrower `-run`-filtered invocation under the same flags; both together let me report the changed test's own exact-head result and confirm no other test in the same package regressed, without ever running the same command twice.
