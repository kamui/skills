# Versioned conformance

Read this reference only when the rubric's Issue fit section sends you here: an issue, the pull-request text, or a repository convention makes the change conform to a versioned artifact — a stub, binding, or SDK tracking a package release; a schema; a generated source and its generator input. It adds a third ledger source to the rubric's two, and the verifier and coverage rules that source needs. Nothing here changes the admission gates.

## Rows

The artifact is a third row source, read after the pull-request text. Obtain its pinned version, or the delta between the pinned versions when the change is a bump, and take the export surface or diff — a compare, an export list, a changelog's API section, a generated-symbol list — rather than the artifact tree file by file. List one row per public addition, removal, rename, and changed signature or field inside that surface, at `artifact-<identity>@<version or range>/<path>:<name>`, class acceptance requirement. Public means exported, documented, or un-underscored at module level. Private internals, incidental mentions in tests or prose, and anything a repository convention explicitly tolerates — an annotation the convention says to widen, an omission it permits — produce no obligation; record the tolerating convention's coordinate once. A tolerated widening is not a missing-name candidate, and is a candidate only on its own consequence under the ordinary gates.

Locate each obligation with one batched search over the whole consuming tree, unchanged files included. The search is a locator, not proof: a hit or a miss settles nothing until the reviewer reads the bounded definition it points at, or the alias, re-export, conditional or platform-guarded export, and documented-exception sites that could supply the name, and compares the signature or fields against the artifact. A demonstrated omission or contradiction is `partial` and an ordinary `kind=requirement` candidate with `Source` at its `artifact-` coordinate; that the consumer never carried the name, or that its file is untouched, is not a refutation when this change owns conformance. A `met` row stays one line: the name, its coordinate, and the consumer pointer.

## An artifact the reviewer cannot obtain

It is an unrecoverable input under the rubric's Uncertainty routing: list no rows for it, never assemble the surface from the submitted diff, and name under `Coverage gaps` the artifact and the consumer surfaces its enumeration would have covered. When the orchestrator supplies it, enumerate the rows and run only their dispositions.

## Verifier brief

When a candidate in a batch cites an `artifact-` coordinate, the brief adds the pinned artifact version or delta location to the candidate-mode inputs, and the candidate's citations carry both the artifact-side line and the consumer-side sites inspected: the definition, alias, re-export, or conditional-export sites read, or the search and sites that supplied nothing. The verifier's step 4 then reads the artifact line and the consumer's alias, re-export, and conditional-export sites itself: a name the consumer supplies under another spelling or guard refutes with basis `contradicted`, and a name the search did not find is confirmed only after those sites are read.
