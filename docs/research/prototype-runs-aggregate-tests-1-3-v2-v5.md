# Aggregate analysis — code-review prototypes v2–v5 across the three 2026-09-01 test runs

> **Scope.** Tests 1–3 only, prototypes v2–v5, the first twelve runs. This is the earlier of the two
> aggregate analyses. The later one —
> [`prototype-runs-aggregate-tests-1-4-v2a-v5a.md`](prototype-runs-aggregate-tests-1-4-v2a-v5a.md) —
> covers all four tests and all twenty-six runs and grades the patched prototypes v2a and v5a. Read
> that one for the current picture; read this one for the contract the patched prototypes were built
> against.

> **Naming status.** “v5” is the historical prototype name used by this record. PR #17 promoted that
> workflow to `skills/code-review-publish`; **PR #42 (2026-09-03) then replaced it there with v5a**,
> so `/code-review-publish` now invokes v5a, `skills/code-review-publish-legacy` is the v1 legacy
> reviewer, and v5 itself is no longer present on `main` (pin it from `571f31d` if needed).

**2026-09-01.** Synthesis of the three controlled comparisons of `code-review-publish-2` through
`code-review-publish-5`:

- [test 1](prototype-runs-2026-09-01-test-1/) — `kamui/shortlist#66`, a documentation/schema PR in
  the reviewer author's own repository, with an originating issue and two real doc-sync drifts
- [test 2](prototype-runs-2026-09-01-test-2/) — `redis/redis#15680`, a merged, expertly reviewed C
  concurrency PR with no originating issue and no known defect
- [test 3](prototype-runs-2026-09-01-test-3/) — `tokio-rs/tokio#7757`, a merged Rust PR with a
  ground-truth production regression (hang → emergency revert → corrected re-land)

This document draws its own conclusions from the raw run records (`v*-run.md`), not only from the
per-test evaluations; where it disagrees with or extends a per-test evaluation, it says so
explicitly. It ends with a recommendation: which prototype to advance, what to graft onto it from
the other three, and what new changes the runs collectively motivate.

## The experiment grid

| | Test 1 | Test 2 | Test 3 |
| --- | --- | --- | --- |
| Target character | doc/schema change, 9 files +160/−6 | C cluster/replication change, 5 files +401/−1 | Rust runtime concurrency change, 6 files +340/−126 |
| Originating issue | yes, 10 acceptance criteria | **none** | yes (#2528) |
| Prior review state | none (first review) | approval + technical LGTM | 52 threads, approval, one unresolved design concern |
| Ground truth | two real drifts (author-adjudicated) | none (merged clean is evidence, not proof) | **real shipped regression, independently confirmed** |
| Model / harness | Claude Opus 5 (1M), Claude Code | GLM-5.3-Flash, opencode | Claude Sonnet 5, Claude Code |
| Token data | full, comparable | none | partial (see [Economics](#economics-what-the-cost-data-actually-supports)) |
| What it discriminates | calibration, verifier behavior | restraint on clean code, no-issue path | recall on a real defect, blind severity |

Model and harness were held constant *within* each test, so every four-way comparison is internally
valid; they changed *between* tests, so no cross-test difference can be attributed to the prototypes
alone.

The four architectures under test:

| | v2 (PR #14) | v3 (PR #13) | v4 (PR #16) | v5 (PR #17) |
| --- | --- | --- | --- | --- |
| Shape | 2 parallel axis finders (Code, Requirements) + mandatory fresh-context verifier | 1 integrated reviewer, self-falsification, conditional verifier | 1 integrated reviewer + conditional fresh-context verifier | 1 integrated reviewer + consequence-triggered fresh-context verifier |
| Verifier trigger | every candidate (skipped only when finders return none) | high-risk/large/coupled change or difficult high-impact claim | every `must-fix` plus named high-risk/contract categories | every `must-fix` plus enumerated consequential risks; artifact names alone never trigger |

## Aggregate outcomes

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Test 1 findings / status | 4 (2 blocking) / **Changes Requested** | 1 blocking / **Changes Requested** | 2 `consider` / Approved | 2 `consider` / Approved |
| Test 2 findings / status | 0 / Approved | 0 / Approved | 0 / Approved | 0 / Approved |
| Test 3 findings / status | 2 (1 must-fix P1, 1 P2) + 1 question / Changes Requested | 1 must-fix P1 / Changes Requested | 1 must-fix **P0** / Changes Requested | 1 must-fix P1 / Changes Requested |
| Published findings, total | 6 + 1 question | 2 | 3 | 3 |
| Outright false findings published | 0 | 0 | 0 | 0 |
| Checkable factual errors in published analysis | 0 | **1** (test 3 "self-healing" dismissal) | 0 | 0 |
| Verifier fired (of 3 tests) | 2 | 1 | 2 | 2 |
| `plausible` verdicts across all runs | 0 | 0 | 0 | 0 |

Two headline facts frame everything below:

1. **No prototype ever manufactured a finding.** Twelve runs, three very different targets, 29
   candidates raised and unanimously killed on the clean redis PR — and zero published findings that
   turned out to be fabricated. The observed failure modes are *calibration* (real facts, wrong
   severity/action — v2 and v3 in test 1) and *false reassurance* (a wrong "checked, cleared" claim —
   v3 in test 3), never invention.
2. **All four caught the tokio regression that 52 human review threads and an approval missed**, from
   a static pass over the merge-base diff, with builds/tests/loom forbidden. Whatever else separates
   these architectures, the shared core (falsification-gated candidates, evidence-cited claims,
   fresh-context verification of consequential findings) is doing real work.

## Prototype-by-prototype: aggregated pros and cons

### v2 — parallel axis finders + mandatory verifier

**Pros**

- **Highest recall across all three tests.** Widest finding set in test 1; the only run in test 3 to
  publish a second, independently confirmed finding (mandatory work run on the caller's thread —
  real, distinct, and confirmed by its verifier) that the three integrated architectures never
  mention checking.
- **The only architecture with a channel for open questions.** Its Requirements axis produced the
  single published author-facing question across all twelve runs (test 3: does the non-sharded
  `condvar_mutex` cap scalability past 16 threads?) — a genuinely valuable item no other prototype
  could have surfaced at all.
- Its verifier is the only one that ever *refuted* candidates in a run where others confirmed
  (test 1: two false candidates removed, one cross-axis duplicate merged), and its
  `verify.md` carries the correct Requirements-candidate exception to the "introduced here" gate
  that v3–v5 all lack.
- The run's single most careful observation in test 2 (the `redis.conf` first sentence is broader
  than the code) came from its Code finder, when three other runs affirmatively asserted the doc was
  exact.

**Cons**

- **Severity coupled to merge action.** In test 1 it turned two one-line doc drifts into P1
  `must-fix` blockers and derived `Changes Requested` on a change the author-adjudicated ground
  truth calls approvable. Priority derives action in its rubric; this is a design flaw, not a bad
  day.
- **Degenerates on issueless PRs.** Its no-issue rule makes the Requirements axis `Not applicable`,
  silently deleting half the architecture (test 2); the body-claims check that substituted happened
  by finder initiative, not by rule.
- **Prose falsification records.** Its finders report narrative, not a per-candidate disposition
  ledger — the worst substrate for re-review continuity of the four.
- Most expensive shape where clean comparison exists (test 1: 253.7k tokens, 1.45× v4/v5, 2.3× v3),
  and its parallel finders duplicate the whole-diff context pass.

### v3 — single integrated reviewer, self-falsification

**Pros**

- **Cheapest measured run by far** (test 1: 110.6k tokens, 44% of v2, 63% of v4/v5) with complete
  coverage and the widest candidate exploration in test 2 (11 candidates, two unique, all killed
  with specific evidence).
- Introduced history-as-evidence (test 1's lockstep-commit argument, later adopted and extended by
  v5) and treats priority and blocking as independent axes.
- The most architecturally self-aware run: the only one to notice its own "high-risk change"
  verifier disjunct in test 2 and to raise the deepest design question of the program — **nothing
  ever verifies a clean verdict** — and the only one to explicitly reason through the closed-PR
  stop-rule tension in test 3.
- In test 3, its conditional verifier both corrected its mechanism framing and refuted its false
  `fastrand_n` cfg candidate — the conditional trigger fired exactly when it should have.

**Cons**

- **The one checkable factual error in any published analysis of the program.** In test 3 it
  examined the "at max threads, notify anyway" branch — the branch the production incident
  historically originated in — and cleared it as "self-healing" on a premise direct inspection
  refutes (`idle == 0` also holds when the last worker is mid-exit). Its published P1 against the
  sibling branch kept the overall status correct, but "checked, cleared" language about the actual
  root-cause site is a worse failure for an unattended reviewer than silence.
- Verification is exceptional by design, so its sole test-1 blocker shipped without a second look —
  and it was miscalibrated (P2 blocking for doc drift).
- Dropped the bundle-contract drift in test 1 that three other runs confirmed at P3; defensible for
  a high-signal reviewer, but it discards a provable drift.

### v4 — integrated reviewer + conditional verifier

**Pros**

- **The most defensible published artifact of test 1** (it was in fact published): both real drifts
  retained, both non-blocking, verifier corrections materially improved both, and its verifier
  explicitly cut an overstated impact and instructed "do not raise" the priority.
- **Best operational discipline.** The only run ever to stop and ask the orchestrator (test 1's
  unrecoverable PR-body fetch: coverage marked `incomplete`, provisional `Incomplete` status, named
  exactly what the missing input could change, addressed the question to the orchestrator rather
  than the author) and the only one to flag an ambiguous policy call (whether `SKILL.md` files are a
  "public contract") instead of silently resolving it.
- Most complete requirement ledger on the issueless PR (test 2: nine body claims plus the explicit
  non-goal, each cited), and the only run to check integer overflow on the data-age arithmetic.
- In test 3 its verifier produced the most upstream-accurate fix guidance of any report — though see
  the contamination caveat.

**Cons**

- **Hindsight contamination in test 3.** A routine `git log --all` surfaced the real revert history;
  v4 used it candidly and legitimately under its own rubric, but its P0 (versus everyone else's P1)
  and its upstream-matching fix rewrite were reached with the answer key open. Nothing from that run
  can be credited to the architecture's calibration.
- **Its one-batch verifier rule cost it a real finding.** In test 3 it independently noticed the
  unguarded-notify-branches shutdown gap (the very thing v2 and v5 published) *after* dispatching
  its single verifier batch, and — correctly following its own rule that an unverified `must-fix`
  cannot publish — dropped it to a note. The skill design, not the reviewer, forced a known-real
  candidate off the review.
- Needed a coverage-recovery round in test 1 that v5 avoided, and its "public/external contract"
  verification trigger was ambiguous enough to require an escalation (good behavior, bad rule).

### v5 — integrated reviewer + consequence-triggered verifier

**Pros**

- **The only verifier behavior across the program that changed an outcome without erasing a
  finding.** Test 1: primary proposed P2 `must-fix`, verifier confirmed the fact but disproved the
  merge consequence, downgraded across the blocking boundary to P3 `consider`, replaced a weak
  trigger example with the decisive `policy terms` fact — moving the run from Changes Requested to
  Approved while keeping the finding published. That verdict shape (fact confirmed, action
  recalibrated) is exactly what a binary confirm/refute court cannot express.
- **Cleanest blind replication of the tokio defect.** Matched the branch identification and
  interleaving without touching post-merge history; its verifier did the most additional
  falsification work of any uncontaminated run (proving neither adjacent loom test models the
  interleaving, for two different specific reasons).
- Best epistemic hygiene habits: coverage caveat attached at the point of the licensing claim
  (test 2, alone in this); fingerprint-input classification recorded as an explicit ambiguity;
  primary re-verified verifier-supplied facts before citing them and recorded a contestable point
  in a correction it accepted; acquitted one test-1 candidate pre-candidate by executing the
  validator.
- **Self-diagnosing.** Its test-1 run reported six concrete under-specifications in its own output
  contract (digest input membership, trailer SHA width, anchor coordinate format, the circular
  `consider`-batch clause, tie-breaks, permission-sentence placement) — free skill-debugging output
  no other prototype produced.
- Matches v4's artifact quality at essentially identical cost (174.6k vs 175.8k tokens in test 1)
  with 18% fewer tool calls, complete coverage with no recovery round, and it degrades to the cheap
  single-agent path on clean PRs exactly as designed.

**Cons**

- **Development-set exposure.** v5 was designed after the v2–v4 results on test 1's exact PR; its
  test-1 performance is not holdout evidence. (Tests 2 and 3, which its design never saw, are —
  and its behavior there is consistent.)
- In test 3 its verifier confirmed the claim *and its proposed fix* without noticing the fix was
  narrower than the bug class (see the next section) — consequence-triggered verification validated
  correctness of the stated claim, not sufficiency of the remedy.
- Its test-1 P3 for the Narrow drift sits a notch below where the evidence points (P2 is defensible),
  and it was the slowest test-1 run. Its `consider`-inclusion verifier clause is circular in one
  direction, by its own report.

## Cross-cutting conclusions

### 1. Facts converge; calibration is the variable

Across all three tests, when two or more runs examined the same item they almost always agreed on
the *facts* — the twelve-item test-1 matrix, the eight-theme test-2 table, and the shared tokio
trace all show convergence on substance through different rubric vocabularies. What diverges is
severity and action: the same test-1 drift drew P1 `must-fix`, P2 blocking, P2 `consider`, and P3
`consider` from four architectures reading identical evidence; the identical tokio defect drew P0
from the contaminated run and P1 from the three blind ones. **The skill text's leverage is almost
entirely in calibration rules — action decoupled from priority, consequence-based verification
routing, "what licenses blocking" — not in finding-generation instructions.** V4 and v5 encode this;
v2 and v3 don't; that single difference explains most of the observable quality gap.

### 2. Fresh-context verification earns its cost — but part of its vocabulary is dead

The verification mechanism produced the program's best moments: two structurally different verifiers
(v3's and v4's, test 3) independently refuted the identical false cfg claim via the identical
citation — the strongest reliability evidence available for the mechanism itself; v5's verifier
recalibrated an action; v2's removed two false candidates; every verifier that fired made at least
one material correction. Withholding the primary's `support` narrative demonstrably preserved
independence.

But across **twelve runs, zero `plausible` verdicts and zero verifier-originated questions**. The
`plausible` → question path — a load-bearing branch in every prototype's design — has never
executed. Either its trigger is practically unreachable (verifiers always find decisive evidence one
way or the other) or verifiers over-commit rather than admit uncertainty. Until a run produces one,
that machinery is untested code shipped in every skill.

### 3. Test 3's deeper lesson: four projections of one defect, and a fix-sufficiency gap

The per-test evaluation says all four runs "identified the real defect." My reading of the raw
traces is sharper and less flattering: all four identified the same *structural cause* — the PR
split queue operations from idle/thread accounting that used to be atomic under one lock — but each
published a different concrete interleaving of it:

- **v2 and v5**: the *shutdown* projection (task pushed during teardown is orphaned; both proposed
  adding shutdown rechecks to the two unguarded branches).
- **v3**: the *keep-alive timeout* projection (idle worker times out and exits; reachable in normal
  operation, no shutdown needed) — v2's verifier flagged this exact path as an aside it was
  forbidden to smuggle into a verdict.
- **v4** (hindsight-corroborated): the *spawn-time stale-idle-claim* projection — a worker that has
  claimed a task is still counted idle, so a concurrent spawn notifies instead of spawning a needed
  thread; with a long-lived blocking task this deadlocks under ordinary load. This is the mechanism
  that matches the production hang (#8056) and the eventual re-land's fix.

The consequence: **v2's and v5's proposed `change` — recheck shutdown in the unguarded branches —
would not have prevented the production incident**, which requires no shutdown at all. v3's and
v4's fix shapes (restore atomicity between the accounting and the claim/decision) generalize; the
shutdown-recheck fix patches one projection. All four runs would have correctly blocked the merge
and pointed the author at the right lines, which is the review's primary job — but no blind run's
verifier asked "does this fix close the bug *class*, and are there sibling interleavings of the same
broken invariant?" That question is answerable statically (v3 and v4's traces effectively answer
it) and belongs in the verifier's brief for concurrency/invariant findings.

### 4. Every architecture loses accurate sub-threshold observations

Test 2's only real disagreement — one run found the `redis.conf` scope imprecision, three asserted
exactness — was invisible in four identical `Approved (advisory)` artifacts, because no prototype
has a channel for an accurate observation that doesn't clear the finding bar. v2's finder routed it
out-of-band to the orchestrator; v4 parked two items under "test-site observations (not findings)";
v2's verifier had to label its timeout-path insight "outside my mandate." Three independent runs
improvising the same workaround is the design telling us it's missing a bounded, explicitly
non-actionable `Observations` output section.

### 5. Clean verdicts are structurally unverified

Every architecture verifies findings; none verifies an approval. The highest-consequence output an
unattended reviewer can produce — silent `Approved` — gets no second look by construction, in all
four designs. v3's test-2 offer (run one verifier over the *falsification log* when the diff is
high-risk but the survivor list is empty) is the cheap, testable version of the fix, and it is also
the only mechanism that could have exposed test 2's hidden three-versus-one disagreement.

### 6. The structured candidate ledger is a re-review asset, not bookkeeping

v3/v4/v5's per-candidate disposition tables (claim → falsification route → evidence) are what lets a
future re-review recognize a hypothesis as already tested and killed. v2's prose finder reports
don't correlate across heads. Since frequent, unattended re-review is the stated use case, the
ledger format should be mandatory for anything that generates candidates — including any finder-
or axis-style agent that survives into the next iteration.

### 7. Anchor/fix separation and base-branch acquittal are proven, keep them

Both test-1 findings in v4 and v5 had repair sites in *unchanged* files; the anchor/fix split is the
only reason they were publishable without tripping the `introduced here` gate. And all twelve runs
used base-branch state to *acquit* candidates, not just convict — several of the best drops
(never-lockstep-peers, base-idiom fixture, pre-existing regex) rest on it. Both mechanisms carried
their weight in every test.

### 8. Economics: what the cost data actually supports

Only test 1 has clean, comparable token counts: v3 110.6k < v5 174.6k ≈ v4 175.8k < v2 253.7k, with
v4/v5 spending 27% of tokens on verification. Test 2 has no token data and wall-clock spans
uncorrelated with anything. **Test 3's "v2 cost 3–4× the others" (in its evaluation) overstates the
case**: the harness metered only directly spawned sub-agents, so v2's total includes its primary
work (the two finders) while v3/v4/v5's totals are verifier-only — their primaries went unmetered.
The honest cross-test statement is: v2's duplicated whole-diff pass costs roughly 1.5× a
single-reviewer-plus-verifier architecture when measured cleanly, and in test 3 that premium bought
one real extra finding and the program's only question. That is a real trade, not a dominated
option — which is why the recommendation below grafts v2's channels rather than resurrecting its
default shape.

### 9. Methodology debts that gate the next iteration

- **Hindsight contamination**: mirror history must be truncated at the merge-base (test 3's P0/P1
  split and fix-accuracy comparison are unadjudicable because of it).
- **The closed-PR stop rule**: read literally, test 3 should have produced four refusals. v3 alone
  surfaced the tension. Retrospective review of merged PRs is now this program's main evaluation
  method; the rule must permit it explicitly (publication off by default) rather than relying on
  each run's judgment.
- **n = 1 per prototype per target, no repeated seeds, three different models** — no variance data,
  no cross-test differencing, and v5's test-1 numbers are development-set.
- **Never exercised**: `plausible` verdicts, published author questions from the verifier path,
  re-review against prior threads, stale-head aborts, file-only anchors, the GitHub body fallback,
  gating (non-advisory) events.

## Recommendation

### Advance v5 as the base

**Carry `code-review-publish-5` forward as the winning prototype.** The case, on holdout evidence
(tests 2 and 3, which its design never saw): it is the only architecture whose verification layer
has demonstrated action recalibration without finding erasure; it replicated the hardest true
positive blind and cheaply; its calibration matched the defensible band everywhere; its habits
(caveat at point of claim, re-verify supplied facts, record ambiguities) are the ones an unattended
reviewer needs; and it collapses to the economical single-agent path on clean changes. v4 is the
close second — equal artifact quality in test 1, better escalation behavior — but v5's verifier
verdict shape and its consequence-based (rather than name-based) trigger are the load-bearing
improvements, and v4's one-batch rule demonstrably dropped a real finding.

On the LLM question the data is confounded by design (one model per test), so no strong claim is
available. What the runs do show: the discriminating machinery worked at the Sonnet tier (test 3's
blind catch), and a small model (GLM-5.3-Flash) held the no-false-positives discipline on a clean
PR. Nothing observed requires the largest model for the frequent path; the sensible default is a
Sonnet-tier model for primary review with the option to run the verifier at a higher tier for
must-fix findings — but that split is untested and belongs in the next evaluation round, not in the
skill text as fact.

### Graft from the other three

From **v2**:

1. **The question channel.** A "cannot tell from the code" bucket whose items become published
   open questions (with explicit "change no code for this" framing), not dropped candidates. This
   produced the program's only question and is the piece v3/v4/v5 architecturally cannot express.
2. **The Requirements-candidate exception to the `introduced here` gate** (its `verify.md`):
   pre-existing-at-base refutes Code candidates, never Requirements candidates whose outcome this
   change was responsible for. Test 1's evaluation already flagged v5's unscoped gate text; v2 has
   the correct wording to lift.
3. **An escalation mode, not a default**: permit a second, independent Code-axis pass on
   large/high-risk diffs where extra recall justifies ~1.5× cost (test 3's extra finding is the
   evidence it can pay), while keeping the single-reviewer frequent path.

From **v3**:

4. **The clean-verdict verifier option**: when the diff meets the high-risk bar but zero candidates
   survive, offer/run one verifier over the falsification log instead of the empty survivor list.
5. Its cost profile as the budget target for the frequent path — v5's clean-PR path should cost
   like v3, and in tests 2–3 it already roughly does.

From **v4**:

6. **The orchestrator-question protocol** for recoverable-versus-unrecoverable context failures:
   mark coverage incomplete, derive a provisional status, name exactly what the missing input could
   change, ask the orchestrator (never the author) — v5 never faced this branch and has no
   equivalent drill.
7. **Ambiguity-flagging over silent resolution** when a rubric term is genuinely contestable.
8. Its habit of proving both directions with base-state evidence (lists matched at base; prior
   Kind addition updated all copies) as the standard proof shape for drift findings.

### New modifications the runs motivate

1. **Add a bounded `Observations` section to the output contract** — explicitly non-actionable,
   explicitly not findings — so accurate sub-threshold items (test 2's `redis.conf` scope; v4's
   test-site notes; v2's verifier aside) surface instead of dying out-of-band.
2. **Extend the verifier brief for invariant/concurrency findings with a bug-class check**: given a
   confirmed candidate, enumerate sibling code paths governed by the same broken invariant and state
   whether the proposed `change` closes all of them; prefer fix guidance at the invariant level.
   Test 3 shows two of three blind runs proposing a fix that would not have prevented the actual
   incident, with the generalization statically derivable.
3. **Permit one follow-up verifier round for candidates noticed after the batch dispatched**
   (bounded to one), so v4's test-3 situation — a real, must-fix-shaped finding dropped because the
   single batch had already run — cannot recur.
4. **Resolve the `plausible` path**: define an operational trigger (e.g., the verifier must return
   `plausible` when it can neither construct the failing trace nor refute a step of the claim's
   trace) and build a test PR that forces it. If it still never fires, delete it and make
   confirmed-with-corrections/refuted the honest contract.
5. **Fix v5's six self-reported output-contract under-specifications**, the `context`-digest
   `guidance` membership first (two conforming reviewers can currently compute different digests
   from identical inputs, which defeats the duplicate-review check the digest exists for).
6. **Rewrite the closed-PR rule**: "closed" means abandoned/rejected; merged targets are reviewable
   under explicit invocation with publication disabled by default (retrospective/audit mode, stated
   in the summary).
7. **If any axis/finder-style agent survives (per graft 3), require the structured candidate
   disposition ledger from it** — prose falsification records don't survive to re-review.
8. **Fix v2's no-issue rule if v2 is kept as an escalation component**: `Not applicable` →
   "issue text unavailable; review against the PR body, including explicit non-goals, and say so in
   the summary" (the v4/v5 behavior, which test 2 showed is strictly better).

### Keep v2 as the standing comparator

If exactly one other prototype stays alive for comparison, keep **v2** and retire v3 and v4.

The reasoning: a comparator is only worth its maintenance if it is *architecturally distant* from
the advancing prototype and produces things the advancing one structurally cannot, so that every
future target measures a real gap rather than noise. v4 fails that test — it is v5's immediate
ancestor, within 1% on cost and identical on findings, so v5-vs-v4 comparisons measure wording.
v3's distinctive property (no independent verification on the frequent path) is better measured as
an *ablation of v5* (run v5 with the verifier disabled) than as a separate skill with its own
divergent rubric. v2 is the genuine other pole: partitioned parallel finders, verify-everything,
prose reports, and the two channels v5 lacks natively (the question track, cross-axis dedup). Its
record earns it the slot — highest recall in tests 1 and 3, the only extra true finding, the only
published question, the only verifier refutations in a run where others confirmed, and the only
run to catch test 2's doc-scope imprecision. Running v2 alongside v5 on every future target gives
a per-target recall ceiling and a live check on whether the grafts (question channel, escalation
mode) actually reproduce what v2's native architecture produces. When v5-with-grafts stops losing
recall to v2 across an adjudicated set, v2 retires.

### A third direction worth exploring: replicated primaries with reconciliation

The best candidate for a genuinely new direction is not another verification-trigger variant — it
is **running v5's primary reviewer twice, independently, and reconciling the two candidate ledgers
before verification**. Call it N-version review. It is "based on" v2's multi-agent idea, but
partitioned by *replication* rather than by axis.

Three independent observations from these runs point at it:

- Test 2's only substantive disagreement (one run found the `redis.conf` scope mismatch, three
  asserted exactness) was invisible because no artifact ever confronted one reviewer's claim with
  another's. Two independent primaries reconciling ledgers would have surfaced it mechanically:
  "reviewer A asserts the doc is exact, reviewer B asserts it is broader" is itself a finding-or-
  observation generator.
- Test 3's four runs each published a different projection of the same broken invariant. Any two
  of those reports, reconciled, would have yielded the generalized fix (the union of interleavings
  implies the atomicity-level remedy) that no single blind run produced.
- The strongest reliability evidence in the whole program — two structurally different verifiers
  refuting the same false claim via the identical citation — is precisely the signal replication
  produces: independent convergence confirms, independent divergence localizes exactly where a
  second look is needed.

Reconciliation also gives the clean-verdict problem (cross-cutting conclusion 5) a real answer for
free: two independent `Approved` verdicts whose internal ledgers agree is a meaningfully stronger
clean signal than one unverified approval, and ledger *disagreement* under matching verdicts is the
trigger for the falsification-log verifier. The cost is bounded and known — roughly v2's test-1
premium (~1.5×) on targets where it runs — so it should be an escalation tier (high-risk diffs,
clean-verdict-on-risky-code), not the frequent path. This direction subsumes graft 3 (a second
Code-axis pass) if it proves out: replicate the whole primary rather than one axis, and let the
reconciler route divergences to findings, observations, questions, or the verifier.

### Before calling it: the evaluation protocol

Freeze the grafted v5 (version-stamp the workflow), then run the blinded evaluation the test-1
recommendation already called for, amended by what tests 2–3 taught:

1. truncate every mirror's history at the merge-base (no hindsight);
2. adjudicated known-clean and known-defective PRs, including a defect whose fix requires the
   bug-class generalization (test 3's shape) and a requirements omission living entirely in an
   unchanged file (the unexercised gate);
3. at least one target engineered to force a `plausible` verdict and a published question;
4. repeated seeds per target for variance, one model held constant across all runs — then, and only
   then, a controlled model-tier comparison on the same targets;
5. v2 run alongside v5 on every target as the standing recall comparator, plus a v5-without-verifier
   ablation arm standing in for v3;
6. the untested operational surface: re-review over prior threads, stale-head abort, anchor
   fallback, gating events.

Until that runs, the defensible summary of three tests is: v4 won the published artifact once, v3
won measured economy, v2 won recall and still owns the only question channel — and v5, on the two
targets its design never saw, is the architecture whose behavior you would want from an unattended
reviewer. Advance v5, keep v2 as the yardstick, graft the channels v5 lacks, explore reconciled
replication as the next architectural bet, and stop iterating on development-set evidence.
