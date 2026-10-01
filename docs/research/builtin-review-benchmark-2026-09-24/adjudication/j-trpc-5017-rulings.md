# Rulings: trpc/trpc#5017

## NC-1: material (new defect, not a duplicate of GT-j1)

**Claim.** With an `any` root context, the new `TType extends object` gate in `Overwrite` takes both branches. A middleware-extended ctx then becomes a union that rejects arbitrary property access (TS2339).

### 1. True at head? Yes. Merge-base? Clean.

The head's gate (`packages/server/src/core/internals/utils.ts`):

```ts
export type Overwrite<TType, TWith> = TType extends object
  ? TWith extends object ? { ...merge... } : TWith extends any ? TWith : never
  : TType extends any ? (TWith extends any ? TWith : TType) : never;
```

When `TType` is `any`, a conditional type resolves to the union of both arms. The false arm returns the bare `TWith` (`{ user: number }`), so the whole result is a union. The merge-base's gate was `TType extends any ? ...`, which takes only the true arm for `any` and so produced `{ [x: string]: any; user: number }`.

Setup (all under `clone-work/nc1/`; the clone itself was not touched, and `git status` in the clone is empty at `7dc04a7e`):

```sh
for r in main review-head; do mkdir -p $r && git -C ../../clone archive $r packages/server/src | tar -x -C $r; done
mkdir -p fix && cp -r review-head/packages fix/
curl -sfL https://raw.githubusercontent.com/trpc/trpc/de858987/packages/server/src/core/internals/utils.ts > fix/packages/server/src/core/internals/utils.ts
curl -sfL https://raw.githubusercontent.com/trpc/trpc/de858987/packages/server/src/types.ts > fix/packages/server/src/types.ts
# The compare API head...de858987 shows only utils.ts, types.ts and shared/internal/serialize.ts changed in server/src
# tsconfig.<v>.json: strict, paths @trpc/server -> <v>/packages/server/src, files [probe.ts]
../../clone/packages/tests/node_modules/.bin/tsc -p tsconfig.<v>.json    # tsc 5.1.3
```

`probe.ts` case A:

```ts
const t2 = initTRPC.context<any>().create();
t2.procedure.use(({ next }) => next({ ctx: { user: 1 } })).query(({ ctx }) => ctx.foo);
```

Results (the same environment-only TS7017/TS2591 errors inside the server sources, about `globalThis` and `process` with `types: []`, appear for every variant and are omitted):

- **merge-base (`main`)**: no `probe.ts` errors.
- **head**:
  `probe.ts(7,27): error TS2339: Property 'foo' does not exist on type '{ user: number; } | { [x: string]: any; [x: number]: any; [x: symbol]: any; } | { [x: string]: any; [x: number]: any; [x: symbol]: any; }'.` Case E (`.input(...)` followed by the same middleware) fails the same way at line 30.
- **#5039 fix (de858987)**:
  `probe.ts(7,27): error TS2339: Property 'foo' does not exist on type '{ user: number; } | { user: number; } | { user: number; }'.` Line 30 fails too.

Controls that compile at all three: `context<any>` with no middleware (B), reading the added `ctx.user` (C), an object context with a middleware (D), and `next()` with no ctx override (probe2 F).

A more realistic shape, `probe2.ts` case G: `createContext = async (): Promise<any> => ({})`, then `initTRPC.context<typeof createContext>()`, then an `isAuthed` middleware adding `user`, then a resolver reading `ctx.req.headers`.

- merge-base: clean.
- head: `probe2.ts(8,67): error TS2339: Property 'req' does not exist on type '{ user: { id: number; }; } | { [x: string]: any; ... }'`.
- fix: `probe2.ts(8,67): error TS2339: Property 'req' does not exist on type '{ user: { id: number; }; } | { user: { id: number; }; } | { user: { id: number; }; }'`.

### 2. Introduced by this PR? Yes

The diff only replaced the outer gate of `Overwrite`, and the behaviour flips from clean to error across exactly that change.

### 3. In the register? No

- **GT-j1** has a different trigger: an unconstrained generic type parameter feeding ProcedureParams (issue #5037, Sentry-style middleware factories). Its required outcome is checked by `issue-5037-context-inference.test.ts`, which #5039 satisfies. #5039 does **not** fix this claim: the probe still fails at de858987. A fix sufficient for GT-j1 is therefore not sufficient here, so under the rubric ("same underlying mechanism and required corrective outcome") this is not a duplicate. In #5037 a maintainer did speculate that `any` taking both arms of a conditional might be involved, but the shipped fix left the `any`-context case broken.
- **Non-defects**: the index-signature entry is about the unchanged mapped-type body, not the gate. None of the others apply.

### 4. Material? Yes

- **Trigger**: an `any` root context (`context<any>()` or a createContext returning `any`), a middleware that extends ctx, and a read of any ctx property that middleware did not add.
- **What breaks**: TS2339 compile failure on code that compiled on 10.43.2. That is a type-level compatibility break shipped in the 10.43.3 patch release.
- **Evidence**: my own reproduction above, contrasted across the merge-base, the head and #5039. `TType extends object` survives in v10.45.2 and current `main` (`unstable-core-do-not-import/types.ts`), so it was never corrected upstream. GitHub search (`"initTRPC.context<any>"`, `context<any> middleware`, `"10.43.3"`) found no downstream report beyond #5037.

### 5. Counter-arguments

The strongest case against: `any` context is an opt-out escape hatch, nobody has reported this in about three years, and upstream's own fix and current main keep the gate. That suggests low impact, or tacit acceptance.

I accept that this lowers severity but not materiality. The break is real and reproducible on a public API shape (an auth middleware over an untyped context is common). The rubric accepts the adjudicator's own reproduction as demonstrated consequence. Nothing in the record shows a deliberate design choice: #5039's degenerate `{user}|{user}|{user}` type looks like an unnoticed artifact.
