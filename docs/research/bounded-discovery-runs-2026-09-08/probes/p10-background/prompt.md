This is a capability probe, not a review. Answer the question by doing the steps, not by reasoning
about what the harness probably supports.

1. Dispatch the custom agent `bd-verifier` **once** with `run_in_background: true` and this
   instruction verbatim: "Read /tmp/bd149/probes/p2/work/clone/go.mod and reply with the module path
   on its first line, and nothing else."
2. Immediately after dispatching it, and **without waiting for it**, run this Bash command:
   `git -C /tmp/bd149/probes/p2/work/clone log --oneline -1`
3. Then collect the background agent's result by whatever mechanism this harness provides, and say
   what that mechanism was.

Then reply with ONLY a fenced ```json block, no prose before or after:

{"background_accepted": true|false,
 "how_dispatched": "<the exact tool and parameters you used>",
 "worked_while_running": true|false,
 "collection_mechanism": "<how you got the result, or why you could not>",
 "agent_result": "<what the agent returned, or null>",
 "errors": "<any error text the harness gave you, or null>"}
