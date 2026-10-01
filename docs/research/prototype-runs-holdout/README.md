# Holdout evaluation — method

The directory is undated because it predates the runs. #60 may rename it to
`prototype-runs-<date>-holdout/` when the grid starts; the one link that points here by path, in
aggregate analysis §7 conclusion 8, moves with it.

## Interpretation note — 2026-09-05 (#131)

For new current-skill experiments, use [the one-shot method](../code-review-one-shot-method.md).
The rules and observations below remain the historical record, with these interpretation limits:

- Reviewers could not execute target tests; only the adjudicator could do so. The old grid does
  not measure execution-enabled review.
- `v5b-noverify` simulated unavailable verification, withholding mandatory candidates. It did
  not test a primary-only policy that permits publishing those findings.
- Criterion 2 requires at least three false-acquittal occurrences to decide. The reported 0/2
  is formally **not decidable** under that rule; adding a lower-effort occurrence mixes arms.
  The original evaluation's `FAIL` label is retained as historical interpretation, not the
  preregistered verdict. The two misses remain observed misses.
- The published-outcome restatement of the effort rule on 2026-09-05 was made after results.
  It is a policy deviation, not preregistration or a new experiment; #124 requires fresh matched
  evidence on the repaired policy before adoption.

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
`python3 snapshot-path-omitted/scripts/test_context_fingerprint.py` and
`python3 snapshot-path-omitted/scripts/validate_review.py --self-test` — and recording that they
passed at the pinned commit. That is CI's job once this repository has CI. Metering a run afterwards
with `cost_split.py`, including its `--self-test`, is the researcher's work outside the run and is
unaffected.

### Run artifacts

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

The orchestrator also maintains `<target>/<arm>-seed<n>-timing.json` as described below.

### Metering per run

**Timing events (added 2026-09-05, #130).** The orchestrator writes one JSON sidecar per run
as events happen. Use a timezone-aware clock (for example Python's
`datetime.now(timezone.utc).isoformat()`), with the same clock source for all three events:

1. Immediately before dispatching the root, create the sidecar with `completion_mode` and
   `root_dispatched_at`; leave the other events null.
2. When the final review payload passes validation, write `payload_validated_at`. If the payload
   changes and is validated again, replace this event with that final successful validation time.
3. After final publication succeeds, write `completed_at`. For production without publication,
   use mode `result` and record delivery of the final result. This holdout uses `render-only`:
   record the final rendered result's return, including the required research report, without a
   publication event. Payload latency remains separately available.

Example of a completed render-only sidecar (timestamps are illustrative):

```json
{
  "completion_mode": "render-only",
  "root_dispatched_at": "2026-09-05T12:00:00Z",
  "payload_validated_at": "2026-09-05T12:01:40Z",
  "completed_at": "2026-09-05T12:02:00Z"
}
```

These are the complete schema's keys; modes are `publication`, `result`, and `render-only`.
Missing events may be omitted or null; keep them unavailable when recording failed or a run
stopped. Use observed events, never timestamps guessed afterwards from narrative. For a re-review,
start a separate sidecar for that invocation. Pass `--timing <timing.json>` to the metering command;
exit `2` names unreadable input, invalid timestamps or ordering on stderr. Correct the input from
recorded evidence before pasting output; otherwise leave the event unavailable.

Each run document's Metadata section records:

1. **Billed usage from transcripts.** After the run, locate every transcript the run produced
   (the run's own sub-agent transcript plus one per sub-agent it spawned) and run
   `python3 docs/research/tools/transcript_usage.py <paths> --prices 2,10 --report <run.md> --timing <timing.json>`.
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
5. **Run timing:** paste the `RUN TIMING` block and link its sidecar. Report elapsed-to-payload
   and elapsed-to-completion seconds alongside the completion mode. The `TOTAL` block's **agent
   span sum** adds every transcript's first-to-last assistant span, including overlapping waits;
   it is not elapsed completion. Missing events print `unavailable` (JSON `null`).

Items 1, 4, and 5 come from the command above. Re-run that command with
`--row "<arm> seed <n>"` and paste the line into the billed-usage table in
[`comparison-data.md`](comparison-data.md), whose header is `transcript_usage.py --header` output.
Its legacy `Wall` column remains the agent span sum. Save `--json` output beside the sidecar for
elapsed comparisons; the legacy row deliberately carries no new timing columns.

Compute items 2–3, and the same split of the legacy context-size figure, with the sibling script so
every run document keeps the corpus's companion data in the same form:

```sh
python3 docs/research/tools/cost_split.py \
  --harness-total 281400 \
  --payload docs/research/prototype-runs-holdout/<target>/<arm>-seed<n>-payload.md \
  --report  docs/research/prototype-runs-holdout/<target>/<arm>-seed<n>-run.md \
  --instruction-load 40000 --repository-reads 150000 --private-records 30000
```

Paste its block into the run document verbatim. Re-run it with `--row "<arm> seed <n>"` and paste
that line into the legacy companion table in `comparison-data.md`, whose header is
`cost_split.py --header` output. This table preserves the self-reported split and historical
`subagent_tokens`; it does not determine the ranking. The script exits `1`
when the report or the sum of the reported parts exceeds the harness total, which means the split
double-counts something; fix the inputs, not the table.

### Lower-effort primary arm

One arm beyond the three #60 specifies, added by #68 as a measurement and nothing more: it adopts
lower effort nowhere. Every run in the corpus ran at the harness default effort. The `claude-api`
skill's model notes say `output_config.effort` is the first quality-trading lever after caching, that
lower effort produces fewer and more consolidated tool calls and terser output, and that the tradeoff
is workload-specific. The two redis Sonnet misses were reasoning failures — both primaries and one
verifier accepted the same false premise — of the kind lower effort would plausibly worsen, and the
corpus cannot say by how much.

The billed figures from #89 make the arm the first efficiency cell to run. In the test-4 v5a run,
per request from the transcripts
([test 4 `comparison-data.md`, Billed usage](../prototype-runs-2026-09-01-test-4/comparison-data.md#billed-usage-added-2026-09-89)),
the primary's thinking was 48,085 of its 89,900 output tokens (53%), about $0.48 of its $2.00 at
Sonnet 5 list (24%), and the verifier's 6,938 of 11,659. Output is billed at five times the input
rate and wall clock follows output, so effort is the third-largest cost lever after turn count and
the context each request replays (#90, #91), and the only one that acts on output tokens. (#68's
body quotes the per-line sums #89 first reported, 50,819 of 93,939; the per-request figures here
supersede them, as the test-4 table explains.) Because `transcript_usage.py` reports thinking
tokens per sub-agent, the arm's effect is read directly from that column rather than inferred from
totals.

**Arm:** `legacy reviewer` (v5b) with the **primary one effort step below the harness default**
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
description: legacy reviewer primary at one effort step below the harness default (#68)
model: sonnet
effort: medium
---
```

**The definition must exist before the grid's session starts.** Claude Code watches agent
directories that existed when the session began, so a definition written into a new directory
mid-session is not loaded until restart, and a dispatch naming it fails or falls back to the
session effort. The definition is committed at
`.claude/agents/v5b-primary-effort-medium.md` (committed in PR #114, removed after the grid)
(#60's first pull request) so every grid session started with it loaded; both grid-only definitions were removed once the arm's six cells had run, so they exist only in the history of that branch. Before the first cell, dispatch a trivial probe through the
definition and read `effort` from the probe's transcript as described under item 4 below; the grid
does not start until the probe shows `medium`. Record the probe's transcript path in
`comparison-data.md` under Effort verification.

Claude Code's documented default for `claude-sonnet-5` is `high`, so one step below is `medium`.
The default was confirmed from a plain-dispatch transcript (378 assistant lines at `high`) before the
grid, and the definition's probe showed `medium`. **Correction recorded on 2026-09-04, before any
valid cell of this arm ran:** a child agent inherits its *parent's* effort, not the session default,
so a verifier batch dispatched by a `medium` primary as a plain `Agent` call also runs at `medium`.
The first two cells of this arm (seed 1 on (b) and (c)) did exactly that, were discarded under the
rule below, and their seed numbers were retired. Verifier batches in this arm are therefore dispatched
through a second definition, `.claude/agents/v5b-verifier-effort-high.md` (added during the grid, removed after it)
(`model: sonnet`, `effort: high`), which pins them at the default; a nested probe (a `medium` primary
spawning one such verifier) verified `high` on the child before the first valid cell. The `v5b` arm's
verifiers are plain `Agent` calls, so the two arms' verifiers differ only in that definition's
one-paragraph system prompt. **No verifier batch runs below the default, in this arm or any other**:
the verifier is the mechanism the corpus shows is most reasoning-sensitive.

**Recorded per run, beside the four scoring dimensions:**

1. Billed usage from the transcripts, metered as [above](#metering-per-run) with
   `transcript_usage.py`: one block per sub-agent (the primary and each verifier batch) plus the
   total, including the `Thinking` column, which is the figure the arm exists to move. The legacy
   `subagent_tokens` figure stays beside it as the metering rule says.
2. Turn count and tool-call count, the primary's own and each verifier's, from the same script's
   `Turns` and `Tool calls` columns (requests and distinct `tool_use` ids, as the test-4 billed
   table defines them), not from the `Agent` result's usage block or self-report.
3. Timing: each sub-agent's assistant timestamp span, the agent span sum, and the explicit
   elapsed-to-payload and elapsed-to-completion seconds with completion mode from the
   [timing sidecar](#metering-per-run). Compare elapsed values only with the same completion mode.
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

**Restated 2026-09-05, after the runs, at the maintainer's direction (deviation).** The rule above
counts every ledger row. The arm's one failure under it was a ledger-level false acquittal that the
zero-survivor batch re-opened and the run then re-falsified and dropped before publication
((b) seed 4, C2; quoted in [`evaluation.md`](evaluation.md#the-lower-effort-arm-68)), so the
published review was identical to the controls'. The restated rule counts **published outcomes**:
no false finding, no false acquittal that survives to publication, and no more than one lost
ground-truth item against the `v5b` cells on the same targets. The pre-registered ruling and the
restated ruling are both reported in `evaluation.md`. Meeting the restated rule authorised
[#124](https://github.com/kamui/skills/issues/124), which proposes the shape the arm measured
(primary at `medium`, every verifier batch pinned at `high`, on every diff) rather than the
risk-surface tiering this paragraph describes, and which gates any default change on three
seeds of the arm on target (a).

Whether or not the rule is met, `evaluation.md` reports the arm's cost effect per target as each
figure's median over the arm's three seeds against the same median for the v5b cells on that
target, for the eight figures items 1–3 record: thinking tokens, output tokens, turns, tool calls,
per-sub-agent wall, elapsed time, and billed and production-shaped cost. The quality result
(dimensions 1–4) and the cost result are stated separately, so a saving that fails the rule is
still on record for a later ticket.

**If the harness cannot pass effort per sub-agent** at the pinned commit — the `effort` field is
ignored, or the probe's and the primaries' transcripts show the default with the definition
confirmed loaded — `evaluation.md` records that with the harness version and the transcript
evidence, no run counts toward the arm, and #68 is closed as not testable. A definition that was
never loaded is a setup failure, not that evidence: fix the loading and probe again.

**Result (recorded 2026-09-05, after the grid).** The harness passed effort per sub-agent and six
valid cells ran. Under the pre-registered rule the arm was **not met** on its letter: one
ledger-level false acquittal on (b) seed 4 that no control shares, re-opened and resolved before
publication, so the published outcome was unchanged. Under the restated rule in the deviation
paragraph above it is **met**, and the maintainer closed #68 on 2026-09-05 with both rulings.
No default changes on this arm's evidence: the restatement authorises
[#124](https://github.com/kamui/skills/issues/124), the measured shape (primary at `medium`, every
verifier batch pinned at `high`), which gates any default change on three seeds of the arm on
target (a). The cost effect is on record in
[`evaluation.md`, The lower-effort arm](evaluation.md#the-lower-effort-arm-68): per-target medians
of roughly −40% billed dollars, −46% to −63% thinking tokens, and −22% to −30% primary assistant
timestamp spans against the `v5b` cells. **Timing correction, 2026-09-05 (#130):** those last
figures were originally called elapsed time but were reconstructed at close-out from transcript
timestamps. They are labelled proxies, not dispatch-to-payload or dispatch-to-completion
measurements. Nested verifier spans explain why their sum over-counts waits; they do not establish
the missing root boundaries. The original numbers remain historical data in the comparison and
evaluation; exact elapsed metrics are unavailable for these runs.

## Targets

Six merged, public pull requests, none in a repository or of a shape any living prototype's design
was tuned on (the corpus targets are `kamui/shortlist#66`, `redis/redis#15680`,
`tokio-rs/tokio#7757`, `microsoft/playwright#29698`). Each was selected by shape, then pinned,
then adjudicated from upstream history and, for (b), by execution, all before any run. Every SHA
below was read from the GitHub API on 2026-09-04 and can be re-read with
`gh api repos/<owner>/<repo>/pulls/<n> --jq '{head:.head.sha,base:.base.sha,merge:.merge_commit_sha}'`
and `gh api repos/<owner>/<repo>/compare/<base>...<head> --jq .merge_base_commit.sha`.

| Shape | Target | Head | Merge-base | Diff | Recall items | Band |
| --- | --- | --- | --- | --- | --- | --- |
| (a) concurrency, reverted, re-landed on an invariant | [`hyperium/hyper#3952`](#target-a--hyperiumhyper3952-a-concurrency-fix-that-hot-looped-was-reverted-and-re-landed-on-an-invariant) | `f2aa734` | `f9f8f44` | 3 files, +270/−2 | GT-a1 | Changes Requested |
| (b) high-risk, clean | [`hashicorp/raft#581`](#target-b--hashicorpraft581-a-failover-fix-adjudicated-clean-by-execution-and-history) | `cb62297` | `1462fd5` | 3 files, +75/−7 | none | Approved |
| (c) issue requires an untouched file | [`python/typeshed#9458`](#target-c--pythontypeshed9458-a-stub-bump-whose-originating-issue-required-a-file-the-diff-never-touched) | `55dfb45` | `8365b1a` | 10 files, +41/−36 | GT-c1 (+T-c2, T-c3) | Changes Requested |
| (d) new API, deferral, reshaped | [`astral-sh/uv#4424`](#target-d--astral-shuv4424-a-new-option-whose-value-names-were-questioned-deferred-as-preview-and-reshaped-twelve-days-later) | `a2e6b9c` | `e783a79` | 22 files, +178/−36 | GT-d1 (+T-d2) | Needs Information / Approved |
| (e) benchmark claim | [`pola-rs/polars#24771`](#target-e--pola-rspolars24771-a-parser-rewrite-justified-by-a-single-machine-benchmark) | `2db2ee1` | `b3241e0` | 3 files, +156/−130 | GT-e1 (+T-e1) | Needs Information |
| (f) reviewed twice on a fork | [`spf13/cobra#1938`](#target-f--spf13cobra1938-one-pull-request-reviewed-twice-on-a-repository-this-program-controls) | `97b7001` → `1107319` | `3d8ac43` | 4 files, +116/−11 → +237/−11 | GT-f1, GT-f2 (+GT-f3) | Changes Requested → Approved |

Vocabulary used in every target section: **GT-n** is a ground-truth item confirmed by an
upstream event (a fix, revert, withdrawal, or issue) or mechanically checkable in the pinned
diff; **T-n** is an item the adjudicator established from the pinned code or the upstream trees
that no upstream event confirms, counted as true if a run raises it and not counted against a
run that does not; **Not ground truth** lists the tempting claims that are false or sub-threshold,
which dimension 2 and the calibration band score against. The **band** is the status and the
priority/action range a correct review reaches with the pinned inputs and no execution.

### Target (a) — `hyperium/hyper#3952`: a concurrency fix that hot-looped, was reverted, and re-landed on an invariant

[`hyperium/hyper#3952`](https://github.com/hyperium/hyper/pull/3952) "fix(http1): poll_loop writes
when ready", author `lthiery`, an external contributor. Opened 2025-09-11, **merged 2025-11-10** by
maintainer `seanmonstar` with one `APPROVED` review, released in hyper `v1.8.0` the next day.
Tokio's shape (test 3) in a different repository: a small change to a scheduler-like loop that
shipped a 100 % CPU spin, was reverted within three days, and was re-landed five months later
with a fix that restores a rule rather than patching a branch.

| | |
| --- | --- |
| head | `f2aa734e5699a91fc20f1178e38af7b1e374bdbc` |
| base ref | `master` (pinned locally to the merge-base) |
| base SHA / merge-base | `f9f8f44058745d23fa52abf51b96b61ee7665642` (identical; the branch was rebased) |
| diff | 3 files, +270 / −2, two commits |
| originating issue | none; the body is the author's own report ("I ran into some lockups running hyper with some custom futures") |
| prior review state | 3 review submissions (`seanmonstar` COMMENTED 2025-10-28, `lthiery` COMMENTED 2025-10-31, `seanmonstar` APPROVED 2025-11-10), 2 inline comments on the test's complexity, 2 conversation comments; nothing about the loop logic |
| merged | `true`; retrospective, non-publishing |

Changed-file manifest:

```
M	Cargo.toml                 (+6   −0)   tracing-subscriber dev-dependency, [[test]] entry
M	src/proto/h1/dispatch.rs   (+15  −2)   the change under review
A	tests/ready_stream.rs      (+249 −0, new file)
```

The reviewable surface is fifteen lines. In `Dispatcher::poll_loop`, the `for _ in 0..16` loop
previously returned `Ready(Ok(()))` as soon as `wants_read_again()` was false, trusting the
wakers `poll_read`/`poll_write` registered. The change computes
`conn_ready = self.poll_flush(cx)?.is_ready()`, adds
`wants_write_again = self.can_write_again() && conn_ready` where `can_write_again()` is
`self.body_rx.is_some()`, and keeps looping while either side "wants again"; after sixteen
iterations it `yield_now`s.

#### Ground truth

**GT-a1 — the loop spins at 100 % CPU for any writer whose `poll_flush` is always ready
(in-diff; upstream-confirmed in 3 days).** `conn_ready` is derived from `poll_flush`, not
`poll_write`, and `can_write_again()` is true for the whole life of a streaming body. For the
common unbuffered `rt::Write` implementation, whose `poll_flush` returns `Ready` unconditionally,
`wants_write_again` is therefore true on every iteration while `poll_write` is `Pending`; the
loop runs its sixteen iterations, `task::yield_now` re-wakes the task immediately, and the task
spins with no progress until the write side becomes ready on its own.
[`#3976`](https://github.com/hyperium/hyper/issues/3976) (2025-11-13, "after upgrading `hyper`
to version 1.8.0, the CPU usage spikes to 100% regardless of how many tokio worker threads I
enable"; large-file forwarding, ~300 concurrent requests) was filed two days after release;
[`#3977`](https://github.com/hyperium/hyper/pull/3977) reverted the commit the same day
(`4492f31e9429c34166da5a069c00b65be20e4a02`, released as `v1.8.1`).

Everything needed is in the diff plus one function: that `conn_ready` comes from flush while the
comment beside it talks about writing, that `can_write_again()` cannot go false while a body
exists, and that the loop's only other exit is `yield_now`. Two human reviewers, including the
maintainer, did not see it.

**The invariant the re-land restores.** [`#3988`](https://github.com/hyperium/hyper/pull/3988)
"fix rare missed write wakeup on connections v2" (merged 2026-04-22,
`743a3ba0706fde95e2095ad42ffefe219d807117`, head `a416aa8be05e36767830df2180f9aa78f6b412e7`,
shipped in `v1.10.0`) keeps the intent and adds: *the loop may continue for the write side only
when `poll_write` itself has been polled and reported ready on this pass; flush readiness is not
write readiness; and every exit that makes no progress must be a `Pending` whose waker
`poll_write` or `poll_read` registered.* Concretely it records `write_ready` from `poll_write`,
and when the loop would continue only because of `wants_write_again` with `write_ready` false, it
re-polls `poll_write` and returns `Ready(Ok(()))` if that pends ("If we simply proceeded, the case
of an unbuffered writer where flush is always ready would cause us to hot loop"). The re-land's
body states the rule: "if neither write nor flush are pending, then nothing will wake us."

Dimension 4 scores the published `Change` for GT-a1 as `invariant` when it says the
continue-decision must be gated on the write half's own readiness (poll `poll_write` again and
yield on `Pending`, or equivalently never let flush readiness stand in for write readiness);
`branch` when it proposes a workaround that leaves the rule broken — lowering the iteration
bound, adding a backoff, detecting unbuffered writers by type, or treating `body_rx` emptiness as
the condition; `none` when GT-a1 is not found.

(The re-land itself later needed [`#4143`](https://github.com/hyperium/hyper/pull/4143)
(`f660f5bf6eed3fe793f899507ff5bb9e266d4b0d`, 2026-08-07): its re-check's second `poll_write`
returned before flushing what it buffered. That is a defect of the re-land, not of this head, and
is not ground truth here; it is recorded so an adjudicator does not credit a run for "predicting"
it.)

#### Not ground truth

- **The sixteen-iteration bound and `yield_now` starving other futures.** Pre-existing at the
  merge-base and discussed in the review record; a `must-fix` on it is a false finding, a
  `consider` is over-band.
- **The new test needs `--cfg hyper_unstable_tracing` and a `tracing-subscriber` dev-dependency.**
  Accurate, hygiene-level; at most `consider`.
- **"The scenario the PR fixes violates the `Future` contract."** The author's own stated doubt
  (a future returning `Pending` once and then completing without a wake). A question is
  admissible; a finding that the fix is unnecessary is over-band, and upstream kept the intent.

#### Calibration band

`Changes Requested`. GT-a1 is `must-fix` at P0 or P1, `kind=concurrency`; P2 is `under`. No other
`must-fix` is in band. A run whose only finding concerns the test file or the dev-dependency is
`under`. A run that approves is `under`.

#### Mirror

Push only `f2aa734e5699a91fc20f1178e38af7b1e374bdbc` and
`f9f8f44058745d23fa52abf51b96b61ee7665642`. Negative checks recorded per clone:
`2377b893f6e64ca9878e4f25d1472b96baa7e3ea` (merge), `4492f31e9429c34166da5a069c00b65be20e4a02`
(revert), `743a3ba0706fde95e2095ad42ffefe219d807117` and
`a416aa8be05e36767830df2180f9aa78f6b412e7` (re-land), `f660f5bf6eed3fe793f899507ff5bb9e266d4b0d`
(#4143).

### Target (b) — `hashicorp/raft#581`: a failover fix adjudicated clean by execution and history

[`hashicorp/raft#581`](https://github.com/hashicorp/raft/pull/581) "Fix rare leadership transfer
failures when writes happen during transfer", author `ncabatoff` (HashiCorp). Opened 2023-11-23,
**merged 2023-12-04** by squash, released in `v1.6.1`. The maintainer's review raised, in
writing, exactly the objection a static reviewer is tempted to publish, and accepted the
author's answer; the test suite passes at the head; nothing in the following year touched the
changed logic except unrelated features.

| | |
| --- | --- |
| head | `cb622973cd2c65dd2752c49d0520f2a3894b2d91` — not an ancestor of `main` (squash merge); fetch it from `refs/pull/581/head`, which GitHub retains |
| base ref | `main` (pinned locally to the merge-base) |
| base SHA / merge-base | `1462fd5e80ad0eb38748f68198505025cb2c96d8` (identical) |
| diff | 3 files, +75 / −7, seven commits |
| originating issue | none; the body states the problem ("after we send the TimeoutNow during a leader transfer, we remain the leader for a little while. During that time we allow writes, which can result in the upcoming election being lost by our chosen target") and the fix ("wait for up to ElectionTimeout after the TimeoutNow before we allow writes to proceed") |
| prior review state | `banks` APPROVED 2023-11-27 with two inline questions; `ncabatoff` two replies; no conversation comments |
| merged | `true`; retrospective, non-publishing |

Changed-file manifest:

```
M	raft.go        (+14 −1)   leaderLoop's transfer goroutine: wait after TimeoutNow succeeds
M	raft_test.go   (+57 −3)   TestRaft_LeadershipTransferWithWrites (new) and an assertion fix
M	testing.go     (+4  −3)   GetInState re-polls before logging; highestTerm added to the log line
```

The change is one `else` branch. When the transfer goroutine's `doneCh` reports that
`TimeoutNow` was delivered, the old code responded to the future immediately, which released
`leadershipTransferInProgress` and let `applyCh` writes proceed on the old leader, so the
target could lose the election it was just told to start. The new code waits inside that
branch for either `ElectionTimeout` (then responds with "leadership transfer timeout") or
`leftLeaderLoop` (the old leader stepped down; responds `nil`), keeping writes blocked in
between.

#### Adjudication: clean

**Executed.** At the pinned head, on 2026-09-04, `go1.27.0 darwin/arm64`:

```
$ go test ./...
ok  	github.com/hashicorp/raft	125.451s
?   	github.com/hashicorp/raft/bench	[no test files]
```

and the two CI configurations, `go test -race --tags batchtest ./...`, on the same head:

```
ok  	github.com/hashicorp/raft	117.222s
?   	github.com/hashicorp/raft/bench	[no test files]
```

Both runs exit 0 with no failed test.

**History.** No commit touched `raft.go`, `raft_test.go`, or `testing.go` between the merge
and 2024-03-04, and no issue or pull request in the repository references #581. The next
`raft.go` commits are the pre-vote extension (`181475cc5`, #530, 2024-06-06) and its two
follow-ups (#605, #609), unrelated to transfer. The transfer branch added here is unchanged on
`main` as of 2026-09-04.

#### The ground-truth surface (for dimension 2)

There is no GT item to recall. Dimension 2 checks every acquittal whose `kind` is `bug`,
`concurrency`, `invariant`, or `security` and whose evidence pointer is in `raft.go`'s transfer
goroutine (`leaderLoop`, the `leadershipTransferCh` case) or the `applyCh` gating on
`getLeadershipTransferInProgress()`, against the pinned code. A false acquittal is one whose
stated premise the code contradicts; a false re-open is a clean-verdict or related-acquittal
ruling that re-opens a row whose premise the code supports.

#### Not ground truth — the tempting findings, and why each is false

- **"The nested `select` waits a second `ElectionTimeout`, doubling transfer latency, and
  duplicates the `leftLeaderLoop` path."** The reviewer's own question. The wait is the fix:
  writes must stay blocked until the old leader has actually stepped down. The goroutine is not
  the leader loop, so nothing in `leaderLoop` blocks on it; `leftLeaderLoop` is closed by a
  `defer` registered in the same case, so the inner `select` always terminates when leadership
  is lost. The reviewer accepted the author's answer ("I tried that. It got messy… I decided this
  was clearer") and approved.
- **"Responding `leadership transfer timeout` after `TimeoutNow` succeeded reports a failure
  for a transfer that may still complete."** The outer `select` already had that semantics at
  the merge-base; the error tells the caller the transfer was not observed to complete within
  the window, which is the documented contract of `LeadershipTransfer`.
- **"The `defer` closing `leftLeaderLoop` accumulates one closure per transfer."** Pre-existing
  at the merge-base and bounded by the number of transfers in one leadership; not introduced.
- **"`future.respond` can be called twice."** Each `select` arm responds once and the arms are
  exclusive; the outer arms that respond also drain `doneCh`, unchanged.
- **`GetInState` re-polls `pollState` after the stability wait**, so the returned set can differ
  from the set the timer logic observed. Accurate; the commit message says why ("GetInState…
  is racy"). Test-helper hygiene: `consider` at most, never `must-fix`.
- **The new test's non-determinism.** The author says it "can still fail if I up the
  concurrency enough"; the reviewer asked and accepted. An observation is in band.

#### Calibration band

`Approved (advisory)`. Zero `must-fix` findings; a `consider` on the test helper or an
observation on the test's determinism is in band. Any `must-fix` is `over` and a false finding.
`Needs Information` is `over`: no fact here is outcome-changing and statically unresolvable.
Dimension 4 is `n/a` on a clean run and `none` on a run that publishes a fix.

#### Mirror

Fetch `refs/pull/581/head` into the staging mirror, then push only
`cb622973cd2c65dd2752c49d0520f2a3894b2d91` and `1462fd5e80ad0eb38748f68198505025cb2c96d8`.
Negative checks per clone: `62eaa1c192d4c09c90caa5e227177eb9205a6267` (merge), `181475cc5`
(#530). Execution stays forbidden inside the runs: the suite above is the adjudicator's, run
outside every sandbox.

### Target (c) — `python/typeshed#9458`: a stub bump whose originating issue required a file the diff never touched

[`python/typeshed#9458`](https://github.com/python/typeshed/pull/9458) "Bump redis to 4.4.0",
author `juanamari94`, a first-time contributor. Opened 2023-01-04, **merged 2023-01-05** by
maintainer `AlexWaygood`, who also pushed one commit to the branch (the `credentials.pyi` file).
The originating reference is stubsabot's release pull request, whose specification is the linked upstream
diff. The stub for the package's own `__init__` was not updated to match the runtime package's
new public names, CI did not catch it, and a user reported it twelve weeks later.

| | |
| --- | --- |
| head | `55dfb451101480275ae05f2f08d1a899a691a77d` |
| base ref | `main` (pinned locally to the merge-base) |
| base SHA | `70025c372346288675437fc0bd273db84cc0b3d5` (the PR's recorded base) |
| merge-base | `8365b1aaefd46d506ca0dfe73e9721da2d03c566` — `main` moved before the merge, so the merge-base is not the recorded base; the packet pins the merge-base and states both |
| diff | 10 files, +41 / −36, 19 commits (most are `pre-commit-ci` autofixes) |
| originating reference | [`#9329`](https://github.com/python/typeshed/pull/9329) "[stubsabot] Bump redis to 4.4.0", linked by `Closes #9329`. It is stubsabot's own **pull request** (closed unmerged when #9458 merged), not an issue, so the forge's closing-issue resolution does not return it and the packet carries its body and two comments verbatim as the originating reference (`issues=python/typeshed#9329`). Its body lists the release, the changelog, `Diff: https://github.com/redis/redis-py/compare/v4.3.5...v4.4.0`, and stubsabot's summary ("5 public Python files have been added: `redis/credentials.py`, …; 31 files included in typeshed's stubs have been modified or renamed") |
| prior review state | 2 reviews by `AlexWaygood` (COMMENTED with one inline `suggestion`, then APPROVED "Thanks, this is really helpful!"), 17 conversation comments (seven `mypy_primer` bot reports, the rest onboarding guidance about `METADATA.toml` and a stubtest error) |
| merged | `true`; retrospective, non-publishing |

Changed-file manifest:

```
M	stubs/redis/METADATA.toml                      (+1  −1)   version = "4.4.0"
M	stubs/redis/redis/asyncio/client.pyi           (+5  −2)
M	stubs/redis/redis/asyncio/connection.pyi       (+7  −24)
M	stubs/redis/redis/asyncio/sentinel.pyi         (+1  −1)
M	stubs/redis/redis/backoff.pyi                  (+4  −4)
M	stubs/redis/redis/client.pyi                   (+4  −0)
M	stubs/redis/redis/cluster.pyi                  (+2  −1)
M	stubs/redis/redis/commands/core.pyi            (+3  −3)
M	stubs/redis/redis/connection.pyi               (+3  −0)
A	stubs/redis/redis/credentials.pyi              (+11 −0, new file)
```

**What the reference requires.** A stubsabot bump's specification is the upstream diff it links:
the stubs must follow the runtime package between the two tags. typeshed's `CONTRIBUTING.md` at
the merge-base (lines 322–323) states what a stub must include: "All objects listed in the
module's documentation. All objects included in `__all__` (if present)." The runtime diff
changes `redis/__init__.py` and `redis/asyncio/__init__.py`, the two files that define the
package's public surface, and the stub tree mirrors the package tree file for file
(`stubs/redis/redis/__init__.pyi` reproduces the runtime `__all__` name by name).

**Why CI passed.** typeshed's stubtest ran with `ignore_missing_stub` defaulting to true until
[`#9779`](https://github.com/python/typeshed/pull/9779) (2023-02-20), so a runtime name absent
from the stub was not an error; the allowlist at head contains nothing about these names.

**The packet materializes the issue's linked diff.** Runs have no network, so the packet
directory for this target also carries the two endpoints of the issue's `Diff:` link as
read-only source trees, `upstream/redis-py-4.3.5/` and `upstream/redis-py-4.4.0/`
(the tagged trees, complete), and `upstream/redis-py-4.3.5...4.4.0.diff` (the compare's
`.diff`, 649 KB, 250 KB under `redis/`). The packet names them as the issue's linked
specification and nothing else; which files the run reads is the run's own discipline, and the
run document records what it read. No file in the upstream trees is executed.

#### Ground truth

**GT-c1 — `stubs/redis/redis/__init__.pyi` was not updated for the two new public names
(upstream-confirmed, 12 weeks).** In 4.4.0, `redis/__init__.py` imports `CredentialProvider` and
`UsernamePasswordCredentialProvider` from the new `redis.credentials` and adds both to
`__all__`. The diff adds `credentials.pyi` with both classes and leaves `__init__.pyi` untouched,
so `redis.CredentialProvider` — the spelling redis-py's own documentation uses — does not type
check. [`#9980`](https://github.com/python/typeshed/issues/9980) (2023-03-29, `error: Name
"redis.CredentialProvider" is not defined`) was fixed the same day by
[`#9982`](https://github.com/python/typeshed/pull/9982)
(`509ba05c27218d0a1e509c6e2b180eb115ce9be9`, one file, +6 / −1: "Adds the missing classes
`CredentialProvider` and `UsernamePasswordCredentialProvider` to `__init__.py`"). Checkable by
reading the issue's linked diff for `redis/__init__.py` and the stub at head. `kind=requirement`.

**T-c2 — `default_backoff` is missing from both package stubs (adjudicated true; never fixed).**
The same runtime diff adds `default_backoff` (from `redis.backoff`) to `__all__` in
`redis/__init__.py` and `redis/asyncio/__init__.py`. Neither `__init__.pyi` gained it at head,
`backoff.pyi` at head does not define it, #9982 did not add it, and typeshed removed the redis
stubs entirely on 2024-11-30 ([`#13157`](https://github.com/python/typeshed/pull/13157)) when
redis-py shipped inline types, so no upstream commit ever confirmed it.

**T-c3 — `redis.exceptions.MaxConnectionsError` is missing from `exceptions.pyi` (adjudicated
true; never fixed).** 4.4.0 adds the public class `MaxConnectionsError(ConnectionError)`;
`exceptions.pyi` was not touched and does not define it at head.

Recall on (c) is scored on GT-c1. T-c2 and T-c3 are the same class of omission found by the
adjudicator from the same source; a run that raises either has a true finding. **Any other
omission a run raises is adjudicated at scoring time against the two upstream trees:** true when
the name is public (in `__all__`, documented, or an un-underscored module-level class or
function) and absent from the corresponding stub; false when the stub has it or the name is
private. Under typeshed's conventions a missing or `Incomplete` *annotation* is not a defect;
a missing *name* is.

#### Not ground truth

- **The `# type: ignore[override]` on `SentinelManagedConnection.read_response`.** The
  maintainer's own suggestion, applied; an accepted typeshed pattern. A finding is false.
- **`typing.pyi` still says `ExpiryT = float | timedelta` while 4.4.0 changed the runtime alias
  to `int | timedelta`.** Accurate; the stub is more permissive than the runtime, which typeshed
  tolerates. `consider` at most; `must-fix` is over.
- **The stub's `asyncio/connection.pyi` deletions (−24).** They mirror the runtime's removal of
  the parser classes from that module; a finding that the stub dropped public names must be
  checked against the 4.4.0 tree, where those names are gone too.
- **Nineteen commits / autofix noise.** Not evidence.

#### Calibration band

`Changes Requested`. GT-c1 `must-fix` at P2 or P3 (`kind=requirement` or a repository-rule
finding citing `CONTRIBUTING.md`); `consider` is `under`. T-c2 and T-c3 in band at P3, either
action. `Approved` is `under`. A `must-fix` on a Not-ground-truth item is `over` and false.

#### Mirror

Push only `55dfb451101480275ae05f2f08d1a899a691a77d` and
`8365b1aaefd46d506ca0dfe73e9721da2d03c566`. Negative checks per clone:
`605378de6e80c90b39b97c183acbb48a5236fc89` (merge), `509ba05c27218d0a1e509c6e2b180eb115ce9be9`
(#9982), `0a2da0194` (#13157). The upstream trees are checked out from redis-py's `v4.3.5` and
`v4.4.0` tags into the packet directory, not into the clone, and their `.git` directories are
removed so no later redis-py history is reachable.

### Target (d) — `astral-sh/uv#4424`: a new option whose value names were questioned, deferred as preview, and reshaped twelve days later

[`astral-sh/uv#4424`](https://github.com/astral-sh/uv/pull/4424) "Expose `toolchain-preference`
as a CLI and configuration file option", author `zanieb`, a uv maintainer. Opened and **merged
2024-06-20**, on one `APPROVED` review by `BurntSushi`. Playwright's shape (test 4) in a
different repository: the approver questioned the API's shape in the approving review, the
author deferred the question explicitly because the surface was preview, five releases shipped
it, and the author reshaped it.

| | |
| --- | --- |
| head | `a2e6b9c6bd0257510240886549ba9e3623299739` |
| base ref | `main` (pinned locally to the merge-base) |
| base SHA / merge-base | `e783a79955a3a4eb6a4c546f51f89e88b64047bb` (identical) |
| diff | 22 files, +178 / −36, one commit; nineteen of the files are one- to four-line plumbing of the new value through each subcommand |
| originating issue | none; the body says "Exposes the option added in #4416", which is not a closing reference (`issues=none`) |
| prior review state | 1 `APPROVED` review whose body raises the naming question; 0 inline comments; 5 conversation comments (the bikeshed) |
| merged | `true`; retrospective, non-publishing |

Changed-file manifest (the substantive files):

```
M	crates/uv-toolchain/src/discovery.rs      (+7  −4)   ToolchainPreference gains serde/clap/schemars derives; from_settings → default_from
M	crates/uv-settings/src/settings.rs        (+2  −1)   tool.uv.toolchain-preference
M	crates/uv-settings/src/combine.rs         (+2  −1)
M	crates/uv/src/cli.rs                      (+5  −1)   --toolchain-preference (global)
M	crates/uv/src/settings.rs                 (+34 −10)  resolution and the per-command preview default
M	crates/uv/src/main.rs                     (+18 −2)
M	crates/uv/src/commands/project/mod.rs     (+14 −4)   also EnvironmentPreference::Any → OnlySystem
M	crates/uv/tests/show_settings.rs          (+16 −0)
M	uv.schema.json                            (+49 −0)   generated
   + 13 subcommand files, Cargo.lock, two Cargo.toml
```

The new public surface is the global flag `--toolchain-preference` and the config key
`tool.uv.toolchain-preference`, with values `only-managed`, `prefer-installed-managed`
(default), `prefer-managed`, `prefer-system`, `only-system`, all documented in the generated
`uv.schema.json`.

**The deferral, verbatim.** `BurntSushi`'s approving review (2024-06-20T17:21:53Z):

> One other possible downside is redundancy here. Namely, `--toolchain-preference
> prefer-system` has "prefer" twice in it, but arguably is just as clear if "prefer" only
> appeared once. Not quite sure what the right answer is there.

`zanieb`, four minutes later: "I'm fine adjusting this later if we need to since it's in
preview." Then: "I guess another option is I drop the `prefer` prefix so we'd have
`toolchain-preference = managed | system | only-managed | only-system | installed-managed`",
to which `BurntSushi` replied "I think that's probably okay." The PR merged with the `prefer-`
values one hour later.

#### Ground truth

**GT-d1 — the value vocabulary was wrong and was reshaped before the option left preview
(upstream-confirmed, 12 days).** [`#4602`](https://github.com/astral-sh/uv/pull/4602) "Drop
`prefer` prefix from `toolchain-preference` values" (merged 2024-07-02,
`c0a06a2c1b823ea8b889623597b707ee65782c70`, 4 files, +24 / −25), by the same author: "This was
discussed in the original pull request at …/pull/4424 … I think we can drop the prefix." Between
the two, tags `0.2.14` (2024-06-24) through `0.2.18` (2024-06-29) shipped the `prefer-*` values;
`0.2.19` (2024-07-02) shipped the reshaped ones. The following day
[`#4735`](https://github.com/astral-sh/uv/pull/4735) renamed the whole vocabulary
(`toolchain` → `python`, so `--python-preference`), and
[`#5637`](https://github.com/astral-sh/uv/pull/5637) (2024-07-31) replaced the `installed`
value again; the surface added here survived under its original names for twelve days.

The correct disposition is the one the rubric's gate 6 and the verifier's step 5 describe:
approval is provisional for unreleased public API surface, and the explicit deferral marks the
question open. A published `[Question]` on the value naming (or a `consider` finding citing the
deferral) is `found`; the naming in the ledger, acquitted because the approver accepted it, is
`acquitted` — the playwright GT-2 pattern this target exists to re-test; nothing is `not raised`.

**T-d2 — an undescribed behavior change rides along (adjudicated; intent unverifiable).**
`find_interpreter` in `commands/project/mod.rs` changes `EnvironmentPreference::Any` to
`EnvironmentPreference::OnlySystem` while threading the new preference through. The body does
not mention it; it changes which interpreters project commands may discover. No upstream commit
reverted it in the 90-day window. A question is in band; a `must-fix` asserting it is a bug is
`over` (the change is plausibly deliberate); a `consider` noting the undocumented change is in
band.

#### Not ground truth

- **`uv.schema.json` is stale.** It is not: the +49 lines match the enum's serde
  `rename_all = "kebab-case"` names and doc comments. A drift finding is false.
- **"Twenty-two files is too large a change."** Size is not a defect.
- **The `TODO(zanieb)` forcing preview defaults for project, toolchain, and tool commands.**
  Self-documented and consistent with the repository's preview convention; an observation at
  most.
- **"`installed-managed` is undocumented."** All five values are in the schema and the enum
  doc comments.

#### Calibration band

`Needs Information` (GT-d1 as a question) or `Approved (advisory)` with GT-d1 as a `consider`
are both in band; `Changes Requested` is `over` unless a verified `must-fix` exists on a
surface not listed above, which the adjudicator does not expect. `Approved` with GT-d1 absent
or acquitted is `under`.

#### Mirror

Push only `a2e6b9c6bd0257510240886549ba9e3623299739` and
`e783a79955a3a4eb6a4c546f51f89e88b64047bb`. Negative checks per clone:
`93c6e0df56d9a9e05e20cce3f2723575097ced42` (merge), `c0a06a2c1b823ea8b889623597b707ee65782c70`
(#4602), `dd7da6af5` (#4735).

### Target (e) — `pola-rs/polars#24771`: a parser rewrite justified by a single-machine benchmark

[`pola-rs/polars#24771`](https://github.com/pola-rs/polars/pull/24771) "perf: Duration/interval
string parsing optimisation (2-5x faster)", author `alexander-beedie`, a core contributor. Opened
2025-10-06, **merged 2025-10-08** on one `APPROVED` review by `ritchie46` submitted nine seconds
before the merge, with **zero review comments**. The only conversation comment is Codecov's
(patch coverage 94.79 %, five uncovered lines in `duration.rs`). No originating issue; the body
cites [`#24737`](https://github.com/pola-rs/polars/pull/24737) (merged 2025-10-03) as the work
during which the opportunity was noticed.

| | |
| --- | --- |
| head | `2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f` |
| base ref | `main` (pinned locally to the merge-base) |
| base SHA / merge-base | `b3241e0d50b5e9196fa0b070811e3d043157c5ba` (identical) |
| diff | 3 files, +156 / −130, two commits |
| originating issue | none (`issues=none`) |
| prior review state | 1 `APPROVED` review, 0 review comments, 1 bot comment |
| merged | `true`; retrospective, non-publishing |

Changed-file manifest:

```
M	crates/polars-time/src/windows/duration.rs                                  (+143 −110)
M	py-polars/src/polars/functions/lazy.py                                      (+5   −3)
M	py-polars/tests/unit/operations/namespaces/temporal/test_datetime.py        (+8   −17)
```

`Duration::_parse` is rewritten from a `char_indices` walk with a `String` unit buffer and a
`parse::<i64>()` per number into a single pass over `s.as_bytes()` that accumulates each integer
by hand and matches units as byte-string literals. The Python file change is an unrelated
docstring reorder in `row_index`. The test change rewrites error-message expectations.

**The claim, verbatim from the body:**

> Benchmarked* `Duration::parse` in isolation (with a small `criterion` `black_box` harness). Is
> always much faster, with the exact degree of speedup depending on the string under consideration
> (mostly just a function of length); short/common strings like `"-1d"` are parsed **5x** faster:
> [table: nine strings, 2.26x–5.24x] _(*testing done on an Apple Silicon M4 Max)_

No benchmark file is in the diff or the repository; the harness is described, not included; the
numbers are sub-30-nanosecond `criterion` timings on one named machine. A static reader can see
fewer passes and no UTF-8 decoding, and cannot settle whether that is 2x or 5x anywhere, or
anything on another microarchitecture.

#### Ground truth

**GT-e1 — the question channel fires on the benchmark claim.** The correct disposition of the
claim is a published `[Question]` under the rubric's static-unresolvability rule: no static
source available to the reviewer can settle a measured speedup, and the answer is
outcome-changing because the change's entire justification is that number — a 143-line rewrite
of a working parser, with its own new error-message surface, is warranted by a 2–5x gain and not
obviously by a marginal one. The question names what would settle it: the harness, its inputs,
and a run on a second architecture, or a `benches/` entry in the repository. Scored `found` when
such a question is published (any wording that asks for the measurement rather than asserting a
result); `raised` when the claim is in the ledger as `not-verifiable` without a question;
`not raised` when the run cites the number as established or does not mention it.

**T-e1 — the hand-rolled integer accumulation has no overflow check (adjudicated true; not
upstream-confirmed).** `n = n * 10 + (s[pos] - b'0') as i64` accumulates without bound. The
replaced code called `s[start..i].parse::<i64>()` and bailed with "expected leading integer" on
`Err`, so a duration string with more than nineteen digits previously produced an error and now
wraps in a release build (panics under debug assertions). No upstream commit has changed this as
of 2026-09-04: the later `duration.rs` commits in the 90-day window (`20a239d92` #24832,
`c6d29c8af` #24916, `fa0e9d0ae` #25058) and after it (`1e98e1d9b` #29047, `a97a1d88f` #29059)
touch other functions. A finding here is **true**; it is recorded separately from GT-e1 because
no upstream event confirms it and it is not what the target was selected for.

#### Not ground truth

- **The `lazy.py` docstring move** (`versionadded` above the `warning`) is an unrelated
  drive-by; an observation is in band, a finding is over.
- **The error-message wording changes** ("can only have a single '+' sign", "expected a valid
  unit") are intentional, tested, and not a public contract; a finding is false.
- **"Byte indexing breaks on non-ASCII input."** False: every `s[pos]` is on a `&[u8]` under a
  `pos < s.len()` guard; a non-ASCII byte is simply not a digit or letter and reaches an error
  branch. The `ch as char` in that message renders a UTF-8 lead byte as a Latin-1 character
  (cosmetic); `consider` at most.
- **"Upper-case interval units such as `3 DAYS` no longer match the lower-case byte literals."**
  False: `try_parse_interval` lower-cases before `_parse` at head (`duration.rs:172`), unchanged
  by the diff, and the new unit test `test_parse_interval` covers `"3 DAYS"`.
- **Sign handling.** `negative: leading_minus` reproduces the old `s.starts_with('-')`; the
  second-sign errors reproduce the old ones with reworded messages.

#### Calibration band

`Needs Information` (coverage complete, GT-e1 open) is the adjudicated status; `Changes
Requested` is in band only if T-e1 is published at P3 `must-fix`; `Approved` with GT-e1 published
as a question is in band (a question with a settled verdict is allowed by the contract when the
answer does not change the verdict, but the adjudicated reading is that it does). `Approved`
without a question is `under`. Any `must-fix` on a Not-ground-truth item is `over` and false.
T-e1 in band at P3, `consider` or `must-fix`; P1/P2 is `over`.

#### Mirror

Push only `2db2ee17d05f9482b59eb60d0c42f9d50bb4f64f` and
`b3241e0d50b5e9196fa0b070811e3d043157c5ba`. Negative checks per clone:
`4be4470d2b21e20754d49ec3c2ee6fe4a30d25cb` (merge) and `20a239d92` (#24832, the first later
commit to `duration.rs`).

### Target (f) — `spf13/cobra#1938`: one pull request reviewed twice, on a repository this program controls

[`spf13/cobra#1938`](https://github.com/spf13/cobra/pull/1938) "Add env variable to suppress
completion descriptions on create", author `scop`, an external contributor who also filed the
originating issue. Opened 2023-03-27 as a draft, rebased 2023-11-26, reviewed by maintainer
`marckhouzam` on 2023-12-09 (six inline comments, all change requests, submitted as `COMMENTED`),
answered with five commits on 2023-12-11, **approved and merged 2023-12-17**, released in cobra
`v1.8.1`. Chosen because both review-round heads are reachable in the current commit list
(`ahead_by 5, behind_by 0` between them; no force-push after the review), the round-1 comments
have a mixed outcome (four fixed, one partly declined with a reply, one never answered), and the
repository is small (2.1 MB).

| | |
| --- | --- |
| round-1 head (`R1`) | `97b70019e9a3e2618c895c0e93c3fc6d7101fc17` — every round-1 comment carries this `original_commit_id` |
| round-2 head (`R2`) | `1107319c750f917bc3bf1c74a7705fe6e93123be` — the merged head |
| base ref | `main` |
| base SHA / merge-base | `3d8ac432bdad89db04ab0890754b2444d7b4e1cf` (identical for both heads) |
| diff at `R1` | 4 files, +116 / −11, two commits |
| diff at `R2` | 4 files, +237 / −11, seven commits; `R1..R2` is 3 files, +132 / −11 |
| originating issue | [`#1937`](https://github.com/spf13/cobra/issues/1937) "RFE: env var for disabling descriptions"; the maintainer's and `Luap99`'s comments direct the shape: the Go code checks the variable itself, two variables `COBRA_…` and `<PROGRAM>_…`, "follow what active help does" |
| prior review state at `R1` | none from the posting identity (the fork PR is fresh); the human round-1 comments are **not** carried, see below |

Changed-file manifest at `R1`:

```
M	active_help.go                    (+3  −10)  active-help env var built via the new helper
M	completions.go                    (+34 −1)   configEnvVar, exported GetEnvConfig, `off` sentinel
M	completions_test.go               (+76 −0)   TestGetEnvConfig
M	site/content/completions/_index.md (+3 −0)   documents `off`
```

#### How this target runs

Per seed, one at a time because the pull request's state is shared:

1. **First review** at `R1`, published to the fork PR. Network is permitted for `gh` against
   `kamui/cobra-holdout` only; the clone's `origin` is the fork.
2. **Head move:** push `R2` to the seed branch (a fast-forward; `R1` stays an ancestor).
3. **Re-review** at `R2`: a second packet naming `R2`, with the run's own first review as the
   prior state it fetches. The run reads `re-review.md`, computes the delta (`ancestor: yes`,
   `merge-base-unchanged: yes`), classifies each of its prior items, replies on their threads,
   and publishes a second review naming `97b7001..1107319`.
4. **Stale-head probe:** push `R3`, an empty commit on top of `R2`, then dispatch one more
   re-review run with the `R2` packet. The correct outcome is **no write**: step 5's re-fetch
   finds the head moved and the run reports the stale review. Any write is a failure of the
   abort. This run is not scored on dimensions 1–4; it is metered.

#### Ground truth at `R1` (first review)

**GT-f1 — the new test unsets its environment variables before reading them (in-diff,
mechanical; the maintainer's comment 6, fixed by `c96f1a62`).**
`defer assertNoErr(t, os.Unsetenv(tc.cmdVar))` evaluates `os.Unsetenv` at the `defer` statement,
so both variables are cleared before `GetEnvConfig` runs; four of the five cases expect a
non-empty value and fail. `go test ./...` at `R1` is red on `TestGetEnvConfig`. Checkable by
reading the test.

**GT-f2 — `GetEnvConfig` is exported with a `suffix` parameter whose only valid values are
unexported constants (in-diff, API shape; comment 2, fixed by `7aa559d6`).** Programs cannot
call it meaningfully, so the diff widens the public API with a function no caller can use.
Checkable from the diff.

**GT-f3 — the `off` sentinel is inconsistent with the sibling `COBRA_ACTIVE_HELP=0` convention
in the same file family (in-diff, design; comment 1, changed by `138b0ab9` to
`strconv.ParseBool`).** The issue's own direction was "follow what active help does". In band as
`consider` or as a question, not as `must-fix`.

Recall on (f) is scored over GT-f1 and GT-f2; GT-f3 is recorded.

#### Ground truth at `R2` (re-review)

For each of the run's own prior items, the adjudicated classification:

| Prior item | Classification | Evidence in `R1..R2` |
| --- | --- | --- |
| GT-f1 | `fixed` | `c96f1a62`: `defer func() { assertNoErr(t, os.Unsetenv(...)) }()` |
| GT-f2 | `fixed` | `7aa559d6`: `getEnvConfig` unexported |
| GT-f3 | `fixed` | `138b0ab9`: `strconv.ParseBool`, sentinel removed, docs say "falsey value" |
| a precedence item, if raised (the `<PROGRAM>_` variable overrides `COBRA_` for descriptions while `COBRA_ACTIVE_HELP=0` overrides the program variable for active help; the maintainer wrote "let's do that in another PR") | `still-open` | nothing in `R1..R2` touches `GetActiveHelpConfig` |
| anything else | `still-open` if the code is unchanged, `obsolete` if the lines are gone |

The delta introduces one new fact a re-review may raise: `strconv.ParseBool` errors are ignored,
so `off` — the value `R1`'s docs advertised — now does nothing, silently. In band as
`consider` (the review record shows it was chosen deliberately); `must-fix` is `over`.

#### Not ground truth

- **"The refactor changes the active-help variable names."** False: `configEnvVar(name,
  "ACTIVE_HELP")` yields exactly the old `<PROGRAM>_ACTIVE_HELP`, and
  `configEnvVarGlobalPrefix + "_" + suffix` is `COBRA_ACTIVE_HELP`; the base's regexp and
  upper-casing are preserved. A finding is false.
- **The 200-line size bot comment.** Not evidence of anything.

#### Calibration band

First review: `Changes Requested`; GT-f1 `must-fix` at P2 or P3 (a red test inside the diff);
GT-f2 P3, either action; GT-f3 `consider` or a question. Re-review: `Approved (advisory)` when
every prior item classifies as above and no new `must-fix` is verified; a run that re-posts a
fixed item as open, or that publishes a `must-fix` on the ParseBool behavior, is `over`. A
declined-then-still-valid item does not exist on this target, so `disputed` is `over`.

#### Mirror

The fork repository *is* the truncated mirror: `main` at `3d8ac432bdad89db04ab0890754b2444d7b4e1cf`
and the seed branches at `R1`, then `R2`, then `R3`. Negative checks per clone and on the fork
itself: `e63925d3216142ba2c8d7641d729c6c15f4433e7` (merge).

## Conditions

Everything test 4 held constant holds here, plus the additions #60 specifies. The list is the
dispatch checklist; a cell that violates any line is discarded and re-run.

### Model

`claude-sonnet-5`, passed explicitly as `model: "sonnet"` on **every** `Agent` call — each run's
orchestrator and every sub-agent it spawns. The harness default is not Sonnet and has changed
mid-program before. Nothing is inherited. Verified after the fact, before any scoring, by reading
`message.model` from every assistant line of every transcript belonging to the grid (the
[Model verification](#model-verification) rule); the same lines supply the `effort` field the
lower-effort arm checks.

### Arms

| Row label | Skill | Snapshot | What differs |
| --- | --- | --- | --- |
| `v5b` | `legacy reviewer`, `workflow=v5b-1` | `main` at the commit recorded in [comparison-data.md](comparison-data.md#comparison-boundaries) | the advancing line |
| `v5b-noverify` | `legacy reviewer` with verification disabled | the `v5b` snapshot with `references/verifier.md` deleted | the v3 ablation; see below |
| `v5b-effort-medium` | `legacy reviewer`, primary at effort `medium` | the `v5b` snapshot | #68's arm, targets (b) and (c) only; see [Lower-effort primary arm](#lower-effort-primary-arm) |

Three seeds per arm per target. A seed is an independent dispatch of the same packet into a fresh
clone with a fresh orchestrator context; nothing is shared between seeds except the packet and the
mirror. Seeds are numbered in dispatch order and a discarded seed's number is retired, not reused,
so `comparison-data.md`'s Run continuity table can name it.

**How the ablation is disabled.** The `v5b-noverify` snapshot is the `v5b` snapshot with
`references/verifier.md` removed, and its dispatch carries this sentence: "`references/verifier.md`
is unavailable in this snapshot. Do not imitate independent verification in the primary context.
Apply `SKILL.md`'s handling rule for a verifier that fails or cannot inspect required evidence:
mandatory verification is incomplete, every candidate that required it stays unpublished, and
coverage is reported incomplete." That is the fail-closed behavior the skill already specifies when
isolation is unavailable; the ablation measures what the primary alone finds and how it reports the
gap, not a primary that pretends to verify. Every run in this arm therefore ends `Incomplete` or
`Changes Requested` with unverified candidates withheld; the run document lists the withheld
candidates so dimension 1 can be scored on what the primary found, and the payload is scored as
published. A `v5b-noverify` run whose payload contains a finding whose trailer says
`independent-confirmed`, or whose report describes a verifier dispatch, is discarded.

### Mirror and clones

One bare mirror per target, built as test 4 built it: fetch the repository into a staging mirror
outside the runs' tree, create a fresh bare repository, push **only** the pinned head and
merge-base SHAs into it, and record the negative `git cat-file -e` checks below per clone: the
merge commit, every post-merge fix or withdrawal the target's ground truth cites, and, for target
(a), the revert and the re-land. Inline the literal SHAs in every refspec; a zsh `:r` modifier in a
variable ate one once and the cleanup deleted a working tree (memory:
`prototype-run-orchestration-hazards`). Each run gets its own clone with `origin` repointed to the
mirror's filesystem path, `main` (or the target's base branch name) force-set to the merge-base, and
the head checked out on `review-head`. Every clone's newest reachable commit is the pinned head.

Network access is forbidden in every run. Execution is forbidden in every run except the arm's own
helper scripts, as in test 4; target (b)'s test suite is executed by the **adjudicator** for the
ground truth, never by a run. The run document records the sandbox path and any read outside it.

### Phase-1 packets

Phase 1 is done once per target by the orchestrator and handed identically to every arm and seed as
one packet file. Each packet carries:

- the run identity: repository, pull request, `head`, `base` ref and SHA, `merge-base`, `state`,
  and **`merged: true`** (every target here is merged; the runs are retrospective and
  non-publishing except (f)'s fork, whose packet says `merged: false` because the fork PR is open);
- `baseRepository.url` (the fork's URL for (f));
- the verified changed-file manifest with per-file counts;
- the pull-request body verbatim and every commit message verbatim;
- the originating issue body verbatim and its comments verbatim, or
  **`comments_available: false`** and no comments when the packet cannot carry them verbatim;
  never an empty list standing in for comments that exist;
- the complete prior review record verbatim: every review, review comment, thread, and
  conversation comment up to the pinned head, including bot and CI comments;
- the guidance-file inventory at base (root `AGENTS.md` / `CLAUDE.md` / `CONTEXT.md` and
  path-scoped ones, with blob ids);
- the run conditions above, the program's standard note that author responses to earlier review
  rounds are already applied in the reviewed head, and the persistence instruction below.

The packet is identical across arms and seeds for a target, byte for byte; its SHA-256 is recorded
in `comparison-data.md`. Target (f)'s second packet (the re-review) is a second file.

### Persistence and budget

Every dispatch says: write the expensive phase (the manifest and requirement ledger, then the
complete candidate ledger) to the run's report file **before** dispatching any verifier batch, and
update the file as the run goes. No session relays: a run is dispatched with enough budget to
finish, and an interrupted run is discarded and its cell re-run clean. Dispatch at most two cells
at a time; when any agent returns a session-limit notice, record the reset time, dispatch nothing
further, and resume after it (#96, which lands its wording in "Dispatch hygiene" above). **Deviation
recorded:** at the maintainer's request after a session reset, concurrency was raised to four cells
from 16:38 on 2026-09-04, mixed across targets so one limit event could not take out one target's
seeds together; no limit event occurred during the grid. Every
discarded attempt is priced and recorded under Run continuity.

**Pointer (2026-09-05, #96).** The attempt ledger, the pre-dispatch record and the reset-aware
scheduling rule live in
[the one-shot method §3](../code-review-one-shot-method.md#3-preserve-every-attempt-and-its-output),
not in "Dispatch hygiene" above as the previous paragraph anticipated. The two-cell rule, the
recorded four-cell deviation and the Run continuity rows in `comparison-data.md` remain this
grid's history.

## Model verification

Before any run is scored, list every transcript belonging to the grid — each run's orchestrator
transcript and one per sub-agent it spawned, under
`~/.claude/projects/<project>/<session>/subagents/agent-*.jsonl` — and read `message.model` and
the top-level `effort` from every assistant line, not only the first turns; a resumed agent can
change either. Record the per-run result in `comparison-data.md` under Model verification and
Effort verification. A run with any line not reporting `claude-sonnet-5` (or, for the tier-split
cells, the assigned model on the assigned role only) is discarded and its cell re-run.

## Scoring

Four dimensions per run, kept separate; none is folded into a composite.

1. **Ground-truth recall.** Each target's GT items below, scored `found` (published as a finding
   naming the same defect), `raised` (in the ledger or a question or observation but not a
   finding), `acquitted` (in the ledger with a disposition that rejects it), or `not raised`.
   Only `found` counts as recall; the other three are recorded because they separate reviewer
   misses from verification misses.
2. **False findings and false acquittals.** A false finding is a published finding whose claim the
   pinned code contradicts or whose consequence the target's history shows absent, judged against
   the "not ground truth" items below and the pinned code. A false acquittal is a ledger row whose
   decisive premise the pinned code contradicts; every acquittal on a GT surface is checked, and
   on targets (a) and (b) every acquittal whose `kind` is `bug`, `concurrency`, `invariant`, or
   `security` is checked. Both are counted per run.
3. **Action calibration.** The run's status and each published finding's priority and action
   against the target's calibration band, written below before the runs. A run is `in band`,
   `over` (blocks or escalates beyond the band), or `under` (approves or downgrades below it).
4. **Fix sufficiency** (targets (a) and (b) only). Whether the published `Change` for a GT item
   restores the invariant the target's ground truth names, or only patches the observed
   branch. Scored `invariant`, `branch`, or `none`.

Plus cost, metered as [above](#metering-per-run) with primaries metered.

**Calibration band.** Each target states the adjudicated status a correct review reaches, the
priority and action range for each GT item, and the items that must not be blocking. The band is
what a careful reviewer with the pinned inputs and no execution could reach; upstream's later
history sets the ground truth but the band is set at what was knowable.

## Success criteria

`evaluation.md` states pass or fail for each line, in this order, with the run ids that decide it.

**v5b**

**Lower-effort arm** (#68): report the adoption rule's result and the eight cost figures as
[above](#lower-effort-primary-arm) specifies.

**Tier split:** the target used, chosen from (b) or (e) after the Sonnet grid is scored, and
the six runs' dimensions and cost beside the Sonnet cells on that target; #88 reads them from
here.

## Sign-off

The six targets above were proposed in pull request #114 and **signed off by the maintainer on
2026-09-04**. The alternates considered, for each shape, are listed in that pull request. No cell
is dispatched for a target whose ground truth and calibration band are not in this file at the
commit the run records.

## Files

- `README.md` — this file: method, targets with ground truth and calibration bands, conditions,
  model verification, scoring, success criteria
- `<target>/<arm>-seed<n>-payload.md` and `<target>/<arm>-seed<n>-run.md` — one pair per run;
  target (f) adds `-rereview-payload.md`, `-rereview-run.md`, and `-staleprobe-run.md`
- `<target>/packet.md` — the phase-1 packet given to every run on that target ((f): `packet-r1.md`,
  `packet-r2.md`); (c) adds `upstream/` as described in its section
- `comparison-data.md` — side-by-side metadata with the production-shaped cost column
- `evaluation.md` — pass/fail against each #60 success criterion, plus the lower-effort arm's six
  runs and whether the #68 adoption rule was met; written by #60 after the grid
- [`../tools/build_packet.py`](https://github.com/kamui/code-review-bench/blob/main/bench/tools/build_packet.py) — the phase-1 packet builder that renders
  a `<target>/packet.md` from one forge query and the staging mirror. It is the #124 builder quoted in
  [`../one-shot-effort-2026-09-06/tooling.md`](../one-shot-effort-2026-09-06/tooling.md) shipped as a
  tool, preserving that builder's packet layout at the merge-time cutoff. Its stricter metadata
  validation now requires established historical text and complete source collections before
  rendering; old captures missing provenance must be replaced with established inputs. The format
  is the one used by `../one-shot-effort-2026-09-06/g-bytes-698/packet.md` and its `h-etcd-18749` sibling.
  It does **not** regenerate this bundle's packets, which came from the earlier cutoff-free builder:
  that one titles a packet "holdout target (x)" and gives §6 no cutoff, as
  `../one-shot-effort-2026-09-06/a-hyper-3952/packet.md` shows.
  `python3 ../../../bench/tools/test_build_packet.py` checks the shipped tool
- [`../tools/cost_split.py`](../tools/cost_split.py) and
  [`../tools/transcript_usage.py`](https://github.com/kamui/code-review-bench/blob/main/bench/tools/transcript_usage.py) — the metering scripts;
  `--self-test` checks each
- the two grid-only agent definitions (`v5b-primary-effort-medium`, `v5b-verifier-effort-high`) lived under
  `.claude/agents/` during the grid and were removed afterwards; their frontmatter is quoted above
