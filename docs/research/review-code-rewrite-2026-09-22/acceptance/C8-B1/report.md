# review-code — one-shot / publishable — kamui/skills#325

## 1. Run identity

| | |
| --- | --- |
| Skill root | `/tmp/issue-333/snapshots/7387c169/skills/review-code` (absolute; every script below resolves under it unless noted) |
| Repository | `https://github.com/kamui/skills` (clone: `/tmp/issue-333/cells/7387c169/repo`) |
| Target kind | pull-request, `kamui/skills#325` |
| Head | `0ea287f0c07fda09b9d063612353dcef37f38063` |
| Base ref | `main` (local `origin/main`) |
| Base SHA / merge-base | `160d1201bed57d96de6fc8b1ae657bd098aa2de6` (identical) |
| `state` / `merged` | `MERGED` / `true` |
| Reviewer identity | `kamui` — no prior review, thread, or comment from this identity in the supplied packet → first review |
| `profile` | `publishable` |
| `mode` | `one-shot` |
| Workflow | `v5b-22` (retained; unchanged by this diff) |
| Private directory / store | `/tmp/issue-333/cells/7387c169/work` / `/tmp/issue-333/cells/7387c169/work/review-context-0ea287f0c07fda09b9d063612353dcef37f38063.json` |
| `context` digest | `832509935f5049b6f9bb6992042e77615f5bf013f5d44d191b27578d56b9df4d` (`context_fingerprint.py`, no `--packet`: pr/issues supplied directly from the orchestrator's markdown packet, since it is not itself a `forge_packet.py normalize` JSON page; `--guidance-base 160d120...` let the script derive `guidance` from the base tree) |
| Phase-1 packet | `/tmp/issue-333/cells/7387c169/packet.md` (supplied; replaced the live fetch per `SKILL.md`/`pull-request-target.md` — no `gh`, no network call was made) |
| Originating issue(s) | none (`issues=none`) — PR body carries no closing reference; ledger built from PR title + body |

**History bound.** No git history beyond the pinned head was read. Commands run: `git log --oneline -5`, `git branch -a`, `git status`, `git rev-parse HEAD main`, `git rev-parse origin/main`, `git merge-base main HEAD` / `origin/main HEAD`, `git log --oneline origin/main -1`, `git show <merge-base>:<path>` for `docs/agents/issue-tracker.md`, `AGENTS.md`, `CONTEXT.md`, `docs/agents/scripts.md`, and `review_context.py`'s own bounded `history` section (ancestors of head only, printed by the tool). Nothing after `0ea287f0c` was fetched, read, or inferred.

**Sandbox.** Only the supplied packet, the pinned skill installation, this repository clone, and this work directory were read or written. No other cell, host worktree, study document, or scorecard was touched. No `gh`/`curl`/`wget`/network call was made (confirmed by the disallowed-tools list and by not invoking any).

## 2. Private record

### 2a. Issue-fit ledger (source: PR title + body; issues=none)

| # | Source coordinate | Class | Disposition | Evidence |
| - | --- | --- | --- | --- |
| 1 | `pr-body/"Conditions, deferral reasons, verdict lines, and the block's exit handling are unchanged"` | acceptance requirement | **met** | Line-by-line comparison of the removed heredoc (`pull-request-target.md` diff) against the new `eligibility()`/`Deferred`/CLI dispatch in `forge_packet.py` (diff read in full): every condition, defer reason string, and the `eligible <merge-base> <head>` / `deferred: <reason>` verdict lines are structurally identical, only the control-flow idiom changed (early-`sys.exit` → raised `Deferred` caught once). |
| 2 | `pr-body/"test_command_chains.py runs the block with the same cases and assertions, including the guard that raises on a truthy non-object data"` | supporting assertion | **met** | `test_root_block_defers_when_first_review_status_is_unproven`'s "guard exits without a verdict" subtest passes `{"data": "x"}` and asserts `deferred: eligibility guard failed with exit 1` plus `AttributeError` on stderr; suite passes at head. |
| 3 | `pr-body/"test_run_events.py binds the new placeholder in its documented-command replay"` | supporting assertion | **met** | `test_documented_wrapped_commands_run` diff adds `.replace("<forge-packet-script>", ...)`; suite passes at head. |
| 4 | `pr-body/"Workflow v5b-22 is retained. No rule changes."` | acceptance requirement | **met** | `review-record.md`'s `workflow=v5b-22` untouched by diff; no admission/verification/rendering/state rule in the changed files differs in substance from base. |
| 5 | `pr-body` table: `pull-request-target.md` 12,566 → 8,775 bytes | supporting assertion | **met** | `wc -c` at merge-base = 12566; at head = 8775. |
| 6 | `pr-body/"the always-loaded set stays at 92,272 bytes"` | supporting assertion | **met** | `wc -c SKILL.md review-rubric.md review-record.md rendering.md` sums to 92272 at both merge-base and head. |
| 7 | `pr-body` Checks: "all 10 `scripts/test_*.py` suites, `validate_review.py --self-test`, `review_context.py --self-test`, and `forge_packet.py --self-test` exit 0" | supporting assertion | **met** (partially independently reproduced — see §2c; `validate_review.py`/`review_context.py` self-tests not rerun, as neither script is touched by this diff and per `SKILL.md` step 3 their self-tests are reviewer tooling, not owed reproduction) | `ls scripts/test_*.py` → exactly 10 files. `test_forge_packet.py`, `test_command_chains.py`, `test_run_events.py`, `forge_packet.py --self-test` independently rerun at head 0ea287f — all exit 0. |

No `not-verifiable` rows; no material question raised (repository workflow, per `docs/agents/issue-tracker.md`, does not require every PR to link an issue — no `issue-required` question).

### 2b. Candidate ledger

| id | kind | disposition | attackable | evidence |
| --- | --- | --- | --- | --- |
| `review-code/forge-packet-eligibility-exit-codes` | maintainability | **survivor** (P3, consider) | no (kind excluded; no verifier ran; falsification does not rest on a safety premise) | `scripts/forge_packet.py:1039` (`pr = ((page.get("data") or {}).get("repository") or {}).get("pullRequest")`) can raise an uncaught `AttributeError` on an unrecognized page shape, exiting 1 via Python's default handler; the `Exit codes:` table at lines 94–100 documents exit 1 only for `--self-test`/`later-state` and exit 2 only for `normalize`'s handled-shape `PageError` path, so `eligibility`'s own crash exit is undocumented, unlike `normalize`'s identical "matches no documented shape" case, which is cleanly routed to exit 2. Genuinely introduced by this diff: this code (and therefore its exit-code contract under `docs/agents/scripts.md`) did not exist under `scripts/` before — it lived in a reference-doc heredoc, outside that convention's scope. |
| (dropped) DESIGN.md "Early first-review context build (issue #258)" section still describes the guard as "a standard-library Python predicate inside the documented block" | maintainability | dropped (observation, consequence absent) | n/a | `DESIGN.md:1028-1065` is unchanged by this diff and is not rewritten to reflect the move. Dropped: `DESIGN.md` is a journal of dated/issue-numbered design decisions — later sections (e.g. "Attackable rows narrow the clean-verdict batch") consistently supersede earlier ones without rewriting them, and the new section (`DESIGN.md:1136-1138`) explicitly cross-links the old one (`#early-first-review-context-build-issue-258`, verified to resolve). Matches the file's own established convention; no reader is misled given the two are read together via the link. |
| (dropped) `eligibility()` has no direct unit/self-test entry in `test_forge_packet.py` or `forge_packet.py --self-test` | maintainability | dropped (observation, consequence absent) | n/a | No coverage regression: the old heredoc was likewise only testable end-to-end via `test_command_chains.py`'s shell-level `root_block` harness (it was never a standalone Python callable before this diff), and this diff preserves that exact test venue and case set (7 deferral reasons, success, crash, query/build failure). |
| (dropped) `eligibility_parser.add_argument("--reviewer", required=True)` combined with an intentionally empty-string value | — | dropped (no defect) | n/a | Confirmed intended and covered: `test_root_block_defers_when_first_review_status_is_unproven`'s "posting identity unknown" subtest passes `reviewer=""` and asserts the correct defer. |

**Risk-led discovery reads** (SKILL.md/rubric): `docs/agents/scripts.md` (script conventions — governs the finding above), `AGENTS.md` and `CONTEXT.md` at merge-base (no bearing beyond scripts.md; no issue involved), `docs/agents/issue-tracker.md` at merge-base (no hard issue-linking requirement found), a repository-wide case-insensitive grep for `42-line`, `forge-packet-script`, and `eligibility` (no other stale reference to the old heredoc found; all other `eligibility` hits are unrelated docs/research or other skills' own "eligibility" vocabulary).

### 2c. File accounting (complete merge-base diff; 11/11 chunks consumed)

| File | State | Notes |
| --- | --- | --- |
| `CHANGELOG.md` | reviewed | +2/-0; new bullet cross-checked against the actual diff and byte counts |
| `skills/review-code/DESIGN.md` | reviewed | +8/-0; new section cross-checked for anchor validity and journal-convention consistency |
| `skills/review-code/references/pull-request-target.md` | reviewed | +3/-46; new prose and shell-block line diffed against removed heredoc |
| `skills/review-code/scripts/forge_packet.py` | reviewed | +104/-3; new `Deferred`/`eligibility()`/CLI dispatch compared condition-by-condition to the removed heredoc; whole-file read of surrounding `self_test()` and CLI (unchanged) to confirm no other coupling |
| `skills/review-code/scripts/test_command_chains.py` | reviewed | +1/-0 (placeholder binding); full affected test class read; suite run |
| `skills/review-code/scripts/test_run_events.py` | reviewed | +1/-0 (placeholder binding); full affected test class read; suite run |

No file ignored, none unreviewed.

### 2d. Check accounting

Reviewer-executed at head `0ea287f0c07fda09b9d063612353dcef37f38063`, from `skills/review-code` (wrapped via the skill root's `scripts/run_events.py` into this run's `run-events.jsonl`):

- `python3 scripts/test_forge_packet.py` — exit 0 (8 case groups passed)
- `python3 scripts/test_command_chains.py` — exit 0 (19 tests)
- `python3 scripts/test_run_events.py` — exit 0 (26 tests)
- `python3 scripts/forge_packet.py --self-test` — exit 0

No caller-supplied check evidence was provided to accept or retain. `validate_review.py --self-test` and `review_context.py --self-test` (named in the PR body's Checks section) were not independently rerun: neither script is touched by this diff, so under `SKILL.md` step 3 they are reviewer tooling, not owed reproduction; the PR body's claim about them is read as a supporting assertion and disposed on rather than repeated.

### 2e. Verification accounting

Zero material survivors (the one survivor is `kind=maintainability`, `action=consider` — not material) and zero attackable ledger rows (no row of a non-excluded kind, no verifier refutation, no acquittal resting on a safety premise). Per `SKILL.md` step 3's batch-requirement rule, **no clean-verdict batch was required or dispatched**: `clean_verdict: not-required`. Batches used: 0 initial, 0 follow-up (well within the one-initial-plus-one-follow-up cap).

### 2f. Recorded deferrals, prior items

None (first review; no recorded deferrals in the pull-request body).

## 3. Semantic status and coverage

- **Status: Approved** (advisory — merged target, publication disabled). No unsettled `must-fix`; no open question; coverage complete.
- **Coverage: complete.** Every changed file reviewed; both risk-directed checks (script-convention compliance, byte-count claims) have evidence-backed outcomes; all four selected focused checks ran and passed; no packet gap (packet reported no incomplete connections); no unrecoverable input.

## 4. Artifacts (this run)

| Artifact | Path |
| --- | --- |
| Review-context store | `/tmp/issue-333/cells/7387c169/work/review-context-0ea287f0c07fda09b9d063612353dcef37f38063.json` |
| Context-build stdout/stderr | `/tmp/issue-333/cells/7387c169/work/context-build.out`, `.err` |
| Diff chunks read back from store | `/tmp/issue-333/cells/7387c169/work/chunks/*.txt` |
| Context-fingerprint input | `/tmp/issue-333/cells/7387c169/work/context-input.json` |
| Composition input | `/tmp/issue-333/cells/7387c169/work/composition.json` |
| Validated payload | `/tmp/issue-333/cells/7387c169/work/payload.json` |
| Forge batch (unpublished) | `/tmp/issue-333/cells/7387c169/work/batch.json` |
| Rendered fragments | `/tmp/issue-333/cells/7387c169/work/fragments.md` |
| This report | `/tmp/issue-333/cells/7387c169/work/report.md` |

All produced by `python3 /tmp/issue-333/snapshots/7387c169/skills/review-code/scripts/finalize_review.py --store <store> /tmp/issue-333/cells/7387c169/work` (exit 0, one call, `--profile publishable`), following `python3 .../scripts/review_context.py` (step 2 build) and `python3 .../scripts/context_fingerprint.py` (context digest). No payload, batch, or link was assembled by hand.

## 5. The complete would-be review (exactly as it would be posted)

> **Approved (advisory)** — 1 consider finding.
>
> **Mode:** Retrospective review of merged pull request; publication disabled.
>
> **Intent:** Move the pull-request root invocation's first-review eligibility guard out of a 42-line Python heredoc in `references/pull-request-target.md` and into a new `scripts/forge_packet.py eligibility` subcommand, called through an absolute path like the block's other scripts, preserving every condition, deferral reason, verdict line, and exit-handling behavior unchanged.
>
> **Issue fit:** No originating issue; the pull request carries no closing reference. Built from the pull-request title and body (issues=none). The promise that conditions, deferral reasons, verdict lines, and exit handling are unchanged is met: verified line-for-line against the removed heredoc and the new `eligibility` function, and confirmed by running `test_command_chains.py`, `test_run_events.py`, `test_forge_packet.py`, and `forge_packet.py --self-test` at the reviewed head, all passing. The byte-count claims (`pull-request-target.md` 12,566 to 8,775 bytes; always-loaded set unchanged at 92,272 bytes) are met, verified directly with `wc -c` against the base and head trees. The "10 `scripts/test_*.py` suites" claim is met (10 files present).
>
> **Coverage:** Complete merge-base diff reviewed across all 6 changed files (CHANGELOG.md, DESIGN.md, references/pull-request-target.md, scripts/forge_packet.py, scripts/test_command_chains.py, scripts/test_run_events.py). Focused checks run at the reviewed head from `skills/review-code`: `python3 scripts/test_forge_packet.py`, `python3 scripts/test_command_chains.py`, `python3 scripts/test_run_events.py`, and `python3 scripts/forge_packet.py --self-test`, all exit 0.
>
> **Reviewed:** `0ea287f` against merge-base `160d120`.
>
> ## Findings
>
> **[P3] [consider] Document eligibility's exit code on an unrecognized page shape** — anchor [`skills/review-code/scripts/forge_packet.py:94-100`](https://github.com/kamui/skills/blob/0ea287f0c07fda09b9d063612353dcef37f38063/skills/review-code/scripts/forge_packet.py?plain=1#L94-L100)
>
> **Triggers when:** `forge_packet.py eligibility` reads a saved root page whose shape it cannot interpret, such as `{"data": "x"}` (a truthy non-object `data`).
>
> **Impact:** `pr = ((page.get("data") or {}).get("repository") or {}).get("pullRequest")` raises an uncaught `AttributeError` and the process exits 1 with a bare traceback, but the module's `Exit codes:` table attributes exit 1 only to a `--self-test` failure or `later-state` output and exit 2 only to `normalize`'s handled unrecognized-shape case, so a reader has no accurate account of `eligibility`'s own unhandled-shape exit code.
>
> **Change:** Add a line to the `Exit codes:` table (or the `eligibility` section above it) stating that `eligibility` also exits non-zero via an uncaught exception, distinct from the documented `1`/`2` cases, when it cannot interpret the page's shape.
>
> **Source:** docs/agents/scripts.md, `Each script` exit-code convention.
>
> Closing this without action is a correct response.
>
> <sub>`<!-- finding id=review-code/forge-packet-eligibility-exit-codes head=0ea287f0c07fda09b9d063612353dcef37f38063 priority=P3 action=consider blocking=false kind=maintainability -->`</sub>
>
> <sub>`<!-- review-run head=0ea287f0c07fda09b9d063612353dcef37f38063 base-ref=main base-sha=160d1201bed57d96de6fc8b1ae657bd098aa2de6 merge-base=160d1201bed57d96de6fc8b1ae657bd098aa2de6 workflow=v5b-22 context=832509935f5049b6f9bb6992042e77615f5bf013f5d44d191b27578d56b9df4d issues=none coverage=complete -->`</sub>

No open questions, no observations, no ambiguities, no disputed or prior items.

## 6. Routed items

None. No ambiguity required dual-reading, no input was unrecoverable, and no material question was left open — the single supported deferral-free ledger and the single low-priority `consider` finding above are the review's complete output. `merged` was supplied by the packet (`true`), so no unrecoverable-input route applied for that field.

## 7. Compliance notes for this invocation

- Model/effort: this session ran as the primary at `claude-sonnet-5`/high effort per the invocation; **no verification worker was dispatched**, because `SKILL.md` step 3's batch-requirement rule (no material survivor and no attackable ledger row) makes a clean-verdict batch explicitly *not required* — this was computed, not assumed, and is recorded in §2e.
- Batch allowance: 0 of the permitted 1-initial-plus-1-follow-up used.
- No network access, live forge command, publication action, or mutation of reviewed source occurred. All four focused-test invocations ran the target clone's own checked-out scripts (`skills/review-code/scripts/*.py` inside `/tmp/issue-333/cells/7387c169/repo`), writing only to Python's own temp directories and this work directory.
- Coverage is honestly complete; nothing is reported as finished that was not verified.
