# Scorecard: n-ripgrep-2957, mapping v1

Register v2 (1a98c37fb18b), rubric v1, scored at 2026-09-27T07:10:28Z.

Adjudicator: headless Claude Code 2.1.282, --safe-mode, fresh home, claude-opus-5-5 at high, single-threaded; prompt sha256 2b02a88340b242dce68215aecb969aa319089c84ef317db07d4559d3d44f8ed3; session 33e58001-ae1d-4887-92f8-12e3b7c26cc5; read audit clean.

## att-002 (review-code-sonnet-high), blind-22c34d

Verdict 'Approved'; completion completed; approved on buggy True; zero recovery True; false clean True.

- item-0: `non-material`, fix n/a, priority error False, group none. Quote: "The clause after the first comma drops its subject (\"while this approach is easier to setup, is generally slower...\"), so the sentence reads as ungrammatical". True: the added FAQ.md text at head reads "Note though that while this approach is easier to setup, is generally slower than the previous method". But the register's non_defects list rules this exact claim ('There is a redundant or awkward sentence in the FAQ ("is easier to setup, is generally slower...")') a cosmetic grammar nit. It does not touch GT-n1, the stray `$ ` prefix on the `source <(rg --generate complete-zsh)` block two lines above, so it is an accurate observation below the threshold.
- item-1: `non-material`, fix n/a, priority error n/a, group none. Quote: "The diff also fixes an unrelated pre-existing typo in the bash/fish intro sentence (\"generate completes\" -> \"generate completions\")". Confirmed by git diff main...review-head -- FAQ.md at line 97 (-completes / +completions). This is an accurate observation about a benign change, with no defect asserted, so it is non-material.

## New candidates

None.
