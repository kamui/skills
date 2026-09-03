# Prototype run data — v2, v3, v4, v5 against `tokio-rs/tokio#7757` (test 3)

> **Promotion status:** “v5” is the historical prototype name used by this record. PR #17 promoted that workflow to `skills/code-review-publish` on `main`; new experiments should invoke `/code-review-publish` without the `-5` suffix. **Superseded 2026-09-03:** PR #42 replaced that skill with **v5a**, so `/code-review-publish` now invokes v5a, not the v5 workflow this record tests. `skills/code-review-publish-legacy` is the v1 legacy reviewer, and v5 is no longer on `main` — pin it from `571f31d`.

**2026-09-01.** Raw outputs and metadata from a third controlled comparison of the same four
code-review prototypes against a different pull request. **Data only** — the analysis of this run
lives in [`evaluation.md`](evaluation.md).
The first two comparison sets live in
[`../prototype-runs-2026-09-01-test-1/`](../prototype-runs-2026-09-01-test-1/) and
[`../prototype-runs-2026-09-01-test-2/`](../prototype-runs-2026-09-01-test-2/).

## The target

[`tokio-rs/tokio#7757`](https://github.com/tokio-rs/tokio/pull/7757) — "rt: improve spawn_blocking
scalability with sharded queue". Author `alex` (Alex Gaynor), a long-standing external contributor,
not a maintainer. **Merged** 2026-04-10 after four months of review. Head branch (unmerged,
force-fetched by SHA — see below), base `master`.

Run identity, pinned once and given identically to all four runs:

| | |
| --- | --- |
| head | `9de7950e59f8acea412600c2102ab592c419483a` |
| base ref | `master` (pinned locally to the merge-base) |
| base SHA / merge-base | `43134f1e5784993eb4fb3863933d74ac9e28f598` |
| diff | 6 files, +340/−126, two commits (`11cf7b5d2`, `9de7950e5`) |
| originating issue | [#2528](https://github.com/tokio-rs/tokio/issues/2528) "Heavy contention on blocking", closed by this PR's body |
| prior review state | 52 review-comment threads across 5 participants (author + 4 maintainers) over 4+ months; one `APPROVED` review (`Darksonn`); one raised-then-not-carried-forward design concern about nested locking (`ADD-SP`) |
| posting identity | `kamui`, who did NOT author the PR and has zero prior comments/reviews anywhere on it → ordinary first review, `COMMENT` event |

Changed-file manifest:

```
M	spellcheck.dic                              (+3 −1)
M	tokio/src/runtime/blocking/mod.rs           (+2 −0)
M	tokio/src/runtime/blocking/pool.rs          (+95 −119)
A	tokio/src/runtime/blocking/sharded_queue.rs (+238, new file)
M	tokio/src/runtime/context.rs                (+1 −1)
M	tokio/src/util/rand.rs                      (+1 −5)
```

**This target differs from tests 1 and 2 in a way that matters more than any prior difference: it
has a known, independently verifiable ground-truth defect.** The reviewed head already contains a
second commit that fixed two concurrency bugs introduced by the first (lost condvar wakeups;
orphaned tasks on shutdown via one code path). What none of the commits fixed, and what human review
did not catch across 52 comment threads and an eventual approval, is that the same "orphaned task"
bug class survives in two of `spawn_task`'s three post-push branches. **This PR was merged, caused a
real production hang, and was reverted six days later** (`tokio-rs/tokio#8057`, "rt: revert #7757 to
fix regression in `spawn_blocking`", citing `tokio-rs/tokio#8056`); a corrected, opt-in re-land
shipped four months after that (`tokio-rs/tokio#8337`). This history is independently confirmed
(see [Methodology note: hindsight contamination](#methodology-note-hindsight-contamination) below) —
this is not a synthetic or injected bug, it is the actual defect that shipped.

## Conditions held constant

- Each run got its own offline clone (`/tmp/tokio-review/run-v2` … `run-v5`) of a single local bare
  mirror of `tokio-rs/tokio`, with `origin` repointed to that local mirror's filesystem path (not
  `github.com`), `master` force-set to the merge-base SHA, and the PR head checked out on branch
  `review-head`. No run's `origin` could reach GitHub.
- Phase 1 (target resolution) was done once by the orchestrator and handed to every run identically
  as a single packet file: pinned run identity, verified diff manifest, the originating issue and PR
  body verbatim, both commit messages verbatim (including an explicit note that commit 2's fixes were
  already applied and should not be rediscovered as if still broken), the prior-review-state summary,
  and the run conditions.
- Publication was disabled for all four runs, and no run had forge write credentials for
  `tokio-rs/tokio` regardless.
- Network access (`git fetch`, `git pull`, `gh`, any other network call) was forbidden in all runs;
  builds and test/loom/miri execution were forbidden (they create artifacts and this is a Rust
  workspace where a build is expensive), so review was entirely static.
- Each prototype's own reference documents were treated as authoritative and its phase structure
  followed as written, including its own fan-out and verification policy.
- **Harness and model:** every run (orchestrator sub-agent and any further sub-agents it spawned) ran
  as a Claude Code `general-purpose` agent via the `Agent` tool, at this session's default model
  (Claude Sonnet 5). Where a skill's own architecture called for further fan-out (parallel axis
  finders, a fresh-context verifier), the run's own top-level agent spawned those itself via the same
  `Agent` tool, matching how tests 1 and 2 had each skill's orchestrator spawn its own sub-agents
  under opencode's `task` tool.
- **Harness difference vs both prior tests:** unlike test 1 (Claude Code reporting token counts) or
  test 2 (opencode reporting none), this harness reports **per-sub-agent** token and tool-use counts
  reliably (via each `Agent` call's own usage block) but only for sub-agents the orchestrator directly
  spawns — a run's own top-level tool-use count is self-reported by that run, not independently
  metered. Wall-clock spans are self-measured by each run via `date -u`, cross-checked against the
  background-task dispatch/completion timestamps observed by the orchestrator.

## Methodology note: hindsight contamination

**The local mirror clone was not truncated to pre-merge history.** It was cloned fresh from
`github.com/tokio-rs/tokio` at experiment time (2026-09-01), so — although each run's own `master`
branch was pinned to the merge-base and the PR head was fetched by exact SHA — the mirror's other
refs (in particular `master`'s later history) contain everything that happened *after* this PR
merged, including the emergency revert (`56aaa43e`, `tokio-rs/tokio#8057`) and the eventual correct
re-land (`8b13642a`, `tokio-rs/tokio#8337`). Nothing in the phase-1 packet mentioned the revert or
pointed any run at post-merge history.

**v4 found and used this history anyway**, via an incidental `git log --all -- <path>` while checking
whether the new file had prior references. It treated this as legitimate local evidence (no network
call was made — the objects were already present) and cited the revert commit's own message as
"decisive history evidence" for its finding, which is defensible under the rubric's explicit
endorsement of history as falsification/confirmation material, but is not something a contemporaneous
reviewer working forward-only from the merge-base could have had. v4's *mechanism* was independently
derived from static tracing before the history was found (see [evaluation.md](evaluation.md)), so the
history corroborated rather than manufactured the finding — but the confidence and P0 priority v4
assigned are stronger, and more certain, than the other three runs could reach by construction.
**v2, v3, and v5 show no evidence of consulting this history**; their reports rest entirely on static
analysis of the diff and the pre-PR code via the pinned merge-base. This is disclosed here rather than
scrubbed, because the four-way comparison in [evaluation.md](evaluation.md) treats it as a load-bearing
fact, not an incidental detail — a repeat of this experiment should truncate the mirror's history at
the merge-base to prevent it.

## What differs between the runs

Only the skill under test:

| | v2 (PR #14) | v3 (PR #13) | v4 (PR #16) | v5 (PR #17) |
| --- | --- | --- | --- | --- |
| Architecture | axis finder(s) in parallel + mandatory fresh-context verifier when candidates exist | 1 integrated reviewer, self-falsification | 1 integrated reviewer + conditional fresh-context verifier | 1 integrated reviewer + consequence-triggered fresh-context verifier |
| Verification | always (when finders return candidates) | only for high-risk/large/coupled changes | mandatory for `must-fix`, security, data-loss, contract changes | mandatory for `must-fix` and enumerated consequential risks; artifact names alone do not trigger |

On this PR, unlike test 2, **every run's verifier fired** — all four raised at least one candidate
that met their own must-fix/high-risk trigger, so unlike test 2 the fresh-context-verification
machinery is fully observed here in all four architectures.

## Files

- `v2-run.md` — two parallel axis finders + verifier, full output and metadata
- `v3-run.md` — integrated reviewer + conditional verifier, output and metadata
- `v4-run.md` — integrated reviewer + mandatory verifier, output and metadata
- `v5-run.md` — integrated reviewer + consequence-triggered verifier, output and metadata
- `comparison-data.md` — side-by-side metadata table
- `evaluation.md` — the analysis of this run

No `publication-decision.md`: nothing was published; all four runs were data-only (no forge write
credentials for `tokio-rs/tokio` existed regardless of the skills' own decisions).

## Reproducing

The pinned inputs and run files permit a replay against the same head, **provided the local mirror's
history is truncated to the merge-base** (see the hindsight-contamination note above) to keep the
comparison fair to a contemporaneous reviewer. The PR is merged and its regression/revert history is
now public record, so a replay done today cannot fully un-know what the actual outcome was — the
mirror-truncation step only prevents the *reviewing agent* from directly reading it out of local git
objects.

See [`addendum-2026-09-03.md`](addendum-2026-09-03.md) for the 2026-09-03 v2a/v5a re-test against this same pinned target, run on Sonnet 5 with the mirror **truncated at the merge-base** — which closes the hindsight-contamination problem this README discloses above. Headline: v5a found the ground-truth defect and its verifier corrected the fix to the invariant level; v2a missed it, explicitly acquitting the two branches that carry it, and published a different (also verifier-confirmed) stranding defect instead. See [`v2a-run.md`](v2a-run.md) and [`v5a-run.md`](v5a-run.md).

The aggregate analysis covering this directory alongside every other run recorded through 2026-09-03 — the change-by-change scorecards for v2a and v5a, the pole comparison, the regression watch, and the next-experiment recommendation — is [`../prototype-runs-aggregate-tests-1-4-v2a-v5a.md`](../prototype-runs-aggregate-tests-1-4-v2a-v5a.md).
