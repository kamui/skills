# Re-review and prior state

Read at local-session start for snapshot lifetime, on a requested local-session recheck, or when `SKILL.md` step 1 finds prior state from the posting identity. It owns review state across heads: prior-state reading, the duplicate-review shortcut, delta scope, reply dispositions, and the prior-item classification that feeds the review record's `disputed` status input and rendering.md's `Disputed` and `Prior findings` sections.

## Prior-state sources

A pull-request target takes prior state only from the persisted packet, in either mode. A local target takes it only from a session record persisted at the reviewed head in this same session, on a requested recheck. One-shot local runs remain first reviews. Preserve stable finding ids and prior trailers for either source.

### Session snapshot lifetime

At local-session start, create a private directory with `mktemp -d` outside the working tree; its basename is `<session id>`. List `git for-each-ref --format='%(refname)' refs/review-code/session/`. Report other sessions' refs as potentially live: a concurrent session in this repository or a linked worktree may still own them. Only after the user confirms that no such session is running, report the leftovers as stale and offer deletion; delete them only on the user's authorization and never reuse them as prior state.

After each session snapshot, run `git update-ref refs/review-code/session/<session id>/<n> <snapshot sha>` with a fresh increasing `<n>` and retain the name in the run identity. This keeps the snapshot reachable even through `git gc --prune=now`. Keep the session's owned-ref inventory across runs, including unchanged-tree probes and failed runs. On exit, run `git update-ref -d <ref>` for every owned ref. Report any ref-command failure; a failed protection step stops the recheck before relying on that snapshot, and failed cleanup leaves a named stale ref for the next session. The snapshot script itself leaves refs unchanged.

### Session recheck

Read the persisted identity and artifact paths required by `review-record.md`'s Review identity. Use a fresh run subdirectory, retaining earlier artifacts. Resolve and pin the current local target and base under `local-targets.md`. For a range, step 2 passes the prior run head as `--prior-head` and the current pinned base as `--base-ref`. For a working tree, run once at step 1:

```sh
python3 scripts/review_context.py --worktree --parent <prior snapshot> --prior-head <prior snapshot> --merge-base <pinned merge-base> --base-ref <pinned base> --store <run-dir>/review-context.json
```

Protect the returned snapshot as above and reuse this context at step 2. `chain: chained` permits testing the delta conditions below. `chain: reset` invalidates the prior record: real HEAD moved through a commit, merge, or rebase. Report that reason, use the full `diff` as a first review, and consult no prior dispositions or amendments for classification, even if ordinary ancestry checks pass. Only snapshot identity was needed to detect the reset. An unreadable parent follows `snapshot-failed` under `local-targets.md`.

For a code-only recheck with unchanged base, merge-base, reviewed inputs and scope, `chain: chained`, the same tree hash, and an empty tree delta, report that the current record already covers this state and keep it current; create no new review, layer, or session record and dispatch no verifier. Apply this check before `nothing-to-review`; dirty submodule content cannot be declared unchanged from its gitlink alone. Retain the probe ref in the existing run's ownership inventory for exit cleanup. The duplicate-review shortcut below never applies to a session record.

Otherwise begin a new run. Use the prior session record's coverage and file accounting for the four delta conditions and two widening exceptions below; also compare its saved merge-base to the current pinned merge-base, since the helper compares both heads against the current base. Record a changed saved merge-base as a failed condition. Read prior items from its validated payload and private record and classify them on current evidence. Apply `Disputed` and `Prior findings` rendering as on a pull-request re-review, but draft no thread replies and record no thread node ids. A still-valid finding declined in the session becomes disputed after one verified recheck under the same rule below.

Seed a new session layer from the prior layer's entries, preserving their source coordinates and continuing the session coordinate sequence. Apply scope directives and tighter test policy as up-front inputs; apply a chosen reading to a recurring ambiguity without asking again, and retain the answer to a material question whose stable id survives. Carry these layer inputs even when continuity or delta conditions require a full review. Copy no amendments: re-derive each against the new head if its premise still holds, using `session.md`'s amendment and validation procedure after the new immutable record exists. Re-attach an explicit residual-risk `accepted` layer entry to a surviving finding without changing status or converting it into the `accepted` prior-item classification. That classification requires evidence under the rules below; the session cannot verify the user's authority to accept risk.

Each recheck has its own initial-plus-follow-up verification cap; step 3 still independently verifies a code-decided prior `must-fix`, including one closing as `fixed`. Retain the session-wide further-batch accounting across runs. If new work still requires verification after this run's follow-up is spent, finish the immutable record with that gap, then follow `session.md`'s existing authorization rule; a recheck never replenishes that further batch.

## Prior state from the packet

Read prior state from the packet `SKILL.md` step 1 persisted, never from a second fetch. Record the reviewed heads, stable ids, and unresolved requests of the posting identity's prior reviews, and take the prior head from the earlier review's run trailer (`head=`); step 2 passes it as `--prior-head`. Every review, thread comment, reply, issue comment, and pull-request comment in the packet carries the forge's stable numeric `id`, `created_at` (or `submitted_at`), and `last_edited_at`, which is `null` until the object is edited; a thread carries `is_resolved`, which has no timestamp. A reply edited after the prior review, without any code change, is later state and is re-read as prose. `python3 scripts/forge_packet.py later-state packet.json --review <prior review id>` lists everything created or edited after a review, and its `thread-state` lines name each thread whose undated resolved state cannot be ruled unchanged — every resolved thread, and every thread predating that review, which may have been un-resolved since — so a thread is never assumed unchanged.

## Duplicate-review shortcut

Report an existing review instead of duplicating it only when the packet is `complete`, the head, base, merge-base, `workflow` version, and recomputed `context` digest match its run trailer, and no relevant PR, issue, review, comment, or reply was created or edited after that review. Settle that last condition with `python3 scripts/forge_packet.py later-state packet.json --review <the candidate's id>`: it excludes only the candidate review and its own original comments and includes replies to them, reads every comment's and review's `last_edited_at`, and prints one line per later item, per packet gap, and per thread whose undated resolved state cannot be ruled unchanged and that carries no later comment. Exit 0 permits the shortcut. Exit 1 permits it only when every printed line is a `thread-state` line the reviewer settles by matching that thread's current state to the candidate review's own prior-item classification of its finding — `resolved` against `fixed`, `accepted`, or `obsolete`, and `unresolved` against `not-fixed` or an item that review left open — recording the match in the private record; any other line, and any unmatched thread, defeats the shortcut, and a truncated packet never qualifies. The review record defines the version and digest. Replies can change status without changing code.

## Re-review without losing state

Use the single context run from `SKILL.md` step 2, built with `--prior-head`: its `delta-conditions`, `delta-manifest`, and `delta-overlap` sections report the re-review scope inputs, and `delta-diff` is the delta itself. Review the **delta** when all of the following hold: `ancestor: yes`, `merge-base-unchanged: yes`, prior coverage is complete (the earlier review’s trailer, or the session record’s coverage), and the reviewer judges the delta's interactions bounded from `## delta-overlap`. Two exceptions widen a delta review: a delta hunk that overlaps a range where a prior finding is still open is reviewed together with that whole enclosing range at head, and a path the prior review listed under `Coverage gaps` is reviewed in full. When any condition fails, review the full diff and write which condition failed in the private record. A delta review still reads `## delta-diff` under step 3's rules — from the store, `--section delta-diff` selects it — and still runs every prior-item classification below. Carry and classify every unresolved item under the review record. For packet prior state, draft a reply for its existing thread; the caller posts it. After one verified re-review, a still-valid declined finding becomes disputed: stop re-posting it, but keep its blocking effect for human settlement.

A delta review's summary names the delta range (`<prior head>..<head>`) in its first paragraph and carries every open prior item; the run trailer's `context` digest is computed over the full inputs exactly as on a first review, so deduplication is unchanged.

## Replies and prior state

Read replies as prose first. Recognize these visible dispositions when present:

| Disposition | Meaning | Required evidence |
| --- | --- | --- |
| `implemented` | the requested change was made | what changed, commit, verification |
| `already-addressed` | current code already satisfies it | the decisive location or behavior |
| `answered` | a question was resolved without code | the answer and its source |
| `declined` | the author intentionally leaves it unchanged | technical or product rationale |
| `needs-info` | action needs a missing answer | the smallest focused question |
| `blocked` | the change is warranted but cannot proceed | blocker and next step |

An agent reply may carry this optional trailer:

```markdown
**Implemented** in `9f1e0aa` — retries now reuse the logical charge's key.

**Verification:** `pnpm test payments` passes with a timeout-after-commit case.

<!-- reply to=payments/retry-idempotency disposition=implemented head=9f1e0aa0b1c2d3e4f5061728394a5b6c7d8e9f01 -->
```

Never require or add a trailer on a human's behalf. Verify replies against current code. A reply states intent; it does not prove outcome.

On re-review, classify each prior item as `fixed`, `accepted`, `obsolete`, `still-open`, or `not-verifiable`. For packet prior state, retain each item's thread node id with its classification for the caller's thread actions; `review-code` does not mutate forge thread state. `Accepted` means the rereviewer verified that technical evidence makes the finding fail the rubric, or an authorized human explicitly accepted the residual risk; the author's `declined` disposition alone is not acceptance. Keep the other states open; for packet prior state, draft a reply for the existing thread rather than creating a duplicate, and the caller posts it. A declined item that remains after one verified re-review becomes `disputed`; list it for a person and stop re-posting it.
