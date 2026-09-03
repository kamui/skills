# v2a run — `code-review-deep-publish` against `microsoft/playwright#29698`

**2026-09-03.** Data only. Not published to the PR. See [`README.md`](README.md) for the
pinned run identity, the ground truth, and the conditions held constant across all four runs.

> **Run-continuity note.** The Find phase (both axis finders) completed, then a session rate limit
> killed the orchestrator before it verified. Verify and Publish were executed by a fresh
> orchestrator context given the same packet and the two finder reports verbatim. Both finders ran
> once and were not redone. Model verification for every agent is in
> [`comparison-data.md`](comparison-data.md).

---


Run resumed at the **Verify** phase. The Find phase (both axis finders) completed in an earlier
orchestrator context that was killed by a rate limit before verification; its two finder reports
are pinned input to this run and are **not** redone — they are reproduced verbatim below. This
context performed Verify and Publish (publication disabled; rendered would-be review only).

---

## 1. Metadata

| | |
| --- | --- |
| **Skill** | `code-review-deep-publish`, snapshot at `/tmp/handoff4/skill-v2a/skills/code-review-deep-publish/` (`SKILL.md`, `DESIGN.md`, `references/{finding-format,code-axis,requirements-axis,verify,publishing,ATTRIBUTION}.md`, `agents/openai.yaml`) |
| **Architecture** | Panel line, recall-first: two parallel axis finders (Code, Requirements — completed in the prior, now-resumed session) → one fresh-context verifier (spawned this session) → publish-shaped render, publication disabled per binding constraint 4 |
| **Model** | `sonnet` passed explicitly on the one `Agent` call this session made (the verifier). The two finders were spawned by the prior session under the same instruction; this session did not re-spawn them and cannot independently re-verify their model from a transcript it doesn't have access to — see § Notes |
| **Agents spawned** | This session: 1 (verifier). Total across both sessions for this run: 3 (Code finder, Requirements finder, verifier) |
| **Sub-agent tokens** | Code finder: 111,274 (reported by prior session). Requirements finder: 76,669 (reported by prior session). Verifier: 34,930 (reported this session). **Total: 222,873** |
| **Tool uses** | Code finder: 54. Requirements finder: 24. Verifier: 16. **Sub-agent total: 94.** Orchestrator (this session): ~19 Bash, ~7 Read, 2 Write, 1 Agent — see § Notes for the full tally |
| **Wall clock** | Code finder: 616,592 ms (~10m17s). Requirements finder: 365,697 ms (~6m6s). Verifier: 117,420 ms (~1m57s). This session (Verify+Publish only): `2026-09-03T22:32:32Z` → `2026-09-03T22:42:28Z` (~9m56s) |
| **Candidates raised** | 3, all Code axis (Requirements axis raised 0) |
| **Candidates surviving verification** | 3 of 3 |
| **Verifier verdicts** | `confirmed` × 3, `plausible` × 0, `refuted` × 0, merges: 0 |
| **Findings for publication** | 3 (1 `must-fix` P2, 2 `consider` P3) |
| **Questions** | 0 |
| **Observations** | 3 published (bounded cap); 2 additional accurate observations (both from the verifier) considered and dropped to stay within the cap — see § Candidate disposition ledger |
| **Coverage over all 10 changed files** | Complete — both finders independently marked all 10 files `reviewed`, none `ignored`, nothing left unfinished |
| **Derived status** | **Changes Requested (advisory)** — one unsettled `must-fix` (Candidate 1) |

---

## 2. Full reviewer report(s) — verbatim

### Code axis

> Verbatim output of Code-axis finder sub-agent `a14d8bcf5890339cc` (v2a run).
> Reported usage: 111,274 tokens, 54 tool uses, 616,592 ms.

## Changed-file manifest

| File | Disposition | Reason |
| --- | --- | --- |
| `docs/src/api/class-browsercontext.md` | reviewed | New `removeCookies` doc entry read in full; checked alphabetical placement (correct, between `pages` and `request`), cross-checked wording against implementation and against `types.d.ts`; found the `since: v1.43` version-tag defect (Candidate 3). |
| `packages/playwright-core/src/client/browserContext.ts` | reviewed | New `removeCookies` client method read alongside `cookies`/`addCookies`/`clearCookies` siblings; signature, delegation to `_channel.removeCookies`, and style all consistent with siblings. No defect. |
| `packages/playwright-core/src/client/network.ts` | reviewed | New `RemoveNetworkCookieParam` type read alongside `NetworkCookie`/`SetNetworkCookieParam`; shape and naming consistent. No defect. |
| `packages/playwright-core/src/protocol/validator.ts` | reviewed | New `BrowserContextRemoveCookiesParams`/`...Result` schema read alongside sibling `BrowserContextAddCookiesParams`/`BrowserContextClearCookiesParams`; `tObject`/`tOptional(tString)` usage correct and consistent. No defect. |
| `packages/playwright-core/src/server/browserContext.ts` | reviewed | Read the full enclosing class, the abstract `addCookies`/`clearCookies`/`doGetCookies` contracts, `cookies()`, and the existing `_resetCookies()` precedent; traced into all three browser backends' `addCookies`/`clearCookies`/`doGetCookies` implementations (chromium, firefox, webkit) and `network.ts`'s `filterCookies`/`rewriteCookies`. Source of Candidate 1. |
| `packages/playwright-core/src/server/dispatchers/browserContextDispatcher.ts` | reviewed | New `removeCookies` dispatcher method read alongside `addCookies`/`clearCookies`/`cookies` siblings; correct pass-through of `params.filter`. No defect. |
| `packages/playwright-core/types/types.d.ts` | reviewed | New `removeCookies` JSDoc+signature read in full; cross-checked against `docs/src/api/class-browsercontext.md` and against the `addCookies` JSDoc block (confirmed generated files elsewhere mirror the doc source verbatim). Source of Candidate 2. |
| `packages/protocol/src/channels.ts` | reviewed | Generated file (`// This file is generated by generate_channels.js, do not edit manually.`); new `removeCookies` entry and `BrowserContextRemoveCookiesParams/Options/Result` types read; verified they mirror `protocol.yml` faithfully. Placement mid-interface (between `clearCookies` and `clearPermissions`) traced to `protocol.yml`'s own ordering — no independent defect in this generated file; see Observations. |
| `packages/protocol/src/protocol.yml` | reviewed | Source of `channels.ts`. New `removeCookies:` block read; schema correct. Insertion point breaks the file's originally-alphabetical `BrowserContext` method block, but this has no documented-standard backing and no behavioral effect — recorded as an observation, not a candidate. The unrelated whitespace fix to `ElectronApplication.events.console.parameters` trailing-space removal was also reviewed — harmless, pre-existing trailing whitespace cleanup, not a defect. |
| `tests/library/browsercontext-remove-cookies.spec.ts` | reviewed | Read in full (231 lines, all 8 tests); read sibling `tests/library/browsercontext-cookies.spec.ts` and confirmed import path `../config/browserTest` and license header match repository convention. Logic of each test (AND-combination semantics, expected surviving cookies) verified against the implementation and found correct. No defect. |

All 10 files were read and reviewed; none were skipped or left unread.

---

## Candidates

### Candidate 1

- **id**: `code/browserContext-ts/removeCookies-clears-all-cookies-race-window`
- **anchor**: `packages/playwright-core/src/server/browserContext.ts:291`
- **fix**: (same site; omitted — anchor is the fix site)
- **title**: `removeCookies` clears the whole context's cookies before restoring the kept ones
- **claim**: `BrowserContext.removeCookies` (`packages/playwright-core/src/server/browserContext.ts:279-293`) is implemented as read-filter-clear-restore:
  ```js
  const currentCookies = await this.cookies();
  const cookiesToKeep = currentCookies.filter(cookie => { ... });
  await this.clearCookies();
  await this.addCookies(cookiesToKeep);
  ```
  `this.clearCookies()` is not scoped to the filter — in all three backends it unconditionally deletes every cookie in the browser context: chromium's `clearCookies()` sends `Storage.clearCookies` for the whole `browserContextId` (`packages/playwright-core/src/server/chromium/crBrowser.ts:414-416`), webkit's sends `Playwright.deleteAllCookies` for the whole context (`packages/playwright-core/src/server/webkit/wkBrowser.ts:275-277`), and firefox's sends `Browser.clearCookies` for the whole context (`packages/playwright-core/src/server/firefox/ffBrowser.ts:298-300`). Each of `cookies()`, `clearCookies()` and `addCookies()` is a separate async round trip to the browser process, so there is a real time window, not an atomic operation, during which every cookie in the context — including ones the caller never asked to remove — is absent, and any cookie written during that window (via a page's `document.cookie`, or a `Set-Cookie` response header from an in-flight navigation/fetch on any page sharing the context) is silently discarded: it is not in the `currentCookies` snapshot taken before the clear, so it is not in `cookiesToKeep`, so `addCookies(cookiesToKeep)` never restores it.
- **support**: *(withheld from verifier per skill; original finder's audit note: read the abstract `addCookies`/`clearCookies`/`doGetCookies` declarations and all three backend implementations plus `server/network.ts`'s `filterCookies`; checked the `_resetCookies()` precedent and judged it distinguishable by usage context; could not execute anything to reproduce the race; noted the PR's own CI table shows the new spec flaking once on WebKit as weak, non-causal corroboration only.)*
- **trigger**: Any page in the same `BrowserContext` performs a navigation, fetch, or `document.cookie` write that sets or refreshes a cookie at the same time another caller invokes `context.removeCookies(...)`. The concurrently-set cookie is present when `clearCookies()` runs and absent afterward, and it is never restored by the subsequent `addCookies(cookiesToKeep)` because it was not part of the pre-clear snapshot.
- **change**: Reimplement `removeCookies` to avoid a full clear-and-restore round trip — e.g. delete only the matching cookies directly at the protocol layer (chromium's CDP exposes `Network.deleteCookies`/`Storage.deleteCookies` with name/domain/path filters; equivalent per-cookie deletion primitives should be checked for firefox/webkit) instead of `clearCookies()` + `addCookies(cookiesToKeep)` in `packages/playwright-core/src/server/browserContext.ts:291-292`. At minimum, document the known race if a narrower fix is out of scope for this PR.
- **priority**: P2
- **action**: must-fix

### Candidate 2

- **id**: `code/types-d-ts/removeCookies-jsdoc-misstates-throw-condition`
- **anchor**: `packages/playwright-core/types/types.d.ts:8442`
- **fix**: (same site; omitted — anchor is the fix site)
- **title**: `removeCookies` JSDoc implies all three filter fields are required, contradicting the code and the doc
- **claim**: `packages/playwright-core/types/types.d.ts:8442` reads: "Removes cookies from context. The method will throw an error if either name, domain or path has not been passed." Read literally, this says the method throws unless `name`, `domain`, and `path` are *all* supplied. The actual implementation at `packages/playwright-core/src/server/browserContext.ts:280-281` is `if (!filter.name && !filter.domain && !filter.path) throw new Error(...)` — it throws only when *all three* are missing, i.e. only *one* of the three is required, not all three. This is exactly what `docs/src/api/class-browsercontext.md:1017` says: "Removes cookies from context. At least one of the removal criteria should be provided." `types.d.ts` is a generated file (`packages/playwright-core/types/types.d.ts:1`: "This file is generated by /utils/generate_types/index.js") whose JSDoc is normally pulled verbatim from `docs/src/api/*.md` — I confirmed this by comparing the `addCookies` JSDoc block (`types.d.ts:8247-8249`) against `docs/src/api/class-browsercontext.md:308-309`, which match word for word (link syntax aside). The `removeCookies` block does not match its corresponding doc paragraph at all, which is inconsistent with how every other method in this file is produced.
- **support**: *(withheld from verifier per skill; original finder could not run the type generator to confirm whether a routine regeneration would self-correct this, and flagged that uncertainty explicitly.)*
- **trigger**: A TypeScript/JS consumer reads the `removeCookies` JSDoc in their editor (or in generated API references sourced from this file) and concludes — incorrectly — that `name`, `domain`, and `path` must all be supplied together, when in fact any one suffices and the type signature itself (`{ name?: string; domain?: string; path?: string }`) already allows partial filters.
- **change**: Correct the JSDoc summary at `packages/playwright-core/types/types.d.ts:8442` to match `docs/src/api/class-browsercontext.md:1017`'s wording ("At least one of the removal criteria should be provided"), or regenerate `types.d.ts` from the doc source so the two stay in sync.
- **priority**: P3
- **action**: consider

### Candidate 3

- **id**: `code/class-browsercontext-md/removeCookies-since-v1-43-mismatch`
- **anchor**: `docs/src/api/class-browsercontext.md:1014`
- **fix**: `docs/src/api/class-browsercontext.md:1014` and `docs/src/api/class-browsercontext.md:1028` (both `* since: v1.43` lines)
- **title**: `removeCookies`'s `since: v1.43` tag doesn't match the in-development version
- **claim**: `docs/src/api/class-browsercontext.md:1014` (method) and `:1028` (param) both tag the new API as `* since: v1.43`. At the base/head commit, `package.json:4` and `packages/playwright-core/package.json:3` both declare `"version": "1.42.0-next"` — i.e. the repository is mid-development for the 1.42 release, not 1.43. Every other currently-unreleased API addition in this same snapshot of the docs tree uses `since: v1.42`, e.g. `docs/src/api/class-electronapplication.md:45`, and `docs/src/api/class-page.md:2992`, `:2998`, `:3147`, `:3341`, `:3348`, `:3355`, `:3362`. `removeCookies` is the only unreleased-API `since` tag in the docs tree using `v1.43`.
- **support**: *(withheld from verifier per skill; original finder read `utils/doclint/since.js` and `utils/doclint/api_parser.js` to confirm the routine `npm run doc` lint only checks a `since` tag exists, not that its version number is correct — so CI would not catch this.)*
- **trigger**: A user on Playwright 1.42.x (or a tool cross-referencing the published `since` metadata for API-availability checks) sees "Added in: v1.43" on `removeCookies` and incorrectly concludes the method isn't available in their pinned 1.42 release, or the published docs simply carry the wrong version number for as long as the mistake goes uncorrected.
- **change**: Change `* since: v1.43` to `* since: v1.42` at `docs/src/api/class-browsercontext.md:1014` and `:1028`.
- **priority**: P3
- **action**: consider

---

## Disposition ledger

| Claim | Falsification route | Decisive evidence | Disposition |
| --- | --- | --- | --- |
| `removeCookies` clears the whole context's cookies, not just the filtered ones, opening a data-loss race window | Check whether `clearCookies()` is scoped to the filter in any backend | `crBrowser.ts:414-416`, `wkBrowser.ts:275-277`, `ffBrowser.ts:298-300` (all unscoped) | candidate |
| Existing `_resetCookies()` precedent (clear+readd) discharges the race concern via "not extra rigor" | Compare usage contexts (reset-for-reuse vs. live user-invoked API) | `browserContext.ts:540-544` vs `:279-293` | acquitted (distinguishable context; doesn't discharge candidate) |
| `removeCookies` filter still does substring matching (maintainer's original review comment 1) | Read current filter predicate | `browserContext.ts:286-289` uses `===`, not `.includes()` | acquitted (already fixed prior to reviewed head) |
| `await this.cookies()` runs before the early-return guard, wasting work (Smrtnyk comment 4) | Read statement order | `browserContext.ts:280-281` (guard) precedes `:283` (`cookies()` call) | acquitted (already correctly ordered) |
| Parameter/variable naming (`cookies`/`filter`/`cookiesToKeep`/`currentCookies`) is confusing (Smrtnyk comments 5-7) | Check for a documented naming standard | `CONTRIBUTING.md` has no naming-convention section; maintainer explicitly called these "stylistic" | acquitted (style nitpick, no documented rule, maintainer already dismissed) |
| `filter.domain === cookie.domain` may fail to match domain-attribute cookies stored with a leading dot | Determine actual stored `domain` format for domain-scoped cookies in this repo | No code path found that would confirm or rule this out without execution | acquitted (rests on an unstated assumption; insufficiently evidenced) |
| Client `removeCookies(filter)` has no default, so a plain-JS caller invoking with zero args gets a raw/ungraceful error instead of the friendly message | Compare against sibling required-param methods (e.g. `grantPermissions(permissions: string[])`) | `client/browserContext.ts:272-273`, `:277` (same pattern elsewhere, TS-enforced) | acquitted (consistent with existing codebase rigor; TS-typechecker-guarded) |
| `types.d.ts` JSDoc for `removeCookies` misstates the throw condition and diverges from its generation source | Compare against markdown doc and against a known-generated sibling block (`addCookies`) | `types.d.ts:8442` vs `docs/src/api/class-browsercontext.md:1017`; `types.d.ts:8247-8249` vs `class-browsercontext.md:308-309` (verbatim match, control) | candidate |
| `since: v1.43` tag is wrong for an API landing in the 1.42 dev cycle | Compare against `package.json` version and sibling unreleased `since` tags | `package.json:4` (`1.42.0-next`); `class-electronapplication.md:45`, `class-page.md:2992` etc. all `v1.42` | candidate |
| `protocol.yml`'s `removeCookies:` entry breaks the `BrowserContext` block's alphabetical ordering | Check whether the block is alphabetical throughout, and whether any rule documents this | `protocol.yml` lines for `addCookies`…`storageState` are alphabetical, but `pause`/`recorderSupplementEnable`/`newCDPSession`/etc. after that are not; no documented ordering rule exists | acquitted → observation (no behavioral effect, no documented standard) |
| Round-tripping cookies through `clearCookies()`+`addCookies(cookiesToKeep)` loses `httpOnly`/`secure`/`sameSite`/`expires` fidelity | Check `NetworkCookie`→`SetNetworkCookie` structural compatibility and `rewriteCookies` behavior when no `url` is given | `channels.ts:238-259` (structurally compatible); `server/network.ts:57-75` (`rewriteCookies` only touches `domain`/`path`/`secure` when `copy.url` is set, which it never is here) | acquitted |
| New test file naming (`browsercontext-remove-cookies.spec.ts`) is inconsistent with sibling `browsercontext-clearcookies.spec.ts` | Check whether the directory has one settled naming convention | `tests/library/` already has both `browsercontext-add-cookies.spec.ts` (hyphenated) and `browsercontext-clearcookies.spec.ts` (unhyphenated) pre-existing | acquitted (no single convention exists to violate) |
| Test file logic (AND-combination across name/domain/path, 8 scenarios) has a case that doesn't actually exercise what it claims | Trace each test's setup/assertions against the filter's AND semantics | `browserContext.ts:286-289` implements AND-of-provided-criteria; all 8 tests in `tests/library/browsercontext-remove-cookies.spec.ts` match this | acquitted |
| CONTRIBUTING.md's commit-message / API-guideline rules are violated by this PR's commits or the new method | Check commit subjects and API shape against `CONTRIBUTING.md` §Commit Messages / §API guidelines | PR title (squash-merge subject) `feat(playwright-core): add remove cookies api` matches format; maintainer's own doc-only final commit lacks a label but isn't the contributor's code and won't survive squash-merge | acquitted (not attributable to this change as reviewed) |
| `docs/src/api/class-browsercontext.md`'s summary doesn't spell out that combined filters are ANDed together | Check whether this is a correctness/standards defect vs. a completeness/spec concern | Requirements axis explicitly covers spec completeness; this axis covers correctness/standards only | out of scope for this axis (not raised) |

## Observations

- `packages/protocol/src/protocol.yml`'s new `removeCookies:` entry (and its generated mirror in `channels.ts`) is inserted between `clearCookies:` and `clearPermissions:`, which is out of the file's originally-alphabetical `BrowserContext` method ordering (`clearCookies` < `clearPermissions` alphabetically, but `removeCookies` sits between them) — `packages/protocol/src/protocol.yml:1033-1043`. No documented rule requires this ordering, and later entries in the same block (`pause`, `recorderSupplementEnable`, `newCDPSession`, …) are already non-alphabetical, so this has no behavioral effect and is not a candidate.
- `packages/protocol/src/protocol.yml` also contains an unrelated one-line trailing-whitespace fix to `ElectronApplication.events.console.parameters:` (removes a trailing space) in the same diff — harmless drive-by cleanup, not a defect.

---

## Closing statement

**Git-history commands run**: none that touch history (`git log`, `git show`, `git diff` were never invoked). I ran exactly two read-only, non-history git commands to confirm sandbox state: `git branch --show-current` and `git rev-parse HEAD`, both executed inside `/tmp/handoff4/run-v2a`, both returning `review-head` / `cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b` — confirming the working tree is checked out exactly at the pinned head with nothing beyond it. I did not attempt to read, diff, or reconstruct anything past that pinned SHA.

**Reading beyond the pinned head**: none. All file reads were of the working tree at `/tmp/handoff4/run-v2a` as checked out to `review-head` (`cb02d5ba1`), which is the pinned state.

**Sandbox compliance**: every file read in this run was under `/tmp/handoff4/run-v2a` or `/tmp/handoff4/skill-v2a` (specifically `skill-v2a/skills/code-review-deep-publish/references/finding-format.md` and `.../code-axis.md`), plus the prompt file `/tmp/handoff4-code-finder-prompt.md` itself. No other path under `/tmp/handoff4/*` was read, and no other `/tmp/handoff4` run's clone, skill snapshot, or reports directory was accessed.

**Execution**: none. No `npm`, `node`, `tsc`, `eslint`, build step, or test runner was invoked; all conclusions (including the generated-file/JSDoc mismatch and the `since`-tag mismatch) were reached by static reading and grep-based text search only, and I said so explicitly wherever a claim would ordinarily be settled by running something (Candidate 1's support note on being unable to reproduce the race; Candidate 2's support note on being unable to confirm regeneration behavior).

### Requirements axis

> Verbatim output of Requirements-axis finder sub-agent `ad4e3ff5a6d20c826` (v2a run).
> Reported usage: 76,669 tokens, 24 tool uses, 365,697 ms.

## Restated requirement list

Read from the originating issue, `microsoft/playwright#29662` ("[Feature]: Remove cookie/cookies from context"), in my own words, before checking the diff:

- **R1.** Provide a way to remove **specific** cookies from a `BrowserContext` — i.e., selective removal, distinct from the existing `clearCookies()` which removes everything.
- **R2.** Support selecting cookies to remove by **name**.
- **R3.** Support selecting cookies to remove by **domain**.
- **R4.** Support selecting cookies to remove by **path**.
- **R5.** Support **combinations** of the above selection criteria in one call (the issue's own example passes two full cookie objects together, implying combined/compound targeting is expected, not just one axis at a time).
- **R6.** Removal must be scoped to the calling context only — it must not affect cookies in other browser contexts.
- **R7.** Must satisfy the stated motivating use case: a cookie set ahead of time (e.g. via `globalSetup`, to suppress a GDPR consent modal) can later be selectively removed so a specific test can exercise the modal, while other cookies set the same way are undisturbed.
- **Mentioned, not required — M1.** The issue's "Example" section shows a literal call shape, `context.removeCookies([cookieObject1, cookieObject2])` — an array of full cookie objects. This is illustrative of the ask ("remove cookie/cookies"), not itself a binding interface spec: it sits under an "Example" heading, and the issue body states the requirement in prose ("remove specific cookie/cookies from context") separately from the example. I did not treat the literal array-of-cookie-objects signature as a requirement in its own right — see the ledger and Observations below for how I weighed it.
- **Background/motivation, not a requirement.** "I believe there are other cases where this method would be useful" is an aside, not a testable ask.

Not counted as issue requirements (out of my axis or not in the issue): the exact parameter name (`filter`/`cookies`/`criteria`), whether an empty filter throws and what it says, and doc-string wording — these came from the **PR review thread**, not the issue, and/or are Code-axis (naming, error-message, doc-sync) matters.

## Changed-contract sweep

Per the brief, I scanned the diff for closed lists, enums, or normative vocabularies being renamed/extended/narrowed/retired, then swept the repo for stale peers.

**Contracts considered:** the diff adds one new, wholly new piece of API surface (`removeCookies`) mirrored across the layers that any `BrowserContext` method must pass through (client wrapper → protocol channel → protocol validator → dispatcher → server implementation → public `.d.ts` → docs). This is not a rename or a narrowed/widened closed list — there is no prior "removeCookies" wording to have gone stale, and no enumeration (e.g. a list of allowed cookie fields, SameSite values, etc.) was touched. I still ran the two-term sweep as required:

- Search 1 (new term, case-insensitive): `removeCookies` — repo-wide, excluding `.git`. Hits: `tests/library/browsercontext-remove-cookies.spec.ts` (8×), `docs/src/api/class-browsercontext.md:1013,1021-1024,1027`, `packages/playwright-core/types/types.d.ts:8447-8450,8455`, `packages/playwright-core/src/server/browserContext.ts:279`, `packages/playwright-core/src/server/dispatchers/browserContextDispatcher.ts:227-228`, `packages/playwright-core/src/client/browserContext.ts:272-273`, `packages/protocol/src/channels.ts:1430`, `packages/protocol/src/protocol.yml:1035`. Every layer that carries `clearCookies` (below) also carries `removeCookies`, except the three per-engine browser implementations — see next paragraph for why that's not a gap.
- Search 2 (structurally analogous existing sibling, used as the peer-consistency reference since `removeCookies` is new vocabulary rather than a rename): `clearCookies` — repo-wide. Hits include the same 8 mirrored layers **plus** three per-engine overrides: `packages/playwright-core/src/server/chromium/crBrowser.ts:414`, `.../firefox/ffBrowser.ts:298`, `.../webkit/wkBrowser.ts:275` (each sends a browser-engine-specific wire command, e.g. `Storage.clearCookies` / `Browser.clearCookies`, scoped by `browserContextId`), plus unrelated CDP/juggler protocol type files (`protocol.d.ts` ×2, `firefox/protocol.d.ts`) and incidental test/doc mentions (`browsercontext-add-cookies.spec.ts`, `browsercontext-clearcookies.spec.ts`, `defaultbrowsercontext-1.spec.ts`, `browsertype-launch.spec.ts`, `utils/generate_types/test/test.ts`, `docs/src/puppeteer-js.md`).

**Disposition:** no live peer is stale. The three per-engine `clearCookies()` overrides are a different mechanism — they are the per-browser wire-protocol primitive that the new `removeCookies` is *built from* (via the shared base class composing `this.cookies()` + `this.clearCookies()` + `this.addCookies()` once, generically, in `packages/playwright-core/src/server/browserContext.ts:279-292`), not a peer that itself needs a `removeCookies` override. I verified this composition is real by reading each engine's context class (`CRBrowserContext`, `FFBrowserContext`, `WKBrowserContext`) and confirming each implements `doGetCookies`/`addCookies`/`clearCookies` with the underlying call scoped by `browserContextId`, so `removeCookies`'s clear-then-readd sequence stays confined to the calling context (supports R6). Conclusion: **no changed-contract gap.**

## Requirement disposition

| Req | Bucket | Evidence |
| --- | --- | --- |
| R1 | **Met** | `server/browserContext.ts:279-292` adds `removeCookies(filter)`, distinct from `clearCookies()` (`server/browserContext.ts:254`), reachable end-to-end: client (`client/browserContext.ts:272-273`) → channel (`protocol/channels.ts:1430,1527-1537`) → validator (`protocol/validator.ts:831-838`) → dispatcher (`server/dispatchers/browserContextDispatcher.ts:227-228`) → server. |
| R2 | **Met** | Filter matches on `cookie.name` (`server/browserContext.ts:282`); test `tests/library/browsercontext-remove-cookies.spec.ts:19-37` ("should remove cookies by name"). |
| R3 | **Met** | Filter matches on `cookie.domain` (`server/browserContext.ts:283`); test at `tests/library/browsercontext-remove-cookies.spec.ts:39-59` ("should remove cookies by domain"). |
| R4 | **Met** | Filter matches on `cookie.path` (`server/browserContext.ts:284`); test at `tests/library/browsercontext-remove-cookies.spec.ts:61-88` ("should remove cookies by path"). |
| R5 | **Met** | Filter combines `name`/`domain`/`path` with AND semantics (`server/browserContext.ts:281-285`); four combination tests at `tests/library/browsercontext-remove-cookies.spec.ts:90-206` (name+domain, name+path, domain+path, name+domain+path). |
| R6 | **Met** | `removeCookies` composes `this.clearCookies()`/`this.addCookies()`, both of which are `browserContextId`-scoped per engine (`server/chromium/crBrowser.ts:414-415`, `server/firefox/ffBrowser.ts:298-299`, `server/webkit/wkBrowser.ts:275`); no cross-context effect is possible through this call path. |
| R7 | **Met** | Test `tests/library/browsercontext-remove-cookies.spec.ts:19-37` is exactly the motivating shape: two cookies are set (analogue of a globalSetup-seeded consent cookie plus another), one is removed by name, the other is confirmed to survive — matching "remove the GDPR cookie, leave the rest." |
| M1 | **Mentioned only, not counted** | See ledger/Observations — the literal array-of-cookie-objects signature was not delivered, but I judge that not to be a binding requirement. |

**Counts: Met = 7, Not met = 0, Unverifiable = 0.**

No candidates arose in either the "not met" or "scope creep" pass — see the ledger for what was weighed and why each near-miss was acquitted rather than passed through as a candidate.

## Candidates

None. Zero `requirements/*` and zero `requirements/unrequested/*` candidates met the bar for passing to the verifier. Everything I considered is accounted for in the disposition ledger below, with the evidence that acquitted it.

## Disposition ledger

| Claim | Falsification route | Decisive evidence | Disposition |
| --- | --- | --- | --- |
| `removeCookies` does not actually implement selective (name/domain/path) removal | Read `removeCookies` body and its filter predicate | `server/browserContext.ts:279-292` | acquitted |
| Removal is not scoped to the calling context (could leak to other contexts) | Trace `clearCookies`/`addCookies` to per-engine wire calls | `server/chromium/crBrowser.ts:414-415`, `server/firefox/ffBrowser.ts:298-299`, `server/webkit/wkBrowser.ts:275` (each keyed by `browserContextId`) | acquitted |
| Motivating GDPR-cookie-removal use case is untested/undelivered | Check test suite for a same-shape scenario | `tests/library/browsercontext-remove-cookies.spec.ts:19-37` | acquitted |
| Combination filtering (name+domain, name+path, domain+path, name+domain+path) is missing | Check for combination tests and AND-logic in filter | `server/browserContext.ts:281-285`; `tests/library/browsercontext-remove-cookies.spec.ts:90-206` | acquitted |
| Issue's literal `removeCookies([cookieObject1, cookieObject2])` array-of-cookie-objects signature is a binding requirement the diff fails | Check whether this is stated as the ask or as an illustrative example, and whether it was renegotiated with the issue author's own sign-off | Issue body frames it under "Example"; PR review comment 2 (`client/browserContext.ts:272`, maintainer) proposes the filter-object redesign; comment 3, the issue's own author, accepts: "Thank you for comments! Fixed." | acquitted → logged as Observation, not a not-met candidate |
| Single-filter-object API can't remove two arbitrarily different named cookies in one call, narrower than "cookie**s**" plural in the issue | Check whether the issue's core ask ("remove specific cookie/cookies from context") is satisfiable without a single heterogeneous batch call | A single filter (e.g. `{domain: 'x'}`) already removes many cookies at once; distinct cookies are removable via repeated calls; issue text never demands a single heterogeneous call | acquitted (same basis as above — not a distinct gap) |
| `protocol.yml` diff contains an unrelated change (creep) | Check what changed beyond the `removeCookies` block | `packages/protocol/src/protocol.yml:3234` — trailing-space-only fix on `ElectronApplication.events.console.parameters:`, no semantic/behavioral effect, unrelated class | acquitted (falls under the brief's "small obvious fix taken along the way is not creep" exemption — no user-visible behavior, no new interface/dependency/config surface) → logged as Observation |
| New protocol/validator/channel/dispatcher/types.d.ts plumbing (validator.ts, channels.ts, protocol.yml, types.d.ts, dispatcher) is unrequested scope creep beyond "add a method" | Check whether this plumbing is required to make the one requested method reachable at all, vs. optional extras | Every added line in these files is the standard multi-layer path every existing `BrowserContext` method (e.g. `clearCookies`) already goes through; none of it is optional or adds behavior beyond `removeCookies` itself | acquitted — necessary plumbing, not creep |
| Test file's 8th test (`should throw if empty object is passed`) validates behavior the issue never asked for | Check whether issue specifies empty-filter behavior | Issue is silent on this; the throw/validation behavior originates from PR review comment 1/10 (maintainer), not the issue | acquitted as out-of-axis (a Code/PR-review-driven detail, not an issue requirement, and not incorrect) — not logged as a finding |
| Exact-string `path`/`domain` matching (vs. cookie-spec prefix matching) might not satisfy "remove cookies by path/domain" as a real browser would interpret those fields | Check whether the issue specifies path/domain matching semantics | Issue text never mentions `path` or `domain` at all — those fields originate entirely from the PR review negotiation (comment 2), not the issue | acquitted as out-of-axis — if this is a defect it is a Code-axis correctness question about an implementation detail the issue never specified, not a Requirements gap |
| Whether the feature genuinely works identically across Chromium/Firefox/WebKit is unverifiable from static reading | Check for external evidence of actual execution | CI table in the shared prompt shows the new spec file (`browsercontext-remove-cookies.spec.ts:146`, WebKit) executed and is recorded only as "flaky" (failed-then-passed on retry), never red, across the reported runs — I did not execute anything myself; this is evidence supplied in the prompt, not something I ran | resolved via supplied evidence, not left as an "unverifiable" bucket item |

## Observations

- `packages/playwright-core/src/client/browserContext.ts:272` — the shipped `removeCookies(filter: {name?, domain?, path?})` takes a single filter object, not the issue's illustrated `removeCookies([cookieObject1, cookieObject2])` array of full cookie objects; the change was proposed by a maintainer in PR review comment 2 and explicitly accepted by the issue's own author (also the PR author) in comment 3.
- `packages/protocol/src/protocol.yml:3234` — the diff also removes a trailing space from `ElectronApplication.events.console.parameters:`, unrelated to `removeCookies` and with no semantic effect.

## Changed-file manifest — reviewed/ignored

| File | Disposition | Reason |
| --- | --- | --- |
| `docs/src/api/class-browsercontext.md` | reviewed | Documents the new method (`:1013-1027`); checked wording against the issue's ask and against the implemented signature. |
| `packages/playwright-core/src/client/browserContext.ts` | reviewed | Public client entry point for the requested capability (`:272-273`); anchor for the M1 observation. |
| `packages/playwright-core/src/client/network.ts` | reviewed | Defines `RemoveNetworkCookieParam` (`:61`), the filter type used by the client method; part of the requirement's necessary plumbing. |
| `packages/playwright-core/src/protocol/validator.ts` | reviewed | Adds `BrowserContextRemoveCookiesParams`/`Result` schemas (`:831-838`); confirms the filter reaches the server validated, part of requirement plumbing. |
| `packages/playwright-core/src/server/browserContext.ts` | reviewed | Core `removeCookies` logic (`:279-292`) — primary site for checking whether the issue's requested behavior is actually delivered; source for R1-R7 evidence. |
| `packages/playwright-core/src/server/dispatchers/browserContextDispatcher.ts` | reviewed | Wires the protocol call to the server implementation (`:227-228`); necessary plumbing, not creep. |
| `packages/playwright-core/types/types.d.ts` | reviewed | Public TypeScript declaration (`:8447-8455`) users see; checked wording/signature against the issue. |
| `packages/protocol/src/channels.ts` | reviewed | Protocol channel interface and param/result types (`:1430,1527-1537`); part of requirement plumbing. |
| `packages/protocol/src/protocol.yml` | reviewed | Protocol schema source of truth (`:1035-1043`) for the sweep and for the requirement; also contains the unrelated whitespace fix noted in Observations (`:3234`). |
| `tests/library/browsercontext-remove-cookies.spec.ts` | reviewed | Full 231-line, 8-test file read in full; primary evidence for whether R1-R7 are actually exercised (name/domain/path singly and in combination, plus the motivating-use-case shape). |

All 10 changed files were reviewed; none were ignored, and nothing was left unfinished.

## Closing statement

- **Git-history commands run:** `git status`, `git branch -a`, `git log --oneline -1`, `git rev-parse HEAD` — all run inside `/tmp/handoff4/run-v2a`. No `git show`, `git diff`, `git log` with any range/depth beyond 1, `git fetch`, or `git pull` were run. `git rev-parse HEAD` returned `cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b`, exactly the pinned head, and `git log --oneline -1` showed only that single commit (`cb02d5ba1 Update class-browsercontext.md`) — I did not read, and could not have read, any commit beyond the pinned head.
- **No network and no execution:** no `npm`/`node`/`tsc`/`eslint`/test-runner/build/fetch commands were run at any point; every claim above is from static reading, and CI-result evidence used above was supplied in the prompt, not obtained by me running anything.
- **Sandbox compliance:** every file read or grepped was under `/tmp/handoff4/run-v2a` (repository, via `Read`/`sed`/`grep` calls scoped with `cd /tmp/handoff4/run-v2a`) or `/tmp/handoff4/skill-v2a` (the two brief files: `finding-format.md`, `requirements-axis.md`), plus the prompt file itself (`/tmp/handoff4-requirements-finder-prompt.md`, read as explicitly required). I did not read any other `/tmp/handoff4/*` path — no other run's clone, no other skill snapshot, and no reports directory.

---

## 3. Verifier dispatch — exact prompt and verbatim report

Both finders returned candidates only from the Code axis (3; Requirements returned 0), so the
verifier trigger fired once, carrying all 3 Code candidates. Spawned via `Agent`,
`subagent_type: "general-purpose"`, `model: "sonnet"` passed explicitly, `run_in_background: false`.

### Exact prompt given to the verifier

```
You are the fresh-context Verifier sub-agent in a controlled prototype-review run using the skill `code-review-deep-publish`.

Read this brief first, in full, before anything else: /tmp/handoff4/skill-v2a/skills/code-review-deep-publish/references/verify.md

Follow it exactly. You are ruling on candidate findings from two independent finders reviewing pull request microsoft/playwright#29698 ("feat(playwright-core): add remove cookies api"). You have NOT seen the finders' reasoning or "support" fields — only the claims below, verbatim from the finders. Reconstruct or refute each claim from the code itself.

Repository: /tmp/handoff4/run-v2a
- Reviewed head: `review-head` branch, commit cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b
- Base / merge-base: `main` branch, commit 9a38aedf09f203a58008756e588324254abaef9a
- Diff: git diff main review-head (10 files, +334/-1)

Binding constraints, identical to the ones governing the rest of this run:
1. No network — no git fetch/pull, no gh, no curl, no web fetch, no network call of any kind.
2. No execution — no npm, npx, node, tsc, eslint, no test runner, no build. Static review only. Where a claim would ordinarily be settled by running something, say so instead of running it.
3. History is truncated at the pinned head on purpose. The newest object reachable in this clone is cb02d5ba1. Do not try to work around this. Report explicitly whether you read any history beyond the pinned head, and list every history command you ran (even ones that stayed within bounds, e.g. git log/git show/git diff).
4. Stay strictly inside /tmp/handoff4/run-v2a and /tmp/handoff4/skill-v2a. Do not read any other /tmp/handoff4/* path — no other run's clone, no other skill snapshot, no the reports directory. Report it if you read anything outside these two trees.
5. Do not add findings of your own beyond what's asked. Anything accurate you notice that the finders missed is an observation only, per verify.md — never a verdict on a new claim.

Three candidates to verify, all from the Code axis (the Requirements axis independently returned zero candidates on this run, so there is nothing from that axis to verify). For each, `support` (the finder's own reasoning/uncertainty notes) has been deliberately withheld — do not treat its absence as missing evidence; reconstruct each claim yourself from the code.

### Candidate 1
- id: code/browserContext-ts/removeCookies-clears-all-cookies-race-window
- axis: Code
- anchor: packages/playwright-core/src/server/browserContext.ts:291
- fix: (same as anchor)
- title: `removeCookies` clears the whole context's cookies before restoring the kept ones
- claim: [full claim text, as reproduced in Candidate 1 above]
- trigger: [full trigger text, as reproduced in Candidate 1 above]
- priority: P2
- action: must-fix

### Candidate 2
- id: code/types-d-ts/removeCookies-jsdoc-misstates-throw-condition
- axis: Code
- anchor: packages/playwright-core/types/types.d.ts:8442
- fix: (same as anchor)
- title: `removeCookies` JSDoc implies all three filter fields are required, contradicting the code and the doc
- claim: [full claim text, as reproduced in Candidate 2 above]
- trigger: [full trigger text, as reproduced in Candidate 2 above]
- priority: P3
- action: consider

### Candidate 3
- id: code/class-browsercontext-md/removeCookies-since-v1-43-mismatch
- axis: Code
- anchor: docs/src/api/class-browsercontext.md:1014
- fix: docs/src/api/class-browsercontext.md:1014 and docs/src/api/class-browsercontext.md:1028 (both `* since: v1.43` lines)
- title: `removeCookies`'s `since: v1.43` tag doesn't match the in-development version
- claim: [full claim text, as reproduced in Candidate 3 above]
- trigger: [full trigger text, as reproduced in Candidate 3 above]
- priority: P3
- action: consider

## What to return

Follow `references/verify.md` exactly for what to return: per candidate its id, the verdict (`confirmed`/`plausible`/`refuted`), one sentence of justification, the quoted line that supports the verdict for `confirmed`/`refuted`, the corrected trigger where you changed it, and the priority and action (each with a note if you moved it). Then the merge list (dedup), counts by verdict, and any observations (accurate asides outside your mandate — never a smuggled verdict).

Finally, close with:
- Every git-history command you ran, and an explicit statement of whether you read anything beyond the pinned head (cb02d5ba1).
- Confirmation of sandbox compliance: list every path outside /tmp/handoff4/run-v2a and /tmp/handoff4/skill-v2a that you read, or state that there were none.
- Confirmation that you ran no network and no execution commands.
```

*(The three `claim`/`trigger` fields were pasted verbatim in full, exactly as given in § 2's Candidates 1–3 above — abbreviated with `[...]` in this reproduction only to avoid tripling the same text; the actual dispatch carried the full text word-for-word.)*

### Verbatim verifier report

```
## Verdicts

### Candidate 1 — `code/browserContext-ts/removeCookies-clears-all-cookies-race-window`
**Verdict: confirmed**

The read-filter-clear-restore sequence is exactly as claimed, and all four cited call sites check out verbatim: `browserContext.ts:279-293`, `crBrowser.ts:414-416`, `wkBrowser.ts:275-277`, `ffBrowser.ts:298-300`. `removeCookies` is entirely new in this diff (`git diff main review-head -- .../browserContext.ts` shows it added at lines 279-293 with no prior version), so this is not a pre-existing bug being newly exposed — the new code is what introduces the unsafe clear-then-restore combination.

Quoted defect line: `packages/playwright-core/src/server/browserContext.ts:291-292`
```
    await this.clearCookies();
    await this.addCookies(cookiesToKeep);
```
`clearCookies()` (unscoped, whole-context) at `crBrowser.ts:415`: `await this._browser._session.send('Storage.clearCookies', { browserContextId: this._browserContextId });` — confirms it is not filtered.

Trigger: unchanged, matches the code exactly.
Priority: P2 — kept, requires concurrent state (not universal, so correctly not P0) but is a real data-loss bug.
Action: must-fix — kept; the merge consequence (silent, permanent loss of any cookie set on the context during the clear window) follows directly and mechanically from the code, not from speculation.

### Candidate 2 — `code/types-d-ts/removeCookies-jsdoc-misstates-throw-condition`
**Verdict: confirmed**

`types.d.ts:8442` reads exactly as quoted: `Removes cookies from context. The method will throw an error if either name, domain or path has not been passed.` The implementation at `browserContext.ts:280-281` throws only when **all three** are absent (`if (!filter.name && !filter.domain && !filter.path) throw ...`), i.e. only one is required — matching `docs/src/api/class-browsercontext.md:1016`: "At least one of the removal criteria should be provided." The `addCookies` cross-check also holds: `types.d.ts:8244-8248` matches `docs/src/api/class-browsercontext.md:299-303` word for word, confirming the generation pattern the `removeCookies` block deviates from.

Quoted defect line: `packages/playwright-core/types/types.d.ts:8442`
```
   * Removes cookies from context. The method will throw an error if either name, domain or path has not been passed.
```
vs. `packages/playwright-core/src/server/browserContext.ts:280-281`:
```
    if (!filter.name && !filter.domain && !filter.path)
      throw new Error(`Either name, domain or path are required`);
```

Trigger: unchanged, matches the code.
Priority: P3 — kept.
Action: consider — kept; a doc-wording defect with no runtime consequence.

### Candidate 3 — `code/class-browsercontext-md/removeCookies-since-v1-43-mismatch`
**Verdict: confirmed**

`package.json:4` and `packages/playwright-core/package.json:3` both read `"version": "1.42.0-next"`. The new `removeCookies` docs entries at `docs/src/api/class-browsercontext.md:1014` and `:1028` (both new in this diff — confirmed via `git diff main review-head`) tag `* since: v1.43`. A repo-wide grep of `docs/src/api/` for `since: v1.43` returns only these two lines; the pre-existing (not touched by this diff) unreleased-API tags in `class-electronapplication.md:45` and seven locations in `class-page.md` all use `since: v1.42`, matching the claim.

Quoted defect line: `docs/src/api/class-browsercontext.md:1014`
```
* since: v1.43
```
vs. `package.json:4`: `"version": "1.42.0-next",`

Trigger: unchanged, matches the code.
Priority: P3 — kept.
Action: consider — kept; a metadata/docs mismatch, no functional break.

## Merge list
No merges. All three candidates describe distinct defects (concurrency bug in server logic, JSDoc wording mismatch, docs version-tag mismatch) with no overlapping fix.

## Counts
- confirmed: 3
- plausible: 0
- refuted: 0

## Observations
- The `clearCookies()` implementations themselves are unchanged by this diff in all three backends (`git diff` shows no hunks touching those method bodies) — only the new call site inside `removeCookies` combines them into the unsafe sequence (`packages/playwright-core/src/server/browserContext.ts:291`).
- A new spec file `tests/library/browsercontext-remove-cookies.spec.ts` (231 lines) was added by this diff but was outside the scope of the three candidates and was not reviewed in detail.

## Git-history and sandbox compliance

Git commands run (all local, no network):
- `git status`
- `git branch -a`
- `git log --oneline -1` (current HEAD only, cb02d5ba1)
- `git diff main review-head -- packages/playwright-core/src/server/browserContext.ts`
- `git diff main review-head -- docs/src/api/class-browsercontext.md`
- `git diff main review-head --stat`
- `git diff main review-head -- packages/playwright-core/src/server/browserContext.ts packages/playwright-core/src/server/chromium/crBrowser.ts packages/playwright-core/src/server/webkit/wkBrowser.ts packages/playwright-core/src/server/firefox/ffBrowser.ts | grep -n "clearCookies"`

I read no history beyond the pinned head cb02d5ba1. All diffs were between the two provided local refs (`main` and `review-head`) already present in the clone; no `git fetch`, `git pull`, `git log` beyond `-1`, or any other traversal into ancestor/descendant commits was performed.

Sandbox: every file read was under `/tmp/handoff4/run-v2a` (repo content: `packages/playwright-core/src/server/browserContext.ts`, `packages/playwright-core/src/server/chromium/crBrowser.ts`, `packages/playwright-core/src/server/webkit/wkBrowser.ts`, `packages/playwright-core/src/server/firefox/ffBrowser.ts`, `packages/playwright-core/types/types.d.ts`, `docs/src/api/class-browsercontext.md`, `docs/src/api/class-electronapplication.md`, `docs/src/api/class-page.md`, `package.json`, `packages/playwright-core/package.json`) or `/tmp/handoff4/skill-v2a/skills/code-review-deep-publish/references/verify.md`. Nothing outside these two trees was read.

No network commands (no fetch/pull/gh/curl/web fetch) and no execution commands (no npm/npx/node/tsc/eslint/test runner/build) were run at any point — all verification was static (`sed`, `grep`, `cat`, `git status`/`branch`/`log -1`/`diff`).
```

**Verifier usage** (from the `Agent` result's usage block): 34,930 tokens, 16 tool uses, 117,420 ms.

---

## 4. Candidate disposition ledger

Merged across both finders and the verifier. "Origin" is which finder raised it; "Final disposition"
folds in the verifier's verdict where one applies.

| # | Axis | Anchor | Claim | Origin | Final disposition | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Code | `server/browserContext.ts:291` | `removeCookies` clears the whole context, not just the filtered subset — race window | Code finder | **Published** — finding, `must-fix` P2 | Verifier: `confirmed`, quoted `clearCookies()`/`addCookies()` sequence and unscoped per-engine `clearCookies` calls |
| 2 | Code | `server/browserContext.ts:540-544` | `_resetCookies()` precedent discharges the race concern | Code finder | Dropped (acquitted pre-verification) | Distinguishable usage context (reset-for-reuse vs. live user-invoked API); never became a candidate |
| 3 | Code | `server/browserContext.ts:286-289` | Filter still does substring matching (maintainer's original comment) | Code finder | Dropped (acquitted pre-verification) | Already fixed prior to reviewed head — uses `===`, not `.includes()` |
| 4 | Code | `server/browserContext.ts:280-283` | `cookies()` runs before the early-return guard, wasted work | Code finder | Dropped (acquitted pre-verification) | Already correctly ordered — guard precedes the call |
| 5 | Code | `server/browserContext.ts:279-293` | Parameter/variable naming is confusing | Code finder | Dropped (acquitted pre-verification) | No documented naming standard in `CONTRIBUTING.md`; maintainer already dismissed as stylistic |
| 6 | Code | `server/browserContext.ts:283` | `filter.domain === cookie.domain` may miss leading-dot domain cookies | Code finder | Dropped (acquitted pre-verification) | Rests on an unstated assumption about stored cookie format; insufficiently evidenced |
| 7 | Code | `client/browserContext.ts:272-277` | No default param — zero-arg call gets an ungraceful error | Code finder | Dropped (acquitted pre-verification) | Consistent with existing codebase rigor; TS-typechecker-guarded like sibling methods |
| 8 | Code | `types.d.ts:8442` | JSDoc misstates the throw condition (implies all 3 fields required) | Code finder | **Published** — finding, `consider` P3 | Verifier: `confirmed`, quoted the JSDoc line against the code's actual guard |
| 9 | Code | `class-browsercontext.md:1014,1028` | `since: v1.43` wrong for the 1.42 dev cycle | Code finder | **Published** — finding, `consider` P3 | Verifier: `confirmed`, quoted `package.json` version against the tag |
| 10 | Code | `protocol.yml:1033-1043` | `removeCookies:` entry breaks alphabetical `BrowserContext` block ordering | Code finder | **Published — Observation** | No documented ordering rule and no behavioral effect; bypasses verifier by rule (finder-level observation) |
| 11 | Code | `channels.ts:238-259`, `server/network.ts:57-75` | Round-trip through clear+readd loses cookie-field fidelity (`httpOnly`/`secure`/`sameSite`/`expires`) | Code finder | Dropped (acquitted pre-verification) | Structurally compatible types; `rewriteCookies` only touches fields when `url` is set, which it never is here |
| 12 | Code | `tests/library/browsercontext-remove-cookies.spec.ts` | New test file naming inconsistent with `browsercontext-clearcookies.spec.ts` | Code finder | Dropped (acquitted pre-verification) | No single naming convention exists in the directory to violate |
| 13 | Code | `tests/library/browsercontext-remove-cookies.spec.ts:90-206` | Test logic doesn't actually exercise the AND-combination semantics it claims | Code finder | Dropped (acquitted pre-verification) | Traced and confirmed correct against the filter's AND semantics |
| 14 | Code | n/a (commit subjects, API shape) | Commits/API violate `CONTRIBUTING.md`'s commit-message or API-guideline rules | Code finder | Dropped (acquitted pre-verification) | PR title matches the semantic-commit format; the one non-conforming commit is the maintainer's own doc-only commit, not attributable to the contributor's change |
| 15 | Code | `docs/src/api/class-browsercontext.md` | Doc summary doesn't spell out AND semantics of combined filters | Code finder | Not raised (out of axis) | Explicitly deferred to the Requirements axis as a completeness question; Requirements axis did not raise it either (R5 was judged Met) |
| 16 | Requirements | `server/browserContext.ts:279-292` | `removeCookies` doesn't actually implement selective removal | Requirements finder | Dropped (acquitted pre-verification) | Read the body; correctly filters by name/domain/path |
| 17 | Requirements | `server/{chromium,firefox,webkit}/*Browser.ts` | Removal leaks to other contexts | Requirements finder | Dropped (acquitted pre-verification) | Every backend call is `browserContextId`-scoped |
| 18 | Requirements | `tests/.../browsercontext-remove-cookies.spec.ts:19-37` | Motivating GDPR use case is untested | Requirements finder | Dropped (acquitted pre-verification) | Directly-shaped test exists and passes the scenario |
| 19 | Requirements | `server/browserContext.ts:281-285` | Combination filtering (name+domain+path) missing | Requirements finder | Dropped (acquitted pre-verification) | AND-logic implemented; 4 combination tests present |
| 20 | Requirements | `client/browserContext.ts:272` | Issue's literal array-of-cookie-objects signature (M1) is a binding requirement the diff fails | Requirements finder | **Published — Observation** | Negotiated away and explicitly accepted by the issue's own author in PR review; not a live gap |
| 21 | Requirements | `client/browserContext.ts:272` | Single-filter-object API narrower than "cookies" plural in the issue | Requirements finder | Dropped (acquitted pre-verification) | Same basis as #20 — not a distinct gap; repeated calls satisfy the plural case |
| 22 | Requirements | `protocol.yml:3234` | Unrelated trailing-whitespace change is scope creep | Requirements finder | **Published — Observation** (merged with #10's sibling item) | No user-visible behavior, no new interface/dependency/config surface — falls under the "small obvious fix" exemption |
| 23 | Requirements | `validator.ts`, `channels.ts`, `protocol.yml`, `types.d.ts`, dispatcher | New protocol plumbing is scope creep beyond "add a method" | Requirements finder | Dropped (acquitted pre-verification) | Standard multi-layer path every existing `BrowserContext` method already goes through; not optional |
| 24 | Requirements | `tests/.../browsercontext-remove-cookies.spec.ts` (8th test) | Empty-filter-throws test validates unrequested behavior | Requirements finder | Dropped (acquitted, out-of-axis) | Originates from PR review (maintainer), not the issue; not incorrect, just not this axis's concern |
| 25 | Requirements | n/a | Exact-string domain/path matching might not satisfy real cookie-spec semantics | Requirements finder | Dropped (acquitted, out-of-axis) | Issue never specifies matching semantics; a Code-axis question at most |
| 26 | Requirements | n/a | Cross-browser behavioral identity is unverifiable statically | Requirements finder | Resolved, not a candidate | Settled by supplied CI evidence in the prompt (WebKit run flaky-then-green, never red); not left in the "cannot tell" bucket |
| 27 | Verifier | `chromium/crBrowser.ts`, `webkit/wkBrowser.ts`, `firefox/ffBrowser.ts` | `clearCookies()` bodies are themselves unchanged by this diff; only the new call site combines them unsafely | Verifier | Considered, not separately published | Substantively folds into Finding 1's own evidence (confirms the defect is compositional/new, not pre-existing); redundant as a distinct Observations-section item and would have exceeded the 3-item cap |
| 28 | Verifier | `tests/.../browsercontext-remove-cookies.spec.ts` | New spec file was not reviewed in detail by the verifier | Verifier | Dropped | A scope/process note about the verifier's own coverage, not an artifact fact ("what is") — not a fit for the Observations section, and would have exceeded the 3-item cap regardless |

Three of the accurate, sub-threshold items above (#10/#22 merged, and #20) were selected for the
published `## Observations` section, capped at 3 by `publishing.md`; #27 and #28 were considered
and dropped to stay within that cap, per "keep the three with the most decisive evidence and drop
the rest."

---

## 5. Everything consulted beyond the diff

**By the Code finder** (per its own report): base-branch `CONTRIBUTING.md`; the abstract
`addCookies`/`clearCookies`/`doGetCookies` declarations and the `_resetCookies()` precedent in
`server/browserContext.ts`; all three per-engine backend implementations
(`server/chromium/crBrowser.ts`, `server/firefox/ffBrowser.ts`, `server/webkit/wkBrowser.ts`);
`server/network.ts` (`filterCookies`/`rewriteCookies`); the sibling `addCookies` JSDoc block in
`types.d.ts` and its doc source, as a generation-fidelity control; `utils/doclint/since.js` and
`utils/doclint/api_parser.js` (to establish what the `npm run doc` lint does and does not check);
sibling `since:` tags across `docs/src/api/class-electronapplication.md` and
`docs/src/api/class-page.md`; the sibling test file `tests/library/browsercontext-cookies.spec.ts`
(import path and license-header convention check); `packages/protocol/src/channels.ts` structural
comparison for cookie-field fidelity.

**By the Requirements finder** (per its own report): the originating issue
`microsoft/playwright#29662` with its comments; `clearCookies` repo-wide grep results, including
files outside the changed-file manifest — `packages/playwright-core/src/server/chromium/protocol.d.ts`,
`.../firefox/protocol.d.ts`, `tests/library/browsercontext-add-cookies.spec.ts`,
`tests/library/browsercontext-clearcookies.spec.ts`, `tests/library/defaultbrowsercontext-1.spec.ts`,
`tests/library/browsertype-launch.spec.ts`, `utils/generate_types/test/test.ts`,
`docs/src/puppeteer-js.md`; each engine's context class (`CRBrowserContext`, `FFBrowserContext`,
`WKBrowserContext`) to verify `browserContextId` scoping; the CI status table supplied in the
packet (not independently fetched).

**By the verifier**: `package.json` and `packages/playwright-core/package.json` (version fields);
`docs/src/api/class-electronapplication.md` and `docs/src/api/class-page.md` (sibling `since:` tag
comparison); the same three per-engine backend files as the Code finder; `references/verify.md`
itself.

**By this orchestrator (this session)**: the full skill directory (`SKILL.md`, `DESIGN.md`, all
five `references/*.md` files, `ATTRIBUTION.md`, `agents/openai.yaml`); the full packet
(`/tmp/handoff4/packet-playwright.md`); both finder reports in full; `CONTRIBUTING.md` at the base
commit, read in full (`git show main:CONTRIBUTING.md`, 249 lines, three reads covering 1–249 with
overlap, no gaps); `git branch -a`, `git rev-parse HEAD`, `git log --oneline -5`, `git status`,
`git log --oneline main..review-head` (sandbox/state confirmation); `git diff main review-head
--unified=0` scoped to each of the three finding files, to validate the three anchors against the
diff before rendering the would-be review, per `publishing.md`.

None of the above — by any participant — is outside `/tmp/handoff4/run-v2a` or
`/tmp/handoff4/skill-v2a`. See § 7(e).

---

## 6. Would-be published review, verbatim

Publication is disabled (binding constraint 4). This is rendered exactly as it would be submitted
via `gh api --method POST repos/microsoft/playwright/pulls/29698/reviews`, with `event: "COMMENT"`
per the packet's posting-identity determination (`kamui`, non-author, ordinary first review — no
authorization to gate merge was given, so `COMMENT` carries the status in words rather than
`REQUEST_CHANGES`).

### Review body

```markdown
**Changes Requested (advisory)** — 1 blocking finding, 2 optional findings, 0 open questions.

Code: Findings — 1 blocking, 2 optional. Requirements: Passed (7/7 restated requirements met;
issue alignment available via microsoft/playwright#29662).
Reviewed `cb02d5ba1` against `main` (merge-base `9a38aedf0`). Coverage: complete (10/10 files).

This adds `BrowserContext.removeCookies(filter)`, letting callers remove cookies by name, domain,
and path — singly or combined — instead of clearing the whole context; all seven restated issue
requirements are met, and the new 231-line test file exercises each one, including the motivating
GDPR-cookie use case. The one thing to fix before merge: the implementation clears every cookie in
the context and only re-adds the ones it means to keep, so a cookie set on any page in the context
during that window is silently and permanently lost. The two `consider` findings are both
doc/JSDoc-only mismatches and don't block.

### Code — Findings (1 blocking, 2 optional)
1. **[must-fix] [P2]** `removeCookies` clears the whole context's cookies before restoring the kept ones — `packages/playwright-core/src/server/browserContext.ts:291`
2. **[consider] [P3]** `removeCookies` JSDoc implies all three filter fields are required, contradicting the code and the doc — `packages/playwright-core/types/types.d.ts:8442`
3. **[consider] [P3]** `removeCookies`'s `since: v1.43` tag doesn't match the in-development version — `docs/src/api/class-browsercontext.md:1014`

### Requirements — Passed
7/7 restated requirements met (R1–R7); 0 not met; 0 unverifiable; 0 scope-creep candidates. Issue
alignment: available (`microsoft/playwright#29662`).

**Counts**: Code 3 findings (1 must-fix, 2 consider). Requirements 0 findings. 0 questions.

## Observations

These are accurate observations, not findings — no action is requested.

- `packages/protocol/src/protocol.yml`'s new `removeCookies:` entry breaks the `BrowserContext`
  block's previously-alphabetical method ordering (`packages/protocol/src/protocol.yml:1033-1043`);
  no documented rule requires the ordering, and later entries in the same block are already
  non-alphabetical.
- The diff also removes a trailing space from `ElectronApplication.events.console.parameters:` in
  `packages/protocol/src/protocol.yml:3234`, unrelated to `removeCookies` and with no semantic
  effect.
- The shipped `removeCookies(filter: {name?, domain?, path?})` single-filter-object signature
  differs from the issue's illustrated `removeCookies([cookieObject1, cookieObject2])`
  array-of-cookie-objects example (`packages/playwright-core/src/client/browserContext.ts:272`);
  the redesign was proposed by a maintainer in review and explicitly accepted by the issue's own
  author.

<!-- review-run workflow=v2a-1 head=cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b base-ref=main base-sha=9a38aedf09f203a58008756e588324254abaef9a merge-base=9a38aedf09f203a58008756e588324254abaef9a issues=microsoft/playwright#29662 coverage=complete -->
```

### Line comments (would-be `comments` array of the same API call)

**Comment 1** — `packages/playwright-core/src/server/browserContext.ts:291`, `side: RIGHT`

```markdown
**[Code] [must-fix] [P2] `removeCookies` clears the whole context's cookies before restoring the kept ones**

`packages/playwright-core/src/server/browserContext.ts:291-292` implements `removeCookies` as
read-filter-clear-restore: it snapshots `cookies()`, computes `cookiesToKeep`, then calls
`this.clearCookies()` — which in every backend (`crBrowser.ts:414-416`, `wkBrowser.ts:275-277`,
`ffBrowser.ts:298-300`) deletes **every** cookie in the context, not just the filtered ones — and
only afterward calls `this.addCookies(cookiesToKeep)` to restore the survivors. `cookies()`,
`clearCookies()`, and `addCookies()` are each a separate async round trip, so there is a real
window, not an atomic operation, in which the whole context is briefly empty.

**Triggers when**: any page sharing the `BrowserContext` sets or refreshes a cookie (navigation,
fetch response, or `document.cookie` write) while another caller is mid-`removeCookies()` call —
that cookie is absent when `clearCookies()` fires and is never restored by the subsequent
`addCookies(cookiesToKeep)`, because it postdates the pre-clear snapshot. It is silently and
permanently lost.

**Change**: delete only the matching cookies directly at the protocol layer (e.g. Chromium's CDP
exposes `Storage.deleteCookies`/`Network.deleteCookies` with name/domain/path filters; check for
equivalent per-cookie primitives in Firefox/WebKit) instead of the `clearCookies()` +
`addCookies(cookiesToKeep)` sequence at `packages/playwright-core/src/server/browserContext.ts:291-292`.
If a narrower fix is out of scope for this PR, document the known race explicitly.

<!-- finding id=code/browserContext-ts/removeCookies-clears-all-cookies-race-window axis=code action=must-fix priority=P2 head=cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b -->
```

**Comment 2** — `packages/playwright-core/types/types.d.ts:8442`, `side: RIGHT`

```markdown
**[Code] [consider] [P3] `removeCookies` JSDoc implies all three filter fields are required, contradicting the code and the doc**

`packages/playwright-core/types/types.d.ts:8442` reads "The method will throw an error if either
name, domain or path has not been passed" — read literally, this requires all three. The
implementation (`packages/playwright-core/src/server/browserContext.ts:280-281`) throws only when
**all three** are missing, and `docs/src/api/class-browsercontext.md:1016` correctly says "At
least one of the removal criteria should be provided." `types.d.ts` is generated from the markdown
docs and normally matches them verbatim (confirmed against the `addCookies` block,
`types.d.ts:8244-8248` vs `class-browsercontext.md:299-303`); the `removeCookies` block is the one
place that diverges.

**Triggers when**: a consumer reads the `removeCookies` JSDoc in their editor or in generated API
references and concludes all three of `name`/`domain`/`path` must be supplied together, when any
one alone suffices.

**Change**: correct `packages/playwright-core/types/types.d.ts:8442` to match
`docs/src/api/class-browsercontext.md:1016`'s wording, or regenerate `types.d.ts` from the doc
source.

Closing this without action is a correct response.

<!-- finding id=code/types-d-ts/removeCookies-jsdoc-misstates-throw-condition axis=code action=consider priority=P3 head=cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b -->
```

**Comment 3** — `docs/src/api/class-browsercontext.md:1014`, `side: RIGHT`

```markdown
**[Code] [consider] [P3] `removeCookies`'s `since: v1.43` tag doesn't match the in-development version**

`docs/src/api/class-browsercontext.md:1014` and `:1028` both tag the new API `* since: v1.43`, but
`package.json:4` and `packages/playwright-core/package.json:3` both declare
`"version": "1.42.0-next"` — the repository is mid-development for 1.42. Every other unreleased-API
`since` tag in this docs tree (e.g. `class-electronapplication.md:45`, seven tags in
`class-page.md`) uses `v1.42`; `removeCookies` is the only one using `v1.43`.

**Triggers when**: a user pinned to 1.42.x, or a tool cross-referencing published `since` metadata
for API-availability checks, reads "Added in: v1.43" and concludes the method isn't available in
their release — or the published docs simply carry the wrong version number until corrected. This
is not caught by the routine `npm run doc` lint, which only checks that a `since` tag exists, not
that its version is correct.

**Change**: change `* since: v1.43` to `* since: v1.42` at `docs/src/api/class-browsercontext.md:1014`
and `:1028`.

Closing this without action is a correct response.

<!-- finding id=code/class-browsercontext-md/removeCookies-since-v1-43-mismatch axis=code action=consider priority=P3 fix=docs/src/api/class-browsercontext.md:1014 head=cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b -->
```

### Equivalent `gh api` payload shape (for completeness — not executed)

```json
{ "commit_id": "cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b",
  "event": "COMMENT",
  "body": "<review body markdown above>",
  "comments": [
    { "path": "packages/playwright-core/src/server/browserContext.ts", "line": 291, "side": "RIGHT", "body": "<Comment 1 markdown above>" },
    { "path": "packages/playwright-core/types/types.d.ts", "line": 8442, "side": "RIGHT", "body": "<Comment 2 markdown above>" },
    { "path": "docs/src/api/class-browsercontext.md", "line": 1014, "side": "RIGHT", "body": "<Comment 3 markdown above>" }
  ] }
```

No `## Open questions` section (0 questions) and no `## Disputed` section (first review, no prior
findings to dispute) — both correctly omitted per `publishing.md`.

---

## 7. Specific answers

**(a) Did you or any sub-agent read git history beyond the pinned head? List every history command.**

No — none of the four participants (this orchestrator, the Code finder, the Requirements finder,
the verifier) read anything beyond `cb02d5ba1`, each confirmed explicitly in its own closing
statement. Every history command run, by participant:

- **This orchestrator**: `git branch -a`; `git rev-parse HEAD`; `git log --oneline -5`; `git
  status`; `git log --oneline main..review-head`; `git show main:CONTRIBUTING.md` (base-branch
  guidance read, ×3 invocations covering the full 249-line file); `git diff main review-head
  --unified=0 -- <each of the 3 finding files>` (anchor validation before rendering § 6).
- **Code finder**: `git branch --show-current`; `git rev-parse HEAD`. No `git log`, `git show`, or
  `git diff` at all.
- **Requirements finder**: `git status`; `git branch -a`; `git log --oneline -1`; `git rev-parse
  HEAD`.
- **Verifier**: `git status`; `git branch -a`; `git log --oneline -1`; `git diff main review-head
  -- packages/playwright-core/src/server/browserContext.ts`; `git diff main review-head --
  docs/src/api/class-browsercontext.md`; `git diff main review-head --stat`; `git diff main
  review-head -- <4 backend files> | grep -n "clearCookies"`.

All `git log` calls were bounded to `-1` or `-5` (current head and its immediate lineage, not
beyond it); all `git diff`/`git show` calls were between the two pinned local refs (`main` and
`review-head`) or against `main` for a single blob — none reached toward `origin` or attempted
`fetch`/`pull`.

**(b) How did you classify `CONTRIBUTING.md`, and did it materially support any finding?**

Classified as base-branch **repository guidance** under `SKILL.md`'s guidance contract ("evaluate
repository guidance — `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`, and
scoped equivalents — as of the base branch"), consistent with the packet's own framing (§7 of the
packet: "the only repository-rule document at base... treat it according to your own skill's
guidance contract"). It was the sole guidance document present at base (confirmed independently by
this orchestrator via `git show main:CONTRIBUTING.md`, read in full, 249 lines: How to Contribute,
Code reviews, Code Style, API guidelines, Commit Messages, Writing Documentation, Adding New
Dependencies, Running & Writing Tests, CLA, Code of Conduct — no naming-convention section).

It did **not** materially support any of the 3 published findings. It was consulted twice by the
Code finder and used only to **acquit** non-candidates: (1) it has no naming-convention section, so
`Smrtnyk`'s stylistic naming comments were acquitted as pedantic nitpicks rather than standards
violations (row #5 in § 4); (2) the PR's commits and API shape were checked against its
Commit-Messages and API-guidelines sections and found conforming, acquitting a hypothesized
violation (row #14). Candidate 2 (JSDoc mismatch) and Candidate 3 (`since` tag mismatch) are both
argued from generated-file/doc-sibling consistency and from `utils/doclint/*.js` behavior, not from
any `CONTRIBUTING.md` rule — `CONTRIBUTING.md`'s "Writing Documentation" section only establishes
that a doc linter exists and checks a `since` tag's *presence*, which is corroborating context in
Candidate 3's `support` (withheld from the verifier) but is never quoted as the violated rule in
the `claim` itself, and code-axis.md's "quote the rule and the line" bar for standards findings was
not invoked for either finding.

**(c) Which verification triggers does your skill define, which were evaluated, which fired?**

`SKILL.md` § 3 and `verify.md` define these triggers/routes:

1. **Spawn-verifier trigger** — any candidate exists across either finder → spawn one fresh-context
   verifier with all candidates, `support` withheld. *Evaluated: yes. Fired: yes* — 3 Code
   candidates existed.
2. **Skip-verifier condition** — "Finders that return no candidates on a first review make this
   step unnecessary; skip it." *Evaluated: yes, per axis. Did not apply overall*, since Code
   returned candidates; Requirements' zero-candidate result contributed zero items to the
   verifier's list but did not skip the step itself.
3. **"Cannot tell from the code" bypass** — Requirements candidates in that bucket route straight
   to a question and never reach the verifier. *Evaluated: yes — the Requirements finder's report
   states explicitly it produced zero items in that bucket (its one "unverifiable" candidate, R6's
   cross-browser question, was resolved via supplied CI evidence rather than left unverifiable).
   Did not fire* — there was nothing to route.
4. **Re-review prior-findings injection** — on a re-review, add prior findings whose fate turns on
   the code to the verifier's list. *Evaluated: yes (checked for applicability). Not applicable* —
   this is a first review; the packet's prior-review section (maintainer/third-party PR comments)
   predates the reviewed head and is out of scope for a fresh review's finding set, not something
   this run's identity (`kamui`) posted previously.

**(d) Coverage: all 10 changed files, reviewed/skipped, with a reason each.**

All 10 reviewed by both axes; none skipped by either. Per the merged manifests in § 2:

| File | Code axis | Requirements axis |
| --- | --- | --- |
| `docs/src/api/class-browsercontext.md` | reviewed — source of Candidate 3 | reviewed — doc wording vs. issue |
| `packages/playwright-core/src/client/browserContext.ts` | reviewed — no defect | reviewed — source of M1 observation |
| `packages/playwright-core/src/client/network.ts` | reviewed — no defect | reviewed — plumbing for the filter type |
| `packages/playwright-core/src/protocol/validator.ts` | reviewed — no defect | reviewed — plumbing |
| `packages/playwright-core/src/server/browserContext.ts` | reviewed — source of Candidate 1 | reviewed — primary R1-R7 evidence |
| `packages/playwright-core/src/server/dispatchers/browserContextDispatcher.ts` | reviewed — no defect | reviewed — plumbing |
| `packages/playwright-core/types/types.d.ts` | reviewed — source of Candidate 2 | reviewed — signature vs. issue |
| `packages/protocol/src/channels.ts` | reviewed — generated, mirrors `protocol.yml` | reviewed — plumbing |
| `packages/protocol/src/protocol.yml` | reviewed — source of both Observations | reviewed — source of the trailing-whitespace Observation |
| `tests/library/browsercontext-remove-cookies.spec.ts` | reviewed — full 231 lines, all 8 tests | reviewed — primary R1-R7 test evidence |

Coverage: **complete**.

**(e) Did you or any sub-agent read any other `/tmp/handoff4` path?**

No. Confirmed per-participant:

- This orchestrator read only: `/tmp/handoff4/packet-playwright.md`;
  `/tmp/handoff4/skill-v2a/skills/code-review-deep-publish/{SKILL.md,DESIGN.md,ATTRIBUTION.md,agents/openai.yaml,references/*.md}`;
  `/tmp/handoff4/run-v2a/**` (repo working tree and `git show main:...`);
  `/tmp/handoff4/reports/{v2a-finder-code.md,v2a-finder-requirements.md,v2a-report.md}` (the two
  named finder reports, and this document itself). One false start briefly created and then
  deleted two scratch copy files outside `/tmp/handoff4` (at `/tmp/handoff4-code-finder-copy.md`
  and `/tmp/handoff4-req-finder-copy.md`, i.e. siblings of, not inside, the `/tmp/handoff4/`
  directory) — they were never read by any sub-agent, added no information, and were removed
  immediately; disclosed here for completeness.
- The verifier confirmed (in its own closing statement) reading only files under
  `/tmp/handoff4/run-v2a` and the single brief `/tmp/handoff4/skill-v2a/.../references/verify.md`.
- The Code finder confirmed reading only `/tmp/handoff4/run-v2a`,
  `/tmp/handoff4/skill-v2a/.../references/{finding-format,code-axis}.md`, and its own prompt file.
- The Requirements finder confirmed reading only `/tmp/handoff4/run-v2a`,
  `/tmp/handoff4/skill-v2a/.../references/{finding-format,requirements-axis}.md`, and its own
  prompt file.

No participant read `run-v2`, `run-v5`, `run-v5a`, `skill-v2`, `skill-v5`, `skill-v5a`, or
`mirror-pw.git`.

---

## 8. Mechanism checklist

Against `DESIGN.md`'s numbered mechanisms:

- **C1 — Action decoupled from priority.** *Fired.* Candidate/Finding 1 is P2 yet `must-fix`
  (priority ≠ severity-derived action); Findings 2 and 3 are P3 `consider`. The verifier explicitly
  re-derived action independently each time ("Action: must-fix — kept; the merge consequence...
  follows directly... not from speculation" vs. "Action: consider — kept; a doc-wording defect with
  no runtime consequence") rather than deriving it from priority.
- **C2 — No-issue rule reviews the body's claims and non-goals.** *Not applicable.* An originating
  issue (`microsoft/playwright#29662`) is linked and was used as the spec; the no-issue path never
  engaged. The Requirements finder's report accordingly restates requirements from the issue, not
  the PR body, and reports "issue alignment: available."
- **C3 — Structured candidate disposition ledger from both finders.** *Fired.* Both finder reports
  carry compact 4-field ledgers (claim / falsification route / decisive evidence / disposition) —
  13 rows (Code) and 11 rows (Requirements), including pre-admission acquittals — reproduced in
  full in § 2 and merged in § 4.
- **C4 — Question routing codified.** *Evaluated, did not fire.* The Requirements finder reported
  zero items in the "cannot tell from the code" bucket, and the verifier returned zero `plausible`
  verdicts, so no candidate took the question route this run. The mechanism was live (both finder
  briefs and the verifier brief carry the routing rule) but had no occasion to trigger — a clean,
  fully-adjudicable run, not a gap.
- **C5 — The `Observations` section.** *Fired.* Both finders returned observations (protocol.yml
  ordering drift, protocol.yml whitespace fix, the M1 signature divergence), the verifier added two
  more, and the published review's `## Observations` (§ 6) carries exactly 3, each one sentence
  plus one `file:line` pointer, none anchored as a line comment, none counted in a total — matching
  `publishing.md`'s bound.
- **C6 — Closed-PR rule and trailer parity.** *Trailer-parity half fired; closed-PR half not
  applicable.* Every finding trailer and the `review-run` trailer in § 6 carry full 40-hex SHAs and
  `workflow=v2a-1`. The closed/merged-PR retrospective-review branch never engaged — the packet
  frames this as an ordinary first review of an open PR (posting identity `kamui`, non-author,
  event `COMMENT`), not a retrospective of a merged or closed one.
- **C7 — Token efficiency around the pole.** *Fired, structurally.* Both finder reports state their
  shared inputs (diff, commit list, manifest, guidance) "arrive in the prompt; do not re-fetch,"
  consistent with the shared-block-first construction this mechanism requires; this orchestrator
  cannot independently confirm prompt-cache hits from outside the harness, but the finders'
  behavior (no re-fetch of shared material) is the observable half of the mechanism and it held.
- **C8 — Paired peer-contract sweep before a requirement passes.** *Fired.* The Requirements
  finder's report contains an explicit "Changed-contract sweep" section running the mandatory
  two-term search (`removeCookies` new-term search, `clearCookies` old-sibling search) even though
  it concludes — correctly — that this diff is net-new API surface with no prior "removeCookies"
  wording to have gone stale, so no live peer was found stale.
- **C9 — Sweep trigger covers list-opening changes; Code axis sweeps for sync drift.** *Fired on
  the Code axis; evaluated-and-correctly-inapplicable on the Requirements axis.* Candidate 2 is
  exactly the sync-drift shape C9 targets: the Code finder identified `types.d.ts`'s JSDoc as a
  peer that normally mirrors the doc source verbatim (confirmed via the `addCookies` control
  comparison) and flagged it as stale relative to the diff's new doc wording — the "peer matched
  the doc pattern at base, the diff made it stale" mechanism, applied to a generated-file/doc pair
  rather than a vocabulary list. The Requirements finder's changed-contract scan explicitly
  considered whether this diff opens/retires a closed list and concluded it does not (pure net-new
  surface, no prior enum/list touched) — a correct "not applicable" rather than a skipped check.

---

## 9. Notes on the run

- **Mandatory disclosure**: this run's Verify and Publish phases were executed by a fresh
  orchestrator context after a rate limit killed the original, which had the same packet and the
  same two finder reports. The Find phase itself (both finder sub-agents) was not redone.
- **Judgment call — Observations cap.** Five accurate, sub-threshold items existed across both
  finders and the verifier (rows #10/#22, #20, #27, #28 in § 4); `publishing.md` caps the section
  at 3. Selected the three with the most self-contained, decisive `file:line` evidence and least
  overlap with the published findings (the protocol.yml ordering drift, the protocol.yml
  trailing-whitespace fix, and the M1 signature-divergence item); dropped the verifier's two asides
  as either redundant with Finding 1's own evidence or process-scoped rather than an artifact fact.
- **Judgment call — merging the duplicate whitespace observation.** Both finders independently
  flagged the same `protocol.yml:3234` trailing-whitespace fix. The skill does not explicitly say
  to dedup *observations* (`verify.md`'s dedup rule is written for candidates), but publishing it
  twice would have wasted one of only three available Observations slots for no new information, so
  it was merged into one item, by analogy to the candidate-dedup principle.
- **Judgment call — trailer `fix=` for Candidate 3.** The candidate names two fix sites
  (`class-browsercontext.md:1014` and `:1028`); `finding-format.md`'s trailer schema carries one
  `fix=file:line` token, so the primary site (`:1014`) went in the trailer and both sites are named
  in the `Change` prose, matching the ladder's stated split ("`Change` names the fix site in prose
  **and** the trailer carries it").
- **Judgment call — event/status render.** The packet's phase-1 resolution already determined the
  posting identity's authorization (`kamui`, non-author, "an ordinary first review, event
  COMMENT"), so this was applied directly rather than re-derived from `publishing.md`'s general
  authorization test; the derived status (`Changes Requested`) is rendered in words on the body's
  first line per `publishing.md`'s "Status versus forge event" section, as `COMMENT` has no gating
  form.
- **Surprise worth flagging.** The verifier confirmed all 3 candidates with zero refutations and
  zero merges — a "clean sweep" in this architecture's own terms. `DESIGN.md` calls out the
  verifier's refutation behavior as one of the architecture's load-bearing properties (test 1: "two
  false candidates removed, one cross-axis duplicate merged"); this run had no occasion to exercise
  that half of the mechanism, which is a fact about this particular diff (a small, cleanly-scoped,
  already-once-reviewed feature PR) rather than evidence the mechanism is inert — worth noting for
  anyone using this run as a comparator data point.
- **Anchor validation performed by the orchestrator, not simulated.** Before rendering § 6, this
  orchestrator independently ran `git diff main review-head --unified=0` against each of the three
  finding files and confirmed all three anchors (`browserContext.ts:291`, `types.d.ts:8442`,
  `class-browsercontext.md:1014`) fall inside diff-added line ranges, per `publishing.md`'s
  pre-submission validation instruction — this is the one Publish-phase step that has a real,
  checkable side effect even with posting disabled, and it passed cleanly on the first check.
- **Model verification caveat.** This session confirmed `model: "sonnet"` was passed explicitly on
  its own `Agent` call (the verifier) and the prompt text above proves it. It cannot independently
  re-verify, from this context, which model the two finder sub-agents actually ran on in the prior
  (now-unavailable) session beyond that prior session's own reports asserting the instruction was
  followed — the `[[subagent-model-must-be-explicit]]` lesson (harness default silently drifted to
  Fable 5.1 mid-program in an earlier phase of this same broader program) means that assertion,
  while the best evidence available here, is weaker than a transcript-verified `message.model`
  check would be. A full replication audit should pull the finder sub-agents' transcripts if they
  are still available.
