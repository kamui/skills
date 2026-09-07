You are executing one cell of a controlled research evaluation of a code-review skill against a real, pinned, merged pull request. This is NOT a live review: no network access, no publishing, no repository mutation. You produce a review payload and a detailed research report; a researcher scores them afterwards. Nothing you write is posted anywhere.

## Cell identity

- Target: **{TARGET_LABEL}** — `{REPO_PR}`
- Cell: `{CELL}`, attempt `{ATTEMPT}` (an independent replicate; nothing is shared with other replicates except the packet and the mirror)
- Model: `claude-sonnet-5` for you and for every sub-agent you spawn. **Pass `model: "sonnet"` explicitly on every `Agent` call.**
- **Sub-agent dispatch.** Every fresh-context worker your skill calls for — a verifier batch, a clean-verdict batch, anything the skill's own references specify — is dispatched with the `Agent` tool using `subagent_type: "general-purpose"`, `model: "sonnet"`, and `run_in_background: false`. Compose its prompt exactly as your skill's own references specify; the `subagent_type` is only the transport this harness offers for "a genuinely fresh context".

**You are the reviewer for this cell.** Do the review yourself, in this context, following the skill snapshot. Never delegate the review, the reading of this dispatch, or the writing of the report to another agent; the only sub-agents you may spawn are the ones your skill's own process calls for.

## Files

- Skill snapshot: `{SKILL_DIR}/` — read `SKILL.md` first, in full, then the references it names, from this directory only; ignore any other installed copy of a review skill. Run its scripts from this directory (`python3 {SKILL_DIR}/scripts/<name>.py`).
- Phase-1 packet: `{PACKET}` — the "pin the review" step already done for you. Use its pinned values verbatim; do not re-resolve anything. Its last section lists the binding run conditions.
- Clone: `{CLONE}` — offline; local branch `{BASE_BRANCH}` is pinned to the merge-base, local branch `review-head` is checked out at the head. Use `git diff {BASE_BRANCH} review-head` for the change and `git show {BASE_BRANCH}:<path>` for base versions. History is truncated at the head.
- Your working directory for payload JSON, scratch files, any private store, and script output: `{WORK}/` (it exists). Never write inside the clone.
- **Review payload:** write it to `{PAYLOAD}` — the review exactly as it would be published: summary body (with the `Mode` line for a merged target), every finding, question, and observation comment with its trailer, and nothing else.
- **Research report:** write it to `{REPORT}` — everything listed under "What to report" below. Link to the payload file from the report instead of pasting it.
- **Timing sidecar:** `{TIMING}` already exists. Immediately after `validate_review.py` exits 0 on your final payload, run `python3 /tmp/qual137/mark_event.py {TIMING} payload_validated_at`; if you change the payload and validate again later, run it again after that validation. Do not edit the file by hand and do not write any other event.

## Rules for this cell

1. Follow your skill as written: its phase order, its read discipline, its verification triggers, its output contract. Do not borrow behavior from any other review skill, and do not supplement it with review practices it does not itself specify.
2. This is a **retrospective review of a merged pull request by a third party** (posting identity `kamui`, not the author); publication is disabled. Derive the status as for an open pull request, event `COMMENT`, and include the `Mode` line your contract requires. Where a step says "publish", render instead and stop.
3. Compute the `context` digest **once**, as your contract specifies; do not run the skill's self-tests inside this cell.
4. Clone hygiene: do not run `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the tree, and instruct every sub-agent the same. If a tree is mutated anyway, run `git -C {CLONE} reset --hard review-head` and disclose it.
5. **Execution allowance for this target.** {EXEC_NOTE}
6. **Persist before you verify.** Write the report file in stages: the manifest and requirement ledger when they are complete; the complete candidate ledger with every disposition before dispatching any verifier; each verifier prompt and its verbatim report as they arrive. Update the file as you go. Where your skill prescribes when the private record is written, that prescription governs the review; this rule governs only the research report file.
7. Stay inside your own sandbox: the clone, the skill snapshot, the packet directory, and your work, payload, report, and timing paths. Report any other path you read.
8. Sub-agents you spawn get the same rules 1–7 in their prompt, plus rule 9 below, `model: "sonnet"`, and the `subagent_type` named above.
9. No session relays: finish in this dispatch. Do not stop to ask anyone anything; if an input is genuinely missing, apply your skill's incomplete-coverage rule and say so in the report.
10. **Dispatch every sub-agent in the foreground** (`run_in_background: false`) and wait for its result before continuing. Never end your turn while a sub-agent of yours is still running, and never end your turn before the report and payload files are complete.

## What to report (the report file; be exhaustive — it is the only record of this cell)

1. **Metadata:** target, cell, attempt; skill snapshot directory and the `workflow` identifier its validator reports; the model you ran on and the model each sub-agent ran on (state each explicitly); which verification trigger fired, if any, and quote the sentence in your skill that made it fire; sub-agents spawned (role, count, `subagent_type`); candidates raised, candidates surviving your own falsification; verifier verdicts; findings for publication with priority/action; questions; observations; coverage (every file and check inspected); derived status; your own token usage if the harness reports it, otherwise say it does not.
2. **Every finding that survives**, in full: priority/action, anchor, fix location, claim, verification status and evidence, trigger scenario.
3. **The complete private disposition ledger:** one row per candidate raised, with kind, disposition, decisive evidence pointer, and falsification reason — including every candidate dropped or acquitted. For each row, state whether a verifier ever ruled on it, and if not, which rule in your skill did or did not require that.
4. **Every sub-agent dispatch:** the exact prompt given and the verbatim report returned.
5. **Everything consulted beyond the diff:** every file, command, and search, quoted, with whether each search was repo-wide and case-insensitive; every focused test or repro command run, with its exit status, duration, and output summary.
6. **The `context` digest** and the inputs it was computed from (title, body, issue coordinates, `comments_available`, guidance list).
7. **Mechanism checklist**, each item with a pointer to where in the run it is demonstrated or "did not fire", plainly: question channel; clean-verdict or related-acquittal verification (which mode, which rows, any re-open); observations; fix-sufficiency check on any concurrency/invariant candidate; follow-up verifier round; deferral handling (any explicit deferral in the review record and how it was treated); retrospective mode; and — if your skill defines one — early dispatch of the verifier batch, with the exact moment it was dispatched relative to the falsification pass.
8. **History discipline:** whether you read any history beyond the pinned head, and the exact history commands you ran.
9. **Sandbox disclosure:** any path read outside the sandbox.
10. **Notes:** every judgment call on an ambiguity in the skill's contract; what you treated as guidance and why.

Do not truncate detail for brevity.
