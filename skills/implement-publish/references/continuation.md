# Continue a review after fixes

Update verification results under [step 3's rules](../SKILL.md#3-implement). Group results sharing a retention or invalidation reason; reference earlier results instead of copying them.

After committing fixes, choose a route under [step 4's awaited-completion rules](../SKILL.md#4-review-before-publishing):

- Resume the same reviewer if the host can resume and await its completed result. Dispatch followed by a supported wait qualifies; an acknowledgment alone does not.
- Otherwise use a fresh isolated reviewer meeting step 4's requirements, at the same tier, on an awaited route. This continues a completed review; it cannot replace pending, failed or partial work.

For either route, brief a re-review from a prior record: invoke `review-code` with `mode: one-shot` on the base-to-final-head range, with the same base and spec sources and `prior_record` set to the absolute path of the latest accepted record. `review-code`'s `references/prior-state.md` governs it: the new record classifies every open item, carries open findings, confirmations, outstanding work and routed items, and spends only the verification allowance the prior record left. A delta too large to inspect is still this run, reviewed in full scope. Supply:

- Full previously reviewed and final head SHAs, updated verification results with retention/invalidation reasons, and fixed finding ids.
- References for the repository, applicable instructions, every spec and base. Reuse saved references rather than restating their content.

Recheck each fixed finding at the final head with bounded reads and focused tests. Inspect the complete fix delta (`git diff <reviewed head>...<final head>`) under review-code's scope and admission rules. Independently check retention and invalidation decisions against that delta using step 3's verification rules. Open supporting artifacts only as needed for review; assess unavailable evidence under the Supplied checks section of `review-code`'s `references/rubric.md`.

Falsify new candidates under the rubric. For new candidates meeting `review-code`'s mandatory-verification trigger, materially changed mandatory claims, and safety premises its safety-premise check requires, await one verifier batch within the remaining allowance. Preserve stable ids, verification accounting, test restrictions and batch limits across workers. Unresolved blockers and incomplete required verification prevent publication.

Return the output of `render_review.py --check` on the new record's private directory. Read the returned `report.md`, the complete current result. Before accepting it, `python3 <skill root>/scripts/render_review.py --check --head <final committed head> --lineage <each accepted record> --lineage <new record> <private-dir>` must exit 0, naming every record accepted so far, the latest included. Another head, a missing report, or a record that does not descend from the latest accepted record, such as a sibling that continued an earlier one and reused its allowance, is an incomplete review, never a publishable one: discard it and continue again from the latest accepted record. Once it passes, the new record is the latest accepted record.

A record from before `review-code-record/1`, such as an implementation-gate record with an `addenda` directory, cannot be a prior record: brief a full base-to-final-head review without `prior_record`, which starts a new allowance and names the earlier record in its coverage.
