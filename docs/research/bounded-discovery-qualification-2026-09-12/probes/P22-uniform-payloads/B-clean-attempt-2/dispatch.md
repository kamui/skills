You are reviewing one small change. The whole diff is in the relative file `packet.md`; read it, decide whether it has a material defect, and write your review payload. Do not run anything and do not write any other file.

## Your review payload

Write your review as **one** file named `review-payload.json` in your working directory. It is the
only payload you write, in every outcome, and its shape does not depend on what you found.

```json
{
  "schema_version": "bounded-discovery-payload-v1",
  "attempt_id": "probe-p22-B-clean2",
  "arm": "B",
  "outcome": "findings",
  "summary": {"body": "<the review body you would publish, as Markdown>"},
  "items": [],
  "stop": null
}
```

- `outcome` is `"findings"` when you are reporting at least one item and `"clean"` when you are
  reporting none. You never write `"stopped"` or `"unavailable"`; the coordinator writes those when
  an attempt ends without you.
- `summary.body` always carries the review body you would publish. It is never empty in a payload
  you write.
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
`true` or `false`. `kind` is your own short label for the defect class. `anchor` is either
`{"type": "file", "path": "<repo-relative path>"}` or
`{"type": "line", "path": "<repo-relative path>", "start_line": N, "end_line": M}`, optionally with
`"side": "LEFT"` or `"RIGHT"`.

Nothing about **what** a finding says is changed by this block: the policy under test still decides
what you raise, how you word it and whether you raise anything at all. Only the envelope it is
delivered in is frozen.
