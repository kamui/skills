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

- Re-fetch the head immediately before writing; a stale or unreadable head aborts all publication. The freshness-and-submission block below makes that a preflight failure with exit 3.
- Keep retrospective review of a merged pull request non-publishing unless the caller separately and explicitly authorized publication to that merged target.
- Submit one review body and all new line comments in one forge-native review call. Include file-level comments there only when that batch endpoint documents file subjects; otherwise move their complete prose into the body before the call.
- A general comment is a fallback only when a non-gating native review is unavailable or refused.
- Re-read the target after an ambiguous write result before one retry.
- Store the run trailer in the summary and finding/question trailers in raw comment bodies.

- On a conclusive malformed-comment rejection, apply `review-code`'s render-and-validate step to the repaired record, confirm no review exists, and retry once.

## Timing events

Run every forge fetch and write this skill makes through the `run_events.py` path the review record carries: `python3 <recorded-absolute-run_events.py-path> wrap --private-dir <private-dir> --event <event> --data role=<role> [--data connection=root] -- <command>`, where `<private-dir>` is the directory of the record's private store. Wrap each command of a chain separately so no fetch or write escapes, and keep stdout redirects outside the wrapper. A record without that path runs the same commands unwrapped.

| Command | Event and data |
| --- | --- |
| Head re-fetch before writing, re-read after an ambiguous result, thread re-read, published-review readback | `forge-fetched`, `role=root`, `connection=root` |
| Review submission | `forge-written`, `role=review` |
| Each thread reply | `forge-written`, `role=replies` |
| Each thread resolution | `forge-written`, `role=resolutions` |
| General-comment fallback | `forge-written`, `role=summary` |

The wrapper exits with the command's status; exit 2 with a `run_events:` line on stderr means it could not run the command, which counts as that fetch or write failing. These events time commands only. A successful wrapped write is not evidence that publication finished; the readback and failure reporting below still decide that.

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

GitHub's separate review-comment endpoint documents `subject_type: "file"`, but using it would break this workflow's atomic one-review publication invariant. Use the equivalent forge-native operation elsewhere.

### Freshness and review submission

Run the head re-fetch, the equality check, and the single review POST as one shell invocation. `<reviewed head>` is the record's full head SHA, `<private-dir>` holds the record's `batch.json` as `--emit-batch` printed it, and `ev` is empty when the record carries no `run_events.py` path:

```sh
d=<private-dir> ev=<recorded-absolute-run_events.py-path> pr=<pr> reviewed=<reviewed head>
rm -f "$d/head.txt" "$d/review-response.json"
forge() { # <forge-fetched|forge-written> <command...>
  kind=$1; shift
  if [ -z "$ev" ]; then "$@"
  elif [ "$kind" = forge-fetched ]; then python3 "$ev" wrap --private-dir "$d" --event forge-fetched --data role=root --data connection=root -- "$@"
  else python3 "$ev" wrap --private-dir "$d" --event forge-written --data role=review -- "$@"; fi
}
forge forge-fetched gh api "repos/{owner}/{repo}/pulls/$pr" --jq .head.sha > "$d/head.part" 2> "$d/head.stderr"
rc=$?
live=$(cat "$d/head.part")
batch_head=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["commit_id"])' "$d/batch.json" 2> /dev/null)
case $live in
  *[!0-9a-f]*|"") shape=bad ;;
  *) if [ "${#live}" -eq 40 ]; then shape=ok; else shape=bad; fi ;;
esac
if [ "$rc" -ne 0 ]; then reason="head fetch exited $rc"
elif [ "$shape" != ok ]; then reason="head fetch returned an empty or malformed head"
elif [ "$batch_head" != "$reviewed" ]; then reason="batch.json commit_id is not the reviewed head"
elif [ "$live" != "$reviewed" ]; then reason="live head $live is not the reviewed head $reviewed"
else reason=; fi
if [ -n "$reason" ]; then
  echo "preflight failed: $reason; nothing was written"; cat "$d/head.part" "$d/head.stderr"; exit 3
fi
mv "$d/head.part" "$d/head.txt"
echo "preflight passed: live head $live"
forge forge-written gh api --method POST "repos/{owner}/{repo}/pulls/$pr/reviews" --input "$d/batch.json" > "$d/review-response.json" 2> "$d/review-response.stderr"
rc=$?
if [ "$rc" -ne 0 ]; then
  echo "write attempted: review POST exited $rc; re-read the pull request's reviews before one retry"
  cat "$d/review-response.json" "$d/review-response.stderr"; exit "$rc"
fi
echo "review POST exited 0"; cat "$d/review-response.json"
```

A `preflight failed` line with exit 3 is the freshness route: a failed, empty, malformed, or mismatched head, or a batch whose `commit_id` is not the reviewed head, publishes nothing, no POST runs, and the stale or unreadable head is reported. A `write attempted` line means the POST ran and exits with its own status, whatever that number is; exit 3 after that line is a write failure, never a preflight failure. The block posts the batch unchanged, reviewed `commit_id` included; it checks the head just before the write and is not an atomic compare-and-swap against a concurrent push. The malformed-comment rejection, ambiguous-write reconciliation, one-retry, gating, and retrospective rules above and below still govern what follows each outcome.

## Authorized gating emission

`review-code` returns the advisory `COMMENT` batch. For a separately authorized gating event, run `python3 <recorded-absolute-validate_review.py-path> --emit-batch --event <REQUEST_CHANGES|APPROVE> < payload.json > batch.json`. Never edit the batch by hand. A non-zero exit stops publication: report the script's output.

On this gating path only, the script enforces the first-line grammar `**<Status>[ (advisory)]** — …`: the input advisory suffix is present exactly for `Changes Requested` or `Approved` under `COMMENT`. `APPROVE` requires `Approved`, and `REQUEST_CHANGES` requires `Changes Requested`; a mismatch exits 1. It removes the suffix and re-validates the edited body before printing. The batch is what validated after that one scripted edit. The ordinary `COMMENT` path retains its existing acceptance rules. Report the posted form from `batch.json`, not the advisory form in `payload.json`.

## Existing-thread replies and resolution

Post each drafted reply to its recorded comment id with `python3 <recorded-absolute-run_events.py-path> wrap --private-dir <private-dir> --event forge-written --data role=replies -- gh api --method POST repos/{owner}/{repo}/pulls/<pr>/comments/<id>/replies -f body='<drafted reply>'`. Use the equivalent structured body input when quoting needs it. Preserve the draft's stable id and disposition; do not create a new finding for a surviving prior item. Re-read the thread after an ambiguous result before one retry. Report any reply that failed.

For every prior item `review-code` classified `fixed`, `accepted`, or `obsolete`, resolve its existing thread. If the item has a drafted reply, post it successfully before resolving; if it has no drafted reply, resolve directly. Use the returned thread node id, not the numeric comment id. Skip threads already resolved; leave `still-open`, `not-verifiable`, and disputed items open. An author's `declined` reply alone does not qualify: `review-code`'s evidence-backed classification governs the action. A prior item without a forge thread has no thread to resolve.

On GitHub, run:

```sh
python3 <recorded-absolute-run_events.py-path> wrap --private-dir <private-dir> --event forge-written --data role=resolutions -- \
gh api graphql -f query='mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread{ isResolved } } }' -f id=<thread-node-id>
```

Confirm `isResolved: true`. If the result is ambiguous, re-read that thread's state before one retry; if resolution is refused or still fails, report the thread as unresolved rather than claiming it closed. Resolve nothing whose drafted reply failed to post. Non-publishing retrospective runs perform neither replies nor resolutions.
