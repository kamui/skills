# Review packet — `graphql/graphql-js#1582`

Forge state of the pull request frozen at the cutoff named in section 6; records first
published after the cutoff are omitted. This packet carries facts only. The run supplies its
policy (branch layout, execution allowance, what is unavailable) separately.

## 1. Pinned run identity

| | |
| --- | --- |
| Pull request | [`graphql/graphql-js#1582`](https://github.com/graphql/graphql-js/pull/1582) — "Enable Flow typings on errors tests + Fix typing for Error constructor" |
| Author | `IvanGoncharov` (association at fetch time: `MEMBER`) |
| Repository URL | `https://github.com/graphql/graphql-js` |
| Head SHA | `7e39a122eea9292eeffa6905ffdf8a60c5161cfd` |
| Base ref | `master` |
| Base SHA (as recorded on the pull request) | `5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11` |
| Merge-base | `5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11` (identical to the base SHA) |
| Diff | 5 files, +48 / −47, 1 commits |
| `state` | `MERGED` |
| `merged` | **`true`** (merged 2018-11-21T14:33:19Z) |
| `isDraft` | `false` |
| Originating issue(s) | none — the PR body carries no closing reference |

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

None. The pull-request body is the only statement of intent.

## 5. Commits on the head, oldest first — messages verbatim

| # | SHA | Date | Author | Message |
| --- | --- | --- | --- | --- |
| 1 | `7e39a122e` | 2018-11-21 | Ivan Goncharov | Enable Flow typings on errors tests + Fix typing for Error constructor |

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
