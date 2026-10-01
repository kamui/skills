# Research report — `g-high-seed1-att-07`

## 0. Metadata

- **Target:** `tokio-rs/bytes#698` ("Reuse capacity when possible in `<BytesMut as Buf>::advance` impl")
- **Cell:** `g-high-seed1`, attempt `att-07`
- **Skill:** `legacy reviewer` (skill snapshot at `/tmp/effort124/skill/snapshot-path-omitted/`, `workflow=v5b-10` per `references/output-contract.md`)
- **Model I (the primary reviewer) ran on:** `claude-sonnet-5`
- **Model every sub-agent ran on:** `claude-sonnet-5` (passed explicitly as `model: "sonnet"` on the one verifier dispatch made — see §4)
- **Verification trigger that fired:** zero-survivor clean-verdict mode (`SKILL.md` step 3) — zero candidates survived primary falsification as findings, and the diff touches a data-integrity surface (unsafe raw pointer/length/capacity bookkeeping inside `BytesMut`, the crate's core buffer type). No candidate met the independent mandatory-verification trigger (none proposed as `must-fix`, none security/authorization/data-loss/destructive-migration/compatibility-break survivors), so no candidate batch ran — only the clean-verdict batch.
- **Sub-agents spawned:** 1 — role: clean-verdict verifier, `subagent_type: v5b-verifier-effort-high`, `model: sonnet`, `run_in_background: false`.
- **Candidates raised:** 7 (all in the primary candidate ledger, §3). Issue-fit ledger rows: 3 (no separate issue; built from PR title/body only).
- **Candidates surviving my own falsification (findings):** 0.
- **Verifier verdicts:** clean verdict stands on all 7 ledger rows (see §4 for the verbatim return).
- **Findings for publication:** none.
- **Questions:** none.
- **Observations:** none published (nothing met the Observations gate — see §2).
- **Coverage:** complete. One changed file (`src/bytes_mut.rs`, +8/−0), fully read from the persisted diff (chunk coverage `complete`, 1/1 chunks consumed); no test file changed by the diff, so the Changed Tests section's per-test-function obligations do not apply to anything; no repository guidance files present at the merge-base (verified by the pinned packet, not re-verified); no packet gaps (this is a from-packet pinned run, not a live forge fetch — see §6/§9 for how the digest was computed without a live `forge_packet.py normalize` packet).
- **Derived status:** `Approved` — see §0a below.
- **Token usage:** the harness does not report my own token usage to me in this session; I have no figure to give.

### 0a. Status derivation

Per `references/output-contract.md`'s Status section: no unsettled `must-fix` finding (rule 1 does not apply — zero findings at all), no unfinished material coverage or verification (rule 2 does not apply — the required clean-verdict batch ran and returned a clean verdict, and coverage is complete), no unanswered outcome-changing question (rule 3 does not apply — zero questions). So status is `Approved` (rule 4). Because the target is merged and this is a retrospective, non-publishing review, this renders as **Approved (advisory)** using event `COMMENT` (the default event; no gating authorization exists), with the mandatory `Mode` line for a merged target.

## 1. Pin the review (step 1) — inputs taken verbatim from the packet

I did not re-resolve the target over the network (no network access; packet rule 1). Everything below is copied from `/tmp/effort124/packets/g/packet.md`, treated as authoritative pinned input, per the dispatch's instructions.

| Field | Value |
| --- | --- |
| Repository | `tokio-rs/bytes` |
| Pull request | `#698` — "Reuse capacity when possible in `<BytesMut as Buf>::advance` impl" |
| Author | `paolobarbolini` (`CONTRIBUTOR`) |
| `summary.repository_url` | `https://github.com/tokio-rs/bytes` |
| Head SHA | `7052d2454a2370ab9583f63711df89f3bd7bec83` |
| Base ref | `master` |
| Base SHA / merge-base | `ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401` (identical) |
| `state` | `MERGED` |
| `merged` | `true` (2024-04-25T07:08:17Z) |
| `isDraft` | `false` |
| Originating issue(s) | none (`issues=none`); the PR body is the only source, per packet §4 |
| Posting identity | `kamui` — did not author the PR, has no prior comments/reviews on it → first review by a third party, event `COMMENT` |

**Retrospective mode.** The target is merged, so this is a retrospective/audit review with publication disabled by default (`SKILL.md` step 1 / Boundaries). No caller separately authorized publication to this merged target, so I rendered the complete would-be review instead of publishing (packet run-condition 4, dispatch rule 2).

I did **not** run the `gh api graphql` fetch in `SKILL.md` step 1 — packet run-condition 1 states the clone is offline with no network access of any kind, and "If your skill's phase 1 asks you to resolve the target from the forge, that phase is satisfied by this packet, including its `merged` field." I therefore treated the packet as the completed step-1 fetch and did not attempt `forge_packet.py normalize` over saved GraphQL pages (there are none — no forge call was made). This is a judgment call recorded in §10.

Since `kamui` has no prior review, reply, or trailer-bearing comment on this PR (packet, "Posting identity" row), step 1's re-review trigger does not fire; `references/re-review.md` does not apply. This is a first review.

## 2. Build private review context (step 2)

**Private store.** Created with `mktemp -d` (a path under `/var/folders/.../T/tmp.JzDR5Yyj3p`, recorded only in my own work directory at `/tmp/effort124/work/g-high-seed1-att-07/store-dir.txt`, never in the clone or a shared predictable location). Store file: `<mktemp-dir>/review-context-7052d2454a2370ab9583f63711df89f3bd7bec83.json`.

**Build command (run exactly once):**
```
python3 /tmp/effort124/skill/snapshot-path-omitted/scripts/review_context.py \
  --merge-base ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401 \
  --head 7052d2454a2370ab9583f63711df89f3bd7bec83 \
  --store <mktemp-dir>/review-context-7052d2454a2370ab9583f63711df89f3bd7bec83.json
```
run from inside `/tmp/effort124/runs/g-high-seed1-att-07` (the clone). Exit 0.

**Output (verbatim, reproduced in full — this is the complete build-call output, nothing was withheld):**

- `## manifest`: `M src/bytes_mut.rs +8 -0 new=no lines=1823`
- `## diff`: the complete 8-line-added hunk inside `impl Buf for BytesMut`, with automatic function-context widening that already printed the whole `impl Buf for BytesMut` block (`remaining`, `chunk`, `advance`, `copy_to_bytes`) — see §3 for the diff text itself.
- `## ranges`: `src/bytes_mut.rs:1056-1093 @head`, `src/bytes_mut.rs:1056-1085 @merge-base`
- `## history`: `src/bytes_mut.rs: 9d3ec1c 2024-04-24 Resize refactor (#696)`, `src/bytes_mut.rs: 4e2c9c0 2024-04-17 Truncate tweaks (#694)`, `src/bytes_mut.rs: e4af486 2024-04-09 Don't set \`len\` in \`BytesMut::reserve\` (#682)`
- `## chunks`: `diff src/bytes_mut.rs#1/1 lines=1-43 bytes=1233 consumed` / `diff coverage: complete (1/1 chunks consumed)`

Nothing was `withheld` and no chunk was `missing`; the single small diff fit entirely inside the 24000-byte bound, so I did not need a `--from` recovery read. I never re-ran the build call and never read the diff a second time from `git show` of individual commits.

**Issue-fit ledger.** No originating issue (`issues=none`); built from the PR title and body alone, per the rubric's Issue fit section and the output contract's "issue alignment was unavailable" clause.

| # | Source coordinate | Class | Row | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | `pr-body/"This PR makes advance do it automatically for cases in which it's safe to do"` | acceptance requirement (PR promise of a concrete outcome) | `BytesMut::advance` must reuse the buffer's full underlying capacity when the amount advanced equals the entire remaining length (the "safe" case), instead of going through the allocator. | **met** | Diff hunk `src/bytes_mut.rs` (`if cnt == self.remaining() { unsafe { self.set_len(0) }; return; }`); traced against `set_len` (`src/bytes_mut.rs:519-522`, only sets `self.len`) versus the pre-existing `advance_unchecked` path which shifts `ptr` and shrinks `cap` by `cnt` (`src/bytes_mut.rs:904-906`) — the new path leaves `ptr`/`cap` untouched, so the full original capacity is preserved and reusable via `spare_capacity_mut` (`src/bytes_mut.rs:1027-1032`). |
| 2 | `pr-body/"which is why I didn't put it inside advance_unchecked"` | acceptance requirement (explicit non-goal / scope boundary) | The optimization must not be applied inside `advance_unchecked`, because `split_to`/`split_off` depend on `advance_unchecked` unconditionally shifting `ptr`/`cap` to keep split halves disjoint. | **met** | The diff touches only the `Buf::advance` impl. `split_to` (`src/bytes_mut.rs:385-402`) calls `self.advance_unchecked(at)` directly (not `Buf::advance`); `split_off` (`src/bytes_mut.rs:310-325`) calls `other.advance_unchecked(at)` directly. Neither can reach the new branch. |
| 3 | `pr-body/"I'm not sure the Buf API allows it"` | supporting assertion (author's own uncertainty, not a requirement) | Whether the optimization is compatible with the `Buf` trait's documented contract for `advance`. | **met** (statically settled, not an open question) | `src/buf/buf_impl.rs:194-224` — the trait's only documented obligations for `advance` are that `chunk()` return a slice `cnt` bytes further in, and that a `cnt == 0` call never panic and be a no-op. Both hold trivially in the full-length case: `chunk()` returns an empty slice regardless of internal pointer/capacity identity once `remaining() == 0`, and the `cnt == remaining() == 0` sub-case is a genuine no-op (`set_len(0)` when `len` is already 0). No further constraint on internal pointer/capacity identity exists in the trait contract, so the author's doubt does not correspond to an unresolved fact — I do not report a question for it (rubric's static-unresolvability bar is not met: static evidence settles it). |

No `not-verifiable` rows. No repository-rule findings: no `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` exists at the merge-base for any ancestor directory of the changed path (packet §7, "Verified by direct lookup in the mirror" — I treated this pinned fact as authoritative and did not re-run the lookup myself, per the dispatch's "use its pinned values verbatim" instruction). `guidance` for the context digest is therefore the empty set.

## 3. Review once, then falsify (step 3)

**Diff read once**, from the step-2 store's `diff` output (first review, so `diff` not `delta-diff`):

```diff
diff --git a/src/bytes_mut.rs b/src/bytes_mut.rs
index 0ea0272..35e1900 100644
--- a/src/bytes_mut.rs
+++ b/src/bytes_mut.rs
@@ -1066,30 +1066,38 @@ impl Buf for BytesMut {
     #[inline]
     fn chunk(&self) -> &[u8] {
         self.as_slice()
     }

     #[inline]
     fn advance(&mut self, cnt: usize) {
+        // Advancing by the length is the same as resetting the length to 0,
+        // except this way we get to reuse the full capacity.
+        if cnt == self.remaining() {
+            // SAFETY: Zero is not greater than the capacity.
+            unsafe { self.set_len(0) };
+            return;
+        }
+
         assert!(
             cnt <= self.remaining(),
             "cannot advance past `remaining`: {:?} <= {:?}",
             cnt,
             self.remaining(),
         );
         unsafe {
             // SAFETY: We've checked that `cnt` <= `self.remaining()` and we know that
             // `self.remaining()` <= `self.cap`.
             self.advance_unchecked(cnt);
         }
     }

     fn copy_to_bytes(&mut self, len: usize) -> Bytes {
         self.split_to(len).freeze()
     }
}
```

The build call's automatic function-context widening (`--function-context`, applied by the script) already printed the whole `impl Buf for BytesMut` block (`remaining`, `chunk`, `advance`, `copy_to_bytes`), so I did not re-read that enclosing symbol separately.

**Changed tests.** The diff touches only `src/bytes_mut.rs`; `git diff master review-head --stat` confirms exactly one file, no test file changed (`tests/test_bytes.rs`, `tests/test_serde.rs`, `tests/test_buf_mut.rs` all untouched). The rubric's Changed Tests section applies "For every test function the change adds or substantively changes" — there is none, so no test-function inspection or focused execution was owed by that section. I did not run `cargo test` or any focused command: nothing the section requires needed deciding, so running the suite would have been an unrequired, budget-wasting run under `SKILL.md`'s suite-once rule and the rubric's own scope for that section. I did inspect the *existing* tests to establish whether the new fast path is exercised by anything already in CI (relevant to the maintainability candidate in §3.3 below, not to Changed Tests) — see the "beyond the diff" list.

### 3.1 Falsification method

I traced the exact invariant chain this diff depends on: `set_len` (only sets `self.len`, precondition `len <= cap`), `advance_unchecked` (moves `ptr`, shrinks `cap`, updates `vec_pos` for `KIND_VEC`, all three always together), `split_to`/`split_off` (call `advance_unchecked` directly, never `Buf::advance`), `capacity()`/`len()` (plain field reads), and the `Buf` trait's own documented contract for `advance` (`src/buf/buf_impl.rs:194-224`). I also read `truncate` (`src/bytes_mut.rs:404-429`) for its parallel "shrinking cannot expose uninitialized bytes" rationale, and two sibling same-file commits (`4e2c9c0` "Truncate tweaks", `9d3ec1c` "Resize refactor") to establish this repository's actual test-authoring convention for comparably-sized internal `BytesMut` optimizations (gate 8, proportionate rigor).

### 3.2 Candidate ledger (complete, written before any verifier dispatch)

All seven candidates below were raised, then dropped by my own falsification. None survives as a finding. This is the exact ledger given to the verifier in clean-verdict mode (§4).

| id | kind | claim | disposition | falsification reason | decisive evidence |
| --- | --- | --- | --- | --- | --- |
| `bytes_mut/advance-split-overlap` | invariant | Skipping the `ptr`/`cap` adjustment in the new full-length fast path could let a later split-off `BytesMut` share the same capacity range as `self`. | dropped | prevented — `split_to`/`split_off` call `advance_unchecked` directly, never `Buf::advance`, so the new branch is never on their call path; the split-disjointness invariant is established entirely by `advance_unchecked`, which this diff does not touch. | `src/bytes_mut.rs:397` (`split_to` calls `self.advance_unchecked(at)` directly) |
| `bytes_mut/advance-vecpos-stale` | invariant | Leaving `vec_pos` un-updated in the new fast path could desynchronize it from `ptr`, corrupting a later `reserve()` shift-to-front. | dropped | prevented — `vec_pos` tracks `ptr`'s offset from the underlying `Vec`'s original start and is only ever updated by `advance_unchecked` in lockstep with a `ptr` shift; the new fast path leaves `ptr` untouched too, so the pair stays consistent by construction. | `src/bytes_mut.rs:904` (the paired `ptr`/`vec_pos` update inside `advance_unchecked`, absent from the new branch) |
| `bytes_mut/advance-capacity-compat` | requirement | `capacity()` reporting a larger value after `advance(len())` than the pre-change code would is an observable, possibly-breaking behavior change. | dropped | intentional — the PR body states this exact outcome ("reuse the full capacity" instead of "going through the allocation machinery") as its explicit stated purpose; both reviewing maintainers approved the diff with no objection to the capacity change itself, and no documented invariant anywhere ties `capacity()` to a monotonic-decrease contract. | PR body paragraph 3; `src/bytes_mut.rs:217-219` (`capacity()`'s doc carries no monotonicity claim) |
| `bytes_mut/advance-missing-fastpath-test` | maintainability | No test exercises the new `cnt == remaining() > 0` fast path (e.g. asserting `capacity()` is preserved across `advance(len())`). | dropped | consequence unproven / disproportionate to repo norms — sibling same-file unsafe-code changes of comparable and larger size (`4e2c9c065a0` "Truncate tweaks", 3-line; `9d3ec1cffb7` "Resize refactor", 26-line, also `unsafe`-touching) shipped with no test-file changes, and two maintainers reviewed this diff twice, including one approval, without requesting a test. | commits `4e2c9c0`, `9d3ec1c` (`git show --stat`: `src/bytes_mut.rs` only, no test files) |
| `bytes_mut/advance-double-remaining-eval` | maintainability | `self.remaining()` is evaluated in both the new `if` and the retained `assert!`, adding overhead. | dropped | no-consequence — the `assert!` branch is unreachable once the fast path's condition holds (the fast path `return`s), so there is no double evaluation on the path it would matter for; `remaining()` is an inlined trivial getter (`self.len()`) with no side effects regardless. | diff hunk itself (`if cnt == self.remaining() {…return;}` followed by the retained `assert!(cnt <= self.remaining()…)`) |
| `bytes_mut/advance-safety-comment-scope` | maintainability | The safety comment "Zero is not greater than the capacity" doesn't separately justify that shrinking length can't expose uninitialized bytes. | dropped | no-consequence — `set_len`'s only documented precondition is `len <= cap` (exactly what the comment states), and shrinking never exposes uninitialized data, per the identical rationale already used for `truncate`'s own safety comment in this same file. | `src/bytes_mut.rs:520` (`set_len`'s `debug_assert`); `src/bytes_mut.rs:427` (`truncate`'s "Shrinking the buffer cannot expose uninitialized bytes") |
| `bytes_mut/advance-unchecked-scope-creep` | maintainability | The same capacity-reuse optimization could also apply inside `advance_unchecked`/`split_to` when `at == len`. | dropped | intentional / out of scope — explicitly discussed and rejected in the review record: Darksonn confirmed "The conflict with split_to and split_off is a good reason to not put it in advance_unchecked," and the author agreed ("Good idea. Fixed!"). | packet §6, non-review conversation items #1–#2 (`Darksonn`, `paolobarbolini`, 2024-04-24T08:37–08:49) |

No candidate met gates 1+4 with an unproven-but-possible consequence (the Observations route), so nothing was routed to `Observations` either — each dropped candidate above failed on a decisive, proven refutation (prevented/intentional/no-consequence/disproportionate), not merely on an absent proof of consequence. Per the rubric's Observations section, a fact that fails only gate 4 with a possible-but-unestablished consequence would be `dropped (consequence unproven)`; every row here has stronger, affirmative refuting evidence (a cited code path, a cited review-record statement, or a cited sibling-commit convention), so none is even eligible for `Observations` and none is narrated as an unpublished observation.

### 3.3 Zero-survivor trigger and clean-verdict dispatch

Zero candidates survived as findings. The changed behavior is `unsafe`, raw-pointer/length/capacity bookkeeping inside `BytesMut` — the crate's foundational buffer type — which I judge to be a data-integrity surface under `SKILL.md` step 3's zero-survivor trigger (a wrong invariant here would silently corrupt or expose stale/uninitialized bytes, not merely misbehave functionally). This fires the zero-survivor clean-verdict batch rather than a candidate batch (there is no candidate batch to send: nothing survived, nothing met the independent mandatory-verification trigger on its own).

Dispatched in the fresh context described in §4 below.

## 4. Verifier dispatch (fresh, isolated context)

- **Sub-agent role:** clean-verdict verifier (zero-survivor mode).
- **`subagent_type`:** `v5b-verifier-effort-high`.
- **Model:** `claude-sonnet-5` (passed as `model: "sonnet"` explicitly on the `Agent` call).
- **Dispatch mode:** `run_in_background: false` (foreground; I waited for the result before continuing, per dispatch rule 10).
- **Isolation:** a genuinely fresh Agent-tool context with no primary-review reasoning, confidence, or narrative carried over — only the pinned coordinates, the PR title/body, the prior-review-record summary (to prevent re-litigating already-fixed feedback), the complete diff, and the compact 7-row ledger (kind, claim, disposition, falsification reason, one decisive evidence pointer each — `support` and my own narrative withheld, per `verifier.md`).

### 4.1 Exact prompt given

The complete prompt is reproduced in full below (this is the literal text sent to the `Agent` tool; I have not paraphrased or trimmed it):

> You are an independent verifier for one code review. This is a fresh, isolated context: you have no access to and must not assume anything about a primary reviewer's reasoning, confidence, or narrative — you are given only the facts below, and you must reach your own conclusions from the cited evidence and your own inspection of the repository.
>
> ## Rules binding on you
>
> 1. Offline. No `git fetch`, `git pull`, `gh`, `curl`, web fetch, or any network call of any kind.
> 2. Clone hygiene: do not run `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the tree. Read-only inspection only.
> 3. History is truncated at the pinned head on purpose: the newest object reachable in this clone is `7052d2454a2370ab9583f63711df89f3bd7bec83`. Nothing after this pull request exists locally. At the end of your report, state explicitly whether you read any history beyond this pinned head and which history commands you ran.
> 4. Focused test execution is permitted, offline only, using cargo with environment `CARGO_HOME=/tmp/effort124/cargo-home CARGO_NET_OFFLINE=true CARGO_TARGET_DIR=/tmp/effort124/work/g-high-seed1-att-07/target`, five minutes per command, at most once, scratch crates only under `/tmp/effort124/work/g-high-seed1-att-07/`, nothing added to or changed in the clone. You are not required to run anything for this task.
> 5. Stay inside your sandbox: the clone at `/tmp/effort124/runs/g-high-seed1-att-07`, this prompt's own content, and (only if you need scratch space) `/tmp/effort124/work/g-high-seed1-att-07/`. Do not read any other path, any other run's clone/report/payload, or the skill snapshot/packet directories. If you read anything outside this list anyway, report it explicitly.
> 6. This is a clean-verdict verification task, not a search for new findings. Do not search the rest of the pull request for anything not covered by the ledger below. You may return at most one explicitly non-actionable `observation` aside (a decisive evidence pointer, no `should`/`must` language) if an accurate, sub-threshold fact surfaces incidentally — but do not manufacture one.
> 7. Do not write to, publish to, or modify anything. You cannot access the network or the pull request/forge in any way. Return your verdicts as your final message; nothing else consumes your output.
>
> ## Repository and pinned coordinates
>
> - Clone: `/tmp/effort124/runs/g-high-seed1-att-07` (local branch `master` = merge-base, local branch `review-head` = head; currently checked out at `review-head`)
> - Head SHA: `7052d2454a2370ab9583f63711df89f3bd7bec83`
> - Merge-base / base SHA: `ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401` (identical to base ref `master` here)
> - Changed file: `src/bytes_mut.rs` (+8/−0, one hunk, inside `impl Buf for BytesMut`)
> - No originating issue (`issues=none`); the only source is the pull-request title/body reproduced below.
> - No applicable base-branch repository rule files exist for this changed path (verified: no root/path-scoped `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` at the merge-base).
>
> **Pull-request title:** "Reuse capacity when possible in `<BytesMut as Buf>::advance` impl"
>
> **Pull-request body (verbatim):** *[the complete PR body, reproduced exactly as in §6 below]*
>
> **Prior human review record relevant to the ledger below (all already reflected in the pinned head; do not re-report anything here as still outstanding):**
>
> - `Darksonn` (review thread on `src/bytes_mut.rs:1074`, now-resolved): asked that the safety comment address `set_len`'s actual requirement (length not greater than capacity), and that the semicolon go outside the unsafe block. Both were applied.
> - `braddunbar` (review): asked to use `self.remaining()` consistently and to move the new conditional before the `assert!`. Both were applied. `braddunbar` then approved.
> - Non-review conversation: `Darksonn` asked "Would it make more sense to move this check to `advance_unchecked`?"; `paolobarbolini` replied that `advance_unchecked` is also called by `split_to`/`split_off`, which require it to unconditionally advance the position, so moving the check there would break those; `Darksonn` agreed this is a good reason not to. The author then said "Good idea. Fixed!" (i.e. kept the check only in `advance`, not `advance_unchecked`).
>
> **The diff (complete):** *[the same diff quoted in §3 above]*
>
> ## Task: clean-verdict mode
>
> Zero candidates survived the primary reviewer's own falsification as findings. This is the zero-survivor clean-verdict batch: attack every acquittal below and either let the clean verdict stand or re-open specific rows. Follow this procedure for every row, citing `path:line` for each step:
>
> 1. Restate the row's decisive premise in one sentence.
> 2. State the concrete condition under which that premise would be false.
> 3. Trace the *opposite* branch of every conditional the premise depends on through the current code, citing `path:line` for each step.
> 4. Either construct the complete failing state transition from trigger to observable consequence, or cite the specific step that is impossible.
> 5. Re-reading the row's own reasoning and agreeing with it is not a verdict: a `holds` ruling — including any row you cover under a blanket `clean verdict stands` — must cite at least one line the row itself did not cite.
>
> Attack depth by `kind`: the five steps above apply IN FULL to every row whose `kind` is `bug`, `concurrency`, `invariant`, or `security`. For every other row (`performance`, `maintainability`, `requirement`) — unless it asserts a safety claim — do a one-citation check instead: read the row's evidence pointer, confirm or contradict its stated fact, and return `holds`/`re-open` without tracing conditionals.
>
> Two of the rows below are `kind: invariant`, so also apply this addendum to them specifically (it adds no new verdict track, just extra rigor inside your `holds`/`re-open` reasoning for those two rows):
>
> - State the invariant at the rule level (name which fields/pointers must stay consistent with which operations, and under which conditions that consistency held at the merge-base), not at the transition level.
> - Enumerate the sibling code paths governed by the rule (here: `advance`, `advance_unchecked`, `split_to`, `split_off`, `reserve`) and state for each whether the row's claimed protection actually covers it.
> - If the row's premise can only be defeated by one specific interleaving or call path, name it explicitly; if none exists, say so.
>
> Return, for **every** row: `holds` or `re-open`, with your citations. In addition, return exactly one of these two batch conclusions:
>
> - `clean verdict stands` — every row survives your attack; OR
> - `disposition <id> does not hold; re-open it` — once for each row whose stated acquittal you find contradicted or unsupported.
>
> You may also return at most one non-actionable `observation` aside (optional) if something accurate and sub-threshold surfaces incidentally that neither rules on a row's safety nor contradicts a row.
>
> ## The complete candidate disposition ledger (7 rows — attack every one)
>
> *[the same 7-row ledger reproduced in §3.2 above, each with id, kind, claim, disposition, falsification reason given, and decisive evidence cited]*
>
> Read the cited code yourself at both head and merge-base as needed (`git show ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401:src/bytes_mut.rs` for merge-base versions). Return your complete verdict now.

(The two `*[...]*` elisions above are exact reproductions of text already given in full in §3 and §3.2 of this report; I have not shortened or altered them in the actual prompt, only in this transcript to avoid duplicating several hundred words verbatim twice in the same document. Everything else is the literal prompt text.)

### 4.2 Verbatim report returned

> All citations verified against the repository at the pinned head (`7052d2454a2370ab9583f63711df89f3bd7bec83`) and merge-base (`ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401`, which equals the parent of the head commit, so no separate merge-base check-out was needed — the file at merge-base is what's shown minus the diff hunk).
>
> ## Row-by-row verdicts
>
> **1. `bytes_mut/advance-split-overlap`** (invariant) — **holds**
> - Premise: `split_to`/`split_off` never reach the new fast path because they call `advance_unchecked` directly, not `Buf::advance`.
> - False-condition: some code path would have to invoke `<BytesMut as Buf>::advance` as part of constructing a second handle sharing the same allocation.
> - Opposite-branch trace: `split_to` (`src/bytes_mut.rs:397`) and `split_off` (`src/bytes_mut.rs:320`) both call `self.advance_unchecked(...)`/`other.advance_unchecked(...)` directly — confirmed by direct read, not just the row's own citation of line 397. I additionally traced every `.advance(` call site in the crate (`src/buf/chain.rs`, `src/buf/take.rs`, `src/buf/reader.rs`, `src/buf/buf_impl.rs`, `src/buf/buf_mut.rs`) — all are generic `Buf`/`BufMut` combinator wrappers, none of which participate in `split_to`/`split_off`/`reserve`'s internal implementation.
> - Rule-level invariant: two `BytesMut` handles derived from one allocation via split must reference disjoint `[ptr, ptr+cap)` ranges; this is established solely by `advance_unchecked`'s ptr shift (`src/bytes_mut.rs:904-906`) coupled with the cap truncation each split function performs on itself (`split_off` line 321-322, `split_to` line 398-399). The new fast path (`src/bytes_mut.rs:1068-1075`) never calls `shallow_clone`/creates a second handle — it only mutates `self.len`, so it cannot be the site of an overlap regardless of which call path reaches it.
> - Sibling coverage: `advance` (fast path is a no-op for ptr/cap, so trivially non-violating), `advance_unchecked` (untouched by diff), `split_to`/`split_off` (never call `Buf::advance`), `reserve`/`reserve_inner` (its own ptr shift at line 636 is independent of this diff). No interleaving defeats the premise.
> - Extra citation beyond the row's own (`:397`): `src/bytes_mut.rs:320` (`split_off`'s direct `advance_unchecked` call) and `src/bytes_mut.rs:1068-1075` (fast path never creates a second handle).
>
> **2. `bytes_mut/advance-vecpos-stale`** (invariant) — **holds**
> - Premise: `vec_pos` (packed into `self.data`, see `get_vec_pos`/`set_vec_pos` at `src/bytes_mut.rs:985-994`) is only mutated by `advance_unchecked` (`:891`) and `reserve_inner` (`:637`, only after physically shifting `ptr` back to the vec base at `:636`), always in lockstep with a `ptr` move. The new fast path touches neither `ptr` nor `data`/`vec_pos`.
> - False-condition: any code path that changes `len` without leaving `ptr` fixed, while the reader still trusts `vec_pos` as an accurate ptr-offset.
> - Opposite-branch trace: `truncate` (`src/bytes_mut.rs:424-429`) already sets `self.len` via `set_len` without touching `vec_pos`, establishing the existing precedent that length-only mutations never require a `vec_pos` update — `vec_pos` encodes a `ptr` offset, not a length. The new fast path (`:1068-1075`) does exactly the same class of mutation (`set_len(0)`), so it inherits the same correctness argument, not a novel one.
> - Sibling coverage: `advance` fast path (len-only, safe by the `truncate` precedent), `advance_unchecked` (unchanged, still updates `ptr`+`vec_pos` together at `:888-906`), `split_to`/`split_off` (route through `advance_unchecked`, unaffected), `reserve`/`reserve_inner` (its own `ptr`/`vec_pos` pairing at `:633-637` is untouched by this diff). No interleaving desyncs the pair because the fast path never writes `ptr` or `data`.
> - Extra citation beyond the row's own (`:904`): `src/bytes_mut.rs:424-429` (truncate's identical len-only precedent) and `src/bytes_mut.rs:985-994` (`vec_pos` storage/accessors showing it's independent of `len`).
>
> **3. `bytes_mut/advance-capacity-compat`** (requirement) — **holds**
> - One-citation check: `src/bytes_mut.rs:217-219` confirms `capacity()`'s doc comment and body (`self.cap`) carry no monotonicity contract. PR body explicitly states the capacity-reuse behavior as the intended purpose. Fact confirmed as stated.
>
> **4. `bytes_mut/advance-missing-fastpath-test`** (maintainability) — **holds**
> - One-citation check: verified via `git show --stat` that commit `4e2c9c065a06bf9cb5d7dd46e3b29f62a1c20057` (2 lines) and `9d3ec1cffb76141b4706bb289beced8b04ecac4a` (26 lines, 17 insertions/9 deletions) both touch only `src/bytes_mut.rs` with no test-file changes. Matches the row's claim exactly.
>
> **5. `bytes_mut/advance-double-remaining-eval`** (maintainability) — **holds**
> - One-citation check: `src/bytes_mut.rs:1058-1060` confirms `remaining()` is `self.len()`, a trivial inlined getter with no side effects; and the diff hunk itself (`src/bytes_mut.rs:1071-1082`) confirms the fast path `return`s before the `assert!`, so no double-evaluation occurs on the path where it would matter. Confirmed.
>
> **6. `bytes_mut/advance-safety-comment-scope`** (maintainability) — **holds**
> - One-citation check: `src/bytes_mut.rs:520` confirms `set_len`'s only precondition is `len <= self.cap`; `src/bytes_mut.rs:427` confirms `truncate`'s adjacent safety comment uses the identical "cannot expose uninitialized bytes" rationale for the same class of length-shrink operation. Confirmed.
>
> **7. `bytes_mut/advance-unchecked-scope-creep`** (maintainability) — **holds**
> - One-citation check: this row's evidence is the review-record conversation supplied in the task prompt itself (not independently verifiable from repo code, but it is given as established, already-reflected-at-head context, not a code fact to re-derive). Cross-checked against the diff: `advance_unchecked` (`src/bytes_mut.rs:872-907`) indeed contains no such fast path, consistent with the claim that the optimization was deliberately kept out of it. Confirmed consistent with the code.
>
> ## Batch conclusion
>
> **clean verdict stands**
>
> All seven rows survive the attack. For the two `invariant` rows I traced the opposite branch of every conditional the premise depends on (all `.advance(` call sites in the crate, `reserve_inner`'s independent ptr/vec_pos pairing, and `truncate`'s precedent for len-only mutation) and cited lines beyond what each row originally cited (`:320`, `:1068-1075` for row 1; `:424-429`, `:985-994` for row 2), per the instructions. No complete failing state transition could be constructed for any row.
>
> **Sandbox/history disclosure:** I ran only `git log --oneline -3` on `master`/`review-head`, `git merge-base master review-head`, and `git show --stat` on the two named historical commits (`4e2c9c0`, `9d3ec1c`), all of which are ancestors of the pinned head and were already named in the ledger — no history beyond the pinned head (`7052d2454a2370ab9583f63711df89f3bd7bec83`) was read, and no `fetch`/`pull`/network command was run. No tree-mutating commands were run; all reads were via `Read`/`Grep`/`git show`/`git log` (read-only). No paths outside `/tmp/effort124/runs/g-high-seed1-att-07` were accessed.
>
> No non-actionable observation to add beyond the above.

**Sub-agent's own reported usage:** `subagent_tokens: 37250`, `tool_uses: 17`, `duration_ms: 112159` (reported by the harness alongside the agent's completion; I report it verbatim, not estimated).

### 4.3 What I did with the return

The batch conclusion is `clean verdict stands` with `holds` on all seven rows and citations beyond what each ledger row itself supplied (satisfying the reference's "must cite at least one line the ledger row did not cite" rule for every `holds`, including the two full-depth `invariant` rows). No row was re-opened. Per `SKILL.md` step 3: "A successful clean-verdict batch does not retrigger itself." No follow-up batch is owed (nothing became render-eligible, nothing was re-opened, and the mandatory-verification trigger never applied to any candidate in the first place, so there was never a candidate batch to run in addition to this clean-verdict batch). The one-initial-plus-one-follow-up cap was not approached: exactly one batch ran, and none is left to run. Status remains `Approved` (advisory), unchanged from the provisional derivation in §0a.

## 5. Everything consulted beyond the diff

All of the following were read from the offline clone at `/tmp/effort124/runs/g-high-seed1-att-07` unless noted otherwise. None of these searches were repo-wide grep sweeps over the whole tree except where marked; I used targeted `Read`/`Grep` calls scoped to the one changed file and its direct dependencies (the `Buf` trait definition and the existing test files), each named against the specific risk or gate it served (risk-led discovery / Complete inspection):

| # | What | Why (risk/gate served) | Repo-wide? | Case-insensitive? |
| --- | --- | --- | --- | --- |
| 1 | `git status`, `git log --oneline -5 master`, `git log --oneline -5 review-head`, `git diff master review-head -- src/bytes_mut.rs \| head -100` | Orient the clone; confirm both branches' tips and that the diff matches the packet's stated +8/−0 on one file | No | N/A |
| 2 | `python3 review_context.py --merge-base ... --head ... --store ...` (step 2 build call) | The mandated single diff read | No (single file manifest) | N/A |
| 3 | `git show ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401:src/bytes_mut.rs \| sed -n '1000,1095p'` | Confirm the exact merge-base (pre-diff) shape of `impl Buf for BytesMut` | No | N/A |
| 4 | `grep -n "fn advance_unchecked\|fn set_len\|fn len(\|fn capacity\|fn split_off\|fn split_to\|fn split(\|fn as_slice\|fn as_mut_slice\|struct BytesMut\|fn with_capacity\|fn cap\b" src/bytes_mut.rs` | Locate every function whose invariant the new fast path could interact with (candidates C1/C2/C3/C6) | Scoped to `src/bytes_mut.rs` only, not repo-wide | Case-sensitive (regex has no `-i`) |
| 5 | `Read src/bytes_mut.rs` offset 490-560 (`set_len`, `reserve` doc) | Confirm `set_len`'s only precondition (`len <= cap`) — decisive for C6 | No | N/A |
| 6 | `Read src/bytes_mut.rs` offset 840-900 (`from_vec`, `as_slice`, `as_slice_mut`, `advance_unchecked` start) | Confirm `advance_unchecked`'s `KIND_VEC` branch and `vec_pos` handling — decisive for C1/C2 | No | N/A |
| 7 | `Read src/bytes_mut.rs` offset 899-970 (`advance_unchecked` tail, `try_unsplit`, `kind`, `promote_to_shared`) | Confirm the `ptr`/`cap` shift that pairs with `vec_pos` — decisive for C1/C2 | No | N/A |
| 8 | `Read src/bytes_mut.rs` offset 180-220 (`len`, `is_empty`, `capacity`) | Confirm `capacity()` carries no monotonicity doc contract — decisive for C3 | No | N/A |
| 9 | `Read src/bytes_mut.rs` offset 300-430 (`split_off`, `split`, `split_to`, `truncate`) | Confirm split functions call `advance_unchecked` directly (not `Buf::advance`) and capture `truncate`'s parallel safety rationale — decisive for C1 and C6 | No | N/A |
| 10 | `grep -rn "\.advance(" tests/` then `grep -rln "BytesMut" tests/`, and `git diff master review-head --stat` | Confirm no test file is touched by the diff and locate every existing `BytesMut`-related test file, to scope the Changed Tests section correctly | Scoped to `tests/`, not the whole repo | Case-sensitive |
| 11 | `Read tests/test_bytes.rs` offset 640-694 (`advance_static`, `advance_vec`, `advance_bytes_mut`, `advance_past_len`) | Confirm no existing test exercises the new `cnt == remaining() > 0` fast path — decisive for C4 | No | N/A |
| 12 | `git show --stat 4e2c9c0`, `git show 9d3ec1c --stat -- .` | Establish repository convention for test-authoring on comparably-sized internal `BytesMut` optimizations — decisive for C4 (gate 8, proportionate rigor) | No (two named ancestor commits) | N/A |
| 13 | `grep -n "fn advance" src/buf/buf_impl.rs` then `Read src/buf/buf_impl.rs` offset 1-80 and 195-225 | Locate and read the `Buf` trait's documented contract for `advance` — decisive for Issue-fit row 3 (the author's own stated uncertainty) | Scoped to `src/buf/buf_impl.rs` | Case-sensitive |
| 14 | `grep -n "monoton\|capacity.*decreas\|decreas.*capacity" src/*.rs CHANGELOG.md` | Check for any documented capacity-monotonicity invariant that the diff might violate — decisive for C3 | Scoped to `src/*.rs` and `CHANGELOG.md` (a glob, not a full recursive repo sweep) | Case-sensitive |

No focused test or repro command was run (rule/§3 above): the diff adds or changes no test function, so nothing under the rubric's Changed Tests section required deciding by execution, and running the existing full suite would have been an unrequired use of the once-per-run allowance with nothing to decide. I judged that my static trace of `set_len`/`advance_unchecked`/`split_to`/`split_off`/`capacity()` was sufficient and decisive (each conclusion is cited to an exact `path:line`), so I did not additionally build a scratch crate to empirically probe the optimization; the verifier likewise ran no test.

## 6. The `context` digest and its inputs

**Digest:** `ea94526181af0db99933265225e9cb726540a9c0b839990daee177aff1f81e5e`

**Command:**
```
python3 scripts/context_fingerprint.py /tmp/effort124/work/g-high-seed1-att-07/pr_input.json
```
run once, from the skill directory, against a JSON file I constructed under my own work directory (`/tmp/effort124/work/g-high-seed1-att-07/pr_input.json`).

**Inputs it was computed from** (the `--json`/plain-input direct-supply mode described in `output-contract.md`'s `context` paragraph — "On a forge without that packet, supply `pr`, `issues`, `specs`, and `guidance` directly from the exact reviewed inputs" — since no live GraphQL fetch happened in this offline cell; see the judgment call recorded in §10):

- `pr.title`: `Reuse capacity when possible in \`<BytesMut as Buf>::advance\` impl`
- `pr.body`: the complete pull-request body reproduced verbatim in §1 of the packet, extracted programmatically (via a small Python script reading the exact byte range between the ```` ```` ```` fences in `packet.md` §3, to avoid any manual-transcription error) and embedded unmodified in the JSON input file.
- `issues`: `[]` (no originating issue; `issues=none`)
- `specs`: `[]` (no user-supplied spec)
- `guidance`: `[]` (no root or path-scoped `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` at the merge-base, per packet §7's verified-at-the-mirror table, which I did not re-verify myself — see §10)

I confirmed the digest is reproducible by inspecting `context_fingerprint.py`'s `normalize()` function directly: only `pr.title`, `pr.body`, `issues`, `specs`, and `guidance` feed the canonical JSON that is hashed; no other field (author, dates, association) participates.

## 7. Mechanism checklist

| Mechanism | Fired? | Where demonstrated |
| --- | --- | --- |
| Question channel | Did not fire | The one candidate that looked like it might need a question (Issue-fit row 3, the author's stated `Buf`-API doubt) was statically settled by reading the trait's own documented contract (`src/buf/buf_impl.rs:194-224`); the rubric's static-unresolvability bar was not met, so no question was published (§2, Issue-fit table row 3). |
| Clean-verdict / related-acquittal verification | Clean-verdict fired (zero-survivor mode); related-acquittal mode did not apply | Zero candidates survived as findings, and the diff is a data-integrity surface (unsafe pointer/length/capacity bookkeeping) — §3.3 states the trigger reasoning; the full batch and verbatim return are in §4. No survivor existed, so there was no related-acquittal set to fold in. No row was re-opened, so there was no re-open re-entry into primary falsification. |
| Observations | Did not fire | Every dropped candidate failed on an affirmative, decisive refutation (prevented / intentional / no-consequence / disproportionate-to-convention), not merely on an unproven consequence, so none qualified for the Observations route (rubric: "A fact that passes gates 1 and 4 at any priority is a finding... A fact that might meet the finding gates with more available static work remains a candidate, not an observation" — none of these seven needed more static work; each was conclusively closed). See the "no candidate met gates 1+4..." paragraph immediately after the ledger table in §3.2. |
| Fix-sufficiency check on any concurrency/invariant candidate | Fired, in the verifier's return | Two ledger rows are `kind: invariant` (`bytes_mut/advance-split-overlap`, `bytes_mut/advance-vecpos-stale`). The verifier stated each rule at the rule level ("two `BytesMut` handles derived from one allocation via split must reference disjoint `[ptr, ptr+cap)` ranges"; "`vec_pos` ... always in lockstep with a `ptr` move"), enumerated the sibling code paths governed by the rule (`advance`, `advance_unchecked`, `split_to`, `split_off`, `reserve`/`reserve_inner`) for both, and stated for each whether the row's claimed protection covers it — see §4.2, rows 1 and 2. There was no "proposed `change`" to widen (these are acquitted rows, not confirmed bug findings), so the "widen `change` to the rule" step of `verifier-concurrency.md` was not applicable in this direction; the addendum was otherwise applied in full as instructed. |
| Follow-up verifier round | Did not fire | `SKILL.md`: "A successful clean-verdict batch does not retrigger itself." Nothing was re-opened and no candidate newly became render-eligible, so no follow-up batch was owed or run (§4.3). Total batches run: 1 of the allowed 1-initial-plus-1-follow-up cap. |
| Deferral handling | Did not fire (no deferral exists) | The prior review record (packet §6) contains no explicit deferral of a design/naming/API-shape decision ("we can fix this later", "revisit the name", etc.) — every review comment was either a concrete, already-applied request (safety-comment wording, semicolon placement, `remaining()`-vs-`len` consistency, conditional ordering) or the `advance_unchecked`-vs-`advance` design discussion, which was resolved (not deferred) within the same conversation. I recorded this as a candidate (`bytes_mut/advance-unchecked-scope-creep`) and dropped it as intentional/settled, not as an open deferral. |
| Retrospective mode | Fired | The `Mode` line is present in both the payload (`g-high-seed1-att-07-payload.md`) and this report's derivation (§0a): `**Mode:** Retrospective review of merged pull request; publication disabled.` Publication was skipped throughout; step 6's "render instead and stop" instruction was followed — I never attempted a `gh api --method POST` call or any write, and I re-derived the would-be summary/batch purely via `validate_review.py --render`/`--emit-batch`, never composing a URL or comment by hand. |

## 8. History discipline

I read git history, but never beyond the pinned head `7052d2454a2370ab9583f63711df89f3bd7bec83`; every commit I inspected is that commit or one of its ancestors (all reachable from `master`, which is pinned to the merge-base and is itself an ancestor of `review-head`). Exact history commands run, myself:

```
git status
git log --oneline -5 master
git log --oneline -5 review-head
git diff master review-head -- src/bytes_mut.rs | head -100
git show ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401:src/bytes_mut.rs | sed -n '1000,1095p'
git show --stat 4e2c9c0
git show 9d3ec1c --stat -- .
git status --porcelain (final hygiene check)
git rev-parse HEAD
git branch -v
```

The verifier sub-agent, independently, ran (per its own disclosure in §4.2): `git log --oneline -3` on `master`/`review-head`, `git merge-base master review-head`, and `git show --stat` on `4e2c9c0` and `9d3ec1c` — the same two ancestor commits I had already named in its ledger, nothing new and nothing beyond the pinned head.

No `git fetch`, `git pull`, `gh`, `curl`, or any network call was made by me or (per its disclosure) by the verifier.

## 9. Sandbox disclosure

I read only: the skill snapshot at `/tmp/effort124/skill/snapshot-path-omitted/` (SKILL.md and the five references it named on the branches that applied: `review-rubric.md`, `output-contract.md`, `verifier.md`, `verifier-concurrency.md`, and `re-review.md` — the last only to confirm its trigger did not fire, per SKILL.md step 1's instruction), the packet at `/tmp/effort124/packets/g/packet.md`, the clone at `/tmp/effort124/runs/g-high-seed1-att-07`, and my own work/report/payload/timing paths under `/tmp/effort124/work/g-high-seed1-att-07/` and `/tmp/effort124/reports/g/`. I did not read `conformance.md` (no versioned artifact was named by any source) beyond noting from `review-rubric.md`'s own text that it would only apply if one existed.

While listing `/tmp/effort124/reports/g/` to confirm the timing sidecar existed, I incidentally observed the *names* of two files belonging to a different attempt in the same shared directory (`g-medium-seed1-att-08-session.txt`, `g-medium-seed1-att-08-timing.json`) via a directory listing (`ls -la`) — I did not open, read, or otherwise use their contents, only saw their filenames as a side effect of listing the shared parent directory that the dispatch itself designated as my report output location. Disclosing this per rule 7's "report it if you read one anyway," even though only filenames (not contents) were seen and the directory itself is where the dispatch told me to write my own files.

No other path outside the sandbox was read. I did not read any other run's clone, report, or payload.

## 10. Notes — judgment calls on the skill's contract

1. **No live forge fetch was performed.** `SKILL.md` step 1 specifies a `gh api graphql` call producing `forge-*.json` pages, then `forge_packet.py normalize` to build `packet.json`, from which `context_fingerprint.py --packet` would read `pr`/`issues`. This cell is offline by design and supplies the equivalent already-resolved facts via `packet.md` instead (packet run-condition 1: "If your skill's phase 1 asks you to resolve the target from the forge, that phase is satisfied by this packet"). I treated this as licensing the `context_fingerprint.py`'s direct-JSON-input mode ("On a forge without that packet, supply `pr`, `issues`, `specs`, and `guidance` directly from the exact reviewed inputs") rather than fabricating synthetic `forge-*.json` GraphQL response files to feed `forge_packet.py normalize`, which would have required inventing numeric comment ids, `pageInfo` structures, and other fields the packet does not supply and that I have no authority to invent. I extracted the PR title/body programmatically from the packet's own verbatim section to avoid transcription drift, and used empty lists for `issues`/`specs`/`guidance` per the packet's own explicit statements (`issues=none`; no guidance files present).
2. **`re-review.md` was read but its branch does not apply.** SKILL.md step 1 says to read it "When the packet holds any prior review, reply, or trailer-bearing comment from the posting identity." The packet's own "Posting identity" row states `kamui` "did NOT author the PR and has no prior comments or reviews on it," which I treated as dispositive that this is a first review, not a re-review, even though the packet does record *other* participants' (Darksonn, braddunbar, paolobarbolini) reviews and comments. Those are prior review record from other people, useful as context for gate 6 (unintentional) and for confirming already-applied feedback, but not "prior state from the posting identity" that would trigger `re-review.md`'s own machinery (duplicate-review shortcut, delta scope, reply dispositions).
3. **The zero-survivor clean-verdict trigger's "data-integrity surface" judgment.** `SKILL.md` step 3 names three trigger surfaces for the zero-survivor clean-verdict batch: "a concurrency or failover path, a data-integrity surface, or a security or authorization boundary." `BytesMut::advance` is not concurrency (no cross-thread state) and not security/authorization in the usual sense, but it is `unsafe` code directly manipulating a buffer's length/capacity/pointer invariants — a wrong invariant here would corrupt or expose stale/uninitialized memory. I judged this squarely a "data-integrity surface" and ran the clean-verdict batch rather than skip verification; I consider this the more conservative and better-supported reading given the rubric's own repeated emphasis on unsafe-code guarantee changes (gate 2's explicit unsafe-guarantee language) as the paradigm case this rubric was built to catch.
4. **Kind labeling `bytes_mut/advance-split-overlap` and `bytes_mut/advance-vecpos-stale` as `kind: invariant`** rather than plain `bug`, even though both were dropped (not survivors), so as to trigger the verifier's full five-step attack depth and the `verifier-concurrency.md` addendum on them specifically, on the view that a cross-path state-consistency claim about `ptr`/`cap`/`vec_pos` is exactly what that kind exists to flag for deeper adversarial attack, survivor or not. `review-rubric.md`'s Private finding record section only requires kind for routing/attack-depth purposes and does not restrict it to survivors.
5. **No packet gap, no unrecoverable input, and no re-fetch-before-write step.** The output contract's Publication invariants require re-fetching the head immediately before the first write and aborting on a stale or unreadable head; since this cell is offline and non-publishing by design, there is no live head to re-fetch, and rule 2/`SKILL.md` step 6 direct that in non-publishing retrospective mode I "skip the write and report the complete would-be review instead," which is what §11 below and the payload file do. I did not attempt a network re-fetch of the PR head (which would have violated the offline constraint) and instead relied on the packet's pinned head and the clone's own `git rev-parse HEAD` (confirmed identical to the pinned SHA in §9's final hygiene check) as the closest available integrity check.
6. **Word budget on the seven ledger rows' one-line claims/falsification-reasons** in §3.2 runs slightly longer than a strict one-clause "one-line" in a couple of rows (e.g. the invariant rows' falsification reasons), because the underlying mechanism (pointer/capacity/`vec_pos` triple-consistency across four sibling functions) genuinely needs that much text to state precisely; I judged terse-to-the-point-of-vague worse than a slightly longer single sentence, consistent with the rubric's general instruction to prefer decisive, checkable prose over brevity for its own sake.

## 11. Where the complete would-be review and payload live

- **Payload (rendered exactly as it would be published):** [`/tmp/effort124/reports/g/g-high-seed1-att-07-payload.md`](file:///tmp/effort124/reports/g/g-high-seed1-att-07-payload.md)
- **`validate_review.py` (no `--flag`):** exit `0`, zero violations.
- **`validate_review.py --render`:** exit `0`, empty output (no findings or questions to render).
- **`validate_review.py --emit-batch`:** exit `0`; produced the one-call batch JSON reproduced in this report's working notes (§ above) — `commit_id=7052d2454a2370ab9583f63711df89f3bd7bec83`, `event=COMMENT`, `comments: []`.
- No forge write was attempted (retrospective, non-publishing mode). No review URL, no finding URLs, no disputed findings, nothing failed to publish because nothing was submitted for publication; the complete would-be review is the payload file linked above, standing in for those in the reporting requirement (`SKILL.md` step 6's final paragraph).

