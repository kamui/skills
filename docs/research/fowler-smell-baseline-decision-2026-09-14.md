# Fowler smell baseline in `review-code` — issue #235

Decision record for [#235](https://github.com/kamui/skills/issues/235), part of
[#225](https://github.com/kamui/skills/issues/225). No review ran, and the shipped skill is unchanged.

## Decision

**Retain; no smell baseline.** `review-code` does not carry the two-axis `code-review` skill's Fowler
smell baseline (*Refactoring*, ch. 3), not even as optional heuristics. Its maintainability findings
on evidence are enough. No implementation issue is opened, and the workflow identifier stays
`v5b-17`.

## Policy inspected

| Pin | Role |
| --- | --- |
| `f26c32d393bf902120445a4be6718cec02d5ce7d` (`origin/main`, workflow `v5b-17`) | [`references/review-rubric.md`](../../skills/review-code/references/review-rubric.md): admission gates 4 and 7, and the Complete inspection risk-signal list. |
| Installed two-axis `code-review` `SKILL.md` | The baseline under assessment. Its Standards brief asks for "any baseline smell you spot: name it and quote the hunk", always as a judgement call, with documented repository standards overriding it. |

## Reasons

1. **Admission already covers what a smell could legitimately contribute.** Gate 4 admits a
   maintainability candidate only after it demonstrates "the exact contradiction or drift and the
   concrete reader or maintenance consequence". Gate 7 drops "generic preferences". A Duplicated
   Code or Mysterious Name instance with a proven consequence is already admissible as
   `maintainability`, with no label. Without that consequence, a baseline would not change the
   outcome.
2. **The only compatible shape adds attention cost for no demonstrated recall.** #235 bounds any
   adoption to a risk-signal aid beside "Use risk signals to direct attention, not to create
   findings". Every signal in that list names a correctness, security, compatibility, or hygiene
   surface, and [risk-led discovery](../../skills/review-code/references/review-rubric.md) spends
   bounded reads on the risk each one names. Twelve design-taste signals would direct those reads at
   surfaces where no miss is on record. Adding them would still be an admission-adjacent change and
   would bump the identifier.
3. **Earlier research already rejected the baseline for this reason.** The
   [candidate survey](agentic-code-review-candidates.md) found that handing a taste checklist to an
   agent is "close to the worst-case prompt shape for precision". It recommended demoting the list
   below a consequence-and-intent gate. `review-code`'s gates now do that work without the list.
4. **The reconsideration condition has not occurred.** No cited routine run has missed a
   maintainability defect that the baseline names:
   - The [#216 diagnosis](routine-review-diagnosis-2026-09-13/README.md) found one material missed
     concept (C05, a ruling-table glob) plus low-impact reporting and documentary omissions. None is
     a smell-named defect.
   - The [target-j scorecard](one-shot-qualification-2026-09-07/scoring/j-scorecard.md) points the
     other way. All four blind reviews there, under the older `v5b-10`/`v5b-1` snapshots, raised a
     smell-shaped dead-branch finding that the register had graded true but non-material. None of
     them recovered the material defect. This is one target on superseded policy, so it supports no
     claim about `v5b-17`. It only shows that such facts already surface without a baseline.

## What would be evaluated if reopened

This section is not proposed and not authorized. A future implementation issue would have to specify:

- the exact text, placed as a risk-signal aid in `review-rubric.md`'s Complete inspection section;
- no new finding channel, label, or "possible X" comment form;
- the workflow identifier bump past `v5b-17`;
- two replays: one where a smell directs a bounded read that leads to a finding admitted under the
  ordinary gates, including a demonstrated maintenance consequence, and one where the smell is present
  but correctly produces no finding.

## Reconsideration trigger

Reconsider only when a routine `review-code` run misses a maintainability defect that the baseline
names, and the run and the defect are both cited. This record schedules no collection or paid run.
Until such a case exists, #235 is closed with this disposition.
