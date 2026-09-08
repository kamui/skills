# Independent review verifier

Read this reference only when `SKILL.md` requires independent verification. It owns the verifier's evidence procedure: what the verifier receives, how it decides, and what it returns. It defines a candidate mode and a clean-verdict mode; one batch may carry both tasks, and their records stay separate. The verifier fact-checks supplied records; it is not a second reviewer, cannot search for unrelated findings, and cannot write to the pull request. Which batches run, what they carry, and what the primary does with their results are `SKILL.md` step 3's rules; the brief carries no publication syntax — no trailers, comment shapes, or summary sections — because the verifier renders nothing.

## Isolation

Run each permitted batch in a genuinely fresh context. Do not inherit the primary review conversation, its chain of reasoning, or prior finder output. In a harness with fork controls, use an empty or minimal fork such as `fork_turns=none`; otherwise start an equivalent clean worker.

If the runtime cannot provide that isolation, do not imitate independent verification in the primary context. Report mandatory verification as incomplete to `SKILL.md` step 3.

For candidate mode, give the verifier only:

- the repository and pinned base, head, and merge-base;
- linked issue/spec coordinates, the pull-request title and body when any candidate cites a `pr-title` or `pr-body` requirement coordinate, and applicable base-branch rule coordinates; when any candidate cites an `artifact-` coordinate, the additional inputs [`conformance.md`](conformance.md)'s verifier section names;
- the following candidate record for each candidate;
- the `ranges` lines from `scripts/review_context.py` for each candidate's anchor and fix, so the verifier reads them in one message;
- for a candidate whose claim rests on a focused check the primary ran, the recorded command, head, exit status, and decisive output lines, as an evidence citation without the primary's interpretation;
- the ledger rows a batch carries beside its candidates, each in the compact form described for clean-verdict mode below: the related non-survivor rows under `SKILL.md`'s related-acquittal mode, or the complete disposition ledger when its no-material-survivor mode attaches the clean-verdict task to a candidate batch;
- [`verifier-concurrency.md`](verifier-concurrency.md) when any candidate's `kind` is `concurrency` or `invariant`; and
- permission to inspect the cited code and the narrow callers, tests, configuration, history, or issue text needed to decide it.

For each candidate, provide `id`, `kind`, `priority`, `action`, `anchor`, optional `fix`, `title`, `claim`, `trigger`, `impact`, `change`, raw code citations, and any requirement or rule citation. Do not provide the primary reviewer's `support`, confidence, conclusion, or argument for believing the claim.

`claim` is the falsifiable statement about the changed artifact. `support` is the primary reviewer's private account of what it inspected, ran, inferred, or could not establish. Separating them prevents the verifier from merely agreeing with the first reviewer's reasoning.

For clean-verdict mode, give it the same pinned coordinates and rules plus the complete candidate disposition ledger: each `id`, `kind`, `claim`, disposition, decisive evidence, and falsification reason. Each ledger entry is passed in the compact form of at most a one-line `claim`, the `kind`, the one-word `disposition`, a one-line falsification reason (including any refutation basis and, for `unresolved`, its settling fact), and one decisive evidence pointer in `path:line` form; the verifier requests nothing beyond the ledger and reads the cited code itself. Preserve any safety assertion's scope in that reason. Name unavailable evidence as unavailable rather than inventing a pointer. Withhold `support` and the primary's narrative argument here too.

## Verification task

For each candidate, independently:

1. Read the cited anchor and actual fix site as bounded ranges at head and at the merge-base (`git show <merge-base>:<path>` with a line range), then only enough surrounding context to decide the claim. Read a whole file only when a conditional the claim depends on cannot be located otherwise; say so.
2. Reproduce or trace the stated trigger through the current code.
3. Establish the observable impact and whether unchanged code prevents it.
4. For a Code candidate, confirm that the change introduced the behavior, or that it removed the guarantee an unchanged path relied on; state which of the two applies and cite the base-branch guarantee (`git show <merge-base>:<path>`) and the head-branch code that no longer provides it. For `kind=requirement`, decide whether the explicit requirement — the issue or spec requirement, the pull-request promise of a concrete outcome, or the versioned artifact's obligation, at the source coordinate the candidate cites — made this change responsible for the outcome; never refute it merely because the missing implementation predates the diff or lives in an unchanged file, or because its source is the pull-request body or a versioned artifact rather than an issue. For an `artifact-` obligation, apply the reading rule [`conformance.md`](conformance.md)'s verifier section supplies with the brief.
5. Confirm that the issue, pull-request description, rules, history, or review record do not make it intentional. A maintainer's approval, LGTM, or merge establishes intent only for what the review record explicitly addresses; it is provisional for public API surface that appears in no released version at the merge-base, and an explicit deferral in that record ("we can fix this during the API review") marks the deferred question open, not settled.
6. Check whether another candidate requests the same underlying change.

For a candidate whose claim is that a test the diff adds or changes fails, or passes without exercising the behavior it claims, decide by execution or by a bounded semantics trace, and say which. Execution means running the cited focused command once, at the pinned head, in a disposable environment under the run policy and safety bounds the rubric's Changed tests section sets for the primary; never a suite. A decisive existing output — an exact-head CI log, or the primary's recorded command, head, exit status, and output lines — may stand in for a run only after checking that it names the same head and the same test; a reported pass or failure without those fields is not evidence. When execution is unavailable, trace the decisive lines under the language's execution rules — which statement evaluates which expression, and when — from the test's setup through its assertions, and cite each line. An environmental failure refutes nothing and confirms nothing: return `unresolved` with the settling fact.

For synchronization drift, compare the peer artifacts at the merge-base and inspect the last commit that changed their shared rule. For a requirement candidate, verify the required outcome without assuming a particular representation. Calibrate `action` independently from priority: an explicit requirement gap on an authoritative execution path may be P2/P3 and still `must-fix`, while optional normative consistency remains `consider` when canonical behavior is intact.

For every confirmed `kind=concurrency` or `kind=invariant` candidate, apply the bug-class check in [`verifier-concurrency.md`](verifier-concurrency.md), which the brief carries whenever a supplied candidate has either kind: name the invariant at the rule level, answer the shutdown question with a steady-state trace, enumerate sibling interleavings and paths, and widen `change` to the rule.

Do not search the rest of the pull request for new findings. If an accurate, sub-threshold fact surfaces incidentally, return at most one explicitly non-actionable `observation` aside with a decisive evidence pointer and no `should` or `must` language. Safety rulings about supplied candidates belong in their verdicts under the next section. An incidental fact that contradicts the decisive premise of any supplied ledger row instead returns as `disposition <id> does not hold; re-open it`, citing the contradicted premise and decisive `path:line`. Use the observation aside only for facts that neither rule on a candidate's safety nor contradict a row. Do not weaken a verdict merely because a test has not yet been written; decide from the strongest available evidence.

## Scoped safety rulings

Every assertion that a supplied candidate's path is safe, unreachable, handled, or correct is a scoped acquittal, even inside a `confirmed` verdict or a proposed correction. State the path, state/ordering conditions, and exact premise established; apply all five opposite-branch steps of the clean-verdict task below to that safety premise, regardless of candidate kind. A working trace alone cannot establish safety on other branches. Cite the decisive evidence for the asserted scope, including the procedure's additional citation. If evidence cannot settle the premise, record it as unresolved rather than safe.

Keep each such ruling, including steady-state `holds`/`fails` with citations, inside the candidate verdict. A safety assertion with no citation has no power to narrow a confirmed finding. When cited safety evidence narrows or contradicts the finding's rule-level scope, flag the scope dispute on that id for primary falsification. Neither an observation aside nor prose beside the finding may silently undermine it. A refutation establishes only its stated basis and scope; it does not establish that the whole change is correct.

## Verdicts

Return exactly one of the two verdicts below for every supplied *candidate* id:

- `confirmed`: decisive evidence establishes the trigger, qualifying impact, requested outcome, and either the Code introduced-here condition or the explicit requirement responsibility.
- `refuted`: include exactly one compact `basis`: `contradicted` (a cited step is false), `prevented` (a cited guard blocks the consequence), `intentional` (established under task step 5), `pre-existing` (Code only: the same failing path was unsafe at the merge-base under the same guarantees), `no-consequence` (evidence establishes no qualifying impact), or `unresolved` (the trace can neither be completed nor specifically refuted). Unchanged code whose relied-on guarantee the diff removed is not `pre-existing`; an unproven consequence is `unresolved`, not `no-consequence`. For `unresolved`, name in one sentence the single settling fact and who or what measurement can supply it. This basis withholds a finding; it supplies no evidence that the surface is safe.

A related non-survivor row supplied under related-acquittal mode is not a candidate: it takes exactly one `holds` or `re-open` ruling under the clean-verdict task and never a verdict from this list.

For each candidate id, return the verdict, its basis (the decisive justification for `confirmed`, the named basis above for `refuted`), decisive code or requirement citations, scoped safety rulings if any, and any correction to `trigger`, `impact`, `priority`, `action`, `anchor`, `fix`, or `change`. Keep these as compact records, not a second report; no confidence scores or additional verdict branch. Also return groups of duplicate ids that should be merged. Do not return publication-ready prose.

## Clean-verdict task

Attack each acquittal supplied to you, using its cited code and the narrow surrounding evidence needed to decide whether the disposition holds. The rows arrive in one of the two modes `SKILL.md` step 3 defines: the complete disposition ledger under its no-material-survivor mode, which arrives either alone or beside candidates whose own verdicts stay separate, or related-acquittal rows beside a candidate batch. A batch may carry either kind of row with no candidate at all, and the presence of candidates changes nothing about how a ledger row is ruled on. Follow this procedure for every row you rule on, in either mode, to the depth the kind rule below sets; scoped safety rulings always take all five steps:

1. Restate the row's decisive premise in one sentence — the fact the acquittal depends on, such as "`sender->slaveof` is always non-NULL when `updateShardId()` runs."
2. State the concrete condition under which that premise would be false.
3. Trace the *opposite* branch of every conditional the premise depends on — a failed lookup, a NULL pointer, an error return, an empty list, a timeout, a counter already decremented — through the current code, citing `path:line` for each step.
4. Either construct the complete failing state transition from trigger to observable consequence, or cite the specific step that is impossible.
5. Re-reading the ledger's own reasoning and agreeing with it is not a verdict. A `holds` ruling on a fully attacked row — including every such row covered by `clean verdict stands` — must cite at least one line the ledger row did not cite.

Attack depth follows the row's `kind`. The five steps apply in full to every row whose `kind` is `bug`, `concurrency`, `invariant`, or `security`. Every other row — `performance`, `maintainability`, or `requirement` — gets a one-citation check instead unless it asserts safety: read the row's evidence pointer, confirm or contradict its stated fact, and return `holds` or `re-open` without tracing conditionals. The row list itself does not shrink: rule on every row supplied, whatever its subject, and request no others. Depth is reduced, coverage is not.

An `unresolved` row asserts an evidence gap, not safety. Check whether its settling fact is truly unavailable; `holds` preserves that gap and its question/coverage routing. Return `re-open` if the claimed gap or a safety premise is contradicted or unsupported. Neither `holds` on an unresolved row nor `clean verdict stands` clears an outstanding question or incomplete coverage.

Do not invent a new claim. Return `holds` or `re-open` for every supplied ledger id with its decisive evidence or named unresolved gap. When the brief carries the complete disposition ledger under no-material-survivor mode, also return exactly one batch conclusion, covering those ledger rows and no candidate verdict in the same batch:

- `clean verdict stands` when every disposition survives that procedure; or
- `disposition <id> does not hold; re-open it` for each supplied ledger row whose stated acquittal is contradicted or unsupported.

When the brief instead carries related-acquittal rows, return `holds` or `re-open` for each of them alongside the candidate verdicts, with no batch conclusion, on the same standard: `re-open` when the stated acquittal is contradicted or unsupported. A `re-open` carries the same wording in either mode, `disposition <id> does not hold; re-open it`.

For every re-opened id, cite the failed disposition step and decisive evidence or the missing settling fact. `clean verdict stands` validates only the supplied dispositions, not global safety. The single non-actionable `observation` aside permitted by the verification task is available in both modes on the same terms. Safety rulings stay in their candidate verdict or ledger ruling; contradictions of supplied ledger premises return as `re-open`, never as observations.

## What the primary does with the return

`SKILL.md` step 3 owns it: validating corrections against the diff, merging duplicates, recording refutation bases, settling scope disputes, re-falsifying re-opened rows, spending the one follow-up batch, and declaring verification incomplete when a required verdict or ruling is missing. The rubric's Uncertainty routing owns an `unresolved` basis, and its Observations section owns an aside. Independent confirmation never replaces the rubric: the primary still checks every admission gate, renders the authoritative prose, validates anchors and metadata, and performs the stale-head check before publication.
