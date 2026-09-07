# Scorecard — target k (`graphql/graphql-js#1582`)

Ground truth: 1 material defect, **GT-k1** — `GraphQLError-test.js:57-63`, "creates new stack if original error has no stack" no longer exercises the fallback branch because `original` became `new Error('original')` (which already has a `.stack`) instead of a stack-less double.

Verified independently against `/tmp/qual137/transport-check/k`:
- `review-head` diff stat: `5 files changed, 48 insertions(+), 47 deletions(-)` — matches all four reviews' "+48/-47" claim and the packet.
- `src/error/__tests__/GraphQLError-test.js:57-59` at `review-head` reads exactly as the register states: `const original = new Error('original'); const e = new GraphQLError('msg', null, null, null, null, original);` — confirms the defect is real and each review's technical description of it is accurate.
- `src/error/GraphQLError.js:22-100` at `review-head` confirms: `declare class` constructor (line 25) has `nodes?: ... | void | null`; `export function GraphQLError` (line 94) still has `nodes?: ... | void` with no `null`. This asymmetry, raised by three of the four reviews, is real (see "New candidates" below).
- `src/type/definition.js:340-390` confirms `GraphQLList`/`GraphQLNonNull` use the same `declare class` + `export function` idiom, with the function implementation's parameters *fully unannotated* relative to the `declare class` — corroborating that divergence between the two signatures is an established, tolerated pattern in this file, not a novel defect class.
- Packet's "Prior review state" section (single inline comment by `IvanGoncharov` on `GraphQLError.js:25`, PR body empty) matches what every review states as "Issue fit" intent.

No other production or test defect was found in the diff beyond GT-k1; this matches the register's verdict.

---

## Review `blind-06e57d`

**1. Recovered defect IDs:** GT-k1.
> "Impact: The fixture is now `new Error('original')`, which already carries a real `.stack` at construction. `GraphQLError`'s `originalError && originalError.stack` branch copies that stack instead of reaching the `Error.captureStackTrace` fallback the test claims to check (`src/error/GraphQLError.js:195-201`)."

Clears the specificity bar: names the exact file/line, the exact branch taken vs. the branch that should be exercised, and the mechanism (any `new Error()` already has `.stack`). A reader would know exactly what to change.

**2. Missed defect IDs:** none (GT-k1 is the only registered defect).

**3. Fix sufficiency:** `sufficient`.
> "Change: In `src/error/__tests__/GraphQLError-test.js:58`, use an `originalError` without a `.stack` again (a plain object, or an `Error` with `stack` deleted) so the assertion exercises `Error.captureStackTrace`."
Matches both mechanisms the register accepts as sufficient (plain object, or `delete stack`).

**4. Findings not in the register:**
- `[P3] Match the constructor's own nodes type to the fixed declaration`, anchor `GraphQLError.js:25`/fix `:94`. Quote: *"The two declarations of the same `nodes` parameter now disagree: the class declaration accepts `void | null`... but the function's own signature still allows only `void`."* — **true but not material**. Verified real (see source excerpt above), but no demonstrated consequence: `flow check` passes with 0 errors at head per the register's own reproduction, and the sibling `GraphQLList`/`GraphQLNonNull` classes in the same codebase already tolerate exactly this kind of declare-class/function divergence, suggesting it's tolerated idiom rather than a live bug. Labeling it a formal "Finding" (rather than an observation) slightly overstates it, but the assigned priority (`P3`/`consider`, non-blocking) is calibrated low enough that I don't count it as an action error.

**5. Action/severity errors:** none. Both findings are tagged `consider`/non-blocking, appropriate to their evidence.

**6. Questions, observations, hygiene items:** none — no dedicated Observations or Questions section; everything is folded into the two Findings.

**7. Derived status:** "Approved (advisory) — 0 must-fix findings, 2 consider findings." Coverage explicitly declared complete (`coverage=complete` trailer; "Complete merge-base diff reviewed (5 files, +48/−47). Ran flow check on the head (0 errors). Ran the full suite for all four changed test files... (27/27 passing)" — matches the register's own reproduction numbers exactly).

**8. False clean:** No. The review does not claim "no material defects"; it surfaces GT-k1 as a (non-blocking) finding.

**9. Duplicates:** none.

---

## Review `blind-7744c2`

**1. Recovered defect IDs:** GT-k1.
> "Impact: The constructor's `if (originalError && originalError.stack)` branch reuses `originalError.stack` verbatim, so this test (named for the fallback that creates a *new* stack) actually exercises the reuse branch instead; `e.stack === original.stack` holds. A regression in the `Error.captureStackTrace` fallback this test claims to cover would go undetected."

Clears the bar: identifies the wrong branch, the observable symptom (`e.stack === original.stack`), and the coverage consequence.

**2. Missed defect IDs:** none.

**3. Fix sufficiency:** `sufficient`.
> "Change: In `src/error/__tests__/GraphQLError-test.js`, give `original` a double that genuinely lacks `.stack` (e.g. `const original: any = { message: 'original' }`, matching the `: any` cast this same PR already uses in `locatedError-test.js`) instead of `new Error('original')`."
Restores the register's mechanism #1 (plain object without a `stack` property) and additionally anchors the Flow-typing side-constraint to a real precedent already in the diff (`: any` in `locatedError-test.js`). This is sufficient and, unlike the other three reviews' fixes, explicitly addresses how to keep the fixture Flow-clean.

**4. Findings not in the register:** none formalized as Findings — the one non-GT item is placed under Observations (see item 6).

**5. Action/severity errors:** none.

**6. Questions, observations, hygiene items:** 1 observation, 0 questions.
> "The `nodes` constructor parameter gained `| null` only in the ambient `declare class` signature, not in the exported implementation function's own signature, mirroring how `GraphQLList` and `GraphQLNonNull` in `src/type/definition.js` already leave their implementation functions unannotated relative to their `declare class` counterparts."
Verified true (see source excerpt above) and correctly demoted to an observation rather than a blocking finding — this is the most accurate framing of this fact among the four reviews, since it independently supplies the comparator (`GraphQLList`/`GraphQLNonNull`) that supports treating the asymmetry as tolerated idiom rather than a defect. Not answerable-vs-unanswerable in the "question" sense since it's not phrased as a question; as an observation it doesn't change the review's verdict.

**7. Derived status:** "Approved (advisory) — 1 consider finding." Coverage declared complete; also notes "the PR's sole review thread... is already resolved in the reviewed head," correctly avoiding re-flagging the one prior review comment as still open.

**8. False clean:** No.

**9. Duplicates:** none.

---

## Review `blind-a8ddd0`

**1. Recovered defect IDs:** GT-k1.
> "Impact: `original` is now `new Error('original')`, which already has a populated `.stack` in this Node/V8 test environment, so `originalError && originalError.stack` is true and `GraphQLError.js:195`'s reuse branch runs, giving `e.stack === original.stack`. ... the test now silently duplicates 'uses the stack of an original error' instead of exercising `Error.captureStackTrace`'s fallback..."

Clears the bar: precise, cites the exact source line, names the duplicated sibling test, and the missing coverage.

**2. Missed defect IDs:** none.

**3. Fix sufficiency:** `sufficient`.
> "Change: In `src/error/__tests__/GraphQLError-test.js`, construct `original` so it still satisfies the constructor's `Error`-typed parameter but genuinely has no `.stack` (for example an `Error` instance with `stack` deleted or set to `undefined`), and assert `e.stack !== original.stack` so the test again proves the fallback path runs."
Matches the register's mechanism #2 (`delete original.stack`, exactly what PR #4774 later did) and adds a strengthened assertion, which is a bonus, not a requirement. Sufficient.

**4. Findings not in the register:**
- `[P3] Sync the constructor implementation's own type with the widened public signature`, anchor `GraphQLError.js:25`/fix `:94`. Quote: *"The two Flow signatures for the same constructor now disagree about whether `nodes` accepts `null`... A reader trusting the implementation's own type believes `null` is still unsupported, even though it is accepted and handled correctly at runtime."* — **true but not material**, same reasoning as `blind-06e57d`'s equivalent finding: verified real, but `flow check` passes with 0 errors at head and the codebase already tolerates this class of divergence elsewhere (`GraphQLList`/`GraphQLNonNull`). This review explicitly notes "it is accepted and handled correctly at runtime," which is itself evidence the review is not overclaiming consequence — it correctly frames this as a documentation/consistency nit, and the `P3`/`consider` tag is appropriately calibrated.

**5. Action/severity errors:** none.

**6. Questions, observations, hygiene items:** none — no separate Observations/Questions section; the `nodes`-sync item is a formal Finding (see item 4).

**7. Derived status:** "Approved (advisory) — 0 must-fix findings, 2 consider findings." Coverage declared complete, plus an extra verification step not seen in the other three: "A repository-wide grep for other `nodes?:` constructor-type declarations and for `new GraphQLError(` call sites passing `null` found no other location this change should have touched." I did not independently re-run this grep; it is a plausible, low-stakes process claim that doesn't affect any finding's classification. `unresolved` if it needed independent confirmation, but it carries no weight on the scored findings.

**8. False clean:** No.

**9. Duplicates:** none.

---

## Review `blind-ad8fdf`

**1. Recovered defect IDs:** GT-k1.
> "Impact: The test is named for the case where `originalError` has no stack, but with a real `Error` instance that branch (`Error.captureStackTrace`) is never taken; the assertion `expect(e.stack).to.be.a('string')` passes either way, so a future regression in the stack-synthesis branch would go undetected."

Clears the bar: identifies the branch, the assertion's blindness, and the consequence.

**2. Missed defect IDs:** none.

**3. Fix sufficiency:** `sufficient`.
> "Change: In `src/error/__tests__/GraphQLError-test.js`, keep `original` typed as an `Error` but strip its stack (e.g. `delete original.stack;` after construction) so the test still exercises the fallback branch it names."
This is verbatim the mechanism PR #4774 actually used. Sufficient.

**4. Findings not in the register:** none formalized as Findings — the one non-GT item is an Observation (item 6).

**5. Action/severity errors:** none.

**6. Questions, observations, hygiene items:** 1 observation, 0 questions.
> "The constructor's declared public type now accepts `null` for `nodes`, but the same file's implementation function still types the parameter as `void`-only. Evidence: `src/error/GraphQLError.js:25`, `src/error/GraphQLError.js:94`."
Verified true, correctly kept at observation weight (no priority tag, no proposed action), consistent with its low materiality.

**7. Derived status:** "Approved (advisory) — 0 must-fix findings, 1 consider finding." Coverage declared complete; explicitly notes "no repository guidance files present at the merge-base," which matches packet section 7 verbatim.

**8. False clean:** No.

**9. Duplicates:** none.

---

## Cross-review table

| Review | Recovered | Recall (R/D) | Fix sufficiency | False findings | Action errors | Questions | Observations | False clean | Status |
|---|---|---|---|---|---|---|---|---|---|
| `blind-06e57d` | GT-k1 | 1/1 | sufficient | 0 | 0 | 0 | 0 (nodes-mismatch raised as a Finding, not an observation) | No | Approved (advisory), 2 consider, coverage complete |
| `blind-7744c2` | GT-k1 | 1/1 | sufficient | 0 | 0 | 0 | 1 | No | Approved (advisory), 1 consider, coverage complete |
| `blind-a8ddd0` | GT-k1 | 1/1 | sufficient | 0 | 0 | 0 | 0 (nodes-mismatch raised as a Finding, not an observation) | No | Approved (advisory), 2 consider, coverage complete |
| `blind-ad8fdf` | GT-k1 | 1/1 | sufficient | 0 | 0 | 0 | 1 | No | Approved (advisory), 1 consider, coverage complete |

All four reviews recover the sole registered defect (GT-k1) with sufficient proposed fixes, report zero false findings, zero action/severity errors, and correctly decline to claim false-clean. The only differentiator among them is how they treat one non-registered, true-but-non-material observation (the `nodes` type mismatch between `declare class` and the implementation function): two reviews (`06e57d`, `a8ddd0`) elevate it to a formally tagged "Finding" at `P3`/`consider`, two (`7744c2`, `ad8fdf`) correctly keep it at Observation weight with no priority tag. None of the four treats it as blocking or overstates its consequence, so this difference does not rise to an action/severity error in any of them — it is a minor calibration difference in presentation, not in substance.

## New candidates (consolidated across reviews)

**NC-1: `nodes` parameter type mismatch between `GraphQLError`'s `declare class` constructor (line 25, `void | null`) and its `export function` implementation (line 94, `void` only).**

Raised (in some form) by all of `blind-06e57d`, `blind-7744c2`, `blind-a8ddd0`, `blind-ad8fdf`.

- Evidence checked: `src/error/GraphQLError.js:22-100` at `review-head` confirms the asymmetry exactly as described by all four reviews.
- Evidence against materiality: the register's own reproduction (item 4) ran `flow check` at head and got `Found 0 errors`; the same idiom (function implementation looser/untyped relative to its `declare class`) is already used for `GraphQLList` and `GraphQLNonNull` in `src/type/definition.js`, which this session independently confirmed by reading that file — there, the function parameters are fully unannotated relative to the `declare class`, an even larger gap than `GraphQLError`'s, with no apparent issue. No review demonstrated a runtime or type-checking consequence (a Flow error, a wrong inference, a crash); no review claimed one — all four scoped it to `consider`/non-blocking.
- **Ruling: not material.** It is a real, verifiable inconsistency but has no demonstrated consequence and matches a tolerated pattern elsewhere in the same codebase. Confidence: high. What would change this ruling: evidence that some other call site or downstream Flow check actually fails or produces an unsound type inference because of this specific gap (I did not find any in `flow check` at head, per the register, nor in a manual read of the function body, which treats `null` and `undefined` identically at runtime regardless of the declared type).

No other new candidates were raised by any of the four reviews.

---

## Correction appended 2026-09-07T17:48Z — false-clean flag (orchestrator, after pull-request review)

The rulings above are the blind scorer's and are retained unedited. One column is overridden for
scoring: **False clean is `Yes` for all four reviews.** The scorer read the flag as "claims no
material defects" and exempted reviews that reported GT-k1 before approving. The frozen definition
in the method (§4) and in this scorer's own brief is broader — *the review explicitly returns
Approved / no material defects on a target that has at least one material defect* — and every one
of the four derives `Approved (advisory)`. Recovery credit, fix sufficiency and every other column
are unchanged. The corrected counts are in `comparison-data.md` §4, and the deviation is recorded in
the README's §3, item 7.
