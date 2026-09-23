# Treatment arm freeze

Recorded 2026-09-23T20:43:59Z for [#347](https://github.com/kamui/skills/issues/347), before any treatment cell ran.

- **Treatment revision:** `1684cf4d` (`origin/main` after #346 merged as #353), installed with `git archive 1684cf4 skills/review-code` at `/tmp/rcs-savings/skills/1684cf4/skills/review-code`. It combines #342–#346. Workflow `validate_review.WORKFLOW` is still `v5b-24`.
- **Harness:** Claude Code `2.1.280`, the version the baseline cells ran. The host's default had moved to `2.1.281`, so the launcher ran with `/tmp/rcs-savings/harness-2.1.280/claude` first on `PATH`. That entry is a symlink to the installed `2.1.280` binary, and `claude --version` through it printed `2.1.280 (Claude Code)`. The launch command, model id `claude-sonnet-5` and effort `high` are unchanged.
- **Baseline reuse:** protocol step 3 lets the treatment reuse #341's baseline cells because the harness version, model id and launch command are unchanged. The baseline arm is not rerun: that would repeat a cell.
- **Realization:** `verify` passed with manifest SHA-256 `f7880b94…5a9ca9`. `materialize --root /tmp/rcs-savings/treatment` then `check` passed. As the protocol specifies, the treatment skips the seeded chain's helper replay.

Nothing else in [protocol.md](../protocol.md) changes.

## Amendment: same-session baseline control

Recorded 2026-09-23T20:55:57Z, after the four treatment cells and before any control cell ran.

The treatment workers ran on the same generated briefs as the baseline workers, within 1–10% of their bundle words. Yet worker turns fell from 8–10 to 4–5, and worker thinking fell from 3,655–8,331 tokens to 67–1,082. The harness, model id, effort and launch command are unchanged. So something outside the skill changed between the baseline's 03:45 UTC run and the treatment's 20:44 UTC run, and the reuse condition in step 3 did not hold it constant.

A supplementary **control** arm therefore reruns the baseline skill `d8c2dd9`, in the same session as the treatment, under this protocol. It uses the same pinned harness, a fresh `materialize --root /tmp/rcs-savings/control` with the baseline `check --skill-root` replay, and one attempt per cell in task order. Evidence goes under `control/`. The #341 baseline cells stay the protocol comparison and are neither replaced nor rerun: both baseline sets are reported beside the treatment. The control only separates the interface change from the drift.
