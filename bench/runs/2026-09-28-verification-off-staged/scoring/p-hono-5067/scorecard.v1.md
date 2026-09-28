# Scorecard: p-hono-5067, mapping v1

Register v1 (d0fe3517872a), rubric v1, scored at 2026-09-28T07:45:11Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 e1d3d3bb3941d30ed1109edd3ded4cf380267ce086257ad0679c41e11471499e; session ca1a9dd2-ee2c-42a3-bdd4-082bf2ea93f4; read audit clean.

## att-007 (review-code-sonnet-high-enforced-verification-off), blind-4d6e09

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "patch coverage 76.47% under the 80% target, but the base repository's codecov.yml marks the patch status check `informational: true`, so it does not block merges." Accurate: clone/codecov.yml lines 6-9 (same at main) set patch target 80% with informational: true. The register's non_defects rule that Codecov patch-coverage hygiene alone is non-material; the item doesn't identify the formData()-then-parseBody() failure (GT-p1) and asserts no defect.

## att-008 (review-code-sonnet-high-enforced-x394-control), blind-5e78c0

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "`parseFormData` in src/utils/body.ts now reads the whole body via `arrayBuffer()` and re-parses it through `bufferToFormData()` instead of calling the platform `Request.formData()` directly, matching the pattern `src/validator/validator.ts`'s `form` branch already used". Accurate description: clone/src/utils/body.ts:126-132 at head and validator.ts form branch (arrayBuffer + bufferToFormData, unchanged from main). It is a neutral observation with no consequence asserted. It touches the GT-p1 code, but it never names the cached-FormData re-serialization / formData()-before-parseBody() failure or a corrective outcome, so it only points at the right function and does not recover GT-p1.

## New candidates

None.
