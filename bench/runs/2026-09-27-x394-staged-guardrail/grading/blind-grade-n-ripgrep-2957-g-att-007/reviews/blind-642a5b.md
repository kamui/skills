# Review blind-642a5b

### Item 1
Location: (no file)
Claim: The classic fpath-install completion path (`autoload`-ing `_rg` from a directory on `$fpath`) is preserved: the new `[[ $funcstack[1] == _rg ]]` branch still calls `_rg "$@"` directly in that case, matching pre-change behavior.
Consequence: crates/core/flags/complete/rg.zsh:438-443 (diff, RIGHT); confirmed by focused test.
Fix: —

### Item 2
Location: (no file)
Claim: The change also fixes an unrelated, pre-existing typo in FAQ.md's completions intro ("completes" → "completions"), bundled into the same commit.
Consequence: FAQ.md:97 (diff, RIGHT).
Fix: —
