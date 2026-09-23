# Issue 333 static clarity and caller-contract inspection

Revision inspected: `44b9331ae45650450fbd56fbf1f0ad1d29257b15`. Every source coordinate below refers to that revision, obtained with `git show` or `git grep`.

## Method and limits

I read only `skills/review-code/SKILL.md` before opening the research instructions, caller contracts, or linked references. The first-read account below records what I could identify from that entrypoint. I then inspected direct callers and selected contract tests. This is one agent's static reading, not owner/user comprehension testing, an independent model comparison, a benchmark, or a live workflow integration. I did not execute tests or models, read comparison expected-outcome documents, modify repository files, or write to the forge. Test assertions below establish what the source intends to check, not that those checks passed in this inspection.

## First read of the entrypoint

- The strategy is identifiable: establish sourced requirements before judging the diff, read the entire change and affected behavior, attempt to disprove suspected defects, independently verify costly conclusions, then render and validate. Every changed file requires a reviewed, defensibly ignored, or unreviewed classification. Source: `skills/review-code/SKILL.md:38-44`.
- The verifier triggers are explicit. Surviving must-fix, security/authorization, data-integrity, destructive-migration, and released-compatibility candidates require verification; so do code-decided prior must-fix findings on PR re-review. A proposed no-blocker conclusion in the listed risky areas, including concurrency/failover, needs safety-premise checks. Optional scrutiny is separate. Source: `skills/review-code/SKILL.md:52-64`.
- Merge blockers are separate from priority. `must-fix` blocks; `consider` does not. The status order is Changes Requested, Incomplete, Needs Information, Approved. An unsettled prior blocker can keep Changes Requested even with a coverage gap. Sources: `skills/review-code/SKILL.md:48`, `skills/review-code/SKILL.md:72-79`.
- Incomplete coverage includes unread files, missing required checks or inputs, incomplete fetches, and unfinished required verification. The verifier allowance is one initial batch plus at most one follow-up across continuations; pending batches must be awaited. Confirmed findings still return when coverage is incomplete. Sources: `skills/review-code/SKILL.md:66-77`.
- The return contents are discoverable without opening a helper: pinned identity, findings/questions, requirement outcomes, per-file coverage, evidence, verification and remaining allowance, routed items, full rendered review, and artifact paths. Publishable and implementation-gate outputs differ, and named stops replace the record. Source: `skills/review-code/SKILL.md:81-96`.

One first-read comprehension problem was the boundary between an unconfirmed new proposed must-fix and an existing unsettled must-fix. “It publishes only when confirmed” at line 60 and “including a disputed or unverifiable one” at line 76 require the reader to distinguish a candidate from a retained finding when choosing Changes Requested versus Incomplete. The entrypoint gives both rules but does not demonstrate that boundary. The linked handoff settles the candidate side: required work after exhaustion stays unpublished and outstanding, while an existing known blocker can retain status precedence. Source: `skills/review-code/references/verifier-handoff.md:15-23`. This is recorded reading friction, not a demonstrated contract defect or evidence of owner confusion.

I found no other concrete comprehension failure in identifying the requested five topics. The detailed admission and encoding rules remain in the explicitly linked references; this account does not claim the entrypoint is sufficient to execute the entire workflow alone.

## Caller contracts checked

| Consumer | Static evidence |
| --- | --- |
| `implement-publish` | Explicitly requests one-shot implementation-gate review, `record.json`, continuation paths, and a final committed-head gate. Its continuation consumes prior record/addenda, preserves stable ids and verifier allowance, and blocks publication on unresolved blockers or incomplete required verification. `skills/implement-publish/SKILL.md:45-57`; `skills/implement-publish/references/continuation.md:10-21`. |
| `review-code-publish` | Requests one-shot review and consumes `batch.json`; uses the recorded skill root for gating regeneration; reports the posted batch form. Publication invariants retain the run trailer in the summary and finding/question trailers in comments. `skills/review-code-publish/SKILL.md:23-36,49-52`; `skills/review-code-publish/references/publication.md:39-46`. |
| `resolve-review` | Reads public stable finding ids, priority/action/blocking fields, whole-change questions and reply trailers. The ledger has comment-id fallback. Its independent internal reviewer and continuation retain their own assessment artifacts and evidence rather than reading implementation-gate records. `skills/resolve-review/SKILL.md:27,49-59`; `skills/resolve-review/references/addressing-protocol.md:7-11,40-44,68-70,87-99`. |
| `finish-it` | Reads forge review status/current head, question/dispute state, and addressing summaries. It counts addressed-head trailers and passes only its packet between fresh step agents. Private implementation-gate records are not its cross-step transport. `skills/finish-it/SKILL.md:62-70,80-92`. |

No incompatible field consumption was found in these static caller checks. This is not an executed end-to-end compatibility result.

## Public rendering and private continuation evidence

The composer owns formatting, trailers and artifact shapes; profiles must derive the same findings, questions, status and coverage. Both retain private accounting. Sources: `skills/review-code/references/rendering.md:3,26-30,44`.

The public-output contract test asserts exact finding/question markdown and trailers, the run trailer, the inline coordinate, historical payload readability, and the optional action/blocking trailer. Source: `skills/review-code/scripts/test_compose_review.py:596-621`.

The private-profile test asserts schema `implementation-gate-record/2`, validator-readable output, identical public summary/items across profiles, verification accounting retention, evidence outcomes, and addenda paths. Source: `skills/review-code/scripts/test_compose_review.py:310-337`.

Continuation rules preserve open findings/questions, outstanding work, cumulative allowance, and immutable earlier records. Missing or broken chains return Incomplete. Replacement records carry confirmations and spent allowance; version-1 chains have an explicit mapping. Source: `skills/review-code/references/continuation-addendum.md:5-39`. The source explicitly says no script validates an addendum at line 5, so the tests cited above do not establish validation of an actual continuation chain.

The inspected sources support preserved caller-facing comments/trailers and a defined private continuation contract. Remaining evidence limits are owner comprehension, actual reviewer behavior, live caller integration, and test execution in this inspection.
