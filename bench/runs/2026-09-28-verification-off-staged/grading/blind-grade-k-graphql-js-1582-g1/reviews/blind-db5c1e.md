# Review blind-db5c1e

### Item 1
Location: src/error/__tests__/GraphQLError-test.js:58
Claim: Restore coverage of the no-stack fallback branch. `creates new stack if original error has no stack` now builds `original` with `new Error('original')`, and a freshly constructed `Error` always has a truthy `.stack` in this runtime (confirmed: `new Error('original').stack` is a non-empty string).
Consequence: `GraphQLError`'s `if (originalError && originalError.stack)` branch is taken instead of the `Error.captureStackTrace` fallback it means to test — verified by instrumenting the constructor: `e.stack === original.stack` is `true` at head, whereas the prior `{ message: 'original' }` fixture (no `.stack`) made it `false`. The test's own assertion (`e.stack` is a string) holds under either branch, so the fallback stack-creation path is no longer exercised or protected by any test in this file.
Fix: Give `original` an `Error` instance with no `.stack` so the no-stack branch is exercised again, e.g. add `delete original.stack;` right after constructing it on line 58, keeping `original` a real `Error` for the `@flow strict` `?Error` parameter type.

### Item 2
Location: (no file)
Claim: `GraphQLError.js:25`'s `declare class` constructor now types `nodes` as accepting `null`, but the exported `GraphQLError` function's own parameter type on line 94 still omits `null`; `flow check` reports no error from this asymmetry in the reviewed files.
Consequence: src/error/GraphQLError.js:25, src/error/GraphQLError.js:94; `./node_modules/.bin/flow check --show-all-errors` at the reviewed head.
Fix: —
