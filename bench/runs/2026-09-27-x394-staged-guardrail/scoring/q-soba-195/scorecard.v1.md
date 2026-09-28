# Scorecard: q-soba-195, mapping v1

Register v1 (e54d5cbf17ad), rubric v1, scored at 2026-09-28T02:39:52Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 47f1dc450bbc998bd323f88512c892cee9a1f65f528d06a0e4db1cca11b0bb2d; session 6623b9ee-b2e1-497a-963e-41ab7f9567df; read audit clean.

## att-002 (review-code-sonnet-high-enforced-x394-trimmed), blind-c6475a

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "that misspelling is unchanged from the base branch, which already used it in the GitHub, Gitea, and Azure DevOps startup-config blocks — the new `logProviderOrgs` helper only relocates the existing text, so it is pre-existing, not introduced by this refactor." Verified: main:internal/backup.go:187/209/275 print "GitHub/Gitea/Azure DevOps Organistations: %s"; review-head:internal/backup.go:205 prints "%s Organistations: %s" with label. Accurate, and it matches the register's non_defect that the typo is preserved verbatim and is at most a non-material remark. The item asserts no defect and proposes no fix; it is an accurate observation below the finding threshold.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "that double-call structure is identical in the base branch's version of the same test ... and is only extracted into helper functions here, not changed." Verified: base backup_test.go:669/703 (resetBackups at the end of each case) and 706 (after the switch); head backup_test.go:629/632/635 keep the same structure around assertGiteaOrgTwoOnlyBackedUp/assertGiteaAllOrgsBackedUp. This matches the register's non_defect (test-only, pre-existing, idempotent). It is an accurate observation with no defect asserted, so it is non-material.

## New candidates

None.
