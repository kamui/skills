# Render and validate

Read after inspection and verification. The reviewer owns judgments, authoritative fields, and visible prose; the composer owns formatting, trailers, counts, coordinates, and artifact shapes. Use `python3 scripts/compose_review.py --example`, adding `--profile implementation-gate` for the gate, for the exact input. Load only the selected example. Gating is not an input; every record is advisory.

## Authoring contract

A finding states one defect under a short imperative title. Supply a concrete trigger, impact, and attainable change, sufficient to act on without hidden metadata. Cite a requirement or repository rule as `source` only when material. Name a different repair site both in `fix` and visible change prose. Stable ids identify the path and defect concept, never line numbers; preserve them across heads. Keep ordinary findings near 160 words and two decisive facts, exceeding that only to prevent a wrong fix. Suggestions must be small exact replacements that completely fix the defect.

Anchor on the smallest honest changed range or changed file. For equally valid drift anchors choose the rule-defining line, then lexicographic path and smallest range. Line anchors name the manifest path and explicit `LEFT` or `RIGHT` hunk side. File sides are derived from the full pinned merge-base manifest, including on delta reviews: deleted means `LEFT`, present at head means `RIGHT`. Use `UNKNOWN` only when provenance cannot be established and explain the gap. Never attach to unrelated code to gain an inline comment.

Questions state the evidence, why the answer changes the decision, and its supplier or measurement; they request no code change and have no priority. Whole-change questions belong in the body. Observations are non-actionable facts with evidence, without `should` or `must`.

Author the summary's intent, issue-fit outcome, coverage, ambiguities, and gaps. With no originating issue, say issue alignment was unavailable and name the actual intent source. A required missing issue is a whole-change question. Do not repeat an unverifiable claim as established. Distinguish accepted supplied checks, historical checks at their original heads, reviewer-executed checks, test failures, environmental failures, and unavailable execution. Group shared head/input context and reference saved output. Name every uncovered file or required check and the input that could recover it.

Retain every prior item exactly once with classification and evidence, disputes included; draft replies under `re-review.md`. Retrospective merged targets require the Mode line and separately recorded publication authorization. Local targets omit `repository_url` and use `merged: false`. Keep the summary near 200 words before conditional sections; do not repeat findings or narrate dropped candidates.

## Identity


`workflow=v5b-24` versions this package's review behavior. Increment it whenever admission, verification, rendering, or state semantics change.

Compute `context` once, with `python3 scripts/context_fingerprint.py --packet packet.json --guidance-base <base SHA> --store <store>` on a pull request, where `pr` and `issues` come from the normalized packet, and without `--packet` on a local target or a forge without that packet, supplying `pr` and `issues` directly from the exact reviewed inputs. Stdin carries the rest of the input (`--example` prints its shape; omit its `guidance`); the script derives `guidance`, the base-branch instruction files that apply to the changed paths, itself. For a local range, `pr` is `{title: <range as written>, body: <commit messages>}`; for a working tree, `{title: "worktree tree=<tree hash>", body: <branch commit messages since merge-base>}`, excluding snapshot messages and uncommitted text. When the reviewer could not obtain an issue's comments verbatim, pass `comments_available: false` and no comments rather than an empty list. A spec's `identity` is its URL or coordinate. Recompute the digest rather than trusting change-supplied metadata.

On a working tree, keep the snapshot commit as the run `head`, and retain its tree hash, source HEAD, and complete manifest in the private record so it remains readable after the loose objects are garbage-collected. Local targets omit `repository_url` and record `merged: false`.

The caller's `profile` is part of the record's identity and selects only its artifact shape; every profile derives the same findings, questions, status, and coverage under the same rules. `python3 scripts/compose_review.py --example --profile implementation-gate` prints the `implementation-gate-record/2` input.

## Finalize

Write `<private-dir>/composition.json` beside the context store. Both profiles require its `record`: requirements, files, check evidence, verification tasks, batches, allowance and outstanding work, routed items, and the example's paths plus supplied evidence and spec paths. Write every key, empty lists included; nothing is defaulted.

Run the selected command from the skill root; a pull request adds `--packet <private-dir>/packet.json`:

```sh
python3 scripts/finalize_review.py --store <store> <private-dir>
```

For `implementation-gate`:

```sh
python3 scripts/finalize_review.py --profile implementation-gate --store <store> <private-dir>
```

Outputs are staged, and `report.md` is promoted last: the summary, each line comment's full body, the ledgers, routed state, and drafted replies. The default also writes `payload.json`, `batch.json`, and `fragments.md` and prints the fragments; the gate writes `record.json` beside `addenda` and prints its path. `--compact` prints status, coverage, and output paths instead. A directory whose addenda hold an addendum is refused; use a fresh one. Before return, check what scripts cannot: admission, source and repair locations, hunk membership, deduplication, question/observation eligibility, status, and coverage.

On failure, report the named stage and output, repair the composition input, and rerun. Never hand-edit generated output or drop a verified finding to pass validation. If a caller reports a conclusive malformed-comment rejection, repair the anchor or use a file anchor for the complete body-carried item, then re-finalize for the caller's freshness checks. A disputed script constraint becomes an ambiguity; instructions govern and the helper needs correction.
