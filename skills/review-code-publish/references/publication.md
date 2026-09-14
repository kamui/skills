# Publication

## Events

Authorization changes only the forge event, never the semantic status:

| Status | Authorized gating event | Default event |
| --- | --- | --- |
| Changes Requested | `REQUEST_CHANGES` | `COMMENT` |
| Incomplete | none | `COMMENT` |
| Needs Information | none | `COMMENT` |
| Approved | `APPROVE` | `COMMENT` |

## Publication invariants

- Re-fetch the head immediately before writing; a stale or unreadable head aborts all publication.
- Keep retrospective review of a merged pull request non-publishing unless the caller separately and explicitly authorized publication to that merged target.
- Submit one review body and all new line comments in one forge-native review call. Include file-level comments there only when that batch endpoint documents file subjects; otherwise move their complete prose into the body before the call.
- A general comment is a fallback only when a non-gating native review is unavailable or refused.
- Re-read the target after an ambiguous write result before one retry.
- Store the run trailer in the summary and finding/question trailers in raw comment bodies.

- On a conclusive malformed-comment rejection, apply `review-code`'s render-and-validate step to the repaired record, confirm no review exists, and retry once.

On GitHub, the `Create a review for a pull request` batch documents line comments but not file subjects. Keep file-anchored findings in `Unanchored findings` rather than making a separate write through the review-comment endpoint or inventing an unrelated line. The one-call batch shape is:

```json
{
  "commit_id": "<reviewed head>",
  "event": "COMMENT",
  "body": "<summary>",
  "comments": [
    {
      "path": "src/payments.ts",
      "line": 42,
      "side": "RIGHT",
      "body": "<finding>"
    }
  ]
}
```

Post it with `gh api --method POST repos/{owner}/{repo}/pulls/<pr>/reviews --input batch.json` as `--emit-batch` printed it. GitHub's separate review-comment endpoint documents `subject_type: "file"`, but using it would break this workflow's atomic one-review publication invariant. Use the equivalent forge-native operation elsewhere.

## Authorized gating emission

`review-code` returns the advisory `COMMENT` batch. For a separately authorized gating event, run `python3 <recorded-absolute-validate_review.py-path> --emit-batch --event <REQUEST_CHANGES|APPROVE> < payload.json > batch.json`. Never edit the batch by hand. A non-zero exit stops publication: report the script's output.

On this gating path only, the script enforces the first-line grammar `**<Status>[ (advisory)]** — …`: the input advisory suffix is present exactly for `Changes Requested` or `Approved` under `COMMENT`. `APPROVE` requires `Approved`, and `REQUEST_CHANGES` requires `Changes Requested`; a mismatch exits 1. It removes the suffix and re-validates the edited body before printing. The batch is what validated after that one scripted edit. The ordinary `COMMENT` path retains its existing acceptance rules. Report the posted form from `batch.json`, not the advisory form in `payload.json`.

## Existing-thread replies and resolution

Post each drafted reply to its recorded comment id with `gh api --method POST repos/{owner}/{repo}/pulls/<pr>/comments/<id>/replies -f body='<drafted reply>'`. Use the equivalent structured body input when quoting needs it. Preserve the draft's stable id and disposition; do not create a new finding for a surviving prior item. Re-read the thread after an ambiguous result before one retry. Report any reply that failed.

For every prior item `review-code` classified `fixed`, `accepted`, or `obsolete`, resolve its existing thread. If the item has a drafted reply, post it successfully before resolving; if it has no drafted reply, resolve directly. Use the returned thread node id, not the numeric comment id. Skip threads already resolved; leave `still-open`, `not-verifiable`, and disputed items open. An author's `declined` reply alone does not qualify: `review-code`'s evidence-backed classification governs the action. A prior item without a forge thread has no thread to resolve.

On GitHub, run:

```sh
gh api graphql -f query='mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -f id=<thread-node-id>
```

Confirm `isResolved: true`. If the result is ambiguous, re-read that thread's state before one retry; if resolution is refused or still fails, report the thread as unresolved rather than claiming it closed. Resolve nothing whose drafted reply failed to post. Non-publishing retrospective runs perform neither replies nor resolutions.
