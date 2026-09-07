**Approved (advisory)** — 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Fix `Overwrite<TType, TWith>` so it only does a key-by-key merge when both `TType` and `TWith` are objects, instead of always iterating `TType`'s keys — which mangled inferred input/output/context types whenever a procedure combined a primitive `.input()` schema (e.g. a plain `z.string()`) with a `.use()` middleware, since `Overwrite<string, string>` previously merged in `string`'s own prototype keys (`charCodeAt`, etc.).

**Issue fit:** Issue alignment was unavailable — the pull-request body carries no closing or referenced issue, so the ledger was built from the pull-request title alone ("inference fix for inputs with middleware"). Met — the new `Overwrite` only key-merges when both arguments are object types and otherwise fully replaces `TType` with `TWith`; the added regression test's `strWithMiddleware` case (`.input(z.string())` plus a pass-through `.use()` middleware) type-checks cleanly at the head, confirming the previously garbled inferred input type is now the plain `string` the test asserts.

**Coverage:** Complete merge-base diff reviewed (2/2 changed files, 2/2 diff chunks consumed). `Overwrite<>`'s call sites in `middleware.ts`, `procedureBuilder.ts`, and `initTRPC.ts` were read to bound the compatibility risk of changing this internal type: `_ctx_out` is always instantiated from an object type, and `_input_in`/`_input_out` are already guarded by an `UnsetMarker` check before `Overwrite` is invoked, so no call site regresses from the change. Focused `tsc --noEmit -p tsconfig.json` run once in `packages/tests` at the head: pass, no errors, 5.5s. Focused `vitest run` on the new test file was unavailable — the toolchain could not resolve the `@trpc/server` package because this offline clone has no built `dist` output — and the case was instead decided by trace, since the file's only assertions are the compile-time `expectTypeOf` checks already exercised by the `tsc` run.

**Reviewed:** `7dc04a7e94654dfad6ef1289dfe01a0a206fff3b` against merge-base `2abb2d5cd19740be37272dac6ad7fdd36244ae54`.

## Findings

- [P3] [consider] Assert inferred types for `voidWithMiddleware` — anchor [`packages/tests/server/regression/issue-5020-inference-middleware.test.ts:13-17`](https://github.com/trpc/trpc/blob/7dc04a7e94654dfad6ef1289dfe01a0a206fff3b/packages/tests/server/regression/issue-5020-inference-middleware.test.ts?plain=1#L13-L17); fix [`packages/tests/server/regression/issue-5020-inference-middleware.test.ts:38`](https://github.com/trpc/trpc/blob/7dc04a7e94654dfad6ef1289dfe01a0a206fff3b/packages/tests/server/regression/issue-5020-inference-middleware.test.ts?plain=1#L38)

## Observations

- The `: TType` fallback added to `Overwrite`'s non-object branch is unreachable, since TypeScript collapses a distributive conditional on a naked type parameter equal to `never` to `never` before either branch runs, confirmed by isolating the type under `tsc`. Evidence: `packages/server/src/core/internals/utils.ts:25-29`.

<!-- review-run head=7dc04a7e94654dfad6ef1289dfe01a0a206fff3b base-ref=main base-sha=2abb2d5cd19740be37272dac6ad7fdd36244ae54 merge-base=2abb2d5cd19740be37272dac6ad7fdd36244ae54 workflow=v5b-10 context=1c8dbb4d4781a49c2ab16f3b0f4b47c4c18838264b00c621266aefd91fd8d750 issues=none coverage=complete -->

---

## Finding comment (as it would be posted inline)

**Anchor:** `packages/tests/server/regression/issue-5020-inference-middleware.test.ts:13-17` (RIGHT)

**[P3] [consider] Assert inferred types for `voidWithMiddleware`**

**Triggers when:** A future change to `Overwrite`, `FlatOverwrite`, or the middleware chain regresses inference for a procedure that has middleware but no `.input()` call.

**Impact:** The declared `voidWithMiddleware` procedure in the router fixture is never referenced anywhere in the `describe`/`test` body, so no `expectTypeOf` assertion checks its inferred `ctx`, input, or output types; a regression specific to input-less middleware chains would compile without failing this file.

**Change:** In the `test('string', ...)` block, add `AppRouterInputs['voidWithMiddleware']` / `AppRouterOutputs['voidWithMiddleware']` type assertions alongside the existing `str` and `strWithMiddleware` cases, matching the local convention of exercising every declared procedure with `expectTypeOf` (e.g. `packages/tests/server/regression/issue-2856-middleware-infer.test.ts`).

Closing this without action is a correct response.

<!-- finding id=tests/issue-5020-void-with-middleware-unused head=7dc04a7e94654dfad6ef1289dfe01a0a206fff3b priority=P3 action=consider blocking=false kind=maintainability fix=packages/tests/server/regression/issue-5020-inference-middleware.test.ts:38 -->
