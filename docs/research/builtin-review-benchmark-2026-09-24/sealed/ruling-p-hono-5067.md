# Ruling: p-hono-5067

## Target

- Repository / PR: `honojs/hono#5067`, "fix(utils/body,validator): normalize Content-Type media type for case-insensitive matching". Author yusukebe. Created 2026-07-01T09:39:48Z, merged 2026-07-01T09:42:27Z as squash `b20d4225c9aa9e615717ca74e437852cc9fd5b94`. Body: "Fixes #5060".
- Head `5226d4165d48643586152614cbd07422a0ab7a22` (single commit). Merge-base `9728702911073aec5a63a3ba2840b7240e5d3205`: `git merge-base 5226d41 9728702` on a clone of the full mirror returns `9728702…`, so it matches the PR-recorded base.
- Diff (`git diff --numstat 9728702 5226d41`): `src/utils/body.test.ts` +28/−9, `src/utils/body.ts` +12/−5, `src/utils/buffer.test.ts` +14/−0, `src/utils/buffer.ts` +2/−1, `src/validator/validator.test.ts` +48/−0, `src/validator/validator.ts` +3/−3.
- Stated goal (issue #5060, MicroMilo, 2026-06-30): "Supported media type matching should be case-insensitive for the media type portion. Parameter values such as multipart boundaries should remain intact."

## Verdict

1 material defect

## Defect register

### GT-p1: `parseBody()` after `formData()` re-parses re-serialized multipart bytes against the original Content-Type, so it fails (multipart) or garbles the fields (urlencoded), and it overwrites the good cached FormData

- **Where (head 5226d41):** `src/utils/body.ts`, `parseFormData()`, lines 121–139. The defect is at lines 124–132:
  ```ts
  const headers = request instanceof HonoRequest ? request.raw.headers : request.headers
  const arrayBuffer = await (request as Request).arrayBuffer()
  const formDataPromise = bufferToFormData(arrayBuffer, headers.get('Content-Type') || '')
  if (request instanceof HonoRequest) {
    // Cache so that a later `c.req.formData()` reuses the already-consumed body
    request.bodyCache.formData = formDataPromise as unknown as FormData
  }
  ```
  At the merge-base the same function called `await (request as Request).formData()` (`src/utils/body.ts:125` at 9728702). For a `HonoRequest` that call goes to `#cachedBody('formData')`, which returns an already cached `FormData` unchanged. The interacting code, unchanged by the PR, is `src/request.ts` `#cachedBody` (lines 220–239 at head). When a *different* key is cached it returns `new Response(body)[key]()` (line 234). With only `formData` cached, `c.req.arrayBuffer()` therefore re-serializes that `FormData` as a new multipart body with a new random boundary. `parseFormData` then parses those bytes with the request's **original** `Content-Type`: the old boundary for multipart, or `application/x-www-form-urlencoded` for urlencoded. It also stores the resulting failing or garbled promise in `bodyCache.formData`, replacing the valid cached `FormData`.
- **Expected behaviour / contract:**
  - Released behaviour up to v4.12.27: `parseBody()` after `formData()` returns the parsed form. `src/utils/body.ts`, `src/request.ts` and `src/utils/buffer.ts` are byte-identical between `v4.12.27` and the merge-base (`git diff --stat v4.12.27 9728702 -- …` is empty), and v4.12.27 is an ancestor of the base.
  - Public JSDoc, `src/request.ts:201`: "`.parseBody()` can parse Request body of type `multipart/form-data` or `application/x-www-form-urlencoded`".
  - The repository's cross-method caching contract: `src/request.test.ts:245` `describe('Body methods with caching', …)` at the base. The mirror-order failure was accepted as a bug in #4806 ("parseBody() breaks subsequent text()/json() calls with TypeError", closed) and fixed by `8bd9dddc` (#4807, 2026-03-21).
  - Maintainer ruling on this exact behaviour (#5129, yusukebe, MEMBER, 2026-07-17T23:04:02Z): "@marcovietovega Thank you for the report! This is a bug. I'll fix it."
- **Trigger:** a `HonoRequest` whose body was first read with `c.req.formData()` (for example an auth middleware that reads the form), then `c.req.parseBody()`, with `Content-Type` `multipart/form-data; boundary=…` or `application/x-www-form-urlencoded`. Nothing else may have been cached first: `arrayBuffer`, `text` and `blob` are not affected, and neither is `validator('form')`, because it caches `arrayBuffer` too.
- **Demonstrated consequence:**
  - Multipart: `parseBody()` rejects with `TypeError: Failed to parse body as FormData.` (cause `no boundary found in multipart body`). An `app.request` round-trip returns **500**.
  - Urlencoded: 200, but the body is one garbage key made of the multipart serialization (`{"------formdata-undici-…\r\nContent-Disposition: form-data; name":"\"foo\"\r\n\r\nbar…"}`), and `foo`/`baz` are missing. The data loss is silent.
  - Cache poisoning: after that `parseBody()` call, a later `c.req.formData()` returns the same failure (multipart) or the garbled keys (urlencoded).
  - At the merge-base all of these return the correct fields.
  - Downstream report #5129 (marcovietovega, 2026-07-17T15:07:49Z): "hono 4.12.27: `200 {"gotFile":true}` / hono 4.12.28 / 4.12.29 / 4.12.30: `500`".
  - Upstream fix `80959d47d56ac18c2985336ad311917dc56497c5` (#5131, "Fixes #5129") and its regression test `should parse form data even if formData() is called before parseBody()`. The test fails at head and passes at the base (see Reproduction).
- **Required corrective outcome:** when a `HonoRequest` body has already been read and cached as `FormData`, `parseBody()` must return the same fields and files as a first read, for both multipart and urlencoded bodies. It must not leave `bodyCache.formData` holding a failing or garbled value, so a later `formData()` still returns the original fields. The PR's case-insensitive media-type handling and the orders that already work at head (first read; `text()`/`arrayBuffer()`/`blob()`/`validator('form')` before `parseBody()`; `parseBody()` before `formData()`) must keep working. The upstream fix reuses the cached `FormData`. Any fix that restores the outcome is sufficient, for example rebuilding the Content-Type from the re-serialized body.
- **Promised behaviour or unintended?** Unintended. #5060/#5067 asked only for case-insensitive media-type matching. The added comment ("Cache so that a later `c.req.formData()` reuses the already-consumed body") shows the author considered the reverse order only.
- **Attribution (#5067, not #5071):** the reporter blamed #5071. `git log v4.12.27..v4.12.28 -- src/utils/body.ts` lists only `b20d4225` (#5067) and `82b321b5` (#5071). `git show 82b321b5` only changes `import { HonoRequest }` to `import type` and replaces `instanceof HonoRequest` with an `isRawRequest` type guard. The `formData()` → `arrayBuffer()` + `bufferToFormData` switch is in #5067, and the head repro already fails before #5071 exists. The attribution is therefore established from the code history. No maintainer named #5067 explicitly.
- **Released in:** v4.12.28 (npm 2026-07-06T10:07:44Z; `git tag --contains b20d4225` starts at v4.12.28), then 4.12.29 and 4.12.30. Fixed in v4.12.31 (npm 2026-07-18T23:16:05Z).
- **Manifestations (one defect, one corrective outcome):** (a) multipart, a thrown TypeError and a 500; (b) urlencoded, silent garbling and field loss; (c) `bodyCache.formData` overwritten, so a later `formData()` fails or is garbled.

## Reproduction

Environment: a clone of the full bare mirror at `work/hono`, Node v24.7.0, bun 1.3.10. `bun install --frozen-lockfile --ignore-scripts` at head: 747 packages, exit 0, 1.9 s. `git status --porcelain` was empty after every step. The scratch script lives outside the tree at `work/repro/repro.ts`. It is bundled with `hono/node_modules/.bin/esbuild repro/repro.ts --bundle --platform=node --format=esm --outfile=repro/out-<rev>.mjs` and run with `node repro/out-<rev>.mjs`. It exits 1 if `formData()`→`parseBody()` does not return `foo` for multipart or urlencoded.

| Rev | Command | Exit | Time | Key output |
|---|---|---|---|---|
| head 5226d41 | repro | **1** | 0.16 s | `/fd-then-pb multipart 500 ERR Failed to parse body as FormData. \| cause: no boundary found in multipart body`; `/fd-then-pb urlencoded 200 {"------formdata-undici-…Content-Disposition: form-data; name":"\"foo\"…"}`; `/fd-then-pb-then-fd multipart 500`, urlencoded keys garbled; every other case 200 with correct fields, mixed-case included |
| base 9728702 | repro | 0 | 0.27 s | `/fd-then-pb multipart 200 {"foo":"bar","file":"File(t.txt)"}`, urlencoded `{"foo":"bar","baz":"qux"}`. The base **fails** `text()`→`parseBody()` and `arrayBuffer()`→`parseBody()` (500 "Content-Type was not one of …"), and mixed-case urlencoded returns `{}` (the #5060 bug) |
| fix 80959d47 | repro | 0 | 0.15 s | every case correct |
| head | `npx vitest --run --project main src/utils/body.test.ts src/request.test.ts src/utils/buffer.test.ts src/validator/validator.test.ts` | 0 | 1.3 s | 144 passed, 1 skipped (the PR's own suite does not catch GT-p1) |
| base | same | 0 | 1.1 s | 138 passed, 1 skipped |
| head + the #5131 test hunk applied (`git show 80959d47 -- src/request.test.ts \| git apply`) | `npx vitest --run --project main src/request.test.ts -t 'is called before parseBody'` | **1** | 0.9 s | `FAIL … should parse form data even if formData() is called before parseBody()`: `TypeError: Failed to parse body as FormData.` Caused by `expected a value starting with -- and the boundary` |
| base + the same hunk | same | 0 | 0.9 s | 1 passed |

The defect is absent at the base and present at head: this change introduced it.

## Not ground truth

A correct review must not assert these as defects.

1. **"`bufferToFormData` lowercases the Content-Type and corrupts the case-sensitive boundary."** False. `contentType.replace(/^[^;]+/, m => m.toLowerCase())` changes only the text before the first `;`. The first-read multipart case parses correctly at head.
2. **"Adding `/i` to `jsonRegex`/`multipartRegex`/`urlencodedRegex` over-accepts."** The only new inputs accepted are case variants of media types and parameter names, which RFC 9110 defines as case-insensitive. That is the PR's stated goal.
3. **"Storing a Promise in `bodyCache.formData` (typed `FormData`) breaks later `formData()` or the validator."** Not in the first-read case: `#cachedBody` returns the cached value and callers await it, and the validator does `await c.req.bodyCache.formData`. The repro shows `parseBody()`→`formData()` at 200 with the right keys. The cast is type hygiene. The only harm from the stored promise arises in the GT-p1 order (manifestation c).
4. **"Reading `arrayBuffer()` instead of `formData()` doubles memory or breaks streaming."** `Request.formData()` also buffers the whole body, and on a first read the raw stream is consumed once, as before. No meaningful-performance consequence is demonstrated.
5. **"A null Content-Type makes `.split` throw."** It is guarded by `contentType?.split(…)`. `mediaType` is `undefined`, which falls through to `{}` as before.
6. **"`text()`/`arrayBuffer()`/`blob()` before `parseBody()` also regresses."** False. Head handles these correctly, because the cached bytes are identical to the original. The base failed `text()` and `arrayBuffer()` with 500 (see Reproduction). This is an incidental improvement.
7. **"`validator('form')` followed by `c.req.parseBody()` breaks."** False. The validator calls `c.req.arrayBuffer()` (caching `arrayBuffer`) before setting `bodyCache.formData`. `parseBody()` then gets the original bytes, and the repro returns 200 with the right fields for all three content types.
8. **"Exact media-type equality drops inputs `startsWith` accepted."** Only non-media-types such as `multipart/form-dataX` are now rejected. Surrounding whitespace is now trimmed. There is no compatibility consequence for any valid header.
9. **"The json regex's `[a-z-\.]+\+` suffix group now also matches uppercase."** That is intended case-insensitivity with no consequence.
10. **"`cloneRawRequest` produces a boundary mismatch after `formData()`."** True upstream, but pre-existing and not in this diff. The reporter says it reproduces on 4.12.27, `src/request.ts` is unchanged by this PR, and it was fixed separately in `d7964503` (#5133). It is not attributable to #5067.
11. **"`text()` then `formData()` throws."** Pre-existing (#5365, fixed in #5366 `edd138ee`). It lives in `src/request.ts` `#cachedBody`, which this PR does not touch.
12. **"Circular import between `body.ts` and `request.ts`."** The value import `import { HonoRequest } from '../request'` already existed at the base, and #5067 only adds uses of it. #5071 later changed it to a type import. This is hygiene, not a defect introduced here.
13. **"Codecov reports 76.47% patch coverage / 4 uncovered lines."** Test-coverage hygiene. Coverage alone is not a defect, although a finding that the missing coverage hides the GT-p1 order would count as a recovery of GT-p1.
14. **"An unhandled rejection leaks when `bufferToFormData` rejects."** The promise is awaited in the same call and the rejection propagates to the caller. No unhandled-rejection path exists in the parseBody-first case.
15. **"A raw `Request` (not `HonoRequest`) passed to `parseBody` now behaves differently."** It still consumes the body once. The only difference is that mixed-case media types now parse, which is intended.

## Preexisting hints

None. PR #5067 has 0 reviews and 0 review-thread comments (`gh api repos/honojs/hono/pulls/5067/comments` → 0). Its two conversation comments before the cutoff are bots:
- `github-actions` (2026-07-01T09:41:13Z): an HTTP benchmark table.
- `codecov` (2026-07-01T09:41:59Z): patch coverage, with "4 lines in your changes missing coverage". This does not name or gesture at the cached-body order or the boundary mismatch.

Issue #5060 (in the packet) discusses only case-insensitivity. Its line "Parameter values such as multipart boundaries should remain intact" gestures at tempting surface 1, not at GT-p1.

## Leakage

A truncated mirror must exclude these commits:
- `b20d4225c9aa9e615717ca74e437852cc9fd5b94`: squash merge of #5067.
- `82b321b5b0e7a57cdaab45f2f90671ec0737795b`: #5071, a follow-up edit on the same lines.
- `80959d47d56ac18c2985336ad311917dc56497c5`: #5131, the fix plus its regression test.
- `d7964503c956ae4af78597b7b11a05f9e5e73d2d`: #5133, the companion cloneRawRequest boundary fix from the same report.
- `64c613ab0f15526b0c0edb25ad0c2989eace2ea1`: #5136, touches validator tests.
- `fc8bd834dd2e01fc2d26d4459680984150e3b5f6`: #5176, body-cache probe.
- `612b59c0227b421090d46721cd5a98243ad8c6ec`: #5282.
- `c409d855d91d1f0904d19439692216fcf789e6cb`: #5288.
- `531e9c5a3ae058d10de33f643055bd4009a87178`: 2026-08-26 security merge touching body.ts.
- `edd138ee3049749190de3dcd7e32d7bcbf224e41`: #5366, cached-body media type.
- Every commit after head `5226d41` on `main`.
- Release tags v4.12.28 (`626b185d`), v4.12.29 (`cda1af20`), v4.12.30 (`b2ae3a22`), v4.12.31 (`cadff88b`), and v4.12.32 through v4.12.34.

The PR head `5226d41` is the only PR-branch commit.

These issues, PRs and records would give the answer away:
- #5129: the report, its comments and the maintainer's confirmation.
- #5131: the fix.
- #5133: the cloneRawRequest fix referencing #5129.
- #5071: created 2026-07-02, after the cutoff. It is misattributed in #5129.
- #5365/#5366: same bug class.
- The npm changelog and release notes for 4.12.28–4.12.31.
- All #5067 activity after 2026-07-01T09:42:27Z.

## Confidence and limits

Confidence: high. My head/base/fix reproduction, the upstream regression test (fails at head, passes at base), the downstream report, the maintainer's "This is a bug" and the fix commit all agree.

Limits:
- **Runtime coverage.** I reproduced on Node v24.7.0 (undici FormData) only. On Bun, Deno or workerd the exact error text and the shape of the garbled urlencoded output may differ. The mechanism (a new random boundary on re-serialization, parsed against the original header) is runtime-independent per the Fetch spec. `unresolved` for other runtimes: running the same script under each runtime would settle it.
- **Attribution.** #5067 is identified from `git log`/`git diff` of v4.12.27..v4.12.28 and the #5071 diff, not from any upstream statement. The reporter named #5071, and the maintainer did not name a PR.
- **Precision of the vetting claim.** Its "silently drops the fields (`{"gotFile":false}` with no `foo`)" is accurate but understated. The actual body is a single garbage key containing the multipart serialization. I found no other part of the proposal to be wrong.
- **Source of the contract.** The contract comes from released behaviour, the caching test suite, the #4806/#4807 precedent and the maintainer's ruling, not from an explicit sentence in the docs.
