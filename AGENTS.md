## Agent skills

### Subagent model selection

Unless the user requests otherwise, default subagents of a top-tier immediate parent to its provider's next lower capability tier. Resolve tiers from the current model catalog or provider docs. Preserve reasoning effort where supported. For other parents, keep harness defaults. If model selection is unsupported or the target tier is unavailable or unclear, keep harness defaults and briefly report the limitation.

### Issue tracker

Issues and specs live in GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default five-role label vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

Use the single-context layout. See `docs/agents/domain.md`.

### Shared protocol vocabulary

`code-review-publish/references/review-protocol.md` and `resolve-review/references/addressing-protocol.md` share the reply, disposition, verdict, and thread-state vocabulary. Skills install one at a time, so neither can point at the other's copy; a change to that vocabulary lands in both.

### Runtime review dependency

`review-code-publish` and `implement-publish` require `review-code`; each stops with a named report when it is absent. `finish-it` requires `implement-publish`, `review-code-publish`, `resolve-review`, and `review-code`, and stops with `missing-dependency: <name>` before any write. These are the two named exceptions to installing skills alone. `review-bot` is optional for `review-code-publish`, `code-review-publish`, `audit-code-publish`, and `finish-it`; its absence is a recorded fallback to the authenticated user with gating withheld, never a stop or a third install-alone exception.

### Global skill sync

After successfully pushing or merging a change under `skills/` into `origin/main`, run `scripts/sync-global-skills` and report its result. The script owns installation and provenance-checked removal; do not reproduce those operations by hand.

### Scripts

Skill scripts are standard-library Python 3.9+, invoked as `python3 scripts/<name>.py`; repo tooling is POSIX `sh`. macOS and Linux only. Scripts do mechanical work and the model keeps every review judgment. See `docs/agents/scripts.md` before adding or changing one.
