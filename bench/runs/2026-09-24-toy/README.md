# Run 2026-09-24-toy: the four-arm harness shakedown

A synthetic fixture run: one planted defect, four reviewer arms, seven attempts. It exercised the
adapters, the read audit, the normalizer and the meters before any scored target ran, and it is
filed here so the suite's filing path (`file_attempt.py`) has real records to run against. It is
never pooled with scored runs; its cohort group is `fixture`.

The narrative, the decisions and the review history that led to it are in
[`docs/research/builtin-review-benchmark-2026-09-24/`](../../../docs/research/builtin-review-benchmark-2026-09-24/README.md).

## Files

| Path | Holds |
| --- | --- |
| `manifest.json` | arms with their file hashes, the fixture cohort, the cells as run, and three deviations |
| `fixture/` | `target.json`, `register.v1.json` (GT-toy1), `packet.md`, and the repository as `toy-average.bundle` |
| `attempts/att-NNN/` | `attempt.json` plus `dispatch.txt`, `timing.json`, `audit.json`, `normalized.json`, the native output, `usage-requests.jsonl` |
| `scoring/toy-average/mapping.v1.json` | rubric v1 assignments for all seven attempts, not blind |
| `results.v1.json` | the metrics `score.py` computed from the attempts and the mapping |

Transcripts are archived outside the repository under `~/.t3/bench-cache/transcripts/2026-09-24-toy/`
with their hashes in each `attempt.json`; every archive passed its restoration check. The fixture
directories the attempts ran in are under `~/.t3/bench-runs/toy/`.

## Attempts

| Attempt | Arm, replicate | Disposition | Elapsed | Cost ($) | Requests |
| --- | --- | --- | --- | --- | --- |
| att-001 | claude-builtin-sonnet-high, 1 | valid completed | 5 s | 0.10 | 2 |
| att-002 | claude-builtin-opus-high, 1 | harness-invalid: effort medium and the low prompt variant | 9 s | 0.09 | 4 |
| att-003 | codex-default, 1 | harness-invalid: `find ..` read outside the attempt | 33 s | 0.10 list | 4 |
| att-004 | claude-builtin-opus-high, 1 (replaces att-002) | valid completed | 15 s | 0.06 | 3 |
| att-005 | claude-builtin-sonnet-high, 2 | valid completed | 7 s | 0.04 | 2 |
| att-006 | review-code-sonnet-high, 1 | valid completed | 89 s | 0.50 | 17 |
| att-007 | codex-default, 2 | valid completed | 34 s | 0.09 list | 3 |

Codex costs are list-price equivalents; the account is a ChatGPT plan that consumes quota.
Elapsed runs from `dispatched_at` to `completed_at` for a valid completed attempt. The two
harness-invalid attempts carry no `completed_at`: their `stopped_at` is the wrapper's recorded end,
and Elapsed runs to it. The attempts before att-007 predate the four-event timing semantics. att-001,
att-002, att-003 and att-006 had their `payload_validated_at` stamped by a later normalizer run,
after the wrapper's recorded end; att-004 and att-005 have none.

## What the records show

- **Every attempt recovered GT-toy1**, the planted `ZeroDivisionError` on an empty cart,
  including the two harness-invalid ones, and every recovery stated a sufficient fix. Rubric v1
  grades fix sufficiency by what the item states, not by whether the arm has a fix field: only
  review-code filled `proposed_fix`, and the built-in and Codex items state the required outcome
  (a defined value or a handled error for an empty cart) in their claim, title or consequence. The
  Opus built-in also restated the defect from the docstring's side and added a no-test remark,
  which maps to `non-material`.
- **The session effort flag selects the built-in's prompt.** att-002 passed `high` only as the
  argument and ran Opus at `medium` with the low variant; att-004 set `--effort high` and matched
  the registered high variant. Sonnet's default effort is already `high`, which is why att-001
  matched without the flag.
- **The export layout is necessary.** att-003's clone sat beside the other attempts' clones, and
  Codex's `find .. -name AGENTS.md` walked them. att-007 ran with the clone inside its own attempt
  directory and read nothing outside it.
- **review-code's early scratch was in `/tmp`.** att-006 predates the wrapper's `TMPDIR` inside the
  attempt directory, so its store and a `/tmp/rc_dir` note it wrote itself are allowed explicitly
  in the audit, as its record states.

One cost moved when the run was filed. att-004 is priced at the recorded Opus 5.5 cache-read rate
of $0.20 per million tokens (`bench/rates.json`), where the shakedown table had used the meter's
default one-tenth ratio and shown $0.07.

## Reproducing

```sh
git clone --bare bench/runs/2026-09-24-toy/fixture/toy-average.bundle /tmp/toy-staging.git
python3 bench/tools/provision.py mirror --target bench/runs/2026-09-24-toy/fixture --staging /tmp/toy-staging.git
python3 bench/tools/provision.py clone  --target bench/runs/2026-09-24-toy/fixture --out <attempt-dir>/clone
bench/tools/dispatch.sh <arm-kind> <attempt-dir> <attempt-dir>/clone main bench/runs/2026-09-24-toy/fixture/packet.md [model] [effort]
python3 bench/tools/file_attempt.py --attempt-dir <attempt-dir> --clone <attempt-dir>/clone \
    --target bench/runs/2026-09-24-toy/fixture --arm bench/arms/<arm>.json --run-id <new-run-id> \
    --attempt-id att-001 --replicate 1 --out bench/runs/<new-run-id>/attempts/att-001
```

## Results

`results.v1.json` is computed by `score.py` from the seven records and mapping v1 against register
v1. Of the six planned cells, five ended valid completed and one harness-invalid (codex-default
replicate 1, att-003, never replaced). Every arm's completed-only recall is 1.0. The attempt-level
recall of the Opus built-in and of Codex is 0.5, because each has one harness-invalid attempt that
scores zero. There are no false findings, and the Opus built-in has one noise item. Repricing every
request at the run's own `rates.json` entries reproduces each metered cost exactly, for both the
Claude and the Codex formulas.
