# Scorecard: j-trpc-5017, mapping v1

Register v2 (f4c3bc6e55ed), rubric v1, scored at 2026-09-26T08:55:18Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 96c8cdbd049580a2f2c5de02a5e904367133a86e2232317da6e0bafc2cbe4c84; session 815167e8-1275-4ad5-bae4-4e5a690c78ba; read audit clean.

## att-002 (review-code-sonnet-high), blind-a780c7

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error False, group none. Quote: "Remove the unreachable TType fallback and fix the never comment ... a tsc probe shows Overwrite<{a:1}, never> is never, so readers are misled about the contract." True: my tsc probe (clone-work/g2/probe.ts) confirms Overwrite<{a:1}, never> and Overwrite<string, never> are never, so the `: TType` arm at utils.ts:29 can't be reached. The merge-base type also gave never here, so no behaviour changed. This is cleanup plus a comment clarification, covered by the non_defects entries on the redundant `TWith extends any` branches. It recovers neither registered defect.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "Overwrite now returns TWith unchanged when it is unknown or any (Overwrite<{a:1}, unknown> is unknown, was {a:1}), a behavior change from the merge-base that existing callers and the full packages/tests tsc do not exercise." Verified by tsc probe: head gives unknown and the merge-base Overwrite gives {a:1}. The item states only that the behaviour changed and names no failing caller or user-visible consequence; it even says existing callers don't exercise it. It concerns TWith being unknown/any, not TType being any (GT-j2) or unconstrained generic middleware params dropping context (GT-j1), so it recovers neither. An accurate observation below the finding threshold.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "The new test file is named issue-5020 although the PR is #5017 ... and the fixture voidWithMiddleware is never asserted." Both facts are true: the file is packages/tests/server/regression/issue-5020-inference-middleware.test.ts, the packet thread cites issue-5017-inference-middleware.test.ts, and voidWithMiddleware has no expectTypeOf. The naming point is hygiene. The missing assertion is listed in the register's non_defects ("No test covers voidWithMiddleware's inferred input" is a coverage gap, not a defect).

## att-007 (review-code-sonnet-high), blind-b01404

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The `: TType` arm of `TWith extends any ? TWith : TType` in the non-object branch of `Overwrite` is unreachable, since `X extends any` is true for every non-never `TWith` and distributes to never otherwise." Accurate, and confirmed by tsc probe (Overwrite<string, never> = never). This is a dead-code observation with no consequence, and it matches the register's non_defects on the `TWith extends any` check and the redundant branches. It recovers neither defect.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "The regression test declares `voidWithMiddleware` on the router but makes no assertion about its input or output types, so that case only guards against compile errors." True (issue-5020-inference-middleware.test.ts:13-17 has no expectTypeOf for it). The register's non_defects explicitly rule this a coverage gap, not a defect.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "Some non-object `TWith` cases now replace rather than merge: `Overwrite<{a:1}, {b:2}|undefined>` is `{a:1;b:2}|undefined` (was `{a:1}|{a:1;b:2}`) and `Overwrite<{a:1}, unknown>` is `unknown` (was `{a:1}`); the whole `packages/tests` project still type-checks." Both before/after results were confirmed with tsc in clone-work/g2/probe.ts. The item names no broken caller or consequence and reports that the tests still type-check, so it is an accurate behaviour-change observation. It doesn't identify GT-j1's unconstrained generic middleware context drop or GT-j2's any-context union.

## att-012 (review-code-sonnet-high), blind-7b128b

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error False, group none. Quote: "Remove the unreachable `TType` branch and fix the never comment ... `: TType` never executes ... `Overwrite<string, never>` is `never`, which misleads maintainers about the contract." Accurate: in clone/packages/server/src/core/internals/utils.ts the non-object arm `TWith extends any ? TWith : TType` distributes over the naked TWith, so never gives never; a tsc probe in clone-work/g2 confirms Overwrite<string, never> = never. But this is dead-branch cleanup and a doc-comment wording fix; the register's non_defects rule that the `TWith extends any` check and the duplicated branches are working as intended or a factoring preference. No behavioural consequence is claimed. It names neither GT-j1 (dropped context with unconstrained generic middleware params) nor GT-j2 (any context turned into a union).

## New candidates

None.
