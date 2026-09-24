# Built-in reviewer benchmark — `review-code` against Claude Code's `/code-review` and Codex `review`

**Status: draft preregistration, not frozen.** Phase 0 (mechanism shakedown) ran on 2026-09-24;
its records are in §9 and the independent review of the first draft is in §11. No scored cell has
been dispatched. Freezing happens when §10's open items are closed and this file is committed with
its stage-1 commit named in `ledger.md`.

This bundle follows [the one-shot method](../code-review-one-shot-method.md) for freezing,
inputs, attempt accounting, adjudication and scoring, and departs from it only where §3, §4 and
§8 say so. It is a **benchmark**, not an adoption screen: it preregisters questions, not
thresholds, and nothing it measures authorizes changing any skill.

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

| Arm | What runs | Model / prompt variant | Row label |
| --- | --- | --- | --- |
| A | `skills/review-code` at the pinned tree, invoked as a caller would: `mode: one-shot`, `return_format: artifacts`, render-only | `claude-sonnet-5` / `high`, verifiers the same | `review-code` |
| B | Claude Code built-in `/code-review` | `claude-sonnet-5` / session `--effort high`; the built-in then selects `high effort → 3+5 angles × 6 candidates → 1-vote verify (recall-biased)` | `claude-builtin-sonnet` |
| C | Claude Code built-in `/code-review` | `claude-opus-5-5` (the harness default when no `--model` is passed, observed in §9) / session `--effort high`; the built-in then selects `high effort → 8 inline angles → dedup (no verify)` | `claude-builtin-opus` |
| D | Codex `codex review`, as shipped | Codex default model and reasoning effort as the CLI header reports them (`gpt-6-astra`, `reasoning effort: none` on 2026-09-24) | `codex-review-default` |

A/B is the matched pair that separates skill from model. **B/C is not a model ablation**: the
built-in chooses its prompt per model, and under Opus it runs an inline, no-verifier variant (§9),
so B/C compares two shipped configurations of the same product. D is a product comparison: what a user gets by typing the
command. The built-in's **as-shipped default** is not run: with no effort argument in a fresh home
it selects the `low` variant (`minimal prompt → single careful diff pass → ≤15 findings`, §9),
which would differ from B in both model and prompt; that fact is recorded here and the `low`
variant is left to a later experiment. `/code-review ultra` and the Codex GitHub app are excluded
by construction. The publish step of `review-code-publish` is not under test; nothing is posted.

**Arm A runs without the research-report dispatch of prior grids.** The #137 template made the
reviewer write a staged research report during the review, which the independent review (§11)
identified as an intervention the other arms do not receive. Here A is invoked the way
`review-code-publish` invokes it, and the run record is derived afterwards from the skill's own
artifacts (`report.md`, `run-events.jsonl`, the private directory) and the transcripts. No
production-shaped subtraction is applied to any arm; every arm's billed cost is reported as-is.

Pins recorded at freeze: `skills/review-code` tree hash; Claude Code version (`2.1.281` at
shakedown), because the built-in's prompts are compiled into the binary; Codex CLI version
(`0.156.1`); SHA-256 of the built-in prompt text the subagent received for each variant that runs
(`high` on 2.1.281: `30dad62c…78e40`; `low`, recorded not run: `95d10a8c…bff4`), kept outside
the repository because the prompt is proprietary; and the presence of Codex's rubric system text
(`You are acting as a reviewer for a proposed code change`) in each D child rollout. A pin that
changes mid-grid invalidates the affected cells.

## 3. Isolation

The first shakedown probes under the maintainer's normal environment were both contaminated:

- `claude -p "/code-review …"` resolved the **user-level `~/.claude/skills/code-review`** (the
  Matt Pocock two-axis Standards/Spec skill), not the built-in.
- `codex review` read **`~/.agents/skills/review-code/SKILL.md`** (a symlink into the
  maintainer's iCloud skills, which hold this repository's own skill) and applied
  `~/.codex/AGENTS.md`.

Isolation for every B, C and D attempt, all verified in §9:

1. **Fresh home per attempt.** A new directory outside `/tmp` (Codex refuses to create PATH
   helpers under `/tmp`) holding only the credentials: for Claude, `.claude/.credentials.json` and a
   `.claude.json` reduced to the account and onboarding keys; for Codex, `.codex/auth.json` and a
   `trust_level` entry for the clone. `HOME` (and `CODEX_HOME`) point at it. No `CLAUDE.md`,
   `AGENTS.md`, skills, plugins, hooks or typed-effort history exist there, so the built-in's
   "reuse the level you typed last" rule has nothing to reuse and the effort argument alone selects
   the variant.
2. **`--safe-mode`** for Claude, which additionally disables bundled plugin skills the built-in
   might otherwise see; the bundled `code-review` itself stays available.
3. **Network off.** Claude: `--allowedTools "Bash,Read,Glob,Grep,Agent"` (no `WebFetch`,
   `WebSearch`); Codex: the sandbox's `network_access: false`. Bash itself can reach the network, so
   the read audit below also covers `curl`/`gh`/`git fetch` invocations.
4. **Post-hoc read audit** ([`tools/attempt_audit.py`](tools/attempt_audit.py)). Every command
   and file read is in the transcript (Claude: root plus `subagents/agent-*.jsonl`; Codex: the
   child rollout's `exec` items). An attempt that read any path outside the clone, the attempt
   directory (which holds the fresh home and the reviewer's `TMPDIR`), or that ran a network
   command, is **harness-invalid**: it stays in the denominators and cost totals with zero
   admissible recovery and is replaced inside the cap. Probes of `AGENTS.md`/`CLAUDE.md` in
   ancestors of the clone are recorded as guidance probes and violate only if the file exists;
   the clone's ancestors are kept free of guidance files. A tree identity mismatch between
   dispatch and exit is likewise harness-invalid.
5. **Truth kept unreadable, as far as this machine allows.** The four fresh registers and every
   adjudication note are stored as a passphrase-encrypted archive until scoring; the sealed (i)–(n)
   registers are already public on GitHub and in the maintainer's checkouts, so a same-user process
   *could* read them. The audit in item 4 is the control; a separate Unix user would be stronger
   and is recorded as a limitation, not done.

Arm A runs from the same fresh home with the pinned `skills/review-code` tree copied in as its
only user skill (no `--safe-mode`, which would disable it), `model: "sonnet"` on every sub-agent,
and items 3–5.

Two more facts the adapters rely on: the built-in runs its review inside a **forked subagent**
whose transcript is `<session-dir>/subagents/agent-*.jsonl` (the root transcript bills nothing);
the Codex review runs in a **child thread** (`thread_source: subagent`, `parent_thread_id` set) and
the parent rollout records no usage.

## 4. Adapters — identical inputs, native outputs, mechanical normalization

**Inputs.** An offline clone at the pinned head with local branch **`main`** at the merge-base
and `review-head` checked out (the built-in's Phase 0 runs `git diff main...HEAD` whatever the
argument says, §9, so the pinned range is honoured only under that naming), dependencies
preinstalled; the byte-identical phase-1 packet from
[`build_packet.py`](../tools/build_packet.py); the execution allowance (five minutes per focused
command, ten minutes provisioning). The packet is transported to each arm the only way that arm
accepts text: A through its caller contract; B/C in the prompt after the target argument
(`/code-review <base>...review-head high` followed by the packet); D as the review's
custom-instructions argument read from stdin, naming the range (`git diff <base>...review-head`)
and carrying the packet, because `codex review --base` **refuses a prompt** (§9). Each attempt's
executed diff command is checked against the pinned range from the transcript. D's sandbox is
pinned to `workspace-write` on the disposable clone (`-c sandbox_mode="workspace-write"`, honoured
in §9) so it can run focused checks as A can; a before/after tree identity check catches mutation.

**Wrapper.** [`tools/dispatch.sh`](tools/dispatch.sh) builds the fresh home, exports `TMPDIR`
inside the attempt directory, records the tree identity before and after, writes the timing
sidecar, and runs the arm: A through the Skill tool with the caller inputs above; B/C with
`--safe-mode`, `--model`, session `--effort` and the argument; D with the stdin prompt and
`workspace-write`. **Outputs per attempt.** `prompt.txt`, `dispatch.txt` (versions, model, effort,
skill tree hash), the native final output verbatim (A's `artifacts/{composition,payload,report}`;
B/C's `payload.json` from the audit, holding the final text and any `ReportFindings` input; D's
`stdout.txt`), `audit.json`, `normalized.json`, `timing.json`, and the usage row.

**Normalized schema.** Review level: `native_verdict` (A's status; B/C: `empty-array` or
`findings`; D: `overall_correctness` when the rubric JSON is present in the child rollout, else
the stdout summary line) and `arm_reported_complete`. Finding level: `file`, `line_start`,
`line_end`, `claim`, `consequence`, `proposed_fix` (nullable), `native_priority` (A and D `P<n>`;
B/C rank position), `native_action` (A only: `must-fix`/`consider`), `native_confidence`
(B/C `verdict` when present). **No `blocking` flag is derived**: the review of the first draft
showed that mapping Codex priorities or built-in ranks to a blocking bit invents action
information. **No `kind` is derived by keyword** either; every item is a finding until an
adjudicator classifies it (§8). Normalization is mechanical ([`normalize_review.py`](../tools/normalize_review.py), stdlib,
self-tested against the toy fixtures) and blind to the register; a parse failure is recorded, not repaired by hand.

**Blinding.** Scorers receive uniformly rendered items (location, claim, consequence, fix) with
native formatting, priority labels, verdict words and arm-identifying structure stripped, under
`blind-<hash>.md` names. Residual cues (prose style, item count) are disclosed; blinding is a
mitigation, not a guarantee.

## 5. Targets

Six targets are reused from the [#137 preregistration](../one-shot-qualification-2026-09-07/README.md)
§Targets; their SHAs and packet hashes are pinned there. **Their registers are the versioned ones
after #137's adjudication**, not the originals: target (n) gained GT-n1 (the `.zshrc` snippet
carries a `$ ` prompt prefix and cannot work as pasted; [evaluation §2](../one-shot-qualification-2026-09-07/evaluation.md))
and is **buggy**, so the reused set is five buggy and one clean. Mirrors are rebuilt from the
pinned SHAs ([#333](../review-code-rewrite-2026-09-22/acceptance/README.md) found the historical
mirrors unavailable); a rebuilt packet must hash to the recorded value or the deviation is recorded.
Four fresh targets are hunted for the shapes the regression set lacks. Shape is the **sampling
rationale**, not a causal claim: prior grids varied shape, language and repository together, so
results are reported per target and per shape as observations.

| Slot | Shape | Domain | Truth |
| --- | --- | --- | --- |
| (i) | concurrency, shared mutable state | Python HTTP client | buggy, sealed (GT-i1, GT-i2) |
| (j) | cross-file type obligation outside the diff | TypeScript API | buggy, sealed (GT-j1) |
| (k) | changed-test correctness | JavaScript | buggy, sealed (GT-k1) |
| (l) | ordinary behavioural change | TypeScript frontend widget | buggy, sealed (GT-l1) |
| (m) | clean, high risk | Go concurrency | clean, sealed |
| (n) | promised change that does not work as pasted | Rust project, shell surface | buggy, sealed (GT-n1, versioned register) |
| (o) | security: authorization or injection | web backend | buggy, fresh |
| (p) | released-compatibility break | public API or SDK | buggy, fresh |
| (q) | refactor claiming no behaviour change | any, large mechanical diff | **clean**, fresh |
| (r) | frontend component logic | React or comparable | buggy, fresh; defect settleable statically or by a focused test, never visual |

Eight buggy, two clean. False findings are counted on every target, not only clean ones, so the
two clean targets and the refactor trap are not the only precision evidence. Fresh-target rules:
merged public PRs with post-merge evidence (follow-up fix, revert, or issue); register sealed by an
adjudicator who has seen no reviewer output; truncated mirror and merge-time packet cutoff.

**Training-data exposure.** Every target is public and may be in any model's training data, and
the six reused targets have additionally shaped this repository's skill development. Controls: the
merge date, the fix-publication date and each model's published cutoff are recorded per target;
regression and fresh results are reported **separately**; post-cutoff cases are preferred for the
fresh slots; and chronology is never claimed to prove non-exposure.

## 6. Grid, order, caps

| | |
| --- | --- |
| Planned cells | 4 arms × 10 targets × 2 replicates = **80** |
| Order | **replicate 1 of every target and arm first** (40 cells), arm order rotated per target and sealed before dispatch; then replicate 2 in balanced four-arm blocks per target in the sealed order |
| Concurrency | at most two cells in flight |
| Replacements | at most **4** across the grid, 84 attempts total; a harness-invalid cell is replaced, a miss never is |
| Pilot | targets (i) and (n), arms B and D, one replicate each, before the sealed order runs; valid rows count |

**Budget.** Dated rates: Sonnet 5 `$2/$10`; Opus 5.5 `$4/$20`, cache read `$0.20` (the `claude-api`
skill's table cached 2026-06-24; re-checked against the pricing page at freeze); GPT-6 Astra `$10/$50`, cached input `$1`, cache
write `$12.50` (launched 2026-09-03, looked up 2026-09-24). Expected per-cell spend, with A from
prior grids and the built-ins scaled up from §9's five-line-diff probes to a grid-sized diff:

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
(`plan_type: prolite` in the rollout's rate-limit block), so D's cost column is a list-price
equivalent from [`codex_usage.py`](../tools/codex_usage.py) and its real constraint is the plan's
weekly quota, recorded in the ledger before each D dispatch. The `$250` cap counts the list-price
equivalent so the arms stay comparable.

## 7. Metering

| Arm | Meter | Inputs |
| --- | --- | --- |
| A | `transcript_usage.py --prices 2,10` | root transcript and every sub-agent transcript |
| B, C | `transcript_usage.py --prices <model rates>` | `<session-dir>/subagents/agent-*.jsonl` only; the root has no billed turn and makes the meter exit 2 |
| D | `codex_usage.py --sessions-dir <fresh CODEX_HOME>/sessions --session <root thread> --prices 10,50 --cached-mult 0.1 --cache-write-mult 1.25` | gathers child threads by `parent_thread_id`; ordinary input is `input − cached − cache_write`; a malformed line or inconsistent usage exits 2 and the attempt keeps an upper-bound reservation instead of a total |

Timing sidecars record `root_dispatched_at` immediately before the CLI call, `payload_validated_at`
when `normalized.json` is written, and `completed_at` at CLI exit.

## 8. Adjudication and scoring

Section 4 of the method applies: material defect, false finding (raw and unique, including
unsupported assertions), false clean, fix sufficiency, priority errors, questions, duplicates,
three cost views, elapsed-to-payload. Clarifications for arms that lack `review-code`'s vocabulary:

- **False clean** is measured on **buggy targets**, as the method defines it: a completed review
  whose payload recovers no registered defect. Per-arm review-level outcomes are fixed now: A
  `Approved`; B/C an empty array; D `patch is correct` or a stdout summary with no finding. A
  buggy-target review that recovers nothing but was not a clean verdict (incomplete, or findings
  that all miss the register) is **zero recovery**, reported separately.
- **Action errors** are scorable for A only. For D, priority errors use its `P<n>`; for B/C,
  rank errors (a material defect ranked below a non-material item).
- **Materiality is adjudicated, not keyword-classified.** Every normalized item is scored the
  same way in every arm: material recovery, false finding, or non-material (cleanup,
  observation, hygiene). Non-material items go to a **noise column** per review. A "waste" item
  that establishes a material performance failure is a recovery; a guidance-rule item that
  establishes an explicit requirement failure is a recovery.
- **Per-shape breakdown** is the primary table: recall, false findings and false-clean per target
  per arm. Macro figures are secondary. Regression (i)–(n) and fresh (o)–(r) are tabulated apart.
- Unexpected plausible findings go to blind adjudication and the register is versioned before
  rescoring; a clean target that turns buggy is a target-mix deviation.

Preregistered questions, answered per arm against A: material recall per completed review; raw
and unique false findings per review; false-clean rate on buggy targets; matched median cost
ratio; elapsed-to-payload ratio; and the set of registered defects no arm recovered.

## 9. Shakedown record (Phase 0, 2026-09-24)

Toy repository: one Python file, base commit adds two helpers, head commit adds `average()` that
divides by `len(prices)` while its docstring says empty lists are common. Every valid probe found it.

| Probe | Valid | Model | Turns | Tool calls | Input | Cache write | Cache read | Output | Wall | Cost ($) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude, normal home: user skill shadowed the built-in | **invalid** | claude-sonnet-5 | 2 | 1 | 4 | 17,831 | 36,873 | 749 | 0:00:07 | 0.09 |
| B: built-in, `--safe-mode`, `--model sonnet`, `high` | valid | claude-sonnet-5 | 2 | 1 | 4 | 14,855 | 13,964 | 261 | 0:00:03 | 0.04 |
| C: built-in, fresh home, `--safe-mode`, no `--model`, no effort | valid, ran the **`low`** variant | claude-opus-5-5 | 4 | 3 | 8 | 14,143 | 38,756 | 562 | 0:00:05 | 0.10 |
| codex, normal home: read the maintainer's `review-code` skill | **invalid** | gpt-6-astra | 4 | — | 13,717 | 0 | 40,704 | 633 | — | 0.20 list |
| D: codex, clean home under `/tmp`, `--base base` | valid; no prompt possible | gpt-6-astra | 3 | 2 | 8,046 | 0 | 13,824 | 379 | 0:00:12 | 0.11 list |
| D: codex, clean home outside `/tmp`, prompt on stdin naming the range, `workspace-write` | valid | gpt-6-astra | 3 | 2 | 11,660 | 0 | 10,496 | 361 | 0:00:12 | 0.15 list |

Wrapper runs on the toy (all four arms, [`comparison-data.md`](comparison-data.md)): every arm
found the defect; A billed `$0.50` over 17 requests with one verifier, the others about `$0.10`.

Observations carried into §2–§4:

- The `high` built-in did not fan out its eight angles or run a verifier on a five-line diff (two
  requests, one `git diff`, findings as a fenced JSON array). Whether it fans out on grid-sized
  diffs is recorded per cell from the subagent count. Its Phase 0 ran `git diff main...HEAD`
  despite the `base..review-head` argument, which coincided on the toy repository; the grid checks
  the executed diff against the pinned range.
- With no effort argument in a fresh home the built-in ran the `low` variant, which submits via a
  `ReportFindings` call (`level: "low"`, `verdict: CONFIRMED`) instead of the JSON block, and the
  harness default model was `claude-opus-5-5`. The effort **argument alone does not select the
  variant** (Opus with `high` as an argument still ran `low`); the session `--effort high` flag
  does, and under Opus it selects `8 inline angles → dedup (no verify)` rather than Sonnet's
  fan-out-and-verify prompt. Hence arm C's definition in §2.
- `codex review --base <branch>` exits 2 with `--base <BRANCH> cannot be used with '[PROMPT]'`
  when a prompt is given. The stdin-prompt transport ran `git diff base...review-head` exactly as
  instructed, kept the rubric (four rubric markers in the child rollout), and honoured
  `workspace-write`. Under the clean home Codex still walked up the tree looking for `AGENTS.md`
  (`find .. -name AGENTS.md`, `ls /tmp/AGENTS*`) and found none; the clone's parent directory must
  therefore stay free of guidance files.
- The clean-home Codex probes confirmed the crash **statically** (diff and file reads only); the
  first, contaminated run was the one that executed `average([])`. Focused-test execution under
  the final D adapter is demonstrated separately in §10.
- Priority varied between two otherwise identical D probes (`P2`, then `P1`): a reminder that
  replicate variance is real and priority is not a stable signal for scoring.

## 10. Open before freeze

1. Re-check Opus 5.5 rates against the pricing page; record the ChatGPT plan quota.
2. Done on 2026-09-24: normalizer, wrapper, audit, and toy fixtures for all four arms
   ([`comparison-data.md`](comparison-data.md)). Remaining: a CLI test sibling for
   `normalize_review.py` and `attempt_audit.py` beyond their self-tests.
3. Demonstrate focused-test execution under D's final adapter (a target whose review needs a test
   run) and under B; A reproduced the toy error at the head already.
4. Rebuild mirrors and packets for (i)–(n); compare packet hashes with the recorded values; pin
   the versioned (n) register.
5. Hunt, adjudicate and seal (o)–(r); encrypt the registers; the adjudicator sees no reviewer
   output.
6. Record CLI versions, prompt hashes, model cutoffs and per-target merge and fix dates.
7. Open `ledger.md` with the setup entries before any further chargeable step; the shakedown
   probes above are its first rows.

## 11. Independent review of the first draft (2026-09-24)

A Codex reviewer (`gpt-6-astra`, reasoning `high`, read-only) reviewed the first draft of this
file and the meter. Its report is kept at the bundle's `review-1.md`. Disposition of each item:

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
