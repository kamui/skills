# Scorecard: q-soba-195, mapping v1

Register v1 (e54d5cbf17ad), rubric v1, scored at 2026-09-26T08:54:27Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 9fa445290a5a2b27859377c4a1dad4afb09de98addcf7b912bb5ea69bf485eac; session 6c56bf98-e115-477d-ab47-0caae1cdc8da; read audit clean.

## att-005 (review-code-sonnet-high), blind-9c7b26

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The 'Organistations' log typo ... already exists at the merge-base; the refactor keeps it, still emitted for exactly the GitHub, Gitea and Azure DevOps startup lines." Verified: base backup.go:187 (GitHub), :209 (Gitea), :275 (Azure DevOps); head logProviderOrgs at backup.go:203-207 preserves the text. The register lists the typo as a non-defect preserved verbatim. This is an accurate observation with no defect claimed, so non-material.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "The doubled `resetBackups()` in `TestGiteaOrgsRepositoryBackup` (inside each case and after the switch) is carried over unchanged from the merge-base." Verified: head backup_test.go:629/632/635 and base :669/:703/:706. The register non_defect says it is test-only, pre-existing and idempotent. This is an accurate observation, so non-material.

## att-010 (review-code-sonnet-high), blind-04e7d4

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The 'Organistations' log typo and the duplicated resetBackups() call in TestGiteaOrgsRepositoryBackup already existed at the merge-base and are carried over unchanged, as the 'log output unchanged' promise requires." Accurate observation, no defect asserted. Verified: head internal/backup.go:205 logs "%s Organistations: %s" (base :187/:209/:275); head backup_test.go:629/632/635 vs base :669/:703/:706 show the doubled resetBackups(). Register non_defects rule both are pre-existing and not defects; the cited line 207 is off by two (Copilot's anchor) but the fact is right. Non-material.

## att-015 (review-code-sonnet-high), blind-b4cb84

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The 'Organistations' log typo is carried verbatim into the new logProviderOrgs helper, which keeps the log output unchanged as the PR promises; it existed at the merge-base for GitHub, Gitea and Azure DevOps." Verified at head backup.go:203-207 (logProviderOrgs) and base :187/:209/:275. It matches the register's non-defect ruling that the typo is preserved verbatim. This is an accurate observation, so non-material.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "TestGiteaOrgsRepositoryBackup still calls resetBackups() inside each switch case and again after the switch, exactly as at the merge-base." Verified: head backup_test.go:629/632/635, base :669/:703/:706. The register rules this as pre-existing, test-only and idempotent. This is an accurate observation, so non-material.

## New candidates

None.
