# Scorecard: q-soba-195, mapping v1

Register v1 (e54d5cbf17ad), rubric v1, scored at 2026-09-27T07:11:13Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 b8ae20d9d1c8b3d5d90dce83309ccfacf2465265b3a58033e5fe0991d9851661; session c16eb036-1202-45f0-bb0d-68aadab6fe97; read audit clean.

## att-003 (review-code-sonnet-high), blind-5e8872

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The pre-existing \"Organistations\" typo ... is preserved verbatim by the new shared logProviderOrgs helper rather than fixed." Accurate: clone/internal/backup.go:203-205 (logProviderOrgs) logs "%s Organistations: %s", and main's backup.go:187/209/275 had the same wording for GitHub, Gitea and Azure DevOps. The cited 183-186 is slightly off (the helper is at 203), but the fact holds. The register's non_defects list this typo as not a defect: it is preserved verbatim, and fixing it would break the PR's 'log output unchanged' promise. The item proposes no fix and claims no material consequence, so it is a true but inconsequential remark.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "TestGiteaOrgsRepositoryBackup calls resetBackups() once inside each switch case and once more unconditionally after the switch ... this pre-existing double reset is preserved unchanged." Accurate: clone/internal/backup_test.go:625-635 shows resetBackups() in each case and again after the switch. The register's non_defects rule this test-only, pre-existing at the base, and idempotent (resetBackups -> removeContents). The item claims no material consequence, so it is a hygiene observation.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "`rm -f \"/var/cache/apk/*\"` quotes the glob, which (pre-existing, unchanged by this diff) prevents shell expansion." Accurate: clone/docker/Dockerfile:8 has the quoted glob, and main's Dockerfile:9 had it too. The register's non_defects say this is true but pre-existing at the base and not introduced by #195. With --no-cache on apk add, the practical effect is negligible. The item correctly frames it as pre-existing, so it is below the finding threshold for this PR.

## New candidates

None.
