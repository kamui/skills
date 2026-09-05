**Approved (advisory)** — 0 must-fix findings, 0 open questions.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Expose the internal `ToolchainPreference` option (added in #4416) as the `--toolchain-preference` CLI flag and the `tool.uv.toolchain-preference` configuration key, plumbed through every command that discovers or creates a Python toolchain.

**Issue fit:** No linked issue; the pull request body is the only statement of intent. Both stated capabilities are met — the CLI flag and configuration key are present with matching kebab-case values, and both `only-managed` and `only-system` opt-outs are available.

**Coverage:** Complete merge-base diff reviewed across all 22 changed files (Rust sources, `Cargo.lock`/`Cargo.toml`, one test file, and the generated `uv.schema.json`), including every call site that plumbs the new parameter, the derive-macro and schema consistency of the new enum, and the resolution/`Combine` logic for the new setting. No repository guidance files (`AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`) apply to any changed path.

**Reviewed:** `a2e6b9c` against merge-base `e783a799`.

## Observations

- `find_interpreter`'s fallback discovery narrows from `EnvironmentPreference::Any` to `EnvironmentPreference::OnlySystem`, excluding active or discovered virtual/conda environments when the project's own environment is insufficient, a change the pull request description does not mention. Evidence: `crates/uv/src/commands/project/mod.rs:187`, `e783a79955a3a4eb6a4c546f51f89e88b64047bb:crates/uv/src/commands/project/mod.rs:186`.

<!-- review-run head=a2e6b9c6bd0257510240886549ba9e3623299739 base-ref=main base-sha=e783a79955a3a4eb6a4c546f51f89e88b64047bb merge-base=e783a79955a3a4eb6a4c546f51f89e88b64047bb workflow=v5b-1 context=b647922cbc9c7a5f46ddadeba537c3e076f16f9262d6121c2b2ff0edfa233889 issues=none coverage=complete -->
