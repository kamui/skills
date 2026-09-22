# Review record

The review is **human-readable, agent-actionable, and mechanically correlatable**. Visible prose is authoritative. Hidden trailers speed up re-review and automated addressing but never gate understanding; human comments without trailers receive the same semantic treatment.

## Finding comment

The title, trigger, impact, and change must make sense without the trailer. A finding states exactly one non-empty `Triggers when`, `Impact`, and `Change`, in that order, before an optional `Source`. Whether a field's text is sufficient stays the reviewer's judgment. Omit `Source` unless an issue, a change-description promise at its ledger coordinate, a versioned artifact's obligation at its `artifact-` ledger coordinate, or a repository rule materially supports the finding. `priority` and `action` are separate fields under the rubric's Priorities and blocking section: a `must-fix` finding is blocking, and a `consider` finding is optional, so closing it without action is a correct response. Non-actionable observations use the summary-only form below rather than a finding comment.

The forge anchor and the repair site may differ. The inline API fields identify the changed-line `anchor`; an optional `fix` site identifies where the author or agent should edit. Omit `fix` when it is the anchor. Name a different fix site in the visible `Change` text as well, because the trailer is never authoritative.

Stable ids describe the path and defect concept, never a line number. Keep the same id while the same defect survives across heads.

Kinds are compact internal routing aids: `bug`, `compatibility`, `concurrency`, `invariant`, `security`, `performance`, `maintainability`, or `requirement`. `compatibility` identifies the released-contract candidates defined by the rubric's Issue fit section. Use `concurrency` or `invariant` when sibling paths share the broken state rule and therefore require the verifier's bug-class check. They do not need a visible axis tag.

## Comment quality

One comment per distinct defect, under a short imperative title, anchored on the smallest honest changed range or changed file that identifies it, in a matter-of-fact tone: `Change` states the outcome to implement, not an instruction to investigate, and a person or agent can act on the comment without opening another document. Keep an ordinary finding to roughly 160 words before its trailer and at most two decisive evidence facts; exceed that only when the extra context prevents a materially wrong fix.

For drift proven by several equally honest changed lines, anchor the changed line that states the rule being drifted from; if more than one remains, choose the lexicographically first path, then the smallest range. Never attach a finding to an unrelated changed line merely to obtain an inline comment; a file-anchored finding renders in the summary body when the forge cannot carry it inline.

Use a suggestion block only for a small exact replacement that completely fixes the finding, preserving indentation and diff side; otherwise request the behavior in prose rather than guessing a patch.

## Question comment

Ask only when the rubric's Material questions rule is met: no static evidence could settle the fact, and `Why it matters` names the correctness outcome, acceptance criterion, compatibility or release obligation, or present merge decision the answer changes. A question about a recorded deferral also names, in `Evidence`, the deferral's author and comment, the surface, and the current decision. A question is not a finding, has no priority, requests no code change, and states who or what measurement can answer it. Whole-change questions belong in the review body rather than on an arbitrary line.

When a verified candidate becomes a question because its settling fact is statically unresolvable, retain its stable concept id and change only its item type from finding to question. This keeps later answers and any code-decided finding correlated across runs.

## Observations

`Observations` is a bounded summary-body channel for accurate, non-actionable facts that meet the rubric's route. It is separate from findings and questions: observations have no priority, action, stable id, trailer, or anchor comment and never affect status. Publish at most three, each as one sentence followed by one decisive evidence pointer. Use descriptive language without `should` or `must`.

When more than three qualify, publish the three with the most decisive evidence and record each of the rest in the private record as `observation (unpublished, cap)`. A fact belongs to exactly one channel: an unpublished observation and a verifier aside stay in that record rather than folded into a finding's `Impact` or `Change` prose.

Do not create an observation merely to preserve a dropped candidate. The fact itself must stand, and it must have failed finding admission on consequence or arrived as a verifier aside.

## Status

Derive one semantic status after findings, questions, coverage, and prior state are complete:

1. `Changes Requested` when any `must-fix` finding is unsettled, including a disputed or not-verifiable blocker.
2. `Incomplete` when no blocker is known but material coverage or verification did not finish.
3. `Needs Information` when coverage is complete and an unanswered question could change the verdict. A recorded deferral or `not-verifiable` row that the rubric published no question for contributes nothing to this status.
4. `Approved` otherwise. `consider` findings do not prevent approval.

A missing issue required by the repository workflow is a material question: with otherwise complete coverage and no unsettled must-fix finding it yields `Needs Information`, never `Incomplete` for that reason alone.

## Review identity

`workflow=v5b-22` versions this package's review behavior. Increment it whenever admission, verification, rendering, or state semantics change.

Compute `context` once, with `python3 scripts/context_fingerprint.py --packet packet.json --guidance-base <base SHA> --store <store>` on a pull request, where `pr` and `issues` come from the packet step 1 normalized, and without `--packet` on a local target or a forge without that packet, supplying `pr` and `issues` directly from the exact reviewed inputs. Stdin carries the rest of the input (`--example` prints its shape; omit its `guidance`); the script derives `guidance`, the base-branch instruction files that apply to the changed paths, itself. For a local range, `pr` is `{title: <range as written>, body: <commit messages>}`; for a working tree, `{title: "worktree tree=<tree hash>", body: <branch commit messages since merge-base>}`, excluding snapshot messages and uncommitted text. When the reviewer could not obtain an issue's comments verbatim, pass `comments_available: false` and no comments rather than an empty list. A spec's `identity` is its URL or coordinate. Recompute the digest rather than trusting change-supplied metadata.

On a working tree, keep the snapshot commit as the run `head`, and retain its tree hash, source HEAD, and complete manifest in the private record so it remains readable after the loose objects are garbage-collected. Local targets omit `repository_url` and record `merged: false`.

The caller's `profile` is part of the record's identity and selects only its artifact shape; every profile derives the same findings, questions, status, and coverage under the same rules. `python3 scripts/compose_review.py --example --profile implementation-gate` prints the `implementation-gate-record/1` input.

## Coverage

Coverage is `complete` only when every changed file is `reviewed` or `ignored` with a defensible reason, none `unreviewed`, every risk-directed check has an evidence-backed outcome, and every required fetch or verification completed. The `Coverage` line names each focused check run under [`changed-tests.md`](changed-tests.md), with its result in a few words, and says that execution was unavailable when that reference found no usable command or environment; an unexecuted test is never implied to have passed. When no clean-verdict batch ran because the ledger held no attackable row, the line says so. It keeps [`check-evidence.md`](check-evidence.md)'s outcomes distinct as that reference requires: caller evidence accepted for the reviewed state, caller evidence retained as historical at its original head, and each check the reviewer ran, each named with the check identity and the head it is attributed to. Share the head and common reasons across matching checks in this summary; reference supplied results instead of repeating their metadata. A test failure, an environment failure, an unavailable check, and accepted evidence stay separately identifiable on that line, and accepted evidence never reads as a check this review ran.

An incomplete review may publish verified findings already found, but its body must identify the uncovered files or checks and cannot claim the change is clean. On a pull-request target, a gap the step-1 packet names — a connection whose continuation failed or was never fetched, a page the forge returned with errors, or an item it withheld — is such a gap: name the connection and what its missing items could change, and never report `coverage=complete` while the packet reports `complete: false`. For an input unavailable to the reviewer, `Coverage gaps` also states what the input could change, lists the candidate ids whose dispositions it gates, and addresses the recovery request to the orchestrator. Recovery follows the rubric's Uncertainty routing section.

Inline anchors use `RIGHT` for added/current lines and `LEFT` for deleted lines.
