# Scorecard — target `n` (`BurntSushi/ripgrep#2957`)

Ground truth: **`D_n = 0`** — the register lists zero `GT-` defects and is adjudicated clean. No review can
"recover" anything from an empty register, so every published material-sounding finding below is either
(a) a true fact that doesn't clear the material bar, (b) a false finding contradicted by the source, or
(c) a genuine new candidate that must go to adjudication. I checked every finding against
`/tmp/qual137/transport-check/n` (source at `review-head`) and, where useful, against real zsh execution.

I noticed what might look like a reviewer/system identifier in one payload's internal text. I did not use it
to compare or identify reviewers, and I flag it only per the "ignore and say so" rule — see review 3 below.

---

## Review A — `blind-17e56c.md`

**1. Recovered defect IDs:** none (register is empty; nothing to recover).

**2. Missed defect IDs:** none (register is empty).

**3. Fix sufficiency:** N/A — no defects to recover, no findings published.

**4. Findings not in the register:** none published. The review's only substantive content is an
"Ambiguities" note explaining that it *considered* the FAQ.md:138 dangling-clause grammar issue (register's
"Not ground truth" item 7) and deliberately dropped it rather than publish it as an Observation, under a
stated (defensible) reading of its own rubric:
> "a documentation prose nit that failed only on meaningful impact (`FAQ.md:138`) was dropped rather than
> published as an observation."
This is a self-disclosed methodology choice, not a finding — nothing to classify as true/false/candidate.

**5. Action/severity errors:** none (no findings published, so nothing to mis-prioritize).

**6. Questions, observations, hygiene items:** 0 questions, 0 observations, 0 hygiene items published.

**7. Derived status:** "Approved (advisory) — clean review; no findings." Declares coverage **complete**
("Complete merge-base diff reviewed... traced both branches of the new `rg.zsh` conditional against base
and head with focused zsh scratch scripts... read `ci/test-complete`").

**8. False clean:** **No**, per the register (`D_n=0`, so "no findings" is the correct call against the
register). Quoted: *"Approved (advisory) — clean review; no findings."* — See the cross-review "New
candidates" section below for why this could be reopened if `NC-1` is later adjudicated material.

**9. Duplicates:** none (no findings).

---

## Review B — `blind-5f5255.md`

**1. Recovered defect IDs:** none (register is empty).

**2. Missed defect IDs:** none (register is empty).

**3. Fix sufficiency:** N/A.

**4. Findings not in the register:**

- Finding: *"Fix missing subject in the zsh dynamic-source caveat"* (`FAQ.md:138-139`):
  > "'Note though that while this approach is easier to setup, is generally slower than the previous
  > method, and will add more time to loading your shell prompt.' drops the subject before 'is generally
  > slower,' so the second clause reads as a sentence fragment."
  Checked against source — confirmed verbatim at `FAQ.md:138-139`. **Classification: true but not
  material.** This is exactly the register's "Not ground truth" item 7 ("purely cosmetic... doesn't change
  the accuracy or actionability of the guidance"). Correctly scored `[P3][consider]`, non-blocking, with
  "Closing this without action is a correct response" — well-calibrated, not an action error.

- Observation: *"The new zsh code blocks in FAQ.md are tagged with the `zsh` language for syntax
  highlighting while the adjacent bash, fish, and PowerShell blocks in the same section remain untagged."*
  Checked against source: confirmed — the bash/fish/PowerShell fences at `FAQ.md` are plain ` ``` `, the
  three zsh fences (generate, fpath, source) are all ` ```zsh `. **Classification: true but not material**
  (accurate, cosmetic, correctly filed under Observations rather than Findings).

**5. Action/severity errors:** none — the one finding's priority (P3/consider/non-blocking) matches its
actual (cosmetic) severity.

**6. Questions, observations, hygiene items:** 0 questions; 1 observation (language-tag consistency,
answerable from the material at hand, true, would not change the review's verdict); 0 separate hygiene
items (the grammar item is filed as a Finding, not a hygiene note).

**7. Derived status:** "Approved (advisory) — 0 must-fix findings, 1 consider finding." Declares coverage
**complete** in the trailer, but the prose itself discloses a real gap: *"the full `ci/test-complete`
script could not run because it also diffs against `rg --help`, which requires a built `rg` binary that
this run's execution allowance excludes."* This is an honest disclosure of incompleteness sitting inside a
nominally "complete" coverage line — worth noting but not a false-clean issue since no material defect was
missed as a result (register is empty, and the untested half of `ci/test-complete` is orthogonal to the
`rg.zsh` guard logic the review otherwise verified directly).

**8. False clean:** **No.** The review does not assert "no material defects" in that language; it reports
one (non-material) consider finding and approves, consistent with `D_n=0`.

**9. Duplicates:** none.

---

## Review C — `blind-6a3b3a.md`

**1. Recovered defect IDs:** none from the register (register is empty). However, this review is the only
one to surface a specific, reproducible, previously-undiscussed claim — see `NC-1` below, which I could not
refute and which I am escalating as a new candidate rather than folding into "true but not material."

**2. Missed defect IDs:** none (register is empty).

**3. Fix sufficiency:** N/A for the (empty) register. For `NC-1` (see below), the proposed fix is
**sufficient**: it restores exact parity with the file's own established convention.

**4. Findings not in the register:**

- **`NC-1`** — Finding: *"Fix broken copy-paste `source` snippet in zsh FAQ"* (`FAQ.md:135`):
  > "The pasted line still starts with `$ `, so zsh reports `command not found: $` at every shell startup
  > and never runs `source`; ripgrep's zsh completions are never loaded via this documented method."
  I reproduced this directly. Source at `FAQ.md:131-136`:
  ```
  Or if you'd prefer to load and generate completions at the same time, you can
  add the following to your `$HOME/.zshrc` file:

  ```zsh
  $ source <(rg --generate complete-zsh)
  ```
  ```
  This is explicitly framed as *file content to add to `.zshrc`* — the same framing as the immediately
  preceding block (`FAQ.md:124-129`, "add `$HOME/.zsh-complete` to your `fpath`... `fpath=($HOME/.zsh-complete
  $fpath)`"), which correctly has **no** `$ ` prompt prefix. Every other "add this to your config/profile
  file" block in this same document (the `fpath` block; the PowerShell profile block at `FAQ.md:341-351`;
  the `alias` bullet near `FAQ.md:780`) omits the prompt prefix; only one-time terminal commands (bash/fish/
  zsh-generate blocks) carry `$ `. I ran the literal reproduction:
  ```
  $ printf '%s\n' '$ source <(echo "echo hi")' > /tmp/test_zshrc_snippet.zsh
  $ zsh -c 'source /tmp/test_zshrc_snippet.zsh'
  /tmp/test_zshrc_snippet.zsh:1: command not found: $
  ```
  confirming the exact failure the finding describes. I also checked the review-thread record in the packet:
  `vegerot`'s own FAQ-wording suggestion (packet §6, thread 10) shows the line **without** the `$ ` prefix
  (`> source <(rg --generate=complete-zsh)`), consistent with the prefix being an unintentional artifact of
  copying the PR-body/commit-message form (which *is* legitimately `$`-prefixed, since there it's a one-time
  terminal command) into the FAQ's "add to your `.zshrc`" context.
  **Classification: new candidate, not a false finding** — I could not refute it; the claimed mechanism,
  trigger, and consequence all check out against the source and against live zsh behavior. The register
  does not discuss this claim anywhere in its "Not ground truth" section (which is otherwise thorough about
  every other plausible objection on this target), so it is unsettled by the register itself. I flag this to
  the adjudication step with **medium-high confidence it is a real, demonstrated documentation defect**;
  what's unresolved is only whether "breaks on literal copy-paste of a doc snippet" clears this program's
  material bar the way a code/runtime defect would. What would further settle it: whether any later
  (post-truncation) master commit touched this exact FAQ line — the packet's history is deliberately
  truncated at the reviewed head, so I could not check.

- Finding: *"Document that `compinit` must run before the one-line `source` method works"* (`FAQ.md:131-136`):
  > "zsh instead fails with `command not found: _arguments`, and ripgrep's completions never load, with no
  > hint in the FAQ that ordering relative to `compinit` matters."
  I reproduced this too — fresh zsh, no rc files, no `compinit`, sourcing the real head file directly
  produces exactly `_rg:341: command not found: _arguments`. **But** this precondition is **pre-existing**,
  not introduced by this PR: the old unconditional `_rg "$@"` call has the identical dependency on
  `compinit` having populated `_arguments`/`compdef`; the PR doesn't change whether `compinit` is required,
  only what happens once it has run. **Classification: true but not material** — a real, correctly-scoped
  documentation completeness gap (rightly filed `[P3][consider]`, non-blocking, "closing without action is
  correct"), not a regression the PR introduced.

- Finding: *"Fix the malformed sentence in the new zsh slowness caveat"* (`FAQ.md:138-139`) — same text as
  Review B's finding, matches register item 7 exactly. **Classification: true but not material**, same
  reasoning as Review B; correctly scoped `[P3][consider]`.

- Observation: *"The new guard's leading comment describes only the `else` branch's skip-execution
  behavior, not the `if` branch that calls `_rg \"$@\"` two lines later."* Checked against source
  (`crates/core/flags/complete/rg.zsh:436-443`): the comment reads "Don't run the completion function when
  being sourced by itself," but the `if` branch (taken when `$funcstack[1] == _rg`, i.e. when the file *is*
  legitimately running as the dispatched completion widget, not "sourced by itself" in the problematic
  sense) does call `_rg "$@"`. The comment's phrasing indeed doesn't explain that branch. **Classification:
  true but not material** (accurate, filed correctly as an Observation, not a Finding).

**5. Action/severity errors:** The `compinit`-precondition and grammar findings are both correctly scored
`P3`/`consider`/non-blocking — no action errors there. For `NC-1` (`P2`/`must-fix`/`blocking=true`): I am
not treating this as an action error, because on my own reproduction the claimed consequence is real and
falls on exactly the population the PR's own author said this method was for (users who "may not want to
create directories, new files, and update their fpath" — i.e. the audience least likely to know to strip a
`$ ` prompt marker from something explicitly billed as ".zshrc content"). If the adjudication step later
rules `NC-1` sub-material, this priority would retroactively become an action error; as things stand I
can't make that call myself.

**6. Questions, observations, hygiene items:** 0 questions; 1 observation (guard-comment scope, true, would
not change the verdict on its own); 0 separate hygiene items.

**7. Derived status:** "Changes Requested (advisory) — 1 must-fix finding, 2 consider findings." Declares
coverage **complete** ("The `rg.zsh` guard was traced and reproduced with focused zsh execution across
three invocation paths... The new FAQ prose was compared against the file's own bash/fish/PowerShell sibling
conventions").

**8. False clean:** **No** — this is the one review that does *not* return a clean bill; it requests
changes.

**9. Duplicates:** none within this review (three distinct findings, one distinct observation).

*(Note on the payload's identity trailer: this payload's front matter uses a posting handle string; per
instructions I did not use it to infer or compare reviewer identity, and mention it only to disclose that I
saw and ignored it.)*

---

## Review D — `blind-96b2b1.md`

**1. Recovered defect IDs:** none (register is empty).

**2. Missed defect IDs:** none (register is empty).

**3. Fix sufficiency:** N/A.

**4. Findings not in the register:**

- Finding: *"Fix the dropped subject in the zsh completion caveat"* (`FAQ.md:138-139`):
  > "The caveat sentence has no subject for its second clause ('...is easier to setup, is generally
  > slower...'), so it reads as a broken run-on in otherwise carefully written documentation."
  Same nit as Reviews B and C, matches register item 7. **Classification: true but not material.** Correctly
  scored `[P3][consider]`, includes a concrete `suggestion` diff, "Closing this without action is a correct
  response" — well-calibrated.

**5. Action/severity errors:** none.

**6. Questions, observations, hygiene items:** 0 questions (explicitly "(none)"); 0 observations
(explicitly "(none — no accurate fact both failed admission only on meaningful/proven consequence and
cleared the Observations bar...)"). This review does *not* surface the language-tag consistency fact
(Review B) or the guard-comment-scope fact (Review C) at all — not wrong, just less coverage of the
low-stakes observation space, and it does not surface `NC-1` or the `compinit` precondition either.

**7. Derived status:** "Approved (advisory) — 0 must-fix findings, 1 consider finding." Declares coverage
**complete** ("`ci/test-complete`'s argument-extraction path (`get_comp_args`) exercised directly against
both the base and head completion scripts and confirmed byte-identical; no CI log was available offline to
reuse instead").

**8. False clean:** **No** — one (non-material) finding is reported; the review does not claim zero
findings, and matches `D_n=0` on the register.

**9. Duplicates:** none.

---

## Cross-review table

| Review | Recovered GT IDs | Recall R/D | Fix sufficiency | False findings (raw) | Action errors | Questions | Observations | False clean | Status |
|---|---|---|---|---|---|---|---|---|---|
| A (`17e56c`) | none | 0/0 | N/A | 0 | 0 | 0 | 0 | No | Approved, no findings, coverage complete |
| B (`5f5255`) | none | 0/0 | N/A | 0 | 0 | 0 | 1 | No | Approved, 1 consider, coverage complete (with disclosed partial-CI caveat) |
| C (`6a3b3a`) | none | 0/0 | N/A (GT); `NC-1` fix = sufficient | 0 | 0 (see caveat above on `NC-1`'s priority) | 0 | 1 | No | Changes Requested, 1 must-fix + 2 consider, coverage complete |
| D (`96b2b1`) | none | 0/0 | N/A | 0 | 0 | 0 | 0 | No | Approved, 1 consider, coverage complete |

`D_n = 0`, so R/D is vacuous (0/0) for every review — none had anything to recover, and none falsely claimed
a register defect existed. **Zero false findings** were found across all four reviews: every published
finding either matches the register's own explicitly-dismissed grammar nit (item 7, correctly kept at
non-material/consider severity by three of four reviews) or is the one new, independently-reproduced
candidate below. No review asserted any of the register's seven "Not ground truth" objections (1–6) as
defects — good calibration across the board on the harder, more tempting objections (the `funcstack`/
`compdef`/`no_unset` code-correctness questions).

## New candidates (consolidated)

**`NC-1` — `FAQ.md:135`, one-liner zsh snippet carries a literal `$ ` shell-prompt prefix inside a block
explicitly framed as ".zshrc content," breaking on verbatim copy-paste.**
- Raised by: Review C (`blind-6a3b3a.md`) only.
- Evidence checked: reproduced the exact failure (`command not found: $`) with a live zsh; confirmed the
  file's own internal convention (config-file-content blocks omit `$ `; one-time-terminal-command blocks
  carry it) is violated only by this one new block, immediately adjacent to a correctly-formatted block
  using the identical "add this to your `.zshrc`" framing; confirmed the PR-thread's own draft wording
  (packet §6, thread 10) lacked the `$ ` prefix, suggesting it was accidentally carried over from the
  commit-message/PR-body form (where it is legitimately a terminal-command example) rather than intended
  as literal file content.
- Ruling: **plausible, specific, and I could not refute it — genuine new candidate.** Confidence: medium-high
  that the mechanism and consequence are real (I reproduced both); lower confidence on whether "a doc
  snippet breaks on literal copy-paste, with an easy recognizable fix (strip `$ `) for anyone who's seen a
  shell prompt before" clears this program's bar for a *material* defect on a documentation-only PR, versus
  being the kind of thing the original register's author considered and folded into "not ground truth"
  implicitly (it did not appear in that section at all, so this is genuinely unsettled rather than
  contradicted).
- What would settle it: the register-owning adjudicator's explicit ruling on whether copy-paste-breaking doc
  formatting counts as "a correctness failure with a demonstrated consequence" for this program; secondarily,
  whether any subsequent (post-truncation) master commit patched this exact line, which would corroborate it
  being a real, later-acknowledged defect — not checkable from this offline, truncated clone.

No other new candidates surfaced. The `compinit`-precondition point (Review C) and the language-tag /
guard-comment observations (Reviews B and C) are all real facts I was able to fully settle as **true but not
material** (pre-existing precondition not introduced by this PR; purely cosmetic stylistic facts), so none
of those go forward as candidates.
