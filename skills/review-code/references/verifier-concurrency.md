# Verifier bug-class check for concurrency and invariant candidates

Include this reference in the verifier brief only when a supplied candidate's `kind` is `concurrency` or `invariant`. It extends [`verifier.md`](verifier.md)'s verification task for every such candidate the verifier confirms; it adds no verdict, no batch, and no candidate.

For every confirmed `kind=concurrency` or `kind=invariant` candidate:

1. **State the invariant at the rule level, not the transition level.** Name which counters, flags, queue contents, or ownership records must stay consistent with which operations, and under which lock or ordering that consistency was guaranteed at the merge-base. Do not name it as "during X" (a transition); name it as "A must never be observed inconsistent with B".
2. **State whether the candidate's failing interleaving requires runtime shutdown, teardown, or an error path.** If it does, additionally ask whether the same rule can fail in steady state, and trace at least one steady-state interleaving (normal spawn, normal wake, normal idle) to a `holds` or `fails` verdict with `path:line` citations.
3. **Enumerate sibling interleavings before sibling code paths.** For each pair of concurrent actors that touch the rule's state — producer vs consumer, spawner vs worker-going-idle, spawner vs worker-exiting, spawner vs shutdown, claimant vs releaser — state whether the rule holds, citing the lines where each actor reads and writes the shared state.
4. **Then enumerate sibling code paths** governed by the rule and state for each whether the proposed `change` protects it.
5. **Widen `change` to the rule level when needed.** When the proposed fix covers only one interleaving or one path, correct `change` to the outcome that restores the rule for every failing interleaving found in steps 2–3. If the rule can only be restored by re-serializing two operations, say which two and under which lock.

A `change` that closes the shutdown projection while a steady-state projection of the same rule remains open is narrower than the bug class; say so in the correction. The steady-state `holds`/`fails` rulings from context construction stay inside the candidate's verdict as scoped safety rulings under `verifier.md`.
