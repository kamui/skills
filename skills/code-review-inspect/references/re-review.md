# Re-review and prior state

Read this reference only when `SKILL.md` step 1 finds a prior review, reply, or trailer-bearing comment from the posting identity. It owns review state across heads: prior-state reading, the duplicate-review shortcut, delta scope, reply dispositions, and the prior-item classification that feeds the review record's `disputed` status input and rendering.md's `Disputed` and `Prior findings` sections.

## Prior state from the packet

Read prior state from the packet `SKILL.md` step 1 persisted, never from a second fetch. Record the reviewed heads, stable ids, and unresolved requests of the posting identity's prior reviews, and take the prior head from the earlier review's run trailer (`head=`); step 2 passes it as `--prior-head`. Every review, thread comment, reply, issue comment, and pull-request comment in the packet carries the forge's stable numeric `id`, `created_at` (or `submitted_at`), and `last_edited_at`, which is `null` until the object is edited; a thread carries `is_resolved`, which has no timestamp. A reply edited after the prior review, without any code change, is later state and is re-read as prose. `python3 scripts/forge_packet.py later-state packet.json --review <prior review id>` lists everything created or edited after a review, and its `thread-state` lines name each thread whose undated resolved state cannot be ruled unchanged — every resolved thread, and every thread predating that review, which may have been un-resolved since — so a thread is never assumed unchanged.

## Duplicate-review shortcut

Report an existing review instead of duplicating it only when the packet is `complete`, the head, base, merge-base, `workflow` version, and recomputed `context` digest match its run trailer, and no relevant PR, issue, review, comment, or reply was created or edited after that review. Settle that last condition with `python3 scripts/forge_packet.py later-state packet.json --review <the candidate's id>`: it excludes only the candidate review and its own original comments and includes replies to them, reads every comment's and review's `last_edited_at`, and prints one line per later item, per packet gap, and per thread whose undated resolved state cannot be ruled unchanged and that carries no later comment. Exit 0 permits the shortcut. Exit 1 permits it only when every printed line is a `thread-state` line the reviewer settles by matching that thread's current state to the candidate review's own prior-item classification of its finding — `resolved` against `fixed`, `accepted`, or `obsolete`, and `unresolved` against `not-fixed` or an item that review left open — recording the match in the private record; any other line, and any unmatched thread, defeats the shortcut, and a truncated packet never qualifies. The review record defines the version and digest. Replies can change status without changing code.

## Re-review without losing state

Use the single context run from `SKILL.md` step 2, built with `--prior-head`: its `delta-conditions`, `delta-manifest`, and `delta-overlap` sections report the re-review scope inputs, and `delta-diff` is the delta itself. Review the **delta** when all of the following hold: `ancestor: yes`, `merge-base-unchanged: yes`, the earlier review's trailer says `coverage=complete`, and the reviewer judges the delta's interactions bounded from `## delta-overlap`. Two exceptions widen a delta review: a delta hunk that overlaps a range where a prior finding is still open is reviewed together with that whole enclosing range at head, and a path the prior review listed under `Coverage gaps` is reviewed in full. When any condition fails, review the full diff and write which condition failed in the private record. A delta review still reads `## delta-diff` under step 3's rules — from the store, `--section delta-diff` selects it — and still runs every prior-item classification below. Carry and classify every unresolved item under the review record. Draft a reply for its existing thread; the caller posts it. After one verified re-review, a still-valid declined finding becomes disputed: stop re-posting it, but keep its blocking effect for human settlement.

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

On re-review, classify each prior item as `fixed`, `accepted`, `obsolete`, `still-open`, or `not-verifiable`. Record the first three as resolved; inspect does not mutate forge thread state. `Accepted` means the rereviewer verified that technical evidence makes the finding fail the rubric, or an authorized human explicitly accepted the residual risk; the author's `declined` disposition alone is not acceptance. Keep the other states open, drafting a reply for the existing thread rather than creating a duplicate; the caller posts it. A declined item that remains after one verified re-review becomes `disputed`; list it for a person and stop re-posting it.
