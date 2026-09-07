You are a research assistant vetting one candidate pull request for a controlled evaluation of an AI code-review skill. Work on this machine, use `gh` and `git` freely (network is available), and write your report to `/tmp/qual137/hunts/crossfile.md`. Do not stop to ask questions; finish in this dispatch.

## What I need

**One merged pull request whose defect is only visible by reading a file the diff never touches.** The changed code looks locally correct; it violates a contract, invariant, or documented obligation that lives somewhere else in the repository — an interface or trait definition, a caller that depends on a post-condition, a config/schema/constant table that must be kept in step, a documented guarantee in an AGENTS.md/CONTRIBUTING.md/docs page, a sibling implementation that must stay consistent, or a versioned artifact whose obligations the change fails to discharge. The point is that a reviewer who reads only the diff and its immediate neighbours will miss it, while a reviewer who follows the change out to the untouched file will find it.

It must be **independently confirmed after the fact** by the upstream project: a later fix, revert, or issue that identifies exactly this. I need its exact SHAs so I can hide them from the reviewer.

## Hard constraints

1. **Merged at least 6 months before 2026-09-06**, so downstream history exists, and the confirming fix must already exist.
2. **Small diff: at most 200 changed lines across at most 6 files.** Hard budget — reject anything larger. Smaller is much better. I will mechanically re-check this and reject a candidate that misses it.
3. **Public repository, permissively licensed, real project with real maintainers.**
4. **The review trail must be visible through `gh`** (GitHub-native reviews/threads/comments), not on an external tool like Reviewable.io. This disqualifies cockroachdb repositories, which review on Reviewable.io.
5. **Offline-runnable focused tests.** After a one-time provisioning step with network (dependency download / module cache warm), it must be possible to run the relevant focused tests offline in under 5 minutes on macOS. Go, Rust, Python and Node are all fine. Say exactly which commands and environment variables, and how long provisioning and the tests each took **when you actually ran them**.
6. **NOT any of these — already used or reserved; check every candidate against this list:** hyperium/hyper#3952, hashicorp/raft#581, python/typeshed#9458, astral-sh/uv#4424, pola-rs/polars#24771, spf13/cobra#1938, tokio-rs/bytes#698, etcd-io/etcd#18749, psf/requests#6667, cockroachdb/pebble#5743, quic-go/quic-go#5220, etcd-io/bbolt#1179, golang-jwt/jwt#456, libuv/libuv#4400, etcd-io/etcd#17563, microsoft/playwright#29698, microsoft/playwright#29811, microsoft/playwright#30111, redis/redis#15530, redis/redis#15680, tokio-rs/tokio#7757.
7. **The defect must be statically visible** to a careful reviewer who follows the change outward — not something that needs production telemetry or long fuzzing.
8. **The defect must NOT be the behaviour change the pull request openly promises.** It has to be an unintended error.
9. Prefer a repository that is NOT Go if you can — the grid already has Go and Python targets — but a strong Go candidate beats a weak non-Go one.

## What to report, for your top pick and for at least two alternates

- Repository, PR number, title, author, merge timestamp, base branch.
- head SHA, PR-recorded base SHA, and the **`git merge-base` you computed yourself on a full clone** — say explicitly whether they agree.
- Complete changed-file manifest with +/- per file, and the **total changed-line count**.
- Originating issue, if any.
- Prior review record: how many reviews/threads/comments, who, whether anyone raised the defect. Quote the substantive comments.
- **The defect**, precisely: which changed lines, and **which untouched file and which lines in it** carry the violated obligation; what the obligation says verbatim; the trigger; the demonstrated consequence.
- **The confirming evidence**: the exact later PR/issue/commit, SHAs, dates, and the verbatim sentence where the project identifies it.
- **The corrective outcome** a correct review would have to require.
- **Tempting false positives**: at least three plausible-but-wrong objections a reviewer might raise on this diff, each with why it is wrong.
- **SHAs a truncated mirror must exclude**, and the issue/PR numbers to hide.
- **Test evidence you actually ran**: exact commands, exit status, duration, output summary, at head and at merge-base.
- **Confidence that the defect is statically visible**, with reasoning.

Be exhaustive and concrete. A candidate you have not verified with real commands is not a candidate. If nothing meets the bar, say so plainly and report the closest misses with the reason each fails.
