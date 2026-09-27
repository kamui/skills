# Run 2026-09-26-x381-action: #381 alone on frozen A

This run implements [#381](https://github.com/kamui/skills/issues/381) under the
[#389 protocol](../../../docs/research/builtin-review-benchmark-2026-09-24/README.md#13-preregistered-follow-up-isolated-a-changes-2026-09-25).
The maintainer authorized the three separate experiments on 2026-09-26, including the
existing $35, $30 and $45 caps. This run's total cap is $35, including replacements,
grading and adjudication. No fresh baseline run is authorized or planned.

## Frozen inputs

- Control: original A outputs in `2026-09-24-builtin-baseline`, corrected `results.v3.json`,
  skill tree `c3c53da5381dace16876b0f5b7abe4bccc6bc58b`.
- Candidate: `81efdd3e5c30e67f5370a9b67e1c9b4544e4faa2`, the control tree plus `candidate.patch` alone.
- Patch SHA-256: `46bd99408690845502d054b8d6facd0a4eb6fe5c2a29ed7487baedf64074ba5d`. It adds 272 UTF-8 bytes to `references/rubric.md`.
- Model: `claude-sonnet-5`, high effort, for primary and verifier workers, through Claude Code
  2.1.282. The original arm file and original factual packets and allowances are unchanged.
- Runtime workflow identity remains frozen A's identity; the candidate tree and patch identify
  this experiment. Release identities, budget-test limits and DESIGN history are not additional
  changes to the experimental tree.
- Cohort and register versions: i-requests-6667 v2, n-ripgrep-2957 v2, m-grpc-go-7390 v1, q-soba-195 v1.
- Order: replicate 1 across the cohort above, then replicate 2, then replicate 3.
- Caps: 12 planned cells, 14 maximum attempts, two invalid replacements,
  $5 reserved per attempt, $5 closeout reserve, one review in flight per experiment.
- Independent experiments may run concurrently in separate work directories. Do not compare
  pooled elapsed times across their different cohorts.

The runner now forwards its reserved attempt amount to Claude's `--max-budget-usd`.
Earlier dispatches had a hard-coded $15 CLI limit despite a $5 reservation. The correction
changes no reviewer prompt, tools, skill text or execution allowance. Claude's limit is checked
between requests; retain the actual metered cost and stop if it exhausts the run cap.
Raw transcripts and temporary clones remain outside the repository. File every attempt and charge.

## Decision rule

GT-n1 must be recovered as `must-fix` in 3/3 ripgrep reviews, with 0/3 approvals. Every recovered GT-i2 and GT-i3 must be actionable `must-fix` with a remedy, with at least one recovery of each. Requests recall must be at least 2/3. Do not promote unsupported late trust-store changes, pre-compinit behavior or grammar complaints.

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
5. Publish the evidence and closure work for review. Close #381 only when its acceptance
   conditions or documented rejection and revert are complete; report an inconclusive blocker.

## Results, 2026-09-27

**Disposition: reject.** The valid ripgrep review recovered no registered defect and approved. Frozen A recovered GT-n1 in both historical reviews. The common guardrail requires no loss of per-target recall, so this valid miss is a measured guardrail failure and further dispatch stops. Even perfect remaining replicates could produce only 2/3 recovery, below the required 3/3. This is an early guardrail stop, not a claim that all 12 planned cells ran. The valid Requests review also left recovered GT-i2 as `consider` with a partial remedy, so the action objective is not met. Revert the two action sentences; retain the shared runtime cap only because remaining rules still require it.

All existing outputs were blind-graded under the original template by Opus 5.5 high through Claude Code 2.1.282. No grader returned an unresolved new candidate. No additional review was purchased during recovery. Unattempted cells remain visible in `results.v1.json`; no missing cell is an approval or a recovered defect.

| Target | Valid / all attempts | Valid-review recall | Valid false findings | Median elapsed-to-payload |
| --- | ---: | ---: | ---: | --- |
| i-requests-6667 | 1/1 | 0.667 | 0 | 1123 s; n=1 |
| m-grpc-go-7390 | 0/1 | n/a | 0 | unavailable; n=0 |
| n-ripgrep-2957 | 1/1 | 0.000 | 0 | 718 s; n=1 |
| q-soba-195 | 0/0 | n/a | 0 | unavailable; n=0 |

- Validity: 2/3 attempts are valid. No replacements were dispatched.
- Costs: reviews $8.908711; blind grading $0.778697; total **$9.687408**, including invalid attempts. No adjudication was required.
- Action and remedies: the [scorecards](scoring/) grade each recovered defect and its remedy; each attempt's `normalized.json` retains native action and observations. All-attempt score fields can include invalid reviews; use the table's valid-review counts for guardrails.
- Timing: interrupted wrapper finalization leaves a missing elapsed-to-payload event on recovered outputs. `recovery.json` retains CLI durations separately; they are not substituted into the frozen metric. Medians show their actual valid, timed sample count.
- Audit correction: [the recovery report](../2026-09-27-audit-recovery.json) records every original and revised disposition. The local-clone correction changes no historical baseline classification across 83 audits. Historical baseline files remain unchanged; prior experiment records are in `audit-revisions/before-local-clone-fix/`. Existing filesystem violations are preserved.
- Run supervision: the original terminal jobs did not finish wrapper finalization for three completed CLI sessions. Recovery grading ran to completion in detached tmux sessions with logs under `~/.t3/bench-runs/2026-09-26-x381-action/recovery-grading.log`. There are no further eligible review dispatches for this run under its stop decision.

This partial, stopped experiment does not establish an improvement or complete #380's adoption screen. A new attempt to qualify an inconclusive variant needs a separately preregistered run and spending decision; these caps are not extended.
