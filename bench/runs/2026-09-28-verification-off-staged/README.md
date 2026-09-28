# Verification-off staged run

Refs [#394](https://github.com/kamui/skills/issues/394) and
[#380](https://github.com/kamui/skills/issues/380). It tests whether `review-code`'s independent
verification phase earns its cost, by comparing the current tree with a tree that has the phase
removed. The reasons for choosing this part, and the simulation behind the rules below, are in
the [analysis note](../../../docs/research/review-code-large-part-ablation-2026-09-28/README.md).

The maintainer approved the staged design and the $40 Stage 1 cap on 2026-09-28. Stage 2 has no
approved budget.

## Why the run is staged and matched

The current tree has no filed review. Every earlier attempt ran the frozen tree `c3c53da` or a
variant of it, and reviews under enforced isolation cost and behave differently from the
historical ones. So each stage buys control cells beside the variant's.

Stage 1 buys four matched pairs. It can reject the variant, clear it for Stage 2, or end
inconclusive. It cannot pass the variant.

## Frozen inputs

- Control skill tree: `5e12864b52b6c0c52b9b1b1f41d5b22fa2576676`, `skills/review-code` at
  `ca29bad`. It is the tree the #394 run named as its control and never dispatched.
- Variant skill tree: `59e7df1b15096ccb029b35df78bbc54311795650`, `skills/review-code` at
  `db731b1` on branch `bench/verification-off-variant`. The [candidate patch](candidate.patch)
  is the difference between the two, SHA-256
  `30a3cc8d26489989eb4fe484ee42b679860397669528dd69c8c06f61aec3f58e`.
- Arms: `review-code-sonnet-high-enforced-x394-control` and
  `review-code-sonnet-high-enforced-verification-off`. Primary reviewer and any fresh-context
  worker are `claude-sonnet-5`, high effort, Claude Code 2.1.282 at
  `/home/jack/.local/share/claude/versions/2.1.282`. The runner checks the pin before it claims
  a cell.
- `mode: one-shot`, `profile: publishable`, `return_format: artifacts`.
- Registers: requests v2, every other target v1. Packets, diff identities and provisioning
  hashes equal the #394 run's.
- Rubric v1 and the original method revision. The execution policy text is the #394 run's.

Reviewers receive the factual packet, source diff, execution policy and one skill tree. They
receive no issue text, threshold, register, mapping, grade or earlier output.

## What the variant changes

The variant removes the mechanism and nothing else.

| Removed | Where |
| --- | --- |
| The Verification section and step 6 | `SKILL.md` |
| The verification clauses in status, coverage, observations and the survivor record | `SKILL.md`, `references/rubric.md`, `references/output.md` |
| Carried confirmations | `references/prior-state.md` |
| The three verifier references | `references/verification.md`, `references/verifier.md`, `references/verifier-concurrency.md` |
| The brief builder, the return accounting and their test | `scripts/build_verifier_prompt.py`, `scripts/account_verifier_return.py`, `scripts/test_verifier_handoff.py` |
| The requirement that a `must-fix`, security or compatibility finding carry a confirmed task | `scripts/render_review.py` |

The finalizer's example now shows an empty verification record. The finalizer still validates a
verification record when one is written. All nine remaining test files pass on the variant.

| Loaded set | Control | Variant |
| --- | ---: | ---: |
| Always loaded | 29,684 | 26,492 |
| Review | 48,405 | 44,477 |
| Re-review | 57,598 | 53,176 |
| Runtime total | 73,188 | 46,679 |

## Cohort

Four targets, in sealed order: gRPC `m-grpc-go-7390`, requests `i-requests-6667`, Bokeh
`l-bokeh-9232` and Hono `p-hono-5067`. In filed valid reviews the control's tree family
dispatched a verifier batch on gRPC in 8 of 8, requests 7 of 7, Bokeh 6 of 6 and Hono 5 of 7.
gRPC is the clean target, and its batches hold safety premises only.

The manifest lists each excluded target with its reason. GraphQL joins in Stage 2.

Within each pair the two arms run back to back. The control runs first on gRPC and Bokeh, and the
variant first on requests and Hono.

## Isolation

Both arms use `claude-strict-v2`, as in the #394 run. Validity is that run's: missing or altered
isolation evidence, a changed clone tree, a wrong model, effort, CLI version or skill tree, a
wrong diff range, or a request the settings leave reachable invalidates an attempt.

## Stage 1 cells and caps

Eight cells: control and variant on each of the four targets, replicate 1, one at a time.

| Cap | Value |
| --- | ---: |
| Planned cells | 8 |
| Replacements for invalid attempts | 2 |
| Maximum attempts | 10 |
| Reserved per attempt | $5 |
| Closeout reserve | $5 |
| Approved Stage 1 ceiling, reviews, grading and adjudication | **$40** |

Expected spend is about $21: $11.60 for the control, about $8.70 for the variant, and about $1
for grading.

Replace an invalid cell immediately, in filing order. A valid miss, a false finding or a skill
timeout is never replaced. Do not add cells, change the variant or extend a cap after an outcome
is seen.

## Rules common to both stages

1. **Jurisdiction.** A false or non-material finding is *in jurisdiction* when the removed part
   governed it: its action is `must-fix`, or its kind is `security` or `compatibility`. The class
   is read from the finding's own fields.
2. **No single event decides.** One false finding in one variant review is recorded and compared
   with the control. It rejects nothing alone.
3. **Differences, not counts.** Every rule compares the variant with its control over the same
   cells.
4. **Blind grading.** Grade each target once both of its valid attempts are filed, with the
   existing grader template and Opus 5.5 high. The grader sees no arm, tree, cost, native action
   or verdict. An `unresolved` new candidate goes to an independent adjudicator before the
   decision. Grading and adjudication count against the cap.
5. **No extension.** Cells, caps and margins do not change after an outcome.

## Stage 1 decision rule

| Outcome | Rule |
| --- | --- |
| Reject | On two or more of the four targets, the variant carries an in-jurisdiction false or non-material finding and its control does not |
| Reject | On two or more of requests, Bokeh and Hono, the variant recovers no registered defect and its control recovers one |
| Reject | The variant's total review cost over the four targets is not below the control's |
| Stop, inconclusive | The control dispatches a verifier batch on fewer than three of the four targets, so the stage cannot observe the part |
| Stop, inconclusive | The caps run out before a decision |
| Clear | None of the above. This opens Stage 2. It is not a pass |

Stage 1 records recall, action, remedy sufficiency, non-material blockers, cost, elapsed time,
finalizer refusals and reads of the finalizer's source for every valid review.

Simulated from the filed recovery rates, Stage 1 rejects a variant that changes nothing 8% of the
time, or 16% if recall under isolation is 0.7 of the filed rate. It rejects a variant that loses
40% of recoveries 33% of the time. It is a futility gate. Stage 2 decides.

## Stage 2, fixed before any Stage 1 outcome

Stage 2 runs only after a clear and a separately approved cap of $70. It has 22 cells:
replicates 2 and 3 of both arms on the four Stage 1 targets, and three replicates of both arms on
GraphQL `k-graphql-js-1582`. With Stage 1 this gives 15 matched pairs. Within each replicate the
targets keep the sealed order and the arms alternate.

The variant passes only when every row holds:

| Measure over the 15 pairs | The variant passes when |
| --- | --- |
| Reviews carrying an in-jurisdiction false or non-material finding | Variant minus control is at most 1 |
| Reviews carrying any false finding | Variant minus control is at most 2 |
| Registered defects recovered | Variant total is at least control total minus 3, and no defect the control recovers 3 of 3 is recovered 0 of 3 |
| `must-fix` on recovered defects | Variant total is at least control total minus 3 |
| Sufficient remedies on recovered defects | Variant total is at least control total minus 3 |
| Invalid attempts | Variant is at most control plus 1 |
| Cost | Median over targets of the variant-to-control ratio of per-target median cost is at most 0.90 |
| Elapsed to payload | The same ratio is at most 0.90 |

Simulated, these rules reject a variant that changes nothing 25% of the time and a variant that
loses 40% of recoveries 83% of the time. A pass still leaves #380's unseen-target comparison
before adoption.

## Launch checklist

1. Commit the arm file, the manifest and this protocol. Record that commit as the manifest's
   freeze and metric revision.
2. Repeat the free native isolation checks and the target smokes on the launch host with the
   pinned CLI and a local fake API.
3. Set `frozen_at`. Confirm zero claims and zero charges for this run.
4. Unset every `CLAUDE*`, `ANTHROPIC*` and `AI_AGENT` variable of the orchestrating session. Set
   `BENCH_CLAUDE` to the pinned executable and put the sandbox tools on `PATH`. Dispatch with
   `run_cell.py --next` and `--replace`.
5. File and audit each attempt before the next dispatch. Grade a target once both of its valid
   attempts are filed. Act on a stopping condition at once.

## Preparation results

The [preflight summary](preflight/summary.json) records zero paid calls. All 24 native isolation
checks passed with the real CLI and a local fake API, including a smoke on each of the four
targets and GraphQL. The 149 benchmark tests passed, 16 of them native checks skipped in that
suite and passed in the native one. Runner, filing, provisioning and scoring self-tests passed.

To repeat the free native checks on this host:

```sh
BENCH_ISOLATION_CLI=/home/jack/.local/share/claude/versions/2.1.282 \
BENCH_ISOLATION_TARGETS=m-grpc-go-7390,i-requests-6667,l-bokeh-9232,p-hono-5067,k-graphql-js-1582 \
PATH=/tmp/x384-sandbox-tools/usr/bin:$PATH \
LD_LIBRARY_PATH=/tmp/x384-sandbox-tools/usr/lib/x86_64-linux-gnu \
PYTHONDONTWRITEBYTECODE=1 \
python3 -B bench/tools/test_review_isolation.py
```
