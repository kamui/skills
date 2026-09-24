# Continue a review after fixes

Update verification results under [step 3's rules](../SKILL.md#3-implement). Group results sharing a retention or invalidation reason; reference earlier results instead of copying them.

After committing fixes, choose a route under [step 4's awaited-completion rules](../SKILL.md#4-review-before-publishing):

- Resume the same reviewer if the host can resume and await its completed result. Dispatch followed by a supported wait qualifies; an acknowledgment alone does not.
- Otherwise use a fresh isolated reviewer meeting step 4's requirements, at the same tier, on an awaited route. This continues a completed review; it cannot replace pending, failed or partial work.

For either route, brief an implementation-gate addendum applying `review-code`'s rubric, verification and record rules. Use the continuation procedure below, not its initial-review procedure. Supply:

- Full previously reviewed and final head SHAs, updated verification results with retention/invalidation reasons, and fixed finding ids.
- The original record path and the absolute `continuation` helper path step 4's review returned, plus references for the repository, applicable instructions, every spec and base. Reuse saved references rather than restating their content.

Establish current findings, unresolved or disputed items, questions, coverage and verification allowance with `python3 <continuation> state --json <record>`, which validates the repository and head chain. `chain-invalid` leaves coverage incomplete; `legacy-chain-needs-mapping` maps version-1 files by hand as that reference defines. Never reduce the chain another way. Open supporting artifacts only as needed for review; assess unavailable evidence under the Supplied checks section of `review-code`'s `references/rubric.md`.

Recheck each fixed finding at the final head with bounded reads and focused tests. Inspect the complete fix delta (`git diff <reviewed head>...<final head>`) under review-code's Strategy and admission rules. Independently check retention and invalidation decisions against that delta using step 3's verification rules.

Falsify new candidates under the rubric. For new candidates meeting `review-code`'s mandatory-verification trigger, and safety premises its safety-premise check requires, await one verifier batch within the remaining allowance. Preserve stable ids, verification accounting, test restrictions and batch limits across workers. Unresolved blockers and incomplete required verification prevent publication.

Compose the addendum with the helper as `review-code`'s `references/continuation-addendum.md` defines, leaving earlier records unchanged, and return its output: `status`, `coverage`, `head`, `record`, `addendum`, `report` and `continuation`. If the delta is too large to inspect, instead use a fresh-context full base-to-final-head review under step 4 that writes that reference's replacement record, carrying outstanding findings, questions and verification accounting without resetting the batch allowance, and compose the addendum naming it.

Read the returned `report`, the complete current result. Before step 5, `python3 <continuation> state <record>` must exit 0 with `head` equal to the final committed head; `chain-invalid`, a missing report or another head is an incomplete review, never a publishable one. Only a chain the helper routes to `legacy-chain-needs-mapping` is read from its hand-mapped addendum, as before.
