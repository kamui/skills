# Worker-saved verifier returns, issue #344

[#344](https://github.com/kamui/skills/issues/344) lets a verifier worker save its return to an assigned private file. The primary then accounts that file and reads the accounting report once, instead of receiving the return as a tool result, rewriting it to `raw-return.json`, and reading it again inside `accounting.json`. It also takes `verifier-return.md` off the primary's read path. This note records the offline check the issue requires before merge. It replays [#341's archived verifier batches](../review-code-artifact-savings-2026-09-22/README.md) under both transports. No model ran, and the workflow stays `v5b-24`.

## Method

[`demo.py`](demo.py) takes the two baseline cells that ran a verifier batch, `publishable` and `required-verification`. For each cell it:

- reads the root transcript for the primary's reference reads, the worker hand-back that entered the primary's context, and the raw return the primary then wrote;
- rebuilds the archived projected `input.json` with this checkout's builder, once inline and once with `--return-file`;
- plays the worker with the archived raw return, changing only its `manifest_sha256` to the rebuilt manifest's hash. Under file transport it creates the assigned file exclusively and replies with the path. Inline, the primary saves the response;
- accounts both with this checkout's helper. It then compares the accounted and withheld IDs, violations, completeness and the return, less its manifest hash, across the two transports and against the archived `accounting.json`.

It measures the primary's return instructions as `verifier-handoff.md` plus `verifier-return.md` at `b5f3b04`, the merge of #343, against the handoff alone after this change. [`demo.json`](demo.json) holds the rows.

```sh
python3 docs/research/review-code-verifier-transport-2026-09-23/demo.py --output docs/research/review-code-verifier-transport-2026-09-23/demo.json
```

## Result

| Cell | Accounting, inline vs file vs archive | Primary-written return (chars) | Worker reply (chars) | Baseline hand-back into primary context (chars) |
| --- | --- | --- | --- | ---: |
| publishable | identical, exit 0 | 2,162 → 0 | 2,162 → 93 | 4,631 |
| required-verification | identical, exit 0 | 3,315 → 0 | 3,315 → 103 | 4,503 |

In both cells the two transports account the same tasks with the same judgments, evidence, corrections and asides, and both match the archived report. Under file transport the primary writes no return content. It passes the returned path to the helper, and the complete return reaches it once, inside `accounting.json`. The baseline primaries received the return inside the hand-back, wrote it again to `raw-return.json` (2,162 and 3,315 characters), and then read it a third time in the accounting report. A hand-back also carries the harness's own wrapper text, which this change leaves alone.

**Primary instruction load.** Both baseline primaries read `verifier-handoff.md` and `verifier-return.md` once each. After this change the primary reads only the handoff, which now carries the return fields it interprets. Together the two files were 14,112 bytes (1,884 words), and the handoff is now 11,575 bytes (1,585 words), 2,537 bytes fewer. `test_instruction_budget.py` shows the same drop on its expanded paths: the PR primary goes from 66,663 to 64,126 bytes and the local primary from 64,735 to 62,198.

**Worker growth.** The inline brief grows 155 bytes (16,411 → 16,566 and 17,900 → 18,055), because the transport now has its own section. The file-transport brief grows 621 and 631 bytes over the archived ones (to 17,032 and 18,531), for the exclusive-create instruction and the assignment line, whose path length differs. The worker also makes one extra tool call to write the file. The runtime reference total rises from 89,667 to 91,584 bytes, within its 92,000 limit. No limit rises.

## Limits

These are replays of two saved batches, not usage measurements. They show that the transport changes neither the accounting nor the judgments it carries, and they count the characters the primary no longer writes or reads. They show no turn, token, cost or latency effect, and make no recall claim; #347 runs the paired measurement. File transport applies only where the host can grant the worker that one write and the primary can read the result. Everywhere else, the inline path is the baseline path.
