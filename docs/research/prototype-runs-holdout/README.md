# Holdout evaluation — method

**Status: method only; no cell has run.** This directory was created ahead of the holdout evaluation
(#60) by #67, which fixes how every run in it is metered. Everything #60 specifies — the six targets,
their ground truth and calibration bands, the conditions, the model verification, the run documents,
and `evaluation.md` — is written by #60 and lands here. The full experimental design is #60's body and
[aggregate analysis §8 "The holdout demand"](../prototype-runs-aggregate-tests-1-4-v2a-v5a.md#the-holdout-demand);
this file carries only the parts of the method that were decided before the runs.

The directory is undated because it predates the runs. #60 may rename it to
`prototype-runs-<date>-holdout/` when the grid starts; the one link that points here by path, in
aggregate analysis §7 conclusion 8, moves with it.

## Method

Replicate the test-4 method as written in
[`../prototype-runs-2026-09-01-test-4/README.md`](../prototype-runs-2026-09-01-test-4/README.md):
a single cohort, one model passed explicitly on every `Agent` call and verified from every transcript's
`message.model` before scoring, a truncated mirror with negative `git cat-file -e` checks recorded per
clone, identical phase-1 packets across arms, per-run sandboxes with self-disclosure, and the
expensive phase persisted to disk before any verifier is dispatched. #60 adds three seeds per cell and
the ground-truth-before-run rule. The rest of this section is the metering rule #67 adds.

### Two files per run

Every run writes two files and keeps them apart:

- **Review payload:** `<target>/<arm>-seed<n>-payload.md`. The review exactly as the arm would
  publish it — summary body, every finding, question, and observation with its trailer — and nothing
  else. This is what a production run emits. Target (f)'s re-review writes a second payload file.
- **Research report:** `<target>/<arm>-seed<n>-run.md`, in the existing run-document format:
  metadata, the verifier dispatch prompts and verbatim reports, the complete disposition ledger,
  everything consulted beyond the diff, mechanism checklist, specific answers. This is the evidence
  base and is never dropped; it is metered separately, not stopped.

The report links to the payload file instead of reproducing it. A report that must quote the payload
says so in its metadata, because the arithmetic below then counts the payload twice (once as payload,
once inside the report) and overstates the report by the payload's size.

### Metering per run

Each run document's Metadata section records:

1. **Harness-reported tokens for the run.** Record what the harness meters and say what that
   covers, as test 4 did: the run's own usage block when the orchestrator dispatched it as a
   sub-agent, plus the usage block of every sub-agent the run spawned. Where the primary is not
   metered, say so; the figure is then a lower bound of the run and the comparison notes it.
2. **A self-reported approximate split** of that total into five parts: instruction load (skill
   files read), repository reads, private records (ledger, notes, staging files), review payload,
   research report. The first three are the run's own estimate and are labelled as such.
3. **The payload's and report's byte sizes.** Where the harness does not expose output tokens per
   file, convert at **4 bytes per token** and label the result `est.`; where it does, record the
   metered count and label it `metered`. The byte sizes are exact either way.
4. **The production-shaped figure:** harness total minus the research report. Only the report is
   subtracted. Instruction load, repository reads, and private records are costs a production run
   pays too (the ledger is required by the skill), so they stay in.

Compute items 2–4 with the shared script so every run document does it the same way:

```sh
python3 docs/research/tools/cost_split.py \
  --harness-total 281400 \
  --payload docs/research/prototype-runs-holdout/<target>/<arm>-seed<n>-payload.md \
  --report  docs/research/prototype-runs-holdout/<target>/<arm>-seed<n>-run.md \
  --instruction-load 40000 --repository-reads 150000 --private-records 30000
```

Paste its block into the run document verbatim. Re-run it with `--row "<arm> seed <n>"` and paste
that line into the cost table in [`comparison-data.md`](comparison-data.md). The script exits `1`
when the report or the sum of the reported parts exceeds the harness total, which means the split
double-counts something; fix the inputs, not the table.

### Ranking

Arms are ranked on the **production-shaped** column, not on the raw harness figure. The raw figure
stays in the table for continuity with the corpus, whose numbers are all raw. The report's share of
the total is expected to differ by arm — in test 4 the Panel run documents are 89–93 KB against
57–75 KB for the Skeptic line — so subtracting it moves the ratios, not just the totals.

## Files

- `README.md` — this file; #60 adds targets, ground truth, conditions, and model verification
- `<target>/<arm>-seed<n>-payload.md` and `<target>/<arm>-seed<n>-run.md` — one pair per run
- `comparison-data.md` — side-by-side metadata with the production-shaped cost column
- `evaluation.md` — pass/fail against each #60 success criterion; written by #60
- [`../tools/cost_split.py`](../tools/cost_split.py) — the metering script; `--self-test` checks it
