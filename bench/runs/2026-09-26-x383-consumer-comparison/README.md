# Run 2026-09-26-x383-consumer-comparison: #383 alone on frozen A

The [#389 preregistration](../../../docs/research/builtin-review-benchmark-2026-09-24/README.md#13-preregistered-follow-up-isolated-a-changes-2026-09-25)
row for [#383](https://github.com/kamui/skills/issues/383): arm A (`review-code` on Sonnet 5 at
`high`) with the shared-helper consumer-comparison paragraph added to the frozen A tree and nothing
else, on j, i, p, m and q, three replicates each, 15 planned cells. The maintainer approved the
billed run on 2026-09-26, against the issue's $12.66 review-only estimate.

**Frozen 2026-09-26.** `manifest.json` carries `frozen_at`; `freeze_commit` names the commit that
introduced it. After the first dispatch, the manifest changes only by an appended deviation.

## Pins

| What | Pinned as |
| --- | --- |
| Control | arm A's original two valid replicates per target in [`2026-09-24-builtin-baseline`](../2026-09-24-builtin-baseline/README.md), scored by `results.v3.json`; tree `c3c53da5381dace16876b0f5b7abe4bccc6bc58b`. No baseline rerun. |
| Candidate tree | `207b72c5bc1e7ec5c85ebfe43bfc6c3354df9805` = the control tree with `candidate.patch` applied (local ref `refs/bench/x383-candidate-tree`) |
| Patch | `candidate.patch`, SHA-256 `e982088f4efdd0defe5e597f5937708bb6b09ef22ca9fa290165f94e9576b953`: #383's paragraph verbatim after the ledger-gated trigger paragraph in `references/rubric.md`'s Released compatibility, 256 bytes and 38 words, byte-identical to the paragraph in main's `skills/review-code/references/rubric.md` |
| Arm | `bench/arms/review-code-sonnet-high.json`, SHA-256 `b1e566c1…` (unchanged); `mode: one-shot`, `profile: publishable`, `return_format: artifacts`; Sonnet 5 at `high` for the primary and every worker |
| Claude Code | `2.1.282`, the control's version, through `~/.t3/bench-runs/2026-09-26-x383-consumer-comparison/bin/claude` |
| Cohort | the control manifest's packet, diff and provisioning hashes; registers v2 for (j) and (i), v1 elsewhere, as `results.v3.json` uses |
| Order | replicate 1 across j, i, p, m, q, then replicate 2, then 3 |
| Caps | 17 attempts, 2 replacements, $45 including grading and adjudication, $5 per attempt, $5 grading reserve |
| Rates, method, rubric, metric code | Sonnet 5 and Opus 5.5 `as_of 2026-09-24`; `bf3c25f5…`, scoring v1, `8073b48c…` |

## Decision rule

**Pass** only if all of these hold at the fixed stopping point:

- GT-j1 and GT-j2 are each recovered in at least 2/3.
- Requests recall is at least 2/3, with GT-i1 recovered in 3/3.
- Hono GT-p1 is recovered in 3/3.
- (m) and (q) have zero false findings, and no target gains a false finding or non-material blocker.
- Correct action, sufficient remedy and validity do not get worse on comparable recoveries.
- Historical per-target recall holds: (i) at least 2/3, (p) 3/3.

Hypothetical type differences and pre-existing array behavior on Hono are not defects; the register
rules on them. Input-matrix coverage is diagnostic, not recovery.

**Reject** on a measured failure. **Inconclusive** if the cap or missing valid cells prevents a verdict.
A miss is never replaced, and no threshold changes after results.

Whether each (j) review compared helper inputs inside actual consumer compositions (middleware
pipelines, procedure builders) or only probed isolated helper outputs is recorded as a diagnostic
for #383's acceptance item, outside this decision.

## Results (2026-09-26)

**Disposition: reject.** GT-j1 was recovered in 0 of 3 valid (j) reviews and GT-j2 in 1 of 3. Each
needed at least 2/3. All three planned (j) cells ended with a valid, completed review, so the cap
and the missing (m) cell do not affect this outcome. Every other threshold holds, and so does every
guardrail over valid reviews. More attempts were invalid than in frozen A, but the outcome does not
depend on how that is counted.

(m) ended with 2 of its 3 planned valid reviews. Three attempts were harness-invalid, each because
the reviewer wrote its private directory under `/tmp`, outside the attempt's roots: att-001 on (j)
replicate 1, and att-009 and att-014 on (m) replicates 2 and 3. Replacements went in filing order.
att-016 replaced att-001 and att-017 replaced att-009, and both were valid. That used both
replacements and all 17 attempts, so att-014's cell has no valid review. The candidate tree does not
touch private-directory handling. x382 lost 3 of 17 attempts the same way.

`results.v1.json` comes from `score.py`. It uses mapping v1 on every target except (j), which uses
mapping v2 at register v3. Each target was graded once, blind, by `grade.py`: Opus 5.5 at `high`,
`--safe-mode`, with a clean read audit. The (j) grader left one new candidate unresolved: NC-1, on
att-006, where a `next({ ctx: X | undefined })` override replaces an object context. An
independent adjudicator (A1) reproduced it at the merge-base, the head and the #5039 fix, and
ruled it a new material defect, GT-j3. Its rulings are in [`adjudication/`](adjudication/). A blind
re-grade for GT-j3 alone (R1) found that one recovery, and `grade.py revise` wrote mapping v2.
The manifest records the register change as a deviation. The #383 thresholds name only GT-j1 and
GT-j2, whose mappings are the same in v1 and v2. "Frozen A" means the control's two valid reviews
per target, from `results.v3.json`, with (j) scored at register v2.

| Target | Candidate valid reviews | Recovery (valid reviews) | Native action on the recovery | Fix | Approved on buggy | False findings | Frozen A |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (j) tRPC | 3 (plus the invalid att-001) | GT-j1 0/3, GT-j2 1/3, new GT-j3 1/3 | GT-j2 `must-fix` P2; GT-j3 an observation | GT-j2 partial; GT-j3 absent | 2/3 | 0 | GT-j1 0/2, GT-j2 0/2, approved 2/2 |
| (i) Requests | 3 | GT-i1 3/3, GT-i2 3/3, GT-i3 0/3; recall 0.667 | GT-i1 `must-fix` P1 3/3; GT-i2 `must-fix` P2 2/3, observation 1/3 | GT-i1 partial 3/3; GT-i2 sufficient 2/3, absent 1/3 | 0/3 | 0 | GT-i1 2/2 `must-fix` P1 partial; GT-i2 1/2 as an observation, absent; GT-i3 1/2 `consider` P3 (a priority error), partial; recall 0.667; approved 0/2 |
| (p) Hono | 3 | GT-p1 3/3 | `must-fix` P2 3/3 | sufficient 2/3, partial 1/3 | 0/3 | 0 | GT-p1 2/2 `must-fix` P2, sufficient 1/2; approved 0/2 |
| (m) gRPC, clean | 2 of 3 | — | — | — | — | 0 (also 0 on both invalid attempts) | 0 |
| (q) Soba, clean | 3 | — | — | — | — | 0 | 0 |

- **Thresholds:** GT-j1 0/3 against the required 2/3, a fail. GT-j2 1/3 against the required 2/3, a fail. Requests recall is 0.667, meeting 2/3, and GT-i1 is 3/3. Hono GT-p1 is 3/3.
- **Guardrails:** (m) and (q) have 0 false findings. No target has a false finding, an unresolved item or a non-material blocker. The only `must-fix` items are recoveries of GT-j2, GT-i1, GT-i2 and GT-p1. Historical recall holds: (i) 0.667 against 0.667, and (p) 1.0 against 1.0. All three GT-p1 recoveries are the real `formData()`-then-`parseBody()` cache interaction. No hypothetical type difference or pre-existing array behavior is counted.
- **Per-defect change outside the thresholds:** GT-i3 falls from 1/2 to 0/3. (i)'s recall still holds, because GT-i2 rises from 1/2 to 3/3.
- **Action, fixes and validity on comparable recoveries:** none is worse. GT-i1 is `must-fix` with a partial fix in every recovery, in both runs. GT-i2 moves from 0/1 `must-fix` to 2/3 `must-fix`, and from 0/1 sufficient to 2/3 sufficient. GT-p1 stays `must-fix` in every recovery and goes from 1/2 to 2/3 sufficient. Priority errors on these targets fall from 1 to 0. Every recovery is on a valid attempt, in both runs. Invalid attempts rose to 3 of 17, from frozen A's 0 of 10 on these targets and 1 of 21 overall. None of the invalid attempts recovered a defect.
- **Dollars:** $17.49 for 17 reviewer attempts. That is $1.09 mean per valid review ($1.03 per attempt), against frozen A's $0.84 on these targets. The three invalid attempts cost $2.26. Grading was $1.89, the adjudication $0.82 and the re-grade $0.26, so the run total is $20.45 against the $45 cap. The valid reviews alone cost $15.23, above the issue's $12.66 review-only estimate.
- **Latency:** median elapsed-to-payload over valid reviews is 213 s (14 reviews), against frozen A's 142.5 s on the same targets (10 reviews). Per target: (j) 99 → 325 s (2 → 3 reviews), (i) 260.5 → 291 s, (p) 142.5 → 172 s, (m) 179 → 215 s (2 → 2), (q) 99.5 → 116 s. `results.v1.json`'s per-target medians include the invalid attempts, so they differ on (j) and (m).

## Consumer-composition diagnostic

This diagnostic addresses #383's acceptance item, "Consumer compositions, not isolated helper outputs
alone, support the investigated cases". For each (j) review, it records from the normalized items
and the report whether the review compared `Overwrite` inputs inside a real procedure-builder and
middleware pipeline (`initTRPC…procedure.use(…next({ ctx })…).query(…)`) or only through isolated
`Overwrite<A, B>` outputs. The scratch probes left in each attempt's work directory confirm each
reading. Nothing here counts as recovery.

| Attempt | Valid | Verdict | Isolated `Overwrite` probes | Consumer composition | Result |
| --- | --- | --- | --- | --- | --- |
| att-016 (r1) | yes | Approved | base against head: `unique symbol`, `any`, `unknown`, `never`, union and `X \| undefined` inputs | none. The report says every `Overwrite` consumer was inspected by reading, and it holds a safety premise that non-object operands reach no in-repo consumer in a breaking way | only the unreachable-branch observation |
| att-006 (r2) | yes | Approved | base against head: `unknown`, `any`, `never`, `undefined`, union, `any` and `unknown` as `TType`, function and array inputs | yes, with an object context only: `procedure.use(opts => opts.next({ ctx }))`, with `ctx` set to `undefined`, `{ a } \| undefined` and `{ a }` | GT-j3 (an observation). Its compatibility candidate was refuted as intended behavior |
| att-011 (r3) | yes | Changes Requested | base against head: `unknown`, `any`, `never`, `undefined`, union and optional inputs, on either side | yes: `initTRPC.context<any>()` and an object context, each through `procedure.use(next({ ctx: { foo } })).query(…)` | GT-j2, `must-fix` P2, found in that composition |
| att-001 (r1, invalid) | no | Approved | base against head: `any`, `unknown`, `never`, `undefined`, `null`, union and array inputs | none | observations only |

Two of the three valid reviews tested inputs inside real middleware pipelines, and both composed
reviews found a defect that neither frozen A review reported: GT-j2 in att-011 and GT-j3 in att-006. The third
valid review and the invalid attempt probed isolated helper outputs only. No review built a
middleware or procedure from an unconstrained generic type parameter. That is GT-j1's trigger, and
all three reviews missed GT-j1. No review composed an `any` context and a nullable override in the
same review. So consumer compositions supported the investigated cases in 2 of 3 reviews, and they
never reached GT-j1's generic role.
