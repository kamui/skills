**Mode: retrospective review of an already-merged pull request.** `astral-sh/uv#4424` merged on 2024-06-20T18:42:09Z; this review was run after the fact, posting identity `kamui` (not the author), and publication is disabled for this run — the review below is rendered exactly as it would be submitted (one `COMMENT` review, body plus line comments), and stops short of any write.

**Needs Information** — 0 blocking findings, 1 open question.

Code: Findings — 1 optional. Requirements: Waiting for information (issue alignment: unavailable) — an explicit review-record deferral is open on the flag's naming.

Reviewed `a2e6b9c6b` against `main` (merge-base `e783a799`). Coverage: complete.

This change mechanically threads a new `toolchain_preference` value through every interpreter-discovery call site the diff touches to expose the CLI flag and config key described in the pull-request body, and every behavioral claim the body makes checks out against the code. One line inside that threading — `find_interpreter`'s fallback search, shared by `lock`/`add`/`sync`/`run` — quietly narrows from accepting any virtualenv-sourced interpreter to system-only; the body never mentions it and no test exercises the changed path, but it is non-blocking because the crate's own documented guidance already recommended the tighter setting. The one open item is the flag's own name and value vocabulary, which the author explicitly left unsettled for later since the surface is preview-gated.

- [Code] [consider] [P2] — `find_interpreter` narrows discovery to `OnlySystem`, dropping the active-venv fallback — anchor [`crates/uv/src/commands/project/mod.rs:187`](https://github.com/astral-sh/uv/blob/a2e6b9c6bd0257510240886549ba9e3623299739/crates/uv/src/commands/project/mod.rs?plain=1#L187)

**[Code] [consider] [P2] `find_interpreter` narrows discovery to `OnlySystem`, dropping the active-venv fallback**

[`crates/uv/src/commands/project/mod.rs:187`](https://github.com/astral-sh/uv/blob/a2e6b9c6bd0257510240886549ba9e3623299739/crates/uv/src/commands/project/mod.rs?plain=1#L187) — the call `Toolchain::find_or_fetch(python_request, EnvironmentPreference::OnlySystem, toolchain_preference, client_builder, cache)` replaces the prior `EnvironmentPreference::Any`. `satisfies_environment_preference` (`crates/uv-toolchain/src/discovery.rs:513-519`) rejects any interpreter sourced from a virtualenv once the preference is `OnlySystem`, and `python_executables` (`crates/uv-toolchain/src/discovery.rs:353-361`) never even chains in the active-environment source under `OnlySystem`, whereas `Any` (`discovery.rs:485`) accepted it. Every other call site this diff touches left its `EnvironmentPreference` argument unchanged — `crates/uv/src/commands/project/run.rs:145`'s own direct `find_or_fetch` call keeps `EnvironmentPreference::Any` — so this is the sole environment-preference behavior change bundled into a diff whose stated purpose is exposing `toolchain-preference`. `find_interpreter` is used directly by `lock.rs:51` and, via `init_environment`, by `add`/`sync`/`run`, so all four commands inherit it. No test in `crates/uv/tests/` exercises this path with `VIRTUAL_ENV` set, and neither the commit message nor the diff carries a comment explaining the narrowing — consistent with an unreviewed side effect of an otherwise mechanical refactor. The crate's own doc comment on `Toolchain::find` (`crates/uv-toolchain/src/toolchain.rs:38-40`, unchanged by this diff) already recommends `OnlySystem` "in most cases," which is why this lands `consider` rather than `must-fix`: the tightening plausibly moves the code toward its own documented recommendation rather than away from correct behavior, and no test result or user report demonstrates the consequence firing.

**Triggers when**: a project has no `.venv` (or one that doesn't satisfy `Requires-Python`), no `--python`/`.python-version` is given, and the user is currently inside a foreign but version-compatible activated virtualenv (common in minimal containers, CI images that ship only a venv Python on `PATH`, or a manually `source`d unrelated venv). Running `uv lock`, `uv add`, `uv sync`, or `uv run` will no longer accept that virtualenv's interpreter as a candidate and will instead search only for a genuine system/managed interpreter, which can fail to find one where the old `Any` preference would have succeeded.

**Change**: at `crates/uv/src/commands/project/mod.rs:187`, either restore `EnvironmentPreference::Any` to preserve the prior discovery behavior, or, if the tightening to `OnlySystem` is intentional, add a comment at the call site explaining the rationale (consistent with the doc comment on `Toolchain::find`) and a regression test exercising `lock`/`add`/`sync`/`run` inside an active foreign virtualenv.

Closing this without action is a correct response.

<!-- finding id=code/project-mod-rs/find-interpreter-onlysystem axis=code action=consider priority=P2 head=a2e6b9c6bd0257510240886549ba9e3623299739 -->

## Observations

These are accurate observations, not findings — no action is requested.

- `crates/uv/Cargo.toml:36`'s `uv-toolchain = { workspace = true, features = ["clap", "schemars"]}` is missing a space before the closing brace, unlike its neighboring dependency lines.
- `crates/uv/src/cli.rs:94`'s new `--toolchain-preference` flag carries no `env = "UV_..."` binding, unlike sibling global flags `--native-tls` (`UV_NATIVE_TLS`) and `--preview` (`UV_PREVIEW`).
- `crates/uv/src/commands/project/run.rs:145` deliberately keeps `EnvironmentPreference::Any` in `uv run`'s second, direct `find_or_fetch` call, so `uv run` now runs two toolchain-discovery paths (one through `find_interpreter`/`init_environment`, one direct) that disagree on whether a foreign active virtualenv is eligible.

## Open questions

**[Question] Should `--toolchain-preference` / `tool.uv.toolchain-preference` keep this name and value vocabulary?**

The flag and config key ship as `--toolchain-preference` / `tool.uv.toolchain-preference` with values `only-managed`, `prefer-installed-managed`, `prefer-managed`, `prefer-system`, `only-system` ([`crates/uv/src/cli.rs:94`](https://github.com/astral-sh/uv/blob/a2e6b9c6bd0257510240886549ba9e3623299739/crates/uv/src/cli.rs?plain=1#L94), [`crates/uv-toolchain/src/discovery.rs:58-71`](https://github.com/astral-sh/uv/blob/a2e6b9c6bd0257510240886549ba9e3623299739/crates/uv-toolchain/src/discovery.rs?plain=1#L58-L71)). In the pull request's own conversation, `BurntSushi` raised naming concerns — whether a shorter CLI name would be preferable, and that `--toolchain-preference prefer-system` repeats "prefer" — and `zanieb` (the author) replied "I'm fine adjusting this later if we need to since it's in preview." (2024-06-20T17:27:06Z), postponing the decision rather than resolving it. No repository rule settles the naming on its own, and the vocabulary is user-facing and not trivially grep-and-replace once released. If the name or vocabulary is expected to change before the feature leaves preview, a tracking note would tell the next reader not to build on the current spelling; if it is now considered settled, saying so here would close the thread this pull request's own conversation left open.

**Change no code for this.** Answer it, or say what would settle it.

<!-- finding id=question/toolchain-preference-naming action=question head=a2e6b9c6bd0257510240886549ba9e3623299739 -->

<!-- review-run workflow=v2a-1 head=a2e6b9c6bd0257510240886549ba9e3623299739 base-ref=main base-sha=e783a79955a3a4eb6a4c546f51f89e88b64047bb merge-base=e783a79955a3a4eb6a4c546f51f89e88b64047bb issues=none coverage=complete -->
