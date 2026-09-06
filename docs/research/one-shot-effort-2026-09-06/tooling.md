# Experiment tooling (issue #124), quoted verbatim from `/tmp/effort124`

These files ran the grid. They are experiment-local (absolute `/tmp` paths, one machine) and are quoted here so every dispatch is reproducible from the record; they are not skill scripts. `build_packet.py` is the holdout's builder with the merge-time cutoff added for this experiment. `run_cell.sh` is quoted in its final form (the detach-before-branch-move fix of ledger S8); `blind.py` in its final form (identifier redaction added after replicate 1).

## `agents.json`

````json
{"v5b-verifier-effort-high":{"description":"code-review-publish verifier batch pinned at effort high, for the issue #124 matched effort experiment. A child agent inherits its parent's effort, so every verifier batch is dispatched through this definition so that it runs at high regardless of the primary's effort. Not for ordinary use.","prompt":"You are one verifier batch for a cell of a controlled evaluation. The dispatch message carries the verifier task exactly as the primary reviewer composed it under the skill snapshot's references/verifier.md; follow that message and that reference. The only thing this definition changes is the effort level, which pins you at high regardless of the primary's effort. You do not spawn sub-agents.","model":"sonnet","effort":"high"}}
````

## `run_cell.sh`

````sh
#!/bin/sh
# run_cell.sh <target> <arm: high|medium> <seed> <attempt-id>
# Builds the clone, work dir, dispatch prompt and timing sidecar, then runs one headless
# claude session as the primary reviewer at the arm's effort with the verifier definition loaded.
set -eu
T=${1:-}; ARM=${2:-}; SEED=${3:-}; ATT=${4:-}
[ -n "$T" ] && [ -n "$ARM" ] && [ -n "$SEED" ] && [ -n "$ATT" ] || { echo "usage: run_cell.sh <target> <high|medium> <seed> <attempt-id>" >&2; exit 1; }
case "$ARM" in high|medium) ;; *) echo "arm must be high or medium" >&2; exit 1;; esac
B=/tmp/effort124
. "$B/targets/$T.sh"
CELL="$T-$ARM-seed$SEED"
CLONE="$B/runs/$CELL-$ATT"; WORK="$B/work/$CELL-$ATT"
REPORT="$B/reports/$T/$CELL-$ATT-run.md"; PAYLOAD="$B/reports/$T/$CELL-$ATT-payload.md"
TIMING="$B/reports/$T/$CELL-$ATT-timing.json"; DISPATCH="$B/dispatch/$T/$CELL-$ATT.md"
SKILL_DIR="$B/skill/skills/code-review-publish"
[ -s "$PACKET" ] || { echo "no packet $PACKET" >&2; exit 1; }
[ ! -e "$CLONE" ] || { echo "clone exists: $CLONE (attempt ids are never reused)" >&2; exit 1; }
[ ! -e "$TIMING" ] || { echo "sidecar exists: $TIMING" >&2; exit 1; }
mkdir -p "$B/runs" "$WORK" "$B/reports/$T" "$B/dispatch/$T" "$B/logs" "$B/sessions"
git clone -q "$B/mirrors/$T.git" "$CLONE"
git -C "$CLONE" remote set-url origin "$B/mirrors/$T.git"
git -C "$CLONE" checkout -q --detach "$HEAD_SHA"
git -C "$CLONE" branch -q -f "$BASE_BRANCH" "$MERGE_BASE"
git -C "$CLONE" checkout -q -B review-head "$HEAD_SHA"
[ "$(git -C "$CLONE" rev-parse HEAD)" = "$HEAD_SHA" ] || { echo "head mismatch" >&2; exit 1; }
for s in $NEG_SHAS; do
  if git -C "$CLONE" cat-file -e "$s" 2>/dev/null; then echo "LEAK: $s present in $CLONE" >&2; exit 1; fi
done
echo "clone $CLONE head=$HEAD_SHA merge-base=$MERGE_BASE negative checks passed: $NEG_SHAS" >> "$B/logs/clones.log"
python3 - "$B/dispatch-template.md" "$DISPATCH" "$LABEL" "$REPO_PR" "$CELL" "$ATT" "$SKILL_DIR" "$PACKET" "$CLONE" "$BASE_BRANCH" "$WORK" "$PAYLOAD" "$REPORT" "$TIMING" "$EXEC_NOTE" <<'PY'
import sys
tpl, out, label, repo_pr, cell, att, skill, packet, clone, base, work, payload, report, timing, exec_note = sys.argv[1:]
t = open(tpl, encoding="utf-8").read()
for k, v in {"{TARGET_LABEL}": label, "{REPO_PR}": repo_pr, "{CELL}": cell, "{ATTEMPT}": att, "{SKILL_DIR}": skill,
             "{PACKET}": packet, "{CLONE}": clone, "{BASE_BRANCH}": base, "{WORK}": work, "{PAYLOAD}": payload,
             "{REPORT}": report, "{TIMING}": timing, "{EXEC_NOTE}": exec_note}.items():
    t = t.replace(k, v)
assert "{" not in t.replace("{owner}", "").replace("{repo}", ""), "unfilled placeholder"
open(out, "w", encoding="utf-8").write(t)
PY
SID=$(uuidgen | tr 'A-Z' 'a-z')
echo "$CELL $ATT arm=$ARM session=$SID $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$B/logs/dispatch.log"
printf '%s\n' "$SID" > "$B/reports/$T/$CELL-$ATT-session.txt"
python3 "$B/mark_event.py" "$TIMING" root_dispatched_at
cd "$B/sessions"
set +e
timeout 5400 claude -p --session-id "$SID" --model sonnet --effort "$ARM" \
  --agents "$(cat "$B/agents.json")" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep,Agent" \
  --output-format json "$(cat "$DISPATCH")" < /dev/null \
  > "$B/logs/$CELL-$ATT.json" 2> "$B/logs/$CELL-$ATT.err"
RC=$?
set -e
echo "$CELL $ATT exit=$RC $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$B/logs/dispatch.log"
if [ "$RC" -eq 0 ] && [ -s "$REPORT" ] && [ -s "$PAYLOAD" ]; then
  python3 "$B/mark_event.py" "$TIMING" completed_at
else
  python3 - "$B/reports/$T/$CELL-$ATT-stop.json" "$RC" <<'PY'
import json, sys
from datetime import datetime, timezone
json.dump({"stopped_at": datetime.now(timezone.utc).isoformat(), "exit_code": int(sys.argv[2])}, open(sys.argv[1], "w"), indent=2)
PY
fi
exit $RC
````

## `dispatch-template.md`

````markdown
You are executing one cell of a controlled research evaluation of a code-review skill against a real, pinned, merged pull request. This is NOT a live review: no network access, no publishing, no repository mutation. You produce a review payload and a detailed research report; a researcher scores them afterwards. Nothing you write is posted anywhere.

## Cell identity

- Target: **{TARGET_LABEL}** — `{REPO_PR}`
- Cell: `{CELL}`, attempt `{ATTEMPT}` (an independent replicate; nothing is shared with other replicates except the packet and the mirror)
- Model: `claude-sonnet-5` for you and for every sub-agent you spawn. **Pass `model: "sonnet"` explicitly on every `Agent` call.**
- **Verifier dispatch.** Every verifier batch your skill calls for is dispatched with the `Agent` tool using `subagent_type: "v5b-verifier-effort-high"`, `model: "sonnet"`, and `run_in_background: false`. That agent definition is loaded in this session; it carries the verifier's effort setting and nothing else, and the verifier task text you compose under `references/verifier.md` is passed as its prompt exactly as the skill specifies. Never dispatch a verifier without that `subagent_type`.

**You are the reviewer for this cell.** Do the review yourself, in this context, following the skill snapshot. Never delegate the review, the reading of this dispatch, or the writing of the report to another agent; the only sub-agents you may spawn are the verifier batches your skill's own process calls for.

## Files

- Skill snapshot: `{SKILL_DIR}/` — read `SKILL.md` first, in full, then the references it names, from this directory only; ignore any other installed copy of a review skill. Run its scripts from this directory (`python3 {SKILL_DIR}/scripts/<name>.py`).
- Phase-1 packet: `{PACKET}` — the "pin the review" step already done for you. Use its pinned values verbatim; do not re-resolve anything. Its last section lists the binding run conditions.
- Clone: `{CLONE}` — offline; local branch `{BASE_BRANCH}` is pinned to the merge-base, local branch `review-head` is checked out at the head. Use `git diff {BASE_BRANCH} review-head` for the change and `git show {BASE_BRANCH}:<path>` for base versions. History is truncated at the head.
- Your working directory for payload JSON, scratch files, the private store, and script output: `{WORK}/` (it exists). Never write inside the clone.
- **Review payload:** write it to `{PAYLOAD}` — the review exactly as it would be published: summary body (with the `Mode` line for a merged target), every finding, question, and observation comment with its trailer, and nothing else.
- **Research report:** write it to `{REPORT}` — everything listed under "What to report" below. Link to the payload file from the report instead of pasting it.
- **Timing sidecar:** `{TIMING}` already exists. Immediately after `validate_review.py` exits 0 on your final payload, run `python3 /tmp/effort124/mark_event.py {TIMING} payload_validated_at`; if you change the payload and validate again later, run it again after that validation. Do not edit the file by hand and do not write any other event.

## Rules for this cell

1. Follow your skill as written: its phase order, its read discipline, its verification triggers, its output contract. Do not borrow behavior from any other review skill.
2. This is a **retrospective review of a merged pull request by a third party** (posting identity `kamui`, not the author); publication is disabled. Derive the status as for an open pull request, event `COMMENT`, and include the `Mode` line your contract requires. Where a step says "publish", render instead and stop.
3. Compute the `context` digest **once**, as your contract specifies; do not run the skill's self-tests inside this cell.
4. Clone hygiene: do not run `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the tree, and instruct every sub-agent the same. If a tree is mutated anyway, run `git -C {CLONE} reset --hard review-head` and disclose it.
5. **Execution allowance for this target.** {EXEC_NOTE}
6. **Persist before you verify.** Write the report file in stages: the manifest and requirement ledger when they are complete; the complete candidate ledger with every disposition before dispatching any verifier; each verifier prompt and its verbatim report as they arrive. Update the file as you go.
7. Stay inside your own sandbox: the clone, the skill snapshot, the packet directory, and your work, payload, report, and timing paths. Report any other path you read.
8. Sub-agents you spawn get the same rules 1–7 in their prompt, plus rule 9 below, `model: "sonnet"`, and the `subagent_type` named above.
9. No session relays: finish in this dispatch. Do not stop to ask anyone anything; if an input is genuinely missing, apply your skill's incomplete-coverage rule and say so in the report.
10. **Dispatch every sub-agent in the foreground** (`run_in_background: false`) and wait for its result before continuing. Never end your turn while a sub-agent of yours is still running, and never end your turn before the report and payload files are complete.

## What to report (the report file; be exhaustive — it is the only record of this cell)

1. **Metadata:** target, cell, attempt; skill and pin; the model you ran on and the model each sub-agent ran on (state each explicitly); which verification trigger fired, if any; sub-agents spawned (role, count, `subagent_type`); candidates raised, candidates surviving your own falsification; verifier verdicts; findings for publication with priority/action; questions; observations; coverage (every file and check inspected); derived status; your own token usage if the harness reports it, otherwise say it does not.
2. **Every finding that survives**, in full: priority/action, anchor, fix location, claim, verification status and evidence, trigger scenario.
3. **The complete private disposition ledger:** one row per candidate raised, with kind, disposition, decisive evidence pointer, and falsification reason — including every candidate dropped or acquitted.
4. **Every sub-agent dispatch:** the exact prompt given and the verbatim report returned.
5. **Everything consulted beyond the diff:** every file, command, and search, quoted, with whether each search was repo-wide and case-insensitive; every focused test or repro command run, with its exit status, duration, and output summary.
6. **The `context` digest** and the inputs it was computed from (title, body, issue coordinates, `comments_available`, guidance list).
7. **Mechanism checklist**, each item with a pointer to where in the run it is demonstrated or "did not fire", plainly: question channel; clean-verdict or related-acquittal verification (which mode, which rows, any re-open); observations; fix-sufficiency check on any concurrency/invariant candidate (did the verifier state the rule-level invariant and enumerate interleavings?); follow-up verifier round; deferral handling (any explicit deferral in the review record and how it was treated); retrospective mode.
8. **History discipline:** whether you read any history beyond the pinned head, and the exact history commands you ran.
9. **Sandbox disclosure:** any path read outside the sandbox.
10. **Notes:** every judgment call on an ambiguity in the skill's contract; what you treated as guidance and why.

Do not truncate detail for brevity.
````

## `mark_event.py`

````python
#!/usr/bin/env python3
"""mark_event.py <timing.json> <event>: set <event> in the timing sidecar to the current UTC time.
Events: root_dispatched_at, payload_validated_at, completed_at. Creates the file with
completion_mode render-only when it does not exist. Same clock source for every event."""
import json, sys, os
from datetime import datetime, timezone
path, event = sys.argv[1], sys.argv[2]
assert event in ("root_dispatched_at", "payload_validated_at", "completed_at"), event
d = {"completion_mode": "render-only", "root_dispatched_at": None, "payload_validated_at": None, "completed_at": None}
if os.path.exists(path):
    d.update(json.load(open(path, encoding="utf-8")))
d[event] = datetime.now(timezone.utc).isoformat()
json.dump(d, open(path, "w", encoding="utf-8"), indent=2)
print(event, d[event])
````

## `close_cell.py`

````python
#!/usr/bin/env python3
"""close_cell.py <target> <cell> <attempt> [--expect-effort high|medium]
Finds the cell's session transcript (root = primary) and every sub-agent transcript, scans
message.model and effort on every assistant line, meters billed usage, writes <cell>-<attempt>-meta.json."""
import argparse, glob, json, os, subprocess
B = "/tmp/effort124"
USAGE = "/Users/jack/.t3/worktrees/skills/t3code-e30d085b/docs/research/tools/transcript_usage.py"
PROJ = os.path.expanduser("~/.claude/projects/-private-tmp-effort124-sessions")

def scan(path):
    models, efforts, n = {}, {}, 0
    for line in open(path, encoding="utf-8"):
        try: o = json.loads(line)
        except Exception: continue
        if o.get("type") == "assistant":
            n += 1; m = o.get("message", {}).get("model"); e = o.get("effort")
            models[m] = models.get(m, 0) + 1; efforts[e] = efforts.get(e, 0) + 1
    return {"assistant_lines": n, "models": models, "efforts": efforts}

ap = argparse.ArgumentParser(); ap.add_argument("target"); ap.add_argument("cell"); ap.add_argument("attempt")
ap.add_argument("--expect-effort", required=True); a = ap.parse_args()
pre = f"{B}/reports/{a.target}/{a.cell}-{a.attempt}"
sid = open(pre + "-session.txt").read().strip()
root = f"{PROJ}/{sid}.jsonl"; subs = sorted(glob.glob(f"{PROJ}/{sid}/subagents/agent-*.jsonl"))
agents = [{"role": "primary (session root)", "path": root, "definition": f"--effort {a.expect_effort}", **scan(root)}]
for s in subs:
    meta = {}
    try: meta = json.load(open(s.replace(".jsonl", ".meta.json")))
    except Exception: pass
    agents.append({"role": "child", "path": s, "definition": meta.get("agentType"), "description": meta.get("description"), **scan(s)})
problems = []
for ag in agents:
    if set(ag["models"]) != {"claude-sonnet-5"}: problems.append(f"{ag['path']}: models {ag['models']}")
    want = a.expect_effort if ag["role"].startswith("primary") else "high"
    if set(ag["efforts"]) != {want}: problems.append(f"{ag['path']}: efforts {ag['efforts']} (expected {want})")
    if ag["role"] == "child" and ag["definition"] != "v5b-verifier-effort-high": problems.append(f"{ag['path']}: child definition {ag['definition']}")
paths = [root] + subs
timing = pre + "-timing.json"
cmd = ["python3", USAGE, *paths, "--prices", "2,10", "--report", pre + "-run.md"]
if os.path.exists(timing): cmd += ["--timing", timing]
block = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
js = subprocess.run(cmd + ["--json"], capture_output=True, text=True, encoding="utf-8")
row = subprocess.run(["python3", USAGE, *paths, "--prices", "2,10", "--report", pre + "-run.md", "--row", f"{a.cell} {a.attempt}"], capture_output=True, text=True, encoding="utf-8")
meta = {"cell": a.cell, "attempt": a.attempt, "session": sid, "agents": agents, "problems": problems,
        "usage_block": block.stdout + block.stderr, "usage_json": js.stdout, "row": row.stdout.strip(),
        "payload_bytes": os.path.getsize(pre + "-payload.md") if os.path.exists(pre + "-payload.md") else None,
        "report_bytes": os.path.getsize(pre + "-run.md") if os.path.exists(pre + "-run.md") else None}
json.dump(meta, open(pre + "-meta.json", "w", encoding="utf-8"), indent=2)
print(json.dumps({k: meta[k] for k in ("cell", "attempt", "session", "problems", "row", "payload_bytes", "report_bytes")}, indent=1))
for ag in agents: print(ag["role"], ag.get("definition"), ag["assistant_lines"], ag["models"], ag["efforts"], os.path.basename(ag["path"]))
print(block.stdout[-1600:])
````

## `meter.sh`

````sh
#!/bin/sh
# meter.sh <session-id> [label]: one usage row over the session root and every sub-agent transcript
P=$HOME/.claude/projects/-private-tmp-effort124-sessions
U=/Users/jack/.t3/worktrees/skills/t3code-e30d085b/docs/research/tools/transcript_usage.py
set -- "$P/$1.jsonl" $(find "$P/$1/subagents" -name 'agent-*.jsonl' 2>/dev/null) --prices 2,10 --row "${2:-$1}"
python3 "$U" "$@" 2>&1 | tail -1
````

## `blind.py`

````python
#!/usr/bin/env python3
"""blind.py seal <out-dir> <payload>...: copy payloads under random tokens, write a sealed mapping.
blind.py reveal <out-dir>: print the mapping."""
import json, os, secrets, shutil, sys
mode, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
mp = os.path.join(out, "mapping.sealed.json")
if mode == "seal":
    m = json.load(open(mp)) if os.path.exists(mp) else {}
    for p in sys.argv[3:]:
        tok = "blind-" + secrets.token_hex(3)
        while tok in m: tok = "blind-" + secrets.token_hex(3)
        import re
        txt = open(p, encoding="utf-8").read()
        txt = re.sub(r"[agh]-(high|medium)-seed\d-att-\d\d", "CELL", txt)
        txt = re.sub(r"\batt-\d\d\b", "ATT", txt)
        txt = re.sub(r"(?i)\b(effort|arm)\b[^\n]*", "[redacted line]", txt) if False else txt
        open(os.path.join(out, tok + ".md"), "w", encoding="utf-8").write(txt); m[tok] = os.path.abspath(p)
    json.dump(m, open(mp, "w"), indent=2); print("sealed", len(sys.argv) - 3, "payloads;", len(m), "total")
else:
    for k, v in sorted(json.load(open(mp)).items()): print(k, v)
````

## `build_packet.py`

````python
#!/usr/bin/env python3
"""Build a phase-1 review packet for one holdout target, in the test-4 packet format.

Reads the pull request, its closing issues with comments, reviews, review threads, and
conversation comments in ONE GraphQL call (the same shape code-review-publish step 1 uses),
the commit list and changed files from the same query, and the guidance inventory and
verified manifest from the local staging mirror. Writes Markdown to --out.

Usage:
  build_packet.py --repo hyperium/hyper --pr 3952 --head <sha> --merge-base <sha> \
      --base-sha <sha> --staging /tmp/holdout-staging/hyper.git --target a \
      --execution-note "..." --out /tmp/holdout/packets/a/packet.md
"""
import argparse, json, subprocess, sys, textwrap, os

QUERY = r'''
query($owner:String!,$name:String!,$number:Int!){
  repository(owner:$owner,name:$name){ url
    pullRequest(number:$number){
      title body state merged mergedAt isDraft baseRefName baseRefOid headRefOid createdAt
      author{login} authorAssociation
      baseRepository{ url }
      commits(first:100){ totalCount nodes{ commit{ oid committedDate message
        author{ name user{login} } } } }
      files(first:100){ nodes{ path additions deletions changeType } }
      closingIssuesReferences(first:10){ nodes{ number title body createdAt author{login} url repository{ nameWithOwner }
        comments(first:100){ totalCount nodes{ author{login} createdAt updatedAt body } } } }
      reviews(first:100){ nodes{ author{login} state body submittedAt commit{oid} } }
      reviewThreads(first:100){ nodes{ isResolved path line originalLine
        comments(first:50){ nodes{ author{login} body createdAt commit{oid} originalCommit{oid} } } } }
      comments(first:100){ nodes{ author{login} body createdAt } } } } }
'''


def gh_graphql(owner, name, number):
    out = subprocess.run(
        ["gh", "api", "graphql", "-F", f"owner={owner}", "-F", f"name={name}",
         "-F", f"number={number}", "-f", f"query={QUERY}"],
        check=True, capture_output=True, text=True).stdout
    return json.loads(out)["data"]["repository"]


def git(staging, *args):
    return subprocess.run(["git", "-C", staging, *args], check=True,
                          capture_output=True, text=True).stdout


def fence(text):
    text = (text or "").replace("\r\n", "\n").rstrip("\n")
    if text == "":
        return "*(empty)*"
    ticks = "```"
    while ticks in text:
        ticks += "`"
    return f"{ticks}\n{text}\n{ticks}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", type=int, required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--merge-base", required=True)
    ap.add_argument("--base-sha", required=True)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--target", required=True, help="a..f")
    ap.add_argument("--execution-note", default="Do not run the repository's build, test, lint, or any interpreter/compiler against it.")
    ap.add_argument("--extra-section", default=None, help="path to a Markdown file appended before the run conditions")
    ap.add_argument("--truncation-newest", default=None)
    ap.add_argument("--ref-pr", type=int, default=None, help="a pull request the body closes (GraphQL closingIssuesReferences omits PRs); fetched by REST and rendered as the originating reference")
    ap.add_argument("--spec-issue", default=None, help="owner/repo#n: an issue from another repository supplied as the user-supplied spec, fetched by REST with comments")
    ap.add_argument("--publish-to-fork", action="store_true", help="target (f): open PR on a repository we control; publication enabled; network permitted for gh against that repository only")
    ap.add_argument("--cutoff", default=None, help="ISO-8601 UTC instant; every review, thread comment, conversation comment and issue comment created after it is omitted (default: the merge time)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    owner, name = a.repo.split("/")
    R = gh_graphql(owner, name, a.pr)
    P = R["pullRequest"]
    assert P["headRefOid"] == a.head, (P["headRefOid"], a.head)
    cutoff = a.cutoff or P["mergedAt"]
    assert cutoff, "no cutoff and the PR is not merged"
    omitted = {"reviews": 0, "thread_comments": 0, "conversation": 0, "issue_comments": 0}
    def keep(nodes, key, name):
        kept = [x for x in nodes if (x.get(key) or "") <= cutoff]
        omitted[name] += len(nodes) - len(kept)
        return kept
    P["reviews"]["nodes"] = keep(P["reviews"]["nodes"], "submittedAt", "reviews")
    for t in P["reviewThreads"]["nodes"]:
        t["comments"]["nodes"] = keep(t["comments"]["nodes"], "createdAt", "thread_comments")
    P["reviewThreads"]["nodes"] = [t for t in P["reviewThreads"]["nodes"] if t["comments"]["nodes"]]
    P["comments"]["nodes"] = keep(P["comments"]["nodes"], "createdAt", "conversation")
    for i in P["closingIssuesReferences"]["nodes"]:
        i["comments"]["nodes"] = keep(i["comments"]["nodes"], "createdAt", "issue_comments")
        i["comments"]["totalCount"] = len(i["comments"]["nodes"])

    # manifest from the mirror, verified against the pinned SHAs
    numstat = git(a.staging, "diff", "--numstat", a.merge_base, a.head).strip().splitlines()
    status = git(a.staging, "diff", "--name-status", a.merge_base, a.head).strip().splitlines()
    st = {}
    for line in status:
        parts = line.split("\t")
        st[parts[-1]] = parts[0][0]
    rows = []
    adds = dels = 0
    for line in numstat:
        ad, de, path = line.split("\t")
        adds += int(ad) if ad != "-" else 0
        dels += int(de) if de != "-" else 0
        rows.append(f"{st.get(path, '?')}  {path:<70} (+{ad:<4} −{de})")
    manifest = "\n".join(rows)

    # commits on the head, oldest first (from the mirror, so nothing beyond the head)
    log = git(a.staging, "log", "--reverse", "--format=%H%x1f%cI%x1f%an%x1f%B%x1e", f"{a.merge_base}..{a.head}")
    commits = []
    for rec in log.split("\x1e"):
        rec = rec.strip("\n")
        if not rec.strip():
            continue
        oid, date, an, msg = rec.split("\x1f", 3)
        commits.append((oid, date[:10], an, msg.strip()))

    # guidance inventory at the merge-base
    changed_paths = [r.split()[1] for r in rows]
    candidates = ["AGENTS.md", "CLAUDE.md", "CONTEXT.md", "CONTRIBUTING.md", "CODEOWNERS",
                  ".github/CODEOWNERS", ".github/PULL_REQUEST_TEMPLATE.md", ".github/pull_request_template.md"]
    scoped = set()
    for p in changed_paths:
        d = os.path.dirname(p)
        while d:
            scoped.add(f"{d}/AGENTS.md"); scoped.add(f"{d}/CLAUDE.md")
            d = os.path.dirname(d)
    guidance_rows = []
    for c in candidates + sorted(scoped):
        try:
            blob = git(a.staging, "rev-parse", "--verify", "-q", f"{a.merge_base}:{c}").strip()
        except subprocess.CalledProcessError:
            blob = ""
        if c in candidates or blob:
            guidance_rows.append(f"| `{c}` | {'**yes**' if blob else 'no'} | {('`'+blob+'`') if blob else '—'} |")

    issues = P["closingIssuesReferences"]["nodes"]
    ref_pr = None
    if a.ref_pr:
        rp = json.loads(subprocess.run(["gh","api",f"repos/{a.repo}/pulls/{a.ref_pr}"],check=True,capture_output=True,text=True).stdout)
        rc = json.loads(subprocess.run(["gh","api",f"repos/{a.repo}/issues/{a.ref_pr}/comments?per_page=100"],check=True,capture_output=True,text=True).stdout)
        ref_pr = {"number": a.ref_pr, "title": rp["title"], "body": rp["body"], "createdAt": rp["created_at"], "author": {"login": rp["user"]["login"]}, "state": rp["state"], "merged": rp["merged"], "closedAt": rp["closed_at"],
                  "comments": {"totalCount": len(rc), "nodes": [{"author": {"login": c["user"]["login"]}, "createdAt": c["created_at"], "body": c["body"]} for c in rc]}}
    spec = None
    if a.spec_issue:
        srepo, snum = a.spec_issue.split("#")
        si = json.loads(subprocess.run(["gh","api",f"repos/{srepo}/issues/{snum}"],check=True,capture_output=True,text=True).stdout)
        sc = json.loads(subprocess.run(["gh","api",f"repos/{srepo}/issues/{snum}/comments?per_page=100"],check=True,capture_output=True,text=True).stdout)
        spec = {"coord": a.spec_issue, "url": si["html_url"], "title": si["title"], "body": si["body"], "createdAt": si["created_at"], "author": si["user"]["login"],
                "comments": [{"author": c["user"]["login"], "createdAt": c["created_at"], "body": c["body"]} for c in sc]}
    out = []
    w = out.append
    w(f"# Review packet — `{a.repo}#{a.pr}` (target ({a.target}), issue #124 effort experiment)\n")
    w(textwrap.dedent(f"""\
        Phase 1 (target resolution) has already been performed by the orchestrator and is reproduced here in
        full. **Do not attempt to re-resolve the target over the network — you have no network access.**
        Treat every fact in this packet as authoritative pinned input. This packet is byte-identical for every
        arm and replicate on this target.
        """))
    w("## 1. Pinned run identity\n")
    w("| | |\n| --- | --- |")
    w(f"| Pull request | [`{a.repo}#{a.pr}`]({R['url']}/pull/{a.pr}) — \"{P['title']}\" |")
    w(f"| Author | `{P['author']['login']}` (association at fetch time: `{P['authorAssociation']}`) |")
    w(f"| Repository URL (`summary.repository_url`) | `{P['baseRepository']['url']}` |")
    w(f"| Head SHA | `{a.head}` (local branch `review-head`, checked out) |")
    w(f"| Base ref | `{P['baseRefName']}` (local branch `{P['baseRefName']}`, force-pinned to the merge-base) |")
    w(f"| Base SHA (as recorded on the pull request) | `{a.base_sha}` |")
    w(f"| Merge-base | `{a.merge_base}`{' (identical to the base SHA)' if a.merge_base == a.base_sha else ' (**differs from the base SHA**: the base branch moved before the merge; review against the merge-base)'} |")
    w(f"| Diff | {len(rows)} files, +{adds} / −{dels}, {len(commits)} commits |")
    w(f"| `state` | `{P['state']}` |")
    w(f"| `merged` | **`{'true' if P['merged'] else 'false'}`** (merged {P['mergedAt']}) |")
    w(f"| `isDraft` | `{'true' if P['isDraft'] else 'false'}` |")
    if issues:
        w("| Originating issue(s) | " + "; ".join(f"[`{i['repository']['nameWithOwner']}#{i['number']}`]({i['url']}) — \"{i['title']}\" (closing reference in the PR body{'; the issue lives in another repository, which the forge resolved for reading; record `issues=' + i['repository']['nameWithOwner'] + '#' + str(i['number']) + '`' if i['repository']['nameWithOwner'] != a.repo else ''})" for i in issues) + " |")
    elif ref_pr:
        w(f"| Originating reference | [`{a.repo}#{ref_pr['number']}`]({R['url']}/pull/{ref_pr['number']}) — \"{ref_pr['title']}\", a **pull request** (state `{ref_pr['state']}`, merged `{'true' if ref_pr['merged'] else 'false'}`, closed {ref_pr['closedAt']}) that the PR body closes with `Closes #{ref_pr['number']}`. It is the spec source: treat its body and comments as the originating issue text and record `issues={a.repo}#{ref_pr['number']}` |")
    else:
        w("| Originating issue(s) | none — the PR body carries no closing reference; `issues=none` unless the dispatch supplies a spec |")
    if a.publish_to_fork:
        w("| Posting identity | `kamui` (also the repository owner and the PR opener on this replay repository; the original author is `scop`). Treat this as an ordinary first review by a third party, event `COMMENT`: this is a **live, open pull request on a repository this program controls, and publication is ENABLED** |")
    else:
        w("| Posting identity | `kamui`, who did NOT author the PR and has no prior comments or reviews on it → an ordinary first review by a third party, event `COMMENT`; the target is merged, so this is a **retrospective review with publication disabled** |")
    w("")
    w(f"Compute the diff as `git diff {P['baseRefName']} review-head` (the `{P['baseRefName']}` branch is pinned to the merge-base, so two-dot and three-dot are identical here).\n")
    w("## 2. Changed-file manifest (verified against the pinned SHAs from the mirror)\n")
    w("```\n" + manifest + "\n```\n")
    w("## 3. Pull-request body, verbatim\n")
    w(fence(P["body"]) + "\n")
    if issues:
        for i in issues:
            w(f"## 4. Originating issue `{i['repository']['nameWithOwner']}#{i['number']}`, verbatim\n")
            w(f"Title: **{i['title']}**  \nOpened {i['createdAt'][:10]} by `{i['author']['login'] if i['author'] else 'ghost'}`.\n")
            w(fence(i["body"]) + "\n")
            cs = i["comments"]["nodes"]
            w(f"### Issue comments through the frozen cutoff `{cutoff}`, verbatim, in order ({i['comments']['totalCount']} total; `comments_available: true`)\n")
            if not cs:
                w("*(none)*\n")
            for k, c in enumerate(cs, 1):
                w(f"**{k}.** {c['createdAt']} · `{c['author']['login'] if c['author'] else 'ghost'}`\n")
                w(fence(c["body"]) + "\n")
    elif ref_pr:
        i = ref_pr
        w(f"## 4. Originating reference `#{i['number']}` (a pull request, closed unmerged), verbatim\n")
        w(f"Title: **{i['title']}**  \nOpened {i['createdAt'][:10]} by `{i['author']['login']}`; state `{i['state']}`, not merged; closed {i['closedAt']} when the reviewed pull request merged.\n")
        w(fence(i["body"]) + "\n")
        cs = i["comments"]["nodes"]
        w(f"### Comments on `#{i['number']}`, verbatim, in order ({i['comments']['totalCount']} total; `comments_available: true`)\n")
        if not cs:
            w("*(none)*\n")
        for k, c in enumerate(cs, 1):
            w(f"**{k}.** {c['createdAt']} · `{c['author']['login']}`\n")
            w(fence(c["body"]) + "\n")
    elif spec:
        w(f"## 4. User-supplied spec: `{spec['coord']}`, verbatim\n")
        w(f"The PR body's closing reference points at an issue in another repository, which the forge does not resolve across repositories. The orchestrator supplies that issue here as the user-supplied spec (`SKILL.md` step 1, order item 3). Record `issues={spec['coord']}`. Title: **{spec['title']}**, opened {spec['createdAt'][:10]} by `{spec['author']}` ({spec['url']}).\n")
        w(fence(spec["body"]) + "\n")
        w(f"### Issue comments, verbatim, in order ({len(spec['comments'])} total; `comments_available: true`)\n")
        for k, c in enumerate(spec["comments"], 1):
            w(f"**{k}.** {c['createdAt']} · `{c['author']}`\n")
            w(fence(c["body"]) + "\n")
    else:
        w("## 4. Originating issue\n\nNone. The pull-request body is the only statement of intent. Record `issues=none` (or the coordinate of a spec the dispatch supplies).\n")
    w("## 5. Commits on the head, oldest first — messages verbatim\n")
    w("| # | SHA | Date | Author | Message |\n| --- | --- | --- | --- | --- |")
    for k, (oid, date, an, msg) in enumerate(commits, 1):
        m = msg.replace("|", "\\|").replace("\n", "<br>")
        w(f"| {k} | `{oid[:9]}` | {date} | {an} | {m} |")
    w("")
    w(textwrap.dedent("""\
        > **Mandatory note, same class as prior packets in this program.** Where later commits on the head
        > applied the author's responses to earlier review rounds, that feedback is already fixed in the reviewed
        > head and must not be rediscovered and reported as still outstanding. Read the prior-review section
        > below against the head before treating any earlier comment as live.
        """))
    w(f"## 6. Prior review state through the frozen cutoff `{cutoff}` (the merge instant), reproduced verbatim\n")
    revs = P["reviews"]["nodes"]
    w(f"### Review submissions ({len(revs)})\n")
    w("| When | Who | State | On commit | Body |\n| --- | --- | --- | --- | --- |")
    for r in revs:
        body = (r["body"] or "").replace("\r\n", "\n").replace("|", "\\|").replace("\n", "<br>")
        w(f"| {r['submittedAt']} | `{r['author']['login'] if r['author'] else 'ghost'}` | {r['state']} | `{(r['commit'] or {}).get('oid', '')[:9]}` | {body if body else '*(empty)*'} |")
    w("")
    threads = P["reviewThreads"]["nodes"]
    w(f"### Review threads ({len(threads)}), comments verbatim, in order\n")
    if not threads:
        w("*(no inline review comments)*\n")
    n = 0
    for t in threads:
        for c in t["comments"]["nodes"]:
            n += 1
            w(f"**{n}.** {c['createdAt']} · `{c['author']['login'] if c['author'] else 'ghost'}` · `{t['path']}:{t['originalLine'] or t['line']}` · on commit `{(c['originalCommit'] or {}).get('oid', '')[:9]}` · thread {'resolved' if t['isResolved'] else 'unresolved'}\n")
            w(fence(c["body"]) + "\n")
    conv = P["comments"]["nodes"]
    w(f"### Non-review conversation ({len(conv)}), verbatim, in order\n")
    if not conv:
        w("*(none)*\n")
    for k, c in enumerate(conv, 1):
        w(f"**{k}.** {c['createdAt']} · `{c['author']['login'] if c['author'] else 'ghost'}`\n")
        w(fence(c["body"]) + "\n")
    w("## 7. Repository guidance present at the merge-base\n")
    w("Verified by direct lookup in the mirror. Path-scoped `AGENTS.md`/`CLAUDE.md` in every ancestor directory of a changed path were checked; only rows that exist or are the standard root candidates are listed.\n")
    w("| Path | Present at merge-base | Blob |\n| --- | --- | --- |")
    out.extend(guidance_rows)
    w("\nRead any present file from the clone with `git show <base-branch>:<path>` and treat it according to your own skill's guidance contract; record how you classified it.\n")
    if a.extra_section:
        w(open(a.extra_section).read().rstrip("\n") + "\n")
    newest = a.truncation_newest or a.head[:9]
    w("## 8. Run conditions — binding on this run and on every sub-agent you spawn\n")
    if a.publish_to_fork:
        w(textwrap.dedent(f"""\
        1. **Network: forge access to this one repository only.** `gh` may be used against `{a.repo}` (read the pull request, its reviews, threads, and comments; post the review; reply on threads). No other network call of any kind: no `git fetch`/`pull` from anywhere but your clone's `origin`, no access to `spf13/cobra` or any other repository, no `curl`, no web fetch. Your clone's `origin` is the replay repository.
        2. **No execution.** {a.execution_note} **The review is entirely static** — reason from the source, and say so where a claim would ordinarily be settled by running something. Your own skill's helper scripts are exempt.
        3. **History is truncated at the pinned head on purpose.** The newest object reachable in your clone and in the replay repository is `{newest}`. Nothing that happened after this head exists there. Do not try to work around this.
        4. **Publication is ENABLED**, to this pull request on `{a.repo}`, exactly as your skill specifies: one forge-native review with the summary and every finding, event `COMMENT`, after the validator and the stale-head re-fetch. This is the only target in the evaluation that publishes. Do not edit the pull request, the branch, or the repository in any other way.
        5. **Follow your own skill as written** — its phase structure, its fan-out policy, its verification triggers, its output contract. Where the skill tells you to spawn sub-agents, spawn them with the `Agent` tool and **pass `model: "sonnet"` explicitly on every call**.
        6. **Persist before you verify.** Write the expensive phase to your report file before dispatching any verifier or finder, and update the file as you go.
        7. **Stay in your own sandbox.** Your clone, your skill snapshot, this packet directory, and your own report and payload paths only.
        """))
    else:
      w(textwrap.dedent(f"""\
        1. **Offline.** Your clone's `origin` points at a local filesystem path, not `github.com`. No
           `git fetch`, no `git pull`, no `gh`, no `curl`, no web fetch, no network call of any kind, by you
           or by any sub-agent. If your skill's phase 1 asks you to resolve the target from the forge, that
           phase is satisfied by this packet, including its `merged` field.
        2. **Execution allowance.** {a.execution_note} Your own skill's helper scripts are always
           permitted; run them from the skill directory.
        3. **History is truncated at the pinned head on purpose.** The newest object reachable in your clone
           is `{newest}`. Nothing that happened after this pull request exists locally. Do not try to work
           around this. At the end, report explicitly whether you read any history beyond the pinned head and
           which history commands you ran.
        4. **Publication is disabled.** The target is merged; this is a retrospective review. Do not post
           anything anywhere. Follow your skill through to the point where it would publish, then render the
           review **exactly as it would be posted**, including summary body (with the `Mode` line your
           contract requires for a merged target), per-finding comments, and any trailers, and stop.
        5. **Follow your own skill as written** — its phase structure, its fan-out policy, its verification
           triggers, its output contract. Do not borrow behavior from any other review skill. Where the skill
           tells you to spawn sub-agents, spawn them with the `Agent` tool and **pass `model: "sonnet"`
           explicitly on every call**.
        6. **Persist before you verify.** Write the expensive phase to your report file before dispatching
           any verifier or finder: the manifest and requirement ledger when they are complete, then the
           complete candidate ledger with every disposition, then the verifier prompts and verbatim reports as
           they arrive. A session interruption after that point loses nothing that the file holds.
        7. **Stay in your own sandbox.** Your clone, your skill snapshot, this packet directory, and your
           own report and payload paths only. Do not read any other run's clone, report, or payload. Report
           it if you read one anyway.
        """))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        f.write("\n".join(out))
    print(f"cutoff {cutoff}; omitted after cutoff: {omitted}")
    print(f"wrote {a.out}: {len(rows)} files, {len(commits)} commits, {len(revs)} reviews, {n} thread comments, {len(conv)} conversation comments, {len(issues)} issues, ref_pr={a.ref_pr}")


if __name__ == "__main__":
    main()
````

## `provision_g.sh`

````sh
#!/bin/sh
set -eu
B=/tmp/effort124
HEAD=7052d2454a2370ab9583f63711df89f3bd7bec83
BASE=ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401
mkdir -p $B/staging $B/packets/g $B/reports/g $B/dispatch/g
[ -d $B/staging/bytes.git ] || git clone -q --bare https://github.com/tokio-rs/bytes $B/staging/bytes.git
S=$B/staging/bytes.git
git -C $S cat-file -e $HEAD && echo "head present in staging"
MB=$(git -C $S merge-base $BASE $HEAD); echo "merge-base $MB"
[ "$MB" = "$BASE" ] || echo "NOTE: merge-base differs from base"
git -C $S log -1 --format='%H %cI %s' $HEAD
git -C $S diff --stat $MB $HEAD
rm -rf $B/mirrors/g.git; git init -q --bare $B/mirrors/g.git
git -C $S push -q $B/mirrors/g.git 7052d2454a2370ab9583f63711df89f3bd7bec83:refs/heads/review-head ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401:refs/heads/master
git -C $B/mirrors/g.git symbolic-ref HEAD refs/heads/master
git -C $B/mirrors/g.git for-each-ref
for s in baa5053572ed9e88ca1058ec2b5a3f08046c5a40 f488be48d07d899dc428c5cd7f5c11a95bf7716c ed7d5ff39e39c2802c0fa9e2fc308f6a3e0beda7 f400b119a9773973118eb4a4fc3dcb127974bcc9 f50c007da958d4ed597e25b9e1f54f727f9953fe; do
  git -C $S cat-file -e $s && echo "staging has $s (expected)"
  if git -C $B/mirrors/g.git cat-file -e $s 2>/dev/null; then echo "LEAK $s"; exit 1; else echo "mirror absent $s"; fi
done
# newest reachable object check: every commit reachable from review-head must be dated <= head's date
git -C $B/mirrors/g.git log --format='%cI' review-head | sort | tail -1
````

## `provision_h.sh`

````sh
#!/bin/sh
# Provision target (h) etcd-io/etcd#18749: staging, truncated mirror, offline Go module cache, timed test run.
set -eu
B=/tmp/effort124
HEAD=8a0fd66db3291bd6397a1341dc07ad41294a3caf
BASE=bb381d473c24ff2cd771f109c63443e03ac459c2
START=$(date -u +%s)
mkdir -p $B/staging $B/packets/h $B/reports/h $B/dispatch/h $B/gomodcache
[ -d $B/staging/etcd.git ] || git clone -q --bare https://github.com/etcd-io/etcd $B/staging/etcd.git
S=$B/staging/etcd.git
git -C $S cat-file -e $HEAD 2>/dev/null || git -C $S fetch -q origin refs/pull/18749/head:refs/pull/18749/head
git -C $S cat-file -t $HEAD
MB=$(git -C $S merge-base $BASE $HEAD); echo "merge-base $MB base $BASE"
git -C $S log -1 --format='%H %cI %s' $HEAD
git -C $S diff --stat $MB $HEAD
rm -rf $B/mirrors/h.git; git init -q --bare $B/mirrors/h.git
git -C $S push -q $B/mirrors/h.git 8a0fd66db3291bd6397a1341dc07ad41294a3caf:refs/heads/review-head bb381d473c24ff2cd771f109c63443e03ac459c2:refs/heads/main
git -C $B/mirrors/h.git symbolic-ref HEAD refs/heads/main
git -C $B/mirrors/h.git for-each-ref
for s in 38c27a4f8d5e3766a41edbbf8145f03850542d96; do
  git -C $S cat-file -e $s && echo "staging has $s (expected)"
  if git -C $B/mirrors/h.git cat-file -e $s 2>/dev/null; then echo "LEAK $s"; exit 1; else echo "mirror absent $s"; fi
done
echo "newest reachable: $(git -C $B/mirrors/h.git log --format='%cI' review-head | sort | tail -1)"
echo "clone+mirror done at $(( $(date -u +%s) - START ))s"
T=$(mktemp -d); git clone -q $B/mirrors/h.git $T/etcd; git -C $T/etcd checkout -q review-head
export GOMODCACHE=$B/gomodcache GOFLAGS=-mod=mod
cd $T/etcd/server && go mod download 2>&1 | tail -3; echo "mod download done at $(( $(date -u +%s) - START ))s"
export GOPROXY=off
t0=$(date -u +%s); go test ./etcdserver/txn/... 2>&1 | tail -5; echo "txn tests: $(( $(date -u +%s) - t0 ))s"
t0=$(date -u +%s); go test -race ./etcdserver/txn/... 2>&1 | tail -3; echo "txn race tests: $(( $(date -u +%s) - t0 ))s"
git -C $T/etcd status --short | head -5
cd /; rm -rf $T; du -sh $B/gomodcache; echo "total $(( $(date -u +%s) - START ))s"
````

## `targets/a.sh`

````sh
LABEL="(a) hyperium/hyper#3952"
REPO_PR="hyperium/hyper#3952"
BASE_BRANCH=master
MERGE_BASE=f9f8f44058745d23fa52abf51b96b61ee7665642
HEAD_SHA=f2aa734e5699a91fc20f1178e38af7b1e374bdbc
PACKET=/tmp/effort124/packets/a/packet.md
NEG_SHAS="2377b893f6e64ca9878e4f25d1472b96baa7e3ea 4492f31e9429c34166da5a069c00b65be20e4a02 743a3ba0706fde95e2095ad42ffefe219d807117 a416aa8be05e36767830df2180f9aa78f6b412e7 f660f5bf6eed3fe793f899507ff5bb9e266d4b0d"
EXEC_NOTE="No execution: do not run cargo, rustc, miri, or loom in any form (the toolchain would need the network for crates); the review is entirely static, as the packet's section 8 states. Your own skill's helper scripts are exempt."
````

## `targets/g.sh`

````sh
LABEL="(g) tokio-rs/bytes#698"
REPO_PR="tokio-rs/bytes#698"
BASE_BRANCH=master
MERGE_BASE=ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401
HEAD_SHA=7052d2454a2370ab9583f63711df89f3bd7bec83
PACKET=/tmp/effort124/packets/g/packet.md
NEG_SHAS="baa5053572ed9e88ca1058ec2b5a3f08046c5a40 f488be48d07d899dc428c5cd7f5c11a95bf7716c ed7d5ff39e39c2802c0fa9e2fc308f6a3e0beda7 f400b119a9773973118eb4a4fc3dcb127974bcc9 f50c007da958d4ed597e25b9e1f54f727f9953fe"
EXEC_NOTE="Focused test execution IS permitted on this target, offline, exactly as the packet's section 8 item 2 states: cargo with CARGO_HOME=/tmp/effort124/cargo-home CARGO_NET_OFFLINE=true CARGO_TARGET_DIR=<your work dir>/target, five minutes per command, the suite at most once, scratch crates only under your work directory, nothing added to or changed in the clone."
````

## `targets/h.sh`

````sh
LABEL="(h) etcd-io/etcd#18749"
REPO_PR="etcd-io/etcd#18749"
BASE_BRANCH=main
MERGE_BASE=bb381d473c24ff2cd771f109c63443e03ac459c2
HEAD_SHA=8a0fd66db3291bd6397a1341dc07ad41294a3caf
PACKET=/tmp/effort124/packets/h/packet.md
NEG_SHAS="38c27a4f8d5e3766a41edbbf8145f03850542d96"
EXEC_NOTE="Focused test execution IS permitted on this target, offline, exactly as the packet's section 8 item 2 states: go commands from the clone's server/ module with GOMODCACHE=/tmp/effort124/gomodcache GOCACHE=/tmp/effort124/gocache GOFLAGS=-mod=mod GOPROXY=off, five minutes per command, a package's tests at most once per flag set, scratch modules only under your work directory, nothing added to or changed in the clone."
````
