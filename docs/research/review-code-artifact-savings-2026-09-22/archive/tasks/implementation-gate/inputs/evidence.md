# Verification results

Shared context: head 2ba40465ef91f15b2963a4b12e80f46ee0e9efae, committed tree with no uncommitted or untracked changes, Python 3.14.7 and Git 2.34.1 on Linux (WSL2); standard library only, no generated inputs.

- `python3 -m unittest discover -s tests -v` from the repository root: exit 0, 17 tests run, none skipped. Output: @TASK_ROOT@/inputs/unittest-head.txt.

Acceptance exercises at the same head and context, for criterion 5, which no test exercises through the command line:

- `python3 -m ledger.cli statement /dev/null 1001 --since 2026-13-01`: exit 2. Stdout and stderr: @TASK_ROOT@/inputs/criterion-5.txt.
- `python3 -m ledger.cli statement /dev/null 1001 --since 2026-09-03 --until 2026-09-01`: exit 2. Stdout and stderr: the same file.

Missing required evidence: none recorded.
