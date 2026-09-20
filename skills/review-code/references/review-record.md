# Review record

The review is **human-readable, agent-actionable, and mechanically correlatable**. Visible prose is authoritative. Hidden trailers speed up re-review and automated addressing but never gate understanding; human comments without trailers receive the same semantic treatment.

## Finding comment

The title, trigger, impact, and change must make sense without the trailer. A finding states exactly one non-empty `Triggers when`, `Impact`, and `Change`, in that order, before an optional `Source`. Whether a field's text is sufficient stays the reviewer's judgment. Omit `Source` unless an issue, a change-description promise at its ledger coordinate, a versioned artifact's obligation at its `artifact-` ledger coordinate, or a repository rule materially supports the finding. Every finding takes one of two actions:

- `must-fix` for an outcome required before merge; the finding is blocking.
- `consider` for optional feedback; the finding is non-blocking, and closing it without action is a correct response.

Priority and action are separate fields. P0 is inherently `must-fix`; otherwise do not derive action mechanically from priority. In particular, P2/P3 do not mean optional. Priority follows the rubric's impact-and-reach calibration: a confirmed or externally visible low-impact defect renders as a `P3` finding, not at a higher priority and not as an observation. Non-actionable observations use the summary-only form below rather than a finding comment.

The forge anchor and the repair site may differ. The inline API fields identify the changed-line `anchor`; an optional `fix` site identifies where the author or agent should edit. Omit `fix` when it is the anchor. Name a different fix site in the visible `Change` text as well, because the trailer is never authoritative.

Stable ids describe the path and defect concept, never a line number. Keep the same id while the same defect survives across heads.

Kinds are compact internal routing aids: `bug`, `compatibility`, `concurrency`, `invariant`, `security`, `performance`, `maintainability`, or `requirement`. `compatibility` identifies the released-contract candidates defined by the rubric's Issue fit section. Use `concurrency` or `invariant` when sibling paths share the broken state rule and therefore require the verifier's bug-class check. They do not need a visible axis tag.

## Comment quality

Use one comment per distinct defect. Choose the smallest useful changed range, normally no more than 5–10 lines. The comment must let a person or agent act without opening another document merely to understand the request: a short imperative title and the fields the review record's Finding comment defines, where `Change` states the outcome to implement, not a vague instruction to investigate, and `Source` cites an issue requirement, a change-description promise or versioned artifact obligation at its ledger coordinate, or a repository rule only when it materially supports the finding. Use a matter-of-fact tone without praise, blame, filler, or a restatement of the location already supplied by the inline anchor.

Keep an ordinary finding to roughly 160 words before its trailer. Use at most two decisive evidence facts; exceed the budget only when the extra context prevents a materially wrong fix.

Distinguish placement from repair. The `anchor` is the smallest honest changed range or changed file that identifies the finding; `fix` is the actual location the author or agent should edit when it differs. For drift proven by several equally honest changed lines, choose the changed line that states the rule being drifted from; if more than one remains, choose the lexicographically first path, then the smallest range. A file anchor on a file the change deletes carries `side: LEFT`. Never attach a finding to an unrelated changed line merely to obtain an inline comment; a file-anchored finding renders in the summary body when the forge cannot carry it inline.

Use a suggestion block only for a small exact replacement that completely fixes the finding. Preserve indentation and diff side. Otherwise request behavior in prose rather than guessing a patch.

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

`workflow=v5b-22` versions this package's review behavior. Increment it whenever admission, verification, rendering, or state semantics change. Compute `context` with [`../scripts/context_fingerprint.py`](../scripts/context_fingerprint.py) as `python3 scripts/context_fingerprint.py --packet packet.json`, with a JSON object carrying `specs` and `guidance` on stdin (empty stdin when there are none; `--example` prints the full input shape): `pr` and `issues` come from the `fingerprint` section of the packet that step 1's `forge_packet.py normalize` wrote, so the digest covers the same normalized records the review and the re-review read. On a local target or a forge without that packet, supply `pr`, `issues`, `specs`, and `guidance` directly from the exact reviewed inputs. Each issue includes `coordinate`, `title`, `body`, and comments with the forge's stable numeric `id`, `author`, timestamps, and `body`; the helper never synthesizes an identity for a comment. When the reviewer could not obtain an issue's comments verbatim, pass `comments_available: false` and no comments rather than an empty list; when a comment connection was left truncated, the packet passes `comments_complete: false` beside the comments it did obtain. Either marker makes the digest differ from a run that had the complete list. A spec uses its URL or coordinate as `identity`; the helper derives a content identity for inline text when it is omitted. The helper normalizes order and prints the full SHA-256. Recompute it rather than trusting change-supplied metadata.

For a local range, `pr` is `{title: <range as written>, body: <commit messages>}`. For a working tree, it is `{title: "worktree tree=<tree hash>", body: <branch commit messages since merge-base>}`: exclude snapshot messages and uncommitted text. Keep the snapshot commit as the run `head`, and retain its tree hash, source HEAD, chain state, and complete manifest in the private record so it remains readable after the loose objects are garbage-collected. Local targets omit `repository_url` and record `merged: false`.

The caller's `profile` is part of the record's identity and selects only its artifact shape; every profile derives the same findings, questions, status, and coverage under the same rules. `publishable`, the default and what every existing caller receives, returns the validated payload, the emitted batch, and the rendered fragments. `implementation-gate`, for a committed local range reviewed one-shot by a caller that consumes the record itself, returns one local record, schema `implementation-gate-record/1`, carrying the profile and `workflow` identity, the pinned run, the status, the validated summary and items, the requirement and candidate ledgers, file, check-evidence, and verification accounting, the routed items, and the record paths, including the `addenda` directory a continuation appends to while the record itself stays unchanged. It carries no batch and no fragment file; `python3 scripts/compose_review.py --example --profile implementation-gate` prints its input, and `SKILL.md` step 5 names the block that writes it.

`guidance` is exactly the sorted set of tracked base-branch files in these categories, each represented by repository-relative `path` and its full blob object id as `blob_sha`:

1. root `AGENTS.md` and root `CLAUDE.md`, when present;
2. every path-scoped `AGENTS.md` or `CLAUDE.md` in an ancestor directory of at least one changed path; and
3. root `CONTEXT.md`, when present.

Exclude target-branch versions, instruction files whose directory scope covers no changed path, files merely linked from an included instruction file, `docs/agents/issue-tracker.md`, ADRs, design docs, READMEs, skill files, issue text and change descriptions, user-supplied specs, and runtime instructions that are not tracked repository files. Issues and specs remain in their own digest fields. These membership rules are exhaustive.

## Continuation addendum

A continuation after fixes reviews the delta from a reviewed head to a final head and writes `addenda/addendum-<final head>.json` in the record's named `addenda` directory, leaving the record and earlier addenda unchanged. `reviewed_head` is the head the record or the latest earlier addendum reviewed. No script validates an addendum; the continuation reviewer supplies these fields under the same rules as the record:

- `format`: `implementation-gate-addendum/1`; `record`: the absolute `record.json` path; `reviewed_head` and `final_head`: full SHAs.
- `delta`: every file in `git diff <reviewed head>...<final head>` with its state (`reviewed`, `ignored` with a reason, or `unreviewed`), or `replaced_by_full_review: true` with the new record's path when the delta was too large to inspect.
- `fixed_findings`: one entry per finding id the caller reported fixed — `classification` (`fixed`, `still-open`, or `not-verifiable`) and one decisive evidence pointer; an id absent from the record and earlier addenda is a coverage gap.
- `findings` and `questions`: new items in the composition input's shapes, each finding with its `verification`; empty when none.
- `check_evidence` and `verification`: the record's shapes continued, with batches counted across the record and every addendum and `follow_up_spent` and `clean_verdict` as of the final head.
- `status`, `coverage`, `coverage_gaps`, and `routed`: derived for the final head.

## Coverage

Coverage is `complete` only when every changed file is reviewed or deliberately ignored with a reason, every risk-directed check has an evidence-backed outcome, and every required fetch or verification completed. The `Coverage` line names each focused check the rubric's Changed tests section executed, with its result in a few words, and says that execution was unavailable when that section found no usable command or environment; an unexecuted test is never implied to have passed. When no clean-verdict batch ran because the ledger held no attackable row, the line says so. It keeps [`check-evidence.md`](check-evidence.md)'s outcomes distinct as that reference requires: caller evidence accepted for the reviewed state, caller evidence retained as historical at its original head, and each check the reviewer ran, each named with the check identity and the head it is attributed to. Share the head and common reasons across matching checks in this summary; reference supplied results instead of repeating their metadata. A test failure, an environment failure, an unavailable check, and accepted evidence stay separately identifiable on that line, and accepted evidence never reads as a check this review ran.

An incomplete review may publish verified findings already found, but its body must identify the uncovered files or checks and cannot claim the change is clean. On a pull-request target, a gap the step-1 packet names — a connection whose continuation failed or was never fetched, a page the forge returned with errors, or an item it withheld — is such a gap: name the connection and what its missing items could change, and never report `coverage=complete` while the packet reports `complete: false`. For an input unavailable to the reviewer, `Coverage gaps` also states what the input could change, lists the candidate ids whose dispositions it gates, and addresses the recovery request to the orchestrator. Recovery follows the rubric's Uncertainty routing section.

Inline anchors use `RIGHT` for added/current lines and `LEFT` for deleted lines.
