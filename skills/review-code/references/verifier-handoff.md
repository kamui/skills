# Mechanical verifier handoff

Read when step 3 selects a verifier batch. The primary owns eligibility, relatedness, phase, and the one-initial-plus-one-follow-up cap in `SKILL.md`; these commands perform no dispatch or review judgment. Scripts and references are installed within this skill, with no audit-skill dependency.

## Build input

Write one JSON object per model-selected batch. Keep the authoritative **full candidate disposition ledger** separately as a JSON array of rows. `--ledger` reads that full ledger, not a selected copy. The builder selects the explicitly listed IDs from it and projects allowed fields; in complete-ledger mode it refuses any omitted authoritative ID. In related-acquittal mode it checks the explicit selection without determining relatedness.

```json
{
  "run": {
    "id": "<unique private review run ID>",
    "repository": "<absolute checkout path>",
    "base": "<full base SHA>",
    "head": "<full head SHA>",
    "merge_base": "<full merge-base SHA>"
  },
  "batch": {"id": "<unique batch ID within run>", "phase": "initial", "mode": "candidate-only"},
  "run_policy": "<focused-test run policy, including any tighter limits or no execution>",
  "sources": [{"coordinate": "<issue/spec or base-branch rule coordinate>", "text": "<raw source>"}],
  "candidates": [],
  "ledger_ids": []
}
```

`phase` is `initial` or `follow-up`. `mode` is `candidate-only` (nonempty candidates, no ledger rows), `complete-ledger` (the full ledger, including empty), or `related-acquittal` (the explicitly selected rows). Either ledger mode permits candidates beside its rows or no candidates. Keep stable finding IDs unchanged. The builder does not infer mode, material survivors, or which follow-up work is eligible.

Each candidate requires `id`, `kind`, `priority`, `action`, `title`, `claim`, `trigger`, `impact`, `change`, `anchor`, `evidence`, and `ranges`. Strings retain their exact content. Kinds and actions are the review record's vocabulary; priority is P0–P3. `anchor` uses the private record's object: `type: line`, `path`, positive `start_line`, `end_line`, and `side: LEFT|RIGHT|UNKNOWN`; a file anchor uses `type: file`, `path`, and optional `side`. Optional `fix` is the existing `path:line` string. `evidence` is a nonempty array of evidence objects as defined in [verifier-return.md](verifier-return.md). `ranges` maps `anchor` and, if present, `fix` to those evidence objects: preserve the `review_context.py` range lines and their coordinates, or name unavailable ranges explicitly.

Optional `test_evidence` is an array of `{command, head, exit_status, output}` for focused checks the claim relies on: strings except integer `exit_status`; `head` must equal the pinned head and `output` carries decisive raw lines. An unavailable check is `{unavailable: "<reason>"}`. Preserve the command's test identity. Empty or omitted test evidence makes no assertion that execution ran.

These are the only fields caller-supplied check evidence travels in. An item the rubric's Supplied check evidence section accepted for the reviewed state is projected into them: its check identity as `command`, the pinned head as `head`, its exit status or conclusion as `exit_status`, and its readable output as `output`. Anything else about it goes in as `{unavailable: "<reason>"}` naming the check and why it establishes nothing here — evidence retained as historical at an earlier head, a result from a dirty tree whose input state these fields cannot express, an item whose output was only an artifact reference the primary could not read. The primary settles claimed coverage, environment match, and completeness itself; the caller's coverage claims, conclusions about the code, and implementation reasoning are not projected, and the builder's refusal of `head` values other than the pinned head keeps historical evidence out of the exact-head assertion.

Each full-ledger row requires `id`, `kind`, one-line `claim`, one-word `disposition`, one-line `falsification`, and one decisive `evidence` object. Preserve any refutation basis, safety scope, and unresolved settling fact in `falsification`. Compact survivor records into this form too when supplying the complete ledger. The builder never derives a falsification reason from private support.

Candidates and ledger rows may additionally carry:

- `requirement_source` and `rule_source`: exact source coordinates. Put the linked issue/spec and applicable base-branch rules in `sources`, including explicit unavailable sources. For a change-description requirement, include the raw change-description entries in `sources`: both `pr-title` and `pr-body` on a pull request; the cited full commit message at `commit-<sha7>` on a local target whose requirement coordinate is `commit-<sha7>/"<quoted phrase>"`.
- `conformance`: `{coordinate, version, artifact, consumer_sites}`; the last two are nonempty evidence arrays with the pinned artifact version/delta location, artifact-side citation, and inspected consumer definitions/aliases/re-exports/conditional sites (or the search and sites that supplied nothing). Required for an `artifact-` requirement source. The builder includes the conformance verifier procedure.
- `released_compatibility`: `{coordinate, promise, scope, documentation, tests, callers, release_decision}`. The last four are nonempty evidence arrays, including unavailable inputs. Supply this for every promised released-contract candidate or row; semantic applicability belongs to the primary. The builder includes the rubric's Released compatibility procedure.

The builder includes the concurrency reference only for a `concurrency` or `invariant` candidate. It always includes verifier procedure, return encoding, focused-test safety bounds, and supplied run policy. A source entry with `unavailable` may retain its known `coordinate`; name the missing source and what could supply it.

Projection constructs every nested object from allowed fields. Private `support`, confidence, conclusions, and narrative argument fields are omitted; it never deletes matching words from evidence or rewrites claims. The model must put raw sources and compact scoped falsification reasons in the documented fields, not smuggle persuasion into them. An allowlist cannot judge prose.

## Commands and artifacts

After selecting the batch, run relative to this skill root:

```sh
python3 scripts/build_verifier_prompt.py input.json --ledger full-ledger.json --output <private-dir>/initial
```

On exit 0, the new bundle contains `input.json` (projected input), `brief.md`, and `manifest.json`. The manifest binds run identity, phase/mode/batch ID, exact IDs in each role, and SHA-256 identities of projected input, brief bytes, and the authoritative full ledger. Send only the generated brief and manifest to the fresh-context worker, with their absolute paths or exact bytes. Retain the original private input and full ledger beside the bundle. A distinct follow-up uses a distinct directory and batch ID. Never dispatch a refused build or use a stale bundle: report a non-zero exit and stop dispatch, repair the input or helper as appropriate, and rerun the build into a new path. Unrecoverable mandatory verification follows step 3's incomplete-coverage rules.

Save the worker's return **verbatim** as `raw-return.json` before interpretation, then run:

```sh
python3 scripts/account_verifier_return.py --bundle <private-dir>/initial --output accounting.json raw-return.json
```

On exit 0 or a readable return's exit 1, the report retains the supplied return, raw path and hash, and separate `accounted`/`withheld` ID arrays for candidates and ledger rows, plus conclusion completeness. Read that report before reconciliation. Exit 0 means only syntactic completeness; no script output assigns confirmation, safety, coverage, or review status. The raw verdict still decides whether an accounted candidate is confirmed or refuted.

On any non-zero exit, report the output and stop ordinary reconciliation. An exit-1 report allows the primary to reconcile the individually accounted records while withholding unusable records and retaining the required coverage gap; an unknown ID, invalid aside, or batch-conclusion failure is not silently ignored. A wrong manifest identity or unparseable return withholds all task roles. An unreadable/mismatched bundle or I/O failure may produce no report: recover that operation or treat the affected batch as unaccounted. Existing output files are never overwritten.

For structural repair, keep the raw file and write a separate repaired return, preserving supplied judgments, evidence, and asides verbatim; account that file to a new report and retain both raw and repaired identities. Repair may fix encoding only. It cannot invent an absent verdict, evidence, settling fact, row ruling, or clean conclusion, reclassify a ledger ruling as a candidate verdict, or launch an extra worker. Additional actual verification may use only the remaining step-3 follow-up. A required gap after it is spent remains incomplete, while already verified unrelated findings remain publishable under the existing status precedence. Keep bundle, raw return, any repair, and accounting report paths in the returned verification record.
