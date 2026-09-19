You are a relay. Do exactly this and nothing else:

1. Write a JSON file /tmp/i273/item3/root-tools.json with one object: {"agent_tool_parameters": [...names of every parameter the Agent tool's schema offers you, verbatim...], "tools": [...names of every tool you have...]}.
2. Read /tmp/i273/item3/brief-step.md and dispatch exactly one subagent with the Agent tool: subagent_type "general-purpose", model "opus", description "implement step 4", and the file's full contents, verbatim, as the prompt. Do not add or remove anything. If the Agent tool offers a foreground option, do not use it; use the tool's default.
3. Wait for that subagent to complete. When its completed result reaches you, write its final report verbatim to /tmp/i273/item3/step-report.md, then write /tmp/i273/item3/root-observation.json with {"agent_id": "...", "dispatch_tool_result": "<the text the Agent tool call returned to you, verbatim>", "how_result_arrived": "<inside the Agent tool result | as a later notification message | other, describe>", "utc_dispatched": "...", "utc_result_received": "..."} using timestamps from `date -u +%FT%TZ` run right before the dispatch and right after the result arrives.
4. Print DONE.

Do not read the repository, do not review anything yourself, and never send the subagent a message.
