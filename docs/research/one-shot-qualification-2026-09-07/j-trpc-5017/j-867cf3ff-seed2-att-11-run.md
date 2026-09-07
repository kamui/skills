# Research report — cell `j-867cf3ff-seed2`, attempt `att-11`

Target: `trpc/trpc#5017` ("fix(server): inference fix for inputs with middleware"), retrospective review of a **merged** pull request, posting identity `kamui` (third party, not the author). Publication disabled per rule 2 of the dispatch; this report and the sibling payload file are the complete would-be review.

Payload (the review exactly as it would be posted): [`j-867cf3ff-seed2-att-11-payload.md`](./j-867cf3ff-seed2-att-11-payload.md).

## 1. Metadata

| Field | Value |
| --- | --- |
| Target | `trpc/trpc#5017` |
| Cell / attempt | `j-867cf3ff-seed2` / `att-11` |
| Skill snapshot | `/tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/` |
| `workflow` identifier (from `validate_review.py`'s `WORKFLOW` constant) | `v5b-1` |
| Model I ran on | `claude-sonnet-5` (Sonnet 5) |
| Sub-agents spawned | **none** — see §7 for why the verification trigger did not fire |
| Model each sub-agent ran on | n/a (none spawned) |
| Verification trigger fired? | **No.** Neither zero-survivor mode nor mandatory per-candidate verification nor the "ordinary consider" cross-module-trace clause applied. Quoted sentences in §7. |
| Candidates raised | 6 (2 survivors as findings, 1 routed to Observations, 3 dropped before reaching ledger-worthy status — see §3) |
| Candidates surviving falsification | 2 (both `[P3] [consider] [maintainability]`) |
| Verifier verdicts | n/a — no verifier batch was dispatched |
| Findings for publication | 2, both `P3`/`consider`/`maintainability`, `blocking=false` |
| Questions | 0 |
| Observations | 1 (of a 3-item cap) |
| Coverage | `complete` — both changed files reviewed in full; all applicable risk-directed checks addressed; no unresolved fetch or verification |
| Derived status | `Approved (advisory)` (COMMENT event, non-gating; `(advisory)` appended per the output contract because status is `Approved` and event is `COMMENT`) |
| My own token usage | Not reported to me by this harness; I cannot state a number. |

## 2. Every finding that survives, in full

### Finding 1 — `server/utils-overwrite-dead-branch`

- **Priority/action:** `P3` / `consider` / `blocking=false` / `kind=maintainability`
- **Anchor:** `packages/server/src/core/internals/utils.ts:25-30` (RIGHT — all six lines are additions in the merge-base diff)
- **Fix location:** same as anchor (omitted `fix` field; anchor is the fix site)
- **Claim:** In the new `Overwrite<TType, TWith>` non-object branch (`: TType extends any ? TWith extends any ? TWith : TType : never`), the `: TType` arm is unreachable for every instantiation of `TWith`, because a naked type parameter's `extends any` check is true for every type except `never`, and instantiating that parameter with `never` short-circuits the entire conditional to `never` before either branch is evaluated (TypeScript's distributive-conditional-on-`never` rule). So the branch always evaluates to `TWith`, or to `never` when `TWith` is `never` — it can never evaluate to `TType`.
- **Verification status and evidence:**
  - Not independently verified (not required — see §7); primary-confirmed only.
  - Decisive evidence: a self-contained scratch TypeScript reproduction of the exact head-branch `Overwrite` definition, type-checked with the clone's own `tsc` binary. `Overwrite<UnsetMarker, never>` (Case B, `TType` non-object, `TWith=never`) was asserted `Equal<..., never>` — **passed** (no tsc error). A negative-control assertion, `Equal<..., UnsetMarker>` on the same type, was asserted true to confirm the `Equal` helper actually discriminates — it **failed** with `error TS2344: Type 'false' does not satisfy the constraint 'true'.`, proving the check is not vacuously true. Full scratch file and both runs are recorded in §4/§5.
  - I additionally traced every call site of `Overwrite` in `packages/server/src` (`procedureBuilder.ts:38,41,44`; `middleware.ts:65,81,103,136`; `utils.ts:71`) to confirm this branch is reachable in real usage (it is, via `Overwrite<TPrev['_input_in'], TNext['_input_in']>` when `TPrev['_input_in']` is `UnsetMarker`, e.g. the first `.input()` call in a chain) and that no unchanged guard prevents `TWith` from resolving to `never` there in principle (an input schema whose inferred type is `never`, e.g. `z.never()`, would exercise it) — though I found no evidence any current caller actually does so today; the finding rests on the branch's structural unreachability, not on a live regression.
  - Confirmed introduced-here: `git show <merge-base>:packages/server/src/core/internals/utils.ts` shows no `TType extends object` split at all — the base version always executed the mapped-type/`never` structure regardless of object-ness, so this specific dead sub-branch did not exist before this diff.
  - Confirmed unintentional: none of the four review comments in the packet's prior-review section, nor the PR body, discuss this specific sub-branch; they discuss only the `Overwrite<string, string>` garbling that the PR fixes.
- **Trigger scenario:** `TType` is a non-object type (e.g. `UnsetMarker`, a bare primitive) and `TWith` is any type; the `: TType` fallback that the branch's shape and its "Same as above" comment imply exists is never selected by the compiler.

### Finding 2 — `tests/regression-5020-void-middleware-unused`

- **Priority/action:** `P3` / `consider` / `blocking=false` / `kind=maintainability`
- **Anchor:** `packages/tests/server/regression/issue-5020-inference-middleware.test.ts:13-17` (RIGHT — new file)
- **Fix location:** `packages/tests/server/regression/issue-5020-inference-middleware.test.ts:38` (inside the existing `test('string', ...)` block, where the missing assertions would go)
- **Claim:** The new regression test's router declares a third procedure, `voidWithMiddleware` (middleware but no `.input()`), but no assertion anywhere in the file reads `AppRouterInputs['voidWithMiddleware']` or `AppRouterOutputs['voidWithMiddleware']`; the procedure is declared and never exercised by a type-level assertion.
- **Verification status and evidence:**
  - Not independently verified (not required — rubric's hygiene-candidate rule applies mechanically and I already had full-file evidence; no cross-module trace needed). Primary-confirmed.
  - Decisive evidence: the full 40-line new file (already complete in the merge-base diff — read again at head via `git show review-head:...` for exact line numbers) contains exactly one `describe`/`test` block, and it only ever indexes `AppRouterInputs['str']` and `AppRouterInputs['strWithMiddleware']` (and the matching `Outputs`); `voidWithMiddleware` never appears again after its declaration at lines 13–17.
  - Convention check (rubric's "new file, establish local convention" rule): I read the two sibling regression tests whose names or content most plausibly share the "middleware + inference" convention — `issue-4947-merged-middleware-inputs.test.ts` and `issue-2856-middleware-infer.test.ts` — plus ran a batched, non-recursive `grep` for `t\.router\(\{` across `packages/tests/server/regression/` to find router-literal-style siblings. Every router endpoint or middleware declared in those siblings is asserted on (`issue-4947` explicitly asserts `expectTypeOf(...).toEqualTypeOf<...>()` on its one procedure; `issue-2856` asserts on the middleware's error type). This corroborates that `voidWithMiddleware` being declared-but-unused departs from the local convention.
  - The full-project `tsc --noEmit` run (see §5) confirms the file compiles today regardless of the gap — the finding is about missing test *coverage*, not a compile error.
- **Trigger scenario:** A reader runs, extends, or greps this regression suite for middleware-without-input inference coverage and finds none, even though the router literal already sets up the scenario.

## 3. Complete private disposition ledger

| id | kind | disposition | verifier ruling? | decisive evidence | falsification / routing reason |
| --- | --- | --- | --- | --- | --- |
| `server/utils-overwrite-dead-branch` | maintainability | **survivor** (Finding 1) | No — not must-fix/security/dataloss/destructive/compat-break, and I already had a self-contained proof requiring no cross-module trace, so SKILL.md's verification-dispatch conditions never applied (quoted in §7). | Scratch-`tsc` `Equal` check, `packages/server/src/core/internals/utils.ts:25-30` | Passed all 8 rubric gates: introduced-here (base had no such branch), discrete/actionable (one dead branch, one-line fix), proven consequence (positive + negative-control tsc proof), grounded (no assumption about intent needed — pure type algebra), unintentional (no review discussion covers it), worth author's time (a one-token simplification that removes misleading dead code), proportionate (matches the file's existing hand-written-type-algebra style). |
| `tests/regression-5020-void-middleware-unused` | maintainability | **survivor** (Finding 2) | No — hygiene candidate, `kind=maintainability`/`action=consider` per rubric's explicit routing rule, never mandatory-verification-eligible; no cross-module trace needed (whole new file already read). | `packages/tests/server/regression/issue-5020-inference-middleware.test.ts:13-17` (declaration) vs. lines 21-39 (assertions, which never mention it) | Passed all 8 gates via the rubric's explicit "declared but unused" hygiene rule for new test files; corroborated against 2 sibling regression tests' conventions. |
| `tests/filename-issue-5020-vs-pr-5017` | requirement/observation-only | **routed to Observations** | No — observations never go to a verifier; the rubric routes them directly. | `packages/tests/server/regression/issue-5020-inference-middleware.test.ts` (file); packet §5 commit `26814253` message `rename` (the file was renamed mid-review from `issue-5017-...` to `issue-5020-...`) | Fails gate 4 (proven consequence) / gate 1 (meaningful impact) — nothing breaks and no repository rule requires filename-issue-number alignment, but the fact is accurate and decisively evidenced, so it is an `observation (consequence absent)` per the rubric's routing sentence rather than a dropped candidate. |
| `server/utils-missing-changeset` | requirement (repository-rule, speculative) | **dropped before ledger-worthy status** | No. | `CONTRIBUTING.md` (searched, no changeset requirement stated); `.changeset/` (contains only `config.json` and `README.md`, no pending changeset); `.github/pull_request_template.md` (no changeset checkbox) | Dropped under the rubric's "do not manufacture findings because a rule file exists" instruction: I found no repository-rule text anywhere in the base-branch guidance actually requiring a changeset per PR, so this never became a citable repository-rule candidate — I record it here only for ledger completeness, not as a routed/observed fact, since it also lacks the "decisive evidence pointer" an observation requires. |
| `server/utils-array-object-mapping` | bug (speculative) | **dropped, pre-existing** | No. | `git show <merge-base>:packages/server/src/core/internals/utils.ts` (base always ran the mapped-type branch for any non-`never` `TType`/`TWith`, including arrays/functions, since it had no object-ness split at all) | Falsified on gate 2 (introduced-here): arrays/functions being merged key-wise via `keyof` is unchanged behavior from the base version; this diff does not worsen it (if anything, the new branching narrows when key-wise mapping happens, since it now requires `TWith extends object` too). Pre-existing, not this change's responsibility. |
| `server/utils-twith-unknown-ctx` | bug (speculative) | **dropped, unproven** | No. | `packages/server/src/core/internals/utils.ts:59-63` (`deriveParamsFromConfig`: `_ctx_out: {}`, always an object literal default) | Falsified on gate 4 (proven consequence): I traced the one place `_ctx_out`-style context values originate (`deriveParamsFromConfig`) and found no call path where `TNext['_ctx_out']` legitimately resolves to `unknown` rather than an object; the concern was speculative and the available static work (reading every context-shape declaration site) did not establish a real trigger, so per the rubric's gate-4 routing sentence this is `dropped (consequence unproven)`, not even eligible for Observations (no decisive evidence of a real instance). |

Every row above states, per the requirement in the dispatch, whether a verifier ever ruled on it (none did) and which rule in the skill did or did not require that (quoted in full in §7).

## 4. Every sub-agent dispatch

**None were dispatched.** No verifier batch (candidate mode or clean-verdict mode) and no other sub-agent was spawned during this run. §7 documents, with the exact triggering sentences quoted, why neither the mandatory-verification rule, the zero-survivor clean-verdict rule, nor the "ordinary consider survivor" cross-module-trace clause applied to either surviving candidate. Per the dispatch's own rule 10 ("dispatch every sub-agent in the foreground... never end your turn while a sub-agent... is still running"), there is nothing to wait on; this section is empty by design, not omission.

## 5. Everything consulted beyond the diff

All commands were run from a foreground shell against the offline clone at `/tmp/qual137/runs/j-867cf3ff-seed2-att-11` or the skill snapshot at `/tmp/qual137/snapshots/867cf3ff/skills/code-review-publish`, or against scratch files under `/tmp/qual137/work/j-867cf3ff-seed2-att-11/`. None reached the network (none were attempted).

1. `ls -la /tmp/qual137/snapshots/867cf3ff/skills/code-review-publish/scripts/` and `ls -la /tmp/qual137/runs/j-867cf3ff-seed2-att-11` and `cat` the timing sidecar and work dir — orientation, not repo-wide, not case-sensitive-relevant.
2. `git -C /tmp/qual137/runs/j-867cf3ff-seed2-att-11 branch -a`, `git log --oneline -3 main`, `git log --oneline -3 review-head`, `git status` — clone orientation. Both `log -3` calls stayed within the pinned range (`main`'s tip is the merge-base itself; `review-head`'s tip is the pinned head `7dc04a7e9`); no history beyond the pinned head was read (see §8).
3. Step-2 context command (run once, from inside the clone, per the skill): `python3 .../scripts/review_context.py --merge-base 2abb2d5cd19740be37272dac6ad7fdd36244ae54 --head 7dc04a7e94654dfad6ef1289dfe01a0a206fff3b`. Exit 0. Output saved to `context_output.txt` (manifest, full diff, ranges, and a bounded pre-merge-base `history` section for `utils.ts` — 3 commits, all dated before the PR, none beyond the pinned head).
4. `git show review-head:packages/server/src/core/internals/utils.ts` — whole-file read (95 lines total per the manifest, ≤300-line threshold, so a whole-file read needs no candidate-scoped justification per the rubric).
5. `cat packages/server/tsconfig.json packages/server/tsconfig.build.json tsconfig.json` — compiler-option context to build a valid scratch `tsc` config.
6. `grep -rn "Overwrite<" ` via the Grep tool, scoped to `packages/` (not the full repo — `Overwrite` is an unexported-from-npm internal type, unlikely to appear in `examples/`/`www/`; this scoping choice is disclosed as a judgment call in §10), case-sensitive (identifier name, case matters) — batched search finding all 9 call sites across `packages/server/src`.
7. `Read` on `packages/server/src/core/internals/procedureBuilder.ts` (lines 1-60) and `packages/server/src/core/middleware.ts` (lines 1-140) — bounded ranges to see how each `Overwrite<...>` call site is guarded (e.g. the `UnsetMarker extends TNext['_input_in'] ? ... : Overwrite<...>` guard).
8. Scratch reproduction: wrote `/tmp/qual137/work/j-867cf3ff-seed2-att-11/scratch/dead-branch.ts` (a standalone copy of the head-branch `Overwrite` definition plus an `Equal`/`Assert` type-equality harness) and `/tmp/qual137/work/j-867cf3ff-seed2-att-11/scratch/tsconfig.json`. Ran `cd .../packages/tests && ./node_modules/.bin/tsc --noEmit -p /tmp/qual137/work/j-867cf3ff-seed2-att-11/scratch/tsconfig.json` **twice**: first with only the positive assertions (exit 0, ~0.56s, no errors — confirms `Overwrite<UnsetMarker, never>` is exactly `never`, not `UnsetMarker`, and the ordinary/base-bug-regression cases resolve as documented); then with an added negative-control assertion (exit 2, one `TS2344` error — confirms the `Equal` harness actually discriminates and the first run's pass was not vacuous). This is the two-flag-set exception explicitly allowed by run-condition 2 ("a configuration at most once per flag set" — the second run added a line, changing what's being checked, not the flags).
9. Focused, project-wide typecheck permitted by run condition 2: `cd /tmp/qual137/runs/j-867cf3ff-seed2-att-11/packages/tests && ./node_modules/.bin/tsc --noEmit -p tsconfig.json`. Exit 0, ~6.4s (well under the 5-minute budget), **zero output** — the whole `packages/tests` project (including the new regression test and the changed `utils.ts`, reached via the `@trpc/server` path mapping) compiles cleanly at head. Run once for this flag set, per run condition 2.
10. `ls packages/tests/server/regression/` — listing all 29 sibling regression files.
11. Grep tool, pattern `` t\.router\(\{ ``, scoped to `packages/tests/server/regression/` (not repo-wide), default case sensitivity — batched search for router-literal-style siblings to establish local convention, per the rubric's "new file" hygiene rule. 19 files matched.
12. `Read` on `packages/tests/server/regression/issue-4947-merged-middleware-inputs.test.ts` (whole file, 82 lines) and `packages/tests/server/regression/issue-2856-middleware-infer.test.ts` (whole file, 15 lines) — convention comparison.
13. `grep -n -i "changeset" CONTRIBUTING.md` — case-insensitive, single file, no matches.
14. `ls .changeset/`, `cat .changeset/config.json`, `cat .github/pull_request_template.md` — checked whether a changeset or PR-template rule bears on the missing-changeset candidate; found none.
15. `sed -n '1,50p' CONTRIBUTING.md` and `grep -n -i "regression|issue-|naming" CONTRIBUTING.md` — checked for a documented regression-test naming convention; found none (only an unrelated comment-line match).
16. Grep tool, pattern `issue-5017|5017`, path = clone root, `-i: true` — **repo-wide, case-insensitive**. No matches anywhere in the tree, confirming the mid-review rename from `issue-5017-...` to `issue-5020-...` left no dangling reference.
17. `git show review-head:packages/tests/server/regression/issue-5020-inference-middleware.test.ts | cat -n` — line-numbered re-read of the already-fully-diffed new file, solely to pin exact anchor line numbers (13-17 for the declaration, 38 for the fix site) for the payload.
18. `python3 .../scripts/context_fingerprint.py /tmp/qual137/work/.../context_input.json` — the one-time `context` digest computation (§6).
19. `python3 .../scripts/validate_review.py --render < payload.json`, `python3 .../scripts/validate_review.py < payload.json`, `python3 .../scripts/validate_review.py --emit-batch < payload.json > batch.json` — all exit 0 on the first attempt; no self-test (`--self-test`) was run, per the dispatch's rule 3.

No focused unit/regression test (vitest) was executed at runtime; the `tsc --noEmit` runs in items 8-9 are the proportionate focused check for a type-only change with type-level (`expectTypeOf`) test assertions, and they directly decide both surviving candidates' factual claims.

## 6. The `context` digest

**Digest:** `1c8dbb4d4781a49c2ab16f3b0f4b47c4c18838264b00c621266aefd91fd8d750`

Computed once, via `python3 scripts/context_fingerprint.py` on this exact input (saved at `/tmp/qual137/work/j-867cf3ff-seed2-att-11/context_input.json`):

```json
{
  "pr": {
    "title": "fix(server): inference fix for inputs with middleware",
    "body": "Closes #\n\n## 🎯 Changes\n\nWhat changes are made in this PR? Is it a feature or a bug fix?\n\n## ✅ Checklist\n\n- [ ] I have followed the steps listed in the [Contributing guide](https://github.com/trpc/trpc/blob/main/CONTRIBUTING.md).\n- [ ] If necessary, I have added documentation related to the changes made.\n- [ ] I have added or updated the tests related to the changes made."
  },
  "issues": [],
  "specs": [],
  "guidance": []
}
```

- `pr.title`/`pr.body`: verbatim from packet §3 (the PR body — no issue/closing reference is present in it).
- `issues`: empty — packet §1/§4 pin `issues=none` (no closing reference, no other explicit issue link, no user-supplied issue/spec).
- `specs`: empty — none supplied.
- `guidance`: empty — packet §7 confirms no root or path-scoped `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` exist at the merge-base for any changed path (only `CONTRIBUTING.md`, `.github/CODEOWNERS`, and `.github/pull_request_template.md` are present, none of which are in the digest's `guidance` membership categories per the output contract).
- `comments_available`: not applicable — no issues, so no comments field is needed.

## 7. Mechanism checklist

| Mechanism | Fired? | Where demonstrated |
| --- | --- | --- |
| Question channel | **Did not fire.** | No candidate met the rubric's static-unresolvability bar ("no static evidence could settle the fact") — both surviving candidates were fully settled by direct code/tsc evidence, so no `[Question]` item was written. |
| Clean-verdict verification (either mode) | **Did not fire.** | Zero-survivor mode requires "zero candidates survive as findings"; 2 candidates survived, so the precondition in SKILL.md ("Zero-survivor mode: when zero candidates survive *as findings*... run one clean-verdict batch") never held. Related-acquittal mode requires "the initial candidate batch is dispatched" — none was (see below), so its precondition ("include in that same batch every non-survivor ledger row that is *related* to a survivor") never held either. |
| Observations | **Fired once.** | `tests/filename-issue-5020-vs-pr-5017` — routed per the rubric: "Route an accurate fact to `Observations` when it fails finding admission specifically on meaningful or proven consequence." Rendered in the payload's `## Observations` section (1 of the 3-item cap). |
| Fix-sufficiency check on a concurrency/invariant candidate | **Did not fire — no such candidate.** | Neither surviving candidate is `kind=concurrency` or `kind=invariant` (both are `maintainability`); the verifier's rule-level/sibling-interleaving checklist in `references/verifier.md` §"For every confirmed `kind=concurrency` or `kind=invariant` candidate" never applies here, and no verifier ran regardless. |
| Follow-up verifier round | **Did not fire — no initial batch to follow up.** | SKILL.md: "After the initial candidate or clean-verdict batch is dispatched, collect any candidate that newly reaches render eligibility... Run at most one fresh follow-up batch." No initial batch was dispatched (see below), so there is nothing to follow up. |
| Deferral handling | **Did not fire — no deferral in the record.** | The packet's prior-review section (§6) contains no explicit deferral language ("we can fix this later", "revisit the name", etc.) among the four review comments; they are substantive technical discussion of the `Overwrite<string, string>` bug this PR fixes, not a deferred decision. No deferral-as-open-question treatment was needed. |
| Retrospective mode | **Fired.** | The `Mode` line is present in the summary body verbatim: `**Mode:** Retrospective review of merged pull request; publication disabled.` Per dispatch rule 2 and packet §1 (`state=MERGED`, `merged=true`), publication was rendered rather than executed; step 6 was followed through composition of `batch.json` via `--emit-batch` (exit 0) but the batch was never submitted to any forge. |
| Early dispatch of the verifier batch (this skill defines "run one initial candidate batch... After the initial... batch is dispatched, collect any candidate that newly reaches render eligibility") | **Did not fire.** | Quoting SKILL.md exactly: *"Independently verify every surviving candidate proposed as `must-fix`, plus every candidate involving security or authorization, data loss or corruption, destructive migration, or an externally observable compatibility break."* Neither survivor is `must-fix` (both are `consider`) nor touches security/authorization/data-loss/destructive-migration/compatibility-break. Quoting the rubric's companion clause: *"Include an ordinary `consider` survivor only when proving or refuting its existing claim requires a cross-module trace or another difficult reconstruction."* Candidate 1 was fully settled by a self-contained scratch-`tsc` type-algebra proof (no cross-module trace — the claim is about the shape of one type expression); candidate 2 was fully settled by reading the complete 40-line new file plus two bounded sibling-file reads (not a "difficult reconstruction"). So the "at least one candidate qualifies" precondition for dispatching *any* batch (SKILL.md: "When at least one candidate qualifies, run one initial candidate batch in the fresh isolated context it specifies") was never met, and no batch — early or otherwise — was ever dispatched. This is a legitimate, skill-compliant zero-dispatch outcome for a diff of this size and risk profile, not a shortcut. |

## 8. History discipline

I did **not** read any history beyond the pinned head `7dc04a7e94654dfad6ef1289dfe01a0a206fff3b`. Exact history-touching commands run, all of which stayed at or before the pinned head/merge-base:

- `git branch -a` (listed branches only; no revision walk).
- `git log --oneline -3 main` → showed `2abb2d5c` (the merge-base, `main`'s pinned tip) and its two immediate ancestors `b26797c6`, `acea5332` — both dated before the PR, part of ordinary pre-merge-base history.
- `git log --oneline -3 review-head` → showed the pinned head `7dc04a7e9` and its two immediate ancestors on the head branch, `26814253` ("rename") and `3c12b289` ("col") — both are commits *on this PR's own head branch*, at or before the pinned head, not beyond it.
- The step-2 `review_context.py` run's own `## history` section (bounded pre-merge-base history for `utils.ts`, 3 commits, all dated 2023-04-20 through 2023-06-15 — well before the PR's 2023-11-10 merge) — generated by the skill's own script, not a manually issued command, and explicitly scoped to pre-merge-base history by the script's design.
- `git show review-head:<path>` (three times, for `utils.ts` and the new test file) — reads file *content* at the pinned head, not history.

No `git log` targeting anything past `7dc04a7e9`, no `git fetch`/`git pull` (both would fail offline regardless), and no attempt to inspect the PR's actual GitHub thread beyond what the packet already reproduced verbatim.

## 9. Sandbox disclosure

No path outside the sandbox was read for content. Every content read/command targeted one of: the clone (`/tmp/qual137/runs/j-867cf3ff-seed2-att-11`), the skill snapshot (`/tmp/qual137/snapshots/867cf3ff/skills/code-review-publish`), the packet directory (`/tmp/qual137/packets/j/packet.md`), or my own work/report/payload/timing paths under `/tmp/qual137/work/j-867cf3ff-seed2-att-11/` and `/tmp/qual137/reports/j/`. I did not read any other run's clone, report, or payload content, and no sub-agent was spawned that could have done so either.

One disclosure for completeness: a final sanity-check `ls -la /tmp/qual137/reports/j/` (run only to confirm my own four output files existed with the right names before finishing) also listed the *filenames* of other attempts' output files in the same shared directory — `j-867cf3ff-seed1-att-10-*`, `j-bea6be14-seed1-att-09-*`, `j-bea6be14-seed2-att-12-*`. I did not open, read, or otherwise use the content of any of those files; only their names and sizes were visible in the listing.

## 10. Notes — judgment calls

1. **No verifier dispatch at all.** The most significant judgment call in this run: I concluded, after building the full candidate ledger, that neither surviving candidate met any of the skill's verification-dispatch conditions (mandatory-action, mandatory-kind, or the ordinary-consider cross-module-trace clause), so I dispatched zero sub-agents. I treated this as the skill working as designed for a small, low-risk, type-only diff, not as license to skip a step — §7's last row documents the exact quoted sentences that govern this, and the ledger in §3 shows every candidate's routing rationale independent of any verifier.
2. **Scoping the `Overwrite<` repo-wide search to `packages/`.** The rubric's synchronization-drift falsification step calls for a repo-wide, case-insensitive sweep specifically "for propagation or synchronization drift." My `Overwrite<` search was a caller-enumeration search, not a synchronization-drift search (there is no peer artifact restating an `Overwrite`-like rule elsewhere that this PR could have drifted from), so I judged the narrower `packages/` scope adequate for that specific purpose and instead ran the repo-wide, case-insensitive sweep (item 16 in §5) for the one place it was actually called for: confirming the `issue-5017`→`issue-5020` rename left no dangling references anywhere in the tree.
3. **Including the filename discrepancy as an Observation.** `issues=none` is pinned by the packet as authoritative, and I did not attempt to re-resolve GitHub issue #5020 (no network access, and the packet instructs against re-resolving the target). I judged the bare fact — this PR's own regression test cites a different, unlinked issue number — decisively evidenced and non-speculative enough to qualify as an observation under the rubric's "fails only on consequence" routing sentence, rather than omitting it or trying to inflate it into a requirement finding (which would have required treating the filename as an issue link, contradicting the packet's pinned `issues=none`).
4. **`FlatOverwrite` (a sibling, unchanged type in `packages/server/src/types.ts`) was out of scope.** It shares a name-root with `Overwrite` but is a distinct, unchanged type not touched by this diff; I did not review it as a candidate surface since gate 2 (introduced-here) would fail immediately for anything about it, and I only opened `types.ts` far enough (the `grep -n "Overwrite"` hit list) to confirm it's a different, unmodified declaration.
5. **Whole-file reads for both changed files.** Both are ≤300 lines (95 and 40 respectively), so per the rubric's explicit exception I read them whole without needing to name a candidate justifying it.
6. **No re-review handling.** Packet §1 states the posting identity `kamui` has no prior review or comment on this PR, so step 2's re-review trigger ("When step 1 found any prior review, reply, or trailer-bearing comment from the posting identity, read `references/re-review.md` now") never fired; I did not read `re-review.md` and did not apply step 4. This is a first review.
