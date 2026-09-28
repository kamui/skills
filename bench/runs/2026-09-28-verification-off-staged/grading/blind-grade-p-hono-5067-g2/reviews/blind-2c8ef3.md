# Review blind-2c8ef3

### Item 1
Location: src/utils/body.ts:121-132
Claim: Reuse cached formData in parseFormData instead of rebuilding it from a stale Content-Type. `c.req.formData()` (directly, or by any code that reads it first, e.g. a middleware) runs before `c.req.parseBody()` on the same `multipart/form-data` or `application/x-www-form-urlencoded` request.
Consequence: `parseFormData` now always calls `request.arrayBuffer()` first. When only `bodyCache.formData` is already cached, `HonoRequest#cachedBody`'s fallback rebuilds bytes via `new Response(cachedFormData).arrayBuffer()`, which the Fetch spec always re-serializes with a brand-new random multipart boundary, while `parseFormData` still passes the original, now-stale `Content-Type` header (old boundary) to `bufferToFormData`. For multipart requests this throws `Failed to parse body as FormData.` out of `parseBody()`; for urlencoded requests it silently returns corrupted data (a `------formdata-undici-...` boundary line as the sole key) instead of `{message: 'hello'}`. Confirmed by direct execution; the same sequence against the merge-base's `parseFormData` (which calls `request.formData()` directly and hits `#cachedBody`'s already-cached short-circuit) succeeds correctly.
Fix: In `parseFormData` (src/utils/body.ts:121-139), check `request.bodyCache.formData` first and `await`/reuse it when present, mirroring the pattern `validator('form')` already uses for the same cache (src/validator/validator.ts:115-121), before falling back to `arrayBuffer()` + `bufferToFormData()`.

### Item 2
Location: (no file)
Claim: Codecov (PR packet §6) reports src/utils/body.ts patch coverage at 75% (3 missing lines) and src/utils/buffer.ts at 50% (1 missing line); the missing branches are exactly parseFormData's new bodyCache-population path, consistent with the untested regression above.
Consequence: PR packet §6 Codecov comment; src/utils/body.ts:128-131.
Fix: —

### Item 3
Location: (no file)
Claim: `request.bodyCache.formData = formDataPromise as unknown as FormData` stores a pending Promise under a field typed `FormData`; this mirrors `#cachedBody`'s own existing convention of storing an unresolved promise under a resolved-value-typed key, so it is not a new type-safety regression.
Consequence: src/utils/body.ts:130; src/request.ts:220-239 (`bodyCache[key] = raw[key]()`).
Fix: —
