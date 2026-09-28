# Review blind-9d25cd

### Item 1
Location: src/error/__tests__/GraphQLError-test.js:57-64
Claim: Restore no-stack coverage in the stack-creation test. A caller constructs a `GraphQLError` from an `originalError` that is truthy but has no `.stack` — the exact case this test names and previously covered with a plain `{ message: 'original' }` fixture.
Consequence: This diff replaced that fixture with `new Error('original')`, which always has a `.stack`, so the code now takes the stack-reuse branch instead (confirmed: `e.stack === original.stack`). The test's only assertion, `e.stack` is a string, holds either way, so it can no longer catch a regression that weakens the `originalError.stack` presence check and would have failed here before this change.
Fix: Give `original` no `.stack` (e.g. `delete original.stack` after construction, or an equivalent fixture Flow still accepts as `?Error`) and assert `e.stack !== original.stack` so the fallback path is exercised again.

### Item 2
Location: (no file)
Claim: The self-review comment on `GraphQLError.js:25` ("nodes accepts undefined but not null") is addressed for the exported `declare class` signature (now `| void | null`), but the internal `export function GraphQLError`'s own `nodes` parameter (line 93) still omits `| null`; `flow check` reports 0 errors either way, so this leftover asymmetry has no observed effect.
Consequence: src/error/GraphQLError.js:25, src/error/GraphQLError.js:93; `./node_modules/.bin/flow check` at 7e39a122e: 0 errors.
Fix: —
