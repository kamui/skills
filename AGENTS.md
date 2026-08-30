## Agent skills

### Issue tracker

Issues and specs live in GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default five-role label vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

Use the single-context layout. See `docs/agents/domain.md`.

### Mirrored reference

`references/review-protocol.md` is byte-identical in `code-review-publish` and `code-review-address`. Skills install one at a time, so neither can point at the other's copy. Edit both together and `diff` them before committing.

### Global skill sync

After successfully pushing or merging a change under `skills/` into `origin/main`, run `scripts/sync-global-skills` and report its result. The script owns installation and provenance-checked removal; do not reproduce those operations by hand.
