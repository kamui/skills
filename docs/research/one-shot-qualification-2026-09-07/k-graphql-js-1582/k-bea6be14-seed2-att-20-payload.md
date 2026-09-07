**Approved (advisory)** — 0 must-fix findings, 2 consider findings.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Enable Flow type-checking on the `src/error/__tests__` test files (plus `inspect-test.js`) and widen the `GraphQLError` constructor's declared `nodes` type to also accept `null`, per the author's own review comment on this PR.

**Issue fit:** Issue alignment was unavailable; the ledger was built from the pull-request title alone (the body is empty). "Enable Flow typings on errors tests" — met: all four `src/error/__tests__/*` files plus `src/jsutils/__tests__/inspect-test.js` moved from `@noflow` to `@flow strict`, and each runs clean under mocha. "Fix typing for Error constructor" — partial: the constructor's public `declare class` type now accepts `null` for `nodes` as requested, but the implementation function's own parameter type was not updated to match (see finding below).

**Coverage:** Complete merge-base diff reviewed (5/5 changed files, all diff chunks consumed). Focused tests run once each at the reviewed head with `./node_modules/.bin/mocha --require @babel/register --require @babel/polyfill`: `src/error/__tests__/GraphQLError-test.js` (13 tests, pass, ~28ms) and `src/error/__tests__/locatedError-test.js` + `src/error/__tests__/printError-test.js` + `src/jsutils/__tests__/inspect-test.js` together (14 tests, pass, ~23ms). A repository-wide grep for other `nodes?:` constructor-type declarations and for `new GraphQLError(` call sites passing `null` found no other location this change should have touched.

**Reviewed:** `7e39a122eea9292eeffa6905ffdf8a60c5161cfd` against merge-base `5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11`.

## Findings

- [P3] [consider] Sync the constructor implementation's own type with the widened public signature — anchor [`src/error/GraphQLError.js:25`](https://github.com/graphql/graphql-js/blob/7e39a122eea9292eeffa6905ffdf8a60c5161cfd/src/error/GraphQLError.js?plain=1#L25); fix [`src/error/GraphQLError.js:94`](https://github.com/graphql/graphql-js/blob/7e39a122eea9292eeffa6905ffdf8a60c5161cfd/src/error/GraphQLError.js?plain=1#L94)
- [P2] [consider] Restore coverage for the stack-fallback branch when `originalError` lacks its own stack — anchor [`src/error/__tests__/GraphQLError-test.js:58`](https://github.com/graphql/graphql-js/blob/7e39a122eea9292eeffa6905ffdf8a60c5161cfd/src/error/__tests__/GraphQLError-test.js?plain=1#L58)

<!-- review-run head=7e39a122eea9292eeffa6905ffdf8a60c5161cfd base-ref=master base-sha=5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11 merge-base=5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11 workflow=v5b-10 context=2f460df7d4bbfa66725887115e49119100fa089004fbc86dc9f62a0a6fa62257 issues=none coverage=complete -->

---

## Finding 1 — anchor `src/error/GraphQLError.js:25`

**[P3] [consider] Sync the constructor implementation's own type with the widened public signature**

**Triggers when:** A maintainer reads or edits `export function GraphQLError` in this file and relies on its own parameter annotation for `nodes`, or a future refactor removes the `declare class` trick and exposes the function's own signature as the real public type.

**Impact:** The two Flow signatures for the same constructor now disagree about whether `nodes` accepts `null`: the `declare class` at line 25 was widened to `void | null` for exactly this reason, but the runtime `export function GraphQLError` at line 94 still declares only `void`. A reader trusting the implementation's own type believes `null` is still unsupported, even though it is accepted and handled correctly at runtime.

**Change:** In `src/error/GraphQLError.js`, add `| null` to the `nodes` parameter of `export function GraphQLError` (line 94) to match the `declare class` constructor this PR already updated.

**Source:** Pull request title, "Fix typing for Error constructor".

Closing this without action is a correct response.

<!-- finding id=error/graphqlerror-nodes-type-sync head=7e39a122eea9292eeffa6905ffdf8a60c5161cfd priority=P3 action=consider blocking=false kind=requirement fix=src/error/GraphQLError.js:94 -->

## Finding 2 — anchor `src/error/__tests__/GraphQLError-test.js:58`

**[P2] [consider] Restore coverage for the stack-fallback branch when `originalError` lacks its own stack**

**Triggers when:** `new GraphQLError(...)` is constructed with an `originalError` that itself carries no `.stack`, the exact scenario this test's name promises to cover.

**Impact:** `original` is now `new Error('original')`, which already has a populated `.stack` in this Node/V8 test environment, so `originalError && originalError.stack` is true and `GraphQLError.js:195`'s reuse branch runs, giving `e.stack === original.stack`. The assertions (`e.stack` is a string) don't discriminate reuse from a freshly captured stack, so the test now silently duplicates "uses the stack of an original error" instead of exercising `Error.captureStackTrace`'s fallback for an `originalError` that lacks its own stack; no other test in the file covers that scenario.

**Change:** In `src/error/__tests__/GraphQLError-test.js`, construct `original` so it still satisfies the constructor's `Error`-typed parameter but genuinely has no `.stack` (for example an `Error` instance with `stack` deleted or set to `undefined`), and assert `e.stack !== original.stack` so the test again proves the fallback path runs.

Closing this without action is a correct response.

<!-- finding id=error/graphql-error-test-stack-fallback-coverage head=7e39a122eea9292eeffa6905ffdf8a60c5161cfd priority=P2 action=consider blocking=false kind=maintainability -->
