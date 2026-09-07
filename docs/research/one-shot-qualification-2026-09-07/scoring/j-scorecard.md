# Scorecard — target j (`trpc/trpc#5017`)

Ground truth: 1 material defect, **GT-j1** (`Overwrite`'s new object-gate drops inferred
context/input properties when a middleware's params are built from an unconstrained generic type
parameter). Register's "Not ground truth" list pre-empts two specific non-material observations
that all four blind reviews independently rediscovered: the redundant/dead `TWith extends any ? ... : TType`
branch, and the untested `voidWithMiddleware` procedure in the new regression test.

I re-verified the two recurring technical claims myself against a local `typescript@5.2.2` (from
`/tmp/qual137/repro/node_modules/typescript`) rather than taking them on faith:

- `Overwrite<string, never>` (using the actual shipped `Overwrite` body) resolves to `never`, **not**
  `TType` — confirms the "unreachable `: TType` branch" claim made (in some form) by all four reviews.
- Replacing the branch with `[TWith] extends [never] ? TType : TWith` (a190cd's proposed alternative)
  does make `Overwrite<string, never>` resolve to `string` and `Overwrite<string, number>` resolve to
  `number` — confirms that fix would work, for that (non-material) finding.
- The `voidWithMiddleware` procedure in `issue-5020-inference-middleware.test.ts` is declared (lines
  13–17) and never referenced in the `test('string', …)` body (lines 25–39) — confirms the test-gap
  claim made by all four reviews.

I did not observe anything I'd flag as a reviewer identifier; the four payloads are structurally
near-identical (same trailer format, same two recurring findings, same "Approved (advisory)"
verdict), which I note only because it affects how much independent signal these four samples
give, not because I inferred anything about who produced them.

---

## `blind-11726b.md`

**1. Recovered defect IDs:** None.

**2. Missed defect IDs:** GT-j1.

**3. Fix sufficiency:** N/A (no recovered defects).

**4. Findings not in the register:**

- Finding: *"Assert inferred types for `voidWithMiddleware`"* — anchor
  `issue-5020-inference-middleware.test.ts:13-17`.
  > "The declared `voidWithMiddleware` procedure in the router fixture is never referenced anywhere
  > in the `describe`/`test` body, so no `expectTypeOf` assertion checks its inferred `ctx`, input,
  > or output types; a regression specific to input-less middleware chains would compile without
  > failing this file."
  Verified true against the test file (confirmed above). Classification: **true but not
  material** — this is verbatim the register's "Not ground truth" item ("No test covers
  `voidWithMiddleware`'s inferred input" — "a real test-coverage gap in the PR's own regression
  test, but not a defect in the shipped type").

- Observation: *"The `: TType` fallback added to `Overwrite`'s non-object branch is unreachable,
  since TypeScript collapses a distributive conditional on a naked type parameter equal to `never`
  to `never` before either branch runs, confirmed by isolating the type under `tsc`. Evidence:
  `packages/server/src/core/internals/utils.ts:25-29`."*
  Verified true — I reproduced this exact collapse independently (`Overwrite<string, never>` ⇒
  `never`, not `TType`). Classification: **true but not material** — this is the register's "Not
  ground truth" item about the duplicated/redundant `TWith extends any ? TWith : never` /
  `TWith extends any ? TWith : TType` branches: "a real code-smell … but a factoring preference,
  not a correctness defect with a demonstrated consequence." Correctly filed as an Observation, not
  escalated to a Finding, which matches its non-material weight.

**5. Action/severity errors:** None — the one Finding is P3/consider, matching its true-but-not-material weight; no over-escalation.

**6. Questions, observations, hygiene:**
- 1 observation (the dead-branch one above): technically correct, but the underlying phenomenon was already visible in the pre-fix code shape the reviewers argued over (see register's "Preexisting hints"); reading it would not change the review's verdict since it's explicitly a non-material code-smell. Answerable from the material at hand (the diff) — yes, and I confirmed it's accurate.
- 0 open questions.

**7. Derived status:** "Approved (advisory) — 1 consider finding." Declares coverage **complete**:
"Complete merge-base diff reviewed (2/2 changed files, 2/2 diff chunks consumed)." Also asserts, as
part of its reasoning: "`_ctx_out` is always instantiated from an object type, and `_input_in`/`_input_out`
are already guarded by an `UnsetMarker` check before `Overwrite` is invoked, so no call site
regresses from the change." This specific claim is the load-bearing reasoning behind the false
clean, and it is contradicted by GT-j1: `_ctx_out` fields are *not* always concretely `object` at
the point `Overwrite` is applied — they can be indexed-access expressions into an unresolved
generic `ProcedureParams` type parameter (as demonstrated by the register's reproduction), which is
exactly the case that regresses. I flag this as the specific unsupported claim underlying the false
clean rather than a separate "false finding" in the Findings list (it appears in prose, not as a
tagged finding).

**8. False clean:** **Yes.** > "**Approved (advisory)** — 1 consider finding." with no must-fix or
material finding, on a target with GT-j1 present.

**9. Duplicates:** None (2 distinct items, 1 Finding + 1 Observation, neither restating the other).

---

## `blind-8b00f8.md`

**1. Recovered defect IDs:** None.

**2. Missed defect IDs:** GT-j1.

**3. Fix sufficiency:** N/A.

**4. Findings not in the register:**

- Finding: *"Assert the inferred types for `voidWithMiddleware`"* — anchor
  `issue-5020-inference-middleware.test.ts:13-17`.
  > "This regression test would keep passing even if that no-input-with-middleware path became
  > mangled again, because no assertion in the file reads `AppRouterInputs['voidWithMiddleware']`
  > or `AppRouterOutputs['voidWithMiddleware']`; the procedure is declared but never checked."
  Verified true. Classification: **true but not material** (same register item as above).

- Observation: *"The `object`-branch's trailing `: never` fallback in the new `Overwrite` (for a
  non-object, non-never `TWith`) is unreachable, because TypeScript's distributive-conditional
  collapse over the naked `TWith extends object` check already resolves the whole expression to
  `never` whenever `TWith` is `never`, before that inner ternary is reached. Evidence:
  `packages/server/src/core/internals/utils.ts:12-19`."*
  This is internally inconsistent: as written, the claim is scoped to "a non-object, non-never
  `TWith`" — but the branch it names (the "trailing `: never` fallback") is reached *only* when
  `TWith` **is** `never` (i.e., does not extend `any`); a non-never `TWith` never reaches that
  fallback at all, it takes the sibling branch that returns `TWith`. The cited evidence range,
  `utils.ts:12-19`, is also the wrong code — that range is the `{merge}` mapped-type body for the
  object+object case, not the "`TWith extends any ? TWith : never`" fallback (which sits at
  `utils.ts:21-24` in the file as read from the clone). The general phenomenon this observation is
  reaching for (a `never`-instantiated `TWith` collapsing a naked-parameter distributive conditional
  before an else-branch is reached) is real elsewhere in the file — see `blind-11726b`'s and
  `a190cd`'s versions of the same underlying point, which cite the correct lines and check out under
  `tsc`. As written here, though, the sentence and its own evidence citation contradict each other,
  so I classify this specific observation as **inaccurate as stated** (not a "false finding" in the
  Findings-list sense, since it's an Observation, but its reasoning and citation do not hold up).

**5. Action/severity errors:** None (single Finding, P3/consider, matches its non-material weight).

**6. Questions, observations, hygiene:**
- 1 observation (the garbled dead-branch one above): as written, not fully answerable/correct from
  the material at hand — the claim's own internal logic and its evidence citation don't match each
  other. Even if repaired to point at the right lines, it would still land on the register's
  non-material code-smell item, not change the verdict.
- 0 open questions (explicit: "No open questions were published.").

**7. Derived status:** "Approved (advisory) — 0 must-fix findings, 1 consider finding, 0 open
questions." Declares coverage **complete**: "Complete merge-base diff reviewed (2 files); … all six
call sites of `Overwrite` in `packages/server/src` inspected." No explicit "no call site regresses"
claim as strong/specific as `11726b`'s, just a coverage-breadth statement.

**8. False clean:** **Yes.** > "**Approved (advisory)** — 0 must-fix findings, 1 consider finding, 0
open questions." on a target with GT-j1 present.

**9. Duplicates:** None.

---

## `blind-a190cd.md`

**1. Recovered defect IDs:** None.

**2. Missed defect IDs:** GT-j1.

**3. Fix sufficiency:** N/A.

**4. Findings not in the register:**

- Finding 1: *"Fix the unreachable `: TType` branch in `Overwrite`"* — anchor
  `packages/server/src/core/internals/utils.ts:25-29`.
  > "TypeScript's naked-type-parameter distribution collapses the whole `TWith extends any ? TWith :
  > TType` conditional to `never` before the new `: TType` branch can ever be selected, so
  > `Overwrite<string, never>` still resolves to `never`, not `TType` as the branch and its comment
  > claim."
  Verified true — matches my own reproduction exactly (`Overwrite<string, never>` ⇒ `never`).
  Proposed change: *"Either delete the unreachable `: TType` branch … or implement the documented
  fallback with a non-distributive check such as `[TWith] extends [never] ? TType : TWith`."* I
  tested this exact alternative: it makes `Overwrite<string, never>` resolve to `string` and
  `Overwrite<string, number>` resolve to `number`, i.e., it is a correct, working fix for the stated
  (non-material) issue. Classification: **true but not material** — register's "Not ground truth"
  item on the redundant/dead branches ("a real code-smell … but a factoring preference, not a
  correctness defect").

- Finding 2: *"Add type assertions for `voidWithMiddleware` in the new regression test"* — same
  claim and evidence as the other three reviews, verified true. **True but not material.**

**5. Action/severity errors:** None — both findings correctly filed as P3/consider.

**6. Questions, observations, hygiene:** None published ("No open questions and no observations
were admitted in this run").

**7. Derived status:** "Approved (advisory) — 0 must-fix findings, 2 consider findings." Declares
coverage **complete**: "Complete merge-base diff reviewed (2 files, +57/−3) … Traced every
`Overwrite` call site." Notably makes the most specific (and, per GT-j1, incorrect) supporting
claim of the four: *"the default root `ctx` type (`object`) always takes the object branch, so only
input inference exercises the new non-object branch."* This is contradicted by GT-j1: the
regression manifests precisely in `_ctx_out` composition (`middleware.ts:65,81,103,136`) when a
middleware's context-extension type is built from an unconstrained generic type parameter, not the
default root `ctx`. The reasoning conflates "the *default* root ctx type is `object`" (true, and
irrelevant) with "*every* `_ctx_out` `Overwrite` call only ever sees object-typed operands" (false —
this is exactly what fails to hold under a naked generic `T`). This is the most concrete,
checkable-and-wrong technical claim among the four reviews' approval reasoning, though it appears in
prose rather than as a tagged Finding.

**8. False clean:** **Yes.** > "**Approved (advisory)** — 0 must-fix findings, 2 consider
findings." on a target with GT-j1 present.

**9. Duplicates:** None (2 distinct findings).

---

## `blind-f3a3b7.md`

**1. Recovered defect IDs:** None.

**2. Missed defect IDs:** GT-j1.

**3. Fix sufficiency:** N/A.

**4. Findings not in the register:**

- Finding 1: *"Drop the unreachable `TType` fallback in `Overwrite`"* — anchor
  `packages/server/src/core/internals/utils.ts:25-30`.
  > "`TWith extends any ? TWith : TType` never selects `TType`: every type except `never` satisfies
  > a naked `extends any` check, and instantiating that same naked parameter with `never`
  > short-circuits the whole conditional to `never` before either branch runs."
  Verified true. Proposed change: *"replace the nested conditional with `: TWith`, which is
  equivalent to the current code for every instantiation."* I confirmed this is a behavior-preserving
  simplification (the branch is unreachable regardless of its content, so swapping in `TWith`
  changes nothing observable). Classification: **true but not material** (same register item).

- Finding 2: *"Assert on `voidWithMiddleware`'s inferred types or drop it"* — same claim as the
  other three, verified true, plus a comparison to a sibling convention: *"Every other regression
  test in this directory that declares a procedure asserts on its inferred type (e.g.
  `issue-4947-merged-middleware-inputs.test.ts`)."* I did not independently verify the naming of
  that specific sibling file, but the core claim (the file's own `voidWithMiddleware` procedure goes
  unchecked) is independently confirmed from the test file itself. **True but not material.**

- Observation: *"The new regression test's filename cites issue #5020 rather than this PR's own
  number, and the PR body carries no closing reference to any issue."*
  The filename fact is true (`issue-5020-inference-middleware.test.ts`). However, the implied
  suggestion of an inconsistency is weak: the packet's own commit history shows this file was
  explicitly renamed to reference the origin issue (`rename` commit), and this is the same
  filename-by-origin-issue convention `a190cd`'s Finding 2 cites as the established pattern
  (`issue-4947-merged-middleware-inputs.test.ts`) — i.e., naming regression tests after the bug they
  regress-test, not the fixing PR, appears to be the repo's normal convention rather than a defect
  or oddity. Classification: **true but not material**, and the "not material" case is stronger than
  the observation's phrasing suggests (it reads as flagging a possible inconsistency, when the
  evidence available in the packet suggests this is the intended convention).

**5. Action/severity errors:** None — both findings correctly filed as P3/consider.

**6. Questions, observations, hygiene:**
- 1 observation (filename naming, above): answerable from the packet (commit history shows the
  deliberate "rename" step); would not change the verdict either way.
- 0 open questions.

**7. Derived status:** "Approved (advisory) — 0 must-fix findings, 2 consider findings." Declares
coverage **complete**: "Complete merge-base diff reviewed (both changed files read in full); callers
of `Overwrite` across `procedureBuilder.ts` and `middleware.ts` traced."

**8. False clean:** **Yes.** > "**Approved (advisory)** — 0 must-fix findings, 2 consider
findings." on a target with GT-j1 present.

**9. Duplicates:** None (2 findings + 1 observation, each distinct).

---

## Cross-review table

| Review | Recovered | Recall (R/D) | Fix sufficiency | False findings (raw) | Action errors | Questions | Observations | False clean | Status declared |
|---|---|---|---|---|---|---|---|---|---|
| `blind-11726b.md` | none | 0/1 | N/A | 0 | 0 | 0 | 1 (accurate) | **Yes** | Approved (advisory), coverage complete |
| `blind-8b00f8.md` | none | 0/1 | N/A | 0 | 0 | 0 | 1 (internally inconsistent claim + wrong evidence citation) | **Yes** | Approved (advisory), coverage complete |
| `blind-a190cd.md` | none | 0/1 | N/A | 0 | 0 | 0 | 0 | **Yes** | Approved (advisory), coverage complete |
| `blind-f3a3b7.md` | none | 0/1 | N/A | 0 | 0 | 0 | 1 (accurate but overstated implication) | **Yes** | Approved (advisory), coverage complete |

All four: 2 findings max, both true-but-not-material (dead-branch code smell + untested
`voidWithMiddleware`), both explicitly pre-empted as non-material in the register's "Not ground
truth" section. None recovered GT-j1. All declared complete coverage and an advisory-approved
verdict, which is a false clean on this target in all four cases.

## New candidates (consolidated across reviews)

None. Every substantive claim raised across all four reviews (the unreachable/dead conditional
branch, the untested `voidWithMiddleware` procedure, and the test-filename-vs-issue-number
observation) is either explicitly listed in the register's "Not ground truth" section as a
considered-and-rejected candidate, or is a directly-verifiable, low-stakes stylistic note with no
plausible path to a demonstrated consequence. I checked each against the source (`utils.ts`,
the test file, and `git log` on `utils.ts`) and against the register; nothing surviving that check
rises to a new, unrefuted, material candidate. Confidence: high — this is a narrow, single-file,
type-level diff, and the four independent reviews converged on the same two non-material items
without surfacing anything the register hadn't already anticipated.

## Note on apparent similarity

The four blind payloads are structurally and substantively very similar to one another (same
trailer/comment format, same two recurring findings, same verdict shape). I did not see anything
that reads as an explicit reviewer identifier, and per instructions I have not tried to infer or
compare identities — I'm noting the similarity only because it means these four samples carry less
independent signal about generalization than four unrelated reviews would, which is relevant context
for whoever aggregates these scorecards, not a scoring input for any individual review.
