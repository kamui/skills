# Frozen dispatch for one #138 cell

The exact prompts and launch shapes #150 and #151 use. Placeholders in `{BRACES}` are filled by the
runner from the cell's row in the sealed schedule and its slot manifest; every other byte is frozen.
A rendered prompt is hashed and retained with the attempt, and the assertion "no unfilled
placeholder" is a dispatch precondition.

Nothing here changes the policy under test. The primary reads the pinned skill snapshot and follows
it; these instructions carry the harness, the packet, the clone, the execution allowance and — in
arm C only — the barrier.

## Worker definitions supplied at startup

One JSON object, passed as `--agents`. The name is the same in every arm so that the transport is
identical and only the configuration differs; probe 1 and probe 5 established that a definition
supplied this way is what the child actually runs at.

Arm A (`agents-A.json`):

```json
{"bd-verifier": {"description": "Fresh-context verification worker for this review", "prompt": "You are a fresh-context verification worker. You have not seen this review before. Follow only the instructions in the task you are given, use the evidence it names, and answer in the form it asks for.", "model": "claude-sonnet-5", "effort": "high", "tools": ["Read", "Grep", "Glob", "Bash"]}}
```

Arms B and C (`agents-BC.json`) — byte-identical to A except the model:

```json
{"bd-verifier": {"description": "Fresh-context verification worker for this review", "prompt": "You are a fresh-context verification worker. You have not seen this review before. Follow only the instructions in the task you are given, use the evidence it names, and answer in the form it asks for.", "model": "claude-opus-5", "effort": "high", "tools": ["Read", "Grep", "Glob", "Bash"]}}
```

## Launch: the primary

```sh
CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 \
HTTPS_PROXY=http://127.0.0.1:{PROXY_PORT} HTTP_PROXY=http://127.0.0.1:{PROXY_PORT} \
ALL_PROXY=http://127.0.0.1:{PROXY_PORT} \
timeout {ROOT_WALL_REMAINING} claude -p --session-id "{PRIMARY_SID}" \
  --model claude-sonnet-5 --effort high --restricted \
  --tools "Bash,Read,Write,Edit,Glob,Grep,Agent,Task" \
  --allowedTools "Write" "Edit" \
                 "Bash(git:*)" "Bash(go:*)" "Bash(cargo:*)" "Bash(python3:*)" "Bash(cat:*)" \
                 "Bash(ls:*)" "Bash(head:*)" "Bash(tail:*)" "Bash(wc:*)" "Bash(sed:*)" "Bash(grep:*)" \
  --add-dir "{CLONE}" --add-dir "{SKILL_DIR}" --add-dir "{PACKET_DIR}" \
  --permission-prompts none --agents "$(cat {AGENTS_JSON})" \
  --max-budget-usd {REMAINING_ALLOWANCE} --output-format json "$(cat {DISPATCH})" < /dev/null
```

The working directory is `{WORK}`. `{ROOT_WALL_REMAINING}` is the whole attempt's wall allowance:
**5400 seconds counted once, from the root dispatch instant recorded in the timing sidecar** — not
per invocation. In arm C the same command runs twice, phase 1 as written and then
`--resume "{PRIMARY_SID}"` with `{ADMISSION}` as the prompt; before the resume the runner recomputes
`{ROOT_WALL_REMAINING}` as `5400 - (now - root_dispatched_at)` and reduces
`{REMAINING_ALLOWANCE}` by phase 1's settled cost. The barrier wait and the finder's own run fall
inside that window, so a C attempt gets the same 5400 seconds an A or B attempt gets, and an
exhausted allowance stops the attempt rather than starting a second full-length phase.

`Write` and `Edit` are named in `--allowedTools` because they have to be: under `--restricted` with
`--permission-prompts none` the write tools are denied outright unless the allow list names them,
even inside the permitted roots (probe 8), while naming them restores writes inside the roots and
still refuses one outside (probe 9). A shell command is admitted only when it matches an
allow-listed prefix, so the per-target execution note must use simple commands: a compound
`a && b && c` is refused even when each part would be allowed on its own.

## Launch: the finder (arm C only, concurrently with the primary's phase 1)

```sh
CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 \
HTTPS_PROXY=http://127.0.0.1:{PROXY_PORT} HTTP_PROXY=http://127.0.0.1:{PROXY_PORT} \
ALL_PROXY=http://127.0.0.1:{PROXY_PORT} \
timeout 1800 claude -p --session-id "{FINDER_SID}" \
  --model claude-opus-5 --effort high --restricted \
  --tools "Read,Grep,Glob" --add-dir "{CLONE}" --add-dir "{FINDER_STORE}" \
  --permission-prompts none --max-budget-usd 2.00 --output-format json \
  "$(cat {FINDER_PROMPT})" < /dev/null
```

The finder's working directory is `{FINDER_STORE}`, which the primary cannot read and which the
finder cannot leave. It has no shell, no sub-agent tool and no network tool — and no write tool
either, which is why it does not write its own artifact.

**The coordinator captures the finder's output.** Probes 8 and 9 established that a session cannot
write a file unless `--allowedTools` names `Write`, and the finder is deliberately kept read-only:
giving it `Write` would also let it write into `{CLONE}`, which `--add-dir` puts inside its permitted
roots and which no worker may dirty. So the finder returns its discovery JSON as the last thing it
says, the runtime saves that verbatim in the result envelope, and the coordinator — not the finder —
persists it:

1. read `.result` from the finder's `--output-format json` envelope;
2. parse the single fenced ```json block out of it;
3. check the required keys (`context_id`, `packet_sha256`, `scope_id`, `claims`, `inspected`,
   `frontier_expansions`, `unavailable`), that `claims` is a list, and that every claim carries
   `id`, `kind`, `claim`, `trigger`, `impact` and `citations`;
4. write it to `{FINDER_STORE}/discovery.json`, hash it, and record that hash as the finder's
   freeze artifact;
5. a missing envelope, a missing or unparsable block, or a failed key check is a **missing or
   malformed finder**, which the design's transition table already covers: cancel the remaining
   work, preserve the partial stores, close the attempt as an operational failure, and never
   substitute arm B's shape for it or infer a clean result from it.

Only after step 4 succeeds does the coordinator release the claims to the primary.

---

## Primary dispatch prompt

````markdown
You are executing one cell of a controlled research evaluation of a code-review skill against a real,
pinned, merged pull request. This is NOT a live review: no network access, no publishing, no
repository mutation. You produce a review payload and a detailed research report; a researcher scores
them afterwards. Nothing you write is posted anywhere.

## Cell identity

- Target: **{TARGET_SLOT}** — `{REPO_PR}`
- Cell: `{CELL}`, attempt `{ATTEMPT}` (an independent replicate; nothing is shared with other
  replicates except the packet and the mirror)
- Model: `claude-sonnet-5` for you. **Every fresh-context worker your skill calls for is dispatched
  with the `Agent` tool using `subagent_type: "bd-verifier"`, `model: "{WORKER_MODEL}"` and
  `run_in_background: false`.** That agent is defined for this session and already runs at the
  configuration this cell requires; pass the model explicitly anyway so the record is unambiguous.
- Your packet's run-conditions section says to pass `model: "<the model your dispatch names for that
  worker>"`. **That line means `{WORKER_MODEL}`**: the packet is byte-identical in every arm of this
  experiment, so the dispatch names the worker model instead of the packet.

**You are the reviewer for this cell.** Do the review yourself, in this context, following the skill
snapshot. Never delegate the review, the reading of this dispatch, or the writing of the report to
another agent; the only sub-agents you may spawn are the ones your skill's own process calls for.

## Files

- Skill snapshot: `{SKILL_DIR}/` — read `SKILL.md` first, in full, then the references it names, from
  this directory only; ignore any other installed copy of a review skill. Run its scripts from this
  directory (`python3 {SKILL_DIR}/scripts/<name>.py`).
- Phase-1 packet: `{PACKET}` — the "pin the review" step already done for you. Use its pinned values
  verbatim; do not re-resolve anything.
- Clone: `{CLONE}` — offline; local branch `{BASE_BRANCH}` is pinned to the merge-base, local branch
  `review-head` is checked out at the head. Use `git diff {BASE_BRANCH} review-head` for the change
  and `git show {BASE_BRANCH}:<path>` for base versions. History is truncated at the head.
- Your working directory for payload JSON, scratch files, your private store and script output:
  `{WORK}/` (it exists). Never write inside the clone.
- **Review payload:** write it to `{PAYLOAD}` — the review exactly as it would be published: summary
  body (with the `Mode` line for a merged target), every finding, question and observation comment
  with its trailer, and nothing else.
- **Research report:** write it to `{REPORT}` — everything listed under "What to report" below. Link
  to the payload file from the report instead of pasting it.
- **Timing sidecar:** `{TIMING}` already exists. Immediately after `validate_review.py` exits 0 on
  your final payload, run `python3 {RUNNER}/mark_event.py {TIMING} payload_validated_at`; if you
  change the payload and validate again later, run it again after that validation. Do not edit the
  file by hand and do not write any other event.

## Rules for this cell

1. Follow your skill as written: its phase order, its read discipline, its verification triggers, its
   output contract. Do not borrow behavior from any other review skill, and do not supplement it with
   review practices it does not itself specify.
2. This is a **retrospective review of a merged pull request by a third party** (posting identity
   `kamui`, not the author); publication is disabled. Derive the status as for an open pull request,
   event `COMMENT`, and include the `Mode` line your contract requires. Where a step says "publish",
   render instead and stop.
3. Compute the `context` digest **once**, as your contract specifies; do not run the skill's
   self-tests inside this cell.
4. Clone hygiene: do not run `git checkout`, `git switch`, `git reset`, `git stash`, or any command
   that mutates the tree, and instruct every sub-agent the same. If a tree is mutated anyway, run
   `git -C {CLONE} reset --hard review-head` and disclose it.
5. **Execution allowance for this target.** {EXEC_NOTE}
6. **Persist before you verify.** Write the report file in stages: the manifest and requirement
   ledger when they are complete; the complete candidate ledger with every disposition before
   dispatching any verifier; each verifier prompt and its verbatim report as they arrive. Update the
   file as you go. Where your skill prescribes when the private record is written, that prescription
   governs the review; this rule governs only the research report file.
7. **Stay inside your sandbox: the clone, the skill snapshot, the packet directory and your work,
   payload, report and timing paths.** Do not read any other path, by any means — not with a file
   tool, not through a shell command, not through an interpreter. Do not make any network request.
   Both boundaries are checked against your transcript after this cell stops, and a read or a request
   outside them invalidates this attempt.
8. Sub-agents you spawn get the same rules 1–7 in their prompt, plus rule 9 below,
   `model: "{WORKER_MODEL}"`, and `subagent_type: "bd-verifier"`.
9. No session relays: finish in this dispatch. Do not stop to ask anyone anything; if an input is
   genuinely missing, apply your skill's incomplete-coverage rule and say so in the report.
10. **Dispatch every sub-agent in the foreground** (`run_in_background: false`) and wait for its
    result before continuing. Never end your turn while a sub-agent of yours is still running, and
    never end your turn before the report and payload files are complete. This is a deliberate
    constraint, not a runtime limit: probe 10 showed background dispatch works in this exact
    configuration. It is frozen foreground because #137 lost a session to a background-wait
    termination on this runtime family, because it is identical in all three arms and so cannot bias
    the comparison, and because it leaves token cost — which is a gate — untouched. What it does
    change is elapsed time, and the preregistration records that as an interpretation limit.

{ARM_C_BARRIER_BLOCK}

## What to report (the report file; be exhaustive — it is the only record of this cell)

1. **Metadata:** target, cell, attempt; skill snapshot directory and the `workflow` identifier its
   validator reports; the model you ran on and the model each sub-agent ran on (state each
   explicitly); which verification trigger fired, if any, and quote the sentence in your skill that
   made it fire; sub-agents spawned (role, count, `subagent_type`); candidates raised, candidates
   surviving your own falsification; verifier verdicts; findings for publication with
   priority/action; questions; observations; coverage (every file and check inspected); derived
   status; your own token usage if the harness reports it, otherwise say it does not.
2. **Every finding that survives**, in full: priority/action, anchor, fix location, claim,
   verification status and evidence, trigger scenario.
3. **The complete private disposition ledger:** one row per candidate raised, with kind, disposition,
   decisive evidence pointer, and falsification reason — including every candidate dropped or
   acquitted. For each row, state whether a verifier ever ruled on it, and if not, which rule in your
   skill did or did not require that. For every acquitted high-risk row, state the safety premise you
   relied on, the scope you asserted it over, and the evidence you inspected for it.
4. **Every sub-agent dispatch:** the exact prompt given and the verbatim report returned.
5. **Everything consulted beyond the diff:** every file, command and search, quoted, with whether
   each search was repo-wide and case-insensitive; every focused test or repro command run, with its
   exit status, duration and output summary.
6. **The `context` digest** and the inputs it was computed from.
7. **Mechanism checklist**, each item with a pointer to where in the run it is demonstrated or "did
   not fire", plainly: question channel; clean-verdict or related-acquittal verification (which mode,
   which rows, any re-open); observations; fix-sufficiency check on any concurrency or invariant
   candidate; follow-up verifier round; deferral handling; retrospective mode; and early dispatch of
   the verifier batch, with the exact moment it was dispatched relative to the falsification pass.
8. **History discipline:** whether you read any history beyond the pinned head, and the exact history
   commands you ran.
9. **Sandbox disclosure:** any path read outside the sandbox, and any network request attempted.
10. **Notes:** every judgment call on an ambiguity in the skill's contract; what you treated as
    guidance and why.

Do not truncate detail for brevity.
````

### `{ARM_C_BARRIER_BLOCK}` — empty in arms A and B, this text in arm C

````markdown
## The discovery barrier (this cell only)

A separate worker is inspecting a bounded part of this change at the same time as you, from the same
packet and clone. You will receive its claims later. You cannot see it, its store or its output, and
it cannot see yours.

1. Work exactly as your skill prescribes until you have completed your inspection of the whole change
   and your own first falsification pass over every candidate it produced.
2. Then write `{FREEZE}` — a JSON object with `context_id`, `packet_sha256`, your complete candidate
   ledger with every disposition, and the SHA-256 of the report file as it stands — and stop your
   turn. Do not dispatch any verifier before this file exists. This is the only point in the cell
   where you stop early, and it is required.
3. You will be resumed with a compact list of the other worker's claims and citations. Falsify each
   one yourself against the diff and the clone, deduplicate the union semantically, and record for
   every canonical claim whether its origin is `primary`, `finder` or `both`, naming the source local
   IDs. Two workers finding the same thing is not confirmation of it.
4. Then continue your skill's normal process over the complete admitted union: apply its verification
   triggers to that union, send every ordinarily eligible candidate and every required related row to
   your verifier, and finish as your contract requires. The other worker's bounded scope never limits
   your own mandatory work, and its silence about a surface is not evidence that the surface is safe.
````

### `{ADMISSION}` — the resume prompt for arm C's phase 2

````markdown
The bounded discovery worker for this cell has finished and terminated. Its claims and citations
follow, verbatim and complete; you are receiving no other part of its context, and nothing about
whether it was right.

{FINDER_CLAIMS}

Resume at step 3 of the discovery barrier in your dispatch: falsify each claim yourself, deduplicate
the union, record origins, then continue your skill's normal process over the complete admitted
union. Finish the payload, the report and the timing event as your dispatch requires.
````

---

## Finder prompt (arm C only)

````markdown
You are a bounded independent discovery worker in a controlled research evaluation. You are not
reviewing this pull request and you are not verifying anyone's work. You inspect one selected part of
one change and report what you find, once, then stop.

## What you have

- Packet: `{PACKET}` — the pinned description of the change under inspection. Use its values verbatim.
- Clone: `{CLONE}` — offline; branch `{BASE_BRANCH}` is at the merge-base, `review-head` at the head.
- Selected scope: `{SCOPE}` — the roots and frontier you may read. This is the whole of your surface.
- Your working directory: `{FINDER_STORE}`. You have `Read`, `Grep` and `Glob` and nothing else: no
  shell, no tests, no sub-agents, no network, and no way to write a file. You do not need one — your
  report is the last thing you say, and the harness saves it.

## Your scope, and its edges

Read the scope's roots in full. From a root you may follow the frontier edges the scope names — a
caller, a callee or a contract, at most two hops from a root — where following one is needed to
establish that something triggers or to rule it out. Anything else is outside your bound: record what
you would have needed and mark it unavailable rather than guessing at it or wandering.

Reading everything you are allowed to read does not make the code safe. An empty search is an empty
search. Never write a sentence that turns the absence of a finding into a safety conclusion, for your
scope or for the change as a whole.

## What to report

End your turn with a single fenced ```json block and nothing after it. The block is one JSON object
with

- `context_id`, `packet_sha256`, `scope_id`,
- `claims`: a list, possibly empty, each with a local `id`, a `kind`, the `claim` in one or two
  sentences, the concrete `trigger` (the state or interleaving that makes it happen), the `impact`,
  and `citations` as `path:line` or `path:start-end` in the clone — raw citations only, no narrative
  support and no proposed fix;
- `inspected`: every range you actually read, as `path:start-end`;
- `frontier_expansions`: each edge you followed, with the root symbol it came from and why;
- `unavailable`: every piece of evidence you wanted and could not reach under this bound.

Report a complete object even when you found nothing; `claims: []` is a real result. A claim you are
unsure of belongs in the list with its uncertainty stated in the `claim` field — someone else will
falsify it, and that is their job, not yours.

Emit that block exactly once, as your final message, with no prose after it. It is the whole of your
output: nothing you say elsewhere is collected, and a missing or unparsable block ends this cell as a
failed discovery pass rather than an empty one.

Do not read outside the clone, the packet and your working directory. Do not make any network
request. Both are checked against your transcript after this session stops.
````
