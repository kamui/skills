# Review payload — graphql/graphql-js#1582 (retrospective, publication disabled)

This is the review exactly as it would have been posted as one GitHub `COMMENT`-event
review (summary + inline comments in one native batch), had publication been authorized.
It was rendered by `scripts/validate_review.py --render` / `--emit-batch` from
`/tmp/qual137/work/k-867cf3ff-seed2-att-19/payload.json` (validator exit 0), and nothing
was written to the pull request.

## Summary body

**Approved (advisory)** — 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Enable Flow typings (`@flow strict`) on the GraphQLError/locatedError/printError/inspect test suites, and fix the `GraphQLError` constructor's ambient type so `nodes` accepts `null` like every other constructor argument, per the reviewer's own comment on this commit.

**Issue fit:** No linked issue; the PR body is empty. Judged against the PR title's two stated goals, both are met: all four touched test files now carry `@flow strict` headers, and `nodes?: ... | void` gained `| null` in the `declare class` signature (`src/error/GraphQLError.js:25`), matching the requested parity with the constructor's other arguments.

**Coverage:** Complete merge-base diff reviewed (5 files, +48/-47). The PR's sole review thread (`GraphQLError.js:25`, requesting `null` support for `nodes`) is already resolved in the reviewed head. Ran `src/error/__tests__/GraphQLError-test.js` under mocha (13 passing) and a scratch probe confirming `e.stack === original.stack` for the finding below.

**Reviewed:** `7e39a122eea9292eeffa6905ffdf8a60c5161cfd` against merge-base `5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11`.

## Findings

- [P2] [consider] Give the "no stack" double an actual missing `.stack` — anchor [`src/error/__tests__/GraphQLError-test.js:58`](https://github.com/graphql/graphql-js/blob/7e39a122eea9292eeffa6905ffdf8a60c5161cfd/src/error/__tests__/GraphQLError-test.js?plain=1#L58)

## Observations

- The `nodes` constructor parameter gained `| null` only in the ambient `declare class` signature, not in the exported implementation function's own signature, mirroring how `GraphQLList` and `GraphQLNonNull` in `src/type/definition.js` already leave their implementation functions unannotated relative to their `declare class` counterparts. Evidence: `src/error/GraphQLError.js:94`, `src/type/definition.js:349`.

<!-- review-run head=7e39a122eea9292eeffa6905ffdf8a60c5161cfd base-ref=master base-sha=5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11 merge-base=5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11 workflow=v5b-1 context=2f460df7d4bbfa66725887115e49119100fa089004fbc86dc9f62a0a6fa62257 issues=none coverage=complete -->

## Inline finding comment

**Anchor:** `src/error/__tests__/GraphQLError-test.js:58` (RIGHT side, single line)

```markdown
**[P2] [consider] Give the "no stack" double an actual missing `.stack`**

**Triggers when:** `originalError` passed into `GraphQLError` already carries a `.stack` property, which every real `Error` instance does.

**Impact:** The constructor's `if (originalError && originalError.stack)` branch reuses `originalError.stack` verbatim, so this test (named for the fallback that creates a *new* stack) actually exercises the reuse branch instead; `e.stack === original.stack` holds. A regression in the `Error.captureStackTrace` fallback this test claims to cover would go undetected.

**Change:** In `src/error/__tests__/GraphQLError-test.js`, give `original` a double that genuinely lacks `.stack` (e.g. `const original: any = { message: 'original' };`, matching the `: any` cast this same PR already uses in `locatedError-test.js`) instead of `new Error('original')`.

Closing this without action is a correct response.

<!-- finding id=error-tests/no-stack-double head=7e39a122eea9292eeffa6905ffdf8a60c5161cfd priority=P2 action=consider blocking=false kind=bug -->
```

## Would-be forge-native batch (`--emit-batch` output, event=COMMENT, not submitted)

```json
{
  "commit_id": "7e39a122eea9292eeffa6905ffdf8a60c5161cfd",
  "event": "COMMENT",
  "body": "<the summary body above, verbatim>",
  "comments": [
    {
      "path": "src/error/__tests__/GraphQLError-test.js",
      "line": 58,
      "side": "RIGHT",
      "body": "<the inline finding comment above, verbatim, plus its trailer>"
    }
  ]
}
```

Full JSON with escaped body/comment text is preserved at
`/tmp/qual137/work/k-867cf3ff-seed2-att-19/batch.json`.
