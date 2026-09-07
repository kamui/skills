You are a research assistant vetting one candidate pull request for a controlled evaluation of an AI code-review skill. Work on this machine, use `gh` and `git` freely (network is available), and write your report to `/tmp/qual137/hunts/clean-highrisk.md`. Do not stop to ask questions; finish in this dispatch.

## What I need

**One merged pull request that is genuinely CLEAN — no material defect at all — on a HIGH-RISK surface.** High-risk means the change touches a concurrency or failover path, a data-integrity surface, or a security or authorization boundary. It is a control: a correct reviewer must return it with no material finding.

The value of the target is that it **looks** dangerous. It must contain at least two **tempting but false** objections — things that look wrong on the diff and are provably correct once you follow them out. Ideally one of those objections was actually raised by a human reviewer on the pull request and answered.

You must **prove cleanliness**: show that in the months since the merge nothing fixed, reverted, or reported a defect in this change. Say exactly what you searched, over what window, and what you found.

## Hard constraints

1. **Merged at least 6 months before 2026-09-06**, so downstream history exists.
2. **Small diff: at most 200 changed lines across at most 6 files.** Hard budget — I will mechanically re-check and reject a candidate that misses it.
3. **Public repository, permissively licensed, real project with real maintainers.**
4. **The review trail must be visible through `gh`** (GitHub-native reviews/threads/comments), not on an external tool like Reviewable.io. This disqualifies cockroachdb repositories.
5. **CRITICAL — comment edit provenance.** My packet builder freezes the pull request at its merge instant and refuses to build if any admitted input was edited after that instant. So: for the pull-request **body**, every **review**, every **review-thread comment**, every **conversation comment**, and every comment on any **closing issue**, report `createdAt`/`submittedAt` **and `lastEditedAt`**. A candidate is only usable if **no** such record has a `lastEditedAt` later than the pull request's `mergedAt`. Bot comments (codecov, CI) are the usual offenders — they edit themselves at merge time. Check this with a GraphQL query and paste the result. **Reject any candidate that fails it** and say so.
6. **Offline-runnable focused tests.** After a one-time provisioning step with network, it must be possible to run the relevant focused tests offline in under 5 minutes on macOS. Go, Rust, Python and Node are all fine. Say exactly which commands and environment variables, and how long provisioning and the tests each took **when you actually ran them**.
7. **NOT any of these — already used or reserved; check every candidate:** hyperium/hyper#3952, hashicorp/raft#581, python/typeshed#9458, astral-sh/uv#4424, pola-rs/polars#24771, spf13/cobra#1938, tokio-rs/bytes#698, etcd-io/etcd#18749, psf/requests#6667, cockroachdb/pebble#5743, quic-go/quic-go#5220, etcd-io/bbolt#1179, golang-jwt/jwt#456, libuv/libuv#4400, etcd-io/etcd#17563, microsoft/playwright#29698, microsoft/playwright#29811, microsoft/playwright#30111, redis/redis#15530, redis/redis#15680, tokio-rs/tokio#7757.

## What to report, for your top pick and for at least two alternates

- Repository, PR number, title, author, merge timestamp, base branch.
- head SHA, PR-recorded base SHA, and the **`git merge-base` you computed yourself on a full clone** — say explicitly whether they agree.
- Complete changed-file manifest with +/- per file, and the **total changed-line count**.
- Originating issue, if any.
- **The edit-provenance table required by constraint 5**, in full.
- Prior review record: how many reviews/threads/comments, who, and the substantive comments quoted.
- **Why it is high-risk**: which concurrency, failover, data-integrity, security or authorization surface it touches, concretely.
- **Cleanliness evidence**: what you searched, the window, and the result. Include `git log` over the changed files since the merge, and issue/PR searches.
- **Tempting false positives**: at least three, each with the reason it is wrong, and whether a human reviewer raised it.
- **The ground-truth surface a correct review must NOT assert as a defect.**
- **SHAs a truncated mirror must exclude**, and the issue/PR numbers to hide.
- **Test evidence you actually ran**: exact commands, exit status, duration, output summary, at head and at merge-base.
- **Confidence**, with reasoning.

Be exhaustive and concrete. A candidate you have not verified with real commands is not a candidate. If nothing meets the bar, say so plainly and report the closest misses with the reason each fails.
