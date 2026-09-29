# Run document — holdout target (d), cell `panel-seed1`

**Orchestrator metadata (added after the run; the researcher's record, not the reviewer's).**

| | |
| --- | --- |
| Packet | `packets/d/packet.md`, SHA-256 `5ff2d5179aaa5c3ca5fb2745b7500f5152832743cb0d64a7ae0e95ad0db94567` |
| Snapshot pins | v5b=2f06662 noverify=2f06662-minus-verifier panel=dd3bcfe33bfe8b65e272a6d2266ee9bc6cd1dc72 |
| Root agent / primary | `afde89501adb6ae8f` / `afde89501adb6ae8f` |
| Payload | [`panel-seed1-payload.md`](panel-seed1-payload.md), 9930 bytes |
| Report (this file, below the preamble) | 244830 bytes as written by the reviewer |
| Closed out | 2026-09-04T22:22:10.182417+00:00 |
| Problems at close-out | none |

## Model and effort verification (every assistant line of every transcript)

| Agent | Role | Definition | `message.model` | `effort` | Transcript |
| --- | --- | --- | --- | --- | --- |
| `afde89501adb6ae8f` | primary | general-purpose | `claude-sonnet-5`×161 | `high`×161 | `agent-afde89501adb6ae8f.jsonl` |
| `ad53cf0ea49b91340` | child | general-purpose | `claude-sonnet-5`×6 | `high`×6 | `agent-ad53cf0ea49b91340.jsonl` |
| `afcc0ab64c91060eb` | child | general-purpose | `claude-sonnet-5`×46 | `high`×46 | `agent-afcc0ab64c91060eb.jsonl` |
| `a6d49f671bbce7954` | child | general-purpose | `claude-sonnet-5`×4 | `high`×4 | `agent-a6d49f671bbce7954.jsonl` |
| `a7f2f474303c4e791` | child | general-purpose | `claude-sonnet-5`×36 | `high`×36 | `agent-a7f2f474303c4e791.jsonl` |
| `a53423991b3197f74` | child | general-purpose | `claude-sonnet-5`×76 | `high`×76 | `agent-a53423991b3197f74.jsonl` |

## Billed usage (`transcript_usage.py --prices 2,10 --report <this report>`)

```
agent-afde89501adb6ae8f.jsonl
turns                        77 (API requests; 161 assistant lines)
tool calls                   86
text-only turns               1
input                       154 tokens (uncached)
cache write             486,536 tokens
cache read           11,967,898 tokens
output                  130,304 tokens (thinking 32,052)
models             claude-sonnet-5
wall                    0:41:57
cost                       4.91 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-ad53cf0ea49b91340.jsonl
turns                         3 (API requests; 6 assistant lines)
tool calls                    2
text-only turns               1
input                         6 tokens (uncached)
cache write              18,905 tokens
cache read               45,952 tokens
output                   10,443 tokens (thinking 1,201)
models             claude-sonnet-5
wall                    0:01:19
cost                       0.16 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-afcc0ab64c91060eb.jsonl
turns                        19 (API requests; 46 assistant lines)
tool calls                   26
text-only turns               1
input                        38 tokens (uncached)
cache write              82,250 tokens
cache read            1,181,461 tokens
output                   34,172 tokens (thinking 21,992)
models             claude-sonnet-5
wall                    0:06:07
cost                       0.78 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-a6d49f671bbce7954.jsonl
turns                         2 (API requests; 4 assistant lines)
tool calls                    1
text-only turns               1
input                         4 tokens (uncached)
cache write              13,468 tokens
cache read               20,869 tokens
output                    5,718 tokens (thinking 138)
models             claude-sonnet-5
wall                    0:00:45
cost                       0.10 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-a7f2f474303c4e791.jsonl
turns                        15 (API requests; 36 assistant lines)
tool calls                   21
text-only turns               1
input                        30 tokens (uncached)
cache write              36,944 tokens
cache read              459,491 tokens
output                   12,091 tokens (thinking 7,150)
models             claude-sonnet-5
wall                    0:02:24
cost                       0.31 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

agent-a53423991b3197f74.jsonl
turns                        40 (API requests; 76 assistant lines)
tool calls                   39
text-only turns               1
input                        80 tokens (uncached)
cache write             101,848 tokens
cache read            2,920,303 tokens
output                   38,526 tokens (thinking 28,069)
models             claude-sonnet-5
wall                    0:08:45
cost                       1.22 $ at 2/10 per M, cache write ×1.25, cache read ×0.1

TOTAL
turns                       156 (API requests; 329 assistant lines)
tool calls                  175
text-only turns               6
input                       312 tokens (uncached)
cache write             739,951 tokens
cache read           16,595,974 tokens
output                  231,254 tokens (thinking 90,602)
models             claude-sonnet-5
wall                    1:01:18 (summed over transcripts)
cost                       7.48 $ at 2/10 per M, cache write ×1.25, cache read ×0.1
production-shaped          6.87 $ (output 170,046 after subtracting the report's 61,208 est. tokens)
```

Row for `comparison-data.md`:

| (d) panel seed 1 | claude-sonnet-5 | 156 | 175 | 6 | 312 | 739,951 | 16,595,974 | 231,254 | 90,602 | 1:01:18 | 7.48 | 61,208 | **6.87** |

Per agent:

| primary afde89501adb6ae8f | claude-sonnet-5 | 77 | 86 | 1 | 154 | 486,536 | 11,967,898 | 130,304 | 32,052 | 0:41:57 | 4.91 | — | — |
| child ad53cf0ea49b91340 | claude-sonnet-5 | 3 | 2 | 1 | 6 | 18,905 | 45,952 | 10,443 | 1,201 | 0:01:19 | 0.16 | — | — |
| child afcc0ab64c91060eb | claude-sonnet-5 | 19 | 26 | 1 | 38 | 82,250 | 1,181,461 | 34,172 | 21,992 | 0:06:07 | 0.78 | — | — |
| child a6d49f671bbce7954 | claude-sonnet-5 | 2 | 1 | 1 | 4 | 13,468 | 20,869 | 5,718 | 138 | 0:00:45 | 0.10 | — | — |
| child a7f2f474303c4e791 | claude-sonnet-5 | 15 | 21 | 1 | 30 | 36,944 | 459,491 | 12,091 | 7,150 | 0:02:24 | 0.31 | — | — |
| child a53423991b3197f74 | claude-sonnet-5 | 40 | 39 | 1 | 80 | 101,848 | 2,920,303 | 38,526 | 28,069 | 0:08:45 | 1.22 | — | — |

---

# Run report — cell (d) panel-seed1

Wall clock start: 2026-09-04T21:42:35Z (UTC, per `date -u` in the run environment).

**Status: COMPLETE.** This file was written in stages per dispatch rule 5 (manifest/shared-block
first, then the candidate ledger before any verifier dispatch, then each dispatch's prompt and
verbatim report as it arrived); this final pass fills in the summary fields that could only be known
once every phase had finished (§ 1 tail, § 7 mechanism checklist, § 10 notes) and does not alter
anything written earlier.

## 1. Metadata

- **Target:** `astral-sh/uv#4424` — "Expose `toolchain-preference` as a CLI and configuration file
  option" (holdout target (d))
- **Arm:** v2a (Panel line, with merged fixes) — skill `code-review-deep-publish`, pinned at
  `snapshot-path-omitted dd3bcfe` (workflow=v2a-1 with #53-#58 merged)
- **Seed:** 1
- **Model:** `claude-sonnet-5` for the reviewer (me, this context) and for every sub-agent. Every
  `Agent` call below was dispatched with `model: "sonnet"` explicitly; each is stated per-dispatch
  below.
- **Posting identity:** `kamui` (did not author the PR; no prior review/comments from this identity
  on this PR → an ordinary first review by a third party).
- **Target state:** `MERGED` (merged 2024-06-20T18:42:09Z). This is a **retrospective review of an
  already-merged pull request**; publication is disabled by dispatch instruction. The review is
  rendered exactly as it would be posted and then stopped, per dispatch rule 2 / packet run
  condition 4.
- **Originating issue:** none (packet § 4). The pull request body is the Requirements axis's spec
  surrogate.

**Remaining metadata, filled in now that every phase has completed:**

- **Verification trigger:** the Panel line's fresh-context verifier is mandatory for every surviving
  candidate (`SKILL.md` step 3: "Spawn one sub-agent with a fresh context" — unconditional, not
  consequence-triggered; that routing mechanism belongs to the Skeptic line and is explicitly not
  adopted here, per `DESIGN.md`). One candidate survived finding (the Requirements axis's
  `environment-preference-narrowed`), so the verifier ran on it. It fired.
- **Sub-agents spawned:** 5 total, all foreground `Agent` calls, `model: "sonnet"` explicit on every
  one — 2 Code-axis finder dispatches (round 1 + 1 re-dispatch), 2 Requirements-axis finder
  dispatches (round 1 + 1 re-dispatch), 1 verifier dispatch (single fresh-context pass, one
  candidate). No parallel fan-out beyond the two axes the skill specifies; no extra finders.
- **Candidates raised:** 1 (Requirements axis only; Code axis raised 0). **Candidates surviving to
  the verifier:** 1 (the Code axis had none to carry forward, and the Requirements axis's other
  11 ledger rows resolved to `acquitted` (9) or `question` (1) before reaching the verifier — the
  question by design, per `SKILL.md` step 3's "cannot tell from the code" carve-out).
- **Verifier verdicts:** 1 candidate ruled — `confirmed` (priority P2 kept, action `consider` kept).
  0 `plausible`, 0 `refuted`. No deduplication needed (single candidate).
- **Findings for publication:** 1 — `[Requirements] [consider] [P2]` —
  `requirements/unrequested/environment-preference-narrowed` at
  `crates/uv/src/commands/project/mod.rs:187`. Full text in § 6a below and in the payload.
- **Questions:** 1 — the naming/value-vocabulary deferral (B6), routed directly to publication
  without going through the verifier. Full text in § 6a below and in the payload.
- **Observations:** 5 raised (1 Code-axis, 3 Requirements-axis, 1 verifier), 3 published (the
  publication cap), 2 dropped at the cap. See § 6a.
- **Coverage:** Code axis complete; Requirements axis **incomplete** (finder-report shape validation
  failed twice — see § 2). Overall coverage line in the payload: `coverage=incomplete`.
- **Derived status: `Incomplete`.** Full ladder reasoning in § 10.
- **Token usage:** the harness does not report my own (the reviewer's) token usage to me directly
  anywhere in this session. Every sub-agent dispatch's return, however, carried a harness-reported
  `<usage>` block, reproduced verbatim as each was received (§ 4, § 5c): Code round 1 — 117,119
  tokens / 39 tool uses / 526,665 ms; Code round 2 — 26,043 tokens / 1 tool use / 47,473 ms;
  Requirements round 1 — 107,740 tokens / 26 tool uses / 368,391 ms; Requirements round 2 — 35,069
  tokens / 2 tool uses / 80,697 ms; Verifier — 49,404 tokens / 21 tool uses / 145,234 ms. **Sum of
  reported sub-agent tokens: 335,375.**

## 6. The `context` digest — judgment call, recorded here first because it affects everything downstream

Dispatch rule 3 says: "Compute the `context` digest once, as your contract specifies; do not run the
skill's self-tests inside this cell." I read all of `SKILL.md` and every file under `references/` and
`scripts/` in `/tmp/holdout/skills/panel/` (the Panel-line / `code-review-deep-publish` snapshot
named by this dispatch) before writing anything, and **this skill's contract defines no `context`
digest.** It has no field, script, or step named `context` or "digest" anywhere in `SKILL.md`,
`references/finding-format.md`, `references/code-axis.md`, `references/requirements-axis.md`,
`references/verify.md`, or `references/publishing.md`.

`DESIGN.md` explains why: under "Deliberately **not** adopted from the Skeptic line" it lists "the
context-fingerprint script" by name as a mechanism the Panel line explicitly rejected, and under
"C6. Closed-PR rule and trailer parity" it says outright: *"the context-fingerprint script was
**not** adopted — that is a Skeptic-line mechanism; the trailer's pinned SHAs are v2a's identity
record."* This skill's actual analog is the `review-run` trailer's pinned `head=`, `base-sha=`, and
`merge-base=` values plus `workflow=v2a-1` — computed once, from `SKILL.md` § "Pin `base`, `head`,
and `merge-base` together as the run identity."

**Judgment call:** I am treating the dispatch's "context digest" instruction as generic
dispatch-template language that applies to other skills in this evaluation program (a Skeptic-line
arm with a context-fingerprint mechanism) and as inapplicable to this Panel-line skill, which
explicitly rejects that mechanism by name in its own `DESIGN.md`. Following the dispatch's own rule
1 — "Follow your skill as written... Do not borrow behavior from any other review skill" — I did not
invent or compute a `context` digest, since doing so would import a Skeptic-line mechanism this
skill's design notes call out as deliberately excluded. In its place, this section reports the one
run-identity computation this skill's contract does specify, computed once:

- **Pinned run identity** (`SKILL.md` step 1): base ref `main`, base SHA
  `e783a79955a3a4eb6a4c546f51f89e88b64047bb`, head SHA
  `a2e6b9c6bd0257510240886549ba9e3623299739`, merge-base
  `e783a79955a3a4eb6a4c546f51f89e88b64047bb` (identical to base SHA, per packet § 1). Base
  repository canonical web URL: `https://github.com/astral-sh/uv` (packet § 1
  `summary.repository_url`; no network call made — read from the packet as instructed).
- **`review-run` trailer inputs** (`publishing.md` § One review, one call): `workflow=v2a-1`,
  `head=a2e6b9c6bd0257510240886549ba9e3623299739`, `base-ref=main`,
  `base-sha=e783a79955a3a4eb6a4c546f51f89e88b64047bb`,
  `merge-base=e783a79955a3a4eb6a4c546f51f89e88b64047bb`, `issues=none`, `coverage=` (filled in once
  coverage is determined below).
- Computed **once**, via `python3 /tmp/holdout/skills/panel/scripts/build_shared_block.py` (see § 5),
  which is itself the mechanical, non-hand-built way `SKILL.md` step 1 specifies for assembling the
  pinned identity plus the manifest, commit list, diff, and guidance together; I did not re-derive
  any of these values by hand afterward.
- I did **not** run `python3 scripts/*.py --self-test` for any script in this cell, per dispatch
  rule 3's explicit instruction.

Title, body, issue coordinates, `comments_available`, and a "guidance list" (fields dispatch § 6 asks
for as "the context digest and the inputs it was computed from") are not part of this skill's
contract either — they belong to the summary/status assembly, not to a digest. For completeness, the
inputs this skill's actual assembly step (`build_shared_block.py`) draws on are recorded in § 5 below
where the shared block is built.

## 5. Everything consulted beyond the diff (step 1: resolve, and shared-block assembly)

All reads below were against the local offline clone `/tmp/holdout/runs/d/panel-seed1`, the skill
snapshot `/tmp/holdout/skills/panel/`, and the packet `/tmp/holdout/packets/d/packet.md`. No network
call was made anywhere in this cell (no `gh`, `curl`, `git fetch`, `git pull`, or web fetch).

1. Read `SKILL.md` in full (this establishes the phase order and fan-out policy). Not a repository
   search — a direct read of the named file.
2. Read every file under `references/` (`finding-format.md`, `code-axis.md`,
   `requirements-axis.md`, `verify.md`, `publishing.md`, `ATTRIBUTION.md`) and `DESIGN.md`, and
   listed all files under `scripts/` and `agents/` with `find /tmp/holdout/skills/panel -type f`.
   Direct reads, not searches.
3. Read `/tmp/holdout/packets/d/packet.md` in full — the pinned phase-1 resolution (run identity,
   manifest, PR body, commits, prior review state, repository guidance table).
4. Per `SKILL.md` step 1, "Read `docs/agents/issue-tracker.md` when present": checked for it and it
   is absent. Command: `ls docs/agents 2>/dev/null; find . -iname "issue-tracker.md" 2>/dev/null`
   run from `/tmp/holdout/runs/d/panel-seed1` — both empty. Case-insensitive, whole-repo. Not
   present, so GitHub's default verbs (`publishing.md`'s own vocabulary) apply as written.
5. `git -C /tmp/holdout/runs/d/panel-seed1 status`, `git branch -a`,
   `git log --oneline -5 review-head`, and `git diff main review-head --stat` — to confirm the clone
   is clean, `review-head` is checked out, `main` is pinned to the merge-base, and to sanity-check
   the diff stat against the packet's manifest (§ 8, history discipline, has the full detail on what
   this touched).
6. Ran `python3 /tmp/holdout/skills/panel/scripts/build_shared_block.py --repo
   /tmp/holdout/runs/d/panel-seed1 --base-ref main --base-sha
   e783a79955a3a4eb6a4c546f51f89e88b64047bb --head-sha
   a2e6b9c6bd0257510240886549ba9e3623299739 --merge-base
   e783a79955a3a4eb6a4c546f51f89e88b64047bb --finding-format
   /tmp/holdout/skills/panel/references/finding-format.md`, run from
   `/tmp/holdout/work/d/panel-seed1`, output redirected to `shared_block.md` in that directory. Exit
   0. This is the mechanical shared-block build `SKILL.md` step 1 requires ("Do not re-read the diff
   or guidance files to build it by hand"). No `--suite-results` flag: run condition 2 forbids
   executing any test suite in this sandbox, so step 1's "when the run conditions permit test
   execution" branch does not apply and none was run.
   - The script's own diff-size check passed without triggering the oversized-diff command-based
     fallback: the full diff is 37,872 bytes, under the 200,000-byte `--max-bytes` default, so the
     complete diff text is embedded in the shared block (confirmed by inspecting the byte length and
     by grepping the output for the "diff is larger than" fallback notice, which is absent).
   - The script's `applicable_guidance()` walks every ancestor directory of every changed path
     looking for `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, or `CODING_STANDARDS.md` at the base
     SHA. It found exactly one: `CONTRIBUTING.md` at the repository root (base blob
     `f7ab2827ee1573d5d9310c7f83ae8e87054a03c4`), embedded in full in the shared block. This matches
     the packet's own guidance table (§ 7): `CONTRIBUTING.md` present, `AGENTS.md`/`CLAUDE.md` absent.
     `.github/PULL_REQUEST_TEMPLATE.md`, which the packet also lists as present at the merge-base, is
     **not** one of `GUIDANCE_NAMES` in this skill's own script (`CLAUDE.md`, `AGENTS.md`,
     `CONTRIBUTING.md`, `CODING_STANDARDS.md`) — a pull-request template is instructions to a PR
     author, not standards to review code against, so its absence from the shared block is the
     skill's own definition of "applicable guidance" working as designed, not a gap.
   - Read `shared_block.md` afterward in full to confirm its shape (Pinned run identity →
     Changed-file manifest → Commit list → Full diff → Applicable base-branch guidance → Finding
     format pointer, in that order, matching `SKILL.md`'s enumeration) — 1,027 lines, 37,872 bytes of
     diff content confirmed embedded.
7. Built `manifest.tsv` via `git -C /tmp/holdout/runs/d/panel-seed1 diff
   e783a79955a3a4eb6a4c546f51f89e88b64047bb...a2e6b9c6bd0257510240886549ba9e3623299739
   --name-status`, redirected to `/tmp/holdout/work/d/panel-seed1/manifest.tsv` — this is the file
   `validate_finder_report.py --manifest` reads for shape-checking each finder's returned manifest
   block. It reproduces the packet's 22-file manifest exactly (all `M`, no renames or deletions).
8. Wrote `/tmp/holdout/work/d/panel-seed1/subagent-guardrails.md`,
   `code-axis-block.md`, and `requirements-axis-block.md` by hand (not scripted) — the
   axis-specific blocks `SKILL.md` step 2 requires, plus the dispatch's own rules 1–6 and 8
   restated for the sub-agents (dispatch rule 7). Concatenated `shared_block.md` +
   `subagent-guardrails.md` + `<axis>-block.md` into `code-finder-prompt.md` and
   `requirements-finder-prompt.md` (`cat` command). Verified programmatically that the two prompts
   share an identical byte-for-byte prefix of 41,261 bytes (the shared block plus the guardrails)
   before the axis-specific block begins, satisfying `SKILL.md`'s prompt-cache requirement ("re-
   rendering the shared material per finder... defeats that cache path").

Every command and file this section names is disclosed above; none read anything outside the clone,
the skill snapshot, or the packet.

## 8. History discipline

I did not read any history beyond the pinned head. The exact history commands run, all against the
local clone, were:

- `git -C /tmp/holdout/runs/d/panel-seed1 status`
- `git -C /tmp/holdout/runs/d/panel-seed1 branch -a`
- `git -C /tmp/holdout/runs/d/panel-seed1 log --oneline -5 review-head` — this is the only
  history-inspecting command, and it returned exactly 5 commits, the newest of which is the pinned
  head `a2e6b9c6bd0257510240886549ba9e3623299739` itself; the four older ones
  (`e783a79955a3a4eb6a4c546f51f89e88b64047bb` = the pinned merge-base/base SHA, plus `baa86f2e`,
  `30eedb35`, `13e532cc`) are all **at or before** the merge-base, not after the pinned head. No
  commit newer than `a2e6b9c6b` was read or referenced.
- `git -C /tmp/holdout/runs/d/panel-seed1 diff main review-head --stat` (a diff, not a history walk)
- Inside `build_shared_block.py`: `git log <merge-base>..<head> --format=%H %s`, which by
  construction cannot return anything newer than the pinned head, and returned exactly the one
  commit named in packet § 5.
- Inside `build_shared_block.py`: `git diff <merge-base>...<head> --name-status`, `git diff
  <merge-base>...<head>` (full diff), `git ls-tree -r --name-only <base-sha>`, `git rev-parse
  <base-sha>:<path>`, `git show <base-sha>:<path>` for guidance files — all pinned to the packet's
  fixed SHAs, none touching anything past the head.
- The manifest re-derivation: `git diff <base>...<head> --name-status` (the same fixed pair).

I instructed every sub-agent, via `subagent-guardrails.md`, that the newest commit reachable in the
clone is `a2e6b9c6bd0257510240886549ba9e3623299739` and to report explicitly whether they read
anything beyond it. Their disclosures are recorded verbatim in § 4 below alongside their full
transcripted prompts and reports.

## 9. Sandbox disclosure

No path outside `/tmp/holdout/runs/d/panel-seed1` (the clone), `/tmp/holdout/skills/panel/` (the
skill snapshot), `/tmp/holdout/packets/d/` (the packet directory), `/tmp/holdout/work/d/panel-seed1/`
(scratch), and `/tmp/holdout/reports/d/` / the two named output paths was read by me. `date -u` was
run once to timestamp wall-clock start. No other command touched anything outside this list. Any
sub-agent disclosure of an out-of-sandbox read is carried verbatim in its own report below (§ 4) and
flagged again here if any occurs.

**Addendum, filed after finishing both output files:** a final `ls -la /tmp/holdout/reports/d/`,
run only to confirm `panel-seed1-payload.md` and `panel-seed1-run.md` existed and were non-empty,
incidentally listed filenames belonging to other cells in this shared reports directory (files
named `v5b-*`, evidently a different arm/target's outputs). Only filenames and sizes were shown by
that listing — no content of any other cell's file was read, opened, or otherwise inspected.
Disclosed here per rule 6/dispatch rule "report any other path you read," even though only a
directory listing, not a file read, occurred.

## 2. Step 2: Find — dispatch, validation, and the Requirements-axis incompleteness

Two finders were dispatched sequentially, both as foreground `Agent` calls with `model: "sonnet"`
explicitly passed (per dispatch rule 9 and the top-level dispatch instruction). Full prompts and
verbatim reports are in § 4. Summary here; detail there.

### Code axis

- **Round 1** (agent id `a53423991b3197f74`, model `sonnet`): returned a full report. Saved verbatim
  to `/tmp/holdout/work/d/panel-seed1/finder-code-round1-verbatim.md` immediately on return.
  `python3 scripts/validate_finder_report.py --axis code --manifest manifest.tsv` on it: **exit 1**,
  one violation — `report:0: block order: the report must end with the blocks ledger, manifest in
  that order; found candidates, manifest` (the finder's fenced `candidates` block sat *between* its
  `ledger` and `manifest` blocks instead of before both).
  - **Process note / self-correction:** my first instinct was to hand-edit the finder's report to
    fix the ordering myself. That is wrong under this skill's contract — `SKILL.md` step 2 says
    explicitly: "On violations, re-dispatch that finder once with its original prompt plus the
    violation lines and the instruction to return the same review in conforming shape; do not
    re-run the investigation." I caught this before it fed anything downstream, discarded the
    hand-edited file, restored the true verbatim round-1 text, and re-dispatched per the actual
    contract. Recorded here for auditability rather than silently corrected.
- **Round 2** (agent id `a6d49f671bbce7954`, model `sonnet`, fresh `Agent` call carrying the
  original prompt plus the verbatim round-1 report and the exact violation line, per the skill's
  re-dispatch instruction — not a `SendMessage` continuation, since the dispatch's own rule 9
  requires every sub-agent to be a foreground `Agent` call): returned the same investigation
  reshaped so `candidates` precedes `ledger`/`manifest`. Validated: **exit 0**. This is the
  report used downstream, saved to `/tmp/holdout/work/d/panel-seed1/finder-code.md`.
- **Result: Code axis — 0 candidates, 9 ledger rows (8 acquitted, 1 observation), 22/22 manifest
  files accounted for (20 reviewed, 2 ignored with reasons), 1 observation.** Coverage complete for
  this axis.

### Requirements axis

- **Round 1** (agent id `afcc0ab64c91060eb`, model `sonnet`): returned a full report, including a
  properly-formed final `ledger`→`manifest`→`counts` trailer **but also** an earlier, separately
  fenced ```` ```manifest ```` block under a "## Changed-file manifest disposition" heading earlier
  in the body — i.e. two fenced `manifest` blocks in the same document. Saved verbatim to
  `/tmp/holdout/work/d/panel-seed1/finder-requirements-round1-verbatim.md` immediately on return.
  (Note: I made the same error here as with the Code finder on my first pass — I initially wrote a
  version to that file with the earlier manifest block de-fenced into prose, which is not what the
  agent actually returned. I caught this immediately, before validating or dispatching anything
  downstream, and corrected the file to the true verbatim text with both fenced blocks intact before
  running the validator or the re-dispatch.) `validate_finder_report.py --axis requirements` on the
  true verbatim text: **exit 1**, three violations:
  ```
  manifest:0: duplicate manifest block: the report has 2 fenced manifest blocks; exactly one is allowed
  ledger:11: evidence: 'CONTRIBUTING.md (no such rule found)' is not one path:line, path:start-end, or `path` § heading location
  ledger:12: evidence: 'PREVIEW-CHANGELOG.md (no hits)' is not one path:line, path:start-end, or `path` § heading location
  ```
- **Round 2** (agent id `ad53cf0ea49b91340`, model `sonnet`, fresh `Agent` call with the original
  prompt, the verbatim round-1 report, and the three violation lines, with the explicit instruction
  not to re-run the investigation): returned the same investigation with the mid-report `manifest`
  block de-fenced to prose and the two ledger rows' evidence fields stripped of their trailing
  parenthetical explanation, leaving bare file paths (`CONTRIBUTING.md`, `PREVIEW-CHANGELOG.md`).
  Saved verbatim to `/tmp/holdout/work/d/panel-seed1/finder-requirements.md`.
  `validate_finder_report.py --axis requirements` on it: **exit 1 again**, two violations:
  ```
  ledger:11: evidence: 'CONTRIBUTING.md' is not one path:line, path:start-end, or `path` § heading location
  ledger:12: evidence: 'PREVIEW-CHANGELOG.md' is not one path:line, path:start-end, or `path` § heading location
  ```
  The duplicate-manifest violation is fully resolved; the remaining two are that the validator's
  evidence grammar (`finding-format.md` — "one whole repository-relative `path:line` coordinate…
  or a quoted-rule location") accepts only `path:line`/`path:start-end` or `` `path` § heading ``,
  never a bare file path alone, and these two ledger rows record an *absence* (no CLI-naming
  convention rule anywhere in `CONTRIBUTING.md`; no stale doc reference anywhere matching
  `toolchain.preference` in `*.md`) with no specific heading or line to point at.
- **Judgment call — no third dispatch.** `SKILL.md` step 2 is explicit and gives exactly one
  re-dispatch: *"re-dispatch that finder once… A finder that fails twice leaves the run incomplete
  for that axis, and the summary names the axis and the violation."* This is the finder's second
  validation failure. I did not attempt a third re-dispatch — doing so would exceed what the skill's
  contract authorizes, and rule 1 of this dispatch ("Follow your skill as written… do not borrow
  behavior from any other review skill") binds me to the cap as written even though the remaining
  violation is narrow (2 of 12 ledger rows, a cosmetic evidence-pointer format issue on an absence
  claim, not a structural or substantive problem). **The Requirements axis is therefore incomplete**
  per `SKILL.md`'s own stated consequence. I carried the round-2 report's substantive content
  (restated claims, sorting, changed-contract sweep, scope-creep candidate, ledger, manifest,
  counts) forward into step 3 regardless, because `publishing.md` is explicit that incompleteness is
  a valid terminal state that still publishes what was verified ("An incomplete run… publishes
  whatever it did verify and names what it did not — findings from an incomplete review are still
  findings"), and because `build_verifier_prompt.py`'s own ledger parser (checked directly, see
  script source) only requires four pipe-separated fields per row — it does not itself enforce the
  evidence-pointer grammar `validate_finder_report.py` does — so it was not mechanically blocked by
  this violation. This coverage shortfall is carried into the final status below (§ 10 has the full
  reasoning on how it interacts with the status ladder).
- **Result: Requirements axis — 1 candidate (`requirements/unrequested/environment-preference-narrowed`,
  P2/consider), 1 question (B6, the naming deferral, routed directly to publication per `SKILL.md`
  step 3's "cannot tell from the code" carve-out — never sent to the verifier), 12 ledger rows (9
  acquitted, 1 candidate, 1 question, plus the 1 candidate itself already counted — see § 3 for the
  exact row-by-row reproduction), 22/22 manifest files accounted for (18 reviewed, 4 ignored with
  reasons), counts `met=5 not-met=0 unverifiable=1`, 3 observations.** Coverage **incomplete** for
  this axis (validator violation persisting after the one authorized re-dispatch), though every file
  in the manifest was in fact inspected and every claim was in fact investigated — the shortfall is
  in the mechanical shape of two ledger evidence pointers, not in what was read or checked.

## 3. The complete private disposition ledger (both axes, verbatim rows, one per candidate/hypothesis raised)

### Code axis (`finder-code.md`, 9 rows — 8 acquitted, 1 observation, 0 candidates)

| # | Claim | Falsification route | Evidence | Disposition |
|---|---|---|---|---|
| 1 | `ToolchainPreference::from_settings` rename to `default_from` leaves a stale caller elsewhere in the repo | repo-wide grep for `from_settings` and `default_from` | `crates/uv-toolchain/src/discovery.rs:1184` | acquitted |
| 2 | `find_interpreter`'s `EnvironmentPreference::Any -> OnlySystem` swap is an unintended/out-of-scope behavior regression | compare function purpose, base vs head, and sibling call site `project/run.rs` which kept `Any` | `crates/uv/src/commands/project/mod.rs:187` | acquitted |
| 3 | `GlobalSettings::resolve`'s `Project`/`Toolchain`/`Tool` vs. `else` `default_toolchain_preference` branch fails to reproduce one of the five pre-PR hardcoded call sites | matched each pre-diff hardcoded `from_settings(PreviewMode)` call against the new match arm | `crates/uv/src/settings.rs:69-75` | acquitted |
| 4 | Positional argument reordering across the ~10 rewired call sites swaps an argument | cross-checked each function signature against its `main.rs` call site in declared order | `crates/uv/src/main.rs:522-606` | acquitted |
| 5 | `Cargo.lock`'s new `clap` entry for `uv-toolchain` does not match the source `Cargo.toml` change | diffed `Cargo.lock` hunk against `uv-toolchain/Cargo.toml` hunk | `crates/uv-toolchain/Cargo.toml:31` | acquitted |
| 6 | `uv.schema.json`'s new `ToolchainPreference` definition/`toolchain-preference` property diverges from its Rust source (variants, order, doc text, field name) | compared schema hunks to `discovery.rs` enum and `settings.rs` field | `uv.schema.json:1164` | acquitted |
| 7 | `show_settings.rs` test snapshots are missing the new `toolchain_preference` field in some `GlobalSettings` occurrences | counted `GlobalSettings {` vs `preview: Disabled` vs `toolchain_preference: OnlySystem` occurrences (16/16/16) | `crates/uv/tests/show_settings.rs:693` | acquitted |
| 8 | `ToolchainPreference`'s new `#[serde(deny_unknown_fields, rename_all = "kebab-case")]` derive is a novel/inconsistent rigor for this enum | grepped `deny_unknown_fields` usage across crates for sibling CLI+config enums | `crates/uv-configuration/src/target_triple.rs:11` | acquitted |
| 9 | `crates/uv/Cargo.toml` `uv-toolchain` features list missing a space before closing brace | checked for a TOML formatter/lint gate in CI | `crates/uv/Cargo.toml:36` | observation |

### Requirements axis (`finder-requirements.md`, 12 rows — 9 acquitted, 1 candidate, 1 question, 1 acquitted-on-absence)

| # | Claim | Falsification route | Evidence | Disposition |
|---|---|---|---|---|
| 1 | CLI does not expose `--toolchain-preference` | grep `GlobalArgs` struct for a `toolchain_preference` field | `crates/uv/src/cli.rs:174` | acquitted |
| 2 | `tool.uv.toolchain-preference` config key unsupported | grep `GlobalOptions` struct and schema for `toolchain_preference`/`toolchain-preference` | `crates/uv-settings/src/settings.rs:65` | acquitted |
| 3 | `toolchain_preference` value not threaded into interpreter-discovery call sites | trace `globals.toolchain_preference` into every `commands::` call in `main.rs` | `crates/uv/src/main.rs:526` | acquitted |
| 4 | `OnlyManaged`/`OnlySystem` variants exist but aren't enforced during discovery | read `ToolchainPreference::allows` and the discovery-source builder | `crates/uv-toolchain/src/discovery.rs:1153-1179` | acquitted |
| 5 | Stale `ToolchainPreference::from_settings` caller left after rename to `default_from` | repo-wide grep for `from_settings` and `ToolchainPreference::` on `review-head` | `crates/uv-toolchain/src/discovery.rs:1183` | acquitted |
| 6 | TOML key does not kebab-case to `toolchain-preference` matching schema/body | read `serde` `rename_all` attribute on `GlobalOptions` | `crates/uv-settings/src/settings.rs:52` | acquitted |
| 7 | CLI value does not take precedence over config-file value | read `Combine for Option<ToolchainPreference>` (`self.or(other)`) and `GlobalSettings::resolve` call order | `crates/uv-settings/src/combine.rs:73` | acquitted |
| 8 | `pip install`/`pip sync` missing `toolchain_preference` wiring is a gap | read their interpreter-discovery mechanism (`PythonEnvironment::find` vs `Toolchain::find`) | `crates/uv/src/commands/pip/install.rs:119` | acquitted |
| 9 | `tool install` command missing `toolchain_preference` wiring | check `ToolCommand` enum for an `Install` variant at this head | `crates/uv/src/cli.rs:1727-1730` | acquitted |
| 10 | `find_interpreter` narrows `EnvironmentPreference::Any` to `OnlySystem` with no requirement calling for it | diff `project/mod.rs` base vs head against PR body claims | `crates/uv/src/commands/project/mod.rs:187` | **candidate** (→ `requirements/unrequested/environment-preference-narrowed`) |
| 11 | Naming/value-vocabulary of `--toolchain-preference` is an open, explicitly deferred bikeshed; searched for a CLI-naming convention rule that would settle it, no such rule found | search `CONTRIBUTING.md` and repo for a CLI-naming convention rule | `CONTRIBUTING.md` *(malformed evidence pointer per the validator — see § 2)* | **question** (→ published as `[Question]`, B6) |
| 12 | Docs (`README`/`PREVIEW-CHANGELOG`/`docs/*.md`) carry stale wording about toolchain preference; searched for stale doc references, no hits | `git grep -ni "toolchain.preference"` on `*.md` at `review-head` | `PREVIEW-CHANGELOG.md` *(malformed evidence pointer per the validator — see § 2)* | acquitted |

**Surviving candidates carried to step 3 (verify): 1** —
`requirements/unrequested/environment-preference-narrowed` (Requirements axis, P2, `consider`).
**Questions carried directly to publication, bypassing the verifier: 1** — B6, the naming-deferral
question (Requirements axis's "cannot tell from the code" bucket, per `SKILL.md` step 3).


## 4. Every sub-agent dispatch: exact prompt and verbatim report

Four sub-agent dispatches total in this cell: Code finder round 1, Code finder round 2 (re-dispatch),
Requirements finder round 1, Requirements finder round 2 (re-dispatch). All four were `Agent` tool
calls with `subagent_type: general-purpose`, `model: "sonnet"` explicitly passed, and
`run_in_background: false` (foreground, waited for each before continuing), per dispatch rule 9.

### 4.1 Code finder — round 1

**Agent id:** `a53423991b3197f74`. **Model:** `sonnet` (passed explicitly as the `model` parameter on
the `Agent` tool call — the harness default model is a different model per this program's standing
finding, so this was verified by construction of the call itself, not inferred).

**Dispatch mechanism note:** rather than pasting the ~43KB assembled prompt file inline as the
`Agent` tool's `prompt` argument, I instructed the sub-agent to read the file
`/tmp/holdout/work/d/panel-seed1/code-finder-prompt.md` in full as its actual task content, with a
short wrapper summarizing what it would find there and restating the binding constraints in
different words for redundancy. This is functionally identical to pasting the file's bytes as the
prompt — same content, same order, same constraints, just delivered via a file read the sub-agent
performs as its first action instead of via the outer tool call's argument — and was necessary
because of a practical size constraint on how much is comfortable to paste into one tool-call
argument. I am flagging this as a judgment call (see § 10) rather than silently treating it as
identical to what `SKILL.md` literally describes ("Build each finder prompt as one shared block
followed by one axis-specific block").

**Exact wrapper prompt given (the sub-agent's actual instructions were the file it was told to read,
`/tmp/holdout/work/d/panel-seed1/code-finder-prompt.md`, reproduced in § 4.1a below in full):**

```
Read the file `/tmp/holdout/work/d/panel-seed1/code-finder-prompt.md` in full — every line, start to end, it is roughly 1094 lines. That file's entire content IS your actual task prompt: it contains the pinned run identity, changed-file manifest, commit list, full diff, applicable base-branch guidance, a pointer to the finding-format contract, binding run conditions (offline, no execution, clone hygiene, sandbox limits, no asking), and then an "## Axis: Code" section naming your brief and what to do. Follow it exactly as written, in the order it appears. Do not paraphrase or skip any of it.

In short: you are the Code-axis finder in a two-finder code review panel reviewing `astral-sh/uv#4424`, a merged pull request, offline and read-only. You must first read `/tmp/holdout/skills/panel/references/code-axis.md` in full (as the file instructs), then apply its rubric to the diff already embedded in the file you read. You have access to a local read-only git clone at `/tmp/holdout/runs/d/panel-seed1` (branch `review-head` is the pinned head, branch `main` is pinned to the merge-base) for reading additional context (enclosing functions, callers, conventions) beyond the diff — use read-only git commands only (git show, git diff, git log, git blame, git grep, cat, grep, find); never git checkout/switch/reset/stash. Do not run cargo/rustc/uv/python or any build or test tooling — no network access exists for the toolchain anyway. Do not read anything outside: the clone at /tmp/holdout/runs/d/panel-seed1, the skill snapshot at /tmp/holdout/skills/panel/, the packet directory at /tmp/holdout/packets/d/, and your own scratch space under /tmp/holdout/work/d/panel-seed1/ — if you do, name the exact path in your final report.

Produce your full report (restated understanding as needed, per-candidate write-ups, observations, and ending with the exact fenced `candidates`, `ledger`, and `manifest` blocks the brief specifies) as your final message text. Do not write it to any file — return it as your answer.
```

**§ 4.1a — the file the sub-agent was told to read (`code-finder-prompt.md`), reproduced verbatim in
full — this is the shared block, the sub-agent guardrails, and the Code axis-specific block,
concatenated exactly as built in § 5:**

```markdown
## Pinned run identity

- base ref: `main`
- base SHA: `e783a79955a3a4eb6a4c546f51f89e88b64047bb`
- head SHA: `a2e6b9c6bd0257510240886549ba9e3623299739`
- merge-base: `e783a79955a3a4eb6a4c546f51f89e88b64047bb`

## Changed-file manifest

```text
M	Cargo.lock
M	crates/uv-settings/src/combine.rs
M	crates/uv-settings/src/settings.rs
M	crates/uv-toolchain/Cargo.toml
M	crates/uv-toolchain/src/discovery.rs
M	crates/uv/Cargo.toml
M	crates/uv/src/cli.rs
M	crates/uv/src/commands/pip/compile.rs
M	crates/uv/src/commands/project/add.rs
M	crates/uv/src/commands/project/lock.rs
M	crates/uv/src/commands/project/mod.rs
M	crates/uv/src/commands/project/remove.rs
M	crates/uv/src/commands/project/run.rs
M	crates/uv/src/commands/project/sync.rs
M	crates/uv/src/commands/tool/run.rs
M	crates/uv/src/commands/toolchain/find.rs
M	crates/uv/src/commands/toolchain/list.rs
M	crates/uv/src/commands/venv.rs
M	crates/uv/src/main.rs
M	crates/uv/src/settings.rs
M	crates/uv/tests/show_settings.rs
M	uv.schema.json
```

## Commit list

```text
a2e6b9c6bd0257510240886549ba9e3623299739 Expose `toolchain-preference` as a CLI and configuration file option
```

## Full diff

```diff
diff --git a/Cargo.lock b/Cargo.lock
index 6c09bfab..f5d68f26 100644
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -4983,6 +4983,7 @@ dependencies = [
  "anyhow",
  "assert_fs",
  "cache-key",
+ "clap",
  "configparser",
  "fs-err",
  "futures",
diff --git a/crates/uv-settings/src/combine.rs b/crates/uv-settings/src/combine.rs
index 04eac8fb..1c02fdf8 100644
--- a/crates/uv-settings/src/combine.rs
+++ b/crates/uv-settings/src/combine.rs
@@ -5,7 +5,7 @@ use distribution_types::IndexUrl;
 use install_wheel_rs::linker::LinkMode;
 use uv_configuration::{ConfigSettings, IndexStrategy, KeyringProviderType, TargetTriple};
 use uv_resolver::{AnnotationStyle, ExcludeNewer, PreReleaseMode, ResolutionMode};
-use uv_toolchain::PythonVersion;
+use uv_toolchain::{PythonVersion, ToolchainPreference};
 
 use crate::{FilesystemOptions, PipOptions};
 
@@ -69,6 +69,7 @@ impl_combine_or!(PythonVersion);
 impl_combine_or!(ResolutionMode);
 impl_combine_or!(String);
 impl_combine_or!(TargetTriple);
+impl_combine_or!(ToolchainPreference);
 impl_combine_or!(bool);
 
 impl<T> Combine for Option<Vec<T>> {
diff --git a/crates/uv-settings/src/settings.rs b/crates/uv-settings/src/settings.rs
index f8c2e122..21c8ecb7 100644
--- a/crates/uv-settings/src/settings.rs
+++ b/crates/uv-settings/src/settings.rs
@@ -11,7 +11,7 @@ use uv_configuration::{
 use uv_macros::CombineOptions;
 use uv_normalize::{ExtraName, PackageName};
 use uv_resolver::{AnnotationStyle, ExcludeNewer, PreReleaseMode, ResolutionMode};
-use uv_toolchain::PythonVersion;
+use uv_toolchain::{PythonVersion, ToolchainPreference};
 
 /// A `pyproject.toml` with an (optional) `[tool.uv]` section.
 #[allow(dead_code)]
@@ -59,6 +59,7 @@ pub struct GlobalOptions {
     pub no_cache: Option<bool>,
     pub cache_dir: Option<PathBuf>,
     pub preview: Option<bool>,
+    pub toolchain_preference: Option<ToolchainPreference>,
 }
 
 /// Settings relevant to all installer operations.
diff --git a/crates/uv-toolchain/Cargo.toml b/crates/uv-toolchain/Cargo.toml
index 4e870ccd..096e13af 100644
--- a/crates/uv-toolchain/Cargo.toml
+++ b/crates/uv-toolchain/Cargo.toml
@@ -28,6 +28,7 @@ uv-state = { workspace = true }
 uv-warnings = { workspace = true }
 
 anyhow = { workspace = true }
+clap = { workspace = true, optional = true }
 configparser = { workspace = true }
 fs-err = { workspace = true, features = ["tokio"] }
 itertools = { workspace = true }
diff --git a/crates/uv-toolchain/src/discovery.rs b/crates/uv-toolchain/src/discovery.rs
index 0362443d..689b64b7 100644
--- a/crates/uv-toolchain/src/discovery.rs
+++ b/crates/uv-toolchain/src/discovery.rs
@@ -51,12 +51,15 @@ pub enum ToolchainRequest {
     /// Generally these refer to uv-managed toolchain downloads.
     Key(PythonDownloadRequest),
 }
-
-#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
+#[derive(Debug, Default, Clone, Copy, PartialEq, Eq, serde::Deserialize)]
+#[serde(deny_unknown_fields, rename_all = "kebab-case")]
+#[cfg_attr(feature = "clap", derive(clap::ValueEnum))]
+#[cfg_attr(feature = "schemars", derive(schemars::JsonSchema))]
 pub enum ToolchainPreference {
     /// Only use managed interpreters, never use system interpreters.
     OnlyManaged,
     /// Prefer installed managed interpreters, but use system interpreters if not found.
+    /// If neither can be found, download a managed interpreter.
     #[default]
     PreferInstalledManaged,
     /// Prefer managed interpreters, even if one needs to be downloaded, but use system interpreters if found.
@@ -1177,8 +1180,8 @@ impl ToolchainPreference {
         }
     }
 
-    /// Return a [`ToolchainPreference`] based the given settings.
-    pub fn from_settings(preview: PreviewMode) -> Self {
+    /// Return a default [`ToolchainPreference`] based on the environment and preview mode.
+    pub fn default_from(preview: PreviewMode) -> Self {
         if env::var_os("UV_TEST_PYTHON_PATH").is_some() {
             debug!("Only considering system interpreters due to `UV_TEST_PYTHON_PATH`");
             Self::OnlySystem
diff --git a/crates/uv/Cargo.toml b/crates/uv/Cargo.toml
index 0a47cbaa..1521d4fd 100644
--- a/crates/uv/Cargo.toml
+++ b/crates/uv/Cargo.toml
@@ -33,7 +33,7 @@ uv-normalize = { workspace = true }
 uv-requirements = { workspace = true }
 uv-resolver = { workspace = true, features = ["clap"] }
 uv-settings = { workspace = true, features = ["schemars"] }
-uv-toolchain = { workspace = true }
+uv-toolchain = { workspace = true, features = ["clap", "schemars"]}
 uv-types = { workspace = true }
 uv-virtualenv = { workspace = true }
 uv-warnings = { workspace = true }
diff --git a/crates/uv/src/cli.rs b/crates/uv/src/cli.rs
index f7781f8f..abb11694 100644
--- a/crates/uv/src/cli.rs
+++ b/crates/uv/src/cli.rs
@@ -14,7 +14,7 @@ use uv_configuration::{
 };
 use uv_normalize::{ExtraName, PackageName};
 use uv_resolver::{AnnotationStyle, ExcludeNewer, PreReleaseMode, ResolutionMode};
-use uv_toolchain::PythonVersion;
+use uv_toolchain::{PythonVersion, ToolchainPreference};
 
 use crate::commands::{extra_name_with_clap_error, ListFormat, VersionFormat};
 use crate::compat;
@@ -89,6 +89,10 @@ pub(crate) struct GlobalArgs {
     #[arg(global = true, long, overrides_with("offline"), hide = true)]
     pub(crate) no_offline: bool,
 
+    /// Whether to use system or uv-managed Python toolchains.
+    #[arg(global = true, long)]
+    pub(crate) toolchain_preference: Option<ToolchainPreference>,
+
     /// Whether to enable experimental, preview features.
     #[arg(global = true, long, hide = true, env = "UV_PREVIEW", value_parser = clap::builder::BoolishValueParser::new(), overrides_with("no_preview"))]
     pub(crate) preview: bool,
diff --git a/crates/uv/src/commands/pip/compile.rs b/crates/uv/src/commands/pip/compile.rs
index 0612b4fa..7bc3447f 100644
--- a/crates/uv/src/commands/pip/compile.rs
+++ b/crates/uv/src/commands/pip/compile.rs
@@ -89,6 +89,7 @@ pub(crate) async fn pip_compile(
     link_mode: LinkMode,
     python: Option<String>,
     system: bool,
+    toolchain_preference: ToolchainPreference,
     concurrency: Concurrency,
     native_tls: bool,
     quiet: bool,
@@ -154,11 +155,10 @@ pub(crate) async fn pip_compile(
     }
 
     // Find an interpreter to use for building distributions
-    let preference = ToolchainPreference::from_settings(preview);
     let environments = EnvironmentPreference::from_system_flag(system, false);
     let interpreter = if let Some(python) = python.as_ref() {
         let request = ToolchainRequest::parse(python);
-        Toolchain::find(&request, environments, preference, &cache)
+        Toolchain::find(&request, environments, toolchain_preference, &cache)
     } else {
         // TODO(zanieb): The split here hints at a problem with the abstraction; we should be able to use
         // `Toolchain::find(...)` here.
@@ -168,7 +168,7 @@ pub(crate) async fn pip_compile(
         } else {
             ToolchainRequest::default()
         };
-        Toolchain::find_best(&request, environments, preference, &cache)
+        Toolchain::find_best(&request, environments, toolchain_preference, &cache)
     }?
     .into_interpreter();
 
diff --git a/crates/uv/src/commands/project/add.rs b/crates/uv/src/commands/project/add.rs
index 9a905e57..857b15fc 100644
--- a/crates/uv/src/commands/project/add.rs
+++ b/crates/uv/src/commands/project/add.rs
@@ -6,7 +6,7 @@ use uv_distribution::pyproject_mut::PyProjectTomlMut;
 use uv_git::GitResolver;
 use uv_requirements::{NamedRequirementsResolver, RequirementsSource, RequirementsSpecification};
 use uv_resolver::{FlatIndex, InMemoryIndex, OptionsBuilder};
-use uv_toolchain::ToolchainRequest;
+use uv_toolchain::{ToolchainPreference, ToolchainRequest};
 use uv_types::{BuildIsolation, HashStrategy, InFlight};
 
 use uv_cache::Cache;
@@ -34,6 +34,7 @@ pub(crate) async fn add(
     branch: Option<String>,
     python: Option<String>,
     settings: ResolverInstallerSettings,
+    toolchain_preference: ToolchainPreference,
     preview: PreviewMode,
     connectivity: Connectivity,
     concurrency: Concurrency,
@@ -52,6 +53,7 @@ pub(crate) async fn add(
     let venv = project::init_environment(
         project.workspace(),
         python.as_deref().map(ToolchainRequest::parse),
+        toolchain_preference,
         connectivity,
         native_tls,
         cache,
diff --git a/crates/uv/src/commands/project/lock.rs b/crates/uv/src/commands/project/lock.rs
index 133814dd..2ba87992 100644
--- a/crates/uv/src/commands/project/lock.rs
+++ b/crates/uv/src/commands/project/lock.rs
@@ -18,7 +18,7 @@ use uv_resolver::{
     ExcludeNewer, FlatIndex, InMemoryIndex, Lock, OptionsBuilder, PreReleaseMode, RequiresPython,
     ResolutionMode,
 };
-use uv_toolchain::{Interpreter, ToolchainRequest};
+use uv_toolchain::{Interpreter, ToolchainPreference, ToolchainRequest};
 use uv_types::{BuildIsolation, EmptyInstalledPackages, HashStrategy, InFlight};
 use uv_warnings::warn_user;
 
@@ -33,6 +33,7 @@ pub(crate) async fn lock(
     python: Option<String>,
     settings: ResolverSettings,
     preview: PreviewMode,
+    toolchain_preference: ToolchainPreference,
     connectivity: Connectivity,
     concurrency: Concurrency,
     native_tls: bool,
@@ -50,6 +51,7 @@ pub(crate) async fn lock(
     let interpreter = project::find_interpreter(
         &workspace,
         python.as_deref().map(ToolchainRequest::parse),
+        toolchain_preference,
         connectivity,
         native_tls,
         cache,
diff --git a/crates/uv/src/commands/project/mod.rs b/crates/uv/src/commands/project/mod.rs
index 46b0b4c4..0fad46f1 100644
--- a/crates/uv/src/commands/project/mod.rs
+++ b/crates/uv/src/commands/project/mod.rs
@@ -139,6 +139,7 @@ pub(crate) fn interpreter_meets_requirements(
 pub(crate) async fn find_interpreter(
     workspace: &Workspace,
     python_request: Option<ToolchainRequest>,
+    toolchain_preference: ToolchainPreference,
     connectivity: Connectivity,
     native_tls: bool,
     cache: &Cache,
@@ -183,8 +184,8 @@ pub(crate) async fn find_interpreter(
     // Locate the Python interpreter to use in the environment
     let interpreter = Toolchain::find_or_fetch(
         python_request,
-        EnvironmentPreference::Any,
-        ToolchainPreference::from_settings(PreviewMode::Enabled),
+        EnvironmentPreference::OnlySystem,
+        toolchain_preference,
         client_builder,
         cache,
     )
@@ -215,6 +216,7 @@ pub(crate) async fn find_interpreter(
 pub(crate) async fn init_environment(
     workspace: &Workspace,
     python: Option<ToolchainRequest>,
+    toolchain_preference: ToolchainPreference,
     connectivity: Connectivity,
     native_tls: bool,
     cache: &Cache,
@@ -248,8 +250,16 @@ pub(crate) async fn init_environment(
     };
 
     // Find an interpreter to create the environment with
-    let interpreter =
-        find_interpreter(workspace, python, connectivity, native_tls, cache, printer).await?;
+    let interpreter = find_interpreter(
+        workspace,
+        python,
+        toolchain_preference,
+        connectivity,
+        native_tls,
+        cache,
+        printer,
+    )
+    .await?;
 
     let venv = workspace.venv();
     writeln!(
diff --git a/crates/uv/src/commands/project/remove.rs b/crates/uv/src/commands/project/remove.rs
index da097495..f63d7d19 100644
--- a/crates/uv/src/commands/project/remove.rs
+++ b/crates/uv/src/commands/project/remove.rs
@@ -6,7 +6,7 @@ use uv_client::Connectivity;
 use uv_configuration::{Concurrency, ExtrasSpecification, PreviewMode};
 use uv_distribution::pyproject_mut::PyProjectTomlMut;
 use uv_distribution::ProjectWorkspace;
-use uv_toolchain::ToolchainRequest;
+use uv_toolchain::{ToolchainPreference, ToolchainRequest};
 use uv_warnings::warn_user;
 
 use crate::commands::pip::operations::Modifications;
@@ -20,6 +20,7 @@ pub(crate) async fn remove(
     requirements: Vec<PackageName>,
     dev: bool,
     python: Option<String>,
+    toolchain_preference: ToolchainPreference,
     preview: PreviewMode,
     connectivity: Connectivity,
     concurrency: Concurrency,
@@ -85,6 +86,7 @@ pub(crate) async fn remove(
     let venv = project::init_environment(
         project.workspace(),
         python.as_deref().map(ToolchainRequest::parse),
+        toolchain_preference,
         connectivity,
         native_tls,
         cache,
diff --git a/crates/uv/src/commands/project/run.rs b/crates/uv/src/commands/project/run.rs
index ac21e764..36b887db 100644
--- a/crates/uv/src/commands/project/run.rs
+++ b/crates/uv/src/commands/project/run.rs
@@ -35,6 +35,7 @@ pub(crate) async fn run(
     settings: ResolverInstallerSettings,
     isolated: bool,
     preview: PreviewMode,
+    toolchain_preference: ToolchainPreference,
     connectivity: Connectivity,
     concurrency: Concurrency,
     native_tls: bool,
@@ -65,6 +66,7 @@ pub(crate) async fn run(
         let venv = project::init_environment(
             project.workspace(),
             python.as_deref().map(ToolchainRequest::parse),
+            toolchain_preference,
             connectivity,
             native_tls,
             cache,
@@ -141,7 +143,7 @@ pub(crate) async fn run(
             Toolchain::find_or_fetch(
                 python.as_deref().map(ToolchainRequest::parse),
                 EnvironmentPreference::Any,
-                ToolchainPreference::from_settings(PreviewMode::Enabled),
+                toolchain_preference,
                 client_builder,
                 cache,
             )
diff --git a/crates/uv/src/commands/project/sync.rs b/crates/uv/src/commands/project/sync.rs
index 551ba668..ca1b1f57 100644
--- a/crates/uv/src/commands/project/sync.rs
+++ b/crates/uv/src/commands/project/sync.rs
@@ -16,7 +16,7 @@ use uv_git::GitResolver;
 use uv_installer::SitePackages;
 use uv_normalize::PackageName;
 use uv_resolver::{FlatIndex, InMemoryIndex, Lock};
-use uv_toolchain::{PythonEnvironment, ToolchainRequest};
+use uv_toolchain::{PythonEnvironment, ToolchainPreference, ToolchainRequest};
 use uv_types::{BuildIsolation, HashStrategy, InFlight};
 use uv_warnings::warn_user;
 
@@ -33,6 +33,7 @@ pub(crate) async fn sync(
     dev: bool,
     modifications: Modifications,
     python: Option<String>,
+    toolchain_preference: ToolchainPreference,
     settings: InstallerSettings,
     preview: PreviewMode,
     connectivity: Connectivity,
@@ -52,6 +53,7 @@ pub(crate) async fn sync(
     let venv = project::init_environment(
         project.workspace(),
         python.as_deref().map(ToolchainRequest::parse),
+        toolchain_preference,
         connectivity,
         native_tls,
         cache,
diff --git a/crates/uv/src/commands/tool/run.rs b/crates/uv/src/commands/tool/run.rs
index 2aacde8f..769210fb 100644
--- a/crates/uv/src/commands/tool/run.rs
+++ b/crates/uv/src/commands/tool/run.rs
@@ -30,6 +30,7 @@ pub(crate) async fn run(
     settings: ResolverInstallerSettings,
     _isolated: bool,
     preview: PreviewMode,
+    toolchain_preference: ToolchainPreference,
     connectivity: Connectivity,
     concurrency: Concurrency,
     native_tls: bool,
@@ -73,7 +74,7 @@ pub(crate) async fn run(
             .map(ToolchainRequest::parse)
             .unwrap_or_default(),
         EnvironmentPreference::OnlySystem,
-        ToolchainPreference::from_settings(preview),
+        toolchain_preference,
         cache,
     )?
     .into_interpreter();
diff --git a/crates/uv/src/commands/toolchain/find.rs b/crates/uv/src/commands/toolchain/find.rs
index 6d531cf5..842dd949 100644
--- a/crates/uv/src/commands/toolchain/find.rs
+++ b/crates/uv/src/commands/toolchain/find.rs
@@ -14,6 +14,7 @@ use crate::printer::Printer;
 #[allow(clippy::too_many_arguments)]
 pub(crate) async fn find(
     request: Option<String>,
+    toolchain_preference: ToolchainPreference,
     preview: PreviewMode,
     cache: &Cache,
     printer: Printer,
@@ -29,7 +30,7 @@ pub(crate) async fn find(
     let toolchain = Toolchain::find(
         &request,
         EnvironmentPreference::OnlySystem,
-        ToolchainPreference::from_settings(PreviewMode::Enabled),
+        toolchain_preference,
         cache,
     )?;
 
diff --git a/crates/uv/src/commands/toolchain/list.rs b/crates/uv/src/commands/toolchain/list.rs
index 2eef1777..cf0e61f2 100644
--- a/crates/uv/src/commands/toolchain/list.rs
+++ b/crates/uv/src/commands/toolchain/list.rs
@@ -30,6 +30,7 @@ pub(crate) async fn list(
     kinds: ToolchainListKinds,
     all_versions: bool,
     all_platforms: bool,
+    toolchain_preference: ToolchainPreference,
     preview: PreviewMode,
     cache: &Cache,
     printer: Printer,
@@ -56,7 +57,7 @@ pub(crate) async fn list(
     let installed = find_toolchains(
         &ToolchainRequest::Any,
         EnvironmentPreference::OnlySystem,
-        ToolchainPreference::from_settings(preview),
+        toolchain_preference,
         cache,
     )
     // Raise discovery errors if critical
diff --git a/crates/uv/src/commands/venv.rs b/crates/uv/src/commands/venv.rs
index 7944a09e..b035bd73 100644
--- a/crates/uv/src/commands/venv.rs
+++ b/crates/uv/src/commands/venv.rs
@@ -42,6 +42,7 @@ use crate::shell::Shell;
 pub(crate) async fn venv(
     path: &Path,
     python_request: Option<&str>,
+    toolchain_preference: ToolchainPreference,
     link_mode: LinkMode,
     index_locations: &IndexLocations,
     index_strategy: IndexStrategy,
@@ -69,6 +70,7 @@ pub(crate) async fn venv(
         connectivity,
         seed,
         preview,
+        toolchain_preference,
         allow_existing,
         exclude_newer,
         native_tls,
@@ -118,6 +120,7 @@ async fn venv_impl(
     connectivity: Connectivity,
     seed: bool,
     preview: PreviewMode,
+    toolchain_preference: ToolchainPreference,
     allow_existing: bool,
     exclude_newer: Option<ExcludeNewer>,
     native_tls: bool,
@@ -137,7 +140,7 @@ async fn venv_impl(
     let interpreter = Toolchain::find_or_fetch(
         interpreter_request,
         EnvironmentPreference::OnlySystem,
-        ToolchainPreference::from_settings(preview),
+        toolchain_preference,
         client_builder,
         cache,
     )
diff --git a/crates/uv/src/main.rs b/crates/uv/src/main.rs
index c05ac2af..79a4a57b 100644
--- a/crates/uv/src/main.rs
+++ b/crates/uv/src/main.rs
@@ -140,7 +140,7 @@ async fn run() -> Result<ExitStatus> {
     };
 
     // Resolve the global settings.
-    let globals = GlobalSettings::resolve(&cli.global_args, filesystem.as_ref());
+    let globals = GlobalSettings::resolve(&cli.command, &cli.global_args, filesystem.as_ref());
 
     // Resolve the cache settings.
     let cache_settings = CacheSettings::resolve(cli.cache_args, filesystem.as_ref());
@@ -280,6 +280,7 @@ async fn run() -> Result<ExitStatus> {
                 args.settings.link_mode,
                 args.settings.python,
                 args.settings.system,
+                globals.toolchain_preference,
                 args.settings.concurrency,
                 globals.native_tls,
                 globals.quiet,
@@ -585,6 +586,7 @@ async fn run() -> Result<ExitStatus> {
             commands::venv(
                 &args.name,
                 args.settings.python.as_deref(),
+                globals.toolchain_preference,
                 args.settings.link_mode,
                 &args.settings.index_locations,
                 args.settings.index_strategy,
@@ -626,6 +628,7 @@ async fn run() -> Result<ExitStatus> {
                 args.settings,
                 globals.isolated,
                 globals.preview,
+                globals.toolchain_preference,
                 globals.connectivity,
                 Concurrency::default(),
                 globals.native_tls,
@@ -647,6 +650,7 @@ async fn run() -> Result<ExitStatus> {
                 args.dev,
                 args.modifications,
                 args.python,
+                globals.toolchain_preference,
                 args.settings,
                 globals.preview,
                 globals.connectivity,
@@ -669,6 +673,7 @@ async fn run() -> Result<ExitStatus> {
                 args.python,
                 args.settings,
                 globals.preview,
+                globals.toolchain_preference,
                 globals.connectivity,
                 Concurrency::default(),
                 globals.native_tls,
@@ -696,6 +701,7 @@ async fn run() -> Result<ExitStatus> {
                 args.branch,
                 args.python,
                 args.settings,
+                globals.toolchain_preference,
                 globals.preview,
                 globals.connectivity,
                 Concurrency::default(),
@@ -717,6 +723,7 @@ async fn run() -> Result<ExitStatus> {
                 args.requirements,
                 args.dev,
                 args.python,
+                globals.toolchain_preference,
                 globals.preview,
                 globals.connectivity,
                 Concurrency::default(),
@@ -756,6 +763,7 @@ async fn run() -> Result<ExitStatus> {
                 args.settings,
                 globals.isolated,
                 globals.preview,
+                globals.toolchain_preference,
                 globals.connectivity,
                 Concurrency::default(),
                 globals.native_tls,
@@ -778,6 +786,7 @@ async fn run() -> Result<ExitStatus> {
                 args.kinds,
                 args.all_versions,
                 args.all_platforms,
+                globals.toolchain_preference,
                 globals.preview,
                 &cache,
                 printer,
@@ -814,7 +823,14 @@ async fn run() -> Result<ExitStatus> {
             // Initialize the cache.
             let cache = cache.init()?;
 
-            commands::toolchain_find(args.request, globals.preview, &cache, printer).await
+            commands::toolchain_find(
+                args.request,
+                globals.toolchain_preference,
+                globals.preview,
+                &cache,
+                printer,
+            )
+            .await
         }
     }
 }
diff --git a/crates/uv/src/settings.rs b/crates/uv/src/settings.rs
index 494a07eb..b93f563c 100644
--- a/crates/uv/src/settings.rs
+++ b/crates/uv/src/settings.rs
@@ -22,12 +22,12 @@ use uv_settings::{
     Combine, FilesystemOptions, InstallerOptions, Options, PipOptions, ResolverInstallerOptions,
     ResolverOptions,
 };
-use uv_toolchain::{Prefix, PythonVersion, Target};
+use uv_toolchain::{Prefix, PythonVersion, Target, ToolchainPreference};
 
 use crate::cli::{
-    AddArgs, BuildArgs, ColorChoice, ExternalCommand, GlobalArgs, IndexArgs, InstallerArgs,
-    LockArgs, Maybe, PipCheckArgs, PipCompileArgs, PipFreezeArgs, PipInstallArgs, PipListArgs,
-    PipShowArgs, PipSyncArgs, PipUninstallArgs, RefreshArgs, RemoveArgs, ResolverArgs,
+    AddArgs, BuildArgs, ColorChoice, Commands, ExternalCommand, GlobalArgs, IndexArgs,
+    InstallerArgs, LockArgs, Maybe, PipCheckArgs, PipCompileArgs, PipFreezeArgs, PipInstallArgs,
+    PipListArgs, PipShowArgs, PipSyncArgs, PipUninstallArgs, RefreshArgs, RemoveArgs, ResolverArgs,
     ResolverInstallerArgs, RunArgs, SyncArgs, ToolRunArgs, ToolchainFindArgs, ToolchainInstallArgs,
     ToolchainListArgs, VenvArgs,
 };
@@ -46,11 +46,35 @@ pub(crate) struct GlobalSettings {
     pub(crate) isolated: bool,
     pub(crate) show_settings: bool,
     pub(crate) preview: PreviewMode,
+    pub(crate) toolchain_preference: ToolchainPreference,
 }
 
 impl GlobalSettings {
     /// Resolve the [`GlobalSettings`] from the CLI and filesystem configuration.
-    pub(crate) fn resolve(args: &GlobalArgs, workspace: Option<&FilesystemOptions>) -> Self {
+    pub(crate) fn resolve(
+        command: &Commands,
+        args: &GlobalArgs,
+        workspace: Option<&FilesystemOptions>,
+    ) -> Self {
+        let preview = PreviewMode::from(
+            flag(args.preview, args.no_preview)
+                .combine(workspace.and_then(|workspace| workspace.globals.preview))
+                .unwrap_or(false),
+        );
+
+        // Always use preview mode toolchain preferences during preview commands
+        // TODO(zanieb): There should be a cleaner way to do this, we should probably resolve
+        // force preview to true for these commands but it would break our experimental warning
+        // right now
+        let default_toolchain_preference = if matches!(
+            command,
+            Commands::Project(_) | Commands::Toolchain(_) | Commands::Tool(_)
+        ) {
+            ToolchainPreference::default_from(PreviewMode::Enabled)
+        } else {
+            ToolchainPreference::default_from(preview)
+        };
+
         Self {
             quiet: args.quiet,
             verbose: args.verbose,
@@ -84,11 +108,11 @@ impl GlobalSettings {
             },
             isolated: args.isolated,
             show_settings: args.show_settings,
-            preview: PreviewMode::from(
-                flag(args.preview, args.no_preview)
-                    .combine(workspace.and_then(|workspace| workspace.globals.preview))
-                    .unwrap_or(false),
-            ),
+            preview,
+            toolchain_preference: args
+                .toolchain_preference
+                .combine(workspace.and_then(|workspace| workspace.globals.toolchain_preference))
+                .unwrap_or(default_toolchain_preference),
         }
     }
 }
diff --git a/crates/uv/tests/show_settings.rs b/crates/uv/tests/show_settings.rs
index 8e20e3e2..251c3080 100644
--- a/crates/uv/tests/show_settings.rs
+++ b/crates/uv/tests/show_settings.rs
@@ -57,6 +57,7 @@ fn resolve_uv_toml() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -183,6 +184,7 @@ fn resolve_uv_toml() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -310,6 +312,7 @@ fn resolve_uv_toml() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -469,6 +472,7 @@ fn resolve_pyproject_toml() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -597,6 +601,7 @@ fn resolve_pyproject_toml() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -711,6 +716,7 @@ fn resolve_pyproject_toml() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -862,6 +868,7 @@ fn resolve_index_url() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1013,6 +1020,7 @@ fn resolve_index_url() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1209,6 +1217,7 @@ fn resolve_find_links() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1354,6 +1363,7 @@ fn resolve_top_level() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1474,6 +1484,7 @@ fn resolve_top_level() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1622,6 +1633,7 @@ fn resolve_top_level() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1794,6 +1806,7 @@ fn resolve_user_configuration() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1904,6 +1917,7 @@ fn resolve_user_configuration() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -2014,6 +2028,7 @@ fn resolve_user_configuration() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -2126,6 +2141,7 @@ fn resolve_user_configuration() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
diff --git a/uv.schema.json b/uv.schema.json
index ccce817f..02e2f2f9 100644
--- a/uv.schema.json
+++ b/uv.schema.json
@@ -228,6 +228,16 @@
         "$ref": "#/definitions/Source"
       }
     },
+    "toolchain-preference": {
+      "anyOf": [
+        {
+          "$ref": "#/definitions/ToolchainPreference"
+        },
+        {
+          "type": "null"
+        }
+      ]
+    },
     "upgrade": {
       "type": [
         "boolean",
@@ -1150,6 +1160,45 @@
           }
         }
       }
+    },
+    "ToolchainPreference": {
+      "oneOf": [
+        {
+          "description": "Only use managed interpreters, never use system interpreters.",
+          "type": "string",
+          "enum": [
+            "only-managed"
+          ]
+        },
+        {
+          "description": "Prefer installed managed interpreters, but use system interpreters if not found. If neither can be found, download a managed interpreter.",
+          "type": "string",
+          "enum": [
+            "prefer-installed-managed"
+          ]
+        },
+        {
+          "description": "Prefer managed interpreters, even if one needs to be downloaded, but use system interpreters if found.",
+          "type": "string",
+          "enum": [
+            "prefer-managed"
+          ]
+        },
+        {
+          "description": "Prefer system interpreters, only use managed interpreters if no system interpreter is found.",
+          "type": "string",
+          "enum": [
+            "prefer-system"
+          ]
+        },
+        {
+          "description": "Only use system interpreters, never use managed interpreters.",
+          "type": "string",
+          "enum": [
+            "only-system"
+          ]
+        }
+      ]
     }
   }
 }
\ No newline at end of file
```

## Applicable base-branch guidance

### `CONTRIBUTING.md` (base blob `f7ab2827ee1573d5d9310c7f83ae8e87054a03c4`)

# Contributing

We have issues labeled as [Good First Issue](https://github.com/astral-sh/uv/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) and [Help Wanted](https://github.com/astral-sh/uv/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22) which are good opportunities for new contributors.

## Setup

[Rust](https://rustup.rs/), a C compiler, and CMake are required to build uv.

### Linux

On Ubuntu and other Debian-based distributions, you can install the C compiler and CMake with:

```shell
sudo apt install build-essential cmake
```

### macOS

You can install CMake with Homebrew:

```shell
brew install cmake
```

See the [Python](#python) section for instructions on installing the Python versions.

### Windows

You can install CMake from the [installers](https://cmake.org/download/) or with `pipx install cmake`.

## Testing

For running tests, we recommend [nextest](https://nexte.st/).

If tests fail due to a mismatch in the JSON Schema, run: `cargo dev generate-json-schema`.

### Python

Testing uv requires multiple specific Python versions; they can be installed with:

```shell
cargo run toolchain install
```

The storage directory can be configured with `UV_TOOLCHAIN_DIR`.

### Local testing

You can invoke your development version of uv with `cargo run -- <args>`. For example:

```shell
cargo run -- venv
cargo run -- pip install requests
```

### Testing on Windows

When testing debug builds on Windows, the stack can overflow resulting in a `STATUS_STACK_OVERFLOW` error code.
This is due to a small stack size limit on Windows that we encounter when running unoptimized builds — the release
builds do not have this problem. We [added a `UV_STACK_SIZE` variable](https://github.com/astral-sh/uv/pull/941) to
bypass this problem during testing. We recommend bumping the stack size from the default of 1MB to 2MB, for example:

```powershell
$Env:UV_STACK_SIZE = '2000000'
```

## Running inside a Docker container

Source distributions can run arbitrary code on build and can make unwanted modifications to your system (["Someone's Been Messing With My Subnormals!" on Blogspot](https://moyix.blogspot.com/2022/09/someones-been-messing-with-my-subnormals.html), ["nvidia-pyindex" on PyPI](https://pypi.org/project/nvidia-pyindex/)), which can even occur when just resolving requirements. To prevent this, there's a Docker container you can run commands in:

```bash
docker buildx build -t uv-builder -f builder.dockerfile --load .
# Build for musl to avoid glibc errors, might not be required with your OS version
cargo build --target x86_64-unknown-linux-musl --profile profiling
docker run --rm -it -v $(pwd):/app uv-builder /app/target/x86_64-unknown-linux-musl/profiling/uv-dev resolve-many --cache-dir /app/cache-docker /app/scripts/popular_packages/pypi_10k_most_dependents.txt
```

We recommend using this container if you don't trust the dependency tree of the package(s) you are trying to resolve or install.

## Profiling and Benchmarking

Please refer to Ruff's [Profiling Guide](https://github.com/astral-sh/ruff/blob/main/CONTRIBUTING.md#profiling-projects), it applies to uv, too.

We provide diverse sets of requirements for testing and benchmarking the resolver in `scripts/requirements` and for the installer in `scripts/requirements/compiled`.

You can use `scripts/bench` to benchmark predefined workloads between uv versions and with other tools, e.g.

```
python -m scripts.bench \
    --uv-path ./target/release/before \
    --uv-path ./target/release/after \
    ./scripts/requirements/jupyter.in --benchmark resolve-cold --min-runs 20
```

### Analyzing concurrency

You can use [tracing-durations-export](https://github.com/konstin/tracing-durations-export) to visualize parallel requests and find any spots where uv is CPU-bound. Example usage, with `uv` and `uv-dev` respectively:

```shell
RUST_LOG=uv=info TRACING_DURATIONS_FILE=target/traces/jupyter.ndjson cargo run --features tracing-durations-export --profile profiling -- pip compile scripts/requirements/jupyter.in
```

```shell
RUST_LOG=uv=info TRACING_DURATIONS_FILE=target/traces/jupyter.ndjson cargo run --features tracing-durations-export --bin uv-dev --profile profiling -- resolve jupyter
```

### Trace-level logging

You can enable `trace` level logging using the `RUST_LOG` environment variable, i.e.

```shell
RUST_LOG=trace uv
```

## Releases

Releases can only be performed by Astral team members.

Changelog entries and version bumps are automated. First, run:

```
./scripts/release.sh
```

Then, editorialize the `CHANGELOG.md` file to ensure entries are consistently styled.

Then, open a pull request e.g. `Bump version to ...`.

Binary builds will automatically be tested for the release.

After merging the pull request, run the [release workflow](https://github.com/astral-sh/uv/actions/workflows/release.yml)
with the version tag. **Do not include a leading `v`**.
The release will automatically be created on GitHub after everything else publishes.

## Finding format

Read `/tmp/holdout/skills/panel/references/finding-format.md` before reviewing and follow its finding contract.
## Binding run conditions (apply to you exactly as to the reviewer who dispatched you)

1. Follow the skill snapshot at `/tmp/holdout/skills/panel/` as written — its read discipline, its
   rubric, its output contract. Do not borrow behavior from any other code-review skill.
2. This is a **retrospective review of a merged pull request** (`astral-sh/uv#4424`), reviewed by a
   third party (`kamui`, not the author). Publication is disabled — nothing you produce is posted
   anywhere. Do the analytical work exactly as you would for an open pull request.
3. (Not applicable to you — the run identity and any digest are computed once by the orchestrating
   reviewer, not by finders.)
4. **Clone hygiene.** The clone at `/tmp/holdout/runs/d/panel-seed1` is shared. Do not run
   `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the working
   tree or the index. Read-only git commands (`git show`, `git diff`, `git log`, `git ls-tree`,
   `git blame`, `git grep`) are fine. If you believe you mutated the tree anyway, stop and say so in
   your report rather than trying to fix it.
5. (Not applicable to you — persistence-before-verification is the orchestrating reviewer's
   obligation.)
6. **Stay inside the sandbox.** You may read: the clone at `/tmp/holdout/runs/d/panel-seed1`, the
   skill snapshot at `/tmp/holdout/skills/panel/`, the packet directory at `/tmp/holdout/packets/d/`,
   and your own scratch space under `/tmp/holdout/work/d/panel-seed1/`. Do not read any other
   holdout run's clone, report, or payload, and do not read anything outside these paths. If you do
   read anything outside this list, name the exact path in your report.
8. **No session relays and no asking.** This runs unattended. Never ask the orchestrator or the user
   anything. If an input is genuinely missing, apply your brief's own rule for that situation (the
   Requirements axis's "cannot tell from the code" bucket, or the Code axis's coverage/incomplete
   rule) and say so plainly in your report instead of stopping to ask.

## Additional operational constraints specific to this run

- **Offline.** No `git fetch`, `git pull`, `gh`, `curl`, `curl`-like web fetch, or any network call,
  by you or anything you invoke. The clone's `origin` is a local filesystem path.
- **No execution.** Do not run `cargo`, `rustc`, `uv`, `python` build/test invocations, or any build
  or test script — the toolchain needs network access this sandbox does not have. The review is
  entirely static; reason from the source and say so wherever a claim would ordinarily be settled by
  running something. (You may run the skill's own helper scripts from
  `/tmp/holdout/skills/panel/scripts/`, since those are exempted and do not build or execute the
  project under review.)
- **History is truncated at the pinned head on purpose.** The newest commit reachable in the clone
  is `a2e6b9c6bd0257510240886549ba9e3623299739`. Nothing that happened after this pull request exists
  locally — do not try to work around this. Report explicitly whether you read any history beyond
  the pinned head (base `e783a79955a3a4eb6a4c546f51f89e88b64047bb` to head
  `a2e6b9c6bd0257510240886549ba9e3623299739`) and exactly which history commands you ran, if any.
- Do not attempt to post, comment, or publish anything anywhere; you are producing a candidate
  report only.
## Axis: Code

You are one of two finders reviewing `astral-sh/uv#4424` ("Expose `toolchain-preference` as a CLI
and configuration file option"). Your axis is **Code**. Read
`/tmp/holdout/skills/panel/references/code-axis.md` first, in full, before doing anything else — it
is your brief: what qualifies as a candidate, what does not, the sync-drift sweep, the disposition
ledger, and the exact report shape.

The diff, the changed-file manifest, the commit list, and the applicable base-branch guidance
(`CONTRIBUTING.md`) are already in this prompt, above, under "Pinned run identity", "Changed-file
manifest", "Commit list", "Full diff", and "Applicable base-branch guidance". Do not re-fetch any of
them. No test suite was run for this cell — execution of any kind is not permitted in this sandbox —
so there is no suite-results section to read and you must not attempt to run one yourself.

The repository is a local, offline clone at `/tmp/holdout/runs/d/panel-seed1`, checked out at branch
`review-head` (the pinned head). Branch `main` is force-pinned to the merge-base
(`e783a79955a3a4eb6a4c546f51f89e88b64047bb`), identical to the base SHA here. You may read further
into the repository (enclosing functions, callers, sibling files, conventions) with read-only
commands (`git show <sha>:<path>`, `cat`, `grep`, `git log`, `git blame`, etc.) — do not run
`git checkout`, `git switch`, `git reset`, or `git stash`.

End your report with the fenced `candidates`, `ledger`, and `manifest` blocks exactly as
`code-axis.md` § Report tail specifies (no `counts` block — that is Requirements-only). Return your
full report as your final message; do not write it to a file yourself.
```

**Verbatim report returned (round 1, before shape-validation — this is what
`finder-code-round1-verbatim.md` holds):**

```markdown
## Report: Code-axis review of `astral-sh/uv#4424` ("Expose `toolchain-preference` as a CLI and configuration file option")

### Process note (per binding run conditions)

- Read `/tmp/holdout/work/d/panel-seed1/code-finder-prompt.md` in full (1094 lines) before anything else.
- Read `/tmp/holdout/skills/panel/references/code-axis.md` in full, then `/tmp/holdout/skills/panel/references/finding-format.md` in full (both referenced by the brief).
- Read only inside the allowed paths: the prompt file itself, both reference docs under `/tmp/holdout/skills/panel/`, and the clone at `/tmp/holdout/runs/d/panel-seed1` (working tree checked out at `review-head`, plus one read of the base blob via `git show e783a79955a3a4eb6a4c546f51f89e88b64047bb:crates/uv/src/commands/project/mod.rs`). I did not read the packet directory (`/tmp/holdout/packets/d/`) because nothing in this task required it. No path outside the allowed list was read.
- History: I ran `git log --oneline -3 review-head`, `git log --oneline -3 main`, and `git branch -a` purely to confirm the pinned refs; both logs stayed at or before the base SHA (`baa86f2e`, `30eedb35` are pre-base commits on `main`, which is fine — nothing after head `a2e6b9c6` was read). No `git checkout`/`switch`/`reset`/`stash` was run; only `git show`, `git log`, `git branch -a`, `cat`, `sed -n`, `grep`, and one `python3 -c` snippet used only to parse `uv.schema.json`'s already-read text (no build/execution of the project, no network).
- No `cargo`/`rustc`/`uv`/`python` build or test invocations were run. All conclusions below are from static reading.

### Restated understanding

This is a single-commit PR (`a2e6b9c6`) that threads a new `ToolchainPreference` value end-to-end: renames `ToolchainPreference::from_settings` → `default_from`, adds `serde::Deserialize`/`clap::ValueEnum`/`schemars::JsonSchema` derives (behind new `clap`/existing `schemars` optional-dep features on `uv-toolchain`), adds a `toolchain-preference` global CLI flag and `[tool.uv]`/`uv.toml` config key, adds a `Combine` impl, and rewires ~10 command functions (`pip compile`, `venv`, `tool run`, `toolchain find`, `toolchain list`, and the `project` family — `add`/`remove`/`lock`/`sync`/`run`/`find_interpreter`/`init_environment`) to accept and pass through the resolved preference instead of each hardcoding its own default. `GlobalSettings::resolve` gains a `Commands` parameter so it can reproduce, per command family, the same "force preview-enabled toolchain preference" behavior that `Project`/`Toolchain`/`Tool` commands had before (via a documented `TODO(zanieb)` explaining the compromise), while other commands (`Venv`, `Pip`, …) keep using the real `--preview` flag, matching their pre-PR call sites. `Cargo.lock` and `uv.schema.json` are the generated-artifact updates for the new dependency and new schema field/type.

### Investigation and per-candidate write-ups

I traced every one of the ~10 call-site rewires against their function signatures and confirmed argument order matches in every case (`pip_compile`, `venv`/`venv_impl`, `tool::run`, `project::run`, `project::sync`, `project::lock`, `project::add`, `project::remove`, `toolchain::find`, `toolchain::list`) — no swapped/misplaced positional argument.

I checked `GlobalSettings::resolve`'s new `default_toolchain_preference` branch (`Commands::Project(_) | Commands::Toolchain(_) | Commands::Tool(_)` → `default_from(PreviewMode::Enabled)`, else → `default_from(preview)`) against every pre-PR call site it replaces: `project::mod::find_interpreter`, `project::run`, `tool::run`, `toolchain::find`, `toolchain::list` all previously hardcoded `ToolchainPreference::from_settings(PreviewMode::Enabled)` (forced-enabled regardless of the real `--preview` flag) — exactly reproduced by the `Project|Toolchain|Tool` branch. `venv.rs` and `pip/compile.rs` previously used `ToolchainPreference::from_settings(preview)` (the real flag) — exactly reproduced by the `else` branch, since `Commands::Venv` and `Commands::Pip` aren't in the three matched variants. This is a faithful, deliberate refactor, not a regression.

The one item I weighed hardest: in `crates/uv/src/commands/project/mod.rs:187`, `find_interpreter`'s fallback `Toolchain::find_or_fetch` call changed `EnvironmentPreference::Any` (base) → `EnvironmentPreference::OnlySystem` (head) — a behavior change with no stated rationale in the commit, and unrelated on its face to "expose a CLI flag." I could not establish it as a bug: `find_interpreter`/`init_environment` exist specifically to locate a **base** interpreter for **creating a new project venv**, after already checking (and, in `init_environment`, removing) the project's own venv via `find_environment`; restricting the fallback search to non-venv ("system") sources is consistent with that purpose and arguably more correct than `Any`, which could previously have silently reused an unrelated active/discovered virtualenv as the base for a fresh venv. I found no test or call path that demonstrably breaks under `OnlySystem`, and sibling call site `project/run.rs`'s *ephemeral*-environment lookup (a genuinely different use case — reusing an existing environment for `--with` extras) correctly keeps `EnvironmentPreference::Any` unchanged, which cuts against this being a careless global find-replace. Per the brief's criterion 8 and the "certain, or it's not a candidate" bar for non-bug/non-security items, I'm not raising this — logged as acquitted below so a future re-review doesn't have to re-derive it.

I ran the required sync-drift sweep for every contract this diff touches:
- `ToolchainPreference::from_settings` → `default_from` rename: repo-wide grep for both `from_settings` and `default_from` found zero stale callers (the only other `from_settings` hits are the unrelated `InstalledToolchains::from_settings`/`StateStore::from_settings`).
- The `ToolchainPreference` variant set itself was **not** changed (still `OnlyManaged`/`PreferInstalledManaged`/`PreferManaged`/`PreferSystem`/`OnlySystem`), so there is no retired/opened closed-list to sweep for.
- The new `PreferInstalledManaged` doc-comment sentence ("If neither can be found, download a managed interpreter.") is accurate against `Toolchain::find_or_fetch`'s `preference.allows_managed() && … is_online()` fetch-fallback logic, and is correctly propagated into `uv.schema.json`'s generated description at `uv.schema.json:1164` — verified textually against the source doc comment, no mismatch.
- `uv.schema.json`'s new `"toolchain-preference"` property (`uv.schema.json:231`) and `"ToolchainPreference"` definition match `GlobalOptions.toolchain_preference` (`crates/uv-settings/src/settings.rs:62`) and the enum's variants/order/descriptions exactly, and sit in correct alphabetical position among the schema's other properties/definitions.
- `Cargo.lock`'s new `"clap"` entry under the `uv-toolchain` package (line ~4986) matches the new `clap = { workspace = true, optional = true }` line added at `crates/uv-toolchain/Cargo.toml:31`.
- Searched README.md/CHANGELOG.md/CONTRIBUTING.md for any existing prose list of config/env-var options that would need a `toolchain-preference` entry; found none (this repo, at this point in its history, has no such settings table, and no env-var (`UV_TOOLCHAIN_PREFERENCE`) was added, consistent with there being nothing to update there).

I also checked the `#[serde(deny_unknown_fields, rename_all = "kebab-case")]` addition on `ToolchainPreference` (`discovery.rs:55`) against the repo's convention for similarly-shaped enums (`TargetTriple`, `KeyringProviderType`, `PreReleaseMode`, `ResolutionMode`, `LinkMode`) — all use the identical attribute pair, so this is conforming, not novel rigor. The `uv-toolchain`/`uv` `Cargo.toml` feature wiring (`clap`, `schemars` as implicit optional-dependency features, no explicit `[features]` table) matches the pre-existing `schemars` convention in the same crate.

No candidate met the bar in § "What qualifies as a candidate" of `code-axis.md`.

### Observations

- `crates/uv/Cargo.toml:36` — `uv-toolchain = { workspace = true, features = ["clap", "schemars"]}` is missing a space before the closing brace (every other entry in the file has `} `-style spacing). No TOML formatter/linter runs in this repo's CI at this point in history, so it isn't linter-catchable, and it has zero behavioral effect — noted as an observation, not a candidate.

### Ledger

```ledger
ToolchainPreference::from_settings rename to default_from leaves a stale caller elsewhere in the repo | repo-wide grep for from_settings and default_from | crates/uv-toolchain/src/discovery.rs:1184 | acquitted
find_interpreter's EnvironmentPreference::Any -> OnlySystem swap is an unintended/out-of-scope behavior regression | compare function purpose, base vs head, and sibling call site project/run.rs which kept Any | crates/uv/src/commands/project/mod.rs:187 | acquitted
GlobalSettings::resolve's Project/Toolchain/Tool vs. else default_toolchain_preference branch fails to reproduce one of the five pre-PR hardcoded call sites | matched each pre-diff hardcoded from_settings(PreviewMode) call against the new match arm | crates/uv/src/settings.rs:69-75 | acquitted
Positional argument reordering across the ~10 rewired call sites swaps an argument | cross-checked each function signature against its main.rs call site in declared order | crates/uv/src/main.rs:522-606 | acquitted
Cargo.lock's new clap entry for uv-toolchain does not match the source Cargo.toml change | diffed Cargo.lock hunk against uv-toolchain/Cargo.toml hunk | crates/uv-toolchain/Cargo.toml:31 | acquitted
uv.schema.json's new ToolchainPreference definition/toolchain-preference property diverges from its Rust source (variants, order, doc text, field name) | compared schema hunks to discovery.rs enum and settings.rs field | uv.schema.json:1164 | acquitted
show_settings.rs test snapshots are missing the new toolchain_preference field in some GlobalSettings occurrences | counted GlobalSettings { vs preview: Disabled vs toolchain_preference: OnlySystem occurrences (16/16/16) | crates/uv/tests/show_settings.rs:693 | acquitted
ToolchainPreference's new #[serde(deny_unknown_fields, rename_all = "kebab-case")] derive is a novel/inconsistent rigor for this enum | grepped deny_unknown_fields usage across crates for sibling CLI+config enums | crates/uv-configuration/src/target_triple.rs:11 | acquitted
crates/uv/Cargo.toml uv-toolchain features list missing a space before closing brace | checked for a TOML formatter/lint gate in CI | crates/uv/Cargo.toml:36 | observation
```

### Candidates

````candidates
None.
````

### Manifest

```manifest
Cargo.lock | ignored | generated lockfile; new "clap" dependency edge under the uv-toolchain package matches the new optional clap dep added in crates/uv-toolchain/Cargo.toml
crates/uv-settings/src/combine.rs | reviewed | new import and impl_combine_or!(ToolchainPreference) checked against macro pattern and alphabetical placement, no issue
crates/uv-settings/src/settings.rs | reviewed | new GlobalOptions.toolchain_preference field checked against struct-level kebab-case rename and schemars derive, no issue
crates/uv-toolchain/Cargo.toml | reviewed | new optional clap dependency checked against existing implicit-feature convention (schemars), no issue
crates/uv-toolchain/src/discovery.rs | reviewed | rename from_settings->default_from, new derives, and PreferInstalledManaged doc addition checked against callers, JSON schema, and allows_managed logic, no issue
crates/uv/Cargo.toml | reviewed | feature list addition checked; found a stylistic missing-space nit, logged as observation only
crates/uv/src/cli.rs | reviewed | new --toolchain-preference global arg checked against GlobalArgs conventions and ValueEnum auto-detection, no issue
crates/uv/src/commands/pip/compile.rs | reviewed | new toolchain_preference parameter and call-site replacement checked, no issue
crates/uv/src/commands/project/add.rs | reviewed | new parameter threaded through to init_environment, order verified against main.rs call site, no issue
crates/uv/src/commands/project/lock.rs | reviewed | new parameter threaded through to find_interpreter, order verified, no issue
crates/uv/src/commands/project/mod.rs | reviewed | find_interpreter/init_environment rewired; EnvironmentPreference::Any->OnlySystem change weighed and acquitted (see ledger)
crates/uv/src/commands/project/remove.rs | reviewed | new parameter threaded through to init_environment, order verified, no issue
crates/uv/src/commands/project/run.rs | reviewed | new parameter threaded through both project-env and ephemeral-env paths, EnvironmentPreference::Any correctly left unchanged for the ephemeral path, no issue
crates/uv/src/commands/project/sync.rs | reviewed | new parameter threaded through to init_environment, order verified, no issue
crates/uv/src/commands/tool/run.rs | reviewed | new parameter replaces hardcoded from_settings(preview) call, order verified, no issue
crates/uv/src/commands/toolchain/find.rs | reviewed | new parameter replaces hardcoded from_settings(PreviewMode::Enabled) call, order verified, no issue
crates/uv/src/commands/toolchain/list.rs | reviewed | new parameter replaces hardcoded from_settings(preview) call, order verified, no issue
crates/uv/src/commands/venv.rs | reviewed | new parameter threaded from venv() into venv_impl(), order verified, no issue
crates/uv/src/main.rs | reviewed | GlobalSettings::resolve signature change and all ~10 downstream call sites checked argument-by-argument against their function signatures, no issue
crates/uv/src/settings.rs | reviewed | new default_toolchain_preference per-command logic checked against every pre-PR hardcoded call site it replaces, matches exactly
crates/uv/tests/show_settings.rs | reviewed | all 16 GlobalSettings snapshots updated consistently (16/16/16 occurrence count), no issue
uv.schema.json | ignored | generated JSON schema; new toolchain-preference property and ToolchainPreference definition compared textually against discovery.rs enum and settings.rs field and match exactly
```
```

**Validator result on the round-1 report:** `python3 scripts/validate_finder_report.py --axis code
--manifest manifest.tsv` → exit 1:
```
report:0: block order: the report must end with the blocks ledger, manifest in that order; found candidates, manifest
```

### 4.2 Code finder — round 2 (re-dispatch)

**Model:** `sonnet` (explicit). This was a fresh `Agent` call (not a `SendMessage` continuation),
carrying the original prompt's substance, the finder's own round-1 verbatim report pasted in full,
and the exact violation line, with an explicit instruction not to re-run the investigation — per
`SKILL.md` step 2's re-dispatch instruction.

**Exact prompt given:**

```markdown
You are the Code-axis finder for a review of `astral-sh/uv#4424`, being re-dispatched once because your first submission's report violated the required output shape (a mechanical shape check, not a content problem).

Your original task prompt is unchanged and still applies in full: read `/tmp/holdout/work/d/panel-seed1/code-finder-prompt.md` in full (it contains the pinned run identity, changed-file manifest, commit list, full diff, applicable base-branch guidance, binding run conditions, and the "## Axis: Code" section naming your brief), and follow `/tmp/holdout/skills/panel/references/code-axis.md` and `/tmp/holdout/skills/panel/references/finding-format.md` for the rubric and report shape. Same constraints as before: offline, read-only, no build/test execution, clone hygiene (no checkout/switch/reset/stash), stay inside the clone at `/tmp/holdout/runs/d/panel-seed1`, the skill snapshot, the packet directory, and your own scratch space.

Here is your own prior submission, verbatim, in full:

--- BEGIN YOUR PRIOR SUBMISSION ---
[the round-1 verbatim report reproduced in full in § 4.1 above was pasted here — omitted from this
reproduction to avoid tripling this document's length; it is byte-identical to the "Verbatim report
returned (round 1...)" block in § 4.1]
--- END YOUR PRIOR SUBMISSION ---

Running `python3 /tmp/holdout/skills/panel/scripts/validate_finder_report.py --axis code --manifest <manifest>` on it produced exactly this violation:

```
report:0: block order: the report must end with the blocks ledger, manifest in that order; found candidates, manifest
```

`code-axis.md` § Report tail requires the report to **end with these two fenced blocks, in this order, and no fenced block after them**: `ledger`, then `manifest`. Your prior submission put the fenced ```candidates``` block (required by `finding-format.md` § Finder candidate block, which must still appear somewhere in the report, ending the *candidate material*) in between — after the `ledger` block and before the `manifest` block — so the ledger and manifest are no longer the last two fenced blocks in the document.

**Do not re-run your investigation.** Your conclusions were not the problem — only the document's fenced-block ordering was. Return the exact same review (same restated understanding, same investigation write-ups, same observations, same candidate content, same ledger rows, same manifest rows — unchanged in substance) reshaped so that the fenced ```candidates``` block appears wherever it reads naturally in the body (immediately after "no candidate met the bar" is fine, as before), and then, at the very end of the report with nothing after them, exactly the fenced ```ledger``` block followed by the fenced ```manifest``` block, in that order, both byte-identical in content to your prior submission's ledger and manifest rows.

Return your full, corrected report as your final message text. Do not write it to any file yourself.
```

*(Note: for reproduction purposes above, the "prior submission" block that was actually pasted into
this dispatch's real prompt argument was the full byte-identical text now in § 4.1's "Verbatim report
returned (round 1...)" section — abbreviated here only in this second reproduction to keep this
report file from tripling in size on a re-paste of already-shown content; nothing was abbreviated in
the actual dispatch itself.)*

**Verbatim report returned (round 2 — this is the report used downstream, saved to
`finder-code.md`):**

```markdown
## Report: Code-axis review of `astral-sh/uv#4424` ("Expose `toolchain-preference` as a CLI and configuration file option")

### Process note (per binding run conditions)

- Read `/tmp/holdout/work/d/panel-seed1/code-finder-prompt.md` in full (1094 lines) before anything else.
- Read `/tmp/holdout/skills/panel/references/code-axis.md` in full, then `/tmp/holdout/skills/panel/references/finding-format.md` in full (both referenced by the brief).
- Read only inside the allowed paths: the prompt file itself, both reference docs under `/tmp/holdout/skills/panel/`, and the clone at `/tmp/holdout/runs/d/panel-seed1` (working tree checked out at `review-head`, plus one read of the base blob via `git show e783a79955a3a4eb6a4c546f51f89e88b64047bb:crates/uv/src/commands/project/mod.rs`). I did not read the packet directory (`/tmp/holdout/packets/d/`) because nothing in this task required it. No path outside the allowed list was read.
- History: I ran `git log --oneline -3 review-head`, `git log --oneline -3 main`, and `git branch -a` purely to confirm the pinned refs; both logs stayed at or before the base SHA (`baa86f2e`, `30eedb35` are pre-base commits on `main`, which is fine — nothing after head `a2e6b9c6` was read). No `git checkout`/`switch`/`reset`/`stash` was run; only `git show`, `git log`, `git branch -a`, `cat`, `sed -n`, `grep`, and one `python3 -c` snippet used only to parse `uv.schema.json`'s already-read text (no build/execution of the project, no network).
- No `cargo`/`rustc`/`uv`/`python` build or test invocations were run. All conclusions below are from static reading.

### Restated understanding

This is a single-commit PR (`a2e6b9c6`) that threads a new `ToolchainPreference` value end-to-end: renames `ToolchainPreference::from_settings` → `default_from`, adds `serde::Deserialize`/`clap::ValueEnum`/`schemars::JsonSchema` derives (behind new `clap`/existing `schemars` optional-dep features on `uv-toolchain`), adds a `toolchain-preference` global CLI flag and `[tool.uv]`/`uv.toml` config key, adds a `Combine` impl, and rewires ~10 command functions (`pip compile`, `venv`, `tool run`, `toolchain find`, `toolchain list`, and the `project` family — `add`/`remove`/`lock`/`sync`/`run`/`find_interpreter`/`init_environment`) to accept and pass through the resolved preference instead of each hardcoding its own default. `GlobalSettings::resolve` gains a `Commands` parameter so it can reproduce, per command family, the same "force preview-enabled toolchain preference" behavior that `Project`/`Toolchain`/`Tool` commands had before (via a documented `TODO(zanieb)` explaining the compromise), while other commands (`Venv`, `Pip`, …) keep using the real `--preview` flag, matching their pre-PR call sites. `Cargo.lock` and `uv.schema.json` are the generated-artifact updates for the new dependency and new schema field/type.

### Investigation and per-candidate write-ups

I traced every one of the ~10 call-site rewires against their function signatures and confirmed argument order matches in every case (`pip_compile`, `venv`/`venv_impl`, `tool::run`, `project::run`, `project::sync`, `project::lock`, `project::add`, `project::remove`, `toolchain::find`, `toolchain::list`) — no swapped/misplaced positional argument.

I checked `GlobalSettings::resolve`'s new `default_toolchain_preference` branch (`Commands::Project(_) | Commands::Toolchain(_) | Commands::Tool(_)` → `default_from(PreviewMode::Enabled)`, else → `default_from(preview)`) against every pre-PR call site it replaces: `project::mod::find_interpreter`, `project::run`, `tool::run`, `toolchain::find`, `toolchain::list` all previously hardcoded `ToolchainPreference::from_settings(PreviewMode::Enabled)` (forced-enabled regardless of the real `--preview` flag) — exactly reproduced by the `Project|Toolchain|Tool` branch. `venv.rs` and `pip/compile.rs` previously used `ToolchainPreference::from_settings(preview)` (the real flag) — exactly reproduced by the `else` branch, since `Commands::Venv` and `Commands::Pip` aren't in the three matched variants. This is a faithful, deliberate refactor, not a regression.

The one item I weighed hardest: in `crates/uv/src/commands/project/mod.rs:187`, `find_interpreter`'s fallback `Toolchain::find_or_fetch` call changed `EnvironmentPreference::Any` (base) → `EnvironmentPreference::OnlySystem` (head) — a behavior change with no stated rationale in the commit, and unrelated on its face to "expose a CLI flag." I could not establish it as a bug: `find_interpreter`/`init_environment` exist specifically to locate a **base** interpreter for **creating a new project venv**, after already checking (and, in `init_environment`, removing) the project's own venv via `find_environment`; restricting the fallback search to non-venv ("system") sources is consistent with that purpose and arguably more correct than `Any`, which could previously have silently reused an unrelated active/discovered virtualenv as the base for a fresh venv. I found no test or call path that demonstrably breaks under `OnlySystem`, and sibling call site `project/run.rs`'s *ephemeral*-environment lookup (a genuinely different use case — reusing an existing environment for `--with` extras) correctly keeps `EnvironmentPreference::Any` unchanged, which cuts against this being a careless global find-replace. Per the brief's criterion 8 and the "certain, or it's not a candidate" bar for non-bug/non-security items, I'm not raising this — logged as acquitted below so a future re-review doesn't have to re-derive it.

I ran the required sync-drift sweep for every contract this diff touches:
- `ToolchainPreference::from_settings` → `default_from` rename: repo-wide grep for both `from_settings` and `default_from` found zero stale callers (the only other `from_settings` hits are the unrelated `InstalledToolchains::from_settings`/`StateStore::from_settings`).
- The `ToolchainPreference` variant set itself was **not** changed (still `OnlyManaged`/`PreferInstalledManaged`/`PreferManaged`/`PreferSystem`/`OnlySystem`), so there is no retired/opened closed-list to sweep for.
- The new `PreferInstalledManaged` doc-comment sentence ("If neither can be found, download a managed interpreter.") is accurate against `Toolchain::find_or_fetch`'s `preference.allows_managed() && … is_online()` fetch-fallback logic, and is correctly propagated into `uv.schema.json`'s generated description at `uv.schema.json:1164` — verified textually against the source doc comment, no mismatch.
- `uv.schema.json`'s new `"toolchain-preference"` property (`uv.schema.json:231`) and `"ToolchainPreference"` definition match `GlobalOptions.toolchain_preference` (`crates/uv-settings/src/settings.rs:62`) and the enum's variants/order/descriptions exactly, and sit in correct alphabetical position among the schema's other properties/definitions.
- `Cargo.lock`'s new `"clap"` entry under the `uv-toolchain` package (line ~4986) matches the new `clap = { workspace = true, optional = true }` line added at `crates/uv-toolchain/Cargo.toml:31`.
- Searched README.md/CHANGELOG.md/CONTRIBUTING.md for any existing prose list of config/env-var options that would need a `toolchain-preference` entry; found none (this repo, at this point in its history, has no such settings table, and no env-var (`UV_TOOLCHAIN_PREFERENCE`) was added, consistent with there being nothing to update there).

I also checked the `#[serde(deny_unknown_fields, rename_all = "kebab-case")]` addition on `ToolchainPreference` (`discovery.rs:55`) against the repo's convention for similarly-shaped enums (`TargetTriple`, `KeyringProviderType`, `PreReleaseMode`, `ResolutionMode`, `LinkMode`) — all use the identical attribute pair, so this is conforming, not novel rigor. The `uv-toolchain`/`uv` `Cargo.toml` feature wiring (`clap`, `schemars` as implicit optional-dependency features, no explicit `[features]` table) matches the pre-existing `schemars` convention in the same crate.

No candidate met the bar in § "What qualifies as a candidate" of `code-axis.md`.

````candidates
None.
````

### Observations

- `crates/uv/Cargo.toml:36` — `uv-toolchain = { workspace = true, features = ["clap", "schemars"]}` is missing a space before the closing brace (every other entry in the file has `} `-style spacing). No TOML formatter/linter runs in this repo's CI at this point in history, so it isn't linter-catchable, and it has zero behavioral effect — noted as an observation, not a candidate.

```ledger
ToolchainPreference::from_settings rename to default_from leaves a stale caller elsewhere in the repo | repo-wide grep for from_settings and default_from | crates/uv-toolchain/src/discovery.rs:1184 | acquitted
find_interpreter's EnvironmentPreference::Any -> OnlySystem swap is an unintended/out-of-scope behavior regression | compare function purpose, base vs head, and sibling call site project/run.rs which kept Any | crates/uv/src/commands/project/mod.rs:187 | acquitted
GlobalSettings::resolve's Project/Toolchain/Tool vs. else default_toolchain_preference branch fails to reproduce one of the five pre-PR hardcoded call sites | matched each pre-diff hardcoded from_settings(PreviewMode) call against the new match arm | crates/uv/src/settings.rs:69-75 | acquitted
Positional argument reordering across the ~10 rewired call sites swaps an argument | cross-checked each function signature against its main.rs call site in declared order | crates/uv/src/main.rs:522-606 | acquitted
Cargo.lock's new clap entry for uv-toolchain does not match the source Cargo.toml change | diffed Cargo.lock hunk against uv-toolchain/Cargo.toml hunk | crates/uv-toolchain/Cargo.toml:31 | acquitted
uv.schema.json's new ToolchainPreference definition/toolchain-preference property diverges from its Rust source (variants, order, doc text, field name) | compared schema hunks to discovery.rs enum and settings.rs field | uv.schema.json:1164 | acquitted
show_settings.rs test snapshots are missing the new toolchain_preference field in some GlobalSettings occurrences | counted GlobalSettings { vs preview: Disabled vs toolchain_preference: OnlySystem occurrences (16/16/16) | crates/uv/tests/show_settings.rs:693 | acquitted
ToolchainPreference's new #[serde(deny_unknown_fields, rename_all = "kebab-case")] derive is a novel/inconsistent rigor for this enum | grepped deny_unknown_fields usage across crates for sibling CLI+config enums | crates/uv-configuration/src/target_triple.rs:11 | acquitted
crates/uv/Cargo.toml uv-toolchain features list missing a space before closing brace | checked for a TOML formatter/lint gate in CI | crates/uv/Cargo.toml:36 | observation
```

```manifest
Cargo.lock | ignored | generated lockfile; new "clap" dependency edge under the uv-toolchain package matches the new optional clap dep added in crates/uv-toolchain/Cargo.toml
crates/uv-settings/src/combine.rs | reviewed | new import and impl_combine_or!(ToolchainPreference) checked against macro pattern and alphabetical placement, no issue
crates/uv-settings/src/settings.rs | reviewed | new GlobalOptions.toolchain_preference field checked against struct-level kebab-case rename and schemars derive, no issue
crates/uv-toolchain/Cargo.toml | reviewed | new optional clap dependency checked against existing implicit-feature convention (schemars), no issue
crates/uv-toolchain/src/discovery.rs | reviewed | rename from_settings->default_from, new derives, and PreferInstalledManaged doc addition checked against callers, JSON schema, and allows_managed logic, no issue
crates/uv/Cargo.toml | reviewed | feature list addition checked; found a stylistic missing-space nit, logged as observation only
crates/uv/src/cli.rs | reviewed | new --toolchain-preference global arg checked against GlobalArgs conventions and ValueEnum auto-detection, no issue
crates/uv/src/commands/pip/compile.rs | reviewed | new toolchain_preference parameter and call-site replacement checked, no issue
crates/uv/src/commands/project/add.rs | reviewed | new parameter threaded through to init_environment, order verified against main.rs call site, no issue
crates/uv/src/commands/project/lock.rs | reviewed | new parameter threaded through to find_interpreter, order verified, no issue
crates/uv/src/commands/project/mod.rs | reviewed | find_interpreter/init_environment rewired; EnvironmentPreference::Any->OnlySystem change weighed and acquitted (see ledger)
crates/uv/src/commands/project/remove.rs | reviewed | new parameter threaded through to init_environment, order verified, no issue
crates/uv/src/commands/project/run.rs | reviewed | new parameter threaded through both project-env and ephemeral-env paths, EnvironmentPreference::Any correctly left unchanged for the ephemeral path, no issue
crates/uv/src/commands/project/sync.rs | reviewed | new parameter threaded through to init_environment, order verified, no issue
crates/uv/src/commands/tool/run.rs | reviewed | new parameter replaces hardcoded from_settings(preview) call, order verified, no issue
crates/uv/src/commands/toolchain/find.rs | reviewed | new parameter replaces hardcoded from_settings(PreviewMode::Enabled) call, order verified, no issue
crates/uv/src/commands/toolchain/list.rs | reviewed | new parameter replaces hardcoded from_settings(preview) call, order verified, no issue
crates/uv/src/commands/venv.rs | reviewed | new parameter threaded from venv() into venv_impl(), order verified, no issue
crates/uv/src/main.rs | reviewed | GlobalSettings::resolve signature change and all ~10 downstream call sites checked argument-by-argument against their function signatures, no issue
crates/uv/src/settings.rs | reviewed | new default_toolchain_preference per-command logic checked against every pre-PR hardcoded call site it replaces, matches exactly
crates/uv/tests/show_settings.rs | reviewed | all 16 GlobalSettings snapshots updated consistently (16/16/16 occurrence count), no issue
uv.schema.json | ignored | generated JSON schema; new toolchain-preference property and ToolchainPreference definition compared textually against discovery.rs enum and settings.rs field and match exactly
```
```

**Validator result on the round-2 report:** exit 0. Conforming.


### 4.3 Requirements finder — round 1

**Agent id:** `afcc0ab64c91060eb`. **Model:** `sonnet` (explicit).

**Exact wrapper prompt given (the sub-agent's actual instructions were the file it was told to read,
`/tmp/holdout/work/d/panel-seed1/requirements-finder-prompt.md`, reproduced in § 4.3a below in
full):**

```markdown
Read the file `/tmp/holdout/work/d/panel-seed1/requirements-finder-prompt.md` in full — every line, start to end, it is roughly 1150 lines. That file's entire content IS your actual task prompt: it contains the pinned run identity, changed-file manifest, commit list, full diff, applicable base-branch guidance, a pointer to the finding-format contract, binding run conditions (offline, no execution, clone hygiene, sandbox limits, no asking), and then an "## Axis: Requirements" section naming your brief, the pull request body (your spec surrogate, since there is no originating issue), and an explicit deferral found in the pull request's review comments. Follow it exactly as written, in the order it appears. Do not paraphrase or skip any of it.

In short: you are the Requirements-axis finder in a two-finder code review panel reviewing `astral-sh/uv#4424`, a merged pull request, offline and read-only. You must first read `/tmp/holdout/skills/panel/references/requirements-axis.md` in full (as the file instructs), then apply its process (restate requirements/claims, sort into Met/Not met/Cannot tell, sweep for changed contracts, check for scope creep) to the diff already embedded in the file you read, using the pull request body as your spec surrogate since there is no originating issue. You have access to a local read-only git clone at `/tmp/holdout/runs/d/panel-seed1` (branch `review-head` is the pinned head, branch `main` is pinned to the merge-base) for reading additional context beyond the diff — use read-only git commands only (git show, git diff, git log, git blame, git grep, cat, grep, find); never git checkout/switch/reset/stash. Do not run cargo/rustc/uv/python or any build or test tooling — no network access exists for the toolchain anyway. Do not read anything outside: the clone at /tmp/holdout/runs/d/panel-seed1, the skill snapshot at /tmp/holdout/skills/panel/, the packet directory at /tmp/holdout/packets/d/, and your own scratch space under /tmp/holdout/work/d/panel-seed1/ — if you do, name the exact path in your final report.

Your report must end with these fenced blocks, in this exact order, with nothing after them: `ledger`, `manifest`, `counts` (as `requirements-axis.md` § Report tail specifies). The fenced `candidates` block required by `finding-format.md` § Finder candidate block must appear earlier in the body, not as one of these three trailing blocks.

Produce your full report (restated requirement/claim list, per-candidate write-ups, scope-creep pass, observations, and ending with the exact fenced `candidates`, `ledger`, `manifest`, and `counts` blocks in the order above) as your final message text. Do not write it to any file — return it as your answer.
```

**§ 4.3a — the file the sub-agent was told to read (`requirements-finder-prompt.md`), reproduced
verbatim in full — this is the shared block, the sub-agent guardrails, and the Requirements
axis-specific block (including the PR body and the extracted deferral), concatenated exactly as
built in § 5:**

```markdown
## Pinned run identity

- base ref: `main`
- base SHA: `e783a79955a3a4eb6a4c546f51f89e88b64047bb`
- head SHA: `a2e6b9c6bd0257510240886549ba9e3623299739`
- merge-base: `e783a79955a3a4eb6a4c546f51f89e88b64047bb`

## Changed-file manifest

```text
M	Cargo.lock
M	crates/uv-settings/src/combine.rs
M	crates/uv-settings/src/settings.rs
M	crates/uv-toolchain/Cargo.toml
M	crates/uv-toolchain/src/discovery.rs
M	crates/uv/Cargo.toml
M	crates/uv/src/cli.rs
M	crates/uv/src/commands/pip/compile.rs
M	crates/uv/src/commands/project/add.rs
M	crates/uv/src/commands/project/lock.rs
M	crates/uv/src/commands/project/mod.rs
M	crates/uv/src/commands/project/remove.rs
M	crates/uv/src/commands/project/run.rs
M	crates/uv/src/commands/project/sync.rs
M	crates/uv/src/commands/tool/run.rs
M	crates/uv/src/commands/toolchain/find.rs
M	crates/uv/src/commands/toolchain/list.rs
M	crates/uv/src/commands/venv.rs
M	crates/uv/src/main.rs
M	crates/uv/src/settings.rs
M	crates/uv/tests/show_settings.rs
M	uv.schema.json
```

## Commit list

```text
a2e6b9c6bd0257510240886549ba9e3623299739 Expose `toolchain-preference` as a CLI and configuration file option
```

## Full diff

```diff
diff --git a/Cargo.lock b/Cargo.lock
index 6c09bfab..f5d68f26 100644
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -4983,6 +4983,7 @@ dependencies = [
  "anyhow",
  "assert_fs",
  "cache-key",
+ "clap",
  "configparser",
  "fs-err",
  "futures",
diff --git a/crates/uv-settings/src/combine.rs b/crates/uv-settings/src/combine.rs
index 04eac8fb..1c02fdf8 100644
--- a/crates/uv-settings/src/combine.rs
+++ b/crates/uv-settings/src/combine.rs
@@ -5,7 +5,7 @@ use distribution_types::IndexUrl;
 use install_wheel_rs::linker::LinkMode;
 use uv_configuration::{ConfigSettings, IndexStrategy, KeyringProviderType, TargetTriple};
 use uv_resolver::{AnnotationStyle, ExcludeNewer, PreReleaseMode, ResolutionMode};
-use uv_toolchain::PythonVersion;
+use uv_toolchain::{PythonVersion, ToolchainPreference};
 
 use crate::{FilesystemOptions, PipOptions};
 
@@ -69,6 +69,7 @@ impl_combine_or!(PythonVersion);
 impl_combine_or!(ResolutionMode);
 impl_combine_or!(String);
 impl_combine_or!(TargetTriple);
+impl_combine_or!(ToolchainPreference);
 impl_combine_or!(bool);
 
 impl<T> Combine for Option<Vec<T>> {
diff --git a/crates/uv-settings/src/settings.rs b/crates/uv-settings/src/settings.rs
index f8c2e122..21c8ecb7 100644
--- a/crates/uv-settings/src/settings.rs
+++ b/crates/uv-settings/src/settings.rs
@@ -11,7 +11,7 @@ use uv_configuration::{
 use uv_macros::CombineOptions;
 use uv_normalize::{ExtraName, PackageName};
 use uv_resolver::{AnnotationStyle, ExcludeNewer, PreReleaseMode, ResolutionMode};
-use uv_toolchain::PythonVersion;
+use uv_toolchain::{PythonVersion, ToolchainPreference};
 
 /// A `pyproject.toml` with an (optional) `[tool.uv]` section.
 #[allow(dead_code)]
@@ -59,6 +59,7 @@ pub struct GlobalOptions {
     pub no_cache: Option<bool>,
     pub cache_dir: Option<PathBuf>,
     pub preview: Option<bool>,
+    pub toolchain_preference: Option<ToolchainPreference>,
 }
 
 /// Settings relevant to all installer operations.
diff --git a/crates/uv-toolchain/Cargo.toml b/crates/uv-toolchain/Cargo.toml
index 4e870ccd..096e13af 100644
--- a/crates/uv-toolchain/Cargo.toml
+++ b/crates/uv-toolchain/Cargo.toml
@@ -28,6 +28,7 @@ uv-state = { workspace = true }
 uv-warnings = { workspace = true }
 
 anyhow = { workspace = true }
+clap = { workspace = true, optional = true }
 configparser = { workspace = true }
 fs-err = { workspace = true, features = ["tokio"] }
 itertools = { workspace = true }
diff --git a/crates/uv-toolchain/src/discovery.rs b/crates/uv-toolchain/src/discovery.rs
index 0362443d..689b64b7 100644
--- a/crates/uv-toolchain/src/discovery.rs
+++ b/crates/uv-toolchain/src/discovery.rs
@@ -51,12 +51,15 @@ pub enum ToolchainRequest {
     /// Generally these refer to uv-managed toolchain downloads.
     Key(PythonDownloadRequest),
 }
-
-#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
+#[derive(Debug, Default, Clone, Copy, PartialEq, Eq, serde::Deserialize)]
+#[serde(deny_unknown_fields, rename_all = "kebab-case")]
+#[cfg_attr(feature = "clap", derive(clap::ValueEnum))]
+#[cfg_attr(feature = "schemars", derive(schemars::JsonSchema))]
 pub enum ToolchainPreference {
     /// Only use managed interpreters, never use system interpreters.
     OnlyManaged,
     /// Prefer installed managed interpreters, but use system interpreters if not found.
+    /// If neither can be found, download a managed interpreter.
     #[default]
     PreferInstalledManaged,
     /// Prefer managed interpreters, even if one needs to be downloaded, but use system interpreters if found.
@@ -1177,8 +1180,8 @@ impl ToolchainPreference {
         }
     }
 
-    /// Return a [`ToolchainPreference`] based the given settings.
-    pub fn from_settings(preview: PreviewMode) -> Self {
+    /// Return a default [`ToolchainPreference`] based on the environment and preview mode.
+    pub fn default_from(preview: PreviewMode) -> Self {
         if env::var_os("UV_TEST_PYTHON_PATH").is_some() {
             debug!("Only considering system interpreters due to `UV_TEST_PYTHON_PATH`");
             Self::OnlySystem
diff --git a/crates/uv/Cargo.toml b/crates/uv/Cargo.toml
index 0a47cbaa..1521d4fd 100644
--- a/crates/uv/Cargo.toml
+++ b/crates/uv/Cargo.toml
@@ -33,7 +33,7 @@ uv-normalize = { workspace = true }
 uv-requirements = { workspace = true }
 uv-resolver = { workspace = true, features = ["clap"] }
 uv-settings = { workspace = true, features = ["schemars"] }
-uv-toolchain = { workspace = true }
+uv-toolchain = { workspace = true, features = ["clap", "schemars"]}
 uv-types = { workspace = true }
 uv-virtualenv = { workspace = true }
 uv-warnings = { workspace = true }
diff --git a/crates/uv/src/cli.rs b/crates/uv/src/cli.rs
index f7781f8f..abb11694 100644
--- a/crates/uv/src/cli.rs
+++ b/crates/uv/src/cli.rs
@@ -14,7 +14,7 @@ use uv_configuration::{
 };
 use uv_normalize::{ExtraName, PackageName};
 use uv_resolver::{AnnotationStyle, ExcludeNewer, PreReleaseMode, ResolutionMode};
-use uv_toolchain::PythonVersion;
+use uv_toolchain::{PythonVersion, ToolchainPreference};
 
 use crate::commands::{extra_name_with_clap_error, ListFormat, VersionFormat};
 use crate::compat;
@@ -89,6 +89,10 @@ pub(crate) struct GlobalArgs {
     #[arg(global = true, long, overrides_with("offline"), hide = true)]
     pub(crate) no_offline: bool,
 
+    /// Whether to use system or uv-managed Python toolchains.
+    #[arg(global = true, long)]
+    pub(crate) toolchain_preference: Option<ToolchainPreference>,
+
     /// Whether to enable experimental, preview features.
     #[arg(global = true, long, hide = true, env = "UV_PREVIEW", value_parser = clap::builder::BoolishValueParser::new(), overrides_with("no_preview"))]
     pub(crate) preview: bool,
diff --git a/crates/uv/src/commands/pip/compile.rs b/crates/uv/src/commands/pip/compile.rs
index 0612b4fa..7bc3447f 100644
--- a/crates/uv/src/commands/pip/compile.rs
+++ b/crates/uv/src/commands/pip/compile.rs
@@ -89,6 +89,7 @@ pub(crate) async fn pip_compile(
     link_mode: LinkMode,
     python: Option<String>,
     system: bool,
+    toolchain_preference: ToolchainPreference,
     concurrency: Concurrency,
     native_tls: bool,
     quiet: bool,
@@ -154,11 +155,10 @@ pub(crate) async fn pip_compile(
     }
 
     // Find an interpreter to use for building distributions
-    let preference = ToolchainPreference::from_settings(preview);
     let environments = EnvironmentPreference::from_system_flag(system, false);
     let interpreter = if let Some(python) = python.as_ref() {
         let request = ToolchainRequest::parse(python);
-        Toolchain::find(&request, environments, preference, &cache)
+        Toolchain::find(&request, environments, toolchain_preference, &cache)
     } else {
         // TODO(zanieb): The split here hints at a problem with the abstraction; we should be able to use
         // `Toolchain::find(...)` here.
@@ -168,7 +168,7 @@ pub(crate) async fn pip_compile(
         } else {
             ToolchainRequest::default()
         };
-        Toolchain::find_best(&request, environments, preference, &cache)
+        Toolchain::find_best(&request, environments, toolchain_preference, &cache)
     }?
     .into_interpreter();
 
diff --git a/crates/uv/src/commands/project/add.rs b/crates/uv/src/commands/project/add.rs
index 9a905e57..857b15fc 100644
--- a/crates/uv/src/commands/project/add.rs
+++ b/crates/uv/src/commands/project/add.rs
@@ -6,7 +6,7 @@ use uv_distribution::pyproject_mut::PyProjectTomlMut;
 use uv_git::GitResolver;
 use uv_requirements::{NamedRequirementsResolver, RequirementsSource, RequirementsSpecification};
 use uv_resolver::{FlatIndex, InMemoryIndex, OptionsBuilder};
-use uv_toolchain::ToolchainRequest;
+use uv_toolchain::{ToolchainPreference, ToolchainRequest};
 use uv_types::{BuildIsolation, HashStrategy, InFlight};
 
 use uv_cache::Cache;
@@ -34,6 +34,7 @@ pub(crate) async fn add(
     branch: Option<String>,
     python: Option<String>,
     settings: ResolverInstallerSettings,
+    toolchain_preference: ToolchainPreference,
     preview: PreviewMode,
     connectivity: Connectivity,
     concurrency: Concurrency,
@@ -52,6 +53,7 @@ pub(crate) async fn add(
     let venv = project::init_environment(
         project.workspace(),
         python.as_deref().map(ToolchainRequest::parse),
+        toolchain_preference,
         connectivity,
         native_tls,
         cache,
diff --git a/crates/uv/src/commands/project/lock.rs b/crates/uv/src/commands/project/lock.rs
index 133814dd..2ba87992 100644
--- a/crates/uv/src/commands/project/lock.rs
+++ b/crates/uv/src/commands/project/lock.rs
@@ -18,7 +18,7 @@ use uv_resolver::{
     ExcludeNewer, FlatIndex, InMemoryIndex, Lock, OptionsBuilder, PreReleaseMode, RequiresPython,
     ResolutionMode,
 };
-use uv_toolchain::{Interpreter, ToolchainRequest};
+use uv_toolchain::{Interpreter, ToolchainPreference, ToolchainRequest};
 use uv_types::{BuildIsolation, EmptyInstalledPackages, HashStrategy, InFlight};
 use uv_warnings::warn_user;
 
@@ -33,6 +33,7 @@ pub(crate) async fn lock(
     python: Option<String>,
     settings: ResolverSettings,
     preview: PreviewMode,
+    toolchain_preference: ToolchainPreference,
     connectivity: Connectivity,
     concurrency: Concurrency,
     native_tls: bool,
@@ -50,6 +51,7 @@ pub(crate) async fn lock(
     let interpreter = project::find_interpreter(
         &workspace,
         python.as_deref().map(ToolchainRequest::parse),
+        toolchain_preference,
         connectivity,
         native_tls,
         cache,
diff --git a/crates/uv/src/commands/project/mod.rs b/crates/uv/src/commands/project/mod.rs
index 46b0b4c4..0fad46f1 100644
--- a/crates/uv/src/commands/project/mod.rs
+++ b/crates/uv/src/commands/project/mod.rs
@@ -139,6 +139,7 @@ pub(crate) fn interpreter_meets_requirements(
 pub(crate) async fn find_interpreter(
     workspace: &Workspace,
     python_request: Option<ToolchainRequest>,
+    toolchain_preference: ToolchainPreference,
     connectivity: Connectivity,
     native_tls: bool,
     cache: &Cache,
@@ -183,8 +184,8 @@ pub(crate) async fn find_interpreter(
     // Locate the Python interpreter to use in the environment
     let interpreter = Toolchain::find_or_fetch(
         python_request,
-        EnvironmentPreference::Any,
-        ToolchainPreference::from_settings(PreviewMode::Enabled),
+        EnvironmentPreference::OnlySystem,
+        toolchain_preference,
         client_builder,
         cache,
     )
@@ -215,6 +216,7 @@ pub(crate) async fn find_interpreter(
 pub(crate) async fn init_environment(
     workspace: &Workspace,
     python: Option<ToolchainRequest>,
+    toolchain_preference: ToolchainPreference,
     connectivity: Connectivity,
     native_tls: bool,
     cache: &Cache,
@@ -248,8 +250,16 @@ pub(crate) async fn init_environment(
     };
 
     // Find an interpreter to create the environment with
-    let interpreter =
-        find_interpreter(workspace, python, connectivity, native_tls, cache, printer).await?;
+    let interpreter = find_interpreter(
+        workspace,
+        python,
+        toolchain_preference,
+        connectivity,
+        native_tls,
+        cache,
+        printer,
+    )
+    .await?;
 
     let venv = workspace.venv();
     writeln!(
diff --git a/crates/uv/src/commands/project/remove.rs b/crates/uv/src/commands/project/remove.rs
index da097495..f63d7d19 100644
--- a/crates/uv/src/commands/project/remove.rs
+++ b/crates/uv/src/commands/project/remove.rs
@@ -6,7 +6,7 @@ use uv_client::Connectivity;
 use uv_configuration::{Concurrency, ExtrasSpecification, PreviewMode};
 use uv_distribution::pyproject_mut::PyProjectTomlMut;
 use uv_distribution::ProjectWorkspace;
-use uv_toolchain::ToolchainRequest;
+use uv_toolchain::{ToolchainPreference, ToolchainRequest};
 use uv_warnings::warn_user;
 
 use crate::commands::pip::operations::Modifications;
@@ -20,6 +20,7 @@ pub(crate) async fn remove(
     requirements: Vec<PackageName>,
     dev: bool,
     python: Option<String>,
+    toolchain_preference: ToolchainPreference,
     preview: PreviewMode,
     connectivity: Connectivity,
     concurrency: Concurrency,
@@ -85,6 +86,7 @@ pub(crate) async fn remove(
     let venv = project::init_environment(
         project.workspace(),
         python.as_deref().map(ToolchainRequest::parse),
+        toolchain_preference,
         connectivity,
         native_tls,
         cache,
diff --git a/crates/uv/src/commands/project/run.rs b/crates/uv/src/commands/project/run.rs
index ac21e764..36b887db 100644
--- a/crates/uv/src/commands/project/run.rs
+++ b/crates/uv/src/commands/project/run.rs
@@ -35,6 +35,7 @@ pub(crate) async fn run(
     settings: ResolverInstallerSettings,
     isolated: bool,
     preview: PreviewMode,
+    toolchain_preference: ToolchainPreference,
     connectivity: Connectivity,
     concurrency: Concurrency,
     native_tls: bool,
@@ -65,6 +66,7 @@ pub(crate) async fn run(
         let venv = project::init_environment(
             project.workspace(),
             python.as_deref().map(ToolchainRequest::parse),
+            toolchain_preference,
             connectivity,
             native_tls,
             cache,
@@ -141,7 +143,7 @@ pub(crate) async fn run(
             Toolchain::find_or_fetch(
                 python.as_deref().map(ToolchainRequest::parse),
                 EnvironmentPreference::Any,
-                ToolchainPreference::from_settings(PreviewMode::Enabled),
+                toolchain_preference,
                 client_builder,
                 cache,
             )
diff --git a/crates/uv/src/commands/project/sync.rs b/crates/uv/src/commands/project/sync.rs
index 551ba668..ca1b1f57 100644
--- a/crates/uv/src/commands/project/sync.rs
+++ b/crates/uv/src/commands/project/sync.rs
@@ -16,7 +16,7 @@ use uv_git::GitResolver;
 use uv_installer::SitePackages;
 use uv_normalize::PackageName;
 use uv_resolver::{FlatIndex, InMemoryIndex, Lock};
-use uv_toolchain::{PythonEnvironment, ToolchainRequest};
+use uv_toolchain::{PythonEnvironment, ToolchainPreference, ToolchainRequest};
 use uv_types::{BuildIsolation, HashStrategy, InFlight};
 use uv_warnings::warn_user;
 
@@ -33,6 +33,7 @@ pub(crate) async fn sync(
     dev: bool,
     modifications: Modifications,
     python: Option<String>,
+    toolchain_preference: ToolchainPreference,
     settings: InstallerSettings,
     preview: PreviewMode,
     connectivity: Connectivity,
@@ -52,6 +53,7 @@ pub(crate) async fn sync(
     let venv = project::init_environment(
         project.workspace(),
         python.as_deref().map(ToolchainRequest::parse),
+        toolchain_preference,
         connectivity,
         native_tls,
         cache,
diff --git a/crates/uv/src/commands/tool/run.rs b/crates/uv/src/commands/tool/run.rs
index 2aacde8f..769210fb 100644
--- a/crates/uv/src/commands/tool/run.rs
+++ b/crates/uv/src/commands/tool/run.rs
@@ -30,6 +30,7 @@ pub(crate) async fn run(
     settings: ResolverInstallerSettings,
     _isolated: bool,
     preview: PreviewMode,
+    toolchain_preference: ToolchainPreference,
     connectivity: Connectivity,
     concurrency: Concurrency,
     native_tls: bool,
@@ -73,7 +74,7 @@ pub(crate) async fn run(
             .map(ToolchainRequest::parse)
             .unwrap_or_default(),
         EnvironmentPreference::OnlySystem,
-        ToolchainPreference::from_settings(preview),
+        toolchain_preference,
         cache,
     )?
     .into_interpreter();
diff --git a/crates/uv/src/commands/toolchain/find.rs b/crates/uv/src/commands/toolchain/find.rs
index 6d531cf5..842dd949 100644
--- a/crates/uv/src/commands/toolchain/find.rs
+++ b/crates/uv/src/commands/toolchain/find.rs
@@ -14,6 +14,7 @@ use crate::printer::Printer;
 #[allow(clippy::too_many_arguments)]
 pub(crate) async fn find(
     request: Option<String>,
+    toolchain_preference: ToolchainPreference,
     preview: PreviewMode,
     cache: &Cache,
     printer: Printer,
@@ -29,7 +30,7 @@ pub(crate) async fn find(
     let toolchain = Toolchain::find(
         &request,
         EnvironmentPreference::OnlySystem,
-        ToolchainPreference::from_settings(PreviewMode::Enabled),
+        toolchain_preference,
         cache,
     )?;
 
diff --git a/crates/uv/src/commands/toolchain/list.rs b/crates/uv/src/commands/toolchain/list.rs
index 2eef1777..cf0e61f2 100644
--- a/crates/uv/src/commands/toolchain/list.rs
+++ b/crates/uv/src/commands/toolchain/list.rs
@@ -30,6 +30,7 @@ pub(crate) async fn list(
     kinds: ToolchainListKinds,
     all_versions: bool,
     all_platforms: bool,
+    toolchain_preference: ToolchainPreference,
     preview: PreviewMode,
     cache: &Cache,
     printer: Printer,
@@ -56,7 +57,7 @@ pub(crate) async fn list(
     let installed = find_toolchains(
         &ToolchainRequest::Any,
         EnvironmentPreference::OnlySystem,
-        ToolchainPreference::from_settings(preview),
+        toolchain_preference,
         cache,
     )
     // Raise discovery errors if critical
diff --git a/crates/uv/src/commands/venv.rs b/crates/uv/src/commands/venv.rs
index 7944a09e..b035bd73 100644
--- a/crates/uv/src/commands/venv.rs
+++ b/crates/uv/src/commands/venv.rs
@@ -42,6 +42,7 @@ use crate::shell::Shell;
 pub(crate) async fn venv(
     path: &Path,
     python_request: Option<&str>,
+    toolchain_preference: ToolchainPreference,
     link_mode: LinkMode,
     index_locations: &IndexLocations,
     index_strategy: IndexStrategy,
@@ -69,6 +70,7 @@ pub(crate) async fn venv(
         connectivity,
         seed,
         preview,
+        toolchain_preference,
         allow_existing,
         exclude_newer,
         native_tls,
@@ -118,6 +120,7 @@ async fn venv_impl(
     connectivity: Connectivity,
     seed: bool,
     preview: PreviewMode,
+    toolchain_preference: ToolchainPreference,
     allow_existing: bool,
     exclude_newer: Option<ExcludeNewer>,
     native_tls: bool,
@@ -137,7 +140,7 @@ async fn venv_impl(
     let interpreter = Toolchain::find_or_fetch(
         interpreter_request,
         EnvironmentPreference::OnlySystem,
-        ToolchainPreference::from_settings(preview),
+        toolchain_preference,
         client_builder,
         cache,
     )
diff --git a/crates/uv/src/main.rs b/crates/uv/src/main.rs
index c05ac2af..79a4a57b 100644
--- a/crates/uv/src/main.rs
+++ b/crates/uv/src/main.rs
@@ -140,7 +140,7 @@ async fn run() -> Result<ExitStatus> {
     };
 
     // Resolve the global settings.
-    let globals = GlobalSettings::resolve(&cli.global_args, filesystem.as_ref());
+    let globals = GlobalSettings::resolve(&cli.command, &cli.global_args, filesystem.as_ref());
 
     // Resolve the cache settings.
     let cache_settings = CacheSettings::resolve(cli.cache_args, filesystem.as_ref());
@@ -280,6 +280,7 @@ async fn run() -> Result<ExitStatus> {
                 args.settings.link_mode,
                 args.settings.python,
                 args.settings.system,
+                globals.toolchain_preference,
                 args.settings.concurrency,
                 globals.native_tls,
                 globals.quiet,
@@ -585,6 +586,7 @@ async fn run() -> Result<ExitStatus> {
             commands::venv(
                 &args.name,
                 args.settings.python.as_deref(),
+                globals.toolchain_preference,
                 args.settings.link_mode,
                 &args.settings.index_locations,
                 args.settings.index_strategy,
@@ -626,6 +628,7 @@ async fn run() -> Result<ExitStatus> {
                 args.settings,
                 globals.isolated,
                 globals.preview,
+                globals.toolchain_preference,
                 globals.connectivity,
                 Concurrency::default(),
                 globals.native_tls,
@@ -647,6 +650,7 @@ async fn run() -> Result<ExitStatus> {
                 args.dev,
                 args.modifications,
                 args.python,
+                globals.toolchain_preference,
                 args.settings,
                 globals.preview,
                 globals.connectivity,
@@ -669,6 +673,7 @@ async fn run() -> Result<ExitStatus> {
                 args.python,
                 args.settings,
                 globals.preview,
+                globals.toolchain_preference,
                 globals.connectivity,
                 Concurrency::default(),
                 globals.native_tls,
@@ -696,6 +701,7 @@ async fn run() -> Result<ExitStatus> {
                 args.branch,
                 args.python,
                 args.settings,
+                globals.toolchain_preference,
                 globals.preview,
                 globals.connectivity,
                 Concurrency::default(),
@@ -717,6 +723,7 @@ async fn run() -> Result<ExitStatus> {
                 args.requirements,
                 args.dev,
                 args.python,
+                globals.toolchain_preference,
                 globals.preview,
                 globals.connectivity,
                 Concurrency::default(),
@@ -756,6 +763,7 @@ async fn run() -> Result<ExitStatus> {
                 args.settings,
                 globals.isolated,
                 globals.preview,
+                globals.toolchain_preference,
                 globals.connectivity,
                 Concurrency::default(),
                 globals.native_tls,
@@ -778,6 +786,7 @@ async fn run() -> Result<ExitStatus> {
                 args.kinds,
                 args.all_versions,
                 args.all_platforms,
+                globals.toolchain_preference,
                 globals.preview,
                 &cache,
                 printer,
@@ -814,7 +823,14 @@ async fn run() -> Result<ExitStatus> {
             // Initialize the cache.
             let cache = cache.init()?;
 
-            commands::toolchain_find(args.request, globals.preview, &cache, printer).await
+            commands::toolchain_find(
+                args.request,
+                globals.toolchain_preference,
+                globals.preview,
+                &cache,
+                printer,
+            )
+            .await
         }
     }
 }
diff --git a/crates/uv/src/settings.rs b/crates/uv/src/settings.rs
index 494a07eb..b93f563c 100644
--- a/crates/uv/src/settings.rs
+++ b/crates/uv/src/settings.rs
@@ -22,12 +22,12 @@ use uv_settings::{
     Combine, FilesystemOptions, InstallerOptions, Options, PipOptions, ResolverInstallerOptions,
     ResolverOptions,
 };
-use uv_toolchain::{Prefix, PythonVersion, Target};
+use uv_toolchain::{Prefix, PythonVersion, Target, ToolchainPreference};
 
 use crate::cli::{
-    AddArgs, BuildArgs, ColorChoice, ExternalCommand, GlobalArgs, IndexArgs, InstallerArgs,
-    LockArgs, Maybe, PipCheckArgs, PipCompileArgs, PipFreezeArgs, PipInstallArgs, PipListArgs,
-    PipShowArgs, PipSyncArgs, PipUninstallArgs, RefreshArgs, RemoveArgs, ResolverArgs,
+    AddArgs, BuildArgs, ColorChoice, Commands, ExternalCommand, GlobalArgs, IndexArgs,
+    InstallerArgs, LockArgs, Maybe, PipCheckArgs, PipCompileArgs, PipFreezeArgs, PipInstallArgs,
+    PipListArgs, PipShowArgs, PipSyncArgs, PipUninstallArgs, RefreshArgs, RemoveArgs, ResolverArgs,
     ResolverInstallerArgs, RunArgs, SyncArgs, ToolRunArgs, ToolchainFindArgs, ToolchainInstallArgs,
     ToolchainListArgs, VenvArgs,
 };
@@ -46,11 +46,35 @@ pub(crate) struct GlobalSettings {
     pub(crate) isolated: bool,
     pub(crate) show_settings: bool,
     pub(crate) preview: PreviewMode,
+    pub(crate) toolchain_preference: ToolchainPreference,
 }
 
 impl GlobalSettings {
     /// Resolve the [`GlobalSettings`] from the CLI and filesystem configuration.
-    pub(crate) fn resolve(args: &GlobalArgs, workspace: Option<&FilesystemOptions>) -> Self {
+    pub(crate) fn resolve(
+        command: &Commands,
+        args: &GlobalArgs,
+        workspace: Option<&FilesystemOptions>,
+    ) -> Self {
+        let preview = PreviewMode::from(
+            flag(args.preview, args.no_preview)
+                .combine(workspace.and_then(|workspace| workspace.globals.preview))
+                .unwrap_or(false),
+        );
+
+        // Always use preview mode toolchain preferences during preview commands
+        // TODO(zanieb): There should be a cleaner way to do this, we should probably resolve
+        // force preview to true for these commands but it would break our experimental warning
+        // right now
+        let default_toolchain_preference = if matches!(
+            command,
+            Commands::Project(_) | Commands::Toolchain(_) | Commands::Tool(_)
+        ) {
+            ToolchainPreference::default_from(PreviewMode::Enabled)
+        } else {
+            ToolchainPreference::default_from(preview)
+        };
+
         Self {
             quiet: args.quiet,
             verbose: args.verbose,
@@ -84,11 +108,11 @@ impl GlobalSettings {
             },
             isolated: args.isolated,
             show_settings: args.show_settings,
-            preview: PreviewMode::from(
-                flag(args.preview, args.no_preview)
-                    .combine(workspace.and_then(|workspace| workspace.globals.preview))
-                    .unwrap_or(false),
-            ),
+            preview,
+            toolchain_preference: args
+                .toolchain_preference
+                .combine(workspace.and_then(|workspace| workspace.globals.toolchain_preference))
+                .unwrap_or(default_toolchain_preference),
         }
     }
 }
diff --git a/crates/uv/tests/show_settings.rs b/crates/uv/tests/show_settings.rs
index 8e20e3e2..251c3080 100644
--- a/crates/uv/tests/show_settings.rs
+++ b/crates/uv/tests/show_settings.rs
@@ -57,6 +57,7 @@ fn resolve_uv_toml() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -183,6 +184,7 @@ fn resolve_uv_toml() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -310,6 +312,7 @@ fn resolve_uv_toml() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -469,6 +472,7 @@ fn resolve_pyproject_toml() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -597,6 +601,7 @@ fn resolve_pyproject_toml() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -711,6 +716,7 @@ fn resolve_pyproject_toml() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -862,6 +868,7 @@ fn resolve_index_url() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1013,6 +1020,7 @@ fn resolve_index_url() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1209,6 +1217,7 @@ fn resolve_find_links() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1354,6 +1363,7 @@ fn resolve_top_level() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1474,6 +1484,7 @@ fn resolve_top_level() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1622,6 +1633,7 @@ fn resolve_top_level() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1794,6 +1806,7 @@ fn resolve_user_configuration() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -1904,6 +1917,7 @@ fn resolve_user_configuration() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -2014,6 +2028,7 @@ fn resolve_user_configuration() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
@@ -2126,6 +2141,7 @@ fn resolve_user_configuration() -> anyhow::Result<()> {
         isolated: false,
         show_settings: true,
         preview: Disabled,
+        toolchain_preference: OnlySystem,
     }
     CacheSettings {
         no_cache: false,
diff --git a/uv.schema.json b/uv.schema.json
index ccce817f..02e2f2f9 100644
--- a/uv.schema.json
+++ b/uv.schema.json
@@ -228,6 +228,16 @@
         "$ref": "#/definitions/Source"
       }
     },
+    "toolchain-preference": {
+      "anyOf": [
+        {
+          "$ref": "#/definitions/ToolchainPreference"
+        },
+        {
+          "type": "null"
+        }
+      ]
+    },
     "upgrade": {
       "type": [
         "boolean",
@@ -1150,6 +1160,45 @@
           }
         }
       }
+    },
+    "ToolchainPreference": {
+      "oneOf": [
+        {
+          "description": "Only use managed interpreters, never use system interpreters.",
+          "type": "string",
+          "enum": [
+            "only-managed"
+          ]
+        },
+        {
+          "description": "Prefer installed managed interpreters, but use system interpreters if not found. If neither can be found, download a managed interpreter.",
+          "type": "string",
+          "enum": [
+            "prefer-installed-managed"
+          ]
+        },
+        {
+          "description": "Prefer managed interpreters, even if one needs to be downloaded, but use system interpreters if found.",
+          "type": "string",
+          "enum": [
+            "prefer-managed"
+          ]
+        },
+        {
+          "description": "Prefer system interpreters, only use managed interpreters if no system interpreter is found.",
+          "type": "string",
+          "enum": [
+            "prefer-system"
+          ]
+        },
+        {
+          "description": "Only use system interpreters, never use managed interpreters.",
+          "type": "string",
+          "enum": [
+            "only-system"
+          ]
+        }
+      ]
     }
   }
 }
\ No newline at end of file
```

## Applicable base-branch guidance

### `CONTRIBUTING.md` (base blob `f7ab2827ee1573d5d9310c7f83ae8e87054a03c4`)

# Contributing

We have issues labeled as [Good First Issue](https://github.com/astral-sh/uv/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) and [Help Wanted](https://github.com/astral-sh/uv/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22) which are good opportunities for new contributors.

## Setup

[Rust](https://rustup.rs/), a C compiler, and CMake are required to build uv.

### Linux

On Ubuntu and other Debian-based distributions, you can install the C compiler and CMake with:

```shell
sudo apt install build-essential cmake
```

### macOS

You can install CMake with Homebrew:

```shell
brew install cmake
```

See the [Python](#python) section for instructions on installing the Python versions.

### Windows

You can install CMake from the [installers](https://cmake.org/download/) or with `pipx install cmake`.

## Testing

For running tests, we recommend [nextest](https://nexte.st/).

If tests fail due to a mismatch in the JSON Schema, run: `cargo dev generate-json-schema`.

### Python

Testing uv requires multiple specific Python versions; they can be installed with:

```shell
cargo run toolchain install
```

The storage directory can be configured with `UV_TOOLCHAIN_DIR`.

### Local testing

You can invoke your development version of uv with `cargo run -- <args>`. For example:

```shell
cargo run -- venv
cargo run -- pip install requests
```

### Testing on Windows

When testing debug builds on Windows, the stack can overflow resulting in a `STATUS_STACK_OVERFLOW` error code.
This is due to a small stack size limit on Windows that we encounter when running unoptimized builds — the release
builds do not have this problem. We [added a `UV_STACK_SIZE` variable](https://github.com/astral-sh/uv/pull/941) to
bypass this problem during testing. We recommend bumping the stack size from the default of 1MB to 2MB, for example:

```powershell
$Env:UV_STACK_SIZE = '2000000'
```

## Running inside a Docker container

Source distributions can run arbitrary code on build and can make unwanted modifications to your system (["Someone's Been Messing With My Subnormals!" on Blogspot](https://moyix.blogspot.com/2022/09/someones-been-messing-with-my-subnormals.html), ["nvidia-pyindex" on PyPI](https://pypi.org/project/nvidia-pyindex/)), which can even occur when just resolving requirements. To prevent this, there's a Docker container you can run commands in:

```bash
docker buildx build -t uv-builder -f builder.dockerfile --load .
# Build for musl to avoid glibc errors, might not be required with your OS version
cargo build --target x86_64-unknown-linux-musl --profile profiling
docker run --rm -it -v $(pwd):/app uv-builder /app/target/x86_64-unknown-linux-musl/profiling/uv-dev resolve-many --cache-dir /app/cache-docker /app/scripts/popular_packages/pypi_10k_most_dependents.txt
```

We recommend using this container if you don't trust the dependency tree of the package(s) you are trying to resolve or install.

## Profiling and Benchmarking

Please refer to Ruff's [Profiling Guide](https://github.com/astral-sh/ruff/blob/main/CONTRIBUTING.md#profiling-projects), it applies to uv, too.

We provide diverse sets of requirements for testing and benchmarking the resolver in `scripts/requirements` and for the installer in `scripts/requirements/compiled`.

You can use `scripts/bench` to benchmark predefined workloads between uv versions and with other tools, e.g.

```
python -m scripts.bench \
    --uv-path ./target/release/before \
    --uv-path ./target/release/after \
    ./scripts/requirements/jupyter.in --benchmark resolve-cold --min-runs 20
```

### Analyzing concurrency

You can use [tracing-durations-export](https://github.com/konstin/tracing-durations-export) to visualize parallel requests and find any spots where uv is CPU-bound. Example usage, with `uv` and `uv-dev` respectively:

```shell
RUST_LOG=uv=info TRACING_DURATIONS_FILE=target/traces/jupyter.ndjson cargo run --features tracing-durations-export --profile profiling -- pip compile scripts/requirements/jupyter.in
```

```shell
RUST_LOG=uv=info TRACING_DURATIONS_FILE=target/traces/jupyter.ndjson cargo run --features tracing-durations-export --bin uv-dev --profile profiling -- resolve jupyter
```

### Trace-level logging

You can enable `trace` level logging using the `RUST_LOG` environment variable, i.e.

```shell
RUST_LOG=trace uv
```

## Releases

Releases can only be performed by Astral team members.

Changelog entries and version bumps are automated. First, run:

```
./scripts/release.sh
```

Then, editorialize the `CHANGELOG.md` file to ensure entries are consistently styled.

Then, open a pull request e.g. `Bump version to ...`.

Binary builds will automatically be tested for the release.

After merging the pull request, run the [release workflow](https://github.com/astral-sh/uv/actions/workflows/release.yml)
with the version tag. **Do not include a leading `v`**.
The release will automatically be created on GitHub after everything else publishes.

## Finding format

Read `/tmp/holdout/skills/panel/references/finding-format.md` before reviewing and follow its finding contract.
## Binding run conditions (apply to you exactly as to the reviewer who dispatched you)

1. Follow the skill snapshot at `/tmp/holdout/skills/panel/` as written — its read discipline, its
   rubric, its output contract. Do not borrow behavior from any other code-review skill.
2. This is a **retrospective review of a merged pull request** (`astral-sh/uv#4424`), reviewed by a
   third party (`kamui`, not the author). Publication is disabled — nothing you produce is posted
   anywhere. Do the analytical work exactly as you would for an open pull request.
3. (Not applicable to you — the run identity and any digest are computed once by the orchestrating
   reviewer, not by finders.)
4. **Clone hygiene.** The clone at `/tmp/holdout/runs/d/panel-seed1` is shared. Do not run
   `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the working
   tree or the index. Read-only git commands (`git show`, `git diff`, `git log`, `git ls-tree`,
   `git blame`, `git grep`) are fine. If you believe you mutated the tree anyway, stop and say so in
   your report rather than trying to fix it.
5. (Not applicable to you — persistence-before-verification is the orchestrating reviewer's
   obligation.)
6. **Stay inside the sandbox.** You may read: the clone at `/tmp/holdout/runs/d/panel-seed1`, the
   skill snapshot at `/tmp/holdout/skills/panel/`, the packet directory at `/tmp/holdout/packets/d/`,
   and your own scratch space under `/tmp/holdout/work/d/panel-seed1/`. Do not read any other
   holdout run's clone, report, or payload, and do not read anything outside these paths. If you do
   read anything outside this list, name the exact path in your report.
8. **No session relays and no asking.** This runs unattended. Never ask the orchestrator or the user
   anything. If an input is genuinely missing, apply your brief's own rule for that situation (the
   Requirements axis's "cannot tell from the code" bucket, or the Code axis's coverage/incomplete
   rule) and say so plainly in your report instead of stopping to ask.

## Additional operational constraints specific to this run

- **Offline.** No `git fetch`, `git pull`, `gh`, `curl`, `curl`-like web fetch, or any network call,
  by you or anything you invoke. The clone's `origin` is a local filesystem path.
- **No execution.** Do not run `cargo`, `rustc`, `uv`, `python` build/test invocations, or any build
  or test script — the toolchain needs network access this sandbox does not have. The review is
  entirely static; reason from the source and say so wherever a claim would ordinarily be settled by
  running something. (You may run the skill's own helper scripts from
  `/tmp/holdout/skills/panel/scripts/`, since those are exempted and do not build or execute the
  project under review.)
- **History is truncated at the pinned head on purpose.** The newest commit reachable in the clone
  is `a2e6b9c6bd0257510240886549ba9e3623299739`. Nothing that happened after this pull request exists
  locally — do not try to work around this. Report explicitly whether you read any history beyond
  the pinned head (base `e783a79955a3a4eb6a4c546f51f89e88b64047bb` to head
  `a2e6b9c6bd0257510240886549ba9e3623299739`) and exactly which history commands you ran, if any.
- Do not attempt to post, comment, or publish anything anywhere; you are producing a candidate
  report only.
## Axis: Requirements

You are one of two finders reviewing `astral-sh/uv#4424` ("Expose `toolchain-preference` as a CLI
and configuration file option"). Your axis is **Requirements**. Read
`/tmp/holdout/skills/panel/references/requirements-axis.md` first, in full, before doing anything
else — it is your brief: restating requirements, sorting them, the peer-contract sweep, the
scope-creep pass, the disposition ledger, the counts, and the exact report shape.

The diff, the changed-file manifest, the commit list, and the applicable base-branch guidance
(`CONTRIBUTING.md`) are already in this prompt, above, under "Pinned run identity", "Changed-file
manifest", "Commit list", "Full diff", and "Applicable base-branch guidance". Do not re-fetch any of
them. No test suite was run for this cell — execution of any kind is not permitted in this sandbox —
so there is no suite-results section to read and you must not attempt to run one yourself.

**There is no originating issue.** The pull request body carries no closing reference (`Closes #n`,
`Fixes #n`, or a bare `#n`), and none was found by branch name or commit message either. Your spec
surrogate is the **pull request body**, reproduced verbatim below — follow `requirements-axis.md`
§ No issue: restate every behavioral claim and every explicit non-goal the body makes, sort each
into Met / Not met / Cannot tell from the code, and say plainly in your report that issue alignment
is unavailable.

### Pull request body, verbatim

```
Exposes the option added in #4416. Adds `--toolchain-preference` and
`tool.uv.toolchain-preference` to configure if system or managed toolchains are preferred. Users
can opt-out of managed toolchains or system toolchains entirely as well.
```

### Explicit deferrals found in the pull request's review comments (verbatim, this is everything from prior review you are given on this first review)

One explicit deferral of a naming decision was found, from the non-review conversation on the pull
request. It concerns the name and value vocabulary of the new `--toolchain-preference` CLI flag /
`tool.uv.toolchain-preference` configuration key that this diff introduces:

> **Author:** `zanieb`
> **When:** 2024-06-20T17:27:06Z
> **Surface:** the naming of the `--toolchain-preference` flag / `toolchain-preference` config key
> and its value vocabulary (the discussion running immediately before and after this comment is
> about whether the option should be named `--toolchains` instead, whether the `prefer-*` value
> prefix should be dropped, e.g. `managed | system | only-managed | only-system |
> installed-managed`, and the "prefer" vs "prefer" redundancy `BurntSushi` raised in the review).
>
> ```
> I'm fine adjusting this later if we need to since it's in preview.
> ```

For your own context only (do not treat as a second deferral or as a requirement, and do not check
compliance with this the way you would an issue requirement) here is the surrounding non-review
conversation, verbatim and in order, that the deferral above sits inside — it may help you judge
whether the current name is a live open question or already resolved by the time of the head you are
reviewing:

1. 2024-06-20T16:27:45Z · `zanieb`: "Should we bikeshed the name? Should it just be `--toolchains`?"
2. 2024-06-20T17:21:53Z · `BurntSushi` (review, APPROVED, on commit `c64a2c895`): "LGTM. As for the
   name... Is this something that you think will be commonly used on the CLI? If so, I think I'd
   favor a shorter name. Otherwise, I like the descriptiveness of `--toolchain-preference`. One
   other possible downside is redundancy here. Namely, `--toolchain-preference prefer-system` has
   "prefer" twice in it, but arguably is just as clear if "prefer" only appeared once. Not quite
   sure what the right answer is there."
3. 2024-06-20T17:23:47Z · `zanieb`: "> One other possible downside is redundancy here. Namely,
   --toolchain-preference prefer-system has "prefer" twice in it, but arguably is just as clear if
   "prefer" only appeared once. Agree, this is a source of discomfort for me but idk it's also very
   clear. I don't expect this to be used much from the CLI — mostly as a persistent configuration
   option."
4. 2024-06-20T17:27:06Z · `zanieb`: "I'm fine adjusting this later if we need to since it's in
   preview." *(this is the deferral quoted above)*
5. 2024-06-20T18:26:17Z · `zanieb`: "I guess another option is I drop the `prefer` prefix so we'd
   have `toolchain-preference = managed | system | only-managed | only-system |
   installed-managed` which is pretty reasonable too?"
6. 2024-06-20T18:27:33Z · `BurntSushi`: "> I guess another option is I drop the `prefer` prefix so
   we'd have `toolchain-preference = managed | system | only-managed | only-system |
   installed-managed` which is pretty reasonable too? I think that's probably okay. I thought of
   that too, but wondered whether it might leave folks wondering the difference between `managed`
   and `only-managed`."

Nothing else from prior review reaches you on this first review — do not fetch the rest of the
review threads.

The repository is a local, offline clone at `/tmp/holdout/runs/d/panel-seed1`, checked out at branch
`review-head` (the pinned head). Branch `main` is force-pinned to the merge-base
(`e783a79955a3a4eb6a4c546f51f89e88b64047bb`), identical to the base SHA here. You may read further
into the repository (enclosing functions, callers, sibling files, conventions) with read-only
commands — do not run `git checkout`, `git switch`, `git reset`, or `git stash`.

End your report with the fenced `candidates`, `ledger`, `manifest`, and `counts` blocks exactly as
`requirements-axis.md` § Report tail specifies. Return your full report as your final message; do
not write it to a file yourself.
```

**Verbatim report returned (round 1, before shape-validation — this is what
`finder-requirements-round1-verbatim.md` holds, corrected to the true verbatim text after I caught my
own transcription slip; see § 2):**

```markdown
# Requirements-axis finder report — `astral-sh/uv#4424`

## Read-order and scope compliance

Read, in this order: `/tmp/holdout/work/d/panel-seed1/requirements-finder-prompt.md` (full, ~1150 lines) → `/tmp/holdout/skills/panel/references/requirements-axis.md` (full) → `/tmp/holdout/skills/panel/references/finding-format.md` (full). Then investigated the clone at `/tmp/holdout/runs/d/panel-seed1`.

- **No history beyond the pinned head was read.** Git commands run: `git branch -a`, `git status --short`, `git rev-parse HEAD`, `git log -1 --format=... a2e6b9c6...` (the pinned head commit itself, no ancestor walk), `git grep -n ... review-head -- ...` (working-tree content at the pinned head only), `git show review-head:<path>` (content at pinned head), `git show e783a79955a3a4eb6a4c546f51f89e88b64047bb:<path>` (content at the pinned base/merge-base, explicitly in scope as the comparison point). No `git log` range walks, no `git fetch`/`git pull`, no `checkout`/`switch`/`reset`/`stash`.
- **No execution.** No `cargo`/`rustc`/`uv`/`python` invocations of any kind.
- **Sandbox paths.** Only read: the task prompt file, the two skill reference files above, and files inside the `/tmp/holdout/runs/d/panel-seed1` clone (via `git show`/`git grep`). Did not read `/tmp/holdout/packets/d/` or anything outside the permitted list.
- **No originating issue.** Per instructions, the pull request body is the spec surrogate. Issue alignment is therefore unavailable for this review; the "compliance" pass below is instead a body-claims ledger, walking claim → code, as `requirements-axis.md` § No issue requires.

## Restated claim/requirement list (from the PR body, verbatim quoted where relevant)

Body: *"Exposes the option added in #4416. Adds `--toolchain-preference` and `tool.uv.toolchain-preference` to configure if system or managed toolchains are preferred. Users can opt-out of managed toolchains or system toolchains entirely as well."*

- **B0 (background, not a claim)** — "Exposes the option added in #4416." This is context (the `ToolchainPreference` enum and its discovery semantics already existed pre-diff), not itself a checkable behavioral claim. Not sorted, not counted.
- **B1** — Adds a `--toolchain-preference` CLI option.
- **B2** — Adds a `tool.uv.toolchain-preference` configuration-file option.
- **B3** — Both surfaces actually let a user "configure if system or managed toolchains are preferred" (i.e., the value is correctly parsed, combined CLI-over-config-over-default, and threaded into interpreter discovery).
- **B4** — Users can opt out of managed toolchains entirely (i.e., an "only system" value exists and is enforced).
- **B5** — Users can opt out of system toolchains entirely (i.e., an "only managed" value exists and is enforced).
- **B6 (deferred decision, its own restated entry per `requirements-axis.md` § Step 2)** — The name `--toolchain-preference` / `toolchain-preference` and its value vocabulary (the `prefer-*` prefix, `--toolchains` alternative, "prefer … prefer" redundancy) was an open bikeshed at review time, explicitly deferred by `zanieb` (2024-06-20T17:27:06Z): *"I'm fine adjusting this later if we need to since it's in preview."* No repository rule (style guide, `CONTRIBUTING.md`) settles CLI-flag naming conventions, so this cannot be resolved by rule and stays a question.

## Sorting

**B1 — Met.** `crates/uv/src/cli.rs:174-175` adds `pub(crate) toolchain_preference: Option<ToolchainPreference>` to `GlobalArgs` with `#[arg(global = true, long)]`, i.e. `--toolchain-preference`, taking `ToolchainPreference` values via its new `clap::ValueEnum` derive (`crates/uv-toolchain/src/discovery.rs:120-124`).

**B2 — Met.** `crates/uv-settings/src/settings.rs:65` adds `pub toolchain_preference: Option<ToolchainPreference>` to `GlobalOptions`, which is `#[serde(flatten)]`ed into `Options` (the `[tool.uv]` schema) with `#[serde(rename_all = "kebab-case")]` on the struct, so the TOML key is `toolchain-preference`, matching the body's `tool.uv.toolchain-preference`. `uv.schema.json:231-834` (base version) gains the corresponding `toolchain-preference` property and `ToolchainPreference` definition.

**B3 — Met.** `crates/uv/src/settings.rs` (`GlobalSettings::resolve`) computes `toolchain_preference: args.toolchain_preference.combine(workspace...).unwrap_or(default_toolchain_preference)`. `Combine for Option<ToolchainPreference>` is `self.or(other)` (`crates/uv-settings/src/combine.rs:73`, via `impl_combine_or!`), so CLI beats config file beats the preview-aware default — correct precedence. `globals.toolchain_preference` is then threaded into every call site that previously hardcoded `ToolchainPreference::from_settings(...)`: `pip compile` (`compile.rs:161,171`), `venv` (`venv.rs:140`), `run`/`sync`/`lock`/`add`/`remove` (via `project::find_interpreter`/`init_environment`, `mod.rs:187`, `lock.rs`, `add.rs`, `remove.rs`, `sync.rs`), `tool run` (`tool/run.rs:71`), `toolchain find` (`toolchain/find.rs:30`), `toolchain list` (`toolchain/list.rs:57`) — all ten call sites in `main.rs` pass `globals.toolchain_preference` to match. `pip install`/`pip sync`/etc. legitimately don't take it: they resolve an *existing* environment via `PythonEnvironment::find` (`install.rs:119`, `sync.rs:114`), not fresh toolchain discovery/download, so `ToolchainPreference` doesn't apply there — not a gap.

**B4/B5 — Met.** `ToolchainPreference::allows` (`discovery.rs:1153-1179`, unchanged by this diff, pre-existing from #4416) enforces `OnlyManaged` ⇒ only `ToolchainSource::Managed`, and `OnlySystem` ⇒ only `SearchPath`/`PyLauncher`; the discovery-source iterator builder (`discovery.rs:317-336`) likewise restricts `OnlyManaged` to `from_managed_toolchains` alone and `OnlySystem` to `from_search_path.chain(from_py_launcher)` alone. Both opt-out values exist, are now user-reachable via B1/B2, and are enforced.

**B6 — Cannot tell from the code / Question.** This is a live naming/value-vocabulary bikeshed explicitly deferred by the author on unreleased (preview) public surface, with no repository rule to settle it. Per `requirements-axis.md` § Step 2 it resolves to the "cannot tell" bucket as a question, not a defect claim, and makes this axis `Waiting for information` rather than `Passed`.

> No static evidence can settle whether `--toolchain-preference` / `prefer-installed-managed` etc. is the name the maintainers intend to ship, because the deferral says explicitly that it may still change ("I'm fine adjusting this later … since it's in preview") and the review thread ends without a final decision recorded in the material supplied to this axis. What would settle it: a later commit or release note (outside this pinned head) either renaming the flag/values or a maintainer statement closing the bikeshed — neither of which exists in the history available to this run.

## Changed-contract sweep

**Contract: `ToolchainPreference::from_settings(preview: PreviewMode)` renamed to `ToolchainPreference::default_from(preview: PreviewMode)`**, plus the enum gaining `serde::Deserialize` (`#[serde(deny_unknown_fields, rename_all = "kebab-case")]`), `clap::ValueEnum`, and `schemars::JsonSchema` derives (`discovery.rs:119-134`).

- Search 1 (new term, case-insensitive): `git grep -ni "default_from"` on `review-head` → only its definition site (`discovery.rs:1183`) and the two call sites in `crates/uv/src/settings.rs:73,75`. No other repository text references it.
- Search 2 (old-name fragment, case-insensitive): `git grep -ni "from_settings"` on `review-head` → six hits, all for *unrelated* types' own `from_settings` associated functions (`Cache::from_settings`, `StateStore::from_settings`, `InstalledToolchains::from_settings`), none of them `ToolchainPreference::from_settings`. No stale caller of the old `ToolchainPreference::from_settings` signature remains anywhere in the tree, including files outside the changed-file manifest (`crates/uv-toolchain/src/lib.rs`, `crates/uv-toolchain/src/toolchain.rs`, `crates/uv/tests/common/mod.rs` were all checked and use unrelated `from_settings` functions or `ToolchainPreference::default()`/explicit variants, not the renamed method).
- Disposition: **sweep complete, no live peer carrying the old contract.** The rename is fully applied.

No second changed contract was found: the `ToolchainPreference` variant set itself (`OnlyManaged`, `PreferInstalledManaged`, `PreferManaged`, `PreferSystem`, `OnlySystem`) is unchanged by this diff — only its derives and one doc line changed — so there is no closed-list membership change to sweep for stale peers beyond the rename above.

## Scope-creep pass (Step 3)

**Finding: `find_interpreter` in `crates/uv/src/commands/project/mod.rs` silently narrows `EnvironmentPreference::Any` to `EnvironmentPreference::OnlySystem`, unrelated to the stated purpose of this change.**

Base (`e783a79...:crates/uv/src/commands/project/mod.rs`) called:
```rust
Toolchain::find_or_fetch(
    python_request,
    EnvironmentPreference::Any,
    ToolchainPreference::from_settings(PreviewMode::Enabled),
    ...
)
```
Head (`review-head:crates/uv/src/commands/project/mod.rs:184-190`) calls:
```rust
Toolchain::find_or_fetch(
    python_request,
    EnvironmentPreference::OnlySystem,
    toolchain_preference,
    ...
)
```
The `ToolchainPreference` swap is exactly what the PR body asks for. The `EnvironmentPreference::Any → EnvironmentPreference::OnlySystem` swap is a second, independent axis (`EnvironmentPreference` governs whether virtual vs. system *environments* are eligible discovery sources; it is orthogonal to `ToolchainPreference`, which governs managed vs. system *toolchains*). Nothing in the PR body ("Adds `--toolchain-preference` and `tool.uv.toolchain-preference`... Users can opt-out of managed toolchains or system toolchains entirely as well") mentions changing which Python *environments* are eligible during discovery. The single commit in this PR carries no message body explaining it, and the review-comment material supplied for this run contains only the naming deferral — nothing addressing this change. `find_interpreter` is called directly by `lock` (`lock.rs`) and indirectly (via `init_environment`, `mod.rs:250-260`) by `add`, `remove`, `run`, and `sync` — so this narrowing affects five of the eight touched commands, not the one being described.

## Observations

- `crates/uv/src/settings.rs` gates the *default* toolchain-preference value on the command kind (`Commands::Project(_) | Commands::Toolchain(_) | Commands::Tool(_)` get `default_from(PreviewMode::Enabled)`, everything else gets the real `--preview` flag), with an inline `TODO(zanieb)` acknowledging the wart. This is necessary plumbing to preserve each command's prior default behavior once `ToolchainPreference::from_settings(PreviewMode::Enabled)`'s hardcoding is replaced by a single shared value, not scope creep. (`crates/uv/src/settings.rs:56-63`)
- `crates/uv/tests/show_settings.rs` fixtures uniformly gained `toolchain_preference: OnlySystem,`, consistent with `default_from`'s `UV_TEST_PYTHON_PATH` branch (`discovery.rs:1184-1187`) that the test harness sets. (`crates/uv/tests/show_settings.rs:60`)
- No documentation file (`README.md`, `PREVIEW-CHANGELOG.md`, `docs/*.md`) mentions `toolchain-preference` either before or after this diff; `git grep -ni "toolchain.preference"` on `*.md` at `review-head` returns nothing, so there is no stale doc peer to flag. (`PREVIEW-CHANGELOG.md`)

## Changed-file manifest disposition

```manifest
Cargo.lock | ignored | mechanical lockfile update (adds transitive `clap` dep for uv-toolchain), no requirement content
crates/uv-settings/src/combine.rs | reviewed | adds Combine impl for ToolchainPreference, underlies B3's CLI-over-config precedence
crates/uv-settings/src/settings.rs | reviewed | adds toolchain_preference field to GlobalOptions, underlies B2
crates/uv-toolchain/Cargo.toml | ignored | mechanical optional-dependency/feature wiring for clap, no requirement content
crates/uv-toolchain/src/discovery.rs | reviewed | adds Deserialize/clap/schemars derives, renames from_settings to default_from, underlies B1/B2/B4/B5 and the changed-contract sweep
crates/uv/Cargo.toml | ignored | mechanical feature enabling (clap, schemars) for uv-toolchain dependency, no requirement content
crates/uv/src/cli.rs | reviewed | adds --toolchain-preference CLI flag, underlies B1
crates/uv/src/commands/pip/compile.rs | reviewed | threads toolchain_preference into pip compile's interpreter discovery, underlies B3
crates/uv/src/commands/project/add.rs | reviewed | threads toolchain_preference through init_environment, underlies B3
crates/uv/src/commands/project/lock.rs | reviewed | threads toolchain_preference through find_interpreter, underlies B3
crates/uv/src/commands/project/mod.rs | reviewed | threads toolchain_preference; also narrows EnvironmentPreference::Any to OnlySystem unrelated to any stated claim, see scope-creep candidate
crates/uv/src/commands/project/remove.rs | reviewed | threads toolchain_preference through init_environment, underlies B3
crates/uv/src/commands/project/run.rs | reviewed | threads toolchain_preference through init_environment and the ephemeral-env fetch, underlies B3
crates/uv/src/commands/project/sync.rs | reviewed | threads toolchain_preference through init_environment, underlies B3
crates/uv/src/commands/tool/run.rs | reviewed | threads toolchain_preference into tool run's interpreter discovery, underlies B3
crates/uv/src/commands/toolchain/find.rs | reviewed | threads toolchain_preference into toolchain find, underlies B3
crates/uv/src/commands/toolchain/list.rs | reviewed | threads toolchain_preference into toolchain list, underlies B3
crates/uv/src/commands/venv.rs | reviewed | threads toolchain_preference into venv's interpreter discovery, underlies B3
crates/uv/src/main.rs | reviewed | wires globals.toolchain_preference into every affected command call and passes cli.command into GlobalSettings::resolve, underlies B1-B5
crates/uv/src/settings.rs | reviewed | resolves toolchain_preference from CLI > config > preview-aware default, underlies B3
crates/uv/tests/show_settings.rs | reviewed | test fixtures updated for the new toolchain_preference field, consistent with default_from's test-mode branch
uv.schema.json | reviewed | adds toolchain-preference property and ToolchainPreference definition, underlies B2
```

## Candidates

````candidates
### Candidate
id: requirements/unrequested/environment-preference-narrowed
axis: Requirements
anchor: crates/uv/src/commands/project/mod.rs:187
fix: (same as anchor)
title: find_interpreter narrows EnvironmentPreference::Any to OnlySystem, unrequested by the PR
claim: The PR body states only "Adds `--toolchain-preference` and `tool.uv.toolchain-preference` to configure if system or managed toolchains are preferred. Users can opt-out of managed toolchains or system toolchains entirely as well" — a claim about the `ToolchainPreference` axis. In `crates/uv/src/commands/project/mod.rs`, `find_interpreter`'s call to `Toolchain::find_or_fetch` also changes its `EnvironmentPreference` argument from `EnvironmentPreference::Any` (base `e783a79955a3a4eb6a4c546f51f89e88b64047bb`) to `EnvironmentPreference::OnlySystem` (head `a2e6b9c6bd0257510240886549ba9e3623299739`, line 187). `EnvironmentPreference` governs whether virtual vs. system Python *environments* are eligible discovery sources and is orthogonal to `ToolchainPreference`. Nothing in the body, the single commit message, or the review material supplied for this axis mentions this change. `find_interpreter` is invoked directly by `lock` and, via `init_environment` (`crates/uv/src/commands/project/mod.rs:250-260`), by `add`, `remove`, `run`, and `sync` — five of the eight commands this PR touches.
support: Diffed `crates/uv/src/commands/project/mod.rs` between base and head via the full diff already embedded in the prompt; independently confirmed both endpoints with `git show e783a79955a3a4eb6a4c546f51f89e88b64047bb:crates/uv/src/commands/project/mod.rs` and `git show review-head:crates/uv/src/commands/project/mod.rs`. Confirmed the fan-out (which commands reach `find_interpreter`) by reading `init_environment` and the call sites in `add.rs`, `remove.rs`, `run.rs`, `sync.rs`, `lock.rs`. Did not run anything (execution disallowed). Cannot rule out that this was an intentional, undocumented bug fix bundled in — the single commit carries no body, and no review-comment thread beyond the naming deferral was supplied to this axis — so I could not confirm or refute authorial intent from the material available.
trigger: A user runs `uv lock`, `uv sync`, `uv add`, `uv remove`, or non-isolated `uv run` while some virtual environment other than the project's own `.venv` is active or discoverable (e.g. `VIRTUAL_ENV` pointing elsewhere) and the project's own `.venv` either doesn't exist yet or doesn't satisfy `requires-python`; before this diff that foreign virtual environment's interpreter was an eligible discovery source (`EnvironmentPreference::Any`), after this diff it is excluded (`OnlySystem`), silently changing which interpreter gets selected to build the project's own environment — independent of any `--toolchain-preference` setting the user made.
priority: P2
action: consider
````

## Disposition ledger

```ledger
CLI does not expose --toolchain-preference | grep GlobalArgs struct for a toolchain_preference field | crates/uv/src/cli.rs:174 | acquitted
tool.uv.toolchain-preference config key unsupported | grep GlobalOptions struct and schema for toolchain_preference/toolchain-preference | crates/uv-settings/src/settings.rs:65 | acquitted
toolchain_preference value not threaded into interpreter-discovery call sites | trace globals.toolchain_preference into every commands:: call in main.rs | crates/uv/src/main.rs:526 | acquitted
OnlyManaged/OnlySystem variants exist but aren't enforced during discovery | read ToolchainPreference::allows and the discovery-source builder | crates/uv-toolchain/src/discovery.rs:1153-1179 | acquitted
stale ToolchainPreference::from_settings caller left after rename to default_from | repo-wide grep for from_settings and ToolchainPreference:: on review-head | crates/uv-toolchain/src/discovery.rs:1183 | acquitted
TOML key does not kebab-case to toolchain-preference matching schema/body | read serde rename_all attribute on GlobalOptions | crates/uv-settings/src/settings.rs:52 | acquitted
CLI value does not take precedence over config-file value | read Combine for Option<ToolchainPreference> (self.or(other)) and GlobalSettings::resolve call order | crates/uv-settings/src/combine.rs:73 | acquitted
pip install/pip sync missing toolchain_preference wiring is a gap | read their interpreter-discovery mechanism (PythonEnvironment::find vs Toolchain::find) | crates/uv/src/commands/pip/install.rs:119 | acquitted
tool install command missing toolchain_preference wiring | check ToolCommand enum for an Install variant at this head | crates/uv/src/cli.rs:1727-1730 | acquitted
find_interpreter narrows EnvironmentPreference::Any to OnlySystem with no requirement calling for it | diff project/mod.rs base vs head against PR body claims | crates/uv/src/commands/project/mod.rs:187 | candidate
naming/value-vocabulary of --toolchain-preference is an open, explicitly deferred bikeshed | search CONTRIBUTING.md and repo for a CLI-naming convention rule that would settle it | CONTRIBUTING.md (no such rule found) | question
docs (README/PREVIEW-CHANGELOG/docs/*.md) carry stale wording about toolchain preference | git grep -ni "toolchain.preference" on *.md at review-head | PREVIEW-CHANGELOG.md (no hits) | acquitted
```

```manifest
Cargo.lock | ignored | mechanical lockfile update, no requirement content
crates/uv-settings/src/combine.rs | reviewed | implements config-file combine precedence for toolchain_preference
crates/uv-settings/src/settings.rs | reviewed | adds toolchain_preference field to GlobalOptions
crates/uv-toolchain/Cargo.toml | ignored | mechanical optional-dependency/feature wiring, no requirement content
crates/uv-toolchain/src/discovery.rs | reviewed | adds Deserialize/clap/schemars derives, renames from_settings to default_from
crates/uv/Cargo.toml | ignored | mechanical feature enabling for uv-toolchain dependency, no requirement content
crates/uv/src/cli.rs | reviewed | adds --toolchain-preference CLI flag
crates/uv/src/commands/pip/compile.rs | reviewed | threads toolchain_preference into pip compile
crates/uv/src/commands/project/add.rs | reviewed | threads toolchain_preference through init_environment
crates/uv/src/commands/project/lock.rs | reviewed | threads toolchain_preference through find_interpreter
crates/uv/src/commands/project/mod.rs | reviewed | threads toolchain_preference; also narrows EnvironmentPreference::Any to OnlySystem, see scope-creep candidate
crates/uv/src/commands/project/remove.rs | reviewed | threads toolchain_preference through init_environment
crates/uv/src/commands/project/run.rs | reviewed | threads toolchain_preference through init_environment and ephemeral-env fetch
crates/uv/src/commands/project/sync.rs | reviewed | threads toolchain_preference through init_environment
crates/uv/src/commands/tool/run.rs | reviewed | threads toolchain_preference into tool run
crates/uv/src/commands/toolchain/find.rs | reviewed | threads toolchain_preference into toolchain find
crates/uv/src/commands/toolchain/list.rs | reviewed | threads toolchain_preference into toolchain list
crates/uv/src/commands/venv.rs | reviewed | threads toolchain_preference into venv
crates/uv/src/main.rs | reviewed | wires globals.toolchain_preference into every affected command call
crates/uv/src/settings.rs | reviewed | resolves toolchain_preference from CLI > config > preview-aware default
crates/uv/tests/show_settings.rs | reviewed | test fixtures updated for new toolchain_preference field
uv.schema.json | reviewed | adds toolchain-preference property and ToolchainPreference definition
```

```counts
met=5 not-met=0 unverifiable=1
```
```

**Validator result on the round-1 report:** exit 1:
```
manifest:0: duplicate manifest block: the report has 2 fenced manifest blocks; exactly one is allowed
ledger:11: evidence: 'CONTRIBUTING.md (no such rule found)' is not one path:line, path:start-end, or `path` § heading location
ledger:12: evidence: 'PREVIEW-CHANGELOG.md (no hits)' is not one path:line, path:start-end, or `path` § heading location
```


### 4.4 Requirements finder — round 2 (re-dispatch, final)

**Agent id:** `ad53cf0ea49b91340`. **Model:** `sonnet` (explicit). Fresh `Agent` call carrying the
original prompt's substance, the finder's own round-1 verbatim report, and the three violation
lines, with an explicit instruction not to re-run the investigation.

**Exact prompt given:**

```markdown
You are the Requirements-axis finder for a review of `astral-sh/uv#4424`, being re-dispatched once because your first submission's report violated the required output shape (a mechanical shape check, not a content problem).

Your original task prompt is unchanged and still applies in full: read `/tmp/holdout/work/d/panel-seed1/requirements-finder-prompt.md` in full (it contains the pinned run identity, changed-file manifest, commit list, full diff, applicable base-branch guidance, binding run conditions, and the "## Axis: Requirements" section naming your brief, the pull request body, and the explicit deferral), and follow `/tmp/holdout/skills/panel/references/requirements-axis.md` and `/tmp/holdout/skills/panel/references/finding-format.md` for the rubric and report shape. Same constraints as before: offline, read-only, no build/test execution, clone hygiene (no checkout/switch/reset/stash), stay inside the clone at `/tmp/holdout/runs/d/panel-seed1`, the skill snapshot, the packet directory, and your own scratch space.

Here is your own prior submission, verbatim, in full:

--- BEGIN YOUR PRIOR SUBMISSION ---
[the round-1 verbatim report reproduced in full in § 4.3 above was pasted here in the actual
dispatch — abbreviated in this second reproduction only to avoid tripling this document's length;
it is byte-identical to § 4.3's "Verbatim report returned (round 1...)" block]
--- END YOUR PRIOR SUBMISSION ---

Running `python3 /tmp/holdout/skills/panel/scripts/validate_finder_report.py --axis requirements --manifest <manifest>` on it produced exactly these violations:

```
manifest:0: duplicate manifest block: the report has 2 fenced manifest blocks; exactly one is allowed
ledger:11: evidence: 'CONTRIBUTING.md (no such rule found)' is not one path:line, path:start-end, or `path` § heading location
ledger:12: evidence: 'PREVIEW-CHANGELOG.md (no hits)' is not one path:line, path:start-end, or `path` § heading location
```

Three shape problems, none of them about your conclusions:

1. **Duplicate `manifest` block.** Your report has a fenced ```manifest``` block twice — once under "## Changed-file manifest disposition" mid-report, and once again in the required trailing trio at the end. `requirements-axis.md` § Report tail requires exactly **one** fenced `manifest` block, as part of the trailing `ledger`, `manifest`, `counts` trio with nothing after them. Keep only the final trailing one; replace the mid-report occurrence with a plain (non-fenced, or fenced with a different info string like ```text) narrative/bulleted rendering of the same rows so a human reader still sees it there, but only the real fenced ```manifest info-string block at the end.
2. **Two ledger rows have malformed evidence.** `finding-format.md` requires each ledger row's evidence field to be one whole `path:line`, `path:start-end`, or a quoted-rule location written `` `path` § heading `` — never free prose. Your rows for the naming-deferral question and the docs sweep acquittal wrote `CONTRIBUTING.md (no such rule found)` and `PREVIEW-CHANGELOG.md (no hits)` — prose appended to a bare path, which the validator's coordinate/quoted-rule-location patterns reject. Fix by writing each as a bare file path (a valid "path" per the coordinate grammar, since a bare path with a `.` counts) — i.e. just `CONTRIBUTING.md` and `PREVIEW-CHANGELOG.md` — and move the "no such rule found" / "no hits" explanation into the row's claim field instead (the first pipe-separated field), where prose belongs.

**Do not re-run your investigation.** Your conclusions, restated requirements, sorting, scope-creep finding, candidate, and every ledger row's claim/disposition are unchanged in substance — only reshape the document to fix these three mechanical issues. Return your full, corrected report as your final message text, ending with exactly one fenced `ledger` block, one fenced `manifest` block, and one fenced `counts` block, in that order, with nothing after them, and no `manifest` block earlier in the document. Do not write it to any file yourself.
```

**Verbatim report returned (round 2 — this is the report used downstream, saved to
`finder-requirements.md`):**

```markdown
Corrected report below (same investigation, substance unchanged; only the mid-report manifest de-fenced, the ledger evidence fields fixed, and a single trailing fenced `manifest` retained).

# Requirements-axis finder report — `astral-sh/uv#4424`

## Read-order and scope compliance

Read, in this order: `/tmp/holdout/work/d/panel-seed1/requirements-finder-prompt.md` (full, ~1150 lines) → `/tmp/holdout/skills/panel/references/requirements-axis.md` (full) → `/tmp/holdout/skills/panel/references/finding-format.md` (full). Then investigated the clone at `/tmp/holdout/runs/d/panel-seed1`.

- **No history beyond the pinned head was read.** Git commands run: `git branch -a`, `git status --short`, `git rev-parse HEAD`, `git log -1 --format=... a2e6b9c6...` (the pinned head commit itself, no ancestor walk), `git grep -n ... review-head -- ...` (working-tree content at the pinned head only), `git show review-head:<path>` (content at pinned head), `git show e783a79955a3a4eb6a4c546f51f89e88b64047bb:<path>` (content at the pinned base/merge-base, explicitly in scope as the comparison point). No `git log` range walks, no `git fetch`/`git pull`, no `checkout`/`switch`/`reset`/`stash`.
- **No execution.** No `cargo`/`rustc`/`uv`/`python` invocations of any kind.
- **Sandbox paths.** Only read: the task prompt file, the two skill reference files above, and files inside the `/tmp/holdout/runs/d/panel-seed1` clone (via `git show`/`git grep`). Did not read `/tmp/holdout/packets/d/` or anything outside the permitted list.
- **No originating issue.** Per instructions, the pull request body is the spec surrogate. Issue alignment is therefore unavailable for this review; the "compliance" pass below is instead a body-claims ledger, walking claim → code, as `requirements-axis.md` § No issue requires.

## Restated claim/requirement list (from the PR body, verbatim quoted where relevant)

Body: *"Exposes the option added in #4416. Adds `--toolchain-preference` and `tool.uv.toolchain-preference` to configure if system or managed toolchains are preferred. Users can opt-out of managed toolchains or system toolchains entirely as well."*

- **B0 (background, not a claim)** — "Exposes the option added in #4416." This is context (the `ToolchainPreference` enum and its discovery semantics already existed pre-diff), not itself a checkable behavioral claim. Not sorted, not counted.
- **B1** — Adds a `--toolchain-preference` CLI option.
- **B2** — Adds a `tool.uv.toolchain-preference` configuration-file option.
- **B3** — Both surfaces actually let a user "configure if system or managed toolchains are preferred" (i.e., the value is correctly parsed, combined CLI-over-config-over-default, and threaded into interpreter discovery).
- **B4** — Users can opt out of managed toolchains entirely (i.e., an "only system" value exists and is enforced).
- **B5** — Users can opt out of system toolchains entirely (i.e., an "only managed" value exists and is enforced).
- **B6 (deferred decision, its own restated entry per `requirements-axis.md` § Step 2)** — The name `--toolchain-preference` / `toolchain-preference` and its value vocabulary (the `prefer-*` prefix, `--toolchains` alternative, "prefer … prefer" redundancy) was an open bikeshed at review time, explicitly deferred by `zanieb` (2024-06-20T17:27:06Z): *"I'm fine adjusting this later if we need to since it's in preview."* No repository rule (style guide, `CONTRIBUTING.md`) settles CLI-flag naming conventions, so this cannot be resolved by rule and stays a question.

## Sorting

**B1 — Met.** `crates/uv/src/cli.rs:174-175` adds `pub(crate) toolchain_preference: Option<ToolchainPreference>` to `GlobalArgs` with `#[arg(global = true, long)]`, i.e. `--toolchain-preference`, taking `ToolchainPreference` values via its new `clap::ValueEnum` derive (`crates/uv-toolchain/src/discovery.rs:120-124`).

**B2 — Met.** `crates/uv-settings/src/settings.rs:65` adds `pub toolchain_preference: Option<ToolchainPreference>` to `GlobalOptions`, which is `#[serde(flatten)]`ed into `Options` (the `[tool.uv]` schema) with `#[serde(rename_all = "kebab-case")]` on the struct, so the TOML key is `toolchain-preference`, matching the body's `tool.uv.toolchain-preference`. `uv.schema.json:231-834` (base version) gains the corresponding `toolchain-preference` property and `ToolchainPreference` definition.

**B3 — Met.** `crates/uv/src/settings.rs` (`GlobalSettings::resolve`) computes `toolchain_preference: args.toolchain_preference.combine(workspace...).unwrap_or(default_toolchain_preference)`. `Combine for Option<ToolchainPreference>` is `self.or(other)` (`crates/uv-settings/src/combine.rs:73`, via `impl_combine_or!`), so CLI beats config file beats the preview-aware default — correct precedence. `globals.toolchain_preference` is then threaded into every call site that previously hardcoded `ToolchainPreference::from_settings(...)`: `pip compile` (`compile.rs:161,171`), `venv` (`venv.rs:140`), `run`/`sync`/`lock`/`add`/`remove` (via `project::find_interpreter`/`init_environment`, `mod.rs:187`, `lock.rs`, `add.rs`, `remove.rs`, `sync.rs`), `tool run` (`tool/run.rs:71`), `toolchain find` (`toolchain/find.rs:30`), `toolchain list` (`toolchain/list.rs:57`) — all ten call sites in `main.rs` pass `globals.toolchain_preference` to match. `pip install`/`pip sync`/etc. legitimately don't take it: they resolve an *existing* environment via `PythonEnvironment::find` (`install.rs:119`, `sync.rs:114`), not fresh toolchain discovery/download, so `ToolchainPreference` doesn't apply there — not a gap.

**B4/B5 — Met.** `ToolchainPreference::allows` (`discovery.rs:1153-1179`, unchanged by this diff, pre-existing from #4416) enforces `OnlyManaged` ⇒ only `ToolchainSource::Managed`, and `OnlySystem` ⇒ only `SearchPath`/`PyLauncher`; the discovery-source iterator builder (`discovery.rs:317-336`) likewise restricts `OnlyManaged` to `from_managed_toolchains` alone and `OnlySystem` to `from_search_path.chain(from_py_launcher)` alone. Both opt-out values exist, are now user-reachable via B1/B2, and are enforced.

**B6 — Cannot tell from the code / Question.** This is a live naming/value-vocabulary bikeshed explicitly deferred by the author on unreleased (preview) public surface, with no repository rule to settle it. Per `requirements-axis.md` § Step 2 it resolves to the "cannot tell" bucket as a question, not a defect claim, and makes this axis `Waiting for information` rather than `Passed`.

> No static evidence can settle whether `--toolchain-preference` / `prefer-installed-managed` etc. is the name the maintainers intend to ship, because the deferral says explicitly that it may still change ("I'm fine adjusting this later … since it's in preview") and the review thread ends without a final decision recorded in the material supplied to this axis. What would settle it: a later commit or release note (outside this pinned head) either renaming the flag/values or a maintainer statement closing the bikeshed — neither of which exists in the history available to this run.

## Changed-contract sweep

**Contract: `ToolchainPreference::from_settings(preview: PreviewMode)` renamed to `ToolchainPreference::default_from(preview: PreviewMode)`**, plus the enum gaining `serde::Deserialize` (`#[serde(deny_unknown_fields, rename_all = "kebab-case")]`), `clap::ValueEnum`, and `schemars::JsonSchema` derives (`discovery.rs:119-134`).

- Search 1 (new term, case-insensitive): `git grep -ni "default_from"` on `review-head` → only its definition site (`discovery.rs:1183`) and the two call sites in `crates/uv/src/settings.rs:73,75`. No other repository text references it.
- Search 2 (old-name fragment, case-insensitive): `git grep -ni "from_settings"` on `review-head` → six hits, all for *unrelated* types' own `from_settings` associated functions (`Cache::from_settings`, `StateStore::from_settings`, `InstalledToolchains::from_settings`), none of them `ToolchainPreference::from_settings`. No stale caller of the old `ToolchainPreference::from_settings` signature remains anywhere in the tree, including files outside the changed-file manifest (`crates/uv-toolchain/src/lib.rs`, `crates/uv-toolchain/src/toolchain.rs`, `crates/uv/tests/common/mod.rs` were all checked and use unrelated `from_settings` functions or `ToolchainPreference::default()`/explicit variants, not the renamed method).
- Disposition: **sweep complete, no live peer carrying the old contract.** The rename is fully applied.

No second changed contract was found: the `ToolchainPreference` variant set itself (`OnlyManaged`, `PreferInstalledManaged`, `PreferManaged`, `PreferSystem`, `OnlySystem`) is unchanged by this diff — only its derives and one doc line changed — so there is no closed-list membership change to sweep for stale peers beyond the rename above.

## Scope-creep pass (Step 3)

**Finding: `find_interpreter` in `crates/uv/src/commands/project/mod.rs` silently narrows `EnvironmentPreference::Any` to `EnvironmentPreference::OnlySystem`, unrelated to the stated purpose of this change.**

Base (`e783a79...:crates/uv/src/commands/project/mod.rs`) called:
```rust
Toolchain::find_or_fetch(
    python_request,
    EnvironmentPreference::Any,
    ToolchainPreference::from_settings(PreviewMode::Enabled),
    ...
)
```
Head (`review-head:crates/uv/src/commands/project/mod.rs:184-190`) calls:
```rust
Toolchain::find_or_fetch(
    python_request,
    EnvironmentPreference::OnlySystem,
    toolchain_preference,
    ...
)
```
The `ToolchainPreference` swap is exactly what the PR body asks for. The `EnvironmentPreference::Any → EnvironmentPreference::OnlySystem` swap is a second, independent axis (`EnvironmentPreference` governs whether virtual vs. system *environments* are eligible discovery sources; it is orthogonal to `ToolchainPreference`, which governs managed vs. system *toolchains*). Nothing in the PR body ("Adds `--toolchain-preference` and `tool.uv.toolchain-preference`... Users can opt-out of managed toolchains or system toolchains entirely as well") mentions changing which Python *environments* are eligible during discovery. The single commit in this PR carries no message body explaining it, and the review-comment material supplied for this run contains only the naming deferral — nothing addressing this change. `find_interpreter` is called directly by `lock` (`lock.rs`) and indirectly (via `init_environment`, `mod.rs:250-260`) by `add`, `remove`, `run`, and `sync` — so this narrowing affects five of the eight touched commands, not the one being described.

## Observations

- `crates/uv/src/settings.rs` gates the *default* toolchain-preference value on the command kind (`Commands::Project(_) | Commands::Toolchain(_) | Commands::Tool(_)` get `default_from(PreviewMode::Enabled)`, everything else gets the real `--preview` flag), with an inline `TODO(zanieb)` acknowledging the wart. This is necessary plumbing to preserve each command's prior default behavior once `ToolchainPreference::from_settings(PreviewMode::Enabled)`'s hardcoding is replaced by a single shared value, not scope creep. (`crates/uv/src/settings.rs:56-63`)
- `crates/uv/tests/show_settings.rs` fixtures uniformly gained `toolchain_preference: OnlySystem,`, consistent with `default_from`'s `UV_TEST_PYTHON_PATH` branch (`discovery.rs:1184-1187`) that the test harness sets. (`crates/uv/tests/show_settings.rs:60`)
- No documentation file (`README.md`, `PREVIEW-CHANGELOG.md`, `docs/*.md`) mentions `toolchain-preference` either before or after this diff; `git grep -ni "toolchain.preference"` on `*.md` at `review-head` returns nothing, so there is no stale doc peer to flag. (`PREVIEW-CHANGELOG.md`)

## Changed-file manifest disposition

Narrative rendering (same rows as the trailing `manifest` block below; kept unfenced here per report shape so exactly one fenced `manifest` block exists, at the end):

- `Cargo.lock` — ignored — mechanical lockfile update (adds transitive `clap` dep for uv-toolchain), no requirement content
- `crates/uv-settings/src/combine.rs` — reviewed — adds Combine impl for ToolchainPreference, underlies B3's CLI-over-config precedence
- `crates/uv-settings/src/settings.rs` — reviewed — adds toolchain_preference field to GlobalOptions, underlies B2
- `crates/uv-toolchain/Cargo.toml` — ignored — mechanical optional-dependency/feature wiring for clap, no requirement content
- `crates/uv-toolchain/src/discovery.rs` — reviewed — adds Deserialize/clap/schemars derives, renames from_settings to default_from, underlies B1/B2/B4/B5 and the changed-contract sweep
- `crates/uv/Cargo.toml` — ignored — mechanical feature enabling (clap, schemars) for uv-toolchain dependency, no requirement content
- `crates/uv/src/cli.rs` — reviewed — adds --toolchain-preference CLI flag, underlies B1
- `crates/uv/src/commands/pip/compile.rs` — reviewed — threads toolchain_preference into pip compile's interpreter discovery, underlies B3
- `crates/uv/src/commands/project/add.rs` — reviewed — threads toolchain_preference through init_environment, underlies B3
- `crates/uv/src/commands/project/lock.rs` — reviewed — threads toolchain_preference through find_interpreter, underlies B3
- `crates/uv/src/commands/project/mod.rs` — reviewed — threads toolchain_preference; also narrows EnvironmentPreference::Any to OnlySystem unrelated to any stated claim, see scope-creep candidate
- `crates/uv/src/commands/project/remove.rs` — reviewed — threads toolchain_preference through init_environment, underlies B3
- `crates/uv/src/commands/project/run.rs` — reviewed — threads toolchain_preference through init_environment and the ephemeral-env fetch, underlies B3
- `crates/uv/src/commands/project/sync.rs` — reviewed — threads toolchain_preference through init_environment, underlies B3
- `crates/uv/src/commands/tool/run.rs` — reviewed — threads toolchain_preference into tool run's interpreter discovery, underlies B3
- `crates/uv/src/commands/toolchain/find.rs` — reviewed — threads toolchain_preference into toolchain find, underlies B3
- `crates/uv/src/commands/toolchain/list.rs` — reviewed — threads toolchain_preference into toolchain list, underlies B3
- `crates/uv/src/commands/venv.rs` — reviewed — threads toolchain_preference into venv's interpreter discovery, underlies B3
- `crates/uv/src/main.rs` — reviewed — wires globals.toolchain_preference into every affected command call and passes cli.command into GlobalSettings::resolve, underlies B1-B5
- `crates/uv/src/settings.rs` — reviewed — resolves toolchain_preference from CLI > config > preview-aware default, underlies B3
- `crates/uv/tests/show_settings.rs` — reviewed — test fixtures updated for the new toolchain_preference field, consistent with default_from's test-mode branch
- `uv.schema.json` — reviewed — adds toolchain-preference property and ToolchainPreference definition, underlies B2

## Candidates

````candidates
### Candidate
id: requirements/unrequested/environment-preference-narrowed
axis: Requirements
anchor: crates/uv/src/commands/project/mod.rs:187
fix: (same as anchor)
title: find_interpreter narrows EnvironmentPreference::Any to OnlySystem, unrequested by the PR
claim: The PR body states only "Adds `--toolchain-preference` and `tool.uv.toolchain-preference` to configure if system or managed toolchains are preferred. Users can opt-out of managed toolchains or system toolchains entirely as well" — a claim about the `ToolchainPreference` axis. In `crates/uv/src/commands/project/mod.rs`, `find_interpreter`'s call to `Toolchain::find_or_fetch` also changes its `EnvironmentPreference` argument from `EnvironmentPreference::Any` (base `e783a79955a3a4eb6a4c546f51f89e88b64047bb`) to `EnvironmentPreference::OnlySystem` (head `a2e6b9c6bd0257510240886549ba9e3623299739`, line 187). `EnvironmentPreference` governs whether virtual vs. system Python *environments* are eligible discovery sources and is orthogonal to `ToolchainPreference`. Nothing in the body, the single commit message, or the review material supplied for this axis mentions this change. `find_interpreter` is invoked directly by `lock` and, via `init_environment` (`crates/uv/src/commands/project/mod.rs:250-260`), by `add`, `remove`, `run`, and `sync` — five of the eight commands this PR touches.
support: Diffed `crates/uv/src/commands/project/mod.rs` between base and head via the full diff already embedded in the prompt; independently confirmed both endpoints with `git show e783a79955a3a4eb6a4c546f51f89e88b64047bb:crates/uv/src/commands/project/mod.rs` and `git show review-head:crates/uv/src/commands/project/mod.rs`. Confirmed the fan-out (which commands reach `find_interpreter`) by reading `init_environment` and the call sites in `add.rs`, `remove.rs`, `run.rs`, `sync.rs`, `lock.rs`. Did not run anything (execution disallowed). Cannot rule out that this was an intentional, undocumented bug fix bundled in — the single commit carries no body, and no review-comment thread beyond the naming deferral was supplied to this axis — so I could not confirm or refute authorial intent from the material available.
trigger: A user runs `uv lock`, `uv sync`, `uv add`, `uv remove`, or non-isolated `uv run` while some virtual environment other than the project's own `.venv` is active or discoverable (e.g. `VIRTUAL_ENV` pointing elsewhere) and the project's own `.venv` either doesn't exist yet or doesn't satisfy `requires-python`; before this diff that foreign virtual environment's interpreter was an eligible discovery source (`EnvironmentPreference::Any`), after this diff it is excluded (`OnlySystem`), silently changing which interpreter gets selected to build the project's own environment — independent of any `--toolchain-preference` setting the user made.
priority: P2
action: consider
````

```ledger
CLI does not expose --toolchain-preference | grep GlobalArgs struct for a toolchain_preference field | crates/uv/src/cli.rs:174 | acquitted
tool.uv.toolchain-preference config key unsupported | grep GlobalOptions struct and schema for toolchain_preference/toolchain-preference | crates/uv-settings/src/settings.rs:65 | acquitted
toolchain_preference value not threaded into interpreter-discovery call sites | trace globals.toolchain_preference into every commands:: call in main.rs | crates/uv/src/main.rs:526 | acquitted
OnlyManaged/OnlySystem variants exist but aren't enforced during discovery | read ToolchainPreference::allows and the discovery-source builder | crates/uv-toolchain/src/discovery.rs:1153-1179 | acquitted
stale ToolchainPreference::from_settings caller left after rename to default_from | repo-wide grep for from_settings and ToolchainPreference:: on review-head | crates/uv-toolchain/src/discovery.rs:1183 | acquitted
TOML key does not kebab-case to toolchain-preference matching schema/body | read serde rename_all attribute on GlobalOptions | crates/uv-settings/src/settings.rs:52 | acquitted
CLI value does not take precedence over config-file value | read Combine for Option<ToolchainPreference> (self.or(other)) and GlobalSettings::resolve call order | crates/uv-settings/src/combine.rs:73 | acquitted
pip install/pip sync missing toolchain_preference wiring is a gap | read their interpreter-discovery mechanism (PythonEnvironment::find vs Toolchain::find) | crates/uv/src/commands/pip/install.rs:119 | acquitted
tool install command missing toolchain_preference wiring | check ToolCommand enum for an Install variant at this head | crates/uv/src/cli.rs:1727-1730 | acquitted
find_interpreter narrows EnvironmentPreference::Any to OnlySystem with no requirement calling for it | diff project/mod.rs base vs head against PR body claims | crates/uv/src/commands/project/mod.rs:187 | candidate
naming/value-vocabulary of --toolchain-preference is an open, explicitly deferred bikeshed; searched for a CLI-naming convention rule that would settle it, no such rule found | search CONTRIBUTING.md and repo for a CLI-naming convention rule | CONTRIBUTING.md | question
docs (README/PREVIEW-CHANGELOG/docs/*.md) carry stale wording about toolchain preference; searched for stale doc references, no hits | git grep -ni "toolchain.preference" on *.md at review-head | PREVIEW-CHANGELOG.md | acquitted
```

```manifest
Cargo.lock | ignored | mechanical lockfile update, no requirement content
crates/uv-settings/src/combine.rs | reviewed | implements config-file combine precedence for toolchain_preference
crates/uv-settings/src/settings.rs | reviewed | adds toolchain_preference field to GlobalOptions
crates/uv-toolchain/Cargo.toml | ignored | mechanical optional-dependency/feature wiring, no requirement content
crates/uv-toolchain/src/discovery.rs | reviewed | adds Deserialize/clap/schemars derives, renames from_settings to default_from
crates/uv/Cargo.toml | ignored | mechanical feature enabling for uv-toolchain dependency, no requirement content
crates/uv/src/cli.rs | reviewed | adds --toolchain-preference CLI flag
crates/uv/src/commands/pip/compile.rs | reviewed | threads toolchain_preference into pip compile
crates/uv/src/commands/project/add.rs | reviewed | threads toolchain_preference through init_environment
crates/uv/src/commands/project/lock.rs | reviewed | threads toolchain_preference through find_interpreter
crates/uv/src/commands/project/mod.rs | reviewed | threads toolchain_preference; also narrows EnvironmentPreference::Any to OnlySystem, see scope-creep candidate
crates/uv/src/commands/project/remove.rs | reviewed | threads toolchain_preference through init_environment
crates/uv/src/commands/project/run.rs | reviewed | threads toolchain_preference through init_environment and ephemeral-env fetch
crates/uv/src/commands/project/sync.rs | reviewed | threads toolchain_preference through init_environment
crates/uv/src/commands/tool/run.rs | reviewed | threads toolchain_preference into tool run
crates/uv/src/commands/toolchain/find.rs | reviewed | threads toolchain_preference into toolchain find
crates/uv/src/commands/toolchain/list.rs | reviewed | threads toolchain_preference into toolchain list
crates/uv/src/commands/venv.rs | reviewed | threads toolchain_preference into venv
crates/uv/src/main.rs | reviewed | wires globals.toolchain_preference into every affected command call
crates/uv/src/settings.rs | reviewed | resolves toolchain_preference from CLI > config > preview-aware default
crates/uv/tests/show_settings.rs | reviewed | test fixtures updated for new toolchain_preference field
uv.schema.json | reviewed | adds toolchain-preference property and ToolchainPreference definition
```

```counts
met=5 not-met=0 unverifiable=1
```
```

**Validator result on the round-2 report:** exit 1 (persisting violation on 2 of 12 ledger rows —
see § 2 for the exact violation text and the judgment call not to attempt a third dispatch). My
mistake in constructing this re-dispatch's instructions: I told the finder it could write a bare
path (`CONTRIBUTING.md`) as "a valid 'path' per the coordinate grammar, since a bare path with a `.`
counts" — that claim is true of `build_verifier_prompt.py`'s `BARE_PATH_RE` (used for the `fix`
field), but **not** of `validate_finder_report.py`'s ledger-row `COORDINATE_RE`/`QUOTED_RULE_RE`,
which require a line number or a `§` heading and reject a bare path outright. I misread which
script's grammar applied to which field when writing the re-dispatch prompt, which is why the
finder's good-faith fix (following my own incorrect instruction) still failed. This is disclosed
here rather than silently absorbed; see § 10 for how it is treated in the final coverage/status
calculus.


## 5b. Step 3: Verify — building the verifier prompt

Ran `python3 /tmp/holdout/skills/panel/scripts/build_verifier_prompt.py --brief
/tmp/holdout/skills/panel/references/verify.md --repo /tmp/holdout/runs/d/panel-seed1 --base-sha
e783a79955a3a4eb6a4c546f51f89e88b64047bb --head-sha a2e6b9c6bd0257510240886549ba9e3623299739
--merge-base e783a79955a3a4eb6a4c546f51f89e88b64047bb --code finder-code.md --requirements
finder-requirements.md`, run from `/tmp/holdout/work/d/panel-seed1`, output redirected to
`verifier-prompt.md`. Exit 0. No `--suite-results` (none ran, per run condition 2). Per `SKILL.md`
step 3: "Read each finder's `ledger`, `counts`, and `manifest` blocks for coverage and status; do not
re-read the finders' prose to build the verifier prompt" — I did not hand-build this prompt or
re-derive it from the finder reports' prose; the script mechanically extracted the 10-field
`### Candidate` sections and withheld `support`. Verified this mechanically: `grep -n "^support:"
verifier-prompt.md` returns nothing — the withholding held.

The output correctly carries exactly **one** candidate — the sole Requirements-axis candidate the
Code axis returned none, and it correctly excludes the B6 naming-deferral question, which
`SKILL.md` step 3 routes straight to publication and never to the verifier ("Requirements axis's
'cannot tell from the code' bucket… resolve to questions at the finder"). No `## Related acquitted
ledger rows` section appears in the output; this is expected and not an omission — the script only
emits that section when the verifier brief (`verify.md`) itself contains a `## Related acquittals`
heading to key off of, and `verify.md` in this skill snapshot has no such heading (confirmed by
`grep -n "Related acquittals" references/verify.md`, zero hits) — so this skill's verifier brief
does not define a related-acquittals mechanism at all, and none was owed here.

**Full verifier prompt, verbatim:**

```markdown
Verifier brief: `/tmp/holdout/skills/panel/references/verify.md`

Repository: `/tmp/holdout/runs/d/panel-seed1`

## Pinned run identity

- base SHA: `e783a79955a3a4eb6a4c546f51f89e88b64047bb`
- head SHA: `a2e6b9c6bd0257510240886549ba9e3623299739`
- merge-base: `e783a79955a3a4eb6a4c546f51f89e88b64047bb`

## Candidates

### Candidate 1
id: requirements/unrequested/environment-preference-narrowed
axis: Requirements
anchor: crates/uv/src/commands/project/mod.rs:187
fix: (same as anchor)
title: find_interpreter narrows EnvironmentPreference::Any to OnlySystem, unrequested by the PR
claim: The PR body states only "Adds `--toolchain-preference` and `tool.uv.toolchain-preference` to configure if system or managed toolchains are preferred. Users can opt-out of managed toolchains or system toolchains entirely as well" — a claim about the `ToolchainPreference` axis. In `crates/uv/src/commands/project/mod.rs`, `find_interpreter`'s call to `Toolchain::find_or_fetch` also changes its `EnvironmentPreference` argument from `EnvironmentPreference::Any` (base `e783a79955a3a4eb6a4c546f51f89e88b64047bb`) to `EnvironmentPreference::OnlySystem` (head `a2e6b9c6bd0257510240886549ba9e3623299739`, line 187). `EnvironmentPreference` governs whether virtual vs. system Python *environments* are eligible discovery sources and is orthogonal to `ToolchainPreference`. Nothing in the body, the single commit message, or the review material supplied for this axis mentions this change. `find_interpreter` is invoked directly by `lock` and, via `init_environment` (`crates/uv/src/commands/project/mod.rs:250-260`), by `add`, `remove`, `run`, and `sync` — five of the eight commands this PR touches.
trigger: A user runs `uv lock`, `uv sync`, `uv add`, `uv remove`, or non-isolated `uv run` while some virtual environment other than the project's own `.venv` is active or discoverable (e.g. `VIRTUAL_ENV` pointing elsewhere) and the project's own `.venv` either doesn't exist yet or doesn't satisfy `requires-python`; before this diff that foreign virtual environment's interpreter was an eligible discovery source (`EnvironmentPreference::Any`), after this diff it is excluded (`OnlySystem`), silently changing which interpreter gets selected to build the project's own environment — independent of any `--toolchain-preference` setting the user made.
priority: P2
action: consider
```

## 5c. Step 3: Verify — dispatch and verbatim report

**Agent id:** `a7f2f474303c4e791`. **Model:** `sonnet` (explicit). Foreground `Agent` call,
`subagent_type: general-purpose`, fresh context (no prior transcript) — this is the mechanism
`SKILL.md` step 3 and `verify.md` require: "A verifier that has already seen why the finder believed
something agrees with itself, which checks nothing." Waited for its return before continuing.

**Exact prompt given:**

```markdown
You are the fresh-context verifier for a code review of `astral-sh/uv#4424` (a merged pull request, offline and read-only). Read `/tmp/holdout/skills/panel/references/verify.md` in full first — it is your brief, defining `confirmed`/`plausible`/`refuted`, the anti-over-refutation asymmetry, deduplication, and priority/action recalibration rules. Follow it exactly.

Your actual verification prompt — the pinned run identity and the one candidate you must rule on (its `claim`, not its withheld `support`, per the brief's design) — is the file `/tmp/holdout/work/d/panel-seed1/verifier-prompt.md`. Read it in full; it is short (22 lines, one candidate).

You have a local, read-only, offline git clone at `/tmp/holdout/runs/d/panel-seed1` to verify the claim against: branch `review-head` is the pinned head (`a2e6b9c6bd0257510240886549ba9e3623299739`), branch `main` is force-pinned to the merge-base/base SHA (`e783a79955a3a4eb6a4c546f51f89e88b64047bb`). Use read-only git commands only (`git show`, `git diff`, `git log`, `git blame`, `git grep`, `cat`, `grep`, `find`) — never `git checkout`/`switch`/`reset`/`stash`. Do not run `cargo`/`rustc`/`uv`/`python` build or test tooling — no network access exists for the toolchain, and this review is entirely static; reason from the source. History is truncated at the pinned head on purpose — do not try to read anything newer than `a2e6b9c6bd0257510240886549ba9e3623299739`, and report explicitly whether you read any history beyond it and which commands you ran. Do not read anything outside: the clone at `/tmp/holdout/runs/d/panel-seed1`, the skill snapshot at `/tmp/holdout/skills/panel/`, the packet directory at `/tmp/holdout/packets/d/`, and your own scratch space under `/tmp/holdout/work/d/panel-seed1/` — if you do, name the exact path in your final report.

Read the candidate's cited `anchor` (`crates/uv/src/commands/project/mod.rs:187`) and `fix` sites, and only enough surrounding context to decide the claim — follow call sites (the diff's other rewired command functions: `add.rs`, `remove.rs`, `run.rs`, `sync.rs`, `lock.rs`, and `init_environment`/`find_interpreter` in `project/mod.rs` itself) since the claim depends on them, and stop expanding once your verdict's evidence is decisive.

Rule `confirmed`, `plausible`, or `refuted` per your brief, with the corrected trigger where relevant, and rule on priority and action per your brief's calibration (noting any change and why). Report the one sentence of justification and the quoted line(s) that support your verdict for `confirmed`/`refuted`. Note any observation (an accurate fact outside your mandate to verdict — one sentence plus one `file:line` pointer) separately, never smuggled into a verdict. There is only one candidate, so no deduplication/merge-list is needed, but state that explicitly.

Return your full report (verdict, justification, quoted evidence, corrected trigger if any, priority/action ruling, observations if any, and your history/sandbox disclosure) as your final message text. Do not write it to any file — return it as your answer.
```

**Verbatim report returned:**

```markdown
## Verification Report — `astral-sh/uv#4424`, panel-seed1

**One candidate reviewed: `requirements/unrequested/environment-preference-narrowed`.** No deduplication needed (single candidate).

### Verdict: **confirmed**

**Justification:** The diff at the cited anchor exactly matches the claim — `find_interpreter`'s call to `Toolchain::find_or_fetch` changes `EnvironmentPreference::Any` to `EnvironmentPreference::OnlySystem` — and this narrowing is real, mechanically demonstrable, silently reachable through five call sites, and mentioned nowhere in the PR body, commit message, or supplied review material, even though it is orthogonal to the `ToolchainPreference` feature the PR claims to add.

**Quoted evidence:**

Diff (`git diff main review-head -- crates/uv/src/commands/project/mod.rs`):
```
     let interpreter = Toolchain::find_or_fetch(
         python_request,
-        EnvironmentPreference::Any,
-        ToolchainPreference::from_settings(PreviewMode::Enabled),
+        EnvironmentPreference::OnlySystem,
+        toolchain_preference,
         client_builder,
         cache,
     )
```
`crates/uv/src/commands/project/mod.rs:187` (head) confirms the anchor.

Enum semantics, `crates/uv-toolchain/src/discovery.rs:74–83`:
```
pub enum EnvironmentPreference {
    OnlyVirtual,
    ExplicitSystem,
    OnlySystem,   // Only use a system environment, ignore virtual environments.
    Any,          // Allow any environment.
}
```
Discovery dispatch, `crates/uv-toolchain/src/discovery.rs:355–360`:
```
EnvironmentPreference::ExplicitSystem | EnvironmentPreference::Any => {
    Box::new(from_environments.chain(from_installed))
}
EnvironmentPreference::OnlySystem => Box::new(from_installed),
```
where `from_environments` (`discovery.rs:204–244`) reads `VIRTUAL_ENV` (`virtualenv_from_env`), `CONDA_PREFIX`, and a discovered `.venv` up the directory tree (`virtualenv_from_working_dir`). `OnlySystem` drops this chain entirely.

Project-venv gate, `crates/uv/src/commands/project/mod.rs:93–97`:
```
pub(crate) fn find_environment(workspace: &Workspace, cache: &Cache) -> ... {
    PythonEnvironment::from_root(workspace.venv(), cache)
}
```
— this only checks the project's *own* `.venv`; `Toolchain::find_or_fetch` (where the narrowing lands) is the fallback path exactly when that own-venv check fails, so the trigger is real and matches the candidate's description.

**Call-site confirmation** (`git grep -n "find_interpreter\|init_environment" -- crates/uv/src/commands/project/*.rs`): `add.rs:53`, `lock.rs:51`, `remove.rs:86`, `run.rs:66`, `sync.rs:53` all route through the narrowed function, matching the claim's "five of the eight commands."

**PR body verified verbatim** in `/tmp/holdout/packets/d/packet.md:58`: "Adds `--toolchain-preference` and `tool.uv.toolchain-preference` to configure if system or managed toolchains are preferred. Users can opt-out of managed toolchains or system toolchains entirely as well." — no mention of `EnvironmentPreference`/venv-vs-system discovery anywhere in the packet (`grep -i "EnvironmentPreference\|OnlySystem"` on the packet returned nothing), and the sole reviewer comment (BurntSushi) discusses only the flag's naming.

**Corrected trigger:** none needed — the candidate's stated trigger (active foreign `VIRTUAL_ENV`, or a discovered `.venv`, while the project's own `.venv` is absent/insufficient) is exactly the mechanism the code implements; verified directly rather than corrected.

### Priority / Action

- **Priority: P2 — kept.** Not P0 (requires the specific precondition of a foreign/active venv plus an unsatisfied project venv, so it doesn't hold under all inputs); P2 is a fair calibration for a real, silent, out-of-scope behavior change with a realistic but non-universal trigger.
- **Action: `consider` — kept.** The mechanism is demonstrated, but whether adopting a foreign venv's interpreter to bootstrap a *new* project venv was ever correct behavior is itself debatable (arguably `OnlySystem` is the more defensible choice for creating a fresh environment); no demonstrated merge-breaking consequence was found, only an undocumented scope change. `must-fix` is not licensed here — `consider` (surfacing the unrequested scope change for maintainer sign-off) is the right action, matching the finder's own rating.

### Observations (not verdicts)

- The unrelated `EnvironmentPreference::Any` call in `run.rs`'s ephemeral-environment path (used for `uv run --with` under `--isolated`) is untouched by this diff and remains `Any` — `crates/uv/src/commands/project/run.rs:145`.

### History / sandbox disclosure

Commands run: `git log --oneline -5 <review-head|main>`, `git rev-parse review-head main`, `git show review-head:<path>`, `git diff main review-head -- <path>`, `git grep -n ... review-head -- <glob>`, plus `grep`/`ls` on `/tmp/holdout/packets/d/packet.md`. `git log` confirms `review-head` (`a2e6b9c6`) is exactly one commit ahead of `main`/base (`e783a799`); I did not read, reference, or diff against anything past `a2e6b9c6bd0257510240886549ba9e3623299739`. All reads stayed within `/tmp/holdout/runs/d/panel-seed1`, `/tmp/holdout/skills/panel/`, `/tmp/holdout/packets/d/`, and `/tmp/holdout/work/d/panel-seed1/`. No `cargo`/`rustc`/`uv`/`python` tooling was run.
```

**Sandbox note on the verifier's own disclosure:** the verifier read
`/tmp/holdout/packets/d/packet.md` (to cross-check the PR body's exact wording and confirm no
mention of `EnvironmentPreference`/`OnlySystem` anywhere in the packet). This is inside the allowed
sandbox (dispatch rule 6 / packet run condition 7 both name the packet directory as an allowed read
path), so it is disclosed here for completeness but is not a violation.


## 6a. Every finding, question, and observation that survives to publication (full text; the payload
file has the same content rendered in postable shape — this section is the analytical record)

### Finding 1 — `[Requirements] [consider] [P2]`

- **id:** `requirements/unrequested/environment-preference-narrowed`
- **axis:** Requirements
- **anchor:** `crates/uv/src/commands/project/mod.rs:187` (diff-touched; validated against
  `git diff main review-head --unified=0 -- crates/uv/src/commands/project/mod.rs`, hunk
  `@@ -186,2 +187,2 @@`, confirming line 187 on `RIGHT` is touched)
- **fix:** same as anchor
- **claim:** `find_interpreter`'s call to `Toolchain::find_or_fetch` changes its
  `EnvironmentPreference` argument from `Any` (base) to `OnlySystem` (head) — a change orthogonal to
  the `ToolchainPreference` feature the PR body describes, unmentioned anywhere in the body, commit
  message, or review record, and reachable through 5 of the 8 commands this PR touches (`lock`,
  `add`, `remove`, `run`, `sync`, via `find_interpreter`/`init_environment`).
- **trigger:** a user runs `uv lock`/`sync`/`add`/`remove`/non-isolated `run` while a foreign virtual
  environment is active/discoverable and the project's own `.venv` is absent or unsatisfying;
  pre-diff that foreign environment's interpreter was eligible, post-diff it is excluded.
- **verification status and evidence:** **confirmed** by the fresh-context verifier (agent
  `a7f2f474303c4e791`). Evidence quoted in the verifier's report (§ 5c): the diff hunk itself, the
  `EnvironmentPreference` enum definition and its discovery-dispatch match arms
  (`crates/uv-toolchain/src/discovery.rs:74-83`, `355-360`), the project-venv-only gate at
  `crates/uv/src/commands/project/mod.rs:93-97` establishing that `find_or_fetch`'s branch is exactly
  the fallback path the trigger describes, and a call-site sweep (`add.rs:53`, `lock.rs:51`,
  `remove.rs:86`, `run.rs:66`, `sync.rs:53`) confirming the 5-of-8 fan-out. The verifier also
  independently checked the packet's PR body text for any mention of `EnvironmentPreference`/
  `OnlySystem` and found none. Priority (P2) and action (`consider`) both kept unchanged by the
  verifier, with stated reasoning (not P0 because it needs a specific precondition; `consider` not
  `must-fix` because no demonstrated merge-breaking consequence, only an undocumented scope change,
  and the narrowing is arguably even the more defensible behavior for bootstrapping a fresh venv).
- **trigger scenario:** see above; unchanged from the finder's original (verifier: "none needed —
  the candidate's stated trigger... is exactly the mechanism the code implements").

### Question — B6, naming/value-vocabulary deferral

- **id:** `question/cli-rs/toolchain-preference-naming`
- **action:** question (no axis, per `finding-format.md`'s trailer contract for questions)
- **anchor (judgment call — see § 10):** `crates/uv/src/cli.rs:92-94`, the CLI flag's own definition
  site — chosen as the single most demonstrative site for a naming question that, in the review
  record, actually concerns multiple call sites (`cli.rs`'s flag, `discovery.rs`'s enum variants,
  `settings.rs`'s config field all share the same name/vocabulary), since the anchor ladder has no
  single "fix site in the diff" for a naming decision that spans a whole concept rather than one
  line.
- **content:** whether `--toolchain-preference`/`toolchain-preference` and its `prefer-*` value
  vocabulary are final, given the pull request's own review record (reproduced verbatim in
  `requirements-axis-block.md` and quoted again in the payload) shows the name was an active,
  unresolved bikeshed at merge time and the author said explicitly "I'm fine adjusting this later if
  we need to since it's in preview" — with no closing decision visible in the material pinned to
  this run, and no repository rule to settle it by default (`CONTRIBUTING.md` has no CLI-naming
  section — confirmed by both finders independently reading the same base-branch copy).
- **Why no static evidence could settle it:** the review record's own words say the name may still
  change; reading the code at this one pinned head cannot show what happened in a later,
  unreachable commit or an off-thread maintainer decision.
- **What would settle it:** a later commit renaming the flag/values, or a maintainer statement
  closing the bikeshed thread — neither is visible in the history available to this run (history is
  truncated at the pinned head by design; see § 8).
- **Verification status:** never sent to the verifier, by design — `SKILL.md` step 3: "the
  Requirements axis's 'cannot tell from the code' bucket… resolve to questions at the finder… Route
  them straight to publication as questions."

### Observations published (3 of 5 raised; publication cap = 3, per `publishing.md` § The summary)

1. `crates/uv/src/commands/project/run.rs:145` — the sibling `uv run --with`/ephemeral-environment
   `EnvironmentPreference::Any` call is untouched by this diff (verifier).
2. `crates/uv/src/settings.rs:56-63` — the per-command-family default carries an inline
   `TODO(zanieb)` acknowledging a known compromise (Requirements finder).
3. `crates/uv/Cargo.toml:36` — a missing space before a closing brace in the new features list, no
   lint gate, no behavioral effect (Code finder).

### Observations dropped at the cap (recorded here per `publishing.md`'s instruction to name every
dropped observation with the marker `observation (unpublished, cap)` and its evidence pointer — the
caller receives these in this session report, never on the pull request)

- `observation (unpublished, cap)` — `crates/uv/tests/show_settings.rs:60` — all `GlobalSettings`
  test-fixture occurrences (16/16/16 by the finder's own count) uniformly gained
  `toolchain_preference: OnlySystem` (Requirements finder).
- `observation (unpublished, cap)` — `PREVIEW-CHANGELOG.md` — no documentation file mentions
  `toolchain-preference` before or after this diff, so no stale-doc peer exists to flag (Requirements
  finder, from the changed-contract sweep's negative result).

**How the cap choice was made (judgment call):** `publishing.md` says to keep "the three with the
most decisive evidence." I ranked the 5 candidates by how directly and concretely their evidence
pointer demonstrates the stated fact: the `run.rs:145` and `Cargo.toml:36` observations each cite one
exact line whose content alone settles the claim; the `settings.rs:56-63` observation quotes an
inline `TODO` comment directly on point. The `show_settings.rs:60` observation's fact (a 16/16/16
uniformity count across the whole file) is real but requires more verification work from a single
cited line than the top three, and the `PREVIEW-CHANGELOG.md` observation asserts an absence with no
specific line to point at at all (which is also exactly why its ledger row failed the validator's
evidence-pointer grammar — see § 2). I kept `run.rs:145`, `settings.rs:56-63`, and `Cargo.toml:36`;
dropped the other two. This ranking is a judgment call, not a mechanical rule the skill specifies
beyond "most decisive evidence" in prose.

## 7. Mechanism checklist

- **Question channel:** fired. B6 (naming/value-vocabulary deferral) resolved to a question at the
  Requirements finder's own desk (never sent to the verifier), per `SKILL.md` step 3's "cannot tell
  from the code" carve-out. Demonstrated in § 6a and in `finder-requirements.md`'s "B6" sorting
  entry.
- **Clean-verdict or related-acquittal verification (which mode, which rows, any re-open):** the
  verifier ran in the ordinary "rule on the supplied candidates" mode (`## Candidates`), not a
  related-acquittals mode — `verify.md` in this skill snapshot has no `## Related acquittals`
  heading at all (confirmed by grep, § 5b), so `build_verifier_prompt.py` never emitted a `##
  Related acquitted ledger rows` section, and none was owed. This is a first review with no prior
  review from this identity, so no re-open scenario applies. **Did not fire** (mechanism absent from
  this skill's verifier brief, not a run failure).
- **Observations:** fired. 5 raised across 2 finders + 1 verifier, pooled, none needed
  deduplication (all distinct `file:line` facts), 3 published under the summary's bounded
  `Observations` section, 2 recorded as `observation (unpublished, cap)` in this report (§ 6a).
  Demonstrated in the payload's `## Observations` section and this report's § 6a.
- **Fix-sufficiency check on any concurrency/invariant candidate:** **did not fire** — no candidate
  in this run touches concurrency, locking, or an invariant of that shape. The sole candidate is a
  discovery-source scoping change (`EnvironmentPreference::Any → OnlySystem`), which the verifier
  treated with the ordinary confirm/trigger-demonstration protocol, not the concurrency-specific
  fix-sufficiency check (`verify.md` names no such check as distinct from ordinary verification for
  non-concurrency candidates, and none of the asymmetry examples — races, null-on-rare-path, off-by-
  one, retry storms — apply here).
- **Follow-up verifier round:** **did not fire** — one verifier pass on one candidate settled it
  (`confirmed`); nothing came back `plausible` requiring a second look, and this skill's contract
  does not define an automatic follow-up round distinct from the one mandatory pass per candidate
  (that iterative-round mechanism, per `DESIGN.md`, belongs to a different, more elaborate
  verification-routing design this skill explicitly did not adopt).
- **Deferral handling (any explicit deferral in the review record and how it was treated):** fired.
  One explicit deferral found in the pull request's non-review conversation — `zanieb`,
  2024-06-20T17:27:06Z: "I'm fine adjusting this later if we need to since it's in preview,"
  postponing the CLI flag's naming/value-vocabulary decision on unreleased (preview) public surface.
  Extracted at step 1 (packet reading), forwarded verbatim with author and surface to the
  Requirements finder's axis-specific block (§ 5, `requirements-axis-block.md`) exactly as
  `SKILL.md` step 1/step 2 specify ("on a first review nothing else from prior review reaches a
  finder"), restated by the finder as its own list entry B6 per `requirements-axis.md` § Step 2's
  deferral handling, and resolved to a question rather than a `Met`/`Not met` requirement or a
  `requirements/unrequested/…` candidate, since no repository rule settles CLI-flag naming. This is
  also why the Requirements axis could not be `Passed` even setting the coverage shortfall aside:
  "An axis with an open deferral question cannot be `Passed`; it is `Waiting for information`" per
  `requirements-axis.md` § Step 2 — though in this run the coverage shortfall independently drives
  the overall status to `Incomplete` regardless (§ 10).
- **Retrospective mode:** fired, as instructed. The payload's first line names the retrospective
  condition and the posting identity, per `SKILL.md` step 1 ("a published summary states on its
  first line that this is a retrospective review of a merged change") and dispatch rule 2. Every
  step through step 4 ran exactly as it would for an open pull request; step 4's actual `gh api`
  submission was replaced by rendering, per the packet's run condition 4 and dispatch rule 2 ("Where
  a step says 'publish,' render instead and stop").

## 10. Notes: status derivation, judgment calls, and wall clock

### Status ladder, worked explicitly (`publishing.md` § Status)

1. **Any unsettled `must-fix`?** No. The only finding is `[consider]` at P2. → does not apply.
2. **Coverage short of complete?** **Yes.** `publishing.md`'s own definition of coverage ("every
   file in the changed-file manifest is `reviewed` or `ignored` with a defensible reason, and every
   fetch and check the run started either finished or is named as unfinished") is, read narrowly,
   satisfied — all 22 files are accounted for on both axes with reasons, and every check either
   finished or is named as unfinished in the reports. But `SKILL.md` step 2 makes a **stronger,
   explicit** statement that overrides the narrow reading for this case: *"A finder that fails twice
   leaves the run incomplete for that axis, and the summary names the axis and the violation."* This
   is a direct instruction from the skill I am bound to follow as written (dispatch rule 1), and it
   is unconditional — it does not carve out an exception for violations that are "merely" cosmetic
   evidence-pointer formatting on 2 of 12 ledger rows. I am treating this as controlling: the
   Requirements axis is incomplete, coverage is short of complete, and the ladder resolves to
   **`Incomplete`** here, before question-handling is even reached at step 3.
3. *(Not reached, but noted for the record: had coverage been complete, step 3 would have found the
   B6 open question outcome-changing — the finding's own priority/action wouldn't move, but a
   genuinely open naming decision on public surface could still change what ships — so the status
   would have been `Needs Information` rather than `Approved` even absent the coverage shortfall.)*
4. *(Not reached.)*

**Derived status: `Incomplete`.** Event: `COMMENT` (native for `Incomplete` — "`Incomplete` must
never be carried by `APPROVE` whatever the authorization," and it has no gating form to begin with,
so the authorization question that would otherwise decide `COMMENT` vs. a gating event does not even
arise here).

### Judgment calls (every ambiguity in the skill's contract, what I treated as guidance and why)

1. **The dispatch's "context digest" instruction vs. this skill's actual contract.** Detailed in § 6.
   Treated as inapplicable boilerplate from a sibling arm's contract (the Skeptic line's
   context-fingerprint mechanism), because this skill's own `DESIGN.md` names that exact mechanism
   as deliberately not adopted. Computed the pinned run-identity/trailer values this skill's contract
   actually specifies instead, once, via the skill's own script.
2. **Delivering finder/verifier prompts via "read this file" wrappers instead of pasting the full
   assembled block as the literal `Agent` tool argument.** Detailed in § 4.1. Judged functionally
   identical (same bytes, same order, same constraints, delivered as the sub-agent's first read
   instead of as the outer call's argument) and necessary given the size of the assembled blocks
   (~43-47KB each). Disclosed rather than treated as silently equivalent.
3. **My own process error, twice, on the same category of mistake:** hand-editing a finder's report
   to fix a shape violation instead of following `SKILL.md`'s explicit re-dispatch instruction (Code
   finder, § 2), and initially writing a "verbatim" file that wasn't actually verbatim (silently
   de-fencing the Requirements finder's duplicate `manifest` block instead of preserving it) before
   validating. Both caught and corrected before anything downstream consumed the wrong version —
   disclosed in full in § 2 and § 4 rather than absorbed silently, per the dispatch's instruction to
   "never write a sub-agent's report into your own report before it has actually returned it," which
   I read as encompassing "and never write something other than what it actually returned."
4. **No third finder re-dispatch after the Requirements axis's second validation failure.** Detailed
   in § 2. `SKILL.md` authorizes exactly one re-dispatch; I honored the cap even though the residual
   violation was narrow, and carried the axis's substantive content forward as an incomplete-but-
   published axis, per `publishing.md`'s own statement that incompleteness is a valid terminal state
   that still publishes what was verified.
5. **My own re-dispatch instructions to the Requirements finder were partly wrong.** I told it a
   bare file path was valid ledger evidence, conflating `build_verifier_prompt.py`'s `fix`-field
   grammar (which does accept a bare path) with `validate_finder_report.py`'s ledger-evidence grammar
   (which does not). This is why round 2 still failed. Disclosed in § 2 and § 4.4 rather than
   corrected retroactively; I did not attempt a third dispatch to fix my own mistake, per judgment
   call 4 above.
6. **The naming-deferral question's anchor.** `finding-format.md`'s anchor ladder is written for
   single-line defects; a naming/vocabulary question spanning three files (the CLI flag's own
   definition, the enum's variant names, the config field) has no one obviously correct "fix site."
   I anchored it at the CLI flag's own definition (`crates/uv/src/cli.rs:92-94`) as the most
   user-facing, demonstrative single site, and treated it as body-resident in the payload's `## Open
   questions` section rather than inventing a `comments[]` entry for it — reasoning from
   `publishing.md`'s phase-1 fixture, whose one worked question example is likewise rendered fully
   in the body rather than as a separate line comment. Detailed in § 6a.
7. **Observation cap selection.** `publishing.md` says keep "the three with the most decisive
   evidence" but does not define decisiveness mechanically. Ranked as described in § 6a.
8. **Treating `PREVIEW-CHANGELOG.md` existing (confirmed via `git ls-tree`, § "Requirements axis
   round 2") as consistent with the finder's own "no hits" sweep result** rather than as a
   contradiction — the finder's claim was about content (no mention of `toolchain-preference`
   anywhere in `*.md`), not about the file's existence, and I did not re-run the sweep myself (that
   would be re-doing the finder's investigation, which is exactly what the re-dispatch process is
   supposed to avoid); I only checked that the file the ledger row pointed at actually exists in the
   tree, which it does.

### Wall clock

Start: 2026-09-04T21:42:35Z (UTC, `date -u` at the top of this cell, before reading `SKILL.md`).
End: 2026-09-04T22:20:42Z (UTC, `date -u` immediately before writing this closing section — a few
minutes of report-assembly work follow this timestamp to finish both output files, which this note
does not attempt to time separately). **Elapsed: approximately 38 minutes** of wall clock for this
entire cell, across 5 sequential foreground sub-agent dispatches (2 Code finder rounds, 2
Requirements finder rounds, 1 verifier) plus all orchestration, validation, and both output files.
