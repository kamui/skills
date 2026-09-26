# Run 2026-09-26-x384-lifecycle: #384 alone on frozen A

This run implements [#384](https://github.com/kamui/skills/issues/384) under the
[#389 protocol](../../../docs/research/builtin-review-benchmark-2026-09-24/README.md#13-preregistered-follow-up-isolated-a-changes-2026-09-25).
The maintainer authorized the three separate experiments on 2026-09-26, including the
existing $35, $30 and $45 caps. This run's total cap is $30, including replacements,
grading and adjudication. No fresh baseline run is authorized or planned.

## Frozen inputs

- Control: original A outputs in `2026-09-24-builtin-baseline`, corrected `results.v3.json`,
  skill tree `c3c53da5381dace16876b0f5b7abe4bccc6bc58b`.
- Candidate: `938f7c80925248cc76943317d6fec243ddac5a08`, the control tree plus `candidate.patch` alone.
- Patch SHA-256: `da0a42b02fa4d7396457c78c20d8a6307ecb831c266f51e8e39b22679ba26c8f`. It adds 153 UTF-8 bytes to `SKILL.md`.
- Model: `claude-sonnet-5`, high effort, for primary and verifier workers, through Claude Code
  2.1.282. The original arm file and original factual packets and allowances are unchanged.
- Runtime workflow identity remains frozen A's identity; the candidate tree and patch identify
  this experiment. Release identities, budget-test limits and DESIGN history are not additional
  changes to the experimental tree.
- Cohort and register versions: r-base-ui-5460 v1, m-grpc-go-7390 v1, q-soba-195 v1.
- Order: replicate 1 across the cohort above, then replicate 2, then replicate 3.
- Caps: 9 planned cells, 11 maximum attempts, two invalid replacements,
  $5 reserved per attempt, $5 closeout reserve, one review in flight per experiment.
- Independent experiments may run concurrently in separate work directories. Do not compare
  pooled elapsed times across their different cohorts.

The runner now forwards its reserved attempt amount to Claude's `--max-budget-usd`.
Earlier dispatches had a hard-coded $15 CLI limit despite a $5 reservation. The correction
changes no reviewer prompt, tools, skill text or execution allowance. Claude's limit is checked
between requests; retain the actual metered cost and stop if it exhausts the run cap.
Raw transcripts and temporary clones remain outside the repository. File every attempt and charge.

## Decision rule

GT-r1 and GT-r2 must each be recovered in at least 2/3 Base UI reviews. Each target's median elapsed-to-payload must be no more than 1.25 times its frozen A median. Exclude null/control-mode-switch claims, intended cancellation behavior, the accepted extra render and pre-existing uncontrolled remount behavior. Record concrete base/head lifecycle transitions for recovered defects.

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
5. Publish the evidence and closure work for review. Close #384 only when its acceptance
   conditions or documented rejection and revert are complete; report an inconclusive blocker.

## Results

Pending. No reviewer was dispatched before this manifest and decision rule were frozen.
