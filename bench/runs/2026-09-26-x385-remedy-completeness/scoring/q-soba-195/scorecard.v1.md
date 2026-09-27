# Scorecard: q-soba-195, mapping v1

Register v1 (e54d5cbf17ad), rubric v1, scored at 2026-09-27T07:12:05Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 1cd323683a32d460140bb7d78b253aaa7058c55ec932020e11445a70a36df76f; session b54e16e1-4b71-4d05-8154-20924f91424b; read audit clean.

## att-005 (review-code-sonnet-high), blind-d2da7b

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error False, group none. Quote: "Drop the duplicate resetBackups() call ... resetBackups() is idempotent today ... the second call is a harmless no-op rather than a masked ordering bug." Accurate: clone/internal/backup_test.go:627-636 calls resetBackups() in each switch case and again after the switch. The item itself disclaims any consequence, and the register's non_defects rules this test-only redundancy (already present at base) not a defect. Hygiene cleanup, below the finding threshold.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "the refactor computes bitbucketAPITokenDefined() once before the loop, which removes that latent order-dependence rather than introducing one." Accurate observation: base set bitbucketAPITokenComplete inside the map loop (main backup.go:630/639/649); head hoists it at clone/internal/backup.go:685. Matches the register's non_defect ruling that hoisting is not a defect (count only compared with 0). The cited line numbers (643-646) are slightly off, but the claim asserts no defect; it is an observation.
- item-2: `non-material`, fix n/a, priority error n/a, group none. Quote: "The 'Organistations' log-message typo ... predates this change ... the diff only relocates the string into shared helpers without altering its text." Verified: git show main:internal/backup.go lines 187, 209, 275 contain 'Organistations'; head has it once in the shared helper at clone/internal/backup.go:205. Register non_defects: typo preserved verbatim, not a defect. True observation asserting no defect.

## New candidates

None.
