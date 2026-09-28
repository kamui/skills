# Review blind-14eda6

### Item 1
Location: (no file)
Claim: `parseFormData` now stores the in-flight `formData()` promise directly into `HonoRequest.bodyCache.formData` (declared as `FormData`) before awaiting it; this matches the pre-existing runtime idiom in `HonoRequest#cachedBody`, which always stores an unawaited promise there, so it works correctly despite the misleading static type.
Consequence: src/utils/body.ts:126-132; src/request.ts:220-238.
Fix: —

### Item 2
Location: (no file)
Claim: Codecov reports patch coverage of 76.47% with 3 uncovered lines in body.ts and 1 in buffer.ts; the reviewer's local run confirms every new test in this diff passes, so the uncovered lines are pre-existing branches, not the new mixed-case-matching behavior.
Consequence: codecov PR comment, 2026-07-01T09:41:59Z.
Fix: —
