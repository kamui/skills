---
name: code-review-publish
description: Review an issue-linked pull request and publish findings as PR comments or a PR review. Use only when the caller intends both code review and posting feedback to the PR.
---

# Publish code review

Review the change with the best available reviewer, then publish the findings to the pull request as a review with line comments. Keep the review's Standards and Spec axes separate throughout. The originating issue is the spec source only; publish nothing to it.

## Process

### 1. Resolve the review and publication targets

Use the fixed point the user supplied. If they omitted it, ask for one so the review has a stable comparison base.

Read the repository's issue-tracker instructions, including `docs/agents/issue-tracker.md` when present. Resolve:

- the pull request for the current change;
- the originating issue used as the spec source;
- the current pull-request head SHA;
- any earlier review from the posting identity, including its reviewed head SHA, findings, responses, and resolution state;
- the connected forge capabilities for pull-request reviews, review bodies, and line or general comments.

Follow repository-specific instructions for fetching and writing tracker data. Treat tracker and forge tools by capability, not vendor name. If the issue or pull request is ambiguous, ask the user before any external write. If a target or write capability is absent, continue with the supported target and record the gap for the final report.

### 2. Run the review

Honor a code-review skill the user names. Otherwise, invoke the model-invoked review skill whose description best matches the current change. Give it the fixed point and any spec source the user supplied. If no review skill is available, perform the review directly.

The review must cover both axes:

- **Standards**: violations of documented repository standards and relevant code-quality findings.
- **Spec**: missing, partial, incorrect, or unrequested behavior compared with the originating spec.

If the selected reviewer omits an axis, complete that axis directly. If no spec exists, mark the Spec axis as unavailable instead of inventing requirements.

When an earlier review exists at a different head SHA, treat this run as a re-review. Keep the original fixed point as the comparison base, use the earlier reviewed head to identify intervening changes, and still evaluate the complete pull-request diff. Independently reassess every prior finding against the current code, its responses, the spec, and repository standards as **resolved**, **still present**, **obsolete**, or **superseded**.

Normalize every finding to an axis, summary, evidence, file and line when available, and requested change. These normalized findings are authoritative for publication. Do not merge or rerank the axes.

### 3. Prepare the publications

Create one pull-request review summary that is not tied to a line of code, containing:

- the pull request link and reviewed head SHA;
- for a re-review, the earlier reviewed head SHA and prior-finding dispositions, separate from new findings;
- separate `Standards` and `Spec` sections;
- every normalized finding from each section, lightly cleaned only for the forge format;
- the review's per-axis summary.

When the pull-request author and the posting identity are the same user, the forge cannot assign an external reviewer: publish the summary as one general pull-request comment. Otherwise, submit the summary and the line comments together as one pull-request review when the forge supports it.

Create exactly one line comment for each new finding. For a prior finding that is still present, follow up on its existing thread when the provider supports replies; otherwise create one comment that identifies the earlier finding. Each new or follow-up comment must:

- start with `[Standards]` or `[Spec]`;
- state the finding, its evidence, and the requested change;
- retain the documented-standard citation or quoted spec evidence supplied by the review;
- attach to the most specific changed line that supports it.

If a finding cannot attach to a changed line, use one separate general pull-request comment for that finding. A forge may submit several line comments as one review operation, but each finding must remain its own comment. With no new or still-present findings, submit an approval only when the user or repository workflow authorizes it; otherwise leave no line comments and let the review summary record that both axes passed or that an axis lacked a spec.

### 4. Publish once

Before writing, inspect existing pull-request review activity from the posting identity for a review of the same head SHA. Update the matching publication when the provider supports edits. Otherwise, skip already-published items and report them. Do not create duplicates.

Post the pull-request comments together with the review summary. Attempt each external write once. If a write returns an ambiguous result, read the target before deciding whether a retry is safe. Stop after one confirmed retry and report any remaining failure instead of continuing to post.

Finish with links or stable identifiers for the review summary and the pull-request comments, counts by axis, skipped duplicates, and unsupported or failed publication capabilities.
