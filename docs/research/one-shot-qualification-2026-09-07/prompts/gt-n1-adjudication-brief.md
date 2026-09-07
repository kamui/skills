You must do ALL of this work YOURSELF in this session. Do NOT use the Agent tool and do NOT dispatch any sub-agent. Work single-threaded.

You are an independent adjudicator ruling on **one** disputed claim about a merged pull request. You are deliberately not told who raised it, how many reviewers raised it, what tool or configuration produced it, or what any other reviewer said. Do not try to find out, and do not let any guess about its source affect your ruling. Write your ruling to `/tmp/qual137/adjudication2/nc1-ruling.md`. Do not stop to ask questions; finish in this dispatch.

## The change under review

`BurntSushi/ripgrep#2957`, "feat(completion): support sourcing zsh completion dynamically", merged 2024-12-31.
Head `855bfa6cdae4f4fe8762f892fc4957635397083e`, merge-base `79cbe89deb1151e703f4d91b19af9cdcc128b765` (base branch `master`).
It changes exactly two files: `FAQ.md` (+20/−3) and `crates/core/flags/complete/rg.zsh` (+9/−1).

A clone with the reviewed head checked out as `review-head` and `master` pinned at the merge-base is at `/tmp/qual137/transport-check/n`. It is offline; read anything in it. `zsh` is installed on this machine and you may run it.

## The claim

> **`FAQ.md` line 135 ships a broken copy-paste snippet.** The pull request adds a block that the surrounding prose introduces as content to *add to your `$HOME/.zshrc` file*, but the line inside it reads `$ source <(rg --generate complete-zsh)` — with a leading `$ ` shell-prompt prefix. Pasted into `.zshrc` as instructed, zsh reports `command not found: $` at every shell startup and never runs `source`, so ripgrep's zsh completions are never loaded by the method this pull request exists to document.

## What to decide

Rule whether this is a **material defect** introduced by this pull request. A material defect is an actionable correctness, security, data-integrity, compatibility, meaningful-performance or **explicit-requirement** failure **with a demonstrated consequence**. A cosmetic or stylistic complaint is not one.

Work through, with evidence, and state each conclusion plainly:

1. **Is the text accurate?** Read `FAQ.md` at the head yourself. Quote the full surrounding passage — the prose that introduces the block, the block itself, and the neighbouring blocks. Does the prose in fact instruct the reader to put that line in `.zshrc`, or does it read as a terminal command to run once?
2. **What is the file's own convention?** Examine every other fenced block in `FAQ.md` at the head. Which carry a `$ ` prompt prefix and which do not, and does that split track "one-time terminal command" versus "content for a config file"? Give the counts and the line numbers. If the convention is inconsistent in the file itself, say so — that materially weakens the claim.
3. **Does it actually fail?** Run the reproduction yourself in `zsh` and paste the exact commands and output. Also check what happens on the merge-base version of the same passage, if one exists.
4. **Was the line introduced by this pull request**, or did it already exist at the merge-base? Show the diff.
5. **Consequence.** If a reader follows the instruction literally, what breaks, how visibly, and how easily would they notice and self-correct? Weigh honestly: a broken line that produces a loud error every shell startup is different from a silent failure, and both are different from a cosmetic nit.
6. **Counter-arguments.** Give the strongest case that this is *not* a material defect, and say why you do or do not accept it. Consider at least: that `$ ` is a widely understood prompt marker readers strip automatically; that the block may be intended as a terminal command; and that documentation-only issues may fall below the material bar.

## Your ruling

End with a section headed `## Ruling` containing exactly one of:

- `MATERIAL — <defect id GT-n1>` with the required corrective outcome any sufficient fix must achieve, the trigger, and the demonstrated consequence; or
- `NOT MATERIAL` with the reason, and whether it is nonetheless a true-but-sub-threshold fact or an outright false claim; or
- `UNRESOLVED` with exactly what would settle it.

Be willing to rule either way. A wrong ruling in either direction corrupts a measurement, so decide on the evidence you gathered, not on how the claim is phrased.
