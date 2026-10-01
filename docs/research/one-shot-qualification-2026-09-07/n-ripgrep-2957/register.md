# Target

- Repository: `BurntSushi/ripgrep`
- PR #2957 — "feat(completion): support sourcing zsh completion dynamically"
- Head SHA (PR branch): `855bfa6cdae4f4fe8762f892fc4957635397083e`
- Merge-base: `79cbe89deb1151e703f4d91b19af9cdcc128b765` (master)
- The PR contains two commits on top of the merge-base:
  - `7c2a7b018e2a3fe65be19f8d3f0bd1028e8421b1` — "feat(completion): support sourcing zsh completion dynamically" (author: Max Coplan / vegerot)
  - `855bfa6cdae4f4fe8762f892fc4957635397083e` — "improve FAQ text for zsh completions" (author: Andrew Gallant / BurntSushi)
- Squash-merged into master as `94305125ef33b86151b6cd2ce2b33d641f6b6ac3` ("zsh: support sourcing zsh completion dynamically", committed 2024‑12‑31T13:23:13Z — matches the PR's recorded `mergedAt`). The tree of `9430512` is byte-identical in effect to the tree at `855bfa6`; it is not a follow-up fix, it is the same change under a different commit hash produced by GitHub's squash-merge. `855bfa6` itself is *not* an ancestor of current master, but only because of the squash — not because it was reverted or superseded by different content.
- Files touched: `FAQ.md` (+19/‑4 across the two commits), `crates/core/flags/complete/rg.zsh` (+7/‑2).

# Verdict

**adjudicated clean — 0 material defects (`D_n = 0`)**

# Defect register

None.

# Reproduction

Both commands below were run from a real clone of the staging bare repo (`/tmp/qual137/staging/ripgrep.git`), building `rg` in release mode and running the repo's own completion-consistency test.

**At head (`855bfa6cdae4f4fe8762f892fc4957635397083e`):**
```
$ git checkout 855bfa6cdae4f4fe8762f892fc4957635397083e
$ cargo build --release -q        # 13.3s wall
$ ./ci/test-complete
Comparing options:
-.../target/release/rg
+.../crates/core/flags/complete/rg.zsh
OK
$ echo $?
0
```

**At merge-base (`79cbe89deb1151e703f4d91b19af9cdcc128b765`):**
```
$ git checkout 79cbe89deb1151e703f4d91b19af9cdcc128b765
$ cargo build --release -q        # 4.6s wall
$ ./ci/test-complete
Comparing options:
-.../target/release/rg
+.../crates/core/flags/complete/rg.zsh
OK
$ echo $?
0
```
`ci/test-complete` (the only CI job that exercises this file — see `.github/workflows/ci.yml:182`) passes identically before and after. It does not, however, exercise the `funcstack`/`compdef` branch at all (it only sources the file with `_RG_COMPLETE_LIST_ARGS=1` and diffs option names against `rg --help`), so passing it is necessary but not sufficient evidence of correctness for the new branch; the branch itself was verified by direct zsh experimentation below.

`zsh -n crates/core/flags/complete/rg.zsh` → no syntax errors at head.

**Direct behavioural reproduction of the bug being fixed (issue #2956), old vs. new code**, using the actual `_arguments`-based function body sourced under an interactive-like zsh with `compinit` already loaded:

- Old code (`_rg "$@"` unconditional at end of file), `source`d directly:
  ```
  _arguments:comparguments:327: can only be called from completion function
  EXIT_STATUS=1
  ```
  This is the exact error text reported in issue #2956.

- New code (the `if [[ $funcstack[1] == _rg ]] || (( ! $+functions[compdef] )); then … else compdef _rg rg; fi` guard), same `source` scenario:
  ```
  EXIT_STATUS=0
  ```
  and inspecting the compsys state afterward shows `${_comps[rg]}` = `_rg` — i.e. `compdef _rg rg` performed exactly the registration that `compinit`'s own fpath scan would have performed for a `#compdef rg`-tagged file. This is the correct, documented public API (`man zshcompsys`) for registering a completion function outside of the normal fpath scan.

**Confirmation that the ordinary fpath/compinit path is unaffected:**
Placing the same file in `$fpath`, running `autoload -Uz compinit; compinit`, then invoking the (autoload-stub) `_rg` the way the completion dispatcher would, shows `$funcstack` at the moment the file is loaded is `(_rg _rg)` — i.e. `$funcstack[1] == _rg` is true in exactly this path, so the guard takes the `_rg "$@"` branch, identical to the pre-PR unconditional behavior. Also confirmed with a counter that the explicit trailing `_rg "$@"` call does **not** cause a double-invocation with zsh's own "call the function after autoload" semantics — a `_rg2` control file with no trailing call is auto-invoked exactly once by zsh itself, and the real `_rg` file (which explicitly self-invokes) is also invoked exactly once (`count=1` after the first completion attempt). So there is no double-registration/double-run hazard either way.

**Cross-checked against widely-deployed prior art:** `docker completion zsh`, `gh completion -s zsh`, and `kubectl completion zsh` (all Cobra-generated, installed locally) end with the identical `if [ "$funcstack[1]" = "_cmd" ]; then _cmd; fi` idiom. ripgrep's version is a strict superset (it also registers via `compdef` in the `else` branch instead of silently doing nothing), so the core guard is an established, battle-tested pattern, not a novel and unproven one.

# Not ground truth

Plausible-sounding objections that do **not** hold up:

1. **"Dropping the unconditional `_rg "$@"` breaks normal fpath/compinit completion."** False — see Reproduction above. `$funcstack[1] == _rg` is true precisely in the autoload/compsys-dispatch path, so the branch taken there is identical to the old unconditional call.

2. **"`compdef` might not be the right call, or might not exist when needed."** The `(( ! $+functions[compdef] ))` half of the guard already handles the case where `compdef` is undefined, falling back to the old (best-effort) `_rg "$@"` call. `compdef` is the documented zshcompsys API for exactly this purpose and is proven correct empirically (`_comps[rg]` ends up `_rg` after the call, matching what compinit's own registration produces).

3. **"`$funcstack[1] == _rg` / `$+functions[compdef]` is non-idiomatic or fragile zsh."** It is exactly the form recommended in review by contributor `okdana` (a zsh-completion domain expert), replacing an earlier `type compdef >/dev/null` draft that the author's own CI (`ci/test-complete`) rejected. It is idiomatic zsh (`$+name` is the standard "is-set" test; `functions` is zsh's real associative array of defined functions).

4. **"Referencing `$funcstack[1]` under `setopt no_unset` will abort with 'parameter not set' since `funcstack` may be empty."** Verified true only for a synthetic case that never occurs on this code path: bare top-level evaluation with no enclosing frame (`zsh -c '[[ $funcstack[1] == _rg ]]'`). The instant this code is reached via `source <(...)` or `eval "$(...)"` — the only two invocation styles the PR/FAQ/review thread ever discuss — `$funcstack` already has an entry (the source/eval frame itself), so the reference is always "set," with or without `no_unset`. Confirmed by direct experiment. Not a real trigger.

5. **"The FAQ's added fpath step is scope creep for a completion-behavior PR."** It isn't: reviewer `okdana` explicitly flagged, on this very PR, that the *pre-existing* zsh FAQ instructions never told the user to add the directory to `fpath` and thus "don't really do anything as written." The head commit's FAQ rewrite fixes that pre-existing documentation defect as part of "improve FAQ text for zsh completions"; it is a deliberate, discussed, in-scope repair, not accidental drift.

6. **"The FAQ's slower-startup claim (~4ms) is unsubstantiated."** BurntSushi's own merge comment (`2024-12-31T13:11:11Z`) frames it as a soft, honestly-hedged claim ("4ms might not seem like much... I cannot perceive a 4ms lag, but if you accrue 10 of those..."), and it's directionally uncontroversial: the dynamic method forks/execs `rg` and regenerates ~450 lines of zsh on every shell startup, versus the static-file method which zsh's completion-dump caching can skip entirely until first actual completion. A reviewer could ask for a benchmark, but disputing the *direction* of the claim would be wrong, and its absence is a hygiene nit, not a material defect.

7. **"There's a redundant/awkward sentence in the FAQ ('is easier to setup, is generally slower... and will add more time')."** True as a grammar nit (dangling parallel structure — the "it" is dropped after the first clause), but purely cosmetic; doesn't change the accuracy or actionability of the guidance.

# Preexisting hints

The PR's own review thread (all comments below predate the merge instant `2024-12-31T13:23:13Z`) already surfaced and resolved exactly the two design questions a reviewer would need to check — and both were resolved *in favor of* the final code, i.e. the record affirmatively supports "clean" rather than gesturing at an undiscovered defect:

- `okdana` (2024-12-31T00:42:57Z, inline on `crates/core/flags/complete/rg.zsh:438`), responding to the author's own doubt about `ci/test-complete`:
  > "the test script isn't wrong. the function is designed to be sourced by it without requiring anything from the completion system. we could have the script load `compdef` but it would still do the wrong thing with that check. i would suggest this as more idiomatic (and faster) than the `type` method: `if [[ $funcstack[1] == _rg ]] || (( ! $+functions[compdef] ))`"

  This is verbatim the guard that shipped. The author (`vegerot`) replied "Thanks! Done" (2024-12-31T01:01:21Z).

- `vegerot`'s own earlier comment on the same line (2024-12-31T00:26:22Z) shows the iteration history (an initial `type compdef` 2-branch version, CI failure, a 3-branch workaround felt "redundant," then okdana's cleaner fix) — i.e. the exact mechanism being adjudicated here was stress-tested by the repo's own CI (`ci/test-complete`) during review, not merged on faith.

- `okdana` (2024-12-31T00:45:31Z, inline on `FAQ.md:122`) flagged the pre-existing FAQ gap (missing `fpath` step) that the head commit fixes — see "Not ground truth" item 5.

No participant flagged anything resembling a correctness concern about the final guard, nor about the `compdef _rg rg` call, nor was there any post-merge issue, revert, or regression report referencing #2956/#2957 found in the repo's history through the current `master` tip.

# Leakage

A truncated mirror for this evaluation must exclude:

- `9430512` (`94305125ef33b86151b6cd2ce2b33d641f6b6ac3`) — the squash-merge commit on `master`; its diff is the same change and its commit message ("Fixes #2956") gives away both the bug and the fix.
- `7c2a7b0` (already presumably excluded as pre-head, but flagging since it's the true first commit of the PR with the informative message "Fixes #2956" / "Closes #2956" and test plan).
- Issue **#2956** ("Can't source zsh completions directly") — states the exact bug and reproduction.
- PR **#2957** itself and all its review comments (`gh api repos/BurntSushi/ripgrep/pulls/2957/comments`) — contains the exact fix under discussion, including okdana's verbatim final guard.
- No later commit touches the `funcstack`/`compdef` block (checked every subsequent commit on `master` that touched `crates/core/flags/complete/rg.zsh`: `78383de, 99fe884, cdeff3e, 640ad85, 365edbf, f168a87, c4f34e0, 42e6e85, a709a3b, b357caa, f2f3d00` — none mention or modify this hunk), so there is no later "repair" commit to worry about hiding.

# Adjudicator's confidence and limits

High confidence. Every load-bearing claim in the hypothesis was independently reproduced from primary sources rather than taken on the PR author's/reviewers' word:

- The exact pre-fix error message from #2956 was reproduced live.
- The post-fix absence of that error, and correct `compdef`-based registration (`_comps[rg]=_rg`), was reproduced live.
- The claim that the ordinary fpath/compinit path is unaffected was verified by directly inspecting `$funcstack` state during a real zsh-autoload-triggered load, not merely inferred.
- The "no double-invocation" property (relevant because the file both defines and unconditionally-in-one-branch calls `_rg`) was verified with an invocation counter.
- `ci/test-complete` was actually run (not just read) at both the head and merge-base commits, with a real `cargo build --release` in between.
- The one genuine-looking edge case found during adversarial testing (`no_unset` + bare top-level `$funcstack[1]` reference) was chased down to the byte and shown not to trigger on any invocation path the PR/FAQ actually recommends.

Remaining minor uncertainty (does not affect the verdict): I did not get a fully scripted interactive TAB-completion capture working end-to-end via `zpty` (terminal-control-code noise made the transcript hard to parse cleanly), so the very last mile — an actual keystroke-driven completion firing `_arguments` inside genuine completion-widget context after `compdef`-based dynamic registration — is inferred from the `_comps[rg]=_rg` state match with the compinit-native registration rather than watched live end-to-end. I judge this `unresolved`-but-immaterial: `_comps[cmd]=_funcname` is the sole piece of state `_main_complete` consults to dispatch completion, and it is the same registration compinit itself produces, so a difference in downstream behavior would require zsh's own completion dispatcher to treat identically-shaped registrations differently depending on how they were created, which is not documented or plausible.

---

## Register version 2 — 2026-09-07T10:03Z (post-grid revision)

**`D_n` changes from 0 to 1. This target is no longer a clean control.**

Version 1 above adjudicated this pull request clean before any reviewer ran, and it is retained
verbatim as the sealed pre-dispatch record. One cell of the grid then published a finding that
version 1 had not considered. Under the method's §4 rule, that finding went to an **independent
adjudicator with the arm, replicate and cost labels removed**; the adjudicator's brief and full
ruling are in [`../adjudication/nc1-ruling.md`](../adjudication/nc1-ruling.md). It ruled the claim
**material**.

### GT-n1 — the `.zshrc` snippet the pull request adds cannot be pasted as instructed

**Location (at head `855bfa6c`):** `FAQ.md` line 135, inside the block the pull request adds.

The prose immediately above it says: *"Or if you'd prefer to load and generate completions at the
same time, you can add the following to your `$HOME/.zshrc` file"*. The block it introduces reads

```zsh
$ source <(rg --generate complete-zsh)
```

with a leading `$ ` shell-prompt prefix.

**Trigger.** A reader follows the instruction literally and pastes that line into `.zshrc`.

**Demonstrated consequence.** Every interactive zsh startup emits `command not found: $` (reproduced
by the adjudicator with `zsh -i` against a `.zshrc` holding the block; exit 127 on direct sourcing),
and `source` is never reached, so the completions this pull request exists to make loadable are
never loaded. The adjudicator isolated the cause with a control run: the identical line without the
stray `$ ` sources cleanly. The line is introduced by this pull request and does not exist at the
merge-base.

**The file's own convention supports the reading.** Blocks that are content for a config file —
the adjacent `fpath=($HOME/.zsh-complete $fpath)` block, the PowerShell profile-function block —
carry no prompt prefix; the `$ ` prefix in this document marks one-time terminal commands. This
block is introduced as config-file content and prefixed as a terminal command.

**Required corrective outcome.** Any sufficient fix removes the stray `$ ` from the `.zshrc`-paste
block, so a reader who copies the documented snippet gets a working `source` call rather than an
error at every shell startup. The specific patch shape does not matter.

**Class.** This defect **is the pull request's own promised change failing** — the pull request
exists to document sourcing zsh completions dynamically, and the line documenting it does not work.
It is therefore the one target in this grid of the class #124 identified, and stage 1's criterion 8
capped that class at one of the four *buggy* targets. It arrived here by register revision on a
target that was frozen as **clean**, which is a different and stronger deviation: see the README's
§3, deviation 3.

### Consequences for the grid, applied uniformly

- The frozen target mix becomes **five buggy and one clean**, not four and two. Under method §4 that
  alone prevents a full positive screen and makes this qualification **incomplete**.
- Every attempt on this target is rescored against version 2: three attempts that returned Approved
  are **false clean**, and one recovered GT-n1 with a sufficient fix.
- No other target's register changed. No other new candidate survived adjudication anywhere in the
  grid.
