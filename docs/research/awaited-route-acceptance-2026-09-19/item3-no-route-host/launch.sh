#!/bin/sh
# The exact launch used on 2026-09-19 (Claude Code 2.1.278, macOS). CLAUDE_CODE_FORK_SUBAGENT=1 turns fork
# mode on for a headless session, which removes the Agent tool's run_in_background parameter and runs every
# dispatch in the background. Nothing global was changed: both variables apply to this process only.
cd /tmp/i273/item3
CLAUDE_CODE_FORK_SUBAGENT=1 CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 timeout 2400 claude -p \
  --session-id 1d194fdc-cfc3-435c-a76d-c128d1953d90 --model claude-sonnet-5 --effort high \
  --allowedTools "Read" "Write" "Edit" "Skill" "Agent" "Glob" "Grep" "Bash(git:*)" "Bash(python3:*)" "Bash(ls:*)" \
    "Bash(cat:*)" "Bash(rg:*)" "Bash(sed:*)" "Bash(wc:*)" "Bash(head:*)" "Bash(tail:*)" "Bash(mkdir:*)" "Bash(cp:*)" \
    "Bash(tar:*)" "Bash(mktemp:*)" "Bash(date:*)" "Bash(sha256sum:*)" "Bash(shasum:*)" "Bash(pwd:*)" "Bash(find:*)" "Bash(fd:*)" \
  --permission-prompts none --add-dir /tmp/i273 --max-budget-usd 10 --output-format json "$(cat root-prompt.md)" \
  < /dev/null > result.json 2> stderr.log
