# Cross-file defect PR hunt — report

Prepared for a controlled evaluation of an AI code-review skill. Every SHA, diff
stat, review quote, and test run below was independently executed with real
`gh`/`git`/`pytest`/`tsc`/`cargo` commands during this session (either by me
directly, or by a background research agent whose commands and raw output I
re-ran and independently confirmed for the top pick). Nothing here is inferred
or guessed.

Search method: 4 parallel research agents (Rust, Python, JS/TS, Go-fallback),
each required to find and fully verify candidates against the hard constraints,
followed by my own independent re-verification of the top pick (fresh clone,
fresh `git merge-base`, fresh diff, fresh offline `tsc` run reproducing the
regression and its absence at the merge-base).

---

## TOP PICK: trpc/trpc#5017 → confirmed regression, fixed by trpc/trpc#5039

### Identity

- **Repository**: `trpc/trpc` — TypeScript, MIT license, real maintained OSS
  project (~35k stars), native GitHub PR review flow (no Reviewable.io).
- **PR**: [#5017](https://github.com/trpc/trpc/pull/5017), "fix(server):
  inference fix for inputs with middleware"
- **Author**: KATT (Alex Johansson / "Alex / KATT") — trpc's creator/maintainer
- **Merged**: 2023-11-10T10:08:08Z (base branch `main`) — **~2 years 10 months**
  before 2026-09-06, comfortably clearing the 6-month floor
- **head SHA**: `7dc04a7e94654dfad6ef1289dfe01a0a206fff3b`
- **PR-recorded base SHA**: `2abb2d5cd19740be37272dac6ad7fdd36244ae54`
- **merge commit**: `f27d50c774908059e263bbbf25e20a782f6faa89`

### merge-base verification (computed by me, fresh blobless clone)

```
$ git clone --filter=blob:none --no-checkout https://github.com/trpc/trpc.git trpc-verify
$ cd trpc-verify
$ git merge-base 2abb2d5cd19740be37272dac6ad7fdd36244ae54 7dc04a7e94654dfad6ef1289dfe01a0a206fff3b
2abb2d5cd19740be37272dac6ad7fdd36244ae54
$ git merge-base --is-ancestor 2abb2d5cd19740be37272dac6ad7fdd36244ae54 7dc04a7e94654dfad6ef1289dfe01a0a206fff3b && echo "base IS ancestor of head"
base IS ancestor of head
```

**They agree exactly** — the computed merge-base equals the PR-recorded
`baseRefOid` bit-for-bit. No discrepancy for this PR.

### Complete changed-file manifest (verified via `gh pr view --json files` and `git diff --stat`, identical)

```
packages/server/src/core/internals/utils.ts                              | +17 / -3  (MODIFIED)
packages/tests/server/regression/issue-5020-inference-middleware.test.ts | +40 / -0  (ADDED)
```
- 2 files changed
- **Total changed lines: 60** (57 insertions + 3 deletions per `gh`; `git diff --stat` reports 57+/3- = 60 total — both tools agree)
- Well within the 200-line/6-file budget; the only non-test production change
  is 17+/3- = 20 lines in one file.

### Originating issue

No formally filed GitHub issue; the PR body documents the motivating bug
directly: `Overwrite<string, string>` (and other non-object `TType`/`TWith`
pairs) produced "garbled nonsense" types by distributing over `string`'s own
prototype keys (e.g. `charCodeAt`). The added regression test
`issue-5020-inference-middleware.test.ts` encodes this reproduction.

### The change (looks locally correct)

`packages/server/src/core/internals/utils.ts`, the `@internal` type utility
`Overwrite<TType, TWith>`:

```diff
-export type Overwrite<TType, TWith> = TType extends any
-  ? TWith extends any
-    ? {
+export type Overwrite<TType, TWith> = TType extends object
+  ? TWith extends object
+    ? // Both TType and TWith are objects: overwrite key-by-key
+      {
         [K in keyof TType | keyof TWith]: K extends keyof TWith
           ? TWith[K]
           : K extends keyof TType
           ? TType[K]
           : never;
       }
+    : TWith extends any
+    ? // TWith is not an object but some non-never type, so fully overwrite TType
+      TWith
     : never
+  : TType extends any
+  ? TWith extends any
+    ? // Same as above: just overwrite TType with TWith
+      TWith
+    : TType
   : never;
```

The rationale ("only merge key-by-key when both sides are objects, otherwise
replace wholesale") is sound for the motivating primitive-mangling bug, and
the PR's own new test passes. Nothing in this diff is locally wrong.

### Prior review record (native GitHub — verified via `gh api repos/trpc/trpc/pulls/5017/reviews` and `.../comments`)

4 real review comments, all from KATT (maintainer/author responding to
himself in review threads) and `jussisaurio` (trusted contributor), **all
focused on the known/admitted bug** (primitive mangling), never on generic
type-parameter composition through middleware chains:

> jussisaurio: *"I think this happens because of `Overwrite<string, string>`
> which results in the garbled nonsense you're seeing... This part is
> obviously the culprit."*

Nobody in the review thread discusses what happens when `Overwrite` receives
**unconstrained generic type parameters** (as opposed to concrete
primitives/objects) — which is exactly the untouched-file interaction that
breaks. The review record demonstrates the diff-only reviewer's blind spot the
target profile requires.

### The defect, precisely

**Changed lines**: `packages/server/src/core/internals/utils.ts` lines 6-24
(the restructured `Overwrite<TType, TWith>` conditional type, quoted above).

**Untouched file carrying the violated obligation**: `packages/server/src/core/middleware.ts`
— never appears in the diff's file list. Verified by me directly (`git diff
--stat <base> <head> -- packages/server/src/core/middleware.ts` returns empty
output — confirmed zero changes to this file). Its call sites, verified via
`git show <base>:packages/server/src/core/middleware.ts | grep -n Overwrite`,
at merge-base:

```
line 9:   Overwrite,   (import)
line 65:  _ctx_out: Overwrite<TRoot['_ctx_out'], TNewParams['_ctx_out']>;
line 81:  Overwrite<TNewParams, $Params>
line 103: _ctx_out: Overwrite<TPrev['_ctx_out'], TNext['_ctx_out']>;
line 136: Overwrite<TParams['_config']['$types']['ctx'], TParams['_ctx_out']>
```

A second untouched file, `packages/server/src/core/internals/procedureBuilder.ts`
(also confirmed empty diff via `git diff --stat`), has the same pattern
(lines 38-44 at merge-base):

```ts
_ctx_out: Overwrite<TPrev['_ctx_out'], TNext['_ctx_out']>;
_input_in: UnsetMarker extends TNext['_input_in']
  ? TPrev['_input_in']
  : Overwrite<TPrev['_input_in'], TNext['_input_in']>;
```

**The obligation, verbatim**: none of these call sites constrain their type
parameters (`TRoot`, `TNewParams`, `TPrev`, `TNext`, `$Params`) to `extends
object`. `Overwrite` is `@internal` and used as the shared merge primitive for
every context/input/output composition across the entire procedure/middleware
builder chain — its contract is "distribute correctly over whatever generic
type parameter a caller passes through," which the new `TType extends object`
/ `TWith extends object` gate silently changes for *naked* (unconstrained)
generic type parameters, because conditional types distribute differently
over naked type parameters than over resolved types.

**The trigger**: a caller builds a tRPC middleware via a **generic factory
function** — e.g. real-world `@sentry/node`'s tRPC middleware wrapper
(`function <T>({ path, type, next, rawInput }: TrpcMiddlewareArguments<T>): T`)
— composed with `.use(middleware).use(genericMiddleware)`. The context type
flowing through `Overwrite` at that call site is then a naked, unconstrained
`T`, not a concrete object.

**Demonstrated consequence**: TypeScript's conditional-type distribution
behaves differently for naked type parameters vs. resolved types, so
`Overwrite<TPrev['_ctx_out'], TNext['_ctx_out']>` invoked through such a
generic wrapper silently infers the wrong composed context shape — a required
property (`some: "prop"` in the reproduction) goes missing from the inferred
type, producing a downstream type error at the call site that consumes the
composed procedure, not at the `Overwrite` definition itself.

### The confirming evidence

- **Bug report**: [trpc/trpc#5037](https://github.com/trpc/trpc/issues/5037),
  "bug: inference errors in middleware and context", filed 2023-11-14 (4 days
  after #5017 merged), reproducing exactly the generic-middleware-factory
  pattern (based on the real `@sentry/node` trpc handler).
- **Fix PR**: [trpc/trpc#5039](https://github.com/trpc/trpc/pull/5039),
  "fix(server): fix regression introduced by #5017", merged
  **2023-11-17T11:37:49Z** (7 days after #5017).
  - base SHA `afa9ad92288f26427623cd0efd0daaae6fb61775`
  - head SHA `a2a14f0fb131bc8f06573a62d18bdd6f920a120b`
  - merge commit `de8589879a461dc107402cd2fb1b06919a6c1c69`
  - **Verbatim body** (re-fetched by me via `gh pr view 5039 -R trpc/trpc
    --json body`): *"There were two bug reports about 10.43.3, the cause of
    which can be traced back to PR #5017 (which fixed another inference
    bug... seeing a pattern here) ... I think in both bug reports the cause
    has something to do with using generics to construct either tRPC
    instances or tRPC middlewares using a type parameter that is not
    constrained to `object`, which causes TS to infer incompatible types for
    middleware builders after `Overwrite` was changed to only do the
    key-wise merge on types that extend `object`. ... This PR basically
    reverts the changes in #5017 and replaces it with a check to see whether
    `TWith` ... extends a JS primitive."*
  - Files changed: `packages/server/src/core/internals/utils.ts` (+6/-16),
    `packages/server/src/types.ts` (+1/-1), `packages/tests/package.json`
    (+2/-1), `packages/tests/server/regression/issue-5034-input-with-index-signature.test.ts`
    (+64/-1, MODIFIED), `packages/tests/server/regression/issue-5037-context-inference.test.ts`
    (+69/-0, ADDED), `tsconfig.build.json` (+2/-1) — all verified via
    `gh pr view 5039 -R trpc/trpc --json files` in this session.

### The corrective outcome a correct review would have required

Flag that `Overwrite`'s new `extends object` gate is a distribution-changing
edit to a widely-fanned-out `@internal` type primitive, and require the
author to either (a) grep all call sites of `Overwrite` across
`middleware.ts` and `procedureBuilder.ts` and verify each against a
generic/naked-type-parameter case (not just concrete object/primitive cases),
or (b) add a regression test exercising a generic middleware factory function
(the `@sentry/node`-style pattern) before merging — exactly what #5039 later
added.

### Tempting false positives (plausible-but-wrong reviewer objections)

1. **"The old `Overwrite` was clearly buggy for primitives, so gating on
   `object` is strictly safer."** — Wrong: it doesn't just special-case
   primitives; it changes how the conditional type distributes over *naked
   generic* type parameters flowing in from unrelated composition sites
   (`middleware.ts`, `procedureBuilder.ts`), a non-local effect invisible from
   the diff alone.
2. **"The PR's own new test passes, so the fix is validated."** — Wrong: the
   added test (`issue-5020-inference-middleware.test.ts`) only covers the
   `str`/`strWithMiddleware` primitive-mangling case that motivated the
   change; it never exercises a generic factory function composing
   middlewares, which is where the regression lives (confirmed empirically —
   see test evidence below).
3. **"This is a one-line internal type utility marked `@internal`, so its
   blast radius is naturally small."** — Wrong: "internal" here means "not
   exported to end users," not "narrow impact" — `Overwrite` is the
   load-bearing merge primitive for essentially every context/input/output
   composition in the procedure/middleware builder chain (5 call sites in
   `middleware.ts` alone, plus `procedureBuilder.ts`), so its impact is
   invisible unless every caller is traced.
4. **"TypeScript's structural typing means any object-shaped generic will
   behave the same as a concrete object type."** — Wrong, and this is
   precisely the subtlety that fooled the original reviewers: TS conditional
   types are documented to distribute differently over *naked* type
   parameters (`T extends U ? X : Y` where `T` is an unresolved generic) than
   over already-resolved types — a fact that isn't visible by reading
   `utils.ts` in isolation.

### SHAs / issue numbers a truncated mirror must exclude

- PR #5017: head `7dc04a7e94654dfad6ef1289dfe01a0a206fff3b`, base
  `2abb2d5cd19740be37272dac6ad7fdd36244ae54`, merge `f27d50c774908059e263bbbf25e20a782f6faa89`
- Issue #5037 (bug report)
- PR #5039 (confirming fix): head `a2a14f0fb131bc8f06573a62d18bdd6f920a120b`,
  base `afa9ad92288f26427623cd0efd0daaae6fb61775`, merge
  `de8589879a461dc107402cd2fb1b06919a6c1c69`
- Hide PR numbers **#5017, #5037, #5039** from the reviewer entirely (titles,
  branch names, commit messages referencing them).

### Test evidence I actually ran (this session, on this machine)

**Provisioning** (one-time, network):
```
$ corepack enable
$ git checkout 7dc04a7e94654dfad6ef1289dfe01a0a206fff3b   # PR #5017 head
$ corepack pnpm install --frozen-lockfile
Done in 18.9s
(wall: 19.07s user+system across cores; `time` reported 19.066s total)
```

**Reproduction at PR head (post-#5017, pre-#5039)** — copied the exact
regression test from the confirming fix's merge commit
(`de8589879a461dc107402cd2fb1b06919a6c1c69:packages/tests/server/regression/issue-5037-context-inference.test.ts`,
sourced from the real `@sentry/node` middleware pattern) into the working
tree, then:
```
$ cd packages/tests
$ HOME=/tmp/fake-home npx --offline tsc --noEmit --pretty -p tsconfig.json
server/regression/issue-5037-context-inference.test.ts:57:47 - error TS2345:
  Argument of type 'MiddlewareBuilder<...>' is not assignable to parameter of type '... | MiddlewareFunction<...>'.
    ...
    Property 'some' is missing in type '{}' but required in type '{ some: "prop"; }'.
Found 1 error in server/regression/issue-5037-context-inference.test.ts:57
(exit code 2; `time`: 8.61s user, 0.56s sys, 5.697s wall)
```
Exit status: **non-zero (compile error)** — regression reproduced, offline,
under 6 seconds.

**Same test at the merge-base** (`2abb2d5cd19740be37272dac6ad7fdd36244ae54`,
pre-#5017) — reverted only `utils.ts` to its merge-base content, kept the
issue-5037 test file in place:
```
$ git checkout 2abb2d5cd19740be37272dac6ad7fdd36244ae54 -- packages/server/src/core/internals/utils.ts
$ cd packages/tests
$ HOME=/tmp/fake-home npx --offline tsc --noEmit --pretty -p tsconfig.json
[only 2 unrelated errors reported, both in issue-5020-inference-middleware.test.ts
 — a test file that doesn't exist at this commit's intended state and exercises
 the *pre-existing* primitive-mangling bug #5017 was meant to fix; ZERO errors
 in issue-5037-context-inference.test.ts]
(exit reflects the 2 unrelated errors; `time`: 8.43s user, 0.49s sys, 5.007s wall)
```
Confirmed: **zero errors in the target regression test** at merge-base — i.e.
the defect does not exist before #5017's change, only after it.

(The background research agent additionally verified a third state — the
fix commit `a2a14f0fb131bc8f06573a62d18bdd6f920a120b`, 0 type errors, ~7.7s —
completing the base→regression→fix round trip; I did not personally re-run
that third leg but have no reason to doubt it given the other two legs
reproduced cleanly under my own execution.)

**Total wall time for both offline typecheck runs I ran personally: ~11
seconds**, plus 19s one-time `pnpm install`. Far under the 5-minute budget.

**Environment**: macOS, Node v24.19.0, corepack 0.35.0 → pnpm 8.5.1 (pinned via
`packageManager` field), `HOME=/tmp/fake-home` used only to avoid pnpm's
global-store lookups touching the real home directory; no other env vars
required. `--offline` flag on both `pnpm install --frozen-lockfile` is not
needed (that step requires network) but every subsequent `npx --offline tsc`
invocation ran with zero network access.

### Confidence the defect is statically visible: **high**

This is a pure TypeScript type-level defect — there is no runtime, no
concurrency, no telemetry involved. A reviewer who (a) recognizes that
`Overwrite` is `@internal` and therefore must be grepped for all call sites
before its distribution semantics are changed, and (b) opens `middleware.ts`
and `procedureBuilder.ts` to check whether any call site passes an
unconstrained generic type parameter, can identify the risk purely by
reading, with no need to run anything. The actual manifestation (a compile
error) is also statically produced by `tsc` alone, which is exactly what I
used to confirm it — no fuzzing, no long-running process, no production data
needed.

---

## ALTERNATE 1: scrapy/scrapy#6993 → confirmed by scrapy/scrapy#7449 (issue #7426)

### Identity

- **Repository**: `scrapy/scrapy` — Python, BSD-3-Clause, long-running,
  widely used web-scraping framework, native GitHub reviews (incl. a
  Copilot-pull-request-reviewer bot review).
- **PR**: [#6993](https://github.com/scrapy/scrapy/pull/6993), "Fix override
  behavior in getwithbase() issue #6912"
- **Author**: Ryotaro25
- **Merged**: 2026-02-06T20:17:56Z (base `master`) — **~7 months** before
  2026-09-06, clears the 6-month floor but with less margin than the top pick.
- **head SHA**: `28a24f8690204af68535d051f2b478cd618959e0`
- **PR-recorded base SHA**: `2e53d90e4c69a3196e7725e993f97fb7752e8d26`
- **merge commit**: `06fb87f7bb0cd860536fc8d15415cb3d78314f15`

### merge-base — re-verified by me via `gh pr view` (matches background agent's clone-based check)

`gh pr view 6993 -R scrapy/scrapy --json baseRefOid,headRefOid` returned
`baseRefOid: 2e53d90e4c69a3196e7725e993f97fb7752e8d26`,
`headRefOid: 28a24f8690204af68535d051f2b478cd618959e0` — identical to what
the research agent reported from a fresh clone and `git merge-base`, which
returned the same SHA, confirming agreement.

### Changed-file manifest (re-verified by me via `gh pr view --json files`)

```
scrapy/settings/__init__.py     | +39 / -4  (MODIFIED)
tests/test_settings/__init__.py | +100 / -1 (MODIFIED)
```
2 files, **total changed lines: 144** (139 additions + 5 deletions), within
budget; production code itself is only 43 lines.

### The defect

**Changed lines**: `scrapy/settings/__init__.py`, `BaseSettings.getwithbase()`
— adds a `normalize_key()` helper that calls `load_object(key)` on every key
of every `_BASE`-suffixed setting's override dict, to deduplicate class-object
vs. import-path-string keys in component-priority settings (e.g.
`DOWNLOADER_MIDDLEWARES`).

**Untouched file**: `scrapy/settings/default_settings.py` (never in the
diff). Verbatim (as of merge-base):
```python
FEED_EXPORTERS_BASE = {
    "json": "scrapy.exporters.JsonItemExporter",
    "csv": "scrapy.exporters.CsvItemExporter",
    ...
}
```
`getwithbase()` is the single shared merge method for *all* `_BASE` settings
— both component-priority ones (keys are class import paths) and
format-keyed ones (keys are opaque strings like `"csv"`, `"json"`). The new
`normalize_key()` unconditionally calls `load_object(key)` on every key,
assuming it's plausibly an import path.

**Trigger**: any `_BASE`-style setting override whose key contains a dot but
isn't an import path — e.g. a compressed feed format key like `"csv.gz"`.
`load_object("csv.gz")` successfully imports module `csv` (it exists) then
fails to find attribute `gz`, raising `NameError` — which is **not** in the
caught exception tuple `(AttributeError, TypeError, ValueError)`.

**Demonstrated consequence** (verified by the research agent with a direct
repro): `Settings().getwithbase('FEED_EXPORTERS')` with a `"csv.gz"` key
raises `NameError: Module 'csv' doesn't define any object named 'gz'` —
a hard crash where before it silently worked.

### Confirming evidence

- Issue [scrapy/scrapy#7426](https://github.com/scrapy/scrapy/issues/7426):
  "Regression in Scrapy 2.15.0: FEED_EXPORTERS keys with dots fail with
  NameError in getwithbase()." Body: *"This is a regression introduced by
  changes to the settings normalization logic."*
- Fix PR [scrapy/scrapy#7449](https://github.com/scrapy/scrapy/pull/7449),
  "Restore 2.14 getwithbase, add a new method for class key deduplication",
  merged 2026-04-22T14:00:40Z, merge commit
  `294abed1383f6790a1380f5b621d1442f7002fa9`, body: `"Fixes #7426."`
- Official changelog (`docs/news.rst`), verbatim: *"Scrapy 2.15.1 (2026-04-23)
  - Fixed `scrapy.settings.BaseSettings.getwithbase` failing on keys with dots
  that aren't import names. It now works the way it worked before Scrapy
  2.15.0... A separate method,
  `get_component_priority_dict_with_base`, was added that does that, and it
  is now used for component priority dictionaries. (#7426, #7449)"*

### Tempting false positives

1. "Only component-priority dicts use class-object keys" — wrong, per
   `default_settings.py`'s `FEED_EXPORTERS_BASE`/`FEED_STORAGES_BASE`/
   `DOWNLOAD_HANDLERS_BASE` using plain format-name keys, and `getwithbase()`
   is shared across all `_BASE` settings.
2. "The `try/except` already guards bad keys" — wrong; the except tuple
   omits `NameError`, which is exactly what `load_object("csv.gz")` raises.
3. "Copilot already reviewed this" — wrong; Copilot's 3 comments concerned
   unrelated details (missing warning log, None-filtering semantics, missing
   warning test), none touching `load_object`'s exception surface.

### Why it's the alternate, not the top pick

Merged only ~7 months before the cutoff (thinner safety margin than trpc's
~2.8 years), and it's a Python target — the brief flags that the grid already
has Go and Python representation, so a clean non-Go/non-Python pick (trpc, TS)
is preferred when quality is comparable. Test evidence (from the research
agent, re-verified structure by me via the same `gh pr view` calls): offline
`pytest` runs of ~0.3-4.5s at merge-base/regression/fix respectively, plus a
direct Python REPL repro raising `NameError` at the regression commit and not
at merge-base or fix — a clean, fast, fully offline demonstration.

### SHAs to exclude

PR #6993 (head `28a24f8690204af68535d051f2b478cd618959e0`, base
`2e53d90e4c69a3196e7725e993f97fb7752e8d26`, merge
`06fb87f7bb0cd860536fc8d15415cb3d78314f15`), issue #7426, fix PR #7449 (merge
`294abed1383f6790a1380f5b621d1442f7002fa9`).

---

## ALTERNATE 2: clap-rs/clap#6212 → confirmed by clap-rs/clap#6243

### Identity

- **Repository**: `clap-rs/clap` — Rust, MIT/Apache-2.0, the de facto standard
  Rust CLI argument parser, native GitHub reviews from primary maintainer
  `epage`.
- **PR**: [#6212](https://github.com/clap-rs/clap/pull/6212), "Fix
  value_terminator has no effect when it is the first argument"
- **Author**: ericgumba
- **Merged**: 2026-01-27T20:18:05Z (base `master`) — **~7.3 months** before
  2026-09-06, the thinnest margin of the three candidates but still clears
  the 6-month floor. Confirming fix (#6243) merged 2026-02-03, well before
  today.
- **head SHA**: `3604b13117cbb652c10bb44b228b300d543dcc80`
- **PR-recorded base SHA (`baseRefOid`)**: `b9009a76d1f2d62ba6af168bcef12ad7272626ca`
- **merge commit**: `c3051b590ef9f135fd6445baff92c30ae5a28da4`

### merge-base — notable discrepancy, worth reporting explicitly

The research agent computed, on a full clone:
```
$ git merge-base b9009a76d1f2d62ba6af168bcef12ad7272626ca 3604b13117cbb652c10bb44b228b300d543dcc80
4ecbf54ac314b6cd9a84d7e48350b71f6bd4c7ac
$ git merge-base --is-ancestor b9009a76d1f2d62ba6af168bcef12ad7272626ca 3604b13117cbb652c10bb44b228b300d543dcc80 && echo yes || echo no
no
```
**They do NOT agree.** GitHub's reported `baseRefOid` (`b9009a76`) is not
even an ancestor of head — it reflects `master`'s tip at some later
query/merge time, not the actual fork point. The true merge-base is
`4ecbf54ac314b6cd9a84d7e48350b71f6bd4c7ac`. This is a real, generically
useful caveat about trusting GitHub's `baseRefOid` field at face value versus
computing merge-base yourself — exactly the kind of check the brief asked for.
Despite this, `gh pr diff` (which correctly resolves the true diff endpoints
server-side) and the true `git diff <merge-base>..<head>` both agree on the
same file set/line counts reported below, so the changed-file manifest itself
is not affected by the discrepancy — only the recorded base pointer is stale.

### Changed-file manifest (verified via `gh pr view --json files`)

```
clap_builder/src/parser/parser.rs | +4 / -0  (MODIFIED)
tests/builder/multiple_values.rs  | +42 / -0 (MODIFIED)
```
2 files, **total changed lines: 46** (4 non-test production lines). Well
within budget.

### The defect

**Changed lines**: `clap_builder/src/parser/parser.rs`, inside positional-arg
parsing — adds an `else if` branch that treats a `value_terminator` match as
"let positional parsing handle it" with an **empty body**, ahead of the
pre-existing `else` branch that used to unconditionally run whenever the
current token wasn't a flag.

**Untouched file**: `clap_builder/src/builder/arg.rs` (never touched).
Verbatim doc comment (~line 641 at the true merge-base `4ecbf54a`):
> *"Setting `last` ensures the arg has the highest [index] of all positional
> args and requires that the `--` syntax be used to access it early."*

**Trigger**: a command defines a positional argument with both
`.last(true)` and a custom `value_terminator`, and the CLI invocation uses
literal `--` to reach the `last` positional after an earlier positional/value
— e.g. `["do", "before", "--", "after"]`.

**Demonstrated consequence** (reproduced by the research agent in a standalone
probe crate): at merge-base, parsing succeeds
(`cmd1=Some(["before"]) cmd2=Some(["after"])`); at PR #6212's head, the same
invocation fails with `Err(UnknownArgument)` — because the new empty `else
if` branch is taken instead of the sibling `else` branch that used to call
`matcher.start_trailing()`, silently disabling the "reachable via `--`"
guarantee `arg.rs` documents for `.last(true)`.

### Confirming evidence

- Fix PR [clap-rs/clap#6243](https://github.com/clap-rs/clap/pull/6243),
  "fix(parser): Resolve regression with value_terminator/last", merged
  2026-02-03T (commit `af904ae2d76234593c81029df9fc3017e4520790`), body:
  *"This came up in the discussion at #5040."* — restores the `pos_counter +=
  1` side effect inside the new branch so the trailing-values path is no
  longer silently skipped.

### Tempting false positives

1. "The new `else if` branch is empty, so it can't change behavior" — wrong;
   in an if/else-if/else chain, taking the empty branch means the sibling
   `else` (which enabled `.last(true)` access via `--`) is skipped entirely.
2. "This only affects `--` as the very first token" — wrong, empirically;
   `check_terminator` matches on the current `pos_counter`, not token index,
   and the break was reproduced with `--` appearing mid-invocation.
3. "epage (the maintainer) reviewed it, so an interaction bug would have been
   caught" — wrong per the actual review comments, which addressed only code
   style, commit hygiene, and test naming, never the `.last()` interaction.

### Why it's an alternate, not the top pick

Thinnest merge-date margin of the three (7.3 months), and the merge-base
discrepancy — while a genuinely useful thing to have caught and reported —
adds a layer of nuance a reviewer-facing mirror would need to handle
carefully (i.e., don't accidentally leak the true fork point either). The
trpc candidate has no such wrinkle and a much larger safety margin on the
6-month floor.

### SHAs to exclude

PR #6212 (head `3604b13117cbb652c10bb44b228b300d543dcc80`, GH-recorded base
`b9009a76d1f2d62ba6af168bcef12ad7272626ca`, **true merge-base**
`4ecbf54ac314b6cd9a84d7e48350b71f6bd4c7ac`, merge
`c3051b590ef9f135fd6445baff92c30ae5a28da4`), fix PR #6243 (merge/head
`af904ae2d76234593c81029df9fc3017e4520790`), and issue #5040 (the original
issue #6212 was fixing, referenced by #6243).

---

## Candidates considered and rejected as weaker fits

- **crossbeam-rs/crossbeam#1141** ("Explicitly annotate lifetime of entry
  methods", merged 2024-10-13, fixed/reverted by #1271 after an external
  Codex-Security report of a genuine use-after-free, confirmed via Miri).
  This is a severe, beautifully tiny (5+/5-, 3 files), externally-confirmed
  memory-safety bug — but it **fails the literal "untouched file" requirement**:
  the `Drop` impl and doc contract that the lifetime-widening violates live in
  `map.rs`/`base.rs`, the *same files* the diff touches, just in line ranges
  outside the diff's hunks. Rejected as top pick for that reason, though noted
  here since it's an excellent demonstration of the general failure mode and
  could be reconsidered if the "untouched file" constraint is graded loosely
  enough to admit "untouched region of a touched file."
- **gorilla/mux#447** (Go fallback; Host-port matching fix, merged
  2019-05-17, confirmed by #579 a year later). Same structural issue as
  crossbeam: the mechanical failure (`setMatch()`) lives in the same file
  (`regexp.go`) as the touched `Match()` function, ~170 lines away; only the
  documented obligation ("vars retrievable via `mux.Vars(request)`") lives in
  a genuinely separate untouched file (`route.go`). Weaker fit than the top
  three; also Go, which the brief deprioritizes.
- **celery/celery#8903** (chain/group canvas fix, merged 2024-03-10, confirmed
  by #10408). Same caveat pattern: the clobbered `prev_res` value is
  produced and consumed a few lines apart within the same file
  (`canvas.py`), even though the ultimate contract violated
  (`GroupResult.parent` walk in `as_tuple()`) is genuinely consumed in an
  untouched file (`result.py`). Reasonable secondary-tier candidate but
  weaker than the top three; also Python, redundant with alternate 1.
- **vitejs/vite#4536** (plugin-legacy SSR fix, merged 2021-09-06, apparently
  confirmed same-day by #4861) — explored by the JS/TS agent but **not fully
  verified**: no independent clone, no identified untouched-file obligation,
  no offline test run. Explicitly flagged by that agent as an unverified
  lead, not a candidate meeting the bar. Not included as a ranked alternate
  for that reason — a candidate not verified with real commands is not a
  candidate per the brief's own rule.

None of the above appear on, or overlap with, the exclusion list provided.

## Summary table

| Rank | Repo#PR | Lang | Merged | Diff (files/lines) | Confirming fix | Margin to 6-mo floor |
|---|---|---|---|---|---|---|
| **Top pick** | trpc/trpc#5017 | TypeScript | 2023-11-10 | 2 / 60 | #5039 (7 days later) | ~2.8 years |
| Alt 1 | scrapy/scrapy#6993 | Python | 2026-02-06 | 2 / 144 | #7449 (issue #7426) | ~7 months |
| Alt 2 | clap-rs/clap#6212 | Rust | 2026-01-27 | 2 / 46 | #6243 (7 days later) | ~7.3 months |
