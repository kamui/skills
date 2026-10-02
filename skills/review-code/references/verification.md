# Verification

Read when the complete primary pass has selected required or optional verification tasks. Candidate tasks take `confirmed` or `refuted`; safety-premise tasks take `holds`, `fails`, or `unresolved`. The primary owns admission and rendering.

## Dispatch and allowance

Record each task's id, trigger or area, premise and evidence when applicable, batch, and ruling. Candidate triggers are `must-fix`, `security`, `data-integrity`, `destructive-migration`, `compatibility`, `prior-must-fix`, or `optional`. Optional premises use `trigger: optional`. Undispatched tasks are `pending`; unusable returns are `withheld`.

After the complete diff, file accounting, and primary falsification, combine selected tasks in one initial batch. Choose an awaited host route before dispatch and record its operation. An agent id or acknowledgment is not completion. With no awaited route or no fresh-context isolation, dispatch nothing and report required verification incomplete, naming `review-wait-unavailable` when appropriate. Never hand back while a batch is pending.

Start the initial batch in a fresh worker without the primary conversation, such as `fork_turns=none`. For the follow-up, resume that worker when available and still isolated from the primary conversation at the same pinned revisions and relevant inputs; otherwise start a fresh worker. The builder embeds the worker instructions, return encoding, and applicable specialized procedures, so the primary does not read `verifier.md` or `verifier-concurrency.md`. A failed batch still spends its allowance; repairs and worker changes grant no replacement batch.

## Reconcile

Read the accounting report, whose `return` holds the complete worker return, before using a ruling. Candidates carry `verdict`, `basis` (a refutation's `unresolved` adds `settling_fact`), `evidence`, and optional `corrections` and `safety_rulings`; premises carry `ruling`, `evidence`, and `failed_step` or `settling_fact`. `duplicate_groups` only suggest merges; `observation` is one optional aside. Accounted means structurally usable, not true. Check citations, corrections, admission, priority, and scope against the diff. Merge duplicates under one stable id and remedy. Required candidates publish only when confirmed; refuted candidates are withheld. For basis `unresolved`, finish available static work, then route a required task to a material question retaining its id or to `outstanding`.

A cited safety ruling that narrows or contradicts a finding reopens primary falsification. If a mandatory claim changes beyond its confirmation, reconfirm it in the follow-up or withhold it with incomplete coverage. An unsettled material scope dispute also remains incomplete. Verifier asides follow ordinary observation eligibility; admitting one as a finding requires full admission and any mandatory confirmation.

A failed premise reopens as a candidate named by `reopened_as`, never as an observation. An unresolved premise names its material question in `reopened_as` or stays outstanding. A holds ruling establishes only the cited premise under its conditions.

Collect all newly required work into at most one follow-up: admitted asides, reopened premises, changed mandatory claims, and safety premises newly required after refutations remove blockers. The initial-plus-follow-up allowance spans the review, any run continuing it from a `prior_record`, and every worker. Optional work never makes coverage incomplete.

After exhaustion, required work stays unpublished and in `outstanding`, with task id and reason. This includes failed/withheld returns, unresolved tasks without qualifying questions, and new mandatory claims. Publish already confirmed unrelated findings and disclose gaps even when a known blocker takes status precedence. No batch establishes global safety.

## Build input

`python3 scripts/build_verifier_prompt.py --example` prints the input with a batch `phase` of `initial` or `follow-up`. The builder projects allowed fields and refuses, by field, a record it cannot project; it does not decide which tasks are required. Keep stable finding IDs unchanged.

A candidate carries the survivor record's fields. Its evidence entries, and the `anchor` and any `fix` entries of `ranges`, carry decisive raw text, or `{unavailable}` naming the gap and optionally its `coordinate`; preserve the `review_context.py` range lines. A premise carries `id`, `area` (`security`, `data-integrity`, `destructive-migration`, `compatibility`, or `concurrency`), a one-line `premise` stating the fact and the conditions it holds under, and the evidence lines it rests on. The builder never derives either from private support.

Optional `test_evidence` entries are focused checks the claim relies on, at the pinned head with decisive raw output lines, or `{unavailable: "<reason>"}`. Preserve the command's test identity. Empty or omitted test evidence makes no assertion that execution ran.

Project caller check evidence only after accepting it under the rubric's Supplied checks. These fields must express the exact pinned-head input and readable raw output; otherwise use `{unavailable: "<check and reason>"}`, including historical results and dirty inputs the fields cannot express. Settle coverage, environment, and completeness before projection. Never pass caller conclusions or implementation reasoning.

Candidates and premises may additionally carry:

- `requirement_source` and `rule_source`: exact source coordinates. Put the linked issue/spec and applicable base-branch rules in `sources`, including explicit unavailable sources. For a change-description requirement, include the raw change-description entries in `sources`: both `pr-title` and `pr-body` on a pull request; the cited full commit message at `commit-<sha7>` on a local target whose requirement coordinate is `commit-<sha7>/"<quoted phrase>"`.
- `conformance`: `{coordinate, version, artifact, consumer_sites}`; the last two are nonempty evidence arrays with the pinned artifact version/delta location, artifact-side citation, and inspected consumer definitions/aliases/re-exports/conditional sites (or the search and sites that supplied nothing). Required for an `artifact-` requirement source. The builder includes the conformance verifier procedure.
- `released_compatibility`: `{coordinate, promise, scope, documentation, tests, callers, release_decision}`. The last four are nonempty evidence arrays, including unavailable inputs. Supply this for every promised released-contract candidate or premise; semantic applicability belongs to the primary. The builder includes the rubric's Released compatibility procedure.

A source entry with `unavailable` may retain its known `coordinate`; name the missing source and what could supply it. Put raw sources and scoped premises in the documented fields, not persuasion: projection drops private `support` and conclusions but never rewrites claims, and an allowlist cannot judge prose.

## Commands and artifacts

After selecting the batch, run relative to this skill root:

```sh
python3 scripts/build_verifier_prompt.py input.json --output <private-dir>/initial
```

On exit 0, send only the new bundle's `brief.md` to the selected verifier, by absolute path or exact bytes. It prints the bundle's unique ID, which the worker echoes in its inline JSON return. Retain the original private input beside the bundle. A distinct follow-up uses a distinct directory and batch ID. Never dispatch a refused build or use a stale bundle: report a non-zero exit and stop dispatch, repair the input or helper as appropriate, and rerun the build into a new path, which gets a new ID. Unrecoverable mandatory verification follows the review's incomplete-coverage rules.

Await the completed response and save it **verbatim** once to a new file, such as `<private-dir>/initial-return.json`, and pass that as `<return>`.

```sh
python3 scripts/account_verifier_return.py --bundle <private-dir>/initial --output <private-dir>/initial/accounting.json <return>
```

The report's `accounted` and `withheld` arrays partition each role's IDs; a return without this bundle's `bundle_id` answers another brief and withholds every task. Read that report once, before reconciliation. Exit 0 means only syntactic completeness; no script output assigns confirmation, safety, coverage, or review status. The raw verdict still decides whether an accounted candidate is confirmed or refuted.

On any non-zero exit, report the output and stop ordinary reconciliation. An exit-1 report allows the primary to reconcile the individually accounted records while withholding unusable records and retaining the required coverage gap; an unknown ID or invalid aside is not silently ignored. A mismatched bundle or an I/O failure may leave no report: recover that operation or treat the affected batch as unaccounted.

For structural repair, keep the raw file and write a separate repaired return, preserving supplied judgments, evidence, and asides verbatim; account that file with `--repair-of <original>` to a new report, which records the original's path and hash, and retain both identities. Repair may fix encoding only; an original without this bundle's ID withholds every task. It cannot invent an absent verdict, evidence, settling fact, or premise ruling, reclassify a premise ruling as a candidate verdict, or launch an extra worker; no encoding repair grants a batch. Additional actual verification may use only the remaining follow-up. A required gap after it is spent remains incomplete, while already verified unrelated findings remain publishable under the existing status precedence. Each batch names its `bundle` and the reconciled `accounting` report, from which the finalizer derives `raw_return`, the file that report accounted; name an original beside a repair under `record.paths`. The finalizer reads that report, or for a carried confirmation the report of the batch its `confirmed_in` record names, and refuses a task whose ruling the report does not establish.
