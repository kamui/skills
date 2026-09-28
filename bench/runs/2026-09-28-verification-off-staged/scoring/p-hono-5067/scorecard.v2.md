# Scorecard: p-hono-5067, mapping v2

Register v1 (d0fe3517872a), rubric v1, scored at 2026-09-28T13:08:23Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 a20a687c6f42d254464dff6440da1ae0950f3f6bd831eaa5cbfd097b7990f962; session 46e172e7-06ff-43dd-b8f4-f1b822f519db; read audit clean.

## att-007 (review-code-sonnet-high-enforced-verification-off), blind-db2e4d

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "patch coverage 76.47% under the 80% target, but the base repository's codecov.yml marks the patch status check `informational: true`, so it does not block merges." Verified: clone/codecov.yml has `patch: default: target: 80%, informational: true`. This is a true CI-hygiene remark with no defect claim. The register rules coverage by itself non-material.

## att-008 (review-code-sonnet-high-enforced-x394-control), blind-1f5c54

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "`parseFormData` ... now reads the whole body via `arrayBuffer()` and re-parses it through `bufferToFormData()` instead of calling the platform `Request.formData()` directly, matching the pattern `src/validator/validator.ts`'s `form` branch already used." This is accurate: body.ts:125-126 and validator.ts:118-121. It is a neutral description of the change and names no consequence. In particular it does not name what happens when only bodyCache.formData is cached (GT-p1), so it only gestures at the right function and is not a recovery.

## att-018 (review-code-sonnet-high-enforced-x394-control), blind-b1fa85

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "parseFormData now buffers the whole request body via arrayBuffer() and re-wraps it in a synthetic Response before calling formData() ... this mirrors the pattern already used in validator.ts's 'form' branch and is required so the normalized (lower-cased) Content-Type reaches the platform's own media-type check." This is an accurate description of body.ts:125-126 and buffer.ts:110-116 with a design rationale. It asserts no defect and does not identify the cached-FormData re-serialization failure, so it is not a recovery of GT-p1. It is an observation.

## att-019 (review-code-sonnet-high-enforced-verification-off), blind-2c8ef3

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-p1`, fix sufficient, priority error False, group none. Quote: "When only `bodyCache.formData` is already cached, `HonoRequest#cachedBody`'s fallback rebuilds bytes via `new Response(cachedFormData).arrayBuffer()`, which ... re-serialize[s] with a brand-new random multipart boundary, while `parseFormData` still passes the original, now-stale `Content-Type` header ... For multipart requests this throws `Failed to parse body as FormData.` ... for urlencoded requests it silently returns corrupted data." This matches the register's trigger, mechanism (src/request.ts:234 plus body.ts:125-126) and both main manifestations exactly, including the merge-base contrast. Proposed fix: "check `request.bodyCache.formData` first and `await`/reuse it when present ... before falling back to `arrayBuffer()` + `bufferToFormData()`." This is the upstream approach the register names as sufficient. It restores correct fields for multipart and urlencoded. Because the cache is reused and not reassigned, bodyCache.formData is no longer overwritten, which also removes the cache-poisoning manifestation. The first-read path and the other working orders are unchanged. Sufficient.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "Codecov ... reports src/utils/body.ts patch coverage at 75% (3 missing lines) ... the missing branches are exactly parseFormData's new bodyCache-population path, consistent with the untested regression above." The figures match packet section 6. The attribution of the missing lines cannot be confirmed without coverage output, though it is plausible because src/utils/body.test.ts builds raw `new Request` objects. This is a coverage-hygiene note that supports item 1, not a separate defect. The register rules coverage by itself non-material.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "stores a pending Promise under a field typed `FormData`; this mirrors `#cachedBody`'s own existing convention ... so it is not a new type-safety regression." This is accurate (body.ts:130; request.ts:238). The register's non_defects entry calls the cast type hygiene. The item explicitly disclaims any defect, so it is non-material.

## att-028 (review-code-sonnet-high-enforced-verification-off), blind-f9a0b3

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "`src/middleware/method-override/index.ts:92` (`contentType?.startsWith('application/x-www-form-urlencoded')`) is unchanged at both merge-base and head ... out of this change's scope since it doesn't touch that file." Verified: line 92 still uses the case-sensitive startsWith, and the diff stat shows method-override is not touched. The item itself labels this pre-existing and out of scope. The PR introduces nothing here, so it is a true observation about adjacent code that sits below the finding threshold for this change.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "Codecov reports this diff's patch coverage below the repository's target ... 76.47% patch coverage against an 80% target." This matches packet section 6. The register rules coverage hygiene non-material, and the item names no cached-body failure.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "`parseFormData` ... now always reads the full request body into an `ArrayBuffer` before parsing form data, where it previously delegated straight to the platform's own `Request.formData()` ... body-request throughput essentially unchanged (35,864.38 to 35,802.34, -0.17%)." This is accurate (body.ts:125-126, and the benchmark in packet section 6). It is a neutral observation that asserts no defect. It does not identify the formData()-then-parseBody() failure, so it is not a recovery of GT-p1.

## att-029 (review-code-sonnet-high-enforced-x394-control), blind-14eda6

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "stores the in-flight `formData()` promise directly into `HonoRequest.bodyCache.formData` (declared as `FormData`) ... so it works correctly despite the misleading static type." Accurate description of src/utils/body.ts:128-131 and the #cachedBody idiom (src/request.ts:220-239). The register's non_defects rule that storing a Promise there is type hygiene and harmless on a first read. The item asserts no defect. It does not identify the formData()-then-parseBody() re-serialization failure (GT-p1), so it is not a recovery. It is a hygiene observation below the finding threshold.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "Codecov reports patch coverage of 76.47% with 3 uncovered lines in body.ts and 1 in buffer.ts ... the uncovered lines are pre-existing branches, not the new mixed-case-matching behavior." The coverage figures match packet section 6. Calling the lines "pre-existing" is loose, because Codecov patch coverage counts only changed lines. The item still asserts no defect, and the register's non_defects rule coverage hygiene non-material by itself. It says nothing about the cached-body order, so it does not recover GT-p1.

## New candidates

None.
