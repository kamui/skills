#!/bin/sh
# Run one exercise task under an isolated Codex home and record its event log.
#
#   sh run_task.sh ROOT TASK ISOLATED_HOME OUT
#
# ROOT is an `exercise.py prepare` root and TASK one of its tasks. ISOLATED_HOME holds only
# `.codex/auth.json` and a `.codex/config.toml` trusting ROOT, so no user skills, AGENTS.md or hooks
# load; it sits outside /tmp. The primary and any verifier it dispatches run gpt-6-sol at high
# effort. Exit status is codex's own.
set -u
root=$1 task=$2 home=$3 out=$4
if [ -e "$out" ]; then echo "run_task: refusing to overwrite $out" >&2; exit 2; fi
mkdir -p "$out"
start=$(date +%s)
HOME="$home" CODEX_HOME="$home/.codex" codex exec --json -m gpt-6-sol -c model_reasoning_effort=high \
  -s danger-full-access --skip-git-repo-check -C "$root/$task" -o "$out/last-message.md" - \
  < "$root/$task/prompt.md" > "$out/events.jsonl" 2> "$out/stderr.txt"
status=$?
end=$(date +%s)
printf '{"task": "%s", "exit": %s, "elapsed_seconds": %s, "model": "gpt-6-sol", "effort": "high"}\n' \
  "$task" "$status" "$((end - start))" > "$out/run.json"
exit "$status"
