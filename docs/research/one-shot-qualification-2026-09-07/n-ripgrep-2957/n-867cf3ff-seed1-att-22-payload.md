**Approved (advisory)** — clean review; no findings.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Let users source ripgrep's generated zsh completion script directly (`source <(rg --generate complete-zsh)`) without the previous `_arguments: ... can only be called from completion function` error, and document the new option alongside the existing `fpath`-based install method.

**Issue fit:** Met — BurntSushi/ripgrep#2956's exact repro is fixed; the completion function now detects direct sourcing via `$funcstack[1]` and registers itself with `compdef` instead of unconditionally invoking `_arguments` outside completion context.

**Coverage:** Complete merge-base diff reviewed (`FAQ.md`, `crates/core/flags/complete/rg.zsh`); traced both branches of the new `rg.zsh` conditional against base and head with focused zsh scratch scripts (dynamic sourcing with and without `compinit` pre-loaded, and traditional `fpath`/autoload usage); read `ci/test-complete` to confirm it still exercises the file correctly.

**Reviewed:** `855bfa6` against merge-base `79cbe89`.

## Ambiguities

- The rubric's Observations sentence — "Route an accurate fact to `Observations` when it fails finding admission specifically on meaningful or proven consequence" — can be read either to admit a gate-1 (not meaningful) failure as well as a gate-4 (no proven consequence) failure, or to admit gate-4 failures only, matching the paragraph's later gate-4-specific wording (`observation (consequence absent)` / `dropped (consequence unproven)`) and its caution against creating "an observation merely to preserve a dropped candidate." This run applied the narrower, gate-4-only reading: a documentation prose nit that failed only on meaningful impact (`FAQ.md:138`) was dropped rather than published as an observation.

<!-- review-run head=855bfa6cdae4f4fe8762f892fc4957635397083e base-ref=master base-sha=79cbe89deb1151e703f4d91b19af9cdcc128b765 merge-base=79cbe89deb1151e703f4d91b19af9cdcc128b765 workflow=v5b-1 context=fea14e64c218222905fc4b1fc7bde1d1907a2826ffb04195d9add739b148f6a1 issues=BurntSushi/ripgrep#2956 coverage=complete -->
