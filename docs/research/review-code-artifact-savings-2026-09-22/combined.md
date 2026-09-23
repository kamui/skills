# Combined artifact interfaces, issue #347

This measures #342–#346 together on the four archived tasks, under the [protocol](protocol.md) that #341 froze. It implements [#347](https://github.com/kamui/skills/issues/347) for the epic [#340](https://github.com/kamui/skills/issues/340). The result is informational acceptance evidence. It is not a retroactive gate on the merged feature changes, and it establishes no review recall.

**Arms.**
- The **treatment** is `review-code` at `1684cf4d`, `origin/main` after #353 merged #346.
- The **#341 baseline** is `d8c2dd9`, the cells [README.md](README.md) reports.
- The **control** reruns `d8c2dd9` in the same session as the treatment.

All three arms run at workflow `v5b-24`. [treatment/freeze.md](treatment/freeze.md) records the treatment freeze before its cells ran, and the control amendment before the control cells ran.

## Attempts and settings

The paid attempts were eight cells: four treatment and four control. All exited 0. None was capped, timed out, retried or denied a permission, and no preflight ran. The treatment cost $1.9953 and the control $1.7775, a total of $3.7728 at harness list price. The cells ran one at a time on 2026-09-23: the treatment from 20:44 to 20:52 UTC and the control from 20:56 to 21:04 UTC.

The launcher pinned Claude Code `2.1.280`, the version the baseline used, through a `PATH` entry. The host default had moved to `2.1.281`. `agent_effort.py` found `claude-sonnet-5` at `high` on every assistant line of all eight root and seven worker transcripts (`effort.txt` in each cell). After every cell, `savings_archive.py check` still matched the archive. No cell is unavailable.

**Cache conditions.** Every cell started a new session. Each root session's first request wrote to the 1-hour cache, and later writes mixed 5-minute and 1-hour TTLs in every arm. The first request read 18,170 cached tokens in each #341 cell. Today's cells read between 8,244 and 16,788: 9,221 in all four control cells and in two treatment cells. The prefix the harness sends therefore changed between the two days on the same binary.

## Why a control arm

Protocol step 3 lets #347 reuse the #341 cells when the harness version, model id and launch command are unchanged. All three were unchanged. The treatment workers read generated briefs within 1–10% of the baseline workers' bundle words, yet their turns fell from 8–10 to 4–5 and their thinking from 3,655–8,331 tokens to 67–1,082. Something outside the skill had changed. The control reran the baseline skill beside the treatment to separate the two, and its totals confirm the drift:

| Arm | All turns / tool calls | Cache read | Cache write | Output | Thinking | Process elapsed | Harness cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| #341 baseline | 169 / 240 | 11,258,984 | 513,179 | 162,519 | 89,431 | 1,685.1 s | $5.7695 |
| Control, `d8c2dd9` today | 73 / 76 | 2,377,171 | 232,560 | 44,138 | 5,732 | 448.7 s | $1.7775 |
| Treatment, `1684cf4` today | 79 / 79 | 2,729,396 | 272,520 | 46,170 | 9,055 | 467.0 s | $1.9953 |

Against the #341 baseline, the treatment used 65% less cost and 72% less elapsed time. The control, running the same baseline skill, fell by about as much. **Those reductions are drift, not the interface.** Against the same-session control, the treatment used 3 more tool calls (79 against 76), 15% more cache reads and $0.22 more across the four cells. With one pair per task these are not savings or cost results in either direction. The mechanical effects below hold across the pairs and match what each feature changed.

## Contract comparison

**Checks at `1684cf4`.** Every `review-code` test file passes on Python 3.14.7:

| Group | Result |
| --- | --- |
| unittest files | check runs 9, command chains 17, continuation 21, finalization 21, review context 7, run events 27, thread writes 18, verifier handoff 26 |
| case-group files | composer 28 `ok` cases, context fingerprint 12 groups, deleted-file links 13 cases, forge packet 8 groups |
| instruction budget | passes |

The research tool tests pass, including the updated `test_interface_metrics.py`. `git diff --check d8c2dd9 1684cf4` is clean.

`implement-publish` and `review-code-publish` ship no scripts. `test_command_chains.py`, `test_thread_writes.py` and `test_continue_review.py`'s installed-caller test drive their review-code contracts through the returned helper paths. Those contracts are `finalize_review.py --check`, the continuation helper path, and publication inputs.

**Public shapes.** Where both arms produced them, the payloads have the same top-level keys (`summary`, `items`) and the same `summary` keys. The batches have the same keys (`commit_id`, `event`, `body`, `comments`). Finding items carry the same keys, with `fix` optional. The gate record stays `implementation-gate-record/2` and the addendum `implementation-gate-addendum/2`. The treatment adds only the `finalization` block (`review-code-finalization/1`) to each record and addendum. Every treatment output passes the treatment's own read-only check:
- `finalize_review.py --check` exits 0 on both pull-request work directories.
- `finalize_review.py --check --profile implementation-gate` exits 0 on the gate work directory.
- `continue_review.py state` exits 0 on the continuation chain, which now ends at `b96a362`.

**Additive contracts.** Each is opt-in or additive, so an earlier caller's inputs and returns still work:
- **Generated report (#342).** The finalizer writes `report.md` last. `return_format: artifacts` with `--compact` returns status, coverage and paths instead of the report, and `--check` re-reads them.
- **Required accounting (#342).** Finalization now requires the composition's `record` for both profiles, including publishable reviews that earlier omitted it.
- **Derived metadata (#343).** A saved `fingerprint.json` sits beside the store and packet, and the finalizer derives run identity and the context digest from them.
- **Worker-saved returns (#344).** `build_verifier_prompt.py --return-file` enables file transport. `account_verifier_return.py` handles an inline fallback with `--inline-fallback` and records a repair with `--repair-of`.
- **Continuation helper (#345).** It takes a `continuation.json` and runs `continue_review.py compose` and `state`. Compose writes the addendum's own `.report.md`.

**Invalid chains.** At the baseline no script validated an addendum, and `continuation-addendum.md` stated the rejections in prose. `test_continue_review.py` now asserts them. Its `test_malformed_missing_forked_cyclic_and_mismatched_chains`, `test_unknown_protocols_and_missing_reports`, `test_explicit_dropping_of_carried_state_fails`, `test_replacement_that_drops_state_is_invalid` and `test_version_one_and_mixed_chains_route_to_the_manual_mapping` all pass. So does `test_installed_caller_reads_the_helper_path_and_cannot_publish_from_an_invalid_chain`, and a mixed or version-1 chain still routes to the manual mapping.

**Outcomes.** These are recorded as observed, not scored:

| Task | #341 baseline | Control | Treatment |
| --- | --- | --- | --- |
| publishable | Changes Requested: `export/csv-formula-injection` P2 must-fix (security) at `ledger/export.py:18`, confirmed | Approved, no findings, no verifier batch | **Incomplete**: no findings. A security premise `fails`; the primary judged the reopened candidate inadmissible, left it `outstanding` and did not spend the follow-up |
| implementation-gate | Approved, no batch | Changes Requested: `ledger/statement/running-balance-not-from-opening` P2 must-fix at `ledger/statement.py:33`, confirmed | Changes Requested: `ledger/statement/running-balance-posting-order` P2 must-fix at `ledger/statement.py:34`, confirmed |
| required-verification | Changes Requested: two must-fix (`grant-revoke-auth-placement` P2 security, `grant-revoke-docstring-errors` P3); tasks not recorded in the composition | Approved: `grant-owner-check-outside-auth` P3 consider; tasks not recorded | Approved, no findings; both security premises `holds`, recorded |
| continuation | Approved; both fixes `fixed`; two premises `holds`; follow-up spent | Same | Same |

The control and the treatment found the same gate defect. The running balance counts entries the date filter excludes, whenever entries were posted out of date order. Reading `statement_rows` at `2ba4046` confirms it. The #341 baseline missed it, and today's control and treatment missed the baseline's CSV formula injection. The two runs of `d8c2dd9` disagree about as much as the arms do, so these single runs support no recall claim.

The contract checks found no loss of required content or state. Every treatment report holds each finding and question once, and every treatment record keeps its verification tasks, rulings and allowance. By contrast, both `d8c2dd9` runs of the required-verification task, and the control's publishable run, composed without `record`. Their verification state therefore reached no durable artifact, which #342's requirement now prevents.

## Interface measurements

All from `interface_metrics.py cell` in each cell's `metrics.json`.

### Usage

| Cell | Arm | Root turns / tool calls | Worker turns / tool calls | Cache read (all) | Cache write (all) | Output (all) | Thinking (all) | Process elapsed | Harness cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| publishable | #341 baseline | 44 / 60 | 8 / 10 | 3,833,433 | 154,922 | 46,385 | 24,427 | 443.8 s | $1.7964 |
| publishable | Control | 13 / 12 | — | 389,746 | 36,121 | 5,434 | 642 | 62.5 s | $0.2784 |
| publishable | Treatment | 20 / 20 | 5 / 5 | 1,084,314 | 88,417 | 16,225 | 5,253 | 169.6 s | $0.6941 |
| implementation-gate | #341 baseline | 34 / 52 | — | 2,396,868 | 97,344 | 36,884 | 20,652 | 357.7 s | $1.2393 |
| implementation-gate | Control | 19 / 19 | 4 / 5 | 799,471 | 69,781 | 12,188 | 1,131 | 121.2 s | $0.5330 |
| implementation-gate | Treatment | 15 / 14 | 4 / 4 | 586,427 | 70,055 | 10,960 | 1,490 | 107.8 s | $0.4794 |
| required-verification | #341 baseline | 35 / 58 | 9 / 14 | 3,120,411 | 152,068 | 51,564 | 30,429 | 616.0 s | $1.6895 |
| required-verification | Control | 15 / 15 | 5 / 5 | 665,689 | 69,911 | 15,961 | 2,894 | 159.3 s | $0.5465 |
| required-verification | Treatment | 12 / 13 | 4 / 4 | 482,599 | 58,247 | 9,223 | 1,201 | 92.9 s | $0.4034 |
| continuation | #341 baseline | 29 / 36 | 10 / 10 | 1,908,272 | 108,845 | 27,686 | 13,923 | 267.5 s | $1.0443 |
| continuation | Control | 13 / 16 | 4 / 4 | 522,265 | 56,747 | 10,555 | 1,065 | 105.8 s | $0.4196 |
| continuation | Treatment | 15 / 15 | 4 / 4 | 576,056 | 55,801 | 9,762 | 1,111 | 96.7 s | $0.4183 |

The control's publishable review ran no verifier batch, while the treatment's ran one. That accounts for much of the difference in that pair.

### Validation tail and repairs

| Cell | Arm | Finalizer calls / failed / repair loops | After first validated output: turns / tool calls / seconds | `report.md` written by |
| --- | --- | --- | --- | --- |
| publishable | #341 baseline | 1 / 0 / 0 | 5 / 5 / 44.9 | model (10,054 characters) |
| publishable | Control | 1 / 0 / 0 | 3 / 2 / 21.1 | model (2,827 characters) |
| publishable | Treatment | 4 / 3 / 3 | 1 / 0 / 7.8 | finalizer |
| implementation-gate | #341 baseline | 1 / 0 / 0 | 5 / 4 / 53.1 | model (9,351 characters) |
| implementation-gate | Control | 1 / 0 / 0 | 3 / 2 / 20.9 | model (3,223 characters) |
| implementation-gate | Treatment | 1 / 0 / 0 | 2 / 1 / 9.0 | finalizer |
| required-verification | #341 baseline | 1 / 0 / 0 | 5 / 6 / 74.7 | model (12,692 characters) |
| required-verification | Control | 1 / 0 / 0 | 3 / 2 / 31.6 | model (5,306 characters) |
| required-verification | Treatment | 2 / 1 / 1 | 2 / 1 / 8.5 | finalizer |
| continuation | #341 baseline | none | after the addendum write: 3 / 2 / 34.7 | model (5,516 characters) |
| continuation | Control | none | after the addendum write: 2 / 1 / 21.1 | model (3,494 characters) |
| continuation | Treatment | 1 / 0 / 0 (`continue_review.py compose`) | 2 / 1 / 13.0 | helper; the model then copied it to `work/report.md` with a 946-character Bash write |

This is #342's effect, and it holds in every pair. No treatment primary wrote a report after validation. In the three finalizer cells the post-validation tail fell to 1–2 turns and 7.8–9.0 s, against 3 turns and 20.9–31.6 s in the control. The continuation tail is shorter, at 13.0 s against 21.1 s.

The cost was **repair loops**. The treatment failed 3 finalizer calls in the publishable cell and 1 in the required-verification cell; the control and baseline failed none. Each refusal named a rule the composition broke:
- A failed premise needs `reopened_as` or an `outstanding` entry. The composer applies this rule at both revisions.
- An `incomplete` run needs `coverage_gaps`, and then as a list.
- The composition needs a `run` object.

Each was fixed in one turn. In the continuation, `account_verifier_return.py` refused an unknown `safety_rulings` field on a premise. The primary wrote a repaired return and accounted it with `--repair-of`. That rerun refused to overwrite `accounting.json`, so the primary renamed the original report to `accounting-original.json`, where `verifier-handoff.md` asks for a new report path. No record lost state, but that one step departed from the documented repair.

### Loads

| Cell | Arm | Entrypoint + references (words delivered) | Helper help / example (words) | Script source (words) | Mixed calls (words) | Worker dispatch / bundle words |
| --- | --- | --- | --- | --- | --- | --- |
| publishable | #341 baseline | 1 + 9 (9,806) | 8 / 2 (1,335) | 5 (4,501) | 0 (0) | 243 / 2,435 |
| publishable | Control | 1 + 5 (1,951) | 0 / 2 (347) | 0 (0) | 0 (0) | — |
| publishable | Treatment | 1 + 8 (5,862) | 1 / 3 (729) | 4 (636) | 1 (2,525) | 53 / 2,383 |
| implementation-gate | #341 baseline | 1 + 7 (8,235) | 4 / 1 (1,002) | 2 (1,041) | 0 (0) | — |
| implementation-gate | Control | 1 + 9 (8,575) | 1 / 3 (540) | 0 (0) | 1 (387) | 56 / 2,597 |
| implementation-gate | Treatment | 1 + 8 (8,035) | 0 / 3 (834) | 0 (0) | 0 (0) | 46 / 2,452 |
| required-verification | #341 baseline | 1 + 9 (9,054) | 6 / 3 (1,194) | 1 (90) | 1 (182) | 279 / 2,613 |
| required-verification | Control | 1 + 6 (7,358) | 1 / 4 (172) | 2 (in mixed) | 3 (1,257) | 56 / 2,994 |
| required-verification | Treatment | 1 + 5 (7,185) | 0 / 3 (846) | 0 (0) | 0 (0) | 51 / 2,380 |
| continuation | #341 baseline | 1 + 4 (5,900) | 0 / 1 (211) | 7 (3,522) | 0 (0) | 111 / 2,254 |
| continuation | Control | 1 + 5 (6,018) | 1 / 2 (71) | 0 (0) | 1 (822) | 48 / 2,280 |
| continuation | Treatment | 1 + 3 (4,323) | 0 / 2 (588) | 0 (0) | 0 (0) | 39 / 2,317 |

Helper help and source reads fell sharply in the control too, so drift explains most of the change from #341. Today, both arms read little helper source. The treatment read it only in the publishable cell, where it read `compose_review.py` four times (636 words) while repairing. The control read it only in required-verification, twice, inside mixed calls. Help calls went from 1 in the control to 0 in the treatment's gate, required-verification and continuation cells, and from 0 to 1 in publishable.

Worker-only references still load. The treatment's publishable and gate primaries both opened `verifier-concurrency.md` and `verifier-return.md` despite #346's load condition, the publishable primary in its one mixed call. The required-verification and continuation primaries did not. Static text is about flat: [`treatment/static.json`](treatment/static.json) has `SKILL.md` at 1,630 words, against 1,596, and the 14 references at 10,659 words, against 10,771.

### Authored fields (mechanical / judgment leaves)

| Cell | Arm | Composition, addendum or continuation input | Fingerprint input | Verifier input | Raw return |
| --- | --- | --- | --- | --- | --- |
| publishable | #341 baseline | 30 / 55 | — | 8 / 33 | 1 / 26 |
| publishable | Control | 8 / 9 | — | — | — |
| publishable | Treatment | 31 / 59 | 1 / 0 | 8 / 23 | 1 / 30 |
| implementation-gate | #341 baseline | 34 / 63 | 5 / 0 | — | — |
| implementation-gate | Control | 36 / 66 | 5 / 0 | 8 / 32 | 1 / 17 |
| implementation-gate | Treatment | 20 / 62 | 5 / 0 | 8 / 28 | 1 / 20 |
| required-verification | #341 baseline | 8 / 38 | — | 8 / 56 | 1 / 31 |
| required-verification | Control | 8 / 21 | — | 8 / 52 | 1 / 59 |
| required-verification | Treatment | 31 / 61 | 1 / 0 | 8 / 25 | 1 / 29 |
| continuation | #341 baseline | 22 / 35 (addendum) | — | 8 / 17 | 1 / 21 |
| continuation | Control | 23 / 38 (addendum) | — | 8 / 17 | 1 / 25 |
| continuation | Treatment | 10 / 30 (continuation input) | — | 8 / 21 | 1 / 24; repaired 1 / 23 |

Three effects stand out:
- **#343.** The gate composition's mechanical leaves fell from 36 to 20.
- **#345.** A continuation input of 10 mechanical leaves replaced a hand-written addendum of 22–23. The helper also validated the chain, where the control's addendum went unchecked.
- **#342's precondition.** The required-verification composition grew from 8 to 31 mechanical leaves, because it now has to carry `record`. The pull-request compositions that omitted `record` were exactly the ones whose verification state went unrecorded.

Verifier inputs still carry 8 mechanical leaves in every arm.

## Conditional paths and worker growth

- **File transport was never chosen.** All four treatment primaries dispatched inline, because a Claude Code general-purpose worker cannot be limited to creating one file. #344's condition held them to inline. They then saved each raw return themselves with a Bash heredoc: 20–30 judgment leaves, and in the continuation a second, repaired return. On this host the transcription #344 removes is still paid, and the file path is exercised only by `test_verifier_handoff.py`.
- **Workers.** Dispatch prompts were 39–53 words in the treatment and 48–56 in the control. Bundle loads were 2,317–2,452 words in the treatment and 2,280–2,994 in the control. The inline example brief grew by 155 bytes, from 22,786 to 22,941. A file-transport brief would be 23,385 bytes: 599 bytes and 87 words over the baseline, within the unchanged 24,000-byte limit.
- **Stricter finalization.** Requiring accounting and validated continuations cost the treatment 4 finalizer repair loops and one return repair across four cells. The control had none. In exchange, every treatment artifact records its verification state, and a malformed chain is refused rather than silently written.

## Epic report for #340

- **Contracts.** #342–#346 kept every public payload, batch, finding, status, anchor and allowance shape, and added only the `finalization` block and opt-in inputs. All `review-code` tests pass at `1684cf4`, and they assert the invalid-chain rejections the baseline left to prose. No run lost required content or state.
- **Supported mechanical effects,** each measured against a same-session control:
  - The model no longer writes the report after validation. The tail fell from 2–3 turns and 21–32 s to 1–2 turns and 8–13 s.
  - Gate compositions carry 16 fewer mechanical leaves.
  - Continuations write a validated 10-leaf input, not a 22–23-leaf addendum.
  - The one treatment read of helper source came during a repair.
- **Costs and open risks:**
  - Finalizer and accounting repairs rose from 0 to 5 across the four cells.
  - Pull-request compositions carry more mechanical fields, because they must record accounting.
  - Primaries still transcribe verifier returns, because the host cannot confine a worker to one file.
  - Primaries still open worker-only references.
  - One return repair renamed a helper-written report by hand.
- **No savings claim.** The four pairs show no overall cost, latency or quality change against the control: $1.9953 against $1.7775. The apparent 65% drop against #341 is harness and model drift, measured by the control. Recall moved as much between two runs of one revision as between arms. The earlier rewrite's inconclusive disposition (#333) stands.

A follow-up could:
- have `account_verifier_return.py`'s repair example name a new output path;
- look at why primaries still open worker-only references;
- decide whether a host that can confine worker writes is worth targeting before the transcription saving is counted.

## Tool changes

`interface_metrics.py` gained what the treatment's interfaces need, with tests:
- `continue_review.py compose` is a finalizer call, and its first success starts the validation tail. `--check` and `state` are read-only and are not counted.
- A continuation input has its own inventory. Its mechanical fields are the addendum's, minus what the helper now derives.
- A saved fingerprint input holding only `specs` is recognized.
- `static` measures `continue_review.py`'s help and example, and skips a helper a revision does not ship.
- `NAME=value;` assignments expand like one-line assignments.
- A heredoc write resolves against its starting directory and any top-level `cd`, so relative addendum writes count.

Rerunning the tool on the four #341 cells reproduces their committed `metrics.json` exactly, except the continuation's `validation.reason` text, which now names the continuation helper. The static inventory reproduces too. The committed baseline files are unchanged.

## Reproduce

```sh
T=/tmp/rcs-savings D=docs/research/review-code-artifact-savings-2026-09-22
mkdir -p $T/harness-2.1.280 && ln -sfn ~/.local/share/claude/versions/2.1.280 $T/harness-2.1.280/claude
git archive 1684cf4 skills/review-code | tar -x -C $T/skills/1684cf4
python3 docs/research/tools/savings_archive.py materialize $D/archive --root $T/treatment --skill-root $T/skills/1684cf4/skills/review-code
python3 docs/research/tools/savings_archive.py check $D/archive --root $T/treatment
PATH=$T/harness-2.1.280:$PATH sh $D/run_cell.sh $T/treatment <task> $T/skills/1684cf4/skills/review-code $T/evidence/treatment/<task>
sh $D/collect_cell.sh $T/treatment <task> $T/skills/1684cf4/skills/review-code $T/evidence/treatment/<task> $D/treatment/<task>
```

The control uses `d8c2dd9`, `--root $T/control`, and `check --skill-root` for the seeded-chain replay. `collect_cell.sh` writes `metrics.json` with the tool as it was when collected. The committed `treatment/` and `control/` metrics were regenerated with the final tool, using the same `interface_metrics.py cell` command.

## Limits

- Each task has one pair per arm, so run-to-run variance is unmeasured beyond what the two `d8c2dd9` runs show.
- Process elapsed time is the launcher's wall clock, and cost is the harness's list price.
- The control is outside the frozen protocol's original plan. It was recorded in [treatment/freeze.md](treatment/freeze.md) before it ran, and it replaced nothing.
- Evidence paths name `/tmp/rcs-savings`.
