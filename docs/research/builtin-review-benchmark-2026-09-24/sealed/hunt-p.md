# Hunt (p): released-compatibility break in a public API or SDK — buggy

Started 2026-09-24. Single-threaded; search API paced.

## 1. Inventory (in order examined)

| # | Repo | PR | Merged | Lines / files | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 | E10 | Notes |
|---|------|----|--------|---------------|----|----|----|----|----|----|----|----|----|-----|-------|
| 1 | webpack/minimizer-webpack-plugin | (via webpack/webpack#22288) | 2026-09 | not measured | – | – | not checked | not checked | – | – | – | – | fail: issue fixed same day by ccb722d468 (#748), but the introducing change is unclear and the plugin is under daily AI-assisted churn; the break is in how a sibling package passes `as` to minimizers, not a released export/signature | – | Glanced and dropped |
| 2 | conda/conda | (via conda/conda#16726) | 2026-09 | not measured | – | – | – | – | – | – | – | **fail**: the removal of `CondaPreCommand`/`CondaRequestHeader` from `conda.plugins` was a planned deprecation removal ("compatible with the plugin API removals in conda 26.9", jezdez), reported on a canary build | – | – | Glanced and dropped |
| 3 | tornadoweb/tornado | #3719 "Release 6.5.9" (introduced `allowed_symlink_directory`, commit 437ab5f765 / master f9f50b8bab) | 2026-09-14 | 1371+/52− in 18 files (GitHub API) | pass | pass | **fail** (18 files, 1423 lines) | not checked | fail: 0 reviews, 0 comments; the security commit was never reviewed in its own PR | – | – | pass (AttributeError in subclasses overriding `initialize()` was unintended) | pass (tornado#3724, fix #3725 dde5765, 6.5.10) | pass (Apache-2.0) | A textbook break (Jupyter `FileFindHandler` → `AttributeError: ... no attribute 'allowed_symlink_directory'`), but it shipped in an unreviewed 18-file release-batch PR; neither #3725 (the fix) nor #3729 (port to master) is the introducing PR |
| 4 | toss/es-toolkit | #1615 (via issue #1931) | 2026 (v1.49) | not measured | – | – | – | – | – | – | – | **fail**: throwing on multi-character `chars` was the PR's stated intent; the complaint is about semver labelling | – | – | Glanced and dropped |
| 5 | pallets/click | #3641 "Streamline option flag management" | 2026-07-16 | 234+/160− in 2 files (GitHub API) | pass | pass | pass (394 lines, per API) | not checked | pass | – | pass (`Option.default` of a boolean flag becomes `UNSET` instead of `False`; see pip-tools#2472) | pass ("I did not break any") | **fail**: the only report is jazzband/pip-tools#2472 (user mnencia, 2026-09-02, 0 comments). No click maintainer has acknowledged it, and stable has no fix, shim or revert (stable commits since 8.5.0 checked through 2026-09-21) | pass (BSD-3-Clause) | Closest miss so far. Re-check later if click ships 8.5.1 with a default shim |
| 6 | firebase/firebase-functions | #1955 "feat: unify global manifest on globalThis…" | 2026-09-03 | 291+/84− in 8 files (API) | pass | pass | pass (API) | not checked | pass (15 reviews) | – | pass (legacy `Symbol.for("firebase-functions:params:declaredParams:v${major}")` no longer written or read) | pass | **fail (partial)**: maintainer fix #1957 (ajperel, 2026-09-08) restores compatibility, but the break shipped only in pre-release `v7.3.3-rc.0` (2026-09-03), and no user report of a release exists. The fix landed before stable v7.4.0 (2026-09-15) | pass (MIT) | Closest miss on "released and user-reported" |
| 7 | Sage/carbon | #8116 "feat(textarea): remove legacy FormField, Label and Input usage" (reverted by #8174: "introduced breaking API and behavioural changes") | 2026-09-10 | 443+/167− in 17 files (API) | pass | pass | **fail** (17 files, 610 lines) | not checked | – | – | – | – | – | – | UI component library |
| 8 | pyathena-dev/PyAthena | #733 "Centralize shared execute() kwargs into an ExecuteOptions dataclass" (reports: PyAthena#734, dbt-labs/dbt-adapters#2052; shim #735 in v3.35.1) | 2026-07-07 | 706+/154− in 24 files (API) | pass | pass | **fail** (24 files, 860 lines) | not checked | fail (0 reviews, 0 comments) | – | – | **fail**: the PR body announced the private `_execute()` signature change | pass | pass (MIT) | A real released break with a maintainer shim, but too big, unreviewed and announced |
| 9 | TanStack/query | (via issue #11244, 5.100.13 `NoInfer`) | 2026-08 | not measured | – | – | – | – | – | – | – | – | **fail**: the reporter withdrew it as an editor using TypeScript 5.3. Maintainer TkDodo: "this code looks fine in a typescript playground". No fix | – | Glanced and dropped |
| 10 | nodejs/undici | (via issue #5486, `addAbortListener` in 8.4.0) | 2026-06/07 | not measured | – | – | – | – | – | – | – | – | **fail**: fails only under Jest 29's vm realm, which lacks `Symbol.dispose`. mcollina: "Supporting Jest is a lost battle". Closed with no fix | – | Glanced and dropped |
| 11 | honojs/hono | #5071 "fix: avoid circular dependency between body.ts and request.ts" (the PR user report #5129 blamed) | 2026-07-03 | 6+/4− in 1 file (numstat) | pass | pass | pass | not run | pass | – | **fail**: not the introducing change. At #5071's base (b20d4225), `parseFormData` already calls `arrayBuffer()`. `git diff v4.12.27 v4.12.28` and `git log` show the switch arrived in #5067 (b20d4225), which is candidate 12 | – | – | pass (MIT) | Misattribution in the user report; followed through to #5067 |
| 12 | **honojs/hono** | **#5067** "fix(utils/body,validator): normalize Content-Type media type for case-insensitive matching" | 2026-07-01T09:42:27Z | 107+/18− in 6 files (numstat: 125 lines) | pass | pass (preferred window; confirmed 2026-07-17) | pass | **pass**: exit 0 at default cutoff 2026-07-01T09:42:27Z; omitted 0/0/0/0 | pass (GitHub-native; 0 human reviews; 2 bot comments) | pass (bun install 12 s; repro 0.2 s; vitest 1 s) | pass (diff + one hop to `HonoRequest.#cachedBody` in src/request.ts) | pass (PR promised only case-insensitive media-type matching) | pass (user report #5129; maintainer yusukebe (MEMBER): "This is a bug. I'll fix it."; fix #5131 80959d47 with regression test, shipped in 4.12.31) | pass (MIT, 32k stars) | **Recommended**. Shipped in 4.12.28 (npm 2026-07-06) |
| 13 | nodejs/undici | #5367 "fix(mock): emit request body lifecycle hooks" (report #5649; fix #5650 by mcollina: "Regression introduced in #5367.") | 2026-08-03 | 789+/23− in 2 files (API) | pass | pass | **fail** (812 lines) | not checked | pass | – | – | pass | pass | pass (MIT) | Good confirmation (MockAgent `.reply(cb)` + `.persist()` replays the first response in 8.10.0), but too large |
| 14 | **immerjs/immer** | **#1259** "fix: prevent prototype pollution via constructor.prototype access" | 2026-07-01T10:53:23Z | 140+/1− in 3 files (numstat: 141 lines) | pass | pass (preferred window; revert 2026-07-16) | pass | **pass**: exit 0 at default cutoff 2026-07-01T10:53:23Z; omitted conversation 2 (post-merge release bot, mweststrate 2026-08-19), others 0 | pass (GitHub-native; 0 reviews; 1 pre-cutoff bot comment) | pass (yarn install 37 s; repro 0.25 s; vitest base.js 1–2 s) | pass (all in the diff: the `prototype` get trap breaks a Proxy invariant; a fresh wrapper per access breaks identity) | pass (PR promised `.prototype` "returns frozen empty object" and `draft.arr.constructor(5)` "still works"; the crash and identity loss were not promised) | pass (user reports #1265, #1266, #1268 on 11.1.9–11.1.11; maintainer revert #1271 4d3d6ff8 "This fixes #1266 and #1268, #1265"; shipped in 11.1.12) | pass (MIT, 29k stars) | **Alternate** |

Search notes: GitHub issue, PR and commit searches were run for "backward(s) compatibility", "no longer exported", "breaking change", "backwards incompatible", "restore backwards compatibility" (commits), `label:regression`, and batched `repo:` searches for "regression" across about 55 popular Python and JavaScript libraries, all dated 2026-07-01 or later. Every search was paced; there were no rate-limit hits. Leads glanced at and dropped without a row (intentional, unreleased, or not a library): eclipse.platform.ui#4262 (planned API move), jupyterlab#19767 (the tornado break in row 3), pytest#15099 (#14969 not released yet), pytest#14964 (collection bug, not an API break), click#3473 / typer argument help (merged 2026-05-28, and no click-side fix for Typer).

## 2. Recommendation

**Primary: honojs/hono#5067** (row 12). **Alternate: immerjs/immer#1259** (row 14). Both merged on or after 2026-07-01 (preferred window), so no fallback to the 2025-10-01 window was needed.

---

### 2.1 Primary: honojs/hono#5067

- **Repository / PR:** honojs/hono#5067, "fix(utils/body,validator): normalize Content-Type media type for case-insensitive matching"
- **Author:** yusukebe (Yusuke Wada, the Hono lead maintainer). **Merged:** 2026-07-01T09:42:27Z (squash, as b20d4225c9aa9e615717ca74e437852cc9fd5b94). **Base branch:** main. **Licence:** MIT.
- **Head SHA:** 5226d4165d48643586152614cbd07422a0ab7a22 (a single commit). **PR-recorded base SHA:** 9728702911073aec5a63a3ba2840b7240e5d3205. **`git merge-base` on a full clone** (`git clone https://github.com/honojs/hono.git`, not shallow, 2832 commits; head fetched from `refs/pull/5067/head`): 9728702911073aec5a63a3ba2840b7240e5d3205. **They agree.**
- **Changed-file manifest** (`git diff --numstat 9728702 5226d41`; 125 lines, 6 files):

  | File | + | − |
  |---|---|---|
  | src/utils/body.test.ts | 28 | 9 |
  | src/utils/body.ts | 12 | 5 |
  | src/utils/buffer.test.ts | 14 | 0 |
  | src/utils/buffer.ts | 2 | 1 |
  | src/validator/validator.test.ts | 48 | 0 |
  | src/validator/validator.ts | 3 | 3 |

- **Originating issue:** honojs/hono#5060, "parseBody and validator skip mixed-case Content-Type media types" (MicroMilo). It asks only for case-insensitive media-type matching in `parseBody()` and `validator()`.
- **Prior review record up to the merge instant:** no reviews and no review threads. There are two conversation comments, both from bots: `github-actions` (HTTP benchmark table, 2026-07-01T09:41:13Z) and `codecov` (patch coverage 76.47%, "4 lines in your changes missing coverage", 09:41:59Z). **Nobody raised the defect.** The PR was merged about three minutes after creation.

**The defect**

- **Where (at head 5226d41):** `src/utils/body.ts`, `parseFormData()` (lines ~121–133). The previous `const formData = await (request as Request).formData()` became:
  ```ts
  const headers = request instanceof HonoRequest ? request.raw.headers : request.headers
  const arrayBuffer = await (request as Request).arrayBuffer()
  const formDataPromise = bufferToFormData(arrayBuffer, headers.get('Content-Type') || '')
  if (request instanceof HonoRequest) { request.bodyCache.formData = formDataPromise as unknown as FormData }
  ```
  One hop away, in `src/request.ts`: `HonoRequest.arrayBuffer()` → `#cachedBody('arrayBuffer')` (lines 220–239). When a *different* body type is already cached, it rebuilds the body with `return new Response(body)[key]()`. So when `c.req.formData()` ran first, `parseBody()` re-serializes the cached `FormData` as multipart with a **new, random boundary**. It then parses those bytes against the **original** `Content-Type`, whose boundary is the old one (and, for urlencoded requests, whose media type no longer matches a multipart body). It also overwrites `bodyCache.formData` with the resulting (rejected or garbled) promise.
- **Released contract it broke:** from 4.12.27 back, `c.req.parseBody()` after `c.req.formData()` returned the parsed form. `parseBody` went through `formData()` → `#cachedBody('formData')`, which returns the cached value. The repository's own suite at the merge-base states the cross-method caching contract: `src/request.test.ts:245`, `describe('Body methods with caching', …)` (each test reads the body one way, then again through the other methods). The mirror case was accepted as a bug and fixed before: #4806 "parseBody() breaks subsequent text()/json() calls with TypeError", fixed by yusukebe in #4807 (2026-03-21). The public JSDoc (`src/request.ts:201`): "`.parseBody()` can parse Request body of type `multipart/form-data` or `application/x-www-form-urlencoded`".
- **Release that shipped it:** 4.12.28 (npm publish 2026-07-06T10:07:44Z; `git tag --contains b20d4225` → v4.12.28), then 4.12.29 and 4.12.30. Fixed in 4.12.31 (npm 2026-07-18T23:16:05Z).
- **Concrete caller that breaks:** middleware reads the form, then the handler parses it (from #5129):
  ```ts
  app.post('/upload', async (c) => { await c.req.formData(); const body = await c.req.parseBody(); … })
  ```
- **Demonstrated consequence** (I ran it; see below): for a multipart request, `parseBody()` rejects with `TypeError: Failed to parse body as FormData.` (cause: `no boundary found in multipart body`), and the request becomes a **500**. For a urlencoded request it returns 200 but **silently drops the fields** (`{"gotFile":false}` with no `foo`). At the merge-base both return `{"foo":"bar",…}`.
- **Confirming upstream record:**
  - User report honojs/hono#5129 (marcovietovega, 2026-07-17T15:07:49Z), "parseBody() fails with "Failed to parse body as FormData" when formData() was read first (regression in 4.12.28)": "hono 4.12.27: `200 {"gotFile":true}` / hono 4.12.28 / 4.12.29 / 4.12.30: `500`, with `parseBody()` rejecting with `Failed to parse body as FormData.`" and "`parseBody()` -> `parseFormData()` in `src/utils/body.ts` now calls `request.arrayBuffer()` instead of `request.formData()`". The reporter blamed #5071. That is a misattribution: #5071 only swapped `instanceof` for a type guard, and `git diff v4.12.27 v4.12.28` plus `git log` place the `arrayBuffer()` switch in b20d4225 (#5067). See row 11.
  - Maintainer yusukebe (MEMBER), 2026-07-17T23:04:02Z: **"@marcovietovega Thank you for the report! This is a bug. I'll fix it."**
  - Fix honojs/hono#5131, "fix(utils/body): reuse cached formData in `parseBody()`", commit **80959d47d56ac18c2985336ad311917dc56497c5** (merged 2026-07-17T23:26:28Z, "Fixes #5129"). It adds the regression test `it('should parse form data even if formData() is called before parseBody()', …)` in `src/request.test.ts`. First tag: v4.12.31.
- **Corrective outcome any sufficient fix must restore:** when a `HonoRequest` body has already been read and cached as `FormData`, `parseBody()` must return the same fields and files as a first read, for both multipart and urlencoded bodies. It must not reparse re-serialized bytes against the original `Content-Type` boundary, and it must not replace the cached `FormData` with a failing one. The case-insensitive media-type handling the PR added must keep working.

**Tempting false positives**

1. *"`bufferToFormData` lowercases the Content-Type and corrupts the case-sensitive multipart boundary."* Wrong: `contentType.replace(/^[^;]+/, m => m.toLowerCase())` touches only the media type before the first `;`. The `boundary=` value is preserved.
2. *"Adding `/i` to `multipartRegex`/`jsonRegex`/`urlencodedRegex` over-accepts headers."* The only newly accepted input is mixed-case media types and parameter names, which RFC 9110 defines as case-insensitive. This is the PR's stated goal.
3. *"Storing a Promise in `bodyCache.formData` (typed `FormData`) breaks `c.req.formData()`."* `#cachedBody` returns the cached value and callers await it. The other cache entries are promises too (`raw[key]()`), so a later `formData()` resolves correctly in the first-read case.
4. *"Reading `arrayBuffer()` instead of `formData()` doubles memory or breaks streaming."* `Request.formData()` also buffers the whole body. On a first read the raw body is consumed exactly once, as before.
5. *"`contentType` may be `null`, and `.split` throws."* It is guarded by `contentType?.split(…)`, and `mediaType` then falls through to the `{}` path as before.

**Leak set**

- SHAs to exclude: b20d4225c9aa9e615717ca74e437852cc9fd5b94 (squash merge of #5067); 82b321b5b0e7a57cdaab45f2f90671ec0737795b (#5071, the misattributed follow-up on the same lines); **80959d47d56ac18c2985336ad311917dc56497c5** (#5131 fix plus regression test); d7964503c956ae4af78597b7b11a05f9e5e73d2d (#5133, companion clone fix from the same report); edd138ee (#5366, a related cached-body media-type fix); fc8bd834 (#5176), 612b59c0 (#5282), c409d855 (#5288), 531e9c5a (2026-08-26 security merge touching body.ts). Also the release commits and tags v4.12.28 and later. The PR head 5226d41 is the only PR-branch commit.
- Issues and PRs that give it away: #5129 (report plus comments), #5131, #5133, #5071 (its thread postdates the merge), #5365/#5366 (the same bug class).

**Provisioning and test evidence I ran** (clone `scratch/hono`, Node v24.21.0, bun 1.3.10)

| Step | Rev | Command | Exit | Time | Output |
|---|---|---|---|---|---|
| provision | 5226d41 | `bun install --frozen-lockfile --ignore-scripts` (the PR-era `packageManager` is bun; `bun.lock` is identical at base and head) | 0 | 12 s | 747 packages |
| repro | head 5226d41 | `esbuild ../repro-hono.ts --bundle --platform=node --format=esm` then `node repro-hono.mjs` (a script outside the tree; `app.request` with `formData()` then `parseBody()`) | **1** | 0.18 s | `multipart: 500 Internal Server Error` (TypeError "Failed to parse body as FormData." / "no boundary found in multipart body"); `urlencoded: 200 {"gotFile":false}` (the `foo` field is lost) |
| repro | merge-base 9728702 | same | **0** | 0.17 s | `multipart: 200 {"foo":"bar","gotFile":true}`; `urlencoded: 200 {"foo":"bar","gotFile":false}` |
| repro | fix 80959d47 | same | 0 | <1 s | same as the merge-base |
| suite | head | `vitest --run --project main src/utils/body.test.ts src/request.test.ts src/utils/buffer.test.ts src/validator/validator.test.ts` | 0 | 1 s | 144 passed, 1 skipped (the existing suite does **not** catch the defect) |
| suite | merge-base | same | 0 | 1 s | 138 passed, 1 skipped |

`git status --porcelain` stayed empty after every step (node_modules is gitignored; scripts live in `scratch/`).

**E4:** `build_packet.py --repo honojs/hono --pr 5067 --head 5226d41… --merge-base 9728702… --base-sha 9728702… --staging scratch/hono --target p --out scratch/packet-5067.md` → **exit 0**, cutoff **2026-07-01T09:42:27Z** (default), omitted after cutoff `{'reviews': 0, 'thread_comments': 0, 'conversation': 0, 'issue_comments': 0}`. It wrote 6 files, 1 commit, 0 reviews, 0 thread comments, 2 conversation comments and 1 issue.

**Confidence: high.** The report, the maintainer's confirmation, the fix with its regression test, and my own head/base/fix repro agree. Caveats: (a) the user report names the wrong PR (#5071); the maintainer never named #5067, and the attribution to #5067 is mine, from `git diff v4.12.27 v4.12.28` and the #5071 base already containing `arrayBuffer()`. (b) The PR had no human review, so the prior-review record is empty. (c) The contract is established by prior behaviour, tests and the #4806/#4807 precedent, not by a sentence in the docs.

---

### 2.2 Alternate: immerjs/immer#1259

- **Repository / PR:** immerjs/immer#1259, "fix: prevent prototype pollution via constructor.prototype access (CVE-2026-XXXX)"
- **Author:** mweststrate (Michel Weststrate, the Immer author). **Merged:** 2026-07-01T10:53:23Z (squash, as 48fc3788609ce46dd789c313768bae4f48b00ec5). **Base branch:** main. **Licence:** MIT.
- **Head SHA:** bd0970b8e638a991658fa7e66a6430eea46f3293 (single commit). **PR-recorded base SHA:** bf2d15439259887f98f2737cf7ebde4234d5adea. **`git merge-base` on a full clone** (not shallow): bf2d15439259887f98f2737cf7ebde4234d5adea. **They agree.**
- **Changed-file manifest** (numstat; 141 lines, 3 files): `.vscode/settings.json` +4/−1; `__tests__/base.js` +92/−0; `src/core/proxy.ts` +44/−0.
- **Originating issue:** none linked. The body is a self-written vulnerability analysis claiming a bypass of CVE-2021-23436.
- **Prior review record up to the merge instant:** no reviews and no threads. There is one pre-cutoff conversation comment, from `coveralls` (coverage +0.4%). Nobody raised the defect. The PR was merged 2 min 27 s after creation. After the cutoff: the semantic-release bot ("included in version 11.1.9") and mweststrate on 2026-08-19 (a link explaining why hardening against prototype pollution is not viable). The packet omits both.

**The defect**

- **Where (head bd0970b):** `src/core/proxy.ts`, `objectTraps.get` (new lines ~113–137). For `prop === "constructor" || "__proto__"`, the draft returns `new Proxy(value || {}, { get: (t, key) => key === "__proto__" || key === "prototype" ? Object.freeze(Object.create(null)) : Reflect.get(t, key), set: () => true, apply: … })`. This has three consequences:
  1. `draft.x.constructor.prototype` breaks a Proxy invariant. `Object.prototype` (like any function's `prototype`) is a non-writable, non-configurable data property of the target, so returning a fresh object makes the engine throw `TypeError: 'get' on proxy: property 'prototype' is a read-only and non-configurable data property…`. The PR promised that access "returns frozen empty object".
  2. Every read of `draft.constructor` allocates a new wrapper, so `draft.a.constructor === Object` and `draft.a.constructor === draft.b.constructor` are false.
  3. A *data* key named `constructor` is also intercepted: `new Proxy("x", …)` throws `Cannot create proxy with a non-object as target`.
- **Released contract it broke:** in 11.1.8 and earlier, drafts behave like the plain objects and arrays they stand for; property reads return `latest(state)[prop]`. The PR itself states the intended contract: "Allows constructor calls: draft.arr.constructor(5) still works", and `.prototype` access "returns frozen empty object". Ecosystem callers depend on `value.constructor === Object` and `value.constructor.prototype` (lodash `isEmpty`/`isPlainObject`/`isEqual`, fast-deep-equal).
- **Release that shipped it:** 11.1.9 (npm 2026-07-01T10:54:26Z), then 11.1.10 and 11.1.11. Reverted in 11.1.12 (npm 2026-07-16T18:30:44Z).
- **Concrete caller that breaks:** a Redux Toolkit reducer calling `_.isEmpty(draft)` or `_.isEqual(draft, …)` (#1265, #1268), or `fast-deep-equal(draft.a, draft.b)` (#1266).
- **Demonstrated consequence** (I ran it): at head, 6 of 6 checks fail, including a `TypeError` on `draft.constructor.prototype`, `draft.a.constructor === Object → false`, and a `TypeError` reading a data key named `constructor`. At the merge-base and at the revert, 6 of 6 pass.
- **Confirming upstream record:**
  - #1265 (dwiyatci, 2026-07-07): "We're upgrading from v11.1.7 to v11.1.11, and got the aforementioned error … TypeError: 'get' on proxy: property 'prototype' is a read-only and non-configurable data property on the proxy target but the proxy did not return its actual value".
  - #1266 (olemartinorg, 2026-07-09): "`immer@11.1.9` regresses the identity of `draft.constructor` after the CVE fix … the implementation now returns a fresh wrapper on each access".
  - #1268 (jonatankruszewski, 2026-07-09): "Since **11.1.9** … reading `constructor` on a draft returns a wrapper `Proxy` whose `prototype` read returns a fabricated value. Because a function's `prototype` is a non-configurable, non-writable data property, returning anything else violates a Proxy invariant and throws".
  - Maintainer revert #1271 by mweststrate, commit **4d3d6ff88caa85734a802a91cdb3dbe004d88b17** (2026-07-16): "This reverts commit 48fc3788609ce46dd789c313768bae4f48b00ec5. **This fixes #1266 and #1268, #1265**". On #1265, mweststrate (COLLABORATOR): "Should be fixed I think by 11.1.12."
- **Corrective outcome:** reading `constructor` on a draft must return the real constructor again (stable identity, `=== Object` for plain objects). Reading `.prototype` through it must not throw. Data keys named `constructor` must read and write like any other key. Any remaining pollution guard must not break a Proxy invariant.

**Tempting false positives**

1. *"`__proto__` returning a frozen object also breaks a Proxy invariant."* No. On the wrapped constructor function, `__proto__` is an inherited accessor, not an own non-configurable data property, so no invariant applies. Only `prototype` throws.
2. *"`new draft.constructor()` is broken because there is no `construct` trap."* Without a `construct` trap the Proxy forwards `[[Construct]]` to the target, so it works.
3. *"The `.vscode/settings.json` edit ships to users."* It is editor configuration, not in the npm package, and has no runtime effect.
4. *"The `has` trap returning false and silent `set` are the bug."* The PR announced both ("HAS TRAP - Returns false", "SET TRAP - Blocks assignment"). They were intended, and the upstream reports centre on the crash and the identity loss.
5. *"A Proxy allocation per property read is a performance regression."* True in principle, but it is not the reported or fixed defect.

**Leak set:** 48fc3788609ce46dd789c313768bae4f48b00ec5 (merge); 4d3d6ff88caa85734a802a91cdb3dbe004d88b17 (revert #1271); later proxy.ts and base.js commits a73672ab, e3df956d, 0c3efdd4, 0f158b3d, 9491138b; tags v11.1.9 and later. Issues and PRs: #1265, #1266, #1268, #1267 and #1269 (closed alternative fixes), #1271. Also the adventures.nodeland.dev link in mweststrate's post-cutoff comment.

**Provisioning and test evidence I ran** (clone `scratch/immer`, Node v24.21.0)

| Step | Rev | Command | Exit | Time | Output |
|---|---|---|---|---|---|
| provision | bd0970b | `npx -y yarn@1.22.22 install --frozen-lockfile --ignore-scripts --non-interactive` | 0 | 37 s | "Done in 35.82s" |
| repro | head bd0970b | `esbuild ../repro-immer.ts --bundle --platform=node` then `node repro-immer.mjs` | **1** | 0.24 s | 6 of 6 FAIL: identity false ×2; `.prototype` TypeError (Proxy invariant); `"constructor" in draft` false; data-key read TypeError "Cannot create proxy with a non-object"; data-key write ignored |
| repro | merge-base bf2d154 | same | **0** | 0.24 s | 6 of 6 ok |
| repro | revert 4d3d6ff | same | 0 | 0.23 s | 6 of 6 ok |
| suite | head | `vitest run __tests__/base.js` | 0 | 2 s | 3224 passed (the existing suite does not catch it) |
| suite | merge-base | same | 0 | 1 s | 3197 passed |

The tracked tree stayed clean (`git status --porcelain` empty).

**E4:** `build_packet.py --repo immerjs/immer --pr 1259 --head bd0970b… --merge-base bf2d154… --base-sha bf2d154… --staging scratch/immer --target p --out scratch/packet-1259.md` → **exit 0**, cutoff **2026-07-01T10:53:23Z** (default), omitted `{'reviews': 0, 'thread_comments': 0, 'conversation': 2, 'issue_comments': 0}`. It wrote 3 files, 1 commit, 0 reviews and 1 conversation comment.

**Confidence: high on the facts, medium-high on slot fit.** There are three independent user reports on released versions, a maintainer revert naming them, and a deterministic repro. Caveats: (a) the PR is a security hardening whose *intended* behaviour (blocking prototype access) itself changes semantics, so a grader must score the unintended mechanisms (Proxy-invariant crash, identity loss, data-key crash) rather than "it blocks `.prototype`". (b) The revert also cites doubts about the vulnerability, not only the breakage. (c) The PR body reads as machine-written, though a maintainer wrote and merged it, and the confirmations are organic user reports.

## 3. Closest misses (for the curator)

- pallets/click#3641 (row 5): a real, statically visible change to `Option.default` for flags (`False` → `UNSET`) that broke pip-tools. It fails E9 only: there is no maintainer acknowledgement or fix yet.
- firebase/firebase-functions#1955 (row 6): a maintainer shim (#1957) exists, but the break shipped only in a pre-release and no user report exists.
- tornadoweb/tornado 6.5.9 (row 3), undici#5367 (row 13), PyAthena#733 (row 8): textbook confirmed breaks, but they fail E3 (size) and, for tornado and PyAthena, E5 (no review).
