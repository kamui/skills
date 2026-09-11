# Evaluation — issue #153, the #138 decision

**Inconclusive, for both candidate arms.** The frozen screen cannot return a verdict on this
evidence: eighteen of the twenty-four planned cells were never attempted, two of the three buggy
targets have no attempt at all, and none of the eight attempts that ran is a valid completed
outcome, because the closeout could not certify any of them faithful and invalidated three. No arm
can be rejected either: the independent grading ruled **zero raw false findings** in every packet,
and a supported false finding is the one thing the frozen rules let reject an arm on a partial grid.
Nothing here promotes a default, recommends a confirmation study, or authorises another cell.

Data: [`comparison-data.md`](comparison-data.md). The scorer's own output:
[`scorecard-v2.md`](scorecard-v2.md) against graded truth and [`scorecard-v1.md`](scorecard-v1.md)
against the registers as frozen. The decision record is [`decision.json`](decision.json); the stage
record is [`handoff.json`](handoff.json). The revealed truth, schedule, packets, redaction map and
ruling tables are under [`revealed/`](revealed/), each byte-identical to the digest its stage
sealed ([`verification.json`](verification.json)).

## 1. The screening rule, applied

Preregistration section 8, applied by the pinned `score_attempts.py` (digest checked against the
frozen manifest before it ran). Every criterion must hold for a positive screen; a blocker forces
`inconclusive`; a supported false finding rejects outright.

| # | Gate | Threshold | B against A | C against A |
| --- | --- | --- | --- | --- |
| 1 | Raw false findings in the candidate arm, invalid attempts included | zero | **0 — pass** | **0 — pass** |
| 2 | False-clean count and rate | no worse | 0 (0%) vs 1 (100%) — pass | 0 (0%) vs 1 (100%) — pass |
| 3 | Completion, valid completed / dispatched | no worse | 0/2 vs 0/3 — pass | 0/3 vs 0/3 — pass |
| 4 | Macro material recall, all attempts | ≥ +20% relative, positive absolute | **unavailable** | **unavailable** |
| 4b | Macro material recall, completed only | same | **unavailable** | **unavailable** |
| 5 | Median matched billed cell-cost ratio | ≤ 1.25 | 1.205 over 2 pairs — pass | **2.106 over 2 pairs — fail** |
| | Blockers | none | 18 cells unattempted; 6 attempted without a valid completed outcome; macro unavailable | same |
| | **Verdict** | | **inconclusive** | **inconclusive** |

The verdict is the same against v1 truth. The macro is unavailable because it is an equal-weight
mean over the three buggy targets and two of them were never attempted; the rule leaves it
unavailable rather than counting an unattempted target as zero. Gate 3 passes vacuously: no arm has
a valid completed attempt, so no arm is worse. Gate 5's fail for C is a measured fact on two pairs
and is reported as such; under the frozen rule a blocker outranks a criterion fail, so the verdict
is `inconclusive`, not `fail`, and the section below says what the two pairs show.

## 2. What was measured

The pilot ran one replicate of each arm on two targets: the adjudicated clean slot
(`grpc/grpc-go#7417`) and the lowest-numbered buggy slot (`clap-rs/clap#6212`). Everything below
is one replicate on one buggy target, joined to operational validity after the rulings froze.

**On the clean target, every arm returned Approved with zero findings**, and every explicit
safety claim in the three summaries was ruled supported. Arm C's finder raised two concurrency
claims about the fixed early return; the primary falsified both against the documented balancer
contract before any verifier saw them, and the clean-verdict batch upheld the rejections. Both
rejections were right: the register lists that class of objection under not-ground-truth. That is
the admission step doing what the design asks of it, and it is why C carries no false finding.

**On the buggy target the three arms diverged, and none of the three outcomes is admissible.**

- **A returned Approved with zero findings** — a false clean under the frozen definition. Its
  primary raised three candidates (a redundant predicate call, a test-name mismatch, and an
  adjacent `num_args` edge case it correctly traced to a pre-existing path) and none named either
  defect. No verifier ran: with zero survivors, the pinned policy dispatches a clean-verdict batch
  only on a concurrency, data-integrity or security surface, and command-line parsing is none of
  them. Both defects are lost at `never-discovered`, and the clean verdict at
  `omitted-from-verification-by-policy`. The attempt is operationally `unresolved`.
- **B recovered both defects** with a sufficient fix for the one grading added (GT-p2) and a
  partial fix for the registered one (GT-p1). The primary found the option-state fall-through
  itself; the `claude-opus-5` verifier confirmed it and added the single-positional `.last(true)`
  scenario, which is GT-p1's register manifestation, and the primary folded it in and raised the
  priority. The attempt is **invalid on protocol grounds** — a read outside its permitted roots —
  so the recovery is measured and not admissible.
- **C recovered both defects** with the same fix rulings. The primary had frozen GT-p2 before the
  discovery barrier; the finder supplied GT-p1 (the `trailing_values` omission and the
  `.last(true)` hard error), the primary admitted it, and the shared verifier confirmed both. This
  is the pilot's **one finder-origin material recovery**. The session then hit the $9.00 ceiling
  during its final re-validation, after the payload was written: `stopped-budget`, so the cap took
  the validation mark and the report's post-barrier sections, not the finding. The attempt is
  `unresolved` and stopped, so the recovery is measured and not admissible.

The scope selector did not miss: both defects sit inside the selected fourteen lines. Neither
sufficient-fix ruling covers GT-p1's single-positional manifestation, which the pull-request review
of #152 surfaced and both adjudicators reproduced at the head and the merge-base, so both recovering
arms hold one sufficiency credit out of two. No packet carries an action or priority error.

**Cost.** Matched by target and replicate, each cell charged every attempt including its
discarded predecessor: B/A is 1.405 on the buggy target and 1.005 on the clean one, median 1.205;
C/A is 1.987 and 2.224, median 2.106; C/B is 1.414 and 2.214, median 1.814. C's clean-target
cell carries a $1.58 discarded predecessor (a provider error at turn 43); without it that pair is
1.814 and C's median 1.90, still above the gate. Where C's money went, by #151's recovered role
split: $2.56 of finder, $2.84 of verifier and $12.15 of primary across three attempts, against A's
$0.62 of verifier and $7.75 of primary — C's primary runs as two invocations and falsifies the
finder's claims, and that is the treatment, not a confound.

**Elapsed.** Root elapsed for complete attempts: A 18.5 and 31.1 minutes, B 20.2 and 27.8, C 31.3;
C's stopped attempt was censored at 35.8. Every arm ran its verifier in the foreground by the frozen
rule, so these are this harness's timings and say nothing about the policy's production timing or
about whether deferring verification is cheaper in time.

## 3. Truth, versioned

Grading confirmed a second defect on the buggy slot, independently, by running a test at the pinned
head and the merge-base: the register moves to `v2` with two defects and every attempt on it is
scored against `v2`, with the `v1` figures beside. The clean/buggy mix is unchanged. Against `v1`
the two recovering attempts hold one recovery each and **no** sufficient fix, because the only fix
ruled sufficient restores the added defect. Two rulings were amended on the review evidence as a
versioned layer over the byte-unchanged frozen tables; the join reads the amended derived fields and
verifies both freeze records first.

## 4. What this does and does not establish

- **It does not test the hypothesis.** Whether a stronger verifier, or a bounded finder ahead of
  one, recovers more than the control is a question about the frozen 24-cell design, and the design
  did not run: one buggy target, one replicate, no faithful attempt. The per-target row where both
  candidate arms recovered what the control approved is a **hypothesis for a future freeze**, not
  evidence for one, and the finder-origin recovery is one observation.
- **Nothing here says `claude-opus-5` verifies better than `claude-sonnet-5`.** That was the
  treatment hypothesis; it remains untested.
- **The negative observation stands on its own.** The control's false clean on this target is the
  same shape #137 recorded on its cross-file target and #124 recorded under #185: an acquittal on a
  surface outside the zero-survivor vocabulary ships as Approved with no verifier exposure. That is a
  gap in the pinned #136 policy, already carried in #129's known limits, and it is not a regression
  measured by this grid.
- **Isolation regime.** Every cell ran in a container mounting only its permitted roots, because
  host absence was unreachable. Cells under a different regime would not be comparable to these.
- **Blinding was label masking**, and every cue is listed; none was resolved before the freeze.
- **The four targets are now revealed** and stay reserved: any future study needs fresh targets.

## 5. What would change the conclusion

- **Reject** needs a supported raw false finding in a candidate arm. None was ruled in any of the
  six packets, so no arm can be rejected on this evidence, and no amount of missing cells changes
  that.
- **Proceed to fresh confirmation** needs a complete positive screen: valid completed cells on all
  four targets with the frozen mix, recall and cost gates met. The frozen limits cannot fund it —
  one replacement remains against six cells that would have to be re-run — and the retained
  evidence cannot certify any attempt faithful, because the launch argv was never kept. It would
  take a new preregistration whose freeze closes [#199](https://github.com/kamui/skills/issues/199)'s
  seven gaps first, on fresh targets.
- **Inconclusive stands** if nothing further runs. Nothing runs from this handoff.

## 6. Cost and closure

This decision charged nothing: no model session ran for it, and the fresh-context review of this
bundle before publishing is ordinary ticket work outside the measured spend. The ledger stands
where #152 settled it: **$50.3304587** actual with $0.164316 retained uncertainty, no reservation
outstanding, an unbroken eighty-eight-event chain, and **$6.9831994** of the $10.00 protected
grading and closeout reserve unused. $99.5052253 remains under the $150.00 cap after the retained
uncertainty; none of it is authorised. The design's `stop` operation is not implemented in
`budget.py`, so no closing event is appended and this bundle is the closing record.

The epic's measurement is closed on this capped, inconclusive result. #138 closes on it; #129
records it under its known limits, with the false-clean observation beside #185's; #199 stays
unscheduled and becomes the precondition of any future freeze. `dispatch_authorized` is `false`.
