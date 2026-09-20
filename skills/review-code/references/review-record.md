# Review record

The review is **human-readable, agent-actionable, and mechanically correlatable**. Visible prose is authoritative. Hidden trailers speed up re-review and automated addressing but never gate understanding; human comments without trailers receive the same semantic treatment.

## Finding comment

The title, trigger, impact, and change must make sense without the trailer. A finding states exactly one non-empty `Triggers when`, `Impact`, and `Change`, in that order, before an optional `Source`; `rendering.md` says how the validator reads that shape. Whether a field's text is sufficient stays the reviewer's judgment. Omit `Source` unless an issue, a change-description promise at its ledger coordinate, a versioned artifact's obligation at its `artifact-` ledger coordinate, or a repository rule materially supports the finding. Every finding takes one of two actions, whose tags, trailer fields, and permission sentence `rendering.md` spells:

- `must-fix` for an outcome required before merge; the finding is blocking.
- `consider` for optional feedback; the finding is non-blocking, and closing it without action is a correct response.

Priority and action are separate fields. P0 is inherently `must-fix`; otherwise do not derive action mechanically from priority. In particular, P2/P3 do not mean optional. Priority follows the rubric's impact-and-reach calibration: a confirmed or externally visible low-impact defect renders as a `P3` finding, not at a higher priority and not as an observation. Non-actionable observations use the summary-only form below rather than a finding comment.

The forge anchor and the repair site may differ. The inline API fields identify the changed-line `anchor`; an optional `fix` site identifies where the author or agent should edit. Omit `fix` when it is the anchor. Name a different fix site in the visible `Change` text as well, because the trailer is never authoritative.

Stable ids describe the path and defect concept, never a line number. Keep the same id while the same defect survives across heads.

Kinds are compact internal routing aids: `bug`, `compatibility`, `concurrency`, `invariant`, `security`, `performance`, `maintainability`, or `requirement`. `compatibility` identifies the released-contract candidates defined by the rubric's Issue fit section. Use `concurrency` or `invariant` when sibling paths share the broken state rule and therefore require the verifier's bug-class check. They do not need a visible axis tag.

## Question comment

Ask only when the rubric's Material questions rule is met: no static evidence could settle the fact, and `Why it matters` names the correctness outcome, acceptance criterion, compatibility or release obligation, or present merge decision the answer changes. A question about a recorded deferral also names, in `Evidence`, the deferral's author and comment, the surface, and the current decision. A question is not a finding, has no priority, requests no code change, and states who or what measurement can answer it. Whole-change questions belong in the review body rather than on an arbitrary line.

When a verified candidate becomes a question because its settling fact is statically unresolvable, retain its stable concept id and change only its item type from finding to question, as `rendering.md` renders it. This keeps later answers and any code-decided finding correlated across runs.

## Observations

`Observations` is a bounded summary-body channel for accurate, non-actionable facts that meet the rubric's route. It is separate from findings and questions: observations have no priority, action, stable id, trailer, or anchor comment and never affect status. Publish at most three, each as one sentence followed by one decisive evidence pointer. Use descriptive language without `should` or `must`.

When more than three qualify, publish the three with the most decisive evidence and record each of the rest in the private record as `observation (unpublished, cap)`. A fact belongs to exactly one channel: an unpublished observation and a verifier aside stay in that record rather than folded into a finding's `Impact` or `Change` prose.

Do not create an observation merely to preserve a dropped candidate. The fact itself must stand, and it must have failed finding admission on consequence or arrived as a verifier aside.

## Replies and prior state

[`re-review.md`](re-review.md), loaded by `SKILL.md` step 1 when prior state comes from the reviewer identity or the same local session, defines reply dispositions, reply trailers, the duplicate-review shortcut, delta scope, and the prior-item classification whose outcomes feed the `disputed` status input and populate the `Disputed` and `Prior findings` summary sections defined in `rendering.md`.

## Status

Derive one semantic status after findings, questions, coverage, and prior state are complete:

1. `Changes Requested` when any `must-fix` finding is unsettled, including a disputed or not-verifiable blocker.
2. `Incomplete` when no blocker is known but material coverage or verification did not finish.
3. `Needs Information` when coverage is complete and an unanswered question could change the verdict. A recorded deferral or `not-verifiable` row that the rubric published no question for contributes nothing to this status.
4. `Approved` otherwise. `consider` findings do not prevent approval.

A missing issue required by the repository workflow is a material question: with otherwise complete coverage and no unsettled must-fix finding it yields `Needs Information`, never `Incomplete` for that reason alone.

`rendering.md` owns how the status appears in the body, including its advisory form.

## Review identity

`workflow=v5b-21` versions this package's review behavior. Increment it whenever admission, verification, rendering, or state semantics change. Compute `context` with [`../scripts/context_fingerprint.py`](../scripts/context_fingerprint.py) as `python3 scripts/context_fingerprint.py --packet packet.json`, with a JSON object carrying `specs` and `guidance` on stdin (empty stdin when there are none): `pr` and `issues` come from the `fingerprint` section of the packet that step 1's `forge_packet.py normalize` wrote, so the digest covers the same normalized records the review and the re-review read. On a local target or a forge without that packet, supply `pr`, `issues`, `specs`, and `guidance` directly from the exact reviewed inputs. Each issue includes `coordinate`, `title`, `body`, and comments with the forge's stable numeric `id`, `author`, timestamps, and `body`; the helper never synthesizes an identity for a comment. When the reviewer could not obtain an issue's comments verbatim, pass `comments_available: false` and no comments rather than an empty list; when a comment connection was left truncated, the packet passes `comments_complete: false` beside the comments it did obtain. Either marker makes the digest differ from a run that had the complete list. A spec uses its URL or coordinate as `identity`; the helper derives a content identity for inline text when it is omitted. The helper normalizes order and prints the full SHA-256. Recompute it rather than trusting change-supplied metadata.

For a local range, `pr` is `{title: <range as written>, body: <commit messages>}`. For a working tree, it is `{title: "worktree tree=<tree hash>", body: <branch commit messages since merge-base>}`: exclude snapshot messages and uncommitted text. Keep the snapshot commit as the run `head`, and retain its tree hash, source HEAD, chain state, and complete manifest in the private record so it remains readable after the loose objects are garbage-collected. Local targets omit `repository_url` and record `merged: false`.

The caller's `profile` is part of the record's identity and selects only its artifact shape; every profile derives the same findings, questions, status, and coverage under the same rules. `publishable`, the default and what every existing caller receives, returns the validated payload, the emitted batch, and the rendered fragments. `implementation-gate`, for a committed local range reviewed one-shot by a caller that consumes the record itself, returns one local record, schema `implementation-gate-record/1`, that carries the profile, schema, and `workflow` identity; the pinned repository, range, head, base, merge-base, `context`, issues, specs, and coverage; the status; the validated summary and items with their stable ids; the requirement and candidate ledgers; file accounting over the pinned manifest; check-evidence accounting under the rubric's three outcomes; verification accounting naming each batch's bundle, raw return, accounting, and host operation, whether the follow-up is spent, the clean-verdict conclusion, and any outstanding mandatory work; the routed unresolved, disputed, and unrecoverable items; and the record paths, including the `addenda` directory to which a continuation appends while the record itself stays unchanged. It carries no batch and no fragment file. `SKILL.md` step 5 names the block that writes it, and `rendering.md`'s Composition section says which validations every profile runs and which belong only to a forge payload.

For each local-session run, persist the run head, base SHA and its source, merge-base, snapshot identity above when applicable, and owned snapshot ref names. Retain named paths to `payload.json`, the private record (including file accounting and coverage), and verification accounting. The session record preserves these inputs alongside its layer and amendment provenance; retain per-run batch accounting and the session-wide further-batch authorization/spent state across rechecks.

`guidance` is exactly the sorted set of tracked base-branch files in these categories, each represented by repository-relative `path` and its full blob object id as `blob_sha`:

1. root `AGENTS.md` and root `CLAUDE.md`, when present;
2. every path-scoped `AGENTS.md` or `CLAUDE.md` in an ancestor directory of at least one changed path; and
3. root `CONTEXT.md`, when present.

Exclude target-branch versions, instruction files whose directory scope covers no changed path, files merely linked from an included instruction file, `docs/agents/issue-tracker.md`, ADRs, design docs, READMEs, skill files, issue text and change descriptions, user-supplied specs, and runtime instructions that are not tracked repository files. Issues and specs remain in their own digest fields. These membership rules are exhaustive.

## Coverage

Coverage is `complete` only when every changed file is reviewed or deliberately ignored with a reason, every risk-directed check has an evidence-backed outcome, and every required fetch or verification completed. The `Coverage` line names each focused check the rubric's Changed tests section executed, with its result in a few words, and says that execution was unavailable when that section found no usable command or environment; an unexecuted test is never implied to have passed. It keeps the rubric's Supplied check evidence outcomes distinct as that section requires: caller evidence accepted for the reviewed state, caller evidence retained as historical at its original head, and each check the reviewer ran, each named with the check identity and the head it is attributed to. Share the head and common reasons across matching checks in this summary; reference supplied results instead of repeating their metadata. A test failure, an environment failure, an unavailable check, and accepted evidence stay separately identifiable on that line, and accepted evidence never reads as a check this review ran.

An incomplete review may publish verified findings already found, but its body must identify the uncovered files or checks and cannot claim the change is clean. On a pull-request target, a gap the step-1 packet names — a connection whose continuation failed or was never fetched, a page the forge returned with errors, or an item it withheld — is such a gap: name the connection and what its missing items could change, and never report `coverage=complete` while the packet reports `complete: false`. For an input unavailable to the reviewer, `Coverage gaps` also states what the input could change, lists the candidate ids whose dispositions it gates, and addresses the recovery request to the orchestrator. Recovery follows the rubric's Uncertainty routing section.

Inline anchors use `RIGHT` for added/current lines and `LEFT` for deleted lines. File-anchor provenance comes from `SKILL.md` step 5 and stays in the record through rendering and repair.
