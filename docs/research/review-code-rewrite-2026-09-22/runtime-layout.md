# Runtime rewrite, issue #332

The entrypoint now starts from the strategy draft. Reading recipes, whole-file thresholds, read justifications, risk catalogs, candidate-support quotas, and repeated output-format instructions are removed. The reviewer chooses how to inspect the full requested change. Exact target, state, execution, and return contracts remain in conditional references or helper examples.

The main skill is about 1,600 words rather than the drafting aim of 1,000. The exception retains public caller inputs, both modes' asking rules, context recovery and timing interfaces, and the returned state needed by publishing and continuation callers. These contracts account for the extra length; they are not hidden in another universally loaded manual.

Workflow `v5b-24` supersedes `v5b-23` because mandatory reading/search procedures are removed. The candidate and safety-premise policy and version-2 continuation contracts introduced by #331 remain. Public payload and batch shapes, asking behavior, and target semantics are unchanged. This work does not run #333's bounded quality comparison.

## Measurements

Baseline is `7387c169c9b5b23c5c679efb7110c9c07fc3f7f3`, the pin in [comparison.md](comparison.md). Bytes are UTF-8 sizes; words are whitespace-separated tokens, equivalent to `wc -w` for these files. Code and reviewed evidence are excluded. Generated example briefs report their fixture records separately from instructions.

| Load | Baseline bytes / words | Rewrite bytes / words |
| --- | ---: | ---: |
| Entrypoint and all runtime references | 150,821 / 22,046 | 88,363 / 12,367 |
| Always-loaded instructions | 70,938 / 10,423 | 25,285 / 3,435 |
| Local primary, expanded helper output included | 120,731 / 17,068 | 64,918 / 8,547 |
| PR primary, expanded helper output included | 121,507 / 17,259 | 64,052 / 8,501 |
| Ordinary verifier instructions, supplied-check branch | 28,685 / 4,287 | 14,056 / 2,003 |
| Ordinary generated example brief, records included | 30,802 / 4,476 | 16,460 / 2,221 |
| Verifier instructions, all specialized branches | 34,014 / 5,052 | 19,302 / 2,752 |
| Specialized example brief, records included | 37,225 / 5,320 | 22,800 / 3,049 |

Reproduce current figures with `python3 skills/review-code/scripts/test_instruction_budget.py`. For the baseline, read the same files and execute the same helper commands from an archive of the pinned skill. The baseline always-loaded set includes the removed `review-record.md`. Its builder example uses `project(EXAMPLE['input'], EXAMPLE['ledger'])`; the rewrite uses `project(EXAMPLE)`. Render those inputs for ordinary briefs. Add concurrency kind, conformance, and released-compatibility evidence to the example candidate for the specialized case, as the budget check does. Instruction-only sizes stop before `## Supplied records`.

The representative primary paths are first reviews with changed tests, caller check evidence, and an ordinary verifier batch. Each includes the always-loaded set, the appropriate target reference, `changed-tests.md`, `check-evidence.md`, `verifier-handoff.md`, and `verifier-return.md`. They also count the actual output of `review_context.py --help`, `context_fingerprint.py --example`, `build_verifier_prompt.py --example`, and the selected `compose_review.py --example --profile` variant. Local uses `implementation-gate`; PR uses `publishable`. Conformance, released compatibility, re-review, and continuation are not part of these representative paths. The earlier 15,087-word local estimate excluded helper output and supplied-check instructions; the table includes both for each revision.

The budget lowers the old 73,000-byte always-loaded cap to 26,000. Rounded ceilings also guard the whole runtime at 92,000, each representative primary path at 67,000, specialized verifier instructions at 20,000, and its full fixture brief at 24,000. These allow a small maintenance margin above the measured layout, rather than preserving the former allowance. Expanding helper examples cannot escape the primary-path check.

These counts establish no latency, quality, recall, or billed-cost improvement. The policy changes and their recall tradeoff remain subjects of #333.

## Remaining references and consumers

| Reference | Trigger and consumer |
| --- | --- |
| `review-rubric.md` | Every primary review, admission and requirement outcomes |
| `rendering.md` | Primary composition; Identity also serves the PR duplicate check |
| `local-targets.md` | Range/worktree pinning and snapshot/identity inputs |
| `pull-request-target.md` | PR pinning, persisted fetch, pagination, and deferrals |
| `re-review.md` | PR prior state from the reviewer identity |
| `changed-tests.md` | Primary changed-test inspection or execution; worker execution slice |
| `check-evidence.md` | Caller evidence production, primary reuse decisions; worker reuse slice only when evidence is supplied |
| `conformance.md` | Versioned-artifact obligation; worker slice only for conformance task data |
| `released-compatibility.md` | Promise changing a released contract; builder includes its procedure only for matching task data |
| `verifier-handoff.md` | Primary selected a verification batch |
| `verifier.md` | Builder supplies isolated worker procedure |
| `verifier-return.md` | Worker encoding and primary return accounting |
| `verifier-concurrency.md` | Builder sees a concurrency/invariant candidate |
| `continuation-addendum.md` | Continuation or replacement of an implementation-gate record |

`review-record.md` is removed. The composer examples own exact output shapes, rendering owns authoring and identity, and the entrypoint owns status and coverage. The command-chain check reads the finalizer commands from rendering. The continuation caller now points to Strategy and admission instead of the removed Complete inspection section. Other caller input names and reference paths remain stable.
