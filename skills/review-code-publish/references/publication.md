# Publication

## Events

Authorization changes only the forge event, never the semantic status:

| Status | Authorized gating event | Default event |
| --- | --- | --- |
| Changes Requested | `REQUEST_CHANGES` | `COMMENT` |
| Incomplete | none | `COMMENT` |
| Needs Information | none | `COMMENT` |
| Approved | `APPROVE` | `COMMENT` |

## Reviewer identity

The **reviewer identity** is the login this review publishes as. It is the forge CLI's authenticated user unless the caller supplied one, or `docs/agents/issue-tracker.md` names a reviewing app; that file also gives the **review-token command**, a shell command that prints a short-lived token for the app (for example `<runner> token <owner>/<repo>`). Name the repository explicitly in that command; never let the runner infer it from a remote, which is the fork on a fork checkout.

Resolve it before `review-code` runs, so an unusable app costs nothing: read the login with that token in the environment — `GH_TOKEN=$(sh -c '<review-token command>') gh api graphql -f query='{viewer{login}}' --jq .data.viewer.login` — since `gh api user` is refused for an app token. A command that is absent, that fails, or whose token cannot authenticate is not an error — fall back to the authenticated user, record that fallback in the report, and publish under the ordinary self-review and gating rules.

Both shell blocks below carry that command in `tok`, which they assign empty: fill it in when a reviewing app publishes, and leave it empty to publish as the authenticated user. Each block runs it through `sh -c` and exports the token it prints, rather than expanding a command prefix in command position: an unquoted multiword expansion splits into words under `sh`, `bash`, and `dash` but not under `zsh`, where the whole string is read as one command name. Keeping the token in the environment also keeps it out of `argv`, which the timing wrapper records.

Each block then proves that token with `gh api "repos/{owner}/{repo}" --silent` before its first write, and exits 3 with nothing written when a filled-in `tok` fails, prints nothing, or prints a token the forge refuses. An empty `tok` is not that case: no app was declared, and the block writes as the authenticated user. Non-empty is not usable: a token minted against the wrong repository, or one whose installation was suspended after the review posted, passes an emptiness test and is then refused on every write. In the thread write loop that refusal is terminal — each reply records `failed`, every rerun skips it as `refused earlier; not retried`, and the thread actions behind those replies stay `blocked` — so the round's replies and resolutions would never publish against that results file.

Every login comparison against this identity ignores a trailing `[bot]`: REST records carry the suffix that GraphQL's `author{login}` omits for the same app, so an unnormalized compare makes an app's own prior review invisible.

A review published under a reviewing app is not a self-review, so the event table's gating events are available to it once the caller's packet carries that authorization. A gating event stands until a later review from the same identity replaces it or it is dismissed; a subsequent `COMMENT` leaves it standing. Dismiss a superseded gate with that token in the environment, as one `sh -c` argument so the timing wrapper can exec it:

```sh
sh -c 'GH_TOKEN=$(<review-token command>) || { echo "the review-token command failed; nothing was dismissed"; exit 3; }
[ -n "$GH_TOKEN" ] || { echo "the review-token command printed no token; nothing was dismissed"; exit 3; }
export GH_TOKEN
gh api --method PUT "repos/{owner}/{repo}/pulls/<pr>/reviews/<review id>/dismissals" -f message="$1" -f event=DISMISS' _ '<why>'
```

Dismiss only a review this identity published. The token is computed inside that shell, so it reaches the forge through the environment and never through the recorded `argv`. An empty one exits 3 with nothing dismissed rather than falling through: `gh` reads an empty `GH_TOKEN` as no token at all and would dismiss the app's review as the authenticated user. Each guard prints a reason before it exits, as the other two blocks do, and names its own route, which they do not need to: this is the only place where a runner that failed and a runner that printed an empty token are separate guards, and the gate left standing is reported rather than passed over in silence. A non-empty token the forge refuses needs no separate check here, because this single write is where it would be refused, visibly. The message travels as a positional argument rather than inside the quoted command: written into that string it would be expanded again by the inner shell, and a dismissal reason carrying a backtick, a `$`, or a code span would be executed or corrupted on its way to the forge. It is still a single-quoted argument of the outer shell, so a reason containing a single quote is quoted the ordinary way, as is a review-token command that contains one.

## Publication invariants

- Re-fetch the head immediately before writing; a stale or unreadable head aborts all publication. The freshness-and-submission block below makes that a preflight failure with exit 3.
- Keep retrospective review of a merged pull request non-publishing unless the caller separately and explicitly authorized publication to that merged target.
- Submit one review body and all new line comments in one forge-native review call. Include file-level comments there only when that batch endpoint documents file subjects; otherwise move their complete prose into the body before the call.
- A general comment is a fallback only when a non-gating native review is unavailable or refused.
- Re-read the target after an ambiguous write result before one retry.
- Store the run trailer in the summary and finding/question trailers in raw comment bodies.

- On a conclusive malformed-comment rejection, apply `review-code`'s render-and-validate step to the repaired record, confirm no review exists, and retry once.

## Timing events

Run every forge fetch and write this skill makes through the `run_events.py` path the review record carries: `python3 <recorded-absolute-run_events.py-path> wrap --private-dir <private-dir> --event <event> --data role=<role> [--data connection=root] -- <command>`, where `<private-dir>` is the directory of the record's private store. Wrap each command of a chain separately so no fetch or write escapes, and keep stdout redirects outside the wrapper. The thread write loop is the one exception: its whole run is wrapped once, and the replies, resolutions, and reconciliation reads inside it are not wrapped again. A record without that path runs the same commands unwrapped.

| Command | Event and data |
| --- | --- |
| Head re-fetch before writing, re-read after an ambiguous result, published-review readback | `forge-fetched`, `role=root`, `connection=root` |
| Review submission | `forge-written`, `role=review` |
| Each run of the thread write loop, reruns included | `forge-written`, `role=replies` |
| Dismissal of a superseded gate, as its single `sh -c` argument | `forge-written`, `role=review` |
| General-comment fallback | `forge-written`, `role=summary` |

A dismissal shares `role=review` because it writes that review's state; the wrapper's roles are a fixed vocabulary, and a command beginning with a `GH_TOKEN=` assignment is not one the wrapper can exec, which is why the dismissal is written as a single `sh -c` argument. The reviewer identity's own calls are the forge calls outside this table: the login read above, and each block's token check. They authenticate the publisher rather than reading or writing review state, and each block's check gates that block's writes.

The wrapper exits with the command's status; exit 2 with a `run_events:` line on stderr means it could not run the command, which counts as that fetch or write failing. These events time commands only. A successful wrapped write is not evidence that publication finished; the readback and failure reporting below still decide that. The loop's interval covers the whole loop, not each mutation, and its `write-results.jsonl` decides which writes succeeded.

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
tok=  # the review-token command when a reviewing app publishes; empty publishes as the authenticated user
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
if [ -n "$tok" ]; then
  GH_TOKEN=$(sh -c "$tok" 2> "$d/reviewer.stderr") || GH_TOKEN=
  export GH_TOKEN
  if [ -z "$GH_TOKEN" ] || ! gh api "repos/{owner}/{repo}" --silent 2>> "$d/reviewer.stderr"; then
    echo "preflight failed: the review-token command yielded no usable token; nothing was written"; cat "$d/reviewer.stderr"; exit 3
  fi
fi
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

`review-code` returns the advisory `COMMENT` batch. For a separately authorized gating event, run `python3 <recorded-absolute-validate_review.py-path> --emit-batch --event <REQUEST_CHANGES|APPROVE> < <private-dir>/payload.json > <private-dir>/batch.json`, replacing the advisory batch the freshness-and-submission block posts. Never edit the batch by hand. A non-zero exit stops publication: report the script's output.

On this gating path only, the script enforces the first-line grammar `**<Status>[ (advisory)]** — …`: the input advisory suffix is present exactly for `Changes Requested` or `Approved` under `COMMENT`. `APPROVE` requires `Approved`, and `REQUEST_CHANGES` requires `Changes Requested`; a mismatch exits 1. It removes the suffix and re-validates the edited body before printing. The batch is what validated after that one scripted edit. The ordinary `COMMENT` path retains its existing acceptance rules. Report the posted form from `batch.json`, not the advisory form in `payload.json`.

## Existing-thread replies and resolution

Every drafted reply and thread resolution goes through the thread write loop below, once, after the review posts. Non-publishing retrospective runs write no `writes.jsonl` and run no loop.

For every prior item `review-code` classified `fixed`, `accepted`, or `obsolete`, resolve its existing thread. If the item has a drafted reply, post it successfully before resolving; if it has no drafted reply, resolve directly. Use the returned thread node id, not the numeric comment id. Skip threads already resolved; leave `still-open`, `not-verifiable`, and disputed items open. An author's `declined` reply alone does not qualify: `review-code`'s evidence-backed classification governs the action. A prior item without a forge thread has no thread to resolve. Preserve the draft's stable id and disposition; do not create a new finding for a surviving prior item.

Write `<private-dir>/writes.jsonl` once from the completed record, one JSON object per prior item per line, with the host's file-writing tool rather than a shell `echo`:

- `id`: the item's stable id.
- `comment_id`: the numeric id of the thread's first comment; `thread_id`: the thread's GraphQL node id. Both are null for an item without a forge thread.
- `body`: the drafted reply exactly as drafted, or null when the item has no drafted reply.
- `action`: `resolve` for `fixed`, `accepted`, and `obsolete`; `none` for `still-open`, `not-verifiable`, disputed items, and items without a forge thread.
- `is_resolved` (optional): the thread's recorded state. `true` records the already-resolved skip instead of resolving again.

### Thread write loop

Run as one shell invocation after replacing `<private-dir>` and `<pr>`; `ev` is empty when the record carries no `run_events.py` path:

```sh
d=<private-dir> pr=<pr>
cat > "$d/writes.py" <<'PY'
import hashlib, json, os, re, sys

d, cmd, args = sys.argv[1], sys.argv[2], sys.argv[3:]
WRITES, RESULTS = os.path.join(d, "writes.jsonl"), os.path.join(d, "write-results.jsonl")
RAW = os.path.join(d, "write-responses")
FIELDS = ("id", "comment_id", "thread_id", "body", "action")
MUTATION = {"resolve": "resolveReviewThread", "reopen": "unresolveReviewThread"}
READ = ("query($id:ID!){ viewer{ login } node(id:$id){ ... on PullRequestReviewThread{ isResolved "
        "comments(last:100){ pageInfo{ hasPreviousPage } nodes{ fullDatabaseId databaseId url body "
        "author{ login } replyTo{ fullDatabaseId databaseId } } } } } }")

def jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f.read().split("\n") if line]

def get(obj, *path):
    for key in path:
        obj = obj.get(key) if isinstance(obj, dict) else None
    return obj

def bare(login):  # REST reports an app as `name[bot]`, GraphQL as `name`
    return login[:-5] if isinstance(login, str) and login.endswith("[bot]") else login

def number(comment):
    raw = get(comment, "fullDatabaseId")
    try:
        return int(get(comment, "databaseId") if raw is None else raw)
    except (TypeError, ValueError):
        return None

def op(row, step):  # (target, body digest) of a required write, or None
    if step == "reply":
        body = row["body"]
        return None if body is None else (row["comment_id"], hashlib.sha256(body.encode("utf-8")).hexdigest())
    if step == "none" or row.get("is_resolved") is (step == "resolve"):
        return None
    return (row["thread_id"], None)

def confirmed(results, row, step, key):
    return any(r["item"] == row["id"] and r["step"] == step and r["outcome"] == "confirmed"
               and [r["target"], r["body_sha256"]] == list(key) for r in results)

def append(row, i, step, kind, key, outcome, reason=None, **extra):
    rec = dict(item=row["id"], index=i, step=step, kind=kind, target=key[0] if key else None,
               body_sha256=key[1] if key else None, outcome=outcome, reason=reason, **extra)
    with open(RESULTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def validate():
    try:
        with open(WRITES, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print("unreadable writes.jsonl: %s" % e)
        sys.exit(2)
    problems, ids, threads, replies, count = [], set(), {}, set(), 0
    try:
        jsonl(RESULTS)
    except (OSError, ValueError) as e:
        problems.append("write-results.jsonl is unreadable or malformed: %s" % e)
    for n, line in enumerate(text.split("\n"), 1):
        if not line:
            continue
        count += 1
        try:
            row = json.loads(line)
        except ValueError:
            row = None
        if not isinstance(row, dict):
            problems.append("line %d: not a JSON object" % n)
            continue
        bad = ["missing %s" % k for k in FIELDS if k not in row]
        bad += ["unknown field %s" % k for k in sorted(set(row) - set(FIELDS) - {"is_resolved"})]
        if not bad:
            item, cid, tid, body, action = (row[k] for k in FIELDS)
            if not isinstance(item, str) or not item:
                bad.append("id is not a non-empty string")
            if cid is not None and (type(cid) is not int or cid <= 0):
                bad.append("comment_id is not a positive integer or null")
            if tid is not None and (not isinstance(tid, str) or not tid):
                bad.append("thread_id is not a non-empty string or null")
            if body is not None and (not isinstance(body, str) or not body):
                bad.append("body is not a non-empty string or null")
            if action not in ("resolve", "reopen", "none"):
                bad.append("action is not resolve, reopen, or none")
            if row.get("is_resolved") is not None and type(row["is_resolved"]) is not bool:
                bad.append("is_resolved is not a boolean or null")
        if not bad:
            if body is not None and (cid is None or tid is None):
                bad.append("a reply needs comment_id and thread_id")
            if action != "none" and tid is None:
                bad.append("%s needs thread_id" % action)
            if item in ids:
                bad.append("duplicate id %s" % item)
            if action != "none" and tid in threads:
                bad.append("second thread action on %s" % tid)
            elif tid in threads:
                bad.append("row on thread %s follows that thread's action on line %d" % (tid, threads[tid]))
            if body is not None and (cid, body) in replies:
                bad.append("duplicate reply to comment %s" % cid)
            ids.add(item)
            if action != "none" and tid not in threads:
                threads[tid] = n
            if body is not None:
                replies.add((cid, body))
        problems += ["line %d: %s" % (n, b) for b in bad]
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print(count)

def next_step(i, part, no_read):
    rows, results = jsonl(WRITES), jsonl(RESULTS)
    row = rows[i]
    step = "reply" if part == "reply" else row["action"]
    key = op(row, step)

    def skip(outcome, reason):
        append(row, i, step, "skip", key, outcome, reason)
        print("skip")
        sys.exit(0)
    if key is None:
        skip("skipped", {"reply": "no reply required", "none": "no thread action"}.get(step, "thread already in that state"))
    if step != "reply" and any(r["thread_id"] == row["thread_id"] and r["body"] is not None
                               and not confirmed(results, r, "reply", op(r, "reply")) for r in rows):
        skip("blocked", "reply not confirmed")
    if confirmed(results, row, step, key):
        skip("skipped", "already confirmed")
    mine = [r for r in results if r["item"] == row["id"] and r["step"] == step and r["kind"] != "skip"]
    same = [r for r in mine if [r["target"], r["body_sha256"]] == list(key)]
    attempts = lambda kind: len({r["attempt"] for r in mine if r["kind"] == kind})
    writes, last = attempts("write"), same[-1]["outcome"] if same else None
    if last == "failed":
        skip("blocked", "refused earlier; not retried")
    if last == "ambiguous" and no_read:
        skip("blocked", "reconciliation unsettled; not retried")
    if last == "ambiguous":
        tag = "%s-read%d" % (step, attempts("read") + 1)
        request = {"query": READ, "variables": {"id": row["thread_id"]}}
    elif writes >= 2:
        skip("blocked", "retry budget spent")
    elif step == "reply":
        tag, request = "reply-write%d" % (writes + 1), {"body": row["body"]}
    else:
        tag = "%s-write%d" % (step, writes + 1)
        request = {"query": "mutation($id:ID!){ %s(input:{threadId:$id}){ thread{ isResolved } } }" % MUTATION[step],
                   "variables": {"id": row["thread_id"]}}
    kind, attempt = tag.split("-")[1].rstrip("0123456789"), tag.split("-")[1]
    append(row, i, step, kind, key, "ambiguous", "attempt started; no result recorded", attempt=attempt)
    with open(os.path.join(RAW, "%d.%s.request.json" % (i, tag)), "w", encoding="utf-8") as f:
        json.dump(request, f, ensure_ascii=False)
    print(("reply %s %d" % (tag, row["comment_id"])) if tag.startswith("reply-write") else "graphql " + tag)

def refusal(rc, doc, err):
    code = re.search(r"HTTP (\d{3})", err)
    if get(doc, "errors") or (code and code.group(1)[0] == "4" and code.group(1) not in ("408", "429")):
        return "failed", "refused: " + (code.group(0) if code else "GraphQL errors")
    return "ambiguous", "exit %d without a conclusive refusal" % rc

def record(i, tag, rc):
    row = jsonl(WRITES)[i]
    step, attempt = tag.split("-")
    kind, key, want = ("read" if attempt.startswith("read") else "write"), op(row, step), step == "resolve"
    base = os.path.join(RAW, "%d.%s" % (i, tag))
    extra = dict(attempt=attempt, exit=rc, response=base + ".response.json", stderr=base + ".stderr")
    texts = []
    for path in (extra["response"], extra["stderr"]):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                texts.append(f.read())
        except OSError:
            texts.append("")
    try:
        doc = json.loads(texts[0])
    except ValueError:
        doc = None
    if kind == "read":
        node, viewer = get(doc, "data", "node"), get(doc, "data", "viewer", "login")
        nodes, earlier = get(node, "comments", "nodes"), get(node, "comments", "pageInfo", "hasPreviousPage")
        state = get(node, "isResolved")
        if rc != 0 or get(doc, "errors") or not isinstance(node, dict) or not viewer:
            outcome, reason = "ambiguous", "reconciliation read failed"
        elif step != "reply":
            outcome, reason = (("confirmed", "thread already in that state") if state is want else
                               ("absent", "thread state unchanged") if type(state) is bool else
                               ("ambiguous", "reconciliation read without isResolved"))
            extra["is_resolved"] = state
        elif not isinstance(nodes, list) or type(earlier) is not bool:
            outcome, reason = "ambiguous", "reconciliation read without comments or pageInfo"
        else:
            match = [c for c in nodes if bare(get(c, "author", "login")) == bare(viewer)
                     and number(get(c, "replyTo")) == row["comment_id"] and get(c, "body") == row["body"]]
            if match:
                outcome, reason = "confirmed", "matching reply already posted"
                extra.update(url=match[-1].get("url"), created_id=number(match[-1]))
            elif not earlier:
                outcome, reason = "absent", "no matching reply on the thread"
            else:
                outcome, reason = "ambiguous", "thread has comments before the 100 read"
    elif step == "reply":
        if rc == 0 and type(get(doc, "id")) is int and isinstance(get(doc, "html_url"), str) \
                and get(doc, "in_reply_to_id") == row["comment_id"]:
            outcome = "confirmed"
            reason = None if doc.get("body") == row["body"] else "returned body differs from the request"
            extra.update(url=doc["html_url"], created_id=doc["id"])
        elif rc == 0:
            outcome, reason = "ambiguous", "exit 0 without id, html_url, and in_reply_to_id"
        else:
            outcome, reason = refusal(rc, doc, texts[1])
    else:
        state = get(doc, "data", MUTATION[step], "thread", "isResolved")
        extra["is_resolved"] = state
        if rc == 0 and state is want:
            outcome, reason = "confirmed", None
        elif rc == 0 and type(state) is bool:
            outcome, reason = "failed", "returned isResolved %s" % json.dumps(state)
        elif rc == 0:
            outcome, reason = "ambiguous", "exit 0 without isResolved"
        else:
            outcome, reason = refusal(rc, doc, texts[1])
    append(row, i, step, kind, key, outcome, reason, **extra)
    print("%s %s %s: %s%s%s" % (row["id"], step, kind, outcome, "" if reason is None else " (%s)" % reason,
                                " " + extra["url"] if extra.get("url") else ""))

def summary():
    results, done, idle, unresolved = jsonl(RESULTS), 0, 0, []
    for row in jsonl(WRITES):
        for step in ("reply", row["action"]):
            key = op(row, step)
            if key is None:
                idle += 1
            elif confirmed(results, row, step, key):
                done += 1
            else:
                last = ([r for r in results if r["item"] == row["id"] and r["step"] == step] or [{}])[-1]
                unresolved.append("unresolved %s %s: %s%s%s" % (
                    row["id"], step, last.get("outcome", "not attempted"),
                    " (%s)" % last["reason"] if last.get("reason") else "",
                    ", see %s" % last["stderr"] if last.get("stderr") else ""))
    print("writes: %d confirmed, %d not required, %d unresolved" % (done, idle, len(unresolved)))
    for line in unresolved:
        print(line)
    sys.exit(1 if unresolved else 0)

if cmd == "validate":
    validate()
elif cmd == "next":
    next_step(int(args[0]), args[1], args[2:] == ["--no-read"])
elif cmd == "record":
    record(int(args[0]), args[1], int(args[2]))
else:
    summary()
PY
cat > "$d/write-loop.sh" <<'SH'
d=$1 pr=$2
w() { python3 "$d/writes.py" "$d" "$@"; }
mkdir -p "$d/write-responses" || exit 2
n=$(w validate); rc=$?
if [ "$rc" -eq 1 ]; then echo "$n"; echo "writes.jsonl refused; nothing was written"; exit 3; fi
if [ "$rc" -ne 0 ]; then echo "$n"; exit 2; fi
i=0
while [ "$i" -lt "$n" ]; do
  for part in reply action; do
    after=
    while :; do
      next=$(w next "$i" "$part" $after) || exit 2
      set -- $next
      [ "$1" = skip ] && break
      base="$d/write-responses/$i.$2"
      if [ "$1" = reply ]; then
        gh api --method POST "repos/{owner}/{repo}/pulls/$pr/comments/$3/replies" --input "$base.request.json" \
          > "$base.response.json" 2> "$base.stderr"
      else
        gh api graphql --input "$base.request.json" > "$base.response.json" 2> "$base.stderr"
      fi
      w record "$i" "$2" "$?" || exit 2
      case $2 in *-read*) after=--no-read ;; *) break ;; esac
    done
  done
  i=$((i + 1))
done
w summary
SH
ev=<recorded-absolute-run_events.py-path>
tok=  # the review-token command when a reviewing app publishes; empty publishes as the authenticated user
if [ -n "$tok" ]; then
  GH_TOKEN=$(sh -c "$tok" 2> "$d/reviewer.stderr") || GH_TOKEN=
  export GH_TOKEN
  if [ -z "$GH_TOKEN" ] || ! gh api "repos/{owner}/{repo}" --silent 2>> "$d/reviewer.stderr"; then
    echo "the review-token command yielded no usable token; no reply or resolution was written"
    cat "$d/reviewer.stderr"; exit 3
  fi
fi
if [ -z "$ev" ]; then sh "$d/write-loop.sh" "$d" "$pr"
else python3 "$ev" wrap --private-dir "$d" --event forge-written --data role=replies -- sh "$d/write-loop.sh" "$d" "$pr"; fi
```

The loop validates the whole file before its first write. A row that is not a JSON object, lacks or adds a field, has a mistyped value, lacks an id its operation needs (a reply needs `comment_id` and `thread_id`, a thread action needs `thread_id`), repeats an id, a reply body to one comment, or an action on one thread, or puts any row after its thread's action row refuses the file. The loop then prints one line per violation and `writes.jsonl refused; nothing was written`, and exits 3. Otherwise it takes items in file order, one write at a time. It posts the reply when `body` is non-null and performs the thread action only after every reply on that thread is confirmed; a thread with no reply to post leaves the action to run directly. Bodies travel as JSON request files through `--input` and are never evaluated or interpolated as shell, so multiline text, quotes, backslashes, Unicode, and trailing newlines arrive unchanged. A failed item does not stop the items after it.

Each attempt keeps its request, raw response, and stderr under `write-responses/`. Before its `gh` call it appends a started row to `write-results.jsonl`, and after the call a compact result row: item, step, kind (`write`, `read`, or `skip`), target, body digest, exit, outcome, reason, returned URL, created comment id or `isResolved`, and the file paths. A reply is `confirmed` only when the response carries an integer `id`, an `html_url`, and an `in_reply_to_id` equal to the target comment. A thread action is `confirmed` only when it returns the requested `isResolved`, and a returned opposite state is `failed`. An exit 0 without those fields is `ambiguous`. A non-zero exit is `failed` for GraphQL errors or an HTTP 4xx refusal other than 408 or 429, and `ambiguous` otherwise. A thread action while any reply on its thread is not confirmed is recorded `blocked` and checked again on a rerun, and an action already in the requested state or `none` is `skipped`. The loop prints one line per attempt, then `writes: <n> confirmed, <n> not required, <n> unresolved` with one `unresolved` line per required operation that is not confirmed. It exits 0 only when none is unresolved and 1 otherwise; an all-skipped or already-confirmed run exits 0. Exit 2 means the loop could not run.

After reading the results, reconcile by running the same block again. It re-validates and skips every confirmed operation, matching item, target, and exact body digest, so an earlier confirmation never covers a changed body or target. An attempt with a started row and no result row, as when the loop is interrupted mid-write, counts as `ambiguous`. For an operation whose last attempt was `ambiguous`, it first reads that thread's `isResolved`, the posting identity (`viewer`), and the thread's last 100 comments. A reply from that identity to the target comment with the exact body, stable trailer included, or the requested thread state confirms the operation without writing; that identity match ignores a trailing `[bot]`, which REST carries and GraphQL omits for the same app. A read showing neither permits the single retry of that operation alone. A failed read, or a thread with comments before the window, stays `ambiguous` with nothing retried. Each operation has at most two write attempts across every run against one results file, and a `failed` refusal is not retried. A reply confirmed before a failed action is never posted again, and a reply confirmed on a rerun is followed by its still-required action in the same run. Report every `unresolved` line as a reply or thread that failed to publish; never claim it closed.
