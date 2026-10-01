# Hunt q — refactor claiming no behaviour change, large mechanical diff, clean

## Inventory (in order examined)

| # | Repo | PR | Merged | +/- lines (files) | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 | E10 | Result |
|---|------|----|--------|-------------------|----|----|----|----|----|----|----|----|----|-----|--------|
| 1 | IBM/sarama | #3686 | 2026-07-26 | +497/-491 (2) | pass | pass (Jul, 8.5 wk window) | pass (988 lines, 2 files) | not run | pass (no reviews) | likely (Go, offline unit tests) | n/a | n/a | not run | pass (MIT) | **drop**: verbatim file move (sorted removed vs added lines differ only by imports/package header and one dropped separator comment); no hunk that looks behaviour-changing, so no tempting-but-false surface for slot q |
| 2 | jonhadfield/soba | #195 | 2026-07-30T07:53:54Z | +312/-305 (4) | pass | pass (July; window 07-30 → 09-24 = 56 days + ~16 h, just over 8 weeks) | pass (617 lines, 4 files; merge-base = PR base c77f548c) | pass (exit 0, cutoff = merge instant, 0 omissions) | pass | pass (Go 1.26.5; `go test ./...` exit 0 at both revs, ~5 s each; equivalence harness 30,000 env cases produced identical output at both revs) | pass | n/a (clean) | pass (6 later commits on the paths, none a fix or revert; no issue or PR reports a problem) | pass (MIT, 173★, active maintainer) | **PASS: recommended** |
| 3 | jaegertracing/jaeger | #9097 | 2026-07-24T02:56:51Z | +512/-387 (17) | pass | pass (62-day window) | pass (899 lines, 17 files; merge-base = PR base f6fcb05e); partly mechanical (rename, mock regeneration, param plumbing) plus a hand restructure of `WriteSpans` | pass (exit 0, cutoff = merge instant, 0 omissions) | pass (18 reviews, 22 inline comments, GitHub-native) | pass (32 s module download; focused `go test` on 5 ES package trees exit 0 at head (23 s) and base (4 s)) | pass | n/a | pass with caveat: 16 later commits on the paths, none attributable. #9416, #9440, #9363 and #9113 fix pre-existing or unwired behaviour. Caveat: the new `SyncBulkWriter.WriteBatch` doc comment calls a 409 "benign" before #9113 made the unwired sync writer do so. Comment only. | pass (Apache-2.0) | **PASS: alternate** (lower confidence: the PR was written by the maintainer's AI bot, and the doc-comment caveat) |
| 4 | vshulcz/deja-vu | #224 | 2026-07-20 | +281/-228 (3) | pass | pass | pass by GitHub counts (509, 3) | not run | fail: no reviews at all | not checked | not checked | n/a | not checked | doubtful: repo created 2026-07-14, one author | **drop**: glanced only; no review trail and a days-old single-author repo |

Also glanced from search results and dropped without cloning, on the GitHub API's size numbers or on title and body: jawkio/jawk#506 (Java, and no JDK on this machine), sanity-io/cli#1570 (75 files > 40), oxc-project/oxc#25039 and wxMaxima#2139 (> 1,600 lines), isdaniel/pg-walstream#102 (a new feature, not a refactor), DouglasdeMoura/chroncal#558/#559 (add validation, so a behaviour change), Tochemey/goakt#1282 (a feature plus docs), FelixKrueger/Bismark#1082 (2,472 lines), and the many small or personal repositories in the "no behaviour change" searches (under 300 lines or without real maintainers).

Search log (window `merged:2026-07-01..2026-07-30`, the only merges with at least 8 weeks of cleanliness window by today): REST `gh search prs` for "no behavior change" refactor, "no functional change", "no behaviour change", "pure refactor", "mechanical refactor", "no functional changes intended", NFC; GraphQL search (filtered to 280–1,050 lines, ≤ 40 files, ≥ 100–150★) for `refactor "no behavior change"` by language (go, python, typescript), `refactor "no functional change"` (go, python), `refactor in:title` (go, python, 6 pages), and the "behaviour/behavior unchanged" phrases. Note: during the hunt the shared skills worktree switched to branch `t3code/bench-run-cell`, and `prompts/used-pull-requests.txt` disappeared from disk. E1 was therefore checked against the file as committed at 844b9d3 (162 lines, the same count seen at the start), extracted to `scratch/used.txt`. None of the examined repositories appears in it.

## Recommendation

**Primary: jonhadfield/soba#195** (inventory row 2). **Alternate: jaegertracing/jaeger#9097** (inventory row 3). Both pass E1–E10. Both merged in the preferred window, so no fallback to 2025-10-01 or later was needed.

---

### Primary: jonhadfield/soba#195

- **Title:** "refactor: resolve SonarQube findings". **Author:** jonhadfield (the repository owner). **Merged:** 2026-07-30T07:53:54Z, squash merge into `main`. **Licence:** MIT (173★, active; 36 commits on main since the merge).
- **Head** `136a4850df9aec8cf8813b27ba1533d4a17bc642` (a single commit, the only one ever on the branch). **PR-recorded base** `c77f548cbd340d2e744da7c6d92a54372b4b900b`. **Computed `git merge-base`** on a full clone: `c77f548cbd340d2e744da7c6d92a54372b4b900b`, so the two **agree**. **Merge commit** `06922a224f36436511eb098e9c698b6966b58b78`; `git diff --stat <head> <merge>` is empty, so its tree is identical to the head.
- **Changed-file manifest** (`git diff --numstat c77f548c 136a4850`; 617 lines across 4 files):

  | file | + | − |
  |---|---|---|
  | docker/Dockerfile | 3 | 4 |
  | internal/backup.go | 246 | 201 |
  | internal/backup_test.go | 45 | 72 |
  | internal/notify.go | 18 | 28 |

- **Originating issue:** none. The change is driven by 13 SonarQube findings (go:S3776 cognitive complexity, go:S1192 duplicated literals, go:S4144 identical test, and Docker rules S7031, S7018 and S6570).
- **No-behaviour-change claim:** the body says "decomposed into focused helpers. Behaviour and log output are unchanged." The squash commit says "behaviour and log output unchanged".
- **Prior review record up to the merge instant:**
  - `sonarqubecloud` conversation comment, 2026-07-28T21:07Z: Quality Gate passed.
  - `copilot-pull-request-reviewer` COMMENTED review, 2026-07-28T21:09Z. It summarises the change "while keeping runtime behavior consistent" and left two inline comments:
    - `internal/backup_test.go:629`: "`resetBackups()` is called inside each switch case and again unconditionally after the switch, so each loop iteration resets backups twice."
    - `internal/backup.go:207`: "Log message contains a typo: \"Organistations\"."
  - No human review. The typo comment is the tempting objection already on the record. It is wrong as a defect claim, because the typo is carried over verbatim from the old log strings, and "fixing" it would change the log output the PR promised to keep. Nobody raised the hoisting, short-circuit, `EqualFold` or De Morgan surfaces.

- **Cleanliness evidence:**
  - *Window:* 2026-07-30T07:53:54Z to 2026-09-24 (56 days plus about 16 hours; just over eight weeks).
  - *Later commits on the four paths* (`git log 06922a22..origin/main -- <paths>`), none a fix or revert of #195:
    - a84ace5 (#196, 07-30): follow-up Sonar S1192, turning the "Azure DevOps" label into a constant. Same strings.
    - 31b464f (#206): switches to the `alpine:3.22` tag and adds `apk upgrade`.
    - f3cb641 (#212): `curl -fL`.
    - 2a30df5 (#213): arm64 `TARGETARCH`.
    - b356029 (#218): the live GitLab test becomes opt-in.
    - 7476b2b (#233): adds the Codeberg provider as one more registry entry and startup-display helper.
  - *Issue and PR searches* (`gh search issues -R jonhadfield/soba --include-prs`): "Organistations", "backupStatusTitle", "checkProvidersDefined", "\"compare method\"", "195", "SonarQube", "bitbucket". I also listed every issue and PR created since 2026-07-28. Only #195 itself, the follow-up #196, and #231 appear. #231 relies on `backupStatusTitle`'s three cases as correct, and the rest are dependency bumps and CI. The only issue in the window is #203, an owner "routine diagnostic" test issue. Nothing reports a regression.
  - *Tests at both revisions:* soba's own suite, `go test ./... -count=1`, gives exit 0 at the head and at the base, with 24 PASS each. The head has 15 SKIP and the base 16, the extra one being the deleted duplicate test, and the skips are live-credential tests. The refactored credentialed tests (TestGiteaOrgsRepositoryBackup, TestPublicGitLabRepositoryBackup) skip without tokens. So the repository's own coverage of the moved code is thin: only TestCheckProvidersFailureWhenNoneDefined exercises it.
  - *Equivalence harness:* to supplement those tests I ran a mechanical comparison, the scratch file `scratch/zz_equiv_test.go`, copied into `internal/` only while it ran and then deleted.
    - It covers 30,000 seeded random environment configurations over 31 provider variables. Values include unset, empty, a space, `refs`/`REFS`/`Refs`/`clone`, `true`/`false`, numbers, and `*_FILE` pointing at a good, an empty, or a missing file.
    - For each configuration it captures the log output of `displayStartupConfig()`, the result and logs of `checkProvidersDefined()`, and `checkProvider(p)` for every non-Bitbucket provider. It also captures the ntfy `Title` header for all nine (succeeded, failed) combinations through an httptest server.
    - After normalising random temp-directory names, the outputs are **byte-identical** at the head and at the base (sha256 `9f477107…02e9dd` for both). The runs include 1,922 lines logging "compare method: refs" and 11,124 cases where `checkProvidersDefined` returned nil.
  - *Static check:* `TestPublicGitLabRepositoryBackup2`'s body is byte-identical to `TestPublicGitLabRepositoryBackup` at the base (checked with a script).

- **Surfaces a correct review must NOT assert as defects:**
  1. `checkProvidersDefined` now computes `bitbucketAPITokenComplete` before the `range enabledProviderAuth` loop, instead of setting it inside the `BitBucketAPIToken` case. Map order is random, so under the old code the OAuth case sometimes counted even when the API token was complete. However, `count` is only compared with `0`, and a complete API token already contributes 1. The set of `GetEnvOrFile` reads is the same (only their order changed, and it was already random). The harness confirms identical results.
  2. `collectProviderBackupResults` keeps the provider order Bitbucket → Gitea → GitHub → GitLab → Azure DevOps → Sourcehut. The table-driven loop replaces five `if` blocks with the same env-var-to-function pairs.
  3. The `bitbucketAPITokenDefined() || bitbucketOAuthDefined()` short-circuit skips reading the OAuth variables when the API token is complete. The same backups run, because `Bitbucket()` (bitbucket.go:15–21) re-reads all five variables itself.
  4. The early returns in `display*StartupConfig` (`!exists || tok == ""`) are De Morgan inversions of the old guards.
  5. `if ghOrgsExists { if !githubTokenExists {…} }` becoming `if ghOrgsExists && !githubTokenExists` is equivalent.
  6. `runScheduledJob` assigns the package-level `job` (`job, err = s.NewJob(...)` with a local `var err error`), so the global is not shadowed. `WithStartAt(WithStartImmediately())` is still passed only for interval mode. The error strings are unchanged.
  7. `logger.Print("X compare method: refs")` becoming `logger.Printf("%s compare method: %s", label, compareTypeRefs)` produces the same text, because `compareTypeRefs = "refs"` and `compareTypeClone = "clone"` (constants.go:122–123).
  8. `backupStatusTitle` keeps the three `switch` arms and the exact emoji strings, including the leading U+FE0F. The ntfy titles are identical in the harness.
  9. The Dockerfile merges two `RUN` layers, sorts the apk package list, and quotes the URL. These are equivalent. `rm -f "/var/cache/apk/*"` (a quoted glob, so a no-op) is pre-existing, not introduced.
  10. The removed test is an exact duplicate.
- **Honest disclosure: two true but immaterial nuances.** Neither is a defect, and a review must not call either a regression.
  - (a) The BitBucket startup log line changed from `strings.ToLower(c) == "refs"` to `strings.EqualFold`. It now differs only for Unicode fold-equivalents such as `BITBUCKET_COMPARE=refſ` (U+017F): the head logs "refs" and the base logged "clone". I verified this at both revisions. The new text matches what the backup actually does, because githosts-utils v2.1.2 `canonicalDiffRemoteMethod` uses `strings.EqualFold`.
  - (b) Because of the short-circuit in item 3, when the API token is complete and an OAuth `*_FILE` points at a missing file, a backup run logs "file … does not exist" once (from `Bitbucket()`) instead of twice.

- **Tempting false positives** (each looks behaviour-changing and is not):
  1. "Hoisting `bitbucketAPITokenDefined()` changes provider counting." It does not: `count` is only tested for zero, and the old behaviour was map-order-dependent anyway.
  2. "The short-circuit `||` drops the OAuth credential check, so OAuth-only users lose Bitbucket backups." It does not: `||` only skips the OAuth check when the API token is already complete, and the OAuth branch is still evaluated otherwise.
  3. "The typo 'Organistations' / 'Gitlab backup LFS' should be fixed." Both are preserved verbatim, and fixing them would break the promise of unchanged log output.
  4. "Dropping the `nolint: nestif` and flattening the conditions inverts the provider-token checks." They are De Morgan-equivalent.
  5. "`runScheduledJob` shadows `job` / loses the scheduler error." It assigns the global, and the `errors.Wrap(err, "failed to create job")` path is unchanged.
  6. "`EqualFold` versus `ToLower ==` changes the compare method." That affects the startup log only, for exotic input, and now matches the library's own canonicalisation.
  7. "Calling `resetBackups()` twice masks cleanup problems" (Copilot). This is test-only and idempotent (`removeContents`).
- **Leak set:**
  - Merge commit `06922a224f36436511eb098e9c698b6966b58b78`.
  - Later commits on the changed paths: `a84ace57c4e2` (#196, whose body says "introduced by #195"), `31b464f`, `f3cb641`, `2a30df5`, `b356029`, `7476b2b`.
  - The whole of `main` after the base, currently up to `c39e6c0`, since the squash lands after the head.
  - There are no PR branch heads after the reviewed head: 136a4850 was the only commit.
  - Issue and PR numbers to withhold: **#196** (follow-up that names #195) and **#231** (describes `backupStatusTitle`'s three cases as the reference behaviour).
- **Provisioning and test evidence** (Go 1.26.5 linux/amd64; `GOPATH` and `GOCACHE` under scratch):

  | Step | Result |
  |---|---|
  | `git clone https://github.com/jonhadfield/soba.git` | Done, then `git fetch origin pull/195/head` |
  | `go mod download` | exit 0, 1.2 s |
  | `go vet ./internal/` | exit 0, 5.9 s |
  | Head `136a4850`: `go test ./... -count=1` | exit 0, 5 s (24 PASS, 15 SKIP, 0 FAIL) |
  | Head: equivalence harness `go test ./internal/ -run TestZZEquivalence` | exit 0, 2 s |
  | Head: fold probe `TestZZFold` | exit 0 |
  | Base `c77f548c`: `go test ./... -count=1` | exit 0, 6 s (24 PASS, 16 SKIP, 0 FAIL) |
  | Base: equivalence harness | exit 0, 2 s, normalised output identical to the head's |
  | Base: fold probe | exit 0 |

  The tracked tree stayed clean: `git status --short` was empty after each run, and the harness file was removed each time. No credentials or services were used; the live tests skip by default.
- **E4:** `build_packet.py … --pr 195 --head 136a4850… --merge-base c77f548c… --base-sha c77f548c… --target q` gave **exit 0**. Cutoff was the default, 2026-07-30T07:53:54Z (the merge instant). Omissions: `{'reviews': 0, 'thread_comments': 0, 'conversation': 0, 'issue_comments': 0}`. The packet has 4 files, 1 commit, 1 review, 2 thread comments and 1 conversation comment.
- **Confidence: high.**
  - For: the production refactor is small and fully readable; a 30,000-case differential harness shows identical observable output; eight weeks passed with no report; a single human maintainer wrote it; and it has a rich tempting surface (map-order hoisting, short-circuit, De Morgan, `EqualFold`, preserved typos).
  - Against: the window is barely eight weeks (56 days plus 16 hours); the repo's own tests cover little of the moved code (the harness fills the gap); and the two immaterial nuances above must be disclosed to graders.

---

### Alternate: jaegertracing/jaeger#9097

- **Title:** "refactor(es): Unify bulk writes behind a single batch-write API". **Author:** `ysh-bot` ("yurishkuro's AI bot": the maintainer's bot account; the body carries a Claude Code footer). **Merged:** 2026-07-24T02:56:51Z into `main`. **Licence:** Apache-2.0.
- **Head** `86198848aec26ac5833b1db675d587c61c9fe3e8`. **PR-recorded base** `f6fcb05e5f3256da49bba8ae2cff78685e18b787`. **Computed merge-base:** `f6fcb05e5f3256da49bba8ae2cff78685e18b787`, so they **agree**. **Merge commit** `e25782b69e8b071828f2f79f62383eca80e8c3cd`; its tree is identical to the head.
- **Manifest** (899 lines across 17 files):

  | file | + | − |
  |---|---|---|
  | esclient/bulk.go | 15 | 1 |
  | esclient/bulk_test.go | 16 | 0 |
  | esclient/interfaces.go | 10 | 5 |
  | esclient/mocks/mocks.go | 43 | 26 |
  | esclient/sync_bulk.go | 9 | 11 |
  | esclient/sync_bulk_test.go | 14 | 14 |
  | integration/elasticsearch_test.go | 2 | 2 |
  | v1/elasticsearch/factory.go | 3 | 3 |
  | v1 samplingstore/storage.go | 15 | 11 |
  | v1 samplingstore/storage_test.go | 11 | 11 |
  | v2 depstore/storage.go | 8 | 11 |
  | v2 depstore/storage_test.go | 6 | 6 |
  | tracestore/core/reader.go | 1 | 1 |
  | tracestore/core/service_operation.go | 58 | 25 |
  | tracestore/core/service_operation_test.go | 28 | 33 |
  | tracestore/core/writer.go | 57 | 70 |
  | tracestore/core/writer_test.go | 216 | 157 |

  All paths are under `internal/storage/`.
- **Originating reference:** RFC 0007 tracking issue #8476 ("groundwork for milestone M4"). The body says: "**No behavior change:** still async, `WriteTraces` still returns `nil`, wire format identical — the request snapshots are unchanged."
- **Prior review record:** 18 reviews: Copilot twice, and yurishkuro 16 COMMENTED plus 1 APPROVED at 02:46Z. There are 22 inline comments.
  - Copilot caught an in-batch dedup regression in an earlier revision. It was fixed before the reviewed head.
  - yurishkuro asked "how is it a valid situation for service index be blank?". The reply: "no production rotation's WriteTarget returns \"\" … The guard was dead defensive code … Removed". So the tempting objection was raised and answered on the record.
  - The remaining comments are naming and ordering nits, all applied.
- **Cleanliness evidence:**
  - *Commits:* `git log e25782b6..origin/main` over all 17 paths shows 16 commits (07-24 to 09-22). I read the bodies of the ones touching the same behaviour:
    - #9416 (549f2459, clear the service cache in `Purge`) and #9440 (74c1123d, `hashCode` collisions) fix defects that predate #9097. `hashCode` is byte-identical at the base, and the TTL=1 s workaround dates from 2025 (093da18d).
    - #9363 (8b8e07f2) fixes the data-stream `@timestamp` format introduced by #8833.
    - #9113 (68f481b1) fixes 409 handling in `SyncBulkWriter`. Its own words: "latent rather than a regression in a shipped path".
    - The rest are features and moves.
  - *Tests:* the request snapshot files are untouched by the PR, and the snapshot tests pass at both revisions. That is evidence the wire format is identical.
- **Must NOT be asserted as defects:**
  1. The dropped `serviceIndexName != ""` guard: every `Rotation.WriteTarget` is non-empty (`indices/build.go` defaults every alias and prefix).
  2. The deferred `commitToCache`: the only wired writer is `*esclient.BulkIndexer` (`factory.go:56`), whose `WriteBatch` always returns nil. The per-batch key set reproduces the old per-span dedup.
  3. The dependency and sampling stores now "propagate" the `WriteBatch` error: it is always nil in async mode.
  4. The service item is built before tag elevation and timestamping: it reads only `Process.ServiceName` and `OperationName`. The enqueue order (service, then span) and the item set are unchanged, including when a span fails to encode.
  5. `context.Background()` in the dependency and sampling stores: `BulkIndexer.WriteBatch` ignores the context.
  6. The removed nil-writer log in `ServiceOperationStorage.Write`: `Write` is gone, and readers never called it.
- **Caveats** (true, but immaterial or not behaviour):
  - The per-span Debug log "Wrote span to ES index" and the `index` field on the encode-failure log were dropped.
  - Under concurrent `WriteSpans` calls, the window in which two batches both send the same service doc is wider. That is harmless, because the deterministic `_id` makes it an upsert.
  - The new `SyncBulkWriter.WriteBatch` doc comment says a retried create "is a benign 409" before the code did so (#9113). This is a comment on an unwired path.
- **Tempting false positives:** items 1–5 above, plus "`WriteSpans` now fails the whole batch on a writer error where it used to return nil": that cannot happen with the async writer.
- **Leak set:**
  - Merge `e25782b6`.
  - Pre-head branch commits 2454d3cb5, 97a0b042c, 46ca31d87 and 7c28f7125. These precede the head and appear in the thread text; no commits came after the head.
  - Later commits b5b4f028 (#9109), 8ab54205 (#9093), 68f481b1 (#9113), 549f2459 (#9416), 74c1123d (#9440), 8b8e07f2 (#9363), 78a284c3 (#9409), b8e9435a (#9407), b066452f (#9598), and the rest of main after the base.
  - Issue and PR numbers to withhold: #9112/#9113 (the 409 caveat), #9411/#9416 and #9438/#9440 (service cache and hash), #9093 (sync wiring).
- **Provisioning and tests** (Go 1.26.5):

  | Step | Result |
  |---|---|
  | `git clone` | 4 s |
  | `go mod download` | exit 0, 32 s (1.2 GB module cache) |
  | Head: `go test ./internal/storage/elasticsearch/esclient/... ./internal/storage/v2/elasticsearch/depstore/... ./internal/storage/v2/elasticsearch/tracestore/... ./internal/storage/v1/elasticsearch/samplingstore/... ./internal/storage/v1/elasticsearch/ -count=1` | exit 0, 23 s (9 packages ok) |
  | Base: same command | exit 0, 4 s (9 packages ok) |

  The tree stayed clean. The ES/OS integration tests were not run, because they need a live cluster.
- **E4:** exit 0. Cutoff 2026-07-24T02:56:51Z. Omissions all 0. The packet has 18 reviews, 22 thread comments and 1 conversation comment.
- **Confidence: medium.** The diff is less mechanical than soba's (a hand restructure of `WriteSpans`); the author is an AI bot account, although a maintainer reviewed and approved it; and the doc-comment caveat is true but immaterial. The equivalence rests on the async writer being the only wired writer, together with the unchanged snapshots.

### Closest misses
- IBM/sarama#3686: passes E1–E3 and E10, but it is a verbatim move (I compared the sorted removed and added lines), so there is no tempting-but-false surface for this slot.
