# Verifier return encoding

Return one JSON object, without a Markdown fence or surrounding prose. This is an encoding of `verifier.md`'s verdicts and rulings, not an additional decision policy. Read the supplied `manifest.json` and echo its exact file SHA-256 as `manifest_sha256` (compute with Python's `hashlib.sha256(Path(...).read_bytes()).hexdigest()`). Every candidate and ledger ID is owed one record **in its own array**, even when the same ID appears in both roles.

```json
{
  "manifest_sha256": "<SHA-256 of the supplied manifest file>",
  "candidates": [
    {
      "id": "retry/duplicate-charge",
      "verdict": "confirmed",
      "basis": "The changed retry path creates a new key for the same charge.",
      "evidence": [{"coordinate": "src/retry.py:42", "text": "key = new_key()"}],
      "corrections": {"change": "Retain the key for the entire logical charge."},
      "safety_rulings": []
    }
  ],
  "ledger": [
    {
      "id": "retry/empty-queue",
      "ruling": "holds",
      "evidence": [{"coordinate": "src/queue.py:19", "text": "if not queue: return"}]
    }
  ],
  "duplicate_groups": [],
  "observation": null
}
```

Candidate records require `id`, `verdict`, `basis`, and a nonempty `evidence` array. `verdict` is `confirmed` or `refuted`. A confirmation's basis is its decisive justification. A refutation's basis is exactly `contradicted`, `prevented`, `intentional`, `pre-existing` (Code only), `no-consequence`, or `unresolved`; `unresolved` also requires `settling_fact`, naming the single fact and its supplier. Other verdicts, confidence scores, and audit-skill basis names are invalid.

Optional `corrections` contains only `trigger`, `impact`, `priority`, `action`, `anchor`, `fix`, and `change`, with the same types as the supplied candidate. Safety rulings stay inside their candidate record or ledger ruling as `safety_rulings`: an array of objects with `path`, `conditions`, `premise`, `ruling` (`holds`, `fails`, or `unresolved`), and nonempty `evidence`. Keep steady-state traces and the opposite-branch procedure's decisive citations here. A scoped correction never silently changes the finding's remedy: the primary still falsifies the scope dispute.

Ledger records require `id`, `ruling` (`holds` or `re-open`), and nonempty `evidence`. A `re-open` also requires `failed_step`, naming the contradicted/unsupported premise or missing settling fact. Its meaning is `disposition <id> does not hold; re-open it`. Neither a candidate verdict nor a batch conclusion substitutes for a row ruling.

Only `complete-ledger` mode requires a `conclusion` field. Encode its one batch conclusion as `"clean verdict stands"` when every supplied ledger ruling is `holds`, or `{"re_open": ["<id>", "<id>"]}` listing exactly the re-opened ledger IDs. An empty complete ledger still returns `"clean verdict stands"`. Candidate-only and related-acquittal modes omit `conclusion`; mixed batches apply their selected ledger mode only to the ledger portion.

`duplicate_groups` is an array of arrays, each suggesting at least two supplied candidate IDs for merging; the primary decides. `observation` is `null` or one object with `fact` and nonempty `evidence`, subject to the reference's non-actionable aside rule. Safety assertions and ledger contradictions stay in their records, never the aside.

Evidence entries are `{"coordinate": "<source location>", "text": "<decisive raw evidence>"}` or `{"unavailable": "<named evidence gap>"}` (optionally retaining `coordinate`). Preserve quoted evidence, including strings such as `support: enabled`. Named unavailable evidence never becomes confirmation or safety merely because it fits this encoding. The accounting helper checks membership, vocabulary, structure, and identity; the verifier and primary still decide citation truth, sufficient evidence, scoped safety, observation eligibility, and the current coverage/status rules.
