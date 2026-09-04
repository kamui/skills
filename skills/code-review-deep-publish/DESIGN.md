# Design notes — code-review-deep-publish

v2a is the Panel line's second iteration: `code-review-publish-2` (v2, PR #14, seeded at commit
`f42f708`) with the fixes the three 2026-09-01 test runs proved necessary, and nothing that would
move it toward the Skeptic line. The evidence base is
[`docs/research/prototype-runs-2026-09-01-aggregate-analysis.md`](../../docs/research/prototype-runs-2026-09-01-aggregate-analysis.md)
and the three v2 run records it synthesizes. v2's original assembly rationale — the survey of
thirteen published reviewers, the Codex-rubric base, the pr-agent Requirements graft, the
dual-audience finding contract — is in v2's own `DESIGN.md` on its branch and is inherited here
unchanged.

## Positioning

The v2a prototype is now named `code-review-deep-publish`. It runs on two deliberate occasions: as
the recall-first escalation for large or high-risk changes, and as the standing comparator arm in
review-skill evaluations. The frequent path belongs to `code-review-publish`.

## The pole statement

v2a exists to be measured against, not to win. The program advanced the Skeptic line (v5 → v5a) as
the production candidate and kept the Panel line alive as the standing recall comparator — and a
comparator is only worth running if it stays *architecturally distant* from what it measures
(aggregate analysis § "Keep v2 as the standing comparator"). Every convergence shrinks what the
comparison can detect. So these are deliberately preserved, and future edits should treat removing
any of them as defeating the skill's purpose:

- **Two parallel axis finders** (Code, Requirements), each independently sweeping the full diff.
  This is the recall engine: highest recall in tests 1 and 3, including the only extra
  independently-confirmed true finding of the program (test 3's mandatory-work-on-caller-thread).
- **Mandatory fresh-context verification of every candidate**, with `support` withheld so the
  verifier gets claims only, and `verify.md`'s anti-over-refutation asymmetry. v2's verifier is the
  only one that ever refuted candidates in a run where others confirmed (test 1: two false
  candidates removed, one cross-axis duplicate merged).
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
replication. The trailer's pinned SHAs are v2a's identity record; it needs no fingerprint.

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
([aggregate analysis § 8](../../docs/research/prototype-runs-2026-09-01-aggregate-analysis.md#8-economics-what-the-cost-data-actually-supports)).
The trace behind that comparison recorded 118 tool calls: 91.3k and 99.8k tokens in the two finders,
then 62.5k in the verifier.

Three changes target waste around that architecture. The orchestrator now reads the diff, commits,
manifest, and base-branch guidance once, then gives both finders a byte-identical prompt prefix for
cache reuse. The verifier follows claim-dependent call sites but stops expanding once decisive
evidence supports a verdict. Both finder ledgers keep every hypothesis while limiting each row to
four compact fields on one line. The two full-diff analyses and verification of every candidate
remain mandatory.

C14 supersedes the cache-reuse claim above: the measured harness did not reuse that prefix.

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
clone (290 tests) and three of its ledger rows are acquitted on `290 tests pass`, while the
Requirements finder separately recorded 290 Python and 60 Node tests passing as its verification of
requirement 11 ([test 1 v2a run](../../docs/research/prototype-runs-2026-09-01-test-1/v2a-run.md), §2
Observations item 9 and §4). The same Python suite was therefore executed twice, in two contexts, for one suite's
worth of information — and the run's own Coverage line reports it once.

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
exactly as before, by a cheaper route. The workflow identifier stays `v2a-1`; issue #59 bumps it once
after all v2b behavior changes land (tracking epic #62).

### C14. Orchestration is script-driven

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

### Subtractions

None structural. Beyond the deletions listed under C2 and C5, no working v2 machinery was removed
or made conditional.
