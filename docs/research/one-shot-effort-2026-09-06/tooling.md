# Experiment tooling (issue #124), quoted verbatim from `/tmp/effort124`

These files ran the grid. They are experiment-local (absolute `/tmp` paths, one machine) and are quoted here so every dispatch is reproducible from the record; they are not skill scripts.

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
