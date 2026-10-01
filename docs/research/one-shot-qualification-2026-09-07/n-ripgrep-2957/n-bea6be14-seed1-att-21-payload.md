# Review payload — `BurntSushi/ripgrep#2957`

Cell `n-bea6be14-seed1`, attempt `att-21`. Retrospective review of a merged pull request; publication disabled (see the run report's Mechanism checklist for the "Mode" derivation). Posting identity `kamui`, event `COMMENT` (advisory only — never authorized to gate, and merged targets never gate anyway). Rendered exactly as `scripts/validate_review.py --emit-batch` would submit it in a live run.

## Summary (posted as the review body)

**Approved (advisory)** — 0 must-fix findings, 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Let zsh users dynamically source ripgrep's completion script (`source <(rg --generate complete-zsh)`) instead of only writing it to a file on `fpath`, and document that option alongside a slower-startup caveat.

**Issue fit:** Met — issue #2956's `source <(rg --generate=complete-zsh)` error (`_arguments:comparguments:327: can only be called from completion function`) is gone: the script now calls `_rg "$@"` directly only when it is actually executing as the completion function (or when `compdef` is unavailable), and otherwise registers itself with `compdef _rg rg` instead of invoking completion internals outside a completion context. Confirmed by sourcing the script before and after this change, with and without `compinit` having run, in a disposable zsh (see run report for commands and output).

**Coverage:** Complete merge-base diff reviewed (`FAQ.md`, `crates/core/flags/complete/rg.zsh`); `ci/test-complete`'s argument-extraction path (`get_comp_args`) exercised directly against both the base and head completion scripts and confirmed byte-identical; no CI log was available offline to reuse instead.

**Reviewed:** `855bfa6c` against merge-base `79cbe89d`.

## Findings

- [P3] [consider] Fix the dropped subject in the zsh completion caveat — anchor [`FAQ.md:138-139`](https://github.com/BurntSushi/ripgrep/blob/855bfa6cdae4f4fe8762f892fc4957635397083e/FAQ.md?plain=1#L138-L139)

<!-- review-run head=855bfa6cdae4f4fe8762f892fc4957635397083e base-ref=master base-sha=79cbe89deb1151e703f4d91b19af9cdcc128b765 merge-base=79cbe89deb1151e703f4d91b19af9cdcc128b765 workflow=v5b-10 context=fea14e64c218222905fc4b1fc7bde1d1907a2826ffb04195d9add739b148f6a1 issues=BurntSushi/ripgrep#2956 coverage=complete -->

## Inline comment 1 of 1 — `FAQ.md:138-139` (RIGHT)

**[P3] [consider] Fix the dropped subject in the zsh completion caveat**

**Triggers when:** A reader reaches the new "Or if you'd prefer to load and generate completions at the same time" paragraph in the zsh completion section of the FAQ.

**Impact:** The caveat sentence has no subject for its second clause ("...is easier to setup, is generally slower..."), so it reads as a broken run-on in otherwise carefully written documentation.

**Change:** In `FAQ.md`, restore the missing subject:

```suggestion
Note though that while this approach is easier to set up, it is generally
slower than the previous method and will add more time to loading your shell
prompt.
```

Closing this without action is a correct response.

<!-- finding id=faq/zsh-source-caveat-grammar head=855bfa6cdae4f4fe8762f892fc4957635397083e priority=P3 action=consider blocking=false kind=maintainability -->

## Open questions

*(none)*

## Observations

*(none — no accurate fact both failed admission only on meaningful/proven consequence and cleared the Observations bar; see the run report's private ledger for what was considered and why each was dropped outright instead)*
