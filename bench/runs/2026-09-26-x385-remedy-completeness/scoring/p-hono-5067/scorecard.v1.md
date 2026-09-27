# Scorecard: p-hono-5067, mapping v1

Register v1 (d0fe3517872a), rubric v1, scored at 2026-09-27T07:10:43Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 531d26dde33560c55bc6014a295e258492bc80016db91c2b6b702fe4a6492c8e; session 5c4afdc2-cca1-422d-81fd-8b34fbcd4a66; read audit clean.

## att-002 (review-code-sonnet-high), blind-123970

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The supplied Codecov comment reports patch coverage of 76.47% for this diff (4 lines missing ...), below the repository's 80% patch target, though the added tests directly exercise every mixed-case behavior the change introduces." This restates the codecov bot comment in packet section 6 accurately. The register's non_defects say coverage hygiene is non-material by itself, and the item never names the formData()-then-parseBody() failure, so it does not recover GT-p1. It is a true observation below the finding threshold.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "parseFormData now buffers the request body into an ArrayBuffer and reparses it ... which is the same arrayBuffer+bufferToFormData+bodyCache pattern validator.ts's 'form' branch already used ... so the two entry points are now symmetric rather than one being newly speculative." This is a reassuring observation, not a defect claim. It looks at the exact code behind GT-p1 (clone/src/utils/body.ts:124-131) but misses the asymmetry that causes it: validator.ts:115-116 checks `c.req.bodyCache.formData` first and reuses it, while parseFormData unconditionally calls request.arrayBuffer(). After an earlier formData(), that call gets re-serialized multipart bytes with a new boundary and parses them against the original Content-Type. So the 'symmetric' framing is imprecise. It asserts no defect or material consequence, though, so it is not a false finding. It also gives no trigger, consequence or corrective outcome, so it does not recover GT-p1.

## New candidates

None.
