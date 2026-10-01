You are a curator's research assistant vetting candidate pull requests for a controlled benchmark of AI code reviewers. You are finding **one target slot**, described under "The slot" below. Work on this machine: `gh`, `git` and the network are available. Do not stop to ask questions; finish in this dispatch.

Work **single-threaded**: do not start sub-agents or background tasks. GitHub's search API allows 30 requests a minute for the whole account and other hunts share it; pace searches, and on a rate-limit response wait for the reset rather than retrying at once.

## Where you write

- Your report: `{OUT}`. **Write it incrementally.** Create it at the start with the inventory table header, and append each candidate's row as soon as you finish checking it, so that an interrupted session still leaves a usable inventory.
- Clones and scratch work: under `{SCRATCH}` only.
- Never write anything inside the `kamui/skills` checkout at `{REPO_ROOT}`. You may read it and run its tools.

## The slot

{SHAPE}

## Eligibility, checked for every candidate you examine

- **E1 Unused.** The pull request is not listed in `{USED}` (one `owner/repo#number` per line, collected from every earlier grid). A different pull request in a listed repository is fine.
- **E2 Fresh and settled.** Prefer `mergedAt` on or after **2026-07-01**, after the reviewers' training data. Accept a merge from 2025-10-01 onward only when a real search found no qualifying preferred candidate, and say so. A buggy candidate's upstream confirmation must already exist today (2026-09-24). A clean candidate needs at least **eight weeks** between its merge and today, and that whole window is its cleanliness window.
- **E3 Size.** {SIZE}, counted from `git diff --numstat <merge-base> <head>` on a full clone.
- **E4 Packet-buildable.** This command must exit 0:
  `python3 {REPO_ROOT}/bench/tools/build_packet.py --repo <owner/repo> --pr <n> --head <head> --merge-base <merge-base> --base-sha <PR base SHA> --staging <your full clone> --target {LETTER} --out {SCRATCH}/packet-<n>.md`
  It refuses a thread, review or comment whose recorded edit postdates the cutoff (the merge instant by default). If it refuses only for that reason, record the refusal and try one earlier `--cutoff`: the latest instant that passes and drops comments only, never a review submission. Any other refusal fails E4. Do not quote the packet's contents in your report; only the exit status, cutoff and the omissions it prints.
- **E5 Trail readable through `gh`.** The review happened in GitHub-native reviews, threads and comments, not Reviewable, Gerrit or a mailing list.
- **E6 Safe reproducibility on this machine** (Linux x86_64, WSL2; node 24, Python 3.14 and `uv`, Go 1.26, Rust via `cargo` if installed; check with `command -v`). Either focused offline commands that take at most five minutes each after at most ten minutes of network provisioning, **measured by you**, or a static-only allowance with the reason. No credentials, services, browsers or destructive external effects. For a UI candidate, the defect must be settleable by reading code or by a focused unit or component test, never by looking at rendered output.
- **E7 Statically visible.** The defect (or, for a clean candidate, the tempting-but-false surface) can be reached by reading the diff plus at most two caller, callee or contract hops. Defects found only by telemetry, fuzzing, load or production incident reports are excluded.
- **E8 Unintended.** For a buggy candidate, the defect must not be the observable behaviour the pull request openly promised. It is an error the change made, not the contract it asked for.
- **E9 Independently confirmed.** Buggy: the upstream record identifies this defect and its mechanism: a fix, revert, regression test, security advisory or issue, written or accepted by a maintainer, with SHAs and dates. Clean: `git log` over every changed path from the merge to today, plus issue and pull-request searches for the changed symbols and the PR number, find no fix, revert or report attributable to the change.
- **E10 Public and permissive.** Public repository, OSI-approved licence, real maintainers.

**Organic evidence only.** Earlier hunts found recent issues and pull requests that were AI-generated reports ("Generated with Claude Code" and similar) with no maintainer confirmation behind them. Such an item is not a confirmation. A candidate needs a maintainer-written or maintainer-accepted fix, revert or advisory.

## What to report

1. **Inventory**, first: a table of every candidate you examined, **in the order examined**, with repository, PR, merge date, changed lines and files, and the result of each of E1–E10 (pass, fail with the reason, or not checked because an earlier criterion failed). Candidates you glanced at and dropped belong here too.
2. **Recommendation**: the first candidate in inventory order that passes E1–E10, and one alternate that also passes, if any exists. Then, for each of those two:
   - repository, PR number, title, author, merge instant, base branch and licence;
   - head SHA, PR-recorded base SHA, and the `git merge-base` **you computed on a full clone**, stating whether they agree;
   - the changed-file manifest with additions and deletions per file;
   - the originating issue, if any;
   - the prior review record up to the merge instant: reviews, threads and comments, who wrote them, and whether anyone raised the defect (buggy) or the tempting objection (clean), with quotes;
   - {EVIDENCE}
   - at least three **tempting false positives**, each with the reason it is wrong;
   - **leak set**: every SHA a truncated mirror must exclude (merge commit, later fixes, reverts, regression tests, PR branch heads after the reviewed head) and every issue or PR number whose content gives the answer away;
   - **provisioning and test evidence you actually ran**: the provisioning commands, then the focused commands, each with exit status, duration and an output summary, at the head and at the merge-base, and whether the tracked tree stayed clean;
   - the E4 command's exit status, cutoff and omissions;
   - confidence, with reasons.
3. If nothing meets the bar, say so plainly, and report the closest misses with the criterion each fails.

A candidate you have not verified with real commands is not a candidate. Be concrete and cite evidence for every claim.
