# Design notes — code-audit-publish

v2a is the Panel line's second iteration: `code-review-publish-2` (v2, PR #14, seeded at commit
`f42f708`) with the fixes the three 2026-09-01 test runs proved necessary, and nothing that would
move it toward the Skeptic line. The evidence base is
[`docs/research/prototype-runs-aggregate-tests-1-3-v2-v5.md`](../../docs/research/prototype-runs-aggregate-tests-1-3-v2-v5.md)
and the three v2 run records it synthesizes. v2's original assembly rationale — the survey of
thirteen published reviewers, the Codex-rubric base, the pr-agent Requirements graft, the
dual-audience finding contract — is in v2's own `DESIGN.md` on its branch and is inherited here
unchanged.

## Positioning

The skill is named `code-audit-publish`, formerly `code-review-deep-publish`. Its direction is a
PR-triggered audit of affected requirements, contracts and system guarantees, bounded by the
change's effects. The frequent path belongs to `code-review-publish`; the audit remains explicit-only.
The rename retains the `v2b-1` review protocol and the existing two-finder workflow. It does not
claim that the planned transition audits, stronger verification or executable experiments have
shipped. Admission, verification, rendering and state changes receive their own release bumps.

The [assessment](../../docs/research/code-review-deep-publish-assessment-2026-09-05.md) motivates
three work streams: reliable verification/publication, discovery of affected obligations and
guarantees, and matched evaluation of incremental findings and operating cost. Preserve independent
discovery and permit shared reliability mechanisms with the routine skill. Keep historical
comparators as pinned snapshots rather than freezing the live skill to maintain a contrasting pole.

The implementation roadmap is tracked in GitHub:

- [#156: verification and publication foundations](https://github.com/kamui/skills/issues/156).
- [#157: affected contracts, guarantees and executable behavior](https://github.com/kamui/skills/issues/157).
- [#158: usefulness, operating cost and selective routing](https://github.com/kamui/skills/issues/158).

[#159](https://github.com/kamui/skills/issues/159) owns landing this rename. The existing
[#84](https://github.com/kamui/skills/issues/84) owns the demonstrated deleted-file coordinate repair
shared with the routine publisher. The bounded discovery-worker prototype remains a separate
experiment under [#138](https://github.com/kamui/skills/issues/138).

The strongest controlled evidence is requirements completeness and external-reference conformance.
High-risk superiority remains unproven. Historical matched production-shaped cost premiums were
2.15–2.25× on two targets, a different measure from the older 1.5× token estimate below. Neither
figure is a general current cost promise.

## v2b

Workflow identifier: `v2b-1`. A `v2a-1` trailer remains readable because v2b changes the identifier,
not the trailer vocabulary.

### The pole statement

Historical rationale for v2b, superseded as a product constraint by Positioning above. The current
integrated reviewer has a question channel; the claim below about what those architectures cannot
express described an earlier design and is not current capability guidance. The retained history
explains the experiments, not a prohibition on backporting stronger verification or state handling.

v2b keeps v2a's purpose: it exists to be measured against, not to win. The program advanced the
Skeptic line (v5 → v5a) as the production candidate and kept the Panel line alive as the standing
recall comparator — and a comparator is only worth running if it stays *architecturally distant*
from what it measures (aggregate analysis § "Keep v2 as the standing comparator"). Every convergence
shrinks what the comparison can detect. These properties remain the pole, and removing any of them
defeats the skill's purpose:

- **Two parallel axis finders** (Code, Requirements), each independently sweeping the full diff.
  This is the recall engine: highest recall in tests 1 and 3, including the only extra
  independently-confirmed true finding of the program (test 3's mandatory-work-on-caller-thread).
- **Mandatory fresh-context verification of every candidate and every acquittal related to one**,
  with `support` withheld so the verifier gets claims only, and `verify.md`'s
  anti-over-refutation asymmetry. v2's verifier is the only one that ever refuted candidates in a
  run where others confirmed (test 1: two false candidates removed, one cross-axis duplicate
  merged).
- **The Requirements-candidate exception** to pre-existing-at-base refutation (`verify.md`
  § refuted, "pre-existing"). v5a grafted this *from* v2; the original wording stays here verbatim.
- **The question channel** — the Requirements axis's "cannot tell from the code" bucket. It
  produced the only published author-facing question in twelve runs (test 3's `condvar_mutex`
  saturation question), a thing the integrated architectures structurally cannot express.
- **Recall-first posture and its cost.** The duplicated whole-diff pass costs ~1.5× a
  single-reviewer-plus-verifier architecture where cleanly measured (test 1: 253.7k tokens vs
  ~175k). That premium bought a real extra finding and the program's only question in test 3. It is
  the accepted price of the pole; do not optimize it away.

Deliberately **not** adopted from the Skeptic line, for the same reason: consequence-triggered
verification routing, conditional verification, the context-fingerprint script, N-version
replication. The trailer's pinned SHAs are v2b's identity record; it needs no fingerprint.

### Change map

Each row states an externally checkable intent. A prototype run can grade the mechanism as worked,
inert, or harmful against that intent.

| ID | Runtime change | Checkable intent | Evidence |
| --- | --- | --- | --- |
| C1 | Tighten documentary-finding action and priority calibration. | A stale restatement links to a correct canonical rule or cannot name a forbidden wrong action stays advisory and at most P2. | [test 1 v2a run](../../docs/research/prototype-runs-2026-09-01-test-1/v2a-run.md), [aggregate C1 analysis](../../docs/research/prototype-runs-aggregate-tests-1-4-v2a-v5a.md) |
| C5 | Deduplicate pooled observations against each other and confirmed findings before the cap; report cap overflow to the caller. | One fact publishes once, and every accurate observation dropped by the cap remains visible in the run report without changing status. | [test 2 Fable run](../../docs/research/prototype-runs-2026-09-01-test-2-fable/v2a-run.md), [test 4 run](../../docs/research/prototype-runs-2026-09-01-test-4/v2a-run.md) |
| C10 | Run permitted suites once before finder fan-out and share their results. | Both finders and the verifier receive the same suite result without either finder re-running the suite; focused candidate tests remain allowed. | [test 1 v2a run](../../docs/research/prototype-runs-2026-09-01-test-1/v2a-run.md) |
| C11 | Send every candidate-related acquittal through the existing fresh-context verifier dispatch. | A related row receives a cited `holds` or `re-open` ruling; `re-open` becomes caller-visible uncertainty, never a verifier-created finding. | [test 3 v2a run](../../docs/research/prototype-runs-2026-09-01-test-3/v2a-run.md), [verifier addendum](../../docs/research/prototype-runs-2026-09-01-test-3/addendum-2026-09-03.md) |
| C12 | Compare a generated artifact's changed hunks with its source before ignoring it. | A same-diff source/artifact contradiction becomes a candidate even when CI would ordinarily catch it. | [test 4 v2 run](../../docs/research/prototype-runs-2026-09-01-test-4/v2-run.md), [test 4 evaluation](../../docs/research/prototype-runs-2026-09-01-test-4/evaluation.md) |
| C13 | Forward explicit review-record deferrals to the Requirements finder. | An unresolved design, naming, or API-shape deferral on unreleased public surface produces a question and prevents `Passed`. | [test 4 v2a run](../../docs/research/prototype-runs-2026-09-01-test-4/v2a-run.md), [test 4 evaluation](../../docs/research/prototype-runs-2026-09-01-test-4/evaluation.md) |
| C14 | Render summary and caller-report coordinates as checked, commit-pinned links. | Every expressible file coordinate resolves at the reviewed full head SHA while `LEFT` and observation coordinates remain code spans. | [coordinate-link contract](references/publishing.md#coordinate-links), [link checker](scripts/link_coordinate.py) |
| C15 | Build shared finder input and verifier prompts with scripts, and keep the caller report compact. | Mechanical orchestration is reproducible without moving review judgment or exposing finder `support` to the verifier. | [shared-block builder](scripts/build_shared_block.py), [verifier-prompt builder](scripts/build_verifier_prompt.py) |
| C16 | Validate finder ledger, manifest, and counts shape before verification. | A malformed finder report gets one shape-only retry, then makes its axis incomplete instead of entering verification unaudited. | [finder-report validator](scripts/validate_finder_report.py), [test 1 v2a run](../../docs/research/prototype-runs-2026-09-01-test-1/v2a-run.md) |

## The changes, mapped to evidence

### C1. Action decoupled from priority

v2's worst result: in test 1 it published two one-line doc-sync drifts — items every calibrated run
called optional — as P1 `must-fix` and derived `Changes Requested` on an author-adjudicated
approvable change ([test-1 v2-run](../../docs/research/prototype-runs-2026-09-01-test-1/v2-run.md),
[test-1 evaluation](../../docs/research/prototype-runs-2026-09-01-test-1/evaluation.md)
§ "Narrow: the central disagreement"). Root cause per that evaluation: v2 "derives action from
priority" — one judgment, two renderings, so severity dragged blocking along with it.

`finding-format.md` § Vocabularies now makes them separate judgments: action is licensed by
demonstrated merge consequence, never the severity label; P0 is inherently `must-fix` and no other
derivation exists; priority must not be inflated to communicate action. The calibration sentences
(authoritative-execution-path gap → `must-fix`; consistency drift with canonical behavior intact →
`consider`) are borrowed from the v4/v5 vocabulary, as is the standing "Closing this without action
is a correct response" line v2 already carried. `verify.md` § Priority and action licenses the
verifier's "fact confirmed, merge consequence disproved → downgrade to `consider`" verdict shape —
the single best verifier behavior of the program (v5, test 1). `publishing.md`'s ladder states that
status keys on action alone. Both axis briefs return `action` per candidate.

**Checkable intent** (handoff 3's success test): on the test-1 target, v2a still *finds* both
drifts — that is the recall pole — but lands them in the non-blocking band.

The post-C9 test-1 runs measured that intent on two models, and it held on one. Both runs found both
drifts. The Fable run landed the Narrow drift `P2 consider`, its verifier noting that the stage
skill links to and says to follow the protocol, so the stale list is paraphrase drift rather than a
broken execution path. The model-matched Sonnet run confirmed the same item `P1 must-fix`, published
the bundle drift `P1 consider`, and derived `Changes Requested` on an author-adjudicated approvable
change ([test 1 v2a run](../../docs/research/prototype-runs-2026-09-01-test-1/v2a-run.md) §2 and §7;
[test 1 evaluation](../../docs/research/prototype-runs-2026-09-01-test-1/evaluation.md) § "Narrow
refresh drift: stable fact, unstable action"; [aggregate
analysis](../../docs/research/prototype-runs-aggregate-tests-1-4-v2a-v5a.md) §2 "v2a C1", §3 row C1,
and §5 item 3). Its verifier defended `must-fix` from this section's own calibration sentence — an
executed skill step is an authoritative execution path — and both priorities sat above every
calibrated run on the item (v4, v5, and the Fable run: P2/P3). The decoupling mechanism worked; the
calibration text left two joints loose. [Issue #55](https://github.com/kamui/skills/issues/55)
tightens both. `finding-format.md` now says when a restatement is on an authoritative execution
path: only when the stale text carries no link or reference to the canonical rule, **and** following
it literally causes a named wrong action the canonical text forbids; when either fails, the drift is
`consider`. It also caps restatement drift — a second document carrying an older version of a rule
whose canonical statement is correct — at `P2` when the stale document is executed as instructions
and `P3` otherwise. `verify.md` § Priority and action asks the verifier to quote the wrong action
and the forbidding canonical line before confirming `must-fix` on a documentary candidate, and to
name the non-documentary consequence before confirming `P1`. `requirements-axis.md`'s priority scale
no longer reads a requirement met at its canonical implementation, with only a sibling document
stale, as `P1`. On paper against the test-1 Narrow finding, the first part of the test fails —
`shortlist-narrow/SKILL.md:46` links to the protocol — so the item lands `consider`, and the
bundle-contract item lands `P3 consider`. The two-part test still licenses `must-fix` where the
stale text is the executed one and causes a wrong action, and action stays independent of priority.

### C2. The no-issue rule reviews the body's claims and non-goals

v2's rule made the Requirements axis `Not applicable` on any PR without a linked issue — silently
deleting half the architecture, as test 2 showed; the body-claims check that substituted happened
only because the finder chose to do it
([test-2 evaluation](../../docs/research/prototype-runs-2026-09-01-test-2/evaluation.md)
§ "The no-issue path", which calls v2's rule "the weak one" against v3/v4/v5's strictly better
handling).

Now: with no issue, the Requirements finder runs against the pull request body's behavioral claims
**and explicit non-goals**, the body-claims ledger is required rather than finder initiative, and
the published summary reports issue alignment as **unavailable**. The direction of the walk is the
guard against the original worry (an author's description restates the diff, so compliance-walking
it always passes): the finder verifies each claim *against the code* and tests stated non-goals as
scope boundaries, rather than checking the diff off against its own description.

Deleted as contradicting this change: `SKILL.md`'s "Requirements axis becomes `Not applicable`"
paragraph, `requirements-axis.md`'s "return `not-applicable` immediately and stop" rule, and
`publishing.md`'s "With no originating issue, Requirements is `Not applicable`" line. `Not
applicable` also left the axis-classification vocabulary entirely — the no-issue path was its only
producer, and vocabulary no run can reach is exactly the dead machinery the aggregate analysis
warns about (cross-cutting conclusion 2).

### C3. Structured candidate disposition ledger from both finders

v2's finders reported narrative. Test 2's evaluation
(§ "Candidate generation versus falsification") showed why that fails the stated use case: v2's
zero-findings run had done real falsification work — six mechanisms "specifically tried to convict
and could not" — but recorded it as prose, "the worst substrate for re-review continuity of the
four"; only its own report proved its zero was a different kind of zero. Both axis briefs now
require the same ledger v3–v5 produce: one row per hypothesis weighed — claim, falsification
route, decisive evidence, disposition — with pre-admission acquittals as rows, not narrative. The
ledger also gives the orchestrator and the verifier a stable interface, and re-reviews hand each
finder the prior round's ledger.

### C4. Question routing codified

Test 3's run had to improvise whether "cannot tell from the code" items pass through the verifier;
its Notes flag the choice as the run's one deviation from a literal reading
([test-3 v2-run](../../docs/research/prototype-runs-2026-09-01-test-3/v2-run.md) § Notes). The
choice that run made is now the rule, in `requirements-axis.md` § Step 2 and `SKILL.md` § Verify:
items in that bucket resolve to questions at the finder and bypass the confirm/refute verifier — a
question is not a defect claim — and each must carry (a) why no static evidence can settle it and
(b) what measurement or answer would. The bar matches v5a's G1 guard: "no static evidence could
settle this", not "I didn't find it". The `plausible` → question route through the verifier is
unchanged and remains the other way a question arises.

### C5. The `Observations` section

Every architecture lost accurate sub-threshold observations (aggregate analysis, cross-cutting
conclusion 4). v2 hit both variants: its test-2 Code finder made the run's most careful observation
(the `redis.conf` first sentence is broader than the code) and had nowhere to put it but an
out-of-band orchestrator note; its test-3 verifier's aside about the `WaitResult::Timeout` path —
in fact a real defect v3 published — was "outside my mandate" by rule.

`publishing.md` now specifies a summary-body `## Observations` section with the same shape as
v5a's N1, kept identical on purpose so the two prototypes' outputs stay comparable: at most three
items, one sentence plus one evidence pointer each, explicitly non-actionable, no
"should"/"must" language, no line-comment anchors, counted in no total. Two routes in, matching
the two failures above: a finder's accurate observation that fails the candidate bar (axis
briefs § Observations), and a verifier aside (`verify.md`, replacing the old "say so at the end in
one line" text).

Two runs showed the channel's edges. On test 2 Fable the `redis.conf:1795` first-sentence scope fact
was raised twice: the Requirements finder made it candidate R2, the verifier confirmed it at
`P3 consider`, and the Code finder returned the same fact as an observation, so the would-be review
carried it as a finding *and* as an observation ([test 2 Fable v2a
run](../../docs/research/prototype-runs-2026-09-01-test-2-fable/v2a-run.md) § "The `redis.conf`
item and the third-party state, per finder", and its C5 note "confirmed, with a split"). On test 4
both finders flagged the same `protocol.yml:3234` trailing-whitespace fix, and the orchestrator
merged them "by analogy to the candidate-dedup principle" because the Deduplicate rule was written
for candidates; five observation-shaped items then met the cap of three, and the verifier's two
accurate asides were dropped with no record, one of them noted as folding "into Finding 1's own
evidence" ([test 4 v2a run](../../docs/research/prototype-runs-2026-09-01-test-4/v2a-run.md) § 4
rows 10, 22, 27, 28 and § 9 "Judgment call — Observations cap"). The aggregate scorecard's verdict
on C5 reads "worked; no cross-axis dedup, cap binds" ([aggregate
analysis](../../docs/research/prototype-runs-aggregate-tests-1-4-v2a-v5a.md) § 3 row C5).

Four edits. `verify.md` § Deduplicate now covers observations: two are the same when they cite the
same `file:line` or state the same fact, and one that describes the fact of a confirmed candidate
is not an observation at all — the finding carries it. `publishing.md` § The summary applies that
rule to the pooled observations before the cap, because `scripts/build_verifier_prompt.py`
forwards candidates and related acquitted rows only, so a finder's observation never reaches the
verifier and the orchestrator is the only place the cross-axis duplicate can be caught. The same
paragraph records every observation the cap drops in the run report as
`observation (unpublished, cap)` with its evidence pointer — the caller receives them in the
session report, not the pull request — and forbids folding a dropped observation or a verifier
aside into a finding's prose, which is the test-4 row-27 move. `SKILL.md` step 4's closing report
lists the observations dropped at the cap. The cap stays three, as does the route into the channel.

Checked on paper against the test 2 Fable run: R2 is confirmed at `P3 consider`; the Code finder's
observation states the same fact at the same `file:line`, so the pool drops it, and the
`redis.conf` fact publishes once, as the finding. Against test 4: the two whitespace observations
collapse by rule rather than by analogy, three publish as before, and rows 27 and 28 appear in the
run report as `observation (unpublished, cap)` with their pointers instead of vanishing, row 27 no
longer folded into Finding 1. Expected cost is ≈0: the comparison is one the verifier already makes
for candidates, and the record is a few hundred output tokens on a run that overflows the cap.
Specified by [issue #58](https://github.com/kamui/skills/issues/58). The workflow identifier stayed
`v2a-1` pending #59.

### C6. Closed-PR rule and trailer parity

Two fixes applied identically in v5a, for comparability:

- **Merged PRs are reviewable** under explicit invocation as retrospective review, with publication
  disabled by default and the condition stated in the summary; "closed" means abandoned or rejected
  without merge. Evidence: retrospective review of merged PRs is the program's main evaluation
  method, and read literally the old rules should have produced four refusals on test 3 (aggregate
  analysis § "Methodology debts").
- **Trailer parity**: full 40-hex SHAs in every trailer, and `workflow=v2a-1` in the `review-run`
  trailer so a later run knows whose contract it is reading. The context-fingerprint script was
  *not* adopted — that is a Skeptic-line mechanism; the trailer's pinned SHAs are v2a's identity
  record.

### C7. Token efficiency around the pole

The clean test-1 comparison put the Panel line at 253.7k tokens versus roughly 175k for the
single-reviewer-plus-verifier lines
([aggregate analysis § 8](../../docs/research/prototype-runs-aggregate-tests-1-3-v2-v5.md#8-economics-what-the-cost-data-actually-supports)).
The trace behind that comparison recorded 118 tool calls: 91.3k and 99.8k tokens in the two finders,
then 62.5k in the verifier.

Three changes target waste around that architecture. The orchestrator now reads the diff, commits,
manifest, and base-branch guidance once, then gives both finders a byte-identical prompt prefix for
cache reuse. The verifier follows claim-dependent call sites but stops expanding once decisive
evidence supports a verdict. Both finder ledgers keep every hypothesis while limiting each row to
four compact fields on one line. The two full-diff analyses and verification of every candidate
remain mandatory.

C15 supersedes the cache-reuse claim above: the measured harness did not reuse that prefix.

### C8. Paired peer-contract sweep before a requirement passes

The first v2a rerun against `kamui/shortlist#66` missed a stale bundle-contract enumeration that
the original v2 finder, v4, v5, and the same round's v5a run found. Four fresh unchanged v2a
Requirements runs missed it too. The 0/5 result rules out an isolated bad sample. Removing only
C3's disposition-ledger output requirement produced the same miss, so ledger construction was not
the cause.

The original transcript shows the finder searching freshness terms, opening
`category-bundle-format.md`, acquitting its separate cache-reuse rule, and never searching for
`search-bundle-format.md`, `discovery branch`, or `safeguard`. An initial peer-sweep fix still
missed in two fresh runs. Both searched new vocabulary and found the Narrow drift, but neither
searched an unchanged phrase from the old obligation-kind list. A new-term search cannot discover
a stale copy that omits the new term.

`requirements-axis.md` now makes a paired peer-contract sweep the completion criterion for each
requirement that changes a vocabulary, enum, schema field, or normative enumeration. The finder
searches once for the new term and once for a distinctive phrase or member that survives from the
base contract, then accounts for every live result in the disposition ledger before marking that
requirement met. This preserves C1 through C5 and fixes discovery where the miss occurred.

### C9. Sweep trigger covers list-opening changes; Code axis sweeps for sync drift

The first post-C8 run against `kamui/shortlist#66` missed the other known drift on that target:
`narrowing-protocol.md` replaced a closed Volatile-refresh list with an open rule, and
`shortlist-narrow/SKILL.md:46` still carries the closed list. Neither finder raised or acquitted
it. Replication showed the miss was mechanism, not noise: 1 of 5 unchanged Requirements runs and
0 of 5 Code runs found it, while every run that swept the Kind enum found C8's own target. The
finder's transcript states the cause in its own words — "the peer-contract sweep was run for the
one enum-touching requirement." C8's trigger, "changes a named vocabulary, enum, schema field, or
normative enumeration," reads as membership changes to a surviving list; a change that retires a
closed list in favor of an open rule was classified as prose generalization, so no sweep
obligation ever reached the consumer file. A diagnostic run with only the per-requirement scope
made emphatic ("every qualifying requirement, not just the first") still missed, isolating the
trigger classification rather than sweep scope. The identical text on Opus classified the
refresh-rule change as a fourth qualifying contract and found the item, matching the
Sonnet-tier execution pattern recorded for v5a.

Two changes, each restructured after a first attempt failed validation. `requirements-axis.md`
now opens the sort step with a **changed-contract scan**: before sorting any requirement, write
down every vocabulary, enum, schema field, or normative enumeration the diff renames, extends,
narrows, or retires, with a closed list replaced by an open rule named as the most commonly
missed kind — nothing in the new text looks like a list any more, and its stale peers are the
files still carrying the retired one. A generalization diff usually contains more than one, and
the sweep is owed to each. The contract list is a required output: per contract, the two search
terms used and every live peer found with its disposition. Both legs are repo-wide and
case-insensitive, and the old-wording leg must be keyed to a short distinctive fragment — two or
three consecutive members of the retired list, or one rare phrase — never a whole sentence,
because consumers restate a rule in their own words and keep only fragments. `code-axis.md`
gains a "Sync drift from a changed rule" section carrying the same discipline into an axis that
had no sweep at all: a peer that matched at base and was made stale by the diff satisfies
criterion 4 even though the stale line is untouched, and before treating such a change as clean
the finder enumerates the qualifying contracts, sweeps each separately, and records every live
result in the ledger. Cross-axis duplicates land under the existing dedup rule, as v2a's
original run already demonstrated for this item.

The first attempt at both stated the rule declaratively — the trigger sentence extended to name
list-opening changes, the Code section describing the paired sweep — and it moved neither axis
(0 of 3 Requirements runs, 0 of 3 Code runs). The transcripts show why the restructure was
needed. One Requirements run read the extended trigger and still wrote "the only contract this
diff opens/generalizes," naming the Kind enum; another acquitted the Narrow item on a
misreading; a third demoted the known bundle item to an observation. The Code runs swept, but
keyed their old-wording legs to whole base sentences or to the wrong contract. Meanwhile both
runs that had ever found the item unprompted — the one passing Requirements replicate and the
Opus diagnostic — began by enumerating the diff's qualifying contracts as an explicit artifact.
The restructure makes that artifact mandatory rather than asking the finder to classify
correctly in passing.

The validation runs also surfaced a third live drift on this target that no prior round had
tracked: `skills/shortlist/scripts/validate-completion.py:2948` still hardcodes the retired
Volatile term list as a regex, and is called unconditionally.

Validation: three fresh Requirements runs and three fresh Code runs against the same pinned
target, Sonnet 5, offline clone, publication disabled. All three Requirements runs enumerated the
diff's changed contracts before sorting, ran a fragment-keyed old-wording sweep for each, and
raised both known drifts as candidates — 3 of 3, against 1 of 5 for the unchanged rubric and 0 of
3 for the first attempt. The Code axis improved less evenly: one run raised both items, one swept
the consumer file and then acquitted it on a false claim that an earlier pull request had already
generalized it, and one never reached the file, collapsing its contract list back onto the enum.
Panel-wide every run pair surfaced the item, because the Requirements axis carried it in all
three, but the Code axis is the weaker leg and is worth re-scoring in the next repeated-seed
evaluation. Both Code runs that swept widely also reached the `validate-completion.py` drift, one
of them with an executed reproduction.

### C10. Test suites run once, before the fan-out

The Panel line pays for every shared input twice, because two finders sweep the same diff. Test
suites had no owner in the skill at all, so both finders picked them up independently. On test 1 the
Code finder's own method note records `python3 -m unittest discover -s tests -p "test_*.py"` in its
clone (290 tests) and four of its ledger rows cite the passing suite as evidence, while the
Requirements finder separately recorded 290 Python and 60 Node tests passing as its verification of
requirement 11 ([test 1 v2a run](../../docs/research/prototype-runs-2026-09-01-test-1/v2a-run.md), §2
Observations item 9 and §4). The same Python suite was therefore executed twice, in two contexts,
for one suite's worth of information — and the run's own Coverage line reports it once.

Step 1 now runs the repository's permitted suites once, before spawning, and puts a one-line result
summary per suite into the shared block alongside the diff, manifest, commit list, and guidance. That
is the same treatment C7 gave every other shared input, and it extends C7's byte-identical-prefix
property rather than competing with it. Both finder briefs and the verifier brief say the results
arrive in the prompt.

The rule is *suite once*, not *no tests*. A finder or the verifier may still run a single focused test
that decides a candidate, which is where executed evidence actually changes a verdict — one Code run
under C9 reached the `validate-completion.py` drift with an executed reproduction, and nothing here
touches that. Estimated saving: −5–10k tokens and −1–3 minutes of wall clock per run on a repository
with suites, and none on one without. Quality risk is none: the suite result reaches both finders
exactly as before, by a cheaper route. The workflow identifier stayed `v2a-1` pending the single
bump in #59 after all v2b behavior changes landed (tracking epic #62).

### C11. Acquittals related to a candidate are verified

The test 3 tokio run exposed a hole inside the Panel line's verification boundary: the Code finder
acquitted the two branches that carried the shipped regression while a different `WouldBlock`
candidate survived, so the false acquittals never reached a verifier that received candidates only
([test 3 v2a run](../../docs/research/prototype-runs-2026-09-01-test-3/v2a-run.md);
[addendum](../../docs/research/prototype-runs-2026-09-01-test-3/addendum-2026-09-03.md)). Step 3 now
adds every related acquitted ledger row to the existing candidate dispatch: related means its evidence
is in a candidate's anchor or fix file, or its claim names the same function, branch, state field, or
lock. `verify.md` applies the same adversarial five-step procedure as the Skeptic line, including an
opposite-branch trace and a fresh citation before `holds`; a premise-contradicting fact is `re-open`,
never an observation.

This extends the Panel pole's verify-everything property rather than adopting consequence-triggered
routing. A re-opened acquittal is reported to the caller and keeps its axis `Waiting for information`;
it is not a verifier-created finding and this run has no second verifier dispatch. The high-risk
zero-candidate dispatch and the re-open round from #54 were deliberately left out on cost, so a later
round may promote the row. Specified by [issue #64](https://github.com/kamui/skills/issues/64).

### C12. Generated artifacts are compared to their source

On test 4 the ancestor Panel run's Code finder found the one ground-truth item checkable inside the
diff and reasoned itself out of reporting it. `packages/playwright-core/types/types.d.ts` is
generated from `docs/src/api/*.md`; the head's final commit rewrote the markdown description and
never regenerated the types, so the two disagreed inside the same diff, four files apart. The finder
marked `types.d.ts` and `channels.ts` "ignored — generated artifact", quoted both conflicting
sentences in its manifest row, and wrote: "That's exactly the class of thing the clean-tree check
exists to catch, so it isn't reported as a candidate"
([test 4 v2 run](../../docs/research/prototype-runs-2026-09-01-test-4/v2-run.md) § Code-axis
manifest; [test 4 evaluation](../../docs/research/prototype-runs-2026-09-01-test-4/evaluation.md)
§ "GT-3"). The CI job would have been red; the diff in front of the finder was the proof that the
generator had not been run. v2a recovered the item through C9's sync-drift section, using
`addCookies`'s JSDoc as a control, but `code-axis.md` still carried the rule that produced the
miss: "Anything a linter, typechecker, formatter, or compiler catches. Assume CI runs them; do not
run them yourself and do not report what they would say." The aggregate analysis names the
mechanism: what counts as terminal evidence is the calibration lever nobody tuned, and the finder
treated tooling as closure on a diff where the tooling had demonstrably closed nothing
([aggregate analysis](../../docs/research/prototype-runs-aggregate-tests-1-4-v2a-v5a.md) § 7,
conclusion 11).

Three edits to `code-axis.md`, all textual checks; none requires running a generator. The first
"What is not a candidate" bullet keeps the assume-CI default for ordinary style and adds the
carve-out: when the diff itself shows the tool did not run or did not catch it — a generated
artifact whose content contradicts its source in the same diff, or a lint-enforced convention the
diff already violates — the item is a candidate, because "a tool would catch this" is a hypothesis
and a diff containing the stale artifact falsifies it. "Account for every file" now permits
`ignored` on a generated file only after its hunks have been compared against the source it is
generated from, with the source named in the reason; hunks that disagree make the file `reviewed`
and the disagreement a candidate. "Sync drift from a changed rule" names a generated artifact and
its source as a peer pair, so a generator that was not re-run is handled as a stale peer by the
sweep C9 already requires.

Checked on paper against test 4's pinned head (`cb02d5ba`, test 4 README):
`docs/src/api/class-browsercontext.md:1016` says "At least one of the removal criteria should be
provided" and `packages/playwright-core/types/types.d.ts:8442` says "will throw an error if either
name, domain or path has not been passed"; under the manifest rule the file is `reviewed` and the
contradiction is a candidate. Expected cost is ≈0 to +3k tokens per run: comparing a generated
file's hunks against its source is a read the finder usually makes anyway, and the rule adds one
read on pull requests that touch generated files. Specified by
[issue #56](https://github.com/kamui/skills/issues/56). The workflow identifier stayed `v2a-1`
pending #59.

### C13. Review-record deferrals reach the Requirements axis

On test 4 the Requirements axis returned `Passed` — 7/7 restated requirements met, 0 questions — on
an API that upstream deleted twenty-four days later. Playwright `#30111`, authored by the maintainer
who approved the pull request, removed `BrowserContext.removeCookies`, deleted its test file, and
folded the `name`/`domain`/`path` filters into `clearCookies()` as options; `removeCookies` never
shipped ([test 4 evaluation](../../docs/research/prototype-runs-2026-09-01-test-4/evaluation.md) §
"GT-2"; [test 4 v2a run](../../docs/research/prototype-runs-2026-09-01-test-4/v2a-run.md) §
Requirements axis). The seed was in the review record the orchestrator held: `pavelfeldman` had
written "`filter` would probably be a better name, but we can fix it during the pre-release api
review." The ancestor v2 Requirements finder had at least asked whether domain/path filters exceeded
the issue's "remove a specific cookie" ([test 4 v2
run](../../docs/research/prototype-runs-2026-09-01-test-4/v2-run.md) § Requirements axis, candidate
2); v2a asked nothing. Two gaps produced that. On a first review the orchestrator withholds prior
review threads from the finders — prior findings and ledgers are appended only on a re-review — so
the deferral never reached the axis. And `Passed` had no rule for a design decision the record
itself says is still open: every requirement can be met by a method whose shape its own reviewers
have agreed to revisit. The aggregate analysis names the mechanism — what counts as terminal
evidence is the calibration lever nobody tuned, and approval is not closure on unreleased public API
([aggregate analysis](../../docs/research/prototype-runs-aggregate-tests-1-4-v2a-v5a.md) § 7
conclusion 11 and § 8 item 4).

Four edits. Step 1 of `SKILL.md` resolves, beside the earlier review, every explicit deferral of a
design, naming, or API-shape decision in the pull request's review comments — any participant, any
round — verbatim with its author and the surface it concerns, and step 2 appends those to the
Requirements finder's axis block. Nothing else from prior review reaches a finder on a first review.
That restriction is deliberate: the finder needs a deferral only as evidence that a question is
open, and the rest of the record would anchor it to the earlier reviewers' conclusions, which is the
approval-as-closure gate test 4 showed failing. `requirements-axis.md` Step 2 gains a fourth bucket
rule, **Deferred by the review record**: a deferred decision on unreleased public surface lands in
the "cannot tell" bucket as a question naming the deferral, its author, and the decision, unless a
repository rule settles it, in which case it is a `requirements/unrequested/` candidate citing the
rule. It is never `Met`, it joins the restated list as its own entry and counts there as
unverifiable, and an axis with an open deferral question is `Waiting for information`, not `Passed`.
Step 3's creep list adds the duplicate-capability case: a new public surface expressible by
composing existing methods is creep worth raising when guidance discourages it or the issue asked
for a capability rather than a method — the `removeCookies`- beside-`clearCookies()` shape, which
playwright's `CONTRIBUTING.md` "avoid adding sugar API" rule covers. `publishing.md` § Status says
an unresolved deferral on the axis's subject keeps the Requirements axis at `Waiting for
information`, and `SKILL.md` step 3's outcome derivation carries the same exception.

The rule needs an explicit postponement in a review comment. A suggestion the author declined, or a
preference a reviewer stated once and dropped, is not a deferral, and a naming nit does not become
one by being about a name.

Checked on paper against test 4's pinned head (`cb02d5ba`, test 4 README): step 1 extracts the
`pavelfeldman` sentence with `removeCookies(filter)` as its surface; the Requirements finder
receives it after the issue text; `removeCookies` is absent from every released version, so the
deferred naming and API-shape decision lands in the "cannot tell" bucket as a question naming
`pavelfeldman`, the deferral, and the decision — whether the filter parameter, and a second
cookie-removal method beside `clearCookies()`, keep their shape before release. The restated list
grows to eight entries, the counts read `met=7 not-met=0 unverifiable=1`, the axis is `Waiting for
information` rather than `Passed`, and the question publishes without passing through the verifier.
Expected cost is ≈0: the extraction is a few hundred tokens, and an open deferral yields one
question in place of `Passed`. Specified by [issue #57](https://github.com/kamui/skills/issues/57).
The workflow identifier stayed `v2a-1` pending #59.

### C14. Review file coordinates are commit-pinned links

The Panel line's summaries and caller handoffs named review coordinates as bare code spans, leaving
the reader to navigate to a file and recover the reviewed revision. `publishing.md` now renders each
expressible coordinate through [`link_coordinate.py`](scripts/link_coordinate.py) as a link to the
base repository at the reviewed full head SHA. The visible coordinate is unchanged; line and range
links carry GitHub's `?plain=1` fragment, a distinct fix site gets its own link, and every assembled
fragment is checked against the script before publication. `LEFT` anchors and observation pointers
remain code spans because the current record does not carry enough revision provenance to link them
honestly.

The checkable intent is that every linked coordinate resolves to the exact code the review read and
stays stable across later branch movement, while a coordinate without sufficient provenance is not
made falsely clickable. The script's self-test covers line, range, file, encoding, revision, and
Markdown-injection cases. Specified by [issue #83](https://github.com/kamui/skills/issues/83).

### C15. Orchestration is script-driven

The Panel runs made the orchestrator 30–45% of total token use even though it made no review
judgment beyond status derivation. Most of that work was mechanical: reading and reproducing the
shared diff and guidance, re-reading both finder reports to remove private reasoning, hand-building
the verifier prompt, and then reproducing the reports for the caller. The byte-identical finder
prefix described in C7 produced no measured cache reuse, so this decision supersedes that proposed
saving rather than depending on it.

[`build_shared_block.py`](scripts/build_shared_block.py) now gathers and renders the pinned finder
inputs, and [`build_verifier_prompt.py`](scripts/build_verifier_prompt.py) parses the structured
finder blocks and removes every `support` field. The caller report carries only status, identity,
coverage, counts, questions, observations, the refuted count, and the publication result. These
changes remove orchestrator tokens without changing review judgment: candidate generation,
falsification, verification, deduplication, status derivation, and publication decisions remain
where the process already assigns them. This is the script-driven boundary specified by
[issue #65](https://github.com/kamui/skills/issues/65).

### C16. Ledger shape is enforced mechanically

C3 made the disposition ledger a required return, and six of the seven corpus runs complied. The
model-matched test-1 run did not: the Requirements finder returned a prose changed-contract sweep in
the ledger's place, the orchestrator correctly refused to fabricate rows, and that axis's search
process — which files it checked and dismissed — became unauditable from its output
([test 1 v2a run](../../docs/research/prototype-runs-2026-09-01-test-1/v2a-run.md) §4;
[aggregate analysis](../../docs/research/prototype-runs-aggregate-tests-1-4-v2a-v5a.md) §3 row C3
and §5 item 8). The ledger is what made every false acquittal in the corpus quotable, and a return
a finder can decline to produce is a rule, not a mechanism.

Both axis briefs now end the report with fenced `ledger` and `manifest` blocks, plus a `counts`
block on the Requirements axis, in a row grammar a script can check, and
[`validate_finder_report.py`](scripts/validate_finder_report.py) checks it before step 3, the way
`code-review-publish` gates its own output with `validate_review.py` (issue #31). A violation
re-dispatches the finder once with its original prompt, the violation lines, and the instruction
to return the same review in shape; a second failure leaves the axis `incomplete` and the summary
names it. The script validates shape only — block presence and order, field counts, the
disposition set, the evidence pointer form, manifest coverage, and the three integer counts — and
never reads the repository, runs git, or judges a row.

This is an enforcement of C3, not a rule change: the ledger means what it meant, the dispositions
are the ones C3 and C4 defined, and the rows the verifier-prompt builder (C15) already parses are
the rows the validator admits. Reformatting the test-4 Code finder's verbatim ledger into the
blocks showed where the grammar bites: six of its fifteen rows carried a sentence in the evidence
field where the brief asked for one pointer, and each needed a location supplied — which is the
row shape the briefs now spell out for acquittals that rest on an absence. Expected cost is
+5–7k tokens per run, because the retry fired once in seven corpus runs. Specified by
[issue #53](https://github.com/kamui/skills/issues/53), which named this section C10; that number
went to the suite-once change, C11–C14 to #64, #56, #57, and #83, and C15 to script-driven
orchestration. The workflow identifier stayed `v2a-1` pending #59.

### Subtractions

None structural. Beyond the deletions listed under C2 and C5, no working v2 machinery was removed
or made conditional.
