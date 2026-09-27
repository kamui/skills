# Render and validate

After verification, author judgments, fields, and prose; the finalizer handles presentation and artifacts. `python3 scripts/render_review.py --example` prints composition input. Records are advisory; gating is not an input.

## Authoring contract

Use one defect and a short imperative title. Supply concrete `trigger`, `impact`, and attainable `change` sentences that form one actionable paragraph; cite a material rule as `source`. The finalizer joins them without labels, preserves fenced code after the prose, and closes `consider` findings with permission to decline. Name a different repair site in both `fix` and change prose. Stable ids name path and defect, never lines; preserve across heads. Aim for 50-90 words and two decisive facts; exceed only to prevent a wrong fix. Suggestions must completely fix the defect with small exact replacements.

Anchor on the smallest honest changed range or file, never unrelated code. Break drift-anchor ties by rule-defining line, lexicographic path, then smallest range. Line anchors require manifest path and `LEFT`/`RIGHT` hunk side. File sides use the full pinned merge-base manifest even on delta reviews: deleted `LEFT`, present `RIGHT`. Use `UNKNOWN` only for unestablished provenance and explain the gap.

Questions state evidence, how the answer changes the decision, and its supplier or measurement; no requested code change or priority. Whole-change questions go in the body. Observations state evidenced non-actionable facts, without `should` or `must`.

Author intent, issue fit, concise coverage, ambiguities, and gaps. Without an issue, state alignment was unavailable and name the intent source; a required missing issue is a whole-change question. Never present unverifiable claims as established. In `summary.check_details`, distinguish accepted supplied checks, historical checks with original heads, reviewer runs, test failures, environmental failures, and unavailable execution. Group shared head/input context and link saved output. Unmet requirements need findings or questions; `coverage_gaps` names every uncovered file or required check and its recovery input.

## Identity

`workflow=v5b-30-x382` versions review behavior; increment for admission, verification, rendering, or state changes.

The run trailer carries `packet_context=` and `supplied_inputs=`. A pull request's `packet_context` is the digest `forge_packet.py` computes from the saved packet's intent, and the finalizer derives it; never write or copy one. A local target has none and its trailer reads `packet_context=none`. List the identities of the caller-supplied issues and specs in `run.specs`, empty when there were none; the finalizer derives `supplied_inputs=yes|no` from that list.

## Finalize

Write `<private-dir>/composition.json` beside the context store, with every key the example shows written, empty lists included; nothing judged is defaulted. Omit what the finalizer derives, as the example does: run identity from the store and packet, `supplied_inputs`, the record's own paths, the spent allowance, the lineage, and each batch's name, phase and raw return from its bundle and accounting report. An explicit copy that disagrees is refused. A local target also writes `run.target_kind` (`range` or `worktree`), `target` for a range as written, `base_ref`, `base_sha`, `issues` (coordinates, empty for none), and `change_description`, its real commit messages byte for byte or empty.

Run in the reviewed repository; a pull request adds `--packet <private-dir>/packet.json`, and a run from a prior record adds `--prior-record <prior record>`:

```sh
python3 scripts/render_review.py --store <store> <private-dir>
```

The finalizer writes `record.json`, `payload.json` and `batch.json`, promotes `report.md` last, and prints the status, coverage and each output's path, the report last. Before return, check what scripts cannot: admission, source and repair locations, hunk membership, deduplication, question/observation eligibility, status, and coverage.

On failure, report the named stage and output, repair the composition input, and rerun. Never hand-edit generated output or drop a verified finding to pass validation. If a caller reports a conclusive malformed-comment rejection, repair the anchor or use a file anchor for the complete body-carried item, then re-finalize for the caller's freshness checks. A disputed script constraint becomes an ambiguity; instructions govern and the helper needs correction.
