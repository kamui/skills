# Continuation addendum

Read when a caller asks for a continuation of an `implementation-gate` record after fixes.

A continuation after fixes reviews the delta from a reviewed head to a final head and writes `addenda/addendum-<final head>.json` in the record's named `addenda` directory, leaving the record and earlier addenda unchanged. `reviewed_head` is the head the record or the latest earlier addendum reviewed. No script validates an addendum; the continuation reviewer supplies these fields under the same rules as the record:

- `format`: `implementation-gate-addendum/2`; `workflow`: the continuing reviewer's identifier; `record`: the absolute `record.json` path; `record_format`: that record's `schema`; `reviewed_head` and `final_head`: full SHAs.
- `delta`: every file in `git diff <reviewed head>...<final head>` with its state (`reviewed`, `ignored` with a reason, or `unreviewed`). `replaced_by_full_review` is `null`, or the new record's absolute path when the delta was too large to inspect.
- `fixed_findings`: one entry per finding id the caller reported fixed — `id`, `classification` (`fixed`, `still-open`, or `not-verifiable`), and one decisive `evidence` pointer; an id absent from the record and earlier addenda is a coverage gap.
- `findings` and `questions`: new items in the composition input's shapes; empty when none.
- `requirements`: only the rows whose disposition changed at the final head, in the record's row shape.
- `check_evidence`: the record's shape; results carried forward keep their original head.
- `verification`: `tasks` and `batches` this continuation added, in the record's shapes; `allowance` (`initial_spent`, `follow_up_spent`) and `outstanding` cumulative as of the final head. A new finding under a mandatory trigger needs its `confirmed` candidate task here, within the remaining allowance.
- `status`, `coverage`, `coverage_gaps`, and `routed`: derived for the final head, with `routed` cumulative.

## Current state of a chain

The state at the final head is the record, then each addendum in `reviewed_head` → `final_head` order. An item is open from the record's `items` or any addendum's `findings` or `questions` until a later `fixed_findings` entry classifies it `fixed`. `status`, `coverage`, `outstanding`, `routed`, and `allowance` are the latest addendum's values; read them, never recompute them from scratch. Per-file coverage the delta did not reach stays as the record or an earlier addendum left it. Open findings and questions, `routed.unresolved` and `routed.disputed`, `outstanding`, and the spent allowance survive every fix and every worker change.

Before continuing, validate the chain: the record `schema` and each addendum `format` are known, the `repository` matches, and each `reviewed_head` equals the previous head. A record with `finalization` must also pass `python3 scripts/finalize_review.py --check --profile implementation-gate <record directory>`: a known protocol whose report exists. A record without it predates the report and keeps these checks. A missing file, an unknown format, or a broken chain is rejected as incomplete: report the missing or mismatched state as a coverage gap and return `Incomplete`. Never start over, and never reset the allowance.

## Replacement record

When the delta is too large to inspect, run a full base-to-final-head review into a new `implementation-gate-record/2`, and write the addendum with `replaced_by_full_review` naming it; later continuations continue from the new record. The new record carries the chain's current state:

- **Open state.** Every open finding and question, `routed`, and every `outstanding` entry.
- **Allowance.** The spent flags as the chain left them, with `verification.allowance.carried_from` naming the latest chain file by absolute path. Its own batches spend only what those flags leave.
- **Confirmations.** Each `confirmed` candidate task whose finding is still open, with `batch` rewritten to `carried:<chain file>#<batch name>`, where the chain file is the absolute path of the record or addendum whose `verification.batches` holds that batch. Never copy a bare batch name: it would resolve against the replacement's own batches. The composer reads that chain file and batch's accounting report, and refuses a carried confirmation they do not establish. A carried task keeps its `trigger`.

## Version 1 chains

A record or addendum written before workflow `v5b-23` is version 1 (`implementation-gate-record/1`, `implementation-gate-addendum/1`). Map it into the state above; never write a version-1 file.

1. **Open items.** The record's `items` plus every addendum's `findings` and `questions`, in chain order, as above. `routed` and version-1 `outstanding` entries carry over verbatim.
2. **Allowance.** Count the batches recorded across the record and every addendum: one or more sets `initial_spent`, two sets `follow_up_spent`. A version-1 `follow_up_spent: true`, or a version-2 addendum's `allowance`, also sets it. A reinterpretation never grants a batch.
3. **Clean verdict.** A version-1 `clean_verdict: outstanding` becomes the outstanding entry `v1-clean-verdict`. Discharge it with safety-premise tasks within the remaining allowance when the final-head review touches a high-risk area; otherwise close it as `superseded-by-v2-policy` with the reason in `coverage_gaps`. Never record it as `stands`.
4. **Confirmations.** A version-1 candidate row, or a finding a version-1 addendum added, whose `verification` is `independent-confirmed` counts as a `confirmed` candidate task naming the batch in that file whose raw return confirmed it. Its trigger is `must-fix` for a `must-fix` finding, the finding's `kind` when that is `security` or `compatibility`, and `optional` otherwise. A confirmation whose file records no batch is not carried: that finding needs confirmation again within the allowance, or stays in `outstanding`. Other version-1 ledger rows are ignored.

An addendum over a version-1 chain is `implementation-gate-addendum/2` with `record_format: implementation-gate-record/1`; a full replacement is a version-2 record built from the mapped state under Replacement record.
