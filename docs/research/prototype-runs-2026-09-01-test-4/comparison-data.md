# Comparison data — v2, v2a, v5, v5a on `microsoft/playwright#29698`

> **Historical note:** The skill name and snapshot path are omitted from this archive. PR #42 later replaced v5 with v5a; this record retains its original data. Pin v5 from `571f31d` for a historical rerun.

**2026-09-03. Data only.** This consolidates the four run records in this directory:
[v2](v2-run.md), [v2a](v2a-run.md), [v5](v5-run.md), [v5a](v5a-run.md). Interpretation is in
[evaluation.md](evaluation.md); the pinned target, the ground truth, and the conditions held
constant are in [README.md](README.md).

Unlike tests 1–3, all four runs here are in **one cohort**: same model, same harness, same packet,
same truncated mirror, same session. Cost figures are directly comparable across the four columns —
the first time that has been true in this program.

## Comparison boundaries

| Cohort | Runs | Model / harness | History available |
| --- | --- | --- | --- |
| Test 4 | v2, v2a, v5, v5a | explicit `claude-sonnet-5` / `t3code` | mirror truncated at the pinned head; merge commit, `#29811` and `#30111` all unreachable |

**Model verification.** Every agent in all four runs was checked after the fact by reading
`message.model` from its harness transcript rather than trusting intent. All nineteen agent
transcripts belonging to this test report `claude-sonnet-5` on every assistant turn — the four run
orchestrators, the four axis finders, and the four verifiers. `model: "sonnet"` also appears in the
recorded `Agent` tool-call parameters, confirming it was passed explicitly at every level and never
inherited. Both the v2 and v2a orchestrators flagged their finders' model as an evidence gap they
could not close from inside their own context; the transcript check closes it.

## Run continuity

A session rate limit interrupted the first attempt. What survived and what was redone:

| Run | Find phase | Verify + Publish | Notes |
| --- | --- | --- | --- |
| v2 | completed in attempt 1, **reused verbatim** | fresh orchestrator, attempt 2 | Same packet, same two finder reports; finders not re-run |
| v2a | completed in attempt 1, **reused verbatim** | fresh orchestrator, attempt 2 | Same packet, same two finder reports; finders not re-run |
| v5 | — | **clean single-pass full run**, attempt 2 | Attempt 1 died before producing usable output; nothing carried over |
| v5a | — | **clean single-pass full run**, attempt 2 | Attempt 1 died before producing usable output; nothing carried over |

The two Panel-line runs therefore have an orchestrator-context discontinuity between Find and
Verify that the two Skeptic-line runs do not. The discontinuity sits at a point where the
architecture already imposes a context boundary — v2/v2a finders are fresh-context sub-agents whose
reports are the orchestrator's whole input to Verify — so the substitute orchestrator received the
same information the original had. It is disclosed rather than scrubbed because it is a real
difference in run conditions, and because the second orchestrators lacked one thing the first had:
direct visibility into their finders' model parameter.

## Cost and shape

| | v2 | v2a | v5 | v5a |
| --- | --- | --- | --- | --- |
| Line | Panel | Panel, patched | Skeptic | Skeptic, patched |
| Skill directory | `snapshot-path-omitted` | `code-review-deep-publish` | `legacy reviewer` | `snapshot-path-omitted` |
| Pinned commit | `3c93b42` | `87c68a9` | `571f31d` | `c5f76df` |
| Architecture | 2 axis finders + verifier | 2 axis finders + verifier | integrated reviewer + verifier | integrated reviewer + verifier |
| Agents spawned | 3 | 3 | 1 | 1 |
| Sub-agent tokens | **198,466** (Code 99,128 + Requirements 55,058 + verifier 44,280) | **222,873** (Code 111,274 + Requirements 76,669 + verifier 34,930) | **35,917** (verifier only) | **44,198** (verifier only) |
| Tool uses | 110 (sub-agents 85 + orchestrator 25) | ~123 (sub-agents 94 + orchestrator ~29) | ~63 (primary ~44 + verifier 19) | ~100 (primary ~77 + verifier 23) |
| Wall clock | finders 554 s / 294 s, verifier 221 s; Verify session ~9 min | finders 617 s / 366 s, verifier 117 s; Verify session ~10 min | **~12 min, single pass** | **~15 min, single pass** |
| Verifier policy | mandatory when candidates exist | mandatory when candidates exist | consequence-triggered | consequence-triggered, candidate mode |
| Verifier ran? | yes | yes | yes | yes |
| `context` digest | not computed by this skill | not computed by this skill | `5800da33…3c67` | `ade4903f…44dd` |

The Panel line costs roughly **4–6× the metered sub-agent tokens** of the Skeptic line on this
target, and the gap is not an artifact of what each meter counts: v2 and v2a spawn every reviewing
agent as a sub-agent, so their finders are metered, while v5 and v5a do the primary review in the
top-level agent, which the harness does not meter. The true Skeptic-line totals are therefore higher
than the cells show — but their *sub-agent* work really is one verifier each, against three agents
each for the Panel line. Tool-use counts, which are self-reported on the same basis for all four,
show a smaller gap: 110 and ~123 against ~63 and ~100.

## Output

| | v2 | v2a | v5 | v5a |
| --- | --- | --- | --- | --- |
| Candidates raised | 6 (4 Code + 2 Requirements) | 3 (3 Code + 0 Requirements) | 3 rendered, ~14 examined and dropped | 14 considered |
| Sent to verifier | 6 | 3 | 1 | 1 |
| Verifier verdicts | 4 `confirmed`, 2 `plausible`, 0 `refuted` | 3 `confirmed`, 0 `plausible`, 0 `refuted` | 1 `confirmed` | 1 `confirmed` |
| **Findings** | **4** | **3** | **3** | **2** |
| Blocking findings | 2 | 1 | 1 | 1 |
| Priority spread | P1, P1, P3, P3 | P2, P3, P3 | P2, P3, P3 | P1, P3 |
| Questions | 2 | 0 | 0 | 1 |
| Observations | 1 (verifier's out-of-scope note; skill has no bounded section) | 3 published, at the cap; 2 more dropped to stay under it | 0 standalone (folded into finding prose) | 1 (cap 3) |
| Ambiguities | — | — | — | 1 recorded |
| Coverage | complete, 10/10 | complete, 10/10 | complete, 10/10 | complete, 10/10 |
| **Status** | **Changes Requested (advisory)** | **Changes Requested (advisory)** | **Changes Requested (advisory)** | **Changes Requested (advisory)** |

All four statuses are advisory, event `COMMENT`. **Status is unanimous for the fourth test running
and again fails to distinguish the runs.** The axis outcomes underneath it do differ: v2 reports
Requirements as *Waiting for information* (3/3 met, 1 unverifiable, 2 questions) while v2a reports
Requirements *Passed* (7/7 met, 0 questions) — on the same diff and the same issue.

## Ground-truth matrix

The four ground-truth items are defined in [README.md](README.md). GT-1 and GT-2 are confirmed by
upstream commits the runs could not reach; GT-3 and GT-4 are checkable inside the pinned diff.

| | v2 | v2a | v5 | v5a |
| --- | --- | --- | --- | --- |
| **GT-1** — new tests hit the live internet (`#29795`, fixed 2 days later by `#29811`) | **not raised** | **not raised** | **not raised** | **not raised** |
| **GT-2** — API surface wrong; `removeCookies` deleted and folded into `clearCookies` 24 days later (`#30111`) | not raised | **not raised** — Requirements axis returned *Passed*, 7/7 | not raised as a finding; anti-“sugar” rule checked and **acquitted as compliant** | **raised and dropped** — ledger item A5 quotes `CONTRIBUTING.md`'s "Avoid adding 'sugar' API… unless very common" and notes the method is fully expressible as `cookies()`+`clearCookies()`+`addCookies()`; dropped because the maintainer approved it |
| **GT-3** — generated `types.d.ts` stale against its own `.md` source | **examined and acquitted** — file marked *ignored, generated artifact*; both conflicting sentences quoted, then dismissed as "caught by CI's clean-tree check, not by manual review" | **published**, P3 `consider` | **published**, P3 `consider` | **published**, P3 `consider` |
| **GT-4** — docs entry carries only a `js` snippet where every sibling carries js/java/python/csharp | **not raised** | **not raised** | **not raised** | **not raised** |

**GT-1 is a clean four-way miss.** Every run read the 231-line test file in full and every run
commented on it in its manifest — v2 noted it "never exercises… a concurrent-cookie-write
scenario," v2a verified all eight tests' AND-semantics and recorded "No defect," v5 checked its
naming convention, v5a used it to falsify other candidates. None noticed that all eight tests
destructure a `server` fixture they never use and navigate to `https://www.example.com` instead.
Three of the four runs additionally had the WebKit flake on that exact spec file quoted verbatim in
their packet and treated it only as weak corroboration for the concurrency finding.

**GT-3 is the discriminator.** Three of four published it; v2 is the sole miss, and its miss is a
documented acquittal rather than an oversight — the finder found the drift, wrote it down, and
reasoned itself out of reporting it on the grounds that CI would catch it. It would have: that is
exactly why the job would have been red.

## Upstream-checkable follow-ups on the runs' own findings

Two items the runs raised can be scored against what upstream actually did, using `#30111`'s diff.

| Item | What upstream did | v2 | v2a | v5 | v5a |
| --- | --- | --- | --- | --- | --- |
| Clear-then-re-add is not atomic; a concurrently written cookie is lost | **Not fixed.** `#30111` rewrote this exact function and kept the snapshot → `doClearCookies()` → re-add shape | **published P1 must-fix** | **published P2 must-fix** | **published P2 must-fix** | **published P1 must-fix** |
| `filter.domain === cookie.domain` exact string match is too narrow | **Partly vindicated.** `#30111` widened `name`/`domain`/`path` to `string \| RegExp` and documents `clearCookies({ domain: /.*my-origin\.com/ })`; plain-string comparison stayed exact | **published P1 must-fix** (dot-prefix/RFC 6265 argument, verifier-confirmed) | **acquitted** — "rests on an unstated assumption; insufficiently evidenced" | **dropped** — reframed as case-sensitivity and acquitted as "expected exact-match behavior" | **routed to a published question** — asks whether a header-set `Domain=` cookie matches, and names the experiment that would settle it |

The unanimous blocking finding is the one upstream declined to act on; the finding the four runs
disagreed most sharply about is the one upstream partially conceded. Unanimity is not accuracy here
in either direction.

## False positives

| Item | v2 | v2a | v5 | v5a |
| --- | --- | --- | --- | --- |
| `since: v1.43` should be `v1.42` (base is `1.42.0-next`) | **published P3** | **published P3** | **published P3** | **considered as ledger item A6 and dropped** — "plausible, ordinary release-boundary practice… not proven wrong" |

Upstream kept `since: v1.43`, and `#30111`'s replacement options carry the same tag. Three of four
runs published a wrong finding here; **v5a is the only run that reached the correct disposition**,
and it did so by applying an evidentiary gate rather than by knowing the answer — it recorded that
the claim was plausible but unproven and declined to publish on that basis.

## Secondary items and disagreements

| Item | v2 | v2a | v5 | v5a |
| --- | --- | --- | --- | --- |
| Doc doesn't state that an empty filter throws | **published P3 consider** | not raised | not raised | not raised |
| Issue's `removeCookies([obj1, obj2])` array shape not implemented | **published as a question** | acquitted → observation (author accepted the redesign) | acquitted (deliberate, maintainer-directed) | acquitted |
| Domain/path filter dimensions exceed "remove a specific cookie" | **published as a question** (P2 scope-creep candidate → question) | not raised | not raised | not raised |
| `protocol.yml` unrelated whitespace edit | acquitted (small obvious cleanup) | **published observation** | dropped (harmless drive-by) | **published observation** |
| `protocol.yml` / `channels.ts` alphabetical-ordering break | rejected as a nitpick | **published observation** | not raised | not raised |
| `BrowserContextRemoveCookiesOptions = {}` empty-type boilerplate | not raised | not raised | acquitted (matches sibling pattern) | not raised |
| New spec file naming vs `browsercontext-clearcookies.spec.ts` | not raised | acquitted (no single convention exists) | acquitted (pre-existing inconsistency) | not raised |

## Verifier contributions

| Run | Material verifier effect |
| --- | --- |
| v2 | Confirmed 4, routed 2 to questions, refuted 0. **Caught a fabricated citation**: a finder cited test lines `435-454` in a 231-line file (correct site `212-230`), and flagged a pattern of imprecise line citations across both finders as an out-of-scope note |
| v2a | Confirmed 3, refuted 0, merged 0. Contributed 2 additional accurate observations that were dropped to stay inside the 3-item cap |
| v5 | Confirmed the race and **corrected the proposed remedy** — established that no backend exposes a filtered-delete primitive at the needed scope, so the fix cannot be "use the native delete" |
| v5a | Confirmed the race, **corrected the remedy the same way**, and **corrected the anchor range** from `283-292` to `279-293` |

Both Skeptic-line verifiers independently reached the same correction to the same proposed fix. The
Panel-line verifiers, given more candidates, spent their effort on adjudication and citation
checking rather than on remedy design.

## Mechanism results

- **v2a:** the doc-sync/drift sweep is what separates v2a from v2 on GT-3 — its Code finder reached
  the drift by using `addCookies`'s JSDoc as a control to establish that generated blocks normally
  match their `.md` source verbatim. The Requirements-axis changed-contract sweep ran, swept
  `removeCookies` and `clearCookies` repo-wide, and returned a **clean negative**. Question routing
  did not fire (0 questions). The observation cap bound at 3 and forced 2 accurate items out.
- **v5a:** the fix-sufficiency check fired and, with the verifier, replaced a backend-specific
  remedy with a reconciliation-after-restore fix that holds on all three backends. The question
  channel fired, on domain matching. The clean-verdict verifier did not apply (2 survivors). The
  `context` digest was recomputed twice through order-shuffled inputs and matched. The review
  validator ran and passed with zero violations, and its self-test was run first.
- **v5:** consequence-triggered verification fired exactly once, on the data-loss candidate, and the
  two `consider` findings were published primary-confirmed without verification — the designed
  behavior.
- **v2:** the mandatory-verification rule sent all 6 candidates, including 2 that the verifier ruled
  `plausible` and routed to questions rather than refuting.

## Sandbox and hygiene disclosures

- v2's Code finder wrote the diff to `/tmp/handoff4_pr.diff`, outside its two permitted directories,
  to read it in one pass. Contents derived entirely from the permitted repo; disclosed by the finder
  itself.
- v5 briefly wrote two scratch files outside its sandboxed roots and deleted them; disclosed.
- v5a made one incidental directory *listing* outside its sandbox, reading no file contents;
  disclosed.
- v2a had one transient scratch-file false start, created and deleted, never read by a sub-agent.
- No run read git history beyond the pinned head. Every run enumerated its history commands, and
  the lists contain only `git status`/`git branch`/`git rev-parse`/`git log --oneline -1`/
  `git diff main…review-head`/`git show main:<path>` forms.
- No run executed anything against the repository. The only scripts run were v5's and v5a's own
  helper scripts, which is explicitly permitted and which touch no repository code.

## Billed usage (added 2026-09, #89)

The **Sub-agent tokens** row above is roughly each agent's final context size. Billing is per API
request: every request re-sends the whole context as cache reads, adds the new context as cache
writes, and pays for the output, thinking included. The figures below sum the per-request `usage`
objects in the harness's own transcripts with
[`transcript_usage.py`](../tools/transcript_usage.py) at `--prices 2,10` (Sonnet 5 list, $2 in /
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
| v2 orchestrator, attempt 1 (Find) | claude-sonnet-5 | 30 | 45 | 3 | 60 | 183,300 | 1,999,010 | 32,206 | 16,896 | 0:16:22 | 1.18 | — | — |
| v2 Code finder | claude-sonnet-5 | 39 | 48 | 2 | 78 | 104,245 | 2,191,765 | 48,653 | 29,878 | 0:10:54 | 1.19 | — | — |
| v2 Requirements finder | claude-sonnet-5 | 13 | 17 | 2 | 26 | 96,662 | 373,613 | 31,775 | 20,437 | 0:10:24 | 0.63 | — | — |
| v2 orchestrator, attempt 2 (Verify + Publish) | claude-sonnet-5 | 16 | 25 | 1 | 32 | 226,978 | 970,867 | 61,198 | 16,690 | 0:14:47 | 1.37 | — | — |
| v2 verifier | claude-sonnet-5 | 25 | 24 | 1 | 50 | 36,998 | 638,932 | 17,116 | 9,998 | 0:03:40 | 0.39 | — | — |
| **v2 run** | claude-sonnet-5 | 123 | 159 | 9 | 246 | 648,183 | 6,174,187 | 190,948 | 93,899 | 0:56:08 | 4.77 | — | — |
| v2a orchestrator, attempt 1 (Find) | claude-sonnet-5 | 23 | 42 | 1 | 46 | 97,737 | 1,508,869 | 23,289 | 12,641 | 0:05:16 | 0.78 | — | — |
| v2a Code finder | claude-sonnet-5 | 35 | 54 | 1 | 70 | 99,582 | 2,252,486 | 48,244 | 34,686 | 0:10:15 | 1.18 | — | — |
| v2a Requirements finder | claude-sonnet-5 | 15 | 24 | 1 | 30 | 66,399 | 715,463 | 31,092 | 20,886 | 0:06:04 | 0.62 | — | — |
| v2a orchestrator, attempt 2 (Verify + Publish) | claude-sonnet-5 | 18 | 28 | 1 | 36 | 156,508 | 1,397,495 | 84,111 | 26,696 | 0:14:59 | 1.51 | — | — |
| v2a verifier | claude-sonnet-5 | 12 | 16 | 1 | 24 | 25,259 | 272,653 | 9,508 | 5,067 | 0:01:56 | 0.21 | — | — |
| **v2a run** | claude-sonnet-5 | 103 | 164 | 5 | 206 | 445,485 | 6,146,966 | 196,244 | 99,976 | 0:38:31 | 4.31 | — | — |
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

The **run** rows sum the agents that make up the run as recorded in [Run continuity](#run-continuity):
for v2 and v2a the attempt-1 orchestrator (whose Find phase was reused), both finders, the attempt-2
orchestrator, and the attempt-2 verifier; for v5 and v5a the attempt-2 primary and its verifier.
The `Wall` cell of a run row is the sum of its agents' walls, not the elapsed time. The four
**discarded** rows are the attempt-1 Skeptic-line agents the session limit killed before they
produced usable output; they cost $3.60 and belong to the session, not to any run. The attempt-1
v2 verifier (`agent-a8f7d349c577728c9`) has no billed request at all: its only transcript line is
the session-limit notice, and the script exits 2 on it.

**Recorded `subagent_tokens` against billed cache reads**, per arm, for the same agents the
recorded figure covers:

- **v2:** recorded 198,466 (Code + Requirements + verifier); those three agents billed 3,204,310
  cache-read tokens, **16×** the recorded figure, and $2.21 of the run's $4.77.
- **v2a:** recorded 222,873; billed 3,240,602 cache reads, **15×**, $2.01 of $4.31.
- **v5:** recorded 35,917 (verifier only); billed 245,826 cache reads, **7×**, $0.19 of $1.82.
- **v5a:** recorded 44,198 (verifier only); billed 638,957 cache reads, **14×**, $0.32 of $2.32.

**Production-shaped cost** (`--report <arm>-run.md`, the research report's bytes ÷ 4 subtracted from
billed output, #67's rule): v2 $4.53, v2a $4.08, v5 $1.64, v5a $2.18. The report is 5–10% of each
run's billed cost, less than #67's 15–25% estimate, because output is not the only thing billed.

**What the billed figures change.**

- The Panel/Skeptic gap on whole-run cost is **2.6× (v2 / v5) and 1.9× (v2a / v5a)**, not the 4–6×
  the sub-agent-token row shows, because that row excludes the Skeptic primaries and counts one
  context size per agent rather than one per request.
- For the v5a primary the dollar split is output $0.90, cache reads $0.69, cache writes $0.41,
  uncached input under a cent: cache reads are the largest **token** component (93%) but output is
  the largest **dollar** one (45%). Thinking is 53% of that output.
- Turn structure: the v5a primary made 41 requests for 61 tool calls, 1 request with no tool call
  and 18 with more than one. #89 reported 101 turns, 40 of them without a tool call and none with
  more than one; those were content-block lines, not requests. #90, which acts on that count, should
  start from the request figures here.

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
| v2a orchestrator, attempt 2 | 26,696 | 57,415 tokens over 147,331 chars | 131,303 (89%) | 1 of 1 | `/tmp/handoff4/reports/v2a-report.md` 131,303, 2× | 2,952 |

File writes are most of the visible output of every agent that wrote a file: 80% of the v5a
primary's visible characters, 75% of the v5 primary's and 89% of the v2a attempt-2 orchestrator's,
against 0% for the v5a verifier, which wrote none. On each of those three the one path written more
than once was written exactly twice, and it carries 74% (v5a primary), 98% (v5 primary) and 100%
(v2a orchestrator) of that agent's file-write characters. The largest path on every agent is that
agent's research report, the largest of them `/tmp/handoff4/reports/v2a-report.md` at 131,303
characters over two writes.
