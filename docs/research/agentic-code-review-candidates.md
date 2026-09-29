# Agentic code-review skills and prompts: candidates for `legacy reviewer` to delegate to

**Researched 2026-08-31.** Every URL below was live on that date. Prompt text in vendored
artifacts drifts fast — Anthropic's bundled plugin prompts and the Claude Code binary in
particular are versioned with the product, and the quotes here are pinned to the versions
named in each section. Treat anything unpinned as liable to have moved.

## The question

the historical reviewer instructions (snapshot path omitted), step 2 delegates the actual reviewing:

> Honor a code-review skill the user names. Otherwise invoke the model-invoked review skill
> whose description best matches the change, passing it the fixed point, the spec source,
> and — re-reviewing — the earlier reviewed head.

On this machine that lands on Matt Pocock's `code-review`. Is there a better published
artifact to land on instead? "Better" = finds real defects, low false-positive rate,
findings anchorable to `file:line`, published rather than invented ad hoc, and — because
this runs unattended to post a review on a PR — never stops to ask a question.

## Method, and what "verified" means here

Three classes of source, and I keep them distinct throughout:

1. **Read directly, full text.** Files on this machine (`~/.claude/skills/`,
   `~/.claude/plugins/marketplaces/claude-plugins-official/`) and files fetched raw from
   public repos. Quotes from these are verbatim.
2. **Extracted from the Claude Code binary.** `/Users/jack/.local/share/claude/versions/2.1.252`
   (Mach-O arm64). Its prompt strings are UTF-16LE in the binary's string table; I decoded
   regions around known anchors. These quotes are verbatim but **reassembled** — the string
   table interleaves template fragments, so the surrounding prose is contiguous within each
   fragment but the fragments' order is my reconstruction. Where a fragment boundary matters
   I say so. This is a proprietary binary: readable, **not** vendorable.
3. **Relayed.** Search results, vendor benchmark pages, blog posts. Flagged inline.

I did **not** investigate Danger, ReviewDog, sweep, or Aider in depth. Danger and ReviewDog
are rule/linter-output plumbing rather than LLM reviewers, so they are the wrong category
for this question; I am excluding them on that basis without having read their sources, and
that is a gap rather than a finding.

## The incumbent, read carefully

`~/.claude/skills/code-review/SKILL.md` is **byte-identical** to upstream
[`mattpocock/skills` → `skills/engineering/code-review/SKILL.md`](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md)
(verified by `diff`; 87 lines). Repo is MIT, ~243k stars as of 2026-08-31 (`gh api repos/mattpocock/skills`).
Star count is a popularity signal only — I am judging it on the text.

Two things about it are commonly mis-stated, and both matter:

**Its interactivity is mostly not a live liability.** It has two "ask the user" branches:
step 1 ("If they didn't specify one, ask for it" — the fixed point) and step 2 ("If nothing
is found, ask the user where the spec is"). `legacy reviewer` step 1 supplies both:
it resolves the fixed point (merge-base by default) and the originating issue as spec
source before invoking anything. So under this caller, neither branch fires. There is a
third, harder stop that *can* fire — "If `docs/agents/issue-tracker.md` is missing, tell
the user to run `/setup-matt-pocock-skills`" — but that file exists in this repo
(`docs/agents/issue-tracker.md`). **Interactivity is not the reason to replace it.**

**Its real weakness is false-positive control, and that weakness is amplified by this
particular caller.** The Standards sub-agent brief, verbatim:

> "Report, per file/hunk where relevant, (a) every place the diff violates a documented
> standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name
> it and quote the hunk. Distinguish hard violations from judgement calls: documented-standard
> breaches can be hard, but baseline smells are always judgement calls, and a documented repo
> standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

That is the *entire* noise discipline: one "skip anything tooling enforces" clause and a
hard/judgement distinction. There is no confidence threshold, no verify pass, no "was this
introduced by the diff", no "would the author fix it", no exclusion list. And the baseline
it hands the sub-agent is a 12-item Fowler smell list — Mysterious Name, Speculative
Generality, Middle Man, Refused Bequest — which is a *design-taste* checklist. Handing a
taste checklist to an agent and asking it to find instances is close to the worst-case
prompt shape for precision: a sufficiently motivated reviewer can find "possible Feature
Envy" in almost any diff.

That would be tolerable in an interactive report. It is not tolerable here, because
`references/review-protocol.md` makes **blocking the default**:

> A finding is blocking unless it says otherwise. Unmarked means the change should not merge
> until this is settled, and that is what the author reads it as.

and `code-review-address` will dutifully act on each one. `legacy reviewer` step 2 already
knows this — "a fabricated finding costs a round and an agent will dutifully 'fix' it" — but
it is compensating downstream for a reviewer that does no filtering upstream.

**What it is genuinely best at:** the two-axis separation, and the *Spec* axis specifically.
The Spec sub-agent brief asks for (a) missing/partial requirements, (b) scope creep, (c)
requirements implemented wrongly, each with the spec line quoted. That is a real requirements
review, and it is rarer in published artifacts than you would expect — see below.

## Candidates

### 1. Anthropic's `code-review` plugin (`/code-review`, Boris Cherny) — the strongest FP machinery in a readable file

**Source, read in full:**
`~/.claude/plugins/marketplaces/claude-plugins-official/plugins/code-review/commands/code-review.md`
(Apache-2.0; `plugin.json` author Anthropic; README author "Boris Cherny (boris@anthropic.com)",
version 1.0.0). Same marketplace is public at
[`anthropics/claude-plugins`-style official marketplace](https://claude.com/plugins) — I read
the on-disk copy, which is what actually runs here.

This is a full unattended PR-review pipeline. Structure:

1. Haiku eligibility check (closed / draft / trivial / already reviewed → stop).
2. Haiku gathers governing `CLAUDE.md` paths.
3. Haiku summarizes the PR.
4. **Five parallel Sonnet finders** on different angles: CLAUDE.md compliance; shallow
   obvious-bug scan; git blame/history; comments on *previous* PRs touching these files;
   in-code comment guidance.
5. **One Haiku confidence scorer per finding**, given a verbatim 0–100 rubric.
6. **Filter < 80.** If nothing survives, do not post.
7. Re-run the eligibility check.
8. Post via `gh`.

The rubric is handed to the scorer verbatim, and it is unusually well-calibrated:

> a. 0: Not confident at all. This is a false positive that doesn't stand up to light
> scrutiny, or is a pre-existing issue. […] d. 75: Highly confident. The agent double checked
> the issue, and verified that it is very likely it is a real issue that will be hit in
> practice. The existing approach in the PR is insufficient. […]

And the exclusion taxonomy is the best short list of review noise I found anywhere:

> - Pre-existing issues
> - Something that looks like a bug but is not actually a bug
> - Pedantic nitpicks that a senior engineer wouldn't call out
> - Issues that a linter, typechecker, or compiler would catch […] No need to run these build
>   steps yourself -- it is safe to assume that they will be run separately as part of CI.
> - General code quality issues (eg. lack of test coverage, general security issues, poor
>   documentation), unless explicitly required in CLAUDE.md
> - Issues that are called out in CLAUDE.md, but explicitly silenced in the code […]
> - Changes in functionality that are likely intentional or are directly related to the broader change
> - Real issues, but on lines that the user did not modify in their pull request

Note the fourth bullet is a strictly stronger version of Pocock's "skip anything tooling
enforces", and the fifth actively *narrows* to documented rules — the opposite of a Fowler
taste baseline.

- **License:** Apache-2.0. Vendorable.
- **Interactivity:** none. Fully unattended by design.
- **Requirements axis:** **none.** Every angle is code-quality or convention. It never reads
  the originating issue. This is disqualifying as a whole-skill replacement.
- **Output shape:** a single markdown comment with numbered findings and permalink URLs
  (`https://github.com/owner/repo/blob/<full-sha>/path#L4-L7`). **It does not produce line
  comments** — it posts one `gh pr comment`. It has no severity field at all, and the format
  is prose, not structured. Heavy impedance mismatch with the publish protocol's
  "every finding that names code is a line comment on that code".
- **Runtime:** ~4 Haiku + 5 Sonnet + N Haiku calls. Expensive but the Haiku tiering keeps it
  reasonable.
- **Portability:** it is a slash command with `disable-model-invocation: false`, so it is
  model-invocable in principle, but it *owns* the posting step, which collides with
  `legacy reviewer` step 3.

**Verdict: not a drop-in, but the single best donor of false-positive discipline.**

### 2. Claude Code's built-in local `/code-review` — the most sophisticated reviewer here, and unusable as a dependency

**Source: extracted from the binary** (`2.1.252`), method described above. This is a
tiered prompt family: the runtime picks a variant by effort level, and there are
"tool unavailable" fallbacks for each.

The high-effort variant announces itself:

> `high effort — 3+5 angles — 6 candidates — 1-vote verify (recall-biased) — 10 findings`
>
> You are reviewing for **recall** at high effort: catch every real bug a careful reviewer
> would catch in one sitting. At this level, catching real bugs matters more than avoiding
> false positives. Err on the side of surfacing.

Phase 1 fans out to named angles. Verbatim:

> **### Angle A — line-by-line diff scan**
> Read every hunk in the diff, line by line. Then Read the enclosing function for each hunk —
> bugs in unchanged lines of a touched function are in scope (the PR re-exposes or fails to
> fix them). For every line ask: what input, state, timing, or platform makes this line wrong?
> […]
>
> **### Angle B — removed-behavior auditor**
> For every line the diff DELETES or replaces, name the invariant or behavior it enforced,
> then search the new code for where that invariant is re-established. If you can't find it,
> that's a candidate: a removed guard, a dropped error path, a narrowed validation, a deleted
> test that was covering a real case.
>
> **### Angle C — cross-file tracer** […] **### Angle D — language-pitfall specialist** […]
> **### Angle E — wrapper/proxy correctness** […]

plus cleanup angles — Reuse, Efficiency, Altitude, and a **Conventions (CLAUDE.md)** angle
whose discipline is exactly right for a Standards axis:

> Only flag a violation when you can quote the exact rule and the exact line that breaks it —
> no style preferences, no vague "spirit of the doc" inferences. In the finding, name the
> CLAUDE.md path and quote the rule so the report can cite it. If no CLAUDE.md applies,
> return nothing for this angle.

Phase 2 is a **three-state single-vote verifier** with an explicit anti-over-refutation bias
— the most interesting piece of prompt engineering I found in this whole survey:

> - **CONFIRMED** — can name the inputs/state that trigger it and the wrong output or crash.
>   Quote the line.
> - **PLAUSIBLE** — mechanism is real, trigger is uncertain (timing, env, config). State what
>   would confirm it.
> - **REFUTED** — factually wrong (code doesn't say that) or guarded elsewhere. Quote the line
>   that proves it.
>
> **PLAUSIBLE by default** — do not refute a candidate for being "speculative" or "depends on
> runtime state" when the state is realistic: concurrency races, nil/undefined on a
> rare-but-reachable path (error handler, cold cache, missing optional field), falsy-zero
> treated as missing, off-by-one on a boundary the code does not exclude, retry storms /
> partial failures, regex/allowlist that lost an anchor. These are PLAUSIBLE.
>
> **REFUTED** only when constructible from the code: factually wrong (quote the actual line);
> provably impossible (type/constant/invariant — show it); already handled in this diff (cite
> the guard); or pure style with no observable effect.

Phase 3 is a gap sweep by a fresh finder that has the verified list and is told to look
*only* for what is not already there. There is also an explicit instruction against finders
self-censoring:

> Pass every candidate with a nameable failure scenario through — finders that silently drop
> half-believed candidates bypass the verify step and are the dominant cause of misses.

**Output shape** is a structured tool call whose field descriptions I read verbatim from the
binary's tool schema: `file` ("Repo-relative path of the file the finding is in"), `line`
("1-indexed line the finding anchors to"), `summary` ("One-sentence statement of the defect"),
`short_summary` ("Compressed label for compact UI (≤60 chars): the claim alone, no rationale
or consequence clause"), `failure_scenario` ("Concrete inputs/state → wrong output/crash"),
`category` ("Short kebab-case slug of the finding type, e.g. \"correctness\", \"simplification\",
\"efficiency\", \"test-coverage\""), `verdict` ("Set when a verify pass ran"), `outcome`
("Set ONLY when re-reporting after applying fixes"). The top-level result is
"Verified findings, most-severe first; empty if none survived".

**There is no severity field.** I searched the schema region specifically for one; severity is
carried purely by ordering. For a caller that must decide blocking-vs-`[Suggestion]` per
finding, that is the worst impedance mismatch of any candidate here — ironically, given how
good the rest of it is.

- **License:** proprietary, compiled into the CLI. **Cannot be vendored.** Reading it to
  learn from is fine; copying it into this repo is not.
- **Requirements axis:** **none.** Not one angle reads an issue or spec.
- **Interactivity:** none.
- **Portability:** it is a built-in slash command, not a skill. `legacy reviewer` cannot
  `Skill(...)` it.

**Verdict: read it, steal from it, cannot depend on it.**

### 3. `/code-review ultra` (cloud multi-agent) — ruled out by construction

The binary is explicit that an agent may not launch it:

> If the user asks about "ultrareview" or how to run it, explain that /code-review ultra
> launches a multi-agent cloud review of the current branch (or /code-review ultra <PR#> for
> a GitHub PR); /ultrareview is a deprecated alias for the same command. **It is user-triggered
> and billed; you cannot launch it yourself, so do not attempt to via Bash or otherwise.**

Its prompts run server-side and are not on disk (I searched; only the client-side plumbing,
error strings, and the `--comment`/`--fix` flag handling are local). **Non-starter:**
un-invokable and unreadable.

### 4. Anthropic `/security-review` + `anthropics/claude-code-security-review` — the best-documented FP filter, wrong scope

Two copies of the same prompt, and I read both: the binary's (`2.1.252`) and the MIT-licensed
public one at
[`anthropics/claude-code-security-review/claudecode/prompts.py`](https://github.com/anthropics/claude-code-security-review/blob/main/claudecode/prompts.py)
(repo MIT, © 2025 Anthropic, ~6.1k stars). They agree on the substance.

Its noise machinery is the most explicit anywhere:

> 1. MINIMIZE FALSE POSITIVES: Only flag issues where you're >80% confident of actual exploitability
> 2. AVOID NOISE: Skip theoretical issues, style concerns, or low-impact findings

with a numbered **hard exclusion list** (17 items in the binary's filtering stage), a
per-finding confidence float with a stated floor ("Below 0.7: Don't report (too speculative)"),
and a three-step runtime that separates finding from filtering:

> 1. Use a sub-task to identify vulnerabilities. […] 2. Then for each vulnerability identified
> by the above sub-task, create a new sub-task to filter out false-positives. Launch these
> sub-tasks as parallel sub-tasks. […] 3. Filter out any vulnerabilities where the sub-task
> reported a confidence less than 8.

Output schema is exactly the shape `legacy reviewer` wants:
`{file, line, severity: HIGH|MEDIUM|LOW, category, description, exploit_scenario,
recommendation, confidence}`.

The repo also ships `findings_filter.py` with a `HardExclusionRules` class and a
`FindingsFilter`, and supports a `false-positive-filtering-instructions` input — i.e. the
filter is a first-class, tunable, testable component rather than a paragraph of prompt.

- **Requirements axis:** none, and by design.
- **Scope:** security only. The README (fetched) is unambiguous that it does not do general
  code review.
- **Measured claims:** none. I looked; the README quantifies nothing, and
  [Anthropic's launch post](https://claude.com/blog/automate-security-reviews-with-claude-code)
  (2025-08-06) claims only that the action "Applies customizable rules to filter out
  false-positives and known issues" and that it "has already caught security vulnerabilities
  in our own code". No rates.

**Verdict: not a candidate for the job, but the best template for how to *structure* an FP
filter — an exclusion list plus a separate parallel filtering pass plus a numeric floor.**

### 5. Anthropic `pr-review-toolkit` plugin — good specialist agents, weak orchestration

**Source, read in full:** `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/pr-review-toolkit/`
(Apache-2.0, author Anthropic). Six agents: `code-reviewer`, `silent-failure-hunter`,
`pr-test-analyzer`, `type-design-analyzer`, `comment-analyzer`, `code-simplifier`, plus a
`review-pr` command.

`code-reviewer.md` (model: opus) carries the same confidence discipline as the `code-review`
plugin, at agent scope:

> ## Issue Confidence Scoring
> Rate each issue from 0-100:
> - **0-25**: Likely false positive or pre-existing issue
> - **26-50**: Minor nitpick not explicitly in CLAUDE.md
> - **51-75**: Valid but low-impact issue
> - **76-90**: Important issue requiring attention
> - **91-100**: Critical bug or explicit CLAUDE.md violation
>
> **Only report issues with confidence ≥ 80**
>
> […] Be thorough but filter aggressively - quality over quantity.

and it groups output by severity ("Critical: 90-100, Important: 80-89") with file path and
line number per finding. That is directly mappable.

`silent-failure-hunter` is a genuinely good specialist — it is the only artifact in this
survey that systematically hunts dropped errors, and its brief is concrete ("List every type
of unexpected error that could be hidden by this catch block").

The orchestrating `review-pr` command is the weak part. It is prose workflow with no
confidence gate of its own, offers sequential-or-parallel as a user choice, and aggregates
into Critical/Important/Suggestions/Positive Observations — no dedup, no verify.

- **Requirements axis:** none.
- **Interactivity:** the agents are non-interactive; the command's "Parallel approach (user
  can request)" implies a user but does not block on one.
- **Verdict: `code-reviewer` and `silent-failure-hunter` are worth borrowing as extra angles.
  The command is not an upgrade on Pocock's orchestration.**

### 6. Anthropic `claude-security` plugin — right architecture, wrong job, and interactive

**Source, read:** `plugins/claude-security/skills/claude-security/SKILL.md` and `role.md`
(Apache-2.0). Its Researcher/Verifier split is stated better than anywhere else:

> **Scan Verifiers** have the important role of guarding humans' limited attention from false
> positives or findings of infinitesimal value. They review and critique the Researchers'
> proposed vulnerabilities and eliminate all that crumble under targeted scrutiny.
> Ultimately, humans have to understand and decide to fix the right vulnerabilities and if the
> results are noisy, humans would just give up or fail to notice important vulnerabilities to fix.

It is also the only artifact I read that explicitly designs for the unattended case:

> Users desire to leave the session unattended very soon after kicking off a scan, around a
> minute of wall-clock time. […] 2. Optimize for asking all questions in one batch as early as
> possible. 3. If it's likely been too long based on a date call and the user might be away,
> instead of using AskUserQuestion which would block permanently, ask something like "Can you
> answer a few questions? […]"

But: `disable-model-invocation: true`, it opens with an `AskUserQuestion` menu, it requires a
fixed start confirmation, and it is security-scoped. **Non-starter as a delegate; excellent
prose on why verification matters.**

### 7. OpenAI Codex review rubric — the strongest *readable, vendorable, drop-in-shaped* single artifact

**Source, read in full:**
[`openai/codex` → `codex-rs/prompts/templates/review/rubric.md`](https://github.com/openai/codex/blob/main/codex-rs/prompts/templates/review/rubric.md).
Repo is **Apache-2.0**. This is the actual rubric Codex's `/review` uses, not a demo.

Its flag/no-flag test is the best-stated one I found, and it encodes several of the
discriminations Pocock's baseline lacks:

> 1. It meaningfully impacts the accuracy, performance, security, or maintainability of the code.
> 2. The bug is discrete and actionable (i.e. not a general issue with the codebase or a
>    combination of multiple issues).
> 3. Fixing the bug does not demand a level of rigor that is not present in the rest of the
>    codebase […]
> 4. The bug was introduced in the commit (pre-existing bugs should not be flagged).
> 5. The author of the original PR would likely fix the issue if they were made aware of it.
> 6. The bug does not rely on unstated assumptions about the codebase or author's intent.
> 7. It is not enough to speculate that a change may disrupt another part of the codebase, to
>    be considered a bug, one must identify the other parts of the code that are provably affected.
> 8. The bug is clearly not just an intentional change by the original author.

Criterion 5 — "the author would likely fix it" — is the single most useful noise filter in
this whole survey, because it is the exact question a Fowler-smell reviewer never asks.
Criterion 7 kills the "this might break something elsewhere" class outright.

It also handles the "how many" question in a way that avoids both padding and premature stopping:

> Output all findings that the original author would fix if they knew about it. If there is no
> finding that a person would definitely love to see and fix, prefer outputting no findings.
> Do not stop at the first qualifying finding. Continue until you've listed every qualifying finding.

**Repository standards are covered**, generically, under "Repository Rule Attribution":

> Use the root and scoped project instruction files applicable to changed files, respecting
> normal project-document precedence (`AGENTS.override.md`, `AGENTS.md`, then configured
> fallback filenames). […] A finding is rule-supported only when applicable guidance materially
> contributes repository-specific scope, an invariant, remedy, convention, or confirmation
> behavior beyond generic correctness advice. […] Do not omit ordinary findings or invent
> findings solely because a rule file exists.

**Output shape is the best match to this repo's needs of anything I read:**

```json
{
  "findings": [
    { "title": "<≤ 80 chars, imperative>",
      "body": "<valid Markdown explaining *why* this is a problem; cite files/lines/functions>",
      "confidence_score": <float 0.0-1.0>,
      "priority": <int 0-3, optional>,
      "code_location": { "absolute_file_path": "<file path>",
                         "line_range": {"start": <int>, "end": <int>} } }
  ],
  "overall_correctness": "patch is correct" | "patch is incorrect",
  "overall_explanation": "<1-3 sentence explanation …>",
  "overall_confidence_score": <float 0.0-1.0>
}
```

with anchoring rules written for exactly this use case:

> * Line ranges must be as short as possible for interpreting the issue (avoid ranges over
>   5–10 lines; pick the most suitable subrange).
> * The code_location should overlap with the diff.

and a priority scale that maps cleanly onto the publish protocol's binary:

> [P0] – Drop everything to fix. Blocking release, operations, or major usage. Only use for
> universal issues that do not depend on any assumptions about the inputs. · [P1] – Urgent. […]
> · [P2] – Normal. To be fixed eventually · [P3] – Low. Nice to have.

Plus comment-writing rules that read like they were written against this repo's protocol
("The comment should be brief. The body should be at most 1 paragraph"; "should clearly and
explicitly communicate the scenarios, environments, or inputs that are necessary for the bug
to arise"; "avoid phrasing like 'Great job …', 'Thanks for …'").

**What it does not have:**

- **No requirements/spec axis.** `overall_correctness` is about whether the patch is
  self-consistently correct, not whether it implements the issue.
- **No fan-out or verify stage.** It is a single-pass rubric. The multi-agent machinery, if
  any, lives in Codex's Rust orchestration, not this file.

Separately, `openai/codex` ships repo-scoped review skills at `.codex/skills/code-review*/`
— but I read them and they are **specific to the Codex codebase** (rules about
`core/context`, `app-server` APIs, `test_codex`), plus an orchestrator that is three lines:
"Use subagents to review code using all code-review-* skills other than this orchestrator.
One subagent per skill." Not portable. The rubric is the artifact worth having.

- **License:** Apache-2.0. Vendorable with attribution.
- **Interactivity:** none. It is a pure rubric — no user-facing branches at all.
- **Portability:** it is a plain Markdown prompt with a `{{results}}`-free body. Nothing
  binds it to Codex except its placement.

**Verdict: the strongest single drop-in for the *Code* axis. It cannot cover Requirements.**

### 8. Qodo / CodiumAI `pr-agent` `/review` — the only mature published reviewer with a real requirements axis

**Source, read in full:**
[`pr_agent/settings/pr_reviewer_prompts.toml`](https://github.com/qodo-ai/pr-agent/blob/main/pr_agent/settings/pr_reviewer_prompts.toml)
(404 lines) and
[`pr_agent/settings/code_suggestions/pr_code_suggestions_reflect_prompts.toml`](https://github.com/qodo-ai/pr-agent/blob/main/pr_agent/settings/code_suggestions/pr_code_suggestions_reflect_prompts.toml).
Repo **MIT**, ~12.8k stars, now at `The-PR-Agent/pr-agent` (the `qodo-ai` paths still resolve).
Note `pr_code_suggestions_prompts.toml` moved into `code_suggestions/` — the old path 404s.

Its "what to flag" section is close in spirit to Codex's, with a nice asymmetry:

> - For clear bugs and security issues, be thorough. Do not skip a genuine problem just because
>   the trigger scenario is narrow.
> - For lower-severity concerns, be certain before flagging. If you cannot confidently explain
>   why something is a problem with a concrete scenario, do not flag it.
> - Each issue must be discrete and actionable, not a vague concern about the codebase in general.
> - Do not speculate that a change might break other code unless you can identify the specific
>   affected code path from the diff context.
> - Do not flag intentional design choices or stylistic preferences unless they introduce a clear defect.
> - When confidence is limited but the potential impact is high (e.g., data loss, security),
>   report it with an explicit note on what remains uncertain. Otherwise, prefer not reporting
>   over guessing.

**The requirements axis is real and structured.** With `related_tickets` populated:

```python
class TicketCompliance(BaseModel):
    ticket_url: str
    ticket_requirements: str = Field(description="Repeat, in your own words (in bullet points),
        all the requirements, sub-tasks, DoD, and acceptance criteria raised by the ticket")
    fully_compliant_requirements: str
    not_compliant_requirements: str
    requires_further_human_verification: str = Field(description="… items … that cannot be
        assessed through code review alone, are unclear, or need further human review …")
```

That fourth field is notable: it is a built-in **"raise a question rather than guess a finding"**
channel, which is exactly what `legacy reviewer` step 2 asks for and which Pocock's Spec
brief has no slot for.

It also emits merge-level judgments directly:

> `risk_level`: "Answer with exactly one of: low, medium, high. Use high only when the PR
> introduces a clear bug, security concern, or major logic risk. […]"
>
> `merge_recommendation`: "Answer with exactly one of: safe_to_merge, merge_with_caution,
> changes_required. […]"

and findings anchor properly: `KeyIssuesComponentLink{relevant_file, issue_header,
issue_content, start_line, end_line}`, capped at `num_max_findings`.

Its distinctive FP mechanism lives in the *suggestions* path rather than `/review`: a separate
**self-reflection scoring pass** that re-reads each suggestion against the diff and scores 0–10,
with a hard zero list:

> - Assign a score of 0 to suggestions aiming at: Adding docstring, type hints, or comments;
>   Remove unused imports or variables; Add missing import statements; Using more specific
>   exception types; Questions the definition, declaration, import, or initialization of any
>   entity in the PR code, that might be done in the outer codebase.

and calibration guards ("If the suggestion only asks the user to verify or ensure a change done
in the PR, it should not receive a score above 7").

**Weaknesses:**

- **Diff-only, hunk-formatted.** The prompt explicitly tells the model it is blind:
  "Note that you only see changed code segments (diff hunks in a PR), not the entire codebase.
  Avoid suggestions that might duplicate existing functionality…". That is a precision aid and
  a recall cost — it structurally cannot do Angle B/C-style cross-file tracing that the Claude
  Code built-in does.
- It is a Jinja-templated TOML inside a Python application, not a skill. Adapting it means
  lifting the prose and the Pydantic shape and re-hosting them, not calling it.
- `/review` output has no per-finding severity — severity lives at PR level (`risk_level`,
  `merge_recommendation`), and per-finding you get an `issue_header` string like "Possible Bug".

- **License:** MIT. Vendorable.
- **Interactivity:** none in the review path.

**Verdict: the best published *Requirements*-axis prompt, and the closest thing to a
two-axis published reviewer. Its Code axis is weaker than Codex's rubric.**

### 9. `obra/superpowers` `requesting-code-review` — two axes, zero noise control

**Source, read in full:**
[`skills/requesting-code-review/SKILL.md`](https://github.com/obra/superpowers/blob/main/skills/requesting-code-review/SKILL.md)
and its
[`code-reviewer.md`](https://github.com/obra/superpowers/blob/main/skills/requesting-code-review/code-reviewer.md)
template. MIT (© 2025 Jesse Vincent), ~280k stars.

It genuinely has both axes — "**Plan alignment:** Does the implementation match the plan /
requirements? Are deviations justified improvements, or problematic departures? Is all planned
functionality present?" alongside code quality, architecture, testing, production readiness —
and it produces the right *shape*: Critical / Important / Minor tiers, `File:line` per issue,
and an explicit `**Ready to merge?** [Yes | No | With fixes]` verdict. Severity maps to the
publish protocol almost directly (Critical+Important → blocking, Minor → `[Suggestion]`).

It is also usefully strict about scope hygiene — read-only on the checkout, and a hard
no-nested-subagents rule:

> Do all of this review yourself. Never spawn a subagent to review part of the diff, and never
> spawn another reviewer for a second opinion. This process already provides every review seat
> the work gets […]

But the noise discipline is one paragraph of vibes:

> Categorize issues by actual severity. Not everything is Critical. Acknowledge what was done
> well before listing issues — accurate praise helps the implementer trust the rest of the feedback.

No confidence threshold. No verify pass. No "was it introduced by this diff". No
"would the author fix it". And it *requires* a Strengths section, which is dead weight in a
posted PR review. Its checklist ("Proper error handling? Type safety where applicable? DRY
without premature abstraction?") is a taste checklist in the same family as Pocock's smells.

**Verdict: structurally the closest published two-axis artifact, and materially worse than
Pocock on the Code axis while being no better on noise. Not an upgrade.**

### 10. `anthropics/claude-code-action` — plumbing, not a reviewer

**Source, read:**
[`.claude/commands/review-pr.md`](https://github.com/anthropics/claude-code-action/blob/main/.claude/commands/review-pr.md)
and
[`examples/pr-review-comprehensive.yml`](https://github.com/anthropics/claude-code-action/blob/main/examples/pr-review-comprehensive.yml).

The command is eleven lines and delegates to five named subagents with one instruction:
"Instruct each to only provide noteworthy feedback. Once they finish, review the feedback and
post only the feedback that you also deem noteworthy." The example workflow's prompt is a
generic five-bucket checklist (Code Quality / Security / Performance / Testing / Documentation).

There is no rubric, no confidence gate, no output schema, no requirements axis. The repo's
value here is the **transport** — it documents
`mcp__github_inline_comment__create_inline_comment` as the line-comment mechanism, which is
worth knowing, and which the Claude Code binary's `--comment` path also targets. As a
*reviewer*, **non-starter**.

Notably, [`anthropics/skills`](https://github.com/anthropics/skills) contains **no**
code-review skill at all (I listed the tree: academy-guide, algorithmic-art, brand-guidelines,
canvas-design, claude-api, discernment-nudge, doc-coauthoring, docx, frontend-design,
internal-comms, mcp-builder, pdf, pptx, skill-creator, slack-gif-creator, theme-factory,
web-artifacts-builder, webapp-testing, xlsx). There is no official Anthropic *skill*-shaped
reviewer to adopt.

### 11. `coderabbitai/ai-pr-reviewer` — the open ancestor, and it is gone and obsolete

The upstream repo now **404s** for me (`gh api repos/coderabbitai/ai-pr-reviewer` → Not Found);
search results say it was archived 2025-12-18, so it appears to have been removed since. I read
its prompts from a fork:
[`avinashdvv/ai-pr-reviewer` → `src/prompts.ts`](https://github.com/avinashdvv/ai-pr-reviewer/blob/master/src/prompts.ts)
(MIT). **Caveat: a fork is not the upstream; I could not verify it against the original.**

The review prompt is 2023-vintage and would be a downgrade on every axis:

> - Do NOT provide general feedback, summaries, explanations of changes, or praises for making
>   good additions.
> - Focus solely on offering specific, objective insights based on the given context and refrain
>   from making broad comments about potential impacts on the system or question intentions
>   behind the changes.
>
> If there are no issues found on a line range, you MUST respond with the text `LGTM!` for that
> line range in the review section.

Per-file review, no severity, no confidence, no requirements axis, no cross-file context, and
the `LGTM!` protocol is pure token burn. **Non-starter.**

### 12. Closed-prompt hosted reviewers — CodeRabbit, Greptile, Cursor BugBot, Sourcery, Bito, Graphite

I looked for readable prompts for each and found none. These are hosted SaaS with proprietary
prompts; the only configuration surface is YAML (`.coderabbit.yaml`, file-path instruction
overrides). **A reviewer you cannot read is not a reviewer you can adopt**, and none of them is
callable as a skill from inside a Claude Code session anyway. They matter only as evidence
about what works (next section). Greptile is available as a Claude Code plugin on this machine
(`plugins/marketplaces/.../external_plugins/greptile`) — but that is an MCP connector to the
hosted service, not a prompt.

### 13. Community persona collections — judged by their text, and they fail

- [`wshobson/agents`](https://github.com/wshobson/agents) `plugins/comprehensive-review/agents/code-reviewer.md`
  (MIT, ~39k stars). Read it. It is a capability inventory, not a procedure: "Integration with
  modern AI review tools (Trag, Bito, Codiga, GitHub Copilot)", "SonarQube, CodeQL, and Semgrep
  for comprehensive code scanning". It tells the model what a code reviewer *knows about*, not
  what to do with a diff. No output schema, no severity, no confidence gate, no diff-scoping.
- [`VoltAgent/awesome-claude-code-subagents`](https://github.com/VoltAgent/awesome-claude-code-subagents)
  `categories/04-quality-security/code-reviewer.md` (MIT, ~24.8k stars). Worse: its checklist
  asserts outcomes the agent cannot observe — "Code coverage > 80% confirmed", "Cyclomatic
  complexity < 10 maintained", "Zero critical security issues verified" — which invites the
  model to *claim* them.

Both have large star counts. That is the only positive signal either has, and I am saying so
explicitly. **Non-starters.**

## What the evidence actually says about finding real bugs vs. producing noise

This is thinner than the tooling landscape suggests, and I want to be blunt about that.

**The one peer-reviewable multi-agent comparison I found.**
[*Code Review Agent Benchmark* (c-CRAB), arXiv 2603.23448](https://arxiv.org/abs/2603.23448)
(Zhang, Pan, Yusuf, Ruan, Shariffdeen, Roychoudhury; submitted 2026-03-24, revised 2026-04-07).
It builds tests from human PR reviews and checks whether an agent's review covers the same
issues. Pass rates, relayed from my fetch of the HTML version:

| Agent | c-CRAB pass rate |
| --- | --- |
| Claude Code | 32.1% |
| Devin Review | 24.8% |
| PR-Agent | 23.1% |
| Codex | 20.1% |
| *(union of all four)* | *41.5% (97/234)* |
| Human reviewers | 100% |

Two findings from it matter more than the ranking. First, **the union is barely above the best
single agent** — these tools miss the same things, so stacking reviewers buys less than you
would hope. Second, the paper's manual usefulness audit **inverts the ranking**: PR-Agent 94%
useful, Codex 88%, Devin 85%, Claude Code 78%, and the authors conclude that "the low pass
rates do not necessarily imply that the generated reviews are low quality and not useful.
Instead, they suggest that the reviews produced by automated tools are less aligned with the
types of issues that human reviewers typically raise." They also warn that agents
"tend to raise concerns related to robustness and testing more frequently than humans […]
the resulting false positives may also substantially increase the burden on maintainers."

**Read that against this repo's design.** A reviewer that is *useful but unaligned* is fine
when a human reads the output and files what they like. It is actively harmful when
`legacy reviewer` posts every finding as a blocking line comment and `code-review-address`
fixes them. The publish pipeline converts "unaligned but useful" into "unaligned and merged".
That is the strongest argument in this document for prioritising precision machinery over
recall machinery in step 2 — and it is an argument *against* adopting the Claude Code
built-in's recall-biased high-effort variant wholesale, notwithstanding how good its prompt is.

**Vendor benchmarks: treat as marketing.** [Greptile's benchmarks page](https://www.greptile.com/benchmarks)
(July 2025, 50 PRs, 5 repos) reports catch rates — Greptile 82%, Bugbot 58%, Copilot 54%,
CodeRabbit 44%, Graphite 6% — with a strict counting rule ("a bug counted as 'caught' only when
the tool explicitly identified the faulty code in a line-level comment and explained the
impact"). It is published by the vendor that wins, and it **publishes no false-positive data at
all**. Recall without precision is exactly the number a recall-maximising vendor would choose to
publish.

**Independent-ish FP numbers, with a disclosed conflict.** A 3.5-week head-to-head over 146
merged PRs / 679 findings —
[dev.to: "Best AI Code Reviewer in 2026?"](https://dev.to/_vjk/best-ai-code-reviewer-in-2026-we-ran-4-in-parallel-for-3-weeks-146-prs-679-findings-1c0f)
— reports FP rates of Greptile 0% (120 findings), CodeRabbit 2.3%, Cursor BugBot 4.8%, Sentry
Seer 15.0% at high severity. The author discloses working at Sentry. It is one codebase
(PHP/React), one author's adjudication, and a blog post, and its Greptile result contradicts
another figure in the same search results (11 FPs on a 50-PR corpus). **I would not act on any
of these numbers.** What the corpus is good for is the qualitative claim, also relayed rather
than verified, that BugBot "runs 8 parallel analysis passes with randomized diff order, then
uses majority voting plus a validator model", i.e. that the top commercial systems converge on
*fan-out plus an independent validator* — which is precisely the shape of Anthropic's
`/code-review` plugin and the built-in's Phase 2.

**Prompt-design evidence.** [Sphinx (arXiv 2601.04252)](https://arxiv.org/abs/2601.04252),
submitted 2026-01-06, trains against a **checklist-based** evaluation and reports up to 40%
better checklist coverage. That is recall-shaped evidence for grounding review in an explicit
rubric rather than open-ended "review this" — which supports the rubric-first designs (Codex,
pr-agent) over persona-first designs (wshobson, VoltAgent).

**What there is no good evidence for.** I found nothing that isolates the effect of a
confidence threshold, or of a separate verify pass, or of diff-only vs whole-repo context, on
false-positive rate in a controlled way. The `>80% confidence` / `filter <80` / `PLAUSIBLE by
default` patterns are converged-upon industry practice across four independent Anthropic
artifacts and Codex's `confidence_score`, and that convergence is meaningful — but it is
convergence, not measurement. **Anyone who tells you the 80 threshold is empirically
calibrated is guessing.**

## Comparison

Scored against what `legacy reviewer` actually needs.

| Candidate | Text readable? | License | Asks the user? | Anchoring | Per-finding severity | Requirements axis | FP control | Runtime | Callable as a skill? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Pocock `code-review`** (incumbent) | Yes, 87 lines | MIT | 2 branches, neither fires under this caller; 1 hard stop on missing `issue-tracker.md` | Prose "per file/hunk"; no schema | Hard violation vs judgement call | **Yes** — missing/partial/scope-creep/wrong, spec line quoted | "Skip what tooling enforces"; repo overrides baseline. Nothing else. | 2 parallel sub-agents, 400 words each | **Yes** — it is the wired-up default |
| **Anthropic `code-review` plugin** | Yes, full | Apache-2.0 | No | Permalink URLs w/ full SHA — **not line comments** | None | No | **Best**: 5 finders → per-finding Haiku scorer → filter <80 + 8-item FP taxonomy | ~4 Haiku + 5 Sonnet + N Haiku | Slash command; owns its own posting step |
| **Claude Code built-in `/code-review`** | Yes, by binary extraction | **Proprietary** | No | `file` + 1-indexed `line`, structured tool | **None** — ordering only | No | 3-state verify, PLAUSIBLE-by-default, gap sweep, dedup | 10 finders → verify → sweep (high effort) | **No** — built-in command, not a skill |
| **`/code-review ultra`** | **No** — server-side | Proprietary | No | ? | ? | ? | ? | Cloud multi-agent | **No** — "you cannot launch it yourself" |
| **`/security-review` / `claude-code-security-review`** | Yes, full | MIT | No | `file` + `line` | HIGH/MED/LOW + confidence float | No | **Best-structured**: 17 hard exclusions, parallel filter sub-tasks, confidence ≥8 gate | find → N parallel filters → threshold | Slash command / GH Action; security only |
| **`pr-review-toolkit` agents** | Yes, full | Apache-2.0 | No | file path + line number | Critical 90-100 / Important 80-89 | No | Per-agent 0-100 rubric, report only ≥80 | 1-6 agents, no verify pass | Agents; invocable, but no orchestrator worth using |
| **`claude-security`** | Yes, full | Apache-2.0 | **Yes** — opens with `AskUserQuestion` menu | SARIF-ish via scripts | Yes | No | Researcher/Verifier panel | Workflow + subagents | **No** — `disable-model-invocation: true` |
| **Codex `rubric.md`** | Yes, full | **Apache-2.0** | No | **`absolute_file_path` + short `line_range`, must overlap diff** | **P0–P3 + `confidence_score` float** | No | **8-criterion flag test incl. "introduced in the commit" and "author would fix it"** | Single pass | Plain Markdown — trivially portable |
| **`pr-agent` `/review`** | Yes, full | **MIT** | No | `relevant_file` + `start_line`/`end_line` | PR-level `risk_level` + `merge_recommendation`; per-finding only an `issue_header` string | **Yes — `TicketCompliance`, incl. a "needs human verification" channel** | Strong asymmetric flag rules; separate 0-10 reflect pass (suggestions path) | Single pass, diff-hunks only | Jinja/TOML in a Python app — adapt, don't call |
| **`superpowers` `requesting-code-review`** | Yes, full | MIT | No | `File:line` | **Critical / Important / Minor + merge verdict** | **Yes** — plan alignment | One paragraph of "categorize by actual severity" | Single subagent, explicitly no nesting | Yes, it is a skill |
| **`claude-code-action`** | Yes — 11 lines | MIT | No | inline-comment MCP tool | No | No | "only noteworthy feedback" | 5 subagents | GH Action |
| **`ai-pr-reviewer`** | Fork only; upstream 404s | MIT | No | line ranges in `new_hunk` | No | No | "Do NOT provide general feedback" | Per-file | GH Action |
| **CodeRabbit / Greptile / BugBot / Sourcery / Bito / Graphite** | **No** | Proprietary | n/a | Line comments | Yes | Varies | Unknown | Hosted | **No** |
| **wshobson / VoltAgent personas** | Yes | MIT | No | None specified | Vague | No | **None** | Single agent | Yes |

## Recommendation

### (a) Is there a strongest drop-in replacement?

**No. Nothing published beats what is already wired up, as a whole-skill swap** — and the
reason is narrow and specific: **no published artifact combines a real requirements axis with
serious false-positive machinery.**

The two families split cleanly. The precision leaders — Codex's rubric, Anthropic's
`code-review` plugin, the Claude Code built-in, `/security-review` — are **all code-only**.
Not one of them reads the originating issue. The requirements-capable artifacts — pr-agent's
`TicketCompliance`, superpowers' plan alignment, Pocock's Spec axis — all have weak-to-absent
noise control. `legacy reviewer` needs both axes and cannot get both from one place.

Pocock's skill also has two structural advantages this repo has already paid for. Its
axis separation is load-bearing: `references/review-protocol.md` builds `[Code]` / `[Requirements]`
tags, per-axis outcomes, per-axis counts, and the whole status ladder on top of it, and its
"Do **not** merge or rerank findings" instruction is what keeps the two axes independent
through publication. And the Spec brief already produces the three shapes the protocol wants
(missing/partial, scope creep, implemented-wrong) with the spec line quoted as evidence.

**Swapping it out would cost the Requirements axis to buy noise control. That is a bad trade
when the noise control can be bought separately.**

### (b) Does a hybrid beat any single existing artifact?

**Yes, clearly.** Keep the two-axis frame; graft in the precision machinery the frame lacks.
Three grafts, in descending order of value per unit of effort:

1. **Replace the Fowler smell baseline's role with Codex's 8-criterion flag test on the
   Standards/Code axis.** This is the highest-value single change in this document. Criteria 4
   ("The bug was introduced in the commit"), 5 ("The author of the original PR would likely fix
   the issue"), 7 ("one must identify the other parts of the code that are provably affected"),
   and 8 ("clearly not just an intentional change") each individually kill a whole class of
   finding that the smell baseline actively invites. Apache-2.0, one file, no runtime change.
   The smell list need not go — but it should be demoted from "the baseline always applies" to
   candidate-generation, with the Codex criteria as the gate every candidate must pass.

2. **Add a verify pass, using the built-in's three-state vocabulary rather than a bare
   confidence number.** CONFIRMED / PLAUSIBLE / REFUTED with "PLAUSIBLE by default" and
   "REFUTED only when constructible from the code" is a better instrument than "score 0-100,
   filter <80", because it forces the verifier to *quote the line that proves it* rather than
   emit a number. And it fixes the specific failure mode Pocock's brief has: nothing currently
   stops a Standards sub-agent from reporting a smell it half-believes. (Learn from the binary;
   write your own words — it is not vendorable.) Pair it with Anthropic's 8-item FP taxonomy
   from the `code-review` plugin, which *is* Apache-2.0 and quotable.

3. **Give the Spec/Requirements axis pr-agent's `requires_further_human_verification` slot.**
   MIT, and it directly serves an instruction `legacy reviewer` already carries: "Where a
   verdict turns on something the code, spec, standards, and history do not answer, raise a
   question rather than guess a finding." Right now the Spec sub-agent has no output slot for
   "I can't tell from the code" — so an uncertain requirement either becomes a finding or
   silently disappears. A third bucket alongside missing/scope-creep/wrong makes the question
   path structural instead of aspirational.

Two smaller ones worth considering: **borrow the built-in's Conventions discipline verbatim in
spirit** — "Only flag a violation when you can quote the exact rule and the exact line that
breaks it — no style preferences, no vague 'spirit of the doc' inferences" — which is strictly
tighter than Pocock's current "cite the standard (file + the rule)"; and **add
`silent-failure-hunter` (Apache-2.0) as a third angle**, since dropped-error hunting is a
high-yield defect class that neither Pocock axis covers and it is the one specialist in
`pr-review-toolkit` with no substitute elsewhere.

**What the hybrid must not import:** the built-in's high-effort recall bias ("catching real
bugs matters more than avoiding false positives — err on the side of surfacing"). That
calibration is written for a human reading a terminal. Under `legacy reviewer` every
surfaced finding becomes a blocking line comment by default, so the correct calibration here
is the *medium*-effort precision framing — "every finding you surface should be one a
maintainer would act on" — or Codex's, which is the same idea stated better.

### (c) What would have to change in `legacy reviewer` step 2 to adopt each option

Step 2's delegation is description-matched: "invoke the model-invoked review skill whose
description best matches the change". So adoption cost is mostly *how the reviewer is reached*
and *how much normalization step 2 must do afterward*.

| Option | Change required in step 2 |
| --- | --- |
| **Status quo (Pocock)** | None. The existing "If the selected reviewer calls these axes Standards and Spec, map them to Code and Requirements" clause already handles it. |
| **Hybrid (recommended)** | Still none *in step 2*, if the grafts land in a skill whose description keeps matching — either a fork of Pocock's skill in `skills/`, or a repo-local reviewer skill. Step 2's axis-mapping clause and its "These are authoritative for publication" normalization both keep working. This is the whole reason the hybrid is cheap: **step 2 is already written against an interface, not against Pocock.** |
| **Codex rubric as the Code axis** | Step 2 would need to say the reviewer emits JSON, and add a mapping: `priority` P0–P1 → blocking, P2–P3 → `[Suggestion]`; `code_location.line_range.start` → the line comment anchor; `title`/`body` → title/evidence. Requirements would still need a second reviewer, so step 2 would go from one delegation to two, and would have to classify the axes independently rather than receiving them pre-separated. `overall_correctness` should be *ignored*, not mapped to status — the protocol's status ladder is richer and already accounts for questions and disputes. |
| **pr-agent `/review`** | Not callable. Step 2 would have to describe a re-hosted adaptation (its prompt is Jinja/TOML inside a Python app). Also needs a per-finding severity rule invented from `issue_header` + PR-level `risk_level`, since pr-agent has no per-finding severity. Its `merge_recommendation` maps suggestively onto the protocol's three statuses but must not be used directly — the protocol derives status from an ordered ladder over findings and questions, and letting the reviewer pre-empt that would break the `Needs Information` case. |
| **Anthropic `code-review` plugin** | Would require step 2 *and* step 3 to change: the plugin posts its own single summary comment via `gh`, which collides head-on with "Publish through the forge's review system: one review whose body is the summary and whose line comments are the findings, submitted together". You would have to fork it to stop at findings. Then you still have no Requirements axis. |
| **Claude Code built-in `/code-review`** | Not adoptable. It is a slash command, not a skill; step 2 has no way to invoke it; its severity is ordering-only; and it is proprietary. |
| **`/code-review ultra`** | Not adoptable — user-triggered and explicitly forbidden to launch from an agent. |
| **`/security-review`** | Not a replacement, but a plausible *addition*: it is MIT, non-interactive, and emits `{file, line, severity, confidence}`. If added it should be a third axis or fold into `[Code]`, and step 2 would need a confidence-to-severity rule. Out of scope for this question. |
| **superpowers `requesting-code-review`** | Cheapest mechanical swap of any alternative — it is already a skill, already two-axis, already Critical/Important/Minor. But it is a downgrade on noise, which is the actual problem. Not recommended. |

### Honest summary

Nothing published clearly beats the incumbent, and the reason is a real gap in the ecosystem
rather than a failure of searching: **the published artifacts that take false positives
seriously are all code-only, and the ones that check the change against its spec all take
false positives casually.** Pocock's skill is on the wrong side of that split — good axes,
casual filtering — but it is on the side this repo's protocol is built around, and the
filtering is the part you can bolt on from Apache-2.0 and MIT sources without touching
`legacy reviewer` at all.

The one artifact I would put real weight on is
[Codex's `rubric.md`](https://github.com/openai/codex/blob/main/codex-rs/prompts/templates/review/rubric.md):
Apache-2.0, 100% readable, zero interactivity, anchoring and severity that fit this repo's
protocol almost exactly, and the best-articulated "should I flag this" test in public. It is
not a replacement. It is the missing half.
