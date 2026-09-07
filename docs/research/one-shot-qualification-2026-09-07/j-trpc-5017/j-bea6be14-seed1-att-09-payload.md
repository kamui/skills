# Review payload — `trpc/trpc#5017` (cell `j-bea6be14-seed1`, attempt `att-09`)

Retrospective review of a merged pull request; publication disabled. This file renders the review
exactly as it would have been published — one forge-native review with a summary body and one
inline line comment — had publication been authorized. Event: `COMMENT`. Posting identity: `kamui`.

Produced by `python3 scripts/validate_review.py --emit-batch < payload.json`, which validated
(exit 0) against `/tmp/qual137/snapshots/bea6be14/skills/code-review-publish/scripts/validate_review.py`.

---

## Review summary body

**Approved (advisory)** — 0 must-fix findings, 1 consider finding, 0 open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix `Overwrite<TType, TWith>` so it only merges keys when both `TType` and `TWith` are objects, instead of always building a mapped type over `keyof TType | keyof TWith`; the previous implementation mangled inference when a procedure had a middleware between `.input()` and `.query()`, because it iterated the keys of primitive types (e.g. `string`'s prototype members).

**Issue fit:** Unavailable — no linked issue; the pull-request title and body carry no checkable acceptance criterion (the body is the unfilled template, and its checklist items are unchecked boilerplate, not concrete promises).

**Coverage:** Complete merge-base diff reviewed (2 files); `packages/server/src/core/internals/utils.ts` inspected whole-file (95 lines) and against the merge-base version; all six call sites of `Overwrite` in `packages/server/src` inspected; new regression test file inspected in full. Focused `tsc --noEmit -p tsconfig.json` run once at the head in `packages/tests`: pass, no errors (confirms the `str` and `strWithMiddleware` type assertions the new test adds); `vitest` execution not run — outside this run's authorized execution allowance (focused type-checking only).

**Reviewed:** `7dc04a7e94654dfad6ef1289dfe01a0a206fff3b` against merge-base `2abb2d5cd19740be37272dac6ad7fdd36244ae54`.

## Findings

- [P3] [consider] Assert the inferred types for `voidWithMiddleware` — anchor [`packages/tests/server/regression/issue-5020-inference-middleware.test.ts:13-17`](https://github.com/trpc/trpc/blob/7dc04a7e94654dfad6ef1289dfe01a0a206fff3b/packages/tests/server/regression/issue-5020-inference-middleware.test.ts?plain=1#L13-L17); fix [`packages/tests/server/regression/issue-5020-inference-middleware.test.ts:39`](https://github.com/trpc/trpc/blob/7dc04a7e94654dfad6ef1289dfe01a0a206fff3b/packages/tests/server/regression/issue-5020-inference-middleware.test.ts?plain=1#L39)

## Observations

- The `object`-branch's trailing `: never` fallback in the new `Overwrite` (for a non-object, non-never `TWith`) is unreachable, because TypeScript's distributive-conditional collapse over the naked `TWith extends object` check already resolves the whole expression to `never` whenever `TWith` is `never`, before that inner ternary is reached. Evidence: `packages/server/src/core/internals/utils.ts:12-19`.

<!-- review-run head=7dc04a7e94654dfad6ef1289dfe01a0a206fff3b base-ref=main base-sha=2abb2d5cd19740be37272dac6ad7fdd36244ae54 merge-base=2abb2d5cd19740be37272dac6ad7fdd36244ae54 workflow=v5b-10 context=1c8dbb4d4781a49c2ab16f3b0f4b47c4c18838264b00c621266aefd91fd8d750 issues=none coverage=complete -->

---

## Inline comments

### 1. `packages/tests/server/regression/issue-5020-inference-middleware.test.ts:13-17` (side `RIGHT`)

**[P3] [consider] Assert the inferred types for `voidWithMiddleware`**

**Triggers when:** A future change to `Overwrite` regresses inference for a procedure that has no `.input()` call and only uses middleware — exactly the `voidWithMiddleware` case this file already declares.

**Impact:** This regression test would keep passing even if that no-input-with-middleware path became mangled again, because no assertion in the file reads `AppRouterInputs['voidWithMiddleware']` or `AppRouterOutputs['voidWithMiddleware']`; the procedure is declared but never checked.

**Change:** In `packages/tests/server/regression/issue-5020-inference-middleware.test.ts`, add a block that asserts `AppRouterInputs['voidWithMiddleware']` and `AppRouterOutputs['voidWithMiddleware']`, following the pattern already used for `str` and `strWithMiddleware`.

Closing this without action is a correct response.

<!-- finding id=tests/void-with-middleware-untested head=7dc04a7e94654dfad6ef1289dfe01a0a206fff3b priority=P3 action=consider blocking=false kind=maintainability fix=packages/tests/server/regression/issue-5020-inference-middleware.test.ts:39 -->

---

No open questions were published. No further inline comments.
