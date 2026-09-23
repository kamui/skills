# Verifier return encoding

Worker instructions: `build_verifier_prompt.py` embeds what applies of this file in a verifier brief, so the primary reviewer does not read it.

Encode your return as one JSON object and deliver it by the transport section below. This is an encoding of `verifier.md`'s verdicts and rulings, not an additional decision policy. Read the supplied `manifest.json` and echo its exact file SHA-256 as `manifest_sha256` (compute with Python's `hashlib.sha256(Path(...).read_bytes()).hexdigest()`). Every candidate and premise ID is owed exactly one record **in its own array**.

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
  "premises": [
    {
      "id": "premise-1",
      "ruling": "holds",
      "evidence": [{"coordinate": "src/queue.py:19", "text": "if not queue: return"}]
    }
  ],
  "duplicate_groups": [],
  "observation": null
}
```

Candidate records require `id`, `verdict`, `basis`, and a nonempty `evidence` array. `verdict` is `confirmed` or `refuted`. A confirmation's basis is its decisive justification. A refutation's basis is exactly `contradicted`, `prevented`, `intentional`, `pre-existing` (Code only), `no-consequence`, or `unresolved`; `unresolved` also requires `settling_fact`, naming the single fact and its supplier. Other verdicts, confidence scores, and audit-skill basis names are invalid.

Optional `corrections` contains only `trigger`, `impact`, `priority`, `action`, `anchor`, `fix`, and `change`, with the same types as the supplied candidate. Safety rulings stay inside their candidate record as `safety_rulings`: an array of objects with `path`, `conditions`, `premise`, `ruling` (`holds`, `fails`, or `unresolved`), and nonempty `evidence`. Keep steady-state traces and the opposite-branch procedure's decisive citations here. A scoped correction never silently changes the finding's remedy: the primary still falsifies the scope dispute.

Premise records require `id`, `ruling` (`holds`, `fails`, or `unresolved`), and nonempty `evidence`. A `fails` also requires `failed_step`, naming the step that reaches the failing state transition; an `unresolved` requires `settling_fact`, naming the single fact and its supplier. A candidate verdict never substitutes for a premise ruling. There is no batch conclusion.

`duplicate_groups` is an array of arrays, each suggesting at least two supplied candidate IDs for merging; the primary decides. `observation` is `null` or one object with `fact` and nonempty `evidence`, subject to the reference's non-actionable aside rule. Safety assertions and premise contradictions stay in their records, never the aside.

Evidence entries are `{"coordinate": "<source location>", "text": "<decisive raw evidence>"}` or `{"unavailable": "<named evidence gap>"}` (optionally retaining `coordinate`). Source coordinates include `commit-<sha7>/"<quoted phrase>"` for a local change-description requirement, alongside the pull-request `pr-title` and `pr-body` forms. Preserve quoted evidence, including strings such as `support: enabled`. Named unavailable evidence never becomes confirmation or safety merely because it fits this encoding: every record cites at least one raw location unless it is `unresolved` — a refutation with basis `unresolved`, or an `unresolved` premise — and the accounting withholds one that does not. The accounting helper checks membership, vocabulary, structure, and identity; the verifier and primary still decide citation truth, sufficient evidence, scoped safety, observation eligibility, and the current coverage/status rules.

## Inline transport

Return the JSON object as your whole response, without a Markdown fence or surrounding prose.

## File transport

Save the complete JSON object, unfenced, to the assigned return file below by exclusive create, such as Python's `open(path, "x", encoding="utf-8")`. That is your only write: no other file, source change, or forge write. Then respond with only `{"return_file": "<the assigned absolute path>", "status": "complete"}`. If the file exists or the write fails, leave what was written, write nowhere else, and return the complete JSON object inline as your whole response instead.
