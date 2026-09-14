# Empty-ledger verification exemption — issue #222

Decision record for [#222](https://github.com/kamui/skills/issues/222), part of
[#217](https://github.com/kamui/skills/issues/217). Its inputs are the bounded
[#216 diagnosis](routine-review-diagnosis-2026-09-13/README.md) and the records
[#218](https://github.com/kamui/skills/issues/218) had already produced. No review ran, no sample was
enlarged, and the shipped skill is unchanged.

## Decision

**Insufficient evidence; no change.** Keep `review-code` step 3's sentence "An empty ledger still
requires the batch; its conclusion covers only that empty ledger." The inspected evidence has no
explicit zero-row candidate disposition ledger and no timing or usage for any empty batch. The saving
an exemption would bring is therefore unobserved. The only facts available are mechanical ones, so no
exemption is proposed and no implementation issue is opened.

## Policy versions inspected

| Pin | Role |
| --- | --- |
| `7a349667b1606d4557ac0b1c4f4ef3d271c48117` (`origin/main`, workflow `v5b-17`) | Shipped rule under assessment: [`SKILL.md` step 3](../../skills/review-code/SKILL.md), no-material-survivor mode. It applies the same way to pull-request, range, and working-tree targets and to both caller modes. |
| `9b9e18d98e2b22eb538410deda149a949159754f` (2026-09-11, `v5b-13`) | Added the empty-ledger sentence when [#202](clean-verdict-any-surface-2026-09-11.md) removed the surface condition. `v5b-12` and earlier ran no-material-survivor mode only on concurrency, integrity, and security surfaces and had no explicit empty-ledger rule. |
| `v5b-17` at [#218](../../skills/review-code/DESIGN.md#ordinary-run-timing-records-issue-218) | Added `run-events.jsonl` recording. It is the first source that can tell an explicit zero-row complete-ledger batch from an unknown one. It was installed on this host at 2026-09-14 04:00 −0400. |

## Evidence table

A candidate disposition ledger counts as **explicit zero** only when a retained record shows the
complete ledger with zero rows. A run with zero findings or no published ledger is **unknown**, never
zero. A local target's empty *requirement* ledger is a different ledger and is not counted.

| Source | Runs | Target kind / caller mode | Workflow | Candidate ledger | Empty-batch timing or usage |
| --- | --- | --- | --- | --- | --- |
| #216 R01–R20 ([collection](routine-review-diagnosis-2026-09-13/collection.md)) | 20 | pull-request / published (predates caller modes) | 7 × `v5b-12`, 12 × `v5b-13`, 1 × `v5b-14` | Unknown for all 20. The public summaries do not include private ledgers or verifier returns ([README](routine-review-diagnosis-2026-09-13/README.md#collection-and-policy-identity)). | Unavailable |
| #218 pre-publish review of `origin/main..d3c8537` (local record) | 1 | range / one-shot | `v5b-17` | Nonempty: two surviving `bug`-kind `consider` findings, which are material, so no-material-survivor mode did not apply. No batch was triggered or dispatched. | None; no batch |
| #218 addendum at `0297f79` | Not a run | Addendum to the record above, not a new record | `v5b-17` | Excluded: it re-verifies two fixed ids and raises no new candidates. It has no ledger of its own. | None; no batch |
| [PR #242 review 5194968143](https://github.com/kamui/skills/pull/242#pullrequestreview-5194968143) at `0297f79` | 1 | pull-request / one-shot | `v5b-17` | Nonempty: three confirmed findings and two related acquittals | Unavailable |
| [PR #242 review 5195193241](https://github.com/kamui/skills/pull/242#pullrequestreview-5195193241) at `07affb5` | 1 | pull-request / one-shot | `v5b-17` | Nonempty: a complete-ledger clean verdict over at least three fixed dispositions | Unavailable |
| `run-events.jsonl` on this host (filesystem search, 2026-09-14, before this record's own pre-publish review) | 0 ordinary runs | — | — | The three files found are #218 test and benchmark artifacts: `bench.py` events with synthetic heads, and two empty test fixtures. | None |

| Denominator | pull-request | range | worktree | Total |
| --- | --- | --- | --- | --- |
| Runs inspected | 22 | 1 | 0 | 23 |
| Explicit zero-row candidate ledger | 0 | 0 | 0 | **0** |
| Known nonempty ledger | 2 | 1 | 0 | 3 |
| Unknown or missing ledger | 20 | 0 | 0 | 20 |

By mode, the three `v5b-17` runs are all one-shot. The 20 #216 runs predate caller modes. No session
run was inspected.

Only 3 of the 23 runs use the shipped workflow. None of the 20 historical runs retains a ledger. Later
`v5b-15`–`v5b-17` reviews on other pull requests exist, but they were deliberately not collected,
because #222 forbids enlarging the sample.

## Mechanical facts versus review-quality evidence

The following facts are **mechanical** and hold by construction:

- In a complete ledger, every raised candidate keeps a disposition row. A literally empty ledger
  therefore means the primary raised no candidate at all.
- The worker receives no rows. It cannot search for new findings, and its required conclusion covers
  only the empty ledger. It cannot re-open anything or rule on any row.
- [`DESIGN.md`'s transition replay](../../skills/review-code/DESIGN.md#instruction-transition-replay)
  records that the builder accepts an empty complete-ledger batch and the accountant requires its
  conclusion.

Those facts suggest the batch adds little independent checking. They are not evidence about review
quality. No record shows what such a worker returns, whether its dispatch catches a primary that
under-recorded candidates, or what it costs.

The only clean-verdict worker charges on record are #137's three runs at $0.24–$0.53 and #138's
control run at $0.62. Those came from nonempty ledgers, under experimental rates and pre-`v5b-13` pins
([source](clean-verdict-any-surface-2026-09-11.md#incremental-cost-at-the-recorded-rates)). They are
not a proxy for an empty batch and are not converted to current prices.

## Exemption that would be evaluated

This section is not proposed and not authorized. It records the bar a future proposal would have to
meet.

An exemption would apply only when all of these hold:

- the full changed-file manifest is complete;
- the required changed-test, risk, and requirement checks are recorded;
- the primary review is complete;
- every raised candidate has a retained disposition;
- the entire candidate disposition ledger has zero rows;
- no mandatory verification, follow-up obligation, or unresolved candidate remains.

It would not suppress rows, skip substantive acquittals, turn incomplete coverage or an exhausted
follow-up into approval, or use a small candidate count as a threshold.

In place of the vacuous conclusion, the record would state: "Clean-verdict check not dispatched: the
primary raised no candidates, so the disposition ledger was empty." Coverage and status would stay
exactly as the primary derived them. The record would not use the words "independent", "verified",
or "clean verdict stands".

An implementation would need its own issue: a workflow bump past `v5b-17`, plus tests for:

- empty, nonempty, and missing ledgers;
- incomplete coverage;
- prior reviews;
- mixed batches;
- follow-up exhaustion;
- duplicate-review invalidation across workflow versions.

## Reconsideration trigger

Reconsider only when retained `run-events.jsonl` summaries from ordinary runs at `v5b-17` or later
meet both of these conditions:

- Several runs, across more than one pull request, contain a complete-ledger batch with an explicit
  `0` row count. `run_events.py summarize` reports this separately from unknown counts.
- For those batches, the brief-to-accounting proxy bracket, or worker usage from an authoritative
  transcript, is attributable.

Those captures are opportunistic. This record schedules no collection, monitoring, or paid run.
Until they exist, the current behavior stays and #222 is closed with this disposition.
