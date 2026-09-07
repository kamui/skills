# Review packet — `graphql/graphql-js#1582` (target (k), issue #137 qualification grid)

Phase 1 (target resolution) has already been performed by the orchestrator and is reproduced here in
full. **Do not attempt to re-resolve the target over the network — you have no network access.**
Treat every fact in this packet as authoritative pinned input. This packet is byte-identical for every
arm and replicate on this target.

## 1. Pinned run identity

| | |
| --- | --- |
| Pull request | [`graphql/graphql-js#1582`](https://github.com/graphql/graphql-js/pull/1582) — "Enable Flow typings on errors tests + Fix typing for Error constructor" |
| Author | `IvanGoncharov` (association at fetch time: `MEMBER`) |
| Repository URL (`summary.repository_url`) | `https://github.com/graphql/graphql-js` |
| Head SHA | `7e39a122eea9292eeffa6905ffdf8a60c5161cfd` (local branch `review-head`, checked out) |
| Base ref | `master` (local branch `master`, force-pinned to the merge-base) |
| Base SHA (as recorded on the pull request) | `5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11` |
| Merge-base | `5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11` (identical to the base SHA) |
| Diff | 5 files, +48 / −47, 1 commits |
| `state` | `MERGED` |
| `merged` | **`true`** (merged 2018-11-21T14:33:19Z) |
| `isDraft` | `false` |
| Originating issue(s) | none — the PR body carries no closing reference; `issues=none` unless the dispatch supplies a spec |
| Posting identity | `kamui`, who did NOT author the PR and has no prior comments or reviews on it → an ordinary first review by a third party, event `COMMENT`; the target is merged, so this is a **retrospective review with publication disabled** |

Compute the diff as `git diff master review-head` (the `master` branch is pinned to the merge-base, so two-dot and three-dot are identical here).

## 2. Changed-file manifest (verified against the pinned SHAs from the mirror)

```
M  src/error/GraphQLError.js                                              (+1    −1)
M  src/error/__tests__/GraphQLError-test.js                               (+27   −33)
M  src/error/__tests__/locatedError-test.js                               (+3    −3)
M  src/error/__tests__/printError-test.js                                 (+15   −9)
M  src/jsutils/__tests__/inspect-test.js                                  (+2    −1)
```

## 3. Pull-request body, verbatim

*(empty)*

## 4. Originating issue

None. The pull-request body is the only statement of intent. Record `issues=none` (or the coordinate of a spec the dispatch supplies).

## 5. Commits on the head, oldest first — messages verbatim

| # | SHA | Date | Author | Message |
| --- | --- | --- | --- | --- |
| 1 | `7e39a122e` | 2018-11-21 | Ivan Goncharov | Enable Flow typings on errors tests + Fix typing for Error constructor |

> **Mandatory note, same class as prior packets in this program.** Where later commits on the head
> applied the author's responses to earlier review rounds, that feedback is already fixed in the reviewed
> head and must not be rediscovered and reported as still outstanding. Read the prior-review section
> below against the head before treating any earlier comment as live.

## 6. Prior review state through the frozen cutoff `2018-11-21T14:33:19Z` (the merge instant), reproduced verbatim

### Review submissions (1)

| When | Who | State | On commit | Body |
| --- | --- | --- | --- | --- |
| 2018-11-21T14:26:56Z | `IvanGoncharov` | COMMENTED | `7e39a122e` | *(empty)* |

### Review threads (1), comments verbatim, in order

**1.** 2018-11-21T14:26:56Z · `IvanGoncharov` · `src/error/GraphQLError.js:25` · on commit `7e39a122e` · thread unresolved

```
All other arguments support `null` so there is no reason why `nodes` accepts `undefined` but not the `null`.
```

### Non-review conversation (0), verbatim, in order

*(none)*

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
2. **Execution allowance.** Focused test execution IS permitted on this target, offline: dependencies are already installed in the clone (untracked and ignored; leave them alone). Run mocha with the clone's own binary, for example `./node_modules/.bin/mocha --require @babel/register --require @babel/polyfill <test file>` (about 2 seconds); five minutes per command, a selection at most once per flag set. Write any scratch JavaScript under your work directory; nothing may be added to or changed in the clone, and no network call of any kind is available (npm and npx cannot reach a registry). Your own skill's helper scripts are always
   permitted; run them from the skill directory.
3. **History is truncated at the pinned head on purpose.** The newest object reachable in your clone
   is `7e39a122e`. Nothing that happened after this pull request exists locally. Do not try to work
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
