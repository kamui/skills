# Review blind-8df7f7

### Item 1
Location: src/error/__tests__/GraphQLError-test.js:58
Claim: Restore the no-stack branch this test claims to cover. This test replaced `originalError = { message: 'original' }` with `new Error('original')`. Node/V8 populates a real Error's `.stack` immediately, so `originalError.stack` is now always truthy.
Consequence: `GraphQLError`'s constructor now takes the `if (originalError && originalError.stack)` branch instead of the `else if (Error.captureStackTrace)` branch this test's title names. `expect(e.stack).to.be.a('string')` passes under either branch, so a future regression that breaks stack creation for a stack-less `originalError` would no longer be caught here.
Fix: Keep `new Error('original')` so the value still flow-types as a real `Error`, but strip its captured stack before constructing the `GraphQLError`, e.g. add `delete original.stack;` on the next line, so the no-stack branch runs again.

### Item 2
Location: src/error/GraphQLError.js:94
Claim: Finish the `nodes` null-typing fix in the function's own signature. The packet's unresolved review comment asked why `nodes` accepted `undefined` but not `null`, unlike every other constructor argument. This diff answered it by adding `| null` only to the ambient `declare class` constructor at GraphQLError.js:25.
Consequence: `export function GraphQLError`'s own `nodes` parameter (line 94) still reads `$ReadOnlyArray<ASTNode> | ASTNode | void`, with no `| null`. The file's two parallel declarations of the same parameter now disagree with each other, so the PR's own stated goal, "Fix typing for Error constructor," and the reviewer's request are only half applied.
Fix: Add `| null` to the `nodes` parameter of `export function GraphQLError` on line 94 too, matching the `declare class` constructor's now-fixed type.
