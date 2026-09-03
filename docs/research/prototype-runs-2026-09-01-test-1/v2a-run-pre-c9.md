# v2a run (pre-C9, superseded) — `code-review-deep-publish` against `kamui/shortlist#66`

> **Superseded.** This is the first 2026-09-02 v2a run, under skill commit `5db5903` (handoff 5's
> paired-sweep fix only). Its "known item this run missed" section is what prompted DESIGN.md §C9
> and commit `940aa2c` "Sweep every changed contract, on both axes". The re-run under the fixed
> skill (`87c68a9`) is the record of note, held in
> [`../prototype-runs-2026-09-01-test-1-fable/v2a-run.md`](../prototype-runs-2026-09-01-test-1-fable/v2a-run.md)
> because it ran on a different model. Kept verbatim as the
> before-state for the regression watch in [`addendum-2026-09-02.md`](addendum-2026-09-02.md).

**2026-09-02.** Data only. Not published to the PR. See
[`addendum-2026-09-02.md`](addendum-2026-09-02.md) for run conditions, model/harness, and the
dev-set caveat that applies to this run.

## Metadata

| | |
| --- | --- |
| Skill | `code-review-deep-publish` (research nickname **v2a**, "Panel line"; [PR #18](https://github.com/kamui/skills/pull/18), branch `t3code/prototype-code-review-publish-2a`, pinned commit `5db5903`) |
| Includes fix | `326ef6f` "Require paired peer-contract sweeps" (handoff 5's fix — the Requirements axis must now search both the new term and a surviving base-contract phrase before marking a vocabulary/enum requirement `Met`) |
| Architecture | 2 axis finders in parallel (Code, Requirements) → 1 mandatory fresh-context verifier |
| Model | `claude-sonnet-5` on every agent, verified from the harness's sub-agent transcripts |
| Agents spawned | 3 |
| **Total sub-agent tokens** | **246,621** |
| — Code finder | 97,617 (29 tool uses, 246,029 ms / ~4.10 min) |
| — Requirements finder | 110,705 (50 tool uses, 555,478 ms / ~9.26 min) |
| — Verifier | 38,299 (27 tool uses, 170,911 ms / ~2.85 min) |
| Total tool uses (sub-agents) | 106 |
| Wall clock (sub-agents) | ~726 s (finders parallel at max 555 s, then verifier +171 s) |
| Orchestrator tokens/tool-uses | not instrumented by this harness the way sub-agent usage is; the orchestrating run itself (per the harness's outer `<usage>` wrapper) totaled 182,133 tokens / 41 tool uses / 1,551,133 ms wall clock, which is the number to use for a total-cost comparison against v5a |
| Candidates raised | 1 (Requirements axis only; Code axis raised 0) |
| Verdicts | 1 confirmed · 0 plausible · 0 refuted · 0 merged |
| Findings for publication | **1** — P3 `consider` |
| Questions | 0 |
| Coverage | complete (9/9 files, both finders) |
| Derived status | **Approved (advisory)** |

## Findings

### F1 — `requirements/search-bundle-format-stale-obligation-kind` — consider / P3

- **anchor** `skills/shortlist/references/record-schemas.md:392`
- **fix** `skills/shortlist/references/search-bundle-format.md:208`

`record-schemas.md:392` (and `record_schemas.py`'s `OBLIGATION_KINDS`) add a sixth Research-obligation
`Kind`, `Volatile-claim class`, to `Source family`, `Audit`, `Candidate relationship`,
`Discovery branch`, `Safeguard`, `Other`. `search-bundle-format.md:208` mirrors the same enumeration
in near-identical prose and was **not touched by this diff** (`git diff base...head --
search-bundle-format.md` is empty) — it still enumerates only the five pre-PR kinds.

Verifier: **confirmed**, with a corrected, narrower trigger. The finder's search-bundle-format.md
sentence at line 208 links directly to `record-schemas.md#research-obligation`, the file's own
canonical field-value source, so a reader who follows the link still lands on the correct six-value
list. Corrected trigger: a reader who stops at the summary sentence without following the adjacent
link sees only five categories and does not learn `Volatile-claim class` is valid — a real but
narrower harm than the finder's original framing, which is why priority/action stayed P3/`consider`
rather than escalating.

**Trigger:** a reader consults `search-bundle-format.md` as the bundle-contract summary, reads only
the inline sentence, and comes away believing `Volatile-claim class` is not a valid `Kind`, even
though the validator, `record-schemas.md`, `CONTEXT.md`, `research-protocol.md`, and both new/updated
test fixtures all treat it as valid.

**This is the item the paired peer-contract sweep fix (handoff 5) was written to catch.** The
Requirements finder's own `support` field confirms it ran both legs of the sweep — a new-term search
*and* a base-contract-phrase search — rather than only the new-term search that caused the original
miss: "Ran `git diff ... -- search-bundle-format.md` (empty output). Grepped the repo for
'Discovery branch' and 'Safeguard' to find every live peer of the enumeration; `search-bundle-format.md:208`
was the only other file carrying this same enumeration prose." The verifier independently
reconstructed and confirmed the same empty-diff fact rather than trusting the finder's word. **On
this specific check, the fix worked exactly as designed.**

## A known item this run missed — new, reportable gap

This target has **two** known doc-sync drifts from the original v2–v5 comparison, not one — the
bundle-contract enumeration above (found, this run), and a second: the Narrow-stage entrypoint's
closed refresh list at `skills/shortlist-narrow/SKILL.md:46` ("Refresh volatile evidence before the
final handoff... price, stock, delivery, and restock facts in a commerce bundle; access, cost,
catalog, licensing, compatibility, and support claims in a generalized bundle" — still closed,
confirmed still present verbatim at head via `git show review-head:skills/shortlist-narrow/SKILL.md`).

All four original prototypes (v2 F2, v3, v4, v5 finding 2) found this second drift, **and so did the
pre-fix round of this same v2a skill** (handoff 6's background section credits "this same round's
v2a run" with finding it as F1, verifier-confirmed P1 must-fix). **Neither finder in this run raised
it — it does not appear anywhere in either finder's disposition ledger below, not even as an
acquitted hypothesis.** This is a genuine recall gap in this specific run, sitting right next to the
paired-peer-contract-sweep fix's confirmed success on the other item. See the addendum's regression
watch; this is n=1 and needs a repeated-seeds look before it's called systematic, but it is flagged
here because it wasn't present in the round that motivated the fix.

## Disposition ledgers (both finders, complete — every hypothesis weighed, including acquittals)

### Code axis (0 candidates, 7 acquittals + 1 observation)

| Claim | Falsification route | Decisive evidence | Disposition |
| --- | --- | --- | --- |
| New `Volatile-claim class` Kind not reflected in ADR 0017 | Read ADR 0017 | `docs/adr/0017-*.md` already omits `Safeguard`/`Other` before this PR | acquitted (pre-existing) |
| New `Freshness credibility` attestation is unenforced dead weight | Check whether other attestations in the tuple are enforced | Whole tuple printed as "not mechanically validated"; five prior entries are the same shape | acquitted |
| `check_freshness.py` regex set doesn't support the newly-generalized language | Read `VOLATILE_PATTERNS` | `check_freshness.py:34-59` already has `catalog`, `plan-feature`, `cost` patterns pre-dating this diff | acquitted |
| Streaming/physical fixtures reference `Snnn` IDs not present in a real bundle | Check how fixtures are consumed | `test_generalized_bundle.py:503-542` checks fixtures only against a synthetic `committed` set | acquitted |
| Duplicate `Obligation` names within new ledger fixtures | Run `research_obligation_syntax_errors` | Both new tests assert `[]` and pass | acquitted |
| `OBLIGATION_KINDS` addition breaks a hardcoded enum list elsewhere | grep for other Kind enumerations | No hits in `skills/shortlist/assets/**` or other scripts | acquitted |
| `matching_inaccessible_route`'s `Kind == "Source family"` special-case mishandles `Volatile-claim class` marked `Inaccessible` | Check whether any record uses that combination | No fixture/template uses that combination; logic unchanged | acquitted |
| New test `test_completion_attestations_cover_freshness_credibility` only checks a substring | quality note | `test_generalized_bundle.py:67-86` | observation, not a candidate |

Ran `python3 -m unittest tests.test_generalized_bundle -v` (53/53) and the full suite (290/290)
read-only.

### Requirements axis (1 candidate, 8 acquittals)

Restated 10 acceptance criteria first: 9 met, 1 not met (AC1/the bundle-contract enumeration),
0 unverifiable.

| Claim | Falsification route | Decisive evidence | Disposition |
| --- | --- | --- | --- |
| Kind enum broadened but a live peer doc wasn't updated | repo-wide grep for enumeration phrasing + diff on peer file | `search-bundle-format.md:208`; `git diff` empty for that file | **candidate (F1)** |
| `PROJECT_BRIEF.md`'s obligation-seed list is also stale | check if diff touches it / predates PR | `PROJECT_BRIEF.md:85` already lacked "Safeguard" pre-PR | acquitted (pre-existing) |
| `check_freshness.py` "already generalized" PR-body claim is false | read script's `VOLATILE_PATTERNS`/doc | `check_freshness.py:37-68`, `freshness-checker.md:6-8` show broad kind detection already present | acquitted |
| AC4 (Volatile marking w/ observation date + freshness expectation) unimplemented | check Evidence schema + glossary for pre-existing mechanism | `record-schemas.md` Evidence fields (`Observed`), `CONTEXT.md:294-296` unchanged by diff | acquitted (pre-existing, unaffected) |
| AC8(b) community-technology fixture missing Volatile-claim-class content | check whether a new/updated fixture exists | `generalized-bundle/current/coverage.md` unchanged, no Volatile-claim-class record | acquitted / observation (ambiguous scope) |
| Streaming ledger fixture is structurally/terminally valid | run repo test suite | `test_streaming_catalog_ledger_seeds_volatile_claim_classes` passes | acquitted |
| Physical ledger fixture covers full obligation-kind/origin enum | run repo test suite | `test_physical_product_ledger_covers_applicable_work` passes | acquitted |
| Full test suite fails somewhere | run `python3 -m unittest discover -s tests` at head | 290 tests, all pass | acquitted |
| New "Freshness credibility" attestation is scope creep | check whether it serves a stated AC | matches AC6, same shape as existing attestations | acquitted |
| `use-scenario-catalog.md` becomes executable routing | check whether file itself was modified/still self-disclaims | catalog file unmodified; intro already disclaims routing | acquitted |

Requirements finder's counts: **met 9, not met 1, unverifiable 0.**

### Verifier's addition

No new candidates (verifier does not add findings). One negative-check observation: confirmed the
stale-enumeration pattern does not recur anywhere besides `search-bundle-format.md` —
`research-protocol.md` already carries `Volatile-claim class` correctly, so the drift is isolated to
one file.

## Notes on the run

- **Guidance membership (explicit judgment call — no `CLAUDE.md`/`CONTRIBUTING.md` exists at base):**
  treated `AGENTS.md` and `docs/agents/domain.md` as the repo's scoped equivalents (`AGENTS.md` is
  named literally in the skill's guidance list; `domain.md` is the agent-facing process document
  `AGENTS.md` points to). Treated base-branch `CONTEXT.md` as guidance too, since `domain.md`
  instructs using its vocabulary, and the diff itself edits `CONTEXT.md`. Excluded
  `docs/agents/issue-tracker.md` — read for target resolution but treated as forge-verb
  configuration, not a content standard, since nothing in the diff touches issue-tracking
  conventions. This was stated to both finders explicitly rather than decided silently.
- **Verifier necessity:** Code axis returned 0 candidates but Requirements returned 1, so per
  SKILL.md's plural condition ("finders that return no candidates" — both must) the verifier step
  was not skippable, and ran.
- **Observations cap:** `publishing.md` bounds the published Observations section to 3 items; 5
  distinct observation-shaped items surfaced across both finders and the verifier (ADR 0017
  staleness, thin substring-only test, AC8 fixture-scope ambiguity, `PROJECT_BRIEF.md:85` staleness,
  verifier's "drift is isolated" note). All 5 are reported above/in the ledgers for research
  completeness; a real publish would keep only the 3 most decisive and drop the weakest two.
- **No live-state contamination:** the orchestrator read this research program's own prior-round
  docs (this test's `README.md`/`evaluation.md`, `DESIGN.md` §C8) to know what the calibration
  checklist was asking about, and to confirm file/line identities after the run finished — never fed
  to either finder or the verifier. Both finders and the verifier worked from the shared/axis-specific
  prompt blocks only, with no hint toward `search-bundle-format.md` or `shortlist-narrow/SKILL.md`.
- **Clone hygiene:** the orchestrator ran a stray `git checkout -- .` pair against the clone while
  inspecting the manifest; caught before any subagent ran and repaired with `git reset --hard
  review-head`, then reconfirmed a clean tree. No subagent read the clone in a disturbed state.

## Mechanism checklist

- **C1 (Calibration) — partially demonstrated, one real gap.** Of the target's two known drifts: the
  bundle-contract enumeration was found and correctly landed non-blocking (P3 `consider`,
  verifier-confirmed, derived status `Approved (advisory)` — calibration is right for this item). The
  Narrow-stage fixed-list item was not found by either finder and does not appear in either ledger
  even as an acquitted hypothesis. Recall was therefore **half-preserved** (1 of 2 known items) this
  run, while calibration was correct for the one item that was found. The derived status
  (`Approved (advisory)`) is computed correctly from what the finders saw — not from the full set of
  real issues in this diff.
- **C3 (Disposition ledger) — confirmed.** Both finders returned structured, one-row-per-hypothesis
  tables including pre-admission acquittals, reproduced in full above.
- **C5 (Observations) — confirmed.** 5 distinct items were routed to the observations channel rather
  than the verdict list across both finders and the verifier; none were counted as findings.
- **Pole intact — confirmed.** Both finders ran; the sole candidate got exactly one verifier verdict;
  the verifier's prompt supplied only `id, axis, anchor, fix, title, claim, trigger, priority, action`
  and explicitly withheld `support` — confirmed against the actual sub-agent prompt used.
- **C2 (no-issue rule) and C4 (question-routing) — not applicable to this target, as expected.** A
  real issue exists (#45, 10 ACs), so the no-issue path never engaged; no candidate landed in the
  "cannot tell from the code" bucket, so no question-routing scenario arose. Both are honestly inert
  here, not forced.
