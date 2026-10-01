# Rewrite acceptance, issue #333

Disposition: **inconclusive**. The mechanical checks and instruction measurements are complete. Unavailable frozen inputs prevent acceptance of the rewrite's review usefulness. Implementation completion in #330 through #332 is separate from this acceptance decision. No runtime skill or review policy changes are proposed by this report.

The baseline is `7387c169c9b5b23c5c679efb7110c9c07fc3f7f3`; the treatment is `44b9331ae45650450fbd56fbf1f0ad1d29257b15`. The [comparison manifest](../comparison.md) and [adjudicator expectations](../expected-outcomes.md) remain unchanged. This report implements [#333](https://github.com/kamui/skills/issues/333) and updates the acceptance evidence for [#328](https://github.com/kamui/skills/issues/328).

## Mechanical and integration evidence

All 14 commands in [checks.json](checks.json) passed on the treatment revision. The tracked tree was clean when checks began; the run created only untracked acceptance artifacts. Python 3.14.7, Git 2.34.1, Linux. The commands took 97.808 seconds in total, measured around each process. This is check execution time, not review latency or total task elapsed time.

| Obligation | Executed evidence | Limit |
| --- | --- | --- |
| Composition, public shapes, missing verification results, incomplete coverage, versioned records and spent allowance | [Composition](logs/test_compose_review.txt), [validator](logs/validate_review.txt), [verifier handoff](logs/test_verifier_handoff.txt) | Synthetic contract fixtures; no claim of an actual C9/C10 continuation |
| Snapshots, provenance, deleted-file anchors, complete fetches and stale identity | [Context fixtures](logs/test_review_context.txt), [context self-test](logs/review_context.txt), [deleted links](logs/test_deleted_file_links.txt), [forge packet](logs/test_forge_packet.txt), [fingerprints](logs/test_context_fingerprint.txt) | Disposable local fixtures |
| Changed recipes, publication freshness, token refusal and ambiguous-write handling | [Command chains](logs/test_command_chains.txt), [run events](logs/test_run_events.txt) | Stubbed forge commands, no live publication |
| Preserved public comments, reply vocabulary and addressing writes | [Check runs](logs/test_check_runs.txt), [thread writes](logs/test_thread_writes.txt), [resolve-review blocks](logs/test_run_block.txt) | `resolve-review` consumes the published contract; this is not a live addressing round |
| `finish-it` through its direct dependencies | The preceding command/contract checks plus the [static caller trace](clarity.md) | No live delivery, published review, or merge |
| Real instruction layout and generated briefs | [Budget output](logs/test_instruction_budget.txt) | Measures actual runtime Markdown and expanded helper output, not model tokenization |

The [static inspection](clarity.md) traces `implement-publish`, `review-code-publish`, `resolve-review`, and `finish-it`. The private addendum contract explicitly has no dedicated script validator. Passing record/chain fixtures does not prove a model continuation follows that contract. Supplied-evidence reuse still requires judgment about check identity, head, inputs, environment, completeness, and coverage; a schema check cannot establish those facts for a live review.

## Instruction measurements

The [baseline archive measurement](baseline-sizes.json) and treatment budget output reproduce [the documented method](../runtime-layout.md#measurements). Bytes are UTF-8; words are whitespace-separated. Primary paths include actual helper help/examples. Example briefs include their fixture records; instruction-only rows exclude them.

| Load | Baseline bytes / words | Treatment bytes / words | Word reduction |
| --- | ---: | ---: | ---: |
| All runtime instructions | 150,821 / 22,046 | 88,349 / 12,367 | 43.9% |
| Always loaded | 70,938 / 10,423 | 25,285 / 3,435 | 67.0% |
| Local primary with helper output | 120,731 / 17,068 | 64,918 / 8,547 | 49.9% |
| PR primary with helper output | 121,507 / 17,259 | 64,052 / 8,501 | 50.7% |
| Ordinary verifier instructions | 28,685 / 4,287 | 14,056 / 2,003 | 53.3% |
| Ordinary example brief | 30,802 / 4,476 | 16,460 / 2,221 | 50.4% |
| All specialized verifier instructions | 34,014 / 5,052 | 19,288 / 2,752 | 45.5% |
| Specialized example brief | 37,225 / 5,320 | 22,786 / 3,049 | 42.7% |

The budget test enumerates the actual remaining runtime references and renders both ordinary and specialized verifier inputs. It includes supplied checks and the conformance, concurrency, and released-compatibility branches. The lowered limits remain 26,000 bytes always loaded, 92,000 total, 67,000 per representative primary path, 20,000 specialized verifier instructions, and 24,000 for its example brief. No limit was raised. These measurements establish no general quality, latency, or billed-cost improvement.

## Entrypoint comprehension

An independent first read of only `SKILL.md` identified the strategy, candidate and safety-premise triggers, merge-blocking action, incomplete conditions, and returned artifacts. [The reading record](clarity.md) cites each rule before tracing callers. This is a static comprehension exercise, not an owner usability test.

One problem remains visible: the entrypoint requires confirmation before publishing a new candidate but gives an unsettled existing blocker status precedence. A reader must distinguish those states to choose `Incomplete` versus `Changes Requested` after verification runs out. The handoff reference settles the distinction, but the entrypoint does not illustrate it. Record this friction; this sample does not demonstrate that another policy rule is needed.

## Bounded comparison

The [screen record](screen.json) preserves the frozen 20 planned case attempts, at most two replacements, two concurrent attempts, $15 per attempt, and $250 total. The owner retained `claude-sonnet-5` at `high` for the experiment. Claude Code 2.1.280 is the common harness. Later implementation/review subagents use Sol 6 high at the owner's request; their work is outside the matched screen.

A no-tools availability probe was capped at $0.10 and conservatively consumes one replacement slot. [Its result](model-preflight.json) reports READY and $0.0263998 of harness cost, including a small Haiku helper charge. It is not a case attempt or review-quality result.

The owner confirmed that no historical archive is available and requested inconclusive results for unavailable cases. [Resource preflight](resource-preflight.json) records the absent paths and continuation evidence gap. Reviewers receive neither expected outcomes nor adjudication reports.

| Case | Result or reason unavailable |
| --- | --- |
| C1, Redis failover recovery | Inconclusive, not run. Original truncated mirror and packet were not recovered from the recorded host paths. The historical verifier-aside recovery remains context, not a result at either new pin. |
| C2, ordinary parser false clean | Inconclusive, not run. Packet text exists; the frozen mirror is unavailable. No observation about the rewrite's reduced scrutiny of ordinary parser acquittals. |
| C3, hygiene beside a behavioral concern | Inconclusive, not run. Historical packet exists; frozen target mirror is unavailable. |
| C4, unchanged-code requirement omission | Inconclusive, not run. Historical record exists; frozen target mirror is unavailable. |
| C5, released compatibility | Inconclusive, not run. Historical packet exists; target and released-source mirror are unavailable. |
| C6, clean concurrency control | Inconclusive, not run. Historical packet exists; frozen target mirror is unavailable. |
| C7, fresh buggy sample | Inconclusive, not run. Current PR body was edited after the first review and reveals the fix. [Packet construction refused the moved head](C7-packet-build.json); deleting later comments would not remove the body contamination. Independent adjudication reproduced the known defect and repair, but that is not a blinded review recovery. |
| C8, fresh clean control | Both returned `Approved`, with no must-fix and no questions. Baseline returned one `consider`; treatment returned none. Both payloads validate. See the attempt evidence and scoring below. |
| C9, continuation and version transition | Inconclusive, not run. Source revisions and unedited specs are available, but the required acceptance packet is not. Both pinned implementations explicitly say the real-delivery initial brief, continuation packet and returned accounting are still owed. An invented successful capture would invalidate the exercise. |
| C10, exhausted continuation | Inconclusive, not run. No admitted C9 phase-1 record and complete acceptance packet exist here to seed the prescribed case. The synthetic commit was not constructed. Exhaustion and carried allowance were exercised only in the mechanical fixtures. |

C7 and C8 expectations were independently checked before case dispatch. [Adjudication](fresh-adjudication.md) separates the C7 base/head/fix reproduction and C8 source/test inspection from model outcomes. Its [C7 reproduction artifacts](adjudication-evidence/) are retained. No historical optional comment or exact prose match is a scoring requirement.

## C8 results and limits

| Attempt | Returned status | Must-fix / consider | Verifier batches | Process elapsed | Harness-reported cost |
| --- | --- | ---: | ---: | ---: | ---: |
| [C8-B1, baseline](C8-B1/report.md) | Approved, complete coverage | 0 / 1 | 0 | 844.004 s | $3.1261698 |
| [C8-T1, treatment](C8-T1/report.md) | Approved, complete coverage | 0 / 0 | 0 | 487.891 s | $2.5684718 |

Both ran to completion without permission denials or model/effort mismatches. The baseline's optional finding asks the extracted command's docstring to acknowledge an existing uncaught-error exit. The treatment records only an observation about test placement. Optional differences do not establish a consequential divergence.

The pair occupied 844.004 seconds from the first dispatch to the last completion. The sum of process durations is 1,331.895 seconds and counts overlapping time twice. Total harness-reported screen cost, including the $0.0263998 probe and helper charges, is $5.7210414. These are reported list-price usage costs, not billing receipts. This is one pair, with different investigations and check selections, and it supports no general speed or cost claim.

Both arms' own `validate_review.py` accepted their original payloads. The [baseline](C8-B1/events-summary.json) and [treatment](C8-T1/events-summary.json) event summaries have no violations. Their missing root dispatch/completion and usage fields remain unavailable; process durations above come from the orchestrator's recorded timestamps, and token/cost observations come from the separate transcripts/results. Zero verifier work is supported by both transcripts and harness worker counts, not inferred from absent timing events.

The frozen cross-case expectation that trailers differ only in `workflow` was not fully met. Their `context` hashes also differ. The treatment's transcription of the PR body adds one trailing newline. [The investigation](context-difference.json) reproduces each full hash with base guidance and the saved context store. The fingerprint helper is byte-identical in both arms and produces the same result on the same input. The artifacts retain the original hashes; no output was repaired. This limits the exact-identity comparison and does not establish a changed trailer grammar or a rewrite-policy cause.

Three model invocations count against the 22-attempt bound: the probe and two completed case attempts. No review attempt failed or was stopped. Adding the availability probe was a preflight departure from the ten-case list; it consumes one of the two replacement slots conservatively. Packet-construction refusal for C7 is retained as a preflight result, not miscounted as a reviewer attempt. No additional screen work was launched for unavailable cases.

The [independent blinded scorer](C8-scoring.md) passed both consequential outcomes and found no unsupported blocker or material coverage gap. The post-scoring key is sample K = C8-T1 and sample O = C8-B1. The scorer did not receive arm labels. No consequential outcome diverged, so no repeat was required. The strict identical-fingerprint-input comparison remains limited by the recorded newline difference.

## Disposition and follow-up

Do not accept the rewrite's review usefulness from these checks or instruction counts. The unrun cases leave known-blocker recovery, ordinary-parser recall, high-risk premise selection, unchanged-code requirements, released compatibility, and live continuation behavior unsettled. The small admitted sample cannot establish a broad quality guarantee.

The policy tradeoffs remain deliberate: low-risk acquittals lose the exhaustive clean-verdict attack; high-risk no-blocker conclusions receive selected safety-premise checks; ledgers and early dispatch disappear; the two-batch allowance remains. Missing comparison evidence does not validate those tradeoffs or justify adding speculative rules.

Demonstrated follow-up needs are the missing historical inputs, an uncontaminated C7 pre-review body, and C9's missing acceptance capture or an explicitly revised fixture/expectation before a new freeze. Preserve stopped or invalid attempts in the attempt count. No finding from this work closes or repurposes #297 or #265.

This change adds research evidence only. It does not push or merge a `skills/` change into `origin/main`, so the global-sync trigger does not apply to this branch. Run and report `scripts/sync-global-skills` after any future qualifying main-branch skill change.
