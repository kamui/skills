# Design: a rerunnable reviewer benchmark suite (`bench/`)

**Status: §8 steps 1 to 5 are implemented in [`bench/`](https://github.com/kamui/code-review-bench/blob/main/bench/README.md). The #137 targets are
migrated. The mirrors and dependency caches are rebuilt and verified. The arms are written as data.
`file_attempt.py` filed the shakedown as the run `bench/runs/2026-09-24-toy/`. Step 6 added the
runner `run_cell.py`, the scorer `score.py`, and the comparer `compare.py`. It also added the four
fresh targets with sealed registers and the first frozen run, `bench/runs/2026-09-24-builtin-baseline/`,
which awaits dispatch.**

This design was written on 2026-09-24, after a Codex reviewer reviewed the first-draft proposal.
The reviewer was `gpt-6-astra` with reasoning `high`. The review is
[`builtin-review-benchmark-2026-09-24/review-2.md`](builtin-review-benchmark-2026-09-24/review-2.md),
and §9 records the disposition of every item. This design supersedes the layout of
[`builtin-review-benchmark-2026-09-24/`](builtin-review-benchmark-2026-09-24/README.md). That
bundle's tools and fixtures migrate here, as §8 describes.

## 1. Why

The benchmark needs a rerun whenever a new model ships, whenever Claude Code or Codex change their
built-in reviewers, and whenever `review-code` changes. The current layout cannot support that.
The mechanism, the truth, and one experiment's narrative sit in a dated research bundle. Target
definitions are shell fragments quoted in prose. Registers are markdown. Packets and mirrors live
outside the repository. Results are rows pasted by hand. A rerun has to rebuild everything by hand
and compare results by reading them.

The design separates three things that change on different schedules. It also adds the one thing
the first draft lacked, an explicit **comparison contract**. The contract says which revisions two
runs must share before they can be compared. It also says which differences are declared
dimensions rather than confounds.

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

Mirrors, dependency caches, and transcripts never enter the repository. They live in a cache root
outside it, `~/.t3/bench-cache/`. The manifests record their identities and archive hashes, so a
later machine can verify what it restored.

## 3. Suite manifests

**`target.json`.** The file holds `id` and `schema_version`. It holds `repo`, `pr`, `head`,
`merge_base`, and `base_sha`. `base_sha` is the PR's recorded base, and the file keeps it separate
from the computed merge-base. `base_ref_name` is the upstream name, for example `master`.
`local_base_branch` is always `main`, per §6. `negative_shas` lists the excluded SHAs with the
reason for each exclusion. The file also holds `cutoff`, `diff_manifest_sha256`, and
`packet_sha256`. `diff_manifest_sha256` covers the changed-file list with per-file blob hashes, so
a rebuilt mirror can be checked against the frozen diff identity. The file records `shape`,
`domain`, and `language`, and also `merged_at`, `fix_published_at`, and `originating_issue`.
`provisioning` holds the recipe, the resolved dependency identities such as lockfile hashes and
cache archive hashes, the toolchain and platform record, the focused-command allowance, and what is
unavailable. `exposure` records when the target entered the suite, which runs and
skill-development work used it, and when its register was published. Last, the file names the
`current_register` version.

**`packet.md`** is the factual forge state at the cutoff. It holds the title, the body, the
commits, and the reviews and comments up to the cutoff, and it reports the omissions. It carries
**no run policy**. It has no execution note, no worker model, no report instructions, and no
experiment label. The #137 packets included those, and they would restore the very intervention
that the current benchmark removed. The run supplies policy separately, as §5 describes. The #137
packets are preserved byte-for-byte with their hashes as `packet.legacy.md`. A derived factual
`packet.md` is built and hashed once.

**`register.v<N>.json`.** The file holds `target`, `version`, `sealed_at`, `sealed_by`, and
`supersedes`. `sealed_by` is the adjudicator configuration, which covers person or model, effort,
tools, and evidence access. `defects[]` lists each defect with an `id` that stays stable across
versions, plus `title`, `trigger`, `consequence`, `required_outcome`, `evidence[]`,
`demonstration`, and `added_in_version`. `demonstration` is the reproduction that was performed.
`non_defects[]` lists plausible claims adjudicated false, with reasoning, so a later scorer can
classify a repeated claim consistently. A clean target has `clean_basis`. A new version adds
defects or non-defects and never renumbers. The old file stays.

**`arm.json`.** The file holds `id`, `kind`, `model`, `effort`, `requested_workers`, `skill_tree`,
`isolation`, `adapter`, and `budget_usd_per_attempt`. `kind` is `review-code`, `claude-builtin`,
or `codex`. `requested_workers` gives the model and effort for sub-agents or verifiers.
`skill_tree` is a tree hash or `current`. `run_cell.py` resolves `current` to a hash at run start
and freezes that hash in the manifest. `isolation` covers a fresh home, safe mode, allowed tools,
sandbox mode, and network off. `adapter` sets the transport for the range and the packet, and the
output capture rule. Nothing in an arm file is "as observed". Observations go in `attempt.json`.

## 4. Run manifests

**`manifest.json`.** The file holds `run_id`, `created_at`, `method_revision`, `rubric_version`,
and `schema_versions`. `method_revision` is the commit of the one-shot method. `arms[]` lists each
arm as resolved, with the arm file hash, the resolved skill tree, the CLI versions observed at a
pre-dispatch probe, and the expected built-in prompt hashes. `cohort` is the frozen list of target
IDs with their register versions, plus the exclusions with reasons. `planned_cells[]` lists cells
by `target`, `arm`, and `replicate`. `caps` sets limits on attempts, replacements, spend, reserve,
and concurrency. The file also holds `sealed_order`. `rates` holds the `rates.json` entries used,
by date. `execution_policy` holds the allowance text given to every arm and the per-target
availability. After the first dispatch, a change to any resolved field invalidates the affected
cells. From that point on the manifest is append-only, and any drift is recorded as a deviation
with the cells it invalidates.

**`attempt.json`.** `attempt_id` is never reused. The file also holds `cell`, `predecessor`,
`retry_reason`, `continuity`, and `dispatched_at`. `continuity` is `fresh` or
`resumed from <attempt>`. `observed` records the harness and CLI version, the model per request
from transcripts, the effort, the built-in prompt hash and header line, the skill tree, the
executed diff commands, the sandbox, and the tree identity before and after. The file records
`phase_reached` and `disposition`. `disposition` is `valid completed`, `stopped: <reason>`,
`harness-invalid: <reason>`, or `skill failure`. The file also records `arm_reported_complete`.
`audit` lists violations, guidance probes, and network commands. `usage` holds per-request records
with model, cache tier and service tier, plus the priced total and its bounds. `timing` follows
§7. The file holds the `native_payload` path and hash, and the `normalized` path. `parse_status`
is `parsed`, `empty`, or `unresolved` with the reason. `transcript_archive` holds the path outside
the repo, the SHA-256, and the result of the restoration check.

**`mapping.v<M>.json`.** The file holds `attempt_id`, `register`, `rubric_version`, `scored_by`,
and `blind_token`. `register` names the target, the version, and the file hash. `scored_by` is the
adjudicator configuration. `items[]` is keyed by stable item ID. Each item has `assignment`,
`duplicate_group`, `fix_sufficiency`, `priority_error`, and `notes`. `assignment` is
`defect:<id>`, `false-finding`, `non-material`, or `unresolved`. `fix_sufficiency` applies to
recoveries and is `sufficient`, `partial`, `absent`, or `n/a`. `review_level` holds
`native_verdict`, `approved_on_buggy`, `zero_recovery`, `false_clean`, and `completion`.
Everywhere in these files, unavailable is distinct from zero.

**`results.v<M>.json`.** For each `(target, arm)`, the file reports the attempts included, the
cells unattempted, the cells that were harness-invalid, and the replacements used. It reports
recall in an **attempt-level** view and a **completed-only** view. It reports raw and unique false
findings. It reports approved-on-buggy and zero-recovery counts and keeps them apart. It reports
fix sufficiency, priority and rank errors, and noise. It reports contemporaneous cost, common-rate
repriced cost, and quota consumed, and labels each one. It reports the elapsed time to payload and
to completion. It has per-shape and per-cohort tables, where the cohorts are regression and fresh.
The file names the mapping versions and register versions it was computed from.

## 5. Run policy and isolation

Run policy is a per-run document. It is rendered from the manifest and given identically to every
arm alongside the packet. It states the local branch layout, with `main` at the merge-base and
`review-head` at the head. It states the execution allowance and what is unavailable. It says
nothing about how to review.

Reviewers run on the same machine as the suite. The suite's plaintext registers, other attempts,
and the repository history are therefore readable unless something prevents it. The design has
three controls, listed in order of strength, and the manifest records which ones applied:

1. **Export, not checkout.** Each attempt's working set is an export directory. It holds only the
   clone, the packet, the run policy, and the fresh home. The reviewer's working directory is
   inside it. Nothing from `bench/` is mounted or copied in.
2. **Read audit with relative paths resolved.** `attempt_audit.py` resolves every path against the
   command's working directory. It flags any path that escapes the export, including `..` escapes
   and `~` expansion. It verifies that the built-in's guidance probes hit nothing. Review item M1
   found that the first draft's audit missed relative paths, and the migration fixes that.
3. **Enforced sandbox.** A dedicated unprivileged user, `bench`, owns the export and cache roots.
   That user has no read access to the maintainer's home or the repository checkout. The wrapper
   runs reviewers as that user. This is the only control that makes contamination impossible
   rather than detectable. It is a one-time setup step. A run that lacks it says so.

Network is off for every arm. The arms get no web tools, the sandbox disables the network, and the
audit treats any network command as a violation. Registers for fresh targets stay encrypted until
first scoring.

## 6. Comparison contract

Two runs are comparable on a target when they share all of the following: the target's
`packet_sha256`, the `diff_manifest_sha256`, the register version, the rubric version, the metric
code revision, the execution policy, and the provisioning identity. The register version may
differ if the later run's mapping has been re-adjudicated against the earlier version's defects,
as §7 describes. Every other difference is a **declared dimension** that the comparison names. The
declared dimensions are the product version, meaning the harness, the CLI, and the prompt hash, and
also the model, effort, skill tree, rates, and adjudicator configuration. The comparison reports a
product-version delta as a product-version delta, never as an isolated model or skill effect.

The cohort is frozen per run. `compare.py` never silently intersects cohorts. It takes the
intended cohort and reports which targets are missing from which run and why. It labels any subset
analysis as a subset analysis. It shows contemporaneous costs and common-rate repriced costs side
by side, and it shows quota separately.

## 7. Scoring, register revisions, and timing

**Rubric.** `bench/rubric/scoring.v<N>.md` states each definition once. It defines material
defect, false finding including unsupported assertions, duplicate grouping, fix sufficiency, false
clean versus zero recovery, priority and rank errors, and noise. False clean means approved on a
buggy target. The #137 evaluation and the 2026-09-24 draft disagreed on false clean, as review
item M6 noted. Version 1 of the rubric carries both counts as separate columns, so neither history
is rewritten.

**Register revisions.** Adding a defect changes judgments as well as arithmetic. Items previously
mapped `non-material` or `false-finding` may be recoveries of the new defect. When a register
gains a version, every historical attempt on that target gets a **blind re-adjudication for the
new defect only**. That re-adjudication produces a new mapping version. The old mapping and results
stay, and the comparison names which mapping version it used. Target (n)'s history is the worked
example. Its version 1, which is clean, and its version 2, which has GT-n1, both migrate, with the
adjudication ruling as evidence.

**Timing.** The suite records four events, in order. The first is `dispatched_at`. The second is
`payload_validated_at`. For `review-code`, the arm's own validator sets it. For the built-ins,
successful normalization sets it, so normalization runs inside the wrapper before the wrapper
declares completion. The third is `completed_at`, which is written only on a valid completed
attempt. The fourth is `stopped_at`, which goes in the attempt record for every other outcome. The
first wrapper wrote completion on any exit and stamped validation afterwards, as review item M8
found. The migrated `dispatch.sh` stamps validation during normalization, writes `completed_at`
only after that, and writes `stop.json` for any other outcome.

**Parsing.** An output that lacks the arm's expected markers is `unresolved`, not an empty review.
The authoritative final response is selected by session and role, not by "last text seen".
Fixtures cover clean, incomplete, malformed and multi-worker outputs.

## 8. Migration

1. Create `bench/` with the schemas, the rubric v1, and `rates.json` seeded from the dated evidence
   already recorded. Seed `harness/` with the two Claude Code 2.1.281 prompt hashes.
2. Move `dispatch.sh`, `attempt_audit.py`, `normalize_review.py`, `codex_usage.py`,
   `transcript_usage.py`, and `build_packet.py` into `bench/tools/`. `dispatch.sh` keeps its own
   name until `run_cell.py` replaces it. Keep their provenance checks, replay support, request
   deduplication, cache-tier bounds, native output retention and blind rendering. Update the links
   in the research docs that cite them. Apply the three defect fixes from the review, which cover
   the relative-path audit, the timing semantics, and unresolved parsing.
3. Convert the six #137 targets. Build `target.json` from the shell fragments and README tables.
   Preserve `packet.legacy.md` with the recorded hash, and derive a factual `packet.md` from it.
   Build `register.v1.json` from each prose register, and build `register.v2.json` for (n). Build
   `smoke.json` from the recorded provisioning outcomes where they exist, and otherwise re-measure
   the outcomes at rebuild.
4. Rebuild mirrors and caches into the cache root. Verify the negative SHAs and diff identities.
   Archive the caches with hashes.
5. File the toy fixtures as `bench/runs/2026-09-24-toy/` with attempt manifests. Rewrite the
   2026-09-24 README as the narrative for the first real run, and point it at the run's future
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
