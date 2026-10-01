# Review packet — `etcd-io/etcd#18749` (target (h), issue #124 effort experiment)

Phase 1 (target resolution) has already been performed by the orchestrator and is reproduced here in
full. **Do not attempt to re-resolve the target over the network — you have no network access.**
Treat every fact in this packet as authoritative pinned input. This packet is byte-identical for every
arm and replicate on this target.

## 1. Pinned run identity

| | |
| --- | --- |
| Pull request | [`etcd-io/etcd#18749`](https://github.com/etcd-io/etcd/pull/18749) — "Fix risk of a partial write txn being applied" |
| Author | `shyamjvs` (association at fetch time: `CONTRIBUTOR`) |
| Repository URL (`summary.repository_url`) | `https://github.com/etcd-io/etcd` |
| Head SHA | `8a0fd66db3291bd6397a1341dc07ad41294a3caf` (local branch `review-head`, checked out) |
| Base ref | `main` (local branch `main`, force-pinned to the merge-base) |
| Base SHA (as recorded on the pull request) | `bb381d473c24ff2cd771f109c63443e03ac459c2` |
| Merge-base | `bb381d473c24ff2cd771f109c63443e03ac459c2` (identical to the base SHA) |
| Diff | 2 files, +34 / −7, 1 commits |
| `state` | `MERGED` |
| `merged` | **`true`** (merged 2024-10-24T09:25:08Z) |
| `isDraft` | `false` |
| Originating issue(s) | [`etcd-io/etcd#18679`](https://github.com/etcd-io/etcd/issues/18679) — "Write txn shouldn't End() on a failure" (closing reference in the PR body) |
| Posting identity | `kamui`, who did NOT author the PR and has no prior comments or reviews on it → an ordinary first review by a third party, event `COMMENT`; the target is merged, so this is a **retrospective review with publication disabled** |

Compute the diff as `git diff main review-head` (the `main` branch is pinned to the merge-base, so two-dot and three-dot are identical here).

## 2. Changed-file manifest (verified against the pinned SHAs from the mirror)

```
M  server/etcdserver/txn/txn.go                                           (+5    −4)
M  server/etcdserver/txn/txn_test.go                                      (+29   −3)
```

## 3. Pull-request body, verbatim

```
Fixes https://github.com/etcd-io/etcd/issues/18679

I was able to confirm this risk exists based on the unit test failing with txnWrite.End() still around. I did have to add a few milliseconds of wait time between the txn End and panic to reliably reproduce it because it depends on whether backend commit happens in that window or not.

/cc @serathius @ahrtr 
```

## 4. Originating issue `etcd-io/etcd#18679`, verbatim

Title: **Write txn shouldn't End() on a failure**  
Opened 2024-10-05 by `shyamjvs`.

```
### What happened?

Offshoot of https://github.com/etcd-io/etcd/issues/18667#issuecomment-2394848548

When two nodes both execute the same write txn (i.e validation step already passed on both), but one ends up in failed execution and the other in success, we shouldn't let the failed node increment its CI and move on - but explicitly fail and crash at the old CI - because we [never expect a write txn to fail](https://github.com/etcd-io/etcd/blob/c1976a67172fff1e63ee1b0117d34e8be8c35b45/server/etcdserver/txn/txn.go#L312-L313). Otherwise it would cause asymmetric side-effect across nodes and lead to data inconsistency.

Here's where I think our code may be potentially violating that:

https://github.com/etcd-io/etcd/blob/c1976a67172fff1e63ee1b0117d34e8be8c35b45/server/etcdserver/txn/txn.go#L307-L314

If I'm reading that correctly, when we run into a txn failure (which may contain some partially executed writes) the txn is ended **before** triggering server panic - which means there could be a KV rev and CI bump with some incorrect changes. So if/when the server restarts, it will assume it's caught up (till that badly applied txn) and move on to the next record leading to inconsistent state. Reproducing such failure is going to be hard iiuc but it seems like we should panic without calling txn.End here?

### What did you expect to happen?

The etcd node on which write txn execution fails should crash without trying to commit the failed transaction (or other side effects like incrementing KV revision or CI).

### Anything else we need to know?

There was no observed failure or a confirmed repro I have for this issue, but bringing it up as a potential risk in our current code.

Please share any thoughts about making the above change/trying to repro or if you think this is a non-issue.
/cc @serathius @ahrtr 
```

### Issue comments through the frozen cutoff `2024-10-24T09:25:08Z`, verbatim, in order (7 total; `comments_available: true`)

**1.** 2024-10-05T10:30:30Z · `serathius`

```
Context why this was introduced https://github.com/etcd-io/etcd/pull/14149
```

**2.** 2024-10-07T20:39:41Z · `shyamjvs`

```
As I read through that change, it seems the goal was to make timeouts of read-only txns not cause panic. But the change also makes undesirable side-effect of letting the partial-write end before panic.
```

**3.** 2024-10-07T20:50:46Z · `shyamjvs`

```
This comment from @ptabor was quite relevant actually (the miss seems to be to not panic right away):

> I have small preference towards apply workflow being extremely strict and deterministic and any unexpected error causing premature exit from function (even in RO) code is something that should lead to investigation and fixing.

@ahrtr - please share any add'l context you might have from that PR - or I can make a change to remove txn.End and test
```

**4.** 2024-10-08T13:20:59Z · `ahrtr`

```
Thanks @shyamjvs for the good catch.  Right, we need to remove the `txnWrite.End()`, otherwise the data might be partially committed into the backend storage (bbolt) before panicking. cc @lavacat 

https://github.com/etcd-io/etcd/blob/f1aefa5e90f1c69236a0c71a7d37814aa538fcc4/server/etcdserver/txn/txn.go#L310-L311
```

**5.** 2024-10-08T13:25:04Z · `serathius`

```
Looks like a good place for a failpoint.
```

**6.** 2024-10-17T23:05:23Z · `shyamjvs`

```
Sorry this took a while, I sent out a fix above.

@serathius I'm happy to add failpoints too, but had a few questions first around how to make them effective. Could we discuss over a call (maybe next SIG sync)?
```

**7.** 2024-10-18T08:52:50Z · `serathius`

```
See example in https://github.com/etcd-io/etcd/pull/17555
```

## 5. Commits on the head, oldest first — messages verbatim

| # | SHA | Date | Author | Message |
| --- | --- | --- | --- | --- |
| 1 | `8a0fd66db` | 2024-10-22 | Shyam Jeedigunta | Fix risk of a partial write txn being applied<br><br>Signed-off-by: Shyam Jeedigunta <jeedigv@amazon.com> |

> **Mandatory note, same class as prior packets in this program.** Where later commits on the head
> applied the author's responses to earlier review rounds, that feedback is already fixed in the reviewed
> head and must not be rediscovered and reported as still outstanding. Read the prior-review section
> below against the head before treating any earlier comment as live.

## 6. Prior review state through the frozen cutoff `2024-10-24T09:25:08Z` (the merge instant), reproduced verbatim

### Review submissions (12)

| When | Who | State | On commit | Body |
| --- | --- | --- | --- | --- |
| 2024-10-18T08:47:17Z | `serathius` | COMMENTED | `` | *(empty)* |
| 2024-10-18T12:20:16Z | `ahrtr` | COMMENTED | `` | *(empty)* |
| 2024-10-18T12:33:20Z | `mmorel-35` | COMMENTED | `` | *(empty)* |
| 2024-10-18T17:09:58Z | `shyamjvs` | COMMENTED | `` | *(empty)* |
| 2024-10-18T17:41:17Z | `shyamjvs` | COMMENTED | `` | *(empty)* |
| 2024-10-18T20:27:23Z | `fuweid` | COMMENTED | `` | *(empty)* |
| 2024-10-18T20:30:09Z | `fuweid` | COMMENTED | `` | *(empty)* |
| 2024-10-18T21:28:21Z | `chaochn47` | COMMENTED | `` | *(empty)* |
| 2024-10-19T21:10:53Z | `shyamjvs` | COMMENTED | `` | *(empty)* |
| 2024-10-20T08:23:30Z | `ahrtr` | APPROVED | `` | LGTM<br><br>Thanks @shyamjvs <br><br>Ideally it would be great if we could create an e2e or integration test to reproduce the partially committed/persisted issue. |
| 2024-10-20T08:25:00Z | `ahrtr` | COMMENTED | `` | *(empty)* |
| 2024-10-24T09:23:50Z | `serathius` | APPROVED | `8a0fd66db` | *(empty)* |

### Review threads (4), comments verbatim, in order

**1.** 2024-10-18T08:47:17Z · `serathius` · `server/etcdserver/txn/txn_test.go:380` · on commit `` · thread unresolved

```
Is there a need to defer? `assert.Panics` should handle panic?
```

**2.** 2024-10-18T12:20:09Z · `ahrtr` · `server/etcdserver/txn/txn_test.go:380` · on commit `` · thread unresolved

```
Did not follow @serathius 's comment above. 

- The purpose here is to verify the hash of the db did not change after the panicking. It's good!
- When panicking happens, any functions [deferred](https://go.dev/ref/spec#Defer_statements) are then executed as usual
```

**3.** 2024-10-18T17:09:57Z · `shyamjvs` · `server/etcdserver/txn/txn_test.go:380` · on commit `` · thread unresolved

```
that's correct, test function stops executing after assert.panic - so further verification needs to happen either inside a defer or a t.Cleanup() 
```

**4.** 2024-10-18T20:27:23Z · `fuweid` · `server/etcdserver/txn/txn_test.go:380` · on commit `` · thread unresolved

```
I think what @serathius said is that the `assert.Panics` is capable to recover the panic. there is no need to use defer.
We should check the hash after `assert.Panics`. 
```

**5.** 2024-10-18T20:30:09Z · `fuweid` · `server/etcdserver/txn/txn_test.go:380` · on commit `` · thread unresolved

```
FYI https://github.com/stretchr/testify/blob/bb548d0473d4e1c9b7bbfd6602c7bf12f7a84dd2/assert/assertions.go#L1190-L1205
```

**6.** 2024-10-18T21:27:55Z · `chaochn47` · `server/etcdserver/txn/txn_test.go:380` · on commit `` · thread unresolved

```
Shyam - if the initial intended further assertion requires opening a bbolt file, it is protected by the advisory flock so it appears that so further verification could be added after `assert.Panics`. 

However, this advisory lock does not block you from opening the file and perform checksum. 
```

**7.** 2024-10-19T21:10:53Z · `shyamjvs` · `server/etcdserver/txn/txn_test.go:380` · on commit `` · thread unresolved

```
sorry I stand corrected - the test indeed continues after the assert (the defer pattern was a remnant from earlier when I was calling Txn() directly without an assert) 

however, the test still got stuck after adding the assert because of the `defer betesting.Close(t, b)` at the start of the function, because it tries to write to an unbuffered channel [here](https://github.com/etcd-io/etcd/blob/3869f0e77dce84fc3da8d9385927fcdff6c87169/server/storage/backend/backend.go#L446) that is no longer read from anywhere

fixed both now, thanks!
```

**8.** 2024-10-20T08:24:59Z · `ahrtr` · `server/etcdserver/txn/txn_test.go:380` · on commit `` · thread unresolved

```
> I think what @serathius said is that the `assert.Panics` is capable to recover the panic. there is no need to use defer.

thx for the clarification. `defer` is still a good pattern for such case, but not a big deal though.
```

**9.** 2024-10-18T12:15:30Z · `ahrtr` · `server/etcdserver/txn/txn_test.go:377` · on commit `` · thread resolved

```
Please use `require.NoErrorf`.

cc @mmorel-35
```

**10.** 2024-10-18T12:16:24Z · `ahrtr` · `server/etcdserver/txn/txn_test.go:387` · on commit `` · thread resolved

```
ditto, pls use `require.NoErrorf`
```

**11.** 2024-10-18T12:17:33Z · `ahrtr` · `server/etcdserver/txn/txn_test.go:390` · on commit `` · thread resolved

```
What's the recommendation here? `require.Equalf` ? cc @mmorel-35
```

**12.** 2024-10-18T12:33:20Z · `mmorel-35` · `server/etcdserver/txn/txn_test.go:390` · on commit `` · thread resolved

```
Exactly :) ! 
assert would be for t.Error
```

**13.** 2024-10-18T17:41:17Z · `shyamjvs` · `server/etcdserver/txn/txn_test.go:390` · on commit `` · thread resolved

```
thanks for this suggestion - made it much cleaner
```

### Non-review conversation (7), verbatim, in order

**1.** 2024-10-17T22:59:06Z · `k8s-ci-robot`

```
Hi @shyamjvs. Thanks for your PR.

I'm waiting for a [etcd-io](https://github.com/orgs/etcd-io/people) member to verify that this patch is reasonable to test. If it is, they should reply with `/ok-to-test` on its own line. Until that is done, I will not automatically test new commits in this PR, but the usual testing commands by org members will still work. Regular contributors should [join the org](https://github.com/etcd-io/etcd/blob/main/CONTRIBUTING.md) to skip this step.

Once the patch is verified, the new status will be reflected by the `ok-to-test` label.

I understand the commands that are listed [here](https://go.k8s.io/bot-commands?repo=etcd-io%2Fetcd).

<details>

Instructions for interacting with me using PR comments are available [here](https://git.k8s.io/community/contributors/guide/pull-requests.md).  If you have questions or suggestions related to my behavior, please file an issue against the [kubernetes-sigs/prow](https://github.com/kubernetes-sigs/prow/issues/new?title=Prow%20issue:) repository.
</details>
```

**2.** 2024-10-17T23:47:05Z · `codecov-commenter`

````
## [Codecov](https://app.codecov.io/gh/etcd-io/etcd/pull/18749?dropdown=coverage&src=pr&el=h1&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=etcd-io) Report
:white_check_mark: All modified and coverable lines are covered by tests.
:white_check_mark: Project coverage is 68.72%. Comparing base ([`bb381d4`](https://app.codecov.io/gh/etcd-io/etcd/commit/bb381d473c24ff2cd771f109c63443e03ac459c2?dropdown=coverage&el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=etcd-io)) to head ([`aa8c785`](https://app.codecov.io/gh/etcd-io/etcd/commit/aa8c7852b4557e3f6bbf86aa8c9c5e7be18c3ec1?dropdown=coverage&el=desc&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=etcd-io)).
:warning: Report is 2625 commits behind head on main.

:warning: **Current head aa8c785 differs from pull request most recent head 8a0fd66**

Please [upload](https://docs.codecov.com/docs/codecov-uploader) reports for the commit 8a0fd66 to get more accurate results.

<details><summary>Additional details and impacted files</summary>



| [Files with missing lines](https://app.codecov.io/gh/etcd-io/etcd/pull/18749?dropdown=coverage&src=pr&el=tree&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=etcd-io) | Coverage Δ | |
|---|---|---|
| [server/etcdserver/txn/txn.go](https://app.codecov.io/gh/etcd-io/etcd/pull/18749?src=pr&el=tree&filepath=server%2Fetcdserver%2Ftxn%2Ftxn.go&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=etcd-io#diff-c2VydmVyL2V0Y2RzZXJ2ZXIvdHhuL3R4bi5nbw==) | `92.69% <ø> (-0.46%)` | :arrow_down: |

... and [18 files with indirect coverage changes](https://app.codecov.io/gh/etcd-io/etcd/pull/18749/indirect-changes?src=pr&el=tree-more&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=etcd-io)

```diff
@@            Coverage Diff             @@
##             main   #18749      +/-   ##
==========================================
+ Coverage   68.68%   68.72%   +0.03%     
==========================================
  Files         420      420              
  Lines       35504    35503       -1     
==========================================
+ Hits        24385    24398      +13     
+ Misses       9685     9667      -18     
- Partials     1434     1438       +4     
```

------

[Continue to review full report in Codecov by Sentry](https://app.codecov.io/gh/etcd-io/etcd/pull/18749?dropdown=coverage&src=pr&el=continue&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=etcd-io).
> **Legend** - [Click here to learn more](https://docs.codecov.io/docs/codecov-delta?utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=etcd-io)
> `Δ = absolute <relative> (impact)`, `ø = not affected`, `? = missing data`
> Powered by [Codecov](https://app.codecov.io/gh/etcd-io/etcd/pull/18749?dropdown=coverage&src=pr&el=footer&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=etcd-io). Last update [bb381d4...8a0fd66](https://app.codecov.io/gh/etcd-io/etcd/pull/18749?dropdown=coverage&src=pr&el=lastupdated&utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=etcd-io). Read the [comment docs](https://docs.codecov.io/docs/pull-request-comments?utm_medium=referral&utm_source=github&utm_content=comment&utm_campaign=pr+comments&utm_term=etcd-io).
</details>
<details><summary> :rocket: New features to boost your workflow: </summary>

- :snowflake: [Test Analytics](https://docs.codecov.com/docs/test-analytics): Detect flaky tests, report on failures, and find test suite problems.
</details>
````

**3.** 2024-10-18T12:20:54Z · `ahrtr`

```
/ok-to-test
```

**4.** 2024-10-20T08:23:55Z · `ahrtr`

```
@shyamjvs Please signoff the commit. Please read https://github.com/etcd-io/etcd/pull/18749/checks?check_run_id=31776671478
```

**5.** 2024-10-21T01:16:05Z · `shyamjvs`

```
done - thanks @ahrtr 
```

**6.** 2024-10-22T23:25:55Z · `shyamjvs`

```
/retest
```

**7.** 2024-10-24T09:23:57Z · `k8s-ci-robot`

```
[APPROVALNOTIFIER] This PR is **APPROVED**

This pull-request has been approved by: *<a href="https://github.com/etcd-io/etcd/pull/18749#pullrequestreview-2380245108" title="Approved">ahrtr</a>*, *<a href="https://github.com/etcd-io/etcd/pull/18749#pullrequestreview-2391865999" title="Approved">serathius</a>*, *<a href="https://github.com/etcd-io/etcd/pull/18749#" title="Author self-approved">shyamjvs</a>*

The full list of commands accepted by this bot can be found [here](https://go.k8s.io/bot-commands?repo=etcd-io%2Fetcd).

The pull request process is described [here](https://git.k8s.io/community/contributors/guide/owners.md#the-code-review-process)

<details >
Needs approval from an approver in each of these files:

- ~~[OWNERS](https://github.com/etcd-io/etcd/blob/main/OWNERS)~~ [ahrtr,serathius]

Approvers can indicate their approval by writing `/approve` in a comment
Approvers can cancel approval by writing `/approve cancel` in a comment
</details>
<!-- META={"approvers":[]} -->
```

## 7. Repository guidance present at the merge-base

Verified by direct lookup in the mirror. Path-scoped `AGENTS.md`/`CLAUDE.md` in every ancestor directory of a changed path were checked; only rows that exist or are the standard root candidates are listed.

| Path | Present at merge-base | Blob |
| --- | --- | --- |
| `AGENTS.md` | no | — |
| `CLAUDE.md` | no | — |
| `CONTEXT.md` | no | — |
| `CONTRIBUTING.md` | **yes** | `ab08d3ab2ce256500a969651b1f70c7f6e8b0be9` |
| `CODEOWNERS` | no | — |
| `.github/CODEOWNERS` | no | — |
| `.github/PULL_REQUEST_TEMPLATE.md` | **yes** | `48dc1a253d48c58000deb405af47998ad484857a` |
| `.github/pull_request_template.md` | no | — |

Read any present file from the clone with `git show <base-branch>:<path>` and treat it according to your own skill's guidance contract; record how you classified it.

## 8. Run conditions — binding on this run and on every sub-agent you spawn

1. **Offline.** Your clone's `origin` points at a local filesystem path, not `github.com`. No
   `git fetch`, no `git pull`, no `gh`, no `curl`, no web fetch, no network call of any kind, by you
   or by any sub-agent. If your skill's phase 1 asks you to resolve the target from the forge, that
   phase is satisfied by this packet, including its `merged` field.
2. **Execution allowance.** Focused test execution IS permitted on this target, offline, using go commands from the clone's server/ module with GOMODCACHE=/tmp/effort124/gomodcache GOCACHE=/tmp/effort124/gocache GOFLAGS=-mod=mod GOPROXY=off, five minutes per command, a package's tests at most once per flag set, scratch modules only under your work directory, nothing added to or changed in the clone. Your own skill's helper scripts are always
   permitted; run them from the skill directory.
3. **History is truncated at the pinned head on purpose.** The newest object reachable in your clone
   is `8a0fd66db`. Nothing that happened after this pull request exists locally. Do not try to work
   around this. At the end, report explicitly whether you read any history beyond the pinned head and
   which history commands you ran.
4. **Publication is disabled.** The target is merged; this is a retrospective review. Do not post
   anything anywhere. Follow your skill through to the point where it would publish, then render the
   review **exactly as it would be posted**, including summary body (with the `Mode` line your
   contract requires for a merged target), per-finding comments, and any trailers, and stop.
5. **Follow your own skill as written** — its phase structure, its fan-out policy, its verification
   triggers, its output contract. Do not borrow behavior from any other review skill. Where the skill
   tells you to spawn sub-agents, spawn them with the `Agent` tool and **pass `model: "sonnet"`
   explicitly on every call**.
6. **Persist before you verify.** Write the expensive phase to your report file before dispatching
   any verifier or finder: the manifest and requirement ledger when they are complete, then the
   complete candidate ledger with every disposition, then the verifier prompts and verbatim reports as
   they arrive. A session interruption after that point loses nothing that the file holds.
7. **Stay in your own sandbox.** Your clone, your skill snapshot, this packet directory, and your
   own report and payload paths only. Do not read any other run's clone, report, or payload. Report
   it if you read one anyway.
