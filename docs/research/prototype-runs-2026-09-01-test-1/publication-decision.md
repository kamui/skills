# Publication decision

**2026-09-01.** Which run's output was published to `kamui/shortlist#66`, and why. This is a
selection record, not the comparative analysis — that is a separate pass. The publication decision
was made after v2-v4; the later v5 controlled run is recorded below without rewriting that history.

## Published: v4

[Review `5076220814`](https://github.com/kamui/shortlist/pull/66#pullrequestreview-5076220814) —
`Approved (advisory)`, two `consider` findings as line comments:

- [`narrowing-protocol.md:68`](https://github.com/kamui/shortlist/pull/66#discussion_r3902611240) — P2, fix at `shortlist-narrow/SKILL.md:46`
- [`research-protocol.md:295`](https://github.com/kamui/shortlist/pull/66#discussion_r3902611259) — P3, fix at `search-bundle-format.md:208`

V2's, v3's, and v5's outputs were **not** published.

## Why v4's output

Judged on the published artifact's value to the PR author, not on the architecture that produced it:

1. **Both findings were independently verified**, and the verifier did real work rather than
   rubber-stamping: it corrected F1's trigger basis, reordered F1's requirement citation to lead
   with the criterion the text straightforwardly violates, and **cut F2's impact as "not
   establishable"** — explicitly instructing that its priority not be raised.
2. **Severity calibration was the most defensible of the first three.** Both items are
   documentation-sync drift with one-line fixes and a limited blast radius. v2 published the same
   two as P1 `must-fix` and derived `Changes Requested`, which would block a merge on doc drift
   whose own reviewer noted the reader has a working link to the correct enumeration.
3. **Content is a superset of v3's and a well-scoped subset of v2's.** v3 published one finding and
   dropped the bundle-contract item entirely; v2 published four, two of which the other runs
   dropped with reasoning that holds up (pre-existing regex; a `CONTEXT.md` sentence present at base).
4. **It handled its own coverage gap correctly** — detected an unrecoverable fetch, marked coverage
   incomplete, derived a provisional `Incomplete` status rather than falling through to approval,
   named exactly what the missing input could change, and asked the orchestrator rather than the
   author. Supplying the PR body recovered the fetch and moved the status to `Approved (advisory)`.

## Publication conditions

- Stale-head re-check ran immediately before the write; head matched `4349ff4`.
- `context` digest computed with the skill's own
  [`scripts/context_fingerprint.py`](https://github.com/kamui/skills/blob/t3code/prototype-code-review-publish-4/skills/code-review-publish-4/scripts/context_fingerprint.py)
  over the PR title/body, issue #45, and base-branch blob SHAs for `AGENTS.md`, `CONTEXT.md`, and
  `docs/agents/domain.md`: `c8deb4157b5a2cbbca1a70d4f800db3702f93fddf8beb5791c1be1d970d3fd30`.
- Self-review (`kamui` authored the PR), so `event: COMMENT` with the semantic status in the body.
- One batched call carrying the body and both line comments; both anchors verified against the diff.
- The summary footer discloses that v2 and v3 also reviewed this PR and that their output was
  withheld, so a later reader of the PR is not misled about how the review was produced.

## Later v5 controlled run

V5 ran after the v4 publication, but received the original pinned `none` prior-review state and did
not read current live review state. Publication remained disabled. It would have produced
`Approved (advisory)` with two `consider` findings — the same two items v4 published, both at P3:

- anchor `narrowing-protocol.md:68`, fix `shortlist-narrow/SKILL.md:46`
- anchor `research-protocol.md:295`, fix `search-bundle-format.md:208`

Its primary reviewer proposed the Narrow entrypoint's fixed refresh list as a P2 `must-fix`. The
mandatory fresh verifier confirmed the underlying claim but downgraded the record to P3 `consider`
and `maintainability`, because `shortlist-narrow/SKILL.md:37` requires following the broader
ledger-driven protocol, which keeps canonical behavior intact. It also replaced the trigger example
with the `policy terms` class, which the stage skill genuinely omits. The primary validated each
correction against the diff and accepted it. That downgrade is what moved the run from
`Changes Requested` to `Approved`.

The existing v4 review was not edited, contradicted, or supplemented. V5 is retained as controlled
evaluation data in `v5-run.md`; publishing it after v4 would instead exercise re-review and prior
thread handling, which was not the test requested here.

## What this decision is not

It is not a verdict on which prototype is best. V2 found two items the others missed, and whether
those are real defects or over-flagging is exactly the question the analysis pass has to settle.
The same is true of v3 dropping the bundle-contract item that v2, v4, and v5 confirmed, and of the
four-way split on how severely to treat the Narrow finding. Publishing v4 records which single
artifact was judged most defensible after the original three-way test, before v5 existed.
