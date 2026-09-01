# Comparison data — v2, v3, v4, v5 on `redis/redis#15680`

> **Promotion status:** “v5” is the historical prototype name used by this record. PR #17 promoted that workflow to `skills/code-review-publish` on `main`; new experiments should invoke `/code-review-publish` without the `-5` suffix.

**2026-09-01. Data only.** Every number here is measured or directly observed; the analysis is in
[`evaluation.md`](evaluation.md).
All runs (orchestrator and sub-agents) used the GLM-5.3-Flash model at the High reasoning setting
under the opencode CLI harness with context-mode MCP. Token totals are unavailable from this
harness (see test-2 README); wall clock is the orchestrator's measurement of each sub-agent's span;
tool counts are sub-agent self-reports.

## Cost and shape

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Agents spawned | 1 (Requirements axis N/A by rule) | 1 | 1 | 1 |
| Sub-agent tokens | unavailable | unavailable | unavailable | unavailable |
| Tool uses (self-reported) | ~46 | 35 | 30 | 37 |
| Wall clock (orchestrator-measured) | ~9 min | ~19 min | ~22 min | ~6 min |
| Verifier used? | no — skipped (no candidates) | no — zero survivors | no — zero survivors | no — zero survivors |

## Output

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Candidates raised | 0 | 11 | 10 | 8 |
| Dropped before publication | — | 7 refuted, 4 dropped | 10 dropped (0 by verifier) | 8 dropped (0 by verifier) |
| **Findings** | **0** | **0** | **0** | **0** |
| Blocking findings | 0 | 0 | 0 | 0 |
| Priority spread | — | — | — | — |
| Questions | 0 | 0 | 0 | 0 |
| Coverage reported | complete (5/5) | complete (5/5) | complete (5/5) | complete (5/5) |
| **Derived status** | **Approved (advisory)** | **Approved (advisory)** | **Approved (advisory)** | **Approved (advisory)** |

## Requirement-ledger comparison

No originating issue exists on this PR. All four runs applied their own no-issue rule:

| | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Requirements axis | `Not applicable` (Code axis runs alone) | issue alignment "unavailable", stated in summary | issue alignment "unavailable", stated in summary | issue alignment "unavailable", stated in summary |
| PR-body behavioral claims | used as claims to check (not from an issue); all checked out | ledger of body claims, all "satisfied" | ledger of body claims + non-goal, all verified | ledger of body claims + non-goal, all "met" with decisive evidence |

## Candidate-theme agreement

Eight distinct themes were considered by at least one run (v2 raised none). "Checked" means the
theme was examined even if not raised as a formal candidate.

| Theme | v2 | v3 | v4 | v5 |
| --- | --- | --- | --- | --- |
| Ordering of discard after `replicationSetMaster` / re-cache risk | checked, acquitted | C4 refuted | C1, C2 falsified (call-site bypass variants) | C1 dropped |
| `repl_down_since = 0` misread by downstream consumers (INFO, ROLE, data-age) | checked, acquitted (INFO, data-age) | C3 refuted, C10/C11 (ROLE semantics, race) refuted | C1 falsified, C6 falsified (pre-existing) | C2 dropped |
| Same-shard re-point handling / partial-resync preservation | checked (flagged as intent) | C5 refuted | non-goal verified | C3 dropped; non-goal "met" |
| Manual `CLUSTER FAILOVER` bypass of data-age check | checked, acquitted (pre-existing) | C7 refuted | C9 falsified (pre-existing) | C5 dropped (pre-existing) |
| `memcmp` on unknown/zero `shard_id` | checked (adoption race) | C6 dropped | C3 falsified (fixed array) | C6 dropped |
| Commit 2 "remove unnecessary check" weakening the test | checked, acquitted (flaky assertion) | (second commit inspected; justified) | C8 falsified (timing-sensitive) | C4 dropped (race-dependent) |
| Test weight / CI cost | noted, not a candidate | C9 dropped | C10 dropped (rubric condition) | (not raised) |
| Log-pattern / helper existence in new Tcl test | cross-checked, acquitted | C2 refuted | (helpers verified) | C7 dropped |

**All four runs examined the same three decisive mechanisms** — discard-after-cache ordering,
`repl_down_since = 0` consumers, and same-shard/cross-shard gate semantics — and all four reached
clean dispositions. The candidate *generation* differed (v3 raised the most, v2 none), but the
falsification endpoints converged.

**Pre-existing-behavior refutations appear in three runs** (v3 C7, v4 C9, v5 C5 — manual failover
bypass; v4 C6, v5 C2 — INFO semantics of `repl_down_since == 0`), each reaching the same
"pre-existing/intended" disposition through its own rubric's vocabulary.

**Prior third-party state:** all four runs read the sundb approval and shun-lee LGTM as evidence;
v2, v3, and v5 explicitly note they re-derived shun-lee's ordering claims from source rather than
trusting them.

## Distinguishing behaviors observed

- **v2** was the only run to return zero candidates outright, ending as 1 agent with no verifier —
  and the only run whose skill makes the Requirements axis `Not applicable` (rather than
  "unavailable") in the no-issue case.
- **v3** raised the most candidates (11) and was the only run to explicitly surface the rubric's
  "high-risk change" verifier disjunct and explain why an empty survivor list kept it untriggered.
- **v4** was the only run to trace an integer-overflow candidate on the data-age arithmetic, and it
  computed the `context` fingerprint with the skill's script.
- **v5** was the fastest run (~6 min) despite raising 8 candidates, and the only run to record its
  fingerprint-input classification (specs/guidance/evidence) as an explicit ambiguity decision.
- **No verifier ran in any run** — on this PR every architecture collapsed to its primary/frequent
  path, so the fresh-context verification machinery that dominated test-1's differences is
  unobserved here.
- All four runs statically reviewed the new Tcl tests without executing them (forbidden by run
  conditions) and disclosed that gap; all four verified CI wiring from workflow files instead.
