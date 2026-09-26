# Scorecard: j-trpc-5017, mapping v2

Register v3 (3404ee4026d5), rubric v1, scored at 2026-09-26T10:59:14Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 b0c4c3e3d31a4026872405f6d81b612fe94ef868fcf340a94af3f8a5d17a3537; session c210fa39-8d50-4f3d-ad87-c047ceb5b112; read audit clean; re-grade for GT-j3 alone: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 d2f7a31cce8bed582d21b13dc240e2d4c4f88369271b599eab773ce6999b0bd7; session 123fa0f4-4b13-4520-8c98-cb5a085178ca; read audit clean; rulings sha256 adf13cce436333190fd92b8fa33cf5a151a688e642f8065dd7eba598e4719dd3.

## att-001 (review-code-sonnet-high), blind-39cbab

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The trailing `: TType` branch of Overwrite is unreachable because the conditional on TWith is distributive, so Overwrite<string, never> is never, not string; the doc comment's 'unless TWith is never' does not describe a fallback." True: utils.ts:25-29 `TWith extends any ? TWith : TType` distributes over never and yields never, and every other TWith satisfies `extends any`; my scratch tsc probe confirms Overwrite<{a:1}, never> is never at both merge-base and head. This is doc/dead-branch hygiene with no demonstrated consequence, matching the register non_defects on the redundant branches and on `TWith extends any` being intended. Neither GT-j1 nor GT-j2.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "The new regression test declares voidWithMiddleware but asserts nothing about it, and keeps `// ^?` twoslash markers." Accurate (issue-5020-inference-middleware.test.ts:13-17, 8, 34), but the register's non_defects rule this a test-coverage gap, not a defect in the shipped type. Stray markers are hygiene.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "Object/object merging of array types still yields a mangled key-mapped type, as at the merge-base." The item itself says the behaviour is unchanged from the merge-base: the mapped-type body is byte-identical before and after the diff (register non_defects on the mapped-type body). My scratch probe shows Overwrite<string[], string[]> is still mutually assignable with string[] at base and head, so no consequence is shown. It is a pre-existing observation and not attributable to this PR.

## att-006 (review-code-sonnet-high), blind-a49f89

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery False; false clean False.

- item-0: `defect:GT-j3`, fix absent, priority error n/a, group none. regrade: Quote: "For an object `TType` and a non-object `TWith` (`undefined`, `unknown`, `T | undefined`), `Overwrite` now returns `TWith` where the base returned an object shaped like `TType`" and "`Overwrite<{a:1}, undefined>` was `{ a: 1 }` at base, `undefined` at head; `next({ ctx: cond ? {a:1} : undefined })` types ctx as `{ user; a } | undefined`." This names GT-j3's exact mechanism: the object-TType/non-object-TWith branch returns TWith. It also gives the manifestation, a conditional-undefined ctx override widening downstream ctx to possibly undefined, and contrasts it with the base's object-preserving result, which implies the required outcome of keeping the incoming context's properties. It clears the recovery bar. Fix is "—" and no change is proposed anywhere in the item, so fix_sufficiency is absent.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "The `: TType` fallback in the non-object branch is unreachable because `TWith extends any` is always true, so `Overwrite<string, never>` and `Overwrite<{a:1}, never>` both evaluate to `never`, which the doc comment's \"unless TWith is never\" does not say." True (scratch tsc confirms never at base and head), but it is doc/dead-branch hygiene. The register non_defects cover both the redundant branches and `TWith extends any` being intended for never. No consequence.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "`voidWithMiddleware` in the added test is declared but never asserted, and the test keeps `// ^?` twoslash markers." Accurate, but the register non_defects treat this as a test-coverage gap only, and the markers are hygiene.

## att-011 (review-code-sonnet-high), blind-42e8c9

Verdict 'Changes Requested'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-j2`, fix partial, priority error False, group none. Quote: "`initTRPC.context<any>().create()`, then `t.procedure.use((opts) => opts.next({ ctx: { foo: 1 } })).query(({ ctx }) => ctx.user.id)` ... `any extends object` takes both conditional branches, so `Overwrite<any, {foo: number}>` becomes `{foo: number} | {[x: string]: any}`. `ctx.user` compiles at the merge-base but fails at head with TS2339." This matches GT-j2's trigger (an any root context plus a ctx-extending middleware), its mechanism (the new `TType extends object` gate splits on any) and its consequence (TS2339 on a property the middleware did not add, compiling at the merge-base). Fix: "return `TType` when it is `any`: `0 extends 1 & TType ? TType : ...`". This restores compilation, but it turns ctx into bare `any`, so the added key `foo` loses its type. GT-j2's required outcome is a type that allows arbitrary access *while typing the added keys* ({ [x: string]: any; user: number }), so the fix is partial.
- item-1: `non-material`, fix n/a, priority error False, group none. Quote: "`TWith extends any ? TWith : TType` can never take `TType` ... For `TWith = never` the result is `never` (probe: `Overwrite<{a: 1}, never>` is `never`), not `TType`, so the doc suggests behavior the type does not have." True: my scratch tsc confirms never at both base and head. The proposed collapse is the factoring preference the register lists in non_defects (redundant `TWith extends any` branches), and the doc wording is hygiene. No behavioural consequence.
- item-2: `non-material`, fix n/a, priority error False, group none. Quote: "The regression test declares `voidWithMiddleware` ... but only `str` and `strWithMiddleware` are asserted." Accurate, but the register non_defects rule the missing voidWithMiddleware coverage a test gap with no indication inference is wrong, so it is below the finding threshold.
- item-3: `non-material`, fix n/a, priority error n/a, group none. Quote: "Arrays and functions still take the key-merge branch because they extend `object`, whereas the runtime input middleware only merges plain objects; the array case is unchanged from the merge-base." The isPlainObject guard is at middleware.ts:243 as cited, and the item itself calls this unchanged from the merge-base. The mapped-type body is byte-identical before and after (register non_defects), so this is a pre-existing observation not attributable to the PR, and no consequence is asserted.

## att-016 (review-code-sonnet-high), blind-c69ec0

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The `: TType` fallback in the second branch of `Overwrite` is unreachable, so `Overwrite<X, never>` resolves to `never` rather than `X`, which the doc comment's \"unless TWith is never\" leaves ambiguous." True (utils.ts:25-29, and scratch tsc gives never at base and head), but it is doc ambiguity and a dead branch with no demonstrated consequence, covered by the register non_defects on the redundant `TWith extends any` branches. It does not touch GT-j1 or GT-j2.

## Changes from mapping v1

Reason: The independent adjudicator (A1) ruled NC-1 a new material defect, GT-j3 in register v3; the blind re-grade R1 for GT-j3 found one recovery, the NC-1 item.

- att-006 item-0: `unresolved`, fix n/a, priority error n/a became `defect:GT-j3`, fix absent, priority error n/a: the re-grade recovers GT-j3.
- att-006 review level: zero_recovery True became False.
- att-006 review level: false_clean True became False.
