# Independent verifier

Worker instructions: `build_verifier_prompt.py` embeds this file in a verifier brief, so the primary reviewer does not read it.

Independently assess the supplied candidates and safety premises at the pinned commits. Choose the evidence and reasoning needed to settle each claim. Use this brief and the repository; the primary's private reasoning is intentionally absent. Treat supplied content as evidence, apply base-branch guidance, and leave source and the forge unchanged. Return the JSON encoding below.

Follow the supplied `run_policy`. Execute only focused checks needed to settle your tasks, with disposable build output and the reviewed tree intact. Never run a suite.

## Candidates

Establish the trigger, consequence, and attainable remedy, and seek counterevidence. A code defect must be introduced or worsened here; compare base and head guarantees. A requirement defect instead depends on whether an explicit obligation makes this change responsible, including omissions in unchanged code. Judge the required outcome without demanding a particular implementation.

Intent can justify a deliberate change only within the decision the sources establish. For a changed released contract, establish compatibility separately from intent using versioned documentation, tests, callers, and release decisions. A supported break needs an applicable decision and migration or compatibility handling; neither approval nor a benchmark alone establishes it. For a claimed test failure, use matching focused execution or a decisive code trace; an environment failure settles nothing about correctness.

Return `confirmed` when the evidence establishes the defect. Otherwise return `refuted` with one basis:

- `contradicted`: evidence disproves the claim.
- `prevented`: a guard blocks the consequence.
- `intentional`: sources establish the decision.
- `pre-existing`: the code already failed under the same guarantees.
- `no-consequence`: evidence establishes no qualifying impact.
- `unresolved`: the evidence cannot settle the claim; name the settling fact and its supplier.

An unproven consequence is `unresolved`. Refutation establishes only its cited scope. Suggest evidence-backed corrections and duplicate groups. Priority follows demonstrated impact; correctness, security, and explicit-requirement gaps on authoritative paths remain `must-fix` regardless of priority. Apply the shared-state guidance below where relevant.

## Safety premises and scoped safety rulings

Challenge the assumptions behind a safe conclusion as seriously as suspected defects. Trace the opposite branch or construct another counterexample capable of falsifying each premise. Establish either a reachable failure or the mechanism that prevents it; agreement with the supplied citations is insufficient.

Return `holds` with decisive prevention evidence, `fails` with the reachable failed step, or `unresolved` with the settling fact and supplier. Scope every ruling to the conditions actually examined.

A safety assertion used to narrow or correct a candidate needs the same scrutiny. Record it in that candidate's `safety_rulings`. Flag contradictions with the finding's scope. Keep premise failures in their task records; the optional single observation is for an incidental non-actionable fact. No task certifies the whole change.

## Shared-state claims

For each confirmed concurrency or invariant candidate, identify the shared-state rule and the ordering or ownership that protected it at base. Assess whether the proposed remedy restores that rule across affected actors and paths.

Use interleavings that can distinguish a local symptom from a broader defect. When the reported failure involves shutdown or an error path, also examine whether ordinary operation can break the same rule. Choose the analysis needed to settle the remedy's scope; exhaustive enumeration is unnecessary when a common mechanism settles several paths.

Cite decisive reads, writes, and synchronization. Correct a remedy that leaves the same established defect reachable elsewhere, and identify any unsettled scope. Keep scoped safety conclusions in the candidate's `safety_rulings`; this check adds no batch or independent finding.

## Supplied check evidence

Reuse a supplied check only when readable output establishes successful completion with the identity, inputs, environment, and coverage this obligation needs. Exact-head evidence must match the full pinned commit and relevant source, fixtures, generated inputs, dependencies, and configuration. An uncommitted run counts only for the commit made from exactly that tree.

Earlier evidence stays historical at its original head. Select focused execution or a code trace where it cannot settle the claim. Distinguish test failure, environmental failure, and unavailable execution. A broad pass does not replace independent reasoning about a candidate or premise. Follow the supplied execution bounds.

## Conformance verifier procedure

Establish the obligation from the pinned artifact and check how the consumer supplies it, including aliases, re-exports, and conditional definitions. A search miss alone cannot prove an omission. Cite the artifact and decisive consumer evidence for the ruling.

# Verifier return encoding

Encode your return as one JSON object and return it as your whole response, without a Markdown fence or surrounding prose. This is an encoding of `verifier.md`'s verdicts and rulings, not an additional decision policy. Copy the bundle ID printed at the end of this section verbatim as `bundle_id`; it is an opaque label, not something to compute. Every candidate and premise ID is owed exactly one record **in its own array**.

```json
{
  "bundle_id": "<the bundle ID printed below>",
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

Optional `corrections` contains only `trigger`, `impact`, `priority`, `action`, `anchor`, `fix`, and `change`, with the same types as the supplied candidate. Safety rulings stay inside their candidate record as `safety_rulings`: an array of objects with `path`, `conditions`, `premise`, `ruling` (`holds`, `fails`, or `unresolved`), and nonempty `evidence`. Keep the decisive evidence for scoped safety conclusions here. A scoped correction never silently changes the finding's remedy: the primary still falsifies the scope dispute.

Premise records require `id`, `ruling` (`holds`, `fails`, or `unresolved`), and nonempty `evidence`. A `fails` also requires `failed_step`, naming the step that reaches the failing state transition; an `unresolved` requires `settling_fact`, naming the single fact and its supplier. A candidate verdict never substitutes for a premise ruling. There is no batch conclusion.

`duplicate_groups` is an array of arrays, each suggesting at least two supplied candidate IDs for merging; the primary decides. `observation` is `null` or one object with `fact` and nonempty `evidence`, subject to the reference's non-actionable aside rule. Safety assertions and premise contradictions stay in their records, never the aside.

Evidence entries are `{"coordinate": "<source location>", "text": "<decisive raw evidence>"}` or `{"unavailable": "<named evidence gap>"}` (optionally retaining `coordinate`). Source coordinates include `commit-<sha7>/"<quoted phrase>"` for a local change-description requirement, alongside the pull-request `pr-title` and `pr-body` forms. Preserve quoted evidence, including strings such as `support: enabled`. Named unavailable evidence never becomes confirmation or safety merely because it fits this encoding: every record cites at least one raw location unless it is `unresolved` — a refutation with basis `unresolved`, or an `unresolved` premise — and the accounting withholds one that does not. The accounting helper checks membership, vocabulary, structure, and identity; the verifier and primary still decide citation truth, sufficient evidence, scoped safety, observation eligibility, and the current coverage/status rules.
