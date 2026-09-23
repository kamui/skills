# review-code simplification: staged draft

The artifact-savings epic (#340) made review-code's mechanics cheaper to author, but the skill stayed large: 88 KB of runtime prose, 25 KB always loaded, about 60K words of non-test Python, and a 53K-word history installed with it. Its combined measurement (#347) found no overall cost or latency saving, more finalizer repairs under the stricter preconditions, and verifier returns still inline under Claude Code. This stage cuts the machinery instead of automating it, and keeps what makes the skill better than a plain review prompt.

## What stays

1. **Review against intent.** A requirements ledger from issues, specs, and the change description. An omission in unchanged code still counts.
2. **A high admission bar, enforced by falsification.** Introduced here, a proven trigger and consequence, an attainable remedy. Priority is separate from action.
3. **Independent verification where a wrong call is costly.** A fresh-context verifier gets claims and evidence only. Verification is mandatory for `must-fix` and the risk areas, a safety-premise attack runs on high-risk no-blocker conclusions, and the allowance is one batch plus one follow-up.
4. **Honest completeness.** A complete pinned diff with truncation recovery, per-file coverage, and status precedence `Changes Requested` > `Incomplete` > `Needs Information` > `Approved`.
5. **Continuity.** Stable ids, classified prior items, disputes, and a duplicate-review shortcut.
6. **The model judges and scripts do the mechanics.**

## Decisions

| Decision | Effect |
| --- | --- |
| One record shape; no `profile` input | Every run writes `record.json`, `report.md`, `payload.json`, `batch.json`. `fragments.md` has no consumer and goes. `compose_review.py`, `validate_review.py` and `finalize_review.py` merge into one `render_review.py`, keeping `--check` and `--emit-batch --event`, the only entry `review-code-publish` uses. |
| Continuation is a re-review | A local run takes `prior_record` and writes a new, complete record in a new directory linked to it. Addenda, chain walking, replacement records, the version-1 mapping and `continue_review.py` go. See Prior-record check. |
| PR fetch moves into a script | `forge_packet.py fetch` runs the GraphQL root and continuation queries through `gh` and normalizes them, a recorded departure like `review-bot`'s. |
| Inline verifier returns only | The file transport, `--inline-fallback` and the transport choice go. The SHA-256 echo becomes an echo of the batch name the brief states, so an initial return is never accounted against a follow-up bundle that reuses its stable ids. |
| No context digest | The trailer drops `context=`, and `context_fingerprint.py`, `fingerprint.json` and the finalizer's digest derivation go. The shortcut holds when head, base, merge-base and `workflow` match the trailer and `later-state` settles, and never when the caller supplies specs or issues, which `later-state` cannot see. Trailer parsing still accepts `context=` on older reviews. `audit-code-publish` keeps its own copies of these scripts and diverges further. |
| Session reruns keep their own allowance | As today, an answer or code change in `session` starts a fresh run with its own allowance. Only a caller continuing after fixes, such as `implement-publish`, passes `prior_record` and shares the allowance. |
| Mode decides the return | `return_format` goes: `session` presents `report.md`, and `one-shot` returns the finalizer's status line and paths, which is what both skill callers pass today. |
| Publication authorization leaves review-code | The merged-target authorization input goes. The retrospective Mode line reads only "Retrospective review of merged pull request", and `review-code-publish` alone decides whether to publish. |
| No timing log | `run_events.py`, its tests and the hooks in other scripts go, along with every `wrap` prefix in review-code and review-code-publish. Timing for later measurements comes from transcript tool-call timestamps, which `transcript_usage.py` already parses. |
| History leaves the installed skill | `HISTORY.md` moves under `docs/`; `DESIGN.md` keeps only the current design. |

### Prior-record check

The one-hop check replaces the chain validator, so it must keep what that validator enforced. `render_review.py` refuses a `prior_record` run unless:

- the prior record carries its finalization marker and the same repository and base;
- every prior open finding and question is classified, and every `outstanding` and `routed` entry survives unless a task in this run settled it;
- the spent allowance flags are at least the prior's;
- each carried confirmation names the prior record and a batch whose accounting establishes it (`confirmed_in`), transitively through the prior's own carried entries;
- the record's `lineage` is the prior's lineage plus the prior itself, so `implement-publish` verifies with one read that the final record descends from the records it dispatched, and a fork that reuses an unspent ancestor is detectable.

## Target layout

| File | Replaces | Loaded |
| --- | --- | --- |
| `SKILL.md` ([draft](SKILL.draft.md)) | `SKILL.md` | Always |
| `rubric.md` ([draft](rubric.draft.md)) | `review-rubric.md`, `conformance.md`, `released-compatibility.md`, `changed-tests.md`, `check-evidence.md` | Always |
| `targets.md` | `pull-request-target.md`, `local-targets.md` | Step 1 |
| `prior-state.md` | `re-review.md`, `continuation-addendum.md` | A re-review |
| `verification.md` | `verifier-handoff.md` | A batch |
| `output.md` | `rendering.md` | Step 7 |
| `verifier.md`, `verifier-concurrency.md` | also `verifier-return.md` | Worker brief only |

The builder embeds the rubric's Released compatibility and Changed tests sections by heading; Supplied checks stays primary-only.

**Undrafted files must keep.** `targets.md`: dirty submodule content is a coverage gap; a short base name prefers `origin/<base>`, and a base equal to the current branch means `HEAD`; local records carry no `repository_url`, so unpushed commits never become forge links; a packet without `merged` gives a provisional `Incomplete`; `[bot]` login normalization (moves into `forge_packet.py` where possible). `verification.md`: dispatch only after the full pass; reconciliation of corrections, safety rulings and duplicate groups; a changed mandatory claim is reconfirmed in the follow-up or withheld; repair fixes encoding only.

## Size

The two drafts total about 20 KB, including about 800 bytes of draft and license comments. The files they replace total 38,413 bytes. Changed tests and check evidence were already loaded on every path, so the always-loaded pair (about 19 KB) replaces a common set of about 32 KB. The rest of the layout is not drafted; `test_instruction_budget.py` sets new limits as each change lands.

## Sequence

1. **Prose and history.** Consolidate references into the target layout and move `HISTORY.md`, keeping today's semantics: `SKILL.md` still names the profiles, addenda and fingerprint. Fix consumer paths in the same change (`implement-publish/SKILL.md` names `check-evidence.md`, `implement-publish/references/continuation.md` names `continuation-addendum.md`, `review-code-publish/SKILL.md` names `rendering.md`). No workflow bump.
2. **One record, prior records, no digest.** `render_review.py`, `prior_record` with the check above, the trailer without `context=`, the plain retrospective Mode line, and the draft `SKILL.md` activated without `profile`, `return_format` or publication authorization. Rewrite `implement-publish`'s gate call and `continuation.md`, and drop those inputs from `review-code-publish`'s invocation. One workflow bump covers the record, state and trailer changes; each open pull request gets one fresh review.
3. **Verifier.** Inline only and the batch-name echo. Mechanics only, no bump.
4. **Fetch and timing.** `forge_packet.py fetch`; delete `run_events.py` and remove `wrap` from both skills. Mechanics only, no bump.

`finish-it` changes through its dependencies only.

## Considered and rejected

- **Dropping observations.** They keep accurate, non-actionable facts from becoming low-value `consider` findings or summary padding, and the verifier's aside needs a channel outside its verdicts. The saving is a few sentences.
- **Merging the `concurrency` and `invariant` kinds.** It saves one word, changes public vocabulary, and `invariant` also covers shared-state rules unrelated to threads.
