# Evaluating four agentic code-review prototypes on a merged upstream C pull request

**2026-09-01.** This analyzes the second controlled four-way run of
`code-review-publish-2` through `code-review-publish-5` (v2-v5), against
[`redis/redis#15680`](https://github.com/redis/redis/pull/15680). It is the
holdout counterpart to the
[first evaluation](2026-09-01-code-review-prototype-evaluation.md), which used a
documentation- and schema-heavy pull request in the reviewer author's own
repository.

Raw records: [method and inputs](prototype-runs-2026-09-01-test-2/README.md),
[v2](prototype-runs-2026-09-01-test-2/v2-run.md),
[v3](prototype-runs-2026-09-01-test-2/v3-run.md),
[v4](prototype-runs-2026-09-01-test-2/v4-run.md),
[v5](prototype-runs-2026-09-01-test-2/v5-run.md), and
[comparison data](prototype-runs-2026-09-01-test-2/comparison-data.md).

## Conclusion

**All four prototypes produced the same review: zero findings, zero questions,
complete coverage, `Approved (advisory)`. The architectures are therefore
indistinguishable on this pull request, and this run discriminates far less
between them than test 1 did.**

That is not a null result, but it is a narrow one. What it establishes:

- **No prototype manufactured a finding on a clean, expert-reviewed change.**
  Between them the four runs raised 29 candidates and killed every one. On a
  400-line change to redis cluster failover and replication — exactly the
  material where a reviewer that pattern-matches on risk words would invent
  problems — none of them published anything. Test 1 could not establish this,
  because that pull request contained two real drifts.
- **Prior approval did not anchor them.** The PR carried an `APPROVED` review and
  a detailed technical LGTM. Three of four runs explicitly re-derived the LGTM's
  ordering claims from source rather than accepting them, and none cited the
  approval as a reason to stop looking.
- **The no-issue path is where the architectures actually diverge here**, and
  v2's is materially weaker than the other three.

What it does not establish: anything about verification. **No fresh-context
verifier ran in any of the four runs**, because no candidate survived
falsification anywhere. The machinery that produced almost all of test 1's
behavioral differences is entirely unobserved on this target.

There is one substantive disagreement, and it is invisible in the outputs. See
[the `redis.conf` scope mismatch](#the-one-real-disagreement).

## Controlled method

| Input | Pinned value |
| --- | --- |
| Pull request | [`redis/redis#15680`](https://github.com/redis/redis/pull/15680), merged at run time |
| Head | `c54fa4184e7db1ea30c91916f6c0aeb12b5c3f61` |
| Base and merge-base | `065d397030712fe216e795720ae0affd3211212c` on `unstable` |
| Diff | 5 files, +401/−1, two commits |
| Specification | **none** — no closing reference, no linked issue |
| Prior review state | 1 `APPROVED` (`sundb`); 3 comments including a detailed technical LGTM (`shun-lee`) |
| Posting identity | `kamui`, not the author — ordinary first review, `COMMENT` |
| Model | GLM-5.3-Flash, High reasoning |
| Harness | opencode CLI with context-mode MCP |

Each run got an offline clone with `origin` pointed at a local path, the same
phase-1 packet verbatim, publication disabled, and network, builds, and test
execution forbidden. See
[conditions held constant](prototype-runs-2026-09-01-test-2/README.md#conditions-held-constant).

### This is not directly comparable to test 1

Three variables changed at once between the two experiments: the target pull
request, the model, and the harness. Test 1 ran on Claude Opus 5 (1M context)
under Claude Code; test 2 ran on GLM-5.3-Flash under opencode. **No difference
between test 1 and test 2 can be attributed to the pull request alone.** Within
test 2, all four runs share a model and harness, so the four-way comparison below
is internally valid; across tests, only the internally-valid conclusions of each
should be carried forward.

The harness also reports no token counts, so test 2 has **no cost data at all**.
Test 1's economy findings do not transfer.

### What ground truth is available

None, strictly. The PR was merged upstream with maintainer approval, which is
evidence that redis maintainers considered it correct — not proof that it is. A
unanimous clean verdict from four reviewers that agree with two human reviewers
is consistent with the change being clean and consistent with all six missing the
same thing. This experiment can show the reviewers do not over-flag; it cannot
show they would catch a real defect here.

## Architecture, output, and cost

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Agents spawned | **1** (of a possible 3) | 1 | 1 | 1 |
| Verifier run? | no — skipped by rule, no candidates | no — zero survivors | no — zero survivors | no — zero survivors |
| Candidates raised | **0** | **11** | 10 | 8 |
| Findings | 0 | 0 | 0 | 0 |
| Questions | 0 | 0 | 0 | 0 |
| Coverage | complete (5/5) | complete (5/5) | complete (5/5) | complete (5/5) |
| Status | Approved (advisory) | Approved (advisory) | Approved (advisory) | Approved (advisory) |
| Tokens | unavailable | unavailable | unavailable | unavailable |
| Tool uses (self-reported) | ~46 | 35 | 30 | 37 |
| Wall clock (orchestrator) | ~9 min | ~19 min | ~22 min | ~6 min |

**Every architecture collapsed to a single agent.** v2 is the striking case: its
three-agent design (two parallel axis finders plus a mandatory verifier) reduced
to one agent, because its own no-issue rule makes the Requirements axis
`Not applicable` and its verifier is skipped when finders return no candidates.
The prototype that is most expensive by design was the cheapest available shape
here, and none of its distinguishing machinery ran.

**The wall-clock numbers should not be read as cost.** v5 raised 8 candidates in
~6 minutes; v4 raised 10 in ~22 minutes. The ordering is uncorrelated with
candidate count, tool count, or architecture, and v2's own finder self-estimated
~20 minutes against an orchestrator-measured ~9. Without token data these spans
are dominated by model and harness variance, not by the skills. **Test 2 supplies
no usable economy signal.**

## The unanimous clean verdict

All four reviewers examined the same three decisive mechanisms and cleared all
three:

1. **Ordering of `replicationDiscardCachedMaster()` after `replicationSetMaster()`.**
   The discard looks suspiciously late. All four established that caching happens
   *inside* `replicationSetMaster` — via `freeClient(server.master)` →
   `replicationCacheMaster` for a replica, or `replicationCacheMasterUsingMyself`
   for a demoted master — so the PR's discard is the last writer and covers both
   paths.
2. **Consumers of `repl_down_since = 0`.** All four enumerated the read sites and
   found the cluster data-age computation is the intended consumer, and that
   `INFO`'s two readers already guard zero.
3. **Same-shard versus cross-shard gate semantics.** All four confirmed
   `shard_changed` is false for same-shard re-points, so partial resync is
   preserved where the history is valid.

Three of four independently reached the same disposition on the manual-failover
bypass (`CLUSTER FAILOVER` skips the data-age check): pre-existing, operator-
initiated, correctly scoped by the PR body's "automatic" qualifier. They reached
it through three different rubric vocabularies — v3 "refuted", v4 "falsified,
pre-existing", v5 "dropped, pre-existing" — which is convergence on substance
rather than on wording.

This is the run's most useful positive result. A reviewer aimed at unattended
operation must not generate findings on clean changes, and four architectures
tested against a genuinely intricate concurrency change all declined to.

## The one real disagreement

**Only v2 noticed that the new `redis.conf` paragraph is broader than the code it
documents, and the other three affirmatively asserted the opposite.**

The added text opens:

> A replica that has not completed its first synchronization with its current
> master is considered to have been disconnected since forever.

Read literally, that covers every unsynchronized replica. The code resets
`repl_down_since = 0` only inside `if (shard_changed)`. For a **same-shard**
re-point, `replicationSetMaster` reaches
`replicationHandleMasterDisconnection`, which sets
`server.repl_down_since = server.unixtime` — so a replica that has not completed
its first synchronization with its current master is *not* treated as
disconnected since forever. The paragraph's second sentence ("This includes a
replica that has moved to a different shard…") signals the narrower intent, but
"includes" widens rather than restricts.

v2's finder recorded this precisely, judged it "an intentional model
simplification, not a defect," and flagged it for the orchestrator in case it
disagreed. The other three checked the same file and concluded:

- **v3** — "redis.conf text matches code exactly, including the 'automatic' qualifier"
- **v4** — "Verified — wording matches the `:4460` semantics"
- **v5** — "doc paragraph verified against actual `data_age` behavior"

All three statements are about the *second* half of the paragraph, which is
accurate. None engages the scope of the first sentence.

Two things follow, and they point in opposite directions.

**In v2's favor:** it did the more careful read, and it was the only run whose
report distinguishes "the doc is accurate about what it describes" from "the doc
describes only what the code does."

**Against all four:** none of them had anywhere to put it. v2's own skill makes an
unraised observation ineligible to become a question, so the finder had to route
it out-of-band to the orchestrator, where it became run data rather than review
content. v4 similarly parked two items under "Test-site observations (not
findings)." The shared gap is that all four architectures are binary — a candidate
either clears the rubric and gets published, or it vanishes — with no channel for
a sub-threshold observation the author might still want.

Whether this particular item should have been published is genuinely arguable:
it is a one-sentence documentation imprecision, the code is correct, and the
rubric's bar is deliberately asymmetric. But **the disagreement is invisible in
the artifacts.** Four identical `Approved (advisory)` reviews conceal that one
reviewer found a doc/code scope mismatch and three asserted there was none. For
an unattended reviewer, that is the more troubling half.

## Candidate generation versus falsification

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Candidates raised | 0 | 11 | 10 | 8 |
| Survivors | 0 | 0 | 0 | 0 |

29 candidates, 29 deaths, one shared conclusion. On this PR, candidate count
measured exploration style and internal cost, nothing else.

But v2's zero is not the same kind of zero as the others'. v2 did the work — its
report names six mechanisms it "specifically tried to convict and could not,"
with citations as good as anyone's. It simply never wrote them down as
candidates, so its falsification record is prose rather than structure. v3, v4,
and v5 each produced an auditable candidate table with a disposition and evidence
per row.

That difference does not matter when the answer is zero findings. It matters for
**re-review**: a structured disposition table lets a later run recognize that a
hypothesis was already tested and killed, and why. An unstructured narrative does
not correlate across heads. v2's architecture partitions work across finders that
each return prose; v3-v5's single reviewer with a candidate ledger is the better
substrate for state that has to survive to the next review.

v3's 11 included two the others did not reach — a claim that ROLE element 4
reflects `repl_down_since`, and an election-race scenario under validity factor
zero — and killed both with specific evidence. v4 was the only run to test the
data-age arithmetic for integer overflow. v5 was the only run to check that the
moved forward declaration left exactly one declaration behind. None of these
mattered to the outcome; all three are the kind of check you want the reviewer
running.

## The no-issue path — what test 2 actually discriminates

This PR has no originating issue. That is the one condition test 1 could not test,
and the architectures respond differently:

| | Requirements handling | Body-claim treatment |
| --- | --- | --- |
| v2 | Requirements axis **`Not applicable`**; the axis does not run | body claims checked, but recorded under "Notes", not as a ledger |
| v3 | issue alignment **"unavailable"**, stated in the summary | 7-row ledger of body claims, each "satisfied" with citations |
| v4 | issue alignment **"unavailable"**, stated in the summary | 9-row ledger including the same-shard **non-goal**, each verified |
| v5 | issue alignment **"unavailable"**, stated in the summary | 7-row ledger including the non-goal, each "met" with decisive evidence |

**v2's rule is the weak one.** Declaring the axis `Not applicable` discards half
its architecture on any PR without a linked issue, and the substitute — checking
the PR body's behavioral claims — happened because the finder chose to, not
because the skill required it. The other three convert "no issue" into "no issue
*text*, so review against the body and say so," which keeps the requirements
discipline and states the limitation in the published summary.

v4 and v5 go furthest by carrying the **non-goal** ("same-shard failovers
untouched") into the ledger as a checkable entry. That is the right instinct: on
an issueless PR the body is the only statement of intent available, and its
explicit non-goals are the only scope boundary a reviewer can test against.

This is the clearest architectural discrimination test 2 offers, and it favors
v3/v4/v5 over v2 — for a different reason than test 1 did.

## Prior third-party review state

All four read `sundb`'s `APPROVED` review and `shun-lee`'s detailed LGTM as
evidence rather than as authority. v2, v3, and v5 explicitly state that they
re-derived shun-lee's `freeClient` → `replicationCacheMaster` ordering claims
from source instead of trusting them; v4 reached the same conclusion in its C4
falsification and noted it was "consistent with shun-lee's review" — agreement
reached independently, not deference.

No run treated the existing approval as a reason to shorten its own inspection,
and no run replied to or deduplicated against threads belonging to another
identity. Correct behavior across the board, and worth recording because
deferring to an existing approval is an obvious failure mode for an automated
reviewer that reads prior review state.

## The unobserved verifier

Test 1's differences were dominated by verification: whether it ran, on what, with
what isolation, and what it changed. Here it never ran.

- **v2** skipped it by rule — its finders returned no candidates, and its verify
  step takes candidates as input.
- **v3, v4, v5** each falsified everything in their own context, leaving nothing
  to verify.

Two runs engaged the question rather than passing over it. **v3** was the only run
to notice that its rubric's "high-risk change" disjunct could have triggered a
verifier independently of the survivor list — the diff does touch failover
eligibility — and it explained that the empty list left it untriggered, while
explicitly offering the orchestrator a verifier over its *falsification log* if
it wanted assurance about the zero-finding conclusion itself. **v5** recorded that
its nearest miss (the cached-master lifecycle, "data-loss-adjacent *if broken*")
did not qualify because the trigger applies to surviving candidates only.

v3's observation identifies a real design question none of the prototypes
answers: **every architecture verifies findings, and none verifies a clean
verdict.** A reviewer that silently approves is making the highest-consequence
call it can make, with no second look by construction. On this PR that call was
almost certainly right. The prototypes provide no way to know when it is not.

## Coverage and the test-execution gap

All four statically reviewed the new 378-line Tcl test file without executing it —
builds and test runs were forbidden — and all four disclosed the gap. All four
still reported coverage `complete`.

That is defensible under every version of the rubric: coverage is defined over
changed files reviewed and risk checks with evidence-backed outcomes, not over
tests executed. All four substituted real static verification — matching each
asserted log pattern against the emitting source line, confirming helper procs
exist with the right arity, and verifying the new file is auto-discovered by
`tests/test_helper.tcl`'s glob so no manifest edit is needed.

**v5 was the only run to attach the caveat to the coverage line itself**, rather
than only to a note further down. Given that "complete coverage" is what licenses
`Approved` in every one of these skills, putting the qualifier where the licensing
claim is made is the better habit.

## Prototype verdicts

**v2 — degenerates on this target.** Three agents became one, the Requirements
axis switched itself off, the verifier never ran, and the falsification record is
prose rather than structure. It nevertheless produced the run's single most
careful observation. The `Not applicable` no-issue rule is the concrete defect:
it should become "no issue text — review against the body and say so," matching
v3-v5.

**v3 — the widest exploration.** 11 candidates, two of them unique, all killed
with specific evidence, and the only run to reason explicitly about whether a
verifier should have run at all. Its question about verifying a clean verdict is
the most useful thing any run said about architecture.

**v4 — the most complete requirement ledger.** Nine body claims plus the non-goal,
each with a citation, and the only integer-overflow check. Slowest measured span,
which given the absent token data means little.

**v5 — the most economical shape.** Second-highest candidate count in the fewest
minutes, the only run to record its fingerprint-input classification as an
explicit ambiguity, and the only one to caveat coverage at the point of claim.
Its behavior here is consistent with test 1's, on a target its design never saw.

## What test 2 changes about the test-1 recommendation

Test 1 recommended advancing v5 with one correction (scope change attribution by
candidate kind) and then running a frozen, blinded evaluation. Test 2 does not
disturb that. It adds three items:

1. **Fix v2's no-issue rule if v2 is carried forward at all** — `Not applicable`
   silently removes an axis, where "unavailable, stated in the summary" preserves
   the discipline and discloses the limit.
2. **Add a sub-threshold observation channel.** All four prototypes lose an
   accurate observation that does not clear the finding bar. A bounded
   `Observations` section — explicitly non-actionable, explicitly not a finding —
   would have surfaced the `redis.conf` scope mismatch without inflating it into a
   defect. This is a change to the output contract, not the rubric.
3. **Decide whether a clean verdict deserves verification.** v3 raised this and no
   prototype answers it. A cheap version — verify the falsification log rather
   than the (empty) candidate list — is testable and would have been the only way
   for the three runs that called `redis.conf` exact to discover that one run did
   not.

## Limits

- **n = 1 per prototype**, one target, no repeated seeds.
- **No token data**, and wall-clock spans that do not correlate with any
  architectural property. No economy conclusion is available.
- **No ground truth.** Merged-with-approval is the strongest available signal and
  is not proof.
- **Verification unobserved.** The subsystem that differentiates these skills most
  did not execute in any run.
- **Model and harness differ from test 1**, so the two evaluations may be read
  side by side but not differenced.
- **The `plausible` verdict and the published author question remain untested**
  across both experiments — eight runs, zero instances of either.
