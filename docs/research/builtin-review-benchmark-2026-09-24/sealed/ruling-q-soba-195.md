# Ruling: q-soba-195 (jonhadfield/soba#195, "refactor: resolve SonarQube findings")

## Target

| | |
|---|---|
| Repository | `jonhadfield/soba` (MIT) |
| Pull request | #195, author `jonhadfield` (the repository owner), squash-merged 2026-07-30T07:53:54Z |
| Head | `136a4850df9aec8cf8813b27ba1533d4a17bc642`, the PR's only commit (`gh pr view 195 --json commits`) |
| Merge-base | `c77f548cbd340d2e744da7c6d92a54372b4b900b`. It equals the PR-recorded `baseRefOid` and the computed `git merge-base 136a4850 06922a22`. |
| Merge commit | `06922a224f36436511eb098e9c698b6966b58b78` (parent `c77f548c`). `git diff --stat 136a4850 06922a22` is empty, so its tree equals the head's. |
| Changed files | `docker/Dockerfile` +3/−4, `internal/backup.go` +246/−201, `internal/backup_test.go` +45/−72, `internal/notify.go` +18/−28 |
| Stated contract | PR body: "decomposed into focused helpers. Behaviour and log output are unchanged." Squash message: "behaviour and log output unchanged." |
| Slot | (q), a mechanical refactor claiming no behaviour change, expected clean |

## Verdict

adjudicated clean

## Defect register

None.

I found no material defect as defined in `bench/rubric/scoring.v1.md`. Every production hunk was compared line by line with the base, then mechanically with the harnesses described under Reproduction. Two differences are observable. Both are true, and neither is material:

- **Nuance A (startup log text for exotic Unicode).** `displayBitBucketStartupConfig` → `logProviderCompareMethod` uses `strings.EqualFold` where the base used `strings.ToLower(c) == "refs"`.
  - `BITBUCKET_COMPARE=refſ` (U+017F) or `ReFſ` now logs "BitBucket compare method: refs"; the base logged "clone". I reproduced this at both revisions.
  - For every ASCII input the output is identical.
  - The GitHub, Gitea, GitLab and Azure DevOps lines already used `EqualFold` at the base, so the BitBucket line now matches its siblings.
  - The change only affects this log line; backups are unaffected. Which compare method a backup uses is decided outside this diff.
- **Nuance B (one fewer diagnostic line at backup time).**
  - `collectProviderBackupResults` evaluates `bitbucketAPITokenDefined() || bitbucketOAuthDefined()` with short-circuiting.
  - When the API token pair is complete, the three OAuth variables are not read in the gate. So an OAuth `*_FILE` pointing at a missing or unopenable file no longer logs its "file … does not exist" or "error opening file" line from the gate.
  - The same line is still logged once by `Bitbucket()` (`internal/bitbucket.go:15-21`), which re-reads all five variables.
  - The gate's boolean result is unchanged. In 20,000 random configurations it differed 0 times; the log differed in 623 of them, always in this way.
  - By construction, the head's gate log is either identical to the base's or its prefix: the base's two API-variable reads.

## Reproduction

Environment: Go 1.26.5 linux/amd64; `GOCACHE` and `GOPATH` under `work/`.
- Clone: `work/soba`, cloned from the sealed bare mirror; live `main` was fetched separately as `live/main` (`c39e6c0`).
- No credentials were used: `GITHUB_TOKEN`, `GITLAB_TOKEN` and `GITEA_TOKEN` were unset.
- Harness files were copied into `internal/` only while they ran, then removed. `git status --short` was empty after every run.

| Step | Revision | Command | Exit | Duration | Result |
|---|---|---|---|---|---|
| deps | head | `go mod download` | 0 | — | — |
| vet | head | `go vet ./internal/` | 0 | 5.6 s | clean |
| repo suite | head `136a4850` | `go test ./... -count=1 -v` | 0 | 6.7 s | 24 PASS, 15 SKIP, 0 FAIL at top level (`work/gotest-head.log`) |
| repo suite | base `c77f548c` | same | 0 | 6.0 s | 24 PASS, 16 SKIP, 0 FAIL (`work/gotest-base.log`) |
| suite diff | both | diff of the sorted `--- PASS/SKIP/FAIL` lines | — | — | The only difference is `--- SKIP: TestPublicGitLabRepositoryBackup2` at the base: the deleted duplicate. |
| differential harness | head | `go test ./internal/ -run 'TestAdjEquivalence\|TestAdjFold' -count=1` with `work/adj_equiv_test.go` | 0 | 2.8 s | `work/equiv-136a4850.txt` |
| differential harness | base | same file | 0 | 2.7 s | `work/equiv-c77f548c.txt` |
| comparison | both | `sed 's#/tmp/sobabackup-[0-9]+#…X#'`, then `cmp` and `sha256sum` | — | — | **Identical**, sha256 `171ea46c98e364813e7ddd8c0a257165b147fa3ee0a00a55f8635b0c6862d4f3` for both (the raw files differ only in the random `/tmp/sobabackup-N` directory that `backup_test.go:159` creates) |
| fold probe | both | `TestAdjFold` (in the same file) | 0 | — | Differs only on `BITBUCKET_COMPARE="refſ"` and `"ReFſ"`: base "clone", head "refs" (nuance A). `GITHUB_COMPARE` behaves identically at both revisions. |
| head-only differential | head | `go test ./internal/ -run TestAdjHeadOnly -count=1 -v` with `work/adj_headonly_test.go` | 0 | 2.4 s | `gateMismatch=0 cpdMismatch=0 nilCount=579 gateLogDiffCases=623` (`work/headonly.log`) |

**Differential harness** (`adj_equiv_test.go`). This is my own harness; I did not open the vetting pass's `zz_equiv_test.go`. It is revision-neutral: it calls only `displayStartupConfig`, `checkProvidersDefined`, `checkProvider` and `sendNtfy`, all of which exist at both revisions.
- 25,000 seeded configurations (PCG seed 195) over 31 provider variables.
- Each variable is either unset (40%), set from a pool of 21 values (40%), or given a `*_FILE` pointing at a good, a `refs`, an empty, a blank or a missing file (20%).
- The value pool includes empty, spaces, refs/REFS/Refs/rEfS/" refs", clone/CLONE, true/false/yes/y/1/0, numbers, and org lists.
- For each configuration it captures:
  - the full `displayStartupConfig()` log (logger flags 0);
  - the `checkProvidersDefined()` error and log, with lines sorted because both revisions iterate a Go map;
  - `checkProvider(p)` count, error and log for Azure DevOps, GitHub, GitLab, Gitea and Sourcehut.
- It also captures the ntfy `Title` header for all nine (succeeded, failed) ∈ {0,1,2}² pairs through an `httptest` server.
- The output has 477,724 lines: 6,583 "compare method: refs" lines, 5,268 `<nil>` results, and 35,950 "does not exist" lines.

**Head-only differential** (`adj_headonly_test.go`) checks two things in-process against verbatim copies of the base code, over 20,000 further configurations:
- The head's Bitbucket gate, `bitbucketAPITokenDefined() || bitbucketOAuthDefined()`, against the base's inline gate from `runProviderBackups`.
- The head's `checkProvidersDefined` against the base's, with the map order made explicit and **both** relative orders of the `BitBucketAPIToken`/`BitBucketOAuth` keys tried.

Neither showed a mismatch. This settles the map-order hoisting question empirically, not just by argument.

**Static checks**
- The notification titles are byte-identical. `xxd` of the three string literals at base and head matches, including the leading U+FE0F (`ef b8 8f`) on the warning and failure titles. The base had three identical copies of each literal: Telegram, ntfy and Slack.
- At the base, the body of `TestPublicGitLabRepositoryBackup2` is byte-identical to `TestPublicGitLabRepositoryBackup` (awk extract, then `cmp`).
- The refactored `TestGiteaOrgsRepositoryBackup` helpers keep every assertion, in the same order. The double `resetBackups()` was already present at the base (`backup_test.go` lines 669, 703 and 706 at the base).

**Not run**
- The Dockerfile was not built: the Docker daemon is not reachable from this WSL distro ("docker could not be found in this WSL 2 distro"). The Dockerfile ruling is static.
- The live-provider tests were not run (no credentials).

## Not ground truth

Each item below is a plausible reviewer claim that is **not** a material defect.

1. **"Hoisting `bitbucketAPITokenDefined()` out of the loop in `checkProvidersDefined` changes provider counting."**
   - At the base, when both methods were complete and the map visited `BitBucketOAuth` first, `count` was 2; otherwise it was 1. At the head it is always 1.
   - `count` is only compared with 0 (`backup.go:712`), and it is not returned.
   - The same `GetEnvOrFile` reads happen; only their position moved, within an order that was already map-random.
   - The head-only harness found 0 mismatches over 20,000 configurations × 2 orders.
2. **"The short-circuit `||` drops the OAuth check, so OAuth-only users lose Bitbucket backups."**
   - The OAuth check is skipped only when the API token pair is already complete. Otherwise `bitbucketOAuthDefined()` is evaluated as before.
   - The gate's boolean result never differed (0 of 20,000).
   - `Bitbucket()` re-reads all five variables itself, so the backup is the same. The only observable effect is nuance B.
3. **"`collectProviderBackupResults` changes provider order or conditions."**
   - The order is still Bitbucket, then Gitea, GitHub, GitLab, Azure DevOps and Sourcehut.
   - The table uses the same env-var-to-function pairs as the five removed `if` blocks, with the same `ok && val != ""` test.
   - With no providers the result is still a nil slice.
4. **"The typos 'Organistations' / 'Gitlab backup LFS' should be fixed"** (Copilot on `backup.go:207`).
   - Both strings are carried over verbatim from the base.
   - Changing them would break the PR's explicit promise of unchanged log output. Pointing out a typo is at most a non-material remark, not a regression.
5. **"The early returns in `display*StartupConfig`, or `ghOrgsExists && !githubTokenExists`, invert the checks."** Both are exact De Morgan and nesting equivalents. The harness captured identical startup logs.
6. **"`runScheduledJob` shadows the global `job`, or loses the scheduler error."**
   - `var err error; job, err = s.NewJob(...)` assigns the package-level `var job gocron.Job` (`backup.go:737`).
   - `errors.Wrap(err, "failed to create job")` is unchanged.
   - Option order is unchanged: `WithStartAt(WithStartImmediately())` is still passed only in interval mode.
   - The blocking `s.Start(); waitForShutdown(s)` and the final `nil` return are unchanged.
7. **"`Run`'s decomposition changes validation order or messages."** The order is unchanged: git path, startup display, git version, request timeout, backup dir, GitHub orgs/token, stat, providers, working dir, scheduler. So are the error strings. The helpers only add `""` as the first return value on error paths.
8. **"`Printf("%s compare method: %s", label, method)` changes the text."** `compareTypeRefs = "refs"` and `compareTypeClone = "clone"` (`internal/constants.go:108-109` at the head), so the text is the same. The harness confirms it.
9. **"`EqualFold` versus `ToLower ==` changes the BitBucket compare method."** It changes the startup log line only, and only for non-ASCII fold-equivalents (nuance A). It does not change what the backup does. It also makes the BitBucket line consistent with the other four providers, which already used `EqualFold`.
10. **"`backupStatusTitle` changes notification titles, or drops the invisible U+FE0F."** The strings are byte-identical, the three switch arms are identical, and the ntfy titles are identical for all nine pairs.
11. **"`checkJustTokenProvider` / `checkUserAndPasswordProvider` change counting."**
    - They are direct extractions: `if exists { blank ? err : count++ }` became `if !exists { continue }` with the same body.
    - The user-and-password helper returns `1` exactly when the base did `count++`.
    - The harness captured identical `checkProvider` results for all five non-Bitbucket providers.
12. **"Log output changed because the `file:line` prefix changed."** The logger uses `log.Lshortfile` (`backup.go:660`), so the line numbers in log prefixes move, and helper call sites now share one line each. Any edit to the file does this. The promise concerns message content, not caller line numbers.
13. **"The merged Dockerfile `RUN`, the sorted apk list or the quoted URL change the image."**
    - The same commands run in the same order.
    - apk does not depend on argument order.
    - `${TAG}` is an `ARG` exposed to the `RUN` shell, and `/bin/sh -c` expands it inside double quotes exactly as it did unquoted. For any tag without whitespace or glob characters the result is the same, and quoting is strictly safer.
    - The layer count and digests change, which is not a behaviour change. (Static; not built.)
14. **"`rm -f \"/var/cache/apk/*\"` is a no-op, because the glob is quoted."** True, but it was already there at the base; #195 did not introduce it.
15. **"The Docker image uses a frozen `alpine:3.22.0` with CVEs" (#206), "`curl -L` should be `-fL`" (#212), "amd64 is hard-coded" (#213).** All three predate #195, which touched none of them, and all were addressed later in separate, unrelated PRs.
16. **"Deleting `TestPublicGitLabRepositoryBackup2` reduces coverage."** It was a byte-identical duplicate.
17. **"Calling `resetBackups()` twice masks cleanup problems"** (Copilot on `backup_test.go:629`). It is test-only, it was already present at the base, and `resetBackups` → `removeContents` is idempotent.
18. **"The `TestGiteaOrgsRepositoryBackup` helpers weaken assertions."** Every `require` call is kept, and `t.Helper()` is added.
19. **"The BitBucket startup block is gated only on `BITBUCKET_EMAIL`, so OAuth-only users see no BitBucket startup lines."** Also "`strings.ToLower(orgs) != \"\"` is a pointless `ToLower`." Both are pre-existing quirks carried over verbatim; neither was introduced.
20. **"An empty secret in `maskSecrets` interleaves the mask" (#232, reachable via Bitbucket's unused auth slot).** This is a githosts-utils library bug, fixed by a `go.mod` bump. `internal/bitbucket.go` is untouched by #195.
21. **"The new helpers lack unit tests."** This is test-coverage hygiene with no demonstrated consequence, so it is non-material.

## Preexisting hints

These are the review-record items dated up to the merge instant; every arm's packet contains them.
- `sonarqubecloud[bot]` conversation comment, 2026-07-28T21:07:02Z: "Quality Gate passed".
- `copilot-pull-request-reviewer[bot]` COMMENTED review, 2026-07-28T21:09:20Z: "…address SonarQube findings (complexity, duplicate literals, duplicate tests) while keeping runtime behavior consistent…". It came with two inline comments:
  - `internal/backup_test.go:629`: "`resetBackups()` is called inside each switch case and again unconditionally after the switch, so each loop iteration resets backups twice. This is redundant and can mask ordering/cleanup issues in the test." This is non-material (item 17), and the behaviour predates #195.
  - `internal/backup.go:207`: "Log message contains a typo: \"Organistations\". This makes logs harder to search/grep and is inconsistent with the helper's comment spelling." It is tempting but wrong as a defect claim (item 4): the string is preserved verbatim, and fixing it would break the promise of unchanged logs.

There is no human review. Nobody on the record raised the hoisting, short-circuit, `EqualFold`, De Morgan or Dockerfile surfaces. There is no defect to hint at.

## Leakage

A truncated mirror must exclude:
- **Merge commit** `06922a224f36436511eb098e9c698b6966b58b78`.
- **Later commits on the changed paths:**
  - `a84ace57c4e2fec9d26f65608f03ff4a9dd93bb8` (#196; body: "…repeated three times in the startup-config logging introduced by #195")
  - `31b464f` (#206)
  - `f3cb641` (#212)
  - `2a30df5` (#213)
  - `b356029` (#218)
  - `7476b2b` (#233)
- **All of `main` after the base,** up to the current tip `c39e6c0`: 36 commits after the merge. The squash itself lands after the head.
- **Branch heads:** none after the reviewed head; `136a4850` was the PR's only commit.
- **Issues and PRs whose content gives the answer away:**
  - #196: follow-up that names #195 and shows the code survived.
  - #231: cites `backupStatusTitle`'s three cases as reference behaviour.
  - #233: describes `tokenProviders` from #195 as the provider registration point. Its sensitivity is low; it only shows the structure survived.

No advisory exists.

## Confidence and limits

Confidence: **high** that the change is clean.

**For:**
- The production diff is small enough to read in full, and I read every hunk against the base.
- Two independent mechanical harnesses (25,000 + 20,000 configurations) show identical observable output. The only differences are the two disclosed nuances, and neither is material.
- The repository's suite passes identically at both revisions.
- 56 days and about 16 hours passed after the merge (2026-07-30T07:53:54Z to 2026-09-24) with no report.
  - I listed every issue and PR created since 2026-07-28: one issue (#203, an owner "routine diagnostic", closed) and #191–#237.
  - I searched for "Organistations", "backupStatusTitle", "checkProvidersDefined", "compare method", "195", "SonarQube", "bitbucket", "regression", "log output", "ntfy", "telegram", "slack", "Dockerfile", "scheduler", "cron", "interval" and "no providers defined".
  - Nothing reports a regression. The later commits on the changed paths (#196, #206, #212, #213, #218, #233) are unrelated follow-ups or features; none is a fix or revert of #195.

**Limits:**
- The window is only about eight weeks.
- The repository's own tests exercise little of the moved code, because the live-credential tests skip. My harnesses fill the gap for `displayStartupConfig`, `checkProvidersDefined`, `checkProvider`, the Bitbucket gate and the ntfy title.
- Not exercised dynamically: `collectProviderBackupResults` end to end (the provider functions hit the network) and the scheduler paths. Those rest on static comparison: identical calls, same order, same options.
- The Dockerfile was not built (no Docker daemon), so it rests on static review.
- Telegram and Slack titles are covered by the shared helper plus the byte comparison, not by a live send.

**Corrections to the vetting proposal:**
- It cites `constants.go:122–123` for the compare constants. That numbering is from current `main`; at the pinned head the lines are 108–109.
- It says only #195, #196 and #231 appear in searches. My broader searches also surfaced #232 (an unrelated library bug) and #233 (which references the #195 `tokenProviders` table, so it is added to the leak set).
- Its harness hash (`9f477107…`) and counts (1,922 and 11,124) come from its own harness, which I did not run. My independent harness reached the same conclusion with different figures.
- Everything else in the proposal checked out against primary sources.
