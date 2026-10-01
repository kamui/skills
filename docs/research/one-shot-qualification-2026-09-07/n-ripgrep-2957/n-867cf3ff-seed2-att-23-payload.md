# Review payload — `BurntSushi/ripgrep#2957` (as it would be posted)

Posting identity: `kamui`. Event: `COMMENT`. This is a **retrospective review of a merged pull request; publication is disabled** — rendered here exactly as it would be posted, and not submitted anywhere.

---

## Summary (review body)

**Changes Requested (advisory)** — 1 must-fix finding, 2 consider findings.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Let zsh users source the generated completion script directly (`source <(rg --generate complete-zsh)`) instead of only installing it to a file in `fpath`, and document that path in the FAQ.

**Issue fit:** Met — sourcing the generated completion directly no longer reproduces the issue's reported error (`_arguments:comparguments:327: can only be called from completion function`) in the issue's own scenario (a `.zshrc` where `compinit` already ran); tab-completion of `--generate`'s own values is untouched by this change.

**Coverage:** Complete merge-base diff reviewed (`FAQ.md`, `crates/core/flags/complete/rg.zsh`). The `rg.zsh` guard was traced and reproduced with focused zsh execution across three invocation paths (direct `source` without `compdef`, direct `source` with `compdef`, and real `fpath` autoload) and checked against `ci/test-complete`'s invocation method. The new FAQ prose was compared against the file's own bash/fish/PowerShell sibling conventions and reproduced with focused zsh execution.

**Reviewed:** `855bfa6c` against merge-base `79cbe89d`.

## Findings

- [P2] [must-fix] Fix broken copy-paste `source` snippet in zsh FAQ — anchor [`FAQ.md:135`](https://github.com/BurntSushi/ripgrep/blob/855bfa6cdae4f4fe8762f892fc4957635397083e/FAQ.md?plain=1#L135)
- [P3] [consider] Document that `compinit` must run before the one-line `source` method works — anchor [`FAQ.md:131-136`](https://github.com/BurntSushi/ripgrep/blob/855bfa6cdae4f4fe8762f892fc4957635397083e/FAQ.md?plain=1#L131-L136)
- [P3] [consider] Fix the malformed sentence in the new zsh slowness caveat — anchor [`FAQ.md:138-139`](https://github.com/BurntSushi/ripgrep/blob/855bfa6cdae4f4fe8762f892fc4957635397083e/FAQ.md?plain=1#L138-L139)

## Observations

- The new guard's leading comment describes only the `else` branch's skip-execution behavior, not the `if` branch that calls `_rg "$@"` two lines later. Evidence: `crates/core/flags/complete/rg.zsh:439-443`.

<!-- review-run head=855bfa6cdae4f4fe8762f892fc4957635397083e base-ref=master base-sha=79cbe89deb1151e703f4d91b19af9cdcc128b765 merge-base=79cbe89deb1151e703f4d91b19af9cdcc128b765 workflow=v5b-1 context=fea14e64c218222905fc4b1fc7bde1d1907a2826ffb04195d9add739b148f6a1 issues=BurntSushi/ripgrep#2956 coverage=complete -->

---

## Finding comments (would be posted as inline review comments on the batch above)

### `FAQ.md:135` (RIGHT)

**[P2] [must-fix] Fix broken copy-paste `source` snippet in zsh FAQ**

**Triggers when:** A reader follows the FAQ's instruction to add the `source <(rg --generate complete-zsh)` block to `~/.zshrc` and pastes it verbatim.

**Impact:** The pasted line still starts with `$ `, so zsh reports `command not found: $` at every shell startup and never runs `source`; ripgrep's zsh completions are never loaded via this documented method.

**Change:** In `FAQ.md`, remove the leading `$ ` from that line so it matches the `fpath=($HOME/.zsh-complete $fpath)` block immediately above it, which carries the same "add to your `.zshrc`" instruction and correctly has no prompt prefix.

<!-- finding id=faq/zsh-source-snippet-prompt-prefix head=855bfa6cdae4f4fe8762f892fc4957635397083e priority=P2 action=must-fix blocking=true kind=bug -->

### `FAQ.md:131-136` (RIGHT)

**[P3] [consider] Document that `compinit` must run before the one-line `source` method works**

**Triggers when:** `source <(rg --generate complete-zsh)` runs in a `.zshrc` before `compinit` has been called, or when `compinit` never runs.

**Impact:** zsh instead fails with `command not found: _arguments`, and ripgrep's completions never load, with no hint in the FAQ that ordering relative to `compinit` matters.

**Change:** Add a short caveat to this paragraph noting that the line must come after `compinit` has run in the same shell startup file.

Closing this without action is a correct response.

<!-- finding id=faq/zsh-source-missing-compinit-precondition head=855bfa6cdae4f4fe8762f892fc4957635397083e priority=P3 action=consider blocking=false kind=requirement -->

### `FAQ.md:138-139` (RIGHT)

**[P3] [consider] Fix the malformed sentence in the new zsh slowness caveat**

**Triggers when:** A reader parses the sentence "Note though that while this approach is easier to setup, is generally slower than the previous method, and will add more time to loading your shell prompt." as a single grammatical unit.

**Impact:** The sentence omits a subject after the first comma and uses "setup" where the verb "set up" is needed, reading as a run-on with a dangling clause; the intended meaning is still recoverable from context.

**Change:** Rewrite as, e.g., "Note, though, that while this approach is easier to set up, it is generally slower than the previous method and will add more time to loading your shell prompt."

Closing this without action is a correct response.

<!-- finding id=faq/zsh-note-grammar head=855bfa6cdae4f4fe8762f892fc4957635397083e priority=P3 action=consider blocking=false kind=maintainability -->
