# Research report — `n-867cf3ff-seed2-att-23`

## 1. Metadata

- **Target:** `BurntSushi/ripgrep#2957` — "feat(completion): support sourcing zsh completion dynamically" (cell `n`)
- **Cell:** `n-867cf3ff-seed2`, attempt `att-23`
- **Skill snapshot:** `/tmp/qual137/snapshots/867cf3ff/snapshot-path-omitted/`
- **`workflow` identifier the validator reports:** `v5b-1` (from `scripts/validate_review.py` source, `WORKFLOW = "v5b-1"`, line 99; also enforced at line 267-268)
- **Model:** I (the primary reviewer) ran on `claude-sonnet-5`. Every sub-agent I dispatch is instructed with `model: "sonnet"` explicitly, as required.
- **Verification trigger fired:** Yes — mandatory verification for a `must-fix` candidate. SKILL.md's exact sentence: *"Independently verify every surviving candidate proposed as `must-fix`, plus every candidate involving security or authorization, data loss or corruption, destructive migration, or an externally observable compatibility break."* Candidate `faq/zsh-source-snippet-prompt-prefix` (below) is proposed `must-fix`, so it fired. No candidate involved security/authorization/data-loss/destructive-migration/compat-break, and the zero-survivor and related-acquittal clean-verdict triggers did not fire (at least one candidate survived as a finding, and no dropped candidate's `kind` was `bug`/`concurrency`/`invariant`/`security` while also sharing the survivor's file/function/branch/lock — see ledger row `zsh/funcstack-compdef-guard` and `zsh/ci-test-complete-compat`, both dropped with kind=bug but in a *different* file (`crates/core/flags/complete/rg.zsh`) than the must-fix survivor's anchor/fix (`FAQ.md`), and not naming the same function/branch as the survivor's claim, so related-acquittal inclusion was not required).
- **Sub-agents spawned:** 1 — role: candidate-mode independent verifier for the single `must-fix` candidate. `subagent_type: general-purpose`, `model: "sonnet"`, `run_in_background: false`.
- **Candidates raised:** 6 (see full ledger in §3)
- **Candidates surviving primary falsification (eligible for verification/publication):** 3 — `faq/zsh-source-snippet-prompt-prefix` (must-fix, P2), `faq/zsh-source-missing-compinit-precondition` (consider, P3), `faq/zsh-note-grammar` (consider, P3)
- **Verifier verdicts:** `faq/zsh-source-snippet-prompt-prefix` → `confirmed` (see §4 for the verbatim report)
- **Findings for publication:** 3 total (1 must-fix P2, 2 consider P3) — full text in §2 and in the payload file `/tmp/qual137/reports/n/n-867cf3ff-seed2-att-23-payload.md`
- **Questions:** none — no candidate met the static-unresolvability bar
- **Observations:** 1 published (comment-accuracy nitpick in `rg.zsh`); 0 unpublished/capped
- **Coverage:** both changed files (`FAQ.md`, `crates/core/flags/complete/rg.zsh`) reviewed in full via the complete merge-base diff with `--function-context`; every risk-directed check applicable to a docs+shell-completion change was run (see §5); no fetch, patch, or verification failed or was incomplete
- **Derived status:** `Changes Requested (advisory)` — one unsettled `must-fix` finding (`faq/zsh-source-snippet-prompt-prefix`), `COMMENT` event (posting identity `kamui` is a third party; this is also a non-gating retrospective review with publication disabled)
- **Token usage:** the harness does not report my own token usage to me in this session; I have no figure to give.

## 2. Findings that survive, in full

### [P2] [must-fix] Fix the broken copy-paste `source` snippet in the zsh FAQ

- **Anchor:** `FAQ.md:135` (`RIGHT` side, head `855bfa6cdae4f4fe8762f892fc4957635397083e`)
- **Fix location:** same line, `FAQ.md:135` (omitted from the trailer as identical to anchor)
- **Claim:** The FAQ's new zsh "load and generate at the same time" snippet keeps a `$ ` shell-prompt prefix on the `source <(rg --generate complete-zsh)` line even though the surrounding prose instructs the reader to "add the following to your `$HOME/.zshrc` file" — i.e., to paste it as file content, not type it at a prompt.
- **Verification status and evidence:** `independent-confirmed`. My own falsification: (a) diff comparison shows this exact paragraph, including the erroneous prefix, was introduced/left in place by the maintainer's own final polish commit `855bfa6cd` (not carried over unexamined from an earlier round — see §3 row for full citation); (b) the file's own established convention, visible three lines above in the same commit (`FAQ.md:127-129`, the `fpath=($HOME/.zsh-complete $fpath)` block, also introduced "to add to your `.zshrc` file") and in every sibling shell section (bash `FAQ.md:100-106`, fish `FAQ.md:108-114`, PowerShell `FAQ.md:141-150`, none of which prefix file-content snippets with `$ `) proves the `$ ` is not intentional styling for this case; (c) I reproduced the failure empirically: pasting `$ source <(...)` literally into a scratch zsh script under `/tmp/qual137/work/n-867cf3ff-seed2-att-23/zsh_test2/fake_zshrc.zsh` and running it with `zsh -f` produced `fake_zshrc.zsh:2: command not found: $`, and the `source` command was never reached — the exact failure a reader following the FAQ literally would hit at every shell startup. The independent verifier reproduced this given only the claim, the diff citations, and permission to inspect the code and run its own checks — see §4 for its verbatim report, which confirmed the claim, the trigger, and the impact, and validated the proposed fix and priority/action without correction.
- **Trigger scenario:** A reader follows the FAQ's explicit instruction ("add the following to your `$HOME/.zshrc` file") and pastes the fenced block verbatim, including the leading `$ `.
- **Impact:** Every new interactive zsh shell prints `command not found: $` at startup, and the `source <(rg --generate complete-zsh)` command is never executed, so ripgrep's zsh completions are never actually loaded via the method the FAQ just added — defeating the FAQ's stated purpose for this exact snippet.
- **Change:** In `FAQ.md`, remove the leading `$ ` from the `source <(rg --generate complete-zsh)` line so the fenced block is valid, literal `.zshrc` content, consistent with the `fpath=(...)` block immediately above it.

### [P3] [consider] Document that `compinit` must already be loaded before the one-line `source` method works

- **Anchor:** `FAQ.md:131-136` (`RIGHT` side, head `855bfa6cdae4f4fe8762f892fc4957635397083e`)
- **Fix location:** same range (omitted — anchor is the fix)
- **Claim:** The new "load and generate at the same time" paragraph presents `source <(rg --generate complete-zsh)` as an alternative, equally-viable setup step, but does not state that it only works when zsh's completion system (`compinit`) has already run in the same shell; placing the line before `compinit` produces a different, equally opaque failure.
- **Verification status and evidence:** `primary-confirmed` (not independently verified — not proposed `must-fix`, and not security/data-loss/migration/compat-break, so mandatory verification did not apply; see rubric SKILL.md §3, "Independently verify every surviving candidate proposed as `must-fix`, plus…"). My own falsification used real `zsh`/`compinit`, not just static reading, because the claim is about runtime behavior: with `autoload -Uz compinit; compinit -u -d …` run first, then `source crates/core/flags/complete/rg.zsh` (a copy standing in for the generated output), the shell registered the completion cleanly (`$_comps[rg]` == `_rg`, exit 0). Without `compinit` run first, the identical `source` failed with `_rg:341: command not found: _arguments`, exit 1 — a distinct message from the pre-existing-at-merge-base error (`_arguments:comparguments:327: can only be called from completion function`, itself reproduced against the merge-base file for comparison) but an equally broken outcome. This whole paragraph is new in this diff (not pre-existing), so any completeness gap in it is introduced here.
- **Trigger scenario:** A `.zshrc` that places `source <(rg --generate complete-zsh)` before calling `compinit` (or never calls it) — plausible for a minimal or unusually ordered zsh configuration, though the issue's own example `.zshrc` (which calls the analogous `fzf`/`gh`/`fd` lines) implies `compinit` typically precedes such lines.
- **Impact:** The reader sees a confusing `command not found: _arguments` error and gets no working completions, with no hint in the FAQ that ordering relative to `compinit` matters.
- **Change:** Add a short caveat to the FAQ noting that this line must come after `compinit` has run in the same shell startup file.
- **Closing this without action is a correct response.**

### [P3] [consider] Fix the malformed sentence in the new zsh slowness caveat

- **Anchor:** `FAQ.md:138-139` (`RIGHT` side, head `855bfa6cdae4f4fe8762f892fc4957635397083e`)
- **Fix location:** same range (omitted — anchor is the fix)
- **Claim:** "Note though that while this approach is easier to setup, is generally slower than the previous method, and will add more time to loading your shell prompt." omits the subject ("it") after the first comma, so the sentence reads as a run-on with a dangling subordinate clause, and uses "setup" (a noun) where the verb "set up" is needed.
- **Verification status and evidence:** `primary-confirmed` (not independently verified — pure prose/grammar, not must-fix and not one of the mandatory-verification categories). Evidence: `FAQ.md:138-139` read directly; this exact wording was authored by the maintainer (`BurntSushi`) in commit `855bfa6cd` (the reviewed head's own second commit — `git show 855bfa6cd -- FAQ.md`), replacing an earlier, shorter inline comment from `vegerot`'s first commit that had no such grammar problem, so the defect is introduced in this diff, not carried over.
- **Trigger scenario:** Any reader parsing this sentence as a single grammatical unit.
- **Impact:** The sentence is harder to parse than necessary and reads as ungrammatical, though the intended meaning (the source method is slower) is still recoverable from context.
- **Change:** Rewrite as, e.g., "Note, though, that while this approach is easier to set up, it is generally slower than the previous method and will add more time to loading your shell prompt."
- **Closing this without action is a correct response.**

## Observations (rendered in the summary body)

- The new guard's leading comment, "Don't run the completion function when being sourced by itself," describes only the `else` branch's skip-execution behavior, not the `if` branch that does call `_rg "$@"` two lines later. Evidence: `crates/core/flags/complete/rg.zsh:439-443`.

## 3. Complete private disposition ledger

| id | kind | disposition | decisive evidence | falsification reason | verifier ruling? |
| --- | --- | --- | --- | --- | --- |
| `faq/zsh-source-snippet-prompt-prefix` | bug | **survivor** (must-fix, P2) | `FAQ.md:135` vs. `FAQ.md:127-129` (sibling "add to .zshrc" block, no prefix); empirical repro in `/tmp/qual137/work/n-867cf3ff-seed2-att-23/zsh_test2/fake_zshrc.zsh` → `command not found: $` | n/a (survivor) | Yes — mandatory (proposed must-fix); verdict `confirmed` (§4) |
| `faq/zsh-source-missing-compinit-precondition` | requirement | **survivor** (consider, P3) | `FAQ.md:131-136` (new paragraph, no precondition stated); empirical repro: `source` before `compinit` → `_rg:341: command not found: _arguments`, exit 1, vs. clean `compdef` registration when `compinit` runs first | n/a (survivor) | No — not proposed must-fix and not in a mandatory-verification category (SKILL.md §3); an ordinary `consider` survivor is sent to the verifier "only when proving or refuting its existing claim requires a cross-module trace or another difficult reconstruction" (rubric intake in SKILL.md line 78) — this claim was settled directly by my own runtime reproduction, no cross-module trace needed, so it was not sent |
| `faq/zsh-note-grammar` | maintainability | **survivor** (consider, P3) | `FAQ.md:138-139`; `git show 855bfa6cd -- FAQ.md` (authored in this diff's own second commit) | n/a (survivor) | No — same reasoning as above; a plain-text grammar read requires no cross-module trace |
| `zsh/comment-accuracy-observation` | maintainability | **observation** | `crates/core/flags/complete/rg.zsh:439-443` (comment vs. the `if` branch it precedes) | fails finding admission on gate 1 (meaningful impact) and gate 7 (worth author's time) — the comment is imprecise but the code it describes is correct and unaffected; routed as an accurate, non-actionable fact per rubric's Observations rule | No — observations are never sent to a verifier; the verifier ruled on candidates and, in related-acquittal mode, on `kind=bug/concurrency/invariant/security` rows only. This row's `kind=maintainability` places it outside both the mandatory-verification categories and the related-acquittal `kind` set (SKILL.md §3, "A row is related when its `kind` is `bug`, `concurrency`, `invariant`, or `security`…") |
| `zsh/funcstack-compdef-guard` | bug | **dropped** (acquitted) | `crates/core/flags/complete/rg.zsh:439-443`; empirical tests in `/tmp/qual137/work/n-867cf3ff-seed2-att-23/zsh_test2/` (Test A: real `autoload -Uz _rg` + call, no compdef stub → correctly runs `_rg "$@"`; Test B: same with a `compdef` stub present → still correctly runs `_rg "$@"` because `$funcstack[1]==_rg`); plus real-`compinit` Test 1 (source after compinit → clean `compdef _rg rg` registration, `$_comps[rg]==_rg`) | Claim was "the funcstack/compdef guard fails for at least one realistic invocation path (autoload, direct source with compdef, direct source without compdef)." All three realistic invocation paths were traced and reproduced and none fails; the guard behaves exactly as the review-thread discussion (okdana's suggested condition, packet §6 comment 7-8) intended. Dropped under rubric falsification step 1-2 (trigger does not reproduce) | No — dropped/acquitted, `kind=bug`, but its decisive evidence is in `crates/core/flags/complete/rg.zsh`, a different file from the must-fix survivor's anchor/fix (`FAQ.md`), and its claim does not name the same function, branch, state field, or lock as the survivor's claim (the survivor's claim is about a documentation snippet, not about the zsh guard), so related-acquittal mode's condition (a) or (b) is not met — SKILL.md §3 |
| `zsh/ci-test-complete-compat` | bug | **dropped** (acquitted) | `ci/test-complete:16` (`( _RG_COMPLETE_LIST_ARGS=1 source $1 )`, a subshell with no `compdef` defined); empirical Test 1 in `/tmp/qual137/work/n-867cf3ff-seed2-att-23/zsh_test/` (no-compdef source → `_rg "$@"` branch fires, matching pre-existing unconditional-call behavior) | Claim was "the new guard could change how `ci/test-complete` invokes the completion function and break CI." Traced: `ci/test-complete`'s subshell never defines `compdef`, so `(( ! $+functions[compdef] ))` is always true there, and the `_rg "$@"` branch fires exactly as the old unconditional call did. No behavior change for this caller. Dropped under rubric falsification step 3 (checked relevant caller/CI evidence; this is also directly corroborated by review thread comment 6-8 in the packet, where `vegerot` reports `ci/test-complete` was the reason the guard has an `_rg "$@"` fallback branch at all) | No — same reasoning as the row above; `kind=bug`, evidence in a different file from the survivor's anchor, no shared function/branch/lock with the survivor's claim |

Requirement ledger (private, from step 2 of the skill; issue `BurntSushi/ripgrep#2956`):

| requirement | disposition | evidence |
| --- | --- | --- |
| Sourcing the zsh completion output directly (`source <(rg --generate complete-zsh)`) must not error the way the issue reports (`_arguments:comparguments:327: can only be called from completion function`) | `met` (for the issue's own scenario — a `.zshrc` where `compinit` already ran, matching the issue's own example config) | `crates/core/flags/complete/rg.zsh:439-443`; empirical repro in `/tmp/qual137/work/n-867cf3ff-seed2-att-23/zsh_test2/` real-compinit Test 1 (clean registration, exit 0) vs. base-branch Test (same error text as the issue, reproduced against `git show 79cbe89…:crates/core/flags/complete/rg.zsh`) |
| Tab-completion of the flag's own value (`rg --generate=complete-zs<TAB>`) must keep working | `met` (unaffected — pre-existing capability in `_rg`'s option-value completion, not touched by this diff's changed lines) | diff shows only lines 434-441 of `rg.zsh` changed; the `--generate` value-completion logic lives elsewhere in the unchanged body of `_rg()` |
| `ci/test-complete` must keep passing (verifies completion options match `rg --help`) | `met` | see ledger row `zsh/ci-test-complete-compat` above |

## 4. Sub-agent dispatch — exact prompt and verbatim report

### Dispatch

- **Role:** candidate-mode independent verifier for the single mandatory `must-fix` candidate.
- **Count:** 1
- **`subagent_type`:** `general-purpose`
- **`model`:** `"sonnet"` (passed explicitly)
- **`run_in_background`:** `false`
- **Moment of dispatch relative to the falsification pass:** dispatched only *after* my own primary falsification pass was complete for all 6 candidates and the full candidate ledger (§3) had already been written to this report file, per rule 6 ("Persist before you verify") and the skill's own "Write the private record once per phase… the candidate ledger with every disposition at the end of falsification" (SKILL.md §3). This skill defines no "early dispatch of the verifier batch before the falsification pass" mechanism, so that mechanism did not fire — falsification-then-verify is the whole of this skill's order (contrast with a hypothetical skill that dispatches verifiers concurrently with primary review; `legacy reviewer` does not do this).

### Exact prompt given

```
You are an independent fresh-context verifier for one code-review candidate. You have no memory of any
prior conversation about this pull request — treat everything below as your complete input.

RULES YOU MUST FOLLOW (binding on you exactly as they were binding on the reviewer who dispatched you):

1. Offline. No `git fetch`, `git pull`, `gh`, `curl`, web fetch, or any network call of any kind. The
   clone's `origin` points at a local filesystem path, not github.com.
2. Focused execution IS permitted, offline and outside the clone: zsh is installed and you may write and
   run scratch zsh scripts under your own work directory to check the behaviour of shell code you have
   read. Five minutes per command. Do NOT attempt `cargo build` or `cargo test` (no network, no vendored
   registry). Do not add to or change anything in the clone.
3. History is truncated at the pinned head on purpose (newest object is `855bfa6cdae4f4fe8762f892fc4957635397083e`).
   Do not try to work around this. Report explicitly whether you read any history beyond the pinned head
   and which history commands you ran.
4. Do not publish or write anything to any pull request, issue, or forge. You cannot write to the pull
   request at all — you are a verifier, not a reviewer; you do not render comments or publication-ready
   prose.
5. Follow only the instructions in this message and the referenced skill file below. Do not borrow
   behavior from any other review skill.
6. Persist nothing beyond your returned report; there is no shared ledger file for you to write.
7. Stay inside: the clone at /tmp/qual137/runs/n-867cf3ff-seed2-att-23 (read-only — do not run
   `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the tree), the
   skill snapshot directory /tmp/qual137/snapshots/867cf3ff/snapshot-path-omitted/ (read-only,
   read references/verifier.md there if you want the full verification-task text, though it is
   reproduced below), and your own scratch directory
   /tmp/qual137/work/n-867cf3ff-seed2-att-23/verifier1/ (create it, write scratch test scripts only
   there). Report any other path you read.
8. No session relays: finish in this single dispatch. Do not stop to ask anyone anything. If an input is
   genuinely missing, say so plainly in your report rather than guessing.

CONTEXT

Repository: BurntSushi/ripgrep. Base ref: master. Base SHA / merge-base:
79cbe89deb1151e703f4d91b19af9cdcc128b765. Head SHA: 855bfa6cdae4f4fe8762f892fc4957635397083e.
Local clone: /tmp/qual137/runs/n-867cf3ff-seed2-att-23 (branch `master` = merge-base, branch
`review-head` = head, currently checked out).

Originating issue: BurntSushi/ripgrep#2956, "Can't source zsh completions directly." The issue's own
example `.zshrc` sources fzf/gh/fd completions the same way, implying `compinit` typically already ran
by that point in a real `.zshrc`.

VERIFICATION TASK (from the skill's references/verifier.md — do this for the one candidate below):

1. Read the cited anchor and actual fix site as bounded ranges at head and at the merge-base
   (`git show <merge-base>:<path>` with a line range), then only enough surrounding context to decide
   the claim.
2. Reproduce or trace the stated trigger through the current code.
3. Establish the observable impact and whether unchanged code prevents it.
4. For a Code candidate, confirm that the change introduced the behavior, or that it removed a guarantee
   an unchanged path relied on; state which applies and cite the base-branch guarantee and the
   head-branch code that no longer provides it.
5. Confirm that the issue, pull-request description, rules, history, or review record do not make it
   intentional.
6. Check whether another candidate requests the same underlying change (none other is supplied to you).

Return exactly one of:
- `confirmed`: decisive evidence establishes the trigger, qualifying impact, requested outcome, and the
  Code introduced-here condition.
- `refuted`: decisive evidence shows the claim is false, prevented, intentional, lacks a qualifying
  impact, or is pre-existing (already broken the same way at the merge-base under the same guarantees).

For the candidate, return the verdict, a concise independent justification, decisive code citations, and
any correction to trigger/impact/priority/action/anchor/fix/change. Do not return publication-ready
prose — you are fact-checking, not writing the review.

THE CANDIDATE

id: faq/zsh-source-snippet-prompt-prefix
kind: bug
priority: P2
action: must-fix
anchor: {type: line, path: FAQ.md, start_line: 135, end_line: 135, side: RIGHT}
fix: FAQ.md:135 (same as anchor)
title: Fix broken copy-paste `source` snippet in zsh FAQ
claim: The FAQ's new zsh "load and generate at the same time" snippet keeps a literal `$ ` shell-prompt
  prefix on the `source <(rg --generate complete-zsh)` line even though the surrounding prose instructs
  the reader to "add the following to your `$HOME/.zshrc` file" (i.e., paste it as file content, not
  type it at a prompt).
trigger: A reader copies the fenced snippet at FAQ.md:134-136 verbatim into `~/.zshrc`, following the
  literal instruction immediately above it.
impact: zsh reports `command not found: $` at shell startup and never executes the `source` command, so
  ripgrep's zsh completions are never loaded via this documented method.
change: In FAQ.md, remove the leading `$ ` from the line at FAQ.md:135 so the fenced block is valid,
  literal .zshrc content — consistent with the `fpath=($HOME/.zsh-complete $fpath)` block at
  FAQ.md:127-129, which carries the identical "add to your .zshrc file" instruction and correctly omits
  the prompt prefix.
raw code citations (read these yourself; do not trust this description):
  - FAQ.md:116-139 at head (`git show 855bfa6cdae4f4fe8762f892fc4957635397083e:FAQ.md | sed -n '116,139p'`)
  - FAQ.md:100-114 and FAQ.md:141-150 at head, the bash/fish/PowerShell sibling sections, for the
    file's own convention on when a fenced block gets a `$ ` prompt (one-time terminal command) versus
    when it does not (literal file content to paste)
  - FAQ.md at merge-base (`git show 79cbe89deb1151e703f4d91b19af9cdcc128b765:FAQ.md | sed -n '90,130p'`)
    to see this whole "for zsh" paragraph did not exist before this pull request at all
ranges (from the skill's review_context.py, so you can read them in one message):
  FAQ.md:94-100 @head
  FAQ.md:94-100 @merge-base
  FAQ.md:113-143 @head
  FAQ.md:113-126 @merge-base
requirement/rule citation: none cited — this is not being justified by a specific repository rule or
  issue acceptance criterion, only by the file's own established internal convention and the literal
  instruction text adjacent to it.

Do not search the rest of the pull request for unrelated findings. If an accurate, sub-threshold fact
surfaces incidentally, you may return at most one non-actionable "observation" aside with a decisive
evidence pointer and no "should"/"must" language — but only if it does not contradict the candidate
above; if it contradicts the candidate's premise instead, say so explicitly as part of your verdict
reasoning rather than as a separate aside.

Report your verdict, justification, citations, and any corrections now.
```

### Verbatim report returned

Returned by agent id `ab76a6c9ac1e63ce2` (`Agent` tool, `subagent_type: general-purpose`, `model: "sonnet"`, `run_in_background: false`); subagent token usage as reported by the harness: `subagent_tokens: 25632`, `tool_uses: 6`, `duration_ms: 73651`.

```
## Verdict: **confirmed**

### Scope disclosure
- No history read beyond the pinned head. History commands run: `git log --oneline <merge-base>..<head> -- FAQ.md` and `git diff <merge-base> <head> -- FAQ.md`, both bounded to the given merge-base/head SHAs.
- Files read: `FAQ.md` at head (855bfa6) and merge-base (79cbe89) via `git show <sha>:FAQ.md`, within the clone at `/tmp/qual137/runs/n-867cf3ff-seed2-att-23` (read-only, no mutating commands run).
- Scratch scripts written/run only under `/tmp/qual137/work/n-867cf3ff-seed2-att-23/verifier1/` (`test_zshrc.zsh`, `test2.zsh`), executed with `zsh -f`, each well under 5 minutes.

### Citations
- Head `FAQ.md:134-136` (`git show 855bfa6...:FAQ.md`, line numbers preserved from tool output):
```
134	```zsh
135	$ source <(rg --generate complete-zsh)
136	```
```
  preceded at lines 131-132 by the literal instruction: *"Or if you'd prefer to load and generate completions at the same time, you can add the following to your `$HOME/.zshrc` file:"*
- Immediately preceding sibling block, head `FAQ.md:127-129`, driven by the identical-phrasing instruction at 124-125 (*"And then add ... to your ... `$HOME/.zshrc` file:"*):
```
127	```zsh
128	fpath=($HOME/.zsh-complete $fpath)
129	```
```
  — correctly has **no** `$ ` prefix, establishing the file's own convention: blocks meant to be pasted as `.zshrc` content omit the prompt marker; blocks meant to be typed once at an interactive prompt (bash/fish/zsh-generate sections, e.g. head `FAQ.md:102-106`, `110-114`, `118-122`) keep it.
- Merge-base `FAQ.md:90-130` (`git show 79cbe89...:FAQ.md`): the entire "recommended approach" fpath paragraph and the "load and generate at the same time" paragraph (including the buggy `source` line) **do not exist at all** — confirmed via `git diff 79cbe89..855bfa6 -- FAQ.md`, which shows the whole block, including the `$ source <(rg --generate complete-zsh)` line, added fresh by commit `855bfa6` ("improve FAQ text for zsh completions"), itself layered on `7c2a7b0` ("feat(completion): support sourcing zsh completion dynamically"). This is squarely a Code-introduced-here condition, not a removed guarantee.

### Reproduction
```
$ cat test_zshrc.zsh
$ source <(rg --generate complete-zsh)
$ zsh -f test_zshrc.zsh
test_zshrc.zsh:1: command not found: $
exit code: 127
```
Second test confirms zsh doesn't abort the rest of `.zshrc` on this error, it just skips the `source` line entirely and continues — i.e., the completions are silently never loaded via this documented method, matching the candidate's stated impact (word-for-word: "zsh reports `command not found: $`... and never executes the `source` command, so ripgrep's zsh completions are never loaded via this documented method").

### Intentionality check
No rule, requirement, issue text, or review record cited or found suggests the `$ ` prefix is deliberate. The provided context note about issue #2956 (fzf/gh/fd's `.zshrc` examples implying `compinit` typically already ran) concerns a different, substantive question — ordering relative to `compinit` — not the copy-paste literalness of the prompt-prefix character. It does not touch or excuse this typo. The diff shows the paragraph was hand-authored in this PR by evidently copying the `$ `-prefixed style from the preceding one-time-command zsh block, while forgetting that this particular block's prose promises literal `.zshrc` content, exactly as its neighbor (the `fpath=(...)` block, itself correct) does. This reads as an oversight, not a design choice.

### Assessment against verification steps
1. Anchor/fix site read as bounded ranges at head and merge-base — matches candidate description exactly (line 135, `$ source <(rg --generate complete-zsh)`).
2. Trigger reproduced live in zsh — confirmed identical error text and mechanism.
3. Observable impact confirmed — `source` line is a no-op due to the leading `$` being parsed as a command name; shell startup continues but completions from this method never load.
4. Code-introduced-here confirmed — this exact line and its surrounding paragraph did not exist at merge-base; added wholesale by commit 855bfa6 in this PR.
5. No basis found for intentionality in issue/PR/rules/history.
6. No other candidate supplied to compare against per task scope.

No corrections needed to the candidate's trigger, impact, priority, action, anchor, or fix — all check out against the code as read. No separate observation to append (nothing incidental surfaced that doesn't already fold into this finding).
```

Note: the verifier's own reproduction used exit code `127` (`command not found`) where my own earlier scratch reproduction (§5) reported exit `0` for a slightly different script that had further lines after the error; this is not a discrepancy in substance — both runs confirm the identical `command not found: $` failure and the `source` line never executing, just with different trailing shell state depending on what followed the failing line in each scratch script. Both independently reproduce the candidate's claimed trigger and impact.

## 5. Everything consulted beyond the diff

All commands below were run against the offline local clone `/tmp/qual137/runs/n-867cf3ff-seed2-att-23` (`origin` is a local filesystem path) or the skill snapshot; none touched the network.

**Skill reading (full text, in order):** `SKILL.md`, `references/review-rubric.md`, `references/output-contract.md`, `references/verifier.md`. `references/re-review.md` was *not* read: step 2 of `SKILL.md` gates it on "step 1 found any prior review, reply, or trailer-bearing comment from the posting identity," and the packet states the posting identity `kamui` "did NOT author the PR and has no prior comments or reviews on it" — so this is an ordinary first review, not a re-review, and the reference's trigger condition did not fire. This is a judgment call recorded here for transparency (see §10).

**Packet reading (full text):** `/tmp/qual137/packets/n/packet.md`, all 8 sections — pinned run identity, changed-file manifest, PR body, issue body, commit table, prior review-state (10 review submissions, 10 review-thread comments, 1 non-review comment), repository-guidance table, and the binding run conditions.

**Context-gathering commands run (all exit 0 unless noted):**

- `git log --oneline -n 5 master review-head` — confirmed the two-commit head (`855bfa6` on `7c2a7b0` on `79cbe89`) and that `master` is exactly the merge-base, not beyond it.
- `git show master:docs/agents/issue-tracker.md` — exit 128, `fatal: path 'docs/agents/issue-tracker.md' does not exist in 'master'` — confirms the packet's implicit claim (the file isn't in packet §7's guidance table, and SKILL.md step 1 says "Read the base-branch `docs/agents/issue-tracker.md` when present"; it is not present).
- `git branch -a` and `git status` — confirmed branch layout (`master`, `review-head` checked out, both local + matching `origin/*` remotes) and a clean working tree before I touched anything.
- `python3 scripts/review_context.py --help` — read the tool's own interface before using it.
- `python3 scripts/review_context.py --merge-base 79cbe89deb1151e703f4d91b19af9cdcc128b765 --head 855bfa6cdae4f4fe8762f892fc4957635397083e` (run once, from the skill directory, with `GIT_DIR`/`GIT_WORK_TREE` pointed at the clone) — exit 0. Produced the manifest, the complete `--function-context` diff for both changed files, the `ranges` block, and the `history` block, saved to `/tmp/qual137/work/n-867cf3ff-seed2-att-23/review_context.md`. This is the single required diff read for step 3; I did not re-run it and did not read the diff again via any other command.
- `git show 7c2a7b018e2a3fe65be19f8d3f0bd1028e8421b1 -- FAQ.md` (`7c2a7b0`) and `git show 855bfa6cdae4f4fe8762f892fc4957635397083e -- FAQ.md` (`855bfa6cd`) — both commits are *within* the pinned head range (`master..review-head`), not beyond it; used to attribute which commit introduced the "Note though…" sentence and the `$ source <(...)` line, per the rubric's falsification step 5 (confirm gate 6, unintentional) and the packet's mandatory note about not re-litigating fixed-up review feedback.
- `git show review-head:crates/core/flags/complete/rg.zsh | sed -n '1,40p'` and `'420,450p'` — bounded-range reads of the `#compdef rg` header and the guarded invocation block, to confirm the enclosing function structure that the `--function-context` diff output already showed (the diff's own hunk for `rg.zsh` actually printed the entire remainder of the file as unchanged context, because zsh has no `diff.<lang>.xfuncname` pattern configured, so git's function-context fallback is a plain positional-context dump rather than a symbol match — recorded per the rubric's instruction to say so when this happens).
- `git show 79cbe89deb1151e703f4d91b19af9cdcc128b765:crates/core/flags/complete/rg.zsh` — read the merge-base version of the completion script to establish the pre-existing (unconditional `_rg "$@"`) behavior for the falsification of candidates `zsh/funcstack-compdef-guard` and the compinit-precondition finding.
- `find . -iname "test-complete*"` and `find . -path ./.git -prune -o -iname "*complete*" -print` (repo-wide, case-insensitive via `-iname`) — located `ci/test-complete` as the only CI script touching completions; located `crates/core/flags/complete/` as the only other completion-related path.
- Read `ci/test-complete` in full (98 lines, under the 300-line whole-file threshold) — confirmed its `get_comp_args` helper runs `_RG_COMPLETE_LIST_ARGS=1 source $1` in a bare subshell with no `compdef` defined, which is exactly the "no compdef" branch of the new guard.
- Read `FAQ.md:90-152` (bounded range at head) — the complete "shell auto-completion" FAQ answer, covering bash, fish, zsh (both methods), and PowerShell, to establish the file's own sibling convention for when a fenced block carries a `$ ` prompt versus when it is literal file content.

**Focused execution (all under the packet's execution allowance, offline, outside the clone, in `/tmp/qual137/work/n-867cf3ff-seed2-att-23/`, none over 5 minutes):**

| # | Command / script | Purpose | Exit | Duration | Result summary |
| --- | --- | --- | --- | --- | --- |
| 1 | `zsh_test/mock_rg.zsh` sourced 3 ways (`zsh -f -c '...'`, 3 invocations) | Initial sanity check of the `funcstack`/`compdef` guard logic | 0 (all 3) | <1s each | Test 1 (no compdef): ran `_rg` immediately, as expected. Test 2 (compdef stub present): called `compdef _rg rg`, as expected. Test 3 (nested `source` inside a wrapper function, meant to simulate autoload): also called `compdef`, which on reflection is *not* a valid simulation of real zsh autoload semantics — flagged and redone properly in run 2 below rather than relied on. |
| 2 | `zsh_test2/fpathdir/_rg` via real `autoload -Uz _rg; fpath=(...)`, 2 invocations (no compdef stub, and with a compdef stub) | Correctly simulate real fpath-autoload invocation, the traditional install method | 0 (both) | <1s each | Both: `$funcstack[1] == _rg` was true inside the autoloaded function body, so `_rg "$@"` ran directly in both cases, exactly matching intended behavior for the traditional "installed completion file" usage. |
| 3 | Real `compinit` test: `autoload -Uz compinit; compinit -u -d …; source fpathdir/_rg` | Reproduce the PR's actual primary use case: `.zshrc` calls `compinit`, then sources the generated completion | 0 | ~1s | `$_comps[rg]` == `_rg` after sourcing — the completion was cleanly registered via `compdef _rg rg`, no error. This is the head-branch, fixed behavior. |
| 4 | Real, no-`compinit` test: `source fpathdir/_rg` with no prior `compinit` | Check the edge case the FAQ doesn't warn about | 1 | ~1s | `_rg:341: command not found: _arguments` — confirms the `faq/zsh-source-missing-compinit-precondition` finding's claimed failure mode on the head branch. |
| 5 | Same two tests (3 and 4) repeated against the **merge-base** version of `rg.zsh` (copied out via `git show 79cbe89…:… > fpathdir_base_rg`) | Establish the pre-existing baseline for comparison (rubric falsification step 4: confirm introduced-here vs. pre-existing) | 1 (both) | ~1s each | With `compinit` run first: `_arguments:comparguments:327: can only be called from completion function` — the *exact* error text from the issue. Without `compinit`: `_rg:341: command not found: _arguments`. Confirms both failure modes existed at the merge-base already (the compinit-run-first case is the one this PR actually fixes; the no-compinit case is unchanged, not worsened). |
| 6 | `fake_zshrc.zsh` containing a literal `$ source <(echo ...)` line, run with `zsh -f` | Reproduce the copy-paste bug in the FAQ's `source` snippet | 0 | <1s | `fake_zshrc.zsh:2: command not found: $`; the `source` line never executed; script continued past it. This is the decisive reproduction behind the must-fix finding. |

None of these ran `cargo build`/`cargo test` (excluded by the run conditions), and none modified the clone (all scratch files live under `/tmp/qual137/work/n-867cf3ff-seed2-att-23/`, all git reads used `git show`, no `git checkout`/`switch`/`reset`/`stash` was ever run).

**Context digest inputs** (see §6) were computed once, from a hand-built JSON file `/tmp/qual137/work/n-867cf3ff-seed2-att-23/context_input.json` containing the exact `pr.title`/`pr.body` from packet §3 and the exact issue `coordinate`/`title`/`body` from packet §4, `comments: []` with `comments_available: true` (0 comments, matching the packet's explicit "(0 total; `comments_available: true`)"), `specs: []` (none supplied), and `guidance: []` (packet §7: no `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` present at the merge-base for any changed-path ancestor or the root).

**Output-contract tooling run:**

- `python3 scripts/context_fingerprint.py /tmp/qual137/work/n-867cf3ff-seed2-att-23/context_input.json` — exit 0, printed `fea14e64c218222905fc4b1fc7bde1d1907a2826ffb04195d9add739b148f6a1`, computed once as required.
- `python3 scripts/validate_review.py --render < payload_draft.json` — exit 0, printed the three anchor fragments, pasted verbatim into the summary body.
- `python3 scripts/validate_review.py < payload_draft.json` — exit 0, zero violations, run *after* pasting the rendered fragments into the body (so the summary-reference check could pass by construction) and again as the final check before treating the payload as complete.
- `python3 scripts/validate_review.py --emit-batch < payload_draft.json` — exit 0, produced the one-call batch JSON (`commit_id`, `event: COMMENT`, `body`, 3 line `comments`) saved to `/tmp/qual137/work/n-867cf3ff-seed2-att-23/batch.json`. Not submitted anywhere (publication disabled); its content is reproduced in the payload file.
- I did **not** run `scripts/validate_review.py --self-test` or `scripts/test_context_fingerprint.py` — SKILL.md step 3 explicitly says "the fingerprint script's own regression test and the review validator's self-test belong in the skill repository's CI, not in a review," and rule 3 of the dispatch instructions says not to run the skill's self-tests inside this cell.

## 6. The `context` digest and its inputs

- **Digest:** `fea14e64c218222905fc4b1fc7bde1d1907a2826ffb04195d9add739b148f6a1`
- **Computed once**, via `python3 scripts/context_fingerprint.py <path-to-context_input.json>`, per SKILL.md step 3 ("Compute the `context` digest once").
- **Inputs** (from `/tmp/qual137/work/n-867cf3ff-seed2-att-23/context_input.json`, all values copied verbatim from the pinned packet, none re-fetched):
  - `pr.title`: `feat(completion): support sourcing zsh completion dynamically`
  - `pr.body`: the full PR description verbatim from packet §3 (Summary/Test plan/`Closes #2956`)
  - `issues`: one entry, `coordinate: BurntSushi/ripgrep#2956`, `title: Can't source zsh completions directly`, `body`: the full issue body verbatim from packet §4, `comments: []`, `comments_available: true` (packet §4: "(0 total; `comments_available: true`)")
  - `specs`: `[]` (none supplied or found)
  - `guidance`: `[]` (packet §7: no root or path-scoped `AGENTS.md`/`CLAUDE.md`, no root `CONTEXT.md`, present at the merge-base)

## 7. Mechanism checklist

- **Question channel:** did not fire. No candidate met the rubric's static-unresolvability bar ("no static evidence could settle it") — every candidate I raised was settled either by reading the diff/sibling text or by focused zsh execution, both static-enough sources available to me. No `[Question]` item appears in the payload.
- **Clean-verdict or related-acquittal verification:** neither mode fired. Zero-survivor mode requires zero candidates to survive *as findings*; three survived, so it never applied. Related-acquittal mode requires at least one survivor (true) but only pulls in a dropped row when its `kind` is `bug`/`concurrency`/`invariant`/`security` **and** it shares a file or names the same function/branch/lock as a survivor; the two dropped `kind=bug` rows (`zsh/funcstack-compdef-guard`, `zsh/ci-test-complete-compat`) are both anchored in `crates/core/flags/complete/rg.zsh`, a different file from every survivor's `FAQ.md` anchor/fix, and neither shares a function/branch/lock name with any survivor's claim — so no related-acquittal rows were sent to the verifier. No re-open occurred in either mode because neither mode ran.
- **Observations:** fired once. `zsh/comment-accuracy-observation` (comment-accuracy nitpick in `rg.zsh:439-443`) failed finding admission on gate 1 (meaningful impact) and gate 7 (worth author's time) while still being an accurate, evidence-backed fact, so it was routed to the summary-only `Observations` channel per the rubric's routing rule. It is the only one raised; the 3-item cap was never approached.
- **Fix-sufficiency check on any concurrency/invariant candidate:** did not fire — no candidate was classified `kind=concurrency` or `kind=invariant`; this is a documentation-and-shell-completion change with no concurrent or cross-path state-consistency surface. Verifier.md's five-step concurrency/invariant procedure (state the invariant at rule level, check steady-state vs. shutdown, enumerate sibling interleavings/paths, widen `change` to rule level) was therefore not applicable and was not run.
- **Follow-up verifier round:** did not fire. The single initial candidate batch (one candidate: `faq/zsh-source-snippet-prompt-prefix`) returned `confirmed` with no correction and no re-opened row, so no candidate newly reached render eligibility after it, and the one permitted follow-up batch was not needed.
- **Deferral handling:** the packet's prior-review record (§6 of the packet) contains one explicit deferral-adjacent moment: `vegerot`'s review-thread comment 5 ("how about I remove the FAQ patch, and we can discuss how to improve the FAQ in a new issue?"), addressed to `@okdana @BurntSushi`. This was *not* accepted — the final merged head keeps the FAQ patch (with `BurntSushi`'s own rewrite in commit `855bfa6cd`), so the "remove and defer to a new issue" proposal was superseded by the maintainer's own edit, not left open. I treated this as resolved-by-final-commit rather than as an open deferral under the rubric's "explicit deferral… is evidence that the deferred question is open" clause, because the review record's own last word (`BurntSushi`'s non-review comment, packet §6 non-review-conversation item 1: "I've left it in the FAQ and fixed up the wording…") explicitly re-adopts and finalizes the FAQ content — the deferral was an offer that was not taken up, not an unresolved open question about API/naming/design shape. No candidate was routed as a re-opened question on this basis.
- **Retrospective mode:** applied throughout. The summary body carries the mandatory `**Mode:** Retrospective review of merged pull request; publication disabled.` line (output-contract.md's required sentence for `merged=true` without separate publication authorization). Step 5's "re-fetch the head immediately before the first write" was not performed because step 5 also says "In non-publishing retrospective mode, skip the write and report the complete would-be review instead" — there is no write to precede, so no re-fetch was owed, and none was attempted (also consistent with the offline run condition, which forbids any network call).
- **Early dispatch of the verifier batch:** SKILL.md defines no mechanism for dispatching a verifier batch before the primary falsification pass completes; the skill's order is strictly falsify-then-verify ("Falsify and deduplicate every candidate under the rubric… Only survivors are eligible for verification"). I dispatched the single verifier batch only after the complete 6-row candidate ledger (§3) was already written to this report file, consistent with rule 6's persistence requirement and SKILL.md's own instruction to write the candidate ledger "at the end of falsification" before verification.

## 8. History discipline

I read history only within the pinned range `master..review-head` (merge-base `79cbe89deb1151e703f4d91b19af9cdcc128b765` to head `855bfa6cdae4f4fe8762f892fc4957635397083e`), never beyond the pinned head. Exact history commands run:

- `git log --oneline -n 5 master review-head` (showed the two pinned commits plus three merge-base ancestors, none newer than the merge-base)
- `git show 7c2a7b018e2a3fe65be19f8d3f0bd1028e8421b1 -- FAQ.md` (first commit on the head)
- `git show 855bfa6cdae4f4fe8762f892fc4957635397083e -- FAQ.md` (second commit on the head, = the pinned head itself)
- `git show 79cbe89deb1151e703f4d91b19af9cdcc128b765:crates/core/flags/complete/rg.zsh` and `...:FAQ.md` (merge-base blob reads, not history traversal beyond the pin)

The independent verifier sub-agent reported its own history commands separately in §4 (`git log --oneline <merge-base>..<head> -- FAQ.md` and `git diff <merge-base> <head> -- FAQ.md`), both also bounded to the pinned range, and explicitly disclosed reading nothing beyond `855bfa6cdae4f4fe8762f892fc4957635397083e`.

No `git fetch`, `git pull`, `gh`, `curl`, or other network-touching command was run by me or by the sub-agent.

## 9. Sandbox disclosure

I read only: the clone at `/tmp/qual137/runs/n-867cf3ff-seed2-att-23`; the skill snapshot at `/tmp/qual137/snapshots/867cf3ff/snapshot-path-omitted/`; the packet at `/tmp/qual137/packets/n/packet.md`; my own work directory `/tmp/qual137/work/n-867cf3ff-seed2-att-23/`; and my own report/payload/timing paths under `/tmp/qual137/reports/n/`.

One incidental exception to disclose: in listing `/tmp/qual137/reports/n/` with `ls` (to check that my own report/payload/timing paths existed before creating them), the directory listing surfaced the *names* of other cells' report files for this same target (`n-867cf3ff-seed1-att-22-*`, `n-bea6be14-seed1-att-21-*`, `n-bea6be14-seed2-att-24-*`, and their `-meta.json`/`-session.txt` siblings). I did not open, read, or otherwise consult the contents of any of those files — only their filenames appeared in the `ls` output I requested for my own directory-existence check. Rule 7 requires me to report any other path read; I list these filenames here in the interest of full disclosure even though I did not read their contents, since the bare `ls` on a shared parent directory is arguably already a boundary case. No other path outside the sandbox was touched.

The sub-agent I dispatched was explicitly instructed (rule 7 in its prompt) to stay within the clone, the skill snapshot, and its own scratch directory `/tmp/qual137/work/n-867cf3ff-seed2-att-23/verifier1/`, and it reported reading only `FAQ.md` at head/merge-base via `git show` and its own scratch files under that directory.

## 10. Notes — judgment calls on ambiguity

1. **Re-review reference not read.** SKILL.md step 2 gates reading `references/re-review.md` on "step 1 found any prior review, reply, or trailer-bearing comment from the posting identity." The packet's prior-review record (10 review submissions, 10 thread comments, 1 non-review comment) is extensive, but none of it is from `kamui` (the posting identity for this run). I treated this literally: the gate is about the *posting identity's own* prior involvement, not about whether the PR has *any* prior review activity at all, so I ran this as an ordinary first review rather than a re-review, and did not apply carried-finding/thread-reply/dispute rules to the pre-existing `BurntSushi`/`vegerot`/`okdana` threads (all already resolved and superseded by the final merged head per the packet's own mandatory note).
2. **`must-fix` vs. `consider` for the prompt-prefix finding.** The rubric's line "A proven correctness, security, or explicit-requirement gap on an authoritative execution path is `must-fix`, even when the edit is one line, documentary" could be read narrowly (only code execution paths qualify) or broadly (a documented, user-facing setup instruction that provably fails when followed literally also qualifies, since "authoritative" documentation is functionally an execution path for the reader). I applied the broad reading, given the explicit "documentary" carve-out in that same sentence, and classified `faq/zsh-source-snippet-prompt-prefix` as `must-fix`/P2 rather than `consider`. This reading is recorded here rather than in the payload's `Ambiguities` section because I judged it a settled application of an explicit rubric clause (the clause itself anticipates documentary must-fix findings), not a genuinely two-readings-supportable term contest requiring disclosure under SKILL.md step 3's "two genuinely supportable readings" rule. I flag it here for the record regardless, since a narrower reader could disagree.
3. **`--function-context` fallback for `rg.zsh`.** The single diff hunk for `crates/core/flags/complete/rg.zsh` printed the change plus the *entire remainder of the file* as context (207 lines), because zsh has no `diff.<lang>.xfuncname` pattern configured in this environment and git's function-context feature fell back to a positional dump rather than isolating the enclosing function. Per the rubric ("read that symbol as a bounded range… and say so in the private record"), I did not treat this as satisfying "read the enclosing symbol" by itself; I separately read `crates/core/flags/complete/rg.zsh:1-40` and `:420-450` as bounded ranges to confirm the `#compdef rg` header and the `_rg()` function boundary, which the oversized diff context had already shown but which I wanted directly cited at known line numbers.
4. **Comment-accuracy candidate routed to Observations, not dropped silently.** `zsh/comment-accuracy-observation` is accurate (the new comment technically describes only the `else` branch) but immaterial (the code it describes is correct either way). I judged this squarely within the rubric's Observations routing rule ("Route an accurate fact to `Observations` when it fails finding admission specifically on meaningful or proven consequence") rather than within the stricter rule that a fact passing gates 1 and 4 must be a finding — here it fails gate 1 (no meaningful impact: the comment's imprecision has zero runtime or reader-safety consequence), so Observations was the correct channel, not a finding at any priority.
5. **No `Ambiguities` section in the published summary.** I did not add one, because I judged no rubric or contract *term* had two genuinely supportable readings that I resolved by picking the "safer" one — item 2 above is a judgment call about severity classification, not a contested term. If a stricter reviewer disagrees with the must-fix classification in item 2, that disagreement would surface as a disputed finding on republication, not as an ambiguity I was required to flag in this run.
6. **Two `kind=bug` dropped rows evaluated for related-acquittal even though no clean-verdict batch ran.** Related-acquittal mode only matters when the verifier batch is dispatched (which it was, for the must-fix candidate) and a dropped row is "related." I explicitly checked both dropped `kind=bug` rows against the file/function/branch/lock test and excluded both (different file, unrelated claim) rather than assuming the mode doesn't apply just because the survivor and the dropped rows look topically related (all three concern "the zsh completion feature this PR adds"). Topical relatedness is not the test the skill defines; file/function/branch/lock identity is, and I applied that narrower test.

## Payload file

The complete rendered review (summary body, run trailer, and all three finding comments with their trailers, plus the emitted-batch JSON structure) is in `/tmp/qual137/reports/n/n-867cf3ff-seed2-att-23-payload.md`. `validate_review.py` (no arguments) reported zero violations against the assembled payload, and `--emit-batch` produced the one-call batch cleanly (saved to `/tmp/qual137/work/n-867cf3ff-seed2-att-23/batch.json`, not submitted anywhere). The timing sidecar's `payload_validated_at` was marked immediately after that zero-violation validation run.

