# Review blind-63c8e7

### Item 1
Location: (no file)
Claim: `Overwrite` carries an `@internal` JSDoc tag and is re-exported only from `packages/server/src/internals.ts`, a module not listed among `@trpc/server`'s `package.json` `exports` subpaths, so it is not part of a documented external contract.
Consequence: packages/server/src/core/internals/utils.ts:4-10; packages/server/src/internals.ts:11; packages/server/package.json `exports`.
Fix: —
