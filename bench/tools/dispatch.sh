#!/bin/sh
# Dispatch one benchmark attempt of a built-in reviewer arm under a fresh home.
#
# Usage: dispatch.sh <arm> <attempt-dir> <clone> <base-branch> <packet-file> [model] [effort]
#   arm         claude-builtin | codex | review-code
#               review-code: SKILL_TREE=<path to the pinned skills/review-code tree> must be exported; it is
#               copied into the fresh home as its only user skill and invoked through the Skill tool.
#               SKILL_TREE_ID=<tree sha> records the tree when SKILL_TREE is an extracted archive of it
#               (run_cell.py); otherwise the tree is read from the git checkout SKILL_TREE sits in.
#   attempt-dir new directory for this attempt; must not be under /tmp (Codex refuses PATH helpers there)
#   clone       offline clone with <base-branch> at the merge-base and review-head checked out.
#               For claude-builtin the base branch MUST be named `main`: the built-in's Phase 0 runs
#               `git diff main...HEAD` regardless of the range argument (observed on 2.1.281), so the
#               pinned range is honoured only when `main` is the merge-base and HEAD is review-head.
#   packet-file phase-1 packet text, given to the reviewer verbatim after the range instruction
#   model       claude-builtin only: value for --model (e.g. sonnet, opus); omitted = harness default
#   effort      claude-builtin only: passed both as the session `--effort` and as the built-in's argument;
#               the variant is selected from the session effort (an argument alone left Opus on `low`).
#               Omitted = harness default (low variant).
#
# Writes under <attempt-dir>: home/ (fresh HOME; its credential copy is deleted at exit), tmp/ (TMPDIR), timing.json, stdout.*, stderr.txt, tree-before.txt,
# tree-after.txt, dispatch.txt (the exact command and versions), audit.json, payload.json (claude arms), normalized.json.
#
# Timing semantics: timing.json gets root_dispatched_at before the CLI starts; after a zero exit the wrapper runs the
# read audit (claude arms, which also extracts payload.json) and the normalizer, which stamps payload_validated_at on a
# parsed or empty result; only then is completed_at written. Any other outcome writes stop.json with stopped_at and
# the reason and leaves completed_at null. Metering is left to the caller:
#   claude-builtin: python3 attempt_audit.py --arm claude-builtin --attempt-dir <dir> --clone <clone>
#                   python3 docs/research/tools/transcript_usage.py <dir>/home/.claude/projects/*/*/subagents/*.jsonl --prices ...
#   codex:          python3 attempt_audit.py --arm codex --attempt-dir <dir> --clone <clone>
#                   python3 docs/research/tools/codex_usage.py --sessions-dir <dir>/home/.codex/sessions --session <id> --prices ...
# Exit: the reviewer CLI's exit code; 2 for a usage or setup error.
set -eu
ARM=${1:?arm}; DIR=${2:?attempt-dir}; CLONE=${3:?clone}; BASE=${4:?base-branch}; PACKET=${5:?packet}; MODEL=${6:-}; EFFORT=${7:-}
case "$DIR" in /tmp/*) echo "attempt-dir must not be under /tmp" >&2; exit 2;; esac
[ -d "$CLONE/.git" ] || { echo "not a clone: $CLONE" >&2; exit 2; }
[ -f "$PACKET" ] || { echo "no packet: $PACKET" >&2; exit 2; }
mkdir -p "$DIR/home" "$DIR/tmp"; DIR=$(cd "$DIR" && pwd); H="$DIR/home"; CLONE=$(cd "$CLONE" && pwd)
# Every arm's scratch and private stores land inside the attempt directory, so the read audit's allowed roots cover them.
TMPDIR="$DIR/tmp"; export TMPDIR
stamp() { python3 -c 'from datetime import datetime,timezone; print(datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z"))'; }
tree_id() { { git -C "$CLONE" rev-parse HEAD; git -C "$CLONE" status --porcelain --untracked-files=all; } | sha256sum | cut -d' ' -f1; }
tree_id > "$DIR/tree-before.txt"
case "$ARM" in
  claude-builtin)
    mkdir -p "$H/.claude"; cp "$HOME/.claude/.credentials.json" "$H/.claude/"
    python3 - "$HOME/.claude.json" "$H/.claude.json" <<'PY'
import json, sys
src = json.load(open(sys.argv[1], encoding="utf-8"))
keep = {k: src[k] for k in ("oauthAccount", "userID", "installMethod", "autoUpdates", "numStartups") if k in src}
keep["hasCompletedOnboarding"] = True
json.dump(keep, open(sys.argv[2], "w", encoding="utf-8"), indent=2)
PY
    [ "$BASE" = "main" ] || { echo "claude-builtin requires the base branch to be named main" >&2; exit 2; }
    SID=$(python3 -c 'import uuid; print(uuid.uuid4())'); printf '%s\n' "$SID" > "$DIR/session-id.txt"
    PROMPT="/code-review $BASE...review-head${EFFORT:+ $EFFORT}

$(cat "$PACKET")"
    printf '%s\n' "$PROMPT" > "$DIR/prompt.txt"
    { echo "claude $(claude --version)"; echo "model=${MODEL:-<default>} effort=${EFFORT:-<default>} session=$SID"; } > "$DIR/dispatch.txt"
    printf '{"completion_mode": "render-only", "root_dispatched_at": "%s", "payload_validated_at": null, "completed_at": null}\n' "$(stamp)" > "$DIR/timing.json"
    set +e
    ( cd "$CLONE" && HOME="$H" CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 timeout 5400 claude -p --safe-mode --session-id "$SID" \
        ${MODEL:+--model "$MODEL"} ${EFFORT:+--effort "$EFFORT"} --max-budget-usd 15 --allowedTools "Bash,Read,Glob,Grep,Agent" \
        --output-format stream-json --verbose "$PROMPT" < /dev/null > "$DIR/stdout.jsonl" 2> "$DIR/stderr.txt" )
    RC=$?; set -e
    ;;
  codex)
    mkdir -p "$H/.codex"; cp "$HOME/.codex/auth.json" "$H/.codex/"
    printf '[projects."%s"]\ntrust_level = "trusted"\n' "$CLONE" > "$H/.codex/config.toml"
    { printf 'Review scope: the changes that local branch `review-head` introduces relative to local branch `%s`. Obtain the diff with `git diff %s...review-head`; do not review uncommitted changes.\n\n' "$BASE" "$BASE"; cat "$PACKET"; } > "$DIR/prompt.txt"
    { echo "$(codex --version)"; echo "model=<default> effort=<default>"; } > "$DIR/dispatch.txt"
    printf '{"completion_mode": "render-only", "root_dispatched_at": "%s", "payload_validated_at": null, "completed_at": null}\n' "$(stamp)" > "$DIR/timing.json"
    set +e
    ( cd "$CLONE" && HOME="$H" CODEX_HOME="$H/.codex" timeout 5400 codex review -c 'sandbox_mode="workspace-write"' - \
        < "$DIR/prompt.txt" > "$DIR/stdout.txt" 2> "$DIR/stderr.txt" )
    RC=$?; set -e
    sed -n 's/^session id: //p' "$DIR/stderr.txt" | head -1 > "$DIR/session-id.txt"
    ;;
  review-code)
    [ -n "${SKILL_TREE:-}" ] && [ -f "$SKILL_TREE/SKILL.md" ] || { echo "SKILL_TREE must point at a review-code skill tree" >&2; exit 2; }
    mkdir -p "$H/.claude/skills"; cp -r "$SKILL_TREE" "$H/.claude/skills/review-code"; cp "$HOME/.claude/.credentials.json" "$H/.claude/"
    python3 - "$HOME/.claude.json" "$H/.claude.json" <<'PY'
import json, sys
src = json.load(open(sys.argv[1], encoding="utf-8"))
keep = {k: src[k] for k in ("oauthAccount", "userID", "installMethod", "autoUpdates", "numStartups") if k in src}
keep["hasCompletedOnboarding"] = True
json.dump(keep, open(sys.argv[2], "w", encoding="utf-8"), indent=2)
PY
    if [ -n "${SKILL_TREE_ID:-}" ]; then echo "$SKILL_TREE_ID"
    else (cd "$SKILL_TREE" && git rev-parse "HEAD:$(git rev-parse --show-prefix | sed 's,/$,,')" 2>/dev/null || echo unpinned); fi > "$DIR/skill-tree.txt"
    SID=$(python3 -c 'import uuid; print(uuid.uuid4())'); printf '%s\n' "$SID" > "$DIR/session-id.txt"
    mkdir -p "$DIR/artifacts"
    PROMPT="Invoke the \`review-code\` skill now with the Skill tool and these caller inputs: mode \`one-shot\`; profile \`publishable\`; return_format \`artifacts\`; target: the committed range from local branch \`$BASE\` (the base) to local branch \`review-head\` (the head) in the current repository, which is an offline clone; user-supplied spec: the pull-request text below; focused-test policy: the skill's defaults; no publication authorization and no forge access (there is no remote; never run gh, curl, or git fetch/pull/push). Dispatch every fresh-context worker the skill's references call for with the Agent tool using subagent_type general-purpose, model \`sonnet\`, and run_in_background false. Never modify the repository tree. When the skill returns, copy its private directory's \`composition.json\`, \`payload.json\`, and \`report.md\` to \`$DIR/artifacts/\` and print the finalizer's compact status and paths.

Pull-request text:

$(cat "$PACKET")"
    printf '%s\n' "$PROMPT" > "$DIR/prompt.txt"
    { echo "claude $(claude --version)"; echo "model=${MODEL:-sonnet} effort=${EFFORT:-high} session=$SID skill_tree=$(cat "$DIR/skill-tree.txt")"; } > "$DIR/dispatch.txt"
    printf '{"completion_mode": "render-only", "root_dispatched_at": "%s", "payload_validated_at": null, "completed_at": null}\n' "$(stamp)" > "$DIR/timing.json"
    set +e
    ( cd "$CLONE" && HOME="$H" CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 timeout 5400 claude -p --session-id "$SID" \
        --model "${MODEL:-sonnet}" --effort "${EFFORT:-high}" --max-budget-usd 15 --allowedTools "Bash,Read,Write,Edit,Glob,Grep,Agent,Skill" \
        --output-format stream-json --verbose "$PROMPT" < /dev/null > "$DIR/stdout.jsonl" 2> "$DIR/stderr.txt" )
    RC=$?; set -e
    ;;
  *) echo "unknown arm: $ARM" >&2; exit 2;;
esac
TOOLS=$(cd "$(dirname "$0")" && pwd)
stop() { printf '{"stopped_at": "%s", "exit_code": %s, "reason": "%s"}\n' "$(stamp)" "$RC" "$1" > "$DIR/stop.json"; echo "stopped: $1" >> "$DIR/dispatch.txt"; }
if [ "$RC" -ne 0 ]; then
  stop "reviewer exit $RC"
else
  set +e
  case "$ARM" in
    claude-builtin)
      python3 "$TOOLS/attempt_audit.py" --arm claude-builtin --attempt-dir "$DIR" --clone "$CLONE" > "$DIR/audit.txt" 2>&1
      python3 "$TOOLS/normalize_review.py" --arm claude-builtin --payload "$DIR/payload.json" --out "$DIR/normalized.json" --timing "$DIR/timing.json" > "$DIR/normalize.txt" 2>&1; NRC=$? ;;
    codex)
      python3 "$TOOLS/attempt_audit.py" --arm codex --attempt-dir "$DIR" --clone "$CLONE" > "$DIR/audit.txt" 2>&1
      python3 "$TOOLS/normalize_review.py" --arm codex --stdout "$DIR/stdout.txt" --sessions-dir "$H/.codex/sessions" --clone "$CLONE" --out "$DIR/normalized.json" --timing "$DIR/timing.json" > "$DIR/normalize.txt" 2>&1; NRC=$? ;;
    review-code)
      python3 "$TOOLS/attempt_audit.py" --arm review-code --attempt-dir "$DIR" --clone "$CLONE" > "$DIR/audit.txt" 2>&1
      if [ -s "$DIR/artifacts/composition.json" ]; then
        python3 "$TOOLS/normalize_review.py" --arm review-code --composition "$DIR/artifacts/composition.json" --clone "$CLONE" --out "$DIR/normalized.json" --timing "$DIR/timing.json" > "$DIR/normalize.txt" 2>&1; NRC=$?
      else
        echo "no artifacts/composition.json returned" > "$DIR/normalize.txt"; NRC=1
      fi ;;
  esac
  set -e
  if [ "$NRC" -eq 0 ]; then
    python3 - "$DIR/timing.json" "$(stamp)" <<'PY'
import json, sys
t = json.load(open(sys.argv[1], encoding="utf-8")); t["completed_at"] = sys.argv[2]
json.dump(t, open(sys.argv[1], "w", encoding="utf-8"), indent=2)
PY
  else
    stop "normalization exit $NRC: $(head -c 200 "$DIR/normalize.txt" | tr '\n' ' ')"
  fi
fi
tree_id > "$DIR/tree-after.txt"
# The fresh home held a copy of the credentials only for the run; scrub it so fixtures can be kept.
rm -f "$H/.claude/.credentials.json" "$H/.codex/auth.json"
if ! cmp -s "$DIR/tree-before.txt" "$DIR/tree-after.txt"; then echo "TREE MUTATED during attempt" >> "$DIR/dispatch.txt"; git -C "$CLONE" status --porcelain >> "$DIR/dispatch.txt"; fi
echo "exit=$RC" >> "$DIR/dispatch.txt"
exit $RC
