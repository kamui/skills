# Review blind-f83983

### Item 1
Location: src/error/__tests__/GraphQLError-test.js:58
Claim: Restore no-stack coverage in the 'creates new stack' test. GraphQLError's constructor branches on `if (originalError && originalError.stack)` (src/error/GraphQLError.js:195). At merge-base 5384d21, the test's `originalError` fixture was `{ message: 'original' }`, a plain object with no `.stack`, driving the `else` fallback (`Error.captureStackTrace` / `Error().stack`). At head, the fixture is `new Error('original')`, whose `.stack` is populated synchronously by Node/V8, so the same test now drives the `if (originalError && originalError.stack)` branch instead — the same branch already covered by the 'uses the stack of an original error' test directly above it.
Consequence: No test in the suite still passes GraphQLError a *present* `originalError` that lacks a `.stack` property (a real scenario: `locatedError.js` and `coerceValue.js` can hand it non-Error or deserialized `originalError` values). A regression narrowly scoped to the fallback branch — e.g. weakening the guard to `if (originalError.stack)` and unconditionally copying it whenever `originalError` is truthy — would go undetected, since no remaining test drives a truthy-but-stackless `originalError`.
Fix: Keep the fixture an Error instance (satisfying Flow's `?Error` typing) but strip its stack before constructing, e.g. `const original = new Error('original'); delete original.stack;`, so the test again exercises the no-stack fallback branch its name and assertions describe.

### Item 2
Location: (no file)
Claim: The `declare class GraphQLError` constructor's `nodes` type gained `| null` (src/error/GraphQLError.js:25), but the runtime `export function GraphQLError`'s own Flow annotation for `nodes` a few lines below (src/error/GraphQLError.js:94) still omits `null`, though `flow check` at head still reports 0 errors since nothing calls `GraphQLError(...)` without `new`.
Consequence: src/error/GraphQLError.js:25 vs. src/error/GraphQLError.js:94; `flow check` clean on src/ at head.
Fix: —
