**Approved (advisory)** — 0 must-fix findings, 2 consider findings.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix `Overwrite<TType, TWith>` so a non-object `TType` (e.g. `string`) is no longer iterated key-by-key like an object — the commit message documents `Overwrite<string, string>` mangling into an object keyed by `String.prototype` members whenever a procedure combined `.input()` with `.use()` middleware.

**Issue fit:** Not applicable — the PR body has no closing or explicit issue reference (`Closes #` unfilled) and no spec was supplied; the commit message is the only stated intent, and the diff was checked against it directly.

**Coverage:** Complete merge-base diff reviewed (2 files, +57/−3): full `utils.ts` (95 lines) at head and merge-base, and the full new 40-line regression test. Traced every `Overwrite` call site (`middleware.ts`, `procedureBuilder.ts`, `utils.ts:71`); the default root `ctx` type (`object`) always takes the object branch, so only input inference exercises the new non-object branch. An isolated `tsc --noEmit --strict` type-level check confirmed `Overwrite<string, string>` now resolves to `string` (previously mangled) and object+object overwrite is unchanged. `tsc --noEmit -p packages/tests/tsconfig.json` (whole project, includes the new test): 0 errors. Checked `utils.ts`'s pre-merge-base history (a prior perf fix, two prior inference fixes); none conflicts. Authorization, secrets, path handling, migrations, and concurrency risk categories do not apply to this compile-time type-only change.

**Reviewed:** `7dc04a7e9` against merge-base `2abb2d5c`.

## Findings

- [P3] [consider] Fix the unreachable `: TType` branch in `Overwrite` — anchor [`packages/server/src/core/internals/utils.ts:25-29`](https://github.com/trpc/trpc/blob/7dc04a7e94654dfad6ef1289dfe01a0a206fff3b/packages/server/src/core/internals/utils.ts?plain=1#L25-L29)
- [P3] [consider] Add type assertions for `voidWithMiddleware` in the new regression test — anchor [`packages/tests/server/regression/issue-5020-inference-middleware.test.ts:13-17`](https://github.com/trpc/trpc/blob/7dc04a7e94654dfad6ef1289dfe01a0a206fff3b/packages/tests/server/regression/issue-5020-inference-middleware.test.ts?plain=1#L13-L17); fix [`packages/tests/server/regression/issue-5020-inference-middleware.test.ts:38`](https://github.com/trpc/trpc/blob/7dc04a7e94654dfad6ef1289dfe01a0a206fff3b/packages/tests/server/regression/issue-5020-inference-middleware.test.ts?plain=1#L38)

<!-- review-run head=7dc04a7e94654dfad6ef1289dfe01a0a206fff3b base-ref=main base-sha=2abb2d5cd19740be37272dac6ad7fdd36244ae54 merge-base=2abb2d5cd19740be37272dac6ad7fdd36244ae54 workflow=v5b-1 context=1c8dbb4d4781a49c2ab16f3b0f4b47c4c18838264b00c621266aefd91fd8d750 issues=none coverage=complete -->

---

## Finding: server/overwrite-never-with-branch

**[P3] [consider] Fix the unreachable `: TType` branch in `Overwrite`**

**Triggers when:** `Overwrite<TType, TWith>` is instantiated with a non-object `TType` and `TWith` resolves to exactly `never` (for example a middleware chain whose next `_input_in`/`_input_out` is `never`, as with `.input(z.never())`).

**Impact:** TypeScript's naked-type-parameter distribution collapses the whole `TWith extends any ? TWith : TType` conditional to `never` before the new `: TType` branch can ever be selected, so `Overwrite<string, never>` still resolves to `never`, not `TType` as the branch and its comment claim. The branch is dead code documenting a behavior the type does not have; the actual result is unchanged from before this fix.

**Change:** Either delete the unreachable `: TType` branch and note in the comment that a `never` `TWith` still collapses the whole type to `never`, or implement the documented fallback with a non-distributive check such as `[TWith] extends [never] ? TType : TWith`.

Closing this without action is a correct response.

<!-- finding id=server/overwrite-never-with-branch head=7dc04a7e94654dfad6ef1289dfe01a0a206fff3b priority=P3 action=consider blocking=false kind=maintainability -->

Anchor: `packages/server/src/core/internals/utils.ts:25-29` (RIGHT). Rendered as a line comment on that range in the forge-native batch.

---

## Finding: tests/void-with-middleware-unused

**[P3] [consider] Add type assertions for `voidWithMiddleware` in the new regression test**

**Triggers when:** A future change to `Overwrite`, `UnsetMarker` handling, or procedure-builder inference alters the inferred input/output types for a procedure that has middleware but no `.input()` call.

**Impact:** The new regression test declares `voidWithMiddleware` in its router but never reads `AppRouterInputs['voidWithMiddleware']` or `AppRouterOutputs['voidWithMiddleware']`, so the suite would not catch a regression in that inference path even though the fixture exists specifically to exercise it.

**Change:** In the `test('string', ...)` block, add a third assertion group checking that `AppRouterInputs['voidWithMiddleware']` is `undefined` and `AppRouterOutputs['voidWithMiddleware']` is `void`, matching the pattern already used for `str` and `strWithMiddleware`.

Closing this without action is a correct response.

<!-- finding id=tests/void-with-middleware-unused head=7dc04a7e94654dfad6ef1289dfe01a0a206fff3b priority=P3 action=consider blocking=false kind=maintainability fix=packages/tests/server/regression/issue-5020-inference-middleware.test.ts:38 -->

Anchor: `packages/tests/server/regression/issue-5020-inference-middleware.test.ts:13-17` (RIGHT); fix `packages/tests/server/regression/issue-5020-inference-middleware.test.ts:38`. Rendered as a line comment on the anchor range in the forge-native batch.

---

No open questions and no observations were admitted in this run (see the research report for the candidates considered and why neither channel was populated).
