# Scorecard: p-hono-5067, mapping v1

Register v1 (d0fe3517872a), rubric v1, scored at 2026-09-28T03:51:05Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 ed7a43d72f751ae3252ce47902d11378b66d6f2b7ebc8dfb72d9b6b9b61795fb; session a1301c26-ff55-43fe-bf11-3458e2798102; read audit clean.

## att-008 (review-code-sonnet-high-enforced-x394-trimmed), blind-8cc4b5

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `false-finding`, fix n/a, priority error n/a, group none. Quote: "Avoid buffering the whole body for every multipart/urlencoded parseBody() call" ... "Large uploads the platform could parse without fully materializing now pay a full in-memory buffering cost inside Hono on every request". The code fact is true (clone src/utils/body.ts:126-132 at head replaces request.formData() with arrayBuffer() + bufferToFormData), but the claimed material consequence matches register non_defect 'Reading arrayBuffer() instead of formData() doubles memory or breaks streaming', ruled: 'Request.formData() also buffers the whole body; on a first read the raw body is consumed exactly once, as before. No demonstrated performance consequence.' The item offers no evidence that the platform parses multipart without materializing. It never mentions the cached-body order (formData() then parseBody()) or re-parsing re-serialized bytes against the original Content-Type, so it does not recover GT-p1. Its suggested canonical-case fast path would only avoid GT-p1 by accident, and only for canonical-case headers, so it does not count as identifying the defect.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "body.ts's `parseFormData` now delegates to `bufferToFormData` ... the same helper validator.ts's `form` target already used before this PR, centralizing the media-type-case normalization". This is accurate: main:src/validator/validator.ts:6,120 already imports and calls bufferToFormData, and head body.ts now calls it too. It is a neutral design observation that asserts no defect, so it falls below the finding threshold.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "replaces a `vi.spyOn`-based mock of `formData()` in the file-object-properties preservation test with a real `FormData`, a test-hygiene cleanup". This is accurate per the body.test.ts diff (the vi.spyOn(req, 'formData') mock is removed, and data.append('file', file) / data.append('file.hoo', 'hoo') are added). It is a test-hygiene observation with no claimed consequence.

## New candidates

None.
