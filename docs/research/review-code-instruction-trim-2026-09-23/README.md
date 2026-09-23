# Superseded reference instructions, issue #346

[#346](https://github.com/kamui/skills/issues/346) removes the reference text that #342–#345's helpers made unnecessary, and measures each load path separately. This note records how those paths are measured, before and after. No model ran, and the workflow stays `v5b-24`.

## Method

[`measure.py`](measure.py) loads this checkout's `skills/review-code/scripts/test_instruction_budget.py` against two skill roots, so both roots use identical path definitions. The first root is `origin/main` at `4e31ec2`, the merge of #345, extracted with `git archive`. The second is this change. A path is the concatenated UTF-8 bytes a primary loads on that route: files, plus the helper `--help` and `--example` output its references direct it to run.

- **Every path**: `SKILL.md`, `review-rubric.md`, `rendering.md`, `changed-tests.md`, `check-evidence.md`, and `review_context.py --help`.
- **First reviews** add `context_fingerprint.py --example`:
  - **local publishable**: `local-targets.md`, plus the composer's publishable example;
  - **PR publishable**: `pull-request-target.md`, plus the same example;
  - **implementation-gate**: `local-targets.md`, plus the gate example.
- **required verifier**: PR publishable, plus `verifier-handoff.md` and `build_verifier_prompt.py --example`. The generated worker brief is measured on its own.
- **re-review**: PR publishable, plus `re-review.md`.
- **continuation**: the every-path set, plus `continuation-addendum.md` and `continue_review.py --example`.

The previous check measured two combined primaries, each carrying one verifier batch. Those two correspond to required verifier and to implementation-gate plus a batch. A batch adds the same `verifier-handoff.md` and builder example to any path.

Commands are counts of `python3 scripts/…` and `python3 <…>` mentions in a path. Authored fields are the leaves of each helper example, which is the input shape a reviewer writes. [`measure.json`](measure.json) holds the output:

```sh
git archive 4e31ec2 skills/review-code | tar -x -C /tmp/rc346-before
python3 docs/research/review-code-instruction-trim-2026-09-23/measure.py \
  --before /tmp/rc346-before/skills/review-code --after skills/review-code \
  --output docs/research/review-code-instruction-trim-2026-09-23/measure.json
```

## Result

| Path | Before: bytes / words | After: bytes / words | Bytes | Commands (before = after) | Limit after (before) |
| --- | ---: | ---: | ---: | ---: | ---: |
| runtime total | 91,790 / 12,858 | 87,803 / 12,289 | −3,987 | 21 | 88,000 (92,000) |
| always loaded | 25,953 / 3,531 | 24,894 / 3,377 | −1,059 | 6 | 25,000 (26,000) |
| local publishable | 48,374 / 6,535 | 46,819 / 6,317 | −1,555 | 8 | 47,000 (new) |
| PR publishable | 50,209 / 6,677 | 49,042 / 6,515 | −1,167 | 10 | 50,000 (new) |
| implementation-gate | 48,281 / 6,514 | 46,726 / 6,296 | −1,555 | 8 | 47,000 (new) |
| required verifier | 64,138 / 8,474 | 61,589 / 8,100 | −2,549 | 13 | 62,000 (PR primary 67,000) |
| re-review | 57,963 / 7,813 | 55,571 / 7,477 | −2,392 | 13 | 56,000 (new) |
| continuation | 44,481 / 6,056 | 43,270 / 5,882 | −1,211 | 11 | 44,000 (new) |
| verifier example brief, every branch | 22,941 / 3,075 | 22,941 / 3,075 | 0 | 0 | 24,000 (unchanged) |
| same brief, file transport | 23,385 / 3,136 | 23,385 / 3,136 | 0 | 0 | 24,000 (unchanged) |
| ordinary verifier example brief | 16,615 / 2,247 | 16,615 / 2,247 | 0 | 0 | — |

Every primary path shrinks, and no path grows. The largest cuts are on the verifier and re-review paths. Those references repeated the builder's input schema, the accounting helper's withholding rules, and `later-state`'s exclusions. The three worker-only references each gain a 145-byte load condition. They are counted in the runtime total but in no primary path, because the builder strips them.

- **Worker instructions.** All four representative briefs, ordinary and every-branch under both transports, are byte-identical before and after (`briefs_identical`). `test_savings_archive.py` also replays the builder against #341's archived bundles byte for byte.
- **Authored fields.** Every helper example is byte-identical, so a reviewer writes the same input shapes. The leaf counts are 78 for the publishable composition, 76 for the gate, 14 for the fingerprint input, 41 for the verifier input and 31 for the continuation input. #343–#345 already removed the mechanical ones, and this change removes no further field.
- **Documented commands.** The counts are unchanged on every path. No command was removed. The trimmed text restated what commands do, not which ones run.
- **Repair output.** No helper message a reviewer's input can trigger has changed. The only new message is the builder refusing a worker reference that lacks its load condition, which is a packaging fault.
- **Helper source.** One instruction sent readers to helper source: `local-targets.md` pointed to `review_context.py`'s docstring. That pointer is gone, so no runtime reference now directs a reader to helper source. Whether primaries still open source unprompted is a usage question for #347.

## Limits

These are static byte, word and mention counts over fixed path definitions, not measured loads. They show no turn, token, cost or latency effect, and make no recall claim. #347 runs the paired measurement. Helper `--help` output differs by a few bytes between Python versions because of argparse formatting. The figures above are from Python 3.14.7, and the lowered limits leave room for that difference under Python 3.9.25.
