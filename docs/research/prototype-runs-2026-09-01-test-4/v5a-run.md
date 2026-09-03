# v5a run — `code-review-publish-5a` against `microsoft/playwright#29698`

**2026-09-03.** Data only. Not published to the PR. See [`README.md`](README.md) for the
pinned run identity, the ground truth, and the conditions held constant across all four runs.

> This run completed in a single pass.

---


## Metadata

| | |
| --- | --- |
| Skill | `code-review-publish-5a`, snapshot `/tmp/handoff4/skill-v5a/skills/code-review-publish-5a/` (workflow id `v5a-1`) |
| Architecture | SKILL.md as written: step 1 pinned by the packet (no re-resolution); step 2 built the private changed-file manifest and requirement ledger; step 3 ran as one integrated primary reviewer over the complete merge-base diff, falsifying every candidate in place, then dispatched exactly one candidate-mode verifier batch (one mandatory candidate) via `references/verifier.md`; step 4 skipped (no prior review/reply/trailer from the posting identity — first review); step 5 ran `scripts/validate_review.py` on the assembled payload (0 violations) before any write; step 6 (publish) executed only through "render the review exactly as it would be posted," per binding constraint 4 — no write attempted. |
| Model | `sonnet` passed explicitly (`model: "sonnet"`) on the one `Agent` call made in this run (the verifier dispatch). No other sub-agents were spawned. |
| Agents spawned | 1 — candidate-mode verifier, general-purpose agent type. |
| Sub-agent tokens | Verifier: `subagent_tokens: 44198`, `tool_uses: 23`, `duration_ms: 166240` (from the `Agent` result's usage block, copied verbatim). Total across all sub-agents: 44,198 tokens, 23 tool uses, ~166.2s. |
| Tool uses | Self-reported, approximate, top-level agent only (excludes the verifier's own 23): reading skill/reference docs and memory (`cat`) ≈ 12; reading the packet ≈ 1; git history/diff/show/status/branch/log ≈ 14; static code reading of the repo beyond the raw diff (`grep`/`sed`/`cat` over source, tests, types, protocol files) ≈ 38; running the skill's own helper scripts (`context_fingerprint.py` × 3, `test_context_fingerprint.py` self-test, `validate_review.py` self-test and real payload) ≈ 5; workspace/report file writes (`mkdir`, heredocs to `/tmp/handoff4/reports/...`) ≈ 6; one `Agent` dispatch. Total ≈ 77 top-level tool calls. |
| Wall clock | 2026-09-03 22:33:18 UTC → 2026-09-03 22:48:18 UTC (≈ 15 minutes) |
| Candidates raised | 14 total considered: 2 published findings (C1, C2), 1 published question (Q1), 1 published observation (O1), 10 acquitted/dropped candidates (A1–A10, see ledger) |
| Candidates surviving falsification | 2 survivors eligible for rendering (C1 must-fix/concurrency, C2 consider/maintainability); Q1 and O1 are not findings and are not subject to the survivor/falsification framing but did pass their own routing gates |
| Verifier verdicts | C1 (`playwright-core/remove-cookies-clear-restore-race`): **confirmed**, with a correction widening `change` and correcting the anchor range from 283–292 to 279–293. No duplicates to merge (only one candidate in the batch). |
| `context` digest | `ade4903fce157eca3d47eae8a85428eca83f5bda1e7baea143b3278a028744dd`. Inputs: `pr.title`/`pr.body` verbatim from packet §3; `issues[0]` = `microsoft/playwright#29662` with `coordinate`/`title`/`body` verbatim from packet §4 and `comments: []` (the packet records only the issue's opening body, no separate issue-thread comments); `specs: []` (no user-supplied spec beyond the issue); `guidance: []` (packet §7: no root/path-scoped `AGENTS.md`/`CLAUDE.md`, no root `CONTEXT.md` at base; `CONTRIBUTING.md` exists but is excluded from digest membership by the output contract's exhaustive rule — see Specific answers (b)). Recomputed independently twice with `scripts/context_fingerprint.py`: once from the input as first assembled, once from a key-order- and array-order-shuffled version of the identical semantic content; both runs produced the same 64-hex digest, confirming the documented order-invariance. |
| Findings for publication | 2: `[P1] [must-fix]` cookie-loss race in `removeCookies` (independent-confirmed); `[P3] [consider]` `.d.ts`/`.md` doc drift for `removeCookies`. |
| Questions | 1: whether `removeCookies({ domain })` reliably matches cookies set via a real `Set-Cookie` `Domain` attribute. |
| Observations | 1 (of a cap of 3): an unrelated whitespace-only edit to `ElectronApplication.events.console` in `packages/protocol/src/protocol.yml`. |
| Ambiguities | 1: whether a CI status report reproduced in the packet alone can ground a published `Observations` entry (resolved by applying the narrower reading — repository evidence only). |
| Coverage | Complete over all 10 changed files (reviewed: 10, ignored: 0, unreviewed: 0); risk-directed checks (concurrency/data-loss, external-contract/version-skew, repository-guidance) evidence-backed; the one mandatory verification finished. See Specific answers (d) for the per-file table. |
| Derived status | **Changes Requested (advisory)** — one unsettled, independently confirmed `must-fix` finding; posting identity is an ordinary non-gating `COMMENT` review (packet §1), so per the output contract's status/event table this renders as `Changes Requested` with the `(advisory)` marker and event `COMMENT`. |

## Full reviewer report — verbatim

This section is the complete, unsummarized primary-reviewer output. It is identical to the "Would-be published review, verbatim" section below by design — the primary reviewer's output *is* the rendered review in this workflow, so it is not duplicated a second time; see that section for the full text (summary body, both findings, the question, the observation, and the ambiguity, in rendered form with trailers).

## Verifier dispatch — exact prompt and verbatim report

**Mode fired:** Candidate mode (not clean-verdict mode). Two candidates (C1, C2) survived primary falsification, so the zero-survivor precondition for clean-verdict mode was never met. Of the two survivors, only C1 met a mandatory-verification trigger from `SKILL.md` step 3: it was proposed as `must-fix` **and** it is a concurrency/data-loss candidate (`kind=concurrency`, claim is that concurrently-written cookies are silently and permanently dropped). C2 (`consider`, `maintainability`, a plain two-file text mismatch requiring no cross-module trace) met no mandatory trigger and was not sent to the verifier, consistent with `references/output-contract.md`'s "include an ordinary `consider` survivor only when proving or refuting its claim requires a cross-module trace or another difficult reconstruction" — it did not. One candidate batch was dispatched; no follow-up batch was needed (see Mechanism checklist, N3).

### Exact prompt given to the verifier

```
You are the independent verifier for one candidate finding from a static code review, per
code-review-publish-5a's references/verifier.md, candidate mode. Read that file's "Verification
task" and "Verdicts" sections as your authoritative instructions if you have access to it at
/tmp/handoff4/skill-v5a/skills/code-review-publish-5a/references/verifier.md (read-only). You are
NOT a second reviewer: do not search for unrelated findings, do not write anything, do not run any
command against the repository.

BINDING CONSTRAINTS (identical to the primary reviewer's):
- No network of any kind: no git fetch/pull, no gh, no curl, no web fetch.
- No execution against the repository: no npm/npx/node/tsc/eslint/test runner/build. Reason
  entirely from static source. If a claim would ordinarily be settled by running something, say so
  instead of running it.
- History is truncated at the pinned head (cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b) on purpose;
  nothing after this PR exists locally. Report explicitly whether you read any history beyond the
  pinned head, and list every history command you ran (even if the answer is "none").
- Stay in your sandbox: you may read anywhere under /tmp/handoff4/run-v5a (the repository, checked
  out at branch `review-head` = the pinned head; branch `main` = the merge-base) and
  /tmp/handoff4/skill-v5a. Do not read any other /tmp/handoff4/* path (other run clones, other
  skill snapshots, the reports directory). If you do read one by accident, say so explicitly in
  your report.
- Make no writes anywhere.

REPOSITORY AND PINNED COORDINATES
- Repository: microsoft/playwright, offline clone at /tmp/handoff4/run-v5a.
- head = cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b (branch `review-head`, checked out)
- base-ref = main, base-sha = merge-base = 9a38aedf09f203a58008756e588324254abaef9a (branch `main`,
  force-pinned to the merge-base)
- Linked issue: microsoft/playwright#29662, "[Feature]: Remove cookie/cookies from context" — body
  asks for a way to remove specific cookies from a BrowserContext by criteria, motivated by removing
  a GDPR-consent cookie that was set via globalSetup.
- Applicable base-branch repository rule file: CONTRIBUTING.md (present at base; no AGENTS.md,
  CLAUDE.md, or CONTEXT.md exist in this repository at base).

CANDIDATE RECORD (this is the only candidate in this batch)

```yaml
id: playwright-core/remove-cookies-clear-restore-race
kind: concurrency
priority: P1
action: must-fix
anchor:
  type: line
  path: packages/playwright-core/src/server/browserContext.ts
  start_line: 283
  end_line: 292
  side: RIGHT
title: Fix cookie loss when removeCookies races with concurrent cookie writes
claim: >
  BrowserContext.removeCookies (packages/playwright-core/src/server/browserContext.ts, lines
  279-294 on the pinned head) implements removal as: snapshot all current cookies via
  `await this.cookies()`, compute `cookiesToKeep` by filtering out matches in memory, then
  `await this.clearCookies()` (which wipes every cookie in the browser context, not just the
  matched ones), then `await this.addCookies(cookiesToKeep)` to restore the kept subset. These are
  three separate, non-atomic async round trips to the browser backend. Any cookie written into the
  same browser context by other concurrent activity (e.g. a page navigation receiving a
  `Set-Cookie` response header, a `document.cookie` write from page script, or another
  `addCookies`/`removeCookies` call) after the initial snapshot is taken is not in `cookiesToKeep`,
  is wiped by `clearCookies()`, and is never restored — it is silently and permanently lost, even
  though it never matched the removal filter and even though nothing else in this diff or the
  existing codebase treats this as an accepted trade-off.
trigger: >
  A page or another concurrent caller in the same BrowserContext sets or modifies any cookie after
  `removeCookies`'s internal `await this.cookies()` snapshot but before its `await
  this.addCookies(cookiesToKeep)` completes.
impact: >
  The newly-written cookie is permanently dropped with no error, warning, or return value
  indicating loss. This is data loss on a common concurrency pattern (Playwright contexts
  routinely have multiple pages/navigations active at once), and it is a regression relative to
  every other cookie-mutating method in this file (`addCookies`, `clearCookies`,
  `clearPermissions`, etc.), none of which perform a read-modify-write cycle across the whole
  context's cookie jar.
change: >
  Do not implement removeCookies as "wipe every cookie in the context, then restore a
  possibly-stale subset." Either (a) after `addCookies(cookiesToKeep)` completes, take a second
  `cookies()` snapshot and re-add any cookie now present that is absent from `cookiesToKeep` and
  does not match the removal filter, so cookies written during the clear/restore window are not
  lost; or (b) delete only the matching cookies via a backend primitive that targets them
  specifically, without ever clearing non-matching cookies. State which each of the three browser
  backends (chromium, firefox, webkit) can support.
requirement_source: none (this is a Code candidate, not a requirement-ledger candidate)
verification: pending
```

RAW CODE CITATIONS (for your convenience; verify them yourself against the live files — do not
trust this transcription)

`packages/playwright-core/src/server/browserContext.ts` (pinned head), the whole method:
```ts
async removeCookies(filter: {name?: string, domain?: string, path?: string}): Promise<void> {
    if (!filter.name && !filter.domain && !filter.path)
      throw new Error(`Either name, domain or path are required`);

    const currentCookies = await this.cookies();

    const cookiesToKeep = currentCookies.filter(cookie => {
      return !((!filter.name || filter.name === cookie.name) &&
        (!filter.domain || filter.domain === cookie.domain) &&
        (!filter.path || filter.path === cookie.path));
    });

    await this.clearCookies();
    await this.addCookies(cookiesToKeep);
  }
```

The abstract `addCookies`/`clearCookies` contract is declared in the same file
(`abstract addCookies(cookies: channels.SetNetworkCookie[]): Promise<void>;` /
`abstract clearCookies(): Promise<void>;`) and implemented once per backend. Confirm for yourself
in at least the chromium backend
(`packages/playwright-core/src/server/chromium/crBrowser.ts`, methods `addCookies`/`clearCookies`
near line 410) whether `clearCookies()` is genuinely a whole-context wipe (not scoped to the
filtered subset), and separately check the firefox and webkit backends
(`packages/playwright-core/src/server/firefox/ffBrowser.ts`,
`packages/playwright-core/src/server/webkit/wkBrowser.ts`) for the same
`doGetCookies`/`addCookies`/`clearCookies` shape, since this candidate is `kind: concurrency` and
your task therefore requires you to (1) name the broken invariant, (2) enumerate every sibling code
path governed by it — here, whether the same three-step race exists identically for all three
browser backends because `removeCookies` itself lives once in the shared abstract `BrowserContext`
base class — and (3) state for each sibling path whether the proposed `change` protects it, widening
`change` if the proposed fix covers only one projection of the bug class.

Also inspect the new test file `tests/library/browsercontext-remove-cookies.spec.ts` (all of it) to
confirm it does not already exercise or foreclose this concurrency window, and check
`packages/playwright-core/src/server/network.ts` if you want independent context on how cookie
identity/domain is represented (not required to decide this particular claim, which is about
ordering/atomicity, not domain-string matching).

TASK
Follow references/verifier.md's "Verification task" exactly: read the cited anchor and fix site,
trace the trigger through current code, establish whether unchanged code prevents the failure,
confirm the diff introduced this behavior (it is new code, not a pre-existing pattern reused from
elsewhere — please independently confirm that by checking whether any other method in this
codebase already composes clearCookies()+addCookies() this way), and confirm the issue/PR
description/rules/history do not establish this as an intentional, accepted trade-off. Then, since
this is `kind: concurrency`, do the invariant/sibling-path/fix-sufficiency check described above.

Return exactly one verdict for id `playwright-core/remove-cookies-clear-restore-race`:
`confirmed`, `plausible`, or `refuted`, per the definitions in references/verifier.md, with a
concise independent justification, decisive code citations, and any correction to `trigger`,
`impact`, `priority`, `action`, `anchor`, `fix`, or `change` (including whether `change` needs to
be widened per the sibling-path check). If you notice an accurate, sub-threshold fact incidentally,
you may return at most one non-actionable `observation` aside with a decisive evidence pointer and
no `should`/`must` language — do not search for it deliberately. Do not return publication-ready
prose. Do not render a finding comment yourself.

At the end of your report, state: (1) every git history command you ran, if any, and confirm you
did not read history beyond the pinned head; (2) confirm you did not read any other /tmp/handoff4/*
path; (3) confirm you made no writes and ran no repository commands.
```

### Verbatim verifier report

```
## Verdict for `playwright-core/remove-cookies-clear-restore-race`: **confirmed**

### Independent justification

**Introduced-here (Code candidate requirement).** `git diff main..review-head -- packages/playwright-core/src/server/browserContext.ts` shows `removeCookies` (lines 279–293 in full, not 283–292) is entirely new code added by this PR — every line is a `+`. The only other `clearCookies()`+`addCookies()` composition in the codebase is `_resetCookies()` (browserContext.ts:540–544), used for context-reuse resets: it restores a *fixed desired* `storageState`, not a snapshot meant to preserve arbitrary pre-existing cookies, so it does not establish this read-modify-write pattern as an accepted, pre-existing idiom. Confirmed via `grep -rn "clearCookies()"` across `packages/playwright-core/src/`.

**Trigger traced, nothing in unchanged code prevents it.** `removeCookies` performs three independent `await` round-trips to the browser backend (`cookies()` → `clearCookies()` → `addCookies()`) with no lock/mutex/queue anywhere in `BrowserContext` or `browserContextDispatcher.ts` (`grep -n "_lock\|Mutex\|serialize\|queue"` returned nothing). Multiple pages in one context can navigate/write cookies concurrently; nothing serializes that against `removeCookies`.

**Impact confirmed identically across all three backends** — `clearCookies()` is a genuine whole-context wipe, never scoped to the filtered subset:
- chromium `crBrowser.ts:414-416` — `Storage.clearCookies({ browserContextId })`
- firefox `ffBrowser.ts:298-300` — `Browser.clearCookies({ browserContextId })`
- webkit `wkBrowser.ts:275-277` — `Playwright.deleteAllCookies({ browserContextId })`

None take a name/domain/path filter, so any cookie written into the context during the race is wiped, and only the stale `cookiesToKeep` snapshot is restored — the new cookie is silently, permanently lost, exactly as claimed.

**No accepted trade-off.** `git log main..review-head --format='%H %s%n%b'` shows five iterative commits plus a docs-only tail commit; none mention concurrency/atomicity/races. `docs/src/api/class-browsercontext.md:1013-1025` documents no such caveat. The new test file `tests/library/browsercontext-remove-cookies.spec.ts` (all 8 tests read) only exercises sequential add→goto→remove→goto assertions and never introduces a concurrent write during removal — it neither exercises nor forecloses this window. `CONTRIBUTING.md` has no concurrency-related rule.

### Concurrency-kind mandatory checks

1. **Broken invariant**: `removeCookies` must not lose any cookie that does not match its removal filter, even under a concurrent cookie write to the same `BrowserContext` during the call.
2. **Sibling paths**: `removeCookies` exists exactly once, in the shared abstract `BrowserContext` base class, inherited unchanged by the chromium/firefox/webkit subclasses. All three backends' `clearCookies`/`addCookies`/`doGetCookies` have the identical "whole-context, unfiltered" shape (cited above), so the race is realized identically for all three — one shared logical path, fully exposed on every backend.
3. **`change` must be widened**: option (b) ("delete only matching cookies via a backend primitive") is **not** uniformly available:
   - **Chromium** *does* expose a matching scoped primitive: CDP `Network.deleteCookies` (`chromium/protocol.d.ts:9733-9755`) takes `name` (required) plus optional `domain`/`path` — almost exactly `removeCookies`' filter shape.
   - **Firefox**: the exposed `Browser` domain (`firefox/protocol.d.ts`) has only `setCookies`/`clearCookies`/`getCookies` — no scoped/selective delete at context level.
   - **WebKit**: the exposed `Playwright` domain has only whole-context `getAllCookies`/`setCookies`/`deleteAllCookies`; the only per-cookie primitive, `Page.deleteCookie` (`webkit/protocol.d.ts:7017-7026`), is page-scoped (`cookieName`+`url`, no independent domain/path match) and cannot substitute for a context-level selective delete.
   Since `removeCookies` is one shared method, a uniform fix is required: option (a) (post-restore reconciliation — re-snapshot after `addCookies(cookiesToKeep)` and re-add anything present that isn't in `cookiesToKeep` and doesn't match the filter) is the only approach that protects firefox and webkit today; chromium could additionally/alternatively switch to `Network.deleteCookies` as a backend-specific hardening, but `change` should require (a) or an equivalent invariant-preserving approach as the baseline, not present it as an equally-viable option (b) across all backends.

### Minor corrections
- **Anchor**: full fix site is lines 279–293 (candidate cites 283–292, which omits the guard clause and closing brace); not blocking.
- No duplicate candidates to merge — only one candidate was supplied in this batch.

### Required disclosures

1. **Git history commands run** (all within `main..review-head`, i.e. base merge-base to pinned head — nothing beyond the pinned head, no fetch/pull/remote access):
   - `git branch -a`
   - `git log --oneline -1 review-head`
   - `git log --oneline -1 main`
   - `git diff main..review-head -- packages/playwright-core/src/server/browserContext.ts`
   - `git log main..review-head --oneline`
   - `git log main..review-head -p --stat | head -50`
   - `git log main..review-head --format='%H %s%n%b' --`
   I did not read any history beyond the pinned head (`cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b`).
2. I did not read any `/tmp/handoff4/*` path other than `/tmp/handoff4/run-v5a` (the assigned repository clone) and `/tmp/handoff4/skill-v5a/skills/code-review-publish-5a/references/verifier.md`.
3. I made no writes anywhere and ran no repository commands other than read-only `git log`/`git diff`/`git branch` and file inspection (`cat`, `sed`, `grep`) — no build/test/lint/execute commands were run.
```

**Disposition after verifier return:** C1 kept `action=must-fix`, `priority=P1` (verifier did not correct either), gained `verification: independent-confirmed`, had its anchor corrected to `browserContext.ts:279-293`, and had `change` rewritten to state option (a) — post-restore reconciliation — as the required baseline fix rather than presenting it as one of two equally-viable options, per the verifier's sibling-path finding that firefox and webkit have no scoped-delete primitive. The rendered finding below reflects this corrected form.

## Complete private disposition ledger

Every candidate considered in this run, in the order raised. `kind` and `action`/`priority` are shown for survivors; acquitted/dropped candidates keep the compact one-line form the rubric specifies (claim, kind, disposition, one-line falsification reason, one evidence pointer).

| id | claim (compact) | kind | disposition | reason |
| --- | --- | --- | --- | --- |
| `playwright-core/remove-cookies-clear-restore-race` (C1) | `removeCookies` snapshots, clears the whole context, then restores a stale subset, losing cookies concurrently written during the window | concurrency | **survivor, independent-confirmed, published** `[P1] [must-fix]` | Verifier `confirmed`; evidence at `packages/playwright-core/src/server/browserContext.ts:279-293` and all three backends' `clearCookies()` (see verifier report). |
| `playwright-core/remove-cookies-doc-drift` (C2) | `class-browsercontext.md` and `types.d.ts` give different rationale text for when `removeCookies` throws | maintainability | **survivor, primary-confirmed, published** `[P3] [consider]` | Direct text diff: `docs/src/api/class-browsercontext.md:1016` vs `packages/playwright-core/types/types.d.ts:8442`; caused by commit `cb02d5ba1` editing only the `.md`. No mandatory-verification trigger; not sent to verifier. |
| `playwright-core/remove-cookies-domain-dot-matching` (Q1) | Untested whether `removeCookies({domain})` matches cookies set via a real `Set-Cookie` `Domain=` header the same way it matches `addCookies`-authored cookies | requirement/consistency | **routed to question, published** | Static-unresolvability: the browser-engine domain-normalization convention for header-set cookies is empirical, not visible in this repo's source, and no test exercises it; `filterCookies` in `packages/playwright-core/src/server/network.ts` is decisive evidence that domain strings are not assumed to be literal-equal elsewhere in this codebase, which is why the gap is live rather than idle speculation. |
| protocol.yml drive-by whitespace edit (O1) | `packages/protocol/src/protocol.yml:3234` (`ElectronApplication.events.console.parameters:`) had trailing whitespace removed, unrelated to the feature | — | **routed to observation, published** | Accurate but fails the "meaningful impact" gate — no behavior change; a verifier aside was not the source (found during primary review), routed per the rubric's "accurate fact that fails admission on... meaningful... consequence" clause. |
| A1: substring-match bug from review comment #1 (`removeCookies('long-cookie-name')` would match `long`, `cookie`, `name`) | bug | **acquitted (already fixed)** | Current code uses strict equality `filter.name === cookie.name` (`browserContext.ts:286`), not substring/`.includes()` matching. Fixed in commit `c3f031994`. |
| A2: wasted `cookies()` call before the required-filter guard (review comment #4) | maintainability | **acquitted (already fixed)** | Guard (`browserContext.ts:280-281`) now runs before `await this.cookies()` (`:283`). Fixed in commit `c3f031994`. |
| A3: variable naming `setCookies`/unnamed filter var (review comments #5, #7) | maintainability | **acquitted (already fixed)** | Current names are `currentCookies` and `cookiesToKeep`, matching the requested renames. Fixed in commit `c3f031994`. |
| A4: parameter named `filter` instead of `criteria` (review comment #6) | maintainability | **dropped (intentionally deferred)** | Maintainer (`pavelfeldman`) explicitly deferred this ("we can fix during the pre-release api review") rather than requesting it now; gate 6 (unintentional) fails — this is a known, deliberately-postponed decision, not something to re-surface as a new finding. |
| A5: `removeCookies` as a whole may be "sugar" API per `CONTRIBUTING.md`'s API guidelines ("Avoid adding 'sugar' API... unless very common") since it is fully expressible as existing `cookies()`+`clearCookies()`+`addCookies()` | requirement/repo-rule | **dropped (deliberate, maintainer-approved)** | The maintainer reviewed and approved this exact feature ("Looks great!", then APPROVED) with full knowledge of its implementation; gate 6 (unintentional) fails — this is litigated, accepted repository policy application, not an oversight. |
| A6: `since: v1.43` tag is one version ahead of `package.json`'s `"1.42.0-next"` at base, while sibling new methods elsewhere use `since: v1.42` | maintainability | **dropped (insufficient evidence)** | Plausible, ordinary release-boundary practice (deferring a late-landing feature to the next minor); no repository evidence in the pinned history contradicts it, and the reviewer cannot access post-head history or release notes to settle it further. Not proven wrong (gate 4 fails for a *finding*; did not rise to question status either, since it is not proven to be outcome-changing). |
| A7: empty-string filter fields (`{name: ''}`) are falsy and silently treated as "not provided," which could theoretically hide an empty-named cookie | edge-case/bug | **dropped (speculative, low impact)** | Consistent with the codebase's existing convention of using falsy checks for "unset" optional string fields throughout `removeCookies` itself (the top-level guard uses the identical falsy check); empty-string cookie names are not a realistic scenario named by the issue or tests. Fails gates 1 (meaningful impact) and 5 (grounded intent). |
| A8: dispatcher's `removeCookies` doesn't take a `CallMetadata` parameter | consistency | **acquitted (matches siblings)** | `addCookies`/`clearCookies` on the same dispatcher (`browserContextDispatcher.ts:218-223`) also omit `CallMetadata`; consistent, not a defect. |
| A9: `BrowserContextRemoveCookiesOptions` is an empty `{}` type in `channels.ts` | consistency | **acquitted (matches siblings)** | `BrowserContextClearCookiesOptions` and other sibling generated `*Options` types are identically empty when a method takes no separate options object; matches existing code-generation convention. |
| A10: CI-reported single flaky failure of "should remove cookies by domain and path" on webkit (packet §6, last CI comment) | test-infra | **dropped (no repo evidence, no execution available)** | Cannot be investigated further under this run's no-execution constraint; a single flake amid an otherwise all-green CI history is consistent with this suite's documented pre-existing flakiness (every CI comment in the packet lists unrelated flaky tests); does not carry a decisive repository evidence pointer, so it was also not promoted to a formal Observation (see the recorded Ambiguity). Mentioned in the rendered review's Ambiguities prose rather than published as a standalone item. |

## Everything consulted beyond the diff

**Skill package** (`/tmp/handoff4/skill-v5a/skills/code-review-publish-5a/`): `SKILL.md`, `DESIGN.md`, `references/review-rubric.md`, `references/output-contract.md`, `references/verifier.md`, `references/re-review.md` (read to confirm step 4 could be skipped), `scripts/context_fingerprint.py`, `scripts/test_context_fingerprint.py` (ran its self-test), `scripts/validate_review.py` (ran `--self-test` and the real payload).

**Packet:** `/tmp/handoff4/packet-playwright.md` (read in full).

**Repository files beyond the 10-file changed-file manifest** (all under `/tmp/handoff4/run-v5a`, all read-only, all pinned to `review-head`/`main` as checked out — no fetch):
- `packages/playwright-core/src/server/chromium/crBrowser.ts` — `doGetCookies`/`addCookies`/`clearCookies` (chromium backend semantics, CDP `Storage.*` calls).
- `packages/playwright-core/src/server/firefox/ffBrowser.ts`, `packages/playwright-core/src/server/webkit/wkBrowser.ts` — confirmed the same three methods exist per backend.
- `packages/playwright-core/src/server/network.ts` — `filterCookies` (domain leading-dot normalization, motivating Q1) and `rewriteCookies` (used to rule out a type-mismatch candidate between `NetworkCookie` and `SetNetworkCookie`).
- `packages/protocol/src/channels.ts` (beyond the diff hunk) — `NetworkCookie`/`SetNetworkCookie` full type definitions.
- `CONTRIBUTING.md` (full file) — repository guidance at base; used for the API-guidelines ("sugar API") acquittal (A5) and to confirm no concurrency/testing rule bears on C1.
- `package.json` — `"version": "1.42.0-next"` and the `lint`/`doc` script definitions (for the since-tag check, A6, and to note what static tooling exists that this run cannot execute).
- `docs/src/api/class-page.md`, `docs/src/api/class-electronapplication.md` — cross-checked `since:` tag conventions for A6.
- `tests/library/browsercontext-remove-cookies.spec.ts` — read in full (231 lines / all 8 tests), both by the primary reviewer and, independently, by the verifier.

**Git history/inspection commands run by the primary reviewer** (all within the pinned `main`↔`review-head` range; see Specific answers (a) for the completeness statement):
`git status`, `git branch -av`, `git log --oneline -20 review-head`, `git log --oneline -5 main`, `git diff --stat main review-head`, `git diff main review-head -- <each of the 9 non-test changed files, individually and in small groups>`, `git show cb02d5ba1 --stat`, `git show cb02d5ba1` (full patch of the PR's final commit), `git show c3f031994:packages/playwright-core/types/types.d.ts` (twice, to inspect the pre-final-commit state of the doc comment for C2's falsification).

**Git history/inspection commands run by the verifier** (listed verbatim in its own report above): `git branch -a`; `git log --oneline -1 review-head`; `git log --oneline -1 main`; `git diff main..review-head -- packages/playwright-core/src/server/browserContext.ts`; `git log main..review-head --oneline`; `git log main..review-head -p --stat | head -50`; `git log main..review-head --format='%H %s%n%b' --`. The verifier additionally read `packages/playwright-core/src/server/browserContext.ts:540-544` (`_resetCookies`), the chromium/firefox/webkit `protocol.d.ts` files (for the CDP/backend primitive survey), and `tests/library/browsercontext-remove-cookies.spec.ts` in full.

**Not consulted:** anything reachable only via network (no `git fetch`/`gh`/`curl`/web fetch was run by the primary reviewer or the verifier); anything under any other `/tmp/handoff4/*` directory (see Specific answers (e)).

## Would-be published review, verbatim

**Changes Requested (advisory)** — 1 must-fix finding.

**Intent:** Add `BrowserContext.removeCookies(filter)` to remove cookies by name/domain/path, implementing microsoft/playwright#29662.

**Issue fit:** Met — the requested capability (remove specific cookies from a context without recreating it) is implemented and covered by tests; the API shape (a `{name, domain, path}` filter object rather than the issue's illustrative `removeCookies([cookieObject, ...])`) was explicitly negotiated with the maintainer during review and is not required by the issue's non-goals.

**Coverage:** Complete merge-base diff reviewed (10/10 changed files); concurrency/data-loss, external-contract/version-skew, and repository-guidance (`CONTRIBUTING.md`) risk checks are evidence-backed. One candidate required independent verification and was `confirmed`; see run trailer.

**Reviewed:** `cb02d5ba1` against merge-base `9a38aedf0`.

## Findings

- [P1] [must-fix] Fix cookie loss when removeCookies races with concurrent cookie writes — anchor `packages/playwright-core/src/server/browserContext.ts:279-293`
- [P3] [consider] Sync the generated `.d.ts` doc comment for removeCookies with its `.md` source — anchor `docs/src/api/class-browsercontext.md:1016`; fix `packages/playwright-core/types/types.d.ts:8442`

---

**[P1] [must-fix] Fix cookie loss when removeCookies races with concurrent cookie writes**

**Triggers when:** Any other cookie write happens in the same `BrowserContext` — a page receiving a `Set-Cookie` response, a `document.cookie` write, another `addCookies` call — after `removeCookies`'s internal snapshot (`await this.cookies()`) but before its restore (`await this.addCookies(cookiesToKeep)`) completes.

**Impact:** `removeCookies` (`packages/playwright-core/src/server/browserContext.ts:279-293`) wipes every cookie in the context via `clearCookies()` and restores only the pre-snapshotted, filtered subset. A cookie written during that window is not in the snapshot, is wiped, and never restored — silent, permanent data loss of a cookie that never matched the removal filter. `removeCookies` lives once in the shared abstract `BrowserContext` base class, and chromium, firefox, and webkit all implement `clearCookies()` as an unfiltered whole-context wipe, so the race is realized identically on every backend.

**Change:** After `addCookies(cookiesToKeep)`, take a second `cookies()` snapshot and re-add any cookie now present that is absent from `cookiesToKeep` and doesn't match the removal filter, so cookies written during the clear/restore window survive. Treat this reconciliation as the required baseline: firefox and webkit expose no per-cookie or selective delete at context scope (only a whole-context clear), so swapping chromium alone to CDP `Network.deleteCookies` would leave the other two backends unprotected.

<!-- finding id=playwright-core/remove-cookies-clear-restore-race head=cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b priority=P1 action=must-fix blocking=true kind=concurrency -->

---

**[P3] [consider] Sync the generated `.d.ts` doc comment for removeCookies with its `.md` source**

**Triggers when:** A developer reads the `removeCookies` JSDoc in `packages/playwright-core/types/types.d.ts` (what ships in the npm package and what IDEs show on hover) instead of the website docs built from `docs/src/api/class-browsercontext.md`.

**Impact:** The two texts disagree about the same behavior. `docs/src/api/class-browsercontext.md:1016` reads "At least one of the removal criteria should be provided," while `types.d.ts:8442` still reads the earlier "The method will throw an error if either name, domain or path has not been passed." The last commit on this PR (`cb02d5ba1`) softened only the `.md` wording and never regenerated `types.d.ts`, so the two doc-generation outputs are now out of sync for this method.

**Change:** Regenerate `types.d.ts` from the current `.md` (or otherwise re-sync the JSDoc comment for `removeCookies`) so both surfaces describe the same behavior.

Closing this without action is a correct response.

<!-- finding id=playwright-core/remove-cookies-doc-drift head=cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b priority=P3 action=consider blocking=false kind=maintainability fix=packages/playwright-core/types/types.d.ts:8442 -->

---

## Open questions

**[Question] Does `removeCookies({ domain })` reliably match cookies set via a real `Set-Cookie` `Domain` attribute?**

**Evidence:** `removeCookies`'s domain filter (`packages/playwright-core/src/server/browserContext.ts:287`) compares `filter.domain === cookie.domain` by strict string equality. The existing `filterCookies` helper (`packages/playwright-core/src/server/network.ts`) treats a cookie's reported `domain` as not reliably normalized — it re-prefixes a leading `.` before comparing scope, because the browser-reported domain string does not always equal the literal `Domain=` value a site sent. The new test suite only exercises domain matching for cookies added via `context.addCookies()`; no test here exercises `removeCookies` against a cookie set by an actual `Set-Cookie: ...; Domain=...` response header — the scenario in the motivating issue (a GDPR-consent cookie set by the site).

**Why it matters:** If the domain string a browser reports for a header-set cookie differs from what `context.addCookies()` round-trips, `removeCookies({ domain })` would silently no-op on exactly its advertised primary use case, with no error.

**Change no code for this.** Run a case with the test server responding `Set-Cookie: name=value; Domain=<host>` and then `context.removeCookies({ domain: '<host>' })`, across chromium/firefox/webkit; the result settles whether this should re-open as a finding.

<!-- question id=playwright-core/remove-cookies-domain-dot-matching head=cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b action=question -->

## Observations

- This diff makes an unrelated whitespace-only edit to the pre-existing `ElectronApplication.events.console` entry. Evidence: `packages/protocol/src/protocol.yml:3234`.

## Ambiguities

- **Whether a CI status report reproduced in the review packet can alone ground a published `Observations` entry.** Reading A: the rubric directs reviewers to read current CI, so a verbatim CI comment (the one flaky `browsercontext-remove-cookies.spec.ts` run on webkit) is itself sufficient grounding for an observation. Reading B: the output contract requires an observation to carry a decisive *repository* evidence pointer, and a CI textual report is not repository evidence. This run applied reading B: the single reported webkit flake on the new domain+path test is noted here in prose but was not published as a formal Observation, since no static repository evidence explains or reproduces it and no execution is available to investigate it further.

<!-- review-run head=cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b base-ref=main base-sha=9a38aedf09f203a58008756e588324254abaef9a merge-base=9a38aedf09f203a58008756e588324254abaef9a workflow=v5a-1 context=ade4903fce157eca3d47eae8a85428eca83f5bda1e7baea143b3278a028744dd issues=microsoft/playwright#29662 coverage=complete -->

This exact payload (summary body plus every finding/question/observation item, trailers included) was validated with `scripts/validate_review.py` before being finalized here — see Specific answers (f). Consistent with binding constraint 4, publication was not attempted; the rendering above is the complete would-be write.

## Specific answers

**(a) Git history beyond the pinned head.** No. Neither the primary reviewer nor the verifier read any commit, ref, or object beyond `cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b` (the pinned head) or before `9a38aedf09f203a58008756e588324254abaef9a` in a way that reached outside the `main`↔`review-head` range; no `git fetch`, `git pull`, `gh`, or remote-touching command was ever run. Every history command run, by either agent:
- Primary reviewer: `git status`; `git branch -av`; `git log --oneline -20 review-head`; `git log --oneline -5 main`; `git diff --stat main review-head`; `git diff main review-head -- <changed files, several invocations>`; `git show cb02d5ba1 --stat`; `git show cb02d5ba1`; `git show c3f031994:packages/playwright-core/types/types.d.ts` (×2).
- Verifier: `git branch -a`; `git log --oneline -1 review-head`; `git log --oneline -1 main`; `git diff main..review-head -- packages/playwright-core/src/server/browserContext.ts`; `git log main..review-head --oneline`; `git log main..review-head -p --stat | head -50`; `git log main..review-head --format='%H %s%n%b' --`.

**(b) `CONTRIBUTING.md` classification.** Classified as applicable base-branch repository guidance for the rubric's "Repository rules" section (findings must cite the applicable file; standards are judged from the base-branch version) — it is the only repository-rule document present at base per packet §7. It was read in full and materially supported one acquittal: candidate A5 (whether `removeCookies` is "sugar" API under `CONTRIBUTING.md`'s "Avoid adding 'sugar' API... unless they're very common" guideline) was dropped specifically because the maintainer's own approval of this exact implementation establishes gate 6 (unintentional) as failed. It did **not** feed the `context` digest: the output contract's guidance-digest membership rule (F1.1) is exhaustive — root/path-scoped `AGENTS.md`/`CLAUDE.md` and root `CONTEXT.md` only — and `CONTRIBUTING.md` matches none of those categories, so `guidance: []` in the digest computation is correct even though `CONTRIBUTING.md` was read and used. It did not materially support either published finding (C1, C2); it supported one acquittal and one general check (confirming no repo rule bears on concurrency or commit/testing hygiene relevant to C1).

**(c) Verification triggers.** `SKILL.md` step 3 defines: mandatory independent verification for every surviving `must-fix` candidate, plus every candidate involving security/authorization, data loss/corruption, destructive migration, or an externally observable compatibility break; and (DESIGN.md G3) a separate zero-survivor clean-verdict trigger for high-risk surfaces. Evaluated against this run's candidates:
- C1 (`must-fix`, `concurrency`, data-loss claim) — **triggered** on two independent grounds (`must-fix` and data loss/corruption). Verified in candidate mode.
- C2 (`consider`, `maintainability`) — evaluated, **did not trigger** (not `must-fix`; not security/data-loss/migration/compat-break).
- Q1, O1 — not findings, not subject to the verification-trigger framing.
- Zero-survivor clean-verdict trigger (G3) — evaluated, **did not fire**: its precondition (zero surviving candidates on a high-risk surface) was never met, since C1 and C2 both survived primary falsification.
- N3 (one permitted follow-up batch for candidates reaching render eligibility after the initial dispatch) — evaluated, **did not fire**: no candidate newly became render-eligible after the C1 batch was dispatched, so no second batch was needed or run.

**(d) Coverage — all 10 changed files:**
| File | Status | Reason |
| --- | --- | --- |
| `docs/src/api/class-browsercontext.md` | reviewed | Diff read in full; cross-checked against `types.d.ts` (source of C2) and other `since:` tags in the same file (A6). |
| `packages/playwright-core/src/client/browserContext.ts` | reviewed | Diff read; confirmed thin client pass-through, consistent with sibling methods. |
| `packages/playwright-core/src/client/network.ts` | reviewed | Diff read; `RemoveNetworkCookieParam` type checked against server-side filter shape. |
| `packages/playwright-core/src/protocol/validator.ts` | reviewed | Diff read; scheme checked against `protocol.yml`/`channels.ts` for consistency (no version skew found). |
| `packages/playwright-core/src/server/browserContext.ts` | reviewed | Primary locus of C1; full method read, surrounding class context (abstract methods, `_resetCookies`) inspected by the verifier. |
| `packages/playwright-core/src/server/dispatchers/browserContextDispatcher.ts` | reviewed | Diff read; checked against sibling `addCookies`/`clearCookies` dispatcher methods (A8). |
| `packages/playwright-core/types/types.d.ts` | reviewed | Diff read; primary locus of C2 (compared against the `.md` source). |
| `packages/protocol/src/channels.ts` | reviewed | Diff read; `NetworkCookie`/`SetNetworkCookie` structural compatibility checked (ruled out a type-mismatch candidate). |
| `packages/protocol/src/protocol.yml` | reviewed | Diff read in full, including the unrelated whitespace-only hunk (source of O1). |
| `tests/library/browsercontext-remove-cookies.spec.ts` (new file) | reviewed | Read in full (231 lines, all 8 tests), by both the primary reviewer and the verifier; used to falsify/refute several candidates and to confirm no test exercises the C1 race or the Q1 domain-header scenario. |

All 10/10 reviewed; none ignored or unreviewed. Coverage is `complete`.

**(e) Other `/tmp/handoff4` directories.** No. The primary reviewer read only `/tmp/handoff4/packet-playwright.md`, `/tmp/handoff4/run-v5a/` (the assigned repo), `/tmp/handoff4/skill-v5a/` (the assigned skill), and its own working files under `/tmp/handoff4/reports/v5a-work/` and the final `/tmp/handoff4/reports/v5a-report.md`. One incidental exception: an `ls -la` was run on `/tmp/handoff4/reports/` before this report existed, to create the directory; that listing showed two filenames belonging to another run (`v2-finder-code.md`, `v2-finder-requirements.md`) but their **contents were never read** — only the directory listing was seen, and no further action was taken on them. The verifier confirmed in its own report that it read only `/tmp/handoff4/run-v5a` and one file under `/tmp/handoff4/skill-v5a` (`references/verifier.md`), touching no other `/tmp/handoff4/*` path.

**(f) Review validator script.** Yes, it ran, at `/tmp/handoff4/skill-v5a/skills/code-review-publish-5a/scripts/validate_review.py`. It was first run with `--self-test` (30 cases passed) to confirm the tool itself works, then run against the fully assembled real payload (summary body + both findings + the question + the observation, trailers included) with `python3 scripts/validate_review.py < payload.json`. **It passed with zero violations** (exit code 0, no output). `scripts/context_fingerprint.py`'s own regression suite (`scripts/test_context_fingerprint.py`) was also run and passed (7 case groups) before trusting the digest tool.

## Mechanism checklist

| ID | Fired? | Evidence |
| --- | --- | --- |
| G1 (statically-unresolvable question channel) | **Fired** | Q1 published: the browser-engine domain-normalization convention for `Set-Cookie`-header-origin cookies is empirical and untestable from source under this run's no-execution constraint; framed with `Change no code for this` and a named settling measurement. |
| G2 (introduced-here gate scoped to Code candidates; requirement candidates exempt) | **Not applicable** | No `kind=requirement` candidate was raised in this run — the issue was fully satisfied (`met`), so the requirement-exemption clause was never exercised. Both C1 and C2 are `kind` values that are trivially "introduced here" (entirely new code/new doc text), so the Code introduced-here gate itself was applied but not meaningfully stress-tested either. |
| G3 (fresh verifier on zero-survivor high-risk clean verdict) | **Did not fire** | Precondition (zero surviving candidates) was not met — C1 and C2 both survived primary falsification, so clean-verdict mode was never a candidate; candidate mode ran instead. |
| G4 (orchestrator recovery protocol for unrecoverable context failures) | **Did not fire** | No input was unavailable or unrecoverable in this run; the packet supplied everything phase 1/2 needed, and no fetch, read, or tool failure occurred that would have required a provisional `Incomplete`/orchestrator-recovery request. |
| G5 (render contestable rubric/contract terms with both readings) | **Fired** | One `Ambiguities` entry recorded: whether a packet-reproduced CI status comment alone can ground a published `Observations` entry, with both readings stated and the applied (narrower) reading identified. |
| N1 (summary-only Observations channel, capped at 3, non-actionable) | **Fired** | One observation published (of the cap of 3): the unrelated `protocol.yml` whitespace edit. No priority/id/anchor/trailer/`should`/`must` language attached. |
| N2 (verifier invariant/sibling-path/fix-widening check for `concurrency`/`invariant` kinds) | **Fired** | The verifier, on C1 (`kind=concurrency`), named the broken invariant, enumerated all three backend sibling paths (chromium/firefox/webkit), determined the proposed fix's option (b) was not uniformly available, and widened `change` to require option (a) as the baseline — exactly the mechanism's intended effect. |
| N3 (one permitted follow-up batch for late-render-eligible candidates) | **Did not fire (correctly unused)** | No candidate newly reached render eligibility after the single C1 batch was dispatched; nothing required a follow-up batch, and none was run. |
| N4 (forced `plausible` → question route via G1) | **Did not fire** | The verifier returned `confirmed`, not `plausible`, for the only verified candidate — this branch was never exercised in this run. |
| F1.1 (exhaustive guidance-digest membership) | **Applied correctly** | `guidance: []` computed per the exhaustive rule; `CONTRIBUTING.md` correctly excluded (see Specific answers (b)) despite being used elsewhere in the review. |
| F1.2 (`consider` survivors included by proof-difficulty; `independent-confirmed` preserved after downgrade) | **Partially exercised** | C2 (`consider`) was correctly *not* sent to the verifier because falsifying it required no cross-module trace (a direct two-file text diff settled it). The "preserved after downgrade" clause was not exercised — the verifier did not downgrade C1's `must-fix`/`P1`, so no correction-preservation case arose. |
| F1.3 (full 40-hex commit SHAs in every trailer) | **Fired/applied** | All trailers use the full 40-character `cb02d5ba126479dddb3ecbe32e8ead024ca5dd6b` / `9a38aedf09f203a58008756e588324254abaef9a`; `scripts/validate_review.py`'s `trailer-sha` check passed against them. |
| F1.4 (`path:line` / `path:start-end` summary anchor format) | **Fired/applied** | Summary anchors rendered as `packages/playwright-core/src/server/browserContext.ts:279-293` and `docs/src/api/class-browsercontext.md:1016`; validator's `summary-anchor` check passed. |
| F1.5 (`Source` after `Change`; consider-permission sentence last) | **Fired/applied** | C2 ends with the exact sentence `Closing this without action is a correct response.` immediately before its trailer; neither finding used `Source` (not materially needed); validator's `field-order` check passed. |
| F1.6 (drift anchor: changed line stating the drifted rule first, then lexicographic/smallest-range tie-break) | **Fired/applied** | C2 anchored on `docs/src/api/class-browsercontext.md:1016` — the changed line stating the (now-drifted-from) rule — rather than the stale, unchanged `types.d.ts` line, with `types.d.ts:8442` correctly relegated to `fix`. |
| F2 (stop only closed-unmerged targets; merged-PR retrospective mode) | **Did not fire** | The packet frames this run as "an ordinary first review" (packet §1) rather than an explicitly invoked retrospective review of a merged target, and gives no "state: closed-unmerged" signal; neither the hard-stop nor the retrospective `Mode:` line applied. See Notes on the run for the judgment call this required. |

## Notes on the run

- **Merged-PR status was never independently confirmed, by design.** The real-world PR this is modeled on was, in fact, merged (it carries an `APPROVED` review and a maintainer-authored final commit). The packet does not state a `state`/`merged` field explicitly, and binding constraint 1/packet framing forbids resolving this over the network. I treated the packet's explicit characterization — "an ordinary first review, event COMMENT" (packet §1) — as the authoritative, already-resolved phase-1 output per the run's own instructions ("Phase 1 ... has already been performed ... treat every fact in this packet as authoritative pinned input"), and did not apply F2's retrospective-mode machinery (no `Mode:` line, publication treated as ordinarily-disabled-by-run-condition rather than disabled-by-retrospective-default). A later replication should note this as a real interpretive fork: a stricter reading could hold that an unresolved merge state is itself an input the reviewer cannot recover, forcing an `Incomplete`/G4 orchestrator-recovery request instead. I judged the packet's explicit "ordinary first review" framing as foreclosing that reading, since re-litigating an already-completed phase-1 output would contradict the run's own instruction not to re-resolve the target.
- **The G3/candidate-mode boundary is easy to conflate.** DESIGN.md's G3 row is specifically about the *zero-survivor clean-verdict* extension; the baseline "verify every must-fix/security/data-loss/migration/compat-break candidate" rule that actually fired here is inherited v5 behavior stated directly in `SKILL.md` step 3, not a separately-numbered G-series mechanism. I initially had to re-read DESIGN.md's table carefully to avoid mislabeling the C1 verification as "G3 firing" in this report — it does not; G3 firing specifically means the clean-verdict batch ran, which never happened in this run.
- **The domain leading-dot theory (Q1) was almost a false-positive finding.** My first hypothesis was that `removeCookies`'s strict-equality domain comparison was already broken for `context.addCookies()`-authored cookies too. Direct evidence refuted that: the CI comments reproduced in the packet show the PR's own "should remove cookies by domain" test passing consistently, and a genuine literal-domain mismatch would fail that test deterministically, not merely flake once on an unrelated test. Only the untested `Set-Cookie`-header-origin path remains genuinely open, which is why it is a question rather than a finding. This is exactly the kind of active-falsification step the rubric asks for, and it materially changed the shape of what got published.
- **Nothing was withheld from the verifier that should not have been.** Per `references/verifier.md`, the candidate record given to the verifier omitted `support`, confidence, and the primary's argument for believing the claim, giving only `claim`/`trigger`/`impact`/`change` plus raw code citations and explicit permission to inspect the repository itself — the verifier's own report shows it re-derived everything (including finding the CDP `Network.deleteCookies` primitive and the firefox/webkit gap) independently rather than merely agreeing with a pre-supplied argument, which is the intended effect of the claim/support separation.
- **Token/tool-count self-reporting is approximate for the top-level agent** (no built-in usage-block equivalent is exposed to this agent for its own turns, unlike the verifier's `Agent` result); the verifier's numbers, by contrast, are copied verbatim from its returned usage block and are exact.
- **Crash safety was honored as instructed:** the primary review output and disposition ledger (in draft form, with C1 marked pending) were written to this file *before* the verifier was dispatched; this file was then rewritten in full with the verifier's confirmed result once it returned.
