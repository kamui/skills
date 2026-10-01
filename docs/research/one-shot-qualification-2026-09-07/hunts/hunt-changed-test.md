# Changed-test defect hunt — report

Scope note: worked single-threaded, no sub-agents, on this machine, with real
`git`/`gh` commands against full local clones. All timings and outputs below
are from commands actually executed in this session (see "Test evidence you
actually ran").

---

## TOP PICK

### graphql/graphql-js PR #1582 — "Enable Flow typings on errors tests + Fix typing for Error constructor"

**Repository**: `graphql/graphql-js` — public, MIT license, 20,344 stars (checked
via `gh api repos/graphql/graphql-js`). Reference implementation of GraphQL for
JS; real maintainers (GraphQL Foundation / Ivan Goncharov / Lee Byron lineage).

**PR**: #1582, title "Enable Flow typings on errors tests + Fix typing for Error
constructor"
**Author**: Ivan Goncharov (`IvanGoncharov`), a graphql-js maintainer
**Merged**: 2018-11-21T14:33:19Z (created 2018-11-21T14:25:49Z — merged 8
minutes after opening)
**Base branch**: `master` (graphql-js's default branch at the time)

**head SHA (PR-recorded)**: `7e39a122eea9292eeffa6905ffdf8a60c5161cfd`
**base SHA (PR-recorded, `baseRefOid`)**: `5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11`
**merge-base I computed myself** (full clone, `git merge-base 5384d218... 7e39a122...`):
`5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11` — **identical to the PR-recorded
base**. This is a linear/fast-forward merge (the GitHub "merge commit"
`f0ae3f4c0ba469c8f2147f8d12c9e670313b865c` has a single parent, `5384d218...`,
and its tree is byte-identical to `7e39a122...`; `git diff f0ae3f4c
7e39a122` is empty — the two SHAs differ only in committer metadata/timezone
from GitHub's merge rewrite).

**Complete changed-file manifest** (`git diff --stat` between merge-base and
head, verified locally):

| file | + | - |
|---|---|---|
| `src/error/GraphQLError.js` | 1 | 1 |
| `src/error/__tests__/GraphQLError-test.js` | 27 | 33 |
| `src/error/__tests__/locatedError-test.js` | 3 | 3 |
| `src/error/__tests__/printError-test.js` | 15 | 9 |
| `src/jsutils/__tests__/inspect-test.js` | 2 | 1 |
| **Total** | **48** | **47** |

5 files, 95 changed lines — well inside the 250-line/6-file budget.

**Originating issue**: none. `closingIssuesReferences` is empty; PR body is
empty. This was a proactive Flow-typing cleanup, not tied to a bug report.

**Prior review record**: Extremely thin — this is central to how the defect
escaped.
- Reviews: 1, by the author himself (`IvanGoncharov`, state `COMMENTED`, empty
  body).
- Inline PR comments: 1, also by the author, on `src/error/GraphQLError.js`:
  > "All other arguments support `null` so there is no reason why `nodes`
  > accepts `undefined` but not the `null`."

  This comment is about the Flow type of the `nodes` parameter — it has
  nothing to do with the test file's semantic change.
- Issue-level comments: 0.
- `requested_reviewers`: none.
- `merged_by`: `IvanGoncharov` (self-merged).

No one — including the author — commented on the change to the "no stack"
test. It was buried inside a 5-file, 95-line diff where 4 of 5 files are
mechanical `@noflow` → `@flow strict` annotation churn, which is exactly the
kind of diff a reviewer skims rather than reads line-by-line.

### The defect, precisely

**Test function**: `it('creates new stack if original error has no stack', ...)`
**File**: `src/error/__tests__/GraphQLError-test.js`
**Lines** (in the PR's own diff, in the hunk for that test):

```diff
   it('creates new stack if original error has no stack', () => {
-    const original = { message: 'original' };
+    const original = new Error('original');
     const e = new GraphQLError('msg', null, null, null, null, original);
     expect(e.name).to.equal('GraphQLError');
     expect(e.stack).to.be.a('string');
     expect(e.message).to.equal('msg');
     expect(e.originalError).to.equal(original);
   });
```

**What the test claims to check**: that when you construct a `GraphQLError`
from an `originalError` that has **no** `.stack` property, `GraphQLError`
synthesizes a brand-new stack trace (the `else` branch of the constructor's
stack-handling logic, confirmed in `GraphQLError.js`:

```js
if (originalError && originalError.stack) {
  Object.defineProperty(this, 'stack', { value: originalError.stack, ... });
} else if (Error.captureStackTrace) {
  Error.captureStackTrace(this, GraphQLError);
} else {
  Object.defineProperty(this, 'stack', { value: Error().stack, ... });
}
```

**What it actually checks after PR #1582**: `new Error('original')` is a real
`Error` instance, and every `Error` instance already has a non-empty `.stack`
string at construction time. So `original.stack` is truthy, meaning the test
now exercises the **`if` branch** (copy the original's stack) — the exact
same branch already covered by the sibling test `'uses the stack of an
original error'` a few lines above. The assertion left behind,
`expect(e.stack).to.be.a('string')`, is true on **either** branch, so it
cannot discriminate between "stack was copied" and "stack was freshly
generated." The test is vacuous with respect to its own name and purpose: it
tests a different code path (stack-copy) than the one it claims to cover
(stack-fallback-generation), using an assertion too weak to tell the
difference even if it did hit the right branch.

**Trigger and demonstrated consequence** (reproduced live, see test evidence
below): I re-broke the fallback branch in `GraphQLError.js` (made the `else`
path assign `undefined` instead of a captured/generated stack) at the PR's
own head commit, then ran exactly the test file this PR touched. The named
test — `'creates new stack if original error has no stack'` — **passed**
anyway. The only reason the regression was caught at all was an unrelated
test (`'has a name, message, and stack trace'`, which constructs a
`GraphQLError` with no `originalError` at all and therefore also falls into
the broken branch by coincidence). This is exactly the failure mode the task
describes: a test that cannot fail for the reason it exists to check.

### The confirming evidence

**PR**: `graphql/graphql-js#4774`, "test: restore GraphQLError no-stack
coverage"
**Author**: Yaacov Rydzinski (`yaacovCR`), a current graphql-js maintainer
**Base branch**: `17.x.x` (current default/dev branch)
**Commit** (single-commit PR): `8d621b00f7513194bce4a4b2f48d402a4da404bd`,
authored/committed 2026-06-02 00:14–00:16 +03:00
**Merged/landed SHA on `17.x.x`**: `25680d28f749a3e48362c355e1d3a2668d845006`,
2026-06-02T00:22:04+03:00 (mergedAt reported by GitHub API:
2026-06-01T21:22:04Z UTC)
**Diff**: 1 file, +1/-0 (`src/error/__tests__/GraphQLError-test.ts`):

```diff
   it('creates new stack if original error has no stack', () => {
     const original = new Error('original');
+    delete original.stack;
     const e = new GraphQLError('msg', { originalError: original });
```

**Verbatim sentence where the project says the test was wrong** (PR body,
identical to the commit message):

> "This test originally used a plain object without a stack. PR #1582
> changed it to `new Error('original')` while enabling Flow typing, which
> meant the test no longer exercised the no-stack fallback path."

and:

> "This PR deletes the generated stack before constructing GraphQLError so
> the test can synthetically cover the intended branch while still passing
> type check."

This is as clean a confirmation as this task could ask for: the fixing PR
names the exact culprit PR (#1582) and states in its own words that the test
"no longer exercised" the branch it names.

### The corrective outcome a correct review would have to require

A reviewer of PR #1582 would have to insist that the `original` object used
in the "creates new stack if original error has no stack" test genuinely
lack a `.stack` property after the edit — either by leaving it as a plain
object (`{ message: 'original' }`, sufficient for the Flow-typing goal only
if typed permissively), or, if a real `Error` was wanted for stronger typing,
by explicitly stripping the stack (`delete original.stack`) as PR #4774
ultimately did nearly 7.5 years later.

### Tempting false positives

1. **"This is purely a Flow-typing PR; nothing here changes test semantics."**
   Wrong: 4 of 5 files are indeed mechanical `@noflow` → `@flow strict`
   annotation edits (confirmed by diffing every file), but the fifth file
   contains one substantive behavioral change — swapping the mock object's
   *type*, not just annotating it — that has nothing to do with typing and
   everything to do with which runtime branch gets exercised.

2. **"The assertions for `name`, `message`, and `originalError` still hold,
   so nothing was lost."** Wrong: those three assertions were never the ones
   that distinguished the two branches. The discriminating assertion is
   `expect(e.stack).to.be.a('string')`, and that assertion is satisfied by
   *both* the stack-copy branch and the stack-generation branch — it was
   already too weak to prove branch coverage, and became fully vacuous once
   the input started satisfying the `if` branch's guard.

3. **"There's a sibling test, `'uses the stack of an original error'`, so
   the `if` branch and the `else` branch are both still covered somewhere."**
   Wrong: the sibling test exercises the same `if` branch as the mutated
   test now does, twice — with no test genuinely driving the `else`/fallback
   branch of `GraphQLError`'s constructor with a value that lacks `.stack`.
   My injected regression in that exact branch went undetected by the test
   whose name promises to catch it, and was only caught by an unrelated test
   that happened to also touch that branch by omitting `originalError`
   entirely — a coincidence, not a guarantee.

4. **"There's a reviewer comment on this PR, so it clearly got scrutiny."**
   Wrong: the one inline comment (from the author, on himself) addresses a
   completely different line — the Flow type of the `nodes` parameter
   accepting `null` — and never touches the `original` variable or the
   stack-fallback test.

### SHAs a truncated mirror must exclude

To keep this hidden from a reviewer of PR #1582:
- Commit `8d621b00f7513194bce4a4b2f48d402a4da404bd` (PR #4774's branch commit)
- Commit `25680d28f749a3e48362c355e1d3a2668d845006` (PR #4774 as landed on `17.x.x`)
- PR number **#4774** and its title/body text (both quote PR #1582 by number)

I checked for any other places PR #1582 is mentioned in graphql-js history
(`git log --all --grep="1582"` and `--grep="4774"` on the full local clone):
only the two SHAs above reference #1582, and there is no CHANGELOG.md or
release-notes commit mentioning either PR. No GitHub issue references either
number. The exclusion set above is complete as far as I can determine.

### Test evidence I actually ran

Environment: macOS (Darwin 27.0.0), Node v24.19.0, npm 12.0.2, network
available for the one provisioning step only; all test invocations used
`npx --offline` afterward.

**Provisioning** (one-time, network required), at PR head
`7e39a122eea9292eeffa6905ffdf8a60c5161cfd`:
```
$ npm install --no-audit --no-fund
added 484 packages in 9s          # 9.304s wall time (measured with `time`)
```

**Focused test at PR head** (defective test, as merged):
```
$ npx --offline mocha --require @babel/register --require @babel/polyfill \
    --full-trace src/error/__tests__/GraphQLError-test.js
  GraphQLError
    ✓ is a class and is a subclass of Error
    ✓ has a name, message, and stack trace
    ✓ uses the stack of an original error
    ✓ creates new stack if original error has no stack
    ... (13 total)
  13 passing (33ms)
```
Wall time: 1.742s (`time` measured). Exit status 0.

**Demonstrating the escape** — I edited `src/error/GraphQLError.js` at this
same head commit, replacing the `else if (Error.captureStackTrace) {...}
else {...}` fallback with a single `else` branch that assigns
`value: undefined` (simulating a real regression in the "no original stack"
path), then reran the identical test command:
```
  ✓ is a class and is a subclass of Error
  1) has a name, message, and stack trace
  ✓ uses the stack of an original error
  ✓ creates new stack if original error has no stack     <-- still passes!
  ... 
  12 passing (18ms)
  1 failing
  1) GraphQLError has a name, message, and stack trace:
     AssertionError: expected undefined to be a string
```
Wall time: 0.576s. Exit status 1 — but note *which* test failed: not the one
whose name claims to guard this branch.

**Applying the fix from PR #4774** (`delete original.stack;`) to the *same*
head commit, with the *same* injected regression still in place:
```
  11 passing (24ms)
  2 failing
  1) GraphQLError has a name, message, and stack trace: ...
  2) GraphQLError creates new stack if original error has no stack:
     AssertionError: expected undefined to be a string
```
Wall time: 0.553s. Now the named test does fail, as it should.

**At the merge-base** `5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11` (pre-PR
#1582, original correct test with `original = { message: 'original' }`):
```
$ npm install --no-audit --no-fund     # up to date in 0.875s (cache reused)
$ npx --offline mocha ... GraphQLError-test.js
  13 passing (19ms)                    # baseline, all green, 0.620s wall
```
Then with the *same* injected regression in `GraphQLError.js`:
```
  11 passing
  2 failing
  1) GraphQLError has a name, message, and stack trace: ...
  2) GraphQLError creates new stack if original error has no stack:
     AssertionError: expected undefined to be a string
```
i.e., **before** PR #1582, this exact regression was caught by the exact
test in question; **after** PR #1582 (and until PR #4774 in 2026), it was
not. This is a controlled, reproducible before/after demonstration, not an
inference.

All runs used `--offline`, so no network access occurred beyond the one
`npm install` per checkout. Total hands-on verification time across both
checkouts: well under a minute of actual test execution.

### Confidence that the defect is statically visible

High. A reviewer needs only:
1. The PR diff itself (`src/error/__tests__/GraphQLError-test.js`).
2. ~15 lines of surrounding context: the sibling test two lines above
   (`'uses the stack of an original error'`, which also uses
   `new Error('original')` and asserts `e.stack === original.stack`), and
   the constructor's `if (originalError && originalError.stack) {...} else
   {...}` branch in `GraphQLError.js` (unchanged by this PR, 5 lines away in
   the same repo).

Comparing "what makes `original.stack` truthy" against "what the test's name
promises" is a pure reading exercise — no telemetry, fuzzing, or runtime
observation is required, only noticing that `new Error(...)` always has a
stack. I only *ran* the code to make the escape undeniable, not because it
was necessary to see it.

---

## ALTERNATE 1 (verified, but disqualified — reported for completeness)

### boutproject/BOUT-dev — tautological convergence-order assertion

**Repository**: `boutproject/BOUT-dev`, public, LGPL-3.0, 245 stars (checked
via `gh api repos/boutproject/BOUT-dev`). Plasma-fluid finite-difference
simulation code; real maintainers (University of York fusion group).

**Confirming fix** (found via `gh search commits "test always passed"`):
commit `e961e75696aa7fcaf194c6994732725df9bc900c`, "tests: Fix typo that made
tests always pass" (2025-11-06T17:13:18Z), part of PR **#3196** "Add more
tests for FCI operators" (merged 2026-03-02T09:34:23Z, confirmed via
`gh api repos/boutproject/BOUT-dev/commits/<sha>/pulls`). Diff (verified with
`gh api .../commits/<sha>`):

```diff
-def assert_convergence(error, dx, name, order) -> bool:
+def assert_convergence(error, dx, name, expected) -> bool:
     fit = polyfit(log(dx), log(error), 1)
     order = fit[0]
     ...
-    success = order > order * 0.95
+    success = order > expected * 0.95
```

**The defect**: `tests/MMS/spatial/fci/runtest`'s `assert_convergence`
originally took a parameter named `order` for the *expected* convergence
order, then immediately reassigned a local `order = fit[0]` from the
curve-fit *measured* order — silently shadowing the intended-order parameter.
The success check `order > order * 0.95` therefore compares the measured
value against 95% of *itself*, which is true for **any** positive measured
order, however far from the expected physical convergence rate. This is a
canonical tautological/self-referential assertion — a numerical-convergence
regression test that cannot fail as long as the fit produces any positive
slope.

**Why this doesn't qualify (disqualifying findings, both verified)**:
1. **Size budget.** I traced the test's origin with
   `git log --all --oneline -S"order * 0.95" -- tests/MMS/spatial/fci/runtest`
   and `git log --diff-filter=A --follow` on a local clone; the file (and the
   buggy function) was introduced in commit `af2ca9b1e78c83f35fd5bc79fa9db16e56c4ad4c`,
   "Add proper scaling test for FCI with C2 and C4" (2019-01-25, Peter Hill),
   which touches **7 files** and **300 inserted lines** — over both the
   6-file and 250-line hard budgets in this task.
2. **Offline-runnable in <5 min.** BOUT-dev's own README lists hard
   requirements of a C++20 compiler, MPI, and NetCDF, with FFTW/PETSc/SUNDIALS
   as strongly-recommended optional deps; the FCI test specifically is gated
   on having PETSc/zoidberg (per its own commit history: "Ensure FCI test only
   runs if we have zoidberg", "Split in X only if we have PETSc"). This is a
   from-source compiled physics-simulation build, not a "one dependency
   download" provisioning step; I did not attempt to build it because the
   requirements alone make a <5-minute offline focused-test run implausible,
   and confirming that would cost far more than the payoff.
3. **Popularity.** 245 stars is thin for "popular enough that the review
   trail is meaningful," though the project is a real, actively maintained
   scientific code with genuine external users.

I did not chase down PR review-thread details for `af2ca9b1e` given (1)
alone already disqualifies it.

---

## ALTERNATE 2 (verified, but disqualified — reported for completeness)

### kubernetes/kubernetes — dual-stack node-IP e2e test

**Repository**: `kubernetes/kubernetes`, public, Apache-2.0, extremely
popular (110k+ stars). Real trail: fix landed as PR **#137119**, "dual stack
test fixups" (author `danwinship`, merged 2026-02-25T14:13:48Z, 3 files,
+30/-27, confirmed via `gh pr view 137119`).

**The defect** (in `test/e2e/network/dual_stack.go`, confirmed via
`gh api repos/kubernetes/kubernetes/commits/05ca65743419c4a56a6552b0c48db00d12231405`):
the e2e test `'should have ipv4 and ipv6 internal node ip'` asserted that
**every** node in the cluster has *exactly* 2 `NodeInternalIP` addresses, one
IPv4 and one IPv6:
```go
internalIPs := e2enode.GetAddresses(&node, v1.NodeInternalIP)
gomega.Expect(internalIPs).To(gomega.HaveLen(2))
if netutils.IsIPv4String(internalIPs[0]) == netutils.IsIPv4String(internalIPs[1]) {
  framework.Failf(...)
}
```
The fix's own commit message states the old assertion was simply wrong:
> "The test was previously asserting that in a dual-stack cluster, every
> node had exactly 2 InternalIPs... this test was wrong since (a) it didn't
> allow nodes to have additional non-primary node IPs, and (b) it
> discriminated against ExternalIPs."

This is a real "asserts the wrong thing" defect (over-strict universal
assertion where the spec only guarantees an existential property), with an
explicit maintainer admission — a strong match for the task's criteria in
every dimension except one.

**Why this doesn't qualify**: it is a Kubernetes e2e test that requires a
live, real, multi-node **dual-stack** cluster to execute at all — it cannot
be run offline on a laptop within 5 minutes (or at all, absent a running
cluster with dual-stack networking configured) regardless of any dependency
pre-provisioning. This decisively fails constraint 5. I did not chase down
the original introducing PR/commit for this test (git-blaming a specific
`test/e2e/network/dual_stack.go` line back through kubernetes/kubernetes's
huge history would require a full clone I judged not worth the time once the
offline-runnability constraint was already a hard, unfixable disqualifier),
nor did I verify its diff size against the 250-line/6-file budget for the
same reason.

---

## Summary

| Candidate | Meets size budget | Popular + permissive | Review trail via `gh` | Offline test <5min | Confirmed by upstream | Verdict |
|---|---|---|---|---|---|---|
| **graphql-js #1582** | ✅ 5 files / 95 lines | ✅ MIT, 20k★ | ✅ (thin but real: 1 self-review, 1 comment) | ✅ ran it, ~2s | ✅ PR #4774, exact quote | **PASSES — top pick** |
| BOUT-dev (`af2ca9b1e`) | ❌ 7 files / 300 lines | ⚠️ 245★, LGPL | not checked (moot) | ❌ needs full MPI/PETSc build | ✅ commit `e961e756`, exact quote | fails on size + offline-test |
| kubernetes dual-stack e2e | not checked (moot) | ✅ Apache-2.0, 110k★ | ✅ PR #137119 | ❌ needs live dual-stack cluster | ✅ PR #137119, exact quote | fails on offline-test |

The graphql-js candidate is the only one of the three that I could fully
verify against every constraint with commands actually executed, including a
constructed before/after regression that proves the named test provides zero
protection for the branch it claims to guard, and that the pre-PR-#1582 test
did provide that protection.
