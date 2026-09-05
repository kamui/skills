# Re-review and prior state

Read this reference only when `SKILL.md` step 2 requires it.

## Re-review without losing state

Use the single context run from `SKILL.md` step 2. Review the **delta** when all of the following hold: `ancestor: yes`, `merge-base-unchanged: yes`, the earlier review's trailer says `coverage=complete`, and the reviewer judges the delta's interactions bounded from `## delta-overlap`. Two exceptions widen a delta review: a delta hunk that overlaps a range where a prior finding is still open is reviewed together with that whole enclosing range at head, and a path the prior review listed under `Coverage gaps` is reviewed in full. When any condition fails, review the full diff and write which condition failed in the private record. A delta review still reads `## delta-diff` under step 3's rules and still runs every prior-item classification below. Carry and classify every unresolved item under the output contract. Reply on its existing thread. After one verified re-review, a still-valid declined finding becomes disputed: stop re-posting it, but keep its blocking effect for human settlement.

## Replies and prior state

Read prior state from the packet `SKILL.md` step 1 persisted, never from a second fetch. Every review, thread comment, reply, issue comment, and pull-request comment there carries the forge's stable numeric `id`, `created_at` (or `submitted_at`), and `last_edited_at`, which is `null` until the object is edited; a thread carries `is_resolved`, which has no timestamp. A reply edited after the prior review, without any code change, is later state and is re-read as prose. `python3 scripts/forge_packet.py later-state packet.json --review <prior review id>` lists everything created or edited after a review, and its `thread-state` lines name each resolved thread whose resolution cannot be dated, so a thread is never assumed unchanged.

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

On re-review, classify each prior item as `fixed`, `accepted`, `obsolete`, `still-open`, or `not-verifiable`. Resolve the first three. `Accepted` means the rereviewer verified that technical evidence makes the finding fail the rubric, or an authorized human explicitly accepted the residual risk; the author's `declined` disposition alone is not acceptance. Keep the other states open, replying on the existing thread rather than creating a duplicate. A declined item that remains after one verified re-review becomes `disputed`; list it for a person and stop re-posting it.
