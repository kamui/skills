# Continue a review after fixes

Update verification results under [step 3's rules](../SKILL.md#3-implement). Group results sharing a retention or invalidation reason; reference earlier results instead of copying them.

After committing fixes, choose a route under [step 4's awaited-completion rules](../SKILL.md#4-review-before-publishing):

- Resume the same reviewer if the host can resume and await its completed result. Dispatch followed by a supported wait qualifies; an acknowledgment alone does not.
- Otherwise use a fresh isolated reviewer meeting step 4's requirements, at the same tier, on an awaited route. This continues a completed review; it cannot replace pending, failed or partial work.

For either route, brief an implementation-gate addendum applying `review-code`'s rubric, verification and record rules. Use the continuation procedure below, not its initial-review procedure. Supply:

- Full previously reviewed and final head SHAs, updated verification results with retention/invalidation reasons, and fixed finding ids.
- Original record and ordered addendum paths, plus references for the repository, applicable instructions, every spec and base. Reuse saved references rather than restating their content.

Read the record and addenda to establish current findings, unresolved or disputed items, questions, coverage and verification allowance. Validate their repository and head chain, reading version-1 files as that reference maps them. Missing or mismatched required state leaves coverage incomplete. Open supporting artifacts only as needed for review; assess unavailable evidence under `review-code`'s `references/check-evidence.md`.

Recheck each fixed finding at the final head with bounded reads and focused tests. Inspect the complete fix delta (`git diff <reviewed head>...<final head>`) under the rubric's Complete inspection rules. Independently check retention and invalidation decisions against that delta using step 3's verification rules.

Falsify new candidates under the rubric. For new candidates meeting `review-code`'s mandatory-verification trigger, and safety premises its safety-premise check requires, await one verifier batch within the remaining allowance. Preserve stable ids, verification accounting, test restrictions and batch limits across workers. Unresolved blockers and incomplete required verification prevent publication.

Append the result as the addendum `review-code`'s `references/continuation-addendum.md` defines, in the original record's `addenda` directory, leaving earlier records unchanged. If the delta is too large to inspect, instead use a fresh-context full base-to-final-head review under step 4 that writes that reference's replacement record, carrying outstanding findings, questions and verification accounting without resetting the batch allowance.
