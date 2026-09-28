# Scorecard: j-trpc-5017, mapping v1

Register v3 (3404ee4026d5), rubric v1, scored at 2026-09-28T03:14:42Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 b267d2c68425ef6aca697e68734e67a28060cf3e71d25b93a9894110227b898d; session 31b22f1c-24ad-44a4-96f4-925f9b13a55e; read audit clean.

## att-004 (review-code-sonnet-high-enforced-x394-trimmed), blind-63c8e7

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "`Overwrite` carries an `@internal` JSDoc tag and is re-exported only from `packages/server/src/internals.ts`, a module not listed among `@trpc/server`'s `package.json` `exports` subpaths, so it is not part of a documented external contract." This is an observation about API surface. It asserts no defect and proposes no fix ("Fix: —"; the Consequence line only cites locations). Checked in clone/: the `@internal` tag is at packages/server/src/core/internals/utils.ts:4-5, and the re-export is at packages/server/src/internals.ts:11. `internals.ts` is not an `exports` subpath in packages/server/package.json. However, packages/server/src/index.ts:6 does `export * from './internals'`, so `Overwrite` is reachable from the root `@trpc/server` entry. "Re-exported only from internals.ts" is therefore imprecise. The narrower point, that it is undocumented or internal (`@internal`), holds. The item does not identify any of GT-j1/j2/j3, all of which are consequences of the new gate at call sites through middleware.ts and procedureBuilder.ts, whatever Overwrite's export status. It also claims no material consequence that could be refuted as a false finding. It is an inconsequential observation below the finding threshold.

## New candidates

None.
