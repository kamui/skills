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

## Results

Pending. No reviewer was dispatched before this manifest and decision rule were frozen.
