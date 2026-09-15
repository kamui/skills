# Fowler smell baseline in `review-code` — issue #235

Decision record for [#235](https://github.com/kamui/skills/issues/235), part of
[#225](https://github.com/kamui/skills/issues/225). This assessment uses existing evidence; the shipped
skill is unchanged.

## Decision

**Defer implementation pending evidence; retain the current skill.** `review-code` continues without
the two-axis `code-review` skill's Fowler smell baseline (*Refactoring*, ch. 3). Optional discovery
heuristics remain a compatible design to reconsider: their incremental benefit has not been
established by the cited evidence. Existing admission gates continue to govern findings, but do not
establish discovery coverage. No implementation issue is opened, and the workflow identifier stays
`v5b-17`.

## Policy inspected

| Pin | Role |
| --- | --- |
| `f26c32d393bf902120445a4be6718cec02d5ce7d` (`origin/main`, workflow `v5b-17`) | [`references/review-rubric.md`](../../skills/review-code/references/review-rubric.md): admission gates 4 and 7, and the Complete inspection risk-signal list. |
| Installed two-axis `code-review` `SKILL.md` | The baseline under assessment. Its Standards brief asks for "any baseline smell you spot: name it and quote the hunk", always as a judgement call, with documented repository standards overriding it. |

## Reasons

1. **Admission and discovery answer different questions.** Gate 4 admits a
   maintainability candidate only after it demonstrates "the exact contradiction or drift and the
   concrete reader or maintenance consequence". Gate 7 drops "generic preferences". A Duplicated
   Code or Mysterious Name instance with a proven consequence is already admissible as
   `maintainability`, with no label. Those gates determine whether a discovered candidate qualifies;
   they do not establish how reliably the reviewer discovers it. An optional smell heuristic could
   direct a bounded read that finds the consequence while leaving the admission bar intact.
2. **The incremental benefit of a discovery aid is unmeasured.** #235 bounds any
   adoption to a risk-signal aid beside "Use risk signals to direct attention, not to create
   findings". Existing [risk-led discovery](../../skills/review-code/references/review-rubric.md)
   already uses signals to direct bounded reads. Adding twelve smell signals would add instructions
   and could direct additional reads, but the cited evidence does not compare their discovery benefit
   or attention cost against the current skill. This shape preserves the admission bar; it does not
   establish the value of adding the aid. Retain the current skill until evidence justifies that
   change, which would also require a workflow identifier bump.
3. **Earlier research permits gated candidate generation.** The
   [candidate survey](agentic-code-review-candidates.md) criticized asking an agent to report smell
   instances as a precision hazard. Its recommendation explicitly says the list can remain for
   candidate generation, with the admission criteria as the gate every candidate must pass.
   This supports keeping smell labels out of findings by themselves and leaves optional discovery
   heuristics open for evaluation; it does not establish that such heuristics are unnecessary.
4. **The cited evidence does not meet the reconsideration trigger.** No cited routine run has missed a
   maintainability defect that the baseline names:
   - The [#216 diagnosis](routine-review-diagnosis-2026-09-13/README.md) found one material missed
     concept (C05, a ruling-table glob) plus low-impact reporting and documentary omissions. None is
     a smell-named defect.
   - In the [target-j scorecard](one-shot-qualification-2026-09-07/scoring/j-scorecard.md), all four
     blind reviews, under the older `v5b-10`/`v5b-1` snapshots, raised a
     smell-shaped dead-branch finding that the register had graded true but non-material. None of
     them recovered the material defect. This is one target on superseded policy, so it supports no
     claim about `v5b-17`. It only shows that such facts already surface without a baseline; it does
     not measure whether an optional aid would improve discovery.

   Neither source establishes that the current skill discovers every worthwhile maintainability
   defect or that optional heuristics have no benefit. They support deferral on present evidence.

## What would be evaluated if reopened

An optional aid would guide discovery while preserving the ordinary admission gates. A future
implementation issue would have to specify:

- the exact text, placed as a risk-signal aid in `review-rubric.md`'s Complete inspection section;
- no new finding channel, label, or "possible X" comment form;
- the workflow identifier bump past `v5b-17`;
- two replays: one where a smell directs a bounded read that leads to a finding admitted under the
  ordinary gates, including a demonstrated maintenance consequence, and one where the smell is present
  but correctly produces no finding.

## Reconsideration trigger

Keep #235's entry condition: reconsider when a routine `review-code` run misses a maintainability
defect that the baseline names, and the run and the defect are both cited. Such a case would justify
evaluating whether a bounded smell heuristic helps discover the defect; it would not by itself prove
that the heuristic improves review quality. This record schedules no collection or paid run.
#235 can close with the current skill retained and implementation deferred pending evidence.
