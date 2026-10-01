# Metering evidence — issue #137

Everything the cost tables in [`comparison-data.md`](../comparison-data.md) §7 and the totals in
[`ledger.md`](../ledger.md) rest on, committed so that every dollar in the bundle recomputes from
files in the repository rather than from transcripts that live only on one machine.

## What is here

Two files per reviewer attempt, under `cells/`, and two per helper session, under `helpers/`:

- `<name>-meta.json` (attempts) or `<name>-usage.json` (helpers) — the complete JSON output of
  `transcript_usage.py --prices 2,10 --json` over the session root and every sub-agent transcript:
  per-transcript and total token counts split by cache tier, the priced cost with its bounds, the
  agent-span sum, and for attempts the `timing` object from the #130 sidecar. Attempt files also
  carry `close_cell.py`'s per-agent scan (`agents[]`: transcript path, definition, assistant-line
  count, and the set of `model` and `effort` values observed on those lines) and its `problems`
  list, empty for all 24.
- `<name>-requests.jsonl` — **one record per unique API request**: request id, message id, which
  transcript it came from, `model`, `effort`, first and last timestamp, and the usage fields the
  billing arithmetic uses (`input_tokens`, `cache_creation_input_tokens` with its `cache_write_5m`
  and `cache_write_1h` split, `cache_read_input_tokens`, `output_tokens`, `thinking_tokens`,
  `service_tier`). A streamed request appears on several assistant lines with identical usage; the
  record keeps the maximum of every counter, which is the de-duplication rule `transcript_usage.py`
  applies, so summing a file reproduces the CLI's totals. The extractor is quoted in
  [`tooling.md`](../tooling.md).

The raw transcripts themselves — 36 for the cells (51 MB) and 28 for the helpers (21 MB) — are not
committed. They remain on the machine that ran the grid under the session ids recorded in
`ledger.md` and in each `meta.json`'s `agents[].path`; the per-request files above carry every
field from them that any number in this bundle depends on, and the model/effort evidence the
verification claims rest on.

## Reconciliation

Each attempt's cost recomputed from its `requests.jsonl` at the frozen prices (input $2/M, 5-minute
cache write ×1.25, 1-hour cache write ×2.0, cache read ×0.1, output $10/M) against the metering
CLI's figure in its `meta.json`. All 24 agree to the cent.

| Attempt | Requests | Transcripts | CLI cost | Recomputed |
| --- | --- | --- | --- | --- |
| `i-867cf3ff-seed1-att-02` | 129 | 2 | $7.02 | $7.02 |
| `i-867cf3ff-seed2-att-03` | 103 | 2 | $5.66 | $5.66 |
| `i-bea6be14-seed1-att-01` | 79 | 2 | $4.50 | $4.50 |
| `i-bea6be14-seed2-att-04` | 81 | 2 | $4.22 | $4.22 |
| `j-867cf3ff-seed1-att-10` | 52 | 1 | $2.34 | $2.34 |
| `j-867cf3ff-seed2-att-11` | 50 | 1 | $2.20 | $2.20 |
| `j-bea6be14-seed1-att-09` | 42 | 1 | $2.02 | $2.02 |
| `j-bea6be14-seed2-att-12` | 48 | 1 | $2.22 | $2.22 |
| `k-867cf3ff-seed1-att-18` | 42 | 1 | $1.97 | $1.97 |
| `k-867cf3ff-seed2-att-19` | 47 | 1 | $2.16 | $2.16 |
| `k-bea6be14-seed1-att-17` | 51 | 1 | $2.21 | $2.21 |
| `k-bea6be14-seed2-att-20` | 45 | 1 | $2.21 | $2.21 |
| `l-867cf3ff-seed1-att-14` | 49 | 2 | $2.54 | $2.54 |
| `l-867cf3ff-seed2-att-15` | 78 | 2 | $3.96 | $3.96 |
| `l-bea6be14-seed1-att-13` | 60 | 2 | $2.98 | $2.98 |
| `l-bea6be14-seed2-att-16` | 83 | 2 | $4.31 | $4.31 |
| `m-867cf3ff-seed1-att-06` | 58 | 2 | $2.86 | $2.86 |
| `m-867cf3ff-seed2-att-07` | 63 | 1 | $2.46 | $2.46 |
| `m-bea6be14-seed1-att-05` | 86 | 2 | $4.61 | $4.61 |
| `m-bea6be14-seed2-att-08` | 132 | 2 | $6.78 | $6.78 |
| `n-867cf3ff-seed1-att-22` | 56 | 1 | $2.21 | $2.21 |
| `n-867cf3ff-seed2-att-23` | 53 | 2 | $2.58 | $2.58 |
| `n-bea6be14-seed1-att-21` | 49 | 1 | $2.45 | $2.45 |
| `n-bea6be14-seed2-att-24` | 50 | 1 | $2.53 | $2.53 |
| **Total, 24 cells** | 1586 | 36 | **$78.99** | **$78.99** |

Helper sessions — the vetting hunts (including the discarded S3), the six pre-dispatch ground-truth
adjudicators, the six blind scorers, and the post-grid GT-n1 adjudication — metered the same way:

| Helper | Transcripts | Requests | Cost |
| --- | --- | --- | --- |
| `S3-hunt-changed-test-discarded` | 5 | 191 | $3.29 |
| `S4-hunt-ordinary` | 1 | 66 | $3.00 |
| `S5-hunt-crossfile` | 7 | 369 | $8.82 |
| `S6-hunt-clean-highrisk` | 1 | 65 | $1.90 |
| `S7-hunt-changed-test` | 1 | 96 | $2.66 |
| `S8-adjudicator-i` | 1 | 39 | $1.09 |
| `S8-adjudicator-j` | 1 | 66 | $1.59 |
| `S8-adjudicator-k` | 1 | 38 | $0.64 |
| `S8-adjudicator-l` | 1 | 41 | $1.00 |
| `S8-adjudicator-m` | 1 | 62 | $1.22 |
| `S8-adjudicator-n` | 1 | 51 | $1.22 |
| `adjudication-gt-n1` | 1 | 16 | $0.39 |
| `scorer-i` | 1 | 16 | $0.71 |
| `scorer-j` | 1 | 17 | $0.67 |
| `scorer-k` | 1 | 7 | $0.44 |
| `scorer-l` | 1 | 8 | $0.59 |
| `scorer-m` | 1 | 17 | $0.63 |
| `scorer-n` | 1 | 12 | $0.62 |
| **Total, 18 helper sessions** | | | **$30.48** |

Ticket total from these files: $78.99 cells + $30.48 helpers =
**$109.47**, which is the figure in the ledger's close-out table. The
ledger's setup rows quote the same helper costs individually; the harness's own self-reported
totals, where they differ, are noted beside them there and are not used.
