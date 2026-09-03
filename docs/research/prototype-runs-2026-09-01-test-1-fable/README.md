# v2a re-run of `kamui/shortlist#66` under DESIGN.md §C9 — Fable 5.1 run (test 1, 2026-09-02)

**Data only.** This directory holds one run: the second 2026-09-02 v2a run against test 1's pinned
target, under skill commit `87c68a9` (the DESIGN.md §C9 fix, `940aa2c`). It is separated from
[`../prototype-runs-2026-09-01-test-1/`](../prototype-runs-2026-09-01-test-1/) for one reason:

**It executed on `claude-fable-5-1`, not the Sonnet 5 tier the program intended.** The dispatch
inherited the harness's configured default model instead of setting one explicitly, and the drift
was discovered only afterwards, by reading `message.model` out of the harness's own sub-agent
transcripts. Because the run it was meant to be compared against — v2a run 1, pre-C9
([`../prototype-runs-2026-09-01-test-1/v2a-run-pre-c9.md`](../prototype-runs-2026-09-01-test-1/v2a-run-pre-c9.md))
— ran on `claude-sonnet-5`, the pair changed two variables at once and **cannot attribute the
recovered recall to the C9 fix alone**. The Sonnet 5 re-run has since been done and lives beside run 1 as
[`../prototype-runs-2026-09-01-test-1/v2a-run.md`](../prototype-runs-2026-09-01-test-1/v2a-run.md); it confirms the recovered
recall is attributable to the C9 fix. This run remains the only one to find a **third** drift
(`validate-completion.py:2949`) and to raise the AC4 question, neither of which the Sonnet run reproduced — so it is retained
as evidence in its own right, not merely as a superseded artifact.

The data is retained rather than discarded because the run still shows the fix's *mechanism*
operating: the Requirements finder returned the changed-contract list first, row 3 is the
closed-list → open-rule shape §C9 added, and that row's old-fragment sweep is what surfaced both
`shortlist-narrow/SKILL.md:46` (the item run 1 missed entirely) and a third drift no prototype run
had previously reported. It also raised an AC4 question that held the derived status at
`Needs Information`.

## Files

- [`v2a-run.md`](v2a-run.md) — the run record, including both finders' ledgers and the verifier's
  verdicts verbatim
- [`comparison-data.md`](comparison-data.md) — normalized measurements and cross-model sensitivity
- [`evaluation.md`](evaluation.md) — analysis of the Fable result and its evidentiary limits

Run conditions, model verification, the packet reconstruction, the side-by-side table, and the
regression watch covering all three of this round's runs live in the shared addendum at
[`../prototype-runs-2026-09-01-test-1/addendum-2026-09-02.md`](../prototype-runs-2026-09-01-test-1/addendum-2026-09-02.md).

The aggregate analysis covering this directory alongside every other run recorded through 2026-09-03 — the change-by-change scorecards for v2a and v5a, the pole comparison, the regression watch, and the next-experiment recommendation — is [`../prototype-runs-aggregate-tests-1-4-v2a-v5a.md`](../prototype-runs-aggregate-tests-1-4-v2a-v5a.md).
