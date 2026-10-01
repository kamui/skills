# Research report — cell `j-bea6be14-seed1-att-09`

Target **(j) `trpc/trpc#5017`** — "fix(server): inference fix for inputs with middleware". Cell
`j-bea6be14-seed1`, attempt `att-09`, an independent replicate. Payload:
[`j-bea6be14-seed1-att-09-payload.md`](j-bea6be14-seed1-att-09-payload.md).

## 1. Metadata

| | |
| --- | --- |
| Target | `trpc/trpc#5017`, MERGED, retrospective/non-publishing (packet §1, §8.4) |
| Cell / attempt | `j-bea6be14-seed1` / `att-09` |
| Skill snapshot | `/tmp/qual137/snapshots/bea6be14/snapshot-path-omitted/` |
| `workflow` identifier (validator) | `v5b-10` (`WORKFLOW = "v5b-10"` in `scripts/validate_review.py:115`) |
| Model — reviewer (me) | `claude-sonnet-5` |
| Model — sub-agents | none spawned this run (see §4/§7 for why) |
| Verification trigger fired | **none.** See §7 for the exact sentences that decided this. |
| Sub-agents spawned | 0 |
| Candidates raised | 3 (1 survivor / finding, 2 dropped on falsification) + 1 fact routed directly to Observations |
| Candidates surviving primary falsification | 1 (`tests/void-with-middleware-untested`, P3/consider/maintainability) |
| Verifier verdicts | none (no batch dispatched) |
| Findings published | 1 (P3, consider, maintainability) |
| Questions published | 0 |
| Observations published | 1 (of ≤3 cap) |
| Coverage | complete |
| Derived status | **Approved (advisory)** |
| Token usage | not reported to me by this harness for this session; I have no figure to give |

## 2. Findings for publication (in full)

### [P3] [consider] Assert the inferred types for `voidWithMiddleware`

- **Priority / action:** P3 / `consider`, `blocking=false`
- **kind:** `maintainability`
- **Anchor:** `packages/tests/server/regression/issue-5020-inference-middleware.test.ts:13-17`, side `RIGHT`
- **Fix location:** `packages/tests/server/regression/issue-5020-inference-middleware.test.ts:39` (inside the existing `test('string', ...)` block, where a companion assertion block would go)
- **Claim:** The new regression test file declares a third router procedure, `voidWithMiddleware` (no `.input()`, only middleware), but no `test` block or assertion in the file ever reads `AppRouterInputs['voidWithMiddleware']` or `AppRouterOutputs['voidWithMiddleware']`. Only `str` and `strWithMiddleware` are asserted against, each via a matching `expectTypeOf<...>().toBeString()` pair.
- **Trigger scenario:** A future edit to `Overwrite` (or to the `_input_in`/`_ctx_out` merge logic that calls it) regresses inference specifically for procedures that skip `.input()` and only apply middleware. This regression test suite would keep passing green because nothing in it exercises that code path's output.
- **Verification status:** Not independently verified — not required. It is not `must-fix`, and it does not touch security/authorization, data loss/corruption, destructive migration, or an externally observable compatibility break, so `SKILL.md` step 3's mandatory-verification list does not apply. It is also not a case where "proving or refuting its existing claim requires a cross-module trace or another difficult reconstruction" (`SKILL.md` step 3, the ordinary-`consider`-survivor inclusion clause): the claim is settled by reading the 40-line new file once — no cross-module trace needed — so the primary reviewer's own falsification is the complete and sufficient evidence.
- **Evidence:** `packages/tests/server/regression/issue-5020-inference-middleware.test.ts:13-17` (declaration); `packages/tests/server/regression/issue-5020-inference-middleware.test.ts:21-40` (the entire `describe`/`test` block — no reference to `voidWithMiddleware` anywhere in it, confirmed by reading the whole 40-line file and by the fact the file contains the literal string `voidWithMiddleware` exactly once, at its declaration).

Full rendered markdown (as it would post) is in the payload file's "Inline comments" section.

## 3. Complete private disposition ledger

| id | kind | disposition | decisive evidence pointer | falsification reason | verifier ruled? |
| --- | --- | --- | --- | --- | --- |
| `tests/void-with-middleware-untested` | maintainability | **survivor → published finding** | `packages/tests/server/regression/issue-5020-inference-middleware.test.ts:13-17` (declared), `:21-40` (never referenced again) | n/a — passed all 8 admission gates (see §2 above and reasoning below) | No. Not a `must-fix`/security/data-loss/migration/compat-break candidate (`SKILL.md` step 3's mandatory list), and its claim needed no cross-module trace (the "ordinary `consider` survivor" inclusion clause), so no batch was ever assembled in this run — see §7. |
| `overwrite-any-distributive-branching` | bug (type-correctness, hypothesis only) | **dropped** | `packages/server/src/core/internals/utils.ts:12-19` (new `Overwrite`); `packages/server/src/core/initTRPC.ts:32-33` (`ctx: TTypes['ctx'] extends RootConfigTypes['ctx'] ? TTypes['ctx'] : object` — context always defaults to `object`, never `any`); `packages/server/src/core/middleware.ts:65,81,103,136` and `packages/server/src/core/internals/procedureBuilder.ts:38,41,44` (every call site of `Overwrite` in the package, all supplying concrete context/input/output type parameters, never a literal `any`) | Fails gate 4 (proven consequence): TypeScript's `any`-in-conditional-type special case (`T extends U ? X : Y` unions both branches when `T` is literally `any`) could in principle make `Overwrite<any, TWith>` behave differently under the new two-level branching than under the old one-level branching, but no call site anywhere in the reviewed package instantiates `Overwrite` with a literal `any` for either parameter — context types default to `object`, and every other call site supplies a concrete generic parameter. No concrete input, state, or call path could be constructed to trigger it, so the candidate is speculation about an unreachable instantiation, which the rubric's gate 4 explicitly disqualifies ("speculation about downstream breakage is insufficient"). | No — dropped in primary falsification before any batch existed. |
| `overwrite-perf-regression` | performance (hypothesis only) | **dropped** | `packages/server/src/core/internals/utils.ts` history line from `review_context.py`'s `## history` section: `65b6bebc 2023-04-20 perf(server): \`Overwrite\` util type is unnecessarily expensive (#4204)`; focused command `cd packages/tests && ./node_modules/.bin/tsc --noEmit -p tsconfig.json` — exit 0, ~4.8s wall / 8.10s user | Risk-led discovery, not a proven candidate: the file's own history shows a prior PR was specifically about `Overwrite`'s compile-time cost, so a widened read was justified under the rubric's risk-led-discovery rule (external-contracts/performance risk signal) to check whether this diff regresses it. The new implementation adds one bounded extra conditional level (not unbounded recursion), and the focused `tsc --noEmit` run over the whole `packages/tests` project (which imports and exercises `Overwrite` pervasively through every router/procedure type in the suite) completed in ~4.8s with zero errors — no timeout, no observable slowdown signal available to compare against. Fails gate 4 (no measurement establishes a regression) and admits no concrete trigger; dropped as `dropped (consequence unproven)`, not published as an observation either, because it is not an established accurate fact (it is a hypothesis I could not confirm), and the Observations route requires an accurate fact, not an untested hypothesis. | No — risk settled during primary falsification, never reached batch-eligibility. |
| (unnamed — routed directly as observation, not carried as a `bug`/`maintainability` finding candidate) | maintainability (fact) | **routed to Observations, published** | `packages/server/src/core/internals/utils.ts:12-19` | Fails finding admission specifically on gate 1/4 (meaningful impact / proven consequence): the trailing `: never` arm of `TWith extends any ? TWith : never` inside the object-branch of the new `Overwrite` is unreachable — TypeScript's conditional-type distributivity collapses the outer `TWith extends object ? … : …` expression straight to `never` whenever `TWith` is instantiated as `never`, before the inner ternary is ever reached, so the explicit `: never` fallback text never actually executes for any input; the type's behavior is identical whether that fallback exists or not. This is an accurate, decisively grounded fact with zero observable consequence — exactly the Observations route ("Route an accurate fact to `Observations` when it fails finding admission specifically on meaningful or proven consequence"). | No — an observation is explicitly non-actionable and never enters candidate/batch machinery. |

Every row above states whether a verifier ruled on it, per the report's requirement; none did, because — as detailed in §7 — no candidate in this run ever met a mandatory-verification trigger, the zero-survivor clean-verdict trigger never applied (one candidate survived, so it was not a zero-survivor run), and the sole survivor's claim did not require the "cross-module trace or another difficult reconstruction" that would have earned it a discretionary seat in a batch — so **no batch of any kind was ever dispatched in this run.**

I also actively checked, but never formulated into an even-provisional candidate (so these are *not* ledger rows — they never reached the "raised" bar because no repository rule or evidence could support even a hypothesis):

- Whether the PR should have added a `.changeset/*.md` entry. `CONTRIBUTING.md` (`git show main:CONTRIBUTING.md`, read in full) contains no mention of changesets, and `.changeset/` at the reviewed head contains only `config.json` and `README.md` (tooling scaffolding, not entries) — I did not attempt to determine changeset convention from history because no rule cites it as a requirement, so raising this would have had no evidentiary basis under the rubric's Repository rules section ("must cite the applicable file and smallest supporting range").
- `.github/CODEOWNERS` and `.github/pull_request_template.md` — present per packet §7, but out of scope for a type-correctness diff (routing/template files, no content standard bearing on this change); not read beyond what the packet already quoted verbatim.

## 4. Every sub-agent dispatch

**None were dispatched.** `SKILL.md` step 3 gates every batch (candidate batch or clean-verdict batch) behind one of exactly two triggers, and neither fired:

1. *Mandatory-verification trigger* — "Independently verify every surviving candidate proposed as `must-fix`, plus every candidate involving security or authorization, data loss or corruption, destructive migration, or an externally observable compatibility break." The one survivor is `consider`/`maintainability`; it touches none of those surfaces.
2. *Zero-survivor clean-verdict trigger* — "when zero candidates survive *as findings* … run one clean-verdict batch instead of a candidate batch." One candidate survived as a finding, so this mode's precondition (`zero` survivors) never held. (It is also moot that this diff is not a concurrency/failover/data-integrity/security surface, which is the trigger's other precondition.)

The remaining discretionary door — "Include an ordinary `consider` survivor only when proving or refuting its existing claim requires a cross-module trace or another difficult reconstruction" — also did not open: the sole survivor's claim ("no assertion in this 40-line file references `voidWithMiddleware`") is fully settled by reading that one file once; no cross-module trace exists to perform.

Because no batch condition ever held, `SKILL.md`'s early-dispatch clause ("Dispatch that batch as soon as (a)… and (b)…") never had a batch to dispatch early or late — it is inapplicable in a run with zero eligible candidates for any batch. No verifier, no clean-verdict worker, and no "related-acquittal" worker were spawned at any point. This is a legitimate, calibrated outcome for a two-file, 57-line diff whose only defect is a low-priority test-hygiene gap: the rubric's whole point is that verification is *consequence-triggered*, not universal.

## 5. Everything consulted beyond the diff

All commands below were run from `/private/tmp/qual137/sessions` (harness cwd) unless a `cd` is shown; all targets are inside `/tmp/qual137/runs/j-bea6be14-seed1-att-09` (the pinned clone) or the skill/packet/work directories.

**Diff and manifest (read once, per `SKILL.md` step 3):**
- `git diff main review-head` inside the clone — full 2-file diff, read directly once for orientation before building the persisted store.
- `python3 /tmp/qual137/snapshots/bea6be14/snapshot-path-omitted/scripts/review_context.py --merge-base 2abb2d5cd19740be37272dac6ad7fdd36244ae54 --head 7dc04a7e94654dfad6ef1289dfe01a0a206fff3b --store <mktemp-dir>/review-context-7dc04a7e94654dfad6ef1289dfe01a0a206fff3b.json` — the one authoritative build call. Diff text printed in full (not withheld — 2 small files, well under the 24000-byte bound); `## chunks` inventory showed `diff coverage: complete (2/2 chunks consumed)`, so no `--from` recovery read was ever needed.

**Whole-file reads (files ≤300 lines, permitted without extra justification per the rubric's Complete inspection section):**
- `Read packages/server/src/core/internals/utils.ts` (95 lines) — the changed file, both to see the head state in full and to compare structurally against the diff.
- `Read packages/tests/server/regression/issue-5020-inference-middleware.test.ts` (40 lines) — the new test file; a file the diff adds is "already fully present in it," so this read is a convenience re-display, not an extra inspection charge.

**Batched searches (repo-wide `grep`, not per-file reads), all case-sensitive except where noted, none needed case-insensitivity since `Overwrite` is a fixed TypeScript identifier:**
- `Grep "Overwrite" path=packages` (files_with_matches) — found 8 files referencing the identifier `Overwrite` (as substring, so it also matches `OverwriteKnown`, `FlatOverwrite`, `OverwriteIfDefined`). Repo-wide under `packages/`, not confined to the changed file's directory — satisfies the rubric's propagation/synchronization-drift sweep discipline even though no drift candidate ultimately needed it.
- `Grep "Overwrite" path=packages/server/src/core/middleware.ts -C 3 output_mode=content` — bounded context around each of the 4 call sites in that file (lines 9, 65, 81, 103, 136 per the file's numbering).
- `Grep "Overwrite" path=packages/server/src/core/internals/procedureBuilder.ts -C 3 output_mode=content` — bounded context around the 5 call sites in that file (lines 26-27, 38, 41, 44, 59, 69, 108, 112).
- `Grep "Overwrite" path=packages/tests/server/regression/issue-4321-context-union-inference.test.ts -C 5 output_mode=content` — confirmed this sibling regression test is about a *different*, already-fixed `Overwrite` bug (union-distributivity, fixed by an earlier PR referenced in that test's own comment), not overlapping with this PR's fix; read to rule out double-counting or a missed regression in that adjacent test.
- `Bash: grep -n -i "changeset" CONTRIBUTING.md` (via `git show main:CONTRIBUTING.md | grep -n -i changeset`) — repo-wide within the one file, case-insensitive; zero matches, which is why no changeset-related candidate was ever raised (see §3, bottom).

**Base-branch comparisons (`git show <merge-base>:<path>`), used for gate 2's introduced-here guarantee check:**
- The merge-base version of `packages/server/src/core/internals/utils.ts` is visible directly in the diff's `-` lines (the file is small enough that the diff itself constitutes the full before/after comparison); I did not need a separate `git show main:packages/server/src/core/internals/utils.ts` call because the unified diff already shows every removed line in context (`@@ -2,19 +2,33 @@` covers the whole `Overwrite` declaration). I did run `git show main:CONTRIBUTING.md` (see above) as the one base-branch guidance-file read the packet's §7 asked me to classify.

**Base-branch context-default read:**
- `Read packages/server/src/core/initTRPC.ts` (first 80 lines) — bounded range, read to establish that `ctx` (the most common `Overwrite` operand) defaults to `object`, never `any`, which is the decisive evidence that falsified the `overwrite-any-distributive-branching` candidate.

**Focused execution (the one command this target's packet explicitly authorizes, run once for this exact flag set):**
- `cd /tmp/qual137/runs/j-bea6be14-seed1-att-09/packages/tests && ./node_modules/.bin/tsc --noEmit -p tsconfig.json` — exit 0, wall time 4.838s (8.10s user / 0.41s system across cores), **zero output** (clean pass). This is the decisive execution evidence for the Changed Tests section: the new file's `expectTypeOf<Input>().toBeString()`/`toBeString()` pairs for `str` and `strWithMiddleware` are compile-time-only assertions (no runtime check fires from `expectTypeOf` itself for this matcher), so a clean `tsc --noEmit` over the whole `packages/tests` project — which imports `@trpc/server` and therefore compiles the new `Overwrite` against every router type in the suite, including the new regression file — is the only real "did the fix work" signal available offline. I did not run `vitest` (`pnpm test-run:vitest`): the packet's §8.2 execution allowance names only "the TypeScript compiler," and rule 5 in the main dispatch repeats the same scope ("Focused type-checking IS permitted… Run the TypeScript compiler…"), so I treated `vitest` execution as outside this run's authorized allowance rather than assuming it was included, and recorded it as "not run" (never as an implicit pass) in the Coverage line.
- `./node_modules/.bin/tsc --version` — `Version 5.1.3`, a one-line sanity check before the real run; not itself a "configuration," so it does not count against the one-per-flag-set budget.

**Context digest:**
- `python3 /tmp/qual137/snapshots/bea6be14/snapshot-path-omitted/scripts/context_fingerprint.py /tmp/qual137/work/j-bea6be14-seed1-att-09/context-input.json` — run exactly once (see §6).

**Not read / not run, and why:**
- No `git log`/`git show` beyond the pinned head or beyond the one `main:CONTRIBUTING.md` base-branch read (see §8 — history discipline).
- No `--self-test` invocation of any script (rule 3 forbids it for this cell).
- No `forge_packet.py` call — no raw `forge-*.json` pages exist offline; the packet's binding condition §8.1 states phase 1 is already satisfied by the packet itself.
- `vitest` not run (see focused-execution paragraph above).
- `.github/CODEOWNERS` content not read (routing metadata, no bearing on a type-correctness diff).

## 6. The `context` digest and its inputs

Digest: **`1c8dbb4d4781a49c2ab16f3b0f4b47c4c18838264b00c621266aefd91fd8d750`**

Computed once via `python3 scripts/context_fingerprint.py /tmp/qual137/work/j-bea6be14-seed1-att-09/context-input.json` (direct-input mode, not `--packet`, because no `forge-packet/1`-schema JSON file was available offline — only the human-readable `packet.md`; the output contract explicitly permits this: "On a forge without that packet, supply `pr`, `issues`, `specs`, and `guidance` directly from the exact reviewed inputs.").

Input JSON (verbatim, `/tmp/qual137/work/j-bea6be14-seed1-att-09/context-input.json`):

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

- `pr.title` / `pr.body`: taken verbatim from packet §3 (the PR body, reproduced in full including the unfilled template).
- `issues`: empty — packet §1/§4 states no originating issue (`issues=none`; the PR body carries no closing reference and no other issue link).
- `specs`: empty — the dispatch supplied no user spec.
- `guidance`: empty — packet §7's table shows no root or path-scoped `AGENTS.md`/`CLAUDE.md`/root `CONTEXT.md` present at the merge-base for any changed path (only `CONTRIBUTING.md`, `.github/CODEOWNERS`, and `.github/pull_request_template.md` exist, none of which the output contract's three `guidance` categories include).
- `comments_available` / `comments_complete`: not applicable — `issues` is empty, so no issue-comment markers apply.

## 7. Mechanism checklist

| Mechanism | Fired? | Where demonstrated |
| --- | --- | --- |
| Question channel | **Did not fire.** | No statically-unresolvable, outcome-changing fact arose. The one issue-fit ambiguity (no linked issue) was resolved by the rubric's own instruction ("With none, step 2 builds its ledger from the pull-request title and body… and the summary states that issue alignment was unavailable"), which is a stated summary line, not a question. |
| Clean-verdict / related-acquittal verification | **Did not fire, either mode.** | Zero-survivor mode requires zero surviving findings; one survived. Related-acquittal mode requires a dispatched candidate batch to ride along with; none was dispatched (§4). No re-open ever occurred. |
| Observations | **Fired once.** | The unreachable `: never` fallback fact, routed and published — see §2/§3 last row and the payload's `## Observations` section. |
| Fix-sufficiency check on a concurrency/invariant candidate | **Did not fire — not applicable.** | No candidate in this run carries `kind=concurrency` or `kind=invariant`; `verifier-concurrency.md` was never read, correctly, since `SKILL.md` only loads it "when at least one batch candidate's `kind` is `concurrency` or `invariant`," and no batch existed at all. |
| Follow-up verifier round | **Did not fire.** | No initial batch was ever dispatched (§4), so there is nothing to follow up. |
| Deferral handling | **No explicit deferral found in the review record.** | Packet §6's four review comments (KATT, jussisaurio ×3) discuss *how* to fix `Overwrite` (pseudocode alternatives) but contain no phrase of the "we can fix this later"/"let's revisit" shape the rubric's deferral rule targets. I read all four comments as part of building the private ledger in step 2 and found no deferral to record. |
| Retrospective mode | **Fired, as required.** | Packet §1/§8.4: target is `MERGED`; publication is disabled by default for a retrospective review of a merged PR (`SKILL.md` Boundaries: "retrospective review of a merged pull request is non-publishing by default"). The summary body's `**Mode:** Retrospective review of merged pull request; publication disabled.` line reflects this, per the output contract's mandatory `Mode` line rule. |
| Early dispatch of the verifier batch relative to the falsification pass | **Not applicable — no batch of any kind existed to dispatch early or late.** | See §4. The early-dispatch clause presupposes at least one eligible batch; this run never reached that precondition. |

## 8. History discipline

I read **no commit history beyond the pinned head** and **no history the packet did not already supply or that `review_context.py` did not itself print**. Specifically:

- `git log --oneline -3 main review-head` (run early, for orientation) — printed exactly the three most-recent commits reachable from the pinned `review-head`/`main` tips: `7dc04a7e9`, `26814253`, `3c12b289`, all of which are on the pinned commit list in packet §5 (commits 8, 7, 6 respectively, oldest-first there). This command touches nothing past the pinned head — `main` is force-pinned to the merge-base and `review-head` is pinned to the head SHA, so neither ref can reach anything newer.
- `git diff main review-head` — the merge-base-to-head diff; not history traversal.
- `git show main:CONTRIBUTING.md` and `git show main:packages/server/src/core/internals/utils.ts` (the latter not actually needed in the end, see §5) — both read the **merge-base** (`main`) tree state, not history.
- `review_context.py`'s own `## history` section (part of the one authoritative store-build call in §5) printed three pre-merge-base commits that last touched `packages/server/src/core/internals/utils.ts` (`1f4a2ead`, `2ddc5405`, `65b6bebc`) — these are commits *before* the merge-base, surfaced by the tool itself as context for understanding the file's evolution, not commits I fetched by name. I did not `git show` any of them individually; I used only the one-line summary the tool printed (message + date + PR number) as the risk-led-discovery trigger for the performance candidate in §3, and that one line was sufficient to settle it.

I ran no `git fetch`, `git pull`, `gh`, `curl`, or other network-touching command (none would have worked offline regardless — the clone's `origin` is a local filesystem path per packet §8.1). I ran no `git checkout`, `git switch`, `git reset`, or `git stash` at any point; the clone was never mutated.

## 9. Sandbox disclosure

Everything substantive was read from: the clone (`/tmp/qual137/runs/j-bea6be14-seed1-att-09`), the skill snapshot (`/tmp/qual137/snapshots/bea6be14/snapshot-path-omitted/`), the packet (`/tmp/qual137/packets/j/packet.md`), and my own work/report/payload/timing paths under `/tmp/qual137/work/j-bea6be14-seed1-att-09/` and `/tmp/qual137/reports/j/j-bea6be14-seed1-att-09-*`.

Two paths outside that enumerated list were touched, both required by the dispatch or the skill itself rather than chosen by me:

1. **The private review-context store**, created by `mktemp -d` per `SKILL.md` step 2's explicit instruction ("Create a private directory outside the working tree"): `/var/folders/tj/sr3wvlgs0v9608r9tjwmtnk40000gn/T/tmp.tE1JcAMSZ0/review-context-7dc04a7e94654dfad6ef1289dfe01a0a206fff3b.json`. This is a location I created and only I wrote to and read from; nothing pre-existing was read from it, and it never held anything other than this run's own diff/manifest data. Its path is also recorded in `/tmp/qual137/work/j-bea6be14-seed1-att-09/store-dir.txt` and `store-path.txt` for my own bookkeeping.
2. **`/tmp/qual137/mark_event.py`** — the timing-sidecar helper script, invoked exactly once as the top-level dispatch instructed ("Immediately after `validate_review.py` exits 0 on your final payload, run `python3 /tmp/qual137/mark_event.py …`"), writing only to my own timing file `/tmp/qual137/reports/j/j-bea6be14-seed1-att-09-timing.json`.

One incidental exposure: an early `ls /tmp/qual137/reports/j/` (run to see what already existed before I started writing) listed the **filenames** `j-867cf3ff-seed1-att-10-session.txt` and `j-867cf3ff-seed1-att-10-timing.json` — another cell/attempt's bookkeeping files in the shared `reports/j/` directory. I did not open or read the content of either file, and no other command referenced them. Disclosing this per rule 7/9 even though only filenames, not content, were seen.

No other run's clone, report, or payload was read. No content outside the sandbox was used to inform any finding, disposition, or the digest.

## 10. Notes — judgment calls on ambiguities in the skill's contract

1. **Phase-1 mechanics vs. the packet's override.** `SKILL.md` step 1 specifies a `gh api graphql` fetch-and-normalize procedure. The packet explicitly states phase 1 is already done and forbids re-resolving over the network, and its §8.1 states this satisfies the skill's phase-1 requirement "including its `merged` field." I treated this as a binding substitution for step 1's mechanics only, not for step 1's *substance* (I still recorded `state`, `merged`, `head`, `base`, `merge-base`, and the posting-identity/re-review determination exactly as step 1 requires — I just took the values from the packet instead of a live fetch).
2. **`context_fingerprint.py` without a `forge-packet/1` file.** Since no raw `forge-*.json` pages exist offline and `forge_packet.py normalize` was never run (per note 1), I used the script's documented direct-input mode rather than `--packet`. I judged this to be exactly the "forge without that packet" case the output contract anticipates, not a deviation from it.
3. **Whether the `voidWithMiddleware` gap is a legitimate rubric candidate at all, or too close to "generic test-quality nitpicking" to admit.** The rubric's Changed Tests section calibrates this exact shape of candidate explicitly ("A test that passes without exercising the behavior it claims… supports at most an optional test-quality candidate, `maintainability` and `consider`, when the ordinary benefit and evidence bar holds"). I judged the bar met here because the gap is concretely named (a specific procedure, a specific missing assertion pair) and ties directly to the PR's own stated purpose (middleware/inference regression coverage) rather than being a generic "add more tests" complaint — the file itself already signals intent to cover this case by declaring the procedure, it just stops short of asserting on it.
4. **Not raising the `Overwrite<any, …>` and performance hypotheses as published findings, but keeping them as full ledger rows rather than silently discarding them.** Both were seriously enough formulated (with a specific evidence-seeking check performed to try to confirm or refute them) that I treated them as "raised candidates" under the rubric's falsify-and-deduplicate discipline, even though neither survived. I judged that omitting them from the ledger would have understated the risk-led discovery actually performed on this diff's two named risk categories (external contracts/type correctness; performance) given the file's own history.
5. **`CONTRIBUTING.md`'s classification.** I treated it as general contributor documentation consulted for repo convention (testing commands, changeset presence/absence), not as an `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md`-class "repository rule" or as part of the `context` digest's `guidance` field — the output contract's `guidance` membership rules are stated as exhaustive and do not include `CONTRIBUTING.md`, and the Repository rules rubric section's own examples and framing are oriented at instruction-file-style guidance rather than a human contributor guide.
6. **Anchor choice for the one finding.** I anchored on the `voidWithMiddleware` declaration (lines 13-17) rather than on the `describe`/`test` block that fails to reference it (lines 21-40), because the rubric directs choosing "the smallest honest changed range… that identifies the finding," and the declaration is the more specific, smaller honest anchor for "this procedure exists but nothing asserts on it"; I named the `test` block's end (line 39) as the separate `fix` location because that is where an agent would actually add the missing assertion block.
