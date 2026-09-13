# PR #213 addressing: original output and reproducible inputs

Starting head: `1eec684b13e6ae119544cf9bcd145bb261bbe2ea`. Spec: [#166](https://github.com/kamui/skills/issues/166). Feedback: [own-output drift](https://github.com/kamui/skills/pull/213#discussion_r3998469126), [gate membership](https://github.com/kamui/skills/pull/213#discussion_r3998469130), [changelog](https://github.com/kamui/skills/pull/213#discussion_r3998469132).

The blocking finding is warranted: the original later-state check compares the candidate review's `updated_at` against `submitted_at`, and compares original comments' `updated_at` against that same cutoff. A one-second forge publication delay with `last_edited_at: null` therefore forces another audit. The final linked-index update also looks like a later edit. The correction uses an `output` digest of the exact prospective publication body and original comment bodies, including a recomputed digest in the final phase-2 body. A later run compares content against that baseline; replies remain outside the excluded original set. The helper strips the run trailer before hashing to avoid self-reference and needs neither timestamps nor ids before publication. Changed or missing original content still defeats suppression. This is content identity, not an authenticity signature; a same-content re-save adds no evidence. Missing output identity cannot suppress a current-contract review.

Mechanical validation: the identity CLI fixtures cover original review/comment timestamps one second after submission with no edit, a phase-2 linked body with its recomputed digest, later original-comment edits, deleted original comments, missing publication identity, changed review body and human replies. The output-digest CLI is exercised against the payload consumed by the identity fixture. The existing forge-packet and context-fingerprint suites cover pagination, later replies and canonical input normalization.

The optional membership suggestion addresses a real repeated-work defect in changed instructions. The remedy preserves the spec's exact reviewed-guidance digest: step 1 resolves the complete applicable normative pointer closure before hashing or dispatch. It does not drop guidance that turns out to govern the review. A missed pointer returns to input preparation and repeats affected assessment using the expanded handover. The changelog omission is corrected alongside the release's existing DESIGN note. These are changes within the still-unmerged `v2b-5` release, not another independently merged semantic release.

## Instruction replay

These are paper transitions through the instructions, not executed discovery/verifier experiments or measured recall gains.

| Scenario | Result under corrected instructions |
| --- | --- |
| Root AGENTS points to scripts guidance; that file applies to the changed Python helper | Step 1 resolves and records its pinned blob before the gate; the next identical run selects the same membership and produces the same context |
| Reached guidance points to another applicable tracked base file | Continue the closure until every applicable normative pointer is accounted for; each file enters once, including cycles |
| A worker discovers an applicable pointer preparation missed | Return to step 1, rebuild inputs and affected handovers, then repeat affected assessment; no publication-only digest extension |
| Phase-2 body update succeeds | Its body and recomputed output digest travel in the same PUT, with the original submitted comment bodies; a later identical collection matches despite later edit stamps |
| Phase-2 update fails | The complete phase-1 body and its original digest stand; never write the digest alone |
| Someone edits an original finding after publication | Current content differs from the frozen output digest, so duplicate suppression fails; later replies remain checked independently |

Relevant implementation: [publication](../../skills/code-audit-publish/references/publishing.md), [input membership](../../skills/code-audit-publish/references/input-identity.md), [workflow](../../skills/code-audit-publish/SKILL.md), [CLI fixtures](../../skills/code-audit-publish/scripts/test_review_identity.py).
