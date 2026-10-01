# Review experiment data

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

Unlike tests 1–3, all four runs here are in **one cohort**: same model, same harness, same packet,
same truncated mirror, same session. Cost figures are directly comparable across the four columns —
the first time that has been true in this program.

## Run continuity

A session rate limit interrupted the first attempt. What survived and what was redone:

| Run | Find phase | Verify + Publish | Notes |
| --- | --- | --- | --- |
| v5 | — | **clean single-pass full run**, attempt 2 | Attempt 1 died before producing usable output; nothing carried over |
| v5a | — | **clean single-pass full run**, attempt 2 | Attempt 1 died before producing usable output; nothing carried over |

## Cost and shape

| | v5 | v5a |
| --- | --- | --- |
| Line | Skeptic | Skeptic, patched |
| Skill directory | `legacy reviewer` | `snapshot-path-omitted` |
| Pinned commit | `571f31d` | `c5f76df` |
| Architecture | integrated reviewer + verifier | integrated reviewer + verifier |
| Agents spawned | 1 | 1 |
| Sub-agent tokens | **35,917** (verifier only) | **44,198** (verifier only) |
| Tool uses | ~63 (primary ~44 + verifier 19) | ~100 (primary ~77 + verifier 23) |
| Wall clock | **~12 min, single pass** | **~15 min, single pass** |
| Verifier policy | consequence-triggered | consequence-triggered, candidate mode |
| Verifier ran? | yes | yes |
| `context` digest | `5800da33…3c67` | `ade4903f…44dd` |

## Output

| | v5 | v5a |
| --- | --- | --- |
| Candidates raised | 3 rendered, ~14 examined and dropped | 14 considered |
| Sent to verifier | 1 | 1 |
| Verifier verdicts | 1 `confirmed` | 1 `confirmed` |
| **Findings** | **3** | **2** |
| Blocking findings | 1 | 1 |
| Priority spread | P2, P3, P3 | P1, P3 |
| Questions | 0 | 1 |
| Observations | 0 standalone (folded into finding prose) | 1 (cap 3) |
| Ambiguities | — | 1 recorded |
| Coverage | complete, 10/10 | complete, 10/10 |
| **Status** | **Changes Requested (advisory)** | **Changes Requested (advisory)** |

## Ground-truth matrix

The four ground-truth items are defined in [README.md](README.md). GT-1 and GT-2 are confirmed by
upstream commits the runs could not reach; GT-3 and GT-4 are checkable inside the pinned diff.

| | v5 | v5a |
| --- | --- | --- |
| **GT-1** — new tests hit the live internet (`#29795`, fixed 2 days later by `#29811`) | **not raised** | **not raised** |
| **GT-2** — API surface wrong; `removeCookies` deleted and folded into `clearCookies` 24 days later (`#30111`) | not raised as a finding; anti-“sugar” rule checked and **acquitted as compliant** | **raised and dropped** — ledger item A5 quotes `CONTRIBUTING.md`'s "Avoid adding 'sugar' API… unless very common" and notes the method is fully expressible as `cookies()`+`clearCookies()`+`addCookies()`; dropped because the maintainer approved it |
| **GT-3** — generated `types.d.ts` stale against its own `.md` source | **published**, P3 `consider` | **published**, P3 `consider` |
| **GT-4** — docs entry carries only a `js` snippet where every sibling carries js/java/python/csharp | **not raised** | **not raised** |

## Upstream-checkable follow-ups on the runs' own findings

Two items the runs raised can be scored against what upstream actually did, using `#30111`'s diff.

| Item | What upstream did | v5 | v5a |
| --- | --- | --- | --- |
| Clear-then-re-add is not atomic; a concurrently written cookie is lost | **Not fixed.** `#30111` rewrote this exact function and kept the snapshot → `doClearCookies()` → re-add shape | **published P2 must-fix** | **published P1 must-fix** |
| `filter.domain === cookie.domain` exact string match is too narrow | **Partly vindicated.** `#30111` widened `name`/`domain`/`path` to `string \| RegExp` and documents `clearCookies({ domain: /.*my-origin\.com/ })`; plain-string comparison stayed exact | **dropped** — reframed as case-sensitivity and acquitted as "expected exact-match behavior" | **routed to a published question** — asks whether a header-set `Domain=` cookie matches, and names the experiment that would settle it |

The unanimous blocking finding is the one upstream declined to act on; the finding the four runs
disagreed most sharply about is the one upstream partially conceded. Unanimity is not accuracy here
in either direction.

## False positives

| Item | v5 | v5a |
| --- | --- | --- |
| `since: v1.43` should be `v1.42` (base is `1.42.0-next`) | **published P3** | **considered as ledger item A6 and dropped** — "plausible, ordinary release-boundary practice… not proven wrong" |

Upstream kept `since: v1.43`, and `#30111`'s replacement options carry the same tag. Three of four
runs published a wrong finding here; **v5a is the only run that reached the correct disposition**,
and it did so by applying an evidentiary gate rather than by knowing the answer — it recorded that
the claim was plausible but unproven and declined to publish on that basis.

## Secondary items and disagreements

| Item | v5 | v5a |
| --- | --- | --- |
| Doc doesn't state that an empty filter throws | not raised | not raised |
| Issue's `removeCookies([obj1, obj2])` array shape not implemented | acquitted (deliberate, maintainer-directed) | acquitted |
| Domain/path filter dimensions exceed "remove a specific cookie" | not raised | not raised |
| `protocol.yml` unrelated whitespace edit | dropped (harmless drive-by) | **published observation** |
| `protocol.yml` / `channels.ts` alphabetical-ordering break | not raised | not raised |
| `BrowserContextRemoveCookiesOptions = {}` empty-type boilerplate | acquitted (matches sibling pattern) | not raised |
| New spec file naming vs `browsercontext-clearcookies.spec.ts` | acquitted (pre-existing inconsistency) | not raised |

## Verifier contributions

| Run | Material verifier effect |
| --- | --- |
| v5 | Confirmed the race and **corrected the proposed remedy** — established that no backend exposes a filtered-delete primitive at the needed scope, so the fix cannot be "use the native delete" |
| v5a | Confirmed the race, **corrected the remedy the same way**, and **corrected the anchor range** from `283-292` to `279-293` |

## Billed usage (added 2026-09, #89)

The **Sub-agent tokens** row above is roughly each agent's final context size. Billing is per API
request: every request re-sends the whole context as cache reads, adds the new context as cache
writes, and pays for the output, thinking included. The figures below sum the per-request `usage`
objects in the harness's own transcripts with
[`transcript_usage.py`](https://github.com/kamui/code-review-bench/blob/main/bench/tools/transcript_usage.py) at `--prices 2,10` (Sonnet 5 list, $2 in /
$10 out per million; cache writes ×1.25, cache reads ×0.1). The transcripts live on the research
machine only (session `e4b94e80-336f-484a-a919-71a13c4cc57c`, one `agent-*.jsonl` per agent) and
are not committed; the sums are.

**One turn is one API request.** The harness writes one transcript line per content block of a
response and repeats the response's `usage` object on every line, so a line count overstates the
billed context by the blocks-per-request ratio. The v5a primary is 101 assistant lines but 41
requests. #89's own table was summed per line and so reads 7.86M cache-read tokens and $3.55 for
that agent; the per-request figures are 3.45M and $2.00. The `Turns` column counts requests, and
`Tool calls` counts distinct `tool_use` ids, which equals the number of `tool_result` blocks in
the same transcript. Every agent reports `claude-sonnet-5` on every request, which is the model
verification above done again from the same lines.

| Run / agent | Model | Turns | Tool calls | Text-only turns | Input | Cache write | Cache read | Output | Thinking | Wall | Billed cost ($) | Report output (est.) | Production-shaped ($) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v5 primary | claude-sonnet-5 | 33 | 50 | 1 | 66 | 144,912 | 2,429,084 | 78,374 | 37,564 | 0:18:27 | 1.63 | — | — |
| v5 verifier | claude-sonnet-5 | 11 | 19 | 1 | 22 | 27,028 | 245,826 | 7,497 | 3,799 | 0:01:57 | 0.19 | — | — |
| **v5 run** | claude-sonnet-5 | 44 | 69 | 2 | 88 | 171,940 | 2,674,910 | 85,871 | 41,363 | 0:20:24 | 1.82 | — | — |
| v5a primary | claude-sonnet-5 | 41 | 61 | 1 | 82 | 163,871 | 3,448,613 | 89,900 | 48,085 | 0:19:35 | 2.00 | — | — |
| v5a verifier | claude-sonnet-5 | 24 | 23 | 1 | 48 | 32,177 | 638,957 | 11,659 | 6,938 | 0:02:44 | 0.32 | — | — |
| **v5a run** | claude-sonnet-5 | 65 | 84 | 2 | 130 | 196,048 | 4,087,570 | 101,559 | 55,023 | 0:22:20 | 2.32 | — | — |
| v5 primary, attempt 1 (discarded) | claude-sonnet-5 | 35 | 56 | 0 | 70 | 102,522 | 2,122,794 | 46,550 | 34,249 | 0:16:49 | 1.15 | — | — |
| v5 verifier, attempt 1 (discarded) | claude-sonnet-5 | 20 | 34 | 1 | 40 | 41,022 | 546,243 | 10,373 | 6,328 | 0:03:03 | 0.32 | — | — |
| v5a primary, attempt 1 (discarded) | claude-sonnet-5 | 50 | 61 | 0 | 100 | 132,884 | 4,373,517 | 56,493 | 42,365 | 0:12:03 | 1.77 | — | — |
| v5a verifier, attempt 1 (discarded) | claude-sonnet-5 | 23 | 31 | 0 | 46 | 38,039 | 693,713 | 13,301 | 8,516 | 0:02:58 | 0.37 | — | — |

**Recorded `subagent_tokens` against billed cache reads**, per arm, for the same agents the
recorded figure covers:

**What the billed figures change.**

### Output by kind

`transcript_usage.py --by-kind` (#95) splits an agent's billed output into **thinking**, taken from
`usage` because thinking blocks are stored empty, and **visible** output: every `text` block and
every `tool_use` input, counted in characters (`len` of the text, `len` of `json.dumps` of the
input) and given the visible tokens in proportion. **File writes** are a second accounting of some
of the same characters, per destination path — a `Write` call under its `file_path`, a `Bash`
heredoc under the redirect target parsed from its command — measured in the same serialized
characters as the `tool:` bucket they are part of, so the two are reported separately and never
summed. Each content block is counted once per request. The figures below are
`transcript_usage.py <transcript> --prices 2,10 --by-kind` on the same four transcripts as the
table above.

| Run / agent | Thinking | Visible | File writes (chars) | Paths written >1× | Largest path (chars, times written) | Text |
| --- | --- | --- | --- | --- | --- | --- |
| v5a primary | 48,085 | 41,815 tokens over 103,920 chars | 83,487 (80%) | 1 of 5 | `/tmp/handoff4/reports/v5a-report.md` 61,923, 2× | 2,529 |
| v5a verifier | 6,938 | 4,721 tokens over 9,622 chars | 0 (0%) | 0 of 0 | — | 5,999 |
| v5 primary | 37,564 | 40,810 tokens over 106,013 chars | 79,520 (75%) | 1 of 2 | `/tmp/handoff4/reports/v5-report.md` 78,158, 2× | 2,766 |
