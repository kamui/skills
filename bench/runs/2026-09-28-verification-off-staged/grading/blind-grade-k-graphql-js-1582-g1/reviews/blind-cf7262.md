# Review blind-cf7262

### Item 1
Location: src/error/__tests__/GraphQLError-test.js:57-64
Claim: Restore a stack-less originalError in the "no stack" test. The `originalError` fixture in "creates new stack if original error has no stack" changed from `{ message: 'original' }` (no `.stack`) to `new Error('original')`, whose `.stack` is already a truthy string once constructed in this Node/V8 runtime (confirmed empirically: `new Error('original').stack` is truthy; at merge-base the plain-object fixture's `.stack` is `undefined`).
Consequence: `GraphQLError`'s constructor branches on `originalError && originalError.stack`: truthy reuses `originalError.stack`, falsy creates a fresh one via `Error.captureStackTrace`/`Error().stack` (src/error/GraphQLError.js:195-206). With the new fixture, that condition is now truthy, so this test enters the same branch as the adjacent "uses the stack of an original error" test and its only assertion, `expect(e.stack).to.be.a('string')`, is satisfied either way. A regression that breaks stack creation for a stack-less `originalError` would no longer be caught here, yet `mocha` still reports this test passing (13/13 at head).
Fix: Keep `new Error('original')` for the `originalError?: ?Error` Flow typing, but strip its stack before constructing the `GraphQLError`, e.g. `delete original.stack;`, or otherwise supply an Error-shaped value with no `.stack`, so the assertions again exercise the `else` branch at src/error/GraphQLError.js:195-206.

### Item 2
Location: src/error/GraphQLError.js:92-99
Claim: Match the runtime constructor's `nodes` typing to the ambient class. This diff added `| null` to the ambient `declare class GraphQLError` constructor's `nodes` parameter (src/error/GraphQLError.js:25), which is the type external `new GraphQLError(...)` call sites are checked against, but left the sibling `export function GraphQLError`'s own `nodes` parameter (line 94) typed as `... | void` only; before this diff the two matched (`| void` in both).
Consequence: The same constructor parameter is now typed two different ways in one file: the public/ambient signature promises `null` is accepted, but the actual implementation's own parameter type still says otherwise, so a reader of the implementation (or a future refactor merging the two) has no type-level signal that `null` is a supported `nodes` value.
Fix: Add `| null` to the `nodes` parameter type of `export function GraphQLError` at src/error/GraphQLError.js:94 to mirror line 25.
