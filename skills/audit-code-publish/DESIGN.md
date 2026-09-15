# Design notes — audit-code-publish

v2a is the Panel line's second iteration: `code-review-publish-2` (v2, PR #14, seeded at commit
`f42f708`) with the fixes the three 2026-09-01 test runs proved necessary, and nothing that would
move it toward the Skeptic line. The evidence base is
[`docs/research/prototype-runs-aggregate-tests-1-3-v2-v5.md`](../../docs/research/prototype-runs-aggregate-tests-1-3-v2-v5.md)
and the three v2 run records it synthesizes. v2's original assembly rationale — the survey of
thirteen published reviewers, the Codex-rubric base, the pr-agent Requirements graft, the
dual-audience finding contract — is in v2's own `DESIGN.md` on its branch and is inherited here
unchanged.

## Positioning

The skill is named `audit-code-publish`, formerly `code-audit-publish` (issue #245) and before that `code-review-deep-publish`. Its direction is a
PR-triggered audit of affected requirements, contracts and system guarantees, bounded by the
change's effects. The frequent path belongs to `review-code-publish`; the audit remains explicit-only.
The `code-review-deep-publish` rename retained the `v2b-1` review protocol and the existing two-finder workflow; C17
advanced the identifier to `v2b-2`, C18 to `v2b-3`, C19 to `v2b-4`, C20 advanced it to `v2b-5`, and the paired deleted-file repair advances it to `v2b-6`. It does not claim that the planned transition audits, stronger
verification or executable experiments have shipped. Admission, verification, rendering and state
changes receive their own release bumps.

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
shared with the routine publisher. The bounded discovery-worker prototype was a separate
experiment under [#138](https://github.com/kamui/skills/issues/138), now closed; its result does not
change this skill.

The strongest controlled evidence is requirements completeness and external-reference conformance.
High-risk superiority remains unproven. Historical matched production-shaped cost premiums were
2.15–2.25× on two targets, a different measure from the older 1.5× token estimate below. Neither
figure is a general current cost promise.

## v2b

Workflow identifier: `v2b-6`. Issue #84 adds the deleted-file provenance contract described below. Issue #166 adds complete forge input identity and same-head review eligibility in [C20](#c20-complete-input-identity-and-same-head-changes). Issue #160 increments `v2b-3` to `v2b-4` for the verification
change recorded in [C19](#c19-isolated-verification-and-verdict-accounting): the verifier runs
in a genuinely non-inheriting worker or verification is incomplete, candidates and ledger rows carry
a risk kind and ledger rows a per-run id, and every candidate verdict and acquittal ruling is
accounted mechanically, with an empty return a failure rather than a clean review. Issue #163
incremented `v2b-2` to `v2b-3` for the verdict-routing and status semantics recorded in
[C18](#c18-unresolved-evidence-material-questions-and-optional-findings). Issue #161 incremented
`v2b-1` to `v2b-2` for the admission and refutation change recorded in
[C17](#c17-removed-guarantees-put-unchanged-code-in-scope): unchanged code is introduced-here when
the diff removed or weakened a guarantee it relied on, and a `pre-existing` refutation must compare
the same path, trigger and governing guarantee at base and head. A `v2a-1`, `v2b-1`, `v2b-2` or
`v2b-3` or `v2b-4` trailer remains readable as historical state. The current trailer adds context and lifecycle identity; prior finding ids, replies and verdicts remain legible, but older run trailers cannot suppress a current-contract review.

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
| C13 | Forward explicit review-record deferrals to the Requirements finder. | An unresolved design, naming, or API-shape deferral on unreleased public surface reaches the axis, never counts as `Met`, and produces a question that prevents `Passed` where C18's outcome-changing test admits one. | [test 4 v2a run](../../docs/research/prototype-runs-2026-09-01-test-4/v2a-run.md), [test 4 evaluation](../../docs/research/prototype-runs-2026-09-01-test-4/evaluation.md) |
| C14 | Render summary and caller-report coordinates as checked, commit-pinned links. | Ordinary coordinates resolve at head; known deleted whole files resolve at the pinned merge-base. LEFT lines, unknown file provenance, rename and observation coordinates remain code spans. | [coordinate-link contract](references/publishing.md#coordinate-links), [link checker](scripts/link_coordinate.py) |
| C15 | Build shared finder input and verifier prompts with scripts, and keep the caller report compact. | Mechanical orchestration is reproducible without moving review judgment or exposing finder `support` to the verifier. | [shared-block builder](scripts/build_shared_block.py), [verifier-prompt builder](scripts/build_verifier_prompt.py) |
| C16 | Validate finder ledger, manifest, and counts shape before verification. | A malformed finder report gets one shape-only retry, then makes its axis incomplete instead of entering verification unaudited. | [finder-report validator](scripts/validate_finder_report.py), [test 1 v2a run](../../docs/research/prototype-runs-2026-09-01-test-1/v2a-run.md) |
| C17 | Admit unchanged code whose relied-on guarantee the diff removed, and require the same base/head comparison before a `pre-existing` refutation. | A byte-identical path safe at base and unsafe at head becomes a candidate citing both revisions and its consumer, while a path already unsafe at base is still refuted as pre-existing and a guarantee-preserving refactor still yields nothing. | [replay record](../../docs/research/audit-removed-guarantee-scope-2026-09-12.md), [assessment B3](../../docs/research/code-review-deep-publish-assessment-2026-09-05.md#what-shipped-and-what-to-backport) |
| C18 | Route an unsettled thing by settle / ask / record, name the five refutation bases, and gate deferral questions on the present decision. | An answerable claim is settled rather than asked, a published question is outcome-changing and unanswerable, an unresolved record never reads as safety, and a proven low-priority defect stays a `consider` finding. | [holdout evaluation (a), (d), (e)](../../docs/research/prototype-runs-holdout/evaluation.md), [assessment B2/B6/B8](../../docs/research/code-review-deep-publish-assessment-2026-09-05.md#what-shipped-and-what-to-backport) |
| C19 | Run the verifier in a non-inheriting worker, carry kind / impact / change and per-run ledger ids through the packet, and account every verdict and ruling mechanically. | Every candidate id the verifier was given has exactly one verdict and every related row exactly one ruling before any verdict is read; an empty return to a non-empty packet is a failure that withholds the affected candidates; a run without isolation publishes no confirmed finding; support text never reaches the worker while the requested repair does. | [accounting fixtures](scripts/account_verifier_return.py), [packet fixtures](scripts/test_build_verifier_prompt.py), [replay record](../../docs/research/audit-verifier-accounting-2026-09-12.md), [assessment B5](../../docs/research/code-review-deep-publish-assessment-2026-09-05.md#what-shipped-and-what-to-backport) |

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
settle this", not "I didn't find it". The `plausible` → question route through the verifier was the
other way a question arose; C18 keeps that route and gates it, so a `plausible` verdict asks only
where the unsettled fact is outcome-changing and no available source can settle it. C18 also adds a
third thing each bucket item carries, beside (a) and (b): the present decision the answer moves.

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
compact fields on one line — four at the time, six since C19 added the per-run id and kind. The two
full-diff analyses and verification of every candidate
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

C18 narrows the publication half of this change and leaves the rest standing: the deferral still
reaches the axis, is never `Met`, and counts as unverifiable, and it publishes as a question — the
thing that holds the axis at `Waiting for information` — when its answer moves a decision this merge
settles. Structurally the bucket is no longer a fold into "cannot tell": the deferral rule now
carries its own two-rule split, and a recorded deferral keeps the `question` ledger disposition so a
later round reads the decision as open rather than as tested and killed. The paper check below is
unaffected, because `removeCookies` was what that merge would release.

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
base repository at the reviewed full head SHA, with the deleted-file exception added by
[issue #84](#deleted-file-provenance-issue-84) resolving at the pinned merge-base. The visible
coordinate is unchanged; line and range
links carry GitHub's `?plain=1` fragment, a distinct fix site gets its own link, and every assembled
fragment is checked against the script before publication. LEFT lines, unknown file provenance,
rename coordinates and observation pointers remain code spans because the record does not establish
a linkable path and revision for them.

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

### C17. Removed guarantees put unchanged code in scope

The [assessment](../../docs/research/code-review-deep-publish-assessment-2026-09-05.md#what-shipped-and-what-to-backport)
item B3 is the gap this closes. `code-axis.md` criterion 4 excluded every defect the diff did not
write, and the one exception it carried — C9's sync drift — is documentary: it admits a peer whose
text went stale, and says nothing about a consumer whose *runtime* safety went stale. Between them
sat the class the routine line already admits (`review-rubric.md` gate 2, shipped for its issue #49
under `v5a-1` and folded into `v5b-1`): a lock
whose scope shrank, an ordering constraint dropped, an ownership or lifetime rule relaxed, a
validated invariant no longer validated, a check or a bound removed — with the code that relied on
it left byte-identical, and therefore silently out of scope. `verify.md` compounded it: its
`pre-existing` refutation asked only for "the prior state", which a verifier can satisfy by
observing that the consumer's line is untouched, the same reasoning that put the candidate out of
scope in the first place.

Three owners move together. `code-axis.md` gains § Guarantees removed from unchanged code: name
which of the two shapes of introduction you have, and for the guarantee shape carry the whole
comparison in the `claim` — the base line that established the guarantee, the diff line that
removed or weakened it, the consumer that relied on it, and the trigger. A path already unsafe at
the merge-base under the same conditions stays pre-existing and stays out; proximity, refactor
size, and unease are explicitly not substitutes for the comparison; and the section says in its own
text that it is a scope rule, not a licence to audit the repository. `verify.md` gains
§ The pre-existing comparison, which turns that refutation into four steps against both revisions
and routes an unreconstructable base state to `plausible` rather than to a refutation.
`finding-format.md` § Anchor and fix site derives both coordinates from the proposed repair rather
than fixing either in advance: restoring the protection the diff removed makes that changed line the
fix site and rung 1 the anchor, while a deliberate removal the consumer must adapt to makes the
consumer the fix site and rung 2 the anchor at the line that dropped the protection. Fabricating a
changed line at the consumer is called out as the thing not to do in both directions — the forge
rejects it, and a reader who follows it finds a claim the diff does not make.

Two existing properties are preserved deliberately, because a general introduction rule is exactly
what could erode them. The Requirements exception keeps `verify.md`'s wording verbatim and gains a
restatement in `code-axis.md`, which never carried it before: a requirements gap is measured against
the issue, so an explicit unmet obligation is this change's responsibility even when the missing
work lives entirely in unchanged or pre-existing code. And C9's paired
old/new peer sweep keeps its own evidence rule rather than being folded into the new comparison;
the new section points at it as the documentary case and changes none of its searches.

Evidence is a [replay record](../../docs/research/audit-removed-guarantee-scope-2026-09-12.md): five
pinned fixtures traced through the pre-change and post-change instruction text, one per acceptance
case in the issue. It is a paper transition check of what the rules admit and refute, not a measured
recall or precision result — no reviewer run, no corpus, no rescoring of any historical snapshot.
The pre-change pin is recorded there. Specified by
[issue #161](https://github.com/kamui/skills/issues/161), under
[epic #156](https://github.com/kamui/skills/issues/156). Identifier bumped to `v2b-2` with the
trailer example in [`publishing.md`](references/publishing.md#one-review-one-call) and this note; the
skill ships no validator that asserts the identifier, so nothing mechanical changed with it.

### C18. Unresolved evidence, material questions, and optional findings

Three channels had one boundary between them, and it sat in the wrong place. A `plausible` verdict
became an author question automatically, whatever had left it unsettled, so a claim a reader could
have settled by opening one more file reached the author as a request to finish the review. C13
turned every explicit deferral on unreleased public surface into an open question, whatever the
merge itself decided. And "accurate but sub-threshold" covered both a fact whose consequence was
shown absent and a consequence nobody had established, so an unproven safety aside could publish as
an observation beside the candidate it contradicted.

The holdout shows each edge. On (a) the ground truth records that "everything needed is in the diff
plus one function", and two of three `v5b` seeds still carried a false acquittal on that surface:
seed 2 published the contradiction as an observation next to the finding it undercut, and seed 3
refuted the candidate and added "the diff is correct as merged"
([holdout evaluation](../../docs/research/prototype-runs-holdout/evaluation.md) § "(a)",
[ground truth](../../docs/research/prototype-runs-holdout/README.md) § "Target (a)"). On (d) every
cell located the same preview naming deferral and the four Skeptic-line cells published nothing,
reasoning that "restating a question the maintainers had already deferred adds nothing a reviewer
can settle" — scored `under`, because the `prefer-*` values shipped through five releases before the
same author renamed them twelve days later (evaluation § "(d)", README § "Target (d)"). On (e) the
designated question was outcome-changing precisely because "the change's entire justification is
that number" (README § "Target (e)"). The assessment asks for the same three repairs in its B2, B6
and B8 rows: align what an approval establishes across every role without turning each deferred name
into a question; adopt explicit unresolved-evidence routing instead of deleting `plausible`; and
separate lack of consequence from lack of evidence
([assessment](../../docs/research/code-review-deep-publish-assessment-2026-09-05.md) § "What
shipped, and what to backport").

`confirmed` / `plausible` / `refuted` stays the verifier's vocabulary. B6's deletion is not copied:
the integrated arm leaving its own branch unused is not evidence that this one must lose the middle
verdict, and the routing repair is what the failures actually call for.

Six edits. `finding-format.md` gains § Settle, ask, or record, the ladder every unsettled thing now
takes: **settle it** where a reachable source answers it, **ask it** where an outcome-changing fact
no available source can settle remains, **record it** otherwise — with material nobody could read
and checks nobody finished leaving the ladder at coverage instead. Outcome-changing is defined there
as the ladder's own verdict test: the answer moves a decision this merge settles rather than one
somebody makes later, which covers present correctness, what the change releases, what consumers may
then depend on, and whether the change's stated justification holds. Priority moves nothing between
rungs, so a proven `P3` defect is a `consider` finding rather than an observation, and a published
question carries no priority and asks for no code change. `verify.md` names five refutation evidence
bases — contradiction, prevention, established intent, pre-existing behavior, no qualifying
consequence — each with the citation it requires, adds § Finish the legwork before any `plausible`
ruling, makes `plausible` carry which of trigger or impact is unsettled, the smallest settling fact,
and where
that fact must come from, and bars an aside that asserts a consequence the verifier never checked.
The two axis briefs carry the same intent test — an approval establishes exactly what it explicitly
accepted, a postponement is open evidence rather than acceptance — the Code brief settles a
reachable trigger before returning a candidate and treats a contradicted documented rule as a
candidate on its own account, and the Requirements brief routes its "cannot tell" bucket through the
ladder and gates the C13 deferral rule on the present decision. `publishing.md` gates the axis's
`Waiting for information` on a deferral that published as a question, states that an unresolved
record is never evidence the code is correct, drops a pooled observation asserting an unestablished
consequence, and requires stated reasoning before a decline is `accepted` — an author's word alone
never settles a verified blocker. `SKILL.md` routes the verifier's `plausible` through the same
ladder and reports the unresolved records that published nothing.

Acceptance table. Source, the channel it belongs in, and what it does to the status:

| Source | Expected channel | Status |
| --- | --- | --- |
| Race premise a reader can settle — a flag that cannot go false while a body exists | Read the source and rule: `confirmed` finding, or `refuted` and dropped | `Changes Requested` on a `must-fix`; unchanged when refuted |
| A required artifact the spec names that the diff never adds | Requirements finding, `must-fix` | `Changes Requested` |
| A deployment fact only an operator holds, and the merge decision turns on it | Question naming the operator and the measurement | `Needs Information`; Requirements `Waiting for information` |
| A benchmark justification nothing this merge decides turns on | Observation where the absence of consequence is established, else a ledger row | unchanged |
| A preview naming decision the record defers to a named gate, on a surface the repository's own compatibility policy exempts | Recorded: a `question`-disposition ledger row carrying the deferral, its author and the decision, counted unverifiable, reported to the caller | unchanged; the axis may pass |
| A deferral whose answer decides what this merge releases, or what consumers may already depend on | Question naming the deferral, its author and the decision | `Needs Information`; Requirements `Waiting for information` |
| A true, actionable defect at `P3` | `consider` finding at `P3` | unchanged — `consider` holds nothing back |
| An accurate fact with the absence of consequence established | Observation: pooled, deduplicated, capped at three | unchanged |
| Prose asserting safety with no consequence established — "correct as merged" | Not an observation: rule on the candidate it bears on, or name the check as unfinished | `Incomplete` where a material check is unfinished; never `Approved` on the prose |

Two properties the table holds fixed. A published question carries `action=question`, no priority
and no `fix` in its trailer, plus the standing "Change no code for this." line
(`finding-format.md` § The trailer). The observations channel keeps the cap of three, the pooled
cross-axis deduplication, and the `observation (unpublished, cap)` record in the run report that C5
specified; the only addition is dropping an item that asserts what nobody established.

Replayed against the corpus as instructions, not as measurements: no run was executed for this
change, and it claims no recall gain. On (d) the deferral still publishes as a question, and the
conjunct that decides it is the named gate: "I'm fine adjusting this later if we need to since it's
in preview" postpones without naming where, so the recorded rule cannot apply and rule 1 governs —
consistent with the `prefer-*` values reaching users in `0.2.14` four days after the merge. Test 4's
`removeCookies` deferral publishes on a different conjunct: its gate is named ("the pre-release api
review"), but no exemption covers the surface — the diff adds the method to the public API docs and
to the generated `types.d.ts`, and nothing in the packet marks it preview or unstable, which is an
inference from absence rather than a quoted policy. So the exemption fails on the available evidence
and rule 1 governs, as it does on its own release trigger. C13's paper check is unchanged. On (e)
the benchmark question still publishes: whether the change's stated justification holds is one of
the verdict-moving decisions the definition names, which is the ground truth's own reason for
designating it. On (a) the retry premise is settled by reading rather than left in the middle
verdict, seed 3's "correct as merged" is not a refutation on any of the five bases, and seed 2's
aside fails the observation bar — it asserts a consequence the run never established beside the
finding it contradicts, so it goes back as a ruling on that candidate. The test 2 Fable
`redis.conf` scope fact is unchanged from C5's paper check and shows the low-priority rule working:
it publishes as the confirmed `P3 consider` finding R2, and the Code finder's duplicate observation
of the same fact at the same `file:line` is what the pool drops — a proven defect at the bottom
priority stays a finding rather than sinking into the channel beside it.

The gate can bite in the wrong direction, and the (d) cells show how: read "preview" as the author's
word in the thread and the question disappears, which is the outcome the holdout scored `under`. The
recorded rule therefore keys on what the repository marks, what its compatibility policy promises,
and whether the record names the later gate — never on how a participant described the surface — and
the briefs say that already discussed and already deferred are not the test.

Two known softnesses, recorded rather than papered over. The `question` disposition now covers both
a published question and a recorded one, so which of the two a row is lives in the row's claim and
not in a mechanical field, while the axis outcome turns on that difference; the alternative was
`acquitted`, which the orchestrator forwards to the verifier as a related acquittal and a later
round reads as tried and killed, so the softness is the better trade. And the Code axis has no
`question` disposition to record an open consequence with, so such a row is `acquitted` with the
openness carried in its claim; `verify.md` § Related acquittals gains the ruling for a row that
names no premise, which is what keeps that record from being attacked as an acquittal it is not.

Expected cost is ≈0: the added work is a read the investigator should already have made, and the new
refusals remove output rather than adding it. Specified by
[issue #163](https://github.com/kamui/skills/issues/163). The workflow identifier advances to
`v2b-3` with this change.

### C19. Isolated verification and verdict accounting

Two holes sat in the verification boundary, and both let a verifier's silence read as a verdict.
Step 3 said that a verifier which "runs and returns nothing" is a clean review, so a worker that
timed out, truncated, or answered only the first three of five candidates approved the rest by
omission. And the only isolation mechanism was
[`build_verifier_prompt.py`](scripts/build_verifier_prompt.py) stripping `support` from the prompt,
which withholds the finder's argument from the text but cannot withhold a parent conversation from a
worker that inherits it — a forked sub-agent that has already read the finder reports agrees with
itself however clean its prompt is. The candidate schema compounded the second problem: without
`kind`, `impact`, or the proposed `change`, a verifier could rule on a claim without being told what
consequence was asserted or what repair was requested, and the later scope checks (#162) had
nothing to read.

Five edits, made as one packet-contract change. The candidate block gains `kind` (the routine
line's seven risk kinds, minus `compatibility`, which the audit has no released-contract admission
for yet), `impact`, and `change`, in a fixed thirteen-field order; the builder carries all three to
the verifier and still removes `support` mechanically, so the persuasive text never reaches the
worker while the raw citations and the requested repair do. The disposition ledger row gains a
per-run id (`code-3`, `requirements-1`) and the same `kind` as its first two fields, so every ruling
is matched back to one row unambiguously; the id lives for one run and is never the durable
`code/…` finding id, which survives across rounds. The builder now also writes an **accounting
packet** — every candidate id the verifier owes a verdict, every related acquittal row it owes a
ruling — and a new [`account_verifier_return.py`](scripts/account_verifier_return.py) checks the
return against it: exactly one well-formed verdict per candidate id, exactly one well-formed ruling
per row id, and a refusal for any missing, duplicate, unexpected, or malformed record, each
violation naming the record id where the row carries one. The orchestrator gets one shape-only
repair — a fresh worker handed the original prompt, the verifier's own return as the artifact to
repair, and the violation lines, told to preserve every judgment that return already carries and to
invent none — and never writes a verdict itself. After a second failure the script's own
`accounted:` and `withheld:` lines partition the packet: every id on the withheld line — missing,
duplicated, or malformed, whether or not a violation happened to name it — is withheld and coverage
says so, while every accounted id has exactly one conforming record and still publishes under the
ordinary status precedence. A zero-record return to a non-empty packet is a failure that takes the
same repair. An intentionally empty input — no candidates and, on a re-review, no code-decided
prior finding — takes the explicit clean-review path in `SKILL.md` on any round and dispatches no
verifier, so the accounting script refuses an empty packet outright rather than treating an absent
return as clean. `verify.md` gains an Isolation
section adapted from the routine line's `verifier.md`: a genuinely non-inheriting worker,
`fork_turns=none` where supported, with the pinned identity, the rule and spec pointers, and bounded
inspection; where the runtime cannot provide it, mandatory verification is incomplete, every
candidate is withheld, and nothing imitates independence in the parent.

The old shapes are refused by name, never misread. The validator and builder both refuse a ten-field
candidate as missing `kind` before `anchor`, and a four-field ledger row by count with the old
grammar named, so a finder still writing the earlier contract is sent back once for the same review
in shape rather than having its claim silently read as an id. The validator now also runs the
builder's candidate parser, so a candidate-shape violation gets the same one-shot re-dispatch a
ledger violation had; before, it surfaced at step 3 with no repair path. Prior findings on a
re-review reach the verifier through the builder's `--prior` input in the same grammar, so they join
the packet, owe a verdict like any candidate, and count as candidates when the builder selects the
related acquittal rows; the earlier text asked for them to be "added to the list" with no mechanism.

Kept fixed: the `confirmed` / `plausible` / `refuted` vocabulary, the five refutation bases, the
`holds` / `re-open` rulings, the related-only acquittal filter, the published finding shape and
trailer (no `kind=` key is published; the trailer vocabulary is unchanged and prior trailers stay
readable), and the verify-all posture — every candidate is mandatory, so there is no routing by
kind. Calibration and the clean-verdict and follow-up transitions belong to #162 and #164.

Evidence is mechanical where the change is mechanical, and a paper replay where it is policy. The
accounting cases — two candidates and one related row all returned; an empty return, a missing last
id, a duplicate id, an unknown id, a malformed verdict; a refutation without its basis; a `holds`
citing only the row's own evidence; the empty-packet refusal — are CLI fixtures with asserted exit
codes in the two scripts' self-tests, and the packet cases — support text absent from the emitted
prompt with the requested repair present, and the same claim on both axes keeping two ids — are
fixtures in the builder's test runner. The isolation case is an instruction replay in the [replay
record](../../docs/research/audit-verifier-accounting-2026-09-12.md): it shows which rule text
withholds the output when no isolated worker exists, and it is not runtime evidence that any harness
provides the isolation or that an isolated verifier performs better. No reviewer was run for this
change and it claims no recall or precision gain. Specified by
[issue #160](https://github.com/kamui/skills/issues/160), under
[epic #156](https://github.com/kamui/skills/issues/156), whose own text names the empty-output gap;
the assessment's B5 row names the schema one. The workflow identifier advances to `v2b-4` with this change.

### C20. Complete input identity and same-head changes

Issue [#166](https://github.com/kamui/skills/issues/166), under [#156](https://github.com/kamui/skills/issues/156), replaces head/status duplicate suppression with full head/base/merge-base, workflow and normalized intent/guidance identity. The workflow advances to `v2b-5`; its run trailer adds `context`, `state`, `merged` and `output`, and `review_identity.py` asserts that version. Historical trailers remain readable for finding ids, replies, verdicts and the round cap, but cannot suppress a current-contract review.

The audit packages the routine skill's tested `forge_packet.py` and `context_fingerprint.py` mechanics delivered by #132, with their CLI fixtures, as local helpers. No sibling skill is required and no forge operation moves into Python. Step 1 persists all outer and nested pages, stable numeric ids, comment timestamps, explicit state/merged, missing slices and per-connection coverage. Audit additions retain continuation cursors, reject missing state/timestamp evidence for complete coverage, and compare the candidate's content to its publication `output` digest, excluding original timestamp drift and the phase-2 index update while retaining later content changes and replies. The input identity reference defines exact membership and type/order normalization, retaining this audit's existing broader guidance set and resolving the full applicable normative pointer closure before the duplicate gate and dispatch.

The new identity checker requires complete current and prior coverage, full matching identity and no later evidence. Undated resolution state conservatively defeats its shortcut. Changed same-head inputs trigger assessment and new eligible findings publish even when aggregate status stays unchanged; standing defects retain their ids and original threads, including human replies without trailers. A separate complete prepublication collection checks input freshness, and supplied missing merged state never becomes publication permission. Retrospective publication still requires explicit separate authority.

Validation combines the copied multi-page, edit-detection and digest fixtures with audit-specific CLI eligibility cases and an [instruction replay](../../docs/research/audit-input-identity-2026-09-12.md). These are mechanical regressions and paper policy transitions, not measured recall or precision gains. Full payload validation remains separate work; this ticket checks duplicate identity, not finding admission or review rendering. The addressing-round [replay](../../docs/research/audit-input-identity-addressing-2026-09-13.md) covers original-output drift and reproducible gate-time membership. The conservative later-state rule may repeat an assessment after harmless activity, and missing external evidence remains incomplete even when the visible pages normalize successfully.

### Subtractions

None structural. Beyond the deletions listed under C2 and C5, no working v2 machinery was removed
or made conditional.


## Deleted-file provenance (issue #84)

`v2b-6` adds merge-base links for known deleted whole files. The orchestrator derives `{coordinate, side}` from the full pinned merge-base manifest, retains it beside the pinned head/merge-base, and passes the same record to render and check for findings and questions, body repairs, index updates and the caller report. `--revision` remains head; `--side LEFT --merge-base <sha>` selects the established pre-image file. Missing merge-base or `UNKNOWN` file provenance produces an honest code span. Malformed supplied identity fails; LEFT lines and rename coordinates remain unlinked.

The later audit payload emitter must preserve this publication record and argument mapping in `references/publishing.md`; finder and verifier accounting grammars stay unchanged. Whole-file items remain body-resident and native `commit_id` and trailers stay at head. The paired routine release is `v5b-15`. CLI fixtures cover PR #118's exact deleted path and revision, ordinary links, malformed provenance and unavailable/ambiguous pre-images. These are mechanical checks only; no general LEFT-line, rename, observation or prior-finding provenance expansion is claimed. Earlier workflow trailers and stable ids remain readable history.

## Verb-first rename (issue #245)

`code-audit-publish` became `audit-code-publish` so that every skill name in this repository starts with its verb, ends in `-publish` when it writes to the forge, and stays clear of `code-review`, which the harness and skills from other sources use. Only names changed: the directory moved with `git mv`, and the frontmatter, `agents/openai.yaml` prompt, script descriptions, and current cross-references followed. Earlier notes in this file and the research records keep the name they were written under.

**Identifier retained: `v2b-6`.** Trailers, the context digest, and the finder and verifier grammars carry no skill name, so admission, verification, rendering, and state semantics are unchanged and earlier audits remain continuous.

## One-invocation fragment renders (issue #255)

Step 4 rendered each body coordinate with its own `link_coordinate.py render` call, and no decision sits between those calls once the publication record is fixed. It now documents one shell block with one `frag <n> <coordinate> <side> [--old-path <path>]` line per coordinate. Every line passes the same `--repo-url`, `--revision` (the reviewed head), and `--merge-base` that the Coordinate links contract names, so each fragment is byte-identical to a separate `render`. Each attempt writes into a fresh `mktemp -d` directory, and a fragment file is promoted from its `.part` file only after exit 0. The first failure prints the coordinate, its stdout (where `link_coordinate.py` prints violations), and its stderr, then exits with its status, so no later fragment renders and no body, `check`, or `output-digest` step consumes the failure. Body writing, `check`, and `output-digest` stay at the steps that depend on them.

`scripts/test_link_coordinate.py` runs the published block under every available `sh`, `bash`, `zsh`, and `dash`. The inputs are ordinary RIGHT, deleted LEFT, RIGHT line, UNKNOWN whole-file, and rename coordinates, and each fragment must match a direct render. A failing `UNKNOWN` line must exit 1 with its visible violation and leave only the earlier fragment. Rendering goes from one tool invocation per coordinate to one invocation per publication record. That is a mechanical count, not a model-request, time, or cost claim; #265 owns the matched assessment.

**Identifier retained: `v2b-6`.** Script arguments, fragment bytes, trailers, and digests are unchanged. `SKILL.md` grows from 5,198 words / 34,526 bytes to 5,399 / 35,898 (`wc -w`, `wc -c` on `origin/main` at `5ca40b5`).
