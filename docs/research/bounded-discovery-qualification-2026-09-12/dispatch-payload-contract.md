# The payload-contract block (proposed D2 addition to the dispatch template)

**Proposed, and probed at synthetic scale only.** This is the block a future freeze would add to
every arm's rendered dispatch prompt so that gap 6 is satisfied at the source rather than converted
at settlement. The #149 template instructs the Markdown payload form, which
[`payload.py`](../bounded-discovery-readiness-2026-09-12/scripts/payload.py) now refuses to mask
rather than converting. The block below is **identical in every arm**: that is the point of it, and
an arm-specific variant would reintroduce the structural tell it exists to remove.

It was exercised by probe [P22](probes/P22-uniform-payloads/), where a session in each arm's launch
shape wrote a contract payload for a five-line synthetic change. It has never been rendered against a
real target, because no target is frozen and no dispatch is authorized.

**This block is at revision 2, and the first revision is retained beside the probe.** Revision 1
described `side` as optional on a line anchor and did not say that `summary` carries only `body`.
Every arm's review payload was refused at acceptance — `items[0].anchor: side is required in every
arm's payload` in all three arms, plus `summary: trailer is not part of the frozen contract` in arm
C. The validator was right and the instruction was wrong, which is the whole reason this block is
probed rather than assumed. The failed attempts are kept under
`probes/P22-uniform-payloads/*-attempt-1/`.

---

## Your review payload

Write your review as **one** file named `review-payload.json` in your working directory. It is the
only payload you write, in every outcome, and its shape does not depend on what you found.

```json
{
  "schema_version": "bounded-discovery-payload-v1",
  "attempt_id": "{ATTEMPT_ID}",
  "arm": "{ARM}",
  "outcome": "findings",
  "summary": {"body": "<the review body you would publish, as Markdown>"},
  "items": [],
  "stop": null
}
```

- `outcome` is `"findings"` when you are reporting at least one item and `"clean"` when you are
  reporting none. You never write `"stopped"` or `"unavailable"`; the coordinator writes those when
  an attempt ends without you.
- `summary` carries exactly one member, `body`: the review body you would publish. Nothing else
  goes in `summary` — not a trailer, not a count, not a status. It is never empty in a payload you
  write.
- `items` **always exists**. A clean review carries `[]`. Never invent an item to fill it, and
  never omit the key.
- `stop` is `null` in a payload you write.
- Unknown keys are refused at every level, in the envelope and in every item.

Each item is one of three types, and carries exactly these members:

| type | required | optional |
| --- | --- | --- |
| `finding` | `type`, `markdown`, `trailer`, `anchor`, `priority`, `action`, `blocking`, `kind` | `fix` |
| `question` | `type`, `markdown`, `trailer`, `anchor` | — |
| `observation` | `type`, `markdown` | — |

`priority` is one of `P0`, `P1`, `P2`, `P3`. `action` is `must-fix` or `consider`. `blocking` is
`true` or `false`. `kind` is your own short label for the defect class. `trailer` is a one-line
identifier for the item and must not be empty.

`anchor` is one of exactly two shapes, and every member listed is required:

- a file anchor — `{"type": "file", "path": "<repo-relative path>"}`, which may also carry
  `"side": "LEFT"` or `"side": "RIGHT"`;
- a line anchor — `{"type": "line", "path": "<repo-relative path>", "start_line": N,
  "end_line": M, "side": "LEFT" | "RIGHT"}`. On a line anchor `side` is **required**, not
  optional: `RIGHT` for a line as the change leaves it, `LEFT` for a line as it was.

Nothing about **what** a finding says is changed by this block: the policy under test still decides
what you raise, how you word it and whether you raise anything at all. Only the envelope it is
delivered in is frozen.
