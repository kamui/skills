---
name: code-review-publish
description: "Invoke code-review-inspect and publish one forge-native review of an existing pull request. Use when the caller wants a review posted to the pull request, not just reported back."
---

# Publish code review

## Boundaries

Invoking this skill authorizes publishing a review to the resolved pull request.
Retrospective review of a merged pull request is non-publishing unless separately authorized.
This does not authorize changing code, editing the pull request or issue, adding labels, or merging.
Use a gating event only when the user or repository workflow separately authorizes this identity to gate the merge.
A self-review always uses `COMMENT`.

This workflow is one-shot: finish without pausing for reviewer preferences.
If `code-review-inspect` is not among the installed skills, stop with `missing-dependency: code-review-inspect`.

## Inspect

Invoke `code-review-inspect` with the target, any user-supplied issues or spec, any merged-target publication authorization, and the duplicate-review shortcut on.
Pass through supplied phase-1 packets, posting identity, focused-test policy, and up-front inputs under its Caller contract when provided.
Apply the one-shot column of inspect's Return routing table.
A named stop ends this run with its report; a completed record supplies everything needed below.
For a merged target without separate publication authorization, report the complete would-be review and finish.

## Publish

Read [`references/publication.md`](references/publication.md) now and follow its invariants, event table, batch shape, and reply operation.
Use the returned `batch.json` for the common `COMMENT` path.
For authorized gating, regenerate it with `--emit-batch --event` through the absolute validator path recorded by inspect; the script owns the suffix change.
Never edit the batch by hand or locate scripts through a sibling-relative path.

Re-fetch the pull-request head immediately before the first write.
If it differs from the reviewed head or cannot be read, publish nothing and report the stale review.
Post the batch in one forge-native review call, then post each drafted reply on its existing thread through the reference's reply verb.

For a conclusive malformed-comment rejection, apply inspect's render-and-validate step to the repaired record using its recorded absolute script paths.
If compaction dropped the rendering instructions, re-read `references/rendering.md` from the inspect skill root those paths identify.
Confirm no review exists before the single retry, as publication.md specifies.
Use a general comment only for the reference's documented fallback; re-read after an ambiguous write before one retry.

## Report

Read the published review back.
Report the posted status, reviewed head, coverage, review URL, finding URLs, open questions, disputed findings, and anything that failed to publish.
Use the posted form from `batch.json` after gating emission, not the advisory `payload.json` body.
Every file coordinate is the same script-rendered commit-pinned link the summary carries.
On a non-publishing retrospective run, report the complete would-be review in place of the review URL.
