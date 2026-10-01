# Review experiment data

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

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

## Methodology note: hindsight contamination

**The local mirror clone was not truncated to pre-merge history.** It was cloned fresh from
`github.com/tokio-rs/tokio` at experiment time (2026-09-01), so — although each run's own `master`
branch was pinned to the merge-base and the PR head was fetched by exact SHA — the mirror's other
refs (in particular `master`'s later history) contain everything that happened *after* this PR
merged, including the emergency revert (`56aaa43e`, `tokio-rs/tokio#8057`) and the eventual correct
re-land (`8b13642a`, `tokio-rs/tokio#8337`). Nothing in the phase-1 packet mentioned the revert or
pointed any run at post-merge history.

## What differs between the runs

Only the skill under test:

| | v3 (PR #13) | v4 (PR #16) | v5 (PR #17) |
| --- | --- | --- | --- |
| Architecture | 1 integrated reviewer, self-falsification | 1 integrated reviewer + conditional fresh-context verifier | 1 integrated reviewer + consequence-triggered fresh-context verifier |
| Verification | only for high-risk/large/coupled changes | mandatory for `must-fix`, security, data-loss, contract changes | mandatory for `must-fix` and enumerated consequential risks; artifact names alone do not trigger |

On this PR, unlike test 2, **every run's verifier fired** — all four raised at least one candidate
that met their own must-fix/high-risk trigger, so unlike test 2 the fresh-context-verification
machinery is fully observed here in all four architectures.

## Files

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
