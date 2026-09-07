# Target

- Repository: `trpc/trpc`
- Pull request: [#5017](https://github.com/trpc/trpc/pull/5017) — "fix(server): inference fix for inputs with middleware"
- Head SHA: `7dc04a7e94654dfad6ef1289dfe01a0a206fff3b`
- Merge-base: `2abb2d5cd19740be37272dac6ad7fdd36244ae54`
- Merged: 2023-11-10T10:08:08Z
- Files changed: `packages/server/src/core/internals/utils.ts` (+17/-3) and a new test, `packages/tests/server/regression/issue-5020-inference-middleware.test.ts` (+40).
- Only production-code change: the `@internal` conditional type `Overwrite<TType, TWith>` in `packages/server/src/core/internals/utils.ts`.

# Verdict

1 material defect.

# Defect register

## GT-j1 — `Overwrite`'s new object-gate drops inferred context/input properties when a middleware's params are built from an unconstrained generic type parameter

**Location (at pinned head `7dc04a7e9`):**
`packages/server/src/core/internals/utils.ts:11-30` (the `Overwrite<TType, TWith>` definition itself), consumed unmodified at:
- `packages/server/src/core/middleware.ts:65,81,103,136` (`MiddlewareBuilder.unstable_pipe`, `CreateMiddlewareReturnInput`, `MiddlewareFunction`'s `ctx` field)
- `packages/server/src/core/internals/procedureBuilder.ts:38,41,44` (`CreateProcedureReturnInput`'s `_ctx_out`/`_input_in`/`_input_out`)

Neither `middleware.ts` nor `procedureBuilder.ts` is touched by this diff — the diff is `utils.ts` (+17/-3) and a new test file only.

**Expected behaviour / contract:**
tRPC's documented middleware-composition contract is that each `.use()` in a procedure/middleware chain additively extends the inferred `ctx` type — a property added by an earlier middleware must still be present in the type seen by a later middleware/resolver. `Overwrite<TType, TWith>` is the type-level primitive this composition is built on (`_ctx_out: Overwrite<TPrev['_ctx_out'], TNext['_ctx_out']>` etc.). The PR's own doc-comment states the intended behaviour: "Only overwrites properties when both types are objects... Otherwise it will overwrite the entire TType with TWith, unless TWith is never."

**The change:** before the PR, `Overwrite` was
```ts
export type Overwrite<TType, TWith> = TType extends any
  ? TWith extends any
    ? { [K in keyof TType | keyof TWith]: ... }
    : never
  : never;
```
i.e. a single distributive conditional keyed on `TType`/`TWith extends any` (true for any non-`never` type), always doing the key-wise merge. The PR changes the *gate* to `TType extends object ? (TWith extends object ? {merge} : TWith) : (TType extends any ? TWith : TType)`. This fixes the case the PR targets (`Overwrite<string, string>` no longer iterates over `String.prototype` keys like `charCodeAt`), but it adds a second, separately-distributing conditional (`TType extends object`) ahead of the existing one. When `TType`/`TWith` are indexed-access expressions into a still-generic `ProcedureParams` type parameter (as at all four call sites above), TS's handling of distributive conditionals over such not-yet-resolved types differs across the old vs. new gate shape, and the merged type TS computes for the composed middleware can lose properties that were present in the type before the offending middleware.

**Trigger:** compose two middlewares where the first middleware's context-extension type is produced through a *generic function that returns a naked, unconstrained type parameter* (not `T extends object`), then pipe a second middleware/procedure on top and inspect the final inferred context. Concretely (the shape reported in issue #5037 and encoded as the regression test added by the fix PR #5039, `packages/tests/server/regression/issue-5037-context-inference.test.ts`):
```ts
function sentryTrpcMiddleware(_options: any) {
  return function <T>({ path, type, next, rawInput }: TrpcMiddlewareArguments<T>): T {
    return null as any as T;
  };
}
const t = initTRPC.context<{ some: 'prop' }>().create();
const baseMiddleware = t.middleware(sentryTrpcMiddleware({ foo: 'bar' }));
const someMiddleware = t.middleware(async (opts) => opts.next({ ctx: { object: { a: 'b' } } }));
const baseProcedure = t.procedure.use(baseMiddleware);
const bazQuxProcedure = baseProcedure.use(someMiddleware);
```

**Demonstrated consequence (reproduced myself, see Reproduction):** at the PR head, `tsc` fails to compile this composition with
```
error TS2345: ... Property 'some' is missing in type '{}' but required in type '{ some: "prop"; }'.
```
i.e. the base context property `some: 'prop'` is silently dropped from the inferred/checked `ctx` type once a generically-constructed middleware sits in the pipeline. This is not a hypothetical: it shipped as `@trpc/server@10.43.3`, a real user hit a structurally-identical compile break upgrading from 10.43.2→10.43.3 in production code using a generic `makeTRPC<T>()`/`Context<T>` factory (issue #5037, filed 2023-11-14, four days after merge), and the maintainer who wrote this PR authored the follow-up fix PR #5039 four days later, whose body states plainly: "using generics to construct either tRPC instances or tRPC middlewares using a type parameter that is not constrained to `object` ... causes TS to infer incompatible types for middleware builders after `Overwrite` was changed to only do the key-wise merge on types that extend `object`."

**Required corrective outcome:** any sufficient fix must restore both properties simultaneously — (a) `Overwrite<string,string>`-style primitive/primitive overwrites must not iterate the source type's prototype keys (the PR's own promised behaviour), **and** (b) composing middlewares/procedures whose `ProcedureParams` fields are (partially) derived from an unconstrained generic type parameter must not drop previously-established context/input properties from the inferred type. It need not be shaped as the eventual patch (PR #5039's single-conditional `TWith extends any ? (TType extends object ? {merge} : TWith) : never` plus `WithoutIndexSignature` handling) — any `Overwrite` formulation (or call-site change) that keeps both properties holds, verified against the two regression tests `issue-5020-inference-middleware.test.ts` and `issue-5037-context-inference.test.ts` (the latter did not exist until #5039, but its scenario is a valid acceptance test regardless of which commit introduces it).

**Is this the PR's own promised change, or unintended?** Unintended. The PR's promised, tested, and reviewed behaviour change is exclusively about `Overwrite<primitive, primitive>` (issue #5020, `strWithMiddleware`/`voidWithMiddleware`). The generic-factory-built-middleware regression is a side effect on an input class (naked/unconstrained generic type parameters flowing into `Overwrite`'s `TType`/`TWith`) that is never mentioned, tested, or discussed anywhere in the PR's review record.

# Reproduction

Methodology: the target commit's `package.json` pins `node ^18`/`pnpm` for a full workspace install, and the working machine has a newer toolchain than 2023; rather than fight a full monorepo install, I built a minimal standalone harness that type-checks the real, unmodified `packages/server/src` (all files, `adapters/` excluded — it only fails on absent runtime deps like `express`/`fastify`/`aws-lambda`, unrelated to this diff) against the two regression tests, using `typescript@5.2.2` (the exact version reported in issue #5037) and `vitest@0.34.6` (for the `expectTypeOf` global types) via a plain `tsc --noEmit -p tsconfig.base.json`. Harness lives in `/tmp/qual137/repro` (`server-src/` = copy of `packages/server/src` at the commit under test; `test/` = the regression test file(s)). Worktrees: `/tmp/qual137/work/at-base` (2abb2d5c), `/tmp/qual137/work/at-head` (7dc04a7e9), `/tmp/qual137/work/at-5039fix` (de8589879).

| Commit | Test | Command | Exit | Result | Duration |
|---|---|---|---|---|---|
| merge-base `2abb2d5c` | `issue-5020-inference-middleware.test.ts` (copied in manually — file didn't exist yet) | `tsc -p tsconfig.base.json` | 2 | **FAILS**: `TS2554: Expected 1 arguments, but got 0` on both `expectTypeOf<Input>()`/`expectTypeOf<Output>()` calls for `strWithMiddleware` — a downstream symptom of the pre-fix `Overwrite<string,string>` mangling the inferred type into something `expect-type`'s overload resolution treats as callable. Confirms the bug PR #5017 targets (issue #5020) was real and present before this PR. | 0.85s |
| head `7dc04a7e9` | `issue-5020-inference-middleware.test.ts` | `tsc -p tsconfig.base.json` | 0 | **PASSES** — the PR's promised fix works. | ~0.7s |
| merge-base `2abb2d5c` | `issue-5037-context-inference.test.ts` (copied in manually — file didn't exist until #5039) | `tsc -p tsconfig.base.json` | 0 | **PASSES** — the GT-j1 regression is not present before this PR. | 0.85s |
| head `7dc04a7e9` | `issue-5037-context-inference.test.ts` | `tsc -p tsconfig.base.json` | 2 | **FAILS**: `TS2345 ... Property 'some' is missing in type '{}' but required in type '{ some: "prop"; }'` — GT-j1, reproduced directly. | 1.13s |
| `de8589879` (#5039, the fix) | both tests together | `tsc -p tsconfig.base.json` | 0 | **PASSES** — confirms the required corrective outcome is achievable and was in fact delivered a week later. | ~1s |

Raw logs: `/tmp/qual137/repro/out2-atbase.txt`, `/tmp/qual137/repro/out2-athead.txt`, `/tmp/qual137/repro/out-atbase.txt`, `/tmp/qual137/repro/out-athead.txt`, `/tmp/qual137/repro/out-fix5039.txt`.

I did not find, and did not go looking for, a *runtime* (non-type-level) test failure — this whole defect class is a TypeScript inference-only regression; there is no runtime behavior change (the emitted JS for `Overwrite` and its call sites is unaffected — these are `type` aliases, erased at compile time). `vitest --run` (runtime) would pass at every commit in this table; only `tsc --noEmit` distinguishes them. This matches how trpc's own CI is wired (`test-run:tsc` is a separate script from `test-run:vitest`).

# Not ground truth

- **"The duplicated `TWith extends any ? TWith : never` / `TWith extends any ? TWith : TType` branches are redundant/should be factored"** — a real code-smell (KATT/jussisaurio's own back-and-forth in review, see Preexisting hints, essentially converges on a cleaner shape later in #5039), but a factoring preference, not a correctness defect with a demonstrated consequence.
- **"Index-signature keys (`[x: string]: unknown`) get collapsed/lost by the `[K in keyof TType | keyof TWith]` mapped type"** — true of `Overwrite`, and it is exactly what issue #5034 / PR #5035 fixed via `WithoutIndexSignature`, bundled together with the GT-j1 fix in #5039. But this mapped-type shape (`[K in keyof TType | keyof TWith]: K extends keyof TWith ? TWith[K] : ...`) is byte-for-byte the same before and after this PR (compare the pre-image: `TType extends any ? TWith extends any ? { [K in keyof TType | keyof TWith]: ... } : never : never` — identical inner mapped type). This PR only changed the *outer gate*, not the mapped type body, so the index-signature behavior is unchanged by this diff and is **not** attributable to it — it is a pre-existing defect in `Overwrite` that predates the merge-base.
- **"`TWith extends any` is always true so that check is dead code"** — true for every `TWith` except `never` itself, which is precisely its documented purpose ("unless TWith is never"); working as intended, not a defect.
- **"The type is more deeply nested / could be slower for the compiler"** — plausible-sounding, no compile-time-perf measurement exists anywhere in the record and none was found; unsubstantiated.
- **"No test covers `voidWithMiddleware`'s inferred input"** — the added test file's router includes a `voidWithMiddleware` procedure but only asserts on `str`/`strWithMiddleware`; a real test-coverage gap in the PR's own regression test, but not a defect in the shipped type — I did not find any indication `voidWithMiddleware`'s inference was ever wrong.

# Preexisting hints

Yes — reviewers came close to the general shape of the fix, but nobody flagged the specific naked-generic-type-parameter regression (GT-j1); it was discovered post-merge via real user reports, not during review.

- KATT (2023-11-09T11:16:53Z, on the then-draft test file): *"This is the one that's failing"* — flags that the `strWithMiddleware` case is broken pre-fix (this is issue #5020, not GT-j1).
- jussisaurio (2023-11-09T17:30:37Z): *"I think this happens because of `Overwrite<string, string>` which results in the garbled nonsense you're seeing in the inferred type. This part is obviously the culprit -- it needs some handling to only overwrite in cases that make sense."* — correctly diagnoses issue #5020's cause; says nothing about generic-derived `TType`/`TWith`.
- jussisaurio (2023-11-09T17:36:20Z): proposes two candidate pseudocode designs for `Overwrite`, the second of which ("If they are both objects, overwrite A's keys with B; If both extend any, return B; Otherwise return the one that extends any, or if neither: never") is structurally close to what #5039 eventually ships (a *single* outer gate on `TWith`, rather than two nested gates), but this alternative was **not** the one implemented in this PR — the PR implements the first, two-gate ("If TType extends object...") version, which is the one that regresses. The reviewer thread thus contains an unimplemented alternative that likely would have avoided GT-j1, but no one states *why* the chosen version is riskier, and no one mentions unconstrained generics.
- jussisaurio (2023-11-09T17:52:22Z): *"I think it makes more sense for an intuitive meaning of 'Overwrite' so that key-wise overwrite happens when both are objects, and otherwise `TWith` just replaces `TType` entirely."* — settles on the shape that shipped, framed purely in terms of intuitive semantics for concrete types, not generic-parameter distributivity.

No comment in the review record mentions distributive conditional types over naked/unconstrained type parameters, `middleware.ts`, `procedureBuilder.ts`, or generic middleware-factory functions.

# Leakage

A truncated mirror for this evaluation must exclude:
- **Issue #5020** (origin bug fixed by this PR — gives away the PR's intended change) and its body/reproduction.
- **Issue #5037** ("bug: inference errors in middleware and context", 2023-11-14) — the downstream bug report that *is* the evidence for GT-j1.
- **PR #5039** ("fix(server): fix regression introduced by #5017") and all its commits: `c63604e70737e6c838fe00190a12c1f5a2f11aab`, `c57097c1319e5a990efa3551804af7e35c69c03b`, `eec398d69f056007b886b3de2b5c2fd594b10fd7`, `e603b48b7b18bb996266fa479b0ec2edcc281fa9`, `e359fec7e66811d0e43f322b5a1c821dc6203365`, `e79b1f4721082bab3dfb2abedd0514f3e52b6529`, `394be05895d09d3992610c7c5008a3343007f0de`, `a2a14f0fb131bc8f06573a62d18bdd6f920a120b`, and merge commit `de8589879a461dc107402cd2fb1b06919a6c1c69` — its PR body states the diagnosis verbatim.
- The regression test file it adds, `packages/tests/server/regression/issue-5037-context-inference.test.ts`, and its expanded rewrite of `packages/tests/server/regression/issue-5034-input-with-index-signature.test.ts`.
- **Issue #5034** / **PR #5035** (`fix(client+server): avoid losing type information w/ index signatures`) — a related but *not* attributable-to-this-PR defect (see Not ground truth); a mirror should still exclude it since its presence right after #5017 would prime a reviewer to suspect this PR, even though it's a distinct, pre-existing issue.
- Any commit message or PR title containing "5017", "5020", "5034", "5037", or "5039".
- The four inline PR review comments on `issue-5017-inference-middleware.test.ts` (r1387858035, r1388343418, r1388353128, r1388374654) quoted under Preexisting hints.

# Adjudicator's confidence and limits

High confidence in GT-j1: it is corroborated by (a) an independent, blind user bug report (#5037) filed against the shipped release that contains this exact commit, (b) the original author's own post-hoc root-cause analysis in PR #5039 naming this commit, and (c) my own from-scratch reproduction against the pinned head commit's unmodified source, isolating the regression to exactly this diff (fails at head, passes at merge-base, passes again after #5039). I did not rely on GitHub code search (rate-limited) for any of this — all evidence comes from `git log`/`git show` on the local clone, `gh pr/issue view`, and my own `tsc` runs.

Limits:
- My reproduction harness is a partial extraction of `packages/server/src` (adapters excluded) compiled with `typescript@5.2.2`/`vitest@0.34.6` types outside the real pnpm workspace, not trpc's actual CI. I did not run the full `packages/tests` suite (pnpm install of the 2023-era workspace was not attempted against the current toolchain). I consider the risk this introduces a false result low, given the reproduction cleanly reverses between merge-base/head/fix exactly as the primary-source narrative (#5037 → #5039) predicts, and the error text (`Property 'some' is missing in type '{}'`) is a structural match for "a required property goes missing from the inferred type," not an artifact of my harness (the same harness passes cleanly at merge-base and at the #5039 fix commit with no changes other than swapping in `server-src`).
- I did not attempt to give a rigorous, mechanical account of *exactly* which TypeScript distributivity rule produces the drop (i.e., I did not derive it purely from the TS spec) — I established it empirically via bisection across the three commits, which is sufficient for a "material defect with demonstrated consequence" verdict but leaves the precise compiler-internals mechanism as `unresolved` if a reviewer wanted a from-first-principles type-theory proof rather than an empirical one.
- I found no second, independent material defect in this diff; the search surface was the full commit diff (single file, 20 lines) plus every call site of `Overwrite` in `packages/server/src` at head, plus the full PR review record and all GitHub issues/PRs referencing "5017" via the search API (one query, within the 30/min budget).
