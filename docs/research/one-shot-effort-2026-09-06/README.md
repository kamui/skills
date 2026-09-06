# One-shot effort experiment — medium primary with pinned high verifiers (issue #124)

**Bundle for [#124](https://github.com/kamui/skills/issues/124), started 2026-09-06.** This is the
matched experiment the ticket authorizes: the same repaired `code-review-publish` snapshot run with
its primary at effort `high` (the measured runtime's default for `claude-sonnet-5`) and at effort
`medium`, with every verifier batch pinned at `high` in both arms. It follows the
[one-shot evaluation method](../code-review-one-shot-method.md) and uses the pins from
[#136](../code-review-one-shot-baseline.md). Results and the screening verdict are in
[`evaluation.md`](evaluation.md); every cell's rows are in [`comparison-data.md`](comparison-data.md);
every attempt and every dollar are in [`ledger.md`](ledger.md).

This README is the preregistration. It is committed in two stages, each before the dispatch it
governs, and both stage commits are named below. Anything changed after its stage commit is a dated
deviation with the original text retained.

## 1. Freeze

### 1.1 Stage 1 — design, adapter, thresholds, caps, and the Hyper fixture

**Committed before the first Hyper dispatch** (commit recorded in the ledger's dispatch record of
attempt `att-01`). Nothing from any candidate-arm review had been inspected when this stage was
written: the only chargeable work before it was the configuration probes and the target vetting in
[ledger.md](ledger.md) §Setup, none of which ran a review.

**Hypothesis.** With verifiers held at `high`, a `medium` primary produces the same published
outcomes as a `high` primary at materially lower billed cost, on a reasoning-heavy target where the
lower-effort arm has never run (Hyper) and on two fresh reasoning-heavy targets.

**Arms.** One skill snapshot, one model, one verifier configuration, one packet per target; the arms
differ in one command-line flag.

| Arm | Primary effort | Verifier effort | Row label |
| --- | --- | --- | --- |
| control | `high` (`--effort high`, the observed default) | `high`, via the `v5b-verifier-effort-high` definition | `high` |
| candidate | `medium` (`--effort medium`) | `high`, via the same definition | `medium` |

**Pins.**

| | Value |
| --- | --- |
| Skill | `skills/code-review-publish` at commit `83bc170e8ae9c5f2d6a6941a94f25f6748a36ed6`, tree `bea6be143582e75bada966ee85964623ef31f167` (the #136 repaired baseline; `workflow=v5b-10`). Snapshot taken with `git archive` and the tree hash re-checked; runs identify the snapshot by tree hash, never by trailer |
| Model | `claude-sonnet-5`, passed as `--model sonnet` on the root and `model: "sonnet"` on every `Agent` call; verified from every assistant line of every transcript before scoring |
| Runtime | Claude Code `2.1.263` (headless `claude -p`), Darwin 27.0.0, Python 3.14.7, git 2.55.0 |
| Prices | Sonnet 5 list `$2/$10` per M tokens; cache write ×1.25 (5-minute tier) and ×2.0 (1-hour tier) as the transcripts report them; cache read ×0.1. `transcript_usage.py` prices each tier from the usage fields (#97) |
| Method | [`code-review-one-shot-method.md`](../code-review-one-shot-method.md) at the stage-1 commit |

**Adapter: how effort is set and recorded in this runtime.** Claude Code has no per-call effort
parameter on the `Agent` tool; effort is a session setting (`--effort`, `/effort`, `effortLevel`)
or a sub-agent definition's `effort` frontmatter/JSON field, and a child agent inherits its parent's
effort unless its own definition sets one. Definitions in a `.claude/agents/` directory created
after a session starts are not loaded (runtime docs; observed twice here, ledger S1). The smallest
supported shape that meets the ticket's requirement — every verifier at `high` while the primary
varies, requested and observed effort both recorded — is therefore one headless session per cell:

```sh
claude -p --session-id <uuid> --model sonnet --effort <high|medium> \
  --agents "$(cat agents.json)" \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep,Agent" \
  --output-format json "<dispatch prompt>"
```

where `agents.json` defines exactly one agent, `v5b-verifier-effort-high`
(`model: sonnet`, `effort: high`, a one-paragraph prompt saying it changes nothing but the effort),
and the dispatch prompt tells the primary to dispatch every verifier batch with
`subagent_type: "v5b-verifier-effort-high"`. The primary is the session root, so its transcript is
`~/.claude/projects/<cwd>/<uuid>.jsonl` and each verifier's is under `<uuid>/subagents/`. Requested
effort is the `--effort` value and the definition's field; observed effort is the top-level `effort`
beside `message.model` on every assistant line, scanned by [`../tools/agent_effort.py`](../tools/agent_effort.py)
(shipped with this bundle) and by the close-out step. The dispatch prompt names neither arm nor
effort, so the reviewer is blind to its arm. The adapter and the definition are experiment tooling;
no skill text, agent definition, or session setting of the user's changes.

**Probes (ledger S1–S4, all `claude-sonnet-5`).** Plain in-session dispatch: `high` (the default).
Headless root at `--effort medium`: `medium` on 4/4 lines; its child through the definition: `high`
on 3/3; its plain child: `medium` on 2/2 (inheritance confirmed, which is why the definition is
mandatory). Headless root at `--effort high`: `high` on 3/3; its child through the definition: `high`.

**Cells.** Fourteen planned cells: three replicates per arm on Hyper, two per arm on each of two
fresh targets. A replicate is a fresh headless session and a fresh clone; the harness exposes no API
seed, so replicates are labelled by ordinal. Attempt IDs are `att-NN`, never reused. At most two
replacement attempts (16 attempts total).

| Target | Kind | Cells | Execution |
| --- | --- | --- | --- |
| (a) `hyperium/hyper#3952` | regression fixture from the holdout; buggy (GT-a1) | `high` ×3, `medium` ×3 | none (Rust toolchain would need network; identical for both arms, as in the holdout) |
| (x) stage 2 | fresh, buggy, reasoning-heavy | `high` ×2, `medium` ×2 | stage 2 |
| (y) stage 2 | fresh, clean, high-risk | `high` ×2, `medium` ×2 | stage 2 |

**Order and concurrency.** Matched pairs dispatch together, at most two cells in flight: Hyper
replicate 1 (`high` then `medium`), replicate 2 (`medium` then `high`), replicate 3 (`high` then
`medium`); then (x) replicates 1–2 and (y) replicates 1–2 the same way. A session-limit notice stops
new dispatch until its reported reset. No pilot is planned for this ticket (the method's pilot is
#137's).

**Replacement policy.** An attempt is discarded and replaced inside the cap when it is stopped by a
session-limit notice or harness error, when any transcript line shows a model other than
`claude-sonnet-5` or an effort other than the arm's requested value (primary) or `high` (verifier),
when a verifier was dispatched without the definition, when the clone was mutated or a leak SHA was
reachable, or when the reviewer read another cell's files. A reviewer that finishes but violates its
own contract is a **skill failure** and stays a valid attempt (scored, and completion judged under
the method). No resumed continuation is allowed: a stopped attempt leaves evidence only.

**Ground truth.** Hyper's register is the holdout README's
[Target (a)](../prototype-runs-holdout/README.md#target-a--hyperiumhyper3952-a-concurrency-fix-that-hot-looped-was-reverted-and-re-landed-on-an-invariant):
one material defect, **GT-a1** (the loop spins for any writer whose `poll_flush` is always ready;
`conn_ready` from flush is not write readiness), sufficient fix = gate continuation on the write
half's own readiness; the "not ground truth" list there is binding. Fresh targets' registers are
sealed in stage 2 before their first dispatch. Unexpected plausible true findings go to blinded
independent adjudication (arm, effort, and replicate labels removed) before any register change,
and every attempt is rescored against a versioned register.

**Scoring.** Method §4. Payloads are scored blind: each attempt's payload is copied under a random
token with the mapping sealed in `scoring/`, scored, then unblinded. The screening rule, applied to
the candidate (`medium`) arm against the control (`high`) arm:

1. zero raw false findings across all candidate attempts, harness-invalid ones included;
2. no more false-clean outcomes (count and rate, on the same buggy targets);
3. macro material recall not lower, in both the attempt-level and completed-only views, and
   completion rate not worse;
4. matched median billed cost ratio (candidate cell all-attempt cost / control cell all-attempt
   cost, matched by target and replicate, median over complete pairs) `<= 0.80`.

Known-Hyper and fresh-target outcomes are reported separately and the fresh subset must meet
gates 1–3 on its own before any runtime-specific recommendation. A full positive screen needs all
fourteen cells validly completed. Otherwise the default stays and the report names the failing gate.

**Budget gate.** Projection from the holdout's billed medians on the same skill line (Hyper `v5b`
$4.43; `v5b` overall $3.62; `v5b-effort-medium` $2.33 ≈ −40%): Hyper 3 × ($4.43 + $2.66) = $21.27;
fresh 2 × 2 × ($3.62 + $2.33) = $23.80; cells $45.07. Setup, probes, vetting and adjudication
allowance $15; grading/closeout reserve $5; two replacements ≈ $8. Projected ticket total ≈ $73.
Spend cap = min(1.5 × $73, $150) = **$110**. Per-pair run budget: no cell is stopped for cost, but
a single attempt projected past $12 (2.7× the Hyper control median) is reported as an outlier; the
cap binds on the ticket total. The 1-hour cache tier appeared in the probes (ledger S3–S4) and is
priced at ×2.0 where the transcripts report it. Assumptions: fresh targets are of holdout size
(under ~400 changed lines); no paid tool or repro charges.

### 1.2 Stage 2 — fresh targets

_Written and committed before the first fresh-target dispatch; see §3._

## 2. Preparation

### 2.1 Hyper fixture

Mirror: a bare copy of the holdout's `hyper.git` (refs `master` = merge-base
`f9f8f44058745d23fa52abf51b96b61ee7665642`, `review-head` = `f2aa734e5699a91fc20f1178e38af7b1e374bdbc`).
Negative checks on the mirror and on every clone: `2377b893…` (merge), `4492f31e…` (revert),
`743a3ba0…` and `a416aa8b…` (re-land), `f660f5bf…` (#4143) — all absent. Packet: the holdout's
`packets/a/packet.md`, byte-identical, SHA-256
`c94a8d3ed431594d9acd0803bac2558d9227aa58733404f1a5fd416a6e3bf1f2`, copied to
[`a-hyper-3952/packet.md`](a-hyper-3952/packet.md). Its section 8 (offline, no execution,
truncated history, publication disabled, persist before verify, sandbox) binds every cell.

### 2.2 Per-cell mechanics

`run_cell.sh <target> <high|medium> <replicate> <attempt>` (experiment tooling in `/tmp/effort124`,
quoted in [`tooling.md`](tooling.md)): fresh clone from the mirror with the base branch forced to
the merge-base and `review-head` checked out at the head; negative checks; the dispatch prompt
rendered from one template (quoted in `tooling.md`) with the cell's paths; the timing sidecar
created with `root_dispatched_at` immediately before the `claude -p` call; `payload_validated_at`
written by the reviewer right after its final successful `validate_review.py` run via
`mark_event.py`; `completed_at` written by the runner when the session returns with both the report
and the payload present (completion mode `render-only`). A non-zero exit or a missing file writes a
stop record outside the sidecar. Close-out (`close_cell.py`) scans model and effort on every line of
the root and every child transcript, refuses any child not dispatched through the definition, and
meters with `transcript_usage.py --prices 2,10 --report <run.md> --timing <timing.json>`.
