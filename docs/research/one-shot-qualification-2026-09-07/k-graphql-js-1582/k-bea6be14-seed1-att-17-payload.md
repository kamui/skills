**Approved (advisory)** — 0 must-fix findings, 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Enable Flow strict-mode typing on the error-related test suite (`GraphQLError-test.js`, `locatedError-test.js`, `printError-test.js`, `inspect-test.js`) and correct the `GraphQLError` constructor's declared `nodes` parameter type so it accepts `null` like its sibling parameters.

**Issue fit:** Issue alignment was unavailable — the pull-request body is empty and carries no closing or explicit issue reference, so the ledger was built from the pull-request title alone. Both title promises are met: the four test files' pragma changed from `@noflow` to `@flow strict`, and the declared constructor's `nodes` type gained `| null`.

**Coverage:** Complete merge-base diff reviewed (5/5 files, 5/5 diff chunks); no repository guidance files present at the merge-base. Focused test run once at the head: `./node_modules/.bin/mocha --require @babel/register --require @babel/polyfill src/error/__tests__/GraphQLError-test.js src/error/__tests__/locatedError-test.js src/error/__tests__/printError-test.js src/jsutils/__tests__/inspect-test.js` — 27 passing, 0 failing.

**Reviewed:** `7e39a122eea9292eeffa6905ffdf8a60c5161cfd` against merge-base `5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11`.

## Findings

- [P3] [consider] Restore the stack-less original-error case in this test — anchor [`src/error/__tests__/GraphQLError-test.js:58`](https://github.com/graphql/graphql-js/blob/7e39a122eea9292eeffa6905ffdf8a60c5161cfd/src/error/__tests__/GraphQLError-test.js?plain=1#L58)

## Observations

- The constructor's declared public type now accepts `null` for `nodes`, but the same file's implementation function still types the parameter as `void`-only. Evidence: `src/error/GraphQLError.js:25`, `src/error/GraphQLError.js:94`.

<!-- review-run head=7e39a122eea9292eeffa6905ffdf8a60c5161cfd base-ref=master base-sha=5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11 merge-base=5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11 workflow=v5b-10 context=2f460df7d4bbfa66725887115e49119100fa089004fbc86dc9f62a0a6fa62257 issues=none coverage=complete -->

---

## Finding comments (as they would post inline)

### `src/error/__tests__/GraphQLError-test.js:58` (RIGHT)

**[P3] [consider] Restore the stack-less original-error case in this test**

**Triggers when:** The test's `original` value is `new Error('original')`, which already has a populated `.stack` in this engine (verified: `original.stack` is truthy and `e.stack === original.stack`).

**Impact:** The test is named for the case where `originalError` has no stack, but with a real `Error` instance that branch (`Error.captureStackTrace`) is never taken; the assertion `expect(e.stack).to.be.a('string')` passes either way, so a future regression in the stack-synthesis branch would go undetected.

**Change:** In `src/error/__tests__/GraphQLError-test.js`, keep `original` typed as an `Error` but strip its stack (e.g. `delete original.stack;` after construction) so the test still exercises the fallback branch it names.

Closing this without action is a correct response.

<!-- finding id=error/graphqlerror-test-stackless-original head=7e39a122eea9292eeffa6905ffdf8a60c5161cfd priority=P3 action=consider blocking=false kind=maintainability -->
