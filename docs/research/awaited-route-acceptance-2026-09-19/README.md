# Awaited-route acceptance for issue #273 — 2026-09-19

Issue #273's instruction changes landed in PR #275 and PR #282. Its **Acceptance and validation** section lists eight items, and those two pull requests left items 3, 4, 5 (in part), and 6 open, with item 1 only partly exercised. This record closes what can be closed from captured runs on the affected runtime, Claude Code, and names what stays open. Nothing here changes a skill; every observation is from a transcript, a result envelope, or a fixture artifact kept in this directory.

Two kinds of evidence appear below.

- **Captured production runs.** Deliveries on `kamui/skills` between 2026-09-15 and 2026-09-19, read back from the session transcripts under `~/.claude/projects/<project>/<session>/subagents/agent-<id>.jsonl`. Agent ids, timestamps, models, and tool parameters are quoted from those files. The transcripts are not copied here; the ids let them be re-read while the retention window lasts.
- **Disposable fixtures run for this record.** A tiny repository with a planted defect (`item5-fixture/make_fixture.sh`), a headless session configured as a host with no awaited route (`item3-no-route-host/`), and fresh-continuation fixtures for the failure cases item 5 names. Their prompts, reports, and result envelopes are in this directory.

Every subagent below was dispatched through Claude Code's `Agent` tool unless the row says otherwise, and "foreground" means `run_in_background=false` on that call, whose tool result carries the completed report when the subagent hands back.

## Summary by acceptance item

| Item | What #273 asks | State after this record |
| --- | --- | --- |
| 1 | The real nested sequence: implement, first review with a required fix, committed fix, deliberately delayed addendum with its verifier, consumed before publication, hand-back only after the PR exists | Established: #282's run (delayed addendum); PR #308 and PR #300 implement steps below repeat the sequence without the delay |
| 2 | Both continuation routes where available, with the host operation recorded; a send acknowledgment is not proof | Established: foreground `Agent` returns inside the tool call; `SendMessage` and fork-mode dispatch return acknowledgments only (three independent observations below) |
| 3 | A host with neither route reports `review-wait-unavailable` before dispatching or publishing | **Established today** on a fork-mode headless host (`item3-no-route-host/`) |
| 4 | `resolve-review` with no code changes but a draft check, with a reviewer-induced commit, with revised replies; assessment before drafts; no approval for an obsolete head or draft set | Established from the PR #298, PR #278, and PR #276 rounds |
| 5 | Missing or mismatched records, a partial or failed reviewer or verifier, a disputed blocking finding, a required verifier still pending | Records: #282. Failed reviewer and partial verifier: PR #278 round 2 and PR #300, with one deviation noted. **Disputed blocker and pending verifier: established today** on fixtures (`item5-fixture/`): blocker kept blocking, no replacement worker, batch cap held, publication refused |
| 6 | #264's unsupported-host fallback and failure-after-start stay distinct | Not applicable: `main` carries no #264 artifact (checked at `4ca5a5a`) |
| 7 | A supported delayed-review run ends with one open PR at the pushed, reviewed head, or a named failure | Established: #282 (`604b616`), PR #308 (`a6d4ca6`), PR #300 (`dd0701f`), and this record's own pull request |
| 8 | Changelog entry, DESIGN.md counts, checks, `sync-global-skills` after merge | Entry and counts landed with #275/#282; global copies matched `main` at `4ca5a5a` on 2026-09-19 (`~/.agents/.skill-lock.json` `updatedAt` 2026-09-19T16:08:40Z); this record changes no skill text |

## Item 1 and item 7: the nested sequence, consumed before publication

Beyond #275 and #282's own runs, two later `finish-it` deliveries ran the whole sequence on Claude Code with the current text.

**PR #308 (issue #296), session `t3code-f9bd6ea3`, 2026-09-16.** The implement step `a4603589e7b42c835` (Fable 5.1, foreground under `finish-it`, 21:12:17Z–22:45:06Z) dispatched its first reviewer `a9f45516cee1dca5d` (Opus, foreground, 21:35:30Z–22:03:24Z), which dispatched verifier `ac0e03842794b0160` (Opus, foreground, 21:51:35Z–21:57:19Z). The review returned one must-fix and one consider. After the fix commit the step dispatched a **fresh continuation** `a58cf5bdf9110960a` (Opus, foreground, 22:08:09Z–22:43:28Z), which validated the original record paths, inspected the delta, and dispatched the follow-up verifier `a5f3f4f5753261e30` (foreground, 22:18:19Z–22:32:24Z; 17 ledger rulings, 3 re-opened, re-falsified by the continuation). The addendum landed at `/tmp/reviewcode296.OvP7uk/addenda/addendum-1.md`; the step reported "both reviewer phases ran on awaited foreground routes at the Opus tier", and PR #308 opened at the reviewed head `a6d4ca64e62ea7cb5bd7e0e7b6d7493bc2887e62` after the continuation returned.

**PR #300 (issue #294), session `t3code-e8a96bf9`, 2026-09-16.** Implement step `a3f866dbe4370131d` (Opus, 16:57:58Z–17:23:33Z); first reviewer `a6903a53dbe16dcb2` (Sonnet, foreground, 17:08:59Z–17:21:58Z) with clean-verdict verifier `acd5c50fc7ec8f74c` (foreground). Approved with no findings, so no continuation ran; the pull request opened at `dd0701fe09a0daecdd6798e616f9bff091ef74be`.

**Issues #286 and #305, session `t3code-d9681fd6`, 2026-09-19.** The most recent gate reviews under the `implementation-gate` profile. Reviewer `a7009b68f790fe58b` (Opus, foreground, 09:41:05Z–10:02:37Z) with verifier `ae912b587a190d080` (foreground); its record at `/tmp/review-code-i286.Jb9m57/record.json` names the batch's host operation as `Agent tool, subagent_type general-purpose, model opus, run_in_background=false (foreground dispatch returning the completed batch)`. A continuation for the #305 range wrote `addenda/addendum-dbd7c826….json` (format `implement-publish-review-addendum/1`) beside `/tmp/review-code-305.ksNnJy/record.json`, recording `record_path_validation: declared 30, readable 30, mismatches []`, the original record's SHA-256, and its batch operation — the addendum contract from #273's part 2, observed in production.

## Item 2: the two routes, and what an acknowledgment looks like

| Observation | Host operation | What came back |
| --- | --- | --- |
| #275 probe `a1e734bb0ef63c919`, 2026-09-15 | Foreground `Agent`, then `SendMessage` to the finished agent | The `Agent` call returned the result inside the tool call; `SendMessage` returned `{"message":"Resuming agent …"}` and the resumed result arrived only as a later message |
| PR #300 review step `adf5113ddc45ad41c`, 2026-09-16 17:46:15Z | `SendMessage` from a depth-1 subagent to its finished verifier `ae9bb639d28cd4375`, asking for a missing `conclusion` field | Returned in 2 s: `{"success":true,"message":"Resuming agent ae9bb63",…}`. The verifier's reply at 17:47:04Z was "queued for delivery … at its next tool round"; no such delivery appears in the primary's transcript before its hand-back at 17:50:52Z. The primary completed the structural repair itself from the rulings it already held, dispatched no replacement, and published |
| This record's item-3 relay root, 2026-09-19 17:35:27Z | `Agent` under fork mode (no `run_in_background` parameter) | `Async agent launched successfully … You will be notified automatically when it completes`; the result arrived as a task notification 82 s later (`item3-no-route-host/root-observation.json`) |
| Every reviewer phase in the PR #276, #278, #298, #300, #308 rows of this record | `Agent` with `run_in_background=false` | The tool result, delivered when the subagent handed back, reads `This agent's report was delivered to you as a message from "<id>" (its SubagentHandback call)` with usage; the dispatching step was still active |

So on Claude Code 2.1.27x the awaited route is the foreground `Agent` dispatch, the resumption route acknowledges only, and the skills' "fresh continuation" is the route every continuation above used.

## Item 3: a host with neither route

Fork mode, on by default in interactive sessions, removes the `Agent` tool's `run_in_background` parameter and runs every dispatch in the background (Claude Code sub-agents documentation, *Turn fork mode on or off*). A headless `claude -p` session with `CLAUDE_CODE_FORK_SUBAGENT=1` reproduces that host without touching any global setting: the variable applies to that process only.

**Setup** (`item3-no-route-host/launch.sh`, Claude Code 2.1.278, macOS): a Sonnet relay root wrote the parameter names of its own `Agent` tool (`description, isolation, model, prompt, subagent_type` — `root-tools.json`), then dispatched one general-purpose Opus subagent with `brief-step.md`: the implement step of an `implement-publish` delivery resumed at step 4, with the fixture repository at head `8da72475`, `spec.md` as the spec source, and the step-3 packet `evidence-packet.md`.

**Result** (`step-report.md`, `step-trace.txt`, `result.json`): the step loaded `implement-publish` through the Skill tool, inspected its tool surface (three `ToolSearch` calls covering `Monitor`, `SendMessage`, `TaskStop`), read the packet, and stopped with **`review-wait-unavailable` before dispatching anything**, naming the phase (the first review, `mode: one-shot`, `profile: implementation-gate`, over `787236cd…8da72475`), the missing operation (an awaited dispatch: no foreground option, no blocking wait or join anywhere in the tool surface, `SendMessage` returning on delivery rather than completion), and the pending work (none). Its transcript has no `Agent` and no `SendMessage` call; every assistant line ran on `claude-opus-5` at `high`. The whole session cost $0.75 and took 22 s of wall clock after the dispatch.

Two incidental observations: the relay's `Agent` result arrived as a later task notification, not inside the tool call, which is the shape #273 diagnosed; and the step's compound `cd && git …` command was denied by the allow-list, so it carried the head from the packet instead of confirming it and said so.

## Item 4: `resolve-review` rounds

**No code changes, then a draft check — PR #298, session `t3code-bf658ac0`, 2026-09-16.** Resolve step `a0b74ce6bdae4e8ff` (Sonnet, 09:49:43Z–10:10:37Z). Its first phase `aa0277219e66986b4` (Sonnet, foreground, 09:54:27Z–09:58:32Z) was briefed with starting head = final head `c09e41a3` ("the addresser made no code changes this round; verify this yourself"). Its tool sequence: read the skill, the pull request, the issue, and the protocol; diff the round; **write `step3-assessment.md` at 09:57:10Z; read `drafts.md` at 09:57:15Z**; hand back. Assessment before drafts is evidenced by the transcript order, not by the brief's instruction alone.

**A reviewer-induced commit and revised replies — the same round.** The assessment stood the candidate as a non-blocking inconsistency; the addresser committed `a190b7f` at 10:00:55Z, revised the drafts, and dispatched a **fresh continuation** `afff818042a9e2a71` (Sonnet, foreground, 10:02:27Z–10:07:14Z), briefed as "a continuation of an earlier reviewer phase … that phase is complete and is not running anymore; you replace it". It wrote `step3-assessment-v2.md` at 10:04:06Z, read `drafts.md` (revision 2) at 10:04:11Z, ran the focused suite, and handed back. The push came at 10:08:27Z, after the phase returned. The round's approval is for `a190b7f`, the pushed head.

**Several commits and an obsolete approval — PR #278 round 1, session `t3code-d92e2888`, 2026-09-16.** Resolve step `ae9152cee36dad8e3` (Opus, 01:08:09Z–02:37:09Z) ran five foreground Opus phases with commits between them (`6ea8680`, `88d23d6`, `acafb9b`, `ab62652`): independent assessment `a1af08e9ff2459d6c`; verify final head and drafts `a84c9ab2518e28536`; verify final head and **revised** drafts `a8b1b8b649b113b3a`; final verification at `acafb9b` `ade741a412e1468d6`; then, because a further commit followed that phase, confirm final delta and drafts at `ab62652` `a0c9ef433ea419318`. Each brief kept the drafts in a separate file (`/tmp/pr278-round2/2-drafts.md`) read only in its PHASE 2; the push at 02:34:47Z followed the last phase. The approval-shaped phase at `acafb9b` was not treated as covering `ab62652`.

**PR #276 round 1, session `t3code-97a8c180`, 2026-09-15.** Resolve step `a793d16294cb6fc34` (Opus) ran three foreground Opus phases: independent assessment `a9da42ad7a2842ecc`, check drafts and final head `aeda1dbdf6119ed26`, re-verify final head and drafts `a25087058d7c58a74`, then pushed `14a83e5`.

PR #276 and PR #278 round 1 ran under #275's text (before #282 merged at 2026-09-16T04:16Z); PR #298 ran after it, and its briefs carry #282's assessment-artifact rule.

## Item 5: failure cases

**Missing or mismatched records.** #282's fixture: one record path absent and one recording a foreign reviewed head produced coverage gap `review-record-invalid`, no clean addendum, no replacement reviewer, no batch. In production, the #305 continuation's `record_path_validation` (30 declared, 30 readable, no mismatches) shows the check running on the clean path.

**A failed reviewer — PR #278 round 2, session `t3code-d92e2888`, 2026-09-16.** Resolve step `a8ae5a5ff2714c674`'s phase `ab191d925f95761f6` (Opus, foreground) was terminated at 03:36:31Z by HTTP 429 (`You've hit your session limit`). The `Agent` tool result read: `Agent terminated early due to an API error … Everything below is PARTIAL output … The agent did NOT finish its task … no report was delivered.` The step consumed none of the partial output, resumed nothing, and pushed nothing; at 03:53:20Z, after the limit reset, it dispatched a new full phase `a41410775095c2f30` (foreground, briefed "a previous attempt at this task was cut off by a rate limit"), which returned APPROVE at `841d82c`; the push followed at 04:01:55Z, and the round's report disclosed the cutoff and the re-run. **Deviation to weigh:** `resolve-review` step 3 says a fresh continuation is "never … a retry of a failed phase", and this run re-ran the phase. None of item 5's four prohibited outcomes occurred: no unresolved state was dropped (the whole phase re-ran from its brief), no verification limit was reset (the step has none), no replacement ran beside a pending worker (the failed one had exited), and no false completion was published. Whether a host-terminated phase may be re-run, or must stop the round, is a call the text does not make explicitly; this record leaves the text unchanged and flags it.

**A partial verifier return — PR #300, session `t3code-e8a96bf9`, 2026-09-16.** The verifier `ae9bb639d28cd4375` handed back a structurally incomplete return (no `conclusion`). The primary `adf5113ddc45ad41c` sent it a `SendMessage` (acknowledged only, see item 2), did not wait on that resumption, completed the structural repair itself from the twelve `holds` rulings it already held, ran the accounting script at exit 0, dispatched no replacement worker and no extra batch, and published Approved at `dd0701f`.

**A disputed blocking finding and a required verifier still pending.** Exercised on the fixture; see the next section.

## Item 5 fixtures: disputed blocker and pending verifier

**The fixture** (`item5-fixture/make_fixture.sh`): a two-commit repository whose head adds `paginate` with `start = page * size` where `spec.md` requires 1-based pages, and five tests that pass against both the buggy and the corrected implementation. Every reviewer below ran on Opus at high effort (checked with `docs/research/tools/agent_effort.py` on each transcript); every dispatch was a foreground `Agent` call whose tool result carried the completed report.

**Initial gate review (R0).** Reviewer `a5d6d45e8e46ec748` (17:35:45Z–17:46:24Z; brief `r0-brief.md`, packet `r0-evidence-packet.md`) invoked `review-code` with `mode: one-shot`, `profile: implementation-gate`, and dispatched verifier `a9397d7c1d13e2199` (foreground, 17:40:40Z–17:42:56Z). Result (`r0-review.md`): Changes Requested, coverage complete; `pagination-page-offset-off-by-one` P1 must-fix, verifier-confirmed; `test-pagination-no-content-assertion` P3 consider; follow-up batch unspent; record at `/private/tmp/rc-i273-WfwNt6/record.json` (schema `implementation-gate-record/1`, validator exit 0). Two reviewer-executed checks in a disposable copy settled the packet's one unevidenced criterion empirically instead of leaving it as a question.

**A required verifier still pending (case P).** A copy of R0's private directory was altered to the state a reviewer cut off mid-batch would leave: the initial batch's raw return and accounting deleted, `verification.batches[0]` marked `returned: false` with no return paths, `outstanding: ["pagination-page-offset-off-by-one"]`, that candidate removed from the published items, status `Incomplete`, coverage `incomplete` (validator exit 0 after the edit). The fresh continuation `a619854bf88a6cabe` (17:48:41Z–17:58:39Z; brief `caseP-brief.md`) confirmed every record path at the reviewed head, found the bundle without a return, and applied `review-code` step 3's rule as written: the pending batch is spent and earns no replacement worker and no restored allowance. It dispatched exactly one batch, the unspent follow-up, as verifier `a7c7b57daf97e67a4` (foreground, 17:51:50Z–17:54:13Z), which confirmed the outstanding candidate and ruled the three related acquittals `holds`; it accounted the return at exit 0 and marked the follow-up spent. Its addendum (`caseP-addendum-1.md`, written to the copy's `addenda/`) leaves the must-fix blocking and unpublished, sets status Changes Requested, and answers the gate "no: the implement step may not proceed to publication". None of item 5's prohibited outcomes occurred: no state dropped, no limit reset (two batches in total, the cap), no competing replacement, no completion claim. The continuation also reported, without editing anything, that the altered record's summary prose, ledger annotations, and event log still narrated the deleted verdicts, and treated those verdicts as absent; that inconsistency is the fixture's, from editing only the verification accounting.

**A disputed blocking finding (case D).** On the real record, the fixture gained one commit `6f64c9a` ("Export paginate and document the import": `__all__` and a README line, nothing at the defect), and an updated packet (`caseD-evidence-packet-2.md`) carrying the rerun suite at that head plus the implementer's dispositions (`caseD-dispositions.md`): the must-fix declined on an unevidenced "header block convention in the calling application", the consider closed as optional. The fresh continuation `a63df28a032f2d9e9` (17:59:21Z–18:14:16Z; brief `caseD-brief.md`) confirmed all thirteen record paths, inspected the delta completely, evaluated the decline against its own evidence (the spec byte-identical at all three commits, no caller or convention anywhere in the tree, the commit message and docstring promising 1-based pages, the defect reproduced at the final head), and classified the finding **still-open, disputed, blocking**: "a declined disposition is intent, not outcome". It dispatched the one unspent follow-up as verifier `a60680f0d70134565` (foreground, 18:05:12Z–18:07:56Z), which confirmed the finding at the final head and ruled four ledger rows `holds`; it raised and refuted one new candidate about the `__all__` claim. Its addendum (`caseD-addendum-1.md`, written to the record's `addenda/`, original files unchanged by SHA-256 and mtime) sets Changes Requested, coverage complete, one blocking finding listed for human settlement, follow-up spent, and answers the gate "no: the implement step may not proceed to publication". It also corrected one packet label: the reviewed-head suite run was invalidated and rerun, so "retained as historical" was the wrong outcome name for it, a labeling correction and not a gap.

Both continuations, in two different failure states, arrived at the same terminal state: a confirmed blocker still blocking, two batches in total, nothing replaced, nothing approved. Agent ids, dispatch parameters, and tool results for all six fixture agents are in `agent-trace.txt`.

## Item 6: #264

`rg -n "264" skills README.md CHANGELOG.md` at `4ca5a5a` matches only a byte count in `skills/review-code/DESIGN.md`. There is no #264 experiment text on `main`, so its unsupported-host fallback and failure-after-start paths cannot be distinguished here, and nothing in this record authorizes a replacement reviewer inside that experiment. Unchanged from #275 and #282.

## Cost of the runs made for this record

| Run | Agents | Spend |
| --- | ---: | --- |
| Item 3 headless session (relay root plus the step) | 2 | $0.75 (result envelope) |
| Fixture initial review R0 with its verifier | 2 | not metered by the host; 146,457 subagent tokens, 33 tool uses, 653 s |
| Case P continuation with its verifier | 2 | 129,477 subagent tokens, 30 tool uses, 610 s |
| Case D continuation with its verifier | 2 | 172,954 subagent tokens, 27 tool uses, 911 s |

The token figures are the harness's `<usage>` lines on each hand-back and count the dispatching subagent only; verifier usage sits inside its own transcript.

## What stays open

- Item 5's failed-reviewer wording (above): decide whether a host-terminated phase may be re-run.
- Item 6 until #264 has an artifact.
- Item 8's `scripts/sync-global-skills` run after this record merges, which changes no skill text, so the sync is expected to be a no-op.
