You must do ALL of this work YOURSELF in this session. Do NOT use the Agent tool and do NOT dispatch any sub-agent: this harness terminates a headless session that waits on background workers. Work single-threaded. GitHub's search endpoints allow only 30 queries per minute; prefer `git log`, `git log -S` and `git show` on the local clone over API searches, and pace any `gh` call you do make.

You are an independent adjudicator establishing **ground truth** for one pull request that will be used as a target in a controlled evaluation of code-review strategies. You are not reviewing the pull request and you will never see any reviewer's output. Your job is to decide, from primary sources, what a correct review of this change would have to find, and what it must not assert.

Work on this machine. `gh`, `git`, `go`, `cargo` and the network are available. Write your register to `{OUT}` (create the directory if needed). Do not stop to ask questions; finish in this dispatch.

## Target

- Repository: `{REPO}` (base branch `{BASE_BRANCH}`)
- Pull request: `{PR}` — {TITLE}
- Head SHA: `{HEAD}`
- Merge-base: `{MERGE_BASE}`
- Merged: {MERGED_AT}
- A full staging clone with complete history is at `{STAGING}` (bare). Clone from it into a directory under `{SCRATCH}` and check out what you need; you may read anything, including everything that happened after the merge, and you may use the network for `gh`.
- Offline build material, if you want to run things: {EXEC_HINT}

## The hypothesis to adjudicate

A curator who knows the later history proposed the following. **Treat it as an unproven hypothesis, not as an answer.** Verify every part of it against primary sources yourself, and say plainly where it is wrong, overstated, or unsupported. Rule against it if the evidence does not hold; a wrong register in either direction corrupts every measurement built on it.

{CLAIM}

## What to establish

1. **Is there a material defect in this change?** A material defect is an actionable correctness, security, data-integrity, compatibility, meaningful-performance or explicit-requirement failure **with a demonstrated consequence** at the pinned head. Not a style preference, not a hygiene suggestion, not a hypothetical. A test that cannot fail for the reason it exists, or that fails intermittently by construction, is a material defect of the test.
2. For each material defect you confirm, give it a stable ID (`GT-{LETTER}1`, `GT-{LETTER}2`, …) and record:
   - the exact file, function and lines **at the pinned head**, and which diff hunk introduces it;
   - the expected behaviour and the violated rule, contract or test intent, quoted from where it actually lives (including untouched files);
   - the **trigger**: a concrete input, interleaving or state that reaches it;
   - the **demonstrated consequence**, with evidence: a downstream report, a revert, a follow-up fix, a regression test, or a reproduction you ran yourself;
   - the **required corrective outcome**: what any sufficient fix must restore, stated at the level of the outcome, not one specific patch, so that a differently-shaped but sufficient fix still counts;
   - the **category** it belongs to under these definitions, and whether it fits the category the hypothesis names: (C1) a defect in a concurrency, cancellation, wake-up, ordering, timeout, retry or liveness mechanism the diff touches; (C2) a failure to discharge an obligation stated outside the diff's own hunks; (C3) a test the diff adds or substantively changes that is materially wrong;
   - whether the defect **is the observable behaviour change the pull request itself promised** (report this separately), or an unintended error, or an insufficient implementation of a promised fix (say which).
3. **Reproduce what you can.** Run the relevant focused tests, race detector or type-check at the head and at the merge-base and report both, with commands, exit status and duration. If a failure exists at the merge-base too, say so: it is not introduced by this change. Keep every command under five minutes.
4. **Deduplicate.** Manifestations that share one underlying defect and one required corrective outcome are one defect, not several.
5. **If the change is clean**, say so explicitly, record `D_{LETTER} = 0`, and prove it: what you searched (`git log` over every changed path from the merge to today, issue and pull-request searches for the changed symbols, reverts), over what window, and what you found. Then record the **ground-truth surface a correct review must NOT assert as a defect**: the specific thing that looks wrong and is right, with the reason it is right.
6. **Not ground truth.** List the plausible objections a reviewer might raise that are **not** material defects, each with the reason. Be generous: this list keeps the scoring honest when a reviewer says something true-sounding.
7. **Preexisting hints.** The reviewers receive the pull request's review record up to the merge instant. Read that record and say whether any participant already gestured at the defect (or at the clean surface), quoting them.
8. **Leakage.** List every SHA a truncated mirror must exclude (merge commits, reverts, follow-up fixes, regression tests, later commits on the same code that reveal the answer) and every issue and pull-request number whose content would give the answer away. Include the merge commit of this pull request itself.
9. **Static visibility.** Say whether a careful reviewer reading the diff plus at most two caller/callee/contract hops could establish the defect (or the clean surface) without telemetry or long fuzzing, and why.

## Form

Write the register as Markdown with these sections, in this order: `Target`, `Verdict` (one line: `N material defects` or `adjudicated clean`), `Category fit` (one line per defect: fits the hypothesized category yes/no and which category it is; for a clean ruling, which supported surfaces the change has), `Defect register` (one subsection per defect ID, or "none"), `Reproduction`, `Not ground truth`, `Preexisting hints`, `Leakage`, `Static visibility`, `Adjudicator's confidence and limits`.

Cite evidence for every claim. Where you cannot settle something, say `unresolved` and explain what would settle it; do not guess. Delete nothing from the staging clone; work only under `{SCRATCH}`.
