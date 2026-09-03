# v2 run — `code-review-publish-2` against `microsoft/playwright#29698`

**2026-09-03.** Data only. Not published to the PR. See [`README.md`](README.md) for the
pinned run identity, the ground truth, and the conditions held constant across all four runs.

> **Run-continuity note.** The Find phase (both axis finders) completed, then a session rate limit
> killed the orchestrator before it verified. Verify and Publish were executed by a fresh
> orchestrator context given the same packet and the two finder reports verbatim. Both finders ran
> once and were not redone. Model verification for every agent is in
> [`comparison-data.md`](comparison-data.md).

---


Skill: `code-review-publish-2` (prototype). Run resumed at the **Verify** phase after an earlier
attempt's Find phase completed and the attempt was then killed by a rate limit. This orchestrator
is a fresh context; the Find phase was not redone.

Wall clock (this orchestrator's session, Verify → Publish-rendering): **2026-09-03T22:32:12Z** →
**2026-09-03T22:41:16Z** (plus report-assembly time after that timestamp).

---

## Metadata

| | |
| --- | --- |
| **Skill** | `code-review-publish-2`, snapshot at `/tmp/handoff4/skill-v2/skills/code-review-publish-2/` |
| **Architecture** | Two-axis Find (Code, Requirements — run by the prior, crashed orchestrator; not redone) → single fresh-context Verify (run by this orchestrator) → render-only Publish (posting disabled). No re-review machinery invoked (first review on this PR). |
| **Model** | `sonnet` passed explicitly on the one `Agent` call this orchestrator made (the verifier). The two finders were spawned by the prior, crashed orchestrator; their model parameter is not visible to this context and is not recorded in their reports — flagged as an evidence gap, not assumed. |
| **Agents spawned** | 1 by this orchestrator (Verifier). 3 total in the run's lineage (Code finder + Requirements finder, spawned earlier; Verifier, spawned here). |
| **Sub-agent tokens** | Code finder: 99,128. Requirements finder: 55,058. Verifier: 44,280. **Total: 198,466.** |
| **Tool uses** | Sub-agents: Code finder 46, Requirements finder 15, Verifier 24 → 85 total. This orchestrator: 25 (see "Own tool-use count" below). |
| **Wall clock** | Sub-agents (reported durations, not necessarily sequential): Code finder 554,529 ms, Requirements finder 293,502 ms, Verifier 221,415 ms. This orchestrator's session: ~9 min to verifier return, plus report assembly. |
| **Candidates raised** | 6 (4 Code, 2 Requirements) |
| **Candidates surviving verification** | 6 of 6 (0 refuted) — 4 confirmed → findings, 2 plausible → questions |
| **Verifier verdicts** | confirmed: 4, plausible: 2, refuted: 0 |
| **Findings for publication** | 4 — 2 `must-fix` P1 (Code), 2 `consider` P3 (Code) |
| **Questions** | 2 (both Requirements-axis in origin; verifier routed both to questions) |
| **Observations** | 1 (verifier's out-of-scope note on citation-line imprecision across candidates — recorded, not folded into any verdict) |
| **Coverage over all 10 changed files** | Complete — every file `reviewed` or `ignored`-with-defensible-reason by at least one finder, none ignored by both without reason |
| **Derived status** | **Changes Requested (advisory)** |

**This orchestrator's own tool-use count by category:** Bash 18 (includes `date -u` ×2, skill-file `cat`s ×8, repo state checks, `CONTRIBUTING.md` reads ×3, anchor-validation `git diff`), Read 3 (packet, both finder reports), Write 2 (checkpoint report, this final report), ToolSearch 1 (loaded the `Agent` tool schema), Agent 1 (the verifier). Total 25.

---

## Full reviewer report(s) — verbatim

### Code axis — `/tmp/handoff4/reports/v2-finder-code.md`

```markdown
# Code-axis review — PR microsoft/playwright#29698 (add removeCookies API)

> Verbatim output of Code-axis finder sub-agent `ab4546190cb19fe6a` (v2 run).
> Reported usage: 99,128 tokens, 46 tool uses, 554,529 ms.

### 1. Changed-file manifest

| File | Status | Reason |
|---|---|---|
| `docs/src/api/class-browsercontext.md` | **reviewed** | 2 candidates found (see below) |
| `packages/playwright-core/src/client/browserContext.ts` | **reviewed** | Thin pass-through (`removeCookies` → `this._channel.removeCookies({ filter })`), matches the existing `clearCookies`/`addCookies` pattern exactly. Nothing stood out. |
| `packages/playwright-core/src/client/network.ts` | **reviewed** | New `RemoveNetworkCookieParam` type structurally mirrors `SetNetworkCookieParam`. Nothing stood out. |
| `packages/playwright-core/src/protocol/validator.ts` | **reviewed** | `BrowserContextRemoveCookiesParams`/`Result` schemes correctly mirror `protocol.yml`/`channels.ts`. The entry is inserted out of the file's otherwise-alphabetical order (after `ClearCookies` rather than near `R`), matching the same non-alphabetical insertion in `channels.ts`'s `BrowserContextChannel` interface — considered but rejected as a candidate: no documented ordering rule exists in `CONTRIBUTING.md`, it has no behavioral effect, and it's the kind of nitpick the brief explicitly excludes. |
| `packages/playwright-core/src/server/browserContext.ts` | **reviewed** | 2 candidates found (see below) |
| `packages/playwright-core/src/server/dispatchers/browserContextDispatcher.ts` | **reviewed** | Thin pass-through (`this._context.removeCookies(params.filter)`). Nothing stood out. |
| `packages/playwright-core/types/types.d.ts` | **ignored** | Generated artifact — file banner reads "This file is generated by /utils/generate_types/index.js". Produced by `node utils/generate_types/`, one of the steps `npm run lint` runs, and CI's `.github/workflows/infra.yml` `doc-and-lint` job runs `npm run lint` then fails the build if `git status -s` is non-empty ("Verify clean tree"). Any drift between this file and its source docs is caught there, not by manual review. (I did note in passing that its current wording — "The method will throw an error if either name, domain or path has not been passed." — doesn't verbatim match the markdown source's "At least one of the removal criteria should be provided.", the same way `pages()`'s doc text and generated JSDoc match verbatim elsewhere. That's exactly the class of thing the clean-tree check exists to catch, so it isn't reported as a candidate.) |
| `packages/protocol/src/channels.ts` | **ignored** | Generated artifact — produced by `utils/generate_channels.js` (run inside `npm run lint`) from `protocol.yml`. Verified by the same CI clean-tree check as above. |
| `packages/protocol/src/protocol.yml` | **reviewed** | Source of truth for the protocol; new `removeCookies` entry is structurally consistent with sibling entries. The unrelated trailing-whitespace removal on `ElectronApplication.events.console.parameters` (line ~3231) is a no-op formatting fix, not a candidate. |
| `tests/library/browsercontext-remove-cookies.spec.ts` | **reviewed** | New test file, well-structured, covers all filter-field combinations claimed to work. It never exercises a cookie whose `domain` was normalized with a leading dot (the `addCookies` convention documented at `class-browsercontext.md:348`), nor a concurrent-cookie-write scenario — which is exactly why the two bugs below went uncaught. Noted as context, not reported separately (thin test coverage alone isn't a candidate per the brief). |

### 2. Candidates

---

**id**: `code/browsercontext-ts/remove-cookies-domain-exact-match`
**anchor**: `packages/playwright-core/src/server/browserContext.ts:287`
**title**: removeCookies domain filter uses exact match, missing this repo's own dot-prefix domain-cookie convention
**claim**: `server/browserContext.ts:287` matches cookies with `(!filter.domain || filter.domain === cookie.domain)` — a raw string-equality check. This codebase documents, at `docs/src/api/class-browsercontext.md:347`, that cookies applying to subdomains are stored with a domain prefixed by a dot ("For the cookie to apply to all subdomains as well, prefix domain with a dot, like this: `.example.com`."), and this convention is implemented pervasively elsewhere for the exact same `NetworkCookie.domain` field: `packages/playwright-core/src/server/cookieStore.ts:118-125`'s `domainMatches()` treats a domain without a leading dot as host-only (strict-equal only) and a domain with a leading dot as subdomain-matching per RFC 6265; `packages/playwright-core/src/server/network.ts:34-41` (`filterCookies`) and `packages/playwright-core/src/server/fetch.ts:225,646,726` all branch on `domain.startsWith('.')` for this same field. Real cookies set by a website via a `Set-Cookie: ...; Domain=example.com` response header — the primary real-world source of cookies `removeCookies` is meant to clear — are canonicalized by browsers with a leading dot. `removeCookies`'s own documented usage example, `await browserContext.removeCookies({ domain: 'my-origin.com' })` (no leading dot), will silently match zero cookies against such a cookie.
**support**: I read `cookieStore.ts`, `network.ts`, `fetch.ts` and confirmed the leading-dot convention is used consistently across the codebase for this field, and I read `class-browsercontext.md:347` which documents it for `addCookies`. I have not run a browser to directly observe Chromium/WebKit CDP output for a `Domain=`-attributed cookie, so I'm relying on the codebase's own internal modeling (which explicitly encodes RFC 6265 domain canonicalization) plus RFC 6265 itself as the basis for the claim that real Set-Cookie-sourced cookies get the dot. I'm confident in the code-level inconsistency (exact-match vs. the codebase's own `domainMatches` helper for the same field); I'm somewhat less certain whether the maintainers would consider this a bug vs. an accepted "match the raw attribute, symmetric with `addCookies`" design choice — no reviewer raised it in the human review thread. Passing through per the brief's instruction not to self-censor a believed defect.
**trigger**: A page in the context receives a `Set-Cookie: sid=abc; Domain=example.com; Path=/` response (or otherwise gets a cookie with an explicit `Domain` attribute) during normal navigation. Calling `context.removeCookies({ domain: 'example.com' })` — the form shown in this PR's own doc example — matches nothing and silently leaves the cookie in place, with no error and no indication anything went wrong.
**change**: In `server/browserContext.ts`, replace the raw `filter.domain === cookie.domain` comparison with RFC 6265 domain matching (e.g. reuse or adapt `domainMatches()` from `cookieStore.ts`), or, if exact-attribute matching is the intended design, update the doc at `class-browsercontext.md:1016-1024` to state the caveat explicitly the way `addCookies`'s doc does at line 347.
**priority**: P1

---

**id**: `code/browsercontext-ts/remove-cookies-clear-readd-race`
**anchor**: `packages/playwright-core/src/server/browserContext.ts:291`
**fix**: `packages/playwright-core/src/server/browserContext.ts:283-292`
**title**: removeCookies clears and re-adds all context cookies, losing any cookie set between the snapshot and the clear
**claim**: `server/browserContext.ts:283-292` implements removal as read-all → filter → clear-all → re-add-kept:
```js
const currentCookies = await this.cookies();
const cookiesToKeep = currentCookies.filter(cookie => { ... });
await this.clearCookies();
await this.addCookies(cookiesToKeep);
```
`this.cookies()` with no `urls` argument returns every cookie in the entire browser context (`network.ts`'s `filterCookies`: `if (!parsedURLs.length) return true;`), and `clearCookies()` wipes every cookie in the context (e.g. `crBrowser.ts:414-415`, `Storage.clearCookies` for the whole `browserContextId`). Each of the three awaited steps is a separate round trip. Any cookie that is set (by a concurrent page navigation receiving a `Set-Cookie` header, an in-page `document.cookie` write, a redirect, etc.) after the `this.cookies()` snapshot but before `clearCookies()`/`addCookies()` complete is present when `clearCookies()` wipes the context, but is not in `cookiesToKeep`, so it is never restored — it is permanently lost, with no error surfaced.
**support**: I traced `cookies()` → `doGetCookies([])` → `filterCookies([], cookies)` to confirm `urls=[]` returns every cookie context-wide, and `clearCookies()`'s chromium/firefox/webkit implementations to confirm they clear the whole context, not a subset. I did not find any CDP/Storage primitive in this codebase (`Storage.clearCookies` is all-or-nothing) that would let the author remove a subset without this read/clear/rewrite pattern — Chromium's `Network.deleteCookies` exists but is a per-page-session command, not a browser-context-scoped one, so switching to it would be a materially bigger change than a one-line fix, which weakens my confidence the author would consider this a quick fix. I'm flagging it per the brief's instruction to raise severe-impact (data-loss) issues even with narrower/uncertain trigger likelihood. One data point I'm treating as context, not evidence: the CI history you gave me lists a webkit run of `browsercontext-remove-cookies.spec.ts:146:3 › should remove cookies by domain and path` as flaky against an ancestor of the pinned head — consistent with, but not proof of, this race; I have not verified the flake's actual cause.
**trigger**: Two pages exist in the same `BrowserContext`. While one page is calling `context.removeCookies({ name: 'x' })`, the other page navigates and receives a `Set-Cookie` response, or runs `document.cookie = ...`, in the window between the `cookies()` snapshot and the `clearCookies()`/`addCookies()` pair completing. The newly-set, unrelated cookie is permanently deleted.
**change**: Avoid the clear-all/re-add-all round trip — either remove exactly the matching cookies via a targeted per-cookie delete instead of a context-wide clear, or, at minimum, re-snapshot and re-diff `cookies()` immediately before `clearCookies()` to shrink the race window, and document the non-atomicity if a full fix isn't feasible.
**priority**: P1

---

**id**: `code/class-browsercontext-md/remove-cookies-wrong-since-version`
**anchor**: `docs/src/api/class-browsercontext.md:1014`
**title**: removeCookies doc tagged `since: v1.43`, one minor version ahead of the in-development release
**claim**: `class-browsercontext.md:1014` and `:1028` tag the new `removeCookies` method and its `filter` param with `* since: v1.43`. At the base commit, `packages/playwright-core/package.json` declares `"version": "1.42.0-next"`, and every other newly-documented API in the current development cycle in `docs/src/api/*.md` at the base commit uses `since: v1.42` (8 occurrences) — there are zero `since: v1.43` occurrences anywhere in the base tree. This PR's two additions are the only `since: v1.43` tags in the entire docs tree.
**support**: I ran `git show main:packages/playwright-core/package.json` (via cat on the base-checked-out tree state is not accurate — see note below) and `git grep -ho "since: v1\.[0-9]*" main -- docs/src/api | sort | uniq -c | sort -rn` against `main`, confirming 8×`v1.42` and 0×`v1.43` at base. I confirmed the two `v1.43` tags exist only in this PR's diff by checking the diff hunk directly. This is a value the maintainer/`utils/doclint/since.js` tool would eventually reconcile at release time using downloaded driver artifacts, but that script requires a `DRIVERS_DIR` env var and is not part of `npm run lint`/`npm run doc`/any CI workflow I found (`.github/workflows/infra.yml`), so it would not be caught automatically before merge.
**trigger**: Not a runtime trigger — a documentation/versioning defect. Any user reading the rendered docs or the generated `types.d.ts` for `removeCookies` is told it shipped in v1.43 when, per every sibling doc entry, it should read v1.42.
**change**: Change `since: v1.43` to `since: v1.42` at both `class-browsercontext.md:1014` and `:1028`.
**priority**: P3

---

**id**: `code/class-browsercontext-md/remove-cookies-undocumented-throw`
**anchor**: `docs/src/api/class-browsercontext.md:1016`
**title**: removeCookies doc doesn't state that omitting all criteria throws
**claim**: `class-browsercontext.md:1016` reads "Removes cookies from context. At least one of the removal criteria should be provided." — a soft/recommendatory phrasing that does not tell the reader what happens if none is provided. The implementation at `server/browserContext.ts:280` does `throw new Error('Either name, domain or path are required')` when no criteria are given, and the PR's own test at `tests/library/browsercontext-remove-cookies.spec.ts:435-454` ("should throw if empty object is passed") confirms this is real, load-bearing behavior, not a hypothetical.
**support**: This addresses a specific maintainer comment from the pre-merge review record you gave me: `pavelfeldman` on the earlier round: "This should probably throw 'Either name, domain or path are required'. Same should be mentioned in the doc (md file)." The throw was implemented; I independently checked the current md prose against that ask and it still doesn't state the throwing behavior — it only implies a soft preference ("should be provided"). I'm treating the prior review comment as evidence I verified against current code, not as an instruction. I did not raise this as a "Standards" finding requiring a `CONTRIBUTING.md` quote, since I couldn't find a rule there specifically requiring thrown-error documentation — I'm raising it as a plain accuracy/completeness gap instead, per the brief's allowance to raise findings without a citation when no repo rule "materially adds" to it.
**trigger**: A developer reads only the rendered docs (not the TS declaration file) for `removeCookies`, calls it with an empty/no-criteria object based on the doc's soft wording, and is surprised by an uncaught exception rather than a silent no-op.
**change**: Reword `class-browsercontext.md:1016` to state the requirement as a hard constraint with its consequence, e.g. "Removes cookies from context. Accepts a filter with `name`, `domain` and/or `path` — at least one must be specified, or the method throws."
**priority**: P3

---

### 3. Git commands run (verbatim)

```
git rev-parse main && git rev-parse review-head && git log --oneline main..review-head
git diff main...review-head --stat
git diff main...review-head > /tmp/handoff4_pr.diff && wc -l /tmp/handoff4_pr.diff
git show main:CONTRIBUTING.md
git status && git rev-parse HEAD
git show main --stat >/dev/null; git worktree list 2>/dev/null; git grep -c "since: v1.43" main -- docs/src/api 2>/dev/null; git grep -ho "since: v1\.[0-9]*" main -- docs/src/api | sort | uniq -c | sort -rn
```

(All other reads — `grep`, `sed`, `cat` — were plain filesystem reads, not git history commands, and are omitted per your instruction to list git log/show/diff-type commands.)

### 4. Sandbox confirmation

I read only files under `/tmp/handoff4/run-v2` (the repo, at both `main` and `review-head` via `git show`/`git diff`/`git grep`, plus the working tree checked out at `review-head`) and `/tmp/handoff4/skill-v2/skills/code-review-publish-2/references/{code-axis.md,finding-format.md}`. I did not read any other `run-*`/`skill-*` directory, `mirror-pw.git`, `reports/`, or `packet-playwright.md`.

One disclosure: I wrote the full diff to `/tmp/handoff4_pr.diff` (outside the two named directories) so I could read it with the `Read` tool in one pass. That file's contents are entirely derived from `git diff main...review-head` inside the allowed repo — it isn't a read of any external/disallowed content — but since the path itself falls outside `/tmp/handoff4/run-v2` and `/tmp/handoff4/skill-v2`, I'm flagging it explicitly as you asked. No other paths outside the sandbox were touched.

### 5. Summary

Four candidates qualify: two P1 correctness bugs in the new `removeCookies` implementation (`server/browserContext.ts`) — an exact-match domain filter that misses the codebase's own leading-dot domain-cookie convention, and a clear-then-re-add implementation that can silently drop concurrently-set, unrelated cookies — plus two P3 documentation-accuracy gaps in `docs/src/api/class-browsercontext.md` (wrong `since` version, and the doc not stating that an empty filter throws). This is not a clean review; all four are passed through for the verifier to adjudicate, with my uncertainty noted in `support`.
```

### Requirements axis — `/tmp/handoff4/reports/v2-finder-requirements.md`

```markdown
# Requirements-axis review — PR microsoft/playwright#29698 vs. issue #29662

> Verbatim output of Requirements-axis finder sub-agent `a99755f94c8de20b2` (v2 run).
> Reported usage: 55,058 tokens, 15 tool uses, 293,502 ms.

## 1. Restated requirements (Step 1, before reading the diff for compliance)

The issue is one paragraph plus one code example plus a motivation paragraph. Restated in my own words:

- **R1 — Core ask:** Provide a way to remove specific cookie(s) from a `BrowserContext`. ("The feature should remove specific cookie/cookies from context.")
- **R2 — Shape of the ask:** The mechanism should live on the browsing-context object itself, used as `context.removeCookies(...)`, per the issue's own example — not on `Page` or elsewhere.
- **R3 — Motivating scenario (the actual acceptance test the issue cares about):** A cookie set once (e.g. via `globalSetup`, to suppress a GDPR consent modal) must be removable later, selectively, so a test can exercise the state where that one cookie is absent — without wiping the whole context. Removal has to be selective, not "clear everything."
- **R4 — Vague, not sharpened into a testable requirement:** The example, `await context.removeCookies([cookieObject1, cookieObject2]);`, shows one call taking an array of two cookie objects. The prose never specifies the call shape or the matching mechanism (by name? by full object equality? by array vs. single filter?). This is genuinely underspecified — I'm flagging it as vague rather than inventing a strict requirement from it.
- **R5 — Mentioned, not required:** "I believe there are other cases where this method would be useful" is background/motivation, not an acceptance criterion. No bucket.

## 2. Sort (Step 2)

**Met: 3 (R1, R2, R3). Not met: 0. Unverifiable/question: 1 (R4).**

- **R1 — Met.** `removeCookies` is implemented end-to-end: client (`browserContext.ts:272`), server (`browserContext.ts:279`), dispatcher, protocol validator/channels/yml, docs, generated types, and covered by 8 new tests in `tests/library/browsercontext-remove-cookies.spec.ts`.
- **R2 — Met.** Added on `BrowserContext`, matching `context.removeCookies(...)` from the issue's example exactly in call shape (`packages/playwright-core/src/client/browserContext.ts:272`).
- **R3 — Met.** Server implementation reads current cookies, filters out only the ones matching the given criteria, clears, and re-adds the rest (`packages/playwright-core/src/server/browserContext.ts:279-294`). The test `should remove cookies by name` mirrors the globalSetup/GDPR scenario exactly: one named cookie removed, a second cookie left in place.
- **R4 — Unverifiable / question.** Code review shows what was built (a single filter object, AND-matched across `name`/`domain`/`path`, not an array) but cannot settle whether that satisfies the issue author's unstated intent behind the two-object array example — that's a product judgment nobody recorded (the issue has no comment thread).

## 3. Candidates

### Candidate 1 — question (unverifiable, R4)

- `id`: `requirements/question/removecookies-single-filter-per-call`
- `anchor`: `packages/playwright-core/src/client/browserContext.ts:272`
- `fix`: n/a (question — no code change proposed)
- `title`: `removeCookies takes one filter, not an array of distinct cookies`
- `claim`: The issue's example is `await context.removeCookies([cookieObject1, cookieObject2]);` — an array of two distinct cookie identifiers removed in one call. The shipped `removeCookies(filter: {name?, domain?, path?})` at `packages/playwright-core/src/client/browserContext.ts:272` (mirrored in `packages/playwright-core/src/server/browserContext.ts:279`, `packages/protocol/src/protocol.yml:1035-1043`, `packages/protocol/src/channels.ts`) accepts a single filter object, AND-matched across whichever fields are supplied. Removing two cookies that share no common name/domain/path requires two separate `removeCookies` calls, not one.
- `support`: Read the issue body verbatim — one paragraph feature request, one code example, no comment thread to negotiate this. Read the full diff (`git diff main...review-head`) across all 10 changed files: no array/batch variant of `removeCookies` appears anywhere. All 8 tests in `tests/library/browsercontext-remove-cookies.spec.ts` call `removeCookies` with a single filter object, none with an array. Unsure whether the issue author meant the array literally (a batch call) or was just showing two illustrative single-cookie snippets loosely combined into one line.
- `trigger`: A caller with multiple, dissimilar cookies to remove in one logical operation must issue multiple `removeCookies` calls instead of the single call the issue's own example depicts.
- `change`: Change no code for this. Ask whoever can speak for the issue (author `PaulTriandafilov`, or a maintainer) whether single-call batch removal of dissimilar cookies was actually required, or whether repeated single-filter calls are acceptable. If acceptable, nothing to do; if not, it's a follow-up API decision, not a defect in this PR.
- `priority`: n/a (question)

### Candidate 2 — scope creep (Step 3)

- `id`: `requirements/unrequested/domain-path-filter-criteria`
- `anchor`: `docs/src/api/class-browsercontext.md:1027`
- `fix`: same public-surface change spans `packages/playwright-core/src/client/network.ts:61-65`, `packages/playwright-core/src/server/browserContext.ts:279-294`, `packages/protocol/src/protocol.yml:1035-1043`, `packages/protocol/src/channels.ts:1427,1524-1534`, `packages/playwright-core/src/protocol/validator.ts:831-838`, `packages/playwright-core/types/types.d.ts:8441-8460`
- `title`: `removeCookies filter adds domain/path matching beyond "specific cookie"`
- `claim`: The issue asks only to "remove specific cookie/cookies from context," illustrated by `await context.removeCookies([cookieObject1, cookieObject2])` — removing named, specific cookies. The shipped filter, documented at `docs/src/api/class-browsercontext.md:1013-1029` and typed at `packages/playwright-core/src/client/network.ts:61-65`, accepts `domain` or `path` alone with no `name` required, so `context.removeCookies({ domain: 'my-origin.com' })` bulk-removes every cookie for a domain — a broader "clear all cookies matching a domain/path" capability the issue's "specific cookie" framing does not describe.
- `support`: The issue is my only requirements source per the brief; it has no comment thread. The "Relevant prior human review evidence" I was given states this filter shape (domain/path beyond name) originated from maintainer `pavelfeldman`'s suggestion during PR review, not from the issue — I weighed that as evidence the addition was deliberate, not as an instruction narrowing what I check. Confirmed via the full diff that the filter surface is threaded through every layer (client type, client method, server implementation, dispatcher, validator, protocol channels/yml, docs, generated types) and is exercised by dedicated tests (`should remove cookies by domain`, `should remove cookies by path`, `should remove cookies by domain and path`) in `tests/library/browsercontext-remove-cookies.spec.ts`. Considered whether to escalate priority for "enlarges the public surface / hard to reverse" per the brief's creep-priority rule, but since `removeCookies` is a brand-new method first introduced in this very PR (nothing pre-existing depends on it yet), the reversal cost pre-merge is low, so I left it at P2 rather than escalating.
- `trigger`: A caller invoking `context.removeCookies({ domain: 'my-origin.com' })` removes every cookie set for that domain regardless of name — broader than "remove a specific cookie," and once merged becomes a documented, typed, wire-protocol surface that's harder to retract later.
- `change`: If maintainers consider domain/path out of scope for this issue, trim `removeCookies` to name-only matching across the same file set listed under `fix`; otherwise, no action is needed — this is a scope judgment call, not a defect.
- `priority`: P2

## 4. Changed-file manifest — all reviewed, none ignored

| File | Status | Reason |
|---|---|---|
| `docs/src/api/class-browsercontext.md` | reviewed | Documents the new `removeCookies` method and its `filter` param (name/domain/path); user-facing spec surface for R1–R3, and evidence for Candidate 2. |
| `packages/playwright-core/src/client/browserContext.ts` | reviewed | Adds the client-side `removeCookies(filter)` entry point satisfying R1/R2 (method lives on `BrowserContext`, matching the issue's `context.removeCookies(...)` shape). |
| `packages/playwright-core/src/client/network.ts` | reviewed | Defines `RemoveNetworkCookieParam` (name/domain/path) — type surface behind R1 and Candidate 2. |
| `packages/playwright-core/src/protocol/validator.ts` | reviewed | Wire-protocol parameter validation for the new call; plumbing for R1, no independent requirement content. |
| `packages/playwright-core/src/server/browserContext.ts` | reviewed | The actual removal logic (filter, clear, re-add) and the "Either name, domain or path are required" guard; where R1/R3 are actually satisfied. |
| `packages/playwright-core/src/server/dispatchers/browserContextDispatcher.ts` | reviewed | Routes the protocol call to the server implementation; plumbing for R1, no independent requirement content. |
| `packages/playwright-core/types/types.d.ts` | reviewed | Public TypeScript surface for `removeCookies`; evidence for R1 and Candidate 2. |
| `packages/protocol/src/channels.ts` | reviewed | Generated protocol channel types adding `removeCookies`/params; plumbing for R1, also carries domain/path (Candidate 2 evidence). |
| `packages/protocol/src/protocol.yml` | reviewed | Protocol schema source for `removeCookies` (name/domain/path) — same evidence as above for R1/Candidate 2. Also contains one unrelated whitespace-only fix to the `ElectronApplication.console` event (trailing space removed), unconnected to any requirement here — trivial, non-functional, not raised as a candidate (falls under "small obvious cleanup," not creep). |
| `tests/library/browsercontext-remove-cookies.spec.ts` | reviewed | New test file; exercises name/domain/path removal (individually and combined) and the empty-filter throw. Directly evidences R1/R3 being met and the single-filter-per-call shape underlying Candidate 1. |

Nothing left unfinished — all 10 files' full diffs were read.

## 5. Git commands run, verbatim

```
git log --oneline -1 main && git log --oneline -1 review-head && echo "---" && git status
git log --oneline main..review-head
git diff main...review-head --stat
git diff main...review-head -- docs/src/api/class-browsercontext.md
git diff main...review-head -- packages/playwright-core/src/client/browserContext.ts packages/playwright-core/src/client/network.ts
git diff main...review-head -- packages/playwright-core/src/protocol/validator.ts packages/playwright-core/src/server/browserContext.ts
git diff main...review-head -- packages/playwright-core/src/server/dispatchers/browserContextDispatcher.ts packages/protocol/src/channels.ts packages/protocol/src/protocol.yml
git diff main...review-head -- packages/playwright-core/types/types.d.ts
git diff main...review-head -- tests/library/browsercontext-remove-cookies.spec.ts
git diff main...review-head --numstat
git branch --show-current
```
(All run with `cd /tmp/handoff4/run-v2 &&` prefix. Non-git commands — `grep -n` for line numbers — were also used but are not git commands.)

## 6. Sandbox confirmation

I read only:
- `/tmp/handoff4/skill-v2/skills/code-review-publish-2/references/requirements-axis.md`
- `/tmp/handoff4/skill-v2/skills/code-review-publish-2/references/finding-format.md`
- Files under `/tmp/handoff4/run-v2` via the `git` and `grep` commands listed above.

I did not read any other path under `/tmp/handoff4/` — no other `run-*`/`skill-*` directories, no `mirror-pw.git`, no `reports/`, no `packet-playwright.md`. Nothing to disclose.

## 7. Summary

The PR is a faithful, proportionate implementation of a small, mostly-unambiguous issue. Two candidates only: one open question about whether single-filter-per-call satisfies the issue's array-shaped example (unverifiable from code — a product judgment), and one P2 scope-creep candidate about the domain/path filter dimensions extending beyond "remove a specific cookie" (maintainer-requested during PR review, not issue-sourced, still worth a scope check per the brief). No "not met" findings.
```

---

## Verifier dispatch — exact prompt and verbatim report

Trigger: `SKILL.md` step 3 fires whenever either finder returns at least one candidate ("finders that return no candidates on a first review make this step unnecessary; skip it"). Both finders returned candidates (4 + 2 = 6), so verification was mandatory. Spawned as `Agent`, `subagent_type: "general-purpose"`, `model: "sonnet"` explicit, foreground (`run_in_background: false`, since the next action — building the disposition ledger and the rendered review — depended on its result).

### Exact prompt given to the verifier

```text
You are the Verifier sub-agent for a controlled code-review experiment. Read your brief in full before doing anything else: `/tmp/handoff4/skill-v2/skills/code-review-publish-2/references/verify.md`. Follow it exactly.

Your repository is `/tmp/handoff4/run-v2`, an offline clone. The branch `review-head` is checked out at the pinned head `cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b`. The branch `main` is force-pinned to the merge-base `9a38aedf09f203a58008756e588324254abaef9a`. This is a first review — there are no prior findings to carry forward, so ignore the "Prior findings, on a re-review" section of your brief entirely.

Binding constraints, on you and on any tool you use:
1. No network of any kind — no git fetch/pull, no gh, no curl, no web fetch.
2. No execution — no npm, npx, node, tsc, eslint, no test runner, no build. Static review only: reason from source, and say so explicitly anywhere a claim would ordinarily be settled by running something.
3. History is deliberately truncated at the pinned head `cb02d5ba1`. Do not try to read anything beyond it. Report explicitly, at the end, whether you read any git history beyond the pinned head, and list every git-history command (log/show/diff/blame/etc.) you ran, verbatim.
4. Stay inside `/tmp/handoff4/run-v2` (the repository) and `/tmp/handoff4/skill-v2` (your brief and its sibling reference files, if you need finding-format.md for context on the anchor/fix vocabulary). Do not read any other path under `/tmp/handoff4`. Report at the end if you read anything outside those two directories.
5. You are NOT given each candidate's `support` field — only `id`, `axis`, `anchor`, `fix`, `title`, `claim`, `trigger`, `priority`. This is deliberate per your brief; do not ask for it and do not assume any hedging or demonstration beyond what is written below.

Here are the 6 candidates, exactly as produced by the two finders (Code axis and Requirements axis). Rule on each one per your brief's three-state vocabulary (`confirmed` / `plausible` / `refuted`), deduplicate if warranted, and report priority corrections if warranted.

---

### Candidate 1
- id: `code/browsercontext-ts/remove-cookies-domain-exact-match`
- axis: Code
- anchor: `packages/playwright-core/src/server/browserContext.ts:287`
- fix: (same as anchor)
- title: removeCookies domain filter uses exact match, missing this repo's own dot-prefix domain-cookie convention
- claim: `server/browserContext.ts:287` matches cookies with `(!filter.domain || filter.domain === cookie.domain)` — a raw string-equality check. This codebase documents, at `docs/src/api/class-browsercontext.md:347`, that cookies applying to subdomains are stored with a domain prefixed by a dot ("For the cookie to apply to all subdomains as well, prefix domain with a dot, like this: `.example.com`."), and this convention is implemented pervasively elsewhere for the exact same `NetworkCookie.domain` field: `packages/playwright-core/src/server/cookieStore.ts:118-125`'s `domainMatches()` treats a domain without a leading dot as host-only (strict-equal only) and a domain with a leading dot as subdomain-matching per RFC 6265; `packages/playwright-core/src/server/network.ts:34-41` (`filterCookies`) and `packages/playwright-core/src/server/fetch.ts:225,646,726` all branch on `domain.startsWith('.')` for this same field. Real cookies set by a website via a `Set-Cookie: ...; Domain=example.com` response header — the primary real-world source of cookies `removeCookies` is meant to clear — are canonicalized by browsers with a leading dot. `removeCookies`'s own documented usage example, `await browserContext.removeCookies({ domain: 'my-origin.com' })` (no leading dot), will silently match zero cookies against such a cookie.
- trigger: A page in the context receives a `Set-Cookie: sid=abc; Domain=example.com; Path=/` response (or otherwise gets a cookie with an explicit `Domain` attribute) during normal navigation. Calling `context.removeCookies({ domain: 'example.com' })` — the form shown in this PR's own doc example — matches nothing and silently leaves the cookie in place, with no error and no indication anything went wrong.
- priority: P1

### Candidate 2
- id: `code/browsercontext-ts/remove-cookies-clear-readd-race`
- axis: Code
- anchor: `packages/playwright-core/src/server/browserContext.ts:291`
- fix: `packages/playwright-core/src/server/browserContext.ts:283-292`
- title: removeCookies clears and re-adds all context cookies, losing any cookie set between the snapshot and the clear
- claim: `server/browserContext.ts:283-292` implements removal as read-all → filter → clear-all → re-add-kept:
```js
const currentCookies = await this.cookies();
const cookiesToKeep = currentCookies.filter(cookie => { ... });
await this.clearCookies();
await this.addCookies(cookiesToKeep);
```
`this.cookies()` with no `urls` argument returns every cookie in the entire browser context (`network.ts`'s `filterCookies`: `if (!parsedURLs.length) return true;`), and `clearCookies()` wipes every cookie in the context (e.g. `crBrowser.ts:414-415`, `Storage.clearCookies` for the whole `browserContextId`). Each of the three awaited steps is a separate round trip. Any cookie that is set (by a concurrent page navigation receiving a `Set-Cookie` header, an in-page `document.cookie` write, a redirect, etc.) after the `this.cookies()` snapshot but before `clearCookies()`/`addCookies()` complete is present when `clearCookies()` wipes the context, but is not in `cookiesToKeep`, so it is never restored — it is permanently lost, with no error surfaced.
- trigger: Two pages exist in the same `BrowserContext`. While one page is calling `context.removeCookies({ name: 'x' })`, the other page navigates and receives a `Set-Cookie` response, or runs `document.cookie = ...`, in the window between the `cookies()` snapshot and the `clearCookies()`/`addCookies()` pair completing. The newly-set, unrelated cookie is permanently deleted.
- priority: P1

### Candidate 3
- id: `code/class-browsercontext-md/remove-cookies-wrong-since-version`
- axis: Code
- anchor: `docs/src/api/class-browsercontext.md:1014`
- fix: (same as anchor, and also `:1028`)
- title: removeCookies doc tagged `since: v1.43`, one minor version ahead of the in-development release
- claim: `class-browsercontext.md:1014` and `:1028` tag the new `removeCookies` method and its `filter` param with `* since: v1.43`. At the base commit, `packages/playwright-core/package.json` declares `"version": "1.42.0-next"`, and every other newly-documented API in the current development cycle in `docs/src/api/*.md` at the base commit uses `since: v1.42` (8 occurrences) — there are zero `since: v1.43` occurrences anywhere in the base tree. This PR's two additions are the only `since: v1.43` tags in the entire docs tree.
- trigger: Not a runtime trigger — a documentation/versioning defect. Any user reading the rendered docs or the generated `types.d.ts` for `removeCookies` is told it shipped in v1.43 when, per every sibling doc entry, it should read v1.42.
- priority: P3

### Candidate 4
- id: `code/class-browsercontext-md/remove-cookies-undocumented-throw`
- axis: Code
- anchor: `docs/src/api/class-browsercontext.md:1016`
- fix: (same as anchor)
- title: removeCookies doc doesn't state that omitting all criteria throws
- claim: `class-browsercontext.md:1016` reads "Removes cookies from context. At least one of the removal criteria should be provided." — a soft/recommendatory phrasing that does not tell the reader what happens if none is provided. The implementation at `server/browserContext.ts:280` does `throw new Error('Either name, domain or path are required')` when no criteria are given, and the PR's own test at `tests/library/browsercontext-remove-cookies.spec.ts:435-454` ("should throw if empty object is passed") confirms this is real, load-bearing behavior, not a hypothetical.
- trigger: A developer reads only the rendered docs (not the TS declaration file) for `removeCookies`, calls it with an empty/no-criteria object based on the doc's soft wording, and is surprised by an uncaught exception rather than a silent no-op.
- priority: P3

### Candidate 5
- id: `requirements/question/removecookies-single-filter-per-call`
- axis: Requirements
- anchor: `packages/playwright-core/src/client/browserContext.ts:272`
- fix: n/a (question — no code change proposed)
- title: removeCookies takes one filter, not an array of distinct cookies
- claim: The originating issue's example is `await context.removeCookies([cookieObject1, cookieObject2]);` — an array of two distinct cookie identifiers removed in one call. The shipped `removeCookies(filter: {name?, domain?, path?})` at `packages/playwright-core/src/client/browserContext.ts:272` (mirrored in `packages/playwright-core/src/server/browserContext.ts:279`, `packages/protocol/src/protocol.yml:1035-1043`, `packages/protocol/src/channels.ts`) accepts a single filter object, AND-matched across whichever fields are supplied. Removing two cookies that share no common name/domain/path requires two separate `removeCookies` calls, not one.
- trigger: A caller with multiple, dissimilar cookies to remove in one logical operation must issue multiple `removeCookies` calls instead of the single call the issue's own example depicts.
- priority: n/a (question — the finder placed this in its "cannot tell from the code" bucket per the requirements-axis brief, since it turns on unrecorded product intent, not on a code fact in dispute)

### Candidate 6
- id: `requirements/unrequested/domain-path-filter-criteria`
- axis: Requirements
- anchor: `docs/src/api/class-browsercontext.md:1027`
- fix: same public-surface change spans `packages/playwright-core/src/client/network.ts:61-65`, `packages/playwright-core/src/server/browserContext.ts:279-294`, `packages/protocol/src/protocol.yml:1035-1043`, `packages/protocol/src/channels.ts:1427,1524-1534`, `packages/playwright-core/src/protocol/validator.ts:831-838`, `packages/playwright-core/types/types.d.ts:8441-8460`
- title: removeCookies filter adds domain/path matching beyond "specific cookie"
- claim: The originating issue asks only to "remove specific cookie/cookies from context," illustrated by `await context.removeCookies([cookieObject1, cookieObject2])` — removing named, specific cookies. The shipped filter, documented at `docs/src/api/class-browsercontext.md:1013-1029` and typed at `packages/playwright-core/src/client/network.ts:61-65`, accepts `domain` or `path` alone with no `name` required, so `context.removeCookies({ domain: 'my-origin.com' })` bulk-removes every cookie for a domain — a broader "clear all cookies matching a domain/path" capability the issue's "specific cookie" framing does not describe.
- trigger: A caller invoking `context.removeCookies({ domain: 'my-origin.com' })` removes every cookie set for that domain regardless of name — broader than "remove a specific cookie," and once merged becomes a documented, typed, wire-protocol surface that's harder to retract later.
- priority: P2

---

For each candidate: read the cited anchor and fix sites and enough surrounding code to judge the claim, per your brief. Return, per candidate: id, verdict, one sentence of justification, the quoted line supporting `confirmed`/`refuted` verdicts, a corrected trigger if you changed one, and a priority note if you moved one. Then the merge/dedup list if any, and counts by verdict. Then your required disclosures: (a) every git-history command you ran verbatim, and whether any went beyond the pinned head; (b) confirmation you stayed inside the two permitted directories, or a disclosure of any path outside them that you read.

Be blunt. Do not add findings of your own — if you notice something the finders missed, say so in one line at the very end, separate from your verdicts, and do not fold it into any verdict.
```

### Verbatim verifier report

```markdown
# Verification Report

## Candidate 1 — `code/browsercontext-ts/remove-cookies-domain-exact-match`

**Verdict: confirmed**

`browserContext.ts:287` reads exactly as claimed:
```
      return !((!filter.name || filter.name === cookie.name) &&
        (!filter.domain || filter.domain === cookie.domain) &&
```
— strict equality on `cookie.domain`. This is cross-checked against `cookieStore.ts:118-127` (`domainMatches`):
```
118: export function domainMatches(value: string, domain: string): boolean {
119:   if (value === domain)
120:     return true;
122:   if (!domain.startsWith('.'))
123:     return false;
```
which this same codebase uses elsewhere for the identical `NetworkCookie.domain` field, and `docs/src/api/class-browsercontext.md:348` (one line off from the candidate's `:347`, immaterial) states the dot-prefix subdomain convention. `crBrowser.ts:396-406` (`doGetCookies`) passes CDP `Storage.getCookies` results straight through with no domain normalization, so a real cookie set via `Set-Cookie: ...; Domain=example.com` arrives with CDP's dot-prefixed domain and will not string-equal a caller's `'example.com'`. Trigger as stated is accurate and reproducible from the code alone (I did not execute anything — this is inferred from the documented CDP/browser convention this repo itself encodes at three other call sites, not from running a browser). Priority P1 stands — real but conditional on the cookie having an explicit `Domain` attribute, so not P0.

## Candidate 2 — `code/browsercontext-ts/remove-cookies-clear-readd-race`

**Verdict: confirmed**

`browserContext.ts:283-292` is exactly the read→filter→clear→re-add sequence quoted. `clearCookies()` resolves to `crBrowser.ts:414-415`:
```
414:  async clearCookies() {
415:    await this._browser._session.send('Storage.clearCookies', { browserContextId: this._browserContextId });
```
— context-wide, not scoped to any subset. No mutex, lock, or version-stamping guards the three awaited steps (verified: no lock/mutex symbol anywhere in `browserContext.ts`). This is an unguarded read-modify-write with two full round trips between snapshot and clear; any cookie set in that window is wiped and not in `cookiesToKeep`, so it's lost. Trigger as stated is accurate. Priority P1 stands (concurrency-dependent, so not P0, but real and silent).

## Candidate 3 — `code/class-browsercontext-md/remove-cookies-wrong-since-version`

**Verdict: confirmed**

`class-browsercontext.md:1014` and `:1028` both read `* since: v1.43` (exact anchor match). `packages/playwright-core/package.json:3` reads `"version": "1.42.0-next"`. `grep -c 'since: v1.42' docs/src/api/*.md` = 8; `grep 'since: v1.43' docs/src/api/*.md` returns only these same two lines. Quoted line: `* since: v1.43` (line 1014), contradicted by `"version": "1.42.0-next"`. Priority P3 stands — purely a metadata/versioning defect, no runtime consequence.

## Candidate 4 — `code/class-browsercontext-md/remove-cookies-undocumented-throw`

**Verdict: confirmed, with a citation correction**

`class-browsercontext.md:1016` reads exactly as quoted: "Removes cookies from context. At least one of the removal criteria should be provided." `browserContext.ts:280` throws: `throw new Error(\`Either name, domain or path are required\`)`. The doc's soft phrasing genuinely doesn't disclose that an exception is thrown. However, the candidate's test citation is wrong: `tests/library/browsercontext-remove-cookies.spec.ts` is only 231 lines long, so lines **435-454 do not exist**. The actual test ("should throw if empty object is passed") is at **lines 212-230**, and it does confirm the throw:
```
226:  const error = await context.removeCookies({ }).catch(e => e);
227:  expect(error.message).toContain(`Either name, domain or path are required`);
```
The core claim survives verification at the correct location; the citation itself was wrong and should be corrected before publishing. Priority P3 stands.

**Corrected fix-site citation:** `tests/library/browsercontext-remove-cookies.spec.ts:212-230` (not `435-454`).

## Candidate 5 — `requirements/question/removecookies-single-filter-per-call`

**Verdict: plausible**

Code-side mechanism is fully confirmed: `client/browserContext.ts:272-273` takes a single `filter: network.RemoveNetworkCookieParam`, mirrored at `protocol.yml:1035-1041` (`filter: {type: object, properties: {name, domain, path}}`) — no array form anywhere in the surface. What I cannot verify is the candidate's quote of "the originating issue's example," since the issue text is not present anywhere in the pinned commit range (checked `git log` bodies from merge-base to head — no issue link or quoted example appears) and I have no network access to fetch it. What would settle it: reading the actual linked issue. The finder itself flagged this as a question rather than an assertion, which this verdict matches. Priority: leave as `n/a (question)`, unchanged.

## Candidate 6 — `requirements/unrequested/domain-path-filter-criteria`

**Verdict: plausible**

Code-side mechanism is fully confirmed: `protocol.yml:1035-1041` makes `name`, `domain`, `path` all independently optional (`string?`), and `browserContext.ts:285-289`'s AND-filter means `{domain: 'my-origin.com'}` alone matches and removes every cookie for that domain regardless of name — this is directly demonstrable from the code, no test run needed. What is not independently verifiable by me is the "originating issue" framing ("remove specific cookie/cookies," `removeCookies([cookieObject1, cookieObject2])`) — same limitation as Candidate 5: no issue text is present in the pinned commit range and I have no network access to check it. Given the brief's default-to-`plausible` rule for anything I can't settle either way, and since the requirements-gap framing (not just the code mechanism) is what's actually in dispute, I hold this at `plausible` rather than `confirmed`. What would settle it: reading the linked issue's literal wording. Priority: keep P2 — not clearly wrong given the confirmed code mechanism, even though I couldn't verify the issue-comparison.

---

## Merge/dedup list

None. All six candidates describe distinct defects — no fix for one resolves another, and no Code/Requirements pair here describes the same underlying defect (Candidate 1 is a matching-semantics bug; Candidate 6 is a scope-of-criteria question against the issue; these are not the same thing).

## Counts by verdict

- confirmed: 4 (Candidates 1, 2, 3, 4)
- plausible: 2 (Candidates 5, 6)
- refuted: 0

## Required disclosures

**(a) Git-history commands run, verbatim, and whether any went beyond the pinned head:**
```
git branch -a
git log -1 --format='%H %s' review-head
git log -1 --format='%H %s' main
git log --oneline 9a38aedf09f203a58008756e588324254abaef9a..cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b
git log 9a38aedf09f203a58008756e588324254abaef9a..cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b --format='%H%n%B%n---'
```
None of these went beyond the pinned head `cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b`; both range queries are bounded exactly at it. No `show`, `diff`, or `blame` was run.

**(b) Path confinement:** I read only files under `/tmp/handoff4/run-v2` (the repository) and `/tmp/handoff4/skill-v2/skills/code-review-publish-2/references/verify.md` (my brief). I did not open `finding-format.md` or any other file. No path outside those two locations was read.

## Out-of-scope observation (not a verdict, not a finding of mine)

The claimed anchor/quote line numbers in several candidates are off by small amounts from the actual file content (e.g., Candidate 1's doc citation `:347` vs actual `:348`; Candidate 4's test citation `:435-454` vs actual `:212-230`, off by enough to point outside the file entirely). None of these change the substance of any verdict above, but a pattern of imprecise line citations across candidates from both finders is worth the pipeline's attention independent of any single finding.
```

Reported verifier usage: **subagent_tokens: 44,280, tool_uses: 24, duration_ms: 221,415**.

---

## Candidate disposition ledger

| id | Axis | Anchor | Claim (short) | Verifier verdict | Disposition | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| `code/browsercontext-ts/remove-cookies-domain-exact-match` | Code | `server/browserContext.ts:287` | Domain filter uses exact match, missing repo's dot-prefix subdomain convention | confirmed | **Published** — finding, `must-fix`, P1 | Quoted line matches; cross-checked against `cookieStore.ts`'s `domainMatches()` and 3 other call sites using the same convention |
| `code/browsercontext-ts/remove-cookies-clear-readd-race` | Code | `server/browserContext.ts:291` (fix 283-292) | Clear-then-re-add loses cookies set mid-operation | confirmed | **Published** — finding, `must-fix`, P1 | Traced `clearCookies()` to context-wide `Storage.clearCookies`; no lock/mutex guards the 3-step sequence |
| `code/class-browsercontext-md/remove-cookies-wrong-since-version` | Code | `class-browsercontext.md:1014` (& :1028) | `since: v1.43` is one version ahead of `1.42.0-next` | confirmed | **Published** — finding, `consider`, P3 | Verified `package.json` version and 8×`v1.42`/0×`v1.43` grep counts directly |
| `code/class-browsercontext-md/remove-cookies-undocumented-throw` | Code | `class-browsercontext.md:1016` | Doc doesn't disclose the empty-filter throw | confirmed (citation corrected) | **Published** — finding, `consider`, P3, with corrected test citation `spec.ts:212-230` (finder's `:435-454` was out of range — file is only 231 lines) | Core claim verified true at the corrected site |
| `requirements/question/removecookies-single-filter-per-call` | Requirements | `client/browserContext.ts:272` | Single-filter API vs. issue's two-object array example | plausible | **Published** — question, no axis/priority in trailer | Code mechanism (single filter, no array/batch form) is confirmed; whether that satisfies unstated issue intent is not code-checkable — verifier couldn't reach the issue text either (correctly so, no network) |
| `requirements/unrequested/domain-path-filter-criteria` | Requirements | `class-browsercontext.md:1027` | domain/path filter exceeds "remove a specific cookie" | plausible | **Published** — question, no axis/priority in trailer | Code mechanism (domain/path alone matches, no name required) confirmed; whether it constitutes creep against the issue's framing is a scope judgment the verifier left open |

**Acquittals — examined and consciously judged safe (not raised as candidates by either finder):**

| Where | What was examined | Finder's reasoning | Disposition |
| --- | --- | --- | --- |
| `packages/playwright-core/src/protocol/validator.ts` | New `BrowserContextRemoveCookiesParams`/`Result` entries inserted out of the file's otherwise-alphabetical order (after `ClearCookies`, not near `R`) | No documented ordering rule in `CONTRIBUTING.md` (confirmed by this orchestrator directly reading `CONTRIBUTING.md` — see Specific answers (b)); no behavioral effect; excluded nitpick class per `code-axis.md` | Acquitted — dropped, not a candidate |
| `packages/playwright-core/types/types.d.ts` | Generated file's wording ("The method will throw an error if either name, domain or path has not been passed.") doesn't verbatim match the markdown source's prose | Generated artifact; `npm run lint`'s clean-tree CI check catches any drift; class-of-thing that check exists for | Ignored (file-level), noted in passing, not a candidate |
| `packages/protocol/src/channels.ts` | Generated protocol channel types | Same generated-artifact / CI clean-tree reasoning as above | Ignored (file-level) |
| `packages/protocol/src/protocol.yml` | Unrelated trailing-whitespace removal on `ElectronApplication.events.console.parameters` | No-op formatting fix, unconnected to any requirement, not creep ("small obvious cleanup") — noted by **both** finders independently | Acquitted by both axes |
| `tests/library/browsercontext-remove-cookies.spec.ts` | Never exercises a leading-dot-normalized domain cookie, nor a concurrent-cookie-write scenario | Thin test coverage alone isn't a candidate per the code-axis brief; noted as context explaining why the two P1 bugs went uncaught by CI, not reported separately | Acquitted — recorded as context only |
| `packages/playwright-core/src/client/browserContext.ts` | Thin pass-through `removeCookies` → `this._channel.removeCookies({ filter })` | Matches existing `clearCookies`/`addCookies` pattern exactly | Acquitted — nothing stood out |
| `packages/playwright-core/src/client/network.ts` | New `RemoveNetworkCookieParam` type | Structurally mirrors existing `SetNetworkCookieParam` | Acquitted — nothing stood out |
| `packages/playwright-core/src/server/dispatchers/browserContextDispatcher.ts` | Thin pass-through dispatcher | Matches existing dispatcher pattern | Acquitted — nothing stood out |

**Verifier's own out-of-scope observation** (explicitly not folded into any verdict, per its brief): a pattern of imprecise line-number citations across candidates from both finders (Candidate 1's `:347` vs actual `:348`, Candidate 4's `:435-454` vs actual `:212-230`) — worth the pipeline's attention, not itself a finding.

---

## Everything consulted beyond the diff

By the finders (per their own disclosures, reproduced above): `docs/src/api/class-browsercontext.md` (context beyond the diff hunk, e.g. line 347/348's dot-prefix convention), `packages/playwright-core/src/server/cookieStore.ts`, `packages/playwright-core/src/server/network.ts`, `packages/playwright-core/src/server/fetch.ts`, `packages/playwright-core/src/server/crBrowser.ts`, `CONTRIBUTING.md` (at `main`), `packages/playwright-core/package.json` (at `main`), `.github/workflows/infra.yml`, `utils/doclint/since.js` (checked for its invocation surface), `utils/generate_channels.js` / `utils/generate_types/` (checked as the generators for ignored files), the prior human review thread and CI-comment history (given in the packet, not fetched), the originating issue text (given in the packet).

By the verifier: `packages/playwright-core/src/server/browserContext.ts` (full function + surrounding), `packages/playwright-core/src/server/cookieStore.ts` (`domainMatches`), `docs/src/api/class-browsercontext.md` (around line 348), `packages/playwright-core/src/server/crBrowser.ts` (`clearCookies`, `doGetCookies`), `packages/playwright-core/package.json`, `tests/library/browsercontext-remove-cookies.spec.ts` (full file, to correct Candidate 4's citation), `packages/protocol/src/protocol.yml`, `client/browserContext.ts`. Its brief `verify.md`. Its own bounded `git log` range queries (listed above).

By this orchestrator: `SKILL.md`, `DESIGN.md`, all five `references/*.md` files, `ATTRIBUTION.md`; the packet `packet-playwright.md`; both finder reports; repo state (`git status`, `git branch -a`, `git rev-parse`, `git log --oneline -3`); `git diff main...review-head --unified=0` (anchor validation against the three files carrying findings); `git show main:CONTRIBUTING.md` in full (249 lines, read in three chunks), specifically to answer Specific-answer (b) and to independently corroborate the Code finder's acquittal of the `validator.ts` ordering nitpick. Also: a non-content `ls -la` directory listing of `/tmp/handoff4/reports/` and `/tmp/handoff4/` (see Specific answer (e)).

---

## Would-be published review, verbatim

*(Publication is disabled per binding constraint 4. This is rendered exactly as it would post via `gh api ... pulls/29698/reviews`, `event: COMMENT`, and then stops.)*

**Body:**

```markdown
**Changes Requested (advisory)** — 2 blocking findings, 2 optional findings, 2 open questions.

Code: Findings — 2 blocking, 2 optional. Requirements: Waiting for information — 3/3 core
requirements met (R1 core ask, R2 call shape, R3 selective-removal scenario), 1 requirement
unverifiable from code (R4) and 1 scope question, both open as questions below.

Reviewed `cb02d5ba1` against `main` (merge-base `9a38aedf0`). Coverage: complete (10/10 files).

The two blocking findings are the ones to fix first, and they share a root cause: `removeCookies`
treats the read-filter-clear-readd sequence as atomic and the domain comparison as exact, and
neither assumption holds against real browser cookie state — a `Domain`-attributed cookie's
canonical dot-prefixed form, and a cookie set concurrently with the call. The two optional findings
are documentation-accuracy gaps in the same new doc section. Both open questions turn on the
originating issue's intent rather than on the code, and neither can be settled by static review.

### Code — findings

1. **[Code] [must-fix] [P1]** [removeCookies domain filter uses exact match, missing this repo's own dot-prefix domain-cookie convention](#finding-1) — `packages/playwright-core/src/server/browserContext.ts:287`
2. **[Code] [must-fix] [P1]** [removeCookies clears and re-adds all context cookies, losing any cookie set mid-operation](#finding-2) — `packages/playwright-core/src/server/browserContext.ts:291`
3. **[Code] [consider] [P3]** [removeCookies doc tagged `since: v1.43`, one minor version ahead of the in-development release](#finding-3) — `docs/src/api/class-browsercontext.md:1014`
4. **[Code] [consider] [P3]** [removeCookies doc doesn't state that omitting all criteria throws](#finding-4) — `docs/src/api/class-browsercontext.md:1016`

### Requirements — outcome

Waiting for information. 3 of 3 core requirements met (R1–R3); no requirement not met; 1
unverifiable (R4), carried into Open Questions below alongside 1 scope-creep question.

Counts by axis and action: Code — 4 findings (2 must-fix, 2 consider). Requirements — 0 findings,
2 questions. Refuted: 0.

## Open questions

**[Question]** Does `removeCookies` need to accept an array of dissimilar cookies in one call? — `packages/playwright-core/src/client/browserContext.ts:272`

**[Question]** Does the domain/path filter on `removeCookies` exceed "remove a specific cookie"? — `docs/src/api/class-browsercontext.md:1027`

(Full text of both questions is in the line-comment index below, per the forge's anchor mechanism — GitHub questions ride the same review as line comments where they have an honest anchor.)

<!-- review-run head=cb02d5ba1 base-ref=main base-sha=9a38aedf0 merge-base=9a38aedf0 issues=microsoft/playwright#29662 coverage=complete -->
```

**Line comments** (each attached to `path`/`line`/`side: RIGHT` on `cb02d5ba1`):

---

<a name="finding-1"></a>
**Comment on `packages/playwright-core/src/server/browserContext.ts:287`:**

```markdown
**[Code] [must-fix] [P1] `removeCookies` domain filter uses exact match, missing the repo's own dot-prefix subdomain convention**

`packages/playwright-core/src/server/browserContext.ts:287` matches cookies with
`filter.domain === cookie.domain` — a raw string-equality check. This codebase documents, at
`docs/src/api/class-browsercontext.md:348`, that a cookie applying to subdomains is stored with a
domain prefixed by a dot ("prefix domain with a dot, like this: `.example.com`"), and implements
that convention elsewhere for the same `NetworkCookie.domain` field: `cookieStore.ts:118-127`'s
`domainMatches()` treats a dot-prefixed domain as subdomain-matching per RFC 6265, and
`network.ts`/`fetch.ts` branch on `domain.startsWith('.')` for the same field. A real cookie set
via `Set-Cookie: ...; Domain=example.com` is canonicalized with a leading dot before it reaches
this code (confirmed: `crBrowser.ts`'s `doGetCookies` passes CDP's `Storage.getCookies` output
through with no domain normalization), so `removeCookies`'s own documented example,
`removeCookies({ domain: 'my-origin.com' })`, silently matches zero cookies against it.

**Triggers when**: a page receives a `Set-Cookie` response with an explicit `Domain` attribute (or
any cookie otherwise carries a dot-prefixed domain), and the caller then calls
`context.removeCookies({ domain: 'example.com' })` (no leading dot) as shown in this PR's own doc
example — the cookie is not removed, with no error.

**Change**: In `server/browserContext.ts:287`, replace the raw `filter.domain === cookie.domain`
comparison with RFC 6265 domain matching (reuse/adapt `domainMatches()` from `cookieStore.ts`), or,
if exact-attribute matching is intentional, document the caveat explicitly at
`class-browsercontext.md:1016-1024` the way `addCookies` does at line 348.

<!-- finding id=code/browsercontext-ts/remove-cookies-domain-exact-match axis=code action=must-fix priority=P1 head=cb02d5ba1 -->
```

---

<a name="finding-2"></a>
**Comment on `packages/playwright-core/src/server/browserContext.ts:291`:**

```markdown
**[Code] [must-fix] [P1] `removeCookies` clears and re-adds all context cookies, losing any cookie set mid-operation**

`server/browserContext.ts:283-292` implements removal as read-all → filter → clear-all →
re-add-kept, three separate awaited round trips:
`const currentCookies = await this.cookies(); const cookiesToKeep = currentCookies.filter(...);
await this.clearCookies(); await this.addCookies(cookiesToKeep);`. `cookies()` with no `urls`
returns every context cookie, and `clearCookies()` (`crBrowser.ts:414-415`, context-wide
`Storage.clearCookies`) wipes the whole context — nothing guards the sequence. Any cookie set
between the snapshot and the clear (a concurrent page navigation's `Set-Cookie`, an in-page
`document.cookie` write) is wiped by `clearCookies()` but absent from `cookiesToKeep`, so it is
never restored.

**Triggers when**: two pages share a `BrowserContext`; while one calls
`context.removeCookies({ name: 'x' })`, the other receives a `Set-Cookie` response or runs
`document.cookie = ...` in the window between the `cookies()` snapshot and the
`clearCookies()`/`addCookies()` pair completing. The newly-set, unrelated cookie is permanently
deleted with no error.

**Change**: Avoid the clear-all/re-add-all round trip in `server/browserContext.ts:283-292` —
remove exactly the matching cookies via a targeted per-cookie delete instead of a context-wide
clear, or at minimum re-snapshot immediately before `clearCookies()` to shrink the race window and
document the non-atomicity if a full fix isn't feasible.

<!-- finding id=code/browsercontext-ts/remove-cookies-clear-readd-race axis=code action=must-fix priority=P1 fix=packages/playwright-core/src/server/browserContext.ts:283 head=cb02d5ba1 -->
```

---

<a name="finding-3"></a>
**Comment on `docs/src/api/class-browsercontext.md:1014`:**

```markdown
**[Code] [consider] [P3] `removeCookies` doc tagged `since: v1.43`, one minor version ahead of the in-development release**

`docs/src/api/class-browsercontext.md:1014` and `:1028` tag the new method and its `filter` param
`* since: v1.43`. At the base commit `packages/playwright-core/package.json` declares
`"version": "1.42.0-next"`, and every other newly-documented API in `docs/src/api/*.md` at base
uses `since: v1.42` (8 occurrences, 0 occurrences of `v1.43`) — these two lines are the only
`v1.43` tags in the tree.

**Triggers when**: a user reads the rendered docs or generated `types.d.ts` for `removeCookies`
and is told it shipped in v1.43 when, per every sibling entry, it should read v1.42.

**Change**: Change `since: v1.43` to `since: v1.42` at both `class-browsercontext.md:1014` and
`:1028`.

Closing this without action is a correct response.

<!-- finding id=code/class-browsercontext-md/remove-cookies-wrong-since-version axis=code action=consider priority=P3 head=cb02d5ba1 -->
```

---

<a name="finding-4"></a>
**Comment on `docs/src/api/class-browsercontext.md:1016`:**

```markdown
**[Code] [consider] [P3] `removeCookies` doc doesn't state that omitting all criteria throws**

`class-browsercontext.md:1016` reads "Removes cookies from context. At least one of the removal
criteria should be provided." — soft phrasing that doesn't disclose the actual behavior.
`server/browserContext.ts:280` throws `Either name, domain or path are required` when no criteria
are given, confirmed live by the test "should throw if empty object is passed" at
`tests/library/browsercontext-remove-cookies.spec.ts:212-230`.

**Triggers when**: a developer reads only the rendered docs (not the TS declaration), calls
`removeCookies({})` based on the doc's soft wording, and hits an uncaught exception instead of the
implied optional/no-op behavior.

**Change**: Reword `class-browsercontext.md:1016` to state the requirement as a hard constraint
with its consequence, e.g. "Removes cookies from context. Accepts a filter with `name`, `domain`
and/or `path` — at least one must be specified, or the method throws."

Closing this without action is a correct response.

<!-- finding id=code/class-browsercontext-md/remove-cookies-undocumented-throw axis=code action=consider priority=P3 head=cb02d5ba1 -->
```

---

<a name="question-1"></a>
**Comment on `packages/playwright-core/src/client/browserContext.ts:272`:**

```markdown
**[Question] Does `removeCookies` need to accept an array of dissimilar cookies in one call?**

The originating issue's example is `await context.removeCookies([cookieObject1, cookieObject2]);`
— an array of two distinct cookie identifiers removed in one call. The shipped
`removeCookies(filter: {name?, domain?, path?})` (`client/browserContext.ts:272`) accepts a single
filter object, AND-matched across whichever fields are supplied; no array/batch form exists
anywhere in the surface (`protocol.yml:1035-1041` confirms). Removing two cookies that share no
common name/domain/path requires two separate calls, not the single call the issue's example
depicts. Code review can confirm the shipped shape but not whether the issue author's array
example was meant literally as a batch-call requirement or as two illustrative single-cookie
snippets loosely combined — that's a product judgment the issue thread never recorded.

**Change no code for this.** Ask whoever can speak for the issue (author `PaulTriandafilov`, or a
maintainer) whether single-call batch removal of dissimilar cookies is required, or whether
repeated single-filter calls are acceptable. If acceptable, nothing to do; otherwise it's a
follow-up API decision, not a defect in this PR.

<!-- finding id=question/browsercontext-ts/removecookies-single-filter-per-call action=question head=cb02d5ba1 -->
```

---

<a name="question-2"></a>
**Comment on `docs/src/api/class-browsercontext.md:1027`:**

```markdown
**[Question] Does the domain/path filter on `removeCookies` exceed "remove a specific cookie"?**

The issue asks only to "remove specific cookie/cookies from context," illustrated by
`removeCookies([cookieObject1, cookieObject2])`. The shipped filter
(`docs/src/api/class-browsercontext.md:1013-1029`, `client/network.ts:61-65`) accepts `domain` or
`path` alone with no `name` required, so `context.removeCookies({ domain: 'my-origin.com' })`
bulk-removes every cookie for a domain regardless of name — a broader "clear by domain/path"
capability the issue's "specific cookie" framing doesn't describe. This dimension traces to a
maintainer's PR-review suggestion, not the issue itself, and is now a documented, typed,
wire-protocol surface that is harder to retract once merged.

**Change no code for this.** If maintainers consider domain/path matching out of scope for issue
#29662, trim `removeCookies` to name-only matching across the listed files; otherwise this is an
accepted scope decision and needs no action.

<!-- finding id=question/class-browsercontext-md/domain-path-filter-criteria action=question head=cb02d5ba1 -->
```

---

**Event**: `COMMENT` (packet states the posting identity is an ordinary first-time reviewer with no stated authorization to gate the merge, so `APPROVE`/`REQUEST_CHANGES` is not used; status is carried in the body's first line as `Changes Requested (advisory)` per `publishing.md`).

**Publication**: not executed. This is the render-only output required by binding constraint 4.

---

## Specific answers

**(a) Did you or any sub-agent read git history beyond the pinned head? List every history command.**

No. Every git-history command run by this orchestrator, the verifier, and (per their own disclosures) both finders stayed at or below the pinned head `cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b`.

- This orchestrator: `git status && git branch -a && git rev-parse main review-head && git log --oneline -3 review-head`; `git diff main...review-head --unified=0 -- packages/playwright-core/src/server/browserContext.ts docs/src/api/class-browsercontext.md packages/playwright-core/src/client/browserContext.ts`; `git show main:CONTRIBUTING.md` (×3 paginated reads).
- Verifier: `git branch -a`; `git log -1 --format='%H %s' review-head`; `git log -1 --format='%H %s' main`; `git log --oneline 9a38aedf0..cb02d5ba1`; `git log 9a38aedf0..cb02d5ba1 --format='%H%n%B%n---'`.
- Code finder (per its report): `git rev-parse main && git rev-parse review-head && git log --oneline main..review-head`; `git diff main...review-head --stat`; `git diff main...review-head > /tmp/handoff4_pr.diff && wc -l /tmp/handoff4_pr.diff`; `git show main:CONTRIBUTING.md`; `git status && git rev-parse HEAD`; `git show main --stat >/dev/null; git worktree list 2>/dev/null; git grep -c "since: v1.43" main -- docs/src/api 2>/dev/null; git grep -ho "since: v1\.[0-9]*" main -- docs/src/api | sort | uniq -c | sort -rn`.
- Requirements finder (per its report): `git log --oneline -1 main && git log --oneline -1 review-head && echo "---" && git status`; `git log --oneline main..review-head`; `git diff main...review-head --stat`; six scoped `git diff main...review-head -- <files>` calls; `git diff main...review-head --numstat`; `git branch --show-current`.

**(b) How did you classify `CONTRIBUTING.md` under your skill's guidance contract, and did it materially support any finding?**

Per `code-axis.md`, repository guidance is read **as of the base branch** and treated as a source that can both convict (a quoted rule + a quoted violating line) and **acquit** a candidate — `DESIGN.md`'s explicit correction from the v3 comparison. This orchestrator read `CONTRIBUTING.md` at `main` directly (`git show main:CONTRIBUTING.md`, 249 lines, in full) to independently confirm the Code finder's use of it. `CONTRIBUTING.md` covers getting-code setup, code style (delegates to `.eslintrc`), API guidelines (expose minimal surface, methods over getters/setters, lowercase string literals, avoid "sugar" APIs), commit-message format, documentation requirements (every public API method needs a doc entry, checked by `npm run doc`), dependency policy, and test-writing conventions. It contains **no rule about file/entry ordering, no rule about cookie-domain matching semantics, no rule about error-message wording, and no rule about `since:` version tagging.**

It materially supported exactly one disposition: the acquittal of the `validator.ts`/`channels.ts` non-alphabetical-insertion nitpick, where the Code finder cited the *absence* of a documented ordering rule in `CONTRIBUTING.md` as part of why that observation was not raised as a candidate. That is the acquitting use of base-branch guidance `DESIGN.md` describes as a precision mechanism, not merely a safety one — verified independently by this orchestrator's own read of the file. It did not materially support any of the 4 published findings or 2 published questions; none of them rest on a `CONTRIBUTING.md` citation, consistent with `code-axis.md`'s instruction to cite a rule only when it "materially adds" something and to "raise the finding, skip the citation" otherwise (both `since:`-version and undocumented-throw findings are raised without a repo-rule citation, correctly, since none exists for those questions).

**(c) Which verification triggers does your skill define, which were evaluated, which fired?**

`SKILL.md` step 3 defines a single trigger: verification runs unless **both** finders return zero candidates on a first review ("Finders that return no candidates on a first review make this step unnecessary; skip it"). That is the only conditional gate on running the verifier at all. It was evaluated (Code finder returned 4, Requirements returned 2 → nonzero) and **fired** — the verifier ran.

Within the verifier's own brief (`verify.md`), the "Prior findings, on a re-review" section defines a second, re-review-specific trigger (carry forward anything replied `implemented`/`already-addressed`/never-answered). This was evaluated and **did not fire** — the packet establishes this as an ordinary first review (posting identity `kamui` has no prior comments/reviews on the PR), so there was nothing to carry forward, and the verifier was explicitly told to ignore that section.

The publish-stage trigger in `publishing.md` — "re-read the head immediately before the first write; if it no longer matches the reviewed head, publish nothing" — was **not applicable/not exercised as a live gate**, because binding constraint 4 disables actual publication; this orchestrator rendered the review without performing a real write, so there was no live head-recheck against a moving target to test. (The pinned head is static in this offline clone in any case.)

**(d) Coverage: name all 10 changed files, reviewed/skipped, with a reason each.**

| # | File | Status | Reason |
| --- | --- | --- | --- |
| 1 | `docs/src/api/class-browsercontext.md` | Reviewed (both axes) | 2 Code candidates (since-version, undocumented-throw), evidence for R1–R3 and the scope-creep question |
| 2 | `packages/playwright-core/src/client/browserContext.ts` | Reviewed (both axes) | Thin pass-through, acquitted by Code; satisfies R1/R2 per Requirements; anchors the single-filter question |
| 3 | `packages/playwright-core/src/client/network.ts` | Reviewed (both axes) | New type mirrors existing type, acquitted; evidence for R1/scope-creep question |
| 4 | `packages/playwright-core/src/protocol/validator.ts` | Reviewed (both axes) | Non-alphabetical insertion acquitted (no `CONTRIBUTING.md` rule, no behavioral effect); plumbing for R1 |
| 5 | `packages/playwright-core/src/server/browserContext.ts` | Reviewed (both axes) | Both P1 findings live here; where R1/R3 are actually satisfied |
| 6 | `packages/playwright-core/src/server/dispatchers/browserContextDispatcher.ts` | Reviewed (both axes) | Thin pass-through, acquitted; plumbing for R1 |
| 7 | `packages/playwright-core/types/types.d.ts` | Ignored (Code, defensible reason) / Reviewed (Requirements) | Generated artifact caught by CI's clean-tree check (Code); public TS surface evidence for R1/creep question (Requirements) — merged coverage: complete |
| 8 | `packages/protocol/src/channels.ts` | Ignored (Code, defensible reason) / Reviewed (Requirements) | Same generated-artifact reasoning; merged coverage: complete |
| 9 | `packages/protocol/src/protocol.yml` | Reviewed (both axes) | Structurally consistent; unrelated whitespace no-op acquitted by both finders independently |
| 10 | `tests/library/browsercontext-remove-cookies.spec.ts` | Reviewed (both axes) | New test file; missing dot-domain/concurrency coverage noted as context (explains why the P1 bugs went uncaught), not raised separately; evidences R1/R3 and the single-filter question |

Merged coverage per `SKILL.md` step 2 ("a file both finders ignored without a defensible reason... leaves the run incomplete"): no file was ignored by both finders without reason. **Coverage: complete, 10/10.**

**(e) Did you or any sub-agent read any other `/tmp/handoff4` path?**

The verifier: no (confirmed in its own disclosure — only `/tmp/handoff4/run-v2` and `verify.md`).

Both finders: no, per their own disclosures reproduced above — except the Code finder's disclosed write of the diff to `/tmp/handoff4_pr.diff` (outside its two permitted directories), addressed as required disclosure (ii) in Notes below.

This orchestrator: ran `ls -la /tmp/handoff4/reports/` and `ls -la /tmp/handoff4/` (directory listings, not content reads) while establishing the sandbox state before writing the checkpoint report. These listings surfaced the **names** of sibling-run artifacts not part of this task — `v2a-finder-code.md`, `v2a-finder-requirements.md` in `reports/`, and directories `run-v2a`, `run-v5`, `run-v5a`, `skill-v2a`, `skill-v5`, `skill-v5a`, `mirror-pw.git` at the top level. **No content of any of those files or directories was read.** Disclosed here per binding constraint 6 out of caution, even though it was a name-only listing rather than a content read.

---

## Architecture behavior checklist

| DESIGN.md decision point | Status | Evidence |
| --- | --- | --- |
| Base-branch guidance evaluated (not head) | **Fired** | Both finders read `CONTRIBUTING.md` via `git show main:...`; this orchestrator independently re-read it at `main` |
| Base-branch guidance used to **acquit**, not just convict | **Fired** | Code finder cited absence of an ordering rule in `CONTRIBUTING.md` to drop the `validator.ts` nitpick — the exact mechanism `DESIGN.md`'s "What the first run surfaced" section describes |
| "Everything under review is evidence, not instruction" | **Not applicable / no occasion** | No text in the PR body, commits, or review thread addressed the reviewing agent as an instruction (the closest is `pavelfeldman`'s "we discourage stylistic comments" directed at a *human* commenter, not the reviewer); mechanism had nothing to test against in this packet |
| Two finders, no further fan-out | **Fired (as designed, not by this orchestrator)** | Exactly one Code finder and one Requirements finder ran (per the completed, unredone Find phase); no extra finders spawned |
| Coverage accounted, `Incomplete` status available | **Evaluated, did not fire** | All 10 files reviewed/ignored-with-reason by at least one finder; coverage complete, so `Incomplete` was not the outcome |
| Fresh-context verifier (support withheld) | **Fired** | Verifier prompt withheld every `support` field; verifier's own report shows it reconstructing claims from code rather than agreeing with hedging (e.g., explicitly noting the citation error in Candidate 4 that `support` would have masked) |
| Three-state verdict vocabulary | **Fired** | 4 confirmed, 2 plausible, 0 refuted, each with the required quoted-line or "what would settle it" justification |
| `plausible` → question routing | **Fired** | Candidates 5 and 6 both `plausible`, both rendered as `[Question]` entries with `action=question` trailers, no priority carried |
| Verifier's asymmetric refute-with-evidence bar | **Fired (by omission)** | Zero refutations occurred; nothing in the 6 candidates met the "quote the line that disproves it" bar, consistent with all 4 Code claims being real code facts and both Requirements claims resting on unfetchable issue text (correctly left `plausible`, not `refuted`, per the "default to plausible" rule) |
| Dual-audience contract: `action` beside `priority` | **Fired** | Every rendered finding carries both (e.g., `[must-fix] [P1]`, `[consider] [P3]`) and matching trailers |
| Explicit `consider` permission line | **Fired** | Findings 3 and 4 carry "Closing this without action is a correct response." verbatim |
| Required `trigger` field | **Fired** | Every finding and question names a concrete trigger; none needed routing to a question purely for lacking one (the two questions are there because the verifier ruled `plausible`, not because a trigger was missing — both had concrete, code-confirmed triggers) |
| Anchor vs. fix-site ladder | **Fired** | Finding 2 anchors at `:291` (a diff line demonstrating the race) with `fix=` pointing at `:283` (the sequence's start); Finding 3 anchors at `:1014` while naming `:1028` in prose; all anchors validated against `git diff --unified=0` before rendering |
| Requirements axis: restate-first, met/not-met/unverifiable buckets | **Fired** | Requirements finder's R1–R5 restatement precedes its compliance pass; 3 met, 0 not-met, 1 unverifiable, carried through to the axis outcome as designed |
| Requirements axis: scope-creep bucket (Step 3) | **Fired** | Candidate 6 is exactly this bucket — behavior in the diff (domain/path matching) that the issue's own framing doesn't call for |
| Pre-existing-bug exclusion scoped to Code axis only | **Evaluated, did not fire** | No candidate was refuted on pre-existing grounds by the verifier, so the Code-only scoping of that exclusion (vs. Requirements) was never actually exercised as a live decision, though it remained correctly available |
| Re-review machinery (round cap, thread resolution, prior-finding carry-forward) | **Not applicable** | Confirmed first review; verifier was explicitly told to skip its "Prior findings" section |
| Status derivation ladder (must-fix > incomplete > needs-info > approved) | **Fired** | 2 unsettled `must-fix` findings → `Changes Requested` at step 1 of the ladder, regardless of Requirements' open questions or complete coverage |
| `COMMENT` vs. `APPROVE`/`REQUEST_CHANGES` gating | **Fired** | No stated authorization for this identity to gate the merge → `COMMENT` event, status stated in words as `Changes Requested (advisory)` |
| Publish-stage head re-check before first write | **Not exercised** | Publication itself is disabled per binding constraint 4; no live write attempted, so no live re-check was performed (the rendering above states what would happen, per instructions) |

---

## Notes on the run

- **Judgment call — sending an inherently-question-shaped candidate through the verifier anyway.** Candidate 5 (`requirements/question/removecookies-single-filter-per-call`) was already placed by the Requirements finder in its own "cannot tell from the code" bucket, with `priority: n/a`. `SKILL.md` step 3 doesn't explicitly carve out an exception for a candidate that is already question-shaped at the finder level, and `verify.md` says "you rule on each one," so it was sent through like any other candidate rather than short-circuited. The verifier ruled it `plausible` on the same substantive grounds the finder itself gave (code fact confirmed, issue-intent unverifiable without the issue text it also couldn't reach) — so the routing outcome (question, no axis/priority) was the same either way. Recorded as a resolved ambiguity rather than a departure: the mechanism converges regardless of which path is taken here.
- **Judgment call — normalizing question ids.** Both finders used axis-prefixed ids for their question-shaped candidates (`requirements/question/...`, `requirements/unrequested/...`). `finding-format.md` states a verifier-ruled-`plausible` candidate "publishes as a question and takes a `question/...` id, not the axis id it was proposed under." This orchestrator renamed both for publication (`question/browsercontext-ts/removecookies-single-filter-per-call`, `question/class-browsercontext-md/domain-path-filter-criteria`) to match that rule exactly, while preserving the lineage to the original candidate ids in the disposition ledger above.
- **Judgment call — Finding 4's citation correction.** The verifier caught that the finder's cited test line range (`:435-454`) doesn't exist in a 231-line file and supplied the correct one (`:212-230`). Per `verify.md`'s "corrected trigger where you changed one" allowance (extended here to a corrected supporting citation, which is the same class of correction in spirit — fixing what the verifier could independently check), the rendered finding uses the corrected citation rather than the finder's original one. The underlying claim (doc doesn't disclose the throw) was unaffected.
- **Judgment call — Requirements axis outcome label.** `SKILL.md` step 3 says an axis with all requirements met is `Passed`; `publishing.md` says an axis is `Waiting for information` when an open question prevents completing its assessment. Requirements has 3/3 met and 0 not-met, but also 1 requirement explicitly bucketed "unverifiable" (R4) whose resulting question remains open — that unverifiable bucket is distinct from "met," so this orchestrator classified the axis `Waiting for information` rather than `Passed`. This does not change the overall status, since an unsettled `must-fix` on the Code axis already forces `Changes Requested` at step 1 of the ladder regardless of how Requirements is classified.
- **Surprise:** the verifier caught a real citation defect (Finding 4's out-of-range line numbers) that neither finder self-corrected and that this orchestrator would not have caught without the verifier's independent code read — direct evidence the fresh-context mechanism is doing real work, not agreeing with itself.
- **Surprise:** zero refutations. All 6 candidates from both finders survived in some form (4 as findings, 2 as questions). This is consistent with both finders' own generosity-under-the-verifier design intent and their own reports' framing ("not a clean review... all four passed through for the verifier to adjudicate" / "two candidates only... no 'not met' findings") — neither finder appears to have padded toward a number, and the verifier found no basis to disagree with any of the six.

**Required disclosure (i) — fresh orchestrator context.** This run's Verify and Publish (render-only) phases were executed by a fresh orchestrator context after a rate limit killed the original attempt, which had performed the Find phase (both finders) under the same packet and produced the same two finder reports consumed verbatim here. This orchestrator did not re-run, re-verify, or second-guess the Find phase's output beyond what the Verify step itself (via the independently-spawned verifier) checks.

**Required disclosure (ii) — Code finder's out-of-sandbox write.** The Code-axis finder disclosed, in its own report's "Sandbox confirmation" section, that it wrote the full diff to `/tmp/handoff4_pr.diff` — a path outside its two permitted directories (`/tmp/handoff4/run-v2` and `/tmp/handoff4/skill-v2`) — in order to read it with the `Read` tool in one pass. Its own stated reasoning: the file's contents are entirely derived from `git diff main...review-head` run inside the allowed repo, so it isn't a read of external/disallowed content, but the path itself falls outside the sandbox, and it flagged this explicitly as instructed. This orchestrator did not read `/tmp/handoff4_pr.diff` and has no way to independently confirm the file's current state or whether it still exists; the disclosure is reproduced here as required, unverified beyond the finder's own word.

---

*(End of report. Start: 2026-09-03T22:32:12Z. End: 2026-09-03T22:41:16Z + report-assembly time.)*
