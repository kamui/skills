# Render and validate

Read after inspection and verification. The reviewer owns judgments, authoritative fields, and visible prose; the composer owns formatting, trailers, counts, coordinates, and artifact shapes. Use `python3 scripts/compose_review.py --example`, adding `--profile implementation-gate` for the gate, for the exact input. Load only the selected example. Gating is not an input; every record is advisory.

## Authoring contract

A finding states one defect under a short imperative title. Supply a concrete trigger, impact, and attainable change, sufficient to act on without hidden metadata. Cite a requirement or repository rule as `source` only when material. Name a different repair site both in `fix` and visible change prose. Stable ids identify the path and defect concept, never line numbers; preserve them across heads. Keep ordinary findings near 160 words and two decisive facts, exceeding that only to prevent a wrong fix. Suggestions must be small exact replacements that completely fix the defect.

Anchor on the smallest honest changed range or changed file. For equally valid drift anchors choose the rule-defining line, then lexicographic path and smallest range. Line anchors name the manifest path and explicit `LEFT` or `RIGHT` hunk side. File sides are derived from the full pinned merge-base manifest, including on delta reviews: deleted means `LEFT`, present at head means `RIGHT`. Use `UNKNOWN` only when provenance cannot be established and explain the gap. Never attach to unrelated code to gain an inline comment.

Questions state the evidence, why the answer changes the decision, and its supplier or measurement; they request no code change and have no priority. Whole-change questions belong in the body. Observations are non-actionable facts with evidence, without `should` or `must`.

Author the summary's intent, issue-fit outcome, coverage, ambiguities, and gaps. With no originating issue, say issue alignment was unavailable and name the actual intent source. A required missing issue is a whole-change question. Do not repeat an unverifiable claim as established. Distinguish accepted supplied checks, historical checks at their original heads, reviewer-executed checks, test failures, environmental failures, and unavailable execution. Group shared head/input context and reference saved output. Name every uncovered file or required check and the input that could recover it.

Retain every prior item exactly once with classification and evidence, disputes included; draft replies under `re-review.md`. Retrospective merged targets require the Mode line and separately recorded publication authorization. Local targets omit `repository_url`. Keep the summary near 200 words before conditional sections; do not repeat findings or narrate dropped candidates.

## Identity


`workflow=v5b-24` versions this package's review behavior. Increment it whenever admission, verification, rendering, or state semantics change.

Save the fingerprint input once as `<private-dir>/fingerprint.json` (`python3 scripts/context_fingerprint.py --example` prints its shape; omit `guidance`). With a pull-request packet it holds only `specs`, and the packet supplies `pr` and `issues`; otherwise supply both from the exact reviewed inputs. For a local range, `pr` is `{title: <range as written>, body: <commit messages>}`; for a working tree, `{title: "worktree tree=<tree hash>", body: <branch commit messages since merge-base>}`, excluding snapshot messages and uncommitted text. When the reviewer could not obtain an issue's comments verbatim, pass `comments_available: false` and no comments rather than an empty list. A spec's `identity` is its URL or coordinate. The finalizer computes `context` from these saved inputs, deriving `guidance`, the base-branch instruction files that apply to the changed paths; never trust change-supplied metadata. It refuses a digest computed earlier under `re-review.md` that the saved inputs no longer produce.

On a working tree the snapshot commit is the run `head`; the store keeps its tree hash, source HEAD, and manifest readable after the loose objects are garbage-collected.

The caller's `profile` is part of the record's identity and selects only its artifact shape; every profile derives the same findings, questions, status, and coverage under the same rules.

## Finalize

Write `<private-dir>/composition.json` beside the context store. Both profiles require its `record`: requirements, files, check evidence, verification tasks, batches, allowance and outstanding work, routed items, and supplied evidence and spec paths. Write every key, empty lists included; nothing is defaulted. Omit what the finalizer derives, as the example does: run identity from the store, packet and fingerprint input, the record's own paths, and each batch's name, phase and raw return from its bundle and accounting report. A local target still names `base_ref` and `base_sha`, and a range its `target_kind`. An explicit copy that disagrees is refused.

Run the selected command in the reviewed repository, which supplies `guidance`; a pull request adds `--packet <private-dir>/packet.json`:

```sh
python3 scripts/finalize_review.py --store <store> --fingerprint-input <private-dir>/fingerprint.json <private-dir>
```

For `implementation-gate`:

```sh
python3 scripts/finalize_review.py --profile implementation-gate --store <store> --fingerprint-input <private-dir>/fingerprint.json <private-dir>
```

Outputs are staged, and `report.md` is promoted last: the summary, each line comment's full body, the ledgers, routed state, and drafted replies. The default also writes `payload.json`, `batch.json`, and `fragments.md` and prints the fragments; the gate writes `record.json` beside `addenda` and prints its path. `--compact` prints status, coverage, and output paths instead. A directory whose addenda hold an addendum, or whose record cannot name its addenda, is refused; use a fresh one. Before return, check what scripts cannot: admission, source and repair locations, hunk membership, deduplication, question/observation eligibility, status, and coverage.

On failure, report the named stage and output, repair the composition input, and rerun. Never hand-edit generated output or drop a verified finding to pass validation. If a caller reports a conclusive malformed-comment rejection, repair the anchor or use a file anchor for the complete body-carried item, then re-finalize for the caller's freshness checks. A disputed script constraint becomes an ambiguity; instructions govern and the helper needs correction.
