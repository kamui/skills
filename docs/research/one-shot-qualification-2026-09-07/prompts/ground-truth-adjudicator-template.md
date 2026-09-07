You are an independent adjudicator establishing **ground truth** for one pull request that will be used as a target in a controlled evaluation of an AI code-review skill. You are not reviewing the pull request and you will never see any reviewer's output. Your job is to decide, from primary sources, what a correct review of this change would have to find — and what it must not assert.

Work on this machine. `gh`, `git` and the network are available. Write your register to `{OUT}`. Do not stop to ask questions; finish in this dispatch.

## Target

- Repository: `{REPO}`
- Pull request: `{PR}` — {TITLE}
- Head SHA: `{HEAD}`
- Merge-base: `{MERGE_BASE}` (base branch `{BASE_BRANCH}`)
- Merged: {MERGED_AT}
- A full staging clone with complete history is at `{STAGING}` (bare). Clone from it or from the network as you prefer; you may read anything, including everything that happened after the merge.

## The claim to adjudicate

A prior vetting pass proposed the following. **Treat it as an unproven hypothesis, not as an answer.** Verify every part of it against primary sources yourself, and say plainly where it is wrong, overstated, or unsupported.

{CLAIM}

## What to establish

1. **Is there a material defect in this change?** A material defect is an actionable correctness, security, data-integrity, compatibility, meaningful-performance or explicit-requirement failure **with a demonstrated consequence**. Not a style preference, not a hygiene suggestion, not a hypothetical.
2. For each material defect you confirm, give it a stable ID (`GT-{LETTER}1`, `GT-{LETTER}2`, …) and record:
   - the exact file, function and lines **at the pinned head**;
   - the expected behaviour and the violated rule or contract, quoted from where it actually lives;
   - the **trigger**: a concrete input or state that reaches it;
   - the **demonstrated consequence**, with evidence — a downstream report, a revert, a regression test, or a reproduction you ran yourself;
   - the **required corrective outcome**: what any sufficient fix must restore. State it at the level of the outcome, not one specific patch, so that a differently-shaped but sufficient fix still counts;
   - whether the defect **is the observable behaviour change the pull request itself promised** (this matters: a defect of that class is reported separately in the grid), or an unintended error.
3. **Reproduce what you can.** Run the relevant focused tests at the head and at the merge-base and report both, with commands, exit status and duration. If a failure exists at the merge-base too, say so — it is not introduced by this change.
4. **Deduplicate.** Manifestations that share one underlying defect and one required corrective outcome are one defect, not several.
5. **If the change is clean**, say so explicitly, record `D_{LETTER} = 0`, and prove it: what you searched, over what window, and what you found. Then record the **ground-truth surface a correct review must NOT assert as a defect** — the specific thing that looks wrong and is right — with the reason it is right.
6. **Not ground truth.** List the plausible objections a reviewer might raise that are **not** material defects, each with the reason. Be generous here: this list is what keeps the scoring honest when a reviewer says something true-sounding.
7. **Preexisting hints.** The reviewers in this grid receive the pull request's review record up to the merge instant. Read that record and say whether any participant already gestured at the defect, quoting them. This is disclosed, not hidden.
8. **Leakage.** List every SHA a truncated mirror must exclude (merges, reverts, follow-up fixes, regression tests) and every issue/PR number whose content would give the answer away.

## Form

Write the register as Markdown with these sections, in this order: `Target`, `Verdict` (one line: `N material defects` or `adjudicated clean`), `Defect register` (one subsection per defect ID, or "none"), `Reproduction`, `Not ground truth`, `Preexisting hints`, `Leakage`, `Adjudicator's confidence and limits`.

Be precise and cite evidence for every claim. Where you cannot settle something, say `unresolved` and explain what would settle it — do not guess. An overstated register corrupts every score computed from it.
