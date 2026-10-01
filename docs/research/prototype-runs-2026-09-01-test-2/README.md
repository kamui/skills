# Review experiment data

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

**2026-09-01.** Raw outputs and metadata from a second controlled comparison of the same four
code-review prototypes against a different pull request. **Data only** — the analysis of this run
lives in [`evaluation.md`](evaluation.md).
The first comparison set lives in [`../prototype-runs-2026-09-01-test-1/`](../prototype-runs-2026-09-01-test-1/).

## The target

[`redis/redis#15680`](https://github.com/redis/redis/pull/15680) — "Prevent data loss after
cross-shard replica migration". Author `ShooterIT`, **merged** at the time of the run (status was
still derived as for an open PR). Head branch `cross-shard`, base `unstable`.

Run identity, pinned once and given identically to all four runs:

| | |
| --- | --- |
| head | `c54fa4184e7db1ea30c91916f6c0aeb12b5c3f61` |
| base ref | `unstable` |
| base SHA | `065d397030712fe216e795720ae0affd3211212c` |
| merge-base | `065d397030712fe216e795720ae0affd3211212c` |
| diff | 5 files, +401/−1, two commits (`8b3c50521`, `c54fa4184`) |
| originating issue | **none** — no closing reference, no linked issue. The body references a [#15530 discussion](https://github.com/redis/redis/pull/15530#discussion_r3782500859) and Valkey PRs #885/#944. |
| prior review state | 1 `APPROVED` review by `sundb` (empty body, at `8b3c50521`); 3 comments (`ShooterIT`, `shun-lee` with a detailed LGTM, `ShooterIT`). No threads on the posting identity. |
| posting identity | `kamui`, who did NOT author the PR → ordinary first review, `COMMENT` event |

Changed-file manifest:

```
M	redis.conf
M	src/cluster_legacy.c
M	src/replication.c
M	src/server.h
A	tests/unit/cluster/replica-migration.tcl
```

**This target differs from test 1 in three ways that matter for later comparison:**
no originating issue (the Requirements axis resolves per each skill's no-issue rule, not from an
issue text); prior third-party review state present (an approval plus a substantive LGTM comment);
and a much larger, lower-level codebase (redis core C, cluster/replication paths) with a C-heavy
test convention (Tcl) that no run executed.

## Conditions held constant

- Each run got its own clone (`/tmp/run-v2r`, `/tmp/run-v3r`, `/tmp/run-v4r`, `/tmp/run-v5r`) at the
  same head, with `unstable` pinned to the base SHA, and `origin` pointing at a local path so no run
  could read live GitHub state or disturb another's working tree.
- Phase 1 (target resolution) was done once by the orchestrator and handed to every run identically
  as a single packet file: same run identity, same manifest, same PR body verbatim, same prior
  review state, same "no originating issue" statement.
- Publication was disabled for all four runs. Nothing was written to any forge.
- Network access (including `gh` and `git fetch`) was forbidden in all runs; builds and test
  executions were forbidden (they create artifacts), so the new Tcl tests were statically reviewed
  by every run and executed by none.
- Each prototype's own reference documents were treated as authoritative and its phase structure
  followed as written, including its own fan-out and verification policy.
- **Harness and model:** every run (orchestrator and all sub-agents) used the **GLM-5.3-Flash** model
  at the **High** reasoning setting, driven by the **opencode** CLI harness with the context-mode MCP
  toolset. Sub-agents were spawned with opencode's `task` tool (general-purpose agents); the
  orchestrator passed each skill's reference files and the phase-1 packet as file paths the
  sub-agents read themselves.
- **Harness difference vs test 1:** this harness does not report sub-agent token counts, so token
  totals are **unavailable** for all four runs (test 1's harness reported them). Tool-use counts are
  the sub-agents' self-reported invocation counts. Wall clock is the orchestrator's measurement of
  each sub-agent's span.

## What differs between the runs

Only the skill under test:

| | v3 (PR #13) | v4 (PR #16) | v5 (PR #17) |
| --- | --- | --- | --- |
| Architecture | 1 integrated reviewer, self-falsification | 1 integrated reviewer + conditional fresh-context verifier | 1 integrated reviewer + consequence-triggered fresh-context verifier |
| Verification | only for high-risk/large/coupled changes | mandatory for `must-fix`, security, data-loss, contract changes | mandatory for `must-fix` and enumerated consequential risks; artifact names alone do not trigger |

## Files

- `v3-run.md` — output and metadata
- `v4-run.md` — output and metadata
- `v5-run.md` — output and metadata
- `comparison-data.md` — side-by-side metadata table
- `evaluation.md` — the analysis of this run

No `publication-decision.md`: nothing was published; all four runs were data-only.

## Reproducing

The pinned inputs and run files permit a replay against the same head. The clone must be offline
(`origin` a local path) with the phase-1 packet supplied verbatim; the PR is merged, so derived
statuses are advisory reconstructions, not live review state.
