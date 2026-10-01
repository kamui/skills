# Review payload — `kamui/cobra-holdout#9` — v5b seed1 r1

Published as one forge-native review, event `COMMENT`, state `COMMENTED`.
Review URL: https://github.com/kamui/cobra-holdout/pull/9#pullrequestreview-5118103257
Reviewed head (`commit_id`): `97b70019e9a3e2618c895c0e93c3fc6d7101fc17`

This is a first review (no prior review state existed to reply to), so there are no thread replies.

## Summary body (exactly as published)

**Approved (advisory)** — 0 must-fix findings, 1 consider finding, 1 observation, 0 open questions.

**Intent:** Add a `COBRA_COMPLETION_DESCRIPTIONS`/`<PROGRAM>_COMPLETION_DESCRIPTIONS` environment variable that suppresses shell-completion descriptions equivalently to `--no-descriptions`, for callers (such as third-party completion loaders) that invoke the hidden `__complete` command directly and cannot pass that flag.

**Issue fit:** Met — spf13/cobra#1937 asks for an env var equivalent to `--no-descriptions`; `completions.go:215` implements this inside the `__complete`/`__completeNoDesc` request handler itself, so it also covers callers that bypass the generated shell scripts. The issue's suggested variable name/value scheme was explicitly tentative ("something like"); the implemented `<PROGRAM>_COMPLETION_DESCRIPTIONS=off` (falling back to `COBRA_COMPLETION_DESCRIPTIONS=off`) scheme is a valid representation of the same required outcome and is documented in `site/content/completions/_index.md`.

**Coverage:** Complete merge-base diff reviewed (`active_help.go`, `completions.go`, `completions_test.go`, `site/content/completions/_index.md`); the `activeHelpEnvVar` refactor was traced against its merge-base implementation and produces an identical environment-variable name for every input.

**Reviewed:** `97b70019e` against merge-base `3d8ac432b`.

## Findings

- [P3] [consider] Name each TestGetEnvConfig case with t.Run — anchor [`completions_test.go:3579-3594`](https://github.com/kamui/cobra-holdout/blob/97b70019e9a3e2618c895c0e93c3fc6d7101fc17/completions_test.go?plain=1#L3579-L3594)

## Observations

- The new environment-variable branch for suppressing completion descriptions is exercised only through its `GetEnvConfig` helper's unit test, not through the `__complete` request handler itself. Evidence: `completions.go:215`, `completions_test.go:3522`.

<!-- review-run head=97b70019e9a3e2618c895c0e93c3fc6d7101fc17 base-ref=main base-sha=3d8ac432bdad89db04ab0890754b2444d7b4e1cf merge-base=3d8ac432bdad89db04ab0890754b2444d7b4e1cf workflow=v5b-1 context=936fd96d5d5f7758ca3195c2250fc013bd355b826381bc13972fb28d9d4afe92 issues=spf13/cobra#1937 coverage=complete -->

## Finding comment — `completions/getenvconfig-test-missing-subtests`

Comment URL: https://github.com/kamui/cobra-holdout/pull/9#discussion_r3938095840
Anchor: `completions_test.go:3579-3594`, side `RIGHT` (line comment, `start_line=3579`, `line=3594`)

```markdown
**[P3] [consider] Name each TestGetEnvConfig case with t.Run**

**Triggers when:** One case in `TestGetEnvConfig`'s five-case table fails.

**Impact:** `go test -run TestGetEnvConfig/<name>` cannot target the failing case, and `go test -v` reports only the outer `TestGetEnvConfig` result, so a maintainer must match the `t.Errorf` values back to a table row by hand instead of reading a named subtest.

**Change:** Add a `desc` field to each case and wrap the loop body in `t.Run(tc.desc, func(t *testing.T) { ... })`, matching the convention `TestGetFlagCompletion` already uses in this file.

Closing this without action is a correct response.

<!-- finding id=completions/getenvconfig-test-missing-subtests head=97b70019e9a3e2618c895c0e93c3fc6d7101fc17 priority=P3 action=consider blocking=false kind=maintainability -->
```

No questions were published (none met the static-unresolvability bar). No thread replies were published (first review, no prior state).
