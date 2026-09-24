# One record and prior-record re-reviews: bounded exercise, issue #357

This directory holds the bounded reviewer-and-caller exercise [#357](https://github.com/kamui/skills/issues/357) requires. It runs the four archived #341 tasks once each against the change: the one record shape, the `prior_record` continuation, and the scripted packet identity. It then runs each caller's local artifact path on the result, without forge writes. The runs are observations. One run per task supports no recall, precision, cost or latency claim. Exhausted-allowance and malformed-input edge cases stay in the CLI fixtures (`test_render_review.py`, `test_render_composition.py`, `test_forge_packet.py`, `test_command_chains.py`).

## Method

- **Skill.** `git archive` of `skills/review-code` at the implementation commit, installed at `/home/jack/.cache/rc357x/skill`.
- **Tasks.** [`exercise.py`](exercise.py) `prepare` materializes the [#341 archive](../review-code-artifact-savings-2026-09-22/archive/) with that skill and writes each task's prompt from [`prompts/`](prompts/). The prompts follow the archived ones, minus the retired `profile` and `return_format`. Each names `work/review` as the review's private directory, so the caller path can find the record.
- **Continuation reseeded as a prior record.** The archived seed is a version-2 record at `864eea8` and an addendum at `03ce7cd`. `prepare` finalizes the same decisions with this skill's `render_review.py`. `seed/r1` is the initial review at `864eea8`: a confirmed P1 `must-fix` (`accounts/frozen-transfer-bypass`), a P3 `consider` (`accounts/post-docstring-frozen`), and the initial batch spent. `seed/r2` is a re-review from `seed/r1` at `03ce7cd`. Both items are still open and rendered again, the must-fix carries its confirmation with `confirmed_in` naming `seed/r1`, and the follow-up is unspent. The continuation prompt passes `seed/r2` as `prior_record`, so the run takes the prior-record route, not the legacy full-review fallback.
- **Reviewer.** [`run_task.sh`](run_task.sh) runs `codex exec --json -m gpt-6-sol -c model_reasoning_effort=high -s danger-full-access` in the task directory. `HOME` and `CODEX_HOME` point at an isolated directory holding only `auth.json` and trust entries, so no installed skill, `AGENTS.md` or hook loads; the older `review-code` installed on the host could not leak in. The prompts direct each verifier batch to a fresh, awaited `codex exec` on the same model and effort, fed the bundle's `brief.md`.
- **Caller.** `exercise.py consume` runs `implement-publish`'s documented `render_review.py --check --head --lineage` for the implementation gate and the continuation. For the continuation it also checks the lineage, the prior record, the carried blocker, the allowance, the coverage and outstanding agreement, and that the seed records are byte-identical afterwards. For the two pull-request tasks it runs `review-code-publish`'s `--check`, reads `batch.json` and the `writes.jsonl` items `finalization.replies` would produce, and runs a gating `--emit-batch --event` into memory when the status admits one.
- **Observations.** `exercise.py observe` summarizes each event log: skill files read, `render_review.py` finalizations and repair loops, checks, `forge_packet.py` calls, verifier builds, dispatches and accounting, and token usage.

## Runs

All four ran on 2026-09-24 against the skill at implementation commit `04fe1b4`, one attempt each, in parallel. Every Codex process exited 0 and every verifier worker was awaited in the foreground. Each [`results/<task>/`](results/) holds the run metadata, the final message, the record and report, the caller's `consume.json`, the `observe.json` summary, and the gzipped event log with its uncompressed SHA-256.

| Task | Returned | Verifier | Allowance after | Elapsed |
| --- | --- | --- | --- | ---: |
| [publishable](results/publishable/) | Changes Requested: 1 P2 `must-fix` (`security`, CSV formula injection) | Initial, 1 candidate, confirmed | initial spent | 365 s |
| [implementation-gate](results/implementation-gate/) | Changes Requested: 2 P2 `must-fix` (running balance under a date filter; strict date format) | Initial, 2 candidates, confirmed | initial spent | 418 s |
| [required-verification](results/required-verification/) | Changes Requested: 3 P2 `must-fix` (`security` delegate set; two requirement bypasses) | Initial, 3 candidates confirmed, 2 safety premises hold | initial spent | 694 s |
| [continuation](results/continuation/) | Approved: both prior items `fixed`, nothing new | Follow-up, 1 `data-integrity` premise, holds | both spent (initial from the prior) | 296 s |

## Caller paths

Every caller check passed (`unmet` is empty in each `consume.json`).

- **implement-publish, implementation gate.** `render_review.py --check --head 2ba4046… --lineage <record>` exits 0 on the first record, with no prior record and an empty lineage.
- **implement-publish, continuation.** `--check --head b96a362… --lineage seed/r1 --lineage seed/r2 --lineage <new record>` exits 0. The final head is `b96a362`, the lineage is `[seed/r1, seed/r2]`, and `prior_record` is `seed/r2`. Both prior items are classified `fixed`. The primary rechecked the fixed `must-fix` itself, with no candidate task, and no blocker stays open. The allowance reads the initial batch as spent from the prior and the follow-up as spent by this run. Coverage is complete with nothing outstanding, and `seed/` is byte-identical afterwards. Two negative controls on the live record were refused with exit 1: a stale `--head 03ce7cd…`, and a `--lineage` naming a record it does not descend from, which is how a sibling fork reads to the caller.
- **review-code-publish, both pull-request tasks.** `--check` exits 0. `batch.json` names the reviewed head, with one and three line comments. `finalization.replies` yields no `writes.jsonl` items, since the packets carry no prior review. `--emit-batch --event REQUEST_CHANGES` exits 0 and removes the advisory suffix. Nothing was posted.

Carried blockers and a carried confirmation are exercised by the reseed, not the live continuation: `seed/r2` carries the open `must-fix` with `confirmed_in` naming `seed/r1`, and the finalizer accepted it. The live run fixed both items, so it carried nothing forward. The CLI fixtures cover a two-hop carried confirmation, allowance exhaustion and every refusal.

## Observations

These are counts from one run per task, not measurements of an effect.

- **Instruction loads.** Every primary read `SKILL.md`, `output.md` and `targets.md` once, and `rubric.md` twice. Every run dispatched one batch and read `verification.md`, publishable twice. Only the continuation read `prior-state.md`, three times. No primary opened `verifier.md` or `verifier-concurrency.md`.
- **Finalization.** Each run finalized once with `render_review.py` and exited 0: no repair loop. No run called `--check` itself except required-verification, once, and none called `forge_packet.py`, because the packets were supplied.
- **Known-defect recovery.** Publishable and the continuation each had a `build_verifier_prompt.py --return-file` build refused because the return directory did not exist yet. Each created it and rebuilt into a new bundle, and neither batch was charged twice. Required-verification's worker added an unknown `falsifying_condition` field to both premises, so accounting exited 1. The primary wrote a separate repaired return without those fields and accounted it to a new report, keeping the original's path in `record.paths`. These are verifier-transport and encoding paths that #358 changes. The implementation gate's first focused check failed to import the package and was rerun with `PYTHONPATH` set to the repository.
- **Return.** Every run returned the finalizer's status line and paths. The implementation gate and required-verification restyled the path lines as Markdown links with hard line breaks, and required-verification added two sentences; the caller path reads the files, so neither mattered here. Those two `last-message.md` files are stored with the trailing hard-break spaces stripped.
- **Tokens.** Input 1.09M–1.64M, 91–95% cached; output 8.7K–19.6K. Codex bills this on a plan, and one run per task supports no cost claim.

The implementation gate's two findings and the required-verification task's three differ from the #341 baseline cells, which ran a different model and harness, so the counts are not comparable.
