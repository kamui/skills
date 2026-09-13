# Routine-review miss diagnosis — 2026-09-13

**Exit 3: insufficient current-policy evidence.** The bounded sample contains 20 routine-review runs on 15 `kamui/skills` PRs, but none declares the currently shipped **v5b-15**. Historical corrections provide useful case distinctions; they do not establish a current-policy failure or recurring never-discovered material defects. Close [#216](https://github.com/kamui/skills/issues/216) with this evidence gap. No new discovery study or production-policy change is proposed.

## Collection and policy identity

The [collection plan and frozen selection](collection.md) pin the cutoff to **2026-09-13T07:47:31Z**, the preceding 30 days, and the selection rule before selected outcomes were inspected. Shipped policy is repository commit [`374635be7f4e62f6eb9c797530bf6bf091a9d3a1`](https://github.com/kamui/skills/commit/374635be7f4e62f6eb9c797530bf6bf091a9d3a1); the latest package-touching commit is [`afcdbd86bb328d5071153d65a22ea1fa3f5e7433`](https://github.com/kamui/skills/commit/afcdbd86bb328d5071153d65a22ea1fa3f5e7433). Both the [runtime contract](../../../skills/code-review-publish/references/output-contract.md) and [validator](../../../skills/code-review-publish/scripts/validate_review.py) identify v5b-15.

| Policy evidence | Selected runs | Interpretation |
| --- | ---: | --- |
| Current v5b-15 | 0 | No current-release outcome evidence |
| Declared historical v5b-14 | 1 | R01 |
| Declared historical v5b-13 | 12 | R02–R13 |
| Declared historical v5b-12 | 7 | R14–R20 |
| Unknown declared workflow | 0 | Every selected publication has a workflow trailer |
| Exact installed policy commit unknown | 20 | No selected record establishes the installed package commit; target base/head pins are not policy pins |

These provenance dimensions overlap: a declared historical workflow is known while its exact installed bytes remain unknown. R01 reviewed the PR **introducing** v5b-15 using declared v5b-14; it is not a v5b-15 run. No historical result is relabelled current merely because its rule might still exist.

## Sources and boundaries

GitHub metadata searches were `gh pr list --state all --search 'updated:>=2026-08-14' --limit 200` and the equivalent issue search with `--limit 250`: 108 PRs and 108 issues, below both bounds. GraphQL review/comment connections on those PRs returned 97 `review-run` trailer records in the window. All queried connections reported `hasNextPage=false`; the selected 15 PRs' commit/thread/comment connections were also complete. Issue-body/comment link extraction found 50 issue-to-PR/artifact references, no external review-artifact URLs and no embedded run trailers. These were source-location searches, not 97 outcome assessments.

The 20 newest identifiable runs were frozen as R01–R20. More recent non-trailer review objects had empty bodies and corresponded to thread replies; general comments were addressing summaries, not additional runs. Repository filename inventory located historical prototype/holdout/qualification transcripts and paper replays. They were excluded as experiments or policy illustrations. Selected PR bodies linked implementation/replay bundles, not private transcripts of these routine reviews; the inspected public summaries and thread replies did not supply their private ledgers, verifier returns, or installed-policy manifests. No linked external routine artifact displaced the selection. This accessible-record sample is concentrated on this repository's own tooling and documentation, not representative of ordinary application changes or all uses of the installed skill.

For each selected run, inspection covered its published summary, its source PR's existing correction/thread records and commit history through cutoff. Potential new defects were checked with bounded source history where available; [cases.md](cases.md) distinguishes those checks from unadjudicated claims. The source URLs remain authoritative; the report retains the selected identities and evidence coordinates, not an archival copy of every mutable GitHub body. API collection occurred shortly after cutoff, so an unavailable prior version of edited prose would remain a retrospective limitation.

[Audit preparation #173](https://github.com/kamui/skills/issues/173), execution #174 and grading #175 were open; #173 remained blocked by #171, with no frozen fresh target manifest or dispatched comparison identified. [#199](https://github.com/kamui/skills/issues/199) and [#207](https://github.com/kamui/skills/issues/207) were closed before cutoff with no study planned. Their historical reservations persist. No active reserved target was investigated and no sealed file/archive was opened. Public historical snippets surfaced incidentally during initial repository searches, README identity lookup and a bounded comparison-table read; their exposure is recorded conservatively in [consumed.md](consumed.md). Reviews of study **tooling PRs** are routine runs; the experimental cells those PRs discuss are not additional sample runs.

## What the evidence can decide

The case register establishes **one material missed defect concept across two historical runs**: the ruling-table glob in PR #200 (C05, R19 and R18, declared v5b-12). Existing correction `cf044bc` fixes it. This is one concept persisting across re-review, not two independent discovery failures. The register also separates low-impact omissions, a later-introduced recipe failure, and published findings whose fixes expanded. Repeated reports of the same defect remain one concept. Existing fixes are not counted as misses merely because they happened after review; several repair findings were already published by the selected run.

There is no supported recurring **material discovery-loss** pattern in this sample. A public statement that an independent ledger check stood or exposed an item is not the underlying ledger. Where a miss is supported but the decision trace is missing, its earliest loss stage stays **unknown**. The evidence does not distinguish never-discovered from primary-rejected, policy-omitted, verifier-refuted/unresolved, or publication/cap loss. It therefore supplies no causal basis for selecting a finder over stronger verification, changing screening thresholds, or raising caps.

All 20 selected publications self-report complete coverage; nine are advisory Approved and eleven advisory Changes Requested. Those are reported completion/status fields, not independent proof of correctness. Their routine-run cost, root elapsed time, token usage and actual batch-budget consumption are **unavailable**. Dollar figures and session counts in study-tooling reviews describe the studies or probes, not the cost of the routine reviews. Correction replies and some subsequent reviews report successful remedies; those reports and their limits are retained per case rather than converted into a measured sufficient-fix rate.

The specific evidence gap is **zero identified v5b-15 routine runs, no exact installed policy commits for the historical sample, and no retained private stage traces for its candidate misses**. Absence of a detected miss does not prove a correct review. This is retrospective diagnosis, not measured recall or a strategy comparison. The bounded task ends here: no paid review sessions, comparative grid, container provisioning, monitoring program, or repair ticket unsupported by a demonstrated cause.

## Handoff

The exclusion register is available to [#173](https://github.com/kamui/skills/issues/173) without becoming an execution dependency; that study keeps its own inventory and exclusions. #158/#173/#175 retain their separate audit-comparison scope. #138 remains closed and inconclusive; #199/#207 remain closed. Any future study needs its own concrete run decision, fresh targets, prospective decision criteria and requalification on its actual runtime. This report neither proposes such a study nor changes those prerequisites.
