# Review blind-43a9e5

### Item 1
Location: src/error/__tests__/GraphQLError-test.js:58
Claim: Restore coverage for GraphQLError's own-stack fallback. This diff changes the `it('creates new stack if original error has no stack')` fixture from a plain `{ message: 'original' }` object to `new Error('original')`. A real `Error` always carries a truthy `.stack` in Node (confirmed directly: `new Error('x').stack` is a non-empty string immediately after construction), so `GraphQLError`'s `if (originalError && originalError.stack)` branch (src/error/GraphQLError.js:195) now fires instead of the `else if (Error.captureStackTrace)` fallback the test name describes.
Consequence: The fallback that manufactures a fresh stack when the original error has none (src/error/GraphQLError.js:201-208) is no longer exercised by any test in the suite, and this test now silently duplicates the adjacent `'uses the stack of an original error'` test (same fixture shape) with a strictly weaker assertion (`.to.be.a('string')` instead of `.to.equal(original.stack)`). A future regression in the own-stack fallback would go undetected.
Fix: In src/error/__tests__/GraphQLError-test.js:58, keep `original` typed as a real `Error` (required for `@flow strict`) but strip its `.stack` before use, e.g. `const original = new Error('original'); delete original.stack;`, so the assertion again exercises the intended fallback branch.

### Item 2
Location: (no file)
Claim: `GraphQLError.js`'s `declare class` constructor (the type `new GraphQLError(...)` callers are checked against) now accepts `null` for `nodes`, but the separate runtime `function GraphQLError(...)` a few lines below keeps its own narrower `void`-only annotation for the same parameter.
Consequence: src/error/GraphQLError.js:25 vs. src/error/GraphQLError.js:94; `flow check --show-all-errors` at the reviewed head reports 0 errors, confirming no caller (all of which use `new GraphQLError(...)`, never the bare function) is affected by the asymmetry.
Fix: —
