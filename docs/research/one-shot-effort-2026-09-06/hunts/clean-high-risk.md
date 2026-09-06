# Clean high-risk PR hunt

Program exclusions honored: hyperium/hyper#3952, hashicorp/raft#581, python/typeshed#9458,
astral-sh/uv#4424, pola-rs/polars#24771, spf13/cobra#1938, microsoft/playwright#29698,
tokio-rs/tokio#7757, redis/redis#15680, kamui/shortlist#66, and no other PR from those
repos was considered.

"Today" for freshness math = 2026-09-06 (per environment clock). "Merged >=6 months ago"
means merged before 2026-03-06.

---

## Candidate A (previously considered, DISQUALIFIED on freshness): etcd-io/bbolt#1179

**Repo / PR**: etcd-io/bbolt, PR #1179, "freelist/hashmap: batch contiguous IDs when merging
free spans". Author: fuweid (Fu Wei, MEMBER). Base branch: `main`. Merged: 2026-04-07T14:41:59Z.

**VERDICT UP FRONT**: This PR is only about 5 months old as of 2026-09-06, not the required
6+. It is disqualified for the clean-high-risk slot on freshness grounds alone. Documented in
full below anyway, per instructions, since it was one of the two named alternates to vet.

**SHAs**: head `a8d9885e9b53a92e159f286278bceec23582dbed`, PR-recorded base
`cae11e99175482a679eab5f4702c84db96633258`, merge commit `36efe3ee12b5ef4d2ba79a3756d4713efdc4b7ee`.
`git merge-base cae11e99... a8d9885e...` = `417c4eee6a987a528b4a62cb291a26000627019e`, which is
**not** equal to the recorded base SHA — the PR branch was rebased/updated onto a newer `main`
between creation and merge (main moved from `cae11e99` to `417c4ee` in the interim; the PR was
not itself force-pushed with unrelated history, `417c4ee` is a normal ancestor commit bump).

**Changed-file manifest** (2 files, +173/-25 total):
- `internal/freelist/hashmap.go`: +27/-13
- `internal/freelist/hashmap_test.go`: +146/-12

**Originating issue**: none — `closingIssuesReferences` is empty; this was an unsolicited
performance PR with benchmark data in the PR body, not tied to a filed issue.

**Prior review record**: Very thin. One formal GitHub review (ahrtr, APPROVED, comment "Nice
improvement. Please also update the 1.5 changelog, thx"). One informal PR comment from
tjungblu: "very elegant and drops the allocations a lot, great work. /lgtm". No human reviewer
raised the tempting objection identified below — the review was a fast rubber-stamp on a
change whose correctness argument is genuinely non-obvious. Author self-approved per the
k8s-style OWNERS bot. A follow-up PR #1186 added the changelog entry the reviewer asked for.

**Post-merge cleanliness evidence**: `git log --oneline --since=2026-04-07 -- internal/freelist/hashmap.go`
on `main` shows only the merge commit itself — no later commit has touched this file.
`gh api search/issues` for `mergeWithExistingSpan`, `mergeSpans`, and `"#1179"` in
etcd-io/bbolt turns up only the PR itself, an unrelated 2024-era verification issue (#772,
already closed long before this PR), and unrelated dependency/release housekeeping issues.
**No later fix references or repairs this PR.** Caveat: because the PR is only ~5 months old,
this is a short observation window compared to the program's 6-month bar, so the absence of a
fix is weaker evidence here than it would be for an older PR.

**Tempting-but-false objections a reviewer might raise**:
1. *"Moving `sort.Sort(ids)` out of the `common.Verify(...)` closure means it now always runs,
   permanently adding sort overhead to a hot path where it never used to run at all in
   production."* (`internal/freelist/hashmap.go:172-176` new code; the old `sort.Sort(ids)` sat
   inside `common.Verify(func(){...})` at old line ~184). This is **true as a description**
   but **false as an objection to correctness or intent** — `common.Verify` is gated by the
   `BBOLT_VERIFY` env var (see `internal/common/verify.go:56` / `IsVerificationEnabled`), off by
   default, so the debug block's sort was never doing real work in production; the *new*
   algorithm's contiguous-range batching (`start`/`end` walk) requires ids to be sorted to
   correctly detect adjacency, so the unconditional sort is not a regression, it's a
   newly-introduced correctness requirement the author correctly wired up. The included
   benchmarks show the added sort's cost is roughly break-even for span=1 and a net win for
   any longer contiguous run, which is the common case this PR targets.
2. *"The callers of `mergeSpans` (`shared.go:161` `release`, `shared.go:186` `releaseRange`)
   build the `ids` slice by iterating a Go map (`t.pending`) and by swap-removing entries out of
   a slice in `releaseRange`, both of which scramble ordering — so an unsorted-input assumption
   anywhere in the new code would be a landmine."* False as a defect claim: the new
   `mergeSpans` sorts unconditionally as its very first step (`sort.Sort(ids)` before any
   batching), so caller ordering is irrelevant; this was verified by reading `array.go`/`shared.go`
   call sites and confirming no caller relies on `mergeSpans` preserving input order.
3. *"Duplicate pgids in `ids` (which the debug-only assertion in `common.Verify` calls a bug)
   could break the new batching in a way the old per-id loop didn't."* False: duplicates were
   already an assumed-absent invariant pre-PR (the old code's per-id `mergeWithExistingSpan`
   would double-process a duplicate exactly as the new batched version would); this PR neither
   introduces nor worsens that pre-existing invariant reliance.

**Tests**: `go test ./internal/freelist/...` and `go test -race ./internal/freelist/...` both
pass at `main` HEAD in a temp clone (`/tmp/bboltclone`, deleted after this run). Runtime: ~1.8s
plain, ~4.0s with `-race`. Requires network for `go mod download` (`stretchr/testify`,
`go.yaml.in/yaml/v3`) on a clean module cache; otherwise no network needed. New tests in
`hashmap_test.go` (`test5`, `test6`) specifically exercise multi-gap batched merges, which is
exactly the scenario the tempting objections above are about, and they pass.

**Why reasoning-heavy**: The change touches bbolt's freelist, i.e. the free-page bookkeeping
for a durable on-disk B+tree store used by etcd itself — corrupting this data structure would
misattribute live pages as free (data corruption) or vice versa (space leak). The single most
load-bearing line in the diff is moving one `sort.Sort` call from inside a disabled-by-default
debug hook to unconditional execution; superficially this looks like "oops, now it always
sorts" but is in fact the fix that *makes the new batching algorithm correct*, and requires
tracing `common.Verify`'s env-var gating plus every caller's ordering guarantees to see that.
That is exactly the shape of a false-but-tempting objection.

**Why it might NOT be clean**: I did not find a defect. The remaining risk is purely the
freshness one — 5 months of `main` history since merge, plus no downstream consumer report
(bbolt is release-cut into etcd, and etcd's own bbolt bump history was not checked here), is a
shorter track record than the program wants. Treat as "clean so far, insufficiently aged."

---

## Candidate B (previously considered, QUALIFIES on freshness, weak on reasoning-heaviness): golang-jwt/jwt#456

**Repo / PR**: golang-jwt/jwt, PR #456, "Add `WithNotBeforeRequired` parser option and add test
coverage". Author: equalsgibson (Chris Gibson, CONTRIBUTOR). Base branch: `main`. Merged:
2025-08-07T06:01:43Z (≈13 months before 2026-09-06 — comfortably clears the 6-month bar).

**SHAs**: head `734a9292dbc587d5f0e7086af8e622d3541af21c`, PR-recorded base
`ce52acb322f4166c6f50543398a4b85993dd02fc`, merge commit `9d770c8525013476c8d8a56f06e7d3c61d405203`.
`git merge-base ce52acb3... 734a9292...` = `ce52acb322f4166c6f50543398a4b85993dd02fc` —
**equal to the recorded base**, so the branch was cleanly based on `main` at merge time, no
divergent rebase.

**Changed-file manifest** (3 files, +81/-2 total):
- `parser_option.go`: +8/-0
- `validator.go`: +6/-2
- `validator_test.go`: +67/-0

**Originating issue**: #455, "No ParserOption for requiring nbf claim", opened by the same
author (equalsgibson) with 1 comment from maintainer oxisto ("Makes sense. We might need to
split adding the functionality and providing more tests in your PR though").

**Prior review record**: 5 reviews/comments across two reviewers plus the author, over 6 days
(2025-08-01 to 2025-08-07). Two `APPROVED` reviews (oxisto "LGTM"; mfridman, MEMBER, silent
approve). One substantive line-comment thread on `validator_test.go`: reviewer equalsgibson
(self-review) flagged that the added tests called the *private* `verifyNotBefore` method
directly rather than the public `Validate()` entry point, so setting a custom `timeFunc` on the
`Validator` had no effect on the test's outcome (the private method takes `cmp` as an explicit
parameter instead of consulting `timeFunc` itself). Maintainer oxisto's reply: "hm yeah this a
little bit of a problem since the `validateXXX` functions take a `cmp` as an extra parameter
... I wonder if there is a better way to do this ... Probably it would make sense to change
this first and then adapt the tests." This objection was **true**, not tempting-but-false: it
identified a genuine test-design smell, and the author reworked the tests in response
(commit `703b7e0` "Remove changes to testing format, and timefuncs"). No reviewer raised a
false objection about the actual behavior change.

**Post-merge cleanliness evidence**: `git log --since=2025-08-07 -- validator.go
parser_option.go` on `main` shows exactly two later commits touching these files: #484
("Remove misleading ParserOptions documentation", a comment-only edit to `parser_option.go`
unrelated to `WithNotBeforeRequired`) and #510 ("fix: extended token expiry message with
duration", which edits `verifyExpiresAt`'s error message, not `verifyNotBefore`/`requireNbf`).
`gh api search/issues` for `requireNbf` and `WithNotBeforeRequired` across the repo returns
only PR #456 itself. **No later fix references or repairs this PR.**

**Tempting-but-false objections a reviewer might raise**:
1. *"`Validator.requireNbf` is a new unexported bool field with zero value `false` — any code
   constructing `Validator{}` by struct literal instead of via `NewValidator(...)` now behaves
   differently."* False: Go's zero value for `bool` is `false`, which is exactly the pre-PR
   hardcoded behavior (`validator.go:117`, previously `v.verifyNotBefore(claims, now, false)`),
   so struct-literal construction is unaffected either way.
2. *"Making `nbf` required will now reject the many real-world tokens that omit `nbf` (RFC 7519
   marks it OPTIONAL), silently breaking existing verifiers when they upgrade."* False as a
   defect: `WithNotBeforeRequired()` is an opt-in `ParserOption` (`parser_option.go:69-74`); it
   changes nothing unless a caller explicitly requests it, mirroring the existing, uncontroversial
   `WithExpirationRequired()` pattern already in the library.
3. *"`verifyNotBefore`'s existing nil-check path (`nbf == nil` -> `errorIfRequired(required,
   "nbf")`) might not have been designed for `required=true`, since it was always called with
   `false` before this PR — untested code path."* False: `errorIfRequired` is the same
   general-purpose helper already exercised via `verifyExpiresAt`/`requireExp`, and this PR adds
   direct test coverage for the missing-and-required case (`Test_Validator_requireNotBefore`,
   `validator_test.go:265+`).

**Tests**: `go test ./...` at `main` HEAD in a temp clone (`/tmp/jwtclone`, deleted after this
run): passes, `ok github.com/golang-jwt/jwt/v5 0.492s` plus the `request` subpackage. Runtime
~1.1s total. `go.mod` declares no external dependencies (`go 1.21`, empty require block), so no
network is needed to run this package's tests once the repo is cloned — fully offline-capable.

**Why reasoning-heavy, honestly assessed**: It sits on a real security boundary (JWT claim
validation) and is genuinely clean — but the actual code change is close to mechanical: it
plumbs one already-proven boolean-toggle pattern (`requireExp`/`WithExpirationRequired`) through
to a second claim (`nbf`), and `verifyNotBefore`'s `required` parameter was already fully
general before this PR touched it. The one real point of friction in review was about test
methodology, not about a subtle correctness trap in the shipped behavior, so a "tempting but
false objection" is harder to manufacture honestly here than for Candidate A or the new
candidates below. I would rank this *clean* but *weakly* reasoning-heavy relative to the
program's target shape.

**Why it might NOT be clean**: No evidence found that it isn't. Only reservation is the
shallow reasoning-heaviness noted above, which is a fit concern, not a correctness concern.


---

## Candidate C (new): quic-go/quic-go#5220 — "fix deadlock when closing the Transport"

**Repo / PR**: quic-go/quic-go, PR #5220. Author: sukunrt (COLLABORATOR). Base branch:
`master`. Merged: 2025-06-24T11:55:42Z (≈14 months before 2026-09-06 — clears the 6-month bar).

**SHAs**: head `dca83d9270e45d49352463dc7dc0b9eb6f109eba`, PR-recorded base
`92aa7b41d54a66ebbc6e817e2e8d3f69619f8764`, merge commit `cf97a0a39c7fcd90ef0b8f78be772e284873a0b6`.
`git merge-base` of those two = the recorded base exactly — **no rebase divergence**.

**Changed-file manifest** (2 files, +31/-33 total): `server.go` +2/-0; `transport.go` +29/-33.

**Originating issue**: none filed on quic-go itself; the PR body links an external CI failure
in `libp2p/go-libp2p` (a downstream consumer) showing a real 9-minute goroutine deadlock in
production-shaped use (many concurrent `Transport.Dial` calls plus a `Transport.Close`).
Maintainer marten-seemann noted the original PR bundled two separable fixes and split the
second one out into follow-up PR #5237 (merged the same day) — #5237 is a sibling
feature/hardening addition (draining the server's accept queue on transport close), **not** a
repair of a defect in this PR.

**Prior review record**: Rich — 10 review rounds across 2 reviewers (sukunrt, marten-seemann)
over 15 days, with several substantive line comments (quoted in full below). This is a genuine
back-and-forth review, not a rubber stamp.

**Post-merge cleanliness evidence**: `git log --since=2025-06-24 -- transport.go server.go`
on `master` shows no commit besides #5220 and #5237 touching the deadlock-fix logic itself
(later commits are Go-version bumps, doc/API cleanups, and an unrelated OOB-capable-conn error
change). `gh api search/issues` for `"5220"` and `connMx` in quic-go/quic-go returns only #5220
and its sibling #5237. Searching `is:pr deadlock` in the repo turns up a long history of
*earlier* deadlock fixes in unrelated subsystems (crypto setup, streams, http3 server) and one
unrelated *open* enhancement issue (#4103, "limit concurrency when closing all connections")
whose only comment is the same maintainer restating the same design constraint this PR
codifies, not reporting a regression. **No later fix references or repairs this PR.**

**Tempting-but-false objections a reviewer might raise**:
1. *(This one was actually raised, by reviewer marten-seemann, on `transport.go:325`, the write
   `t.handlers[srcConnID] = conn` inside `doDial`):* **"Why is the mutex not needed here
   anymore?"** — looking at the diff, the two-line `t.connMx.Lock(); ...; t.connMx.Unlock()`
   wrapping that specific map write disappears entirely, and it looks unprotected. **False**:
   author's answer, confirmed by reading the surrounding function: "The mutex is acquired
   before on line 289. That mutex protects this map now." The PR unifies the previously-separate
   `t.mutex` and `t.connMx` into one `t.mutex` that is acquired earlier in `doDial` and released
   one line after the write shown in the diff (`t.mutex.Unlock()`), so the write is still fully
   covered by a held lock — the diff view alone hides that.
2. *"`t.close()` now unlocks/re-locks `t.mutex` mid-function around `server.close(e, false)` —
   that reopens a window for a second concurrent `Close()` caller to race in and run the body
   twice."* **False**: `t.closeErr = e` is set **before** the unlock, still under the original
   lock acquisition, so a concurrent caller that reacquires `t.mutex` in that window sees
   `closeErr != nil` and returns immediately; the check-and-set is atomic even though the rest
   of the cleanup isn't.
3. *"Unlocking `t.mutex` before `wg.Wait()` means the handler-map `range` loop above it is now
   reading `t.handlers` without the lock."* **False**: that `range` loop finishes in full, still
   under the lock, before the unlock line; the unlock is required in the *other* direction —
   each spawned `handler.destroy()` goroutine must reacquire `t.mutex` later to deregister
   itself, which is exactly the lock-ordering cycle that caused the original deadlock.
4. *(A real, not-false, tradeoff a reviewer did raise, included for honesty)*: marten-seemann
   flagged that holding `t.mutex` across `newClientConn`'s connection-struct initialization
   (`transport.go:325` region) widens the critical section and could hurt dial throughput under
   load. This is true, not a false alarm — but the author's mutex-profiling data (linked in the
   thread) showed the actual measured regression was small (mutex wait time in a 3-minute kubo
   run went from ~25ms to ~90ms; the per-critical-section hold time was unchanged), and the
   maintainer accepted the tradeoff explicitly rather than blocking the merge.

**Tests**: `go test ./...` at PR head in a temp clone (`/tmp/qgclone`, deleted after this run):
all packages pass, ~15s wall time, including `integrationtests/self` (11s) which exercises real
handshakes/close paths. `go test -race -run 'TestTransport|TestServer' .` also passes (~5.6s).
Pre-existing regression tests `TestTransportAndListenerConcurrentClose` and
`TestTransportAndDialConcurrentClose` (present before this PR, in `transport_test.go`) pass at
head. Caveat: **the PR itself adds no new test** — the two changed files are `server.go` and
`transport.go` only, so confidence in the fix rests on the pre-existing concurrent-close tests
plus the downstream libp2p CI report, not a new deterministic repro. Network needed for
`go mod download` (`qpack`, `x/sync`, `x/text`, etc.) on a clean module cache.

**Why reasoning-heavy**: This is a lock-consolidation fix for a real, externally-reported
production deadlock in a QUIC transport used by IPFS/libp2p. The single most misleading line
in the diff is the disappearance of an explicit lock/unlock pair around a map write that a
static, line-by-line diff read would flag as "lost protection," when in fact protection moved
to a wider, already-held critical section as part of merging two mutexes into one to fix an
inconsistent lock-ordering deadlock — the classic shape of "correct but looks wrong on the
diff." The genuine, unresolved-until-profiled tradeoff about widening the critical section adds
a second, honest layer of reasoning difficulty on top of the first.

**Why it might NOT be clean**: No evidence of a regression was found, but the fix shipped
without a new regression test, so absence-of-failure in existing tests is the only test-suite
signal; the real evidence of correctness is the absence of further deadlock reports against
`Transport.Close`/`doDial` in the following 14 months plus the (accepted, not free) throughput
tradeoff the maintainer knowingly signed up for.

---

## Candidate D (new, strongest): etcd-io/etcd#18749 — "Fix risk of a partial write txn being applied"

**Repo / PR**: etcd-io/etcd, PR #18749. Author: shyamjvs (CONTRIBUTOR). Base branch: `main`.
Merged: 2024-10-24T09:25:08Z (≈23 months before 2026-09-06 — comfortably clears the bar, and
gives the longest post-merge observation window of any candidate here).

**SHAs**: head `8a0fd66db3291bd6397a1341dc07ad41294a3caf`, PR-recorded base
`bb381d473c24ff2cd771f109c63443e03ac459c2`, merge commit `38c27a4f8d5e3766a41edbbf8145f03850542d96`.
`git merge-base` of those two = the recorded base exactly — **no rebase divergence**.

**Changed-file manifest** (2 files, +34/-7 total): `server/etcdserver/txn/txn.go` +5/-4;
`server/etcdserver/txn/txn_test.go` +29/-3.

**The change**: in the write-txn error path, replaces the pattern "call `txnWrite.End()` to
release locks, *then* `lg.Panic(...)`" with just `lg.Panic(...)` (no `End()`), adding a comment
explaining that ending the txn first risks letting a partially-executed write get committed to
the backend before the crash, which could desync replicas.

**Originating issue**: #18679, "Write txn shouldn't End() on a failure," opened by the same
author (shyamjvs), 9 comments, genuinely collaborative: serathius links the PR (#14149) that
introduced the original `End()`-before-panic call (for an unrelated read-only-timeout reason);
ptabor's remembered design principle ("apply workflow being extremely strict and deterministic
... any unexpected error causing premature exit ... should lead to investigation") is quoted;
ahrtr confirms the diagnosis ("we need to remove the `txnWrite.End()`, otherwise the data might
be partially committed into the backend storage (bbolt) before panicking").

**Prior review record**: 12 reviews from 6 distinct reviewers (serathius, ahrtr, mmorel-35,
fuweid×2, chaochn47, plus author), 12 line comments, mostly a real thread about test hygiene
(`assert.Panics` vs `require`, whether `defer` was still needed once the test asserts on the
panic itself) — resolved collaboratively, not about the core semantic change. ahrtr's approval
adds: "Ideally it would be great if we could create an e2e or integration test to reproduce the
partially committed/persisted issue" (a fair ask that wasn't fully done — see below).

**Post-merge cleanliness evidence — the deciding evidence for this candidate**: `git log
--since=2024-10-24 -- server/etcdserver/txn/txn.go` shows only refactor commits (splitting
files, protobuf-struct swaps, auth-check additions) that don't touch this logic; `git show`
of current `main` confirms the code is **unchanged and unreverted** nearly two years later. But
searching `gh api search/issues -f q='repo:etcd-io/etcd "18749"'` surfaces something better than
silence: a **documented, resolved false alarm** that is exactly this candidate's tempting
objection, raised for real:
- **Issue #21939** (2026-06-10, closed 2026-06-22): a contributor reported that
  `TestWriteTxnPanicWithoutApply` (the very test this PR added) leaks a goroutine — the
  backend's periodic `backend.run()` goroutine blocks forever on the `batchTx` mutex that the
  panicking write txn never released, because `End()` (which calls `tx.Unlock()`) is skipped on
  the panic path this PR introduced.
- **PR #21941** (closed, unmerged): added a `goleak`-based regression test
  (`TestWriteTxnPanicWithoutApply_deadlock`) proving the leak reproduces in-process.
  - **PR #21964** (closed, unmerged): proposed `defer txnWrite.End()` right after
  `txnWrite := kv.Write(trace)` so the lock is always released, "even on panic" — i.e., exactly
  reverting this PR's core idea.
- **Resolution**: maintainers fuweid and ahrtr investigated whether a *recovered* panic could
  ever keep the etcd process alive long enough for that leaked goroutine to matter in
  production. fuweid's testing showed the write-txn apply path runs through
  `schedule.fifo.executeJob`, which recovers the panic only to immediately re-panic with
  "execute job failed" — crashing the process regardless — and the read-only path panics with
  no recovery at all; no gRPC-layer panic-recovery middleware is wired into the apply path. The
  PR author (crawfordxx) concluded in their own words: **"Since the deadlock scenario requires
  a recovered panic that keeps the process alive (which does not happen here), the safety
  argument for `defer txnWrite.End()` does not hold. I'll close this PR."** The issue reporter
  closed #21939 the same way: **"It is designed to not [] release the lock when write txn
  panics, which avoids inconsistent db state."** Both follow-ups were closed **without
  merging**, and `main` still carries #18749's original code unchanged.

This is about as strong a "no later fix repairs this PR" verdict as this search can produce:
the community built a fix, proved it rested on a false premise, and discarded it on the record.

**Tempting-but-false objections a reviewer might raise** (all independently corroborated by
the #21939/#21964 saga above, not just my own analysis):
1. *"Removing `txnWrite.End()` before the panic leaks the backend `batchTx` lock forever —
   any other goroutine that later needs that lock will deadlock."* (`txn.go`, the `isWrite`
   error branch, and `server/storage/mvcc/kvstore_txn.go:209` `storeTxnWrite.End()`, which calls
   `tw.tx.Unlock()` and `tw.s.mu.RUnlock()`.) **True in isolation, false as a production
   concern**: `zap`'s own documented contract is that `Logger.Panic` "panics, even if logging at
   PanicLevel is disabled" (`go doc go.uber.org/zap.Logger.Panic`), and no `recover()` exists
   anywhere on etcd's real apply call path (`server/etcdserver/apply/backend.go` →
   `server/etcdserver/server.go` apply loop → `schedule.fifo.executeJob`, which recovers only to
   immediately re-panic and crash the process). The lock is never actually reused because the
   process that holds it is going down. It *does* leak inside a bare unit test that calls
   `assert.Panicsf` (which recovers the panic locally without crashing the test binary), which
   is a real, narrow, and ultimately accepted cost, not a production hazard.
2. *"A write txn and a read-only txn share this function; skipping `End()` on write failure but
   not on read failure is an inconsistent, easy-to-regress special case."* False as a defect:
   the `isWrite` branch panics (crashes) so cleanup is moot; the `else` (read-only) branch logs
   at `Error` and returns normally, so `End()` still runs via the unchanged code path a few
   lines below — verified by reading the full `if err != nil { if isWrite {...} else {...} }`
   block in `txn.go`.

**Tests**: `cd server && go test ./etcdserver/txn/...` and `go test -race
./etcdserver/txn/...` (module root is `server/go.mod`), run at PR head in a temp clone
(`/tmp/etcdclone2`, deleted after this run): both **pass** —
`ok go.etcd.io/etcd/server/v3/etcdserver/txn 0.742s` plain, `1.909s` with `-race`. Targeted this
package rather than `./...` given etcd's server module has a very large dependency graph
(protobuf, grpc, prometheus, bbolt, raft, jwt/v4, ~25+ modules); a `--filter=blob:none` partial
clone made an arbitrary-commit checkout impractically slow in this environment, a plain full
clone (~120MB) resolved it. Network needed for `go mod download` on a clean module cache.

**Why reasoning-heavy**: The change trades one failure mode (silent partial-write commit
causing cross-replica data inconsistency — the worse outcome for a distributed KV store) for
another that *looks* like a classic lock-leak bug on casual inspection, and doing so correctly
depends on tracing panic-recovery semantics through zap's public contract and etcd's apply
scheduler, not just reading the diff. The dynamic is unusually well-documented here: real
contributors, over a year after merge, independently found the "obvious" bug, built the
"obvious" fix, and only closed it after actually testing (not assuming) that etcd's panic path
has no recovery point.

**Why it might NOT be clean**: The only asterisk is ahrtr's own review request for an
integration/e2e test reproducing the "partial commit" scenario the PR fixes, which was never
delivered — coverage rests on the unit test plus the later goroutine-leak investigation, not on
an end-to-end repro of the original bug. That is a documentation/verification gap, not evidence
of a defect.

---

## Ranking and recommendation

1. **Best candidate: etcd-io/etcd#18749.** Longest clean track record (23 months, unreverted),
   the deepest and most concrete post-merge evidence of any candidate here (two independent
   follow-up PRs built and then deliberately discarded after real investigation), a precisely
   quotable tempting-but-false objection with primary-source corroboration on both sides of the
   argument, a small, fully-readable diff (34/-7 across 2 files) on an unambiguous
   data-integrity/durability boundary (a distributed KV store's apply path), and a locally
   confirmed passing test run (including `-race`).

2. **Backup: quic-go/quic-go#5220.** Comparably strong: 14 months clean, a real external
   (libp2p) production bug motivating it, dense review discussion including one *actually
   raised* tempting-but-false line objection with a clean resolution, and a fully-passing local
   test run (including `-race`) that I completed in full inside this session. Ranked second only
   because its own tests were not extended to cover the fixed scenario, and its "no defect"
   verdict rests on absence of new bug reports rather than a documented, resolved false-alarm
   trail as rich as etcd#18749's.

**Not recommended for the slot**: golang-jwt/jwt#456 is genuinely clean but too mechanical to
be reliably "reasoning-heavy" (see Candidate B). etcd-io/bbolt#1179 is an excellent
reasoning-heavy specimen but merged only ~5 months before 2026-09-06 and fails the 6-month
freshness bar outright (see Candidate A) — worth re-checking again after 2026-10-07 if the
program revisits it.
