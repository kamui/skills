# Research report — `n-bea6be14-seed2-att-24`

Target: **(n) BurntSushi/ripgrep#2957** ("feat(completion): support sourcing zsh completion dynamically")
Cell: `n-bea6be14-seed2`, attempt `att-24`
Skill snapshot: `/tmp/qual137/snapshots/bea6be14/skills/code-review-publish/`
Reviewer model: `claude-sonnet-5` (this session). No sub-agents were spawned (see §7 — verification trigger did not fire), so there is no sub-agent model to report beyond this session's own.

Payload file (rendered, would-be-published review): [`n-bea6be14-seed2-att-24-payload.md`](./n-bea6be14-seed2-att-24-payload.md)

---

## 1. Metadata

| Field | Value |
| --- | --- |
| Target | `BurntSushi/ripgrep#2957`, merged 2024-12-31T13:23:13Z |
| Posting identity | `kamui` (third party, did not author the PR, no prior comments/reviews on it) |
| Mode | Retrospective review of a merged pull request; publication disabled (per packet §1 and skill's Boundaries section) |
| Base ref / SHA | `master` / `79cbe89deb1151e703f4d91b19af9cdcc128b765` |
| Head SHA | `855bfa6cdae4f4fe8762f892fc4957635397083e` |
| Merge-base | `79cbe89deb1151e703f4d91b19af9cdcc128b765` (identical to base SHA; recomputed locally with `git merge-base master review-head`, matches packet) |
| Skill's `workflow` identifier | `v5b-10` (from `validate_review.py`'s `WORKFLOW` constant, line 115) |
| Model — reviewer (this session) | `claude-sonnet-5` |
| Model — sub-agents | N/A; none spawned |
| Verification trigger fired? | **No.** See §7 for the exact quoted sentences and reasoning. |
| Sub-agents spawned | **Zero** (role/count/subagent_type: none — no verifier batch, no clean-verdict batch, no finder fan-out; this skill's step 3 is single-integrated-reviewer by design: "This single integrated reviewer is the complete frequent path; do not fan out separate code and requirements finders.") |
| Candidates raised | 3 (see §3 ledger): 1 survivor (finding), 2 dropped |
| Candidates surviving primary falsification | 1 (`faq/zsh-source-caveat-grammar`, P3/consider/maintainability) |
| Verifier verdicts | N/A — no verifier dispatched |
| Findings for publication | 1 — P3/consider, `faq/zsh-source-caveat-grammar`, anchor `FAQ.md:138-139` |
| Questions | 0 |
| Observations | 1 (fenced-code-block language-tag inconsistency in the new zsh section of FAQ.md) |
| Coverage | Complete — both changed files reviewed; both risk-relevant checks (issue-fit compatibility risk, changed-artifact hygiene) settled with evidence; no packet gap, no omitted diff chunk |
| Derived status | `Approved (advisory)` — no unsettled `must-fix`, coverage complete, no open question |
| Own token usage | Not reported by this harness to the agent; I have no figure to give. |

---

## 2. The one surviving finding, in full

**id:** `faq/zsh-source-caveat-grammar`
**Priority / action:** P3 / consider (`blocking=false`)
**Kind:** `maintainability`
**Anchor:** `FAQ.md:138-139` (`side=RIGHT`, line range, commit-pinned to head `855bfa6cd`)
**Fix location:** same as anchor (no separate `fix` — omitted from the trailer as the output contract specifies for that case)

**Claim:** The new caveat sentence added by this diff, "Note though that while this approach is easier to setup, is generally slower than the previous method, and will add more time to loading your shell prompt." (`FAQ.md:138-139` at head), drops the subject before its second clause: "…while this approach is easier to setup, **is** generally slower…" has no subject for "is generally slower," so the sentence reads as a fragment mid-parse.

**Trigger scenario:** Any reader of FAQ.md's zsh completion section, after this change, reaching the "Or if you'd prefer to load and generate completions at the same time" paragraph.

**Impact:** The reader has to reparse the sentence to work out that "is generally slower" and "will add more time" both describe "this approach" (the `source <(...)` method); as written, the middle clause has no explicit subject, which is the kind of drift a technical-writing-conscious maintainer would want fixed — the same diff earlier fixes a separate, unrelated typo ("completes" → "completions") in the same file, evidence the author already cares about textual correctness here.

**Change requested:** Add a subject, e.g.: "…while this approach is easier to set up, **it** is generally slower than the previous method, and will add more time to loading your shell prompt."

**Verification status:** `primary-confirmed`. Not independently verified because it meets none of the skill's mandatory-verification triggers (not `must-fix`, not security/authorization, not data loss/corruption, not a destructive migration, not an externally observable compatibility break — see §7 for the exact quoted rule). It is a plain textual fact (a demonstrable missing-subject construction), so I judged the extra verification round unnecessary and the rubric does not require it.

**Evidence:** `git show 855bfa6cdae4f4fe8762f892fc4957635397083e:FAQ.md` lines 136-140 (read directly, quoted verbatim above); confirmed absent from the merge-base version (`git show 79cbe89deb1151e703f4d91b19af9cdcc128b765:FAQ.md` has no zsh "recommended approach"/"Note though" text at all — the entire passage, including the flawed sentence, is new in this diff, so gate 2 (introduced-here) is trivially satisfied).

---

## 3. Complete private disposition ledger

### 3a. Issue-fit ledger (rubric §"Issue fit", built before reading the diff for compliance)

| Row | Source coordinate | Class | Disposition | Evidence |
| --- | --- | --- | --- | --- |
| A | `issue-2956` (body, verbatim: "`_arguments:comparguments:327: can only be called from completion function`" when sourcing directly) | acceptance requirement | **met** | `crates/core/flags/complete/rg.zsh:437-444` (head) branches on `$funcstack[1] == _rg` vs. `$+functions[compdef]`; confirmed by tracing the code and by executing the exact sourcing sequence in a real zsh with `compinit` already active (scratch script `test2_with_compinit.zsh`, exit 0, no error, `_comps[rg]` becomes `_rg` — scratch script `test4_verify_comps_registered.zsh`). |
| B | `pr-body/"Now, you can dynamically source completions in zsh by running `source <(rg --generate complete-zsh)`"` | acceptance requirement (PR promise of a concrete outcome) | **met** | Same evidence as row A; the promised command succeeds without error under the same conditions the issue reporter's own working setup implies (compinit/completion system already active — the reporter's `.zshrc` snippet in issue #2956 already sources `fzf --zsh`, `gh completion -s zsh`, `fd --gen-completions`, all of which presuppose a working zsh completion system). |
| C | `pr-body` test plan step 2 (`rg --generate=complete-zs<TAB>` must still complete correctly after sourcing) | acceptance requirement (PR promise / regression check) | **met** | Traced: `compdef _rg rg` registers the same `_rg` function the normal `_arguments` completion path already used (confirmed args dump includes `complete-zsh\:"shell completions for zsh"` under the `--generate=` spec); scratch test 4 confirms `_comps[rg]=_rg` is set after sourcing via the fixed code, so subsequent completion dispatch reaches `_rg` the normal way (case where `$funcstack[1]==_rg`, i.e. the same code path that ran unconditionally before this diff). |

No `not-verifiable` rows. No versioned-artifact conformance applies (`conformance.md` not read/applicable — see §10 note).

### 3b. Candidate ledger (falsify-every-candidate pass)

| id | kind | claim (one line) | disposition | decisive evidence | falsification reason | ruled on by verifier? |
| --- | --- | --- | --- | --- | --- | --- |
| `faq/zsh-source-caveat-grammar` | `maintainability` | New sentence `FAQ.md:138-139` drops the subject before "is generally slower" | **survivor** (see §2 for full record) | `FAQ.md:138-139` (head) vs. absence at merge-base | N/A — survives | No. Doesn't meet any mandatory-verification trigger (`consider`, not security/data-loss/migration/compat-break); zero-survivor mode doesn't apply because a candidate does survive as a finding. |
| `zsh/source-before-compinit-still-errors` | `requirement` | The PR-body promise "you can dynamically source completions in zsh" is only true when `compdef` is already defined (i.e. `compinit` has already run); sourcing before that still reproduces a variant of the original error | **dropped** | `crates/core/flags/complete/rg.zsh:439-444` (head, case `! $+functions[compdef]` branch calls `_rg "$@"` directly); reproduced with scratch script `test1_no_compinit.zsh` (`zsh -f`, no compinit ever run): `source` of the file directly errors with `_rg:341: command not found: _arguments` — same failure *class* as the original bug, in the one scenario (no completion system initialized at all) that this diff does not cover. | Fails gate 7 (worth the author's time) and gate 8 (proportionate rigor), not gate 4 (I *did* prove the exact consequence). Reasoning: (a) the issue reporter's own demonstrated `.zshrc` already has a working completion system (sources `fzf --zsh`, `gh completion -s zsh`, `fd --gen-completions`, all of which presuppose `compinit`/`compdef`), so the fix covers the reporter's actual scenario; (b) the *same* class of unstated precondition (a working completion/dynamic-loading mechanism must already exist) is already present, unflagged, in the pre-existing bash instructions (`bash_completion` directory requires the `bash-completion` package's dynamic loader) and fish instructions elsewhere in the same FAQ section, so singling this one caveat out would exceed the FAQ's evident level of rigor; (c) this exact idiom (`source <(cmd --zsh-flag)`) is how fzf/gh/fd — the very tools the issue cites — document their own zsh integration, without spelling out the compinit precondition either, establishing it as the ecosystem convention this FAQ is following, not deviating from. | No — dropped before it could reach a survivor batch; no verifier ran at all this cell (§7). Not related-acquittal eligible either (no survivor shares its file/claim — the surviving finding is a pure grammar fix at a different sentence, not this mechanism). |
| `zsh/fpath-before-compinit-ordering` | `requirement` | The new "recommended approach" (`fpath=($HOME/.zsh-complete $fpath)`) only works if this line runs *before* `compinit`; the FAQ doesn't say so | **dropped** | Reproduced with scratch script `test3_fpath_after_compinit.zsh`: after `compinit` has already run, adding the directory to `fpath` and *not* re-running `compinit` leaves `_comps[rg]` `UNSET` — the completion is not picked up. | Same reasoning as the row above (gates 7/8): this is the standard, ecosystem-wide zsh-fpath-before-compinit convention, and the pre-existing (unflagged, unchanged-by-this-diff) bash/fish sections carry an analogous unstated assumption about their own dynamic-loading mechanisms. This candidate also directly addresses the exact gap `okdana` raised in prior review thread 9 ("these instructions don't really do anything as written") — the PR's fpath addition *is* the agreed fix for that gap, and the review record shows the maintainers considered the fpath instruction sufficient once added (thread 10, `vegerot`: "I can do that", followed by the merged fpath line); nothing in the review record asked for an explicit compinit-ordering caveat, and gate 6 further weighs against inflating this into a new defect the review record already effectively settled by accepting the fpath line as sufficient. | No — dropped, same as above. |

Both dropped candidates were considered for the Observations route (rubric: "Route an accurate fact to Observations when it fails finding admission specifically on meaningful or proven consequence") and **did not qualify**, because neither fails on gates 1/4 — I did prove concrete consequence for both, with a specific reproduction. They fail on gates 7/8 instead, which the rubric's Observations paragraph does not cover ("A fact that passes gates 1 and 4 at any priority is a finding, not an observation: admit it, or drop it on the gate it actually fails, rather than routing it to Observations…"). Both are therefore private-ledger-only, never rendered anywhere, consistent with "for every candidate that is not a survivor, the retained ledger row is at most a one-line claim…".

### 3c. Observation (rubric-eligible, published)

- **Fact:** The new zsh code blocks in `FAQ.md` (added by this diff) are tagged with the ```` ```zsh ```` language for syntax highlighting, while the adjacent, unchanged bash, fish, and PowerShell code blocks in the same FAQ section remain untagged (plain ```` ``` ````).
- **Why not a finding:** No demonstrated reader or maintenance consequence beyond cosmetic inconsistency — fails gate 1 (meaningful impact) cleanly, which is exactly the Observations route's admission condition.
- **Evidence:** `FAQ.md:107-141` (head) — bash block at ~`FAQ.md:107-111`, fish at ~`FAQ.md:113-117`, zsh (new, tagged) at ~`FAQ.md:120-135`, PowerShell (unchanged, untagged) immediately after.
- Rendered in the payload's `## Observations` section, one sentence + one `Evidence:` pointer, no `should`/`must` language, per `output-contract.md`'s Observations format and `validate_review.py`'s `check_observation`.

---

## 4. Sub-agent dispatches

**None.** No verifier batch, no clean-verdict batch, and no finder fan-out were dispatched. See §7 for the exact trigger analysis. Consequently there are no prompts or verbatim sub-agent reports to reproduce here, and rule 10 ("dispatch every sub-agent in the foreground… never end your turn while a sub-agent of yours is still running") is vacuously satisfied — there was nothing to dispatch or wait on.

---

## 5. Everything consulted beyond the diff

All commands below ran directly in this session (never via a sub-agent), from the pinned clone `/tmp/qual137/runs/n-bea6be14-seed2-att-24` unless noted, and none mutated the clone (verified: `git status` in the clone reported "nothing to commit, working tree clean" both before and after this run's activity, since every read used `git show`/`git diff`/`git log`/`git merge-base`, all non-mutating).

### Skill and packet reading (once each, per skill's read discipline)
- Read `SKILL.md` in full.
- Read `references/review-rubric.md` in full.
- Read `references/output-contract.md` in full.
- Read `references/verifier.md` in full (loaded per SKILL.md's instruction to read it "when verification is required" — I read it proactively during setup to know the trigger conditions before falsification, since I needed to evaluate whether any candidate would meet the trigger; it was not applied to any batch since none was dispatched).
- Read `references/verifier-concurrency.md` in full (same proactive reasoning; not applicable to the diff, no concurrency/invariant candidate arose).
- Read `references/conformance.md` in full, to confirm it does not apply (no versioned artifact, schema, or generated-source-with-generator-input is at stake in this diff — the zsh completion script is hand-maintained with a *test*, `ci/test-complete`, that checks it against `rg --help`, not a generator that produces it).
- Did **not** read `references/re-review.md` — not applicable, since the posting identity `kamui` has no prior comments or reviews on this pull request per the pinned packet, so step 1's re-review trigger ("the packet holds any prior review, reply, or trailer-bearing comment from the posting identity") does not fire. This is stated explicitly rather than silently skipped.
- Read `/tmp/qual137/packets/n/packet.md` in full (the pinned phase-1 packet).

### Clone inspection (read-only; `git -C` implicit via cwd)
- `git status` (clone hygiene check, confirmed clean before and after)
- `git log --oneline -5 review-head` and `git log --oneline -5 master` — both stayed within/behind the pinned head `855bfa6cd`; see §8 for the explicit history-discipline statement.
- `git diff master review-head --stat`
- `git diff master review-head -- FAQ.md crates/core/flags/complete/rg.zsh` (full targeted diff, matches the review_context.py output byte-for-byte)
- `git merge-base master review-head` → confirmed `79cbe89deb1151e703f4d91b19af9cdcc128b765`, matching the packet's pinned merge-base
- `git show master:docs/agents/issue-tracker.md` → confirmed absent (exit non-zero, "does not exist in 'master'") — satisfies SKILL.md step 1's "Read the base-branch `docs/agents/issue-tracker.md` when present" with a negative result
- `git show 79cbe89deb1151e703f4d91b19af9cdcc128b765:FAQ.md | sed -n '85,145p'` — base-branch FAQ.md text around the completion section
- `git show 855bfa6cdae4f4fe8762f892fc4957635397083e:FAQ.md | sed -n '85,150p'` — head-branch FAQ.md text, same section
- `git show 855bfa6cdae4f4fe8762f892fc4957635397083e:FAQ.md | grep -n "Note though"` and `sed -n '136,140p'` — pinpointed the exact anchor lines (138-139) for the surviving finding
- `git show 855bfa6cdae4f4fe8762f892fc4957635397083e:crates/core/flags/complete/rg.zsh | sed -n '1,40p'` — file header, `#compdef rg` directive, start of `_rg()` function definition
- `git show 855bfa6cdae4f4fe8762f892fc4957635397083e:crates/core/flags/complete/rg.zsh | sed -n '420,450p'` — the changed tail logic in full context
- `grep -n "_RG_COMPLETE_LIST_ARGS\|_arguments\b" crates/core/flags/complete/rg.zsh` (repo-wide? **No** — scoped to this one file; case-sensitive; this was sufficient because the only file in play is this one, not a repo-wide propagation/synchronization-drift check, which the rubric requires only for drift candidates, and no drift candidate arose)
- Guidance-file presence loop: `git show master:"$p"` for `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, and every path-scoped `AGENTS.md`/`CLAUDE.md` in each ancestor directory of both changed paths (`crates/`, `crates/core/`, `crates/core/flags/`, `crates/core/flags/complete/`) — all confirmed absent, independently corroborating the packet's §7 table. Not repo-wide (targeted at ancestor directories of changed paths only, per the output contract's `guidance` membership rule, which is itself directory-scoped, not repo-wide).
- Read `ci/test-complete` in full (98 lines) — the repository's own documented verification command for this exact file, referenced by name in the changed file's own header comment ("Run ci/test-complete after building…").

### Execution (permitted under packet §8 run condition 2; all under `/tmp/qual137/work/n-bea6be14-seed2-att-24/scratch/`, zsh, offline, none touched the clone's working tree, each well under the 5-minute bound)
1. `which zsh; zsh --version` → `/bin/zsh`, zsh 5.9 (arm64-apple-darwin26.0). Exit 0, instantaneous.
2. `test1_no_compinit.zsh` — sources the head version of `crates/core/flags/complete/rg.zsh` directly in a `zsh -f` shell with no `compinit` ever run. **Exit 1** from the sourced script's own return code (echoed as `EXIT_STATUS=1`), outer script exit 0. Output: `_rg:341: command not found: _arguments`. Decisive evidence for the dropped candidate `zsh/source-before-compinit-still-errors`.
3. `test2_with_compinit.zsh` — runs `compinit -u` first (so `compdef` exists), then sources the same file directly. **Exit 0**, no error; dumps the full `_rg` function body to confirm it redefined correctly; `funcstack` is empty after sourcing (confirms the file returns to top-level scope, not left "inside" a function). Decisive evidence for Issue-fit rows A and B (`met`).
4. `test3_fpath_after_compinit.zsh` — runs `compinit -u` first, checks `_comps[rg]` is unset, adds a directory containing a copy of the head's `rg.zsh` (renamed `_rg`) to `fpath`, and checks `_comps[rg]` again *without* re-running `compinit`. **Exit 0**; both checks print `UNSET`. Decisive evidence for the dropped candidate `zsh/fpath-before-compinit-ordering`.
5. Direct `zsh -f -c '...'` replicating `ci/test-complete`'s `get_comp_args` (`_RG_COMPLETE_LIST_ARGS=1 source $1` in a subshell) **without** first setting `local_options unset` — surfaced an unrelated `no_unset`-option artifact (`_rg:1: curcontext: parameter not set`) that does not occur in the real `ci/test-complete` invocation (which does set `local_options unset`); recorded as a false start, not evidence, and immediately corrected in the next run.
6. Same replication **with** `setopt local_options unset` exactly as `ci/test-complete`'s `get_comp_args` function does — **exit 0**, produced a 341-line argument-spec dump starting with `+`, `(exclusive)`, `(: * -)-h[display help information]`, etc. Confirms `ci/test-complete`'s core sourcing mechanism (case 2 of the new branch: `compdef` undefined because the test never calls `compinit`) is unaffected by this diff — no regression to the existing CI check's mechanism, though the *full* `ci/test-complete` script (which also needs a built `rg` binary to diff against `rg --help`) could not be run end-to-end because building the crate is disallowed under packet run condition 2.
7. `test4_verify_comps_registered.zsh` — runs `compinit -u`, confirms `_comps[rg]` starts `UNSET`, sources the head file directly (taking the new `compdef` branch), confirms `_comps[rg]` becomes `_rg` afterward. **Exit 0**. Decisive evidence for Issue-fit row C (`met`) — this is the mechanism the PR's test-plan step 2 (`rg --generate=complete-zs<TAB>`) depends on.

None of these seven commands took more than a few seconds; all well inside the 5-minute-per-command bound. No network access was attempted or available; no `cargo build`/`cargo test` was attempted.

### Tooling (this skill's own scripts, run from the skill directory as required)
- `python3 scripts/review_context.py --merge-base 79cbe89deb1151e703f4d91b19af9cdcc128b765 --head 855bfa6cdae4f4fe8762f892fc4957635397083e --store <mktemp -d path>/review-context-855bfa6cdae4f4fe8762f892fc4957635397083e.json` — run **exactly once**, from the clone's working directory (cwd inside the clone at invocation time). Exit 0. Output: manifest (2 files, +29/−4), full diff (both hunks, un-withheld), ranges, history, and a `chunks` inventory reporting `diff coverage: complete (2/2 chunks consumed)`. Nothing was `missing`; no rebuild or `--from` recovery read was needed.
- `python3 scripts/context_fingerprint.py <context_input.json>` — run once, with a hand-built JSON payload (no `--packet` flag, since no raw forge JSON pages exist in this offline cell — only the pre-normalized `packet.md`). Per the script's own docstring and `output-contract.md`'s "On a forge without that packet, supply `pr`, `issues`, `specs`, and `guidance` directly from the exact reviewed inputs," I supplied `pr.title`/`pr.body` and the one issue's `coordinate`/`title`/`body`/empty `comments` verbatim from the pinned packet, plus `specs: []` and `guidance: []` (both empty, confirmed independently in the clone). Output digest: `fea14e64c218222905fc4b1fc7bde1d1907a2826ffb04195d9add739b148f6a1` (64 lowercase hex chars, verified with `wc -c`).
- `python3 scripts/validate_review.py --render < payload.json` — printed the one summary-reference fragment (`anchor [\`FAQ.md:138-139\`](...)`), pasted verbatim into the summary body.
- `python3 scripts/validate_review.py < payload.json` — **exit 0**, zero violations, on the assembled payload (summary + the one finding item + the one observation item).
- `python3 scripts/validate_review.py --emit-batch < payload.json > batch.json` — **exit 0**, produced the one-call forge-native batch (`commit_id`, `event=COMMENT`, `body`, one `comments[]` entry for `FAQ.md:138-139`). Not submitted anywhere (offline, non-publishing retrospective mode; no `gh api` call made).
- `python3 /tmp/qual137/mark_event.py /tmp/qual137/reports/n/n-bea6be14-seed2-att-24-timing.json payload_validated_at` — run once, immediately after the final `validate_review.py` exit-0, as the dispatch instructs. Confirmed the timing file now carries `payload_validated_at`.
- Did **not** run `scripts/test_context_fingerprint.py`, `scripts/test_forge_packet.py`, or `validate_review.py --self-test` — the dispatch explicitly says "Compute the context digest once, as your contract specifies; do not run the skill's self-tests inside this cell," and `SKILL.md` itself states these self-tests "belong in the skill repository's CI, not in a review."
- Did **not** run `scripts/forge_packet.py normalize` — there is no raw forge JSON to normalize in this offline cell; the phase-1 packet substitutes for it per the dispatch's explicit instruction ("the 'pin the review' step already done for you… If your skill's phase 1 asks you to resolve the target from the forge, that phase is satisfied by this packet").

---

## 6. The `context` digest

**Digest:** `fea14e64c218222905fc4b1fc7bde1d1907a2826ffb04195d9add739b148f6a1`

Computed once with `python3 scripts/context_fingerprint.py` over this exact JSON (saved at `/tmp/qual137/work/n-bea6be14-seed2-att-24/private/context_input.json`):

- `pr.title`: `"feat(completion): support sourcing zsh completion dynamically"`
- `pr.body`: the pull-request body verbatim from packet §3 (Summary / Test plan / "Closes #2956", including the fenced `zsh` code block)
- `issues`: one entry — `coordinate: "BurntSushi/ripgrep#2956"`, `title: "Can't source zsh completions directly"`, `body`: the issue body verbatim from packet §4 (including the `.zshrc` example and the reproduced error), `comments: []` (packet §4 states 0 issue comments and `comments_available: true`, so the default `comments_available` stays `true` and is omitted per the script's own normalization rule — "Each key is added to the normalized issue only when false")
- `specs`: `[]` — no user-supplied spec
- `guidance`: `[]` — no root or path-scoped `AGENTS.md`/`CLAUDE.md`, and no root `CONTEXT.md`, confirmed both by the packet's §7 table and independently by direct `git show master:<path>` checks against every ancestor directory of both changed paths (§5)

---

## 7. Mechanism checklist

| Mechanism | Fired? | Where demonstrated |
| --- | --- | --- |
| Question channel | **Did not fire.** | No candidate met the rubric's static-unresolvability bar ("no static evidence could settle the fact"). Every claim in this review was settled by reading the diff, the base/head file states, and by direct zsh execution — nothing was left as an empirical unknown requiring a maintainer answer. |
| Clean-verdict / related-acquittal verification | **Did not fire.** | Zero-survivor mode requires "zero candidates survive *as findings*"; one candidate (`faq/zsh-source-caveat-grammar`) survived as a finding, so this mode's precondition is false. Related-acquittal mode requires "at least one candidate survives *and* the initial candidate batch is dispatched"; no initial candidate batch was ever dispatched (see the mandatory-verification row below), so related-acquittal mode's precondition is also false, and correspondingly neither dropped candidate (`zsh/source-before-compinit-still-errors`, `zsh/fpath-before-compinit-ordering`) was related to the survivor by file/claim anyway (different sentence, different file region, different mechanism) — so no re-open occurred. |
| Observations | **Fired once.** | The fenced-code-block language-tag inconsistency (§3c) — an accurate fact that fails gate 1 (meaningful impact) and so routes to Observations per the rubric's Uncertainty routing / Observations sections, rendered in the payload's `## Observations` section and validated by `validate_review.py`'s `check_observation`. |
| Fix-sufficiency check on any concurrency/invariant candidate | **Did not apply.** | No candidate's `kind` was `concurrency` or `invariant`; `verifier-concurrency.md` was read proactively (see §5) but never applied to any candidate — this diff has no cross-path shared-state rule at stake (a single-shell zsh completion script has no concurrent actors in the sense that reference defines). |
| Follow-up verifier round | **Did not apply.** | No initial batch was ever dispatched, so there is no follow-up batch to run; the "one initial plus one follow-up" cap was never approached. |
| Deferral handling | **N/A — none present.** | Packet §6's prior-review record contains no explicit deferral language of the kind the skill flags ("we can fix this during the API review", "let's revisit the name later", "good enough for now"). The one candidate-adjacent deferral-like exchange in the prior-review record — `vegerot`'s thread-5 offer to *remove* the FAQ patch entirely and revisit in a separate issue — was explicitly **not** taken (`BurntSushi`'s non-review comment in packet §6 confirms: "I've left it in the FAQ and fixed up the wording…"), so it resolved to a concrete decision already reflected in the merged head, not an open deferral. I treated it as settled, not as an open question, consistent with the skill's carve-out that only *feedback already fixed in the reviewed head* is not to be "rediscovered and reported as still outstanding" (packet §5's mandatory note). |
| Retrospective mode | **Fired, throughout.** | Packet §1 states `merged: true`, posting identity `kamui` did not author the PR and has no prior state on it; the skill's Boundaries section ("retrospective review of a merged pull request is non-publishing by default") and step 1 ("A merged pull request is reviewable only when invoked as a retrospective or audit review; disable publication unless…") both govern this run. The rendered payload (§ payload file) carries the mandatory `**Mode:** Retrospective review of merged pull request; publication disabled.` line, and no `gh api`/write call was made anywhere in this session. |
| Early dispatch of the verifier batch (relative to the falsification pass) | **Did not apply — no batch was ever eligible for dispatch, early or otherwise.** | SKILL.md step 3: "Independently verify every surviving candidate proposed as `must-fix`, plus every candidate involving security or authorization, data loss or corruption, destructive migration, or an externally observable compatibility break." My one survivor is `[P3] [consider]`, `kind=maintainability` — not `must-fix`, and not security/authorization, data-loss/corruption, destructive-migration, or an externally observable compatibility break (I explicitly traced the compatibility-break risk in the risk-led-discovery pass below and settled it as *not present*, since the pre-fix behavior when sourced directly was **always** an unconditional crash, so nothing legitimate could have depended on it). Because no candidate met a mandatory-verification trigger, and zero-survivor mode's precondition ("zero candidates survive as findings") is false, "When at least one candidate qualifies, run one initial candidate batch" never triggers ("at least one candidate qualifies" is false here) — so §3's "Dispatch that batch as soon as…" early-dispatch clause has no batch to apply to. This is the correct outcome for this diff, not an omission: a documentation-only, single-shell, non-authorization, non-data, non-migration change with one `consider`-level survivor is exactly the shape the skill's calibration is designed to leave unverified. |

### Risk-led discovery (rubric §"Complete inspection")

Named promised behavior: "let users source ripgrep's zsh completions directly without the completion-system error, and fix the previously incomplete zsh FAQ setup instructions" (from the Issue-fit ledger's rows A–C and the diff's evident purpose).

Risk signals checked, with outcome:
- **External contracts / externally observable compatibility break:** Before this diff, sourcing the completion file directly (outside real completion-widget invocation) **always** called `_rg "$@"` unconditionally, which — per the issue report itself — **always** crashed with `_arguments:comparguments:327: can only be called from completion function` (or a closely related "not in a real completion context" error, confirmed by my own `zsh -f` reproduction, §5 item 2, which surfaces the same failure class under a slightly different message because `zsh -f` also skips `_arguments`'s own autoload). Since that path was *always* broken pre-fix, nothing legitimate could have depended on the old unconditional-invoke behavior; the new conditional behavior therefore introduces no compatibility break — it only narrows the set of inputs that still fail (down to "sourced with no completion system initialized at all," the one case covered by the two dropped candidates in §3b). This settles the one risk category actually in play for this diff; the rest of the standard risk list (authorization, secrets/crypto/logging, path traversal, migrations, concurrency, dependency/version skew, test hygiene) does not apply to a same-process, single-shell, documentation-and-completion-script change with no test-file changes.
- **Test and generated-artifact hygiene:** `crates/core/flags/complete/rg.zsh` is not a generated artifact (its own header states it is hand-maintained and checked against `rg --help` by `ci/test-complete`, not produced by a generator), so the rubric's "generated artifact whose content contradicts its source" hygiene check does not apply, and no test file was added or changed by this diff, so the rubric's "Changed tests" section (new/changed test functions) has no rows to apply to either — I record this as `not applicable`, not `unreviewed`, per the Complete inspection section's requirement to give every changed file and risk check an evidence-backed outcome.

---

## 8. History discipline

I read git history **only** within the pinned range (nothing "beyond the pinned head" `855bfa6cdae4f4fe8762f892fc4957635397083e`, which packet §8 condition 3 states is "the newest object reachable in your clone"). Exact history commands run:

- `git log --oneline -5 review-head` → showed `855bfa6` (the pinned head itself) and four ancestors (`7c2a7b0`, `79cbe89`, `bf63fe8`, `8bd5950`), all at or before the pinned head.
- `git log --oneline -5 master` → showed `79cbe89` (the pinned merge-base/base, the newest commit on the `master` branch in this clone) and four further ancestors (`bf63fe8`, `8bd5950`, `6e0539a`, `4649aa9`).
- The `history` section embedded in `scripts/review_context.py`'s output (run once, §5), which itself runs bounded `git log` calls per changed file and returned six single-line entries, the newest being `e0a8567` (2023-12-11) for `crates/core/flags/complete/rg.zsh` — all well before the pinned head/merge-base, none of them past it.

No `git fetch`, `git pull`, or any network-touching git command was run (none is possible — the clone is offline per packet §8 condition 1). No commit newer than `855bfa6cd` was read, referenced, or exists in this clone, consistent with the packet's truncation guarantee.

---

## 9. Sandbox disclosure

- All substantive reads and all execution stayed inside: the clone (`/tmp/qual137/runs/n-bea6be14-seed2-att-24`), the skill snapshot (`/tmp/qual137/snapshots/bea6be14/skills/code-review-publish/`), the packet directory (`/tmp/qual137/packets/n/`), and my own work/report/payload/timing paths under `/tmp/qual137/work/n-bea6be14-seed2-att-24/` and `/tmp/qual137/reports/n/n-bea6be14-seed2-att-24-*`.
- **One incidental directory listing outside that list:** early in the run I executed `ls -la /tmp/qual137/reports/n/` to confirm my own work/report directories existed before writing into them. That directory also holds sibling replicates' files from other cells (`n-867cf3ff-seed1-att-22-*`, `n-867cf3ff-seed2-att-23-*`, `n-bea6be14-seed1-att-21-*`), whose **filenames** were incidentally visible in that listing's output. I did not open, read, or otherwise inspect the **contents** of any of those files at any point. Disclosing this per rule 7 ("Report any other path you read") even though only filenames, not content, were exposed.
- **One instructed exception:** the dispatch itself directs running `python3 /tmp/qual137/mark_event.py /tmp/qual137/reports/n/n-bea6be14-seed2-att-24-timing.json payload_validated_at` for the timing sidecar. `/tmp/qual137/mark_event.py` sits outside the sandbox paths rule 7 enumerates (clone/skill-snapshot/packet-dir/own-report-paths), but the dispatch names this exact command explicitly as a required step, so I ran it as instructed and disclose it here rather than treating it as a silent boundary crossing.
- No other path outside the sandbox was read.

---

## 10. Notes — judgment calls on ambiguities in the skill's contract

1. **No re-review despite a rich prior-review record.** The packet's §6 contains ten review submissions and ten thread comments from `BurntSushi`, `vegerot`, and `okdana` — but none from the posting identity `kamui`. SKILL.md step 1's re-review trigger is keyed specifically to "any prior review, reply, or trailer-bearing comment **from the posting identity**." I read this literally: `kamui` posted nothing before, so this is an ordinary first review, and `references/re-review.md` is out of scope entirely (not even read for its duplicate-review shortcut). I did, however, treat the *existing* review record as evidence for the rubric's gate 6 (intentionality) and for the deferral-handling mechanism (§7 above) — the rubric requires reading prior review threads for falsification purposes ("Search current review threads and CI output for the same issue") regardless of whose identity is reviewing, and I applied that.
2. **No raw forge JSON in this offline cell.** The skill's step 1 and the `context_fingerprint.py --packet` flag both assume a `forge_packet.py normalize` output (`packet.json`) built from live `gh api graphql` pages. This cell is offline and supplies a pre-normalized `packet.md` instead. I treated the dispatch's explicit instruction — "If your skill's phase 1 asks you to resolve the target from the forge, that phase is satisfied by this packet" — as authorizing me to hand-build the `context_fingerprint.py` direct-JSON input (the script's own documented fallback path: "On a forge without that packet, supply `pr`, `issues`, `specs`, and `guidance` directly from the exact reviewed inputs") from the packet's verbatim text, rather than fabricating a fake `packet.json` with a `forge-packet/1` schema tag I never actually produced via `forge_packet.py normalize`. I judged the latter would misrepresent provenance (claiming a normalize step that never ran), while the former uses the script exactly as it documents itself for a forge/scenario where no such packet exists.
3. **Grammar-only finding admitted under gate 4's "authoritative instruction" reading.** Gate 4 (Proven consequence) literally enumerates two categories — "behavior" (code) and "an authoritative instruction or maintainability contract" (drift/contradiction). A prose grammar defect in FAQ.md doesn't map perfectly onto either as literally worded (it's not a code-vs-comment contradiction). I read FAQ.md's purpose — literally instructing users how to set up completions — as falling under "authoritative instruction" broadly construed, with the "exact contradiction or drift" being the missing-subject construction itself (demonstrated verbatim) and the "concrete reader consequence" being the reparse/ambiguity cost. I flagged this reasoning explicitly here rather than resolving it silently, since a different reviewer could reasonably read gate 4 more narrowly and drop this finding instead. I did not route it to `Ambiguities` in the payload because the rubric's `Ambiguities` route is for *rubric or contract terms* with two supportable *readings that change which reading governs the run*, not for a single, self-contained finding-admission judgment call of this kind — but I disclose the judgment call here per instruction 10 of the dispatch.
4. **Two zsh-precondition candidates dropped on gates 7/8 rather than kept as `not-verifiable`/questions.** Both `zsh/source-before-compinit-still-errors` and `zsh/fpath-before-compinit-ordering` are *not* statically unresolvable (I settled them completely by direct zsh execution), so the question route does not apply to them — they are resolved facts, just facts I judged not to clear the "worth the author's time" / "proportionate rigor" bar given the FAQ's own established level of rigor elsewhere in the same section. A reviewer weighing the ecosystem-convention argument less heavily than I did could reasonably promote one or both to a `consider` finding instead; I've laid out the full evidence and reasoning in §3b so that judgment call is auditable rather than hidden.
5. **`ci/test-complete` treated as "execution unavailable" for the full script, not as a coverage gap.** The rubric's Changed-tests section governs test functions the diff *adds or substantively changes*; this diff touches neither a test file nor a test function (the completion script itself is production code with an *external* test, and that test file is unchanged). I therefore did not treat the inability to run the full `ci/test-complete` (blocked by the no-`cargo build` rule) as a Changed-tests-section coverage gap, but I still exercised and reported the one part of it I *could* run without a binary (`get_comp_args`'s sourcing mechanism, §5 items 5–6), and named the full-script gap explicitly in the summary's `Coverage` line for transparency, without downgrading the derived status to `Incomplete` over it, since neither the rubric's Changed-tests section nor its Coverage section make this file's untested-by-me-in-full status a coverage-completeness blocker (the diff's *own* content — both files — was fully read and is `reviewed`, which is what `Coverage: complete` actually requires).
