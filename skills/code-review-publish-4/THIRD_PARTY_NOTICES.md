# Third-party notices

## OpenAI Codex review rubric

`references/review-rubric.md` is derived from the OpenAI Codex review rubric:

<https://github.com/openai/codex/blob/81de4f251cfdaf32ecb85e2160ebfc11a562d44b/codex-rs/prompts/templates/review/rubric.md>

Copyright 2025 OpenAI. Licensed under the Apache License, Version 2.0. The prototype changes the source material for issue-linked review, tool-using evidence collection, candidate falsification, complete-diff coverage, re-review state, and human-and-agent-readable publication. See `licenses/Apache-2.0.txt`.

## Design provenance

The workflow also independently adapts ideas discussed in these sources without copying their prompt text:

- Matt Pocock's local `code-review` skill: merge-base and originating-spec discipline.
- PR-Agent: ticket context, private requirement assessment, and surgical diff context.
- `misospace/pr-reviewer-action`: stale-head checks, fail-closed coverage, carried findings, and evaluation-oriented design.
- Docker Agent Action and Anthropic's review workflow: candidate generation followed by falsification.
- Gemini, OpenHands, and GitHub Agentic Workflows: untrusted-input boundaries, exact anchors, changed-file manifests, deduplication, and one batched review.
