# Private contracts: implementation-gate record and addendum, version 2

Draft for [#329](https://github.com/kamui/skills/issues/329). Nothing here is active. At `7387c169c9b5b23c5c679efb7110c9c07fc3f7f3`, `compose_review.py` still writes and validates `implementation-gate-record/1`. [#331](https://github.com/kamui/skills/issues/331) implements this contract.

Scope: the local record that `implementation-gate` returns, and the addendum that a continuation appends after fixes. Published payloads, batches, finding and question text, trailers, and caller input names do not change. The only public change is the workflow-identifier bump, taken at activation.

## What changes from version 1

| Version 1 field | Version 2 | Reason |
| --- | --- | --- |
| `record.ledger.candidates` (every raised candidate, including dropped ones) | Removed | It existed so a complete-ledger attack could reach every acquittal. That attack is gone. Rendered items carry the findings and questions; `verification.tasks` carries what was verified. |
| Candidate row `material`, `attackable` flags | Removed | Their only use was choosing the clean-verdict mode. |
| `verification.clean_verdict` (`stands`, `outstanding`, `not-required`) | Removed | The safety-premise check replaces it. Its outcomes are task rulings. |
| Candidate row `verification` (`independent-confirmed`, `primary-confirmed`) | Replaced by a candidate task with `ruling: confirmed` | This keeps one place for the rule that a mandatory finding needs a verdict. |
| `verification.follow_up_spent` | `verification.allowance` | Keeps both the initial and follow-up slots countable across continuations. |
| `record.ledger.requirements` | `requirements` (same row shape) | Moved to the top level of `record`; the fields are unchanged. |
| — | `verification.tasks` | Records what verification was required, carried, and ruled. |

## Record: `implementation-gate-record/2`

`record.json` keeps version 1's top level (`schema`, `profile`, `workflow`, `run`, `status`, `summary`, `items`, `record`). `summary` and `items` are still the validated payload, so `validate_review.py < record.json` still exits 0. Only the `record` section changes:

```jsonc
{
  "schema": "implementation-gate-record/2",
  "profile": "implementation-gate",
  "workflow": "<the activated identifier>",
  "run": { /* unchanged: repository, target_kind "range", target, head, base_ref, base_sha,
              merge_base, context, issues, specs, coverage, merged: false */ },
  "status": "Changes Requested | Incomplete | Needs Information | Approved",
  "summary": { /* validated payload summary, unchanged */ },
  "items": [ /* validated payload items, unchanged: findings and questions with stable ids */ ],
  "record": {
    "repository": "/abs/checkout",
    "paths": {
      "private_dir": "/abs", "store": "/abs/review-context-<head>.json",
      "composition": "/abs/composition.json", "addenda": "/abs/addenda",
      "skill_root": "/abs/skills/review-code",
      "evidence_packet": "/abs/results.md", "spec": "/abs/spec.md"      // optional, caller-supplied
    },
    "requirements": [
      {"source": "issue-329/acceptance-criterion-2", "class": "acceptance",
       "disposition": "met | partial | not-verifiable", "evidence": "path:line …"}
    ],
    "files": [
      {"path": "src/a.py", "state": "reviewed"},
      {"path": "gen/b.py", "state": "ignored", "reason": "generated from src/b.idl, reviewed there"},
      {"path": "src/c.py", "state": "unreviewed"}
    ],
    "check_evidence": [
      {"check": "python3 scripts/test_x.py", "head": "<40-hex>",
       "outcome": "accepted | reviewer-executed | failed | unavailable | historical",
       "reason": "required for reviewer-executed and historical"}
    ],
    "verification": {
      "tasks": [
        {"id": "payments/retry-idempotency", "type": "candidate",
         "trigger": "must-fix | security | data-integrity | destructive-migration | compatibility | prior-must-fix | optional",
         "batch": "initial", "ruling": "confirmed | refuted | unresolved | withheld | pending"},
        {"id": "premise-1", "type": "safety-premise",
         "area": "security | data-integrity | destructive-migration | compatibility | concurrency",
         "premise": "One sentence the no-blocker conclusion depends on.",
         "evidence": "path:line", "batch": "initial",
         "ruling": "holds | fails | unresolved | withheld | pending",
         "reopened_as": "payments/lookup-miss"}                            // a candidate when fails; a question when unresolved
      ],
      "batches": [
        {"name": "initial", "phase": "initial", "bundle": "/abs/initial",
         "raw_return": "/abs/initial/raw-return.json",
         "accounting": "/abs/initial/accounting.json",
         "operation": "Agent run_in_background=false"}
      ],
      "allowance": {"initial_spent": true, "follow_up_spent": false,
                    "carried_from": null},           // or the absolute path of the record/addendum a replacement carried spent flags from
      "outstanding": ["premise-2: follow-up spent before its re-opened candidate could be confirmed"]
    },
    "routed": {"unresolved": [], "disputed": [], "unrecoverable_inputs": []}
  }
}
```

### Validation (composer, version 2)

These checks catch contradictions only; they make no judgments. Kept from version 1:

- file accounting equals the pinned manifest;
- `historical` evidence is never attributed to the reviewed head;
- at most two batches are recorded;
- `unrecoverable_inputs` contradicts `coverage=complete`;
- routed ids name rendered or prior items;
- paths are absolute, and the four keys `private_dir`, `store`, `composition`, and `addenda` are required.

New or changed:

1. **Mandatory confirmation.** A rendered finding that is `must-fix`, or whose `kind` is `security` or `compatibility`, has a candidate task with the same `id`, a mandatory `trigger`, and `ruling: confirmed`. This replaces version 1's `verification: independent-confirmed` check.
2. **Task integrity.** Task ids are unique. Each task `batch` names a recorded batch, or is null when the ruling is `pending`. A task a replacement review carried from its chain instead names `carried:<batch name>` and requires `carried_from`; the carried file holds that batch's bundle, raw return, and accounting. A `withheld` or `pending` task other than `optional` appears in `outstanding`. An `unresolved` safety-premise task appears in `outstanding` or names a rendered question in `reopened_as`.
3. **Allowance.** `initial_spent` is true whenever one or more batches are recorded, and `follow_up_spent` whenever two are. A flag may be true without its recorded batch only when `carried_from` names the earlier record or addendum whose spent allowance a replacement review carried; a flag is never false while its batch is recorded or carried.
4. **Coverage.** Non-empty `outstanding` or an `unreviewed` file contradicts `coverage=complete`. A `fails` premise needs `reopened_as`, naming a rendered item or an `outstanding` entry. An `unresolved` premise with no rendered question contradicts `coverage=complete`.
5. **No premise ledger check.** The composer does not decide whether a premise check was needed. That is the reviewer's judgment about the affected behavior. The composer checks only the internal consistency of the tasks that are present.

The instructions keep the rule that when the conclusion is `Approved` or `Needs Information` on a high-risk change, safety-premise tasks are present or explain the gap in `outstanding`. No script enforces it, because deciding which area a change affects is a judgment.

## Addendum: `implementation-gate-addendum/2`

Written to `addenda/addendum-<final head>.json`. The record and earlier addenda never change, and no script validates an addendum, as in version 1. Fields:

```jsonc
{
  "format": "implementation-gate-addendum/2",
  "workflow": "<identifier of the continuing reviewer>",
  "record": "/abs/record.json",
  "record_format": "implementation-gate-record/1 | implementation-gate-record/2",
  "reviewed_head": "<40-hex: head the record or latest earlier addendum reviewed>",
  "final_head": "<40-hex>",
  "delta": [{"path": "src/a.py", "state": "reviewed | ignored | unreviewed"}],   // `reason` when ignored
  "replaced_by_full_review": null,                // or "/abs/new/record.json"
  "fixed_findings": [{"id": "…", "classification": "fixed | still-open | not-verifiable", "evidence": "path:line"}],
  "findings": [ /* composition-input finding shape */ ],
  "questions": [ /* composition-input question shape */ ],
  "requirements": [ /* only rows whose disposition changed at the final head, record-row shape */ ],
  "check_evidence": [ /* record shape; results carried forward keep their original head */ ],
  "verification": {
    "tasks": [ /* new tasks this continuation dispatched or left outstanding */ ],
    "batches": [ /* batches this continuation dispatched */ ],
    "allowance": {"initial_spent": true, "follow_up_spent": true},   // cumulative as of final_head
    "outstanding": [ /* cumulative as of final_head */ ]
  },
  "status": "…", "coverage": "complete | incomplete", "coverage_gaps": ["…"],
  "routed": { /* cumulative as of final_head, record shape */ }
}
```

The current state at the final head is: the record, then each addendum in `reviewed_head` → `final_head` order, applying `fixed_findings` and the new items. `status`, `coverage`, `outstanding`, `routed`, and `allowance` are always the latest addendum's values. A continuation reads the latest addendum for these and never recomputes them from scratch.

Unresolved state that must survive a fix or worker change:

- open findings: rendered and not classified `fixed`;
- open questions;
- `routed.unresolved` and `routed.disputed`;
- `outstanding` verification;
- the allowance;
- per-file coverage for files the delta did not reach.

## Version transition

A continuation run under version-2 instructions may meet a version-1 chain: a record written before activation, possibly with `implementation-gate-addendum/1` files. It handles the chain this way:

1. **Validate the chain.** Check that the record `schema` and each addendum `format` are known, the `repository` matches, and the head chain is unbroken (each `reviewed_head` equals the previous head). A missing file, an unknown format, or a broken chain is **rejected as incomplete**. The continuation reports the missing or mismatched state as a coverage gap and returns `Incomplete`. It does not start over.
2. **Map version-1 state.** Open items are the record's `items` plus every version-1 addendum's `findings` and `questions`, in chain order; an id leaves the open set only when a later `fixed_findings` entry classifies it `fixed`. `routed` carries over as is. The spent allowance is the number of batches recorded across the record and every version-1 addendum: one or more means `initial_spent`, two means `follow_up_spent`. A version-1 addendum's `follow_up_spent: true` also sets it. Nothing resets the allowance, and a reinterpretation never grants a batch.
3. **Carry obligations.** Version-1 `outstanding` entries carry over verbatim.
4. **Resolve the clean-verdict obligation.** A version-1 `clean_verdict: outstanding` becomes one outstanding entry, `v1-clean-verdict`. The continuation either discharges it with safety-premise tasks within the remaining allowance, when the final-head review touches a high-risk area, or closes it as `superseded-by-v2-policy` with the reason recorded in `coverage_gaps`. Closing it never records a `stands` verdict. Candidate rows with `independent-confirmed` count as `confirmed` candidate tasks. Other ledger rows are ignored, because version 2 has no ledger.
5. **Write version 2.** The continuation writes `implementation-gate-addendum/2` with `record_format: implementation-gate-record/1`. A full replacement review writes a new version-2 record, carries forward the open state from step 2, sets the spent flags from step 2 with `allowance.carried_from` naming the latest chain file, and carries each confirmed candidate task from step 4 with `batch: carried:<batch name>`, so its rendered finding keeps the confirmation rule 1 requires without re-recording the chain's batches.

A version-2 reviewer never writes a version-1 file. A version-1 reviewer handed a version-2 chain rejects it as incomplete under its existing rule for missing or mismatched state.

## Consumers of each retained field

| Field | Consumer | Purpose |
| --- | --- | --- |
| `schema`, `workflow`, `run.*` | continuation, `implement-publish` step 5 | head chain, identity, and head of the pull-request body |
| `status`, `summary`, `items` | `implement-publish` step 4, continuation, `validate_review.py` | gate decision, open findings, payload validation |
| `requirements` | `implement-publish` step 5 (issue closes / partially implements), continuation | requirement outcomes, and the spec-fit rows to re-check after fixes |
| `files` | composer (manifest match), continuation | per-file coverage; which files the delta leaves unreviewed |
| `check_evidence` | `implement-publish` step 5 verification summary, continuation | evidence used; retention and invalidation after fixes |
| `verification.tasks` | composer (mandatory confirmation), continuation | what was verified; which obligations remain |
| `verification.batches` | continuation, `run_events.py` summary (by bundle path) | audit trail; timing join |
| `verification.allowance` | continuation | remaining batches |
| `verification.outstanding` | composer (coverage), `implement-publish` step 4 gate | incomplete required work |
| `routed` | `implement-publish` step 4, continuation | disputed blockers, questions, unrecoverable inputs |
| `paths.*` | continuation, `implement-publish` | fresh-worker discovery, evidence packet, spec |
