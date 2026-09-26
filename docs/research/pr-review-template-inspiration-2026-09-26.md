# Public PR review formats worth borrowing

Checked primary documentation, configuration source, and public GitHub reviews on 2026-09-26. These observations concern presentation, not the accuracy of any review finding. GitHub did not render every inline thread in its unauthenticated page view, so the public examples support claims about visible text only.

## Verified patterns

| Source | What a reader sees or can configure | Useful lesson |
| --- | --- | --- |
| [Qodo review anatomy, with screenshots](https://docs.qodo.ai/code-review/comment-anatomy) and [finding visibility controls](https://docs.qodo.ai/code-review/findings-visibility) | Findings have short titles grouped by severity. Description is expanded by default; code, evidence, relevance, and the agent prompt are collapsed. Overflow controls keep further findings accessible. Previous reviews can also collapse. | Borrow the distinction between the information needed to act and the supporting detail. Keep all must-fix titles visible in our format. |
| [PR-Agent review documentation](https://docs.pr-agent.ai/tools/review/), [public demo PR #732](https://github.com/the-pr-agent/pr-agent/pull/732), and [`convert_to_markdown_v2`](https://github.com/The-PR-Agent/pr-agent/blob/main/pr_agent/algo/utils.py#L86) | The linked demo includes a reviewer guide with review effort, tests, security, and linked focus areas. The renderer uses an HTML table and places code excerpts in `details` blocks beneath a visible finding title and explanation. Optional review sections can be disabled. | The renderer is useful implementation reference. Borrow collapsible excerpts and linked titles; omit routine scores, effort estimates, help text, and reassuring empty categories. |
| [CodeRabbit configuration schema](https://github.com/coderabbitai/awesome-coderabbit/blob/main/schema.v2.json) and [CodeRabbit's review type guide](https://www.coderabbit.ai/blog/gpt-5-codex-how-it-solves-for-gpt-5s-drawbacks) | The summary and walkthrough can be separate. `collapse_walkthrough` defaults to `true`; `review_details` defaults to `false`. CodeRabbit names three review types, Potential issue, Refactor suggestion, and Nitpick, and five severities, Critical, Major, Minor, Trivial, and Info. Its guide says nitpicks are hidden unless Assertive mode is selected. | Separate finding type from severity, and make low-value context optional. |
| [CodeRabbit review on mattermost-plugin-calls #1221](https://github.com/mattermost/mattermost-plugin-calls/pull/1221) | The review says `Actionable comments posted: 2`. One nitpick sits under a closed `Nitpick comments (1)` disclosure. The consolidated AI-agent prompt, review info, walkthrough, and prompts beneath inline findings are also closed disclosures in the rendered page. An inline finding starts with type, severity, effort, a short action, rationale, and a suggested patch. The run says `CHILL`, despite the guide's Assertive-mode wording. | Borrow the count and compact inline opening. Keep prompts and routine details behind disclosure, and avoid duplicating findings in a consolidated prompt. This is one observed review, not a universal template. |
| [GitHub Copilot code review documentation](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review) | Copilot labels comments High, Medium, or Low; it can offer suggestions that readers apply from the comment. Review comments use GitHub's ordinary reply, resolve, reaction, and hide controls. The review normally has Comment status. | Put priority on the finding itself and use GitHub's native thread controls. A status label should not imply a required approval unless the review truly has one. |
| [Copilot review on microsoft/PowerToys #49736](https://github.com/microsoft/PowerToys/pull/49736) | The overview gives one compact paragraph, two change bullets, then a reviewed-files count and two-row file table. Its single inline thread is linked below that overview, although the unauthenticated page did not render the comment body. | A reader can understand scope and locate the finding without reading a long review body. The count helps distinguish one finding from incomplete review coverage. |
| [Anthropic's code-review command](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md) | Publication requires `--comment`. Validated issues get one brief inline comment each, with a suggested patch only when it fixes the issue completely. A clean review gets a short no-issues comment. Code links require a full commit SHA and line range. The command excludes pre-existing issues, linter findings, pedantic nits, and explicitly silenced rules. | Borrow concise comments and complete suggestions. The clean-review format is useful when coverage is complete. Its admission rules are separate from its presentation. |
| [OpenAI Codex review rubric](https://github.com/openai/codex/blob/main/codex-rs/prompts/templates/review/rubric.md) | Findings have imperative titles of at most 80 characters with a P0-P3 prefix, a one-paragraph body, and a short code range, normally within 5-10 lines. JSON fields hold priority, confidence, and location. An overall correctness verdict has a 1-3 sentence explanation. | Keep structured fields internally and render concise prose. The source describes JSON output and inline presentation; it does not establish the hosted GitHub integration's exact renderer. |
| [Conventional Comments format](https://conventionalcomments.org/) | A comment has one label, optional decorations such as `blocking`, a short subject, and optional supporting discussion. The specification warns that too many decorations hurt readability. | A compact `issue (blocking): ...` prefix can carry action and urgency. Keep the explanation only as long as needed to show the failure and next step. |
| [Google's code review comment guide](https://google.github.io/eng-practices/review/reviewer/comments.html) | Google suggests intent labels: `Nit` means a minor change the author technically should make; `Optional` or `Consider` means the change is not required; `FYI` expects no change in the current review. It also asks reviewers to explain why when needed and recognize specific good work. | Keep required small fixes distinct from optional suggestions. Do not use `nit` as a synonym for `consider`. |
| [reviewdog README](https://github.com/reviewdog/reviewdog) | The GitHub PR reporter posts findings as review comments. Its default filter includes findings on added or modified lines; diagnostic data can carry severity, rule links, and code suggestions. | Anchor findings in the changed code and suppress routine unrelated diagnostics. Keep a separate visible note when a serious issue cannot be attached to the diff. |

PR-Agent and Qodo are separate references. The [PR-Agent repository](https://github.com/The-PR-Agent/pr-agent) identifies itself as the community-maintained project donated by Qodo, distinct from Qodo's current offering. PR #732 is a historical demo with bot comments from several dates, not proof of the current hosted product's exact default layout. The documentation screenshots are useful visual examples; labels in older screenshots can differ from current configuration wording.

PR-Agent's [configuration](https://github.com/The-PR-Agent/pr-agent/blob/main/pr_agent/settings/configuration.toml) defaults to a persistent review body headed `PR Reviewer Guide`, a maximum of three findings, and enabled effort, tests, security, and ticket checks. Risk, merge recommendation, priority files, splitting advice, a numerical score, and TODO scanning are optional. Its [prompt schema](https://github.com/The-PR-Agent/pr-agent/blob/main/pr_agent/settings/pr_reviewer_prompts.toml) gives each issue a one- or two-word label, file and line range, and concise trigger and impact. Uncertain high-impact concerns must disclose the uncertainty. Its Yes/No test field asks whether relevant tests were added or updated; it does not report test execution. Persistent body updates can still produce separate update notices.

## What made the previous format long

[`review-code-publish`](../../skills/review-code-publish/SKILL.md) publishes the batch produced by `review-code`. The visible template lives in [`render_review.py`](../../skills/review-code/scripts/render_review.py), particularly `compose_body` and `compose_finding`.

At baseline `b6e5831`, the summary put Intent, Issue fit, Coverage, and Reviewed before its finding index. It could then add eight conditional sections. Each finding got separate Triggers when, Impact, and Change paragraphs, plus optional Source and permission text. Body-carried findings repeated their title in both an index entry and a finding heading. The authoring contract targeted roughly 200 words for the base summary and 160 for an ordinary finding. These were targets, not hard limits.

The current renderer already exposes `[must-fix]` and `[consider]`, rather than the `[Suggestion]` marker mentioned in the supplied analysis. It stores `kind` separately, including bug, compatibility, concurrency, invariant, security, performance, maintainability, and requirement. Our [rubric attribution](../../skills/review-code/THIRD_PARTY_NOTICES.md) confirms the Codex derivation at a pinned commit. Shorter prose would recover an upstream presentation choice while retaining our additional verification and accounting.

## Recommendations for `review-code-publish`

Lead with the review outcome, counts, and a short action list. Put the reviewed head and a short coverage statement near that outcome. Keep detailed findings in inline threads, each with a short action title, the concrete failure, and the smallest useful fix. Add a suggested patch only when it completely fixes the finding. Keep body-carried findings self-contained when no valid inline anchor exists.

Put successful check details, settled history, and routine intent or issue-fit context in one collapsed section. Keep essential evidence in the finding itself. Leave actual coverage gaps, unmet requirements, unresolved questions, and disputes affecting the outcome visible. Retain every prior item's classification and evidence even when settled history is collapsed. These are proposed adaptations, not product features verified in the sources above.

Aim for 50-90 words per ordinary finding and under 100 words of summary prose before its index. Treat these as writing targets, never reasons to omit a verified defect or a constraint needed for the right fix. Preserve both priority and `must-fix` versus `consider`; severity alone does not express the action required in this workflow.

The additional proposals are useful options, but adding them all would work against the request for a shorter review:

| Proposal | Recommendation |
| --- | --- |
| Review effort score | Leave out by default. A 1-5 estimate adds little to a review whose findings and coverage already show the work remaining. |
| Files to read first | Add only when a large or cross-file change has a useful reading order. Name each file and why to start there; avoid repeating the finding index. |
| Blocking labels | Keep the existing priority and action labels. Conventional Comments supports their purpose, but changing vocabulary adds migration work without fixing the long prose. |
| Category badges | Show a stored kind only when it helps triage, such as security or compatibility. Avoid adding a third mandatory label to every finding. Our kinds do not exactly match another product's categories. |
| AI-agent prompt block | Confirmed in the public CodeRabbit review. Make it optional and collapsed if added. The existing actionable prose and structured trailers already support follow-up; a second copy of every finding adds length and can drift. |
| Scores, poems, and routine praise | Skip numerical quality scores and decorative sections. Specific praise can be useful when it communicates something the author should preserve. |

Preserve every verified finding rather than adopting PR-Agent's default three-item cap. Keep actual check results and coverage gaps instead of substituting a Yes/No test-presence field. Persistent comment editing is a separate publication-lifecycle change and would need its own design.

An illustrative summary, using the renderer's existing payment example:

```markdown
**Changes Requested (advisory)**. 1 must-fix finding, 1 open question.

Reviewed `a1b2c3d`. Full diff covered; focused retry-policy test passed.

- [P1] [must-fix] Preserve the idempotency key across retries. [Code link]
- [Question] Must retries preserve request order? [Code link]

<details>
<summary>Review details</summary>

Intent, issue alignment, check provenance, and settled findings go here.

</details>
```

The corresponding inline finding can keep all three required ideas in one paragraph:

```markdown
**[P1] [must-fix] Preserve the idempotency key across retries**

If the server commits a charge but its response times out, the retry
creates a new idempotency key and can charge the customer twice.
In `src/retry-policy.ts`, reuse the same key for every attempt at the
same logical charge. This is required by issue #123, acceptance criterion 2.
```

These sketches informed the accepted implementation below. They abbreviate real links and omit hidden trailers. The final renderer retains the existing first-line punctuation used by gating. Changing the shared disposition vocabulary would require the paired review/addressing protocol updates described in `AGENTS.md`; this presentation change keeps that vocabulary.

## Accepted implementation

The requested PR implements the compact examples approved in the conversation:

- Lead with status and counts, then findings. An approval with optional findings states that there are no must-fix findings and counts optional improvements.
- Keep a concise reviewed-head and coverage sentence visible. Collapse intent, issue alignment, base revision, detailed check provenance, observations, and settled findings under one `Review details` disclosure.
- Keep unresolved questions, ambiguities, disputes, open prior findings, unanchored findings, and coverage gaps visible. Each unmet requirement remains a finding or question.
- Render an ordinary finding as its priority/action title and one explanatory paragraph. Retain separately required trigger, impact, and change inputs, optional source evidence, exact suggested code, and the optional finding's permission sentence.
- Preserve stable IDs, hidden trailers, commit-pinned links, evidence accounting, and authorization. `COMMENT` remains advisory; only an authorized `APPROVE` or `REQUEST_CHANGES` removes that suffix.

Effort scores, new badges, reading-order guidance, agent prompt blocks, and persistent-comment updates remain separate proposals. The implementation changes the renderer, its checks and tests, and the authoring instructions. It does not change the protocol vocabulary.
