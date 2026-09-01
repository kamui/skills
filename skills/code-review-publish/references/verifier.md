# Independent finding verifier

Read this reference only when `SKILL.md` requires independent verification. The verifier is a fact-checker for surviving candidates, not a second reviewer or finding generator. It cannot write to the pull request.

## Isolation

Run one batched verifier in a genuinely fresh context. Do not inherit the primary review conversation, its chain of reasoning, or prior finder output. In a harness with fork controls, use an empty or minimal fork such as `fork_turns=none`; otherwise start an equivalent clean worker.

If the runtime cannot provide that isolation, do not imitate independent verification in the primary context. Report mandatory verification as incomplete under the handling rules below.

Give the verifier only:

- the repository and pinned base, head, and merge-base;
- linked issue/spec coordinates and applicable base-branch rule coordinates;
- the following candidate record for each candidate; and
- permission to inspect the cited code and the narrow callers, tests, configuration, history, or issue text needed to decide it.

For each candidate, provide `id`, `kind`, `priority`, `action`, `anchor`, optional `fix`, `title`, `claim`, `trigger`, `impact`, `change`, raw code citations, and any requirement or rule citation. Do not provide the primary reviewer's `support`, confidence, conclusion, or argument for believing the claim.

`claim` is the falsifiable statement about the changed artifact. `support` is the primary reviewer's private account of what it inspected, ran, inferred, or could not establish. Separating them prevents the verifier from merely agreeing with the first reviewer's reasoning.

## Verification task

For each candidate, independently:

1. Read the cited anchor and actual fix site, then only enough surrounding context to decide the claim.
2. Reproduce or trace the stated trigger through the current code.
3. Establish the observable impact and whether unchanged code prevents it.
4. Confirm that the reviewed diff introduced the behavior.
5. Confirm that the issue, pull-request description, rules, or history do not make it intentional.
6. Check whether another candidate requests the same underlying change.

For synchronization drift, compare the peer artifacts at the merge-base and inspect the last commit that changed their shared rule. For a requirement candidate, verify the required outcome without assuming a particular representation. Calibrate `action` independently from priority: an explicit requirement gap on an authoritative execution path may be P2/P3 and still `must-fix`, while optional normative consistency remains `consider` when canonical behavior is intact.

Do not search the rest of the pull request for new findings. Do not weaken a verdict merely because a test has not yet been written; decide from the strongest available evidence.

## Verdicts

Return exactly one verdict for every supplied id:

- `confirmed`: decisive evidence establishes the trigger, qualifying impact, introduced-here condition, and requested outcome.
- `plausible`: the mechanism may be real, but one outcome-changing fact cannot be established from repository evidence.
- `refuted`: decisive evidence shows the claim is false, prevented, pre-existing, intentional, or lacks a qualifying impact.

For each id, return the verdict, a concise independent justification, the decisive code or requirement citations, and any correction to `trigger`, `impact`, `priority`, `action`, `anchor`, `fix`, or `change`. Also return groups of duplicate ids that should be merged. Do not return publication-ready prose.

## Primary reviewer handling

The primary reviewer owns the final decision and must validate any corrections against the diff:

- Publish a mandatory-verification candidate only when it is `confirmed`.
- Drop a `refuted` candidate without mentioning it.
- Do not publish a `plausible` candidate as a finding. Turn its single missing fact into a question only when the answer could change the review outcome, repository evidence is exhausted, and the author or maintainer can reasonably supply it; otherwise drop it. Keep the candidate's stable id when changing the record type from `finding` to `question`.
- Merge duplicates around one stable id and one requested outcome.
- If the verifier omits a candidate, fails, or cannot inspect required evidence, mark verification and coverage incomplete. Do not publish that candidate or approve the change on the strength of incomplete verification.

Independent confirmation does not replace the rubric. The primary reviewer still checks every admission gate, renders the authoritative prose, validates anchors and metadata, and performs the stale-head check before publication.
