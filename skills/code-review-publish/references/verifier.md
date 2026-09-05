# Independent review verifier

Read this reference only when `SKILL.md` requires independent verification. It defines a candidate mode and a clean-verdict mode. The verifier fact-checks supplied records; it is not a second reviewer, cannot search for unrelated findings, and cannot write to the pull request.

## Isolation

Run each permitted batch in a genuinely fresh context. Do not inherit the primary review conversation, its chain of reasoning, or prior finder output. In a harness with fork controls, use an empty or minimal fork such as `fork_turns=none`; otherwise start an equivalent clean worker.

If the runtime cannot provide that isolation, do not imitate independent verification in the primary context. Report mandatory verification as incomplete under the handling rules below.

For candidate mode, give the verifier only:

- the repository and pinned base, head, and merge-base;
- linked issue/spec coordinates, the pull-request title and body when any candidate cites a `pr-title` or `pr-body` requirement coordinate, and applicable base-branch rule coordinates;
- the following candidate record for each candidate;
- the `ranges` lines from `scripts/review_context.py` for each candidate's anchor and fix, so the verifier reads them in one message;
- for a candidate whose claim rests on a focused check the primary ran, the recorded command, head, exit status, and decisive output lines, as an evidence citation without the primary's interpretation;
- when `SKILL.md`'s related-acquittal mode applies, the related non-survivor ledger rows, each in the compact form described for clean-verdict mode below; and
- permission to inspect the cited code and the narrow callers, tests, configuration, history, or issue text needed to decide it.

For each candidate, provide `id`, `kind`, `priority`, `action`, `anchor`, optional `fix`, `title`, `claim`, `trigger`, `impact`, `change`, raw code citations, and any requirement or rule citation. Do not provide the primary reviewer's `support`, confidence, conclusion, or argument for believing the claim.

`claim` is the falsifiable statement about the changed artifact. `support` is the primary reviewer's private account of what it inspected, ran, inferred, or could not establish. Separating them prevents the verifier from merely agreeing with the first reviewer's reasoning.

For clean-verdict mode, give it the same pinned coordinates and rules plus the complete candidate disposition ledger: each `id`, `kind`, `claim`, disposition, decisive evidence, and falsification reason. Each ledger entry is passed in the compact form of at most a one-line `claim`, the `kind`, the one-word `disposition`, a one-line falsification reason (including any refutation basis and, for `unresolved`, its settling fact), and one decisive evidence pointer in `path:line` form; the verifier requests nothing beyond the ledger and reads the cited code itself. Preserve any safety assertion's scope in that reason. Name unavailable evidence as unavailable rather than inventing a pointer. Withhold `support` and the primary's narrative argument here too.

## Verification task

For each candidate, independently:

1. Read the cited anchor and actual fix site as bounded ranges at head and at the merge-base (`git show <merge-base>:<path>` with a line range), then only enough surrounding context to decide the claim. Read a whole file only when a conditional the claim depends on cannot be located otherwise; say so.
2. Reproduce or trace the stated trigger through the current code.
3. Establish the observable impact and whether unchanged code prevents it.
4. For a Code candidate, confirm that the change introduced the behavior, or that it removed the guarantee an unchanged path relied on; state which of the two applies and cite the base-branch guarantee (`git show <merge-base>:<path>`) and the head-branch code that no longer provides it. For `kind=requirement`, decide whether the explicit requirement — the issue or spec requirement, or the pull-request promise of a concrete outcome, at the source coordinate the candidate cites — made this change responsible for the outcome; never refute it merely because the missing implementation predates the diff or lives in an unchanged file, or because its source is the pull-request body rather than an issue.
5. Confirm that the issue, pull-request description, rules, history, or review record do not make it intentional. A maintainer's approval, LGTM, or merge establishes intent only for what the review record explicitly addresses; it is provisional for public API surface that appears in no released version at the merge-base, and an explicit deferral in that record ("we can fix this during the API review") marks the deferred question open, not settled.
6. Check whether another candidate requests the same underlying change.

For a candidate whose claim is that a test the diff adds or changes fails, or passes without exercising the behavior it claims, decide by execution or by a bounded semantics trace, and say which. Execution means running the cited focused command once, at the pinned head, in a disposable environment under the run policy and safety bounds the rubric's Changed tests section sets for the primary; never a suite. A decisive existing output — an exact-head CI log, or the primary's recorded command, head, exit status, and output lines — may stand in for a run only after checking that it names the same head and the same test; a reported pass or failure without those fields is not evidence. When execution is unavailable, trace the decisive lines under the language's execution rules — which statement evaluates which expression, and when — from the test's setup through its assertions, and cite each line. An environmental failure refutes nothing and confirms nothing: return `unresolved` with the settling fact.

For synchronization drift, compare the peer artifacts at the merge-base and inspect the last commit that changed their shared rule. For a requirement candidate, verify the required outcome without assuming a particular representation. Calibrate `action` independently from priority: an explicit requirement gap on an authoritative execution path may be P2/P3 and still `must-fix`, while optional normative consistency remains `consider` when canonical behavior is intact.

For every confirmed `kind=concurrency` or `kind=invariant` candidate:

1. **State the invariant at the rule level, not the transition level.** Name which counters, flags, queue contents, or ownership records must stay consistent with which operations, and under which lock or ordering that consistency was guaranteed at the merge-base. Do not name it as "during X" (a transition); name it as "A must never be observed inconsistent with B".
2. **State whether the candidate's failing interleaving requires runtime shutdown, teardown, or an error path.** If it does, additionally ask whether the same rule can fail in steady state, and trace at least one steady-state interleaving (normal spawn, normal wake, normal idle) to a `holds` or `fails` verdict with `path:line` citations.
3. **Enumerate sibling interleavings before sibling code paths.** For each pair of concurrent actors that touch the rule's state — producer vs consumer, spawner vs worker-going-idle, spawner vs worker-exiting, spawner vs shutdown, claimant vs releaser — state whether the rule holds, citing the lines where each actor reads and writes the shared state.
4. **Then enumerate sibling code paths** governed by the rule and state for each whether the proposed `change` protects it.
5. **Widen `change` to the rule level when needed.** When the proposed fix covers only one interleaving or one path, correct `change` to the outcome that restores the rule for every failing interleaving found in steps 2–3. If the rule can only be restored by re-serializing two operations, say which two and under which lock.

A `change` that closes the shutdown projection while a steady-state projection of the same rule remains open is narrower than the bug class; say so in the correction.

Do not search the rest of the pull request for new findings. If an accurate, sub-threshold fact surfaces incidentally, return at most one explicitly non-actionable `observation` aside with a decisive evidence pointer and no `should` or `must` language. Safety rulings about supplied candidates belong in their verdicts under the next section. An incidental fact that contradicts the decisive premise of any supplied ledger row instead returns as `disposition <id> does not hold; re-open it`, citing the contradicted premise and decisive `path:line`. Use the observation aside only for facts that neither rule on a candidate's safety nor contradict a row. Do not weaken a verdict merely because a test has not yet been written; decide from the strongest available evidence.

## Scoped safety rulings

Every assertion that a supplied candidate's path is safe, unreachable, handled, or correct is a scoped acquittal, even inside a `confirmed` verdict or a proposed correction. State the path, state/ordering conditions, and exact premise established; apply all five opposite-branch steps of the clean-verdict task below to that safety premise, regardless of candidate kind. A working trace alone cannot establish safety on other branches. Cite the decisive evidence for the asserted scope, including the procedure's additional citation. If evidence cannot settle the premise, record it as unresolved rather than safe.

Keep each such ruling, including steady-state `holds`/`fails` with citations, inside the candidate verdict. A safety assertion with no citation has no power to narrow a confirmed finding. When cited safety evidence narrows or contradicts the finding's rule-level scope, flag the scope dispute on that id for primary falsification before any remedy is rendered. Neither an observation aside nor prose beside the finding may silently undermine it. A refutation establishes only its stated basis and scope; it does not establish that the whole change is correct.

## Verdicts

Return exactly one of the two verdicts below for every supplied *candidate* id:

- `confirmed`: decisive evidence establishes the trigger, qualifying impact, requested outcome, and either the Code introduced-here condition or the explicit requirement responsibility.
- `refuted`: include exactly one compact `basis`: `contradicted` (a cited step is false), `prevented` (a cited guard blocks the consequence), `intentional` (established under task step 5), `pre-existing` (Code only: the same failing path was unsafe at the merge-base under the same guarantees), `no-consequence` (evidence establishes no qualifying impact), or `unresolved` (the trace can neither be completed nor specifically refuted). Unchanged code whose relied-on guarantee the diff removed is not `pre-existing`; an unproven consequence is `unresolved`, not `no-consequence`. For `unresolved`, name in one sentence the single settling fact and who or what measurement can supply it. This basis withholds a finding; it supplies no evidence that the surface is safe.

A related non-survivor row supplied under related-acquittal mode is not a candidate: it takes exactly one `holds` or `re-open` ruling under the clean-verdict task and never a verdict from this list.

For each candidate id, return the verdict, its basis (the decisive justification for `confirmed`, the named basis above for `refuted`), decisive code or requirement citations, scoped safety rulings if any, and any correction to `trigger`, `impact`, `priority`, `action`, `anchor`, `fix`, or `change`. Keep these as compact records, not a second report; no confidence scores or additional verdict branch. Also return groups of duplicate ids that should be merged. Do not return publication-ready prose.

## Clean-verdict task

Attack each acquittal supplied to you, using its cited code and the narrow surrounding evidence needed to decide whether the disposition holds. This task runs in the two modes `SKILL.md` defines: a zero-survivor batch carrying the complete disposition ledger (initially or after candidate refutations), and the related-acquittal rows supplied with a candidate batch — a follow-up batch may carry such rows with no candidate at all, and they are ruled on the same way. Follow this procedure for every row you rule on, in either mode, to the depth the kind rule below sets; scoped safety rulings always take all five steps:

1. Restate the row's decisive premise in one sentence — the fact the acquittal depends on, such as "`sender->slaveof` is always non-NULL when `updateShardId()` runs."
2. State the concrete condition under which that premise would be false.
3. Trace the *opposite* branch of every conditional the premise depends on — a failed lookup, a NULL pointer, an error return, an empty list, a timeout, a counter already decremented — through the current code, citing `path:line` for each step.
4. Either construct the complete failing state transition from trigger to observable consequence, or cite the specific step that is impossible.
5. Re-reading the ledger's own reasoning and agreeing with it is not a verdict. A `holds` ruling on a fully attacked row — including every such row covered by `clean verdict stands` — must cite at least one line the ledger row did not cite.

Attack depth follows the row's `kind`. The five steps apply in full to every row whose `kind` is `bug`, `concurrency`, `invariant`, or `security`. Every other row — `performance`, `maintainability`, or `requirement` — gets a one-citation check instead unless it asserts safety: read the row's evidence pointer, confirm or contradict its stated fact, and return `holds` or `re-open` without tracing conditionals. The row list itself does not shrink; in zero-survivor mode every disposition from the run is still present. Depth is reduced, coverage is not. Related-acquittal mode supplies only the four full-depth kinds, so every row it carries gets the full procedure.

An `unresolved` row asserts an evidence gap, not safety. Check whether its settling fact is truly unavailable under the primary-handling rules; `holds` preserves that gap and its question/coverage routing. Return `re-open` if the claimed gap or a safety premise is contradicted or unsupported. Neither `holds` on an unresolved row nor `clean verdict stands` clears an outstanding question or incomplete coverage.

Do not invent a new claim. In zero-survivor mode the ledger is never filtered by risk surface: every disposition from the run is present, including candidates whose subject looks unrelated to the surface that triggered this batch. In related-acquittal mode the batch carries only the related rows defined in `SKILL.md`, and the verifier may request no others.

Return `holds` or `re-open` for every supplied ledger id with its decisive evidence or named unresolved gap. In zero-survivor mode, also return exactly one batch conclusion:

- `clean verdict stands` when every disposition survives that procedure; or
- `disposition <id> does not hold; re-open it` for each supplied ledger row whose stated acquittal is contradicted or unsupported.

In related-acquittal mode, return `holds` or `re-open` for each related row alongside the candidate verdicts, on the same standard: `re-open` when the stated acquittal is contradicted or unsupported. A `re-open` carries the same wording as the zero-survivor conclusion, `disposition <id> does not hold; re-open it`.

For every re-opened id, cite the failed disposition step and decisive evidence or the missing settling fact. The primary reviewer re-runs falsification on only those records and uses the one permitted follow-up batch if still available and any becomes render-eligible. A re-open from the follow-up itself earns no third batch; mandatory confirmation still missing makes verification incomplete. `clean verdict stands` validates only the supplied dispositions, not global safety.

The single non-actionable `observation` aside permitted by the verification task is available in both modes on the same terms. Safety rulings stay in their candidate verdict or ledger ruling; contradictions of supplied ledger premises return as `re-open`, never as observations.

## Primary reviewer handling

The primary reviewer owns the final decision and must validate any corrections against the diff:

- Publish a mandatory-verification candidate only when it is `confirmed`.
- Record every `refuted` candidate's basis and scoped evidence in the compact ledger; omit the dropped finding from publication, subject to the next bullet. Apply `SKILL.md`'s post-initial zero-survivor check to the updated ledger.
- For basis `unresolved`, withhold the finding. Publish a question only when the rubric's static-unresolvability rule is met (no static source available to the reviewer could settle an outcome-changing fact); keep the stable id and use the `question` trailer type. If available static work could settle it, finish that work; if material work or required evidence remains unavailable or unfinished, mark coverage/verification incomplete and use the existing recovery rule. Otherwise keep the non-material drop private. The unresolved basis alone establishes neither safety nor completed verification; completed static-unresolvability routing may leave coverage complete with an open question.
- Validate scoped safety evidence under the procedure above. Re-run primary falsification on a cited scope dispute before rendering the remedy; if it changes a mandatory claim beyond what was confirmed, obtain confirmation in the remaining follow-up or withhold that claim with incomplete verification. An unsettled material scope dispute likewise leaves the affected finding unpublished and coverage incomplete; already verified unrelated findings may publish.
- Keep `independent-confirmed` when a confirmed candidate is corrected from `must-fix` to `consider` or otherwise falls below the threshold that originally put it in the batch.
- Merge duplicates around one stable id and one requested outcome.
- If the verifier omits a required candidate verdict/basis or ledger ruling, fails, or cannot inspect required evidence, mark verification and coverage incomplete. Do not publish the affected candidate or approve the change on the strength of incomplete verification.
- Treat every returned `re-open`, in either clean-verdict mode, as a re-opened disposition: re-run falsification on that record and use the one permitted follow-up batch if still available and it becomes render-eligible; otherwise apply the incomplete-verification rule. Do not downgrade it to an observation.
- Route a verifier `observation` aside through the rubric and output cap; it never becomes a finding without full primary admission and any required follow-up verification. An aside the cap excludes is recorded in the private record as unpublished, not merged into a finding's prose.

Independent confirmation does not replace the rubric. The primary reviewer still checks every admission gate, renders the authoritative prose, validates anchors and metadata, and performs the stale-head check before publication.
