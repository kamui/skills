#!/bin/sh
# Collect one finished cell under protocol.md steps 4 and 5 into a committed evidence directory.
#
#   sh collect_cell.sh ROOT TASK SKILL_ROOT EVIDENCE OUT
#
# EVIDENCE is run_cell.sh's directory for the cell and OUT a new directory in the repository. OUT
# receives run.json, stdout.json, stderr.txt, gzip-compressed root and worker transcripts with the
# SHA-256 of each uncompressed file, the worker .meta.json files, effort.txt from agent_effort.py,
# metrics.json from interface_metrics.py, the cell's work/ directory, and any addendum the cell
# added beside the seeded chain. Exit 1 when the model or effort check fails; 2 on a missing input.
set -u
root=$1 task=$2 skill=$3 evidence=$4 out=$5
here=$(cd "$(dirname "$0")" && pwd)
tools=$here/../tools
[ -f "$evidence/transcript.jsonl" ] || { echo "collect_cell: no transcript in $evidence" >&2; exit 2; }
[ -e "$out" ] && { echo "collect_cell: refusing to overwrite $out" >&2; exit 2; }
mkdir -p "$out/subagents"
cp "$evidence/run.json" "$evidence/stdout.json" "$evidence/stderr.txt" "$out/"
session=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["session_id"])' "$out/run.json")
project=$HOME/.claude/projects/$(printf '%s' "$root/$task" | sed 's#[^A-Za-z0-9]#-#g')
workers=
for transcript in "$evidence"/subagents/*.jsonl; do
  [ -f "$transcript" ] || continue
  workers="$workers --worker $transcript"
  cp "$project/$session/subagents/$(basename "$transcript" .jsonl).meta.json" "$out/subagents/" 2> /dev/null
done
# shellcheck disable=SC2086
python3 "$tools/agent_effort.py" "$evidence/transcript.jsonl" $(printf '%s' "$workers" | sed 's/--worker //g') \
  --expect-model claude-sonnet-5 --expect-effort high > "$out/effort.txt"
effort=$?
# shellcheck disable=SC2086
python3 "$tools/interface_metrics.py" cell --transcript "$evidence/transcript.jsonl" $workers \
  --skill-root "$skill" --task-root "$root/$task" --result "$evidence/stdout.json" > "$out/metrics.json" || exit 2
for transcript in "$evidence/transcript.jsonl" "$evidence"/subagents/*.jsonl; do
  [ -f "$transcript" ] || continue
  case $transcript in */subagents/*) target=$out/subagents/$(basename "$transcript") ;; *) target=$out/transcript.jsonl ;; esac
  python3 -c 'import hashlib, os, sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest() + "  " + os.path.basename(sys.argv[1]))' \
    "$transcript" > "$target.sha256"
  gzip -9nc "$transcript" > "$target.gz"
done
cp -R "$root/$task/work" "$out/work"
python3 "$tools/savings_archive.py" check "$here/archive" --root "$root" > "$out/archive-check.txt" 2>&1
for addendum in "$root/$task"/review/addenda/*.json; do
  [ -f "$addendum" ] || continue
  grep -q "review/addenda/$(basename "$addendum")" "$here/archive/tasks/$task/task.json" || \
    { mkdir -p "$out/addenda" && cp "$addendum" "$out/addenda/"; }
done
exit "$effort"
