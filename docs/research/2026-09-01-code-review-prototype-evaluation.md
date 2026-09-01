# Evaluating four agentic code-review prototypes on one pinned pull request

**2026-09-01.** This evaluates `code-review-publish-2` through
`code-review-publish-5` (v2-v5) as reviewer cores for frequent, unattended,
issue-aware pull-request review. It replaces the stale analysis of three
reviewers on different revisions of `kamui/shortlist#65`. The experiment here is
the controlled four-way run against one pinned revision of
[`kamui/shortlist#66`](https://github.com/kamui/shortlist/pull/66).

Raw records: [method and inputs](prototype-runs-2026-09-01/README.md),
[v2](prototype-runs-2026-09-01/v2-run.md),
[v3](prototype-runs-2026-09-01/v3-run.md),
[v4](prototype-runs-2026-09-01/v4-run.md),
[v5](prototype-runs-2026-09-01/v5-run.md),
[comparison data](prototype-runs-2026-09-01/comparison-data.md), and
[publication decision](prototype-runs-2026-09-01/publication-decision.md).

## Conclusion

**V4 produced the best review artifact observed here. V5 has the best
architecture to advance, but this run does not establish that v5 is the best
reviewer.** V5 was designed after the v2-v4 results on this exact pull request
exposed calibration gaps, so its clean result is development-set evidence with
a real overfitting risk, not an independent holdout result.

The evidence supports a synthesis:

- keep v5's integrated reviewer, fail-closed coverage, consequence-triggered
  fresh verification, action independent from priority, history-aware drift
  checks, outcome-level requirement reading, run identity, and atomic
  publication contract;
- scope the `introduced here` gate so an explicit requirement omission cannot be
  acquitted merely because the omitted artifact predates the pull request;
- prevent the verifier from erasing a factually established optional
  consistency issue merely because its proposed `must-fix` action was too
  strong; and
- freeze that revision before testing it on new, adjudicated pull requests.

On this PR, the most defensible output remains close to v4's: the Narrow
entrypoint inconsistency as P2 `consider`, the bundle-contract list as at most P3
`consider`, and `Approved (advisory)`. V2 and v3 overstate the first item's merge
consequence. V5 likely over-refutes it.

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

Each run used an isolated clone at that head, with `main` fixed to the same base.
The orchestrator supplied the same PR, issue, manifest, and empty prior-review
state. V2-v4 ran without publication; v4 was selected and published only after
those runs completed. V5 ran later with publication disabled and the original
empty review state, so the live v4 review did not enter its runtime context. See
the [controlled conditions](prototype-runs-2026-09-01/README.md#conditions-held-constant).

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
| Sub-agent tokens | **253,712** | **110,630** | **175,824** | unavailable |
| Tool uses | 118 | 49 | 78 | 41 |
| Wall time | ~851 s | ~663 s | ~879 s | unavailable |
| Candidates | 6 + 1 passed along | 10 | 10 | 4 |
| Findings | 4: P1/P1/P2/P2 | 1: P2 blocking | 2: P2/P3, non-blocking | 0 |
| Status | Changes Requested | Changes Requested | Approved | Approved, no findings |
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

V3 is the cheapest measured run: 44% of v2's tokens and 63% of v4's. V4 costs
less than v2 but more than v3, and its serial primary-plus-verifier path was the
slowest measured. V2's parallel finders reduce latency but duplicate the
expensive whole-diff/context pass.

V5 used the fewest reported tool calls, but **cannot be called cheapest**. Its
harness exposed neither sub-agent tokens nor end-to-end time; its five verifier
orchestration calls also contained 21 shell-command invocations. The full caveat
is in [comparison data](prototype-runs-2026-09-01/comparison-data.md#cost-and-shape).

## Complete finding-agreement matrix

Ten distinct items appeared. “Dropped” includes primary falsification,
fresh-verifier refutation, and pre-candidate acquittal; the run files preserve
the exact route.

| Candidate | v2 | v3 | v4 | v5 | Best-supported interpretation |
| --- | --- | --- | --- | --- | --- |
| Narrow entrypoint's closed refresh list | P1 `must-fix` | P2 blocking | P2 `consider` | primary P2 `must-fix`, verifier-refuted | real synchronization ambiguity; P2 `consider` is best calibrated |
| Bundle contract omits the new Kind by name | P1 `must-fix` | dropped | P3 `consider` | dropped | normative drift; runtime omission unproved; at most P3 |
| Completion validator's volatile regex is commerce-only | P2 `consider` | dropped | not raised | not raised | asymmetry exists, but predates the change and no wrong generalized outcome is shown |
| No dedicated freshness-expectation field | P2 `consider` | AC4 met | dropped | dropped | representation question, not demonstrated defect |
| Research protocol's commerce branch excludes generalized claims | refuted | not raised | not raised | not raised | false; generalized escape is in the same passage |
| Attestation test treats incomplete fixture as complete | refuted | dropped after execution | dropped after execution | not raised | false; mutation is required setup |
| Freshness-attestation timing is wrong | not raised | not raised | not raised | dropped | timing is not prohibited; judgment-only check is deliberate |
| `PROJECT_BRIEF.md` / ADR seed lists are stale | not raised | dropped | dropped | not raised | pre-existing; ADR is historical |
| Research entrypoint omits refine/mark-inapplicable | acquitted | dropped | dropped | not raised | valid protocol deferral, not a competing closed list |
| Schema bump required for widened enum | not raised | not raised | dropped | no break found | additive and matches repository precedent |

Raw dispositions: [finding-level agreement](prototype-runs-2026-09-01/comparison-data.md#finding-level-agreement).

### Narrow: the central disagreement

All four found the unchanged Narrow entrypoint sentence. The facts agree:

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

V3 added positive history evidence: commit `1450bc2` introduced the protocol and
entrypoint sentences together. V4's verifier established that they matched at
the merge-base, line 46 is the only stage-entrypoint refresh instruction, and no
mechanical test checks consistency. It correctly narrowed the mechanism: the
broad rule is reachable, so this is conflicting point-of-use restatement, not
total omission.

V5 treated that mitigation as acquittal. Required protocol reading and the
absence of literal “only” disproved the proposed blocker. That does not fully
refute the drift: the local sentence has exhaustive-looking bundle branches,
historically moved with the protocol, is now narrower, and is executable agent
guidance. P2 `consider` is proportional.

This exposes a v5 verdict-shape defect. A verifier should be able to say “the
must-fix consequence is unproved, but the authoritative synchronization claim
is confirmed as optional.” Refuting the entire record because its action is too
strong conflates factual verification with action calibration.

### Bundle-contract enumeration

The bundle contract ends its list with
[`or other category-relevant work`](https://github.com/kamui/shortlist/blob/4349ff41ff4d134e09017662dd30420b80e8eb30/skills/shortlist/references/search-bundle-format.md#L202-L208)
and links the formal schema, which names
[`Volatile-claim class`](https://github.com/kamui/shortlist/blob/4349ff41ff4d134e09017662dd30420b80e8eb30/skills/shortlist/references/record-schemas.md#L380-L394).

V2 made the absent literal name P1. V3/v5 dropped it because the list is open
and the enum is linked. V4 proved the contract and protocol lists matched at
base and that a previous Kind addition updated all copies; its verifier then cut
the impact to normative inconsistency and retained P3 `consider`.

V4's factual framing is strongest. Publishing a one-line consistency issue is
a policy choice; omitting it is defensible for a high-signal reviewer. P1 is not.

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
quality. V5 goes furthest toward outcome-level acquittal. V4's two-layer model
is clearest for this PR.

One defect remains across v3-v5: all eight admission gates include unscoped
“introduced here.” An explicit acceptance-criterion omission can live in an
unchanged file because the issue made updating it this change's responsibility.
V2's
[`verify.md`](https://github.com/kamui/skills/blob/f42f70835fbe8aec1a5085d9b75d47d76ef11891/skills/code-review-publish-2/references/verify.md#L19-L25)
states the needed exception: pre-existing refutation applies to Code candidates,
never Requirements candidates. Outcome and representation gates may still
acquit the freshness-field claim; pre-existence alone should not.

## Verifier behavior

| | Input discipline | Verdicts | Material effect |
| --- | --- | --- | --- |
| v2 | every claim; `support` withheld | 4 confirmed, 2 refuted, 1 merge | removed two false candidates, merged duplicate, corrected triggers/scope |
| v3 | not invoked | n/a | primary self-falsification dropped 9/10 |
| v4 | two survivors; `support` withheld | 2 confirmed | corrected Narrow mechanism/citation; cut bundle impact |
| v5 | sole must-fix; claim/raw citations only | 1 refuted | changed blocker/Changes Requested into no finding/Approved |

V2 shows both value and limit: fresh reconstruction caught factual errors but
did not cure over-calibrated admission and action rules. V3 shows same-context
falsification can be strong and cheap, but its change-level threshold skipped a
second look at its sole blocker. V4 shows the best corrective behavior: its
verifier made both claims more accurate and less severe. It also recovered a
failed PR-body fetch only after the primary correctly reported provisional
`Incomplete`; v3 disclosed the same gap less conservatively. V5 shows why
must-fix verification matters and why a binary admission court can over-acquit.

No run exercised a published author question. No controlled run verified a
genuine executable blocker, security/data-loss claim, or race. The
`plausible`-to-question path remains substantially untested.

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

**V4 — best observed author artifact.** It retained the two real-looking drifts,
made both optional, improved them through verification, and handled coverage
recovery transparently. It was slower and its “public contract” trigger was
ambiguous. It wins artifact quality, not general architecture.

**V5 — architecture to advance, calibration unproven.** Consequence-based
routing, outcome reading, history checks, and publication hardening are the
right direction. But cost is missing, candidate count fell from ten to four,
the target informed its design, and its sole verifier decision may have erased
a valid optional issue. Freeze and test it; do not call this zero-finding result
superior precision yet.

## Publication outcome

V4 was selected after v2-v4 and posted as
[review 5076220814](https://github.com/kamui/shortlist/pull/66#pullrequestreview-5076220814):

- [P2 Narrow `consider`](https://github.com/kamui/shortlist/pull/66#discussion_r3902611240)
- [P3 bundle-contract `consider`](https://github.com/kamui/shortlist/pull/66#discussion_r3902611259)

The self-review used `COMMENT`, stated `Approved (advisory)`, rechecked the head,
validated anchors, fingerprinted context, and submitted one batch. V2/v3 were
withheld. V5 ran later and was withheld; posting it after v4 would test re-review,
not the controlled first-review condition. The
[publication record](prototype-runs-2026-09-01/publication-decision.md) says this
selection was not a categorical prototype verdict.

## Recommendation and unresolved experiments

Advance v5 with two corrections:

1. Scope change attribution by kind: explicit linked requirements are judged by
   whether this change was responsible for the outcome, not whether the omitted
   file happened to change.
2. Separate factual verdict from action correction: after disproving
   `must-fix`, assess whether the core claim survives as `consider` before using
   `refuted`.

Retain v5's rule against inventing fields, schemas, or tests where outcomes admit
several representations. Keep history as evidence, not an automatic finding.
Then pre-register the workflow version and run a frozen, blinded evaluation:

1. known-clean and adjudicated known-defective PRs, including executable bugs
   and requirements omitted from unchanged files;
2. a behavioral Narrow test: do agents given both documents refresh the
   Research-added ad-tier/price-lock class?;
3. a true low-impact inconsistency intentionally proposed as `must-fix`, where
   the verifier should downgrade rather than erase it;
4. genuine correctness, security, compatibility, data-loss, and hard-to-replay
   claims exercising `confirmed`, `plausible`, and `refuted`;
5. repeated seeds and large/coupled diffs to measure variance and context limits;
6. re-review, stale head, missing context, invalid anchors, file-only findings,
   ambiguous writes, and v5's GitHub body fallback; and
7. complete v5 input/output token, wall-time, tool, and verifier-share capture.

Until then: v4 won observed artifact quality, v3 won measured economy, and v5
is the architecture worth testing next.
