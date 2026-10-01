# Review packet — `kamui/skills#325` (target (C8), Pinned review input)

Phase 1 (target resolution) has already been performed by the orchestrator and is reproduced here in
full. **Do not attempt to re-resolve the target over the network — you have no network access.**
Treat every fact in this packet as authoritative pinned input. This packet is byte-identical for every
arm and replicate on this target.

## 1. Pinned run identity

| | |
| --- | --- |
| Pull request | [`kamui/skills#325`](https://github.com/kamui/skills/pull/325) — "Move review-code's first-review eligibility guard into forge_packet.py" |
| Author | `kamui` (association at fetch time: `OWNER`) |
| Repository URL (`summary.repository_url`) | `https://github.com/kamui/skills` |
| Head SHA | `0ea287f0c07fda09b9d063612353dcef37f38063` (local branch `review-head`, checked out) |
| Base ref | `main` (local branch `main`, force-pinned to the merge-base) |
| Base SHA (as recorded on the pull request) | `160d1201bed57d96de6fc8b1ae657bd098aa2de6` |
| Merge-base | `160d1201bed57d96de6fc8b1ae657bd098aa2de6` (identical to the base SHA) |
| Diff | 6 files, +119 / −49, 2 commits |
| `state` | `MERGED` |
| `merged` | **`true`** (merged 2026-09-22T20:24:30Z) |
| `isDraft` | `false` |
| Originating issue(s) | none — the PR body carries no closing reference; `issues=none` unless the dispatch supplies a spec |
| Posting identity | `kamui`, who did NOT author the PR and has no prior comments or reviews on it → an ordinary first review by a third party, event `COMMENT`; the target is merged, so this is a **retrospective review with publication disabled** |

Compute the diff as `git diff main review-head` (the `main` branch is pinned to the merge-base, so two-dot and three-dot are identical here).

## 2. Changed-file manifest (verified against the pinned SHAs from the mirror)

```
M  CHANGELOG.md                                                           (+2    −0)
M  skills/review-code/DESIGN.md                                           (+8    −0)
M  skills/review-code/references/pull-request-target.md                   (+3    −46)
M  skills/review-code/scripts/forge_packet.py                             (+104  −3)
M  skills/review-code/scripts/test_command_chains.py                      (+1    −0)
M  skills/review-code/scripts/test_run_events.py                          (+1    −0)
```

## 3. Pull-request body, verbatim

```
Rank 7 of the 2026-09-20 prose-eviction table.

The pull-request root invocation in `references/pull-request-target.md` carried a 42-line Python heredoc that decides whether step 2's first-review context build can run at once. It is now `scripts/forge_packet.py eligibility`, which already reads the saved forge pages. The block calls it through an absolute `<forge-packet-script>` path, the same way it calls `run_events.py` and `review_context.py`, so it still runs in the reviewed repository.

- Conditions, deferral reasons, verdict lines, and the block's exit handling are unchanged. The conditions now live in the script's docstring, and the reference keeps only what the verdict means for step 2.
- `test_command_chains.py` runs the block with the same cases and assertions, including the guard that raises on a truthy non-object `data`. `test_run_events.py` binds the new placeholder in its documented-command replay.
- Workflow `v5b-22` is retained. No rule changes.

| File | Before | After |
| --- | --- | --- |
| `references/pull-request-target.md` | 12,566 | 8,775 |

The reference loads only for pull-request targets, so the always-loaded set stays at 92,272 bytes.

## Checks

At the final head, from `skills/review-code`: all 10 `scripts/test_*.py` suites, `validate_review.py --self-test`, `review_context.py --self-test`, and `forge_packet.py --self-test` exit 0.
```

## 4. Originating issue

None. The pull-request body is the only statement of intent. Record `issues=none` (or the coordinate of a spec the dispatch supplies).

## 5. Commits on the head, oldest first — messages verbatim

| # | SHA | Date | Author | Message |
| --- | --- | --- | --- | --- |
| 1 | `f20989622` | 2026-09-22 | Jack Chu | Move review-code's first-review eligibility guard into forge_packet.py<br><br>The pull-request root invocation carried a 42-line Python heredoc that<br>decides whether step 2's first-review context build can run at once.<br>It is now `forge_packet.py eligibility`, called through an absolute<br>`<forge-packet-script>` path like the block's other scripts. Conditions,<br>deferral reasons, verdict lines, and the block's exit handling are<br>unchanged; the conditions move to the script's docstring and the<br>reference keeps only what the verdict means for step 2. |
| 2 | `0ea287f0c` | 2026-09-22 | Jack Chu | State the retained workflow and unchanged always-loaded set in the changelog |

> **Mandatory note, same class as prior packets in this program.** Where later commits on the head
> applied the author's responses to earlier review rounds, that feedback is already fixed in the reviewed
> head and must not be rediscovered and reported as still outstanding. Read the prior-review section
> below against the head before treating any earlier comment as live.

## 6. Prior review state through the frozen cutoff `2026-09-22T20:21:16Z`, reproduced verbatim

### Review submissions (0)

| When | Who | State | On commit | Body |
| --- | --- | --- | --- | --- |

### Review threads (0), comments verbatim, in order

*(no inline review comments)*

### Non-review conversation (0), verbatim, in order

*(none)*

## 7. Repository guidance present at the merge-base

Verified by direct lookup in the mirror. Path-scoped `AGENTS.md`/`CLAUDE.md` in every ancestor directory of a changed path were checked; only rows that exist or are the standard root candidates are listed.

| Path | Present at merge-base | Blob |
| --- | --- | --- |
| `AGENTS.md` | **yes** | `1fc440d8d23b8e24f3167def388baa81fc4fed8a` |
| `CLAUDE.md` | no | — |
| `CONTEXT.md` | **yes** | `63aabeba276db823665db282d53116c5826a07bd` |
| `CONTRIBUTING.md` | no | — |
| `CODEOWNERS` | no | — |
| `.github/CODEOWNERS` | no | — |
| `.github/PULL_REQUEST_TEMPLATE.md` | no | — |
| `.github/pull_request_template.md` | no | — |

Read any present file from the clone with `git show <base-branch>:<path>` and treat it according to your own skill's guidance contract; record how you classified it.

## 8. Run conditions — binding on this run and on every sub-agent you spawn

1. **Offline.** Your clone's `origin` points at a local filesystem path, not `github.com`. No
   `git fetch`, no `git pull`, no `gh`, no `curl`, no web fetch, no network call of any kind, by you
   or by any sub-agent. If your skill's phase 1 asks you to resolve the target from the forge, that
   phase is satisfied by this packet, including its `merged` field.
2. **Execution allowance.** Focused tests under changed-tests.md default bounds; offline; no publication. Your own skill's helper scripts are always
   permitted; run them from the skill directory.
3. **History is truncated at the pinned head on purpose.** The newest object reachable in your clone
   is `0ea287f0c`. Nothing that happened after this pull request exists locally. Do not try to work
   around this. At the end, report explicitly whether you read any history beyond the pinned head and
   which history commands you ran.
4. **Publication is disabled.** The target is merged; this is a retrospective review. Do not post
   anything anywhere. Follow your skill through to the point where it would publish, then render the
   review **exactly as it would be posted**, including summary body (with the `Mode` line your
   contract requires for a merged target), per-finding comments, and any trailers, and stop.
5. **Follow your own skill as written** — its phase structure, its fan-out policy, its verification
   triggers, its output contract. Do not borrow behavior from any other review skill. Where the skill
   tells you to spawn sub-agents, spawn them with the `Agent` tool and **pass `model: "claude-sonnet-5"`
   explicitly on every call**.
6. **Persist before you verify.** Write the expensive phase to your report file before dispatching
   any verifier or finder: the manifest and requirement ledger when they are complete, then the
   complete candidate ledger with every disposition, then the verifier prompts and verbatim reports as
   they arrive. A session interruption after that point loses nothing that the file holds.
7. **Stay in your own sandbox.** Your clone, your skill snapshot, this packet directory, and your
   own report and payload paths only. Do not read any other run's clone, report, or payload. Report
   it if you read one anyway.
