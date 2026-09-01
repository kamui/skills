# Independent review verifier

Read this reference only when `SKILL.md` requires independent verification. It defines a candidate mode and a clean-verdict mode. The verifier fact-checks supplied records; it is not a second reviewer, cannot search for unrelated findings, and cannot write to the pull request.

## Isolation

Run each permitted batch in a genuinely fresh context. Do not inherit the primary review conversation, its chain of reasoning, or prior finder output. In a harness with fork controls, use an empty or minimal fork such as `fork_turns=none`; otherwise start an equivalent clean worker.

If the runtime cannot provide that isolation, do not imitate independent verification in the primary context. Report mandatory verification as incomplete under the handling rules below.

For candidate mode, give the verifier only:

- the repository and pinned base, head, and merge-base;
- linked issue/spec coordinates and applicable base-branch rule coordinates;
- the following candidate record for each candidate; and
- permission to inspect the cited code and the narrow callers, tests, configuration, history, or issue text needed to decide it.

For each candidate, provide `id`, `kind`, `priority`, `action`, `anchor`, optional `fix`, `title`, `claim`, `trigger`, `impact`, `change`, raw code citations, and any requirement or rule citation. Do not provide the primary reviewer's `support`, confidence, conclusion, or argument for believing the claim.

`claim` is the falsifiable statement about the changed artifact. `support` is the primary reviewer's private account of what it inspected, ran, inferred, or could not establish. Separating them prevents the verifier from merely agreeing with the first reviewer's reasoning.

For clean-verdict mode, give it the same pinned coordinates and rules plus the complete candidate disposition ledger: each `id`, `kind`, `claim`, disposition, decisive evidence, and falsification reason. Each ledger entry is passed in the compact form of at most a one-line `claim`, the `kind`, the one-word `disposition`, a one-line falsification reason, and one decisive evidence pointer in `path:line` form; the verifier requests nothing beyond the ledger and reads the cited code itself. Withhold `support` and the primary's narrative argument here too.

## Verification task

For each candidate, independently:

1. Read the cited anchor and actual fix site, then only enough surrounding context to decide the claim.
2. Reproduce or trace the stated trigger through the current code.
3. Establish the observable impact and whether unchanged code prevents it.
4. For a Code candidate, confirm that the reviewed diff introduced the behavior. For `kind=requirement`, decide whether the explicit requirement made this change responsible for the outcome; never refute it merely because the missing implementation predates the diff or lives in an unchanged file.
5. Confirm that the issue, pull-request description, rules, or history do not make it intentional.
6. Check whether another candidate requests the same underlying change.

For synchronization drift, compare the peer artifacts at the merge-base and inspect the last commit that changed their shared rule. For a requirement candidate, verify the required outcome without assuming a particular representation. Calibrate `action` independently from priority: an explicit requirement gap on an authoritative execution path may be P2/P3 and still `must-fix`, while optional normative consistency remains `consider` when canonical behavior is intact.

For every confirmed `kind=concurrency` or `kind=invariant` candidate:

1. name the broken invariant;
2. enumerate the sibling code paths governed by it and state for each whether the proposed `change` protects that path; and
3. when the proposed fix covers only one projection of the bug class, correct `change` to the invariant-level outcome that covers every exposed sibling path.

Do not search the rest of the pull request for new findings. If an accurate, sub-threshold fact surfaces incidentally, return at most one explicitly non-actionable `observation` aside with a decisive evidence pointer and no `should` or `must` language. Do not weaken a verdict merely because a test has not yet been written; decide from the strongest available evidence.

## Verdicts

Return exactly one verdict for every supplied id:

- `confirmed`: decisive evidence establishes the trigger, qualifying impact, requested outcome, and either the Code introduced-here condition or the explicit requirement responsibility.
- `plausible`: the verifier can neither construct the claimed failing trace end-to-end nor refute any specific step of that trace from repository evidence. Return `plausible` whenever both conditions hold; do not force uncertainty into `confirmed` or `refuted`.
- `refuted`: decisive evidence shows the claim is false, prevented, intentional, lacks a qualifying impact, or—only for a Code candidate—is pre-existing.

For each id, return the verdict, a concise independent justification, the decisive code or requirement citations, and any correction to `trigger`, `impact`, `priority`, `action`, `anchor`, `fix`, or `change`. Also return groups of duplicate ids that should be merged. Do not return publication-ready prose.

## Clean-verdict task

Attack each acquittal in the supplied disposition ledger using its cited code and the narrow surrounding evidence needed to decide whether the disposition holds. Do not invent a new claim. The ledger is never filtered by risk surface: every disposition from the run is present, including candidates whose subject looks unrelated to the surface that triggered this batch. Return exactly one batch conclusion:

- `clean verdict stands` when every disposition survives; or
- `disposition <id> does not hold; re-open it` for each existing candidate whose stated acquittal is contradicted or unsupported.

For every re-opened id, cite the failed disposition step and decisive evidence. The primary reviewer re-runs falsification on only those records and uses the one permitted follow-up candidate batch if any becomes render-eligible.

## Primary reviewer handling

The primary reviewer owns the final decision and must validate any corrections against the diff:

- Publish a mandatory-verification candidate only when it is `confirmed`.
- Drop a `refuted` candidate without mentioning it.
- Do not publish a `plausible` candidate as a finding. Turn its single missing fact into a question when the answer could change the review outcome and no static evidence can settle it; name the benchmark, measurement, author, or maintainer decision that can. Frame it as `Change no code for this`, give it no priority, and keep the candidate's stable id while changing the trailer type from `finding` to `question`.
- Keep `independent-confirmed` when a confirmed candidate is corrected from `must-fix` to `consider` or otherwise falls below the threshold that originally put it in the batch.
- Merge duplicates around one stable id and one requested outcome.
- If the verifier omits a candidate, fails, or cannot inspect required evidence, mark verification and coverage incomplete. Do not publish that candidate or approve the change on the strength of incomplete verification.
- Route a verifier `observation` aside through the rubric and output cap; it never becomes a finding without full primary admission and any required follow-up verification.

Independent confirmation does not replace the rubric. The primary reviewer still checks every admission gate, renders the authoritative prose, validates anchors and metadata, and performs the stale-head check before publication.
