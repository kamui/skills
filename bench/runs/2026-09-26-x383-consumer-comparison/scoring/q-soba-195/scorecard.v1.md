# Scorecard: q-soba-195, mapping v1

Register v1 (e54d5cbf17ad), rubric v1, scored at 2026-09-26T10:51:28Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 a8ce6861740ad79a2beb8c55ccebbd61d159dae139a7d242af09ab6ddd756e09; session 90a4c069-50cd-4ff0-892e-1ec85731e67a; read audit clean.

## att-005 (review-code-sonnet-high), blind-9f691d

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quotes: "The Sonar bot comment on the pull request reports 1 new issue while the body says all 13 open findings are fixed; the issue itself is not identified in the packet." This is factually accurate per packet.md section 6 (sonarqubecloud: '1 New issue', Quality Gate passed). The item names no defect in the code, only a discrepancy in the PR description, and the register's clean_basis shows the change is behaviour-preserving. It is an observation below the finding threshold.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quotes: "The 'Organistations' log typo is unchanged from the base and now lives once in the shared helper, matching the 'log output unchanged' promise." Verified: head internal/backup.go:205 has the helper's Printf, and the base has the typo at :187, :209 and :275, exactly as cited. The register's non_defects says the preserved typo is not a defect and at most a non-material remark.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quotes: "The doubled resetBackups() call in TestGiteaOrgsRepositoryBackup exists at the base too, so the refactor carries it over rather than adding it." Verified: head internal/backup_test.go:629/632/635 show resetBackups() in each case and after the switch. The register's non_defects confirms the double call is test-only, already present at the base, and harmless. It is an accurate, inconsequential observation.

## att-010 (review-code-sonnet-high), blind-d84aef

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quotes: "The 'Organistations' typo in the organisation log line is carried unchanged into the new logProviderOrgs helper, so it already existed at the merge-base." Accurate in substance: the typo exists at base (internal/backup.go:187/209/275) and is preserved in the head helper at internal/backup.go:205. The cited line numbers (207 at head, 196 at base) are slightly off. The register rules the preserved typo not a defect, so this is a non-material remark.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quotes: "The double resetBackups() call per loop iteration in TestGiteaOrgsRepositoryBackup already existed at the merge-base and is preserved by the refactor." Verified at head internal/backup_test.go:629-635. The register's non_defects says this is test-only, pre-existing at the base, and idempotent. It is an accurate, inconsequential observation.

## att-015 (review-code-sonnet-high), blind-739645

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quotes: "`checkProvidersDefined` now computes the Bitbucket API-token state before the map loop, so OAuth counting no longer depends on random map iteration order." Accurate: clone/internal/backup.go:685 hoists bitbucketAPITokenComplete before the range loop, and the OAuth arm checks !bitbucketAPITokenComplete. The register's non_defects rules the hoisting is not a defect: count is only compared with 0 and the gate result never differs (0 mismatches over 20,000 configurations). The item asserts no harmful consequence and proposes no fix, so it is a true but inconsequential observation.

## New candidates

None.
