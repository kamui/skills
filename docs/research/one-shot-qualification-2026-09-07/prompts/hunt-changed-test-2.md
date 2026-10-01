You must do ALL of this work YOURSELF in this session. Do NOT use the Agent tool and do NOT dispatch any sub-agent: this harness terminates a headless session that waits on background workers, and a previous attempt at this task died that way. Work single-threaded. GitHub's code-search endpoint allows only 30 queries per minute, so pace search calls and prefer `git log`/`git log -S` on a local clone over repeated API searches.

You are a research assistant vetting one candidate pull request for a controlled evaluation of an AI code-review skill. Work on this machine, use `gh` and `git` freely (network is available), and write your report to `/tmp/qual137/hunts/changed-test.md`. Do not stop to ask questions; finish in this dispatch.

## What I need

**One merged pull request whose own CHANGED TEST is materially defective.** The defect must be in a test the pull request adds or substantively changes: the test asserts the wrong thing, is tautological or vacuous (cannot fail), tests a different code path than the one it claims to cover, has a swapped/inverted expectation, sleeps instead of synchronising and is therefore flaky-by-construction, or silently swallows the failure it is supposed to catch. The production change may be fine; the *test* is the defect.

This must be **independently confirmed after the fact** by the upstream project: a later commit, pull request or issue that fixes/rewrites/removes that test and says why, or a reported escape that the broken test failed to catch. I need that confirmation to exist, and I need its exact SHAs so I can hide them from the reviewer.

## Hard constraints

1. **Merged at least 6 months before 2026-09-06** (so downstream history exists), and the confirming fix must also already exist.
2. **Small diff:** at most ~250 changed lines total across at most ~6 files. Smaller is better. This is a hard budget — reject anything larger.
3. **Public repository, permissively licensed, real project with real maintainers.** Popular enough that the review trail is meaningful.
4. **The review trail must be visible through `gh`** (GitHub-native reviews/threads/comments), not on an external tool like Reviewable.io.
5. **Offline-runnable focused tests.** After a one-time provisioning step with network (dependency download / module cache warm), it must be possible to run the relevant focused test offline in under 5 minutes on macOS. Go, Rust, Python and Node are all fine. Say exactly which commands, which environment variables, and how long provisioning and the test each took **when you actually ran them**.
6. **NOT any of these — already used or reserved by earlier experiments; check every candidate against this list:** hyperium/hyper#3952, hashicorp/raft#581, python/typeshed#9458, astral-sh/uv#4424, pola-rs/polars#24771, spf13/cobra#1938, tokio-rs/bytes#698, etcd-io/etcd#18749, psf/requests#6667, cockroachdb/pebble#5743, quic-go/quic-go#5220, etcd-io/bbolt#1179, golang-jwt/jwt#456, libuv/libuv#4400, etcd-io/etcd#17563, microsoft/playwright#29698, microsoft/playwright#29811, microsoft/playwright#30111, redis/redis#15530, redis/redis#15680, tokio-rs/tokio#7757.
7. **The defect must be statically visible** to a careful reviewer reading the diff plus a bounded amount of surrounding code — not something that needs production telemetry or a week of fuzzing.
8. **The defect must NOT be the behaviour change the pull request openly promises.** It has to be an unintended error.

## What to report, for your top pick and for at least two alternates

- Repository, PR number, title, author, merge timestamp, base branch.
- head SHA, PR-recorded base SHA, and the **`git merge-base` you computed yourself on a full clone** — say explicitly whether they agree.
- Complete changed-file manifest with +/- per file.
- Originating issue, if any, with its number.
- Prior review record: how many reviews/threads/comments, who, and whether anyone raised the defect. Quote the substantive comments.
- **The defect**, precisely: which test function, which file, which lines; what the test claims to check; what it actually checks; the trigger and the demonstrated consequence (what escaped, or what a maintainer said when fixing it).
- **The confirming evidence**: the exact later PR/issue/commit, with SHAs and dates, and the verbatim sentence where the project says the test was wrong.
- **The corrective outcome** a correct review would have to require.
- **Tempting false positives**: at least three plausible-but-wrong objections a reviewer might raise on this diff, each with why it is wrong.
- **SHAs a truncated mirror must exclude** so the reviewer cannot see the fix: every merge, revert and follow-up SHA, and the issue/PR numbers to hide.
- **Test evidence you actually ran**: the exact commands, exit status, duration, and output summary, at the PR head and at the merge-base.
- **Confidence that the defect is statically visible**, with your reasoning.

Be exhaustive and concrete. A candidate you have not verified with real commands is not a candidate. If nothing meets the bar, say so plainly and report the closest misses with the reason each fails.
