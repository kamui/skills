You are a research assistant vetting candidate pull requests for a controlled evaluation of an AI code-review skill. Work on this machine, use `gh` and `git` freely (network is available), and write your report to `/tmp/qual137/hunts/ordinary.md`. Do not stop to ask questions; finish in this dispatch.

## What I need — TWO separate candidates

**(A) One merged pull request containing an ORDINARY BEHAVIOURAL DEFECT.** A plain correctness bug in the behaviour the change touches: an off-by-one, a wrong branch condition, a mishandled error or edge case, a wrong default, a boundary that is not handled, a resource not released on one path. Deliberately NOT a concurrency bug, NOT a bug that only shows up through a cross-file invariant, NOT a security issue — those shapes are covered by other targets in this grid. It should be the kind of defect a careful reviewer catches by reading the changed code and its immediate neighbours.

It must be **independently confirmed after the fact** by the upstream project: a later fix, revert, or issue that identifies exactly this bug. I need its exact SHAs so I can hide them from the reviewer.

**(B) One merged pull request that is genuinely CLEAN** — no material defect at all — of ordinary risk. Not a concurrency/failover/data-integrity/security surface (a separate clean control in this grid already covers the high-risk shape). An everyday behavioural change: a new option, a refactor with a behaviour tweak, a bug fix in ordinary logic. It must be substantial enough that a reviewer has real work to do, and it must contain at least one **tempting but false** objection — something that looks wrong on the diff and is actually correct. Prove cleanliness: show that nothing in the following months fixed, reverted or complained about this change.

## Hard constraints (both candidates)

1. **Merged at least 6 months before 2026-09-06**, so downstream history exists.
2. **Small diff:** at most ~250 changed lines across at most ~6 files. Hard budget — reject anything larger.
3. **Public repository, permissively licensed, real project with real maintainers.**
4. **The review trail must be visible through `gh`** (GitHub-native reviews/threads/comments), not on an external tool like Reviewable.io.
5. **Offline-runnable focused tests.** After a one-time provisioning step with network, it must be possible to run the relevant focused tests offline in under 5 minutes on macOS. Go, Rust, Python and Node are all fine. Say exactly which commands and environment variables, and how long provisioning and the tests each took **when you actually ran them**.
6. **NOT any of these — already used or reserved; check every candidate against this list:** hyperium/hyper#3952, hashicorp/raft#581, python/typeshed#9458, astral-sh/uv#4424, pola-rs/polars#24771, spf13/cobra#1938, tokio-rs/bytes#698, etcd-io/etcd#18749, psf/requests#6667, cockroachdb/pebble#5743, quic-go/quic-go#5220, etcd-io/bbolt#1179, golang-jwt/jwt#456, libuv/libuv#4400, etcd-io/etcd#17563, microsoft/playwright#29698, microsoft/playwright#29811, microsoft/playwright#30111, redis/redis#15530, redis/redis#15680, tokio-rs/tokio#7757.
7. For (A), the defect **must be statically visible** to a careful reviewer, and **must NOT be the behaviour change the pull request openly promises** — it has to be an unintended error, not the contract change the PR asked for.
8. Prefer two different languages/ecosystems for (A) and (B) if you can, to spread the grid.

## What to report, for each candidate and for at least one alternate each

- Repository, PR number, title, author, merge timestamp, base branch.
- head SHA, PR-recorded base SHA, and the **`git merge-base` you computed yourself on a full clone** — say explicitly whether they agree.
- Complete changed-file manifest with +/- per file.
- Originating issue, if any.
- Prior review record: how many reviews/threads/comments, who, whether anyone raised the defect (for A) or the tempting objection (for B). Quote the substantive comments.
- For (A): **the defect** precisely — file, function, lines; expected behaviour; trigger; demonstrated consequence; the confirming later PR/issue/commit with SHAs, dates, and the verbatim sentence where the project identifies it; and the corrective outcome a correct review must require.
- For (B): **the cleanliness evidence** — what you searched, over what window, and what you found; the surface a correct review must NOT assert as a defect.
- **Tempting false positives**: at least three for each candidate, each with why it is wrong.
- **SHAs a truncated mirror must exclude**, and the issue/PR numbers to hide.
- **Test evidence you actually ran**: exact commands, exit status, duration, output summary, at head and at merge-base.
- **Confidence**, with reasoning.

Be exhaustive and concrete. A candidate you have not verified with real commands is not a candidate. If nothing meets the bar, say so plainly and report the closest misses with the reason each fails.
