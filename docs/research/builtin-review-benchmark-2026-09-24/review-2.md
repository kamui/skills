## Must change

1. Define exactly which suite files reviewers can access.
   
   Evidence: [proposal:11](/tmp/builtin-bench-probe/codex-review-2/proposal.md:11) places plaintext registers beside packets; [method:85–103](docs/research/code-review-one-shot-method.md) excludes evaluator material from reviewer-accessible directories and history. `attempt_audit.py:65–68,200–202` misses relative paths; I confirmed `cat ../targets/i/register.v1.json` escapes its checks. Consequence: fresh HOME plus the existing audit cannot establish uncontaminated execution. Minimal fix: export only permitted inputs into an enforced filesystem/network sandbox; keep registers, adjudications, other attempts and the suite’s Git history inaccessible.

2. Separate frozen target evidence from experiment instructions before migrating packets.
   
   Evidence: all six committed #137 packets match their recorded hashes. However, `i-requests-6667/packet.md:299–318` binds `/tmp/qual137`, Sonnet workers and staged research-report writing; four packets name `master`, while the new adapter requires `main`. Consequence: unchanged packets contradict new arm configurations and restore the intervention the current benchmark deliberately removed. Minimal fix: preserve original bytes and hashes; create explicitly versioned derivatives separating factual context from run policy. Rebuilding mirrors does not require re-querying GitHub for these packets.

3. `attempt.json` and `results.json` need explicit cell accounting and denominators.
   
   Evidence: [proposal:13–14](/tmp/builtin-bench-probe/codex-review-2/proposal.md:13) names artifacts but omits the relationships required by `code-review-one-shot-method.md:122–154,266–288`. Consequence: six months later, replacement attempts, substantive failures and unattempted cells cannot reliably enter completion, recall or matched-cost calculations. Minimal fix: freeze planned `(target, arm, replicate)` cells; record unique attempt IDs, predecessors, retry reasons, continuity, validity and completion separately. Results must identify included attempts, missing cells, denominators and both attempt-level and completed-only views.

4. Resolve configurations before dispatch and bind every derived artifact to immutable inputs.
   
   Evidence: [proposal:12–14](/tmp/builtin-bench-probe/codex-review-2/proposal.md:12) allows `current` and “newly observed” versions; `builtin-review-benchmark-2026-09-24/README.md:54–60` already invalidates mid-grid pin changes. Consequence: one arm label can silently cover different executions, and later normalization can invalidate item mappings. Minimal fix: resolve `current` once; snapshot exact adapter prompts/commands, requested and observed worker configurations, budgets and CLI identities. Add schema versions and hashes linking target, packet, register, arm, native payload, normalization, mapping, method and metric-code revisions. Reject unexpected within-grid drift.

5. A provisioning recipe does not establish deterministic execution.
   
   Evidence: #137 `tooling.md:426` runs `npm install` against a machine-local cache, restores `yarn.lock` and deletes `package-lock.json`. `README.md:293–296` records an OpenSSL-related failure already present at base. Consequence: a six-month rerun may have different dependencies, available checks or baseline failures despite identical source SHAs. Minimal fix: record toolchain/platform and resolved dependency identities, artifact hashes and retrieval/retention locations; preserve provisioning and base/head smoke-check outcomes. `target.json` also needs the original base SHA, expected ref layout and diff identity. Changed execution availability must be a declared comparison difference.

6. The proposed scoring schema cannot express the governing metrics.
   
   Evidence: [proposal:13](/tmp/builtin-bench-probe/codex-review-2/proposal.md:13) offers only defect, false finding or non-material. The method additionally requires unresolved judgments, duplicate false-claim groups, fix sufficiency and independent review-level outcomes. Existing definitions also differ: #137 `evaluation.md:83–90` counts Approved as false clean despite recovery; the builtin benchmark `README.md:244–248` requires zero recovery. Consequence: identical payloads can receive different scores under an undocumented rule. Minimal fix: version the scoring rubric; retain native verdict/completion, stable item IDs, duplicate groups, unresolved states and per-defect fix judgments. Make unavailable and zero distinct.

7. Register updates require judgment updates, not just arithmetic rescoring.
   
   Evidence: [proposal:19](/tmp/builtin-bench-probe/codex-review-2/proposal.md:19) says to rerun `score.py`. Yet `n-ripgrep-2957/register.md:132–186` changes clean to buggy after adjudication, and `k-graphql-js-1582/register.md:112` explicitly makes materiality rubric-dependent. Consequence: old “non-material” mappings remain wrong after adding a defect; changed adjudicators can also move scores without reviewer improvement. Minimal fix: bind mappings to register and rubric hashes, record adjudicator configuration and evidence, and blindly reconsider affected historical payloads. Preserve original scores and append new scoring revisions. Import n’s v2 while retaining v1; retain clean-target reasoning, non-defects and register revision lineage.

8. Repair timing semantics before adopting the existing wrapper.
   
   Evidence: `dispatch.sh:102–105` records completion even on failed exits; `normalize_review.py:261–266` subsequently timestamps payload validation; `transcript_usage.py:366–383` requires validation before completion. Consequence: normal post-processing creates invalid ordering, while failures acquire fabricated completion times. Minimal fix: distinguish process exit, validated payload, result completion and stop events; define which interval includes normalization. Preserve missing historical events as unavailable.

## Should consider

1. Separate price changes from resource-efficiency changes.
   
   Evidence: [proposal:20](/tmp/builtin-bench-probe/codex-review-2/proposal.md:20) pins each run’s rates; #137 `metering/README.md:18–24` already preserves request-level model, cache-tier and service-tier usage. Consequence: cheaper later prices can look like a more efficient reviewer. Minimal fix: retain those request records, dated rate evidence and cost bounds; distinguish billed dollars, list-price equivalents and quota. Offer common-rate repricing alongside contemporaneous cost.

2. Give external transcripts an archival contract.
   
   Evidence: [proposal:14](/tmp/builtin-bench-probe/codex-review-2/proposal.md:14) records paths only; current toy fixtures likewise live under `~/.t3/bench-runs/toy/`. Consequence: machine cleanup prevents later audit or parser correction. Minimal fix: retain hashed private archives of root and descendant transcripts, with recoverable locations and a restoration check. Commit only the safe evidence subset.

3. Treat unknown output formats as unresolved parsing.
   
   Evidence: `normalize_review.py:145–177,258–260` accepts unfamiliar nonempty Codex output as a summary with zero items. I confirmed this using a changed findings heading. `attempt_audit.py:167` also selects the last assistant text across collected transcripts. Consequence: CLI or fan-out changes can alter apparent recall without changing review quality. Minimal fix: identify the authoritative final response by session/role, retain raw output, and add fixtures for clean, incomplete, malformed and multi-worker results.

4. Track benchmark exposure, not just target age.
   
   Evidence: [proposal:24](/tmp/builtin-bench-probe/codex-review-2/proposal.md:24) records merge dates; the current benchmark `README.md:182–186` also acknowledges that these targets shaped skill development. Consequence: gains on reused targets may reflect local tuning or exposure to published answers. Minimal fix: record suite publication and development-use history; report regression and fresh cohorts separately, with fresh selection frozen before candidate outputs.

## Disagreements with the proposal's reasoning

- “Same target set, same register version, same metric code” is insufficient. Different product versions can legitimately be compared, but execution policy, dependency availability and adjudication changes must remain visible. Use explicit compatibility checks and declared comparison dimensions; do not interpret a product-version delta as an isolated model or skill effect.

- Automatic target intersection changes the question. A difficult unavailable target can disappear, and successive comparisons can use different populations. Freeze the intended comparison cohort; report exclusions and missingness, and label intersection-only results as subset analyses.

- Moving four scripts is not the main simplification. Keep the existing packet provenance checks and replay support, request deduplication, cache-tier bounds, native outputs and blind rendering. Generalize their inputs and validate their contracts. Avoid promising “five small scripts” before accounting for provisioning, isolation, restartable accounting and schema validation.

## What is sound

The suite/run/write-up split is useful. Frozen evidence, stable defect IDs, mechanical scoring, retained native outputs and append-only measurements are appropriate foundations. The missing piece is an explicit contract for what remains comparable across revisions.