# Published review payload — kamui/cobra-holdout#9 (v5b, seed 1, r2, re-review)

Review URL: https://github.com/kamui/cobra-holdout/pull/9#pullrequestreview-5118176440
Reply URL: https://github.com/kamui/cobra-holdout/pull/9#discussion_r3938157948

## Summary body (as published, event COMMENT, commit 1107319c750f917bc3bf1c74a7705fe6e93123be)

**Approved (advisory)** — 0 must-fix findings, 0 consider findings, 1 observation, 0 open questions, 1 prior finding fixed. Delta review of `97b70019e9a3e2618c895c0e93c3fc6d7101fc17..1107319c750f917bc3bf1c74a7705fe6e93123be` since the prior review on this pull request.

**Intent:** Add a `COBRA_COMPLETION_DESCRIPTIONS`/`<PROGRAM>_COMPLETION_DESCRIPTIONS` environment variable, now parsed with `strconv.ParseBool`, that suppresses shell-completion descriptions equivalently to `--no-descriptions` for callers (such as third-party completion loaders) that invoke the hidden `__complete` command directly and cannot pass that flag.

**Issue fit:** Met — spf13/cobra#1937 asks for an env var equivalent to `--no-descriptions`; `completions.go:218` implements this inside the `__complete`/`__completeNoDesc` handler itself. The delta replaces the exact `off` string match with `strconv.ParseBool`, broadening accepted values to any boolean string, and makes the getter (`getEnvConfig`) unexported. Neither is a compatibility break: the whole surface is new and unreleased within this pull request, and the documentation (`site/content/completions/_index.md:397`) was updated in the same commits to describe the new accepted values.

**Coverage:** Complete delta diff reviewed since the prior review (`completions.go`, `completions_test.go`, `site/content/completions/_index.md`); `completions_test.go` was widened to the full `3518`–`3711` range because the delta overlaps both the prior finding's location and the new `TestDisableDescriptions` function. `active_help.go` carries no delta and remains covered by the prior round. The prior review's observation about coverage existing only through the `GetEnvConfig` unit test no longer holds: the delta adds `TestDisableDescriptions`, which now exercises the `__complete` handler end to end (`completions_test.go:3644-3706`).

**Reviewed:** `1107319c7` against merge-base `3d8ac432b`; delta since `97b70019e`.

## Prior findings

- [P3] [consider] Name each TestGetEnvConfig case with t.Run — fixed. `completions_test.go:3586` now wraps each case in `t.Run(tc.desc, ...)` with a `desc` field per case, matching `TestGetFlagCompletion`'s convention; landed in `9740ecead`.

## Observations

- `TestDisableDescriptions` only unsets `ROOT_COMPLETION_DESCRIPTIONS`/`COBRA_COMPLETION_DESCRIPTIONS` when a case's value is empty, leaving both set after its final case runs. Evidence: `completions_test.go:3663`, `completions_test.go:3697-3706`.

## Ambiguities

- **Proven consequence for the `TestDisableDescriptions` residual env state:** one reading ties consequence to this repository's actual invocation (`Makefile`'s `go test -v ./...`/`richgo test -v ./...`, no `-shuffle`), under which the residual value equals the unset default and nothing observably breaks; a broader reading treats any reachable `go test` flag as sufficient consequence on its own. The narrower reading, tied to the repository's actual invocation, governed this run, routing the fact to Observations rather than a `consider` finding.

<!-- review-run head=1107319c750f917bc3bf1c74a7705fe6e93123be base-ref=main base-sha=3d8ac432bdad89db04ab0890754b2444d7b4e1cf merge-base=3d8ac432bdad89db04ab0890754b2444d7b4e1cf workflow=v5b-1 context=936fd96d5d5f7758ca3195c2250fc013bd355b826381bc13972fb28d9d4afe92 issues=spf13/cobra#1937 coverage=complete -->

## Thread reply (as published, replying to discussion_r3938095840 / completions_test.go:3594-3710)

**Implemented** — `completions_test.go:3586` now sets `desc` per case and wraps the loop body in `t.Run(tc.desc, func(t *testing.T) { ... })`, matching `TestGetFlagCompletion`'s existing convention.

**Verification:** Traced statically against the delta; `9740ecead` ("Distinguish env var getter test cases better") adds the `desc` field and the `t.Run` wrapper for all five cases.

<!-- reply to=completions/getenvconfig-test-missing-subtests disposition=implemented head=1107319c750f917bc3bf1c74a7705fe6e93123be -->
