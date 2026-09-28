# Scorecard: n-ripgrep-2957, mapping v1

Register v2 (1a98c37fb18b), rubric v1, scored at 2026-09-28T03:41:41Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 c59f688015fcb78905ee508a98756d1b76b7759bdf2db570af919bf67c735650; session 732e04e8-58bc-4712-897b-101ba38d1d14; read audit clean.

## att-007 (review-code-sonnet-high-enforced-x394-trimmed), blind-642a5b

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error n/a, group none. Quote: "The classic fpath-install completion path ... is preserved: the new `[[ $funcstack[1] == _rg ]]` branch still calls `_rg "$@"` directly in that case, matching pre-change behavior." This is an accurate confirmation, not a defect claim: clone/crates/core/flags/complete/rg.zsh:441-445 at review-head keeps `_rg "$@"` under the funcstack guard, and the register's first non_defect rules that the autoload dispatch path takes that same branch. It is a true observation that asserts no defect, so it is non-material. It does not touch GT-n1, the stray `$ ` prefix in the FAQ .zshrc block.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "The change also fixes an unrelated, pre-existing typo in FAQ.md's completions intro (\"completes\" → \"completions\"), bundled into the same commit." Verified: `git diff main...review-head -- FAQ.md` shows line 97 changing 'generate completes using' to 'generate completions using', made in commit 855bfa6 alongside the rest of the FAQ rewrite. The claim is accurate but is only a hygiene/scope remark with no consequence, so it is non-material. It does not mention the `$ source <(rg --generate complete-zsh)` block at FAQ.md:135, so it does not recover GT-n1.

## New candidates

None.
