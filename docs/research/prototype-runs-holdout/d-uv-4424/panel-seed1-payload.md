# Review payload — `astral-sh/uv#4424`, arm v2a (Panel line), seed 1

This file renders the review **exactly as it would have been submitted** via
`gh api --method POST repos/astral-sh/uv/pulls/4424/reviews`, had publication not been disabled for
this retrospective run. It is not posted anywhere. Structure: the review body (as `body`), then the
one line comment that would ride in `comments[]`, each shown with its path/line/side and full
content, per `references/publishing.md` § One review, one call.

---

## Review body (`body`)

**Mode: this is a retrospective review of an already-merged pull request.** Posting identity
`kamui` did not author it and holds no earlier review or comment on it, so this is treated as an
ordinary first review. Publication is disabled for this run; the review below is rendered as it
would be posted, not actually submitted anywhere.

**Incomplete** — 1 optional finding, 1 open question; coverage on the Requirements axis did not
reach `complete` (see Coverage below).

Code: Passed. Requirements: Findings — 1 optional (`consider`); 1 open question; issue alignment
**unavailable** (no originating issue was found — this axis was reviewed against the pull request
body's behavioral claims and non-goals instead, per `requirements-axis.md` § No issue).

Reviewed [`a2e6b9c6b`](https://github.com/astral-sh/uv/commit/a2e6b9c6bd0257510240886549ba9e3623299739)
against `main` (merge-base `e783a799`, identical to the recorded base SHA). **Coverage: incomplete.**
All 22 changed files were inspected and marked `reviewed`/`ignored` with reasons by both finders, and
every restated claim was sorted and every changed contract swept — but the Requirements-axis finder's
report did not reach the skill's required machine-readable shape within the one re-dispatch this
skill's contract authorizes: two disposition-ledger rows (the naming-deferral question and the
documentation sweep's negative result) still carry a bare-file-path evidence pointer instead of the
required `path:line` or `` `path` § heading `` form after correction. Per `code-review-deep-publish`'s
own rule, this leaves the Requirements axis incomplete; nothing it found is withheld on that account
— the finding and the question below are exactly what the axis produced.

This PR threads the `ToolchainPreference` value already added in #4416 through a new
`--toolchain-preference` CLI flag and `tool.uv.toolchain-preference` configuration key, and rewires
roughly ten command entry points to honor it in place of each one's previous hardcoded default — a
faithful, thoroughly-swept refactor with no code-correctness defects found on either axis. The one
thing worth a maintainer's attention is that the same refactor also narrows an unrelated
`EnvironmentPreference` argument in the project-venv fallback path, a scope change the pull request's
own description never mentions; separately, the flag's name and value vocabulary are still explicitly
unsettled per the review record itself. Status is `Incomplete` rather than `Approved` purely on the
mechanical coverage shortfall above, not because anything found here blocks the change.

- [Requirements] [consider] [P2] — `find_interpreter` narrows `EnvironmentPreference::Any` to `OnlySystem`, unrequested by the PR — anchor [`crates/uv/src/commands/project/mod.rs:187`](https://github.com/astral-sh/uv/blob/a2e6b9c6bd0257510240886549ba9e3623299739/crates/uv/src/commands/project/mod.rs?plain=1#L187)

**Counts:** Code — 0 findings, 0 questions. Requirements — 1 finding (0 blocking, 1 optional), 1
question. Total across axes — 1 finding (`consider`, P2), 1 question, 3 observations published (2
dropped at the observations cap — see below), 0 refuted, 0 disputed.

## Observations

These are accurate observations, not findings — no action is requested.

- The narrowed `find_interpreter` call site is one of several `EnvironmentPreference` call sites this
  diff touches; the sibling `uv run --with`/ephemeral-environment lookup in the same file is
  untouched by this diff and still passes `EnvironmentPreference::Any` — `crates/uv/src/commands/project/run.rs:145`.
- `GlobalSettings::resolve`'s per-command-family default for `toolchain_preference` (forcing
  `PreviewMode::Enabled` for `Project`/`Toolchain`/`Tool` commands, the real `--preview` flag for
  everything else) carries an inline `TODO(zanieb)` acknowledging it as a known compromise —
  `crates/uv/src/settings.rs:56-63`.
- `crates/uv/Cargo.toml`'s new `uv-toolchain` features list is missing a space before its closing
  brace, inconsistent with every other entry in the file — `crates/uv/Cargo.toml:36`.

*(2 further observations were raised and dropped at the three-item publication cap; both are
recorded in the run report, marked `observation (unpublished, cap)`, with their evidence pointers:
`crates/uv/tests/show_settings.rs:60` and `PREVIEW-CHANGELOG.md`.)*

## Open questions

**[Question] Is `--toolchain-preference` / `toolchain-preference`'s name and value vocabulary
settled, or still open per the review record?**

The flag is defined at [`crates/uv/src/cli.rs:92-94`](https://github.com/astral-sh/uv/blob/a2e6b9c6bd0257510240886549ba9e3623299739/crates/uv/src/cli.rs?plain=1#L92-L94)
as `--toolchain-preference`, and the same name (kebab-cased) is the `[tool.uv]`/`uv.toml` key. The
pull request's own review record shows this was an active, unresolved bikeshed at merge time:
`BurntSushi` questioned whether a shorter name would suit common CLI use and flagged the
`prefer-system`/`prefer-*` redundancy; `zanieb` proposed dropping the `prefer` prefix entirely
(`toolchain-preference = managed | system | only-managed | only-system | installed-managed`) and,
independently of that specific proposal, said explicitly: *"I'm fine adjusting this later if we need
to since it's in preview."* No decision closing the thread appears in the material available to this
review, and no repository rule (`CONTRIBUTING.md` has no CLI-naming-convention section) settles it by
default. No static reading of the code can determine whether the name shipped here is the one the
maintainers ultimately intend, because the review record itself says it may still change.

**Change no code for this.** Answer it, or say what would settle it: whether the naming bikeshed in
the review thread was ever closed (a later commit renaming the flag/values, or a maintainer statement
ending the discussion) — neither of which is visible in the material pinned to this run.

<!-- finding id=question/cli-rs/toolchain-preference-naming action=question head=a2e6b9c6bd0257510240886549ba9e3623299739 -->

<!-- review-run workflow=v2a-1 head=a2e6b9c6bd0257510240886549ba9e3623299739 base-ref=main base-sha=e783a79955a3a4eb6a4c546f51f89e88b64047bb merge-base=e783a79955a3a4eb6a4c546f51f89e88b64047bb issues=none coverage=incomplete -->

---

## Line comments (`comments[]`)

Would-be `gh api` call shape:

```json
{
  "commit_id": "a2e6b9c6bd0257510240886549ba9e3623299739",
  "event": "COMMENT",
  "body": "<the review body above>",
  "comments": [
    {
      "path": "crates/uv/src/commands/project/mod.rs",
      "line": 187,
      "side": "RIGHT",
      "body": "<comment 1 below>"
    }
  ]
}
```

### Comment 1 — `crates/uv/src/commands/project/mod.rs:187` (RIGHT)

**[Requirements] [consider] [P2] `find_interpreter` narrows `EnvironmentPreference::Any` to `OnlySystem`, unrequested by the PR**

`crates/uv/src/commands/project/mod.rs:187` — the pull request body states only that it "Adds
`--toolchain-preference` and `tool.uv.toolchain-preference` to configure if system or managed
toolchains are preferred. Users can opt-out of managed toolchains or system toolchains entirely as
well" — a claim about the `ToolchainPreference` axis. But `find_interpreter`'s call to
`Toolchain::find_or_fetch` here also changes its unrelated `EnvironmentPreference` argument from
`EnvironmentPreference::Any` to `EnvironmentPreference::OnlySystem`. `EnvironmentPreference` governs
which Python *environments* (virtual vs. system) are eligible discovery sources and is orthogonal to
`ToolchainPreference`, which governs managed vs. system *toolchains*. Nothing in the body, the single
commit message, or the review record mentions this change. `find_interpreter` is called directly by
`lock` and, via `init_environment`, by `add`, `remove`, `run`, and `sync` — five of the eight commands
this pull request touches.

**Triggers when**: a user runs `uv lock`, `uv sync`, `uv add`, `uv remove`, or non-isolated `uv run`
while some virtual environment other than the project's own `.venv` is active or discoverable (for
example `VIRTUAL_ENV` pointing elsewhere, or a `.venv` found walking up the directory tree via
`crates/uv-toolchain/src/discovery.rs`'s `from_environments` chain) and the project's own `.venv`
either doesn't exist yet or doesn't satisfy `requires-python`. Before this change that foreign
environment's interpreter was an eligible discovery source (`Any`); after this change it is excluded
(`OnlySystem`), silently changing which interpreter gets selected to bootstrap the project's own
environment — independent of any `--toolchain-preference` value the user set.

**Change**: either fold the `EnvironmentPreference::Any → OnlySystem` narrowing into the pull
request's stated scope by naming it explicitly in the description (if it was in fact an intended
correctness fix bundled in here — restricting the fallback search to non-venv sources for a *new*
project venv is a defensible tightening, just not the one this PR claims to make), or revert this
one argument to `EnvironmentPreference::Any` and land it separately with its own rationale.

Closing this without action is a correct response.

<!-- finding id=requirements/unrequested/environment-preference-narrowed axis=requirements action=consider priority=P2 head=a2e6b9c6bd0257510240886549ba9e3623299739 -->
