**Approved (advisory)** — 0 must-fix findings, 1 consider finding.

**Mode:** Retrospective review of merged pull request; publication disabled.

**Intent:** Expose the internal `ToolchainPreference` option (added in #4416) as a `--toolchain-preference` CLI flag and `tool.uv.toolchain-preference` config key, threading it through every command that discovers a Python toolchain.

**Issue fit:** No linked issue; the pull-request body is the sole statement of intent and is satisfied — the flag, config key, and JSON-schema entry are wired through the CLI, project, tool, toolchain, and pip-compile commands. Incidentally, a pre-existing `EnvironmentPreference::Any` regression in project-venv creation (introduced by the immediately prior commit, not this change) is restored to `OnlySystem`.

**Coverage:** Complete merge-base diff reviewed (22 files, all `reviewed`); no execution performed, per this run's static-only condition.

**Reviewed:** `a2e6b9c` against merge-base `e783a79`.

## Findings

- [P3] [consider] Scope the download claim in ToolchainPreference's docs — anchor [`crates/uv-toolchain/src/discovery.rs:62`](https://github.com/astral-sh/uv/blob/a2e6b9c6bd0257510240886549ba9e3623299739/crates/uv-toolchain/src/discovery.rs?plain=1#L62)

## Observations

- `crates/uv/tests/show_settings.rs` exercises `toolchain-preference` only at its default value, the same coverage gap as the pre-existing `native-tls`, `offline`, and `preview` globals in that file. Evidence: `crates/uv/tests/show_settings.rs`.

<!-- review-run head=a2e6b9c6bd0257510240886549ba9e3623299739 base-ref=main base-sha=e783a79955a3a4eb6a4c546f51f89e88b64047bb merge-base=e783a79955a3a4eb6a4c546f51f89e88b64047bb workflow=v5b-1 context=b647922cbc9c7a5f46ddadeba537c3e076f16f9262d6121c2b2ff0edfa233889 issues=none coverage=complete -->

---

## Inline comments

### Comment on `crates/uv-toolchain/src/discovery.rs:62`

**[P3] [consider] Scope the download claim in ToolchainPreference's docs**

**Triggers when:** A user runs `uv pip compile`, `uv tool run`, or `uv toolchain find` with `--toolchain-preference prefer-installed-managed` (or `prefer-managed`), and neither a managed nor a system interpreter satisfies the request.

**Impact:** The doc comment this change makes user-facing (via `--help` and `uv.schema.json`) promises uv will "download a managed interpreter", but these three commands call `Toolchain::find`/`find_best` (`crates/uv-toolchain/src/toolchain.rs:49,61`), which are synchronous and never fetch; only `venv`/`add`/`sync`/`lock`/`run`/`remove` route through `find_or_fetch`. A user following the documented behavior on the non-fetching commands gets `Error::NotFound` instead of a download.

**Change:** In `crates/uv-toolchain/src/discovery.rs`, qualify the `PreferInstalledManaged` and `PreferManaged` doc comments (or the shared CLI help text) to state that automatic download only applies to commands that create an environment.

Closing this without action is a correct response.

<!-- finding id=uv-toolchain/toolchain-preference-download-doc head=a2e6b9c6bd0257510240886549ba9e3623299739 priority=P3 action=consider blocking=false kind=maintainability -->

