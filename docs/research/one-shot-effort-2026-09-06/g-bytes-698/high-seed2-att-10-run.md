# Research report — target (g) `tokio-rs/bytes#698`, cell `g-high-seed2`, attempt `att-10`

## 1. Metadata

- **Target:** `tokio-rs/bytes#698` — "Reuse capacity when possible in `<BytesMut as Buf>::advance` impl"
- **Cell / attempt:** `g-high-seed2` / `att-10`
- **Skill and pin:** `legacy reviewer` (the current, non-legacy skill), read in full from `/tmp/effort124/skill/snapshot-path-omitted/` (`SKILL.md`, `references/review-rubric.md`, `references/output-contract.md`, `references/verifier.md`). `references/re-review.md` and `references/conformance.md` were not read: no prior state from the posting identity exists (first review by `kamui`) and no source names a versioned artifact this change must conform to. `references/verifier-concurrency.md` was not read: no surviving or related candidate has `kind` `concurrency` or `invariant`.
- **Model:** I (the primary reviewer) ran on `claude-sonnet-5`. The one verifier sub-agent I dispatched ran on `model: "sonnet"` via `subagent_type: "v5b-verifier-effort-high"`, per the cell's binding instruction.
- **Verification trigger fired:** Zero-survivor clean-verdict mode (`SKILL.md` step 3 / `verifier.md`'s clean-verdict task). Zero candidates survived as findings, and the changed behavior sits on a data-integrity surface (raw-pointer/unsafe buffer-length manipulation in `BytesMut`), so a clean-verdict batch over the complete disposition ledger was mandatory instead of being optional.
- **Sub-agents spawned:** 1 — role: clean-verdict verifier; `subagent_type: v5b-verifier-effort-high`; `model: sonnet`; `run_in_background: false`. No other sub-agents were spawned (per the dispatch rules, I performed the entire primary review myself and never delegated the review itself).
- **Candidates raised:** 3 (`C1` bug/memory-safety on the `set_len(0)` shortcut; `C2` maintainability on the three already-applied review-thread requests; `C3` maintainability on a possible `self.clear()` simplification).
- **Candidates surviving my own falsification (as findings):** 0.
- **Verifier verdicts:** `clean verdict stands` — all three ledger rows (`C1`, `C2`, `C3`) ruled `holds`; zero rows re-opened; one non-actionable verifier observation aside (about `C2`'s unverifiable-offline provenance claim, not affecting disposition). See §7 for the full verbatim exchange.
- **Findings for publication:** none.
- **Questions:** none — no candidate reached the static-unresolvability bar (Issue-fit rubric: no source left a material, unsettled outcome-changing fact; both PR-text promises are `met`).
- **Observations:** 1 (of the 3-item cap) — `C3`, routed to Observations because it failed admission specifically on proven consequence (gate 4), not because the underlying fact is inaccurate. See §2 for full text and §3 for the ledger row.
- **Coverage:** complete — see §5 and §7.
- **Derived status:** `Approved (advisory)` (`COMMENT` event; posting identity `kamui` is not authorized to gate, and this is a retrospective/merged-target review with publication disabled by default).
- **Token usage:** the harness available to me in this session does not report my own (primary reviewer) token usage; I have no figure to give for myself. The verifier sub-agent's dispatch did return harness-level usage metadata to me: `subagent_tokens: 31886`, `tool_uses: 9`, `duration_ms: 108398`.

## 2. Findings for publication (full)

**None.** Zero candidates survived primary falsification (see §3), and the mandatory zero-survivor clean-verdict verification (§7) returned `clean verdict stands`, so no candidate re-opened. There is nothing to render as a finding comment.

The one published Observation (not a finding — no priority, action, id, or anchor comment):

> The new fast path in `advance()` duplicates the effect of the existing `clear()`/`truncate(0)` helpers, which already reset `len` to 0 under the same `set_len` safety contract. Evidence: `src/bytes_mut.rs:1069-1073`, `src/bytes_mut.rs:424-431`.

This is `C3` from the ledger below, routed to Observations because it fails finding admission specifically on rubric gate 4 (proven consequence) — I could not establish that routing through `clear()`/`truncate(0)` would be a net improvement (see the falsification reason in §3), only that the two code paths have the same *effect*. The fact itself (duplication of effect) is accurate and has decisive evidence, so it is not silently dropped.

The complete rendered review (summary body, `Mode` line, run trailer, and the single Observation) is at [`/tmp/effort124/reports/g/g-high-seed2-att-10-payload.md`](/tmp/effort124/reports/g/g-high-seed2-att-10-payload.md).

## 3. Complete private disposition ledger

One row per candidate raised. All three were falsified (dropped) by me before any verifier dispatch; the verifier batch in §7 re-attacked all three as the zero-survivor clean-verdict ledger.

| id | kind | disposition | decisive evidence | falsification reason |
| --- | --- | --- | --- | --- |
| `C1` — `bytes_mut/advance-set-len-safety` | bug (memory-safety/invariant-adjacent) | dropped (safe) | `src/bytes_mut.rs:519-521` (`set_len`'s only contract is `len <= self.cap`, `debug_assert!`); `src/bytes_mut.rs:217-218` (`capacity()` returns `self.cap` directly, untouched by any `len` write); `src/bytes_mut.rs:985-994` (`get_vec_pos`/`set_vec_pos` read/write the `data` bit-packed word, never `len`); confirmed empirically — scratch program (§5) exit 0 across full-consume, partial-advance, zero-advance, over-advance-panics, and post-`split_to` scenarios | **Claim falsified.** `0 <= self.cap` holds unconditionally since `cap: usize`, so the safety comment ("Zero is not greater than the capacity") is always true and the `debug_assert!` inside `set_len` can never fire for this call site. `ptr`, `cap`, the vec-position bookkeeping, and any `Shared`/ref-count state are all untouched by a `len`-only write, so no invariant that `capacity()`, `split_to`/`split_off`, or the vec-position machinery relies on is disturbed. The change is a faithful inline reimplementation of what `clear()`/`truncate(0)` already do safely at the same call frequency (only when `cnt == remaining()`). |
| `C2` — `bytes_mut/advance-stale-review-requests` | maintainability | dropped (already satisfied at head) | `src/bytes_mut.rs:1069-1078` compared against the packet §6 review-thread quotes | **Claim falsified.** All three review-thread requests reproduced verbatim in the packet (§6) are already applied at the reviewed head: the conditional precedes the `assert!` (braddunbar's request 2); `self.remaining()` is used consistently in both the new condition and the pre-existing assert, not mixed with `self.len` (braddunbar's request 1); the safety comment reads `// SAFETY: Zero is not greater than the capacity.` verbatim, matching Darksonn's suggested replacement exactly; and the semicolon after `unsafe { self.set_len(0) }` sits outside the block, matching Darksonn's third comment ("that way it fmts on one line"). Nothing from the prior review record is still outstanding at this head. |
| `C3` — `bytes_mut/advance-duplicates-clear` | maintainability | **survivor, routed to Observations** (fails gate 4, not gate-1 accuracy) | `src/bytes_mut.rs:1069-1073` (new code) vs. `src/bytes_mut.rs:424-431` (`truncate`) and `:443-445` (`clear`); `#[inline]` present on `advance` (`:1067`) and `set_len` (`:518`) but absent on `truncate`/`clear` | **Not admitted as a finding; not dropped outright either.** The fact that the 4-line block duplicates `clear()`'s effect is accurate and decisively evidenced, so it is not silently discarded, but I could not establish that replacing it with `self.clear()` would be an actual improvement: `truncate`/`clear` are not marked `#[inline]` the way `advance` and `set_len` are, so routing through them would add a non-inlined call boundary plus a redundant `len < self.len()` re-check inside the exact fast path this PR exists to make cheap. Because the claimed "meaningful impact" (gate 1) and "proven consequence" (gate 4) are contested by this plausible, uncontradicted counter-consideration rather than established, the row cannot be admitted as a finding at any priority; it is not a contestable rubric *term* (no `Ambiguities` entry), it is a code-quality judgment with a genuine but unproven upside, so it is routed to Observations per the rubric's "fails specifically on meaningful/proven consequence" route rather than treated as a `consider` finding or silently dropped. |

No row was merged or deduplicated (three genuinely distinct claims). No row required an `Ambiguities` entry (no rubric or contract *term* had two supportable readings here — `C3` is a judgment call about code quality, not a term dispute).

## 4. Sub-agent dispatch — exact prompt and verbatim report

See §7 (Mechanism checklist) for the narrative; the exact prompt and the verbatim returned report are reproduced there in full to avoid duplication, since the rubric's clean-verdict task and this report's "sub-agent dispatch" requirement cover the same one batch.

## 5. Everything consulted beyond the diff

All of the following were read from the pinned clone `/tmp/effort124/runs/g-high-seed2-att-10` (offline, no network) unless noted. None of these searches were repository-wide; each was a targeted `grep -n`/`sed -n` on a single named file, justified by the risk-led-discovery rule (data-integrity surface: raw pointer/capacity/length bookkeeping in `BytesMut`) or by tracing a specific candidate. None needed to be case-insensitive (all patterns are exact Rust identifiers).

1. `git diff master review-head -- src/bytes_mut.rs` — the changed hunk itself (also reproduced via the skill's own `review_context.py`, see below).
2. `git log --oneline -5 review-head` — confirms the pinned head and its four immediate ancestors, all within the pinned history (never beyond `7052d24`).
3. `git diff --stat master review-head` — confirms the manifest is exactly `src/bytes_mut.rs | 8 ++++++++`, one file.
4. `git status --porcelain=v1 -uall` (in the clone) — confirms the clone tree is clean (no mutation) both before and after my scratch-crate work, which lived entirely under `/tmp/effort124/work/g-high-seed2-att-10/`.
5. `git show master:src/bytes_mut.rs | sed -n '1066,1082p'` — base-branch version of the changed function, for the gate-2 (introduced-here) guarantee comparison.
6. `sed -n '1030,1110p' src/bytes_mut.rs` — the `impl Buf for BytesMut` block at head, enclosing function context for `advance`.
7. `grep -n "fn set_len\|fn advance_unchecked\|fn remaining\|fn len(\|fn split_to\|fn split_off\|fn split(" src/bytes_mut.rs` — batched search locating every related method's definition line, one call over the one file, not one grep per symbol.
8. `sed -n '505,535p' src/bytes_mut.rs` — `set_len`'s doc and body (its only safety contract: `debug_assert!(len <= self.cap)`).
9. `sed -n '855,900p' src/bytes_mut.rs` — `advance_unchecked`'s body, including the `KIND_VEC` position-shift and `promote_to_shared` branch that the new fast path deliberately bypasses.
10. `sed -n '180,195p' src/bytes_mut.rs` — `len()`.
11. `grep -n "fn get_vec_pos\|fn set_vec_pos\|MAX_VEC_POS\|KIND_VEC\b\|KIND_ARC\b\|fn kind(\|struct BytesMut\|ptr:\|len:\|cap:\|data:" src/bytes_mut.rs` — batched search establishing the struct's field layout and the vec-position bookkeeping's storage location (the bit-packed `data` word, not `len`).
12. `sed -n '210,225p' src/bytes_mut.rs` — `capacity()` (`self.cap`, unaffected by `len` writes).
13. `sed -n '395,500p' src/bytes_mut.rs` — `split_off`, `truncate`, `clear`, `resize`, the start of `set_len`'s doc — used for the `C3` `#[inline]`-boundary comparison and to confirm `truncate(0)`/`clear()` already perform the identical `set_len` operation with an equivalent safety framing.
14. `grep -n "fn advance" src/buf/buf_impl.rs` then `grep -n "fn advance(&mut self" -A 20 src/buf/buf_impl.rs` — located and read the `Buf::advance` trait's documented contract ("must behave as if `cnt == self.remaining()`" when not panicking) to confirm the new fast path cannot violate the trait's documented implementer notes.
15. `sed -n '190,224p' src/buf/buf_impl.rs` — the full trait doc block for `advance`.
16. `head -40 CHANGELOG.md` — confirms `CHANGELOG.md` entries are batched at release time (grouped under version headings, not one bullet per merged PR in the working tree), so there is no repository convention requiring this PR to touch `CHANGELOG.md` itself; not a repository-rule finding.
17. `cat Cargo.toml` — confirmed no required non-dev dependencies, enabling an offline scratch crate with a bare `path` dependency on the clone.
18. Skill tooling: `python3 scripts/review_context.py --merge-base ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401 --head 7052d2454a2370ab9583f63711df89f3bd7bec83 --store <mktemp -d>/review-context-7052d2454a2370ab9583f63711df89f3bd7bec83.json`, run exactly once — produced the manifest, complete diff (one chunk, `coverage: complete`), `ranges`, and `history` sections reproduced above; confirmed my manual diff read was complete and identical, and gave the file's per-path history (`9d3ec1c`, `4e2c9c0`, `e4af486`, all ancestors of the pinned head, not beyond it).
19. Skill tooling: `python3 scripts/context_fingerprint.py --packet <work-dir>/packet.json -` with empty stdin object (`{}`, i.e. no specs, no guidance) — see §6 for the exact packet contents and the resulting digest.
20. Skill tooling: `python3 scripts/validate_review.py <payload.json>` and `python3 scripts/validate_review.py --render < payload.json` and `python3 scripts/validate_review.py --emit-batch < payload.json` (rendering only — publication is disabled for this retrospective run, so `--emit-batch`'s output was inspected but never sent anywhere).

**Focused test execution (offline, permitted under packet §8 item 2):** No test function was added or changed by this diff (`tests/` has no `test_bytes_mut.rs`, and `grep -n "advance" tests/test_buf.rs tests/test_buf_mut.rs` shows only pre-existing, unrelated `advance`/`advance_mut` tests on `&[u8]`/`Vec<u8>`/`BytesMut` buffer-mut paths not touched by this diff), so the rubric's Changed-tests section does not mandate any run. As additional, self-initiated verification (permitted, not mandated, by the packet's execution allowance), I wrote one scratch crate:

- Command: `CARGO_HOME=/tmp/effort124/cargo-home CARGO_NET_OFFLINE=true CARGO_TARGET_DIR=/tmp/effort124/work/g-high-seed2-att-10/target cargo run --offline`, run from `/tmp/effort124/work/g-high-seed2-att-10/scratch` (a scratch crate with a single `path` dependency on the reviewed clone; the clone itself was never modified — confirmed by `git status --porcelain=v1 -uall` before and after).
- Exit status: `0`.
- Duration: ~0.07s wall (`time` output: `0.01s user 0.01s system 31% cpu 0.068 total`), well inside the 5-minute bound.
- Ran once (not a suite; a single scratch binary), consistent with "the suite at most once."
- Decisive output: all in-process `assert_eq!`/`assert!` checks passed, including (a) full-consume `advance(remaining())` on a filled 16-byte buffer preserves `capacity() == 16` and allows refilling to 16 bytes afterward without a capacity change; (b) a partial `advance(4)` still takes the old `advance_unchecked` path correctly; (c) `advance(0)` on an empty buffer is a no-op; (d) `advance()` past `remaining()` still panics (via `std::panic::catch_unwind`), confirming the new fast path does not bypass the existing bounds check; (e) after `split_to`, advancing the remainder's full length to reuse its capacity does not disturb the split-off front part's bytes. The program printed `all scratch checks passed` and exited 0; the single panic message visible in the raw log is the expected, caught panic from check (d), not an unhandled failure.
- This is not a substitute for CI (unavailable offline, no logs to reuse) and is not claimed as "the repository's documented focused command" — it is independent corroborating execution I chose to run given the packet's execution allowance, and it materially strengthens `C1`'s falsification in §3.

## 6. The `context` digest and its inputs

Digest: `ea94526181af0db99933265225e9cb726540a9c0b839990daee177aff1f81e5e`

Computed once via `python3 scripts/context_fingerprint.py --packet /tmp/effort124/work/g-high-seed2-att-10/packet.json -` with an empty JSON object (`{}`) on stdin (no `specs`, no `guidance` beyond the empty defaults).

Inputs:

- **`pr.title`:** `` Reuse capacity when possible in `<BytesMut as Buf>::advance` impl `` (verbatim from packet §1/§3).
- **`pr.body`:** the complete pull-request body reproduced verbatim in packet §3 (the pseudocode example, the `buf.clear()` rationale, and the closing paragraph about not putting the change in `advance_unchecked`).
- **`issue coordinates`:** none — `issues: []`. The packet states explicitly (`## 4. Originating issue` → "None. The pull-request body is the only statement of intent.") that there is no closing reference and no user-supplied spec.
- **`comments_available`:** not applicable — no issues, so no per-issue `comments_available`/`comments_complete` markers apply.
- **`guidance` list:** empty. Packet §7 verifies, by direct lookup in the mirror, that none of `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, `CONTRIBUTING.md`, `CODEOWNERS`, `.github/CODEOWNERS`, or either PR-template path exist at the merge-base, so the guidance membership rule (root/path-scoped `AGENTS.md`/`CLAUDE.md`, root `CONTEXT.md`) contributes zero entries.
- **Note on provenance:** I did not run `forge_packet.py normalize` on raw GraphQL pages, because this run is offline and phase 1 was already pinned by the dispatch packet (`packets/g/packet.md`), per the binding run condition "If your skill's phase 1 asks you to resolve the target from the forge, that phase is satisfied by this packet." I hand-built a minimal `forge-packet/1`-schema JSON file (`/tmp/effort124/work/g-high-seed2-att-10/packet.json`) whose `fingerprint.pr`/`fingerprint.issues` fields reproduce exactly the packet's pinned title, body, and "no issues" fact, in the shape `forge_packet.py`'s own `build()` method documents it would have produced from the real fetch. This is disclosed as a judgment call in §10.

## 7. Mechanism checklist

- **Question channel:** did not fire. No candidate reached the Issue-fit rubric's static-unresolvability bar: both PR-text promises (`C1`'s underlying behavior request, and the explicit non-goal of not touching `advance_unchecked`) are `met` by direct code inspection, and no material, outcome-changing fact was left unsettled by any candidate. See §3 (no row is `not-verifiable`) and the Issue-fit ledger in the payload's `Issue fit` line.
- **Clean-verdict / related-acquittal verification:** fired, **zero-survivor mode**. Zero candidates survived as findings, and the change is on a data-integrity surface (raw pointer / buffer length / capacity bookkeeping in `BytesMut`, i.e. `unsafe` memory manipulation), which is one of the rubric's named zero-survivor trigger surfaces (`SKILL.md` step 3). I dispatched exactly one clean-verdict batch, giving it the complete three-row disposition ledger from §3 (never filtered by risk surface, as required). Related-acquittal mode did not separately fire (there was no candidate *batch* to attach related rows to, since there were zero survivors — the zero-survivor batch already carries the complete ledger by definition).

  **Exact prompt given to the verifier** (verbatim, as dispatched via `Agent` with `subagent_type: "v5b-verifier-effort-high"`, `model: "sonnet"`, `run_in_background: false`):

  > You are a clean-verdict verifier batch for the `legacy reviewer` skill, target `tokio-rs/bytes#698`. This is a controlled, offline, retrospective research-evaluation cell (`g-high-seed2`/`att-10`); nothing you do is published anywhere, and you must not attempt any network access, `git fetch`, `git pull`, `gh`, or `curl`.
  >
  > **Your sandbox:** the git clone at `/tmp/effort124/runs/g-high-seed2-att-10` (read-only inspection only — do NOT run `git checkout`, `git switch`, `git reset`, `git stash`, or any command that mutates the tree; if you need to run code, do it in a scratch crate under `/tmp/effort124/work/g-high-seed2-att-10/verifier-scratch/` only, never inside the clone), and the skill snapshot at `/tmp/effort124/skill/snapshot-path-omitted/` (you may read `references/verifier.md` and `references/verifier-concurrency.md` there if you need to re-confirm your own task procedure, but none of the supplied candidates are `kind=concurrency` or `kind=invariant`, so the concurrency reference should not be needed). Do not read any other path, any other run's clone/report/payload, or any file outside these two locations plus your own scratch crate; report it if you do.
  >
  > **Pinned coordinates:** repository `tokio-rs/bytes`; base ref `master`; base SHA / merge-base `ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401` (identical); head SHA `7052d2454a2370ab9583f63711df89f3bd7bec83`. In the clone, local branch `master` is pinned to the merge-base and local branch `review-head` is checked out at the head; use `git show ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401:<path>` for merge-base content and read `review-head`'s working tree for head content. No originating issue exists (`issues=none`); the only stated intent is the pull-request title (`` Reuse capacity when possible in `<BytesMut as Buf>::advance` impl ``) and body (reproduced below verbatim). No repository guidance files (`AGENTS.md`/`CLAUDE.md`/`CONTEXT.md`) exist at the merge-base.
  >
  > **Pull-request body, verbatim:**
  > ```
  > While thinking about usage of `BytesMut` in my own code I've realized sometimes the following pattern (explained by the following pseudocode) is encountered:
  >
  > let mut buf = BytesMut::with_capacity(8196);
  >
  > loop {
  >     read_into_bufmut(&mut buf);
  >
  >     if some_condition {
  >         // consume the data and then discard it
  >         let consumed = process_data(&buf);
  >         buf.advance(consumed);
  >         // in most cases the above `advance` ends-up consuming the entire length of `buf`
  >     } else {
  >         // consume the data as `Bytes`
  >         ship_data(buf.split().freeze());
  >         // (this is just to explain that `VecDeque` wouldn't be efficient here)
  >     }
  > }
  >
  > In this particular example it would be more efficient to `buf.clear()` when `consumed == buf.len()`, instead of calling `advance` and eventually ending-up going through the allocation machinery.
  >
  > This PR makes `advance` do it automatically for cases in which it's safe to do (which is why I didn't put it inside `advance_unchecked`). I'm not sure the `Buf` API allows it, the only thing I've found is `#[must_use = "consider BytesMut::advance(len()) if you don't need the other half"]` on `BytesMut::split()`.
  > ```
  >
  > **The diff under review** (`src/bytes_mut.rs`, the only changed file, +8/-0):
  > ```diff
  > @@ -1066,6 +1066,14 @@ impl Buf for BytesMut {
  >
  >      #[inline]
  >      fn advance(&mut self, cnt: usize) {
  > +        // Advancing by the length is the same as resetting the length to 0,
  > +        // except this way we get to reuse the full capacity.
  > +        if cnt == self.remaining() {
  > +            // SAFETY: Zero is not greater than the capacity.
  > +            unsafe { self.set_len(0) };
  > +            return;
  > +        }
  > +
  >          assert!(
  >              cnt <= self.remaining(),
  >              "cannot advance past `remaining`: {:?} <= {:?}",
  >              cnt,
  >              self.remaining(),
  >          );
  >          unsafe {
  >              // SAFETY: We've checked that `cnt` <= `self.remaining()` and we know that
  >              // `self.remaining()` <= `self.cap`.
  >              self.advance_unchecked(cnt);
  >          }
  >      }
  > ```
  >
  > **Your task:** This is a zero-survivor clean-verdict batch under `references/verifier.md`'s "Clean-verdict task." I am supplying you the **complete candidate disposition ledger** (all 3 rows I raised and dropped/routed — never filtered by risk surface). For each row, follow the clean-verdict procedure: (1) restate the row's decisive premise in one sentence; (2) state the concrete condition under which that premise would be false; (3) trace the *opposite* branch of every conditional the premise depends on, citing `path:line` for each step; (4) either construct the complete failing state transition from trigger to observable consequence, or cite the specific step that is impossible; (5) a `holds` ruling on a fully attacked row must cite at least one line the ledger row did not cite. Rows of `kind=bug` get the full five-step attack; rows of `kind=maintainability` get the one-citation check only (confirm or contradict the stated fact from its evidence pointer) unless the row asserts safety, in which case give it the full five steps too.
  >
  > **Ledger row 1 — `C1` (`bytes_mut/advance-set-len-safety`, kind=bug):**
  > - claim: The `unsafe { self.set_len(0) }` shortcut in `<BytesMut as Buf>::advance` can violate `set_len`'s safety contract (`len <= capacity`) or otherwise corrupt buffer state (vec-position bookkeeping, shared/ref-count state) when `cnt == self.remaining()`.
  > - disposition: dropped (safe)
  > - decisive evidence: `src/bytes_mut.rs:519-521` (`set_len`'s contract: `debug_assert!(len <= self.cap)`); `src/bytes_mut.rs:217-218` (`capacity()` returns `self.cap` directly); `src/bytes_mut.rs:985-994` (`get_vec_pos`/`set_vec_pos` operate on the `data` field, not `len`)
  > - falsification reason: `0 <= self.cap` holds unconditionally (`cap: usize`); `ptr`/`cap`/vec-position/shared state are untouched by a `len`-only write.
  >
  > **Ledger row 2 — `C2` (`bytes_mut/advance-stale-review-requests`, kind=maintainability):**
  > - claim: The three review-thread requests recorded against this pull request (move the conditional before the `assert!`; use `self.remaining()` consistently rather than mixing it with `self.len`; correct the `SAFETY` comment wording to state the `set_len` invariant; put the semicolon after `unsafe { self.set_len(0) }` outside the block) are still unaddressed at the reviewed head.
  > - disposition: dropped (already satisfied at head)
  > - decisive evidence: `src/bytes_mut.rs:1069-1078`
  > - falsification reason: direct comparison shows every one of the four requests is already applied verbatim at the reviewed head.
  >
  > **Ledger row 3 — `C3` (`bytes_mut/advance-duplicates-clear`, kind=maintainability):**
  > - claim: The 4-line `if cnt == self.remaining() { unsafe { self.set_len(0) }; return; }` block duplicates the effect of the existing safe `self.clear()`/`self.truncate(0)` method and should call it instead of introducing a second raw-unsafe call site.
  > - disposition: routed to Observations (fails gate 4 "proven consequence", not gate-1 accuracy)
  > - decisive evidence: `src/bytes_mut.rs:1069-1073` vs. `src/bytes_mut.rs:424-431` (`truncate`) and `:443-445` (`clear`); `#[inline]` present on `advance` (`:1067`) and `set_len` (`:518`) but absent on `truncate`/`clear`
  > - falsification reason: routing through `clear()`/`truncate(0)` would add a non-inlined call boundary plus a redundant `len < self.len()` re-check inside the exact fast path this PR exists to make cheap, so the suggested "improvement" is not clearly a net win; the underlying duplication-of-effect fact itself is accurate and is published as an Observation, not a finding.
  >
  > Return, for each of the 3 rows: `holds` or `re-open`, with your five-step (or one-citation) trace and the `path:line` citations you used. Then return exactly one batch conclusion: `clean verdict stands`, or `disposition <id> does not hold; re-open it` for each row whose acquittal is contradicted or unsupported. You may also return at most one non-actionable `observation` aside if an accurate, sub-threshold fact surfaces incidentally — do not search for new findings beyond what these three rows raise. Do not render any publication-ready prose; return only your verdicts, citations, and the batch conclusion.

  **Verbatim report returned by the verifier** (`agentId: a9df430c26b2c7d15`; `subagent_tokens: 31886`; `tool_uses: 9`; `duration_ms: 108398`), reproduced exactly as returned, unedited:

  > ## Verification Results
  >
  > ### Row 1 — C1 (`bytes_mut/advance-set-len-safety`, kind=bug) — full five-step attack
  >
  > **1. Decisive premise:** The `unsafe { self.set_len(0) }` shortcut cannot violate `set_len`'s contract (`len <= cap`) or corrupt vec-position/shared-refcount state, because it only ever writes `self.len` and `0 <= self.cap` holds unconditionally for a `usize`.
  >
  > **2. Falsifying condition:** The premise would be false if either (a) `debug_assert!(len <= self.cap)` at `src/bytes_mut.rs:520` could fail for `len=0`, or (b) skipping the pointer/capacity/vec-position bookkeeping that the normal path (`advance_unchecked`) performs left the struct in an inconsistent state that a later operation could read as corrupted.
  >
  > **3. Trace of the opposite branch:** The normal path this shortcut bypasses is `advance_unchecked` at `src/bytes_mut.rs:872-907`. When taken instead of the shortcut, it: updates vec-position bookkeeping for `KIND_VEC` at `src/bytes_mut.rs:883-899` (including a `promote_to_shared` escape at `:897` if `pos > MAX_VEC_POS`), then unconditionally moves the pointer and shrinks capacity at `src/bytes_mut.rs:904-906` (`self.ptr = vptr(...add(count))`, `self.cap -= count`). The struct's fields are `ptr`, `len`, `cap`, `data` (`src/bytes_mut.rs:61-65`). The shortcut at `src/bytes_mut.rs:1071-1075` returns before reaching any of `883-906`, leaving `ptr`, `cap`, and `data` (hence `get_vec_pos`/`set_vec_pos`, `src/bytes_mut.rs:985-997`) completely untouched.
  >
  > **4. Attempted failing state transition:** For corruption, either `ptr`/`cap` would need to go stale relative to each other, or `len` would need to violate `len <= cap`. Since the shortcut moves neither `ptr` nor `cap`, they remain mutually consistent (the window `[ptr, ptr+cap)` is exactly what it was before `advance` was called); `vec_pos`, which is only ever mutated in step with a `ptr` move (`:888-897`), is never touched here so it cannot desync. And `0 <= self.cap` is a tautology over `usize` — no witness value of `cap` can violate it. No trigger produces an observable inconsistency; this step is impossible to complete.
  >
  > **5. Citation not in the original ledger:** `src/bytes_mut.rs:904-906` (`advance_unchecked`'s pointer/capacity mutation) and `src/bytes_mut.rs:61-65` (struct field layout) were used above and were not cited by the ledger row.
  >
  > **Verdict: holds.**
  >
  > ### Row 2 — C2 (`bytes_mut/advance-stale-review-requests`, kind=maintainability) — one-citation check
  >
  > Checked `src/bytes_mut.rs:1069-1082` against the four stated properties:
  > - Conditional before `assert!`: conditional at `1069-1075` precedes `assert!` at `1077-1082` — confirmed.
  > - Consistent use of `self.remaining()` (no mixing with `self.len`): body uses `self.remaining()` at `1071`, `1078`, `1081`; no direct `self.len` reference in the function — confirmed.
  > - `SAFETY` comment states the `set_len` invariant: `1072` reads "Zero is not greater than the capacity", matching `set_len`'s contract `len <= self.cap` (`:520`) — confirmed.
  > - Semicolon after `unsafe { self.set_len(0) }` outside the block: `1073` has `unsafe { self.set_len(0) };` with the semicolon outside the braces — confirmed.
  >
  > All four sub-claims are accurate as stated against the cited evidence. (Note: the row also implies these were live review-thread requests; that external fact is not independently checkable offline — this is a non-actionable observation, not a defect in the row, since the row's checkable claim is about the code state, which matches.)
  >
  > **Verdict: holds.**
  >
  > ### Row 3 — C3 (`bytes_mut/advance-duplicates-clear`, kind=maintainability, no safety assertion) — one-citation check
  >
  > Checked citations:
  > - `src/bytes_mut.rs:1069-1073` (the shortcut) vs. `truncate` at `424-431` and `clear` at `444-446`: `clear()` calls `truncate(0)` (`445`), and `truncate` performs `if len < self.len() { unsafe { self.set_len(len) } }` (`425-429`) — functionally equivalent to the shortcut's unconditional `set_len(0)` when triggered (guarded upstream by `cnt == self.remaining()`) — confirmed duplication-of-effect claim.
  > - `#[inline]` present on `advance` (`1067`) and `set_len` (`518`), absent immediately above `pub fn truncate` (`424`) and `pub fn clear` (`444`) — confirmed by direct inspection; no `#[inline]` attribute precedes either function.
  >
  > The stated fact is accurate against its evidence pointer, and the accompanying rationale for routing to Observations (an un-inlined call boundary plus a redundant re-check) is consistent with the confirmed `#[inline]` asymmetry.
  >
  > **Verdict: holds.**
  >
  > ## Batch conclusion
  >
  > **clean verdict stands**
  >
  > **Observation (non-actionable, incidental):** C2's premise that four specific requests were raised in PR review threads cannot itself be verified offline (no network/`gh` access to the actual review-comment history in this sandbox); only the resulting code state was checked and it matches what C2 describes. This does not change the disposition since the row's checkable claim (code state at head) is what was cited as evidence.

  **What I (the primary) did with this return:** All three rows `holds`; the batch conclusion is `clean verdict stands`; zero rows re-opened. The verifier's own incidental observation aside (about `C2`'s PR-provenance claim being unverifiable offline) does not affect any disposition, matches my own framing in §3 (the packet — not a live forge fetch — is the authoritative source for the review-thread history in this offline cell), and does not itself qualify as a new candidate or a third publishable Observation (it is about the *ledger row's framing*, not a fact about the reviewed artifact, and the rubric's Observations channel is for facts about the change, not about the reviewer's own evidentiary limits). No follow-up batch was required or run (§7 "Follow-up verifier round").

- **Observations:** fired. One published (`C3`), 0 unpublished (well under the cap of 3). See §2.
- **Fix-sufficiency check on any concurrency/invariant candidate:** did not fire — no candidate is `kind=concurrency` or `kind=invariant`. `C1` is `kind=bug` (a memory-safety/invariant-adjacent claim about a single-threaded, `&mut self` state mutation, not a cross-path/cross-thread state rule), so `verifier-concurrency.md`'s bug-class check does not apply; the verifier was still instructed to give `C1` the full five-step attack as an ordinary `bug`-kind row.
- **Follow-up verifier round:** not used. The rubric caps verification at one initial-or-clean-verdict batch plus one optional follow-up, spent only if a row is re-opened or a candidate first becomes render-eligible after the initial batch. The clean-verdict batch returned `clean verdict stands` with zero re-opened rows, so no follow-up was needed or run.
- **Deferral handling:** The packet's prior-review record (§6) contains no explicit deferral language ("we can fix this during the API review," "let's revisit later," etc.) — all three review threads and both non-review comments are ordinary review-and-fix exchanges that were fully resolved and incorporated before merge (confirmed against the head, see `C2`). There is nothing to treat as an open deferred question.
- **Retrospective mode:** fired, as instructed by the packet and confirmed by `merged: true` and `state: MERGED`. The summary's `Mode` line reads `**Mode:** Retrospective review of merged pull request; publication disabled.` Step 6 ("Publish one review") was followed through to the point of producing `batch.json` via `--emit-batch` for inspection, then stopped — no write of any kind was attempted against any forge, per the packet's binding run condition 4 and the skill's own retrospective-mode rule.

## 8. History discipline

I did not read any history beyond the pinned head. The exact history-touching commands run, all confined to ancestors of (or the pinned head/merge-base itself):

- `git log --oneline -5 review-head` → showed `7052d24` (the pinned head) and its four immediate ancestors (`ce09d7d`, `9d3ec1c`, `4e2c9c0`, `327615e`), all pre-existing ancestors.
- `git show master:src/bytes_mut.rs` (piped to `sed`) → the merge-base's version of the changed file, for the base-vs-head guarantee comparison gate 2 requires.
- `review_context.py`'s own `history` section (run as part of the single mandated context-build call) → reported three prior commits touching `src/bytes_mut.rs` (`9d3ec1c`, `4e2c9c0`, `e4af486`), all ancestors of the pinned head.
- `git diff --stat master review-head` and `git diff master review-head -- src/bytes_mut.rs` → the merge-base-to-head diff itself, not history beyond it.
- `git status --porcelain=v1 -uall` (twice, before and after the scratch-crate run) → working-tree status only, no history traversal.

The clone's history is truncated at `7052d24` by design (per packet condition 3); I made no attempt to fetch, pull, or otherwise access anything past it, and none of the above commands could have done so (all are local, offline, read-only history/diff queries against already-present objects).

## 9. Sandbox disclosure

No path outside the sandbox was read. Everything I read came from exactly one of: the clone (`/tmp/effort124/runs/g-high-seed2-att-10`), the skill snapshot (`/tmp/effort124/skill/snapshot-path-omitted/`), the packet directory (`/tmp/effort124/packets/g/`), and my own work/report/payload/timing paths under `/tmp/effort124/work/g-high-seed2-att-10/` and `/tmp/effort124/reports/g/`. The one scratch crate I built and ran lives entirely under `/tmp/effort124/work/g-high-seed2-att-10/scratch/`, with `CARGO_TARGET_DIR` also redirected under my work directory; it depends on the clone only via a `path` Cargo dependency (read-only) and never wrote into the clone.

## 10. Notes — judgment calls on rubric/contract ambiguities

1. **Constructing `packet.json` by hand instead of running `forge_packet.py normalize`.** The skill's step 1 normally requires running `forge_packet.py normalize` over saved GraphQL page dumps to produce the `forge-packet/1`-schema file that `context_fingerprint.py --packet` consumes. This run is offline with phase 1 already pinned by the dispatch packet, and the binding run conditions state that "If your skill's phase 1 asks you to resolve the target from the forge, that phase is satisfied by this packet." I treated this as also covering the mechanical `packet.json` artifact `context_fingerprint.py` expects: I hand-built a minimal, schema-conformant JSON file whose `fingerprint.pr.title`/`fingerprint.pr.body`/`fingerprint.issues` fields are the packet's own pinned values, in exactly the shape `forge_packet.py`'s `build()` method documents it would emit from a real fetch (verified by reading that method's source, §5 item — not listed separately above but part of reading `forge_packet.py` lines 560-635 to confirm the schema). I did not run the script itself since there is no raw page data to feed it. I record this as a deliberate substitution, not a silent one.
2. **`C3` routing (Observations vs. drop vs. `consider` finding).** The rubric is explicit that a fact failing specifically on gates 1/4 goes to Observations rather than being silently dropped, and that a fact passing gates 1 and 4 "at any priority" must be a finding rather than routed away to avoid publishing a low-priority `consider`. I judged that `C3` does *not* clearly pass gate 4 (I could not establish net benefit, only equivalence-of-effect, and identified a plausible, uncontradicted cost), so it is correctly an Observation and not a `P3 consider` finding. I flag this as the single genuine judgment call in this run: a differently-calibrated reviewer might instead have treated the missing `#[inline]` counter-argument as insufficient to defeat gate 4 and admitted `C3` as a low-priority `consider` finding recommending the `self.clear()` simplification with a caveat about inlining. I did not do this because the rubric requires a *proven* consequence, not a plausible one in either direction, and here the direction of net benefit is genuinely unsettled by static evidence.
3. **Scratch-crate execution was not rubric-mandated but was permitted and useful.** The rubric's Changed-tests section applies only to test functions the diff adds or changes; this diff adds none. I nonetheless used the packet's explicit execution allowance to run one independent scratch program, treating it as risk-led-discovery-style corroborating evidence for `C1` (a data-integrity/memory-safety candidate) rather than as a formally mandated check. I judged this consistent with, not a departure from, "Run a suite at most once per run" (this was a single scratch binary, not the crate's own test suite, and it was run exactly once).
4. **No `Ambiguities` section in the payload.** None of the three candidates turned on a rubric or contract *term* with two genuinely supportable readings (as opposed to a code-quality judgment call, which `C3` is). I therefore judged that no `Ambiguities` entry was required, distinguishing this from the `C3` routing note above, which is a private-record judgment call rather than a contestable-term dispute the summary must surface.
5. **Payload rendering order:** I validated the assembled payload with `scripts/validate_review.py` before dispatching the verifier and it already passed with zero violations (since it currently has zero findings/questions and one well-formed observation, the mechanical checks that matter are the observation's one-sentence-plus-evidence shape and the run trailer's grammar, both satisfied independent of the verifier's answer). The verifier's actual outcome (`clean verdict stands`, all rows `holds`) matched what the payload's `Coverage` line already asserted, so no payload edit was needed after the batch returned; I re-ran `--render` and `--emit-batch` anyway (§11) to confirm the final artifact is still mechanically valid.

## 11. Step 5–6 execution record (validation and stopped publication)

- `python3 scripts/validate_review.py /tmp/effort124/work/g-high-seed2-att-10/payload.json` → exit `0`, zero violations.
- `python3 scripts/validate_review.py --render < payload.json` → exit `0`; printed zero fragment lines (correct: there are no finding or question items to generate `anchor …`/`; fix …` fragments for — only an observation, which carries no summary-reference fragment).
- `python3 scripts/validate_review.py --emit-batch < payload.json > batch.json` → exit `0`; emitted `{"commit_id": "7052d2454a2370ab9583f63711df89f3bd7bec83", "event": "COMMENT", "body": "<the summary body>", "comments": []}` — an empty `comments` array is correct given zero line-anchored findings/questions.
- Immediately after the final successful validation, ran `python3 /tmp/effort124/mark_event.py /tmp/effort124/reports/g/g-high-seed2-att-10-timing.json payload_validated_at` as instructed; the sidecar now records `payload_validated_at`.
- **Step 6 ("Publish one review") was deliberately not executed.** Per the packet's binding condition 4 and the skill's own retrospective-review rule (`SKILL.md` §"Boundaries": "retrospective review of a merged pull request is non-publishing by default"; the packet confirms no separate publication authorization was given), I stopped before any write: no re-fetch of the live PR head was attempted (no network access exists in this cell regardless), no `gh api --method POST .../reviews` call was made, and `batch.json` was produced only for local inspection of the would-be payload shape, never submitted anywhere.
- **Reporting the would-be review in place of a publication result**, as step 6 requires for a non-publishing retrospective run: status `Approved (advisory)`; reviewed head `7052d2454a2370ab9583f63711df89f3bd7bec83` against merge-base `ce09d7d358ab1d1d31ed9d0b52a747c0a21ea401`; coverage `complete`; no review URL (nothing was posted); no finding URLs (zero findings); no open questions; no disputed findings (first review, no prior state); nothing failed to publish because nothing was attempted. The complete would-be review is at [`/tmp/effort124/reports/g/g-high-seed2-att-10-payload.md`](/tmp/effort124/reports/g/g-high-seed2-att-10-payload.md).
