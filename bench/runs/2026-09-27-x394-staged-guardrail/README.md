# #394 staged guardrail run

Part of [#394](https://github.com/kamui/skills/issues/394). It tests the seven
paragraph removals in [#407](https://github.com/kamui/skills/pull/407) against the
tree they trim. #394 preregistered A only, Sonnet 5 high, 3 replicates on all 10
pinned targets. This run keeps that comparison and stages it.

The maintainer approved the staged design and the $40 Stage 1 cap in the #407
delivery thread on 2026-09-27. Stage 2 has no approved budget. Before any dispatch,
the maintainer also chose to exclude Astro (see [Cohort](#cohort)).

The manifest was frozen at `2026-09-28T02:11:35Z` on freeze commit
`f3c7d9ca7a563a3eb41fc25a6b7e23caf81d1b93`, after the [launch checks](launch-preflight/summary.json)
passed and before any paid dispatch.

## Why the run is staged

#394 estimated $23 for 30 A reviews. That figure is the historical A arm at about
$0.76 a review, with no control. Reviews under enforced isolation have cost $2.10 to
$4.98, and no review of the control tree exists, so the full comparison is about 54
cells at roughly $130 to $190.

One #394 guardrail needs no control: false findings stay 0 overall. Stage 1 buys one
candidate review per target, which is enough to reject on that guardrail. Recall,
action, remedy, validity, cost and latency compare the candidate with a matched
control, so they wait for Stage 2.

Stage 1 cannot pass the candidate. It can reject it, clear it for Stage 2, or end
inconclusive.

## Frozen inputs

- Control skill tree: `5e12864b52b6c0c52b9b1b1f41d5b22fa2576676`, `skills/review-code`
  at `05e336791ffd7f42abb74421df47032405fe0b52`.
- Candidate skill tree: `6e6c654707781c03719c5cfe6d0381e2e4046522`, `skills/review-code`
  at #407's head `ca4ed67a77c56377c9c2fc1b1bbd1a4db111b1dd`. The
  [candidate patch](candidate.patch) is the difference between the two, SHA-256
  `2c96ea244a7e50361a2a95d9d2ebd79fe94b20fc35c2fba1c6fa5cc6ee4b5270`. It removes the
  seven paragraphs from four reference files. It also changes `DESIGN.md` and
  `scripts/test_instruction_budget.py`, which no review loads.
- Arms: `review-code-sonnet-high-enforced-x394-trimmed` for Stage 1, and
  `review-code-sonnet-high-enforced-x394-control` fixed for Stage 2. Primary reviewer
  and fresh-context workers are `claude-sonnet-5`, high effort, Claude Code 2.1.282 at
  `/home/jack/.local/share/claude/versions/2.1.282`. The runner checks the pin before
  it claims a cell.
- `mode: one-shot`, `profile: publishable`, `return_format: artifacts`.
- Registers: requests v2, tRPC v3, ripgrep v2, every other target v1. Packets, diff
  identities and provisioning hashes equal the baseline run's.
- Rubric v1 and the original method revision. The execution policy text is the #384
  staged gate's.

Reviewers receive the factual packet, source diff, execution policy and one skill
tree. They receive no issue text, threshold, register, mapping, grade or earlier
output.

## Cohort

Nine targets, in sealed order: gRPC `m-grpc-go-7390`, soba `q-soba-195`, requests
`i-requests-6667`, tRPC `j-trpc-5017`, graphql-js `k-graphql-js-1582`, Bokeh
`l-bokeh-9232`, ripgrep `n-ripgrep-2957`, Hono `p-hono-5067` and Base UI
`r-base-ui-5460`. gRPC and soba go first because #394 names them for the
zero-false-finding guardrail.

Astro `o-astro-16079` is excluded. Its focused tests build each fixture into the
clone (`.astro`, `dist`, `.vercel`), and `claude-strict-v2` mounts the clone
read-only. The sandbox's write deny on the clone overrides any nested allow.
Relocating those directories through links breaks the Vercel adapter's module paths,
and git reports the links as untracked, which would invalidate every attempt.

## Isolation

Both arms use `claude-strict-v2`, as in the #384 staged gate. Enforced isolation had
run on Base UI, gRPC and soba only. The free native checks on the other targets found
three adapter gaps, fixed before the freeze. None changes a reviewer prompt, tool,
skill text or allowance.

- **requests.** The target's relocatable virtualenv runs a uv interpreter outside
  the dependency cache, through a symlinked home. The sandbox now exposes the
  directory holding that home and the install it resolves to, read-only.
- **graphql-js.** `@babel/register` creates `node_modules/.cache` on first use. It
  is now relocated to the attempt's work directory, as `.vite` already was. A
  provisioned `.cache`, as in tRPC, stays in place.
- **Smoke checks.** The native smoke check now substitutes `{clone}` and `{cache}`
  in a target's smoke command, and expects the exit code the target's `smoke.json`
  records. requests' selection records exit 1, from two failures that also occur at
  the merge-base.

Validity is the staged gate's: missing or altered isolation evidence, a changed clone
tree, a wrong model, effort, CLI version or skill tree, a wrong diff range, or a
request the settings leave reachable invalidates an attempt.

## Stage 1 cells and caps

Nine cells: one candidate review per target, replicate 1, one at a time.

| Cap | Value |
| --- | ---: |
| Planned cells | 9 |
| Replacements for invalid attempts | 3 |
| Maximum attempts | 12 |
| Reserved per attempt | $5 |
| Closeout reserve | $5 |
| Approved Stage 1 ceiling, reviews, grading and adjudication | **$40** |

The CLI receives `--max-budget-usd 5` for each review. That limit is checked between
requests, so one request can overshoot it. Record actual charges.

Replace an invalid cell immediately, in filing order. A valid miss, a false finding
or a skill timeout is never replaced. Do not add cells, change the candidate or
extend a cap after an outcome is seen.

## Stage 1 decision rule

Blind-grade each target once its valid attempt is filed, with the existing grader
template and Opus 5.5 high. The grading holds every filed attempt on that target. The
grader sees no arm, tree, cost, native action or verdict. An `unresolved` new
candidate goes to an independent adjudicator, from the existing adjudication
template, before the decision. An adjudicated `false` classification is a false
finding. Grading and adjudication count against the cap.

- **Reject.** A valid candidate review carries a false finding. Stop and leave the
  remaining cells unrun. The removals are not adopted: under #394, restore the
  paragraph that caused the failure when the failure isolates one, otherwise revert
  the change. #407 stays unmerged until that is done.
- **Clear.** Nine valid reviews carry no false finding. This opens Stage 2. It is
  not a pass.
- **Inconclusive.** The caps run out before either outcome. Stop and diagnose.

Stage 1 records recall, action, remedy sufficiency, non-material blockers, cost and
elapsed-to-payload for every valid review. None of them decides Stage 1. Historical A
is context only, because its reviews ran without enforced isolation.

## Stage 2, fixed before any Stage 1 outcome

Stage 2 runs only after a clear and a separately approved cap. It has 45 cells:
three control reviews per target and candidate replicates 2 and 3 per target. The
nine Stage 1 reviews are the candidate's replicate 1. Within each replicate, targets
keep the sealed order, and control and candidate alternate, the control first on
odd-positioned targets.

The candidate passes only when all of #394's conditions hold against the matched
control:

- per-target recall, from three valid reviews per arm, no lower than the control's;
- for recovered defects, must-fix action and sufficient-remedy rates no lower than the
  control's on each target;
- an invalid-attempt rate no higher than the control's;
- zero false findings across every candidate review, gRPC and soba included;
- the median, over targets, of the candidate's per-target median cost divided by the
  control's is at most 1.00, and the same for elapsed-to-payload.

Replicate 1 candidate timings come from Stage 1 and are not interleaved with the
control. Report that limit with the result. A pass still leaves #380's unseen-target
comparison before adoption.

## Launch checklist

1. Commit the runner, the arm files and this protocol. Record that commit as the
   manifest's freeze and metric revision.
2. Repeat the free native isolation checks and the nine target smokes on the launch
   host with the pinned CLI and a local fake API.
3. Set `frozen_at`. Confirm zero claims and zero charges for this run.
4. Unset every `CLAUDE*`, `ANTHROPIC*` and `AI_AGENT` variable of the orchestrating
   session. Set `BENCH_CLAUDE` to the pinned executable and put the sandbox tools on
   `PATH`. Dispatch with `run_cell.py --next` and `--replace`.
5. File and audit each attempt, and grade its target, before the next dispatch. Act on
   a stopping condition at once.

## Preparation results

The [preflight summary](preflight/summary.json) records zero paid calls. All 24 native
isolation checks passed with the real CLI and a local fake API, including a smoke on
each of the nine targets with and without the environment prefix. The 149 benchmark
tests passed, 16 of them native checks skipped in that suite and passed in the native
one. Runner, filing, provisioning and scoring self-tests passed.

To repeat the free native checks on this host:

```sh
BENCH_ISOLATION_CLI=/home/jack/.local/share/claude/versions/2.1.282 \
BENCH_ISOLATION_TARGETS=m-grpc-go-7390,q-soba-195,i-requests-6667,j-trpc-5017,k-graphql-js-1582,l-bokeh-9232,n-ripgrep-2957,p-hono-5067,r-base-ui-5460 \
PATH=/tmp/x384-sandbox-tools/usr/bin:$PATH \
LD_LIBRARY_PATH=/tmp/x384-sandbox-tools/usr/lib/x86_64-linux-gnu \
PYTHONDONTWRITEBYTECODE=1 \
python3 -B bench/tools/test_review_isolation.py
```
