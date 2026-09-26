# Scorecard: m-grpc-go-7390, mapping v1

Register v1 (5a40b59e0c38), rubric v1, scored at 2026-09-26T10:51:28Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 2bf76a8e685cbb81fd4290cb0e2e620e6858f4cbbedea25b4555bff37e74544d; session a6f02354-e3f9-4071-bfce-e60661c0968e; read audit clean.

## att-004 (review-code-sonnet-high), blind-baafe2

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The change adds no deterministic regression test; the only evidence for the race fix is the statistical flake rate of an unrelated xDS test." The absence of a test is true (only clientconn.go changed), and the register's non_defects classify it as coverage hygiene rather than a defect. Calling the xDS test 'unrelated' overstates things: per packet section 4, Test/AuthorityRevive is the test that exposed the race (issue #7365 root cause). The wording is loose, but the item attaches no material consequence, so it stays a non-material hygiene observation.

## att-009 (review-code-sonnet-high), blind-d6b31c

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

(no items)

## att-014 (review-code-sonnet-high), blind-5b8025

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The change adds no regression test for the concurrent-connect race; the PR relies on repeated runs of Test/AuthorityRevive." True: `git diff main...review-head --stat` shows only clientconn.go (+6/-7), and the packet's PR body cites the 100000-run validation of Test/AuthorityRevive. The register's non_defects rule on exactly this point: 'No new unit test was added for the concurrency fix' is a coverage-hygiene observation, and correctness is established by path-by-path inspection. The item states no material consequence, so it is non-material.

## att-017 (review-code-sonnet-high), blind-30d026

Verdict 'Approved'; completion completed; approved on buggy n/a; zero recovery n/a; false clean n/a.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The second commit is titled 'Make callers of resetBackoff() lock the mutex' but it performs the resetTransport to resetTransportAndUnlock lock-ownership change; the message names the wrong function." Accurate: `git show 6214c9dd` in clone/ renames resetTransport to resetTransportAndUnlock and changes the call sites (now clientconn.go:922 and :996); it does not touch resetBackoff (packet section 5 confirms the title). But a mislabelled intermediate commit message is commit hygiene with no effect on the code's behaviour, so it is below the finding threshold. The register lists no defects for this target.

## New candidates

None.
