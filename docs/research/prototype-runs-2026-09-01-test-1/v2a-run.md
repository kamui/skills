# v2a run — `code-review-deep-publish` against `kamui/shortlist#66` (post-C9, Sonnet 5)

**2026-09-03.** Data only. Not published to the PR. This is the model-matched post-C9 run: it
replaces the 2026-09-02 Fable 5.1 run held in
[`../prototype-runs-2026-09-01-test-1-fable/`](../prototype-runs-2026-09-01-test-1-fable/), and it
pairs with the pre-C9 run [`v2a-run-pre-c9.md`](v2a-run-pre-c9.md) on the same model. See
[`addendum-2026-09-03.md`](addendum-2026-09-03.md).

## Metadata

| | |
| --- | --- |
| Skill | `code-review-deep-publish` (**v2a**, "Panel line"), pinned `87c68a9` — includes `326ef6f` and `940aa2c` (DESIGN.md §C9) |
| Model | `claude-sonnet-5` on the orchestrator and all three sub-agents, passed explicitly on every Agent call and verified from the harness transcripts |
| Architecture | 2 axis finders in parallel → 1 mandatory fresh-context verifier |
| Agents spawned | 4 (orchestrator, Code finder, Requirements finder, verifier) |
| Sub-agent tokens | orchestrator 218,249; Code finder 112,792 (44 tool uses); Requirements finder 103,578 (42 tool uses); verifier 56,287 (21 tool uses) |
| Wall clock | ~20 min measured from finder dispatch to verifier completion; ~25–30 min including setup |
| Candidates raised | 5 — Code 3, Requirements 2 |
| Verdicts | **5 confirmed · 0 plausible · 0 refuted**; 2 cross-axis merges |
| Findings for publication | **3** — P1 `must-fix`, P1 `consider`, P3 `consider` |
| Questions | 0 (the "cannot tell from the code" bucket returned 0 items) |
| Coverage | complete (9/9 files, both finders); suites re-run read-only, 290 Python + 60 Node pass |
| Requirements counts | met 9 · not met (partial) 2 · cannot tell 0 |
| Derived status | **Changes Requested (advisory)** — one confirmed `must-fix`; the ladder keys on action alone |

## The headline: the C9 confound is closed

This run exists to answer one question the 2026-09-02 round could not: **did commit `940aa2c` fix
the recall gap, or did the model change do it?** That round compared a pre-C9 run on
`claude-sonnet-5` against a post-C9 run on `claude-fable-5-1`, moving two variables at once.

This run holds the model fixed and moves only the skill commit:

| | pre-C9 (`5db5903`), Sonnet 5 | **post-C9 (`87c68a9`), Sonnet 5** |
| --- | --- | --- |
| `search-bundle-format.md:208` | found (1 axis) | **found, both axes independently** |
| `shortlist-narrow/SKILL.md:46` | **missed entirely** — absent from both ledgers, not even acquitted | **found, both axes independently**, verifier-confirmed |
| Candidates | 1 | 5 |
| Findings | 1 (P3 consider) | 3 (P1 must-fix, P1 consider, P3 consider) |
| Status | Approved (advisory) | Changes Requested (advisory) |

Same model, same target, same packet, same clone — only the skill commit differs. **The recovered
recall is attributable to `940aa2c`.** That is what the earlier round could not say, and it now
matches the skill author's own replication (3/3 on the restructured rubric versus 1/5 unchanged).

The mechanism is visible in the output: both finders wrote down the changed-contract list first, and
Contract B's old-fragment sweep (`"price, stock, delivery, and restock"`) is what surfaced the item
the pre-C9 run never examined.

## The third drift was missed, and the report says so plainly

The Fable post-C9 run found a third drift no prototype had previously reported: the retired
Volatile-term regex at `skills/shortlist/scripts/validate-completion.py:2949`, which still hardcodes
`price|stock|delivery|restock|availability|available|unavailable` to decide whether evidence needs
an offset-bearing timestamp.

**This run missed it on both axes** — not as a candidate, not as an acquittal, not as an
observation. The orchestrator states this without softening, and goes further: the Requirements
finder's own reported old-fragment search string should in principle have matched that line, and its
reported hit list does not include it. Whether that is a genuine miss of a live hit or a
tooling/fragment-variant artifact could not be determined from the output alone.

So on this target the two models split: Fable found three drifts and raised an AC4 question; Sonnet
found two drifts, missed the third, and raised no question. Neither is a superset of the other.

## Calibration moved, and the run defends the move

The pre-C9 and Fable post-C9 runs both landed non-blocking. This run derives **Changes Requested**,
because the verifier independently confirmed `must-fix` on `shortlist-narrow/SKILL.md:46` — reasoning
that the file is cited elsewhere as "the implemented contract" for the Narrow stage and followed as
an executed numbered step, not read as background documentation, and that this PR's own new fixture
supplies a concrete instance the fixed list cannot cover.

The orchestrator reports this as measured rather than reshaping it toward the `Approved (advisory)`
outcome the C1 checklist item anticipated, and argues the ladder behaved correctly: it keys on action
alone, and one confirmed `must-fix` is unconditionally blocking. Worth noting for the program that
the same underlying item was rated `P2 consider` by the Fable run's verifier and `P1 must-fix` here —
the finding is stable across models, its merge consequence is not.

## An honest self-report on C3

The Code finder returned a complete 20-row ledger with 15 explicit acquittals. **The Requirements
finder did not return a ledger in the brief's required shape** — its acquittal reasoning exists, but
inline in the changed-contract prose rather than as one row per weighed hypothesis. The orchestrator
flags this as a partial miss for that axis specifically and declines to fabricate rows to fill the
gap. That matters for auditability: the Requirements axis's search process is less independently
checkable than the Code axis's from this output.

## Mechanism checklist

- **C1 (Calibration)** — recall 2/2 on the known drifts, up from 1/2 pre-C9; calibration split
  (one advisory, one blocking) with the blocking call defended from `finding-format.md`'s own
  calibration text.
- **C3 (Disposition ledger)** — **partial**: Code axis full, Requirements axis not in the required
  shape.
- **C5 (Observations)** — confirmed, 10 observation-shaped items across both finders and the
  verifier; 3 would publish under the cap.
- **C9 (Changed-contract sweep)** — demonstrated, and it is the proximate cause of the recovered
  recall.
- **Pole intact** — both finders ran, all 5 candidates got verdicts, `support` withheld by
  construction (the orchestrator built the verifier prompt from the finders' returned fields,
  deliberately omitting `support`).
- **C2 / C4** — not applicable; this target has an originating issue, and the "cannot tell" bucket
  returned 0 items.

## Full run report

The orchestrator's complete report, verbatim, including both finders' ledgers and the verifier's
verdicts:

### 1. Metadata

| Field | Value |
| --- | --- |
| Skill under test | `code-review-deep-publish` (research nickname **v2a**, "Panel line") |
| Pinned commit | `87c68a9` (branch `t3code/prototype-code-review-publish-2a`, PR #18, `kamui/skills`) — includes `326ef6f` "Require paired peer-contract sweeps" and `940aa2c` "Sweep every changed contract, on both axes" |
| Target | `kamui/shortlist#66` — "Seed category profiles into the ledger and generalize Volatile-claim freshness" |
| base / head / merge-base | base `main`@`ccd1842d742fd940b2afde4f903c7bdcb3a707eb`; head `4349ff41ff4d134e09017662dd30420b80e8eb30`; merge-base = base SHA |
| Architecture | Two parallel finder sub-agents (Code axis, Requirements axis) fanned out from the orchestrator, then one fresh-context verifier sub-agent (all `support` fields withheld) |
| Agents spawned | 3 — Code finder, Requirements finder (parallel), Verifier (sequential, after both finders returned) |
| Model | All three sub-agents run with `model: "sonnet"` passed explicitly on every `Agent` call (Sonnet 5); orchestrator also running as Sonnet 5 |
| Per-sub-agent tokens / tool uses / wall clock | **Not available.** This harness does not surface sub-agent token counts, tool-call counts, or per-agent wall-clock timing to the orchestrator — I receive only each sub-agent's final text report via the coordinator relay. Stated explicitly per the run's own reporting requirement rather than estimated. |
| Total tool uses (orchestrator) | Approximately 45–50 tool calls (Read/Bash/Write/Edit/Agent combined) across the run. This is an approximate count from reviewing my own transcript, not an exact harness-reported figure (which is also not exposed to me). |
| Wall clock | Finder dispatch → verifier completion measured directly: **~20 minutes** (finders launched at run-relative epoch 1788425114; verifier report received by epoch 1788426336). Preceding setup (reading SKILL.md/references, the phase-1 packet, building the shared block and both axis prompts) added an estimated further 5–10 minutes, for a **total estimated wall clock of ~25–30 minutes** for the full run. The lower bound (~20 min) is a precise measurement; the total is an estimate because I did not capture a timestamp before the very first setup action. |
| Candidates raised | 5 total — 3 from the Code finder, 2 from the Requirements finder |
| Verifier verdicts | **confirmed: 5, plausible: 0, refuted: 0** |
| Merges | 2 cross-axis merges (each Code candidate matching a Requirements candidate merged into the Requirements id, per verify.md's tie-break); 1 Code candidate stood alone |
| Findings for publication | **3** — 1 × P1 `consider`, 1 × P1 **`must-fix`**, 1 × P3 `consider` |
| Questions | **0** — no Requirements "cannot tell from the code" bucket items (count: 0), and 0 verifier `plausible` verdicts, so nothing routed to a question |
| Observations | 3 (Code finder) + 5 (Requirements finder) + 2 (Verifier) = 10 total accurate asides outside the verdict list. Per `publishing.md`'s cap, only the 3 most decisive would actually appear in a real summary's `## Observations` section — see §2 below for the full set and the selected three. |
| Coverage | **9/9 files**, both finders independently reviewed all 9 changed-file-manifest entries (`reviewed`, none `ignored`); coverage is **complete** |
| Derived status | **`Changes Requested (advisory)`** — see the C1 discussion in §7. This is **not** `Approved (advisory)`; one of the two known doc-sync drifts survived independent fresh-context verification as a `must-fix` with a demonstrated merge consequence, which the status ladder in `publishing.md` derives on action alone, unconditionally forcing `Changes Requested` regardless of priority or of how many other findings are merely advisory. |

---

### 2. The complete would-be review

This PR is merged; the posting identity (`kamui`) equals the PR author, so this would be a
self-review restricted to `COMMENT`, and publication is unconditionally disabled for this run
regardless. The text below is the complete review this run would have posted had publication been
enabled — summary, every finding, and observations — reconstructed exactly per `references/publishing.md`.

> **This is a retrospective review of an already-merged pull request.**
>
> **Changes Requested (advisory)** — 1 blocking finding, 2 optional findings, 0 open questions.
>
> Code: Findings — contributed to 2 of the 3 published findings (both merged into the Requirements
> axis's framing per the verifier's tie-break) plus 1 standalone `consider` finding.
> Requirements: Findings — 9/11 requirements met, 2 partially met (both are the same shape: a
> primary reference document generalized correctly, one live sibling document left carrying the
> retired closed-list wording).
> Reviewed `4349ff4` against `main` (merge-base `ccd1842`). Coverage: complete (9/9 files).
>
> The change correctly generalizes category-profile seeding and Volatile-claim freshness in its
> primary reference docs (`research-protocol.md`, `record-schemas.md`, `narrowing-protocol.md`,
> `CONTEXT.md`) and ships fixtures/tests that exercise the new mechanism end to end (290/290 and
> 60/60 tests pass, read-only, reproduced independently by this review). The one thing to fix before
> calling this done: `skills/shortlist-narrow/SKILL.md:46` — the Narrow stage's own executed
> instruction, not just background documentation — still hardcodes the retired six-item, per-bundle-type
> Volatile-claim list with no escape hatch, so an agent following it literally has no textual basis to
> refresh a Volatile-claim class outside that list (this PR's own new fixture ships exactly such a
> class). The `search-bundle-format.md:208` gap is the same shape but advisory, because that file is a
> descriptive contract summary rather than an executed step, and record-schemas.md/the validator are
> both already correct and enforced.

#### Findings

---

**[Requirements] [must-fix] [P1] Narrow skill's own refresh instruction still hardcodes the pre-diff Volatile-claim lists**

`skills/shortlist/references/narrowing-protocol.md:68` (this diff) generalizes the pre-handoff
refresh rule: "refresh every applicable Volatile claim whose evidence has grown materially stale …
not only a fixed commerce list … A claim class a category profile did not anticipate is refreshed on
the same terms as one it seeded." `skills/shortlist-narrow/SKILL.md:46` — cited by
`docs/design/intake-criteria-and-ranked-narrowing.md:14` and `README.md:103` as one of "the
implemented contracts" for the Narrow stage, and followed as its own literal numbered step 6 — still
reads: "Refresh volatile evidence before the final handoff when it may have changed since research:
price, stock, delivery, and restock facts in a commerce bundle; access, cost, catalog, licensing,
compatibility, and support claims in a generalized bundle." This closed, per-bundle-type pair of
lists was not touched by the diff and carries no "another decision-relevant class" escape hatch.

**Triggers when**: an agent executes the Narrow stage per SKILL.md's own numbered steps against a
generalized bundle whose ledger has identified a Volatile-claim class outside both fixed lists — for
example "policy terms" (present in `record-schemas.md:392`'s own open example list, absent from
SKILL.md:46's fixed generalized-bundle list), or the ad-tier feature/price-lock class this PR's own
new fixture (`tests/fixtures/generalized-bundle-streaming/ledger.md`, Record 7, `Origin: Research`)
ships as a worked example of "a claim class the category profile did not anticipate." The agent has
no textual basis in SKILL.md to refresh it before handoff.

**Change**: Replace `skills/shortlist-narrow/SKILL.md:46`'s two fixed lists with a pointer to the
ledger-driven rule, e.g. "Refresh every applicable Volatile claim the category and ledger identify as
materially stale before the final handoff — not only a fixed commerce or generalized-bundle list; see
[Volatile evidence](../shortlist/references/narrowing-protocol.md#volatile-evidence)."

<!-- finding id=requirements/shortlist-narrow-skill-stale-freshness-list axis=requirements action=must-fix priority=P1 fix=skills/shortlist-narrow/SKILL.md:46 head=4349ff41ff4d134e09017662dd30420b80e8eb30 -->

---

**[Requirements] [consider] [P1] Bundle contract still lists the pre-diff closed obligation-`Kind` set**

Issue #45 requires `Volatile-claim class` to become a formal obligation `Kind` — met in
`record-schemas.md:392`, `CONTEXT.md:327`, `research-protocol.md:295`, and `record_schemas.py:397`,
all four updated by this diff. `skills/shortlist/references/search-bundle-format.md:208` — the bundle
contract doc, cited elsewhere ("Read the bundle contract before editing the bundle") as authoritative
before touching a bundle — still reads: "one Research obligation record per applicable source family,
audit, Candidate relationship, discovery branch, safeguard, or other category-relevant work," omitting
`Volatile-claim class` entirely, and was not part of this diff. `git show 55e1f25 --stat` shows this
same four-file set (`CONTEXT.md`, `record-schemas.md`, `research-protocol.md`,
`search-bundle-format.md`) was edited together the last time this enum grew, establishing the sync
relationship this diff broke.

**Triggers when**: an agent consults `search-bundle-format.md` (rather than `record-schemas.md`) to
learn the ledger's obligation vocabulary while seeding or auditing the applicability ledger, and
concludes `Volatile-claim class` is not a valid `Kind` — mislabeling a Volatile-claim obligation as
`Other` or omitting it, even though `record-schemas.md` and the validator both accept and expect it.
The line does also hyperlink to `record-schemas.md#research-obligation` in the same sentence, which
mitigates the risk for an agent that follows the link.

**Change**: Add `Volatile-claim class` to the Kind list at `search-bundle-format.md:208`, matching
`record-schemas.md:392`'s ordering.

Closing this without action is a correct response.

<!-- finding id=requirements/search-bundle-format-stale-obligation-kind axis=requirements action=consider priority=P1 fix=skills/shortlist/references/search-bundle-format.md:208 head=4349ff41ff4d134e09017662dd30420b80e8eb30 -->

---

**[Code] [consider] [P3] Research skill still describes obligations as add-only**

`skills/shortlist/references/research-protocol.md:295` (this diff) now reads "Field evidence may add,
refine, or mark inapplicable a seeded obligation at any time, always with a recorded reason," and
`record-schemas.md:394-396` adds "Research may refine a seeded obligation instead of only adding or
closing one … Marking a seeded obligation `Not applicable` follows the same rule as any other
obligation." `skills/shortlist-research/SKILL.md:39` still reads: "…seed it from the category profile
during reconnaissance, add obligations the field evidence reveals, and record a terminal disposition
for every applicable obligation" — naming only the add capability, not refine-in-place.

**Triggers when** *(corrected by the verifier — the finder's original trigger overstated the defect;
marking an obligation `Not applicable` is already covered by SKILL.md's existing "record a terminal
disposition for every applicable obligation" clause, so an agent would not leave an inapplicable
obligation open on this text alone)*: an agent following SKILL.md's condensed step 5, on finding field
evidence that narrows or reshapes what a seeded obligation covers, adds a new, partially-redundant
obligation rather than sharpening the existing record's `Obligation`/`Why it applies` in place, because
the step's vocabulary offers only "add," not "refine."

**Change**: Update `skills/shortlist-research/SKILL.md:39` to mention refining or marking a seeded
obligation inapplicable, e.g. "…add, refine, or mark inapplicable the obligations field evidence
reveals, always with a recorded reason, and record a terminal disposition for every applicable
obligation."

Closing this without action is a correct response.

<!-- finding id=code/shortlist-research-skill/stale-add-only-obligation-verb axis=code action=consider priority=P3 fix=skills/shortlist-research/SKILL.md:39 head=4349ff41ff4d134e09017662dd30420b80e8eb30 -->

---

#### Observations

*(Per `publishing.md`, a real published summary caps this section at 3 items, the most decisive
evidence first. All 10 accurate asides raised across the run are reproduced below in full per this
report's own completeness requirement; the 3 that would make the actual cap are marked.)*

These are accurate observations, not findings — no action is requested.

1. **[Would publish]** `record-schemas.md:394-396`'s new refine/mark-inapplicable language is itself
   not mirrored anywhere in `search-bundle-format.md:208`'s obligation description either — a second,
   narrower staleness in the same paragraph beyond just the `Kind` enum. — Verifier observation.
   (`skills/shortlist/references/search-bundle-format.md:208`)
2. **[Would publish]** `docs/adr/0017-validate-applicable-research-obligations.md:7` still enumerates
   only "source families, audits, Candidate relationships, and discovery branches" (missing Safeguard,
   Other, and now Volatile-claim class) — an accurate but pre-existing gap this diff didn't create or
   worsen in kind. — Code finder observation. (`docs/adr/0017-validate-applicable-research-obligations.md:7`)
3. **[Would publish]** `tests/test_generalized_bundle.py:519-540`
   (`test_streaming_catalog_ledger_seeds_volatile_claim_classes`) is the only test exercising a
   `Volatile-claim class` obligation with `Origin: Research`, and it validates the ledger mechanics
   only — it does not check any SKILL.md or `search-bundle-format.md` prose text, so it would not have
   caught either staleness this review confirmed. — Verifier observation. (`tests/test_generalized_bundle.py:519`)
4. `PROJECT_BRIEF.md:85` similarly enumerates only "source families, audits, Candidate relationships,
   and discovery branches" without Safeguard/Other/Volatile-claim class — same pre-existing pattern. —
   Code finder observation. (`PROJECT_BRIEF.md:85`)
5. `skills/shortlist/references/research-protocol.md:406` and `narrowing-protocol.md:68` now both spell
   out nearly the same generalized-claim example list in slightly different words (e.g., "release
   support" vs. "support or lifecycle status") — accurate paraphrase, no contradiction, just duplicated
   prose across two files. — Code finder observation. (`skills/shortlist/references/research-protocol.md:406`)
6. `tests/fixtures/generalized-bundle/current/coverage.md:9-69` (unchanged by this diff) already models
   a community-technology category profile via `Category profile`-origin obligations, so the PR body's
   claim that this fixture "already covers the community-technology profile from #44" checks out
   without needing modification. — Requirements finder observation.
7. `docs/design/intake-criteria-and-ranked-narrowing.md:60` and
   `docs/adr/0007-non-llm-freshness-checker.md:13` (both unchanged, both outside the manifest) already
   describe the generalized Volatile-claim behavior this PR implements, so they required no update and
   are not stale peers. — Requirements finder observation.
8. `skills/shortlist/references/category-bundle-format.md:96,171` uses similar "price, stock, delivery,
   restock" wording, but it governs a distinct mechanism (warm-start cache freshness classes
   `structural`/`lineup`/`volatile`), already phrased open-endedly ("and similar observations"), and is
   not a peer of either changed contract. — Requirements finder observation.
9. Verified locally: `python3 -m unittest discover -s tests` → 290 tests, all passing;
   `node --test "tests/*.ts"` → 60 tests, all passing — matching the PR's verification claims
   (requirement 11, Met). — Requirements finder observation.
10. No unrequested scope creep found in Step 3: every hunk in the diff maps directly to one of the
    restated requirements. — Requirements finder observation.

---

### 3. Candidates refuted or dropped

**None.** The verifier's verdicts were `confirmed: 5, plausible: 0, refuted: 0` — every one of the 5
raised candidates was independently confirmed from the code alone, with no candidate needing
falsification. Per `verify.md`, a `refuted` candidate is dropped silently and never reaches
publication; there is nothing in that category to report for this run. Two of the five confirmed
candidates were merged as duplicates of the Requirements axis's twin (see §7 "Pole intact" and the
merge list under §1), which is a merge, not a drop — both survive, just under one id.

---

### 4. Both finders' complete disposition ledgers (verbatim)

#### Code axis — full disposition ledger (20 rows, as returned)

| # | Claim | Falsification route | Decisive evidence | Disposition |
|---|---|---|---|---|
| 1 | `OBLIGATION_KINDS` addition (record_schemas.py) is malformed/breaks callers | run full test suite | record_schemas.py:397; 290 tests pass | acquitted |
| 2 | `JUDGMENT_ONLY_ATTESTATIONS` new tuple entry breaks printing/tests | run full test suite, inspect print loop | validate-completion.py:79-91,3770-3771; tests pass | acquitted |
| 3 | search-bundle-format.md Kind list stale after enum grew | diff search-bundle-format.md base vs head; check sync precedent | search-bundle-format.md:208 unchanged; `git show 55e1f25 --stat` shows 4-file sync precedent | candidate |
| 4 | docs/adr/0017 Kind/obligation-source list stale after enum grew | check if ADR was updated in the precedent commit that added `Other` | `git show 55e1f25 --stat` does not include ADR 0017; ADR already omitted Safeguard/Other pre-diff | acquitted — pre-existing drift, ADRs not kept in sync by established convention |
| 5 | PROJECT_BRIEF.md:85 obligation list stale after enum grew | check PROJECT_BRIEF.md against pre-diff enum | PROJECT_BRIEF.md:85 already omitted Safeguard/Other before this diff | acquitted — pre-existing drift |
| 6 | shortlist-narrow/SKILL.md:46 fixed Volatile list stale after Freshness generalization | check prior sync commit; check new fixture against the fixed list | `git log -p --follow` shows commit 1450bc2 rewrote this exact line in lockstep with narrowing-protocol.md; new streaming fixture Record 7 doesn't fit the fixed list | candidate |
| 7 | shortlist-research/SKILL.md:39 "add obligations" undersells new refine/mark-inapplicable capability | check prior sync commit (1450bc2) | shortlist-research/SKILL.md:39 unchanged, matches only the retired "may add" wording | candidate |
| 8 | freshness-checker.md's volatile-kind list is stale after Freshness generalization | grep for fixed commerce list in checker doc | freshness-checker.md:6 already says "plus the category-applicable Volatile vocabulary of ADRs 0015–0017"; commit message states checker is explicitly out of scope | acquitted |
| 9 | category-bundle-format.md's "restock" list (lines 96, 171) is a stale closed list | inspect wording | both instances end in "and similar observations", already open-ended | acquitted |
| 10 | research-protocol.md:67 "cached price, stock, delivery, restock" is a stale closed list | inspect wording | ends in "or similarly volatile claims", already open-ended | acquitted |
| 11 | docs/design/intake-criteria-and-ranked-narrowing.md is stale re: generalized Freshness/obligations | read full relevant section | lines 26, 60, 74 already state the fully generalized rule (this design doc pre-dates and anticipates the diff) | acquitted |
| 12 | docs/design/use-scenario-catalog.md contradicts new "Category profile" definition | read status line and catalog rules | status line ("not a … category-profile specification, benchmark list…") is consistent with new CONTEXT.md/research-protocol.md text | acquitted |
| 13 | New streaming ledger fixture (tests/fixtures/generalized-bundle-streaming/ledger.md) is structurally/semantically invalid | run targeted test, inspect required fields and Sxxx citations | `test_streaming_catalog_ledger_seeds_volatile_claim_classes` passes; all 8 records have required fields and valid S001–S005 citations | acquitted |
| 14 | New physical-ledger Record 9 (Volatile-claim class) breaks existing physical fixture tests | run `test_physical_product_ledger_covers_applicable_work` and friends | test passes; S003/S004 already committed in that fixture's task history | acquitted |
| 15 | New `test_completion_attestations_cover_freshness_credibility` is a false-positive/no-op test | run it in isolation, inspect state.md field replacements | test passes and its assertions require `--require-complete` output to include the new attestation text | acquitted |
| 16 | New ledger fixtures have Markdown formatting bugs (missing blank lines, block boundaries) that would break `field_blocks`/`validate` parsing | run `validate()` against `GENERALIZED` fixture and completion validator against physical/streaming ledgers via the test suite | full suite green, no parse errors | acquitted |
| 17 | CONTEXT.md's new "Category profile" glossary entry conflicts with an existing glossary term | read full CONTEXT.md glossary section around the edit | no existing "Category profile" entry at base; no other entry contradicts the new one | acquitted |
| 18 | narrowing-protocol.md's Volatile-evidence rewrite and research-protocol.md's Freshness rewrite say materially different, conflicting things | read both full sections side by side | both consistently describe "ledger/category-driven, not fixed list" refresh; vocabulary overlaps intentionally (commerce examples vs generalized examples) | acquitted |
| 19 | research-protocol.md's new "Governing and regulatory material controls" paragraph conflicts with existing design guidance | cross-check against docs/design/intake-criteria-and-ranked-narrowing.md:60 | that design doc already states the identical rule ("governing documents and authoritative regulatory sources control policy and legal claims") | acquitted |
| 20 | record_schemas.py / validate-completion.py additions have a typo, wrong ordering, or syntax defect | read diff hunks directly, run tests | both diffs are minimal, correctly formatted frozenset/tuple entries; tests pass | acquitted |

**Method note (Code finder, verbatim):** "I read the full diff and commit as delivered, ran
`python3 -m unittest discover -s tests -p "test_*.py"` in the read-only clone (290 tests, all pass,
including all new tests in `tests/test_generalized_bundle.py`), and inspected the enclosing sections
of every changed reference/protocol file. Per the brief's 'Sync drift from a changed rule' section, I
identified three distinct qualifying contracts this diff touches and swept each across the whole
repository (old-wording fragment search + new-wording search), using `git log`/`git show` on prior
commits that touched the same contracts to establish which peer files are conventionally kept in
lockstep versus which are historical/point-in-time by established practice."

#### Requirements axis — disposition record, as actually returned

**Important note on this section, stated plainly per this run's own reporting requirement:** the
Requirements finder's brief requires "your disposition ledger — one table row per hypothesis you
weighed, including those acquitted before returning them and those resolved to questions… Each row
has four compact fields on one line." **The Requirements finder did not return a table in this shape.**
What it returned instead is a prose-form changed-contract sweep (below), reproduced verbatim, which
documents the two peers it found stale (both became candidates) but does **not** document any
"tried-to-convict-and-acquitted" hypotheses distinct from those two — unlike the Code finder, which
returned 20 explicit rows including 15 acquittals. This asymmetry is called out again under the C3
mechanism check in §7; it means the Requirements axis's search process (what other files it checked
and dismissed while sweeping) is not independently auditable from its output the way the Code axis's
is. I am not fabricating rows to fill this gap — the absence itself is the finding.

What the Requirements finder actually returned, verbatim:

> **Contract A — the Research-obligation `Kind` enumeration** (closed list `Source family, Audit,
> Candidate relationship, Discovery branch, Safeguard, Other` extended with `Volatile-claim class`).
> - New-term search: `"Volatile-claim class"` → live hits in `CONTEXT.md:327,331`,
>   `skills/shortlist/references/record-schemas.md:392`,
>   `skills/shortlist/references/research-protocol.md:289,295`,
>   `skills/shortlist/scripts/record_schemas.py:397`, and the two/three fixtures/tests. All consistent
>   with the new vocabulary.
> - Old-fragment search: `"discovery branch, safeguard"` (three consecutive members of the pre-diff
>   list) → same four prose hits above (all updated) **plus one live, un-updated peer**:
>   `skills/shortlist/references/search-bundle-format.md:208`, which still reads "…discovery branch,
>   safeguard, or other category-relevant work" with no `Volatile-claim class`. This file is not in
>   the changed-file manifest and was not touched by the diff.
> - Disposition: peer at `search-bundle-format.md:208` is stale → **candidate**.
>
> **Contract B — the fixed-per-bundle-type Volatile/freshness claim list, replaced by an open,
> ledger-driven rule**.
> - New-wording search: `"whichever claims the category and ledger identif"` /
>   `"not only a fixed commerce list"` → live in
>   `skills/shortlist/references/narrowing-protocol.md:68` and
>   `skills/shortlist/references/research-protocol.md:406` (both updated, both carry the open escape
>   hatch "another decision-relevant class…").
> - Old-fragment search: `"price, stock, delivery, and restock"` → hits in
>   `docs/adr/0007-non-llm-freshness-checker.md` (already forward-looking, explicitly says ADRs
>   0015–0017 broaden this — consistent, not stale),
>   `skills/shortlist/references/freshness-checker.md` and `skills/shortlist/scripts/check_freshness.py`
>   (deliberately out of scope per the issue's own non-goal and the commit message — not stale,
>   confirmed acquitted), `skills/shortlist/references/category-bundle-format.md:96,171` (a different
>   mechanism — warm-start cache reuse classes `structural`/`lineup`/`volatile` — already phrased
>   open-endedly as "…and similar observations," not the Narrow-handoff refresh contract this diff
>   changed), and **one live, un-updated peer that is the same contract**:
>   `skills/shortlist-narrow/SKILL.md:46` — "Refresh volatile evidence before the final handoff …
>   price, stock, delivery, and restock facts in a commerce bundle; access, cost, catalog, licensing,
>   compatibility, and support claims in a generalized bundle." This is the Narrow skill's own
>   operative restatement of the exact rule the diff generalized, and it still uses the old closed
>   dual-list shape with no "another decision-relevant class" escape hatch. `README.md:103` and
>   `docs/design/intake-criteria-and-ranked-narrowing.md:14` both cite this SKILL.md as "the
>   implemented contract" for the Narrow stage.
> - Disposition: peer at `skills/shortlist-narrow/SKILL.md:46` is stale → **candidate**.

**Counts (verbatim):** Met: 9 (requirements 1, 2, 3, 5, 6, 8, 9, 10, 11). Not met (partial): 2
(requirements 4 and 7 — both are "correctly generalized in the primary reference doc, but a live
sibling document was not updated," found by the peer sweep above). Cannot tell from the code: 0.

**Restated requirements, verbatim (Step 1, from issue #45's acceptance criteria):**

1. A category profile may seed likely source families, audits, Candidate relationships, discovery
   branches, safeguards, **and Volatile-claim classes**, without acting as a closed checklist.
2. Profiles are derived from the recorded Candidate field and Use conditions; the exploratory
   use-scenario catalog must not become executable routing or a required one-profile-per-scenario
   registry.
3. Research may add, refine, or mark a seeded obligation inapplicable, always with a recorded reason;
   every resulting applicable obligation still follows the ledger completion rules.
4. `Volatile-claim class` becomes a formally documented obligation `Kind`, consistently reflected
   everywhere the obligation vocabulary/schema is documented.
5. Evidence can mark any decision-relevant claim as Volatile, carrying an observation date and a
   category-appropriate freshness expectation.
6. The applicable Volatile-claim classes explicitly include cost, access, catalog contents, policy
   terms, compatibility, release support, stock, delivery, or another evidenced class.
7. Narrow refreshes every materially stale applicable Volatile claim before final handoff, preserves
   prior observations in history, and does not assume only commerce facts can expire — this
   generalization must hold everywhere the Narrow-stage refresh behavior is documented, not only in
   one reference file.
8. Authoritative-source guidance varies by claim: governing/regulatory material controls a claim
   within its authority; declared, measured, and observed evidence keep their distinct roles.
9. Focused fixtures cover: a physical-product profile, a community-technology profile, a
   streaming-like catalog claim, and a claim class added during Research.
10. This ticket explicitly does not implement the separate non-LLM freshness-checker issue.
11. The complete automated test suite passes.

Background/non-requirements noted but not checked as requirements (verbatim): "the 'Blocked by #40,
#44' dependency note, and the PR body's own prose (used only to identify deliberate/non-goal claims,
not as a spec source since issue #45 exists)."

---

### 5. Notes on the run — judgment calls and guidance membership

- **Guidance membership (judgment call).** SKILL.md's process step says guidance "includes
  `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`, and scoped equivalents." This
  repository has no `CLAUDE.md`, `CONTRIBUTING.md`, or `CODING_STANDARDS.md` at the base SHA. It does
  have `AGENTS.md` (explicit guidance per the list) at the root, which itself delegates to two
  satellite files — `docs/agents/domain.md` and `docs/agents/issue-tracker.md`. I treated both
  satellite files as "scoped equivalents" and therefore guidance, since `AGENTS.md` is not
  self-contained but exists specifically to point at them for its two named concerns (domain docs,
  issue tracker verbs). I additionally treated `CONTEXT.md` (root) as guidance, on the reasoning that
  `docs/agents/domain.md` makes it explicitly normative for vocabulary ("When naming a domain concept,
  use the term as defined in `CONTEXT.md`") — a scoped equivalent of a coding/vocabulary standard —
  and because `CONTEXT.md` is itself a changed file in this diff, directly implicated in the
  sync-drift mechanism this run exists to check. All four files were confirmed byte-identical between
  the staged `guidance-target1/` copies and `git show main:<path>` in the clone before use, so
  base-branch provenance is not in question — only which of them count as "guidance" was a judgment
  call, and I've named it here as instructed.
- **No re-review context.** This is a first review of this PR under the pinned "Prior review state:
  none" condition; no re-review machinery (prior findings ledger, reply/verdict trailers) applied.
- **No question-routing scenario.** The Requirements finder's "cannot tell from the code" bucket
  returned 0 items; nothing was routed to a question, and the verifier returned 0 `plausible`
  verdicts, so no question-shaped output exists to report as absent — it simply never arose (see C4
  in §7).
- **The one real ambiguity I had to resolve:** whether to independently pre-merge the two
  cross-axis duplicate pairs (Code/Requirements candidates describing the same fix site) before
  handing them to the verifier, or to pass all 5 candidates through unmerged and let the verifier's
  own dedup rule (`verify.md` § Deduplicate) do the merging. I chose the latter — passing all 5
  through separately — because pre-merging is explicitly the finder's or orchestrator's job encroaching
  on a step the skill assigns to the verifier, and because SKILL.md's fan-out step returns "candidates,
  not findings" per axis without instructing the orchestrator to reconcile across axes before
  verification. The verifier did perform the merge correctly and explained its reasoning (§ Merge list,
  reproduced in §7).

---

### 6. The three known items — per finder, verbatim, both ledgers checked

#### (a) `skills/shortlist/references/search-bundle-format.md:208`'s stale five-kind enumeration (the item the `326ef6f` fix targeted)

**Raised by both finders, as a candidate, independently.**

- **Code finder** — ledger row 3 (verbatim): *"search-bundle-format.md Kind list stale after enum
  grew | diff search-bundle-format.md base vs head; check sync precedent | search-bundle-format.md:208
  unchanged; `git show 55e1f25 --stat` shows 4-file sync precedent | candidate"* — and returned it in
  full as Candidate 1, `code/search-bundle-format/stale-obligation-kind-enum`.
- **Requirements finder** — Contract A's sweep (verbatim): *"Old-fragment search:
  `'discovery branch, safeguard'` … → same four prose hits above (all updated) plus one live,
  un-updated peer: `skills/shortlist/references/search-bundle-format.md:208`, which still reads
  '…discovery branch, safeguard, or other category-relevant work' with no `Volatile-claim class`.
  This file is not in the changed-file manifest and was not touched by the diff. Disposition: peer at
  `search-bundle-format.md:208` is stale → **candidate**."* — and returned it in full as Candidate 1,
  `requirements/search-bundle-format-stale-obligation-kind`.
- **Verifier**: confirmed, both instances merged into `requirements/search-bundle-format-stale-obligation-kind`,
  surviving as **P1/consider**.

#### (b) `skills/shortlist-narrow/SKILL.md:46`'s closed Volatile refresh list (the item the `940aa2c` fix targeted; **the single most important check of this run**)

**Raised by both finders, as a candidate, independently.**

- **Code finder** — ledger row 6 (verbatim): *"shortlist-narrow/SKILL.md:46 fixed Volatile list stale
  after Freshness generalization | check prior sync commit; check new fixture against the fixed list |
  `git log -p --follow` shows commit 1450bc2 rewrote this exact line in lockstep with
  narrowing-protocol.md; new streaming fixture Record 7 doesn't fit the fixed list | candidate"* — and
  returned it in full as Candidate 2, `code/shortlist-narrow-skill/stale-fixed-volatile-list`.
- **Requirements finder** — Contract B's sweep (verbatim): *"Old-fragment search:
  `'price, stock, delivery, and restock'` → hits in … and **one live, un-updated peer that is the same
  contract**: `skills/shortlist-narrow/SKILL.md:46` — … This is the Narrow skill's own operative
  restatement of the exact rule the diff generalized, and it still uses the old closed dual-list shape
  with no 'another decision-relevant class' escape hatch. … Disposition: peer at
  `skills/shortlist-narrow/SKILL.md:46` is stale → **candidate**."* — and returned it in full as
  Candidate 2, `requirements/shortlist-narrow-skill-stale-freshness-list`, at **P1/must-fix** — the
  only `must-fix` this run produced.
- **Verifier**: confirmed independently (fresh context, no `support` seen), and — critically — kept
  the `must-fix` action rather than downgrading it, on the grounds that `skills/shortlist-narrow/SKILL.md`
  is cited elsewhere as "the implemented contract" for the Narrow stage and is followed as an executed
  step rather than read as background documentation, and that this PR's own new fixture supplies a
  concrete, in-repo instance of the gap biting (a `Volatile-claim class` outside the fixed list). Both
  instances merged into `requirements/shortlist-narrow-skill-stale-freshness-list`, surviving as
  **P1/must-fix**. **This is the item the previous run under this skill (on a different model) is
  recorded as having missed entirely — neither finder raising nor acquitting it. In this run, both
  finders found it independently, and the fresh-context verifier independently confirmed it as the
  run's one blocking finding.**

#### (c) `skills/shortlist/scripts/validate-completion.py`'s hardcoded retired Volatile-term regex (~line 2948)

**Confirmed present in the actual code** — a repository-wide check during this compilation located it
at line 2949 (not 2948; off by one from the dispatch's approximate pointer, but the same object):

```python
volatile = re.search(
    r"\b(?:price|stock|delivery|restock|availability|available|unavailable)\b",
    claim_text,
    re.I,
)
```

This regex hardcodes exactly the retired commerce-only Volatile-term list (`price`, `stock`,
`delivery`, `restock`, plus availability variants) to decide whether a piece of history-evidence text
requires an offset-bearing timestamp — the same mechanism this PR's Freshness/Volatile-evidence
generalization targets, in a third location neither reference doc's prose sweep would touch (it's a
regex inside a validator script, not a documentation restatement).

**It does not appear anywhere in either finder's output — not as a candidate, not as an acquittal, not
as an observation. Stated plainly: it is absent, in both ledgers, in both sets of observations, and in
both changed-file-manifest entries for `validate-completion.py`.**

- **Code finder**: mentions `validate-completion.py` in exactly two ledger rows (2 and 20) and one
  manifest entry, all three scoped to the diff's own visible addition (the new
  `JUDGMENT_ONLY_ATTESTATIONS` tuple entry) — verbatim: *"`JUDGMENT_ONLY_ATTESTATIONS` new tuple entry
  breaks printing/tests"* (row 2, acquitted) and *"record_schemas.py / validate-completion.py additions
  have a typo, wrong ordering, or syntax defect"* (row 20, acquitted). Nothing in the ledger, the
  observations, or the manifest reason ("New `Freshness credibility` entry verified correct via test
  suite; no defect") reaches line 2949's pre-existing regex at all.
- **Requirements finder**: does not mention `validate-completion.py` outside its manifest entry
  ("New `Freshness credibility` attestation checked; confirmed it prints under
  `--require-complete`/`--require-handoff` via the new test and a manual run"), and its Contract B
  peer sweep — which is exactly the sweep that should have surfaced this file, since the regex is a
  live peer carrying the retired term list — did not turn it up. The file was not in the diff, so a
  sweep confined to grep-for-old-fragment across the repo (which the finder says it ran: `"price,
  stock, delivery, and restock"`) should in principle have matched this line's `price|stock|delivery|restock`
  fragment; the finder's own reported hit list for that search names
  `docs/adr/0007-non-llm-freshness-checker.md`, `freshness-checker.md`, `check_freshness.py`, and
  `category-bundle-format.md:96,171`, but not `validate-completion.py:2949`. This is either a genuine
  miss of a live hit its own stated search should have returned, or the exact regex characters
  (`price|stock|delivery|restock` joined by `|` inside a raw string, no comma-separated prose list)
  did not surface under whatever search tooling or fragment variant it actually used — I cannot
  determine which from the output alone, and I am not able to re-run the finder's search on its
  behalf without re-introducing exactly the kind of second-guessing this report is supposed to avoid.
  Either way, the item is absent from its returned ledger.

**This is a real gap in both finders' recall for this specific target — worth flagging as clearly as
the dispatch asked**, since it is a third, distinct example of the same "sync drift from a changed
rule" pattern the `940aa2c` fix (Sweep every changed contract, on both axes) was specifically built to
catch, and it went unswept by both axes in this run despite the Requirements finder's own reported
old-fragment search string appearing to be a literal substring match for it.

---

### 7. Mechanism checklist

- **C1 (Calibration).** Recall: **both** of the target's two known doc-sync drifts were found — see
  (a) and (b) in §6, each raised independently by both finders and confirmed independently by the
  verifier. Recall is fully preserved (2/2), a clear improvement in this run over the previous run
  under this skill, which the dispatch records as having missed (b) entirely.
  Calibration: **not uniformly non-blocking.** (a) landed as `P1/consider` — correctly advisory,
  because `search-bundle-format.md` is a descriptive contract-summary document and the canonical
  enforcement (`record_schemas.py`'s `OBLIGATION_KINDS`, `record-schemas.md`'s prose) is already
  correct and in sync. (b) landed as `P1/must-fix` — the verifier confirmed this action independently,
  reasoning from `finding-format.md`'s own calibration text ("a proven … explicit-requirement gap on
  an authoritative execution path is must-fix, even when the edit is one line or documentary") that
  `skills/shortlist-narrow/SKILL.md` is not background documentation but an operative, executed script
  cited elsewhere as "the implemented contract" for the Narrow stage, and that this PR's own fixture
  supplies a demonstrated merge consequence (a Volatile-claim class the fixed list cannot cover).
  **Derived status is therefore `Changes Requested (advisory)`, not `Approved (advisory)`.** The
  status ladder in `publishing.md` keys on action alone ("Any unsettled `must-fix` … → `Changes
  Requested`. … Priority never enters the derivation"), so this one confirmed `must-fix` is
  unconditionally blocking regardless of the other two findings being merely advisory. This is a
  genuine, load-bearing result of this run and I am reporting it as measured rather than reshaping it
  toward an assumed "should be advisory" outcome: the mechanism correctly distinguished an executed
  operational script from a descriptive summary and calibrated each accordingly, and the resulting
  status is the honest consequence of that distinction, not a miscalibration.
- **C3 (Disposition ledger).** **Partial.** The Code finder returned a complete, correctly-shaped
  20-row ledger including 15 explicit "tried-to-convict-and-acquitted" rows (§4). The Requirements
  finder did **not** return a ledger in the brief's required shape — it returned the two
  changed-contract sweeps (which do carry a claim/evidence/disposition triple each) but no rows
  documenting any hypothesis it weighed and rejected beyond the two live peers it found stale. Its own
  Contract B write-up *lists* four other files it checked and dismissed as non-stale
  (`docs/adr/0007-non-llm-freshness-checker.md`, `freshness-checker.md`, `check_freshness.py`,
  `category-bundle-format.md`) inline in prose, so the acquittal reasoning exists in the text — it is
  just not formatted as the compact one-line-per-row ledger the brief specifies. I am flagging this as
  a partial miss on this mechanism for the Requirements axis specifically, not smoothing it into a
  pass.
- **C5 (Observations).** **Confirmed present.** The Code finder returned 3 observations, the
  Requirements finder returned 5, and the verifier returned 2 — all landed outside the verdict list,
  correctly separated from the candidate/finding machinery (§2 reproduces all 10, noting which 3 a
  real publication would keep under the cap).
- **Pole intact.** Confirmed on all three counts: (1) both finders ran — Code and Requirements, in
  parallel, both returned complete reports; (2) every one of the 5 candidates received an explicit
  verifier verdict — 5/5 `confirmed`, 0 unaddressed; (3) `support` fields were withheld from the
  verifier — I built the verifier's prompt myself (reproduced in full in my own working files at
  `/tmp/handoff3/v2a-target1-run3-verifier-prompt.md`) and it contains, per candidate, only `id`,
  `axis`, `anchor`, `fix`, `title`, `claim`, `trigger`, `priority`, and `action` — no `support` field
  for any of the 5 candidates. I checked this by construction (I wrote the prompt from the finders'
  returned fields, deliberately omitting `support`) rather than after the fact.
- **C2 (no-issue rule) and C4 (question-routing)** do not apply to this target, as instructed: this PR
  has an originating issue (`kamui/shortlist#45`), so the Requirements finder ran a normal
  issue-compliance pass rather than the no-issue body-claims substitute; and no question-routing
  scenario arose because the Requirements finder's "cannot tell from the code" bucket returned 0 items
  and the verifier returned 0 `plausible` verdicts, so nothing was ever eligible to become a question.
  Noted explicitly rather than forced.

---

### 8. Run integrity

- No network call of any kind was made by the orchestrator or, per each sub-agent's own report and
  explicit prompt-level prohibition, by any finder or the verifier.
- No file inside `/tmp/handoff3/run-v2a-target1` was modified, checked out, reset, or stashed at any
  point in this run. Verified clean at the start (before dispatch) and re-verified at the end of this
  compilation step: `git -C /tmp/handoff3/run-v2a-target1 status --short` returns nothing and
  `git status` reports "On branch review-head / nothing to commit, working tree clean" as the final
  check before writing this report. No `git reset --hard` was ever needed.
- No file was created inside the clone; all working files (shared block, axis prompts, finder reports,
  verifier prompt and report, this report) live under `/tmp/handoff3/` outside the clone.
- Nothing was published anywhere; this section and §2 constitute the complete would-be output in place
  of a real publish action.

