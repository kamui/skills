# Scorecard: j-trpc-5017, mapping v1

Register v1 (4c6a1bb5937e), rubric v1, scored at 2026-09-25T20:42:21Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 e3d44f5da9a87513762f94d8b2d5fe960f088be836cc452d4bd5725901a46f56; session 6a8b1251-1976-470f-99b2-730545360076; read audit clean.

## att-038 (claude-builtin-sonnet-high), blind-eb465e

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "`Overwrite<{a:1}, never>` and `Overwrite<string, never>` both evaluate to `never`, not to TType ... Any caller that passes a never `_ctx_out` ... gets `never`." Accurate (scratch tsc), but the merge-base Overwrite also returns never for a never TWith, so the consequence is unchanged behaviour. This is a doc and dead-branch issue.
- item-1: `defect:GT-j1`, fix absent, priority error n/a, group none. Quote: "A non-object TWith now replaces TType wholesale, which changes Overwrite for existing callers such as ctx and `_ctx_out` ... Now `Overwrite<{a:1}, unknown>` gives `unknown` ... Callers include ... `ResolveOptions` and `middleware.ts` ... If any `_ctx_out` or `ctx` is `unknown` ... ctx can now be `unknown` instead of an object. The `Simplify<>` wrappers then produce an unusable ctx type." This names GT-j1's mechanism and its untouched call sites (middleware.ts:65,103,136): an unknown `_ctx_out` wipes ctx to Simplify<unknown> = {}, which is the #5037 failure reproduced in scratch tsc. One side detail is wrong: the claim that the old Overwrite<{a:1}, unknown> gave `{}`. Scratch tsc shows the merge-base preserved `{a:1}` (ctx.user type-checks at base). That does not undo the recovery. No corrective change is proposed, so absent.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "The regression test is named issue-5020 but the PR is #5017, and it does not cover the void-with-middleware case it declares." Naming and coverage observations. The register lists the voidWithMiddleware gap as a non-defect.

## att-039 (claude-builtin-opus-high), blind-5b3543

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-j1`, fix absent, priority error False, group none. Quote: "When the base type is an object and TWith is `unknown` ... the new `TWith extends any ? TWith` branch replaces the whole type instead of keeping it, so a middleware ctx typed `unknown` wipes out the root context type ... `ctx` was `{ user: string | null }` on base but is `{}` on head." This is exactly GT-j1's mechanism. Reproducing #5037's shape with scratch tsc shows the generic middleware contributes `_ctx_out: unknown`, and the failure reads `Property 'some' is missing in type '{}'`, i.e. Overwrite<ctx, unknown> -> unknown -> Simplify -> {}. The item's own example also reproduces: TS2339 'user' on '{}' at head, passes with the merge-base Overwrite. No corrective change is proposed (Fix: —, and the Consequence line proposes none), so absent.
- item-1: `non-material`, fix n/a, priority error False, group none. Quote: "arrays, tuples, Date, Map and functions ... still go through the key-by-key mapped type ... the output is identical on base, so the fix leaves these unfixed." Confirmed by scratch tsc: the array input is garbled identically at base and head. The item concedes this is pre-existing and not introduced by the diff, so it is an incompleteness remark below the finding threshold.
- item-2: `non-material`, fix n/a, priority error False, group none. Quote: "With union inputs, every member of TType is merged with every member of TWith, which creates fake combinations." Scratch tsc confirms the cross-product type for a discriminated-union input after `.use(o=>o.next())`, but the merge-base Overwrite (`TType extends any ? TWith extends any ? ...`) yields the identical four-member union. The behaviour is pre-existing and not attributable to this diff.
- item-3: `non-material`, fix n/a, priority error False, group none. Quote: "Altitude: the underlying problem is that CreateProcedureReturnInput merges TPrev and TNext inputs with a key-merge helper ... Using [FallbackValue] here ... fixes all shapes." A design suggestion about where to fix the #5020 bug. It rests on the pre-existing array/union behaviour and does not identify a defect introduced by the diff.
- item-4: `non-material`, fix n/a, priority error False, group none. Quote: "`Overwrite<string, never>` and `Overwrite<{a:1}, never>` both resolve to `never` ... which contradicts the new doc comment." Accurate (confirmed by scratch tsc), but the merge-base Overwrite also returns never for a never TWith. The consequence ('a middleware whose ctx/input is inferred as never gets never') is unchanged behaviour. This is a doc-wording and dead-branch matter, below threshold.
- item-5: `non-material`, fix n/a, priority error False, group none. Quote: "The test defines `voidWithMiddleware` but never asserts on it ... nothing checks ... the `ctx` merge." A test-coverage observation. The register lists the voidWithMiddleware gap as a non-defect.
- item-6: `non-material`, fix n/a, priority error False, group none. Quote: "Simplification: the nested `TWith extends any ? ... : never` ... branches are redundant." The register's non_defects rule this factoring preference non-material.
- item-7: `non-material`, fix n/a, priority error False, group none. Quote: "The regression test is named after issue 5020, but the PR is #5017." A traceability and naming remark with no effect on behaviour.
- item-8: `non-material`, fix n/a, priority error False, group none. Quote: "Leftover twoslash `// ^?` probe comments (lines 8 and 34) are debugging artifacts." True (test lines 8, 34). Hygiene only.

## att-040 (codex-default), blind-31b320

Verdict 'patch is incorrect'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `defect:GT-j1`, fix partial, priority error False, group none. Quote: "When middleware calls `next({ ctx: condition ? { user } : undefined })`, this branch now makes the downstream context possibly `undefined`, losing the original context properties ... `Overwrite` also powers context inference in `ResolveOptions` and `MiddlewareFunction` ... Keep the replacement behavior for primitive inputs without applying it to context merging." This names GT-j1's mechanism: the new gate's non-object branch (utils.ts:21-23) replaces an object context with a non-object TWith, dropping established ctx properties at the untouched ctx call sites. Verified with scratch tsc: `.use(o => o.next({ ctx: cond ? {u:1} : undefined })).query(({ctx}) => ctx.some)` fails at head (TS18048) and passes with the merge-base Overwrite. The trigger is an undefined union member, not the generic-derived `unknown` of #5037, but it is the same gate and outcome. The proposed change (stop replacing for context merging) would restore dropped context but does not address input properties, which the required outcome also covers. So partial.

## att-041 (review-code-sonnet-high), blind-590982

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The `: TType` fallback ... is unreachable ... Overwrite<string, never> = never." Accurate: a scratch tsc probe confirms Overwrite<{a:1}, never> is never at head. The merge-base Overwrite also yields never for a never TWith, so behaviour is unchanged. What remains is doc-comment wording and dead-branch hygiene, which the register's non_defects treat as not material.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "Arrays and functions are objects, so Overwrite<string[], string[]> still key-maps into a garbled mapped type exactly as before the change." True: scratch tsc shows `.input(z.array(z.string())).use(o=>o.next())` gives the same garbled `{[x:number]:string; [iterator]...}` at both base and head. The item itself says this is pre-existing. The diff did not introduce it, as with the register's index-signature ruling, so it is an incompleteness observation below the finding threshold.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "The regression test declares `voidWithMiddleware` but never asserts on it." True (issue-5020 test lines 13-17). The register's non_defects list this as a coverage gap, not a defect.

## att-080 (claude-builtin-opus-high), blind-6711d3

Verdict 'findings'; completion completed; approved on buggy False; zero recovery False; false clean False.

- item-0: `unresolved`, fix n/a, priority error n/a, group none. NC-1: Quote: "`TType extends object` with TType = `any` splits into both branches, so the merged ctx type becomes a union ... `initTRPC.context<any>()...use(({next}) => next({ctx:{user:1}})).query(({ctx}) => ctx.foo)` now fails with TS2339." Reproduced with scratch tsc: head fails with TS2339 on the union `{user:number} | {[x:string]:any...}`, and the same code with the merge-base Overwrite compiles. The mechanism (any distributing over both branches of the new `extends object` gate) and the trigger (context<any>) differ from GT-j1 (unknown TWith from an unconstrained generic), and the register records no second defect. Needs adjudication as a new candidate.
- item-1: `defect:GT-j1`, fix absent, priority error False, group none. Quote: "When TWith is a union containing a non-object (e.g. `X | undefined`), the non-object member now replaces TType completely ... Likewise Overwrite<{a:1}, undefined> = undefined and Overwrite<{a:1}, unknown> = unknown (both were {a:1})." This names GT-j1's mechanism: a non-object TWith, including unknown, replaces an object TType and drops established properties. Scratch tsc confirms the item's standalone-middleware example (`input` possibly undefined, TS18048, at head; passes with the merge-base Overwrite) and confirms Overwrite<{a:1}, unknown> = unknown at head. The required outcome covers both context and input properties, so an input-side manifestation that states the unknown case leads to the same fix. No change is proposed, so absent.
- item-2: `non-material`, fix n/a, priority error False, group none. Quote: "Arrays, tuples and Date count as `object`, so they still take the key-by-key merge branch and get mangled ... assignability to string[] break." The garbling is real but identical at base (scratch tsc), so it is pre-existing and not introduced by the diff. One sub-claim is refuted: in the same probe the garbled array input is still assignable to string[] (and string[] to it) at both commits. Below threshold as a finding against this PR.
- item-3: `non-material`, fix n/a, priority error False, group none. Quote: "Overwrite is distributive over both TType and TWith, so for union inputs a pass-through `.use()` yields the cross product." Confirmed by scratch tsc, but the merge-base Overwrite produces the identical four-member union. Pre-existing and not attributable to this diff.
- item-4: `non-material`, fix n/a, priority error False, group none. Quote: "Altitude: `.use()` only passes input through ... The root fix is to skip Overwrite when TNext's input equals or extends TPrev's." A design recommendation that points back to the item's other findings. It identifies no new defect of its own.
- item-5: `non-material`, fix n/a, priority error False, group none. Quote: "The `: TType` branch is dead code ... Overwrite<X, never> actually resolves to never." Accurate (scratch tsc), but the merge-base Overwrite also yields never, so the 'ctx collapses to never' consequence is unchanged behaviour. This is doc wording and dead-branch hygiene.
- item-6: `false-finding`, fix n/a, priority error n/a, group none. Quote: "`t.procedure.input(z.string()).use(standaloneMiddleware<{input:{foo:string}}>)` would type the procedure input as `{foo:string}` ... The mismatch goes unreported." Refuted by scratch tsc: that exact `.use(mw)` call is rejected with TS2345 (MiddlewareBuilder<... {foo:string}> not assignable to one expecting `_input_in: string`) at both head and base. The mismatch is reported.
- item-7: `non-material`, fix n/a, priority error False, group none. Quote: "`voidWithMiddleware` is defined but never asserted, and the test only covers `string`." A test-coverage observation. The register lists the voidWithMiddleware gap as a non-defect.
- item-8: `non-material`, fix n/a, priority error False, group none. Quote: "The regression file is named for issue 5020, but the PR ... [is] #5017 ... Leftover twoslash `// ^?` markers." Naming and hygiene only.

## att-081 (codex-default), blind-b2b28c

Verdict 'patch is correct'; completion completed; approved on buggy True; zero recovery True; false clean True.

(no items)

## att-082 (review-code-sonnet-high), blind-18c649

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

(no items)

## att-083 (claude-builtin-sonnet-high), blind-7acab7

Verdict 'findings'; completion completed; approved on buggy False; zero recovery True; false clean False.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "`Overwrite<{a:1}, never>` and `Overwrite<string, never>` both evaluate to `never`. The `: TType` fallback in the last branch is unreachable." Accurate (scratch tsc), but the merge-base also yields never for a never TWith, so there is no behavioural change. This is doc wording and redundancy, matching the register's non-defect on the duplicated branches.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "The `object` check counts arrays, functions and other built-in object types, so those still go through the key-by-key mapped type." True, but scratch tsc shows the same garbled array input at base. Pre-existing incompleteness, not introduced by the diff.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "The regression test file is named for issue 5020 ... declares `voidWithMiddleware` and never asserts on it." Naming, coverage and hygiene. The register lists the voidWithMiddleware gap as a non-defect.

## New candidates

### NC-1

- Claim: With `initTRPC.context<any>()`, the new `TType extends object` gate distributes `any` over both branches, so Overwrite<any, {user:1}> becomes a union and a middleware-extended ctx rejects previously allowed arbitrary property access (TS2339).
- Evidence: Scratch tsc in clone-work/probe: `const t2 = initTRPC.context<any>().create(); t2.procedure.use(({next}) => next({ctx:{user:1}})).query(({ctx}) => ctx.foo)` errors at head with TS2339 'Property foo does not exist on type { user: number; } | { [x: string]: any; ... }'. The same code compiled against a copy of packages/server/src with the merge-base utils.ts compiles cleanly.
- Confidence: high that the type-level regression exists at head; materiality depends on how common context<any> is
- Would settle: Adjudicator confirmation that a context<any> regression is a separate material defect of this PR (not a GT-j1 manifestation), e.g. by checking whether #5039's fix or later issues addressed it and running the same tsc probe at the fix commit.
- Items: att-080 item-0 (blind-6711d3 item 1)
