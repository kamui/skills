# Continuation addendum

Read when a caller asks for a continuation of an `implementation-gate` record after fixes.

A continuation after fixes reviews the delta from a reviewed head to a final head and writes `addenda/addendum-<final head>.json` in the record's named `addenda` directory, leaving the record and earlier addenda unchanged. `reviewed_head` is the head the record or the latest earlier addendum reviewed. No script validates an addendum; the continuation reviewer supplies these fields under the same rules as the record:

- `format`: `implementation-gate-addendum/1`; `record`: the absolute `record.json` path; `reviewed_head` and `final_head`: full SHAs.
- `delta`: every file in `git diff <reviewed head>...<final head>` with its state (`reviewed`, `ignored` with a reason, or `unreviewed`), or `replaced_by_full_review: true` with the new record's path when the delta was too large to inspect.
- `fixed_findings`: one entry per finding id the caller reported fixed — `classification` (`fixed`, `still-open`, or `not-verifiable`) and one decisive evidence pointer; an id absent from the record and earlier addenda is a coverage gap.
- `findings` and `questions`: new items in the composition input's shapes, each finding with its `verification`; empty when none.
- `check_evidence` and `verification`: the record's shapes continued, with batches counted across the record and every addendum and `follow_up_spent` and `clean_verdict` as of the final head.
- `status`, `coverage`, `coverage_gaps`, and `routed`: derived for the final head.
