**Mode: retrospective review of an already-merged pull request.** This reviews an already-merged change (`astral-sh/uv#4424`, merged 2024-06-20T18:42:09Z); publication is disabled for this run — the review below is rendered exactly as it would be submitted (`event: COMMENT`) and stops there, nothing is posted.

**Needs Information** — 0 blocking findings, 2 open questions.

Code: Passed. Requirements: Waiting for information (issue alignment: unavailable — no originating issue; assessed against the pull-request body's claims).

Reviewed `a2e6b9c6b` against `main` (merge-base `e783a799`). Coverage: complete.

This change wires the previously internal `ToolchainPreference` enum (added in #4416) onto a new `--toolchain-preference` CLI flag and a `tool.uv.toolchain-preference` config key, threading the resolved preference into every toolchain-discovery call site the pull request touches. Both axes traced the wiring end to end against the pull-request body's claims and found it correct and complete, with no code defect surviving review. What holds this at Needs Information is not a bug but an open naming decision the author explicitly deferred mid-review: the flag/key name and the `prefer-*` value vocabulary were both left for a later bikeshed "since it's in preview," and neither has a documented repository convention that resolves it from the code alone.

No findings survived review on either axis — a clean result, not a suspicious one.

**Counts** — Code: 0 findings (0 must-fix, 0 consider). Requirements: 0 findings (0 must-fix, 0 consider), 5 requirements met, 0 not met, 2 unverifiable. Questions: 2. Refuted: 0.

## Observations

These are accurate observations, not findings — no action is requested.

- `find_interpreter`'s `Toolchain::find_or_fetch` call now passes `EnvironmentPreference::OnlySystem` instead of `EnvironmentPreference::Any` (`crates/uv/src/commands/project/mod.rs:187`), which changes `uv add`/`remove`/`sync`/`run`/`lock` interpreter discovery to reject virtualenv/conda-sourced interpreters it previously accepted — but every sibling call site already used `OnlySystem` before this diff, so this brings the one outlier into line with the established convention rather than introducing new behavior.
- The default toolchain preference for every `Project`/`Toolchain`/`Tool` command is now always computed as if `--preview` were enabled, regardless of the actual flag (`crates/uv/src/settings.rs:65`) — a self-disclosed, acknowledged-imperfect stopgap per the adjacent comment, not a silent change.
- The new `--toolchain-preference` flag's help text, "Whether to use system or uv-managed Python toolchains" (`crates/uv/src/cli.rs:91`), undersells the five-value enum it configures (`only-managed`, `prefer-installed-managed`, `prefer-managed`, `prefer-system`, `only-system`), describing a binary choice rather than a preference spectrum.

## Open questions

**[Question] Is `--toolchain-preference` / `toolchain-preference` the final name, or was a shorter name (`--toolchains`) meant to replace it before release?**

[`crates/uv/src/cli.rs:94`](https://github.com/astral-sh/uv/blob/a2e6b9c6bd0257510240886549ba9e3623299739/crates/uv/src/cli.rs?plain=1#L94) ships the flag as `--toolchain-preference`. In this pull request's own conversation, `zanieb` raised renaming it ("Should we bikeshed the name? Should it just be `--toolchains`?") and, after `BurntSushi`'s review raised the same concern, deferred it explicitly: "I'm fine adjusting this later if we need to since it's in preview." No repository rule settles CLI-flag naming, so this cannot be resolved from the code — it is a live, open naming decision on unreleased public surface.

**Change no code for this.** Answer it, or say what would settle it — a maintainer decision on the flag/key name before the option leaves preview.

<!-- finding id=question/cli-rs/toolchain-preference-name action=question head=a2e6b9c6bd0257510240886549ba9e3623299739 -->

**[Question] Should `ToolchainPreference`'s `prefer-*` variants (`prefer-installed-managed`, `prefer-managed`, `prefer-system`) drop the `prefer-` prefix?**

[`crates/uv-toolchain/src/discovery.rs:58`](https://github.com/astral-sh/uv/blob/a2e6b9c6bd0257510240886549ba9e3623299739/crates/uv-toolchain/src/discovery.rs?plain=1#L58) ships the five variants with the `prefer-` prefix on three of them, now made a public, serializable vocabulary by this diff's new `serde`/`clap`/`schemars` derives. In this pull request's own conversation, `zanieb` proposed dropping the prefix ("I guess another option is I drop the `prefer` prefix so we'd have `toolchain-preference = managed | system | only-managed | only-system | installed-managed`... which is pretty reasonable too?"), and `BurntSushi` engaged with the tradeoff without settling it ("I think that's probably okay... wondered whether it might leave folks wondering the difference between `managed` and `only-managed`."). No repository rule settles enum-value naming conventions, so this is unresolved from the code.

**Change no code for this.** Answer it, or say what would settle it — a maintainer decision on the value vocabulary before the option leaves preview.

<!-- finding id=question/discovery-rs/toolchain-preference-vocabulary action=question head=a2e6b9c6bd0257510240886549ba9e3623299739 -->

<!-- review-run workflow=v2a-1 head=a2e6b9c6bd0257510240886549ba9e3623299739 base-ref=main base-sha=e783a79955a3a4eb6a4c546f51f89e88b64047bb merge-base=e783a79955a3a4eb6a4c546f51f89e88b64047bb issues=none coverage=complete -->
