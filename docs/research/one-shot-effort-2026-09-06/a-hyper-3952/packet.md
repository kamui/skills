# Review packet — `hyperium/hyper#3952` (holdout target (a))

Phase 1 (target resolution) has already been performed by the orchestrator and is reproduced here in
full. **Do not attempt to re-resolve the target over the network — you have no network access.**
Treat every fact in this packet as authoritative pinned input. This packet is byte-identical for every
arm and seed on this target.

## 1. Pinned run identity

| | |
| --- | --- |
| Pull request | [`hyperium/hyper#3952`](https://github.com/hyperium/hyper/pull/3952) — "fix(http1): poll_loop writes when ready" |
| Author | `lthiery` (association at fetch time: `CONTRIBUTOR`) |
| Repository URL (`summary.repository_url`) | `https://github.com/hyperium/hyper` |
| Head SHA | `f2aa734e5699a91fc20f1178e38af7b1e374bdbc` (local branch `review-head`, checked out) |
| Base ref | `master` (local branch `master`, force-pinned to the merge-base) |
| Base SHA (as recorded on the pull request) | `f9f8f44058745d23fa52abf51b96b61ee7665642` |
| Merge-base | `f9f8f44058745d23fa52abf51b96b61ee7665642` (identical to the base SHA) |
| Diff | 3 files, +270 / −2, 2 commits |
| `state` | `MERGED` |
| `merged` | **`true`** (merged 2025-11-10T14:51:16Z) |
| `isDraft` | `false` |
| Originating issue(s) | none — the PR body carries no closing reference; `issues=none` unless the dispatch supplies a spec |
| Posting identity | `kamui`, who did NOT author the PR and has no prior comments or reviews on it → an ordinary first review by a third party, event `COMMENT`; the target is merged, so this is a **retrospective review with publication disabled** |

Compute the diff as `git diff master review-head` (the `master` branch is pinned to the merge-base, so two-dot and three-dot are identical here).

## 2. Changed-file manifest (verified against the pinned SHAs from the mirror)

```
M  Cargo.toml                                                             (+6    −0)
M  src/proto/h1/dispatch.rs                                               (+15   −2)
A  tests/ready_stream.rs                                                  (+249  −0)
```

## 3. Pull-request body, verbatim

```
I ran into some lockups running hyper with some custom futures. If one of my futures is ready when polled, the waker is never signaled and I think this uncovered a logical issue with the http1 poll_loop. That it to say, **if the poll_write is demonstrating readiness to write and the connection has readiness to write, we should do that or else hyper may stall**.

I built a pathological example "ready_stream.rs" - you can run it from this branch with: `RUSTFLAGS='--cfg hyper_unstable_tracing' cargo test --test ready_stream --features full,tracing`.

I provided a proposed patch for the poll_loop, but I'm open to other angles on this.
```

## 4. Originating issue

None. The pull-request body is the only statement of intent. Record `issues=none` (or the coordinate of a spec the dispatch supplies).

## 5. Commits on the head, oldest first — messages verbatim

| # | SHA | Date | Author | Message |
| --- | --- | --- | --- | --- |
| 1 | `7ed95afcb` | 2025-09-11 | Louis Thiery | tests(ready_stream): ready_stream as pathological example |
| 2 | `f2aa734e5` | 2025-09-11 | Louis Thiery | fix(http1): poll_loop writes when ready |

> **Mandatory note, same class as prior packets in this program.** Where later commits on the head
> applied the author's responses to earlier review rounds, that feedback is already fixed in the reviewed
> head and must not be rediscovered and reported as still outstanding. Read the prior-review section
> below against the head before treating any earlier comment as live.

## 6. Prior review state (all pre-merge; reproduced verbatim)

### Review submissions (3)

| When | Who | State | On commit | Body |
| --- | --- | --- | --- | --- |
| 2025-10-28T14:42:51Z | `seanmonstar` | COMMENTED | `f2aa734e5` | Thanks for looking into this! This loop can be tricky, it was initially added to improve performance when multiple messages have been batched together. But the loop has a limit, since otherwise it could starve all other futures. (Tokio's cooperative budget can help here, but hyper doesn't assume it's Tokio.)<br><br>Looking close, I appreciate you cleaning up the mistake in here: since we're essentially "selecting" over read and write, we need to make sure both sides either registered a waker, or that we will poll again with the `yield_once` util. Thanks for the attention! |
| 2025-10-31T04:27:56Z | `lthiery` | COMMENTED | `f2aa734e5` | *(empty)* |
| 2025-11-10T14:47:34Z | `seanmonstar` | APPROVED | `f2aa734e5` | *(empty)* |

### Review threads (1), comments verbatim, in order

**1.** 2025-10-28T14:42:40Z · `seanmonstar` · `tests/ready_stream.rs:18` · on commit `f2aa734e5` · thread unresolved

```
I think my only comment for this fix is that if possible, a simpler unit test would be easier to understand and maintain in the future. Can that be done?
```

**2.** 2025-10-31T04:27:56Z · `lthiery` · `tests/ready_stream.rs:18` · on commit `f2aa734e5` · thread unresolved

```
It's a little difficult to simplify because I needed to create a future that would deterministically trigger this edge case.

What's "weird" about this future mock is that it can return Poll::Pending once, but then reach completion on a future poll without the waker being woken, so I don't think it ever happens in Tokio for example but it does happen (probabilistically) with my actual futures that this is modeling. And as far as I know it's no violation of the Futures contract to do so.

Anyway, I'm not sure I can create the situation with less or more simple code. That being said, maybe a fixture like this is generalizable for the project? Creating a "connection" that's purely channel based software could allow other edge cases to be explored. Partial reads and writes or different sequence of readiness.

All that being said, I'll still take another critical pass at what I've done here next week and I'll see what I can do to simplify.
```

### Non-review conversation (2), verbatim, in order

**1.** 2025-10-31T04:32:16Z · `lthiery`

```
It's an interesting loop and I think with this edge case handled it works well. It would be nice to expose the 16 as a config (as noted in the comments) and maybe I'll PR that later.

One thing that I considered while looking at it is that maybe doing some tricks with custom wakers could be nice? Similar to FuturesUnordered, the waker could indicate who is actually ready for polling. The juice is probably not worth the squeeze (or perhaps even an efficiency loss with all the bookkeeping?) as I know FuturesUnordered is intended for some level of scale and three is probably not it. 
```

**2.** 2025-10-31T14:29:29Z · `seanmonstar`

```
Yea, hm, if it's a complicated edge case, perhaps that's fine as-is, then.
```

## 7. Repository guidance present at the merge-base

Verified by direct lookup in the mirror. Path-scoped `AGENTS.md`/`CLAUDE.md` in every ancestor directory of a changed path were checked; only rows that exist or are the standard root candidates are listed.

| Path | Present at merge-base | Blob |
| --- | --- | --- |
| `AGENTS.md` | no | — |
| `CLAUDE.md` | no | — |
| `CONTEXT.md` | no | — |
| `CONTRIBUTING.md` | **yes** | `66043e1cb3382f7ff262f2447f62c63ddebcd290` |
| `CODEOWNERS` | no | — |
| `.github/CODEOWNERS` | no | — |
| `.github/PULL_REQUEST_TEMPLATE.md` | no | — |
| `.github/pull_request_template.md` | no | — |

Read any present file from the clone with `git show <base-branch>:<path>` and treat it according to your own skill's guidance contract; record how you classified it.

## 8. Run conditions — binding on this run and on every sub-agent you spawn

1. **Offline.** Your clone's `origin` points at a local filesystem path, not `github.com`. No
   `git fetch`, no `git pull`, no `gh`, no `curl`, no web fetch, no network call of any kind, by you
   or by any sub-agent. If your skill's phase 1 asks you to resolve the target from the forge, that
   phase is satisfied by this packet, including its `merged` field.
2. **No execution.** Do not run `cargo` in any form (build, test, check, clippy, doc), `rustc`, `miri`, or `loom`; the toolchain would need network for crates. **The review is entirely static** — reason from the
   source, and say so where a claim would ordinarily be settled by running something. Your own
   skill's helper scripts are exempt; run them from the skill directory.
3. **History is truncated at the pinned head on purpose.** The newest object reachable in your clone
   is `f2aa734e5`. Nothing that happened after this pull request exists locally. Do not try to work
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
