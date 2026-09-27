# #384 matched isolation run

Part of [#384](https://github.com/kamui/skills/issues/384). This is a new experiment,
prepared after [#403](https://github.com/kamui/skills/pull/403) merged at
`b41a6df7939978147d05239150a45c9c345b0cc5`. The maintainer selected enforced isolation
and a matched control/candidate comparison on 2026-09-27. The maintainer approved
the new $120 budget and the decision rule below in this thread. The manifest was
frozen after all 15 launch isolation checks passed, before any paid dispatch.

The previous experiment remains inconclusive at 0/4 valid attempts and $13.027116.
Its attempts, charges and original comparison with historical A are not reused as
new cells. This experiment changes the execution setup in both arms, so historical
A is context only. Its original two-replicate evidence remains intact.

## Question and frozen inputs

Does the exact lifecycle sentence proposed in #384 improve defect recovery when
both the original instruction and candidate run under the same enforced isolation?

- Control skill tree: `c3c53da5381dace16876b0f5b7abe4bccc6bc58b`.
- Candidate skill tree: `938f7c80925248cc76943317d6fec243ddac5a08`.
- [Candidate patch](candidate.patch) SHA-256:
  `da0a42b02fa4d7396457c78c20d8a6307ecb831c266f51e8e39b22679ba26c8f`.
  It adds only the original 153-byte lifecycle sentence to the control skill.
- Primary reviewers and fresh-context workers: `claude-sonnet-5`, high effort,
  Claude Code 2.1.282. The installed executable is available at
  `/home/jack/.local/share/claude/versions/2.1.282`; the default `claude` is already
  2.1.283 and must not be used. The runner checks this pin before claiming a cell.
- `mode: one-shot`, `profile: publishable`, `return_format: artifacts`.
- Base UI `r-base-ui-5460`, gRPC `m-grpc-go-7390`, and soba `q-soba-195`, register v1.
  Packets, source ranges, diff identities, dependency archives and target allowances
  retain their original hashes, checked during preparation.
- Rubric v1 and the original method revision. The metric/runner revision is
  `9076ab8bc2b5c5c9db58bd867027f8317a987caa`. This includes the unchanged scoring rule for both new arm names.

Reviewers receive the factual packet, source diff, execution policy and the one
selected skill tree. They receive no issue text, thresholds, other arm output,
register, mapping, grade or previous experiment output.

## Isolation and validity

Both arms use `claude-strict-v1`. Bash must run in Claude's OS sandbox, with empty
external-domain access, no unsandboxed fallback, and failure when sandboxing is
unavailable. Loopback listeners inside the sandbox remain available for focused
tests. The clone is read-only; caches, scratch and artifacts are attempt-local.
The CLI starts in the work directory and names the review clone explicitly.
Runtime executables use their resolved paths, including version-manager installs.
Before dispatch, ignored `.vite` and `.vite-temp` directories beneath workspace
`node_modules` are linked to the attempt work directory. This lets the original
Base UI test command load its configuration without writing into the source tree.
This adapter setup is identical for both arms and is additional to the unchanged
archive/provisioning identity.

A PreToolUse hook checks direct Read, Write, Edit, Glob and Grep paths before
execution. It rejects writes to the clone, outside paths, parent/absolute globs,
and recursive searches containing escaping symlinks. Workers inherit these
settings. Only the fresh attempt home and the explicit isolation configuration
are settings sources; the original user home, project settings and external MCP
servers are excluded. The fresh home contains the selected frozen skill so the
Skill tool can discover it. The tool list stays fixed. Claude's Bash sandbox and file-tool permissions have distinct
boundaries, as documented in the [sandbox scope](https://code.claude.com/docs/en/sandboxing#scope).

Each attempt stores its generated settings and settings/hook hashes. Filing refuses
missing or altered isolation evidence. The existing transcript audit remains in
force: blocked out-of-bounds requests still count as invalid under its conservative
rules. Enforced isolation prevents exposure; it does not guarantee every review
will satisfy the protocol. No denied operation is silently excused or retried with
broader access. Sandbox failures stop the run for diagnosis before more spending.

The host needs bubblewrap and socat, including socat's shared-library dependencies.
Preparation uses extracted Ubuntu packages under `/tmp/x384-sandbox-tools`; these
are temporary, and their location/dependencies must pass preflight again at launch.
Nothing was installed into system directories.

## Cells and order

There are 18 planned cells: three reviews per target per arm. The manifest contains
all cells and their order. Replicate 1 covers Base UI, gRPC and soba, then replicate
2 and replicate 3. Each target/replicate pair runs back-to-back; the first arm
alternates by pair, starting with control. Only one review runs at a time.

Replace an eligible invalid cell immediately, in filing order, within four total
replacements and 22 total attempts. A valid miss, false finding or skill timeout
is never replaced. Stop once the remaining attempt cap cannot yield all 18 valid
cells. Do not add targets, tune the sentence or extend the caps after observing
outcomes. Record all invalid/stopped attempts and all charges.

## Approved budget

| Reservation | Amount |
| --- | ---: |
| 18 planned reviews at at most $5 reserved each | $90 |
| Up to 4 invalid replacements at $5 each | $20 |
| Blind grading, adjudication and closeout reserve | $10 |
| Approved new run dispatch ceiling | **$120** |

The prior four invalid reviews averaged $3.0904 each. At that rate, 18 reviews
would cost about $55.63 before grading or replacements. A $60–75 planning range
is an extrapolation from invalid attempts, not a forecast of valid-review cost.
The $120 budget leaves reservation room for the full matrix and replacements.
It is separate from the previous $13.03 and does not extend that stopped run.

The CLI receives `--max-budget-usd 5` for each review. That limit is checked between
requests, so an in-progress request can overshoot it. Record actual charges and
stop when they exhaust the cap; do not claim this is a provider-enforced invoice
ceiling. Before every dispatch, require room for its $5 reservation and the
remaining $10 closeout reserve. No separate paid setup probe is planned.

## Decision rule

Blind-grade uniformly rendered findings with the existing template and Opus 5.5
high. Hide arm, tree, cost, native action and verdict from the grader. Adjudicate
plausible new defects before opening arm identity. Grading and adjudication count
against this run's cap.

The candidate passes only if all of these hold:

1. Recover GT-r1 and GT-r2 separately in at least 2/3 valid Base UI reviews each,
   proving introduced harm through concrete lifecycle transitions. Do not count
   the excluded control-mode, cancellation, extra-render or pre-existing remount
   claims.
2. Candidate recovery for each defect is no lower than the fresh matched control,
   and at least one defect has strictly more recoveries. Meeting the absolute
   threshold with identical recovery does not establish a benefit from the added
   instruction.
3. Zero candidate false findings on gRPC and soba, and no new false finding or
   non-material blocker elsewhere. Preserve correct action and sufficient remedies
   on comparable recovered defects. Report control failures separately.
4. Each candidate target's median elapsed-to-payload is at most 1.25 times its fresh
   control median. Require three valid timed reviews per arm/target. Missing timing
   cannot become zero or a substituted CLI duration.

These matched-control requirements replace the old historical-control comparison
for this new run and were approved with the budget. Report the historical
numbers separately. They do not establish statistical significance from three
replicates or satisfy #380's later combined and unseen-target adoption gate.

Stop and reject on a measured candidate precision/other guardrail failure or once
its fixed defect threshold is mathematically unattainable. At completion, reject a
measured regression or missed absolute threshold. If the candidate meets the
absolute thresholds but shows no gain over control, record no demonstrated benefit
and do not adopt it. Missing valid or gradable cells, missing timing, or exhausted
budget make the outcome inconclusive. Leave #384 open unless its acceptance or a
documented rejection and required revert are complete.

## Launch checklist

1. Review and commit the isolation implementation and this protocol. Record the
   runner/metric revision and immutable freeze commit. Verify the candidate diff,
   arm hashes, packet/provisioning hashes, both skill trees, CLI and runtime versions.
2. Repeat the free real-CLI isolation checks and target smoke checks on the launch
   host. These use a local fake API and a dummy key, not model inference. Require
   allowed reads/writes to work, outside reads and clone writes to fail, network
   access to fail, and worker restrictions to hold. Confirm unchanged clone trees.
3. Obtain approval for this new $120 run and its matched decision rule. Set
   `frozen_at` only after approval and successful preflight. Check zero attempt
   claims and charges; the original stopped run remains unchanged.
4. Set `BENCH_CLAUDE` to the pinned 2.1.282 executable and put the verified sandbox
   dependencies on PATH. Use the existing `run_cell.py` status/dry-run/next/replace
   commands with this run directory and a fresh work directory. Supervise the CLI
   jobs through wrapper finalization and preserve dispatch exit/timing records.
5. File, audit and blind-grade each completed pair before further dispatch so a
   stopping condition is acted on immediately. Reproduce scores and publish the
   evidence with the disposition and any required revert.

The manifest freeze references `9076ab8bc2b5c5c9db58bd867027f8317a987caa`, which contains the complete
protocol and runner. [Launch evidence](launch-preflight/summary.json) records the
approval and checks. No paid call preceded the freeze.

## Preparation results

[Preflight summary](preflight/summary.json) records zero paid calls, package and CLI
hashes, and the launch refusal checks. All 15 free isolation checks passed,
including discovery of the actual frozen skill, worker restrictions and all three
target smoke checks. Base UI passed 26 tests with one skipped; gRPC and soba passed.
All three targets also allowed a local base clone for comparisons, and their source
trees stayed clean. The benchmark regression suite, runner, filing and provisioning
self-tests passed.

To repeat the free integration checks on this host:

```sh
BENCH_ISOLATION_CLI=/home/jack/.local/share/claude/versions/2.1.282 \
BENCH_ISOLATION_TARGETS=r-base-ui-5460,m-grpc-go-7390,q-soba-195 \
PATH=/tmp/x384-sandbox-tools/usr/bin:$PATH \
LD_LIBRARY_PATH=/tmp/x384-sandbox-tools/usr/lib/x86_64-linux-gnu \
PYTHONDONTWRITEBYTECODE=1 \
python3 -B bench/tools/test_review_isolation.py
```

These tests use a localhost fake model API and dummy credentials. Their timings and
synthetic token counters are not benchmark outcomes or charges.
