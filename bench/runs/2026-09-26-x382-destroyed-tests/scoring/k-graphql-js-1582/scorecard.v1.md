# Scorecard: k-graphql-js-1582, mapping v1

Register v1 (ac8cf95f9b3f), rubric v1, scored at 2026-09-26T08:54:27Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 edc9a0f114ea7ce6a3a627b87d403f4ff6821ae4ba1a5c5829816c91c8d0c695; session 8ab0e999-a6f9-4b22-9c00-30471302e488; read audit clean.

## att-001 (review-code-sonnet-high), blind-6706d6

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-k1`, fix sufficient, priority error False, group none. Quote: "`creates new stack if original error has no stack` now passes `new Error('original')`, which has a stack, so it takes the same branch as the previous test. Nothing tests the `Error.captureStackTrace` fallback any more"; fix: "`const original: any = new Error('original'); original.stack = undefined;`". This matches GT-k1's mechanism and consequence (see the copy branch at clone/src/error/GraphQLError.js:195 and the test at src/error/__tests__/GraphQLError-test.js:57-63). The guard change in the Claim is the mutation used to demonstrate the gap, not a proposed production edit. The fix makes originalError.stack falsy while typed `any` for Flow, which restores exercising the fallback branches. Sufficient.

## att-006 (review-code-sonnet-high), blind-2fc4cd

Verdict 'Changes Requested'; completion incomplete; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-k1`, fix sufficient, priority error False, group none. Quote: "now builds `new Error('original')`, which always has a stack, so it takes the `originalError.stack` branch. It still passes on that mutation ... where the merge-base fixture `{ message: 'original' }` failed it"; fix: "`const original: any = new Error('original'); original.stack = undefined;`". This is GT-k1's mechanism: a real Error has a truthy stack, so the test takes the copy branch at clone/src/error/GraphQLError.js:195 and cannot catch loss of the fallback. The Claim's 'Change ... to `if (originalError)`' describes the mutation used to show the gap, not a proposed production change. Setting stack to undefined makes originalError.stack falsy, the any annotation satisfies Flow, and the assertions are unchanged, which meets the register's required outcome. Sufficient.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "The `GraphQLError` function implementation still declares `nodes?: $ReadOnlyArray<ASTNode> | ASTNode | void`; only the `declare class` signature gained `| null`, and the runtime already handles null." This is accurate: clone/src/error/GraphQLError.js:25 has `| void | null` and :94 still has `| void`, and the runtime at :102-108 handles null. The item states no consequence and proposes no fix. Callers get their types from the declared class, so this is a consistency observation, not a defect. The register's non_defects also treat the nodes widening as correct.

## att-011 (review-code-sonnet-high), blind-d0e089

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-k1`, fix sufficient, priority error False, group none. Quote: "The test now builds `original` with `new Error('original')`, which always has a truthy `stack`, so it takes only the `originalError.stack` branch. Removing the `&& originalError.stack` guard ... fails the merge-base test but passes every head test."; fix: "`const original: any = { message: 'original' };`". This is GT-k1's mechanism and lost-coverage consequence. The fix restores the plain stackless object and adds an `any` annotation for Flow, which is one of the register's named sufficient outcomes ('a plain object without stack, as before'). Sufficient.

## New candidates

None.
