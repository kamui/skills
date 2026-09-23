# Review-code artifact-savings baseline, issue #341

This directory freezes the inputs and the baseline for the artifact-savings work in [#340](https://github.com/kamui/skills/issues/340), and implements [#341](https://github.com/kamui/skills/issues/341). It contains:

- four archived interface tasks that reconstruct offline and detect altered or missing inputs by hash;
- four measured baseline cells at the frozen Sonnet 5 High setting;
- a [consumer map](consumers.md) from each repeated field to its authority;
- the [paired protocol](protocol.md) that #347 runs the treatment under.

No runtime skill text, workflow, private schema, helper, forge fetching or review policy changes here. The #333 bundle stayed inconclusive because nine historical inputs were never archived. These tasks avoid that by committing every input they need.

## Baseline revision

The baseline is `d8c2dd93bbfff6ac85907159e7763508265f5442`, the merge of #339, at workflow `v5b-24` (`validate_review.WORKFLOW`). `origin/main` was that commit when this work began, so there were no intervening changes to reconcile. `git diff 44b9331 d8c2dd9 -- skills/` is empty, so the #333 treatment run C8-T1 used the same skill tree. [`baseline/static.json`](baseline/static.json) records the static inventory: `SKILL.md` is 1,596 words and 11,494 bytes, and the 14 references total 10,771 words and 76,855 bytes. It also records every helper's `--help` and `--example` output and each script's source size.

## Archive

[`archive/`](archive/) holds 59 files. Its [`manifest.json`](archive/manifest.json) has SHA-256 `f7880b94071417ed440219ae8b8a21836d03760ed6cbd209848a156d9e5a9ca9` and lists every file's size and hash, the fixture commit SHAs, and the bundle heads. The target is a small standard-library Python ledger built from text fixtures ([`archive/fixture/`](archive/fixture/)) with pinned identity and dates. [`ledger.bundle`](archive/ledger.bundle) (12,747 bytes, SHA-256 `3d62a06b…01cc52`) holds all eight commits. The pull-request coordinates name a fictional `https://github.com/example/ledger`, and no reviewer reaches it. The target is synthetic because no historical PR offered an uncontaminated body with complete frozen inputs.

| Task | Interface | Target | Inputs |
| --- | --- | --- | --- |
| `publishable` | `review-code-publish`'s one-shot publishable review from a supplied packet | PR 4, CSV export, `2301c83…0eb283d` | Saved GraphQL root page and its `forge_packet.py normalize` packet, closing issue 3 |
| `implementation-gate` | `implement-publish` step 4 over a committed range | `2301c83…2ba4046`, date filters, two commits | Spec file, caller verification results, suite output, and criterion-5 exercise output |
| `required-verification` | One-shot publishable review whose change edits `ledger/auth.py` authorization | PR 6, delegates, `2301c83…a13922e` | Packet and page, closing issue 5 |
| `continuation` | `implement-publish` continuation after fixes | Record at `864eea8`, addendum at `03ce7cd`, final head `b96a362` | Seeded version-2 record, addendum, verifier bundle, raw return and accounting; spec; verification results at the final head |

The verification task requires a batch whatever the reviewer finds. The change edits authorization, so a must-fix or security candidate needs confirmation and a no-blocker conclusion needs the safety-premise check. It depends on neither a planted defect nor a PR body.

The seeded chain is an initial review of account freezing at `864eea8`. It carries a confirmed P1 `must-fix` (`accounts/frozen-transfer-bypass`: `Ledger.transfer` never reads `frozen`), a P3 `consider` about the `post` docstring, and one initial batch with its bundle, raw return and accounting. Its addendum at `03ce7cd` classifies the finding `still-open` because only a frozen source is refused. The follow-up is still unspent. The final head `b96a362` refuses both directions and documents the error. [`seed_archive.py`](seed_archive.py) derived the context store and digest, bundle, accounting report and record by running the baseline helpers on the authored inputs. The composer accepted the seeded composition unchanged.

**Relocation.** Templates carry `@TASK_ROOT@`, `@SKILL_ROOT@` and `@SHA256:<file>@` tokens, only in fields each task's `task.json` declares, including `carried:` task references. [`savings_archive.py`](../tools/savings_archive.py) realizes them in hash-dependency order: input, brief, manifest, raw return's `manifest_sha256`, then the accounting hashes. It writes `realization.json` with the path map, template and realized hashes, and the manifest hash. `check` recomputes every realized file, compares each JSON value with its template with only the declared fields masked, and confirms each repository's branches, head and clean tree. With `--skill-root` it realizes the tasks again at a second root. There it replays `review_context.py`, `context_fingerprint.py`, `build_verifier_prompt.py`, `account_verifier_return.py` and the implementation-gate composer, and requires byte-identical output. Materialization never repairs a live record, and spec identities are coordinates, so relocation leaves the context digest unchanged.

**Reconstruction.** [`reconstruction.md`](reconstruction.md) copies only `archive/` and the tool into a new temporary directory. It runs verify, fixture rebuild, materialize and check inside `unshare -rn`, with loopback down and no parent repository. All pass. One altered byte, a missing file, and materializing from the altered archive are each refused with exit 1. `test_savings_archive.py` repeats this and adds tampered realizations, relocation to two roots (only declared pointers differ), unsafe roots, the declaration rules on a synthetic archive with carried references, and the baseline helper replay, including a changed composer.

## Baseline cells

[`run_cell.sh`](run_cell.sh) launched each cell from a fresh `materialize` of the archive, with `git archive d8c2dd9 skills/review-code` as the skill. It used Claude Code 2.1.280 with `--safe-mode`, no setting sources, and no MCP, hooks, skills or CLAUDE.md, capped at $15. Cells ran one at a time on 2026-09-23. A $0.0257 no-tool [preflight](preflight/result.json) first confirmed that the `Agent` tool keeps `run_in_background`, so a foreground route exists. `agent_effort.py` found `claude-sonnet-5` at `high` on every assistant line of all four root and three worker transcripts ([`effort.txt`](baseline/publishable/effort.txt) in each cell). No cell was capped, timed out, retried or denied a permission. After the runs, `check` still matched the archive. [`collect_cell.sh`](collect_cell.sh) gathered each cell's evidence: gzip transcripts with uncompressed SHA-256, the harness result, `metrics.json` from [`interface_metrics.py`](../tools/interface_metrics.py), and the cell's `work/` outputs.

| Cell | Returned | Verifier batch | Artifacts | Process elapsed | Harness cost |
| --- | --- | --- | --- | ---: | ---: |
| [publishable](baseline/publishable/) | Changes Requested: 1 P2 must-fix (CSV formula injection, security), 1 observation | Initial, 1 candidate, confirmed | Payload validates; batch and fragments written | 443.8 s | $1.7964 |
| [implementation-gate](baseline/implementation-gate/) | Approved, 1 observation | None required | `record.json` validates | 357.7 s | $1.2393 |
| [required-verification](baseline/required-verification/) | Changes Requested: 2 must-fix (P2 security, P3 requirement), 1 observation | Initial, 2 candidates, both confirmed | Payload validates; batch and fragments written | 616.0 s | $1.6895 |
| [continuation](baseline/continuation/) | Approved: both reported fixes `fixed`, nothing new | Follow-up, 2 data-integrity premises, both `holds`; follow-up now spent | [Addendum](baseline/continuation/addenda/) written beside the unchanged seed | 267.5 s | $1.0443 |

The four cells cost $5.7695, or $5.7952 with the probe. These are harness list-price costs, including about $0.0016 per cell of the harness's own Haiku charges. Outcomes are reported as observed, not scored: these tasks measure interfaces, not recall.

### Usage

| Cell | Root turns / tool calls | Worker turns / tool calls | Cache read (all) | Cache write (all) | Output (all) | Thinking (all) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| publishable | 44 / 60 | 8 / 10 | 3,833,433 | 154,922 | 46,385 | 24,427 |
| implementation-gate | 34 / 52 | — | 2,396,868 | 97,344 | 36,884 | 20,652 |
| required-verification | 35 / 58 | 9 / 14 | 3,120,411 | 152,068 | 51,564 | 30,429 |
| continuation | 29 / 36 | 10 / 10 | 1,908,272 | 108,845 | 27,686 | 13,923 |

Turns are distinct API requests, as `transcript_usage.py` counts them. The harness's `num_turns` (61, 53, 59, 37) counts differently and is kept in each `metrics.json`.

### Validation tail and repairs

| Cell | Finalizer calls / failed / repair loops | After first validated output: turns / tool calls / seconds |
| --- | --- | --- |
| publishable | 1 / 0 / 0 | 5 / 5 / 44.9 |
| implementation-gate | 1 / 0 / 0 | 5 / 4 / 53.1 |
| required-verification | 1 / 0 / 0 | 5 / 6 / 74.7 |
| continuation | none (no finalizer for an addendum) | After the last addendum write: 3 / 2 / 34.7 |

No cell needed a finalizer repair. At this baseline, the post-validation tail is spent writing `report.md` (5,516–12,692 characters) and the final message after the validated artifacts already exist.

### Loads

| Cell | Entrypoint + distinct references read | Their static words | Helper help / example invocations (words delivered) | Script source reads (words delivered) | Primary reads of bundle files |
| --- | --- | ---: | --- | --- | --- |
| publishable | 1 + 9 | 9,338 | 8 / 2 (1,335) | 5, of `compose_review.py` and `finalize_review.py` (4,501) | 2 |
| implementation-gate | 1 + 7 | 7,836 | 4 / 1 (1,002) | 2, of `context_fingerprint.py` (1,041) | 0 |
| required-verification | 1 + 9 | 8,608 | 6 / 3 (1,194, plus a 182-word call mixing help and example) | 1, `build_verifier_prompt.py` through inline Python (90) | 2 |
| continuation | 1 + 4 | 5,608 | 0 / 1 (211) | 7, of four helpers (3,522) | 2 |

Each worker read only its generated brief and manifest (2,254–2,613 words) after a dispatch prompt of 111–279 words, and loaded no skill file. Delivered words exceed static words because Read results carry line-number prefixes. Both pull-request primaries loaded `verifier.md` and `verifier-return.md`, and the verification primary also loaded `verifier-concurrency.md`, although the builder embeds that text for the worker. Every primary also read helper source to learn an input shape, most often the composer's or the verifier builder's. Counts are per invocation: a Bash loop over seven helpers' `--help` is seven loads, and relative paths follow the shell's directory across calls.

### Authored fields

Every JSON artifact the model wrote, split under the consumer map's inventory. That includes one the gate cell wrote from a program inside a heredoc, which no tool-call write names:

| Cell | Composition or addendum: mechanical / judgment leaves | Verifier input | Raw return | `report.md` characters |
| --- | --- | --- | --- | ---: |
| publishable | 30 / 55 | 8 / 33 | 1 / 26 | 10,054 |
| implementation-gate | 34 / 63, plus fingerprint input 5 / 0 (147 words) | — | — | 9,351 |
| required-verification | 8 / 38 | 8 / 56 | 1 / 31 | 12,692 |
| continuation | Addendum 22 / 35 | 8 / 17 | 1 / 21 | 5,516 |

Mechanical leaves are fields an authority already determines: run identity, fingerprint input, paths, manifest file paths, rulings, allowance, the worker's `manifest_sha256`, and the addendum's identity and delta paths. Judgment leaves include verifier-input candidate fields that repeat the composition's findings. `run.coverage` and summary fields count as judgment. The counts measure transcription, not review effort.

## Explaining 1,596 + 10,771 words

The static inventory is unchanged at the baseline, but no run loads it. The primaries read the entrypoint plus 4 to 9 of the 14 references, whose static text is 5,608–9,338 words. On top of that came helper help and example output (211–1,335 words) and helper source (90–4,501 words). C8-T1 ran the same tree on a different PR and read 12 references and three helpers' source seven times. Reference count is therefore a poor proxy for load. What moves between tasks is which references a primary opens, whether it reads worker-only instructions, and whether it falls back to helper help or source to learn an input shape. Later tickets should report those loads from `interface_metrics.py cell` alongside any static change. A word or reference reduction alone is not a savings result.

## For the feature tickets

These are baseline observations, not savings claims:

- #342: every cell rewrote the complete review into `report.md` after validation, which is most of the post-validation tail.
- #343: no repair loops occurred, so savings can come only from mechanical transcription. Composition inputs carried 8–34 mechanical leaves, and the gate cell also hand-built its fingerprint input.
- #344: every worker hand-copied `manifest_sha256`. Verifier inputs carried 17–56 judgment leaves, among them candidate fields the composition repeats.
- #345: the continuation hand-wrote an addendum with 22 mechanical leaves and no validator, after seven reads of helper source.
- #346: both pull-request primaries opened worker-only references.

## Limits

These are single runs of small synthetic tasks, so run-to-run variance is unmeasured and no recall, general cost or latency claim follows. Process elapsed time is the launcher's wall clock around the session. Cost is harness-reported list price, not billing. Evidence paths name `/tmp/rcs-savings`, the realization root. The fixture's `AGENTS.md` and `.gitignore` are committed under their real names in `archive/fixture/files/M0/`, so an agent working inside that folder may read them as live instructions. Renaming them would change the sealed manifest these cells ran against. #347 may reuse these cells only under the protocol's unchanged-harness condition. Otherwise it reruns them beside the treatment.

## Reproduce

```sh
python3 docs/research/tools/savings_archive.py verify docs/research/review-code-artifact-savings-2026-09-22/archive
git archive d8c2dd93bbfff6ac85907159e7763508265f5442 skills/review-code | tar -x -C /tmp/rcs-savings/skills/d8c2dd9
python3 docs/research/tools/savings_archive.py materialize docs/research/review-code-artifact-savings-2026-09-22/archive \
  --root /tmp/rcs-savings/baseline --skill-root /tmp/rcs-savings/skills/d8c2dd9/skills/review-code
python3 docs/research/tools/savings_archive.py check docs/research/review-code-artifact-savings-2026-09-22/archive \
  --root /tmp/rcs-savings/baseline --skill-root /tmp/rcs-savings/skills/d8c2dd9/skills/review-code
python3 docs/research/tools/test_savings_archive.py
python3 docs/research/tools/test_interface_metrics.py
```

Cells then follow [protocol.md](protocol.md). This work touches `skills/review-code/DESIGN.md`, so run `scripts/sync-global-skills` once it reaches `origin/main`.
