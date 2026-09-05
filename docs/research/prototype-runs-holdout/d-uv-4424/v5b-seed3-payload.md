**Approved (advisory)** — no findings.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Expose the existing internal `ToolchainPreference` enum (added in #4416) as a `--toolchain-preference` CLI flag and `tool.uv.toolchain-preference` config option, so users can force managed-only, system-only, or mixed-preference Python toolchain discovery.

**Issue fit:** Met — no linked issue; the PR body's own two stated additions (the CLI flag and the config option) are both implemented and threaded through every command that previously hardcoded a toolchain preference.

**Coverage:** Complete merge-base diff reviewed (22 files, +178/-36); parameter threading verified at all 9 call sites in `main.rs`, the `Combine`/precedence logic in `settings.rs`, the Cargo feature wiring for the new `clap`/`schemars` derives, and `uv.schema.json` traced field-by-field against the Rust enum. Static review only — no build, `cargo`, or tests were run (offline, no-execution sandbox); reasoning proceeded entirely from source and existing test snapshots.

**Reviewed:** `a2e6b9c` against merge-base `e783a799`.

## Observations

- `find_interpreter` narrows its interpreter search from `EnvironmentPreference::Any` to `EnvironmentPreference::OnlySystem`, matching the convention already used at the other environment-creation call sites in `venv.rs` and documented in `toolchain.rs`. Evidence: `crates/uv/src/commands/project/mod.rs:187`, `crates/uv-toolchain/src/toolchain.rs:44`.
- `--toolchain-preference` carries no `env` attribute, unlike the sibling `value_enum` global options `--index-strategy`, `--keyring-provider`, and `--link-mode`, and unlike the boolean globals `--native-tls` and `--offline` that sit beside it in `GlobalArgs`. Evidence: `crates/uv/src/cli.rs:94`, `crates/uv/src/cli.rs:79`.
- No test in the diff or the existing suite exercises the `Commands::Project(_) | Commands::Toolchain(_) | Commands::Tool(_)` branch of `default_toolchain_preference`, which forces `PreviewMode::Enabled` regardless of the real `--preview` flag. Evidence: `crates/uv/src/settings.rs:69`, `crates/uv/tests/show_settings.rs:29`.

<!-- review-run head=a2e6b9c6bd0257510240886549ba9e3623299739 base-ref=main base-sha=e783a79955a3a4eb6a4c546f51f89e88b64047bb merge-base=e783a79955a3a4eb6a4c546f51f89e88b64047bb workflow=v5b-1 context=b647922cbc9c7a5f46ddadeba537c3e076f16f9262d6121c2b2ff0edfa233889 issues=none coverage=complete -->
