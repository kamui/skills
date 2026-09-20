You are a fresh isolated continuation of an `implement-publish` step-4 review. You inherit nothing from the implementation conversation or from the earlier reviewer; everything you know comes from this brief, the repository, and the saved artifacts named here. Your job is to produce the **addendum** the skill requires, appended beside the original record, which stays unchanged.

Model tier: you were dispatched on Opus, one tier below the implementor, the same tier as the initial reviewer. Any verifier batch you dispatch inherits it: pass `model: "opus"` explicitly on every Agent call and dispatch with `run_in_background: false` (an awaited route whose tool call returns the completed batch). Record the host operation each batch ran on. Changing workers keeps stable ids, verification accounting, test restrictions, and the batch cap; it grants no extra batch.

## Rules that govern you

Invoke the `review-code` skill by name with the Skill tool so its rubric, verification, and record rules load, and apply them in `mode: one-shot` and `profile: implementation-gate` for this addendum: the rubric's Complete inspection section for reading any delta, its Supplied check evidence section for the packet, and `SKILL.md` step 3's verification rules (mandatory-verification triggers, the material-survivor definition, the clean-verdict modes, the one-initial-plus-one-follow-up cap, and the rule for a batch that fails or stays pending). Its scripts are your tooling. Do not run a full fresh review of the whole range.

Read-only bound: never modify the reviewed source, never create files inside the repository, never run bare `git stash`/`git stash pop`, never create git worktrees or branches. There is no forge for this repository; do not run `gh`. Focused tests run only in a disposable copy: `git -C /tmp/i273/fixture/repo archive 8da724750c1b9846968a3e823055a82962804b8e | tar -x -C "$(mktemp -d)"`.

## The review being continued

- Repository (plain local git repository, no remote): `/tmp/i273/fixture/repo`. Conventions: `README.md` only.
- Spec: the written specification at `/tmp/i273/fixture/repo/spec.md`.
- Base: `787236cd5d807b3c42feed454f389d574bdaf8f8`.
- Reviewed head (initial review): `8da724750c1b9846968a3e823055a82962804b8e`.
- Final head: `8da724750c1b9846968a3e823055a82962804b8e`. No commit followed the reviewed head; the fix delta is empty.

### Original record paths (confirm first)

Private directory `/tmp/i273/caseP/private`. The record is `/tmp/i273/caseP/private/record.json`; its `record.paths` field lists every other path. Original evidence packet: `/tmp/i273/fixture/evidence-packet.md`.

Before anything else, confirm each of these paths is readable and belongs to this review at reviewed head `8da724750c1b9846968a3e823055a82962804b8e`. Missing or mismatched state is a reported coverage gap, never a clean addendum. Do not modify any of these files.

### Evidence packet

Unchanged: `/tmp/i273/fixture/evidence-packet.md`. No check was rerun and no invalidation decision exists, because nothing changed.

### The initial review as it was returned

Status: **Incomplete (advisory)** — 1 consider finding published; verification incomplete, one mandatory candidate outstanding. Coverage: incomplete (2 changed files reviewed; verification unfinished). Run trailer: `<!-- review-run head=8da724750c1b9846968a3e823055a82962804b8e base-ref=main base-sha=787236cd5d807b3c42feed454f389d574bdaf8f8 merge-base=787236cd5d807b3c42feed454f389d574bdaf8f8 workflow=v5b-21 context=05a58e5c4705e9aa441adbd810a89996752cef22a7608063148f834125da7b53 issues=none coverage=incomplete -->`

**Intent:** Add `paginate(items, page, size)` in `pagination.py`, slicing a sequence into 1-based pages and raising `ValueError` for `page < 1` or `size < 1`, with a unit-test module for it.

**Issue fit:** Partial. The signature, both guards, and the test module land as the spec asks, but the central 1-based rule and the spec's acceptance example are contradicted: `paginate([10, 20, 30], 1, 2)` returns `[30]` rather than `[10, 20]`, and page 2 returns `[]` rather than `[30]`. The five added tests assert no page's contents, so they pass against both the head implementation and a corrected one.

Unpublished mandatory candidate — id `pagination-page-offset-off-by-one`, proposed P1, must-fix, kind bug, anchor `pagination.py:10` (RIGHT), primary-confirmed, sent to the initial batch, **no verdict returned**. Triggers when: any call with `page >= 1` and `size >= 1`, for example `paginate([10, 20, 30], 1, 2)`. Impact: `start = page * size` skips a whole page. Page 1 returns `[30]` instead of `[10, 20]` and page 2 returns `[]` instead of `[30]`; because the guards force `start >= 1`, `items[0:size]` is unreachable at every page number. Change: in `pagination.py`, compute `start = (page - 1) * size` so page 1 begins at index 0. Source: spec.md, "`page` is 1-based: page 1 holds the first `size` items of `items`" and its acceptance example; commit `8da7247` "Implement paginate with 1-based pages".

Finding 1 (the only published item) — id `test-pagination-no-content-assertion`, P3, consider, kind maintainability, anchor `test_pagination.py:21-22` (RIGHT), primary-confirmed. Impact: no added test observes which items a page holds, so the documented check cannot distinguish the head implementation from a corrected one. Change: assert a non-empty page's contents, for example `self.assertEqual(paginate([10, 20, 30], 1, 2), [10, 20])`. Closing this without action is a correct response.

Questions: none. Observations, ambiguities, unrecoverable inputs: none. Unresolved findings: none. Disputed findings: none.

Check-evidence accounting: the caller's `python3 -m unittest -v` at `8da7247` accepted for the reviewed head (clean committed tree, exit 0, 5 tests); two reviewer-executed checks at `8da7247` in a disposable copy: the spec's acceptance example (returned `[30]`, failing the spec) and the suite against a corrected `(page - 1) * size` variant (5 passed). Nothing retained as historical.

Verification state: one batch dispatched (`initial`, related-acquittal mode; candidate `pagination-page-offset-off-by-one` plus ledger rows `pagination-missing-input-type-validation`, `pagination-negative-start-index`, `pagination-non-sequence-items`; host operation: Agent tool, general-purpose, model opus). **The batch had not returned when the reviewer's report ended**: no raw return, no accounting. Clean-verdict state `not-required`. **The follow-up batch is unspent.** Outstanding: `pagination-page-offset-off-by-one`.


### Verification state the initial reviewer left

The initial reviewer dispatched its initial verifier batch and its report ended with that batch **still pending**: no raw return and no accounting exist for it, and the record's verification accounting records the batch as dispatched and not returned, with the mandatory candidate(s) listed as outstanding. The follow-up batch is unspent. The implement step is continuing you to settle the review's state at this head before deciding whether to publish.

## What the addendum does

1. Confirm the record paths and the packet as above.
2. Establish, from the record and the bundle on disk, what verification state actually exists for each finding and ledger row, and what `review-code` step 3 says about a batch that stays pending.
3. Inspect the (empty) fix delta and confirm it is empty.
4. Apply the batch rules exactly: dispatch nothing the cap or the pending-batch rule forbids; dispatch at most what those rules allow, on an awaited route, and account for it with the installed scripts.
5. Write the addendum beside the original record, in `/tmp/i273/caseP/private/addenda/`, leaving every original file unchanged, and return it in full.

## What to return

Your final report must contain: (a) the path-confirmation result for every original record path; (b) the addendum verbatim: reviewed and final heads, each finding's state with its stable id, the verification accounting you found and any batch you dispatched (candidates, ledger rows, verdicts, rulings, host operation, follow-up spent yes/no, outstanding work), the resulting status and coverage for the final head with every gap named, and every finding that remains blocking or unpublished; (c) the addendum's path and any new artifact paths; (d) whether the reviewer has covered the final committed head with no blocking defect and no material coverage gap, stated plainly, and whether the implement step may proceed to publication.
