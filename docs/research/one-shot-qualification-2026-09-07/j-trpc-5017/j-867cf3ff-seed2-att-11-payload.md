**Approved (advisory)** — 0 must-fix findings, 2 consider findings.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix TypeScript inference for procedure inputs when middleware sits between `.input()` and `.query()`/`.mutation()`, by making the internal `Overwrite<TType, TWith>` utility only merge object types key-by-key and fully replace non-object types instead of always mapping over `keyof`.

**Issue fit:** Unavailable — the PR body carries no closing issue reference and no issue or spec was supplied; reviewed on the code and its own regression test alone.

**Coverage:** Complete merge-base diff reviewed (both changed files read in full); callers of `Overwrite` across `procedureBuilder.ts` and `middleware.ts` traced; sibling regression tests inspected for convention; `packages/tests` typechecked with the repo's own `tsc --noEmit` (0 errors).

**Reviewed:** `7dc04a7e9` against merge-base `2abb2d5c`.

## Findings

- [P3] [consider] Drop the unreachable `TType` fallback in `Overwrite` — anchor [`packages/server/src/core/internals/utils.ts:25-30`](https://github.com/trpc/trpc/blob/7dc04a7e94654dfad6ef1289dfe01a0a206fff3b/packages/server/src/core/internals/utils.ts?plain=1#L25-L30)
- [P3] [consider] Assert on `voidWithMiddleware`'s inferred types or drop it — anchor [`packages/tests/server/regression/issue-5020-inference-middleware.test.ts:13-17`](https://github.com/trpc/trpc/blob/7dc04a7e94654dfad6ef1289dfe01a0a206fff3b/packages/tests/server/regression/issue-5020-inference-middleware.test.ts?plain=1#L13-L17); fix [`packages/tests/server/regression/issue-5020-inference-middleware.test.ts:38`](https://github.com/trpc/trpc/blob/7dc04a7e94654dfad6ef1289dfe01a0a206fff3b/packages/tests/server/regression/issue-5020-inference-middleware.test.ts?plain=1#L38)

## Observations

- The new regression test's filename cites issue #5020 rather than this PR's own number, and the PR body carries no closing reference to any issue. Evidence: `packages/tests/server/regression/issue-5020-inference-middleware.test.ts` (file).

<!-- review-run head=7dc04a7e94654dfad6ef1289dfe01a0a206fff3b base-ref=main base-sha=2abb2d5cd19740be37272dac6ad7fdd36244ae54 merge-base=2abb2d5cd19740be37272dac6ad7fdd36244ae54 workflow=v5b-1 context=1c8dbb4d4781a49c2ab16f3b0f4b47c4c18838264b00c621266aefd91fd8d750 issues=none coverage=complete -->

---

## Finding 1

**[P3] [consider] Drop the unreachable `TType` fallback in `Overwrite`**

**Triggers when:** `TType` is a non-object type, so the second (non-object) branch of `Overwrite` runs.

**Impact:** `TWith extends any ? TWith : TType` never selects `TType`: every type except `never` satisfies a naked `extends any` check, and instantiating that same naked parameter with `never` short-circuits the whole conditional to `never` before either branch runs. The `: TType` arm is therefore unreachable for every instantiation; the branch always yields `TWith`, or `never` when `TWith` is `never`, so it never actually preserves `TType` the way the branch's shape and its "Same as above" comment suggest.

**Change:** In `packages/server/src/core/internals/utils.ts:25-30`, replace the nested conditional with `: TWith`, which is equivalent to the current code for every instantiation and removes the misleading dead branch.

Closing this without action is a correct response.

<!-- finding id=server/utils-overwrite-dead-branch head=7dc04a7e94654dfad6ef1289dfe01a0a206fff3b priority=P3 action=consider blocking=false kind=maintainability -->

## Finding 2

**[P3] [consider] Assert on `voidWithMiddleware`'s inferred types or drop it**

**Triggers when:** A reader runs or extends `issue-5020-inference-middleware.test.ts`.

**Impact:** The router declares `voidWithMiddleware` (a procedure with middleware but no `.input()`), yet no assertion in the `test('string', ...)` block ever reads `AppRouterInputs['voidWithMiddleware']` or `AppRouterOutputs['voidWithMiddleware']`. Every other regression test in this directory that declares a procedure asserts on its inferred type (e.g. `issue-4947-merged-middleware-inputs.test.ts`), so this entry drops coverage for the middleware-without-input inference path instead of exercising it.

**Change:** In `packages/tests/server/regression/issue-5020-inference-middleware.test.ts`, add `expectTypeOf` assertions for `AppRouterInputs['voidWithMiddleware']` and `AppRouterOutputs['voidWithMiddleware']` inside the test block, or remove the unused procedure.

Closing this without action is a correct response.

<!-- finding id=tests/regression-5020-void-middleware-unused head=7dc04a7e94654dfad6ef1289dfe01a0a206fff3b priority=P3 action=consider blocking=false kind=maintainability fix=packages/tests/server/regression/issue-5020-inference-middleware.test.ts:38 -->
