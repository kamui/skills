# Rulings: trpc/trpc#5017 (register v2)

## NC-1: material (new defect)

**Claim.** Overwrite's new non-object branch replaces an object context with a non-object `TWith` such as `undefined`. As a result, `next({ ctx: cond ? {...} : undefined })` makes the downstream ctx possibly undefined, even though the runtime never produces an undefined ctx.

### 1. Is it true at the head? Yes. At the merge-base? No.

Setup: scratch copies only. The clone was not modified; `git status --short` was empty afterwards and HEAD was `7dc04a7e`.

```sh
cd clone
for r in main:base review-head:head; do ref=${r%%:*}; d=${r##*:}; mkdir -p ../clone-work/$d \
  && git archive $ref packages/server/src | tar -x -C ../clone-work/$d; done
# third tree: head with #5039's fix (de858987) utils.ts + types.ts
cp -r ../clone-work/head ../clone-work/fix
curl -sSfL https://raw.githubusercontent.com/trpc/trpc/de858987/packages/server/src/types.ts -o ../clone-work/fix/packages/server/src/types.ts
curl -sSfL https://raw.githubusercontent.com/trpc/trpc/de858987/packages/server/src/core/internals/utils.ts -o ../clone-work/fix/packages/server/src/core/internals/utils.ts
# each tree: tsconfig.probe.json {strict, noEmit, es2020, moduleResolution node, skipLibCheck, types: [], files: [probe.ts]}
(cd ../clone-work/$d && ../../clone/packages/tests/node_modules/.bin/tsc -p tsconfig.probe.json)   # tsc 5.1.3
```

`probe.ts`, where the root context is `initTRPC.context<{ user: { id: number } }>().create()`:

| line | case |
|---|---|
| 8 | `const o1: Overwrite<{a:1}, undefined> = { a: 1 }` |
| 15 | `.use(o => o.next({ ctx: cond ? { a: 1 } : undefined })).query(({ctx}) => ctx.user.id)` |
| 20 | control: `next({ ctx: { a: 1 } })`, reads `ctx.user.id + ctx.a` |
| 25 | control: `next({ ctx: cond ? { a: 1 } : {} })` |
| 30 | `next({ ctx: undefined })` |
| 36 | `next({ ctx: extra })`, where `extra: { a: number } \| undefined` |
| 41 | `next({ ctx: cond ? { a: 1 } : null })` |
| 45 | reusable `t.middleware(o => o.next({ ctx: cond ? { a: 1 } : undefined }))` |

Probe-file output:

```
== base
(no probe errors)
== head
probe.ts(8,14): error TS2322: Type '{ a: number; }' is not assignable to type 'undefined'.
probe.ts(15,23): error TS18048: 'ctx' is possibly 'undefined'.
probe.ts(30,23): error TS18048: 'ctx' is possibly 'undefined'.
probe.ts(36,23): error TS18048: 'ctx' is possibly 'undefined'.
probe.ts(41,23): error TS18047: 'ctx' is possibly 'null'.
probe.ts(45,58): error TS18048: 'ctx' is possibly 'undefined'.
== fix (de858987)
(no probe errors)
```

All three trees report the same 6 errors inside `packages/server/src` (TS7017 on `globalThis` indexing, TS2591 `process`). These come from the environment and are not relevant.

Sanity probe (`probe2.ts`): assign `ctx!.user.id` to a `string`, to confirm that ctx is typed rather than `any`.

```
== base
probe2.ts(7,31): error TS2322: Type 'number' is not assignable to type 'string'.
probe2.ts(10,31): error TS2322: Type 'number' is not assignable to type 'string'.
== head
probe2.ts(7,31): error TS2322: Type 'number' is not assignable to type 'string'.
probe2.ts(10,48): error TS2339: Property 'user' does not exist on type 'never'.
== fix
probe2.ts(7,31): error TS2322: Type 'number' is not assignable to type 'string'.
probe2.ts(10,31): error TS2322: Type 'number' is not assignable to type 'string'.
```

At the base and at the fix, ctx is properly typed. At the head, a literal `next({ ctx: undefined })` makes ctx exactly `undefined`.

Runtime: `procedureBuilder.ts:371-374` computes `ctx: nextOpts && 'ctx' in nextOpts ? { ...callOpts.ctx, ...nextOpts.ctx } : callOpts.ctx`. Spreading `undefined` or `null` is a no-op, so the runtime ctx is always the incoming object. The API permits these inputs: `MiddlewareFunction`'s `next` is `<$Context>(opts: { ctx: $Context })`, which is unconstrained.

### 2. Was it introduced by this PR? Yes.

The diff (`git diff main review-head -- packages/server/src`) replaces `TType extends any ? TWith extends any ? {mapped} : never : never` with `TType extends object ? (TWith extends object ? {mapped} : TWith extends any ? TWith : never) : ...`. The `TWith extends object` check distributes over `X | undefined`, and the `undefined` member replaces the whole object. At the base, the mapped type over `keyof TType | keyof undefined` keeps TType's keys.

Published artifacts:

```
$ curl .../@trpc/server/-/server-10.43.3.tgz | tar -xz; sed -n '/export type Overwrite</,/never;/p' dist/core/internals/utils.d.ts
export type Overwrite<TType, TWith> = TType extends object ? TWith extends object ? { ...
$ (10.43.4)
export type Overwrite<TType, TWith> = TWith extends any ? TType extends object ? { [K in keyof WithoutIndexSignature<TType> | ...
```

npm publish times: 10.43.2 on 2023-11-09, 10.43.3 on 2023-11-10T10:19Z, and 10.43.4 on 2023-11-17T12:32Z, which carries #5039. v10.45.2 keeps #5039's shape. Upstream therefore removed this behaviour after 7 days: #5039 always merges key-wise when TType is an object.

### 3. Is it already in the register? No.

- **GT-j1** concerns unconstrained generic type parameters in middleware factories that drop ctx/input properties (#5037). Its required outcome concerns primitive/primitive overwrite and generic-derived params. It says nothing about a concrete nullable `TWith` replacing an object `TType`. #5039's own prose describes a GT-j1-sufficient design ("check whether TWith extends a JS primitive, and if so, wholly replaces it") that would *keep* NC-1, because `undefined` is a primitive. The two claims are therefore independent.
- **GT-j2** concerns `TType = any` taking both branches, which is a different operand and mechanism.
- **The non_defects** (redundant branches, index signatures, `TWith extends any` dead code, compile speed, missing voidWithMiddleware test) are all unrelated.

### 4. Is it material? Yes, as a compatibility break.

- **Trigger:** an object root context plus a middleware whose `next()` ctx argument is or includes `undefined`/`null`. Examples: `cond ? {...} : undefined`, forwarding a `X | undefined` value, `next({ ctx: undefined })`, or `cond ? {...} : null`.
- **What breaks:** tsc fails with TS18048/TS18047 wherever ctx is read. The same code compiled at 10.43.2, so this is a type-level compatibility break in a patch release. The type also contradicts the runtime.
- **Evidence:** my reproduction across the merge-base, the head and the #5039 fix (above), and the upstream reversal in 10.43.4. No downstream report was found. GitHub search for `repo:trpc/trpc "possibly undefined" ctx` in Nov 2023 to Mar 2024 returned 0 results. The 10.43.3 reports are #5037 (GT-j1), #5042 and #5075, and the last two are unrelated. Admitting this on a reproduction is the same bar on which GT-j2 was admitted.
- **Required outcome:** when the incoming context is an object, a non-object (or partly non-object) ctx override must not replace or widen the downstream ctx to that non-object type. The downstream ctx must keep the incoming properties, as the runtime does and as 10.43.2 typed it. This must hold together with GT-j1, GT-j2 and #5020's fix.

### 5. Counter-arguments

- **The usage is rare and unidiomatic, and nobody reported it.** The clone's tests and examples contain no nullable ctx override (Grep found no matches), and issue search found no report. I accept that this lowers the severity below GT-j1, but not that the defect is immaterial. The signature explicitly accepts the input. Idioms like `session && { user }` or forwarding an optional value produce exactly these unions. The failure is deterministic. The 10.43.3 window lasted only 7 days before 10.43.4 changed the behaviour, which explains why there were no reports.
- **The PR's comment documents "overwrite the entire TType with TWith", so this is intended.** That is right for input overwrite, but the same `Overwrite` combines ctx (`middleware.ts:65,103,136`; `procedureBuilder.ts:38`), where the runtime merges rather than replaces. Upstream reversed this behaviour for object `TType` in the next patch release.

**Ruling: material, new defect.**
