# Aggregate analysis — v2a and v5a across the 2026-09-01–03 runs

> **Promotion status:** "v5" is the historical prototype name used by this record. PR #17 promoted
> that workflow to `skills/code-review-publish` on `main`; new experiments should invoke
> `/code-review-publish` without the `-5` suffix. "v2a" is `code-review-deep-publish` (PR #18,
> pinned `87c68a9`, the Panel line) and "v5a" is `code-review-publish-5a` (PR #19, pinned `c5f76df`,
> the Skeptic line). Neither branch moved during the runs analyzed here.

**2026-09-03.** Successor to
[`prototype-runs-2026-09-01-aggregate-analysis.md`](prototype-runs-2026-09-01-aggregate-analysis.md).
That document synthesized twelve runs of v2–v5 on three targets and set the contract the two
patched prototypes were built against (handoffs 1 and 2, kept in the untracked `handoffs/` working directory). This one covers every run recorded under
`docs/research/` since — fourteen more, on four targets, two model tiers — and grades every design
change in the two `DESIGN.md`s against its stated, checkable intent.

Inputs, all read in full:

- [test 1](prototype-runs-2026-09-01-test-1/) — `kamui/shortlist#66`: original four runs (Opus 5),
  [`v2a-run-pre-c9.md`](prototype-runs-2026-09-01-test-1/v2a-run-pre-c9.md),
  [`v2a-run.md`](prototype-runs-2026-09-01-test-1/v2a-run.md),
  [`v5a-run.md`](prototype-runs-2026-09-01-test-1/v5a-run.md), both addenda,
  [`evaluation.md`](prototype-runs-2026-09-01-test-1/evaluation.md),
  [`comparison-data.md`](prototype-runs-2026-09-01-test-1/comparison-data.md)
- [test 1 Fable](prototype-runs-2026-09-01-test-1-fable/) — the post-C9 v2a run that executed on
  `claude-fable-5-1`
- [test 2](prototype-runs-2026-09-01-test-2/) — `redis/redis#15680`: original four (GLM-5.3-Flash),
  Sonnet 5 v2a/v5a, addendum, evaluation, comparison data
- [test 2 Fable](prototype-runs-2026-09-01-test-2-fable/) — the v2a/v5a round that executed on
  `claude-fable-5-1`, plus its addendum, evaluation, and comparison data
- [test 3](prototype-runs-2026-09-01-test-3/) — `tokio-rs/tokio#7757`: original four (Sonnet 5,
  untruncated mirror), Sonnet 5 v2a/v5a on a truncated mirror, addendum, evaluation, comparison data
- [test 4](prototype-runs-2026-09-01-test-4/) — `microsoft/playwright#29698`: v2, v2a, v5, v5a in
  one Sonnet 5 cohort, README, evaluation, comparison data
- the two `DESIGN.md`s at the pinned commits, and the pinned run clones under `/tmp/handoff3/` and
  `/tmp/handoff4/`, which were used to re-check the code claims below

The method follows the prior analysis: conclusions are drawn from the raw run records, not only
from the per-test evaluations, and every place this document disagrees with a lower-level document
says so (collected in [§9](#9-where-this-analysis-disagrees-with-lower-level-documents)).

## 0. The corpus and the three caveats that govern it

Twenty-six runs now exist. The prior analysis covered the first twelve.

| Target | Original cohort (model) | Handoff-3 re-test (model) | Fable round (model) | Test-4 cohort (model) |
| --- | --- | --- | --- | --- |
| 1 `kamui/shortlist#66` — doc/schema PR, two author-adjudicated drifts | v2 v3 v4 v5 (Opus 5) | v2a pre-C9, v2a post-C9, v5a (Sonnet 5) | v2a post-C9 (Fable 5.1) | — |
| 2 `redis/redis#15680` — C cluster failover, no issue, human-approved | v2 v3 v4 v5 (GLM-5.3-Flash) | v2a, v5a (Sonnet 5) | v2a, v5a (Fable 5.1) | — |
| 3 `tokio-rs/tokio#7757` — Rust runtime, shipped regression and revert | v2 v3 v4 v5 (Sonnet 5, untruncated mirror) | v2a, v5a (Sonnet 5, truncated) | — | — |
| 4 `microsoft/playwright#29698` — TS API addition, withdrawn 24 days later | — | — | — | v2 v2a v5 v5a (Sonnet 5) |

v2a ran seven times, v5a five. Sonnet 5 was verified from every agent transcript on the handoff-3
and test-4 runs; the Fable rounds were discovered after the fact and are analyzed here as what they
are — same skill, same packet, same clone, different model — not discarded.

Three caveats apply to every quality claim below and are restated at the sites where they bite:

1. **Development set.** Both prototypes were designed after their authors saw tests 1–3. On those
   targets a mechanism firing as designed is evidence; a finding being found is not new evidence of
   reviewer quality. Only test 4 is holdout, and it is holdout for v2a and v5a exactly once each.
2. **n = 1 per cell**, except where the same skill was run twice on one target at two model tiers.
   Those pairs are the program's only variance data, and they show the variance is large.
3. **Cost is comparable only inside a cohort.** Test 4 is the first cohort where all four runs share
   a model, harness, packet, and session. Everywhere else the meters differ, and the two Fable
   rounds were interrupted by rate limits and are not cost data at all.

## 1. Headline outcomes

| | v2a (7 runs) | v5a (5 runs) |
| --- | --- | --- |
| Ground-truth defects found / available | T1 drifts 2/2 (post-C9, both models); T2 defect 1/2 (Fable yes, Sonnet no); T3 regression **0/1**; T4 GT-3 1/1 | T1 Narrow 1/2 (missed bundle drift); T2 1/2 (Fable yes, Sonnet no); T3 **1/1**; T4 GT-3 1/1 |
| Outright false findings published | 1 (T4 `since: v1.43`, P3) | 0 |
| Checkable false acquittals recorded | 2 (T2 Sonnet sub-replica path; T3 branches B and C) | 1 (T2 Sonnet, refuted and then re-confirmed by its own verifier) |
| Published questions | 3 (T2 Fable ×2, T3) plus 1 via `plausible` (T1 Fable) | 2 (T3, T4) |
| `plausible` verdicts | 1 (T1 Fable) | **0** |
| Verifier fired | 6 of 7 (skipped by rule on T2 Sonnet) | 5 of 5 (candidate mode ×3, clean-verdict ×2) |
| Derived status matched the better-adjudicated answer | T1: 1 of 3; T2: Fable under-blocked; T3: right for the wrong reason; T4: unanimous | T1 over-blocked; T2 Fable right, Sonnet wrong; T3 right; T4 unanimous |

Two facts frame everything below.

**The two most important results of the round came from targets the program had called settled.**
Test 2, the "clean" target that four prototypes and two humans approved, has a real defect: the
Fable round found it twice, three fresh-context verifiers reconstructed it, and I re-derived it
from the pinned clone (§2, G3). Test 3's ground truth was found blind by v5a and the fix was
generalized by its verifier — but not to the invariant the production hang actually broke (§2, N2).

**Status is dead as a discriminator.** Ten of ten runs on tests 3 and 4 derived
`Changes Requested (advisory)`; six of six Sonnet/GLM runs on test 2 derived `Approved` on a
defective change. Every comparison in this document is at the finding level.

## 2. Scorecard — v5a (G1–G5, N1–N4, F1, F2)

Verdicts use the handoff's vocabulary: **worked** (fired as intended with the intended effect),
**inert** (no observable effect — split into "no qualifying situation" and "situation arose, did not
fire"), **harmful** (fired and made an output worse, or added cost with no return).

| ID | Change | T1 (Sonnet) | T2 (Sonnet) | T2 (Fable) | T3 (Sonnet) | T4 (Sonnet, holdout) | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G1 | Question channel | no item qualified | none | none | **fired** — benchmark-vs-fixed-`NUM_SHARDS` ([run §9](prototype-runs-2026-09-01-test-3/v5a-run.md)) | **fired** — header-set `Domain=` matching ([run](prototype-runs-2026-09-01-test-4/v5a-run.md)) | **worked** |
| G2 | `introduced here` gate scoped to Code candidates | **fired** — `kind=requirement` finding with fix in unchanged `shortlist-narrow/SKILL.md:46`, no anchor workaround ([run](prototype-runs-2026-09-01-test-1/v5a-run.md)) | n/a (no issue) | n/a | n/a (no requirement candidate) | n/a (issue fully met) | **worked** (1 of 1) |
| G3 | Clean-verdict verifier on high-risk zero-survivor | n/a (survivor) | **fired; upheld a false refutation** ([run §4](prototype-runs-2026-09-01-test-2/v5a-run.md)) | **fired; decisive via aside, not via re-open** ([run §4b](prototype-runs-2026-09-01-test-2-fable/v5a-run.md)) | n/a (survivor) | n/a (survivors) | **split: worked ×1 / harmful ×1**; its contract output (`re-open`) is 0-for-2 |
| G4 | Orchestrator recovery on unrecoverable context | no situation | no situation | no situation | no situation | one interpretive fork (merged state unstated), resolved without invoking it | **inert — no qualifying situation** |
| G5 | Ambiguities section | guidance call recorded in notes, no section | **fired** ×3, incl. the G3 trigger-wording gap | judgment calls in notes, no section | **fired** (digest membership) | **fired** (CI report as observation grounding) | **worked** |
| N1 | Observations channel | fired ×2 (ADR gap; commerce regex) | fired ×2 (`redis.conf`; removed assertion) | fired ×1 (`redis.conf`) | fired ×3 at cap | fired ×1 | **worked** |
| N2 | Fix-sufficiency check for concurrency/invariant kinds | n/a | n/a (refuted) | **fired** — six `clusterSetMaster()` callers, fix refined ([run §4d](prototype-runs-2026-09-01-test-2-fable/v5a-run.md)) | **fired** — narrow per-branch fix replaced by a central one ([run §4](prototype-runs-2026-09-01-test-3/v5a-run.md)) | **fired** — backend survey, remedy widened ([run](prototype-runs-2026-09-01-test-4/v5a-run.md)) | **worked, with a ceiling** (see below) |
| N3 | One follow-up verifier batch | nothing late | nothing late | **fired, load-bearing** — late candidate verified ([run §4c–d](prototype-runs-2026-09-01-test-2-fable/v5a-run.md)) | nothing late | nothing late | **worked** (1 of 1) |
| N4 | Mandatory `plausible` trigger | 0 | 0 (no candidate batch) | 0 | 0 | 0 | **inert — 0-for-5**; delete (see below) |
| F1 | Six contract fixes | digest identical across independently built inputs; validator 0 violations | same; **digest byte-identical to the Fable run** | same | same, three ways | same, two ways | **worked** |
| F2 | Merged-PR retrospective mode | fired, `Mode:` line | fired | fired | fired | **did not fire** — packet framed the PR as an ordinary first review; run followed the packet | **worked** (4 of 5; the miss is a packet defect) |

### The four highest-stakes cells

**N2 on tokio: did the fix guidance reach the invariant level blind?** Partly, and less far than the
test-3 addendum and evaluation say. The primary drafted the per-branch patch ("copy A's recheck into
B and C"), the verifier refused it, named an invariant, enumerated the three post-push branches with
a coverage verdict each, and moved the fix to a single point in `ShardedQueue::push` or
`BlockingPool::shutdown` under the lock that flips the shutdown flag. That is real generalization —
from three copies to one — and it happened with the revert and re-land unreachable. I confirmed the
race the finding describes against the pinned clone: a worker decrements `num_idle_threads` on
`WaitResult::Shutdown` (`pool.rs:542`), drains (`:562-567`), and only then decrements `num_threads`
(`:570`), so a push landing in that window reads "no idle, at cap" and takes branch B, which only
notifies.

But the invariant the verifier named is shutdown-scoped: "a task pushed during a shutdown transition
must be observed by a worker or by the pusher's recheck." The production hang did not involve
shutdown. The revert (`56aaa43e`, #8057) says the hang reproduces with `NUM_SHARDS = 1`, and the
re-land (`8b13642a`, #8337, read from the untruncated staging mirror at
`/tmp/handoff3/mirror-tokio-full`) fixes two things: it seals each shard for shutdown so a racing
push is either rejected or collected — the half v5a's fix matches — **and** it puts the
claim-or-spawn decision and the worker's transition to idle under one `coord` lock, with the worker
re-checking the shards under that lock before going idle, "a task may have been pushed after the scan
above, its spawner seeing this worker as busy and so neither notifying nor spawning." That second half
is the accounting-atomicity invariant the prior analysis identified as the incident's mechanism, and
nothing in v5a's published `Change` restores it. N2 generalized across *branches of one interleaving*;
it did not generalize across *interleavings of one broken invariant*. The mechanism worked as written.
Its brief asks the wrong enumeration question for this bug class, and §8 says how to widen it.

**G3 on redis: did it fire, and did it surface the hidden disagreement class?** It fired both times
zero survivors met a high-risk surface, and the two outcomes could not differ more. On Fable, the
verifier upheld all eighteen dispositions — including the `redis.conf` observation routing the prior
analysis hoped a calibrated run would reach — and spent its single permitted aside on the branch the
primary's row-1 refutation had not traced: when `hdr->slaveof` does not resolve, the demoted master
keeps `slaveof == NULL`, and `updateShardId()` (`cluster_legacy.c:943`) takes its propagation branch
and rewrites the sub-replica's own `shard_id` before the safeguard runs `clusterSetMaster()`, so the
new guard at `:5428` computes `shard_changed == 0`. I re-derived this from the pinned clone: the
`sender->slaveof = master` assignment sits inside `if (master && sender->slaveof != master)`, and the
ping-extension call `updateShardId(sender, ext_shardid)` at `:2782` is unconditional. The finding is
real. On Sonnet, the same mechanism over the same ledger examined the same row and *strengthened* the
false refutation, calling it "structural, not probabilistic." Verifier independence of context did
not produce independence of reasoning: both Sonnet primaries and the Sonnet verifier made the
identical premise error. By the handoff's definition — extra cost with no return — the Sonnet
instance was harmful. And note where the value landed on Fable: not in the batch conclusion, which
said `clean verdict stands`, but in an aside the contract treats as non-actionable. The mechanism's
formal output has never fired; its side channel has fired once and carried the round's best result.

**N4 / G1: did `plausible` or a published question finally occur?** Questions, yes: v5a published
two, on exactly the shape G1 was built for (a benchmark claim; a browser-engine normalization
behavior), and the test-4 question was the best-calibrated handling of the one item the four runs
split on and upstream partly conceded. `plausible`, no: v5a is 0-for-5, the Skeptic line is 0-for-15
across v3–v5a. The branch is reachable — the Panel verifier returned it three times (T1 Fable once, T4
v2 twice) — but v5a's primary routes statically unresolvable items to G1 *before* verification and
drops unproven ones outright (T4's `since` tag), so the verifier never receives a candidate it could
call indeterminate. In v5a, G1 has absorbed `plausible`'s job. Handoff 1's stated bargain applies:
remove the branch from v5b's verifier vocabulary and keep the question channel. v2a keeps it; there
the finders forward question-shaped candidates and the verifier is where they resolve.

**v2a C1: recall retained and calibration fixed on target 1?** Recall, yes: post-C9, both known
drifts on both axes on both models. Calibration, one of two: the Fable run landed all four findings
`consider` and held status only by a question; the model-matched Sonnet run confirmed `P1 must-fix`
on the Narrow drift and derived `Changes Requested` — the outcome C1 exists to prevent, on the target
it was tuned for. Its verifier defended the call from `finding-format.md`'s own text (an executed
skill step is an authoritative execution path). The decoupling *mechanism* works — the same run
published a `P1 consider` and test 4 published a `P2 must-fix` — but the intent ("non-blocking band on
target 1") reproduced on one model of two. See §4 and §5.

### Notes on the other cells

- **G1 did not carry the item the checklist predicted.** The `condvar_mutex`-saturation question v2
  and v2a asked on tokio never appeared in v5a's ledger; v5a asked a different, also-good question.
  Channel parity with the Panel is real; item parity is not.
- **N1 sometimes absorbs a finding.** On test 1 the commerce-only timestamp regex went to
  Observations; v2 had published it at `P2 consider` and the Fable v2a verifier confirmed it at P2. On
  tokio the verifier's dead-notify-counter aside was folded into the finding because the three slots
  were full. The cap and the "fails only on consequence" rule are doing what they say, but the channel
  is where v5a's lowest-priority real findings now go to die quietly.
- **F1 has two new gaps** the runs surfaced: the G3 trigger says "zero candidates survive" and an
  Observations-routed candidate is neither a survivor nor dropped (test 2 Sonnet, recorded under G5);
  and the digest is only reproducible across runs given verbatim issue comments, which test 3's packet
  summarized (`comments: []`).
- **F2 depends on the packet.** Test 4's packet never stated the merged state, so neither patched
  prototype ran in retrospective mode. The rule is fine; phase-1 output needs a `merged` field.

## 3. Scorecard — v2a (C1–C9, pole intact)

| ID | Change | T1 pre-C9 (S) | T1 post-C9 (S) | T1 post-C9 (F) | T2 (S) | T2 (F) | T3 (S) | T4 (S, holdout) | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | Action decoupled from priority | 1 finding `P3 consider`, Approved (recall ½) | `P1 must-fix`, `P1 consider`, `P3 consider` → **Changes Requested** | 4 × `consider` → Needs Information (question) | n/a (0 candidates) | real failover gap at `P2 consider`, Approved | `P2 must-fix`, proportionate | `P2 must-fix`, 2 × `P3 consider` | **partially worked** — fields decouple; target-1 intent met on one model of two; T2 Fable under-blocked |
| C2 | No-issue rule: body claims and non-goals | n/a | n/a | n/a | **fired** — 11 claims, all "met", one on a false acquittal ([run §6b](prototype-runs-2026-09-01-test-2/v2a-run.md)) | **fired** — 16-row ledger, 2 questions, found the defect through claim A8 ([run](prototype-runs-2026-09-01-test-2-fable/v2a-run.md)) | n/a | n/a | **worked** (2 of 2) |
| C3 | Structured disposition ledger, both finders | fired | Code 20 rows; **Requirements not in required shape** | 29 + 22 rows | 11 + 12 rows | 21 + 24 rows | 11 + 9 rows; made the false acquittal legible | 13 + 11 rows | **worked** (6½ of 7); needs mechanical enforcement |
| C4 | Question routing by rule | none | none | (question arrived via `plausible`, not C4) | none | **fired** ×2 (lineage, timing) | **fired** — residual `condvar_mutex` | none (v2, its ancestor, published 2 on this target) | **worked**; one T2 question is offline-artifact-shaped |
| C5 | Observations section | fired | 10 raised / 3 publish | 12 / 3 | 2 (and `redis.conf` appeared nowhere) | 9 / 3; `redis.conf` as both a P3 finding and an observation | 9 / 3 | 5 / 3, cap forced 2 accurate verifier asides out | **worked**; no cross-axis dedup, cap binds |
| C6 | Retrospective mode + trailer parity | fired | fired | fired | fired | fired | fired | retrospective half not invoked (packet); trailers full-SHA `v2a-1` | **worked** |
| C7 | Token efficiency around the pole | — | children 272,657 vs v2's 253,712 (different model) | interrupted | — | interrupted | — | **222,873 vs v2's 198,466** in the one clean cohort | **inert — not demonstrated**; cost rose |
| C8 | Paired peer-contract sweep | **fired** — bundle item found | fired, both axes | fired, both axes | correct negative | correct negative | correct negative | correct negative | **worked** |
| C9 | Changed-contract scan; Code-axis sync drift | (pre-C9) | **fired** — Narrow item from absent to both axes, model-matched ([addendum](prototype-runs-2026-09-01-test-1/addendum-2026-09-03.md)) | fired; also the validator regex | correct negative | correct negative | correct negative | **fired on holdout** — Code axis found GT-3 via the `addCookies` control, which v2 acquitted ([run](prototype-runs-2026-09-01-test-4/v2a-run.md)) | **worked** — the strongest evidence of the round |
| Pole | Two finders, verify every candidate, `support` withheld | intact | intact | intact (serial after interruption) | **verifier skipped by rule** — the designed exception, on the run with the false acquittal | intact | intact | intact | held, with one designed hole |

Two things the table cannot show:

- **C9 is the only change with a controlled before/after and a holdout hit.** The Sonnet pair on
  target 1 moves only the skill commit; the Narrow item goes from absent in both ledgers to raised on
  both axes, and the mechanism is visible in the output (the changed-contract list, the old-fragment
  sweep). Test 4's GT-3 is the same mechanism on a generated-file/doc pair the design never
  anticipated. It also has a documented miss: the Sonnet post-C9 run's reported old-fragment search
  should have matched `validate-completion.py:2949` and its hit list does not include it.
- **The Code axis is the weaker arm on three targets and the decisive one on two.** It returned zero
  candidates on test 2 Fable, missed the regex on test 1 both times, and acquitted the tokio ground
  truth; it found GT-3 on test 4 and the `WouldBlock` arm on test 3. The Requirements axis found the
  redis defect (through a body claim), the regex, and the AC4 question — and on test 4 returned
  `Passed, 7/7, 0 questions` on an API deleted 24 days later, where v2's Requirements axis had at least
  asked whether domain/path filters exceeded the issue.

## 4. The pole comparison

Is v2a still earning its comparator slot? Measured per target, v5a against v2a, same model.

| Target (model) | Items v2a found that v5a missed | Items v5a found that v2a missed | Question / observation parity | Cost ratio v2a : v5a |
| --- | --- | --- | --- | --- |
| 1 (Sonnet) | bundle drift `search-bundle-format.md:208`; Research-skill add-only wording | none | v2a 0 Q / 10 obs; v5a 0 Q / 2 obs | ~3.0× (490,906 all agents vs 160,853 outer total; meters differ) |
| 1 (Fable v2a only) | plus validator regex as a finding, AC4 question | — | — | not cost data |
| 2 (Sonnet) | none (both 0) | none | v2a 0 Q / 2 obs; v5a 0 Q / 2 obs incl. `redis.conf` | 1.23× (317,807 vs 257,473, primaries metered) |
| 2 (Fable) | `redis.conf` as a P3 finding; 2 questions | the defect at `must-fix` (v2a had it at `consider`) | v2a 2 Q; v5a 0 Q | not cost data |
| 3 (Sonnet) | `WouldBlock` arm stranding; `condvar_mutex` question | **the shipped regression** (v2a acquitted it) | 1 Q each; 3 obs each | 1.77× (491,450 vs 276,985, primaries metered) |
| 4 (Sonnet, holdout) | only the `since: v1.43` false positive | domain-match question; correct drop of the false positive | v2a 0 Q / 3 obs; v5a 1 Q / 1 obs | metered sub-agents 5.0× (222,873 vs 44,198, v5a primary unmetered); tool uses ~1.2× (~123 vs ~100) |

What was and wasn't metered: on tests 2 and 3 the harness metered both prototypes' primaries and
children, so those two ratios are the cleanest the program has — the Panel costs 1.2–1.8× the Skeptic
on the same model. Test 4's token ratio is inflated by v5a's unmetered primary; its tool-use ratio is
on the same basis for all four runs. Test 1's Sonnet figures mix an orchestrator-plus-children sum
against an outer-wrapper total.

**The retirement condition** — "when v5a-with-grafts stops losing recall to v2a across an
adjudicated set, v2a retires" — is **partially met and not yet testable**. On tests 3 and 4, v5a lost
nothing real to v2a (the `WouldBlock` arm is real but v5a's pre-existing drop is a defensible reading
the program has not adjudicated; §7). On test 1 v5a still loses two real drifts. Test 2 is a tie on
Sonnet and a split on Fable (v2a's extra items are a doc-scope finding and two questions; v5a's is the
correct action on the defect). One holdout target at n = 1 cannot settle a condition phrased "across
an adjudicated set." v2a stays.

Channel parity is now real: v5a publishes questions and observations at comparable rates. The
architectural distance the comparator exists to preserve is also intact — nothing in v2a's runs
converged toward consequence-triggered verification, and the two prototypes disagreed in
instructive ways on every target (§7).

## 5. Regression watch

Each patched prototype against its own ancestor, per target, losses only, most severe first. Every
cross-cohort comparison here is directional: the ancestors ran on Opus 5 (test 1), GLM (test 2), and
default-model Sonnet with an untruncated mirror (test 3); only test 4 is like for like.

1. **v2a acquitted the tokio ground truth that v2 found.** v2 implicated both unguarded branches at
   P1 on this target; v2a's Code finder examined the same two branches and acquitted them on the
   premise that a worker whose counters still look available has not yet drained — the reverse of the
   code's ordering (`pool.rs:542` before `:562-567` before `:570`). This is v3's test-3 error
   reproduced by the Panel line. Neither C-change touches concurrency tracing, so it is not a change
   that broke, but it is the most serious recall loss in the corpus, and nothing in the architecture
   could catch it: acquittals never reach the verifier, and a candidate survived, so no ledger-wide
   check would have fired in either line.
2. **v5a lost v5's best behavior on test 1.** v5's verifier confirmed the Narrow fact and disproved
   its merge consequence, moving the run to Approved without erasing the finding — the verdict shape
   the prior analysis called the program's single best verifier moment. v5a's verifier confirmed
   `P2 must-fix` as proposed, and the run derived `Changes Requested` on the author-adjudicated
   approvable change. v5a also missed the bundle drift v5 found at P3 and routed the regex to
   Observations. Directional (Opus → Sonnet), but the addendum's own regression watch already records
   that half of six pre-fix Sonnet replicates published zero findings on this target, so the model
   tier is at least half the story.
3. **v2a's calibration regressed on the model-matched run.** The pre-C9 Sonnet run had the one drift
   it found at `P3 consider`; the post-C9 Sonnet run has the Narrow drift at `P1 must-fix` and the
   bundle drift at `P1 consider`. Priority inflated on both, action inflated on one. C1's
   "priority must not be inflated to communicate action" rule did not hold under verification.
4. **v5a's clean path got more expensive on high-risk clean diffs, and once paid for nothing.**
   On test 2 Sonnet, v5 ran no verifier and v5a ran a 69,277-token clean-verdict batch that agreed
   with the error. The design accepts this cost on the high-risk ∩ zero-survivor intersection; the
   run shows the intersection is not rare on the targets this program picks and the return is not
   guaranteed.
5. **v2a's Requirements axis became more confident and less useful on test 4.** v2 returned
   `Waiting for information` with two questions, one of them ("domain/path filter dimensions exceed
   'remove a specific cookie'") the closest any run came to GT-2 from the requirements side. v2a
   returned `Passed, 7/7, 0 questions` and acquitted the same scope item.
6. **Sub-threshold loss on test 2 Sonnet.** The `redis.conf` scope item — v2's finder noted it,
   both Fable runs carried it, v5a Sonnet published it as an observation — appears nowhere in v2a
   Sonnet's output. C5 provides the channel; it does not guarantee the fact reaches it.
7. **Both patched prototypes cost more than their ancestors** in the one clean cohort: v2a 12% more
   metered tokens than v2, v5a 23% more verifier tokens and ~60% more tool uses than v5. Small, and
   partly bought real things (GT-3, the question, the false-positive drop), but C7 promised the
   opposite direction.
8. **v2a's C3 output shape is not enforced.** The Sonnet post-C9 Requirements finder returned prose;
   the orchestrator refused to fabricate rows. A ledger that a finder can decline to produce is an
   audit asset only when it exists.
9. **Coverage and verification discipline held everywhere.** Both prototypes reviewed every file on
   every target, no recovery rounds, no partial statuses; v2a verified every candidate it raised and
   its verifier refuted (T3, a fabricated issue quotation) and caught a fabricated line citation (T4,
   its ancestor); v5a's verifier corrected a remedy on all three concurrency findings. Nothing in that
   column regressed.

## 6. The Fable rounds, treated as data

The user asked that the Fable runs be included rather than quarantined. They are the only cases where
one skill, packet, and clone were run at two model tiers, so they are the program's only variance
evidence, and it is stark.

| Same skill, same target | Sonnet 5 | Fable 5.1 |
| --- | --- | --- |
| v2a on test 1 (post-C9) | 3 findings, no question, `Changes Requested` | 4 findings incl. the validator regex, AC4 `plausible` → question, `Needs Information` |
| v2a on test 2 | 0 findings, defect acquitted, verifier skipped | 2 findings incl. the defect at `P2 consider`, 2 questions, `Approved` |
| v5a on test 2 | 0 findings, defect refuted, G3 upheld the refutation | 1 finding, the defect at `P2 must-fix`, `Changes Requested` |

Three conclusions survive the caveat that each cell is one run:

- **A single clean run is weak evidence of absence.** Test 2 was "clean" through six runs at two
  model tiers and a human approval before the Fable round found the defect. Both Sonnet runs reached
  the right hypothesis and killed it on the same false premise.
- **Model changes move calibration as much as recall.** The Narrow drift was `consider` on Fable and
  `must-fix` on Sonnet under the same v2a commit; the redis defect was `consider` under v2a and
  `must-fix` under v5a on the same model.
- **Same-model replication would not have caught the test-2 miss.** The two Sonnet prototypes,
  different architectures, made the identical error. Cross-model replication did catch it. This
  bears directly on the third direction (§8).

The Fable data cannot rank models: on tokio, Sonnet v5a found the shipped defect; on redis it missed
it; every Fable run was rate-limit-interrupted. The test-2 Fable finding stands on its verifiers and
on my re-derivation, not on the model.

## 7. Cross-cutting conclusions, revisited

The prior analysis's nine, with the new corpus.

1. **Facts converge; calibration is the variable — strengthened.** The Narrow drift now spans
   `P1 must-fix` to `P3 consider` across eight runs; the redis defect drew opposite actions from two
   prototypes at the same priority; the playwright race drew P1 and P2 from four runs that agreed on
   every fact. New: calibration also moves with the model under a fixed skill (§6).
2. **Fresh verification earns its cost, `plausible` is dead — half resolved.** `plausible` fired three
   times, all in the Panel line, so the vocabulary is live there and dead in the Skeptic line, where
   G1 has taken its job (§2). New: the corpus now holds a verifier that confirmed a false premise
   (T2 Sonnet v5a). Context isolation is not reasoning independence, and the verifier brief needs an
   adversarial task — attack the weakest premise, take the opposite branch of every conditional the
   acquittal relies on — not just "re-derive."
3. **Test 3's fix-sufficiency gap — partly closed, and the ceiling is now visible.** N2 works as a
   sibling-path enumerator. It does not ask whether the named invariant explains the bug class, and on
   tokio it did not (§2). Two blind runs on the truncated mirror each found a different projection of
   the same broken accounting invariant (v5a the shutdown orphan, v2a the `WouldBlock` strand); the
   re-land fixed the invariant. The program has still never produced the incident's fix blind.
4. **Every architecture loses accurate sub-threshold observations — resolved.** Both prototypes now
   carry them; the `redis.conf` item landed in an Observations section in three of four runs that had
   one. The residual is a cap that binds (T3, T4) and a channel that can swallow a finding (§2, N1).
5. **Clean verdicts are structurally unverified — partly addressed, and the gap moved.** G3 exists
   and has fired. Its formal output never has. And the case that mattered on test 3 — a false
   acquittal beside a true survivor — is outside G3's trigger in v5a and outside the verifier's input in
   v2a. The general statement: **verification sees candidates, not beliefs.** Every false acquittal in
   this corpus (T2 ×3, T3 ×1) lived in a ledger row no verifier was asked to attack, or was attacked
   by a verifier that was asked to re-derive rather than to refute.
6. **The ledger is a re-review asset — strengthened.** Every false acquittal above is quotable
   because the ledger exists. The one run where a finder skipped the ledger shape (T1 Sonnet v2a
   Requirements) is the one whose search process cannot be audited from its output.
7. **Anchor/fix separation and base-branch acquittal — proven, with one open rule.** G2's finding
   with its fix in an unchanged file is the cleanest demonstration yet. But tokio's `WouldBlock` arm is
   byte-identical at base and its safety argument was broken by this diff; v2a's verifier called that
   introduced-here and v5a dropped it as pre-existing. Both readings are defensible under their own
   text. The program needs a rule for unchanged code whose invariant the diff changed.
8. **Economics — first clean numbers.** In the test-4 cohort the Panel line spends 4–6× the
   Skeptic line's metered sub-agent tokens and ~1.2× its tool uses; on the two Sonnet targets where
   both primaries were metered, 1.2–1.8×. On test 4 the premium bought one false positive and no
   recall the cheaper line lacked; on test 1 it bought two real drifts; on test 3 it bought a real
   sibling finding and a good question while missing the ground truth.
9. **Methodology debts — two paid, three new.** Mirror truncation and the closed-PR rule are done
   and worked (test 3's contamination is closed; retrospective mode ran on three targets). Model is now
   passed explicitly and verified from transcripts. New debts: rate limits destroyed unsaved phases in
   three rounds and split the test-4 Panel runs across orchestrator contexts; a paused orchestrator
   cannot see its children, so the session relayed results (disclosed, unavoidable, still a
   condition difference); and the model drift that produced the Fable rounds was found by accident.
   Still never exercised: re-review over prior threads, stale-head abort, gating events, G4.

New conclusions, each with run-record evidence:

10. **Unanimity is not accuracy, in either direction.** Six runs approved a defective redis change.
    Four runs blocked on a playwright race upstream declined to fix, and split four ways on the item
    upstream partly conceded. Cross-architecture agreement measures shared priors.
11. **What counts as terminal evidence is the calibration lever nobody tuned.** v2 acquitted GT-3
    because "CI would catch it" on a diff where CI had not. v5a dropped GT-2 because the maintainer
    approved it, holding the maintainer's own "we can fix it during the pre-release api review" in the
    packet. v5a correctly dropped the `since` tag because it could not be proven. The same evidentiary
    gate produced the round's best and worst dispositions; the difference was whether approval and
    tooling were treated as closure.
12. **New test files are not reviewed as code.** GT-1 (eight tests hitting the live internet with an
    unused `server` fixture in every signature) was missed by four runs that all read the file and
    three of which had the flake quoted in their packet. No skill says a test file has its own
    standards.
13. **The Panel's verifier catches fabrication; the Skeptic's catches wrong remedies.** v2a's
    verifier refuted a candidate on a quotation that does not exist in the issue and corrected a line
    citation into a 231-line file from `435-454` to `212-230`. v5a's verifier changed the published
    `change` on all three concurrency findings. Both are the claim/support split working; they are
    different jobs, and the comparator is still the only place the first one is exercised.

## 8. Recommendation

### v5a is confirmed as the advancing line, as v5b

The case, stated with the caveats attached: on the one holdout target v5a was the best run — no false
findings, the only correct drop of the false positive, the only question, and the nearest approach to
the API-shape problem; on tokio it found the shipped defect blind and its verifier generalized the fix
further than any uncontaminated run before it; on redis at the Fable tier its G3 → N3 chain converted
a clean verdict into the right one; F1 held across models. Against that: it over-blocked test 1, its
G3 agreed with an error on redis Sonnet, and N2's ceiling is now known. None of that is a design
error worth reverting. Build v5b with these changes, in priority order:

1. **Widen the G3 trigger and harden its brief.** Fire the ledger batch when a high-risk surface has
   *any* refuted or dropped candidate of kind `concurrency`/`invariant`/`bug` on the same invariant as
   a survivor, not only at zero survivors (T3's shape). Require the batch to attack the weakest
   premise of each acquittal and to trace the opposite branch of every conditional it relies on
   (T2 Sonnet's failure). Give it a formal `reopen` output for an aside that contradicts a disposition
   premise, so the round's best result stops arriving through a channel the contract calls
   non-actionable (T2 Fable).
2. **Change N2's enumeration question.** For concurrency kinds, the verifier must state whether the
   failing interleaving requires shutdown or teardown, name the invariant at the level of the
   accounting or ownership rule that changed (not the transition it was observed in), and enumerate
   sibling *interleavings* of that rule — spawn-vs-idle, spawn-vs-exit, spawn-vs-shutdown — before
   sibling code paths. Tokio's re-land is the reference shape.
3. **Delete `plausible` from the verifier vocabulary**, per handoff 1's bargain; keep G1. Add a
   test target that forces the question route so G1 is exercised on purpose rather than by luck.
4. **Approval is not closure on unreleased public API.** An explicit deferral in the review record
   ("we can fix it during the pre-release api review") reopens the API-shape question; gate 6
   (unintentional) must not treat a maintainer's approval as terminal on surface that has not shipped.
5. **A new or changed test file is code under review**, with the repository's test conventions as
   the standard: fixture use, network access, per-language snippets where the file generates them.
6. **An introduced-here rule for unchanged code whose invariant changed**: compare the relied-on
   invariant at base and head; if the diff made a previously safe unchanged path unsafe, it is
   introduced here.
7. **Contract fixes:** the G3 trigger wording ("zero finding-survivors"); a `merged` field in phase-1
   output so F2 keys off the packet, not the reviewer's inference; digest input records
   `comments: unavailable` rather than `[]` when a packet summarizes them.
8. **Observations must not absorb findings:** an item a verifier has confirmed at any priority is a
   finding, and a full cap defers an item to the run record rather than folding it into another finding.

### v2a stays the comparator, with three repairs and one retirement condition

Keep v2a. It still finds real things v5a misses (test 1's bundle drift and Research wording, tokio's
`WouldBlock` arm, the redis doc-scope item as a finding), still owns the verifier that refutes and
catches fabrication, and still produces a different projection of every shared defect. Repairs, none
of which converge on the Skeptic line:

- enforce C3 mechanically (a validator for the ledger shape, as v5a has for its output);
- re-examine C1's calibration text against the Sonnet post-C9 run — `P1 consider` and `must-fix` on
  a doc restatement violate the rule's own "priority must not be inflated" sentence;
- send high-risk acquittals on the same invariant as any candidate to the mandatory verifier. The
  pole's identity is verify-everything; verifying acquittals extends it rather than diluting it.

Retire v2a when, on a holdout set of at least four adjudicated targets with at least three seeds per
cell on one model, v5b's union recall over adjudicated true items is at least v2a's, and v2a produces
no unique true item on more than one target. Test 4 at n = 1 is one data point toward that; test 1 is
one against it.

### The holdout demand

All four targets are now development-set for every living prototype except v2 and v5 on test 4. The
prior analysis's protocol items still unmet: repeated seeds; a forced `plausible`/question target; a
requirements-omission-in-unchanged-file target; the re-review/stale-head/gating surface; a controlled
model-tier comparison. Test 4 met the truncated-mirror, explicit-model, and single-cohort items. The
next experiment, concretely:

**Targets (six, none seen by any prototype's design).** (a) A merged concurrency PR with a later
revert whose corrected re-land restores an invariant rather than patching a branch — tokio's shape in
a different repository, scored on whether the published fix names that invariant. (b) A high-risk
merged PR adjudicated clean by executing its tests, to measure G3's false-reopen rate. (c) A PR whose
originating issue requires updating a file the diff never touches. (d) An API addition with an
explicit deferral in its review record and a later withdrawal — playwright's shape. (e) A PR whose
body makes a benchmark claim no static reading can settle, to force G1 and, in v2a, `plausible`. (f)
One target reviewed twice: first review, then re-review against posted threads with a moved head, to
exercise the surface no run has touched.

**Conditions.** One model (Sonnet 5) passed explicitly on every agent and verified from every
transcript before scoring; three seeds per prototype per target; mirrors truncated with negative
object checks recorded per clone; packets carrying a `merged` field and verbatim issue comments;
every run instructed to persist its expensive phase before dispatching a verifier; no session relays
(dispatch runs with enough budget to finish). Arms: v5b, v2a, v5b-without-verifier as the v3 ablation.
After the Sonnet grid is complete and only then, one target (b) or (e) re-run with Fable 5.1 on the
verifier only, then on the primary only, to test the tier split the prior analysis proposed.

**Scoring, per run, four dimensions kept separate:** adjudicated ground-truth recall; false findings
and false acquittals, both counted; action calibration against an adjudicated band; fix sufficiency
at the invariant level for concurrency targets. Plus cost with primaries metered.

**What counts as success for v5b.** Zero false findings across eighteen runs; the widened G3
re-opens the seeded false acquittal on target (b)'s sibling (a run with one true survivor and one
false acquittal on the same invariant) in at least two of three seeds; the published fix on target (a)
names the re-land's invariant in at least two of three seeds; G1 fires on target (e) in every seed;
recall on targets (c) and (d) at least matches v2a's. Anything less on the first two items says the
verification design, not the reviewer, is still the bottleneck.

### The third direction: build it, cross-model

The prior analysis proposed replicated primaries with reconciliation. The new runs strengthen the
case on every count it named, and change its shape on one:

- Hidden cross-run disagreement recurred: test 2 Sonnet, both prototypes wrong on the same row with
  no artifact confronting them; test 3, v2a's acquittal of the exact branches v5a's candidate named —
  a reconciler holding both ledgers would have routed that contradiction to verification mechanically.
- Single-projection findings recurred: two different projections of tokio's broken invariant, four
  dispositions of playwright's domain-match claim.
- v5a's channels captured some of what replication would have (the domain question, the
  `redis.conf` observation) but none of the above.
- **Same-model replication would not have caught test 2.** Two Sonnet primaries of different
  architecture made the identical false premise. The one thing that found the defect was a different
  model tier. So the replicated primary should be cross-tier by default — one Sonnet, one Fable —
  with ledger reconciliation routing every disagreement to the widened G3 batch. Cost is bounded at
  roughly the Panel's premium and belongs on the high-risk escalation path, where the two rounds
  above say the frequent path's clean verdicts are least trustworthy.

Build it after v5b's grid, not instead of it; the grid is what tells you whether reconciliation is
finding real disagreement or noise.

## 9. Where this analysis disagrees with lower-level documents

- **Test-3 addendum and evaluation** say v5a's corrected fix "is the shape of the eventual
  real-world correction" and "the shape the real correction required." Reading `8b13642a` in the
  untruncated mirror: the re-land seals shards for shutdown (v5a's fix matches this half) *and* puts
  the claim-or-spawn decision and the idle transition under one coordination lock with a re-check
  before idling (v5a's fix does not). The production hang is the second half. N2 generalized within
  the shutdown projection; it did not reach the invariant the incident broke.
- **Test-2 addendum (2026-09-03)** headline table lists the Fable v5a finding as `P1 must-fix`. The
  Fable run record, its evaluation, and its comparison data all say `P2 must-fix`. P2 is correct.
- **Test-2 Fable evaluation** says v5a's action was better calibrated than v2a's `consider`. I agree
  on the action, and add that the Sonnet v2a and v5a runs' identical false premise is the more
  transferable fact from that target than either Fable run's calibration.
- **Test-1 addendum (2026-09-02)** described the validator regex and AC4 carrier as new to the Fable
  run; the test-1 evaluation and comparison data already correct this against v2's original record
  (F3, F4). This document counts them as independent rediscoveries.
- **Test-1 evaluation** reads v5a's repo-wide peer sweep as a "targeted discovery success." I agree
  and add that the same run lost v5's action-recalibrating verifier behavior on the same item, which
  the evaluation records but does not weigh as a regression.
- **Test-4 evaluation** ranks v5a first and credits N2 with the remedy correction. v5's verifier,
  which has no N2 brief, made the same correction on the same candidate. On that target N2's marginal
  contribution is not separable from the base verifier's; the tokio and redis runs are where N2 did
  something v5 did not.
- **Test-2 Sonnet addendum** records G3 as having "fired and confirmed an error." Under the
  handoff's own scoring vocabulary that instance is harmful (cost, no return), and the scorecard says
  so rather than calling it inert.
- **Test-3 v2a run record** calls its `WouldBlock` finding "this target's ground-truth defect" in
  its C1 answer. The addendum and evaluation correctly do not; this document follows them.

## 10. Limits

- Every quality claim about v2a and v5a on tests 1–3 is development-set. Test 4 is one holdout
  run per prototype.
- n = 1 per cell everywhere except the three same-skill model pairs, which are the only variance
  data and were interrupted on the Fable side.
- Cost is comparable only within test 4 and, with metering caveats, within tests 2 and 3 on Sonnet.
- No run executed a build, test, loom, or Tcl suite on any target; every concurrency claim,
  including my re-derivations, is static.
- The tokio re-land was read from a staging mirror the runs could not reach; its description here is
  my reading of its comments and structure, not an execution.
- The test-2 defect has two independent primaries, three verifier traces, and one re-derivation
  behind it, and no dynamic reproduction.
