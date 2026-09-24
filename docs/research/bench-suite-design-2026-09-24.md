# Design: a rerunnable reviewer benchmark suite (`bench/`)

**Status: §8 steps 1–4 implemented in [`bench/`](../../bench/README.md): mirrors rebuilt and
verified, dependency caches built and archived with hashes, smoke checks measured on the suite
machine (`provision.py`); the toy run of step 5 and the fresh targets of step 6 remain.**
Written 2026-09-24 after the first-draft proposal was reviewed by a Codex reviewer (`gpt-6-astra`,
reasoning `high`); the review is
[`builtin-review-benchmark-2026-09-24/review-2.md`](builtin-review-benchmark-2026-09-24/review-2.md)
and §9 records the disposition of every item. This design supersedes the layout of
[`builtin-review-benchmark-2026-09-24/`](builtin-review-benchmark-2026-09-24/README.md), whose
tools and fixtures migrate here (§8).

## 1. Why

The benchmark will be rerun whenever a new model ships, whenever Claude Code or Codex change
their built-in reviewers, and whenever `review-code` changes. The current layout cannot support
that: the mechanism, the truth, and one experiment's narrative sit in a dated research bundle;
target definitions are shell fragments quoted in prose; registers are markdown; packets and
mirrors live outside the repository; results are hand-pasted rows. A rerun rebuilds by hand and
compares by reading.

The design separates three things that change on different clocks and adds the one thing the
first draft lacked: an explicit **comparison contract** that says which revisions two runs must
share to be compared, and which differences are declared dimensions rather than confounds.

## 2. Layout

```
bench/
  README.md                  how to provision, run, score, compare
  schema/                    JSON Schemas, one file per manifest kind, each with a schema_version
  rates.json                 dated price evidence per model (input, output, cache read, cache write, source URL)
  harness/                   observed built-in prompt hashes per CLI version (Claude Code, Codex)
  rubric/scoring.v<N>.md     the scoring rubric, versioned; score.py names the version it applies
  targets/<id>/
    target.json              identity, pins, shape, dates, provisioning, exposure history
    packet.md                frozen forge facts at the cutoff; original bytes; hash in target.json
    register.v<N>.json       sealed truth, one file per version; IDs never renumber
    smoke.json               base/head provisioning and smoke-check outcomes at freeze
  arms/<id>.json             reviewer configuration as data
  tools/                     provision.py, run_cell.py, attempt_audit.py, normalize_review.py,
                             codex_usage.py, transcript_usage.py, build_packet.py, score.py, compare.py
  runs/<date>-<label>/
    manifest.json            resolved arms, cohort, planned cells, rates, method and rubric revisions
    attempts/<attempt-id>/   attempt.json + small artifacts (normalized, usage, timing, audit, native payload)
    scoring/<target>/mapping.v<M>.json   adjudicator assignments, bound to register and rubric hashes
    results.v<M>.json        computed metrics, denominators, both views, exclusions
docs/research/<dated>/       narrative only: hypothesis, freeze, deviations, evaluation, pointing at a run
```

Mirrors, dependency caches, and transcripts never enter the repository. They live in a cache
root outside it (`~/.t3/bench-cache/`) with their identities and archive hashes recorded in the
manifests, so a later machine can verify what it restored.

## 3. Suite manifests

**`target.json`.** `id`, `schema_version`; `repo`, `pr`, `head`, `merge_base`, `base_sha` (the
PR's recorded base, kept separate from the computed merge-base), `base_ref_name` (upstream name,
e.g. `master`), `local_base_branch` (always `main`, §6), `negative_shas` with the reason each is
excluded, `cutoff`, `diff_manifest_sha256` (the changed-file list with per-file blob hashes, so a
rebuilt mirror is checked against the frozen diff identity), `packet_sha256`; `shape`, `domain`,
`language`; `merged_at`, `fix_published_at`, `originating_issue`; `provisioning` (recipe, resolved
dependency identities such as lockfile hashes and cache archive hashes, toolchain and platform
record, focused-command allowance, what is unavailable); `exposure` (when the target entered the
suite, which runs and skill-development work used it, when its register was published);
`current_register` version.

**`packet.md`** is the factual forge state at the cutoff: title, body, commits, reviews and
comments up to the cutoff, with the omissions reported. It carries **no run policy**: no
execution note, no worker model, no report instructions, no experiment label. Those were baked
into the #137 packets and would restore the very intervention the current benchmark removed; the
run supplies policy separately (§5). The #137 packets are preserved byte-for-byte with their
hashes as `packet.legacy.md` and a derived factual `packet.md` is built and hashed once.

**`register.v<N>.json`.** `target`, `version`, `sealed_at`, `sealed_by` (adjudicator configuration:
person or model, effort, tools, evidence access), `supersedes`; `defects[]` with `id` (stable across
versions), `title`, `trigger`, `consequence`, `required_outcome`, `evidence[]`, `demonstration`
(the reproduction performed), `added_in_version`; `non_defects[]` (plausible claims adjudicated
false, with reasoning, so a later scorer can classify a repeated claim consistently); `clean_basis`
for a clean target. A new version adds defects or non-defects and never renumbers; the old file
stays.

**`arm.json`.** `id`, `kind` (`review-code`, `claude-builtin`, `codex`), `model`, `effort`,
`requested_workers` (model and effort for sub-agents or verifiers), `skill_tree` (a tree hash, or
`current`, which `run_cell.py` resolves to a hash at run start and freezes in the manifest),
`isolation` (fresh home, safe mode, allowed tools, sandbox mode, network off), `adapter`
(transport for the range and the packet, output capture rule), `budget_usd_per_attempt`. Nothing
in an arm file is "as observed"; observations go in `attempt.json`.

## 4. Run manifests

**`manifest.json`.** `run_id`, `created_at`, `method_revision` (commit of the one-shot method),
`rubric_version`, `schema_versions`; `arms[]` as resolved: the arm file hash, the resolved skill
tree, the CLI versions observed at a pre-dispatch probe, the built-in prompt hashes expected;
`cohort` (the frozen list of target IDs with their register versions; exclusions with reasons);
`planned_cells[]` (`target`, `arm`, `replicate`), `caps` (attempts, replacements, spend, reserve,
concurrency), `sealed_order`, `rates` (the `rates.json` entries used, by date), `execution_policy`
(the allowance text given to every arm, and per-target availability). A change to any resolved
field after the first dispatch invalidates the affected cells; the manifest is append-only after
that point and drift is recorded as a deviation with the cells it invalidates.

**`attempt.json`.** `attempt_id` (never reused), `cell`, `predecessor`, `retry_reason`,
`continuity` (`fresh` or `resumed from <attempt>`), `dispatched_at`; `observed` (harness and CLI
version, model per request from transcripts, effort, built-in prompt hash and header line,
skill tree, executed diff commands, sandbox, tree identity before and after); `phase_reached`,
`disposition` (`valid completed`, `stopped: <reason>`, `harness-invalid: <reason>`,
`skill failure`), `arm_reported_complete`; `audit` (violations, guidance probes, network commands);
`usage` (per-request records with model, cache tier and service tier, plus the priced total and
its bounds); `timing` (§7); `native_payload` path and hash; `normalized` path, `parse_status`
(`parsed`, `empty`, `unresolved` with the reason); `transcript_archive` (path outside the repo,
SHA-256, restoration check result).

**`mapping.v<M>.json`.** `attempt_id`, `register` (target, version, file hash), `rubric_version`,
`scored_by` (adjudicator configuration), `blind_token`; `items[]` keyed by stable item ID with
`assignment` (`defect:<id>`, `false-finding`, `non-material`, `unresolved`), `duplicate_group`,
`fix_sufficiency` (`sufficient`, `partial`, `absent`, `n/a`) for recoveries, `priority_error`,
`notes`; `review_level` (`native_verdict`, `approved_on_buggy`, `zero_recovery`, `false_clean`,
`completion`). Unavailable is distinct from zero everywhere.

**`results.v<M>.json`.** For each `(target, arm)`: attempts included, cells unattempted, cells
harness-invalid, replacements used; recall in **attempt-level** and **completed-only** views;
raw and unique false findings; approved-on-buggy and zero-recovery counts, kept apart; fix
sufficiency; priority and rank errors; noise; contemporaneous cost, common-rate repriced cost, and
quota consumed, each labelled; elapsed to payload and to completion. Per-shape and per-cohort
(regression versus fresh) tables. The file names the mapping versions and register versions it
was computed from.

## 5. Run policy and isolation

Run policy is a per-run document rendered from the manifest and given identically to every arm
alongside the packet: the local branch layout (`main` at the merge-base, `review-head` at the
head), the execution allowance, what is unavailable, and nothing about how to review.

Reviewers run on the same machine as the suite, so the suite's plaintext registers, other
attempts, and the repository history are readable unless something prevents it. Three controls,
in strength order, and the manifest records which applied:

1. **Export, not checkout.** Each attempt's working set is an export directory holding only the
   clone, the packet, the run policy, and the fresh home; the reviewer's working directory is
   inside it. Nothing from `bench/` is mounted or copied in.
2. **Read audit with relative paths resolved.** `attempt_audit.py` resolves every path against the
   command's working directory and flags any that escapes the export, including `..` escapes and
   `~` expansion; it verifies that the built-in's guidance probes hit nothing. The first draft's
   audit missed relative paths (review M1) and is fixed as part of migration.
3. **Enforced sandbox.** A dedicated unprivileged user (`bench`) that owns the export and cache
   roots and has no read access to the maintainer's home or the repository checkout; the wrapper
   runs reviewers as that user. This is the only control that makes contamination impossible
   rather than detectable, and it is a one-time setup step; a run that lacks it says so.

Network is off for every arm (no web tools, sandbox network disabled, and any network command in
the audit is a violation). Registers for fresh targets stay encrypted until first scoring.

## 6. Comparison contract

Two runs are comparable on a target when they share the target's `packet_sha256`,
`diff_manifest_sha256`, register version (or the later run's mapping has been re-adjudicated
against the earlier version's defects, §7), rubric version, metric code revision, execution
policy, and provisioning identity. Every other difference is a **declared dimension** that the
comparison names: product version (harness, CLI, prompt hash), model, effort, skill tree, rates,
adjudicator configuration. A product-version delta is reported as a product-version delta, never
as an isolated model or skill effect.

The cohort is frozen per run. `compare.py` never silently intersects: it takes the intended cohort,
reports which targets are missing from which run and why, and labels any subset analysis as such.
Costs are shown contemporaneous and common-rate repriced side by side, with quota separate.

## 7. Scoring, register revisions, and timing

**Rubric.** `bench/rubric/scoring.v<N>.md` states the definitions once: material defect, false
finding including unsupported assertions, duplicate grouping, fix sufficiency, false clean
(approved on a buggy target) versus zero recovery, priority and rank errors, noise. The #137
evaluation and the 2026-09-24 draft disagreed on false clean (review M6); version 1 of the rubric
carries both counts as separate columns so neither history is rewritten.

**Register revisions.** Adding a defect changes judgments, not just arithmetic: items previously
mapped `non-material` or `false-finding` may be recoveries of the new defect. When a register gains
a version, every historical attempt on that target gets a **blind re-adjudication for the new
defect only**, producing a new mapping version; the old mapping and results stay, and the
comparison names which mapping version it used. Target (n)'s history is the worked example: its
version 1 (clean) and version 2 (GT-n1) both migrate, with the adjudication ruling as evidence.

**Timing.** Four events, in order: `dispatched_at`, `payload_validated_at` (the arm's own validator
for `review-code`; successful normalization for the built-ins, which therefore runs inside the
wrapper before completion is declared), `completed_at` (written only on a valid completed
attempt), and `stopped_at` in the attempt record for every other outcome. The current wrapper
writes completion on any exit and stamps validation afterwards (review M8); migration fixes both.

**Parsing.** An output that lacks the arm's expected markers is `unresolved`, not an empty review;
the authoritative final response is selected by session and role, not "last text seen"; fixtures
cover clean, incomplete, malformed and multi-worker outputs.

## 8. Migration

1. Create `bench/` with the schemas, the rubric v1, `rates.json` seeded from the dated evidence
   already recorded, and `harness/` seeded with the two Claude Code 2.1.281 prompt hashes.
2. Move `dispatch.sh` (under its own name until `run_cell.py` replaces it), `attempt_audit.py`,
   `normalize_review.py`, `codex_usage.py`, `transcript_usage.py`, and `build_packet.py` into
   `bench/tools/`, keeping their provenance checks, replay support, request deduplication,
   cache-tier bounds, native output retention and blind rendering; update links in the research
   docs that cite them. Apply the three defect fixes from the review: relative-path audit, timing
   semantics, unresolved parsing.
3. Convert the six #137 targets: `target.json` from the shell fragments and README tables;
   `packet.legacy.md` preserved with the recorded hash and a factual `packet.md` derived from it;
   `register.v1.json` from each prose register, and `register.v2.json` for (n); `smoke.json` from
   the recorded provisioning outcomes where they exist, otherwise re-measured at rebuild.
4. Rebuild mirrors and caches into the cache root, verify negative SHAs and diff identities,
   archive the caches with hashes.
5. File the toy fixtures as `bench/runs/2026-09-24-toy/` with attempt manifests, and rewrite the
   2026-09-24 README as the narrative for the first real run, pointing at its future run
   directory.
6. Only then add the four fresh targets and freeze the first run.

## 9. Disposition of the second review

| # | Finding | Disposition |
| --- | --- | --- |
| M1 | reviewers can read plaintext registers; the audit misses relative paths | accepted: export-not-checkout, relative-path audit, unprivileged user (§5) |
| M2 | #137 packets embed run policy and the old base branch name | accepted: legacy packets preserved, factual packets derived, policy per run (§3, §5) |
| M3 | attempt and results manifests lack cell accounting and denominators | accepted: §4 |
| M4 | `current` and "observed" versions let one arm label cover different executions | accepted: resolved at run start, frozen in the manifest, hashes link every artifact (§3, §4) |
| M5 | a provisioning recipe is not deterministic execution | accepted: dependency identities, cache archives, smoke outcomes, availability as a declared dimension (§3, §6) |
| M6 | the scoring schema cannot express the method's metrics; false-clean definitions conflict | accepted: versioned rubric, richer mapping, both false-clean columns (§7) |
| M7 | register updates need judgment updates, not arithmetic rescoring | accepted: blind re-adjudication per new defect, mapping versions (§7) |
| M8 | wrapper timing semantics are wrong | accepted: four events, completion only on success, normalization inside the wrapper (§7) |
| S1 | separate price drift from efficiency | accepted: contemporaneous and common-rate costs side by side, quota apart (§6) |
| S2 | transcripts need an archival contract | accepted: hashed archives with restoration checks (§4) |
| S3 | unknown output formats parse as empty reviews | accepted: `unresolved` status, authoritative-response selection, fixtures (§7) |
| S4 | track benchmark exposure, not just age | accepted: `exposure` in `target.json`, cohorts reported apart (§3, §4) |
| D1 | "same targets, register, metric code" is insufficient | accepted: the comparison contract with declared dimensions (§6) |
| D2 | automatic intersection changes the question | accepted: frozen cohort, missingness reported, subset analyses labelled (§6) |
| D3 | "five small scripts" understates the work | accepted: §8 lists what is kept and the scope; no size claim is made |
