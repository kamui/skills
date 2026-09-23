# review-code — one-shot / publishable review of kamui/skills#325

## Run identity (pinned)

| | |
| --- | --- |
| Repository | `kamui/skills` (`https://github.com/kamui/skills`) |
| Pull request | [`kamui/skills#325`](https://github.com/kamui/skills/pull/325) — "Move review-code's first-review eligibility guard into forge_packet.py" |
| Head | `0ea287f0c07fda09b9d063612353dcef37f38063` |
| Base ref / SHA | `main` / `160d1201bed57d96de6fc8b1ae657bd098aa2de6` |
| Merge-base | `160d1201bed57d96de6fc8b1ae657bd098aa2de6` (identical to base SHA) |
| `state` / `merged` | `MERGED` / `true` (merged 2026-09-22T20:24:30Z) |
| Mode | Retrospective review of a merged pull request; **publication disabled** (no separately recorded authorization) |
| Reviewer identity | `kamui`; no prior review, thread, or comment from this identity in the packet at the frozen cutoff → ordinary first review, not a re-review; duplicate-review shortcut not applicable (no prior state exists to shortcut against) |
| Gating | Withheld per orchestrator instruction; `review-code` itself never publishes or gates in any case |
| Phase-1 source | Supplied packet at `/tmp/issue-333/cells/44b9331a/packet.md`, treated as authoritative pinned input per the packet's own instruction; no live fetch attempted or available |
| Originating issue(s) | `issues=none` — PR body carries no closing reference; intent taken from `pr-title`/`pr-body` |
| Mode invoked | `mode: one-shot`, `profile: publishable` |
| Skill root (absolute) | `/tmp/issue-333/snapshots/44b9331a/skills/review-code` |
| Reviewed clone | `/tmp/issue-333/cells/44b9331a/repo` |
| Private work directory | `/tmp/issue-333/cells/44b9331a/work/private` |
| Context store | `/tmp/issue-333/cells/44b9331a/work/private/store.json` |
| Context digest (`context_fingerprint.py`) | `a2534d17a7398c34bcaed6aa63b21f2b2c97bc002ec708981e689feac366ef53` |
| Workflow | `v5b-24` (this skill installation's `rendering.md` identity; the target repo's own copy of `review-code` separately defines and retains its own `v5b-22`, which this diff does not touch — see Requirement ledger) |

## Status: **Approved**

No unsettled `must-fix` (no findings at all), coverage is complete, and there is no open material question. Per the rubric's status derivation this is `Approved`.

## Complete would-be review (exactly as it would be posted, publication disabled)

This is `payload.json`'s `summary.body`, verbatim — the composer-rendered artifact `review-code` produces at this profile. It was never posted anywhere; publication and `review-code-publish` were not invoked.

> **Approved (advisory)** — no findings.
>
> **Mode:** Retrospective review of merged pull request; publication disabled.
>
> **Intent:** Move the pull-request root invocation's first-review eligibility guard out of a 42-line Python heredoc embedded in `references/pull-request-target.md` and into a new `eligibility` subcommand of `scripts/forge_packet.py`, preserving every condition, deferral reason, verdict line, and the block's exit handling exactly, per pr-title and pr-body.
>
> **Issue fit:** Issue alignment unavailable: `issues=none`, no closing reference or linked spec. Intent is taken from pr-title and pr-body. Both checkable claims there hold: the guard's conditions/reasons/verdict lines and the block's exit handling are unchanged (verified by tracing the moved logic against the removed heredoc, byte for byte apart from `raise Deferred(...)` replacing `defer()`'s print+exit), and `test_command_chains.py`/`test_run_events.py` were updated exactly as described (one placeholder substitution each) with all cases, including the truthy non-object `data` guard-failure case, intact and passing.
>
> **Coverage:** Complete merge-base diff reviewed across all 6 changed files (CHANGELOG.md, DESIGN.md, references/pull-request-target.md, scripts/forge_packet.py, scripts/test_command_chains.py, scripts/test_run_events.py). Focused checks run once at the pinned head from `skills/review-code`: `scripts/forge_packet.py --self-test` (pass), `scripts/test_forge_packet.py` (pass, 8 case groups), `scripts/test_command_chains.py` full suite (pass, 19 tests) and its four `root_block`-related tests individually, `scripts/test_run_events.py` full suite (pass, 26 tests, including the documented-command replay that needed the new placeholder). Byte-count claims in the PR body and CHANGELOG/DESIGN.md entries (`pull-request-target.md` 12,566 → 8,775) were independently recomputed and match exactly. `workflow=v5b-22` is defined in `references/review-record.md`/`scripts/validate_review.py`/`scripts/run_events.py`, none of which this diff touches, so "workflow retained" is trivially true.
>
> **Reviewed:** `0ea287f` against merge-base `160d120`.
>
> ## Observations
>
> - `forge_packet.py`'s new `eligibility()` function and CLI subcommand carry no direct test in `test_forge_packet.py` (the file that unit-tests `normalize` and `later-state` in isolation); all of its coverage remains indirect, through `test_command_chains.py`'s shell-block integration tests, unchanged in scope by this move. Evidence: scripts/test_forge_packet.py has no `eligibility` reference; scripts/test_command_chains.py:339-407 (`root_block`/`assert_deferred` tests) are the sole coverage, and they pass.
>
> <!-- review-run head=0ea287f0c07fda09b9d063612353dcef37f38063 base-ref=main base-sha=160d1201bed57d96de6fc8b1ae657bd098aa2de6 merge-base=160d1201bed57d96de6fc8b1ae657bd098aa2de6 workflow=v5b-24 context=a2534d17a7398c34bcaed6aa63b21f2b2c97bc002ec708981e689feac366ef53 issues=none coverage=complete -->

**Findings:** none.
**Questions:** none.
**Observations (1 of max 3 published):** the test-coverage-location fact quoted above. No other eligible observation exceeded the cap.

## Requirement / issue-fit ledger

No originating issue or spec (`issues=none`). Rows below are drawn from `pr-title` and `pr-body/"<quoted phrase>"` (class: supporting assertions describing the mechanical move, not acceptance criteria in the formal sense, since there is no linked issue to set acceptance criteria — treated as checkable claims under the rubric's Issue fit section regardless).

| # | Coordinate | Claim | Class | Disposition | Evidence |
| - | - | - | - | - | - |
| 1 | `pr-title` | "Move review-code's first-review eligibility guard into forge_packet.py" | supporting assertion | met | `git diff main review-head -- skills/review-code/references/pull-request-target.md skills/review-code/scripts/forge_packet.py`: the heredoc is gone from the reference; `forge_packet.py` gains `eligibility()`/`Deferred`/the `eligibility` subparser. |
| 2 | `pr-body/"Conditions, deferral reasons, verdict lines, and the block's exit handling are unchanged."` | behavioral equivalence of the moved guard | supporting assertion | met | Line-by-line trace: every `defer(reason)` call site in the old heredoc has an identical `raise Deferred(reason)` at the same logical point in `eligibility()`; the uncaught-exception path (e.g. a truthy non-object `data`) propagates the same way through `main()`'s undecorated `if args.command == "eligibility": try/except Deferred` to the same non-zero exit; the surrounding shell block (`rc=$?` capture, `deferred: eligibility guard failed with exit $rc` fallback, `read -r verdict merge_base head`, the `eligible` branch's build invocation, and both failure exits) is byte-identical apart from the substituted script-call line and the added `packet=<forge-packet-script>` variable. |
| 3 | `pr-body/"test_command_chains.py runs the block with the same cases and assertions, including the guard that raises on a truthy non-object data."` | test parity | supporting assertion | met | `git diff` on `test_command_chains.py` shows exactly one added line (`.replace("<forge-packet-script>", ...)`); `test_root_block_defers_when_first_review_status_is_unproven`'s `"guard exits without a verdict"` subtest (still present, unmodified) exercises `{"data": "x"}` and asserts `AttributeError` in stderr with exit 1 → `deferred: eligibility guard failed with exit 1`. Ran and passed. |
| 4 | `pr-body/"test_run_events.py binds the new placeholder in its documented-command replay."` | test parity | supporting assertion | met | `git diff` on `test_run_events.py` shows exactly one added line, in `test_documented_wrapped_commands_run`, which greps every ```` ```sh ```` fence out of `pull-request-target.md` and replays it; without the added `.replace(...)` the `<forge-packet-script>` placeholder would reach `sh -c` literally and fail. Ran full suite (26 tests) — pass. |
| 5 | `pr-body/"Workflow v5b-22 is retained. No rule changes."` | workflow/state-semantics claim | supporting assertion | met (trivial) | `v5b-22` is defined in `references/review-record.md`, `scripts/validate_review.py`, and `scripts/run_events.py`; `git diff main review-head --stat -- SKILL.md references/` shows only `pull-request-target.md` changed among references, and the workflow identifier is not written anywhere in this diff. No admission/verification/rendering/state rule is touched. |
| 6 | `pr-body` table: `references/pull-request-target.md` 12,566 → 8,775 bytes | measurement | supporting assertion | met | `git show <sha>:skills/review-code/references/pull-request-target.md \| wc -c` at both `main` and `review-head`: `12566` and `8775` exactly. |
| 7 | `pr-body/"The reference loads only for pull-request targets, so the always-loaded set stays at 92,272 bytes."` | measurement/no-change claim | supporting assertion | met (trivial) | `pull-request-target.md` is conditionally loaded (per `SKILL.md`'s Strategy) and is not one of the always-loaded files (`SKILL.md`, `review-rubric.md`, `review-record.md` per this repository's own `DESIGN.md:77`); this PR touches none of those three files, so their combined size is unchanged by construction regardless of what that combined size actually is. |
| 8 | `pr-body` Checks: "all 10 `scripts/test_*.py` suites, `validate_review.py --self-test`, `review_context.py --self-test`, and `forge_packet.py --self-test` exit 0" | supplied check evidence | supporting assertion | partial (directly reproduced for the changed-file subset; the remainder is an unverified claim, not structured check evidence under `check-evidence.md` — no explicit head/state/output was supplied in a reusable form) | Reproduced: `forge_packet.py --self-test` (pass), `test_forge_packet.py` (pass), `test_command_chains.py` full suite (pass, 19/19), `test_run_events.py` full suite (pass, 26/26). Not independently reproduced: `validate_review.py --self-test`, `review_context.py --self-test`, and the other 6 `test_*.py` suites (`test_check_runs.py`, `test_compose_review.py`, `test_context_fingerprint.py`, `test_deleted_file_links.py`, `test_review_context.py`, `test_thread_writes.py`), none of which cover files this diff touches. This does not affect `coverage=complete` (file coverage, not exhaustive test execution, gates that field) and settles no candidate — the claim is recorded as unverified for that remainder rather than accepted. |

No `kind=requirement` finding: every checkable claim held under inspection.

## Candidate ledger (private falsification)

One candidate was actively considered and dropped before it reached finding admission (no verification needed — it never survived primary falsification):

- **Missing direct unit test for `forge_packet.py`'s new `eligibility()`/`eligibility` subcommand.** `test_forge_packet.py` is this repository's established location for isolated, direct-subprocess unit tests of `forge_packet.py`'s other subcommands (`normalize`, `later-state`, `--self-test`), with dense edge-case coverage (malformed pages, HTTP errors, pagination gaps, etc.). The new `eligibility` code path gets no such test; its only coverage is `test_command_chains.py`'s full shell-block integration tests, which were already thorough before this move and are unchanged in scope by it (one placeholder substitution). **Dropped as a finding**: I independently ran the full `test_command_chains.py` suite and traced every branch of `eligibility()` against the old heredoc — the integration coverage already exercises every deferral reason, the eligible path, and the uncaught-exception path (including the truthy non-object `data` case the PR body calls out). There is no unverified behavior, only a style/convention gap (test *location*, not test *coverage*), which the rubric routes to `maintainability`/`consider` only when a real benefit is established, and I could not establish concrete proven consequence beyond convention. Retained as the one published **observation** instead, since it is an accurate, non-actionable fact with decisive evidence and no "should"/"must" attached to it.

No other candidate was raised. No security, authorization, data-loss, destructive-migration, released-compatibility, or concurrency/invariant surface is touched by this diff (it is a same-behavior code relocation inside an internal review-tooling skill), so:

- **Mandatory verification triggers**: none apply (no `must-fix`, no security/data-integrity/destructive-migration/compatibility/prior-must-fix candidate).
- **Safety-premise check**: not run — the change does not affect security, authorization, data integrity, a destructive migration, released compatibility, or a concurrency/failover invariant.
- **Optional scrutiny**: none added — nothing here needed a difficult cross-module reconstruction to prove or refute; direct diff comparison plus running the tests settled everything.
- **Verifier batch**: **not dispatched** — there was nothing to hand a fresh-context verifier. Allowance unspent: 1 initial + 1 follow-up available, 0 used, across this run and any continuation.

## Per-file coverage (6/6 files reviewed; matches the pinned manifest exactly)

| File | Disposition | Notes |
| --- | --- | --- |
| `CHANGELOG.md` | reviewed | New `### Changed` entry only; content verified against the actual diff and independently-recomputed byte counts. |
| `skills/review-code/DESIGN.md` | reviewed | New trailing subsection ("First-review eligibility guard moved to a script"); its `#early-first-review-context-build-issue-258` anchor link resolves to an existing heading (`## Early first-review context build (issue #258)`, line 1028); its claims cross-checked against the code diff. |
| `skills/review-code/references/pull-request-target.md` | reviewed | Full before/after read; the removed 42-line heredoc traced line-by-line against the new `eligibility()` function; surrounding shell block confirmed byte-identical apart from the one substituted call line and the added `packet=` variable. |
| `skills/review-code/scripts/forge_packet.py` | reviewed | New `Deferred` exception, `eligibility()` function, CLI subparser, and `main()` dispatch branch; docstring/Usage/Exit-codes updates cross-checked against actual behavior; ran `--self-test` and the full `test_forge_packet.py` suite. |
| `skills/review-code/scripts/test_command_chains.py` | reviewed | One-line addition (`<forge-packet-script>` placeholder substitution); ran full suite and the four `root_block`-scoped tests individually. |
| `skills/review-code/scripts/test_run_events.py` | reviewed | One-line addition (same placeholder, in the documented-command replay test); ran full suite. |

Coverage: **complete**. No file ignored, no file unreviewed, no governing diff chunk left `missing`.

## Focused checks executed (all via `run_events.py wrap`, head `0ea287f0c07fda09b9d063612353dcef37f38063`, from `skills/review-code`)

| Command | Result |
| --- | --- |
| `python3 scripts/forge_packet.py --self-test` | pass |
| `python3 scripts/test_forge_packet.py` | pass — 8 case group(s) |
| `python3 -m unittest` on the 4 `root_block`-related tests in `test_command_chains.py` | pass — 4/4 |
| `python3 scripts/test_command_chains.py` (full) | pass — 19/19 |
| `python3 scripts/test_run_events.py` (full) | pass — 26/26 |

Not run (out of scope — cover files this diff does not touch): `validate_review.py --self-test`, `review_context.py --self-test`, `test_check_runs.py`, `test_compose_review.py`, `test_context_fingerprint.py`, `test_deleted_file_links.py`, `test_review_context.py`, `test_thread_writes.py`, `test_verifier_handoff.py`.

Check evidence accounting: the packet's own "## Checks" section is a PR-body claim, not structured caller-supplied evidence per `check-evidence.md` (no per-check identity/output in reusable form) — accounted as an unverified assertion (ledger row 8), reviewer-executed for the subset above, unused/unavailable for the remainder.

## Ambiguities, unrecoverable inputs, routed items

None. The packet was complete for this run's purposes: `merged` was explicitly present (`true`), prior-state sections were present and empty (0 reviews/threads/comments), and no packet gap blocked any check above.

## Verification record

No batch dispatched (nothing required or optional to verify). Allowance: 1 initial + 1 follow-up, 0 spent, available to any continuation of this review chain.

## Artifact paths (all under the private work directory; nothing published)

- Context store: `/tmp/issue-333/cells/44b9331a/work/private/store.json`
- Composition input: `/tmp/issue-333/cells/44b9331a/work/private/composition.json`
- Validated payload: `/tmp/issue-333/cells/44b9331a/work/private/payload.json`
- Advisory batch (never posted; `review-code` never publishes and publication is separately disabled here): `/tmp/issue-333/cells/44b9331a/work/private/batch.json`
- Rendered fragments (empty — no findings/questions to render as code-span fragments): `/tmp/issue-333/cells/44b9331a/work/private/fragments.md`
- Context-fingerprint input: `/tmp/issue-333/cells/44b9331a/work/private/fingerprint_input.json`
- Run-events log: `/tmp/issue-333/cells/44b9331a/work/private/run-events.jsonl`
- Full pulled diff (context-store chunk dump, for this report's own working notes): `/tmp/issue-333/cells/44b9331a/work/private/diff_full.txt`
- This report: `/tmp/issue-333/cells/44b9331a/work/report.md`

## Run-condition disclosures

- **Offline honored.** No `git fetch`/`git pull`/`gh`/`curl`/network call was made, by me or by any sub-agent (none was spawned — no fan-out was needed since no verification batch was required). `origin` in the clone points at a local filesystem path (`/tmp/issue-333/c8.git`) and was never contacted.
- **History boundary honored.** The newest object reachable in the clone is `0ea287f0c` (confirmed via `git show-ref`, `git log --oneline`, `git branch -a`). History commands run: `git log --oneline -5`, `git branch -a`, `git status`, `git rev-parse`, `git show-ref`, `git diff` (various ref pairs, all between `main`≡merge-base and `review-head`≡head), `git show <sha>:<path>` (only for `main`/`review-head`), and `review_context.py`'s internal `git log --follow`-style per-file history (all entries returned predate or equal the pinned head — the newest listed commit for any changed file is `bf584f0`/`00ecf47`/`41fe39d`/`36c26bd`, all ancestors of `160d120`/`0ea287f`). Nothing beyond the pinned head was read or existed to read.
- **No mutation of reviewed source.** `git status` is clean in the reviewed clone. The only local-repo change I made was creating a new branch ref `main` pointing at `160d1201bed57d96de6fc8b1ae657bd098aa2de6` (== `origin/main`, the pinned merge-base) so the skill's own documented `git diff main review-head` form worked as written; this adds a ref, not a change to any tracked file, blob, or tree. Running the test suites created a `scripts/__pycache__/` directory as an incidental Python bytecode-cache side effect; I removed it immediately afterward and re-confirmed `git status` was clean.
- **Sandbox honored.** Only the supplied packet, this installed skill (`/tmp/issue-333/snapshots/44b9331a/skills/review-code`), the target clone (`/tmp/issue-333/cells/44b9331a/repo`), and this run's own private work directory were read or written. No other cell's clone, report, or payload was accessed.
- **Model/effort/tooling.** No worker was dispatched (none was required), so the "every worker uses model sonnet, high effort, run_in_background: false" instruction had no applicable dispatch this run.
