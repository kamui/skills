# Record the review

Read when your judgments are settled. You write one input file of judgments and prose. The finalizer renders every artifact from it, checks the result against the pinned context, and refuses a record that contradicts itself.

## What you author

`python3 scripts/render_review.py --example` prints the input with every key. Write them all, empty lists included, because nothing judged is defaulted. Leave out what the example leaves out: the finalizer derives run identity, paths, the spent allowance, and lineage, and refuses a copy that disagrees.

**Findings.** One defect each, under a short imperative title. `trigger`, `impact`, and `change` are separate sentences that read together as one paragraph a person could act on with nothing else open. Name the rule or requirement in `source` when one decides it. Say enough to prevent a wrong fix and stop there. A suggested replacement must fix the whole defect.

**Ids and anchors.** A stable id names the path and the defect, never a line, and survives across heads. Anchor on the smallest changed range that honestly shows the defect, or on the file when no changed line does. Never attach a finding to unrelated code to get a line comment. When the repair belongs somewhere else, name that site in `fix` and in the prose.

**Questions and observations.** A question states the evidence, how the answer changes the decision, and who or what can supply it, and asks for no code change. An observation states an evidenced fact without `should` or `must`.

**Summary.** State the intent, how the change fits its issues, what you covered, and how each check was settled. Without an issue, say alignment was unavailable and name the intent source. Every unmet requirement has a finding or a question. The example omits two optional `summary` keys. `coverage_gaps` holds one line for each unreviewed file, missing check, or unfinished verification with what would recover it, and `ambiguities` holds entries of `term`, two or more `readings`, and the reading `applied`. Keep the summary short. The finalizer leads with status and findings and collapses routine detail.

**The private record.** `record` holds the accounting behind the review: each requirement with its disposition, each changed file's state, each check, each verification task and batch, and what stays open. It is how a later run or a caller audits this one.

## Identity

`workflow=v5b-31` versions review behavior for the duplicate-review shortcut. Raise it in `render_review.py` and here whenever admission, verification, rendering, or prior-state rules change. List caller-supplied issues and specs in `run.specs`. The finalizer derives the rest of the run trailer.

## Finalize

Write `<private-dir>/composition.json` beside the context store and run this in the reviewed repository. A pull request adds `--packet <private-dir>/packet.json`, and a run from a prior record adds `--prior-record <prior record>`.

```sh
python3 scripts/render_review.py --store <store> <private-dir>
```

Success prints the status, coverage, and each artifact's path, `report.md` last. A refusal names its stage, location, and rule. Repair the composition and rerun. Never edit generated output, and never drop a verified finding to get past validation. If a refusal contradicts these instructions, record an ambiguity and keep the judgment. When a publisher reports that the forge rejected a comment as malformed, repair that item's anchor or give it a file anchor, then finalize again.

The finalizer checks consistency, not truth. Before you return, reread the report for what it cannot check: that each finding clears the rubric, each cited line says what you claim, and the status follows from the evidence.
