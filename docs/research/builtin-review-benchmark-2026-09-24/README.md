# Built-in reviewer benchmark — `review-code` against Claude Code's `/code-review` and Codex `review`

**Status: draft preregistration, not frozen.** This is the narrative of the first scored run of the
[reviewer benchmark suite](../../../bench/README.md). The run will live at
`bench/runs/<freeze date>-builtin-baseline/`; its `manifest.json` is written and committed at freeze,
and its commit is named in [`ledger.md`](ledger.md). No scored cell has been dispatched. Freezing
happens when §10's open items are closed.

The mechanism this file used to describe has moved into `bench/`: the arms are data in
[`bench/arms/`](../../../bench/arms/), the targets and their sealed registers in
[`bench/targets/`](../../../bench/targets/), the scoring definitions in
[`bench/rubric/scoring.v1.md`](../../../bench/rubric/scoring.v1.md), and the tools in
[`bench/tools/`](../../../bench/tools/). The suite's design and its comparison contract are in
[`bench-suite-design-2026-09-24.md`](../bench-suite-design-2026-09-24.md). What stays here is what
a run's narrative owns: the question, the decisions, the grid and budget, the scoring
clarifications this run adds, what the shakedown established, what is open, and the review
history.

This run follows [the one-shot method](../code-review-one-shot-method.md) for freezing, inputs,
attempt accounting, adjudication and scoring, and departs from it only where §3, §4 and §8 say so.
It is a **benchmark**, not an adoption screen: it preregisters questions, not thresholds, and
nothing it measures authorizes changing any skill.

## 1. Question and decisions

**Question.** On the same sealed targets, how many adjudicated material defects does the current
`review-code` recover per completed review compared with Claude Code's built-in `/code-review`
and with Codex's `review` subcommand, at what false-finding rate, what false-clean rate, and what
cost; and which registered defects does each reviewer miss?

Decisions taken by the maintainer on 2026-09-24, before any dispatch:

| Decision | Value |
| --- | --- |
| Arms | four (§2) |
| Spend cap | **$250** for the whole experiment: pilot, replacements, setup, adjudication, grading |
| Targets | the six #137 targets (i)–(n) reused as a regression set, plus four fresh targets (§5) |
| `review-code` model | `claude-sonnet-5`, effort `high` on the primary and every verifier, as in every prior grid |

## 2. Arms

| Arm | Arm file | What runs | Row label |
| --- | --- | --- | --- |
| A | [`review-code-sonnet-high`](../../../bench/arms/review-code-sonnet-high.json) | `skills/review-code` at the tree resolved at freeze, invoked as a caller would: `mode: one-shot`, `return_format: artifacts`, render-only; Sonnet 5 at `high`, verifiers the same | `review-code` |
| B | [`claude-builtin-sonnet-high`](../../../bench/arms/claude-builtin-sonnet-high.json) | built-in `/code-review`, `claude-sonnet-5`, session `--effort high`; expected variant `3+5 angles × 6 candidates → 1-vote verify (recall-biased)` | `claude-builtin-sonnet` |
| C | [`claude-builtin-opus-high`](../../../bench/arms/claude-builtin-opus-high.json) | built-in `/code-review`, `claude-opus-5-5` (the harness default), session `--effort high`; expected variant `8 inline angles → dedup (no verify)` | `claude-builtin-opus` |
| D | [`codex-default`](../../../bench/arms/codex-default.json) | `codex review` as shipped, default model and reasoning effort (`gpt-6-astra`, `reasoning effort: none` on 2026-09-24) | `codex-review-default` |

A/B is the matched pair that separates skill from model. **B/C is not a model ablation**: the
built-in chooses its prompt per model, and under Opus it runs an inline, no-verifier variant, so
B/C compares two shipped configurations of the same product. D is a product comparison: what a
user gets by typing the command. The built-in's **as-shipped default** is not run: with no effort
flag in a fresh home it selects the `low` variant (`minimal prompt → single careful diff pass →
≤15 findings`), which would differ from B in both model and prompt; the fact is registered in
[`bench/harness/claude-code.json`](../../../bench/harness/claude-code.json) and the `low` variant is
left to a later run. `/code-review ultra` and the Codex GitHub app are excluded by construction.
The publish step of `review-code-publish` is not under test; nothing is posted.

**Arm A runs without the research-report dispatch of prior grids.** The #137 template made the
reviewer write a staged research report during the review, which the independent review (§11)
identified as an intervention the other arms do not receive. Here A is invoked the way
`review-code-publish` invokes it, and the run record is derived afterwards from the skill's own
artifacts and the transcripts. No production-shaped subtraction is applied to any arm; every arm's
billed cost is reported as-is.

**Pins are observations, recorded per attempt.** The manifest records each arm file's hash, the
resolved `skills/review-code` tree, and the CLI versions and prompt hashes a pre-dispatch probe
observed. Every `attempt.json` records the CLI version, the models and effort on every request,
and the prompt hash, matched against the harness registries (Claude Code `2.1.281` and Codex CLI
`0.156.1` at the shakedown). An attempt whose prompt hash is not among its arm's expected variants
is harness-invalid; a pin that changes mid-grid invalidates the affected cells.

## 3. Isolation

The first shakedown probes under the maintainer's normal environment were both contaminated:

- `claude -p "/code-review …"` resolved the **user-level `~/.claude/skills/code-review`** (the
  Matt Pocock two-axis Standards/Spec skill), not the built-in.
- `codex review` read **`~/.agents/skills/review-code/SKILL.md`** (a symlink into the
  maintainer's iCloud skills, which hold this repository's own skill) and applied
  `~/.codex/AGENTS.md`.

The controls are the suite's (design §5), applied by
[`dispatch.sh`](../../../bench/tools/dispatch.sh) and checked by
[`attempt_audit.py`](../../../bench/tools/attempt_audit.py) and
[`file_attempt.py`](../../../bench/tools/file_attempt.py):

1. **Export layout and a fresh home per attempt.** The attempt directory holds only the clone,
   the packet and a home with credentials alone; the reviewer's `TMPDIR` is inside it. Nothing
   from `bench/` is mounted or copied in. The toy run showed why: a clone beside other attempts'
   clones let Codex's `find ..` walk them (att-003).
2. **`--safe-mode`** for the Claude built-in, so bundled plugin skills stay out; arm A keeps its
   own skill as the only user skill instead.
3. **Network off.** No web tools for Claude; Codex's sandbox with `network_access: false`; any
   network command in the audit is a violation.
4. **Read audit.** Every path in every command and file read is resolved against its working
   directory, `..` and `~` included; anything outside the attempt directory and its clone is a
   violation. Ancestor probes for `AGENTS.md`/`CLAUDE.md` are recorded and violate only if the file
   exists. A violation, a tree-identity change, or an unexpected model, effort or prompt makes the
   attempt **harness-invalid**: it stays in the denominators and cost totals with zero admissible
   recovery and is replaced inside the cap.
5. **Truth kept unreadable, as far as this machine allows.** The four fresh registers and every
   adjudication note stay in an encrypted archive until scoring. The reused registers are public
   already, so a same-user process *could* read them; the audit is the control. A separate Unix
   user would make that impossible rather than detectable and is recorded as not done.

## 4. Adapters

Inputs are identical across arms: an offline clone at the pinned head with `main` at the merge-base
and `review-head` checked out (the built-in diffs `main...HEAD` whatever its argument says), the
dependency cache restored from its hashed archive, the factual packet, and the target's
execution allowance. Each arm file's `adapter` block states how the range and the packet reach that
arm: A through its caller inputs, B and C in the prompt after the range argument, D on stdin
because `codex review --base` refuses a prompt. Every executed diff command is resolved in the
clone and must name the pinned merge-base and head.

Native output is kept verbatim and normalized mechanically by
[`normalize_review.py`](../../../bench/tools/normalize_review.py): review level (`native_verdict`)
and per item `file`, `line_start`, `line_end`, `claim`, `consequence`, `proposed_fix`,
`native_priority`, `native_action` (A only) and `native_confidence`. **No `blocking` flag and no
keyword `kind` are derived**; the first review of this plan showed both invent information. An
output the normalizer does not recognize is `unresolved`, never an empty review.

**Blinding.** Scorers receive uniformly rendered items (location, claim, consequence, fix) with
native formatting, priority labels, verdict words and arm-identifying structure stripped, under
random names. Residual cues (prose style, item count) are disclosed; blinding is a mitigation, not
a guarantee.

## 5. Targets

Six targets are reused from the [#137 grid](../one-shot-qualification-2026-09-07/README.md) and are
now suite targets, each with its pins, factual packet, register, provisioning and exposure history.
**Their registers are the versioned ones after #137's adjudication**: target (n) gained GT-n1 and
is **buggy**, so the reused set is five buggy and one clean. Four fresh targets are hunted for the
shapes the regression set lacks. Shape is the **sampling rationale**, not a causal claim: prior
grids varied shape, language and repository together, so results are reported per target and per
shape as observations.

| Slot | Suite target | Shape | Truth |
| --- | --- | --- | --- |
| (i) | [`i-requests-6667`](../../../bench/targets/i-requests-6667/) | concurrency, shared mutable state | buggy (GT-i1, GT-i2) |
| (j) | [`j-trpc-5017`](../../../bench/targets/j-trpc-5017/) | cross-file type obligation outside the diff | buggy (GT-j1) |
| (k) | [`k-graphql-js-1582`](../../../bench/targets/k-graphql-js-1582/) | changed-test correctness | buggy (GT-k1) |
| (l) | [`l-bokeh-9232`](../../../bench/targets/l-bokeh-9232/) | ordinary behavioural change | buggy (GT-l1) |
| (m) | [`m-grpc-go-7390`](../../../bench/targets/m-grpc-go-7390/) | clean, high risk (concurrency) | clean |
| (n) | [`n-ripgrep-2957`](../../../bench/targets/n-ripgrep-2957/) | promised change that does not work as pasted | buggy (GT-n1, register v2) |
| (o) | to hunt | security: authorization or injection, web backend | buggy, fresh |
| (p) | to hunt | released-compatibility break, public API or SDK | buggy, fresh |
| (q) | to hunt | refactor claiming no behaviour change, large mechanical diff | **clean**, fresh |
| (r) | to hunt | frontend component logic, React or comparable; settleable statically or by a focused test, never visually | buggy, fresh |

Eight buggy, two clean. False findings are counted on every target, not only clean ones, so the
two clean targets and the refactor trap are not the only precision evidence. Fresh-target rules:
merged public pull requests with post-merge evidence (follow-up fix, revert, or issue); a register
sealed by an adjudicator who has seen no reviewer output; a truncated mirror and a merge-time packet
cutoff.

**Training-data exposure.** Every target is public and may be in any model's training data, and
the six reused targets have additionally shaped this repository's skill development; each
`target.json` lists that history. Controls: the merge date, the fix-publication date and each
model's published cutoff are recorded per target; regression and fresh results are reported
**separately**; post-cutoff cases are preferred for the fresh slots; and chronology is never claimed
to prove non-exposure.

## 6. Grid, order, caps

| | |
| --- | --- |
| Planned cells | 4 arms × 10 targets × 2 replicates = **80** |
| Order | **replicate 1 of every target and arm first** (40 cells), arm order rotated per target and sealed before dispatch; then replicate 2 in balanced four-arm blocks per target in the sealed order |
| Concurrency | at most two cells in flight |
| Replacements | at most **4** across the grid, 84 attempts total; a harness-invalid cell is replaced, a miss never is |
| Pilot | targets (i) and (n), arms B and D, one replicate each, before the sealed order runs; valid rows count |

**Budget.** Rates are the dated entries in [`bench/rates.json`](../../../bench/rates.json): Sonnet 5
`$2/$10`; Opus 5.5 `$4/$20` with cache reads at `$0.20`; GPT-6 Astra `$10/$50`, cached input `$1`,
cache write `$12.50`. Expected per-cell spend, with A from prior grids and the built-ins scaled up
from the shakedown's five-line diff to a grid-sized one:

| Arm | Expected / cell | Conservative / cell | 20 cells expected | 20 cells conservative |
| --- | --- | --- | --- | --- |
| A | $4.00 | $5.00 | $80 | $100 |
| B | $1.50 | $2.50 | $30 | $50 |
| C | $3.00 | $5.00 | $60 | $100 |
| D | $2.00 | $3.00 | $40 | $60 |
| Setup, packets, four adjudications, grading | | | $40 | $50 |
| Replacements (4 × arm mean) | | | $11 | $16 |
| **Total** | | | **$261** | **$376** |

The expected total already exceeds the cap, so the grid cannot promise 80 cells. **Stopping
rule, preregistered:** a closeout reserve of `$25` is protected from the start. Before each block
the conservative bound of that block must fit in `cap − spent − reserve`. Replicate 1 across all
40 cells runs first (`≈ $105` expected). Replicate-2 blocks then run in the sealed target order
until the next block's conservative bound no longer fits; the unrun blocks are reported as
unattempted, never as incomplete evidence about the arms that happened to be scheduled last, and
the per-shape tables use completed-only and attempt-level views as the method requires.

**Codex spend is not dollars.** The maintainer's Codex runs on a ChatGPT plan
(`plan_type: prolite`), so D's cost column is a list-price equivalent and its real constraint is
the plan's weekly quota, recorded in the ledger before each D dispatch. The `$250` cap counts the
list-price equivalent so the arms stay comparable.

## 7. Metering and timing

`file_attempt.py` meters every attempt from its transcripts at the `rates.json` entry for the
observed model: `transcript_usage.py` for Claude (the built-in's root transcript bills nothing, so
only its subagent transcripts are metered) and `codex_usage.py` for Codex (the review runs in a
child thread; ordinary input is `input − cached − cache_write`). Per-request records go beside each
attempt record; transcripts are archived outside the repository with their hashes, because the
built-in's proprietary prompt is in them. Timing has four events: `dispatched_at`,
`payload_validated_at` when normalization succeeds inside the wrapper, `completed_at` only for a
valid completed attempt, and `stopped_at` otherwise.

## 8. Adjudication and scoring

Rubric v1 applies. Clarifications for arms that lack `review-code`'s vocabulary:

- **Review-level outcomes are three separate columns.** `approved_on_buggy` (the #137 false
  clean), `zero_recovery`, and `false_clean` (both). Per arm, an approving verdict is A
  `Approved`; B/C an empty findings array; D `patch is correct` or a stdout summary with no
  finding.
- **Action errors** are scorable for A only. For D, priority errors use its `P<n>`; for B/C,
  rank errors (a material defect ranked below a non-material item).
- **Materiality is adjudicated, not keyword-classified.** Every normalized item is scored the
  same way in every arm: recovery, false finding, non-material, or unresolved. Non-material items
  go to a **noise column** per review. A "waste" item that establishes a material performance
  failure is a recovery; a guidance-rule item that establishes an explicit requirement failure is a
  recovery.
- **Per-shape breakdown** is the primary table: recall, false findings and the three review-level
  columns per target per arm. Macro figures are secondary. Regression (i)–(n) and fresh (o)–(r) are
  tabulated apart.
- Unexpected plausible findings go to blind adjudication and the register is versioned before
  rescoring, with every earlier attempt re-adjudicated for the new defect only; a clean target that
  turns buggy is a target-mix deviation.

Preregistered questions, answered per arm against A: material recall per completed review; raw
and unique false findings per review; the three review-level rates on buggy targets; matched
median cost ratio; elapsed-to-payload ratio; and the set of registered defects no arm recovered.

## 9. What the shakedown established (Phase 0, 2026-09-24)

The adapter shakedown is filed as the suite run
[`2026-09-24-toy`](../../../bench/runs/2026-09-24-toy/README.md): seven attempts of the four arms on
a two-commit fixture whose `average()` divides by `len(prices)` while its docstring says empty carts
are common. Every attempt recovered the planted defect. Before those wrapper runs, six probes
established the isolation facts in §3; they are recorded in [`ledger.md`](ledger.md) and here:

| Probe | Valid | Model | Turns | Tool calls | Input | Cache write | Cache read | Output | Wall | Cost ($) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude, normal home: user skill shadowed the built-in | **invalid** | claude-sonnet-5 | 2 | 1 | 4 | 17,831 | 36,873 | 749 | 0:00:07 | 0.09 |
| B: built-in, `--safe-mode`, `--model sonnet`, `high` | valid | claude-sonnet-5 | 2 | 1 | 4 | 14,855 | 13,964 | 261 | 0:00:03 | 0.04 |
| C: built-in, fresh home, `--safe-mode`, no `--model`, no effort | valid, ran the **`low`** variant | claude-opus-5-5 | 4 | 3 | 8 | 14,143 | 38,756 | 562 | 0:00:05 | 0.10 |
| codex, normal home: read the maintainer's `review-code` skill | **invalid** | gpt-6-astra | 4 | — | 13,717 | 0 | 40,704 | 633 | — | 0.20 list |
| D: codex, clean home under `/tmp`, `--base base` | valid; no prompt possible | gpt-6-astra | 3 | 2 | 8,046 | 0 | 13,824 | 379 | 0:00:12 | 0.11 list |
| D: codex, clean home outside `/tmp`, prompt on stdin naming the range, `workspace-write` | valid | gpt-6-astra | 3 | 2 | 11,660 | 0 | 10,496 | 361 | 0:00:12 | 0.15 list |

Observations carried into §2–§4:

- The `high` built-in did not fan out its eight angles or run a verifier on a five-line diff (two
  requests, one `git diff`, findings as a fenced JSON array). Whether it fans out on grid-sized
  diffs is recorded per attempt from the subagent count. Its Phase 0 ran `git diff main...HEAD`
  despite the `base..review-head` argument; the suite names every base branch `main`.
- The **session `--effort` flag, not the argument, selects the built-in's variant**: Opus with
  `high` only as the argument ran at `medium` with the `low` variant (toy att-002), and with the
  flag it matched the `8 inline angles → dedup (no verify)` variant (att-004). Sonnet's default
  effort is already `high`.
- `codex review --base <branch>` exits 2 with `--base <BRANCH> cannot be used with '[PROMPT]'`
  when a prompt is given. The stdin-prompt transport ran the named range exactly, kept the rubric,
  and honoured `workspace-write`. Under the clean home Codex still walked up the tree looking for
  `AGENTS.md`; the clone's ancestors must hold none, and with a sibling layout that walk reads other
  attempts' clones (att-003), hence the export layout.
- The clean-home Codex probes confirmed the crash **statically** (diff and file reads only); the
  first, contaminated run was the one that executed `average([])`. Focused-test execution under
  the final D adapter is still to be demonstrated (§10).
- Priority varied between two otherwise identical D attempts (`P2`, then `P1`): a reminder that
  replicate variance is real and priority is not a stable signal for scoring.

## 10. Open before freeze

1. Re-check the Opus 5.5 and Sonnet 5 rates against the live pricing page (the recorded entries
   come from the `claude-api` skill's table cached 2026-06-24, which gives Opus 5.5 cache reads at
   `$0.20`); record the ChatGPT plan's quota.
2. Demonstrate focused-test execution under D's final adapter and under B on a suite target whose
   review needs a test run.
3. Hunt, adjudicate and seal (o)–(r); encrypt their registers; the adjudicator sees no reviewer
   output.
4. Write the run manifest: arms resolved, the pre-dispatch probe's CLI versions and prompt hashes,
   the cohort with register versions and packet and diff hashes, the sealed order, the caps above,
   the rates, and the execution policy.
5. Open the ledger's attempt table before any further chargeable step.

Done since the first draft: targets (i)–(n) migrated with factual packets, rebuilt mirrors and
verified diff identities; dependency caches archived with hashes and smoke checks measured on the
suite machine; the shakedown filed as a run with attempt records and computed results; CLI test
siblings for `attempt_audit.py` and `normalize_review.py`; `run_cell.py` (the caps and the
method's dispatch record checked before every dispatch, then `dispatch.sh` and `file_attempt.py`),
`score.py` and `compare.py`.

## 11. Independent review of the first draft (2026-09-24)

A Codex reviewer (`gpt-6-astra`, reasoning `high`, read-only) reviewed the first draft of this
file and the meter. Its report is kept at [`review-1.md`](review-1.md); the review of the suite
design that followed is [`review-2.md`](review-2.md), dispositioned in the design's §9. Disposition
of each item of the first review:

| # | Finding | Disposition |
| --- | --- | --- |
| M1 | `codex review --base` refuses a prompt, so the specified packet transport was impossible | **accepted**: stdin-prompt transport, verified in §9 |
| M2 | target (n) is buggy under #137's versioned register | **accepted**: §5 |
| M3 | false clean measured on the wrong denominator; no review-level disposition in the schema | **accepted**: §8, `native_verdict` in §4 |
| M4 | Codex priority cannot be mapped to a blocking flag | **accepted**: no `blocking` field |
| M5 | keyword cleanup classification suppresses material items | **accepted**: adjudicated materiality, §8 |
| M6 | isolation did not cover guidance files, truth files, network | **accepted** with a stated limit: fresh home, network off, read audit, encrypted truth; no separate Unix user |
| M7 | arm A's research-report dispatch is an intervention the other arms lack | **accepted**: A runs as a caller invokes it; no production-shaped subtraction |
| M8 | meter double-charged cache-write tokens | **accepted and fixed**: ordinary input is `input − cached − cache_write`, partition validated |
| M9 | malformed rollout lines were skipped silently | **accepted and fixed**: exit 2 with `file:line` |
| M10 | budget conclusion contradicted its arithmetic | **accepted**: §6 table and stopping rule |
| S1 | hashing native payloads does not blind origin | **accepted**: uniform rendering, §4 |
| S2 | merge dates do not control training exposure | **accepted**: §5 controls and separate reporting |
| S3 | meter lacked CLI-level tests and classified diagnostics | **accepted and fixed**: `test_codex_usage.py` |
| S4 | negative prices and oversized report estimates | **accepted and fixed** |
| S5 | the clean-home Codex probe did not execute Python | **accepted**: §9 corrected |
| D1 | "shape not language" stated as causation | **accepted**: shape is a sampling rationale |
| D2 | dropping only C's fresh replicate 2 was a poor fallback | **accepted**: replicate 1 first, then balanced blocks |
| D3 | omitting the effort argument does not select a factory default | **accepted in substance**: the fresh home removes typed history; the observed default was `low`, so C now pins `high` and the default is recorded, not run |
