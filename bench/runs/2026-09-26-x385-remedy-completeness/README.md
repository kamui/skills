# Run 2026-09-26-x385-remedy-completeness: #385 alone on frozen A

This run implements [#385](https://github.com/kamui/skills/issues/385) under the
[#389 protocol](../../../docs/research/builtin-review-benchmark-2026-09-24/README.md#13-preregistered-follow-up-isolated-a-changes-2026-09-25).
The maintainer authorized the three separate experiments on 2026-09-26, including the
existing $35, $30 and $45 caps. This run's total cap is $45, including replacements,
grading and adjudication. No fresh baseline run is authorized or planned.

## Frozen inputs

- Control: original A outputs in `2026-09-24-builtin-baseline`, corrected `results.v3.json`,
  skill tree `c3c53da5381dace16876b0f5b7abe4bccc6bc58b`.
- Candidate: `8c5b592421d2e9ff528a370c6e95725437425c4b`, the control tree plus `candidate.patch` alone.
- Patch SHA-256: `5c838d3eb07728aa660c53a0e5af60f30f7086dc7eea78e3c16cc0745a31a967`. It adds 131 UTF-8 bytes to `references/output.md`.
- Model: `claude-sonnet-5`, high effort, for primary and verifier workers, through Claude Code
  2.1.282. The original arm file and original factual packets and allowances are unchanged.
- Runtime workflow identity remains frozen A's identity; the candidate tree and patch identify
  this experiment. Release identities, budget-test limits and DESIGN history are not additional
  changes to the experimental tree.
- Cohort and register versions: i-requests-6667 v2, p-hono-5067 v1, l-bokeh-9232 v1, m-grpc-go-7390 v1, q-soba-195 v1.
- Order: replicate 1 across the cohort above, then replicate 2, then replicate 3.
- Caps: 15 planned cells, 17 maximum attempts, two invalid replacements,
  $5 reserved per attempt, $5 closeout reserve, one review in flight per experiment.
- Independent experiments may run concurrently in separate work directories. Do not compare
  pooled elapsed times across their different cohorts.

The runner now forwards its reserved attempt amount to Claude's `--max-budget-usd`.
Earlier dispatches had a hard-coded $15 CLI limit despite a $5 reservation. The correction
changes no reviewer prompt, tools, skill text or execution allowance. Claude's limit is checked
between requests; retain the actual metered cost and stop if it exhausts the run cap.
Raw transcripts and temporary clones remain outside the repository. File every attempt and charge.

## Decision rule

GT-i1 must have sufficient remedies in 3/3 Requests reviews. GT-i3 must be recovered in at least 2/3, with a sufficient remedy on every recovery. Requests recall must remain at least 2/3. Hono and Bokeh must remain recovered in 3/3, with sufficient remedies in at least 2/3 and 3/3 respectively. Judge Requests remedies against adapter identity and mutation, proxy TLS and stale CA reset. Preserve Hono's conditional cache repair rather than an overbroad remedy.

Require zero false findings on gRPC and soba and no new false findings or non-material blockers
elsewhere. Preserve historical A recall on every exercised target, correct action, sufficient
remedies and validity under the common protocol. Count recovered observations separately from
actionable findings. Render and grade items blind with the existing grader template and Opus 5.5
high, as in the prior experiments. An independent adjudicator resolves plausible new defects.

Pass only when every threshold and guardrail holds. Reject a measured failure and revert the
failed change on main, including its associated metadata where applicable. Missing valid or
gradable cells that prevent a decision make the result inconclusive; they cannot be declared a
pass. A valid miss is never replaced. Stop on a measured guardrail failure, insufficient room
for the next $5 attempt plus the reserve, or exhaustion of fixed cells and two replacements.
Do not add opportunistic replicates or change thresholds after results.

Report recovery, action, remedy sufficiency, validity, billed dollars and elapsed-to-payload
separately. A focused pass does not complete #380's combined and unseen-target adoption gate.

## Closeout steps

1. Validate the candidate patch/tree, manifest, pins and dispatch accounting before paid calls.
2. Dispatch and file the fixed cells using `bench/tools/run_cell.py`; replace eligible invalid
   attempts in filing order within the fixed caps.
3. Blind-grade, adjudicate unresolved candidates, validate mappings and reproduce the scores.
4. Record pass/reject/inconclusive with the paid-run ledger. Apply and verify any required revert.
5. Publish the evidence and closure work for review. Close #385 only when its acceptance
   conditions or documented rejection and revert are complete; report an inconclusive blocker.

## Results, 2026-09-27

**Disposition: reject.** The valid Hono review recovered no registered defect and approved. Frozen A recovered GT-p1 in both historical reviews. This loses per-target recall and trips the common stop guardrail. Even perfect remaining replicates could produce only 2/3 recovery, below the required 3/3. This is an early guardrail stop, not completion of the 15-cell screen. The valid Requests review also supplies only partial remedies for GT-i1 and GT-i2; GT-i3 is absent. Revert the completeness sentence. The sufficient Bokeh remedy came from an invalid attempt and does not satisfy its retention threshold.

All existing outputs were blind-graded under the original template by Opus 5.5 high through Claude Code 2.1.282. No grader returned an unresolved new candidate. No additional review was purchased during recovery. Unattempted cells remain visible in `results.v1.json`; no missing cell is an approval or a recovered defect.

| Target | Valid / all attempts | Valid-review recall | Valid false findings | Median elapsed-to-payload (valid) |
| --- | ---: | ---: | ---: | --- |
| i-requests-6667 | 1/1 | 0.667 | 0 | 1169 s; n=1 |
| l-bokeh-9232 | 0/1 | n/a | 0 | unavailable; n=0 |
| m-grpc-go-7390 | 0/1 | n/a | 0 | unavailable; n=0 |
| p-hono-5067 | 1/1 | 0.000 | 0 | 474 s; n=1 |
| q-soba-195 | 1/1 | n/a | 0 | unavailable; n=0 |

- Validity: 3/5 attempts are valid. No replacements were dispatched.
- Costs: reviews $13.455287; blind grading $1.146891; total **$14.602178**, including invalid attempts. No adjudication was required.
- Action and remedies: the [scorecards](scoring/) grade each recovered defect and its remedy; each attempt's `normalized.json` retains native action and observations. All-attempt score fields can include invalid reviews; use the table's valid-review counts for guardrails.
- Timing: interrupted wrapper finalization leaves a missing elapsed-to-payload event on recovered outputs. `recovery.json` retains CLI durations separately; they are not substituted into the frozen metric. Medians show their actual valid, timed sample count.
- Audit correction: [the recovery report](../2026-09-27-audit-recovery.json) records every original and revised disposition. The local-clone correction changes no historical baseline classification across 83 audits. Historical baseline files remain unchanged; prior experiment records are in `audit-revisions/before-local-clone-fix/`. Existing filesystem violations are preserved.
- Run supervision: the original terminal jobs did not finish wrapper finalization for three completed CLI sessions. Recovery grading ran to completion in detached tmux sessions with logs under `~/.t3/bench-runs/2026-09-26-x385-remedy-completeness/recovery-grading.log`. There are no further eligible review dispatches for this run under its stop decision.

This partial, stopped experiment does not establish an improvement or complete #380's adoption screen. A new attempt to qualify an inconclusive variant needs a separately preregistered run and spending decision; these caps are not extended.

The [complete-path audit replay](../2026-09-27-quoted-path-audit.json) checks all 95 saved audits. It adds two experiment invalidations for filesystem-root scans, preserves prior records, and changes no historical baseline classification.
