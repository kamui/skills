**Approved (advisory)** — 0 must-fix findings, 2 consider findings.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Enable Flow typings on the error tests (`@flow strict`) and fix the `GraphQLError` constructor's `nodes` typing, per the PR title and the author's own review comment that `nodes` should accept `null` like every other constructor argument.

**Issue fit:** No linked issue (`issues=none`); the PR's own title and its one review comment are the only stated intent. Both stated goals are substantially met — the test files compile under `@flow strict`, and the ambient class declaration for `nodes` now accepts `null` — but the review comment's fix is applied to only one of the two places the parameter's type is declared; see the findings below.

**Coverage:** Complete merge-base diff reviewed (5 files, +48/−47). Ran `flow check` on the head (0 errors). Ran the full suite for all four changed test files with the clone's own mocha (27/27 passing). No history read beyond the pinned head.

**Reviewed:** `7e39a122e` against merge-base `5384d218`.

## Findings

- [P2] [consider] Restore a stack-less fixture for the "creates new stack" test — anchor [`src/error/__tests__/GraphQLError-test.js:58`](https://github.com/graphql/graphql-js/blob/7e39a122eea9292eeffa6905ffdf8a60c5161cfd/src/error/__tests__/GraphQLError-test.js?plain=1#L58)
- [P3] [consider] Match the constructor's own `nodes` type to the fixed declaration — anchor [`src/error/GraphQLError.js:25`](https://github.com/graphql/graphql-js/blob/7e39a122eea9292eeffa6905ffdf8a60c5161cfd/src/error/GraphQLError.js?plain=1#L25); fix [`src/error/GraphQLError.js:94`](https://github.com/graphql/graphql-js/blob/7e39a122eea9292eeffa6905ffdf8a60c5161cfd/src/error/GraphQLError.js?plain=1#L94)

<!-- review-run head=7e39a122eea9292eeffa6905ffdf8a60c5161cfd base-ref=master base-sha=5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11 merge-base=5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11 workflow=v5b-1 context=2f460df7d4bbfa66725887115e49119100fa089004fbc86dc9f62a0a6fa62257 issues=none coverage=complete -->

---

## Finding: `src/error/__tests__/GraphQLError-test.js:58`

**[P2] [consider] Restore a stack-less fixture for the "creates new stack" test**

**Triggers when:** `GraphQLError` receives an `originalError` that itself has no `.stack` — the exact scenario this test's name promises to exercise.

**Impact:** The fixture is now `new Error('original')`, which already carries a real `.stack` at construction. `GraphQLError`'s `originalError && originalError.stack` branch copies that stack instead of reaching the `Error.captureStackTrace` fallback the test claims to check (`src/error/GraphQLError.js:195-201`). The assertion (`e.stack` is a string) passes either way, so the suite stays green while this test now duplicates "uses the stack of an original error" and no test covers the fallback branch.

**Change:** In `src/error/__tests__/GraphQLError-test.js:58`, use an `originalError` without a `.stack` again (a plain object, or an `Error` with `stack` deleted) so the assertion exercises `Error.captureStackTrace`.

Closing this without action is a correct response.

<!-- finding id=error/graphqlerror-stack-test-fixture head=7e39a122eea9292eeffa6905ffdf8a60c5161cfd priority=P2 action=consider blocking=false kind=bug -->

---

## Finding: `src/error/GraphQLError.js:25`

**[P3] [consider] Match the constructor's own `nodes` type to the fixed declaration**

**Triggers when:** A reader consults the exported `GraphQLError` function's own parameter types (`src/error/GraphQLError.js:94`) instead of the ambient `declare class` stub this commit updated (`src/error/GraphQLError.js:25`).

**Impact:** The two declarations of the same `nodes` parameter now disagree: the class declaration accepts `void | null`, matching every sibling argument as the open review thread on this line requested, but the function's own signature still allows only `void`. Before this change both declarations agreed (neither accepted `null`); the fix widened only one of the two.

**Change:** In `src/error/GraphQLError.js:94`, widen `nodes?: $ReadOnlyArray<ASTNode> | ASTNode | void,` to add `| null`, matching line 25.

Closing this without action is a correct response.

<!-- finding id=error/graphqlerror-nodes-null-mismatch head=7e39a122eea9292eeffa6905ffdf8a60c5161cfd priority=P3 action=consider blocking=false kind=maintainability fix=src/error/GraphQLError.js:94 -->
