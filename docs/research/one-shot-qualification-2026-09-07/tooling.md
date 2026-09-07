# Experiment tooling (issue #137), quoted verbatim from `/tmp/qual137`

These files ran the grid. They are experiment-local (absolute `/tmp` paths, one machine) and are quoted here so every dispatch is reproducible from the record; they are not skill scripts. The packet builder is not reproduced: this grid used the shipped [`docs/research/tools/build_packet.py`](../tools/build_packet.py) (#184) unmodified, and the exact invocations are in §Packet builds below. `run_cell.sh` is quoted in its final form, including the `POST_CLONE` provisioning hook and the `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` export added after ledger S3.

## `run_cell.sh`

````sh
#!/bin/sh
# run_cell.sh <target-letter> <arm: bea6be14|867cf3ff> <seed> <attempt-id>
# Builds the clone, work dir, dispatch prompt and timing sidecar, then runs one headless
# claude session as the primary reviewer from the arm's pinned skill snapshot.
set -eu
T=${1:-}; ARM=${2:-}; SEED=${3:-}; ATT=${4:-}
[ -n "$T" ] && [ -n "$ARM" ] && [ -n "$SEED" ] && [ -n "$ATT" ] || { echo "usage: run_cell.sh <target> <bea6be14|867cf3ff> <seed> <attempt-id>" >&2; exit 1; }
case "$ARM" in bea6be14|867cf3ff) ;; *) echo "arm must be a pinned tree hash prefix" >&2; exit 1;; esac
B=/tmp/qual137
. "$B/targets/$T.sh"
CELL="$T-$ARM-seed$SEED"
CLONE="$B/runs/$CELL-$ATT"; WORK="$B/work/$CELL-$ATT"
REPORT="$B/reports/$T/$CELL-$ATT-run.md"; PAYLOAD="$B/reports/$T/$CELL-$ATT-payload.md"
TIMING="$B/reports/$T/$CELL-$ATT-timing.json"; DISPATCH="$B/dispatch/$T/$CELL-$ATT.md"
SKILL_DIR="$B/snapshots/$ARM/skills/code-review-publish"
[ -s "$PACKET" ] || { echo "no packet $PACKET" >&2; exit 1; }
[ -d "$SKILL_DIR" ] || { echo "no skill snapshot $SKILL_DIR" >&2; exit 1; }
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
if [ -n "${POST_CLONE:-}" ]; then
  echo "post-clone provisioning for $T in $CLONE" >> "$B/logs/clones.log"
  ( cd "$CLONE" && eval "$POST_CLONE" ) >> "$B/logs/clones.log" 2>&1 || { echo "post-clone provisioning failed" >&2; exit 1; }
  DIRTY=$(git -C "$CLONE" status --short | head -3)
  [ -z "$DIRTY" ] || { echo "post-clone provisioning dirtied the tree: $DIRTY" >&2; exit 1; }
fi
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
CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 timeout 5400 claude -p --session-id "$SID" --model sonnet --effort high \
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
- **Sub-agent dispatch.** Every fresh-context worker your skill calls for — a verifier batch, a clean-verdict batch, anything the skill's own references specify — is dispatched with the `Agent` tool using `subagent_type: "general-purpose"`, `model: "sonnet"`, and `run_in_background: false`. Compose its prompt exactly as your skill's own references specify; the `subagent_type` is only the transport this harness offers for "a genuinely fresh context".

**You are the reviewer for this cell.** Do the review yourself, in this context, following the skill snapshot. Never delegate the review, the reading of this dispatch, or the writing of the report to another agent; the only sub-agents you may spawn are the ones your skill's own process calls for.

## Files

- Skill snapshot: `{SKILL_DIR}/` — read `SKILL.md` first, in full, then the references it names, from this directory only; ignore any other installed copy of a review skill. Run its scripts from this directory (`python3 {SKILL_DIR}/scripts/<name>.py`).
- Phase-1 packet: `{PACKET}` — the "pin the review" step already done for you. Use its pinned values verbatim; do not re-resolve anything. Its last section lists the binding run conditions.
- Clone: `{CLONE}` — offline; local branch `{BASE_BRANCH}` is pinned to the merge-base, local branch `review-head` is checked out at the head. Use `git diff {BASE_BRANCH} review-head` for the change and `git show {BASE_BRANCH}:<path>` for base versions. History is truncated at the head.
- Your working directory for payload JSON, scratch files, any private store, and script output: `{WORK}/` (it exists). Never write inside the clone.
- **Review payload:** write it to `{PAYLOAD}` — the review exactly as it would be published: summary body (with the `Mode` line for a merged target), every finding, question, and observation comment with its trailer, and nothing else.
- **Research report:** write it to `{REPORT}` — everything listed under "What to report" below. Link to the payload file from the report instead of pasting it.
- **Timing sidecar:** `{TIMING}` already exists. Immediately after `validate_review.py` exits 0 on your final payload, run `python3 /tmp/qual137/mark_event.py {TIMING} payload_validated_at`; if you change the payload and validate again later, run it again after that validation. Do not edit the file by hand and do not write any other event.

## Rules for this cell

1. Follow your skill as written: its phase order, its read discipline, its verification triggers, its output contract. Do not borrow behavior from any other review skill, and do not supplement it with review practices it does not itself specify.
2. This is a **retrospective review of a merged pull request by a third party** (posting identity `kamui`, not the author); publication is disabled. Derive the status as for an open pull request, event `COMMENT`, and include the `Mode` line your contract requires. Where a step says "publish", render instead and stop.
3. Compute the `context` digest **once**, as your contract specifies; do not run the skill's self-tests inside this cell.
4. Clone hygiene: do not run `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the tree, and instruct every sub-agent the same. If a tree is mutated anyway, run `git -C {CLONE} reset --hard review-head` and disclose it.
5. **Execution allowance for this target.** {EXEC_NOTE}
6. **Persist before you verify.** Write the report file in stages: the manifest and requirement ledger when they are complete; the complete candidate ledger with every disposition before dispatching any verifier; each verifier prompt and its verbatim report as they arrive. Update the file as you go. Where your skill prescribes when the private record is written, that prescription governs the review; this rule governs only the research report file.
7. Stay inside your own sandbox: the clone, the skill snapshot, the packet directory, and your work, payload, report, and timing paths. Report any other path you read.
8. Sub-agents you spawn get the same rules 1–7 in their prompt, plus rule 9 below, `model: "sonnet"`, and the `subagent_type` named above.
9. No session relays: finish in this dispatch. Do not stop to ask anyone anything; if an input is genuinely missing, apply your skill's incomplete-coverage rule and say so in the report.
10. **Dispatch every sub-agent in the foreground** (`run_in_background: false`) and wait for its result before continuing. Never end your turn while a sub-agent of yours is still running, and never end your turn before the report and payload files are complete.

## What to report (the report file; be exhaustive — it is the only record of this cell)

1. **Metadata:** target, cell, attempt; skill snapshot directory and the `workflow` identifier its validator reports; the model you ran on and the model each sub-agent ran on (state each explicitly); which verification trigger fired, if any, and quote the sentence in your skill that made it fire; sub-agents spawned (role, count, `subagent_type`); candidates raised, candidates surviving your own falsification; verifier verdicts; findings for publication with priority/action; questions; observations; coverage (every file and check inspected); derived status; your own token usage if the harness reports it, otherwise say it does not.
2. **Every finding that survives**, in full: priority/action, anchor, fix location, claim, verification status and evidence, trigger scenario.
3. **The complete private disposition ledger:** one row per candidate raised, with kind, disposition, decisive evidence pointer, and falsification reason — including every candidate dropped or acquitted. For each row, state whether a verifier ever ruled on it, and if not, which rule in your skill did or did not require that.
4. **Every sub-agent dispatch:** the exact prompt given and the verbatim report returned.
5. **Everything consulted beyond the diff:** every file, command, and search, quoted, with whether each search was repo-wide and case-insensitive; every focused test or repro command run, with its exit status, duration, and output summary.
6. **The `context` digest** and the inputs it was computed from (title, body, issue coordinates, `comments_available`, guidance list).
7. **Mechanism checklist**, each item with a pointer to where in the run it is demonstrated or "did not fire", plainly: question channel; clean-verdict or related-acquittal verification (which mode, which rows, any re-open); observations; fix-sufficiency check on any concurrency/invariant candidate; follow-up verifier round; deferral handling (any explicit deferral in the review record and how it was treated); retrospective mode; and — if your skill defines one — early dispatch of the verifier batch, with the exact moment it was dispatched relative to the falsification pass.
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
"""close_cell.py <target> <cell> <attempt>
Finds the cell's session transcript (root = primary) and every sub-agent transcript, scans
message.model and effort on every assistant line, meters billed usage, writes <cell>-<attempt>-meta.json.
Both arms of issue #137 run claude-sonnet-5 at effort high on the primary and on every child."""
import argparse, glob, json, os, subprocess
B = "/tmp/qual137"
USAGE = "/Users/jack/.t3/worktrees/skills/t3code-e30d085b/docs/research/tools/transcript_usage.py"
PROJ = os.path.expanduser("~/.claude/projects/-private-tmp-qual137-sessions")

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
a = ap.parse_args()
pre = f"{B}/reports/{a.target}/{a.cell}-{a.attempt}"
sid = open(pre + "-session.txt").read().strip()
root = f"{PROJ}/{sid}.jsonl"; subs = sorted(glob.glob(f"{PROJ}/{sid}/subagents/agent-*.jsonl"))
agents = [{"role": "primary (session root)", "path": root, "definition": "--effort high", **scan(root)}]
for s in subs:
    meta = {}
    try: meta = json.load(open(s.replace(".jsonl", ".meta.json")))
    except Exception: pass
    agents.append({"role": "child", "path": s, "definition": meta.get("agentType"), "description": meta.get("description"), **scan(s)})
problems = []
for ag in agents:
    if set(ag["models"]) != {"claude-sonnet-5"}: problems.append(f"{ag['path']}: models {ag['models']}")
    if set(ag["efforts"]) != {"high"}: problems.append(f"{ag['path']}: efforts {ag['efforts']} (expected high)")
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

## `dispatch_record.sh`

````sh
#!/bin/sh
# dispatch_record.sh <attempt> <cell> <expected> <spent> <inflight-before> <inflight-after> [note]
set -eu
B=/tmp/qual137
printf '| %s | %s | %s; attempt %s of 26; $%s spent of $150; quota `unknown`; expected %s; in flight %s→%s%s | | | | | |\n' \
  "$1" "$2" "$(date -u +%H:%M:%SZ)" "${1#att-}" "$4" "$3" "$5" "$6" "${7:+; $7}" >> "$B/ledger-rows.md"
tail -1 "$B/ledger-rows.md"
````

## `pair.sh`

````sh
#!/bin/sh
# pair.sh <t1> <arm1> <seed1> <att1> <t2> <arm2> <seed2> <att2>
set -eu
B=/tmp/qual137
nohup "$B/run_cell.sh" "$1" "$2" "$3" "$4" > "$B/logs/runner-$4.log" 2>&1 &
P1=$!
sleep 3
nohup "$B/run_cell.sh" "$5" "$6" "$7" "$8" > "$B/logs/runner-$8.log" 2>&1 &
P2=$!
echo "dispatched $4 (pid $P1) and $8 (pid $P2) at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
````

## `meter.sh`

````sh
#!/bin/sh
# meter.sh <session-id> [label] [project-dir-slug]: one usage row over a session root and its sub-agents
P=$HOME/.claude/projects/${3:--private-tmp-qual137-sessions}
U=/Users/jack/.t3/worktrees/skills/t3code-e30d085b/docs/research/tools/transcript_usage.py
set -- "$P/$1.jsonl" $(find "$P/$1/subagents" -name 'agent-*.jsonl' 2>/dev/null) --prices 2,10 --row "${2:-$1}"
python3 "$U" "$@" 2>&1 | tail -1
````

## `blind.py`

````python
#!/usr/bin/env python3
"""blind.py seal <out-dir> <payload>...: copy payloads under random tokens, write a sealed mapping.
blind.py reveal <out-dir>: print the mapping.
Cell, attempt, snapshot-path and workflow identifiers are redacted so the scorer cannot see the arm."""
import json, os, re, secrets, sys
mode, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
mp = os.path.join(out, "mapping.sealed.json")
if mode == "seal":
    m = json.load(open(mp)) if os.path.exists(mp) else {}
    for p in sys.argv[3:]:
        tok = "blind-" + secrets.token_hex(3)
        while tok in m: tok = "blind-" + secrets.token_hex(3)
        txt = open(p, encoding="utf-8").read()
        txt = re.sub(r"[a-z]-(bea6be14|867cf3ff)-seed\d-att-\d\d", "CELL", txt)
        txt = re.sub(r"\b(bea6be14|867cf3ff)\w*", "SNAPSHOT", txt)
        txt = re.sub(r"\batt-\d\d\b", "ATT", txt)
        txt = re.sub(r"workflow=v5b-\d+", "workflow=WORKFLOW", txt)
        open(os.path.join(out, tok + ".md"), "w", encoding="utf-8").write(txt)
        m[tok] = os.path.abspath(p)
    json.dump(m, open(mp, "w"), indent=2); print("sealed", len(sys.argv) - 3, "payloads;", len(m), "total")
else:
    for k, v in sorted(json.load(open(mp)).items()): print(k, v)
````

## `aggregate.py`

````python
#!/usr/bin/env python3
"""Aggregate cost/timing views over closed-out cells: per-arm medians, matched pair ratios, totals."""
import json, glob, statistics as st
B = "/tmp/qual137/reports"
ARMS = ("bea6be14", "867cf3ff")
cells = {}
for mp in sorted(glob.glob(f"{B}/*/*-meta.json")):
    m = json.load(open(mp)); cell = m["cell"]
    t, arm, seed = cell.split("-")[0], cell.split("-")[1], int(cell[-1])
    u = json.loads(m["usage_json"]); tot = u["total"]; tim = u.get("timing", {})
    cells.setdefault((t, arm, seed), {"atts": [], "cost": 0.0})
    c = cells[(t, arm, seed)]
    c["atts"].append(m["attempt"]); c["cost"] += tot["cost"]
    c.update({"prod": tot.get("production_shaped_cost"), "think": tot.get("thinking"), "out": tot.get("output"),
              "turns": tot.get("turns"), "tools": tot.get("tool_calls"),
              "e2p": tim.get("elapsed_to_payload_seconds"), "e2c": tim.get("elapsed_to_completion_seconds"),
              "span": tot.get("agent_span_sum_seconds"), "n_agents": len(m["agents"])})
def med(v):
    v = [x for x in v if x is not None]; return round(st.median(v), 3) if v else None
print("cell rows (cost is all-attempt for the cell):")
for k in sorted(cells): print(k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in cells[k].items()})
print("\nper-arm medians (all targets):")
for arm in ARMS:
    v = [c for k, c in cells.items() if k[1] == arm]
    if v: print(arm, "n", len(v), "cost", med([c["cost"] for c in v]), "think", med([c["think"] for c in v]),
                "out", med([c["out"] for c in v]), "turns", med([c["turns"] for c in v]),
                "tools", med([c["tools"] for c in v]), "e2c", med([c["e2c"] for c in v]))
targets = sorted({k[0] for k in cells})
print("\nper-target medians:")
for t in targets:
    for arm in ARMS:
        v = [c for k, c in cells.items() if k[0] == t and k[1] == arm]
        if v: print(t, arm, "n", len(v), "cost", med([c["cost"] for c in v]), "e2c", med([c["e2c"] for c in v]))
print("\nmatched pairs (candidate bea6be14 / control 867cf3ff):")
ratios, fresh = [], []
for (t, arm, seed), c in sorted(cells.items()):
    if arm == "867cf3ff" and (t, "bea6be14", seed) in cells:
        cand = cells[(t, "bea6be14", seed)]["cost"]
        r = cand / c["cost"]; ratios.append(r)
        print(t, seed, round(cand, 2), round(c["cost"], 2), round(r, 3))
if ratios: print("matched median ratio", round(st.median(ratios), 3), "n", len(ratios))
tot = sum(c["cost"] for c in cells.values())
print("\ncells all-attempt total", round(tot, 2),
      "per arm", {a: round(sum(c["cost"] for k, c in cells.items() if k[1] == a), 2) for a in ARMS})
````

## `extract_requests.py`

Added after the pull-request review to make the metering evidence durable; see [`metering/README.md`](metering/README.md). Run once per attempt and once per helper session over the session root and every sub-agent transcript.

````python
#!/usr/bin/env python3
"""extract_requests.py <out.jsonl> <transcript.jsonl>...
One record per unique API request across the given transcripts: request id, message id, model,
effort, first/last timestamp, and the usage fields the billing arithmetic uses. A streamed request
appears on several assistant lines with identical usage; the per-request record keeps the maximum
of every counter, the same rule transcript_usage.py applies, so summing this file reproduces its
totals. Lines that are not assistant turns, or carry no usage, are skipped and counted."""
import json, os, sys
out, paths = sys.argv[1], sys.argv[2:]
reqs, order, skipped = {}, [], 0
for p in paths:
    label = os.path.basename(p)
    for line in open(p, encoding="utf-8"):
        try: o = json.loads(line)
        except Exception: skipped += 1; continue
        if o.get("type") != "assistant": continue
        m = o.get("message") or {}; u = m.get("usage")
        rid = o.get("requestId")
        if not u or not rid: skipped += 1; continue
        cc = u.get("cache_creation") or {}
        rec = {"request_id": rid, "message_id": m.get("id"), "transcript": label, "model": m.get("model"),
               "effort": o.get("effort"), "first_seen": o.get("timestamp"), "last_seen": o.get("timestamp"),
               "input_tokens": u.get("input_tokens", 0), "cache_creation_input_tokens": u.get("cache_creation_input_tokens", 0),
               "cache_write_5m": cc.get("ephemeral_5m_input_tokens"), "cache_write_1h": cc.get("ephemeral_1h_input_tokens"),
               "cache_read_input_tokens": u.get("cache_read_input_tokens", 0), "output_tokens": u.get("output_tokens", 0),
               "thinking_tokens": (u.get("output_tokens_details") or {}).get("thinking_tokens"), "service_tier": u.get("service_tier")}
        if rid not in reqs:
            reqs[rid] = rec; order.append(rid)
        else:
            r = reqs[rid]
            for k in ("input_tokens", "cache_creation_input_tokens", "cache_write_5m", "cache_write_1h",
                      "cache_read_input_tokens", "output_tokens", "thinking_tokens"):
                a, b = r.get(k), rec.get(k)
                r[k] = max(x for x in (a, b) if x is not None) if (a is not None or b is not None) else None
            r["last_seen"] = rec["last_seen"]
            if r["model"] != rec["model"] or r["effort"] != rec["effort"]:
                r.setdefault("inconsistent", []).append({"model": rec["model"], "effort": rec["effort"]})
with open(out, "w", encoding="utf-8") as f:
    for rid in order: f.write(json.dumps(reqs[rid]) + "\n")
print(f"{out}: {len(order)} requests from {len(paths)} transcript(s); {skipped} non-usage lines skipped")
````

## `provision.sh`

````sh
#!/bin/sh
# provision.sh <letter> <staging-repo.git> <head> <merge-base> <base-branch> <neg-shas...>
set -eu
B=/tmp/qual137
L=$1; S=$B/staging/$2; HEAD=$3; MB=$4; BR=$5; shift 5
rm -rf $B/mirrors/$L.git; git init -q --bare $B/mirrors/$L.git
git -C $S push -q $B/mirrors/$L.git "$HEAD:refs/heads/review-head" "$MB:refs/heads/$BR"
git -C $B/mirrors/$L.git symbolic-ref HEAD "refs/heads/$BR"
echo "--- ($L) mirror refs ---"; git -C $B/mirrors/$L.git for-each-ref --format='%(refname) %(objectname)'
for s in "$@"; do
  git -C $S cat-file -e "$s" 2>/dev/null && echo "staging has $s (expected)" || echo "staging MISSING $s (check the sha)"
  if git -C $B/mirrors/$L.git cat-file -e "$s" 2>/dev/null; then echo "LEAK $s in mirror"; exit 1; else echo "mirror absent $s"; fi
done
echo "newest reachable from review-head: $(git -C $B/mirrors/$L.git log --format='%cI' review-head | sort | tail -1)"
echo "head date:                        $(git -C $B/mirrors/$L.git log -1 --format='%cI' review-head)"
````

## `targets/i.sh`

````sh
LABEL="(i) psf/requests#6667"
REPO_PR="psf/requests#6667"
BASE_BRANCH=main
MERGE_BASE=8dd3b26bf59808de24fd654699f592abf6de581e
HEAD_SHA=4089f3dc65f783beaa53cc032958ab625440d0ac
PACKET=/tmp/qual137/packets/i/packet.md
NEG_SHAS="9a40d1277807f0a4f26c9a37eea8ec90faa8aadc 145b5399486b56e00250204f033441f3fdf2f3c9 90fee0876aea97c639b3bf698d83a12876d2f160 11d68c17bcd66bd3e2c5137b0a7aad7f59967102"
EXEC_NOTE="Focused test execution IS permitted on this target, offline, exactly as the packet's section 8 states: run pytest from the clone root with the pre-provisioned virtualenv, as PYTHONPATH=<clone>/src /tmp/qual137/venvs/requests/bin/python -m pytest <selection>; five minutes per command, a selection at most once per flag set, scratch files only under your work directory, nothing added to or changed in the clone. The virtualenv has no network access and its packages are already installed."
````

## `targets/j.sh`

````sh
LABEL="(j) trpc/trpc#5017"
REPO_PR="trpc/trpc#5017"
BASE_BRANCH=main
MERGE_BASE=2abb2d5cd19740be37272dac6ad7fdd36244ae54
HEAD_SHA=7dc04a7e94654dfad6ef1289dfe01a0a206fff3b
PACKET=/tmp/qual137/packets/j/packet.md
NEG_SHAS="f27d50c774908059e263bbbf25e20a782f6faa89 a2a14f0fb131bc8f06573a62d18bdd6f920a120b de8589879a461dc107402cd2fb1b06919a6c1c69 afa9ad92288f26427623cd0efd0daaae6fb61775"
POST_CLONE='PNPM_HOME=/tmp/qual137/pnpm-home corepack pnpm install --frozen-lockfile --offline --store-dir /tmp/qual137/pnpm-store'
EXEC_NOTE="Focused type-checking IS permitted on this target, offline, exactly as the packet's section 8 states: dependencies are already installed in the clone (they are untracked and ignored; leave them alone). Run the TypeScript compiler with the clone's own binary, for example \`cd <clone>/packages/tests && ./node_modules/.bin/tsc --noEmit -p tsconfig.json\` (about 5 seconds); five minutes per command, a configuration at most once per flag set. Write any scratch TypeScript you want to typecheck under your work directory and point tsc at it from there; nothing may be added to or changed in the clone, and no network call of any kind is available (npx and pnpm cannot reach a registry)."
````

## `targets/k.sh`

````sh
LABEL="(k) graphql/graphql-js#1582"
REPO_PR="graphql/graphql-js#1582"
BASE_BRANCH=master
MERGE_BASE=5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11
HEAD_SHA=7e39a122eea9292eeffa6905ffdf8a60c5161cfd
PACKET=/tmp/qual137/packets/k/packet.md
NEG_SHAS="f0ae3f4c0ba469c8f2147f8d12c9e670313b865c 8d621b00f7513194bce4a4b2f48d402a4da404bd 25680d28f749a3e48362c355e1d3a2668d845006"
POST_CLONE='npm install --no-audit --no-fund --offline --cache /tmp/qual137/npm-cache >/dev/null 2>&1; git checkout -- yarn.lock 2>/dev/null; rm -f package-lock.json'
EXEC_NOTE="Focused test execution IS permitted on this target, offline, exactly as the packet's section 8 states: dependencies are already installed in the clone (they are untracked and ignored; leave them alone). Run mocha with the clone's own binary, for example ./node_modules/.bin/mocha --require @babel/register --require @babel/polyfill <test file> (about 2 seconds); five minutes per command, a selection at most once per flag set. Write any scratch JavaScript under your work directory; nothing may be added to or changed in the clone, and no network call of any kind is available (npm and npx cannot reach a registry)."
````

## `targets/l.sh`

````sh
LABEL="(l) bokeh/bokeh#9232"
REPO_PR="bokeh/bokeh#9232"
BASE_BRANCH=master
MERGE_BASE=ccb4bcb4c2b841d89b0e88303a97bf4604a5795f
HEAD_SHA=36549bca3a63d581f7b68d08054a7813c1e6a499
PACKET=/tmp/qual137/packets/l/packet.md
NEG_SHAS="ec1e525c9a8ad128e29b3b74beb732e79a0db437 ec557b685bf941658b0a569db2ee4ae4d917045e 16d3d0efcc91a4206be0c3f11ede33f9fc03cda9"
EXEC_NOTE="Focused execution IS permitted on this target, offline and outside the clone, exactly as the packet's section 8 states: node (v24.19.0) is installed and you may write and run scratch JavaScript under your work directory, including with a TZ environment variable set, to check the behaviour of code you have read; five minutes per command. The project's own build and its Selenium integration suite are NOT available (no browser, no npm install, no network) — do not attempt them. Nothing may be added to or changed in the clone."
````

## `targets/m.sh`

````sh
LABEL="(m) grpc/grpc-go#7390"
REPO_PR="grpc/grpc-go#7390"
BASE_BRANCH=master
MERGE_BASE=daab56344e612097fd50c46c433de5d9b6013837
HEAD_SHA=76ef33f44a600c3ed1a385979fd1dfbcade3fbb6
PACKET=/tmp/qual137/packets/m/packet.md
NEG_SHAS="45d44a736ec6cdcb73f9411bf6a1c2d1abea1956"
EXEC_NOTE="Focused test execution IS permitted on this target, offline, exactly as the packet's section 8 states: go commands from the clone root with GOMODCACHE=/tmp/qual137/gomodcache GOCACHE=/tmp/qual137/gocache GOFLAGS=-mod=mod GOPROXY=off; five minutes per command, a package's tests at most once per flag set, scratch modules only under your work directory, nothing added to or changed in the clone."
````

## `targets/n.sh`

````sh
LABEL="(n) BurntSushi/ripgrep#2957"
REPO_PR="BurntSushi/ripgrep#2957"
BASE_BRANCH=master
MERGE_BASE=79cbe89deb1151e703f4d91b19af9cdcc128b765
HEAD_SHA=855bfa6cdae4f4fe8762f892fc4957635397083e
PACKET=/tmp/qual137/packets/n/packet.md
NEG_SHAS="94305125ef33b86151b6cd2ce2b33d641f6b6ac3"
EXEC_NOTE="Focused execution IS permitted on this target, offline and outside the clone, exactly as the packet's section 8 states: zsh is installed and you may write and run scratch zsh scripts under your work directory to check the behaviour of shell code you have read; five minutes per command. Building the Rust crate is NOT available (no network, no vendored registry) — do not attempt cargo build or cargo test. Nothing may be added to or changed in the clone."
````

## Packet builds

Each packet was built once with the shipped `build_packet.py`, from the target's staging clone.
Every build passed the tool's provenance validation; target (l) carries the earlier cutoff explained
in the README's §1.2 and every other target used the default merge-time cutoff. Common arguments to
all six: `--experiment-label "issue #137 qualification grid" --subagent-model sonnet`, plus the
target's `--execution-note` (reproduced verbatim in that target's `targets/<letter>.sh` above, as
`EXEC_NOTE`).

````sh
B=/tmp/qual137

python3 docs/research/tools/build_packet.py --repo psf/requests --pr 6667 \
  --head 4089f3dc65f783beaa53cc032958ab625440d0ac \
  --merge-base 8dd3b26bf59808de24fd654699f592abf6de581e \
  --base-sha  8dd3b26bf59808de24fd654699f592abf6de581e \
  --staging $B/staging/requests.git --target i --out $B/packets/i/packet.md
# cutoff 2024-05-15T20:07:26Z; omitted after cutoff: 1 review, 11 conversation comments

python3 docs/research/tools/build_packet.py --repo trpc/trpc --pr 5017 \
  --head 7dc04a7e94654dfad6ef1289dfe01a0a206fff3b \
  --merge-base 2abb2d5cd19740be37272dac6ad7fdd36244ae54 \
  --base-sha  2abb2d5cd19740be37272dac6ad7fdd36244ae54 \
  --staging $B/staging/trpc.git --target j --out $B/packets/j/packet.md
# cutoff 2023-11-10T10:08:08Z; nothing omitted

python3 docs/research/tools/build_packet.py --repo graphql/graphql-js --pr 1582 \
  --head 7e39a122eea9292eeffa6905ffdf8a60c5161cfd \
  --merge-base 5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11 \
  --base-sha  5384d218539dbb6bb39b25e0b7a5dcdd69ad8a11 \
  --staging $B/staging/graphql-js.git --target k --out $B/packets/k/packet.md
# cutoff 2018-11-21T14:33:19Z; nothing omitted

python3 docs/research/tools/build_packet.py --repo bokeh/bokeh --pr 9232 \
  --head 36549bca3a63d581f7b68d08054a7813c1e6a499 \
  --merge-base ccb4bcb4c2b841d89b0e88303a97bf4604a5795f \
  --base-sha  ccb4bcb4c2b841d89b0e88303a97bf4604a5795f \
  --staging $B/staging/bokeh.git --target l --cutoff 2019-10-03T15:51:00Z \
  --out $B/packets/l/packet.md
# at the merge instant this build refuses:
#   required input unavailable: conversation #9: lastEditedAt is after the cutoff; historical text unavailable
# with the 62-seconds-earlier cutoff: omitted 4 conversation, 2 issue comments

python3 docs/research/tools/build_packet.py --repo grpc/grpc-go --pr 7390 \
  --head 76ef33f44a600c3ed1a385979fd1dfbcade3fbb6 \
  --merge-base daab56344e612097fd50c46c433de5d9b6013837 \
  --base-sha  daab56344e612097fd50c46c433de5d9b6013837 \
  --staging $B/staging/grpc-go.git --target m --out $B/packets/m/packet.md
# cutoff 2024-07-09T20:27:27Z; nothing omitted

python3 docs/research/tools/build_packet.py --repo BurntSushi/ripgrep --pr 2957 \
  --head 855bfa6cdae4f4fe8762f892fc4957635397083e \
  --merge-base 79cbe89deb1151e703f4d91b19af9cdcc128b765 \
  --base-sha  79cbe89deb1151e703f4d91b19af9cdcc128b765 \
  --staging $B/staging/ripgrep.git --target n --out $B/packets/n/packet.md
# cutoff 2024-12-31T13:23:13Z; omitted 2 conversation comments
````

The rejected candidate `quic-go/quic-go#5220` failed the same tool at the merge instant and no
packet was written:

````
required input unavailable: conversation #1: lastEditedAt is after the cutoff; historical text unavailable
````

## Context-build size and arm-identity check

Run on a fresh clone of each mirror, with both arms' own `review_context.py`, before the freeze.
Criterion 5 requires the output to be at most 24,000 bytes and byte-identical between the arms.

````sh
for L in i j k l m n; do
  C=$B/transport-check/$L
  H=$(git -C $C rev-parse review-head); MB=$(git -C $C rev-parse $BASE_BRANCH)
  for ARM in 867cf3ff bea6be14; do
    (cd $C && python3 $B/snapshots/$ARM/skills/code-review-publish/scripts/review_context.py \
        --merge-base $MB --head $H > $B/transport-check/$L-$ARM.txt)
  done
  cmp -s $B/transport-check/$L-867cf3ff.txt $B/transport-check/$L-bea6be14.txt \
    && echo "$L identical $(wc -c < $B/transport-check/$L-bea6be14.txt)" || echo "$L DIFFER"
done
# i identical 22095 / j identical 3620 / k identical 18831
# l identical  7374 / m identical 6305 / n identical 13253
# rejected: cockroachdb/pebble#5743 identical 41976 — over the 24,000-byte criterion
````

## Blind scoring and adjudication prompts

The scorer prompt template, the six per-target renderings, the six ground-truth adjudicator prompts
and the post-grid GT-n1 adjudication brief were all rendered from templates with the target's
coordinates substituted. The GT-n1 brief is quoted in full inside
[`adjudication/nc1-ruling.md`](adjudication/nc1-ruling.md)'s companion record; the scorer template's
operative rules — the definitions of material defect, recovery, false finding and false clean, and
the instruction not to compare or identify reviews — are reproduced in the README's §2.
