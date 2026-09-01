# Evaluating four agentic code-review prototypes on one pinned pull request

**2026-09-01.** This evaluates `code-review-publish-2` through
`code-review-publish-5` (v2-v5) as reviewer cores for frequent, unattended,
issue-aware pull-request review. It replaces the stale analysis of three
reviewers on different revisions of `kamui/shortlist#65`. The experiment here is
the controlled four-way run against one pinned revision of
[`kamui/shortlist#66`](https://github.com/kamui/shortlist/pull/66).

Raw records: [method and inputs](prototype-runs-2026-09-01-test-1/README.md),
[v2](prototype-runs-2026-09-01-test-1/v2-run.md),
[v3](prototype-runs-2026-09-01-test-1/v3-run.md),
[v4](prototype-runs-2026-09-01-test-1/v4-run.md),
[v5](prototype-runs-2026-09-01-test-1/v5-run.md),
[comparison data](prototype-runs-2026-09-01-test-1/comparison-data.md), and
[publication decision](prototype-runs-2026-09-01-test-1/publication-decision.md).

## Conclusion

**V4 and v5 produced equivalent-quality review artifacts, and v5 reached its
result with better verification behavior at slightly lower cost. That still does
not establish v5 as the better reviewer.** V5 was designed after the v2-v4
results on this exact pull request exposed calibration gaps, so its performance
here is development-set evidence with a real overfitting risk, not an
independent holdout result.

The two runs converged: the same two documentation-synchronization items, both
non-blocking, both independently verified, both ending in `Approved (advisory)`.
They differ only in impact signalling — v4 called the Narrow item P2, v5 called
it P3 — which changes nothing about the merge decision. V2 and v3 both derived
`Changes Requested` from the same underlying facts.

The evidence supports advancing v5:

- keep its integrated reviewer, fail-closed coverage, consequence-triggered
  fresh verification, action independent from priority, history-aware drift
  checks, outcome-level requirement reading, run identity, and atomic
  publication contract;
- keep the anchor/fix separation, which is what let it publish two findings
  whose repair sites are unchanged files without tripping the `introduced here`
  gate;
- scope that gate by candidate kind anyway, because its text is still unscoped
  and this run did not exercise the failure case; and
- freeze the workflow version before testing it on new, adjudicated pull
  requests.

On this PR the most defensible output is v4's or v5's: the Narrow entrypoint
inconsistency and the bundle-contract enumeration as non-blocking `consider`
findings, and `Approved (advisory)`. V2 and v3 overstate the merge consequence.

## Controlled method

All prototypes received the same phase-1 inputs:

| Input | Pinned value |
| --- | --- |
| Pull request | [`kamui/shortlist#66`](https://github.com/kamui/shortlist/pull/66) |
| Head | [`4349ff41ff4d134e09017662dd30420b80e8eb30`](https://github.com/kamui/shortlist/commit/4349ff41ff4d134e09017662dd30420b80e8eb30) |
| Base and merge-base | `ccd1842d742fd940b2afde4f903c7bdcb3a707eb` on `main` |
| Diff | 9 files, +160/-6, one commit |
| Specification | [`kamui/shortlist#45`](https://github.com/kamui/shortlist/issues/45), 10 acceptance criteria, no comments |
| Prior review state | none |
| Publication authority | self-review; `COMMENT` only |
| Model | Claude Opus 5 (1M context), High reasoning |
| Harness | Claude Code CLI; sub-agents via its `Agent` tool |

Each run used an isolated clone at that head, with `main` fixed to the same base.
The orchestrator supplied the same PR, issue, manifest, and empty prior-review
state, and every run — orchestrator, reviewer, and verifier alike — used the same
model at the same reasoning setting under the same harness, so the cost columns
below are directly comparable. V2-v4 ran without publication; v4 was selected and
published only after those runs completed. V5 ran later with publication disabled
and the original empty review state, so the live v4 review did not enter its
runtime context. See the
[controlled conditions](prototype-runs-2026-09-01-test-1/README.md#conditions-held-constant).

The controls do not create ground truth. This is one documentation/schema-heavy
change in one repository, one run per prototype, with no independent
adjudication of disputed findings. The reviewer author and PR author are the
same person. The experiment measures behavior, calibration, and operational
discipline, not population-level recall or false-positive rate.

V5 is also adaptive. Its own
[`DESIGN.md`](https://github.com/kamui/skills/blob/0c110187ade59af364845cb44ff77f4199bc2015/skills/code-review-publish-5/DESIGN.md#L32-L36)
says this v2-v4 run exposed the calibration gaps it changes. Runtime isolation
prevents direct contamination, but not design-time exposure to the target.

## Architecture, output, and cost

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Architecture | parallel Code + Requirements finders; mandatory fresh verifier | integrated reviewer; self-falsification | integrated reviewer; conditional fresh verifier | integrated reviewer; consequence-triggered fresh verifier |
| Verifier routing | every candidate | large/coupled/high-risk change or difficult high-impact claim; skipped here | every `must-fix` and named high-risk/contract category | every `must-fix` and consequential-risk category; names alone do not trigger |
| Agents | 3 | 1 | 2 | 2 |
| Sub-agent tokens | **253,712** | **110,630** | **175,824** | **174,563** |
| Tool uses | 118 | 49 | 78 | 64 |
| Wall time | ~851 s | ~663 s | ~879 s | ~986 s |
| Candidates | 6 + 1 passed along | 10 | 10 | 6 |
| Findings | 4: P1/P1/P2/P2 | 1: P2 blocking | 2: P2/P3, non-blocking | 2: P3/P3, non-blocking |
| Status | Changes Requested | Changes Requested | Approved | Approved |
| Coverage | complete, both finders 9/9 | complete manifest/risk report; unrecovered PR-body gap disclosed | incomplete, then complete after recovery | complete |

The source packages show the progression:

- [v2](https://github.com/kamui/skills/blob/f42f70835fbe8aec1a5085d9b75d47d76ef11891/skills/code-review-publish-2/SKILL.md#L44-L77)
  partitions Code and Requirements, then sends every claim—without finder
  `support`—to a fresh verifier. It separates `anchor` from `fix` and `claim`
  from `support`, but derives action from priority.
- [v3](https://github.com/kamui/skills/blob/a73314fdd30b1a2d4b1a57a4987e37651b160109/skills/code-review-publish-3/SKILL.md#L38-L52)
  collapses both axes into one reviewer with a requirement ledger, risk checks,
  manifest, and same-context falsification. Verification is exceptional.
- [v4](https://github.com/kamui/skills/blob/f6ee104eed7bb814b1911502a2c4fbb91329c815/skills/code-review-publish-4/SKILL.md#L44-L56)
  adds candidate-triggered verification, claim/support isolation, explicit
  action, distinct anchor/fix sites, and a context fingerprint.
- [v5](https://github.com/kamui/skills/blob/0c110187ade59af364845cb44ff77f4199bc2015/skills/code-review-publish-5/SKILL.md#L44-L56)
  routes by action and consequence, strengthens outcome/history checks, and
  adds bounded prose plus a file-anchor/body fallback.

V3 is the cheapest measured run: 44% of v2's tokens and 63% of v4's. V2's
parallel finders reduce latency but duplicate the expensive whole-diff/context
pass, and cost 45% more tokens than either single-reviewer-plus-verifier run.

V4 and v5 are within 1% of each other on tokens (175,824 versus 174,563) and
split their spend almost identically between reviewer and verifier (27% each).
V5 does the same work in 18% fewer tool calls, which is consistent with routing
verification by action rather than by artifact name. It is also the slowest run
end to end, because its serial reviewer-then-verifier path carried two
candidates through the batch rather than short-circuiting.

Cost differences at this scale are not decision-grade. Nothing here separates v4
from v5 economically. The full breakdown is in
[comparison data](prototype-runs-2026-09-01-test-1/comparison-data.md#cost-and-shape).

## Complete finding-agreement matrix

Twelve distinct items appeared. “Dropped” includes primary falsification,
fresh-verifier refutation, and pre-candidate acquittal; the run files preserve
the exact route.

| Candidate | v2 | v3 | v4 | v5 | Best-supported interpretation |
| --- | --- | --- | --- | --- | --- |
| Narrow entrypoint's closed refresh list | P1 `must-fix` | P2 blocking | P2 `consider` | P3 `consider` | real synchronization drift; non-blocking `consider` is the defensible band |
| Bundle contract omits the new Kind by name | P1 `must-fix` | dropped | P3 `consider` | P3 `consider` | normative drift; runtime omission unproved; P3 is right |
| Completion validator's volatile regex is commerce-only | P2 `consider` | dropped | not raised | not raised | asymmetry exists, but predates the change and no wrong generalized outcome is shown |
| No dedicated freshness-expectation field | P2 `consider` | AC4 met | dropped | AC4 met | representation question, not a demonstrated defect |
| Research protocol's commerce branch excludes generalized claims | refuted | not raised | not raised | dropped | false; `Observed` is required on every Evidence record in both bundle forms |
| Attestation test treats incomplete fixture as complete | refuted | dropped after execution | dropped after execution | acquitted pre-candidate | false; mutation is required setup |
| `PROJECT_BRIEF.md` / ADR seed lists are stale | not raised | dropped | dropped | dropped | pre-existing; demonstrably not lockstep peers |
| Research entrypoint omits refine/mark-inapplicable | acquitted | dropped | dropped | not raised | valid protocol deferral, not a competing closed list |
| Schema bump required for widened enum | not raised | not raised | dropped | no break found | additive and matches repository precedent |
| `narrowing-protocol.md:68` cites "the ledger" in a commerce-shared section | not raised | not raised | not raised | dropped | imprecise but the sentence supplies the list inline; no wrong outcome |
| Streaming fixture record 8's negative `Why it applies` | not raised | not raised | not raised | dropped | the base fixture uses the identical idiom |
| Freshness-attestation timing | not raised | not raised | not raised | not raised | — |

Raw dispositions:
[finding-level agreement](prototype-runs-2026-09-01-test-1/comparison-data.md#finding-level-agreement).

### Narrow: the central disagreement

All four found the unchanged Narrow entrypoint sentence, and all four confirmed
it. The facts agree:

- the entrypoint requires reading the
  [narrowing protocol](https://github.com/kamui/shortlist/blob/4349ff41ff4d134e09017662dd30420b80e8eb30/skills/shortlist-narrow/SKILL.md#L10-L12)
  and later says to
  [follow it](https://github.com/kamui/shortlist/blob/4349ff41ff4d134e09017662dd30420b80e8eb30/skills/shortlist-narrow/SKILL.md#L35-L46);
- its point-of-use refresh sentence still names fixed commerce and generalized
  sets without “for example” or another explicit escape;
- the changed protocol says to refresh
  [every applicable ledger-defined Volatile class](https://github.com/kamui/shortlist/blob/4349ff41ff4d134e09017662dd30420b80e8eb30/skills/shortlist/references/narrowing-protocol.md#L66-L70),
  “not only a fixed commerce list,” including Research-added classes; and
- the new fixture contains a Research-added
  [ad-tier feature and price-lock class](https://github.com/kamui/shortlist/blob/4349ff41ff4d134e09017662dd30420b80e8eb30/tests/fixtures/generalized-bundle-streaming/ledger.md#L63-L71).

The disagreement is entirely about consequence. V2 made it a P1 merge blocker.
V3 made it a P2 blocker. V4 called it P2 `consider`. V5's primary proposed P2
`must-fix` and its verifier downgraded it to P3 `consider`, on the ground that
`SKILL.md:37` requires following the protocol, so canonical behavior is intact
and merge does not depend on resolving the restatement.

Two runs added evidence the others lacked. V3 established the lockstep history:
commit `1450bc2` introduced the protocol and entrypoint sentences together. V4's
verifier established that they matched at the merge-base, that line 46 is the
only stage-entrypoint refresh instruction, and that no mechanical test checks
consistency; it correctly narrowed the mechanism to conflicting point-of-use
restatement rather than total omission.

V5's verifier added the sharpest single fact: the stage skill omits the
`policy terms` class that
[`record-schemas.md:392`](https://github.com/kamui/shortlist/blob/4349ff41ff4d134e09017662dd30420b80e8eb30/skills/shortlist/references/record-schemas.md#L392)
now names, and `grep -c policy skills/shortlist-narrow/SKILL.md` returns `0`.
That replaced the primary's weaker trigger example, which had cited fixture
classes the skill's existing terms already cover.

`Consider` is the right band. Between P2 and P3 there is no evidence to settle
it, and the merge decision is identical either way.

### Bundle-contract enumeration

The bundle contract ends its list with
[`or other category-relevant work`](https://github.com/kamui/shortlist/blob/4349ff41ff4d134e09017662dd30420b80e8eb30/skills/shortlist/references/search-bundle-format.md#L202-L208)
and links the formal schema, which names
[`Volatile-claim class`](https://github.com/kamui/shortlist/blob/4349ff41ff4d134e09017662dd30420b80e8eb30/skills/shortlist/references/record-schemas.md#L380-L394).

V2 made the absent literal name P1. V3 dropped it because the list is open and
the enum is linked. V4 proved the contract and protocol lists matched at base and
that a previous Kind addition updated all copies; its verifier then cut the
impact to normative inconsistency and retained P3 `consider`. V5 reached the same
P3 `consider` and deepened the history: `1c25a91` *and* `55e1f25` each extended
the same four-document set together, so the lockstep precedent is two commits
deep, and `55e1f25`'s message names `search-bundle-format.md` explicitly.

Three of four runs confirming it at a non-blocking priority is the strongest
agreement in the experiment. P1 is not supportable; dropping it entirely, as v3
did, is defensible for a high-signal reviewer but discards a provable drift.

## Requirement-ledger divergence

| | Met | Partial / not met | Unverifiable |
| --- | ---: | --- | ---: |
| v2 | 7 | AC1, AC4, AC6 | 0 |
| v3 | 8 | AC5 protocol-only; AC6 partial | 0 |
| v4 | 10 | none; AC1/5/6 “met, with propagation gap” | 0 |
| v5 | 10 | none | 0 |

All ran 290 Python and 60 Node tests successfully under a modern Python. V2 and
v4 found no scope creep; v4/v5 explicitly checked both non-goals.

The counts encode different models, not independent truth. V2 treats
unsynchronized representations as incomplete implementation. V3 emphasizes
observable paths. V4 separates outcome compliance from optional propagation
quality. V5 goes furthest toward outcome-level acquittal — it closed AC4 on the
ground that `record_schemas.py:336-343` already makes `Observed` a required field
on every Evidence record, so no new freshness field is needed for the criterion
to be met. That is the correct reading, and it is the same reasoning that let it
drop two candidates the earlier runs spent effort on.

A textual risk remains across v3-v5: all eight admission gates include unscoped
“introduced here.” An explicit acceptance-criterion omission can live in an
unchanged file, because the issue made updating it this change's responsibility.
V2's
[`verify.md`](https://github.com/kamui/skills/blob/f42f70835fbe8aec1a5085d9b75d47d76ef11891/skills/code-review-publish-2/references/verify.md#L19-L25)
states the needed exception: pre-existing refutation applies to Code candidates,
never Requirements candidates.

This run did not exercise the failure. V5 published two findings whose repair
sites are unchanged files (`search-bundle-format.md:208`,
`shortlist-narrow/SKILL.md:46`) without the gate blocking them, because the
anchor/fix separation kept each anchor on a changed line. It also used gate 2
correctly to drop the ADR/`PROJECT_BRIEF` candidate, having proved those files
were never lockstep peers. The mechanism works; the wording is still permissive
enough to misfire on a requirements candidate with no changed-line anchor at all.

## Verifier behavior

| | Input discipline | Verdicts | Material effect |
| --- | --- | --- | --- |
| v2 | every claim; `support` withheld | 4 confirmed, 2 refuted, 1 merge | removed two false candidates, merged duplicate, corrected triggers/scope |
| v3 | not invoked | n/a | primary self-falsification dropped 9/10 |
| v4 | two survivors; `support` withheld | 2 confirmed | corrected Narrow mechanism/citation; cut bundle impact |
| v5 | two survivors; claim/raw citations only, `support` withheld | 2 confirmed | replaced a bad trigger example; downgraded P2 `must-fix` to P3 `consider`, changing the status from Changes Requested to Approved |

V2 shows both value and limit: fresh reconstruction caught factual errors but
did not cure over-calibrated admission and action rules. V3 shows same-context
falsification can be strong and cheap, but its change-level threshold skipped a
second look at its sole blocker. V4 and v5 show the best corrective behavior,
and v5's is the most instructive: it separated the factual verdict from the
action calibration, confirming the claim while disproving the merge consequence.
That is precisely the verdict shape a binary confirm/refute court cannot express,
and it is why v5's sole blocker became a published optional finding rather than
either a false blocker or a silently erased issue.

V5's verifier also supplied a fact its primary had missed — the second lockstep
commit — which the primary independently re-verified before citing. And the
primary did not accept the correction uncritically: it recorded that the
verifier's characterization of ad-tier features as “catalog” is contestable
against `check_freshness.py:106-107`, while accepting the substitution because
the original example was unclean either way.

Neither v4's nor v5's verifier refuted anything. Only v2's did. Whether that
reflects better primary falsification downstream of v3, or verifiers that agree
too readily with a well-argued claim, is not separable from this run.

No run exercised a published author question. No controlled run verified a
genuine executable blocker, security/data-loss claim, or race. The
`plausible`-to-question path remains entirely untested — across four runs, no
verifier returned `plausible` even once.

## Prototype verdicts

**V2 — recall baseline, not production frequent path.** It found the widest
set, exposed cross-axis duplication, and demonstrated meaningful fresh
refutation. It is by far the most expensive and couples severity to merge
action, turning documentation drift into P1 blockers. Keep its claims-only
verification, anti-over-refutation, Requirements exception, and explicit agent
actions; retire the always-two-finders architecture.

**V3 — measured cost baseline.** One agent delivered complete inspection,
requirements, risk checks, and strong execution/history-based falsification at
the lowest measured cost. Its verifier threshold failed to challenge its only
consequential conclusion, and its missing-context handling was weaker than
v4's. Self-falsification is viable; it is not proven sufficient for blockers.

**V4 — the published artifact, and still a strong one.** It retained both real
drifts, made both optional, improved them through verification, and handled
coverage recovery transparently. Its “public contract” verification trigger was
ambiguous enough that it stopped to ask, which is good behavior from a bad rule.

**V5 — same artifact quality, better verification behavior, calibration still
unproven.** Consequence-based routing, outcome reading, history checks, and
publication hardening all did visible work: it matched v4's findings, added the
decisive `policy terms` fact, reached complete coverage without a recovery
round, dropped four candidates on defensible grounds including two nobody else
raised, and produced the run's only action-calibrating verdict. Against that: it
was the slowest run, its P3 for the Narrow item is a notch below where the
evidence naturally sits, and the target informed its design. Freeze and test it;
do not treat matching v4 on v4's own development set as proof of superiority.

## Publication outcome

V4 was selected after v2-v4 and posted as
[review 5076220814](https://github.com/kamui/shortlist/pull/66#pullrequestreview-5076220814):

- [P2 Narrow `consider`](https://github.com/kamui/shortlist/pull/66#discussion_r3902611240)
- [P3 bundle-contract `consider`](https://github.com/kamui/shortlist/pull/66#discussion_r3902611259)

The self-review used `COMMENT`, stated `Approved (advisory)`, rechecked the head,
validated anchors, fingerprinted context, and submitted one batch. V2/v3 were
withheld. V5 ran later and was withheld; posting it after v4 would test re-review,
not the controlled first-review condition. Its would-be output names the same two
items at P3/P3 with the same `Approved (advisory)` status, so nothing about the
published artifact would change materially. The
[publication record](prototype-runs-2026-09-01-test-1/publication-decision.md)
says this selection was not a categorical prototype verdict.

## Recommendation and unresolved experiments

Advance v5 with one correction: scope change attribution by kind, so an explicit
linked requirement is judged by whether this change was responsible for the
outcome, not by whether the omitted file happened to change. Retain v5's rule
against inventing fields, schemas, or tests where outcomes admit several
representations, its separation of factual verdict from action calibration, and
history as evidence rather than an automatic finding.

Then pre-register the workflow version and run a frozen, blinded evaluation:

1. known-clean and adjudicated known-defective PRs, including executable bugs
   and requirements omitted from unchanged files;
2. a behavioral Narrow test: do agents given both documents refresh the
   Research-added ad-tier/price-lock class?;
3. a true low-impact inconsistency intentionally proposed as `must-fix`, to
   confirm the downgrade behavior observed here is reliable rather than a single
   favorable draw;
4. genuine correctness, security, compatibility, data-loss, and hard-to-replay
   claims exercising `confirmed`, `plausible`, and `refuted` — no run has yet
   produced a `plausible` verdict or a published question;
5. repeated seeds and large/coupled diffs to measure variance and context limits;
   every result here is n=1 per prototype; and
6. re-review, stale head, missing context, invalid anchors, file-only findings,
   ambiguous writes, and v5's GitHub body fallback.

V5's own run also surfaced six concrete under-specifications in its output
contract — `consider` permission-sentence placement, `guidance` membership for
the context digest, trailer SHA width, the line-anchor coordinate format, the
circular `consider`-inclusion clause for the verifier batch, and the missing
tie-break for multi-file drift anchors. The digest one matters most: two
reviewers can compute different `context` values from identical inputs, which
directly weakens the duplicate-review check that digest exists to serve. All six
are listed with proposed fixes in the
[v5 run record](prototype-runs-2026-09-01-test-1/v5-run.md#run-conditions-and-observed-ambiguity).

Until the frozen evaluation runs: v4 won observed artifact quality by a margin
too thin to call, v3 won measured economy, and v5 is the architecture worth
carrying forward.
