---
name: review-code-publish
description: "Invoke review-code and publish one forge-native review of an existing pull request. Use when the caller wants a review posted to the pull request, not just reported back."
---

# Publish code review

## Boundaries

Invoking this skill authorizes publishing a review to the resolved pull request.
Retrospective review of a merged pull request is non-publishing unless separately authorized.
This does not authorize changing code, editing the pull request or issue, adding labels, or merging.
Use a gating event only when the user or repository workflow separately authorizes this identity to gate the merge.
A caller that resolved a reviewing app distinct from the pull request's author carries an explicit gating authorization in its packet, and that authorization is what permits a gating event here; a review published under a reviewing app is not a self-review.
A self-review always uses `COMMENT`.

This workflow is one-shot: finish without pausing for reviewer preferences.
If `review-code` is not among the installed skills, stop with `missing-dependency: review-code`.

## Inspect

Invoke `review-code` with `mode: one-shot`, the explicit pull-request target (coordinate, URL, or current branch's open pull request), any user-supplied issues or spec, any merged-target publication authorization, and the duplicate-review shortcut on.
Pass through supplied phase-1 packets, reviewer identity, review-token command, focused-test policy, and up-front inputs under its Caller contract when provided.
With no supplied reviewer identity, resolve it as `references/publication.md` specifies before the review runs, so an unusable reviewing app falls back to the authenticated user before any work is spent.
Apply the one-shot column of `review-code`'s Return routing table.
A named stop ends this run with its report; a completed record supplies everything needed below.
For a merged target without separate publication authorization, report the complete would-be review and finish.

## Publish

Read [`references/publication.md`](references/publication.md) now and follow its invariants, event table, batch shape, and thread operations.
Use the returned `batch.json` for the common `COMMENT` path.
An `issue-required` routed item appears as a `[Question]` in the review body; `Issue fit` states that the ledger came from the pull-request text. With otherwise complete coverage and no unsettled must-fix finding, the status is `Needs Information`, never `Incomplete` for this reason alone.
For authorized gating, regenerate it with `--emit-batch --event` through the absolute validator path recorded by `review-code`; the script owns the suffix change.
Never locate scripts through a sibling-relative path.

Re-fetch the pull-request head, check it, and post the batch in one forge-native review call with the reference's freshness-and-submission block, one shell invocation.
Exit 3 means nothing was written on that block's `preflight failed` route and on the thread write loop's pre-write exits: report what it printed — a stale or unreadable head, a review-token command that yielded no usable token, or a refused `writes.jsonl` — and stop.
An exit 3 the block prints after its `write attempted` line is a failed review POST, not a preflight failure, and takes the repair, retry, and fallback rules below instead.
Run that fetch, every write, and the readback below through the recorded `run_events.py` wrapper as the reference's Timing events section classifies them.
After the review posts, write `writes.jsonl` for every prior item and run the reference's thread write loop once for its replies and thread resolutions, wrapped as one `role=replies` event.

On a malformed-comment rejection, an ambiguous write, or a refused review, follow the reference's repair, retry, and fallback rules, using `review-code`'s recorded absolute script paths; if compaction dropped the rendering instructions, re-read `references/rendering.md` from the skill root those paths identify.

## Report

Read the published review back.
Report the posted status, reviewed head, coverage, review URL, finding URLs, open questions, disputed findings, and anything that failed to publish.
Use the posted form from `batch.json` after gating emission, not the advisory `payload.json` body.
Every file coordinate is the same script-rendered commit-pinned link the summary carries.
On a non-publishing retrospective run, report the complete would-be review in place of the review URL.
