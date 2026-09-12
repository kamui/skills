# Target

- Repository: `golang-jwt/jwt`, base branch `main`
- Pull request: `#456` — "Add `WithNotBeforeRequired` parser option and add test coverage"
- Head SHA: `734a9292dbc587d5f0e7086af8e622d3541af21c`
- Merge-base: `ce52acb322f4166c6f50543398a4b85993dd02fc`
- Merge commit: `9d770c8525013476c8d8a56f06e7d3c61d405203`, merged 2025-08-07T06:01:43Z
- Files touched: `parser_option.go` (+8), `validator.go` (+8/-2), `validator_test.go` (+67)
- Working clone: `/tmp/bd148/adjudication/jwt-456/repo` (clone of `/tmp/bd148/staging/jwt.git`)

# Verdict

1 material defect

# Category fit

- **GT-t1**: does **not** fit the hypothesized category (C4 "clean control"). It is a **C3** defect — "a test the diff adds ... that is materially wrong." The hypothesis explicitly claims the "added tests" are part of the clean, supported surface; that claim is false. The production change (`parser_option.go`, `validator.go`) *is* clean and supports the C4 framing — see "ground-truth surface" below.

# Defect register

## GT-t1 — `Test_Validator_requireNotBefore` cannot detect a regression in the feature it exists to test

- **Location at pinned head (734a9292dbc587d5f0e7086af8e622d3541af21c)**: `validator_test.go:265-330`, function `Test_Validator_requireNotBefore`. Introduced by the diff hunk `@@ -262,6 +262,73 @@ func Test_Validator_verifyIssuedAt` in the merge-base→head diff (the PR's only change to `validator_test.go`).
- **Expected behaviour / violated intent**: The PR's own title is "Add `WithNotBeforeRequired` parser option **and add test coverage**." The single line of production logic the PR adds that matters is `validator.go:119`: `if err = v.verifyNotBefore(claims, now, v.requireNbf); err != nil {` inside `Validate()` — this is the wiring from the new `WithNotBeforeRequired()` option (`parser_option.go:69-74`, sets `p.validator.requireNbf = true`) through to actual claim rejection. A test with this name and stated purpose must exercise that wiring and must be capable of failing if it regresses.
- **What the test actually does**: at `validator_test.go:311-323` it builds a `*Validator` via `NewValidator(opts...)`, correctly including `WithNotBeforeRequired()` when `tt.fields.requireNbf` is true — so `v.requireNbf` is genuinely set on `v`. But at line 325 it then calls `v.verifyNotBefore(tt.args.claims, tt.args.cmp, tt.args.required)` **directly**, passing `tt.args.required` (a value the test table sets explicitly, independent of `tt.fields.requireNbf`) as the `required` argument. `Validate()` — the only place `v.requireNbf` is read in production code — is never called. `v.requireNbf` is therefore write-only in this test: it is set on the struct and never read by anything the test executes.
- **Second, compounding defect in the same test**: the assertion at line 325-327, `if err := ...; (err != nil) && !errors.Is(err, tt.wantErr) { t.Errorf(...) }`, only fires when `err` is non-nil and does not match `wantErr`. It never fires when `err` is `nil` but `wantErr` was non-nil (a "wanted an error, got none" case is silently accepted). Of the test's 3 subtests, only one ("token nbf time is in future") has a non-nil `wantErr` (`ErrTokenNotValidYet`); for that subtest the assertion is a no-op if the code under test wrongly returns `nil`.
- **Trigger / reproduction I ran**:
  1. Mutated `validator.go:119` from `v.verifyNotBefore(claims, now, v.requireNbf)` back to the pre-PR hard-coded `v.verifyNotBefore(claims, now, false)` (i.e., made `WithNotBeforeRequired()` a complete no-op in `Validate()`, exactly reverting the PR's behavioural change). Ran `go test -count=1 ./...` at head with this mutation: **all packages pass**, including `Test_Validator_requireNotBefore` (command: `go test -count=1 -run 'Test_Validator_requireNotBefore|WithNotBeforeRequired' -v ./`, exit 0; full-suite `go test -count=1 ./...`, exit 0, ~0.3s). Restored the file afterward (`git diff --stat` empty, confirmed).
  2. Independently mutated `verifyNotBefore` (`validator.go:217-228`) to unconditionally `return nil` (simulating a broken not-before check that never rejects a future-dated token). Ran `go test -count=1 -run Test_Validator_requireNotBefore -v ./`: **still passes**, including the "token nbf time is in future" subtest, because of the weak assertion described above. Restored the file afterward (`git diff --stat` empty, confirmed).
  3. Confirmed the production wiring is in fact correct when exercised properly: added a throwaway test calling `NewValidator(WithNotBeforeRequired()).Validate(RegisteredClaims{})` and got `ErrTokenRequiredClaimMissing` as expected (message: `token is missing required claim: nbf claim is required`), then removed the throwaway file.
- **Demonstrated consequence**: the entire repository test suite (`go test -count=1 ./...`, all packages) is insensitive to two different, realistic regressions in the exact behaviour this PR introduces — (a) the option being silently disconnected from `Validate()`, and (b) the not-before-in-the-future check being silently broken. No other test in the repository covers `WithNotBeforeRequired`/`requireNbf`: `grep -rn "WithNotBeforeRequired\|requireNbf"` over the tree at current `main` (`1a11d37`, 2026-09-08) shows it appears only in `parser_option.go`, `validator.go`, and this one test function — unlike the analogous `WithExpirationRequired`, which additionally has an end-to-end case in `parser_test.go`'s `jwtTestData` table ("rejects if exp is required but missing", `parser_test.go:427-434`) that goes through the real `Parser`/`Validate()` path. `WithNotBeforeRequired` has no such end-to-end case, at merge or since.
- **Required corrective outcome**: any sufficient fix must add at least one assertion that (i) actually calls `Validator.Validate()` (or the full `Parser.Parse`/`ParseWithClaims` path) with `WithNotBeforeRequired()` set and a claims value lacking `nbf`, and observes the resulting error is `ErrTokenRequiredClaimMissing`; and (ii) uses an assertion that fails when a non-nil `wantErr` is expected but `err` comes back `nil` (e.g. `errors.Is` regardless of `err == nil`, or a dedicated "wanted err, got nil" branch). The specific shape (rewriting the existing table test vs. adding a `parser_test.go` case, as was done for `requireExp`) is not prescribed — only that the resulting suite goes red when the two mutations above are reintroduced.
- **Category**: **C3** — a test the diff adds that is materially wrong (cannot fail for the reason it exists, and has a dead branch for the one non-nil-error case). Not C1 (no concurrency/timing mechanism involved) and not C2 (this is entirely within the diff's own hunks, not an obligation stated outside them).
- **Relationship to the PR's promised change**: this is **not** a defect in the observable behaviour the PR promised (`WithNotBeforeRequired()` making `nbf` mandatory) — that behaviour works correctly, verified directly above. It is an **insufficient implementation of the second half of what the PR explicitly promised** ("...and add test coverage"): the added test does not, in fact, cover the field/wiring it was written for.

# Reproduction

All commands run from `/tmp/bd148/adjudication/jwt-456/repo` with `GOMODCACHE=/tmp/bd148/gomodcache GOFLAGS=-mod=mod GOPROXY=off GOCACHE=<scratch>`.

| Commit | Command | Result | Duration |
|---|---|---|---|
| Head `734a929` | `go test -count=1 ./...` | ok, all 3 packages pass | ~1.3s |
| Head `734a929` | `go test -count=1 -race -run Test_Validator ./...` | ok, all pass | ~8.8s |
| Merge-base `ce52acb` | `go test -count=1 ./...` | ok, all 3 packages pass | ~0.7s |
| Head, mutated (`v.requireNbf`→`false` in `Validate`) | `go test -count=1 ./...` | ok — **should have failed and did not** | ~n/a |
| Head, mutated (`verifyNotBefore` → `return nil`) | `go test -count=1 -run Test_Validator_requireNotBefore -v ./` | PASS on all 3 subtests — **should have failed and did not** | ~n/a |
| Head, ad hoc end-to-end check (not part of repo) | `NewValidator(WithNotBeforeRequired()).Validate(RegisteredClaims{})` | correctly returns `ErrTokenRequiredClaimMissing` — production code is correct | ~n/a |

No test fails at either merge-base or head under the unmodified source; the defect is a coverage/assertion gap, not a failing test. All mutations were reverted; `git status --short` / `git diff --stat` confirmed clean before finishing.

# Not ground truth

- **"`Validator{}` zero-value construction changes behaviour."** False. `requireNbf`'s zero value is `false`, identical to the old hard-coded `false` passed to `verifyNotBefore`. Existing callers building `&Validator{}` directly (bypassing `NewValidator`) see no behaviour change. Confirmed by reading `validator.go:36-72` (field default) and the diff (`validator.go:114-121`).
- **"Requiring `nbf` breaks existing verifiers."** False — the option is strictly opt-in (`parser_option.go:69-74`); no caller is affected unless they explicitly add `WithNotBeforeRequired()`.
- **"The `nbf == nil` path with `required=true` is untested/unsupported."** Overstated as a defect claim: the underlying shared function `errorIfRequired(required, claim string)` (`validator.go:324-330`) *is* exercised end-to-end through `Validate()` for other claims (`iss`, `sub`) via existing cases "expected iss is missing" / "expected sub is missing" in `Test_Validator_Validate` (`validator_test.go`, unchanged by this PR), giving reasonable confidence in the shared branch itself. It is true that no case in this PR's own new test combines "nbf missing" with `required=true`, but this is subsumed by, and less severe than, GT-t1 above — the real defect is that the field-to-`Validate()` wiring specific to `requireNbf` is unexercised at all, not merely that one combination of inputs is missing from one function's table.
- **Doc-comment or naming nitpicks on `WithNotBeforeRequired`** (`parser_option.go:69-70`): the comment "By default nbf claim is optional" accurately reflects RFC 7519 §4.1.5 ("The processing of the `nbf` claim requires that the current date/time MUST be after or equal to the not-before date/time listed in the `nbf` claim... Use of this claim is OPTIONAL."). No defect.
- **Later commits #484 (doc comment cleanup on `ParserOption` type, `76f5828`) and #510 (`verifyExpiresAt` message wording, `9a70137`)** do not touch `nbf`/`requireNbf` logic at all — confirmed by `git show --stat` on both; irrelevant to this PR's correctness.
- **General "these tests call private methods directly instead of `Validate()`" pattern** is a known, pre-existing convention across the *entire* file (present at merge-base already in `Test_Validator_verifyIssuedAt`, `Test_Validator_verifyIssuer`, `Test_Validator_verifySubject`, and the original `Test_Validator_verifyExpiresAt`, all using the identical `(err != nil) && !errors.Is(...)` idiom — confirmed via `git show ce52acb:validator_test.go | grep -n "err != nil) && !errors.Is"`, 5 pre-existing hits). A reviewer flagging "this whole file's test style is weak" would be right in general but that broad claim is not attributable to this PR and is not itself a material defect of this diff — it is scoped down to GT-t1 only because GT-t1 is where the pattern collides with code this PR actually introduces (`v.requireNbf`) and leaves it completely unprotected.

# Preexisting hints

The PR's own review record (available to reviewers up to the merge instant) directly discusses the general version of this problem, but for `timeFunc`/`verifyExpiresAt` rather than `requireNbf`/`verifyNotBefore`, and the discussion concludes by **deferring** it rather than fixing it — right before the commit that introduces GT-t1:

- **equalsgibson** (PR author), review comment on an earlier revision, 2025-08-01T16:08:34Z: *"Note: While reviewing the tests for this, it appears that explicitly setting the timeFunc on the Validator does not actually impact the tests. This is due to the test calling the private method directly (i.e. Validator.verifyExpiresAt()), rather than the "Validator.Validate()" method where the timeFunc is used to determine the time for the validation methods. Because of this, the Validator in the tests was always reporting the the cmp time as being wrong (as the Validator had it's time set to the zero value)."*
- **oxisto** (maintainer), 2025-08-02T07:30:01Z, replying: *"hm yeah this a little bit of a problem since the `valiateXXX` functions take a `cmp` as an extra parameter which is set by the `Validate` function. ... I wonder if there is a better way to do this ... Probably it would make sense to change this first and then adapt the tests or use them in a way that was originally intended."*
- **equalsgibson**, 2025-08-04T22:16:43Z, commit `703b7e0` ("Remove changes to testing format, and timefuncs"): *"Hey @oxisto, I've adjusted the test formats back to what they were originally - I agree, I should probably rework / revisit this in a separate unrelated PR."*
- The very next and final commit, `734a929` ("Change test to use NewValidator with opts", the pinned head), is where `Test_Validator_requireNotBefore` reaches its merged form — switching construction from `&Validator{...}` struct literals to `NewValidator(opts...)`, which *looks* like it addresses the concern (options are now genuinely applied to `v`) but does not, because the test still calls `v.verifyNotBefore(...)` directly rather than `v.Validate()`. Reviewers approved this final commit (oxisto "LGTM", mfridman approved) without re-raising the point for the new `nbf` test specifically.

So: the *general* failure mode behind GT-t1 was explicitly named and discussed by both the author and a maintainer, but explicitly deferred ("a separate unrelated PR") rather than fixed, and the deferral was never revisited for the new `requireNbf` test that shipped in the same PR. No participant flagged GT-t1 itself (the `requireNbf`-specific instance) by name.

# Leakage

A truncated mirror must exclude:
- The merge commit `9d770c8525013476c8d8a56f06e7d3c61d405203` and PR #456 itself (title says "add test coverage" — a strong hint to inspect the added test's adequacy).
- The intra-PR commits `30eed99`, `bd12f6b`, `703b7e0`, `a5214ec`, `734a929` — the visible commit history/diff traffic on `validator_test.go` (the back-and-forth of adding then stripping down a more thorough test rewrite) telegraphs that test coverage was contentious.
- The PR's review comments quoted above (`2248352598`, `2249156277`, `2252685086`) — these are properly part of "preexisting hints" available to reviewers pre-merge, but a mirror used to test *whether a reviewer can find the defect unaided* should decide deliberately whether to include or strip this discussion, since it directly primes the general failure mode (though not the specific `nbf` instance).
- No later commit, issue, or PR fixes or reports GT-t1 specifically — `git log --all -S "WithNotBeforeRequired" -- parser_test.go` returns nothing; `gh search issues/prs --repo golang-jwt/jwt "WithNotBeforeRequired"` returns only #456 itself and two unrelated later feature requests for an analogous `iat` option (#513, closed without merge; #520, open) that do not mention or fix this gap. Nothing to exclude on that front beyond #456 itself.

# Static visibility

Yes. The entire defect is establishable from the diff alone plus zero to one hop:
- The diff itself contains the full new test function (`validator_test.go` hunk) and the full production change (`validator.go` hunk showing `v.verifyNotBefore(claims, now, v.requireNbf)` inside `Validate()`).
- One hop (reading `Validate()`, already inside the diff) shows `v.requireNbf` is read nowhere else in production code.
- Comparing that single call site against the test's call to `v.verifyNotBefore(tt.args.claims, tt.args.cmp, tt.args.required)` (also inside the diff, same file) immediately shows the test never calls `Validate()` and passes `required` explicitly rather than through `v.requireNbf`.
- The weak-assertion half of the defect is visible by inspecting the one-line `if` condition at the bottom of the same added function — no callee hop needed at all.

No telemetry, fuzzing, or long-running reproduction was needed; the two mutation runs I performed were single-second `go test` invocations confirming what static reading already shows.

# Adjudicator's confidence and limits

High confidence in GT-t1: independently reproduced twice via mutation (both mutations left the full suite green), cross-checked against `main` as of 2026-09-08 (no later fix/coverage added), and corroborated by the PR's own review thread naming the general anti-pattern. High confidence the production code (`parser_option.go`, `validator.go`) itself is correct and clean — verified by direct end-to-end exercise (`Validate()` correctly returns `ErrTokenRequiredClaimMissing` for a missing `nbf` when required) and by diffing against the well-established, previously-shipped `requireExp` sibling pattern, which is identical in shape.

One thing I did not exhaustively verify: whether any *out-of-repo* consumer (e.g. a downstream project's own test suite, or a golang-jwt integration test outside this repository) happens to catch the `requireNbf` regression that this repository's own suite misses. That is `unresolved` — it would require searching GitHub-wide for consumers of `WithNotBeforeRequired`, which is out of scope for adjudicating this PR's own review record and test suite, and does not change the verdict that *this repository's* test suite, which is what a reviewer of this PR is responsible for, provides no protection.
