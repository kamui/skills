---
name: code-review-publish
description: Review an issue-linked pull request and publish findings as PR comments or a PR review. Use only when the caller intends both code review and posting feedback to the PR.
---

# Publish code review

Review the change with the best available reviewer, then publish the findings to the change's issue and pull request. Keep the review's Standards and Spec axes separate throughout.

## Process

### 1. Resolve the review and publication targets

Use the fixed point the user supplied. If they omitted it, ask for one so the review has a stable comparison base.

Read the repository's issue-tracker instructions, including `docs/agents/issue-tracker.md` when present. Resolve:

- the pull request for the current change;
- the originating issue used as the spec source;
- the current pull-request head SHA;
- any earlier review from the posting identity, including its reviewed head SHA, findings, responses, and resolution state;
- the connected forge and issue-tracker capabilities for reviews, issue activity or comments, and pull-request line or general comments.

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

Create one issue-tracker review note containing:

- the pull request link and reviewed head SHA;
- for a re-review, the earlier reviewed head SHA and prior-finding dispositions, separate from new findings;
- separate `Standards` and `Spec` sections;
- every normalized finding from each section, lightly cleaned only for the tracker format;
- the review's per-axis summary.

Use a native code-review or review-activity feature when the tracker exposes one. Otherwise, an issue comment is the equivalent. Do not change issue status, labels, assignee, or other fields.

Create exactly one pull-request comment for each new finding. For a prior finding that is still present, follow up on its existing thread when the provider supports replies; otherwise create one comment that identifies the earlier finding. Each new or follow-up comment must:

- start with `[Standards]` or `[Spec]`;
- state the finding, its evidence, and the requested change;
- retain the documented-standard citation or quoted spec evidence supplied by the review;
- attach to the most specific changed line that supports it.

If a finding cannot attach to a changed line, use one separate general pull-request comment for that finding. A forge may submit several line comments as one review operation, but each finding must remain its own comment. With no new or still-present findings, submit an approval only when the user or repository workflow authorizes it; otherwise leave no pull-request comments. The issue note should record that both axes passed or that an axis lacked a spec.

### 4. Publish once

Before writing, inspect existing issue and pull-request activity from the posting identity for a review of the same head SHA. Update the matching publication when the provider supports edits. Otherwise, skip already-published items and report them. Do not create duplicates.

Post the pull-request comments, then post the issue-tracker review note with the final comment counts. Attempt each external write once. If a write returns an ambiguous result, read the target before deciding whether a retry is safe. Stop after one confirmed retry and report any remaining failure instead of continuing to post.

Finish with links or stable identifiers for the issue note and pull-request comments, counts by axis, skipped duplicates, and unsupported or failed publication capabilities.
