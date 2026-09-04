# Holdout evaluation — method

**Status: method only; no cell has run.** This directory was created ahead of the holdout evaluation
(#60) by #67, which fixes how every run in it is metered, and #69, which fixes what a dispatch may ask
a run to do; #68 adds one lower-effort arm with its adoption rule written before any run. Everything
#60 specifies — the six targets, their ground truth and calibration bands, the
conditions, the model verification, the run documents, and `evaluation.md` — is written by #60 and
lands here. The full experimental design is #60's body and
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
the ground-truth-before-run rule. The rest of this section is the metering rule #67 adds, the
dispatch-hygiene rule #69 adds, and the lower-effort arm #68 adds.

### Dispatch hygiene

A dispatch gives a run its target, its conditions, and its output contract. It leaves the arm's own
execution alone, so the grid meters the skill and not the demonstration.

Two instructions in the test-1 to test-4 dispatches broke that rule and do not carry forward. Runs were
told to compute the `context` digest three times, to show it was deterministic, and to invoke the arm's
scripts with `--self-test` inside the run, to show the validator was sound. Both demonstrate F1 rather
than review the target, and every v5a run document carries them at a cost of roughly 3–5k tokens.

A holdout dispatch asks for the digest **once**, as the arm's own contract specifies, and asks for no
in-run self-test. Determinism and validator soundness are established once, before the grid starts, by
running the arm's script regression tests in this repository — for the Skeptic line
`python3 skills/code-review-publish/scripts/test_context_fingerprint.py` and
`python3 skills/code-review-publish/scripts/validate_review.py --self-test` — and recording that they
passed at the pinned commit. That is CI's job once this repository has CI. Metering a run afterwards
with `cost_split.py`, including its `--self-test`, is the researcher's work outside the run and is
unaffected.

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

1. **Billed usage from transcripts.** After the run, locate every transcript the run produced
   (the run's own sub-agent transcript plus one per sub-agent it spawned) and run
   `python3 docs/research/tools/transcript_usage.py <paths> --prices 2,10 --report <run.md>`.
   Paste its block into the run document. Read `message.model` from the same lines for the model
   verification #60 requires. Record the transcript paths. Keep the harness's `subagent_tokens`
   beside it as `legacy`, for continuity with the corpus; rank on the billed figure. Where the
   legacy figure omits the primary, pass `--harness-note "primary not metered"` to `cost_split.py`
   so the legacy split says so.
2. **A self-reported approximate split** of that total into five parts: instruction load (skill
   files read), repository reads, private records (ledger, notes, staging files), review payload,
   research report. The first three are the run's own estimate and are labelled as such.
3. **The payload's and report's byte sizes.** Where the harness does not expose output tokens per
   file, convert at **4 bytes per token** and label the result `est.`; where it does, record the
   metered count and label it `metered`. The byte sizes are exact either way.
4. **The production-shaped figure:** billed total minus the report's estimated output cost, as
   the script prints. Only the report is subtracted. Instruction load, repository reads, and
   private records are costs a production run pays too (the ledger is required by the skill), so
   they stay in.

Item 4 comes from `transcript_usage.py --report`. Compute items 2–3, and the same split of the
legacy figure, with the sibling script so every run document does it the same way:

```sh
python3 docs/research/tools/cost_split.py \
  --harness-total 281400 \
  --payload docs/research/prototype-runs-holdout/<target>/<arm>-seed<n>-payload.md \
  --report  docs/research/prototype-runs-holdout/<target>/<arm>-seed<n>-run.md \
  --instruction-load 40000 --repository-reads 150000 --private-records 30000
```

Paste its block into the run document verbatim. Re-run it with `--row "<arm> seed <n>"` and paste
that line into the cost table in [`comparison-data.md`](comparison-data.md), whose header is the
script's `--header` output. The script exits `1`
when the report or the sum of the reported parts exceeds the harness total, which means the split
double-counts something; fix the inputs, not the table.

### Ranking

Arms are ranked on the **production-shaped** column, not on the raw harness figure. The raw figure
stays in the table for continuity with the corpus, whose numbers are all raw. The report's share of
the total is expected to differ by arm — in test 4 the Panel run documents are 89–93 KB against
57–75 KB for the Skeptic line — so subtracting it moves the ratios, not just the totals.

### Lower-effort primary arm

One arm beyond the three #60 specifies, added by #68 as a measurement and nothing more: it adopts
lower effort nowhere. Every run in the corpus ran at the harness default effort. The `claude-api`
skill's model notes say `output_config.effort` is the first quality-trading lever after caching, that
lower effort produces fewer and more consolidated tool calls and terser output, and that the tradeoff
is workload-specific. The two redis Sonnet misses were reasoning failures — both primaries and one
verifier accepted the same false premise — of the kind lower effort would plausibly worsen, and the
corpus cannot say by how much.

**Arm:** `code-review-publish` (v5b) with the **primary one effort step below the harness default**
and every verifier batch at the default. Row label `v5b-effort-medium`.

**Targets and seeds:** three seeds on target (b), high-risk and adjudicated clean, where reasoning
depth is most likely to degrade; three seeds on target (c), the requirements omission in an unchanged
file, where search breadth is. Six runs. Same packets, same mirror, same model, same conditions as
the v5b cells on those targets; the arm differs from v5b in the primary's effort and in nothing else.

**How effort is set and why `medium`.** In Claude Code the effort is a harness setting, not skill
text. The `Agent` call carries `model` but no effort parameter; effort is set per sub-agent by the
`effort` field in an agent definition's frontmatter, which overrides the session level for that
sub-agent. The arm therefore dispatches its primary through a project-local definition that #60
creates for the grid and removes afterwards, at `.claude/agents/v5b-primary-effort-medium.md`:

```yaml
---
name: v5b-primary-effort-medium
description: code-review-publish primary at one effort step below the harness default (#68)
model: sonnet
effort: medium
---
```

**The definition must exist before the grid's session starts.** Claude Code watches agent
directories that existed when the session began; this repository has no `.claude/agents/` today, so
a definition written into a new directory mid-session is not loaded until restart, and a dispatch
naming it fails or falls back to the session effort. Either commit the file or write it, then launch
the session, or pass the same definition at launch with `--agents` as JSON carrying `description`,
`prompt`, `model`, and `effort`. Before the first cell, dispatch a trivial probe through the
definition and read `effort` from the probe's transcript as described under item 4 below; the grid
does not start until the probe shows `medium`. Record the probe's transcript path in
`comparison-data.md` under Effort verification.

Claude Code's documented default for `claude-sonnet-5` is `high`, so one step below is `medium`.
The default is confirmed at run time from the session header, which names the active effort beside
the model, and recorded in the run document; if the observed default is not `high`, the arm runs one
step below whatever is observed and the README's figure is corrected before the first cell. Verifier
batches are dispatched exactly as the v5b arm dispatches them, with no definition and no effort
override, so they inherit the default. **No verifier batch runs below the default, in this arm or any
other**: the verifier is the mechanism the corpus shows is most reasoning-sensitive.

**Recorded per run, beside the four scoring dimensions:**

1. Harness-reported tokens, metered as [above](#metering-per-run).
2. Tool-call count, the primary's own and each verifier's, from the `Agent` result's usage block
   where the harness reports one and self-reported otherwise, labelled as test 4 labels them.
3. Wall clock, start to end of the run.
4. The effort **as passed** (the definition's `effort` field, or "none; default" for the verifiers)
   and **as verified from the transcript**: every assistant line of a sub-agent transcript carries a
   top-level `effort` beside `message.model`, so the model check #60 already requires reads both
   fields from the same lines. Verify the whole transcript, not the first turns; a resumed agent can
   pick up a different level. A run whose verified effort differs from the effort passed is
   discarded and re-run, as an interrupted run is.

**Adoption rule, fixed here before any run.** Effort tiering by risk surface — lower effort on a
review whose diff touches no risk-surface path and whose review produces zero survivors, default or
higher otherwise — is adopted only if, across the six runs, the lower-effort arm shows **no loss on
dimension 2** (no false finding and no false acquittal that the v5b cells on the same target and seed
do not also show) **and loses no more than one ground-truth item** in total against those cells.
Otherwise the result is recorded in `evaluation.md` and the default stays. Meeting the rule
authorises a ticket proposing the tiering, not a change to skill text or harness defaults on the
strength of this arm alone.

**If the harness cannot pass effort per sub-agent** at the pinned commit — the `effort` field is
ignored, or the probe's and the primaries' transcripts show the default with the definition
confirmed loaded — `evaluation.md` records that with the harness version and the transcript
evidence, no run counts toward the arm, and #68 is closed as not testable. A definition that was
never loaded is a setup failure, not that evidence: fix the loading and probe again.

## Files

- `README.md` — this file; #60 adds targets, ground truth, conditions, and model verification
- `<target>/<arm>-seed<n>-payload.md` and `<target>/<arm>-seed<n>-run.md` — one pair per run
- `comparison-data.md` — side-by-side metadata with the production-shaped cost column
- `evaluation.md` — pass/fail against each #60 success criterion, plus the lower-effort arm's six
  runs and whether the #68 adoption rule was met; written by #60
- [`../tools/cost_split.py`](../tools/cost_split.py) — the metering script; `--self-test` checks it
