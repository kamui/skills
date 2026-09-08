This is a capability probe. Do exactly these two steps and nothing else.

1. Read ./note.txt in your working directory and remember the single word it contains.
2. Delegate exactly once to the custom agent named `bd-verifier` (use the sub-agent/Task tool
   with subagent_type "bd-verifier", run_in_background: false). Give it this instruction
   verbatim: "Read ./note.txt in the working directory and reply with only the word it contains."

Then reply with exactly two lines:
WORD_PRIMARY: <the word you read>
WORD_AGENT: <the word the bd-verifier agent returned>

Do not create, edit or delete any file. Do not run any other tool.
