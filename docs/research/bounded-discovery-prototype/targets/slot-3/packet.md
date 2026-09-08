# Review packet — `nats-io/nats-server#6593` (target (nats-server-6593), issue #138 bounded discovery)

Phase 1 (target resolution) has already been performed by the orchestrator and is reproduced here in
full. **Do not attempt to re-resolve the target over the network — you have no network access.**
Treat every fact in this packet as authoritative pinned input. This packet is byte-identical for every
arm and replicate on this target.

## 1. Pinned run identity

| | |
| --- | --- |
| Pull request | [`nats-io/nats-server#6593`](https://github.com/nats-io/nats-server/pull/6593) — "De-flake TestNRGTermDoesntRollBackToPtermOnCatchup" |
| Author | `MauriceVanVeen` (association at fetch time: `MEMBER`) |
| Repository URL (`summary.repository_url`) | `https://github.com/nats-io/nats-server` |
| Head SHA | `282d01c5466d7694a098112a012097aa3a5dfaf1` (local branch `review-head`, checked out) |
| Base ref | `main` (local branch `main`, force-pinned to the merge-base) |
| Base SHA (as recorded on the pull request) | `4791216cdc896f127a9a2420edd42dcaf7e3b428` |
| Merge-base | `4791216cdc896f127a9a2420edd42dcaf7e3b428` (identical to the base SHA) |
| Diff | 3 files, +34 / −13, 1 commits |
| `state` | `MERGED` |
| `merged` | **`true`** (merged 2025-02-27T17:07:22Z) |
| `isDraft` | `false` |
| Originating issue(s) | none — the PR body carries no closing reference; `issues=none` unless the dispatch supplies a spec |
| Posting identity | `kamui`, who did NOT author the PR and has no prior comments or reviews on it → an ordinary first review by a third party, event `COMMENT`; the target is merged, so this is a **retrospective review with publication disabled** |

Compute the diff as `git diff main review-head` (the `main` branch is pinned to the merge-base, so two-dot and three-dot are identical here).

## 2. Changed-file manifest (verified against the pinned SHAs from the mirror)

```
M  server/raft_chain_of_blocks_helpers_test.go                            (+14   −5)
M  server/raft_helpers_test.go                                            (+15   −8)
M  server/raft_test.go                                                    (+5    −0)
```

## 3. Pull-request body, verbatim

````
Various Raft tests could potentially deadlock if they'd make a call to `rg.lockAll()` which locks all Raft nodes while another part is also holding the state machine's lock and requires a Raft lock.

`TestNRGTermDoesntRollBackToPtermOnCatchup` could fail with the following error message due to interest propagation not being immediate.
```
raft_test.go:882: require read from channel within 5s but didn't get anything
```

Signed-off-by: Maurice van Veen <github@mauricevanveen.com>
````

## 4. Originating issue

None. The pull-request body is the only statement of intent. Record `issues=none` (or the coordinate of a spec the dispatch supplies).

## 5. Commits on the head, oldest first — messages verbatim

| # | SHA | Date | Author | Message |
| --- | --- | --- | --- | --- |
| 1 | `282d01c54` | 2025-02-27 | Maurice van Veen | De-flake TestNRGTermDoesntRollBackToPtermOnCatchup<br><br>Signed-off-by: Maurice van Veen <github@mauricevanveen.com> |

> **Mandatory note, same class as prior packets in this program.** Where later commits on the head
> applied the author's responses to earlier review rounds, that feedback is already fixed in the reviewed
> head and must not be rediscovered and reported as still outstanding. Read the prior-review section
> below against the head before treating any earlier comment as live.

## 6. Prior review state through the frozen cutoff `2025-02-27T17:07:22Z` (the merge instant), reproduced verbatim

### Review submissions (1)

| When | Who | State | On commit | Body |
| --- | --- | --- | --- | --- |
| 2025-02-27T16:47:22Z | `derekcollison` | APPROVED | `282d01c54` | LGTM |

### Review threads (0), comments verbatim, in order

*(no inline review comments)*

### Non-review conversation (0), verbatim, in order

*(none)*

## 7. Repository guidance present at the merge-base

Verified by direct lookup in the mirror. Path-scoped `AGENTS.md`/`CLAUDE.md` in every ancestor directory of a changed path were checked; only rows that exist or are the standard root candidates are listed.

| Path | Present at merge-base | Blob |
| --- | --- | --- |
| `AGENTS.md` | no | — |
| `CLAUDE.md` | no | — |
| `CONTEXT.md` | no | — |
| `CONTRIBUTING.md` | **yes** | `f0543e9b29f3bea0551b990b314b6f09fcac2ae2` |
| `CODEOWNERS` | no | — |
| `.github/CODEOWNERS` | **yes** | `f77be596f36bd7aa3e675e16b59be5da42c58153` |
| `.github/PULL_REQUEST_TEMPLATE.md` | **yes** | `89b1adaf917e851cb3c9094f0efbf8c52fb678af` |
| `.github/pull_request_template.md` | no | — |

Read any present file from the clone with `git show <base-branch>:<path>` and treat it according to your own skill's guidance contract; record how you classified it.

## 8. Run conditions — binding on this run and on every sub-agent you spawn

1. **Offline.** Your clone's `origin` points at a local filesystem path, not `github.com`. No
   `git fetch`, no `git pull`, no `gh`, no `curl`, no web fetch, no network call of any kind, by you
   or by any sub-agent. If your skill's phase 1 asks you to resolve the target from the forge, that
   phase is satisfied by this packet, including its `merged` field.
2. **Execution allowance.** Focused test execution IS permitted on this target, offline, exactly as the packet's section 8 item 2 states: run go commands from the clone root with GOMODCACHE=/tmp/bd148/gomodcache GOCACHE=/tmp/bd148/gocache-nats-server-6593 GOFLAGS=-mod=mod GOPROXY=off, for example `go test -count=1 -run '<test name regex>' ./server/` (about 15 seconds to compile the server test binary, then the named tests); the race detector (`-race`) is permitted; always pass -run with a specific name and never run the server package's whole suite (it takes hours); `go vet ./server/` reports pre-existing IPv6 address-format findings in unrelated test files at both the head and the merge-base; five minutes per command; a name regex at most once per flag set; scratch modules only under your work directory; nothing added to or changed in the clone. The module cache is already populated and no network call of any kind is available. Your own skill's helper scripts are always
   permitted; run them from the skill directory.
3. **History is truncated at the pinned head on purpose.** The newest object reachable in your clone
   is `282d01c54`. Nothing that happened after this pull request exists locally. Do not try to work
   around this. At the end, report explicitly whether you read any history beyond the pinned head and
   which history commands you ran.
4. **Publication is disabled.** The target is merged; this is a retrospective review. Do not post
   anything anywhere. Follow your skill through to the point where it would publish, then render the
   review **exactly as it would be posted**, including summary body (with the `Mode` line your
   contract requires for a merged target), per-finding comments, and any trailers, and stop.
5. **Follow your own skill as written** — its phase structure, its fan-out policy, its verification
   triggers, its output contract. Do not borrow behavior from any other review skill. Where the skill
   tells you to spawn sub-agents, spawn them with the `Agent` tool and **pass `model: "<the model your dispatch names for that worker>"`
   explicitly on every call**.
6. **Persist before you verify.** Write the expensive phase to your report file before dispatching
   any verifier or finder: the manifest and requirement ledger when they are complete, then the
   complete candidate ledger with every disposition, then the verifier prompts and verbatim reports as
   they arrive. A session interruption after that point loses nothing that the file holds.
7. **Stay in your own sandbox.** Your clone, your skill snapshot, this packet directory, and your
   own report and payload paths only. Do not read any other run's clone, report, or payload. Report
   it if you read one anyway.
