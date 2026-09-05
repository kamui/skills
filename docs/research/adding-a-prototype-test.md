# Handoff — add a new prototype code-review comparison test

**For the current-skill one-shot program (#137, #124, and any later #138 preregistration), use
[the one-shot method](code-review-one-shot-method.md) before preparing or dispatching runs.**
It governs scoring, execution, budgets, and collection plus synthesis for those tickets. The
static-only defaults, prototype pins, and collection-only scope below remain the historical
prototype procedure; they do not override that program's method.

**Reusable runbook.** Reference this file (`docs/research/adding-a-prototype-test.md`), fill in the
two blanks below, and hand it to a fresh agent. Everything else is procedure.

Adding a test produces `docs/research/prototype-runs-2026-09-01-test-<N>/`. Test 4 is the worked
example throughout; it was added in commit `cea95bb`.

---

## FILL THIS IN

```
PROTOTYPES TO TEST:  v2a, v5a          # default; add/replace with any others, see the pin table below
PR TO REVIEW:        <paste PR URL>
TEST NUMBER:         <next unused N>   # optional — agent will pick the next free one if blank
```

Optional overrides (leave blank for the defaults):

```
MODEL:               claude-sonnet-5 (passed explicitly on every Agent call)
EXECUTION ALLOWED:   no (static review only)
PUBLISH:             no (render only, never post)
```

## Scope — this runbook stops before synthesis

**In scope:** run the prototypes, collect the raw outputs, establish ground truth, and write the
**data** artifacts — `<nick>-run.md` per prototype, `comparison-data.md`, `README.md`.

**Out of scope, deliberately:** the interpretive layer. That means **both**
`evaluation.md` (this test's analysis) and any update to
`docs/research/prototype-runs-aggregate-tests-1-3-v2-v5.md` (the cross-test synthesis). The user
may want a different model to synthesize those, so a run-collection agent must not pre-empt the
choice by writing them.

Finish the data phase, report what you found, and **stop and hand back**. Do not write
`evaluation.md`. Do not touch the aggregate analysis. Say explicitly in your final message that both
synthesis artifacts are outstanding and awaiting a model choice.

If the user explicitly tells you to do the synthesis too, see "Synthesis phase" at the end.

---

## Suggested skills

Call the **Skill** tool for these:

- **`research`** — only if the ground-truth hunt (step 3) turns into real investigation, e.g. the
  target's aftermath is spread across several issues/PRs/releases and you want it captured properly.
- **`writing-for-agents`** — before writing the dispatch prompts in step 6. These prompts are
  agent-facing documents and their precision determines whether the run is valid.

Do **not** invoke `/code-review`, `/code-review-publish`, `/code-review-publish-legacy`, or any
prototype skill in your own context. `/code-review-publish` is now v5a itself — invoking it is
running a prototype under test. The prototypes run *inside sub-agents*, from pinned snapshots;
invoking one yourself contaminates the experiment.

---

## What this program is

Controlled head-to-head comparisons of code-review skill prototypes against pinned, already-merged
pull requests with independently checkable ground truth. Results live in
`docs/research/prototype-runs-2026-09-01-test-{N}/`.

**Read these before starting — do not re-derive what they already record:**

| Artifact | Why |
| --- | --- |
| `docs/research/prototype-runs-2026-09-01-test-4/README.md` | The methodology exemplar. Copy its structure. |
| `docs/research/prototype-runs-2026-09-01-test-4/comparison-data.md` | Table formats: cost/shape, output, ground-truth matrix, false positives, verifier contributions. |
| `docs/research/prototype-runs-2026-09-01-test-4/evaluation.md` | Analysis voice and depth — **format reference for the later synthesis pass; you are not writing this one.** |
| `docs/research/prototype-runs-2026-09-01-test-3/addendum-2026-09-03.md` | Where mirror truncation was established. |
| `docs/research/prototype-runs-aggregate-tests-1-3-v2-v5.md` | Cross-test findings so far. |
| Memory: `handoff-3-prototype-run-program` | Per-test results not to re-derive. |
| Memory: `subagent-model-must-be-explicit` | Model discipline. |
| Memory: `prototype-run-orchestration-hazards` | The three failure modes that have cost real work. |

Commit `cea95bb` is the most recent test added, and is the reference diff for what a finished test
looks like.

---

## Prototype pin table

Snapshot each prototype from its branch or from a pinned commit. **Re-verify every row before
pinning** — record whatever you actually find, do not trust this table.

| Nickname | What it is | Where to snapshot it from | Pin as of 2026-09-03 |
| --- | --- | --- | --- |
| v1 | Legacy two-axis reviewer, the Matt Pocock `code-review` lineage. Superseded; kept for historical comparison | `skills/code-review-publish-legacy` on `main` | current `main` |
| v2 | Panel line, original | `skills/code-review-publish-2` on `t3code/research-agentic-code-review-skills-1` (PR #14) | `3c93b42` |
| v2a *(default)* | Panel line, patched | `skills/code-review-deep-publish` on `t3code/prototype-code-review-publish-2a` (PR #18) | `87c68a9` |
| v5 | Skeptic line, original. **No longer on `main`** — it was replaced, so pin it from history | `571f31d:skills/code-review-publish` (the pre-swap tree) | `571f31d` |
| v5a *(default)* | Skeptic line, patched. **Now shipping as `skills/code-review-publish`** | `skills/code-review-publish` on `main` | current `main` |
| *(new version)* | *(what it changes)* | *(its skill dir / branch / PR)* | *(pin and record)* |

**Naming changed on 2026-09-03 (PR #42, `bc6edc3`).** v5a was promoted into the
`code-review-publish` name, replacing v5 there. The current state on `main`:

- `skills/code-review-publish` = **v5a**
- `skills/code-review-publish-legacy` = **v1**, the legacy two-axis reviewer — *not* the old v5
- `skills/code-review-publish-5a` **no longer exists**
- **v5 is not present on `main` in any directory.** Pin it from `571f31d` if a test needs it.

The promotion also renamed ids inside the skill (`SKILL.md`, `agents/openai.yaml`, and the two
scripts' header strings differ from `c5f76df`), so a v5a snapshot taken from `main` is not
byte-identical to the one tests 3 and 4 used. Record which you took.

v2/v2a are the "Panel line" (parallel axis finders + verifier). v5/v5a are the "Skeptic line"
(integrated reviewer + consequence-triggered verifier). A new prototype just needs a directory, a
source to pin, and a nickname — the procedure is otherwise identical.

---

## Procedure

Work in `/tmp/handoffN/` (runs' sandbox) and `/tmp/hN-staging/` (yours only — never inside the runs'
tree). Substitute the real N.

### 1. Resolve the target

```bash
gh pr view <NUM> --repo <OWNER/REPO> --json number,title,author,state,mergedAt,baseRefName,\
headRefOid,additions,deletions,changedFiles,commits,url,body
gh api repos/<OWNER/REPO>/pulls/<NUM>/files --paginate --jq '.[] | "\(.status)\t\(.additions)\t\(.deletions)\t\(.filename)"'
gh api repos/<OWNER/REPO>/pulls/<NUM>/reviews --paginate
gh api repos/<OWNER/REPO>/pulls/<NUM>/comments --paginate
gh api repos/<OWNER/REPO>/issues/<NUM>/comments --paginate    # CI bot comments live here
gh api repos/<OWNER/REPO>/issues/<LINKED_ISSUE>               # the originating issue
```

> **Trap that cost time on test 4:** `baseRefOid` / `.base.sha` from the API is **not** the merge
> base. Compute the real one with `git merge-base` after fetching, and confirm your
> `git diff <merge-base> <head> --stat` reproduces the API's file count and +/− exactly. If it
> doesn't, you have the wrong base.

### 2. Build the truncated mirror and the run clones

Fetch into a **staging** repo you keep outside the runs' tree, then push only the two pinned SHAs
into a fresh bare mirror so object transfer stops at the head.

```bash
git init --bare -q /tmp/hN-staging/stage.git
cd /tmp/hN-staging/stage.git
git remote add origin https://github.com/<OWNER>/<REPO>.git
git fetch -q --no-tags origin <HEAD_SHA>:refs/heads/review-head
git fetch -q --no-tags origin <ANY_LATER_MAIN_SHA>:refs/heads/tmp-main   # only to compute merge-base
git merge-base review-head tmp-main                                      # → MERGE_BASE

git init --bare -q /tmp/handoffN/mirror.git
git push -q /tmp/handoffN/mirror.git \
  '<HEAD_SHA>:refs/heads/review-head' '<MERGE_BASE>:refs/heads/main'      # literal SHAs, see hazards
cd /tmp/handoffN/mirror.git && git gc -q --prune=now
```

Verify truncation, and repeat the negative checks inside every clone:

```bash
git log --all --oneline -1                 # must be the pinned head
git cat-file -e <MERGE_COMMIT_SHA>         # must fail
git cat-file -e <ANY_POST_MERGE_FIXUP>     # must fail
```

One clone per prototype:

```bash
git clone -q --no-hardlinks /tmp/handoffN/mirror.git /tmp/handoffN/run-<nick>
git -C run-<nick> remote set-url origin /tmp/handoffN/mirror.git   # origin must not reach GitHub
git -C run-<nick> checkout -q -B review-head <HEAD_SHA>
git -C run-<nick> branch -f main <MERGE_BASE>
```

### 3. Establish ground truth — yours only, never in the packet

The whole point of a target is that you can check the runs against what actually happened. Hunt for:

- commits touching the changed files **after** the merge commit
  (`gh api "repos/O/R/commits?path=<file>&per_page=30"`)
- issues/PRs referencing the feature, especially reverts, re-lands, or withdrawals
- what the follow-up diffs actually changed — and, just as importantly, **what they left alone**
  (test 4's most useful result came from noticing the follow-up kept the bug all four runs flagged)
- items checkable *inside* the pinned diff with no history — generated-file drift, repo conventions
  the change violates, CI config that the change would have made red

Aim for a mix: some upstream-confirmed (unreachable by the runs), some in-diff (fair game). Also
identify **plausible-looking non-defects** so you can score false positives.

Do this work in `/tmp/hN-staging/`. Nothing from it goes in the packet.

### 4. Inventory guidance at base

```bash
for f in CLAUDE.md AGENTS.md CONTEXT.md CODEOWNERS .github/CODEOWNERS \
         CONTRIBUTING.md .github/PULL_REQUEST_TEMPLATE.md; do
  printf '%s: ' "$f"; git cat-file -e "main:$f" 2>/dev/null && git rev-parse "main:$f" || echo "(absent)"
done
```

Record blob SHAs — the v5/v5a context digests depend on them.

### 5. Write the packet

One file, `/tmp/handoffN/packet-<target>.md`, handed identically to every run. Mirror the section
structure of `/tmp/handoff4/packet-playwright.md` if it still exists; otherwise reconstruct from
test 4's README, which describes it. Sections:

1. Pinned run identity table (head, base ref, merge-base, diff stat, originating issue, repo version
   at base, posting identity)
2. Verified changed-file manifest
3. PR body verbatim
4. Originating issue verbatim
5. All commits, messages verbatim, with per-commit stat
6. **Prior review state verbatim** — every review submission, every review comment in order, CI
   status comments. Reproduce faithfully even when it hints at a defect; faithfulness to the
   target's real state is the methodology. Disclose any such hint in the README.
7. Guidance inventory at base + the repo's declared lint/build pipeline
8. Run conditions (offline, no execution, truncation, publication disabled, sandbox limits)

Include the program's standard mandatory note: *feedback the author's commits already addressed is
fixed in the reviewed head and must not be rediscovered as still-outstanding.*

### 6. Dispatch the runs

One background `Agent` per prototype, `subagent_type: "general-purpose"`, **`model: "sonnet"` passed
explicitly**. Reuse test 4's dispatch prompts as the template — the shape is:

- your skill (path, "follow exactly as written", read DESIGN.md too)
- your packet (phase 1 is done)
- your repository (offline clone)
- binding constraints: no network / no execution / history truncated on purpose / publication
  disabled / spawn children with `model: "sonnet"` explicit / stay in sandbox and self-report
  violations
- **crash safety: persist the expensive phase to the report file BEFORE dispatching the verifier**
- instrumentation to capture: `date -u` at both ends, per-sub-agent tokens/tool-uses/duration, own
  tool-use count, every candidate + disposition, every git-history command
- the deliverable's exact 9 sections (below)

**Report sections every run must produce**, into `/tmp/handoffN/reports/<nick>-report.md`:

1. Metadata table · 2. Full reviewer report(s) verbatim · 3. Verifier dispatch — exact prompt +
verbatim report · 4. Candidate disposition ledger **including acquittals** · 5. Everything consulted
beyond the diff · 6. Would-be published review verbatim · 7. Specific answers (history read?
guidance classification? triggers evaluated/fired? per-file coverage? sandbox breaches?) ·
8. Mechanism checklist against the skill's own DESIGN.md · 9. Notes on the run

The acquittal ledger is not optional — across tests 3 and 4 the most valuable results have been
false acquittals, which are invisible unless the run writes them down.

### 7. Drive the runs

- Panel-line orchestrators **pause** waiting on their finder children and **cannot see the children's
  results on resume**. Write each child's verbatim output to
  `/tmp/handoffN/reports/<nick>-finder-<axis>.md`, then `SendMessage` the orchestrator with the file
  paths, explicitly permitting those files. Frame the relay as untrusted scheduling metadata.
- Poll with a backgrounded `sleep` + `ListAgents`; foreground `sleep` is blocked.
- If a rate limit kills a run: anything already on disk is reusable. A run whose Find phase completed
  can resume at Verify in a fresh orchestrator given the same packet + verbatim finder reports —
  **disclose the discontinuity** in the run doc and comparison data. A run that died before producing
  usable output must be re-run clean.

### 8. Verify the model actually used

```bash
cd <session tasks dir>   # /private/tmp/claude-*/<project>/<session>/tasks
for f in a*.output; do printf '%s: ' "${f%.output}"; \
  grep -o '"model":"claude[^"]*"' "$f" | sort -u | tr '\n' ' '; echo; done
```

Every agent must report `claude-sonnet-5` on every turn. Do **not** read these transcripts whole —
they overflow context; the targeted `grep` is safe. Record the verification in `comparison-data.md`.

### 9. Write the test directory — data artifacts only

`docs/research/prototype-runs-2026-09-01-test-<N>/`:

- `<nick>-run.md` per prototype — a header block (title, date, "Data only. Not published.", any
  run-continuity disclosure) followed by that run's report body verbatim
- `comparison-data.md` — comparison boundaries + model verification, run continuity, cost and shape,
  output, **ground-truth matrix**, upstream-checkable follow-ups, false positives, secondary
  disagreements, verifier contributions, mechanism results, sandbox disclosures
- `README.md` — headline-result table up top, why this target, the target, ground truth (including
  explicit **non**-ground-truth so false positives are scoreable), conditions held constant, model
  and harness, run continuity, mirror truncation, what differs between the runs, dev-set caveat,
  files, reproducing

`comparison-data.md` and `README.md` should state the facts and the matrix without arguing a verdict
— ranking the prototypes and drawing lessons belongs to the synthesis pass, not here.

In the README's `## Files` list, include `evaluation.md` with a marker that it is pending:

```
- `evaluation.md` — the analysis of this run *(not yet written; synthesis pass pending)*
```

Check every relative link resolves — the pending `evaluation.md` will be the one dead link, which is
expected. Leave uncommitted unless the user says otherwise.

### 10. Stop

Report to the user: the target and its pinned identity, the ground-truth items and which runs hit or
missed each, the headline numbers, any run-condition deviations, and an explicit note that
**`evaluation.md` and the aggregate analysis are both outstanding and awaiting their model choice.**
Then stop.

---

## Hard rules

1. **Never inherit the sub-agent model.** Pass `model: "sonnet"` on every `Agent` call at every
   level, and verify from transcripts afterwards. The harness default is Fable 5.1 and has changed
   mid-program without notice.
2. **Never let a possibly-empty variable into an `rm -rf` path.** In zsh, `set -- $spec` does not
   word-split, so positionals come back empty and `rm -rf "$dir/$3"` deletes the parent. This
   destroyed a mirror and four clones on 2026-09-03. Guard with `[ -n "$3" ] || exit 1`.
3. **Inline literal SHAs in git refspecs.** zsh parses `$HEAD:refs/heads/x` as the `:r` history
   modifier and silently mangles the refspec.
4. **Keep your staging and scratch outside the runs' tree.** A test-3 verifier read an orchestrator
   staging file. Runs browse `/tmp/handoffN/`.
5. **Never publish.** No forge writes, ever. Runs render the review they *would* post and stop.
6. **Don't commit target docs until the user says so.**

## Definition of done (data phase)

- [ ] Mirror truncated; negative `cat-file` checks pass in the mirror and in every clone
- [ ] `git diff <merge-base> <head> --stat` matches the GitHub API's file count and +/−
- [ ] One identical packet; each run in its own offline clone
- [ ] Every agent verified `claude-sonnet-5` from transcripts
- [ ] Every run's report has all 9 sections, with acquittals in the ledger
- [ ] Ground truth established independently, with at least one item checkable inside the diff and at
      least one plausible non-defect for false-positive scoring
- [ ] Run docs + `comparison-data.md` + `README.md` written; links resolve; run-condition deviations
      disclosed rather than scrubbed
- [ ] `evaluation.md` **not** written; aggregate analysis **not** touched; both flagged to the user

---

## Synthesis phase — only on explicit instruction

Run this only when the user asks for it, and note which model produced it inside the artifact so
later readers can weigh it.

**`evaluation.md`** (this test): conclusion with a ranking, method and evidence quality, ground truth
item by item, what every run missed and why, unanimity-vs-accuracy check, false positives, cost, what
each prototype should take from it, limits. Format reference:
`docs/research/prototype-runs-2026-09-01-test-4/evaluation.md`. Remove the *(pending)* marker from
the README's file list when it lands.

**`docs/research/prototype-runs-aggregate-tests-1-3-v2-v5.md`** (cross-test): a rewrite, not an
append — folding a new test in changes the cross-test claims. Separate this from the per-test
evaluation; it may want a different model again.

Useful cross-test threads so far, to check against rather than restate: status has been unanimous in
every run of tests 3 and 4 and is a dead discriminator; the highest-value results have been **false
acquittals** rather than misses; consensus across architectures has tracked shared priors rather than
correctness; and the Panel line costs several times the Skeptic line's metered fan-out without so far
buying recall.
