# Target

- Repository: `graphql/graphql-js`
- Pull request: [#1582](https://github.com/graphql/graphql-js/pull/1582) — "Enable Flow typings on errors tests + Fix typing for Error constructor"
- Head SHA: `7e39a122eea9292eeffa6905ffdf8a60c5161cfd`
- Merge-base: `5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11` (base branch `master`)
- Merged: 2018-11-21T14:33:19Z, author/merger `IvanGoncharov` (self-merged)
- Files changed: `src/error/GraphQLError.js`, `src/error/__tests__/GraphQLError-test.js`, `src/error/__tests__/locatedError-test.js`, `src/error/__tests__/printError-test.js`, `src/jsutils/__tests__/inspect-test.js`

# Verdict

1 material defect

# Defect register

## GT-k1 — `GraphQLError-test.js`: "creates new stack if original error has no stack" no longer exercises the no-stack fallback branch

- **File / lines at pinned head** (`7e39a122`): `src/error/__tests__/GraphQLError-test.js:57-63`, inside the test `it('creates new stack if original error has no stack', ...)`.
- **What changed here**: `const original = { message: 'original' };` → `const original = new Error('original');` (confirmed via `git show 7e39a122eea9292eeffa6905ffdf8a60c5161cfd -- src/error/__tests__/GraphQLError-test.js`). The remainder of the test body (constructor call and four assertions, including `expect(e.stack).to.be.a('string')`) is untouched.
- **Contract the test is supposed to verify**: `GraphQLError`'s constructor, `src/error/GraphQLError.js:195-208` at head:
  ```js
  if (originalError && originalError.stack) {
    Object.defineProperty(this, 'stack', { value: originalError.stack, ... });
  } else if (Error.captureStackTrace) {
    Error.captureStackTrace(this, GraphQLError);
  } else {
    Object.defineProperty(this, 'stack', { value: Error().stack, ... });
  }
  ```
  There are two branches: copy `originalError.stack` when present, or synthesize a fresh stack when it is absent/falsy. The test's own name/intent is to cover the second (fallback) branch — its sibling test two cases above it, `it('uses the stack of an original error', ...)` (`GraphQLError-test.js:41-52`), already covers the first branch with `new Error('original')` and asserts `expect(e.stack).to.equal(original.stack)`.
- **Trigger**: any `new Error(...)` instance has a non-empty `.stack` string populated at construction time in V8/Node (this is standard V8 behavior, not GraphQL.js-specific). Passing such an instance as `originalError` therefore always satisfies `originalError && originalError.stack` and takes the *copy* branch, never the fallback branch that `Error.captureStackTrace`/`Error().stack` implements.
- **Demonstrated consequence** (reproduced directly, see Reproduction section): with the post-PR test body, `e.stack === original.stack` evaluates to `true` — i.e. the test silently runs the same branch as its sibling and could not fail even if the fallback branch (`Error.captureStackTrace(...)`/`Error().stack`) were deleted or broken outright, because the retained assertion `expect(e.stack).to.be.a('string')` is satisfied by either branch. The fallback branch of `GraphQLError`'s constructor became untested by this suite as of this commit. This was independently discovered and fixed in [PR #4774](https://github.com/graphql/graphql-js/pull/4774) ("test: restore GraphQLError no-stack coverage", merged 2026-06-01), whose description states verbatim: *"This test originally used a plain object without a stack. PR #1582 changed it to `new Error('original')` while enabling Flow typing, which meant the test no longer exercised the no-stack fallback path."* Its fix adds `delete original.stack;` right after construction. `git log -S "creates new stack if original error has no stack"` and direct diffing of every intervening revision of the test file (`c1ca5467`, `daf11ba1`, and others through the TS migration) confirm the bug was introduced exactly at `7e39a122` and persisted unchanged for ~7.5 years until #4774.
- **Required corrective outcome**: the test body for "creates new stack if original error has no stack" must construct or mutate `originalError` so that `originalError.stack` is falsy at the time `GraphQLError` reads it (e.g. a plain object with no `stack` property, as before the PR, or `delete original.stack` after constructing a real `Error`, as #4774 did), while still satisfying whatever type-checker constraint motivated this PR (Flow wants `originalError` typed as `?Error`, which a real `Error` with its `stack` deleted still satisfies). Any change that restores exercising the `else` branches of the constructor's stack-selection logic under this test name is sufficient; the specific mechanism (plain object vs. `delete`) is not prescribed.
- **Is this the PR's promised behavior change, or unintended?** Unintended. The PR's stated purpose is "Enable Flow typings on errors tests + Fix typing for Error constructor" — a typing-only, non-behavioral change. Changing the plain object literal to `new Error(...)` was an incidental step taken to satisfy Flow's `?Error` type for the `originalError` parameter (a plain `{ message: 'original' }` object is not assignable to `?Error` under `@flow strict`), but the author did not preserve the "no stack" property that the test's name and purpose require. This is a test-only regression in coverage, not a production-code defect: `src/error/GraphQLError.js`'s actual runtime logic is untouched and correct (see below).

No other defect was found in this pull request.

# Reproduction

All commands run from a fresh clone of `/tmp/qual137/staging/graphql-js.git` at `/tmp/qual137/work/graphql-js`, Node v24.19.0, `npm install` performed at each checked-out commit.

1. **Focused GraphQLError test suite at head** (`7e39a122`):
   ```
   npx mocha --require @babel/register --require @babel/polyfill --full-trace --timeout 15000 src/error/__tests__/GraphQLError-test.js
   ```
   Result: `13 passing (45ms)`, exit 0. All tests pass, including "creates new stack if original error has no stack" — it passes, but (per GT-k1) for the wrong reason.

2. **Same suite at merge-base** (`5384d218`):
   ```
   npx mocha --require @babel/register --require @babel/polyfill --full-trace --timeout 15000 src/error/__tests__/GraphQLError-test.js
   ```
   Result: `13 passing (15ms)`, exit 0. Also all green — the test suite does not regress in pass/fail status at either commit; the defect is silent (a coverage/assertion-strength defect, not a crash).

3. **Direct demonstration that the branch under test changed** (Node REPL against head's `src/error/GraphQLError.js` via `@babel/register`):
   ```js
   const { GraphQLError } = require('./src/error/GraphQLError');
   const original1 = new Error('original');                      // post-PR test subject
   const e1 = new GraphQLError('msg', null, null, null, null, original1);
   e1.stack === original1.stack;                                  // => true  (copy branch taken)

   const original2 = { message: 'original' };                     // pre-PR test subject
   const e2 = new GraphQLError('msg', null, null, null, null, original2);
   e2.stack === original2.stack;                                  // => false (fallback branch taken)
   typeof e2.stack;                                                // => 'string' (assertion would still pass either way)
   ```
   This confirms: with the post-PR subject the constructor takes the stack-copy branch (same as the sibling test "uses the stack of an original error"); with the pre-PR subject it takes the fallback branch; and the test's only assertion on `.stack` (`to.be.a('string')`) cannot distinguish the two, so the rename to `new Error(...)` silently defeated the test's purpose without breaking the suite.

4. **Confirm the Flow type fix (`src/error/GraphQLError.js`) is real and necessary**: reverting only the one-line type change (`nodes?: ... | void | null` → `nodes?: ... | void`) at head and re-running `npx flow check` produces 8 errors, including at the very call sites this PR's test refactor introduced (e.g. `printError-test.js:23,37`, passing `null` for `nodes`). Restoring the change: `npx flow check` → `Found 0 errors`. This confirms the production-code change is correct and required, not decorative.

5. **Full focused suite for all four other changed test files at head**:
   ```
   npx mocha --require @babel/register --require @babel/polyfill --full-trace --timeout 15000 \
     src/error/__tests__/GraphQLError-test.js src/error/__tests__/locatedError-test.js \
     src/error/__tests__/printError-test.js src/jsutils/__tests__/inspect-test.js
   ```
   Result: `27 passing (19ms)`, exit 0.

# Not ground truth

Plausible-sounding but non-material observations a reviewer might raise — none of these qualify as defects:

- **"The Flow type change on `nodes` (`| void` → `| void | null`) is a red flag / weakens the type."** It is the opposite: it is a correct, minimal, and *necessary* widening. Every other parameter (`source`, `positions`, `path`) already accepts `null` via Flow's `?T` maybe-type sugar; `nodes` was the sole holdout accepting only `void`, which is inconsistent and was already violated by call sites that pass `null` (verified: reverting it reintroduces 8 Flow errors, §Reproduction item 4). This is the PR's stated purpose, delivered correctly.
- **"`e: any` annotations added in `locatedError-test.js` defeat Flow's purpose."** These are narrow, deliberate escape hatches for test fixtures that intentionally monkey-patch non-standard properties (`e.locations = []`, `e.path = []`, `e.nodes = []`) onto a bare `Error` to simulate "GraphQL-error-ish" objects from other libraries — exactly the scenario `locatedError` is designed to handle. Typing these precisely would require a throwaway interface for no benefit; `any` here is idiomatic Flow practice for test doubles, not a leak into production code.
- **"`// $FlowFixMe` in `inspect-test.js` suppresses a real type error."** It suppresses a known, narrow Flow limitation in typing `String.raw` / tagged template literals under `@flow strict` at the time (Flow 0.86). It has no runtime effect and does not mask a behavioral bug — the assertion it decorates (`inspect('"')` → `String.raw\`"\\""\`) passes and is unrelated to the suppressed check.
- **"`printError-test.js`'s refactor from `sourceA.definitions[0].fields[0].type` to `opA.fields[0].type` via an intermediate `fieldA` variable changes behavior."** It does not — `fieldA = opA.fields[0]` then `fieldA.type` is definitionally identical to the old `fieldTypeA = ...fields[0].type`; the refactor exists solely to obtain a value invariant-checked for Flow's benefit (`invariant(opA && opA.kind === Kind.OBJECT_TYPE_DEFINITION && opA.fields)`), not to alter which AST node is used. Verified identical by inspection and by the passing test in Reproduction item 5.
- **"Self-merged PR with a single self-review comment and no second reviewer is a process smell."** True as an observation about process, but it is not a code defect and is not in scope for this adjudication (`state: COMMENTED`, `IvanGoncharov` commenting on his own PR, then merging it — see Preexisting hints). It correlates with why GT-k1 went unnoticed for 7.5 years, but the absence of a second reviewer is not itself an actionable code defect.
- **"The renamed test still exercises `GraphQLError` end-to-end and its assertions are all individually true."** Also true and exactly why this is a *coverage* defect rather than a crash/regression: every assertion in the test passes both before and after the change, and continues to pass at head. A reviewer asserting "this test is broken/failing" would be wrong; the correct framing (GT-k1) is that it passes for the wrong reason and no longer discriminates the fallback branch.

# Preexisting hints

The full review record on PR #1582, retrieved via `gh pr view 1582 --json body,reviews,comments` and `gh api repos/graphql/graphql-js/pulls/1582/comments`, consists of exactly:

- One inline review comment, by the PR's own author `IvanGoncharov`, on `src/error/GraphQLError.js` line 25 (the `nodes` type widening): *"All other arguments support `null` so there is no reason why `nodes` accepts `undefined` but not the `null`."* This is a self-justification of the production-code type fix, not a review by a second party, and it does not touch or gesture at the test-file defect (GT-k1) at all.
- No other reviews, no issue comments, and the PR body itself is empty (`"body":""`).

No participant in the review record gestures at GT-k1. It went completely unflagged during review and remained latent until PR #4774 (2026-06-01), authored by a different person (`yaacovCR`) working on the codebase 7.5 years later.

# Leakage

A truncated mirror used as an evaluation target for this PR must exclude:

- **`8d621b00f7513194bce4a4b2f48d402a4da404bd`** — the commit on PR #4774 that fixes GT-k1 (`delete original.stack;`). This is the single most direct give-away; its presence or its parent/child SHA linkage must not be discoverable.
- **PR #4774** itself (all of it: title "test: restore GraphQLError no-stack coverage", body, and diff) — its body names PR #1582 explicitly and states the defect in plain language. Any mirror must scrub this PR number and its content entirely, not just the commit SHA.
- Any commit carrying the message pattern "restore GraphQLError no-stack coverage" or "no-stack" in its subject/body should be treated as containing the answer.
- No revert of `7e39a122` exists, and no other regression test or follow-up fix specifically targeting this test was found in `git log -S "creates new stack if original error has no stack"` or in a search of `graphql/graphql-js` issues/PRs for "no stack" (checked via `gh api search/issues`) other than #4774 — so #4774 (commit + PR) is the sole leakage vector for GT-k1.
- For the (non-defective) production type fix, no leakage risk was found: no later commit reverts or "fixes" the `nodes?: ... | void | null` change; it stands unmodified in intent through the codebase's history (later superseded wholesale only by the TS migration at `daf11ba1`, which is an unrelated, large-scale rewrite and not a targeted fix, so it is not leakage specific to this PR's content).

# Adjudicator's confidence and limits

- **High confidence** on GT-k1: verified from four independent angles — (a) direct diff of the PR, (b) direct execution against the pinned head's actual `GraphQLError.js` constructor showing the branch taken, (c) an independent primary source (PR #4774, a real production fix authored years later by an unrelated contributor with no connection to this adjudication) stating the identical causal claim, and (d) confirmation via `git log -S` and manual diffing that the defect was never touched between introduction and the #4774 fix.
- **High confidence** that the production code change (`src/error/GraphQLError.js`) and the other three test files (`locatedError-test.js`, `printError-test.js`, `inspect-test.js`) are clean: verified by running `flow check` (0 errors) and the full focused mocha suite (27/27 passing) at head, by reverting the type fix to show it is load-bearing (8 Flow errors reappear), and by manual read of every hunk in the diff confirming each is a type-annotation-only or refactor-preserving-value change.
- **One limitation worth flagging explicitly**: GT-k1 is a defect in a *test*, not in shipped production code — it has no runtime/user-facing consequence on its own (the constructor's fallback branch works correctly; it is simply not exercised by this particular test after the edit). Whether "material defect" as defined for this exercise (an actionable correctness/... failure with demonstrated consequence) is meant to encompass test-coverage regressions is a judgment call; I have included it because it has all the required elements — an actual behavior change from the edit, a violated contract quoted from the code, a concrete trigger, and a demonstrated consequence with primary-source corroboration (PR #4774) — and because the task's own "Proposed defect" framing explicitly invited testing exactly this claim. If the scoring rubric excludes test-only coverage regressions from "material defect" by definition, this register's verdict should be read as "1 material defect under a test-coverage-inclusive definition; 0 under a production-runtime-only definition," with GT-k1's full evidence preserved either way.
- **Unresolved**: none. Every sub-claim in the prior vetting pass's hypothesis was checked against primary sources (the diff, the runtime behavior, and PR #4774) and confirmed true as stated; nothing here required guessing.
