# Research report — `n-867cf3ff-seed1-att-22`

## 1. Metadata

| | |
| --- | --- |
| Target | `BurntSushi/ripgrep#2957` ("feat(completion): support sourcing zsh completion dynamically") |
| Cell | `n-867cf3ff-seed1`, attempt `att-22` |
| Skill snapshot | `/tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/` |
| `workflow` identifier (validator) | `v5b-1` (from `scripts/validate_review.py`'s `WORKFLOW` constant, confirmed by a clean `validate_review.py` exit on the emitted trailer) |
| Model I ran on | `claude-sonnet-5` |
| Sub-agents spawned | **none** — see §7 for why the verification trigger never fired |
| Model each sub-agent ran on | n/a (none spawned) |
| Verification trigger fired? | **No.** Zero candidates survived primary falsification as findings, and none of the changed behavior touches "a concurrency or failover path, a data-integrity surface, or a security or authorization boundary" (SKILL.md, zero-survivor-mode sentence, quoted in full in §7), so the zero-survivor clean-verdict batch is not required either. No candidate was ever a `must-fix`, so the mandatory-verification sentence ("Independently verify every surviving candidate proposed as `must-fix`, plus every candidate involving security or authorization, data loss or corruption, destructive migration, or an externally observable compatibility break") also never applies. |
| Candidates raised | 5 (see §3 ledger) |
| Candidates surviving my own falsification | 0 |
| Verifier verdicts | none (no verifier dispatched) |
| Findings for publication | none |
| Questions | none |
| Observations | none published (see the Ambiguities judgment call in §10 — a candidate that could plausibly have gone to Observations was instead dropped under the narrower reading I applied) |
| Coverage | Complete — both changed files reviewed, all applicable risk checks run with evidence-backed outcomes, no incomplete fetch or verification |
| Derived status | `Approved (advisory)` — `COMMENT` event (posting identity `kamui` is a third party on a merged/retrospective target; publication disabled regardless) |
| My own token usage | Not reported by this harness to me; I have no figure to give. |

Payload file (the review exactly as it would be posted): [`n-867cf3ff-seed1-att-22-payload.md`](./n-867cf3ff-seed1-att-22-payload.md).

## 2. Findings that survive

None. Zero findings were admitted; the rubric explicitly treats this as "a valid and preferable result when none do."

## 3. Complete private disposition ledger

Every candidate I raised during falsification, in the compact ledger form the rubric specifies for non-survivors (`claim`, `kind`, `disposition`, one-line falsification reason, one decisive evidence pointer). None of these reached `survivor` status, so none carry the full survivor record shape.

| id | kind | claim | disposition | decisive evidence | falsification reason | verifier ruling? |
| --- | --- | --- | --- | --- | --- | --- |
| `cand-1` `rgzsh/pre-compinit-source-still-errors` | bug | Sourcing the generated completion script before `compinit`/`compdef` is available still raises a raw shell error, contradicting the PR's "after this commit, it should work as expected." | dropped — pre-existing, gate 2 (introduced-here) fails | `crates/core/flags/complete/rg.zsh:441` (head conditional); scratch tests `test_base_no_compinit.zsh` and `test_no_compinit.zsh` both produced the identical `_rg:341: command not found: _arguments` failure at base and at head | The change does not "materially worsen" this path: base and head fail identically without `compinit` loaded (2×2 matrix in §5 proves this). Rubric gate 2: "Do not report a pre-existing Code problem unless the change materially worsens it." | No — never became a survivor, and gate-2 (pre-existing) failures are not a mandatory-verification trigger (not `must-fix`, not security/data-loss/destructive-migration/compat-break as a *surviving* claim — it never survived to be evaluated against that list). |
| `cand-2` `faq/dynamic-source-missing-compinit-prereq-doc` | requirement | FAQ.md's new "load and generate completions at the same time" snippet doesn't mention that `compinit` must already be loaded for it to work. | dropped — fails gates 7 (worth author's time) / 8 (proportionate rigor) | `FAQ.md:126-138`; issue #2956's own example lists `fzf`/`gh`/`fd` using the identical `source <(...)` idiom without stating a `compinit` prerequisite either | This is universal, ecosystem-wide zsh convention (every one of the issue's own cited tools has the same implicit prerequisite), not a repo-specific gap; no repository rule requires stating it (packet §7 confirms no `AGENTS.md`/`CLAUDE.md`/`CONTRIBUTING.md` exist at the merge-base for this path). | No — dropped on gates 7/8, not a survivor, not in the mandatory-verification list. |
| `cand-3` `faq/zsh-heading-style-inconsistent` | maintainability | "For **zsh**, the recommended approach is:" breaks the parallel "For **X**:" heading pattern used by bash/fish. | dropped — gate 1 (not meaningful impact) | `FAQ.md:100,108,116,141` (bash/fish/zsh/PowerShell headings) | The PowerShell heading ("For **PowerShell**, create the completions:") already deviates from the strict "For **X**:" pattern at the merge-base, so this is not even a new inconsistency this diff introduces, and it has no reader-facing consequence. | No — dropped on gate 1, not a survivor. |
| `cand-4` `faq/caveat-sentence-grammar` | maintainability | The new caveat sentence ("Note though that while this approach is easier to setup, is generally slower than the previous method, and will add more time to loading your shell prompt.") drops the subject before its second and third predicates and uses "setup" as a verb, reading as an unclear run-on. | dropped — gate 1 (not meaningful impact); see §10 Ambiguities note for why this was not routed to Observations | `FAQ.md:138` | The sentence, while grammatically awkward, remains comprehensible to a fluent reader in context; this is a cosmetic prose nit, not a correctness/maintainability/security/performance defect at the bar gate 1 sets. | No — dropped on gate 1, not a survivor. Would have been Observation-eligible under the broader reading of the Observations rule; see §10. |
| `cand-5` `rgzsh/fpath-autoload-path-regression` | bug (compatibility) | The new trailing conditional could break the traditional `fpath`-based autoload usage documented earlier in the same FAQ section (infinite recursion, double registration, or the autoload never resolving to the real `_rg` body). | refuted by direct empirical test | `crates/core/flags/complete/rg.zsh:441-446`; scratch test `test_autoload_fpath.zsh` | Simulated the exact `fpath`/`compinit`/`autoload -Uz _rg` sequence: the autoload correctly detects `$funcstack[1] == _rg` during self-execution, recurses into the now-defined `_rg`, and completes with exit 0, `_rg` fully defined, full option-spec dump printed, no recursion error. | No — refuted directly by reproduction; this candidate never reached survivor status, so it never entered the mandatory-verification list (it would have qualified as "an externally observable compatibility break" candidate *if it had survived*, but it did not survive primary falsification). |

No candidate survived primary falsification, so §"Related-acquittal mode" (which only fires alongside a surviving candidate) never applies, and the zero-survivor clean-verdict trigger's risk-surface condition (concurrency/failover, data-integrity, security/authorization) is not met by this diff — see §7 for the exact quoted condition and why it doesn't fire here.

## 4. Every sub-agent dispatch

**None.** No verifier or clean-verdict batch was dispatched, because:

1. No candidate survived primary falsification as a finding (§3) — there is nothing eligible for the mandatory-verification list (`must-fix`, security/authorization, data loss/corruption, destructive migration, externally observable compatibility break), since every candidate that touched one of those categories (`cand-1`, `cand-5`) was refuted/dropped by decisive evidence before it could become a survivor.
2. Zero-survivor mode's clean-verdict batch requires, in addition to zero survivors, that "the changed behavior touches a concurrency or failover path, a data-integrity surface, or a security or authorization boundary" (`SKILL.md`, quoted verbatim in §7). This change is a zsh shell-completion script and a FAQ prose edit; it touches none of those three surfaces. So the clean-verdict batch's trigger condition is unmet, and no batch runs.

Per the task's own instruction that sub-agent dispatch is used "for a verifier batch, a clean-verdict batch, anything the skill's own references specify" — since the skill's own references specify neither is required here, none was invoked. There is no prompt or verbatim report to record in this section.

## 5. Everything consulted beyond the diff

### Scripted/tool inputs

- `python3 /tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/scripts/review_context.py --merge-base 79cbe89deb1151e703f4d91b19af9cdcc128b765 --head 855bfa6cdae4f4fe8762f892fc4957635397083e` (run from inside the clone `/tmp/qual137/runs/n-867cf3ff-seed1-att-22`, `master` branch checked out at nothing/`review-head` checked out) — exit 0, 298 lines of Markdown output written to `/tmp/qual137/work/n-867cf3ff-seed1-att-22/review_context.md`, read in full. This supplied `manifest`, the complete function-context `diff`, `ranges`, and `history` sections used for the whole review; the diff was read exactly once from this output as the rubric's "Review once" step requires.
- `python3 /tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/scripts/context_fingerprint.py /tmp/qual137/work/n-867cf3ff-seed1-att-22/context_input.json` — exit 0, printed the digest `fea14e64c218222905fc4b1fc7bde1d1907a2826ffb04195d9add739b148f6a1` (see §6 for the exact input JSON).
- `python3 /tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/scripts/validate_review.py /tmp/qual137/work/n-867cf3ff-seed1-att-22/payload.json` — exit 0, no violations.
- `python3 /tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/scripts/validate_review.py --render /tmp/qual137/work/n-867cf3ff-seed1-att-22/payload.json` — exit 0, empty output (correct: zero findings/questions means zero rendered fragments).
- `python3 /tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/scripts/validate_review.py --emit-batch /tmp/qual137/work/n-867cf3ff-seed1-att-22/payload.json` — exit 0, printed the one-call batch JSON (`commit_id`, `event=COMMENT`, `body`, empty `comments`), reproduced verbatim in this session's transcript.
- I did **not** run either script's `--self-test` mode, per the task's explicit instruction ("Compute the `context` digest once... do not run the skill's self-tests inside this cell").

### Repo reads and greps (all inside the pinned clone `/tmp/qual137/runs/n-867cf3ff-seed1-att-22`, offline, no `git checkout`/`switch`/`reset`/`stash` run)

- `git status`, `git log --oneline -5 review-head`, `git log --oneline -5 master`, `git branch -a` — orientation only, no mutation.
- `git rev-parse review-head`, `git rev-parse master` — confirmed the pinned SHAs matched the packet byte-for-byte.
- `git show review-head:crates/core/flags/complete/rg.zsh | sed -n '1,40p'` — read the `#compdef rg` header and the start of the `_rg()` function, not covered by the function-context diff.
- `git show review-head:crates/core/flags/complete/rg.zsh | sed -n '400,450p'` — read the region around the new conditional in wider context than the diff's own function-context window.
- `sed -n '85,150p' FAQ.md` (head) — read the full "shell auto-completion" FAQ section in context, beyond the diff's own hunk.
- `git log -p --follow -1 7c2a7b0 -- FAQ.md` — read the first commit's FAQ.md diff in isolation, to see what BurntSushi's follow-up "improve FAQ text" commit changed relative to the original PR commit (both commits are on the pinned head, so this is not "history beyond the pinned head" — see §8).
- `grep -n "_RG_COMPLETE_LIST_ARGS\|_arguments\b\|^_rg()\|return ret\|funcstack" crates/core/flags/complete/rg.zsh` — one batched, case-sensitive, single-file search (the only zsh completion file in the diff) to locate every place the new conditional's preconditions (`_RG_COMPLETE_LIST_ARGS`, `_arguments`, `funcstack`) are referenced.
- `sed -n '335,360p' crates/core/flags/complete/rg.zsh` — read the `_RG_COMPLETE_LIST_ARGS` early-return branch inside `_rg()`, to understand why `ci/test-complete` never exercises the real `_arguments` call.
- `find . -iname "*test-complete*" -o -iname "*complete*" | grep -i ci` and `cat ci/test-complete` — located and read the repository's own completion-consistency CI script in full (95 lines) to confirm it still exercises the changed file correctly and does not depend on the removed unconditional `_rg "$@"` line.
- `grep -n "For \*\*zsh\*\*\|For \*\*bash\*\*\|For \*\*fish\*\*\|For \*\*PowerShell\*\*" FAQ.md` and `grep -n "Note though that" FAQ.md` — located exact line numbers for `cand-3`/`cand-4`'s evidence pointers. Single-file, case-sensitive.
- `grep -n "Don't run the completion\|funcstack\[1\]\|compdef _rg rg" crates/core/flags/complete/rg.zsh` and `git show <merge-base>:crates/core/flags/complete/rg.zsh | grep -n '_rg "\$@"'` — pinned the exact head (437-446) and base (437) line numbers cited in §3's ledger.
- `sed -n '434,447p' crates/core/flags/complete/rg.zsh | cat -n` — confirmed the exact head anchor range for the changed conditional block.
- `grep -n "generate=\[generate man page" crates/core/flags/complete/rg.zsh` — located the pre-existing, unchanged `--generate=` argspec (line 113) that satisfies the PR's test-plan step 2 (tab-completing the flag's own value), to confirm it was untouched by this diff and therefore out of scope as a candidate.
- `ls crates/core/flags/complete/` — confirmed the sibling bash/fish/PowerShell completion generators (`bash.rs`, `fish.rs`, `powershell.rs`) are Rust-generated, not static templates like `rg.zsh`, so the synchronization-drift procedure's peer-artifact search does not apply here (no shared rule or vocabulary crosses these files).
- `git show <merge-base>:crates/core/flags/complete/rg.zsh > rg_base.zsh` — extracted the full base-branch file into the work directory for use as a scratch-test fixture (execution only, never written back into the clone).
- `git show <base>:docs/agents/issue-tracker.md` — confirmed absent (`fatal: path ... does not exist`), so SKILL.md step 1's "read the base-branch `docs/agents/issue-tracker.md` when present" had nothing to read.

### Focused execution (zsh scratch scripts, per the packet's execution allowance — offline, under my own work directory, never inside the clone, well under the 5-minute-per-command budget)

All scripts and their outputs are reproduced in §7's mechanism checklist and in the transcript; summarized here with exit status:

1. `test_no_compinit.zsh` — sourced the **head** `rg.zsh` with no completion system loaded. Exit 1 (from the sourced script's own internal error, the wrapper script itself completed); output: `_rg:341: command not found: _arguments`. Duration: sub-second.
2. `test_with_compinit.zsh` — ran `compinit` first, then sourced the **head** `rg.zsh`. Exit 0; output: "source completed without error", `funcstack` empty afterward (confirms the `compdef` branch ran, not the `_rg "$@"` branch). Duration: a few seconds (compinit dump generation).
3. `test_base_with_compinit.zsh` — ran `compinit` first, then sourced the **base** (`merge-base`) `rg.zsh`. Exit 0 (wrapper), but the sourced content itself printed `_arguments:comparguments:327: can only be called from completion function` — reproducing the issue's exact reported error verbatim. Duration: a few seconds.
4. `test_base_no_compinit.zsh` — sourced the **base** `rg.zsh` with no completion system loaded. Exit 0 (wrapper); output: `_rg:341: command not found: _arguments` — identical failure mode to test 1, completing the 2×2 matrix that proves `cand-1`/`cand-5`'s "no compinit yet" failure is pre-existing and unchanged by this diff, not a regression it introduces or a regression it leaves unfixed relative to base.
5. `test_autoload_fpath.zsh` — installed the head `rg.zsh` as `_rg` under a scratch `fpath` directory, ran `compinit`, `autoload -Uz _rg`, then invoked `_RG_COMPLETE_LIST_ARGS=1 _rg` to simulate the traditional fpath/autoload usage path documented earlier in the same FAQ section. Exit 0; full option-spec dump printed (confirming the real `_rg` function body executed to completion); `$+functions[_rg]` reported `1` afterward (confirms `_rg` is now the properly-defined function, not left as an autoload stub or recursed indefinitely).

No `cargo build`/`cargo test` was attempted (explicitly disallowed by the packet). No network call of any kind was made.

## 6. The `context` digest and its inputs

Digest: **`fea14e64c218222905fc4b1fc7bde1d1907a2826ffb04195d9add739b148f6a1`**

Computed once via `context_fingerprint.py` from this exact JSON (saved at `/tmp/qual137/work/n-867cf3ff-seed1-att-22/context_input.json`):

```json
{
  "pr": {
    "title": "feat(completion): support sourcing zsh completion dynamically",
    "body": "Summary:\nPreviously, you needed to save the completion script to a file and then\nsource it.  Now, you can dynamically source completions in zsh by\nrunning\n\n```zsh\n$ source <(rg --generate complete-zsh)\n```\n\nTest plan:\n1. Run `source <(rg --generate complete-zsh)`\n2. Run `rg --generate=complete-zs<TAB>`\n\nBefore this commit, you would get an error after step 1.\nAfter this commit, it should work as expected.\n\nCloses #2956"
  },
  "issues": [
    {
      "coordinate": "BurntSushi/ripgrep#2956",
      "title": "Can't source zsh completions directly",
      "body": "<verbatim issue body, byte-checked against the packet with `od -c` for the tab/space indentation inside its zshrc code block>",
      "comments": [],
      "comments_available": true
    }
  ],
  "specs": [],
  "guidance": []
}
```

Inputs, explicitly:

- **title:** `feat(completion): support sourcing zsh completion dynamically` (packet §1).
- **body:** the PR body verbatim, from packet §3.
- **issue coordinates:** `BurntSushi/ripgrep#2956` only — the sole closing reference in the PR body (packet §1, §4), resolved per SKILL.md's issue-resolution order, rung 1 ("closing references in the pull-request body").
- **comments_available:** `true`, with an empty comment list — packet §4 states "0 total; `comments_available: true`", so I passed `"comments": []` with `"comments_available": true` rather than omitting comments (the script's own rule: `comments_available: false` is only used when comments genuinely could not be fetched, which is not this case).
- **guidance:** empty list — packet §7's guidance table shows no `AGENTS.md`, `CLAUDE.md`, or `CONTEXT.md` present at the merge-base for any changed path, so the digest's `guidance` array is `[]`.
- **specs:** empty — no user-supplied spec was given for this run.

I double-checked the issue body's exact whitespace (tabs vs. spaces inside the embedded zshrc snippet) against the packet's raw bytes with `od -c` before hashing, since that whitespace is inside the hashed `body` string and any transcription error there would silently change the digest.

## 7. Mechanism checklist

| Mechanism | Fired? | Where demonstrated |
| --- | --- | --- |
| Question channel | Did not fire | No candidate met the rubric's static-unresolvability bar ("no static evidence could settle the fact"); every candidate I raised was resolvable from the diff, the base-branch file, the issue/PR text, and direct zsh execution. No question item appears in the payload. |
| Clean-verdict or related-acquittal verification | Did not fire | Zero-survivor mode's trigger sentence, quoted verbatim from `SKILL.md`: *"when zero candidates survive as findings ... and the changed behavior touches a concurrency or failover path, a data-integrity surface, or a security or authorization boundary, run one clean-verdict batch instead of a candidate batch."* Zero candidates survived (§3), but this diff (a zsh completion script's sourcing/registration logic and an FAQ prose edit) touches none of the three listed surfaces, so the batch was not run. Related-acquittal mode never applies either, since it requires "at least one candidate survives," which did not happen here. |
| Observations | Did not fire (zero published) | `cand-4` was the only candidate that plausibly qualified for the Observations channel (failed on gate 1, "meaningful impact," with an accurate fact and a decisive evidence pointer). I applied the narrower reading of the Observations-routing sentence (see §10) and dropped it instead of publishing it. This is documented as a judgment call in the summary's `Ambiguities` section and in §10 below, not left silent. |
| Fix-sufficiency check on any concurrency/invariant candidate | Did not fire | No candidate was ever `kind=concurrency` or `kind=invariant`; this diff has no concurrent actors or state-consistency rule at stake (it is single-threaded shell-script control flow). |
| Follow-up verifier round | Did not fire | No initial batch was ever dispatched (§4), so there is nothing to follow up. |
| Deferral handling | N/A — none present | The prior review record (packet §6) contains no explicit deferral language ("we can fix this during API review," "revisit later," etc.) on any thread; every one of the three review threads was resolved in-line during the original review round, with the FAQ-inclusion debate (thread 1, comments 1-5) and the zsh-conditional debate (thread 2, comments 6-8) both reaching an explicit resolution captured in the reviewed head, and the `fpath` FAQ pre-existing-issue thread (thread 3, comments 9-10) resolved by vegerot choosing the alternative fix actually shipped. I re-read all three threads against the reviewed head (per the packet's "mandatory note") and confirmed none is a live, unresolved deferral. |
| Retrospective mode | Fired | `merged=true` (packet §1); the payload's summary carries the mandatory `**Mode:** Retrospective review of merged pull request; publication disabled.` line, and step 5's "re-fetch before write" / step 6's "publish" instructions were followed through to the render-and-stop point per the packet's binding run condition 4. |
| Early dispatch of the verifier batch | Did not fire — no batch was ever eligible to dispatch early or otherwise (§4) | n/a |

## 8. History discipline

I did **not** read any history beyond the pinned head. The exact history-touching commands I ran, all confined to commits reachable from `review-head`/`master` as pinned:

- `git log --oneline -5 review-head` and `git log --oneline -5 master` — both showed only commits at or before the pinned head/merge-base (`855bfa6`, `7c2a7b0`, `79cbe89`, `bf63fe8`, `8bd5950`, ...), consistent with the packet's statement that history is truncated at `855bfa6cd`.
- `git log -p --follow -1 7c2a7b018e2a3fe65be19f8d3f0bd1028e8421b1 -- FAQ.md` — inspected the **first** of the two commits already on the pinned head (`7c2a7b0`, listed in packet §5 row 1) in isolation, to separate what the original PR commit changed in `FAQ.md` from what BurntSushi's second, already-merged commit (`855bfa6`, packet §5 row 2) changed on top of it. Both commits are within the pinned head range, not beyond it.
- `review_context.py`'s own `history` section (in its Markdown output) reported the last commit that touched each changed path **before** the merge-base (e.g. `FAQ.md: a2907db 2023-11-21 ...`, `crates/core/flags/complete/rg.zsh: e0a8567 2023-12-11 ...`). This is the tool's own bounded, pre-merge-base history feed described in SKILL.md step 2 ("`history` provide[s] ... the coordinates ... the synchronization-drift check use[s]"), not a manual history read by me beyond the pinned head.

No `git fetch`, `git pull`, `git log` past the pinned head, or any other history command touching anything newer than `855bfa6cd` was run.

## 9. Sandbox disclosure

No path outside the sandbox was read. Every read and write stayed within:

- the clone `/tmp/qual137/runs/n-867cf3ff-seed1-att-22` (read-only; no mutating git command run),
- the skill snapshot `/tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/`,
- the packet directory `/tmp/qual137/packets/n/`,
- my own work directory `/tmp/qual137/work/n-867cf3ff-seed1-att-22/`, and
- my own report/payload/timing paths under `/tmp/qual137/reports/n/`.

I did not read any other run's clone, report, or payload, and did not touch any path under a different attempt id or a different target letter.

## 10. Notes — judgment calls on skill-contract ambiguities

1. **Observations routing for gate-1 (not-meaningful) failures vs. gate-4 (no-proven-consequence) failures only.** The rubric's Observations paragraph opens with "Route an accurate fact to `Observations` when it fails finding admission specifically on meaningful or proven consequence," which reads naturally as covering *either* a gate-1 ("meaningful impact") or a gate-4 ("proven consequence") failure. But the same paragraph later gives gate-4-specific routing language only ("When a candidate fails only gate 4, its ledger row names which reason applies: `observation (consequence absent)`... or `dropped (consequence unproven)`"), and separately cautions, "Do not create an observation merely to preserve a dropped candidate. The fact itself must stand..." I treated this as a genuine two-reading ambiguity and applied the narrower, gate-4-only reading as the safer one: I dropped `cand-4` (the FAQ.md:138 grammar nit, which fails gate 1, not gate 4) instead of publishing it as an Observation. I recorded both readings and my choice in the payload's `Ambiguities` section (visible to the PR audience) as the contract requires when a rubric term has two genuinely supportable readings. This did not change the derived status either way (both readings still yield `Approved`), but it did change what would have been in the payload, so I judged it worth disclosing rather than silently picking one reading.
2. **No re-review reference needed.** The packet states posting identity `kamui` "did NOT author the PR and has no prior comments or reviews on it," which SKILL.md step 2's trigger condition ("When step 1 found any prior review, reply, or trailer-bearing comment **from the posting identity**") does not meet — the prior review state that exists (packet §6) is entirely from `BurntSushi`, `vegerot`, and `okdana`, none of whom is the posting identity. I treated this as an ordinary first review and did not read `references/re-review.md`, consistent with the skill's own conditional ("On a first review, skip this step" — SKILL.md step 4).
3. **Zero-survivor clean-verdict trigger's risk-surface test.** I read "concurrency or failover path, a data-integrity surface, or a security or authorization boundary" narrowly and literally: a zsh completion script's control flow (which branch of an `if` runs at source time) and a documentation prose edit are neither concurrent, nor failover-related, nor data-integrity-bearing, nor a security/authorization boundary. I did not stretch "the completion function could theoretically be exploited to run arbitrary code if crafted maliciously" into a security-boundary argument, since nothing in this diff changes what code the file can execute or under what privilege — it only changes *when* the file's existing `_rg` function gets invoked/registered.
4. **Treating `ci/test-complete` and the argspec-completion mechanism as coverage checks, not candidates.** I initially treated "does this PR's change break `ci/test-complete`" and "does the flag-value tab-completion in the PR's test-plan step 2 still work" as things to *verify were clean*, not things to hunt for a defect in for their own sake, since neither file is in the diff. I recorded both as coverage/risk-check outcomes (§5) rather than manufacturing ledger candidates for unchanged files, per the rubric's complete-inspection guidance to use risk signals "to direct attention, not to create findings."
5. **`cand-1`/`cand-5` as two framings of one underlying fact, not a duplicate pair to silently merge.** `cand-1` treats "still errors before `compinit`" as a Code (bug) candidate under the introduced-here gate; `cand-2` treats the *documentation* angle of the same fact as a requirement candidate under the issue-fit gates. I kept them as separate ledger rows because they fail on different gates (gate 2 vs. gates 7/8) and would need different evidence to resurrect, even though they describe the same underlying zsh behavior — the verifier-merge instruction ("Merge duplicates around one stable id and one requested outcome") only applies to *surviving* candidates being prepared for publication, which neither of these are.
