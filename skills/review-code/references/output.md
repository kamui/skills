# Render and validate

Read after inspection and verification. The reviewer owns judgments, authoritative fields, and visible prose; the finalizer owns formatting, trailers, counts, coordinates, and artifact shapes. `python3 scripts/render_review.py --example` prints a pull request's composition input exactly. Gating is not an input; every record is advisory.

## Authoring contract

A finding states one defect under a short imperative title. Supply a concrete trigger, impact, and attainable change, sufficient to act on without hidden metadata. Cite a requirement or repository rule as `source` only when material. Name a different repair site both in `fix` and visible change prose. Stable ids identify the path and defect concept, never line numbers; preserve them across heads. Keep ordinary findings near 160 words and two decisive facts, exceeding that only to prevent a wrong fix. Suggestions must be small exact replacements that completely fix the defect.

Anchor on the smallest honest changed range or changed file. For equally valid drift anchors choose the rule-defining line, then lexicographic path and smallest range. Line anchors name the manifest path and explicit `LEFT` or `RIGHT` hunk side. File sides are derived from the full pinned merge-base manifest, including on delta reviews: deleted means `LEFT`, present at head means `RIGHT`. Use `UNKNOWN` only when provenance cannot be established and explain the gap. Never attach to unrelated code to gain an inline comment.

Questions state the evidence, why the answer changes the decision, and its supplier or measurement; they request no code change and have no priority. Whole-change questions belong in the body. Observations are non-actionable facts with evidence, without `should` or `must`.

Author the summary's intent, issue-fit outcome, coverage, ambiguities, and gaps. With no originating issue, say issue alignment was unavailable and name the actual intent source. A required missing issue is a whole-change question. Do not repeat an unverifiable claim as established. Distinguish accepted supplied checks, historical checks at their original heads, reviewer-executed checks, test failures, environmental failures, and unavailable execution. Group shared head/input context and reference saved output. Name every uncovered file or required check and the input that could recover it.

Retain every prior item exactly once with classification and evidence, disputes included; draft replies under `prior-state.md`. A merged target renders the retrospective Mode line; whether it publishes is `review-code-publish`'s decision. Keep the summary near 200 words before conditional sections; do not repeat findings or narrate dropped candidates.

## Identity

`workflow=v5b-26-x382-x383` versions this package's review behavior. Increment it whenever admission, verification, rendering, or state semantics change.

The run trailer carries `packet_context=` and `supplied_inputs=`. A pull request's `packet_context` is the digest `forge_packet.py` computes from the saved packet's intent, and the finalizer derives it; never write or copy one. A local target has none and its trailer reads `packet_context=none`. List the identities of the caller-supplied issues and specs in `run.specs`, empty when there were none; the finalizer derives `supplied_inputs=yes|no` from that list.

## Finalize

Write `<private-dir>/composition.json` beside the context store, with every key the example shows written, empty lists included; nothing judged is defaulted. Omit what the finalizer derives, as the example does: run identity from the store and packet, `supplied_inputs`, the record's own paths, the spent allowance, the lineage, and each batch's name, phase and raw return from its bundle and accounting report. An explicit copy that disagrees is refused. A local target also writes `run.target_kind` (`range` or `worktree`), `target` for a range as written, `base_ref`, `base_sha`, `issues` (coordinates, empty for none), and `change_description`, its real commit messages byte for byte or empty.

Run in the reviewed repository; a pull request adds `--packet <private-dir>/packet.json`, and a run from a prior record adds `--prior-record <prior record>`:

```sh
python3 scripts/render_review.py --store <store> <private-dir>
```

The finalizer writes `record.json`, `payload.json` and `batch.json`, promotes `report.md` last, and prints the status, coverage and each output's path, the report last. Before return, check what scripts cannot: admission, source and repair locations, hunk membership, deduplication, question/observation eligibility, status, and coverage.

On failure, report the named stage and output, repair the composition input, and rerun. Never hand-edit generated output or drop a verified finding to pass validation. If a caller reports a conclusive malformed-comment rejection, repair the anchor or use a file anchor for the complete body-carried item, then re-finalize for the caller's freshness checks. A disputed script constraint becomes an ambiguity; instructions govern and the helper needs correction.
