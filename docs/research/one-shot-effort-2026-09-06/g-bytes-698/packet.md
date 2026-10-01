# Review packet — `tokio-rs/bytes#698` (target (g), issue #124 effort experiment)

Phase 1 (target resolution) has already been performed by the orchestrator and is reproduced here in
full. **Do not attempt to re-resolve the target over the network — you have no network access.**
Treat every fact in this packet as authoritative pinned input. This packet is byte-identical for every
arm and replicate on this target.

## 1. Pinned run identity

| | |
| --- | --- |
| Pull request | [`tokio-rs/bytes#698`](https://github.com/tokio-rs/bytes/pull/698) — "Reuse capacity when possible in `<BytesMut as Buf>::advance` impl" |
| Author | `paolobarbolini` (association at fetch time: `CONTRIBUTOR`) |
| Repository URL (`summary.repository_url`) | `https://github.com/tokio-rs/bytes` |
| Head SHA | `7052d2454a2370ab9583f63711df89f3bd7bec83` (local branch `review-head`, checked out) |
| Base ref | `master` (local branch `master`, force-pinned to the merge-base) |
| Base SHA (as recorded on the pull request) | `ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401` |
| Merge-base | `ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401` (identical to the base SHA) |
| Diff | 1 files, +8 / −0, 1 commits |
| `state` | `MERGED` |
| `merged` | **`true`** (merged 2024-04-25T07:08:17Z) |
| `isDraft` | `false` |
| Originating issue(s) | none — the PR body carries no closing reference; `issues=none` unless the dispatch supplies a spec |
| Posting identity | `kamui`, who did NOT author the PR and has no prior comments or reviews on it → an ordinary first review by a third party, event `COMMENT`; the target is merged, so this is a **retrospective review with publication disabled** |

Compute the diff as `git diff master review-head` (the `master` branch is pinned to the merge-base, so two-dot and three-dot are identical here).

## 2. Changed-file manifest (verified against the pinned SHAs from the mirror)

```
M  src/bytes_mut.rs                                                       (+8    −0)
```

## 3. Pull-request body, verbatim

````
While thinking about usage of `BytesMut` in my own code I've realized sometimes the following pattern (explained by the following pseudocode) is encountered:

```rs
let mut buf = BytesMut::with_capacity(8196);

loop {
    read_into_bufmut(&mut buf);

    if some_condition {
        // consume the data and then discard it
        let consumed = process_data(&buf);
        buf.advance(consumed);
        // in most cases the above `advance` ends-up consuming the entire length of `buf`
    } else {
        // consume the data as `Bytes`
        ship_data(buf.split().freeze());

        // (this is just to explain that `VecDeque` wouldn't be efficient here)
    }
}
```

In this particular example it would be more efficient to `buf.clear()` when `consumed == buf.len()`, instead of calling `advance` and eventually ending-up going through the allocation machinery.

This PR makes `advance` do it automatically for cases in which it's safe to do (which is why I didn't put it inside `advance_unchecked`). I'm not sure the `Buf` API allows it, the only thing I've found is `#[must_use = "consider BytesMut::advance(len()) if you don't need the other half"]` on `BytesMut::split()`.
````

## 4. Originating issue

None. The pull-request body is the only statement of intent. Record `issues=none` (or the coordinate of a spec the dispatch supplies).

## 5. Commits on the head, oldest first — messages verbatim

| # | SHA | Date | Author | Message |
| --- | --- | --- | --- | --- |
| 1 | `7052d2454` | 2024-04-24 | Paolo Barbolini | Reuse capacity when possible in <BytesMut as Buf>::advance impl |

> **Mandatory note, same class as prior packets in this program.** Where later commits on the head
> applied the author's responses to earlier review rounds, that feedback is already fixed in the reviewed
> head and must not be rediscovered and reported as still outstanding. Read the prior-review section
> below against the head before treating any earlier comment as live.

## 6. Prior review state through the frozen cutoff `2024-04-25T07:08:17Z` (the merge instant), reproduced verbatim

### Review submissions (5)

| When | Who | State | On commit | Body |
| --- | --- | --- | --- | --- |
| 2024-04-24T08:11:31Z | `Darksonn` | COMMENTED | `0bd06ed56` | Would it make more sense to move this check to `advance_unchecked`? |
| 2024-04-24T08:31:18Z | `paolobarbolini` | COMMENTED | `0bd06ed56` | *(empty)* |
| 2024-04-24T09:13:14Z | `Darksonn` | COMMENTED | `0bd06ed56` | *(empty)* |
| 2024-04-24T19:15:13Z | `braddunbar` | COMMENTED | `85d9c881e` | This is nice, thanks! I only have two small requests:<br><br>1. Can we use `self.remaining()` or `self.len` consistently in this function? Either one is fine with me, but it's not obvious that those values are synonymous.<br>2. Can we move this conditional before the `assert!` above? If `cnt == self.len`, we already know that `cnt <= self.remaining()` so we don't need to check it twice. |
| 2024-04-24T20:49:41Z | `braddunbar` | APPROVED | `7052d2454` | *(empty)* |

### Review threads (1), comments verbatim, in order

**1.** 2024-04-24T08:10:50Z · `Darksonn` · `src/bytes_mut.rs:1074` · on commit `0bd06ed56` · thread resolved

````
The safety requirement for `set_len` is that the length must not be greater than the capacity, so that is what the safety comment should address. The comment you have right now could stay, but not as a safety comment.
```suggestion
            // SAFETY: Zero is not greater than the capacity.
            unsafe { self.set_len(0) };
```
Also, safety comments should generally go before the unsafe block. I know there are some places where we put it inside, but they should be fixed at some point.
````

**2.** 2024-04-24T08:31:18Z · `paolobarbolini` · `src/bytes_mut.rs:1074` · on commit `0bd06ed56` · thread resolved

```
> The safety requirement for set_len is that the length must not be greater than the capacity, so that is what the safety comment should address.

:+1: I'll include it soon.
```

**3.** 2024-04-24T09:13:13Z · `Darksonn` · `src/bytes_mut.rs:1074` · on commit `0bd06ed56` · thread resolved

```
Notice that the semicolon is outside the unsafe block. That way it fmts on one line.
```

### Non-review conversation (3), verbatim, in order

**1.** 2024-04-24T08:37:28Z · `paolobarbolini`

```
> Would it make more sense to move this check to `advance_unchecked`?

I'm not quite sure how to structure this because the thing with `advance_unchecked` is that it gets called by `split_to` and `split_off`. These functions expect `advance_unchecked` to actually advance the position, otherwise they would end up with the two instances of `BytesMut` having overlapping ranges.
```

**2.** 2024-04-24T08:49:32Z · `Darksonn`

```
The conflict with `split_to` and `split_off` is a good reason to not put it in `advance_unchecked`.
```

**3.** 2024-04-24T19:50:38Z · `paolobarbolini`

```
Good idea. Fixed!
```

## 7. Repository guidance present at the merge-base

Verified by direct lookup in the mirror. Path-scoped `AGENTS.md`/`CLAUDE.md` in every ancestor directory of a changed path were checked; only rows that exist or are the standard root candidates are listed.

| Path | Present at merge-base | Blob |
| --- | --- | --- |
| `AGENTS.md` | no | — |
| `CLAUDE.md` | no | — |
| `CONTEXT.md` | no | — |
| `CONTRIBUTING.md` | no | — |
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
2. **Execution allowance.** Focused test execution IS permitted on this target, offline, using cargo with the environment CARGO_HOME=/tmp/effort124/cargo-home CARGO_NET_OFFLINE=true CARGO_TARGET_DIR=<your work dir>/target, five minutes per command, the suite at most once, scratch crates only under your work directory, nothing added to or changed in the clone. Your own skill's helper scripts are always
   permitted; run them from the skill directory.
3. **History is truncated at the pinned head on purpose.** The newest object reachable in your clone
   is `7052d2454`. Nothing that happened after this pull request exists locally. Do not try to work
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
