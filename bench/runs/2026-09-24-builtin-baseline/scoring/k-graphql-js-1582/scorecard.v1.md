# Scorecard: k-graphql-js-1582, mapping v1

Register v1 (ac8cf95f9b3f), rubric v1, scored at 2026-09-25T20:44:07Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 505a96e75a0030b1c02e377cd13341f6494358f9c00ad63fdc8609e05363e664; session cd6f7bb9-2158-46e7-8c1e-b56857212aac; read audit clean.

## att-024 (claude-builtin-sonnet-high), blind-90cfed

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "the real `GraphQLError` function implementation's `nodes` parameter type (line 94) was not updated ... Runtime behaviour is fine today". Accurate (lines 25 vs 94). The item concedes there is no present effect, and the register rules the widening correct, so this is declaration/implementation consistency hygiene.
- item-1: `defect:GT-k1`, fix absent, priority error n/a, group none. Quote: "The test change `original = new Error('original')` (replacing `{ message: 'original' }`) no longer exercises the 'original error has no stack' path ... It only passes because `new Error` has a stack, so the test may not cover the branch its name describes." This names the GT-k1 mechanism: the stack is present, so the no-stack branch is not covered. It clears the recovery bar despite the hedging and the leading type-drift remarks, which overlap item 1's non-material observation. It proposes no change to the test, so fix_sufficiency is absent.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "A blanket `// $FlowFixMe` was added above `inspect('"')` to silence Flow on `String.raw`". The register's non_defects rule that this suppression covers a known Flow 0.86 limitation with no runtime effect. This is hygiene.

## att-025 (claude-builtin-opus-high), blind-32a02e

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-k1`, fix sufficient, priority error False, group none. Quote: "now passes `new Error('original')`, which has a stack... takes the 'reuse original stack' branch. The `Error.captureStackTrace` and `Error().stack` fallbacks ... are no longer tested ... use an Error whose stack is deleted (`delete original.stack`), or cast a plain object to `any`." Same mechanism as GT-k1 (GraphQLError.js:195 copy branch; confirmed in clone-work: e.stack === original.stack is true). Both proposed changes make originalError.stack falsy under Flow, so the test exercises the else branches again: sufficient.
- item-1: `non-material`, fix n/a, priority error False, group none. Quote: "`null` was added to `nodes` only in the `declare class` constructor (line 25). The real `function GraphQLError` signature on line 94 still says ... `| void`". True (GraphQLError.js:25 vs :94), but the only consequence is a hypothetical future edit; runtime handles null today (line 106-108), and the originalError mismatch at line 98 predates the PR. The register rules the widening correct. This is a consistency/hygiene remark below the finding threshold.
- item-2: `non-material`, fix n/a, priority error False, group none. Quote: "The PR removed the only test that builds a GraphQLError with no arguments; it was changed to `new GraphQLError('str')`." True per the diff (GraphQLError-test.js:30-31). The test's purpose is instanceof checking, and the constructor does nothing with message except store it (line 145). The regression named ('calling message.length') is hypothetical. This is a minor coverage observation, not a material defect.
- item-3: `non-material`, fix n/a, priority error False, group none. Quote: "A bare `// $FlowFixMe` ... suppresses every Flow error on that line". The register's non_defects rule that this $FlowFixMe suppresses a known Flow 0.86 String.raw limitation with no runtime effect. Suggesting a plain literal instead is a style/hygiene suggestion.
- item-4: `non-material`, fix n/a, priority error False, group none. Quote: "Annotating `e` as `any` turns off type checking for `e` ... weakens the new `@flow strict` coverage". The register's non_defects rule that the `e: any` annotations in locatedError-test.js are deliberate, idiomatic escape hatches for test doubles. The item offers a hygiene alternative only.
- item-5: `non-material`, fix n/a, priority error False, group none. Quote: "`opA`/`opB` are misleading names ... `invariant(fieldA && fieldB)` on line 80 is redundant." This is naming and redundancy cleanup in printError-test.js:62-80, with no behavioural claim. The register's non_defects note that the refactor preserves behaviour.
- item-6: `non-material`, fix n/a, priority error False, group none. Quote: "The fixtures ... moved from inside each test to module load time ... a test that mutates a node ... would affect the others." The hoisting is accurate (diff lines 17-26), but no test in the file mutates the shared nodes, and the passing suite shows no effect. This is a test-structure preference with only hypothetical consequences.

## att-026 (codex-default), blind-c2f793

Verdict 'patch is incorrect'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-k1`, fix sufficient, priority error False, group none. Quote: "`new Error('original')` already has a stack in Node, so this test now exercises copying the original stack ... removes the existing regression coverage while leaving the test passing. Delete `original.stack` before constructing the `GraphQLError` to preserve the scenario with a Flow-compatible error." This is GT-k1, and the fix is the #4774 remedy: sufficient.

## att-027 (review-code-sonnet-high), blind-5880ff

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery False; false clean False.

- item-0: `defect:GT-k1`, fix sufficient, priority error True, group none. Quote: "now passes `new Error('original')`, which always has a `stack` ... the `Error.captureStackTrace` fallback (`src/error/GraphQLError.js:201`) is no longer exercised"; Fix: "`const original: any = new Error('original'); delete original.stack;` ... keeping the Flow typing satisfied." This is exactly GT-k1's mechanism, and the fix matches the register's required outcome (and #4774): sufficient.

## att-063 (claude-builtin-opus-high), blind-5b5064

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-k1`, fix sufficient, priority error False, group none. Quote: "passes `new Error('original')`, which always has a stack ... the `to.be.a('string')` check passes trivially. If the fallback broke ... the suite would stay green. A stackless typed value is needed, e.g. `const original: any = { message: 'original' }` or ... `delete original.stack`, plus an assertion that e.stack !== original.stack." This recovers GT-k1 in full. The fix makes stack falsy while typed and adds a discriminating assertion: sufficient.
- item-1: `false-finding`, fix n/a, priority error n/a, group none. Quote: "Code in the repo (or a published .js.flow consumer) typed against the exported function rather than the declared class still rejects `GraphQLError(msg, null, ...)`. That is exactly the call the new test makes". The signature mismatch itself is true (GraphQLError.js:25 vs :94). The material consequence is contradicted: Flow resolves the GraphQLError binding through the `declare class`, and the register records that the widening removes the Flow errors at these call sites (non_defects: reverting 'reintroduces eight Flow errors at call sites this PR touches'), so the test's null call type-checks at head. No consumer types against the implementation signature separately; a .js.flow copy has the same declare-class pairing. A fabricated consequence attached to a true fact counts as a false finding.
- item-2: `non-material`, fix n/a, priority error False, group none. Quote: "locations are computed from the raw `positions && source` arguments rather than from `_positions && _source` ... `new GraphQLError('msg', [fieldNode], undefined, [6])` sets e.positions = [6] ... e.locations is taken from the node's loc.start". I verified in clone-work: positions [6], locations [{line:2,column:3}]. The behaviour is accurate, but line 131 is pre-existing code the diff does not touch (the PR changes only line 25 of GraphQLError.js), so it is not a defect introduced by this change. It is recorded as an out-of-scope observation.
- item-3: `non-material`, fix n/a, priority error False, group none. Quote: "Hoisting source, AST and nodes into module-level shared fixtures means every test now shares one AST object". Accurate, but no test mutates the fixtures and the suite passes. The order-dependence risk is hypothetical, so this is a test-structure preference.
- item-4: `non-material`, fix n/a, priority error False, group none. Quote: "The no-argument `new GraphQLError()` case was dropped in favour of `new GraphQLError('str')`". True per the diff, but that test's purpose was instanceof checking, and the constructor only stores message (line 145). The regression is hypothetical, making this a minor coverage observation.
- item-5: `non-material`, fix n/a, priority error False, group none. Quote: "A bare, unexplained `// $FlowFixMe` blankets the whole `String.raw` assertion". The register's non_defects rule that this suppression covers a known Flow 0.86 String.raw limitation with no runtime effect. The literal-string alternative is hygiene.
- item-6: `non-material`, fix n/a, priority error False, group none. Quote: "Typing the test errors as `any` turns off all type checking for them". The register's non_defects rule that `e: any` here is a deliberate, idiomatic escape hatch for test doubles. The typo scenario is hypothetical hygiene.
- item-7: `non-material`, fix n/a, priority error False, group none. Quote: "Variables holding an ObjectTypeDefinition are named `opA`/`opB` (operation), which misleads, and the same parse-then-invariant block is copy-pasted". This is naming and duplication cleanup in a test with no behavioural effect.
- item-8: `non-material`, fix n/a, priority error False, group none. Quote: "`invariant(fieldA && fieldB)` is redundant". This is a dead-guard cleanup that the item itself says has no change in behaviour. It is a separate claim from item 8's naming.

## att-064 (codex-default), blind-9f468b

Verdict 'patch is incorrect'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-k1`, fix sufficient, priority error False, group none. Quote: "`new Error('original')` already has a stack in Node.js, so this test now exercises copying an existing stack ... duplicates the preceding test and would pass even if stack creation for stackless original errors broke. Clear or delete `original.stack` before constructing the `GraphQLError`". This is GT-k1's mechanism and consequence, and the fix matches the required outcome: sufficient.

## att-065 (review-code-sonnet-high), blind-e27d49

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery False; false clean False.

- item-0: `defect:GT-k1`, fix sufficient, priority error True, group none. Quote: "builds `original` with `new Error('original')`, which always has a `stack` ... takes the `originalError.stack` branch, the same as the preceding test ... a regression in the no-stack fallback path ... would go unnoticed." Fix: "keep the plain `{ message: 'original' }` object typed `any`, so the fallback branch stays exercised under Flow." This recovers GT-k1, and the fix satisfies the required outcome: sufficient.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "The implementation signature of `GraphQLError` still types `nodes` without `null`, while the `declare class` above it now allows it; runtime already handles `null`." Accurate (lines 25 vs 94), and the item itself concedes no runtime effect. This is consistency hygiene.

## att-066 (claude-builtin-sonnet-high), blind-72e92a

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-k1`, fix sufficient, priority error n/a, group none. Quote: "now passes an Error that does have a stack, so it no longer covers the no-stack branch ... GraphQLError.js:195 checks `originalError && originalError.stack` ... If that fallback broke, the test would still pass. ... `const original = new Error('original'); delete original.stack;`". This matches GT-k1's mechanism, and the fix is the one #4774 applied, restoring the else branch: sufficient.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "The `declare class` constructor now accepts `nodes: null`, but the actual function implementation signature still types `nodes` as `... | void` only ... A future change to the null handling ... would not be caught". Accurate (lines 25 vs 94), and the item itself says Flow passes. The only consequence is a hypothetical future edit, so this is a consistency/hygiene note.

## New candidates

None.
