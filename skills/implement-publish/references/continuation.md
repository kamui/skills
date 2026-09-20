# Continue a review after fixes

Before each continuation, update the packet under [step 3's verification rules](../SKILL.md#3-implement). Record every invalidation decision and its reason for checks and acceptance evidence. Neither the reviewer nor future CI substitutes for the implementer's verification before publication.

After committing fixes, choose the route before sending anything. Both routes must meet [step 4's awaited-route requirement](../SKILL.md#4-review-before-publishing).

| Host resumption behavior | Route |
| --- | --- |
| Returns the completed result on an awaited route | Resume the same reviewer with the new head, updated packet, and fixed stable ids. |
| Returns before the result, such as an acknowledgment followed by background work | Dispatch a **fresh continuation**: one isolated general-purpose reviewer at the same tier, on an awaited route. |

A fresh continuation replaces a completed reviewer's next phase. It cannot run beside a pending reviewer, retry a failed review, or bypass a partial result.

Brief the fresh reviewer to invoke `review-code` with `mode: one-shot` for the addendum's rubric, verification, and record rules. Supply:

- Repository, applicable instructions, every spec source, base, and full reviewed and final head SHAs.
- Original record paths, updated evidence packet with invalidation decisions, complete review and routed items, fixed stable ids, unresolved or disputed findings and material questions, and existing finding, coverage, and verification state, including whether the follow-up batch is spent.

It first checks that every record path is readable and belongs to the review and reviewed head. Missing or mismatched state is a coverage gap. So is packet evidence that is missing, unreadable, incomplete, or attributed to a head contradicted by its invalidation decisions. Neither permits a clean addendum.

Either continuation appends an addendum in the original record's named `addenda` directory, leaving the record unchanged. It re-verifies each fixed finding at the new head using bounded reads and focused tests, and inspects the complete fix delta (`git diff <reviewed head>...<final head>`) under the rubric's Complete inspection rules.

The reviewer independently checks every invalidation decision against that delta. Checks remain owed when it reaches their inputs, environment, or covered behavior; acceptance exercises remain owed when it reaches their criterion, method, or inputs. Retained evidence keeps its original head.

Falsify every new candidate. Dispatch one verifier batch containing all new candidates meeting `review-code`'s mandatory-verification trigger, and await its result. Preserve stable ids, verification accounting, test restrictions, and the batch cap across workers; changing workers grants no extra batch. Unsettled findings remain blocking.

If the delta is too large to inspect, replace the addendum with a fresh-context one-shot review of the full base-to-final-head range, accounting for every outstanding finding and question.
