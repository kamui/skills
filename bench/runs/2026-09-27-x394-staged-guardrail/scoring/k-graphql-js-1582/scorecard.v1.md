# Scorecard: k-graphql-js-1582, mapping v1

Register v1 (ac8cf95f9b3f), rubric v1, scored at 2026-09-28T03:21:23Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 855745e5bc91f85e04c56a771b41dc61ad3a0804930d05c8b307717ddd7cc4c4; session f3122ddc-d5a1-41af-be0a-88740dbf41ed; read audit clean.

## att-005 (review-code-sonnet-high-enforced-x394-trimmed), blind-131834

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error False, group none. Quote: "adds `| null` to `nodes` on the ambient `declare class GraphQLError` constructor at src/error/GraphQLError.js:25 ... but leaves the exported function's own parameter annotation at line 94 (`nodes?: $ReadOnlyArray<ASTNode> | ASTNode | void`) unchanged"; consequence: "A reader relying on the function's own signature ... would wrongly conclude `null` is unsupported". The fact checks out in clone/: line 25 now has `| void | null` and line 94 still has `| void`. But the consequence the review states is only about how the code reads. At runtime the function body treats null the same as undefined (`nodes ? [nodes] : undefined`), external callers are typed through the declared class, and the register's non_defects rule that the widening itself is correct. The two declarations also already differ elsewhere (originalError is `?Error` vs `?Error & { +extensions: mixed }`), so this is a consistency/hygiene cleanup below the finding threshold. It does not touch GT-k1 (the no-stack test in GraphQLError-test.js now passes a real Error, so it no longer exercises the fallback branch).

## New candidates

None.
