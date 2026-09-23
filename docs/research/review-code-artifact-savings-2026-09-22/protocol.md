# Paired interface protocol

Frozen on 2026-09-22 for [#341](https://github.com/kamui/skills/issues/341) before any cell ran. [#347](https://github.com/kamui/skills/issues/347) runs the treatment arm under it. A change to anything below needs a new freeze, recorded before its cells run.

## Cells

A cell is one archived task under one arm. The tasks are `publishable`, `implementation-gate`, `required-verification`, and `continuation`, in that order, from the [archive](archive/). The baseline arm is `review-code` at `d8c2dd93bbfff6ac85907159e7763508265f5442`, workflow `v5b-24`. The treatment arm is the combined head #347 names. Both arms receive the same prompts, inputs, repositories and seeded chain. Only the installed skill differs.

## Setting

- Model `claude-sonnet-5` at effort `high` for the primary and every worker. Workers use model `sonnet`, inherit effort, and run in the foreground (`run_in_background: false`). The prompts state this.
- Claude Code `2.1.280` on Linux, launched by [`run_cell.sh`](run_cell.sh). The session runs with `--safe-mode`, no setting sources, an empty MCP configuration and hooks disabled, so no CLAUDE.md, user instructions, skills, plugins or hooks load. Permissions are bypassed and `WebFetch` and `WebSearch` are disallowed. Network and filesystem bounds otherwise come from the prompt. The cap is $15 and the timeout 3,600 seconds per cell.
- Actual-setting verification: `python3 docs/research/tools/agent_effort.py --expect-model claude-sonnet-5 --expect-effort high` over the root transcript and every worker transcript. The harness's own helper-model charges in the result envelope are recorded, not treated as a mismatch.
- An unavailable input, a failed materialization check, a model or effort mismatch, a different harness version, or a capped or timed-out session makes the cell **inconclusive**. Nothing is substituted: no other model, effort, task, input or harness.

## Procedure

1. Install each arm's skill with `git archive <commit> skills/review-code | tar -x -C /tmp/rcs-savings/skills/<short sha>`. The skill root is `/tmp/rcs-savings/skills/<short sha>/skills/review-code`.
2. Run `python3 docs/research/tools/savings_archive.py verify <archive>`. Then run `materialize <archive> --root /tmp/rcs-savings/<arm> --skill-root <skill root>` and `check <archive> --root /tmp/rcs-savings/<arm>`. The baseline arm also passes `--skill-root` to `check`, which replays the seeded chain's helpers. The treatment skips that replay: it proves a seed matches baseline helpers, not treatment compatibility.
3. Run cells one at a time with `sh run_cell.sh /tmp/rcs-savings/<arm> <task> <skill root> <evidence dir>`, in task order and baseline before treatment. #347 may reuse this ticket's baseline cells only when the harness version, model id and launch command are unchanged. Otherwise it reruns the baseline arm in the same session as the treatment.
4. After each cell, run the effort check and `check <archive> --root /tmp/rcs-savings/<arm>`. The check confirms that realized inputs, the seeded chain and the repository are unchanged. The cell's own outputs under `work/` and a new addendum under `review/addenda/` are expected.
5. Collect `python3 docs/research/tools/interface_metrics.py cell --transcript <evidence>/transcript.jsonl --worker <each subagent transcript> --skill-root <skill root> --task-root /tmp/rcs-savings/<arm>/<task> --result <evidence>/stdout.json`. Copy the cell's `work/` directory and any new addendum into the evidence directory.

Each cell gets one attempt. A harness failure before the review starts, such as an API error or a refused launch, allows one replacement per arm. Every attempt is counted and kept. No cell is repeated to obtain a preferred outcome.

## Measurements

Per cell, from `interface_metrics.py`:

- root and worker turns, tool calls, input, cache writes and reads, output, and thinking;
- harness turn count, duration, cost, and spawned workers;
- turns, tool calls and seconds after the first successful payload or record validation, or after the last addendum write for a continuation;
- finalizer invocations and repair loops;
- instruction, helper-help, helper-example and script-source loads, in bytes and words as delivered, and each worker's dispatch prompt and loads;
- model-written artifacts by class and the mechanical/judgment field inventory of each JSON artifact.

Also record the returned status, finding, question and observation counts, whether the required artifacts exist and validate, and whether a verifier batch ran. The `required-verification` task must dispatch one. Its absence is a recorded protocol deviation, not a scoring input.

These are interface measurements on four small tasks. They establish no review recall and no general cost or latency result. A missing cell stays inconclusive in any comparison.
