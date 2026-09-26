# Scorecard: q-soba-195, mapping v1

Register v1 (e54d5cbf17ad), rubric v1, scored at 2026-09-25T20:54:07Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 bc7f987ce0e834592019c36a96c7f2cde129ebfb3e86b5aca86ca7d4a5f01170; session 7f0fc6b3-615b-4344-9655-84c665a683b3; read audit clean.

## att-005 (review-code-sonnet-high), blind-9a463a

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: 'The 'Organistations' log typo Copilot flagged is carried unchanged from the base ... so log output stays identical as the PR states.' An accurate confirmation that matches the register. No defect claimed. Non-material.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: 'The duplicated resetBackups() calls ... also exist at the merge-base and were kept as-is.' Accurate and matches the register's pre-existing ruling. No defect claimed. Non-material.

## att-006 (claude-builtin-sonnet-high), blind-b86cce

Verdict 'findings'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: 'The typo "Organistations" was moved into the shared logProviderOrgs helper.' Preserved verbatim from the base to keep log output unchanged (register). Non-material.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: 'TestGiteaOrgsRepositoryBackup still calls resetBackups() inside each switch case and again after the switch ... dead work.' Pre-existing, test-only, idempotent (register). Non-material.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: 'Now it is deterministic: OAuth is never double-counted when both Bitbucket auth methods are complete. This is a silent behaviour change that contradicts the PR's "behaviour unchanged" claim.' The internal count changes, but count is only compared with 0 (backup.go:712) and never returned, so no observable behaviour changes (register non_defect, head-only harness 0 mismatches). Non-material.

## att-007 (claude-builtin-sonnet-high), blind-8ba852

Verdict 'findings'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: 'The startup log message misspells "Organisations" as "Organistations", and the refactor copies the typo into the shared helper.' The typo is preserved verbatim from the base to keep log output unchanged (register non_defect). Non-material.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: 'calls resetBackups() inside each switch case and again unconditionally after the switch.' The item itself notes it is pre-existing; test-only and idempotent per the register. Non-material.

## att-008 (claude-builtin-opus-high), blind-700e1f

Verdict 'findings'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error False, group none. Quote: 'displayBitBucketStartupConfig only prints config when SOBA_BITBUCKET_EMAIL ... is set, so BitBucket OAuth2 users get no startup config output.' The same gate existed at the base; the register rules the email-only gate a pre-existing quirk carried over verbatim. Only log output is affected. Non-material.
- item-1: `non-material`, fix n/a, priority error False, group none. Quote: 'the new tokenProviders table checks only one variable per provider ... GITEA_TOKEN is set without GITEA_API_URL ... Gitea backup fails at run time.' The base runProviderBackups gated Gitea on GetEnvOrFile(envGiteaToken) alone and Azure DevOps on envAzureDevOpsUserName alone, identical to the new table (diff). The register says collectProviderBackupResults keeps 'the same env-var/function pairs and the same `ok && val != ""` test'. checkJustTokenProvider is a direct extraction of the base loop. The described behaviour exists unchanged at the base, so the PR introduced nothing. Non-material.
- item-2: `non-material`, fix n/a, priority error False, group none. Quote: 'TestGiteaOrgsRepositoryBackup calls resetBackups() inside each switch case and again unconditionally after the switch'. Pre-existing at the base, test-only and idempotent (register non_defect). Non-material.
- item-3: `non-material`, fix n/a, priority error False, group none. Quote: 'The misspelling 'Organistations' is now centralised in the shared logProviderOrgs helper'. The typo is preserved verbatim from the base to keep log output unchanged (register non_defect). Non-material.
- item-4: `non-material`, fix n/a, priority error False, group none. Quote: 'logProviderBackupLFS checks existence with GetEnvOrFile but reads the value with envTrue, which uses os.Getenv only.' True, but the base used the identical pattern for every provider, and the startup logs are byte-identical per the register's differential. Pre-existing and log-only. Non-material.
- item-5: `non-material`, fix n/a, priority error False, group none. Quote: 'The GitLab LFS log line uses the label 'Gitlab''. The base's 'Gitlab backup LFS: true' literal is preserved verbatim (register non_defect on typos). Style only. Non-material.
- item-6: `non-material`, fix n/a, priority error False, group none. Quote: '`rm -f "/var/cache/apk/*"` quotes the glob, so it deletes nothing.' The register rules this true but pre-existing at the base; with --no-cache it has no effect. Non-material.
- item-7: `non-material`, fix n/a, priority error False, group none. Quote: 'logProviderOrgs tests `strings.ToLower(orgs) != ""`, which is the same as `orgs != ""`'. The register lists the pointless ToLower as a pre-existing quirk carried over verbatim. Cleanup only. Non-material.
- item-8: `non-material`, fix n/a, priority error False, group none. Quote: 'scheduleBackups creates a gocron scheduler before choosing the mode, so the one-shot default path creates a scheduler it never starts'. The base Run also called gocron.NewScheduler() before the switch (diff shows only `var s`/`s, err =` collapsing to `s, err :=`). A minor pre-existing inefficiency with no demonstrated consequence. Non-material.

## att-009 (codex-default), blind-fc8256

Verdict 'patch is correct'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

(no items)

## att-042 (claude-builtin-sonnet-high), blind-9f3a3f

Verdict 'findings'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: 'resetBackups() runs inside each switch case and again unconditionally after the switch'. Pre-existing, test-only, idempotent (register). Non-material.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: 'The log message "Organistations" is misspelled, and the new shared logProviderOrgs helper now spreads the typo'. The helper does not spread it: the base already emitted the same typo for all three providers. Preserved verbatim per the register. Non-material.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: 'If both Bitbucket API-token and OAuth credentials are set and OAuth is visited first, the old code counted 2 providers. The new code always counts 1. That is arguably a fix, but it contradicts the PR's "behaviour unchanged" claim'. The count difference is accurate, but count is only compared with 0 (backup.go:712) and never returned, so observable behaviour is identical (register non_defect; 0 mismatches over 20,000 configurations). Non-material.

## att-043 (claude-builtin-opus-high), blind-460555

Verdict 'findings'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error False, group none. Quote: 'displayBitBucketStartupConfig only runs when BITBUCKET_EMAIL is set, so setups that use Bitbucket OAuth2 ... log no Bitbucket startup config at all.' True, but the base had the same gate (base diff: `if bbUser, exists := GetEnvOrFile(envBitBucketEmail); exists && bbUser != ""`). The register lists 'BitBucket startup config is gated only on BITBUCKET_EMAIL' as a pre-existing quirk carried over verbatim. Only the startup log is affected, and the PR promised unchanged output. Pre-existing, so non-material.
- item-1: `non-material`, fix n/a, priority error False, group none. Quote: 'validateStartupConfig reads GIT_BACKUP_DIR with os.LookupEnv, but runProviderBackups reads it with GetEnvOrFile, so the documented *_FILE form of the backup directory is rejected at startup.' The mismatch is real (backup.go:444 os.LookupEnv vs backup.go:41 GetEnvOrFile), but the base Run had the identical os.LookupEnv line; the diff only moves it into the helper and adds the "" return. The PR introduces no behaviour change; this is a pre-existing limitation outside the refactor's scope. Non-material for this PR.
- item-2: `non-material`, fix n/a, priority error False, group none. Quote: 'The new shared logProviderOrgs helper keeps the typo 'Organistations''. True, but the register says the typo is preserved verbatim from the base and fixing it would break the PR's 'log output unchanged' promise. At most a non-material remark.
- item-3: `non-material`, fix n/a, priority error False, group none. Quote: 'both switch cases call resetBackups() and then the loop calls it again after the switch'. The register says this is test-only, present at the base (base backup_test.go:669/703/706), and idempotent. The item itself calls the consequence hypothetical ('if resetBackups ever became non-idempotent'). Hygiene, so non-material.
- item-4: `non-material`, fix n/a, priority error False, group none. Quote: '`rm -f "/var/cache/apk/*"` quotes the glob, so the shell never expands it and the command deletes nothing.' The register rules this true but pre-existing at the base; the PR only merged the RUN layers (diff shows the rm line unchanged). With --no-cache the command has no functional impact. Non-material.
- item-5: `non-material`, fix n/a, priority error False, group none. Quote: 'titleBackupsErrors and titleBackupsFailed start with a stray U+FE0F variation selector ... now built into the shared constants.' The register says the three literals are byte-identical to the base's, including the leading U+FE0F, so the titles clients receive are unchanged by this PR. The consequences about client rendering and filter matching are speculative and pre-existing. Non-material.
- item-6: `non-material`, fix n/a, priority error False, group none. Quote: 'backupStatusTitle returns 'soba backups failed' when succeeded == 0 and failed == 0 ... The new shared helper has no unit test'. The switch arms are identical to the three base copies (diff of notify.go), so 0/0 behaved the same before; the register says the switch arms are identical. Missing unit tests are test-coverage hygiene (register non_defect). Non-material.
- item-7: `non-material`, fix n/a, priority error False, group none. Quote: 'logProviderBackupLFS checks GetEnvOrFile existence and then calls envTrue, which reads only os.Getenv ... an LFS flag set through *_FILE is never reported.' True (envTrue at backup.go:719 uses os.Getenv), but the base had the identical `GetEnvOrFile(...); exists && envTrue(...)` pattern for every provider, and the register's differential shows identical startup logs. Pre-existing, affects only a startup log line, so non-material for this PR.
- item-8: `non-material`, fix n/a, priority error False, group none. Quote: 'The startup logging helpers are called with inconsistent provider labels ('Gitlab' for LFS ...) ... GitHub and Azure DevOps never log backups-to-keep, and Sourcehut has no startup config display at all.' All of these match the base: 'Gitlab backup LFS' is preserved verbatim (register), and the base displayStartupConfig had no Sourcehut block and no GitHub/Azure backups-to-keep line. Changing them would break the 'log output unchanged' promise. Non-material.
- item-9: `non-material`, fix n/a, priority error False, group none. Quote: 'runScheduledJob quietly assigns the package-level `job` global ... If NewJob fails, the scheduler created by scheduleBackups is never shut down.' The register says the assignment to the package-level job and the errors.Wrap are unchanged and not a defect. The base Run also returned errors.Wrap(err, "failed to create job") without s.Shutdown(), so the missing shutdown is pre-existing, and the process exits after Run returns an error anyway. Non-material.

## att-044 (claude-builtin-sonnet-high), blind-8eb8cc

Verdict 'findings'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: 'resetBackups() is called inside the `sobaOrgTwo` and `"*"` switch cases and then again unconditionally after the switch.' Pre-existing, test-only, idempotent (register non_defect). Non-material.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: 'The log text typo "Organistations" is now baked into the shared `logProviderOrgs` helper.' Preserved verbatim from the base to keep the 'log output unchanged' promise (register). Non-material.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: 'If the OAuth case came first in Go's random map order, both Bitbucket credential sets were counted. Now the API-token check runs once before the loop ... it changes the provider count in the 'no providers defined' check.' The internal count difference is real (register: base 2 or 1 by map order, head always 1). But count is only compared with 0 (backup.go:712, `if count == 0`) and never returned, so the error outcome cannot differ; the register's head-only harness found 0 mismatches over 20,000 configurations. The item calls it 'arguably a fix' and asserts no harmful consequence. A true but inconsequential observation, so non-material.

## att-045 (codex-default), blind-d906a7

Verdict 'patch is correct'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

(no items)

## att-046 (review-code-sonnet-high), blind-2acc52

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: 'Provider ordering, log strings (including the pre-existing 'Organistations' spelling) and notification title bytes are preserved exactly by the refactor.' This is an accurate confirmation of equivalence and matches the register's non_defects (provider order, typo kept verbatim, title literals byte-identical). It asserts no defect, so it is a non-material observation.

## New candidates

None.
