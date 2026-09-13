# Audit input identity: mechanical fixtures and instruction replay

Spec: [#166](https://github.com/kamui/skills/issues/166), under [#156](https://github.com/kamui/skills/issues/156). Pre-change pin: `a72cf5df7ef1a9d33de63e4ace7be676ad5d0029`. Runtime: [SKILL](../../skills/code-audit-publish/SKILL.md), [input identity](../../skills/code-audit-publish/references/input-identity.md), [publication](../../skills/code-audit-publish/references/publishing.md). The change advances `v2b-4` to `v2b-5`.

## Mechanical checks

The standalone copies of `test_forge_packet.py` and `test_context_fingerprint.py` run through their helpers' CLIs. They cover equivalent JSON/list ordering and numeric id types, changed issue/spec/guidance inputs, unavailable versus empty comments, a real-query-shaped nonempty issue discussion, outer and nested pagination, page-boundary duplicate ids, failed/missing continuations, edited replies, and explicitly referenced non-closing issues. Audit-specific `test_review_identity.py` covers full identity/version/digest matching, changed base at unchanged head, legacy/no-digest trailers, incomplete current/prior coverage, a human prose reply with the candidate review id, edits to the candidate review itself, undated thread resolution, omitted state/timestamps, and an open-to-merged transition at the same head (which requires a new identity). These are behavioral fixtures for deterministic mechanics, not measured review quality.

The documented root GraphQL query was executed read-only against [PR #212](https://github.com/kamui/skills/pull/212). The resulting packet reported complete coverage: one closing issue, ten reviews, four threads with three comments each, one PR comment, and an available zero-comment issue discussion. It preserved `merged: true`. This smoke test confirms the selected fields against the live schema and exercises normalized review/reply identities; actual multi-page traversal and nonempty issue comments are covered by fixtures, not by that single-page live target. The first network attempt failed; a later read-only attempt succeeded. No audit review was published.

## Policy transition replay

These are paper traces through the instructions, not executed finder/verifier runs or measured recall/precision gains. They hold the diff and aggregate status fixed where stated.

| Input scenario | Pre-change transition | Current transition and evidence |
| --- | --- | --- |
| Same head, one standing `must-fix`; issue now requires refunds and verification confirms a new missing-refund finding | Publishing twice: same head/status lets the old review stand, risking loss of the new finding | Issue text changes `context`; step 1 performs a re-review; Publishing twice submits the new finding even while status remains Changes Requested, carrying the standing id/thread |
| Same head, human replies without a trailer that the supposed implementation has a remaining failing case | Prose is first-class, but head-only round selection and status equality can skip its consequence | Packet retains the prose, identity helper reports later reply, and same-head re-review assesses it against code using the existing finding id |
| Same head, base moves to guidance with a new applicable rule | Head/status alone can leave the old assessment standing | Full base SHA mismatch defeats duplicate identity; the shared block reads pinned base guidance and its blob changes the digest |
| Candidate review has an old workflow or no context digest | Old head/status shortcut may treat it as current | Read historical findings/replies normally; identity check fails workflow/context and requires the current-contract review |
| Issue comment page 2 fails after visible findings were obtained | Earlier capped reading had no precise completion contract | Persist exact connection/cursor and partial records; packet and summary remain incomplete; duplicate shortcut is unavailable |
| Packet says CLOSED and merged is missing | Existing retrospective rule depends on information it did not require to be explicit | Missing `merged` is an input gap; all writes are disabled until recovered, even when ancestry suggests merge |
| An existing open-target review matches code/context; caller now requests retrospective audit after merge | Head/status equality can return the old review | The trailer's explicit state/merged mismatch defeats duplicate identity and the retrospective pipeline runs; this transition has a CLI regression fixture |
| Caller requests retrospective audit; packet explicitly says merged | Publication already disabled unless explicitly enabled | Preserved: run the pipeline and return would-be output, with no forge writes unless separate explicit publication authority exists |
| Caller separately authorizes retrospective publication, but target/evidence changes before write | Only the head was rechecked | Step 4 repeats complete collection and compares normalized evidence and explicit state; stale or failed inputs stop writes until reassessed |
| Inputs fully match; current run has nevertheless already confirmed a new eligible finding | Same status could suppress it | Input identity and Publishing twice explicitly preserve new eligible material; identity eligibility alone cannot discard it |

## Limits

The later-state check is conservative: undated old thread state or harmless later activity may cause another assessment. It does not infer relevance mechanically. External source availability and publication authority remain instruction-governed; a digest is not permission. Full final-payload validation remains outside #166.

The generic skill validator could not run because its environment lacks PyYAML. Frontmatter, local links, Python 3.9 syntax compatibility and whitespace were checked independently; compatibility metadata is preserved. The existing shared-block, verifier-prompt, finder-report, verifier-accounting and coordinate helpers were run directly as the repository requires. No global sync applies until skill changes reach `origin/main`.
