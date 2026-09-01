# Attribution

This skill assembles prompt material from several open-source reviewers. All sources are permissively licensed; each is adapted rather than copied verbatim, and none of the upstream projects endorse this.

Verified against the sources on 2026-08-31. Prompt text in these repositories drifts; re-check before relying on a specific quotation.

| Source | License | Used for |
| --- | --- | --- |
| [`openai/codex`](https://github.com/openai/codex) — `codex-rs/prompts/templates/review/rubric.md` | Apache-2.0 | The eight qualifying criteria and the volume rule in `code-axis.md`; the priority scale `P0`–`P3`; the anchoring and comment-writing discipline in `finding-format.md` |
| [`qodo-ai/pr-agent`](https://github.com/qodo-ai/pr-agent) (now `The-PR-Agent/pr-agent`) — `pr_agent/settings/pr_reviewer_prompts.toml` and `code_suggestions/pr_code_suggestions_reflect_prompts.toml` | MIT | The requirement-restatement step, the compliance buckets, and the "cannot tell from the code" channel in `requirements-axis.md`; the asymmetric flag rule and the low-value exclusions in `code-axis.md` |
| [`mattpocock/skills`](https://github.com/mattpocock/skills) — `skills/engineering/code-review/SKILL.md` | MIT | The two-axis separation, and the scope-creep bucket in `requirements-axis.md` |
| Anthropic `code-review` plugin — `plugins/code-review/commands/code-review.md` in the official Claude Code plugin marketplace | Apache-2.0 | The exclusion taxonomy in `code-axis.md` |
| `code-review-publish` — `references/review-protocol.md`, in this repository | — | Directional ancestor of the comment shape, trailers, status ladder, disposition and verdict vocabularies, round cap, and forge verbs |

## Not used

Claude Code's built-in `/code-review` is proprietary and compiled into the CLI. Its three-state verification vocabulary and its refute-with-evidence asymmetry informed the *design* of `verify.md`, which is written from scratch. No text is taken from it, and none should be.

## What is original here

The dual-audience finding contract — an agent-facing `action` alongside a human-facing `priority`, the explicit permission line on `consider`, the required `trigger` field, and the trailer as the machine-authoritative copy of the tag line — is this skill's own, and is the reason it does not simply adopt one of the above.

Routing verified-`plausible` candidates to questions rather than findings is also original, and follows from the same premise: an agent reading this review will act on a finding, so an unproven finding is more expensive here than an unanswered question.
