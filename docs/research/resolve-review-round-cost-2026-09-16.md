# Cost of a `resolve-review` round, and a plan to cut it

Measured on one real round: the addressing round on [#278](https://github.com/kamui/skills/pull/278),
run 2026-09-16 against review `5218500547`. The round started at
`56ce0bfe1368b0bd458dc79571a838074f2b226d`, landed four commits (`4bd33c3`, `0a6a2e8`, `9d38075`,
`bd187a8`), and the pull request merged as `37389f64a2833c5cc220931bafbad30c37319a8f`. That round is
the sample. The static figures below were re-measured in the merged tree, and where the round's
starting tree differs, both are given.

## Provenance

Two kinds of number appear here and they carry different weight.

- **From the live round, not re-derivable.** The tool-call count, the wall clock, the size the host
  reported for the overflowed opening read, the number of suite runs, and the step-3 reviewer's usage
  (`100,416` tokens, `421` s, `30` tool uses, as the host reported them). Nothing in this repository
  can reproduce them; they stand as reported, and the reviewer's token figure is whatever the host
  counts, cache reads included or not.
- **Re-measured at `37389f6`.** File and line sizes, fenced-block sizes, which tests read which
  files, per-file suite timings, and what the instructions actually say. Every figure in this class
  was re-derived for this record; where it disagreed with the first draft the corrected value is
  the one shown.
- **Unallocated remainder.** The wall clock left after subtracting the reviewer and the suite runs.
  The round did not record per-phase or per-call timings, so nothing in this record can say how that
  remainder splits between model reasoning, command generation, tool execution, and waits. It is
  reported as a total, never as a per-call cost, and no plan item is justified by dividing it.

## What the round delivered

Three findings (1 must-fix, 2 consider) and one review-body observation, on a markdown-only pull
request. The delivered diff was 8 files, +18/−11 lines, no code: prose edits to `README.md`, two
`DESIGN.md` files, three protocol or reference files, and two `SKILL.md` files. It took roughly 40
tool calls and about 35 minutes of wall clock.

## Measured cost

| Cost centre | Measured |
| --- | --- |
| Instructions read before the pull request was touched | 76,161 bytes — [`resolve-review/SKILL.md`](../../skills/resolve-review/SKILL.md) 14,581 + [`references/addressing-protocol.md`](../../skills/resolve-review/references/addressing-protocol.md) 55,223 (751 lines) + [`docs/agents/issue-tracker.md`](../agents/issue-tracker.md) 6,357; about 19k tokens at four bytes a token. At the round's starting head: 14,540 + 54,975 + 6,357 |
| Opening read that overflowed | The host reported a 59.2 KB combined read that exceeded its output limit, was persisted to a file, and cost 3 further reads to recover. Protocol plus tracker at the starting head is 61,332 bytes; the Bash tool on this host persists any output above roughly 30 KB, and persisted the 55 KB protocol on its own when re-measured, while the file-read tool returned all 751 lines in one call |
| Protocol code re-emitted verbatim into `/tmp` | The round reported 20.4 KB / 439 lines. The two block bodies it copied are 154 lines (collection) and 288 lines (thread-write loop), 20,489 bytes together |
| Script suite | 16 `test_*.py` files, ten under `review-code/scripts` and six under `audit-code-publish/scripts`; 98.0 s serial when re-run (the round measured 104.1 s). Run **3 times**: twice by the addresser, once by the step-3 reviewer |
| Step-3 reviewer subagent | 100,416 tokens / 421 s / 30 tool uses; returned no defects |

Per-file suite timings, serial and warm, re-run for this record with the round's figures in
parentheses: `test_thread_writes` 24.0 s (24.7), `test_compose_review` 21.4 s (23.2),
`test_command_chains` 18.0 s (19.5), `test_run_events` 7.9 s (8.4), `test_verifier_handoff` 5.6 s
(5.8), `test_review_context` 3.5 s (3.9), the remaining ten 0.6–2.6 s each. Two of the three slow
files, `test_thread_writes` and `test_command_chains`, run their documented blocks under every shell
present (`sh`, `bash`, `zsh`, `dash`) through subprocesses; `test_compose_review` drives its scripts
through `subprocess` against git fixtures. That is where the time goes.

Wall clock, as far as it can be allocated: 35 minutes is about 2,100 s. The reviewer's 421 s is a
fifth of it. The addresser's two suite runs are about 200 s. The remaining ~1,480 s is unallocated:
it spans about 38 tool calls, but the round has no phase timings, so it cannot be attributed to
those calls, to the model's reasoning between them, to tool execution, or to waits, and the first
draft's "roughly 40 s per tool call" was that division, not a measurement. Two consequences follow.
Nothing here can price a saved tool call, so removing calls is reported as a count, not as seconds.
And no decision that turns on the per-call cost, such as whether deferring part of the protocol
read pays for the extra call it costs, can be taken from this sample; item 4 collects the timings
that would decide it.

## Findings

### F1. The protocol ships executable code as prose, and the round re-typed it

`addressing-protocol.md` carries seven fenced blocks, 561 lines and 25,531 bytes with their fences:
two short `markdown` examples, a four-line `sh` example, and four `sh` programs. The four programs are the collection block
(154 body lines, 6.9 KB), the new-since-inventory command (16 lines, 0.7 KB), the check-runs reader
(74 lines, 3.3 KB), and the thread-write loop (288 lines, 13.6 KB, of which the embedded
`writes.py` is 254 lines). None is invocable by path. The round ran the two large ones by emitting
them from context into the tool call, 20.5 KB of output, and a transcription slip there lands on
forge writes.

The re-emission is not forced by the prose form. The reference is a file on disk at the installed
skill root, the same path the round had just read, and its blocks can be cut out of it
mechanically: `review-code/scripts/test_thread_writes.py` does exactly that, with a one-line regular
expression (`loop_block`, matching the `sh` fence that contains `write-loop.sh`), and
[`DESIGN.md`](../../skills/review-code/DESIGN.md) records that as the test's design. What the
protocol lacks is an instruction to run the block from the file rather than from memory.

The first draft of this record said the prose form contradicts [`docs/agents/scripts.md`](../agents/scripts.md).
It does not. That file governs code under a skill's `scripts/` directory, and it says a script's
"input arrives as arguments, stdin, or the local git repository; forge calls (`gh`) stay in
`SKILL.md` steps". Both large blocks are `gh` orchestration, so the convention as written keeps
them out of `scripts/`. Moving them there is a decision to amend that rule, not an application of
it.

Two tests are shaped by the prose form, but only one is an artifact of it. `test_thread_writes.py`
extracts the loop from markdown because there is nothing else to drive.
`test_both_references_carry_the_same_loop` is a drift guard between the two copies of the loop, in
`addressing-protocol.md` and `review-code-publish/references/publication.md`: it asserts that the
shared part, everything through the inner `SH` heredoc (13,535 bytes), is byte-identical, that the
addresser's copy carries no `run_events` wrapper, that the publisher's copy wraps its loop exactly
once with the timing event, and that the three rule paragraphs after the block appear in both files.
The two copies are deliberately not identical wholes: the publisher's tail acquires the app token
and wraps the loop in timing. That guard exists because [`AGENTS.md`](../../AGENTS.md) installs
skills one at a time, "so neither can point at the other's copy". Two script files would need the
same guard.

### F2. Everything loads up front; what is unreachable until step 4 is a third of it

Mapping the protocol's sections onto `SKILL.md`'s steps, at `37389f6`:

| Reached at | Lines | Bytes | Content |
| --- | --- | --- | --- |
| Step 1 | 1–320 (320) | 27,188 | Reading a finding, replies and dispositions, questions, thread state, verdicts and the round cap, the addressing summary, check evidence, humans, the verbs preamble, and the collection section with its 156-line block |
| Step 2, after commit | 344–426 (83) | 4,809 | Reading check runs |
| Step 4 | 427–751 (325) | 21,647 | Writing review activity and the thread write loop |
| Step 6 | 321–343 (23) | 1,579 | New since inventory |

The first draft put the collection block among the code "unreachable until step 4". It is the
opposite: `SKILL.md` step 1 runs it before any code is touched, and step 6 runs it again. The
content that cannot be used before step 4 is 325 lines and 21.6 KB, 43 percent of lines and 39
percent of bytes, and the decision sections a reader needs at step 1, lines 1–131, are 131 lines
and 15.2 KB, not the 200 lines first estimated.

Separately, `SKILL.md` line 10 instructs a combined read of the protocol and
`docs/agents/issue-tracker.md` "in one tool invocation when the complete output fits the host's
output limit", with a fallback to bounded or separate reads. On the sampled host the condition is
decidable before any call: the protocol alone is 55 KB, the Bash tool persists output above roughly
30 KB, and the file-read tool returns the whole protocol in one call, so a shell concatenation of the
two can never fit and a file read of each always does. There the instruction's only effect is to
invite the wrong tool for a saving of one call, and in this round it cost three. That is one host.
The instruction's fallback clause exists for hosts whose read tools are bounded or absent, and the
sample says nothing about those; what it shows is that the combined-read clause is a bad first
choice wherever a whole-file read exists, not that the fallback is unneeded.

### F3. Check selection was too broad, and the protocol already forbade it

The round changed no Python. Of the sixteen test files, three read the markdown it edited:
`test_thread_writes.py` (both protocol copies), `test_check_runs.py` (the addressing protocol, its
`code-review-publish` peer, and `resolve-review/SKILL.md`), and `test_command_chains.py` (the peer's
token block). Together they run in 44.6 s here (46.6 s in the round). None of the round's eighteen
changed lines fell inside a block those tests extract; their exposure to the edit is their prose
assertions, such as `test_check_runs.py`'s stale-wording guard and shared-vocabulary sites. All
sixteen were run instead, and run twice: once against the uncommitted tree and once at the committed
head with a byte-identical tree.

Both departures are from rules already in force. The protocol's **Selecting** rule (line 111) says a
documentation-only change needs a test invocation only where a documented check covers that
documentation. Its **Reusing** rule (line 116) says a run on uncommitted work counts for the commit
made from exactly that tree. `SKILL.md` step 2 orders the work as "commit the fixes locally" and
then verify, so a run before the commit was not asked for at all. The waste is about 100 s for the
redundant run and about 55 s of over-selection on the first, plus whatever share of the reviewer's
421 s its own full-suite run took.

### F4. The step-3 reviewer is the largest single cost, and part of it was duplicated work

100,416 tokens and 421 s to confirm three prose edits. `SKILL.md` step 3 requires the isolated
reviewer for every round, "also" for "rounds with no code changes", in at least two awaited phases:
an independent assessment sealed from the drafts, then the draft check. Those phases are the
design. Their cost on this round is one observation, not a demonstrated floor: the 421 s includes a
full suite run of about 100 s that the design does not ask for, and the reviewer's 30 tool uses
were not timed by phase, so how much of the rest is the sealed assessment and how much is
avoidable is unknown.

The brief invited an independent re-run of the documented checks, and the reviewer paid for the
third full suite run. The protocol's **Invalidating** rule (line 122) says the step-3 reviewer
"does not substitute for" the addresser's verification. That places the obligation to verify on
the addresser; it does not take verification out of the reviewer's remit. A reviewer that receives
the round's check evidence and finds it complete, current for the head it checks, and sufficient
for the changes has no reason to run the suite again, and this brief gave it no evidence to judge
that from. A reviewer that finds the evidence missing, stale, or too narrow, or that suspects a
defect the evidence does not reach, runs the focused check that settles it. What the round paid
for was the first case treated as the second.

### F5. Output hygiene on inspection reads

This repository has long single-line paragraphs: at `37389f6`, twenty lines over 2 KB across the
skill and agent documents, eight of them over 5 KB in `skills/review-code/DESIGN.md`, the longest
(`DESIGN.md:397`) 8,537 characters. The two the round printed were `README.md:149` at 3,715
characters and `skills/review-code/DESIGN.md:19` at 3,725 characters at the starting head (3,961 at
the merged head; the round edited that file). Both were printed in full, more than once, across
separate `grep` and `sed` calls. `cut -c1-200` was applied on some calls and omitted on others; the
round estimated that inconsistency at roughly 15 KB of context.

### F6. Commit-grouping rework

The round committed, then ran `git reset` plus `git add -p` and recommitted, purely to move one hunk
under a better-fitting message. Four tool calls, identical final tree.

## Plan

Ordered by what each item changes. The first four change this repository; the last section names
what a document cannot fix.

### 1. Run the blocks from the reference file, not from context

Add to the protocol, beside each of the two large blocks, the command that cuts it out of the
reference and runs it. The blocks stay where they are, the tests keep extracting them, and the
two-copy guard is untouched. This removes the 20.5 KB of output per round and the transcription
risk with it. It does not remove the read: the block bodies are still part of the reference the
round loads once.

The launcher is an execution boundary, and its contract is fixed before it is written:

- **Selection.** It selects the `sh` fence that contains a marker string the caller names
  (`write-loop.sh` for the loop, `flatten.py` for the collection block), which is the match
  `test_thread_writes.py`, `test_check_runs.py`, and `test_command_chains.py` already use. It
  requires exactly one match. Zero matches or more than one is an error reported before anything
  runs, with exit `2`, naming the file, the marker, and the count.
- **Binding.** The block's placeholder line (`owner=<owner> repo=<repo> pr=<n> incomplete=0` at
  line 254, `d=<private-dir> pr=<pr>` at line 457) is bound from the launcher's own arguments.
  Argument text is never spliced into the block: the launcher rewrites each placeholder to a
  positional-parameter reference and passes the values as positional arguments to `sh`, so an
  argument containing a space, a quote, or a `$` reaches the block as one value. An unbound
  placeholder left in the selected block is an error before execution, exit `2`.
- **Execution.** It writes the bound block to a file in a private directory and runs it with
  `sh`, the interpreter the protocol names, with the caller's environment and working directory.
- **Exit status.** The block's exit status is the launcher's, unchanged: `0` and `1` from the
  collection block mean `complete` and `incomplete`; `0`, `1`, and `2` from the loop keep the
  meanings the protocol assigns them. The launcher's own failures use `2` and stay distinguishable
  by their message on stderr before any block output.

The tests are the precedent and the bar. The existing tests bind placeholders by string replacement
under `shlex.quote` and run the text with `sh -c`, which drives the block but not the launcher. The
launcher is a new behaviour those tests do not cover, so it gets its own tests that run the
documented invocation exactly as the protocol prints it: exactly-one-match enforcement on a file
with zero and with two marked fences, an argument with shell metacharacters arriving intact, an
unbound placeholder refused before execution, and each block exit status passed through. Then the
loop's existing failure cases in `test_thread_writes.py`, whose names list them (a failed reply
blocking its action, an ambiguous reply reconciled without reposting, an interrupted write
reconciled before retry, an unsettled reconciliation never retried, a changed body not covered by
an earlier confirmation, and the rest), run through the launcher as well as through the current
`sh -c` route, so that the launcher's route demonstrably produces the same results the direct one
does.

Where the launcher lives is a small decision. `docs/agents/scripts.md` lists "parses a fenced
block" as script work, and the launcher makes no forge call of its own, so a stdlib Python
`scripts/run_block.py` under `resolve-review` with a `test_run_block.py` sibling fits the
convention as written and needs only the `compatibility` frontmatter line. `review-code-publish`,
which already requires `review-code`, would call a copy shipped there by the absolute path in the
returned record. An inline `python3 -` heredoc in the protocol avoids the frontmatter line but
cannot be tested as the documented invocation without extracting it from prose, which is the
problem being fixed. Take the script.

The alternative is real scripts, `skills/resolve-review/scripts/collect_activity.py` and
`thread_writes.py`, with `review-code-publish` taking its own copies. It saves what item 1 does plus
the once-per-round read of about 20 KB, and it needs, in order: an amendment to `scripts.md`'s
"forge calls stay in `SKILL.md` steps" rule, a rewrite of the outer `sh` loops as Python against the seventeen tests in
`test_thread_writes.py` that hold the loop's failure cases, and a drift guard renamed rather than
deleted, because install-alone still forbids sharing. `review-code-publish` could instead call a
script shipped by `review-code`, which it already depends on, "using the absolute path named in the
returned record"; `resolve-review` has no such dependency and would keep a copy. That is a design
decision with a rule change in it. Take item 1 first; open the script variant only if the read cost
proves to matter after the output cost is gone.

Splitting the protocol by step, proposed in the first draft, stays open. A round reaches step 4, so
the bytes are read either way, and a split trades a deferred 21.6 KB for one or two more tool calls.
Whether that is a loss or a saving depends on what a tool call costs against what a 21.6 KB earlier
read costs, and neither is measured: the first draft rejected the split on the unallocated
remainder divided by the call count, which is not a measurement of anything. The phase timings
item 4 collects are what decide it. Until then the protocol stays whole.

### 2. Replace the combined-read clause with a portable read

Drop the invitation to read the protocol and the tracker "in one tool invocation when the complete
output fits the host's output limit". Replace it with an instruction that holds on any host: read
each file completely and on its own, with whichever tool returns whole files, and where every
available read is bounded, read in ranges that cover the file's stated size and recover any portion
a bounded read cut off before proceeding. State the sizes the reader is checking against, the
protocol's line count and byte size, so a truncated read is detectable rather than inferred.

The sampled host has a file-read tool that returned all 751 lines in one call, and there the
instruction reduces to two calls. That is not established for other hosts, and the current
clause's fallback, bounded or separate reads with recovery of missing portions and consecutive
reads where multi-read is unsupported, is the part that keeps the instruction correct where the
whole-file read does not exist. The change removes the combined-read condition, not the fallback.

### 3. Give the step-3 reviewer the check evidence, and leave the review's scope open

Edit `SKILL.md` step 3 so the brief hands the reviewer the round's check evidence in the protocol's
Reporting form: each check, the head and input state it establishes, and its coverage. Say what the
reviewer does with it: reuse evidence that meets the protocol's Reusing conditions for the head it
is checking rather than re-running the same check; run a focused check where the evidence is
missing, stale for that head, too narrow for the changes, or where it is investigating a suspected
defect the evidence does not reach; and name in its assessment which of those it did. That
discourages the redundant full-suite run without narrowing what the reviewer may verify. The
sealed phase ordering and the adversarial framing stay. This is an instruction change, not a
request for care: today's text leaves the brief's content to the addresser, and the addresser
invited the re-run.

The first draft went on to ask whether a round with no code changes needs the assessment phase at
all, on the grounds that there is "no diff between the heads" to assess. That conflated two
different rounds. A documentation-only round is not a no-diff round: this sample changed eight
Markdown files, two of them `SKILL.md` files whose text is what an agent executes, and a change to
an instruction file needs the same independent inspection a change to code does. A genuine no-diff
round, one whose final head is the starting head or whose trees are byte-identical, still has the
original concerns and the round's answers to them, and whether a decline or an answer is justified
is exactly the judgment the sealed phase exists to make before the drafts can shape it. So a
reduced path, if one is ever adopted, has two fixed properties. Its eligibility rule is explicit
and mechanical, decided by the diff between the recorded heads being empty and by nothing about the
files' extensions. And it keeps the independent assessment of the original concerns before the
reviewer sees the drafts; what it drops is only the inspection of a diff that does not exist. That
is a smaller saving than the first draft implied, and it is a design decision to be taken with the
failure that motivated the sealed ordering in view. This record does not take it, and it does not
belong in the first implementation pass.

### 4. Make the round's cost part of its report, by phase

`SKILL.md` step 6's report names the checks and the heads they establish. Add what they cost: each
check invocation with its duration and whether it was a reuse, the reviewer's reported usage, and
the tool-call count and wall clock where the host reports them. Then add the split this record
could not make: wall clock and tool-call count per step, from the opening read through inventory,
addressing, checks, the reviewer's phases, the writes, and closeout, taken from timestamps the
round records as it goes. `review-code` already records run timing through `run_events.py`;
`resolve-review` cannot call it under install-alone, and a `date` line per step boundary into the
collection directory is enough for a report.

This is what makes the behavioural items enforceable, and it is what turns the unallocated
remainder into evidence. A round that ran the suite three times says so in its own summary. And
after a few rounds the per-phase figures say what a tool call costs and what the opening read
costs, which is what the split question in item 1 and the reduced-path question in item 3 need
before either is decided.

### 5. Consider a parallel suite runner

The serial suite is 98 s and its three slowest files are independent. Repo tooling under
`scripts/`, POSIX `sh` as `scripts.md` requires, that runs the sixteen files in parallel and reports
each file's exit would bound a full run below by the slowest file, about 24 s, for every caller: the
addresser, the reviewer, and CI. Treat 24 s as the optimistic figure. Two of the three slow files each
fan out into four shells' worth of subprocesses, the third builds git fixtures, and the measured
per-file timings are serial and warm;
what they do to each other under contention is unmeasured, and the real figure lies between 24 s
and the serial 98 s. This does not change what a round should select, but it shrinks the cost of
selecting badly. Optionally, the tests' docstrings already declare their inputs under an `Inputs:`
line; a selector that maps changed paths to those declarations would make the Selecting rule
mechanical for this repository.

### What a document cannot fix

Select checks from what the diff reaches, reuse an uncommitted-tree result for the identical
committed tree, bound reads in a repository with kilobyte lines, settle commit grouping before the
first `git add`. The first two are already rules in the protocol and in `SKILL.md` step 2, and the
round broke them anyway; the last two are ordinary care. Restating them here changes nothing. Item
4 is the durable form: a round that pays twice reports that it did.

## Expected effect

The savings below are separate scenarios against this round's figures. They overlap, so they are
not added: each states what it removes from the round as measured, and where one changes the base
another acts on, that is said.

- **Focused selection** (the protocol's Selecting rule, applied). A full-suite run of about 100 s
  becomes the three files that read the edited markdown, about 45 s. Saves about 55 s per suite
  invocation, and the round had two by the addresser.
- **Evidence reuse** (the Reusing rule, applied). The second addresser run, made at a
  byte-identical committed tree, is dropped. Saves one invocation: about 100 s at full scope, about
  45 s once selection is focused. With both rules applied the addresser's check cost is one focused
  run of about 45 s.
- **No reviewer duplication** (item 3). The reviewer's own full-suite run goes, when the evidence
  handed to it is complete and current for the head. Its share of the 421 s was not timed; a full
  run was about 100 s in the same environment, so that is the bound, not the measurement. The
  remainder of the reviewer's time is the sealed assessment and draft check, and this record cannot
  say what part of that is avoidable.
- **Parallel execution** (item 5). Acts on whatever run is left. On a full run, about 98 s down to
  no less than about 24 s. On the single focused run that the two rules above leave, about 45 s
  down to no less than 24 s, at most about 20 s saved, and less under contention. It cannot save
  70 s from a run that focused selection has already shortened.
- **Fewer tool calls.** Item 2 removes the three overflow-recovery calls on hosts with a whole-file
  read. Item 1 removes the emission of 20.5 KB of output, not a call. The four calls of commit
  rework are reported under item 4 but removed by nothing here; reporting rework is how the next
  round sees it, not how it disappears. None of these calls has a measured cost, so this line is a
  count, not a duration.

What cannot be projected. The sealed assessment and draft check are the round's design, and the
only claim this record makes about their cost is that it was not all design: the third suite run
was inside it. No projection beyond the per-scenario arithmetic is honest with one sample and no
phase timings; the next rounds, reported under item 4, are the measurement.

## Order of work

Implement item 1, the launcher with its tests, and the check-evidence hand-off in item 3 first.
Both change what the round does without changing what it protects, and both are testable or
checkable on the next round. Land item 2 with them. Then collect item 4's phase timings over the
following rounds. Item 1's split question, item 3's reduced path for genuine no-diff rounds, and
item 5's runner stay open until those timings say what a tool call, the opening read, and a
contended parallel run actually cost.

## What must not be traded away

The expensive mechanisms exist because of specific past failures: complete pagination, because
feedback on a later page silently missed the ledger; the write loop's reconciliation, because an
ambiguous reply was posted twice; the sealed phase-A ordering, because an assessment that has already
read the drafts is not independent evidence; the drift guard between the two loop copies, because
install-alone means neither copy can be the other's source of truth. The savings above come from not
paying for those guarantees twice in one round. None of them is a candidate for removal.
