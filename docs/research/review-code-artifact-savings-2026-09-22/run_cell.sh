#!/bin/sh
# Run one frozen interface cell under protocol.md and collect its evidence.
#
#   sh run_cell.sh ROOT TASK SKILL_ROOT OUT
#
# ROOT is a savings_archive.py realization, TASK one of its tasks, SKILL_ROOT the arm's installed
# review-code, and OUT a new directory for the cell's evidence. The session runs in ROOT/TASK with
# no user or project settings, CLAUDE.md, skills, plugins, hooks or MCP servers, and records the
# exact command, timestamps, harness result, root and worker transcripts. Exit status is the
# harness's own; collection still runs after a failed or capped session.
set -u
root=$1 task=$2 skill=$3 out=$4
if [ -e "$out" ]; then echo "run_cell: refusing to overwrite $out" >&2; exit 2; fi
mkdir -p "$out"
session=$(python3 -c 'import uuid; print(uuid.uuid4())')
cwd=$root/$task
cap=15
python_dir=$(dirname "$(python3 -c 'import sys; print(sys.executable)')")
set -- claude -p --session-id "$session" --model claude-sonnet-5 --effort high --safe-mode \
  --setting-sources "" --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --settings '{"disableAllHooks":true}' --permission-mode bypassPermissions \
  --disallowedTools WebFetch WebSearch --add-dir "$cwd" --add-dir "$skill" \
  --max-budget-usd "$cap" --output-format json
python3 - "$out/run.json" "$session" "$task" "$skill" "$cap" "$python_dir" "$@" <<'EOF'
import json, sys
path, session, task, skill, cap, python_dir, *command = sys.argv[1:]
json.dump({"session_id": session, "task": task, "skill_root": skill, "cap_usd": float(cap),
           "model": "claude-sonnet-5", "effort": "high", "path_prefix": python_dir,
           "command": command + ["<prompt.md>"]}, open(path, "w"), indent=2)
EOF
started=$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).isoformat())')
start_s=$(python3 -c 'import time; print(time.time())')
(cd "$cwd" && PATH="$python_dir:$PATH" timeout 3600 "$@" "$(cat prompt.md)" < /dev/null \
  > "$out/stdout.json" 2> "$out/stderr.txt")
status=$?
end_s=$(python3 -c 'import time; print(time.time())')
finished=$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).isoformat())')
project=$HOME/.claude/projects/$(printf '%s' "$cwd" | sed 's#[^A-Za-z0-9]#-#g')
cp "$project/$session.jsonl" "$out/transcript.jsonl" 2> /dev/null || echo "run_cell: no root transcript at $project" >&2
if [ -d "$project/$session/subagents" ]; then
  mkdir -p "$out/subagents" && cp "$project/$session/subagents/"*.jsonl "$out/subagents/" 2> /dev/null
fi
python3 - "$out/run.json" "$status" "$started" "$finished" "$start_s" "$end_s" <<'EOF'
import json, sys
path, status, started, finished, start_s, end_s = sys.argv[1:]
run = json.load(open(path))
run.update(exit_code=int(status), started_at=started, finished_at=finished,
           elapsed_seconds=round(float(end_s) - float(start_s), 3))
json.dump(run, open(path, "w"), indent=2)
EOF
exit "$status"
