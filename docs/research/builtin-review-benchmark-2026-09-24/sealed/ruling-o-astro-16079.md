# Ruling: o-astro-16079 (withastro/astro#16079)

## Target

- Repository `withastro/astro`, PR #16079 "fix(vercel): Fix ISR path rewrite to prevent 404". Author `empoulter-uclan` (Em Poulter, external). Base branch `main`.
- Head `71ae513388df11d7dad6b1e0077c402ad03d0d62`. This is the PR's only commit (`gh pr view --json commits`).
- Reviewed range: merge-base `b089b904f1ed578e9edaefd129bf9843120a808f` .. head.
  - The PR-recorded base `be661fb9fd1348ffb038f561f9f053b1c64a3696` is 2 commits ahead of the merge-base: `2c1ae859d9` (fonts) and `be661fb9fd` ("[ci] format").
  - `git diff --stat b089b904 be661fb9 -- packages/integrations/vercel` is empty, so the reviewed diff is the same from either base.
- Merged 2026-03-25T16:40:00Z as squash commit `aa266364fe9e105317b66e218fe04567307fb57f`. Its parent is `5958ab97d4`.
- Diff: 2 files.
  - `.changeset/common-cats-travel.md`: +5/−0.
  - `packages/integrations/vercel/src/serverless/entrypoint.ts`: +7/−1.
- Licence: MIT. The root `LICENSE` begins "MIT License", and the adapter's `package.json` has `"license": "MIT"`.

## Verdict

1 material defect

## Defect register

### GT-o1: an unauthenticated `x-vercel-isr` header lets any caller choose the rendered route via `x_astro_path` (reintroduces CVE-2026-33768)

**Location.** `packages/integrations/vercel/src/serverless/entrypoint.ts`, the default export's `fetch()`, at head lines 19–34. The new code is lines 21–26:

```ts
let realPath = undefined;
if(hasValidMiddlewareSecret) {
    realPath = request.headers.get(ASTRO_PATH_HEADER)
} else if(request.headers.get('x-vercel-isr') === '1') {
    realPath = url.searchParams.get(ASTRO_PATH_PARAM);   // no secret checked
}
if (typeof realPath === 'string') { url.pathname = realPath; request = new Request(...) }
```

This entrypoint is bundled into both the `_render` function and the `_isr` function; my probe loaded both.

**Violated contract.** The contract was set 6 days earlier by #15959 (commit `335a204161`, 2026-03-19), which is an ancestor of the merge-base.

- Its changeset `.changeset/short-cycles-fail.md` reads: "Fix Vercel serverless path override handling so override values are only applied when the trusted middleware secret is present."
- Its PR body reads: "Require the middleware secret when resolving serverless path overrides."
- Its regression test `packages/integrations/vercel/test/path-override-security.test.js` asserts `'ignores untrusted x_astro_path query param on _render'`.
- The corresponding advisory GHSA-mr6q-rp88-fx84 / CVE-2026-33768 was published 2026-03-24T18:12:25Z, before this PR merged.

This PR brings back an override value taken from the query string. The only guard is a plain request header that any HTTP client can set. Per GHSA-x27w-589x-frm2, Vercel also sets that header itself on direct external requests to `/_isr`.

**Trigger.**

- **Primary (advisory scope):** `@astrojs/vercel` with `isr` enabled, and a route protected at the edge. Edge protection means a Vercel path or firewall rule, or authorization in edge middleware (`edgeMiddleware: true`). The attacker sends `GET /_isr?x_astro_path=/admin`.
- **Code level:** any request to a function built from this entrypoint that carries `x-vercel-isr: 1` and `x_astro_path=<route>`. An example is `GET /api/public?x_astro_path=/api/private` with the header `x-vercel-isr: 1`.
  - Whether Vercel forwards a client-supplied `x-vercel-isr` header to non-ISR functions is **unresolved**. It needs a live Vercel deployment to settle.
  - The `/_isr` vector does not depend on that question.

**Demonstrated consequence.** The origin renders a route the attacker picked, not the route the edge authorized. That is a confused-deputy access-control bypass (CWE-441/CWE-862) that discloses protected GET-rendered content without credentials.

- My reproduction at the head:
  - `_isr` rendered the ISR-excluded page `/two` ("<h1>Two</h1>", 200) for `/_isr?x_astro_path=/two`.
  - `_render` returned `{id:'private'}` for a request addressed to `/api/public`.
- At the merge-base, both requests are not rewritten.
- The maintainers published GHSA-x27w-589x-frm2 / CVE-2026-73424 on 2026-07-17 (medium; affects `@astrojs/vercel >= 10.0.3`, patched in 11.0.3). It names this PR: "Commit aa266364fe (PR #16079, "Fix ISR path rewrite to prevent 404") brought the query parameter back, guarded only by the `x-vercel-isr` header. That header is not a security boundary, so the fix was effectively undone for ISR routes starting in 10.0.3."
- Its PoC shows a Vercel deployment returning 403 for `/admin` and 200 with the admin content for `/_isr?x_astro_path=/admin` (`X-Vercel-Cache: MISS`).
- Scope stated by the advisory: read only (Vercel serves ISR functions for GET only). Classic in-origin middleware is unaffected, and whole-deployment protection is unaffected.

**Required corrective outcome.**

- A caller must never be able to choose the rendered route through `x_astro_path` or any other override, whether through the query or a header.
- A path override may be honoured only when it provably comes from Astro's own build output, meaning an unforgeable per-build secret or an equivalent.
- Legitimate ISR requests, which Vercel rewrites to `/_isr?x_astro_path=$0`, must still render their route rather than 404. That is the behaviour this PR was written to restore, and my probe case A1 shows it is real.
- Upstream (#17370, `3a43cf0f36`) did this with an `x_astro_path_token` equal to the build's `middlewareSecret`: it is appended to the ISR route `dest` and to `allowQuery`, and the entrypoint checks it. A differently shaped fix with the same outcome also counts.

**Promised change or unintended error.** Unintended error. The PR promised to make ISR routes stop 404-ing by rewriting the path for ISR requests; its changeset says "Fix vercel ISR path rewrite". That goal is correct, and the head achieves it. The defect is the authorization gate the PR chose for the rewrite (an attacker-controllable header), which silently undoes #15959's security contract.

**Manifestations** (one defect, one corrective outcome):

1. The `_isr` function, reachable publicly at `/_isr?x_astro_path=…`.
2. The `_render` function, and any other function using this entrypoint, when a client-supplied `x-vercel-isr: 1` header reaches it. This is shown at code level; platform reachability is unresolved.

## Reproduction

All work was in my own clone at `work/astro`, made from the local full mirror. Toolchain: Node v24.21.0, corepack 0.36.0, and pnpm 10.30.3 through a scratch shim `work/bin/pnpm` → `corepack pnpm`.

- **Install:** `pnpm install --frozen-lockfile --filter '@astrojs/vercel...' --filter astro-scripts --filter '{packages/integrations/vercel/test/fixtures/**}'` exited 0 in 3 s (warm store).
- **Build:** `pnpm -r --filter '@astrojs/vercel...' build` exited 0 in 11 s at the head and exited 0 in 11 s at the merge-base.
- **Probe:** `work/probe/isr-override.test.mjs`, outside the repo, run as `ASTRO_REPO=… node --test ../../../../probe/isr-override.test.mjs` from `packages/integrations/vercel`. It builds the upstream fixtures `isr` and `serverless-with-dynamic-routes`, then calls the built `_isr` and `_render` handlers' `fetch` directly.

| Case | Head `71ae5133` | Merge-base `b089b904` |
|---|---|---|
| A1 legit ISR `/_isr?x_astro_path=/one` + `x-vercel-isr: 1` → renders One | pass (200, One) | **fail (404)**: the regression the PR fixes |
| A2 unauth `/_isr?x_astro_path=/two` + `x-vercel-isr: 1` must NOT render Two | **fail (200, Two)** | pass (404) |
| A3 control, no header | pass (404) | pass (404) |
| B1 `_render` `/api/public?x_astro_path=/api/private` + header → public | **fail (`private`)** | pass (`public`) |
| B2 control, no header | pass | pass |
| Totals | exit 1, 5 s; 5 tests, 3 pass, 2 fail | exit 1, 5 s; 5 tests, 4 pass, 1 fail |

- **The security cases A2 and B1 flip from pass to fail.** The functional ISR case A1 flips from fail to pass. At the function boundary, a legitimate ISR rewrite (A1) and an attacker request (A2) cannot be told apart at the head.
- **Upstream tests:** `node --test test/path-override-security.test.js test/isr.test.js` exited 0 in 3 s at the head and exited 0 in 4 s at the merge-base, 4/4 passing each time. No existing test covers the `x-vercel-isr` branch, which is why CI stayed green.
- **Tree:** `git status --porcelain` was empty after all runs. The clone is left at the merge-base, built.
- **Logs:** `work/{build,probe,upstream}-{head,base}.log`.

## Not ground truth

1. **`JSON.parse(astroLocalsHeader)` on a request header** (head lines 40–46). Pre-existing and unchanged. It is reached only after `hasValidMiddlewareSecret`, and otherwise returns 403.
2. **Non-constant-time `middlewareSecretHeader === middlewareSecret`** (line 20). Pre-existing since #15959 and unchanged. It is a speculative timing side channel over the network with no demonstration.
3. **`let realPath = undefined` instead of `null`, the missing semicolon, and `if(` spacing.** Style only. `typeof realPath === 'string'` gates the rewrite correctly, and the post-merge "[ci] format" commit `66830865d3` reformatted it.
4. **`new Request(..., { body: request.body })` without `duplex: 'half'`.** Pre-existing: the merge-base has the identical lines. It is a functional bug for streamed bodies, fixed later by #16486 (`0bae1a51f0`), and is not introduced here.
5. **Case sensitivity of `'x-vercel-isr'`.** `Headers.get` is case-insensitive, so there is no miss and no bypass through casing. The flaw is trusting the header at all, which is GT-o1.
6. **"No tests were added."** True: the PR body says so. On its own it is a test-coverage observation (non-material). It becomes a recovery only if it names the unauthenticated override.
7. **"`x_astro_path` leaks into `Astro.url.searchParams` / user code."** True at the head. The upstream fix later deletes the params, but that behaviour predates #15959 and has no demonstrated consequence. Non-material.
8. **"Unvalidated path value, so path traversal or open redirect."** `url.pathname = value` percent-encodes `?` and `#` and cannot change the origin. The only real consequence is choosing any app route, which is GT-o1. Standalone traversal or redirect claims are unsupported.
9. **ISR cache poisoning of legitimate routes.** Not demonstrated. `allowQuery: ['x_astro_path']` keys the cache by the path, and an attacker-triggered render of an ISR route produces the same output a legitimate request would. Unsupported as a separate defect.
10. **"State-changing POST/PUT/DELETE bypass."** Per GHSA-x27w, Vercel serves ISR functions for GET only (403 otherwise), and bodied requests hit the pre-existing `duplex` error. An item with the right mechanism still recovers GT-o1. A write or integrity impact asserted as demonstrated is an overstated consequence: it is not supported for the `/_isr` vector, and it is unresolved for a client-sent header on `_render`.
11. **"The PR fails to fix the 404" or "ISR still breaks".** Contradicted. Probe A1 passes at the head and fails at the merge-base. Users (leifmarcus) and the maintainer accepted the fix.
12. **`middlewareSecret` embedded in route config (upstream's fix design).** This is not in this PR, so it is not reviewable here.
13. **Edge middleware not running for ISR routes** (later fixed by #17687). A separate pre-existing adapter behaviour, not introduced by this diff.

## Preexisting hints

These are items in the review record up to 2026-03-25T16:40:00Z:

- **PR body (author).** "[This PR](…/pull/15959) introduced a bug with the vercel adaptor which made any route served by ISR result in a 404. This is due to an intricacy with how vercel ISR works, in that we need to change the request path when serving an ISR path." This points at the surface: it links the security PR whose guarantee is being relaxed. It does not raise the security implication.
- **changeset-bot** (12:02Z): boilerplate.
- **Princesseuh:** APPROVED with an empty body at 12:19:44Z. Later, "Tomorrow most likely, with the rest of 6.1." (16:22Z).
- **leifmarcus** (16:09Z): "When can we expect this to be released? This currently blocks our upgrade to Astro 6…"
- No inline review threads. **No participant gestured at the defect.** The post-cutoff "Thanks a lot!" (17:12Z) is correctly omitted.
- **Adjacent pre-cutoff public context** (outside the packet, linked from the body):
  - On #15959, gkurt wrote (2026-03-21): "I think this might have caused a regression as I am getting `404: Not found Path: /_isr`".
  - On #15959, ematipico left an inline changeset comment: "I really don't understand what the fix is about…".
  - GHSA-mr6q (published 2026-03-24) says: "ISR is not affected. Vercel's cache layer appears to intercept before the function runs." This line could mislead a reviewer toward dismissing the ISR vector.

## Leakage

**Commits a truncated mirror must exclude.** Truncating at the merge-base `b089b904`, with the head `71ae5133` added as the only extra commit, excludes all of them.

- Merge commit `aa266364fe9e105317b66e218fe04567307fb57f` and its parent chain beyond the merge-base, including `5958ab97d4`, `2c1ae859d9` and `be661fb9fd`. These are harmless but post-base.
- `66830865d3` ("[ci] format", which reformats these lines).
- The fix `3a43cf0f3690a8e33cb30109bc5165611cf38fcd` (#17370) and its PR head `b6eb4d1a3c9d1ba05d7e86fc193c9d3ef6c02e3c`. The fix adds a regression test in `test/isr.test.ts`.
- Later commits touching `vercel/src/serverless/entrypoint.ts` and `vercel/src/index.ts`:
  - `0bae1a51f0` (#16486)
  - `5557dcabbf` (#15719)
  - `d1bb7fa005` (#17569)
  - `ce9f1da486` (#17680)
  - `0a22ff5b7e` (#17687)
  - `98c07e1735` (#18044)
  - `a09b3288d5` (#18008)
- Release tags `@astrojs/vercel@10.0.3` and later, and their `[ci] release` commits.
- The PR has no commits after the reviewed head.

**Answer-revealing records.**

- GHSA-x27w-589x-frm2 / CVE-2026-73424.
- PR #17370 and its changeset `.changeset/modern-otters-smoke.md`.
- The `@astrojs/vercel@11.0.3` release notes.
- NVD and other mirrors of CVE-2026-73424.

**Correction to the vetting pass.** GHSA-mr6q-rp88-fx84 / CVE-2026-33768 was published **2026-03-24T18:12:25Z** (updated 2026-03-25T04:45:26Z). That is **before** the cutoff, not "2026-03-26 / after the cutoff".

- It does not mention #16079. It says ISR is "not affected".
- It is pre-review public context of the same status as #15959, so it need not be hidden.
- Hiding it is optional. It is no more revealing than #15959's changeset and test, which are in the tree.

**Keep visible.** #15959, its changeset `short-cycles-fail.md`, and `path-override-security.test.js`. These are the contract.

## Confidence and limits

- **High** that GT-o1 is a material defect introduced by this diff. Evidence:
  - The code has an 8-line diff.
  - Probe cases A2 and B1 flip between the merge-base and the head.
  - A maintainer-published advisory names this PR and the mechanism.
  - The upstream fix changes exactly this branch.
- **Corrections to the vetting proposal:**
  - GHSA-x27w was published 2026-07-17T12:36:38Z, not 2026-07-20. Its CVE id is CVE-2026-73424.
  - GHSA-mr6q was published before the cutoff (see Leakage).
  - Everything else I checked held: SHAs, the review record, the numstat, the licence, the fix commit and PR head, the later commit list, and the release tags (`aa266364` first appears in `@astrojs/vercel@10.0.3`, `3a43cf0f` in `11.0.3`).
- **Unresolved: Vercel platform behaviour.**
  - That Vercel sets `x-vercel-isr: 1` on direct external `/_isr` requests, and serves ISR functions for GET only, rests on the advisory. I did not verify it on a live deployment.
  - Whether a client-supplied `x-vercel-isr` header reaches non-ISR functions is also unverified.
  - Neither question changes the ruling: `/_isr` is publicly addressable, and a request header is not an authorization boundary.
- **Not reproduced end to end on Vercel.** I did not reproduce the edge/firewall bypass on Vercel. The reproduction calls the built handlers in-process.
- **Training-data exposure.** The merge date of 2026-03-25 and the July advisory may be in reviewers' training data.
- **Slot fit.** This is an authorization defect (CWE-862 / confused deputy) in a web framework's server entrypoint. The slot label "authorization or injection" fits.
