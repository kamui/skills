# Review blind-8cc4b5

### Item 1
Location: src/utils/body.ts:126-132
Claim: Avoid buffering the whole body for every multipart/urlencoded parseBody() call. Any `parseBody()` call whose Content-Type media type is `multipart/form-data` or `application/x-www-form-urlencoded`, including the previously-working canonical-case requests that this fix did not need to touch.
Consequence: `parseFormData` now always reads the full body into an `ArrayBuffer` and rebuilds a `Response` solely to call `.formData()` on a header-normalized copy, replacing the prior direct `request.formData()` call. Large uploads the platform could parse without fully materializing now pay a full in-memory buffering cost inside Hono on every request, not only the mixed-case ones this PR targets.
Fix: Keep the previous `request.formData()` fast path when the media type is already exactly `multipart/form-data` or `application/x-www-form-urlencoded` (normalization would be a no-op), and only fall back to the buffer-and-normalize path used here for non-canonical casing.

### Item 2
Location: (no file)
Claim: body.ts's `parseFormData` now delegates to `bufferToFormData` (src/utils/buffer.ts), the same helper validator.ts's `form` target already used before this PR, centralizing the media-type-case normalization in one place instead of duplicating it per call site.
Consequence: src/utils/body.ts:126-132; src/validator/validator.ts:119-121; src/utils/buffer.ts:106-117.
Fix: —

### Item 3
Location: (no file)
Claim: This PR's body.test.ts diff also replaces a `vi.spyOn`-based mock of `formData()` in the file-object-properties preservation test with a real `FormData`, a test-hygiene cleanup bundled into the Content-Type fix rather than part of it.
Consequence: src/utils/body.test.ts diff, the file-object-properties preservation test.
Fix: —
