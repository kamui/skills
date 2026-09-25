# Built-in reviewer benchmark — `review-code` against Claude Code's `/code-review` and Codex `review`

**Status: frozen 2026-09-24; grid filed 2026-09-25, all 80 cells valid in 83 attempts; scored 2026-09-25 (§12).** This is the narrative of the first scored
run of the [reviewer benchmark suite](../../../bench/README.md). The run lives at
[`bench/runs/2026-09-24-builtin-baseline/`](../../../bench/runs/2026-09-24-builtin-baseline/README.md);
its `manifest.json` carries `frozen_at` and names its freeze commit, and every chargeable step is in
[`ledger.md`](ledger.md). §10 records how the open items were closed, and §12 gives the results.

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
`0.156.1` at the shakedown; the run pins Claude Code `2.1.282` and Codex CLI `0.156.1`, observed
by its pre-dispatch probes). An attempt whose prompt hash is not among its arm's expected variants
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
| (o) | [`o-astro-16079`](../../../bench/targets/o-astro-16079/) | security: authorization or injection, web backend | buggy, fresh, register sealed |
| (p) | [`p-hono-5067`](../../../bench/targets/p-hono-5067/) | released-compatibility break, public API or SDK | buggy, fresh, register sealed |
| (q) | [`q-soba-195`](../../../bench/targets/q-soba-195/) | refactor claiming no behaviour change, large mechanical diff | **clean**, fresh, register sealed |
| (r) | [`r-base-ui-5460`](../../../bench/targets/r-base-ui-5460/) | frontend component logic, React or comparable; settleable statically or by a focused test, never visually | buggy, fresh, register sealed |

Eight buggy, two clean. False findings are counted on every target, not only clean ones, so the
two clean targets and the refactor trap are not the only precision evidence. Fresh-target rules:
merged public pull requests with post-merge evidence (follow-up fix, revert, or issue); a register
sealed by an adjudicator who has seen no reviewer output; a truncated mirror and a merge-time packet
cutoff.

**How the fresh targets were chosen (2026-09-24).** One vetting hunt per slot, then one independent
adjudicator per chosen candidate, each a headless Opus 5.5 session at `high` (ledger S14–S21,
$26.29). Each hunt checked every candidate against the #148 criteria E1–E10 (unused by any earlier
grid, merged recently with an upstream confirmation or, for (q), an eight-week cleanliness window,
small, packet-buildable at the merge instant, a GitHub-native review trail, offline focused
execution on this machine, statically visible, not the promised behaviour, public and permissive)
and preferred merges on or after 2026-07-01. The adjudicator got the hunt's proposal as an
unproven hypothesis and the full history, and wrote the register; it confirmed each slot's
expected status, corrected facts in two hunts, and, for one target, recorded more than the hunt
proposed. The registers, hunt reports and rulings are sealed ([`sealed/`](sealed/README.md)).
Three slots were filled from the preferred window; (o) was not: of 31 security candidates examined,
none merged on or after 2026-07-01 passed, so it is a March 2026 merge from the fallback window,
disclosed in its `target.json`. Each target's truncated mirror, dependency cache and smoke checks at
both revisions are built and recorded like the regression set's.

Two procedural notes. The hunts and adjudications ran on Opus 5.5 rather than #137's Sonnet 5,
at the maintainer's request, which roughly doubles their price. And while the hunts ran, the
preparation checkout was switched to another branch from 18:44Z to 18:58Z, so the hunt prompt's
list of used pull requests was missing from disk for those 14 minutes. The transcripts show the
(o), (p) and (r) hunts had read it at 18:40Z, before the switch; the (q) hunt's read failed inside
the window, and it checked E1 against the list as committed instead. No later step switched the
checkout while a session was reading it.

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

**Scoring procedure, settled 2026-09-25 after the grid and before any grading.** An independent
review of the scoring plan (ledger S25) settled what the text above leaves open. The run's
eighteenth deviation records it.

- **Graders.** One fresh headless session, `claude-opus-5-5` at `high` as for every helper in this
  run, grades each target, single-threaded, under a fresh home,
  in an export directory holding only that target's reviews rendered by `normalize_review.py
  --render` under random tokens, the whole register, the rubric, the packet and an offline
  provisioned clone. A read audit of the grader's transcript takes that directory as its only
  root; a leak means the target is graded again under new tokens. `bench/tools/grade.py` prepares,
  dispatches and unblinds. Opus 5.5 is also arm C's model, so a grader preference for its own
  model's reviews is possible and is disclosed, not controlled; the maintainer chose it over
  Fable 5.1, which no arm runs, at about 2.5 times the price.
- **What the grader decides**: each item's assignment, its `duplicate_group` within the review,
  and the fix sufficiency of a recovery, judged from the whole item because only arm A has a fix
  line.
- **What is derived after unblinding, per arm.** `completion`: A is `completed` when the skill
  reported complete; B, C and D unless the attempt stopped. `approved_on_buggy` as above;
  `zero_recovery` from the grader's assignments. `priority_error`: A, a recovery not marked
  `must-fix` or a non-material item marked `must-fix`; B `n/a`, because its `high` variant gives no
  ordering instruction; C, a recovery listed after a non-material item, because its variant
  instructs "Sort by severity" (checked in att-011's archived transcript); D, a recovery whose
  `P<n>` ranks below a non-material item's.
- **Blinding residue beyond §4**: a non-empty fix line, and an observation rendered as `(no
  file)`, both mark arm A.
- **New candidates.** A plausible material claim the register lacks is `unresolved` in mapping
  v1 and goes to one independent adjudicator, given the claim with arm, attempt and cost labels
  removed and the register. Every ruling versions the register (a defect or a non-defect) and
  produces mapping v2; a new defect also means a blind re-grade of every attempt on that target
  for that defect alone. `results.v1.json` pins mapping v1 and `results.v2.json` uses v2.
- **The reveal.** The fresh registers are opened one at a time, only after the tests pass and all
  six regression targets are mapped. Once a plaintext register exists on disk, the run is closed
  to dispatch.

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

## 10. Freeze (2026-09-24)

The four items open at the first draft, and how each closed:

1. **Rates and quota.** The Sonnet 5 and Opus 5.5 rates were re-read from the live pricing page on
   2026-09-24 and match the cached entries (Opus 5.5 cache reads at `$0.20`; the Sonnet increase
   announced for 2026-09-01 did not occur); `bench/rates.json` carries them as dated 2026-09-24
   entries, which the run references. The ChatGPT plan's quota at the freeze is in the ledger
   (S24): 62% of the weekly window used, resetting 2026-09-26T09:19:52Z.
2. **Focused-test execution under D and B on a suite target.** Not demonstrated before the freeze:
   a demonstration on a suite target is a chargeable attempt on that target, and the pilot's four
   cells ((i) and (n) under B and D) are exactly that, with their valid rows counting. The pilot
   therefore carries this demonstration; if either arm cannot run the target's allowed command,
   the record shows it and the deviation is written before the sealed order continues. The
   shakedown's clean-home Codex probes confirmed the fixture defect statically, and the pinned D
   adapter honoured `workspace-write` there (§9). The pilot ran on 2026-09-25: D ran offline zsh
   checks under (n)'s allowance, and B ran nothing beyond one `git diff` on either target. It also
   surfaced three harness defects in the Codex post-processing, fixed in `0200519`; the run
   README's pilot section has the details. The two affected Codex attempts were re-filed from their
   own outputs with no replacement (the manifest's second deviation).
3. **The run manifest.** Written and frozen at
   [`bench/runs/2026-09-24-builtin-baseline/manifest.json`](../../../bench/runs/2026-09-24-builtin-baseline/manifest.json):
   arms with file hashes, the `review-code` tree `c3c53da5…`, the CLI versions and prompt hashes
   three pre-dispatch probes observed on the toy fixture (ledger S22–S24, $0.33), the cohort with
   register versions and packet, diff and provisioning identities, the 80 planned cells, the caps
   of §6, a sealed order generated by a recorded procedure with the pilot first, the rates, and
   the execution policy. The probes found Claude Code at `2.1.282` (the shakedown ran `2.1.281`)
   with both built-in prompt bodies unchanged, and Codex CLI `0.156.1` reachable only through a
   pinned path after the machine's node upgrade; the run README records the pins.
4. **The ledger's attempt table** opened before the probes ran.

Done since the first draft: targets (i)–(n) migrated with factual packets, rebuilt mirrors and
verified diff identities; dependency caches archived with hashes and smoke checks measured on the
suite machine; the shakedown filed as a run with attempt records and computed results; CLI test
siblings for `attempt_audit.py` and `normalize_review.py`; `run_cell.py` (the caps and the
method's dispatch record checked before every dispatch, then `dispatch.sh` and `file_attempt.py`),
`score.py` and `compare.py`; targets (o)–(r) hunted, adjudicated by a session that saw no reviewer
output, provisioned and smoke-checked, with their registers, hunt reports and rulings sealed (§5);
the run frozen.

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

## 12. Results (2026-09-25)

Scored as §8 settles it: twelve blind grading sessions, three candidate adjudications and three
one-defect re-grades, all Opus 5.5 at `high` ($18.11 with the plan review; ledger "Scoring").
[`results.v2.json`](../../../bench/runs/2026-09-24-builtin-baseline/results.v2.json) is the
answer: mapping v2 on (i), (j) and (l), v1 elsewhere, no unresolved item.
[`results.v1.json`](../../../bench/runs/2026-09-24-builtin-baseline/results.v1.json) pins mapping
v1 everywhere, leaving unresolved the 11 items that raised the five candidates. The tables below
are printed by [`answers.py`](answers.py) from results v2, the attempt records and the mappings; a
ratio is the median over the 20 cells matched to A's by target and replicate, a cell's cost
counting every attempt it took.

| Arm | Reviews | Recall, completed-only (attempt-level) | False findings raw / unique per review | Approved on buggy | Zero recovery | False clean | Noise per review |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A review-code | 21 | 0.708 (0.667) | 0.00 / 0.00 (0 / 0) | 8/17 | 4/17 | 4/17 | 1.0 |
| B built-in Sonnet 5 | 22 | 0.792 (0.792) | 0.09 / 0.09 (2 / 2) | 0/16 | 2/16 | 0/16 | 2.6 |
| C built-in Opus 5.5 | 20 | 0.844 (0.844) | 0.35 / 0.35 (7 / 7) | 0/16 | 2/16 | 0/16 | 6.2 |
| D codex review | 20 | 0.573 (0.573) | 0.00 / 0.00 (0 / 0) | 3/16 | 5/16 | 3/16 | 0.2 |

Per target: attempt-level recall (`-` on a clean target), then raw false findings and zero-recovery reviews.

| Target | A review-code | B built-in Sonnet 5 | C built-in Opus 5.5 | D codex review |
| --- | --- | --- | --- | --- |
| i-requests-6667 | 0.67; ff 0; zr 0 | 0.83; ff 0; zr 0 | 1.00; ff 0; zr 0 | 0.33; ff 0; zr 0 |
| j-trpc-5017 | 0.00; ff 0; zr 2 | 0.25; ff 0; zr 1 | 0.75; ff 1; zr 0 | 0.25; ff 0; zr 1 |
| k-graphql-js-1582 | 1.00; ff 0; zr 0 | 1.00; ff 0; zr 0 | 1.00; ff 1; zr 0 | 1.00; ff 0; zr 0 |
| l-bokeh-9232 | 1.00; ff 0; zr 0 | 1.00; ff 0; zr 0 | 1.00; ff 0; zr 0 | 1.00; ff 0; zr 0 |
| m-grpc-go-7390 | -; ff 0; zr 0 | -; ff 0; zr 0 | -; ff 2; zr 0 | -; ff 0; zr 0 |
| n-ripgrep-2957 | 1.00; ff 0; zr 0 | 1.00; ff 1; zr 0 | 1.00; ff 0; zr 0 | 0.00; ff 0; zr 2 |
| o-astro-16079 | 0.67; ff 0; zr 0 | 1.00; ff 1; zr 0 | 1.00; ff 1; zr 0 | 1.00; ff 0; zr 0 |
| p-hono-5067 | 1.00; ff 0; zr 0 | 1.00; ff 0; zr 0 | 1.00; ff 2; zr 0 | 1.00; ff 0; zr 0 |
| q-soba-195 | -; ff 0; zr 0 | -; ff 0; zr 0 | -; ff 0; zr 0 | -; ff 0; zr 0 |
| r-base-ui-5460 | 0.00; ff 0; zr 2 | 0.25; ff 0; zr 1 | 0.00; ff 0; zr 2 | 0.00; ff 0; zr 2 |

| Arm | Matched cells | Median cost ratio to A | Arm total cost ($) | Median elapsed-to-payload ratio to A | Median elapsed to payload (s) |
| --- | --- | --- | --- | --- | --- |
| A review-code | 20 | 1.00 | 15.99 | 1.00 | 134 |
| B built-in Sonnet 5 | 20 | 0.18 | 3.04 | 0.21 | 28 |
| C built-in Opus 5.5 | 20 | 0.45 | 7.52 | 0.58 | 85 |
| D codex review | 20 | 0.35 | 5.92 | 0.23 | 31 |

| Target | Register | Defect | Recovered by |
| --- | --- | --- | --- |
| i-requests-6667 | v2 | GT-i1 | A, B, C, D |
| i-requests-6667 | v2 | GT-i2 | A, B, C |
| i-requests-6667 | v2 | GT-i3 | A, B, C |
| j-trpc-5017 | v2 | GT-j1 | B, C, D |
| j-trpc-5017 | v2 | GT-j2 | C |
| k-graphql-js-1582 | v1 | GT-k1 | A, B, C, D |
| l-bokeh-9232 | v1 | GT-l1 | A, B, C, D |
| n-ripgrep-2957 | v2 | GT-n1 | A, B, C |
| o-astro-16079 | v1 | GT-o1 | A, B, C, D |
| p-hono-5067 | v1 | GT-p1 | A, B, C, D |
| r-base-ui-5460 | v1 | GT-r1 | **none** |
| r-base-ui-5460 | v1 | GT-r2 | B |

Answers to the preregistered questions, per arm against A:

- **Material recall per completed review.** C 0.84, B 0.79, A 0.71, D 0.57. Attempt-level, with
  harness-invalid attempts at zero: C 0.84, B 0.79, A 0.67, D 0.57. Attempt-level by cohort: on the
  regression targets C reaches 0.95 and A 0.73; on the fresh four, B leads with 0.75 and A has
  0.56.
- **False findings per review.** A and D none in 21 and 20 reviews; B 2 in 22 (0.09 per review); C
  7 in 20 (0.35), two of them on the clean control (m). Unique counts equal raw counts: no
  review repeated a false claim.
- **Review-level rates on buggy targets.** A approved 8 of its 17 reviews on buggy targets and
  4 of those recovered nothing (false clean); D approved 3 of 16, all false clean; B and C never
  approve, because an empty findings array is their only approving form and neither produced one.
  Zero recovery: D 5, A 4, B 2, C 2. A's approvals follow §8's rule that `Approved` approves
  whatever the items say: four of A's eight approvals carried a recovered defect at `consider`,
  and those four recoveries are four of A's five priority errors. The fifth is att-055's GT-i3
  recovery, not marked `must-fix`, in a `Changes Requested` review.
- **Matched median cost ratio.** B 0.18, D 0.35, C 0.45 of A's cost; A spent $15.99 on its
  cells, C $7.52, D $5.92 (list price; D consumed ChatGPT-plan quota), B $3.04.
- **Elapsed-to-payload ratio.** B 0.21, D 0.23, C 0.58 of A's; median elapsed to payload B 28 s,
  D 31 s, C 85 s, A 134 s.
- **Registered defects no arm recovered:** GT-r1 (a controlled value normalized during blur
  discards the blur validation result). GT-j2 was recovered only by C and GT-r2 only by B.

What these numbers rest on, and do not show:

- **Two replicates per cell.** Each arm's per-target figure rests on two valid reviews, and the
  fresh cohort is four targets; differences of one review are within noise.
- **The grader is Opus 5.5, arm C's model** (§8), so a preference for C's reviews is possible and
  uncontrolled. C also writes the most items per review (8.3; A 1.7, B 3.7, D 0.9), which the
  blind rendering could not hide.
- **Registers grew during scoring.** (i) gained GT-i3, raised by A, B and C reviews, and (j)
  GT-j2, raised by one C review; GT-i3 is confirmed upstream by the later revert, GT-j2 by the
  adjudicator's reproduction. One item on (l), which the adjudicator ruled a duplicate of GT-l1,
  did not recover it on the blind re-grade and counts as non-material.
- **This is a benchmark, not an adoption screen.** It preregistered questions, not thresholds, and
  nothing here authorizes a change to any skill.

