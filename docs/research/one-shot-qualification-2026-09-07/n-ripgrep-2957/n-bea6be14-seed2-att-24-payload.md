**Approved (advisory)** — 0 must-fix findings, 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Let users source ripgrep's zsh completions directly (`source <(rg --generate complete-zsh)`) without first writing them to a file, and fix the FAQ's zsh completion instructions.

**Issue fit:** Met — sourcing the generated zsh completion no longer raises `_arguments:comparguments:327: can only be called from completion function` (issue #2956). `crates/core/flags/complete/rg.zsh:437-444` now distinguishes being invoked as the real `_rg` completion widget (`$funcstack[1] == _rg`) from being sourced directly, calling `compdef _rg rg` only in the latter case; verified by tracing the code and by executing the sourcing sequence in a local zsh with `compinit` already active, matching the issue reporter's own setup. The pull request's test-plan step 2 (tab-completing `--generate=complete-zs<TAB>`) is also satisfied, since `compdef` registers the same `_rg` function the normal completion path already used.

**Coverage:** Complete merge-base diff reviewed (`FAQ.md`, `crates/core/flags/complete/rg.zsh`). `ci/test-complete`'s `get_comp_args` sourcing mechanism was traced and re-executed locally against the head version (still produces the expected argument-spec dump, no regression); the full `ci/test-complete` script could not run because it also diffs against `rg --help`, which requires a built `rg` binary that this run's execution allowance excludes.

**Reviewed:** `855bfa6cd` against merge-base `79cbe89de`.

## Findings

- [P3] [consider] Fix missing subject in the zsh dynamic-source caveat — anchor [`FAQ.md:138-139`](https://github.com/BurntSushi/ripgrep/blob/855bfa6cdae4f4fe8762f892fc4957635397083e/FAQ.md?plain=1#L138-L139)

## Observations

- The new zsh code blocks in FAQ.md are tagged with the `zsh` language for syntax highlighting while the adjacent bash, fish, and PowerShell blocks in the same section remain untagged. Evidence: `FAQ.md:107-141`.

<!-- review-run head=855bfa6cdae4f4fe8762f892fc4957635397083e base-ref=master base-sha=79cbe89deb1151e703f4d91b19af9cdcc128b765 merge-base=79cbe89deb1151e703f4d91b19af9cdcc128b765 workflow=v5b-10 context=fea14e64c218222905fc4b1fc7bde1d1907a2826ffb04195d9add739b148f6a1 issues=BurntSushi/ripgrep#2956 coverage=complete -->

---

## Finding comment — `FAQ.md:138-139`

**[P3] [consider] Fix missing subject in the zsh dynamic-source caveat**

**Triggers when:** A reader reads the new "Or if you'd prefer to load and generate completions at the same time" paragraph in FAQ.md's zsh completion section.

**Impact:** "Note though that while this approach is easier to setup, is generally slower than the previous method, and will add more time to loading your shell prompt." drops the subject before "is generally slower," so the second clause reads as a sentence fragment and the caveat is harder to parse correctly.

**Change:** In FAQ.md, add a subject to the second clause, e.g. "...while this approach is easier to set up, it is generally slower than the previous method, and will add more time to loading your shell prompt."

Closing this without action is a correct response.

<!-- finding id=faq/zsh-source-caveat-grammar head=855bfa6cdae4f4fe8762f892fc4957635397083e priority=P3 action=consider blocking=false kind=maintainability -->
