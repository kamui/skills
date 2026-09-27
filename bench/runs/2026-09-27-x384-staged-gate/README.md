# #384 staged gate run

Part of [#384](https://github.com/kamui/skills/issues/384). This is the third
experiment on the lifecycle sentence and a new one. The
[first run](../2026-09-26-x384-lifecycle/README.md) and the
[matched run](../2026-09-27-x384-matched-isolation/README.md) stay closed and
inconclusive. Their attempts, grades and charges are not reused as cells here.

The maintainer approved the staged design and the $30 Stage 1 cap in this thread
on 2026-09-27. Stage 2 has no approved budget.

## Why the run is staged

The pass rule needs GT-r1 and GT-r2 in at least 2 of 3 candidate Base UI reviews
each. No review has recovered GT-r1 in 14 graded Base UI reviews across every arm
and run. Stage 1 therefore buys only the cells that can end the experiment: the
three candidate Base UI reviews. Control and precision cells matter only if the
candidate clears that threshold, so they wait for Stage 2.

Stage 1 cannot pass the candidate. It can reject it, clear it for Stage 2, or end
inconclusive.

## Frozen inputs

- Candidate skill tree: `938f7c80925248cc76943317d6fec243ddac5a08`. It is the
  control tree `c3c53da5381dace16876b0f5b7abe4bccc6bc58b` plus the
  [candidate patch](candidate.patch) alone, SHA-256
  `da0a42b02fa4d7396457c78c20d8a6307ecb831c266f51e8e39b22679ba26c8f`. The patch
  adds the original 153-byte sentence. [#405](https://github.com/kamui/skills/pull/405)
  removed the sentence from `main`; the run reads the frozen tree, not `main`.
- Arm: `review-code-sonnet-high-enforced-lifecycle`. Primary reviewer and
  fresh-context workers are `claude-sonnet-5`, high effort, Claude Code 2.1.282 at
  `/home/jack/.local/share/claude/versions/2.1.282`. The runner checks the pin
  before it claims a cell.
- `mode: one-shot`, `profile: publishable`, `return_format: artifacts`.
- Target: Base UI `r-base-ui-5460`, register v1. Packet, diff identity and
  provisioning hashes are the matched run's.
- Rubric v1 and the original method revision. The manifest records the runner
  and metric revision at freeze.

Reviewers receive the factual packet, source diff, execution policy and the
candidate skill tree. They receive no issue text, threshold, register, mapping,
grade or earlier output. The execution policy text is the matched run's.

## Isolation and validity

The arm uses `claude-strict-v2`. Its sandbox, file-tool hook, tool list, fresh
home and settings sources are those of `claude-strict-v1`. Two things change.

1. **Shell environment.** The settings carry the target's offline cache
   environment, so a bare `go` or `pnpm` command runs offline against the
   attempt's own caches. For the Go targets this sets `GOPROXY=off` and
   `GOTOOLCHAIN=local`.
2. **Validity.** `attempt_audit.py` judges each request against the attempt's own
   `isolation-settings.json`. A request is confined, and does not invalidate the
   review, when the sandbox denies the path, when everything readable beneath the
   path is declared in the settings, when the file-tool hook gates the path, or
   when the settings allow no network domain. Confined requests are filed under
   `confined_requests` in `audit.json`. A request the settings leave reachable is
   still a violation.

The sandbox also mounts the CLI's own temporary base, which the settings file
does not list. `dispatch.sh` sets `TMPDIR` to the attempt's `tmp`, so that base
is attempt-local. With the host default, the base is `/tmp/claude-<uid>`, which
every Claude Code session on the host shares. The native checks now run with the
attempt's `TMPDIR` and hold a canary in the shared base that the sandbox must not
read.

Missing or altered isolation evidence, a changed clone tree, a wrong model,
effort, CLI version or skill tree, and a wrong diff range still invalidate an
attempt. Sandbox failures stop the run for diagnosis before more spending.

The [audit replay](../2026-09-27-enforced-audit-replay.json) ran the old and
revised audit over the archived transcripts of all 137 filed attempts that have
them. Without isolation settings the two agree on every attempt. Under their own
settings, the matched run's five invalid attempts have no violation and one or
two confined requests each. That replay tests the policy. It does not reclassify
those attempts.

The host needs bubblewrap and socat. The extracted Ubuntu packages under
`/tmp/x384-sandbox-tools` are temporary and must pass the native checks again at
launch.

## Stage 1 cells and caps

Three cells: candidate reviews of Base UI, replicates 1 to 3, one at a time.

| Cap | Value |
| --- | ---: |
| Planned cells | 3 |
| Replacements for invalid attempts | 2 |
| Maximum attempts | 5 |
| Reserved per attempt | $5 |
| Grading and closeout reserve | $5 |
| Approved Stage 1 ceiling | **$30** |

The CLI receives `--max-budget-usd 5` for each review. That limit is checked
between requests, so one request can overshoot it. Record actual charges.

Replace an invalid cell immediately, in filing order. A valid miss, a false
finding or a skill timeout is never replaced. Do not add cells, tune the sentence
or extend a cap after an outcome is seen.

## Stage 1 decision rule

Blind-grade with the existing template and Opus 5.5 high once two valid reviews
are filed, and again after the third. Each grading holds every filed attempt.
The grader sees no arm, tree, cost, native action or verdict. Adjudicate a
plausible new defect before the decision. Grading counts against the cap.

A recovery counts when the review demonstrates the introduced harm through
concrete lifecycle transitions. Null or control-mode-switch claims, intended
cancellation behavior, the accepted extra render and pre-existing uncontrolled
remount behavior do not count.

- **Reject.** Two valid reviews miss GT-r1, or two valid reviews miss GT-r2. The
  2 of 3 threshold is then unattainable. Stop, leave the remaining cells unrun,
  and close #384 as a rejected hypothesis. No revert is owed, because the
  sentence is already off `main`.
- **Clear.** Three valid reviews recover GT-r1 at least twice and GT-r2 at least
  twice. This opens Stage 2. It is not a pass.
- **Inconclusive.** The caps run out before either outcome. Stop and diagnose.
  Leave #384 open.

Stage 1 records false findings, non-material blockers, remedy sufficiency, cost
and elapsed-to-payload for every valid review. None of them decides Stage 1,
because each guardrail compares the candidate with a matched control.

## Stage 2, fixed before any Stage 1 outcome

Stage 2 runs only after a clear and a separately approved cap. It has 15 cells:
three control Base UI reviews, and three control and three candidate reviews on
each of gRPC `m-grpc-go-7390` and soba `q-soba-195`. The arms are
`review-code-sonnet-high-enforced-control` and
`review-code-sonnet-high-enforced-lifecycle`. The three valid Stage 1 reviews
are the candidate Base UI cells.

The candidate passes only under the matched run's four conditions, unchanged:
both absolute recovery thresholds; recovery no lower than the control on either
defect and strictly higher on one; zero candidate false findings on gRPC and
soba, with no new false finding or non-material blocker elsewhere and remedies
preserved; and each target's candidate median elapsed-to-payload at most 1.25
times its control median, from three valid timed reviews per arm.

The Base UI latency comparison then sets Stage 1 candidate timings against
Stage 2 control timings. Those reviews are not interleaved, which the matched
design was. Report that limit with the result.

A pass still leaves #380's combined and unseen-target adoption gate.

## Launch checklist

1. Commit the runner, the arm files and this protocol. Record that commit as the
   manifest's freeze and metric revision.
2. Repeat the free native isolation checks and the three target smokes on the
   launch host with the pinned CLI and a local fake API.
3. Set `frozen_at`. Confirm zero claims and zero charges for this run.
4. Set `BENCH_CLAUDE` to the pinned executable and put the sandbox tools on
   `PATH`. Dispatch with `run_cell.py --next` and `--replace`.
5. File and audit each attempt before the next dispatch. Grade as the decision
   rule states and act on a stopping condition at once.

## Preparation results

The [preflight summary](preflight/summary.json) records zero paid calls. All 21
native isolation checks passed with the real CLI and a local fake API. They
include a shell that reads `GOPROXY=off` and `GOTOOLCHAIN=local` from the
settings, and a bare smoke command on each of the three targets with no
environment prefix. The 144 benchmark tests passed, 14 of them native checks
skipped in that suite and passed in the native one. Runner, filing, provisioning
and scoring self-tests passed.

To repeat the free native checks on this host:

```sh
BENCH_ISOLATION_CLI=/home/jack/.local/share/claude/versions/2.1.282 \
BENCH_ISOLATION_TARGETS=r-base-ui-5460,m-grpc-go-7390,q-soba-195 \
PATH=/tmp/x384-sandbox-tools/usr/bin:$PATH \
LD_LIBRARY_PATH=/tmp/x384-sandbox-tools/usr/lib/x86_64-linux-gnu \
PYTHONDONTWRITEBYTECODE=1 \
python3 -B bench/tools/test_review_isolation.py
```
